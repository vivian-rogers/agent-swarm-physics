"""H17 per-goal-period MSM analysis (exploratory, non-holdout only).

For each period: pooled MSM on the H14 coarse minute grid (primary), ITS vs lag with agent-day bootstrap, t2* at
tau_c = 5 min, PCCA+ sets, CK test, committors/TPT, currents, nulls N1-N3, per-agent heterogeneity, held-out
adequacy, stuckness covariates, half-day split, and robustness on records and 5-min windows (hard / soft / shifted).

`analyze()` takes any sequence dict (hard or soft states), so Jev states run through the same code:
  uv run python .../run_period.py --jev <behavior_states.parquet> --periods 38 39   (5-min windows, soft)

Usage: uv run python hypotheses/H17-behavior-metastable-sets/analysis/run_period.py [--periods 37 38 ...] [--workers 2]
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
CARD = HERE.parent
ROOT = CARD.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "infra/shared"))
import h17lib as L  # noqa: E402
from common import holdout_mask, load_holdout  # noqa: E402
from periods import PERIODS, TAU_C, TAUS_MIN  # noqa: E402

DATA = ROOT / "data/processed/H17-behavior-metastable-sets"
SH = ROOT / "data/processed/shared"
COARSE = ["browse", "type", "shell", "chat", "idle", "consolidate"]
ACT = ["shell", "click", "scroll", "look", "type", "chat", "idle", "consolidate", "search", "session", "other"]
R_BOOT, N_NULL = 200, 100


# ============================================================================ data
def assert_not_holdout(goal, days):
    h = load_holdout()
    if goal in set(h["goal_periods_held_out"]):
        raise SystemExit(f"goal {goal} is in the locked holdout; exploratory runs refuse it")
    m = holdout_mask(list(days), [goal] * len(days))
    if any(m):
        raise SystemExit(f"holdout days present for goal {goal}")


def load_min(goal, days=None, sm=None):
    sm = pl.read_parquet(DATA / "states_min.parquet") if sm is None else sm
    d = sm.filter((pl.col("goal_no") == goal) & pl.col("present"))
    if days is not None:
        d = d.filter(pl.col("pt_date").is_in(list(days)))
    return d


def seq_from_min(d, half=None):
    if half is not None:
        mx = d.group_by("pt_date").agg(pl.col("minute").max().alias("mx"))
        d = d.join(mx, on="pt_date").filter((pl.col("minute") * 2 <= pl.col("mx")) if half == 1 else (pl.col("minute") * 2 > pl.col("mx")))
    df = d.select(pl.col("agent").cast(pl.Int16), "pt_date", pl.col("minute").cast(pl.Int64).alias("order"),
                  pl.col("coarse_min").cast(pl.Int16).alias("state")).sort("agent", "pt_date", "order")
    return L.sequences_from_table(df, grid=True, q=len(COARSE))


# ============================================================================ core analysis
def analyze(S, names, unit_min, taus, tau_c, rng, R=R_BOOT, nnull=N_NULL, kmax=5, heavy=True, block_len_min=60):
    """Full MSM analysis of one sequence dict. Lags are in steps; unit_min converts steps to minutes."""
    x, seg, q = S["x"], S["seg"], S["q"]
    nseg = int(seg.max()) + 1
    lags = sorted(set(taus) | {tau_c * k for k in range(1, kmax + 1)} | {1})
    Csk = {t: L.seg_counts(x, seg, q, t, nseg) for t in lags}
    C = {t: Csk[t].sum(0) for t in lags}
    out = {"n_steps": int(len(x)), "n_segments": nseg, "n_agents": int(len(np.unique(S["seg_agent"]))),
           "n_days": int(len(np.unique(S["seg_day"]))), "unit_min": unit_min, "tau_c": tau_c, "taus": taus,
           "occupancy": (np.bincount(x, minlength=q) / len(x)).tolist(), "names": names}
    # --- ITS (point + bootstrap)
    its = {t: L.its_from_C(C[t], t) * unit_min for t in taus}
    its_rev = {t: L.its_from_C(C[t], t, rev=True) * unit_min for t in taus}
    Wb = L.boot_weights(nseg, R, rng)
    boot_its = {t: np.array([L.its_from_C(np.tensordot(w, Csk[t], 1), t) * unit_min for w in Wb]) for t in taus}
    out["its"] = {str(t): its[t] for t in taus}
    out["its_rev"] = {str(t): its_rev[t] for t in taus}
    out["its_ci"] = {str(t): np.nanpercentile(boot_its[t], [2.5, 97.5], axis=0) for t in taus}
    t2_curve = np.array([its[t][0] for t in taus])
    out["plateau_tau"] = L.plateau_lag(np.array(taus) * unit_min, t2_curve)
    t2 = float(its[tau_c][0])
    out["t2"] = t2
    out["t2_ci"] = np.nanpercentile(boot_its[tau_c][:, 0], [2.5, 97.5])
    out["ln_t2_se"] = float(np.nanstd(np.log(boot_its[tau_c][:, 0][boot_its[tau_c][:, 0] > 0])))
    out["t3"] = float(its[tau_c][1])
    out["sep"] = t2 / out["t3"] if out["t3"] > 0 else None
    T, act = L.T_mle(C[tau_c])
    pi = L.stationary(T)
    lam = L.eig_sorted(T)
    out["gap"] = float(1 - abs(lam[1]))
    out["t_mix"] = float(L.mixing_time(T) * tau_c * unit_min) if np.isfinite(L.mixing_time(T)) else None
    out["active"] = act.tolist()
    out["pi"] = pi
    out["T_tauc"] = T
    if out["plateau_tau"] is not None:
        tp = int(round(out["plateau_tau"] / unit_min))
        out["t2_plateau"] = float(its[tp][0]) if tp in its else None
    # --- R1
    TR1 = L.sticky_fit(C[tau_c])
    out["t2_R1"] = float(L.its_from_T(TR1, tau_c)[0] * unit_min)
    # --- PCCA+
    M = L.msm_sets(C[tau_c])
    M2 = L.msm_sets(C[tau_c], m=2)
    M3 = L.msm_sets(C[tau_c], m=3) if len(act) > 3 else {"m": None}
    nm = [names[i] for i in act]

    def sets_of(Mx):
        if not Mx.get("m"):
            return None
        return [[nm[i] for i in range(len(nm)) if Mx["labels"][i] == k] for k in range(Mx["m"])]

    out.update({"m": M.get("m"), "eig_rev": M.get("eig_rev"), "crispness": M.get("crispness"),
                "metastability": M.get("metastability"), "sets_m": sets_of(M), "sets_m2": sets_of(M2),
                "sets_m3": sets_of(M3), "chi_m2": M2.get("chi"), "chi_m": M.get("chi"), "crispness_m2": M2.get("crispness"),
                "metastability_m2": M2.get("metastability")})
    # --- CK
    Cs_k = {k: C[tau_c * k] for k in range(1, kmax + 1)}
    if M.get("m"):
        est, pred = L.ck_sets(Cs_k, M["T"], M["active"], M["labels"], M["m"], kmax)
        d0 = (est - pred)[:4]
        out["ck_est"], out["ck_pred"] = est, pred
        out["ck_max"] = float(np.nanmax(np.abs(d0)))
        dd = []
        for w in Wb:
            Cb = {k: np.tensordot(w, Csk[tau_c * k], 1) for k in range(1, kmax + 1)}
            Tb, ab = L.T_mle(Cb[1])
            if len(ab) == len(act):
                e, p_ = L.ck_sets(Cb, Tb, ab, M["labels"], M["m"], kmax)
                dd.append((e - p_)[:4])
        se = np.nanstd(np.array(dd), axis=0) if dd else np.full_like(d0, np.nan)
        out["ck_se"] = se
        out["ck_sig_fail"] = bool(np.any(np.abs(d0) > 2 * np.maximum(se, 1e-9)))
    else:
        out["ck_max"], out["ck_sig_fail"] = None, None
    out["ck_full"] = L.ck_full_error(Cs_k, T, act, pi, kmax)
    # --- committors / TPT between cores of the m = 2 split
    if M2.get("m"):
        chi2 = M2["chi"]
        cA, cB = int(np.argmax(chi2[:, 0])), int(np.argmax(chi2[:, 1]))
        tp = L.tpt(T, pi, cA, cB, tau_c * unit_min)
        mf_AB = L.mfpt(T, cB, tau_c * unit_min)[cA]
        mf_BA = L.mfpt(T, cA, tau_c * unit_min)[cB]
        dboot = []
        for w in Wb:
            Tb, ab = L.T_mle(np.tensordot(w, Csk[tau_c], 1))
            if len(ab) == len(act):
                dboot.append(L.tpt(Tb, L.stationary(Tb), cA, cB)["delta"])
        dboot = np.array(dboot)
        lo, hi = np.nanpercentile(dboot, [2.5, 97.5], axis=0) if len(dboot) else (np.full(len(act), np.nan),) * 2
        inter = [i for i in range(len(act)) if i not in (cA, cB)]
        dmax_i = inter[int(np.argmax(np.abs(tp["delta"][inter])))] if inter else None
        out.update({"cores": [nm[cA], nm[cB]], "q_plus": tp["q_plus"], "q_minus": tp["q_minus"], "delta": tp["delta"],
                    "delta_lo": lo, "delta_hi": hi, "rate_AB_per_min": tp["rate_AB_per_unit"], "mfpt_AB": mf_AB, "mfpt_BA": mf_BA,
                    "delta_max": float(abs(tp["delta"][dmax_i])) if dmax_i is not None else None,
                    "delta_max_state": nm[dmax_i] if dmax_i is not None else None,
                    "delta_sig": bool(dmax_i is not None and (lo[dmax_i] > 0 or hi[dmax_i] < 0))})
    # --- currents (tau = 1)
    C1 = C[1]
    out["ep"] = L.ep_plugin(C1)
    if M3.get("m"):
        lab_full = np.full(q, -1)
        lab_full[act] = M3["labels"]
        keep = lab_full >= 0
        Cm = L.lump_counts(C1[np.ix_(keep, keep)], lab_full[keep], 3)
        out["ep_macro"] = L.ep_plugin(Cm)
        out["ep_macro_share"] = out["ep_macro"] / out["ep"] if out["ep"] else None
    T1, a1 = L.T_mle(C1)
    l1 = L.eig_sorted(T1)[1:4]
    out["eig_T1"] = [[float(z.real), float(z.imag)] for z in l1]
    cplx = [z for z in l1 if abs(z.imag) > 1e-9]
    out["complex_period_min"] = float(2 * np.pi / abs(np.angle(cplx[0])) * unit_min) if cplx else None
    nb_c = 0
    for w in Wb[:100]:
        Tb, _ = L.T_mle(np.tensordot(w, Csk[1], 1))
        nb_c += any(abs(z.imag) > 1e-9 for z in L.eig_sorted(Tb)[1:4])
    out["complex_boot_frac"] = nb_c / min(100, len(Wb))
    # --- nulls
    if nnull:
        n1, n2, n3, ep1, ep2, meta2, mrg = [], [], [], [], [], [], []
        for _ in range(nnull):
            xs = L.null_shuffle(x, seg, rng)
            n1.append(L.its_from_C(L.counts(xs, seg, q, tau_c), tau_c)[0] * unit_min)
            ep1.append(L.ep_plugin(L.counts(xs, seg, q, 1)))
            xn, mf = L.null_sojourn(x, seg, rng)
            mrg.append(mf)
            Cn = L.counts(xn, seg, q, tau_c)
            n2.append(L.its_from_C(Cn, tau_c)[0] * unit_min)
            ep2.append(L.ep_plugin(L.counts(xn, seg, q, 1)))
            if M.get("m"):
                Mn = L.msm_sets(Cn, m=M["m"])
                meta2.append(Mn.get("metastability", np.nan))
            if heavy:
                x3 = L.null_semimarkov(x, seg, q, rng)
                n3.append(L.its_from_C(L.counts(x3, seg, q, tau_c), tau_c)[0] * unit_min)
        n1, n2, n3 = np.array(n1), np.array(n2), np.array(n3)
        out.update({"n1_med": float(np.nanmedian(n1)), "n1_p95": float(np.nanpercentile(n1, 95)),
                    "n2_med": float(np.nanmedian(n2)), "n2_p95": float(np.nanpercentile(n2, 95)), "n2_p": float((1 + np.sum(n2 >= t2)) / (1 + len(n2))),
                    "n2_merged_frac": float(np.mean(mrg)),
                    "n3_med": float(np.nanmedian(n3)) if len(n3) else None, "n3_p95": float(np.nanpercentile(n3, 95)) if len(n3) else None,
                    "n3_p_low": float((1 + np.sum(n3 <= t2)) / (1 + len(n3))) if len(n3) else None,
                    "ep_n1_p95": float(np.nanpercentile(ep1, 95)), "ep_n2_p95": float(np.nanpercentile(ep2, 95)),
                    "metastability_n2_p95": float(np.nanpercentile(meta2, 95)) if meta2 else None})
    # --- adequacy (day-blocked)
    segfold, k = L.day_folds(S["seg_day"])
    out["n_folds"] = k
    for t, tag in ((tau_c, "tauc"), (1, "tau1")):
        h = L.heldout_models(Csk[t], segfold, k)
        n = h["n"].sum()
        out[f"ll_{tag}"] = {m_: float(h[m_].sum() / n) for m_ in ("M0", "R1", "M1")}
        out[f"folds_beat_R1_{tag}"] = int(np.sum(h["M1"] > h["R1"]))
        out[f"folds_beat_M0_{tag}"] = int(np.sum(h["M1"] > h["M0"]))
        out[f"folds_{tag}"] = int(len(h["n"]))
    o2 = L.order2_heldout(x, seg, segfold, k, q)
    out["dll_o2"] = float((o2["o2"].sum() - o2["o1"].sum()) / o2["n"].sum()) if len(o2["n"]) else None
    # --- per-agent MSMs
    agents = np.unique(S["seg_agent"])
    per = []
    blk = max(1, int(round(block_len_min / unit_min)))
    for a in agents:
        msk = S["seg_agent"] == a
        if len(np.unique(S["seg_day"][msk])) < 2:
            continue
        Sa = L.subset(S, msk)
        if len(Sa["x"]) - msk.sum() < 300:
            continue
        Ca = L.counts(Sa["x"], Sa["seg"], q, tau_c)
        t2a = L.its_from_C(Ca, tau_c)[0] * unit_min
        Cb, _ = L.block_counts(Sa["x"], Sa["seg"], q, tau_c, blk)
        Wa = L.boot_weights(len(Cb), R, rng)
        bs = np.array([L.its_from_C(np.tensordot(w, Cb, 1), tau_c)[0] * unit_min for w in Wa])
        bs = bs[np.isfinite(bs) & (bs > 0)]
        Csa = {kk: L.counts(Sa["x"], Sa["seg"], q, tau_c * kk) for kk in range(1, kmax + 1)}
        Ta, aa = L.T_mle(Csa[1])
        ck_a = float(L.ck_full_error(Csa, Ta, aa, L.stationary(Ta), kmax)[1:4].mean())
        M2a = L.msm_sets(Csa[1], m=2) if len(aa) > 2 else {}
        sets_a = None
        if M2a.get("m"):
            nma = [names[i] for i in aa]
            sets_a = [[nma[i] for i in range(len(nma)) if M2a["labels"][i] == kk] for kk in range(2)]
        per.append({"agent": int(a), "t2": float(t2a), "ln_se": float(np.std(np.log(bs))) if len(bs) > 5 else np.nan,
                    "n": int(len(Sa["x"])), "days": int(len(np.unique(Sa["seg_day"]))), "ck_full": ck_a,
                    "idle_share": float(np.mean(Sa["x"] == names.index("idle"))) if "idle" in names else None,
                    "sets_m2": sets_a})
    out["per_agent"] = per
    if len(per) >= 3:
        y = [np.log(p["t2"]) if p["t2"] > 0 else np.nan for p in per]
        I2, Qc = L.i_squared(y, [p["ln_se"] for p in per])
        out["I2"], out["I2_Q"] = I2, Qc
        out["ck_full_agent_median"] = float(np.median([p["ck_full"] for p in per]))
        ho = L.agent_heldout(Csk[tau_c], S["seg_agent"], segfold, k)
        out["frac_agent_beats"] = ho["frac_beats"]
        out["frac_shrink_beats"] = ho["frac_shrink"]
    else:
        out["I2"] = None
        out["frac_agent_beats"] = None
    return out


# ============================================================================ wrappers
def covariates(goal, per_agent, sm_goal):
    cov = pl.read_parquet(DATA / "covariates.parquet").filter(pl.col("goal_no") == goal)
    tot = cov.select(pl.col("n_turns").sum(), pl.col("n_error").sum(), pl.col("n_output").sum(), pl.col("present_min").sum()).row(0, named=True)
    idle = float(sm_goal.select((pl.col("coarse_min") == COARSE.index("idle")).mean()).item())
    res = {"err_share": tot["n_error"] / max(tot["n_turns"], 1), "out_rate": tot["n_output"] / max(tot["present_min"] / 60, 1e-9),
           "idle_share": idle, "n_turns": tot["n_turns"]}
    pa = cov.group_by("agent").agg(pl.col("n_turns").sum(), pl.col("n_error").sum(), pl.col("n_output").sum(), pl.col("present_min").sum())
    pad = {r["agent"]: r for r in pa.iter_rows(named=True)}
    rows = []
    for p in per_agent:
        r = pad.get(p["agent"])
        if r is None or r["n_turns"] < 50:
            continue
        p["err_share"] = r["n_error"] / r["n_turns"]
        p["out_rate"] = r["n_output"] / max(r["present_min"] / 60, 1e-9)
        rows.append(p)
    if len(rows) >= 5:
        t2s = np.array([p["t2"] for p in rows])
        res["rho_t2_err"], res["p_t2_err"] = map(float, stats.spearmanr(t2s, [p["err_share"] for p in rows]))
        res["rho_t2_out"], res["p_t2_out"] = map(float, stats.spearmanr(t2s, [p["out_rate"] for p in rows]))
        res["rho_t2_idle"], _ = map(float, stats.spearmanr(t2s, [p["idle_share"] for p in rows]))
        res["n_agents_cov"] = len(rows)
    return res


def lab_eta2(per_agent, rng, nperm=2000):
    ros = pl.read_parquet(SH / "roster.parquet")
    lab_of = dict(zip(ros["agent"].to_list(), ros["lab"].to_list()))
    ys = np.array([np.log(p["t2"]) for p in per_agent if p["t2"] > 0])
    labs = np.array([lab_of.get(p["agent"], "?") for p in per_agent if p["t2"] > 0])
    if len(ys) < 5 or len(set(labs)) < 2:
        return None, None

    def eta(v, lb):
        g = [v[lb == u] for u in np.unique(lb)]
        ssb = sum(len(z) * (z.mean() - v.mean()) ** 2 for z in g)
        sst = np.sum((v - v.mean()) ** 2)
        return ssb / sst if sst > 0 else 0

    e0 = eta(ys, labs)
    perm = [eta(ys, rng.permutation(labs)) for _ in range(nperm)]
    return float(e0), float((1 + np.sum(np.array(perm) >= e0)) / (1 + nperm))


def robustness(goal, rng, sm_goal):
    res = {}
    # 5-min windows: hard, soft counts, shifted soft estimator (tau = 1 window = 5 min)
    w5 = pl.read_parquet(DATA / "states_win5.parquet").filter(pl.col("goal_no") == goal)
    if w5.height:
        df = w5.select(pl.col("agent").cast(pl.Int16), "pt_date", pl.col("w").cast(pl.Int64).alias("order"),
                       pl.col("hard").cast(pl.Int16).alias("state"), *[pl.col(f"p_{k}") for k in range(6)]).sort("agent", "pt_date", "order")
        S5 = L.sequences_from_table(df, grid=True, soft=True, q=6)
        res["w5_hard"] = float(L.its_from_C(L.counts(S5["x"], S5["seg"], 6, 1), 1)[0] * 5)
        res["w5_hard_tau2"] = float(L.its_from_C(L.counts(S5["x"], S5["seg"], 6, 2), 2)[0] * 5)
        res["w5_soft"] = float(L.soft_its(S5["P"], S5["seg"], 1)[0] * 5)
        res["w5_shift"] = float(L.shifted_its(S5["P"], S5["seg"], 1, tau0=1)[0] * 5)
    # records: coarse turn sequence at the record lag closest to 5 minutes
    st = pl.read_parquet(DATA / "states_turn.parquet", columns=["pt_date", "goal_no", "agent", "t", "act", "coarse"]).filter(pl.col("goal_no") == goal)
    pres = sm_goal.select("pt_date", "agent").unique()
    st = st.join(pres, on=["pt_date", "agent"], how="inner")
    rate = st.filter(pl.col("coarse") >= 0).height / max(sm_goal.height, 1)
    res["records_per_min"] = rate
    stc = st.filter(pl.col("coarse") >= 0).sort("agent", "t").with_columns(pl.col("t").rank("ordinal").over(["agent", "pt_date"]).cast(pl.Int64).alias("order"))
    Sr = L.sequences_from_table(stc.select(pl.col("agent").cast(pl.Int16), "pt_date", "order", pl.col("coarse").cast(pl.Int16).alias("state")),
                                grid=True, q=6)
    tau_r = max(1, int(round(5 * rate)))
    res["rec_tau"] = tau_r
    res["rec_t2_steps"] = float(L.its_from_C(L.counts(Sr["x"], Sr["seg"], 6, tau_r), tau_r)[0])
    res["rec_t2_min"] = res["rec_t2_steps"] / rate if rate > 0 else None
    res["rec_its"] = {str(t): float(L.its_from_C(L.counts(Sr["x"], Sr["seg"], 6, t), t)[0]) for t in (1, 2, 3, 5, 8, 12, 20, 30, 50)}
    # fine act classes on records (rare classes < 1% -> other), PCCA+ at tau_r, sets descriptive
    cnt = np.bincount(st["act"].to_numpy(), minlength=len(ACT))
    rare = set(np.flatnonzero(cnt < 0.01 * cnt.sum()).tolist())
    amap = np.array([ACT.index("other") if i in rare else i for i in range(len(ACT))])
    used = sorted(set(amap[np.flatnonzero(cnt)].tolist()))
    remap = {u: i for i, u in enumerate(used)}
    sta = st.sort("agent", "t").with_columns(pl.col("t").rank("ordinal").over(["agent", "pt_date"]).cast(pl.Int64).alias("order"),
                                            pl.Series("st", [remap[amap[a]] for a in st.sort("agent", "t")["act"].to_list()]).cast(pl.Int16))
    Sa = L.sequences_from_table(sta.select(pl.col("agent").cast(pl.Int16), "pt_date", "order", pl.col("st").alias("state")), grid=True, q=len(used))
    namesA = [ACT[u] for u in used]
    tau_ra = max(1, int(round(5 * sta.height / max(sm_goal.height, 1))))
    Ma = L.msm_sets(L.counts(Sa["x"], Sa["seg"], len(used), tau_ra))
    if Ma.get("m") is None or Ma.get("labels") is None:
        Ma = L.msm_sets(L.counts(Sa["x"], Sa["seg"], len(used), tau_ra), m=2)
    if Ma.get("labels") is not None:
        nm = [namesA[i] for i in Ma["active"]]
        res["act_sets"] = [[nm[i] for i in range(len(nm)) if Ma["labels"][i] == k] for k in range(Ma["m"])]
        res["act_crispness"] = Ma["crispness"]
        res["act_t2_min"] = float(L.its_from_C(L.counts(Sa["x"], Sa["seg"], len(used), tau_ra), tau_ra)[0] / max(sta.height / max(sm_goal.height, 1), 1e-9))
    # decimated minute chain: consolidate minutes removed
    Sm = seq_from_min(sm_goal)
    keep = Sm["x"] != COARSE.index("consolidate")
    xd = Sm["x"][keep]
    xd = np.where(xd > COARSE.index("consolidate"), xd - 1, xd)
    res["decimated_t2_steps"] = float(L.its_from_C(L.counts(xd, Sm["seg"][keep], 5, TAU_C), TAU_C)[0])
    return res


def split_test(sm, date, rng, R=400):
    """t2* before vs. after a date inside a period; independent agent-day bootstraps; CI of after - before."""
    res = {}
    boots = {}
    for tag, cond in (("before", pl.col("pt_date") < date), ("after", pl.col("pt_date") >= date)):
        d = sm.filter(cond)
        S = seq_from_min(d)
        nseg = int(S["seg"].max()) + 1
        Cs = L.seg_counts(S["x"], S["seg"], 6, TAU_C, nseg)
        t2 = float(L.its_from_C(Cs.sum(0), TAU_C)[0])
        W = L.boot_weights(nseg, R, rng)
        boots[tag] = np.array([L.its_from_C(np.tensordot(w, Cs, 1), TAU_C)[0] for w in W])
        M2 = L.msm_sets(Cs.sum(0), m=2)
        nm = [COARSE[i] for i in M2["active"]]
        res[tag] = {"t2": t2, "ci": np.nanpercentile(boots[tag], [2.5, 97.5]), "days": int(d["pt_date"].n_unique()),
                    "agent_days": nseg, "sets_m2": [[nm[i] for i in range(len(nm)) if M2["labels"][i] == k] for k in range(2)],
                    "idle_share": float(np.mean(S["x"] == COARSE.index("idle")))}
    diff = boots["after"] - boots["before"]
    res["diff"] = res["after"]["t2"] - res["before"]["t2"]
    res["diff_ci"] = np.nanpercentile(diff, [2.5, 97.5])
    res["shorter_after_sig"] = bool(res["diff_ci"][1] < 0)
    return res


def verdict(p, reg):
    ck_pass = p.get("ck_max") is not None and p["ck_max"] < 0.05
    p3b = bool(p.get("n2_p95") is not None and p["t2"] > p["n2_p95"] and p["t2"] / p["n2_med"] >= 1.25)
    p8 = (p["folds_beat_R1_tauc"] >= min(4, p["folds_tauc"])) and (p["folds_beat_M0_tauc"] >= min(4, p["folds_tauc"])) \
        and p["ll_tauc"]["M1"] > p["ll_tauc"]["R1"] and p["ll_tauc"]["M1"] > p["ll_tauc"]["M0"]
    p3c = bool(p.get("m") in (2, 3) and (p.get("crispness") or 0) >= 0.75 and (p.get("sep") or 0) >= 2)
    s2 = p.get("sets_m2") or []
    p3d = any(set(s) <= {"idle", "consolidate"} and "idle" in s for s in s2)
    p5 = None if p.get("I2") is None else bool(p["I2"] >= 0.5)
    p6 = bool((p.get("delta_max") or 0) >= 0.1 and p.get("delta_sig"))
    p7 = bool(p.get("ep_n2_p95") is not None and p["ep"] > p["ep_n2_p95"] and (p.get("ep_macro_share") is not None and p["ep_macro_share"] < 0.5))
    if ck_pass and p3b and p8:
        v = "supported"
    elif (not ck_pass) and (not p3b):
        v = "failed"
    else:
        v = "mixed"
    reasons = []
    if not ck_pass:
        reasons.append("CK fails")
    if not p3b:
        reasons.append("t2* not beyond the sojourn null")
    if not p8:
        reasons.append("MSM does not beat R1/M0")
    return {"verdict": v + (f" ({'; '.join(reasons)})" if reasons else ""), "ck_pass": ck_pass, "p3b": p3b, "p8": bool(p8),
            "p3c": p3c, "p3d": bool(p3d), "p5": p5, "p6": p6, "p7": p7}


def figure(goal, p, outdir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.4))
    taus = np.array(p["taus"]) * p["unit_min"]
    for k, c in zip(range(3), ("#1f4e79", "#4f8fc0", "#9cc3e4")):
        y = np.array([p["its"][str(t)][k] for t in p["taus"]])
        lo = np.array([p["its_ci"][str(t)][0][k] for t in p["taus"]])
        hi = np.array([p["its_ci"][str(t)][1][k] for t in p["taus"]])
        ax[0].plot(taus, y, "o-", color=c, ms=3, label=f"t{k + 2}")
        ax[0].fill_between(taus, lo, hi, color=c, alpha=0.25, lw=0)
    ax[0].plot(taus, taus, "k:", lw=0.8)
    if p.get("n2_med"):
        ax[0].axhline(p["n2_med"], color="#c0504d", lw=1, ls="--", label="N2 median t2 (τc)")
    ax[0].axvline(p["tau_c"] * p["unit_min"], color="grey", lw=0.6)
    ax[0].set_xlabel("lag τ (active min)")
    ax[0].set_ylabel("implied timescale (min)")
    ax[0].set_yscale("log")
    ax[0].legend(fontsize=7, frameon=False)
    ax[0].set_title(f"G{goal:02d}: ITS (non-reversible MLE)", fontsize=9)
    if p.get("ck_est") is not None:
        est, pred = np.array(p["ck_est"], dtype=float), np.array(p["ck_pred"], dtype=float)
        kk = np.arange(1, est.shape[0] + 1) * p["tau_c"] * p["unit_min"]
        for A in range(est.shape[1]):
            lbl = "+".join(p["sets_m"][A])[:28]
            ax[1].plot(kk, est[:, A], "o", ms=4, color=f"C{A}", label=f"{lbl} (data)")
            ax[1].plot(kk, pred[:, A], "-", color=f"C{A}", lw=1)
        ax[1].set_xlabel("k·τc (min)")
        ax[1].set_ylabel("P(stay in set)")
        ax[1].set_title(f"CK test (m = {p['m']}); max |Δ| = {p['ck_max']:.3f}", fontsize=9)
        ax[1].legend(fontsize=6, frameon=False)
    fig.tight_layout()
    outdir.mkdir(parents=True, exist_ok=True)
    fig.savefig(outdir / "its_ck.pdf")
    plt.close(fig)


def run_goal(goal, seed=20261003):
    t0 = time.time()
    rng = np.random.default_rng(seed + goal)
    reg = PERIODS[goal]
    sm = load_min(goal)
    days = sorted(set(sm["pt_date"].to_list()))
    assert_not_holdout(goal, days)
    S = seq_from_min(sm)
    p = analyze(S, COARSE, 1.0, TAUS_MIN, TAU_C, rng, heavy=True)
    p["covariates"] = covariates(goal, p["per_agent"], sm)
    p.update({k: v for k, v in p["covariates"].items() if k in ("err_share", "out_rate", "idle_share")})
    p["lab_eta2"], p["lab_eta2_p"] = lab_eta2(p["per_agent"], rng)
    # post hoc (not pre-registered): idle runs at the day boundaries
    xt, st_, frac = L.trim_boundary_state(S["x"], S["seg"], COARSE.index("idle"))
    p["idle_boundary_frac"] = frac
    p["t2_trim_boundary_idle"] = float(L.its_from_C(L.counts(xt, st_, 6, TAU_C), TAU_C)[0])
    nn = []
    for _ in range(30):
        xn, _m = L.null_sojourn(xt, st_, rng)
        nn.append(L.its_from_C(L.counts(xn, st_, 6, TAU_C), TAU_C)[0])
    p["trim_n2_med"], p["trim_n2_p95"] = float(np.nanmedian(nn)), float(np.nanpercentile(nn, 95))
    Mt = L.msm_sets(L.counts(xt, st_, 6, TAU_C), m=2)
    nmt = [COARSE[i] for i in Mt["active"]]
    p["trim_sets_m2"] = [[nmt[i] for i in range(len(nmt)) if Mt["labels"][i] == k] for k in range(2)]
    p["trim_its"] = {str(t): float(L.its_from_C(L.counts(xt, st_, 6, t), t)[0]) for t in (1, 5, 15, 30)}
    for h in (1, 2):
        Sh = seq_from_min(sm, half=h)
        p[f"t2_half{h}"] = float(L.its_from_C(L.counts(Sh["x"], Sh["seg"], 6, TAU_C), TAU_C)[0])
    p.update(robustness(goal, rng, sm))
    extra = {}
    if goal == 51:  # O10: calendar weeks
        wk = sm.with_columns(pl.col("pt_date").str.to_date().dt.truncate("1w").cast(pl.Utf8).alias("week"))
        weeks = []
        for (w,), d in sorted(wk.group_by("week"), key=lambda z: z[0]):
            if d["pt_date"].n_unique() < 2:
                continue
            Sw = seq_from_min(d.drop("week"))
            pw = analyze(Sw, COARSE, 1.0, [1, 5, 10], TAU_C, rng, R=100, nnull=30, heavy=False)
            weeks.append({"week": w, "days": int(d["pt_date"].n_unique()), "agents": pw["n_agents"], "t2": pw["t2"],
                          "t2_ci": pw["t2_ci"], "n2_med": pw.get("n2_med"), "n2_p95": pw.get("n2_p95"), "ck_max": pw.get("ck_max"),
                          "sets_m2": pw.get("sets_m2"), "I2": pw.get("I2")})
        extra["weeks"] = weeks
    NE_SPLITS = {21: ("NE07", "2025-12-04"), 30: ("NE10", "2026-02-10"), 38: ("NE17", "2026-04-14")}
    if goal in NE_SPLITS:
        ne, date = NE_SPLITS[goal]
        extra["ne_split"] = split_test(sm, date, rng) | {"ne": ne, "date": date}
    p["extra"] = extra
    v = verdict(p, reg)
    out = {"goal": goal, "regime": reg, "verdict": v, "primary": p, "secs": time.time() - t0}
    od = DATA / f"G{goal:02d}"
    od.mkdir(parents=True, exist_ok=True)
    (od / "result.json").write_text(json.dumps(L.jsonable(out)))
    figure(goal, p, CARD / "goalperiod-subhypotheses" / f"G{goal:02d}" / "figures")
    return goal, v["verdict"], round(p["t2"], 2), round(time.time() - t0, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--periods", nargs="*", type=int)
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    goals = a.periods or list(PERIODS)
    goals = sorted(goals, key=lambda g: -1 if g == 51 else g)  # start the big one first
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        for r in ex.map(run_goal, goals):
            print(r, flush=True)


if __name__ == "__main__":
    main()
