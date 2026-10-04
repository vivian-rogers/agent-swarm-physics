"""H05-MF: two-block (R-block) mean field for rooms (HH82; physics-models/01-inverse-ising, "Mean-field forward version").

Rooms are sublattices with J_ij = J_ab (i in room a, j in room b, i != j). The only inputs are block averages of
excess equal-time correlations, r_ab = < c0_ij - c0_surrogate_ij > over the pairs of a block (the cross-day surrogate
removes schedule-locked fields), and the spin variances v_i = 1 - m_i^2. No N x N couplings are inferred.

Naive mean-field inversion: C^-1 = D^-1 - J with C = D^1/2 R D^1/2, so J = D^-1/2 (I - R^-1) D^-1/2. On the block-
homogeneous R (unit diagonal, r_ab off the diagonal), I - R^-1 is block-constant; dividing by the block's mean
sqrt(v_i v_j) gives J_ab. Loop gain g = v (sum_j J_ij) for an average agent; g -> 1 is the mean-field critical point.

Usage (exploratory, non-holdout): uv run python hypotheses/H05-rooms-cut/analysis/mf_blocks.py
Reads data/processed/H05-rooms-cut/pair_day_bin1.parquet and agent_day.parquet; writes mf_blocks.json and figures/mf_blocks.pdf.

Round 1b (2026-10-04): H05_DATA=r1b [H05_MASK=trim] reads the r1b (activity_bins_fixed) pair-day table of
explore_rooms.py from data/processed/H05-rooms-cut/r1b[/trim]/ and writes mf_blocks.json there, plus
h19_gains.parquet: one row per (two-room window, spin) with the two-block loop gain, its day-bootstrap SE and
percentile CI, in the column layout H19's build_estimates.h05_rows produces (goal_no, window, method, value, se, lo,
hi, ci_kind, n_days, N), so H19 can ingest it directly. The functions block_J / pair_day_arrays / labels_from_agent_day
keep their signatures (H19 imports them read-only).
"""
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import polars as pl

warnings.simplefilter("ignore", RuntimeWarning)  # empty-slice means for pairs absent on resampled days

import os  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
DATA_VERSION = os.environ.get("H05_DATA", "r1")
MASK = os.environ.get("H05_MASK", "none")
PANEL_DIR = ROOT / "data/processed/H05-rooms-cut" / ("" if DATA_VERSION == "r1" else "r1b")
DATA = PANEL_DIR / ("" if MASK == "none" else MASK)
FIG = Path(__file__).resolve().parents[1] / "figures"
FIG_PREFIX = "" if DATA_VERSION == "r1" else ("r1b_" if MASK == "none" else f"r1b_{MASK}_")
NBOOT = 500
NPERM = 1000


