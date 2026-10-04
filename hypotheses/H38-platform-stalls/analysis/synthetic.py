"""H38 synthetic validation (axis F): can stall-adjusted Curie-Weiss gains separate planted stalls from planted coupling?

Simulator (village sampling): N = 12 agents, D = 5 days x 240 one-minute bins.
  Parallel kinetic Ising: P(s_i(t+1)=+1) = sigma(2 [h_i + delta_i(b) + J_self s_i(t) + (J0/N) sum_{j!=i} (x_j(t) - 0.4)]),
    x = (s+1)/2 (coupling to the others' activity around a fixed reference, so coupling does not freeze the swarm off),
    h_i ~ N(-0.1, 0.4), delta_i(b) ~ N(0, 0.4) per (day, 30-min block), J_self = 0.8 (mean activity ~0.4).
  Background scaffold states (independent across agents): a pause process (enter 0.02/min, mean 8 min) forcing the
    agent silent with reason `pause`; staggered day starts / stops (0-8 min) with reasons pre / post.
  Partial stalls (condition `partial`): the same, but each stall hits a random half of the agents.
  Planted stalls: a common field. Stall onsets at rate chosen for stall fraction pi, geometric durations (mean 8 min,
    >= 2); during a stall every agent is forced silent except, with prob. 0.3, one random agent. A stall is *marked*
    with probability r: each forced-silent agent then carries reason `infra_err` with prob. 0.9; unmarked stalls carry
    no reason (beyond background pauses).
Estimators (h38lib): g raw / lull / stall / stall_strict / field, each vs 100 joint N1 block-shift surrogates
(spins and reasons shifted together; flags recomputed). Excess E = g - mean(g_null); z.

Grid: J0 in {0, 0.75, 1.5} x conditions: clean (no edges, no pauses, no stalls: the coupling truth), pauses only,
base (edges + pauses), and stalls (edges + pauses) with (pi, r) in {(0.05, 1), (0.05, 0.7), (0.15, 1), (0.15, 0.7)}.
Outputs: data/processed/H38-platform-stalls/synthetic/{replicates.parquet, summary.json}; figures/synthetic.png.
Usage: uv run python hypotheses/H38-platform-stalls/analysis/synthetic.py [n_rep] [n_surr]
"""
from __future__ import annotations

import json
import sys
from multiprocessing import Pool
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import h38lib as L  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

OUT = L.DATA / "synthetic"
FIG = L.HYP / "figures"
N, D, TD = 12, 5, 240
J0S = (0.0, 0.75, 1.5)
VARIANTS = ["raw", "lull", "stall", "stall_strict", "field", "mask_edge", "mask_infra", "mask_all"]


def simulate(J0, pi, r, rng, edges=True, pauses=True, frac_off=1.0):
    T = D * TD
    day = np.repeat(np.arange(D), TD)
    minute = np.tile(np.arange(TD), D)
    bid = L.h02.block_ids(day, minute)
    h = rng.normal(-0.1, 0.4, N)
    delta = rng.normal(0, 0.4, (bid.max() + 1, N))
    R = np.zeros((T, N), np.int8)
    forced = np.zeros((T, N), bool)
    # staggered starts / stops
    for d in range(D if edges else 0):
        st = rng.integers(0, 9, N); en = rng.integers(0, 9, N)
        for i in range(N):
            a = d * TD
            forced[a:a + st[i], i] = True; R[a:a + st[i], i] = L.R_PRE
            forced[a + TD - en[i]:a + TD, i] = True; R[a + TD - en[i]:a + TD, i] = L.R_POST
    # background pauses
    for i in range(N if pauses else 0):
        p = False
        for t in range(T):
            p = (rng.random() < 0.02) if not p else (rng.random() > 0.125)
            if p and R[t, i] == 0:
                forced[t, i] = True; R[t, i] = L.R_PAUSE
    # stalls
    stall = np.zeros(T, bool)
    if pi > 0:
        rate = pi / 8.0 / (1 - pi)
        t = 0
        while t < T:
            if rng.random() < rate:
                dur = max(2, rng.geometric(1 / 8.0))
                e = min(T, t + dur)
                if day[t] == day[e - 1]:
                    stall[t:e] = True
                    free = rng.integers(N) if rng.random() < 0.3 else -1
                    marked = rng.random() < r
                    hit = rng.random(N) < frac_off if frac_off < 1 else np.ones(N, bool)
                    for i in range(N):
                        if i == free or not hit[i]:
                            continue
                        forced[t:e, i] = True
                        if marked:
                            lab = rng.random(e - t) < 0.9
                            R[t:e, i] = np.where(lab, L.R_INFRA, R[t:e, i])
                t = e
            else:
                t += 1
    S = np.empty((T, N), np.int8)
    s = np.where(rng.random(N) < 0.4, 1, -1)
    for t in range(T):
        if minute[t] == 0:
            s = np.where(rng.random(N) < 0.4, 1, -1)
        else:
            x = (s > 0).astype(float)
            H = h + delta[bid[t]] + 0.8 * s + (J0 / N) * ((x.sum() - x) - 0.4 * (N - 1))
            s = np.where(rng.random(N) < 1 / (1 + np.exp(-2 * H)), 1, -1)
        s = np.where(forced[t], -1, s)
        S[t] = s
    R = np.where(S > 0, 0, R).astype(np.int8)
    return S, R, day, minute, stall


