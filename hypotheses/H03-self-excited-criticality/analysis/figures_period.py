"""Per-goal-period diagnostics figure: hypotheses/H03-self-excited-criticality/G<NN>/figures/diagnostics.pdf
Panels: (a) baseline ladder (real) with this period's synthetic-guard medians; (b) time-rescaling QQ, Hawkes vs
Poisson (TALK); (c) sum-of-exponentials kernel weights; (d) model-free burst CCDF (gap 60 s, TALK);
(e) segments (step-change splits); (f) fast self / cross excitation vs the agent-shift null.
Run: uv run python hypotheses/H03-self-excited-criticality/analysis/figures_period.py [--period G38]
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

from common import DATA, HERE, INK, INK2, fit_path, gdir, hc, load, select_goals, specs  # noqa: E402
from figures import SET_COLORS  # noqa: E402  (also applies the shared rcParams)

RUNGS = [("M1_B0", "B0"), ("M1_B1", "B1"), ("M1_B2", "B2"), ("M1_B2_t30", "B2 τ≤30m"), ("M1_B3_2h", "B3 2h"),
         ("M1_B3", "B3 30m")]


def qq(ax, goal, dm, keys):
    for m, colr, lab in (("M1_B2", "#2a78d6", "Hawkes M1 B2"), ("P_B2", "#eb6834", "Poisson P B2")):
        ds = hc.Dataset(dm, keys, specs()[m])
        f = hc.FitResult(ds, np.load(fit_path(goal, "TALK", m)), np.nan, None)
        z = np.sort(f.rescaled_intervals())
        q = -np.log(1 - (np.arange(1, len(z) + 1) - 0.5) / len(z))
        D, p = hc.ks_exp1(z)
        ax.plot(q, z, color=colr, lw=1.0, label=f"{lab} (KS D={D:.3f})")
    lim = [0, 8]
    ax.plot(lim, lim, color=INK2, lw=0.6, ls=":")
    ax.set_xlim(lim); ax.set_ylim(lim)
    ax.set_xlabel("Exp(1) quantile"); ax.set_ylabel("rescaled interval"); ax.set_title("(b) time-rescaling QQ, TALK")
    ax.legend(fontsize=5.5, loc="upper left")


def main():
    days, ev, exo = load()
    dmT = hc.make_days(ev, exo, days, "TALK")
    fits = pl.read_parquet(DATA / "period_fits.parquet")
    tab = pl.read_parquet(DATA / "period_table.parquet")
    guard = pl.read_parquet(DATA / "synthetic_guard.parquet")
    casc = pl.read_parquet(DATA / "cascades.parquet")
    seg = pl.read_parquet(DATA / "segment_table.parquet")
    jt = pl.read_parquet(DATA / "jitter_table.parquet")
    for goal in select_goals(sorted(days["goal_no"].unique().to_list())):
        keys = days.filter(pl.col("goal_no") == goal).sort("day_id")["day_id"].to_list()
        out = HERE.parent / "goalperiod-subhypotheses" / f"G{goal:02d}" / "figures"
        out.mkdir(parents=True, exist_ok=True)
        fig, axs = plt.subplots(2, 3, figsize=(7.4, 4.8))
        # (a) ladder
        ax = axs[0, 0]
        for s in ("TALK", "ALL"):
            f = fits.filter((pl.col("goal_no") == goal) & (pl.col("set") == s))
            y = [f.filter(pl.col("model") == m)["n"][0] for m, _ in RUNGS]
            ax.plot(range(len(RUNGS)), np.minimum(y, 1.2), marker="o", ms=3, color=SET_COLORS[s], label=s)
            r = tab.filter((pl.col("goal_no") == goal) & (pl.col("set") == s))
            if r["n_boot_lo"][0] is not None:
                ax.plot([2, 2], [r["n_boot_lo"][0], r["n_boot_hi"][0]], color=SET_COLORS[s], lw=2.5, alpha=0.4)
        g0 = guard.filter((pl.col("goal_no") == goal) & (pl.col("scenario") == "n0"))
        g6 = guard.filter((pl.col("goal_no") == goal) & (pl.col("scenario") == "n06"))
        for i, (m, _) in enumerate(RUNGS):
            v = g0.filter(pl.col("model") == m)["n_hat"]
            if len(v):
                ax.scatter([i], [float(v.median())], marker="x", color=INK2, s=12, zorder=4)
            v = g6.filter(pl.col("model") == m)["n_hat"]
            if len(v):
                ax.scatter([i], [float(v.median())], marker="+", color=INK, s=16, zorder=4)
        ax.axhline(0.6, color=INK, lw=0.4, ls=":")
        ax.set_xticks(range(len(RUNGS))); ax.set_xticklabels([l for _, l in RUNGS], rotation=40, ha="right", fontsize=6)
        ax.set_ylim(-0.05, 1.22); ax.set_ylabel("n̂"); ax.set_title("(a) ladder; × n=0 sim, + n=0.6 sim")
        ax.legend(fontsize=6, loc="upper right")
        # (b) QQ
        qq(axs[0, 1], goal, dmT, keys)
        # (c) kernel grid
        ax = axs[0, 2]
        for s in ("TALK", "ALL"):
            g = fits.filter((pl.col("goal_no") == goal) & (pl.col("set") == s) & (pl.col("model") == "M2_grid"))
            w = [g[f"ker_{int(t)}"][0] for t in hc.GRID_TAUS]
            ax.plot(hc.GRID_TAUS, w, marker="o", ms=3, color=SET_COLORS[s], label=s)
            tau = fits.filter((pl.col("goal_no") == goal) & (pl.col("set") == s) & (pl.col("model") == "M1_B2"))["tau_s"][0]
            ax.axvline(min(tau, 3000), color=SET_COLORS[s], lw=0.6, ls="--")
        ax.set_xscale("log"); ax.set_xlabel("τ_m (s)  (dashed: M1 τ̂)"); ax.set_ylabel("α_m")
        ax.set_title("(c) kernel weights (M2)"); ax.legend(fontsize=6)
        # (d) bursts
        ax = axs[1, 0]
        b = casc.filter((pl.col("goal_no") == goal) & (pl.col("set") == "TALK") & (pl.col("gap") == 60.0))
        for src, colr, lab in [("data", INK, "data"), ("sim_hawkes", "#2a78d6", "Hawkes sim"), ("sim_poisson", "#eb6834", "Poisson sim")]:
            x = b.filter(pl.col("source") == src)
            if x.height == 0:
                continue
            sizes = np.repeat(x["size"].to_numpy(), x["count"].to_numpy())
            v = np.sort(np.unique(sizes)); cc = np.array([(sizes >= k).mean() for k in v])
            ax.loglog(v, cc, color=colr, lw=1.0, label=lab)
        ax.set_xlabel("burst size (gap ≤ 60 s)"); ax.set_ylabel("P(S ≥ s)"); ax.set_title("(d) bursts, TALK"); ax.legend(fontsize=6)
        # (e) segments
        ax = axs[1, 1]
        for k, s in enumerate(("TALK", "ALL")):
            x = seg.filter((pl.col("goal_no") == goal) & (pl.col("set") == s)).sort("seg")
            se = x["se"].fill_null(np.nan).to_numpy()
            xx = x["seg"].to_numpy() + (k - 0.5) * 0.15
            ax.errorbar(xx, x["n"], yerr=1.96 * se, fmt="o", ms=3, color=SET_COLORS[s], lw=0.8, label=s)
            if "n_shrunk" in x.columns and x["n_shrunk"].drop_nulls().len():
                ax.scatter(xx, x["n_shrunk"], marker="_", s=40, color=SET_COLORS[s])
        ax.set_xticks(x["seg"].to_list()); ax.set_xticklabels([d[5:] for d in x["first_date"].to_list()], rotation=40, fontsize=6)
        ax.set_ylim(-0.1, 1.3); ax.set_ylabel("n̂ (M1 B2)"); ax.set_title("(e) segments (– = partially pooled)")
        ax.legend(fontsize=6)
        # (f) self / cross vs shift null
        ax = axs[1, 2]
        r = jt.filter(pl.col("goal_no") == goal)
        for k, s in enumerate(("TALK", "ALL")):
            rr = r.filter(pl.col("set") == s)
            if rr.height == 0:
                continue
            t = tab.filter((pl.col("goal_no") == goal) & (pl.col("set") == s))
            vals = [t["n_self_fast"][0], rr["n_cross_fast300_real"][0], rr["n_cross_fast300_shift_mean"][0],
                    rr["t5_real"][0], rr["t5_jit600_mean"][0]]
            ax.bar(np.arange(5) + (k - 0.5) * 0.38, vals, width=0.36, color=SET_COLORS[s], label=s)
        ax.set_xticks(range(5)); ax.set_xticklabels(["self\n≤300s", "cross\n≤300s", "cross\nshift null", "pooled\nτ≤5m", "pooled\njit 10m"], fontsize=6)
        ax.set_title("(f) fast excitation vs surrogates"); ax.legend(fontsize=6)
        fig.suptitle(f"H03 × G{goal:02d}", fontsize=8, fontweight="bold")
        fig.tight_layout()
        fig.savefig(out / "diagnostics.pdf"); plt.close(fig)
    print("done")


if __name__ == "__main__":
    main()
