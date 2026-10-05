"""H13 round 2: append (idempotently) a "Round 2" block to the period READMEs G35-G51 and NE32.

Usage: uv run python hypotheses/H13-family-fields/analysis/r2_periods.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r2lib as R  # noqa: E402

GP = Path(__file__).resolve().parents[1] / "goalperiod-subhypotheses"
START, END = "<!-- r2:start -->", "<!-- r2:end -->"


def f(x, d=3):
    return "–" if x is None else f"{x:.{d}f}"


def put(path: Path, block: str, verdict_line: str):
    s = path.read_text()
    s = re.sub(re.escape(START) + r".*?" + re.escape(END) + r"\n?", "", s, flags=re.S)
    s = re.sub(r"^\*\*Verdict \(r2\):\*\*.*\n", "", s, flags=re.M)
    lines = s.split("\n")
    k = max(i for i, l in enumerate(lines[:8]) if l.startswith("**Verdict"))
    lines.insert(k + 1, verdict_line)
    s = "\n".join(lines).rstrip("\n") + "\n\n" + START + "\n" + block.strip("\n") + "\n" + END + "\n"
    path.write_text(s)


def main():
    lad = json.loads((R.R2 / "ladder.json").read_text())
    ro = json.loads((R.R2 / "readout.json").read_text())
    enc = json.loads((R.R2 / "encult.json").read_text())
    lab_of, name_of = R.roster_labs()
    joiners = enc["bge_white32"]["per_joiner"]
    by_g = {}
    for u, g in R.GDIR.items():
        by_g.setdefault(g, []).append(u)
    head = ("## Round 2 (2026-10-05): graded style rival, read-out family contrast, newcomers\n"
            "*Pre-registered in the card (Round 2, 03:25 UTC), validated on synthetic skeletons, then run on non-reserved data. "
            "The round-2 verdicts are pooled across units; the numbers below are this period's contributions. "
            "Code: `analysis/r2_ladder.py`, `r2_readout.py`, `r2_encult.py`; data: `data/processed/H13-family-fields/r2/`.*\n")
    for g, units in by_g.items():
        rows = ["| Unit | T raw (bge / gte) | T W3: within-agent style + function words (bge / gte) | T S-a (pooled; style-only null −0.046) "
                "| read-out J same / cross lab (bge) | Δ_J^adj [95% CI] | talk Δβ [95% CI] |",
                "| --- | --- | --- | --- | --- | --- | --- |"]
        for u in units:
            b, t = lad["units"]["bge"][u], lad["units"]["gte"][u]
            r = ro["units"].get(u, {})
            if r.get("eligible"):
                c = r["bge_white32"]
                js = f"{f(c['same']['est'])} / {f(c['cross']['est'])}"
                da = f"{f(c['delta_adj']['est'])} [{f(c['delta_adj']['lo'])}, {f(c['delta_adj']['hi'])}]"
            else:
                js, da = "not eligible (< 200 hop-0 rows)", "–"
            tk = r.get("talk", {}).get("delta_adj", {})
            tks = f"{f(tk.get('est'), 4)} [{f(tk.get('lo'), 4)}, {f(tk.get('hi'), 4)}]" if tk else "–"
            sig = lambda v: "*" if v["p"] < 0.05 else ""
            rows.append(f"| {u} | {f(b['L0']['T'])}{sig(b['L0'])} / {f(t['L0']['T'])}{sig(t['L0'])} | "
                        f"{f(b['W3']['T'])}{sig(b['W3'])} / {f(t['W3']['T'])}{sig(t['W3'])} | {f(b['S-a']['T'])} | {js} | {da} | {tks} |")
        gno = int(g[1:])
        jj = [p for p in joiners if p["goal_no"] == gno]
        jtxt = ""
        if jj:
            jtxt = "\n**Newcomers joining in this period (R2-B; lab alignment a(d), bge raw, 5-statement means):**\n" + "\n".join(
                f"- {name_of[p['agent']]} ({p['lab']}): a(d) = " + ", ".join(f(x, 2) for x in p["a"]) +
                "; room outsiderness r(d) = " + ", ".join(f(x, 2) for x in p["r"]) for p in jj) + "\n"
        block = (head + "\n" + "\n".join(rows) + "\n\n* lab-permutation p < 0.05. Pooled (card): W3 keeps 32% (bge) / 47% (gte) of the raw "
                 "field; the read-out contrast Δ_J^adj = 0.029 [0.010, 0.054] over 8 regime-III units (half of it is lab-level "
                 "susceptibility and potency, post hoc); talk shows no family contrast.\n" + jtxt)
        put(GP / g / "README.md", block, "**Verdict (r2):** descriptive (round-2 rules are pooled across units; see the card's Round 2)")
    # NE32: #51 newcomers
    jj = [p for p in joiners if p["goal_no"] == 51]
    ph = json.loads((R.R2 / "posthoc.json").read_text())["PH4"]["bge_white32"]
    block = ("## Round 2 (2026-10-05): enculturation of newcomers (R2-B)\n"
             "*Pre-registered in the card (Round 2, B-P1–B-P4), synthetic-validated, run on non-reserved data. "
             "This folder holds the #51 part; the pooled test uses 20 joiners from regimes I–III.*\n\n"
             "| Joiner | Lab | a(d), d = 1… (bge raw) | r(d) |\n| --- | --- | --- | --- |\n" +
             "\n".join(f"| {name_of[p['agent']]} | {p['lab']} | " + ", ".join(f(x, 2) for x in p["a"]) + " | " +
                       ", ".join(f(x, 2) for x in p["r"]) + " |" for p in jj) +
             f"\n\n**Reading.** Pooled over 20 joiners, newcomers start at their lab's field (a(1) 0.205, relabelling p 0.0045) and "
             f"drift away (slope −0.034 per day [−0.065, −0.003]). *Post hoc:* #51 joiners start neutral "
             f"(a(1) {f(ph['g51']['a1']['mean'])} [{f(ph['g51']['a1']['lo'])}, {f(ph['g51']['a1']['hi'])}], n = {ph['g51']['a1']['n']}); "
             f"the lab start and the drift come from the 13 earlier joiners (a(1) {f(ph['pre51']['a1']['mean'])}). "
             "In #51 private roles, assigned at or after joining, dominate content from day 1 (H98 NE33).\n")
    put(GP / "NE32" / "README.md", block, "**Verdict (r2):** failed for #51 (newcomers start neutral here; pooled B-P1 passes on earlier joiners)")


if __name__ == "__main__":
    main()
