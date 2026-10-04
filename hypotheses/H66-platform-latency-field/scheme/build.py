"""H66 scheme: per-unit minute grids of activity, call intensity, call turnaround (latency spins), Gemini server time,
infrastructure errors and room, for every eligible non-holdout unit of the computer-use scaffold (regimes II-III).

Inputs (shared, read-only): call_windows (DQ1), turn_errors, roster, rooms_timeline, period_units, calendar.
Output: data/processed/H66-platform-latency-field/grid/<unit>.parquet (+ units.parquet, _provenance.json).
  Columns: pt_date, m (minute index from the day's first act-call minute), agent, a (act call in minute), n (act calls),
  lat (median log turnaround of chained calls starting in the minute; NaN if none), n_lat, api (median log dur_api_s;
  Gemini only), err (infrastructure-error turns), room, lab (int code).
No text. Held-out days are dropped with a hard assertion (calendar flag and common.holdout_mask must agree).
Run: OMP_NUM_THREADS=4 POLARS_MAX_THREADS=4 uv run python hypotheses/H66-platform-latency-field/scheme/build.py
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "4")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H66-platform-latency-field"
ACT_KINDS = ["cu_action", "talk", "search", "room_move", "request"]
INFRA = ["timeout", "vm", "resource", "network"]
CLAUDE_CODE = 19


def main(holdout_units: bool = False, out: Path | None = None):
    """holdout_units=True builds the held-out regime-III units for analysis/confirm.py only (guarded there)."""
    OUT = out or globals()["OUT"]
    (OUT / "grid").mkdir(parents=True, exist_ok=True)
    roster = pl.read_parquet(SH / "roster.parquet")
    labs = sorted(roster["lab"].unique().to_list())
    lab_code = {a: labs.index(l) for a, l in zip(roster["agent"], roster["lab"])}
    pu = pl.read_parquet(SH / "period_units.parquet")
    pu = (pu.filter(pl.col("holdout") & (pl.col("regime") == "III")) if holdout_units
          else pu.filter(~pl.col("holdout") & pl.col("regime").is_in(["II", "III"])))
    cal = pl.read_parquet(SH / "calendar.parquet")
    hm = holdout_mask(cal["pt_date"].to_list(), [g if g is not None else -1 for g in cal["goal_no"].to_list()])
    assert all(a == b for a, b in zip(hm, cal["holdout"].to_list())), "calendar.holdout disagrees with holdout_mask"
    held = set() if holdout_units else set(cal.filter(pl.col("holdout"))["pt_date"].to_list())

    cw = (pl.scan_parquet(SH / "call_windows.parquet")
          .filter((pl.col("holdout") if holdout_units else ~pl.col("holdout")) & pl.col("regime").cast(pl.String).is_in(["II", "III"])
                  & (pl.col("agent") != CLAUDE_CODE))
          .select("agent", "pt_date", "kind", "ctx_mode", "gap_kind", "t_first", "t_prev_end", "dur_api_s")
          .collect())
    assert not set(cw["pt_date"].unique().to_list()) & held
    cw = cw.with_columns(
        pl.col("kind").cast(pl.String).is_in(ACT_KINDS).alias("is_act"),
        ((pl.col("gap_kind").cast(pl.String) == "busy") & (pl.col("ctx_mode").cast(pl.String) == "cu")).alias("chained"),
        ((pl.col("t_first") - pl.col("t_prev_end")).dt.total_microseconds() / 1e6).alias("ta"),
        pl.col("t_first").dt.truncate("1m").alias("tm"))
    cw = cw.with_columns((pl.col("chained") & (pl.col("ta") > 0) & (pl.col("ta") < 600)).alias("ta_ok"))
    te = (pl.scan_parquet(SH / "turn_errors.parquet").filter((pl.col("holdout") if holdout_units else ~pl.col("holdout")) & pl.col("err_cat").cast(pl.String).is_in(INFRA))
          .select("agent", "pt_date", pl.col("t").dt.truncate("1m").alias("tm")).collect())
    rt = pl.read_parquet(SH / "rooms_timeline.parquet")

    units = []
    for u in pu.iter_rows(named=True):
        days = [d for d in u["days"] if d not in held]
        c = cw.filter(pl.col("pt_date").is_in(days))
        if c.height == 0:
            continue
        per = (c.group_by("pt_date", "agent", "tm").agg(
            pl.col("is_act").sum().cast(pl.Int16).alias("n"),
            pl.col("ta").filter(pl.col("ta_ok")).log().median().cast(pl.Float32).alias("lat"),
            pl.col("ta_ok").sum().cast(pl.Int16).alias("n_lat"),
            pl.col("dur_api_s").filter(pl.col("dur_api_s") > 0).log().median().cast(pl.Float32).alias("api")))
        errs = te.filter(pl.col("pt_date").is_in(days)).group_by("pt_date", "agent", "tm").agg(pl.len().cast(pl.Int16).alias("err"))
        # minute grid per day: first to last minute with an act call by anyone
        acts = c.filter(pl.col("is_act"))
        rng = acts.group_by("pt_date").agg(pl.col("tm").min().alias("t0"), pl.col("tm").max().alias("t1"))
        agents = acts.group_by("pt_date", "agent").agg(pl.len().alias("_n"))
        grids = []
        for d, t0, t1 in rng.iter_rows():
            T = int((t1 - t0).total_seconds() // 60) + 1
            mins = pl.DataFrame({"pt_date": [d] * T, "m": list(range(T)),
                                 "tm": pl.datetime_range(t0, t1, "1m", eager=True, time_zone="UTC")})
            ag = agents.filter(pl.col("pt_date") == d).select("agent")
            grids.append(mins.join(ag, how="cross"))
        g = pl.concat(grids)
        g = (g.join(per, on=["pt_date", "agent", "tm"], how="left").join(errs, on=["pt_date", "agent", "tm"], how="left")
             .with_columns(pl.col("n").fill_null(0), pl.col("n_lat").fill_null(0), pl.col("err").fill_null(0)))
        g = g.with_columns((pl.col("n") > 0).cast(pl.Int8).alias("a"))
        # room at the minute
        r = rt.filter(pl.col("agent").is_in(g["agent"].unique().to_list())).select("agent", "room", "t_start", "t_end").sort("t_start")
        g = g.sort("tm").join_asof(r, left_on="tm", right_on="t_start", by="agent", strategy="backward")
        g = g.with_columns(pl.when(pl.col("t_end").is_null() | (pl.col("tm") <= pl.col("t_end"))).then(pl.col("room"))
                           .otherwise(None).cast(pl.Int8).alias("room")).drop("t_start", "t_end")
        g = g.with_columns(pl.col("agent").replace_strict(lab_code, return_dtype=pl.Int8).alias("lab"))
        g = g.select("pt_date", pl.col("m").cast(pl.Int16), "tm", pl.col("agent").cast(pl.Int8), "a", "n", "lat", "n_lat", "api",
                     "err", "room", "lab").sort("pt_date", "m", "agent")
        assert not set(g["pt_date"].unique().to_list()) & held
        g.write_parquet(OUT / "grid" / f"{u['unit_id']}.parquet", compression="zstd")
        units.append({"unit_id": u["unit_id"], "goal_no": u["goal_no"], "regime": u["regime"], "n_days": len(days),
                      "first_day": days[0], "last_day": days[-1], "n_agents": g["agent"].n_unique(),
                      "n_rooms": len(u["rooms"] or []), "rows": g.height, "n_lat_minutes": int(g["lat"].is_not_null().sum()),
                      "n_api_minutes": int(g["api"].is_not_null().sum())})
        if not holdout_units:
            print(units[-1], flush=True)
    pl.DataFrame(units).write_parquet(OUT / "units.parquet")
    (OUT / "labs.json").write_text(json.dumps(labs))
    prov_path = OUT / "_provenance.json"
    prov = json.loads(prov_path.read_text()) if prov_path.exists() else {}
    prov.update({"built_by": "hypotheses/H66-platform-latency-field/scheme/build.py", "git_commit": git_commit(),
                 "inputs": [{"source": "ai-village", "revision": REVISION,
                             "tables": ["shared/call_windows", "shared/turn_errors", "shared/roster", "shared/rooms_timeline",
                                        "shared/period_units", "shared/calendar"]}],
                 "params": {"act_kinds": ACT_KINDS, "infra_err": INFRA, "turnaround": "t_first - t_prev_end, gap_kind busy, cu, 0<ta<600 s",
                            "regimes": ["II", "III"], "non_holdout_only": not holdout_units, "claude_code_excluded": True},
                 "built_at": dt.datetime.now(dt.timezone.utc).isoformat()})
    prov_path.write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    main()
