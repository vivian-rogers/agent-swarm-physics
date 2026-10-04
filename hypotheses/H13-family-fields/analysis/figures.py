"""H13 round-1 figures: one-page summary (figures/summary_round1.pdf), per-period figures (G<NN>/figures/),
and the synthetic-validation figure (figures/synthetic_validation.pdf).

Palette: validated categorical slots 1-3 (blue #2a78d6, orange #eb6834, aqua #1baf7a; all-pairs CVD dE >= 9.2);
aqua is below 3:1 contrast, so every series also has its own marker and a legend. Diverging maps: RdBu_r.
Usage: uv run python hypotheses/H13-family-fields/analysis/figures.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h13lib as L  # noqa: E402

ROOT = HERE.parents[2]
DATA = ROOT / "data/processed/H13-family-fields"
FIG = HERE.parent / "figures"
C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"
FAMC = {"Anthropic": C1, "OpenAI": C2, "Google": C3}
plt.rcParams.update({"font.size": 7, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "axes.titlesize": 8,
                     "axes.titleweight": "bold", "legend.frameon": False, "lines.linewidth": 1.2})


def load():
    ex = json.loads((DATA / "explore.json").read_text())
    ph = json.loads((DATA / "posthoc.json").read_text()) if (DATA / "posthoc.json").exists() else {}
    sy = json.loads((DATA / "synthetic_validation.json").read_text())
    return ex, ph, sy


def grid(ax):
    ax.yaxis.grid(True, color=GRID, lw=0.5); ax.set_axisbelow(True)


def summary(ex, ph):
    U = ex["units"]; units = list(U)
    fig = plt.figure(figsize=(8.5, 11))
    gs = fig.add_gridspec(4, 2, height_ratios=[1, 1, 1, 0.95], hspace=0.55, wspace=0.28, left=0.07, right=0.97, top=0.93, bottom=0.04)
    fig.suptitle("H13 round 1: model families carry a stable, style-borne content field; couplings follow rooms, not families",
                 fontsize=9.5, fontweight="bold", color=INK)
    x = np.arange(len(units))
    # A: family field raw vs style-residualized
    ax = fig.add_subplot(gs[0, 0])
    for off, key, col, mk, lab in ((-0.15, "a1", C1, "o", "raw content field"), (0.15, "a2", C2, "s", "style-residualized (S-a)")):
        v = np.array([U[u][key]["obs"] for u in units]); se = np.array([U[u][key].get("se_jack") or 0 for u in units])
        p = np.array([U[u][key]["p"] for u in units])
        ax.errorbar(x + off, v, yerr=1.96 * se, fmt="none", ecolor=col, elinewidth=0.8, alpha=0.6)
        ax.scatter(x[p < 0.05] + off, v[p < 0.05], color=col, marker=mk, s=22, zorder=3, label=f"{lab} (filled: p < 0.05)")
        ax.scatter(x[p >= 0.05] + off, v[p >= 0.05], facecolor="white", edgecolor=col, marker=mk, s=22, zorder=3)
    ax.axhline(0, color=INK2, lw=0.6)
    ax.set_xticks(x); ax.set_xticklabels(units, rotation=60); grid(ax)
    ax.set_ylabel("T_field (within − across mean cos)")
    ax.set_title("A. Family field beyond the day field (lab-permutation p)")
    ax.legend(fontsize=6, loc="upper right")
    # B: invariance
    ax = fig.add_subplot(gs[0, 1])
    inv = ex["cross"]["a3"]; invs = ex["cross"]["a3_style"]
    fams = ["Anthropic", "OpenAI", "Google"]
    xx = np.arange(len(fams))
    ax.bar(xx - 0.18, [inv["family_cos"][f] for f in fams], 0.34, color=C1, label="raw")
    ax.bar(xx + 0.18, [invs["family_cos"][f] for f in fams], 0.34, color=C2, label="style-residualized")
    ax.axhline(inv["null_regroup_median_mean"], color=C1, lw=1, ls="--", label=f"regrouping null, raw (p = {inv['p_regroup']:.3f})")
    ax.axhline(invs["null_regroup_median_mean"], color=C2, lw=1, ls=":", label=f"regrouping null, style-res. (p = {invs['p_regroup']:.2f})")
    ax.axhline(0.5, color=INK2, lw=0.5)
    ax.set_xticks(xx); ax.set_xticklabels(fams); ax.set_ylim(0, 1.35); grid(ax)
    ax.set_ylabel("split-half cos of family field (regime III)")
    ax.set_title(f"B. Invariance across periods (agent level median {inv['agent_median']:.2f})")
    ax.legend(fontsize=5.5, loc="upper left", ncol=2)
    # C: talk K x K delta
    ax = fig.add_subplot(gs[1, 0])
    v = np.array([U[u].get("b1", {}).get("delta", np.nan) for u in units])
    ci = np.array([U[u].get("b1", {}).get("delta_ci95") or [np.nan, np.nan] for u in units], float)
    p = np.array([U[u].get("b1", {}).get("p_perm", 1) for u in units])
    one = np.array([u in ("40", "51a", "51b", "51c", "51d", "51e") for u in units])
    ax.errorbar(x, v, yerr=[v - ci[:, 0], ci[:, 1] - v], fmt="none", ecolor=INK2, elinewidth=0.7)
    ax.scatter(x[one], v[one], color=C1, marker="o", s=20, zorder=3, label="one-room unit")
    ax.scatter(x[~one], v[~one], color=C2, marker="s", s=20, zorder=3, label="two-room unit (room-confounded)")
    for k in np.flatnonzero(p < 0.05):
        ax.annotate("p<.05", (x[k], v[k]), fontsize=5.5, xytext=(3, 3), textcoords="offset points", color=INK)
    ax.axhline(0, color=INK2, lw=0.6); ax.set_ylim(-0.6, 0.65)
    ax.set_xticks(x); ax.set_xticklabels(units, rotation=60); grid(ax)
    m = ex["meta"]["delta_talk"]
    ax.set_ylabel("Δ_talk = J_in − J_out (mean-field, day-bootstrap 95% CI)")
    ax.set_title(f"C. Family coupling in talk timing: RE {m['mu']:.3f} [{m['lo']:.3f}, {m['hi']:.3f}]")
    ax.legend(fontsize=6, loc="upper left", ncol=2)
    # D: content co-movement delta
    ax = fig.add_subplot(gs[1, 1])
    v = np.array([U[u]["b2"].get("delta", np.nan) for u in units]); se = np.array([U[u]["b2"].get("delta_se_jack") or np.nan for u in units])
    p = np.array([U[u]["b2"].get("p_perm", 1) for u in units])
    ax.errorbar(x, v, yerr=1.96 * se, fmt="none", ecolor=INK2, elinewidth=0.7)
    ax.scatter(x[one], v[one], color=C1, marker="o", s=20, zorder=3, label="one-room unit")
    ax.scatter(x[~one], v[~one], color=C2, marker="s", s=20, zorder=3, label="two-room unit")
    for k in np.flatnonzero(p < 0.05):
        ax.annotate("p<.05", (x[k], v[k]), fontsize=5.5, xytext=(3, 3), textcoords="offset points", color=INK)
    ax.axhline(0, color=INK2, lw=0.6); ax.set_ylim(-0.4, 0.4)
    ax.set_xticks(x); ax.set_xticklabels(units, rotation=60); grid(ax)
    m = ex["meta"]["delta_content"]
    ax.set_ylabel("Δ_content (30-min co-movement, jackknife 95% CI)")
    ax.set_title(f"D. Family coupling in content: RE {m['mu']:.3f} [{m['lo']:.3f}, {m['hi']:.3f}]")
    ax.legend(fontsize=6, loc="upper left", ncol=2)
    if np.nanmin(v) < -0.4:
        ax.annotate(f"unit 37: Δ = {np.nanmin(v):.2f} (off scale)", (0.6, 0.03), xycoords="axes fraction", fontsize=5.5, color=INK2)
    # E: family vs room, z-scores per outcome
    ax = fig.add_subplot(gs[2, 0])
    outs = [("y1_talk", "talk\ntiming"), ("y2_field", "content\nfield"), ("y3_comove", "content\nco-movement"), ("y4_lexical", "lexical\nprofile")]
    tr = [u for u in units if "c" in U[u]]
    for k, (y, nm) in enumerate(outs):
        zl = [U[u]["c"][y]["b_lab"] / U[u]["c"][y]["null_sd_lab"] for u in tr if y in U[u]["c"]]
        zr = [U[u]["c"][y]["b_room"] / U[u]["c"][y]["null_sd_room"] for u in tr if y in U[u]["c"]]
        jit = np.linspace(-0.08, 0.08, len(zl))
        ax.scatter(k - 0.17 + jit, zl, color=C1, marker="o", s=12, label="same lab (b_lab / null sd)" if k == 0 else None)
        ax.scatter(k + 0.17 + jit, zr, color=C2, marker="s", s=12, label="same room (b_room / null sd)" if k == 0 else None)
    ax.axhline(1.64, color=INK2, lw=0.6, ls="--"); ax.axhline(0, color=INK2, lw=0.5)
    ax.set_xticks(range(len(outs))); ax.set_xticklabels([n for _, n in outs]); grid(ax)
    ax.set_ylabel("permutation z (per two-room unit)")
    ax.set_title("E. Family vs room (10 two-room units): room carries coupling")
    ax.legend(fontsize=6, loc="upper right")
    # F: post hoc style diagnostics
    ax = fig.add_subplot(gs[2, 1])
    S = ph.get("_summary", {})
    cats = ["T_field\n(of 15 units)", "y2 b_lab\n(of 10)", "y2 b_room\n(of 10)"]
    rows = [("raw", C1, "raw"), ("S-a", C2, "S-a style OLS (pre-registered)"), ("S-a_within", C3, "S-a′ within-agent style map (post hoc)")]
    for k, (key, col, lab) in enumerate(rows):
        vals = [S.get(f"T_{key}_sig", 0), S.get(f"y2_{key}_lab_sig", 0), S.get(f"y2_{key}_room_sig", 0)]
        ax.bar(np.arange(3) + (k - 1) * 0.26, vals, 0.24, color=col, label=lab, hatch="//" if k == 2 else None, edgecolor="white")
        for j, vv in enumerate(vals):
            ax.text(j + (k - 1) * 0.26, vv + 0.2, str(vv), ha="center", fontsize=5.5, color=INK)
    ax.scatter([0], [S.get("T_stylefeatures_sig", 0)], color=INK, marker="D", s=18, zorder=4, label="20 style features alone")
    ax.set_xticks(range(3)); ax.set_xticklabels(cats); grid(ax)
    ax.set_ylabel("units with p < 0.05")
    ax.set_ylim(0, 19)
    ax.set_title("F. Style rival (post hoc): S-a removes family, keeps room")
    ax.legend(fontsize=5.5, loc="upper right")
    # G: verdict table
    ax = fig.add_subplot(gs[3, :]); ax.axis("off")
    rows_t = verdict_rows(ex, ph)
    tb = ax.table(cellText=[[a, b, c] for a, b, c in rows_t], colLabels=["Prediction", "Observed", "Verdict"],
                  colWidths=[0.36, 0.5, 0.14], loc="upper center", cellLoc="left")
    tb.auto_set_font_size(False); tb.set_fontsize(6.2); tb.scale(1, 1.25)
    for (r, c), cell in tb.get_celld().items():
        cell.set_edgecolor(GRID)
        if r == 0:
            cell.set_text_props(fontweight="bold")
    fig.savefig(FIG / "summary_round1.pdf"); plt.close(fig)


def verdict_rows(ex, ph):
    U = ex["units"]; cu = [u for u in U if U[u]["counted"]]
    n = len(cu)
    s1 = sum(U[u]["a1"]["p"] < 0.05 for u in cu)
    s2 = sum(U[u]["a2"]["p"] < 0.05 for u in cu if U[u]["a1"]["p"] < 0.05)
    inv = ex["cross"]["a3"]
    a4 = ex["cross"]["a4"]; s4 = sum(v["p_proj"] < 0.05 for v in a4.values())
    oneroom = [u for u in cu if u in ("40", "51a", "51b", "51c", "51d")]
    s5 = sum(U[u]["b1"]["p_perm"] >= 0.05 for u in oneroom)
    tr = [u for u in cu if "c" in U[u]]
    bl1 = sum(U[u]["c"]["y1_talk"]["p_lab"] >= 0.05 for u in tr)
    s6 = sum(U[u]["b2"].get("p_perm", 1) < 0.05 for u in cu)
    y2l = sum(U[u]["c"]["y2_field"]["p_lab"] < 0.05 for u in tr)
    y3 = sum(U[u]["c"]["y3_comove"]["b_room"] > U[u]["c"]["y3_comove"]["b_lab"] for u in tr)
    y1 = sum(U[u]["c"]["y1_talk"]["b_room"] > U[u]["c"]["y1_talk"]["b_lab"] for u in tr)
    g = sum((U[u]["a5"].get("genuinely", {}).get("p", 1) < 0.05) for u in cu)
    d1 = sum(U[u]["d1"]["p"] < 0.05 for u in cu)
    d2 = ex["cross"]["d2"]
    m = ex["meta"]
    return [
        ("P1 family field beyond the day field", f"p<.05 in {s1}/{n} (needed 10); RE T = {m['T_field']['mu']:.3f} [{m['T_field']['lo']:.3f}, {m['T_field']['hi']:.3f}]", "mixed"),
        ("P2 field survives style residualization", f"{s2}/{s1}; RE T = {m['T_field_style']['mu']:.3f} [{m['T_field_style']['lo']:.3f}, {m['T_field_style']['hi']:.3f}]", "FALSIFIED"),
        ("P3 family field invariant; agent field not", f"family median cos {inv['family_median']:.2f} vs regroup null {inv['null_regroup_median_mean']:.2f} (p={inv['p_regroup']:.3f}); agent {inv['agent_median']:.2f}", "family ✓ / agent ✗"),
        ("P4 period-specific family part (S-b)", f"T' p<.05 in {s4}/{len(a4)} (needed ≥ 1/3)", "failed"),
        ("P5 no family homophily in talk timing", f"one-room n.s. {s5}/{len(oneroom)}; two-room b_lab n.s. {bl1}/{len(tr)}; RE Δ = {m['delta_talk']['mu']:.3f}", "supported"),
        ("P6 content co-movement not family-structured", f"Δ p<.05 in {s6}/{n}; RE Δ = {m['delta_content']['mu']:.3f} [{m['delta_content']['lo']:.3f}, {m['delta_content']['hi']:.3f}]", "supported"),
        ("P7 room dominates coupling; family persists in field", f"y1 room>lab {y1}/{len(tr)}; y3 room>lab {y3}/{len(tr)}; y2 b_lab p<.05 {y2l}/{len(tr)} (but S-a: 0/10)", "supported (y4 mixed)"),
        ("P8 lexical + unfitted classification", f"'genuinely' {g}/{n}; LOO {d1}/{n}; newcomers {d2['accuracy']:.0%} vs chance {d2['chance']:.0%} (p={d2['p_binom']:.2f})", "failed"),
    ]


def per_period(ex):
    U = ex["units"]
    ro = pl.read_parquet(ROOT / "data/processed/shared/roster.parquet", columns=["agent", "name", "lab"])
    lab_of = dict(zip(ro["agent"].to_list(), ro["lab"].to_list())); name_of = dict(zip(ro["agent"].to_list(), ro["name"].to_list()))
    Z = np.load(DATA / "agent_fields_explore.npz")
    by_g = {}
    for u, r in U.items():
        by_g.setdefault(r["gdir"], []).append(u)
    for g, units in by_g.items():
        fig, axes = plt.subplots(len(units), 3, figsize=(10, 3.3 * len(units)), squeeze=False)
        for row, u in enumerate(units):
            r = U[u]
            A = Z[f"u{u}"]
            ags = A[:, 0].astype(int); H = A[:, 1:]
            rooms = r.get("rooms", {})
            order = sorted(range(len(ags)), key=lambda k: (lab_of[ags[k]], rooms.get(str(ags[k]), -1), ags[k]))
            Hn = L.unit(H[order]); C = Hn @ Hn.T
            np.fill_diagonal(C, np.nan)
            ax = axes[row, 0]
            im = ax.imshow(C, cmap="RdBu_r", vmin=-0.8, vmax=0.8)
            lbl = [f"{name_of[ags[k]][:16]}" + (f" [r{rooms.get(str(ags[k]))}]" if rooms else "") for k in order]
            ax.set_yticks(range(len(order))); ax.set_yticklabels(lbl, fontsize=4.5)
            ax.set_xticks(range(len(order))); ax.set_xticklabels([lab_of[ags[k]][:4] for k in order], fontsize=4.5, rotation=90)
            ax.set_title(f"unit {u}: cos(H_i, H_j), lab order; T = {r['a1']['obs']:.2f} (p = {r['a1']['p']:.3f})", fontsize=6.5)
            plt.colorbar(im, ax=ax, fraction=0.04)
            for col, key, ttl in ((1, "b1", "talk spins"), (2, "b2", "content co-movement")):
                ax = axes[row, col]
                b = r.get(key, {})
                if "M" not in b:
                    ax.axis("off"); continue
                M = np.array(b["M"], float)
                K = b["K"]; names = b["families"] + ["other"]
                vmax = np.nanmax(np.abs(M)) if np.isfinite(M).any() else 1
                im = ax.imshow(M, cmap="RdBu_r", vmin=-vmax, vmax=vmax)
                ax.set_xticks(range(K + 1)); ax.set_xticklabels(names, fontsize=5, rotation=45)
                ax.set_yticks(range(K + 1)); ax.set_yticklabels(names, fontsize=5)
                for i in range(K + 1):
                    for j in range(K + 1):
                        if np.isfinite(M[i, j]):
                            ax.text(j, i, f"{M[i, j]:.2f}", ha="center", va="center", fontsize=5,
                                    color="white" if abs(M[i, j]) > 0.6 * vmax else INK)
                ax.set_title(f"{ttl}: K×K mean-field J; Δ = {b.get('delta', np.nan):.3f} (p = {b.get('p_perm', np.nan):.2f})", fontsize=6.5)
                plt.colorbar(im, ax=ax, fraction=0.04)
        fig.tight_layout()
        (HERE.parent / g / "figures").mkdir(parents=True, exist_ok=True)
        fig.savefig(HERE.parent / g / "figures" / f"H13_{g}.pdf"); plt.close(fig)


def synthetic(sy):
    fig, ax = plt.subplots(1, 4, figsize=(13, 3.2))
    for (u, v), col, mk in zip(sy["F1"].items(), (C1, C2, C3), ("o", "s", "^")):
        ph = sorted(v["phi"], key=float)
        ax[0].plot([float(p) for p in ph], [v["phi"][p]["reject_T"] for p in ph], marker=mk, color=col, label=f"unit {u} design (N={v['N']}, D={v['D']})")
    ax[0].axhline(0.05, color=INK2, lw=0.5, ls=":")
    ax[0].set_xlabel("family share φ of agent-offset variance"); ax[0].set_ylabel("P(reject) at α = 0.05")
    ax[0].set_title("F1 family-field test: size and power"); ax[0].legend(fontsize=6); grid(ax[0])
    sc = sy["F2"]["scenarios"]; ks = list(sc); xx = np.arange(len(ks))
    ax[1].bar(xx - 0.27, [sc[k]["family_splithalf_median"] for k in ks], 0.18, color=C1, label="family split-half cos")
    ax[1].bar(xx - 0.09, [sc[k]["regroup_null_median"] for k in ks], 0.18, color="#b5b3ad", label="random-regrouping null")
    ax[1].bar(xx + 0.09, [sc[k]["reject_regroup"] for k in ks], 0.18, color=C2, label="P(invariance passes)")
    ax[1].bar(xx + 0.27, [sc[k]["Sb_reject"] for k in ks], 0.18, color=C3, hatch="//", edgecolor="white", label="P(S-b finds period part)")
    ax[1].set_xticks(xx); ax[1].set_xticklabels([k.replace(" (", "\n(") for k in ks], fontsize=5.5)
    ax[1].set_title("F2 invariance and fixed-offset rival"); ax[1].legend(fontsize=5.5); grid(ax[1])
    s3 = sy["F3"]["scenarios"]; k3 = list(s3)
    ax[2].plot([s3[k]["true_delta"] for k in k3], [s3[k]["reject"] for k in k3], marker="o", color=C1, ls="none", label="P(reject)")
    ax[2].plot([s3[k]["true_delta"] for k in k3], [s3[k]["delta_hat_median"] for k in k3], marker="s", color=C2, ls="none", label="median Δ̂")
    ax[2].plot([0, 0.13], [0, 0.13], color=INK2, lw=0.5, ls=":")
    ax[2].set_xlabel("true J_in − J_out"); ax[2].set_title("F3 content K×K (N = 14, 40 windows)"); ax[2].legend(fontsize=6); grid(ax[2])
    w4 = sy["F4"]["worlds"]; k4 = list(w4); yy = np.arange(len(k4))
    ax[3].barh(yy + 0.2, [w4[k]["reject_family_delta"] for k in k4], 0.36, color=C1, label="family Δ_talk test")
    ax[3].barh(yy - 0.2, [w4[k]["reject_b_lab"] for k in k4], 0.36, color=C2, label="room-adjusted b_lab")
    ax[3].set_yticks(yy); ax[3].set_yticklabels(k4, fontsize=6); ax[3].axvline(0.05, color=INK2, lw=0.5, ls=":")
    ax[3].set_xlabel("P(reject)"); ax[3].set_title("F4 talk spins (kinetic Ising, #41 design)"); ax[3].legend(fontsize=6)
    fig.tight_layout(); fig.savefig(FIG / "synthetic_validation.pdf"); plt.close(fig)


if __name__ == "__main__":
    ex, ph, sy = load()
    summary(ex, ph)
    per_period(ex)
    synthetic(sy)
    print("figures written")
