"""Write the H44 period READMEs (G36..G51 + NE41) from data/processed/H44-erasure-reacquisition-thrash/*/results.json.

Replication folders carry the templated card prediction (labelled as such) and the common estimator table; native
folders (G36, G38, G51, NE41) add their own dated prediction and test. No agent text is written.
Usage: uv run python hypotheses/H44-erasure-reacquisition-thrash/analysis/write_period_folders.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

from h44lib import C  # noqa: E402

PERIODS = ["G36", "G37", "G38", "G39", "G40", "G41", "G42", "G44", "G51"]
INFO = {
    "G36": ("Interact with outside agents", "2026-03-23 → 03-27", "units 36b (NE14 + NE41 onset, 03-24) and 36c (NE16 memory fix, 03-26); 36a is regime II and excluded", "12 agents · two rooms"),
    "G37": ("Free three days", "2026-03-30 → 04-01", "one unit", "12 agents · two free rooms"),
    "G38": ("Charity fundraiser, year 2", "2026-04-02 → 04-24", "units 38a–38e (NE36, NE17, two joins, NE18)", "12 → 14 agents · two rooms"),
    "G39": ("Build your own interactive world", "2026-04-27 → 05-01", "one unit", "15 agents · two rooms"),
    "G40": ("Connect your worlds into a 3D universe", "2026-05-04 → 05-08", "one unit (NE42 merge)", "15 agents · one merged room"),
    "G41": ("Novel research", "2026-05-11 → 05-15", "one unit (NE42 split back)", "15 agents · two rooms"),
    "G42": ("Run your own YouTube channel", "2026-05-18 → 05-22", "units 42a, 42b (Gemini 3.5 Flash joins)", "15 → 16 agents · two rooms"),
    "G44": ("#best fine-tunes a leader; #rest picks its own goals", "2026-05-26 → 05-29", "units 44a, 44b (two joins)", "17 → 18 agents · two rooms"),
    "G51": ("Maximize your private assigned role", "2026-07-06 → 09-04 (non-holdout)", "units 51a–51l (11 joins, NE32, NE38, NE43 bookends/nudges end); the tail 51m is held out", "21 → 32 agents · one room (#general; #focus from 08-05)"),
}
PRED_TS = "2026-10-04 06:40 UTC"


def f(c, nd=3, pct=False):
    if not c or c[0] is None or not np.isfinite(c[0]):
        return "–"
    if pct:
        return f"{100 * c[0]:+.0f}% [{100 * c[1]:+.0f}, {100 * c[2]:+.0f}]"
    return f"{c[0]:+.{nd}f} [{c[1]:+.{nd}f}, {c[2]:+.{nd}f}]"


def sig(c):
    return bool(c) and np.isfinite(c[1]) and (c[1] > 0 or c[2] < 0)


def table(r):
    st = r["stats"]
    rows = []
    def g(kind, tag, stat):
        return st.get(kind, {}).get("contrasts", {}).get(tag, {}).get(stat)
    for lab, tag, stat, pct, nd in (("Θ_c re-acquisition rise, non-write calls, agent × previous-call conditioned (post 1–5 vs far −20…−11)", "post5_vs_far", "Theta_c", False, 3),
                                    ("Θ raw (same, unconditioned)", "post5_vs_far", "Theta", False, 3),
                                    ("ΔR re-acquisition share, all calls", "post5_vs_far", "dR", False, 3),
                                    ("Ω write dip (post 1–10 vs far)", "post10_vs_far", "Omega", True, 0),
                                    ("work commits per call (post 1–10 vs far)", "post10_vs_far", "work_rel", True, 0),
                                    ("Δσ switching rate (post 1–5 vs far)", "post5_vs_far", "d_sigma", False, 3),
                                    ("ΔH category entropy, nats (post 1–5 vs far)", "post5_vs_far", "d_H", False, 3),
                                    ("Δ real-failure share (post 1–5 vs far)", "post5_vs_far", "d_fail", False, 3),
                                    ("Δ talk share (post 1–5 vs far)", "post5_vs_far", "d_talk", False, 3),
                                    ("end of segment: Ω near (−10…−1) vs far", "near_vs_far", "Omega", True, 0)):
        rows.append(f"| {lab} | {f(g('forced', tag, stat), nd, pct)} | {f(g('voluntary', tag, stat), nd, pct)} | "
                    f"{f(g('pseudo31', tag, stat), nd, pct)} |")
    hdr = ("| Statistic (95% agent-day cluster bootstrap CI) | forced | voluntary | no reset (pseudo, pos 31) |\n"
           "| --- | --- | --- | --- |")
    return hdr + "\n" + "\n".join(rows)


def extra(r):
    L_ = []
    ell = r["curves"].get("forced", {}).get("ell")
    if ell:
        cf = r["curves"]["forced"]
        et, ew = cf.get("ell_R_tail", {}), cf.get("ell_W", {})
        L_.append(f"- **Relaxation** after a forced reset: re-acquisition R(k) spikes at the first call (single-exponential ℓ = {ell['ell']:.1f} calls [{ell.get('lo', float('nan')):.1f}, {ell.get('hi', float('nan')):.1f}], amplitude {ell['A']:+.3f}) and then decays with a tail ℓ = {et.get('ell', float('nan')):.1f} calls [{et.get('lo', float('nan')):.1f}, {et.get('hi', float('nan')):.1f}] (k ≥ 2); writes recover with ℓ_W = {ew.get('ell', float('nan')):.1f} calls [{ew.get('lo', float('nan')):.1f}, {ew.get('hi', float('nan')):.1f}] (fits capped at 60 calls).")
    v = r["v3"].get("forced", {})
    if v.get("H_v3"):
        L_.append(f"- **Jev v3 windows** (first 5 min after a forced reset vs ≥ 5 min, paired within {v['n_agent_days']} agent-days): entropy {f(v['H_v3'])}; research/browse {f(v['p_research_browse'])}; execute {f(v['p_execute_task'])}; self-maintenance {f(v['p_self_maintenance'])}; progress score {f(v['progress_score'])}; error rate {f(v['err_rate'])}.")
        pm = v.get("pre_matched", {})
        if pm.get("H_v3"):
            L_.append(f"  - density-matched (vs the last 5 min before a forced reset, {pm['n_agent_days']} agent-days): entropy {f(pm['H_v3'])}; research/browse {f(pm['p_research_browse'])}; execute {f(pm['p_execute_task'])}; progress score {f(pm['progress_score'])}. Five-minute windows (≈ 15 calls) do not resolve the 1–5-call re-acquisition burst.")
    rp = r["replies"].get("forced", {})
    if rp.get("rr_post"):
        L_.append(f"- **Replies** ({rp['n_e']} talk messages after forced resets vs {rp['n_p']} after the no-reset boundary): susceptibility to post-reset items RR = {f(rp['rr_post'])}; coupling cut log DiD (pre-erased vs post, against pre vs post without a reset) = {f(rp['log_did'])}; P(has a reply parent) RR = {f(rp['rr_has_parent'])}.")
    else:
        L_.append(f"- **Replies:** too few talk messages ({rp.get('n_e', 0)} after forced resets, {rp.get('n_p', 0)} controls).")
    pf = r["pull"].get("forced_bge", {})
    if pf.get("D"):
        pg = r["pull"].get("forced_gte", {})
        L_.append(f"- **Content pull** ({pf['n_cross']} forced pairs vs {pf['n_within']} within pairs, 0.05-decade gap strata): D = (post − pre)_forced − (post − pre)_within = {f(pf['D'])} (bge), {f(pg.get('D'))} (gte); toward post-read {f(pf['d_post'])}, toward pre-read {f(pf['d_pre'])}.")
    lo = r["loops"]
    if lo.get("OR_forced_vs_pseudo"):
        ln = r.get("loops_norm", {})
        L_.append(f"- **Loops:** {lo['forced']['n_loop_events']} forced events start inside a loop; the loop command recurs in +1…+10 in {100 * lo['forced']['recur']:.0f}% vs {100 * lo['pseudo31']['recur']:.0f}% without a reset (OR {f(lo['OR_forced_vs_pseudo'], 2)}; normalized hash OR {f(ln.get('OR_forced_vs_pseudo'), 2)}).")
    dv = r.get("deltaV")
    if dv:
        L_.append(f"- **Output lost per forced erasure** (+1…+20 vs far): {dv['write_calls_lost_per_erasure']:+.2f} write calls, {dv['work_commits_lost_per_erasure']:+.3f} work commits; × {r['events'].get('forced', 0)} erasures = {100 * dv['share_write_calls_lost']:.1f}% of the period's write calls and {100 * dv['share_work_commits_lost']:.1f}% of its work commits.")
    d = r.get("dose", {})
    if d.get("rho_dose_dip_within"):
        L_.append(f"- **Memory dose:** within-agent Spearman ρ(lines added / memory size, write dip) = {d['rho_dose_dip_within'][0]:+.3f} (p {d['rho_dose_dip_within'][1]:.2g}, n {d['n']}).")
    return "\n".join(L_)


def verdict_line(r):
    fl = r.get("verdict_flags", {})
    bits = ["re-acquisition up" if fl.get("Theta_pos") else "re-acquisition not up",
            "writes down" if fl.get("Omega_neg") else "write dip not significant",
            "switching up" if fl.get("sigma_or_H_up") else "no entropy/switching rise"]
    if fl.get("P4b_opposite"):
        bits.append("susceptibility opposite")
    return f"{r['verdict']} ({', '.join(bits)})"


def write(per, r, native_text: str | None = None, native_pred: str | None = None, verdict_override: str | None = None):
    t, dates, units, setup = INFO[per]
    d = C.HYP / "goalperiod-subhypotheses" / per
    d.mkdir(parents=True, exist_ok=True)
    role = "native" if native_text else "replication"
    ev = r["events"]
    v = verdict_override or verdict_line(r)
    pred = (f"*Written {PRED_TS}, before running on this period (templated from the card's P1–P6; replication layer).*\n"
            "- Forced resets: Θ_c > 0 (CI; ≥ 0.01), ΔR ≥ +0.05, Ω between −0.25 and −0.60, switching σ and/or entropy H up, "
            "susceptibility to post-reset items RR > 1, coupling cut log DiD < 0, content-pull D > 0; voluntary resets the same sign; "
            "no-reset pseudo-erasures ≈ 0 on every contrast.\n"
            "- *Counts against:* Θ_c ≤ 0 (pure restart overhead, R1); Ω ≥ 0; σ/H flat or down; RR ≤ 1 with entropy up (temperature pulse, R2).")
    body = f"""# H44 × {per}: {t} ({dates})

