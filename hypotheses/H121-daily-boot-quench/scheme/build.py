"""H121 scheme: per non-holdout period unit, every eligible agent-day's receiving calls aligned at the agent's boot
(its first receiving call of the PT day). Codes only (no text).

Output: data/processed/H121-daily-boot-quench/calls/<unit>.parquet, unit_meta.parquet, _provenance.json.

    uv run python hypotheses/H121-daily-boot-quench/scheme/build.py [--units 41,51c]

Holdout is asserted twice (calendar.holdout and common.holdout_mask). `allow_holdout` is set only by
analysis/confirm.py (guarded), which passes its own unit dicts and an out_dir outside the exploratory folder.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import git_commit, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H121-daily-boot-quench"
H67 = ROOT / "data/processed/H67-lagged-criticality-dial/results"
MIN_CALLS = 30          # eligible agent-day
GAP_MIN = 30            # truncate at the first non-edge village-off gap of >= 30 min
SS_AFTER_MIN = 60       # steady-state calls: >= 60 min after the boot ...
SS_BEFORE_END_MIN = 30  # ... and >= 30 min before the agent's last call
SYNC_MIN, LATE_MIN, LATE_LEAD_MIN = 10, 60, 30
KMAX_CAP = 400


def load_shared(allow_holdout: bool = False):
    cc_agents = pl.read_parquet(SH / "roster.parquet").filter(pl.col("claude_code"))["agent"].to_list()
    cw = (pl.scan_parquet(SH / "call_windows.parquet")
          .filter((pl.lit(allow_holdout) | ~pl.col("holdout")) & (pl.col("ctx_mode") != "summary")
                  & ~pl.col("agent").is_in(cc_agents))
          .select("turn_id", "agent", "pt_date", "goal_no", "regime", "holdout", "talk", "ctx_mode", "t_call",
                  "gap_kind")
          .collect())
    og = (pl.read_parquet(SH / "outages_fixed/outages.parquet")
          .filter(pl.col("village_off") & ~pl.col("at_day_edge") & (pl.col("dur_min") >= GAP_MIN))
          .group_by("pt_date").agg(pl.col("t_start").min().alias("t_gap")))
    return cw, og


def build_unit(u: dict, cw: pl.DataFrame, og: pl.DataFrame, cal: pl.DataFrame, out_dir: Path | None = None,
               allow_holdout: bool = False) -> dict | None:
    days = sorted(u["days"])
    if not allow_holdout:
        held = holdout_mask(days, [u["goal_no"]] * len(days))
        assert not any(held), f"holdout day in unit {u['unit_id']}"
        assert not cal.filter(pl.col("pt_date").is_in(days) & pl.col("holdout")).height, "calendar holdout"
    c = (cw.filter(pl.col("pt_date").is_in(days) & (pl.col("goal_no") == u["goal_no"])
                   & (pl.col("t_call") >= u["start"]) & (pl.col("t_call") < u["end"]))
         .join(og, on="pt_date", how="left")
         .filter(pl.col("t_gap").is_null() | (pl.col("t_call") < pl.col("t_gap")))
         .sort("agent", "pt_date", "t_call", "turn_id"))
    if not allow_holdout:
        assert not c["holdout"].any(), "holdout call"
    if c.height == 0:
        return None
    c = c.with_columns(pl.len().over("agent", "pt_date").alias("n_ad"))
    c = c.filter(pl.col("n_ad") >= MIN_CALLS)
    if c.height == 0:
        return None
    us = lambda col: (pl.col(col).dt.epoch("us") / 1e6)  # noqa: E731
    c = c.with_columns(us("t_call").alias("ts"))
    c = c.with_columns(
        pl.int_range(pl.len()).over("agent", "pt_date").cast(pl.Int32).alias("k"),
        pl.col("ts").min().over("agent", "pt_date").alias("t_boot"),
        pl.col("ts").max().over("agent", "pt_date").alias("t_last"),
        pl.col("ts").min().over("pt_date").alias("t_day0"),
        (pl.col("ts") - pl.col("ts").shift(1).over("agent", "pt_date")).alias("dt_prev"),
    )
    # boot classes per day
    boots = (c.group_by("pt_date", "agent").agg(pl.col("t_boot").first()).sort("pt_date", "t_boot"))
    rows = []
    for (d,), g in boots.group_by(["pt_date"], maintain_order=True):
        tb = g["t_boot"].to_numpy()
        t0 = float(np.median(tb))
        for a, b in zip(g["agent"].to_list(), tb):
            n_lead = int(np.sum(tb <= b - LATE_LEAD_MIN * 60)) if True else 0
            if abs(b - t0) <= SYNC_MIN * 60:
                cl = 1
            elif b - t0 >= LATE_MIN * 60 and n_lead >= 3:
                cl = 2
            else:
                cl = 0
            rows.append({"pt_date": d, "agent": a, "cls": cl, "boot_lag_min": (b - t0) / 60})
    bc = pl.DataFrame(rows, schema={"pt_date": pl.String, "agent": pl.Int8, "cls": pl.Int8, "boot_lag_min": pl.Float64})
    c = c.join(bc, on=["pt_date", "agent"], how="left")
    dmap = {d: k for k, d in enumerate(days)}
    first_goal_day = cal.filter(pl.col("goal_no") == u["goal_no"])["pt_date"].min()
    c = c.with_columns(
        pl.col("pt_date").replace_strict(dmap, return_dtype=pl.Int16).alias("day"),
        ((pl.col("ts") - pl.col("t_boot")) / 60).cast(pl.Float32).alias("mins"),
        ((pl.col("ts") - pl.col("t_day0")) // 1800).cast(pl.Int16).alias("block"),
        (((pl.col("ts") - pl.col("t_boot")) >= SS_AFTER_MIN * 60)
         & ((pl.col("t_last") - pl.col("ts")) >= SS_BEFORE_END_MIN * 60)).alias("ss"),
        pl.col("talk").cast(pl.Int8).alias("Y"),
        (pl.col("pt_date") == first_goal_day).alias("kickoff_day"),
        pl.col("dt_prev").cast(pl.Float32),
    )
    out = c.select("agent", "day", "pt_date", "k", "Y", "mins", "block", "ss", "cls", "boot_lag_min", "dt_prev",
                   "kickoff_day", "n_ad", "ctx_mode", "gap_kind")
    base = out_dir or OUT
    (base / "calls").mkdir(parents=True, exist_ok=True)
    out.write_parquet(base / "calls" / f"{u['unit_id']}.parquet", compression="zstd")
    ad = out.group_by("pt_date", "agent").agg(pl.col("n_ad").first(), pl.col("cls").first())
    per_day = ad.group_by("pt_date").agg(pl.len().alias("n"))
    kmax = int(min(KMAX_CAP, np.quantile(ad["n_ad"].to_numpy(), 0.25)))
    ss = out.filter(pl.col("ss") & pl.col("dt_prev").is_not_null())
    return {"unit_id": u["unit_id"], "goal_no": int(u["goal_no"]), "regime": u["regime"], "n_days": len(days),
            "first_day": u["first_day"], "last_day": u["last_day"], "n_agentdays": ad.height,
            "n_days_elig": per_day.height, "N_mean": float(per_day["n"].mean()), "K_max": kmax,
            "med_interval_ss_s": float(ss["dt_prev"].median()) if ss.height else None,
            "n_sync": int((ad["cls"] == 1).sum()), "n_late": int((ad["cls"] == 2).sum()),
            "n_kickoff_agentdays": int(out.filter(pl.col("kickoff_day")).select(pl.struct("pt_date", "agent").n_unique()).item()),
            "n_calls": out.height}


def attach_glag(meta: pl.DataFrame) -> pl.DataFrame:
    """H67's g_lag per unit (read as data); the period pool where H67 dropped the unit."""
    uu = pl.read_parquet(H67 / "units.parquet").select("unit_id", pl.col("g").alias("g_lag"),
                                                        pl.col("g_lo").alias("g_lag_lo"),
                                                        pl.col("g_hi").alias("g_lag_hi"))
    pp = pl.read_parquet(H67 / "periods.parquet").select(pl.col("goal_no").cast(pl.Int64), pl.col("g").alias("g_p"),
                                                          pl.col("g_lo").alias("g_p_lo"), pl.col("g_hi").alias("g_p_hi"))
    m = meta.join(uu, on="unit_id", how="left").join(pp, on="goal_no", how="left")
    src = pl.when(pl.col("g_lag").is_not_null()).then(pl.lit("unit")).when(pl.col("g_p").is_not_null()).then(
        pl.lit("period")).otherwise(pl.lit("none"))
    return m.with_columns(src.alias("g_src"),
                          pl.coalesce("g_lag", "g_p").alias("g_lag"), pl.coalesce("g_lag_lo", "g_p_lo").alias("g_lag_lo"),
                          pl.coalesce("g_lag_hi", "g_p_hi").alias("g_lag_hi")).drop("g_p", "g_p_lo", "g_p_hi")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", default="")
    a = ap.parse_args()
    cal = pl.read_parquet(SH / "calendar.parquet")
    pu = pl.read_parquet(SH / "period_units.parquet").filter(~pl.col("holdout"))
    if a.units:
        pu = pu.filter(pl.col("unit_id").is_in(a.units.split(",")))
    cw, og = load_shared()
    meta = []
    for u in pu.sort("goal_no", "seq").to_dicts():
        r = build_unit(u, cw, og, cal)
        if r:
            meta.append(r)
            print(r["unit_id"], r["n_agentdays"], r["K_max"], flush=True)
    m = attach_glag(pl.DataFrame(meta))
    if a.units and (OUT / "unit_meta.parquet").exists():
        old = pl.read_parquet(OUT / "unit_meta.parquet").filter(~pl.col("unit_id").is_in(m["unit_id"]))
        m = pl.concat([old, m], how="diagonal_relaxed")
    m.sort("goal_no", "unit_id").write_parquet(OUT / "unit_meta.parquet")
    prov = {"built_by": "hypotheses/H121-daily-boot-quench/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": "shared tables (DQ1 context ledger; outages_fixed)",
                        "tables": ["call_windows", "outages_fixed/outages", "calendar", "period_units", "roster"]},
                       {"source": "H67 results (read as data)", "tables": ["units.parquet", "periods.parquet"]}],
            "params": {"min_calls": MIN_CALLS, "gap_min": GAP_MIN, "ss_after_min": SS_AFTER_MIN,
                       "ss_before_end_min": SS_BEFORE_END_MIN, "sync_min": SYNC_MIN, "late_min": LATE_MIN,
                       "late_lead_min": LATE_LEAD_MIN, "kmax_cap": KMAX_CAP, "holdout": "excluded, asserted twice"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    main()
