"""H17 round 1b: soft-state MSM on Jev v3.1 behavior states (6 macro states; 12 states in G51) and the round-1
action-class t2* re-correlated with real failures. Non-holdout only. Design and predictions: card, "Round 1b".

Usage:
  uv run python hypotheses/H17-behavior-metastable-sets/analysis/round1b.py [--periods 38 51 ...] [--workers 2]
  uv run python .../round1b.py --summarize          (cross-period statistics after the per-period runs)
Writes data/processed/H17-behavior-metastable-sets/r1b/G<NN>.json and r1b/summary_r1b.json.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("POLARS_MAX_THREADS", "1")

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import polars as pl
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h17lib as L  # noqa: E402
import v3lib as V  # noqa: E402
from periods import PERIODS  # noqa: E402

ROOT = V.ROOT
DATA = ROOT / "data/processed/H17-behavior-metastable-sets"
OUT = DATA / "r1b"
TO = ROOT / "data/processed/behavior_states/turn_outcomes.parquet"
MACRO = {"work": ["execute_task"], "inquire": ["research_browse", "verify_report"], "fix": ["debug_recover"],
         "talk": ["plan_coordinate", "communicate_external", "social", "meta"],
         "wait": ["monitor_wait", "idle", "absent"], "maint": ["self_maintenance"]}
MNAMES = list(MACRO)
TAUS = [1, 2, 3, 4, 6]
EQ_WINDOWS = 3000
R_BOOT, N_NULL, N_EQ = 200, 100, 50
MIN_TRANS, BLOCK = 300, 12


# ============================================================================ state matrices
def p12(v):
    P = np.zeros((v.height, len(V.STATES12)))
    lab = v["labeled"].to_numpy()
    for j, s in enumerate(V.JEV):
        P[:, j] = np.nan_to_num(v[f"p_{s}"].to_numpy().astype(np.float64)) * lab
    P[~lab, -1] = 1.0
    rs = P.sum(1, keepdims=True)
    return P / np.where(rs > 0, rs, 1.0)


def macro(P12, rare=0.01):
    M = np.zeros((len(V.STATES12), len(MNAMES)))
    for k, nm in enumerate(MNAMES):
        for s in MACRO[nm]:
            M[V.STATES12.index(s), k] = 1.0
    P = P12 @ M
    return merge_rare(P, MNAMES, rare)


def merge_rare(P, names, rare=0.01):
    mass = P.mean(0)
    keep = [j for j in range(P.shape[1]) if mass[j] >= rare]
    rest = [j for j in range(P.shape[1]) if mass[j] < rare]
    out, nm = P[:, keep], [names[j] for j in keep]
    if rest and P[:, rest].sum(1).mean() >= rare:
        out = np.column_stack([out, P[:, rest].sum(1)])
        nm.append("rare")
    rs = out.sum(1, keepdims=True)
    return out / np.where(rs > 0, rs, 1.0), nm


# ============================================================================ estimators
def lam2(K):
    w = np.abs(L.eig_sorted(K))
    return float(w[1]) if len(w) > 1 else np.nan


def t2_of_lam(lam, tau=1, unit=5.0):
    if not np.isfinite(lam) or lam <= 0:
        return np.nan
    return float(-tau * unit / np.log(min(lam, 1 - 1e-12)))


def seg_C(S, lags):
    nseg = int(S["seg"].max()) + 1
    return {t: V.seg_soft_counts(S["P"], S["seg"], t, nseg) for t in lags}


def t2_shift_from(Csk, w=None, tau=1):
    C0 = Csk[1].sum(0) if w is None else np.tensordot(w, Csk[1], 1)
    C1 = Csk[1 + tau].sum(0) if w is None else np.tensordot(w, Csk[1 + tau], 1)
    return lam2(V.K_shift(C0, C1))


def t2_eq(S, Csk, rng, n_eq=N_EQ, target=EQ_WINDOWS):
    """Median t2 over random agent-day sets totalling ~target windows (matched small-sample bias)."""
    nseg = len(S["seg_agent"])
    sizes = np.bincount(S["seg"], minlength=nseg)
    if sizes.sum() <= target:
        return t2_of_lam(t2_shift_from(Csk)), True
    vals = []
    for _ in range(n_eq):
        o = rng.permutation(nseg)
        take = o[: int(np.searchsorted(np.cumsum(sizes[o]), target)) + 1]
        w = np.zeros(nseg)
        w[take] = 1
        vals.append(t2_of_lam(t2_shift_from(Csk, w)))
    return float(np.nanmedian(vals)), False


def analyze(v, P, names, rng, heavy=True, label=""):
    """Soft MSM statistics of one sequence set (soft P with state names)."""
    S = V.sequences(v, P)
    q = S["q"]
    nseg = int(S["seg"].max()) + 1
    lags = sorted(set([1, 2, 3, 4, 5, 6, 7]))
    Csk = seg_C(S, lags)
    C = {t: Csk[t].sum(0) for t in lags}
    out = {"label": label, "names": names, "q": q, "n_windows": int(len(S["x"])), "n_segments": nseg,
           "n_agents": int(len(np.unique(S["seg_agent"]))), "n_days": int(len(np.unique(S["seg_day"]))),
           "occupancy": dict(zip(names, P.mean(0).round(4).tolist())),
           "n_transitions": int(C[1].sum().round())}
    lam = t2_shift_from(Csk)
    out["lam2"] = lam
    out["t2"] = t2_of_lam(lam)
    out["its"] = {str(t): t2_of_lam(t2_shift_from(Csk, tau=t), tau=t) for t in TAUS}
    out["its_rise_15_5"] = out["its"]["3"] / out["t2"] if out["t2"] and np.isfinite(out["t2"]) else None
    Wb = L.boot_weights(nseg, R_BOOT, rng)
    lb = np.array([t2_shift_from(Csk, w) for w in Wb])
    lb = lb[np.isfinite(lb)]
    out["t2_ci_raw"] = [t2_of_lam(np.percentile(lb, 2.5)), t2_of_lam(np.percentile(lb, 97.5))]
    lam_bc = float(np.clip(2 * lam - np.median(lb), 1e-6, 1 - 1e-9))
    out["lam2_bc"] = lam_bc
    out["t2_bc"] = t2_of_lam(lam_bc)
    lo, hi = 2 * lam - np.percentile(lb, 97.5), 2 * lam - np.percentile(lb, 2.5)
    out["t2_bc_ci"] = [t2_of_lam(float(np.clip(lo, 1e-6, 1 - 1e-9))), t2_of_lam(float(np.clip(hi, 1e-6, 1 - 1e-9)))]
    out["t2_eq"], out["eq_all_windows"] = t2_eq(S, Csk, rng)
    out["t2_soft_naive"] = float(L.its_from_T(V.soft_T(C[1]), 1)[0] * 5)
    out["t2_argmax"] = float(L.its_from_C(L.counts(S["x"], S["seg"], q, 1), 1)[0] * 5)
    # sets (composition only)
    Ms = V.soft_sets(C[1])
    M2 = V.soft_sets(C[1], m=2)

    def sets_of(M):
        if not M.get("m"):
            return None
        return [[names[i] for i in range(q) if M["labels"][i] == k] for k in range(M["m"])]
    out.update({"m": Ms.get("m"), "sets_m": sets_of(Ms), "sets_m2": sets_of(M2), "crispness_m2": M2.get("crispness")})
    # soft CK (weak: no power in synthetic) on the m = 2 memberships and the full matrix
    if M2.get("m"):
        est, pred = V.soft_ck(C, M2["chi"], 5)
        out["ck_est"], out["ck_pred"] = est, pred
        out["ck_max"] = float(np.nanmax(np.abs(est - pred)[1:4]))
    out["ck_full"] = V.soft_ck_full(C, 5)
    # P8 on argmax counts (day-blocked held-out)
    Ch = L.seg_counts(S["x"], S["seg"], q, 1, nseg)
    segfold, k = L.day_folds(S["seg_day"])
    if k >= 2:
        h = L.heldout_models(Ch, segfold, k)
        n = h["n"].sum()
        out["ll_tau1"] = {m_: float(h[m_].sum() / n) for m_ in ("M0", "R1", "M1")}
        out["folds_beat_R1"] = int(np.sum(h["M1"] > h["R1"]))
        out["folds_beat_M0"] = int(np.sum(h["M1"] > h["M0"]))
        out["folds"] = int(len(h["n"]))
        out["p8"] = bool(out["folds_beat_R1"] >= min(4, k) and out["folds_beat_M0"] >= min(4, k)
                         and out["ll_tau1"]["M1"] > max(out["ll_tau1"]["R1"], out["ll_tau1"]["M0"]))
    # soft N2 (descriptive; not calibrated on soft states)
    if heavy:
        n2 = []
        for _ in range(N_NULL):
            idx = V.sojourn_index(S["x"], S["seg"], rng)
            Pn = S["P"][idx]
            C1n = V.seg_soft_counts(Pn, S["seg"], 1, nseg).sum(0)
            C2n = V.seg_soft_counts(Pn, S["seg"], 2, nseg).sum(0)
            n2.append(t2_of_lam(lam2(V.K_shift(C1n, C2n))))
        n2 = np.array(n2, float)
        out["n2_med"] = float(np.nanmedian(n2))
        out["n2_p95"] = float(np.nanpercentile(n2, 95))
        out["p3b_descriptive"] = bool(out["t2"] > out["n2_p95"] and out["t2"] / out["n2_med"] >= 1.25)
    # per-agent MSMs
    per = []
    for a in np.unique(S["seg_agent"]):
        msk = S["seg_agent"] == a
        if len(np.unique(S["seg_day"][msk])) < 2:
            continue
        Sa = L.subset(S, msk)
        nsa = int(Sa["seg"].max()) + 1
        if len(Sa["x"]) - nsa < MIN_TRANS:
            continue
        blk = V.block_ids(Sa["seg"], BLOCK)
        nb = int(blk.max()) + 1
        # block-level soft counts (pairs assigned to the block of their start)
        Cb = {}
        for t in (1, 2):
            ok = Sa["seg"][:-t] == Sa["seg"][t:]
            A, B, bb = Sa["P"][:-t][ok], Sa["P"][t:][ok], blk[:-t][ok]
            M_ = np.zeros((nb, q, q))
            np.add.at(M_, bb, A[:, :, None] * B[:, None, :])
            Cb[t] = M_
        la = lam2(V.K_shift(Cb[1].sum(0), Cb[2].sum(0)))
        Wa = L.boot_weights(nb, 100, rng)
        bs = np.array([t2_of_lam(lam2(V.K_shift(np.tensordot(w, Cb[1], 1), np.tensordot(w, Cb[2], 1)))) for w in Wa])
        bs = bs[np.isfinite(bs) & (bs > 0)]
        per.append({"agent": int(a), "t2": t2_of_lam(la), "ln_se": float(np.std(np.log(bs))) if len(bs) > 10 else np.nan,
                    "n": int(len(Sa["x"])), "days": int(len(np.unique(Sa["seg_day"])))})
    out["per_agent"] = per
    ok = [p for p in per if np.isfinite(p["t2"]) and p["t2"] > 0 and np.isfinite(p["ln_se"])]
    if len(ok) >= 3:
        I2, Qc = L.i_squared([np.log(p["t2"]) for p in ok], [p["ln_se"] for p in ok])
        out["I2"], out["I2_Q"] = I2, Qc
    else:
        out["I2"] = None
    return out


def covariates(v):
    """Period and per-agent stuckness covariates from labelled windows (D4)."""
    lab = v.filter(pl.col("labeled"))
    hours = v.height * 5 / 60

    def agg(df, h):
        r = df.select(pl.col("n_errors").sum().alias("err"), pl.col("n_actions").sum().alias("act"),
                      pl.col("n_stderr").sum().alias("stderr"), pl.col("p_blocked").mean().alias("p_blocked"),
                      (pl.col("n_commit_ok").sum() + pl.col("n_push_ok").sum()).alias("out"),
                      pl.col("longest_run").cast(pl.Float64).mean().alias("longest_run"),
                      pl.col("repeated_error_share").mean().alias("rep_err"),
                      pl.col("progress_score").mean().alias("progress")).row(0, named=True)
        return {"fail_share": r["err"] / max(r["act"], 1), "stderr_share": r["stderr"] / max(r["act"], 1),
                "p_blocked": r["p_blocked"], "out_rate": r["out"] / max(h, 1e-9), "longest_run": r["longest_run"],
                "rep_err": r["rep_err"], "progress": r["progress"]}
    res = agg(lab, hours)
    per = {}
    for (a,), g in lab.group_by(["agent"]):
        ha = v.filter(pl.col("agent") == a).height * 5 / 60
        per[int(a)] = agg(g, ha)
    return res, per


def action_class_cov(goal):
    """Round-1 action-class t2* and per-agent t2 with real failure shares (turn_outcomes.failed / computer-use turns)."""
    f = DATA / f"G{goal:02d}" / "result.json"
    if not f.exists():
        return None
    r = json.loads(f.read_text())["primary"]
    cov = pl.read_parquet(DATA / "covariates.parquet").filter(pl.col("goal_no") == goal)
    days = cov["pt_date"].unique().to_list()
    to = pl.read_parquet(TO, columns=["t", "agent", "failed"]).with_columns(
        pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8).alias("pt_date"))
    to = to.filter(pl.col("pt_date").is_in(days))
    fd = to.group_by("agent", "pt_date").agg(pl.col("failed").sum().cast(pl.UInt32).alias("n_failed"))
    cov = cov.join(fd.with_columns(pl.col("agent").cast(cov["agent"].dtype)), on=["agent", "pt_date"], how="left").with_columns(
        pl.col("n_failed").fill_null(0))
    ca = cov.group_by("agent").agg(pl.col("n_turns").sum(), pl.col("n_error").sum(), pl.col("n_output").sum(),
                                   pl.col("present_min").sum(), pl.col("n_failed").sum())
    tot = ca.select(pl.col("n_turns").sum(), pl.col("n_failed").sum(), pl.col("n_error").sum()).row(0, named=True)
    out = {"t2_round1": r["t2"], "fail_share_real": tot["n_failed"] / max(tot["n_turns"], 1),
           "err_share_stderr": tot["n_error"] / max(tot["n_turns"], 1), "per_agent": []}
    pad = {int(z["agent"]): z for z in ca.iter_rows(named=True)}
    for p in r.get("per_agent", []):
        z = pad.get(p["agent"])
        if z is None or z["n_turns"] < 50:
            continue
        out["per_agent"].append({"agent": p["agent"], "t2": p["t2"], "fail_share_real": z["n_failed"] / z["n_turns"],
                                 "err_share_stderr": z["n_error"] / z["n_turns"],
                                 "out_rate": z["n_output"] / max(z["present_min"] / 60, 1e-9)})
    return out


def run_goal(goal, seed=20261004):
    t0 = time.time()
    rng = np.random.default_rng(seed + goal)
    v = V.load_v3_table(goals=[goal])
    if goal == 31:   # round 1 used the whole goal; keep identical days for comparability
        pass
    P12 = p12(v)
    P6, n6 = macro(P12)
    res = {"goal": goal, "regime": PERIODS[goal], "days": sorted(v["pt_date"].unique().to_list())}
    res["v3_q6"] = analyze(v, P6, n6, rng, heavy=True, label="q6")
    if goal == 51:
        P12m, n12 = merge_rare(P12, V.STATES12)
        res["v3_q12"] = analyze(v, P12m, n12, rng, heavy=False, label="q12")
    res["cov"], res["cov_agent"] = covariates(v)
    res["action_class"] = action_class_cov(goal)
    res["secs"] = round(time.time() - t0, 1)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"G{goal:02d}.json").write_text(json.dumps(L.jsonable(res)))
    q6 = res["v3_q6"]
    return goal, round(q6["t2"], 2), round(q6["t2_bc"], 2), round(q6["t2_eq"], 2), res["secs"]


# ============================================================================ cross-period summary
def meta_r(rows):
    """Fisher-z meta of per-period Spearman correlations: rows = [(rho, n)]."""
    rows = [(r, n) for r, n in rows if np.isfinite(r) and n >= 5]
    if not rows:
        return None
    z = np.array([np.arctanh(np.clip(r, -0.999, 0.999)) for r, _ in rows])
    w = np.array([n - 3 for _, n in rows], float)
    zm = float((w * z).sum() / w.sum())
    se = 1 / np.sqrt(w.sum())
    return {"rho": float(np.tanh(zm)), "z": zm / se, "p_two": float(2 * stats.norm.sf(abs(zm / se))), "k": len(rows),
            "n": int(w.sum() + 3 * len(rows))}


def strat_spearman(x, y, strata, rng, n_perm=10000):
    x, y, s = np.asarray(x, float), np.asarray(y, float), np.asarray(strata)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y, s = x[ok], y[ok], s[ok]

    def r(xx, yy):
        rx = np.concatenate([stats.rankdata(xx[s == g]) - stats.rankdata(xx[s == g]).mean() for g in np.unique(s)])
        ry = np.concatenate([stats.rankdata(yy[s == g]) - stats.rankdata(yy[s == g]).mean() for g in np.unique(s)])
        return float(np.corrcoef(rx, ry)[0, 1])
    order = np.concatenate([np.flatnonzero(s == g) for g in np.unique(s)])
    x, y, s = x[order], y[order], s[order]
    obs = r(x, y)
    null = []
    for _ in range(n_perm):
        yp = y.copy()
        for g in np.unique(s):
            m = s == g
            yp[m] = rng.permutation(yp[m])
        null.append(r(x, yp))
    null = np.array(null)
    return {"rho": obs, "p_two": float((1 + np.sum(np.abs(null) >= abs(obs) - 1e-12)) / (n_perm + 1)), "n": int(len(x))}


def summarize():
    rng = np.random.default_rng(20261004)
    R = {}
    for g in PERIODS:
        f = OUT / f"G{g:02d}.json"
        if f.exists():
            R[g] = json.loads(f.read_text())
    rows = []
    for g, r in R.items():
        q6 = r["v3_q6"]
        rows.append({"goal": g, "regime": r["regime"], "t2": q6["t2"], "t2_bc": q6["t2_bc"], "t2_eq": q6["t2_eq"],
                     "n_windows": q6["n_windows"], **{f"cov_{k}": v for k, v in r["cov"].items()},
                     "ac_t2": (r["action_class"] or {}).get("t2_round1"),
                     "ac_fail_real": (r["action_class"] or {}).get("fail_share_real"),
                     "ac_err_stderr": (r["action_class"] or {}).get("err_share_stderr"),
                     "wait_alone_m2": bool(any(set(s) <= {"wait", "maint"} and "wait" in s for s in (q6.get("sets_m2") or []))),
                     "sets_m2": q6.get("sets_m2"), "I2": q6.get("I2"), "p8": q6.get("p8"), "ck_max": q6.get("ck_max"),
                     "p3b_desc": q6.get("p3b_descriptive"), "t2_n2_ratio": (q6["t2"] / q6["n2_med"]) if q6.get("n2_med") else None})
    df = pl.DataFrame(rows, infer_schema_length=None).sort("goal")
    out = {"periods": df.to_dicts()}
    III = df.filter(pl.col("regime") == "III")
    sp = lambda a, b, d: list(map(float, stats.spearmanr(d[a].to_numpy(), d[b].to_numpy()))) if d.height >= 4 else [None, None]
    out["P4b_i_regime3"] = {f"rho_t2eq_{c}": sp("t2_eq", f"cov_{c}", III) for c in ("p_blocked", "out_rate", "fail_share", "longest_run", "rep_err", "progress")}
    out["P4b_i_all_stratified"] = {c: strat_spearman(df["t2_eq"].to_numpy(), df[f"cov_{c}"].to_numpy(), df["regime"].to_numpy(), rng, 5000)
                                   for c in ("p_blocked", "out_rate", "fail_share")}
    # within-period per-agent meta
    mets = {}
    for c in ("p_blocked", "fail_share", "out_rate"):
        rr = []
        for g, r in R.items():
            pa = [p for p in r["v3_q6"]["per_agent"] if np.isfinite(p["t2"] or np.nan) and str(p["agent"]) in r["cov_agent"]]
            if len(pa) >= 5:
                x = [p["t2"] for p in pa]
                y = [r["cov_agent"][str(p["agent"])][c] for p in pa]
                if np.all(np.isfinite(y)):
                    rr.append((float(stats.spearmanr(x, y)[0]), len(pa)))
        mets[c] = meta_r(rr)
    out["P4b_ii_within_meta"] = mets
    # action-class layer with real failures
    out["P4b_iii_action_class_regime3"] = {"rho_t2_fail_real": sp("ac_t2", "ac_fail_real", III),
                                           "rho_t2_err_stderr": sp("ac_t2", "ac_err_stderr", III)}
    rr_real, rr_std = [], []
    for g, r in R.items():
        ac = r.get("action_class") or {}
        pa = ac.get("per_agent", [])
        if len(pa) >= 5:
            rr_real.append((float(stats.spearmanr([p["t2"] for p in pa], [p["fail_share_real"] for p in pa])[0]), len(pa)))
            rr_std.append((float(stats.spearmanr([p["t2"] for p in pa], [p["err_share_stderr"] for p in pa])[0]), len(pa)))
    out["P4b_iii_action_class_within_meta"] = {"real": meta_r(rr_real), "stderr": meta_r(rr_std)}
    out["P4b_iv_p_blocked"] = {"rho_pblocked_fail_all": sp("cov_p_blocked", "cov_fail_share", df),
                               "rho_pblocked_out_all": sp("cov_p_blocked", "cov_out_rate", df),
                               "rho_pblocked_fail_regime3": sp("cov_p_blocked", "cov_fail_share", III),
                               "rho_pblocked_out_regime3": sp("cov_p_blocked", "cov_out_rate", III),
                               "rho_fail_real_vs_stderr_all": sp("cov_fail_share", "cov_stderr_share", df)}
    I_ = df.filter(pl.col("regime") == "I")["t2_eq"].to_numpy()
    T_ = III["t2_eq"].to_numpy()
    mw = stats.mannwhitneyu(I_, T_, alternative="two-sided")
    out["P4c"] = {"median_I": float(np.median(I_)), "median_III": float(np.median(T_)), "mw_p_two": float(mw.pvalue),
                  "I_greater": bool(np.median(I_) > np.median(T_))}
    out["P3d_regime3_wait_alone"] = int(III["wait_alone_m2"].sum())
    out["P5_I2_ge_05"] = [int((df["I2"].drop_nulls() >= 0.5).sum()), int(df["I2"].drop_nulls().len())]
    out["P8_pass"] = [int(df["p8"].sum()), df.height]
    if 51 in R and "v3_q12" in R[51]:
        out["G51_q12_vs_q6"] = {"t2_bc_q12": R[51]["v3_q12"]["t2_bc"], "t2_bc_q6": R[51]["v3_q6"]["t2_bc"],
                                "ratio": R[51]["v3_q12"]["t2_bc"] / R[51]["v3_q6"]["t2_bc"],
                                "sets_m2_q12": R[51]["v3_q12"].get("sets_m2")}
    (OUT / "summary_r1b.json").write_text(json.dumps(L.jsonable(out), indent=1))
    print(json.dumps(L.jsonable({k: v for k, v in out.items() if k != "periods"}), indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--periods", nargs="*", type=int)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--summarize", action="store_true")
    a = ap.parse_args()
    if a.summarize:
        summarize()
        return
    goals = a.periods or list(PERIODS)
    goals = sorted(goals, key=lambda g: -1 if g == 51 else g)
    if a.workers <= 1:
        for g in goals:
            print(run_goal(g), flush=True)
    else:
        with ProcessPoolExecutor(max_workers=min(a.workers, 2)) as ex:
            for r in ex.map(run_goal, goals):
                print(r, flush=True)


if __name__ == "__main__":
    main()
