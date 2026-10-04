"""H124 scheme: per-call step tables (N = 4 closed-roster regime-I units), 1-min grids, and the N = 21 #51-head
schedule (order only) for the synthetic.

Outputs in data/processed/H124-small-n-meanfield-benchmark/:
  percall/<unit>.parquet  day, step, agent (local 0..3), talk (+-1), plus s0..s3 = latest talk spins of the four
                          agents just before the call (own previous call included); first/last 10% of each day's calls
                          and steps before all four have called are dropped.
  grid/<unit>.npz         per day: talk and activity spins (T x 4, +-1) inside the all-present window.
  schedule_51head.npz     per day: actor index sequence of the 21 most frequent callers on the first 10 non-holdout
                          #51 days (no states).
  _provenance.json
Usage: uv run python hypotheses/H124-small-n-meanfield-benchmark/scheme/build.py
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import git_commit, holdout_mask  # noqa: E402
from nulls import all_present_window  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H124-small-n-meanfield-benchmark"
UNITS = ["2", "3", "4a", "4c", "5", "6a", "6b", "7", "8"]
EDGE = 0.10
MIN_CALLS = 5


def _cw(days, allow_holdout=False):
    q = pl.scan_parquet(SH / "call_windows.parquet").filter(pl.col("pt_date").is_in(days))
    if not allow_holdout:
        q = q.filter(~pl.col("holdout"))
    cw = q.select("turn_id", "agent", "pt_date", "goal_no", "talk", "t_call").collect()
    if allow_holdout:   # guarded confirm path only
        return cw
    hm = holdout_mask(cw["pt_date"].to_list(), cw["goal_no"].to_list())
    return cw.filter(~pl.Series(hm))


def build_percall(pu, roster_cc, units=UNITS, allow_holdout=False, write=True):
    """write=False returns {unit: frame} in memory (the guarded confirm path uses allow_holdout=True, write=False)."""
    (OUT / "percall").mkdir(parents=True, exist_ok=True)
    summ, mem = [], {}
    for u in units:
        r = pu.filter(pl.col("unit_id") == u).to_dicts()[0]
        cw = _cw(r["days"], allow_holdout).filter(~pl.col("agent").is_in(roster_cc))
        agents = sorted(cw.group_by("agent").len().sort("len", descending=True)["agent"].to_list()[:4])
        amap = {a: i for i, a in enumerate(agents)}
        frames = []
        for day in sorted(r["days"]):
            x = cw.filter((pl.col("pt_date") == day) & pl.col("agent").is_in(agents)).sort("t_call", "turn_id")
            cnt = dict(x.group_by("agent").len().iter_rows())
            if len(cnt) < 4 or min(cnt.values()) < MIN_CALLS:
                continue
            a = np.array([amap[v] for v in x["agent"].to_list()])
            tk = np.where(x["talk"].to_numpy(), 1, -1).astype(np.int8)
            cur = np.zeros(4, np.int8)
            prev = np.zeros((len(a), 4), np.int8)
            for t in range(len(a)):
                prev[t] = cur
                cur[a[t]] = tk[t]
            ok = np.all(prev != 0, axis=1)
            ix = np.flatnonzero(ok)
            lo, hi = int(len(ix) * EDGE), int(len(ix) * (1 - EDGE))
            ix = ix[lo:hi]
            frames.append(pl.DataFrame({"day": [day] * len(ix), "step": ix.astype(np.int32), "agent": a[ix].astype(np.int8),
                                        "talk": tk[ix], **{f"s{j}": prev[ix, j] for j in range(4)}}))
        if frames:
            P = pl.concat(frames)
            if not write:
                mem[u] = P
                continue
            P.write_parquet(OUT / "percall" / f"{u}.parquet", compression="zstd")
            summ.append({"unit": u, "goal_no": r["goal_no"], "agents": agents, "n_days": P["day"].n_unique(),
                         "n_rows": P.height, "talk_rate": float((P["talk"] > 0).mean())})
    return summ if write else mem


def build_grid(pu, roster_cc, units=UNITS, allow_holdout=False, write=True):
    (OUT / "grid").mkdir(parents=True, exist_ok=True)
    ab = pl.scan_parquet(SH / "activity_bins_fixed.parquet")
    out, mem = [], {}
    for u in units:
        r = pu.filter(pl.col("unit_id") == u).to_dicts()[0]
        days = r["days"] if allow_holdout else \
            [d for d, h in zip(r["days"], holdout_mask(r["days"], [r["goal_no"]] * len(r["days"]))) if not h]
        A = ab.filter(pl.col("pt_date").is_in(days)).select("pt_date", "minute", "agent", "talk", "state").collect()
        A = A.filter(~pl.col("agent").is_in(roster_cc))
        agents = sorted(A.filter(pl.col("state") >= 2).group_by("agent").len().sort("len", descending=True)["agent"]
                        .to_list()[:4])
        store = {}
        for d in sorted(days):
            x = A.filter((pl.col("pt_date") == d) & pl.col("agent").is_in(agents))
            if x.height == 0:
                continue
            T = int(x["minute"].max()) + 1
            st = np.zeros((T, 4), np.int8)
            tk = np.zeros((T, 4), np.int8)
            ai = np.array([agents.index(v) for v in x["agent"].to_list()])
            st[x["minute"].to_numpy(), ai] = x["state"].to_numpy()
            tk[x["minute"].to_numpy(), ai] = x["talk"].to_numpy() > 0
            rec = st >= 2
            span = np.zeros_like(rec)
            for i in range(4):
                w = np.flatnonzero(rec[:, i])
                if len(w):
                    span[w[0]:w[-1] + 1, i] = True
            m = all_present_window(span) if span.any(0).all() else np.zeros(T, bool)
            if m.sum() < 30:
                continue
            store[f"{d}_talk"] = np.where(tk[m] > 0, 1, -1).astype(np.int8)
            store[f"{d}_act"] = np.where(st[m] >= 3, 1, -1).astype(np.int8)
        if not write:
            mem[u] = store
            continue
        np.savez_compressed(OUT / "grid" / f"{u}.npz", **store)
        out.append({"unit": u, "grid_days": len(store) // 2, "grid_minutes": int(sum(v.shape[0] for k, v in store.items()
                                                                                    if k.endswith("_talk")))})
    return out if write else mem


def build_schedule51(pu):
    r = pu.filter((pl.col("goal_no") == 51) & (~pl.col("holdout"))).sort("seq")
    days = sorted({d for ds in r["days"].to_list() for d in ds})[:10]
    cw = _cw(days)
    top = cw.group_by("agent").len().sort("len", descending=True)["agent"].to_list()[:21]
    amap = {a: i for i, a in enumerate(sorted(top))}
    store = {}
    for d in days:
        x = cw.filter((pl.col("pt_date") == d) & pl.col("agent").is_in(top)).sort("t_call", "turn_id")
        store[d] = np.array([amap[v] for v in x["agent"].to_list()], np.int8)
    np.savez_compressed(OUT / "schedule_51head.npz", **store)
    return {"days": days, "n_steps": int(sum(len(v) for v in store.values())), "N": len(top)}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pu = pl.read_parquet(SH / "period_units.parquet")
    roster = pl.read_parquet(SH / "roster.parquet")
    cc = roster.filter(pl.col("claude_code"))["agent"].to_list()
    s1 = build_percall(pu, cc)
    s2 = build_grid(pu, cc)
    s3 = build_schedule51(pu)
    (OUT / "units.json").write_text(json.dumps({"percall": s1, "grid": s2, "schedule51": s3}, indent=1))
    (OUT / "_provenance.json").write_text(json.dumps({
        "built_by": "hypotheses/H124-small-n-meanfield-benchmark/scheme/build.py", "git_commit": git_commit(),
        "inputs": [{"source": "shared", "tables": ["call_windows", "activity_bins_fixed", "period_units", "roster"]}],
        "params": {"units": UNITS, "edge": EDGE, "min_calls": MIN_CALLS},
        "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}, indent=1))
    print(json.dumps({"percall": s1, "grid": s2, "schedule51": s3}, indent=1))


if __name__ == "__main__":
    main()
