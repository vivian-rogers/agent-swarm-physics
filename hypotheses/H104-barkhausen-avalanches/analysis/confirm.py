"""H104 confirmatory run on the LOCKED HOLDOUT. Written and frozen 2026-10-04 after round 1; NOT RUN.

Guard: held-out data are read only with BOTH `--confirm` and H104_CONFIRM=1, and only if `holdout_ledger.check` allows
every target. `--dry-run` runs the identical pipeline on non-holdout stand-ins (#51 days 2026-08-05 -> 08-21 for the
tail; #38 and #41 for the kickoff test) and writes to a scratch directory.

Targets: the #51 tail (2026-09-07 -> 09-21; step response, dispersion, burst ratio) and #43, #45 (kickoff ratio K, and
the step tests where eligible).

Frozen predictions (round-1 estimators, Amendment A1; isolated human steps, W = 60 min, at-risk spans, 999 rotations):
  C1  Original claim, expected to FAIL: the tail's step response X > 1 with p < 0.05 in both channels.
  C2  No Barkhausen-size response: in each channel the tail's X 95% CI includes 1 and X < X_W1_Q05, the 5th percentile
      of X in round 1's Barkhausen synthetic world at #51 counts (work 1.47, attention 1.13).
  C3  Between steps switching is near-Poisson given agent rates: quiet-window D <= 1.25 in both channels.
  C4  HH kill: the burst ratio BR's 95% CI includes 1 in both channels.
  C5  Kickoffs move agents: K > 1 in every held-out period with a kickoff (#43, #45), both channels where computable.
Reading: C2-C4 confirm "mid-period human steps release no Barkhausen avalanches; between-step switching is near-Poisson".
C1 passing would revive the step response (not the tail, which is not identifiable at these counts).
Step set (frozen): isolated eligible steps; if fewer than 8 exist, all eligible steps (round 1's "allsteps" variant).
Fewer than 3 eligible steps makes C1-C4 "not testable". Round 1 had 24 isolated steps in 44 #51 days (37 with all
steps), unevenly spread: the 51g days alone have 2 isolated steps. The tail's step count has not been looked at; at
~5-10 steps the synthetic power for the step response is ~0.25-0.75, so the tail may confirm only C5 strongly.

Reuse policy (hypotheses/holdout.md): planned project-label users of the #51 tail and #45 include H01, H11, H27, H28;
H104's statistics (step-aligned burst sizes, quiet-window dispersion, kickoff ratio) are different statistics. Disclose
in the card and LOG.md before running.

Usage:
  uv run python hypotheses/H104-barkhausen-avalanches/analysis/confirm.py --dry-run
  H104_CONFIRM=1 uv run python hypotheses/H104-barkhausen-avalanches/analysis/confirm.py --confirm
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import build as B  # noqa: E402
import h104lib as L  # noqa: E402

ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
OUT = ROOT / "data/processed/H104-barkhausen-avalanches/confirm"
SCRATCH = Path(os.environ.get("TMPDIR", "/tmp")) / "h104_confirm_dryrun"
W = 3600.0
FROZEN = {"X_W1_Q05": {"work": 1.47, "attn": 1.13}, "D_max": 1.25, "alpha": 0.05}
TARGETS = {"tail": (51, ("2026-09-07", "2026-09-21")), "kick": (43, 45)}
STANDINS = {"tail": (51, ("2026-07-06", "2026-08-05")), "kick": (38, 41)}


def days_of(g, lo, hi, allow_holdout):
    cal = pl.read_parquet(ROOT / "data/processed/shared/calendar.parquet").filter(
        (pl.col("goal_no") == g) & (pl.col("n_agent_events") > 0) & (pl.col("pt_date") >= lo) & (pl.col("pt_date") < hi))
    if not allow_holdout:
        cal = cal.filter(~pl.col("holdout"))
    return sorted(cal["pt_date"].to_list())


def step_tests(P: dict) -> dict:
    out = {}
    for ch in ("work", "attn"):
        ad = L.agent_days(P, "span")
        sw = L.switches_in(P, ch, ad)
        st = L.eligible_steps(P, ad, W)
        step_set = "isolated"
        if st.height < 8:
            st = L.eligible_steps(P, ad, W, isolated=False)
            step_set = "all"
        if st.height < 3 or sw.height < 30:
            out[ch] = {"testable": False, "n_steps": st.height, "step_set": step_set}
            continue
        pan = L.Panel(ad, sw, st["t"].to_numpy(), W, st["pt_date"].to_numpy())
        S, _ = pan.counts(pan.sw_t)
        Sn, _ = pan.null(999, seed=P["g"])
        r = L.step_response(S, Sn, B=2000, seed=P["g"])
        o = {"testable": True, "step_set": step_set, "n_steps": len(S), "X": r["X"], "X_ci": r["X_ci"], "p_X": r["p_X"]}
        q0, qd = L.quiet_windows(P, ad, W)
        if len(q0) >= 5:
            pq = L.Panel(ad, sw, q0, W, qd)
            Sq, _ = pq.counts(pq.sw_t)
            Sqn, _ = pq.null(999, seed=P["g"] + 1)
            o["D"] = L.dispersion(Sq, Sqn)["D"]
            br = L.burst_ratio(S, Sn, Sq, Sqn, B=2000, seed=P["g"])
            o["BR"], o["BR_ci"] = br["BR"], br["BR_ci"]
        out[ch] = o
    return out


def kick(P: dict) -> dict:
    import run_periods as RP  # noqa: E402  (same kickoff estimator as round 1)
    return {ch: RP.kickoff_ratio(P, ch) for ch in ("work", "attn")}


def score(tail: dict, kicks: dict) -> dict:
    s = {}
    ok = all(tail[c].get("testable") for c in ("work", "attn"))
    if ok:
        s["C1"] = all(tail[c]["X"] > 1 and tail[c]["p_X"] < FROZEN["alpha"] for c in ("work", "attn"))
        s["C2"] = all(tail[c]["X_ci"][0] <= 1 <= tail[c]["X_ci"][1] and tail[c]["X"] < FROZEN["X_W1_Q05"][c] for c in ("work", "attn"))
        s["C3"] = all(tail[c].get("D", np.inf) <= FROZEN["D_max"] for c in ("work", "attn"))
        s["C4"] = all(tail[c].get("BR_ci", (2, 2))[0] <= 1 <= tail[c].get("BR_ci", (0, 0))[1] for c in ("work", "attn"))
    else:
        s.update({k: "not testable" for k in ("C1", "C2", "C3", "C4")})
    ks = [v.get("K") for k in kicks.values() for v in k.values() if v and v.get("K") is not None]
    s["C5"] = bool(ks) and all(k > 1 for k in ks)
    s["claim_confirmed"] = bool(ok and s["C2"] and s["C3"] and s["C4"])
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.confirm == a.dry_run:
        sys.exit("choose exactly one of --confirm / --dry-run")
    me = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:12]
    if a.confirm:
        if os.environ.get("H104_CONFIRM") != "1":
            sys.exit("refused: set H104_CONFIRM=1 (Vivian's sign-off) to touch the locked holdout")
        import holdout_ledger as HL
        for tgt in ("#51-tail", "G43", "G45"):
            chk = HL.check("H104", tgt, "project labels", ["project_potts", "artifact_lineage"])
            if not chk["allowed"]:
                sys.exit(f"refused by the holdout ledger for {tgt}: {chk}")
            if chk["needs_disclosure"]:
                print(f"disclosure needed for {tgt}:", sorted({u['hypothesis'] for u in chk['competing_planned']}))
        cfg, root, allow = TARGETS, OUT, True
    else:
        cfg, root, allow = STANDINS, SCRATCH, False
    g, (lo, hi) = cfg["tail"]
    tail_days = days_of(g, lo, hi, allow)
    B.main([g], allow_holdout=allow, out_root=root, days_filter=tail_days)
    tail = step_tests(L.load_period(g, root))
    kicks = {}
    for kg in cfg["kick"]:
        B.main([kg], allow_holdout=allow, out_root=root)
        kicks[kg] = kick(L.load_period(kg, root))
    res = {"mode": "confirm" if a.confirm else "dry-run", "script_sha": me, "frozen": FROZEN, "tail": tail,
           "kickoffs": kicks, "score": score(tail, kicks)}
    root.mkdir(parents=True, exist_ok=True)
    (root / "confirm_result.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
