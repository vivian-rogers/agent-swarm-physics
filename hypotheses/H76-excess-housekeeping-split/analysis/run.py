"""H76 exploratory round 1: replication (G51, G38, G40) and natives (NE43 in G51; NE41 forced erasures in G51, G38).

  uv run python hypotheses/H76-excess-housekeeping-split/analysis/run.py
Writes data/processed/H76-excess-housekeeping-split/<unit>/results*.json, results/summary.json, per-period estimates
and figures/.
"""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h76lib as L  # noqa: E402
import h76run as RN  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
import estimates as EST  # noqa: E402
from common import holdout_mask  # noqa: E402

PERIODS = {51: "2026-07-06", 38: "2026-04-02", 40: "2026-05-04"}
H14_V3 = {51: 0.0118, 38: 0.0069, 40: 0.0026}
NBOOT = 100


def replicate(g: int, kd: str, rng):
    out = {}
    cache = {}
    for space in ("coarse", "fine"):
        days = L.load_v3(g, space)
        bl = RN.build_blocks(days, kd, rng, R=20)
        s = RN.stats(bl, days, kd)
        s["edge_time_share"] = RN.edge_time_share(days, kd)
        s["n_agents_day_median"] = float(np.median([len(d["agents"]) for d in days.values()]))
        s["n_days_total"] = len(days)
        if space == "coarse":
            s["boot"] = RN.bootstrap(bl, days, kd, NBOOT, rng)
            # pseudocount sensitivity (alpha 0.5) on the main ratios
            bl5 = RN.build_blocks(days, kd, np.random.default_rng(5), R=10, alpha=0.5)
            s5 = RN.stats(bl5, days, kd)
            s["alpha05"] = {k: s5.get(k) for k in ("edge_share", "trim_rm_ex", "trim_rm_hk", "hk_share", "kick_share", "kick_rank")}
            cache["days"], cache["bl"] = days, bl
        out[space] = s
    return out, cache


def verdict(c, g):
    p2 = c.get("edge_share", np.nan) >= 0.6
    p3 = (c.get("trim_rm_ex", np.nan) >= 0.7) and (c.get("trim_rm_hk", np.nan) <= c.get("trim_rm_steps", 0) + 0.1)
    if g == 40:
        lo, hi = c["boot"]["edge_share"]
        if not (np.isfinite(lo) and (lo >= 0.6 or hi < 0.6)):
            return "n/a", p2, p3
    if p2 and p3:
        return "supported", p2, p3
    if not p2 and not p3:
        return "failed", p2, p3
    return "mixed", p2, p3


def ne43(res51: dict):
    c = res51["coarse"]
    days = c["days"]
    n = np.array(c["n_agents_by_day"], float)
    edge = np.array(c["ex_edge_by_day"]) / n                      # nats per agent per day at the edges (untrimmed)
    hk = np.array(c["hk_day_untrim"]) / np.array(c["steps_day_untrim"])   # housekeeping per agent-step (untrimmed)
    hkt = np.array(c["hk_day_trim"], float) / np.where(np.array(c["steps_day_trim"]) > 0, np.array(c["steps_day_trim"]), np.nan)
    D = np.array([dt.date.fromisoformat(d) for d in days])

    def ratio(b):
        b = dt.date.fromisoformat(b)
        bef = (D >= b - dt.timedelta(days=7)) & (D < b)
        aft = (D >= b) & (D < b + dt.timedelta(days=7))
        if bef.sum() < 2 or aft.sum() < 2:
            return None
        def r(x):
            a_, b_ = np.nanmedian(x[aft]), np.nanmedian(x[bef])
            return float(a_ / b_) if b_ > 0 else float("nan")
        return {"n_before": int(bef.sum()), "n_after": int(aft.sum()), "edge_ratio": r(edge), "hk_ratio": r(hk),
                "hk_trim_ratio": r(hkt), "edge_before": float(np.nanmedian(edge[bef])), "edge_after": float(np.nanmedian(edge[aft])),
                "hk_before": float(np.nanmedian(hk[bef])), "hk_after": float(np.nanmedian(hk[aft]))}
    real = ratio("2026-08-05")
    plac = {b: ratio(b) for b in ("2026-07-13", "2026-07-20", "2026-07-27", "2026-08-12")}
    pe = [v["edge_ratio"] for v in plac.values() if v and np.isfinite(v["edge_ratio"])]
    ph = [v["hk_trim_ratio"] for v in plac.values() if v and np.isfinite(v["hk_trim_ratio"])]
    phu = [v["hk_ratio"] for v in plac.values() if v and np.isfinite(v["hk_ratio"])]
    inside_e = bool(pe) and min(pe) <= real["edge_ratio"] <= max(pe)
    inside_h = bool(ph) and min(ph) <= real["hk_trim_ratio"] <= max(ph)
    v = "supported" if (inside_e and inside_h) else ("failed" if pe and real["edge_ratio"] < min(pe) else "mixed")
    return {"real": real, "placebo": plac, "placebo_edge_range": [min(pe), max(pe)] if pe else None,
            "placebo_hk_range": [min(ph), max(ph)] if ph else None, "inside_edge": bool(inside_e), "inside_hk": bool(inside_h),
            "placebo_hk_untrim_range": [min(phu), max(phu)] if phu else None,
            "inside_hk_untrim": bool(phu) and min(phu) <= real["hk_ratio"] <= max(phu),
            "verdict": v, "hk_measure": "primary: housekeeping per agent-step on the trimmed grid (days with a trimmed window); "
                                         "secondary: untrimmed",
            "edge_per_agent_by_day": dict(zip(days, edge.tolist())), "hk_rate_by_day": dict(zip(days, hk.tolist()))}


