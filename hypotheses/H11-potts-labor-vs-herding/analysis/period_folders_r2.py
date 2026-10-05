"""Write the round-2 block into each goal-period README (and create G27 / G36, first tested in round 2).

Reads r2/results/score_r2.json. Idempotent: replaces an existing "## Round 2" block and "**Verdict (r2):**" line.
Usage: uv run python hypotheses/H11-potts-labor-vs-herding/analysis/period_folders_r2.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
HYP = HERE.parent
ROOT = HERE.parents[2]
RES = ROOT / "data/processed/H11-potts-labor-vs-herding/r2/results"
GP = HYP / "goalperiod-subhypotheses"
TITLES = {27: ("Hack the OWASP Juice Shop; compete on challenges completed", "2026-01-12 → 2026-01-23", "I"),
          36: ("Interact with other AI agents outside the Village", "2026-03-23 → 2026-03-27", "II → III (units 36a-c)")}


def ci(w, d=2):
    if not w or w.get("est") is None:
        return "n.e."
    if w.get("lo") is None:
        return f"{w['est']:+.{d}f}"
    return f"{w['est']:+.{d}f} [{w['lo']:+.{d}f}, {w['hi']:+.{d}f}]"


def call(w, pos="supported", neg="failed"):
    if not w or w.get("est") is None or w.get("lo") is None:
        return "n.e."
    if w["lo"] > 0:
        return pos
    if w["hi"] < 0:
        return neg
    return "n.s. (" + ("+" if w["est"] > 0 else "−") + ")"


def unit_goal(u):
    return int(u[1:]) if u.startswith("G") else int(u[:2])


def main():
    s = json.loads((RES / "score_r2.json").read_text())
    per = {}
    for key, r in s["R1"]["rows"].items():
        per.setdefault(unit_goal(r["unit"]), {}).setdefault("R1", []).append(r)
    for key, r in s["R2"]["rows"].items():
        per.setdefault(unit_goal(r["unit"]), {}).setdefault("R2", []).append(r)
    for u, r in s["R3"]["rows"].items():
        per.setdefault(unit_goal(u), {}).setdefault("R3", []).append(dict(r, unit=u))
    for g in (18, 19, 20, 24, 25, 26, 27, 30, 31, 33, 35, 36, 37, 38, 39, 40, 41, 42, 44, 51):
        d = GP / f"G{g:02d}"
        f = d / "README.md"
        if not f.exists():
            t, span, reg = TITLES[g]
            d.mkdir(parents=True, exist_ok=True)
            (d / "figures").mkdir(exist_ok=True)
            f.write_text(f"# H11 × G{g:02d}: {t} ({span})\n\n**Verdict:** descriptive (first tested in round 2)\n"
                         f"**Role:** replication (round 2 common estimators)\n"
                         f"**Period:** regime {reg} · whole goal period used as the round-2 unit (named exception (d), card Round 2).\n\n"
                         "## Why this period\nIt has ≥ 25 recruit joins with ≥ 2 choices in at least one channel, so the round-2 "
                         "choice models are testable here. It was not a round-1 candidate or transfer period.\n")
        txt = f.read_text()
        x = per.get(g, {})
        lines = ["## Round 2 (2026-10-05)",
                 "*Predictions: the card's Round 2 block (written 2026-10-05 03:30 UTC, before any round-2 statistic; amendment A1 "
                 "after the synthetic validation, before real data). Units: whole period (#51: period units). Data: "
                 "`data/processed/H11-potts-labor-vs-herding/r2/` (`results/real_r2.json`, `score_r2.json`).*", ""]
        calls = []
        if not x:
            lines.append("Not testable in round 2: fewer than 25 recruit joins with ≥ 2 choices in both channels, and no "
                         "testable output panel.")
            calls.append("n/a (too few joins)")
        if "R1" in x or "R2" in x:
            lines += ["| Unit · channel | α [95% CI] (R1a) | α_FE | lag − lead (R1d) | replay inside: top share / exp(H) (fit · Yule · uniform) | ΔLL artifact − chat (R2a) | OR chat-read \\| act · OR commits \\| chat (R2b) | read − lead, chat · commits (R2c) |",
                      "| --- | --- | --- | --- | --- | --- | --- | --- |"]
            r2by = {(r["unit"], r["ch"]): r for r in x.get("R2", [])}
            for r in sorted(x.get("R1", []), key=lambda r: (r["unit"], r["ch"] != "work")):
                q = r2by.get((r["unit"], r["ch"]), {})
                rep = " · ".join(f"{'✓' if r['replay'][k]['top_share'] else '✗'}/{'✓' if r['replay'][k]['eff_n'] else '✗'}"
                                 for k in ("fit", "yule", "uniform"))
                dll = q.get("dll", {})
                dls = "–" if dll.get("dll") is None else f"{dll['dll']:+.3f} [{dll['lo']:+.3f}, {dll['hi']:+.3f}]"
                om = q.get("or_m", {}).get("or")
                oc = q.get("or_c", {}).get("or")
                ors = f"{om:.2f} · {oc:.2f}" if om and oc else (f"{om:.2f} · –" if om else "–")
                lines.append(f"| {r['unit']} · {r['ch']} (n = {r['n']}) | {ci(r['alpha'])} | {ci(r['alpha_fe'])} | {ci(r['lag_minus_lead'])} | "
                             f"{rep} | {dls} | {ors} | {ci(q.get('rl'))} · {ci(q.get('cl'))} |")
            prim = [r for r in x.get("R1", []) if r["ch"] == "work"] or x.get("R1", [])
            calls.append("R1 attachment " + ", ".join(f"{r['unit']} {r['ch']}: {call(r['alpha'])}" for r in prim))
            q2 = [r for r in x.get("R2", []) if r["ch"] == "work"] or x.get("R2", [])
            calls.append("R2 stigmergy " + ", ".join(
                f"{r['unit']} {r['ch']}: " + call({"est": r['dll'].get('dll'), "lo": r['dll'].get('lo'), "hi": r['dll'].get('hi')})
                for r in q2))
            lines.append("")
        if "R3" in x:
            lines += ["| Unit | log RR herd vs solo, commits (R3a) | landed | matched pairs (mean log ratio) | θ crowding (R3b) | herd / solo windows |",
                      "| --- | --- | --- | --- | --- | --- |"]
            for r in x["R3"]:
                m = r.get("matched")
                lines.append(f"| {r['unit']} ({r['group']}) | {ci(r.get('commit'))} | {ci(r.get('land'))} | "
                             f"{'–' if not m else format(m['mean_log_ratio'], '+.2f') + ' ± ' + format(m['se'], '.2f')} | "
                             f"{ci(r.get('theta'))} | {r.get('n_herd')}/{r.get('n_solo')} |")
            calls.append("R3 herding raises output " + ", ".join(f"{r['unit']}: {call(r.get('commit'))}" for r in x["R3"]))
            calls.append("θ < 1 " + ", ".join(
                f"{r['unit']}: {'yes' if r.get('theta') and r['theta']['hi'] < 1 else ('n.e.' if not r.get('theta') else 'no')}" for r in x["R3"]))
            lines.append("")
        lines.append("Reading rules (card): R1a counts α with CI > 0; causal attachment needs α_FE > 0 and lag − lead > 0 "
                     "together (A1); R2a counts ΔLL > 0 (artifact beats chat), with the CI-based count next to it; R3a counts "
                     "log RR > 0. n.e. = not estimable (A1: < 5 chosen exposed rows), n.s. = CI includes 0.")
        block = "\n".join(lines) + "\n"
        vline = "**Verdict (r2):** " + "; ".join(calls)
        txt = re.sub(r"\n## Round 2 \(2026-10-05\).*?(?=\n## |\Z)", "", txt, flags=re.S).rstrip() + "\n"
        if "**Verdict (r2):**" in txt:
            txt = re.sub(r"\*\*Verdict \(r2\):\*\*.*\n", vline + "\n", txt)
        else:
            lines_t = txt.split("\n")
            idx = max(i for i, l in enumerate(lines_t) if l.startswith("**Verdict"))
            lines_t.insert(idx + 1, vline)
            txt = "\n".join(lines_t)
        f.write_text(txt.rstrip() + "\n\n" + block)
        print(g, vline[:160])


if __name__ == "__main__":
    main()
