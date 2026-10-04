"""H01 round 1b: `**Verdict (1b):**` lines and a per-unit round-1b block in the round-1 period READMEs, plus the native
results (G12, NE42). Round-1 and round-2 lines are kept. Idempotent (<!-- R1B --> block, Verdict (1b) line replaced).

Reads r1b/compare.json (analysis/r1b_compare.py) and r1b/native.json (analysis/r1b_native.py).
Usage: uv run python hypotheses/H01-emergent-superagents-exist/analysis/r1b_period_folders.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h01common import OUT, HYP  # noqa: E402

GP = HYP / "goalperiod-subhypotheses"
UNITS = {"G08": ["8"], "G21": ["21"], "G35": ["35"], "G36": ["36b"], "G37": ["37"], "G38": ["38a", "38b", "38c"],
         "G39": ["39"], "G40": ["40"], "G41": ["41"], "G42": ["42"], "G44": ["44"], "G51": ["51a", "51b", "51c", "51d", "51e"]}
VERDICT = {
    "G08": "descriptive (unchanged; P4 still not as predicted)",
    "G21": "descriptive (unchanged)",
    "G35": "mixed (unchanged, both models)",
    "G36": "failed (unchanged)",
    "G37": "failed (unchanged)",
    "G38": "mixed (unchanged; corrected room fields move within−cross by < 0.03)",
    "G39": "mixed (unchanged)",
    "G40": "supported (P7) in both models; DiD gone after style residualization",
    "G41": "mixed (unchanged, both models)",
    "G42": "mixed (unchanged)",
    "G44": "mixed (unchanged)",
    "G51": "mixed (unchanged)",
}
COLS = [("r1", "round 1"), ("bge_restate", "1b bge"), ("gte_restate", "1b gte"), ("bge_restate_style", "1b bge style-resid"),
        ("gte_restate_style", "1b gte style-resid")]


def f(x, nd=3):
    if x is None:
        return "–"
    if isinstance(x, (list, tuple)):
        return "–" if x[0] is None else f"{x[0]:+.{nd}f} ± {x[1]:.{nd}f}"
    return f"{x:.{nd}f}"


def set_verdict(text, line):
    if "**Verdict (1b):**" in text:
        return re.sub(r"\*\*Verdict \(1b\):\*\*.*", line, text, count=1)
    return re.sub(r"(\*\*Verdict:\*\*[^\n]*\n)", r"\1" + line + "\n", text, count=1)


def set_block(text, body, header="## Round 1b (improved data, 2026-10-04)"):
    blk = f"<!-- R1B -->\n{body}\n<!-- /R1B -->"
    if "<!-- R1B -->" in text:
        return re.sub(r"<!-- R1B -->.*?<!-- /R1B -->", blk, text, flags=re.S)
    return text.rstrip() + f"\n\n{header}\n{blk}\n"


def main():
    C = json.loads((OUT / "r1b" / "compare.json").read_text())
    N = json.loads((OUT / "r1b" / "native.json").read_text())
    for g, units in UNITS.items():
        p = GP / g / "README.md"
        if not p.exists():
            continue
        rows = ["Round-1 statistics re-run on the corrected inputs (card: Round 1b): shared goal vectors, restatements "
                "removed (each model's own DQ5 flag, chat only), bge-small and gte-modernbert, and DQ5's style-residualized "
                "vectors (identity claims).", "",
                "| unit | statistic | " + " | ".join(lab for _, lab in COLS) + " |", "| --- | --- |" + " --- |" * len(COLS)]
        for u in units:
            def cell(key, sub=None, nd=3):
                out = []
                for t, _ in COLS:
                    d = C.get(t, {}).get(key, {}) or {}
                    v = d.get(u) if isinstance(d, dict) else None
                    if sub is not None and v is not None:
                        v = v[sub]
                    out.append(f(v, nd))
                return " | ".join(out)
            rows.append(f"| {u} | P1 room ΔH (median) | {cell('per_unit_P1')} |")
            rows.append(f"| {u} | P5 field R² | {cell('per_unit_r2', 0, 2)} |")
            rows.append(f"| {u} | P6 exposure slope | {cell('per_unit_slope', None, 3)} |")
            rows.append(f"| {u} | P6 within − cross | {cell('P6_wc')} |")
            rows.append(f"| {u} | within − cross, room fields removed | {cell('P6_wc_roomfield')} |")
            rows.append(f"| {u} | P9 βJ₀/n (upper bound) | {cell('per_unit_P9', None, 2)} |")
        rows += ["", "Style-residualized runs report P1/P2/P5–P7 only (goal fields are not defined in that space). "
                 "Data: `data/processed/H01-emergent-superagents-exist/r1b/<instrument>/explore.json`, `r1b/compare.json`."]
        txt = set_verdict(p.read_text(), f"**Verdict (1b):** {VERDICT[g]}")
        p.write_text(set_block(txt, "\n".join(rows)))
    # natives
    g12 = N["G12"]
    rows = ["| instrument | T (raw) | p | debates > 0 | T (centered) | p | debates > 0 |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for t in ("bge_restate", "gte_restate", "bge_restate_style", "gte_restate_style"):
        r = g12[t]
        rows.append(f"| {t} | {r['raw']['T']:+.3f} | {r['raw']['p']:.3f} | {r['raw']['n_positive']}/{r['raw']['n_debates']} | "
                    f"{r['centered']['T']:+.3f} | {r['centered']['p']:.3f} | {r['centered']['n_positive']}/{r['centered']['n_debates']} |")
    rows += ["", "**N1a failed** (p < 0.05 in 0 of 4 instruments; p 0.07–0.24). **N1b passed by the letter** (6/10 debates "
             "positive with style-residualized bge), which with T's null-level p means no team-level content unit beyond "
             "chance: inside one room, the motion and the room, not the drafted team, set what agents say.",
             "", "Data: `data/processed/H01-emergent-superagents-exist/r1b/native.json`."]
    p = GP / "G12" / "README.md"
    txt = set_verdict(p.read_text(), "**Verdict (1b):** failed (no team unit beyond the re-partition null, both models)")
    p.write_text(set_block(txt, "\n".join(rows), header="## Result"))
    ne = N["NE42"]
    rows = ["| instrument | period | P1 ΔH median, #39 labels (days < 0) | within − cross, #39 labels | agent-label perm p |",
            "| --- | --- | --- | --- | --- |"]
    for t in ("bge_restate", "gte_restate"):
        for u in ("39", "40", "41"):
            r = ne[t][u]
            rows.append(f"| {t} | #{u} | {r['p1_median_dH']:+.3f} ({r['p1_frac_neg']:.0%}) | {r.get('wc_old_labels', float('nan')):+.3f} | "
                        f"{r.get('wc_p_agent_perm', float('nan')):.4f} |")
    rows += ["", f"**N2a passed** in both models (the old partition's order vanishes in #40 and returns in #41); **N2b passed** in "
             "both models (within − cross falls from +0.11/+0.08 to −0.03/−0.05 and returns to +0.22/+0.25). Room order "
             "follows the channel, as H47 found for coherence; #40's shared objective is a confound in the same direction.",
             "", "Data: `data/processed/H01-emergent-superagents-exist/r1b/native.json`."]
    p = GP / "NE42" / "README.md"
    txt = set_verdict(p.read_text(), "**Verdict (1b):** supported (both models; goal-confounded)")
    p.write_text(set_block(txt, "\n".join(rows), header="## Result"))
    print("done")


if __name__ == "__main__":
    main()
