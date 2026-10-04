"""Write H84 per-period rows to the shared per_period_estimates table (infra/shared/estimates.py).

Replication: I_Q (bits) at search calls per eligible period. Natives: G37 outage dose x day betas (V1, V3, V4),
NE18 dose x post beta (V1), G51 failed-answer rate ratio.
Usage: uv run python hypotheses/H84-search-outage-memory-scramble/analysis/write_estimates.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

SRC = "data/processed/H84-search-outage-memory-scramble/results/results.json"


def unit(g, first=None, last=None):
    u = E.map_unit(g, first, last)
    return u if u else f"local:G{g:02d}:{first}..{last}"


def main():
    res = json.loads((ROOT / SRC).read_text())
    rows = []
    for k, r in res["replication"].items():
        if k.startswith("_"):
            continue
        g = int(k[1:])
        rows.append({"period_unit": "local:G51-head" if g == 51 else unit(g), "goal_no": g,
                     "statistic": "I_Q_search_allocation_bits",
                     "channel": "history_search", "estimate": r["I"], "ci_lo": r["I_ci"][0], "ci_hi": r["I_ci"][1],
                     "ci_level": 0.95, "ci_kind": "percentile", "se": r["I_se"], "n": r["n"], "n_kind": "search calls",
                     "unit_local": k, "first_day": r["days"][0], "last_day": r["days"][1],
                     "method": "Miller-Madow plug-in I(X+; S_Q) minus within-agent permutation floor (200); agent-day "
                               "cluster bootstrap 300, recentred",
                     "null": f"within-agent permutation p = {r['p_perm']:.3f}", "role": "replication", "source": SRC,
                     "notes": f"verdict {r['verdict']}; answers naming a repo {r['named_share']:.2f}"})
    g37 = res["G37"]
    for k, lab in (("V1_continuity", "continuity share"), ("V3_earlier_goal_refs", "earlier-goal reference share"),
                   ("V4_commits_per20", "work commits per 20 calls")):
        t = g37["tests"][k]
        rows.append({"period_unit": unit(37), "goal_no": 37, "statistic": f"beta_dose_x_outage_{k}",
                     "channel": "history_search", "estimate": t["beta"], "ci_lo": None, "ci_hi": None, "ci_kind": "none",
                     "se": t["placebo"]["sd"], "n": t["n"], "n_kind": "agent-days (12 agents)", "unit_local": "G37-outage",
                     "first_day": "2026-03-31", "last_day": "2026-04-01",
                     "method": f"TWFE OLS of {lab} on dose x outage (03-31, 04-01) with dose x recovery; agent and day "
                               "FE on the 03-24..05-29 regime-III panel; se = SD of 38 placebo-pair betas",
                     "null": f"placebo-pair rank p (predicted direction) {t['placebo']['p_rank']:.3f}; dose permutation "
                             f"p {t['perm_p']:.3f}",
                     "role": "native", "source": SRC,
                     "notes": f"per search per 100 calls; effect at mean searcher dose {t['effect_at_dbar']:+.3f}; "
                              "the outage fully reached one agent"})
    t = res["NE18"]["tests"]["V1_continuity"]
    rows.append({"period_unit": unit(38, "2026-04-06", "2026-04-24"), "goal_no": 38,
                 "statistic": "beta_dose_x_post_V1_continuity", "channel": "history_search", "estimate": t["beta"],
                 "ci_lo": None, "ci_hi": None, "ci_kind": "none", "n": None, "n_kind": "agent-days",
                 "unit_local": "NE18", "first_day": "2026-04-06", "last_day": "2026-04-24",
                 "method": "TWFE OLS dose x post (04-20..04-24), pre 04-06..04-17; agent and day FE",
                 "null": f"placebo-boundary rank p {t['p_rank']:.3f} (17 boundaries; test oversized 0.12-0.22)",
                 "role": "native", "source": SRC, "notes": "no first stage (searchers' answers got shorter)"})
    g = res["G51"]
    rows.append({"period_unit": unit(51, "2026-07-06", "2026-09-04"), "goal_no": 51,
                 "statistic": "rate_ratio_commits_after_failed_search", "channel": "history_search",
                 "estimate": g["rr_failed"], "ci_lo": g["rr_ci"][0], "ci_hi": g["rr_ci"][1], "ci_level": 0.95,
                 "ci_kind": "percentile", "n": g["n"], "n_kind": "search calls", "unit_local": "G51-head",
                 "method": "Poisson FE (agent) of work commits per 20 calls on failed answer (<150 chars), log query "
                           "length, log context position; agent-day bootstrap 300",
                 "null": "RR = 1", "role": "native", "source": SRC,
                 "notes": f"{g['n_failed']} failed answers; descriptive (failures not exogenous)"})
    for r in rows:
        if r["period_unit"].startswith("local:"):
            r["period_unit"] = r["period_unit"].split(":")[0] + ":" + r["unit_local"]
    E.write_estimates(rows, hypothesis="H84")
    print(len(rows), "rows written")


if __name__ == "__main__":
    main()
