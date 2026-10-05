"""H11 round 2 (2026-10-05): R1 preferential attachment, R2 stigmergic vs social joining, R3 herding and output.

Inputs: data/processed/H11-potts-labor-vs-herding/r2/ (scheme/build_r2.py). Outputs: r2/results/*.json,
per_period_estimates rows (H11, round 2).

Usage:
  uv run python hypotheses/H11-potts-labor-vs-herding/analysis/round2.py synth      # validation on real skeletons
  uv run python hypotheses/H11-potts-labor-vs-herding/analysis/round2.py run        # real data (non-reserved only)
  uv run python hypotheses/H11-potts-labor-vs-herding/analysis/round2.py estimates  # write per_period_estimates rows
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "infra/shared"))
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

import r2lib as L  # noqa: E402

ROOT = HERE.parents[2]
R2 = ROOT / "data/processed/H11-potts-labor-vs-herding/r2"
RES = R2 / "results"
OWN = {39, 42, 44, 51}
MIN_REC = 25
SEED = 20261005


def load(ch: str):
    c = pl.read_parquet(R2 / f"cands_{ch}.parquet")
    j = pl.read_parquet(R2 / f"joins_{ch}.parquet")
    sk = pl.read_parquet(R2 / f"skel_{ch}.parquet")
    c = c.join(j.select("unit", "jid", "agent", "pt_date", "goal"), on=["unit", "jid"], how="left")
    return c.sort("unit", "jid"), j, sk


def testable_units(c: pl.DataFrame) -> list[str]:
    n = c.group_by("unit").agg(pl.col("jid").n_unique().alias("n"))
    return sorted(n.filter(pl.col("n") >= MIN_REC)["unit"].to_list(), key=_ukey)


def _ukey(u):
    return (int(u[1:]) if u.startswith("G") else int(u[:2]), u)


def goal_of(u: str) -> int:
    return int(u[1:]) if u.startswith("G") else int(u[:2])


def group_of(u: str) -> str:
    return "own" if goal_of(u) in OWN else "shared"


def arrays(cu: pl.DataFrame):
    gid = cu["jid"].to_numpy()
    y = cu["chosen"].to_numpy().astype(float)
    st = L._starts(gid)
    clus = cu["agent"].to_numpy()[st]
    return gid, y, clus


MIN_EV = 5
EXPOSURES = {"C", "C_lead", "M_read", "M_unread", "M_lead"}


def r2_ridge(names, exp_ridge=0.5, base=1e-4):
    """Amendment A1: L2 0.5 on the R2 exposure coefficients (quasi-separation on sparse exposures)."""
    return np.array([exp_ridge if n in EXPOSURES else base for n in names])


def ridge_for(names, fe_ridge=0.1, base=1e-4):
    return np.array([fe_ridge if n.startswith("fe:") else base for n in names])


# ============================================================================================ R1
def fit_r1(cu: pl.DataFrame, variant: str, y=None) -> dict:
    gid, y0, clus = arrays(cu)
    y = y0 if y is None else y
    X, nm = L.r1_design(cu, variant)
    f = L.clogit(X, gid, y, cluster=clus, ridge=ridge_for(nm))
    out = {n: L.wald(f["beta"][i], f["se"][i]) for i, n in enumerate(nm) if not n.startswith("fe:")}
    if variant == "lead":
        i, k = nm.index("lag"), nm.index("lead")
        d = f["beta"][i] - f["beta"][k]
        v = f["cov"][i, i] + f["cov"][k, k] - 2 * f["cov"][i, k]
        out["lag_minus_lead"] = L.wald(d, math.sqrt(max(v, 0)))
    out["_beta"] = f["beta"][:4].tolist()
    out["_ll"] = f["ll"]
    out["_n"] = f["n_groups"]
    return out


# ============================================================================================ R2
def fit_r2(cu: pl.DataFrame, variant: str, y=None) -> dict:
    gid, y0, clus = arrays(cu)
    y = y0 if y is None else y
    X, nm = L.r2_design(cu, variant)
    f = L.clogit(X, gid, y, cluster=clus, ridge=r2_ridge(nm))
    out = {n: L.wald(f["beta"][i], f["se"][i]) for i, n in enumerate(nm)}
    ev = {n: int(((X[:, i] > 0) & (y > 0)).sum()) for i, n in enumerate(nm)}
    out["_events"] = ev
    if variant == "joint":
        for a, b in (("M_read", "M_unread"), ("M_read", "M_lead"), ("C", "C_lead")):
            i, k = nm.index(a), nm.index(b)
            if min(ev[a], ev[b]) < MIN_EV:          # amendment A1: estimable only with >= 5 chosen exposed rows each
                out[f"{a}-{b}"] = {"est": None, "se": None, "lo": None, "hi": None, "z": None, "p": None, "sig": False,
                                   "not_estimable": True, "events": [ev[a], ev[b]]}
                continue
            d = f["beta"][i] - f["beta"][k]
            v = f["cov"][i, i] + f["cov"][k, k] - 2 * f["cov"][i, k]
            out[f"{a}-{b}"] = L.wald(d, math.sqrt(max(v, 0)))
    out["_ll"] = f["ll"]
    return out


def heldout_dll(cu: pl.DataFrame, y=None) -> dict:
    """R2a: day-blocked held-out log-likelihood per join, base+C minus base+M."""
    gid, y0, clus = arrays(cu)
    y = y0 if y is None else y
    st = L._starts(gid)
    days_g = cu["pt_date"].to_numpy()[st]
    days = sorted(set(days_g.tolist()))
    if len(days) < 2:
        return {"dll": None, "n": 0, "folds": len(days)}
    XC, nC = L.r2_design(cu, "C")
    XM, nM = L.r2_design(cu, "M")
    cnt = np.diff(np.r_[st, len(gid)])
    row_day = np.repeat(days_g, cnt)
    vals, clv = [], []
    for d in days:
        tr = row_day != d
        te = ~tr
        if te.sum() == 0 or tr.sum() == 0:
            continue
        fC = L.clogit(XC[tr], gid[tr], y[tr], ridge=r2_ridge(nC))
        fM = L.clogit(XM[tr], gid[tr], y[tr], ridge=r2_ridge(nM))
        llC = L.clogit_ll(XC[te], gid[te], y[te], fC["beta"])
        llM = L.clogit_ll(XM[te], gid[te], y[te], fM["beta"])
        vals.extend((llC - llM).tolist())
        ag = cu["agent"].to_numpy()[te][L._starts(gid[te])]
        clv.extend([f"{a}|{d}" for a in ag])
    v = np.array(vals)
    # SE clustered by agent-day
    cl = np.array(clv)
    u, inv = np.unique(cl, return_inverse=True)
    sums = np.bincount(inv, weights=v - v.mean())
    se = math.sqrt((sums ** 2).sum()) / len(v) * math.sqrt(len(u) / max(len(u) - 1, 1))
    return {"dll": float(v.mean()), "se": se, "lo": float(v.mean() - 1.96 * se), "hi": float(v.mean() + 1.96 * se),
            "n": len(v), "folds": len(days)}


def mh_contrasts(cu: pl.DataFrame, y=None, unit_strata=False) -> dict:
    y0 = cu["chosen"].to_numpy()
    y = y0 if y is None else y
    a = cu["a"].to_numpy()
    abin = np.select([a == 0, a == 1, a <= 3], [0, 1, 2], 3)
    h = cu["h"].to_numpy().astype(int)
    m = cu["m_read"].to_numpy() > 0
    cc = cu["c"].to_numpy() > 0
    us = cu["unit"].to_numpy() if unit_strata else np.zeros(len(a), dtype=object)
    s = cu["s"].to_numpy()
    sbin = np.select([s == 0, s <= 3, s <= 15], [0, 1, 2], 3)      # amendment A1: size bin in both strata
    s1 = np.array([f"{x}|{yy}|{z}|{q}" for x, yy, z, q in zip(abin, h, us, sbin)])
    s2 = np.array([f"{int(x)}|{yy}|{z}|{q}|{b}" for x, yy, z, q, b in zip(m, h, us, sbin, abin)])
    return {"OR_M_given_act": L.mh_or(y, m, s1), "OR_C_given_M": L.mh_or(y, cc, s2)}


# ============================================================================================ R3
def r3_unit(p: pl.DataFrame, outcome="n_commit", y=None) -> dict:
    p = p.filter(pl.col("act_min") >= 1).with_columns(
        (pl.col("agent").cast(pl.String) + "|" + pl.col("pt_date")).alias("ad"))
    p = p.with_columns(pl.when(pl.col("k_others") == 0).then(0).when(pl.col("k_others") == 1).then(1).otherwise(2).alias("cls"))
    # agent-days containing both solo and herd windows
    both = p.group_by("ad").agg(((pl.col("cls") == 0).sum() > 0).alias("hs"), ((pl.col("cls") == 2).sum() > 0).alias("hh"))
    okad = both.filter(pl.col("hs") & pl.col("hh"))["ad"]
    n_herd = p.filter(pl.col("ad").is_in(okad.implode()) & (pl.col("cls") == 2)).height
    n_solo = p.filter(pl.col("ad").is_in(okad.implode()) & (pl.col("cls") == 0)).height
    out = {"n_herd": n_herd, "n_solo": n_solo, "testable": bool(n_herd >= 20 and n_solo >= 20)}
    if not out["testable"]:
        return out
    p = p.sort("ad", "g")
    _, gid = np.unique(p["ad"].to_numpy(), return_inverse=True)
    order = np.argsort(gid, kind="stable")
    p = p[order]
    gid = gid[order]
    yy = p[outcome].to_numpy().astype(float) if y is None else y
    cls = p["cls"].to_numpy()
    lm = np.log(p["act_min"].to_numpy().astype(float))
    X = np.c_[(cls == 1).astype(float), (cls == 2).astype(float), lm]
    st = L._starts(gid)
    clus = p["agent"].to_numpy()[st]
    f = L.clogit(X, gid, yy, cluster=clus, ridge=1e-6, weights_y=True)
    dfc = len(np.unique(clus)) - 1
    out["log_RR_pair"] = L.wald(f["beta"][0], f["se"][0], df=dfc)
    out["log_RR_herd"] = L.wald(f["beta"][1], f["se"][1], df=dfc)
    out["n_clusters"] = dfc + 1
    out["b_logmin"] = float(f["beta"][2])
    # matched pairs: each herd window vs nearest-minutes solo window in the same agent-day (within +-25%)
    ad = p["ad"].to_numpy()
    m = p["act_min"].to_numpy().astype(float)
    d = []
    for k in np.unique(gid):
        idx = np.flatnonzero(gid == k)
        hs = idx[cls[idx] == 2]
        ss = idx[cls[idx] == 0]
        if len(hs) == 0 or len(ss) == 0:
            continue
        for i in hs:
            j = ss[np.argmin(np.abs(m[ss] - m[i]))]
            if abs(m[j] - m[i]) <= 0.25 * m[i]:
                d.append(math.log((yy[i] + 0.5) / m[i]) - math.log((yy[j] + 0.5) / m[j]))
    if len(d) >= 5:
        dv = np.array(d)
        out["matched"] = {"mean_log_ratio": float(dv.mean()), "se": float(dv.std(ddof=1) / math.sqrt(len(dv))), "n": len(dv)}
    return out


def theta_unit(pw: pl.DataFrame, y=None) -> dict:
    pw = pw.filter(pl.col("n_ag") >= 1).with_columns((pl.col("project") + "|" + pl.col("pt_date")).alias("pd"))
    var = pw.group_by("pd").agg(pl.col("n_ag").n_unique().alias("nv"))
    pw = pw.join(var.filter(pl.col("nv") >= 2), on="pd", how="semi")
    out = {"n_rows": pw.height, "testable": pw.height >= 30}
    if not out["testable"]:
        return out
    _, gid = np.unique(pw["pd"].to_numpy(), return_inverse=True)
    order = np.argsort(gid, kind="stable")
    pw = pw[order]
    gid = gid[order]
    yy = pw["c_proj"].to_numpy().astype(float) if y is None else y
    if yy.sum() == 0:
        out["testable"] = False
        return out
    X = np.c_[np.log(pw["n_ag"].to_numpy().astype(float))]
    f = L.clogit(X, gid, yy, ridge=1e-6, weights_y=True, cluster=np.arange(len(L._starts(gid))))
    out["theta"] = L.wald(f["beta"][0], f["se"][0])
    out["n_groups"] = f["n_groups"]
    return out


# ============================================================================================ synthetic validation
def draw_choice(cu: pl.DataFrame, u: np.ndarray, rng) -> np.ndarray:
    gid = cu["jid"].to_numpy()
    st = L._starts(gid)
    n = len(gid)
    m = L._expand(L._gmax(u, st), st, n)
    e = np.exp(u - m)
    p = e / L._expand(L._gsum(e, st), st, n)
    y = np.zeros(n)
    bounds = np.r_[st, n]
    for k in range(len(st)):
        a, b = bounds[k], bounds[k + 1]
        y[a + rng.choice(b - a, p=p[a:b])] = 1
    return y


def synth(reps=50):
    rng = np.random.default_rng(SEED)
    RES.mkdir(parents=True, exist_ok=True)
    out = {"R1": {}, "R2": {}, "R3": {}}
    plan = {"work": ["G31", "G38", "51f", "51g"], "att": ["G19", "G38", "51d"]}
    t0 = time.time()
    for ch, us in plan.items():
        c, j, sk = load(ch)
        for u in us:
            cu = c.filter(pl.col("unit") == u)
            a = cu["a"].to_numpy().astype(float)
            loga = np.where(a > 0, np.log(np.maximum(a, 1)), 0)
            z0 = (a == 0).astype(float)
            h = cu["h"].to_numpy().astype(float)
            ls = np.log1p(cu["s"].to_numpy().astype(float))
            fin = sk.filter(pl.col("unit") == u).group_by("project").len()
            fsz = dict(fin.iter_rows())
            fit_ = np.log1p(np.array([fsz.get(y, 0) for y in cu["Y"].to_list()], float))
            worlds = {"alpha1": 1.0 * loga - 1.0 * z0 + 1.5 * h, "alpha05": 0.5 * loga - 1.0 * z0 + 1.5 * h,
                      "fitness": 1.0 * fit_ + 1.5 * h, "burst": 1.0 * np.log1p(cu["a_lead"].to_numpy().astype(float)) + 1.5 * h}
            res = {}
            for wn, uu in worlds.items():
                al, cov, alfe, lml, lmlz, sigp = [], [], [], [], [], []
                for _ in range(reps):
                    y = draw_choice(cu, uu, rng)
                    f = fit_r1(cu, "full", y)
                    al.append(f["alpha"]["est"])
                    sigp.append((f["alpha"]["lo"] or 0) > 0)
                    cov.append((f["alpha"]["lo"] or -9) <= {"alpha1": 1, "alpha05": 0.5}.get(wn, 0) <= (f["alpha"]["hi"] or 9))
                    if wn in ("fitness", "burst"):
                        fe = fit_r1(cu, "fe", y)
                        alfe.append(fe["alpha"]["est"])
                        ld = fit_r1(cu, "lead", y)["lag_minus_lead"]
                        lml.append(ld["est"])
                        lmlz.append((ld["z"] or 0) > 1.96)
                res[wn] = {"alpha_mean": float(np.mean(al)), "alpha_sd": float(np.std(al)), "coverage_or_fp": float(np.mean(cov)),
                           "alpha_sig_pos": float(np.mean(sigp))}
                if alfe:
                    res[wn].update({"alpha_fe_mean": float(np.mean(alfe)), "lag_minus_lead_mean": float(np.mean(lml)),
                                    "fp_lag_gt_lead": float(np.mean(lmlz))})
            out["R1"][f"{ch}:{u}"] = res
            # R2 worlds
            f = {k: np.log1p(cu[k].to_numpy().astype(float)) for k in ("c", "c_lead", "m_read", "m_unread", "m_lead")}
            w2 = {"social": 1.2 * f["m_read"] + 1.5 * h + 0.3 * ls, "artifact": 0.8 * f["c"] + 1.5 * h + 0.3 * ls,
                  "burst": 0.8 * f["c_lead"] + 1.2 * f["m_lead"] + 1.5 * h + 0.3 * ls, "null": 1.5 * h + 0.3 * ls}
            r2 = {}
            for wn, uu in w2.items():
                win_C, sig_ru, sig_rl, sig_cl, orw, ne = [], [], [], [], [], []
                for _ in range(max(reps // 2, 10)):
                    y = draw_choice(cu, uu, rng)
                    hd = heldout_dll(cu, y)
                    win_C.append((hd["dll"] or 0) > 0)
                    jt = fit_r2(cu, "joint", y)
                    sig_ru.append((jt["M_read-M_unread"]["z"] or 0) > 1.96)
                    sig_rl.append((jt["M_read-M_lead"]["z"] or 0) > 1.96)
                    sig_cl.append((jt["C-C_lead"]["z"] or 0) > 1.96)
                    ne.append(bool(jt["M_read-M_unread"].get("not_estimable")))
                    mh = mh_contrasts(cu, y)
                    o1, o2 = mh["OR_M_given_act"]["or"], mh["OR_C_given_M"]["or"]
                    orw.append(None if (o1 is None or o2 is None) else o2 > o1)
                r2[wn] = {"P(read-unread n.e.)": float(np.mean(ne)), "P(dLL_CM>0)": float(np.mean(win_C)), "P(read>unread sig)": float(np.mean(sig_ru)),
                          "P(read>lead sig)": float(np.mean(sig_rl)), "P(C>C_lead sig)": float(np.mean(sig_cl)),
                          "P(OR_C>OR_M)": float(np.mean([x for x in orw if x is not None])) if any(x is not None for x in orw) else None}
            out["R2"][f"{ch}:{u}"] = r2
            print(ch, u, f"{time.time() - t0:.0f}s", json.dumps(res)[:300], json.dumps(r2)[:400], flush=True)
    # R3 worlds on the real panel
    P = pl.read_parquet(R2 / "panel_r3.parquet")
    PW = pl.read_parquet(R2 / "projwin_r3.parquet")
    for u in ["G31", "G38", "G41", "51d", "51g"]:
        pu = P.filter(pl.col("unit") == u)
        base = r3_unit(pu)
        if not base.get("testable"):
            out["R3"][u] = {"testable": False}
            continue
        q = pu.filter(pl.col("act_min") >= 1).with_columns((pl.col("agent").cast(pl.String) + "|" + pl.col("pt_date")).alias("ad"))
        q = q.with_columns(pl.when(pl.col("k_others") == 0).then(0).when(pl.col("k_others") == 1).then(1).otherwise(2).alias("cls"))
        both = q.group_by("ad").agg(((pl.col("cls") == 0).sum() > 0).alias("hs"), ((pl.col("cls") == 2).sum() > 0).alias("hh"))
        q = q.sort("ad", "g")
        _, gid = np.unique(q["ad"].to_numpy(), return_inverse=True)
        q = q[np.argsort(gid, kind="stable")]
        rate = q.group_by("ad").agg((pl.col("n_commit").sum() / pl.col("act_min").sum()).alias("r"))
        q = q.join(rate, on="ad", how="left")
        r = q["r"].to_numpy()
        m = q["act_min"].to_numpy().astype(float)
        cls = q["cls"].to_numpy()
        res = {}
        for wn, rr in (("RR1", 1.0), ("RR07", 0.7)):
            ests, cov, sig = [], [], []
            for _ in range(100):
                mu = r * m * np.where(cls == 2, rr, 1.0)
                # rescale so the agent-day totals stay comparable
                y = rng.poisson(mu)
                f = r3_unit(q.drop("r", "ad", "cls").with_columns(pl.Series("ysim", y)), outcome="ysim")
                e = f["log_RR_herd"]
                ests.append(e["est"])
                cov.append(e["lo"] <= math.log(rr) <= e["hi"])
                sig.append(bool(e.get("sig")))
            res[wn] = {"mean_log_RR": float(np.mean(ests)), "true": math.log(rr), "coverage": float(np.mean(cov)),
                       "P(sig)": float(np.mean(sig))}
        # theta: commits proportional to agents (theta = 1) and to sqrt (theta = 0.5)
        pw = PW.filter(pl.col("unit") == u).filter(pl.col("n_ag") >= 1).with_columns((pl.col("project") + "|" + pl.col("pt_date")).alias("pd"))
        var = pw.group_by("pd").agg(pl.col("n_ag").n_unique().alias("nv"))
        pw = pw.join(var.filter(pl.col("nv") >= 2), on="pd", how="semi")
        _, gid = np.unique(pw["pd"].to_numpy(), return_inverse=True)
        pw = pw[np.argsort(gid, kind="stable")]
        lam = pw.group_by("pd").agg((pl.col("c_proj").sum() / pl.col("n_ag").sum()).alias("lam"))
        pw = pw.join(lam, on="pd", how="left")
        for wn, th in (("theta1", 1.0), ("theta05", 0.5)):
            ests, cov = [], []
            for _ in range(100):
                mu = pw["lam"].to_numpy() * pw["n_ag"].to_numpy() ** th * 1.0 + 1e-9
                y = rng.poisson(mu)
                f = theta_unit(pw.drop("lam", "pd").with_columns(pl.Series("c_proj", y)))
                if not f.get("testable"):
                    continue
                ests.append(f["theta"]["est"])
                cov.append(f["theta"]["lo"] <= th <= f["theta"]["hi"])
            res[wn] = {"mean": float(np.mean(ests)) if ests else None, "true": th, "coverage": float(np.mean(cov)) if cov else None}
        out["R3"][u] = res
        print("R3", u, json.dumps(res), flush=True)
    (RES / "synthetic_r2_A1.json").write_text(json.dumps(out, indent=1))


# ============================================================================================ real run
def run():
    RES.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED + 1)
    out = {"R1": {}, "R2": {}, "R3": {}, "R1_replay": {}}
    for ch in ("work", "att"):
        c, j, sk = load(ch)
        for u in testable_units(c):
            cu = c.filter(pl.col("unit") == u)
            r1 = {v: fit_r1(cu, v) for v in ("full", "pa", "fe", "lead")}
            r1["n_recruits"] = int(cu["jid"].n_unique())
            r1["n_births"] = int(j.filter((pl.col("unit") == u) & (pl.col("kind") == "birth")).height)
            r1["group"] = group_of(u)
            out["R1"][f"{ch}:{u}"] = r1
            r2 = {"heldout": heldout_dll(cu), "mh": mh_contrasts(cu), "joint": fit_r2(cu, "joint"),
                  "C": fit_r2(cu, "C"), "M": fit_r2(cu, "M"), "group": group_of(u)}
            out["R2"][f"{ch}:{u}"] = r2
            # replay
            sku = sk.filter(pl.col("unit") == u)
            obs = L.observed_size_stats(sku)
            rep = {"observed": obs}
            for kern in ("fit", "yule", "uniform"):
                sims = [L.replay(sku, kern, np.array(r1["full"]["_beta"]), rng) for _ in range(200)]
                band = {}
                for s in ("top_share", "eff_n", "shared_share"):
                    v = np.array([x[s] for x in sims])
                    band[s] = {"q05": float(np.quantile(v, 0.05)), "q50": float(np.median(v)), "q95": float(np.quantile(v, 0.95)),
                               "inside": bool(np.quantile(v, 0.05) <= obs[s] <= np.quantile(v, 0.95)),
                               "pct": float((v < obs[s]).mean())}
                rep[kern] = band
            out["R1_replay"][f"{ch}:{u}"] = rep
            print(ch, u, "alpha", round(r1["full"]["alpha"]["est"], 2), "dLL", r2["heldout"].get("dll"), flush=True)
    P = pl.read_parquet(R2 / "panel_r3.parquet")
    PW = pl.read_parquet(R2 / "projwin_r3.parquet")
    for u in sorted(P["unit"].unique().to_list(), key=_ukey):
        pu = P.filter(pl.col("unit") == u)
        r = {o: r3_unit(pu, o) for o in ("n_commit", "n_land", "n_deploy")}
        r["theta"] = theta_unit(PW.filter(pl.col("unit") == u))
        r["group"] = group_of(u)
        dup = pu.filter(pl.col("act_min") >= 1).with_columns(
            pl.when(pl.col("k_others") == 0).then(pl.lit("solo")).when(pl.col("k_others") == 1).then(pl.lit("pair"))
            .otherwise(pl.lit("herd")).alias("cls")).group_by("cls").agg(
            pl.col("n_commit").sum(), pl.col("n_revert").sum(), pl.col("n_merge").sum(), pl.col("act_min").sum(), pl.len())
        r["by_class"] = {x["cls"]: x for x in dup.to_dicts()}
        out["R3"][u] = r
    out["R3c"] = between_weeks()
    (RES / "real_r2.json").write_text(json.dumps(out, indent=1, default=str))
    print("done")


def between_weeks() -> dict:
    """R3c: output per active agent-hour per unit vs the round-1b work co-location excess."""
    sys.path.insert(0, str(ROOT / "infra/shared"))
    SH = ROOT / "data/processed/shared"
    import project_states as PS
    units = [g for g in (30, 31, 33, 35, 36, 37, 38, 39, 40, 41, 42, 44)] + ["51" + x for x in "abcdefghijkl"]
    pu = pl.read_parquet(SH / "period_units.parquet")
    rows = []
    wc = pl.scan_parquet(SH / "work_commits.parquet").filter(
        pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind").cast(pl.String) == "agent") & ~pl.col("automated")
        & ~pl.col("holdout") & (pl.col("author_agent") != 19)).select("pt_date").collect()
    ab = pl.scan_parquet(SH / "activity_bins_fixed.parquet").filter(pl.col("state").is_in([3, 4]) & (pl.col("agent") != 19)).group_by(
        "pt_date").len().collect()
    cal = PS.load_calendar(None, allow_holdout=False)
    for u in units:
        if isinstance(u, int):
            days = cal.filter(pl.col("goal_no") == u)["pt_date"].to_list()
            key = f"G{u:02d}"
        else:
            r = pu.filter(pl.col("unit_id") == u)
            days = [d for d in r["days"][0] if d in set(cal["pt_date"].to_list())]
            key = u
        nc = wc.filter(pl.col("pt_date").is_in(days)).height
        am = ab.filter(pl.col("pt_date").is_in(days))["len"].sum()
        exc = None
        f = ROOT / f"data/processed/H11-potts-labor-vs-herding/r1b/work/{key}.json"
        if f.exists():
            js = json.loads(f.read_text())
            exc = ((js.get("work") or {}).get("cowork") or {}).get("excess")
        rows.append({"unit": key, "group": "own" if (u if isinstance(u, int) else 51) in OWN else "shared",
                     "commits_per_agent_hour": nc / (am / 60) if am else None, "cowork_excess_work": exc, "commits": nc,
                     "active_agent_hours": am / 60})
    df = pl.DataFrame(rows)
    ok = df.drop_nulls(["commits_per_agent_hour", "cowork_excess_work"])
    rho = stats.spearmanr(ok["commits_per_agent_hour"], ok["cowork_excess_work"]) if ok.height >= 4 else None
    a = df.filter(pl.col("group") == "own")["commits_per_agent_hour"].drop_nulls().to_numpy()
    b = df.filter(pl.col("group") == "shared")["commits_per_agent_hour"].drop_nulls().to_numpy()
    mw = stats.mannwhitneyu(a, b, alternative="two-sided") if len(a) and len(b) else None
    return {"rows": rows, "spearman": None if rho is None else {"rho": float(rho[0]), "p": float(rho[1]), "n": ok.height},
            "mannwhitney_own_vs_shared": None if mw is None else {"U": float(mw[0]), "p": float(mw[1]), "median_own": float(np.median(a)),
                                                                  "median_shared": float(np.median(b)), "n_own": len(a), "n_shared": len(b)}}


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    {"synth": synth, "run": run}.get(cmd, lambda: None)()


# ============================================================================================ estimates rows
def write_rows():
    import estimates as E
    js = json.loads((RES / "real_r2.json").read_text())
    src = "data/processed/H11-potts-labor-vs-herding/r2/results/real_r2.json"
    rows = []

    def pu(u):
        return E.map_unit(goal_of(u)) if u.startswith("G") else u

    def add(u, stat, ch, method, w, null, n, n_kind, notes="", ci_kind="se_z", est_key="est"):
        if w is None or w.get(est_key) is None:
            return
        rows.append({"period_unit": pu(u), "goal_no": goal_of(u), "statistic": stat, "channel": ch, "estimate": w[est_key],
                     "ci_lo": w.get("lo"), "ci_hi": w.get("hi"), "se": w.get("se"), "n": n, "n_kind": n_kind,
                     "method": method, "null": null, "role": "replication", "ci_level": 0.95, "ci_kind": ci_kind,
                     "post_hoc": False, "source": src, "notes": notes})

    for key, r in js["R1"].items():
        ch, u = key.split(":")
        n = r["n_recruits"]
        add(u, "h11r2_alpha_attach", ch, "clogit_full_cluster_agent", r["full"]["alpha"], "alpha=0", n, "recruit joins",
            "P(join Y) ∝ a_Y^alpha; a = others' labelled windows on Y in previous 2 active h; + zero dummy, log size, habit")
        add(u, "h11r2_alpha_pa", ch, "clogit_kernel_only", r["pa"]["alpha"], "alpha=0", n, "recruit joins")
        add(u, "h11r2_alpha_fe", ch, "clogit_project_fe_ridge0.1", r["fe"]["alpha"], "alpha=0", n, "recruit joins")
        add(u, "h11r2_lag_minus_lead", ch, "clogit_log1p_lag_lead", r["lead"]["lag_minus_lead"], "lag=lead", n, "recruit joins")
    for key, r in js["R2"].items():
        ch, u = key.split(":")
        hd = r["heldout"]
        if hd.get("dll") is not None:
            add(u, "h11r2_dLL_artifact_minus_chat", ch, "clogit_dayblocked_heldout", {"est": hd["dll"], "lo": hd["lo"], "hi": hd["hi"], "se": hd["se"]},
                "dLL=0", hd["n"], "recruit joins", "held-out log-lik per join, base+log1p(C) minus base+log1p(M_read)")
        for k, stat in (("OR_M_given_act", "h11r2_OR_chatread_given_activity"), ("OR_C_given_M", "h11r2_OR_commits_given_chat")):
            o = r["mh"][k]
            if o.get("or") is not None:
                add(u, stat, ch, "mantel_haenszel_RBG", {"est": o["or"], "lo": o["lo"], "hi": o["hi"]}, "OR=1",
                    o["n_exposed_events"], "exposed joins", ci_kind="parametric")
        jt = r["joint"]
        for k, stat in (("M_read-M_unread", "h11r2_beta_chatread_minus_unread"), ("M_read-M_lead", "h11r2_beta_chatread_minus_lead"),
                        ("C-C_lead", "h11r2_beta_commits_minus_lead")):
            add(u, stat, ch, "clogit_joint_cluster_agent", jt[k], "difference=0", None, "recruit joins")
    for u, r in js["R3"].items():
        for o, stat in (("n_commit", "h11r2_logRR_herd_commits"), ("n_land", "h11r2_logRR_herd_landed")):
            x = r[o]
            if x.get("testable") and "log_RR_herd" in x:
                add(u, stat, "work_output", "cond_poisson_agentday_fe", x["log_RR_herd"], "logRR=0", x["n_herd"], "herd windows",
                    "herd = >=2 other agents on the same attention-action project in the window; vs solo; log active minutes")
        t = r["theta"]
        if t.get("testable") and "theta" in t:
            add(u, "h11r2_theta_crowding", "work_output", "cond_poisson_projectday_fe", t["theta"], "theta=1", t["n_rows"], "project-windows")
    E.write_estimates(rows, hypothesis="H11", replace_keys=("statistic", "channel", "method", "role", "source"))
    print(len(rows), "rows written")


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "estimates":
    write_rows()
