"""Write H41 goal-period / NE READMEs.

  uv run python hypotheses/H41-readout-light-cone/analysis/write_period_cards.py --phase predict   # before the real-data run
  uv run python hypotheses/H41-readout-light-cone/analysis/write_period_cards.py --phase results   # after explore + native

Replication READMEs are templated on purpose (layer 1) and say so. Native READMEs (G31, G38, G51, NE42) carry their own
design text. The results phase rewrites Verdict / Result / Scorecard and keeps the prediction section verbatim.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HDIR = ROOT / "hypotheses/H41-readout-light-cone"
PDIR = HDIR / "goalperiod-subhypotheses"
SH = ROOT / "data/processed/shared"
RES = ROOT / "data/processed/H41-readout-light-cone/results"
ELIGIBLE = [5, 6, 7, 8, 10, 11, 12, 13, 16, 17, 18, 19, 20, 21, 23, 24, 25, 26, 27, 30, 31, 33, 35, 36, 37, 38, 39, 40, 41,
            42, 44, 51]
NATIVE = {31, 38, 51}
STAMP = "2026-10-04 06:16 UTC"


def titles() -> dict:
    t = {}
    for line in (ROOT / "hypotheses/hypohypotheses/goal-periods.md").read_text().splitlines():
        m = re.match(r"^### (\d+) · (.+)$", line)
        if m:
            t[int(m.group(1))] = m.group(2).strip()
    return t


def period_info() -> dict:
    pu = pl.read_parquet(SH / "period_units.parquet").filter(~pl.col("holdout"))
    info = {}
    for g in ELIGIBLE:
        u = pu.filter(pl.col("goal_no") == g)
        info[g] = dict(first=u["first_day"].min(), last=u["last_day"].max(), n_days=int(u["n_days"].sum()),
                       regime="/".join(sorted(set(u["regime"].to_list()))), n_agents=int(u["n_agents"].max()),
                       rooms=sorted({r for rr in u["rooms"].to_list() for r in rr}), units=u["unit_id"].to_list())
    return info


def bound(regime: str):
    return (0.10, 0.15) if regime == "I" else (0.05, 0.08)


def replication_prediction(g, inf):
    a_rob, a_best = bound(inf["regime"].split("/")[-1] if inf["regime"] != "I" else "I")
    two = len([r for r in inf["rooms"] if r != 0]) >= 2 or inf["rooms"] == [4]
    cyc = "≤ 5 receiving calls" if inf["regime"] == "I" else "≥ 10 receiving calls"
    lines = [
        f"*Written {STAMP}, before running on this period (templated replication prediction, layer 1; the card's P1–P8 with amendments A1–A5 as they apply here).*",
        f"- **P1 / A1 (gating):** J_in = h(first post-entry talk call) / h(in-flight talk call) > 1, day-bootstrap lower CI > 1 (if powered: ≥ 100 in-room pre-entry at-risk calls, ≥ 20 in-room adoptions at o = 1).",
        f"- **P2:** robust acausal share A_rob ≤ {a_rob:.2f} and A (best) ≤ {a_best:.2f}; for the verdict (A4) the within-room A_rob must meet the {a_rob:.2f} bound.",
        f"- **P3 (reported, not in the verdict; A3):** A among early adoptions below the time-shuffled null.",
        ("- **P4:** two rooms: ≥ 90% of cross-room adopters unreachable on the pre-item read-out graph (h = ∞, W = 4 h), so V − A ≈ the cross-room share."
         if two and g != 40 else "- **P4:** one room: static hops h = 1 for almost all adopters, so V ≈ A."),
        f"- **P5:** median cycles per hop {cyc}; talk calls per hop 1–2.",
        "- **P6:** where ≥ 200 hop events: b > 0 (CI excluding 0), b ∈ [0.5, 1.5], c > −0.2.",
        "- **P7:** ≥ 50% of robustly acausal adoptions have an identified channel.",
        "- **P8:** h(in-flight) ≤ h(o = 1)/3 (the same J_in, read as rooms vs interaction graph).",
        "- **Verdict rule (A4):** supported = J_in lower CI > 1 and within-room A_rob within the bound; failed = J_in powered with CI including 1 or below; mixed = J_in passes but within-room A_rob exceeds the bound; n/a = J_in not powered.",
    ]
    return "\n".join(lines)


NATIVE_TEXT = {
    38: dict(
        why="""**Native test: the two-room cage.** #38 is the largest two-room period (#best / #rest, 17 non-holdout days, regime III). The room split is a known cut of the read-out graph: an item can cross only through a room-mover, a human posting in both rooms, or an unlogged channel (shared repos and sites, the web, memory, history search). Cross-room adoptions are therefore a direct probe of unlogged channels (HH157's artifact leak). The replication numbers are reported as well.""",
        pred="""*Written 2026-10-04 ~06:00 UTC (card, "Native tests"), before any real-data run.* Cross-room adoption = the adopter was in the other room than the source at t0.
- **G38-a:** ≥ 80% of cross-room adoptions are outside the logged cone at use.
- **G38-b:** the cross-room adoption hazard per at-risk talk call within 2 h is ≤ 1/5 of the within-room hazard.
- **G38-c:** among robustly acausal cross-room adoptions, shared artifact + web explain ≥ 30%, more than among within-room acausal adoptions.
- **G38-d:** median wall time to cross-room adoption ≥ 3× the within-room median.
- **Verdict:** supported if a, b and c hold; failed if a or b fails; mixed otherwise. Prior 0.4.
- Replication predictions (templated) also apply; see the card."""),
    31: dict(
        why="""**Native test: the regime-I clock.** In regime I, chat-mode calls are *scheduled* (logged starts a median 55 s after the previous end; start-to-start ≈ 74 s), not chained, and H08 found that regime-I calls producing chat may be unlogged. Which clock makes adoption delays homogeneous across agents (wall seconds, all receiving calls, or chat-mode calls) tests whether the call cycle is the unit of propagation. #31 is a one-room regime-I week with 11–12 agents and dense chat. The replication numbers are reported as well.""",
        pred="""*Written 2026-10-04 ~06:00 UTC (card, "Native tests"), before any real-data run.*
- **G31-a:** J_in > 1 (lower CI > 1), but smaller than the regime-III median J_in.
- **G31-b:** median cycles per hop ≤ 5 receiving calls and ≤ 2 chat-mode calls.
- **G31-c (clock test):** across adopters with ≥ 5 hop events, the between-agent SD of log median hop delay is smaller in receiving calls than in wall seconds.
- **Verdict:** supported if a and c hold; failed if c fails and J_in's CI includes 1; mixed otherwise. Prior 0.45."""),
    51: dict(
        why="""**Native test: isolation and hopping rooms.** #51 (21–29 agents, regime III) has agents alone in onboarding rooms (NE32's Sol/Terra/Luna rooms on 07-09, Grok 4.5's on 07-10) and frequent hops between #general and #focus from 08-05. An agent alone in a room has no logged input from other agents, so every #general-novel item it uses there is outside the logged cone: a ground-truth "no logged channel" condition. #51 also has the widest cadence spread for the cadence-vs-volume test. The replication numbers are reported as well.""",
        pred="""*Written 2026-10-04 ~06:00 UTC (card, "Native tests"), before any real-data run.*
- **G51-a:** every adoption of a #general-novel item by an agent alone in a room is acausal (by construction), and ≥ 50% of them have an identified channel.
- **G51-b:** #general ↔ #focus cross-room adoptions are mostly inside the logged cone (≥ 70%): hoppers bridge on minute scales.
- **G51-c:** cadence regression b ∈ [0.5, 1.5] with CI excluding 0, and c > −0.2.
- **Verdict:** supported if b and c hold and a's channel share ≥ 50% (or a has < 5 events); failed if c fails with b ≈ 0; mixed otherwise. Prior 0.35."""),
}

