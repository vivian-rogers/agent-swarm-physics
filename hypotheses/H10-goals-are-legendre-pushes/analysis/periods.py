"""H10 per-period descriptives (G folders): F1 single well, F2 loop gain, F3 stationarity (free weeks, along the next
week's g); A1 push exists, A2 stationarity and day-1 transient, A3 loop gain (assigned weeks, along their own g).

Outputs data/processed/H10-goals-are-legendre-pushes/G<NN>/period.json and G<NN>/figures/*.pdf.
Usage: uv run python periods.py [--boot 500]
"""
from __future__ import annotations

import argparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import h10data  # noqa: E402
from h10data import DATA, HERE, PAIRS, goal_direction, load_period, save_json, segment  # noqa: E402
from h10lib import agent_stats, day_weights, random_transverse, swarm_stats  # noqa: E402

HYP = HERE.parent
FREE = {11: ("12", 12, "I"), 16: ("17", 17, "I"), 37: ("38", 38, "III")}
ASSIGNED = {12: ("11-12", "I"), 17: ("16-17", "I"), 38: ("37-38", "III")}


def gmm_bic(x, k, iters=200, seed=0):
    """1-D Gaussian mixture by EM; returns BIC."""
    x = np.asarray(x, float)
    n = len(x)
    rng = np.random.default_rng(seed)
    if k == 1:
        s2 = x.var()
        ll = -0.5 * n * (np.log(2 * np.pi * s2) + 1)
        return -2 * ll + 2 * np.log(n)
    mu = np.quantile(x, [0.25, 0.75]) + 1e-6 * rng.standard_normal(2)
    s2 = np.full(2, x.var()); pi = np.full(2, 0.5)
    for _ in range(iters):
        p = pi * np.exp(-0.5 * (x[:, None] - mu) ** 2 / s2) / np.sqrt(2 * np.pi * s2)
        tot = p.sum(1, keepdims=True) + 1e-300
        r = p / tot
        nk = r.sum(0) + 1e-12
        pi = nk / n; mu = (r * x[:, None]).sum(0) / nk
        s2 = np.clip((r * (x[:, None] - mu) ** 2).sum(0) / nk, 1e-4 * x.var(), None)
    ll = np.log(tot).sum()
    return -2 * ll + 5 * np.log(n)


def daily_means(seg, st_agents):
    """Mean over agents of each agent's daily mean alignment (direction 0)."""
    x = (seg.S1 @ seg.U[:, 0]) / seg.c
    out = {}
    for d in np.unique(seg.day):
        vals = [x[(seg.day == d) & (seg.agent == a)].mean() for a in st_agents if ((seg.day == d) & (seg.agent == a)).any()]
        out[int(d)] = (float(np.mean(vals)), len(vals))
    return out


def trend_ci(seg, agents, rng, n_boot=500):
    """OLS slope of the daily mean alignment on day index; CI by resampling agents."""
    x = (seg.S1 @ seg.U[:, 0]) / seg.c
    days = np.unique(seg.day)
    M = np.full((len(agents), len(days)), np.nan)
    for i, a in enumerate(agents):
        for j, d in enumerate(days):
            s = (seg.agent == a) & (seg.day == d)
            if s.any():
                M[i, j] = x[s].mean()

    def slope(Mb):
        y = np.nanmean(Mb, 0)
        ok = np.isfinite(y)
        return np.polyfit(days[ok], y[ok], 1)[0] if ok.sum() >= 2 else np.nan
    s0 = slope(M)
    bs = [slope(M[rng.integers(0, len(agents), len(agents))]) for _ in range(n_boot)]
    return float(s0), [float(np.nanquantile(bs, 0.05)), float(np.nanquantile(bs, 0.95))]


