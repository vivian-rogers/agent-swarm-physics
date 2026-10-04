"""Fill the Result / Verdict / Scorecard / Notes sections of the H26 G folders from summary_units.json and the explore
JSONs. The Prediction section is never touched. Called by write_period_folders.py --results."""
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
HYP = HERE.parent
ROOT = HYP.parents[1]
D = ROOT / "data/processed/H26-content-near-critical"

# Hand-written after looking at the numbers (2026-10-04 ~03:10 UTC): prediction check and reading per period.
COMMENT = {
    35: ("mixed", "Predicted g_ex,c ≥ 0.5 [0.65]: **yes** (0.80). Verdict mixed [0.6]: **yes**. w30 content > activity by > 0.15 [0.5]: **no** (Δg 0.12). "
         "The largest content room excess of all units, with almost no cross-room content co-fluctuation (ρ_c 0.03). But activity is just as room-structured once its global component (ρ_c 0.86) is removed, and the rooms worked on different forks, a room field the projections cannot remove."),
    36: ("mixed", "Predicted g_ex,c 0.3–0.6 [0.6]: **yes** (0.53). Mixed or failed [0.75]: **yes** (mixed). Activity's day-level room excess is strongly negative (clipped −1; 4 days), so Δg is large but uninformative; at w30 activity exceeds content (Δg −0.21)."),
    37: ("failed", "Seen during debugging (Amendment 2). Predicted g_ex,c < 0.5 [0.75]: **yes** (0.15); failed [0.7]: **yes**. Within-room and cross-room content co-fluctuation are equal (ρ_w 0.23, ρ_c 0.20): the free week's day-to-day content co-movement is global. L3 deflates H01's 0.76 to 0.15, as designed. At w30 the room excess is 0.35, similar to activity (0.29); talk is higher (0.67)."),
    38: ("mixed", "Predicted 38a ≥ 0.5 [0.55]: **yes** (0.65). 38b < 0.5 [0.65]: **no** (0.55). 38c < 0.5 [0.65]: **yes** (0.40). Dedupe lowers content gains by ≥ 0.05 [0.5]: **no** (38a unchanged; 38b *rises* 0.49 → 0.55). Verdicts predicted mixed/failed/failed; observed mixed ×3 because activity's day-level room excess is noisy (CIs reach −1). "
         "At w30 content and activity are tied in 38a (0.59 vs 0.59), activity is higher in 38c (0.62 vs 0.45), talk is higher than content in all three. The rooms had different instructions (a room field), so content's room excess here is not evidence for coupling."),
    39: ("mixed", "Predicted g_ex,c < 0.5 [0.7]: **yes** (0.45). Failed [0.65]: **no**, mixed, because activity's room excess is strongly negative (cross-room activity co-moves more than within-room; ρ_c 0.31 > ρ_w 0.19 at w30), which makes Δg large. Talk room excess (0.80 at w30) exceeds content (0.29)."),
    40: ("descriptive", "Not two-room by the pre-registered rule (rooms merged mid-week; < 30% of slots with two rooms of ≥ 2 agents), so descriptive. Predicted g_ex,c 0.3–0.6: not applicable. Whole-room (L2) gains: content 0.75, activity 0.90, talk 0.89 at day level; content is the *lowest* channel at both resolutions."),
    41: ("mixed", "Predicted g_ex,c ≥ 0.5 [0.7]: **yes** (0.77, CI 0.72–0.80, N2 p 0.005). w30 content > activity by > 0.15 [0.55]: **yes** (activity's w30 room excess is negative: ρ_c 0.63 > ρ_w 0.58). Mixed [0.55]: **yes** (day Δg CI −0.03…). "
         "The best case for H26: same instructions in both rooms, so room fields are least plausible, and content's room excess is large and tight. But activity's whole-swarm co-fluctuation is larger than content's (ρ_w 0.83 vs 0.45 at day level), and it is global."),
    42: ("failed", "Predicted g_ex,c < 0.5 [0.75] and < 0.3 [0.6]: **yes** (0.13); failed [0.7]: **yes**. Content co-fluctuation is mostly global (ρ_w 0.14 vs ρ_c 0.12): L3 deflates H01's 0.87 to 0.13. Activity's room excess (0.60 at w30) exceeds content's (0.28)."),
    44: ("mixed", "Predicted g_ex,c ≥ 0.5 [0.6]: **yes** (0.76). L2 lowers the room gain more than anywhere else [0.5]: **no** (L2 *raises* it, 0.72 → 0.77; the 59 human messages explain nothing beyond their null). Mixed [0.6]: **yes**. At w30 activity (0.81) and talk (0.78) exceed content (0.72): Δg_ca −0.09 [−0.16, 0.14]. A per-room goal override (room field) is present."),
    51: ("mixed", "51c (#focus): predicted g_ex,c < 0.5 [0.6]: **no** (0.54, but N2 p 0.18 and CI −0.03…0.71); failed [0.55]: **no** (mixed; activity room excess −inf). Single-room units: P6 g_c ≥ g_a at day level in most sub-units [0.55]: **no, the reverse in 4/4** (activity 0.92–0.95 vs content 0.25–0.65; Δg −0.27 to −0.50, CIs below 0 in 51a, 51b, 51d). "
         "In the big single room, activity co-fluctuates across the whole swarm far more than content does. These L2 values are upper bounds for both channels (no cross-room baseline); the synthetic shows a global drive alone gives ≈ 0.75 at N = 24, T = 15."),
}


