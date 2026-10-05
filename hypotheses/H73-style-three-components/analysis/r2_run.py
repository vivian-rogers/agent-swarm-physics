"""H73 round 2 real run (non-reserved data only): R2-1a conversation-state decomposition, R2-1b read vs in-flight
accommodation, R2-2 register transients (#51 onset, NE38, #12 by minute), R2-3 reset-and-hold (regimes I/II fresh,
regime III seen), C0 (round-1 N1 T with A5 scaling).

The pipeline functions take a style matrix so r2_synthetic.py runs the same code on synthetic worlds.
Output: data/processed/H73-style-three-components/r2/r2.json
Usage: uv run python hypotheses/H73-style-three-components/analysis/r2_run.py [--only acc,cv,trans,rh,c0]
"""
from __future__ import annotations
import os
for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2"
import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import json  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import h73lib as L  # noqa: E402
import r2lib as R  # noqa: E402

OUTP = R.R2 / "r2.json"
ONSET51, END51 = "2026-07-06", "2026-09-06"
NE38 = "2026-07-29"


def style(m: pl.DataFrame, feats: list[str]) -> np.ndarray:
    return m.select([f"tc_{f}" for f in feats]).to_numpy().astype(np.float64)


# ============================================================================================ R2-1b accommodation
def acc_populations(m: pl.DataFrame, P: pl.DataFrame, design: str = "lag") -> dict:
    """AccData per population key."""
    out = {}
    unc = P["uncertain"].to_numpy()
    for reg in ("I", "II", "III"):
        sel = (P["regime"] == reg).to_numpy()
        out[f"{reg}"] = R.AccData(P.filter(pl.Series(sel & ~unc)), design, m)
        out[f"{reg}_unc"] = R.AccData(P.filter(pl.Series(sel)), design, m)
    return out


def run_acc(D: np.ndarray, pops: dict, n_boot: int = 400, secondary: bool = True, prev: np.ndarray | None = None,
            D17: np.ndarray | None = None, pops_lag: dict | None = None) -> dict:
    """Primary (Amendment R2-A1): local-linear jump at the read boundary u = 0 within B call-age x before-age x density
    cells (|u| <= 60 s). The pre-registered lag-cell difference of means is reported as `prereg_lag`."""
    res = {}
    est = R.accommodation_rd
    for reg in ("III", "I", "II"):
        A = pops[reg]
        r = est(D, A, n_boot=n_boot, seed=11)
        res[reg] = {"pooled": r["pooled"], "units": r["units"]}
        if pops_lag is not None:
            res[reg]["prereg_lag"] = R.accommodation(D, pops_lag[reg], n_boot=n_boot, seed=11)["pooled"]
        if not secondary or r["pooled"] is None:
            continue
        units = list(r["units"])
        rn = est(D, A, sel=A.named, n_boot=n_boot, seed=11, units_keep=units)
        ru = est(D, A, sel=~A.named, n_boot=n_boot, seed=11, units_keep=units)
        res[reg]["named"] = rn["pooled"]; res[reg]["unnamed"] = ru["pooled"]
        if rn["pooled"] and ru["pooled"]:
            d = rn["draws"] - ru["draws"]
            res[reg]["named_minus_unnamed"] = {"est": rn["pooled"]["gamma"] - ru["pooled"]["gamma"],
                                               "lo": float(np.nanquantile(d, 0.025)), "hi": float(np.nanquantile(d, 0.975))}
        res[reg]["no_parent"] = est(D, A, sel=~A.parent, n_boot=n_boot, seed=11, units_keep=units)["pooled"]
        res[reg]["with_uncertain"] = est(D, pops[f"{reg}_unc"], n_boot=n_boot, seed=11)["pooled"]
        if prev is not None:
            res[reg]["change_score"] = est(D, A, n_boot=n_boot, seed=11, change_prev=prev, units_keep=units)["pooled"]
        if D17 is not None:
            res[reg]["tc17"] = est(D17, A, n_boot=n_boot, seed=11, units_keep=units)["pooled"]
    return res


def prev_rows(m: pl.DataFrame) -> np.ndarray:
    """Row of each eligible message's previous eligible message (same agent, PT day), -1 if none."""
    ag = m["agent"].to_numpy(); day = m["pt_date"].to_numpy()
    pr = np.full(m.height, -1)
    same = (ag[1:] == ag[:-1]) & (day[1:] == day[:-1])
    pr[1:][same] = np.arange(m.height - 1)[same]
    return pr


