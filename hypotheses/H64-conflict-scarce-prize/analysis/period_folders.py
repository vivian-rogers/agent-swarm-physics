"""Write H64 goal-period folders: `predict` writes each README with its dated prediction (before the real-data run);
`results` rewrites them with the same prediction plus verdict and results (after the run).

    uv run python hypotheses/H64-conflict-scarce-prize/analysis/period_folders.py predict|results
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve().parent
CARD = HERE.parent
ROOT = CARD.parents[1]
DATA = ROOT / "data/processed/H64-conflict-scarce-prize"
PRED_TIME = "2026-10-04 20:10 UTC"
sys.path.insert(0, str(HERE))
from run import COMPETITION, eligible, prize_class  # noqa: E402

TITLES = {}


def meta():
    pa = pl.read_parquet(ROOT / "data/processed/shared/period_affordances.parquet").filter(~pl.col("holdout"))
    m = pa.group_by("goal_no").agg(pl.col("goal_slug").first(), pl.col("mode").first(), pl.col("regime").first(),
                                   pl.col("N").max(), pl.col("n_days").sum(), pl.col("first_day").min(),
                                   pl.col("last_day").max(), pl.col("n_rooms").max(), pl.col("unit_id"))
    return {r["goal_no"]: r for r in m.to_dicts()}


REPL_PRED = {
    "prize_free": ("No rival-exclusive prize is live in this period. H64 predicts **no antagonism beyond agent fields**: "
                   "the cluster-robust count of significantly negative residual pairs within the calibrated agent-field "
                   "null (p_AF > 0.05), and a confident position-opposition rate r_p near the prize-free median. "
                   "Counts against H64 (the 'only' clause): p_AF ≤ 0.05 (antagonistic pairs without a prize)."),
    "competition": ("A rival-exclusive prize is live for the whole period (a single winner). H64 predicts **elevated "
                    "antagonism**: r_p above the prize-free median and/or excess antagonistic pairs (p_AF ≤ 0.05). "
                    "R-protocol (H37) predicts the prize-free level. My credence for H64's direction here: 0.25."),
    "rivalry_no_prize": ("Role holders compete on shared metrics (rival pairs by role) but there is no single winner and "
                         "no settlement. H64 predicts the **prize-free level** (r_p below the prize-free 75th percentile; "
                         "no excess antagonistic pairs per unit). Counts against: excess pairs in most units."),
    "assigned": ("Assigned sides plus a judged prize. H64 and R-protocol both predict the highest r_p of all periods "
                 "and excess antagonistic pairs."),
}

NATIVE_PRED = {
    "G12": """**Native (H64-N1, judged debates).** Rivals = opposite-team debaters; prize open in the `pre` and `deb` phases, settled after the verdict (`post`); DQ6 phases and teams.
- **N1a:** γ_open < 0 (opponents more negative than teammates while the prize is open), relation-permutation p < 0.01 and cluster-bootstrap CI below 0 [0.9; known from H21/H37].
- **N1b (Amendment A1 rule):** the contrast vanishes after the verdict: Δ̂ = γ̂_open − γ̂_set < 0 with permutation p < 0.05, γ̂_set's CI includes 0, and |γ̂_set| < ½|γ̂_open| [0.7].
- **N1c (heat rival):** the teammates' open − settled shift φ̂ has a CI that includes 0 [0.6].
- **N1d (remanence rival):** after the verdict, losers → winners minus winners → losers has a CI that includes 0 [0.6].
- Primary outcome: soft stance s (Amendment A1); hard class as robustness. Counts against H64: N1b fails (the rival contrast survives settlement).""",
    "G26": """**Native (H64-N2, an election).** Rivals = pairs among the three tied approval-vote candidates (agents 0, 6, 17), who contested the runoff. Prize open from the first agent message of 2026-01-05 to the result (19:35:22 UTC); settled from the result to the confirmatory vote (01-09 18:45 UTC); the confirmatory window (an uncontested 9–0 re-election) reported separately.
- **N2a:** γ_open < 0 with exact rival-set permutation p < 0.05 (all 120 three-agent sets) [0.15]. 14 rival replies fall in the open window, so the expected verdict is **inconclusive** (synthetic power ≤ 0.33 at Δ = −2 logit on hard labels).
- **N2b (descriptive):** the confirmatory window looks like the settled one (the rival contrast there has a CI that includes 0).""",
    "G23": """**Native (H64-N3, chess games).** Rivals = two agents who both link the same Lichess game in chat (13 two-agent games, 12 opponent pairs); a game is open from its first to its last link plus 10 min. γ_open = opponents' replies during one of their open games minus non-opponent replies (day fixed effects); γ_set = opponents' replies at other times.
