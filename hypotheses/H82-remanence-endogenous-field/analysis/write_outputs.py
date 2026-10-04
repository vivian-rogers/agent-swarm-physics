"""H82: per-boundary period READMEs (G<P>, role replication) and per_period_estimates rows (replication + natives).

Per-boundary verdict rule (written 2026-10-04 after the pooled result, before per-boundary values were read; labelled in
the card): with b = the model's S0 mean bias of Delta gamma_1 (bge 0.022, gte 0.033), a boundary is positive in a model
if its bootstrap 95% lower bound of Delta gamma_1 exceeds b. Verdict supported = positive in both models; failed = upper
bound < b + 0.05 in both models (rules out the effect that matters); otherwise mixed (inconclusive).
Usage: uv run python hypotheses/H82-remanence-endogenous-field/analysis/write_outputs.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h82lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
import estimates as E  # noqa: E402

SRC = "hypotheses/H82-remanence-endogenous-field"
HYP = L.ROOT / SRC / "goalperiod-subhypotheses"
CH = {"bge_small": "content_bge", "gte_modernbert": "content_gte"}
M2 = ("bge_small", "gte_modernbert")


def main():
    rows = pl.read_parquet(L.OUT / "replication/boundary_rows.parquet")
    bias = {m: json.loads((L.OUT / f"synthetic/synthetic_{m}.json").read_text())["scenarios"]["S0"]["mean:all/e/mean_dg1"] for m in M2}
    prim = rows.filter((pl.col("config") == "primary") & (pl.col("term") == "e"))
    split = rows.filter(pl.col("config") == "newcomer_split")
    est, table = [], []
    for P in sorted(set(prim["P"].to_list())):
        d1 = {m: prim.filter((pl.col("model") == m) & (pl.col("P") == P) & (pl.col("d") == 1)).row(0, named=True) for m in M2}
        pos = all(d1[m]["dgamma_lo"] > bias[m] for m in M2)
        neg = all(d1[m]["dgamma_hi"] < bias[m] + 0.05 for m in M2)
        verdict = "supported" if pos else "failed" if neg else "mixed"
        r0 = d1["bge_small"]
        prof = {m: prim.filter((pl.col("model") == m) & (pl.col("P") == P)).sort("d") for m in M2}
        nsp = split.filter((pl.col("model") == "bge_small") & (pl.col("P") == P) & (pl.col("term") == "e_new"))
        n_new = int(nsp["n_group"].max()) if nsp.height else 0
        f = lambda x: f"{x:+.3f}" if x == x else "n/a"  # noqa: E731
        lines = [f"# H82 × G{P:02d}: boundary #{r0['prev']} → #{P} (day 1 = {r0['day']})", "",
                 f"**Verdict:** {verdict}", "**Role:** replication",
                 f"**Period:** regime {r0['regime']} · {r0['n_agents']} agents with a prior on day 1 · {r0['n_placebo']} placebo centroids · newcomers on days 1–5: {n_new}.",
                 "", "## Why this period",
                 f"Every eligible goal boundary (both sides non-holdout, one regime) is a replication point of the remanence regression. Here the endogenous field is the #{r0['prev']} village centroid.",
                 "", "## Prediction",
                 "*Written 2026-10-04 20:07 UTC in the card (P1–P3), before any real-data statistic; this folder was generated after the run.*",
                 "- Δγ_1 > 0 beyond the S0 bias (P1), γ[P−1] > γ[P+1] (P2), decay over days 1–5 (P3). Per-boundary verdict rule in `analysis/write_outputs.py`.",
                 "", "## Result", "| Quantity | bge | gte |", "| --- | --- | --- |"]
        for lab, key in (("γ_1 [P−1 centroid]", "gamma_prev"), ("median γ_1 [placebo centroids]", "gamma_placebo_med"),
                         ("γ_1 [P+1 centroid]", "gamma_next")):
            lines.append(f"| {lab} | {f(d1['bge_small'][key])} | {f(d1['gte_modernbert'][key])} |")
        lines.append(f"| Δγ_1 [95% agent bootstrap] | {f(d1['bge_small']['dgamma'])} [{f(d1['bge_small']['dgamma_lo'])}, {f(d1['bge_small']['dgamma_hi'])}] | {f(d1['gte_modernbert']['dgamma'])} [{f(d1['gte_modernbert']['dgamma_lo'])}, {f(d1['gte_modernbert']['dgamma_hi'])}] |")
        lines.append(f"| asymmetry A_1 = γ[P−1] − γ[P+1] | {f(d1['bge_small']['asym'])} | {f(d1['gte_modernbert']['asym'])} |")
        lines.append(f"| Δγ_d, d = 1…{prof['bge_small'].height} | {', '.join(f(x) for x in prof['bge_small']['dgamma'].to_list())} | {', '.join(f(x) for x in prof['gte_modernbert']['dgamma'].to_list())} |")
        lines += ["", f"S0 bias of Δγ_1 (pooled synthetic): bge {bias['bge_small']:+.3f}, gte {bias['gte_modernbert']:+.3f}. Data: `data/processed/H82-remanence-endogenous-field/replication/boundary_rows.parquet`.",
                  "", "## Scorecard (period-specific axes)",
                  "- C: Δγ_1 against placebo centroids. D: the time asymmetry and the day profile are unfitted signatures.",
                  "", "## Notes", "- One boundary is one design; per-boundary CIs come from resampling agents (few agents in regime I)."]
        (HYP / f"G{P:02d}" / "figures").mkdir(parents=True, exist_ok=True)
        (HYP / f"G{P:02d}" / "README.md").write_text("\n".join(lines) + "\n")
        table.append((P, r0["prev"], verdict, {m: d1[m] for m in M2}))
        for m in M2:
            r = d1[m]
            se = r["dgamma_se"] if r["dgamma_se"] == r["dgamma_se"] else None
            est.append({"period_unit": f"G{P:02d}", "goal_no": P, "statistic": "remanence_excess_dgamma_d1", "channel": CH[m],
                        "estimate": r["dgamma"], "ci_lo": r["dgamma_lo"], "ci_hi": r["dgamma_hi"], "se": se, "ci_level": 0.95,
                        "ci_kind": "percentile", "n": r["n_agents"], "n_kind": "agents",
                        "method": "day-1 loading on the leave-i-out previous-period centroid minus median placebo-centroid loading; "
                                  "kickoff, goal, previous kickoff, human centroid, room kickoff and leave-out prior as regressors",
                        "null": f"placebo centroids ({r['n_placebo']}); S0 bias {bias[m]:+.3f}", "role": "replication",
                        "first_day": r["day"], "last_day": r["day"], "source": f"{SRC}/analysis/replication.py",
                        "notes": f"from #{r['prev']}; asymmetry {r['asym']:+.3f}"})
    nat = json.loads((L.OUT / "natives/natives.json").read_text())
    for m in M2:
        n27 = nat["NE27"][m]
        for term in ("e_vet", "e_new"):
            re = n27[term]["re"]
            est.append({"period_unit": "local:NE27", "goal_no": 10, "statistic": f"NE27_dgamma_{term}_d1_3", "channel": CH[m],
                        "estimate": n27[term]["mean_dgamma_d1_3"], "ci_lo": re["lo"], "ci_hi": re["hi"], "se": re["se"],
                        "ci_level": 0.95, "ci_kind": "se_z", "n": max(n27[term]["n_group"]), "n_kind": "agents",
                        "method": "#8 centroid loading excess on days 1-3 of #10 (RE over days)", "null": "regime-I placebo centroids",
                        "role": "native", "first_day": n27["days"][0], "last_day": n27["days"][-1],
                        "source": f"{SRC}/analysis/natives.py"})
        n32 = nat["NE32"][m]
        for k in ("dgamma_new", "dgamma_inc"):
            est.append({"period_unit": "local:NE32", "goal_no": 51, "statistic": f"NE32_history_{k}", "channel": CH[m],
                        "estimate": n32[k], "ci_lo": n32[k + "_ci"][0], "ci_hi": n32[k + "_ci"][1], "ci_kind": "percentile",
                        "ci_level": 0.95, "n": n32["n_obs_new"] if k.endswith("new") else n32["n_obs_inc"], "n_kind": "agent-days",
                        "method": "history-centroid (#36-#44) loading minus median single-period loading, #51 fields, own goal, family prior and #51 village centroid as regressors",
                        "null": "single-period placebo centroids", "role": "native", "first_day": n32["days"][0],
                        "last_day": n32["days"][-1], "source": f"{SRC}/analysis/natives.py"})
        n15 = nat["NE15"][m].get("fixed_effect")
        if n15:
            est.append({"period_unit": "local:NE15-room-boundaries", "goal_no": None, "regime": "III", "holdout": False,
                        "statistic": "NE15_gamma_read_minus_unread", "channel": CH[m], "estimate": n15["mu"], "ci_lo": n15["lo"],
                        "ci_hi": n15["hi"], "se": n15["se"], "ci_level": 0.95, "ci_kind": "se_z", "n": n15["k"],
                        "n_kind": "boundaries", "method": "day-1 loading on read minus posted-but-unread previous-period statements (matched hours), fixed-effect over boundaries",
                        "null": "in-flight placebo (unread)", "role": "native", "source": f"{SRC}/analysis/natives.py"})
    df = E.write_estimates(est, hypothesis="H82")
    print("rows written:", df.height)
    for P, prev, v, d in table:
        print(P, prev, v, {m: (round(d[m]["dgamma"], 3), round(d[m]["dgamma_lo"], 3)) for m in M2})


if __name__ == "__main__":
    main()
