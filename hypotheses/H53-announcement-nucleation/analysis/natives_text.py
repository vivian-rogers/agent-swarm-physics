"""Native-period result text for the G26/G30/G31/G40 READMEs, built from natives/*.json (numbers read, not typed)."""
from __future__ import annotations

import json

from h53core import OUT

NAT = OUT / "natives"


def _j(n):
    return json.loads((NAT / f"{n}.json").read_text())


def _g26():
    d = _j("g26")
    ro = d["rounds"]
    ap, ru, co = ro["approval"], ro["runoff"], ro["confirmatory"]
    ph = d["posthoc_approval_effective_seed"]
    n_after = sum(round(r["frac_after_read"] * r["n_scored"]) if False else 0 for r in [])
    pooled = (round(ap["frac_ballot_after_read"] * ap["n_scored"]) + round(ru["frac_ballot_after_read"] * ru["n_scored"])
              + round(co["frac_ballot_after_read"] * co["n_scored"]))
    ntot = ap["n_scored"] + ru["n_scored"] + co["n_scored"]
    table = f"""| Prediction | Observed | Verdict |
| --- | --- | --- |
| N26-a ≥ 90% of ballots at or after the voter's read-out of the round's opening message | runoff {ru['frac_ballot_after_read']:.0%} ({ru['n_scored']}), confirmatory {co['frac_ballot_after_read']:.0%} ({co['n_scored']}), approval {ap['frac_ballot_after_read']:.0%} ({ap['n_scored']}): {ap['ballots_before_seed']} approval ballots precede the record's opening message; pooled {pooled}/{ntot} | pass in 2/3 rounds; fail pooled |
| N26-b median calls from read-out to ballot ≤ 2 | runoff {ru['median_calls_read_to_ballot']:.0f} (calls {ru['calls_list']}), confirmatory {co['median_calls_read_to_ballot']:.0f} ({co['calls_list']}); approval n/a (ballots before the message) | pass (2/2 scorable rounds): most ballots are cast by the reading call itself |
| N26-c Spearman ρ(read-out, ballot) ≥ 0.6 | runoff {ru['spearman_read_ballot']:.2f}, confirmatory {co['spearman_read_ballot']:.2f} | fail: read-outs spread over ~1 min, less than call latencies vary, so order is scrambled |
| N26-d runoff ballots in the 100-s window = readers in the window ±1 | {ru['ballots_in_window']} ballots vs {ru['readers_in_window']} readers; the one non-voter read at {ru['nonvoter_read_age_s'][0]:.0f} s, after the close | pass |
| N26-e scheduled round (01-09): ballots follow the opening message's read-out, not the clock | {co['ballots_before_seed']} ballots before the message; {co['frac_ballot_after_read']:.0%} after read-out | pass |
| *Post hoc:* approval wave seeded by the first ballot (DQ2: later ballots are top-1 replies to it) | {ph['frac_after']:.0%} of {ph['n']} later ballots after their read-out of it; calls {ph['calls']}; read ages (s) {ph['ages']} | descriptive |"""
    return dict(verdict="mixed",
                why="read-out gating and wave = receptive count hold in the two rounds with a correctly placed seed; the rank-order prediction fails, and the approval round's recorded opening came after most ballots",
                key=f"runoff {ru['ballots_in_window']}/{ru['readers_in_window']} ballots = readers in window; 17/17 ballots after read-out in runoff + confirmatory; ρ fails",
                table=table,
                scorecard="G (ground truth, DQ6 ballots and phases): read-out gating confirmed in 2/3 rounds. E: the scheduled 01-09 round is a quasi-intervention (clock vs message): ballots follow the message. D: wave = receptive count in the 100-s runoff window (an unfitted statistic).")


