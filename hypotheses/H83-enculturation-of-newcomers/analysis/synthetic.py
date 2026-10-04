"""H83 synthetic validation at real counts (axis F). Runs before any real-data alignment statistic.

Village sampling: the real eligible statement schedule (agent, day, room, tenure, veteran flag), the real newcomer
joins and windows, and the real per-day veteran read doses. Statement vectors are drawn in 32-d:
  x_s = normalize(q_i(d) + f_lab + h_d + eta_{i,d} + o * w_onb(tau) + eps_s)
with variance components calibrated on VETERANS ONLY (pairwise statement cosines within agent-day, between agents on
a day, within agent across days; real projected bge vectors). Newcomers' trajectories are not looked at.
Scenarios:
  S0   null (kickoff-only): constants fixed; a common onboarding vector o on newcomer days, decaying e^{-(tau-1)}
  S0f  null with a larger family component
  S1   dose-driven enculturation: q_i moves toward the present veterans' mean constant,
       closure lambda (1 - exp(-D/D*)), D = cumulative veteran items read (real doses); lambda 0.5 and 0.25
  S2   calendar-driven enculturation: closure lambda (1 - exp(-(tau-1)/5)), lambda 0.5
  S3   reverse: veterans move toward the newcomers present (lambda_r 0.5); newcomers fixed
Outputs: data/processed/H83-enculturation-of-newcomers/synthetic/synthetic.json

  uv run python hypotheses/H83-enculturation-of-newcomers/analysis/synthetic.py [--reps 40]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h83lib as L  # noqa: E402

OUTD = L.DATA / "synthetic"
DIM = 32


def calibrate(st: pl.DataFrame, X: np.ndarray) -> dict:
    """Mean pairwise statement cosines among veterans: within agent-day, between agents same day, same agent other days."""
    v = st["veteran"].to_numpy()
    s = st.filter(pl.Series(v)).select("agent", "pt_date").with_row_index("r")
    Xv = X[v].astype(np.float64)
    ag = s["agent"].to_numpy(); dy = np.array(s["pt_date"].to_list())
    wd_num = wd_den = 0.0
    bd_num = bd_den = 0.0
    S_ad = {}
    for (a, d), grp in s.group_by("agent", "pt_date"):
        r = grp["r"].to_numpy()
        S = Xv[r].sum(0); n = len(r)
        S_ad[(a, d)] = (S, n)
        if n > 1:
            wd_num += S @ S - n; wd_den += n * (n - 1)
    days = sorted(set(dy))
    for d in days:
        items = [(S, n) for (a, dd), (S, n) in S_ad.items() if dd == d]
        if len(items) < 2:
            continue
        T = sum(S for S, _ in items); N = sum(n for _, n in items)
        bd_num += T @ T - sum(S @ S for S, _ in items)
        bd_den += N * N - sum(n * n for _, n in items)
    wa_num = wa_den = 0.0
    for a in set(ag):
        items = [(S, n) for (aa, dd), (S, n) in S_ad.items() if aa == a]
        if len(items) < 2:
            continue
        T = sum(S for S, _ in items); N = sum(n for _, n in items)
        wa_num += T @ T - sum(S @ S for S, _ in items)
        wa_den += N * N - sum(n * n for _, n in items)
    c_wd, c_bd, c_wa = wd_num / wd_den, bd_num / bd_den, wa_num / wa_den
    # different veterans on different days of the same goal period: the persistent shared (culture/period) part
    gp = st.filter(pl.Series(v))["goal_no"].to_numpy()
    xd_num = xd_den = 0.0
    for g in np.unique(gp):
        r = np.flatnonzero(gp == g)
        if len(r) < 10:
            continue
        Tg = Xv[r].sum(0); N = len(r)
        sub = s[r]
        tot = Tg @ Tg
        A_ = sum((lambda z: z @ z)(Xv[r[sub["agent"].to_numpy() == a]].sum(0)) for a in np.unique(sub["agent"].to_numpy()))
        dyy = np.array(sub["pt_date"].to_list())
        D_ = sum((lambda z: z @ z)(Xv[r[dyy == d]].sum(0)) for d in np.unique(dyy))
        AD_ = sum(S @ S for (a, d), (S, n) in S_ad.items() if d in set(dyy.tolist()) and a in set(sub["agent"].to_list()))
        na = np.array([np.sum(sub["agent"].to_numpy() == a) for a in np.unique(sub["agent"].to_numpy())])
        nd = np.array([np.sum(dyy == d) for d in np.unique(dyy)])
        nad = np.array([n for (a, d), (S, n) in S_ad.items() if d in set(dyy.tolist()) and a in set(sub["agent"].to_list())])
        xd_num += tot - A_ - D_ + AD_
        xd_den += N * N - (na ** 2).sum() - (nd ** 2).sum() + (nad ** 2).sum()
    c_xd = xd_num / xd_den
    # different veterans in different goal periods of the same regime: the village-wide persistent part
    xp_num = xp_den = 0.0
    regs = np.array(st.filter(pl.Series(v))["regime"].to_list())
    for rg in np.unique(regs):
        r = np.flatnonzero(regs == rg)
        sub_a = ag[r]; sub_g = gp[r]
        tot = (lambda z: z @ z)(Xv[r].sum(0)); N = len(r)
        A_ = sum((lambda z: z @ z)(Xv[r[sub_a == a]].sum(0)) for a in np.unique(sub_a))
        G_ = sum((lambda z: z @ z)(Xv[r[sub_g == g]].sum(0)) for g in np.unique(sub_g))
        AG_ = sum((lambda z: z @ z)(Xv[r[(sub_a == a) & (sub_g == g)]].sum(0))
                  for a in np.unique(sub_a) for g in np.unique(sub_g) if ((sub_a == a) & (sub_g == g)).any())
        na = np.array([np.sum(sub_a == a) for a in np.unique(sub_a)])
        ng = np.array([np.sum(sub_g == g) for g in np.unique(sub_g)])
        nag = np.array([((sub_a == a) & (sub_g == g)).sum() for a in np.unique(sub_a) for g in np.unique(sub_g)])
        xp_num += tot - A_ - G_ + AG_
        xp_den += N * N - (na ** 2).sum() - (ng ** 2).sum() + (nag ** 2).sum()
    c_xp = xp_num / xp_den
    T = 1.0 / max(1 - c_wd, 1e-3)
    sCv = max(c_xp, 0.0) * T
    sC = max(c_xd - max(c_xp, 0.0), 0.0) * T
    sq = max(c_wa - c_xd, 0.0) * T; sh = max(c_bd - c_xd, 0.0) * T
    se = max(c_wd - c_wa - c_bd + c_xd, 0.0) * T
    return {"c_wd": c_wd, "c_bd": c_bd, "c_wa": c_wa, "c_xd": c_xd, "c_xp": c_xp, "var_Cv": sCv, "var_C": sC,
            "var_q": sq, "var_h": sh, "var_eta": se}


def cum_doses(st, newc, days, doses):
    """newcomer -> {day: cumulative veteran items read before that day}."""
    out = {}
    for a, jd in newc.select("agent", "join_day").iter_rows():
        if jd is None:
            continue
        dd = doses.filter(pl.col("agent") == a).sort("pt_date")
        m = dict(zip(dd["pt_date"].to_list(), dd["items_vet"].to_list()))
        c = 0; cur = {}
        for d in [x for x in days if x >= jd][:40]:
            cur[d] = c
            c += m.get(d, 0)
        out[int(a)] = cur
    return out


def simulate(st, newc, days, cal, cdose, Dstar, scen, lam, rng, var_f=0.02, var_o=0.6, chi0=0.5):
    ag = st["agent"].to_numpy(); dy = np.array(st["pt_date"].to_list())
    tau = st["tau"].fill_null(-1).to_numpy(); vet = st["veteran"].to_numpy()
    labs = st["lab"].to_list()
    agents = sorted(set(ag.tolist())); udays = sorted(set(dy.tolist()))
    q = {a: rng.normal(0, np.sqrt(cal["var_q"] / DIM), DIM) for a in agents}
    lab_set = sorted(set(labs))
    fam = {lb: rng.normal(0, np.sqrt(var_f / DIM), DIM) for lb in lab_set}
    lab_of = dict(zip(ag.tolist(), labs))
    h = {d: rng.normal(0, np.sqrt(cal["var_h"] / DIM), DIM) for d in udays}
    rooms = st["room"].fill_null(-1).to_list()
    hr = {}
    for d, r in set(zip(dy.tolist(), rooms)):
        hr[(d, r)] = rng.normal(0, np.sqrt(0.03 / DIM), DIM)
    o = rng.normal(0, np.sqrt(var_o / DIM), DIM)
    gps = sorted(set(st["goal_no"].to_list()))
    Cg = {g: rng.normal(0, np.sqrt(cal["var_C"] / DIM), DIM) for g in gps}
    Cv = {rg: rng.normal(0, np.sqrt(max(cal["var_Cv"], 0.01) / DIM), DIM) for rg in ("I", "II", "III")}
    reg_of_day = dict(zip(dy.tolist(), st["regime"].to_list()))
    gp_of_day = dict(zip(dy.tolist(), st["goal_no"].to_list()))
    # present veterans / newcomers per day (agent-days)
    ad_keys = st.select("agent", "pt_date", "veteran", "tau").unique()
    vets_on = {}; news_on = {}
    for a, d, v, t in ad_keys.iter_rows():
        (vets_on if v else news_on).setdefault(d, []).append((a, t))
    eta = {}
    Q = {}
    # culture: veterans carry the period's persistent component C_g fully; newcomers carry chi of it.
    #   S0: chi = 1 (the persistent part is period topic everyone has); S0b: chi = chi0 fixed (never acquired)
    #   S1: chi = chi0 + lam (1 - exp(-D/D*)) (1 - chi0); S2: same with calendar time; S3: veterans move to newcomers
    for a, d, v, t in ad_keys.iter_rows():
        C = Cg[gp_of_day[d]] + Cv[reg_of_day[d]]
        base = q[a] + fam[lab_of[a]]
        if v:
            chi = 1.0
        elif scen in ("S0", "S0f", "S3"):
            chi = 1.0
        elif scen == "S0b":
            chi = chi0
        else:
            if scen == "S1":
                D = cdose.get(a, {}).get(d, 0)
                w = 1 - np.exp(-D / Dstar)
            else:
                w = 1 - np.exp(-(max(t or 1, 1) - 1) / 5.0)
            chi = chi0 + lam * w * (1 - chi0)
        base = base + chi * C
        if v and scen == "S3":
            nn = [(b, tt) for b, tt in news_on.get(d, []) if tt is not None and tt <= 20]
            if nn:
                target = np.mean([q[b] + fam[lab_of[b]] for b, _ in nn], 0)
                w = np.mean([1 - np.exp(-(tt - 1) / 5.0) for _, tt in nn])
                base = base + lam * w * (target - (q[a] + fam[lab_of[a]]))
        Q[(a, d)] = base
        eta[(a, d)] = rng.normal(0, np.sqrt(cal["var_eta"] / DIM), DIM)
    n = st.height
    X = rng.normal(0, np.sqrt(1.0 / DIM), (n, DIM))
    keys = list(zip(ag.tolist(), dy.tolist()))
    for i, (a, d) in enumerate(keys):
        X[i] += Q[(a, d)] + h[d] + eta[(a, d)] + hr[(d, rooms[i])]
        if not vet[i] and tau[i] > 0:
            X[i] += o * np.exp(-(tau[i] - 1) / 1.0)
    X /= np.linalg.norm(X, axis=1, keepdims=True)
    return X.astype(np.float32)


def ne27_start(res, newc_agents=(9, 10, 11)):
    """NE27 native (Amendment A1): the batch's window-E gap (all seven agents got the #10 kickoff on the same day)
    and the batch's mean Delta G."""
    J = res["joins"]
    g = [J[a]["G"] for a in newc_agents if a in J]
    if not g:
        return None
    return {"gap_E": float(np.mean([x["gap_E"] for x in g])), "G_new": float(np.mean([x["delta"] for x in g]))}