def describe(seg, rng, n_boot):
    st = agent_stats(seg)
    sw = swarm_stats(seg, st)
    out = {"n_agents": int(len(st.agents)), "n_win": int(len(np.unique(seg.win))), "n_aw": int(len(seg.c)),
           "mu_mean": float(st.mu[:, 0].mean()), "k2_mean": float(st.k2[:, 0].mean()),
           "gamma": float(st.gamma[0]), "eta": float(st.eta[0]),
           "gamma_perp_median": float(np.nanmedian(st.gamma[1:])), "agents": st.agents.tolist()}
    if sw is not None:
        out.update({"g": float(sw["g"][0]), "R": float(sw["R"][0]), "g_perp_median": float(np.nanmedian(sw["g"][1:])),
                    "R_perp_median": float(np.nanmedian(sw["R"][1:]))})
        dm = sw["dm"]
        z = (dm - dm.mean()) / dm.std()
        out["bic1_swarm"], out["bic2_swarm"] = gmm_bic(z, 1), gmm_bic(z, 2)
        gs = []
        for _ in range(n_boot):
            w = day_weights(seg, rng)
            stb = agent_stats(seg, w=w)
            swb = swarm_stats(seg, stb, w=w) if len(stb.agents) >= 2 else None
            gs.append(swb["g"][0] if swb is not None else np.nan)
        out["g_ci90"] = [float(np.nanquantile(gs, 0.05)), float(np.nanquantile(gs, 0.95))]
        # share of swarm fluctuation power on the biggest single day
        dd = np.array([seg.day[seg.win == u][0] for u in np.unique(seg.win)])
        out["n_days"] = int(len(np.unique(seg.day)))
    x = (seg.S1 @ seg.U[:, 0]) / seg.c
    idx = {a: i for i, a in enumerate(st.agents)}
    dev = np.array([(x[j] - st.mu[idx[a], 0]) / np.sqrt(max(st.k2[idx[a], 0] + st.noise[idx[a], 0], 1e-12))
                    for j, a in enumerate(seg.agent) if a in idx])
    out["bic1_agent"], out["bic2_agent"] = gmm_bic(dev, 1), gmm_bic(dev, 2)
    out["F1_unimodal"] = bool(out["bic1_agent"] <= out["bic2_agent"] and out.get("bic1_swarm", 0) <= out.get("bic2_swarm", 1))
    out["F1_skew_ok"] = bool(abs(out["gamma"]) < 1)
    out["dev_std"] = dev.tolist()
    out["slope"], out["slope_ci90"] = trend_ci(seg, st.agents, rng, n_boot)
    out["daily"] = daily_means(seg, st.agents)
    return out


