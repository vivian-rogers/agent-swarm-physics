"""Shared sidecars to `kicks_classified`: each kick message's leading-@ primary target, and its receiving call per
(message, agent).

Leading-@ rule (H35, `infra/README.md` Known issue "A nudge's target is its leading @"): the text starts with '@' and
the target is the roster agent whose alias regex (common.mention_regexes) gives the longest match at position 1, among
agents on the roster that day (joined <= pt_date < left; the Claude Code agent excluded). 29% of nudges name other
agents too; those are bystanders, not targets. Copies of this rule: H30 (analysis/h30lib.py: leading_targets), H39
(scheme/build.py: leading_targets), H16 (analysis/r1blib.py: nudge_targets), H35 (scheme/build.py: nudge_table), H52
(scheme/build.py: leading_targets); H59 imports H30's. H04 round 1b (analysis/r1b.py: leading_target) uses a different
rule (the earliest mention after the first '@' among the clean targets, falling back to the first target); --verify
reports the agreement. Text is read in memory only, to find the leading '@'; it is never written.

Receiving call: the recipient's ledger call whose new items include the message (DQ1, `visibility.receipts`); it is
where the kick acts (STANDARDS.md section 2). Kick-response designs aligned on the receiving call (H30, H39, H43, H59)
read it from here.

Outputs (data/processed/shared/, zstd parquet, codes only, ALL days; `holdout` flags locked-holdout days):
  kicks_targets.parquet   one row per kicks_classified row that has a message (goal_kickoff rows have none): msg,
                          message_id, kind, subkind, t, pt_date, goal_no, holdout, room, n_targets, primary_target
                          (Int8; null if the text does not start with a roster '@'), primary_in_targets,
                          n_bystanders (named targets other than the primary). The rule is applied to every kind;
                          for nudges it is the target, for human and agent messages it is the addressee.
  kicks_receipts.parquet  one row per (kick message, agent) for agents that are recipients (exposure), named targets,
                          the primary target, or ledger receivers: msg, kind, pt_date, holdout, agent, is_primary,
                          is_named, in_exposure, turn_id (receiving call; null if the agent never received it),
                          t_call (its t_call), rc_date (its pt_date), same_day (rc_date == pt_date), age_s, uncertain
                          (ledger item flags). Self-rows (the speaker) are excluded.
  H16 classes at the receiving call: N_tgt = nudge & is_primary; N_by = nudge & ~is_primary; H_men / H_und = human &
  is_named / ~is_named; A_men = mention & is_named.

Usage: uv run python infra/shared/kicks_targets.py            (build; needs kicks_classified and the context ledger)
       uv run python infra/shared/kicks_targets.py --verify   (H30 leading_targets and r1b kicks, H35 nudge tables, H39
                                                                leading_targets, H04 r1b rule; read-only)
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
           "RAYON_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT, ROOT, mention_regexes, write_provenance  # noqa: E402
from visibility import load_ro, receipts  # noqa: E402

SH = OUT


def leading_targets(message_ids) -> dict:
    """message_id -> agent code of the leading '@' (H35's rule), or None. Text in memory only."""
    ids = pl.Series("message_id", list(message_ids), dtype=pl.String)
    if ids.len() == 0:
        return {}
    chat = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "pt_date"]).filter(
        pl.col("message_id").is_in(ids.implode()))
    txt = pl.read_parquet(SH / "chat_text.parquet", columns=["message_id", "text"]).filter(
        pl.col("message_id").is_in(ids.implode()))
    chat = chat.join(txt, on="message_id", how="left")
    ros = pl.read_parquet(SH / "roster.parquet").filter(~pl.col("claude_code"))
    pats = mention_regexes([{"id": int(a), "name": n} for a, n in ros.select("agent", "name").iter_rows()])
    span = {int(a): (j, l) for a, j, l in ros.select("agent", "joined", "left").iter_rows()}
    out = {}
    for mid, d, text in chat.select("message_id", "pt_date", "text").iter_rows():
        best, blen = None, 0
        if text and text.startswith("@"):
            for a, pat in pats.items():
                j, l = span[a]
                if not (j <= d and (l is None or d < l)):
                    continue
                mt = pat.match(text, 1)
                if mt and (mt.end() - mt.start()) > blen:
                    best, blen = a, mt.end() - mt.start()
        out[mid] = best
    del chat, txt
    return out


