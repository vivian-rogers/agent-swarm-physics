"""H17 round 1b synthetic check of the soft-state tools (axis F), run before any v3 real-data statistic.

Village-like sampling: 15 agents x 5 days x 48 windows (4-h days) and 30 agents x 40 days x 96 windows (8-h days);
q = 6 observed states; Jev-like soft vectors (argmax accuracy ~0.6). Cases:
  markov   hidden = observed Markov chain with two planted sets (t2_true ~ 4 windows)
  lumped   8 hidden states, two pairs observed as one state each (non-Markov in the observed space)
  sticky   sticky-only chain (R1: no multi-state sets)
Checks: shifted ITS recovery; soft CK pass rate (practical 0.05 rule) on markov vs lumped; soft N2 false positives
(sticky) and power (markov).
Writes data/processed/H17-behavior-metastable-sets/r1b/synthetic_v3.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import v3lib as V  # noqa: E402
import h17lib as L  # noqa: E402
import numpy as np  # noqa: E402

OUT = V.ROOT / "data/processed/H17-behavior-metastable-sets/r1b"


def chain_sets(q, sets, p_stay, p_in, rng):
    """Two-set chain: within-set jumps with p_in, between-set with small rate; diagonal p_stay."""
    T = np.zeros((q, q))
    lab = np.zeros(q, int)
    for k, s in enumerate(sets):
        lab[s] = k
    for i in range(q):
        for j in range(q):
            if i == j:
                continue
            T[i, j] = p_in if lab[i] == lab[j] else p_in * 0.06
        T[i] /= T[i].sum()
        T[i] *= (1 - p_stay)
        T[i, i] = p_stay
    return T


def run_case(case, n_seg, L_seg, rng):
    q = 6
    if case == "markov":
        T = chain_sets(q, [[0, 1, 2], [3, 4, 5]], 0.55, 1.0, rng)
        E = np.arange(q)
    elif case == "lumped":
        T = chain_sets(8, [[0, 1, 2, 6], [3, 4, 5, 7]], 0.55, 1.0, rng)
        T[6] = np.roll(T[6], 0)
        # hidden 6 and 7 are fast "shadow" states observed as 0 and 3 but with their own exits (memory)
        T[6] = 0.0; T[6, 6] = 0.85; T[6, 3] = 0.15
        T[7] = 0.0; T[7, 7] = 0.85; T[7, 0] = 0.15
        T = T / T.sum(1, keepdims=True)
        E = np.array([0, 1, 2, 3, 4, 5, 0, 3])
    else:  # sticky
        s = np.array([0.6, 0.7, 0.5, 0.65, 0.55, 0.6])
        nu = np.full(q, 1 / q)
        T = np.array([[(s[i] if i == j else (1 - s[i]) * nu[j] / (1 - nu[i])) for j in range(q)] for i in range(q)])
        E = np.arange(q)
    P, seg, h = V.hmm_soft(T, E, n_seg, L_seg, (0.6, 2.0), rng)
    t2_true = float(L.its_from_T(T, 1)[0])
    nseg = int(seg.max()) + 1
    C = {t: V.seg_soft_counts(P, seg, t, nseg).sum(0) for t in range(1, 7)}
    t2_shift = float(V.its_shift(C[1], C[2], 1)[0])
    t2_soft = float(L.its_from_T(V.soft_T(C[1]), 1)[0])
    x = P.argmax(1)
    t2_arg = float(L.its_from_C(L.counts(x, seg, q, 1), 1)[0])
    S = V.soft_sets(C[1], m=2)
    est, pred = V.soft_ck(C, S["chi"], 5)
    ck = float(np.nanmax(np.abs(est - pred)[1:4]))
    n2 = []
    for _ in range(40):
        idx = V.sojourn_index(x, seg, rng)
        Pn = P[idx]
        Cn = {t: V.seg_soft_counts(Pn, seg, t, nseg).sum(0) for t in (1, 2)}
        n2.append(float(V.its_shift(Cn[1], Cn[2], 1)[0]))
    n2 = np.array(n2)
    return {"t2_true": t2_true, "t2_shift": t2_shift, "t2_soft": t2_soft, "t2_argmax": t2_arg, "ck_max": ck,
            "ck_pass": ck < 0.05, "n2_med": float(np.nanmedian(n2)), "n2_p95": float(np.nanpercentile(n2, 95)),
            "p3b": bool(t2_shift > np.nanpercentile(n2, 95) and t2_shift / np.nanmedian(n2) >= 1.25)}


def main():
    rng = np.random.default_rng(20261004)
    res = {}
    for samp, (n_seg, L_seg, reps) in {"4h_15x5": (75, 48, 30), "8h_30x40": (1200, 96, 6)}.items():
        for case in ("markov", "lumped", "sticky"):
            rows = [run_case(case, n_seg, L_seg, rng) for _ in range(reps)]
            r = {k: float(np.nanmedian([z[k] for z in rows])) for k in ("t2_true", "t2_shift", "t2_soft", "t2_argmax", "ck_max", "n2_med")}
            r["shift_ratio_median"] = float(np.nanmedian([z["t2_shift"] / z["t2_true"] for z in rows]))
            r["ck_pass_rate"] = float(np.mean([z["ck_pass"] for z in rows]))
            r["p3b_rate"] = float(np.mean([z["p3b"] for z in rows]))
            r["reps"] = reps
            res[f"{samp}/{case}"] = r
            print(samp, case, json.dumps(r), flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "synthetic_v3.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__" and "--part2" not in sys.argv:
    main()


# ---------------------------------------------------------------------------- part 2 (added after part 1, still before
# any v3 real-data statistic): small-sample bias of the shifted estimator and its correction; ITS rise as the
# Markovianity diagnostic (the soft CK had no power against lumping in part 1); q = 12.
def part2(reps=24):
    rng = np.random.default_rng(20261005)
    res = {}
    for q, nseg, Lseg in ((6, 75, 48), (12, 75, 48), (12, 300, 48), (12, 1200, 96)):
        for case in ("markov", "sticky", "lumped"):
            rows = []
            for _ in range(reps if nseg < 1000 else 4):
                if case == "markov":
                    half = q // 2
                    T = chain_sets(q, [list(range(half)), list(range(half, q))], 0.55, 1.0, rng)
                    E = np.arange(q)
                elif case == "sticky":
                    s = rng.uniform(0.5, 0.7, q)
                    nu = np.full(q, 1 / q)
                    T = np.array([[(s[i] if i == j else (1 - s[i]) * nu[j] / (1 - nu[i])) for j in range(q)] for i in range(q)])
                    E = np.arange(q)
                else:
                    half = q // 2
                    T = chain_sets(q + 2, [list(range(half)) + [q], list(range(half, q)) + [q + 1]], 0.55, 1.0, rng)
                    T[q] = 0.0; T[q, q] = 0.85; T[q, half] = 0.15
                    T[q + 1] = 0.0; T[q + 1, q + 1] = 0.85; T[q + 1, 0] = 0.15
                    T = T / T.sum(1, keepdims=True)
                    E = np.r_[np.arange(q), 0, half]
                P, seg, h = V.hmm_soft(T, E, nseg, Lseg, (0.6, 2.0), rng)
                ns = int(seg.max()) + 1
                Cs = {t: V.seg_soft_counts(P, seg, t, ns) for t in (1, 2, 3, 4)}
                C = {t: Cs[t].sum(0) for t in Cs}
                t2 = float(V.its_shift(C[1], C[2], 1)[0])
                t2_3 = float(V.its_shift(C[1], C[4], 3)[0])
                lam = float(np.abs(L.eig_sorted(V.K_shift(C[1], C[2])))[1])
                Wb = L.boot_weights(ns, 60, rng)
                lb = np.array([np.abs(L.eig_sorted(V.K_shift(np.tensordot(w, Cs[1], 1), np.tensordot(w, Cs[2], 1))))[1] for w in Wb])
                lam_bc = float(np.clip(2 * lam - np.median(lb), 1e-6, 1 - 1e-9))
                rows.append({"true": float(L.its_from_T(T, 1)[0]), "t2": t2, "t2_bc": float(-1 / np.log(lam_bc)), "rise": t2_3 / t2})
            r = {"q": q, "windows": nseg * Lseg, "case": case,
                 "ratio_raw": float(np.median([z["t2"] / z["true"] for z in rows])),
                 "ratio_bc": float(np.median([z["t2_bc"] / z["true"] for z in rows])),
                 "rise_median": float(np.median([z["rise"] for z in rows]))}
            res[f"q{q}_{nseg * Lseg}/{case}"] = r
            print(json.dumps(r), flush=True)
    (OUT / "synthetic_v3_part2.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__" and "--part2" in sys.argv:
    part2()
