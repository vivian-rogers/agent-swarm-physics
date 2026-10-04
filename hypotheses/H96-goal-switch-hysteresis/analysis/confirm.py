"""H96 confirmatory script (LOCKED HOLDOUT). Written 2026-10-04 after exploratory round 1. NOT RUN.

Frozen predictions (thresholds fixed from round 1, before any holdout data is loaded; bge primary, gte reported):
  C1 quench: over held-out transitions with an identified old state (M_pre CI > 0), the random-effects mean of
     dR1 = R1(switch) - median R1(non-holdout pseudo-switches of the regime, round-1 reference) is < 0 with the
     95% CI below 0.                                                                                          [0.85]
  C2 quench count: R1 < the regime's pseudo-switch median in >= 2/3 of those transitions.                    [0.8]
  C3 no positive order dependence (HH123): Spearman rho(q, ln tau_sw) over transitions with tau_sw < 500 h is
     <= +0.29 (the synthetic null's 95th percentile).                                                          [0.8]
  C4 the round-1 sign: that rho is < 0.                                                                        [0.55]
Targets: transitions with at least one held-out side, both sides in one regime, >= 3 placebo old states:
  8->9, 9->10, 13->14, 14->15, 15->16, 21->22, 27->28, 28->29, 29->30, 33->34, 34->35, 42->43, 43->44, 44->45,
  45->46, 46->47, 47->48, 48->49, 49->50, 50->51 (#22->#23 and #23->#24 stay excluded: H10's blind pair).
Placebo old states and pseudo-switch references come from non-holdout periods only (round-1 tables).

Reuse disclosure (hypotheses/holdout.md): these targets are planned by H82 (remanence regression, same content
modality, different statistic), H54 and H10 (kickoff alignment, quench). H96's statistic (field-orthogonal
old-state persistence ratio and switching time) is a different statistic; disclose in the card and LOG.md first.

Safeguards:
  * refuses to touch the holdout without --confirm --i-understand-this-uses-the-locked-holdout;
  * refuses unless this file, the card, h96lib.py, run.py and scheme/build.py are tracked and unmodified;
  * calls infra/shared/holdout_ledger.check() per target before loading anything;
  * --dry-run evaluates non-holdout stand-ins (39->40, 40->41, 41->42, 19->20, 20->21) with the frozen code and
    asserts that no held-out day is present.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h96lib as L  # noqa: E402

ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
TARGETS = [(8, 9), (9, 10), (13, 14), (14, 15), (15, 16), (21, 22), (27, 28), (28, 29), (29, 30), (33, 34),
           (34, 35), (42, 43), (43, 44), (44, 45), (45, 46), (46, 47), (47, 48), (48, 49), (49, 50), (50, 51)]
STANDINS = [40, 41, 42, 20, 21]
RHO_NULL_P95 = 0.288
FILES = [f"hypotheses/H96-goal-switch-hysteresis/{f}" for f in
         ("analysis/confirm.py", "README.md", "analysis/h96lib.py", "analysis/run.py", "scheme/build.py")]


def git_clean() -> bool:
    for f in FILES:
        tracked = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--error-unmatch", f], capture_output=True).returncode == 0
        dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", f], capture_output=True, text=True).stdout.strip()
        if not tracked or dirty:
            print(f"refusing: {f} is untracked or modified", file=sys.stderr)
            return False
    return True


def evaluate(S, recs, ref):
    rows = []
    for r in recs:
        s = L.summarize(L.projections(S, S.X, r), n_boot=1000, seed=r["P"])
        rows.append({"P": r["P"], "regime": r["regime"], "state": s, "ref": ref[r["regime"]]["median"]})
    ok = [x for x in rows if x["state"]["M_pre"]["lo"] > 0 and np.isfinite(x["state"]["R1"]["est"])]
    d = [x["state"]["R1"]["est"] - x["ref"] for x in ok]
    se = [(x["state"]["R1"]["hi"] - x["state"]["R1"]["lo"]) / 3.92 for x in ok]
    import run as R
    re_ = R.re_mean(d, se)
    below = np.mean([x["state"]["R1"]["est"] < x["ref"] for x in ok]) if ok else np.nan
    sw = [x for x in ok if np.isfinite(x["state"]["tau_sw"]["est"]) and x["state"]["tau_sw"]["est"] < 500]
    rho = spearmanr([x["state"]["q"] for x in sw], np.log([x["state"]["tau_sw"]["est"] for x in sw]))[0] if len(sw) >= 5 else np.nan
    return {"n": len(rows), "n_identified": len(ok), "C1_dR1_RE": re_, "C1": bool(re_["hi"] is not None and re_["hi"] < 0),
            "C2_share_below": float(below), "C2": bool(below >= 2 / 3), "C3_rho": float(rho), "C3": bool(rho <= RHO_NULL_P95),
            "C4": bool(rho < 0), "rows": rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--model", default="bge_small")
    a = ap.parse_args()
    ref = json.loads((L.DATA / f"results/pseudo_{a.model}_style_resid32.json").read_text())["reference"]
    if a.dry_run:
        S = L.Store(a.model, "style_resid32")
        recs = [r for r in L.transition_records() if r["P"] in STANDINS]
        days = {d for r in recs for d in r["old_days"] + r["post_days"] + [r["pre_day"]]}
        from common import holdout_mask
        assert not any(holdout_mask(sorted(days), [0] * len(days)))
        out = evaluate(S, recs, ref)
        out.pop("rows")
        (L.DATA / "confirm_dryrun.json").write_text(json.dumps(out, indent=1, default=float))
        print("dry run on stand-ins:", json.dumps(out, default=float))
        return
    if not (a.confirm and a.ack):
        sys.exit("refusing: confirmatory run needs --confirm --i-understand-this-uses-the-locked-holdout (Vivian's sign-off)")
    if not git_clean():
        sys.exit(1)
    import holdout_ledger as HL
    for p0, p1 in TARGETS:
        for g in (p0, p1):
            chk = HL.check("H96", f"G{g:02d}", "content", ["content_alignment"])
            if not chk["allowed"]:
                sys.exit(f"refusing: ledger blocks G{g:02d}: {chk['prior_runs_same_family']}")
            if chk["needs_disclosure"]:
                print(f"disclosure needed for G{g:02d} (see card)")
    S, recs = holdout_store(a.model)
    out = evaluate(S, recs, ref)
    (L.DATA / f"confirm_{a.model}.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, default=float))


def holdout_store(model):
    """Store whose statements include the target periods (held-out included); records built with scheme rules."""
    import datetime as dt  # noqa: F401
    goals_t = sorted({g for t in TARGETS for g in t})
    st = pl.read_parquet(L.OUT / "embeddings/statements.parquet").with_row_index("row")
    st = st.filter(~pl.col("agent").is_in(list(L.EXCLUDE_AGENTS)) & ~pl.col("goal_no").is_in([23])
                   & (pl.col("goal_no").is_in(goals_t) | ~pl.col("holdout")))
    from embed_models import statement_vectors
    X = L.unit(statement_vectors(model, "style_resid32")[st["row"].to_numpy()].astype(np.float32))
    S = L.Store.__new__(L.Store)
    S.st = st.with_columns(pl.col("regime").cast(pl.String)); S.X = X; S.model = model
    base = L.Store(model, "style_resid32", X=np.zeros((1, 32), np.float32))
    for k in ("cal", "win_start", "win_s", "goals", "G"):
        setattr(S, k, getattr(base, k))
    S.agent = S.st["agent"].to_numpy(); S.day = S.st["pt_date"].to_numpy(); S.t = S.st["t"].to_numpy()
    S.goal = S.st["goal_no"].to_numpy()
    cal = S.cal.sort("pt_date")
    late = pl.read_parquet(L.DATA / "late_days.parquet")
    recs = []
    for p0, p1 in TARGETS:
        old = cal.filter(pl.col("goal_no") == p0); new = cal.filter(pl.col("goal_no") == p1)
        if old.height < 2 or new.height < 1:
            continue
        reg = old["regime"][-1]
        odays = [d for d, r in zip(old["pt_date"].to_list()[:-1][-3:], old["regime"].to_list()[:-1][-3:]) if r == reg]
        pdays = [d for d, r in zip(new["pt_date"].to_list()[:3], new["regime"].to_list()[:3]) if r == reg]
        plac = sorted(q for q in late.filter(pl.col("regime") == reg)["goal_no"].unique().to_list()
                      if q not in range(p1 - 2, p1 + 2))
        if not odays or not pdays or len(plac) < 3:
            continue
        k = S.goals.filter((pl.col("goal_no") == p1) & (pl.col("kind") == "kickoff"))
        t0 = k["win_start"][0] if k.height else new["win_start"].min()
        fg = S.goals.filter((pl.col("goal_no") == p1) & pl.col("kind").is_in(["kickoff", "goal", "kickoff_room"]))["gid"]
        recs.append({"P": p1, "Pm1": p0, "regime": reg, "t0": t0, "pre_day": old["pt_date"][-1], "old_days": odays,
                     "post_days": pdays, "placebos": plac, "field_gids": sorted(fg.to_list()),
                     "first_day": new["pt_date"][0]})
    return S, recs


if __name__ == "__main__":
    main()
