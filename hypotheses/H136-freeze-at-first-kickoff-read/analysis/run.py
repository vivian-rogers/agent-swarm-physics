"""H136 round 1 pipeline after the precondition stop: structural estimates rows, results JSON, period READMEs.

The structural precondition failed in every unit (scheme/structure.py), so this script computes no freeze time, no
call lag K, no settled project and no peer-link read. It writes only read-out statistics that the precondition used.

  uv run python hypotheses/H136-freeze-at-first-kickoff-read/analysis/run.py [--no-estimates] [--no-readmes]
"""
from __future__ import annotations

import datetime as dt
import json
import math
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "scheme"))
import h136lib as L  # noqa: E402
from common import git_commit  # noqa: E402

SEED = 20261007
NBOOT = 2000
GOAL = {n: g for n, g, _ in L.UNITS}
ROOMNAME = {2: "#best", 3: "#rest"}


def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def boot_median(x, rng):
    x = np.asarray(x, float)
    b = np.median(rng.choice(x, size=(NBOOT, len(x)), replace=True), axis=1)
    return float(np.median(x)), float(np.quantile(b, 0.025)), float(np.quantile(b, 0.975))


def unit_stats(R: pl.DataFrame, units: list[dict], rng) -> list[dict]:
    out = []
    for u in units:
        r = R.filter(pl.col("unit") == u["unit"])
        n = r.height
        k2 = int((r["D_r_min"] < 2).sum())
        med, lo, hi = boot_median(r["D_r_wall_min"].to_numpy() * 60, rng)
        out.append(dict(unit=u["unit"], goal_no=u["goal_no"], room=u["room"], day=u["kickoff_day"], n=n,
                        n_dar=u["n_delayed_active_readers"], n_delayed=u["n_delayed"], n_active_before=u["n_active_before"],
                        prev_day_reserved=u["prev_day_reserved"], share_2min=k2 / n, share_2min_ci=wilson(k2, n),
                        read_delay_med_s=med, read_delay_ci=(lo, hi), n_first_call=u["n_read_is_first_call"],
                        max_D_r=u["D_r_max_all"], passes=u["passes_precondition"]))
    return out


def estimates(S: list[dict]):
    sys.path.insert(0, str(L.ROOT / "infra/shared"))
    import estimates as E
    src = "data/processed/H136-freeze-at-first-kickoff-read/structure/readers.parquet"
    rows = []
    for s in S:
        base = dict(period_unit=f"local:k{s['unit']}", unit_local=s["unit"], goal_no=s["goal_no"], first_day=s["day"],
                    last_day=s["day"], channel="readout", role="replication", source=src, post_hoc=False,
                    n=float(s["n"]), n_kind="agents")
        rows.append({**base, "statistic": "h136_delayed_active_readers", "estimate": float(s["n_dar"]), "ci_lo": None,
                     "ci_hi": None, "ci_kind": "none", "method": "count of kickoff readers with >=1 own call in the 30 active min "
                     "before t_k and D_r >= 2 active min (or >= 2 own calls in (t_k, t_r)); DQ1 ledger", "null": None,
                     "status": "ok", "notes": "structural precondition (needs >= 5); previous day reserved" if s["prev_day_reserved"]
                     else "structural precondition (needs >= 5)"})
        rows.append({**base, "statistic": "h136_kickoff_read_delay_median_s", "estimate": s["read_delay_med_s"],
                     "ci_lo": s["read_delay_ci"][0], "ci_hi": s["read_delay_ci"][1], "ci_level": 0.95, "ci_kind": "percentile",
                     "method": "median wall-clock seconds from the unit's first kickoff post to each reader's first DQ1 "
                     "receiving call; bootstrap over readers (2000)", "null": None, "status": "ok"})
        lo, hi = s["share_2min_ci"]
        rows.append({**base, "statistic": "h136_share_read_within_2_active_min", "estimate": s["share_2min"], "ci_lo": lo,
                     "ci_hi": hi, "ci_level": 0.95, "ci_kind": "parametric", "method": "share of kickoff readers with D_r < 2 "
                     "active min; Wilson interval", "null": None, "status": "ok"})
    E.write_estimates(rows, hypothesis="H136")
    return len(rows)


