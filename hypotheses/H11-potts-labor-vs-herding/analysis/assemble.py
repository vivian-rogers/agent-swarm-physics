"""Assemble round-1 verdicts: per-period results.json (for G<NN>/README.md), card tables, cross-period tests.

Verdict rules are the ones written in the card on 2026-10-03 (before the real-data run). Post-hoc quantities
(local-shift null, ownership index, drift-corrected excess, G26 pre-jump snapshot) are labeled as such.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h11common as HC  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import potts_core as P  # noqa: E402
from h11data import load_period  # noqa: E402

ALLC = {**HC.CANDIDATES, **HC.TRANSFER}


def f2(x, d=2):
    return "–" if x is None or (isinstance(x, float) and not math.isfinite(x)) else f"{x:+.{d}f}" if isinstance(x, float) else str(x)


def ownership(g):
    """Post hoc: share of labeled agent-windows on real projects that one agent dominates (>= 80% of that project's
    agent-windows), using raw project names; plus mean number of distinct agents per project."""
    s, df = load_period(g)
    d = df.filter(pl.col("project").is_not_null())
    c = d.group_by("project", "agent").agg(pl.len().alias("n"))
    t = c.group_by("project").agg(pl.col("n").sum().alias("tot"), pl.col("n").max().alias("top"), pl.len().alias("n_ag"))
    t = t.with_columns((pl.col("top") / pl.col("tot")).alias("own"))
    owned = t.filter(pl.col("own") >= 0.8)["tot"].sum() / t["tot"].sum()
    return float(owned), float((t["n_ag"] * t["tot"]).sum() / t["tot"].sum())


def p1_verdict(cls, o1):
    if cls.startswith("none"):
        return "descriptive"
    want = -1 if cls == "AF" else +1
    sgn = np.sign(o1["bj"])
    sig = abs(o1["t"]) > o1["tcrit"] if o1["t"] is not None and math.isfinite(o1["t"]) else False
    if sgn == want and sig:
        return "supported"
    if sgn == want:
        return "weak"
    return "failed (significant)" if sig else "failed"


def p2_verdict(cls, z):
    if cls.startswith("none"):
        return "descriptive"
    if z is None or not math.isfinite(z):
        return "n/a"
    if cls == "AF":
        return "supported" if z <= -1.96 else ("weak" if z <= 0 else ("failed (significant)" if z >= 1.96 else "failed"))
    return "supported" if z >= 1.96 else ("weak" if z > 0 else "failed")


def main():
    RR = {}
    for f in sorted(HC.OUT.glob("G*/round1.json")):
        R = json.loads(f.read_text())
        RR[R["goal"]] = R
    LS = {int(k): v for k, v in json.loads((HC.OUT / "local_shift_posthoc.json").read_text()).items()}
    rows = []
    for g, R in sorted(RR.items()):
        cls = R["cls"]
        row = dict(goal=g, cls=cls, tested=R.get("tested", False), blocks3=R["blocks3"], n_obs=R["n_obs"], q=R["q"])
        if not R.get("tested"):
            row["p1"] = row["p2"] = "n/a (insufficient labels)"
            rows.append(row)
            continue
        o1, o2 = R["O1"], R["O2"]
        own, nag = ownership(g)
        row.update(bj_cw=o1["bj"], se_cw=o1["se"], t_cw=o1["t"], tcrit=o1["tcrit"], z_cw_N1=o1["z_N1"], N1_mean=o1["N1_mean"],
                   bj_pl=o2["bj"], N2_mean=o2["N2_mean"], excess=o2["bj"] - o2["N2_mean"], z_N2=o2["z_N2"], z_N1d=o2["z_N1d"],
                   z_N1=o2["z_N1"], z_loc1=LS[g]["z_local1"], R=R["O3"]["R"], persist=R["persist"],
                   act_bj=R["O6"]["bj_cw"], act_t=R["O6"]["t_cw"], act_z=R["O6"]["z_N2"],
                   dll_pos=R["O7"].get("dll_pos"), folds=R["O7"].get("folds"), plm_z=R["O8"]["z_N1"],
                   jump=R["O45"].get("verdict"), amp=R["O45"].get("amp"), tau=R["O45"].get("tau"),
                   pers=R["O45"].get("persistence_below_mid"), qeff=R["O45"].get("qeff"), bj_s=R["O45"].get("bj_s"),
                   x_last=R["O45"].get("x_last"), mf_region=R["O45"].get("first_order_region"),
                   own=own, n_ag_per_proj=nag,
                   rob_raw=R["O9"].get("raw", {}).get("bj_cw"), rob_W15=R["O9"].get("W15", {}).get("bj_cw"),
                   rob_W60=R["O9"].get("W60", {}).get("bj_cw"), rob_act=R["O9"].get("action_only", {}).get("bj_cw"),
                   rob_q4=R["O9"].get("q4", {}).get("bj_cw"), rob_day=R["O9"].get("cw_day", {}).get("bj_cw"),
                   rob_pool=R["O9"].get("pooled_rooms", {}).get("bj_cw"))
        row["p1"] = p1_verdict(cls, o1)
        row["p2"] = p2_verdict(cls, o2["z_N2"])
        rows.append(row)
    df = pl.DataFrame(rows, infer_schema_length=None)
    df.write_parquet(HC.OUT / "verdicts_round1.parquet")
    t = df.filter(pl.col("tested"))
    af = t.filter(pl.col("cls") == "AF")["bj_cw"].to_numpy()
    fm = t.filter(pl.col("cls").str.starts_with("FM"))["bj_cw"].to_numpy()
    mw = stats.mannwhitneyu(af, fm, alternative="less")
    afz = t.filter(pl.col("cls") == "AF")["z_N2"].to_numpy()
    fmz = t.filter(pl.col("cls").str.starts_with("FM"))["z_N2"].to_numpy()
    mwz = stats.mannwhitneyu(afz, fmz, alternative="less")
    pred = t.filter(~pl.col("cls").str.starts_with("none"))
    correct = int(((pred["cls"] == "AF") & (pred["bj_cw"] < 0)).sum() + ((pred["cls"] != "AF") & (pred["bj_cw"] > 0)).sum())
    sign_p = stats.binomtest(correct, pred.height, 0.5, alternative="greater").pvalue
    rho_own = stats.spearmanr(t["own"].to_numpy(), t["bj_cw"].to_numpy())
    rho_own_z = stats.spearmanr(t["own"].to_numpy(), t["z_N2"].to_numpy())
    act_af = t.filter(pl.col("cls") == "AF")["act_bj"].to_numpy()
    act_fm = t.filter(pl.col("cls").str.starts_with("FM"))["act_bj"].to_numpy()
    mwa = stats.mannwhitneyu(act_af, act_fm, alternative="two-sided")
    cross = dict(mw_af_lt_fm_bjcw_p=float(mw.pvalue), mw_af_lt_fm_zN2_p=float(mwz.pvalue), sign_correct=correct, sign_n=pred.height,
                 sign_p=float(sign_p), spearman_own_bjcw=[float(rho_own.statistic), float(rho_own.pvalue)],
                 spearman_own_zN2=[float(rho_own_z.statistic), float(rho_own_z.pvalue)],
                 act_af_vs_fm_p=float(mwa.pvalue), af_bjcw=af.tolist(), fm_bjcw=fm.tolist())
    (HC.OUT / "cross_period_round1.json").write_text(json.dumps(cross, indent=1))
    pl.Config.set_tbl_rows(40)
    pl.Config.set_tbl_cols(40)
    pl.Config.set_tbl_width_chars(250)
    pl.Config.set_float_precision(2)
    print(df.select("goal", "cls", "blocks3", "bj_cw", "t_cw", "z_cw_N1", "bj_pl", "excess", "z_N2", "z_loc1", "R", "act_bj", "own", "jump", "p1", "p2"))
    print(json.dumps(cross, indent=1))
    write_period_results(RR, df, LS)


NOTES = {
    19: "- 2026-10-03 (round 1): the project label tracks the build repo (`o3-ux/daily-puzzle`). It held about 0.6 of labeled agent-windows from the first windows, so the concept choice (HH25) happened before or outside the artifact record. Concept-mention states from chat are needed to test HH25 (round 2). The P3 'none' verdict is the frozen-consensus case in synthetic S3, not evidence of a gradual choice.",
    31: "- 2026-10-03 (round 1, post hoc): the pre-registered rule picked the final-day dominant repo (`village-event-log`), not the narrative's `civic-safety-guardrails`. The guardrails repo was touched by 11 agents, with a peak of 8 in one window, but its share shows no step (verdict 'none'). `village-time-capsule` peaked at 11 agents in one window, then declined. So #31 is a sequence of herding waves onto shared repos, not one consensus. Details: `data/processed/H11-potts-labor-vs-herding/G31/posthoc_named_projects.json`.",
    40: "- 2026-10-03 (round 1): `the-universe` hub held 0.74 of labeled agent-windows from the start, and each agent also kept its own world repo. The occupancy is far steadier than binomial, so the uniform-field βJ_CW is strongly negative. That is specialization through fields (N1 reproduces it: N1 mean −15.6). βJ_PL against N2 is ≈ 0. The a-priori FM-consensus class was wrong for this week: the 'consensus' (the hub) was given by the goal, not reached.",
    18: "- 2026-10-03 (round 1): the final-day dominant repo (`o3-ux/poverty-etl`) jumps from ≈ 0 to ≈ 1 on the last day, a deadline-driven convergence in a week predicted to be AF.",
    26: "- 2026-10-03 (round 1): the project labels (mostly ballot Google Docs) are not the consensus variable. The declared votes are. The pre-registered runoff-onset rule (≥ 2 'runoff' messages in a window) fired on day 1, long before the decisive vote at window ≈ 27, so P-G26a measured an early state.",
    38: "- 2026-10-03 (round 1): 17 days and 246 blocks give high power. βJ_CW is +4.3, but the within-day excess is small (βJ_PL − N2 mean = +0.4; z_N2 = +2.1; ±1-window local shift z = +1.2), so most of the positive βJ_CW here is day-scale structure.",
}


def write_period_results(RR, df, LS):
    for row in df.iter_rows(named=True):
        g = row["goal"]
        R = RR[g]
        res = {}
        if not row["tested"]:
            d = LS.get(g, {})
            md = (f"Not tested: {row['blocks3']} room blocks with ≥ 3 labeled agents (minimum 15), from {row['n_obs']} labeled agent-windows.\n")
            if "desc_bj_cw" in d:
                md += (f"\n*Descriptive only (below the minimum-data rule):* βJ_CW = {d['desc_bj_cw']:+.2f} (jackknife SE {d['desc_se_cw']:.2f}); "
                       f"βJ_PL = {d['bj_pl']:+.2f}, z vs N2 = {d['desc_z_N2']:+.2f}. The sign is opposite to the AF prediction, but "
                       "this does not count as a test.\n")
            res = dict(verdict="n/a (insufficient labels)", result_md=md,
                       scorecard_md="No period-specific axes scored (insufficient labels).",
                       notes_md=("- 2026-10-03 (round 1): only 28% of agent-windows carry a strict artifact mention (mostly Google Docs/Forms/Sheets), "
                                 "so the HH24 test of this period needs a different state variable (e.g. chat-declared task assignments)." if g == 13 else ""))
            (HC.OUT / f"G{g:02d}" / "results.json").write_text(json.dumps(res, indent=1))
            continue
        cls = row["cls"]
        o45 = R["O45"]
        lines = ["| Test | Prediction | Observed | Null / reference | Verdict |", "| --- | --- | --- | --- | --- |"]
        want = "< 0" if cls == "AF" else ("> 0" if cls.startswith("FM") else "none")
        lines.append(f"| P1 βJ_CW (primary) | {want} | {row['bj_cw']:+.2f} (jackknife SE {row['se_cw']:.2f}, t = {row['t_cw']:+.2f}, t_crit {row['tcrit']:.2f}) | "
                     f"βJ = 0; N1 (within-agent permutation) mean {row['N1_mean']:+.2f}, z_N1 = {row['z_cw_N1']:+.1f} | **{row['p1']}** |")
        want2 = "z ≤ 0" if cls == "AF" else ("z ≥ +2" if cls.startswith("FM") else "none")
        lines.append(f"| P2 βJ_PL (agent fields) | {want2} | {row['bj_pl']:+.2f}; z_N2 = {row['z_N2']:+.2f}, z_N1d = {row['z_N1d']:+.2f}, z_N1 = {row['z_N1']:+.2f} | "
                     f"N2 (circular shift) mean {row['N2_mean']:+.2f} | **{row['p2']}** |")
        lines.append(f"| O3 agreement ratio R | – | {row['R']:.2f} | 1 = interchangeable agents | descriptive |")
        if g in (19, 26, 31, 40):
            pers = row["pers"]
            p3a = (row["jump"] == "jump") and (pers is not None and pers <= 0.15)
            p3b = bool(row["mf_region"])
            p3 = "supported" if (p3a and p3b) else ("field-driven step" if p3a else "failed")
            lines.append(f"| P3 consensus jump (project labels) | jump, Δ ≥ 0.3, τ ≤ 2, persistence ≤ 0.15; βJ_CW ≥ βJ_s(q_eff) | {row['jump']} "
                         f"(Δ = {row['amp']:+.2f}, τ = {row['tau']:.2f} win, persistence {f2(pers)}); q_eff = {row['qeff']:.1f}, βJ_s = {row['bj_s']:.2f}, "
                         f"first-order region: {'yes' if p3b else 'no'} | constant / linear fits | **{p3}** |")
            res["p3"] = p3
        p4 = "consistent" if (row["act_t"] is not None and row["act_t"] > -row["tcrit"]) else "inconsistent"
        lines.append(f"| P4 control: action-class βJ_CW | ≥ 0 or ≈ 0, any class | {row['act_bj']:+.2f} (t = {row['act_t']:+.2f}); action βJ_PL z_N2 = {row['act_z']:+.2f} | – | {p4} |")
        lines.append(f"| P5 held-out PL (coupled vs fields-only) | gain in ≥ 4/5 folds where abs(z_N2) ≥ 2 | {row['dll_pos']}/{row['folds']} day folds improve | fields only | "
                     f"{'consistent' if row['folds'] and row['dll_pos'] / row['folds'] >= 0.8 else ('not applicable' if abs(row['z_N2']) < 2 else 'inconsistent')} |")
        lines.append(f"| P6 plmDCA diagonal (secondary) | same sign as βJ_PL | z_N1 = {row['plm_z']:+.1f} | N1 (9 draws) | "
                     f"{'agrees' if np.sign(row['plm_z']) == np.sign(row['bj_pl']) else 'disagrees'} |")
        lines.append(f"| P7 prior: abs(βJ) < 2 | – | βJ_CW {row['bj_cw']:+.2f}; drift-corrected excess βJ_PL − N2 mean = {row['excess']:+.2f} | – | "
                     f"{'holds' if abs(row['bj_cw']) < 2 else 'fails (βJ_CW)'} |")
        md = "\n".join(lines)
        md += (f"\n\n**Robustness (O9; βJ_CW):** raw labels {f2(row['rob_raw'])}, q ≤ 4 {f2(row['rob_q4'])}, W = 15 min {f2(row['rob_W15'])}, "
               f"W = 60 min {f2(row['rob_W60'])}, computer-use actions only (post hoc) {f2(row['rob_act'])}, day fields {f2(row['rob_day'])}"
               + (f", rooms pooled {f2(row['rob_pool'])}" if row.get("rob_pool") is not None else "") + ".")
        md += (f"\n\n**Post hoc** (added after the round-1 run, not pre-registered):\n"
               f"- z of βJ_PL vs a ±1-window local shift: {row['z_loc1']:+.2f}. This tests alignment at the 30-min scale.\n"
               f"- Ownership index (share of agent-windows on projects one agent dominates): {row['own']:.2f}.\n"
               f"- Persistence P(same project next window): {row['persist']:.2f}.")
        if g == 26 and R.get("votes"):
            v = R["votes"]
            j = v["jump"]
            sym = v.get("sym", {})
            sn = v.get("snapshot", {})
            p26a = "passes the test as written (p > 0.05, q_eff ≥ 3) but is uninformative" if (sym.get("chi2_p", 0) > 0.05 and sym.get("qeff", 0) >= 3) else "failed"
            p26b_ok = j["verdict"] == "jump" and j["amp"] >= 0.3 and j["tau"] <= 2 and j["hi"] >= 0.75 and (j["persistence_below_mid"] or 0) <= 0.15
            p26c = ("at threshold, inconclusive" if sn["bj_ci"][0] < sn["bj_s"] <= sn["bj_ci"][1] else
                    ("supported" if sn["bj_ci"][0] >= sn["bj_s"] else "failed"))
            md += "\n\n**HH22 vote tests (chat-declared votes; candidate codes only, no text):**\n"
            md += "| Test | Prediction | Observed | Verdict |\n| --- | --- | --- | --- |\n"
            md += (f"| P-G26a symmetric point at runoff onset | top-3 level (p > 0.05), q_eff ≥ 3 | onset rule fired at window {v['onset_window']} (day 1). "
                   f"Top-3 approvals {sym.get('top3_counts')}, χ² p = {sym.get('chi2_p', float('nan')):.2f}, q_eff = {sym.get('qeff', float('nan')):.2f}, "
                   f"{sym.get('n_voters_at_onset')} voters | {p26a}: the onset rule fired on a day-1 mention of a runoff, the test has little power, and the proxy does not "
                   f"reproduce the reported three-way tie |\n")
            md += (f"| P-G26b runoff is a first-order jump | jump, Δ ≥ 0.3, τ ≤ 2, ≈ 1/3 → ≥ 0.75, persistence ≤ 0.15 | jump at window {j['t0']:.1f} of {v['n_windows']}: "
                   f"{j['lo']:.2f} → {j['hi']:.2f} (Δ = {j['amp']:.2f}, τ = {j['tau']:.2f} win, ΔBIC step vs linear {j['dbic_step_vs_lin']:.0f}), persistence {j['persistence_below_mid']:.2f} | "
                   f"**{'supported' if p26b_ok else 'failed'}** (the pre-jump level is 0.18, below ≈ 1/3; any-vote-word variant: Δ = {R['votes_any']['jump']['amp']:.2f}, end level {R['votes_any']['jump']['hi']:.2f}) |\n")
            md += (f"| P-G26c Potts mechanism (runoff snapshot, symmetric fields) | βJ_snap ≥ βJ_s(q) | counts {sn['counts']} (q = {sn['q_runoff']}); βJ_snap = {sn['bj_mle']:.2f} "
                   f"[{sn['bj_ci'][0]:.2f}, {sn['bj_ci'][1]:.2f}] vs βJ_s = {sn['bj_s']:.2f}; P(max ≥ {max(sn['counts'])} under independent symmetric voters) = {sn['p_max_indep']:.3f} | "
                   f"**{p26c}** |\n")
            md += (f"\nWinner (most single-candidate declarations, from structural codes) = agent {v['winner']}, DeepSeek-V3.2, matching the dataset's goal summary. "
                   f"The declared-vote universe is {v['q_vote']} named agents, not 6: vote messages also name non-candidates, e.g. ballot organizers.")
            res.update(p26a=p26a, p26b="supported" if p26b_ok else "failed", p26c=p26c)
        verdict = row["p1"]
        if g == 26:
            verdict = f"P1 {row['p1']}; P2 {row['p2']}; HH22: jump supported, mechanism inconclusive"
        elif cls.startswith("none"):
            verdict = "descriptive"
        else:
            verdict = f"P1 {row['p1']}; P2 {row['p2']}" + (f"; P3 {res['p3']}" if "p3" in res else "")
        sc = ("| Axis | Score | Evidence |\n| --- | --- | --- |\n"
              f"| C adequacy | {2 if (row['folds'] and row['dll_pos'] / row['folds'] >= 0.8 and abs(row['z_N2']) >= 2) else (1 if abs(row['z_N2']) >= 2 else 0)} | "
              f"z_N2 = {row['z_N2']:+.1f}; held-out gain {row['dll_pos']}/{row['folds']} folds |\n"
              f"| D unfitted predictions | {1 if (row['p1'] == 'supported' or g == 26) else 0} | sign by goal mode: {row['p1']} (not diagnostic on its own: βJ_CW > 0 in 11/14 tested weeks, whatever the mode)"
              + ("; vote jump predicted and observed" if g == 26 else "") + " |\n"
              f"| G ground truth | {1 if g in (26, 31, 39, 40) else 0} | "
              + {26: "vote winner and runoff jump match the dataset's goal summary",
                 31: "herding onto shared repos matches the summary (\"about nine agents converged\")",
                 39: "per-agent worlds → strong spread, matching 'each agent builds a world'",
                 40: "hub plus own worlds gives spread by fields, not the predicted consensus"}.get(g, "–") + " |")
        res.update(verdict=verdict, result_md=md, scorecard_md=sc, notes_md=NOTES.get(g, ""))
        (HC.OUT / f"G{g:02d}" / "results.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()


def record_provenance():
    import datetime as dt
    pf = HC.OUT / "_provenance.json"
    prov = json.loads(pf.read_text()) if pf.exists() else {}
    prov["posthoc_and_assembly_outputs"] = {
        "built_by": ["hypotheses/H11-potts-labor-vs-herding/analysis/local_shift.py",
                     "hypotheses/H11-potts-labor-vs-herding/analysis/assemble.py",
                     "hypotheses/H11-potts-labor-vs-herding/analysis/confirm_holdout.py --dry-run"],
        "files": ["local_shift_posthoc.json", "verdicts_round1.parquet", "cross_period_round1.json", "G<NN>/results.json",
                  "G31/posthoc_named_projects.json (ad hoc snippet; recorded in the G31 notes)", "confirm_dryrun.json"],
        "git_commit": HC.C.git_commit(), "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    pf.write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    record_provenance()
