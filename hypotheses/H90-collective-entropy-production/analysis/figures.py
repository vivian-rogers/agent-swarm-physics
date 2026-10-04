"""H90 figures: summary_obs.pdf (talk address contrast per period vs the block-shift null; behavior single vs collective)
and synthetic_compact.pdf (power of Delta_addr and false positives of sigma_coll under a lagged field).
  uv run python hypotheses/H90-collective-entropy-production/analysis/figures.py
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h90lib as L  # noqa: E402

FIG = L.ROOT / "hypotheses/H90-collective-entropy-production/figures"
C1, C2, C3, GREY = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984"
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.6,
                     "xtick.major.width": 0.6, "ytick.major.width": 0.6, "legend.frameon": False})


def obs():
    s = json.load(open(L.OUTD / "results/summary.json"))
    gs = [g for g in s if g != "across"]
    fig, ax = plt.subplots(1, 2, figsize=(6.8, 2.4))
    x = np.arange(len(gs))
    for k, g in enumerate(gs):
        t = s[g]["channels"]["talk"]
        sc = 1e3
        nam, un = t["obs"]["coll_named"] * sc, t["obs"]["coll_unnamed"] * sc
        lo, hi = (np.array(t["ci"]["coll_named"]) * sc)
        ax[0].plot([k - 0.12] * 2, [lo, hi], color=C1, lw=1)
        ax[0].plot(k - 0.12, nam, "o", color=C1, ms=4, label="named partners σ_nam" if k == 0 else None)
        lo, hi = (np.array(t["ci"]["coll_unnamed"]) * sc)
        ax[0].plot([k + 0.12] * 2, [lo, hi], color=C2, lw=1)
        ax[0].plot(k + 0.12, un, "s", color=C2, ms=4, label="unnamed partners σ_un" if k == 0 else None)
        ax[0].plot([k - 0.3, k + 0.3], [t["shift_coll_named"]["q95"] * sc] * 2, color=GREY, lw=1,
                   label="block-shift null, 95th pct (σ_nam)" if k == 0 else None)
    ax[0].axhline(0, color=GREY, lw=0.5)
    ax[0].set_xticks(x, [f"G{g}" for g in gs])
    ax[0].set_ylabel("collective EP, talk (10⁻³ nats / min)")
    ax[0].set_ylim(-25, 15)
    ax[0].legend(loc="lower left", fontsize=6.5)
    ax[0].set_title("(a) talk: collective EP by partner set", fontsize=8, loc="left")
    for k, g in enumerate(gs):
        b = s[g]["channels"]["behavior"]
        if "obs" not in b:
            continue
        s1 = b["obs"]["Sigma1"] * 1e3
        cl = b["obs"]["coll_all"] * 1e3
        ax[1].bar(k - 0.18, s1, width=0.34, color=C1, label="single-agent Σ₁" if k == 0 else None)
        ax[1].bar(k + 0.18, cl, width=0.34, color=C3, label="collective σ_coll (all)" if k == 0 else None)
    ax[1].axhline(0, color=GREY, lw=0.5)
    ax[1].set_xticks(x, [f"G{g}" for g in gs])
    ax[1].set_ylabel("EP, behavior (10⁻³ nats / 5 min)")
    ax[1].set_ylim(-160, 120)
    ax[1].legend(loc="upper left", fontsize=6.5, ncol=2)
    ax[1].set_title("(b) behavior: single vs collective", fontsize=8, loc="left")
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs.pdf")
    fig.savefig(FIG / "summary_obs.png", dpi=150)


def syn():
    e = pl.read_parquet(L.OUTD / "synthetic/effect_power.parquet")
    r = pl.read_parquet(L.OUTD / "synthetic/replicates.parquet").filter(pl.col("channel") == "talk")
    sizes = ["S40", "S38", "S51"]
    rows = []
    for J, scen in ((0.0, "0"), (0.5, "C0.5"), (1.0, "C1")):
        for sz in sizes:
            d = r.filter((pl.col("scen") == scen) & (pl.col("size") == sz))
            rows.append((J, sz, float((d["addr_p_shift"] < 0.05).mean())))
    for J in (0.25, 0.35):
        for sz in sizes:
            d = e.filter((pl.col("J") == J) & (pl.col("size") == sz))
            rows.append((J, sz, float((d["addr_p_shift"] < 0.05).mean())))
    fig, ax = plt.subplots(1, 2, figsize=(6.8, 2.1))
    lab = {"S40": "N 15 × 5 d (G39–G42)", "S38": "N 13 × 16 d (G38)", "S51": "N 27 × 33 d (G51)"}
    for sz, c, m in zip(sizes, (C2, C3, C1), ("s", "^", "o")):
        pts = sorted([(J, p) for J, s_, p in rows if s_ == sz])
        ax[0].plot([p[0] for p in pts], [p[1] for p in pts], marker=m, color=c, lw=1.5, ms=4, label=lab[sz])
    ax[0].axvline(0.28, color=GREY, lw=0.8, ls="--")
    ax[0].text(0.30, 0.08, "G51's\nestimate", fontsize=6.5, color="#55534e")
    ax[0].set_xlabel("planted gated coupling J (talk)")
    ax[0].set_ylabel("power of Δ_addr (p < 0.05)")
    ax[0].legend(fontsize=6.5, loc="lower right")
    ax[0].set_title("(a) address contrast: power", fontsize=8, loc="left")
    sz_check = pl.read_parquet(L.OUTD / "synthetic/size_check.parquet").filter(pl.col("scen") == "F")
    vals = []
    for sz in sizes:
        d = r.filter((pl.col("scen") == "F") & (pl.col("size") == sz))
        if sz in ("S38", "S51"):
            d = sz_check.filter(pl.col("size") == sz)
        vals.append((float((d["coll_all_p_shift"] < 0.05).mean()), float((d["addr_p_shift"] < 0.05).mean())))
    xx = np.arange(3)
    ax[1].bar(xx - 0.18, [v[0] for v in vals], width=0.34, color=C2, label="σ_coll(all) > shift null")
    ax[1].bar(xx + 0.18, [v[1] for v in vals], width=0.34, color=C1, label="Δ_addr > shift null")
    ax[1].axhline(0.05, color=GREY, lw=0.8, ls="--")
    ax[1].set_xticks(xx, ["N15×5d", "N13×16d", "N27×33d"])
    ax[1].set_ylabel("false-positive rate")
    ax[1].set_ylim(0, 1.05)
    ax[1].legend(fontsize=6.5, loc="upper left")
    ax[1].set_title("(b) lagged field, no coupling", fontsize=8, loc="left")
    fig.tight_layout()
    fig.savefig(FIG / "synthetic_compact.pdf")
    fig.savefig(FIG / "synthetic_compact.png", dpi=150)


if __name__ == "__main__":
    FIG.mkdir(exist_ok=True)
    obs()
    syn()