def one(args):
    J0, cond, pi, r, rep, n_surr = args
    edges, pauses = {"clean": (False, False), "pauses": (False, True)}.get(cond, (True, True))
    rng = np.random.default_rng([L.SEED, int(J0 * 100), int(pi * 100), int(r * 10), rep, len(cond)])
    S, R, day, minute, stall_true = simulate(J0, pi, r, rng, edges=edges, pauses=pauses,
                                             frac_off=0.5 if cond == "partial" else 1.0)
    sched = np.zeros(len(S), bool)
    bid, segs = L.block_segments(day, minute)
    res, f = L.gains(S, R, sched, bid)
    obs = {v: L.cw(res[v][0])["g"] for v in VARIANTS}
    null = {v: [] for v in VARIANTS}
    for _ in range(n_surr):
        Sx, Rx = L.joint_shift([S, R], segs, rng)
        rx, _ = L.gains(Sx, Rx, sched, bid)
        for v in VARIANTS:
            null[v].append(L.cw(rx[v][0])["g"])
    row = {"J0": J0, "cond": cond, "pi": pi, "r": r, "rep": rep, "js_share": float(f["js"].mean()),
           "stall_share_true": float(stall_true.mean()), "expl_share": float(f["explained"].sum() / max(f["js"].sum(), 1)),
           "recall": float((f["explained"] & stall_true).sum() / max(stall_true.sum(), 1)),
           "precision": float((f["explained"] & stall_true).sum() / max(f["explained"].sum(), 1))}
    for v in VARIANTS:
        nv = np.array(null[v])
        row[f"g_{v}"] = obs[v]
        row[f"E_{v}"] = obs[v] - nv.mean()
        row[f"z_{v}"] = (obs[v] - nv.mean()) / nv.std() if nv.std() > 0 else np.nan
    o6 = L.o6_predict(S, bid, f["explained"])
    row["g_o6_pred"] = o6["g"]
    return row


