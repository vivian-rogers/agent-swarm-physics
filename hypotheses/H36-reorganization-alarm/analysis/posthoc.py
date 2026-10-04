"""H36 post hoc analyses (written after seeing evaluate.py's results; labelled post hoc everywhere; non-holdout only).

PH1  Day -1 lead: AUC of day -1 vs placebo days and vs 'Friday' placebos (last active day before a >= 2-day gap).
PH2  What the content signal is: content statistics recomputed after removing a *linear within-day trend* (alignment
     energy e(w) detrended for C_cont; the swarm's common linear trajectory removed from agent-centered vectors for
     I_cont and chi_cont). If the goal-change signal vanishes, the content alarm sees a monotone within-day drift (the
     post-kickoff ordering/relaxation, a field ramp), not a change in co-fluctuation.
PH3  Activity confounds: Z_act vs |change in day-present n|, |change in log day length| and returns from >= 4-day gaps;
     goal-change AUC of Z_act and Z_phys without events that coincide with such sampling changes.
PH4  Candidate operator rules (for the confirmatory script only; their real-data numbers here are in-sample).

Usage: uv run python hypotheses/H36-reorganization-alarm/analysis/posthoc.py
Output: data/processed/H36-reorganization-alarm/posthoc.json
"""
from __future__ import annotations

import json
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h36lib as L  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

EMB = L.SH / "embeddings"


def content_detrended(V, M, rng, n_surr=L.N_SURR):
    keep = M.sum(1) >= 3
    V, M = V[keep].astype(np.float64), M[keep]
    n, W = M.shape
    if n < L.MIN_PRESENT or W < 4:
        return {}
    V = np.where(M[..., None], V, 0.0)
    mu = V.sum(1, keepdims=True) / M.sum(1)[:, None, None]
    Z = np.where(M[..., None], V - mu, 0.0)
    w = np.arange(W, dtype=float)

    def stats(Vx, Zx):
        # remove the common linear trend of the agent-centered vectors (fit on windows with >= 1 agent)
        cnt = M.sum(0)
        mz = np.where(cnt[:, None] > 0, Zx.sum(0) / np.maximum(cnt, 1)[:, None], 0.0)  # W x d
        okw = cnt > 0
        X = np.c_[np.ones(okw.sum()), w[okw]]
        beta, *_ = np.linalg.lstsq(X, mz[okw], rcond=None)
        trend = np.c_[np.ones(W), w] @ beta
        Zd = np.where(M[..., None], Zx - trend[None], 0.0)
        Q = np.einsum("iwd,jwd->ij", Zd, Zd)
        dg = np.sqrt(np.clip(np.diag(Q), 1e-12, None)); Qn = Q / np.outer(dg, dg)
        i_c = -0.5 * L._ridge_logdet(Qn, 1e-2) / (n * (n - 1) / 2)
        chi = Qn.sum() / n
        G = np.einsum("iwd,jwd->wij", Vx, Vx)
        c = M.sum(0).astype(float)
        S_w = (G.sum((1, 2)) - c) / 2.0; npw = c * (c - 1) / 2; ok = npw > 0
        if ok.sum() >= 4:
            e = -S_w[ok] / npw[ok]
            Xe = np.c_[np.ones(ok.sum()), w[ok]]
            be, *_ = np.linalg.lstsq(Xe, e, rcond=None)
            cc = (e - Xe @ be).var() * npw[ok].mean()
        else:
            cc = np.nan
        return np.array([i_c, chi, cc])
    obs = stats(V, Z)
    pres = [np.flatnonzero(M[i]) for i in range(n)]
    sur = np.empty((n_surr, 3))
    for k in range(n_surr):
        Vs = np.zeros_like(V); Zs = np.zeros_like(Z)
        for i in range(n):
            p = pres[i]; q = rng.permutation(p)
            Vs[i, p] = V[i, q]; Zs[i, p] = Z[i, q]
        sur[k] = stats(Vs, Zs)
    return {nm + "_dt": obs[j] - np.nanmean(sur[:, j]) for j, nm in enumerate(L.CONT_STATS)}


