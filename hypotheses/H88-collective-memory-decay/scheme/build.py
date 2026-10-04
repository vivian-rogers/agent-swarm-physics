"""H88 scheme: items of each finished goal period (artifacts, coined terms), their later uses by carrier group, and
daily attention-share tables.

Inputs (shared tables only; no text read): artifacts, artifact_mentions, H34 markers (uses, first_seen; hashes only,
non-holdout by construction), chat_core (row index msg), roster, calendar, context_ledger_items + call_windows
(newcomers' receipts of term-carrying messages). Held-out days are excluded (calendar.holdout | common.holdout_mask)
before any count and asserted absent.

Output: data/processed/H88-collective-memory-decay/
  items.parquet        P, kind (art|term), item, n_uses_in_P, n_agents_in_P
  uses.parquet         kind, item, P, pt_date, agent, speaker (agent|human) -- every non-holdout use after P's start
  daily.parquet        P, kind, group (vet|new|all), k, pt_date, observed, y, O
  carriers.parquet     P, agent, group (vet|new)
  periods.parquet      P, first_day, last_day, regime, n_items_art, n_items_term
  term_firstuse_newc.parquet  newcomer first uses of P terms with in_cone (a message carrying the term entered one of
                       the newcomer's receiving calls before the use)

  uv run python hypotheses/H88-collective-memory-decay/scheme/build.py
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import git_commit, holdout_mask, load_holdout  # noqa: E402

SH = ROOT / "data/processed/shared"
MK = ROOT / "data/processed/H34-idea-cascades/markers"
OUT = ROOT / "data/processed/H88-collective-memory-decay"
DROP = [19, 28, 30]
LAST_DAY = "2026-09-04"
HORIZON = 120
MIN_USES, MIN_AGENTS = 3, 2


def to_pt(col: str) -> pl.Expr:
    return pl.col(col).dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String)


def markers(include_holdout: bool, chat: pl.DataFrame):
    """H34 N-class marker uses and first-seen goal. Non-holdout: H34's files. include_holdout (confirm.py only): adds
    held-out chat rows through infra/shared/idea_markers.uses_for_rows(allow_holdout=True), in memory, and recomputes
    each marker's first goal over all rows."""
    fs = pl.read_parquet(MK / "first_seen.parquet").filter(pl.col("cls") == 2)
    mu = pl.read_parquet(MK / "uses.parquet").filter(pl.col("cls") == 2)
    if not include_holdout:
        return fs, mu
    import idea_markers as IM
    have = set(mu["msg"].unique().to_list()) | set(pl.read_parquet(MK / "uses.parquet")["msg"].unique().to_list())
    held_rows = chat.filter(pl.col("held"))["msg"].to_list()
    extra = IM.uses_for_rows(held_rows, allow_holdout=True).filter(pl.col("cls") == 2)
    mu = pl.concat([mu.select("msg", "marker", "cls"), extra.select("msg", "marker", "cls").cast(mu.select("msg", "marker", "cls").schema)])
    first = (mu.join(chat.select("msg", "t", "goal_no"), on="msg", how="inner").sort("t")
             .group_by("marker").agg(pl.col("goal_no").first().alias("first_goal")))
    fs = first.with_columns(pl.lit(2).cast(pl.UInt8).alias("cls"))
    del have
    return fs, mu


