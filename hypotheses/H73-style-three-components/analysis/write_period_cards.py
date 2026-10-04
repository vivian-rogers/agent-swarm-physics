"""Write H73 goal-period / NE READMEs.

--phase predict : creates every README with Verdict pending and the dated prediction (before the real-data run).
--phase results : rewrites Verdict / Result / Scorecard from the result JSONs, keeping the prediction section verbatim.
Replication READMEs are templated on purpose (layer 1). Native READMEs carry hand-written predictions (NATIVE_PRED).
"""
from __future__ import annotations
import argparse
import json
import re

import numpy as np
import polars as pl

import h73lib as L

PDIR = L.HYP / "goalperiod-subhypotheses"
NATIVE_G = {12, 44, 51}
PRED_STAMP = "2026-10-04 19:28 UTC"

REPL_PRED = f"""*Written {PRED_STAMP}, before running on this period. Templated replication prediction (layer 1), the same for every period.*
- **O1 decomposition** (17-d type-controlled style; blocks: day field + time of day G, agent constant A, context C, register R where defined): the three components explain most of the non-day-field systematic variance, F3 ≥ 0.57 (0.5 plus the synthetic bias margin, Amendment A2).
- **Ordering:** the agent constant has the largest unique share (u_A > u_C, u_R). With ≥ 500 computer-use messages, the context share is positive (within-agent-day permutation p < 0.05).
- **O2 attribution** (leave-one-day-out, blocks of 5 messages): the agent-specific context model beats the blind centroid, Δ_c > 0.
- **O3 dispersion** (descriptive unless ≥ 2,000 computer-use messages): residual dispersion rises with context fill.
- **Verdict rule:** supported if F3 ≥ 0.57, u_A is the largest unique share and Δ_c > 0 (plus p_C < 0.05 where n_cu ≥ 500); failed if F3 < 0.5 and Δ_c ≤ 0; otherwise mixed.
- *Counts against:* F3 < 0.5 (agent-day jitter carries most systematic style variance) and no attribution gain from the context model."""

NATIVE_PRED = {
    "NE41": f"""*Written {PRED_STAMP}, before running on these data.*
- **Design:** consecutive eligible chat messages of one agent on one PT day in regime III (non-holdout), labelled forced / voluntary / within by the resets between their producing calls (DQ1 ledger flags). The context profile (bin levels and agent slopes on z = log2(1 + fill)) is fitted on within pairs of one day parity and evaluated on the other (Amendment A1).
- **N1 prediction:** the fitted drift predicts the forced-erasure jump: β ∈ [0.3, 1.5] with the agent-cluster CI excluding 0. Subtracting the predicted jump lowers the gap-matched forced-pair style percentile T_s by at least half of its excess over ½.
- **Expected:** β around 0.3–0.6 (part drift, part excursion); T_s raw about 0.55–0.57 (H46: 0.564).
- *Counts against:* β CI including 0, which means the erasure effect is not the reversal of a directed drift (R5, the directionless excursion; synthetic S2 gives T_s 0.556 with β ≈ 0).""",
    "G12": f"""*Written {PRED_STAMP}, before running on this period.*
- **Registers (DQ6):** judge (inside a debate window the agent judges), debater (inside a window where it has a team), outside. Judges: agents 6, 5, 11, 0 (one debate each) and 9 (debates 5–10).
- **N2 predictions:** (i) the register block has a positive unique share u_R (judge-label permutation within agent, p < 0.05). (ii) Judging is a shared register: the mean cosine between a judge's own judge shift and the leave-this-agent-out mean shift of the other judges is > 0 (permutation p < 0.05). (iii) Adding the leave-agent-out judge shift to every candidate centroid raises attribution of judge-window messages (blocks of 5) by ≥ 0.05.
- **Replication layer:** the templated O1–O3 rule also applies (reported, not the native verdict).
- *Counts against:* mean cosine ≤ 0 (each judge moves in its own direction: the register is agent-specific, not assigned).""",
    "G51": f"""*Written {PRED_STAMP}, before running on this period.*
- **Design:** incumbents with ≥ 20 eligible messages in #36–#44 (non-holdout, regime III) and in #51 07-06 → 07-24. Joint fit on #36–#44 + #51 07-06 → 07-24: day field, time of day, agent constant, context, and an agent-specific #51 shift R_i (the register; exception (c), the transition is the object). Placebo shifts: the same contrast at calendar splits that do not straddle 07-06 (inside #36–#44 and inside #51 07-06 → 09-06), each with a three-week post window.
- **N3 predictions:** (i) the Prankster's (agent 10) unbiased ‖R_i‖² stays above its placebo shifts (percentile ≥ 0.95) after the context component is removed. (ii) The four incumbent media agents (12, 16, 18, 22; three labs) share a register direction: their mean pairwise cosine of R_i exceeds that of the other incumbent pairs (role-label permutation p < 0.05). Prior for (ii): 40%.
- **Replication layer:** the templated O1–O3 rule on #51 non-holdout (registers are agent-constant inside #51, so u_R is not identified there).
- *Counts against:* (i) percentile < 0.9 after detrending (the persona shift was context); (ii) p ≥ 0.05 (registers are role- or agent-specific, not shared by class).""",
    "G44": f"""*Written {PRED_STAMP}, before running on this period.*
- **Design (model swap, the weights component):** the temporary fine-tuned leader (agent 28; base Kimi K2.6 self-distilled, H23) posts in #44. Centroids: every main agent's regime-III messages in #36–#44 (non-holdout), day-centred; the leader's messages form one block.
- **N4 prediction (descriptive):** base Kimi K2.6 (agent 25) ranks ≤ 2 of about 17 centroids, blind and after context detrending, and detrending does not lower its rank. H46 found rank 2 (raw style rank 1) blind.
- **Replication layer:** the templated O1–O3 rule also applies (reported, not the native verdict).
- *Counts against:* Kimi rank > 3 under both variants (the fine-tune moved the weights component away from its base).""",
}


