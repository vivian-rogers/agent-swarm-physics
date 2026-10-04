"""H33 summary figures from results.json, synthetic.json and the pooled design (no new tests).

figures/summary_obs.pdf  (~4.3 x 2.6 in, for the one-page RevTeX summary): (a) pooled curve, (b) synthetic power.
figures/H33_summary.pdf  (one-page figure summary): (a) pooled curve, (b) per-period slopes, (c) synthetic validation,
                         (d) rivals and robustness.
Usage: uv run python hypotheses/H33-diversity-productivity/analysis/summary_figure.py
"""
from __future__ import annotations

import json

import h33lib as H  # noqa: I001
import h33common as C
import matplotlib
import numpy as np
from scipy.stats import norm

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

BLUE, RED, GREEN, PURPLE, GRAY = "#4e79a7", "#e15759", "#59a14f", "#b07aa1", "#8c8c8c"


def pooled_curve():
    ad, x, y, Z, au, day = H.load_pooled()
    D = H.Design([au, day], au, Z)
    y_dm = D.dm(y)
    sp = H.spline_fit(D, y_dm, x)
    k = len(sp["beta"])
    B = H.ns_basis(x, sp["knots"])
    X = np.column_stack([D.dm(B), D.Z])
    beta = np.linalg.lstsq(X, y_dm, rcond=None)[0]
    e = y_dm - X @ beta
    fx = B @ beta[:k]
    pr = fx - fx.mean() + e
    edges = np.quantile(x, np.linspace(0, 1, 11))
    bi = np.clip(np.digitize(x, edges[1:-1]), 0, 9)
    bins = [(x[bi == i].mean(), pr[bi == i].mean(), pr[bi == i].std() / np.sqrt((bi == i).sum())) for i in range(10)]
    Bg = H.ns_basis(sp["grid"], sp["knots"])
    dBc = Bg - B.mean(0)
    se = np.sqrt(np.einsum("ij,jk,ik->i", dBc, sp["V"], dBc))
    return sp["grid"], Bg @ beta[:k] - fx.mean(), se, np.array(bins)


def panel_curve(ax, res, cur, small=False):
    grid, f, se, bins = cur
    ax.fill_between(grid, f - 1.96 * se, f + 1.96 * se, color=BLUE, alpha=0.15, lw=0)
    ax.plot(grid, f, color=BLUE, lw=1.5, label="spline, 95% band")
    ax.errorbar(bins[:, 0], bins[:, 1], yerr=1.96 * bins[:, 2], fmt="o", ms=3, color="k", lw=0.7, capsize=0, label="decile means")
    tl = res["pooled"]["two_lines"]
    ax.axvline(tl["xc"], color=RED, ls="--", lw=0.8)
    fs = 6.5 if small else 7.5
    ax.set_xlabel("agent-day content PR10 (self-repeats removed)", fontsize=fs)
    ax.set_xlabel("agent-day PR10 (self-repeats removed)" if small else "agent-day content PR10 (self-repeats removed)", fontsize=fs)
    ax.set_ylabel("partial resid. log(1+write turns)", fontsize=fs)
    ax.tick_params(labelsize=fs - 0.5)
    ax.legend(fontsize=fs - 1, frameon=False, loc="upper left", handlelength=1.2)
    ax.text(0.30, 0.04, f"b$_1$ {tl['b1']:+.3f} (p {tl['p1']:.2f})\nb$_2$ {tl['b2']:+.3f} (p {tl['p2']:.2f})",
            transform=ax.transAxes, ha="left", va="bottom", fontsize=fs - 0.5, color=RED)


def panel_power(ax, syn, small=False):
    cs = {(c["cond"], c["shape"], c["effect_sd"]): c for c in syn["conditions"]}
    labels, p1, qd = [], [], []
    for shape, e, lab in [("null", 0.0, "null"), ("plateau", 0.4, "plat\n.4"), ("plateau", 0.8, "plat\n.8"),
                          ("invU_mid", 0.2, "inv-U\n.2"), ("invU_mid", 0.4, "inv-U\n.4"), ("invU_mid", 0.8, "inv-U\n.8")]:
        c = cs[("eiv", shape, e)]
        labels.append(lab); p1.append(c["P1"]); qd.append(c["quad_U"])
    xs = np.arange(len(labels))
    ax.bar(xs - 0.18, qd, 0.36, color=PURPLE, label="quadratic test")
    ax.bar(xs + 0.18, p1, 0.36, color=BLUE, label="two-lines rule (P1)")
    ax.axhline(0.05, color=GRAY, lw=0.7, ls="--")
    fs = 6.5 if small else 7.5
    ax.set_xticks(xs)
    ax.set_xticklabels(labels, fontsize=fs - 1)
    ax.set_ylabel("rate of 'inverted U' verdict", fontsize=fs)
    ax.set_ylim(0, 1.05)
    ax.tick_params(labelsize=fs - 0.5)
    ax.legend(fontsize=fs - 1, frameon=False, loc="upper left", handlelength=1)