# ============================================================================================ R2-1a decomposition
def run_cv(m: pl.DataFrame, X: np.ndarray, n_perm: int = 100, goals: list | None = None) -> dict:
    out = {}
    rep = json.loads((L.DATA / "replication/replication.json").read_text())
    elig = sorted({v["goal_no"] for k, v in rep.items() if not k.startswith("_")})
    for g in (goals or elig):
        ix = (m["goal_no"] == g).to_numpy()
        mg = m.filter(pl.Series(ix))
        if mg.height < 200:
            continue
        a = L.arrays(mg)
        a["X"] = X[ix]
        r = R.decompose_cv(a, R.cv_block(mg), n_perm=n_perm, seed=g)
        r["regime"] = mg["regime"][0]
        out[f"G{g:02d}"] = r
        print(f"  cv G{g:02d} {r['regime']}: u_Cf {r['u_Cf']:.3f} u_Cv {r['u_Cv']:.3f} p {r.get('p_Cv')}", flush=True)
    return out


# ============================================================================================ R2-2 transients
def incumbents51(m: pl.DataFrame) -> list:
    nat = json.loads((L.DATA / "natives/natives.json").read_text())
    return nat["G51"]["incumbents"]


def onset51(m: pl.DataFrame, X: np.ndarray, n_boot: int = 500, seed: int = 51, focus_all: bool = True) -> dict:
    inc = incumbents51(m)
    pre_m = ((m["regime"] == "III") & m["goal_no"].is_between(36, 44)).to_numpy()
    post_m = ((m["goal_no"] == 51) & (m["pt_date"] >= ONSET51) & (m["pt_date"] <= END51)).to_numpy()
    sel = (pre_m | post_m) & m["agent"].is_in(inc).to_numpy()
    ag, day = m["agent"].to_numpy()[sel], m["pt_date"].to_numpy()[sel]
    Xs = X[sel]
    pre_days = sorted(set(day[pre_m[sel]]))
    post_days = sorted(set(day[post_m[sel]]))
    rng = np.random.default_rng(seed)
    real = R.onset_series(Xs, ag, day, inc, inc, pre_days, post_days, rng, ONSET51)
    # placebo: pseudo-onsets every 7 days inside #36-#44, from the 15th pre day to 14 days before the end
    d0, d1 = dt.date.fromisoformat(pre_days[0]), dt.date.fromisoformat(pre_days[-1])
    pseudo = []
    s = d0 + dt.timedelta(days=14)
    while s <= d1 - dt.timedelta(days=14):
        pseudo.append(s.isoformat()); s += dt.timedelta(days=7)
    plac = {g: [] for g in inc}
    for ps in pseudo:
        pd_ = [d for d in pre_days if d < ps]
        qd = [d for d in pre_days if ps <= d < (dt.date.fromisoformat(ps) + dt.timedelta(days=14)).isoformat()]
        r = R.onset_series(Xs, ag, day, inc, inc, pd_, qd, rng, ps)
        for g, (k, S, n) in r.items():
            plac[g] += [v for v in S if np.isfinite(v)]
    out = {"pseudo_onsets": pseudo, "agents": {}}
    for g, (k, S, n) in real.items():
        if len(k) < 5:
            continue
        f = R.fit_decay(k.astype(float), S, n.astype(float))
        bs = []
        brng = np.random.default_rng(seed + int(g))
        for _ in range(n_boot):
            ix = brng.integers(0, len(k), len(k))
            bs.append(R.fit_decay(k[ix].astype(float), S[ix], n[ix].astype(float)))
        pv = np.array(plac.get(g, []))
        early = S[k <= 2]; mid = S[(k >= 14) & (k <= 42)]; late = S[(k >= 21) & (k <= 60)]
        lw = n[(k >= 21) & (k <= 60)].astype(float)
        # persistence (Amendment R2-A3): late mean vs the placebo mean, day bootstrap of the late days
        lb = []
        if len(late) >= 3:
            for _ in range(n_boot):
                ii = brng.integers(0, len(late), len(late))
                lb.append(float(np.average(late[ii], weights=lw[ii])))
        out["agents"][str(g)] = {
            "k": k.tolist(), "S": S.tolist(), "n": n.tolist(), "fit": f,
            "A_ci": [float(np.quantile([b["A"] for b in bs], 0.025)), float(np.quantile([b["A"] for b in bs], 0.975))],
            "tau_ci": [float(np.quantile([b["tau"] for b in bs], 0.025)), float(np.quantile([b["tau"] for b in bs], 0.975))],
            "early": float(np.mean(early)) if len(early) else np.nan, "mid": float(np.mean(mid)) if len(mid) else np.nan,
            "late": float(np.mean(late)) if len(late) else np.nan,
            "placebo_q95": float(np.quantile(pv, 0.95)) if len(pv) else np.nan,
            "placebo_med": float(np.median(pv)) if len(pv) else np.nan, "n_placebo": int(len(pv)),
            "placebo_mean": float(np.mean(pv)) if len(pv) else np.nan,
            "late_w": float(np.average(late, weights=lw)) if len(late) else np.nan,
            "late_ci": [float(np.quantile(lb, 0.025)), float(np.quantile(lb, 0.975))] if lb else [np.nan, np.nan]}
    diffs = [v["early"] - v["mid"] for v in out["agents"].values() if np.isfinite(v["early"]) and np.isfinite(v["mid"])]
    from scipy.stats import binomtest
    npos = int(sum(d > 0 for d in diffs))
    out["P2"] = {"n": len(diffs), "n_pos": npos, "median_diff": float(np.median(diffs)) if diffs else np.nan,
                 "sign_p": float(binomtest(npos, len(diffs), 0.5, alternative="greater").pvalue) if diffs else np.nan}
    return out


