"""H19 round 1b period-native tests (2026-10-04; predictions written in the period READMEs before these runs).

g51   #51 N sweep: per shared period unit 51a-51l, H19's equal-time gains (raw / DQ8 trim / H38 scaf; active, talk) and
      H03's round-1b per-unit fast cross-triggering (M3, TALK, `period_units` rule; H03 r1b segments.parquet).
      N51-a: log n_c_pair_fast ~ log(N_active - 1), WLS (weights = TALK events), slope = -alpha with a t 95% CI; the
      same on log(1 + k_village) (unit means of controls_days). N51-b: trimmed activity gain ~ N.
ne42  #39 -> #40 -> #41 (room merge A-B-A at N = 15): H03 round-1b fast n_x (TALK) and H19 g_eq raw / trim.
ne43  #51 07-29 .. 08-27 at a fixed roster of 27: sides A (bookends + nudges), B (nudges only), C (no drive); each
      side one window (H02 population rule); g_raw - g_trim (day-edge contribution) with a day-bootstrap SE.
Output: data/processed/H19-loop-gain-collapse/r1b/native_<test>.json
Usage: H19_DATA=r1b uv run python hypotheses/H19-loop-gain-collapse/analysis/r1b_native.py g51|ne42|ne43
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h19common as C  # noqa: E402
import geq_r1b as G  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

H03 = C.PROC / "H03-self-excited-criticality/r1b"
NB = 300


def window_gains(days, rng, n_surr=50):
    ab, sm = G.load_bins(days, "fixed")
    pres = (ab.group_by("agent").agg(pl.col("pt_date").n_unique().alias("nd"), (pl.col("state") >= 3).sum().alias("nact"),
                                     (pl.col("state") == 4).sum().alias("ntalk"))
            .filter((pl.col("nd") == len(days)) & (pl.col("nact") >= G.MIN_ACTIVE_BINS)).sort("agent"))
    agents = pres["agent"].to_list()
    talk_ok = np.array([n >= G.MIN_ACTIVE_BINS for n in pres["ntalk"].to_list()])
    S, Tk, R, day, minute, sched = G.matrices(ab, sm, days, agents)
    est = G.chunk_estimates(S, Tk, R, day, minute, sched, talk_ok, rng, n_surr=n_surr)
    out = {"days": days, "N": len(agents), "N_talk": int(talk_ok.sum())}
    for spin, rec in est.items():
        for v, r in rec.items():
            se, _ = G.boot_se(r["st"], rng, NB)
            out[f"{spin}|{v}"] = {"g": r["g"], "se": se, "E": r.get("E"), "z": r.get("z"), "kept_share": r.get("kept_share", 1.0)}
        # day bootstrap of the edge contribution g_raw - g_trim (same resampled days for both)
        if "trim" in rec:
            a, b = rec["raw"]["st"], rec["trim"]["st"]
            dd = np.unique(a[:, 4])
            diffs = []
            for _ in range(NB):
                pick = rng.choice(dd, len(dd), replace=True)
                ia = np.concatenate([np.flatnonzero(a[:, 4] == x) for x in pick])
                ib = np.concatenate([np.flatnonzero(b[:, 4] == x) for x in pick])
                diffs.append(G.cw(a[ia])["g"] - G.cw(b[ib])["g"])
            out[f"{spin}|edge"] = {"d": rec["raw"]["g"] - rec["trim"]["g"], "se": float(np.nanstd(diffs))}
    return out


def unit_days():
    pu = pl.read_parquet(C.SHARED / "period_units.parquet").filter((pl.col("goal_no") == 51) & ~pl.col("holdout")).sort("seq")
    cal = set(C.calendar_nonholdout()["pt_date"].to_list())
    return {r["unit_id"]: [d for d in sorted(r["days"]) if d in cal] for r in pu.iter_rows(named=True)}


def wls_slope(y, x, w):
    X = np.column_stack([np.ones_like(x), x])
    W = np.diag(w / w.mean())
    b = np.linalg.solve(X.T @ W @ X, X.T @ W @ y)
    r = y - X @ b
    dof = len(y) - 2
    s2 = (r @ W @ r) / dof
    cov = s2 * np.linalg.inv(X.T @ W @ X)
    se = float(np.sqrt(cov[1, 1]))
    q = stats.t.ppf(0.975, dof)
    return {"slope": float(b[1]), "lo": float(b[1] - q * se), "hi": float(b[1] + q * se), "se": se, "n": len(y)}


def g51():
    rng = np.random.default_rng([20261004, 51])
    units = unit_days()
    out = {"units": {}}
    for u, days in units.items():
        if not days:
            continue
        out["units"][u] = window_gains(days, rng, n_surr=30)
        print(u, out["units"][u]["N"], {k: round(v["g"], 3) for k, v in out["units"][u].items() if isinstance(v, dict) and "g" in v},
              flush=True)
    seg = pl.read_parquet(H03 / "segments.parquet").filter((pl.col("rule") == "pu") & (pl.col("goal_no") == 51))
    m3 = seg.filter((pl.col("model") == "M3_sc") & (pl.col("set") == "TALK"))
    m1 = seg.filter((pl.col("model") == "M1_B2") & (pl.col("set") == "TALK"))
    fast = ["10", "30", "100", "300"]
    m3 = m3.with_columns(pl.sum_horizontal([pl.col(f"cross_{k}") for k in fast]).alias("n_c_pair_fast"),
                         (pl.sum_horizontal([pl.col(f"cross_{k}") for k in fast]) * (pl.col("m_bar") - 1)).alias("n_x_fast"))
    ctrd = pl.read_parquet(C.CTRL / "controls_days.parquet")
    kcol = "k_village"   # per unit: agent messages delivered per village turn (controls_days sums, build_controls rule)
    rows = []
    for r in m3.iter_rows(named=True):
        days = units.get(r["seg"], [])
        cd = ctrd.filter(pl.col("pt_date").is_in(days))
        k = float(cd["deliv_agent"].sum() / max(cd["turns_village"].sum(), 1)) if days else np.nan
        k_llm = float(cd["deliv_agent"].sum() / max(cd["turns_llm"].sum(), 1)) if days else np.nan
        n1 = m1.filter(pl.col("seg") == r["seg"])
        rows.append({"unit": r["seg"], "N_active": r["N_active"], "n_events": r["n_events"], "n_c_pair_fast": r["n_c_pair_fast"],
                     "n_x_fast": r["n_x_fast"], "k_village": k, "k_llm": k_llm, "n_talk": float(n1["n"][0]) if n1.height else np.nan,
                     "g_trim_active": out["units"].get(r["seg"], {}).get("active|trim", {}).get("g"),
                     "g_raw_active": out["units"].get(r["seg"], {}).get("active|raw", {}).get("g")})
    df = pl.DataFrame(rows).sort("N_active")
    out["table"] = df.to_dicts()
    ok = df.filter(pl.col("n_c_pair_fast") > 1e-6)
    y = np.log(ok["n_c_pair_fast"].to_numpy())
    w = ok["n_events"].to_numpy().astype(float)
    out["N51a_logN"] = wls_slope(y, np.log(ok["N_active"].to_numpy() - 1), w)
    if kcol:
        kk = ok.filter(pl.col("k_village").is_finite())
        out["N51a_logk"] = wls_slope(np.log(kk["n_c_pair_fast"].to_numpy()), np.log1p(kk["k_village"].to_numpy()),
                                     kk["n_events"].to_numpy().astype(float))
    out["n_zero_pair_units"] = int(df.height - ok.height)
    # the card's P4 estimator (explore.powerlaw_fit: y = A x^-alpha, profile REML over alpha, all units incl. zeros),
    # with explore.p4_exponent's SE convention (SE of n_x floored at 0.02, divided by N_active - 1)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import explore as EX
    y = df["n_c_pair_fast"].to_numpy(); xn = df["N_active"].to_numpy() - 1
    s = np.maximum(0.02 / xn, 1e-4)
    out["N51a_powerlaw_N"] = EX.powerlaw_fit(y, s, xn)
    if kcol:
        kk = df.filter(pl.col("k_village").is_finite())
        out["N51a_powerlaw_k"] = EX.powerlaw_fit(kk["n_c_pair_fast"].to_numpy(), np.maximum(0.02 / (kk["N_active"].to_numpy() - 1), 1e-4),
                                                 1 + kk["k_village"].to_numpy())
    out["rho_pair_N"] = [float(v) for v in stats.spearmanr(df["n_c_pair_fast"], df["N_active"])]
    out["rho_ntalk_N"] = [float(v) for v in stats.spearmanr(df["n_talk"], df["N_active"])]
    gt = df.filter(pl.col("g_trim_active").is_not_null() & pl.col("g_trim_active").is_finite())
    gt = gt.filter(pl.Series([np.isfinite(out["units"][u]["active|trim"]["se"] or np.nan) for u in gt["unit"].to_list()]))
    se = np.array([out["units"][u]["active|trim"]["se"] for u in gt["unit"].to_list()])
    out["N51b_gtrim_vs_N"] = wls_slope(gt["g_trim_active"].to_numpy(), gt["N_active"].to_numpy().astype(float),
                                       1 / np.maximum(se, 0.01) ** 2)
    out["N51b_max_gtrim"] = float(gt["g_trim_active"].max())
    # POST HOC (round-1 channel model, not this README's prediction): talk n-hat and g_eq talk vs k_llm within #51
    gtalk = [out["units"].get(u, {}).get("talk|raw", {}).get("g") for u in df["unit"].to_list()]
    df2 = df.with_columns(pl.Series("g_talk", gtalk, dtype=pl.Float64))
    out["posthoc_rho_ntalk_kllm"] = [float(v) for v in stats.spearmanr(df2["n_talk"], df2["k_llm"])]
    out["posthoc_rho_gtalk_kllm"] = [float(v) for v in stats.spearmanr(df2["g_talk"], df2["k_llm"], nan_policy="omit")]
    out["posthoc_rho_kllm_N"] = [float(v) for v in stats.spearmanr(df2["k_llm"], df2["N_active"])]
    return out


def ne42():
    est = pl.read_parquet(C.OUT / "estimates.parquet")
    pt = pl.read_parquet(H03 / "period_table.parquet").filter(pl.col("set") == "TALK")
    out = {}
    for g in (39, 40, 41):
        r = pt.filter(pl.col("goal_no") == g).to_dicts()[0]
        e = {m: est.filter((pl.col("goal_no") == g) & (pl.col("method") == m)).select("value", "se").to_dicts()
             for m in ("H19.geq_active", "H19.geq_active_trim", "H19.geq_active_scaf", "H19.geq_talk", "H19.geq_talk_trim")}
        out[g] = {"n_x_fast": r["n_cross_fast"], "n_x_lo": r.get("n_cross_fast_boot_lo"), "n_x_hi": r.get("n_cross_fast_boot_hi"),
                  "shift_null": r.get("shift_null_fast"), "n_talk": r["n"], "N_active": r["N_active"],
                  **{m: (v[0] if v else None) for m, v in e.items()}}
    nb = np.mean([out[39]["n_x_fast"], out[41]["n_x_fast"]])
    out["N42a_ratio"] = float(out[40]["n_x_fast"] / nb) if nb > 0 else None
    for m in ("H19.geq_active", "H19.geq_active_trim", "H19.geq_talk"):
        vals = [out[g][m]["value"] if out[g][m] else np.nan for g in (39, 40, 41)]
        out[f"{m}|B_minus_A"] = float(vals[1] - np.nanmean([vals[0], vals[2]]))
    return out


def ne43():
    rng = np.random.default_rng([20261004, 43])
    cal = C.calendar_nonholdout().filter(pl.col("goal_no") == 51)["pt_date"].to_list()
    sides = {"A": ("2026-07-29", "2026-08-04"), "B": ("2026-08-05", "2026-08-20"), "C": ("2026-08-21", "2026-08-27")}
    out = {}
    for s, (a, b) in sides.items():
        days = [d for d in cal if a <= d <= b]
        out[s] = window_gains(days, rng, n_surr=50)
        print(s, out[s]["N"], {k: round(v.get("g", v.get("d", np.nan)), 3) for k, v in out[s].items() if isinstance(v, dict)}, flush=True)
    for x, y in (("A", "B"), ("B", "C")):
        for k in ("active|edge", "active|trim", "talk|raw", "talk|trim", "active|raw", "active|scaf"):
            if k in out[x] and k in out[y]:
                vx, vy = out[x][k].get("g", out[x][k].get("d")), out[y][k].get("g", out[y][k].get("d"))
                se = float(np.hypot(out[x][k]["se"], out[y][k]["se"]))
                out[f"{y}-{x}|{k}"] = {"diff": vy - vx, "se": se, "z": (vy - vx) / se if se > 0 else np.nan}
    return out


def main():
    cmd = sys.argv[1]
    res = {"g51": g51, "ne42": ne42, "ne43": ne43}[cmd]()
    od = C.BASE / "r1b"
    od.mkdir(parents=True, exist_ok=True)
    (od / f"native_{cmd}.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps({k: v for k, v in res.items() if k not in ("units", "table")}, indent=1, default=float))


if __name__ == "__main__":
    main()