# ----------------------------------------------------------------------------- core
def block_J(ai, aj, r, sv, labels):
    """ai, aj: agent indices (into labels) of each pair; r: pair excess correlation; sv: pair sqrt(v_i v_j).

    Returns dict with J_ab per block, pair-weighted J_in / J_out, block correlations, loop gain."""
    labels = np.asarray(labels)
    ok = np.isfinite(r) & np.isfinite(sv)
    ai, aj, r, sv = ai[ok], aj[ok], r[ok], sv[ok]
    blocks = np.unique(labels)
    la, lb = labels[ai], labels[aj]
    key = lambda a, b: (min(a, b), max(a, b))
    rb, svb, nb = {}, {}, {}
    for a in blocks:
        for b in blocks:
            if b < a:
                continue
            m = ((la == a) & (lb == b)) | ((la == b) & (lb == a))
            if m.any():
                rb[(a, b)] = float(r[m].mean()); svb[(a, b)] = float(sv[m].mean()); nb[(a, b)] = int(m.sum())
    n = len(labels)
    R = np.eye(n)
    for x in range(n):
        for y in range(x + 1, n):
            k = key(labels[x], labels[y])
            R[x, y] = R[y, x] = rb.get(k, 0.0)
    w = np.linalg.eigvalsh(R).min()
    if w <= 1e-6:  # keep it a correlation matrix
        R = R + (1e-6 - w) * np.eye(n)
        R = R / np.sqrt(np.outer(np.diag(R), np.diag(R)))
    K = np.eye(n) - np.linalg.inv(R)
    J = {}
    for (a, b), _ in rb.items():
        xs = np.flatnonzero(labels == a); ys = np.flatnonzero(labels == b)
        vals = [K[x, y] for x in xs for y in ys if x != y]
        J[(a, b)] = float(np.mean(vals) / svb[(a, b)]) if vals else np.nan
    win = [k for k in J if k[0] == k[1]]; wout = [k for k in J if k[0] != k[1]]
    J_in = float(np.average([J[k] for k in win], weights=[nb[k] for k in win])) if win else np.nan
    J_out = float(np.average([J[k] for k in wout], weights=[nb[k] for k in wout])) if wout else np.nan
    # loop gain of an average agent: v_bar * sum_j J_ij
    vbar = float(np.mean(sv))
    gain = []
    for x in range(n):
        s = sum(J.get(key(labels[x], labels[y]), 0.0) for y in range(n) if y != x)
        gain.append(vbar * s)
    return {"J": {f"{a}-{b}": v for (a, b), v in J.items()}, "r": {f"{a}-{b}": v for (a, b), v in rb.items()},
            "n_pairs": {f"{a}-{b}": v for (a, b), v in nb.items()}, "J_in": J_in, "J_out": J_out,
            "J_in_minus_out": J_in - J_out if np.isfinite(J_in) and np.isfinite(J_out) else np.nan,
            "loop_gain": float(np.mean(gain)), "v_bar": vbar}


def pair_day_arrays(pdf, days, labels: dict, spin, col="c0_x"):
    """Pair x day matrices of r and sqrt(v_i v_j) restricted to labeled agents."""
    agents = np.array(sorted(labels))
    t = pdf.filter((pl.col("spin") == spin) & pl.col("pt_date").is_in(days)
                   & pl.col("i").is_in(agents.tolist()) & pl.col("j").is_in(agents.tolist()))
    t = t.with_columns((4 * pl.col("act_i") * (1 - pl.col("act_i")) * 4 * pl.col("act_j") * (1 - pl.col("act_j"))).sqrt().alias("sv"))
    pairs = sorted(set(zip(t["i"].to_list(), t["j"].to_list())))
    pk = {p: k for k, p in enumerate(pairs)}
    dk = {d: k for k, d in enumerate(days)}
    Rm = np.full((len(pairs), len(days)), np.nan); Sv = np.full_like(Rm, np.nan)
    for i, j, d, r, s in t.select("i", "j", "pt_date", col, "sv").iter_rows():
        if r is None or s is None:
            continue
        Rm[pk[(i, j)], dk[d]] = r; Sv[pk[(i, j)], dk[d]] = s
    pa = np.array(pairs) if pairs else np.zeros((0, 2), int)
    ai = np.searchsorted(agents, pa[:, 0]); aj = np.searchsorted(agents, pa[:, 1])
    lab = np.array([labels[a] for a in agents])
    return ai, aj, Rm, Sv, lab


