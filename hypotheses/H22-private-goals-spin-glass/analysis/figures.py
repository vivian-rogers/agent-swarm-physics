"""H22 figures: synthetic validation, per-period panels (G folders), one-page summary.

Usage: uv run python hypotheses/H22-private-goals-spin-glass/analysis/figures.py [synthetic|periods|summary|all]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

HERE = Path(__file__).resolve().parent
H = HERE.parent
ROOT = H.parents[1]
DATA = ROOT / "data/processed/H22-private-goals-spin-glass"
FIG = H / "figures"

BLUE, ORANGE, AQUA, VIOLET, RED = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"
INK, INK2, GRID, NULL = "#0b0b0b", "#52514e", "#e4e3df", "#9b9a95"
DIV = LinearSegmentedColormap.from_list("h22div", [BLUE, "#f0efec", RED])
REGIME_COL = {"para": NULL, "sk": BLUE, "sk_j0": AQUA, "ferro": ORANGE, "mattis": VIOLET, "sk_drive": RED}
plt.rcParams.update({"font.size": 7.5, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
                     "grid.color": GRID, "grid.linewidth": 0.5, "axes.titlesize": 8, "axes.titleweight": "bold",
                     "legend.frameon": False, "pdf.fonttype": 42})

UNITS51 = ["51a", "51b", "51c", "51d", "51e"]
CONTRAST = ["38a", "38b", "38c", "40", "44"]
PERIOD = {**{u: "G51" for u in UNITS51}, "38a": "G38", "38b": "G38", "38c": "G38", "40": "G40", "44": "G44"}
COUNTED = {"51b", "51c", "51d", "38a"}


def g(d, *ks, default=np.nan):
    for k in ks:
        if not isinstance(d, dict) or d.get(k) is None:
            return default
        d = d[k]
    return d


# ----------------------------------------------------------------------------- synthetic
def synthetic():
    res = json.loads((DATA / "synthetic/results.json").read_text())
    e1 = res["E1"]
    units = list(res["params"]["units"])
    regimes = ["para", "sk", "sk_j0", "ferro", "mattis", "sk_drive"]
    fig, axs = plt.subplots(2, 3, figsize=(10, 6.2))
    # (a) tau3_dc at s = 0.06 by unit and regime
    for panel, key, ax, title in ((0, "tau3_dc", axs[0, 0], "Drive-robust balance index τ₃(dc), s = 0.06"),
                                  (1, "tau3", axs[0, 1], "Raw balance index τ₃ (drive-sensitive), s = 0.06")):
        for k, rg in enumerate(regimes):
            xs, ys, lo, hi = [], [], [], []
            for ui, u in enumerate(units):
                row = [r for r in e1 if r["unit"] == u and r["regime"] == rg and (r["s"] == 0.06 or rg == "para")]
                if not row:
                    continue
                r = row[0]
                xs.append(ui + (k - 2.5) * 0.12); ys.append(r[key + "_med"]); lo.append(r[key + "_q10"]); hi.append(r[key + "_q90"])
            ys, lo, hi = map(np.array, (ys, lo, hi))
            ax.errorbar(xs, ys, yerr=[ys - lo, hi - ys], fmt="o", ms=3, lw=0.8, color=REGIME_COL[rg], label=rg)
        ax.axhline(0.25, color=INK2, lw=0.6, ls="--"); ax.axhline(0, color=GRID, lw=0.8)
        ax.set_xticks(range(len(units))); ax.set_xticklabels(units); ax.set_ylim(-1.0, 1.5)
        ax.set_title(title, loc="left"); ax.set_ylabel("median and 10–90% of replicates")
    axs[0, 0].legend(ncol=3, fontsize=6, loc="upper left")
    # (b) kappa estimate vs regime (51b)
    ax = axs[0, 2]
    for k, rg in enumerate(regimes):
        rows = [r for r in e1 if r["unit"] == "51b" and r["regime"] == rg]
        for r in rows:
            ax.errorbar(r["s"] if rg != "para" else 0.0, r["kappa_med"], yerr=[[r["kappa_med"] - r["kappa_q10"]], [r["kappa_q90"] - r["kappa_med"]]],
                        fmt="o", ms=3, color=REGIME_COL[rg], lw=0.8, label=rg if r is rows[0] else None)
    ax.axhline(1, color=INK2, lw=0.6, ls="--"); ax.set_yscale("symlog", linthresh=1)
    ax.set_xlabel("coupling RMS s"); ax.set_ylabel("estimated κ = √N·J̄/σ_J")
    ax.set_title("SK ratio κ̂ (51b sampling): drive inflates it", loc="left")
    # (c) power to detect heterogeneous couplings (p_rho < 0.05) by unit, s, regime sk
    ax = axs[1, 0]
    for rg, mk in (("sk", "o"), ("mattis", "s"), ("ferro", "^")):
        for s_, al in ((0.03, 0.4), (0.06, 0.7), (0.09, 1.0)):
            ys = [g(next((r for r in e1 if r["unit"] == u and r["regime"] == rg and r["s"] == s_), {}), "power_rho") for u in units]
            ax.plot(range(len(units)), ys, marker=mk, ms=3, lw=0.8, color=REGIME_COL[rg], alpha=al,
                    label=f"{rg} s={s_}" if rg == "sk" or s_ == 0.09 else None)
    para = [g(next((r for r in e1 if r["unit"] == u and r["regime"] == "para"), {}), "power_rho") for u in units]
    ax.plot(range(len(units)), para, marker="x", color=NULL, lw=0.8, label="para (size)")
    ax.axhline(0.05, color=INK2, lw=0.5, ls=":")
    ax.set_xticks(range(len(units))); ax.set_xticklabels(units); ax.set_ylim(-0.02, 1.02)
    ax.set_ylabel("P(ρ_split > null, p < .05)"); ax.set_title("Power: heterogeneous couplings detected", loc="left")
    ax.legend(fontsize=5.5, ncol=2)
    # (d) overlap synchrony W
    ax = axs[1, 1]
    e3 = res["E3"]
    for k, mdl in enumerate(("rf", "drift", "glass")):
        rows = [r for r in e3 if r["model"] == mdl]
        ax.bar(np.arange(len(rows)) + (k - 1) * 0.27, [r["power_W"] for r in rows], width=0.25,
               color={"rf": NULL, "drift": AQUA, "glass": BLUE}[mdl], label=mdl)
    ax.set_xticks(range(len([r for r in e3 if r["model"] == "rf"])))
    ax.set_xticklabels([r["unit"] for r in e3 if r["model"] == "rf"])
    ax.axhline(0.05, color=INK2, lw=0.5, ls=":"); ax.set_ylim(0, 1.02)
    ax.set_ylabel("P(W > shift null, p < .05)"); ax.set_title("Overlap synchrony W: collective states", loc="left"); ax.legend()
    # (e) treatment test power
    ax = axs[1, 2]
    e2 = res["E2"]
    for sign, col, lab in ((-1, BLUE, "rivals repel (J_SR = −Δ)"), (1, ORANGE, "rivals attract (J_SR = +Δ)")):
        rows = sorted([r for r in e2 if r["sign"] == sign or r["delta"] == 0], key=lambda r: r["delta"])
        key = "power_less" if sign < 0 else "power_greater"
        ax.plot([r["delta"] for r in rows], [r[key] for r in rows], marker="o", ms=3, color=col, label=lab)
    nsd = np.nanmedian([r["pair_noise_sd"] for r in e2])
    ax.set_xlabel(f"Δ (coupling units; per-pair noise SD of Ĵ ≈ {nsd:.3f})"); ax.set_ylabel("power (role permutation, α = .05)")
    ax.set_title("T_SR test power (51b, 7 SR pairs)", loc="left"); ax.legend(); ax.set_ylim(0, 1.02)
    fig.suptitle("H22 synthetic validation: content vector spins at village sampling (no project data)", x=0.01, ha="left", fontsize=9, fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG / "synthetic_validation.pdf"); plt.close(fig)


# ----------------------------------------------------------------------------- per period
def load_res(u):
    p = DATA / PERIOD[u] / u / "results.json"
    return json.loads(p.read_text()) if p.exists() else None


def unit_panel(axrow, u, r):
    mats = np.load(DATA / PERIOD[u] / u / "matrices.npz")
    # coupling heatmap, ordered by role (G51) or room/lab
    ax = axrow[0]
    if "Jc" in mats:
        J = mats["Jc"]
        order = np.arange(len(J))
        lim = np.nanquantile(np.abs(J[np.triu_indices(len(J), 1)]), 0.95) if len(J) > 1 else 1
        ax.imshow(J[np.ix_(order, order)], cmap=DIV, vmin=-lim, vmax=lim)
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(f"{u}: content couplings J^c (N={len(J)})", loc="left")
        ax.grid(False)
    ax = axrow[1]
    if "Jc" in mats:
        v = mats["Jc"][np.triu_indices(len(mats["Jc"]), 1)]
        ax.hist(v, bins=30, color=BLUE if u in UNITS51 else ORANGE, alpha=0.85)
        ax.axvline(0, color=INK2, lw=0.6)
        c = g(r, "content", "moments", default={})
        f = g(r, "content", "frustration", "shuffle", default={})
        ax.set_title(f"τ₃={g(c, 'tau3'):.2f}  τ₃dc={g(c, 'tau3_dc'):.2f}  κ̂={g(c, 'kappa'):.1f}\n"
                     f"F={g(f, 'F'):.2f} (null {g(f, 'F_null_mean'):.2f})  p_neg={g(f, 'p_neg'):.2f}", loc="left", fontsize=6.5)
        ax.set_xlabel("J^c_ij")
    ax = axrow[2]
    if "q" in mats:
        q = mats["q"]
        ax.imshow(q, cmap="Blues", vmin=np.nanmin(q), vmax=np.nanmax(q)); ax.grid(False)
        o = g(r, "overlap", default={})
        ax.set_title(f"overlap q(d,d′)  W={g(o, 'W'):.2f} (p={g(o, 'p_W'):.3f})  M={g(o, 'M'):.2f}", loc="left", fontsize=6.5)
        ax.set_xlabel("day"); ax.set_ylabel("day")
    else:
        ax.axis("off")


def periods():
    groups = {"G51": UNITS51, "G38": ["38a", "38b", "38c"], "G40": ["40"], "G44": ["44"]}
    for per, us in groups.items():
        us = [u for u in us if load_res(u)]
        if not us:
            continue
        fig, axs = plt.subplots(len(us), 3, figsize=(9, 2.6 * len(us)), squeeze=False)
        for k, u in enumerate(us):
            unit_panel(axs[k], u, load_res(u))
        fig.tight_layout()
        for name in ([f"G{u}" for u in us] if per == "G51" else [per]):
            d = H / "goalperiod-subhypotheses" / name / "figures"
            d.mkdir(parents=True, exist_ok=True)
            fig.savefig(d / f"H22_{name}.pdf")
        plt.close(fig)


# ----------------------------------------------------------------------------- summary
def summary():
    units = UNITS51 + CONTRAST
    R = {u: load_res(u) for u in units}
    units = [u for u in units if R[u]]
    col = [BLUE if u in UNITS51 else ORANGE for u in units]
    fig, axs = plt.subplots(2, 3, figsize=(11, 7.2))
    x = np.arange(len(units))

    def errs(key, sub="content"):
        y = np.array([g(R[u], sub, "moments", key) for u in units], float)
        ci = [g(R[u], sub, "moments", key + "_ci90", default=[np.nan, np.nan]) for u in units]
        lo = np.array([c[0] for c in ci], float); hi = np.array([c[1] for c in ci], float)
        return y, lo, hi

    for ax, key, title, ref in ((axs[0, 0], "tau3_dc", "P3: drive-robust balance τ₃(dc) (SK ≈ 0, factions ≈ 0.5)", (0.25, 0.5)),
                                (axs[0, 1], "tau3", "Raw balance τ₃ (includes the uniform mode)", (0.25, 0.5))):
        y, lo, hi = errs(key)
        for i in range(len(units)):
            ax.errorbar(x[i], y[i], yerr=[[max(0, y[i] - lo[i]) if np.isfinite(lo[i]) else 0], [max(0, hi[i] - y[i]) if np.isfinite(hi[i]) else 0]],
                        fmt="o" if units[i] in COUNTED or units[i] in ("51b", "51c", "51d") else "o", mfc=col[i] if units[i] in COUNTED else "white",
                        mec=col[i], color=col[i], ms=4, lw=0.9)
        ax.axhline(ref[0], color=INK2, ls="--", lw=0.6); ax.axhline(0, color=GRID, lw=0.8)
        ax.axhline(ref[1], color=INK2, ls=":", lw=0.6)
        ax.set_xticks(x); ax.set_xticklabels(units, rotation=0); ax.set_title(title, loc="left")
        ax.set_ylim(-1, 1.6)
    # kappa
    ax = axs[0, 2]
    y, lo, hi = errs("kappa")
    for i in range(len(units)):
        ax.plot(x[i], y[i], "o", color=col[i], mfc=col[i] if units[i] in COUNTED else "white", ms=4)
        if np.isfinite(lo[i]) and np.isfinite(hi[i]):
            ax.plot([x[i], x[i]], [lo[i], hi[i]], color=col[i], lw=0.9)
    ax.axhline(1, color=INK2, ls="--", lw=0.6); ax.set_yscale("symlog", linthresh=1)
    ax.set_xticks(x); ax.set_xticklabels(units); ax.set_title("P2: SK ratio κ̂ = √N·J̄/σ_J (glass side < 1)", loc="left")
    # treatment
    ax = axs[1, 0]
    u51 = [u for u in UNITS51 if R.get(u)]
    for k, (cls, c) in enumerate((("SR", BLUE), ("K", VIOLET), ("SY", AQUA), ("NC", NULL))):
        T = [g(R[u], "content", "treatment", "family_adjusted", cls, "T") for u in u51]
        sd = [g(R[u], "content", "treatment", "family_adjusted", cls, "null_sd") for u in u51]
        ax.errorbar(np.arange(len(u51)) + (k - 1.5) * 0.15, T, yerr=1.96 * np.array(sd, float), fmt="o", ms=3.5, color=c, lw=0.8, label=cls)
    ax.axhline(0, color=INK2, lw=0.6)
    ax.set_xticks(range(len(u51))); ax.set_xticklabels(u51)
    ax.set_title("P4: class mean J^c − U (family-adj.; ±1.96 null SD)", loc="left"); ax.legend(ncol=4, fontsize=6)
    # triangle frustration vs sign-shuffle null
    ax = axs[1, 1]
    for i, u in enumerate(units):
        f = g(R[u], "content", "frustration", "shuffle", default={})
        ax.plot([x[i], x[i]], [g(f, "F_null_q05"), g(f, "F_null_q95")], color=NULL, lw=3, alpha=0.6, solid_capstyle="round")
        ax.plot(x[i], g(f, "F"), "o", color=col[i], mfc=col[i] if u in COUNTED else "white", ms=4)
    ax.set_xticks(x); ax.set_xticklabels(units); ax.set_ylabel("fraction of frustrated triangles")
    ax.set_title("Triangle frustration F (gray: sign-shuffle null 5–95%)", loc="left")
    # overlap synchrony
    ax = axs[1, 2]
    for i, u in enumerate(units):
        o = g(R[u], "overlap", default={})
        if isinstance(o, dict) and o:
            ax.plot(x[i], g(o, "W"), "o", color=col[i], mfc=col[i] if g(o, "counted", default=False) else "white", ms=4)
            ax.annotate(f"p={g(o, 'p_W'):.3f}", (x[i], g(o, "W")), fontsize=5.5, color=INK2, xytext=(2, 3), textcoords="offset points")
        orf = g(R[u], "overlap_room_field", default={})
        if isinstance(orf, dict) and orf:
            ax.plot(x[i] + 0.2, g(orf, "W"), "D", color=col[i], mfc="white", ms=3.5)
    ax.axhline(1, color=INK2, ls="--", lw=0.6)
    ax.set_xticks(x); ax.set_xticklabels(units); ax.set_title("P5: overlap synchrony W (1 = independent agents)", loc="left")
    fig.text(0.01, 0.004, "Blue: #51 sub-periods (private roles). Orange: shared-objective contrast weeks. Filled: counted units; open: short / low power.\n"
             "Content couplings: within-day co-movement of whitened chat embeddings minus the cross-day surrogate. P5 diamonds: post-hoc per-room day field. "
             "Exploratory, non-holdout only.", fontsize=6.5, color=INK2)
    fig.suptitle("H22 · Is #51 a spin glass? Round-1 summary", x=0.01, ha="left", fontsize=10, fontweight="bold")
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    fig.savefig(FIG / "summary.pdf"); plt.close(fig)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    FIG.mkdir(exist_ok=True)
    if what in ("synthetic", "all"):
        synthetic()
    if what in ("periods", "all"):
        periods()
    if what in ("summary", "all"):
        summary()