PRED = {
    "G44": "N1: #best meets P2 and P3 (K small, ρ(K, D_r) ∋ 0); #rest has < 1/3 of agents frozen on a named target within "
           "2 active h. Precondition first: each room needs ≥ 5 delayed active readers for O1/O3.",
    "G40": "N2: the kickoff-read anchor beats the hub-link anchor (O4). Replication: P1–P3 if ≥ 5 delayed active readers.",
}


def readme(goal: int, rows: list[dict], syn: dict) -> str:
    title = f"# H136 × G{goal:02d}: kickoff read-out and freeze (kickoff day {rows[0]['day']})\n\n"
    role_line = "replication" + (" + native N1" if goal == 44 else " + native N2" if goal == 40 else "")
    pred = PRED.get(f"G{goal}", "Replication (card, written 2026-10-07): if the unit has ≥ 5 delayed active readers, "
                    "P1 (b CI ∋ 1, excludes 0), P2 (K ≤ 2 for ≥ 1/2 of frozen agents), P3 (ρ(K, D_r) CI ∋ 0). "
                    "Otherwise the kill is untestable here.")
    lines = [title, "**Verdict:** n/a (untestable: structural precondition not met; no freeze time computed)\n",
             "**Role:** exploratory\n",
             f"**Period:** regime {'I' if goal <= 32 else 'II' if goal <= 36 else 'III'} · kickoff unit(s): "
             + ", ".join(f"{r['unit']} ({r['n']} readers)" for r in rows) + f" · layer: {role_line}.\n\n",
             "## Why this period\n",
             "A card candidate kickoff (Design, replication list)" + (" with a regime-I kickoff-frozen consensus event in H31"
                                                                       if goal in (18, 19, 26) else "")
             + (" and the native named-room contrast (N1)" if goal == 44 else "")
             + (" and the hub-link R-copy test (N2)" if goal == 40 else "") + ".\n\n",
             "## Prediction\n", "*Written 2026-10-07 (card), before running on this period.*\n", pred + "\n\n",
             "## Result\n",
             "Structural precondition (`scheme/structure.py`; counted before any freeze time):\n\n",
             "| Unit | Readers | Delayed active readers (need ≥ 5) | Read within 2 active min | Median wall read delay (s) [95% CI] | Read at first call of day | Previous day reserved |\n",
             "| --- | --- | --- | --- | --- | --- | --- |\n"]
    for r in rows:
        lo, hi = r["share_2min_ci"]
        lines.append(f"| {r['unit']} | {r['n']} | {r['n_dar']} | {r['share_2min']:.2f} [{lo:.2f}, {hi:.2f}] | "
                     f"{r['read_delay_med_s']:.0f} [{r['read_delay_ci'][0]:.0f}, {r['read_delay_ci'][1]:.0f}] | "
                     f"{r['n_first_call']}/{r['n']} | {'yes' if r['prev_day_reserved'] else 'no'} |\n")
    lines.append("\nThe kickoff is posted about 1 min before the day window opens, so each agent reads it at boot. "
                 "The kill test (O1, O3) is untestable here. The outcome analysis stopped at the precondition; "
                 "P2, P4, P5 and the native predictions were not computed.\n")
    su = [u for u in syn if GOAL.get(u) == goal]
    for u in su:
        p = syn[u]
        lines.append(f"\nSynthetic on this skeleton ({u}, 500 runs per world): O1 power under W1 is "
                     f"{p['pass_rule_dar']['o1_power_W1']:.2f} on the card's sample and {p['pass_rule_all']['o1_power_W1']:.2f} "
                     f"on all readers (size under W2 {p['pass_rule_all']['o1_size_W2']:.2f}). O3 power under W2 is "
                     f"{p['pass_rule_all']['o3_power_W2']:.2f}. The card's pass rule is not met.\n")
    lines += ["\n## Scorecard (period-specific axes)\n",
              "F (identifiability): 0 here; the read and clock alignments coincide at this read-delay spread.\n",
              "\n## Notes\n", "- 2026-10-07: round 1; data in `data/processed/H136-freeze-at-first-kickoff-read/structure/`.\n"]
    if any(r["prev_day_reserved"] for r in rows):
        lines.append("- The previous calendar day is reserved, so the active-before flag cannot be set (counted false). "
                     "Without that condition the delayed-reader count is still below 5.\n")
    return "".join(lines)


