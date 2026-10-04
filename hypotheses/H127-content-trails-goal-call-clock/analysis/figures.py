"""H127 figures: figures/summary_obs.pdf ((a) normalized day-1 excess alignment vs own calls since the read-out call, both
models, with the shape a call-clock rise would give; (b) the same vs hours since t0 for slow and fast call-rate halves) and
figures/synthetic_compact.pdf (pass rates of the pooled slope P1 and the read-out-origin clock test P3 by world and amplitude)."""
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
import h127lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "writeup/visuals"))
import vstyle as vs  # noqa: E402

FIG = HERE.parent / "figures"


def obs():
    vs.use()
    rc = json.loads((L.DATA / "NE34/rise_curve.json").read_text())
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.4))
    lab = rc["bge_white"]["labels_calls"][1:]
    x = np.arange(len(lab))
    for cfg, col, off in (("bge_white", vs.C["blue"], -0.08), ("gte_white", vs.C["orange"], 0.08)):
        c = rc[cfg]["calls_ro"]
        m, se = np.array(c["mean"][1:]), np.array(c["se"][1:])
        ax[0].errorbar(x + off, m, yerr=1.645 * se, color=col, marker="o", ms=3, capsize=1.5, lw=1.2, label=cfg.split("_")[0])
    mid = np.array([1, 2.5, 5.5, 11.5, 23.5, 47.5, 100])
    ax[0].plot(x, 1 - np.exp(-mid / 20), color=vs.MUTED, ls="--", lw=1, label="call-clock rise, τ = 20 calls")
    ax[0].axhline(1, color=vs.NULL, lw=0.8)
    ax[0].set_xticks(x); ax[0].set_xticklabels(lab, fontsize=6.5)
    ax[0].set_xlabel("own calls since the read-out call"); ax[0].set_ylabel("(a − P) / day-1 plateau")
    ax[0].set_title("(a) alignment peaks at the read-out call", loc="left")
    ax[0].legend(fontsize=6, loc="lower right")
    hl = rc["bge_white"]["labels_hours"]
    xh = np.arange(len(hl))
    for key, col, mk, lb in (("hours_t0_slow", vs.C["green"], "s", "slow half"), ("hours_t0_fast", vs.C["red"], "^", "fast half")):
        c = rc["bge_white"][key]
        ax[1].errorbar(xh, c["mean"], yerr=1.645 * np.array(c["se"]), color=col, marker=mk, ms=3, capsize=1.5, lw=1.2, label=f"{lb} (bge)")
    ax[1].axhline(1, color=vs.NULL, lw=0.8)
    ax[1].set_xticks(xh); ax[1].set_xticklabels(hl, fontsize=6.5)
    ax[1].set_xlabel("time since the kickoff t₀"); ax[1].set_ylabel("(a − P) / day-1 plateau")
    ax[1].set_title("(b) slow and fast agents, hour clock", loc="left")
    ax[1].legend(fontsize=6)
    fig.tight_layout()
    vs.save(fig, FIG / "summary_obs")


def synth():
    vs.use()
    r = json.loads((L.DATA / "synthetic/results_bge_white.json").read_text())["worlds"]
    worlds = ["W_0.15", "W_0.7", "LW_0.5", "L", "C_20", "C_100"]
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.0), sharey=True)
    for j, (key, title) in enumerate((("P1_pool", "pooled slope P1"), ("P3_ro", "read-out clock test P3 (ΔSSE_ro > 0)"))):
        for k, (amp, col) in enumerate(((0.1, vs.C["sky"]), (0.2, vs.C["blue"]), (0.4, vs.C["pink"]))):
            ax[j].bar(np.arange(len(worlds)) + (k - 1) * 0.27, [r[f"{w}|{amp}"][key] for w in worlds], width=0.27, color=col, label=f"Δ = {amp}")
        ax[j].axvline(3.5, color=vs.MUTED, ls="--", lw=0.8)
        ax[j].set_xticks(range(len(worlds))); ax[j].set_xticklabels(["hour τ0.15", "hour τ0.7", "read-out+hour", "read-out jump", "call τ20", "call τ100"], fontsize=6, rotation=30, ha="right")
        ax[j].set_title(title, loc="left"); ax[j].set_ylim(0, 1.05)
    ax[0].set_ylabel("pass rate"); ax[0].legend(fontsize=6, loc="upper left")
    fig.tight_layout()
    vs.save(fig, FIG / "synthetic_compact")


if __name__ == "__main__":
    synth()
    obs()
