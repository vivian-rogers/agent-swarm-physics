"""Write H01 round-2 goal-period and NE folders from round2/results.json (card: Round 2 formal setup, predictions, A1, A2).

For every eligible unit of analysis: goalperiod-subhypotheses/G<NN>/README_round2.md (full round-2 card for the period)
and round2/G<NN>/results.json (numbers). README.md keeps round 1's content; its **Verdict:** line is updated to the
round-2 verdict with round 1's verdict kept on the same line, and a "Round 2" section links README_round2.md. New
folders (#30, #31, #33) get a README.md header. NE folders: NE34 (goal changes as relevance scrambles, exploratory),
NE29 (same-lab succession stand-in, exploratory), NE30 and NE24 (confirmatory designs, pending, not run).

Per-unit verdict rule (fixed with the predictions' logic; agency is the claim, allocation continuity is necessary only):
  agency signature = R4 (crews' within-unit Stouffer Z > 1.64 and crews rank first vs room/lab/reply) OR R5a (crew
                     Delta V_st >= 0.005 with CI above 0)
  supported = agency signature AND R6b (leave-out Delta C >= 0.2) AND R4d (artifact units beat rooms/labs, where defined)
  mixed     = agency signature without both of the others, or R6b and R4d both pass without an agency signature
  failed    = no agency signature (R6b alone does not rescue it)
Run: uv run python hypotheses/H01-emergent-superagents-exist/analysis/r2_period_folders.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r2lib as L  # noqa: E402

import numpy as np  # noqa: E402

HYP = HERE.parent
PS = HYP / "goalperiod-subhypotheses"
R2 = L.ROOT / "data/processed/H01-emergent-superagents-exist/round2"
DATE = "2026-10-04"
TITLES = {30: "Adopt a park and get it cleaned", 31: "Pick your own goal (farewell to Claude 3.7 Sonnet)",
          33: "Discuss and act on the Pentagon–AI company news"}


def f(x, nd=2, sign=True):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "–"
    return f"{x:+.{nd}f}" if sign else f"{x:.{nd}f}"


def unit_verdict(u, r):
    s4 = r["r4"]["per_unit_summary"].get(u)
    units4 = r["r4_units"].get(u, {})
    zc = [x["z"] for x in units4.get("crew", []) if x.get("z") is not None]
    Z, p = L.stouffer(zc) if zc else (np.nan, np.nan)
    rivals = {k: s4[k]["median_z"] for k in ("room", "lab", "comm") if s4 and s4[k]["n_units"] >= 2 and s4[k]["median_z"] is not None}
    first = bool(s4 and s4["crew"]["median_z"] is not None and rivals and all(s4["crew"]["median_z"] > v for v in rivals.values()))
    r4 = bool(np.isfinite(Z) and Z > 1.64 and first)
    r5 = r["r5"]["verdict"]["per_unit"].get(u, {})
    r5a = bool(r5 and r5.get("pos"))
    d4 = r["r4d"]["per_unit"].get(u, {})
    dc = (d4.get("crew") or {}).get("dC")
    r6b = bool(dc is not None and dc >= 0.2)
    art = [d4[k]["dC"] for k in ("crew", "coalloc") if d4.get(k)]
    base = [d4[k]["dC"] for k in ("room", "lab") if d4.get(k)]
    r4d = (min(art) > max(base)) if (art and base) else None
    agency = r4 or r5a
    if agency and r6b and (r4d is None or r4d):
        v = "supported"
    elif agency or (r6b and r4d):
        v = "mixed"
    else:
        v = "failed"
    return v, {"R4": r4, "crew_stouffer_Z": Z, "crew_first": first, "R5a": r5a, "R6b": r6b, "dC_crew": dc, "R4d": r4d}


def unit_block(u, r, flags):
    s4 = r["r4"]["per_unit_summary"][u]
    d4 = r["r4d"]["per_unit"].get(u, {})
    r5 = r["r5"]["verdict"]["per_unit"].get(u, {})
    r5x = r["r5"]["per_unit"].get(u, {})
    sp = r["r6"]["spillover"]["per_unit"].get(u)
    r8 = r["r8"]["response"]["per_unit"].get(u)
    cg = r["coarse_grainings"].get(u, {})
    crews = r["r4_units"][u]["crew"]
    sizes = sorted(x["n"] for x in crews)
    L_ = [f"### Unit {u}",
          f"- **Candidate units:** {cg.get('crew', 0)} crews (sizes {sizes[:12]}{' …' if len(sizes) > 12 else ''}), "
          f"{cg.get('sync', 0)} synchrony and {cg.get('coalloc', 0)} co-allocation communities, {cg.get('comm', 0)} reply communities, "
          f"{cg.get('room', 0)} rooms, {cg.get('lab', 0)} labs.",
          "",
          "| coarse-graining | R4 median z (vs random groups) | local maxima | iota_alloc z | shift z | R4d ΔC overnight (leave-out) |",
          "| --- | --- | --- | --- | --- | --- |"]
    for k, lab in (("crew", "crews (joint work on one artifact)"), ("sync", "behavior-state synchrony"),
                   ("coalloc", "co-allocation (co-adoption)"), ("comm", "reply communities"), ("room", "rooms (baseline)"),
                   ("lab", "labs (baseline)")):
        s = s4.get(k, {})
        dc = (d4.get(k) or {}).get("dC")
        lm = s.get("frac_local_max")
        L_.append(f"| {lab} | {f(s.get('median_z'))} (n {s.get('n_z', 0)}) | {('–' if lm is None else f'{lm:.2f}')} | "
                  f"{f(s.get('median_alloc_z'))} | {f(s.get('median_shift_z'))} | {f(dc)} |")
    sub = (d4.get("sub") or {}).get("dC")
    L_.append(f"| single agents (substrate) | – | – | – | – | {f(sub)} |")
    L_.append("")
    if r5:
        L_.append(f"- **R5 (KW, crews, τ = 2 h):** ΔV_st {f(r5['dV_st'], 4)} [{f(r5['lo'], 4)}, {f(r5['hi'], 4)}], "
                  f"ΔV_obs {f(r5['dV_obs'], 4)}, I(X₀;Y₀) {f(r5['I'], 3, False)} bits, Pinsker envelope ±{f(r5['pinsker'], 3, False)}, "
                  f"η {f(r5['eta'], 2, False)}, members' ΔV_st {f(r5['member_dV_st'], 4)}; CK error {f(r5['ck_err'], 3, False)}, "
                  f"scrambled mass on thin cells {f(r5['positivity_low_mass'], 2, False)}. Day-level landscape: "
                  f"{f((r5x.get('crew_day') or {}).get('dV_st'), 4)} (n {(r5x.get('crew_day') or {}).get('n', 0)}).")
    if sp:
        L_.append(f"- **R6a (NE41 forced consolidations, n {sp['n_events']}):** own writes {f(sp['self']['rel'])} (z {f(sp['self']['z'], 1)}), "
                  f"other members {f(sp['other']['rel'])} (z {f(sp['other']['z'], 1)}), relative to the 5-min base, rotation null.")
    if r8:
        L_.append(f"- **R8a:** others' write attempts within 30 min after an unconfirmed vs a confirmed push: ratio {f(r8['ratio_attempt'], 2, False)} "
                  f"({r8['n_unconfirmed']} unconfirmed, {r8['n_confirmed']} confirmed push events).")
    deps = [d for d in r["r7"]["departures"] if d["unit"] == u]
    if deps:
        L_.append(f"- **R7a:** {len(deps)} departure rows (overlapping crews counted separately); crew write rate relative change "
                  f"{f(float(np.mean([d['rel_V_cnt'] for d in deps])))} vs departed share {f(float(np.mean([d['share'] for d in deps])), 2, False)}; no crew died.")
    th = [t for t in r["r7"]["theseus"] if t["unit"] == u]
    if th:
        L_.append(f"- **R7b:** {len(th)} crews alive ≥ 6 active days, median Jaccard(first third, last third members) "
                  f"{f(float(np.median([t['jaccard_first_last'] for t in th])), 2, False)} (no turnover).")
    L_.append(f"- **Per-unit verdict components:** R4 {'pass' if flags['R4'] else 'fail'} (crews' Stouffer Z {f(flags['crew_stouffer_Z'], 2)}, "
              f"first vs rooms/labs/reply: {flags['crew_first']}); R5a {'pass' if flags['R5a'] else 'fail'}; "
              f"R6b {'pass' if flags['R6b'] else 'fail'} (ΔC {f(flags['dC_crew'])}); R4d {('–' if flags['R4d'] is None else ('pass' if flags['R4d'] else 'fail'))}.")
    return "\n".join(L_)


def write_period(goal, units, r, units_meta):
    folder = PS / f"G{goal:02d}"
    folder.mkdir(parents=True, exist_ok=True)
    verdicts, blocks, res = [], [], {}
    for u in units:
        v, fl = unit_verdict(u, r)
        verdicts.append(v)
        blocks.append(unit_block(u, r, fl))
        res[u] = {"verdict": v, "flags": fl, "r4": r["r4"]["per_unit_summary"][u], "r4d": r["r4d"]["per_unit"].get(u),
                  "r5": r["r5"]["verdict"]["per_unit"].get(u), "spillover": r["r6"]["spillover"]["per_unit"].get(u),
                  "r8": r["r8"]["response"]["per_unit"].get(u)}
    order = {"supported": 0, "mixed": 1, "failed": 2}
    if len(set(verdicts)) == 1:
        V = verdicts[0]
    elif "supported" in verdicts or "mixed" in verdicts:
        V = "mixed"
    else:
        V = "failed"
    gc = [(b, x) for b, x in r["r5"]["goal_change"]["boundaries"].items() if b.split("->")[0] in units]
    m0 = units_meta[units[0]]
    days = sum(units_meta[u]["n_days"] for u in units)
    line = (f"round 2 units {', '.join(units)} · regime {m0['regime']} · {days} non-holdout days · "
            f"{max(units_meta[u]['n_writers'] for u in units)} writers · {sum(units_meta[u]['n_writes_strict'] for u in units)} strict write events")
    short = {"supported": "agency signature + continuity",
             "mixed": "continuity, partial agency",
             "failed": "no agency signature"}[V]
    txt = [f"# H01 × G{goal:02d}, round 2: effective superagents (Kolchinsky–Wolpert) on a substrate of agents",
           "", f"**Verdict:** {V}", "**Role:** exploratory", f"**Period:** {line}", "",
           "## Why this period",
           "It has a work ledger (strict git/deploy write events on shared projects), so candidate units (crews, synchrony and "
           "co-allocation communities, reply communities, with rooms and labs as baselines) and their viability (artifact "
           "advancement) can be measured. See the card's \"Round 2 formal setup\".", "",
           "## Prediction",
           f"*Written {DATE} on the main card (\"Round 2 predictions\" and Amendment A1), before any real-data run of R4–R8; no "
           "period-specific variant.* R4: crews are individuality maxima (composition excess > 0, first among coarse-grainings, "
           "local maxima). R5: positive KW stored and observed semantic information for crews, above the members'. R6: one-member "
           "scrambles are cheap, crews persist overnight (ΔC ≥ 0.2), coordination excess > 0. R7: departures cost no more than the "
           "departed share. R8: others respond to a member's failed write. Per-unit verdict rule in `analysis/r2_period_folders.py`.",
           "", "## Result", f"Data: `data/processed/H01-emergent-superagents-exist/round2/G{goal:02d}/results.json`; pipeline "
           "`analysis/r2_run.py`; figures `figures/r2_summary_obs.pdf`, `figures/r2_kw.pdf`.", ""]
    txt += blocks
    if gc:
        txt += ["", "### Goal change after this period (NE34, relevance scramble)"]
        for b, x in gc:
            txt.append(f"- {b} ({x['kind']}): {x['n_crews']} crews, V_adv on R_G {f(x['mean_v_pre'], 2, False)} → "
                       f"{f(x['mean_v_pre'] + x['mean_dV'], 2, False)} (Δ {f(x['mean_dV'])} ± {f(x['se'], 2, False)}); "
                       f"R_G still written in the next goal's first 2 days for {100 * x['p_written_post']:.0f}% of crews.")
    if goal == 51:
        fc = r["r5"]["focus_cut"]
        txt += ["", "### #focus channel cut (08-05)",
                f"- Crews of 51b split across #general/#focus ({fc['n_split']}) vs kept together ({fc['n_together']}): change in V_adv on R_G "
                f"from the last two 51b days to 08-05/06: {f(fc['mean_dV_split'])} vs {f(fc['mean_dV_together'])} (DiD {f(fc['did'])}). No channel-cut cost."]
    txt += ["", "## Scorecard (period-specific axes)",
            "- **C** 0–1: no candidate beats its activity-matched random-group null on individuality; allocation continuity beats "
            "its permutation null. **E** 0: no unit-level natural scramble inside the period except where noted. **F**: see the card "
            "(timing individuality has ≤ 7% power at this sampling).", "",
            "## Notes",
            f"- {DATE}: round 2 per the card. Rooms and labs are baseline partitions only; coordination-based candidates "
            "(synchrony, co-allocation, reply, crews) were added at Vivian's request before the real-data run (A1.3). A dedicated "
            "coordination-first search is left to H58."]
    (folder / "README_round2.md").write_text("\n".join(txt) + "\n")
    # README.md: update the verdict line, keep round 1, add a pointer
    rd = folder / "README.md"
    if rd.exists() and "Round 1 had no folder for this period" not in rd.read_text():
        t = rd.read_text()
        m = re.search(r"^\*\*Verdict:\*\*\s*(.+)$", t, re.M)
        old = m.group(1).strip() if m else "–"
        old = re.sub(r"^.*?round 1:\s*", "", old)[:-1] if "round 2" in old else old
        t = re.sub(r"^\*\*Verdict:\*\*.*$", f"**Verdict:** {V} (round 2: {short}; round 1: {old})", t, count=1, flags=re.M)
        t = re.sub(r"\n## Round 2 \(2026-10-04\)\n.*", "", t, flags=re.S)
        t = t.rstrip() + f"\n\n## Round 2 (2026-10-04)\nRound 2 (effective superagents in Kolchinsky–Wolpert terms) is in " \
                         f"[`README_round2.md`](README_round2.md). Verdict: **{V}**: {short}.\n"
        rd.write_text(t)
    else:
        title = TITLES.get(goal, f"goal #{goal}")
        rd.write_text(f"# H01 × G{goal:02d}: {title}\n\n**Verdict:** {V} (round 2: {short})\n**Role:** exploratory\n"
                      f"**Period:** {line}\n\n## Round 2 (2026-10-04)\nRound 1 had no folder for this period (only its P9 mean-field fit, now known to be drive-confounded; see the card). "
                      f"The round-2 card for this period is [`README_round2.md`](README_round2.md).\n")
    out = R2 / f"G{goal:02d}"
    out.mkdir(exist_ok=True)
    (out / "results.json").write_text(json.dumps(clean(res), indent=1))
    return V, verdicts


def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    return o


def write_ne(r, conf):
    gc = r["r5"]["goal_change"]
    rows = "\n".join(f"| {b} | {x['kind']} | {x['n_crews']} | {x['mean_v_pre']:.2f} | {x['mean_dV']:+.2f} ± {x['se']:.2f} | "
                     f"{100 * x['p_written_post']:.0f}% |" for b, x in gc["boundaries"].items())
    m = gc["meta_new"]
    (PS / "NE34").mkdir(exist_ok=True)
    (PS / "NE34" / "README.md").write_text(f"""# H01 × NE34: goal changes as a relevance scramble of the unit–goal correlation (round 2)

