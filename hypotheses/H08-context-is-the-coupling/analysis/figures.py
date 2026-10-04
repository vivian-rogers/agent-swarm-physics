"""H08 figures (static PDFs for the card, period folders and the summary page).

  uv run python hypotheses/H08-context-is-the-coupling/analysis/figures.py

Palette: the dataviz reference categorical order (blue, orange, aqua, ...), 2 px lines, hairline recessive axes, text
in ink colors. Reads only the JSON outputs in data/processed/H08-context-is-the-coupling/.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h08lib import *  # noqa: E402,F403

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4",
                                                           "#008300", "#4a3aa7", "#e34948")
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#85847e", "#e4e2dc"
L0 = 30
plt.rcParams.update({"font.size": 7, "axes.edgecolor": GRID, "axes.linewidth": 0.6, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
                     "axes.titlesize": 7.5, "axes.titlecolor": INK, "legend.frameon": False, "font.family": "sans-serif",
                     "pdf.fonttype": 42})
ALL = [24, 25, 26, 27, 30, 31, 33, 35, 36, 37, 38, 39, 40, 41, 42, 44, 51]


def load(p):
    p = OUT / p
    return json.loads(p.read_text()) if p.exists() else None


def style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color=GRID, lw=0.5)
    ax.set_axisbelow(True)


def c9_curve(d, key, kind):
    s = d.get(key, {})
    if kind not in s:
        return None
    return np.array([s[kind]["G"][str(o)][0] for o in range(-2, 4)]), np.array([s[kind]["G"][str(o)][1:] for o in range(-2, 4)])


def fig_summary():
    fig, axs = plt.subplots(1, 2, figsize=(6.6, 2.35), dpi=150)
    ax = axs[0]
    offs = np.arange(-2, 4)
    r3, r1 = [], []
    for g in ALL:
        d = load(f"{gname(g)}/c9.json")
        if not d:
            continue
        c = c9_curve(d, "posthoc_clean", "addr")
        if c is None:
            continue
        y = 100 * c[0]
        (r3 if PERIODS[g]["regime"] in ("III", "II/III") else r1).append(y)
        ax.plot(offs, y, color=BLUE if PERIODS[g]["regime"] in ("III", "II/III") else ORANGE, lw=0.7, alpha=0.45)
    ax.plot(offs, np.median(r3, 0), color=BLUE, lw=2, marker="o", ms=3.5, mec="white", mew=0.8,
            label=f"regime III (n = {len(r3)} periods)")
    ax.plot(offs, np.median(r1, 0), color=ORANGE, lw=2, marker="o", ms=3.5, mec="white", mew=0.8,
            label=f"regimes I–II (n = {len(r1)})")
    ax.axvspan(-2.4, 0.5, color="#f1f0ec", lw=0, zorder=0)
    ax.text(-0.95, ax.get_ylim()[1] * 0.95, "turn's model call began\nbefore the message", ha="center",
            va="top", fontsize=6, color=MUTED)
    ax.axhline(0, color=INK2, lw=0.6)
    ax.set_xticks(offs); ax.set_xticklabels(["−2", "−1", "0", "1", "2", "3"])
    ax.set_xlabel("recipient's turn offset (0 = in flight, 1 = read-out)")
    ax.set_xlim(-2.4, 3.4)
    ax.set_ylabel("excess P(turn addresses sender), pp")
    ax.set_title("(a) agent → agent: response gated by read-out", loc="left")
    ax.legend(loc="upper right", fontsize=6)
    style(ax)
    ax = axs[1]
    d = load("G51/c8.json")
    s = d["sets"]["nudge_target_iso"]
    G = np.array(s["G"], float); lo = np.array(s["G_lo"], float); hi = np.array(s["G_hi"], float)
    tau = np.arange(-30, 61)
    m = (tau >= -10) & (tau <= 45)
    ax.fill_between(tau[m], lo[m], hi[m], color=BLUE, alpha=0.12, lw=0)
    ax.plot(tau[m], G[m], color=BLUE, lw=2, label="measured (H04 design, 303 nudges)")
    fit = s["fit"]
    tt = np.arange(1, 46)
    ax.plot(tt, fit["ctx"]["curve"], color=ORANGE, lw=2, label="read-out prediction (A fitted)")
    ax.plot(tt, fit["delay"]["curve"], color=AQUA, lw=1.4, ls=(0, (3, 1.5)),
            label=f"constant delay d = {int(fit['delay']['params']['d'])} min")
    ax.axhline(0, color=INK2, lw=0.6); ax.axvline(0, color=MUTED, lw=0.6)
    med = s["readout"]["W_obs_s_q"][2] / 60
    ax.annotate(f"median read-out\n{med:.1f} min", xy=(med, 0), xytext=(8, -0.11), fontsize=6, color=INK2,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    ax.set_xlabel("minutes after nudge"); ax.set_ylabel("excess P(active) per minute")
    ax.set_title("(b) nudge → target, #51: onset lags read-out", loc="left")
    ax.legend(loc="upper left", fontsize=6)
    ax.set_ylim(-0.2, 0.25)
    style(ax)
    fig.tight_layout(pad=0.4, w_pad=1.2)
    fig.savefig(FIG / "summary_obs.pdf")
    plt.close(fig)


def fig_c9_grid():
    fig, axs = plt.subplots(3, 6, figsize=(9.5, 4.8), dpi=150, sharex=True)
    offs = np.arange(-2, 4)
    for ax, g in zip(axs.ravel(), ALL):
        d = load(f"{gname(g)}/c9.json")
        for key, col, lab in (("primary", INK2, "all in-flight"), ("posthoc_clean", BLUE, "recipient not just talked")):
            c = c9_curve(d, key, "addr")
            if c is None:
                continue
            ax.plot(offs, 100 * c[0], color=col, lw=1.4, marker="o", ms=2.5, label=lab)
            ax.fill_between(offs, 100 * c[1][:, 0], 100 * c[1][:, 1], color=col, alpha=0.12, lw=0)
        o = d.get("other_room", {})
        if "addr" in o:
            c = c9_curve(d, "other_room", "addr")
            ax.plot(offs, 100 * c[0], color=ORANGE, lw=1, ls=(0, (2, 1)), label="other room")
        ax.axhline(0, color=MUTED, lw=0.5); ax.axvline(0.5, color=GRID, lw=0.8)
        ax.set_title(f"{gname(g)} ({PERIODS[g]['regime']})", loc="left", fontsize=6.5)
        style(ax)
    axs.ravel()[-1].axis("off")
    axs[0, 0].legend(fontsize=5, loc="upper left")
    for ax in axs[-1]:
        ax.set_xticks(offs)
    fig.supxlabel("turn offset o (1 = first turn whose call started after the message)", fontsize=7, color=INK2)
    fig.supylabel("excess P(turn addresses sender), pp", fontsize=7, color=INK2)
    fig.tight_layout(pad=0.4)
    fig.savefig(FIG / "c9_offsets.pdf")
    plt.close(fig)


def fig_period_c9(g):
    d = load(f"{gname(g)}/c9.json")
    if not d:
        return
    fig, axs = plt.subplots(1, 2, figsize=(5.0, 1.9), dpi=150)
    offs = np.arange(-2, 4)
    for ax, kind in zip(axs, ("talk", "addr")):
        for key, col, lab in (("primary", INK2, "all in-flight"), ("posthoc_clean", BLUE, "recipient not just talked")):
            c = c9_curve(d, key, kind)
            if c is None:
                continue
            ax.plot(offs, 100 * c[0], color=col, lw=1.4, marker="o", ms=2.5, label=lab)
            ax.fill_between(offs, 100 * c[1][:, 0], 100 * c[1][:, 1], color=col, alpha=0.12, lw=0)
        if "other_room" in d and kind in d["other_room"]:
            c = c9_curve(d, "other_room", kind)
            ax.plot(offs, 100 * c[0], color=ORANGE, lw=1, ls=(0, (2, 1)), label="other room")
        ax.axhline(0, color=MUTED, lw=0.5); ax.axvline(0.5, color=GRID, lw=0.8)
        ax.set_title(f"{gname(g)}: excess P({'talk' if kind == 'talk' else 'addresses sender'}), pp", loc="left")
        ax.set_xticks(offs); ax.set_xlabel("turn offset (1 = read-out)")
        style(ax)
    axs[1].legend(fontsize=5)
    fig.tight_layout(pad=0.3)
    out = GP / gname(g) / "figures"
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / "c9_offsets.pdf")
    plt.close(fig)


def fig_c8():
    fig, axs = plt.subplots(1, 3, figsize=(8.6, 2.4), dpi=150)
    tau = np.arange(-30, 61); m = (tau >= -15) & (tau <= 45)
    d = load("G51/c8.json"); s = d["sets"]["nudge_target_iso"]
    ax = axs[0]
    for k, col, lab in (("F_hr", ORANGE, "F_hr (headroom-weighted)"), ("F_step", AQUA, "F step (read-out CDF)"),
                        ("F_hr_ren", VIOLET, "F_hr renewal")):
        ax.plot(tau[L0 + 1:L0 + 46], np.array(s[k])[L0 + 1:L0 + 46], color=col, lw=1.6, label=lab)
    ax.set_title("(a) #51 zero-parameter predictions", loc="left"); ax.set_xlabel("minutes after nudge")
    ax.legend(fontsize=5.5); style(ax)
    ax = axs[1]
    p = load("c8_pooled.json")["regime3_all"]
    G = np.array(p["G"]); lo = np.array(p["G_lo"]); hi = np.array(p["G_hi"])
    ax.fill_between(tau[m], lo[m], hi[m], color=BLUE, alpha=0.12, lw=0)
    ax.plot(tau[m], G[m], color=BLUE, lw=1.8, label=f"pooled regime III ({p['n_cells']} cells)")
    h4 = np.array(p["h04_published"]["G"], float)
    ax.plot(tau[m], h4[m], color=INK2, lw=1, ls=(0, (2, 1)), label="H04 published (regime III)")
    ax.plot(np.arange(1, 46), p["fit"]["ctx"]["curve"], color=ORANGE, lw=1.6, label="read-out prediction")
    ax.axhline(0, color=MUTED, lw=0.5); ax.axvline(0, color=MUTED, lw=0.5)
    ax.set_title("(b) pooled nudge kernel", loc="left"); ax.set_xlabel("minutes after nudge"); ax.legend(fontsize=5.5)
    style(ax)
    ax = axs[2]
    pm = d.get("pause_matched", {})
    for k, col, lab in (("paused_ge5min", VIOLET, "paused, ≥ 5 min left"), ("not_paused", AQUA, "not paused")):
        if "G" in pm.get(k, {}):
            g_ = np.array(pm[k]["G"], float)
            ax.plot(tau[m], np.convolve(np.nan_to_num(g_), np.ones(3) / 3, "same")[m], color=col, lw=1.6,
                    label=f"{lab} (n = {pm[k]['n_cells']})")
    ax.axhline(0, color=MUTED, lw=0.5); ax.axvline(0, color=MUTED, lw=0.5)
    ax.set_title("(c) #51 pause-matched, 3-min smoothed", loc="left"); ax.set_xlabel("minutes after nudge")
    ax.legend(fontsize=5.5); style(ax)
    fig.tight_layout(pad=0.4)
    fig.savefig(FIG / "c8_kernels.pdf")
    plt.close(fig)


def fig_c1():
    d = load("cc/c1.json")
    fe = pl.read_parquet(OUT / "cc/cc_fetches.parquet").with_columns(
        pl.col("t_result").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8).alias("d"))
    se = pl.read_parquet(OUT / "cc/cc_seen.parquet").join(fe.select("fetch_id", "d", "t_result"), on="fetch_id")
    se = se.with_columns(((pl.col("t_result") - pl.col("t_event_api").dt.cast_time_unit("us")).dt.total_seconds() > 86400).alias("replay"))
    byd = se.group_by("d").agg(pl.col("replay").mean().alias("replay"), pl.len().alias("n")).sort("d")
    fig, axs = plt.subplots(1, 2, figsize=(6.6, 2.2), dpi=150)
    ax = axs[0]
    x = np.arange(byd.height)
    ax.bar(x, byd["replay"].to_numpy(), width=0.7, color=ORANGE)
    ax.set_xticks(x[::2]); ax.set_xticklabels([s[5:] for s in byd["d"].to_list()][::2], rotation=90, fontsize=5)
    ax.set_ylabel("share of fetched events > 1 day old")
    ax.set_title("(a) Claude Code agent: history replay from 03-17", loc="left"); style(ax)
    ax = axs[1]
    gs = [g for g in d["periods"] if d["periods"][g].get("n_fetches")]
    xx = np.arange(len(gs))
    ax.bar(xx - 0.17, [d["periods"][g]["recall"] for g in gs], width=0.3, color=BLUE, label="recall (seen events predicted)")
    ax.bar(xx + 0.17, [d["periods"][g]["precision"] for g in gs], width=0.3, color=AQUA, label="precision (predicted events seen)")
    ax.set_xticks(xx); ax.set_xticklabels(gs); ax.axhline(0.9, color=MUTED, lw=0.6, ls=(0, (2, 1)))
    ax.set_title("(b) room rule vs logged fetches", loc="left"); ax.legend(fontsize=5.5, loc="upper right"); style(ax)
    fig.tight_layout(pad=0.4)
    fig.savefig(FIG / "c1_cc.pdf")
    plt.close(fig)


def fig_ne41():
    d = load("ne41_pooled.json")
    gs = list(d["periods"].keys())
    fig, ax = plt.subplots(figsize=(4.4, 2.3), dpi=150)
    for j, (key, col, lab) in enumerate((("erased_F", BLUE, "forced (41-turn cap)"), ("erased_V", ORANGE, "voluntary"))):
        for i, g in enumerate(gs):
            b = d["periods"][g].get("beta", {}).get(key)
            if not b:
                continue
            y = i + (j - 0.5) * 0.25
            ax.plot([100 * b[1], 100 * b[2]], [y, y], color=col, lw=1.4)
            ax.plot(100 * b[0], y, "o", color=col, ms=3.5, mec="white", mew=0.6, label=lab if i == 0 else None)
        pz = d["pooled"].get(key)
        if pz:
            y = len(gs) + (j - 0.5) * 0.25
            ax.plot([100 * (pz["mu"] - 1.96 * pz["se"]), 100 * (pz["mu"] + 1.96 * pz["se"])], [y, y], color=col, lw=2.2)
            ax.plot(100 * pz["mu"], y, "D", color=col, ms=4, mec="white", mew=0.6)
    ax.axvline(0, color=INK2, lw=0.6)
    ax.set_yticks(list(range(len(gs))) + [len(gs)]); ax.set_yticklabels(gs + ["pooled (RE)"])
    ax.set_xlabel("change in P(address old sender) after erasure, pp")
    ax.set_title("NE41: erasure cuts coupling to what was in context", loc="left"); ax.legend(fontsize=5.5, loc="lower left")
    style(ax); ax.grid(axis="x", color=GRID, lw=0.5)
    fig.tight_layout(pad=0.4)
    fig.savefig(FIG / "ne41.pdf"); fig.savefig(GP / "NE41" / "figures" / "ne41.pdf")
    plt.close(fig)


def fig_c2_c10():
    fig, axs = plt.subplots(1, 2, figsize=(6.6, 2.2), dpi=150)
    gs = [36, 37, 38, 39, 40, 41, 42, 44, 51]
    ax = axs[0]
    for j, (key, col, lab) in enumerate((("slope_b", INK2, "raw"), ("posthoc_slope_b_prevaction", BLUE, "previous action controlled (post hoc)"))):
        for i, g in enumerate(gs):
            d = load(f"{gname(g)}/c2.json")
            if not d or key not in d:
                continue
            b = d[key]; y = i + (j - 0.5) * 0.3
            ax.plot([b[1], b[2]], [y, y], color=col, lw=1.4); ax.plot(b[0], y, "o", color=col, ms=3.5, mec="white", mew=0.6,
                                                                   label=lab if i == 0 else None)
    ax.axvline(0, color=MUTED, lw=0.6); ax.set_yticks(range(len(gs))); ax.set_yticklabels([gname(g) for g in gs])
    ax.set_xlabel("elasticity of uncached tokens to new messages")
    ax.set_title("(a) C2 inflow", loc="left"); ax.legend(fontsize=5.5, loc="lower right"); style(ax)
    ax = axs[1]
    gs2 = [37, 38, 39, 40, 41, 42, 44, 51]
    for i, g in enumerate(gs2):
        d = load(f"{gname(g)}/c10.json")
        if not d:
            continue
        b = d["slope_logk_per_hour"]
        ax.plot([100 * b[1], 100 * b[2]], [i, i], color=BLUE, lw=1.4); ax.plot(100 * b[0], i, "o", color=BLUE, ms=3.5, mec="white", mew=0.6)
    ax.axvline(0, color=MUTED, lw=0.6); ax.set_yticks(range(len(gs2))); ax.set_yticklabels([gname(g) for g in gs2])
    ax.set_xlabel("% change in backlog k per session hour")
    ax.set_title("(b) C10 backlog vs session hour", loc="left"); style(ax)
    fig.tight_layout(pad=0.4)
    fig.savefig(FIG / "c2_c10.pdf")
    plt.close(fig)


def fig_summary_split():
    """Page-1 figure (C9 gating, column width) and page-2 figure (#51 kernel vs prediction; NE41 forest)."""
    plt.rcParams.update({"font.size": 6})
    fig, ax = plt.subplots(figsize=(3.45, 1.7), dpi=200)
    offs = np.arange(-2, 4)
    r3, r1 = [], []
    for g in ALL:
        d = load(f"{gname(g)}/c9.json")
        c = c9_curve(d, "posthoc_clean", "addr") if d else None
        if c is None:
            continue
        reg3 = PERIODS[g]["regime"] in ("III", "II/III")
        (r3 if reg3 else r1).append(100 * c[0])
        ax.plot(offs, 100 * c[0], color=BLUE if reg3 else ORANGE, lw=0.5, alpha=0.4)
    ax.plot(offs, np.median(r3, 0), color=BLUE, lw=1.8, marker="o", ms=3, mec="white", mew=0.6, label=f"regime III ({len(r3)} periods)")
    ax.plot(offs, np.median(r1, 0), color=ORANGE, lw=1.8, marker="o", ms=3, mec="white", mew=0.6, label=f"regimes I–II ({len(r1)})")
    ax.axvspan(-2.4, 0.5, color="#f1f0ec", lw=0, zorder=0)
    ax.text(-0.95, 2.45, "model call began\nbefore the message", ha="center", va="top", fontsize=5.5, color=MUTED)
    ax.axhline(0, color=INK2, lw=0.5)
    ax.set_xticks(offs); ax.set_xlim(-2.4, 3.4); ax.set_ylim(-0.3, 2.6)
    ax.set_xlabel("recipient's turn offset (0 = in flight, 1 = first call after the message)")
    ax.set_ylabel("excess P(addresses sender), pp")
    ax.legend(loc="upper right", fontsize=5.5)
    style(ax)
    fig.tight_layout(pad=0.3)
    fig.savefig(FIG / "summary_obs.pdf")
    plt.close(fig)
    fig, axs = plt.subplots(1, 2, figsize=(3.45, 1.95), dpi=200, gridspec_kw={"width_ratios": [1.25, 1]})
    ax = axs[0]
    d = load("G51/c8.json"); s = d["sets"]["nudge_target_iso"]
    G = np.array(s["G"], float); lo = np.array(s["G_lo"], float); hi = np.array(s["G_hi"], float)
    tau = np.arange(-30, 61); m = (tau >= -5) & (tau <= 30)
    ax.fill_between(tau[m], lo[m], hi[m], color=BLUE, alpha=0.12, lw=0)
    ax.plot(tau[m], G[m], color=BLUE, lw=1.4, label="measured")
    ax.plot(np.arange(1, 31), s["fit"]["ctx"]["curve"][:30], color=ORANGE, lw=1.4, label="read-out pred.")
    ax.plot(np.arange(1, 31), s["fit"]["delay"]["curve"][:30], color=AQUA, lw=1.1, ls=(0, (3, 1.5)), label="5-min delay")
    ax.axhline(0, color=INK2, lw=0.5); ax.axvline(0, color=MUTED, lw=0.5)
    ax.set_ylim(-0.15, 0.22); ax.set_xlabel("min after nudge"); ax.set_ylabel("excess P(active)")
    ax.set_title("(a) #51 nudge → target", loc="left", fontsize=6.2)
    ax.legend(loc="upper left", fontsize=5, handlelength=1.4)
    style(ax)
    ax = axs[1]
    n41 = load("ne41_pooled.json")
    gs = list(n41["periods"].keys())
    for i, g in enumerate(gs):
        b = n41["periods"][g].get("beta", {}).get("erased_F")
        if b:
            ax.plot([100 * b[1], 100 * b[2]], [i, i], color=BLUE, lw=1.1)
            ax.plot(100 * b[0], i, "o", color=BLUE, ms=2.6, mec="white", mew=0.4)
    pz = n41["pooled"]["erased_F"]
    ax.plot([100 * (pz["mu"] - 1.96 * pz["se"]), 100 * (pz["mu"] + 1.96 * pz["se"])], [len(gs), len(gs)], color=INK, lw=1.8)
    ax.plot(100 * pz["mu"], len(gs), "D", color=INK, ms=3)
    ax.axvline(0, color=INK2, lw=0.5)
    ax.set_yticks(list(range(len(gs))) + [len(gs)]); ax.set_yticklabels([g.replace("G", "#") for g in gs] + ["pooled"], fontsize=5)
    ax.set_xlabel("Δ P(address old sender), pp"); ax.set_xlim(-14, 7)
    ax.set_title("(b) NE41 forced erasure", loc="left", fontsize=6.2)
    style(ax); ax.grid(axis="x", color=GRID, lw=0.4)
    fig.tight_layout(pad=0.3, w_pad=0.6)
    fig.savefig(FIG / "summary_obs2.pdf")
    plt.close(fig)
    plt.rcParams.update({"font.size": 7})


def main():
    FIG.mkdir(exist_ok=True)
    fig_summary(); fig_c9_grid(); fig_c8(); fig_c1(); fig_ne41(); fig_c2_c10()
    import shutil
    shutil.copy(FIG / "summary_obs.pdf", FIG / "overview_two_panel.pdf")
    fig_summary_split()
    for g in ALL:
        fig_period_c9(g)
    print("figures written")


if __name__ == "__main__":
    main()