NE42_TEXT = dict(
    header="# H41 × NE42: #best/#rest merge and split, A-B-A on graph distance (#39 → #40 → #41)",
    why="""**Native test across a natural experiment (exception (c): the transition is the object).** On 2026-05-04 #best and #rest were merged into #universe-coordination (GPT-5 stayed alone in #rest) and on 05-11 split back to the same partition. Hop distance between the two former groups drops from ≥ 2 (or ∞) on the read-out graph to 1 and back. Groups = room in #39 (just before the merge) and, for #41, room just after the split. Goal confound: #40 (connect worlds) had a shared cross-world objective.""",
    pred="""*Written 2026-10-04 ~06:00 UTC (card, "Native tests"), before any real-data run.*
- **NE42-a:** the cross-group adoption hazard per at-risk talk call (2 h horizon) in #40 is ≥ 3× its value in both #39 and #41.
- **NE42-b:** cross-group acausal share ≥ 70% in #39 and #41; in #40 within 0.05 of the within-group acausal share.
- **NE42-c:** within-group cycles per hop change by < 30% across the three periods (the merge changes distance, not cadence).
- **Verdict:** supported if a and b hold; failed if a fails; mixed otherwise. Prior 0.55.""")


def write_predict():
    tt = titles()
    info = period_info()
    for g in ELIGIBLE:
        inf = info[g]
        d = PDIR / f"G{g:02d}"
        (d / "figures").mkdir(parents=True, exist_ok=True)
        role = "native (exploratory)" if g in NATIVE else "replication (exploratory)"
        head = f"# H41 × G{g:02d}: {tt.get(g, '')} ({inf['first']} → {inf['last']})"
        per = (f"**Period:** regime {inf['regime']} · up to {inf['n_agents']} agents · rooms {inf['rooms']} · {inf['n_days']} non-holdout days"
               f" · units {', '.join(inf['units'])}.")
        if g in NATIVE:
            why, pred = NATIVE_TEXT[g]["why"], NATIVE_TEXT[g]["pred"] + "\n\n**Replication layer (templated):**\n" + replication_prediction(g, inf)
        else:
            why = "A replication point for the common estimator (layer 1): every eligible goal period gets the same statistics, so periods are comparable points on a phase diagram, not independent tests."
            pred = replication_prediction(g, inf)
        txt = f"""{head}

**Verdict:** pending
**Role:** {role}
{per}

## Why this period
{why}

## Prediction
{pred}

## Result
*Pending.*

## Scorecard (period-specific axes)
*Pending.*

## Notes
- Data: `data/processed/H41-readout-light-cone/G{g:02d}/`.
"""
        (d / "README.md").write_text(txt)
    d = PDIR / "NE42"
    (d / "figures").mkdir(parents=True, exist_ok=True)
    (d / "README.md").write_text(f"""{NE42_TEXT['header']}

**Verdict:** pending
**Role:** native (exploratory)
**Boundaries:** 2026-05-04 merge (#39 → #40), 2026-05-11 split (#40 → #41). Periods #39, #40, #41 (all non-holdout, regime III).

## Why this natural experiment
{NE42_TEXT['why']}

## Prediction
{NE42_TEXT['pred']}

## Result
*Pending.*

## Scorecard (period-specific axes)
*Pending.*

## Notes
- Data: `data/processed/H41-readout-light-cone/G39/`, `G40/`, `G41/`; results in `results/native.json`.
""")
    print("predict phase written:", len(ELIGIBLE) + 1, "folders")


