"""H75 exploratory round 1: replication (G39, G40, G41, G51) and natives (G44 rooms; G51 newcomers + NE38).

  uv run python hypotheses/H75-reallocation-speed-limit/analysis/run.py
Writes data/processed/H75-reallocation-speed-limit/<unit>/results.json, results/summary.json, per-period estimates
(infra/shared/estimates.py) and figures/.
"""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h75lib as L  # noqa: E402
import build as B  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
import estimates as EST  # noqa: E402

RNG = np.random.default_rng(20261004)
H = 20.0
SYN = {"F": -0.53, "A": -0.86}   # synthetic eps means (N 15/25 averaged), amendment A1
NBOOT = 200


def period_result(goal: int, variant: str, Hh: float = H, agents: list | None = None, clk=None, tag=None) -> dict:
    clk = B.clock(goal) if clk is None else clk
    E = B.ensemble(goal, variant, Hh, clk, agents)
    s = L.settle_stats(E)
    bt = L.bootstrap(E, NBOOT, RNG)
    ag = L.agent_settling(E)
    cr = B.call_rates(clk, E.agents, 0.0, Hh)
    ag = ag.with_columns(pl.col("agent").replace_strict(cr, default=np.nan).alias("call_rate"))
    el = L.elasticity(ag)
    elc = {k: el.get(k) for k in ("n", "eps", "se", "eps_ctrl", "se_ctrl")}
    elm = L.elasticity(ag, "t_mid")
    out = {"goal": goal, "variant": variant, "H": Hh, "tag": tag, **{k: v for k, v in s.items() if k != "curve_D"},
           "curve_D": s["curve_D"], "boot": bt, "elasticity": elc, "elasticity_mid": {k: elm.get(k) for k in ("n", "eps", "se")},
           "agents": ag.to_dicts(), "extra": E.extra, "median_call_rate": float(np.nanmedian(list(cr.values()))) if cr else np.nan}
    return out


def verdict(r):
    S, lo = r.get("S_e"), r["boot"]["S_e"][0]
    if r["N"] < 5 or not np.isfinite(S if S is not None else np.nan):
        return "n/a"
    if S >= 3 and lo >= 2:
        return "supported"
    if S <= 2:
        return "failed"
    return "mixed"


def native_g44():
    clk = B.clock(44)
    Htot = float(np.floor(clk.filter(~pl.col("pre"))["len_h"].sum() * 4) / 4)
    gt = pl.read_parquet(L.SH / "ground_truth_labels.parquet").filter(
        (pl.col("goal_no") == 44) & (pl.col("label_kind") == "room_assignment") & pl.col("preferred") & ~pl.col("holdout"))
    rooms = {r: gt.filter(pl.col("value") == r)["agent"].to_list() for r in ("best", "rest")}
    res = {"H": Htot}
    for r, ags in rooms.items():
        res[r] = period_result(44, "null", Htot, ags, clk, tag=f"room_{r}")
    res["all"] = period_result(44, "null", Htot, None, clk, tag="all")
    b, rr = res["best"], res["rest"]
    Tb, Tr = b.get("T_e"), rr.get("T_e")
    Ab, Ar = b.get("A_e"), rr.get("A_e")
    pred_act = Ab / Ar if (Ab and Ar) else np.nan        # activity-limited: T_rest / T_best = A_best / A_rest
    obs = Tr / Tb if (Tb and Tr) else np.nan
    res["T_ratio_rest_best"] = obs
    res["activity_pred_ratio"] = pred_act
    miss = obs / pred_act if (np.isfinite(obs) and np.isfinite(pred_act) and pred_act > 0) else np.nan
    res["miss_factor"] = miss
    ok1 = np.isfinite(Tb) and np.isfinite(Tr) and Tb <= Tr
    ok2 = np.isfinite(miss) and (miss >= 2 or miss <= 0.5 or np.sign(np.log(obs)) != np.sign(np.log(pred_act)))
    res["verdict"] = "supported" if (ok1 and ok2) else ("failed" if not ok1 else "mixed")
    return res


