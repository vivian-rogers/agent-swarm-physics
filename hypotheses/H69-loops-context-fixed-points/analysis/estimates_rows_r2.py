"""Write H69 round-2 per-period rows to the shared per_period_estimates table (write_estimates).

  uv run python hypotheses/H69-loops-context-fixed-points/analysis/estimates_rows_r2.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

D = ROOT / "data/processed/H69-loops-context-fixed-points"
SRC = "data/processed/H69-loops-context-fixed-points/results_r2.json"


def ok(*x):
    return all(v is not None and isinstance(v, (int, float)) and math.isfinite(v) for v in x)


def main():
    r = json.loads((D / "results_r2.json").read_text())
    rows = []
    for p, o in r["periods"].items():
        g = int(p[1:])
        sc = o["scorable"]
        base = dict(period_unit=E.map_unit(g), goal_no=g, source=SRC, post_hoc=False)

        def add(stat, ch, t, n, nk, method, null, scor, role="replication", post_hoc=False):
            if t and ok(t.get("b"), t.get("se")):
                b, se = t["b"], t["se"]
                rows.append(dict(base, statistic=stat, channel=ch, estimate=b, se=se, ci_lo=b - 1.96 * se,
                                 ci_hi=b + 1.96 * se, ci_level=0.95, ci_kind="se_z", n=n, n_kind=nk, method=method,
                                 null=null, role=role, post_hoc=post_hoc,
                                 status="round 2, 2026-10-05" + ("" if scor else " (not scorable)")))
        r1 = o.get("r1_all") or {}
        add("restatement_onset_b_own_tool_tokens", "chat + prompt tokens", r1.get("U_k"), r1.get("n"),
            "statements at risk", "logit entry, agent FE, log(1+own tool tokens/1000) (H45 P minus room ruler, "
            "minus own chat) at fixed own statements, room items, ctx_pos; agent-day cluster SE", "b = 0",
            sc.get("R1_all"))
        add("restatement_onset_b_own_given_tokens", "chat + prompt tokens", r1.get("o_ctx"), r1.get("n"),
            "statements at risk", "logit entry, agent FE, log(1+own statements in segment) with own tool tokens in "
            "the model", "b = 0", sc.get("R1_all"))
        ex = o.get("r2_exit_dose") or {}
        add("restatement_exit_b_erasure_dose", "chat + prompt tokens", ex.get("dose_c"), ex.get("n"),
            "statements in a loop", "logit exit, agent FE, erasure x centered log(1+own tokens removed/1000)",
            "b = 0", p in ("G38", "G40", "G41", "G51"))
        m = (o.get("r3") or {}).get("P1")
        if m and ok(m.get("log_or"), m.get("lo"), m.get("hi")):
            rows.append(dict(base, statistic="restatement_erased_source_in_memory_logOR", channel="chat pairs + memory",
                             estimate=m["log_or"], se=m.get("se"), ci_lo=m["lo"], ci_hi=m["hi"], ci_level=0.95,
                             ci_kind="percentile", n=m["n"], n_kind="erased statement pairs",
                             method="Mantel-Haenszel, erased sources, in memory (word 3-gram containment >= 0.5 in "
                                    "the memory at t) vs not; strata agent x lag x calls; agent-day bootstrap",
                             null="OR = 1", role="replication",
                             status="round 2, 2026-10-05" + ("" if sc.get("R3") else " (not scorable)")))
        cp = (o.get("r3_composition") or {}).get("copies") or {}
        if ok(cp.get("in_mem")) and cp.get("n", 0) >= 30:
            rows.append(dict(base, statistic="restatement_erased_copies_share_in_memory", channel="chat pairs + memory",
                             estimate=cp["in_mem"], ci_lo=None, ci_hi=None, ci_kind="none", n=cp["n"],
                             n_kind="erased near-copy pairs", method="share of cross-erasure near-copies whose source "
                             "is in the memory at t (containment >= 0.5)", null="none", role="replication",
                             status="round 2, 2026-10-05 (descriptive)"))
        ph = (o.get("posthoc_exit_mem") or {}).get("terms") or {}
        add("restatement_exit_logOR_erasure_x_memory", "chat + memory", ph.get("erased_inmem"),
            (o.get("posthoc_exit_mem") or {}).get("n"), "statements in a loop",
            "POST HOC: logit exit, erasure x (looping statement in memory at t)", "b = 0", sc.get("R3"),
            post_hoc=True)
    E.write_estimates(rows, hypothesis="H69")
    print(len(rows), "rows written")


if __name__ == "__main__":
    main()
