"""H72 round 2: append (or replace) a "## Round 2" section in each replication period README.
Reads r2/results_r2.json and r2/synthetic/power.json. The round-1 verdict line is not changed (it scores the
starvation claim); the section carries the chatter-hold verdict (card, "Per-period R1 verdict", amendment R2-A2).
Usage: uv run python hypotheses/H72-trap-aging-input-starvation/analysis/write_r2_periods.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r2lib as R  # noqa: E402

GP = HERE.parent / "goalperiod-subhypotheses"
SRC = "data/processed/H72-trap-aging-input-starvation/r2/results_r2.json"


def f(v):
    return f"{v['est']:+.2f} [{v['ci'][0]:+.2f}, {v['ci'][1]:+.2f}]"


def t3(v):
    return f"{v[0]:+.1f} [{v[1]:+.1f}, {v[2]:+.1f}]"


def r1_verdict(r, power):
    if "bC_full" not in r:
        return "descriptive (underpowered: < 30 escapes or non-escapes)"
    lo, hi = r["bC_full"]["ci"]
    if hi < 0:
        return "supported"
    if lo > 0:
        return "failed (β_C above 0)"
    return "failed (powered null)" if power >= 0.8 else f"descriptive (CI includes 0; power {power:.2f} at −0.25)"


def section(per, r, pw, d):
    power = pw.get(per, {}).get("power_bC_-0.25") or 0.0
    v = r1_verdict(r, power)
    L = ["## Round 2 (2026-10-05): chatter hold", "",
         f"**Round-2 verdict (chatter hold, R1):** {v}", "",
         "*Prediction (written 2026-10-05 before running; card \"Round 2\", R1 and amendments R2-A1/A2):* escape at a wake "
         "falls with ln(1 + undirected items read at the 5 calls before it), β_C < 0, in the full model "
         "(agent FE + base + ln a + ln k + ln s_dir + dose" + (" + ln(1 − f_call))" if r.get("full_model", "").count("F") else ")") +
         ". Only G51 is powered (synthetic); elsewhere a CI including 0 is descriptive.", "",
         f"*Result* (`analysis/run_r2.py`; `{SRC}`; day-block bootstrap 200):", "",
         "| Quantity | Estimate [95% CI] |", "| --- | --- |",
         f"| wakes / sustained escapes (consolidation-start traps dropped) | {r['n']} / {r['n_escape']} |",
         f"| synthetic power for β_C = −0.25 | {power:.2f} |"]
    if "bC_full" in r:
        L += [f"| β_C, full model | {f(r['bC_full'])} |", f"| β_C, B + A + C | {f(r['bC_BAC'])} |",
              f"| ln k (wake index), full model | {f(r['bk_full'])} |", f"| ln s_dir (starvation), full model | {f(r['bs_full'])} |"]
        if "bf_full" in r:
            L.append(f"| ln(1 − f_call) (urn coefficient), full model | {f(r['bf_full'])} |")
    rc = d["reconcile"].get(per)
    if rc:
        cv = rc["cv"]
        g = ", ".join(f"{nm} {t3(cv[f'gain_{m}'])}" for m, nm in (("A", "clocks"), ("S", "starvation"), ("C", "chatter"), ("F", "self-share")) if f"gain_{m}" in cv)
        L.append(f"| held-out gain over the base (nats per 1,000 wakes) | {g} |")
        if per in ("G51", "G38"):
            e = ", ".join(f"{nm} {cv[f'eps_{m}'][0]:+.2f} [{cv[f'eps_{m}'][1]:+.2f}, {cv[f'eps_{m}'][2]:+.2f}]"
                          for m, nm in (("S", "starvation"), ("C", "chatter"), ("F", "self-share")) if f"eps_{m}" in cv)
            L.append(f"| aging share explained ε (held out) | {e} |")
    tr = d["transfer"].get(per)
    if tr:
        L.append("| transfer of G51 slopes (held-out gain, nats per 1,000 wakes) | " +
                 ", ".join(f"{nm} {t3(tr[m])}" for m, nm in (("S", "starvation"), ("C", "chatter"), ("F", "self-share"))) + " |")
    if per == "G51":
        e = d["g51_extras"]
        L += [f"| β_C, first wakes only (k = 1) | {f(e['bC_k1'])} |", f"| β_C, agent + day FE | {f(e['bC_dayfe'])} |",
              f"| dose × directed read at the wake | {f(e['b_int'])} |", f"| in-flight placebo (full model) | {f(e['b_inflight'])} |",
              f"| slope on ln chatter rate (competing-rates form predicts −1) | {f(e['b_rate'])} |",
              f"| transfer of G38's slopes to G51 | " + ", ".join(f"{nm} {t3(d['transfer']['G51_from_G38'][m])}" for m, nm in
                                                            (("S", "starvation"), ("C", "chatter"), ("F", "self-share"))) + " |"]
    L += [""]
    if per == "G51":
        L += ["Reading: self-share carries 65% of the aging clocks' held-out information (proxy worlds ≤ 22%), chatter 22%, "
              "starvation none. The chatter hold is small, survives day FE and first wakes, and a directed read cancels it.", ""]
    elif per == "G38":
        L += ["Reading: not powered for R1 or the reconcile (A2, A3); the direction agrees with G51 for self-share "
              "(ε 0.72) and not for chatter.", ""]
    return "\n".join(L) + "\n"


def main():
    d = json.loads((R.R2 / "results_r2.json").read_text())
    pw = json.loads((R.R2 / "synthetic/power.json").read_text())
    for per, r in d["r1"].items():
        p = GP / per / "README.md"
        txt = p.read_text()
        if "## Round 2 (2026-10-05)" in txt:
            txt = txt[:txt.index("## Round 2 (2026-10-05)")].rstrip() + "\n"
        p.write_text(txt.rstrip() + "\n\n" + section(per, r, pw, d))
        print(per, r1_verdict(r, pw.get(per, {}).get("power_bC_-0.25") or 0))


if __name__ == "__main__":
    main()