def native_g51_newcomers():
    clk = B.clock(51, pre_days=0)
    a, _ = B.commits_active(clk)
    ros = pl.read_parquet(L.SH / "roster.parquet")
    newc = ros.filter((pl.col("joined") >= "2026-07-09") & (pl.col("joined") <= "2026-09-04"))["agent"].to_list()
    cw = pl.read_parquet(L.SH / "call_windows.parquet", columns=["agent", "pt_date", "goal_no", "holdout", "kind", "t_call"])
    cw = cw.filter((pl.col("goal_no") == 51) & ~pl.col("holdout") & pl.col("agent").is_in(newc + [40])
                   & ~pl.col("kind").cast(pl.String).is_in(list(L.SUMMARY_CALLS)))
    cw = B.to_active(cw, "t_call", clk)
    tmax = float(clk["off_h"].max() + clk.filter(pl.col("off_h") == clk["off_h"].max())["len_h"][0])
    rows = []
    for ag in newc:
        c = cw.filter(pl.col("agent") == ag)
        if c.height == 0:
            continue
        t0 = float(c["ta"].min())
        t1 = min(t0 + 12.0, tmax)
        rows.append(single_agent(a, cw, ag, t0, t1, "newcomer", init=L.NULL))
    # NE38: Claude Opus 5 (agent 40) reassigned 2026-07-29 16:51 UTC
    tr = dt.datetime(2026, 7, 29, 16, 51, tzinfo=dt.timezone.utc)
    trow = B.to_active(pl.DataFrame({"pt_date": ["2026-07-29"], "t": [tr]}), "t", clk)
    t0 = float(trow["ta"][0])
    prev = a.filter((pl.col("agent") == 40) & (pl.col("ta") < t0))
    init_repo = prev["repo"][-1] if prev.height else None
    ne38 = single_agent(a, cw, 40, t0, min(t0 + 12, tmax), "NE38", init_repo=init_repo)
    df = pl.DataFrame(rows)
    ok = df.filter(pl.col("t_i").is_not_null() & pl.col("t_i").is_not_nan())
    el = L.elasticity(ok.with_columns(pl.col("commit_rate")))
    med = float(ok["t_i"].median()) if ok.height else np.nan
    rng_ = (float(ok["t_i"].min()), float(ok["t_i"].max())) if ok.height else (np.nan, np.nan)
    v_eps = el.get("eps") is not None and np.isfinite(el.get("eps", np.nan)) and abs(el["eps"]) <= 0.3
    v_med = np.isfinite(med) and med <= 10
    v_ne38 = np.isfinite(ne38["t_i"]) and rng_[0] <= ne38["t_i"] <= rng_[1]
    verdict = "supported" if (v_eps and v_med and v_ne38) else ("failed" if not (v_eps or v_med or v_ne38) else "mixed")
    return {"newcomers": rows, "ne38": ne38, "elasticity": el, "median_t_i": med, "range_t_i": rng_,
            "checks": {"eps_abs_le_0.3": bool(v_eps), "median_le_10h": bool(v_med), "ne38_in_range": bool(v_ne38)},
            "verdict": verdict}


def single_agent(a, cw, ag, t0, t1, kind, init=L.NULL, init_repo=None):
    p = a.filter((pl.col("agent") == ag) & (pl.col("ta") > t0) & (pl.col("ta") <= t1)).sort("ta")
    reps = p["repo"].to_list()
    out = {"agent": ag, "kind": kind, "t0": t0, "H": t1 - t0, "n_commits": p.height,
           "call_rate": cw.filter((pl.col("agent") == ag) & (pl.col("ta") >= t0) & (pl.col("ta") <= t1)).height / max(t1 - t0, 1e-9),
           "commit_rate": p.height / max(t1 - t0, 1e-9), "t_i": np.nan, "why": "no_commits", "switches": 0, "W": np.nan}
    if not reps:
        return out
    # settled repo = longest occupancy over [t0, t1]
    tt = np.r_[p["ta"].to_numpy(), t1]
    occ = {}
    for k, r in enumerate(reps):
        occ[r] = occ.get(r, 0) + (tt[k + 1] - tt[k])
    settled = max(occ, key=occ.get)
    if init_repo is not None and settled == init_repo:
        out.update(why="no_move", settled_is_init=True)
    first = float(p.filter(pl.col("repo") == settled)["ta"][0]) - t0
    prevs = [init_repo] + reps[:-1] if init_repo is not None else [None] + reps[:-1]
    out.update(t_i=first if out["why"] != "no_move" else np.nan, t_first_settled=first,
               why=out["why"] if out["why"] == "no_move" else "ok",
               switches=int(sum(1 for x, y in zip(prevs, reps) if x != y)), n_repos=len(occ))
    return out


