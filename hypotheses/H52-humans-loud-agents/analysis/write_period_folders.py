"""Write goalperiod-subhypotheses/G<NN>/README.md for H52's replication layer (templated by design; the card's
two-layer rule allows a templated prediction for replication folders, labelled as such). Native folders (G04, G51,
G26, G35, G44, NE43) are written by hand and are skipped here unless they have no README yet.

The prediction block is the card's replication prediction (written 2026-10-04 ~06:10 UTC, before any outcome);
results come from data/processed/H52-humans-loud-agents/<period>/results.json and summary.json.
Usage: uv run python hypotheses/H52-humans-loud-agents/analysis/write_period_folders.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h52lib as L  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

NATIVE = {"G04", "G51", "G26", "G35", "G44"}
TITLE_FALLBACK = "goal period"


def fmt(x, nd=3):
    return "—" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:.{nd}f}"


def fci(c, nd=3):
    if not c or c[0] is None or not np.isfinite(c[0]):
        return "[—]"
    return f"[{c[0]:.{nd}f}, {c[1]:.{nd}f}]"


def period_info(goal):
    gp = pl.read_parquet(L.SH / "calendar.parquet").filter(pl.col("goal_no") == goal)
    days = sorted(gp["pt_date"].to_list())
    return days[0], days[-1], gp["regime"].cast(pl.Utf8).mode()[0]


def verdict_period(r: dict, margins: dict, powered: bool) -> tuple[str, list]:
    """Replication verdict for H52 in this period, from the human premia (content and activity decide H52's
    'loud agents' claim; reply and stance reported). supported: content and activity premia 'equivalent' or CI
    including 0 with |point| < margin; failed: content or reply premium with CI excluding 0 beyond the margin;
    mixed otherwise; descriptive if not powered and every CI includes 0."""
    hd = r["headline"]
    v = {}
    for oc in ("con", "rep", "act", "st"):
        h = hd.get(f"{oc}_human")
        v[oc] = L.verdict_from_ci(h["ci"], margins.get(oc)) if h and h.get("ci") else "n/a"
    beyond = []
    for oc in ("con", "rep"):
        h = hd.get(f"{oc}_human")
        if h and h.get("ci") and h["ci"][0] is not None and np.isfinite(h["ci"][0]):
            if h["ci"][0] > margins.get(oc, 0) or h["ci"][1] < -margins.get(oc, 0):
                beyond.append(oc)
    if beyond:
        out = "failed"
    elif v["con"] in ("equivalent",) and v["act"] in ("equivalent", "inconclusive", "n/a"):
        out = "supported"
    elif not powered and all(x in ("inconclusive", "n/a", "equivalent") for x in v.values()):
        out = "descriptive"
    else:
        out = "mixed"
    return out, v


def main():
    S = json.loads((L.OUT / "summary.json").read_text())
    margins = S["margins"]
    powered = set(S["powered"])
    for p in L.REPLICATION:
        rp = L.OUT / p / "results.json"
        if not rp.exists():
            continue
        folder = L.HYP / "goalperiod-subhypotheses" / p
        if p in NATIVE and (folder / "README.md").exists():
            continue
        r = json.loads(rp.read_text())
        goal = int(p[1:3])
        first, last, regime = period_info(goal)
        de = r.get("descr", {})
        hd = r["headline"]
        verdict, v = verdict_period(r, margins, p in powered)
        nh = de.get("human", {}); na = de.get("agent", {}); nb = de.get("bot", {})
        def tag(oc, nd=3):
            h = hd.get(f"{oc}_human", {})
            c = h.get("ci") or [None, None]
            sig = "" if c[0] is None or not (c[0] > 0 or c[1] < 0) else "*"
            return f"{fmt(h.get('att'), nd)}{sig}"
        key = f"reply {tag('rep')}, content {tag('con')}"
        lines = [f"# H52 × {p}: humans as loud agents, replication ({first} → {last})", "",
                 f"**Verdict:** {verdict} — {key}",
                 "**Role:** replication",
                 f"**Period:** regime {regime} · non-holdout days only · human messages {nh.get('msgs', 0)} on {nh.get('days', 0)} days "
                 f"({nh.get('rows', 0)} message × recipient rows; goal kickoffs excluded) · agent rows {na.get('rows', 0)}"
                 + (f" · bot rows {nb.get('rows', 0)}" if nb else "") + ". "
                 + ("Powered (pre-registered rule)." if p in powered else "Not powered (fewer than 300 matched human content rows or fewer than 6 days with human messages): read as a phase-diagram point, not a test."),
                 "", "## Why this period",
                 "Replication layer: the common estimator on every non-holdout goal period with ≥ 100 non-kickoff human "
                 "(message, recipient) rows on ≥ 3 days. " + ("Regime I: the 2025 public chat, where many human viewers wrote to the agents." if regime == "I"
                                                             else "Regime III: human messages are mostly operator or staff messages."),
                 "", "## Prediction",
                 "*Templated replication prediction, copied from the card (written 2026-10-04 ~06:10 UTC, before any outcome statistic).*",
                 "- H52: the matched human premium is equivalent to 0 in content and activity; reply and stance premia reported.",
                 "- Author's expectation (card P1–P4): content premium > 0 in regime III and ≤ 0 in regime I; reply premium > 0; activity premium CI includes 0; stance premium > 0.",
                 "- Counts against H52: a content or reply premium whose CI lies beyond the margin (δ_con = 0.5 × pooled agent naming effect; δ_rep likewise).",
                 "", "## Result",
                 f"Margins: δ_con {fmt(margins.get('con'), 4)}, δ_rep {fmt(margins.get('rep'), 4)}, δ_act 0.5 min, δ_st 0.05. "
                 "Premium = CEM ATT of human rows vs agent rows in the same salience stratum (Amendment A1 estimators). "
                 "In the verdict line, * marks a 95% CI that excludes 0.", "",
                 "| Outcome | Human premium [95% CI] | Naive human − agent | Matched agent mean | Agent naming effect | Verdict |",
                 "| --- | --- | --- | --- | --- | --- |"]
        names = {"con": "content (DiD χ)", "rep": "reply (parent)", "act": "activity (min / 30 min, BC)", "st": "stance (soft)"}
        for oc in ("con", "rep", "act", "st"):
            h = hd.get(f"{oc}_human", {}); an = hd.get(f"{oc}_agent_naming", {})
            nd = 2 if oc == "act" else 3
            lines.append(f"| {names[oc]} | {fmt(h.get('att'), nd)} {fci(h.get('ci'), nd)} (n {h.get('n_t', '—')}, {h.get('n_t_msgs', '—')} msgs; matched {fmt(h.get('matched'), 2)}) "
                         f"| {fmt(h.get('naive'), nd)} | {fmt(h.get('ctrl_mean'), nd)} | {fmt(an.get('att'), nd)} {fci(an.get('ci'), nd)} | {v[oc]} |")
        if nb:
            lines += ["", "**Bot (automated nudges; named = leading @):**", "",
                      "| Outcome | Bot premium [95% CI] | n rows |", "| --- | --- | --- |"]
            for oc in ("con", "rep", "act", "st"):
                h = hd.get(f"{oc}_bot", {})
                nd = 2 if oc == "act" else 3
                if h:
                    lines.append(f"| {names[oc]} | {fmt(h.get('att'), nd)} {fci(h.get('ci'), nd)} | {h.get('n_t', '—')} |")
        rb = r.get("robustness", {})
        h30 = rb.get("con_h30orth", {}).get("human", {}).get("all", {})
        gte = rb.get("con_gte", {}).get("human", {}).get("all", {})
        jd = rb.get("con_jd", {}).get("human", {}).get("all", {})
        bdd = r.get("boundary", {}).get("human_minus_agent_unnamed", {})
        lines += ["", "Robustness (content, human): H30 orthogonalized χ " + f"{fmt(h30.get('att'))} {fci(h30.get('ci'))}"
                  + f"; gte-modernbert {fmt(gte.get('att'))} {fci(gte.get('ci'))}; joint per-call deconvolution {fmt(jd.get('att'))} {fci(jd.get('ci'))}"
                  + (f"; H29 boundary design, human − agent jump (unnamed) {fmt(bdd.get('diff'))} {fci(bdd.get('ci'))}" if bdd.get('diff') is not None else "; H29 boundary design: too few human rows at the boundary") + "."
                  + (" Regime-I content premia carry a synthetic null bias of about −0.024 (Amendment A1)." if regime == "I" else " Regime-III content premia carry a synthetic null bias of about −0.006 (Amendment A1).")
                  + f" Bootstrap clusters: {hd.get('con_human', {}).get('cluster', '—')}.",
                  "", f"Data: `data/processed/H52-humans-loud-agents/{p}/` (`rows.parquet`, `boundary.parquet`, `results.json`).",
                  "", "## Scorecard (period-specific axes)",
                  "- C: premium vs the matched-agent null and the placebo-class null (see `results.json`).",
                  "- G: agents' own naming effect reproduces H29/H30's addressed > broadcast where powered.",
                  "", "## Notes",
                  "- Written by `analysis/write_period_folders.py` (replication layer; templated by design)."]
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "figures").mkdir(exist_ok=True)
        (folder / "README.md").write_text("\n".join(lines) + "\n")
        print(p, verdict)


if __name__ == "__main__":
    main()