def titles() -> dict:
    t = {}
    for line in (L.ROOT / "hypotheses/hypohypotheses/goal-periods.md").read_text().splitlines():
        m = re.match(r"^### (\d+) · (.+)$", line)
        if m:
            t[int(m.group(1))] = m.group(2).strip()
    return t


def period_info(goals) -> dict:
    m = L.load_messages()
    pu = pl.read_parquet(L.SH / "period_units.parquet").filter(~pl.col("holdout"))
    info = {}
    for g in goals:
        mm = m.filter(pl.col("goal_no") == g)
        u = pu.filter(pl.col("goal_no") == g).sort("start")
        info[g] = {"regime": mm["regime"][0], "n_agents": int(mm["agent"].n_unique()), "n_days": int(mm["pt_date"].n_unique()),
                   "n": mm.height, "n_cu": int((mm["ctx_mode"] == "cu").sum()),
                   "first": u["first_day"].min(), "last": u["last_day"].max(), "units": ", ".join(u["unit_id"].to_list())}
    return info


def header(g, info, ttl, role, verdict="pending"):
    i = info[g]
    return (f"# H73 × G{g:02d}: {ttl.get(g, '')} ({i['first']} → {i['last']})\n\n**Verdict:** {verdict}\n"
            f"**Role:** {role} (exploratory)\n**Period:** regime {i['regime']} · {i['n_agents']} agents with eligible "
            f"messages · {i['n_days']} days · {i['n']:,} eligible messages ({i['n_cu']:,} in computer-use mode) · units "
            f"{i['units']}.\n")


def why(g):
    if g in NATIVE_G:
        return {12: "Native: the only non-holdout period with an assigned, rotating speech register inside the period (debate judges), so the register component is identified within agent.",
                51: "Native: private roles assigned on 07-06 (Prankster, media roles) are the cleanest assigned registers in the record; the persona onset is the intervention.",
                44: "Native: the fine-tuned leader is a weights swap on a known base (Kimi K2.6), the only non-holdout model swap (NE30 is held out)."}[g]
    return "A replication point for the common estimator (layer 1): every eligible goal period gets the same statistics, so periods are comparable points, not independent tests."


def eligible_goals():
    m = L.load_messages()
    e = m.group_by("goal_no", "agent").len().filter(pl.col("len") >= 30).group_by("goal_no").len()
    c = m.group_by("goal_no").agg((pl.col("ctx_mode") == "cu").sum().alias("n_cu"))
    t = c.join(e, on="goal_no").filter((pl.col("len") >= 3) & (pl.col("n_cu") >= 100))
    return sorted(t["goal_no"].to_list())


def predict():
    goals = eligible_goals()
    ttl = titles()
    info = period_info(goals)
    for g in goals:
        d = PDIR / f"G{g:02d}"
        (d / "figures").mkdir(parents=True, exist_ok=True)
        (d / "figures" / ".gitkeep").touch()
        role = "native" if g in NATIVE_G else "replication"
        pred = NATIVE_PRED[f"G{g:02d}"] + "\n\n**Templated replication prediction (also reported):**\n" + REPL_PRED if g in NATIVE_G else REPL_PRED
        txt = (header(g, info, ttl, role) + f"\n## Why this period\n{why(g)}\n\n## Prediction\n{pred}\n\n## Result\n*Pending.*\n\n"
               "## Scorecard (period-specific axes)\n*Pending.*\n")
        (d / "README.md").write_text(txt)
    d = PDIR / "NE41"
    (d / "figures").mkdir(parents=True, exist_ok=True)
    (d / "figures" / ".gitkeep").touch()
    txt = ("# H73 × NE41: forced context erasure at the 41-turn cap (regime III, non-holdout units)\n\n**Verdict:** pending\n"
           "**Role:** native (exploratory)\n**Period:** regime III units #36b–#51 (non-holdout days); turn level.\n\n"
           "## Why this period\nThe scaffold erases the context at a fixed record count, not when the agent chooses. "
           "That is the cleanest exogenous intervention on the context component.\n\n"
           f"## Prediction\n{NATIVE_PRED['NE41']}\n\n## Result\n*Pending.*\n\n## Scorecard (period-specific axes)\n*Pending.*\n")
    (d / "README.md").write_text(txt)
    print(f"wrote {len(goals)} G folders + NE41")