def ne41(g: int, rng, space="coarse"):
    days = L.load_v3(g, space)
    t = pl.read_parquet(L.SH / "context_ledger_turns.parquet",
                        columns=["agent", "pt_date", "goal_no", "holdout", "t_call", "reset_forced", "reset_consol", "reset_session"])
    t = t.filter((pl.col("goal_no") == g) & ~pl.col("holdout") & (pl.col("reset_forced") | pl.col("reset_consol") | pl.col("reset_session")))
    hm = holdout_mask(t["pt_date"].to_list(), t["goal_no"].to_list())
    t = t.filter(~pl.Series(hm) & pl.col("pt_date").is_in(list(days)))
    copies, plac = [], []
    for (d, ag), sub in t.group_by(["pt_date", "agent"]):
        day = days[d]
        if ag not in day["agents"]:
            continue
        i = day["agents"].index(ag)
        t0 = np.array([x.timestamp() for x in day["t0"]])
        nw = day["X"].shape[1]
        w_all = np.searchsorted(t0, np.array([x.timestamp() for x in sub["t_call"].to_list()]), side="right") - 1
        forced = sub["reset_forced"].to_numpy()
        allw = np.sort(w_all)
        for w, f in zip(w_all, forced):
            if not f or w < 3 or w > nw - 4:
                continue
            others = allw[np.abs(allw - w) <= 3]
            if (others != w).any() or (others == w).sum() > 1:
                continue
            copies.append((d, i, int(w)))
            far = np.ones(nw, bool)
            for x in allw:
                far[max(0, x - 3):x + 4] = False
            far[:3] = False
            far[nw - 3:] = False
            # amendment A2: placebo windows must have the agent present (labelled) at p-2 .. p+2, like a working agent
            pres = day["X"][i][:, 0] < 0.5
            ok = np.zeros(nw, bool)
            ok[2:nw - 2] = np.all([pres[j:nw - 4 + j] for j in range(5)], axis=0)
            far &= ok
            cand = np.nonzero(far)[0]
            if len(cand):
                plac.append((d, i, int(cand[np.argmin(np.abs(cand - w))])))
    out = {"n_copies": len(copies), "n_placebo": len(plac)}

    def per_copy(lst, k):
        J = np.zeros((len(lst), days[next(iter(days))]["X"].shape[2], days[next(iter(days))]["X"].shape[2]))
        for n, (d, i, w) in enumerate(lst):
            X = days[d]["X"][i]
            J[n] = np.outer(X[w + k], X[w + k + 1])
        return J
    res = {}
    for k in (-2, -1, 0, 1):
        for lab, lst in (("reset", copies), ("placebo", plac)):
            Jp = per_copy(lst, k)
            raw, fl, p95 = L.eval_block(Jp, len(lst), rng, 20)
            res[f"{lab}_{k}"] = {"raw": list(map(float, raw)), "floor": list(map(float, fl)), "db": list(map(float, np.array(raw) - fl)),
                                 "Jper": Jp}
    # statistic: reset steps k = -1 (e-1 -> e) and 0 (e -> e+1)

    def stat(wr, wp):
        er = sum(L.split(np.tensordot(wr, res[f"reset_{k}"]["Jper"], 1), wr.sum())[1] - res[f"reset_{k}"]["floor"][1] for k in (-1, 0))
        ep = sum(L.split(np.tensordot(wp, res[f"placebo_{k}"]["Jper"], 1), wp.sum())[1] - res[f"placebo_{k}"]["floor"][1] for k in (-1, 0))
        hr = sum(L.split(np.tensordot(wr, res[f"reset_{k}"]["Jper"], 1), wr.sum())[2] - res[f"reset_{k}"]["floor"][2] for k in (-1, 0))
        hp = sum(L.split(np.tensordot(wp, res[f"placebo_{k}"]["Jper"], 1), wp.sum())[2] - res[f"placebo_{k}"]["floor"][2] for k in (-1, 0))
        return er, ep, hr, hp
    er, ep, hr, hp = stat(np.ones(len(copies)), np.ones(len(plac)))
    bt = []
    for _ in range(200):
        wr = np.bincount(rng.integers(0, len(copies), len(copies)), minlength=len(copies)).astype(float)
        wp = np.bincount(rng.integers(0, len(plac), len(plac)), minlength=len(plac)).astype(float)
        a, b, c, d = stat(wr, wp)
        bt.append((a / b if b > 0 else np.inf, c / d if d > 0 else np.inf))
    bt = np.where(np.isinf(np.array(bt)), 1e6, np.array(bt))
    out.update(ex_reset=float(er), ex_placebo=float(ep), hk_reset=float(hr), hk_placebo=float(hp),
               ex_ratio=float(er / ep) if ep > 0 else (np.inf if er > 0 else np.nan),
               hk_ratio=float(hr / hp) if hp > 0 else (np.inf if hr > 0 else np.nan),
               ex_ratio_ci=[float(np.nanpercentile(bt[:, 0], 2.5)), float(np.nanpercentile(bt[:, 0], 97.5))],
               hk_ratio_ci=[float(np.nanpercentile(bt[:, 1], 2.5)), float(np.nanpercentile(bt[:, 1], 97.5))],
               by_step={k: {kk: v for kk, v in r.items() if kk != "Jper"} for k, r in res.items()})
    # occupancy shift across the reset (ensemble mean state at e-1, e, e+1, e+2)
    occ = {}
    for k in (-1, 0, 1, 2):
        occ[k] = np.mean([days[d]["X"][i][w + k] for d, i, w in copies], 0).tolist()
    out["occupancy_reset"] = occ
    out["occupancy_placebo"] = {k: np.mean([days[d]["X"][i][w + k] for d, i, w in plac], 0).tolist() for k in (-1, 0, 1, 2)}
    ok_ex = (not np.isnan(out["ex_ratio"])) and out["ex_ratio"] >= 2
    ok_hk = np.isfinite(out["hk_ratio"]) and 0.5 <= out["hk_ratio"] <= 2
    out["pass"] = bool(ok_ex and ok_hk)
    return out