- **N3a:** γ_open < 0 with node-label permutation p < 0.05 [0.15]. 44 opponent replies fall inside open windows (testable; synthetic power 0.47 at Δ = −2 logit on hard labels).
- H22 found no stance contrast between opponents over the whole week (−0.005), which H64 explains only if the antagonism is confined to open games.""",
}


def write(predict_only: bool):
    M = meta()
    units = eligible()
    goals = sorted({g for g, _ in units})
    res_units = {}
    nat = {}
    if not predict_only:
        for r in json.loads((DATA / "replication/units.json").read_text()):
            res_units.setdefault(r["goal"], []).append(r)
        for n in ("G12", "G26", "G23"):
            p = DATA / f"natives/{n}.json"
            if p.exists():
                nat[n] = json.loads(p.read_text())
    for g in goals:
        name = f"G{g:02d}"
        m = M[g]
        native = name in NATIVE_PRED
        role = "native" if native else "replication"
        cls = prize_class(g)
        d = CARD / "goalperiod-subhypotheses" / name
        (d / "figures").mkdir(parents=True, exist_ok=True)
        gk = d / "figures/.gitkeep"
        if not gk.exists():
            gk.write_text("")
        verdict, result = "pending", "*Pending (run after this prediction).*"
        if not predict_only:
            verdict, result = results_block(name, g, cls, res_units.get(g, []), nat.get(name))
        units_txt = ", ".join(m["unit_id"]) if len(m["unit_id"]) > 1 else "one unit"
        txt = f"""# H64 × {name}: {m['goal_slug']} ({m['first_day']} → {m['last_day']})

**Verdict:** {verdict}
**Role:** {role}
**Period:** regime {m['regime']} · mode {m['mode']} · {m['N']} agents · {m['n_rooms']} room(s) · {m['n_days']} days. Units: {units_txt}. Prize class (pre-registered): **{cls.replace('_', ' ')}**.

## Why this period
{"Native test: " if native else ""}{why(g, cls)}

## Prediction
*Written {PRED_TIME}, before running on this period (card predictions and Amendment A1).*

**Replication layer.** {REPL_PRED[cls]}
{chr(10) + NATIVE_PRED[name] if native else ""}

## Result
{result}

## Scorecard (period-specific axes)
{scorecard(name, cls, verdict)}

