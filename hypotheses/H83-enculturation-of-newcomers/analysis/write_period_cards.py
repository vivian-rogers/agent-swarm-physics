"""Write H83's goal-period READMEs.

  --stage predict   writes each folder with its dated prediction and "Verdict: pending" (before any real-data run)
  --stage results   rewrites the folders keeping the prediction text verbatim and adding the result
                    (reads replication/replication.json and natives/natives.json)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h83lib as L  # noqa: E402

HYP = L.ROOT / "hypotheses/H83-enculturation-of-newcomers"
PRED_STAMP = "2026-10-04 20:34 UTC"

REPL = {  # folder -> joins (agent ids) for the templated replication
    "G04": [8], "G18": [13], "G19": [14], "G20": [15, 16], "G31": [21], "G35": [23], "G39": [26],
}
NATIVE = {"G10": [9, 10, 11], "G38": [24, 25], "G51": [35, 36, 37, 38, 39, 40]}

REPL_PRED = """*Written {stamp}, before running on this period. Templated replication prediction (layer 1), the same for every join.*
- **Observable:** the enculturation index ΔG (O1): the newcomer's change in mean statement cosine with the veterans' same-day centroid from window E (tenure days 2–4) to window L (8–14), minus the same change of the veterans observed on the same days. Vectors: DQ5 `style_resid_period` (bge primary, gte check), goal and kickoff span projected out.
- **Prediction:** the newcomer starts below the veterans (Ḡ_E < 0) and closes part of the gap (ΔG > 0). Where a family baseline exists, the family signature fades (ΔK < 0). Style: ΔS < 0.
- **Verdict rule (per join, templated):** supported if ΔG > 0 and Ḡ_E < 0; failed if ΔG ≤ 0; mixed otherwise. One join has no power on its own (synthetic null SD of a single join ≈ 0.05); the card-level test pools the joins.
- *Counts against:* ΔG ≤ 0 (the newcomer converges only as far as the field pulls everyone)."""

NAT_PRED = {
    "G10": """*Written {stamp}, before running on this period (Amendment A1.4).*
- **Why native:** NE27 is the only join that coincides with a goal start: GPT-5, Grok 4 and Claude Opus 4.1 join the four veterans on 2025-08-18, the first day of #10, so all seven agents get the same kickoff the same day.
- **N3 prediction:** the batch's window-E gap (tenure days 2–4, veterans' same-day centroid, kickoff span projected out) is negative, Ḡ_E < 0, with a day-bootstrap 95% CI below 0: the veterans carry a component beyond the shared kickoff that the newcomers lack. The batch's mean ΔG > 0 (they close part of it by days 8–14).
- *Counts against:* Ḡ_E ≥ 0 (with the same kickoff, the newcomers align with the village as well as the veterans do). Synthetic null SD of the batch gap: 0.036, so only a gap beyond about −0.06 can show.
- The three joins also enter the card-level replication.""",
    "G38": """*Written {stamp}, before running on this period (Amendment A1.6).*
- **Why native:** #38 has two rooms (#best, #rest) with at least two veterans each on 04-20 → 04-24, and two newcomers arrive (Claude Opus 4.7 on 04-17, Kimi K2.6 on 04-22). A newcomer reads only its own room (H05, H41).
- **N2 prediction:** R_new = mean over the newcomers' agent-days of [alignment with own-room veterans − alignment with the other room's veterans] is > 0, with a day-and-agent bootstrap 95% CI above 0: convergence follows the read population. Descriptive: R_new / R_vet (veterans' own-room preference on the same days).
- *Counts against:* R_new ≤ 0 (the newcomer aligns with the whole village alike: a field, not reading).
- Kimi K2.6 posts about 3 statements a day, so Opus 4.7 carries most of the statistic. Both joins also enter the card-level replication.""",
    "G51": """*Written {stamp}, before running on this period (Amendment A1.5).*
- **Why native:** NE32: on 2026-07-09 GPT-5.6 Sol, Terra and Luna each start alone in an isolated onboarding room (no veteran items read; checked in the DQ1 ledger) and merge into the village on 07-10. Every other newcomer reads veterans from its first day.
- **N1 prediction:** d1 = the triplet's tenure-day-1 gap (statement-pooled) − the mean day-1 gap of the other newcomers < 0 (reading on the day raises alignment), and d2 = the triplet's change from day 1 to days 2–6 − the other newcomers' same change > 0 (the triplet catches up after the merge). Bootstrap over the other newcomers.
- *Counts against:* d1 ≥ 0 and d2 ≤ 0. Synthetic null SD 0.10 for both, so only large effects can show; Sol and Terra post 4 and 8 statements on 07-09.
- Caveat: #51 agents hold private roles (an agent-specific field); the own role text is projected out with the kickoff span. The #51 joins (Sol, Terra, Luna, Grok 4.5, Kimi K3, Claude Opus 5) also enter the card-level replication.""",
}


