"""H80 synthetic validation (S1): the Re-Pair assembly proxy against the exact assembly index, known values on s^k,
and the classifier pipeline's size and power for an assembly-only signal.

uv run python hypotheses/H80-assembly-vs-compression/analysis/synthetic.py
Writes data/processed/H80-assembly-vs-compression/synthetic.json and figures/synthetic_validation.pdf
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h80lib as L  # noqa: E402

ROOT = HERE.parents[2]
OUTD = ROOT / "data/processed/H80-assembly-vs-compression"
FIG = HERE.parent / "figures"
CHAIN = {1: 0, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 8: 3, 9: 4, 10: 4, 11: 5, 12: 4, 13: 5, 14: 5, 15: 5, 16: 4}


def gen(rng, Lmax=12, Lmin=6):
    n = int(rng.integers(Lmin, Lmax + 1))
    kind = rng.choice(["iid", "motif", "periodic"])
    k = int(rng.choice([2, 3, 4, 6]))
    if kind == "iid":
        s = list(rng.integers(0, k, n))
    elif kind == "motif":
        m = list(rng.integers(0, k, int(rng.integers(2, 5))))
        s = []
        while len(s) < n:
            s += m if rng.random() < 0.6 else [int(rng.integers(0, k))]
        s = s[:n]
    else:
        p = int(rng.integers(1, 4))
        base = list(rng.integers(0, k, p))
        s = [base[i % p] if rng.random() > 0.1 else int(rng.integers(0, k)) for i in range(n)]
    return tuple(int(x) for x in s), kind


def s1a(n=500, seed=1):
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(n):
        s, kind = gen(rng)
        rows.append((len(s), kind, L.exact_assembly(s), L.assembly_rp(s), L.assembly_lower(s), L.lz76(s), L.lz78(s)))
    A = np.array([r[2:] for r in rows], float)
    ex, rp = A[:, 0], A[:, 1]
    d = rp - ex
    return rows, {
        "n": n, "never_below": bool((d >= 0).all()), "share_exact": float((d == 0).mean()),
        "share_within_1": float((d <= 1).mean()), "max_over": int(d.max()), "mean_over": float(d.mean()),
        "spearman_rp_exact": float(spearmanr(rp, ex)[0]), "spearman_lz78_exact": float(spearmanr(A[:, 4], ex)[0]),
        "spearman_lz76_exact": float(spearmanr(A[:, 3], ex)[0]),
        "spearman_rp_lz78": float(spearmanr(rp, A[:, 4])[0])}


def s1b():
    out = []
    for m in (1, 2, 3):
        s = tuple(range(m))
        for k in range(2, 17):
            if m * k > 16:
                break
            x = s * k
            out.append({"motif_len": m, "k": k, "known": m - 1 + CHAIN[k], "exact": L.exact_assembly(x),
                        "rp": L.assembly_rp(x)})
    ok_exact = all(r["exact"] == r["known"] for r in out)
    ok_rp = float(np.mean([r["rp"] - r["known"] <= 1 for r in out]))
    return out, {"exact_matches_known": ok_exact, "rp_within_1_of_known": ok_rp,
                 "rp_exact_share": float(np.mean([r["rp"] == r["known"] for r in out]))}


FEATS_C = ["lz76", "lz78", "h1", "h_rate", "gzip", "n_distinct"]


def s1c(reps=20, n=1200, n_groups=60, seed=7):
    """Pipeline size and power for a signal carried only by the assembly proxy (residual after C features)."""
    rng = np.random.default_rng(seed)
    pool = []
    for _ in range(n):
        s, _k = gen(rng, Lmax=16, Lmin=16)
        f = L.features(s)
        pool.append([f[c] for c in FEATS_C] + [f["a_rp"]])
    X = np.array(pool, float)
    C, a = X[:, :-1], X[:, -1]
    Cb = np.hstack([np.ones((n, 1)), (C - C.mean(0)) / np.where(C.std(0) > 0, C.std(0), 1)])
    beta, *_ = np.linalg.lstsq(Cb, a, rcond=None)
    resid = a - Cb @ beta
    r2 = 1 - resid.var() / a.var()
    groups = rng.integers(0, n_groups, n)
    out = {"r2_a_given_C": float(r2)}
    for name, drive in (("null_C_only", (C[:, 1] - C[:, 1].mean()) / C[:, 1].std()),
                        ("planted_a_resid_b1", resid / resid.std()),
                        ("planted_a_resid_b2", 2 * resid / resid.std())):
        d = []
        for r in range(reps):
            y = (rng.random(n) < 1 / (1 + np.exp(-2 * drive))).astype(int)
            pc = L.oof_scores(C, y, groups, seed=r)
            pca = L.oof_scores(X, y, groups, seed=r)
            d.append(L.auc(y, pca) - L.auc(y, pc))
        d = np.array(d)
        out[name] = {"dAUC_median": float(np.median(d)), "share_ge_0.02": float((d >= 0.02).mean()),
                     "share_ge_0.05": float((d >= 0.05).mean())}
    return out


def figure(rows, s1b_rows, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    A = np.array([r[2:] for r in rows], float)
    fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.4))
    rng = np.random.default_rng(0)
    jit = lambda v: v + rng.uniform(-0.18, 0.18, len(v))  # noqa: E731
    ax[0].scatter(jit(A[:, 0]), jit(A[:, 1]), s=5, alpha=0.4, color="#2a78d6", lw=0)
    lim = [0, A[:, :2].max() + 1]
    ax[0].plot(lim, lim, color="#85847e", lw=0.8)
    ax[0].plot(lim, [lim[0] + 1, lim[1] + 1], color="#85847e", lw=0.8, ls="--")
    ax[0].set_xlabel("exact assembly index $a$")
    ax[0].set_ylabel("Re-Pair proxy $a_{RP}$")
    ax[0].set_title("random strings, $L$ 6-12", fontsize=8)
    for m, c in ((1, "#2a78d6"), (2, "#e34948"), (3, "#0ca30c")):
        rr = [r for r in s1b_rows if r["motif_len"] == m]
        ax[1].plot([r["k"] for r in rr], [r["known"] for r in rr], "-", color=c, lw=1, label=f"$|s|$={m} known")
        ax[1].plot([r["k"] for r in rr], [r["rp"] for r in rr], "o", color=c, ms=3, mfc="none")
    ax[1].set_xlabel("repeats $k$ in $s^k$")
    ax[1].set_ylabel("$a$")
    ax[1].set_title("lines: $|s|-1+\\ell(k)$; circles: $a_{RP}$", fontsize=8)
    ax[1].legend(fontsize=6, frameon=False)
    for a_ in ax:
        a_.tick_params(labelsize=7)
        a_.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path)


def main():
    OUTD.mkdir(parents=True, exist_ok=True)
    rows, a = s1a()
    b_rows, b = s1b()
    c = s1c()
    res = {"S1a_random": a, "S1b_powers": b, "S1b_rows": b_rows, "S1c_pipeline": c}
    (OUTD / "synthetic.json").write_text(json.dumps(res, indent=1))
    figure(rows, b_rows, FIG / "synthetic_validation.pdf")
    print(json.dumps({k: v for k, v in res.items() if k != "S1b_rows"}, indent=1))


if __name__ == "__main__":
    main()
