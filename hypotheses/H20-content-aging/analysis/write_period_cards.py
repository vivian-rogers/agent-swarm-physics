"""Write H20's per-period folders G<NN>/README.md.

  --predict   (before any real-data run) header, why this period, dated prediction, "Result: pending".
              Never overwrites a README whose prediction already exists.
  --results   (after run_periods.py + summarize.py) fills Verdict, Result table, period scorecard, notes,
              keeping the prediction text untouched.
Usage: uv run python hypotheses/H20-content-aging/analysis/write_period_cards.py --predict | --results
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h20lib as L  # noqa: E402
from h20lib import hc  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

PRED_DATE = "2026-10-03"


def goal_meta():
    txt = (hc.ROOT / "hypotheses/hypohypotheses/goal-periods.md").read_text()
    titles = {int(m.group(1)): m.group(2).strip() for m in re.finditer(r"^### (\d+) · (.+)$", txt, re.M)}
    glance = {}
    for m in re.finditer(r"^\| (\d+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|", txt, re.M):
        glance[int(m.group(1))] = dict(dates=m.group(2).strip(), N=m.group(4).strip(), by=m.group(7).strip(), mode=m.group(8).strip())
    return titles, glance


def period_line(g, cd, glance, rooms):
    reg = "I" if g <= 32 else "II" if g <= 36 else "III"
    mode = glance.get(g, {}).get("mode", "?")
    splits = ""
    if g in hc.STEPS:
        splits = " Step changes inside (kept in one unit; tested as rejuvenation, exception (c)): " + ", ".join(hc.STEPS[g]) + "."
    if g == 51:
        splits += " Holdout tail 09-07 → 09-18 excluded; non-holdout days 07-06 → 09-04 (d = 1–45)."
    if g == 4:
        splits += " Roster swap inside (o4-mini one day; GPT-4.1 out, Claude Opus 4 in); start time moved 05-23."
    return (f"regime {reg} · mode {mode} · {cd['A']} agents with statements · {rooms} · {cd['T']} active days "
            f"({int(cd['valid'].sum())} agent-days with ≥ {hc.MIN_STMTS} statements).{splits}")


WHY = {
    "long": "One of the four long goals named in HH101 (t_w reaches {T} active days). Primary aging test.",
    "medium": "A {T}-day goal: an intermediate range of t_w. Secondary aging test; enters the random-effects summary (transfer within exploration).",
    "short": "A {T}-day goal: the stationary contrast. Too short for a per-period aging verdict; its matched-window slope A_early enters P7 (short vs long, partial pooling, exception (d)).",
}
EXTRA_WHY = {
    4: " Shared objective (write a story, hold an event): a long project with phases (writing → event planning).",
    8: " Four agents designing a benchmark; o3, Opus 4 and 3.7 Sonnet wrote near-identical frameworks independently (a shared field).",
    38: " Shared objective (charity fundraiser), regime III (continuous computer use with consolidation). Two scaffold step changes inside (NE17 outreach approval, NE18 history search): do they rejuvenate?",
    51: " Private, stable individual roles (HH102: glassy); 21 → 32 agents (joins at 07-09/10, 07-17, 07-24/29, 08-28/31, 09-01, 09-03/04); the longest window. Joiners test the agent's own clock vs the kickoff clock.",
    6: " Competitive merch stores (mode K).",
}


def prediction_text(g, role, pw_row):
    p5 = pw_row.get("A|a2=0.15|mu=0.5"); p10 = pw_row.get("A|a2=0.15|mu=1.0")
    p5l = pw_row.get("A|a2=0.05|mu=0.5"); p5h = pw_row.get("A|a2=0.3|mu=0.5")
    pe = pw_row.get("A_early|a2=0.15|mu=0.5")
    powline = (f"Design power of the A test (synthetic, this period's real counts, assumed signal a² = 0.15, 0.05, 0.30): "
               f"{p5:.2f} / {p5l:.2f} / {p5h:.2f} against μ = 0.5 aging, {p10:.2f} against μ = 1 (a² = 0.15). "
               if p5 is not None else "")
    if role == "short":
        return (f"*Written {PRED_DATE}, before running on this period.* {powline}"
                f"Matched-window power (A_early, μ = 0.5, a² = 0.15): {pe:.2f}.\n"
                "- **Expectation:** the kickoff transient K > 0 (the kickoff day is atypical); A and A_early not distinguishable from 0 at this power (the period is reported, not judged).\n"
                "- **P7 input:** A_early with its null SD enters the random-effects contrast between short and long + medium goals; the card predicts no difference (credence 0.55).\n"
                "- **Verdict rule:** descriptive (stationary contrast).")
    pc = pw_row.get("A_c|a2=0.15|mu=0.5")
    s = (f"*Written {PRED_DATE}, before running on this period (card predictions with Amendment 1).* {powline}\n"
         "- **P1:** K > 0 (kickoff transient).\n"
         "- **P2:** A > 0 or A_c > 0 with parametric-bootstrap one-sided p < 0.025 (co-primary; t_w ≥ 2, lags ≤ ⌊(T − 1)/2⌋, "
         "weekend covariate). The original rule (A at p < 0.05) is reported too.\n"
         "- **P3:** if P2 holds, the passing statistic stays > 0 with p < 0.10 after removing ĝ" + (" and the agent's own goal ĝ_i" if g == 51 else "") + ".\n"
         "- **P4:** if P2 holds, μ̂'s 90% CI excludes 0 and A_late > 0 (LODO-CV model ranking reported, not decisive).\n"
         "- **P5:** 0 < μ̂ ≤ 1 if aging is found. **P6:** A_m has the same sign as A.\n"
         "- **Secondary:** β_wk < 0; the active-day clock beats the calendar clock (M1 CV); S3 robustness signs.\n")
    if g == 38:
        s += "- **Rejuvenation (S5):** pairs straddling 04-14 / 04-20 have lower C than the M1 fit predicts (negative step residual); descriptive.\n"
    if g == 51:
        s += ("- **#51:** high plateau q; aging present (credence 0.5). A_c is the better-powered statistic here (many agents). "
              "Joiners: A_i on the own-join clock vs the kickoff clock, descriptive. Rejuvenation at 07-09 / 08-05 / 08-25 / 09-03, descriptive.\n")
    s += ("- **Verdict rule (card + Amendment 1):** supported if P2, P3, P4 hold and A > 0 in chat-only and in the median A_i; failed if "
          "neither A nor A_c is significant and either both lie below the 5th percentile of their μ = 0.5 alternative (fitted nuisance "
          "parameters) or the co-primary design power is ≥ 0.8; failed also if A < 0 with one-sided p < 0.05; mixed otherwise (labelled by cause).")
    return s


def write_predictions():
    st = pl.read_parquet(hc.OUT / "statements.parquet", columns=["goal_no", "agent", "d", "room"])
    days = pl.read_parquet(hc.OUT / "days.parquet")
    titles, glance = goal_meta()
    table = json.loads((hc.OUT / "synthetic/table.json").read_text())
    for g in hc.ALL_PERIODS:
        d = hc.HDIR / f"G{g:02d}"
        rd = d / "README.md"
        if rd.exists() and "## Prediction" in rd.read_text():
            print(f"G{g:02d}: prediction exists, not overwritten")
            continue
        (d / "figures").mkdir(parents=True, exist_ok=True)
        cd = L.count_design(g, st, days)
        nroom = st.filter((pl.col("goal_no") == g) & pl.col("room").is_not_null())["room"].n_unique()
        rooms = "#general only" if g <= 32 else f"{nroom} rooms with agent statements"
        dd = days.filter(pl.col("goal_no") == g).sort("d")
        start, end = dd["pt_date"][0], dd["pt_date"][-1]
        role = hc.role(g)
        why = WHY[role].format(T=cd["T"]) + EXTRA_WHY.get(g, "")
        txt = (f"# H20 × G{g:02d}: {titles.get(g, '?')} ({start} → {end})\n\n"
               f"**Verdict:** pending\n**Role:** exploratory\n**Period:** {period_line(g, cd, glance, rooms)}\n\n"
               f"## Why this period\n{why}\n\n## Prediction\n{prediction_text(g, role, table.get(str(g), {}))}\n\n"
               f"## Result\n*Pending.*\n\n## Scorecard (period-specific axes)\n*Pending.*\n\n## Notes\n")
        rd.write_text(txt)
        print(f"G{g:02d}: prediction written")


# ----------------------------------------------------------------------------------------------
def fmt(x, nd=3, sign=True):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "–"
    return f"{x:+.{nd}f}" if sign else f"{x:.{nd}f}"


def fp(p):
    if p is None or not np.isfinite(p):
        return "–"
    return "< 0.002" if p < 0.002 else f"{p:.3f}"


def result_block(g, r, ra, v, vi):
    """r = pre-registered (isotropic null) result, ra = Amendment 2 (estimated-shape null) result."""
    s, sa = r["raw"]["stats"], ra["raw"]["stats"]
    lines = ["| Statistic | Observed | p, pre-registered null | p, Amendment-2 null | Prediction |",
             "| --- | --- | --- | --- | --- |"]

    def row(name, k, pred, src="raw", upper=True):
        o = r[src]["stats"][k]; oa = ra[src]["stats"][k]
        pk = "p_upper" if upper else "p_lower"
        lines.append(f"| {name} | {fmt(o['obs'])} | {fp(o[pk])} | {fp(oa[pk])} | {pred} |")

    row("K kickoff transient", "K", "> 0 (P1)")
    row("A aging slope (t_w ≥ 2)", "A", "> 0 (P2, co-primary)")
    row("A_c common removed", "A_c", "> 0 (P2, co-primary)")
    row("A_g field removed", "A", "> 0 if P2 (P3)", src="g")
    row("A_late (t_w ≥ median)", "A_late", "> 0 if P2 (P4)")
    row("A_early (t_w 2–4, τ ≤ 2)", "A_early", "P7 input")
    row("A_m swarm mean", "A_m", "sign of A (P6)")
    if "A_ms" in s and "A_ms" in sa:
        row("A_m roster-stable", "A_ms", "reported")
    row("β_wk weekend gap", "bwk", "< 0 (S1)", upper=False)
    lines.append("")
    lines.append(f"Verdict under the pre-registered isotropic null: **{vi['verdict']}**. Under the Amendment-2 null (latent shapes "
                 f"estimated, n_eff shared/private = {ra['raw']['null_model'].get('neff_s', float('nan')):.1f}/"
                 f"{ra['raw']['null_model'].get('neff_p', float('nan')):.1f}; see the card): **{v['verdict']}**.")
    f = r.get("fits", {}); fa = ra.get("fits", {})
    if f:
        cv = f["cv"]
        best = min(cv, key=cv.get)
        lines.append(f"Model fits (t_w ≥ 2, all lags): LODO-CV error × 10³ — " + ", ".join(f"{k} {1e3 * cv[k]:.2f}" for k in ("M0", "M0b", "MQ", "M1", "MT"))
                     + f" (best: {best}; descriptive per Amendment 1). μ̂ = {f['mu_hat']:+.2f}, 90% CI [{f['mu_ci90'][0]:+.2f}, {f['mu_ci90'][1]:+.2f}] "
                     f"(Amendment-2 null: [{fa['mu_ci90'][0]:+.2f}, {fa['mu_ci90'][1]:+.2f}]). "
                     f"M1: q = {f['M1']['params'][0]:.2f}, c0 − q = {f['M1']['params'][1]:.2f}, τ0 = {np.exp(f['M1']['params'][2]):.2g} d. "
                     f"Clock (S2): M1 CV × 10³ calendar {1e3 * f['cv_calendar_clock']['M1']:.2f} vs active-day {1e3 * cv['M1']:.2f}.")
        if "rejuvenation" in f:
            rj = f["rejuvenation"]
            lines.append(f"Rejuvenation (S5) at {', '.join(rj['steps'])}: straddling-pair M1 residual {fmt(rj['obs'])} "
                         f"(M1-simulated null {fmt(rj['null_mean'])} ± {fmt(rj['null_sd'], sign=False)}; p_lower {fp(rj['p_lower'])}).")
    z = np.load(hc.OUT / f"G{g:02d}/matrices.npz")
    C = z["C"]
    lag1 = [C[k, k + 1] for k in range(C.shape[0] - 1)]
    lines.append("Lag-1 correlation C(t_w, t_w + 1) by t_w: " + ", ".join(f"{x:.2f}" if np.isfinite(x) else "–" for x in lag1) + ".")
    a = r["agents"]
    lines.append(f"Per-agent slopes: n = {a['n']}, median A_i {fmt(a['median'])}, share > 0 {fmt(a['frac_pos'], 2, False)}, "
                 f"Wilcoxon p (greater) {fp(a['wilcoxon_p_greater'])}.")
    rob = r["robust"]
    rr = []
    for k in ("chat", "n16", "n64"):
        if k in rob:
            rr.append(f"{k} {fmt(rob[k]['stats']['A']['obs'])}")
    rr.append(f"rarefied {fmt(rob['rare']['A'])}")
    rr.append(f"calendar clock {fmt(rob['calendar_clock']['A'])}")
    if "raw_null2" in r:
        rr.append(f"p under a two-timescale isotropic null {fp(r['raw_null2']['stats']['A']['p_upper'])}")
    lines.append("Robustness of A (S3): " + "; ".join(rr) + ".")
    pw, pwa = r["power"], ra["power"]
    lines.append(f"Design power against μ = 0.5 at the fitted nuisance parameters (q = {r['raw']['null_model']['q']:.2f}, "
                 f"r = {sum(r['raw']['null_model']['r']):.2f}, τ = {r['raw']['null_model']['tau'][0]:.1f} d, mean S = {r['mean_S']:.3f}): "
                 f"co-primary {pw['coprimary|mu=0.5']:.2f} (pre-registered null), {pwa['coprimary|mu=0.5']:.2f} (Amendment-2 null).")
    if r.get("memory"):
        m = r["memory"]
        lines.append(f"Memory (S6; `jaccard_prev` vs log t_w, agent FE): slope {fmt(m['slope'])} ± {fmt(m['se'], sign=False)} (n = {m['n_agent_days']}).")
    if r.get("joiners"):
        jo = r["joiners"]
        ak = np.array([x["A_kickoff_clock"] for x in jo]); ao = np.array([x["A_own_clock"] for x in jo])
        lines.append(f"Joiners (S4, n = {len(jo)}): median A_i on the kickoff clock {fmt(float(np.median(ak)))}, on their own clock "
                     f"{fmt(float(np.nanmedian(ao)))}.")
    lines.append(f"\nData: `data/processed/H20-content-aging/G{g:02d}/` (result.json = pre-registered null, result_aniso.json = Amendment 2, "
                 f"matrices.npz). Figure: [figures/aging_G{g:02d}.pdf](figures/aging_G{g:02d}.pdf).")
    return "\n".join(lines)


def write_results():
    summ = json.loads((hc.OUT / "summary.json").read_text())
    pre = summ["preregistered_iso"]
    for g in hc.ALL_PERIODS:
        rd = hc.HDIR / f"G{g:02d}/README.md"
        rf, rfa = hc.OUT / f"G{g:02d}/result.json", hc.OUT / f"G{g:02d}/result_aniso.json"
        if not rd.exists() or not rf.exists() or not rfa.exists():
            continue
        r, ra = json.loads(rf.read_text()), json.loads(rfa.read_text())
        v, vi = summ["verdicts"][str(g)], pre["verdicts"][str(g)]
        txt = rd.read_text()
        vline = f"{v['verdict']} (Amendment-2 null; pre-registered null: {vi['verdict_word']})"
        txt = re.sub(r"^\*\*Verdict:\*\* .*$", f"**Verdict:** {vline}", txt, count=1, flags=re.M)
        res = result_block(g, r, ra, v, vi)
        note = NOTES.get(g, "")
        txt = re.sub(r"## Result\n.*?(?=\n## Scorecard)", "## Result\n" + v.get("summary_line", "") + " (Amendment-2 null).\n\n" + res + "\n", txt, flags=re.S)
        txt = re.sub(r"## Scorecard \(period-specific axes\)\n.*?(?=\n## Notes)", "## Scorecard (period-specific axes)\n" + v.get("scorecard", "") + "\n", txt, flags=re.S)
        if note and note not in txt:
            txt = txt.rstrip("\n") + "\n" + note + "\n"
        rd.write_text(txt)
        print(f"G{g:02d}: {vline}")


NOTES = {
    38: "- 2026-10-03: the lag-1 correlation rises over the first four days after kickoff (0.66 → 0.87) and is flat at ≈ 0.9 afterwards: a kickoff relaxation with τ_q ≈ 2 active days (interrupted aging), not slowing with age. MQ wins the LODO-CV by a factor 2–5. Day 1 carried the operator's Year-1 correction (NE36). NE17/NE18 cause no rejuvenation.",
    51: "- 2026-10-03: aging of μ = 0.5 size is rejected; a weak late slowing remains (A_late +0.11, μ̂ 0.22 [0.07, 0.41]), carried by the intention stream (chat-only A ≈ 0). Joins and the #focus room cause no rejuvenation detectable at this resolution.",
    20: "- 2026-10-03: the negative slope comes from the last two days (Thanksgiving 11-27/28): lag-1 C falls to 0.48 and 0.30. A holiday perturbation, not age-dependent speed-up.",
    24: "- 2026-10-03: Christmas Day (12-25) breaks the last pair (lag-1 C 0.44 vs ≈ 0.87 before).",
    12: "- 2026-10-03: the most extreme outlier (A = −0.83); the debate week is structured by day (debate, then judging), so its content is phased, not stationary.",
}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--predict", action="store_true")
    ap.add_argument("--results", action="store_true")
    a = ap.parse_args()
    if a.predict:
        write_predictions()
    if a.results:
        write_results()
