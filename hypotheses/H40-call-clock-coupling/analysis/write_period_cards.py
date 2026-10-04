"""Write the replication-layer period READMEs (goalperiod-subhypotheses/G<NN>/README.md) from results/G<NN>.json.
Native folders (G18, G36, G51, NE41) are written by hand from analysis/native.py output and are not overwritten here.

  uv run python hypotheses/H40-call-clock-coupling/analysis/write_period_cards.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h40lib as L  # noqa: E402
import summarize as S  # noqa: E402

GP = L.HYP / "goalperiod-subhypotheses"
NATIVE_FOLDERS = {"G18", "G36", "G51", "NE41"}
SEEN_BEFORE_RULE = {2, 3, 37}


def f(x, nd=2, sign=True):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "n/a"
    return f"{x:+.{nd}f}" if sign else f"{x:.{nd}f}"


def ci(est, se, nd=2):
    if est is None or se is None or not np.isfinite(se):
        return "n/a"
    return f"{est:+.{nd}f} [{est - 1.96 * se:+.{nd}f}, {est + 1.96 * se:+.{nd}f}]"


def card(goal: int, row: dict, r: dict, title: str, units: list[str]) -> str:
    v = row["verdict"]
    c = r["coef"]
    se = r["se"]
    b = r["between"]
    mf = r["modelfree"]
    col = mf["collapse"]
    h = r["heldout"]
    e = r["eps"]
    sens = r.get("sensitivity", {})
    pu = pl.read_parquet(L.SH / "period_units.parquet").filter((pl.col("goal_no") == goal) & ~pl.col("holdout"))
    first, last = pu["first_day"].min(), pu["last_day"].max()
    n_recv = len(set(a for a, rep in zip(r["au_table"]["agent"], r["au_table"]["replies"]) if rep > 0))
    pred_when = ("*Written 2026-10-04 ~06:10 UTC (card P1, P4, P5) and the per-period rule ~07:25 UTC; this period had "
                 "already been run when the rule was written (disclosed on the card).*" if goal in SEEN_BEFORE_RULE else
                 "*Written 2026-10-04 ~06:10 UTC (card P1, P4, P5; per-period rule ~07:25 UTC), before this period was run. "
                 "Templated (Layer 1).*")
    eg = r.get("eta_by_gap", {})
    gap_lines = []
    gr = {}
    for g in ("busy", "long_prev", "pause", "after_forced", "chat_busy"):
        if g in eg and eg[g]["se"] < 1.0:
            gap_lines.append(f"{g.replace('_', ' ')} {ci(eg[g]['est'], eg[g]['se'])}")
    jit = sens.get("jitter", [])
    lines = [
        f"# H40 × G{goal:02d}: {title} ({first} → {last})",
        "",
        f"**Verdict:** {v}",
        "**Role:** replication (exploratory)",
        f"**Period:** regime {r['regime']} · {n_recv} recipients with replies · {r['n_days']} non-holdout days · "
        f"units {', '.join(units)} · {r['n_items']:,} read-out items · {r['n_replies_window']:.0f} replies within 30 min.",
        "",
        "## Why this period",
        "Replication layer: the common call-clock hazard estimator (card, Model) on every eligible goal period "
        "(≥ 4 recipients, ≥ 100 agent-to-agent reply pairs), so periods are comparable phase-diagram points. Not a "
        "period-native test.",
        "",
        "## Prediction",
        pred_when,
        "- **P1:** the exposure-time elasticity η (calls n ≥ 2) has its 95% CI below 0.5: the per-call reply hazard "
        "does not grow with the wall time a call spans (call clock η = 0; wall clock η = 1).",
        "- **P4:** on held-out days the call-clock model predicts reply times better than the wall-clock model (Δ log-lik > 0).",
        "- **P5:** slow and fast cadence tertiles' reply curves collapse better in call count than in wall time.",
        "- Verdict rule: supported if η's CI < 0.5 and Δ log-lik > 0; failed if η's CI > 0.5, or η ≥ 0.5 with Δ log-lik ≤ 0; "
        "mixed otherwise; n/a if SE(η) > 0.5.",
        "",
        "## Result",
        "| Quantity | Value | Reading |",
        "| --- | --- | --- |",
        f"| η (calls n ≥ 2) | {ci(c.get('eta'), se.get('eta'))} | 0 = call clock, 1 = wall clock |",
        f"| η₁ (read-out call, log wait) | {ci(c.get('eta1'), se.get('eta1'))} | effect of how long the message waited |",
        f"| φ / ψ / χ (decay per log calls / log wall age / log newer messages) | {f(c.get('phi'))} / {f(c.get('psi'))} / {f(c.get('chi'))} | which clock relevance decays on |",
        f"| δ (dilution, per log(1 + batch)) | {f(c.get('logk'))} | |",
        f"| η by gap kind | {'; '.join(gap_lines) if gap_lines else 'n/a'} | gap kinds with SE < 1 |",
        f"| Held-out Δ log-lik per item (call − wall) | {f(h['dll_call_wall'], 4)} | > 0: call clock predicts better |",
        f"| Collapse D_call / D_wall | {f(col['D_call'], 2, False)} / {f(col['D_wall'], 2, False)} | lower = tertile curves coincide |",
        f"| Fast / slow tertile, log ratio of reply curves (calls; wall) | {f(col['logratio_call'])}; {f(col['logratio_wall'])} | tertile median call rates {', '.join(f'{x:.0f}' for x in col['tertile_rates'])} /h |",
        f"| Between-agent slope s (per-call coupling on log call rate; {b.get('n_au')} agent-units) | "
        f"{ci(b.get('s'), b.get('s_se'))} (τ = {f(b.get('tau'), 2, False)}) | call clock 0, compensation −1 |",
        f"| Model-free slopes on log rate: per-call β(10 calls); per-hour P(5 min) | {ci(mf.get('slope_call10'), mf.get('slope_call10_se'))}; "
        f"{ci(mf.get('slope_wall5'), mf.get('slope_wall5_se'))} | |",
        f"| Cadence elasticity ε(5 / 15 / 30 min) | {f(e['300']['est'])} / {f(e['900']['est'])} / {f(e['1800']['est'])} "
        f"(SE {f(e['300']['se'], 2, False)} / {f(e['900']['se'], 2, False)} / {f(e['1800']['se'], 2, False)}) | "
        f"d log P(reply within T) / d log speed-up |",
        f"| η under other outcomes / samples: any p_reply ≥ 0.5; addressing; certain items only; jittered starts | "
        f"{f(sens.get('any_tid', {}).get('eta'))}; {f(sens.get('addr_tid', {}).get('eta'))}; "
        f"{f(sens.get('certain_only', {}).get('eta'))}; {', '.join(f(j['eta']) for j in jit) if jit else 'n/a'} | robustness |",
        "",
        "Data: `data/processed/H40-call-clock-coupling/G%02d/` (items, cells, cadence) and `results/G%02d.json`. "
        "Cross-period figure: [`figures/summary_obs.pdf`](../../figures/summary_obs.pdf)." % (goal, goal),
        "",
        "## Scorecard (period-specific axes)",
        f"- **C (adequacy):** held-out Δ log-lik {f(h['dll_call_wall'], 4)} ({'call clock better' if h['dll_call_wall'] > 0 else 'wall clock better'}).",
        f"- **D (unfitted signature):** collapse {'in call count' if col['D_call'] < col['D_wall'] else 'in wall time'} "
        f"(D_call {f(col['D_call'], 2, False)} vs D_wall {f(col['D_wall'], 2, False)}).",
        f"- **F (robustness):** η across outcome definitions and start-time jitter listed above.",
        "",
        "## Notes",
        "- Generated by `analysis/write_period_cards.py` from the replication run; CIs use the larger of the day-bootstrap "
        "and model SEs. The between-agent slope is low-powered in any single period (synthetic SD 0.2–0.35); it is "
        "pooled across periods on the card.",
    ]
    if r["n_days"] < 5:
        lines.append(f"- Only {r['n_days']} non-holdout days: the day bootstrap is degenerate, so model SEs set the CIs.")
    return "\n".join(lines) + "\n"


def main():
    df = S.load_table()
    tt = S.titles()
    pu = pl.read_parquet(L.SH / "period_units.parquet").filter(~pl.col("holdout"))
    for row in df.iter_rows(named=True):
        g = row["goal"]
        name = f"G{g:02d}"
        if name in NATIVE_FOLDERS:
            continue
        r = json.loads((S.RES / f"{name}.json").read_text())
        units = pu.filter(pl.col("goal_no") == g)["unit_id"].to_list()
        d = GP / name
        d.mkdir(parents=True, exist_ok=True)
        (d / "README.md").write_text(card(g, row, r, tt.get(g, f"goal #{g}"), units))
    print("wrote", df.height - len(NATIVE_FOLDERS & {f"G{g:02d}" for g in df["goal"].to_list()}), "replication cards")


if __name__ == "__main__":
    main()