def window_mf(pdf, days, labels, spin, rng, nboot=NBOOT, nperm=NPERM, col="c0_x"):
    ai, aj, Rm, Sv, lab = pair_day_arrays(pdf, days, labels, spin, col)
    if Rm.shape[0] == 0:
        return None
    point = block_J(ai, aj, np.nanmean(Rm, 1), np.nanmean(Sv, 1), lab)
    bs = []
    for _ in range(nboot):
        c = rng.integers(len(days), size=len(days))
        q = block_J(ai, aj, np.nanmean(Rm[:, c], 1), np.nanmean(Sv[:, c], 1), lab)
        bs.append((q["J_in"], q["J_out"], q["J_in_minus_out"], q["loop_gain"]))
    bs = np.array(bs)
    out = dict(point)
    for k, name in enumerate(("J_in", "J_out", "J_in_minus_out", "loop_gain")):
        out[name + "_ci95"] = [float(np.nanpercentile(bs[:, k], 2.5)), float(np.nanpercentile(bs[:, k], 97.5))]
        out[name + "_se"] = float(np.nanstd(bs[:, k]))
    if nperm and len(np.unique(lab)) > 1:
        rbar, sbar = np.nanmean(Rm, 1), np.nanmean(Sv, 1)
        null = np.array([block_J(ai, aj, rbar, sbar, rng.permutation(lab))["J_in_minus_out"] for _ in range(nperm)])
        null = null[np.isfinite(null)]
        out["p_perm_in_gt_out"] = float((1 + np.sum(null >= point["J_in_minus_out"])) / (1 + len(null)))
    out["days"] = len(days); out["n_agents"] = int(len(lab))
    nd = len(days)
    out["loop_gain_se_dayboot"] = float(np.nanstd(bs[:, 3]) * np.sqrt(nd / max(nd - 1, 1)))  # H19's SE convention
    out["_boot"] = bs
    return out


def labels_from_agent_day(ad, days, purity=0.9, exclude=()):
    """Agent -> room if the agent has the same modal room (purity >= 0.9) on every day of the window."""
    t = ad.filter(pl.col("pt_date").is_in(days))
    g = t.group_by("agent").agg(pl.col("room_mode").unique().alias("rooms"), pl.col("purity").min().alias("pmin"),
                                pl.len().alias("n"))
    out = {}
    for a, rooms, pmin, n in g.iter_rows():
        if a in exclude or rooms is None or len(rooms) != 1 or rooms[0] is None or pmin is None or pmin < purity:
            continue
        out[int(a)] = int(rooms[0])
    return out


def strip(d):
    return {k: v for k, v in d.items() if not k.startswith("_")} if d else d


