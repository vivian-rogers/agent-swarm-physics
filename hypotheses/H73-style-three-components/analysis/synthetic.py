"""H73 synthetic validation (axis F) at village sampling, before any real-data decomposition or attribution statistic.

The real eligible-message schedule of a period (agent, day, hours, context bin, z, register) is kept. Style vectors are
replaced by planted components plus message noise resampled from the agent's own real messages after removing its
period mean (permuted within agent: day, context and register structure destroyed).
  S0 null:        x = g_d + q_i + eta_{i,d} + eps
  S1 drift:       S0 + c(bin) + b_i z            (amplitude a_c, in units of the noise SD per feature)
  S2 excitation:  S0 + zeta_seg * (pos/40)       (random direction per context segment; no mean profile)
  S3 F3 sweep:    S1 with eta variance swept, to compare estimated F3 with the planted share
NE41: S0 / S1 / S2 on the regime-III pair schedule (beta should be ~0 / ~1 / ~0).
Outputs: data/processed/H73-style-three-components/synthetic/synthetic.json
Usage: uv run python hypotheses/H73-style-three-components/analysis/synthetic.py [--reps 30]
"""
from __future__ import annotations
import argparse
import json
import time

import numpy as np
import polars as pl

import h73lib as L

PERIODS = [12, 18, 38, 41, 51]
NOISE_SD = 1.0


def schedule(goal: int):
    m = L.load_messages().filter(pl.col("goal_no") == goal)
    a = L.arrays(m)
    # real noise pool: agent-demeaned real vectors, standardized to unit per-feature SD
    X = a["X"].copy()
    for g in np.unique(a["agent"]):
        ix = a["agent"] == g
        X[ix] -= X[ix].mean(0)
    X /= X.std(0) + 1e-9
    a["noise_pool"] = X
    return m, a


def segments(a: dict) -> np.ndarray:
    """Context segment id: a new segment when the fill drops for the agent within a day (or chat mode)."""
    seg = np.zeros(len(a["agent"]), np.int64)
    s = 0
    prev = (None, None, np.inf)
    order = np.lexsort((a["t"], a["agent"]))
    for j in order:
        key = (a["agent"][j], a["day"][j])
        if key != prev[:2] or a["pos"][j] < prev[2] or not a["cu"][j]:
            s += 1
        seg[j] = s
        prev = (key[0], key[1], a["pos"][j])
    return seg


def simulate(a: dict, rng, scen: str, amp_c: float = 0.15, sd_q: float = 0.4, sd_eta: float = 0.2,
             sd_g: float = 0.15, amp_x: float = 0.6, seg=None) -> np.ndarray:
    n, d = a["X"].shape
    ag, day = a["agent"], a["day"]
    ua, inva = np.unique(ag, return_inverse=True)
    ud, invd = np.unique(day, return_inverse=True)
    q = rng.normal(0, sd_q, (len(ua), d))
    g = rng.normal(0, sd_g, (len(ud), d))
    adk, invad = np.unique(inva * 10000 + invd, return_inverse=True)
    eta = rng.normal(0, sd_eta, (len(adk), d))
    eps = np.empty((n, d))
    for k in range(len(ua)):
        ix = np.where(inva == k)[0]
        eps[ix] = a["noise_pool"][rng.permutation(ix)]
    x = g[invd] + q[inva] + eta[invad] + NOISE_SD * eps
    ctx = np.zeros((n, d))
    if scen in ("S1", "S3"):
        prof = rng.normal(0, amp_c, (len(L.BIN_NAMES), d))
        b = rng.normal(0, amp_c, (len(ua), d))
        ctx = prof[a["bin"]] + b[inva] * a["z"][:, None]
        x += ctx
    if scen == "S3":   # true F3: systematic parts residualized on the G block, as the estimator sees them
        G = np.column_stack([np.ones(n), L.block_G(a)])
        def rv(V):
            Bv, *_ = np.linalg.lstsq(G, V, rcond=None)
            return float(((V - G @ Bv) ** 2).sum())
        s3 = q[inva] + ctx
        return x, rv(s3) / rv(s3 + eta[invad])
    if scen == "S2":
        us, invs = np.unique(seg, return_inverse=True)
        zeta = rng.normal(0, amp_x, (len(us), d))
        x += zeta[invs] * np.minimum(a["pos"], 60)[:, None] / 40.0 * a["cu"][:, None]
    return x


