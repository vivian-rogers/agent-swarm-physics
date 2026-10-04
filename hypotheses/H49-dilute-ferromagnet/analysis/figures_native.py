"""H49 per-period figures for the native tests (reads native/*.json and bonds/*.parquet).

goalperiod-subhypotheses/NE43/figures/ne43.png   edge-induced excess per window + bond persistence
goalperiod-subhypotheses/G44/figures/g44.png     conditioned bond z among the 16 agents, #best first
goalperiod-subhypotheses/G51/figures/g51.png     per-unit dense shift vs bonds; enrichment of bonds by pair type
goalperiod-subhypotheses/NE14/figures/ne14.png   conditioned and raw bond z, II side vs III side
Usage: uv run python hypotheses/H49-dilute-ferromagnet/analysis/figures_native.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import h49lib as L  # noqa: E402

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

GP = L.HYP / "goalperiod-subhypotheses"
NAT = L.DATA / "native"
C3, CG = "#1f5fa8", "#888888"


def bonds(uid, variant="scaffold"):
    return pl.read_parquet(L.DATA / "bonds" / f"{uid}.parquet").filter(
        (pl.col("variant") == variant) & (pl.col("channel") == "activity"))


def zmat(b, agents):
    ix = {a: k for k, a in enumerate(agents)}
    Z = np.full((len(agents), len(agents)), np.nan)
    S = np.zeros_like(Z, bool)
    for a, c, z, s in zip(b["a"].to_list(), b["b"].to_list(), b["z"].to_list(), b["sig_pos"].to_list()):
        Z[ix[a], ix[c]] = Z[ix[c], ix[a]] = z
        S[ix[a], ix[c]] = S[ix[c], ix[a]] = s
    return Z, S


def ne43():
    j = json.loads((NAT / "NE43.json").read_text())
    W = ["NE43_W1", "NE43_W2", "NE43_W3"]
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.6))
    x = np.arange(3)
    for k, (key, lab, col) in enumerate((("E_raw", "raw", CG), ("E_edge", "edge-trimmed", "#7fa7d6"),
                                         ("E_scaffold", "scaffold-conditioned", C3))):
        ax[0].bar(x + (k - 1) * 0.27, [j["windows"][w][key] for w in W], 0.27, color=col, label=lab)
    ee = [j["windows"][w]["edge_ex"] for w in W]
    ci = np.array([j["windows"][w]["edge_ex_ci"] for w in W])
    ax[0].errorbar(x + 0.42, ee, yerr=[np.array(ee) - ci[:, 0], ci[:, 1] - np.array(ee)], fmt="kd", ms=4,
                   label="edge-induced (raw − edge)")
    ax[0].set_xticks(x); ax[0].set_xticklabels(["W1 bookends on", "W2 msgs off", "W3 nudges off"], fontsize=7)
    ax[0].set_ylabel("excess gain over null", fontsize=8); ax[0].legend(fontsize=6, frameon=False)
    ax[0].set_title("(a) day-edge excess persists without bookends", fontsize=8)
    pers = j["persistence"]
    sh = j["split_half"]
    keys = list(pers)
    ax[1].bar(np.arange(3) - 0.18, [pers[k]["r"] for k in keys], 0.36, color=C3, label="across windows (r)")
    ax[1].bar(np.arange(3) + 0.18, [sh[w]["r_half"] for w in W], 0.36, color=CG, label="within window, split-half (W1, W2, W3)")
    ax[1].axhline(0, color="k", lw=0.5)
    ax[1].axhline(0.5, color="k", lw=0.5, ls=":")
    ax[1].set_xticks(np.arange(3)); ax[1].set_xticklabels([f"{k} / {w[-2:]}" for k, w in zip(keys, W)], fontsize=7)
    ax[1].set_ylim(-0.2, 0.6)
    ax[1].set_ylabel("correlation of conditioned bond z", fontsize=8); ax[1].legend(fontsize=6, frameon=False)
    ax[1].set_title("(b) no reliable pair structure to persist", fontsize=8)
    fig.tight_layout()
    (GP / "NE43/figures").mkdir(parents=True, exist_ok=True)
    fig.savefig(GP / "NE43/figures/ne43.png", dpi=160); plt.close(fig)


def g44():
    j = json.loads((L.DATA / "G44/G44_all.json").read_text())
    agents = j["agents"]
    team = [24, 25, 26, 27]
    order = [a for a in team if a in agents] + [a for a in agents if a not in team]
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 3.1))
    for k, v in enumerate(("raw", "scaffold")):
        Z, S = zmat(bonds("G44_all", v), order)
        im = ax[k].imshow(Z, cmap="RdBu_r", vmin=-4, vmax=4)
        ii, jj = np.nonzero(S)
        ax[k].scatter(jj, ii, marker="*", s=18, c="k")
        ax[k].axhline(3.5, color="k", lw=0.6); ax[k].axvline(3.5, color="k", lw=0.6)
        ax[k].set_xticks(range(len(order))); ax[k].set_xticklabels(order, fontsize=5, rotation=90)
        ax[k].set_yticks(range(len(order))); ax[k].set_yticklabels(order, fontsize=5)
        ax[k].set_title(f"({'ab'[k]}) bond z, {'raw' if v == 'raw' else 'conditioned'}; #best = first 4", fontsize=8)
    fig.colorbar(im, ax=ax, shrink=0.8, label="z")
    (GP / "G44/figures").mkdir(parents=True, exist_ok=True)
    fig.savefig(GP / "G44/figures/g44.png", dpi=160, bbox_inches="tight"); plt.close(fig)


def g51():
    j = json.loads((NAT / "G51.json").read_text())
    ut = pl.read_parquet(L.DATA / "unit_table.parquet").filter(pl.col("goal_no") == 51)
    ut = ut.filter(pl.col("kind") == "replication").sort("unit")
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.6))
    x = np.arange(ut.height)
    ax[0].bar(x - 0.2, ut["mean_z"], 0.4, color=C3, label="mean bond z (dense shift)")
    ax0 = ax[0].twinx()
    ax0.bar(x + 0.2, ut["n_pos"], 0.4, color=CG, label="significant + bonds")
    ax0.axhline(1, color="k", lw=0.5, ls=":")
    ax[0].set_xticks(x); ax[0].set_xticklabels(ut["unit"].to_list(), fontsize=7)
    ax[0].set_ylabel("mean z", fontsize=8); ax0.set_ylabel("bonds (≈1 expected false)", fontsize=8)
    ax[0].set_title("(a) #51 units: shift without bonds", fontsize=8)
    en = j["enrichment_51"]
    keys = [k for k in ("same_lab", "rival", "opposed", "same_room") if k in en]
    ax[1].bar(range(len(keys)), [en[k]["dz"] for k in keys], color=C3)
    for i, k in enumerate(keys):
        ax[1].text(i, en[k]["dz"], f"p={en[k]['p_perm']:.2f}\nn={en[k]['n_attr_pairs']}", ha="center",
                   va="bottom" if en[k]["dz"] >= 0 else "top", fontsize=6)
    ax[1].axhline(0, color="k", lw=0.5)
    ax[1].set_xticks(range(len(keys))); ax[1].set_xticklabels(keys, fontsize=7)
    ax[1].set_ylabel("Δ mean bond z (pair type − rest)", fontsize=8)
    ax[1].set_title("(b) which pairs carry the bonds", fontsize=8)
    fig.tight_layout()
    (GP / "G51/figures").mkdir(parents=True, exist_ok=True)
    fig.savefig(GP / "G51/figures/g51.png", dpi=160); plt.close(fig)


def ne14():
    agents = json.loads((L.DATA / "NE14/NE14_II.json").read_text())["agents"]
    fig, ax = plt.subplots(1, 2, figsize=(6.4, 2.8))
    iu = np.triu_indices(len(agents), 1)
    for k, v in enumerate(("raw", "scaffold")):
        Za, _ = zmat(bonds("NE14_II", v), agents)
        Zb, _ = zmat(bonds("NE14_III", v), agents)
        ax[k].scatter(Za[iu], Zb[iu], s=8, c=C3 if v == "scaffold" else CG, alpha=0.7)
        lim = [min(np.nanmin(Za[iu]), np.nanmin(Zb[iu])) - 0.3, max(np.nanmax(Za[iu]), np.nanmax(Zb[iu])) + 0.3]
        ax[k].plot(lim, lim, "k:", lw=0.5)
        r = np.corrcoef(Za[iu], Zb[iu])[0, 1]
        ax[k].set_title(f"({'ab'[k]}) {v}: r = {r:.2f}", fontsize=8)
        ax[k].set_xlabel("bond z, regime II side", fontsize=8); ax[k].set_ylabel("bond z, regime III side", fontsize=8)
    fig.tight_layout()
    (GP / "NE14/figures").mkdir(parents=True, exist_ok=True)
    fig.savefig(GP / "NE14/figures/ne14.png", dpi=160); plt.close(fig)


if __name__ == "__main__":
    for f in (ne43, g44, g51, ne14):
        try:
            f()
            print(f.__name__, "ok")
        except FileNotFoundError as e:
            print(f.__name__, "skipped", e)
