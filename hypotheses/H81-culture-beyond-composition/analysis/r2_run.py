"""H81 round 2 on real data (non-holdout; both embedding models). Predictions, nulls and kill rules: card section
"Round 2", written before this script ran. Synthetic thresholds come from r2_synthetic.py outputs.

  R1   C_R1 (read vs placebo record content), mediation M_R / M_U; record ages; goal-bootstrap CI
  R2a  D_adjg with operator directions beyond the centroid removed; 20 placebo removals; retention
  R2b  L_out (outside-topic statements vs size-matched controls), permutation null
  R2c  OU profile under the calendar, documented-hours and goal-count clocks
  R4   H82 boundary regression for every centroid; joint OU fit with H81's block profile; goal jackknife
Output: data/processed/H81-culture-beyond-composition/round2/r2_results.json, r4_gammas_<model>_<regime>.parquet,
pairs_clocks_<model>.parquet
Usage: uv run python hypotheses/H81-culture-beyond-composition/analysis/r2_run.py [--part all|r1|r2a|r2b|r2c|r4]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h81lib as L  # noqa: E402
import r2lib as Q  # noqa: E402
import r2_synthetic as S  # noqa: E402

OUTF = Q.R2 / "r2_results.json"


def syn(part, model):
    p = Q.R2 / f"synthetic_{part}_{model}.json"
    return json.loads(p.read_text()) if p.exists() else None


def record_ages(c, st):
    out = {}
    for nm in ("R", "U"):
        ages = []
        for agent, b, g, f, d in st.ab:
            for x in d[nm]:
                rows = st.rec_idx[(x, agent, f)]
                ages += list(f - c.pan.day[rows])
        out[nm] = {"median_age_days": float(np.median(ages)) if ages else np.nan, "n_record_rows": len(ages)}
    return out


def run_r1(model, rng):
    res = {}
    observed = {"bge_small": 0.237, "gte_modernbert": 0.208}[model]
    sy = syn("r1", model)
    for regime, placebos in (("I", ["U_act"]), ("III", ["U_ledger", "U_act"])):
        c = Q.load(model, regime)
        for plc in placebos:
            st = Q.r1_struct(c, plc)
            o = Q.r1_stats(c, c.X, st, boot=2000, rng=rng)
            o["ages"] = record_ages(c, st)
            if sy:
                s = sy[f"{regime}/{plc}"]
                o["S_ex_q95_C"] = s["S_ex"]["C_R1"]["q95"]; o["S0_q95_C"] = s["S0"]["C_R1"]["q95"]
                o["S_ex_q95_Mdiff"] = s["S_ex"]["M_diff"]["q95"]
                lams = [k for k in s if k.startswith("S_rec_")]
                lam_star = min(lams, key=lambda k: abs(s[k]["D_adjg"]["mean"] - observed))
                o["lam_star"] = lam_star; o["lam_star_D_adjg_mean"] = s[lam_star]["D_adjg"]["mean"]
                o["power_C_at_lam_star"] = s[lam_star]["C_R1"]["pass_vs_S_ex"]
                o["power_C_by_lam"] = {k: s[k]["C_R1"]["pass_vs_S_ex"] for k in lams}
                o["pass_C"] = bool(o["C_R1"] > o["S_ex_q95_C"])
                o["pass_Mdiff"] = bool(o["M_diff"] > o["S_ex_q95_Mdiff"])
            res[f"{regime}/{plc}"] = o
            print(model, regime, plc, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in o.items() if k != "ages"}, flush=True)
    return res


def run_r2a(model, rng):
    res = {}
    sy = syn("r2a", model)
    for regime in ("I", "III"):
        c0 = Q.load(model, regime)
        base = Q.slow(c0.pan, *Q.residuals(c0.pan, c0.X)[:3], c0.kick)[0]["D_adjg"]
        ex = Q.r2a_extra(c0)
        cr = Q.load(model, regime, extra=ex)
        real = Q.slow(cr.pan, *Q.residuals(cr.pan, cr.X)[:3], cr.kick)[0]["D_adjg"]
        pls = []
        for _ in range(20):
            cp = Q.load(model, regime, extra=Q.r2a_extra(c0, rng, placebo=True))
            pls.append(Q.slow(cp.pan, *Q.residuals(cp.pan, cp.X)[:3], cp.kick)[0]["D_adjg"])
        o = {"D_adjg_primary": base, "D_adjg_operator_removed": real, "D_adjg_placebo_mean": float(np.mean(pls)),
             "D_adjg_placebo_sd": float(np.std(pls)), "rho_op": real / base, "rho_pl": float(np.mean(pls)) / base,
             "n_extra_dirs_median": float(np.median([len(v) for v in ex.values()]))}
        if sy:
            o["S0_q95_operator_removed"] = sy[regime]["S0"]["D_real_q95"]
            o["S_ex_retention_real"] = sy[regime]["S_ex"]["retention_real"]
            o["S_ex_retention_plac"] = sy[regime]["S_ex"]["retention_plac"]
            o["survives"] = bool(real > o["S0_q95_operator_removed"])
        o["operator_explains"] = bool(o["rho_op"] <= 0.5 and o["rho_pl"] - o["rho_op"] >= 0.25)
        res[regime] = o
        print(model, regime, {k: round(v, 4) if isinstance(v, float) else v for k, v in o.items()}, flush=True)
    return res


def run_r2b(model, rng):
    res = {}
    for regime in ("I", "III"):
        c = Q.load(model, regime)
        os_ = Q.out_struct(c)
        o = Q.r2b_stats(c, c.X, os_, rng, n_ctl=20, n_perm=200)
        o["pass_outside"] = bool(o["L_out"] > o["perm_q95"])
        res[regime] = o
        print(model, regime, {k: round(v, 4) if isinstance(v, float) else v for k, v in o.items()}, flush=True)
    return res


def run_r2c(model):
    res = {}
    sy = syn("r2c", model)
    for regime in ("I", "III"):
        c = Q.load(model, regime)
        clocks = Q.block_clocks(c)
        scales = Q.clock_scales(c, clocks)
        o = Q.r2c_stats(c, c.X, clocks, scales)
        o["scales"] = scales
        A, B, R, _, _ = Q.residuals(c.pan, c.X)
        U, members, _ = Q.block_U(c.pan, A, B, R)
        T = Q.pair_rows(c.pan, U, members, c.kick, clocks)
        pl.DataFrame(T, schema=["b", "c", "dt", "J", "gs", "s", "s_perp", "w"] + [f"d_{k}" for k in clocks], orient="row") \
            .write_parquet(Q.R2 / f"pairs_clocks_{model}_{regime}.parquet")
        # era split (descriptive): calendar tau within the 2-3 h era (blocks before 2025-11-01) vs the 4 h era
        cut = float(L.day_num(["2025-11-01"])[0])
        early = (c.pan.block_mid[T[:, 0].astype(int)] < cut) & (c.pan.block_mid[T[:, 1].astype(int)] < cut)
        late = (c.pan.block_mid[T[:, 0].astype(int)] >= cut) & (c.pan.block_mid[T[:, 1].astype(int)] >= cut)
        o["era_early_calendar"] = Q.ou_fit(T[early, 8], T[early, 5], T[early, 7], 28.0)
        o["era_late_calendar"] = Q.ou_fit(T[late, 8], T[late, 5], T[late, 7], 28.0)
        if sy and regime == "I":
            o["synthetic_accuracy"] = {k: sy["planted"][k]["frac_best"][k] for k in clocks}
            o["synthetic_confusion"] = {k: sy["planted"][k]["frac_best"] for k in clocks}
        res[regime] = o
        print(model, regime, json.dumps({k: (v["tau"], v["sse"]) if isinstance(v, dict) and "tau" in v else v
                                         for k, v in o.items() if k in clocks or k == "best"}, default=float), flush=True)
    return res


def run_r4(model):
    res = {}
    sy = syn("r4", model)
    for regime in ("I", "III"):
        c = Q.load(model, regime)
        arm = Q.H82Arm(model, regime)
        jf, se, T, G = S.r4_once(c, arm, c.X, c.X)
        pl.DataFrame(G, schema=["P", "d", "Q", "lag", "gamma", "n_agents"], orient="row") \
            .write_parquet(Q.R2 / f"r4_gammas_{model}_{regime}.parquet")
        o = {"joint": jf["joint"], "sep81": jf["sep81"], "sep82": jf["sep82"], "dtau": jf["dtau"], "dtau_se_jk": se,
             "n_h82_rows": int(len(G)), "n_boundaries": int(len(np.unique(G[:, 0])))}
        # asymmetric variant (descriptive): past centroids (Q before P) vs future
        past = G[:, 3] > 0
        o["past_fit"] = Q.ou_fit(np.abs(G[past, 3]), G[past, 4], Q.h82_weights(G[past]), 28.0)
        o["future_fit"] = Q.ou_fit(np.abs(G[~past, 3]), G[~past, 4], Q.h82_weights(G[~past]), 28.0)
        # check the reimplementation against H82's stored gamma_prev (data comparison only)
        h = Q.ROOT / "data/processed/H82-remanence-endogenous-field/replication/boundary_rows.parquet"
        if h.exists():
            br = pl.read_parquet(h).filter((pl.col("model") == model) & (pl.col("config") == "primary") & (pl.col("term") == "e")
                                           & (pl.col("regime") == regime))
            prev = {b["P"]: b["prev"] for b in arm.bd}
            mine = {(int(P), int(d)): g for P, d, Qg, lag, g, n in G if prev.get(int(P)) == int(Qg)}
            pairs = [(mine[(r["P"], r["d"])], r["gamma_prev"]) for r in br.iter_rows(named=True) if (r["P"], r["d"]) in mine]
            if pairs:
                p = np.array(pairs)
                o["check_vs_H82_gamma_prev"] = {"n": len(p), "max_abs_diff": float(np.abs(p[:, 0] - p[:, 1]).max())}
        if sy and regime == "I":
            o["synthetic"] = sy
            o["dtau_inside_90"] = bool(sy["dtau_q05"] <= jf["dtau"] <= sy["dtau_q95"])
            o["LR_below_q95"] = bool(jf["joint"]["LR"] <= sy["LR_q95"])
            o["one_mode"] = bool(o["dtau_inside_90"] and o["LR_below_q95"] and 14 <= jf["joint"]["tau"] <= 56)
        res[regime] = o
        print(model, regime, json.dumps({k: o[k] for k in ("dtau", "dtau_se_jk", "joint")}, default=float),
              {"tau81": jf["sep81"]["tau"], "tau82": jf["sep82"]["tau"]}, o.get("check_vs_H82_gamma_prev"), flush=True)
    return res


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--part", default="all")
    a = ap.parse_args()
    res = json.loads(OUTF.read_text()) if OUTF.exists() else {}
    parts = ["r1", "r2a", "r2b", "r2c", "r4"] if a.part == "all" else a.part.split(",")
    for part in parts:
        res.setdefault(part, {})
        for m in Q.MODELS:
            rng = np.random.default_rng(S.seed(m, part, "real"))
            fn = {"r1": lambda: run_r1(m, rng), "r2a": lambda: run_r2a(m, rng), "r2b": lambda: run_r2b(m, rng),
                  "r2c": lambda: run_r2c(m), "r4": lambda: run_r4(m)}[part]
            res[part][m] = fn()
        OUTF.write_text(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