def header(folder: str) -> str:
    g = int(folder[1:])
    pu = pl.read_parquet(L.SH / "period_units.parquet").filter((pl.col("goal_no") == g) & ~pl.col("holdout"))
    first, last = pu["first_day"].min(), pu["last_day"].max()
    regimes = "/".join(sorted(set(pu["regime"].to_list())))
    n = int(pu["n_agents"].max())
    units = ", ".join(pu["unit_id"].to_list())
    gp = pl.read_parquet(L.SH / "calendar.parquet").filter(pl.col("goal_no") == g)
    return f"# H83 × {folder}: newcomers joining goal period #{g} ({first} → {last})", \
        f"**Period:** regime {regimes} · up to {n} agents · units {units} · non-holdout days {pu['n_days'].sum()}."


def write_predict():
    newc = L.newcomers()
    for folder, joins in {**REPL, **NATIVE}.items():
        d = HYP / "goalperiod-subhypotheses" / folder
        (d / "figures").mkdir(parents=True, exist_ok=True)
        (d / "figures" / ".gitkeep").touch()
        title, per = header(folder)
        names = ", ".join(f"{n} ({j})" for a, n, j in newc.select("agent", "name", "join_day").iter_rows() if a in joins)
        role = "native" if folder in NATIVE else "replication"
        why = (NAT_PRED[folder].split("\n")[1].replace("- **Why native:** ", "") if role == "native"
               else "A replication point for the common estimator (layer 1): every eligible join gets the same statistic.")
        pred = NAT_PRED[folder] if role == "native" else REPL_PRED
        text = f"""{title}

**Verdict:** pending
**Role:** {role} (exploratory)
{per} Joins: {names}.

## Why this period
{why}

## Prediction
{pred.format(stamp=PRED_STAMP)}

## Result
Pending.
"""
        (d / "README.md").write_text(text)
    gnn = HYP / "goalperiod-subhypotheses" / "GNN"
    if gnn.exists():
        import shutil
        shutil.rmtree(gnn)
    print("wrote", len(REPL) + len(NATIVE), "folders")


def native_texts(n):
    b, g = n["bge"], n["gte"]
    out = {}
    x, y = b["NE27"], g["NE27"]
    out["G10"] = {"verdict": "mixed", "text": f"""**N3 (NE27, kickoff-matched start).**

| Statistic | bge | gte | Null (synthetic) |
| --- | --- | --- | --- |
| Batch gap Ḡ_E (days {', '.join(x['E_days'])}) | {x['gap_E']:+.3f} [{x['gap_E_ci'][0]:+.3f}, {x['gap_E_ci'][1]:+.3f}] | {y['gap_E']:+.3f} [{y['gap_E_ci'][0]:+.3f}, {y['gap_E_ci'][1]:+.3f}] | SD 0.036 |
| Batch mean ΔG | {x['dG_batch']:+.3f} | (card replication) | SD 0.04 |

- **Verdict: mixed (inconclusive by the A1.4 rule).** The bge gap is negative but its CI spans 0; the gte gap is positive (the prediction's "against" side). The batch's ΔG is negative (Opus 4.1 −0.08, GPT-5 −0.13, Grok 4 +0.10). With the same kickoff on the same day, the newcomers align with the four veterans about as well as the veterans align with each other.""",
        "scorecard": "- E (interventional): 0. The only kickoff-matched join shows no veteran-only component beyond the kickoff, at power ≈ 0.3."}
    x, y = b["G38"], g["G38"]
    out["G38"] = {"verdict": "supported", "text": f"""**N2 (two rooms, 04-20 → 04-24, both rooms with ≥ 2 veterans).**

| Statistic | bge | gte |
| --- | --- | --- |
| R_new (own-room minus other-room alignment, newcomers) | {x['R_new']:+.3f} [{x['R_new_ci'][0]:+.3f}, {x['R_new_ci'][1]:+.3f}] | {y['R_new']:+.3f} [{y['R_new_ci'][0]:+.3f}, {y['R_new_ci'][1]:+.3f}] |
| R_vet (veterans, same days) | {x['R_vet']:+.3f} | {y['R_vet']:+.3f} |
| R_new / R_vet | {x['ratio_new_vet']:.2f} | {y['ratio_new_vet']:.2f} |

- {x['n_new_agent_days']} newcomer agent-days ({x['n_stmts_new']['24']} statements by Opus 4.7, {x['n_stmts_new']['25']} by Kimi K2.6); {x['n_vet_agent_days']} veteran agent-days.
- **Verdict: supported.** From their first days the newcomers align with the veterans of the room they read, as strongly as the veterans do (ratio 1.1–1.2). Room alignment is acquired at once, not over two weeks: it is conversation shared through reading (plus the room's own topic), not a slow culture. A room-specific field beyond the projected room kickoff is not excluded.""",
        "scorecard": "- G (ground truth): 1. Room membership (structural) predicts which veterans a newcomer aligns with.\n- E: 1 (rooms route the convergence; no slow component seen)."}
    x, y = b["NE32"], g["NE32"]
    out["G51"] = {"verdict": "n/a", "text": f"""**N1 (NE32 isolated triplet): premise false.**
- The DQ1 ledger and `rooms_timeline` show that GPT-5.6 Sol, Terra and Luna left their isolated rooms (sol, terra, luna) for #general on 07-09 itself, about 1.5–2 h after joining (21:38–22:02 UTC). The rooms were deleted on 07-10. The triplet posted **no chat statement** while isolated and read {x['isolated_day_veteran_items']} veteran items on 07-09.
- So "tenure day 1 without veteran reads" does not exist, and N1 has no test. The rule's numbers, for the record: d1 = {x['d1']:+.3f} [{x['d1_ci'][0]:+.3f}, {x['d1_ci'][1]:+.3f}] (bge), {y['d1']:+.3f} [{y['d1_ci'][0]:+.3f}, {y['d1_ci'][1]:+.3f}] (gte); d2 = {x['d2']:+.3f} [{x['d2_ci'][0]:+.3f}, {x['d2_ci'][1]:+.3f}] (bge), {y['d2']:+.3f} [{y['d2_ci'][0]:+.3f}, {y['d2_ci'][1]:+.3f}] (gte). The two models disagree.
- **Catalog correction (for `natural-experiments.md`):** NE32's isolation lasted about 1.5–2 h on 07-09, not until 07-10.
- H89 (coordinator note) finds the #51 newcomers' content moving toward the veterans in bge (cos +0.26) but not in gte (−0.03): the same model dependence.""",
        "scorecard": "- E: n/a (the natural experiment did not happen as catalogued)."}
    return out


