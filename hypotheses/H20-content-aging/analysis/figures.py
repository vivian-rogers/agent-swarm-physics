"""H20 figures: per-period aging plots, cross-period summaries, synthetic validation, one-page summary PDF.

Palette: the dataviz reference instance (series blue / orange / aqua; one-hue blue ramp for ordered t_w bands;
neutral ink and hairline grid). Static PDFs.
Usage: uv run python hypotheses/H20-content-aging/analysis/figures.py [--periods] [--synthetic] [--summary]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h20lib as L  # noqa: E402
from h20lib import hc  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
RAMP = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281"]
INK, INK2, MUTED, GRID, AXIS, SURF = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"
FIG = hc.HDIR / "figures"

plt.rcParams.update({
    "font.size": 8, "axes.titlesize": 9, "axes.labelsize": 8, "axes.edgecolor": AXIS, "axes.labelcolor": INK2,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5,
    "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": SURF, "axes.facecolor": SURF,
    "savefig.facecolor": SURF, "lines.linewidth": 1.6, "legend.frameon": False, "text.color": INK,
    "pdf.fonttype": 42})


def load_results(kind="aniso"):
    out = {}
    for g in hc.ALL_PERIODS:
        f = hc.OUT / f"G{g:02d}/{'result.json' if kind == 'iso' else 'result_aniso.json'}"
        if f.exists():
            out[g] = json.loads(f.read_text())
    return out


def bands(T):
    """Up to 4 t_w bands of roughly equal size over 2..T-1."""
    tws = np.arange(2, T)
    k = min(4, max(1, len(tws) // 2))
    return [b for b in np.array_split(tws, k) if b.size]


def period_figure(g, r):
    z = np.load(hc.OUT / f"G{g:02d}/matrices.npz")
    C, npair, wk = z["C"], z["npair"], z["wk"]
    T = C.shape[0]
    fig, ax = plt.subplots(1, 3, figsize=(10, 3.0))
    # (a) C vs tau, one line per t_w band (ordered blue ramp)
    E = L.entries(C, npair, wk, tw_min=1)
    bs = bands(T)
    cols = RAMP[-len(bs):] if len(bs) <= len(RAMP) else RAMP
    for b, col in zip(bs, cols):
        s = np.isin(E["d1"] + 1, b)
        lags = np.unique(E["lag"][s])
        y = [np.average(E["c"][s & (E["lag"] == l)], weights=E["w"][s & (E["lag"] == l)]) for l in lags]
        ax[0].plot(lags, y, "-o", ms=3, color=col, label=f"t_w {b[0]}–{b[-1]}")
    s1 = E["d1"] == 0
    if s1.any():
        ax[0].plot(E["lag"][s1], E["c"][s1], ":", color=ORANGE, lw=1.2, label="kickoff day (t_w = 1)")
    ax[0].set_xlabel("lag τ (active days)"); ax[0].set_ylabel("C(t_w + τ, t_w)")
    ax[0].set_title(f"#{g}: C by age band", loc="left", fontsize=8)
    ax[0].legend(fontsize=6.5, loc="upper right")
    # (b) C at tau = 1, 2, 3 vs t_w
    for lag, col in zip((1, 2, 3), (BLUE, ORANGE, AQUA)):
        s = E["lag"] == lag
        ax[1].plot(E["tw"][s], E["c"][s], "-o", ms=3, lw=1.2, color=col, label=f"τ = {lag}")
    ax[1].axvline(1.5, color=AXIS, lw=0.8)
    ax[1].set_xlabel("t_w (active days since kickoff)"); ax[1].set_ylabel("C")
    st = r["raw"]["stats"]
    ax[1].set_title(f"A = {st['A']['obs']:+.3f} (p = {st['A']['p_upper']:.3f}); A_late = {st['A_late']['obs']:+.3f}",
                    loc="left", fontsize=8)
    ax[1].legend(fontsize=6.5)
    # (c) scaling collapse on the fitted Box-Cox clock
    f = r.get("fits", {})
    if f:
        q, a, lt, mu = f["M1"]["params"]
        E2 = L.entries(C, npair, wk, tw_min=2)
        ds = L.boxcox(E2["tw"] + E2["tau"], mu) - L.boxcox(E2["tw"], mu)
        sc = ax[2].scatter(ds, E2["c"], s=6, c=np.log(E2["tw"]), cmap=matplotlib.colors.ListedColormap(RAMP), alpha=0.8, lw=0)
        xs = np.linspace(0, ds.max(), 100)
        ax[2].plot(xs, q + a * np.exp(-xs / np.exp(lt)), color=ORANGE, lw=1.4, label=f"M1, μ̂ = {mu:+.2f}")
        ax[2].set_xlabel("s_μ̂(t_w + τ) − s_μ̂(t_w)"); ax[2].set_ylabel("C")
        ax[2].set_title(f"collapse, μ̂ CI [{f['mu_ci90'][0]:+.2f}, {f['mu_ci90'][1]:+.2f}]", loc="left", fontsize=8)
        ax[2].legend(fontsize=6.5)
        cb = fig.colorbar(sc, ax=ax[2], pad=0.01); cb.set_label("log t_w", color=INK2); cb.outline.set_visible(False)
    fig.tight_layout()
    d = hc.HDIR / f"G{g:02d}/figures"
    d.mkdir(parents=True, exist_ok=True)
    fig.savefig(d / f"aging_G{g:02d}.pdf")
    plt.close(fig)


def forest(ax, res, key, label, src="raw"):
    order = [g for g in hc.LONG + hc.MEDIUM + hc.SHORT if g in res]
    y = np.arange(len(order))[::-1]
    for yy, g in zip(y, order):
        st = (res[g][src]["stats"][key])
        col = BLUE if hc.role(g) == "long" else AQUA if hc.role(g) == "medium" else MUTED
        ax.plot([st["null_mean"] - 1.645 * st["null_sd"], st["null_mean"] + 1.645 * st["null_sd"]], [yy, yy], color=GRID, lw=4,
                solid_capstyle="butt")
        ax.plot(st["obs"], yy, "o", color=col, ms=4)
    ax.axvline(0, color=AXIS, lw=0.8)
    ax.set_yticks(y); ax.set_yticklabels([f"#{g}" for g in order], fontsize=6)
    ax.set_xlabel(label)
    ax.grid(axis="y", visible=False)


def cross_period(res, summ):
    fig, ax = plt.subplots(1, 3, figsize=(10, 5.2))
    forest(ax[0], res, "A", "A (agent-averaged); grey = 90% stationary-null band")
    ax[0].set_title("Aging slope by period (blue long, aqua medium, grey short)", loc="left")
    forest(ax[1], res, "A", "A_g (ĝ removed)", src="g")
    ax[1].set_title("Field-removed aging slope", loc="left")
    forest(ax[2], res, "A_c", "A_c (swarm-common removed)")
    ax[2].set_title("Individual aging slope", loc="left")
    fig.tight_layout()
    fig.savefig(FIG / "forest_A.pdf")
    plt.close(fig)
    # mu-hat with CI for long + medium; power vs observed
    fig, ax = plt.subplots(1, 2, figsize=(8, 3))
    gs = [g for g in hc.LONG + hc.MEDIUM if g in res and res[g].get("fits")]
    for i, g in enumerate(gs):
        f = res[g]["fits"]
        col = BLUE if hc.role(g) == "long" else AQUA
        ax[0].plot([f["mu_ci90"][0], f["mu_ci90"][1]], [i, i], color=col, lw=1.4)
        ax[0].plot(f["mu_hat"], i, "o", color=col, ms=4)
    ax[0].axvline(0, color=AXIS, lw=0.8)
    ax[0].set_yticks(range(len(gs))); ax[0].set_yticklabels([f"#{g}" for g in gs]); ax[0].grid(axis="y", visible=False)
    ax[0].set_xlabel("μ̂ (Box-Cox aging exponent), 90% bootstrap CI"); ax[0].set_title("Aging exponent", loc="left")
    for g in res:
        if hc.role(g) == "short":
            continue
        pw = res[g]["power"]["A|mu=0.5"]
        st = res[g]["raw"]["stats"]["A"]
        z = (st["obs"] - st["null_mean"]) / st["null_sd"] if st["null_sd"] else np.nan
        col = BLUE if hc.role(g) == "long" else AQUA
        ax[1].plot(pw, z, "o", color=col, ms=5)
        ax[1].annotate(f"#{g}", (pw, z), fontsize=6, color=INK2, xytext=(3, 2), textcoords="offset points")
    ax[1].axhline(1.645, color=ORANGE, lw=0.8, ls="--")
    ax[1].axhline(0, color=AXIS, lw=0.8)
    ax[1].set_xlabel("design power vs μ = 0.5 (fitted nuisance)"); ax[1].set_ylabel("A, z vs stationary null")
    ax[1].set_title("Observed aging vs power", loc="left")
    fig.tight_layout()
    fig.savefig(FIG / "mu_and_power.pdf")
    plt.close(fig)


def synthetic_figure():
    pw = json.loads((hc.OUT / "synthetic/power.json").read_text())
    pit = json.loads((hc.OUT / "synthetic/pitfalls.json").read_text())
    cv = json.loads((hc.OUT / "synthetic/cv.json").read_text()) if (hc.OUT / "synthetic/cv.json").exists() else {}
    pipe = json.loads((hc.OUT / "synthetic/pipeline.json").read_text()) if (hc.OUT / "synthetic/pipeline.json").exists() else {}
    fig, ax = plt.subplots(1, 3, figsize=(11, 3.6))
    scen = ["S0 stationary", "S0b stationary 2 scales", "MQ uncorrelated", "MQ correlated", "TRAP x=1.5",
            "AG mu=0.5", "AG mu=1", "TRAP x=0.5", "DRIFT to g"]
    pers = [p for p in ("4", "8", "38", "51") if p in pw]
    w = 0.8 / len(pers)
    cols = [BLUE, ORANGE, AQUA, "#4a3aa7"]
    for j, p in enumerate(pers):
        vals = [pw[p][s]["A"]["reject"] for s in scen]
        ax[0].barh(np.arange(len(scen)) + j * w, vals, height=w * 0.9, color=cols[j], label=f"#{p} sampling")
    ax[0].axvline(0.05, color=INK2, lw=0.8, ls="--")
    ax[0].set_yticks(np.arange(len(scen)) + 0.4 - w / 2); ax[0].set_yticklabels(scen, fontsize=6.5)
    ax[0].invert_yaxis(); ax[0].set_xlabel("rejection rate of the A test (α = 0.05)"); ax[0].grid(axis="y", visible=False)
    ax[0].set_title("A test: size and power (a² = 0.15)", loc="left"); ax[0].legend(fontsize=6, loc="upper right")
    # pitfalls
    labs, raw, fix = [], [], []
    for p in pers:
        labs.append(f"#{p}")
        raw.append(pit[p]["drift_to_g"]["reject_raw"]); fix.append(pit[p]["drift_to_g"]["reject_g"])
    x = np.arange(len(labs))
    ax[1].bar(x - 0.2, raw, 0.38, color=ORANGE, label="drift to ĝ: raw C")
    ax[1].bar(x + 0.2, fix, 0.38, color=BLUE, label="drift to ĝ: V-g")
    ax[1].axhline(0.05, color=INK2, lw=0.8, ls="--")
    ax[1].set_xticks(x); ax[1].set_xticklabels(labs); ax[1].set_ylabel("rejection rate")
    ax[1].set_title("Field drift without aging is removed by V-g", loc="left"); ax[1].legend(fontsize=6.5)
    # mu recovery from cv part
    if cv:
        p = "38" if "38" in cv else list(cv)[0]
        names = [s for s in ("S0 stationary", "AG mu=0.5", "AG mu=1", "TRAP x=0.5", "MQ uncorrelated", "MQ correlated") if s in cv[p]]
        m = [cv[p][s]["mu_hat"]["median"] for s in names]; sd = [cv[p][s]["mu_hat"]["sd"] for s in names]
        ax[2].errorbar(np.arange(len(names)), m, yerr=sd, fmt="o", color=BLUE, ms=4, capsize=0, lw=1.2)
        ax[2].plot([0, 1, 2], [0, 0.5, 1.0], "_", color=ORANGE, ms=14, mew=2, label="true μ")
        ax[2].set_xticks(np.arange(len(names))); ax[2].set_xticklabels(names, rotation=30, ha="right", fontsize=6.5)
        ax[2].set_ylabel("μ̂ (median ± SD)"); ax[2].set_title(f"μ recovery (#{p} sampling)", loc="left"); ax[2].legend(fontsize=6.5)
    fig.tight_layout()
    fig.savefig(FIG / "synthetic_validation.pdf")
    plt.close(fig)


def summary_obs(res, res_iso):
    """Figure for the one-page summary (about 4.3 x 2.6 in): #38 kickoff relaxation; calibration of the null."""
    fig, ax = plt.subplots(1, 2, figsize=(4.3, 2.6), gridspec_kw=dict(width_ratios=[1.15, 1]))
    z = np.load(hc.OUT / "G38/matrices.npz")
    C = z["C"]
    T = C.shape[0]
    for lag, col, lab in ((1, BLUE, "τ = 1 d"), (3, ORANGE, "τ = 3 d")):
        tw = np.arange(1, T - lag + 1)
        y = [C[k - 1, k - 1 + lag] for k in tw]
        ax[0].plot(tw, y, "-o", ms=2.5, lw=1.2, color=col, label=lab)
    ax[0].axvspan(0.5, 4.5, color=GRID, alpha=0.6, lw=0)
    ax[0].set_ylim(0.25, 1.02)
    ax[0].text(2.5, 0.965, "kickoff relaxation", ha="center", fontsize=5.2, color=INK2)
    ax[0].set_xlabel("t_w (active days since kickoff)", fontsize=6.5)
    ax[0].set_ylabel("C(t_w + τ, t_w)", fontsize=6.5)
    ax[0].set_title("#38: fast settling, then flat", loc="left", fontsize=7)
    ax[0].legend(fontsize=5.5, loc="lower right")
    ax[0].tick_params(labelsize=5.5)
    order = [g for g in hc.LONG + hc.MEDIUM if g in res]
    y = np.arange(len(order))[::-1]
    for yy, g in zip(y, order):
        for rr, filled in ((res_iso, False), (res, True)):
            st = rr[g]["raw"]["stats"]["A"]
            zz = (st["obs"] - st["null_mean"]) / st["null_sd"]
            col = BLUE if hc.role(g) == "long" else AQUA
            ax[1].plot(np.clip(zz, -6, 8), yy, "o", ms=3.5, mfc=col if filled else "none", mec=col, mew=0.9)
    ax[1].axvspan(-1.645, 1.645, color=GRID, alpha=0.6, lw=0)
    ax[1].axvline(0, color=AXIS, lw=0.6)
    ax[1].set_yticks(y); ax[1].set_yticklabels([f"#{g}" for g in order], fontsize=5.5)
    ax[1].set_xlabel("aging slope A, z vs stationary null", fontsize=6.5)
    ax[1].set_title("open: isotropic null; filled: fitted", loc="left", fontsize=6.2)
    ax[1].tick_params(labelsize=5.5)
    ax[1].grid(axis="y", visible=False)
    fig.tight_layout(pad=0.4, w_pad=0.6)
    fig.savefig(FIG / "summary_obs.pdf")
    plt.close(fig)


