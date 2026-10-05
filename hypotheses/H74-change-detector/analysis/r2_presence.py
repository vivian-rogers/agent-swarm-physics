"""H74 round 2, R2 on real data: presence/retirement rule for search-answer format markers (card: Round 2, Amendment
R2-A1 item 5). Primary: accumulating beta-binomial retirement (rho from the real day-to-day overdispersion, written in
synthetic_presence.json); secondary: the pre-registered one-day rule and the appearance rule. Non-reserved days only.
Run (after r2_synthetic.py and r2_monitor.py): uv run python hypotheses/H74-change-detector/analysis/r2_presence.py
Output: data/processed/H74-change-detector/r2/presence.json, presence_days.parquet
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r2lib as R  # noqa: E402
from r2_common import CLASSES, LABEL_MAP, MARKERS, OUT, load_frame, marker_day_table  # noqa: E402

NAMED = {"NE40": "2026-04-20", "OUT0331": "2026-03-31", "NE45": "2026-07-29", "NE14": "2026-03-24"}


def main():
    rho = json.loads((OUT / "synthetic_presence.json").read_text())["rho_median"]
    rng = np.random.default_rng(20261006)
    res = {"rho": rho}
    for cat in ("prereg", "ext"):
        fr = load_frame(cat)
        tab, n, nag, tag = marker_day_table(fr)
        scored = n >= 3
        rules = {}
        for rule in ("acc", "pre", "appear"):
            A = {}
            for m in MARKERS:
                if rule == "acc":
                    A[m] = R.presence_retire_acc(n, tab[m], rho)
                elif rule == "pre":
                    A[m] = R.presence_retire(n, tab[m])
                else:
                    A[m] = R.presence_appear(n, tab[m], tag[m])
            P = np.sum([A[m] for m in MARKERS], 0)
            alarm = P >= 1
            pool = fr.P2 & scored
            k, nn = int(alarm[pool].sum()), int(pool.sum())
            sc_idx = np.where(scored)[0]
            spos = {int(t): j for j, t in enumerate(sc_idx)}
            named = {}
            for ne, d in NAMED.items():
                i = fr.day_pos[d]
                win = [j for j in fr.nbr[i]]
                hit = bool(alarm[win].any())
                # first alarm within 5 scored days after day 0 (delay in scored days)
                j0 = np.searchsorted(sc_idx, i)
                later = [(int(spos[int(t)] - j0), fr.dl[t], [m for m in MARKERS if A[m][t]]) for t in sc_idx[j0:j0 + 6] if alarm[t]]
                named[ne] = {"hit_pm1": hit, "first_within5": later[0] if later else None,
                             "markers_pm1": sorted({m for t in win for m in MARKERS if A[m][t]})}
            rules[rule] = {"far_P2_scored": [k, nn, k / nn if nn else None, list(R.wilson(k, nn))],
                           "n_alarm_days": int(alarm.sum()), "n_scored_days": int(scored.sum()),
                           "alarm_days": [(fr.dl[t], [m for m in MARKERS if A[m][t]], bool(fr.dist[t] <= 1)) for t in np.where(alarm)[0]],
                           "named": named,
                           "classes": fr.class_hits(alarm, CLASSES, rng, 2000, LABEL_MAP)}
            if rule == "acc" and cat == "prereg":
                pl.DataFrame({"pt_date": fr.dl, "n_answers": n, "P_acc": P, "alarm_acc": alarm, "P2": fr.P2,
                              "scored": scored}).write_parquet(OUT / "presence_days.parquet")
        # union with the monitor (same catalog)
        md = pl.read_parquet(OUT / ("monitor_days.parquet" if cat == "prereg" else "monitor_days_ext.parquet"))
        mon = md["alarm_monitor"].to_numpy()
        accA = np.sum([R.presence_retire_acc(n, tab[m], rho) for m in MARKERS], 0) >= 1
        u = mon | accA
        rules["monitor_plus_presence"] = {"far": fr.far(u), "classes": {k: (v["k"], v["n"], v["hit"]) for k, v in
                                                                         fr.class_hits(u, CLASSES, None, 0, LABEL_MAP).items()}}
        res[cat] = rules
    (OUT / "presence.json").write_text(json.dumps(res, indent=1, default=float))
    for cat in ("prereg", "ext"):
        for rule in ("acc", "pre", "appear"):
            r = res[cat][rule]
            print(cat, rule, "FAR", r["far_P2_scored"][:3], "alarm days", r["n_alarm_days"], "/", r["n_scored_days"])
            print("   named", json.dumps(r["named"], default=int))
            print("   classes", {k: (v["k"], v["n"], round(v["p_rand"], 3)) for k, v in r["classes"].items()})
            if rule == "acc":
                print("   days", r["alarm_days"])
        m = res[cat]["monitor_plus_presence"]
        print(cat, "monitor+presence FAR", m["far"]["P2"]["k"], m["far"]["P2"]["n"], m["classes"])


if __name__ == "__main__":
    main()
