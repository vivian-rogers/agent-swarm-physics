"""H127 descriptive rise curve (post hoc diagnostic after the real run; labelled as such in the card): mean normalized
day-1 excess alignment y = (a - P_i) / A_i of rising agents, binned by own calls since the read-out call and by hours
since t0, pooled over kickoffs with agents weighted equally. A_i = the agent's day-1 plateau (mean a over calls >= 64
since read-out); P_i = pre level. Also by call-rate half (slow / fast) within kickoff.
Writes data/processed/H127-content-trails-goal-call-clock/NE34/rise_curve.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h127lib as L  # noqa: E402

CB = [(-1e9, 0.5), (0.5, 1.5), (1.5, 3.5), (3.5, 7.5), (7.5, 15.5), (15.5, 31.5), (31.5, 63.5), (63.5, 1e9)]
CL = ["before", "1", "2-3", "4-7", "8-15", "16-31", "32-63", "64+"]
HB = [(0, 0.05), (0.05, 0.15), (0.15, 0.5), (0.5, 1.5), (1.5, 1e9)]
HL = ["<3 min", "3-9 min", "9-30 min", "0.5-1.5 h", ">1.5 h"]


def curve(units, key, bins):
    per = []
    for u in units:
        x = u[key]; y = u["a"] - u["P"]
        late = y[u["c_ro"] >= 64]
        A = late.mean() if len(late) >= 4 else u["Delta"]
        if not np.isfinite(A) or A <= 0.02:
            continue
        row = [np.mean(y[(x > lo) & (x <= hi)]) / A if ((x > lo) & (x <= hi)).sum() else np.nan for lo, hi in bins]
        per.append(row)
    P = np.array(per)
    n = np.isfinite(P).sum(0)
    return dict(mean=np.nanmean(P, 0).tolist(), se=(np.nanstd(P, 0, ddof=1) / np.sqrt(np.maximum(n, 1))).tolist(), n=n.tolist())


def main():
    out = {}
    for cfg in ("bge_white", "gte_white"):
        allu, slow, fast = [], [], []
        for des in [d for d in L.tables()["k"].filter(pl.col("kind") == "kickoff")["design"].to_list()]:
            us = [u for u in L.build_units(des, cfg) if u["rising"]]
            allu += us
            if len(us) >= 4:
                r = np.array([u["r"] for u in us]); o = np.argsort(r); h = len(us) // 2
                slow += [us[j] for j in o[:h]]; fast += [us[j] for j in o[-h:]]
        out[cfg] = dict(calls_ro=curve(allu, "c_ro", CB), hours_t0=curve(allu, "h", HB),
                        calls_ro_slow=curve(slow, "c_ro", CB), calls_ro_fast=curve(fast, "c_ro", CB),
                        hours_t0_slow=curve(slow, "h", HB), hours_t0_fast=curve(fast, "h", HB),
                        n_agents=len(allu), labels_calls=CL, labels_hours=HL)
        for k in ("calls_ro", "hours_t0", "calls_ro_slow", "calls_ro_fast"):
            print(cfg, k, [None if m != m else round(m, 2) for m in out[cfg][k]["mean"]], out[cfg][k]["n"])
    (L.DATA / "NE34/rise_curve.json").write_text(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
