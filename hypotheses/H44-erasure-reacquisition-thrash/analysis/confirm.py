"""H44 confirmatory test on the LOCKED HOLDOUT. Written 2026-10-04 after exploratory round 1; NOT RUN.

Refuses to touch held-out data unless called with BOTH flags
    --confirm --i-understand-this-uses-the-locked-holdout
and refuses if hypotheses/H44-erasure-reacquisition-thrash/ has uncommitted changes (reuse policy, condition 1: the
predictions and this script are committed before the run). It also calls infra/shared/holdout_ledger.py: check() for
every target and refuses a target where a prior run used the same estimator family (policy item 2), printing what must
be disclosed. Without the flags it runs a DRY RUN on non-holdout stand-ins and writes
data/processed/H44-erasure-reacquisition-thrash/confirm_dryrun/confirm_results.json.

Targets (held-out regime-III periods with forced erasures): G43 (one day), G45 (45a-b), NE21+NE23 (#46-#50), #51 tail
(2026-09-07 -> 09-21). Estimates per target; the decision uses a DerSimonian-Laird pool over targets (never a pooled fit).

Frozen criteria (2026-10-04, the round-1 findings stated as confirmable claims; card, "Confirmatory plan"):
  CF1  re-acquisition: Theta_c (forced, post 1-5 vs far -20..-11; non-write calls, agent x previous-call conditioned)
       pooled > 0.01 with the 95% CI above 0, and > 0 in >= 3 of 4 targets.   [round 1: +0.079 [0.071, 0.086], 9/9]
  CF2  forced ~ voluntary: Theta_c(voluntary) pooled CI above 0 and Theta_c(forced) >= 0.5 x Theta_c(voluntary).
                                                                            [round 1: 0.079 vs 0.057]
  CF3  no reset, no re-acquisition rise: Theta_c(pseudo31) pooled upper CI < 0.01.   [round 1: -0.011 [-0.016, -0.006]]
  CF4  trial and error: real-failure share (forced, post 1-5 vs far) pooled CI above 0.   [round 1: +0.010 [0.006, 0.015]]
  CF5  no susceptibility rise: reply rate per visible post-reset item vs the no-reset boundary, pooled RR upper CI
       < 1.10.                                                              [round 1: 0.97 [0.91, 1.04]]
  Reported, not scored: Omega (write dip; H15's statistic, its C3), d_sigma (round 1 +0.018, small), entropy
  (round 1 -0.027), coupling-cut log DiD (round 1 ratio 0.60; overlaps H08's CF4 concept).
Scoring: confirmed if CF1, CF3 and CF4 pass and neither CF2 nor CF5 fails.

Reuse (hypotheses/holdout.md): #45 was used by H02 (activity couplings) and H04 (kick kernels); NE21+NE23 by H04.
H44's statistics (call-category composition conditioned on the previous call; switching; reply rates per visible
message) are different statistics; H15 (C3, write dip), H08 (CF4, addressing of pre-read senders), H39 (C6, idle
share after erasure) and H46 (C3, style across erasures) plan NE41-adjacent tests on the same targets: whoever runs
first makes the others second users, so disclose in all five cards and LOG.md before running.

Stand-ins for the dry run (non-holdout): G43 -> G41; G45 -> G42; NE21+NE23 -> G39, G40, G44; #51 tail -> #51 days
2026-08-24 .. 09-04 (after NE43, like the tail).
Usage:  uv run python hypotheses/H44-erasure-reacquisition-thrash/analysis/confirm.py                    (dry run)
        uv run python hypotheses/H44-erasure-reacquisition-thrash/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import h44lib as L  # noqa: E402
from h44lib import C  # noqa: E402

TARGETS = {
    "G43": {"goals": [43]},
    "G45": {"goals": [45]},
    "NE21+NE23": {"goals": [46, 47, 48, 49, 50]},
    "#51-tail": {"goals": [51], "date_from": "2026-09-07", "date_to": "2026-09-22"},
}
STANDINS = {
    "G43": {"goals": [41]},
    "G45": {"goals": [42]},
    "NE21+NE23": {"goals": [39, 40, 44]},
    "#51-tail": {"goals": [51], "date_from": "2026-08-24", "date_to": "2026-09-05"},
}
LEDGER_TARGET = {"G43": "G43", "G45": "G45", "NE21+NE23": "NE21+NE23", "#51-tail": "#51-tail"}
FAMILIES = ["behavior_states", "work_output", "dilution_addressing"]
SUSC_MAX = 1.10            # CF5: pooled RR upper CI must stay below this


def target_days(spec: dict, holdout: bool) -> pl.DataFrame:
    cal = pl.read_parquet(C.SH / "calendar.parquet").filter(pl.col("goal_no").is_in(spec["goals"])
                                                             & (pl.col("n_agent_events") > 0)
                                                             & (pl.col("pt_date") >= C.REGIME3_START))
    if spec.get("date_from"):
        cal = cal.filter(pl.col("pt_date") >= spec["date_from"])
    if spec.get("date_to"):
        cal = cal.filter(pl.col("pt_date") < spec["date_to"])
    hm = C.holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    cal = cal.with_columns(pl.Series("hm", hm))
    cal = cal.filter(pl.col("hm") | pl.col("holdout")) if holdout else cal.filter(~pl.col("hm") & ~pl.col("holdout"))
    return cal.select("pt_date", "goal_no")


def frames(name: str, spec: dict, holdout: bool):
    days = target_days(spec, holdout)
    if not holdout:
        calls = pl.read_parquet(C.OUT / "calls.parquet").filter(pl.col("pt_date").is_in(days["pt_date"].implode()))
        ev = pl.read_parquet(C.OUT / "events.parquet").filter(pl.col("pt_date").is_in(days["pt_date"].implode()))
        rp = pl.read_parquet(C.OUT / "reply_pools.parquet").filter(pl.col("pt_date").is_in(days["pt_date"].implode()))
        return calls, ev, rp
    import build as B
    out = C.OUT / "confirm" / name.replace("#", "").replace("+", "_")
    out.mkdir(parents=True, exist_ok=True)
    um = C.unit_map(include_holdout=True).filter(pl.col("pt_date").is_in(days["pt_date"].implode()))
    calls = B.build_calls(days, um, out=out, guard=False)
    ev = B.build_events(calls, out=out)
    B.build_replies(calls, out=out, guard=False)
    rp = pl.read_parquet(out / "reply_pools.parquet")
    return calls, ev, rp


def evaluate(calls, ev, rp, B: int = 1000) -> dict:
    res = {"n_calls": calls.height, "events": {k: int(v) for k, v in ev.group_by("ev_kind").len().rows()}}
    for kind, (kmin, kmax) in (("forced", (-20, 20)), ("voluntary", (-20, 20)), ("pseudo31", (-20, 10))):
        p = L.panel(calls, ev.filter(pl.col("ev_kind") == kind), kmin, kmax)
        if p.height == 0:
            continue
        st = L.window_stats(p, B=B, seed=1, windows=("post5", "post10", "far"))
        c5, c10 = st["contrasts"]["post5_vs_far"], st["contrasts"]["post10_vs_far"]
        res[kind] = {"n_events": st["n_events"], "Theta_c": c5["Theta_c"], "Theta": c5["Theta"], "d_fail": c5["d_fail"],
                     "d_sigma_reported": c5["d_sigma"], "d_H_reported": c5["d_H"],
                     "Omega_reported_not_scored": c10["Omega"], "class": L.classify(st)}
    rr = L.reply_rates(rp, "forced", B=B, seed=5)
    res["replies"] = {k: rr.get(k) for k in ("rr_post", "log_did", "rr_has_parent", "n_e", "n_p")}
    return res


def score(per_target: dict) -> dict:
    def pool(kind, stat, log=False):
        e, lo, hi = [], [], []
        for t, r in per_target.items():
            c = (r.get(kind) or {}).get(stat)
            if c and all(c_ is not None and np.isfinite(c_) for c_ in c) and (not log or c[1] > 0):
                v = np.log(c) if log else np.array(c)
                e.append(v[0]); lo.append(v[1]); hi.append(v[2])
        return L.dl_pool(e, lo, hi)
    P = {}
    for kind, stat, lg in (("forced", "Theta_c", False), ("voluntary", "Theta_c", False), ("pseudo31", "Theta_c", False),
                           ("forced", "d_fail", False), ("replies", "rr_post", True), ("replies", "log_did", False),
                           ("forced", "Omega_reported_not_scored", False), ("forced", "d_sigma_reported", False)):
        P[f"{kind}:{stat}"] = pool(kind, stat, lg)
    n_pos = sum(1 for r in per_target.values() if r.get("forced") and r["forced"]["Theta_c"][0] > 0)
    f, v, ps, fl, s = (P["forced:Theta_c"], P["voluntary:Theta_c"], P["pseudo31:Theta_c"], P["forced:d_fail"],
                       P["replies:rr_post"])
    fin = lambda x: x["k"] > 0 and np.isfinite(x["est"])
    cf = {"CF1": "pass" if (fin(f) and f["est"] > L.THETA_FLOOR and f["lo"] > 0 and n_pos >= min(3, len(per_target))) else "fail",
          "CF2": ("pass" if (v["lo"] > 0 and f["est"] >= 0.5 * v["est"]) else "fail") if fin(v) else "n/a",
          "CF3": ("pass" if ps["hi"] < 0.01 else "fail") if fin(ps) else "n/a",
          "CF4": ("pass" if fl["lo"] > 0 else "fail") if fin(fl) else "n/a",
          "CF5": ("pass" if np.exp(s["hi"]) < SUSC_MAX else "fail") if fin(s) else "n/a"}
    return {"pools": P, "criteria": cf, "n_targets_theta_pos": n_pos,
            "confirmed": cf["CF1"] == "pass" and cf["CF3"] == "pass" and cf["CF4"] == "pass" and "fail" not in (cf["CF2"], cf["CF5"])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--B", type=int, default=1000)
    a = ap.parse_args()
    holdout = a.confirm and a.ack
    if a.confirm and not a.ack:
        raise SystemExit("refusing: --confirm needs --i-understand-this-uses-the-locked-holdout")
    if holdout:
        dirty = subprocess.run(["git", "-C", str(C.ROOT), "status", "--porcelain", str(C.HYP)], capture_output=True,
                               text=True).stdout.strip()
        if dirty:
            raise SystemExit("refusing: commit the H44 card, predictions and this script before a confirmatory run\n" + dirty)
        sys.path.insert(0, str(C.ROOT / "infra/shared"))
        import holdout_ledger as HL
        for t in TARGETS:
            chk = HL.check("H44", LEDGER_TARGET[t], "turn-level actions / chat", FAMILIES)
            print(t, "allowed" if chk["allowed"] else "BLOCKED", "| disclose:" if chk["needs_disclosure"] else "",
                  [u["hypothesis"] for u in chk["prior_runs"] + chk["competing_planned"]])
            if not chk["allowed"]:
                raise SystemExit(f"refusing: a prior confirmatory run on {t} used the same estimator family")
    specs = TARGETS if holdout else STANDINS
    per = {}
    for name, spec in specs.items():
        calls, ev, rp = frames(name, spec, holdout)
        per[name] = evaluate(calls, ev, rp, B=a.B)
        print(name, json.dumps({k: per[name].get(k, {}).get("Theta_c") for k in ("forced", "voluntary", "pseudo31")}))
    res = {"mode": "CONFIRMATORY (locked holdout)" if holdout else "dry run on non-holdout stand-ins",
           "targets": per, "score": score(per)}
    out = C.OUT / ("confirm" if holdout else "confirm_dryrun")
    out.mkdir(parents=True, exist_ok=True)
    (out / "confirm_results.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res["score"], indent=1, default=float))
    if holdout:
        print("Record the run: infra/shared/holdout_ledger.py record_run(...), disclose in the card and LOG.md.")


if __name__ == "__main__":
    main()
