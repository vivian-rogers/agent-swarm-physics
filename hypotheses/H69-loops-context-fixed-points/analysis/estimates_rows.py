"""Write H69 per-period rows to the shared per_period_estimates table (write_estimates)."""
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
SRC = "data/processed/H69-loops-context-fixed-points/results.json"


def ok(*x):
    return all(v is not None and isinstance(v, (int, float)) and math.isfinite(v) for v in x)


def main():
    r = json.loads((D / "results.json").read_text())
    rows = []
    for p, o in r["periods"].items():
        g = int(p[1:])
        unit = E.map_unit(g)
        ep = o["episodes"]["r_either"]
        sc = o["scorable"]["episodes"]
        base = dict(period_unit=unit, goal_no=g, source=SRC, post_hoc=False,
                    status="round 1" + ("" if sc else " (not scorable: < 30 episodes)"))
        rows.append(dict(base, statistic="restatement_rate", channel="chat (cross-call, either model)",
                         estimate=ep["rate"], ci_lo=None, ci_hi=None, ci_kind="none", n=ep["n_stmt"],
                         n_kind="statements", method="DQ5 self_repeat bge|gte, source in an earlier call",
                         null="none", role="replication"))

        def add(stat, ch, b, se, n, nk, method, null, role="replication"):
            if ok(b, se):
                rows.append(dict(base, statistic=stat, channel=ch, estimate=b, se=se, ci_lo=b - 1.96 * se,
                                 ci_hi=b + 1.96 * se, ci_level=0.95, ci_kind="se_z", n=n, n_kind=nk, method=method,
                                 null=null, role=role))
        on = o.get("onset") or {}
        add("restatement_onset_b_own", "chat", on.get("b_O"), on.get("se_O"), on.get("n"), "statements at risk",
            "logit entry, agent FE (ridge), log(1+own statements in segment), agent-day cluster SE", "b = 0")
        add("restatement_onset_b_room", "chat", on.get("b_K"), on.get("se_K"), on.get("n"), "statements at risk",
            "logit entry, agent FE, log(1+room items in segment) at fixed own count", "b = 0")
        add("restatement_onset_b_selfshare", "chat", on.get("b_s"), on.get("se_s"), on.get("n"), "statements at risk",
            "logit entry, agent FE, self-share O/(O+K)", "b = 0", role="native" if p == "G38" else "replication")
        ex = o.get("exit") or {}
        add("restatement_exit_logOR_forced_erasure", "chat", ex.get("b_forced_between"), ex.get("se_forced_between"),
            ex.get("n"), "statements in a loop", "logit exit, agent FE, controls calls/lag/n_prev", "OR = 1")
        add("restatement_exit_b_novel_read", "chat", ex.get("b_nov_read"), ex.get("se_nov_read"), ex.get("n"),
            "statements in a loop", "logit exit, log(1+novel items read), bge novelty", "b = 0")
        of = o.get("onset_forced") or {}
        add("restatement_onset_logOR_after_forced_erasure", "chat", of.get("b"), of.get("se"), of.get("n"),
            "statements at risk", "logit entry with forced-erasure indicator (NE41)", "OR = 1", role="native")
        en = o.get("enrich") or {}
        if ok(en.get("log_or"), en.get("lo"), en.get("hi")):
            rows.append(dict(base, statistic="restatement_in_context_enrichment_logOR", channel="chat pairs",
                             estimate=en["log_or"], se=en.get("se"), ci_lo=en["lo"], ci_hi=en["hi"], ci_level=0.95,
                             ci_kind="percentile", n=en["n_pairs"], n_kind="statement pairs",
                             method="Mantel-Haenszel, strata agent x 0.1-decade lag x calls-between bin; agent-day bootstrap",
                             null="OR = 1 (pseudo-erasure OR reported)", role="native" if p == "G38" else "replication"))
        if p == "G51" and o.get("exit_kicks"):
            k = o["exit_kicks"]
            add("restatement_exit_b_nudge_read", "chat", k.get("b_read_nudge"), k.get("se_read_nudge"), k.get("n"),
                "statements in a loop", "logit exit, log(1+nudges read); in-flight nudges as placebo", "b = 0",
                role="native")
    E.write_estimates(rows, hypothesis="H69")
    print(len(rows), "rows written")


if __name__ == "__main__":
    main()