VTEXT = {
    35: "content room excess 0.80 (N2 p 0.01), but activity nearly matches it at w30 once its global part is removed (gap +0.12)",
    36: "content 0.53; activity excess noisy (4 days); at w30 activity exceeds content (gap -0.21)",
    37: "content co-fluctuation is global (within-room 0.23, cross-room 0.20): L3 only 0.15; seen during debugging",
    38: "content 0.65, 0.55, 0.40 in 38a, b, c (N2 p up to 0.03); at w30 activity ties or exceeds content; talk higher",
    39: "content 0.45; activity room excess negative (cross-room above within), which inflates the gap; talk above content",
    40: "rooms merged (not two-room by rule); whole-room gains: content 0.75, activity 0.90",
    41: "best case: content 0.77 [0.72, 0.80], N2 p 0.005; activity's whole-swarm co-fluctuation is larger but global",
    42: "content co-fluctuation is global (within-room 0.14, cross-room 0.12): L3 0.13; activity excess higher",
    44: "content 0.76; at w30 activity 0.81 and talk 0.78 exceed content (gap -0.09)",
    51: "one big room: activity 0.92 to 0.95 far above content 0.25 to 0.65 (L2 upper bounds); #focus content 0.54 (N2 p 0.18)",
}


def f(x, nd=2):
    if x is None:
        return "–"
    if isinstance(x, str):
        return x
    if x == float("-inf"):
        return "−∞ (→ −1)"
    return f"{max(-1.0, min(1.0, x)):.{nd}f}"


def fci(c):
    if not c or c[0] is None:
        return ""
    return f" [{max(-1, c[0]):.2f}, {max(-1, c[1]):.2f}]"


def results(PERIODS):
    rows = {r["unit"]: r for r in json.loads((D / "summary_units.json").read_text())}
    for g, p in PERIODS.items():
        dpath = HYP / "goalperiod-subhypotheses" / f"G{g:02d}" / "README.md"
        txt = dpath.read_text()
        verdict, comment = COMMENT[g]
        lines = ["| unit | days | H01 P9 βJ₀/n | content L0 g_all | **content L3 g_ex (day)** | N2 p | activity L3 (day) | talk L3 (day) | Δg_ca (day) | content w30 | activity w30 | talk w30 | Δg_ca (w30) | ρ_c activity / content (w30) | exo share (excess) | verdict |",
                 "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for u in p["units"]:
            r = rows.get(u)
            if r is None:
                continue
            ex = json.loads((D / f"G{g:02d}/{u}.json").read_text())
            l0 = (ex["c_day_dedup"].get("L0") or {}).get("g_all")
            lab = "L3" if r["two_room"] else "L2 (one room)"
            lines.append(
                f"| {u} | {r['n_days']} | {f(r['h01_p9_raw'])} | {f(l0)} | {f(r['c_day_g'])}{fci(r['c_day_g_ci'])} {'' if r['two_room'] else '(L2)'} | "
                f"{f(r['p_N2_content_day'], 3) if r['p_N2_content_day'] is not None else '–'} | {f(r['a_day_g'])}{fci(r['a_day_g_ci'])} | {f(r['k_day_g'])} | "
                f"{'–' if r['dg_ca_day'] is None else format(r['dg_ca_day'], '+.2f')}{fci(r['dg_ca_day_ci'])} | "
                f"{f(r['c_w30_g'])}{fci(r['c_w30_g_ci'])} | {f(r['a_w30_g'])}{fci(r['a_w30_g_ci'])} | {f(r['k_w30_g'])} | "
                f"{'–' if r['dg_ca_w30'] is None else format(r['dg_ca_w30'], '+.2f')}{fci(r['dg_ca_w30_ci'])} | {f(r['a_w30_rho_c'])} / {f(r['c_w30_rho_c'])} | "
                f"{'–' if r['drive_share_day_excess'] is None else format(r['drive_share_day_excess'], '+.3f')} | {r['verdict']} ({lab}) |")
        table = "\n".join(lines)
        res = f"""Values are loop gains g = 1 − 1/VR (clipped at −1), deduped content, outage windows dropped. Two-room units: L3 room excess. One-room units: L2 (upper bound). 95% CIs from a joint day bootstrap (400 draws, the same days for every channel). With 3–8 days these CIs under-cover; synthetic coverage is 0.6–0.9. Δg_ca = content − activity. Data: `data/processed/H26-content-near-critical/G{g:02d}/`. Figure: [`figures/G{g:02d}_ladder.pdf`](figures/G{g:02d}_ladder.pdf).

{table}

**Prediction check and reading.** {comment}
"""
        txt = re.sub(r"\*\*Verdict:\*\* .*", f"**Verdict:** {verdict}: {VTEXT[g]}", txt, count=1)
        txt = re.sub(r"## Result\n.*?\n## Scorecard", "## Result\n" + res + "\n## Scorecard", txt, flags=re.S)
        sc = ("- **C (adequacy):** content room excess beats the room-permutation null (N2) where p < 0.05 above; activity and talk do too in several units. Neither channel's gain is tested against held-out days.\n"
              "- **D (unfitted):** not tested per period; the H26 signature (content gain ≥ 0.5 *and* > activity + 0.15, robustly) is judged pooled in the card.\n"
              "- **G (ground truth):** human/automated message directions explain no room-day variance beyond their null (exo share column).")
        txt = re.sub(r"## Scorecard \(period-specific axes\)\n.*?\n## Notes", "## Scorecard (period-specific axes)\n" + sc + "\n\n## Notes", txt, flags=re.S)
        if "results filled" not in txt:
            txt = txt.rstrip() + "\n- 2026-10-04: results filled from `analysis/summarize.py` (joint bootstrap) and `analysis/explore.py`.\n"
        dpath.write_text(txt)
        print(f"G{g:02d}: {verdict}")
