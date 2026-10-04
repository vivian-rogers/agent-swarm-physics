"""H31 confirmatory test on the LOCKED HOLDOUT (written after exploratory round 1; NOT RUN).

Targets (card, chosen before round 1 to avoid H11's confirmation periods #22/#28/#45):
  E-P (project consensus):     #29, #46, #47, #50
  E-C (content convergence):   #29, #46, #47, #49, #50

Frozen inputs: analysis/frozen_rule.json (copied from data/processed/.../frozen_rule.json after round 1).
Pipeline: identical to round 1. H11's project labels are rebuilt for the targets by calling H11's scheme
functions (imported, never modified) with allow_holdout=True into data/processed/H31-.../confirm/; the H31 scheme
(scheme/build.py: build_period(..., allow_holdout=True)) is written into the same confirm folder.

Decision rules (frozen 2026-10-03):
  C1 (H31 primary)  On target uncensored E-P events, the frozen lambda rule  log tau = c_lambda - log lambda2_w,sym
                    has lower log-RMSE than the frozen constant rule  log tau = c0.          PASS / FAIL.
  C1b (post hoc)    Same with the round-1 free-slope rule  log tau = c + b log(1/lambda2)  (b = 0.37 at W = 30).
  C2 (forecast)     >= 70% of target uncensored E-P events fall inside the chosen rule's 80% interval.
  C3 (content)      If >= 3 target E-C convergence events: the frozen gamma_tr rule beats the frozen constant.
  C4 (descriptive)  sign of the slope of log tau on log(1/lambda2) across target events; event counts.
  H31 is CONFIRMED only if C1 passes; the forecast rule is CONFIRMED if C2 passes.

Holdout reuse policy (hypotheses/holdout.md): #46-#50 sit in the NE21+NE23 window used by H04 (activity timing,
Hawkes); #29 is untouched. H31's observable (consensus-event timing from project labels and content alignment,
against exposure-graph spectra) is a different statistic and has not been examined on these periods. The script
refuses to run unless this file, the card and analysis/frozen_rule.json are committed and unmodified in git, and
it prints the disclosure to paste into both cards and LOG.md.

  uv run python hypotheses/H31-consensus-time-spectral-gap/analysis/confirm_holdout.py --dry-run
  uv run python hypotheses/H31-consensus-time-spectral-gap/analysis/confirm_holdout.py --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h31lib as L  # noqa: E402

TARGETS_EP = [29, 46, 47, 50]
TARGETS_EC = [29, 46, 47, 49, 50]
STANDINS_EP = [30, 41, 42, 44]          # dry run: non-holdout stand-ins (already explored; tests the code path only)
STANDINS_EC = [30, 41, 42, 44, 39]
CONFIRM = L.DATA / "confirm"
FROZEN = HERE / "frozen_rule.json"
SIGN = {"l2_sym": -1, "g_tr": -1, "tau_V": 1, "tau_wave": 1, "ul2_rw": -1, "l2_sym_core": -1}


def git_clean(paths) -> bool:
    for p in paths:
        r = subprocess.run(["git", "-C", str(L.ROOT), "ls-files", "--error-unmatch", str(p)], capture_output=True)
        if r.returncode != 0:
            return False
        d = subprocess.run(["git", "-C", str(L.ROOT), "diff", "--quiet", "HEAD", "--", str(p)])
        if d.returncode != 0:
            return False
    return True


def build_targets(goals, out: Path):
    """Rebuild H11 labels (H11 functions, allow_holdout) and the H31 scheme for held-out targets into out/."""
    import importlib.util
    sys.path.insert(0, str(L.ROOT / "hypotheses/H11-potts-labor-vs-herding/scheme"))
    spec = importlib.util.spec_from_file_location("h11_scheme_build", L.ROOT / "hypotheses/H11-potts-labor-vs-herding/scheme/build.py")
    h11 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h11)
    spec2 = importlib.util.spec_from_file_location("h31_scheme_build", L.HYP / "scheme/build.py")
    h31 = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(h31)
    cal = h11.load_calendar(goals, True)
    labs = {}
    for W in (30,):
        wins = h11.window_table(cal, W)
        lp, _ = h11.label_projects(h11.build_project(cal, W, wins))
        labs[W] = lp
    sh = h31.Shared()
    for g in goals:
        res = h31.build_period(sh, g, allow_holdout=True)
        if res is None:
            continue
        lab = labs[30].filter(pl.col("goal_no") == g).drop("day").join(res["cal"].select("pt_date", "day"), on="pt_date")
        res["states"] = {30: lab.select("pt_date", "day", "win", "agent", "room", "label", "project")}
        h31.write_period(g, res, out)


def evaluate(goals_ep, goals_ec, root: Path, rule: dict):
    from predictors import block_predictors
    from explore import label_matrix
    ev, ec = [], []
    for g in sorted(set(goals_ep) | set(goals_ec)):
        P = L.load_period(g, root)
        if P["days"] is None:
            continue
        for b in L.blocks_of(P):
            pr = block_predictors(P, b, with_voter=True)
            if pr is None:
                continue
            if g in goals_ep and P["states30"] is not None:
                lab, act_h, Nb, _ = label_matrix(P, b, 30)
                for e in L.detect_project_events(lab, act_h, Nb):
                    if e["consensus"]:
                        ev.append(dict(goal_no=g, room=b, frozen=e["frozen"], tau_h=e["tau_h"], **pr))
            if g in goals_ec and P["alignment"] is not None:
                f = L.detect_content_event(P["alignment"], b, L.period_T(P) / 3600)
                ec.append(dict(goal_no=g, room=b, kind=f.get("kind"), tau=f.get("tau", np.nan), **pr))
    ev = pl.DataFrame(ev) if ev else pl.DataFrame()
    out = {"n_consensus": ev.height}
    if ev.height:
        unc = ev.filter(~pl.col("frozen"))
        out["n_uncensored"] = unc.height
        out["n_frozen"] = ev.height - unc.height
        if unc.height:
            y = np.log(unc["tau_h"].to_numpy())
            lam = rule["lambda_rule"]
            p_lam = lam["log_c"] - np.log(unc["l2_sym"].to_numpy())
            p0 = np.full(len(y), rule["constant_rule"]["log_c"])
            r_lam, r0 = L.rmse(y, p_lam), L.rmse(y, p0)
            out["C1"] = dict(rmse_lambda=r_lam, rmse_const=r0, verdict="PASS" if r_lam < r0 else "FAIL")
            fr = rule.get("lambda_free_rule_posthoc")
            if fr:   # C1b (post hoc after round 1): free-slope lambda rule vs constant
                p_f = fr["log_c"] + fr["b"] * (-np.log(unc["l2_sym"].to_numpy()))
                out["C1b_posthoc"] = dict(rmse_free=L.rmse(y, p_f), rmse_const=r0,
                                          verdict="PASS" if L.rmse(y, p_f) < r0 else "FAIL")
            ch = rule["chosen"]
            if ch == "M0":
                pc = p0
            elif ch == "M_N":
                pc = rule["log_c"] + rule["a_N"] * np.log(unc["N_b"].to_numpy())
            else:
                p = rule["predictor"]
                pc = rule["log_c"] + SIGN[p] * np.log(np.maximum(unc[p].to_numpy(), 1e-6))
            lo, hi = rule["lopo_resid_q10_q90"]       # resid = pred - y
            inside = ((pc - y) >= lo) & ((pc - y) <= hi)
            out["C2"] = dict(rule=ch, frac_inside_80=float(inside.mean()), verdict="PASS" if inside.mean() >= 0.7 else "FAIL")
            if unc.height >= 3 and np.ptp(np.log(unc["l2_sym"].to_numpy())) > 0:
                out["C4_slope"] = float(L.ols(-np.log(unc["l2_sym"].to_numpy()), y)[1])
    ec = pl.DataFrame(ec) if ec else pl.DataFrame()
    if ec.height:
        conv = ec.filter(pl.col("kind") == "convergence")
        out["ec_kinds"] = {k: int(v) for k, v in zip(*np.unique(ec["kind"].to_numpy().astype(str), return_counts=True))}
        crule = rule.get("content_rule")
        if conv.height >= 3 and crule:
            y = np.log(conv["tau"].to_numpy())
            ptr = crule["log_c_tr"] - np.log(np.maximum(conv["g_tr"].to_numpy(), 1e-6))
            p0 = np.full(len(y), crule["log_c0"])
            out["C3"] = dict(rmse_tr=L.rmse(y, ptr), rmse_const=L.rmse(y, p0),
                             verdict="PASS" if L.rmse(y, ptr) < L.rmse(y, p0) else "FAIL")
        else:
            out["C3"] = dict(verdict="n/a (fewer than 3 convergence events or no content rule)", n=conv.height)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="non-holdout stand-ins, existing round-1 data")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    a = ap.parse_args()
    if not FROZEN.exists():
        raise SystemExit("refusing: analysis/frozen_rule.json (round-1 frozen rule) is missing")
    rule = json.loads(FROZEN.read_text())
    sha = hashlib.sha256(FROZEN.read_bytes()).hexdigest()[:16]
    if a.dry_run:
        print(f"DRY RUN on non-holdout stand-ins (E-P {STANDINS_EP}, E-C {STANDINS_EC}); frozen rule sha {sha}")
        held = set(L_holdout())
        assert not (set(STANDINS_EP + STANDINS_EC) & held), "stand-ins must be non-holdout"
        res = evaluate(STANDINS_EP, STANDINS_EC, L.DATA, rule)
        (L.DATA / "confirm_dryrun.json").write_text(json.dumps(res, indent=1, default=float))
        print(json.dumps(res, indent=1, default=float))
        print("NOTE: stand-ins were explored in round 1, so this checks the code path only.")
        return
    if not (a.confirm and a.ack):
        raise SystemExit("refusing: the confirmatory run uses the locked holdout. Pass --confirm "
                         "--i-understand-this-uses-the-locked-holdout (after Vivian's sign-off), or --dry-run.")
    must = [Path(__file__).resolve(), L.HYP / "README.md", FROZEN]
    if not git_clean(must):
        raise SystemExit("refusing (holdout reuse policy): commit this script, the card and analysis/frozen_rule.json "
                         "unmodified before the confirmatory run.")
    held = set(L_holdout())
    assert set(TARGETS_EP + TARGETS_EC) <= held, "targets must be held-out periods"
    print("DISCLOSURE (paste into the H31 and H04 cards and LOG.md): H31 confirmatory run uses held-out periods "
          f"{sorted(set(TARGETS_EP + TARGETS_EC))}. #46-#50 lie in the NE21+NE23 window, which H04 used for activity "
          "timing (Hawkes n); H31 uses consensus-event timing from project labels and content alignment, a different, "
          f"unexamined statistic. Frozen rule sha {sha}.")
    CONFIRM.mkdir(parents=True, exist_ok=True)
    build_targets(sorted(set(TARGETS_EP + TARGETS_EC)), CONFIRM)
    res = evaluate(TARGETS_EP, TARGETS_EC, CONFIRM, rule)
    res["frozen_rule_sha"] = sha
    (CONFIRM / "confirm_results.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res, indent=1, default=float))


def L_holdout():
    return json.loads((L.ROOT / "hypotheses/holdout.json").read_text())["goal_periods_held_out"]


if __name__ == "__main__":
    main()
