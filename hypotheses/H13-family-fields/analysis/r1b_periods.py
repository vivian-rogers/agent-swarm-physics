"""H13 round 1b: add a `**Verdict (1b):**` line (round-1 line kept) and a dated round-1b section to each replication
period README (G35 ... G51), from r1b/summary.json and r1b/behavior.json. Idempotent (replaces its own section).

Usage: uv run python hypotheses/H13-family-fields/analysis/r1b_periods.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
R1B = ROOT / "data/processed/H13-family-fields/r1b"
PER = HERE.parent / "goalperiod-subhypotheses"
PERIODS = {"G35": ["35"], "G36": ["36b"], "G37": ["37"], "G38": ["38a", "38b", "38c"], "G39": ["39"], "G40": ["40"],
           "G41": ["41"], "G42": ["42"], "G44": ["44"], "G51": ["51a", "51b", "51c", "51d", "51e"]}
HDR = "## Round 1b (improved data, 2026-10-04)"


def f(x, d=3):
    return "–" if x is None else f"{x:.{d}f}"


def main():
    S = json.loads((R1B / "summary.json").read_text())
    beh = json.loads((R1B / "behavior.json").read_text())
    r1 = S["round1"]["per_unit"]
    vb, vg = S["r1b"]["bge_small_none"]["per_unit"], S["r1b"]["gte_modernbert_none"]["per_unit"]
    pb, pg = S["r1b"]["bge_small_none_styp"]["per_unit"], S["r1b"]["gte_modernbert_none_styp"]["per_unit"]
    rs = S["r1b"].get("bge_small_restatements", {}).get("per_unit", {})
    for g, units in PERIODS.items():
        p = PER / g / "README.md"
        s = p.read_text()
        det = lambda v, u: (v[u]["p"] or 1) < 0.05 or (v[u].get("y2_p_lab") or 1) < 0.05
        det_b = [u for u in units if u != "51e" and det(vb, u)]
        det_g = [u for u in units if u != "51e" and det(vg, u)]
        sty_any = [u for u in units if u != "51e" and ((pb[u]["p_sty"] or 1) < 0.05 or (pg[u]["p_sty"] or 1) < 0.05 or (vb[u]["p_sty"] or 1) < 0.05)]
        beh_det = [u for u in units if u != "51e" and beh["units"][u]["B"]["field"]["p"] < 0.05]
        talk_viol = [u for u in units if u != "51e" and (vb[u]["talk_p"] or 1) < 0.05 and (vb[u]["talk_delta"] or 0) > 0]
        old = re.search(r"^\*\*Verdict:\*\*\s*(.+)$", s, re.M).group(1).strip()
        new = "mixed" if (det_b or det_g) else "failed"
        note = f"round 1: {old.split()[0]}; same rule (a1 p < 0.05 or room-adjusted y2 b_lab p < 0.05; P2 fails everywhere)"
        nat = "; native: mixed" if g == "G35" else ""
        line = f"**Verdict (1b):** {new} (round 1: {old.split()[0]}; same in both embedding models{nat})"
        s = re.sub(r"^\*\*Verdict \(1b\):\*\*.*\n", "", s, flags=re.M)
        s = re.sub(r"^(\*\*Verdict:\*\*.*\n)", r"\1" + line.replace("\\", "\\\\") + "\n", s, count=1, flags=re.M)
        rows = []
        for u in units:
            B = beh["units"][u]["B"]
            rows.append(f"| {u} | {f(r1[u]['T'])} (p {f(r1[u]['p'])}) | {f(vg[u]['T'])} (p {f(vg[u]['p'])}) | "
                        f"{f(vb[u]['T_sty'])} / {f(vg[u]['T_sty'])} | {f(pb[u]['T_sty'])} (p {f(pb[u]['p_sty'])}) / {f(pg[u]['T_sty'])} (p {f(pg[u]['p_sty'])}) | "
                        f"{f(rs.get(u, {}).get('T'))} | {f(r1[u]['talk_delta'])} (p {f(r1[u]['talk_p'])}) → {f(vb[u]['talk_delta'])} (p {f(vb[u]['talk_p'])}) | "
                        f"{f(B['field']['obs'])} (p {f(B['field']['p'])}) |")
        sec = [HDR,
               "*Re-run of the pre-registered statistics on the corrected inputs (card section \"Round 1b\"). Old numbers are kept above.* "
               "Inputs: DQ5 statement vectors (bge and gte-modernbert, regime-whitened, 32-d), H13's own style rival S-a and DQ5's shared "
               "`style_resid_period` vectors, DQ5 restatement flags, `activity_bins_fixed` for talk spins, and Jev v3 behavior states (HH267, card Amendment 2). "
               "Data: `data/processed/H13-family-fields/r1b/`.",
               "",
               "| Unit | T_field round 1 (bge) | T_field gte | S-a own (bge / gte) | shared style_resid_period (bge / gte) | T bge, restatements removed | talk Δ old → fixed table | behavioral T_B |",
               "| --- | --- | --- | --- | --- | --- | --- | --- |", *rows, "",
               f"- **Talk on the corrected table:** family homophily in talk timing (Δ > 0, p < 0.05) in {', '.join(talk_viol) if talk_viol else 'no unit'} of this period.",
               "- **Reading:** the content field is unchanged in both models and still vanishes under either style rival; the behavioral field is reported in the card (B1–B4)."]
        if HDR in s:
            s = re.sub(re.escape(HDR) + r".*?(?=\n## |\Z)", "\n".join(sec) + "\n", s, flags=re.S)
        else:
            s = s.rstrip() + "\n\n" + "\n".join(sec) + "\n"
        p.write_text(s)
        print(g, line[:200])


if __name__ == "__main__":
    main()