def fig_period(name, res, title, path):
    if h10data.out_root() != DATA:      # round-1b configurations: numbers only, round-1 figures kept
        return
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.8))
    d = res["dev_std"]
    ax[0].hist(d, bins=30, density=True, color="#2a78d6", alpha=0.75)
    xs = np.linspace(-4, 4, 200)
    ax[0].plot(xs, np.exp(-xs ** 2 / 2) / np.sqrt(2 * np.pi), color="k", lw=1)
    ax[0].set_xlabel("standardized agent-window deviation along ĝ")
    ax[0].set_ylabel("density")
    ax[0].set_title(f"{name}: shape (γ = {res['gamma']:.2f})", fontsize=9)
    days = sorted(res["daily"], key=int)
    ax[1].plot([int(k) + 1 for k in days], [res["daily"][k][0] for k in days], "o-", color="#eb6834")
    ax[1].set_xlabel("active day"); ax[1].set_ylabel("mean alignment x along ĝ")
    ax[1].set_title(f"g = {res.get('g', np.nan):.2f} {np.round(res.get('g_ci90', [np.nan, np.nan]), 2).tolist()}", fontsize=9)
    fig.suptitle(title, fontsize=9)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=500)
    # round 1b (2026-10-04): corrected inputs; defaults reproduce round 1
    ap.add_argument("--emb", default="bge_small", choices=["bge_small", "gte_modernbert"])
    ap.add_argument("--goals", default="h10", choices=["h10", "shared"])
    ap.add_argument("--dedupe", default="none", choices=["none", "copies", "restate"])
    ap.add_argument("--style", action="store_true")
    args = ap.parse_args()
    h10data.configure(args.emb, args.goals, args.dedupe, args.style)
    OUTR = h10data.out_root()
    rng = np.random.default_rng(11)
    summary = {}
    for gno, (nxt, gnext, reg) in FREE.items():
        g = goal_direction(gnext, reg)
        U = random_transverse(g, 50, np.random.default_rng(0))
        P = load_period(gno)
        res = describe(segment(P, U), rng, args.boot)
        res["direction"] = f"g_{gnext}"; res["days"] = P["days"]
        save_json(res, OUTR / f"G{gno:02d}" / "period.json")
        fig_period(f"G{gno}", res, f"#{gno} (free) along ĝ of #{gnext}", HYP / "goalperiod-subhypotheses" / f"G{gno:02d}" / "figures" / "shape_and_drift.pdf")
        summary[f"G{gno}"] = {k: res.get(k) for k in ("n_agents", "n_win", "gamma", "eta", "F1_unimodal", "g", "g_ci90",
                                                       "g_perp_median", "slope", "slope_ci90", "mu_mean", "k2_mean")}
        print(f"G{gno}", summary[f"G{gno}"], flush=True)
    # #31 (31a): along g_12 and g_17 (never g_32)
    P = load_period(31)
    for gnext in (12, 17):
        g = goal_direction(gnext, "I")
        U = random_transverse(g, 50, np.random.default_rng(0))
        res = describe(segment(P, U), rng, args.boot)
        res["direction"] = f"g_{gnext}"; res["days"] = P["days"]
        save_json(res, OUTR / "G31" / f"period_g{gnext}.json")
        if gnext == 12:
            fig_period("G31", res, "#31a (free) along ĝ of #12 (not #32: held out)", HYP / "goalperiod-subhypotheses" / "G31" / "figures" / "shape_and_drift.pdf")
        summary[f"G31:g{gnext}"] = {k: res.get(k) for k in ("n_agents", "n_win", "gamma", "eta", "F1_unimodal", "g", "g_ci90",
                                                            "g_perp_median", "R_perp_median", "slope", "slope_ci90")}
        print(f"G31 g{gnext}", summary[f"G31:g{gnext}"], flush=True)
    for gno, (key, reg) in ASSIGNED.items():
        g = goal_direction(gno, reg)
        U = random_transverse(g, 50, np.random.default_rng(0))
        Pall = load_period(gno)                 # whole first unit incl. day 1
        res = describe(segment(Pall, U), rng, args.boot)
        d1 = res["daily"].get(0, (np.nan, 0))[0]
        rest = [v[0] for k, v in res["daily"].items() if int(k) >= 1]
        res["A2_day1_minus_rest"] = float(d1 - np.mean(rest)) if rest else np.nan
        PA = load_period(gno, days=PAIRS[key]["A_days"])
        resA = describe(segment(PA, U), rng, args.boot)
        res["A_segment"] = {k: resA.get(k) for k in ("n_agents", "n_win", "g", "g_ci90", "slope", "slope_ci90", "gamma",
                                                      "F1_unimodal", "mu_mean")}
        PF = load_period(PAIRS[key]["F"])
        resF = describe(segment(PF, U), rng, 0)
        res["A1_free_mean"] = resF["mu_mean"]
        res["A1_all_days_above"] = bool(all(v[0] > resF["mu_mean"] for k, v in res["daily"].items() if int(k) >= 1))
        res["days"] = Pall["days"]
        save_json(res, OUTR / f"G{gno:02d}" / "period.json")
        fig_period(f"G{gno}", res, f"#{gno} (assigned) along its own ĝ; day 1 = kickoff day", HYP / "goalperiod-subhypotheses" / f"G{gno:02d}" / "figures" / "shape_and_drift.pdf")
        summary[f"G{gno}"] = {"A1_all_days_above": res["A1_all_days_above"], "A1_free_mean": res["A1_free_mean"],
                              "daily": res["daily"], "A2_day1_minus_rest": res["A2_day1_minus_rest"],
                              "A_segment": res["A_segment"], "g_unit": res.get("g"), "gamma_unit": res["gamma"]}
        print(f"G{gno}", summary[f"G{gno}"], flush=True)
    save_json(summary, OUTR / "periods_summary.json")


if __name__ == "__main__":
    main()