def build(include_holdout: bool = False, write: bool = True, last_day: str = LAST_DAY):
    """include_holdout=True is for analysis/confirm.py only (in memory; write must be False)."""
    assert not (include_holdout and write), "held-out rows are never written to disk"
    if write:
        OUT.mkdir(parents=True, exist_ok=True)
    cal = pl.read_parquet(SH / "calendar.parquet").select("pt_date", "goal_no", "regime", "holdout").sort("pt_date")
    hm = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    cal = cal.with_columns((pl.col("holdout").fill_null(False) | pl.Series(hm)).alias("held"))
    days = cal["pt_date"].to_list()
    held = set() if include_holdout else set(cal.filter(pl.col("held"))["pt_date"].to_list())
    okday = set(d for d in days if d not in held and d <= last_day)
    held_goals = set() if include_holdout else set(load_holdout()["goal_periods_held_out"])
    roster = pl.read_parquet(SH / "roster.parquet").select("agent", "joined")

    # periods
    per = []
    for g in range(1 if include_holdout else 2, 51 if include_holdout else 45):
        if g in held_goals:
            continue
        pd_ = cal.filter(pl.col("goal_no") == g)
        if not pd_.height:
            continue
        pdays = [d for d in pd_["pt_date"].to_list() if d in okday]
        if not pdays:
            continue
        per.append((g, min(pd_["pt_date"]), max(pd_["pt_date"]), pd_["regime"][0], pdays))
    goal_of_day = dict(zip(cal["pt_date"].to_list(), cal["goal_no"].to_list()))

    # chat (agent and human) with msg index, non-holdout days only
    chat = (pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "pt_date", "goal_no", "speaker_kind", "agent", "t"])
            .with_row_index("msg"))
    chat = chat.filter(pl.col("pt_date").is_in(list(okday)))
    chat = chat.with_columns(pl.Series("held", holdout_mask(chat["pt_date"].to_list(), chat["goal_no"].to_list())))
    veterans = {}
    for g, f, l_, r, pdays in per:
        v = chat.filter(pl.col("pt_date").is_in(pdays) & (pl.col("speaker_kind") == "agent")
                        & ~pl.col("agent").is_in(DROP))["agent"].unique().to_list()
        veterans[g] = set(v)

    # ---------------------------------------------------------------- artifact items
    art = pl.read_parquet(SH / "artifacts.parquet")
    art = art.with_columns(pl.coalesce("parent", "artifact").alias("root"))
    am = pl.read_parquet(SH / "artifact_mentions.parquet", columns=["artifact", "t", "agent", "speaker_kind", "source", "how"])
    am = am.with_columns(to_pt("t").alias("pt_date")).filter(pl.col("pt_date").is_in(list(okday)))
    am = am.filter((pl.col("source") != "action") | pl.col("how").cast(pl.String).is_in(["url", "output", "bare"]))
    am = am.join(art.select("artifact", "root", "kind"), on="artifact", how="left")
    am = am.filter(pl.col("kind").cast(pl.String).is_in(["repo", "site", "file"]))
    rootinfo = (art.filter(pl.col("kind").cast(pl.String).is_in(["repo", "site", "file"]))
                .sort("first_t").group_by("root").agg(pl.col("first_t").first(), pl.col("first_speaker_kind").first()))
    rootinfo = rootinfo.with_columns(to_pt("first_t").alias("first_day"))
    am = am.with_columns(pl.when(pl.col("speaker_kind").cast(pl.String) == "agent").then(pl.lit("agent"))
                         .when(pl.col("speaker_kind").cast(pl.String) == "human").then(pl.lit("human"))
                         .otherwise(pl.lit("other")).alias("speaker"))
    am = am.filter((pl.col("speaker") == "human") | ((pl.col("speaker") == "agent") & ~pl.col("agent").is_in(DROP)))
    items = []; uses = []
    for g, f, l_, r, pdays in per:
        cand = rootinfo.filter(pl.col("first_day").is_in(pdays)
                               & (pl.col("first_speaker_kind").cast(pl.String) == "agent"))["root"].to_list()
        inP = am.filter(pl.col("root").is_in(cand) & pl.col("pt_date").is_in(pdays) & (pl.col("speaker") == "agent"))
        st = inP.group_by("root").agg(pl.len().alias("n"), pl.col("agent").n_unique().alias("na"))
        keep = st.filter((pl.col("n") >= MIN_USES) & (pl.col("na") >= MIN_AGENTS))
        for root, n, na in keep.iter_rows():
            items.append((g, "art", int(root), int(n), int(na)))
        ks = keep["root"].to_list()
        u = am.filter(pl.col("root").is_in(ks) & (pl.col("pt_date") >= f))
        uses.append(u.select(pl.lit("art").alias("kind"), pl.col("root").cast(pl.Int64).alias("item"), pl.lit(g).alias("P"),
                             "pt_date", "agent", "speaker"))
    # ---------------------------------------------------------------- term items (H34 N class)
    fs, mu = markers(include_holdout, chat)
    mu = mu.join(chat.select("msg", "pt_date", "speaker_kind", "agent"), on="msg", how="inner")
    mu = mu.with_columns(pl.when(pl.col("speaker_kind").cast(pl.String) == "agent").then(pl.lit("agent"))
                         .when(pl.col("speaker_kind").cast(pl.String) == "human").then(pl.lit("human"))
                         .otherwise(pl.lit("other")).alias("speaker"))
    mu = mu.filter((pl.col("speaker") == "human") | ((pl.col("speaker") == "agent") & ~pl.col("agent").is_in(DROP)))
    for g, f, l_, r, pdays in per:
        cand = fs.filter(pl.col("first_goal") == g)["marker"]
        inP = mu.filter(pl.col("marker").is_in(cand.implode()) & pl.col("pt_date").is_in(pdays) & (pl.col("speaker") == "agent"))
        st = inP.group_by("marker").agg(pl.col("msg").n_unique().alias("n"), pl.col("agent").n_unique().alias("na"))
        keep = st.filter((pl.col("n") >= MIN_USES) & (pl.col("na") >= MIN_AGENTS))
        for m, n, na in keep.iter_rows():
            items.append((g, "term", int(m), int(n), int(na)))
        u = mu.filter(pl.col("marker").is_in(keep["marker"].implode()) & (pl.col("pt_date") >= f))
        uses.append(u.select(pl.lit("term").alias("kind"), pl.col("marker").cast(pl.Int64).alias("item"),
                             pl.lit(g).alias("P"), "pt_date", "agent", "speaker"))
    items = pl.DataFrame(items, schema={"P": pl.Int16, "kind": pl.String, "item": pl.Int64, "n_uses_in_P": pl.Int32,
                                        "n_agents_in_P": pl.Int16}, orient="row")
    uses = pl.concat([u.with_columns(pl.col("P").cast(pl.Int16), pl.col("agent").cast(pl.Int8)) for u in uses])
    if not include_holdout:
        assert not uses["pt_date"].is_in(list(cal.filter(pl.col("held"))["pt_date"].to_list())).any()

    # ---------------------------------------------------------------- daily shares
    # O: all uses of the kind by agents per day (any item: all artifacts / all N markers)
    O_art = am.filter(pl.col("speaker") == "agent").select("pt_date", "agent")
    O_term = mu.filter(pl.col("speaker") == "agent").select("pt_date", "agent")
    joined = dict(zip(roster["agent"].to_list(), roster["joined"].to_list()))
    rows = []; carriers = []
    for g, f, l_, r, pdays in per:
        vet = veterans[g]
        after = [d for d in days if d > l_][:HORIZON]
        newc = {a for a, j in joined.items() if j > l_ and a not in DROP}
        for a in vet:
            carriers.append((g, a, "vet"))
        for a in newc:
            carriers.append((g, a, "new"))
        for kind, Odf in (("art", O_art), ("term", O_term)):
            u = uses.filter((pl.col("P") == g) & (pl.col("kind") == kind) & (pl.col("speaker") == "agent")
                            & pl.col("pt_date").is_in(after))
            Ok = Odf.filter(pl.col("pt_date").is_in(after))
            for grp, members in (("vet", vet), ("new", newc), ("all", None)):
                uu = u if members is None else u.filter(pl.col("agent").is_in(list(members)))
                oo = Ok if members is None else Ok.filter(pl.col("agent").is_in(list(members)))
                yc = dict(uu.group_by("pt_date").len().iter_rows())
                oc = dict(oo.group_by("pt_date").len().iter_rows())
                for k, d in enumerate(after, start=1):
                    obs = d in okday
                    rows.append((g, kind, grp, k, d, obs, yc.get(d, 0) if obs else None, oc.get(d, 0) if obs else None))
    daily = pl.DataFrame(rows, schema={"P": pl.Int16, "kind": pl.String, "group": pl.String, "k": pl.Int16,
                                       "pt_date": pl.String, "observed": pl.Boolean, "y": pl.Int32, "O": pl.Int32},
                         orient="row")
    carriers = pl.DataFrame(carriers, schema={"P": pl.Int16, "agent": pl.Int8, "group": pl.String}, orient="row")
    periods = pl.DataFrame([(g, f, l_, r) for g, f, l_, r, _ in per], schema={"P": pl.Int16, "first_day": pl.String,
                                                                               "last_day": pl.String, "regime": pl.String},
                           orient="row")
    periods = periods.join(items.group_by("P", "kind").len().pivot(on="kind", index="P", values="len"), on="P", how="left")

    # ---------------------------------------------------------------- newcomer first uses of P terms: in-cone?
    tu = uses.filter((pl.col("kind") == "term") & (pl.col("speaker") == "agent"))
    tu = tu.join(carriers.filter(pl.col("group") == "new"), on=["P", "agent"], how="inner")
    first = tu.group_by("P", "item", "agent").agg(pl.col("pt_date").min().alias("first_day"))
    # exact first-use time: earliest message of that agent carrying the marker
    mu_t = mu.join(chat.select("msg", "t"), on="msg", how="left").filter(pl.col("speaker") == "agent")
    ft = (first.join(mu_t.select(pl.col("marker").alias("item"), "agent", "t"), on=["item", "agent"], how="left")
          .group_by("P", "item", "agent").agg(pl.col("t").min().alias("t_first")))
    newc_agents = ft["agent"].unique().to_list()
    cw = (pl.scan_parquet(SH / "call_windows.parquet").select("turn_id", "agent", "t_call", "holdout", "pt_date")
          .filter(pl.col("agent").is_in(newc_agents) & ~pl.col("holdout")).collect())
    cw = cw.filter(pl.col("pt_date").is_in(list(okday)))
    it = pl.scan_parquet(SH / "context_ledger_items.parquet").select("turn_id", "message_id").collect()
    rec = it.join(cw.select("turn_id", "agent", "t_call"), on="turn_id", how="inner")
    carry = mu.select("marker", "msg").filter(pl.col("marker").is_in(ft["item"].unique().implode()))
    carry = carry.join(chat.select("msg", "message_id"), on="msg", how="left")
    rr = rec.join(carry.select(pl.col("marker").alias("item"), "message_id"), on="message_id", how="inner")
    seen = (ft.join(rr.select("item", "agent", "t_call"), on=["item", "agent"], how="left")
            .with_columns((pl.col("t_call") < pl.col("t_first")).fill_null(False).alias("pre"))
            .group_by("P", "item", "agent", "t_first").agg(pl.col("pre").any().alias("in_cone")))
    if not write:
        return {"items": items, "uses": uses, "daily": daily, "carriers": carriers, "periods": periods, "term_firstuse_newc": seen}
    seen.write_parquet(OUT / "term_firstuse_newc.parquet")

    items.write_parquet(OUT / "items.parquet")
    uses.write_parquet(OUT / "uses.parquet", compression="zstd")
    daily.write_parquet(OUT / "daily.parquet")
    carriers.write_parquet(OUT / "carriers.parquet")
    periods.write_parquet(OUT / "periods.parquet")
    prov = {"built_by": "hypotheses/H88-collective-memory-decay/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": "838b4150303ca8228e8edb432d8b8ccae353d258",
                        "tables": ["shared/artifacts", "shared/artifact_mentions", "H34-idea-cascades/markers",
                                   "shared/chat_core", "shared/roster", "shared/calendar", "shared/call_windows",
                                   "shared/context_ledger_items"]}],
            "params": {"min_uses_in_P": MIN_USES, "min_agents_in_P": MIN_AGENTS, "horizon_days": HORIZON,
                       "last_day": LAST_DAY, "action_how": ["url", "output", "bare"], "term_class": "H34 N",
                       "drop_agents": DROP, "holdout": "excluded before any count; held-out days are censored"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print(periods)
    print("items", items.group_by("kind").len(), "uses", uses.height, "daily", daily.height)


def main():
    build(include_holdout=False, write=True)


if __name__ == "__main__":
    main()
