"""H43 figures (matplotlib, light print style; categorical slots blue / orange / aqua, null in neutral gray).

  synthetic   figures/synthetic_validation.pdf   (a) mention R(delta) under null / habituation clock / episode lock;
                                                  (b) episode test: R for busy recipients inside a launched episode
                                                      vs read while busy without one
  summary     figures/summary_obs.pdf            refractory ratio vs read-out spacing per class (real data)
  periods     figures/cross_period.pdf           mention R(0-15) and R(15-60) per goal period
Usage:  uv run python hypotheses/H43-kick-refractory-window/analysis/figures.py [synthetic|summary|periods|all]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h43lib as L  # noqa: E402

FIG = L.HDIR / "figures"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
BLUE, ORANGE, AQUA, GRAY = "#2a78d6", "#eb6834", "#1baf7a", "#8a8986"
MID = {"0-2": 1.0, "2-5": 3.2, "5-15": 8.7, "15-30": 21.2, "30-60": 42.4, "60-120": 84.9, "120-240": 170.0}


def style():
    plt.rcParams.update({"font.size": 7.5, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                         "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                         "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
                         "legend.frameon": False, "pdf.fonttype": 42})


def synthetic():
    d = json.loads((L.OUT / "synthetic" / "synthetic_results.json").read_text())
    runs = [r for r in d["runs"] if r["scale"] == "G51" and r["n_mode"] == "policy"]
    fig, ax = plt.subplots(1, 2, figsize=(3.45, 2.0), gridspec_kw={"width_ratios": [1.45, 1]})
    a = ax[0]
    for var, col, lab, dx in (("null", GRAY, "null", 0.95), ("time_any", ORANGE, "30-min clock", 1.0),
                              ("episode", BLUE, "episode lock", 1.05)):
        xs, med, lo, hi = [], [], [], []
        for b_ in L.DELTA_LABELS:
            v = [r["summary"]["A"]["R_bins"].get(b_) for r in runs if r["variant"] == var]
            v = [x[0] for x in v if x and x[3] is not None and x[3] >= 10 and x[0] is not None]
            if len(v) >= 3:
                xs.append(MID[b_] * dx); med.append(np.median(v))
                lo.append(np.percentile(v, 10)); hi.append(np.percentile(v, 90))
        xs, med, lo, hi = map(np.array, (xs, med, lo, hi))
        a.plot(xs, med, color=col, lw=1.6, marker="o", ms=3, label=lab, zorder=3)
        a.vlines(xs, lo, hi, color=col, lw=0.8, alpha=0.6, zorder=2)
    a.axhline(1, color=INK2, lw=0.5, ls="--")
    a.axhline(0, color=GRID, lw=0.5)
    a.set_xscale("log")
    a.set_xticks([1, 3, 10, 30])
    a.set_xticklabels(["1", "3", "10", "30"])
    a.set_xlabel("spacing $\\delta$ (min)")
    a.set_ylabel("mention $R=E_2/E_1$")
    a.set_ylim(-0.6, 2.0)
    a.legend(loc="upper left", fontsize=5.5, handlelength=1.2, borderaxespad=0.2)
    a.set_title("(a) planted vs recovered", fontsize=6.5, loc="left")
    b = ax[1]
    labels = []
    for k, (var, col) in enumerate((("null", GRAY), ("time_any", ORANGE), ("episode", BLUE))):
        for j, (st, mk) in enumerate((("act", "o"), ("in", "s"))):
            v = [r["summary"]["A"]["by_status"].get(st) for r in runs if r["variant"] == var]
            v = np.array([x[0] for x in v if x and x[0] is not None])
            x0 = k * 2.6 + j
            b.scatter(np.full(len(v), x0) + np.linspace(-0.15, 0.15, len(v)), v, s=7, color=col, marker=mk,
                      edgecolor="white", linewidth=0.3, zorder=3)
            b.hlines(np.median(v), x0 - 0.3, x0 + 0.3, color=INK, lw=1.0, zorder=4)
            labels.append((x0, "busy" if st == "act" else "in ep."))
    b.set_xticks([x for x, _ in labels])
    b.set_xticklabels([t for _, t in labels], fontsize=4.8, rotation=90)
    b.axhline(1, color=INK2, lw=0.5, ls="--")
    b.axhline(0, color=GRID, lw=0.5)
    b.set_ylim(-0.6, 2.2)
    b.set_title("(b) episode test", fontsize=6.5, loc="left")
    fig.tight_layout(pad=0.3, w_pad=0.6)
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / "synthetic_validation.pdf")
    fig.savefig(FIG / "synthetic_validation.png", dpi=250)
    plt.close(fig)


def main():
    style()
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("synthetic", "all"):
        synthetic()
    if which in ("summary", "all") and (L.OUT / "rule.json").exists():
        summary()
    if which in ("periods", "all"):
        periods()


def _pt(d):
    if not d or d.get("est") is None:
        return None
    return d["est"], d.get("lo"), d.get("hi")


def summary():
    rule = json.loads((L.OUT / "rule.json").read_text())
    summ = json.loads((L.OUT / "summary.json").read_text())
    fig, a = plt.subplots(1, 1, figsize=(3.45, 1.7))
    SAME = 0.35
    series = [("A", "O2c", BLUE, "mentions (G51)", 1.0, "bins"),
              ("H", "O2c", AQUA, "human messages (G04)", 1.08, "bins"),
              ("N", "O1a", ORANGE, "nudge re-fires (G51)", 0.93, "pool")]
    for cl, o, col, lab, dx, mode in series:
        f = rule["classes"][cl][o]["full"]
        xs, ys, lo, hi = [], [], [], []
        if mode == "bins":
            for b_, v in f["bins"].items():
                if v["n"] >= 20 and v["R"] and v["R"].get("est") is not None:
                    xs.append(MID[b_] * dx); ys.append(v["R"]["est"]); lo.append(v["R"]["lo"]); hi.append(v["R"]["hi"])
        else:
            for b_, x0 in (("15-60", 32.0), ("60-240", 120.0)):
                v = f["R_pool"].get(b_)
                if v and v["n"] >= 20:
                    xs.append(x0 * dx); ys.append(v["R"]["est"]); lo.append(v["R"]["lo"]); hi.append(v["R"]["hi"])
        xs, ys, lo, hi = map(np.array, (xs, ys, lo, hi))
        a.plot(xs, ys, color=col, lw=1.6, marker="o", ms=3, label=lab, zorder=3)
        a.vlines(xs, np.clip(lo, -0.9, 3), np.clip(hi, -0.9, 3), color=col, lw=0.8, alpha=0.7, zorder=2)
        bt = f.get("batched")
        if bt and bt.get("R") and bt["R"].get("est") is not None:
            r = bt["R"]
            a.plot([SAME * dx], [r["est"]], marker="D", ms=3.5, color=col, zorder=4)
            a.vlines([SAME * dx], max(r["lo"], -0.9), min(r["hi"], 3), color=col, lw=0.8, alpha=0.7)
    Lm = 20.0
    a.plot([0.7, Lm, Lm, 230], [0, 0, 1, 1], color=INK2, lw=0.9, ls=":", zorder=1)
    a.text(Lm * 1.1, -0.8, "H43: $R=0$ inside the\nlaunched episode", fontsize=5, color=INK2, va="bottom")
    a.axhline(1, color=INK2, lw=0.5, ls="--")
    a.axhline(0, color=GRID, lw=0.5)
    a.axvline(0.55, color=GRID, lw=0.7)
    a.set_xscale("log")
    a.set_xlim(0.25, 260)
    a.set_xticks([SAME, 1, 3, 10, 30, 100])
    a.set_xticklabels(["same\ncall", "1", "3", "10", "30", "100"], fontsize=6)
    a.set_ylim(-0.9, 2.9)
    a.set_xlabel("spacing between the two receiving calls $\\delta$ (min)", fontsize=6.5)
    a.set_ylabel("$R=E_2/E_1$", fontsize=6.5)
    a.legend(loc="upper left", fontsize=5.2, handlelength=1.2, ncol=3, borderaxespad=0.2, columnspacing=0.8)
    fig.tight_layout(pad=0.3, h_pad=0.4)
    fig.savefig(FIG / "summary_obs.pdf")
    fig.savefig(FIG / "summary_obs.png", dpi=250)
    plt.close(fig)


def periods():
    summ = json.loads((L.OUT / "summary.json").read_text())
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 3.0), sharey=False)
    for a, key, title in ((ax[0], "A_O2c", "reply at the receiving call (O2c)"), (ax[1], "A_O2", "talk within 5 min (O2)")):
        rows = []
        for row in summ["rows"]:
            d = row.get(key)
            if not d or d["E1"]["n"] < 20:
                continue
            for rng, dx, col in (("0-15", -0.15, BLUE), ("15-60", 0.15, ORANGE)):
                v = d["R_pool"].get(rng)
                if v and v["n"] >= 20 and v["R"].get("est") is not None:
                    rows.append((row["period"], rng, v["R"]["est"], v["R"]["lo"], v["R"]["hi"], d["E1_positive"], col, dx))
        ps = sorted({r[0] for r in rows})
        for p_, rng, e, lo, hi, pos, col, dx in rows:
            x = ps.index(p_) + dx
            a.plot(x, np.clip(e, -2, 4), "o" if pos else "o", mfc=col if pos else "white", mec=col, ms=3.5, zorder=3)
            a.vlines(x, np.clip(lo, -2, 4), np.clip(hi, -2, 4), color=col, lw=0.8, alpha=0.7)
        a.set_xticks(range(len(ps)))
        a.set_xticklabels(ps, rotation=90, fontsize=6)
        a.axhline(1, color=INK2, lw=0.6, ls="--")
        a.axhline(0, color=GRID, lw=0.6)
        a.set_ylim(-2, 4)
        a.set_ylabel("mention $R$")
        a.set_title(title + ": blue $\\delta\\leq$15, orange 15-60 min; open = E1 n.s.", fontsize=6.8, loc="left")
    fig.tight_layout()
    fig.savefig(FIG / "cross_period.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()
