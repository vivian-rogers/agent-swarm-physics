"""H104 replication: per eligible non-holdout period and channel (work, attention), the step response X, tail
statistics (V, F_A, deconvolution tau), quiet-window dispersion D and burst ratio BR, dose (message count, novelty,
broadcast), pre-step placebo, read-out split and kickoff ratio K. Variants: W = 30 / 120 min, all-present trim, all
steps (not only isolated), switch counts C.

    uv run python hypotheses/H104-barkhausen-avalanches/analysis/run_periods.py
Output: data/processed/H104-barkhausen-avalanches/results/{periods.parquet, steps.parquet, pooled.json}
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h104lib as L  # noqa: E402

RES = L.DATA / "results"
NDRAW = 999
VARIANTS = [("primary", dict(W=3600.0, trim="span", isolated=True, size="S")),
            ("W30", dict(W=1800.0, trim="span", isolated=True, size="S")),
            ("W120", dict(W=7200.0, trim="span", isolated=True, size="S")),
            ("allpresent", dict(W=3600.0, trim="allpresent", isolated=True, size="S")),
            ("allsteps", dict(W=3600.0, trim="span", isolated=False, size="S")),
            ("counts", dict(W=3600.0, trim="span", isolated=True, size="C"))]


def readout_split(P, st, ad, sw, rot_draws):
    """Switch rate after vs before each at-risk agent's receiving call, within (t_k, t_k + W]; ratio / null ratio."""
    rc = P.get("step_receipts")
    if rc is None or rc.height == 0:
        return {}
    W = 3600.0
    lo, hi, dd, ag = (ad[c].to_numpy() for c in ("risk_lo", "risk_hi", "pt_date", "agent"))
    swt = {}
    for a_, t_ in zip(sw["ad"].to_numpy(), sw["t"].to_numpy()):
        swt.setdefault(int(a_), []).append(t_)
    cells = []
    rcd = {(r["session"], r["agent"]): r["t_read"] for r in rc.iter_rows(named=True)}
    for r in st.iter_rows(named=True):
        t = r["t"]
        for a in np.flatnonzero((dd == r["pt_date"]) & (lo <= t) & (hi >= t + W)):
            tr = rcd.get((r["session"], int(ag[a])))
            if tr is None or tr <= t or tr >= t + W:
                continue
            cells.append((int(a), t, tr))
    if not cells:
        return {}

    def ratio(times):
        nb = na = eb = ea = 0.0
        for a, t, tr in cells:
            x = np.asarray(times.get(a, []))
            nb += ((x > t) & (x <= tr)).sum()
            na += ((x > tr) & (x <= t + W)).sum()
            eb += tr - t
            ea += t + W - tr
        return ((na + 0.5) / ea) / ((nb + 0.5) / eb), nb, na, eb, ea
    obs, nb, na, eb, ea = ratio(swt)
    nulls = []
    for tt in rot_draws:
        d = {}
        for a_, t_ in zip(tt[0], tt[1]):
            d.setdefault(int(a_), []).append(t_)
        nulls.append(ratio(d)[0])
    nulls = np.asarray(nulls)
    return {"RR_read": float(obs), "RR_null_mean": float(nulls.mean()), "RR_rel": float(obs / nulls.mean()),
            "p_RR": float((1 + (nulls >= obs).sum()) / (1 + len(nulls))), "n_cells": len(cells),
            "n_before": int(nb), "n_after": int(na), "min_before": eb / 60, "min_after": ea / 60}


def kickoff_ratio(P, channel):
    k = P.get("kickoffs")
    if k is None or k.height == 0:
        return {}
    kd = k["pt_date"][0]
    sp = P["spans"]
    ds = P[f"daystart_{channel}"]
    sw = P[f"switches_{channel}"]
    first = sp.select("pt_date", "agent", "first_call")
    a = (ds.filter(pl.col("switch")).join(first, on=["pt_date", "agent"], how="inner")
         .filter((pl.col("t") - pl.col("first_call")) <= 7200).select("pt_date", "agent"))
    b = (sw.join(first, on=["pt_date", "agent"], how="inner").filter((pl.col("t") - pl.col("first_call")) <= 7200)
         .select("pt_date", "agent"))
    sw_ag = pl.concat([a, b]).unique()
    per_day = first.group_by("pt_date").agg(pl.len().alias("n")).join(
        sw_ag.group_by("pt_date").agg(pl.len().alias("k")), on="pt_date", how="left").with_columns(
        (pl.col("k").fill_null(0) / pl.col("n")).alias("frac"))
    fk = per_day.filter(pl.col("pt_date") == kd)["frac"]
    fo = per_day.filter(pl.col("pt_date") != kd)["frac"]
    if fk.len() == 0 or fo.len() == 0:
        return {}
    return {"K": float(fk[0] / fo.mean()) if fo.mean() > 0 else np.inf, "frac_kick": float(fk[0]),
            "frac_other": float(fo.mean()), "n_other_days": fo.len()}