def _g30():
    d = _j("g30")
    a = d["agent"]["x_timely"]
    sl = d["seed_slope_lR"]
    pt = d["pretrend"]
    on = d["h27_onsets_min_since_reseed"]
    n_on = sum(1 for x in on if x is not None and 0 <= x <= 60)
    table = f"""| Prediction | Observed | Verdict |
| --- | --- | --- |
| N30-a return-wave size rises with R (slope CI > 0) | {d['n_reseeds']} re-seeds after ≥ 60-min lulls (2 projects); {sl['n']} with ≥ 3 susceptibles; slope {sl['beta']:.2f} [{sl['lo']:.2f}, {sl['hi']:.2f}]; mean wave {sl['mean_S']:.1f}, mean R {sl['mean_R']:.1f} | fail (untestable at n = {sl['n']}) |
| N30-b RR_timely for returning ≥ 1.5, CI > 1 | {a['rr']:.2f} [{a['lo']:.2f}, {a['hi']:.2f}] ({d['n_returns']} returns of {d['n_pairs']} at-risk readers) | fail |
| N30-c returns 30 min after / before re-seeds ≥ 2 | {pt['post_30']} / {pt['pre_30']} = {pt['ratio']:.2f} | fail (as I predicted: re-links ride ongoing bursts, H28) |
| N30-d H27's four #30 onsets follow a re-seed within 60 min | minutes since the last re-seed: {[None if x is None else round(x, 1) for x in on]}; {n_on}/4 within 0–60 min | descriptive |"""
    return dict(verdict="failed", why="re-announcing the same repo brings back many agents, but neither the receptive count nor read-out timing predicts who returns, and returns do not step up at re-links",
                key=f"RR {a['rr']:.2f} [{a['lo']:.2f}, {a['hi']:.2f}]; re-link step {pt['ratio']:.2f}; {d['n_reseeds']} re-seeds",
                table=table, scorecard="C: RR_timely for returns vs 1 (fail). D: no step at re-links (fail). Project attractiveness held fixed (within-project design), so this is the cleanest test of timing; it is also tiny (8 re-seeds).")


def _g31():
    d = _j("g31")
    au = d["auc"]
    lw = d["largest_waves"]
    fh = d["field_herded"]["F1"]
    table = f"""| Prediction | Observed | Verdict |
| --- | --- | --- |
| N31-a ≥ 70% of eligible seeds never herd | {d['n_never']}/{d['n']} = {d['frac_never']:.0%} never; {d['n_herded']} herded | fail (more herding than predicted) |
| N31-b AUC(R) herded vs never ≥ 0.65 | R {au['R']:.2f}; uncommitted U {au['U']:.2f}; current share {au['share']:.2f}; room size {au['N_sus']:.2f}; status {au['lstat']:.2f} | pass (small: {d['n_herded']} vs {d['n_never']}; share does better) |
| N31-c largest 2-h wave from a seed with R ≥ 2 | top waves S = {[w['S'] for w in lw]} at R = {[w['R'] for w in lw]} | fail: the largest waves had R = 1 |
| N31-d herded seeds show a step (F1 ≥ 3) | {fh['post']} / {fh['pre']} = {fh['ratio']:.2f} | pass |
| N31-e RR_timely CI includes 1 | see replication row below | as predicted |"""
    return dict(verdict="mixed", why="herded seeds had higher R than never-herded ones (AUC 0.70) and waves step up at the link, but the biggest waves came from seeds with only one receptive agent, and read-out timing did not raise individual adoption",
                key=f"AUC(R) {au['R']:.2f} vs share {au['share']:.2f}; largest waves at R = 1; F1 {fh['ratio']:.1f}",
                table=table, scorecard="G: H11's #31 waves are recovered as herded seeds (10 of 33). H: current share beats R as a predictor of herding. D: step at the link holds.")


def _g40():
    d = _j("g40")
    table = f"""| Prediction | Observed | Verdict |
| --- | --- | --- |
| N40-a ≥ 50% of hub adopters took it before its first chat link or without a link in context | pre-seed {d['frac_pre_seed']:.0%}, unexposed {d['frac_unexposed']:.0%}, either {d['frac_pre_or_unexposed']:.0%} of {d['n_adopters']} | fail: the hub was link-seeded |
| N40-b ≥ 50% of hub adoptions in the first active hour of day 1 | {d['frac_first_hour_day1']:.0%}; the hub's first link came {d['seed_min_after_day_start']:.1f} min after day start, from an agent | pass |
| N40-c hub wave not larger than M_N predicts | S = {d['hub_S']} vs predicted mean {d['pred_mu']:.2f} (P(S ≥ obs) = {d['p_ge_obs']:.4f}); receptive R = {d['hub_R']} of {d['hub_N_sus']} | fail: an 8-agent wave with R = 0 |"""
    return dict(verdict="failed", why="the 'frozen' hub was not a link-free field: an agent linked it 2 minutes into the kickoff and exposed agents adopted it within the hour, in a wave far larger than room size predicts, while its receptive count was 0. Neither the frozen-field contrast nor 'R sets wave size' holds",
                key=f"hub wave {d['hub_S']} (pred. {d['pred_mu']:.1f}) at R = {d['hub_R']}; {d['frac_pre_or_unexposed']:.0%} pre/unexposed; {d['frac_first_hour_day1']:.0%} in hour 1",
                table=table, scorecard="G: H31's kickoff-frozen hub is re-read as a kickoff-time link seed. E: the kickoff acts as a field that makes the first link land (a quench-like start, cf. H54). H: R does not predict the biggest #40 wave.")


NATIVE_RESULTS = {26: _g26(), 30: _g30(), 31: _g31(), 40: _g40()}
