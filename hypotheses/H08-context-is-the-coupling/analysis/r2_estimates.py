"""H08 round 2: write per-period rows to the shared per_period_estimates table (infra/shared/estimates.py).

  uv run python hypotheses/H08-context-is-the-coupling/analysis/r2_estimates.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h08lib import *  # noqa: E402,F403
from h08lib import ROOT  # noqa: E402

sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

R2 = OUT / "r2"
SRC = "data/processed/H08-context-is-the-coupling/r2/"


def main():
    rows = []
    for g in sorted(PERIODS):
        f = R2 / gname(g) / "r2_content.json"
        if not f.exists():
            continue
        o = json.loads(f.read_text())
        for m in ("bge", "gte"):
            for sub, lab in (("nonname", "non-name statements"), ("all", "all statements")):
                d = o[m]["own"][sub]
                est, lo, hi = d["delta_boot"]
                rows.append(dict(period_unit=gname(g), goal_no=g, statistic="r2_content_readout_contrast",
                                 channel=f"content {m}, {lab}", estimate=est, ci_lo=lo, ci_hi=hi, n=d["n_read"] + d["n_flight"],
                                 method="read minus in-flight x = cos(s,m) - b(m,i) at matched lag x density strata; "
                                        "1-hour-block bootstrap (R2-A1, A2)",
                                 null="same-message, same-recipient statements 20-60 min away (b); in-flight statements at matched lag",
                                 role="replication", ci_level=0.95, ci_kind="percentile", n_kind="(message, statement) rows",
                                 confirmatory=False, post_hoc=(sub == "all"), status="round 2", source=SRC + f"{gname(g)}/r2_content.json"))
    P = json.loads((R2 / "r4_pooled.json").read_text())
    for gn, v in P["periods"].items():
        g = int(gn[1:])
        for key, stat in (("CFz", "r4_forced_erasure_x_memory_dose"), ("z", "r4_memory_dose_salience")):
            est, lo, hi = v["auth"]["beta"][key]
            rows.append(dict(period_unit=gn, goal_no=g, statistic=stat, channel="reply author", estimate=est, ci_lo=lo, ci_hi=hi,
                             n=v["auth"]["n"], method="LPM, agent x day effects, z x age bins (R4-A1); day bootstrap",
                             null="placebo dose at the next consolidation for non-erased units", role="native",
                             ci_level=0.95, ci_kind="percentile", n_kind="(talk call, sender) units", confirmatory=False,
                             post_hoc=False, status="round 2", source=SRC + f"{gn}/r4_dose.json"))
    A = json.loads((R2 / "r5_audit.json").read_text())
    for gn, v in A["monitor"].items():
        g = int(gn[1:])
        for m in ("bge", "gte"):
            s = (v.get(m) or {}).get("standard")
            if not s:
                continue
            rows.append(dict(period_unit=gn, goal_no=g, statistic="r5_monitor_excess_flagged_pp", channel=f"content {m}",
                             estimate=s["excess_pp"], ci_lo=None, ci_hi=None, n=s["n_agent_days"],
                             method="share of agent-days with M lower bound <= 0 minus the floor expected at the agent-period mean M",
                             null="floor: per-day normal approximation at agent-period mean M", role="replication",
                             ci_kind="none", n_kind="agent-days", confirmatory=False, post_hoc=False, status="round 2",
                             source=SRC + "r5_audit.json"))
        om = A["omitted"].get(gn)
        if om and om["n_items"]:
            rows.append(dict(period_unit=gn, goal_no=g, statistic="r5_ledger_omitted_share", channel="agent messages received",
                             estimate=om["omitted_share"], ci_lo=None, ci_hi=None, n=om["n_items"],
                             method="share of ledger items beyond the 200-event cap", null="none (descriptive)",
                             role="replication", ci_kind="none", n_kind="ledger items", confirmatory=False, post_hoc=False,
                             status="round 2", source=SRC + "r5_audit.json"))
    df = E.write_estimates(rows, hypothesis="H08")
    print(f"wrote {df.height} rows")


if __name__ == "__main__":
    main()