def figures(rep: dict, g44: dict, newc: dict):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fd = L.ROOT / "hypotheses/H75-reallocation-speed-limit/figures"
    fd.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.9))
    cols = {"G39": "#2a78d6", "G40": "#d03b3b", "G41": "#0ca30c", "G51": "#7a4fbf"}
    for k, r in rep.items():
        t = np.arange(len(r["curve_D"])) * L.GRID_H
        ax[0].plot(t, r["curve_D"], color=cols.get(k[:3], "k"), lw=1.3,
                   label=f"{k[:3]} ({'pre' if r['variant'] == 'pre' else 'from ∅'})", ls="-" if r["variant"] == "pre" else "--")
        if np.isfinite(r.get("T_e", np.nan)):
            ax[0].axvline(r["T_e"], color=cols.get(k[:3], "k"), lw=0.6, alpha=0.5)
    ax[0].set_xlabel("active hours since kickoff")
    ax[0].set_ylabel("TV distance to settled allocation")
    ax[0].legend(fontsize=6.5, frameon=False)
    ax[0].set_title("(a) allocation relaxation", fontsize=8)
    # slack panel: S vs W/A for each period (bound line S = 1)
    syn = pl.read_parquet(L.OUTD / "synthetic/summary.parquet")
    for (sc, mk) in (("F", "o"), ("A", "s"), ("Z", "^")):
        v = syn.filter((pl.col("scen") == sc) & (pl.col("N") == 15))
        ax[1].scatter([v["T_e"][0]], [v["S_e"][0]], marker=mk, facecolors="none", edgecolors="grey", s=30,
                      label=f"synthetic {sc}")
    for k, r in rep.items():
        if not np.isfinite(r.get("S_e", np.nan)):
            continue
        lo, hi = r["boot"]["S_e"]
        ax[1].errorbar([r["T_e"]], [r["S_e"]], yerr=[[r["S_e"] - lo], [hi - r["S_e"]]], fmt="o" if r["variant"] == "pre" else "D",
                       color=cols.get(k[:3], "k"), ms=4, lw=0.8)
        ax[1].annotate(k[:3], (r["T_e"], r["S_e"]), fontsize=6, xytext=(3, 2), textcoords="offset points")
    for room, col in (("best", "#e08a00"), ("rest", "#555555")):
        x = g44[room]
        if np.isfinite(x.get("S_e", np.nan)) and np.isfinite(x.get("T_e", np.nan)):
            lo, hi = x["boot"]["S_e"]
            ax[1].errorbar([x["T_e"]], [x["S_e"]], yerr=[[x["S_e"] - lo], [hi - x["S_e"]]], fmt="*", color=col, ms=7, lw=0.8)
            ax[1].annotate(f"G44 #{room}", (x["T_e"], x["S_e"]), fontsize=6, xytext=(3, -8), textcoords="offset points")
    ax[1].axhline(1, color="k", lw=0.7)
    ax[1].axhline(3, color="k", lw=0.5, ls=":")
    ax[1].set_xscale("log")
    ax[1].set_yscale("log")
    ax[1].set_xlabel("settling time T_e (active h)")
    ax[1].set_ylabel("slack S = ĀT/W")
    ax[1].set_title("(b) speed-limit slack (bound: S = 1)", fontsize=8)
    ax[1].legend(fontsize=6, frameon=False, loc="upper left")
    fig.tight_layout()
    fig.savefig(fd / "summary_obs.pdf")
    fig.savefig(fd / "summary_obs.png", dpi=150)
    plt.close(fig)
    # synthetic figure
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.4))
    df = pl.read_parquet(L.OUTD / "synthetic/synthetic.parquet").filter(pl.col("N") == 15)
    for i, sc in enumerate(("F", "A", "Z")):
        v = df.filter(pl.col("scen") == sc)
        ax[0].hist(np.log10(v["S_e"].drop_nans().to_numpy()), bins=25, alpha=0.5, label=sc)
        ax[1].hist(v["el_eps"].drop_nans().to_numpy(), bins=25, alpha=0.5, label=sc)
    ax[0].set_xlabel("log10 slack S (N = 15)")
    ax[0].legend(fontsize=7, frameon=False)
    ax[1].set_xlabel("cadence elasticity ε (N = 15)")
    ax[1].axvline(0, color="k", lw=0.6)
    ax[1].axvline(-1, color="k", lw=0.6, ls=":")
    ax[1].legend(fontsize=7, frameon=False)
    fig.tight_layout()
    fig.savefig(fd / "synthetic_compact.pdf")
    fig.savefig(fd / "synthetic_compact.png", dpi=150)
    plt.close(fig)