def ne38(m: pl.DataFrame, X: np.ndarray, seed: int = 38) -> dict:
    sel = ((m["goal_no"] == 51) & (m["pt_date"] <= END51)).to_numpy()
    ag, day = m["agent"].to_numpy()[sel], m["pt_date"].to_numpy()[sel]
    Xs = X[sel]
    rng = np.random.default_rng(seed)
    d40 = sorted(set(day[ag == 40]))
    comp = sorted(set(ag.tolist()) - {40})

    def one(ev):
        pre = [d for d in d40 if d < ev][-3:]
        post = [d for d in d40 if d >= ev]
        r = R.onset_series(Xs, ag, day, [40], comp, pre, post, rng, ev)
        return r.get(40)
    k, S, n = one(NE38)
    early = float(np.mean(S[k <= 2])); later = float(np.mean(S[(k >= 7) & (k <= 20)])) if ((k >= 7) & (k <= 20)).any() else np.nan
    plac = {}
    for ev in ("2026-08-05", "2026-08-12", "2026-08-19", "2026-08-26"):
        r = one(ev)
        if r is not None and len(r[0]):
            kk, SS, nn = r
            plac[ev] = float(np.mean(SS[kk <= 2])) if (kk <= 2).any() else np.nan
    f = R.fit_decay(k.astype(float), S, n.astype(float)) if len(k) >= 5 else None
    return {"k": k.tolist(), "S": S.tolist(), "n": n.tolist(), "early": early, "later": later, "placebo_early": plac,
            "fit": f, "pass": bool(early > max([v for v in plac.values() if np.isfinite(v)] or [np.inf])
                                  and np.isfinite(later) and later <= 0.5 * early)}