def run(args):
    g, channel = args
    P = L.load_period(g)
    rows, steprows = [], []
    for vname, v in VARIANTS:
        W = v["W"]
        ad = L.agent_days(P, v["trim"])
        sw = L.switches_in(P, channel, ad)
        st = L.eligible_steps(P, ad, W, isolated=v["isolated"])
        if st.height < 3 or sw.height < 30:
            if vname == "primary":
                rows.append({"g": g, "channel": channel, "variant": vname, "eligible": False,
                             "n_steps": st.height, "n_switches": sw.height})
                return rows, steprows
            continue
        pan = L.Panel(ad, sw, st["t"].to_numpy(), W, st["pt_date"].to_numpy())
        S, C = pan.counts(pan.sw_t)
        Sn, Cn = pan.null(NDRAW, seed=g)
        Y, Yn = (S, Sn) if v["size"] == "S" else (C, Cn)
        r = {"g": g, "channel": channel, "variant": vname, "eligible": True, "n_steps": len(S), "n_switches": sw.height,
             "n_agent_days": ad.height, "mean_risk": float(pan.n_at_risk.mean())}
        sr = L.step_response(Y, Yn, B=2000, seed=g)
        r.update({k: sr[k] for k in ("X", "p_X", "V", "p_V", "F_A", "excess", "mean_obs", "mean_null")})
        r["X_lo"], r["X_hi"] = sr["X_ci"]
        r["V_lo"], r["V_hi"] = sr["V_ci"]
        r["F_A_lo"], r["F_A_hi"] = sr["F_A_ci"]
        if vname == "primary":
            t = L.tau_mle(S, Sn, pan.n_at_risk)
            r.update({"tau": t["tau"], "tau_lo": t["tau_lo"], "tau_hi": t["tau_hi"], "pi": t["pi"], "llr": t["llr_vs_null"],
                      "tau_edge": t["at_edge"]})
            # quiet windows
            q0, qd = L.quiet_windows(P, ad, W)
            if len(q0) >= 5:
                pq = L.Panel(ad, sw, q0, W, qd)
                Sq, _ = pq.counts(pq.sw_t)
                Sqn, _ = pq.null(NDRAW, seed=g + 1)
                dsp = L.dispersion(Sq, Sqn)
                br = L.burst_ratio(S, Sn, Sq, Sqn, B=2000, seed=g)
                r.update({"D": dsp["D"], "D_lo": dsp["D_band"][0], "D_hi": dsp["D_band"][1], "p_D": dsp["p_D"],
                          "n_quiet": len(Sq), "BR": br["BR"], "BR_lo": br["BR_ci"][0], "BR_hi": br["BR_ci"][1],
                          "exceed_post": br["exceed_post"], "exceed_quiet": br["exceed_quiet"],
                          "quiet_mean_obs": float(Sq.mean()), "quiet_mean_null": float(Sqn.mean())})
            # dose
            dz = L.dose(st["m"].to_numpy(), S, Sn)
            r.update({"rho_m": dz["rho"], "p_rho_m": dz["p"]})
            nv = st["novelty"].to_numpy().astype(float)
            ok = np.isfinite(nv)
            if ok.sum() >= 4:
                dn = L.dose(nv[ok], S[ok], Sn[:, ok])
                r.update({"rho_nov": dn["rho"], "p_rho_nov": dn["p"], "n_nov": int(ok.sum())})
            E = S - Sn.mean(0)
            bc = st["broadcast"].to_numpy()
            if bc.any() and (~bc).any():
                r.update({"E_broadcast": float(E[bc].mean()), "E_addressed": float(E[~bc].mean()),
                          "n_broadcast": int(bc.sum())})
            # pre-step placebo
            pp = L.Panel(ad, sw, st["t"].to_numpy() - W, W, st["pt_date"].to_numpy())
            Sp, _ = pp.counts(pp.sw_t)
            Spn, _ = pp.null(NDRAW, seed=g + 2)
            ps = L.tail_stats(Sp, Spn)
            r.update({"X_pre": ps["X"], "p_X_pre": float((1 + (Spn.mean(1) >= Sp.mean()).sum()) / (1 + NDRAW))})
            # read-out split (199 rotations)
            rng = np.random.default_rng(g + 3)
            draws = [(pan.sw_ad, pan.rotate(rng)) for _ in range(199)]
            r.update(readout_split(P, st, ad, sw, draws))
            r.update(kickoff_ratio(P, channel))
            for k_, row in enumerate(st.iter_rows(named=True)):
                steprows.append({"g": g, "channel": channel, "session": row["session"], "t": row["t"], "pt_date": row["pt_date"],
                                 "m": row["m"], "broadcast": row["broadcast"], "novelty": row["novelty"], "room": row["room"],
                                 "n_risk": int(pan.n_at_risk[k_]), "S": float(S[k_]), "S_null_mean": float(Sn[:, k_].mean()),
                                 "S_null_q95": float(np.percentile(Sn[:, k_], 95))})
        rows.append(r)
    return rows, steprows


