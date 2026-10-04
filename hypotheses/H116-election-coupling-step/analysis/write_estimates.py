"""H116: per-period estimate rows for data/processed/shared/per_period_estimates.parquet (write_estimates).

  uv run python hypotheses/H116-election-coupling-step/analysis/write_estimates.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h116lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
import estimates as E  # noqa: E402

SRC = "hypotheses/H116-election-coupling-step/analysis/"


def z(est, se):
    return dict(estimate=est, se=se, ci_lo=est - 1.96 * se, ci_hi=est + 1.96 * se, ci_kind="se_z")


def main():
    r = json.loads((L.DATA / "G26" / "results.json").read_text())
    ev = r["event"]
    m = ev["magnitude"]
    ph = json.loads((L.DATA / "G26" / "posthoc_n2.json").read_text())
    c26 = dict(period_unit="26", goal_no=26, role="native", first_day="2026-01-05", last_day="2026-01-09",
               channel="talk_call", unit_local="Ising units", n_kind="reader-calls", source=SRC + "run_g26.py")
    rows = [
        dict(c26, statistic="winner_out_coupling_step_result", n=ev["n"],
             method="winner-focused per-call kinetic Ising, 83-min windows around the 01-05 result, lambda 0.01 (magnitude)",
             null=(f"lambda-4 statistic +{ev['coef']['dJout']:.3f}: pct {ev['pct_dJout_time']:.2f} of 16 time placebos, "
                   f"{ev['pct_dJout_skeleton']:.2f} of 200 skeleton worlds"), **z(m["dJout"]["est"], m["dJout"]["se"])),
        dict(c26, statistic="winner_in_coupling_step_result", n=ev["n"],
             method="winner-focused per-call kinetic Ising, 83-min windows around the 01-05 result, lambda 0.01 (magnitude)",
             null=f"lambda-4 statistic pct {ev['pct_dJin_time']:.2f} of time placebos", **z(m["dJin"]["est"], m["dJin"]["se"])),
        dict(c26, statistic="winner_out_coupling_step_read_minus_inflight", n=ev["n"],
             method="read-gated minus in-flight out-coupling step at the 01-05 result, lambda 0.01",
             null=f"lambda-4 pct {ev['pct_rmi_time']:.2f} of time placebos",
             **z(m["read_minus_inflight"]["est"], m["read_minus_inflight"]["se"])),
        dict(c26, statistic="winner_out_coupling_step_reelection", n=None, post_hoc=True,
             method="winner-focused per-call kinetic Ising, 44-min untrimmed windows around the 01-09 re-election, lambda 0.01",
             null=(f"pre-registered control (expected no step) failed: lambda-4 +0.31, above all event-offset placebos; "
                   f"post hoc above all {ph['n_placebos']} re-election-offset placebos and 200 skeleton worlds"),
             **z(ph["magnitude"]["dJout"]["est"], ph["magnitude"]["dJout"]["se"])),
        dict(c26, statistic="winner_pair_ep_step_result", n=None, ci_kind="none", ci_lo=None, ci_hi=None,
             estimate=ev["dEP_w"], unit_local="nats per call",
             method="held-out Newton bound (ep_newton_heldout) on call-clock multipartite observables, winner pairs",
             null=f"pct {ev['pct_dEP_w_time']:.2f} of time placebos; bound <= 0 in both windows (below resolution)"),
    ]
    for g, unit, fd, ld, stat in (("G12", "12a", "2025-09-01", "2025-09-04", "judge_out_coupling_role_step"),
                                  ("G35", "35", "2026-03-16", "2026-03-20", "lead_out_coupling_role_step")):
        rep = json.loads((L.DATA / g / "replication.json").read_text())
        rows.append(dict(period_unit=unit, goal_no=int(g[1:]), statistic=stat, channel="talk_call", role="replication",
                         first_day=fd, last_day=ld, n=rep["n_role_windows"], n_kind="role windows",
                         unit_local="Ising units", source=SRC + "run_replication.py",
                         method="role-step per-call kinetic Ising pooled over windows (lambda 4, shrunk toward 0)",
                         null=f"designated-label permutation p(>=) {rep['p_perm_dOut_greater']:.2f}",
                         **z(rep["obs"]["dOut"], rep["obs"]["se_dOut"])))
    E.write_estimates(rows, hypothesis="H116")
    print(len(rows), "rows written")


if __name__ == "__main__":
    main()
