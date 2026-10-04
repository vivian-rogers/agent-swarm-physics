"""Write goalperiod-subhypotheses/G<NN>/README.md and NE42/README.md for H68 from results.json.

  uv run python hypotheses/H68-dilution-mixture/analysis/write_period_cards.py
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CARD = HERE.parent
D = ROOT / "data/processed/H68-dilution-mixture"

META = {
    "G10": ("Complete as many games as you can", "2025-08-18 → 08-22", "I", "I", "#general", "NE03 chat fetch limit 08-20"),
    "G24": ("Do random acts of kindness!", "2025-12-22 → 12-26", "I", "C", "#general", "none"),
    "G25": ("Create a digital museum of 2025", "2025-12-29 → 01-02", "I", "C", "#general", "none"),
    "G26": ("Elect a village leader", "2026-01-05 → 01-09", "I", "C", "#general", "none"),
    "G27": ("Hack the OWASP Juice Shop", "2026-01-12 → 01-23", "I", "K", "#general", "none"),
    "G30": ("Adopt a park and get it cleaned!", "2026-02-09 → 02-13", "I", "C", "#general", "NE10 nudger on"),
    "G31": ("Pick your own goal", "2026-02-16 → 02-20", "I", "F", "#general", "joins, retirement, NE11"),
    "G35": ("Test your game", "2026-03-16 → 03-20", "II", "C", "#best / #rest", "NE15 split, first day"),
    "G36": ("Interact with other AI agents outside the Village", "2026-03-23 → 03-27", "II/III", "C", "#best / #rest",
            "NE14 perma-computer-use 03-24"),
    "G37": ("Pick your own goal!", "2026-03-30 → 04-01", "III", "F", "#best / #rest", "none"),
    "G38": ("Choose a charity and raise money", "2026-04-02 → 04-24", "III", "C", "#best / #rest", "NE17, joins"),
    "G39": ("Build your own interactive world!", "2026-04-27 → 05-01", "III", "I", "#best / #rest", "NE42 side A"),
    "G40": ("Connect your worlds into a 3D universe!", "2026-05-04 → 05-08", "III", "C", "merged room", "NE42 side B"),
    "G41": ("Perform novel research!", "2026-05-11 → 05-15", "III", "I", "#best / #rest", "NE42 side A'"),
    "G42": ("Run your own Youtube channel!", "2026-05-18 → 05-22", "III", "I", "#best / #rest", "a join 05-20"),
    "G44": ("Finetune your leader!", "2026-05-26 → 05-29", "III", "C", "#best / #rest", "NE31 joins 05-28"),
    "G51": ("Each agent: maximize your assigned goal", "2026-07-06 → 09-04 (non-holdout)", "III", "P", "#general (+ #focus)",
            "roster joins 21 → 32; NE43; tail held out"),
}


def f(x, d=2):
    return "—" if x is None else f"{x:.{d}f}"


def main():
    res = json.loads((D / "results.json").read_text())
    rows = []
    for p, o in res["periods"].items():
        t, dates, reg, mode, rooms, splits = META[p]
        native = p == "G51"
        role = "native" if native else "replication"
        mix = o.get("mix") or {}
        m2 = mix.get("M2", {})
        verdict = o["verdict"]
        lines = [f"# H68 × {p}: {t} ({dates})", "",
                 f"**Verdict:** {verdict}",
                 f"**Role:** exploratory · {role}",
                 f"**Period:** regime {reg} · mode {mode} · {o['n_agents']} agents ({o['n_eligible']} eligible) · {rooms}. "
                 f"Splits inside the period: {splits} (one unit for per-agent fits).", "",
                 "## Why this period",
                 ("The native period: 32 agents from 9 labs, k above 100, and timer-wake batches with exogenous size "
                  "(per-agent β^D2). It has the most agents, the most labs and the widest k range."
                  if native else "Replication: one of H18's 17 dilution periods (the common per-agent estimator)."), "",
                 "## Prediction",
                 "*Written 2026-10-04 19:15 UTC (card), before any per-agent statistic.* "
                 "P1 here: the mixture LR rejects one exponent (bootstrap p < 0.05) with modes in [0.7, 1.3] and "
                 "[−0.3, 0.3], each with ≥ 2 agents. Against: powered and τ̂ upper 95% CI < 0.35."
                 + (" Native additions: lab η² ≥ 0.4; ρ(β^D2, β) ≥ 0.4; ≤ 20% of agents with β in [0.3, 0.7]." if native else ""),
                 "",
                 "## Result",
                 "| Statistic | Value |", "| --- | --- |",
                 f"| eligible agents | {o['n_eligible']} of {o['n_agents']} |",
                 f"| synthetic power (H68 world W2) · false P1 rate (W1) | {f(o.get('power_W2'))} · {f(o.get('size_W1'))} |",
                 f"| μ̂ (random-effects mean of β_i) | {f(o.get('mu'))} |",
                 f"| τ̂ between-agent SD [profile 95% CI] | {f(o.get('tau'))} [{f((o.get('tau_ci') or [None, None])[0])}, "
                 f"{f((o.get('tau_ci') or [None, None])[1])}] |",
                 f"| mixture LR, bootstrap p | {f(mix.get('lr'))}, {f(mix.get('p'), 3)} |",
                 f"| two-component modes (agents) | {f(m2.get('m_lo'))} ({m2.get('n_lo', '—')}) / {f(m2.get('m_hi'))} "
                 f"({m2.get('n_hi', '—')}) |",
                 f"| H68-literal ℓ − U ℓ | {f(mix.get('dll_H68_U'))} |",
                 f"| share of agents with β in [0.3, 0.7] | {f(o.get('mid_share'))} |",
                 f"| precision-weighted mean β_i − pooled β (P3) | {f(o.get('gap'))} (pooled {f((o.get('pooled') or {}).get('beta'))}) |",
                 "", f"Data: `data/processed/H68-dilution-mixture/{p}/` (`agents.parquet`, `period.json`).", ""]
        if native:
            n = res["N_G51"]
            lab = n.get("lab") or {}
            d2 = n.get("d2") or {}
            lines += ["**Native tests.**",
                      f"- (b) lab share of between-agent variance η² = {f(lab.get('eta2'))} (permutation p {f(lab.get('p'), 3)}; "
                      f"{lab.get('n_labs', '—')} labs).",
                      f"- (c) per-agent timer-wake exponent vs talk-turn exponent: Spearman ρ = {f(d2.get('rho'))} "
                      f"(p {f(d2.get('p'), 3)}, n {d2.get('n', '—')}).",
                      f"- (d) shape: the floor model (1/k + ρ) beats k^−β by > 2 log-lik units in {n.get('floor_better')} agents; "
                      f"k^−β wins in {n.get('pow_better')} of {n.get('n')}.", ""]
        lines += ["## Scorecard (period-specific axes)",
                  "- **C:** the unimodal model is " + ("rejected" if (mix.get('p') or 1) < 0.05 else "not rejected") +
                  " by the parametric bootstrap.",
                  "- **D:** the β distribution shape (spread and modes) is the unfitted statistic.",
                  "- **F:** synthetic power and size at this period's real counts are in the table.", "",
                  "## Notes", "- 2026-10-04: round 1, generated by `analysis/write_period_cards.py`.", ""]
        out = CARD / "goalperiod-subhypotheses" / p
        (out / "figures").mkdir(parents=True, exist_ok=True)
        (out / "README.md").write_text("\n".join(lines))
        rows.append((p, role, verdict, o))
    # NE42
    ne = res.get("N_NE42")
    if ne:
        out = CARD / "goalperiod-subhypotheses" / "NE42"
        (out / "figures").mkdir(parents=True, exist_ok=True)
        ok = (ne["rho"]["rho"] >= 0.4) and abs(ne["mean_dbeta"]) <= 0.15
        bad = (ne["rho"]["rho"] <= 0) or abs(ne["mean_dbeta"]) > 0.3
        v = "supported" if ok else ("failed" if bad else "mixed")
        if ne["n"] < 8:  # 5 agents: the rank test has no power (rho(beta39, beta41) itself is negative)
            v = "descriptive"
        lines = ["# H68 × NE42: merge and split at a fixed roster (#39 → #40 → #41)", "",
                 f"**Verdict:** {v}", "**Role:** exploratory · native",
                 "**Period:** regime III · #39 (two rooms), #40 (merged room, k ×1.45), #41 (two rooms again) · agents "
                 "eligible in all three periods. Transition design (exception (c)).", "",
                 "## Why this period",
                 "The merge raises every agent's backlog k at a fixed roster, then the split lowers it. A trait keeps its "
                 "exponent; a load-set state moves with k.", "",
                 "## Prediction", "*Written 2026-10-04 19:15 UTC (card).* ρ(β_40, mean of β_39 and β_41) ≥ 0.4 and the "
                 "mean within-agent Δβ (40 vs 39/41) within ±0.15. Against: ρ ≤ 0, or |Δβ| > 0.3.", "",
                 "## Result", "| Statistic | Value |", "| --- | --- |",
                 f"| agents eligible in #39, #40 and #41 | {ne['n']} |",
                 f"| Spearman ρ(β_40, side mean) | {f(ne['rho']['rho'])} (p {f(ne['rho']['p'], 3)}) |",
                 f"| Spearman ρ(β_39, β_41) | {f(ne['rho_39_41']['rho'])} (p {f(ne['rho_39_41']['p'], 3)}) |",
                 f"| precision-weighted mean Δβ (40 − sides) | {f(ne['mean_dbeta'])} ± {f(ne['se_dbeta'])} |", "",
                 "## Scorecard (period-specific axes)", "- **E:** the merge is the intervention; see the verdict.", "",
                 "## Notes", "- 2026-10-04: round 1, generated by `analysis/write_period_cards.py`.", ""]
        (out / "README.md").write_text("\n".join(lines))
        rows.append(("NE42", "native", v, None))
    (D / "card_rows.json").write_text(json.dumps([(r[0], r[1], r[2]) for r in rows]))


if __name__ == "__main__":
    main()