# ------------------------------------------------------------------------------------------------ results
def fmt(x, nd=2):
    if x is None or (isinstance(x, float) and (math.isnan(x))):
        return "–"
    if isinstance(x, float) and math.isinf(x):
        return "∞"
    return f"{x:.{nd}f}"


def ci(lo, hi, nd=2):
    return f"[{fmt(lo, nd)}, {fmt(hi, nd)}]"


def replace_section(text, name, body):
    pat = re.compile(rf"(## {re.escape(name)}\n)(.*?)(?=\n## |\Z)", re.S)
    return pat.sub(lambda m: m.group(1) + body.strip() + "\n", text, count=1)


def set_verdict(text, v):
    return re.sub(r"^\*\*Verdict:\*\*.*$", f"**Verdict:** {v}", text, count=1, flags=re.M)


def verdict_posthoc(r):
    reg = r["regime"]
    b = 0.10 if reg == "I" else 0.05
    if not r.get("powered_in"):
        return "n/a"
    jm, jl = r.get("J_mh"), r.get("J_mh_lo")
    if jm is not None and math.isinf(jm):  # no in-flight adoptions at matched delays: use the Haldane-corrected J_in CI
        jl = r.get("J_in_ci_lo")
    if not ((jl or 0) > 1):
        return "failed"
    return "mixed" if (r.get("acaus_rob_within") or 0) > b else "supported"


