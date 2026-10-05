"""H72 round 2 per-period estimates -> shared per_period_estimates (infra/shared/estimates.py: write_estimates).
Reads r2/results_r2.json and r2/wakes_r2.parquet (dates only). Usage: uv run python .../analysis/estimates_r2.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(HERE))
import estimates as E  # noqa: E402
import r2lib as R  # noqa: E402

import polars as pl  # noqa: E402

SRC = "data/processed/H72-trap-aging-input-starvation/r2/results_r2.json"
NOTE = "round 2 (2026-10-05)"
CH = "idle wakes (sustained escape; ledger call clock; consolidation-start traps dropped)"
FULL = "agent-FE logit, full model B+S+C+F+A (regime I: B+S+C+A), day-block bootstrap 200"
CV = "5 interleaved day folds, held-out log-lik (nats per 1,000 wakes); day bootstrap 1000 of per-day contributions"


def ok(x):
    return x if (x is not None and isinstance(x, (int, float)) and math.isfinite(x)) else None


def main():
    d = json.loads((R.R2 / "results_r2.json").read_text())
    w = pl.read_parquet(R.R2 / "wakes_r2.parquet").filter(pl.col("r16"))
    days = {int(g): (a, b) for g, a, b in w.group_by("goal_no").agg(pl.col("pt_date").min().alias("a"),
                                                                     pl.col("pt_date").max().alias("b")).iter_rows()}
    rows = []

    def base(g):
        a, b = days[g]
        u = E.map_unit(g, a, b) or f"local:{g}_{a[5:]}_{b[5:]}"
        return dict(period_unit=u, goal_no=g, first_day=a, last_day=b, source=SRC, ci_level=0.95, ci_kind="percentile",
                    notes=NOTE, post_hoc=False, status="ok")

    def add(g, stat, v, method, null, n, n_kind, channel=CH, role="replication", ci_kind="percentile", **kw):
        if isinstance(v, dict):
            est, lo, hi, se = v["est"], v["ci"][0], v["ci"][1], v.get("se")
        else:
            est, lo, hi, se = v[0], v[1], v[2], None
        rows.append(base(g) | dict(statistic=stat, channel=channel, role=role, estimate=ok(est), ci_lo=ok(lo), ci_hi=ok(hi),
                                   se=ok(se), n=float(n), n_kind=n_kind, method=method, null=null, ci_kind=ci_kind) | kw)

    for gs, r in d["r1"].items():
        g = int(gs[1:])
        if "bC_full" not in r:
            continue
        add(g, "chatter_hold_beta_C", r["bC_full"], FULL, "0 (no hold)", r["n"], "wakes",
            channel=CH + "; ln(1 + undirected items read at the 5 calls before the wake)")
        add(g, "chatter_hold_beta_C_no_S_F", r["bC_BAC"], FULL.replace("full model B+S+C+F+A (regime I: B+S+C+A)", "B+A+C"),
            "0", r["n"], "wakes", channel=CH + "; ln(1 + undirected items, 5 calls)")
        add(g, "wake_index_slope_given_mechanisms", r["bk_full"], FULL, "0 (no aging)", r["n"], "wakes",
            channel=CH + "; ln k (wake index)")
        if "bf_full" in r:
            add(g, "urn_coefficient_ln1mf_given_age_chatter", r["bf_full"], FULL, "0; urn +1", r["n"], "wakes",
                channel=CH + "; ln(1 - own idle share of own calls in the segment)")
    for gs, v in d["reconcile"].items():
        g = int(gs[1:])
        if g not in (37, 38, 40, 41, 44, 51):
            continue
        cv = v["cv"]
        n = d["r1"][gs]["n"]
        for m, nm in (("A", "clocks"), ("S", "starvation"), ("C", "chatter"), ("F", "selfshare")):
            if f"gain_{m}" in cv:
                add(g, f"heldout_gain_{nm}_nats_per_1000", cv[f"gain_{m}"], CV, "0", n, "wakes")
        if g == 51:
            for m, nm in (("S", "starvation"), ("C", "chatter"), ("F", "selfshare"), ("SCF", "all_three")):
                add(g, f"aging_share_explained_{nm}", cv[f"eps_{m}"], CV + "; eps = 1 - [LL(B+M+A) - LL(B+M)] / [LL(B+A) - LL(B)]",
                    "0 (unrelated); proxy worlds <= 0.22 for self-share", n, "wakes")
    e = d["g51_extras"]
    n51 = d["r1"]["G51"]["n"]
    for k, stat in (("bC_k1", "chatter_hold_beta_C_first_wakes"), ("bC_dayfe", "chatter_hold_beta_C_agent_day_fe"),
                    ("b_int", "chatter_hold_x_directed_read_interaction"), ("b_inflight", "inflight_placebo_given_full_model"),
                    ("b_rate", "chatter_rate_slope_competing_rates_test")):
        add(51, stat, e[k], FULL + f" ({k})", "competing-rates form: -1" if "rate" in k else "0",
            e[k].get("n") or n51, "wakes")
    for t, v in d["transfer"].items():
        if t.startswith("G51_from"):
            continue
        g = int(t[1:])
        for m, nm in (("S", "starvation"), ("C", "chatter"), ("F", "selfshare"), ("A", "clocks")):
            add(g, f"transfer_gain_{nm}_from_G51_nats_per_1000", v[m],
                "G51 slopes as a fixed offset; target base refitted on 5 day folds; held-out gain over the base; day bootstrap 1000",
                "0 (no transfer)", d["r1"][t]["n"], "wakes")
    df = E.write_estimates(rows, hypothesis="H72")
    print("estimate rows", df.height)


if __name__ == "__main__":
    main()