def main():
    n_rep = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    n_surr = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    OUT.mkdir(parents=True, exist_ok=True)
    conds = [("clean", 0.0, 1.0), ("pauses", 0.0, 1.0), ("base", 0.0, 1.0), ("stall", 0.05, 1.0), ("stall", 0.05, 0.7),
             ("stall", 0.15, 1.0), ("stall", 0.15, 0.7), ("partial", 0.15, 1.0)]
    jobs = [(J0, c, pi, r, k, n_surr) for J0 in J0S for (c, pi, r) in conds for k in range(n_rep)]
    with Pool(2) as p:
        rows = p.map(one, jobs, chunksize=4)
    df = pl.DataFrame(rows)
    df.write_parquet(OUT / "replicates.parquet", compression="zstd")
    agg = (df.group_by("J0", "cond", "pi", "r").agg(
        pl.len().alias("n"), pl.col("js_share").mean(), pl.col("expl_share").mean(), pl.col("recall").mean(),
        pl.col("precision").mean(),
        *[pl.col(f"g_{v}").mean() for v in VARIANTS], *[pl.col(f"E_{v}").mean() for v in VARIANTS],
        *[(pl.col(f"E_{v}").std() / pl.len().sqrt()).alias(f"seE_{v}") for v in VARIANTS],
        *[(pl.col(f"z_{v}") > 2).mean().alias(f"sig_{v}") for v in VARIANTS],
        ((pl.col("g_o6_pred") - pl.col("g_stall")) / (pl.col("g_raw") - pl.col("g_stall"))).median().alias("o6_ratio_med"))
        .sort("J0", "cond", "pi", "r"))
    truth = agg.filter(pl.col("cond") == "clean").select("J0", pl.col("E_raw").alias("E_true"))
    agg = agg.join(truth, on="J0")
    with pl.Config(tbl_rows=40, tbl_cols=60, tbl_width_chars=400, float_precision=3):
        print(agg.select("J0", "cond", "pi", "r", "js_share", "recall", "precision", "E_true",
                         *[f"E_{v}" for v in VARIANTS], *[f"sig_{v}" for v in VARIANTS], "o6_ratio_med"))
    A = {(r["J0"], r["cond"], r["pi"], r["r"]): r for r in agg.iter_rows(named=True)}
    Jc = [J for J in J0S if J > 0]
    sp = {
        "SP1_raw_sig (J0=0, pi=.05; r=1, r=.7)": [A[(0.0, "stall", 0.05, 1.0)]["sig_raw"], A[(0.0, "stall", 0.05, 0.7)]["sig_raw"]],
        "SP1_stall_sig_r1": A[(0.0, "stall", 0.05, 1.0)]["sig_stall"], "SP1_field_sig_r1": A[(0.0, "stall", 0.05, 1.0)]["sig_field"],
        "SP1_stall_sig_r07": A[(0.0, "stall", 0.05, 0.7)]["sig_stall"], "SP1_field_sig_r07": A[(0.0, "stall", 0.05, 0.7)]["sig_field"],
        "SP1_mask_infra_sig_r1": A[(0.0, "stall", 0.05, 1.0)]["sig_mask_infra"],
        "SP1_mask_infra_sig_r07": A[(0.0, "stall", 0.05, 0.7)]["sig_mask_infra"],
        "SP1_edges_only_raw_sig": A[(0.0, "base", 0.0, 1.0)]["sig_raw"],
        "SP1_edges_only_stall_sig": A[(0.0, "base", 0.0, 1.0)]["sig_stall"],
        "SP1_edges_only_mask_edge_sig": A[(0.0, "base", 0.0, 1.0)]["sig_mask_edge"],
        "SP2_stall_keep (pauses only)": {J: A[(J, "pauses", 0.0, 1.0)]["E_stall"] / A[(J, "pauses", 0.0, 1.0)]["E_raw"] for J in Jc},
        "SP2_lull_keep (pauses only)": {J: A[(J, "pauses", 0.0, 1.0)]["E_lull"] / A[(J, "pauses", 0.0, 1.0)]["E_raw"] for J in Jc},
        "SP2_mask_all_keep (pauses only)": {J: A[(J, "pauses", 0.0, 1.0)]["E_mask_all"] / A[(J, "pauses", 0.0, 1.0)]["E_raw"] for J in Jc},
        "SP3_stall_vs_truth_r1": {f"J{J}_pi{p}": A[(J, "stall", p, 1.0)]["E_stall"] / A[(J, "clean", 0.0, 1.0)]["E_raw"] for J in Jc for p in (0.05, 0.15)},
        "SP3_mask_infra_vs_truth_r1": {f"J{J}_pi{p}": A[(J, "stall", p, 1.0)]["E_mask_infra"] / A[(J, "clean", 0.0, 1.0)]["E_raw"] for J in Jc for p in (0.05, 0.15)},
        "SP3_mask_infra_vs_truth_r07": {f"J{J}_pi{p}": A[(J, "stall", p, 0.7)]["E_mask_infra"] / A[(J, "clean", 0.0, 1.0)]["E_raw"] for J in Jc for p in (0.05, 0.15)},
        "partial_stalls_J0_0": {v: A[(0.0, "partial", 0.15, 1.0)][f"E_{v}"] for v in VARIANTS},
        "partial_stalls_J0_0_sig": {v: A[(0.0, "partial", 0.15, 1.0)][f"sig_{v}"] for v in VARIANTS},
        "J0_0_pi05_r1_E": {v: A[(0.0, "stall", 0.05, 1.0)][f"E_{v}"] for v in VARIANTS},
        "J0_0_pi05_r1_sig": {v: A[(0.0, "stall", 0.05, 1.0)][f"sig_{v}"] for v in VARIANTS},
        "SP4_o6_ratio_med_r1": {f"J{J}_pi{p}": A[(J, "stall", p, 1.0)]["o6_ratio_med"] for J in J0S for p in (0.05, 0.15)},
    }
    (OUT / "summary.json").write_text(json.dumps({"grid": agg.to_dicts(), "scores": sp}, indent=1, default=float))
    print(json.dumps(sp, indent=1, default=float))
    figure(agg)