def main():
    rep = {}
    for g, var in B.REPLICATION.items():
        for v in (["pre", "null"] if var == "pre" else ["null"]):
            r = period_result(g, v)
            rep[f"G{g:02d}_{v}"] = r
            L.write_json(L.OUTD / f"G{g:02d}" / f"results_{v}.json", r)
            print(f"G{g} {v}: N {r['N']} T_e {r.get('T_e')} W {r.get('W_e')} A {r.get('A_e')} S {r.get('S_e')} "
                  f"R {r.get('R_e')} T90 {r.get('T_90')} S90 {r.get('S_90')} eps {r['elasticity']}", flush=True)
    # primary variant per period
    prim = {k: r for k, r in rep.items() if (k.endswith("_pre") or k.startswith("G51"))}
    eps = [r["elasticity"]["eps"] for r in prim.values()]
    se = [r["elasticity"]["se"] for r in prim.values()]
    m, msd, tau = L.re_mean(eps, se)
    pooled = {"eps_re": m, "se": msd, "ci": [m - 1.96 * msd, m + 1.96 * msd], "tau": tau}
    epsc = [r["elasticity"]["eps_ctrl"] for r in prim.values()]
    sec = [r["elasticity"]["se_ctrl"] for r in prim.values()]
    mc, msdc, tauc = L.re_mean(epsc, sec)
    pooled_ctrl = {"eps_re": mc, "se": msdc, "ci": [mc - 1.96 * msdc, mc + 1.96 * msdc], "tau": tauc}
    lo, hi = pooled["ci"]
    p4 = "field-like" if not (lo <= SYN["A"] <= hi) and (lo <= SYN["F"] <= hi) else (
        "activity-like" if not (lo <= SYN["F"] <= hi) and (lo <= SYN["A"] <= hi) else "inconclusive")
    g44 = native_g44()
    L.write_json(L.OUTD / "G44" / "results_native.json", g44)
    print("G44", {k: g44[k] for k in ("T_ratio_rest_best", "activity_pred_ratio", "miss_factor", "verdict")},
          {r: (g44[r]["N"], g44[r].get("T_e"), g44[r].get("A_e"), g44[r].get("S_e")) for r in ("best", "rest", "all")})
    newc = native_g51_newcomers()
    L.write_json(L.OUTD / "G51" / "results_native_newcomers.json", newc)
    print("G51 newcomers", newc["elasticity"], newc["median_t_i"], newc["range_t_i"], newc["ne38"], newc["verdict"])
    summ = {"replication": {k: {kk: r.get(kk) for kk in ("N", "T_e", "W_e", "A_e", "S_e", "R_e", "A_ss", "T_90", "W_90", "S_90",
                                                          "R_90", "Sigma_ex_min_e", "Sigma_ex_min_90", "viol_e", "viol_90",
                                                          "D0", "Df", "W_total", "median_call_rate")} | {
        "boot": r["boot"], "elasticity": r["elasticity"], "elasticity_mid": r["elasticity_mid"], "verdict": verdict(r)}
        for k, r in rep.items()},
        "pooled_eps": pooled, "pooled_eps_ctrl": pooled_ctrl, "P4_reading": p4, "synthetic_reference": SYN,
        "g44": {k: g44[k] for k in ("H", "T_ratio_rest_best", "activity_pred_ratio", "miss_factor", "verdict")} | {
            r: {kk: g44[r].get(kk) for kk in ("N", "T_e", "W_e", "A_e", "S_e", "R_e", "T_90", "S_90")} | {"boot_S": g44[r]["boot"]["S_e"]}
            for r in ("best", "rest", "all")},
        "newcomers": {k: newc[k] for k in ("elasticity", "median_t_i", "range_t_i", "ne38", "checks", "verdict")} | {
            "n": len(newc["newcomers"]), "rows": newc["newcomers"]}}
    L.write_json(L.OUTD / "results/summary.json", summ)
    print("pooled eps", pooled, "ctrl", pooled_ctrl, p4)
    figures(rep, g44, newc)
    # per-period estimates
    rows = []
    for k, r in rep.items():
        g = r["goal"]
        unit = f"G{g:02d}"
        for stat, key, bk in (("speed_limit_slack_S_e", "S_e", "S_e"), ("settling_time_T_e_h", "T_e", "T_e"),
                              ("allocation_distance_W_e", "W_e", "W_e"), ("switch_activity_A_e", "A_e", "A_e"),
                              ("activity_ratio_R_e", "R_e", "R_e")):
            v = r.get(key)
            lo_, hi_ = r["boot"].get(bk, [None, None])
            rows.append(dict(period_unit=unit, goal_no=g, statistic=stat, channel=f"work_commits:{r['variant']}",
                             estimate=v if v is not None and np.isfinite(v) else None, ci_lo=lo_, ci_hi=hi_, n=r["N"],
                             method="H75 repo-allocation speed limit, 20 active h, agent bootstrap B=200",
                             null="synthetic F/A/Z (amendment A1)", role="replication", ci_kind="percentile",
                             n_kind="agents", notes="S_e >= 1 by construction (counting identity)"))
        e = r["elasticity"]
        if e.get("eps") is not None and np.isfinite(e["eps"]):
            lo_, hi_ = EST.ci_from_se(e["eps"], e["se"])
            rows.append(dict(period_unit=unit, goal_no=g, statistic="cadence_elasticity_eps", channel=f"work_commits:{r['variant']}",
                             estimate=e["eps"], ci_lo=lo_, ci_hi=hi_, se=e["se"], n=e["n"], method="OLS log t_i ~ log call rate, HC1",
                             null="synthetic F mean -0.53 / A mean -0.86", role="replication", ci_kind="se_z", n_kind="agents"))
    for r in ("best", "rest"):
        x = g44[r]
        rows.append(dict(period_unit="G44", goal_no=44, statistic="settling_time_T_e_h", channel=f"work_commits:null:room_{r}",
                         estimate=x.get("T_e") if np.isfinite(x.get("T_e", np.nan)) else None, ci_lo=x["boot"]["T_e"][0],
                         ci_hi=x["boot"]["T_e"][1], n=x["N"], method="H75 native N1 (room split)", null="activity-limited ratio",
                         role="native", ci_kind="percentile", n_kind="agents"))
    e = newc["elasticity"]
    if e.get("eps") is not None and np.isfinite(e.get("eps", np.nan)):
        lo_, hi_ = EST.ci_from_se(e["eps"], e["se"])
        rows.append(dict(period_unit="G51", goal_no=51, statistic="newcomer_cadence_elasticity_eps", channel="work_commits:newcomers",
                         estimate=e["eps"], ci_lo=lo_, ci_hi=hi_, se=e["se"], n=e["n"], method="H75 native N2 (newcomers)",
                         null="|eps| <= 0.3", role="native", ci_kind="se_z", n_kind="agents"))
    EST.write_estimates(rows, hypothesis="H75")
    B.provenance({"horizon_h": H, "pre_days": 2, "grid_h": L.GRID_H, "settle_win_h": 4.0, "boot": NBOOT,
                  "work_filter": "DQ4 default", "run": "analysis/run.py"})


if __name__ == "__main__":
    main()