def verdict_rep(r):
    reg = r["regime"]
    a_rob_b = 0.10 if reg == "I" else 0.05
    if not r.get("powered_in"):
        return "n/a", a_rob_b
    jl = r.get("J_in_ci_lo")
    within = r.get("acaus_rob_within")
    if jl is None or not (jl > 1):
        return "failed", a_rob_b
    if within is not None and within > a_rob_b:
        return "mixed", a_rob_b
    return "supported", a_rob_b


def result_block(r):
    v, b = verdict_rep(r)
    rows = [
        ("P1/A1 J_in (in-flight vs first post-entry talk call)",
         f"{fmt(r.get('J_in'))} {ci(r.get('J_in_ci_lo'), r.get('J_in_ci_hi'))}; h(in-flight) {fmt(r.get('h_pre_in'), 4)} "
         f"(n {r.get('risk_pre_in')}), h(o=1) {fmt(r.get('h_o1_in_h'), 4)} (n {r.get('risk_o1_in')})",
         "field synthetic J_in 0.4–0.6", "pass" if (r.get("J_in_ci_lo") or 0) > 1 else ("n/a" if not r.get("powered_in") else "fail")),
        ("A6 (post hoc) delay-matched J_mh", f"{fmt(r.get('J_mh'))} {ci(r.get('J_mh_lo'), r.get('J_mh_hi'))}; lenient cone {fmt(r.get('J_mh_len'))}; "
         f"by class U/D/N/W: {fmt(r.get('J_mh_U'))} / {fmt(r.get('J_mh_D'))} / {fmt(r.get('J_mh_N'))} / {fmt(r.get('J_mh_W'))}",
         "field synthetic 0.8–1.2", "pass" if (r.get("J_mh_lo") or 0) > 1 else "fail"),
        ("P2 acausal share A (best) / A_rob", f"{fmt(r.get('acaus'), 3)} {ci(r.get('acaus_ci_lo'), r.get('acaus_ci_hi'), 3)} / {fmt(r.get('acaus_rob'), 3)}; within-room A_rob {fmt(r.get('acaus_rob_within'), 3)}",
         f"bound {b:.2f}", "pass" if (r.get("acaus_rob") or 0) <= b else "fail"),
        ("P3 early A vs time-shuffled null (A3: not in verdict)", f"{fmt(r.get('acaus_early'), 3)} vs {fmt(r.get('p_jit_early'), 3)}",
         "null", "below" if (r.get("acaus_early") or 0) < (r.get("p_jit_early") or 0) else "not below"),
        ("P4 static V = P(n < h), parts h=1&n=0 / 2≤h<∞ / h=∞", f"{fmt(r.get('v4'), 3)} = {fmt(r.get('v4_h1_n0'), 3)} / {fmt(r.get('v4_hmid'), 3)} / {fmt(r.get('v4_hinf'), 3)}; cross-room share {fmt(r.get('share_cross'), 3)}",
         "", ""),
        ("P5 cycles per hop (receiving / talk calls)", f"{fmt(r.get('cyc_med'), 0)} / {fmt(r.get('talk_med'), 1)} (n {r.get('n_hops')}); v = {fmt(r.get('v'), 3)} hops per call", "", ""),
        ("P6 cadence b, volume c", f"b {fmt(r.get('b'))} {ci(r.get('b_ci_lo'), r.get('b_ci_hi'))}, c {fmt(r.get('c'))} {ci(r.get('c_ci_lo'), r.get('c_ci_hi'))} (n {r.get('n_reg')})", "R4: b≈0, c<0", ""),
        ("P7 identified channels (robust acausal)", f"{fmt(r.get('acaus_rob_identified'))} of {r.get('acaus_rob_n')}",
         f"in-cone controls {fmt(r.get('control_identified'))}", "non-specific" if (r.get('control_identified') or 0) >= (r.get('acaus_rob_identified') or 0) else ""),
    ]
    t = "| Test | Observed | Null / reference | Verdict |\n| --- | --- | --- | --- |\n"
    t += "\n".join(f"| {a} | {b_} | {c} | {d} |" for a, b_, c, d in rows)
    return v, t


