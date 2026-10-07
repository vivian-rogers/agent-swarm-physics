"""Shared per-call project labels: one project label per model call of each agent, with hop flags.
Written for H133 (read-out Glauber Potts); also used by H134 (Polya-urn stickiness) and H137 (named-pair follows).
Definitions: H133 card "Data scheme" (proposed variants *agent state (categorical, project per call)* and *project hop
(call)*); H134 card (project visit, dwell in own calls, f_proj from per-call touches).

Rule:
  calls     every row of DQ1 `call_windows` (all regimes, all ctx modes), the Claude Code agent excluded. Order per agent:
            (t_first, turn_id). Unit: `period_units` (the unit whose day list holds pt_date; a day in two units goes to
            the unit with the latest start <= t_call).
  mentions  `artifact_mentions` by agents (speaker_kind agent), strict (how in url / output / bare), all sources (action,
            chat, intention), mapped to projects with `project_states.project_map` (files and sites -> parent repo);
            deduped once per (agent, source, ref, project) as in `project_states` (earliest t kept).
  touch     a mention touches call c of its agent if t_first(c) <= t <= t_end(c) + 1 s (latest call with t_first <= t;
            the 1-s tolerance is the `calls.py` rule for rows written just after a call's last record).
  proj      the call's modal touched project; ties -> the latest mention, then the project first seen earliest in the
            dataset, then the name (the `project_states.modal` order). Null when the call touched no project.
  carry     per carry block (agent, goal_no, holdout flag): the last touched project. `since` = own calls since that
            touch (0 at a touch call). The carry never crosses a goal period or a reserved/non-reserved boundary.
  label_E   carry if since <= E, else null (expiry after E own calls without a touch; E = 100 primary, 50 and 300
            variants). `prev_label` = label_100 at the agent's previous call in the block.
  hop_E     proj not null, label_E at the previous call not null, and proj != that label (the hop call is the first call
            that touches the new project). Expiry is not a hop. `arrive_E`: proj not null and label_E at the previous
            call null (first label in the block or a touch after expiry).
  span_s    t_call(c) - t_call(c-1) of the same agent and PT day; null at the agent's first call of the day.

Outputs (data/processed/shared/, zstd, no text; ALL days with a `holdout` flag: these are measurements, exploration must
filter `~holdout`):
  project_calls.parquet          one row per call: turn_id, agent, pt_date, goal_no, unit_id, regime, holdout, ctx_mode,
                                 kind, talk, t_call, t_first, t_end, span_s, seq (0-based per agent-day), idx (0-based per
                                 carry block), n_ment (strict deduped mentions touching the call), n_proj (distinct
                                 projects touched), proj, carry, since, label (E = 100), prev_label, hop, arrive,
                                 hop_e50, hop_e300, label_e50_null / label_e300_null (label_E is carry where false)
  project_call_touches.parquet   one row per (call, touched project): turn_id, agent, project, n (mentions), t_last
Project names are canonical artifact names (as `project_states` and `project_mentions_chat`), so they join with
`copying.project_messages`. Cards hash them in their own outputs.

Usage: uv run python infra/shared/project_calls.py            (build)
       uv run python infra/shared/project_calls.py --verify   (invariants, mention coverage, agreement with
                                                               project_states W30 and H129's attention hops; non-
                                                               reserved rows only; read-only)
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
from common import OUT, ROOT, write_provenance  # noqa: E402

SH = OUT
STRICT_HOW = ("url", "output", "bare")
E_PRIMARY = 100
E_VARIANTS = (50, 300)
TOL_S = 1
OUT_CALLS = SH / "project_calls.parquet"
OUT_TOUCH = SH / "project_call_touches.parquet"


def load_calls() -> pl.DataFrame:
    cc = pl.read_parquet(SH / "roster.parquet").filter(pl.col("claude_code"))["agent"].to_list()
    cw = (pl.scan_parquet(SH / "call_windows.parquet")
          .filter(~pl.col("agent").is_in(cc))
          .select("turn_id", "agent", "pt_date", "goal_no", pl.col("regime").cast(pl.String), "holdout", "ctx_mode",
                  "kind", "talk", "t_call", "t_first", "t_end")
          .collect())
    return cw.sort("agent", "t_first", "turn_id")


def attach_units(cw: pl.DataFrame) -> pl.DataFrame:
    pu = (pl.read_parquet(SH / "period_units.parquet", columns=["unit_id", "goal_no", "start", "days"])
          .explode("days", empty_as_null=True).rename({"days": "pt_date"}))
    j = cw.select("turn_id", "pt_date", "goal_no", "t_call").join(pu, on=["pt_date", "goal_no"], how="inner")
    j = (j.filter(pl.col("start") <= pl.col("t_call")).sort("start", descending=True)
         .group_by("turn_id").agg(pl.col("unit_id").first()))
    # a call before its day's unit start (rare: first unit of a split day) falls back to the day's earliest unit
    rest = cw.select("turn_id", "pt_date", "goal_no").join(j, on="turn_id", how="anti").join(pu, on=["pt_date", "goal_no"])
    rest = rest.sort("start").group_by("turn_id").agg(pl.col("unit_id").first())
    return cw.join(pl.concat([j, rest]), on="turn_id", how="left")


def strict_mentions() -> pl.DataFrame:
    import project_states as PS
    pm = PS.project_map()
    am = (pl.scan_parquet(SH / "artifact_mentions.parquet")
          .filter((pl.col("speaker_kind").cast(pl.String) == "agent") & pl.col("how").cast(pl.String).is_in(list(STRICT_HOW))
                  & pl.col("agent").is_not_null())
          .select("artifact", "t", "agent", pl.col("source").cast(pl.String), "message_id", "ref_index").collect())
    am = am.join(pm, on="artifact", how="inner")
    am = am.with_columns(pl.coalesce(pl.col("message_id"), pl.col("ref_index").cast(pl.String)).alias("ref"))
    am = am.sort("t").unique(subset=["agent", "source", "ref", "project"], keep="first", maintain_order=True)
    return am.select("t", "agent", "source", "project")


def map_mentions(am: pl.DataFrame, cw: pl.DataFrame) -> pl.DataFrame:
    keys = cw.select("turn_id", "agent", "t_first", "t_end").sort("t_first")
    m = am.sort("t").join_asof(keys, left_on="t", right_on="t_first", by="agent", strategy="backward")
    ok = pl.col("turn_id").is_not_null() & (pl.col("t") <= pl.col("t_end") + pl.duration(seconds=TOL_S))
    return m.with_columns(ok.alias("mapped"))


def touches(m: pl.DataFrame) -> pl.DataFrame:
    return (m.filter(pl.col("mapped")).group_by("turn_id", "agent", "project")
            .agg(pl.len().cast(pl.Int16).alias("n"), pl.col("t").max().alias("t_last")))


def modal_per_call(tc: pl.DataFrame) -> pl.DataFrame:
    import project_states as PS
    fs = PS.project_first_seen()
    g = tc.join(fs, on="project", how="left").sort(["n", "t_last", "first_seen", "project"],
                                                   descending=[True, True, False, False], nulls_last=True)
    return g.group_by("turn_id", maintain_order=True).agg(
        pl.col("project").first().alias("proj"), pl.col("n").sum().cast(pl.Int16).alias("n_ment"),
        pl.len().cast(pl.Int8).alias("n_proj"))


def carry_labels(cw: pl.DataFrame) -> pl.DataFrame:
    blk = ["agent", "goal_no", "holdout"]
    cw = cw.sort("agent", "t_first", "turn_id").with_columns(pl.int_range(pl.len()).over(blk).cast(pl.Int32).alias("idx"))
    cw = cw.with_columns(
        pl.col("proj").forward_fill().over(blk).alias("carry"),
        pl.when(pl.col("proj").is_not_null()).then(pl.col("idx")).forward_fill().over(blk).alias("_lt"))
    cw = cw.with_columns((pl.col("idx") - pl.col("_lt")).cast(pl.Int32).alias("since")).drop("_lt")
    out = []
    for E in (E_PRIMARY, *E_VARIANTS):
        lab = pl.when(pl.col("since") <= E).then(pl.col("carry"))
        prev = lab.shift(1).over(blk)
        out += [lab.alias(f"_lab{E}"), prev.alias(f"_prev{E}")]
    cw = cw.with_columns(out)
    cols = []
    for E in (E_PRIMARY, *E_VARIANTS):
        hop = pl.col("proj").is_not_null() & pl.col(f"_prev{E}").is_not_null() & (pl.col("proj") != pl.col(f"_prev{E}"))
        arr = pl.col("proj").is_not_null() & pl.col(f"_prev{E}").is_null()
        sfx = "" if E == E_PRIMARY else f"_e{E}"
        cols += [hop.alias(f"hop{sfx}"), arr.alias(f"arrive{sfx}")]
    cw = cw.with_columns(cols).with_columns(pl.col(f"_lab{E_PRIMARY}").alias("label"),
                                            pl.col(f"_prev{E_PRIMARY}").alias("prev_label"),
                                            *[pl.col(f"_lab{E}").is_null().alias(f"label_e{E}_null") for E in E_VARIANTS])
    return cw.drop([c for c in cw.columns if c.startswith("_")])


def build() -> tuple[pl.DataFrame, pl.DataFrame, dict]:
    t0 = time.time()
    cw = attach_units(load_calls())
    print(f"calls {cw.height} ({time.time() - t0:.0f}s)", flush=True)
    am = strict_mentions()
    m = map_mentions(am, cw)
    tc = touches(m)
    print(f"strict mentions {am.height}, mapped {int(m['mapped'].sum())}; touches {tc.height} ({time.time() - t0:.0f}s)",
          flush=True)
    cw = cw.join(modal_per_call(tc), on="turn_id", how="left").with_columns(
        pl.col("n_ment").fill_null(0), pl.col("n_proj").fill_null(0))
    cw = carry_labels(cw)
    cw = cw.sort("agent", "pt_date", "t_call", "turn_id").with_columns(
        pl.int_range(pl.len()).over("agent", "pt_date").cast(pl.Int32).alias("seq"),
        (pl.col("t_call") - pl.col("t_call").shift(1).over("agent", "pt_date")).dt.total_milliseconds()
        .truediv(1000).cast(pl.Float32).alias("span_s"))
    cols = ["turn_id", "agent", "pt_date", "goal_no", "unit_id", "regime", "holdout", "ctx_mode", "kind", "talk", "t_call",
            "t_first", "t_end", "span_s", "seq", "idx", "n_ment", "n_proj", "proj", "carry", "since", "label", "prev_label",
            "hop", "arrive", "hop_e50", "hop_e300", "arrive_e50", "arrive_e300", "label_e50_null", "label_e300_null"]
    cw = cw.select(cols).sort("agent", "t_first", "turn_id")
    hol = cw.select("turn_id", "holdout")
    tc = tc.join(hol, on="turn_id", how="left").select("turn_id", "agent", "project", "n", "t_last", "holdout")
    mm = m.join(hol, on="turn_id", how="left")
    nh = cw.filter(~pl.col("holdout"))
    summ = {"calls": cw.height, "calls_nonreserved": nh.height,
            "mentions_nonreserved_mapped_share": float(mm.filter(pl.col("holdout") == False)["mapped"].mean())  # noqa: E712
            if mm.height else None,
            "touched_calls_nonreserved": int(nh["proj"].is_not_null().sum()),
            "labelled_share_nonreserved": float(nh["label"].is_not_null().mean()),
            "hops_nonreserved": int(nh["hop"].sum()), "hops_e50_nonreserved": int(nh["hop_e50"].sum()),
            "hops_e300_nonreserved": int(nh["hop_e300"].sum())}
    print(f"built ({time.time() - t0:.0f}s): {json.dumps(summ)}", flush=True)
    return cw, tc, summ


def main():
    cw, tc, summ = build()
    cw.write_parquet(OUT_CALLS, compression="zstd", compression_level=9)
    tc.write_parquet(OUT_TOUCH, compression="zstd", compression_level=9)
    write_provenance("project_calls", ["call_windows", "artifact_mentions", "artifacts", "period_units", "roster"],
                     {"strict_how": list(STRICT_HOW), "sources": "action+chat+intention", "touch": "t_first <= t <= t_end + 1 s",
                      "modal_ties": "latest mention, then earliest first_seen, then name",
                      "carry_block": "agent x goal_no x holdout", "expiry_primary": E_PRIMARY,
                      "expiry_variants": list(E_VARIANTS), "hop": "proj != label_E at the previous call (both set)",
                      "claude_code_excluded": True, "holdout": "all days, flagged",
                      "definition": "hypotheses/H133-readout-glauber-potts/README.md (Data scheme)", "summary": summ})
    print(f"{OUT_CALLS.name}: {OUT_CALLS.stat().st_size / 1e6:.1f} MB; {OUT_TOUCH.name}: {OUT_TOUCH.stat().st_size / 1e6:.1f} MB")


def verify() -> dict:
    """Read-only checks on non-reserved rows only (no reserved count is printed)."""
    import project_states as PS
    cw = pl.read_parquet(OUT_CALLS).filter(~pl.col("holdout"))
    tc = pl.read_parquet(OUT_TOUCH).filter(~pl.col("holdout"))
    res = {}
    # 1. invariants
    inv = {
        "turn_id_unique": cw["turn_id"].n_unique() == cw.height,
        "label_equals_proj_at_touch": int(cw.filter(pl.col("proj").is_not_null() & (pl.col("label") != pl.col("proj"))).height) == 0,
        "since_zero_at_touch": int(cw.filter(pl.col("proj").is_not_null() & (pl.col("since") != 0)).height) == 0,
        "hop_has_prev_label": int(cw.filter(pl.col("hop") & pl.col("prev_label").is_null()).height) == 0,
        "hop_differs": int(cw.filter(pl.col("hop") & (pl.col("proj") == pl.col("prev_label"))).height) == 0,
        "no_hop_without_touch": int(cw.filter(pl.col("hop") & pl.col("proj").is_null()).height) == 0,
        "label_null_beyond_expiry": int(cw.filter((pl.col("since") > E_PRIMARY) & pl.col("label").is_not_null()).height) == 0,
        "touch_rows_match_n_proj": int(tc.height) == int(cw["n_proj"].cast(pl.Int64).sum()),
        "claude_code_absent": cw.filter(pl.col("agent") == 19).height == 0,
        "span_null_iff_seq0": int(cw.filter((pl.col("seq") == 0) != pl.col("span_s").is_null()).height) == 0,
    }
    # recompute the carry independently in plain python on a sample of agent-blocks
    smp = cw.filter(pl.col("goal_no").is_in([38, 51])).sort("agent", "t_first", "turn_id")
    bad = 0
    for (_a, _g), d in smp.group_by(["agent", "goal_no"], maintain_order=True):
        last, since, prevlab = None, None, None
        for proj, lab, hop in d.select("proj", "label", "hop").iter_rows():
            if proj is not None:
                last, since = proj, 0
            elif since is not None:
                since += 1
            mylab = last if (since is not None and since <= E_PRIMARY) else None
            myhop = proj is not None and prevlab is not None and proj != prevlab
            bad += (mylab != lab) + (myhop != hop)
            prevlab = mylab
    inv["python_recompute_mismatches_G38_G51"] = bad
    res["invariants"] = inv
    # 2. counts by regime (non-reserved)
    res["by_regime"] = (cw.group_by("regime").agg(pl.len().alias("calls"), pl.col("proj").is_not_null().mean().alias("touch_share"),
                                                  pl.col("label").is_not_null().mean().alias("labelled_share"),
                                                  pl.col("hop").sum().alias("hops"), pl.col("arrive").sum().alias("arrivals"))
                        .sort("regime").to_dicts())
    # 3. mention coverage: share of non-reserved strict mentions that touch a call
    cwa = pl.read_parquet(OUT_CALLS)  # keys only, for the as-of join (no outcome is computed on reserved rows)
    am = strict_mentions()
    m = map_mentions(am, cwa.select("turn_id", "agent", "t_first", "t_end"))
    m = m.join(cwa.select("turn_id", "holdout"), on="turn_id", how="left")
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "holdout"])
    m = m.with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("pt_date"))
    m = m.join(cal.rename({"holdout": "day_ho"}), on="pt_date", how="left").filter(pl.col("day_ho") == False)  # noqa: E712
    res["mention_coverage"] = {"strict_mentions": m.height, "mapped_share": float(m["mapped"].mean()),
                               "by_source": m.group_by("source").agg(pl.col("mapped").mean()).sort("source").to_dicts()}
    # 4. agreement with project_states W30 (sources all): is the window's modal project among the projects that the
    #    agent's calls with t_first in that window touched?
    ps = pl.read_parquet(SH / "project_states.parquet").filter(
        (pl.col("w_min") == 30) & (pl.col("sources").cast(pl.String) == "all") & ~pl.col("holdout")).with_columns(
        pl.col("project").cast(pl.String))
    calp = PS.load_calendar(allow_holdout=False)
    tcw = tc.join(cw.select("turn_id", "t_first"), on="turn_id").rename({"t_first": "t"})
    tcw = PS.assign_windows(tcw, calp, 30).select("goal_no", "pt_date", "win", "agent", "project").unique()
    j = ps.select("goal_no", "pt_date", "win", "agent", "project").join(
        tcw.with_columns(pl.lit(True).alias("hit")), on=["goal_no", "pt_date", "win", "agent", "project"], how="left")
    res["project_states_w30_agreement"] = {"windows": ps.height, "modal_in_call_touches": float(j["hit"].fill_null(False).mean())}
    # 5. hops vs H129's attention hops (W30 windows, per goal period), descriptive
    h129 = ROOT / "data/processed/H129-project-cycle-currents"
    rows = []
    for d in sorted(h129.glob("G*/hops_attention.parquet")):
        g = int(d.parent.name[1:])
        n129 = pl.read_parquet(d).height
        rows.append({"goal_no": g, "h129_attention_hops": n129, "call_hops_e100": int(cw.filter(pl.col("goal_no") == g)["hop"].sum())})
    res["h129_attention_hops"] = rows
    # 6. flicker: hops that return to the pre-hop label at the agent's next hop within 5 own calls (A -> B -> A)
    hp = cw.filter(pl.col("hop")).sort("agent", "t_first", "turn_id").with_columns(
        pl.col("proj").shift(-1).over("agent", "goal_no").alias("next_dst"),
        (pl.col("idx").shift(-1).over("agent", "goal_no") - pl.col("idx")).alias("gap"))
    res["flicker"] = {"hops": hp.height, "return_within_5_calls_share": float(
        ((pl.Series(hp["next_dst"] == hp["prev_label"]).fill_null(False)) & (hp["gap"].fill_null(10 ** 9) <= 5)).mean())}
    print(json.dumps(res, indent=1, default=str), flush=True)
    return res


if __name__ == "__main__":
    if "--verify" in sys.argv:
        verify()
    else:
        main()
