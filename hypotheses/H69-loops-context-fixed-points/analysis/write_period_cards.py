"""Write goalperiod-subhypotheses/G<NN>/README.md and NE41/README.md for H69 from results.json.

  uv run python hypotheses/H69-loops-context-fixed-points/analysis/write_period_cards.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CARD = HERE.parent
D = ROOT / "data/processed/H69-loops-context-fixed-points"

META = {
    "G36": ("Interact with other AI agents outside the Village", "2026-03-24 → 03-27 (regime III days)", "C"),
    "G37": ("Pick your own goal!", "2026-03-30 → 04-01", "F"),
    "G38": ("Choose a charity and raise money", "2026-04-02 → 04-24", "C"),
    "G39": ("Build your own interactive world!", "2026-04-27 → 05-01", "I"),
    "G40": ("Connect your worlds into a 3D universe!", "2026-05-04 → 05-08", "C"),
    "G41": ("Perform novel research!", "2026-05-11 → 05-15", "I"),
    "G42": ("Run your own Youtube channel!", "2026-05-18 → 05-22", "I"),
    "G44": ("Finetune your leader!", "2026-05-26 → 05-29", "C"),
    "G51": ("Each agent: maximize your assigned goal", "2026-07-06 → 09-04 (non-holdout)", "P"),
}
NATIVE = {"G38": "the loop week (17 days, the most restatement pairs): P1 and P4 hold here (b_s > 0; enrichment OR ≥ 2).",
          "G51": "operator and human input: a nudge or human message read inside a loop raises exit (OR ≥ 1.5, CI > 1); "
                 "the same classes in flight do not."}


def f(x, d=2):
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "—"
    return f"{x:.{d}f}"


def ci(b, se, d=2, exp=False):
    if b is None or se is None or not (math.isfinite(b) and math.isfinite(se)):
        return "—"
    lo, hi = b - 1.96 * se, b + 1.96 * se
    if exp:
        return f"{math.exp(b):.{d}f} [{math.exp(lo):.{d}f}, {math.exp(hi):.{d}f}]"
    return f"{b:.{d}f} [{lo:.{d}f}, {hi:.{d}f}]"


def sig_pos(b, se):
    return b is not None and se is not None and math.isfinite(b) and math.isfinite(se) and b - 1.96 * se > 0


def verdict(o):
    if not o["scorable"]["episodes"]:
        return "descriptive"
    on, en, ex = o.get("onset") or {}, o.get("enrich") or {}, o.get("exit") or {}
    p1 = sig_pos(on.get("b_s"), on.get("se_s"))
    p4 = en.get("lo") is not None and math.isfinite(en.get("lo", float("nan"))) and en["lo"] > 0 and \
        en["log_or"] >= math.log(2)
    p3 = sig_pos(ex.get("b_forced_between"), ex.get("se_forced_between"))
    p5 = sig_pos(ex.get("b_nov_read"), ex.get("se_nov_read"))
    if p1 and p4 and (p3 or p5):
        return "supported"
    if not p1 and not p4:
        return "failed"
    return "mixed"


def main():
    res = json.loads((D / "results.json").read_text())
    rows = []
    for p, o in res["periods"].items():
        t, dates, mode = META[p]
        role = "native" if p in NATIVE else "replication"
        v = verdict(o)
        if p == "G51":  # native verdict: nudge/human reads end loops (OR >= 1.5, CI > 1)
            k = o.get("exit_kicks") or {}
            b, se = k.get("b_read_nudge"), k.get("se_read_nudge")
            v = "supported" if (b is not None and se is not None and math.isfinite(b) and b - 1.96 * se > 0
                                and math.exp(b) >= 1.5) else "failed"
        ep = o["episodes"]["r_either"]
        on, ex, en, ps = o.get("onset") or {}, o.get("exit") or {}, o.get("enrich") or {}, o.get("pseudo") or {}
        enf = o.get("enrich_forced") or {}
        L = [f"# H69 × {p}: {t} ({dates})", "", f"**Verdict:** {v}", f"**Role:** exploratory · {role}",
             f"**Period:** regime III · mode {mode} · {ep['n_stmt']} chat statements · context segments from the ledger "
             "(41-call forced erasures and voluntary consolidations).", "",
             "## Why this period",
             ("Native: " + NATIVE[p]) if p in NATIVE else "Replication: a regime-III period with ledger context segments.", "",
             "## Prediction",
             "*Written 2026-10-04 19:25 UTC (card), before any H69 statistic.* P1: onset rises with the self-share "
             "(b_s > 0) and falls with room items at fixed own count (b_K < 0). P3: a forced erasure raises exit (OR ≥ 2). "
             "P4: in-context enrichment OR ≥ 2. P5: novel reads raise exit beyond the in-flight and next-call placebos."
             + (f" Native: {NATIVE[p]}" if p in NATIVE else ""), "",
             "## Result", "| Statistic | Value |", "| --- | --- |",
             f"| restatement rate (either model, cross-call) · episodes (≥ 2 in a row) | {f(ep['rate'], 3)} · {ep['n_episodes']} |",
             f"| P(restate · previous restated) vs P(restate · previous not) | {f(ep['p_stay'])} vs {f(ep['p_enter'])} |",
             f"| P1 onset b_s (self-share, logit) [95% CI] | {ci(on.get('b_s'), on.get('se_s'))} (n {on.get('n', '—')}) |",
             f"| P1 split: b_O (own) · b_K (room items) | {ci(on.get('b_O'), on.get('se_O'))} · {ci(on.get('b_K'), on.get('se_K'))} |",
             f"| P2 hinge vs linear ΔAIC (s*) | {f(on.get('dAIC_hinge'), 1)} ({f(on.get('s_star'))}) |",
             f"| P3 exit OR, forced erasure between | {ci(ex.get('b_forced_between'), ex.get('se_forced_between'), exp=True)} "
             f"(n {ex.get('n', '—')}, forced {ex.get('n_forced', '—')}) |",
             f"| exit OR, voluntary erasure between | {ci(ex.get('b_vol_between'), ex.get('se_vol_between'), exp=True)} |",
             f"| P5 exit OR per log(1 + novel reads) · in flight · next call | "
             f"{ci(ex.get('b_nov_read'), ex.get('se_nov_read'), exp=True)} · {ci(ex.get('b_nov_infl'), ex.get('se_nov_infl'), exp=True)}"
             f" · {ci(ex.get('b_nov_read_next'), ex.get('se_nov_read_next'), exp=True)} |",
             f"| P4 in-context enrichment OR (MH) [bootstrap CI] | {f(math.exp(en['log_or']) if en.get('log_or') is not None and math.isfinite(en['log_or']) else None)}"
             f" [{f(math.exp(en['lo']) if en.get('lo') is not None and math.isfinite(en['lo']) else None)}, "
             f"{f(math.exp(en['hi']) if en.get('hi') is not None and math.isfinite(en['hi']) else None)}] ({en.get('n_pairs', '—')} pairs) |",
             f"| enrichment, forced boundaries only | {f(math.exp(enf['log_or']) if enf.get('log_or') is not None and math.isfinite(enf['log_or']) else None)} |",
             f"| pseudo-erasure OR (same vs other half of a segment) | {f(math.exp(ps['log_or']) if ps.get('log_or') is not None and math.isfinite(ps['log_or']) else None)} |",
             "", f"Data: `data/processed/H69-loops-context-fixed-points/{p}/` (`statements`, `items`, `pairs`, `results.json`).", ""]
        if p == "G51" and o.get("exit_kicks"):
            k = o["exit_kicks"]
            L += ["**Native (operator and human input).** Exit OR per log(1 + count):",
                  f"- nudges read {ci(k.get('b_read_nudge'), k.get('se_read_nudge'), exp=True)}; in flight "
                  f"{ci(k.get('b_infl_nudge'), k.get('se_infl_nudge'), exp=True)};",
                  f"- human messages read {ci(k.get('b_read_human'), k.get('se_read_human'), exp=True)}; in flight "
                  f"{ci(k.get('b_infl_human'), k.get('se_infl_human'), exp=True)}.", ""]
        L += ["## Scorecard (period-specific axes)",
              "- **B:** onset and exit separate the self-share from fill (`ctx_pos`) and inflow controls.",
              "- **D:** the enrichment OR and the placebos are unfitted signatures.",
              "- **E:** forced erasures inside the period (NE41) are the intervention.", "",
              "## Notes", "- 2026-10-04: round 1, generated by `analysis/write_period_cards.py`.", ""]
        out = CARD / "goalperiod-subhypotheses" / p
        (out / "figures").mkdir(parents=True, exist_ok=True)
        (out / "README.md").write_text("\n".join(L))
        rows.append((p, role, v))
    # NE41 pooled event-study folder
    po = res["pooled"]
    fo, of_, ef = po["exit_forced"], po["onset_forced"], po["enrich_forced"]
    p_exit = fo.get("lo") is not None and math.isfinite(fo.get("lo", float("nan"))) and fo["lo"] > 0 and fo["mean"] >= math.log(2)
    p_on = of_.get("mean") is not None and math.isfinite(of_.get("mean", float("nan"))) and of_["mean"] <= math.log(0.5)
    v = "supported" if (p_exit and p_on) else ("failed" if not (fo.get("lo", -1) > 0) else "mixed")
    L = ["# H69 × NE41: forced context erasure at the 41-call cap (regime III)", "", f"**Verdict:** {v}",
         "**Role:** exploratory · native",
         "**Period:** all scorable regime-III periods (per-period rows, random-effects pool); exception (c): the "
         "transition is the object.", "",
         "## Why this period", "The scaffold times the erasure (41 calls), not the agent, so the reset is close to "
         "quasi-random given call distance.", "",
         "## Prediction", "*Written 2026-10-04 19:25 UTC (card).* Exit OR ≥ 2 for a forced erasure between two "
         "statements, and the onset rate in the first statement after a forced erasure ≤ 0.5 × the matched rate. Against: "
         "exit OR CI includes 1.", "",
         "## Result", "| Statistic (random-effects pool) | Value |", "| --- | --- |",
         f"| exit OR, forced erasure | {ci(fo.get('mean'), fo.get('se'), exp=True)} (k {fo.get('k')}, I² {f(fo.get('I2'))}) |",
         f"| onset OR, forced erasure since previous statement | {ci(of_.get('mean'), of_.get('se'), exp=True)} (k {of_.get('k')}) |",
         f"| enrichment OR, forced boundaries only | {ci(ef.get('mean'), ef.get('se'), exp=True)} (k {ef.get('k')}) |", "",
         "## Scorecard (period-specific axes)", "- **E:** the forced erasure is the intervention.", "",
         "## Notes", "- 2026-10-04: round 1, generated by `analysis/write_period_cards.py`.", ""]
    out = CARD / "goalperiod-subhypotheses" / "NE41"
    (out / "figures").mkdir(parents=True, exist_ok=True)
    (out / "README.md").write_text("\n".join(L))
    rows.append(("NE41", "native", v))
    (D / "card_rows.json").write_text(json.dumps(rows))


if __name__ == "__main__":
    main()
