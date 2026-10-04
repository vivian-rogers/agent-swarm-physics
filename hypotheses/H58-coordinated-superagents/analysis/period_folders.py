"""H58 per-period folders (goalperiod-subhypotheses/G<NN>/, NE42/, G51g/). Two phases:
  --predict   write each README with Verdict pending and the dated prediction (before the replication / native runs)
  --results   fill Result, Verdict and the period scorecard from results/units/*.json, replication.json, natives.json,
              reacq.json (keeps the prediction text unchanged)
Run: uv run python hypotheses/H58-coordinated-superagents/analysis/period_folders.py --predict | --results
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h58data as HD  # noqa: E402

CARD = HERE.parent
GP = CARD / "goalperiod-subhypotheses"
RES = HD.D / "results"
TODAY = "2026-10-04"
ATTR = {}    # results/attraction.json (A3)
POWER = {}   # filled from synthetic_summary.json (power at rho = 0.5 per unit)

PERIODS = {
    "G38": {"units": ["38a", "38b", "38c"], "title": "Charity fundraiser, year 2", "role": "replication"},
    "G44": {"units": ["44"], "title": "#best fine-tunes a leader; #rest picks its own goals", "role": "native"},
    "G51": {"units": ["51a", "51b", "51c", "51d", "51e"], "title": "Maximize your private assigned role (head)",
            "role": "replication"},
    "NE42": {"units": ["39", "40", "41"], "title": "NE42 merge (05-04) and split (05-11): #39 -> #40 -> #41",
             "role": "native"},
    "G51g": {"units": ["51b", "51c"], "title": "#51 #focus room (08-05 -> 08-24): a self-selected channel cut",
             "role": "native"},
}

REPLICATION_PRED = ("*Written {today}, before the replication run on this period (templated, per the two-layer rule; "
                    "after amendments A1 and A2).* The card's P1–P3 applied here: at least one coordination-defined unit "
                    "(multi-layer community or calibrated search result) is an effective-superagent candidate "
                    "(g > 0, z_spec ≥ 2, z_shift ≥ 2, specificity ≥ 0.5, testable against an outside reference; "
                    "search p ≤ 0.05); multi-layer communities rank above rooms and labs; candidates may span rooms. "
                    "Synthetic power to see a planted store of strength ρ = 0.5 here: **{power}**{pnote}. "
                    "My prior for this period: {prior}")
PRIORS = {
    "30": "no candidate (two repos, one shared park repo; 4-h days).",
    "31": "no candidate; the herding wave onto one repo is a common field (H11/H27), so co-allocation is not specific to any subset.",
    "33": "no candidate (one shared repo; 3 days).",
    "35": "no candidate; the two room forks are separate artifacts, so crews = rooms, but members keep to their own subtasks.",
    "36b": "no candidate.",
    "37": "no candidate (free days, individual projects).",
    "38a": "no candidate; charity pages are mostly individual.",
    "38b": "no candidate.",
    "38c": "no candidate.",
    "39": "no candidate: 15 own worlds, each agent with its own artifact (the null unit's home ground).",
    "40": "a weak candidate centred on the universe repo is possible, but one dominant repo leaves little 'which artifact' variation at repo level (see NE42 for the file level).",
    "41": "no candidate (independent research).",
    "42": "no candidate (own channels).",
    "44": "see the native prediction.",
    "51a": "no candidate.",
    "51b": "a small candidate around shared infrastructure repos is possible; most allocation is private-role work.",
    "51c": "as 51b.",
    "51d": "as 51b.",
    "51e": "no candidate (2 days).",
}

NATIVE_PRED = {
    "NE42": ("*Written {today}, before the NE42 analysis (card N1).* **Observable:** the size and qualification of the "
             "best coordination-defined unit across the A-B-A (#39 own worlds → #40 one merged room and one shared "
             "universe repo → #41 split back), and, inside #40's shared repo, the coordination gain at **file "
             "granularity** (read-only `git log --name-only`: the hub file vs per-agent landmark files) against the agent "
             "+ own file null. **Prediction (card):** #40's search result has ≥ 4 members and qualifies; no qualifying "
             "unit of size ≥ 4 in #39 or #41; at file level g > 0 with z_shift ≥ 2. **Falsified if** #40 has no "
             "qualifying unit of size ≥ 4. **Power caveat (A2):** 5-day units have synthetic power 0.15–0.30 at ρ = 0.5, "
             "so a null in #40 is weak. **My prior:** at file level members keep to their own landmark file and the hub "
             "file is a common field; #40 does not qualify."),
    "G44": ("*Written {today}, before the #44 analysis (card N2).* **Observable:** the coordination-first search, "
            "run without room or team labels, against DQ6's #best team (room assignment, preferred, non-holdout: four "
            "agents) and its training-data / fine-tuning repo; the known team evaluated directly with both nulls; "
            "qualifying units of size ≥ 3 inside #rest (which chose its own goals). **Prediction (card):** the search "
            "returns a set with Jaccard ≥ 0.5 to the team that qualifies, with the fine-tuning repo in its R_G; no "
            "qualifying unit of size ≥ 3 in #rest. **Falsified if** Jaccard < 0.5 or the set does not qualify. "
            "**Power caveat (A2):** 4 days, 36 bins, synthetic power 0.35 at ρ = 0.5. Replication numbers (P1–P3) are "
            "reported here too. **My prior:** the team is recovered through co-artifact work, but its gain is not "
            "specific against outsiders (the late joiners also write on the team repo) or not beyond member shifts."),
    "G51g": ("*Written {today}, before the #focus analysis (card N3).* **Observable:** pair coordination gain on the "
             "pair's joint artifacts, before (51b, 07-09 → 08-04) and during the #focus era (51c, 08-05 → 08-24), "
             "for pairs split by the cut (one member mostly in #focus, the other in #general) vs pairs kept together; "
             "DiD with a pair bootstrap. Qualifying 51c units that contain members of both rooms. **Prediction "
             "(card):** DiD ≥ −0.5 × the split pairs' pre-cut mean (coordination is artifact-held and survives a "
             "channel cut); qualifying 51c units span both rooms. **Falsified if** DiD < −0.5 × pre mean with the CI "
             "below. **Caveats:** #focus is self-selected; very few agents moved (the rooms table shows two agents "
             "with > 50% of their 51c bins in #focus), so n is small. **My prior:** little coordination to lose; DiD "
             "≈ 0 and uninformative."),
}


def power_of(units):
    s = json.loads((RES / "synthetic_summary.json").read_text())
    vals = [s["per_unit"].get(u, {}).get("store_0.5") for u in units]
    return ", ".join(f"{u} {v:.2f}" if v is not None else f"{u} –" for u, v in zip(units, vals))


def header(key, spec, verdict="pending"):
    meta = {x["unit"]: x for x in HD.units_meta()}
    us = [u for u in spec["units"] if u in meta]
    days = sum(meta[u]["n_days"] for u in us)
    reg = sorted({meta[u]["regime"] for u in us})
    span = f"{meta[us[0]]['days'][0]} → {meta[us[-1]]['days'][-1]}"
    role = spec["role"]
    return (f"# H58 × {key}: {spec['title']} ({span})\n\n**Verdict:** {verdict}\n**Role:** {role}\n"
            f"**Period:** regime {'/'.join(reg)} · units {', '.join(us)} · {days} non-holdout days. Units are H01 round 2's "
            f"(card F1).\n")


def why(key, spec):
    if spec["role"] == "replication":
        return ("## Why this period\nLayer 1 (replication): it has a dense work ledger (DQ4 agent work commits), so the "
                "allocation state (which artifact each agent advances per 30-min bin), the coordination layers and the "
                "decision rule can be computed as on every other eligible period, giving one comparable point.\n")
    return {"NE42": "## Why this period\nThe only A-B-A channel manipulation at a fixed roster (merge into one room, split back), with the store reorganized in between: 15 own artifacts (#39) joined into one shared repo (#40), then independent research (#41). DQ9 lists #40 (one artifact, one room, 14 contributors) as H58's first native test.\n",
            "G44": "## Why this period\nThe only non-holdout period with a known team (#best, four agents, DQ6 room assignment) that shares a dedicated artifact (training data and fine-tuning repos), next to a room that chose its own individual goals on the same days and scaffold. Ground truth for the search.\n",
            "G51g": "## Why this period\nA channel cut inside the stationary #51 head: from 08-05 some agents work in a separate #focus room (chat visibility follows rooms), with the goal, hours and roster fixed. If coordination is held in artifacts, it should survive the cut; if it is carried by chat, split pairs should lose it.\n"}[key]


def predict():
    for key, spec in PERIODS.items():
        d = GP / key
        (d / "figures").mkdir(parents=True, exist_ok=True)
        if spec["role"] == "replication":
            pw = power_of(spec["units"])
            pnote = " (a null here is 'not identifiable', A2.1)" if all(
                (json.loads((RES / "synthetic_summary.json").read_text())["per_unit"].get(u, {}).get("store_0.5") or 0) < 0.5
                for u in spec["units"]) else ""
            prior = " ".join(f"{u}: {PRIORS[u]}" for u in spec["units"])
            pred = REPLICATION_PRED.format(today=TODAY, power=pw, pnote=pnote, prior=prior)
        else:
            pred = NATIVE_PRED[key].format(today=TODAY)
        txt = (header(key, spec) + "\n" + why(key, spec) + "\n## Prediction\n" + pred + "\n\n## Result\n_pending_\n\n"
               "## Scorecard (period-specific axes)\n_pending_\n\n## Notes\n- " + TODAY +
               ": folder created by `analysis/period_folders.py --predict` before the run.\n")
        (d / "README.md").write_text(txt)
    print("predictions written:", ", ".join(PERIODS))


def fmt(x, nd=3):
    if x is None:
        return "–"
    if isinstance(x, float):
        if not np.isfinite(x):
            return "–"
        return f"{x:+.{nd}f}" if nd else f"{x:.0f}"
    return str(x)


def unit_block(u, rep, names):
    pu = rep["per_unit"][u]
    r = json.loads((RES / "units" / f"{u}.json").read_text())
    C = r["candidates"]
    lines = [f"### Unit {u}", f"- {pu['nA']} committing agents, {pu['nB']} bins, {pu['nD']} days, {pu['n_commits']} agent "
             f"work commits; synthetic power at ρ = 0.5: {POWER.get(u, '–')}."]
    lines.append("")
    lines.append("| candidate | members | g (bits / working member-bin) | z_spec | z_shift | specificity | qualifies |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for kind in ("search", "multi", "room", "lab"):
        for c in C.get(kind, []):
            q = c.get("qualifies_search") if kind == "search" else c["qualifies"]
            mem = ", ".join(names.get(a, str(a)) for a in c["agents"])
            lab = {"search": "search", "multi": "multi-layer community", "room": "room", "lab": "lab"}[kind]
            extra = f" (search p {c.get('p_search'):.2f})" if kind == "search" and c.get("p_search") is not None else ""
            lines.append(f"| {lab}{extra} | {len(c['agents'])}: {mem} | {fmt(c['g'])} | {fmt(c['z_comp'], 1)} | "
                         f"{fmt(c['z_shift'], 1)} | {fmt(c.get('specificity'), 2)} | {'yes' if q else 'no'}"
                         f"{'' if c.get('testable', True) else ' (untestable)'} |")
    nq = {k: sum(1 for c in C.get(k, []) if c["qualifies"]) for k in ("w_sync", "w_coad", "w_reply", "w_coart", "crew")}
    nt = {k: len(C.get(k, [])) for k in nq}
    lines.append("")
    lines.append("- Single-layer communities and joint-work crews qualifying: " +
                 ", ".join(f"{k.replace('w_', '')} {nq[k]}/{nt[k]}" for k in nq) + ".")
    s = C["search"][0] if C["search"] else None
    if s:
        lines.append(f"- Search result: lagged gain (transfer entropy) {fmt(s.get('g_lag'))}, content gain "
                     f"{fmt(s.get('g_content'))}, night gain {fmt(s.get('g_night'))} (z {fmt(s.get('z_night_comp'), 1)}); "
                     f"unit individuality ι {fmt(s.get('iota'), 3)} vs aggregation baseline {fmt(s.get('iota_shift_mu'), 3)} "
                     f"(z {fmt(s.get('z_iota_shift'), 1)}), members as agent + own artifact {fmt(s.get('iota_members'), 3)}.")
    att = ATTR.get(u, [])
    for x in att:
        if x["kind"] == "search" or x["qualifies"]:
            lines.append(f"- Attraction diagnostic (A3, post hoc) for the {x['kind']} unit of {len(x['agents'])}: {x.get('joins')} joins "
                         f"of {x.get('n_moves')} moves vs {fmt(x.get('expected'), 1) if x.get('expected') is not None else '–'} "
                         f"expected under agent + own artifacts (ratio {fmt(x.get('attraction'), 2)}).")
    lines.append(f"- Agent + own artifact (singletons): median ι {fmt(pu.get('singleton_iota_median'), 3)}, median colonial "
                 f"(persistence) {fmt(pu.get('singleton_colonial_median'), 3)} bits.")
    v = pu.get("variants") or {}
    vv = []
    for bm, rows in v.items():
        for row in rows:
            vv.append(f"{bm} min ({row['from']}): g {fmt(row.get('g'))}, qualifies {row.get('qualifies')}")
    if vv:
        lines.append("- Bin-width variants: " + "; ".join(vv) + ".")
    return "\n".join(lines), bool(pu["any_candidate"])


def results():
    global POWER, ATTR
    ATTR = json.loads((RES / "attraction.json").read_text()) if (RES / "attraction.json").exists() else {}
    rep = json.loads((RES / "replication.json").read_text())
    nat = json.loads((RES / "natives.json").read_text()) if (RES / "natives.json").exists() else {}
    rq = json.loads((RES / "reacq.json").read_text())
    syn = json.loads((RES / "synthetic_summary.json").read_text())
    POWER = {u: f"{v['store_0.5']:.2f}" for u, v in syn["per_unit"].items() if v.get("store_0.5") is not None}
    import polars as pl
    names = dict(pl.read_parquet(HD.SH / "roster.parquet").select("agent", "name").iter_rows())
    verdicts = {}
    for key, spec in PERIODS.items():
        d = GP / key
        txt = (d / "README.md").read_text()
        pred = txt[txt.index("## Prediction"):txt.index("## Result")]
        if spec["role"] == "replication" or key == "G44":
            blocks, anyc = [], []
            for u in spec["units"]:
                b, a = unit_block(u, rep, names)
                blocks.append(b)
                anyc.append(a)
                if u in rq.get("per_unit", {}):
                    pu = rq["per_unit"][u]
                    f, p = pu["forced_div"], pu["placebo_div"]
                    if f["n"]:
                        blocks.append(f"- Re-acquisition (NE41, divergent events, until the next reset): forced n {f['n']}: "
                                      f"own {fmt(f['own'], 2)}, group {fmt(f['group'], 2)}, other {fmt(f['other'], 2)}, none "
                                      f"{fmt(f['none'], 2)}; placebo n {p['n']}: own {fmt(p['own'], 2)}, group {fmt(p['group'], 2)}.")
            powered = [u for u in spec["units"] if float(POWER.get(u, 0)) >= 0.5]
            if any(anyc):
                v = "mixed" if not all(anyc) else "supported"
            else:
                v = "failed" if powered else "n/a"
            if key == "G44":
                v = native_verdict_44(nat)
            body = "\n\n".join(blocks)
            if key == "G44":
                body = native_44_text(nat, names) + "\n\n#### Replication numbers\n" + body
            verdicts[key] = v
            note = ""
            if v == "n/a":
                note = ("\n\n**Reading:** no candidate, but this period's synthetic power at ρ = 0.5 is < 0.5, so by A2.1 "
                        "the null is *not identifiable* (verdict n/a), not a refutation.")
        elif key == "NE42":
            v, body = native_ne42(nat, names)
            verdicts[key] = v
            note = ""
        else:
            v, body = native_focus(nat, names)
            verdicts[key] = v
            note = ""
        score = scorecard(key, v)
        new = (header(key, spec, v) + "\n" + why(key, spec) + "\n" + pred + "## Result\nData: "
               f"`data/processed/H58-coordinated-superagents/results/` (units/*.json, replication.json, natives.json, "
               f"reacq.json); pipeline `analysis/run.py`, `natives.py`, `reacq.py`.\n\n" + body + note +
               "\n\n## Scorecard (period-specific axes)\n" + score + "\n\n## Notes\n- " + TODAY +
               ": prediction written by `period_folders.py --predict` before the run; results filled by `--results`.\n")
        (d / "README.md").write_text(new)
    (RES / "period_verdicts.json").write_text(json.dumps(verdicts, indent=1))
    print(verdicts)


def scorecard(key, v):
    if key in ("NE42", "G51g"):
        return ("- **E** (interventional): " + ("the natural experiment's prediction held" if v == "supported" else
                "the prediction did not hold or was not testable") + ".\n- **G**: rooms and the A-B-A dates are known; "
                "the file-level and room assignments come from logged fields.\n- **F**: 5-day units have low synthetic power (A2).")
    if key == "G44":
        return ("- **G** (ground truth): the DQ6 #best team is the answer key for the search (see above).\n- **C**: both "
                "nulls and the outside reference applied.\n- **F**: power 0.35 at ρ = 0.5 (36 bins).")
    return ("- **C**: decision rule = both nulls + specificity + outside reference.\n- **F**: synthetic power listed per "
            "unit; nulls in under-powered units are 'not identifiable'.")


def native_verdict_44(nat):
    n2 = nat.get("N2", {})
    s = n2.get("search", {})
    ok = bool(s and (s.get("jaccard_team") or 0) >= 0.5 and s.get("qualifies_search"))
    rest_bad = bool(n2.get("rest_qualifying_ge3"))
    if ok and not rest_bad:
        return "supported"
    if ok or (n2.get("team_eval", {}).get("qualifies")):
        return "mixed"
    return "failed"


def native_44_text(nat, names):
    n2 = nat.get("N2", {})
    s = n2.get("search", {})
    te = n2.get("team_eval", {})
    L = ["#### Native test N2 (the #best team + its artifact)",
         f"- DQ6 #best team: {', '.join(names.get(a, str(a)) for a in n2.get('team', []))}.",
         f"- Search (no labels): {', '.join(names.get(a, str(a)) for a in s.get('agents', []))}; Jaccard with the team "
         f"{fmt(s.get('jaccard_team'), 2)}; g {fmt(s.get('g'))}, z_spec {fmt(s.get('z_comp'), 1)}, z_shift "
         f"{fmt(s.get('z_shift'), 1)}, specificity {fmt(s.get('specificity'), 2)}, search p {fmt(s.get('p_search'), 2)}; "
         f"qualifies {s.get('qualifies_search')}; R_G {', '.join(s.get('repos', []))}.",
         f"- Known team evaluated directly: g {fmt(te.get('g'))}, z_spec {fmt(te.get('z_comp'), 1)}, z_shift "
         f"{fmt(te.get('z_shift'), 1)}, specificity {fmt(te.get('specificity'), 2)}, qualifies {te.get('qualifies')}; "
         f"R_G {', '.join(te.get('repo_names', []))}; lagged gain {fmt(te.get('g_lag'))}, night gain {fmt(te.get('g_night'))}.",
         f"- Qualifying units of size ≥ 3 entirely inside #rest: {len(n2.get('rest_qualifying_ge3', []))}."]
    if "team_plus_29" in n2:
        t2 = n2["team_plus_29"]
        L.append(f"- Team plus Claude Opus 4.8 (joined 05-28): g {fmt(t2.get('g'))}, qualifies {t2.get('qualifies')}.")
    return "\n".join(L)


def native_ne42(nat, names):
    n1 = nat.get("N1", {})
    L = ["| unit | search result (size) | qualifies | g | z_spec | z_shift | specificity | largest qualifying unit |",
         "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for u in ("39", "40", "41"):
        b = n1.get(u, {})
        L.append(f"| {u} | {', '.join(names.get(a, str(a)) for a in (b.get('search_agents') or []))} ({b.get('search_n')}) | "
                 f"{b.get('search_qual')} | {fmt(b.get('search_g'))} | {fmt(b.get('search_z_comp'), 1)} | "
                 f"{fmt(b.get('search_z_shift'), 1)} | {fmt(b.get('search_spec'), 2)} | {b.get('largest_qual')} |")
    fl = n1.get("file_level_40", {})
    cr = fl.get("crew", {})
    se = fl.get("search", {})
    L += ["", "**File level inside #40's shared repo** (artifact = file group, path depth ≤ 2):",
          f"- {fl.get('n_files')} file groups, {fl.get('n_writers')} writers; the hub file takes "
          f"{fmt(fl.get('hub_share_of_working_bins'), 2)} of working bins; median top-file share per agent "
          f"{fmt(fl.get('median_top_file_share'), 2)}.",
          f"- All writers as one unit: g {fmt(cr.get('g'))}, z_spec {fmt(cr.get('z_comp'), 1)}, z_shift {fmt(cr.get('z_shift'), 1)}, "
          f"specificity {fmt(cr.get('specificity'), 2)} ({'untestable: no outsiders' if not cr.get('testable', True) else ''}), "
          f"qualifies {cr.get('qualifies')}.",
          f"- File-level search: {', '.join(names.get(a, str(a)) for a in se.get('agents', []))}; g {fmt(se.get('g'))}, "
          f"z_spec {fmt(se.get('z_comp'), 1)}, z_shift {fmt(se.get('z_shift'), 1)}, specificity {fmt(se.get('specificity'), 2)}, "
          f"search p {fmt(se.get('p_search'), 2)}, qualifies {se.get('qualifies_search')}.",
          "- Multi-layer communities at file level: " + "; ".join(
              f"{c['n']} members, g {fmt(c['g'])}, qualifies {c['qualifies']}" for c in fl.get("multi", [])) + "."]
    q40 = (n1.get("40", {}).get("largest_qual") or 0) >= 4
    q_other = any((n1.get(u, {}).get("largest_qual") or 0) >= 4 for u in ("39", "41"))
    file_ok = bool(se.get("g") is not None and se.get("g") > 0 and (se.get("z_shift") or 0) >= 2)
    if q40 and not q_other and file_ok:
        v = "supported"
    elif q40 or file_ok:
        v = "mixed"
    else:
        v = "failed"
    L.append(f"\n**Verdict rule (card N1):** #40 qualifying unit of size ≥ 4: {q40}; none in #39/#41: {not q_other}; "
             f"file-level g > 0 with z_shift ≥ 2: {file_ok}. Power caveat (A2): 0.15–0.30 at ρ = 0.5.")
    return v, "\n".join(L)


def native_focus(nat, names):
    n3 = nat.get("N3", {})
    L = [f"- #focus agents (> 50% of 51c bins in #focus): {', '.join(names.get(a, str(a)) for a in n3.get('focus_agents', []))}.",
         f"- Pairs with a joint-artifact gain in both 51b and 51c: {n3.get('n_common_pairs')} ({n3.get('n_split')} split by the cut, "
         f"{n3.get('n_kept')} kept together).",
         f"- Split pairs: {fmt(n3.get('pre_mean_split'))} → {fmt(n3.get('post_mean_split'))}; kept pairs: "
         f"{fmt(n3.get('pre_mean_kept'))} → {fmt(n3.get('post_mean_kept'))} bits per working member-bin.",
         f"- DiD (split − kept) {fmt(n3.get('did'))}, 95% bootstrap CI [{fmt(n3.get('did_ci', [None, None])[0])}, "
         f"{fmt(n3.get('did_ci', [None, None])[1])}].",
         f"- Qualifying 51c units: {len(n3.get('qualifying_51c', []))}; spanning both rooms: "
         f"{sum(1 for c in n3.get('qualifying_51c', []) if c['has_focus'] and c['has_general'])}."]
    did, pre = n3.get("did"), n3.get("pre_mean_split")
    ci = n3.get("did_ci") or [None, None]
    if did is None or pre is None or not n3.get("n_split"):
        v = "n/a"
    else:
        fails = did < -0.5 * abs(pre) and ci[1] is not None and ci[1] < 0
        # nothing to lose: split pairs had no pre-cut coordination (pre mean <= 0.01 bits), so the test is uninformative
        v = "failed" if fails else ("descriptive" if ((n3.get("n_split") or 0) < 10 or pre <= 0.01) else "supported")
    L.append(f"\n**Verdict rule (card N3):** falsified if DiD < −0.5 × the split pairs' pre mean with the CI below 0. "
             f"With {n3.get('n_split')} split pairs the test is weak; fewer than 10 split pairs, or no pre-cut coordination to lose (split pairs' pre mean ≤ 0.01 bits), → descriptive.")
    return v, "\n".join(L)


if __name__ == "__main__":
    if "--predict" in sys.argv:
        predict()
    elif "--results" in sys.argv:
        results()
    else:
        sys.exit("--predict or --results")