def ne38_readme() -> str:
    return ("# H136 × NE38: Opus 5's role reassignment (2026-07-29)\n\n"
            "**Verdict:** n/a (excluded by the card's rule: the reassignment is not a readable message)\n"
            "**Role:** exploratory\n"
            "**Period:** #51 (non-reserved part) · one agent (Claude Opus 5) · single-agent descriptive native (N3).\n\n"
            "## Why this period\nA field change on one agent: the read of the reassignment against the first touch of "
            "the new role's repo.\n\n"
            "## Prediction\n*Written 2026-10-07 (card).* N3 is descriptive (one agent); no prediction. "
            "NE38 is kept only if its reassignment is a readable message.\n\n"
            "## Result\nDQ6 `ground_truth_labels`: the new role row (valid from 2026-07-29 16:51 UTC) cites `agent_goals`, "
            "not a chat message. The ledger cannot time its read, so NE38 is excluded. No freeze time was computed.\n\n"
            "## Scorecard (period-specific axes)\nNone informed.\n\n"
            "## Notes\n- 2026-10-07: round 1 structural check only.\n")


def main():
    rng = np.random.default_rng(SEED)
    U = json.loads((L.OUTD / "structure/units.json").read_text())
    R = pl.read_parquet(L.OUTD / "structure/readers.parquet")
    syn = json.loads((L.OUTD / "synthetic/synthetic.json").read_text())["units"]
    S = unit_stats(R, U["units"], rng)
    res = {"built_at": dt.datetime.now(dt.timezone.utc).isoformat(), "git_commit": git_commit(),
           "precondition": {"n_units": len(S), "n_pass": sum(s["passes"] for s in S),
                            "max_dar": max(s["n_dar"] for s in S), "n_readers": int(R.height),
                            "n_within_2min": int((R["D_r_min"] < 2).sum()),
                            "wall_delay_median_s": float(R["D_r_wall_min"].median() * 60),
                            "wall_delay_q90_s": float(R["D_r_wall_min"].quantile(0.9) * 60),
                            "n_read_first_call": int(R["read_is_first_call"].sum()),
                            "n_calls_between_tk_tr": int(R["n_calls_between"].sum())},
           "kill": "untestable (S0 failed; no freeze time computed)", "units": S}
    (L.OUTD / "results").mkdir(exist_ok=True)
    (L.OUTD / "results/round1.json").write_text(json.dumps(res, indent=1, default=str))
    print(res["precondition"])
    if "--no-estimates" not in sys.argv:
        print("estimates rows:", estimates(S))
    if "--no-readmes" not in sys.argv:
        gp = HERE / "goalperiod-subhypotheses"
        for g in sorted({s["goal_no"] for s in S}):
            d = gp / f"G{g:02d}"
            d.mkdir(exist_ok=True)
            (d / "README.md").write_text(readme(g, [s for s in S if s["goal_no"] == g], syn))
        (gp / "NE38").mkdir(exist_ok=True)
        (gp / "NE38/README.md").write_text(ne38_readme())


if __name__ == "__main__":
    main()
