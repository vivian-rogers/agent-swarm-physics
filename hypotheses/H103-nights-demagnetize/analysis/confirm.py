"""H103 confirmatory script (LOCKED HOLDOUT). Written 2026-10-04 after exploratory round 1. NOT RUN.

Frozen predictions (fixed from round 1, before any holdout data is loaded; bge primary, gte reported):
  C1 the kill holds: among held-out periods whose kickoff remanence decays (best-clock dA CI > 0), the active-hour
     clock fits as well as or better than the night clock (SSE_H <= SSE_N) in >= 1/2.                          [0.8]
  C2 no night step at fixed active lag: the RE mean of beta_N over held-out units has a CI that includes 0 and
     |RE| < 0.03.                                                                                                [0.75]
  C3 nights re-magnetize: the RE mean of S_N - S_mid over held-out O1 periods is > 0.                           [0.6]
  C4 an agent's own idle gap does not age content: the RE mean of beta_gap is > 0.                              [0.7]
Targets: held-out goal periods with >= 3 active days and a shared kickoff (#1, #14, #15, #22, #28, #29, #34, #45,
#46, #47, #49, #50) and the #51 tail (O3 only). Decoy kickoffs stay non-holdout (round-1 set).

Reuse disclosure (hypotheses/holdout.md): content statistics on these targets are planned by H20, H54, H82 and H96
(different statistics). H103's statistics (clock comparison of decay; two-time night step) are new; disclose in the
card and LOG.md before running.

Safeguards:
  * refuses to touch the holdout without --confirm --i-understand-this-uses-the-locked-holdout;
  * refuses unless this file, the card, h103lib.py, run.py and scheme/build.py are tracked and unmodified;
  * calls infra/shared/holdout_ledger.check() per target before loading anything;
  * --dry-run evaluates non-holdout stand-ins (G38, G39, G40, G41, G42) with the frozen code (no holdout read).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h103lib as L  # noqa: E402

ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
TARGETS = [1, 14, 15, 22, 28, 29, 34, 45, 46, 47, 49, 50]
STANDINS = [38, 39, 40, 41, 42]
FILES = [f"hypotheses/H103-nights-demagnetize/{f}" for f in
         ("analysis/confirm.py", "README.md", "analysis/h103lib.py", "analysis/run.py", "scheme/build.py")]


def git_clean() -> bool:
    for f in FILES:
        tracked = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--error-unmatch", f], capture_output=True).returncode == 0
        dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", f], capture_output=True, text=True).stdout.strip()
        if not tracked or dirty:
            print(f"refusing: {f} is untracked or modified", file=sys.stderr)
            return False
    return True


def evaluate(S, goals, units):
    import run as R
    o1 = {}
    for rec in S.periods.filter(pl.col("goal_no").is_in(goals)).to_dicts():
        if rec["goal_no"] in S.kick:
            o1[rec["goal_no"]] = L.o1_period(S, rec, n_boot=500, seed=rec["goal_no"])
    o3 = R.o3(S, n_boot=500, units=units)
    dec = [r for r in o1.values() if r["verdict"] != "descriptive"]
    c1 = float(np.mean([r["sse"]["H"] <= r["sse"]["N"] for r in dec])) if dec else np.nan
    bn = R.card_o3(o3, "beta_N")["RE"] if o3 else {"est": np.nan, "lo": np.nan, "hi": np.nan}
    bg = R.card_o3(o3, "beta_gap")["RE"] if o3 else {"est": np.nan, "lo": np.nan, "hi": np.nan}
    sn = [(r["steps"]["S_N"] - r["steps"]["S_mid"], (r["SN_minus_Smid_ci"][1] - r["SN_minus_Smid_ci"][0]) / 3.92)
          for r in o1.values() if np.all(np.isfinite(r["SN_minus_Smid_ci"]))]
    snre = L.re_mean([a for a, b in sn], [b for a, b in sn])
    return {"n_o1": len(o1), "n_decay": len(dec), "C1_share_H_le_N": c1, "C1": bool(c1 >= 0.5) if dec else None,
            "C2_beta_N_RE": bn, "C2": bool(bn["lo"] <= 0 <= bn["hi"] and abs(bn["est"]) < 0.03),
            "C3_SN_minus_Smid_RE": snre, "C3": bool(snre["est"] > 0),
            "C4_beta_gap_RE": bg, "C4": bool(bg["est"] > 0)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--model", default="bge_small")
    a = ap.parse_args()
    if a.dry_run:
        S = L.Store(a.model, "style_resid")
        units = [u for u in S.w.filter(pl.col("goal_no").is_in(STANDINS))["unit_id"].unique().sort().to_list()]
        out = evaluate(S, STANDINS, units)
        (L.DATA / "confirm_dryrun.json").write_text(json.dumps(out, indent=1, default=float))
        print("dry run on stand-ins:", json.dumps(out, default=float))
        return
    if not (a.confirm and a.ack):
        sys.exit("refusing: confirmatory run needs --confirm --i-understand-this-uses-the-locked-holdout (Vivian's sign-off)")
    if not git_clean():
        sys.exit(1)
    import holdout_ledger as HL
    for t in [f"G{g:02d}" for g in TARGETS] + ["#51-tail"]:
        chk = HL.check("H103", t, "content", ["content_alignment"])
        if not chk["allowed"]:
            sys.exit(f"refusing: ledger blocks {t}: {chk['prior_runs_same_family']}")
        if chk["needs_disclosure"]:
            print(f"disclosure needed for {t} (see card)")
    spec = importlib.util.spec_from_file_location("h103build", ROOT / "hypotheses/H103-nights-demagnetize/scheme/build.py")
    B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)
    out_dir = L.DATA / "confirm_build"
    B.main(include_goals=TARGETS, out_dir=out_dir, tail_window=True)
    S = L.Store(a.model, "style_resid", data_dir=out_dir, extra_kickoffs=TARGETS)
    tail_units = S.w.filter((pl.col("goal_no") == 51) & (pl.col("pt_date") >= "2026-09-07"))["unit_id"].unique().to_list()
    units = S.w.filter(pl.col("goal_no").is_in(TARGETS))["unit_id"].unique().to_list() + tail_units
    out = evaluate(S, TARGETS, sorted(set(u for u in units if u)))
    (L.DATA / f"confirm_{a.model}.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, default=float))


if __name__ == "__main__":
    main()
