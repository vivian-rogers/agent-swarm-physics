"""H09 round 1b (2026-10-04): the regime-III timer gate on the context ledger (G1) and the NE43 drive-withdrawal test
(N1). Non-holdout only. Predictions: card, "Round 1b" (written 2026-10-04 08:40 UTC).

Unit: a regime-III model call that follows a timer pause (`call_windows.after_pause`; gap_kind pause or pause_early).
Outcome: act = the call is anything but another pause or wait. Covariates (`context_ledger_turns`, same turn_id): chat
items that newly entered this call: n_ment (@-mentions of this agent, clean mentions), n_nudge_me, n_human, n_agent,
k_new. Mantel-Haenszel odds ratios stratified by agent (and by agent x goal period as a check); agent-cluster
bootstrap CIs.

Outputs: data/processed/H09-swarm-thermodynamics/r1b/r1b_gate.json and gate_calls.parquet (one row per post-pause call;
ids and counts only).
Usage: uv run python hypotheses/H09-swarm-thermodynamics/analysis/r1b_gate.py
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

ROOT = Path(__file__).resolve().parents[3]
SH = ROOT / "data/processed/shared"
OUTD = ROOT / "data/processed/H09-swarm-thermodynamics/r1b"
OUTD.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402

RNG = np.random.default_rng(20261004)
NB = 1000


def load() -> pl.DataFrame:
    cal = pl.read_parquet(SH / "calendar.parquet").filter(~pl.col("holdout"))
    hm = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    days = cal.filter(~pl.Series(hm))["pt_date"].to_list()
    cw = (pl.scan_parquet(SH / "call_windows.parquet")
          .filter((pl.col("regime") == "III") & ~pl.col("holdout") & pl.col("pt_date").is_in(days) & pl.col("after_pause"))
          .select("turn_id", "agent", "pt_date", "goal_no", "kind", "gap_kind", "wake_early", "pause_s", "t_call").collect())
    lt = (pl.scan_parquet(SH / "context_ledger_turns.parquet")
          .select("turn_id", "n_ment", "n_nudge_me", "n_nudge", "n_human", "n_agent", "k_new", "ctx_pos").collect())
    g = cw.join(lt, on="turn_id", how="left").with_columns(
        (~pl.col("kind").cast(pl.Utf8).is_in(["pause", "wait"])).alias("act"),
        (pl.col("n_ment") > 0).alias("ment"), (pl.col("n_nudge_me") > 0).alias("nudge_me"),
        (pl.col("n_human") > 0).alias("human"), (pl.col("n_agent") > 0).alias("agent_msg"),
        (pl.col("k_new").fill_null(0) == 0).alias("no_new"))
    # unaddressed agent messages only (no mention, no nudge, no human)
    g = g.with_columns((pl.col("agent_msg") & ~pl.col("ment") & ~pl.col("nudge_me") & ~pl.col("human")).alias("agent_only"))
    return g


def mh_or(y: np.ndarray, x: np.ndarray, s: np.ndarray) -> float:
    """Mantel-Haenszel odds ratio of outcome y for exposure x over strata s."""
    num = den = 0.0
    for k in np.unique(s):
        m = s == k
        a = np.sum(y[m] & x[m]); b = np.sum(~y[m] & x[m]); c = np.sum(y[m] & ~x[m]); d = np.sum(~y[m] & ~x[m])
        n = a + b + c + d
        if n:
            num += a * d / n; den += b * c / n
    return float(num / den) if den > 0 else float("nan")


def or_with_ci(df: pl.DataFrame, expo: str, ref: str | None = None, strata=("agent",)) -> dict:
    """OR of act for expo vs ref (ref = complement, or a named reference group such as no_new)."""
    d = df if ref is None else df.filter(pl.col(expo) | pl.col(ref))
    y = d["act"].to_numpy(); x = d[expo].to_numpy()
    s = d.select(pl.concat_str([pl.col(c).cast(pl.Utf8) for c in strata], separator="_")).to_series().to_numpy()
    est = mh_or(y, x, s)
    ag = d["agent"].to_numpy(); ua = np.unique(ag)
    idx = {a: np.flatnonzero(ag == a) for a in ua}
    bs = []
    for _ in range(NB):
        pick = np.concatenate([idx[a] for a in RNG.choice(ua, len(ua))])
        bs.append(mh_or(y[pick], x[pick], s[pick]))
    bs = np.array(bs); bs = bs[np.isfinite(bs)]
    return {"or_mh": est, "ci95_agent_boot": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))] if len(bs) else None,
            "p_act_expo": float(y[x].mean()) if x.any() else None, "p_act_ref": float(y[~x].mean()) if (~x).any() else None,
            "n_expo": int(x.sum()), "n_ref": int((~x).sum())}


def gate(df: pl.DataFrame) -> dict:
    out = {"n_calls": df.height, "p_act": float(df["act"].mean()), "frac_wake_early": float(df["wake_early"].fill_null(False).mean()),
           "frac_no_new": float(df["no_new"].mean())}
    out["ment_vs_rest"] = or_with_ci(df, "ment")
    out["ment_vs_no_new"] = or_with_ci(df, "ment", "no_new")
    out["agent_only_vs_no_new"] = or_with_ci(df, "agent_only", "no_new")
    out["nudge_vs_rest"] = or_with_ci(df, "nudge_me")
    out["nudge_vs_no_new"] = or_with_ci(df, "nudge_me", "no_new")
    out["human_vs_no_new"] = or_with_ci(df, "human", "no_new")
    out["ment_vs_rest_agent_x_goal"] = or_with_ci(df, "ment", strata=("agent", "goal_no"))
    return out


def ne43(df: pl.DataFrame) -> dict:
    w = {"pre_0727_0804": ("2026-07-27", "2026-08-04"), "mid_0806_0820": ("2026-08-06", "2026-08-20"),
         "post_0821_0904": ("2026-08-21", "2026-09-04")}
    out = {}
    for k, (a, b) in w.items():
        d = df.filter(pl.col("pt_date").is_between(pl.lit(a), pl.lit(b)))
        nn = d.filter(pl.col("no_new"))
        out[k] = {"calls": d.height, "p_act": float(d["act"].mean()), "p_act_no_new": float(nn["act"].mean()),
                  "n_no_new": nn.height, "share_nudge": float(d["nudge_me"].mean()),
                  "p_act_nudge": float(d.filter(pl.col("nudge_me"))["act"].mean()) if d["nudge_me"].any() else None,
                  "share_ment": float(d["ment"].mean()), "agents": int(d["agent"].n_unique()),
                  "median_pause_s": float(d["pause_s"].median()) if d["pause_s"].is_not_null().any() else None}
    # agent-matched log ratios of P(act | no new item) across each step (agents present on both sides)
    def step(a, b):
        da = df.filter(pl.col("pt_date").is_between(pl.lit(w[a][0]), pl.lit(w[a][1])) & pl.col("no_new"))
        db = df.filter(pl.col("pt_date").is_between(pl.lit(w[b][0]), pl.lit(w[b][1])) & pl.col("no_new"))
        pa = da.group_by("agent").agg(pl.col("act").mean().alias("pa"), pl.len().alias("na"))
        pb = db.group_by("agent").agg(pl.col("act").mean().alias("pb"), pl.len().alias("nb"))
        m = pa.join(pb, on="agent").filter((pl.col("na") >= 10) & (pl.col("nb") >= 10))
        # pooled over matched agents (weights = min count)
        wts = np.minimum(m["na"].to_numpy(), m["nb"].to_numpy()).astype(float)
        lr_pool = float(np.log(np.average(m["pb"].to_numpy(), weights=wts) / np.average(m["pa"].to_numpy(), weights=wts))) if m.height else None
        bs = []
        for _ in range(NB):
            k = RNG.integers(0, m.height, m.height)
            bs.append(np.log(np.average(m["pb"].to_numpy()[k], weights=wts[k]) / np.average(m["pa"].to_numpy()[k], weights=wts[k])))
        return {"agents_matched": m.height, "log_ratio_p_act_no_new": lr_pool,
                "ci95_agent_boot": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))] if bs else None,
                "pass_abs_lt_0.18": bool(lr_pool is not None and abs(lr_pool) < 0.18)}
    out["step_a_bookends"] = step("pre_0727_0804", "mid_0806_0820")
    out["step_b_nudger"] = step("mid_0806_0820", "post_0821_0904")
    mid, post = out["mid_0806_0820"], out["post_0821_0904"]
    bound = mid["share_nudge"] * ((mid["p_act_nudge"] or 0) - mid["p_act_no_new"]) + 0.02
    drop = mid["p_act"] - post["p_act"]
    out["step_b_accounting"] = {"drop_in_p_act": float(drop), "bound": float(bound), "pass": bool(drop <= bound)}
    return out


def main():
    df = load()
    df.select("turn_id", "agent", "pt_date", "goal_no", "act", "ment", "nudge_me", "human", "agent_msg", "no_new", "k_new",
              "wake_early").write_parquet(OUTD / "gate_calls.parquet", compression="zstd")
    R = {"G1_all_regime_III": gate(df)}
    R["G1_by_goal"] = {}
    for (g,), d in df.group_by("goal_no"):
        if d.height >= 300 and d["ment"].sum() >= 20:
            r = {"n": d.height, "p_act": float(d["act"].mean())}
            y, x = d["act"].to_numpy(), d["ment"].to_numpy()
            r["ment_or_mh_agent"] = mh_or(y, x, d["agent"].cast(pl.Utf8).to_numpy())
            r["n_ment"] = int(x.sum())
            nn = d.filter(pl.col("no_new") | pl.col("ment"))
            r["ment_vs_no_new_or_mh_agent"] = mh_or(nn["act"].to_numpy(), nn["ment"].to_numpy(), nn["agent"].cast(pl.Utf8).to_numpy())
            R["G1_by_goal"][int(g)] = r
    R["N1_NE43"] = ne43(df.filter(pl.col("goal_no") == 51))
    g = R["G1_all_regime_III"]
    R["G1_verdict"] = {"a_ment_or_ge_1.5": bool(g["ment_vs_rest"]["or_mh"] >= 1.5),
                       "b_agent_only_in_0.8_1.25": bool(0.8 <= g["agent_only_vs_no_new"]["or_mh"] <= 1.25),
                       "c_nudge_or_gt_1": bool(g["nudge_vs_rest"]["or_mh"] > 1),
                       "d_wake_early_lt_1pct": bool(g["frac_wake_early"] < 0.01)}
    (OUTD / "r1b_gate.json").write_text(json.dumps(R, indent=1, default=float))
    print(json.dumps(R, indent=1, default=float)[:8000])


if __name__ == "__main__":
    main()
