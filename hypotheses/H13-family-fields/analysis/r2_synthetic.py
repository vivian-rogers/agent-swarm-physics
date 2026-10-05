"""H13 round 2 synthetic validation on real skeletons (card: Round 2, "Synthetic validation first").

  A  graded style ladder: real statements, features, agents, days; synthetic statement vectors
       U = style signature (real features x real within-agent W3 map) + agent offsets permuted across agents
           + real day means + real within residuals permuted across statements [+ planted structure]
     worlds S0 (style only), S1 (+ non-style family direction), S2 (+ family position = family mean style through a
     different map), NL (+ squared style terms), SG (+ speech-act signature).
  B  enculturation (r2_encult.synthetic)      C  read-out family coupling (r2_readout.synthetic)

Usage: uv run python hypotheses/H13-family-fields/analysis/r2_synthetic.py A [--reps 20]
Writes data/processed/H13-family-fields/r2/synthetic_A.json
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r2lib as R  # noqa: E402
import h13lib as L  # noqa: E402

REAL_RAW_RE = 0.080          # round-1b raw RE T (bge), the scale of "one third of the raw field"


def prep_units(lab_of):
    P = {}
    for u in R.COUNTED:
        t = R.load_stmts(u)
        U = R.vectors(t)
        blk, inv, cnt = R.blocks(t)
        sk = R.UnitSkel(t, lab_of)
        X3 = np.hstack([blk["S20g"], blk["FW50g"]])
        B, *_ = np.linalg.lstsq(R.agent_demean(X3, inv, cnt), R.agent_demean(U, inv, cnt), rcond=None)
        sig = (X3 - X3.mean(0)) @ B
        res = U - sig
        q = R.agent_demean(res, inv, cnt)
        qa = (res - q)                                      # agent-mean part per statement
        ag_mean = np.array([qa[inv == k][0] for k in range(cnt.size)])
        dd = t["pt_date"].to_numpy()
        _, dinv = np.unique(dd, return_inverse=True)
        dcnt = np.bincount(dinv).astype(float)
        dmean = q - R.agent_demean(q, dinv, dcnt)          # day means of within-agent residuals
        e = q - dmean
        labs = np.array([lab_of[a] for a in t["agent"].to_numpy()])
        P[u] = dict(t=t, blk=blk, inv=inv, cnt=cnt, sk=sk, X3=X3, sig=sig, ag_mean=ag_mean, dmean=dmean, e=e,
                    labs=labs, sig_var=float((sig ** 2).sum(1).mean()), q_rms=float(np.sqrt((ag_mean ** 2).sum(1).mean())))
    return P


def gen(p, world, rng, c=0.5):
    n = len(p["sig"])
    perm_a = rng.permutation(p["cnt"].size)
    U = p["sig"] + p["ag_mean"][perm_a][p["inv"]] + p["dmean"] + p["e"][rng.permutation(n)]
    d = U.shape[1]
    if world in ("S1", "S2"):
        labs = p["labs"]
        ul = [l for l in np.unique(labs)]
        if world == "S1":
            H = {l: rng.normal(0, 1, d) for l in ul}
            H = {l: v / np.linalg.norm(v) * c * p["q_rms"] for l, v in H.items()}
        else:
            A2 = rng.normal(0, 1, (p["X3"].shape[1], d))
            mx = {l: p["X3"][labs == l].mean(0) @ A2 for l in ul}
            norms = np.array([np.linalg.norm(v) for v in mx.values()])
            sc = c * p["q_rms"] / max(np.median(norms), 1e-12)
            H = {l: v * sc for l, v in mx.items()}
        U = U + np.array([H[l] for l in labs])
    elif world == "NL":
        S = p["blk"]["S20g"]
        Q = S ** 2 - (S ** 2).mean(0)
        A2 = rng.normal(0, 1, (Q.shape[1], d))
        Z = Q @ A2
        U = U + Z * np.sqrt(0.25 * p["sig_var"] / (Z ** 2).sum(1).mean())
    elif world == "SG":
        G = p["blk"]["G"]
        A2 = rng.normal(0, 1, (G.shape[1], d))
        Z = (G - G.mean(0)) @ A2
        U = U + Z * np.sqrt(0.25 * p["sig_var"] / (Z ** 2).sum(1).mean())
    return R.unitv(U)


def run_A(reps=20, seed=0, nperm=300):
    lab_of, _ = R.roster_labs()
    t0 = time.time()
    P = prep_units(lab_of)
    print(f"prep {time.time() - t0:.0f}s", flush=True)
    rng = np.random.default_rng(seed)
    out = {"worlds": {}, "settings": {"reps": reps, "nperm": nperm, "real_raw_re": REAL_RAW_RE}}
    plan = [("S0", None), ("NL", None), ("SG", None)] + [("S1", c) for c in (0.1, 0.15, 0.2, 0.3)] + [("S2", c) for c in (0.15, 0.3)]
    for world, c in plan:
        key = world if c is None else f"{world}_c{c}"
        rec = {lv: {"re_mu": [], "re_ci_pos": [], "frac_sig": []} for lv in R.LEVELS}
        for r in range(reps):
            pu = {}
            for u, p in P.items():
                U = gen(p, world, rng, c if c is not None else 0.5)
                pu[u] = R.ladder_unit(U, p["blk"], p["inv"], p["cnt"], p["sk"], nperm=nperm, rng=rng, jack=True)
            for lv in R.LEVELS:
                m = R.re_summary(pu, R.COUNTED, lv)
                rec[lv]["re_mu"].append(m["mu"])
                rec[lv]["re_ci_pos"].append(m["lo"] > 0)
                rec[lv]["frac_sig"].append(np.mean([pu[u][lv]["p"] < 0.05 for u in R.COUNTED]))
            print(key, r, {lv: round(rec[lv]["re_mu"][-1], 3) for lv in ("L0", "W3", "P3", "S-a", "S-a'")},
                  f"{time.time() - t0:.0f}s", flush=True)
        out["worlds"][key] = {lv: {"re_mu_mean": float(np.mean(v["re_mu"])), "re_mu_sd": float(np.std(v["re_mu"])),
                                   "rate_re_ci_pos": float(np.mean(v["re_ci_pos"])),
                                   "unit_sig_rate": float(np.mean(v["frac_sig"]))} for lv, v in rec.items()}
        R.dump(out, R.R2 / "synthetic_A.json")
    out["seconds"] = round(time.time() - t0)
    R.dump(out, R.R2 / "synthetic_A.json")
    return out


if __name__ == "__main__":
    reps = int(sys.argv[sys.argv.index("--reps") + 1]) if "--reps" in sys.argv else 20
    if "A" in sys.argv[1:]:
        run_A(reps=reps)
