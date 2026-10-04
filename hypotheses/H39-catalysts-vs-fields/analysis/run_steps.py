"""H39 step levers: goal kickoffs (NE34), room changes (NE42, NE15), scaffold changes (NE03, NE06, NE07, NE10, NE16,
NE17, NE18 and three unnumbered CHANGELOG prompt steps), each pre days vs post days on a balanced agent panel,
judged against within-goal day-boundary placebos of the same era (regime x hours) and window shape.

States: B4 / B6 behavior (minute grid, lag 1 min) and C6 content clusters (k-means k = 6 on regime-whitened
agent_win30 vectors fitted per comparison; lag one 30-min window).

Usage: uv run python hypotheses/H39-catalysts-vs-fields/analysis/run_steps.py [--quick]
Writes data/processed/H39-catalysts-vs-fields/steps/steps_results.json
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2" if _v == "POLARS_MAX_THREADS" else "1"

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl
from scipy.cluster.vq import kmeans2

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h39lib as L  # noqa: E402

ROOT = L.ROOT
SH = ROOT / "data/processed/shared"
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import load_whitener  # noqa: E402

B6_TO_B4 = np.array([0, 0, 0, 1, 2, 3], np.int8)
HOLD = json.loads((ROOT / "hypotheses/holdout.json").read_text())

SCAFFOLD = [
    # id, first day with the change (PT), goal, kind, folder, label
    ("NE10", "2026-02-13", 30, "nudger", "NE10", "auto-nudger switched on (first nudges 02-13)"),
    ("NE07", "2025-12-04", 21, "prompt-activity", "NE07", "prompt: 'don't do nothing'"),
    ("NE16", "2026-03-26", 36, "unstick-fix", "NE16", "fix of empty Anthropic responses that left agents stuck; memory-instruction fix"),
    ("NE17", "2026-04-14", 38, "tool", "NE17", "outreach approval system"),
    ("NE18", "2026-04-20", 38, "tool", "NE18", "history search: verbatim segments, 10-day window"),
    ("NE03", "2025-08-20", 10, "channel", "NE03", "number of chat messages fetched into context limited"),
    ("NE06", "2025-11-20", 20, "prompt+internal", "NE06", "internal-review prompt changes; Gemini one tool call per turn"),
    ("S20250801", "2025-08-01", 8, "prompt-activity", "G08", "prompt: encouraged the agent to keep going"),
    ("S20251022", "2025-10-22", 18, "prompt-activity", "G18", "prompt: keep working right up until the end of each day"),
    ("S20260528", "2026-05-28", 44, "prompt-style", "G44", "prompt: keep messages short (text-only); first-person # bash comments"),
]


def era_of(regime: str, hours) -> str:
    if regime == "I":
        return "I-early" if (hours is None or hours <= 3) else "I-4h"
    if regime == "II":
        return "II"
    return "III-8h" if (hours or 4) >= 8 else "III-4h"


class Data:
    def __init__(self):
        cal = pl.read_parquet(SH / "calendar.parquet").filter((pl.col("window_s") > 0) & ~pl.col("holdout"))
        self.cal = cal.sort("pt_date")
        self.meta = {r["pt_date"]: r for r in self.cal.iter_rows(named=True)}
        for d, r in self.meta.items():
            assert not any(w["start"] <= d < w["end"] for w in HOLD["ne_windows"])
            assert r["goal_no"] not in HOLD["goal_periods_held_out"]
        st = pl.read_parquet(L.OUT / "states_b6.parquet").filter(pl.col("present"))
        self.seqs = {}
        for (d, a), g in st.sort("pt_date", "agent", "minute").group_by(["pt_date", "agent"], maintain_order=True):
            if d not in self.meta:
                continue
            nrec = g["n_rec"].to_numpy()
            occ = np.flatnonzero(nrec > 0)
            if len(occ) < 2:
                continue
            x = g["coarse_min"].to_numpy()[occ[0]:occ[-1] + 1].astype(np.int8)
            self.seqs.setdefault(d, {})[int(a)] = x
        idx = pl.read_parquet(SH / "embeddings/agent_win30.parquet").with_row_index("row").filter(~pl.col("holdout"))
        self.win = {}
        for (d, a), g in idx.group_by(["pt_date", "agent"]):
            self.win.setdefault(d, {})[int(a)] = (g["win30"].to_numpy(), g["row"].to_numpy())
        self.V = np.load(SH / "embeddings/agent_win30_vec.npy", mmap_mode="r")
        self.wh = {r: load_whitener(r, 32) for r in ("I", "II", "III")}

    def goal_days(self, g: int, regime: str | None = None) -> list[str]:
        return [d for d, r in self.meta.items() if r["goal_no"] == g and (regime is None or str(r["regime"]) == regime)]


def behavior_units(D: Data, pre: list[str], post: list[str]):
    ap = set().union(*[set(D.seqs.get(d, {})) for d in pre])
    bp = set().union(*[set(D.seqs.get(d, {})) for d in post])
    agents = sorted(ap & bp)
    out = {}
    for q6 in (False, True):
        us = []
        for days in (pre, post):
            seqs, ag, dd = [], [], []
            for k, d in enumerate(days):
                for a in agents:
                    x = D.seqs.get(d, {}).get(a)
                    if x is None:
                        continue
                    seqs.append(x if q6 else B6_TO_B4[x])
                    ag.append(a)
                    dd.append(k)
            us.append(L.build_unit(seqs, ag, dd, None, 6 if q6 else 4) if seqs else None)
        out["b6" if q6 else "b4"] = us
    return out, agents


def content_units(D: Data, pre: list[str], post: list[str], regime: str, seed: int = 0):
    ap = set().union(*[set(D.win.get(d, {})) for d in pre])
    bp = set().union(*[set(D.win.get(d, {})) for d in post])
    agents = sorted(ap & bp)
    rows, keys = [], []
    for side, days in enumerate((pre, post)):
        for k, d in enumerate(days):
            for a in agents:
                v = D.win.get(d, {}).get(a)
                if v is None:
                    continue
                for w, r in zip(*v):
                    rows.append(r)
                    keys.append((side, k, a, int(w)))
    if len(rows) < 60:
        return None, None
    X = D.wh[regime](np.asarray(D.V[np.array(rows)], np.float32))
    X /= np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-9)
    np.random.seed(seed)
    _, lab = kmeans2(X, 6, minit="++", seed=seed, iter=30)
    us = []
    for side in (0, 1):
        per = {}
        for (s, k, a, w), l in zip(keys, lab):
            if s == side:
                per.setdefault((k, a), {})[w] = l
        seqs, ag, dd = [], [], []
        for (k, a), m in sorted(per.items()):
            hi = max(m)
            x = np.full(hi + 1, -1, np.int8)
            for w, l in m.items():
                x[w] = l
            seqs.append(x)
            ag.append(a)
            dd.append(k)
        us.append(L.build_unit(seqs, ag, dd, None, 6))
    return us, agents


def compare(D: Data, pre: list[str], post: list[str], B: int, content: bool = True, keep=False) -> dict:
    regime = str(D.meta[post[0]]["regime"])
    bu, agents = behavior_units(D, pre, post)
    out = dict(pre=pre, post=post, regime=regime, n_agents=len(agents))
    if len(agents) < 3 or bu["b4"][0] is None or bu["b4"][1] is None:
        out["status"] = "too few agents"
        return out
    out["b4"] = L.run_step(bu["b4"][0], bu["b4"][1], B=B, keep_draws=keep)
    out["b6"] = L.run_step(bu["b6"][0], bu["b6"][1], B=max(B // 2, 2))
    if content:
        cu, cag = content_units(D, pre, post, regime)
        if cu is not None and cu[0].x.size and cu[1].x.size and cu[0].cum[-1].sum() >= 30 and cu[1].cum[-1].sum() >= 30:
            out["c6"] = L.run_step(cu[0], cu[1], B=max(B // 2, 2))
            out["c6"]["n_agents"] = len(cag)
    out["status"] = "ok"
    return out


def all_boundaries(D: Data, shape, exclude_days: set[str]):
    """Within-goal day boundaries with `shape` = (n_pre, n_post) days, same regime on both sides."""
    dpre, dpost = shape
    out = []
    for g in sorted({r["goal_no"] for r in D.meta.values()}):
        for regime in ("I", "II", "III"):
            days = sorted(D.goal_days(g, regime))
            for i in range(dpre, len(days) - dpost + 1):
                pre, post = days[i - dpre:i], days[i:i + dpost]
                win = set(pre) | set(post)
                if win & exclude_days:
                    continue
                out.append((g, pre, post))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    B = 50 if a.quick else 300
    D = Data()
    print(f"loaded {time.time() - t0:.0f}s; {len(D.meta)} non-holdout days", flush=True)
    dates = sorted(D.meta)
    pos = {d: i for i, d in enumerate(dates)}
    # ---------------- steps to test
    steps = []
    for sid, date, g, kind, folder, label in SCAFFOLD:
        days = sorted(D.goal_days(g, str(D.meta[date]["regime"])))
        i = days.index(date)
        pre, post = days[max(0, i - 2):i], days[i:i + 2]
        steps.append(dict(id=sid, cls="scaffold", kind=kind, folder=folder, label=label, goal=g, pre=pre, post=post))
    goals = sorted({r["goal_no"] for r in D.meta.values()})
    for g in goals:
        if g + 1 not in goals:
            continue
        a_days = sorted(D.goal_days(g))
        b_days = sorted(D.goal_days(g + 1))
        rb = str(D.meta[b_days[0]]["regime"])
        a_days = [d for d in a_days if str(D.meta[d]["regime"]) == rb]
        b_days = [d for d in b_days if str(D.meta[d]["regime"]) == rb]
        if not a_days or not b_days:
            continue
        sid = f"K{g:02d}-{g + 1:02d}"
        label = f"kickoff #{g} -> #{g + 1}"
        flag = {6: "coincides with B (human helpers, 2025-07-16)", 39: "NE42 merge (05-04)", 40: "NE42 split (05-11)",
                35: "post side cut at the 03-24 regime boundary", 36: "pre side includes NE16 (03-26)"}.get(g, "")
        steps.append(dict(id=sid, cls="kickoff", kind="kickoff", folder="NE34", label=label, goal=g, flag=flag,
                          pre=a_days[-2:], post=b_days[:2]))
    # NE15: pre side held out; #33 (last 2 days) vs #35 (first 2 days), descriptive
    steps.append(dict(id="NE15", cls="room", kind="room-split", folder="NE15", label="#best/#rest split (03-16), vs #33",
                      goal=35, pre=sorted(D.goal_days(33))[-2:], post=sorted(D.goal_days(35))[:2],
                      flag="pre side is #33 (two weeks earlier; #34 held out); descriptive"))
    test_days = set()
    for s in steps:
        if s["cls"] == "scaffold":
            k = pos[s["post"][0]]
            test_days |= {dates[j] for j in range(max(0, k - 1), min(len(dates), k + 2))}
    # ---------------- run tests
    res = []
    for s in steps:
        r = compare(D, s["pre"], s["post"], B, keep=True)
        r.update({k: v for k, v in s.items() if k not in ("pre", "post")})
        r["shape"] = [len(s["pre"]), len(s["post"])]
        r["era"] = era_of(str(D.meta[s["post"][0]]["regime"]), D.meta[s["post"][0]]["documented_hours"])
        res.append(r)
        b4 = r.get("b4", {})
        print(f"  {s['id']}: agents {r.get('n_agents')} K {b4.get('K', float('nan')):.3f} phi {b4.get('phi', float('nan')):.3f}"
              f" c6 phi {r.get('c6', {}).get('phi', float('nan')):.3f} ({time.time() - t0:.0f}s)", flush=True)
    # ---------------- placebos per shape
    shapes = sorted({tuple(r["shape"]) for r in res})
    placebo = {}
    for sh in shapes:
        bl = all_boundaries(D, sh, test_days)
        pl_ = []
        for g, pre, post in bl:
            r = compare(D, pre, post, 2)
            if r.get("status") != "ok":
                continue
            r["goal"] = g
            r["era"] = era_of(str(D.meta[post[0]]["regime"]), D.meta[post[0]]["documented_hours"])
            pl_.append(r)
        placebo[f"{sh[0]}x{sh[1]}"] = pl_
        print(f"  placebo {sh}: {len(pl_)} boundaries ({time.time() - t0:.0f}s)", flush=True)
    # ---------------- judge
    for r in res:
        if r.get("status") != "ok":
            continue
        pool = placebo[f"{r['shape'][0]}x{r['shape'][1]}"]
        same = [p for p in pool if p["era"] == r["era"]]
        use = same if len(same) >= 10 else pool
        r["placebo_pool"] = "era" if len(same) >= 10 else "all eras"
        r["n_placebo"] = len(use)
        for fam in ("b4", "b6", "c6"):
            if fam in r:
                pf = [p[fam] for p in use if fam in p]
                r[f"judge_{fam}"] = L.judge_step(r[fam], pf)
    out = dict(steps=res, placebo={k: [{kk: p.get(kk) for kk in ("goal", "era", "pre", "post", "n_agents")}
                                       | {f: {x: p[f][x] for x in ("K", "phi", "dpi") if f in p} for f in ("b4", "c6")}
                                       for p in v] for k, v in placebo.items()},
               runtime_s=time.time() - t0)
    L.jdump(out, L.OUT / "steps" / "steps_results.json")
    # bootstrap draws of the B4 step statistics (for class probabilities)
    np.savez_compressed(L.OUT / "steps" / "boot_draws.npz",
                        **{f"{r['id']}__{k}": np.asarray(v, np.float32) for r in res if "b4" in r and "_boot" in r["b4"]
                           for k, v in r["b4"]["_boot"].items()})
    print(f"done {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