def summary_page(res, summ):
    """One-page summary PDF: headline text + four panels."""
    fig = plt.figure(figsize=(8.27, 11.69))
    fig.text(0.06, 0.965, "H20 · Content aging in the AI Village (exploratory round 1, non-holdout)", fontsize=12, weight="bold")
    fig.text(0.06, 0.945, summ.get("headline", ""), fontsize=8, color=INK2, wrap=True)
    lines = summ.get("summary_lines", [])
    fig.text(0.06, 0.925, "\n".join(lines), fontsize=7, va="top", color=INK, family="DejaVu Sans")
    ax1 = fig.add_axes([0.08, 0.36, 0.38, 0.40])
    forest(ax1, res, "A", "A (t_w ≥ 2); grey: 90% stationary null")
    ax1.set_title("Aging slope by period", loc="left")
    ax2 = fig.add_axes([0.58, 0.36, 0.38, 0.40])
    forest(ax2, res, "A", "A_g (ĝ removed)", src="g")
    ax2.set_title("Field removed", loc="left")
    ax3 = fig.add_axes([0.08, 0.06, 0.38, 0.24])
    g0 = summ.get("example_period", 38)
    if g0 in res:
        z = np.load(hc.OUT / f"G{g0:02d}/matrices.npz")
        E = L.entries(z["C"], z["npair"], z["wk"], tw_min=1)
        for lag, col in zip((1, 2, 3), (BLUE, ORANGE, AQUA)):
            s = E["lag"] == lag
            ax3.plot(E["tw"][s], E["c"][s], "-o", ms=2.5, lw=1.1, color=col, label=f"τ = {lag}")
        ax3.set_xlabel("t_w (active days since kickoff)"); ax3.set_ylabel("C(t_w + τ, t_w)")
        ax3.set_title(f"#{g0}: fixed-lag correlation vs age", loc="left"); ax3.legend(fontsize=6.5)
    ax4 = fig.add_axes([0.58, 0.06, 0.38, 0.24])
    pw = json.loads((hc.OUT / "synthetic/power.json").read_text())
    scen = ["S0 stationary", "MQ uncorrelated", "AG mu=0.5", "AG mu=1", "TRAP x=0.5"]
    pers = [p for p in ("4", "8", "38", "51") if p in pw]
    w = 0.8 / len(pers)
    for j, p in enumerate(pers):
        ax4.bar(np.arange(len(scen)) + j * w, [pw[p][s]["A"]["reject"] for s in scen], w * 0.9,
                color=[BLUE, ORANGE, AQUA, "#4a3aa7"][j], label=f"#{p}")
    ax4.axhline(0.05, color=INK2, lw=0.8, ls="--")
    ax4.set_xticks(np.arange(len(scen)) + 0.4 - w / 2); ax4.set_xticklabels(scen, rotation=25, ha="right", fontsize=6.5)
    ax4.set_ylabel("rejection rate (α = 0.05)"); ax4.set_title("Synthetic: size and power at village sampling", loc="left")
    ax4.legend(fontsize=6, ncol=2)
    fig.savefig(FIG / "H20_summary.pdf")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--periods", action="store_true")
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--summary", action="store_true")
    a = ap.parse_args()
    FIG.mkdir(parents=True, exist_ok=True)
    if a.synthetic:
        synthetic_figure()
    if a.periods or a.summary:
        res = load_results()
        if a.periods:
            for g, r in res.items():
                period_figure(g, r)
        if a.summary:
            summ = json.loads((hc.OUT / "summary.json").read_text())
            cross_period(res, summ)
            summary_page(res, summ)
            summary_obs(res, load_results("iso"))


if __name__ == "__main__":
    main()