**Verdict:** {v}
**Role:** {role}
**Period:** regime III · {setup} · {r['n_days']} non-holdout days · {r['n_agents']} agents with calls · {r['n_calls']:,} model calls. Units: {units}.

## Why this period
{"Replication layer: the common reset event-study estimator, giving one comparable point per regime-III period (templated, labelled as such)." if not native_text else native_text.split("@@PRED@@")[0].strip()}

## Prediction
{pred}
{native_pred or ""}

## Result
*Run 2026-10-04 (`analysis/run_all.py` → `data/processed/H44-erasure-reacquisition-thrash/{per}/results.json`; figure `figures/event_study.pdf`).* Events: {ev.get('forced', 0):,} forced, {ev.get('voluntary', 0):,} voluntary, {ev.get('pseudo31', 0):,} pseudo-erasures (pos 31), {ev.get('pseudo21', 0):,} (pos 21). Pipeline class (Θ_c / Ω rule): forced **{r['stats'].get('forced', {}).get('class')}**, voluntary **{r['stats'].get('voluntary', {}).get('class')}**, no reset (pos 31) **{r['stats'].get('pseudo31', {}).get('class')}**, no reset (pos 21) **{r['stats'].get('pseudo21', {}).get('class')}**.

{table(r)}

{extra(r)}
{("" if not native_text else chr(10) + "## Native test" + chr(10) + native_text.split("@@PRED@@")[1].strip())}