def summarize_run(res):
    J = res["joins"]
    out = {}
    for key in ("G", "G_mm", "K"):
        vals = [r[key]["delta"] for r in J.values() if r.get(key)]
        out[key] = {"mean": float(np.mean(vals)) if vals else None, "n": len(vals),
                    "n_pos": int(sum(v > 0 for v in vals))}
        rows_ = [r for r in J.values() if r.get(key)]
        m, lo, hi, n = L.boot_mean(vals, B=2000, clusters=[r["join_day"] for r in rows_])
        out[key]["lo"], out[key]["hi"] = lo, hi
    gaps = [r["G"]["gap_E"] for r in J.values() if r.get("G")]
    out["gap_E"] = float(np.mean(gaps)) if gaps else None
    kE = [r["K"]["gap_E"] for r in J.values() if r.get("K")]
    out["K_E"] = float(np.mean(kE)) if kE else None
    x = [np.log1p(r["dose_vet_1_7"]) for r in J.values() if r.get("G")]
    y = [r["G"]["delta"] for r in J.values() if r.get("G")]
    from scipy.stats import spearmanr
    out["rho_dose"] = float(spearmanr(x, y).statistic) if len(x) > 3 else None
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=40)
    ap.add_argument("--only", default="", help="comma list of scenario names, e.g. S0,S0b (size runs)")
    ap.add_argument("--tag", default="", help="output suffix")
    args = ap.parse_args()
    OUTD.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    st, X, _ = L.load("bge", "vec")
    newc = L.newcomers(); days = L.calendar_days()
    doses = pl.read_parquet(L.DATA / "doses.parquet")
    cal = calibrate(st, X)
    print("calibration", cal, flush=True)
    cdose = cum_doses(st, newc, days, doses)
    d7 = [v.get(L.window_days(newc.filter(pl.col("agent") == a)["join_day"][0], days, 7, 7)[0], 0)
          for a, v in cdose.items() if v]
    Dstar = float(np.median([x for x in d7 if x > 0])) if any(x > 0 for x in d7) else 50.0
    print("D* =", Dstar, flush=True)
    scen = [("S0", 0.0), ("S0b", 0.0), ("S0f", 0.0), ("S1", 1.0), ("S1", 0.5), ("S2", 1.0), ("S2", 0.5), ("S3", 0.5)]
    out = {"calibration": cal, "Dstar": Dstar, "reps": args.reps, "scenarios": {}}
    if args.only:
        scen = [x for x in scen if x[0] in args.only.split(",")]
    for name, lam in scen:
        runs = []
        for rep in range(args.reps):
            rng = np.random.default_rng(1000 * rep + int(lam * 100) + hash(name) % 97)
            Xs = simulate(st, newc, days, cal, cdose, Dstar, name, lam, rng,
                          var_f=(0.15 if name == "S0f" else 0.02))
            res = L.run_all(st, Xs, None, newc, days, doses, with_family=True, with_mm=True)
            s = summarize_run(res)
            s["ne27"] = ne27_start(res)
            others = [(a, jd) for a, jd, jh in newc.select("agent", "join_day", "join_holdout").iter_rows()
                      if jd and not jh and a not in (35, 36, 37)]
            s["ne32"] = L.ne32_stats(res["ad"], res["vill"], days, others=others)
            rn = L.rooms_native(res["ad"], days, [(24, "2026-04-17"), (25, "2026-04-22"), (23, "2026-03-16"),
                                                  (26, "2026-04-27"), (27, "2026-05-20"), (29, "2026-05-28")])
            s["rooms"] = {a: v.get("dR") for a, v in rn.items()}
            s["roomsR"] = {a: v.get("R_mean") for a, v in rn.items()}
            runs.append(s)
        key = f"{name}_lam{lam}"
        agg = {}
        for stat in ("G", "G_mm", "K"):
            ms = [r[stat]["mean"] for r in runs if r[stat]["mean"] is not None]
            rej = [r[stat]["lo"] is not None and r[stat]["lo"] > 0 for r in runs]
            rej_neg = [r[stat]["hi"] is not None and r[stat]["hi"] < 0 for r in runs]
            agg[stat] = {"mean": float(np.mean(ms)), "sd": float(np.std(ms)), "reject_pos": float(np.mean(rej)),
                         "reject_neg": float(np.mean(rej_neg)), "n_joins": runs[0][stat]["n"]}
        agg["gap_E"] = float(np.mean([r["gap_E"] for r in runs]))
        gm = np.array([r["G"]["mean"] for r in runs])
        agg["G_null_q95"] = float(np.quantile(gm, 0.95))
        agg["G_ci_lo"] = [r["G"]["lo"] for r in runs]
        agg["K_E"] = float(np.mean([r["K_E"] for r in runs if r["K_E"] is not None]))
        rhos = [r["rho_dose"] for r in runs if r["rho_dose"] is not None]
        agg["rho_dose_mean"] = float(np.mean(rhos))
        from scipy.stats import spearmanr  # noqa: F401
        n_j = runs[0]["G"]["n"]
        # one-sided permutation critical value for Spearman at n_j (approx. normal 1.645/sqrt(n-1))
        crit = 1.645 / np.sqrt(max(n_j - 1, 1))
        agg["rho_dose_power"] = float(np.mean([r > crit for r in rhos]))
        ne = [r["ne27"] for r in runs if r["ne27"]]
        if ne:
            agg["ne27"] = {k: float(np.mean([x[k] for x in ne])) for k in ("gap_E", "G_new")}
            agg["ne27"]["gap_E_sd"] = float(np.std([x["gap_E"] for x in ne]))
            agg["ne27"]["G_new_sd"] = float(np.std([x["G_new"] for x in ne]))
        n32 = [r["ne32"] for r in runs if r.get("ne32")]
        if n32:
            agg["ne32"] = {k: [float(np.mean([x[k] for x in n32])), float(np.std([x[k] for x in n32]))]
                           for k in ("d1", "d2")}
        for a in (24, 25):
            v = [r["rooms"].get(a) for r in runs if r["rooms"].get(a) is not None]
            if v:
                agg[f"room_dR_{a}"] = [float(np.mean(v)), float(np.std(v)), len(v)]
        pooled = [np.mean([x for x in r["rooms"].values() if x is not None]) for r in runs
                  if any(x is not None for x in r["rooms"].values())]
        if pooled:
            agg["room_dR_pooled"] = [float(np.mean(pooled)), float(np.std(pooled)), len(pooled)]
        out["scenarios"][key] = agg
        print(key, json.dumps(agg), f"{time.time() - t0:.0f}s", flush=True)
        (OUTD / f"synthetic{args.tag}.json").write_text(json.dumps(out, indent=1))
    print("done", time.time() - t0)


if __name__ == "__main__":
    main()
