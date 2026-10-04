"""H115 data scheme: per-call talk spins with read-gated and in-flight inputs for one goal period.

  uv run python hypotheses/H115-debate-judge-role-recovery/scheme/build.py --period G12   (also G26, G35, G44)

Writes data/processed/H115-debate-judge-role-recovery/G<NN>/: calls.parquet (one row per non-summary call, with the
window id and, for G12, the debate phase), xr.npy / xp.npy (calls x agents uint8), agents.json, windows.parquet,
validation.json (read rule vs the context ledger), _provenance.json. Codes only, no text; held-out rows refused.

G12 windows come from DQ6 `phase` rows only (they carry no agent column); the `judge`, `team` and `debate_result`
rows are never loaded here (blind protocol). Replication windows (G26, G35, G44) use DQ6 `leader` rows for timing.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import callspins as CS  # noqa: E402

ROOT = CS.ROOT
SH = CS.SH
OUTROOT = ROOT / "data/processed/H115-debate-judge-role-recovery"
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit  # noqa: E402

UTC = dt.timezone.utc
GOAL = {"G12": 12, "G26": 26, "G35": 35, "G44": 44}


def gt_rows(goal: int, kinds: list[str]) -> pl.DataFrame:
    """DQ6 rows of the listed kinds only (lazy filter: other kinds never materialize)."""
    return (pl.scan_parquet(SH / "ground_truth_labels.parquet")
            .filter((pl.col("goal_no") == goal) & pl.col("preferred") & ~pl.col("holdout")
                    & pl.col("label_kind").is_in(kinds)).collect())


def windows_for(period: str) -> pl.DataFrame:
    """Window table: win (str), t0, t1 (UTC), room (-9 = any), plus kind-specific columns."""
    g = GOAL[period]
    if period == "G12":
        ph = gt_rows(12, ["phase"]).select("unit", "value", "t_valid_from", "t_valid_to")
        w = (ph.group_by("unit").agg(pl.col("t_valid_from").min().alias("t0"), pl.col("t_valid_to").max().alias("t1"))
             .sort("t0").rename({"unit": "win"}).with_columns(pl.lit(-9).cast(pl.Int8).alias("room")))
        return w
    if period == "G26":
        ld = gt_rows(26, ["leader"]).sort("t_valid_from")
        T1 = ld["t_valid_from"][0]
        T2 = ld["t_valid_from"][1]
        cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("goal_no") == 26).sort("pt_date")
        rows = []
        for d, a, b in cal.select("pt_date", "win_start", "win_end").iter_rows():
            a2, b2 = a, b + dt.timedelta(minutes=1)
            if b2 <= T1:
                continue
            if a2 < T1 < b2:
                a2 = T1
            if a2 < T2 < b2:
                rows.append((f"{d}_term1", a2, T2))
                rows.append((f"{d}_term2", T2, b2))
            else:
                rows.append((f"{d}_term1" if b2 <= T2 else f"{d}_term2", a2, b2))
        return pl.DataFrame(rows, schema={"win": pl.String, "t0": pl.Datetime("us", "UTC"),
                                          "t1": pl.Datetime("us", "UTC")}, orient="row").with_columns(
            pl.lit(-9).cast(pl.Int8).alias("room"))
    if period == "G35":
        ld = gt_rows(35, ["leader"])
        cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("goal_no") == 35)
        rows = []
        for unit, det in ld.select("unit", "detail").unique().iter_rows():
            day = unit.replace("day_", "")
            room = 2 if "room=best" in det else 3
            c = cal.filter(pl.col("pt_date") == day)
            rows.append((f"{day}_{'best' if room == 2 else 'rest'}", c["win_start"][0],
                         c["win_end"][0] + dt.timedelta(minutes=1), room))
        return pl.DataFrame(rows, schema={"win": pl.String, "t0": pl.Datetime("us", "UTC"),
                                          "t1": pl.Datetime("us", "UTC"), "room": pl.Int8}, orient="row").sort("t0", "win")
    if period == "G44":
        ld = gt_rows(44, ["leader"])
        t_from = ld["t_valid_from"][0]
        cal = pl.read_parquet(SH / "calendar.parquet").filter((pl.col("goal_no") == 44) & ~pl.col("holdout")).sort("pt_date")
        rows = []
        for d, a, b in cal.select("pt_date", "win_start", "win_end").iter_rows():
            b2 = b + dt.timedelta(minutes=1)
            if b2 <= t_from:
                continue
            rows.append((f"{d}_best", max(a, t_from), b2, 2))
        return pl.DataFrame(rows, schema={"win": pl.String, "t0": pl.Datetime("us", "UTC"),
                                          "t1": pl.Datetime("us", "UTC"), "room": pl.Int8}, orient="row")
    raise ValueError(period)


def phases_g12() -> pl.DataFrame:
    return gt_rows(12, ["phase"]).select("unit", "value", "t_valid_from", "t_valid_to").sort("t_valid_from")


def build(period: str, out: Path | None = None) -> dict:
    g = GOAL[period]
    out = out or (OUTROOT / period)
    out.mkdir(parents=True, exist_ok=True)
    calls = CS.load_calls([g])
    msgs = CS.load_messages([g])
    agents = sorted(int(a) for a in calls["agent"].unique().to_list())
    calls, XR, XP = CS.build_inputs(calls, msgs, agents)
    keep = CS.all_present_trim(calls)
    calls = calls.with_columns(pl.Series("trim", keep))
    W = windows_for(period)
    tc = calls["t_call"]
    win = np.full(calls.height, None, dtype=object)
    for w, t0, t1, room in W.select("win", "t0", "t1", "room").iter_rows():
        m = ((tc >= t0) & (tc < t1)).to_numpy()
        if room != -9:
            m &= calls["room"].to_numpy() == room
        win[m] = w
    calls = calls.with_columns(pl.Series("win", win.tolist(), dtype=pl.String))
    if period == "G12":
        ph = phases_g12()
        phase = np.full(calls.height, None, dtype=object)
        for unit, val, a, b in ph.iter_rows():
            m = ((tc >= a) & (tc < b)).to_numpy()
            phase[m] = val
        calls = calls.with_columns(pl.Series("phase", phase.tolist(), dtype=pl.String))
    val = CS.validate_against_ledger(calls, XR, agents)
    calls.write_parquet(out / "calls.parquet", compression="zstd")
    np.save(out / "xr.npy", XR)
    np.save(out / "xp.npy", XP)
    (out / "agents.json").write_text(json.dumps(agents))
    W.write_parquet(out / "windows.parquet")
    (out / "validation.json").write_text(json.dumps(val, indent=1))
    prov = {"built_by": "hypotheses/H115-debate-judge-role-recovery/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["call_windows", "context_ledger_turns", "context_ledger_items", "chat_core",
                                   "calendar", "ground_truth_labels (phase / leader rows only)"]}],
            "params": {"period": period, "goal": g, "trim_min_calls": 20, "summary_calls": "dropped",
                       "exclude_recipients": [19]},
            "built_at": dt.datetime.now(UTC).isoformat()}
    (out / "_provenance.json").write_text(json.dumps(prov, indent=1))
    return {"period": period, "n_calls": calls.height, "agents": agents, "n_windows": W.height,
            "calls_in_windows": int(calls["win"].is_not_null().sum()), "validation": val}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", required=True, choices=sorted(GOAL))
    a = ap.parse_args()
    print(json.dumps(build(a.period), indent=1, default=str))
