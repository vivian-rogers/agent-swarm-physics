"""Holdout ledger (DQ8): which hypothesis plans or used which held-out goal period or NE window, with which statistic
and modality, run or not; and which planned uses collide under the reuse policy (hypotheses/holdout.md, bottom).

Ledger: infra/data-quality/holdout_ledger.json (draft; the coordinator moves it next to hypotheses/holdout.md).
  entries[]   one per (hypothesis, target, statistic group): target, target_kind, goal_nos, in_window, statistic,
              estimator_family, channel, modality, script, status (run | script_written_not_run | planned | unclear),
              evidence, prediction_written, note
  targets{}   per held-out target (G01 ... G50, NE windows, #51-tail): the uses, runs first
  overlaps[]  kind = run_collision_same_modality | run_collision_same_family | planned_same_family |
              planned_same_modality | run_collision_other_modality; hypotheses, detail, disclosure_needed
  issues[]    stale status lines, undisclosed reuse, missing prediction sections (from the survey)

Policy encoded (holdout.md): a held-out target already used for confirmation may confirm a second hypothesis only if
(1) its predictions and script are committed first, (2) its observable is a different statistic or modality and
unexamined, (3) the reuse is disclosed in both cards and LOG.md. Exploration never touches held-out data.

Usage
  uv run python infra/shared/holdout_ledger.py --build SURVEY.json    normalize a survey into the ledger
  uv run python infra/shared/holdout_ledger.py --overlaps             recompute targets / overlaps from the ledger
  uv run python infra/shared/holdout_ledger.py --summary
Library: check(hypothesis, target, modality, family=None) -> dict(allowed, needs_disclosure, prior_runs, competing)
         for confirm scripts to call before running; record_run(...) appends a run (the coordinator commits it).
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "infra/data-quality/holdout_ledger.json"
HOLDOUT = ROOT / "hypotheses/holdout.json"

# estimator families: the same family on the same target counts as the same statistic under policy item 2
FAMILIES = [
    ("curie_weiss_gain", r"curie|g_eq|\bvr\b|loop gain|betaj0|βj|bj0|variance ratio|dial|mean-field k\b|equal-time"),
    ("hawkes_branching", r"hawkes|branching ratio|\bn-hat\b|n̂"),
    ("kinetic_ising_couplings", r"kinetic.ising|pairwise coupling|ki-1|net (outgoing )?influence|couplings? j_?ij"),
    ("kick_response", r"nudge|green'?s function|a30|chi_act|susceptib|kick|lever|att\b"),
    ("spectral_mode", r"lambda1|λ1|eigen|market mode|participation ratio|\bpr\b|pr30|collective mode"),
    ("entropy_production", r"entropy production|\bep\b|irreversib|arrow of time"),
    ("content_alignment", r"alignment|cosine|content (loop )?gain|semantic|embedding|room excess|aging|centroid"),
    ("stance", r"stance|oppose|faction|frustration"),
    ("project_potts", r"potts|project label|herding|consensus|link hazard|early warning|ews"),
    ("dilution_addressing", r"dilution|address|mention|read-out|readout|gate jump"),
    ("cascade", r"cascade|idea|adoption|contagion"),
    ("behavior_states", r"behavior state|markov|implied timescale|metastab|trap|kramers|catalyt|field effect"),
    ("artifact_lineage", r"lineage|git|fork|commit|artifact|copy information"),
    ("work_output", r"write|work output|productiv|viability"),
]


def family_of(statistic: str) -> list[str]:
    s = (statistic or "").lower()
    return [name for name, rx in FAMILIES if re.search(rx, s)] or ["other"]


def _targets_of(e: dict) -> list[str]:
    """Goal-period targets G<NN> for every goal number touched, plus the window id when the target is a window."""
    held = set(json.loads(HOLDOUT.read_text())["goal_periods_held_out"])
    out = [f"G{g:02d}" for g in e.get("goal_nos") or [] if g in held]   # #51 itself is not held out (its tail is)
    t = e.get("target")
    if t and not t.startswith("G"):
        out.append(t)
    if e.get("in_window") and e["in_window"] not in out:
        out.append(e["in_window"])
    return sorted(set(out)) or [t]


def build(survey_path: Path) -> dict:
    sv = json.loads(Path(survey_path).read_text())
    hold = json.loads(HOLDOUT.read_text())
    entries = []
    for k, e in enumerate(sv["entries"]):
        x = {key: e.get(key) for key in ("hypothesis", "slug", "target", "target_kind", "goal_nos", "in_window",
                                         "statistic", "channel", "modality", "modality_detail", "script", "status",
                                         "evidence", "prediction_written")}
        x["note"] = e.get("note")
        x["id"] = f"L{k + 1:03d}"
        x["estimator_family"] = family_of(f"{e.get('statistic', '')} {e.get('modality_detail') or ''}")
        x["targets_expanded"] = _targets_of(e)
        entries.append(x)
    led = {"meta": {"built_at": dt.datetime.now(dt.timezone.utc).isoformat(), "built_by": "infra/shared/holdout_ledger.py",
                    "survey": {"generated_at": sv.get("generated_at"), "source_commit": sv.get("source_commit"),
                               "method": "read-only survey of every card's confirmatory section, confirm*.py targets, "
                                         "period READMEs, data/processed confirm outputs and LOG.md (DQ8 agent)"},
                    "holdout_locked_at": hold["locked_at"],
                    "policy": "holdout.md: reuse of a confirmed held-out target needs (1) committed predictions + "
                              "script, (2) a different statistic or modality, unexamined, (3) disclosure in both "
                              "cards and LOG.md. Exploration never touches held-out data.",
                    "status_values": ["run", "script_written_not_run", "planned", "unclear"],
                    "draft": True},
           "held_out": {"goal_periods": hold["goal_periods_held_out"], "ne_windows": hold["ne_windows"]},
           "entries": entries, "no_holdout_use": sv.get("no_holdout_use", []),
           "unspecified_or_inconsistent": sv.get("unspecified_or_inconsistent", {}),
           "issues": sv.get("notes", [])}
    return recompute(led)


def recompute(led: dict) -> dict:
    by_t = defaultdict(list)
    for e in led["entries"]:
        for t in e["targets_expanded"]:
            by_t[t].append(e)
    order = {"run": 0, "script_written_not_run": 1, "planned": 2, "unclear": 3}
    targets = {}
    overlaps = []
    for t in sorted(by_t):
        es = sorted(by_t[t], key=lambda e: (order.get(e["status"], 9), e["hypothesis"]))
        targets[t] = [{"id": e["id"], "hypothesis": e["hypothesis"], "status": e["status"], "modality": e["modality"],
                       "family": e["estimator_family"], "statistic": e["statistic"][:160]} for e in es]
        runs = [e for e in es if e["status"] == "run"]
        rest = [e for e in es if e["status"] != "run"]
        for r in runs:
            for e in rest:
                if e["hypothesis"] == r["hypothesis"]:
                    continue
                fam = sorted(set(e["estimator_family"]) & set(r["estimator_family"]) - {"other"})
                if fam:
                    kind = "run_collision_same_family"
                elif e["modality"] == r["modality"]:
                    kind = "run_collision_same_modality"
                else:
                    kind = "run_collision_other_modality"
                overlaps.append({"target": t, "kind": kind, "prior_run": r["hypothesis"], "prior_run_id": r["id"],
                                 "hypothesis": e["hypothesis"], "entry_id": e["id"], "family": fam,
                                 "modality": e["modality"], "status": e["status"],
                                 "policy": ("blocked unless the statistic is shown to differ (item 2)"
                                            if kind != "run_collision_other_modality" else
                                            "allowed with committed script and disclosure (items 1 and 3)"),
                                 "disclosure_needed": True})
        # competing planned uses (no run yet), grouped: >= 2 hypotheses with the same estimator family, or (when they
        # share no family) the same modality
        fam_groups = defaultdict(set)
        fam_ids = defaultdict(set)
        for e in rest:
            for f in set(e["estimator_family"]) - {"other"}:
                fam_groups[f].add(e["hypothesis"])
                fam_ids[f].add(e["id"])
        for f, hs in sorted(fam_groups.items()):
            if len(hs) >= 2:
                overlaps.append({"target": t, "kind": "planned_same_family", "hypotheses": sorted(hs),
                                 "entry_ids": sorted(fam_ids[f]), "family": [f],
                                 "policy": "first to run consumes the statistic; later runners need a different "
                                           "statistic (or modality) and disclosure", "disclosure_needed": True})
        mod_groups = defaultdict(set)
        for e in rest:
            mod_groups[e["modality"]].add(e["hypothesis"])
        for m, hs in sorted(mod_groups.items(), key=lambda kv: str(kv[0])):
            if len(hs) >= 2:
                overlaps.append({"target": t, "kind": "planned_same_modality", "hypotheses": sorted(hs), "modality": m,
                                 "policy": "allowed for later runners only with a different statistic, a committed "
                                           "script and disclosure", "disclosure_needed": True})
    led["targets"] = targets
    led["overlaps"] = overlaps
    cnt = defaultdict(int)
    for o in overlaps:
        cnt[o["kind"]] += 1
    led["meta"]["overlap_counts"] = dict(cnt)
    led["meta"]["n_entries"] = len(led["entries"])
    led["meta"]["n_runs"] = sum(e["status"] == "run" for e in led["entries"])
    return led


def load() -> dict:
    return json.loads(LEDGER.read_text())


def check(hypothesis: str, target: str, modality: str, family: str | list | None = None) -> dict:
    """Reuse status of a planned confirmatory use. target: 'G45', 'NE12', '#51-tail', ...; family: estimator family
    name(s) (see FAMILIES) or None to infer nothing. allowed=False when a prior run on the target used the same family
    (policy item 2); needs_disclosure=True whenever anyone else ran on or plans the target."""
    led = load()
    fam = set([family] if isinstance(family, str) else (family or []))
    uses = led["targets"].get(target, [])
    prior = [u for u in uses if u["status"] == "run" and u["hypothesis"] != hypothesis]
    same = [u for u in prior if fam & set(u["family"])]
    competing = [u for u in uses if u["status"] != "run" and u["hypothesis"] != hypothesis
                 and ((fam & set(u["family"])) or u["modality"] == modality)]
    return {"target": target, "allowed": not same, "needs_disclosure": bool(prior or competing),
            "prior_runs": prior, "prior_runs_same_family": same, "competing_planned": competing}


def record_run(entry_id: str, evidence: str, when: str | None = None) -> None:
    """Mark a ledger entry as run (evidence: output path + LOG.md date) and recompute overlaps."""
    led = load()
    for e in led["entries"]:
        if e["id"] == entry_id:
            e["status"] = "run"
            e["evidence"] = f"{e['evidence']}; RUN {when or dt.date.today().isoformat()}: {evidence}"
    LEDGER.write_text(json.dumps(recompute(led), indent=1, ensure_ascii=False))


def summary(led: dict) -> str:
    lines = [f"{led['meta']['n_entries']} entries, {led['meta']['n_runs']} run; overlaps {led['meta']['overlap_counts']}"]
    for t, us in led["targets"].items():
        runs = [u["hypothesis"] for u in us if u["status"] == "run"]
        lines.append(f"  {t:10s} {len({u['hypothesis'] for u in us}):2d} hypotheses; run: {', '.join(runs) or '-'}")
    return "\n".join(lines)


if __name__ == "__main__":
    if "--build" in sys.argv:
        led = build(Path(sys.argv[sys.argv.index("--build") + 1]))
        LEDGER.write_text(json.dumps(led, indent=1, ensure_ascii=False))
        print(summary(led))
    elif "--overlaps" in sys.argv:
        led = recompute(load())
        LEDGER.write_text(json.dumps(led, indent=1, ensure_ascii=False))
        print(summary(led))
    else:
        print(summary(load()))
