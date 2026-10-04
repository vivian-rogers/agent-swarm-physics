"""H09 round 1b (2026-10-04): memory equation of state on the context ledger (E8 re-run), the #51 roster sweep (N2)
and the first-order homeostat test (N3, HH269). Non-holdout only; regime III. Predictions: card, "Round 1b" (written
2026-10-04 08:40 UTC).

Changes from round 2 (explore_e7_e8.py, E8):
  - inflow P_read = new chat items that entered the agent's model calls in (t_prev, t] (`context_ledger_turns.k_new`,
    DQ1 visibility), replacing the coincidence count of room messages from `exposure` (which tracked clock time);
  - each snapshot gets the type of the reset it closed, from the agent's first ledger call after it: forced (the
    41-turn cap, `reset_forced`), voluntary (`reset_consol` only), or unknown;
  - tokens: round 2 already summed actions.tok_in + cache fields (Anthropic) / tok_in - cache_read (Gemini), not the
    uncached-only events_core.tokens_in; checked here against H45's per-call prompt sizes (P).
Snapshot table: data/processed/H09-swarm-thermodynamics/consolidation_inflow.parquet (round 2, all days, holdout
flag). Outputs: r1b/r1b_memory.json, r1b/snapshots_ledger.parquet (numbers only).
Usage: uv run python hypotheses/H09-swarm-thermodynamics/analysis/r1b_memory.py
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
SH = ROOT / "data/processed/shared"
IN_D = ROOT / "data/processed/H09-swarm-thermodynamics"
OUTD = IN_D / "r1b"
OUTD.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402

RNG = np.random.default_rng(20261004)


def keep_days() -> list:
    cal = pl.read_parquet(SH / "calendar.parquet").filter(~pl.col("holdout"))
    hm = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    return cal.filter(~pl.Series(hm))["pt_date"].to_list()


def snapshots(days: list) -> pl.DataFrame:
    ci = (pl.read_parquet(IN_D / "consolidation_inflow.parquet")
          .filter(~pl.col("holdout") & pl.col("pt_date").is_in(days) & (pl.col("regime") == "III")
                  & pl.col("consolidate_event_120s") & (pl.col("n_chars") > 0))
          .sort("agent", "t"))
    calls = (pl.scan_parquet(SH / "context_ledger_turns.parquet")
             .filter(pl.col("pt_date").is_in(days) & ~pl.col("holdout") & (pl.col("regime") == "III"))
             .select("agent", "t_call", "k_new", "reset_forced", "reset_consol", "pt_date").collect().sort("agent", "t_call"))
    parts = []
    for (a,), g in ci.group_by("agent"):
        c = calls.filter(pl.col("agent") == a)
        tc = c["t_call"].dt.epoch("us").to_numpy()
        cum = np.r_[0, np.cumsum(c["k_new"].fill_null(0).to_numpy().astype(float))]
        t1 = g["t"].dt.epoch("us").to_numpy()
        tp = g["t_prev"].dt.epoch("us").fill_null(0).to_numpy()
        i0, i1 = np.searchsorted(tc, tp, side="right"), np.searchsorted(tc, t1, side="right")
        p_read = cum[i1] - cum[i0]
        n_calls = i1 - i0
        nxt = np.searchsorted(tc, t1, side="right")
        has = nxt < len(tc)
        rf = c["reset_forced"].to_numpy(); rc = c["reset_consol"].to_numpy()
        typ = np.where(~has, "unknown", np.where(rf[np.clip(nxt, 0, len(tc) - 1)], "forced",
                       np.where(rc[np.clip(nxt, 0, len(tc) - 1)], "voluntary", "unknown")))
        parts.append(g.with_columns(pl.Series("p_read", p_read), pl.Series("n_calls_ledger", n_calls.astype(np.int32)),
                                    pl.Series("reset_type", typ)))
    s = pl.concat(parts).sort("agent", "t")
    return s


def demean(df, cols, by):
    return df.with_columns(*[(pl.col(c) - pl.col(c).mean().over(by)).alias(c + "_w") for c in cols])


def slope(d, y, x):
    d = d.drop_nulls([y, x]).filter(pl.col(x).is_finite() & pl.col(y).is_finite())
    xv, yv = d[x].to_numpy(), d[y].to_numpy()
    return float(np.sum(xv * yv) / np.sum(xv * xv)), int(len(xv))


def e8(s: pl.DataFrame) -> dict:
    c3 = s.filter(pl.col("same_day_prev") & (pl.col("dt_s") > 0)).with_columns(
        pl.col("n_chars").log().alias("lnV"), (pl.col("p_read") + 1).log().alias("lnPr"), (pl.col("n_exposed") + 1).log().alias("lnPm"),
        (1 - pl.col("jaccard_prev")).alias("turn"), (pl.col("n_chars") - pl.col("d_chars")).alias("V_prev"),
        (pl.col("agent").cast(pl.Utf8) + "_" + pl.col("goal_no").cast(pl.Utf8)).alias("ag"),
        pl.col("dt_s").cast(pl.Float64))
    d = demean(c3, ["lnV", "lnPr", "lnPm", "turn", "V_prev", "d_chars", "p_read", "dt_s", "n_exposed"], "ag")
    b_r, n_r = slope(d, "lnV_w", "lnPr_w")
    b_m, n_m = slope(d, "lnV_w", "lnPm_w")
    r_turn = stats.spearmanr(d["p_read_w"].to_numpy(), d["turn_w"].to_numpy(), nan_policy="omit")
    r_dt = stats.spearmanr(d["p_read_w"].to_numpy(), d["dt_s_w"].to_numpy(), nan_policy="omit")
    r_dt_old = stats.spearmanr(d["n_exposed_w"].to_numpy(), d["dt_s_w"].to_numpy(), nan_policy="omit")
    dd = d.drop_nulls(["d_chars_w", "p_read_w", "V_prev_w"])
    A = np.c_[dd["p_read_w"].to_numpy(), dd["V_prev_w"].to_numpy()]
    coef = np.linalg.lstsq(A, dd["d_chars_w"].to_numpy(), rcond=None)[0]
    return {"n_snapshots": c3.height, "agents": int(c3["agent"].n_unique()),
            "median_p_read": float(c3["p_read"].median()), "median_n_exposed": float(c3["n_exposed"].median()),
            "E8a_elasticity_lnV_lnPread": b_r, "n": n_r, "E8a_elasticity_lnV_lnPmsg_round2_measure": b_m,
            "spearman_Pread_vs_interval_within": float(r_dt.statistic), "spearman_Pmsg_vs_interval_within_round2": float(r_dt_old.statistic),
            "E8c_spearman_Pread_turnover": float(r_turn.statistic),
            "E8c_dV_on_Pread_beta_chars_per_item": float(coef[0]), "E8c_dV_on_Vprev_minus_gamma": float(coef[1]),
            "share_reset_type": dict(c3.group_by("reset_type").len().iter_rows())}


def n2_roster_sweep(s: pl.DataFrame, days: list) -> dict:
    s51 = s.filter(pl.col("goal_no") == 51).with_columns(
        pl.col("pt_date").str.to_date().dt.truncate("1w").alias("wk"))
    calls = (pl.scan_parquet(SH / "context_ledger_turns.parquet")
             .filter((pl.col("goal_no") == 51) & ~pl.col("holdout") & pl.col("pt_date").is_in(days))
             .select("agent", "pt_date", "k_new").collect()
             .with_columns(pl.col("pt_date").str.to_date().dt.truncate("1w").alias("wk")))
    inflow = calls.group_by("agent", "wk").agg(pl.col("k_new").mean().alias("reads_per_call"), pl.len().alias("calls"))
    nwk = calls.group_by("wk").agg(pl.col("agent").n_unique().alias("N"))
    v = s51.group_by("agent", "wk").agg(pl.col("n_chars").median().alias("V"), pl.len().alias("snaps"))
    m = (v.join(inflow, on=["agent", "wk"]).join(nwk, on="wk").filter((pl.col("snaps") >= 5) & (pl.col("reads_per_call") > 0))
         .with_columns(pl.col("V").log().alias("lnV"), pl.col("reads_per_call").log().alias("lnR"), pl.col("N").cast(pl.Float64).log().alias("lnN")))
    d = demean(m, ["lnV", "lnR", "lnN"], "agent")
    b_r, n = slope(d, "lnV_w", "lnR_w")
    b_n, _ = slope(d, "lnV_w", "lnN_w")
    # agent-cluster bootstrap
    ags = d["agent"].unique().to_list()
    bsr, bsn = [], []
    for _ in range(2000):
        pick = RNG.choice(ags, len(ags))
        dd = pl.concat([d.filter(pl.col("agent") == a) for a in pick])
        bsr.append(slope(dd, "lnV_w", "lnR_w")[0]); bsn.append(slope(dd, "lnV_w", "lnN_w")[0])
    # inflow vs N (does inflow per call rise with N?)
    b_rn, _ = slope(d, "lnR_w", "lnN_w")
    return {"agent_weeks": n, "agents": len(ags), "weeks": int(m["wk"].n_unique()), "N_range": [int(m["N"].min()), int(m["N"].max())],
            "elasticity_V_on_reads_per_call": b_r, "ci95": [float(np.percentile(bsr, 2.5)), float(np.percentile(bsr, 97.5))],
            "elasticity_V_on_N": b_n, "ci95_N": [float(np.percentile(bsn, 2.5)), float(np.percentile(bsn, 97.5))],
            "elasticity_reads_per_call_on_N": b_rn,
            "pass_a": bool(abs(b_r) < 0.1), "pass_b": bool(abs(b_n) < 0.2)}


def n3_homeostat(s: pl.DataFrame) -> dict:
    res, per = {}, []
    pooled = {"forced": [], "voluntary": []}
    for (a,), g in s.group_by("agent"):
        g = g.sort("t")
        if g.height < 100:
            continue
        x = np.log(g["n_chars"].to_numpy().astype(float))
        same = g["same_day_prev"].to_numpy()
        typ = g["reset_type"].to_numpy()
        n = len(x); cut = int(0.7 * n)
        mu = x[:cut].mean()
        idx = np.arange(1, n)
        idx = idx[same[idx]]                      # steps within a day
        tr, te = idx[idx < cut], idx[idx >= cut]
        if len(tr) < 30 or len(te) < 10:
            continue
        u, v = x[tr - 1] - mu, x[tr] - mu
        phi = float(np.sum(u * v) / np.sum(u * u))
        f_ar = mu + phi * (x[te - 1] - mu)
        f_rw = x[te - 1]
        mse_ar, mse_rw = float(np.mean((x[te] - f_ar) ** 2)), float(np.mean((x[te] - f_rw) ** 2))
        per.append({"agent": int(a), "n": n, "phi": phi, "mse_ar": mse_ar, "mse_rw": mse_rw, "ar_wins": mse_ar < mse_rw})
        allidx = idx
        for k in ("forced", "voluntary"):
            sel = allidx[typ[allidx - 1] == k]       # the step that starts from a snapshot closing a reset of type k
            mu_all = x.mean()
            pooled[k].append(np.c_[x[sel - 1] - mu_all, x[sel] - mu_all])
    phis = np.array([p["phi"] for p in per])
    res["agents"] = len(per)
    res["phi_median"] = float(np.median(phis)) if len(phis) else None
    res["phi_iqr"] = [float(np.percentile(phis, 25)), float(np.percentile(phis, 75))] if len(phis) else None
    res["frac_phi_in_0_0.5"] = float(np.mean((phis >= 0) & (phis <= 0.5))) if len(phis) else None
    res["frac_ar_beats_rw"] = float(np.mean([p["ar_wins"] for p in per])) if per else None
    res["median_mse_ratio_ar_over_rw"] = float(np.median([p["mse_ar"] / p["mse_rw"] for p in per])) if per else None
    for k in ("forced", "voluntary"):
        M = np.vstack([m for m in pooled[k] if len(m)]) if any(len(m) for m in pooled[k]) else np.zeros((0, 2))
        if len(M) > 30:
            phi_k = float(np.sum(M[:, 0] * M[:, 1]) / np.sum(M[:, 0] ** 2))
            bs = []
            for _ in range(2000):
                q = M[RNG.integers(0, len(M), len(M))]
                bs.append(np.sum(q[:, 0] * q[:, 1]) / np.sum(q[:, 0] ** 2))
            res[f"phi_after_{k}"] = {"phi": phi_k, "ci95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))], "n": int(len(M))}
    if "phi_after_forced" in res and "phi_after_voluntary" in res:
        f, v = res["phi_after_forced"]["phi"], res["phi_after_voluntary"]["phi"]
        res["pass_c_no_overshoot"] = bool(f >= 0 and f >= v - 0.1)
    res["pass_a"] = bool(res["frac_phi_in_0_0.5"] is not None and res["frac_phi_in_0_0.5"] >= 0.8)
    res["pass_b"] = bool(res["frac_ar_beats_rw"] is not None and res["frac_ar_beats_rw"] >= 0.8)
    res["per_agent"] = per
    return res


def token_check(days: list) -> dict:
    """Round-2 token accounting vs H45's per-call prompt size P (Anthropic / Google cu calls)."""
    p = ROOT / "data/processed/H45-context-homeostasis/calls.parquet"
    if not p.exists():
        return {"note": "H45 calls.parquet missing"}
    h = (pl.scan_parquet(p).filter(pl.col("pt_date").is_in(days) & (pl.col("regime") == "III") & pl.col("P").is_not_null())
         .select("agent", "t_call", "P", "lab").collect())
    ci = pl.read_parquet(IN_D / "consolidation_inflow.parquet").filter(pl.col("pt_date").is_in(days) & pl.col("tok_context_last").is_not_null()
                                                                       & (pl.col("regime") == "III"))
    # nearest earlier call to the snapshot (backward as-of): its P vs round-2's tok_context_last
    j = ci.sort("t").join_asof(h.sort("t_call"), left_on="t", right_on="t_call", by="agent", strategy="backward")
    j = j.drop_nulls(["P"])
    r = stats.spearmanr(j["tok_context_last"].to_numpy(), j["P"].to_numpy())
    return {"n": j.height, "spearman_round2_context_vs_H45_P": float(r.statistic),
            "median_ratio": float((j["tok_context_last"] / j["P"]).median())}


def main():
    days = keep_days()
    s = snapshots(days)
    s.select("agent", "t", "pt_date", "goal_no", "n_chars", "p_read", "n_calls_ledger", "reset_type", "same_day_prev").write_parquet(
        OUTD / "snapshots_ledger.parquet", compression="zstd")
    R = {"E8_ledger": e8(s), "N2_roster_sweep_51": n2_roster_sweep(s, days), "N3_homeostat": n3_homeostat(s),
         "token_check": token_check(days)}
    R["E8_by_goal"] = {}
    for (g,), d in s.group_by("goal_no"):
        if d.height >= 300:
            R["E8_by_goal"][int(g)] = {k: v for k, v in e8(d).items() if k in ("n_snapshots", "agents", "E8a_elasticity_lnV_lnPread",
                                                                             "E8c_dV_on_Vprev_minus_gamma")}
    (OUTD / "r1b_memory.json").write_text(json.dumps(R, indent=1, default=float))
    print(json.dumps({k: (v if k != "N3_homeostat" else {kk: vv for kk, vv in v.items() if kk != "per_agent"}) for k, v in R.items()},
                     indent=1, default=float)[:7000])


if __name__ == "__main__":
    main()