def figure(agg):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    FIG.mkdir(parents=True, exist_ok=True)
    A = {(r["J0"], r["cond"], r["pi"], r["r"]): r for r in agg.iter_rows(named=True)}
    fig, ax = plt.subplots(1, 2, figsize=(8.4, 3.3), gridspec_kw={"width_ratios": [1.6, 1]})
    cols = {"raw": "#8c8c8c", "lull": "#d08c2a", "stall": "#2a6fb0", "mask_infra": "#5aa469"}
    labs = {"raw": "raw", "lull": "lull filter (drop K≤1)", "stall": "stall filter (drop explained K≤1)",
            "mask_infra": "agent-state conditioning"}
    conds = [(0.0, "base", 0.0, 1.0), (0.0, "stall", 0.05, 1.0), (0.0, "stall", 0.15, 0.7),
             (0.75, "stall", 0.05, 1.0), (1.5, "stall", 0.05, 1.0), (1.5, "stall", 0.15, 0.7)]
    labels = ["J0=0\nedges", "J0=0\nπ=.05", "J0=0\nπ=.15\nr=.7", "J0=.75\nπ=.05", "J0=1.5\nπ=.05", "J0=1.5\nπ=.15\nr=.7"]
    w = 0.2
    for k, v in enumerate(cols):
        ax[0].bar(np.arange(len(conds)) + (k - 1.5) * w, [A[c][f"E_{v}"] for c in conds], w, color=cols[v], label=labs[v],
                  yerr=[1.96 * A[c][f"seE_{v}"] for c in conds], error_kw={"lw": 0.6})
    for i, c in enumerate(conds):
        tr = A[(c[0], "clean", 0.0, 1.0)]["E_raw"]
        ax[0].plot([i - 0.45, i + 0.45], [tr, tr], color="k", ls=":", lw=1.2)
    ax[0].set_xticks(np.arange(len(conds)), labels, fontsize=7)
    ax[0].set_ylabel("excess gain over N1 null", fontsize=8)
    ax[0].axhline(0, color="k", lw=0.5)
    ax[0].legend(fontsize=6.5, frameon=False, loc="upper left")
    ax[0].set_title("planted stalls/edges vs planted coupling (dotted = coupling truth)", fontsize=8)
    cc = [(0.0, "base", 0.0, 1.0), (0.0, "stall", 0.05, 1.0), (0.0, "stall", 0.05, 0.7)]
    for k, v in enumerate(cols):
        ax[1].bar(np.arange(3) + (k - 1.5) * w, [A[c][f"sig_{v}"] for c in cc], w, color=cols[v])
    ax[1].axhline(0.05, color="k", lw=0.5, ls="--")
    ax[1].set_xticks(np.arange(3), ["edges\nonly", "π=.05\nr=1", "π=.05\nr=.7"], fontsize=7)
    ax[1].set_ylabel("P(z > 2 vs N1) with J0 = 0", fontsize=8)
    ax[1].set_title("false 'coupling' rate", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "synthetic.png", dpi=150)


if __name__ == "__main__":
    main()
