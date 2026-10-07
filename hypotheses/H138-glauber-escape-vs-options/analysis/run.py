"""H138 round 1 on exploration data (non-reserved units only): O1-O6, N1-N3, the N1 permutation null, variants, the
kill rule, the verdicts and the estimates rows.

Estimator (Amendment A1, before real data): binary cloglog hazard per window with offset ln(own calls) (the card's
per-call cloglog form), agent fixed effects, a 3-df natural spline in active time, agent-cluster sandwich, t(G-1).

Writes data/processed/H138-glauber-escape-vs-options/results/{units.parquet, results.json} and the estimates rows.
Usage: uv run python hypotheses/H138-glauber-escape-vs-options/analysis/run.py [--perm 1000] [--boot 500] [--no-estimates]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h138lib as L  # noqa: E402

RES = L.D / "results"
SHARED = L.SHARED
TAU = 0.5


# ============================================================================================ loading
def load_channel(ch: str) -> dict[str, pl.DataFrame]:
    out = {}
    for g in (L.WORK_GOALS if ch == "work" else L.ATT_GOALS):
        p = L.D / f"G{g:02d}" / f"windows_{ch}.parquet"
        if not p.exists():
            continue
        d = pl.read_parquet(p)
        for (u,), x in d.group_by(["unit"], maintain_order=True):
            out[u] = x
    return dict(sorted(out.items(), key=lambda kv: (int("".join(c for c in kv[0] if c.isdigit())), kv[0])))


def goal_of(unit: str) -> int:
    return int("".join(c for c in unit[:2] if c.isdigit()))


# ============================================================================================ per-unit pieces
def o1(d: pl.DataFrame, qcol="q_live", model="O1") -> dict:
    r = L.fit(d, model, qcol)
    return r


def agent_boot(d: pl.DataFrame, fn, B: int, rng) -> list:
    ags = d["agent"].unique().sort().to_numpy()
    parts = {int(a): d.filter(pl.col("agent") == a) for a in ags}
    out = []
    for _ in range(B):
        pick = rng.choice(ags, len(ags), replace=True)
        frames = [parts[int(a)].with_columns(pl.lit(k).cast(pl.Int16).alias("agent")) for k, a in enumerate(pick)]
        db = pl.concat(frames)
        if db["leave"].sum() < 3:
            continue
        try:
            out.append(fn(db))
        except Exception:
            continue
    return out


def perm_null(d: pl.DataFrame, n: int, rng) -> np.ndarray:
    """N1: within-agent, within-day permutation of the q_live series (keeps leave times and the q marginal)."""
    d = d.with_row_index("_r")
    groups = [g["_r"].to_numpy() for _, g in d.group_by(["agent", "day"])]
    q = d["q_live"].to_numpy().copy()
    out = np.empty(n)
    for i in range(n):
        qp = q.copy()
        for idx in groups:
            if len(idx) > 1:
                qp[idx] = q[rng.permutation(idx)]
        dp = d.with_columns(pl.Series("q_live", qp))
        r = L.fit(dp, "O1")
        out[i] = L.coef(r, "lnq")["est"] if "lnq" in r["names"] else np.nan
    return out


def oof_score(d: pl.DataFrame) -> dict:
    """O2 model comparison: day-blocked out-of-fold log score per leave, Z_alt model minus q_live model."""
    days = sorted(d["day"].unique().to_list())
    tot = {"O1": 0.0, "O2": 0.0}
    n_leave = 0
    used = 0
    for dd in days:
        tr = d.filter(pl.col("day") != dd)
        te = d.filter(pl.col("day") == dd)
        tr = L.prep(tr)
        if tr["leave"].sum() < 5 or te.height == 0:
            continue
        te = te.filter(pl.col("agent").is_in(tr["agent"].unique().implode()))
        if te.height == 0:
            continue
        ll = {}
        ok = True
        for m in ("O1", "O2"):
            r = L.fit(tr, m)
            Xall, names, _, _ = L.design(pl.concat([tr, te]), m, knots=r["knots"], bounds=r["bounds"])
            # align columns by name (constant-column drops can differ between train and the union)
            Xte_full, names_te, _, _ = L.design(te, m, knots=r["knots"], bounds=r["bounds"])
            cols = []
            for nm in r["names"]:
                cols.append(Xte_full[:, names_te.index(nm)] if nm in names_te else np.zeros(te.height))
            Xte = np.column_stack(cols)
            v = L.ll_rows(r, Xte, np.log(te["calls"].to_numpy().astype(float)), te["agent"].to_numpy(),
                          te["leave"].to_numpy().astype(float))
            if not np.all(np.isfinite(v)):
                ok = False
                break
            ll[m] = float(v.sum())
        if not ok:
            continue
        tot["O1"] += ll["O1"]
        tot["O2"] += ll["O2"]
        n_leave += int(te["leave"].sum())
        used += 1
    if n_leave == 0:
        return {"delta_per_leave": None, "n_leaves_scored": 0, "folds": used}
    return {"delta_per_leave": (tot["O2"] - tot["O1"]) / n_leave, "n_leaves_scored": n_leave, "folds": used,
            "z_wins": bool(tot["O2"] > tot["O1"])}


def ref_rate(d: pl.DataFrame) -> dict:
    """O4's r_u: cloglog with an intercept and the stay covariates on all at-risk rows (no agent effects, no q terms),
    evaluated at the reference (dwell 100 calls, a_a = 0, no own mark, non-owner); per 100 own calls."""
    dd = d.with_columns(pl.when((pl.col("calls") == 0) & (pl.col("leave") == 1)).then(1).otherwise(pl.col("calls"))
                        .alias("calls")).filter(pl.col("calls") > 0)
    y = dd["leave"].to_numpy().astype(float)
    X = np.column_stack([np.log1p(dd["dwell"].to_numpy().astype(float)) - np.log1p(100.0),
                         np.log1p(dd["a_a"].to_numpy().astype(float)), dd["own_prev"].to_numpy().astype(float),
                         dd["owner"].to_numpy().astype(float)])
    keep = [j for j in range(X.shape[1]) if np.ptp(X[:, j]) > 0]
    X = X[:, keep]
    r = L.cloglog_fe(y, X, np.log(dd["calls"].to_numpy().astype(float)), np.zeros(dd.height, int))
    a0 = list(r["alpha"].values())[0]
    # sandwich SE of the intercept from the full beta: refit-free approximation with the model information
    Z = np.hstack([X, np.ones((dd.height, 1))])
    eta = Z @ np.r_[r["b"], a0] + np.log(dd["calls"].to_numpy().astype(float))
    e = np.exp(np.clip(eta, -30, 5))
    S = np.exp(-e)
    mu = np.clip(1 - S, 1e-12, 1 - 1e-12)
    w = (e * S) ** 2 / (mu * (1 - mu))
    u = y * e * S / mu - (1 - y) * e
    Hinv = np.linalg.pinv((Z * w[:, None]).T @ Z)
    ag = dd["agent"].to_numpy()
    lev, inv = np.unique(ag, return_inverse=True)
    Sc = np.zeros((len(lev), Z.shape[1]))
    np.add.at(Sc, inv, Z * u[:, None])
    cov = Hinv @ (Sc.T @ Sc * len(lev) / max(len(lev) - 1, 1)) @ Hinv
    se = float(np.sqrt(cov[-1, -1]))
    qbar = float((dd["q_live"] * dd["calls"]).sum() / dd["calls"].sum())
    return {"r_ref": float(100 * np.exp(a0)), "ln_r": float(a0 + np.log(100)), "se_ln_r": se, "qbar": qbar,
            "raw_rate": float(100 * y.sum() / dd["calls"].sum()), "leaves": int(y.sum()), "calls": int(dd["calls"].sum())}


def wls(X, y, w):
    Wx = X * w[:, None]
    return np.linalg.solve(X.T @ Wx, Wx.T @ y)


# ============================================================================================ unit-level covariates
def unit_covariates(units: list[str]) -> dict:
    e = pl.read_parquet(SHARED / "per_period_estimates.parquet")
    n85 = e.filter((pl.col("hypothesis") == "H85") & (pl.col("statistic") == "active_population_N"))
    pu = pl.read_parquet(SHARED / "period_units.parquet")
    lam = e.filter((pl.col("hypothesis") == "H94") & (pl.col("statistic") == "maxent_lambda_own_nats"))
    out = {}
    for u in units:
        g = goal_of(u)
        if g == 51 or u in ("36a",):
            ids = [u]
        elif u == "36bc":
            ids = ["36b", "36c"]
        else:
            ids = pu.filter(pl.col("goal_no") == g)["unit_id"].to_list()
        x = n85.filter(pl.col("period_unit").is_in(ids)).join(pu.select(pl.col("unit_id").alias("period_unit"), "n_days"),
                                                               on="period_unit")
        N = float((x["estimate"] * x["n_days"]).sum() / x["n_days"].sum()) if x.height else None
        lx = lam.filter(pl.col("period_unit").is_in(ids) if g == 51 else (pl.col("goal_no") == g))
        lam_own = float(lx["estimate"].mean()) if lx.height else None
        pi = None
        rp = L.ROOT / f"data/processed/H54-kickoff-quench-target/G{g:02d}/results.json"
        if rp.exists():
            pi = json.loads(rp.read_text()).get("pi")
        out[u] = {"N_active": N, "lambda_own": lam_own, "lambda_units": lx["period_unit"].to_list(), "pi_H54": pi,
                  "own_role": int(g in L.OWN_ROLE)}
    return out


# ============================================================================================ main
def run_channel(ch: str, args, rng) -> dict:
    data = load_channel(ch)
    cov = unit_covariates(list(data))
    U = {}
    for u, d in data.items():
        t0 = time.time()
        nl = int(d["leave"].sum())
        res = {"unit": u, "goal": goal_of(u), "channel": ch, "leaves": nl, "rows": d.height,
               "testable": nl >= L.MIN_LEAVES, **cov[u]}
        res.update({f"O6_{k}": v for k, v in ref_rate(d).items()})
        lv = d.filter(pl.col("leave") == 1)
        res["O6_share_to_newborn"] = float((lv["to_new"] == 1).sum() / max((lv["to_new"] >= 0).sum(), 1)) if "to_new" in d.columns else None
        dp = L.prep(d)
        if dp["leave"].sum() >= 3 and dp["agent"].n_unique() >= 2:
            r1 = L.fit(dp, "O1")
            c = L.coef(r1, "lnq")
            res.update({"eps_q": c["est"], "eps_se": c["se"], "eps_lo": c["lo"], "eps_hi": c["hi"], "eps_p": c["p"],
                        "G": r1["G"], "df": c.get("df")})
            for nm in ("lndwell", "lnaa", "own_prev", "owner", "q0"):
                k = L.coef(r1, nm)
                res[f"b_{nm}"], res[f"b_{nm}_se"], res[f"b_{nm}_lo"], res[f"b_{nm}_hi"] = k["est"], k["se"], k["lo"], k["hi"]
            r2 = L.fit(dp, "O2")
            k = L.coef(r2, "lnZ")
            res.update({"eps_Z": k["est"], "epsZ_se": k["se"], "epsZ_lo": k["lo"], "epsZ_hi": k["hi"]})
            r3 = L.fit(dp, "O3")
            k3 = L.contrast(r3, "lnq", "lnlead")
            res.update({"o3_eps_q": L.coef(r3, "lnq")["est"], "o3_eps_lead": L.coef(r3, "lnlead")["est"],
                        "o3_diff_sandwich": k3["est"], "o3_diff_sandwich_se": k3["se"]})
            # variants (named in the card)
            for qv in ("q_cum", "q_room", "q_read"):
                kv = L.coef(L.fit(dp, "O1", qv), "lnq")
                res[f"var_{qv}"], res[f"var_{qv}_lo"], res[f"var_{qv}_hi"] = kv["est"], kv["lo"], kv["hi"]
            dnf = dp.with_columns(pl.when(pl.col("q_named") > 0).then(pl.col("q_named").cast(pl.Float64).log()).otherwise(0.0).alias("ln_named"),
                                  pl.when(pl.col("q_free") > 0).then(pl.col("q_free").cast(pl.Float64).log()).otherwise(0.0).alias("ln_free"),
                                  (pl.col("q_named") == 0).cast(pl.Float64).alias("named0"),
                                  (pl.col("q_free") == 0).cast(pl.Float64).alias("free0"))
            rnf = L.fit(dnf, "base", extra=["ln_named", "ln_free", "named0", "free0"])
            for nm in ("ln_named", "ln_free"):
                kv = L.coef(rnf, nm)
                res[f"var_{nm}"], res[f"var_{nm}_lo"], res[f"var_{nm}_hi"] = kv["est"], kv["lo"], kv["hi"]
            kp = L.coef(L.fit(dp, "O1", link="poisson"), "lnq")
            res["var_poisson_eps"], res["var_poisson_lo"], res["var_poisson_hi"] = kp["est"], kp["lo"], kp["hi"]
            if res["testable"]:
                # O3 paired agent-cluster bootstrap
                bs = agent_boot(dp, lambda db: (lambda r: L.coef(r, "lnq")["est"] - L.coef(r, "lnlead")["est"])(L.fit(db, "O3")),
                                args.boot, rng)
                bs = np.array([b for b in bs if b is not None and np.isfinite(b)])
                res.update({"o3_diff": k3["est"], "o3_diff_boot_se": float(bs.std(ddof=1)) if len(bs) > 2 else None,
                            "o3_diff_lo": float(np.percentile(bs, 2.5)) if len(bs) > 2 else None,
                            "o3_diff_hi": float(np.percentile(bs, 97.5)) if len(bs) > 2 else None, "o3_nboot": int(len(bs))})
                # N1 permutation null
                if args.perm:
                    pn = perm_null(dp, args.perm, rng)
                    pn = pn[np.isfinite(pn)]
                    res["perm_p"] = float((1 + (np.abs(pn) >= abs(c["est"])).sum()) / (1 + len(pn)))
                    res["perm_sd"] = float(pn.std())
                    res["perm_mean"] = float(pn.mean())
                res["O2_oof"] = oof_score(dp)
        U[u] = res
        print(f"{ch} {u}: leaves {nl} eps {res.get('eps_q')} ({time.time() - t0:.0f}s)", flush=True)
    return U


def pool(units: list[dict], est: str, se: str) -> dict:
    e = np.array([u.get(est) if u.get(est) is not None else np.nan for u in units], float)
    s = np.array([u.get(se) if u.get(se) is not None else np.nan for u in units], float)
    return L.dl_pool(e, s)


def o4(units: list[dict], with_pi=False, B=2000, seed=11) -> dict:
    us = [u for u in units if u.get("testable") and u.get("N_active") and u.get("O6_qbar", 0) > 0
          and (not with_pi or u.get("pi_H54") is not None)]
    if len(us) < 5:
        return {"n_units": len(us), "b_q": None}
    y = np.array([u["O6_ln_r"] for u in us])
    se = np.array([u["O6_se_ln_r"] for u in us])
    cols = [np.ones(len(us)), np.log([u["O6_qbar"] for u in us]), np.log([u["N_active"] for u in us]),
            np.array([u["own_role"] for u in us], float)]
    if with_pi:
        cols.append(np.array([u["pi_H54"] for u in us], float))
    X = np.column_stack(cols)
    keep = [j for j in range(X.shape[1]) if j == 0 or np.ptp(X[:, j]) > 0]
    X = X[:, keep]
    w = 1 / (se ** 2 + TAU ** 2)
    b = wls(X, y, w)
    rng = np.random.default_rng(seed)
    bs = []
    for _ in range(B):
        i = rng.integers(0, len(us), len(us))
        if np.linalg.matrix_rank(X[i]) < X.shape[1]:
            continue
        bs.append(wls(X[i], y[i], w[i])[1])
    lo, hi = np.percentile(bs, [2.5, 97.5])
    # flat baseline (b_q = 0) with the same covariates: weighted RSS comparison
    X0 = np.delete(X, 1, axis=1)
    b0 = wls(X0, y, w)
    rss1 = float((w * (y - X @ b) ** 2).sum())
    rss0 = float((w * (y - X0 @ b0) ** 2).sum())
    return {"n_units": len(us), "b_q": float(b[1]), "lo": float(lo), "hi": float(hi), "wrss": rss1, "wrss_flat": rss0,
            "units": [u["unit"] for u in us]}


def natives(W: dict, A: dict) -> dict:
    out = {}
    # ---- N1 G38: tercile check
    d = L.prep(pl.read_parquet(L.D / "G38" / "windows_work.parquet"))
    u = W["38"]
    x = d.filter(pl.col("q_live") >= 1)
    q = x["q_live"].to_numpy()
    lo_t, hi_t = np.quantile(q, [1 / 3, 2 / 3])
    bot = x.filter(pl.col("q_live") <= lo_t)
    top = x.filter(pl.col("q_live") >= hi_t)
    h_b = bot["leave"].sum() / bot["calls"].sum()
    h_t = top["leave"].sum() / top["calls"].sum()
    qb, qt = float(bot["q_live"].mean()), float(top["q_live"].mean())
    obs = float(h_t / h_b) if h_b > 0 else None
    pred = float((qt / qb) ** u["eps_q"]) if u.get("eps_q") is not None else None
    out["N1_G38"] = {"eps_q": u.get("eps_q"), "eps_lo": u.get("eps_lo"), "eps_hi": u.get("eps_hi"),
                     "tercile_cut": [float(lo_t), float(hi_t)], "q_bot": qb, "q_top": qt,
                     "leaves_bot": int(bot["leave"].sum()), "leaves_top": int(top["leave"].sum()),
                     "h_bot_per100": 100 * float(h_b), "h_top_per100": 100 * float(h_t), "ratio_obs": obs,
                     "ratio_pred": pred, "obs_over_pred": (obs / pred) if (obs and pred) else None}
    # ---- N2 G44: rooms #best (2) and #rest (3)
    d = pl.read_parquet(L.D / "G44" / "windows_work.parquet")
    d = d.with_columns(pl.when((pl.col("calls") == 0) & (pl.col("leave") == 1)).then(1).otherwise(pl.col("calls")).alias("calls")).filter(pl.col("calls") > 0)
    d = d.filter(pl.col("room").is_in([2, 3]))
    nb = int(d.filter(pl.col("room") == 2)["leave"].sum())
    nr = int(d.filter(pl.col("room") == 3)["leave"].sum())
    y = d["leave"].to_numpy().astype(float)
    X = np.column_stack([(d["room"] == 3).to_numpy().astype(float), d["owner"].to_numpy().astype(float),
                         np.log1p(d["dwell"].to_numpy().astype(float)), np.log1p(d["a_a"].to_numpy().astype(float)),
                         d["own_prev"].to_numpy().astype(float)])
    r = L.cloglog_fe(y, X, np.log(d["calls"].to_numpy().astype(float)), np.zeros(d.height, int))
    # cluster by agent (refit SE): use a one-intercept fit with agent-cluster sandwich via the poisson-style helper
    ag = d["agent"].to_numpy()
    rr = cluster_cov(r, X, d, ag)
    se = float(np.sqrt(rr[0, 0]))
    Gc = len(np.unique(ag))
    tq = float(stats.t.ppf(0.975, max(Gc - 1, 1)))
    b = float(r["b"][0])
    qr_b = float(d.filter(pl.col("room") == 2)["q_room"].mean())
    qr_r = float(d.filter(pl.col("room") == 3)["q_room"].mean())
    pred = qr_r / qr_b if qr_b > 0 else None
    obs = float(np.exp(b))
    out["N2_G44"] = {"leaves_best": nb, "leaves_rest": nr, "testable": bool(nb >= 25 and nr >= 25),
                     "hr_rest_over_best": obs, "hr_lo": float(np.exp(b - tq * se)), "hr_hi": float(np.exp(b + tq * se)),
                     "qroom_best": qr_b, "qroom_rest": qr_r, "pred_ratio": pred,
                     "obs_over_pred": obs / pred if pred else None, "G": Gc,
                     "raw_rate_best_per100": 100 * nb / float(d.filter(pl.col("room") == 2)["calls"].sum()),
                     "raw_rate_rest_per100": 100 * nr / float(d.filter(pl.col("room") == 3)["calls"].sum())}
    # ---- N3 G51
    u51 = [v for k, v in W.items() if k.startswith("51") and v.get("eps_q") is not None]
    out["N3_G51"] = {"pool_all_fitted": pool(u51, "eps_q", "eps_se"),
                     "pool_testable": pool([v for v in u51 if v["testable"]], "eps_q", "eps_se"),
                     "pool_owner": pool([v for v in u51 if v.get("b_owner") is not None], "b_owner", "b_owner_se"),
                     "n_units": len(u51)}
    return out


def cluster_cov(r, X, d, ag):
    a0 = list(r["alpha"].values())[0]
    Z = np.hstack([X, np.ones((X.shape[0], 1))])
    y = d["leave"].to_numpy().astype(float)
    eta = Z @ np.r_[r["b"], a0] + np.log(d["calls"].to_numpy().astype(float))
    e = np.exp(np.clip(eta, -30, 5))
    S = np.exp(-e)
    mu = np.clip(1 - S, 1e-12, 1 - 1e-12)
    w = (e * S) ** 2 / (mu * (1 - mu))
    u = y * e * S / mu - (1 - y) * e
    Hinv = np.linalg.pinv((Z * w[:, None]).T @ Z)
    lev, inv = np.unique(ag, return_inverse=True)
    Sc = np.zeros((len(lev), Z.shape[1]))
    np.add.at(Sc, inv, Z * u[:, None])
    return Hinv @ (Sc.T @ Sc * len(lev) / max(len(lev) - 1, 1)) @ Hinv


def score(ch: str, U: dict, syn: dict) -> dict:
    T = [u for u in U.values() if u["testable"] and u.get("eps_q") is not None]
    p_eps = pool(T, "eps_q", "eps_se")
    n_pos = sum(1 for u in T if u["eps_lo"] is not None and u["eps_lo"] > 0)
    p_Z = pool(T, "eps_Z", "epsZ_se")
    zw = [u["O2_oof"]["z_wins"] for u in T if u.get("O2_oof") and u["O2_oof"].get("delta_per_leave") is not None]
    p_d = pool(T, "o3_diff", "o3_diff_boot_se")
    both = [u for u in T if u.get("b_owner") is not None and u.get("lambda_own")]
    rown = [u["b_owner"] / (-u["lambda_own"]) for u in both]
    power = syn.get(ch, {}).get("W1h", {}).get("pooled_all", {}).get("ci_above0")
    P1 = (n_pos >= (2 / 3) * len(T)) and p_eps["lo"] is not None and p_eps["lo"] > 0 and p_eps["lo"] <= 1 <= p_eps["hi"]
    P1_against = p_eps["lo"] is None or p_eps["lo"] <= 0
    P2 = (p_Z["est"] is not None and 0.5 <= p_Z["est"] <= 1.5 and len(zw) > 0 and sum(zw) >= len(zw) / 2)
    P2_against = (p_Z["lo"] is not None and (p_Z["hi"] < 0.5 or p_Z["lo"] > 1.5)) or (len(zw) > 0 and sum(zw) < len(zw) / 2)
    P3 = p_d["lo"] is not None and p_d["lo"] > 0
    P4 = len(rown) > 0 and sum(1 for x in rown if 0.5 <= x <= 2) >= len(rown) / 2
    kill = bool(P1_against and power is not None and power >= 0.8)
    return {"n_testable": len(T), "units_ci_above0": n_pos, "pool_eps_q": p_eps, "pool_eps_Z": p_Z,
            "oof_z_wins": int(sum(zw)), "oof_n": len(zw), "pool_o3_diff": p_d, "R_own": dict(zip([u["unit"] for u in both], rown)),
            "P1_pass": bool(P1), "P1_counts_against": bool(P1_against), "P2_pass": bool(P2), "P2_counts_against": bool(P2_against),
            "P3_pass": bool(P3), "P4_pass": bool(P4), "synthetic_power_eps05": power, "kill_fires": kill,
            "verdict": ("supported" if (P1 and P3 and not kill) else "narrowed" if (P1 and not P3) else
                        "failed" if kill else "inconclusive")}


def estimates_rows(U: dict, ch: str) -> list[dict]:
    rows = []
    pu = pl.read_parquet(SHARED / "period_units.parquet")
    for u, r in U.items():
        g = r["goal"]
        if u.startswith("51") or u == "36a":
            unit, ul, fd, ld = u, None, None, None
        elif u == "36bc":
            unit, ul = "local:36bc", "36bc"
            fd, ld = "2026-03-24", "2026-03-27"
        else:
            unit, ul, fd, ld = f"G{g:02d}", None, None, None
        base = {"period_unit": unit, "goal_no": g, "channel": f"{ch} (host W30 E100)" if ch == "work" else "attention (project_states W30)",
                "role": "replication", "unit_local": ul, "first_day": fd, "last_day": ld, "post_hoc": False,
                "status": "testable" if r["testable"] else "descriptive (<25 leaves)", "source": "hypotheses/H138-glauber-escape-vs-options/analysis/run.py"}
        if r.get("eps_q") is not None:
            rows.append({**base, "statistic": "h138_option_elasticity", "estimate": r["eps_q"], "ci_lo": r["eps_lo"],
                         "ci_hi": r["eps_hi"], "se": r["eps_se"], "n": float(r["leaves"]), "n_kind": "leaves",
                         "ci_kind": "se_t", "ci_level": 0.95, "method": "cloglog per-call hazard, agent FE, ns(active time, 3 df), agent-cluster sandwich t(G-1)",
                         "null": "eps_q = 0 (Wald); N1 within-agent-day permutation p=" + (f"{r['perm_p']:.3f}" if r.get("perm_p") is not None else "n/a")})
            rows.append({**base, "statistic": "h138_altsum_elasticity", "estimate": r["eps_Z"], "ci_lo": r["epsZ_lo"],
                         "ci_hi": r["epsZ_hi"], "se": r["epsZ_se"], "n": float(r["leaves"]), "n_kind": "leaves",
                         "ci_kind": "se_t", "ci_level": 0.95, "method": "O1 with ln Z_alt (cross-fitted H11-r2 join utilities)",
                         "null": "eps_Z = 0"})
            if r.get("o3_diff_lo") is not None:
                rows.append({**base, "statistic": "h138_lead_placebo_diff", "estimate": r["o3_diff"], "ci_lo": r["o3_diff_lo"],
                             "ci_hi": r["o3_diff_hi"], "se": r["o3_diff_boot_se"], "n": float(r["leaves"]), "n_kind": "leaves",
                             "ci_kind": "percentile", "ci_level": 0.95, "method": "eps_q - eps_lead, paired agent-cluster bootstrap (500)",
                             "null": "difference = 0 (R-coarrival)"})
            if r.get("b_owner") is not None:
                rows.append({**base, "statistic": "h138_owner_log_ratio", "estimate": r["b_owner"], "ci_lo": r["b_owner_lo"],
                             "ci_hi": r["b_owner_hi"], "se": r["b_owner_se"], "n": float(r["leaves"]), "n_kind": "leaves",
                             "ci_kind": "se_t", "ci_level": 0.95, "method": "owner coefficient in O1 (H94 owner rule)",
                             "null": "beta_own = 0"})
        se = r["O6_se_ln_r"]
        rows.append({**base, "statistic": "h138_leave_rate_ref", "estimate": r["O6_r_ref"],
                     "ci_lo": float(np.exp(r["O6_ln_r"] - 1.96 * se) if se else None) if se else None,
                     "ci_hi": float(np.exp(r["O6_ln_r"] + 1.96 * se)) if se else None, "se": None,
                     "n": float(r["leaves"]), "n_kind": "leaves", "ci_kind": "se_z", "ci_level": 0.95,
                     "method": "leaves per 100 own calls at dwell 100, a_a 0, no own mark, non-owner (cloglog, intercept + stay covariates)",
                     "null": "none (descriptive)"})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perm", type=int, default=1000)
    ap.add_argument("--boot", type=int, default=500)
    ap.add_argument("--no-estimates", action="store_true")
    a = ap.parse_args()
    RES.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20261008)
    syn = json.loads((L.D / "synthetic" / "summary.json").read_text())
    W = run_channel("work", a, rng)
    A = run_channel("attention", a, rng)
    out = {"work": {"units": W, "score": score("work", W, syn), "O4": o4(list(W.values())),
                    "O4_pi": o4(list(W.values()), with_pi=True)},
           "attention": {"units": A, "score": score("attention", A, syn), "O4": o4(list(A.values())),
                         "O4_pi": o4(list(A.values()), with_pi=True)}}
    out["natives"] = natives(W, A)
    (RES / "results.json").write_text(json.dumps(out, indent=1, default=float))
    flat = [{k: v for k, v in u.items() if not isinstance(v, (dict, list))} for ch in ("work", "attention")
            for u in out[ch]["units"].values()]
    pl.DataFrame(flat, infer_schema_length=None).write_parquet(RES / "units.parquet")
    print(json.dumps({ch: out[ch]["score"] for ch in ("work", "attention")}, indent=1, default=float))
    print(json.dumps({k: out[k]["O4"] for k in ("work", "attention")}, indent=1, default=float)[:2000])
    print(json.dumps(out["natives"], indent=1, default=float))
    if not a.no_estimates:
        import estimates as E
        rows = estimates_rows(W, "work") + estimates_rows(A, "attention")
        nat = out["natives"]
        n1 = nat["N1_G38"]
        if n1.get("obs_over_pred") is not None:
            rows.append({"period_unit": "G38", "goal_no": 38, "channel": "work (host W30 E100)", "role": "native",
                         "statistic": "h138_tercile_ratio_obs_over_pred", "estimate": n1["obs_over_pred"], "ci_lo": None,
                         "ci_hi": None, "n": float(n1["leaves_bot"] + n1["leaves_top"]), "n_kind": "leaves", "ci_kind": "none",
                         "method": "top/bottom q_live tercile hazard ratio over (q ratio)^eps_q", "null": "within x1.5 of 1"})
        n2 = nat["N2_G44"]
        rows.append({"period_unit": "G44", "goal_no": 44, "channel": "work (host W30 E100)", "role": "native",
                     "statistic": "h138_room_hazard_ratio_rest_best", "estimate": n2["hr_rest_over_best"], "ci_lo": n2["hr_lo"],
                     "ci_hi": n2["hr_hi"], "n": float(n2["leaves_best"] + n2["leaves_rest"]), "n_kind": "leaves",
                     "ci_kind": "se_t", "ci_level": 0.95, "method": "cloglog per-call hazard, room + owner + stay covariates, agent-cluster sandwich",
                     "null": f"predicted (q_room ratio) {n2['pred_ratio']:.2f}"})
        p3 = nat["N3_G51"]["pool_all_fitted"]
        rows.append({"period_unit": "G51", "goal_no": 51, "channel": "work (host W30 E100)", "role": "native",
                     "statistic": "h138_option_elasticity_pooled", "estimate": p3["est"], "ci_lo": p3["lo"], "ci_hi": p3["hi"],
                     "se": p3["se"], "n": float(p3["k"]), "n_kind": "units", "ci_kind": "se_z", "ci_level": 0.95,
                     "method": "DerSimonian-Laird pool of per-unit eps_q over 51a-51l (non-reserved)", "null": "eps_q = 0"})
        E.write_estimates(rows, hypothesis="H138")
        print(f"wrote {len(rows)} estimates rows")


if __name__ == "__main__":
    main()
