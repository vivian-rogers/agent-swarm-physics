"""H110 confirmatory run on the LOCKED HOLDOUT. Written and frozen 2026-10-04 after exploratory round 1. NOT RUN.

Targets: the held-out regime-III goal transitions #42->#43, #43->#44, #44->#45, #45->#46, #46->#47, #47->#48, #48->#49,
#50->#51 (exchange-bias contrast) and NE24 = #49->#50 (2026-06-29, GitHub -> GitLab: the pinning layer is replaced).

Frozen predictions (round-1 estimators unchanged: H96-construction old-state remanence m on style_resid32 statements,
field span = kickoff + goal chunks + room kickoffs, placebo old states from same-regime non-adjacent periods, pinned =
agent work commit to an own repo (owner = earliest agent work commit) in the last 2 active days before the kickoff,
pooled ratio-of-sums over transitions with >= 2 agents per group, agent-cluster bootstrap 2000; bge scored, gte reported):
  C1 (HH340 detection): pooled dR = R1_P - R1_U over the non-NE24 targets has 95% CI lower > 0 AND rho_lambda >= 2.   [0.25]
  C2 (HH340 kill): pooled rho_lambda in [0.8, 1.25] over the non-NE24 targets.                                      [0.35]
  C3 (NE24): at #49->#50 the pinned advantage vanishes: dR(NE24) <= 0.10 (or a group has < 2 agents: void).          [0.5]
  C4 (offset end, HH340's signature): pooled pinned excess while still committing e(live) has CI lower > 0.06 (the
     S0 synthetic 95th percentile, bge) and e(after) <= e(live)/2.                                                   [0.15]
Round 1 (non-holdout) for reference: dR 0.30 [-0.005, 0.57], rho_lambda 2.2 (CI lower at the floor 1.0); e(live) 0.00.

Reuse policy (hypotheses/holdout.md): the same transitions are planned by H96 (old-state remanence, the estimator H110
re-implements: a close cousin, disclose), H82, H54, H10 (#22/#23 not used here), H70 (NE24 C1) and H01/H58 (NE24
continuity). Disclose in the card and LOG.md before running; run after H96's confirm or declare second use.

Guards: needs BOTH --confirm and H110_CONFIRM=1; refuses unless the sha256 of h110lib.py, scheme/build.py and this file
match analysis/confirm.sha256; calls holdout_ledger.check() per target (families content_alignment, artifact_lineage).
--dry-run runs the identical pipeline on non-holdout stand-ins (#36->#37, #37->#38, #40->#41, #41->#42; NE24 stand-in
#40->#41), asserts no held-out row, and writes to data/processed/H110-exchange-bias-own-artifact/confirm_dryrun/.

Usage:
  uv run python hypotheses/H110-exchange-bias-own-artifact/analysis/confirm.py --dry-run
  H110_CONFIRM=1 uv run python hypotheses/H110-exchange-bias-own-artifact/analysis/confirm.py --confirm
  uv run python hypotheses/H110-exchange-bias-own-artifact/analysis/confirm.py --freeze
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
import h110lib as L  # noqa: E402

FROZEN_FILES = [HERE / "h110lib.py", HERE.parent / "scheme/build.py", Path(__file__).resolve()]
SHA_FILE = HERE / "confirm.sha256"
TARGETS = [43, 44, 45, 46, 47, 48, 49, 51]
NE24 = 50
STANDINS = [37, 38, 41, 42]
STANDIN_NE24 = 41
FROZEN = {"kill": (0.8, 1.25), "ne24_dR": 0.10, "e_live_q95": 0.06}


def digest() -> dict:
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in FROZEN_FILES}


def inputs(targets: list, allow: bool):
    cal = B.active_days(include_holdout=allow)
    tr = B.transitions(cal, targets, include_holdout=allow)
    st = B.statements(include_holdout=allow)
    win = B.windows(st, tr)
    wc = B.work(include_holdout=allow)
    pin = B.pinning(wc, B.owners(wc), tr, st)
    if not allow:
        sys.path.insert(0, str(L.ROOT / "infra/shared"))
        from common import holdout_mask
        assert not any(holdout_mask(win["pt_date"].to_list(), win["goal_no"].to_list())), "held-out row in a dry run"
    return tr, win, pin


def evaluate(targets: list, ne24: int, allow: bool, model: str) -> dict:
    tr, win, pin = inputs(targets + [ne24], allow)
    X = L.load_X(win["srow"].to_numpy(), model)
    proj = L.field_projectors(tr, model, include_holdout=allow)
    rem = L.remanence(tr, win, X, proj)
    pan = L.panel(rem, pin, "m", "pinned_own")
    main = L.persistence(pan.filter(pl.col("P") != ne24))
    ne = L.persistence(pan.filter(pl.col("P") == ne24))
    off = L.offset_end(pan.filter(pl.col("P") != ne24))
    return {"main": main, "ne24": ne, "offset": off, "n_transitions": tr.height}


def score(r: dict) -> dict:
    m, ne, off = r["main"], r["ne24"], r["offset"]
    s = {}
    if m.get("n", 0) > 0:
        s["C1"] = bool(m["dR_ci"][0] > 0 and m["ratio"] >= 2)
        s["C2"] = bool(FROZEN["kill"][0] <= m["ratio"] <= FROZEN["kill"][1])
    else:
        s["C1"] = s["C2"] = "not testable"
    s["C3"] = bool(ne["dR"] <= FROZEN["ne24_dR"]) if ne.get("n", 0) > 0 else "void (< 2 agents per group)"
    if off.get("live") is not None and off.get("live_ci"):
        s["C4"] = bool(off["live_ci"][0] > FROZEN["e_live_q95"] and off.get("after") is not None and off["after"] <= off["live"] / 2)
    else:
        s["C4"] = "not testable"
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
        if os.environ.get("H110_CONFIRM") != "1":
            sys.exit("refused: set H110_CONFIRM=1 (Vivian's sign-off) to touch the locked holdout")
        sys.path.insert(0, str(L.ROOT / "infra/shared"))
        import holdout_ledger as HL
        for tgt in [f"G{g}" for g in TARGETS + [NE24]] + ["NE24"]:
            chk = HL.check("H110", tgt, "content", ["content_alignment", "artifact_lineage"])
            if not chk["allowed"]:
                sys.exit(f"refused by the holdout ledger for {tgt}: {chk}")
            if chk["needs_disclosure"]:
                print(f"disclosure needed for {tgt}:", sorted({u["hypothesis"] for u in chk["competing_planned"] + chk["prior_runs"]}))
        targets, ne24, allow, out = TARGETS, NE24, True, L.D / "confirm"
    else:
        targets, ne24, allow, out = [t for t in STANDINS if t != STANDIN_NE24], STANDIN_NE24, False, L.D / "confirm_dryrun"
    out.mkdir(parents=True, exist_ok=True)
    res = {}
    for model in L.MODELS:
        r = evaluate(targets, ne24, allow, model)
        res[model] = {"result": r, "score": score(r) if model == "bge_small" else "reported, not scored"}
    tag = "confirm" if a.confirm else "dryrun"
    (out / f"{tag}.json").write_text(json.dumps(res, indent=1, default=lambda o: o.item() if isinstance(o, np.generic) else str(o)))
    print(json.dumps({m: {"score": res[m]["score"], "main_ratio": res[m]["result"]["main"].get("ratio"),
                          "main_dR": res[m]["result"]["main"].get("dR"), "ne24_dR": res[m]["result"]["ne24"].get("dR")}
                      for m in res}, indent=1, default=str))


if __name__ == "__main__":
    main()
