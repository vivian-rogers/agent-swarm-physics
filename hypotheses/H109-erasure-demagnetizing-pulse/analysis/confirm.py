"""H109 confirmatory run on the LOCKED HOLDOUT. Written and frozen 2026-10-04 after exploratory round 1. NOT RUN.

Targets: forced context erasures (NE41) in the held-out regime-III two-room periods #45 (45a, 45b), #46 (46a-46c; 46d
has #rest + #showcase-live and is dropped), #47 and #50 (50a-50f), rooms #best (+1) / #rest (-1). #48, #49 and the
#51 tail are single-room and are not used.

Frozen predictions (round-1 estimators unchanged: restate-deduped bge style_resid statements, leave-agent-out spontaneous
room axis with room-kickoff and operator directions projected out, agent constants from non-holdout regime-III periods,
0.05-decade gap strata within agent, agent-day cluster bootstrap 1000; gte reported, not scored):
  C1 (HH339 kill, expected to hold): the random-effects mean of delta_F over the target periods with an identified
     pre level has its 95% CI upper bound < 0.30.                                                          [0.8]
  C2 (no drop): the RE point estimate of delta_F <= 0.05 (round 1: -0.08; a small rise is the post hoc direction).  [0.7]
  C3 (prompt-held field): |RE delta_K| < 0.15 where the kickoff pre level is identified in >= 2 targets.     [0.6]
Reading: C1 and C2 confirm "a forced erasure does not demagnetize an agent's room alignment". C1 failing with
delta_F >= 0.30 and CI > 0 would revive HH339.

Reuse policy (hypotheses/holdout.md): #45-#47 and #50 content is planned by many hypotheses (H23, H26, H47, H81-H83,
H100, H102, ...), family content_alignment. H109's statistic (an erasure-boundary change of one agent's room
alignment) is new, but the modality (agent content) is shared: disclose in the card and LOG.md before running.

Guards: needs BOTH --confirm and H109_CONFIRM=1; refuses unless the sha256 of h109lib.py, scheme/build.py and this file
match analysis/confirm.sha256 (the freeze); calls holdout_ledger.check() per target and refuses if not allowed.
--dry-run runs the identical pipeline on non-holdout stand-ins (#38, #41, #44), asserts that no held-out row is loaded,
and writes to data/processed/H109-erasure-demagnetizing-pulse/confirm_dryrun/.

Usage:
  uv run python hypotheses/H109-erasure-demagnetizing-pulse/analysis/confirm.py --dry-run
  H109_CONFIRM=1 uv run python hypotheses/H109-erasure-demagnetizing-pulse/analysis/confirm.py --confirm
  uv run python hypotheses/H109-erasure-demagnetizing-pulse/analysis/confirm.py --freeze   (writes confirm.sha256)
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
import h109lib as L  # noqa: E402

FROZEN_FILES = [HERE / "h109lib.py", HERE.parent / "scheme/build.py", Path(__file__).resolve()]
SHA_FILE = HERE / "confirm.sha256"
TARGET_UNITS = {u: (2, 3) for u in ["45a", "45b", "46a", "46b", "46c", "47", "50a", "50b", "50c", "50d", "50e", "50f"]}
TARGET_GOALS = [45, 46, 47, 50]
STANDIN_UNITS = {u: (2, 3) for u in ["38a", "38b", "38c", "38d", "38e", "41", "44a", "44b"]}
STANDIN_GOALS = [38, 41, 44]
FROZEN = {"kill": 0.30, "c2": 0.05, "c3": 0.15}


def digest() -> dict:
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in FROZEN_FILES}


def evaluate(units: dict, goals: list, allow: bool, model: str) -> dict:
    sm, ct = B.build_statements(include_holdout=allow)
    if not allow:
        assert not sm["hm"].any() and not sm["holdout"].any(), "held-out row loaded in a dry run"
    ur = pl.DataFrame({"unit_id": list(units), "rA": [v[0] for v in units.values()], "rB": [v[1] for v in units.values()]})
    sm = sm.drop("roomA", "roomB", "scoped", "sigma").join(ur, on="unit_id", how="left").rename({"rA": "roomA", "rB": "roomB"})
    sm = sm.with_columns(((pl.col("room") == pl.col("roomA")) | (pl.col("room") == pl.col("roomB"))).fill_null(False).alias("scoped"),
                         pl.when(pl.col("room") == pl.col("roomA")).then(1).when(pl.col("room") == pl.col("roomB"))
                         .then(-1).otherwise(0).cast(pl.Int8).alias("sigma"))
    sm = sm.sort("sid")
    bd = B.boundaries(sm, "restate")
    X = L.load_X(sm, model)
    # agent constants from non-holdout periods only
    nh = ~sm["hm"].to_numpy()
    Xc = L.day_center(sm, X)
    A = L.agent_constants(sm.filter(pl.Series(nh)), Xc[nh])
    F = L.field_dirs(model, include_holdout=allow)
    a, bk, info = L.axes_and_alignment(sm, Xc, X, A, F)
    ev = L.event_table(bd, sm, a, "restate")
    evK = L.event_table(bd, sm, bk, "restate")
    per = {}
    for P in goals:
        d = L.delta(ev.filter(pl.col("period") == P), "F", 1000, P)
        k = L.delta(evK.filter(pl.col("period") == P), "F", 500, P)
        per[P] = {"F": d, "K": k, "axis": info.get(P)}
    okF = [P for P in goals if per[P]["F"].get("n", 0) > 0 and per[P]["F"]["A_pre_ci"][0] > 0]
    okK = [P for P in goals if per[P]["K"].get("n", 0) > 0 and per[P]["K"]["A_pre_ci"][0] > 0]
    re_F = L.re_meta([per[P]["F"]["delta"] for P in okF], [per[P]["F"]["delta_se"] for P in okF])
    re_K = L.re_meta([per[P]["K"]["delta"] for P in okK], [per[P]["K"]["delta_se"] for P in okK])
    return {"periods": per, "re_F": re_F, "re_K": re_K, "identified_F": okF, "identified_K": okK}


def score(r: dict) -> dict:
    s = {}
    if "mu" in r["re_F"]:
        s["C1"] = r["re_F"]["ci"][1] < FROZEN["kill"]
        s["C2"] = r["re_F"]["mu"] <= FROZEN["c2"]
    else:
        s["C1"] = s["C2"] = "not testable (< 2 identified periods)"
    s["C3"] = (abs(r["re_K"]["mu"]) < FROZEN["c3"]) if ("mu" in r["re_K"] and len(r["identified_K"]) >= 2) else "not testable"
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--freeze", action="store_true")
    a = ap.parse_args()
    if a.freeze:
        SHA_FILE.write_text(json.dumps(digest(), indent=1))
        print("frozen:", digest())
        return
    if a.confirm == a.dry_run:
        sys.exit("choose exactly one of --confirm / --dry-run")
    if not SHA_FILE.exists() or json.loads(SHA_FILE.read_text()) != digest():
        sys.exit("refused: frozen files changed since the freeze (confirm.sha256)")
    if a.confirm:
        if os.environ.get("H109_CONFIRM") != "1":
            sys.exit("refused: set H109_CONFIRM=1 (Vivian's sign-off) to touch the locked holdout")
        sys.path.insert(0, str(L.ROOT / "infra/shared"))
        import holdout_ledger as HL
        for tgt in [f"G{g}" for g in TARGET_GOALS]:
            chk = HL.check("H109", tgt, "content", ["content_alignment"])
            if not chk["allowed"]:
                sys.exit(f"refused by the holdout ledger for {tgt}: {chk}")
            if chk["needs_disclosure"]:
                print(f"disclosure needed for {tgt}:", sorted({u["hypothesis"] for u in chk["competing_planned"] + chk["prior_runs"]}))
        units, goals, allow = TARGET_UNITS, TARGET_GOALS, True
        out = L.D / "confirm"
    else:
        units, goals, allow = STANDIN_UNITS, STANDIN_GOALS, False
        out = L.D / "confirm_dryrun"
    out.mkdir(parents=True, exist_ok=True)
    res = {}
    for model in L.MODELS:
        r = evaluate(units, goals, allow, model)
        res[model] = {"result": r, "score": score(r) if model == "bge_small" else "reported, not scored"}
    tag = "confirm" if a.confirm else "dryrun"
    (out / f"{tag}.json").write_text(json.dumps(res, indent=1, default=lambda o: o.item() if isinstance(o, np.generic) else str(o)))
    print(json.dumps({m: {"re_F": res[m]["result"]["re_F"], "re_K": res[m]["result"]["re_K"], "score": res[m]["score"]}
                      for m in res}, indent=1, default=str))


if __name__ == "__main__":
    main()
