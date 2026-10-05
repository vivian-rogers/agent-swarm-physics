"""H11 round-2 summary figures (read r2/results/score_r2.json only; recompute nothing).

figures/summary_obs_r2.pdf  page 1: (a) attachment exponent alpha per unit (work, attention) with pooled values;
                            (b) pooled exposure coefficients before (lag) and after (lead) the join, per channel
figures/r2_output.pdf       page 2: (a) crowding exponent theta per unit; (b) herd vs solo log rate ratio per unit

Usage: uv run python hypotheses/H11-potts-labor-vs-herding/analysis/summary_figure_r2.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "data/processed/H11-potts-labor-vs-herding/r2/results"
FIG = HERE.parent / "figures"
C_W, C_A = "#2a78d6", "#eb6834"          # reference categorical slots 1-2
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.size": 7, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "axes.titlesize": 7.2,
                     "axes.titleweight": "bold", "legend.frameon": False, "pdf.fonttype": 42})


def ukey(u):
    return (int(u[1:]) if u.startswith("G") else int(u[:2]), u)


def lab(u):
    return "#" + u[1:] if u.startswith("G") else u


def page1(s):
    fig, (a, b) = plt.subplots(1, 2, figsize=(4.3, 2.6), gridspec_kw={"width_ratios": [1.6, 1]})
    rows = s["R1"]["rows"]
    units = sorted({r["unit"] for r in rows.values()}, key=ukey)
    x = {u: i for i, u in enumerate(units)}
    for ch, col, dx in (("work", C_W, -0.18), ("att", C_A, 0.18)):
        for r in rows.values():
            if r["ch"] != ch:
                continue
            al = r["alpha"]
            xi = x[r["unit"]] + dx
            mk = "^" if r["group"] == "own" else "o"
            a.plot([xi, xi], [max(al["lo"], -2.5), min(al["hi"], 4)], color=col, lw=0.8, alpha=0.7)
            a.plot(xi, al["est"], mk, color=col, ms=3.2, mec="white", mew=0.4)
        p = s["R1"][f"{ch}:all"]["alpha_pool"]
        a.axhspan(p["lo"], p["hi"], color=col, alpha=0.12, lw=0)
    a.axhline(0, color=INK2, lw=0.6)
    a.axhline(1, color=INK2, lw=0.6, ls="--")
    a.text(-0.4, 1.05, "Yule (α = 1)", ha="left", va="bottom", fontsize=5.5, color=INK2)
    a.set_xticks(range(len(units)))
    a.set_xticklabels([lab(u) for u in units], rotation=90, fontsize=5)
    a.set_ylim(-3.4, 4)
    a.set_ylabel("attachment exponent α")
    a.set_title("(a) P(join Y) ∝ (recent activity)$^α$")
    a.plot([], [], "o", color=C_W, ms=3, label="work (commits)")
    a.plot([], [], "o", color=C_A, ms=3, label="attention")
    a.plot([], [], "^", color=INK2, ms=3, label="own-artifact unit")
    a.legend(loc="lower left", fontsize=5.5, ncol=3, handletextpad=0.2, columnspacing=0.6)
    # (b) pooled coefficients lag vs lead
    names = [("C", "commits\nbefore"), ("C_lead", "commits\nafter"), ("M_read", "chat read\nbefore"),
             ("M_lead", "chat read\nafter"), ("M_unread", "chat\nunread")]
    for ch, col, dy in (("work", C_W, -0.15), ("att", C_A, 0.15)):
        g = s["R2"][f"{ch}:all"]
        for i, (k, _) in enumerate(names):
            p = g["b_" + k + "_pool"]
            b.plot([p["lo"], p["hi"]], [i + dy, i + dy], color=col, lw=1)
            b.plot(p["est"], i + dy, "o", color=col, ms=3.2, mec="white", mew=0.4)
    b.axvline(0, color=INK2, lw=0.6)
    b.set_yticks(range(len(names)))
    b.set_yticklabels([n for _, n in names], fontsize=5.5)
    b.invert_yaxis()
    b.set_xlabel("pooled β")
    b.set_title("(b) lag vs lead")
    fig.tight_layout(pad=0.4, w_pad=0.6)
    fig.savefig(FIG / "summary_obs_r2.pdf")
    fig.savefig(FIG / "summary_obs_r2.png", dpi=200)


def page2(s):
    fig, (a, b) = plt.subplots(1, 2, figsize=(4.3, 2.4))
    rows = s["R3"]["rows"]
    units = sorted(rows, key=ukey)
    for ax, key, ref, ttl, yl in ((a, "theta", 1, "(a) project commits ∝ $n^θ$", "crowding exponent θ"),
                                  (b, "commit", 0, "(b) herded vs solo agent", "log rate ratio (commits)")):
        xs = 0
        tick = []
        for u in units:
            w = rows[u].get(key)
            if not w or w.get("est") is None:
                continue
            col = C_A if rows[u]["group"] == "own" else C_W
            mk = "^" if rows[u]["group"] == "own" else "o"
            ax.plot([xs, xs], [w["lo"], w["hi"]], color=col, lw=0.8)
            ax.plot(xs, w["est"], mk, color=col, ms=3.2, mec="white", mew=0.4)
            tick.append((xs, lab(u)))
            xs += 1
        ax.axhline(ref, color=INK2, lw=0.6, ls="--" if ref else "-")
        ax.set_xticks([t for t, _ in tick])
        ax.set_xticklabels([n for _, n in tick], rotation=90, fontsize=5)
        ax.set_title(ttl)
        ax.set_ylabel(yl)
    for grp, col in (("shared", C_W), ("own", C_A)):
        p = s["R3"][grp]["theta_pool"]
        a.axhspan(p["lo"], p["hi"], color=col, alpha=0.12, lw=0)
        q = s["R3"][grp]["commit_pool"]
        b.axhspan(q["lo"], q["hi"], color=col, alpha=0.12, lw=0)
    a.plot([], [], "o", color=C_W, ms=3, label="shared week")
    a.plot([], [], "^", color=C_A, ms=3, label="own-artifact unit")
    a.legend(loc="upper right", fontsize=5.5)
    b.set_ylim(-1.3, 1.3)
    fig.tight_layout(pad=0.4, w_pad=0.6)
    fig.savefig(FIG / "r2_output.pdf")
    fig.savefig(FIG / "r2_output.png", dpi=200)


if __name__ == "__main__":
    s = json.loads((RES / "score_r2.json").read_text())
    page1(s)
    page2(s)
