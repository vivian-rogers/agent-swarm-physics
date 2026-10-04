"""H74 scheme: daily channel features (non-holdout active days only), from shared tables and the signature scan.

Outputs (data/processed/H74-change-detector/):
  days.parquet               non-holdout active days in time order (idx, pt_date, goal_no, regime, weekday, gap_before)
  agent_day_features.parquet agent x day mix and per-call numbers (channel M)
  day_features.parquet       day-level drive/schedule features (channel D) and content shift R1 (channel C, bge and gte)
  search_daily.parquet       day medians of search-answer format counts (channel O)
  events.parquet             the evaluation catalog (H56's CHANGELOG catalog + roster/goal/room + undocumented)
Run: uv run python hypotheses/H74-change-detector/scheme/build.py   (after scan_signatures.py)
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import PT, REVISION, git_commit, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H74-change-detector"
KINDS = ["cu_action", "talk", "pause", "wait", "consolidate", "search", "session_start", "session_stop", "room_move"]
INFRA = ["timeout", "vm", "resource", "network"]
CLAUDE_CODE = 19
UNDOC = [("NE39", "2025-07-01", "public chat closed (DQ9)"), ("OUT0331", "2026-03-31", "history search returns near-empty answers (H56)"),
         ("NE40", "2026-04-20", "search oracle swap Gemini 2.5 Pro -> Sonnet 4.6 (H56)"),
         ("NE45", "2026-07-29", "search tool date fields int -> str (H56)"),
         ("NE43a", "2026-08-05", "daily pause/resume bookends stop (first day without)"),
         ("NE43b", "2026-08-21", "nudger off (first day without)")]


def main(include_holdout: bool = False, out: Path | None = None):
    """include_holdout=True is for analysis/confirm.py only (guarded there); the default reproduces round 1."""
    OUT = out or globals()["OUT"]
    cal = pl.read_parquet(SH / "calendar.parquet")
    hm = holdout_mask(cal["pt_date"].to_list(), [g if g is not None else -1 for g in cal["goal_no"].to_list()])
    assert hm == cal["holdout"].to_list()
    days = (cal.filter((include_holdout | ~pl.col("holdout")) & (pl.col("n_agent_events") > 0)).sort("pt_date")
            .select("pt_date", "goal_no", pl.col("regime").cast(pl.String), "weekday", "gap_before_s", "win_start", "win_end",
                    "window_s", "documented_hours", "holdout").with_row_index("idx"))
    held = set(cal.filter(pl.col("holdout"))["pt_date"].to_list())
    dset = days["pt_date"].to_list()
    days.write_parquet(OUT / "days.parquet")

    # ---------------- channel M: agent-day mix and per-call numbers
    cw = (pl.scan_parquet(SH / "call_windows.parquet").filter((include_holdout | ~pl.col("holdout")) & (pl.col("agent") != CLAUDE_CODE))
          .select("agent", "pt_date", pl.col("kind").cast(pl.String), "n_rec", "gap_kind", "ctx_mode", "t_first", "t_prev_end", "t_call")
          .collect())
    assert include_holdout or not set(cw["pt_date"].unique().to_list()) & held
    cw = cw.with_columns(((pl.col("t_first") - pl.col("t_prev_end")).dt.total_microseconds() / 1e6).alias("ta"))
    ad = cw.group_by("agent", "pt_date").agg(
        pl.len().alias("n_calls"),
        *[(pl.col("kind") == k).mean().alias(f"sh_{k}") for k in KINDS],
        pl.col("n_rec").mean().alias("rec_per_call"),
        pl.col("ta").filter((pl.col("gap_kind").cast(pl.String) == "busy") & (pl.col("ta") > 0) & (pl.col("ta") < 600)).log().median().alias("log_turnaround"))
    act = pl.scan_parquet(SH / "actions.parquet").with_row_index("row")
    ebh = pl.scan_parquet(SH / "actions_bash_head_fixed.parquet").select("row", "error_class")
    act = (act.join(ebh, on="row", how="left").filter(pl.col("agent") != CLAUDE_CODE)
           .with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("pt_date"))
           .filter(pl.col("pt_date").is_in(dset)).collect())
    aa = act.group_by("agent", "pt_date").agg(
        pl.len().alias("n_turns"),
        (pl.col("tok_in").cast(pl.Float64) + pl.col("tok_cache_read").fill_null(0)).filter(pl.col("tok_in").is_not_null()).log1p().median().alias("log_prompt"),
        pl.col("tok_out").cast(pl.Float64).log1p().median().alias("log_out"),
        pl.col("reasoning_chars").cast(pl.Float64).log1p().median().alias("log_reason"),
        (pl.col("tok_cache_read").sum() / (pl.col("tok_in").sum() + pl.col("tok_cache_read").sum() + pl.col("tok_cache_write").sum())).alias("cache_share"),
        pl.col("tok_in").is_null().mean().alias("tok_null_share"),
        pl.col("error_class").cast(pl.String).is_in(INFRA).mean().alias("infra_err_share"),
        (pl.col("action").cast(pl.String) == "bash").mean().alias("bash_share"))
    agd = ad.join(aa, on=["agent", "pt_date"], how="left").filter(pl.col("pt_date").is_in(dset)).sort("pt_date", "agent")
    agd.write_parquet(OUT / "agent_day_features.parquet")

    # ---------------- channel D: drive and schedule
    kc = pl.read_parquet(SH / "kicks_classified.parquet").filter(include_holdout | ~pl.col("holdout"))
    kd = kc.group_by("pt_date").agg((pl.col("kind").cast(pl.String) == "pause_resume").sum().alias("n_bookends"),
                                     (pl.col("kind").cast(pl.String) == "nudge").sum().alias("n_nudges"),
                                     (pl.col("kind").cast(pl.String) == "human_message").sum().alias("n_human"))
    sm = pl.read_parquet(SH / "outages_fixed/stall_minutes.parquet").filter(include_holdout | ~pl.col("holdout"))
    js = sm.group_by("pt_date").agg(pl.col("js").mean().alias("js_share"))
    first = (cw.filter(pl.col("kind").is_in(["cu_action", "talk", "search"])).group_by("pt_date", "agent")
             .agg(pl.col("t_call").min().alias("t0"), pl.len().alias("n")).filter(pl.col("n") >= 10))
    fs = first.group_by("pt_date").agg(
        ((pl.col("t0").dt.epoch("s").quantile(0.75) - pl.col("t0").dt.epoch("s").quantile(0.25)) / 60).alias("start_iqr_min"),
        pl.len().alias("n_present"))
    dd = (days.select("pt_date", "window_s", "documented_hours", "win_start", "gap_before_s")
          .with_columns((pl.col("win_start").dt.convert_time_zone("America/Los_Angeles").dt.hour().cast(pl.Int32) * 60
                         + pl.col("win_start").dt.convert_time_zone("America/Los_Angeles").dt.minute().cast(pl.Int32)).alias("start_tod_min"),
                        (pl.col("window_s") / 60).alias("window_min"))
          .join(kd, on="pt_date", how="left").join(js, on="pt_date", how="left").join(fs, on="pt_date", how="left")
          .with_columns(pl.col("n_bookends").fill_null(0), pl.col("n_nudges").fill_null(0), pl.col("n_human").fill_null(0)))

    # ---------------- channel C: content centroid shift (R1), bge and gte
    adx = pl.read_parquet(SH / "embeddings/agent_day.parquet")
    for name, fn in (("bge", "agent_day_vec.npy"), ("gte", "agent_day_vec_gte_modernbert.npy")):
        V = np.load(SH / "embeddings" / fn).astype(np.float64)
        ok0 = (~adx["holdout"]).to_numpy() & (adx["agent"] != CLAUDE_CODE).to_numpy()
        V = V - V[ok0].mean(0)   # centering always uses non-holdout rows only
        ok = (include_holdout | ~adx["holdout"]).to_numpy() & (adx["agent"] != CLAUDE_CODE).to_numpy()
        V /= np.maximum(np.linalg.norm(V, axis=1, keepdims=True), 1e-12)
        sub = adx.with_columns(pl.Series("ok", ok)).filter(pl.col("ok") & pl.col("pt_date").is_in(dset))
        cent = {}
        for d, g in sub.group_by("pt_date"):
            cent[d[0]] = V[g["gid"].to_numpy()].mean(0)
        r1, prev = [], None
        for d in dset:
            c = cent.get(d)
            if c is not None and prev is not None:
                r1.append(float(1 - c @ prev / (np.linalg.norm(c) * np.linalg.norm(prev))))
            else:
                r1.append(None)
            if c is not None:
                prev = c
        dd = dd.join(pl.DataFrame({"pt_date": dset, f"r1_{name}": r1}, schema={"pt_date": pl.String, f"r1_{name}": pl.Float64}),
                     on="pt_date", how="left")
    dd.drop("win_start").sort("pt_date").write_parquet(OUT / "day_features.parquet")

    # ---------------- channel O: search answers
    sf = pl.read_parquet(OUT / "search_format.parquet")
    fcols = [c for c in sf.columns if c.startswith("f_")]
    sd = sf.group_by("pt_date").agg(pl.len().alias("n_search"), *[pl.col(c).median() for c in fcols]).sort("pt_date")
    sd.write_parquet(OUT / "search_daily.parquet")

    # ---------------- evaluation catalog
    ec = pl.read_parquet(ROOT / "data/processed/H56-ep-platform-fingerprint/event_catalog.parquet")
    ec = ec.filter(~pl.col("cls").is_in(["infra_invisible", "excluded", "undocumented"])).select(
        pl.col("event_id").cast(pl.String).alias("event"), "date", "cls", "label", "ref", "family_target")
    und = pl.DataFrame([{"event": e, "date": d, "cls": "undocumented", "label": lab, "ref": e, "family_target": None}
                        for e, d, lab in UNDOC], schema=ec.schema)
    ev = pl.concat([ec, und])
    # day 0 = first active day (any, incl. held out) on or after the date; scored only if that day is non-holdout
    all_days = cal.filter(pl.col("n_agent_events") > 0).sort("pt_date")["pt_date"].to_list()
    day0 = [next((x for x in all_days if x >= d), None) for d in ev["date"].to_list()]
    ev = ev.with_columns(pl.Series("day0", day0)).with_columns(pl.col("day0").is_in(list(held)).alias("held0"))
    ev.write_parquet(OUT / "events.parquet")

    prov_path = OUT / "_provenance.json"
    prov = json.loads(prov_path.read_text()) if prov_path.exists() else {}
    prov.update({"built_by": "hypotheses/H74-change-detector/scheme/build.py", "git_commit": git_commit(),
                 "inputs": [{"source": "ai-village", "revision": REVISION,
                             "tables": ["shared/calendar", "shared/call_windows", "shared/actions", "shared/actions_bash_head_fixed",
                                        "shared/kicks_classified", "shared/outages_fixed/stall_minutes", "shared/embeddings/agent_day*",
                                        "H56-ep-platform-fingerprint/event_catalog.parquet (data)", "H74 scan_signatures outputs"]}],
                 "params": {"non_holdout_only": not include_holdout, "claude_code_excluded": True, "undocumented": UNDOC},
                 "built_at": dt.datetime.now(dt.timezone.utc).isoformat()})
    prov_path.write_text(json.dumps(prov, indent=1))
    print(days.height, "days;", agd.height, "agent-days;", ev.height, "events")


if __name__ == "__main__":
    main()