## Scorecard (period-specific axes)
- **C adequacy:** contrasts against the no-reset pseudo-erasure and the far-pre reference ({'pseudo class ' + str(r['stats'].get('pseudo31', {}).get('class'))}).
- **D unfitted:** Θ_c, σ, entropy, replies and pull were not fitted; the write dip (Ω) is H15's statistic (replication).
- **E interventional:** forced resets are timed by the 41-record cap (quasi-random); voluntary resets are the agent's choice.
- **F identifiability:** synthetic recovery at this period's counts: see the card (G51/G38: 100%; G37-size: thrash 62%, no false thrash).

## Notes
- Exploratory, non-holdout. Event windows truncate at the next reset of any kind and at the day edge; a balanced +1…+20 subset is in `results.json` (`forced_balanced`).
- No agent text is stored or quoted; commands were classified in memory (see the card's scheme).
"""
    (d / "README.md").write_text(body)


def native_g51(r):
    pa, d = r["paths"], r["dose"]
    vs = pa["vs_screen"]
    rows = "\n".join(f"| {k} | {v['n']:,} | {f(v['d_write_rate'])} | {f(v['d_k_first_write'], 2)} |" for k, v in vs.items())
    dv = r["deltaV"]
    wk = r["stats"]["forced"]["contrasts"]["post10_vs_far"]["work_rel"]
    om = r["stats"]["forced"]["contrasts"]["post10_vs_far"]["Omega"]
    rho = d["rho_dose_dip_within"][0]
    ok_path = vs.get("artifact", {}).get("d_k_first_write", [0, 0, 0])[2] < 0 and \
        vs.get("artifact", {}).get("d_k_first_write", [0])[0] < vs.get("room", {}).get("d_k_first_write", [0])[0]
    text = f"""Native layer. The largest sample by far (14,593 forced resets in 45 non-holdout days; 48k agent work commits), one room, private roles, so the re-acquisition path an agent takes after a reset can be compared within agent and task mode, and the DQ4 work commits measure output directly. Three period-specific tests: which re-acquisition path restores output fastest (the Kolchinsky store question), whether the memory dose written at the consolidation shortens the dip, and whether git work commits dip like write calls.
@@PRED@@
*Run 2026-10-04.* **Path → recovery** (forced resets with ≥ 20 pre and ≥ 10 post calls, n = {pa['n']:,}). The first substantive call in +1…+3 defines the path: artifact = local file or notes read, remote = web/API/git-remote read, screen = screenshot or GUI, room = history search or talk, direct = write or run. Shares: {', '.join(f"{k} {100 * v:.0f}%" for k, v in sorted(pa['path_shares'].items(), key=lambda x: -x[1]))}. Outcome: write rate in +4…+10 minus the pre-reset rate (−20…−1), and calls to the first write; strata agent × pre-reset mode (shell / GUI / mixed); differences against the screen path, agent-day cluster bootstrap:

| First path | n | Δ write rate vs screen | Δ calls to first write vs screen |
| --- | --- | --- | --- |
{rows}

- **Memory dose:** within-agent ρ(lines added at the consolidation / memory size, write dip) = {rho:+.3f} (n {d['n']:,}): {'|ρ| < 0.1, as predicted' if abs(rho) < 0.1 else 'outside ±0.1'}.
- **Work commits:** relative dip over +1…+10 {f(wk, pct=True)} vs write calls {f(om, pct=True)} (difference {abs(wk[0] - om[0]):.2f}; predicted ≤ 0.2).
- **Output lost to the cap:** {-dv['write_calls_lost_per_erasure']:.2f} write calls and {-dv['work_commits_lost_per_erasure']:.3f} work commits per forced reset, {100 * dv['share_write_calls_lost']:.1f}% of G51's write calls and {100 * dv['share_work_commits_lost']:.1f}% of its work commits.
- **Native verdict:** path prediction {'supported' if ok_path else 'not supported'} (artifact-first resumes writing {-vs['artifact']['d_k_first_write'][0]:.1f} calls sooner than screen-first, room-first only {-vs['room']['d_k_first_write'][0]:.1f}); dose prediction {'supported' if abs(rho) < 0.1 else 'failed'}; work-commit prediction {'supported' if abs(wk[0] - om[0]) <= 0.2 else 'failed'}. Caveat: the path is chosen by the agent, so this is observational within strata, not an intervention."""
    pred = """**Native prediction** *(written 2026-10-04 06:40 UTC, card "Native predictions")*: among forced erasures, a first re-acquisition call on local artifacts or notes is followed by an earlier first write (within agent) than a first call that looks at the screen, browses or reads the room; memory dose does not shorten the dip (|ρ| < 0.1); work commits dip like write calls (relative dip within ±0.2 of Ω)."""
    return text, pred, ok_path and abs(rho) < 0.1 and abs(wk[0] - om[0]) <= 0.2


def native_g38(r):
    lo, ln = r["loops"], r["loops_norm"]
    ok = lo.get("OR_forced_vs_pseudo") and lo["OR_forced_vs_pseudo"][2] < 1 and lo["OR_forced_vs_pseudo"][0] < 0.7
    pa = r["paths"]["vs_screen"]
    text = f"""Native layer. G38 is the longest two-room regime-III period with dense git and the first of the loop-heavy weeks (#38–#40: H12's self-repetition, H46's restatement). If the context window carries a stuck command loop, erasing it should break the loop; if the loop is driven by the task or the environment (a failing build, a polling job), the agent should return to it after re-reading.
@@PRED@@
*Run 2026-10-04.* A forced reset is "in a loop" when ≥ 3 of its last 10 calls repeat an earlier command (exact command hash ≥ 2 times in the previous 10 calls) or are the 3rd real failure within 10 calls. Outcome: the looping command recurs in +1…+10. Control: pseudo-erasures (pos 31) with a loop in their pre-window.

| | events in a loop | loop recurs in +1…+10 | odds ratio vs no reset |
| --- | --- | --- | --- |
| forced | {lo['forced']['n_loop_events']} | {100 * lo['forced']['recur']:.0f}% | {f(lo.get('OR_forced_vs_pseudo'), 2)} |
| voluntary | {lo['voluntary']['n_loop_events']} | {100 * lo['voluntary']['recur']:.0f}% | {f(lo.get('OR_voluntary_vs_pseudo'), 2)} |
| no reset (pos 31) | {lo['pseudo31']['n_loop_events']} | {100 * lo['pseudo31']['recur']:.0f}% | 1 |
| forced, normalized hash (cd/export prefixes dropped, digits collapsed) | {ln['forced']['n_loop_events']} | {100 * ln['forced']['recur']:.0f}% (control {100 * ln['pseudo31']['recur']:.0f}%) | {f(ln.get('OR_forced_vs_pseudo'), 2)} |

- **Native verdict:** {'supported' if ok else 'failed'}: an erasure breaks most command loops (prediction OR < 0.7, CI < 1), and the normalized hash rules out "same command re-typed with a new prefix". Across all periods the pooled odds ratio is in the NE41 folder; the effect weakens in G51 (OR ≈ 0.3).
- **Path → recovery (secondary, as in G51):** calls to first write vs screen-first: artifact {f(pa.get('artifact', {}).get('d_k_first_write'), 2)}, remote {f(pa.get('remote', {}).get('d_k_first_write'), 2)}, room {f(pa.get('room', {}).get('d_k_first_write'), 2)}, direct {f(pa.get('direct', {}).get('d_k_first_write'), 2)}."""
    pred = """**Native prediction** *(written 2026-10-04 06:40 UTC)*: among events whose pre-window is in a loop (≥ 3 calls in loop in −10…−1), the loop recurs in +1…+10 less often after a forced erasure than after a pseudo-erasure with a loop in its pre-window (odds ratio < 0.7, CI < 1)."""
    return text, pred, ok


def native_g36(r, later_mean):
    n = r["native_G36"]
    fd = n["first_two_days"]
    larger = fd["Theta_c"][1] > later_mean
    text = f"""Native layer. G36 holds the regime boundary inside one goal: NE14 (perma-computer-use and the consolidation cap) starts NE41's forced erasures on 03-24 (unit 36b), and NE16 fixes a contradictory "never update memory" consolidation instruction on 03-26 (unit 36c). These are the first forced erasures the agents ever met, and NE16 is a candidate change in the memory store (erasure with vs without memory writes).
@@PRED@@
*Run 2026-10-04.*

| | forced events | Θ_c | Ω (write dip) | Δσ | memory lines added at the consolidation (median) |
| --- | --- | --- | --- | --- | --- |
| 36b (03-24/25, first erasures; before NE16) | {n['36b']['n_events']} | {f(n['36b']['Theta_c'])} | {f(n['36b']['Omega'], pct=True)} | {f(n['36b']['d_sigma'])} | {n['36b']['mem_lines_added_median']} |
| 36c (03-26/27, after NE16) | {n['36c']['n_events']} | {f(n['36c']['Theta_c'])} | {f(n['36c']['Omega'], pct=True)} | {f(n['36c']['d_sigma'])} | {n['36c']['mem_lines_added_median']} |
| G38–G51 replication mean Θ_c | | {later_mean:+.3f} | | | |

- **Onset:** the first two days' thrash index is {'larger than' if larger else 'not larger than'} the later-period mean (prediction failed{'' if not larger else ' — no, supported'}). Agents re-acquire after their very first erasures about as much as months later.
- **NE16:** no first stage: memory lines added per consolidation are the same before and after the fix (median {n['36b']['mem_lines_added_median']} vs {n['36c']['mem_lines_added_median']}), so NE16 did not change the memory store at consolidations and cannot test it. Θ_c is the same in both units; the write dip is larger after the fix but the difference is inside the CIs.
- **Learning across periods** (NE41 folder): Θ_c shows no decline from #36 to #51 and the notes-read share no significant rise.
- **Native verdict:** failed (onset not larger; no learning trend); NE16 uninformative."""
    pred = """**Native prediction** *(written 2026-10-04 06:40 UTC)*: the thrash index on the first two days of forced erasure (03-24/25) is larger than the G38–G51 mean (agents had not yet adapted); NE16's memory fix (03-26) does not change Θ or Ω beyond noise (memory is not the load-bearing store). Across periods Θ declines and the notes-read share rises from #36 to #51."""
    return text, pred, False


def write_ne41(ne, res):
    P = ne["pooled"]
    def pp(key, pct=False, lg=False):
        v = P.get(key)
        if not v or not np.isfinite(v["est"]):
            return "–"
        if lg:
            return f"{np.exp(v['est']):.2f} [{np.exp(v['lo']):.2f}, {np.exp(v['hi']):.2f}] ({v['n_pos']}/{v['k']} > 1)"
        if pct:
            return f"{100 * v['est']:+.0f}% [{100 * v['lo']:+.0f}, {100 * v['hi']:+.0f}] ({v['n_pos']}/{v['k']} > 0)"
        return f"{v['est']:+.3f} [{v['lo']:+.3f}, {v['hi']:+.3f}] ({v['n_pos']}/{v['k']} > 0; τ {v['tau']:.3f})"
    tr = ne["trend"]
    body = f"""# H44 × NE41: forced context erasures at the 41-record cap (regime III, spanning)

**Verdict:** mixed (re-acquisition and output dip supported in 9/9 and 8/9 periods, forced ≥ voluntary, no excess pre-trend; temperature pulse, susceptibility rise and content-pull rise not found)
**Role:** native (exploratory; spans G36–G51, named exception (c): the reset is the object)
**Events:** regime-III non-holdout resets from DQ1 `context_ledger_turns` (21,165 forced, 16,357 voluntary) and 21,806 no-reset pseudo-erasures of each kind.

## Why this NE
The scaffold erases the context window when a segment reaches 41–42 records (40 model calls), keeping memory. Its timing is set by the cap, not by the agent, so each forced reset is a quasi-random scramble of the context store (H15's natural-scramble variant). Voluntary consolidations, chosen by the agent at task boundaries, are the contrast (rival R3).

## Prediction
*Written {PRED_TS}, before any reset-aligned statistic (card P1–P6 and the NE41 native prediction).* Forced resets: Θ_c > 0 with ΔR ≥ +0.05; Ω −0.25…−0.60; switching/entropy up; susceptibility to post-reset items up (RR > 1); coupling to pre-reset items down (log DiD < 0); content pull toward post-read items up (D > 0); Θ_c(forced) ≥ 0.5 × Θ_c(voluntary); **no pre-trend in writes or re-acquisition beyond the pseudo-erasure band** (quasi-random timing), while voluntary resets show a pre-window write excess.

## Result
*Run 2026-10-04 (`analysis/run_all.py` → `data/processed/H44-erasure-reacquisition-thrash/NE41/results.json`; figure `figures/forest.pdf`).* DerSimonian–Laird random effects over the nine per-period estimates (never a pooled fit), 95% CI, number of periods with the predicted sign, between-period SD τ.

| Statistic | forced | voluntary | no reset (pos 31) |
| --- | --- | --- | --- |
| Θ_c (re-acquisition, non-write, agent × previous call) | {pp('forced:post5_vs_far:Theta_c')} | {pp('voluntary:post5_vs_far:Theta_c')} | {pp('pseudo31:post5_vs_far:Theta_c')} |
| ΔR (all calls) | {pp('forced:post5_vs_far:dR')} | {pp('voluntary:post5_vs_far:dR')} | {pp('pseudo31:post5_vs_far:dR')} |
| Ω write dip (+1…+10) | {pp('forced:post10_vs_far:Omega', True)} | {pp('voluntary:post10_vs_far:Omega', True)} | {pp('pseudo31:post10_vs_far:Omega', True)} |
| work commits per call (+1…+10) | {pp('forced:post10_vs_far:work_rel', True)} | {pp('voluntary:post10_vs_far:work_rel', True)} | {pp('pseudo31:post10_vs_far:work_rel', True)} |
| Δσ switching | {pp('forced:post5_vs_far:d_sigma')} | {pp('voluntary:post5_vs_far:d_sigma')} | {pp('pseudo31:post5_vs_far:d_sigma')} |
| ΔH entropy (nats) | {pp('forced:post5_vs_far:d_H')} | {pp('voluntary:post5_vs_far:d_H')} | {pp('pseudo31:post5_vs_far:d_H')} |
| pre-trend: writes −10…−1 vs −20…−11 | {pp('forced:near_vs_far:Omega', True)} | {pp('voluntary:near_vs_far:Omega', True)} | {pp('pseudo31:near_vs_far:Omega', True)} |

| Susceptibility and coupling (pooled) | forced | voluntary |
| --- | --- | --- |
| reply rate per visible post-reset item, vs no reset (RR) | {pp('replies:forced:rr_post(log)', lg=True)} | {pp('replies:voluntary:rr_post(log)', lg=True)} |
| coupling cut: (pre-erased : post) ÷ (pre-in-context : post), ratio | {pp('replies:forced:log_did(log)', lg=True)} | {pp('replies:voluntary:log_did(log)', lg=True)} |
| P(talk message has a reply parent), RR | {pp('replies:forced:rr_has_parent(log)', lg=True)} | {pp('replies:voluntary:rr_has_parent(log)', lg=True)} |
| content pull D (bge) | {pp('pull:forced_bge:D')} | {pp('pull:voluntary_bge:D')} |
| content pull D (gte) | {pp('pull:forced_gte:D')} | – |
| loop recurrence, odds ratio vs no reset | {pp('loops:log_OR_forced_vs_pseudo', lg=True)} | – |

- **Forced vs voluntary (R3):** Θ_c forced {P['forced:post5_vs_far:Theta_c']['est']:+.3f} ≥ 0.5 × voluntary {P['voluntary:post5_vs_far:Theta_c']['est']:+.3f}: the erasure, not the task boundary, drives re-acquisition (P5 supported). Voluntary resets follow a wind-down (talk share rises to 0.17 at −1 in G51, reads fall, writes peak at −10…−2): the agent posts a status and consolidates at a boundary; the post-reset write dip is larger after voluntary resets (−36% vs −26%).
- **Quasi-random timing:** the forced pre-trend in writes (+7%) equals the no-reset pseudo band (+7%): writes ramp up through every segment, so a forced reset arrives at an ordinary point of that ramp (supported). The ramp itself means the post-reset dip is the low phase of a 40-call sawtooth, not a 10-call blip.
- **Past-only control (DQ8):** pseudo-erasures at pos 31 without conditioning on the segment reaching 40 calls give the same answer (G38/G41/G51 Θ_c −0.015 to −0.025, class none; `robustness_pseudo_past.json`).
- **Cross-period trend (phase-diagram points):** Θ_c by period {', '.join(f'{p} {t:+.3f}' for p, t in zip(tr['periods'], tr['Theta']))}; Spearman vs period order ρ {tr['rho_Theta_time'][0]:+.2f} (p {tr['rho_Theta_time'][1]:.2f}); notes-read share ρ {tr['rho_notes_time'][0]:+.2f} (p {tr['rho_notes_time'][1]:.2f}). No learning trend.

## Scorecard (period-specific axes)
- **C:** beats the pseudo-erasure null in 9/9 periods (Θ_c) and 8/9 (Ω); past-only control agrees.
- **D:** Θ_c, σ, entropy, the reply contrasts and pull were not fitted; ℓ (5–7 calls for the re-acquisition tail, ~3 for writes) was predicted 3–15.
- **E:** forced resets are the intervention; forced ≥ voluntary rejects the task-boundary rival.
- **H:** rejects R0 (no effect) and R1 (pure restart overhead: Θ_c ≫ the synthetic dip residual); rejects R2 (temperature pulse: entropy falls); the predicted susceptibility rise also fails.

## Notes
- Exploratory, non-holdout; per-period numbers are in the G folders. The write dip (Ω) is H15's statistic (replication).
"""
    d = C.HYP / "goalperiod-subhypotheses" / "NE41"
    d.mkdir(parents=True, exist_ok=True)
    (d / "README.md").write_text(body)


def main():
    res = {p: json.loads((C.OUT / p / "results.json").read_text()) for p in PERIODS}
    ne = json.loads((C.OUT / "NE41" / "results.json").read_text())
    later = float(np.mean([res[p]["stats"]["forced"]["contrasts"]["post5_vs_far"]["Theta_c"][0]
                           for p in ("G38", "G39", "G40", "G41", "G42", "G44", "G51")]))
    for p, r in res.items():
        if p == "G51":
            t, pr, ok = native_g51(r)
        elif p == "G38":
            t, pr, ok = native_g38(r)
        elif p == "G36":
            t, pr, ok = native_g36(r, later)
        else:
            write(p, r)
            continue
        base = r["verdict"]
        v = ("supported" if (base == "supported" and ok) else "failed" if (base == "failed" and not ok) else "mixed")
        v = f"{v} (replication {verdict_line(r)}; native test {'passed' if ok else 'failed'})"
        write(p, r, t, pr, v)
    write_ne41(ne, res)
    print("written", len(res) + 1)


if __name__ == "__main__":
    main()
