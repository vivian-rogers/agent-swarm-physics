"""Write H15 G<NN>/ and NE<NN>/ folders.

  --predict   writes each README with the period's scramble events (from the catalog: scramble variables only) and the
              dated prediction. Run BEFORE run_scrambles.py touches real outcomes.
  --results   appends the Result section from data/processed/.../results.json (keeps the prediction text verbatim).

No agent text is written; agents appear by roster name.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h15common import HYP, OUT, SH, calendar_nonholdout  # noqa: E402

import polars as pl  # noqa: E402

PRED_DATE = "2026-10-03"
cat = pl.read_parquet(OUT / "scramble_catalog.parquet")
ce = pl.read_parquet(OUT / "consolidations.parquet")
cal = calendar_nonholdout()
ad = pl.read_parquet(OUT / "agent_day.parquet")
vch = json.loads((OUT / "v_choice.json").read_text())
syn = json.loads((OUT / "synthetic.json").read_text()) if (OUT / "synthetic.json").exists() else None
goal_titles = {}
try:
    import gzip
    import orjson
    sys.path.insert(0, str(HYP.parents[1] / "infra/shared"))
    from common import load_goals  # noqa: E402
    goal_titles = {g["goal_no"]: g["goal"] for g in load_goals()}
except Exception:  # noqa: BLE001
    pass

V_STAR = {"I": vch["I"]["chosen"], "II": vch["regime_II_uses"], "III": vch["III"]["chosen"]}
PRIMARY = syn["primary_counterfactual"]["chosen"] if syn else "kal"


def folder_name(unit: str) -> str:
    m = re.match(r"(\d+)([ab]?)", unit)
    return f"G{int(m.group(1)):02d}{m.group(2)}"


def period_line(unit):
    c = cal.filter(pl.col("unit") == unit)
    a = ad.filter(pl.col("unit") == unit)
    reg = str(c["regime"][0])
    d0, d1 = c["pt_date"].min(), c["pt_date"].max()
    return reg, d0, d1, c.height, a["agent"].n_unique()


def events_table(unit):
    e = cat.filter(pl.col("unit") == unit).sort("type", "pt_date")
    if e.height == 0:
        return "", e
    lines = ["| Type | Date | Agent | Dose δ | Detail |", "| --- | --- | --- | --- | --- |"]
    for r in e.iter_rows(named=True):
        det = ""
        if r["type"] in ("ML", "MG"):
            det = f"size {r['n_chars']} chars vs set point {r['sp']:.0f}; line Jaccard {r['jaccard']:.2f}"
        elif r["type"] == "MR":
            det = f"line Jaccard {r['jaccard']:.3f}, size kept"
        elif r["type"] == "CC":
            det = f"exposure share {r['s_pre']:.2f} → {(1 - r['dose']) * r['s_pre']:.2f} for {r['run_len']} active days; {r['note'].split(';')[0]}"
        elif r["type"] == "MN":
            det = f"first active day; {r['note']}"
        lines.append(f"| {r['type']} | {r['pt_date']} | {r['name']} | {r['dose']:.2f} | {det} |")
    return "\n".join(lines), e


def prediction_text(unit, e, reg, ncf, ncv):
    vs = V_STAR[reg]
    types = set(e["type"].to_list()) if e.height else set()
    p = [f"*Written {PRED_DATE}, before running on this period.* Primary viability V* = **{vs}** "
         f"(regime {reg}; the D2.6 rule was inconclusive, so all five candidates get equal weight in the result table). "
         f"Primary counterfactual: `{PRIMARY}` (chosen by the synthetic rule). Units: SD of the period's same-day residual."]
    n = lambda t: int((e["type"] == t).sum()) if e.height else 0  # noqa: E731
    if "ML" in types:
        p.append(f"- **ML ({n('ML')} event(s)), card P1:** ΔV < 0 on V*, about −0.25 SD per event. With this few events "
                 "the per-period test has low power (synthetic: ~50% power for −0.4 SD across all 16 catalogued ML events), "
                 "so a non-significant negative or null result does not count against P1 here; a positive ΔV with z ≥ 2 does. "
                 "P9: a negative pre-trend is expected (resets on bad days).")
    if "MG" in types:
        p.append(f"- **MG ({n('MG')} glitch(es)), secondary:** a smaller effect than ML (memory is restored within 5 snapshots); no sign prediction.")
    if "MR" in types:
        p.append(f"- **MR ({n('MR')} rewrite(s)), card P3 (negative control):** ΔV ≈ 0 (|z| < 2). |z| ≥ 2 counts against the hashed-line measure.")
    if "MN" in types:
        p.append(f"- **MN ({n('MN')} newcomer(s)), card P4:** deficit (tenure days 1–3 vs 6–12, net of incumbents) ≤ −0.3 SD on V* and V_out; "
                 "V_eng may show no deficit or a positive one (novelty). P10: incumbents' V* not changed beyond the placebo band.")
    if "CC" in types:
        p.append(f"- **CC ({n('CC')} chat cut(s)), card P6:** |ΔV| < 0.3 SD on V_out and V_rel (chat has low value for individual output); "
                 "ΔV < 0 on V_eng (chat triggers activity). A V_out ΔV ≤ −0.3 SD with z ≤ −2 counts against P6.")
    if ncf:
        p.append(f"- **Context erasure ({ncf} forced / {ncv} voluntary consolidations), card P5:** writes drop more after forced than after "
                 "voluntary consolidations (dip_CF − dip_CV < 0, 95% CI excluding 0); within forced ones, a larger stored-transfer dose "
                 "goes with a smaller dip (Spearman ρ > 0).")
    if unit == "38":
        p.append("- **NE18 (2026-04-20), card P7:** heavier pre-04-20 searchers gain more V* after the widening (slope > 0); expected n.s.")
    p.append("**Verdict rule:** *supported* if every primary prediction with ≥ 1 usable event has the predicted sign and none is "
             "significantly opposite (|z| ≥ 2 the wrong way); *failed* if any primary prediction is significantly opposite; *mixed* otherwise; "
             "*descriptive* if the period has only MR/MG events.")
    return "\n".join(p)


def write_predict():
    units = sorted(set(cat["unit"].to_list()) | set(ce["unit"].unique().to_list()),
                   key=lambda u: (int(re.match(r"\d+", u).group()), u))
    made = []
    for unit in units:
        reg, d0, d1, ndays, nag = period_line(unit)
        tbl, e = events_table(unit)
        c = ce.filter(pl.col("unit") == unit)
        ncf, ncv = int((c["kind"] == "CF").sum()), int((c["kind"] == "CV").sum())
        gno = int(re.match(r"\d+", unit).group())
        title = goal_titles.get(gno, "")
        role = "exploratory (round 1, non-holdout)"
        split = " Split at the 2026-03-24 regime boundary (NE14 F)." if unit.startswith("36") else ""
        txt = f"""# H15 × {folder_name(unit)}: {title} ({d0} → {d1}, non-holdout days)