def fmt(x, nd=2):
    return "nan" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:.{nd}f}"


def repl_lines(r):
    d, a5, dis = r["dec"], r["att"].get("5") or {}, r["disp"]
    lines = [f"- **Sample:** {d['n']:,} messages, {d['n_agents']} agents, {d['n_days']} days, {d['n_cu']:,} computer-use; {d['n_cells']:,} cells.",
             f"- **Ceiling κ** (adjusted R² of agent × day × context bin × register cells): {fmt(d['kappa'], 3)}; day field + time of day R²: {fmt(d['r2a']['G'], 3)}.",
             f"- **F3** = {fmt(d['F3'])} [{fmt(r['F3_ci'][0])}, {fmt(r['F3_ci'][1])}] (delete-one-day jackknife, ±1.96 SE); unique shares u_A {fmt(d['u_A'])}, u_C {fmt(d['u_C'], 3)} (permutation p {fmt(d.get('p_C'), 3)}; null-corrected {fmt(d.get('u_C_nullcorr'), 3)})"
             + (f", u_R {fmt(d['u_R'], 3)}" if d.get("u_R") == d.get("u_R") and d.get("u_R") is not None else "") + "."]
    if a5:
        lines.append(f"- **Attribution** (blocks of 5, {a5['n_blocks']} blocks, chance {fmt(a5['chance'])}): blind {fmt(a5['blind'])}, common-detrended {fmt(a5['det'])}, agent-specific context {fmt(a5['agent'])}; Δ_c = {a5['gain_agent']:+.3f}, Δ_b = {a5['gain_det']:+.3f}.")
    if dis.get("slope") == dis.get("slope") and dis.get("slope") is not None:
        lines.append(f"- **Dispersion slope** (residual ‖e‖² per unit z, relative to mean ‖e‖²): {dis['slope_rel']:+.3f} (CI on raw slope [{fmt(dis['lo'])}, {fmt(dis['hi'])}]){'' if dis['n_cu'] >= 2000 else ', descriptive (n_cu < 2,000)'}.")
    lines.append(f"- **Templated verdict:** {r['verdict']}.")
    return lines


def results():
    rep = json.loads((L.DATA / "replication" / "replication.json").read_text())
    nat = json.loads((L.DATA / "natives" / "natives.json").read_text())
    stamp = rep["_meta"]["run_at"]
    for key, r in rep.items():
        if key.startswith("_"):
            continue
        g = int(key[1:])
        p = PDIR / key / "README.md"
        txt = p.read_text()
        res = [f"*Run {stamp} (`analysis/replication.py` → `data/processed/H73-style-three-components/replication/replication.json`). Templated replication point.*", ""] + repl_lines(r)
        verdict = r["verdict"]
        score = "- Replication point only (layer 1): informs C (beats the G + A baseline at the ceiling) and I (consistency across periods) in the main card."
        if g in NATIVE_G:
            nk = f"G{g:02d}"
            res = nat[nk]["lines"] + ["", "**Replication layer (templated):**"] + repl_lines(r)
            verdict = nat[nk]["verdict"]
            score = nat[nk]["score"]
        txt = re.sub(r"\*\*Verdict:\*\* \w+", f"**Verdict:** {verdict}", txt, count=1)
        txt = re.sub(r"## Result\n.*?\n## Scorecard", "## Result\n" + "\n".join(res).replace("\\", "\\\\") + "\n\n## Scorecard", txt, flags=re.S)
        txt = re.sub(r"## Scorecard \(period-specific axes\)\n.*$", "## Scorecard (period-specific axes)\n" + score.replace("\\", "\\\\") + "\n", txt, flags=re.S)
        p.write_text(txt)
    p = PDIR / "NE41" / "README.md"
    txt = p.read_text()
    txt = re.sub(r"\*\*Verdict:\*\* \w+", f"**Verdict:** {nat['NE41']['verdict']}", txt, count=1)
    txt = re.sub(r"## Result\n.*?\n## Scorecard", "## Result\n" + "\n".join(nat["NE41"]["lines"]).replace("\\", "\\\\") + "\n\n## Scorecard", txt, flags=re.S)
    txt = re.sub(r"## Scorecard \(period-specific axes\)\n.*$", "## Scorecard (period-specific axes)\n" + nat["NE41"]["score"].replace("\\", "\\\\") + "\n", txt, flags=re.S)
    p.write_text(txt)
    print("results written")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["predict", "results"], required=True)
    a = ap.parse_args()
    predict() if a.phase == "predict" else results()
