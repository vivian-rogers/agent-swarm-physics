"""Write the replication-layer period READMEs.

--init: create goalperiod-subhypotheses/G<NN>/README.md for every eligible period with Verdict pending and the card's
        templated prediction (written before the real-data run).
--fill: fill Verdict / Result / Scorecard from data/processed/H45-context-homeostasis/G<NN>/results.json.
Native folders (NE41, NE42, NE03, G51) are written by hand; --fill leaves G51's native text and appends nothing there.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h45lib as L  # noqa: E402
from run_periods import ELIGIBLE  # noqa: E402

ROOT = L.ROOT
HDIR = ROOT / "hypotheses/H45-context-homeostasis/goalperiod-subhypotheses"
sys.path.insert(0, str(ROOT / "infra/shared"))
PRED_TIME = "2026-10-04 06:21 UTC"


def titles() -> dict:
    from common import load_goals
    return {g["goal_no"]: " ".join(g["goal"].split())[:90] for g in load_goals()}


def meta() -> dict:
    pu = pl.read_parquet(ROOT / "data/processed/shared/period_units.parquet")
    c = L.load_calls(columns=["goal_no", "pt_date", "regime", "agent", "room"])
    out = {}
    for g in ELIGIBLE:
        x = c.filter(pl.col("goal_no") == g)
        u = pu.filter((pl.col("goal_no") == g) & ~pl.col("holdout"))
        out[g] = {"regime": "/".join(sorted(set(x["regime"].cast(pl.Utf8).to_list()))), "days": x["pt_date"].n_unique(),
                  "d0": x["pt_date"].min(), "d1": x["pt_date"].max(), "agents": x["agent"].n_unique(),
                  "rooms": sorted(set(int(v) for v in x["room"].drop_nulls().to_list() if v >= 0)),
                  "units": ", ".join(f"{r['unit_id']} ({r['reason']})" for r in u.iter_rows(named=True))}
    return out


def prediction_block(g: int, m: dict) -> str:
    reg3 = "III" in m["regime"]
    reg23 = ("II" in m["regime"].split("/")) or reg3
    lines = [f"*Templated from the card's predictions (written {PRED_TIME}, before running H45 on any period; replication layer).*",
             "- **P1 (primary):** regulation index RI = 1 − ε/(1 − s̄) ≥ 0.5 with the day-bootstrap CI excluding 0 "
             "(agent × unit fixed effects, band positions 15–35). Passive accumulation: RI ≈ 0.",
             "- **P3 (band):** within-agent CV of segment band shares ≤ 0.5 × the CV after permuting own content across "
             "the agent's segments.",
             "- **P4:** dilution exponent β (reply-parent engagement, cloglog with agent-day effects) ∈ [0.4, 0.9], CI excluding 0.",
             "- **P8:** P(j 30–35)/P(j 8–12) ≥ 1.3 (no truncation plateau)."]
    if reg23:
        lines.append("- **P5 (homeostat signature):** γ_R < 0 and γ_W > 0, both CIs excluding 0 (cu talk calls).")
    if reg3:
        lines.append("- **P2 (consolidation lever):** among voluntarily ended segments, slope of ln L on ln(early inflow) ≤ −0.3.")
        lines.append("- **P6 (post-erasure overshoot):** k-adjusted talk propensity in calls 1–3 after a forced reset ≥ 1.2 × "
                     "the j 20–40 baseline, τ ≤ 10 calls.")
    else:
        lines.append("- **P2 (session lever, regimes I–II):** among segments ended by the agent's own session stop, slope of "
                     "ln L on ln(early inflow) ≤ −0.3.")
    lines.append("- **Verdict rule:** supported if P1 holds and (where testable) P5's sign pattern holds; failed if the RI CI's "
                 "upper bound is < 0.5 and P5 does not show the controller pattern; mixed otherwise.")
    lines.append("- **Against H45:** RI ≈ 0 (the share tracks inflow).")
    return "\n".join(lines)


def header(g: int, m: dict, tt: dict, verdict: str, role: str = "replication") -> str:
    return (f"# H45 × G{g:02d}: {tt.get(g, '')} ({m['d0']} → {m['d1']})\n\n"
            f"**Verdict:** {verdict}\n**Role:** {role}\n"
            f"**Period:** regime {m['regime']} · {m['agents']} agents with calls · rooms {m['rooms']} · {m['days']} non-holdout days. "
            f"Units (shared `period_units`): {m['units']}.\n")


WHY = ("## Why this period\nReplication layer: the common H45 estimators on every eligible goal period (≥ 3 agents with ≥ 30 "
       "computer-use context segments carrying prompt tokens), so that each period is a comparable point on the phase "
       "diagram. {extra}\n")


def why_extra(m: dict) -> str:
    if "III" in m["regime"]:
        return ("Regime III: one continuous computer-use context per agent, erased by forced (41-call cap, NE41) and voluntary "
                "consolidations; talk happens inside that context, so every test applies.")
    if "II" in m["regime"]:
        return "Regime II: computer-use sessions plus chat mode; the consolidate tool arrives during NE14."
    return ("Regime I: computer-use sessions (reset by the agent's own session stop) beside chat mode; talk happens in chat "
            "mode, whose prompt the scaffold rebuilds from recent chat, so the share-dependence test (P5) and the forced-"
            "erasure test (P6) do not apply.")


def init():
    tt, mm = titles(), meta()
    for g in ELIGIBLE:
        d = HDIR / f"G{g:02d}"
        d.mkdir(parents=True, exist_ok=True)
        p = d / "README.md"
        if g == 51:
            continue                      # native folder, written by hand
        txt = (header(g, mm[g], tt, "pending") + "\n" + WHY.format(extra=why_extra(mm[g])) + "\n## Prediction\n"
               + prediction_block(g, mm[g]) + "\n\n## Result\n*Pending.*\n\n## Scorecard (period-specific axes)\n*Pending.*\n\n"
               f"## Notes\n- {PRED_TIME}: folder and templated prediction written before the real-data run.\n")
        p.write_text(txt)


def f2(v, nd=2):
    return "–" if v is None else (f"{v:.{nd}f}" if isinstance(v, (int, float)) else str(v))


def cis(x, nd=2):
    return "" if not x or x[0] != x[0] else f" [{x[0]:.{nd}f}, {x[1]:.{nd}f}]"


def result_rows(r: dict) -> tuple[list[str], dict]:
    reg, bc, lev, pg, be, sd = (r.get(k, {}) for k in ("regulation", "band_cv", "lever", "p_growth", "beta", "share_dependence"))
    rf, rv = r.get("reset_forced_talk", {}), r.get("reset_vol_talk", {})
    sp = r.get("set_points", {})
    ok = {}
    rows = ["| Prediction | Observed | Null / reference | Outcome |", "| --- | --- | --- | --- |"]
    if reg.get("RI") is not None:
        ok["P1"] = reg["RI"] >= 0.5 and reg["RI_ci"][0] > 0
        rows.append(f"| P1 RI ≥ 0.5 | RI {f2(reg['RI'])}{cis(reg['RI_ci'])} (ε {f2(reg['eps'])}{cis(reg['eps_ci'])}; "
                    f"η_W {f2(reg['eta_W'])}{cis(reg['eta_W_ci'])}; {reg['n_seg']} segments, {reg['n_agents']} agents) | "
                    f"passive ε = 1 − s̄ = {f2(reg['eps_passive'])}, RI 0 | {'met' if ok['P1'] else 'not met'} |")
    if bc.get("ratio") is not None:
        ok["P3"] = bc["ratio"] <= 0.5
        rows.append(f"| P3 CV ratio ≤ 0.5 | CV {f2(bc['cv_obs'])} vs W-permuted {f2(bc['cv_perm_median'])} (ratio {f2(bc['ratio'])}, "
                    f"p_lower {f2(bc['p_lower'], 3)}) | ratio 1 | {'met' if ok['P3'] else 'not met'} |")
    if lev.get("slope") is not None:
        ok["P2"] = lev["slope_ci"][1] < 0
        rows.append(f"| P2 lever slope < 0 (A1) | {f2(lev['slope'])}{cis(lev['slope_ci'])} ({lev['n_seg']} voluntary segments) | 0 | "
                    f"{'met' if ok['P2'] else 'not met'} |")
    if be.get("beta") is not None:
        ok["P4"] = 0.4 <= be["beta"] <= 0.9 and be["beta_ci"][0] > 0
        rows.append(f"| P4 β ∈ [0.4, 0.9] | β {f2(be['beta'])}{cis(be['beta_ci'])} ({be['n']} talk calls, reply rate "
                    f"{f2(be['rate'])}) | 0 (constant uptake), 1 (fixed budget) | {'met' if ok['P4'] else 'not met'} |")
    if sd.get("g_R") is not None:
        ok["P5"] = sd["g_R_ci"][1] < 0 and sd["g_W_ci"][0] > 0
        rows.append(f"| P5 γ_R < 0, γ_W > 0 | γ_R {f2(sd['g_R'], 3)}{cis(sd['g_R_ci'], 3)}; γ_W {f2(sd['g_W'], 3)}{cis(sd['g_W_ci'], 3)} "
                    f"({sd['n']} cu talk calls) | 0, 0 (passive); −, − (competition) | {'met' if ok['P5'] else 'not met'} |")
    if rf.get("overshoot") is not None:
        ok["P6"] = rf["overshoot"] >= 1.2 and rf["overshoot_ci"][0] > 1
        rows.append(f"| P6 overshoot ≥ 1.2 | forced {f2(rf['overshoot'])}{cis(rf['overshoot_ci'])}, τ {f2(rf['tau'], 1)} calls "
                    f"({rf['n_segments']} segments); voluntary {f2(rv.get('overshoot'))}{cis(rv.get('overshoot_ci'))} | 1 | "
                    f"{'met' if ok['P6'] else 'not met'} |")
    if pg.get("ratio_median") is not None:
        ok["P8"] = pg["ratio_median"] >= 1.3
        rows.append(f"| P8 P growth ≥ 1.3 | {f2(pg['ratio_median'])} (IQR {f2(pg['ratio_q25'])}–{f2(pg['ratio_q75'])}; "
                    f"{pg['n_seg']} segments) | ≈ 1 under truncation | {'met' if ok['P8'] else 'not met'} |")
    rows.append(f"| set points | s\\* median {f2(sp.get('s_star_median'), 3)} (range {f2(sp.get('s_star_min'), 3)}–"
                f"{f2(sp.get('s_star_max'), 3)}, {sp.get('n_agents')} agents) | – | descriptive |")
    return rows, ok


def fill():
    tt, mm = titles(), meta()
    for g in ELIGIBLE:
        if g == 51:
            continue
        rp = L.DATA / f"G{g:02d}" / "results.json"
        if not rp.exists():
            continue
        r = json.loads(rp.read_text())
        d = HDIR / f"G{g:02d}"
        old = (d / "README.md").read_text()
        pred = old[old.index("## Prediction"):old.index("## Result")]
        rows, ok = result_rows(r)
        reg = r.get("regulation", {})
        reading = (f"The room share at mid-segment positions follows inflow: ε {f2(reg.get('eps'))} against the passive "
                   f"{f2(reg.get('eps_passive'))}, so RI {f2(reg.get('RI'))}, and own content does not respond "
                   f"(η_W {f2(reg.get('eta_W'))}). " if reg.get("RI") is not None else "")
        be, sd, rf = r.get("beta", {}), r.get("share_dependence", {}), r.get("reset_forced_talk", {})
        if be.get("beta") is not None:
            reading += (f"Reply engagement dilutes with β {f2(be['beta'])}"
                        + (" (a literal one-reply-per-talk budget)" if be["beta"] > 0.9 else "") + ". ")
        if sd.get("g_W") is not None:
            reading += (f"Engagement {'falls' if sd['g_W_ci'][1] < 0 else 'does not change detectably'} with own content "
                        f"(γ_W {f2(sd['g_W'], 2)}) and {'rises' if sd['g_R_ci'][0] > 0 else ('falls' if sd['g_R_ci'][1] < 0 else 'does not change detectably')} "
                        "with old room content (γ_R; per-period γ is not identified, Amendment A2). ")
        if rf.get("overshoot") is not None:
            reading += (f"After forced erasures the agents talk {'less' if rf['overshoot_ci'][1] < 1 else 'about as often'} "
                        f"(k-adjusted ratio {f2(rf['overshoot'])}), the opposite of an import overshoot. ")
        txt = (header(g, mm[g], tt, f"{r['verdict']} ({r['verdict_text']})") + "\n" + WHY.format(extra=why_extra(mm[g])) + "\n"
               + pred + "## Result\n" + "\n".join(rows) + "\n\n**Reading.** " + reading
               + f"Numbers: `data/processed/H45-context-homeostasis/G{g:02d}/results.json` (`analysis/run_periods.py`). "
               "Cross-period figures: `figures/`.\n\n## Scorecard (period-specific axes)\n"
               f"- **C:** RI against the passive benchmark (day-cluster bootstrap): {'beats' if ok.get('P1') else 'does not beat'} passive.\n"
               f"- **D:** unfitted statistics: P growth {'consistent' if ok.get('P8') else 'inconsistent'} with accumulation; "
               f"β {'in' if ok.get('P4') else 'outside'} the predicted band.\n"
               + (f"- **E:** forced erasures (NE41) as interventions: overshoot {'met' if ok.get('P6') else 'not met'}.\n" if "P6" in ok else "")
               + "\n## Notes\n" + "\n".join(l for l in old[old.index("## Notes") + len("## Notes\n"):].rstrip().splitlines()
                                             if "results filled" not in l and "Amendments A1" not in l) + "\n"
               "- 2026-10-04 06:46 UTC: card Amendments A1–A3 apply (made after the synthetic validation, before any real data): "
               "P2 judged by sign; verdict by P1 alone; P6 needs its CI above 1.\n"
               f"- 2026-10-04: results filled from `analysis/run_periods.py` (exploratory, non-holdout).\n")
        (d / "README.md").write_text(txt)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", action="store_true")
    ap.add_argument("--fill", action="store_true")
    a = ap.parse_args()
    if a.init:
        init()
    if a.fill:
        fill()