## Notes
- Data: `data/processed/H64-conflict-scarce-prize/replication/units.json`{', `natives/' + name + '.json`' if native else ''}. Holdout masked (`holdout_mask`); no held-out day enters.
"""
        (d / "README.md").write_text(txt)
    print(f"wrote {len(goals)} period folders ({'predict' if predict_only else 'results'})")


def why(g, cls):
    if g == 12:
        return "Ten judged debates with DQ6 teams, judges, verdicts and phase instants: the cleanest dated settlement of a rival-exclusive prize, with assigned sides."
    if g == 26:
        return "An election with exact ballots (DQ6): a 9–9–9 approval tie, a runoff among three candidates and a dated result, then an uncontested re-election."
    if g == 23:
        return "A chess tournament: explicit zero-sum opponents with game-level prizes that open and close at known (linked) times, without assigned debate roles."
    if cls == "competition":
        return "A competition with a single winner live for the whole period (`has_competition`): the prize contrast P1 tests whether competition alone produces antagonism."
    if cls == "rivalry_no_prize":
        return "Private roles with rival pairs that compete on shared metrics but have no single winner or settlement: the contrast class for 'scarce'."
    return "A shared-objective week with no rival-exclusive prize: a point of the prize-free floor (P2) on the phase diagram."


def fmt(t, k=3):
    return f"{t[0]:.{k}f} [{t[1]:.{k}f}, {t[2]:.{k}f}]"


def results_block(name, g, cls, units, nat):
    lines = []
    rows = ["| Unit | n replies | r_p (position) | confident opposes | mean stance s | negative pairs (robust) vs null mean (p_AF) | naive count |",
            "| --- | --- | --- | --- | --- | --- | --- |"]
    for r in units:
        rows.append(f"| {r['unit']} | {r['n']} | {fmt(r['r_pos'])} | {fmt(r['r_opp'])} | {fmt(r['sbar'], 2)} | "
                    f"{r['n_neg_robust']} vs {r['null_mean_robust']:.2f} ({r['p_af_robust']:.3f}) | {r['n_neg_naive']} |")
    lines.append("**Replication layer** (day-cluster bootstrap 95% CIs; agent-field null with 200 simulations).\n")
    lines += rows
    exc = [r for r in units if r["p_af_robust"] <= 0.05]
    summ = json.loads((DATA / "replication/summary.json").read_text())
    med = summ["P1"]["prize_free_median"]
    rmean = sum(r["r_pos"][0] for r in units) / max(len(units), 1)
    if cls == "prize_free":
        verdict = "supported" if not exc else "failed"
        lines.append(f"\nPrize-free floor: {'no unit' if not exc else str(len(exc)) + ' unit(s)'} with excess antagonistic pairs (p_AF ≤ 0.05). r_p {rmean:.4f} vs prize-free median {med:.4f}.")
    elif cls == "competition":
        up = rmean > med
        verdict = "supported" if (up or exc) else "failed"
        lines.append(f"\nCompetition: r_p {rmean:.4f} {'above' if up else 'not above'} the prize-free median {med:.4f}; excess antagonistic pairs: {'yes' if exc else 'no'}.")
    elif cls == "rivalry_no_prize":
        p4 = summ["P4"]
        verdict = "supported" if (p4["pass"] and len(exc) <= len(units) / 2) else "failed"
        lines.append(f"\n#51 (all head replies): r_p {fmt(p4['r51'], 4)} vs prize-free 75th percentile {p4['prize_free_q75']:.4f}; units with excess pairs: {len(exc)} of {len(units)}.")
    else:
        verdict = "descriptive"
    if nat:
        s, h = nat["soft"], nat["hard"]
        lines.append("\n**Native layer** (soft stance s primary; hard class robustness).\n")
        lines.append("| Statistic | soft s | hard class |")
        lines.append("| --- | --- | --- |")
        for k, lab in (("g_open", "γ_open (rival − other, open)"), ("g_set", "γ_set (rival − other, settled)"),
                       ("delta", "Δ = γ_open − γ_set")):
            lines.append(f"| {lab} | {s['est'][k]:+.3f} [{s['ci'][k][0]:+.3f}, {s['ci'][k][1]:+.3f}] | "
                         f"{h['est'][k]:+.3f} [{h['ci'][k][0]:+.3f}, {h['ci'][k][1]:+.3f}] |")
        lines.append(f"| permutation p (γ_open; Δ) | {s['p_open']:.4f}; {s['p_delta']:.4f} | {h['p_open']:.4f}; {h['p_delta']:.4f} |")
        lines.append(f"| rival replies open / settled | {s['n_rival_open']} / {s['n_rival_set']} | |")
        if name == "G12":
            lines.append(f"| heat φ (teammates, open − settled) | {s['est']['phi']:+.3f} [{s['ci']['phi'][0]:+.3f}, {s['ci']['phi'][1]:+.3f}] | {h['est']['phi']:+.3f} |")
            if "N1d" in s:
                lines.append(f"| resentment (losers → winners − winners → losers, post) | {s['N1d']['losers_minus_winners']:+.3f} [{s['N1d']['ci'][0]:+.3f}, {s['N1d']['ci'][1]:+.3f}] (n {s['N1d']['n']}) | |")
            nv = {"N1a": s["N1a_pass"], "N1b": s["N1b_pass"], "N1c": s["N1c_heat_ci_includes_0"], "N1d": s.get("N1d_pass")}
            lines.append("\n" + "; ".join(f"{k} {'pass' if v else 'fail'}" for k, v in nv.items()) + ".")
            verdict = "supported" if (s["N1a_pass"] and s["N1b_pass"]) else ("mixed" if s["N1a_pass"] else "failed")
        elif name == "G26":
            c = s["confirmatory_vs_settled"]
            lines.append(f"| confirmatory window: rival contrast | {c['g_conf']:+.3f} [{c['ci_conf'][0]:+.3f}, {c['ci_conf'][1]:+.3f}] (n {c['n_rival_conf']}) | |")
            verdict = "supported" if s["N2a_pass"] else "inconclusive"
            lines.append(f"\nN2a {'pass' if s['N2a_pass'] else 'not passed'} (exact permutation over {s['n_perm']} rival sets).")
        elif name == "G23":
            lines.append(f"| games / opponent pairs | {s['n_games']} / {s['n_opp_pairs']} | |")
            verdict = "supported" if s["N3a_pass"] else ("inconclusive" if s["est"]["g_open"] < 0 else "failed")
            lines.append(f"\nN3a {'pass' if s['N3a_pass'] else 'not passed'}.")
        verdict = verdict if verdict != "inconclusive" else "mixed"
    return verdict, "\n".join(lines)


def scorecard(name, cls, verdict):
    if verdict == "pending":
        return "*Pending.*"
    if name == "G12":
        return "- **E (interventional):** ten dated settlements (verdicts); see the result.\n- **G (ground truth):** DQ6 teams, judges and phases.\n- **H (comparative):** heat and remanence rivals tested (N1c, N1d)."
    if name in ("G26", "G23"):
        return "- **E:** dated settlement(s) used; low power (Amendment A1).\n- **G:** DQ6 (G26) or linked game pairs (G23)."
    return "- **C (adequacy):** antagonism excess against the calibrated agent-field null with cluster-robust pair tests."


if __name__ == "__main__":
    write(predict_only=(sys.argv[1] == "predict"))