def main():
    res = json.loads((C.OUT / "results.json").read_text())
    syn = json.loads((C.OUT / "synthetic.json").read_text())
    cur = pooled_curve()

    fig, axes = plt.subplots(1, 2, figsize=(4.3, 2.6), gridspec_kw={"width_ratios": [1.1, 1]})
    panel_curve(axes[0], res, cur, small=True)
    axes[0].set_title("(a) real: 1592 agent-days, 17 periods", fontsize=7)
    panel_power(axes[1], syn, small=True)
    axes[1].set_title(f"(b) synthetic, reliability {syn['rel_within']:.2f}", fontsize=7)
    axes[1].set_xlabel("planted shape, effect (resid. SD)", fontsize=6.5)
    fig.tight_layout(pad=0.3, w_pad=0.6)
    fig.savefig(C.FIG / "summary_obs.pdf")
    plt.close(fig)

    fig, axes = plt.subplots(2, 2, figsize=(7.5, 6.6))
    panel_curve(axes[0, 0], res, cur)
    axes[0, 0].set_title("(a) pooled within agent x period and day: flat above PR10 ≈ 14", fontsize=8)
    ax = axes[0, 1]
    per = [p for p in res["per_period"] if p["b1"] is not None]
    yy = np.arange(len(per))[::-1]
    for j, p in zip(yy, per):
        ax.errorbar(p["b1"], j + 0.15, xerr=1.96 * p["se1"], fmt="o", ms=3, color=GREEN, lw=0.7)
        ax.errorbar(p["b2"], j - 0.15, xerr=1.96 * p["se2"], fmt="s", ms=3, color=RED, lw=0.7)
    m1, m2 = res["meta"]["b1"], res["meta"]["b2"]
    ax.errorbar(m1["est"], -1.2, xerr=1.96 * m1["se"], fmt="D", ms=4, color=GREEN, lw=1.3, label="b$_1$ (below x$_c$)")
    ax.errorbar(m2["est"], -1.6, xerr=1.96 * m2["se"], fmt="D", ms=4, color=RED, lw=1.3, label="b$_2$ (above x$_c$)")
    ax.axvline(0, color=GRAY, lw=0.7)
    ax.set_yticks(list(yy) + [-1.4])
    ax.set_yticklabels([f"#{p['unit']} ({p['verdict']})" for p in per] + ["RE meta"], fontsize=6.5)
    ax.set_xlim(-0.7, 0.7)
    ax.set_xlabel("slope per PR unit (95% CI, clipped)", fontsize=7.5)
    ax.tick_params(labelsize=7)
    ax.legend(fontsize=6.5, frameon=False, loc="lower right")
    v = res["meta"]["verdicts"]
    ax.set_title(f"(b) per period: {v['supported']} supported, {v['mixed']} mixed, {v['failed']} failed, {v['n/a']} n/a", fontsize=8)
    panel_power(axes[1, 0], syn)
    axes[1, 0].set_title("(c) synthetic validation at the real design (eiv)", fontsize=8)
    axes[1, 0].set_xlabel("planted shape and effect (residual SD)", fontsize=7.5)
    ax = axes[1, 1]
    rows = [("primary (writes, PR10)", res["pooled"]["two_lines"])]
    for k, lab in [("y=commits", "commits"), ("y=deploys", "deploys"), ("y=artifacts_adv", "artifacts advanced"),
                   ("y=writes_clean", "clean writes"), ("x=tv10", "x = TV10"), ("x=pr6", "x = PR6"), ("x=pr15", "x = PR15"),
                   ("without_51", "without #51"), ("regime_I", "regime I"), ("regime_III", "regime III")]:
        r = res["robustness"][k]
        rows.append((lab, r))
    nc = res["no_controls"]["two_lines"]
    rows.insert(1, ("no activity controls", nc))
    yy = np.arange(len(rows))[::-1]
    for j, (lab, r) in zip(yy, rows):
        z1 = np.sign(r["b1"]) * norm.isf(r["p1"] / 2)  # signed z recovered from the two-sided p
        z2 = np.sign(r["b2"]) * norm.isf(r["p2"] / 2)
        ax.scatter(z1, j + 0.12, color=GREEN, marker="o", s=14)
        ax.scatter(z2, j - 0.12, color=RED, marker="s", s=14)
    ax.axvline(0, color=GRAY, lw=0.7)
    for s in (-1.96, 1.96):
        ax.axvline(s, color=GRAY, lw=0.6, ls="--")
    ax.set_yticks(yy)
    ax.set_yticklabels([lab for lab, _ in rows], fontsize=6.5)
    ax.set_xlabel("z of b$_1$ (green) and b$_2$ (red); inverted U needs z$_1$>1.96, z$_2$<-1.96", fontsize=7)
    ax.tick_params(labelsize=7)
    hd, cv = res["half_day"], res["cv"]
    ax.set_title("(d) robustness, 11 specs (~1 at p<0.05 by chance)", fontsize=8)
    fig.text(0.5, 0.012, f"Day-blocked CV MSE: FE+controls {cv['fe_controls']:.4f}, +linear {cv['linear']:.4f}, +quadratic {cv['quadratic']:.4f}, "
            f"+spline {cv['spline']:.4f}.\nHalf-day cross-lag: PR→writes std {hd['fwd']['std_b']:+.3f} (p {hd['fwd']['p']:.2f}), "
            f"writes→PR std {hd['rev']['std_b']:+.3f} (p {hd['rev']['p']:.2f}).", fontsize=6.5, ha="center", va="bottom")
    fig.suptitle("H33: no inverted U between agent-day content diversity and write output (round 1, non-holdout)", fontsize=9.5)
    fig.tight_layout(rect=(0, 0.045, 1, 0.97))
    fig.savefig(C.FIG / "H33_summary.pdf")
    plt.close(fig)
    print("written summary_obs.pdf, H33_summary.pdf")


if __name__ == "__main__":
    main()