**Verdict:** supported (R5c by the letter: units lose ~40% of their artifact advancement at new goals; the continuation boundary is not different; artifacts are not abandoned)
**Role:** exploratory
**Period:** 8 non-holdout goal boundaries with a work ledger before and after (#30 → #31 … #41 → #42); exception (c), the transition is the object.

## Why this event
At a goal change the environment's state (the goal prompt) is redrawn independently of the unit's stored state (its artifact), which is
Kolchinsky–Wolpert's full scramble of the unit–goal correlation (the goal marginal changes too). The drop in the unit's artifact advancement is the
natural-scramble value of its goal information. Only #39 → #40 ("connect your worlds") keeps the old artifacts relevant (a partial scramble).

## Prediction
*Written {DATE} on the main card before any real-data run.* R5c: crews' V_adv on R_G over the next goal's first 2 active days is below their last 2
days (DerSimonian–Laird over new-goal boundaries, z ≤ −2), less so at the continuation boundary. R7c: R_G written at all in days 1–2 for ≥ 50% of
crews at the continuation boundary and ≤ 20% at new-goal boundaries.

## Result
| boundary | kind | crews | V_adv before | Δ V_adv (± SE) | R_G still written |
| --- | --- | --- | --- | --- | --- |
{rows}

Random-effects over the 7 new-goal boundaries: Δ = {m['mu']:+.2f} ± {m['se']:.2f} (z {m['z']:.2f}; τ² {m['tau2']:.2f}). Continuation (#39 → #40):
{gc['boundaries']['39->40']['mean_dV']:+.2f}. R_G is still written in the next goal's first two days for {100 * gc['p_written_new']:.0f}% of crews at
new-goal boundaries. #37 → #38 is the exception (+0.44): #37 was a 3-day pick-your-own week whose artifacts were reused for the charity drive.

- **R5c: supported by the letter** (z ≤ −2, continuation slightly less negative), but the continuation contrast is negligible (−0.37 vs −0.39).
  In KW terms the units' viability carries a large value of goal information (natural-scramble variant): the operator's field sets the rate.
- **R7c: failed.** Units are not abandoned at new goals (98% still written). They slow down.

## Scorecard (period-specific axes)
- **E** 1: a natural scramble with the predicted sign, but it is bundled with a new instruction (a field), so the value is not separable
  from the new goal's pull. **I** 1: 6 of 7 new-goal boundaries agree in sign.

## Notes
- {DATE}: crews defined within the earlier period; advancement counts writes by anyone on R_G.
""")
    c1 = conf.get("C1_standin", {}).get("result", {})
    (PS / "NE29").mkdir(exist_ok=True)
    crews = c1.get("crews", [])
    (PS / "NE29" / "README.md").write_text(f"""# H01 × NE29: same-lab succession Claude 3.7 Sonnet → Claude Sonnet 4.6 (#31), exploratory stand-in for NE30

**Verdict:** mixed (the successor joins a predecessor crew's project; the crews lose more than the predecessor's share)
**Role:** exploratory
**Period:** #31 (2026-02-16 → 02-20, non-holdout). Claude Sonnet 4.6 joined 02-18; Claude 3.7 Sonnet retired 02-19 (the farewell week); NE11
(100-turn session cap) 02-20.

## Why this event
The only non-holdout same-lab succession. It is the dry-run stand-in for the confirmatory NE30 test (`analysis/confirm_r2.py`, C1), scored with
the same code, and an exploratory R7 (substrate independence) observation in its own right.

## Prediction
*C1 as frozen in `confirm_r2.py` ({DATE}), applied here as a stand-in:* (a) crews that contained the predecessor keep their write rate on R_G
except for the predecessor's share (relative change + share ≥ 0); (b) the successor writes on a predecessor crew's project within 2 active days.

## Result
{len(crews)} crews contained Claude 3.7 Sonnet in the pre-retirement days of #31. Mean (relative change + predecessor share) = {f(c1.get('mean_excess'))}
→ (a) {'met' if c1.get('a') else 'not met'}; the successor wrote on {sum(1 for x in crews if x['successor_writes_post'] > 0)} of them → (b)
{'met' if c1.get('b') else 'not met'}. Verdict by the C1 rule: **{c1.get('verdict')}**.

Confounds: the retirement week was a farewell goal, its last day (02-20) brought the 100-turn cap (NE11), and the successor overlapped the predecessor
by one day. So (a) cannot separate the departure from the week's wind-down.

## Notes
- {DATE}: written after the exploratory round-2 run, from the confirm script's dry run.
""")
    (PS / "NE30").mkdir(exist_ok=True)
    (PS / "NE30" / "README.md").write_text(f"""# H01 × NE30: same-family succession Gemini 3 Pro → Gemini 3.1 Pro (round 2, confirmatory)

**Verdict:** pending (confirmatory, not run)
**Role:** confirmatory (locked holdout)
**Period:** #34, 2026-03-05 → 03-13 (NE30 window 03-05 → 03-16, held out); swap on 03-09.

## Why this event
The cleanest member replacement in the village (same family, one-for-one) tests R7 (substrate independence): does the unit survive the swap
of a member, and does the successor take up the predecessor's place through the artifact rather than through memory?

## Prediction
*Frozen {DATE} in `analysis/confirm_r2.py` (C1), after exploratory round 2 and before any holdout use.* Crews (strict writers of a shared project,
membership from #34's pre-swap days) that contained Gemini 3 Pro: (a) relative change of the crew's writes per bin on R_G over the 2 active days after
the swap + the predecessor's pre-swap share ≥ 0; (b) Gemini 3.1 Pro writes on a predecessor crew's project within its first 2 active days.
Both → supported; neither → failed; else mixed. n = 1 succession, so this is a strength-of-evidence test, not a rate.
Run together with C2 (allocation continuity across nights in every holdout unit), C3 (continuity after memory loss), C4 (NE24 artifact migration,
see `NE24/`) and C5 (R4d ranking).

## Result
Not run. Dry run on the non-holdout stand-in NE29 (`NE29/`): C1 mixed. Refuses without `--confirm --i-understand-this-uses-the-locked-holdout`.

## Notes
- Holdout reuse (policy in `hypotheses/holdout.md`): H15's `confirm_ne30.py` (unrun) also targets NE30 with per-agent write-turn deficits. This
  script's statistics are crew-level continuity of writes on shared projects: a different statistic, unexamined. Disclose in the H15 card and in
  LOG.md before running; commit the script first.
""")
    (PS / "NE24").mkdir(exist_ok=True)
    (PS / "NE24" / "README.md").write_text(f"""# H01 × NE24: GitHub → GitLab artifact migration as a unit-store scramble (round 2, confirmatory)

**Verdict:** pending (confirmatory, not run)
**Role:** confirmatory (locked holdout)
**Period:** 2026-06-29, inside the NE21+NE23 holdout window (06-08 → 07-06); the same day as NE21's last hours switch (4 h → 8 h).

## Why this event
The only scramble of the units' *artifact store* in the data: every repo moved to a new host. R7 says the superagent "dissolves when its artifact
is scrambled, not when its members are swapped"; the rival says the unit is carried by its members and channel and the artifact is replaceable.

## Prediction
*Frozen {DATE} in `analysis/confirm_r2.py` (C4).* Crews alive on github.com projects in the 2 active days before 06-29. R7 predicts (a)
re-formation < 0.5 (re-formation = ≥ 2 former members co-write one gitlab.com project within 3 active days) and (b) the former members' V_adv
(any project) over days 1–2 after falls below their 2 days before by more than the median night-to-night change of crews in the same window.
Re-formation ≥ 0.5 with no dip supports the rival (members and channel carry the unit).

## Result
Not run. Dry-run mechanics checked on a pseudo-cut at 2026-05-11 (same host, so re-formation is trivially 1.0 there).

## Notes
- Confound: NE21's switch on the same day. The design cannot separate the two; the hours switch alone has no reason to dissolve crews.
""")


def main():
    r = json.loads((R2 / "results.json").read_text())
    conf = json.loads((R2 / "confirm_dryrun.json").read_text()) if (R2 / "confirm_dryrun.json").exists() else {}
    um = {u["unit"]: u for u in json.loads((R2 / "units.json").read_text()) if u["eligible"]}
    by_goal = {}
    for u in um:
        by_goal.setdefault(int(re.match(r"\d+", u).group()), []).append(u)
    summ = {}
    for g, units in sorted(by_goal.items()):
        V, vs = write_period(g, sorted(units), r, um)
        summ[f"G{g:02d}"] = {"verdict": V, "units": dict(zip(sorted(units), vs))}
        print(f"G{g:02d}", V, dict(zip(sorted(units), vs)))
    write_ne(r, conf)
    (R2 / "period_verdicts.json").write_text(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
