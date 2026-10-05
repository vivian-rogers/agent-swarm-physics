"""H16 round 2 on real data (exploratory; non-reserved days only): R1 urn, R2 dilution, R3 trap depth, mixture rival.

Pre-registered in the card ("Round 2"); estimators validated in synthetic_r2.py. Reads data/processed/H16-.../r2/
(scheme/build_r2.py) and writes r2/results_r2.json plus r2/G<NN>/results_r2.json.
Usage: uv run python hypotheses/H16-metastable-traps-kramers/analysis/run_r2.py [--part gates|ts1r|r3|all] [--boot 200]
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r2lib as R  # noqa: E402
import synthetic_r2 as S  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

RES = R.R2 / "results_r2.json"
REG3 = ["G37", "G38", "G39", "G40", "G41", "G42", "G44", "G51"]


def load_res():
    return json.loads(RES.read_text()) if RES.exists() else {}


def save(res):
    R.jdump(res, RES)


def ci_of(boot_rows, key):
    v = np.array([r.get(key, [np.nan])[0] for r in boot_rows], float)
    return R.pct_ci(v)


def interp_pred(pred, period, urn, level):
    """Urn-predicted gate slope at the observed escape level (linear in level between 0.3, 0.5, 0.7)."""
    p = pred["gate"][period][urn]
    lv = np.array([0.3, 0.5, 0.7])
    b = np.array([p["level_0.3"]["beta_pred"], p["level_0.5"]["beta_pred"], p["level_0.7"]["beta_pred"]])
    lo = np.array([p["level_0.3"]["band"][0], p["level_0.5"]["band"][0], p["level_0.7"]["band"][0]])
    hi = np.array([p["level_0.3"]["band"][1], p["level_0.5"]["band"][1], p["level_0.7"]["band"][1]])
    x = float(np.clip(level, 0.3, 0.7))
    return float(np.interp(x, lv, b)), [float(np.interp(x, lv, lo)), float(np.interp(x, lv, hi))]


# ============================================================================ gates: R1 absorption, reset, R2 kicks
def run_gates(B, rng, res):
    pred = json.loads((R.R2 / "urn_prediction.json").read_text())
    out = {}
    for goal in (51, 38):
        t0 = time.time()
        g = R.prep_gates(pl.read_parquet(R.R2 / "gates_r2.parquet").filter(pl.col("goal_no") == goal))
        y = g["y_sus"].to_numpy().astype(np.int8)
        days = np.unique(np.array(g["pt_date"].to_list()), return_inverse=True)[1]
        point = R.flat(R.gate_models(g, y))
        boots = []
        rows = R.HF.rows_per_day(days)
        for b in range(B):
            idx = np.sort(R.HF.block_resample(days, rng, rows))
            try:
                boots.append(R.flat(R.gate_models(g[idx], y[idx])))
            except Exception as e:  # noqa: BLE001
                print("boot fail", e, flush=True)
        o = {"n_gates": g.height, "n_escapes": int(y.sum()), "escape_frac": float(y.mean()), "n_days": int(len(np.unique(days))),
             "n_forced": int(g["forced"].sum()), "n_vol": int(g["vol"].sum()), "n_dir": int(g["dir1"].sum()),
             "n_undir": int(g["undir1"].sum()), "boot_B": len(boots), "stats": {}}
        for k, v in point.items():
            o["stats"][k] = {"est": v[0], "se": v[1], "ci": ci_of(boots, k)}
        # R1-P1 (gate): urn prediction at the observed level vs the observed slope
        o["urn_vs_obs"] = {}
        for u in R.URNS:
            bp, band = interp_pred(pred, f"G{goal}", u, o["escape_frac"])
            bo = o["stats"]["beta_a0"]
            hit = (bo["ci"][1] >= band[0]) and (bo["ci"][0] <= band[1]) and abs(bo["est"] - bp) <= 0.2
            o["urn_vs_obs"][u] = {"beta_pred": bp, "band": band, "beta_obs": bo["est"], "ci_obs": bo["ci"],
                                  "delta": bo["est"] - bp, "urn_predicts": bool(hit)}
        # gate aging within trap kind (M-P3)
        o["by_trap_kind"] = {}
        X0 = R.nuisance(g)
        ag = g["agent"].to_numpy()
        tk = np.array(g["trap_kind"].to_list())
        for kd in ("after_work", "after_talk", "after_fail"):
            m = tk == kd
            if m.sum() < 200 or y[m].sum() < 30:
                o["by_trap_kind"][kd] = {"n": int(m.sum()), "ok": False}
                continue
            f = R.fe_logit(y[m], X0[m], ag[m])
            bs = []
            for b in range(min(B, 100)):
                idx = np.sort(R.HF.block_resample(days[m], rng))
                bs.append(R.fe_logit(y[m][idx], X0[m][idx], ag[m][idx])["beta"][0])
            o["by_trap_kind"][kd] = {"n": int(m.sum()), "esc": int(y[m].sum()), "beta_a": float(f["beta"][0]), "se": float(f["se"][0]), "ci": R.pct_ci(bs)}
        # agent x trap-kind FE (within-kind aging, pooled)
        code = R.cell_codes({"agent": ag, "trap_kind": tk}, cols=("trap_kind",))
        f = R.fe_logit(y, X0, code)
        o["within_kind_fe"] = {"beta_a": float(f["beta"][0]), "se": float(f["se"][0])}
        out[f"G{goal}"] = o
        print(f"[{time.time() - t0:5.0f}s] gates G{goal}", {k: o["stats"][k] for k in ("beta_a0", "abs_f_tok.rho", "abs_f_call.rho", "reset.forced", "kick.diff")}, flush=True)
        res["gates"] = out
        save(res)
    return out


# ============================================================================ TS1r: urn exponent and mixture rival
def run_ts1r(B, rng, res, null_sims=200):
    pred = json.loads((R.R2 / "urn_prediction.json").read_text())
    out = {}
    for per in REG3:
        t0 = time.time()
        H = R.ts1r_deep(per)
        H["day"] = np.unique(H["day"], return_inverse=True)[1]
        y = H["y"]
        if y.sum() < 15:
            out[per] = {"ok": False, "events": int(y.sum())}
            continue
        rows = R.HF.rows_per_day(H["day"])
        o = {"rows": int(len(y)), "events": int(y.sum()), "n_days": int(len(rows))}

        def slope_ci(m, groups, nb):
            b, s = R.slope_cloglog(y[m], H["lnel"][m], groups[m])
            bs = []
            dd = H["day"][m]
            rr = R.HF.rows_per_day(dd)
            for _ in range(nb):
                idx = R.HF.block_resample(dd, rng, rr)
                bs.append(R.slope_cloglog(y[m][idx], H["lnel"][m][idx], groups[m][idx])[0])
            return {"beta": b, "se": s, "ci": R.pct_ci(bs), "events": int(y[m].sum()), "rows": int(m.sum())}
        allm = np.ones(len(y), bool)
        nb = B if per in ("G51", "G38") else min(B, 100)
        o["pooled"] = slope_ci(allm, H["agent"], nb)
        kcode = R.cell_codes(H, cols=("kind_start",))
        o["within_kind_start"] = slope_ci(allm, kcode, nb)
        ccode = R.cell_codes(H)
        o["within_cell"] = slope_ci(allm, ccode, nb)
        o["by_kind"] = {}
        for kd in ("pause", "silent", "consol", "wait"):
            m = H["kind_start"] == kd
            if y[m].sum() < 15:
                o["by_kind"][kd] = {"ok": False, "events": int(y[m].sum()), "rows": int(m.sum())}
                continue
            o["by_kind"][kd] = slope_ci(m, H["agent"], nb)
        o["by_last_kind"] = {}
        for kd in ("work", "talk", "fail"):
            m = H["last_kind"] == kd
            if y[m].sum() < 15:
                o["by_last_kind"][kd] = {"ok": False, "events": int(y[m].sum())}
                continue
            b, s = R.slope_cloglog(y[m], H["lnel"][m], H["agent"][m])
            o["by_last_kind"][kd] = {"beta": b, "se": s, "events": int(y[m].sum())}
        o["no_consol"] = slope_ci(H["kind_start"] != "consol", H["agent"], nb)
        o["mix_share"] = 1 - o["within_cell"]["beta"] / o["pooled"]["beta"] if o["pooled"]["beta"] < 0 else None
        if per in ("G51", "G38"):
            nul = R.mixture_null(rng, H, y, ccode, sims=null_sims)
            day_cells = R.cell_codes(H, cols=("kind_start", "last_kind", "day"))
            nul2 = R.mixture_null(rng, H, y, day_cells, sims=max(null_sims // 2, 50))
            o["mixture_null"] = {"cells": "agent x kind_start x last_kind", "mean": float(nul.mean()), "q": [float(np.percentile(nul, 2.5)), float(np.percentile(nul, 97.5))],
                                 "p_obs": float(np.mean(nul <= o["pooled"]["beta"])), "sims": int(len(nul))}
            o["mixture_null_day"] = {"cells": "agent x kind_start x last_kind x day", "mean": float(nul2.mean()),
                                     "q": [float(np.percentile(nul2, 2.5)), float(np.percentile(nul2, 97.5))],
                                     "p_obs": float(np.mean(nul2 <= o["pooled"]["beta"])), "sims": int(len(nul2))}
            u = pred["ts1r"][per]
            o["urn_vs_obs"] = {k: {"beta_pred": u[k]["beta_pred"], "band": u[k]["band"], "delta": o["pooled"]["beta"] - u[k]["beta_pred"],
                                   "urn_predicts": bool((o["pooled"]["ci"][1] >= u[k]["band"][0]) and (o["pooled"]["ci"][0] <= u[k]["band"][1])
                                                        and abs(o["pooled"]["beta"] - u[k]["beta_pred"]) <= 0.2)} for k in R.URNS}
        out[per] = o
        print(f"[{time.time() - t0:5.0f}s] ts1r {per} pooled {o['pooled']['beta']:.3f} {o['pooled']['ci']} within_cell {o['within_cell']['beta']:.3f} "
              f"pause {o['by_kind'].get('pause', {}).get('beta')} no_consol {o['no_consol']['beta']:.3f}", flush=True)
        res["ts1r"] = out
        save(res)
    return out


# ============================================================================ R3: trap depth as a trait
def run_r3(rng, res):
    d = S.depth_cells()
    ros = pl.read_parquet(R.SH / "roster.parquet").select("agent", "model_string", "lab")
    d = d.join(ros, on="agent", how="left")
    o = {"agent": S.r3_stats(d, rng, B=500, n_perm=1000, label="agent")}
    o["lab"] = {"share": S.var_share(d, "lab")}
    perm = []
    for _ in range(1000):
        lab = d["lab"].to_numpy().copy()
        for per in d["period"].unique().to_list():
            m = (d["period"] == per).to_numpy()
            lab[m] = rng.permutation(lab[m])
        perm.append(S.var_share(d.with_columns(pl.Series("lab", lab)), "lab"))
    o["lab"]["perm_p"] = float(np.nanmean(np.array(perm) >= o["lab"]["share"]))
    # partial pooling: shrunk agent depth (period-centred), tau2 from the agent share
    x = d.with_columns(Dc=pl.col("D") - pl.col("D").mean().over("period"))
    tot = float(x["Dc"].var()) - float(x["v"].mean())
    tau2 = max(o["agent"]["share"], 0) * tot if np.isfinite(o["agent"]["share"]) else 0.0
    resid = max(tot - tau2, 1e-6)
    m = x.group_by("agent", "model_string", "lab").agg(pl.col("Dc").mean().alias("mean"), pl.len().alias("n_periods"),
                                                        (pl.col("v").mean()).alias("v"), pl.col("period").alias("periods"))
    m = m.with_columns(se2=(resid + pl.col("v")) / pl.col("n_periods"))
    m = m.with_columns(w=tau2 / (tau2 + pl.col("se2")))
    m = m.with_columns(shrunk=pl.col("w") * pl.col("mean"), post_sd=(pl.col("w") * pl.col("se2")).sqrt())
    o["pooled_depth"] = [{"agent": int(r["agent"]), "model": r["model_string"], "lab": r["lab"], "n_periods": int(r["n_periods"]),
                          "raw": float(r["mean"]), "shrunk": float(r["shrunk"]), "lo": float(r["shrunk"] - 1.96 * r["post_sd"]),
                          "hi": float(r["shrunk"] + 1.96 * r["post_sd"])} for r in m.sort("shrunk").iter_rows(named=True)]
    o["tau2_agent"] = tau2
    o["resid_var"] = resid
    o["cells"] = d.select("agent", "period", "ev", "bins", "D").to_dicts()
    # per-agent aging slopes in G51 (heterogeneity)
    H = R.ts1r_deep("G51")
    sl = []
    for a in np.unique(H["agent"]):
        mm = H["agent"] == a
        if H["y"][mm].sum() < 15:
            continue
        b, s = R.slope_cloglog(H["y"][mm], H["lnel"][mm], np.zeros(mm.sum(), int))
        if np.isfinite(b) and np.isfinite(s) and s > 0:
            sl.append((int(a), b, s, int(H["y"][mm].sum())))
    b = np.array([x[1] for x in sl]); s = np.array([x[2] for x in sl])
    w = 1 / s ** 2
    bbar = float(np.sum(w * b) / np.sum(w))
    Q = float(np.sum(w * (b - bbar) ** 2))
    from scipy import stats as st
    o["G51_agent_slopes"] = {"n_agents": len(sl), "fixed_mean": bbar, "Q": Q, "df": len(sl) - 1, "p": float(st.chi2.sf(Q, len(sl) - 1)),
                             "I2": float(max(0, (Q - (len(sl) - 1)) / Q)) if Q > 0 else 0.0,
                             "slopes": [{"agent": a, "beta": float(bb), "se": float(ss), "events": e} for a, bb, ss, e in sl]}
    res["r3"] = o
    save(res)
    print("R3", {k: o[k] for k in ("agent", "lab")}, o["G51_agent_slopes"]["p"], flush=True)
    return o


def main():
    part = sys.argv[sys.argv.index("--part") + 1] if "--part" in sys.argv else "all"
    B = int(sys.argv[sys.argv.index("--boot") + 1]) if "--boot" in sys.argv else 200
    rng = np.random.default_rng(R.SEED + 10)
    res = load_res()
    if part in ("gates", "all"):
        run_gates(B, rng, res)
    if part in ("ts1r", "all"):
        run_ts1r(B, rng, res)
    if part in ("r3", "all"):
        run_r3(rng, res)


if __name__ == "__main__":
    main()
