"""H34 exploratory round 1 on real data (non-holdout): per-period statistics, verdicts, cross-period link, forecasts.

  uv run python hypotheses/H34-idea-cascades/analysis/explore.py

Reads data/processed/H34-idea-cascades/G<NN>/ (scheme/build.py). Writes results/ :
  period_table.parquet   one row per period x class (ALL, U, D, N, W)
  forecast_days.parquet  day-ahead forecast scores per period-day
  periods.json           per-period rows for the G cards
  summary.json           cross-period tests (P1-P7), forecast-rule table
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import special, stats  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h34stats as S  # noqa: E402
import h34core as C  # noqa: E402

DATA = C.OUT
RES = DATA / "results"
ROOT = C.ROOT
CLS = {0: "U", 1: "D", 2: "N", 3: "W"}
N_WORKERS = 2
MIN_NONSEED = 20
MIN_TREES_SHAPE = 50
MIN_TRAIN_TREES, MIN_TEST_TREES = 30, 20


def gains() -> dict[int, dict]:
    t3 = pl.read_parquet(ROOT / "data/processed/H03-self-excited-criticality/period_table.parquet").filter(pl.col("set") == "TALK")
    out = {int(r["goal_no"]): {"n03": float(r["n"]), "n03_lo": r.get("n_boot_lo"), "n03_hi": r.get("n_boot_hi")}
           for r in t3.iter_rows(named=True)}
    e = pl.read_parquet(ROOT / "data/processed/H19-loop-gain-collapse/estimates.parquet")
    for r in e.filter(pl.col("method") == "H19.geq_talk").iter_rows(named=True):
        out.setdefault(int(r["goal_no"]), {})["g19"] = float(r["value"])
    for r in e.filter(pl.col("method") == "H19.geq_active").iter_rows(named=True):
        out.setdefault(int(r["goal_no"]), {})["g19a"] = float(r["value"])
    h25 = ROOT / "data/processed/H25-criticality-dial"
    out["_h25_available"] = bool(h25.exists() and any(h25.glob("**/*.parquet")))
    return out


# ------------------------------------------------------------------------------------------- per-class statistics
def boot_R(fu: pl.DataFrame, B=1000, seed=0):
    g = (fu.with_columns(((pl.col("status") == 1) & (pl.col("parent") >= 0)).cast(pl.Int64).alias("kid"))
         .group_by("idea").agg(pl.col("kid").sum(), pl.len().alias("nodes")))
    return S.cluster_boot_ratio(g["kid"].to_numpy().astype(float), g["nodes"].to_numpy().astype(float), B=B, seed=seed)


def boot_Rk(fu: pl.DataFrame, B=25, seed=0):
    """(R, k) pairs from idea-cluster bootstrap samples (for forecast parameter uncertainty)."""
    rng = np.random.default_rng(seed)
    ideas = fu["idea"].to_numpy()
    off = fu["offspring"].to_numpy()
    kid = ((fu["status"] == 1) & (fu["parent"] >= 0)).to_numpy()
    u, inv = np.unique(ideas, return_inverse=True)
    groups = [np.where(inv == i)[0] for i in range(len(u))] if len(u) < 20000 else None
    out = []
    for _ in range(B):
        if groups is not None:
            sel = np.concatenate([groups[j] for j in rng.integers(0, len(u), len(u))])
        else:  # large periods: resample ideas via weights (multinomial counts)
            w = rng.multinomial(len(u), np.full(len(u), 1 / len(u)))[inv]
            sel = np.repeat(np.arange(len(ideas)), w)
        R = kid[sel].mean()
        k = S.fit_offspring(off[sel])["k"]
        out.append((R, k))
    return out


def class_stats(fu, tr, ar, jt, rx, N, cls_name, seed=0, full=True):
    d = dict(cls=cls_name, ideas=int(fu["idea"].n_unique()) if fu.height else 0, nodes=fu.height, trees=tr.height)
    if fu.height == 0:
        return d
    nonseed = fu.filter(pl.col("status") > 0)
    d["nonseed"] = nonseed.height
    d["exposed_frac"] = float((nonseed["status"] == 1).mean()) if nonseed.height else np.nan
    R, lo, hi = boot_R(fu, B=1000, seed=seed)
    d.update(R=R, R_lo=lo, R_hi=hi)
    fo = S.fit_offspring(fu["offspring"].to_numpy())
    d["k"] = fo["k"]
    sizes = tr["size"].to_numpy()
    d.update(p2=float((sizes >= 2).mean()), p3=float((sizes >= 3).mean()), p5=float((sizes >= 5).mean()),
             smax=int(sizes.max()), mean_size=float(sizes.mean()))
    reach = fu.group_by("idea").len()["len"].to_numpy()
    d.update(reach_p2=float((reach >= 2).mean()), reach_p3=float((reach >= 3).mean()), reach_p5=float((reach >= 5).mean()),
             reach_max=int(reach.max()))
    rt = tr["root_type"].to_numpy()
    d.update(root_invented=float((rt == 0).mean()), root_human=float((rt == 1).mean()), root_field=float((rt == 2).mean()))
    roots = fu.filter(pl.col("gen") == 0)
    kids_ = fu.filter(pl.col("gen") > 0)
    d.update(off_root=float(roots["offspring"].mean()) if roots.height else np.nan,
             off_nonroot=float(kids_["offspring"].mean()) if kids_.height else np.nan)
    unc = tr.filter(~pl.col("censored"))
    if unc.height:
        ideas_unc = set(unc["idea"].to_list())
        fu_unc = fu.filter(pl.col("idea").is_in(list(ideas_unc)))
        d["R_uncensored"] = float((((fu_unc["status"] == 1) & (fu_unc["parent"] >= 0)).sum()) / max(fu_unc.height, 1))
    ex = fu.filter(pl.col("status") == 1)
    d.update(lag_median=float(ex["lag_turns"].median()) if ex.height else np.nan,
             lag1_frac=float((ex["lag_turns"] == 1).mean()) if ex.height else np.nan,
             ksrc_median=float(ex["k_src"].median()) if ex.height else np.nan)
    if not full:
        return d
    if tr.height >= 10:
        pf = S.powerlaw_fits(np.minimum(sizes, N), max(N, int(sizes.max())))
        d.update(tau_app=pf["tau_app"], tau=pf["tau"], tau_lo=pf["tau_lo"], tau_hi=pf["tau_hi"], s_c=pf["s_c"],
                 lr_15pure=pf["lr_15pure_vs_cut"], p_15pure=float(stats.chi2.sf(max(pf["lr_15pure_vs_cut"], 0), 1)))
        smax_fit = max(N, int(sizes.max()))
        d["R_size"] = S.size_mle(np.minimum(sizes, smax_fit), smax_fit, k=min(fo["k"], S.K_INF))["R"]
    if tr.height >= MIN_TREES_SHAPE:
        bRk = boot_Rk(fu, B=25, seed=seed)
        Nfit = max(N, int(sizes.max()))
        cdf, band, R0 = S.predict_tail_fngw(R, fo["k"], Nfit, tr.height, boot_Rk=bRk, B=1000, n_param=25, seed=seed)
        cdf_g, band_g = S.predict_tail(R, fo["k"], Nfit, tr.height, boot_Rk=bRk, B=1000, seed=seed)
        d.update(fn_R0=R0, fn_pred3=cdf[3], fn_pred5=cdf[5], fn_lo3=band[3][0], fn_hi3=band[3][1], fn_lo5=band[5][0],
                 fn_hi5=band[5][1], fn_cover3=bool(band[3][0] <= d["p3"] <= band[3][1]),
                 fn_cover5=bool(band[5][0] <= d["p5"] <= band[5][1]),
                 gw_pred3=cdf_g[3], gw_cover3=bool(band_g[3][0] <= d["p3"] <= band_g[3][1]),
                 gw_cover5=bool(band_g[5][0] <= d["p5"] <= band_g[5][1]))
        d["shape_pass"] = bool(d["fn_cover3"] and d["fn_cover5"])
    if jt.height:
        j = S.jitter_test(jt["obs_exposed"].to_numpy(), jt["p_exp_1h"].to_numpy(), jt["idea"].to_numpy(), B=1000, seed=seed)
        d.update(jit_obs=j["obs_frac"], jit_null=j["null_frac"], jit_excess=j["excess"], jit_lo=j["lo"], jit_hi=j["hi"],
                 jit_p=j["p_boot"], first_obs=float(jt["obs_first_turn"].mean()), first_null=float(jt["p_first_1h"].mean()))
    if ar.height:
        dr = S.dose_response(ar, B=500, kcol="krbin", seed=seed)
        dc = S.dose_response(ar, B=200, kcol="kbin", seed=seed)
        hr10, (l10, h10) = dr["hr10"], dr["hr10_ci"]
        d.update(h0=dr["h"][0], h1=dr["h"][1], h2=dr["h"][2], h3=dr["h"][3], turns_k=dr["turns"], adopts_k=dr["adopts"],
                 hr10=hr10, hr10_lo=l10, hr10_hi=h10, hr21=dr["hr21"], hr21_lo=dr["hr21_ci"][0], hr21_hi=dr["hr21_ci"][1],
                 hr32=dr["hr32"], hr21_cum=dc.get("hr21", np.nan), n_k0_adopts=dr["n_k0_adopts"],
                 R_c=R * max(0.0, 1 - 1 / hr10) if (np.isfinite(hr10) and hr10 > 0) else (R if hr10 == np.inf else np.nan),
                 R_c_lo=R * max(0.0, 1 - 1 / l10) if (np.isfinite(l10) and l10 > 0) else 0.0,
                 R_c_hi=R * max(0.0, 1 - 1 / h10) if (np.isfinite(h10) and h10 > 0) else (R if h10 == np.inf else np.nan))
        d["contagion_pass"] = bool(np.isfinite(l10) and l10 > 1)
    if rx.height:
        ne, na, ue, ua = (float(rx[c].sum()) for c in ("n_exposed", "n_exposed_adopt", "n_unexposed", "n_unexposed_adopt"))
        d.update(rx_p_exp=na / ne if ne else np.nan, rx_p_unexp=ua / ue if ue else np.nan, rx_n_unexp=ue, rx_n_unexp_adopt=ua)
        if ue >= 100 and ua > 0 and ne > 0:
            # idea-bootstrap CI of the ratio
            rng = np.random.default_rng(seed)
            a = rx.select("n_exposed", "n_exposed_adopt", "n_unexposed", "n_unexposed_adopt").to_numpy().astype(float)
            bs = []
            for _ in range(500):
                s = a[rng.integers(0, len(a), len(a))].sum(0)
                if s[3] > 0 and s[0] > 0:
                    bs.append((s[1] / s[0]) / (s[3] / s[2]))
            d.update(rx_ratio=(na / ne) / (ua / ue), rx_ratio_lo=float(np.percentile(bs, 2.5)), rx_ratio_hi=float(np.percentile(bs, 97.5)))
        elif ue >= 100 and ne > 0:
            d.update(rx_ratio=np.inf, rx_ratio_lo=np.nan, rx_ratio_hi=np.nan)
    return d


# ------------------------------------------------------------------------------------------- day-ahead forecasts
def binom_pmf(N, eps):
    s = np.arange(1, N + 1)
    return stats.binom.pmf(s - 1, N - 1, min(max(eps, 1e-9), 1 - 1e-9))


def betabinom_fit(sizes, N):
    x = np.minimum(sizes, N) - 1
    m = x.mean() / (N - 1)
    v = x.var() / (N - 1) ** 2
    from scipy import optimize

    def nll(th):
        a, b = math.exp(th[0]), math.exp(th[1])
        return -np.sum(stats.betabinom.logpmf(x, N - 1, a, b))
    m = min(max(m, 1e-4), 0.99)
    r = optimize.minimize(nll, x0=[math.log(m * 2), math.log((1 - m) * 2)], method="Nelder-Mead")
    a, b = math.exp(r.x[0]), math.exp(r.x[1])
    return stats.betabinom.pmf(np.arange(N), N - 1, a, b)


def forecast_days(g, fu, tr, N, n03, seed=0):
    rows = []
    days = sorted(tr["day"].unique().to_list())
    Nf = max(N, int(tr["size"].max()))
    for d in days[1:]:
        trn, tst = tr.filter(pl.col("day") < d), tr.filter(pl.col("day") == d)
        fu_trn = fu.filter(pl.col("day") < d)
        if trn.height < MIN_TRAIN_TREES or tst.height < MIN_TEST_TREES or (fu_trn["status"] > 0).sum() < 10:
            continue
        # the training forest: trees rooted before d (their nodes may extend to later days: use trees, not node days)
        ids = trn.select("idea", "tree")
        fu_t = fu.join(ids.rename({"tree": "tree"}), on=["idea", "tree"], how="inner")
        R = float((((fu_t["status"] == 1) & (fu_t["parent"] >= 0)).sum()) / fu_t.height)
        k = S.fit_offspring(fu_t["offspring"].to_numpy())["k"]
        s_tr, s_te = np.minimum(trn["size"].to_numpy(), Nf), np.minimum(tst["size"].to_numpy(), Nf)
        n = len(s_te)
        bRk = boot_Rk(fu_t, B=10, seed=seed + d)
        cdf, band, R0 = S.predict_tail_fngw(R, k, Nf, n, boot_Rk=bRk, B=600, n_param=10, seed=seed + d)
        p_fn, _ = S.fngw_pmf(R, k, Nf, seed=seed + d)
        p_gw = S.nb_gw_pmf_trunc(R, k, Nf)
        emp = np.bincount(s_tr, minlength=Nf + 1)[1:Nf + 1] + 1.0
        p_emp = emp / emp.sum()
        p_bin = binom_pmf(Nf, (s_tr - 1).mean() / (Nf - 1))
        p_bb = betabinom_fit(s_tr, Nf)
        p_h03 = S.fngw_pmf(min(n03, 0.999), S.K_INF, Nf, seed=seed + d)[0] if n03 is not None and np.isfinite(n03) else None

        def ls(p):
            p = np.maximum(np.asarray(p, float), 1e-9)
            p = p / p.sum()
            return float(np.log(p[s_te - 1]).sum())
        o2, o3 = float((s_te >= 2).mean()), float((s_te >= 3).mean())
        rows.append(dict(goal=g, day=int(d), n_test=n, n_train=trn.height, R_train=R, k_train=k, R0=R0,
                         obs_p2=o2, obs_p3=o3, pred_p2=cdf[2], pred_p3=cdf[3], lo2=band[2][0], hi2=band[2][1],
                         lo3=band[3][0], hi3=band[3][1], cover2=bool(band[2][0] <= o2 <= band[2][1]),
                         cover3=bool(band[3][0] <= o3 <= band[3][1]),
                         ls_fngw=ls(p_fn), ls_gwnb=ls(p_gw), ls_emp=ls(p_emp), ls_binom=ls(p_bin), ls_betabin=ls(p_bb),
                         ls_h03=ls(p_h03) if p_h03 is not None else np.nan))
    return rows


# ------------------------------------------------------------------------------------------- per period
def run_period(task):
    g, gn = task
    t0 = time.time()
    od = DATA / f"G{g:02d}"
    meta = json.loads((od / "meta.json").read_text())
    fu = pl.read_parquet(od / "first_uses.parquet")
    tr = pl.read_parquet(od / "trees.parquet")
    ar = pl.read_parquet(od / "atrisk.parquet")
    jt = pl.read_parquet(od / "jitter.parquet")
    rx = pl.read_parquet(od / "roomx.parquet")
    N = int(meta["N_room"])
    out = []
    allst = class_stats(fu, tr, ar, jt, rx, N, "ALL", seed=g)
    allst.update(goal=g, N_room=N, n_days=meta["n_days"], n_agent_msgs=meta["n_agent_msgs"], n_agents=meta["n_agents"],
                 n_rooms_active=meta["n_rooms_active"], s_fallback_frac=meta["s_fallback_frac"],
                 n03=gn.get("n03"), g19=gn.get("g19"), g19a=gn.get("g19a"))
    out.append(allst)
    for c, nm in CLS.items():
        st = class_stats(fu.filter(pl.col("cls") == c), tr.filter(pl.col("cls") == c), ar.filter(pl.col("cls") == c),
                         jt.filter(pl.col("cls") == c), rx.filter(pl.col("cls") == c), N, nm, seed=g + 100 * c,
                         full=True)
        st.update(goal=g, N_room=N)
        out.append(st)
    fc = forecast_days(g, fu, tr, N, gn.get("n03"), seed=g)
    print(f"G{g:02d}: {time.time() - t0:.0f}s, R {allst.get('R', np.nan):.3f}, HR10 {allst.get('hr10', np.nan):.2f}, "
          f"{len(fc)} forecast days", flush=True)
    return out, fc


def verdict(r: dict) -> str:
    if r.get("nonseed", 0) < MIN_NONSEED:
        return "n/a"
    if r.get("R_lo", 0) >= 1:
        return "failed"
    cp = bool(r.get("contagion_pass", False))
    if r.get("trees", 0) < MIN_TREES_SHAPE or "shape_pass" not in r:
        return "mixed" if cp else "failed"
    sp = bool(r["shape_pass"])
    if cp and sp:
        return "supported"
    if cp or sp:
        return "mixed"
    return "failed"


def spearman_1s(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 5:
        return dict(rho=np.nan, p=np.nan, n=int(m.sum()))
    r = stats.spearmanr(x[m], y[m])
    p1 = r.pvalue / 2 if r.statistic > 0 else 1 - r.pvalue / 2
    return dict(rho=float(r.statistic), p=float(p1), n=int(m.sum()))


def holm(ps):
    order = np.argsort(ps)
    adj = np.empty(len(ps))
    run = 0.0
    for i, j in enumerate(order):
        run = max(run, (len(ps) - i) * ps[j])
        adj[j] = min(1.0, run)
    return adj.tolist()


def rule_table(k_med):
    out = []
    for N in (10, 15, 25):
        for R in (0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8):
            p, R0 = S.fngw_pmf(R, k_med, N, M=60000, seed=3)
            ge = np.cumsum(p[::-1])[::-1]
            out.append(dict(N=N, R=R, R0=R0, mean=float(1 / (1 - R)), p_ge2=float(ge[1]), p_ge3=float(ge[2]),
                            p_ge5=float(ge[4]), p_ge_half=float(ge[N // 2 - 1]), s99=int(np.searchsorted(np.cumsum(p), 0.99) + 1)))
    return out


def main():
    RES.mkdir(parents=True, exist_ok=True)
    gn = gains()
    periods = sorted(int(p.name[1:]) for p in DATA.glob("G*") if (p / "meta.json").exists())
    tasks = [(g, gn.get(g, {})) for g in sorted(periods, key=lambda x: -1 if x == 51 else x)]
    with Pool(N_WORKERS) as pool:
        outs = pool.map(run_period, tasks, chunksize=1)
    rows = [r for o, _ in outs for r in o]
    fcs = [r for _, f in outs for r in f]
    for r in rows:
        for k_, v in list(r.items()):
            if isinstance(v, list):
                r[k_] = json.dumps(v)
    pt = pl.DataFrame(rows, infer_schema_length=None)
    pt.write_parquet(RES / "period_table.parquet")
    fc = pl.DataFrame(fcs) if fcs else pl.DataFrame()
    fc.write_parquet(RES / "forecast_days.parquet")
    allp = pt.filter(pl.col("cls") == "ALL").sort("goal")
    al = allp.to_dicts()
    for r in al:
        r["verdict"] = verdict(r)
    elig = [r for r in al if r["verdict"] != "n/a"]
    summ = dict(n_periods=len(al), n_eligible=len(elig), verdicts={v: sum(r["verdict"] == v for r in al)
                                                                   for v in ("supported", "mixed", "failed", "n/a")},
                h25_available=gn["_h25_available"])
    # P1
    summ["P1"] = dict(all_R_hi_lt1=all(r["R_hi"] < 1 for r in elig), R_range=[min(r["R"] for r in elig), max(r["R"] for r in elig)],
                      R_median=float(np.median([r["R"] for r in elig])))
    cells = pt.filter((pl.col("cls") != "ALL") & (pl.col("nodes") >= 30))
    summ["P1"]["cells_R_hi_lt1"] = [int((cells["R_hi"] < 1).sum()), cells.height]
    order_ok = 0
    order_n = 0
    for g in allp["goal"].to_list():
        sub = {r["cls"]: r for r in pt.filter((pl.col("goal") == g) & (pl.col("nodes") >= 30)).to_dicts()}
        if all(c in sub for c in ("U", "N", "D")):
            order_n += 1
            order_ok += sub["U"]["R"] > sub["N"]["R"] > sub["D"]["R"]
    summ["P1"]["order_UND"] = [order_ok, order_n]
    # P2 (HH108)
    w = [r for r in elig if r.get("n03") is not None]
    summ["P2"] = dict(R_lt_n03=[sum(r["R"] < r["n03"] for r in w), len(w)],
                      Rc_lt_n03=[sum((r.get("R_c") if r.get("R_c") == r.get("R_c") else 9) < r["n03"] for r in w), len(w)],
                      R_gt_n03_beyond_ci=sum(r["R_lo"] > r["n03"] for r in w))
    # P3
    sh = [r for r in elig if r.get("trees", 0) >= MIN_TREES_SHAPE and "shape_pass" in r]
    summ["P3"] = dict(fn_cover_both=[sum(bool(r["shape_pass"]) for r in sh), len(sh)],
                      fn_cover3=[sum(bool(r["fn_cover3"]) for r in sh), len(sh)],
                      gw_cover_both=[sum(bool(r["gw_cover3"]) and bool(r["gw_cover5"]) for r in sh), len(sh)],
                      pure15_rejected=[sum(r.get("p_15pure", 1) < 0.05 for r in sh), len(sh)],
                      tau_app_range=[min(r["tau_app"] for r in sh), max(r["tau_app"] for r in sh)],
                      tau_app_ge2=[sum(r["tau_app"] >= 2 for r in sh), len(sh)],
                      fn_obs_minus_pred3_median=float(np.median([r["p3"] - r["fn_pred3"] for r in sh])),
                      off_root_vs_nonroot=[float(np.nanmedian([r["off_root"] for r in sh])), float(np.nanmedian([r["off_nonroot"] for r in sh]))])
    # P4
    keys = [("R", "n03"), ("R", "g19"), ("p3", "n03"), ("p3", "g19")]
    tests = {f"{a}~{b}": spearman_1s([r.get(a) for r in elig], [r.get(b) for r in elig]) for a, b in keys}
    adj = holm([tests[k_]["p"] for k_ in tests])
    for k_, a in zip(tests, adj):
        tests[k_]["p_holm"] = a
    sec = {f"{a}~{b}": spearman_1s([r.get(a) for r in elig], [r.get(b) for r in elig])
           for a, b in [("R_c", "n03"), ("R_c", "g19"), ("R", "g19a"), ("R", "N_room"), ("R_c", "N_room"), ("n03", "N_room")]}
    summ["P4"] = dict(primary=tests, secondary=sec)
    # P5
    summ["P5"] = dict(hr10_lo_gt1=[sum(bool(r.get("contagion_pass")) for r in elig), len(elig)],
                      jitter_p_lt05=[sum(r.get("jit_p", 1) < 0.05 for r in elig), len(elig)],
                      first_turn_obs_gt_null=[sum(r.get("first_obs", 0) > r.get("first_null", 1) for r in elig), len(elig)],
                      R_c_median=float(np.nanmedian([r.get("R_c", np.nan) for r in elig])),
                      Rc_over_R_median=float(np.nanmedian([r.get("R_c", np.nan) / r["R"] for r in elig if r["R"] > 0])),
                      rx=[dict(goal=r["goal"], ratio=r.get("rx_ratio"), lo=r.get("rx_ratio_lo"), hi=r.get("rx_ratio_hi"),
                               n_unexp=r.get("rx_n_unexp")) for r in elig if r.get("rx_ratio") is not None])
    # P6
    summ["P6"] = dict(hr21_le25=[sum(r.get("hr21", 9) <= 2.5 for r in elig if np.isfinite(r.get("hr21", np.nan))),
                                 sum(np.isfinite(r.get("hr21", np.nan)) for r in elig)],
                      complex_flag=[r["goal"] for r in elig if r.get("hr21_lo", 0) > 2.5 and r.get("hr21", 0) > 3],
                      hr21_median=float(np.nanmedian([r.get("hr21", np.nan) for r in elig])))
    cls_rows = pt.filter((pl.col("cls") != "ALL") & (pl.col("nonseed") >= MIN_NONSEED)).to_dicts()
    summ["P6"]["complex_flag_class"] = [(r["goal"], r["cls"], r["hr21"], r["hr21_lo"]) for r in cls_rows
                                        if r.get("hr21_lo") is not None and r["hr21_lo"] == r["hr21_lo"] and r["hr21_lo"] > 2.5 and r["hr21"] > 3]
    # P7
    if fc.height:
        fcp = fc.group_by("goal").agg(pl.col("cover2").mean(), pl.col("cover3").mean(), pl.len().alias("days"),
                                      *[pl.col(c).sum() for c in ("ls_fngw", "ls_gwnb", "ls_emp", "ls_binom", "ls_betabin", "ls_h03")]).sort("goal")
        fcp.write_parquet(RES / "forecast_periods.parquet")
        summ["P7"] = dict(days=fc.height, periods=fcp.height, cover2=float(fc["cover2"].mean()), cover3=float(fc["cover3"].mean()),
                          beats={r: [int((fcp["ls_fngw"] > fcp[f"ls_{r}"]).sum()), int(fcp[f"ls_{r}"].is_not_nan().sum())]
                                 for r in ("binom", "betabin", "h03", "emp", "gwnb")},
                          dls_total={r: float((fcp["ls_fngw"] - fcp[f"ls_{r}"]).fill_nan(0).sum()) for r in ("binom", "betabin", "h03", "emp", "gwnb")})
    kmed = float(np.median([min(r["k"], 50) for r in elig]))
    summ["rule"] = dict(k_median=kmed, table=rule_table(kmed))
    (RES / "summary.json").write_text(json.dumps(summ, indent=1, default=float))
    # per-period json for the cards
    per = {}
    for r in al:
        g = r["goal"]
        cl = pt.filter((pl.col("goal") == g) & (pl.col("cls") != "ALL")).sort("cls").to_dicts()
        per[str(g)] = dict(verdict=r["verdict"], R=r["R"], R_lo=r["R_lo"], R_hi=r["R_hi"], R_c=r.get("R_c"), hr10=r.get("hr10"),
                           hr10_lo=r.get("hr10_lo"), hr10_hi=r.get("hr10_hi"), shape_pass=r.get("shape_pass"),
                           row=r, classes=[dict(cls=c["cls"], ideas=c["ideas"], nodes=c["nodes"], R=c.get("R"), R_lo=c.get("R_lo"),
                                                R_hi=c.get("R_hi"), R_c=c.get("R_c"), p2=c.get("p2"), p3=c.get("p3"),
                                                smax=c.get("smax", 0)) for c in cl])
    (RES / "periods_raw.json").write_text(json.dumps(per, indent=1, default=float))
    print(json.dumps({k_: summ[k_] for k_ in ("verdicts", "P1", "P2", "P5", "P6")}, indent=1, default=float))
    print(json.dumps(summ.get("P7", {}), indent=1, default=float))
    print(json.dumps(summ["P4"], indent=1, default=float))
    print(json.dumps(summ["P3"], indent=1, default=float))


if __name__ == "__main__":
    main()
