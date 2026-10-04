"""H79 synthetic validation (S1).
(a) exactness: maxRAF and irrRAFs against brute force on small random networks (both reactant rules);
(b) size and power: planted cross-catalytic 3-cycles in a village-sized synthetic network with neutral catalysis,
    detection = S3 and rewired-null p < 0.05.

uv run python hypotheses/H79-artifact-autocatalytic-set/analysis/synthetic.py
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import raflib as RL  # noqa: E402

ROOT = HERE.parents[2]
OUTD = ROOT / "data/processed/H79-artifact-autocatalytic-set"
FIG = HERE.parent / "figures"


# ----------------------------------------------------------------------------- (a) brute force
def is_raf(S, R, food, strict):
    if not S:
        return False
    reads = {k: R[k]["reads"] for k in S}
    if strict:
        W = RL.closure(set(S), reads, food)
        return all(reads[r] <= W and r[1] in W for r in S)
    P = {x for (x, _) in S} | food
    return all(r[1] in P for r in S)


def brute(R, food, strict):
    keys = list(R)
    rafs = [frozenset(S) for k in range(1, len(keys) + 1) for S in itertools.combinations(keys, k)
            if is_raf(S, R, food, strict)]
    mx = frozenset().union(*rafs) if rafs else frozenset()
    irr = [S for S in rafs if not any(T < S for T in rafs)]
    return set(mx), irr


def s1a(n=300, seed=3):
    rng = np.random.default_rng(seed)
    bad_max = bad_irr = 0
    for it in range(n):
        n_art = int(rng.integers(4, 8))
        food = set(range(int(rng.integers(1, 3))))
        R = {}
        for _ in range(int(rng.integers(3, 10))):
            x, y = int(rng.integers(0, n_art)), int(rng.integers(0, n_art))
            reads = set(int(v) for v in rng.choice(n_art, int(rng.integers(0, 3)), replace=False)) - {x, y}
            R.setdefault((x, y), {"eids": [0], "commits": 1, "t": 0, "reads": reads})
        for strict in (False, True):
            mx, irr = brute(R, food, strict)
            got = RL.max_raf(R, food, strict=strict)
            bad_max += got != mx
            if not strict:
                multi = sorted(len(S) for S in irr if len(S) >= 2)
                cyc = RL.cycle_stats(RL.catalytic_graph(got, food))
                ours = sorted(k for k, v in cyc["by_len"].items() for _ in range(v))
                bad_irr += multi != ours
    return {"n_networks": n, "maxraf_mismatches": int(bad_max), "irr_vs_cycles_mismatches": int(bad_irr)}


# ----------------------------------------------------------------------------- (b) village-sized
def village(rng, n_events=3000, n_food=200, n_new=150, p_cat=0.35, p_self=0.5, p_food=0.4, k_plant=0):
    """Neutral catalysis: products by popularity; catalysts self / food tool / new artifact (by popularity)."""
    arts_new = list(range(n_food, n_food + n_new))
    w_new = rng.pareto(1.2, n_new) + 1
    w_new /= w_new.sum()
    w_food = rng.pareto(1.2, n_food) + 1
    w_food /= w_food.sum()
    ev = []
    for i in range(n_events):
        x = int(rng.choice(arts_new, p=w_new)) if rng.random() < 0.7 else int(rng.choice(n_food, p=w_food))
        cat = []
        if rng.random() < p_cat:
            u = rng.random()
            if u < p_self:
                cat = [x]
            elif u < p_self + p_food:
                cat = [int(rng.choice(n_food, p=w_food))]
            else:
                cat = [int(rng.choice(arts_new, p=w_new))]
        ev.append({"eid": i, "product": x, "cat": cat, "reads": [], "n_commits": 3, "t_first": float(i), "kind": "agent"})
    food = set(range(n_food))
    planted = None
    if k_plant:
        a, b, c = (n_food + n_new + j for j in range(3))      # three fresh in-period artifacts
        planted = (a, b, c)
        t = n_events
        for x, y in ((b, a), (c, b), (a, c)):                  # a catalyses b, b catalyses c, c catalyses a
            for _ in range(k_plant):
                ev.append({"eid": t, "product": x, "cat": [y], "reads": [], "n_commits": 3, "t_first": float(t),
                           "kind": "agent"})
                t += 1
    return ev, food, planted


def n3(c):
    return sum(v for k, v in c["by_len"].items() if k >= 3)


def detect(ev, food, rng, n_null=100, key="cycles_support3"):
    s = RL.summarize(ev, food)
    real = s[key]["S3"]
    n3r = n3(s[key])
    null = [n3(RL.summarize(RL.rewire(ev, rng), food)[key]) for _ in range(n_null)]
    p = (1 + sum(x >= n3r for x in null)) / (1 + n_null)
    return real, n3r, p


def s1b(reps=30, seed=11):
    rng = np.random.default_rng(seed)
    out = {}
    for k in (0, 1, 3, 5, 10):
        hits_s3 = hits_det = 0
        ps = []
        for r in range(reps):
            ev, food, _ = village(rng, k_plant=k)
            s3, _n, p = detect(ev, food, rng, n_null=40)
            hits_s3 += s3
            hits_det += (s3 and p < 0.05)
            ps.append(p)
        out[f"k{k}"] = {"S3_rate": hits_s3 / reps, "detect_rate(S3 & p<0.05)": hits_det / reps,
                        "median_p": float(np.median(ps))}
    return out


def main():
    OUTD.mkdir(parents=True, exist_ok=True)
    a = s1a()
    b = s1b()
    res = {"S1a_exactness": a, "S1b_planted_3cycles": b,
           "notes": "k = events supporting each planted edge; k0 = size (no planted cycle). Background: 3000 "
                    "events, 200 food and 150 new artifacts, 35% catalysed (50% self, 40% food tool, 10% new tool)."}
    (OUTD / "synthetic.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
