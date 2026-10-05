"""Append (or replace) a "Round 2" section in each H69 period README from results_r2.json (idempotent).

  uv run python hypotheses/H69-loops-context-fixed-points/analysis/write_period_cards_r2.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
D = ROOT / "data/processed/H69-loops-context-fixed-points"
GP = HERE.parent / "goalperiod-subhypotheses"
MARK = "\n## Round 2 (2026-10-05)\n"


def ci(t, exp=False):
    if not t or t.get("b") is None or not math.isfinite(t["b"]) or not math.isfinite(t.get("se", float("nan"))):
        return "n/a"
    b, se = t["b"], t["se"]
    lo, hi = b - 1.96 * se, b + 1.96 * se
    if exp:
        return f"{math.exp(b):.2f} [{math.exp(lo):.2f}, {math.exp(hi):.2f}]"
    return f"{b:+.2f} [{lo:+.2f}, {hi:+.2f}]"


def mh(m):
    if not m or m.get("log_or") is None or not math.isfinite(m["log_or"]):
        return "n/a"
    lo, hi = m.get("lo"), m.get("hi")
    if lo is None or not (math.isfinite(lo) and math.isfinite(hi)):
        return f"{math.exp(m['log_or']):.2f} (no interval)"
    return f"{math.exp(m['log_or']):.2f} [{math.exp(lo):.2f}, {math.exp(hi):.2f}]"


def section(p, o, pooled):
    sc = o["scorable"]
    r1 = o.get("r1_all") or {}
    r1n = o.get("r1_all_noU") or {}
    ex = o.get("r2_exit_dose") or {}
    r3 = o.get("r3") or {}
    comp = (o.get("r3_composition") or {}).get("copies") or {}
    ph = (o.get("posthoc_exit_mem") or {}).get("terms") or {}
    pw = lambda v: "n/a" if v is None else f"{v:.2f}"  # noqa: E731
    lines = [MARK.strip(), "",
             "*Predictions, synthetic validation and amendments R2-A1–A4 are in the card (\"Round 2\"), written before "
             "any round-2 statistic. Exploratory, non-reserved days. Numbers: `data/processed/H69-loops-context-fixed-points/"
             f"{p}/results_r2.json`.*", "",
             "| Statistic | Value | Read? |", "| --- | --- | --- |",
             f"| R1 onset per log(1 + own tool tokens/1000), all labs | {ci(r1.get('U_k'))} (n {r1.get('n', 'n/a')}) | "
             f"{'scorable' if sc.get('R1_all') else 'descriptive'} (power {pw(sc.get('R1_power_all'))}) |",
             f"| R1 onset per log(1 + own statements), with tokens · without | {ci(r1.get('o_ctx'))} · {ci(r1n.get('o_ctx'))} | "
             f"{'scorable' if sc.get('R1_all') else 'descriptive'} |",
             f"| R1 fill (`ctx_pos`) with tokens · without | {ci(r1.get('ctx_pos'))} · {ci(r1n.get('ctx_pos'))} | descriptive |",
             f"| R2a exit: erasure × own tokens removed (per log unit) | {ci(ex.get('dose_c'))} (erasures {ex.get('n_erasure', 'n/a')}) | "
             f"{'read' if p in ('G38', 'G51') else 'pooled only'} (power {pw(sc.get('R2_power'))}) |",
             f"| R2a exit OR, forced erasure at the mean dose | {ci(ex.get('forced_between'), exp=True)} | — |",
             f"| R2b loop statements after a 200-event cap hit | {o['r2_cap'].get('n_cap', 0)} of {o['r2_cap'].get('n_loop', 0)} | inconclusive |",
             f"| R3 erased source in memory vs not (MH OR) | {mh(r3.get('P1'))} ({r3.get('n_copies', 'n/a')} erased near-copies) | "
             f"{'scorable' if sc.get('R3') else 'not scorable'}; size {pw(sc.get('R3_size'))}, power {pw(sc.get('R3_power'))} |",
             f"| R3 newly written into memory vs not · salience-stratified | {mh(r3.get('P2_new'))} · {mh(r3.get('P2_strat'))} | inconclusive by design |",
             f"| share of cross-erasure near-copies with the source in memory (already before the source) | "
             f"{comp.get('in_mem', float('nan')):.3f} ({comp.get('old_mem', float('nan')):.3f}) | descriptive |"
             if comp.get("n") else "| share of cross-erasure near-copies with the source in memory | n/a | — |"]
    if ph:
        lines.append(f"| post hoc: exit OR after erasure, looping text not in memory · × in memory | "
                     f"{ci(ph.get('erased'), exp=True)} · {ci(ph.get('erased_inmem'), exp=True)} | post hoc |")
    lines += ["", "**Verdict:** unchanged (no round-2 kill rule changes a period verdict)."]
    return "\n".join(lines) + "\n"


def main():
    r = json.loads((D / "results_r2.json").read_text())
    per, pooled = r["periods"], r["pooled"]
    for p, o in per.items():
        f = GP / p / "README.md"
        txt = f.read_text()
        if MARK in txt:
            txt = txt[:txt.index(MARK)]
        f.write_text(txt.rstrip("\n") + "\n" + MARK + section(p, o, pooled).split("\n", 1)[1])
    # NE41: the erasure-dose and post hoc pools
    f = GP / "NE41" / "README.md"
    txt = f.read_text()
    if MARK in txt:
        txt = txt[:txt.index(MARK)]

    def pci(k, exp=False):
        q = pooled[k]
        if not q.get("k"):
            return "n/a"
        if exp:
            return f"{math.exp(q['mean']):.2f} [{math.exp(q['lo']):.2f}, {math.exp(q['hi']):.2f}]"
        return f"{q['mean']:+.2f} [{q['lo']:+.2f}, {q['hi']:+.2f}]"
    body = (
        "\n*Card \"Round 2\" (R2a). Pools over G38, G40, G41, G51 (random effects).*\n\n"
        "| Statistic | Value |\n| --- | --- |\n"
        f"| exit: erasure × own tokens removed (per log unit) | {pci('R2_exit_dose')} (OR per log unit {pci('R2_exit_dose', True)}) |\n"
        f"| onset: erasure × own tokens removed | {pci('R2_onset_dose')} |\n"
        f"| exit OR, forced erasure at the mean dose | {pci('R2_exit_forced', True)} |\n"
        f"| post hoc: exit OR after erasure, looping text not in memory | {pci('POSTHOC_exit_erased', True)} (G38, G39, G40, G51) |\n"
        f"| post hoc: × looping text in memory | {pci('POSTHOC_exit_erased_inmem', True)} |\n\n"
        "**Reading:** R2-P1 passed: the erasure acts as a step; a dose slope of 0.7 per log unit is excluded (synthetic "
        "power 1.00). Post hoc, an erasure helps less when the looping text is in the agent's memory.\n\n"
        "**Verdict:** unchanged (mixed).\n")
    f.write_text(txt.rstrip("\n") + "\n" + MARK + body)
    print("period READMEs updated")


if __name__ == "__main__":
    main()