def judge_minutes(m: pl.DataFrame, X: np.ndarray, n_perm: int = 2000, seed: int = 12) -> dict:
    ix = (m["goal_no"] == 12).to_numpy()
    mg = m.filter(pl.Series(ix))
    a = L.arrays(mg); a["X"] = X[ix]
    Y = a["X"] - a["X"].mean(0)
    _, _, _, Res, _, _ = L.fit_r2(Y, [L.block_G(a), L.block_A(a), L.block_C(a)], return_resid=True)
    reg = a["register"]; ag = a["agent"]; t = a["t"]
    gt = pl.read_parquet(L.SH / "ground_truth_labels.parquet").filter(
        (pl.col("goal_no") == 12) & (pl.col("label_kind") == "judge") & pl.col("preferred") & ~pl.col("holdout"))
    wins = [(r["agent"], r["t_valid_from"].timestamp() * 1e6, r["t_valid_to"].timestamp() * 1e6) for r in gt.iter_rows(named=True)]
    judges = sorted({w[0] for w in wins})
    shift = {}
    for j in judges:
        jj, dd = (ag == j) & (reg == "judge"), (ag == j) & (reg == "debater")
        if jj.sum() >= 3 and dd.sum() >= 3:
            shift[j] = Res[jj].mean(0) - Res[dd].mean(0)
    proj = np.full(len(Y), np.nan); minute = np.full(len(Y), np.nan); wid = np.full(len(Y), -1); post = np.zeros(len(Y), bool)
    for j in shift:
        oth = np.mean([v for k, v in shift.items() if k != j], axis=0)
        u = oth / (np.linalg.norm(oth) + 1e-12)
        base = float((Res[(ag == j) & (reg == "debater")] @ u).mean())
        pj = Res @ u - base
        for w_i, (aj, t0, t1) in enumerate(wins):
            if aj != j:
                continue
            inw = (ag == j) & (t >= t0) & (t < t1) & (reg == "judge")
            proj[inw] = pj[inw]; minute[inw] = (t[inw] - t0) / 6e7; wid[inw] = w_i
            pw = (ag == j) & (t >= t1) & (t < t1 + 30 * 6e7) & (reg == "none")
            post |= pw
            proj[pw] = pj[pw]
    inw = wid >= 0
    bins = [0, 5, 10, 20, np.inf]
    bmeans = {}
    for lo, hi in zip(bins[:-1], bins[1:]):
        s = inw & (minute >= lo) & (minute < hi)
        bmeans[f"{lo}-{hi}"] = (float(proj[s].mean()) if s.any() else np.nan, int(s.sum()))
    wmean = float(proj[inw].mean())
    postmean = float(proj[post].mean()) if post.any() else np.nan

    def slope(mm):
        x, y = mm[inw] / 10.0, proj[inw]
        xd = x - np.array([x[wid[inw] == w].mean() for w in wid[inw]])
        yd = y - np.array([y[wid[inw] == w].mean() for w in wid[inw]])
        return float((xd * yd).sum() / (xd ** 2).sum())
    sl = slope(minute)
    rng = np.random.default_rng(seed)
    null = []
    for _ in range(n_perm):
        mm = minute.copy()
        for w in np.unique(wid[inw]):
            s = np.where(wid == w)[0]
            mm[s] = rng.permutation(mm[s])
        null.append(slope(mm))
    null = np.array(null)
    p_up = float((1 + (null >= sl).sum()) / (1 + n_perm))
    e = bmeans["0-5"][0]
    return {"bins": bmeans, "window_mean": wmean, "post30_mean": postmean, "n_post": int(post.sum()),
            "slope_per10min": sl, "p_buildup": p_up, "n_judge": int(inw.sum()),
            "P_i": bool(np.isfinite(e) and e >= 0.5 * wmean), "P_ii": bool(sl <= 0 or p_up >= 0.05),
            "P_iii": bool(np.isfinite(postmean) and postmean < 0.5 * wmean)}


# ============================================================================================ R2-3 reset-and-hold
def run_rh(m: pl.DataFrame, X17: np.ndarray, Xc: np.ndarray | None = None, n_boot: int = 500,
           pops=(("I_II", ["I", "II"]), ("III", ["III"]))) -> dict:
    out = {}
    agent = m["agent"].to_numpy(); unit = m["unit_id"].to_numpy()
    D = R.deviations(X17, agent, unit)
    for nm, regs in pops:
        Rp = R.rh_pairs(m, regs)
        out[nm] = R.rh_stats(D, Rp, n_boot=n_boot)
        if Xc is not None:
            Dc = R.deviations(Xc, agent, unit, clip=None)
            dc = ((Dc[Rp["a"]] - Dc[Rp["b"]]) ** 2).sum(1) / Dc.shape[1]
            yc = (Dc[Rp["a"]] * Dc[Rp["b"]]).sum(1) / Dc.shape[1]
            Tc = R.scaled_T_stat(dc, Rp, n_boot=n_boot)
            l1 = Rp["lag"] == 1
            gb = Rp["gbin"] - Rp["gbin"].min()
            w = l1 & (Rp["nres"] == 0); ac = l1 & (Rp["nres"] == 1)
            dC1c = R._cw(yc, np.ones(len(yc)), w, ac, gb) - yc[ac].mean()
            Vc = float(((Dc[np.array(Rp["seg_rows"]["row"])]) ** 2).sum(1).mean() / Dc.shape[1])
            out[nm]["content"] = {"T": Tc["T"], "T_ci": Tc["T_ci"], "dC1": dC1c, "kappa_seg": dC1c / Vc}
        if nm == "I_II":
            # per goal period (descriptive rows)
            per = {}
            gl = m["goal_no"].to_numpy()
            for g in sorted(set(gl[np.isin(m["regime"].to_numpy(), regs)])):
                rows = set(np.where(gl == g)[0].tolist())
                keep = np.array([a in rows for a in Rp["a"]])
                if ((Rp["lag"] == 1) & (Rp["nres"] == 1) & keep).sum() < 150:
                    continue
                sub = {k: (v[keep] if isinstance(v, np.ndarray) and len(v) == len(keep) else v) for k, v in Rp.items()}
                srk = np.array([r in rows for r in Rp["seg_rows"]["row"]])
                sub["seg_rows"] = {k: [x for x, f in zip(v, srk) if f] for k, v in Rp["seg_rows"].items()}
                rr = R.rh_stats(D, sub, n_boot=200)
                per[f"G{g:02d}"] = {k: rr[k] for k in ("dC1", "dC1_ci", "kappa_seg", "T", "T_ci", "n_across1", "n_within1")}
            out[nm]["per_goal"] = per
    return out


