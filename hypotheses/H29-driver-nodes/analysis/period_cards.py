"""Write goalperiod-subhypotheses/G<NN>/README.md for H29.

  uv run python hypotheses/H29-driver-nodes/analysis/period_cards.py --pre    # predictions only (before the run)
  uv run python hypotheses/H29-driver-nodes/analysis/period_cards.py          # predictions + results from explore.py

The prediction text below was written 2026-10-04 ~02:25 UTC, before explore.py had been run on any period, and is
never edited afterwards (results are appended in separate sections).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h29lib as L  # noqa: E402

GP = L.HYP / "goalperiod-subhypotheses"
PRED_DATE = "2026-10-04 ~02:25 UTC"

PERIODS = {
    "G37": dict(title="Pick your own goal!", dates="2026-03-30 → 2026-04-01", regime="III", mode="F", rooms="#best / #rest",
                role="exploratory (descriptive: 3 days)", why="Free week at the start of regime III; two rooms. Too short "
                "for split halves; included to show what three days give.",
                pred="P1: κ CI includes 0 (2.4k visible rows; low power). P4: structural N_D (self-loops) = root SCCs ≈ 2 "
                "(rooms). P5/P6: split halves of 2 + 1 days; no reliability expected (|ρ| < 0.4). P7b: the top driver is in "
                "the larger room (#rest)."),
    "G38": dict(title="Choose a charity and raise as much money as you can for it", dates="2026-04-02 → 2026-04-24",
                regime="III", mode="C", rooms="#best (~4) / #rest (~10); joins 04-17, 04-22",
                role="exploratory (counted; the largest two-room unit)",
                why="17 days of a shared objective in two rooms: the best-powered unit of the two-room era. H18 and H22 "
                "both found their clearest two-room signals here.",
                pred="P1: κ > 0 with CI excluding 0 (credence 0.6). P2: invisible-placebo contamination ≥ 50% of the "
                "field-corrected pull. P3: net pull falls with k (slope < 0). P4: N_D (self-loops) = root SCCs ≈ 2; LSB "
                "drivers not split-half stable (Jaccard < 0.3). P5: split-half Spearman of D_k ≥ 0.4. P6: cross-fitted "
                "ρ(D_k, H_k) > 0. P7b: top driver in #rest (larger room). P7c: per-recipient pull higher in #best. P9: "
                "15 named human messages: descriptive only."),
    "G39": dict(title="Build your own interactive world!", dates="2026-04-27 → 2026-05-01", regime="III", mode="I",
                rooms="#best / #rest (reshuffled 04-27)", role="exploratory (counted)",
                why="Individual-objective week; few messages (5k visible rows). A low-coupling contrast.",
                pred="P1: κ CI includes 0 (credence of a pass 0.35; individual objectives, low volume). P5: split-half "
                "< 0.4 (5 days). P6: ρ ≈ 0. P7b: top driver in the larger room."),
    "G40": dict(title="Connect your worlds into a 3D universe!", dates="2026-05-04 → 2026-05-08", regime="III", mode="C",
                rooms="merged into #universe-coordination (one room)", role="exploratory (counted)",
                why="Shared objective in one merged room (16.9k visible rows). H12 found its strongest collective mode "
                "in #40, partly self-repetition.",
                pred="P1: κ > 0 (credence 0.5). P4: one room → N_D (self-loops) = 1. P5: split-half ≥ 0.2 (5 days). "
                "P6: ρ > 0. P7b: n/a (one room)."),
    "G41": dict(title="Perform novel research!", dates="2026-05-11 → 2026-05-15", regime="III", mode="I",
                rooms="#best / #rest (split back 05-11)", role="exploratory (counted)",
                why="Individual research in two rooms with the same task (H01's exception: no room field). 14.3k "
                "visible rows.",
                pred="P1: κ > 0 (credence 0.45). P5: split-half ≥ 0.2. P6: ρ > 0 (weak). P7b: top driver in the larger "
                "room. P7c: pull higher in the smaller room."),
    "G42": dict(title="Run your own Youtube channel!", dates="2026-05-18 → 2026-05-22", regime="III", mode="I",
                rooms="#best / #rest", role="exploratory (counted)",
                why="Individual objective, moderate volume (6.5k visible rows).",
                pred="P1: κ CI includes 0 (pass credence 0.35). P5: split-half < 0.4. P6: ρ ≈ 0. P7b: larger room."),
    "G44": dict(title="Finetune your leader!", dates="2026-05-26 → 2026-05-29", regime="III", mode="C",
                rooms="#best / #rest; Opus 4.8 and the temporary fine-tuned leader join 05-28 (NE31)",
                role="exploratory (counted)",
                why="Only #best had the shared objective; the most human messages of regime III before the holdout (59; "
                "19 named). The temporary leader (agent 28) is present on 2 days.",
                pred="P1: κ > 0 (credence 0.5). P5: split-half < 0.4 (4 days). P6: ρ > 0 weak. P7b: top driver in the "
                "larger room. P9: human named-vs-bystander pull, descriptive (19 named messages). The temporary leader "
                "is not predicted to be a top driver (2 days, 27 messages; H23 found no transmission of plans)."),
    "G51a": dict(title="Each agent: Maximize your assigned goal! (roles start)", dates="2026-07-06 → 2026-07-08",
                 regime="III", mode="P", rooms="#general", role="exploratory (descriptive: 3 days)",
                 why="First three days of private roles; one room of 21; heavy volume (69k visible rows).",
                 pred="P1: κ > 0 (credence 0.6; volume). P4: one room → N_D (self-loops) = 1. P5/P6: 2 + 1 days, not "
                 "counted."),
    "G51b": dict(title="Each agent: Maximize your assigned goal!", dates="2026-07-09 → 2026-08-04", regime="III",
                 mode="P", rooms="#general (isolated GPT-5.6 rooms 07-09/10)", role="exploratory (counted)",
                 why="19 days, 27 agents, 319k visible rows: the best-powered unit overall, and the large-N end of the "
                 "scaling test.",
                 pred="P1: κ > 0 with CI excluding 0 (credence 0.7). P3: slope < 0. P5: split-half ≥ 0.4. P6: ρ > 0, "
                 "pooled with the rest ≥ 0.3. P8: E* at N = 27 above the two-room-era E* by ≈ (27/14)^2 ≈ 3.7 (η = 2)."),
    "G51c": dict(title="Each agent: Maximize your assigned goal! (#focus)", dates="2026-08-05 → 2026-08-24",
                 regime="III", mode="P", rooms="#general + #focus (2 agents moved)", role="exploratory (counted)",
                 why="14 days with a two-agent side room: the cleanest small-vs-large room contrast for HH110's 'small "
                 "rooms'.",
                 pred="P1: κ > 0 (credence 0.65). P5: split-half ≥ 0.4. P7b: the top driver is in #general, not #focus "
                 "(a two-agent room holds < 10% of the swarm). P7c: per-recipient pull is higher in #focus."),
    "G51d": dict(title="Each agent: Maximize your assigned goal! (after #focus)", dates="2026-08-25 → 2026-09-02",
                 regime="III", mode="P", rooms="#general", role="exploratory (counted)",
                 why="7 days, 29 agents, one room.",
                 pred="P1: κ > 0 (credence 0.6). P5: split-half ≥ 0.2. P6: ρ > 0."),
    "G51e": dict(title="Each agent: Maximize your assigned goal! (NE33 joins)", dates="2026-09-03 → 2026-09-04",
                 regime="III", mode="P", rooms="#general", role="exploratory (descriptive: 2 days)",
                 why="Two days after a batch join of three agents; the holdout tail starts 09-07.",
                 pred="P1: κ > 0 (credence 0.5). No split-half statistics (1 + 1 days)."),
}


def render(name: str, info: dict, res: dict | None) -> str:
    unit_meta = json.loads((L.OUT / name / "meta.json").read_text()) if (L.OUT / name / "meta.json").exists() else {}
    n = unit_meta.get("n_agents", "?")
    nd = unit_meta.get("n_days", "?")
    verdict = res.get("verdict", "pending") if res else "pending"
    s = [f"# H29 × {name}: {info['title']} ({info['dates']})", "",
         f"**Verdict:** {verdict}",
         f"**Role:** {info['role']}",
         f"**Period:** regime {info['regime']} · mode {info['mode']} · {n} recipients in the network · {info['rooms']} · "
         f"{nd} non-holdout days.", "",
         "## Why this period", info["why"], "",
         "## Prediction", f"*Written {PRED_DATE}, before running on this period.* Card predictions P1–P10 as they apply "
         "here:", "", info["pred"], ""]
    if res:
        s += ["## Result", res["table"], "", res.get("figure", ""), "",
              "## Scorecard (period-specific axes)", res.get("scorecard", ""), "",
              "## Notes", res.get("notes", "")]
    else:
        s += ["## Result", "Pending (explore.py not yet run on this period).", "",
              "## Scorecard (period-specific axes)", "Pending.", "", "## Notes",
              f"- {PRED_DATE}: folder created with the dated prediction."]
    return "\n".join(s) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pre", action="store_true")
    a = ap.parse_args()
    summ = None if a.pre else json.loads((L.OUT / "period_results.json").read_text())
    for name, info in PERIODS.items():
        d = GP / name
        (d / "figures").mkdir(parents=True, exist_ok=True)
        res = None if summ is None else summ.get(name)
        (d / "README.md").write_text(render(name, info, res))
    print(f"wrote {len(PERIODS)} period cards ({'pre' if a.pre else 'with results'})")


if __name__ == "__main__":
    main()