def build() -> tuple[pl.DataFrame, pl.DataFrame]:
    kc = pl.read_parquet(SH / "kicks_classified.parquet").filter(pl.col("message_id").is_not_null())
    lt = leading_targets(kc["message_id"].to_list())
    kc = kc.with_columns(pl.col("message_id").replace_strict(lt, default=None, return_dtype=pl.Int8).alias("primary_target"),
                         pl.col("targets").fill_null(pl.lit([], dtype=pl.List(pl.Int8))),
                         pl.col("recipients").fill_null(pl.lit([], dtype=pl.List(pl.Int8))))
    kc = kc.with_columns(pl.col("targets").list.contains(pl.col("primary_target")).fill_null(False).alias("primary_in_targets"))
    kt = kc.select(pl.col("msg").cast(pl.UInt32), "message_id", "kind", "subkind", "t", "pt_date", "goal_no", "holdout",
                   "room", "n_targets", "primary_target", "primary_in_targets",
                   (pl.col("n_targets").cast(pl.Int16) - pl.col("primary_in_targets").cast(pl.Int16)).cast(pl.Int8)
                   .alias("n_bystanders")).sort("msg")
    # (message, agent) rows: recipients U targets U primary U ledger receivers, minus the speaker
    base = kc.select(pl.col("msg").cast(pl.UInt32), "message_id", "kind", "pt_date", "holdout", "speaker", "primary_target")
    rec = kc.select(pl.col("msg").cast(pl.UInt32), pl.col("recipients").alias("agent")).explode("agent", empty_as_null=True).drop_nulls()
    nam = kc.select(pl.col("msg").cast(pl.UInt32), pl.col("targets").alias("agent")).explode("agent", empty_as_null=True).drop_nulls()
    pri = kc.select(pl.col("msg").cast(pl.UInt32), pl.col("primary_target").alias("agent")).drop_nulls()
    rc = receipts(kc["message_id"].to_list(), item_cols=("age_s", "uncertain"))
    rc = rc.join(base.select("msg", "message_id"), on="message_id", how="inner").rename({"recipient": "agent"})
    keys = pl.concat([rec.select("msg", pl.col("agent").cast(pl.Int8)), nam.select("msg", pl.col("agent").cast(pl.Int8)),
                      pri.select("msg", pl.col("agent").cast(pl.Int8)), rc.select("msg", pl.col("agent").cast(pl.Int8))]).unique()
    kr = (keys.join(base, on="msg", how="left")
          .filter(pl.col("speaker").is_null() | (pl.col("agent") != pl.col("speaker")))
          .join(rec.select("msg", pl.col("agent").cast(pl.Int8), pl.lit(True).alias("in_exposure")), on=["msg", "agent"], how="left")
          .join(nam.select("msg", pl.col("agent").cast(pl.Int8), pl.lit(True).alias("is_named")), on=["msg", "agent"], how="left")
          .join(rc.select("msg", pl.col("agent").cast(pl.Int8), "turn_id", "t_call", "rc_date", "age_s", "uncertain"),
                on=["msg", "agent"], how="left"))
    kr = kr.with_columns(pl.col("in_exposure").fill_null(False), pl.col("is_named").fill_null(False),
                         (pl.col("agent") == pl.col("primary_target")).fill_null(False).alias("is_primary"),
                         (pl.col("rc_date") == pl.col("pt_date")).fill_null(False).alias("same_day"))
    kr = kr.select("msg", "kind", "pt_date", "holdout", "agent", "is_primary", "is_named", "in_exposure", "turn_id", "t_call",
                   "rc_date", "same_day", "age_s", "uncertain").sort("msg", "agent")
    return kt, kr


def main():
    t0 = time.time()
    kt, kr = build()
    p1, p2 = SH / "kicks_targets.parquet", SH / "kicks_receipts.parquet"
    kt.write_parquet(p1, compression="zstd", compression_level=9)
    kr.write_parquet(p2, compression="zstd", compression_level=9)
    nud = kt.filter((pl.col("kind").cast(pl.String) == "nudge") & ~pl.col("holdout"))
    nr = kr.filter((pl.col("kind").cast(pl.String) == "nudge") & ~pl.col("holdout"))
    summ = {"messages": kt.height, "receipt_rows": kr.height,
            "nudges_nonholdout": nud.height, "nudges_with_primary": int(nud["primary_target"].is_not_null().sum()),
            "nudges_primary_not_in_targets": int((nud["primary_target"].is_not_null() & ~nud["primary_in_targets"]).sum()),
            "nudges_with_bystanders": int((nud["n_bystanders"] > 0).sum()),
            "nudge_primary_rows_received": int(nr.filter(pl.col("is_primary"))["turn_id"].is_not_null().sum()),
            "nudge_primary_rows": int(nr["is_primary"].sum()),
            "nudge_primary_received_same_day": int(nr.filter(pl.col("is_primary") & pl.col("same_day")).height)}
    write_provenance("kicks_targets", ["kicks_classified", "chat_core", "chat_text (leading '@' only, in memory)", "roster",
                                       "context_ledger_items", "call_windows"],
                     {"rule": "leading '@': text starts with '@', longest alias match at position 1 among that day's roster "
                              "(Claude Code agent excluded); applied to every kind",
                      "receipt": "visibility.receipts: the recipient's ledger call whose new items include the message",
                      "holdout": "all days, flagged", "sources": "H35 nudge_table; H30 h30lib.leading_targets; H39 "
                      "build.leading_targets (rule unchanged)", "summary": summ})
    print(f"kicks_targets.parquet {kt.height} rows {p1.stat().st_size / 1e6:.2f} MB; kicks_receipts.parquet {kr.height} rows "
          f"{p2.stat().st_size / 1e6:.1f} MB; {time.time() - t0:.0f}s", flush=True)
    print(json.dumps(summ), flush=True)


