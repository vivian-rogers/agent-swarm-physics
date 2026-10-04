"""H120 scheme: 1-min activity and talk spin grids of the core agents on each day's all-present window, per window.

Windows: replication units 4c, 6b, 8, 13, 19a, 27, 38a, 51g (period_units, >= 8 non-holdout days) and the natives
G38 (all #38 days) and 51main (all non-holdout #51 days, units 51a-51l). Holdout days are never read (asserted).

Rules (card, Data scheme): core agents = agents with a record (state >= 2) on >= 90% of the window's days; days on
which a core agent has no record are dropped; trim = shared nulls.all_present_window over the core agents (minutes in
which every core agent is between its first and last record). Spins: activity = state >= 3; talk = talk > 0.

Outputs: data/processed/H120-period-ness-stationarity/windows.parquet, grids/<window>.npz, _provenance.json
Usage: uv run python hypotheses/H120-period-ness-stationarity/scheme/build.py
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

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import git_commit, holdout_mask  # noqa: E402
from nulls import all_present_window  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H120-period-ness-stationarity"
UNITS = ("4c", "6b", "8", "13", "19a", "27", "38a", "51g")
CORE_SHARE = 0.9


def windows() -> dict:
    U = pl.read_parquet(SH / "period_units.parquet")
    cal = pl.read_parquet(SH / "calendar.parquet")
    W = {}
    for u in UNITS:
        r = U.filter(pl.col("unit_id") == u).row(0, named=True)
        W[u] = {"goal": r["goal_no"], "days": sorted(r["days"]), "kind": "unit"}
    W["G38"] = {"goal": 38, "days": sorted(cal.filter((pl.col("goal_no") == 38) & ~pl.col("holdout"))["pt_date"].to_list()),
                "kind": "period"}
    W["51main"] = {"goal": 51, "days": sorted(cal.filter((pl.col("goal_no") == 51) & ~pl.col("holdout"))["pt_date"].to_list()),
                   "kind": "period"}
    for k, w in W.items():
        hm = holdout_mask(w["days"], [w["goal"]] * len(w["days"]))
        assert not any(hm), f"held-out day in window {k}"
    return W


def build_window(name: str, w: dict, ab: pl.LazyFrame, cal: pl.DataFrame) -> dict:
    df = ab.filter(pl.col("pt_date").is_in(w["days"])).collect()
    rec = df.filter(pl.col("state") >= 2).group_by("agent").agg(pl.col("pt_date").n_unique().alias("nd"))
    nd = len(w["days"])
    core = sorted(rec.filter(pl.col("nd") >= CORE_SHARE * nd)["agent"].to_list())
    days_kept, dropped, grids = [], [], {}
    for d in w["days"]:
        x = df.filter((pl.col("pt_date") == d) & pl.col("agent").is_in(core))
        present_agents = set(x.filter(pl.col("state") >= 2)["agent"].unique().to_list())
        if set(core) - present_agents:
            dropped.append(d)
            continue
        T = int(x["minute"].max()) + 1
        st = np.ones((T, len(core)), np.int8)
        tk = np.zeros((T, len(core)), np.int16)
        ai = {a: i for i, a in enumerate(core)}
        st[x["minute"].to_numpy(), [ai[a] for a in x["agent"].to_list()]] = x["state"].to_numpy()
        tk[x["minute"].to_numpy(), [ai[a] for a in x["agent"].to_list()]] = x["talk"].to_numpy()
        rec_m = st >= 2
        pres = np.zeros_like(rec_m)
        for j in range(len(core)):
            idx = np.flatnonzero(rec_m[:, j])
            pres[idx[0]: idx[-1] + 1, j] = True
        trim = all_present_window(pres)
        if trim.sum() < 30:
            dropped.append(d)
            continue
        # keep the longest contiguous trimmed run (transitions only inside it)
        runs, cur = [], []
        for t in np.flatnonzero(trim):
            if cur and t != cur[-1] + 1:
                runs.append(cur)
                cur = []
            cur.append(t)
        runs.append(cur)
        mins = np.array(max(runs, key=len))
        grids[d] = {"act": (st[mins] >= 3).astype(np.uint8), "talk": (tk[mins] > 0).astype(np.uint8),
                    "trim_len": len(mins), "n_trim_runs": len(runs)}
        days_kept.append(d)
    wd = dict(zip(cal["pt_date"].to_list(), cal["weekday"].to_list()))
    np.savez_compressed(OUT / "grids" / f"{name}.npz",
                        days=np.array(days_kept), core=np.array(core),
                        weekday=np.array([wd[d] for d in days_kept]),
                        trim_len=np.array([grids[d]["trim_len"] for d in days_kept]),
                        **{f"act_{i}": grids[d]["act"] for i, d in enumerate(days_kept)},
                        **{f"talk_{i}": grids[d]["talk"] for i, d in enumerate(days_kept)})
    return {"window": name, "goal": w["goal"], "kind": w["kind"], "n_days": nd, "n_kept": len(days_kept),
            "dropped": dropped, "core": core, "n_core": len(core),
            "minutes": int(sum(grids[d]["trim_len"] for d in days_kept)),
            "first_day": w["days"][0], "last_day": w["days"][-1]}


def main():
    (OUT / "grids").mkdir(parents=True, exist_ok=True)
    W = windows()
    ab = pl.scan_parquet(SH / "activity_bins_fixed.parquet")
    cal = pl.read_parquet(SH / "calendar.parquet")
    rows = []
    for k, w in W.items():
        r = build_window(k, w, ab, cal)
        rows.append(r)
        print(k, r["n_kept"], "/", r["n_days"], "days; core", r["n_core"], "; minutes", r["minutes"], "; dropped", r["dropped"])
    pl.DataFrame(rows).write_parquet(OUT / "windows.parquet")
    prov = {"built_by": "hypotheses/H120-period-ness-stationarity/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "tables": ["activity_bins_fixed", "calendar", "period_units"]}],
            "params": {"units": list(UNITS), "core_share": CORE_SHARE, "trim": "nulls.all_present_window over core agents; "
                       "longest contiguous run", "spins": {"act": "state>=3", "talk": "talk>0"}},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    main()
