"""H58 figures: synthetic validation (axis F), replication across units, re-acquisition after erasures, and the two
summary-page panels. Reads data/processed/H58-coordinated-superagents/results/*.json. Writes figures/*.pdf.
Run: uv run python hypotheses/H58-coordinated-superagents/analysis/figures.py"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h58data as HD  # noqa: E402

RES = HD.D / "results"
FIG = HERE.parent / "figures"
C_DATA = "#1f4e79"
C_NULL = "#9a9a9a"
C_ACC = "#c0504d"
C_ALT = "#4f9a5f"
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42})


def synthetic_fig(path, compact=False):
    R = json.loads((RES / "synthetic.json").read_text())
    rows = [r for r in R if r["rep"] < 1000]
    rhos = [0.2, 0.35, 0.5, 0.7]
    groups = {"≥ 100 bins (#51)": lambda r: r["nB"] >= 100, "40–99 bins": lambda r: 40 <= r["nB"] < 100,
              "< 40 bins": lambda r: r["nB"] < 40}
    if compact:
        fig, ax = plt.subplots(1, 1, figsize=(3.4, 2.0))
        axes = [ax]
    else:
        fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.4))
    ax = axes[0]
    styles = ["-", "--", ":"]
    for (lab, f), ls in zip(groups.items(), styles):
        ys = [np.mean([r["qualifies"] for r in rows if r["world"] == "store" and r["rho"] == rho and f(r)] or [np.nan])
              for rho in rhos]
        ax.plot(rhos, ys, ls, color=C_DATA, marker="o", ms=3, label=f"g rule, {lab}")
        yb = [np.mean([bool(r.get("z_bin") is not None and r["z_bin"] >= 2) for r in rows
                       if r["world"] == "store" and r["rho"] == rho and f(r)] or [np.nan]) for rho in rhos]
        ax.plot(rhos, yb, ls, color=C_ACC, marker="s", ms=3, alpha=0.8, label=f"H01 binary z, {lab}" if not compact else None)
    fo = np.mean([r["qualifies"] for r in rows if r["world"] == "own"])
    fe = np.mean([r["qualifies"] for r in rows if r["world"] == "env"])
    ax.axhline(fo, color=C_NULL, lw=0.8)
    ax.axhline(fe, color=C_NULL, lw=0.8, ls="--")
    ax.text(0.71, fo + 0.02, f"W_own {fo:.2f}", color=C_NULL, fontsize=6)
    ax.text(0.71, fe + 0.06, f"W_env {fe:.2f}", color=C_NULL, fontsize=6)
    ax.set_xlabel("planted store strength ρ")
    ax.set_ylabel("detection rate")
    ax.set_ylim(-0.02, 1.02)
    ax.set_title("planted group store vs nulls (real schedules)", fontsize=8)
    ax.legend(fontsize=5.5, frameon=False, loc="upper left")
    if compact:
        fig.tight_layout()
        fig.savefig(path)
        plt.close(fig)
        return
    # panel 2: Krakauer criteria by world
    ax = axes[1]
    worlds = [("own", 0.0), ("env", 0.5), ("store", 0.5)]
    labs = ["W_own", "W_env", "W_store ρ=.5"]
    a1 = [np.nanmean([bool(r["iota_unit"] >= r["iota_members"]) for r in rows if r["world"] == w and r["rho"] == rho
                      and r.get("iota_unit") is not None and r.get("iota_members") is not None
                      and np.isfinite(r["iota_unit"]) and np.isfinite(r["iota_members"])]) for (w, rho) in worlds]
    a2 = [np.nanmean([bool(r.get("z_iota_shift") is not None and r["z_iota_shift"] >= 2) for r in rows
                      if r["world"] == w and r["rho"] == rho]) for (w, rho) in worlds]
    x = np.arange(3)
    ax.bar(x - 0.18, a1, 0.36, color=C_NULL, label="ι_unit ≥ members' ι (P4 as written)")
    ax.bar(x + 0.18, a2, 0.36, color=C_DATA, label="ι_unit > aggregation baseline (A1)")
    ax.set_xticks(x, labs)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("rate")
    ax.set_title("Krakauer individuality criteria", fontsize=8)
    ax.legend(fontsize=5.5, frameon=False)
    # panel 3: search recovery
    ax = axes[2]
    S = [r for r in R if r["rep"] >= 1000]
    vals = []
    for (w, rho) in worlds:
        sub = [r for r in S if r["world"] == w and r["rho"] == rho]
        vals.append((np.mean([bool(r.get("search_qualifies")) for r in sub]) if sub else np.nan,
                     np.mean([bool(r.get("search_jaccard") is not None and r["search_jaccard"] >= 0.5) for r in sub])
                     if (sub and w == "store") else np.nan))
    ax.bar(x - 0.18, [v[0] for v in vals], 0.36, color=C_DATA, label="search result qualifies")
    ax.bar(x + 0.18, [v[1] for v in vals], 0.36, color=C_ALT, label="Jaccard(found, planted) ≥ 0.5")
    ax.set_xticks(x, labs)
    ax.set_ylim(0, 1.05)
    ax.set_title("calibrated subset search", fontsize=8)
    ax.legend(fontsize=5.5, frameon=False)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def replication_fig(path, compact=False):
    rep = json.loads((RES / "replication.json").read_text())
    units = rep["units_order"]
    fig, ax = plt.subplots(1, 1, figsize=(3.4, 2.1) if compact else (7.2, 2.6))
    x = np.arange(len(units))
    for i, u in enumerate(units):
        r = rep["per_unit"][u]
        for c in r["candidates_plot"]:
            col = {"search": C_DATA, "multi": C_ALT, "room": C_ACC, "lab": C_NULL}.get(c["kind"], C_NULL)
            mk = {"search": "D", "multi": "o", "room": "s", "lab": "^"}.get(c["kind"], ".")
            z = c["z"]
            if z is None:
                continue
            ax.scatter(i + {"search": -0.2, "multi": 0, "room": 0.15, "lab": 0.3}.get(c["kind"], 0),
                       np.clip(z, -4, 8), s=14 if c["qualifies"] else 7, marker=mk,
                       facecolors=col if c["qualifies"] else "none", edgecolors=col, lw=0.7)
    ax.axhline(2, color=C_NULL, lw=0.7, ls="--")
    ax.axhline(0, color=C_NULL, lw=0.5)
    ax.set_xticks(x, units, rotation=90 if not compact else 90, fontsize=6)
    ax.set_ylabel("min(z_spec, z_shift) of g")
    for kind, col, mk in (("search", C_DATA, "D"), ("multi-layer", C_ALT, "o"), ("room", C_ACC, "s"), ("lab", C_NULL, "^")):
        ax.scatter([], [], marker=mk, edgecolors=col, facecolors="none", label=kind, s=10)
    ax.legend(fontsize=5.5, frameon=False, ncol=4, loc="upper left")
    ax.set_title("coordination gain of candidate units (filled = qualifies)", fontsize=8)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def reacq_fig(path):
    rq = json.loads((RES / "reacq.json").read_text())
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.4))
    ax = axes[0]
    ets = ["forced", "voluntary", "placebo"]
    outs = ["own", "group", "other"]
    cols = [C_DATA, C_ACC, C_NULL]
    for i, et in enumerate(ets):
        d = rq["outcomes_divergent"][et]
        tot = sum(d[o] for o in outs if d[o] is not None)
        bottom = 0
        for o, c in zip(outs, cols):
            v = (d[o] or 0) / tot if tot else 0
            ax.bar(i, v, 0.6, bottom=bottom, color=c, label=o if i == 0 else None)
            bottom += v
        ax.text(i, 1.02, f"n={d['n']}", ha="center", fontsize=6)
    ax.set_xticks(range(3), ets)
    ax.set_ylabel("share of first commits (divergent events)")
    ax.set_title("where a member goes when its own and the unit's artifact differ", fontsize=7.5)
    ax.legend(fontsize=6, frameon=False)
    ax = axes[1]
    keys = [("int_pre", "intention names own"), ("read_pre", "touches own artifact"), ("peer_member", "item from a member"),
            ("peer_named_pre", "chat names own")]
    for j, et in enumerate(["forced", "placebo"]):
        s = rq["sources"][et]["returned_own"]
        ax.barh(np.arange(len(keys)) + 0.2 * (1 - 2 * j), [s[k] or 0 for k, _ in keys], 0.38,
                color=[C_DATA, C_NULL][j], label=f"{et} (returns to own)")
    ax.set_yticks(range(len(keys)), [lab for _, lab in keys], fontsize=6.5)
    ax.set_xlabel("share of events with the source before the first commit")
    ax.legend(fontsize=6, frameon=False)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def main():
    FIG.mkdir(exist_ok=True)
    which = sys.argv[1:] or ["synthetic", "replication", "reacq"]
    if "synthetic" in which:
        synthetic_fig(FIG / "synthetic_validation.pdf")
        synthetic_fig(FIG / "summary_synthetic.pdf", compact=True)
    if "replication" in which:
        replication_fig(FIG / "replication.pdf")
        replication_fig(FIG / "summary_obs.pdf", compact=True)
    if "reacq" in which:
        reacq_fig(FIG / "reacq.pdf")


if __name__ == "__main__":
    main()
