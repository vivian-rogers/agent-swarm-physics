"""Write / update the G<NN>/README.md cards for H18.

  uv run python hypotheses/H18-attention-dilution/analysis/write_period_cards.py predict   # before any real-data run
  uv run python hypotheses/H18-attention-dilution/analysis/write_period_cards.py results   # after fit_periods.py

`predict` writes the header, "Why this period" and the dated "Prediction" section, verdict pending. It refuses to
overwrite an existing card. `results` keeps everything up to the end of the Prediction section verbatim and replaces
the Result / Scorecard / Notes sections from data/processed/H18-attention-dilution/G<NN>/fits.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from periods import PERIODS, REGIME_I, TWO_ROOM, gname

HERE = Path(__file__).resolve().parent
HYP = HERE.parent
ROOT = HYP.parents[1]
DATA = ROOT / "data/processed/H18-attention-dilution"
PRED_DATE = "2026-10-03"

WHY = {
    24: "Regime I contrast after NE09 (chat visible during computer use), one room, N = 10, shared objective.",
    25: "Regime I contrast, one room, N = 10, shared objective (a museum built by many agents: lots of cross-talk).",
    26: "Regime I contrast; an election week, where agents address each other by name a lot (strong mention field).",
    27: "Regime I contrast, two-week competition (mode K): agents mostly work alone, so k is driven by others' reports.",
    30: "Regime I contrast, N = 12, the largest regime-I room; the nudger switches on inside (NE10), adding automated messages to k.",
    31: "Regime I contrast, free week with a farewell; roster changes inside.",
    35: "The NE15 split's first non-holdout week: #best (3 agents) and #rest (10) on the same days, same goal. The cleanest same-day room-size contrast in the data.",
    36: "Two rooms, and the regime II → III boundary (perma-computer-use) inside: first timer-PAUSE days.",
    37: "First regime-III week, free mode, two rooms; short (3 days).",
    38: "Longest two-room period (17 days): most power for β and the D2 wake design; roster grows by 2.",
    39: "Merge A-B-A, side A: two rooms just before the 05-04 merge.",
    40: "Merge A-B-A, side B: almost everyone in one room (#universe-coordination), so k per turn should rise for the merged agents.",
    41: "Merge A-B-A, side A': split back to the #39 partition.",
    42: "Two rooms, individual objectives; a join inside.",
    44: "Two rooms; #best fine-tunes a leader while #rest works on creative projects (different room activity levels on the same days).",
    51: "Largest N (21 → 29 on non-holdout days), 8 h days: the within-period size gradient for the J/N question, and the most data.",
}


def prediction_text(g: int) -> str:
    p = PERIODS[g]
    lines = [f"*Written {PRED_DATE}, before running on this period (and before any real-data run of H18).*", ""]
    lines.append("Card predictions as they apply here (D1 = talk-turn backlog, primary):")
    lines.append("- **P1:** β̂ (M_pow, agent×day propensities) > 0 with the day-bootstrap 95% CI excluding 0; expected size 0.5–1.2.")
    lines.append("- **P2:** M_inv or M_sat has the best within-day-block held-out log-likelihood among M_const, M_inv, M_sat, M_rec; if M_sat, k̂₀ < 3.")
    lines.append("- **P3:** Σ ≈ const: ε_S ∈ [−0.2, 0.5].")
    lines.append("- **P4:** e^γ ≥ 3 for messages that @-mention the recipient, with a flatter slope (β_M < β_other − 0.3) where ≥ 100 mention units.")
    lines.append("- **P10:** invisible (same-call) messages addressed at ≤ 1.5× the non-pending mention rate.")
    if p["regime"] in ("III", "II/III"):
        lines.append("- **P5 (D2 timer wakes):** β̂_D2 > 0 with CI excluding 0 if ≥ 200 D2 units; β̂_D2 within ±0.4 of β̂_D1.")
    if g in TWO_ROOM:
        lines.append("- **P6 (room size):** on the same days, per-pair uptake is higher in the smaller room by about k̄_large/k̄_small (within ×2); the room coefficient's CI includes 0 once k is in the model.")
    if g in (39, 40, 41):
        lines.append("- **P7 (merge A-B-A):** for the agents merged on 05-04, k̄ is higher and per-pair uptake lower in #40 than in #39 and #41; S per talk turn within ±30%. Scored in `../NE42/`.")
    if g in REGIME_I:
        lines.append("- **P8:** β̂ within ±0.3 of the pooled regime-III β̂ (scored across periods in the main card).")
    if g == 51:
        lines.append("- **P9 (segments at roster joins):** per-pair uptake p̄ falls as N rises, while the effective budget B̂ stays flat (|ρ| < 0.3).")
    lines.append("")
    lines.append("**Verdict rule (fixed now):** *supported* if P1 and P2 hold" +
                 (" and D2 does not contradict (β̂_D2 ≥ 0.2, or < 200 D2 units)" if p["regime"] in ("III", "II/III") else "") +
                 "; *failed* if β̂'s CI includes 0 or M_const is best; *mixed* otherwise (e.g. β̂ > 0 but M_rec best" +
                 (", or D2 contradicts D1" if p["regime"] in ("III", "II/III") else "") + "). Fewer than 300 scored units: *descriptive*.")
    return "\n".join(lines)


def header(g: int, verdict: str = "pending") -> str:
    p = PERIODS[g]
    d0, d1 = p["dates"]
    return (f"# H18 × {gname(g)}: {p['title']} ({d0} → {d1})\n\n"
            f"**Verdict:** {verdict}\n**Role:** exploratory\n"
            f"**Period:** regime {p['regime']} · mode {p['mode']} · N ≈ {p['N']} · {p['rooms']}. "
            f"Splits inside the period: {p['splits']}.\n")


def predict():
    for g in PERIODS:
        d = HYP / gname(g)
        (d / "figures").mkdir(parents=True, exist_ok=True)
        f = d / "README.md"
        if f.exists():
            print("exists, not overwritten:", f)
            continue
        txt = (header(g) + "\n## Why this period\n" + WHY[g] + "\n\n## Prediction\n" + prediction_text(g) +
               "\n\n## Result\n*Pending.*\n\n## Scorecard (period-specific axes)\n*Pending.*\n\n## Notes\n"
               f"- {PRED_DATE}: card created with the prediction, before any H18 real-data run.\n")
        f.write_text(txt)
        print("wrote", f)


def fmt_ci(v, lo, hi, nd=2):
    if v is None:
        return "—"
    s = f"{v:.{nd}f}"
    if lo is not None and hi is not None:
        s += f" [{lo:.{nd}f}, {hi:.{nd}f}]"
    return s


def results():
    from summarize_lib import period_verdict, result_section, scorecard_section, notes_section
    for g in PERIODS:
        f = HYP / gname(g) / "README.md"
        fj = DATA / gname(g) / "fits.json"
        if not f.exists() or not fj.exists():
            print("skip", g)
            continue
        fits = json.loads(fj.read_text())
        txt = f.read_text()
        head, _, rest = txt.partition("## Prediction\n")
        pred = rest.split("\n## Result\n")[0]
        verdict = period_verdict(g, fits)
        head = head.replace("**Verdict:** pending", f"**Verdict:** {verdict}")
        for v in ("supported", "failed", "mixed", "descriptive"):
            head = head.replace(f"**Verdict:** {v}\n", f"**Verdict:** {verdict}\n")
        old_notes = rest.split("\n## Notes\n")[1] if "\n## Notes\n" in rest else ""
        new = (head + "## Prediction\n" + pred + "\n## Result\n" + result_section(g, fits) +
               "\n## Scorecard (period-specific axes)\n" + scorecard_section(g, fits) +
               "\n## Notes\n" + notes_section(g, fits, old_notes))
        f.write_text(new)
        print("updated", f, verdict)


if __name__ == "__main__":
    {"predict": predict, "results": results}[sys.argv[1]]()
