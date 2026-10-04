"""H115: per-period estimate rows for data/processed/shared/per_period_estimates.parquet (write_estimates).

  uv run python hypotheses/H115-debate-judge-role-recovery/analysis/write_estimates.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h115lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
import estimates as E  # noqa: E402

SRC = "hypotheses/H115-debate-judge-role-recovery/analysis/"


def boot_mean(x, B=10000, seed=1):
    x = np.asarray(x, float)
    rng = np.random.default_rng(seed)
    m = rng.choice(x, (B, len(x))).mean(1)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return float(c - h), float(c + h)


def main():
    rows = []
    r = json.loads((L.DATA / "G12" / "results.json").read_text())
    u = (np.array(r["P1"]["judge_ranks"]) - 1) / (np.array(r["P1"]["n_present"]) - 1)
    lo, hi = boot_mean(u)
    common = dict(period_unit="12a", goal_no=12, role="native", first_day="2025-09-01", last_day="2025-09-04",
                  n_kind="debates", source=SRC + "run_g12_unblind.py")
    rows.append(dict(common, statistic="judge_mean_norm_sink_rank", channel="talk_call", estimate=float(u.mean()),
                     ci_lo=lo, ci_hi=hi, ci_kind="percentile", n=10,
                     method="additive in/out kinetic Ising per debate (lambda 4), blind ranking frozen before labels; "
                            "u = (rank-1)/(n-1), 0 = top sink; bootstrap over debates",
                     null="uniform ranks p 0.15; field-only skeleton null mean 0.46 (p 0.24)", unit_local="u in [0,1]"))
    k = int(r["P1"]["n_rank1"])
    lo, hi = wilson(k, 10)
    rows.append(dict(common, statistic="judge_rank1_share", channel="talk_call", estimate=k / 10, ci_lo=lo, ci_hi=hi,
                     ci_kind="parametric", n=10, method="share of debates where the judge has the largest sink score",
                     null="1/7 = 0.143", notes="Wilson interval"))
    rows.append(dict(common, statistic="team_block_JST_minus_JOT", channel="talk_call",
                     estimate=r["P2"]["ST_minus_OT"], se=r["P2"]["se"],
                     ci_lo=r["P2"]["ST_minus_OT"] - 1.96 * r["P2"]["se"],
                     ci_hi=r["P2"]["ST_minus_OT"] + 1.96 * r["P2"]["se"], ci_kind="se_z", n=10,
                     method="pair-type kinetic Ising pooled over 10 debates (lambda 4), Ising units",
                     null="team re-partition permutation p(<=) 0.01", unit_local="Ising units"))
    rows.append(dict(common, statistic="judge_within_agent_sink_contrast", channel="talk_call",
                     estimate=r["P1b"]["contrast"], se=r["P1b"]["perm_sd"],
                     ci_lo=r["P1b"]["contrast"] - 1.96 * r["P1b"]["perm_sd"],
                     ci_hi=r["P1b"]["contrast"] + 1.96 * r["P1b"]["perm_sd"], ci_kind="se_z", n=10,
                     method="S as judge minus mean S of the same agent as non-judge; SE = permutation SD",
                     null="judge-label permutation p 0.12", unit_local="Ising units"))
    vp = json.loads((L.DATA / "G12" / "verdict_placebo.json").read_text())
    pl_ = np.array(vp["placebo"])
    rows.append(dict(common, statistic="verdict_talk_field_step_debaters", channel="talk_call",
                     estimate=r["P3"]["verdict_step"], se=None, ci_lo=None, ci_hi=None, ci_kind="none", n=10,
                     notes=(f"placebo splits inside deb: mean {pl_.mean():+.2f}, 95% [{np.percentile(pl_, 2.5):.2f}, "
                            f"{np.percentile(pl_, 97.5):.2f}]; pre-registered |step| rule p 0.81 (fails); signed step "
                            f"below all {len(pl_)} placebos (post hoc)"),
                     method="debaters' post-verdict talk intercept step (Ising units); SE = placebo-split SD",
                     null="placebo splits inside deb: p(|step|) 0.81", unit_local="Ising units"))
    for g, unit, fd, ld in (("G26", "26", "2026-01-05", "2026-01-09"), ("G35", "35", "2026-03-16", "2026-03-18"),
                            ("G44", "44b", "2026-05-28", "2026-05-29")):
        rep = json.loads((L.DATA / g / "replication.json").read_text())
        us = [v["u"] for v in rep["windows"].values() if v is not None]
        lo, hi = boot_mean(us) if len(us) > 1 else (None, None)
        rows.append(dict(period_unit=unit, goal_no=int(g[1:]), statistic="leader_mean_norm_sink_rank",
                         channel="talk_call", estimate=float(np.mean(us)), ci_lo=lo, ci_hi=hi, ci_kind="percentile",
                         n=len(us), n_kind="role windows", role="replication", first_day=fd, last_day=ld,
                         method="additive in/out kinetic Ising per role window (lambda 4); u = 0 top sink, 1 top source",
                         null=f"field-only skeleton null mean {rep['summary']['mean_u_null']:.2f}",
                         unit_local="u in [0,1]", source=SRC + "run_replication.py"))
    E.write_estimates(rows, hypothesis="H115")
    print(len(rows), "rows written")


if __name__ == "__main__":
    main()
