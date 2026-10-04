"""H35 figures: the one-panel-pair observables figure for the summary page, and a cross-period figure.

summary_obs.pdf: (a) G51 information-work plane at gate level (value of information per nudge vs bits per nudge): the
frontier V*(R), the Donsker-Varadhan ceiling, random, the logged nudger, and gate-once policies; (b) where the nudger
spends its nudges (share by chain age) vs the response per nudge there (extra active minutes, cross-fitted).
cross_period.pdf: bits per nudge and first-nudge ATT by period.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h35lib as L  # noqa: E402

import numpy as np  # noqa: E402
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

FIG = L.HDIR / "figures"
C_LOG, C_FR, C_GO, C_RAND = "#c0392b", "#2c3e50", "#2471a3", "#7f8c8d"
KLAB = ["1", "2–3", "4–9", "≥10"]


def policy_point(cell_n, cell_g, kb_sel, r):
    """(bits per nudge, value per nudge) of a policy nudging only chain-age bin kb_sel at budget r (capped at 1)."""
    n = np.array(cell_n, float); g = np.array(cell_g, float)
    ok = n > 0
    p = n[ok] / n[ok].sum()
    gg = np.nan_to_num(g[ok])
    sel = np.zeros_like(n, bool); sel[kb_sel - 1, :] = True
    sel = sel[ok]
    c = min(1.0, r / p[sel].sum())
    pi = np.where(sel, c, 0.0)
    rr = float(np.sum(p * pi))
    I = L.policy_info(p, pi); V = L.policy_value(p, pi, gg)
    return I / L.LN2 / rr, V / rr, rr


def summary_obs(period="G51"):
    """(a) information-work plane in the minute-level trap-age space (work measured directly in extra active minutes);
    (b) where the nudger spends its nudges vs the response per nudge there, with the gate-level escape effect."""
    r = json.loads((L.OUT / period / "results.json").read_text())
    e = r["minute_k_eff"]
    p = np.array(e["p"]); g = np.array(e["g_shrunk"]); rr = e["r"]
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.75))
    a = ax[0]
    fb, fv = np.array(e["frontier_bits_per_nudge"]), np.array(e["frontier_value_per_nudge"])
    m = fb <= 6
    a.plot(fb[m], fv[m], color=C_FR, lw=1.6, label=r"frontier $V^*(R)$ (same budget)")
    bb = np.linspace(0, 6, 100)
    a.plot(bb, e["half_range_g"] * np.sqrt(2 * bb * L.LN2), color=C_FR, ls=":", lw=1, label="Donsker–Varadhan ceiling")
    a.scatter([0], [0], color=C_RAND, zorder=5, s=25, label="random nudging")
    a.scatter([e["bits_per_nudge"]], [e["dV_per_nudge"]], color=C_LOG, zorder=6, s=45, marker="D", label="logged nudger")
    for j, mk in ((2, "o"), (4, "v")):
        pi = np.zeros_like(p); pi[j] = min(1.0, rr / p[j])
        r_ = float(np.sum(p * pi))
        a.scatter([L.policy_info(p, pi) / L.LN2 / r_], [L.policy_value(p, pi, g) / r_], color=C_GO if j == 2 else "#8e44ad",
                  marker=mk, s=32, zorder=6, label=f"nudge only at k={e['labels'][j]}")
    a.axhline(0, color="k", lw=0.5)
    a.set_xlim(0, 6)
    a.set_xlabel("state information used (bits per nudge)", fontsize=7)
    a.set_ylabel("work beyond random nudging\n(extra active min per nudge)", fontsize=7)
    a.legend(fontsize=5.5, frameon=False, loc="center right", bbox_to_anchor=(1.0, 0.42))
    a.set_title(f"(a) {period}: information vs work", fontsize=8, loc="left")
    a.tick_params(labelsize=6)
    b_ = ax[1]
    x = np.arange(5)
    b_.bar(x, e["share_of_nudges"], color=C_LOG, alpha=0.35, width=0.6)
    b_.set_ylabel("share of logged nudges", color=C_LOG, fontsize=7)
    b_.set_xticks(x, e["labels"])
    b_.set_xlabel("trap age k (pause-chain length; 0 = not in a chain)", fontsize=7)
    b_.tick_params(labelsize=6)
    t = b_.twinx()
    se = np.array(e["g_se"], float)
    t.errorbar(x, e["g_raw"], yerr=1.0 * se, fmt="o", color=C_GO, ms=4, capsize=2, label="extra active min per nudge (±1 SE)")
    t.plot(x, g, "-", color=C_GO, lw=1, alpha=0.6)
    b_.set_ylim(-0.1, 0.4)
    t.set_ylim(-1.3, 5.2)            # zeros of both axes aligned (at 20% height)
    b_.axhline(0, color="k", lw=0.4)
    t.set_ylabel("extra active min per nudge", color=C_GO, fontsize=7)
    t.tick_params(labelsize=6)
    b_.set_title("(b) where nudges go vs where they work", fontsize=8, loc="left")
    fig.tight_layout()
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "summary_obs.pdf")
    plt.close(fig)


def cross_period(periods):
    rows = []
    for p in periods:
        f = L.OUT / p / "results.json"
        if not f.exists():
            continue
        r = json.loads(f.read_text())
        if "info" not in r:
            continue
        rows.append((p, r["info"]["n_nudge_epochs"], r["info"]["I_X"]["bits_per_nudge"], r["info"]["I_X"]["above_null"],
                     r["work"]["first_pastonly"]["y30"]))
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.6))
    x = np.arange(len(rows))
    ax[0].bar(x, [z[2] for z in rows], color=[C_LOG if z[3] else C_RAND for z in rows])
    ax[0].set_xticks(x, [f"{z[0]}\n({z[1]})" for z in rows], fontsize=6)
    ax[0].set_ylabel("bits per nudge (null-corrected)")
    ax[0].set_title("(a) state information used", fontsize=8, loc="left")
    att = np.array([z[4] for z in rows], dtype=float)
    ax[1].errorbar(x, att[:, 0], yerr=[att[:, 0] - att[:, 1], att[:, 2] - att[:, 0]], fmt="o", color=C_GO, ms=4)
    ax[1].axhline(0, color="k", lw=0.5)
    ax[1].set_xticks(x, [z[0] for z in rows], fontsize=6)
    ax[1].set_ylabel("first-nudge ATT, A30 (min)")
    ax[1].set_title("(b) work per nudge", fontsize=8, loc="left")
    fig.tight_layout()
    fig.savefig(FIG / "cross_period.pdf")
    plt.close(fig)


if __name__ == "__main__":
    summary_obs()
    cross_period(["G31", "G33", "G35", "G36", "G37", "G38", "G39", "G40", "G41", "G42", "G44", "G51"])
    print("figures written")