# ----------------------------------------------------------------------------------------------- verification
def verify() -> dict:
    kt = pl.read_parquet(SH / "kicks_targets.parquet")
    kr = pl.read_parquet(SH / "kicks_receipts.parquet")
    nud = kt.filter((pl.col("kind").cast(pl.String) == "nudge") & ~pl.col("holdout"))
    mine = dict(zip(nud["message_id"].to_list(), nud["primary_target"].to_list()))
    res = {}
    # H30 leading_targets (in memory)
    h30 = load_ro("h30lib_ro", ROOT / "hypotheses/H30-operator-susceptibility/analysis/h30lib.py")
    ref = h30.leading_targets(list(mine))
    diff = [m for m in mine if (mine[m] if mine[m] is None else int(mine[m])) != (ref[m] if ref[m] is None else int(ref[m]))]
    res["H30_leading_targets"] = {"nudges": len(mine), "identical": not diff, "n_diff": len(diff)}
    # H39 leading_targets (in memory; same code)
    h39 = load_ro("h39build_ro", ROOT / "hypotheses/H39-catalysts-vs-fields/scheme/build.py")
    ref = h39.leading_targets(list(mine))
    diff = [m for m in mine if mine[m] != ref[m]]
    res["H39_leading_targets"] = {"nudges": len(mine), "identical": not diff, "n_diff": len(diff)}
    # H35 per-period nudge tables (on disk; idle-trigger nudges only)
    rows = []
    for f in sorted((ROOT / "data/processed/H35-nudger-maxwell-demon").glob("G*/nudges.parquet")):
        rows.append(pl.read_parquet(f, columns=["message_id", "target"]))
    h35 = pl.concat(rows).unique("message_id")
    j = h35.join(kt.select("message_id", "primary_target", "holdout"), on="message_id", how="left")
    res["H35_nudge_tables"] = {"nudges": h35.height, "missing_in_shared": int(j["holdout"].is_null().sum()),
                               "holdout_rows": int(j["holdout"].fill_null(False).sum()),
                               "target_identical": int((j["target"].cast(pl.Int16).eq_missing(j["primary_target"].cast(pl.Int16))).sum())}
    # H30 round-1b kicks at the receiving call (on disk): N_tgt = primary, ts = receiving t_call
    chk = {"rows": 0, "found": 0, "ts_equal": 0, "cls_consistent": 0}
    for f in sorted((ROOT / "data/processed/H30-operator-susceptibility/r1b").glob("G*/kicks.parquet")):
        k = pl.read_parquet(f, columns=["agent", "cls", "msg", "ts", "kind"])
        jj = k.with_columns(pl.col("msg").cast(pl.UInt32), pl.col("agent").cast(pl.Int8)).join(
            kr.select("msg", "agent", "is_primary", "is_named", (pl.col("t_call").dt.epoch("us") / 1e6).alias("tc")),
            on=["msg", "agent"], how="left")
        chk["rows"] += jj.height
        chk["found"] += int(jj["tc"].is_not_null().sum())
        chk["ts_equal"] += int(((jj["tc"] - jj["ts"]).abs() < 1e-3).sum())
        cons = (((pl.col("cls") == "N_tgt") & pl.col("is_primary")) | ((pl.col("cls") == "N_by") & ~pl.col("is_primary"))
                | ((pl.col("cls") == "H_men") & pl.col("is_named")) | ((pl.col("cls") == "H_und") & ~pl.col("is_named")))
        chk["cls_consistent"] += int(jj.select(cons.fill_null(False).sum()).item())
    res["H30_r1b_kicks"] = chk
    # H04 round-1b rule (different by design): agreement on nudges with targets
    h04 = load_ro("h04r1b_ro", ROOT / "hypotheses/H04-reversible-forcing/analysis/r1b.py")
    kc = pl.read_parquet(SH / "kicks_classified.parquet", columns=["message_id", "kind", "targets", "holdout"]).filter(
        (pl.col("kind").cast(pl.String) == "nudge") & ~pl.col("holdout"))
    txt = pl.read_parquet(SH / "chat_text.parquet", columns=["message_id", "text"]).filter(
        pl.col("message_id").is_in(kc["message_id"].implode()))
    tmap = dict(zip(txt["message_id"].to_list(), txt["text"].to_list()))
    agree = n = 0
    for mid, tg in kc.select("message_id", "targets").iter_rows():
        tg = [int(x) for x in (tg or [])]
        if not tg:
            continue
        lt = h04.leading_target(tmap.get(mid) or "", set(tg))
        lt = lt if lt is not None else tg[0]
        n += 1
        agree += int(mine.get(mid) is not None and int(mine[mid]) == lt)
    del tmap, txt
    res["H04_r1b_rule_agreement"] = {"nudges_with_targets": n, "agree": agree}
    print(json.dumps(res, indent=1), flush=True)
    return res


if __name__ == "__main__":
    if "--verify" in sys.argv:
        verify()
    else:
        main()