def run(reps: int, seed: int = 7, only: str = "all"):
    rng = np.random.default_rng(seed)
    out = {"params": {"amp_c": 0.15, "sd_q": 0.4, "sd_eta": 0.2, "sd_g": 0.15, "amp_x": 0.6, "noise_sd": NOISE_SD,
                      "periods": PERIODS, "reps": reps}}
    for goal in PERIODS:
        t0 = time.time()
        m, a = schedule(goal)
        seg = segments(a)
        res = {"n": int(len(a["agent"])), "n_cu": int(a["cu"].sum())}
        nperm = 0 if goal == 51 else 49
        rr = reps if goal != 51 else max(reps // 3, 8)
        for scen in (("S0", "S1", "S2") if only == "all" else ()):
            rows = []
            for r in range(rr):
                x = simulate(a, rng, scen, seg=seg)
                b = dict(a); b["X"] = x
                dec = L.decompose(b, n_perm=nperm, seed=r)
                att = L.attribution(b, ks=(5,))
                dis = L.dispersion_slope(b, n_boot=50)
                rows.append({"F3": dec["F3"], "u_A": dec["u_A"], "u_C": dec["u_C"], "p_C": dec.get("p_C"),
                             "gain_det": att[5]["gain_det"] if att.get(5) else np.nan,
                             "gain_agent": att[5]["gain_agent"] if att.get(5) else np.nan,
                             "acc_blind": att[5]["blind"] if att.get(5) else np.nan,
                             "disp_slope": dis.get("slope"), "disp_lo": dis.get("lo")})
            df = pl.DataFrame(rows)
            summ = {c: float(df[c].drop_nulls().mean()) for c in df.columns if df[c].dtype != pl.Null}
            if nperm:
                summ["rej_C"] = float((df["p_C"] < 0.05).mean())
            summ["gain_agent_pos_rate"] = float((df["gain_agent"] > 0).mean())
            summ["gain_agent_sd"] = float(df["gain_agent"].std())
            summ["disp_detect"] = float((df["disp_lo"] > 0).mean())
            res[scen] = summ
        # S3: F3 against the planted share (eta swept)
        sweep = []
        for sd_eta in (0.05, 0.2, 0.4):
            est = []
            tru = []
            for r in range(max(rr // 2, 4)):
                x, f3 = simulate(a, rng, "S3", sd_eta=sd_eta)
                b = dict(a); b["X"] = x
                est.append(L.decompose(b, n_perm=0)["F3"]); tru.append(f3)
            sweep.append({"sd_eta": sd_eta, "F3_est": float(np.mean(est)), "F3_sd": float(np.std(est)),
                          "F3_planted": float(np.mean(tru)), "bias": float(np.mean(np.array(est) - np.array(tru)))})
        res["S3"] = sweep
        out[f"G{goal:02d}"] = res
        print(f"G{goal:02d} done in {time.time() - t0:.0f}s:", json.dumps(res, default=float)[:900], flush=True)
    # NE41 on regime III (S0, S1, S2)
    m3 = L.load_messages().filter(pl.col("regime") == "III")
    a3 = L.arrays(m3)
    X = a3["X"].copy()
    for g in np.unique(a3["agent"]):
        ix = a3["agent"] == g
        X[ix] -= X[ix].mean(0)
    a3["noise_pool"] = X / (X.std(0) + 1e-9)
    pairs = L.ne41_pairs(m3)
    seg3 = segments(a3)
    ne = {}
    for scen in ("S0", "S1", "S2"):
        bet = []
        for r in range(max(reps // 3, 6)):
            x = simulate(a3, rng, scen, seg=seg3)
            f = L.ne41_fit(a3, pairs, n_boot=100, xs=x)
            bet.append([f["forced"]["beta"], f["forced"]["lo"] > 0, f["forced"].get("T_raw", {}).get("T", np.nan),
                        f["forced"].get("T_corr", {}).get("T", np.nan)])
        bet = np.array(bet, dtype=float)
        ne[scen] = {"beta_mean": float(bet[:, 0].mean()), "beta_sd": float(bet[:, 0].std()),
                    "beta_lo_gt0_rate": float(bet[:, 1].mean()), "T_raw": float(np.nanmean(bet[:, 2])),
                    "T_corr": float(np.nanmean(bet[:, 3]))}
    ne["pairs"] = pairs.group_by("label").len().sort("label").to_dicts()
    out["NE41"] = ne
    print("NE41", json.dumps(ne, default=float), flush=True)
    (L.DATA / "synthetic").mkdir(parents=True, exist_ok=True)
    path = L.DATA / "synthetic" / "synthetic.json"
    if only != "all" and path.exists():     # merge: keep the S0-S2 results of the full run
        old = json.loads(path.read_text())
        for g, r in out.items():
            if isinstance(r, dict) and g in old and isinstance(old[g], dict):
                old[g].update(r)
            else:
                old[g] = r
        old["amendments_rerun"] = "S3 (true F3 from planted parts) and NE41 (day cross-fitting), 2026-10-04"
        out = old
    path.write_text(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=30)
    ap.add_argument("--only", default="all", choices=["all", "s3ne41"])
    args = ap.parse_args()
    run(args.reps, only=args.only)