<!-- GENERATED by analysis/write_period_folders.py --predict ({PRED_DATE}); Result appended by --results -->

**Verdict:** pending
**Role:** {role}
**Period:** regime {reg} · {nag} agents with a viability value · {ndays} non-holdout active days.{split}

## Why this period
It contains natural scrambles from the H15 catalog (detected from scramble variables only: memory sizes and hashed-line overlap, roster joins, exposure share, consolidation turn counts).

## Scramble events
{tbl if tbl else "No day-level events."}
{"" if not ncf else f"Context erasures: {ncf} forced (41–42-turn cap) and {ncv} voluntary consolidations with both 10-turn windows on the same day."}

## Prediction
{prediction_text(unit, e, reg, ncf, ncv)}

## Result
*(pending: filled by `--results` after `run_scrambles.py`)*

## Notes
- Agent narration is not used; all variables come from logged actions, events, memory sizes and exposure.
"""
        d = HYP / folder_name(unit)
        d.mkdir(exist_ok=True)
        (d / "README.md").write_text(txt)
        made.append(folder_name(unit))
    print("wrote", len(made), "period folders:", " ".join(made))


def fmt(x, nd=2, sign=True):
    if x is None or x != x:
        return "–"
    return f"{x:+.{nd}f}" if sign else f"{x:.{nd}f}"


def write_results():
    res = json.loads((OUT / "results.json").read_text())
    for unit, ur in res["per_unit"].items():
        d = HYP / folder_name(unit)
        p = d / "README.md"
        if not p.exists():
            continue
        txt = p.read_text()
        head, _, _ = txt.partition("## Result\n")
        notes = txt.split("## Notes\n", 1)[1] if "## Notes\n" in txt else ""
        lines = []
        for typ in ("ML", "MG", "MR", "CC", "MN", "SPILL"):
            if typ not in ur:
                continue
            lines.append(f"\n**{typ}** (n events used per V in brackets; effect = period mean − placebo mean, in SD; z from the unit-pooled placebo null)\n")
            lines.append("| V | primary ΔV | z | p | ar1 | did | naive | pre-trend | own-agent-null z |")
            lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
            for V, r in ur[typ].items():
                if r is None:
                    continue
                pr = r.get(res["primary"]) or r.get("deficit") or {}
                star = " (V*)" if V == ur.get("V_star") else ""
                lines.append(f"| {V}{star} [{pr.get('n', '–')}] | {fmt(pr.get('effect'))} | {fmt(pr.get('z'), 1)} | "
                             f"{fmt(pr.get('p'), 3, False)} | {fmt((r.get('ar1') or {}).get('effect'))} | "
                             f"{fmt((r.get('did') or {}).get('effect'))} | {fmt((r.get('naive') or {}).get('effect'))} | "
                             f"{fmt((r.get('pretrend') or {}).get('effect'))} | {fmt((r.get('own_null') or {}).get('z'), 1)} |")
        if "CTX" in ur:
            c = ur["CTX"]
            lines.append("\n**Context erasure (turn level; write rate per turn; dip vs the agent-day base rate)**\n")
            lines.append("| Outcome | dip CF | dip CV | CF − CV [95% CI] | pre-window version CF − CV | ρ(stored dose, dip) in CF |")
            lines.append("| --- | --- | --- | --- | --- | --- |")
            for o in ("write", "error"):
                r = c.get(o)
                if not r:
                    continue
                b = r["diff_base"] or {}
                q = r["diff_pre"] or {}
                lines.append(f"| {o} | {fmt(r['dip_cf'], 4)} | {fmt(r['dip_cv'], 4)} | {fmt(b.get('est'), 4)} "
                             f"[{fmt(b.get('lo'), 4)}, {fmt(b.get('hi'), 4)}] | {fmt(q.get('est'), 4)} | "
                             f"{fmt(r['rho_dose_dip'], 3)} (n {r['n_rho']}) |")
            ph = c.get("posthoc_rd") or {}
            if ph:
                lines.append("\n*Post-hoc (added after the P5 result; exploratory):* exogenous-timing comparison, writes in turns +1…+10 "
                             "relative to turns −20…−11 of the same segment: " +
                             "; ".join(f"{k} {fmt(v['rel_dip'])} [{fmt(v['lo'])}, {fmt(v['hi'])}] (n {v['n']})" for k, v in ph.items()) +
                             ". Forced consolidations wipe the context at the 41-turn cap regardless of task state, so their row is the cleaner estimate of the cost of losing the context window.")
        if "NE18" in ur:
            r = ur["NE18"]
            lines.append("\n**NE18 (history-search widening, 04-20):** slope of Δu on pre-period search rate per V: " +
                         "; ".join(f"{V} {fmt(x['slope'])} (perm p {fmt(x['p'], 3, False)}, n {x['n']})" for V, x in r.items()))
        # catalogued day-level events that could not be estimated on V* (no in-period pre window, too few days)
        vs = ur.get("V_star")
        used = set()
        for typ in ("ML", "MG", "MR", "CC"):
            x = (ur.get(typ) or {}).get(vs) or {}
            used |= {(typ, e["agent"], e["pt_date"]) for e in x.get("events", [])}
        x = (ur.get("MN") or {}).get(vs) or {}
        used |= {("MN", e["agent"], e["pt_date"]) for e in x.get("events", [])}
        cu = cat.filter(pl.col("unit") == unit)
        miss = [r for r in cu.iter_rows(named=True) if (r["type"], r["agent"], r["pt_date"]) not in used]
        if miss:
            lines.append("\n**Not estimable on V\\*** (event on the period's first days, fewer than 4 non-event days for the agent, "
                         "or no reference window): " + "; ".join(f"{r['type']} {r['name']} {r['pt_date']}" for r in miss) + ".")
        verdict = ur.get("verdict", "pending")
        lines.append(f"\n**Verdict:** {verdict}. {ur.get('verdict_reason', '')}")
        lines.append("\nSource: `data/processed/H15-semantic-information-scrambles/results.json` (`per_unit['" + unit + "']`); code `analysis/run_scrambles.py`.")
        head = re.sub(r"\*\*Verdict:\*\* [a-z]+", f"**Verdict:** {verdict}", head, count=1)
        p.write_text(head + "## Result\n" + "\n".join(lines) + "\n\n## Notes\n" + notes)
    # folders whose events were all non-estimable
    for d in sorted(HYP.glob("G*/README.md")):
        txt = d.read_text()
        if "**Verdict:** pending" not in txt:
            continue
        unit = d.parent.name[1:].lstrip("0") or "0"
        cu = cat.filter(pl.col("unit") == unit)
        head, _, _ = txt.partition("## Result\n")
        notes = txt.split("## Notes\n", 1)[1] if "## Notes\n" in txt else ""
        body = ("No catalogued event in this period could be estimated on any viability candidate (every event falls in the "
                "period's first days, or the agent has fewer than 4 non-event days in the period, or the period has fewer than "
                "3 agents with a value): " + "; ".join(f"{r['type']} {r['name']} {r['pt_date']}" for r in cu.iter_rows(named=True)) +
                ".\n\n**Verdict:** n/a.")
        head = head.replace("**Verdict:** pending", "**Verdict:** n/a", 1)
        d.write_text(head + "## Result\n" + body + "\n\n## Notes\n" + notes)
    print("results written into period folders")


if __name__ == "__main__":
    if "--predict" in sys.argv:
        write_predict()
    if "--results" in sys.argv:
        write_results()