# ============================================================================================ C0
def c0(m: pl.DataFrame, X17: np.ndarray) -> dict:
    """Round-1 N1 forced-erasure T_s with H46 R2-A5 scaling (call rule, regime III, consecutive messages)."""
    agent = m["agent"].to_numpy(); unit = m["unit_id"].to_numpy()
    D = R.deviations(X17, agent, unit, clip=None)
    Rp = R.rh_pairs(m, ["III"], max_lag=1)
    rk = m["reset_kind_prev"].to_numpy()
    lab_forced = np.array([rk[b] == "forced" for b in Rp["b"]])
    dist = ((D[Rp["a"]] - D[Rp["b"]]) ** 2).sum(1) / D.shape[1]
    out = {}
    for nm, sc, mr in (("unscaled_own_only", False, 5), ("scaled", True, 5)):
        r = R.scaled_T_stat(dist, Rp, n_boot=300, scaled=sc, labels=lab_forced & (Rp["nres"] == 1))
        out[nm] = r
    return out


# ============================================================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="acc,cv,trans,rh,c0")
    args = ap.parse_args()
    m, P = R.load()
    agent = m["agent"].to_numpy(); unit = m["unit_id"].to_numpy()
    X16, X17 = style(m, R.TC16), style(m, R.TC)
    out = json.loads(OUTP.read_text()) if OUTP.exists() else {}
    out["_run"] = dt.datetime.now(dt.UTC).isoformat()
    todo = args.only.split(",")
    if "acc" in todo:
        D16 = R.deviations(X16, agent, unit); D17 = R.deviations(X17, agent, unit)
        out["acc"] = run_acc(D16, acc_populations(m, P, "boundary"), prev=prev_rows(m), D17=D17,
                             pops_lag=acc_populations(m, P, "lag"))
        print("acc", json.dumps({k: v["pooled"] for k, v in out["acc"].items()}, default=float)[:1500], flush=True)
    if "cv" in todo:
        out["cv"] = run_cv(m, X17)
    if "trans" in todo:
        out["onset51"] = onset51(m, X17)
        out["ne38"] = ne38(m, X17)
        out["judge_minutes"] = judge_minutes(m, X17)
        print("trans", json.dumps(out["onset51"]["agents"].get("10", {}).get("fit")), out["onset51"]["P2"], flush=True)
    if "rh" in todo:
        srow = m["srow"].to_numpy()
        C = np.load(L.SH / "embeddings/statements_style_resid32_bge_small.npy", mmap_mode="r")[srow].astype(np.float64)
        out["rh"] = run_rh(m, X17, Xc=C)
        print("rh", {k: {kk: v[kk] for kk in ("dC1", "dC_first", "dC_late", "kappa_seg", "T", "carry")} for k, v in out["rh"].items()}, flush=True)
    if "c0" in todo:
        out["c0"] = c0(m, X17)
        print("c0", out["c0"], flush=True)
    OUTP.parent.mkdir(parents=True, exist_ok=True)
    OUTP.write_text(json.dumps(out, indent=1, default=lambda o: o.tolist() if isinstance(o, np.ndarray) else float(o)))


if __name__ == "__main__":
    main()
