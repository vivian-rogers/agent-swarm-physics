"""Write the replication-layer period READMEs (templated; role `replication`) for H56 from the round-1 outputs.
Native folders (NE14, NE43, NE40, G51) are written by hand and are not touched here.
Run: uv run python hypotheses/H56-ep-platform-fingerprint/analysis/write_period_folders.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h56lib as L  # noqa: E402

HYP = Path(__file__).resolve().parents[1]
GP = HYP / "goalperiod-subhypotheses"
GOALS = HYP.parents[0] / "hypohypotheses/goal-periods.md"
NATIVE = {"G51"}
SCAF = ("scaffold_tool", "scaffold_prompt", "scaffold_family")


def goal_meta():
    txt = GOALS.read_text()
    titles = {int(m.group(1)): m.group(2).strip() for m in re.finditer(r"^### (\d+) · (.+)$", txt, re.M)}
    modes = {}
    for line in txt.splitlines():
        m = re.match(r"^\|\s*(\d+)\s*\|\s*(\S+) → (\S+)\s*\|\s*([^|]*)\|\s*(\d+)\s*\|\s*([^|]*)\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*(\S+)\s*\|", line)
        if m and int(m.group(1)) not in modes:
            modes[int(m.group(1))] = dict(start=m.group(2), end=m.group(3), mode=m.group(9))
    return titles, modes


def fmt(x, nd=3):
    return "–" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:.{nd}f}"


def main():
    titles, modes = goal_meta()
    days = pl.read_parquet(L.DATA / "days.parquet")
    es = pl.read_parquet(L.DATA / "replication/events_posthoc.parquet")
    res = json.loads((L.DATA / "replication/results.json").read_text())
    pts = json.loads((L.DATA / "replication/period_points.json").read_text())
    fam = {v: {p["goal_no"]: p for p in res["families"][v]["periods"]} for v in ("act_all", "act_agent_b3")}
    cps = {v: res["blind"][v]["change_points"] for v in ("act_all", "act_agent_b3")}
    summary = []
    for g in sorted(days.filter(~pl.col("holdout"))["goal_no"].unique().to_list()):
        folder = f"G{g:02d}"
        if folder in NATIVE:
            continue
        gd = days.filter((pl.col("goal_no") == g) & ~pl.col("holdout")).sort("pt_date")
        dl = gd["pt_date"].to_list()
        pp = {p["variant"]: p for p in pts if p["goal_no"] == g}
        if "act_all" not in pp:
            continue
        reg = gd["regime"][0]
        ev = es.filter((pl.col("goal_no") == g) & (pl.col("variant") == "act_all"))
        ev5 = es.filter((pl.col("goal_no") == g) & (pl.col("variant") == "act_agent_b3"))
        kick = ev.filter(pl.col("cls") == "goal")
        scaf = ev.filter(pl.col("cls").is_in(SCAF) & pl.col("newton_t").is_not_nan())
        # scaffold share per agent: 1 - EP(V5)/EP(V1)
        a1, a5 = pp["act_all"]["agents"], pp.get("act_agent_b3", {}).get("agents", {})
        shares = [1 - a5[k] / a1[k] for k in a1 if k in a5 and a1[k] and a1[k] > 0.01]
        kick_hit = bool(kick.height and kick["p_n2"][0] is not None and kick["p_n2"][0] < 0.05)
        scaf_hits = int((scaf["p_n2"] < 0.05).sum()) if scaf.height else 0
        if scaf.height == 0 and kick.height == 0:
            verdict = "n/a"
        elif scaf.height:
            verdict = "supported" if (scaf_hits == scaf.height and not kick_hit) else ("mixed" if scaf_hits else "failed")
        else:
            verdict = "failed" if kick_hit else "descriptive"
        cp_in = [c for c in cps["act_all"] if c["pt_date"] in set(dl)]
        cp5_in = [c for c in cps["act_agent_b3"] if c["pt_date"] in set(dl)]
        meta = modes.get(g, {})
        lines = [f"# H56 × G{g:02d}: {titles.get(g, '')} ({meta.get('start', dl[0])} → {meta.get('end', dl[-1])})", "",
                 f"**Verdict:** {verdict}",
                 "**Role:** replication (exploratory, round 1, non-holdout)",
                 f"**Period:** regime {reg} · mode {meta.get('mode', '?')} · {pp['act_all']['n_agents']} test agents · "
                 f"{len(dl)} non-holdout active days ({dl[0]} → {dl[-1]}).", "",
                 "## Why this period",
                 "Layer 1 of the two-layer design: every non-holdout goal period contributes its kickoff (a goal event, day 0 = its first "
                 "active day), the step changes inside it (scaffold, roster, room, operator; from the changelog and the NE catalog) and its "
                 "per-transition EP level (a phase-diagram point). The transition is the object (named exception (c)); this folder reports the "
                 "period's share of the evidence. Templated (replication role).", "",
                 "## Prediction",
                 "*Written 2026-10-04 06:00 UTC in the card, before any real-data EP; applied here as a template.* "
                 "The kickoff does not move the within-agent EP rate (|t| below the null; P2). Every scaffold change inside the period does (P1). "
                 "Period verdict rule: supported if every scored scaffold event is a hit and the kickoff is not; mixed if some scaffold events hit; "
                 "failed if scored scaffold events all miss or the kickoff hits; descriptive if no scaffold event is scored and the kickoff does not hit; "
                 "n/a if nothing is scored. Hits use the Amendment-3 null (card).", "",
                 "## Result", "",
                 "**Phase-diagram point** (per-agent EP over the period, Newton, nats/transition; median over agents):", "",
                 "| chain | median EP | count-matched median | agents |", "| --- | --- | --- | --- |"]
        for v, lab in (("act_all", "V1 fine, all records"), ("act_agent_b3", "V5 fine, agent-only + burn-in"),
                       ("coarse_all", "V3 coarse, all records"), ("coarse_agent_b3", "V6 coarse, agent-only + burn-in")):
            if v in pp:
                lines.append(f"| {lab} | {fmt(pp[v]['median_ep'])} | {fmt(pp[v]['median_ep_matched'])} | {pp[v]['n_agents']} |")
        lines += ["", f"Scaffold share of the fine EP, 1 − Σ(V5)/Σ(V1), median over agents: **{fmt(float(np.median(shares)) if shares else None, 2)}** "
                  f"(range {fmt(min(shares) if shares else None, 2)} to {fmt(max(shares) if shares else None, 2)}).", ""]
        lines += ["**Events** (within-agent count-matched statistic, 3 + 3 non-holdout days; V1 and V5; p against the Amendment-3 null):", "",
                  "| event | class | day 0 | agents | Δ̄ V1 | t V1 | f₊ V1 | p V1 | t V5 | p V5 | confounded by |",
                  "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for r in ev.sort("day0").iter_rows(named=True):
            r5 = ev5.filter(pl.col("event_id") == r["event_id"])
            t5 = r5["newton_t"][0] if r5.height else None
            p5 = r5["p_n2"][0] if r5.height else None
            lines.append(f"| {r['refs']} | {r['cls']} | {r['day0']} | {r.get('newton_n') or '–'} | {fmt(r.get('newton_dbar'))} | "
                         f"{fmt(r.get('newton_t'), 2)} | {fmt(r.get('newton_fpos'), 2)} | {fmt(r.get('p_n2'), 3)} | {fmt(t5, 2)} | {fmt(p5, 3)} | "
                         f"{r.get('confounders') or ''} |")
        if ev.height == 0:
            lines.append("| (no eligible event: windows cross a holdout gap > 14 days or a regime boundary) | | | | | | | | | | |")
        f1, f5 = fam["act_all"].get(g), fam["act_agent_b3"].get(g)
        lines += ["", "**Family contrast** (η²_lab of count-matched per-agent EP, labs with ≥ 2 agents; permutation p): "
                  + (f"V1 η² {fmt(f1['eta2'], 2)} (p {fmt(f1['p'], 3)}), V5 η² {fmt(f5['eta2'], 2)} (p {fmt(f5['p'], 3)})" if f1 and f5 else "not eligible (fewer than 2 labs with 2 agents)") + ".",
                  "", "**Blind change-points in this period** (V1; |t| ≥ the regime's 90th percentile, local maxima): "
                  + (", ".join(f"{c['pt_date']} (t {c['t']:.2f}, f₊ {c['fpos']:.2f}{', unexplained' if c['unexplained'] else ', near ' + '/'.join(c['near'])})" for c in cp_in) or "none")
                  + "; V5: " + (", ".join(f"{c['pt_date']}" for c in cp5_in) or "none") + ".", "",
                  "Data: `data/processed/H56-ep-platform-fingerprint/replication/` (`events_posthoc.parquet`, `tday.parquet`, `period_points.json`).", "",
                  "## Scorecard (period-specific axes)",
                  f"- **E (interventional):** {scaf.height} scored scaffold event(s), {scaf_hits} hit(s); kickoff {'hit' if kick_hit else 'not a hit' if kick.height else 'not scored'}.",
                  "- **C (adequacy):** event statistics are compared with same-regime days far from same-class events (Amendment 3).", "",
                  "## Notes",
                  "- Generated by `analysis/write_period_folders.py` from round-1 outputs (2026-10-04)."]
        (GP / folder).mkdir(parents=True, exist_ok=True)
        (GP / folder / "README.md").write_text("\n".join(lines) + "\n")
        summary.append({"period": folder, "verdict": verdict, "regime": reg, "n_agents": pp["act_all"]["n_agents"],
                        "ep_v1": pp["act_all"]["median_ep"], "ep_v5": pp.get("act_agent_b3", {}).get("median_ep"),
                        "scaffold_share": float(np.median(shares)) if shares else None,
                        "kick_t": kick["newton_t"][0] if kick.height else None, "kick_p": kick["p_n2"][0] if kick.height else None,
                        "n_scaf": scaf.height, "scaf_hits": scaf_hits})
    (L.DATA / "replication/period_summary.json").write_text(json.dumps(summary, indent=1, default=float))
    for s in summary:
        print(s)


if __name__ == "__main__":
    main()