def figures(rep, n43, n41):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fd = L.ROOT / "hypotheses/H76-excess-housekeeping-split/figures"
    fd.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.8))
    cols = {51: "#7a4fbf", 38: "#2a78d6", 40: "#d03b3b"}
    # (a) per-block debiased sigma_ex along the day, G51 untrimmed, mean by block position
    for g in (51, 38):
        b = pl.read_parquet(L.OUTD / f"G{g:02d}" / "blocks_coarse.parquet").filter(pl.col("grid") == "untrimmed")
        b = b.with_columns((pl.col("ex_raw") - pl.col("ex_floor")).alias("ex"), (pl.col("hk_raw") - pl.col("hk_floor")).alias("hk"))
        pos = b.with_columns(pl.col("idx").max().over("day").alias("nmax"))
        pos = pos.with_columns(pl.when(pl.col("kind") == "end").then(99).otherwise(pl.col("idx")).alias("p"))
        agg = pos.group_by("p").agg(pl.col("ex").mean(), pl.col("hk").mean(), pl.len()).sort("p").filter(pl.col("len") >= 5)
        x = agg["p"].to_numpy().astype(float)
        nx = len(x)
        xs = np.where(x == 99, x[x != 99].max() + 1.5 if (x != 99).any() else 1, x) * 0.5
        ax[0].plot(xs, agg["ex"].to_numpy() * 12, "o-", color=cols[g], ms=3, lw=1, label=f"G{g} excess")
        ax[0].plot(xs, agg["hk"].to_numpy() * 12, "s:", color=cols[g], ms=2.5, lw=0.8, alpha=0.7, label=f"G{g} housekeeping")
    ax[0].axhline(0, color="k", lw=0.5)
    ax[0].set_xlabel("hours into the day (30-min blocks; last point = final block)")
    ax[0].set_ylabel("debiased EP (nats / agent-h)")
    ax[0].set_title("(a) excess sits at the day edges", fontsize=8)
    ax[0].legend(fontsize=6, frameon=False)
    # (b) shares per period with CI
    labels, vals, los, his = [], [], [], []
    for g in (51, 38, 40):
        c = rep[g]["coarse"]
        for key, nm in (("edge_share", "edge share σ_ex"), ("trim_rm_ex", "trim removal σ_ex"), ("trim_rm_hk", "trim removal σ_hk"),
                        ("hk_share", "σ_hk/σ (trimmed)")):
            labels.append((g, nm))
            vals.append(c.get(key, np.nan))
            lo, hi = c["boot"].get(key, [np.nan, np.nan])
            los.append(lo)
            his.append(hi)
    keys = ["edge share σ_ex", "trim removal σ_ex", "trim removal σ_hk", "σ_hk/σ (trimmed)"]
    for j, g in enumerate((51, 38, 40)):
        xs = np.arange(4) + (j - 1) * 0.22
        v = np.array([vals[i] for i, (gg, _) in enumerate(labels) if gg == g])
        lo = np.array([los[i] for i, (gg, _) in enumerate(labels) if gg == g])
        hi = np.array([his[i] for i, (gg, _) in enumerate(labels) if gg == g])
        vv = np.clip(v, -0.5, 2.0)
        ax[1].errorbar(xs, vv, yerr=[np.clip(vv - np.clip(lo, -0.5, 2), 0, None), np.clip(np.clip(hi, -0.5, 2) - vv, 0, None)],
                       fmt="o", color=cols[g], ms=4, lw=0.8, label=f"G{g}")
    ax[1].axhline(0.6, color="grey", lw=0.5, ls=":")
    ax[1].axhline(0.7, color="grey", lw=0.5, ls="--")
    ax[1].axhline(0.2, color="grey", lw=0.5, ls="-.")
    ax[1].set_xticks(range(4))
    ax[1].set_xticklabels(keys, fontsize=6.5, rotation=15)
    ax[1].set_ylim(-0.6, 2.1)
    ax[1].set_title("(b) shares with agent-bootstrap 95% CI (clipped)", fontsize=8)
    ax[1].legend(fontsize=6.5, frameon=False)
    fig.tight_layout()
    fig.savefig(fd / "summary_obs.pdf")
    fig.savefig(fd / "summary_obs.png", dpi=150)
    plt.close(fig)
    # synthetic + NE41 figure
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.3))
    sm = pl.read_parquet(L.OUTD / "synthetic/summary.parquet")
    for j, (des, mk) in enumerate((("N25_10x8h", "o"), ("N15_5x4h", "s"))):
        v = sm.filter(pl.col("design") == des)
        ks = ["edge_share", "trim_rm_ex", "hk_share", "kick_share"]
        for i, k in enumerate(ks):
            for jj, scen in enumerate(v["h"].to_list()):
                r = v.filter(pl.col("h") == scen)
                m, s = r[f"{k}_soft"][0], r[f"{k}_soft_sd"][0]
                x = i + (jj - 1) * 0.12 + (j - 0.5) * 0.4
                ax[0].errorbar([x], [np.clip(m, -1, 2.5)], yerr=[[min(s, 3)], [min(s, 3)]], fmt=mk, ms=3, lw=0.6,
                               color=["#888888", "#2a78d6", "#d03b3b"][jj])
                ax[0].plot([x - 0.05, x + 0.05], [r[f"{k}_pop"][0]] * 2, color="k", lw=1.2)
        ax[0].set_xticks(range(4))
        ax[0].set_xticklabels(["edge share", "trim rm σ_ex", "σ_hk/σ", "kickoff share"], fontsize=6.5)
    ax[0].set_ylim(-1, 2.6)
    ax[0].set_title("(a) synthetic: soft-label estimate ± SD; bar = population", fontsize=7)
    for g, c in ((51, "#7a4fbf"), (38, "#2a78d6")):
        r = n41.get(g)
        if not r:
            continue
        ks = [-2, -1, 0, 1]
        ex_r = [r["by_step"][f"reset_{k}"]["db"][1] * 12 for k in ks]
        ex_p = [r["by_step"][f"placebo_{k}"]["db"][1] * 12 for k in ks]
        ax[1].plot(ks, ex_r, "o-", color=c, ms=3, label=f"G{g} forced erasure")
        ax[1].plot(ks, ex_p, "x:", color=c, ms=3, label=f"G{g} placebo")
    ax[1].set_xticks([-2, -1, 0, 1])
    ax[1].set_xticklabels(["e−2→e−1", "e−1→e", "e→e+1", "e+1→e+2"], fontsize=6.5)
    ax[1].set_ylabel("σ_ex (nats / copy-h)", fontsize=7)
    ax[1].set_title("(b) NE41: excess around a forced erasure", fontsize=8)
    ax[1].legend(fontsize=6, frameon=False)
    fig.tight_layout()
    fig.savefig(fd / "synthetic_ne41.pdf")
    fig.savefig(fd / "synthetic_ne41.png", dpi=150)
    plt.close(fig)


