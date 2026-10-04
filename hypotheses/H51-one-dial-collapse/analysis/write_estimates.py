"""Write H51 per-period rows to the shared per_period_estimates table (infra/shared/estimates.py). Non-holdout only.

Replication rows (period_unit 'G<NN>'):
  one_dial_index_u        position on the shared single index u = w.z (w fitted on all four observables; z = standardized
                          g_lag, asinh(c_x/0.01), S_text, log N). Channel 'phase diagram'. No CI.
  one_dial_residual_z     D1 (g_lag) LOPO residual / residual SD, one row per observable (channel = observable)
  loop_rate_restatement   chat self-repeat share (either model), Wald CI (channel 'chat')
  herding_share_excess    cowork rate minus circular-shift null mean (H11 definition re-implemented; channel 'project')
  idea_branching_R_ledger R_hat with H34's rule on its ledger first-use tables, Wald CI (channel 'ideas')
Native rows (role native): the same three observables per #51 sub-unit (51a-51l) and per #36 sub-unit.
Usage: uv run python hypotheses/H51-one-dial-collapse/analysis/write_estimates.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h51lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra" / "shared"))
import estimates as E  # noqa: E402

SRC_P = "data/processed/H51-one-dial-collapse/results/phase_points.parquet"
SRC_O = "data/processed/H51-one-dial-collapse/observables_periods.parquet"
SRC_N = "data/processed/H51-one-dial-collapse/natives_units.parquet"


def f(x):
    return None if x is None or not np.isfinite(x) else float(x)


def wald(p, n):
    if p is None or n is None or not np.isfinite(p) or n <= 0:
        return None, None
    s = np.sqrt(p * (1 - p) / n)
    return float(max(p - 1.96 * s, 0.0)), float(min(p + 1.96 * s, 1.0))


def obs_rows(r, unit, goal, role, first_day=None, last_day=None):
    rows = []
    lo, hi = wald(r.get("loop_rate"), r.get("n_stmt"))
    if f(r.get("loop_rate")) is not None:
        rows.append(dict(statistic="loop_rate_restatement", channel="chat", estimate=f(r["loop_rate"]), ci_lo=lo, ci_hi=hi,
                         ci_level=0.95 if lo is not None else None, ci_kind="se_z" if lo is not None else "none",
                         n=r.get("n_stmt"), n_kind="chat statements",
                         method="share of agent chat statements flagged self_repeat by either model (DQ5 statement_flags)",
                         null=None))
    lo, hi = wald(r.get("R_hat"), r.get("R_n"))
    if f(r.get("R_hat")) is not None:
        rows.append(dict(statistic="idea_branching_R_ledger", channel="ideas", estimate=f(r["R_hat"]), ci_lo=lo, ci_hi=hi,
                         ci_level=0.95 if lo is not None else None, ci_kind="se_z" if lo is not None else "none",
                         n=r.get("R_n"), n_kind="first uses",
                         method="H34 rule (status 1 with agent parent / all first uses) on H34 r1b ledger first-use tables",
                         null="critical R = 1"))
    if f(r.get("herd_own")) is not None:
        rows.append(dict(statistic="herding_share_excess", channel="project", estimate=f(r["herd_own"]), ci_lo=None, ci_hi=None,
                         ci_level=None, ci_kind="none", n=r.get("herd_own_n"), n_kind="labelled agent-windows",
                         method="H11 cowork definition re-implemented: share of agents in (day, 30-min window, room) blocks "
                                "sharing their raw project with >= 1 block-mate, minus circular-shift null mean (20 draws)",
                         null="circular shift within agent-day"))
    for x in rows:
        x.update(period_unit=unit, goal_no=goal, role=role, first_day=first_day, last_day=last_day)
    return rows


def main():
    pts = pl.read_parquet(L.ROOT / SRC_P)
    op = pl.read_parquet(L.ROOT / SRC_O)
    nu = pl.read_parquet(L.ROOT / SRC_N)
    rows = []
    # single index on all four observables (the period's coordinate on the one dial)
    d = L.common_sample(L.load())
    Z = np.column_stack([L.zs(d[a].to_numpy()) for a in L.AXES])
    Ys = {j: L.zs(d[j].to_numpy().astype(float)[d[j].is_not_null().to_numpy()]) for j in L.OBS}
    masks = {j: d[j].is_not_null().to_numpy() for j in L.OBS}
    w = L.fit_index({"Z": Z}, Ys, masks, seed=0)
    u = Z @ w
    wtxt = ", ".join(f"{a} {x:+.2f}" for a, x in zip(L.AXES, w))
    for g, val in zip(d["goal_no"].to_list(), u):
        rows.append(dict(period_unit=f"G{g:02d}", goal_no=g, role="replication", statistic="one_dial_index_u",
                         channel="phase diagram", estimate=float(val), ci_lo=None, ci_hi=None, ci_kind="none", n=None,
                         method=f"shared single index u = w.z over standardized (g_lag, asinh(c_x/0.01), S_text, log N); "
                                f"w fitted on all four observables: {wtxt}", null="regime labels; log N",
                         source=SRC_P))
    for r in pts.iter_rows(named=True):
        for j in L.OBS:
            z = r.get(f"{j}_zK")
            if z is not None and np.isfinite(z):
                rows.append(dict(period_unit=f"G{r['goal_no']:02d}", goal_no=r["goal_no"], role="replication",
                                 statistic="one_dial_residual_z", channel=j, estimate=float(z), ci_lo=None, ci_hi=None,
                                 ci_kind="none", n=None, method="LOPO residual of Y_j on g_lag (D1) / residual SD",
                                 null="|z| < 1.28 (80% band)", source=SRC_P))
    for r in op.iter_rows(named=True):
        for x in obs_rows(r, f"G{r['goal_no']:02d}", r["goal_no"], "replication"):
            x["source"] = SRC_O
            rows.append(x)
    pu = pl.read_parquet(L.ROOT / "data/processed/shared/period_units.parquet").select("unit_id", "first_day", "last_day")
    for r in nu.join(pu, on="unit_id").filter(pl.col("goal_no").is_in([36, 51])).iter_rows(named=True):
        for x in obs_rows(r, r["unit_id"], r["goal_no"], "native", r["first_day"], r["last_day"]):
            x["source"] = SRC_N
            rows.append(x)
    out = E.write_estimates(rows, hypothesis="H51")
    print(f"wrote {out.height} rows")


if __name__ == "__main__":
    main()
