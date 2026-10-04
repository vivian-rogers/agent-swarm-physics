"""H22 round 1b: `**Verdict (1b):**` lines (round-1 line kept) and a dated round-1b table in each replication period
README, from r1b/summary.json. Idempotent.

Usage: uv run python hypotheses/H22-private-goals-spin-glass/analysis/r1b_periods.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
S = json.loads((ROOT / "data/processed/H22-private-goals-spin-glass/r1b/summary.json").read_text())
PER = HERE.parent / "goalperiod-subhypotheses"
HDR = "## Round 1b (improved data, 2026-10-04)"
FOLD = {"G51a": ["51a"], "G51b": ["51b"], "G51c": ["51c"], "G51d": ["51d"], "G51e": ["51e"], "G38": ["38a", "38b", "38c"],
        "G40": ["40"], "G44": ["44"]}
V = {"bge": "bge_small_white32_none", "gte": "gte_modernbert_white32_none", "bge styp": "bge_small_styp_none",
     "gte styp": "gte_modernbert_styp_none", "bge dedup": "bge_small_white32_restatements"}
VERD = {"G51a": "descriptive (round 1: descriptive)",
        "G51b": "failed (round 1: failed; rival homophily in every content variant)",
        "G51c": "inconclusive (round 1: inconclusive)",
        "G51d": "inconclusive (round 1: inconclusive)",
        "G51e": "descriptive (round 1: descriptive)",
        "G38": "descriptive (round 1: descriptive)",
        "G40": "descriptive (round 1: descriptive)",
        "G44": "descriptive (round 1: descriptive)"}


def f(x, d=3):
    return "–" if x is None else (f"{x:.{d}f}" if isinstance(x, float) else str(x))


def main():
    st = S.get("stance", {})
    for g, units in FOLD.items():
        p = PER / g / "README.md"
        s = p.read_text()
        s = re.sub(r"^\*\*Verdict \(1b\):\*\*.*\n", "", s, flags=re.M)
        s = re.sub(r"^(\*\*Verdict:\*\*.*\n)", r"\1" + f"**Verdict (1b):** {VERD[g]}\n", s, count=1, flags=re.M)
        rows = []
        for u in units:
            r1 = S["round1"].get(u) or {}
            rows.append(f"| {u} | round 1 | {f(r1.get('rho'), 2)} (p {f(r1.get('p_rho'))}) | {f(r1.get('tau3_dc'), 2)} | "
                        f"{f(r1.get('T_SR'))} / {r1.get('SR_n')} (p> {f(r1.get('SR_p_greater'))}) | {f(r1.get('T_OP'))} | "
                        f"{f(r1.get('W'), 2)} (p {f(r1.get('p_W'), 2)}) | {f(r1.get('talk_rho'), 2)} (p {f(r1.get('talk_p_rho'))}) |")
            for lab, v in V.items():
                d = S["r1b"].get(v, {}).get(u)
                if not d:
                    continue
                rows.append(f"| {u} | {lab} | {f(d['rho'], 2)} (p {f(d['p_rho'])}) | {f(d['tau3_dc'], 2)} | "
                            f"{f(d['T_SR'])} / {d['SR_n']} (p> {f(d['SR_p_greater'])}) | {f(d['T_OP'])} | "
                            f"{f(d['W'], 2)} (p {f(d['p_W'], 2)}) | {f(d['talk_rho'], 2)} (p {f(d['talk_p_rho'])}) |")
            sd = st.get(u)
            if sd and sd.get("n_replies"):
                rows.append(f"| {u} | **stance (DQ2)** | dc split-half {f(sd.get('rho_dc'), 2)} (agent-field p {f(sd.get('rho_dc_p'))}) | "
                            f"{f(sd.get('tau3_dc'), 2)} {sd.get('tau3_dc_ci90') and '[' + ', '.join(f(x, 2) for x in sd['tau3_dc_ci90']) + ']' or ''} | "
                            f"{f(sd.get('T_SR'))} / {sd.get('SR_n')} (p> {f(sd.get('SR_p_greater'))}) | {f(sd.get('T_OP'))} | – | "
                            f"neg. pairs {sd.get('neg_pairs')} vs {f(sd.get('neg_null'), 1)} |")
        sec = [HDR,
               "*Re-run on the corrected inputs (card section \"Round 1b\"); round-1 numbers kept above.* DQ6 ground-truth roles (Opus 5's first role recovered), "
               "DQ5 statement vectors in two models (bge, gte), DQ5 `style_resid_period` vectors (\"styp\"), restatements removed (\"dedup\"), "
               "`activity_bins_fixed` for talk spins, and the DQ2 stance channel with the calibrated agent-field null. Data: `data/processed/H22-private-goals-spin-glass/r1b/`.",
               "",
               "| Unit | Variant | heterogeneity ρ_split | τ₃(dc) | T_SR / pairs (p>) | T_OP | W (p) | talk ρ_split (p) |",
               "| --- | --- | --- | --- | --- | --- | --- | --- |", *rows, ""]
        if HDR in s:
            s = re.sub(re.escape(HDR) + r".*?(?=\n## |\Z)", "\n".join(sec) + "\n", s, flags=re.S)
        else:
            s = s.rstrip() + "\n\n" + "\n".join(sec) + "\n"
        p.write_text(s)
        print(g, "ok")


if __name__ == "__main__":
    main()
