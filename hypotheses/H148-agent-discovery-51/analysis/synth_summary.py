"""Summarize H148 synthetic validation (axis F): size, power and recovery per world and setting.

Reads data/processed/H148-agent-discovery-51/synthetic/*.jsonl and writes synthetic/summary.json.
Usage: uv run python hypotheses/H148-agent-discovery-51/analysis/synth_summary.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h148lib as L  # noqa: E402
from synthetic import is_false  # noqa: E402


def wilson(k: int, n: int, z: float = 1.96):
    if n == 0:
        return (math.nan, math.nan)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(c - h, 3), round(c + h, 3))


NB = 67      # agent (32) + artifact (33) + room (2) atoms; element atoms come after (synthetic worlds)


def worth(atoms, agents_worth: int) -> int:
    """agents' worth, or 2 for systems with >= 2 element atoms or a room (counted as multi like synthetic.evaluate)."""
    n_el = sum(a >= NB for a in atoms)
    room = any(a in (NB - 2, NB - 1) for a in atoms)
    return agents_worth if agents_worth >= 2 else (2 if (n_el >= 2 or room) else agents_worth)


def main():
    out = {}
    for f in sorted((L.OUT / "synthetic").glob("synthetic_*.jsonl")):
        rows = [json.loads(x) for x in f.read_text().splitlines() if x.strip()]
        by = {}
        for r in rows:
            by.setdefault(r["world"], []).append(r)
        res = {}
        for w, rs in by.items():
            n = len(rs)
            d = {"n_reps": n, "secs_mean": round(float(np.mean([r["secs"] for r in rs])), 1)}
            fm = [r["n_false_multi"] for r in rs]
            if "own" in rs[0] and "maxima" in rs[0]:
                # component rule (A9): a discovery is false when it is multi-agent and not inside one true component
                aw = {}
                for r in rs:
                    for h in ("0", "1"):
                        for m in r["maxima"][h]:
                            aw[tuple(m["atoms"])] = m["agents_worth"]
                fm = [sum(is_false(r, X, worth(X, aw.get(tuple(X), 2))) for X in r["discovered"]) for r in rs]
            d["false_multi_mean"] = round(float(np.mean(fm)), 3)
            k = sum(x > 0 for x in fm)
            d["worlds_with_false_multi"] = k
            d["worlds_with_false_multi_ci"] = wilson(k, n)
            for key in ("agent_single_share", "p1_share", "p2_share"):
                if key in rs[0]:
                    v = [r[key] for r in rs]
                    d[key] = round(float(np.mean(v)), 3)
                    d[key + "_min"] = round(float(np.min(v)), 3)
            for key in [k for k in rs[0] if k.startswith("rec_") or k.startswith("nest_")]:
                kk = sum(bool(r[key]) for r in rs)
                d[key] = round(kk / n, 3)
                d[key + "_ci"] = wilson(kk, n)
            if "n_field_disc" in rs[0]:
                d["field_disc_mean"] = round(float(np.mean([r["n_field_disc"] for r in rs])), 3)
            d["n_disc_mean"] = round(float(np.mean([r["n_disc"] for r in rs])), 2)
            # variant rule (reported, not primary): held out of sample in at least one direction
            if "maxima" in rs[0]:
                fm1, rec1, p2a = [], [], []
                for r in rs:
                    held = [m for h in ("0", "1") for m in r["maxima"][h] if m["holds"]]
                    planted = list(r["planted"].values())
                    jac = lambda a, b: len(set(a) & set(b)) / max(len(set(a) | set(b)), 1)  # noqa: E731
                    fm1.append(sum(is_false(r, m["atoms"], worth(m["atoms"], m["agents_worth"])) for m in held))
                    if "pair" in r["planted"]:
                        rec1.append(any(jac(m["atoms"], r["planted"]["pair"]) >= 0.5 for m in held))
                    # agent + own artifact held in >= 1 direction, share of agents with an own artifact
                    own = r["own"]
                    ok = [any(int(a) in m["atoms"] and set(m["atoms"]) & set(v) and m["agents_worth"] == 1
                              for m in held) for a, v in own.items()]
                    p2a.append(float(np.mean(ok)) if ok else float("nan"))
                d["oneway_false_multi_mean"] = round(float(np.mean(fm1)), 3)
                k = sum(x > 0 for x in fm1)
                d["oneway_worlds_with_false_multi"] = k
                d["oneway_worlds_with_false_multi_ci"] = wilson(k, n)
                d["oneway_own_link_share"] = round(float(np.nanmean(p2a)), 3)
                if rec1:
                    d["oneway_rec_pair"] = round(float(np.mean(rec1)), 3)
                    d["oneway_rec_pair_ci"] = wilson(sum(rec1), len(rec1))
            res[w] = d
        out[f.stem] = res
    (L.OUT / "synthetic" / "summary.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