def main():
    RES.mkdir(parents=True, exist_ok=True)
    per = pl.read_parquet(L.DATA / "periods.parquet")
    jobs = [(g, ch) for g in per["goal_no"].to_list() for ch in ("work", "attn")]
    t0 = time.time()
    with ProcessPoolExecutor(2) as ex:
        out = list(ex.map(run, jobs))
    rows = [r for rr, _ in out for r in rr]
    srows = [s for _, ss in out for s in ss]
    df = pl.DataFrame(rows, infer_schema_length=None)
    df.write_parquet(RES / "periods.parquet")
    if srows:
        pl.DataFrame(srows, infer_schema_length=None).write_parquet(RES / "steps.parquet")
    pooled = pool(df)
    (RES / "pooled.json").write_text(json.dumps(pooled, indent=1, default=float))
    print(df.filter(pl.col("eligible") & (pl.col("variant") == "primary")).select(
        "g", "channel", "n_steps", "X", "p_X", "V", "F_A", "F_A_lo", "tau", "tau_lo", "tau_hi", "D", "BR", "BR_lo", "rho_m",
        "X_pre", "K"))
    print(json.dumps(pooled, indent=1, default=float))
    print(f"done in {time.time() - t0:.0f} s")


def pool(df: pl.DataFrame) -> dict:
    out = {}
    for (ch, var), g in df.filter(pl.col("eligible")).group_by(["channel", "variant"]):
        o = {"k": g.height}
        se = [L.log_ci_se((lo, hi)) for lo, hi in zip(g["X_lo"].to_list(), g["X_hi"].to_list())]
        o["logX"] = L.re_pool(np.log(g["X"].to_numpy()), se)
        sev = [L.log_ci_se((lo, hi)) for lo, hi in zip(g["V_lo"].to_list(), g["V_hi"].to_list())]
        o["logV"] = L.re_pool(np.log(g["V"].to_numpy()), sev)
        if var == "primary":
            t = g.filter(~pl.col("tau_edge"))
            o["tau"] = L.re_pool(t["tau"].to_numpy(), ((t["tau_hi"] - t["tau_lo"]) / 3.92).to_numpy())
            r = g.filter(pl.col("rho_m").is_not_null() & (pl.col("n_steps") > 3))
            o["rho_m"] = L.re_pool(np.arctanh(np.clip(r["rho_m"].to_numpy(), -0.99, 0.99)), 1 / np.sqrt(r["n_steps"].to_numpy() - 3))
            o["n_X_gt1_p05"] = int(((g["X"] > 1) & (g["p_X"] < 0.05)).sum())
            o["n_D_band"] = int(((g["D"] >= 0.8) & (g["D"] <= 1.25)).sum()) if "D" in g.columns else None
            o["n_D"] = int(g["D"].is_not_null().sum()) if "D" in g.columns else 0
            o["n_BR_gt1"] = int((g["BR_lo"] > 1).sum()) if "BR_lo" in g.columns else None
            o["n_K_gt1"] = int((g["K"] > 1).sum()) if "K" in g.columns else None
            o["n_K"] = int(g["K"].is_not_null().sum()) if "K" in g.columns else 0
            if "RR_read" in g.columns:
                rr = g.filter(pl.col("RR_rel").is_not_null())
                o["RR_rel_median"] = float(rr["RR_rel"].median()) if rr.height else None
            if "X_pre" in g.columns:
                xp = g.filter(pl.col("X_pre").is_not_null())
                o["X_pre_median"] = float(xp["X_pre"].median())
        out[f"{ch}|{var}"] = o
    return out


if __name__ == "__main__":
    main()
