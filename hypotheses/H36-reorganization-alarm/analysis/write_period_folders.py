"""Write H36's goal-period (G<NN>) and natural-experiment (NE<NN>) folders.

Phase `pred` (run before any statistic exists): header, why, dated prediction, verdict rule, empty result block.
Phase `result` (after analysis/evaluate.py): fills the <!-- RESULT --> block and the Verdict line from
data/processed/H36-reorganization-alarm/results.json, keeping the prediction text untouched.

Usage: uv run python hypotheses/H36-reorganization-alarm/analysis/write_period_folders.py pred|result
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h36lib as L  # noqa: E402

import polars as pl  # noqa: E402

GP = L.HYP / "goalperiod-subhypotheses"
GOAL_TABLE = L.ROOT / "hypotheses/hypohypotheses/goal-periods.md"
PRED_DATE = "2026-10-04 01:51 UTC"
MODE = {"C": "shared objective", "F": "free / none", "I": "each agent its own objective", "K": "competition",
        "M": "mixed", "A": "assigned roles"}

NE_DEFS = {
    "NE34": dict(title="goal changes (all non-holdout kickoffs, #2–#51)", refs=None,
                 scope="spans #2–#51 (35 non-holdout kickoffs; transitions as the object, exception c)",
                 why="The primary transition class: every goal kickoff whose day 0 is not held out.",
                 pred="The card's P1: the physics alarm (Z_phys ≥ 2.0) hits ≤ 40% of goal changes, window FAR ≈ 15–30%, "
                      "AUC(Z_phys, day 0) < 0.65 [0.65]; R1 (content centroid shift) AUC ≥ 0.8 and beats Z_phys [0.75]; "
                      "content members respond more than activity members [0.6]; hits peak on day 0/+1, not day −1 [0.7]. "
                      "Synthetic power (Amendment 1): a miss rules out S6-sized content reorganizations but is uninformative "
                      "about S1-sized activity ones.",
                 rule="Supported if hit rate ≥ 0.6, window FAR ≤ 0.25, AUC ≥ 0.70 with CI excluding 0.5, random-date p < 0.05 "
                      "and Monday-placebo FAR ≤ 0.25; failed if AUC ≤ 0.60 or random-date p > 0.10; mixed otherwise."),
    "NE15": dict(title="the #best/#rest split (2026-03-16, with goal #35)", refs=["NE15"],
                 scope="#34–#35 boundary (2026-03-16; day −1 is in held-out #34)",
                 why="The first real cut of the chat channel between established agents; coincides with the #35 kickoff.",
                 pred="P4 (descriptive): activity χ/I fall (Z_χ and Z_I ≤ −1 on day 0) [0.4]; the one-sided alarm does not fire [0.7]. "
                      "Day −1 (03-13) is held out, so only days 0 and +1 are scored.",
                 rule="Descriptive (n = 1, goal-confounded): report z per family on days 0..+3; verdict 'descriptive'."),
    "NE42": dict(title="merge into #universe-coordination (05-04) and split back (05-11)", refs=["NE42a", "NE42b"],
                 scope="#39–#41 (2026-05-04 merge with the #40 kickoff; 2026-05-11 split with the #41 kickoff)",
                 why="An A-B-A of room structure; both steps coincide with goal kickoffs.",
                 pred="P4 (descriptive): the merge raises activity χ/I (z ≥ 2 on day 0) [0.35]; the split lowers them (z ≤ −1) [0.4]. "
                      "If the merge alarms and the split does not, that is the sign pattern of a coupling change (S1 vs S2).",
                 rule="Descriptive (two goal-confounded events): verdict 'descriptive'; sign pattern reported."),
    "NE14": dict(title="regime II→III boundary (perma-computer-use, 2026-03-24)", refs=["NE14b"],
                 scope="inside #36 (2026-03-23 → 03-30); the NE14 rollout start (03-11) is in held-out #34",
                 why="The largest scaffold change in the data: discrete sessions replaced by continuous computer use + CONSOLIDATE.",
                 pred="P5: the alarm fires within ±1 day of 03-24 [0.6] (the activity grammar changes completely; expect the activity "
                      "members to carry it).",
                 rule="Supported if Z_phys ≥ 2.0 on any of days −1..+1; failed otherwise."),
    "NE17": dict(title="outreach approval (2026-04-14, inside #38)", refs=["NE17"],
                 scope="inside #38 (2026-04-02 → 04-27)",
                 why="A scaffold change that degrades one external action for outreach-heavy agents; mid-goal, no confound.",
                 pred="P5: no alarm (hit only at chance) [0.7]: a small-dose change to one tool.",
                 rule="Supported if Z_phys ≥ 2.0 on any of days −1..+1; failed otherwise."),
    "NE18": dict(title="history search returns verbatim segments (2026-04-20, inside #38)", refs=["NE18"],
                 scope="inside #38 (2026-04-02 → 04-27)",
                 why="A memory-access change for searchers; mid-goal, no confound.",
                 pred="P5: no alarm [0.7].",
                 rule="Supported if Z_phys ≥ 2.0 on any of days −1..+1; failed otherwise."),
    "NE41": dict(title="forced context erasure at the 41-turn cap (regime III), as a nuisance", refs=None,
                 scope="regime III, #37–#51 (non-holdout days)",
                 why="NE41 is per-agent and asynchronous (turn-level), so it is not a swarm transition at day resolution. "
                     "It is a candidate nuisance: days with more consolidations might look more 'reorganized'.",
                 pred="Consolidations per present agent per day do not predict Z_phys on regime-III placebo days (|Spearman ρ| < 0.2) [0.7].",
                 rule="Nuisance check: verdict 'n/a' (descriptive); pass if |ρ| < 0.2 or p > 0.05."),
}


def goal_catalog() -> dict:
    rows = {}
    for line in GOAL_TABLE.read_text().splitlines():
        m = re.match(r"^\|\s*(\d+)\s*\|\s*(\S+) → (\S+)\s*\|\s*([^|]*)\|\s*(\d+)\s*\|\s*([^|]*)\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*(\S+)\s*\|", line)
        if m and int(m.group(1)) not in rows:
            rows[int(m.group(1))] = dict(start=m.group(2), end=m.group(3), N=int(m.group(5)), reg=m.group(7), mode=m.group(9))
    titles = {}
    for m in re.finditer(r"^### (\d+) · (.+)$", GOAL_TABLE.read_text(), re.M):
        titles[int(m.group(1))] = m.group(2).strip()
    for g in rows:
        rows[g]["title"] = titles.get(g, "")
    return rows


def g_pred(g: int, meta: dict, n_days: int, has_kick: bool, inside: list[str]) -> str:
    lines = [f"# H36 × G{g:02d}: {meta['title']} ({meta['start']} → {meta['end']})", "",
             "**Verdict:** pending",
             "**Role:** exploratory (round 1, non-holdout)",
             f"**Period:** regime {meta['reg']} · mode {meta['mode']} ({MODE.get(meta['mode'], '?')}) · N = {meta['N']} at start · "
             f"{n_days} non-holdout active days" + (f" · events inside: {', '.join(inside)}" if inside else ""), "",
             "## Why this period",
             "Every non-holdout goal period contributes its kickoff (a T-goal transition, day 0 = its first active day) and its "
             "within-period placebo days (≥ 3 active days from any catalogued event) to H36's alarm evaluation. Transitions are the "
             "object (exception c); this folder reports the period's share of the evidence.", "",
             "## Prediction",
             f"*Written {PRED_DATE}, before computing any statistic on real data.* The card's predictions as they apply here "
             "(card: `../README.md`, incl. Amendments 0–1).", ""]
    if has_kick:
        lines += ["- **Kickoff (P1):** no physics alarm (Z_phys < 2.0 on days −1, 0, +1) [0.65]; if one fires, on day 0 or +1, "
                  "not day −1 (P8) [0.7]. R1 (content centroid shift) z ≥ 2 on day 0 or +1 [0.6]."]
    else:
        lines += ["- **Kickoff:** not scored (day 0 held out, or fewer than 5 baseline days)."]
    lines += ["- **Placebo days (P7):** per-day alarm rate ≤ 0.10 [0.7].", "",
              "**Period verdict rule:** supported if the kickoff window alarms and the placebo-day alarm rate is ≤ 0.10 (or there are "
              "no placebo days); mixed if the kickoff alarms but placebo FAR > 0.10; failed if the kickoff window (≥ 1 scored day) "
              "does not alarm; n/a if the kickoff is not scored.", "",
              "## Result", "<!-- RESULT -->", "(pending)", "<!-- /RESULT -->", ""]
    return "\n".join(lines)


def ne_pred(ne: str, d: dict) -> str:
    return "\n".join([f"# H36 × {ne}: {d['title']}", "", "**Verdict:** pending",
                      "**Role:** exploratory (round 1, non-holdout)", f"**Period:** {d['scope']}", "",
                      "## Why this test", d["why"], "",
                      "## Prediction", f"*Written {PRED_DATE}, before computing any statistic on real data.* {d['pred']}", "",
                      f"**Verdict rule:** {d['rule']}", "",
                      "## Result", "<!-- RESULT -->", "(pending)", "<!-- /RESULT -->", ""])


def phase_pred():
    cal = pl.read_parquet(L.SH / "calendar.parquet")
    nh = cal.filter(~pl.col("holdout") & (pl.col("goal_no") > 0))
    ev = pl.read_parquet(L.OUT / "events.parquet")
    cat = goal_catalog()
    for (g,), sub in nh.group_by(["goal_no"]):
        g = int(g)
        kick = ev.filter((pl.col("cls") == "goal") & (pl.col("ref") == f"#{g}") & ~pl.col("holdout0"))
        inside = ev.filter((pl.col("goal0") == g) & (pl.col("cls") != "goal") & ~pl.col("holdout0"))["ref"].to_list()
        d = GP / f"G{g:02d}"; d.mkdir(parents=True, exist_ok=True)
        f = d / "README.md"
        if f.exists() and "**Verdict:** pending" not in f.read_text():
            continue  # never overwrite a filled folder in pred phase
        f.write_text(g_pred(g, cat[g], sub.height, kick.height > 0 and g > 3, inside))
    for ne, dd in NE_DEFS.items():
        d = GP / ne; d.mkdir(parents=True, exist_ok=True)
        f = d / "README.md"
        if f.exists() and "**Verdict:** pending" not in f.read_text():
            continue
        f.write_text(ne_pred(ne, dd))
    print("prediction folders written")


def fill(path: Path, verdict: str, body: str):
    t = path.read_text()
    t = re.sub(r"^\*\*Verdict:\*\*.*$", f"**Verdict:** {verdict}", t, count=1, flags=re.M)
    t = re.sub(r"<!-- RESULT -->.*<!-- /RESULT -->", "<!-- RESULT -->\n" + body.replace("\\", "\\\\") + "\n<!-- /RESULT -->", t,
               count=1, flags=re.S)
    path.write_text(t)


# Prediction checks written after reading results.json (round 1, 2026-10-04); appended inside the RESULT block.
CHECKS = {'NE42': '**Prediction check:** the merge did **not** raise activity χ/I (Z_act −0.61 on day 0; predicted z ≥ 2 [0.35]); the split lowered activity (Z_act −3.0, predicted ≤ −1 [0.4]: held) but the combined score still alarmed on day +1 through content (Z_cont 3.15 on day 0) and R1 jumped at both steps (5.2, 9.0). The S1/S2 sign pattern of a coupling change is absent; both steps look like content field changes (they coincide with the #40 and #41 kickoffs).', 'NE18': '**Prediction check:** no alarm, as predicted (Z_phys 0.73 on day 0). As for NE17, the miss is expected.', 'NE17': "**Prediction check:** no alarm, as predicted (Z_phys −1.18 on day 0). The H36 verdict is 'failed' because the alarm missed a catalogued transition; the miss is the expected behavior for a small-dose tool change.", 'NE34': '**Prediction check:** P1 hit ≤ 40% held (0.30) and AUC came out slightly above the predicted < 0.65 (0.68); window FAR was lower than predicted (0.10 vs 0.15–0.30). R1 AUC ≥ 0.8 and beats Z_phys: held (0.95; difference −0.26, CI excludes 0). Content > activity: held (0.77 vs 0.55). Timing: 7 of 10 hits first fire on day 0/+1, 3 on day −1 (post hoc PH1: day −1 AUC 0.69 vs placebo, 0.68 vs Friday placebos; a weak end-of-goal signal, not predicted). Verdict by the pre-registered rule: **mixed** (hit rate below 0.6; not failed because AUC 0.68 and random-date p 0.03).', 'NE15': '**Prediction check:** activity χ/I fell on day 0 (Z_χ −0.78, Z_I −0.47; z ≤ −1 not reached) and the one-sided alarm did not fire, as predicted. With day −1 held out and one goal-confounded event, nothing more can be read.', 'NE41': '**Prediction check:** held by the pre-registered rule (p > 0.05), but ρ = −0.31 with n = 15 is underpowered; consolidations, if anything, go with *lower* scores.', 'NE14': '**Prediction check:** P5 predicted an alarm within ±1 day of 03-24 [0.6]: **failed**. Every family is near or below zero (Z_act −0.36, Z_cont −1.60). Likely reasons (post hoc): NE14 was rolled out by provider from 03-11 (held out), so 03-24 ends a gradual change rather than starting one; and the per-pair, surrogate-corrected statistics are designed to be invariant to the activity grammar.'}


def phase_result():
    R = json.loads((L.OUT / "results.json").read_text())
    for gkey, r in R["periods"].items():
        f = GP / gkey / "README.md"
        if f.exists():
            fill(f, r["verdict"], r["body"])
    for ne, r in R["ne"].items():
        f = GP / ne / "README.md"
        if f.exists():
            fill(f, r["verdict"], r["body"] + ("\n\n" + CHECKS[ne] if ne in CHECKS else ""))
    print("result folders filled")


if __name__ == "__main__":
    {"pred": phase_pred, "result": phase_result}[sys.argv[1]]()