def main():
    rng = np.random.default_rng(L.SEED + 7)
    d = pl.read_parquet(L.OUT / "day_stats.parquet").sort("aday")
    s = pl.read_parquet(L.OUT / "scores.parquet").sort("aday")
    et = pl.read_parquet(L.OUT / "event_table.parquet")
    cal = pl.read_parquet(L.SH / "calendar.parquet").sort("pt_date").with_row_index("aday").with_columns(pl.col("aday").cast(pl.Int32))
    dts = cal["pt_date"].str.to_date()
    gap_after = (dts.shift(-1) - dts).dt.total_days()
    fri = dict(zip(cal["aday"].to_list(), (gap_after >= 3).fill_null(False).to_list()))
    aday = s["aday"].to_numpy(); pos = {int(a): i for i, a in enumerate(aday)}
    placebo = s["placebo"].to_numpy()
    friday = placebo & np.array([fri.get(int(a), False) for a in aday])
    out = {}
    goal = et.filter((pl.col("cls") == "goal") & (pl.col("n_scored") > 0))

    def col(k):
        return s[k].to_numpy().astype(float)

    # ---- PH1 lead
    ph1 = {}
    for k in ["Z_phys", "Z_cont", "Z_act", "R1"]:
        dm1 = goal[f"{k}_o-1"].to_numpy().astype(float)
        d0 = goal[f"{k}_o0"].to_numpy().astype(float)
        ph1[k] = {"auc_dm1_vs_placebo": L.auc(dm1, col(k)[placebo]), "auc_dm1_vs_friday": L.auc(dm1, col(k)[friday]),
                  "auc_d0_vs_placebo": L.auc(d0, col(k)[placebo]),
                  "dm1_alarm_rate": float(np.mean(dm1[np.isfinite(dm1)] >= 2)), "n_dm1": int(np.isfinite(dm1).sum()),
                  "friday_far": float(np.mean(col(k)[friday] >= 2)), "n_friday": int(friday.sum()),
                  "auc_dm1_ci": L.auc_ci(dm1, col(k)[placebo], rng, 1000)}
    out["PH1_lead"] = ph1

    # ---- PH2 detrended content
    days = d["pt_date"].to_list()
    aw = pl.read_parquet(EMB / "agent_win30.parquet").filter(pl.col("pt_date").is_in(days) & ~pl.col("holdout"))
    vec = np.load(EMB / "agent_win30_vec.npy", mmap_mode="r")
    regs = dict(zip(d["pt_date"].to_list(), d["regime"].to_list()))
    Wh = {r: L.load_whitener(r, 32) for r in ["I", "II", "III"]}
    rows = []
    for (dd,), w in aw.group_by(["pt_date"]):
        agents = sorted(set(w["agent"].to_list())); Wn = int(w["win30"].max()) + 1
        V = np.zeros((len(agents), Wn, vec.shape[1]), np.float32); M = np.zeros((len(agents), Wn), bool)
        ia = {a_: i for i, a_ in enumerate(agents)}
        for ag, wi, gid in w.select("agent", "win30", "gid").iter_rows():
            V[ia[ag], wi] = vec[gid]; M[ia[ag], wi] = True
        Vw = Wh[regs[dd]](V.reshape(-1, V.shape[-1])).reshape(len(agents), Wn, 32)
        Vw /= np.clip(np.linalg.norm(Vw, axis=2, keepdims=True), 1e-9, None)
        r = content_detrended(Vw, M, np.random.default_rng([L.SEED, zlib.crc32(dd.encode())]))
        r["pt_date"] = dd
        rows.append(r)
    dt_ = pl.DataFrame(rows, infer_schema_length=None)
    d2 = d.join(dt_, on="pt_date", how="left").sort("aday")
    Zd = {}
    for st in L.CONT_STATS:
        Zd[st] = L.trailing_z(d2[st + "_dt"].to_numpy().astype(float))
    Zc_dt = np.nanmean(np.vstack([Zd[k] for k in L.CONT_STATS]), 0)
    ph2 = {}
    g0 = np.array([pos.get(int(a), -1) for a in goal["aday0"].to_list()])
    g0 = g0[g0 >= 0]
    for nm, arr in [("Z_cont_detrended", Zc_dt), ("Z_cont", col("Z_cont"))] + [(k + "_dt_z", Zd[k]) for k in L.CONT_STATS] + \
            [("z_" + k, col("z_" + k)) for k in L.CONT_STATS]:
        ph2[nm] = {"auc_d0": L.auc(arr[g0], arr[placebo]), "auc_ci": L.auc_ci(arr[g0], arr[placebo], rng, 1000),
                   "mean_d0": float(np.nanmean(arr[g0])), "far_day": float(np.mean(arr[placebo] >= 2)),
                   "hit_d0": float(np.mean(np.nan_to_num(arr[g0], nan=-9) >= 2))}
    out["PH2_detrended_content"] = ph2

    # ---- PH3 activity confounds
    n = d["n_present"].to_numpy().astype(float); T = d["T_act"].to_numpy().astype(float)
    dn = np.r_[np.nan, np.abs(np.diff(n))]; dT = np.r_[np.nan, np.abs(np.diff(np.log(T)))]
    gap = np.r_[np.nan, np.diff(aday)] if False else None
    cg = d["gap_days"].to_numpy().astype(float)
    big_gap = np.r_[False, np.diff(aday) > 1] | (cg >= 4)  # previous active day held out, or a >= 4-day break
    samp = (dn >= 2) | (dT >= np.log(1.25)) | big_gap
    za = col("Z_act")
    from scipy.stats import spearmanr, mannwhitneyu
    ok = np.isfinite(za) & np.isfinite(dn) & np.isfinite(dT)
    ph3 = {"spearman_Zact_dn": float(spearmanr(za[ok], dn[ok]).statistic), "spearman_Zact_dT": float(spearmanr(za[ok], dT[ok]).statistic),
           "Zact_alarm_rate_sampling_change": float(np.mean(za[np.isfinite(za) & samp] >= 2)),
           "Zact_alarm_rate_no_change": float(np.mean(za[np.isfinite(za) & ~samp] >= 2)),
           "n_sampling_change_days": int((np.isfinite(za) & samp).sum()), "n_no_change_days": int((np.isfinite(za) & ~samp).sum()),
           "mwu_p": float(mannwhitneyu(za[np.isfinite(za) & samp], za[np.isfinite(za) & ~samp]).pvalue)}
    clean = np.array([not samp[pos[int(a)]] if int(a) in pos else False for a in goal["aday0"].to_list()])
    gc = goal.filter(pl.Series(clean))
    for k in ["Z_phys", "Z_act", "Z_cont", "R1"]:
        ph3[f"goal_no_sampling_change_{k}"] = {"n": gc.height, "auc_d0": L.auc(gc[f"{k}_d0"].to_numpy().astype(float), col(k)[placebo & ~samp]),
                                               "hit": float(np.mean(gc[f"{k}_hit"].fill_null(False).to_numpy()))}
    ph3["goal_events_with_sampling_change"] = goal.filter(~pl.Series(clean))["ref"].to_list()
    out["PH3_activity_confounds"] = ph3

    # ---- PH4 candidate operator rules (in-sample)
    def rule_eval(score_fn, name):
        sc = score_fn()
        hits, wins = [], []
        for c in goal["aday0"].to_list():
            v = [sc[pos[c + o]] for o in (-1, 0, 1) if (c + o) in pos]
            hits.append(any(x for x in v))
        pc = aday[placebo]
        for c in pc:
            v = [sc[pos[c + o]] for o in (-1, 0, 1) if (c + o) in pos]
            wins.append(any(x for x in v))
        return {"rule": name, "hit": float(np.mean(hits)), "far_win": float(np.mean(wins)), "far_day": float(np.mean(sc[placebo]))}
    zc, r1, zp = col("Z_cont"), col("R1"), col("Z_phys")
    ph4 = [rule_eval(lambda: zp >= 2.0, "Z_phys >= 2.0 (pre-registered)"),
           rule_eval(lambda: zc >= 2.0, "Z_cont >= 2.0"),
           rule_eval(lambda: zc >= 1.5, "Z_cont >= 1.5"),
           rule_eval(lambda: r1 >= 2.5, "R1 >= 2.5"),
           rule_eval(lambda: r1 >= 3.0, "R1 >= 3.0"),
           rule_eval(lambda: (r1 >= 3.0) | (zc >= 2.0), "R1 >= 3.0 or Z_cont >= 2.0"),
           rule_eval(lambda: (r1 >= 2.5) | (zc >= 2.0), "R1 >= 2.5 or Z_cont >= 2.0")]
    out["PH4_rules_in_sample"] = ph4
    # all-class view of the recommended rule
    allp = et.filter(pl.col("cls").is_in(["goal", "room", "scaffold", "roster"]) & (pl.col("n_scored") > 0))
    byc = {}
    for cls in ["goal", "room", "scaffold", "roster"]:
        sub = allp.filter(pl.col("cls") == cls)
        hs = []
        for c in sub["aday0"].to_list():
            v = [((r1[pos[c + o]] >= 3.0) or (zc[pos[c + o]] >= 2.0)) for o in (-1, 0, 1) if (c + o) in pos]
            hs.append(any(v))
        byc[cls] = {"n": sub.height, "hit": float(np.mean(hs)) if hs else None}
    out["PH4_rule_R1ge3_or_Zcontge2_by_class"] = byc
    (L.OUT / "posthoc.json").write_text(json.dumps(out, indent=1, default=float))
    dt_.write_parquet(L.OUT / "posthoc_content_detrended.parquet", compression="zstd")
    L.write_provenance("hypotheses/H36-reorganization-alarm/analysis/posthoc.py", ["(H36 day_stats, scores, event_table)", "embeddings/agent_win30"],
                       {"note": "post hoc PH1-PH4, non-holdout only", "seed": L.SEED + 7})
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