def write_results():
    rep = json.loads((L.DATA / "replication" / "replication.json").read_text())
    natj = json.loads((L.DATA / "natives" / "natives.json").read_text())
    nat = native_texts(natj)
    newc = L.newcomers()
    name = dict(zip(newc["agent"].to_list(), newc["name"].to_list()))
    for folder, joins in {**REPL, **NATIVE}.items():
        p = HYP / "goalperiod-subhypotheses" / folder / "README.md"
        old = p.read_text()
        pre = old.split("## Result")[0]
        lines = ["## Result", f"*Run {rep['run_at']} (`analysis/replication.py`, `analysis/natives.py`) → "
                 "`data/processed/H83-enculturation-of-newcomers/replication/replication.json`, `natives/natives.json`.*", "",
                 "| Join | Ḡ_E | ΔG (bge) | ΔG (gte) | ΔK | ΔS (style) | veteran items read, days 1–7 | templated |",
                 "| --- | --- | --- | --- | --- | --- | --- | --- |"]
        verdicts = []
        for a in joins:
            r = rep["joins"].get(str(a))
            if not r:
                lines.append(f"| {name[a]} | – | not eligible | | | | | n/a |")
                continue
            g = r["G"]; gg = r.get("G_gte") or {}
            v = "supported" if (g["delta"] > 0 and g["gap_E"] < 0) else ("failed" if g["delta"] <= 0 else "mixed")
            verdicts.append(v)
            k = r.get("K"); s_ = r.get("S")
            lines.append(f"| {name[a]} | {g['gap_E']:+.3f} | {g['delta']:+.3f} | "
                         f"{gg.get('delta', float('nan')):+.3f} | {('%+.3f' % k['delta']) if k else '–'} | "
                         f"{('%+.3f' % s_['delta']) if s_ else '–'} | {r.get('dose_vet_1_7', '–')} | {v} |")
        role = "native" if folder in NATIVE else "replication"
        if role == "replication":
            vv = verdicts[0] if len(set(verdicts)) == 1 else ("mixed" if verdicts else "n/a")
            lines += ["", f"- **Templated verdict:** {vv}. One join has no power alone; see the card for the pooled test."]
        else:
            nv = nat.get(folder, {})
            vv = nv.get("verdict", "pending")
            lines += ["", nv.get("text", "")]
        body = re.sub(r"\*\*Verdict:\*\* [^\n]*", f"**Verdict:** {vv}", pre, count=1)
        sc = ("\n## Scorecard (period-specific axes)\n- Replication point only (layer 1): informs C and I in the main card.\n"
              if role == "replication" else
              "\n## Scorecard (period-specific axes)\n" + nat.get(folder, {}).get("scorecard", "") + "\n")
        p.write_text(body + "\n".join(lines) + "\n" + sc)
    print("results written")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["predict", "results"], required=True)
    a = ap.parse_args()
    write_predict() if a.stage == "predict" else write_results()
