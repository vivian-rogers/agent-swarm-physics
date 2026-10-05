"""H16 + H72 writeup visual: idle traps age by themselves; one directed kick helps.

Static figure (fig.pdf/png, double column):
  (a) simulation: per-gate escape probability vs trap age for one trap depth (Kramers: memoryless, gray) and for a
      broad spread of depths (Bouchaud-type aging), each with one kick that multiplies the escape odds by 1.54
  (b) G51 idle gates (H72 gate table, non-holdout): share of gates where the agent starts a sustained run, by trap age,
      with and without a directed read (mention or own nudge) at the gate; gray band = memoryless null
      (trap ages permuted within agent); agent-day bootstrap 95% bands
  (c) aging slope beta_a per powered aging period, without and with the input-starvation clock (H72), and the
      input-clock slope beta_s; 0 = memoryless (Kramers)

Animation (writeup/animations/H16-trap-aging.mp4): a particle in a well that deepens with age (simulation), its escape hazard falling on the
right, and one directed kick at a pause gate that lets it out; then a fresh trap.

Inputs: data/processed/H72-trap-aging-input-starvation/{gates.parquet, G17,G18,G38,G51/results.json}.
Run: uv run python writeup/visuals/H16-trap-aging/make.py [--no-anim]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from matplotlib import animation
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "writeup/visuals"))
sys.path.insert(0, str(ROOT / "infra/shared"))
import vstyle as vs  # noqa: E402
from common import holdout_mask  # noqa: E402

HERE = Path(__file__).resolve().parent
D72 = ROOT / "data/processed/H72-trap-aging-input-starvation"
KICK = vs.FIELD          # a directed message is an external field: orange
TRAP = vs.INK2
OR_KICK = 1.54           # H16 card, G51 gate OR for a directed kick (round 1)
POWERED = ["G17", "G18", "G38", "G51"]
BINS_S = np.array([5, 30, 60, 120, 240, 480, 960, 1920, 3840, 7680, 30000])


def odds_mult(p, m):
    o = p / (1 - p)
    return m * o / (1 + m * o)


def sim_curves(t):
    """Per-gate escape probability (gate every ~1 unit) for one depth vs a spread of depths (rates r ~ r^(mu-1))."""
    r = np.logspace(-4, 0, 4000)
    w = r ** (0.5 - 1) * np.gradient(r)                       # mu = 0.5 (Bouchaud broad depth distribution)
    surv = np.exp(-np.outer(t, r))                            # survival of each trap class to age t
    h_age = (surv * r * w).sum(1) / (surv * w).sum(1)
    p_age = 1 - np.exp(-h_age)
    p_kr = np.full_like(t, 1 - np.exp(-(r * w).sum() / w.sum()))
    return p_kr, p_age


def gate_table():
    g = pl.read_parquet(D72 / "gates.parquet", columns=["agent", "pt_date", "goal_no", "a_sus", "y_sus", "n_dir"])
    g = g.filter(pl.col("goal_no") == 51)
    m = np.array(holdout_mask(g["pt_date"].to_list(), g["goal_no"].to_list()))
    g = g.filter(pl.Series(~m)).drop_nulls(["a_sus", "y_sus"])
    return g


def binned(g, B=200, seed=1):
    a = g["a_sus"].to_numpy(); y = g["y_sus"].to_numpy().astype(float); kd = g["n_dir"].to_numpy() > 0
    ad = (g["agent"].cast(pl.Utf8) + "|" + g["pt_date"]).to_numpy()
    ud, inv = np.unique(ad, return_inverse=True)
    b = np.digitize(a, BINS_S) - 1
    nb = len(BINS_S) - 1
    rng = np.random.default_rng(seed)

    def rates(w, perm_a=None):
        bb = b if perm_a is None else perm_a
        out = {}
        for key, sel in (("nokick", ~kd), ("kick", kd)):
            num = np.bincount(bb[sel], weights=(y * w)[sel], minlength=nb)
            den = np.bincount(bb[sel], weights=w[sel], minlength=nb)
            out[key] = num / np.where(den > 0, den, np.nan)
            out[key + "_n"] = np.bincount(bb[sel], minlength=nb)
        return out

    est = rates(np.ones_like(y))
    draws = {"nokick": [], "kick": []}
    for _ in range(B):
        cw = rng.multinomial(len(ud), np.full(len(ud), 1 / len(ud)))[inv].astype(float)
        r = rates(cw)
        for k in draws:
            draws[k].append(r[k])
    ci = {k: np.nanpercentile(np.array(v), [2.5, 97.5], axis=0) for k, v in draws.items()}
    # memoryless null: permute trap age within agent (keeps each agent's escape rate and age mix)
    ag = g["agent"].to_numpy()
    nulls = []
    for _ in range(B):
        pb = b.copy()
        for u in np.unique(ag):
            idx = np.where(ag == u)[0]
            pb[idx] = b[rng.permutation(idx)]
        sel = ~kd
        num = np.bincount(pb[sel], weights=y[sel], minlength=nb)
        den = np.bincount(pb[sel], minlength=nb)
        nulls.append(num / np.where(den > 0, den, np.nan))
    null_ci = np.nanpercentile(np.array(nulls), [2.5, 97.5], axis=0)
    return est, ci, null_ci


def static():
    vs.use()
    fig, axs = plt.subplots(1, 3, figsize=(vs.W["double"], 2.5), gridspec_kw={"width_ratios": [1, 1.15, 0.95]})
    # (a) simulation
    ax = axs[0]
    t = np.logspace(0, 3, 200)
    p_kr, p_age = sim_curves(t)
    ax.plot(t, p_kr, color=vs.MUTED, lw=1.5, ls="--")
    ax.plot(t, p_age, color=TRAP, lw=1.5)
    ax.plot(t, odds_mult(p_age, OR_KICK), color=KICK, lw=1.5)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(1, 1000); ax.set_ylim(0.003, 0.6)
    ax.text(1.3, p_kr[0] * 1.18, "one depth (Kramers): memoryless", fontsize=6.3, color=vs.MUTED)
    ax.text(1.4, 0.012, "spread of depths:\nthe trap ages", fontsize=6.3, color=TRAP, va="top")
    ax.text(25, odds_mult(p_age, OR_KICK)[100] * 1.25, "with one kick (odds ×1.54)", fontsize=6.3, color=KICK)
    ax.set_xlabel("trap age (pause points)")
    ax.set_ylabel("escape probability per pause point")
    ax.set_title("(a) aging vs Kramers (simulation)", loc="left")

    # (b) G51 data
    ax = axs[1]
    g = gate_table()
    est, ci, null_ci = binned(g)
    mid = np.sqrt(BINS_S[:-1] * BINS_S[1:]) / 60
    ok_k = est["kick_n"] >= 40
    ax.fill_between(mid, null_ci[0], null_ci[1], color=vs.NULL, alpha=0.6, lw=0)
    ax.plot(mid, est["nokick"], "o-", color=TRAP, ms=3)
    ax.fill_between(mid, ci["nokick"][0], ci["nokick"][1], color=TRAP, alpha=0.2, lw=0)
    ax.plot(mid[ok_k], est["kick"][ok_k], "s-", color=KICK, ms=3)
    ax.fill_between(mid[ok_k], ci["kick"][0][ok_k], ci["kick"][1][ok_k], color=KICK, alpha=0.25, lw=0)
    ax.set_xscale("log")
    ax.set_ylim(0, 1)
    ax.set_xlabel("trap age at the pause point (min)")
    ax.set_ylabel("share of pause points escaped")
    ax.set_title(f"(b) G51 pause points (n = {len(g):,})", loc="left")
    ax.legend(handles=[Line2D([], [], color=KICK, marker="s", ms=3, label="directed read at pause point"),
                       Line2D([], [], color=TRAP, marker="o", ms=3, label="no directed read"),
                       Line2D([], [], color=vs.NULL, lw=5, label="ages shuffled within agent")],
              loc="upper right", fontsize=6.3, handlelength=1.4, borderaxespad=0.2)

    # (c) slopes
    ax = axs[2]
    ys = np.arange(len(POWERED))[::-1]
    for y, p in zip(ys, POWERED):
        r = json.loads((D72 / p / "results.json").read_text())["primary"]
        for val, ci_, dy, col, mk, mfc in ((r["beta_a0"], r["ci_a0"], 0.22, TRAP, "o", TRAP),
                                           (r["beta_a"], r["ci_a"], 0.0, TRAP, "o", "white"),
                                           (r["beta_s"], r["ci_s"], -0.22, vs.C["sky"], "^", vs.C["sky"])):
            ax.plot(ci_, [y + dy] * 2, color=col, lw=1.1)
            ax.plot(val, y + dy, mk, ms=3.5, color=col, mfc=mfc)
    ax.axvline(0, color=vs.INK2, lw=0.6)
    ax.axvspan(-0.05, 0.05, color=vs.NULL, alpha=0.5, lw=0)
    ax.set_yticks(ys); ax.set_yticklabels(POWERED)
    ax.set_xlim(-0.9, 0.7)
    ax.set_ylim(-0.6, ys[0] + 1.6)
    ax.text(0.07, -0.45, "memoryless", fontsize=6, color=vs.MUTED, va="center")
    ax.set_xlabel("logit slope per ln(min)")
    ax.set_title("(c) not input starvation", loc="left")
    ax.legend(handles=[Line2D([], [], color=TRAP, marker="o", ms=3, label=r"age $\beta_{a0}$"),
                       Line2D([], [], color=TRAP, marker="o", mfc="white", ms=3, label=r"age, starvation ctrl. $\beta_a$"),
                       Line2D([], [], color=vs.C["sky"], marker="^", ms=3, label=r"input clock $\beta_s$")],
              loc="upper center", fontsize=6.0, ncol=2, handlelength=1.0, columnspacing=0.6, borderaxespad=0.1)
    ax.grid(axis="y", visible=False)
    fig.tight_layout(w_pad=0.6)
    vs.save(fig, HERE / "fig")
    plt.close(fig)
    print("gates", len(g), "kick share", float((g["n_dir"] > 0).mean()))


# ------------------------------------------------------------------------------------------------ animation
def anim():
    vs.use()
    rng = np.random.default_rng(3)
    fps, T1, T2 = 24, 9.0, 4.0                 # trap 1 ages and is kicked out; trap 2 starts fresh
    nF = int((T1 + T2) * fps)
    fig = plt.figure(figsize=(8, 4.5), dpi=160)
    axT = fig.add_axes([0.05, 0.86, 0.9, 0.12]); axT.axis("off")
    axW = fig.add_axes([0.05, 0.12, 0.5, 0.68]); axW.axis("off")
    axH = fig.add_axes([0.64, 0.17, 0.32, 0.6])
    axT.text(0, 0.7, "Idle traps age by themselves; one directed kick helps", fontsize=13, va="center", color=vs.INK)
    axT.text(0, 0.1, "simulation: a trap whose depth grows with age (escape hazard falls); the memoryless "
             "Kramers hazard would stay flat", fontsize=7.5, va="center", color=vs.INK2)
    counter = axT.text(1, 0.7, "", fontsize=10, ha="right", va="center", color=vs.INK2, family="monospace")
    x = np.linspace(-2.2, 2.2, 300)
    well, = axW.plot([], [], color=vs.INK2, lw=2)
    ball, = axW.plot([], [], "o", ms=12, color=vs.INK)
    kick_arrow = axW.annotate("", xy=(0, 0), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", lw=2.5, color=KICK))
    kick_txt = axW.text(0, 0, "", fontsize=10, color=KICK, ha="center")
    depth_txt = axW.text(-2.1, -2.75, "", fontsize=8, color=vs.INK2)
    axW.set_xlim(-2.3, 2.3); axW.set_ylim(-3.0, 1.6)
    # hazard panel
    tt = np.linspace(0.3, T1, 200)
    h_age = np.minimum(0.45 * tt ** -0.77, 1.1)          # exponent: H16 G51 TS1r deep slope (-0.77)
    axH.plot(tt, np.full_like(tt, 0.3), color=vs.MUTED, ls="--", lw=1.2)
    axH.text(T1, 0.34, "Kramers (flat)", fontsize=7, color=vs.MUTED, ha="right")
    hline, = axH.plot([], [], color=TRAP, lw=1.8)
    hdot, = axH.plot([], [], "o", color=TRAP, ms=5)
    kdot, = axH.plot([], [], "s-", color=KICK, ms=5, lw=1.5)
    axH.set_xlim(0, T1 + 0.3); axH.set_ylim(0, 1.2)
    axH.set_xlabel("trap age (animation s)", fontsize=8)
    axH.set_ylabel("escape hazard", fontsize=8)
    axH.tick_params(labelsize=7)
    axH.set_title(r"hazard $\propto$ age$^{-0.77}$ (G51 slope)", fontsize=8, loc="left")
    tk = 7.0                                   # kick time (a pause gate)
    kh_txt = axH.text(tk + 0.1, 0.55, "", fontsize=7, color=KICK, ha="center")
    jitter = rng.normal(0, 1, nF)

    def U(xx, depth):
        return -depth * np.exp(-xx ** 2 / 0.6) + 0.15 * xx ** 2

    def draw(f):
        t = f / fps
        if t < T1:
            age = t
            depth = 0.8 + 1.6 * (1 - np.exp(-age / 2.5))
            xb = 0.06 * jitter[f] / np.sqrt(depth)
            if age >= tk:
                frac = min((age - tk) / 1.2, 1.0)
                xb = 0.05 + 1.9 * frac ** 1.5
            well.set_data(x, U(x, depth))
            ball.set_data([xb], [U(xb, depth) + 0.18])
            if tk - 0.4 <= age < tk + 0.9:
                kick_arrow.xy = (0.9, U(0.9, depth) + 0.6); kick_arrow.set_position((-0.4, U(0, depth) + 1.3))
                kick_arrow.set_visible(True)
                kick_txt.set_position((0.9, U(0.9, depth) + 0.8)); kick_txt.set_text("directed kick at a pause point")
            else:
                kick_arrow.set_visible(False); kick_txt.set_text("")
            m = tt <= min(age, tk)
            hline.set_data(tt[m], h_age[m])
            kh_txt.set_text("kick: odds ×1.54 (G51)" if age >= tk else "")
            hk = 0.45 * tk ** -0.77
            hdot.set_data([age], [0.45 * max(age, 0.3) ** -0.77]) if age > 0.3 and age < tk else hdot.set_data([], [])
            kdot.set_data([tk, tk], [hk, hk * OR_KICK]) if age >= tk else kdot.set_data([], [])
            depth_txt.set_text(f"trap depth grows with age  ·  age {age:4.1f}")
            counter.set_text(f"t {t:4.1f} s")
        else:
            age = t - T1
            depth = 0.8 + 1.6 * (1 - np.exp(-age / 2.5))
            xb = 0.06 * jitter[f] / np.sqrt(depth)
            well.set_data(x, U(x, depth)); ball.set_data([xb], [U(xb, depth) + 0.18])
            kick_arrow.set_visible(False)
            kick_txt.set_position((0, 1.2)); kick_txt.set_text("")
            depth_txt.set_text(f"new trap: shallow again  ·  age {age:4.1f}")
            m = tt <= age
            hline.set_data(tt[m], h_age[m]); kdot.set_data([], []); kh_txt.set_text("")
            hdot.set_data([age], [0.45 * max(age, 0.3) ** -0.77]) if age > 0.3 else hdot.set_data([], [])
            counter.set_text(f"t {t:4.1f} s")
        return well, ball, hline, hdot, kdot, kick_txt, depth_txt, counter, kh_txt

    a = animation.FuncAnimation(fig, draw, frames=nF, interval=1000 / fps)
    a._save_count = nF
    vs.save_anim(a, HERE / "anim", fps=fps, dpi=160, poster_frame=int((tk + 0.3) * fps))
    plt.close(fig)
    print("anim frames", nF, "duration", nF / fps)


if __name__ == "__main__":
    static()
    if "--no-anim" not in sys.argv:
        anim()