def write_results():
    pt = pl.read_parquet(RES / "period_table.parquet")
    nat = json.loads((RES / "native.json").read_text())
    for r in pt.iter_rows(named=True):
        g = r["goal"]
        p = PDIR / f"G{g:02d}" / "README.md"
        if not p.exists():
            continue
        r["h_o1_in_h"] = (r["adopt_o1_in"] / r["risk_o1_in"]) if r.get("risk_o1_in") else None
        v, tab = result_block(r)
        txt = p.read_text()
        body = (f"Run 2026-10-04 (`analysis/explore.py`; data `data/processed/H41-readout-light-cone/G{g:02d}/`). "
                f"{r['n_items']} novel items, {r['n_adopt']} adoptions.\n\n" + tab
                + f"\n\nVerdict by the pre-registered rule A4 (J_in): **{v}**. Post-hoc verdict with the delay-matched J_mh (A6): "
                  f"**{verdict_posthoc(r)}**.")
        sc = (f"- C (adequacy): J_in {'beats' if (r.get('J_in_ci_lo') or 0) > 1 else 'does not beat'} the field/room null (in-flight hazard).\n"
              f"- D (unfitted): acausal share {fmt(r.get('acaus'), 3)}; cycles per hop {fmt(r.get('cyc_med'), 0)}.\n")
        if g in NATIVE:
            nv = nat[f"G{g}"]
            body = native_block(g, nv) + "\n\n**Replication layer:**\n\n" + body
            v = nv["verdict"][0] if isinstance(nv["verdict"], list) else nv["verdict"]
            sc += native_score(g, nv)
        txt = set_verdict(txt, v)
        txt = replace_section(txt, "Result", body)
        txt = replace_section(txt, "Scorecard (period-specific axes)", sc)
        p.write_text(txt)
    rows = []
    for r in pt.sort("goal").iter_rows(named=True):
        g = r["goal"]
        role = "native" if g in NATIVE else "replication"
        v = nat[f"G{g}"]["verdict"] if g in NATIVE else verdict_rep(r)[0]
        v = v[0] if isinstance(v, list) else v
        rows.append(f"| [G{g:02d}](goalperiod-subhypotheses/G{g:02d}/README.md) | {role} | {v} (post hoc {verdict_posthoc(r)}) | "
                    f"regime {r['regime']}; {r['n_adopt']} adoptions; J_in {fmt(r.get('J_in'))} {ci(r.get('J_in_ci_lo'), r.get('J_in_ci_hi'))}; "
                    f"J_mh {fmt(r.get('J_mh'))} {ci(r.get('J_mh_lo'), r.get('J_mh_hi'))}; A_rob {fmt(r.get('acaus_rob'), 3)} "
                    f"(within-room {fmt(r.get('acaus_rob_within'), 3)}, cross-room {fmt(r.get('acaus_rob_cross'), 2)}); "
                    f"cycles/talk calls per hop {fmt(r.get('cyc_med'), 0)}/{fmt(r.get('talk_med'), 1)} |")
    nv = nat["NE42"]
    rows.append(f"| [NE42](goalperiod-subhypotheses/NE42/README.md) | native | {nv['verdict']} | cross-group hazard #40/#39 "
                f"×{fmt(nv['a_ratio_40_39'], 0)}, #40/#41 ×{fmt(nv['a_ratio_40_41'], 0)}; cross-group acausal "
                f"{fmt(nv['G39']['acaus_cross'])} / {fmt(nv['G40']['acaus_cross'])} / {fmt(nv['G41']['acaus_cross'])} |")
    (RES / "card_table.md").write_text("| Period | Role | Verdict | Key numbers |\n| --- | --- | --- | --- |\n" + "\n".join(rows) + "\n")
    # NE42
    p = PDIR / "NE42" / "README.md"
    nv = nat["NE42"]
    txt = set_verdict(p.read_text(), nv["verdict"])
    txt = replace_section(txt, "Result", native_block("NE42", nv))
    txt = replace_section(txt, "Scorecard (period-specific axes)", native_score("NE42", nv))
    p.write_text(txt)
    print("results written")


