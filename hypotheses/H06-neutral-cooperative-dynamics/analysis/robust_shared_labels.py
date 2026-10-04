"""Robustness check (2026-10-04, requested by the coordinator): H11's modal() broke exact ties nondeterministically,
so H06's imported artifact labels can differ between rebuilds (~2.6% of windows tied). This reruns the artifact-label
analysis for the free weeks where artifact labels are testable (#31, #37, #44 #rest) on the deterministic shared
table data/processed/shared/project_states.parquet (w_min 30, sources "all"), with the same carry-forward (4 windows)
and the same pipeline, and compares LLR_NH, LLR_NC, lambda, beta and the verdicts with round 1.

Output: data/processed/H06-neutral-cooperative-dynamics/robust_shared_labels.json
Usage: uv run python hypotheses/H06-neutral-cooperative-dynamics/analysis/robust_shared_labels.py
"""
from __future__ import annotations

import json
import sys
from multiprocessing import get_context
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import explore as X  # noqa: E402
import ncd_core as M  # noqa: E402

ROOT = X.ROOT
SHARED = ROOT / "data/processed/shared/project_states.parquet"
SCOPES = {"G31": (31, None), "G37": (37, None), "G44": (44, 3)}


def run(scope):
    import build as B  # scheme/build.py (carry_forward)
    goal, room = SCOPES[scope]
    wins, day, remap, art_h11, _, _ = X.load_scope(scope)
    ps = pl.read_parquet(SHARED).filter((pl.col("w_min") == 30) & (pl.col("sources").cast(pl.String) == "all")
                                        & (pl.col("goal_no") == goal) & ~pl.col("holdout"))
    if room is not None:
        ps = ps.filter(pl.col("room") == room)
    ps = ps.join(wins.select("pt_date", "win", "gwin", "day"), on=["pt_date", "win"], how="inner")
    proj = ps.select("project").unique().sort("project").with_row_index("project_id")
    ps = ps.join(proj, on="project").with_columns(pl.col("project_id").cast(pl.Int32), pl.col("gwin").cast(pl.Int32))
    cf = B.carry_forward(ps.select("gwin", "agent", "project_id"), wins, "project_id", B.CARRY)
    lab, agents = X.matrix(cf, "project_id", remap, len(day))
    # agreement with the round-1 (H11-imported) labels on windows labelled in both (ids differ; compare partitions)
    lab0, ag0 = X.matrix(art_h11, "project_id", remap, len(day), agents)
    both = (lab >= 0) & (lab0 >= 0)
    # partition agreement: same-project pairs within a window
    agree = tot = 0
    for t in range(lab.shape[0]):
        idx = np.flatnonzero(both[t])
        for i in range(len(idx)):
            for j in range(i + 1, len(idx)):
                a = lab[t, idx[i]] == lab[t, idx[j]]
                b = lab0[t, idx[i]] == lab0[t, idx[j]]
                agree += a == b
                tot += 1
    bank = M.Bank(lab >= 0, day, seed=M._seed(scope, "art_shared"))
    res = X.analyse_labelset(f"{scope}/art_shared", lab, day, bank, extra=True)
    r0 = json.loads((X.DATA / scope / f"round1_{scope}.json").read_text())["sets"]["art"]
    out = {"scope": scope, "labelled_aw_shared": int((lab >= 0).sum()), "labelled_aw_round1": int((lab0 >= 0).sum()),
           "pair_agreement": agree / tot if tot else None, "n_pairs": tot}
    for nm, s in (("round1", r0), ("shared", res)):
        out[nm] = {"testable": s.get("testable")}
        if s.get("testable"):
            out[nm].update({"LLR_NH": s["LLR_NH"], "LLR_NC": s["LLR_NC"], "best": s["best_model"], "lam": s["obs"]["lam"],
                            "beta": s["obs"]["beta"], "single": s["obs"]["single"], "copyfrac": s["copyfrac"],
                            "mu_ncd": s["fits"]["ncd"]["mu"], "ppcj_ncd": s["fits"]["ncd"]["ppc_joint"],
                            "verdict": X.verdict_simple(s), "P2": X.p2(s), "P3": X.p3(s),
                            "lam_ncd": s["fits"]["ncd"]["pred"]["lam"], "beta_hub": s["fits"]["hubbell"]["pred"]["beta"]})
    print(json.dumps(out, default=float), flush=True)
    return out


def main():
    with get_context("spawn").Pool(2) as pool:
        res = pool.map(run, list(SCOPES), chunksize=1)
    (X.DATA / "robust_shared_labels.json").write_text(json.dumps({r["scope"]: r for r in res}, indent=1, default=float))


if __name__ == "__main__":
    main()
