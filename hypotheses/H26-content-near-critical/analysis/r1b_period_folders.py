"""H26 round 1b: `**Verdict (1b):**` lines and a per-unit round-1b block in the period READMEs (G35-G51), plus the native
results (NE42, G12). Idempotent. Reads summary_units.json (round 1) and r1b/<tag>/summary_units.json, r1b/native.json.
Usage: uv run python hypotheses/H26-content-near-critical/analysis/r1b_period_folders.py
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

HYP = Path(__file__).resolve().parents[1]
D = HYP.parents[1] / "data/processed/H26-content-near-critical"
GP = HYP / "goalperiod-subhypotheses"
RUNS = [("r1", "round 1"), ("bge_fixed", "1b bge"), ("gte_fixed", "1b gte"), ("bge_fixed_trim", "1b bge, trimmed activity")]


def f(x):
    if x is None:
        return "–"
    if isinstance(x, float) and (math.isinf(x) or x < -1):
        return "< −1"
    return f"{x:.2f}"


def set_verdict(t, line):
    if "**Verdict (1b):**" in t:
        return re.sub(r"\*\*Verdict \(1b\):\*\*.*", line, t, count=1)
    return re.sub(r"(\*\*Verdict:\*\*[^\n]*\n)", r"\1" + line + "\n", t, count=1)


def set_block(t, body, header="## Round 1b (improved data, 2026-10-04)"):
    blk = f"<!-- R1B -->\n{body}\n<!-- /R1B -->"
    if "<!-- R1B -->" in t:
        return re.sub(r"<!-- R1B -->.*?<!-- /R1B -->", blk, t, flags=re.S)
    return t.rstrip() + f"\n\n{header}\n{blk}\n"


def main():
    U = {"r1": {u["unit"]: u for u in json.loads((D / "summary_units.json").read_text())}}
    for t, _ in RUNS[1:]:
        U[t] = {u["unit"]: u for u in json.loads((D / "r1b" / t / "summary_units.json").read_text())}
    by_goal = {}
    for u in U["r1"].values():
        by_goal.setdefault(int(u["goal_no"]), []).append(u["unit"])
    for g, units in sorted(by_goal.items()):
        p = GP / f"G{g:02d}" / "README.md"
        if not p.exists():
            continue
        rows = ["Fixed activity table (DQ8), DQ5 restatement dedupe, shared goal fields, both embedding models (card: Round 1b). "
                "Gains g = 1 − 1/VR; two-room units L3 room excess, one-room units L2 (upper bound).", "",
                "| unit | run | content day | activity day | talk day | content w30 | activity w30 | talk w30 | Δg_ca w30 | verdict |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        vs = []
        for un in units:
            for t, lab in RUNS:
                x = U[t].get(un)
                if not x:
                    continue
                rows.append(f"| {un} | {lab} | {f(x['c_day_g'])} | {f(x['a_day_g'])} | {f(x['k_day_g'])} | {f(x['c_w30_g'])} | "
                            f"{f(x['a_w30_g'])} | {f(x['k_w30_g'])} | {f(x.get('dg_ca_w30'))} | {x['verdict']} |")
            vs.append((un, U["r1"][un]["verdict"], U["bge_fixed"][un]["verdict"], U["gte_fixed"][un]["verdict"]))
        parts = []
        for un, v0, vb, vg in vs:
            s = vb if vb == vg else f"{vb} (bge) / {vg} (gte)"
            parts.append((f"{un}: " if len(vs) > 1 else "") + s + (" (unchanged)" if vb == vg == v0 else ""))
        rows += ["", f"Data: `data/processed/H26-content-near-critical/r1b/<run>/G{g:02d}/`."]
        t = set_verdict(p.read_text(), "**Verdict (1b):** " + "; ".join(parts))
        p.write_text(set_block(t, "\n".join(rows)))
    N = json.loads((D / "r1b" / "native.json").read_text())
    rows = ["| run | period | content day | content w30 | activity w30 | talk w30 | content w30 ρ_w / ρ_c |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for t in ("bge_fixed", "gte_fixed"):
        for u in ("39", "40", "41"):
            x = N["NE42"][t][u]
            g = lambda k: f(x[k]["g_ex_pseudo"]) if k in x else "–"  # noqa: E731
            rows.append(f"| {t} | #{u} | {g('c_day')} | {g('c_w30')} | {g('a_w30')} | {g('k_w30')} | "
                        f"{x['c_w30']['rho_w']:.2f} / {x['c_w30']['rho_c']:.2f} |")
    rows += ["", "Pseudo-room excess g_ex with the #39 partition (GPT-5 excluded); '< −1' = cross-partition pairs co-move more than "
             "within-partition pairs. **N1a passed** (both models), **N1c passed** (talk), **N1b uninformative** (activity's "
             "pseudo-room excess is already negative in #39). The room excess is channel-borne; #40's shared objective confounds."]
    p = GP / "NE42" / "README.md"
    t = set_verdict(p.read_text(), "**Verdict (1b):** supported (content and talk, both models; activity uninformative)")
    t = t.replace("**Verdict:** pending", "**Verdict:** supported (native, round 1b)")
    p.write_text(set_block(t, "\n".join(rows), header="## Result"))
    rows = ["| instrument | g_on [95% CI] | g_off [95% CI] | g_on after motion removal [95% CI] | N2a | N2b |", "| --- | --- | --- | --- | --- | --- |"]
    for t in ("bge_restate", "gte_restate"):
        x = N["G12"][t]
        c = lambda k: f"{x[k]['g_room']:.2f} [{x[k]['ci'][0]:.2f}, {x[k]['ci'][1]:.2f}]"  # noqa: E731
        rows.append(f"| {t} | {c('on')} | {c('off')} | {c('on_rm')} | {'pass' if x['N2a'] else 'fail'} | {'pass' if x['N2b'] else 'fail'} |")
    rows += ["", "L2 whole-room gains (one room, upper bounds), 10-min slots, restatements removed. The on/off CIs overlap; removing "
             "one leave-one-agent-out direction per debate halves the on-gain (gte misses the 0.5× bar by 0.004). About half of "
             "the content co-movement in a debate is the motion field."]
    p = GP / "G12" / "README.md"
    t = set_verdict(p.read_text(), "**Verdict (1b):** supported (bge) / mixed (gte; N2b missed by 0.004)")
    t = t.replace("**Verdict:** pending", "**Verdict:** mixed (native, round 1b)")
    p.write_text(set_block(t, "\n".join(rows), header="## Result"))
    print("done")


if __name__ == "__main__":
    main()
