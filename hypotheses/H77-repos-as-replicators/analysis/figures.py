"""H77 figures: summary_obs.pdf (sigma* per period vs the neutral band and the prediction lines) and summary_synth.pdf
(synthetic sigma* recovery at E = 100)."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
HYP = ROOT / "hypotheses/H77-repos-as-replicators"
DATA = ROOT / "data/processed/H77-repos-as-replicators"
HERD = [31, 33, 41]
OWN = [39, 42, 51]
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42})
C_HERD, C_OWN, C_NAT = "#2166ac", "#b2182b", "#5a5a5a"


def res(name):
    p = DATA / "results" / f"{name}.json"
    return json.loads(p.read_text()) if p.exists() else None


def fig_obs():
    fig, ax = plt.subplots(figsize=(3.4, 2.3))
    ax.axhline(1, color=C_HERD, lw=0.7, ls="--")
    ax.axhline(0.3, color=C_OWN, lw=0.7, ls="--")
    ax.axhline(0, color="k", lw=0.5, ls=":")
    labels, x = [], 0
    items = [(f"G{g:02d}", f"#{g}", C_HERD) for g in HERD] + [(f"G{g:02d}", f"#{g}", C_OWN) for g in OWN] + \
            [("G40", "#40", C_NAT), ("G44_arm2", "#44\nbest", C_NAT), ("G44_arm3", "#44\nrest", C_NAT)]
    for name, lab, col in items:
        r = res(name)
        labels.append(lab)
        s = r and r.get("sigma")
        if s and s["J_plus"] + s["J_minus"] > 0:
            mk = "o" if s["testable"] else "o"
            ax.errorbar(x, s["est"], yerr=[[s["est"] - s["lo"]], [s["hi"] - s["est"]]], fmt=mk, color=col, ms=4, capsize=2,
                        mfc=col if s["testable"] else "white")
            nb = r.get("neutral_null")
            if nb:
                ax.plot([x - 0.3, x + 0.3], [nb["q95"]] * 2, color="0.5", lw=1.2)
        else:
            ax.text(x, 0.1, "n/a", ha="center", fontsize=6, color=col)
        x += 1
    ax.set_xticks(range(len(labels)), labels, fontsize=6.5)
    ax.set_ylabel(r"$\hat\sigma^*$ (nats per copy)")
    ax.set_ylim(-3.6, 4.2)
    ax.text(0.99, 0.97, "open: untestable (J$^+$+J$^-$<8); gray bar: neutral 95%", transform=ax.transAxes, fontsize=5.5,
            ha="right", va="top")
    fig.tight_layout()
    fig.savefig(HYP / "figures/summary_obs.pdf")
    plt.close(fig)


def fig_synth():
    runs = []
    for p in sorted((DATA / "synthetic").glob("runs_G??.parquet")):
        runs.append(pl.read_parquet(p))
    d = pl.concat(runs, how="diagonal_relaxed").filter(pl.col("sigma").is_not_null() & pl.col("sigma_true").is_not_null()
                                                         & pl.col("sigma_testable"))
    fig, ax = plt.subplots(figsize=(3.4, 2.1))
    cols = {"neutral": "0.4", "conformist": C_HERD, "parabolic": C_OWN, "field": "#e08214", "neutral_eps_lo": "0.7",
            "neutral_eps_hi": "0.2"}
    for w, c in cols.items():
        x = d.filter(pl.col("world") == w)
        ax.scatter(x["sigma_true"], x["sigma"], s=3, color=c, alpha=0.5, label=w.replace("neutral_eps_", "neutral ε "), lw=0)
    ax.plot([-2, 5], [-2, 5], "k:", lw=0.7)
    ax.set_xlim(-2, 5)
    ax.set_ylim(-2, 5)
    ax.set_xlabel(r"true $\sigma^*$ (simulated events)")
    ax.set_ylabel(r"measured $\hat\sigma^*$ (labels)")
    ax.legend(fontsize=5, frameon=False, markerscale=2, loc="upper left")
    fig.tight_layout()
    fig.savefig(HYP / "figures/summary_synth.pdf")
    plt.close(fig)


if __name__ == "__main__":
    fig_obs()
    fig_synth()