# ----------------------------------------------------------------------------- exploratory main
def main():
    rng = np.random.default_rng(20261003)
    pdf = pl.read_parquet(DATA / "pair_day_bin1.parquet")
    ad = pl.read_parquet(PANEL_DIR / "agent_day.parquet")
    goal = dict(ad.group_by("pt_date").agg(pl.col("goal_no").first()).iter_rows())
    days_all = sorted(goal)
    gd = lambda g: [d for d in days_all if goal[d] == g]
    rngd = lambda a, b, excl=(): [d for d in days_all if a <= d <= b and d not in excl]
    res = {"MF1": {}, "MF2": {}, "MF3": {}, "MF4": "not estimable: each GPT-5.6 isolated room held one agent for ~1.5 h on 07-09 "
           "(J_in undefined; J_out would rest on ~100 bins of a single interval with no cross-day surrogate)"}
    for spin in ("talk", "active"):
        # MF1: two-room windows
        res["MF1"][spin] = {}
        for g in (35, 36, 37, 38, 39, 41, 42, 44):
            ds = gd(g)
            lab = labels_from_agent_day(ad, ds)
            r = window_mf(pdf, ds, lab, spin, rng)
            res["MF1"][spin][str(g)] = strip(r)
            print("MF1", spin, g, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in strip(r).items() if k in ("J_in", "J_out", "J_in_minus_out_ci95", "p_perm_in_gt_out", "loop_gain")}, flush=True)
        # MF2: merge, sublattices = #39 partition, GPT-5 (agent 10) excluded
        lab39 = labels_from_agent_day(ad, gd(39), exclude=(10,))
        per = {}
        for g in (39, 40, 41):
            per[g] = window_mf(pdf, gd(g), lab39, spin, rng, nperm=0)
        m2 = {f"#{g}": strip(per[g]) for g in per}
        for a, b in ((39, 40), (40, 41), (39, 41)):
            d_point = (per[b]["J_out"] - per[b]["J_in"]) - (per[a]["J_out"] - per[a]["J_in"])
            d_bs = (-per[b]["_boot"][:, 2]) - (-per[a]["_boot"][:, 2])
            m2[f"delta(J_out-J_in) #{a}->#{b}"] = {"point": float(d_point), "ci95": [float(np.nanpercentile(d_bs, 2.5)), float(np.nanpercentile(d_bs, 97.5))]}
        res["MF2"][spin] = m2
        print("MF2", spin, {k: v for k, v in m2.items() if k.startswith("delta")}, flush=True)
        # MF3: #focus, sublattices {6, 29} vs #general
        periods = {"pre": rngd("2026-07-27", "2026-08-04"), "during": rngd("2026-08-06", "2026-08-21"),
                   "post": rngd("2026-08-25", "2026-09-04", excl=("2026-08-27",))}
        present = set(ad.filter(pl.col("pt_date").is_in(sum(periods.values(), [])))["agent"].unique().to_list())
        common = set.intersection(*[set(ad.filter(pl.col("pt_date").is_in(v))["agent"].unique().to_list()) for v in periods.values()])
        labf = {a: (1 if a in (6, 29) else 0) for a in present if a in common}
        per = {k: window_mf(pdf, v, labf, spin, rng, nperm=0) for k, v in periods.items()}
        m3 = {k: {kk: per[k][kk] for kk in ("J", "J_in", "J_out", "J_out_ci95", "J_in_ci95", "n_pairs", "days")} for k in per}
        for a, b in (("pre", "during"), ("during", "post")):
            jo = per[b]["J_out"] - per[a]["J_out"]
            jo_bs = per[b]["_boot"][:, 1] - per[a]["_boot"][:, 1]
            g_in = lambda p: p["J"].get("0-0", np.nan)
            m3[f"delta J_out {a}->{b}"] = {"point": float(jo), "ci95": [float(np.nanpercentile(jo_bs, 2.5)), float(np.nanpercentile(jo_bs, 97.5))]}
            m3[f"ratio J_in(general) {b}/{a}"] = float(g_in(per[b]) / g_in(per[a])) if g_in(per[a]) else None
        res["MF3"][spin] = m3
        print("MF3", spin, {k: v for k, v in m3.items() if k.startswith("delta") or k.startswith("ratio")}, flush=True)
    (DATA / "mf_blocks.json").write_text(json.dumps(res, indent=1, default=float))
    if DATA_VERSION != "r1":
        rows = []
        for spin in ("talk", "active"):
            for g, r in res["MF1"][spin].items():
                if not r:
                    continue
                lo, hi = r.get("loop_gain_ci95", [None, None])
                rows.append({"goal_no": int(g), "window": "period", "method": f"H05.g2b_{spin}", "value": float(r["loop_gain"]),
                             "se": float(r["loop_gain_se_dayboot"]), "lo": lo, "hi": hi, "ci_kind": "day_boot",
                             "n_days": int(r["days"]), "N": float(r["n_agents"]), "J_in": float(r["J_in"]),
                             "J_out": float(r["J_out"]), "data_version": DATA_VERSION, "mask": MASK})
        pl.DataFrame(rows).write_parquet(DATA / "h19_gains.parquet")
    figure(res)


def figure(res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.2))
    for ax, spin in zip(axes, ("talk", "active")):
        ks = list(res["MF1"][spin])
        x = np.arange(len(ks))
        for off, nm, col in ((-0.18, "J_in", "#2a7"), (0.18, "J_out", "#999")):
            v = [res["MF1"][spin][k][nm] for k in ks]
            ci = np.array([res["MF1"][spin][k][nm + "_ci95"] for k in ks])
            ax.errorbar(x + off, v, yerr=[np.array(v) - ci[:, 0], ci[:, 1] - np.array(v)], fmt="o", color=col, ms=4, label=nm)
        ax.axhline(0, color="k", lw=0.5)
        ax.set_xticks(x); ax.set_xticklabels([f"#{k}" for k in ks], fontsize=7)
        ax.set_title(f"H05-MF block couplings, {spin} spins (day-bootstrap 95% CI)", fontsize=8)
        ax.legend(fontsize=7)
    fig.tight_layout(); fig.savefig(FIG / f"{FIG_PREFIX}mf_blocks.pdf"); plt.close(fig)


if __name__ == "__main__":
    main()