def native_block(g, nv):
    if g == 38:
        vv = nv["verdict"]
        return f"""**Native test (G38 cage), verdict: {vv[0]}** (checks {vv[1]}).

| Test | Observed | Prediction | Verdict |
| --- | --- | --- | --- |
| a: cross-room adoptions outside the logged cone | {fmt(nv['a_cross_out_of_cone'])} (lenient {fmt(nv['a_cross_out_of_cone_rob'])}); {nv['n_cross']} of {nv['n_adopt']} adoptions are cross-room | ≥ 0.80 | {'pass' if vv[1]['a'] else 'fail'} |
| b: cross / within hazard per talk call (2 h) | {fmt(nv['b_ratio'], 3)} {ci(*nv['b_ratio_ci'], 3)}; h_out {fmt(nv['h_out'], 4)}, h_in {fmt(nv['h_in'], 4)} | ≤ 0.20 | {'pass' if vv[1]['b'] else 'fail'} |
| c: artifact + web among robust acausal, cross vs within | {fmt(nv.get('c_cross_artweb'))} (n {nv.get('c_cross_n')}) vs {fmt(nv.get('c_within_artweb'))} (n {nv.get('c_within_n')}) | ≥ 0.30 and > within | {'pass' if vv[1]['c'] else 'fail'} |
| d: median delay cross / within | {fmt(nv['d_med_delay_cross_s'] / 60, 1)} / {fmt(nv['d_med_delay_within_s'] / 60, 1)} min (ratio {fmt(nv['d_ratio'], 1)}) | ≥ 3 | {'pass' if nv['d_ratio'] >= 3 else 'fail'} |

Channel mix of robust cross-room violations: {nv.get('c_cross_mix')}. In-cone cross-room adoptions by cone hop count: {nv.get('cross_incone_Htr')}."""
    if g == 31:
        return f"""**Native test (G31 regime-I clock), verdict: {nv['verdict']}** (checks {nv['checks']}).

| Test | Observed | Prediction | Verdict |
| --- | --- | --- | --- |
| a: J_in | {fmt(nv['J_in'])} {ci(*nv['J_in_ci'])} (in-flight at risk {nv['risk_pre_in']}); regime-III median {fmt(nv['J_in_regIII_median'])} | > 1 and < regime-III median | {'pass' if nv['checks']['a'] else 'fail'} |
| b: cycles per hop (receiving / chat-mode / talk calls) | {fmt(nv['cyc_med'], 0)} / {fmt(nv['chat_med'], 1)} / {fmt(nv['talk_med'], 1)} (n {nv['n_hops']}) | ≤ 5 / ≤ 2 | {'pass' if nv['checks']['b'] else 'fail'} |
| c: between-agent SD of log median hop delay (seconds / receiving calls / chat calls) | {fmt(nv.get('sd_log_seconds'))} / {fmt(nv.get('sd_log_calls'))} / {fmt(nv.get('sd_log_chatcalls'))} ({nv.get('clock_n_agents')} agents; calls − seconds {ci(*(nv.get('sd_diff_calls_minus_seconds_ci') or [None, None]))}) | calls < seconds | {'pass' if nv['checks']['c'] else 'fail'} |"""
    if g == 51:
        return f"""**Native test (G51 isolation and hopping rooms), verdict: {nv['verdict']}** (checks {nv['checks']}).

| Test | Observed | Prediction | Verdict |
| --- | --- | --- | --- |
| a: adoptions of #general-novel items by agents alone in a room | {nv['n_isolated']} adoptions (rooms {nv.get('isolated_rooms')}); acausal {fmt(nv.get('a_isolated_acausal'))}; identified channel {fmt(nv.get('a_isolated_identified'))}; mix {nv.get('a_isolated_mix')} | all acausal; ≥ 0.5 identified | {'pass' if nv['checks']['a_iso_channels'] else 'fail'} |
| b: #general ↔ #focus cross-room adoptions inside the cone | {fmt(nv.get('b_focus_cross_incone'))} (lenient {fmt(nv.get('b_focus_cross_incone_rob'))}; n {nv.get('n_focus_cross')}); by hop count {nv.get('b_focus_Htr')} | ≥ 0.70 | {'pass' if nv['checks']['b_focus'] else 'fail'} |
| c: cadence b, volume c | b {fmt(nv.get('cad_b'))} {ci(nv.get('cad_b_lo'), nv.get('cad_b_hi'))}, c {fmt(nv.get('cad_c'))} {ci(nv.get('cad_c_lo'), nv.get('cad_c_hi'))} (n {nv.get('cad_n_reg')}) | b ∈ [0.5, 1.5], CI > 0; c > −0.2 | {'pass' if (nv['checks']['c_cadence_b'] and nv['checks']['c_cadence_c']) else 'fail'} |"""
    if g == "NE42":
        rows = []
        for gg in ("G39", "G40", "G41"):
            x = nv[gg]
            rows.append(f"| {gg} | {fmt(x['h_cross'], 4)} (n {x['risk_cross']}) | {fmt(x['h_within'], 4)} (n {x['risk_within']}) | {fmt(x['ratio_cross_within'], 3)} {ci(*x['ratio_ci'], 3)} | {fmt(x['acaus_cross'])} (n {x['n_cross']}) | {fmt(x['acaus_within'])} | {fmt(x['cyc_med_within'], 0)} |")
        return f"""Run 2026-10-04 (`analysis/native.py`). **Verdict: {nv['verdict']}** (checks {nv['checks']}).

| Period | cross-group hazard per talk call (2 h) | within-group hazard | ratio | cross-group acausal share | within-group acausal | within-group cycles per hop |
| --- | --- | --- | --- | --- | --- | --- |
{chr(10).join(rows)}

- **NE42-a:** cross-group hazard #40 / #39 = {fmt(nv['a_ratio_40_39'], 2)} {ci(*nv['a_ratio_40_39_ci'])}; #40 / #41 = {fmt(nv['a_ratio_40_41'], 2)} {ci(*nv['a_ratio_40_41_ci'])} (prediction ≥ 3 for both): {'pass' if nv['checks']['a'] else 'fail'}.
- **NE42-b:** {'pass' if nv['checks']['b'] else 'fail'}. **NE42-c:** {'pass' if nv['checks']['c'] else 'fail'}."""
    return ""


def native_score(g, nv):
    if g == 38:
        return "- E/G: the room cut is known structure; cross-room spread outside the logged cone tests the cage (G).\n"
    if g == 31:
        return "- B: the call-unit (clock) assumption in regime I.\n"
    if g == 51:
        return "- G: isolated agents are a no-logged-input ground truth.\n"
    if g == "NE42":
        return "- E (interventional): the merge/split A-B-A on hop distance.\n"
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["predict", "results"], required=True)
    a = ap.parse_args()
    if a.phase == "predict":
        write_predict()
    else:
        write_results()


if __name__ == "__main__":
    main()