def main():
    rng = np.random.default_rng(2026)
    rep = {}
    for g, kd in PERIODS.items():
        r, cache = replicate(g, kd, np.random.default_rng(1000 + g))   # per-period seed (reproducible floors)
        rep[g] = r
        c = r["coarse"]
        v, p2, p3 = verdict(c, g)
        r["verdict"], r["P2"], r["P3"] = v, bool(p2), bool(p3)
        f = r["fine"]
        r["P4"] = {"hk_share_coarse": c.get("hk_share"), "hk_per_step_fine": f.get("hk_per_step"), "h14_v3": H14_V3[g],
                   "ratio_to_h14": f.get("hk_per_step", np.nan) / H14_V3[g]}
        r["P1"] = {"kick_rank": c.get("kick_rank"), "kick_share": c.get("kick_share"),
                   "pass": bool((c.get("kick_rank", 0) >= 1.0) and (c.get("kick_share", 0) >= 0.3))}
        L.write_json(L.OUTD / f"G{g:02d}" / "results.json", r)
        print(g, v, {k: c.get(k) for k in ("kick_share", "kick_rank", "kick_ratio", "decay_tau", "edge_share", "edge_share_day_median",
                                           "trim_rm_ex", "trim_rm_hk", "trim_rm_steps", "hk_share", "hk_per_step",
                                           "ex_per_step_trim", "ex_per_step_untrim", "edge_time_share", "n_days")},
              "boot", c["boot"], "a05", c["alpha05"], "fine", {k: f.get(k) for k in ("edge_share", "trim_rm_ex", "trim_rm_hk", "hk_share", "hk_per_step", "kick_rank", "kick_share")}, flush=True)
    n43 = ne43(rep[51])
    L.write_json(L.OUTD / "NE43" / "results.json", n43)
    print("NE43", n43["real"], n43["placebo_edge_range"], n43["placebo_hk_range"], n43["verdict"], flush=True)
    n41 = {}
    for g in (51, 38):
        n41[g] = ne41(g, np.random.default_rng(4100 + g))
        L.write_json(L.OUTD / "NE41" / f"results_G{g:02d}.json", n41[g])
        print("NE41", g, {k: n41[g][k] for k in ("n_copies", "n_placebo", "ex_reset", "ex_placebo", "ex_ratio", "ex_ratio_ci",
                                                  "hk_reset", "hk_placebo", "hk_ratio", "hk_ratio_ci", "pass")}, flush=True)
    n41_v = "supported" if all(n41[g]["pass"] for g in n41) else ("failed" if not any(n41[g]["pass"] for g in n41) else "mixed")
    summ = {"replication": {g: {"verdict": r["verdict"], "P1": r["P1"], "P2": r["P2"], "P3": r["P3"], "P4": r["P4"],
                                "coarse": {k: v for k, v in r["coarse"].items() if not isinstance(v, list) or k in ("decay_y",)},
                                "coarse_boot": r["coarse"]["boot"], "fine": {k: v for k, v in r["fine"].items() if not isinstance(v, list)}}
                            for g, r in rep.items()},
            "NE43": {k: n43[k] for k in ("real", "placebo", "placebo_edge_range", "placebo_hk_range", "verdict")},
            "NE41": {g: {k: v for k, v in n41[g].items() if k not in ("by_step",)} for g in n41}, "NE41_verdict": n41_v}
    L.write_json(L.OUTD / "results/summary.json", summ)
    figures(rep, n43, n41)
    rows = []
    for g, r in rep.items():
        c = r["coarse"]
        for stat in ("edge_share", "trim_rm_ex", "trim_rm_hk", "trim_rm_steps", "hk_share", "kick_share"):
            v = c.get(stat)
            lo, hi = c["boot"].get(stat, [None, None])
            rows.append(dict(period_unit=f"G{g:02d}", goal_no=g, statistic=f"ep_split_{stat}", channel="behavior_states_v3:coarse5",
                             estimate=v if v is not None and np.isfinite(v) else None, ci_lo=lo, ci_hi=hi, n=c.get("n_days"),
                             method="Kolchinsky excess/housekeeping on ensemble soft fluxes, block-flip debiased, pooled over days",
                             null="block-flip reversible surrogate", role="replication", ci_kind="percentile", n_kind="days"))
        rows.append(dict(period_unit=f"G{g:02d}", goal_no=g, statistic="ep_split_hk_per_step", channel="behavior_states_v3:fine12",
                         estimate=r["fine"].get("hk_per_step"), ci_lo=None, ci_hi=None, n=r["fine"].get("n_days"),
                         method="housekeeping EP per agent-step (nats), trimmed, debiased", null="block-flip reversible surrogate",
                         role="replication", ci_kind="none", n_kind="days"))
    rows.append(dict(period_unit="G51", goal_no=51, statistic="ne43_edge_excess_ratio", channel="behavior_states_v3:coarse5",
                     estimate=n43["real"]["edge_ratio"], ci_lo=(n43["placebo_edge_range"] or [None, None])[0],
                     ci_hi=(n43["placebo_edge_range"] or [None, None])[1],
                     n=n43["real"]["n_before"] + n43["real"]["n_after"], method="after/before median daily edge excess per agent",
                     null="placebo boundary range (min-max)", role="native", ci_kind="none", n_kind="days",
                     notes="ci_lo/ci_hi hold the placebo range, not a CI"))
    for g in n41:
        rows.append(dict(period_unit=f"G{g:02d}", goal_no=g, statistic="ne41_reset_excess_ratio", channel="behavior_states_v3:coarse5",
                         estimate=n41[g]["ex_ratio"] if np.isfinite(n41[g]["ex_ratio"]) else None,
                         ci_lo=n41[g]["ex_ratio_ci"][0] if np.isfinite(n41[g]["ex_ratio_ci"][0]) else None,
                         ci_hi=n41[g]["ex_ratio_ci"][1] if np.isfinite(n41[g]["ex_ratio_ci"][1]) else None,
                         n=n41[g]["n_copies"], method="event-aligned ensemble excess at reset steps vs matched placebo windows",
                         null="placebo windows >= 6 windows from any reset", role="native", ci_kind="percentile", n_kind="events"))
    EST.write_estimates(rows, hypothesis="H76")


if __name__ == "__main__":
    main()
