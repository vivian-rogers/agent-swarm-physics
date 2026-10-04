"""H129 confirmatory run on the LOCKED HOLDOUT. Written and frozen 2026-10-04 after exploratory round 1. NOT RUN.

Targets (shared-goal code from goal TITLES only): #45 Follow your leader, #46 Organise an event, #47 Reduce global
suffering as much as you can; both channels (work host labels, attention project labels), whole periods. #50 (Compete to
be the best AI Assistant: own-role from the title) is reported, not scored. Ages from the first appearance in ALL data
(held-out rows included only here). Estimators identical to round 1 (`analysis/run.py: analyse`): per-agent reversal null
(2,000), detailed-balance null, age walker W1* calibrated to m_2 and the return share (400 runs), dwell hazard.

Frozen predictions (round 1: HH370's circulation absent; age drift small but consistent; dwell hazards age):
  C1 (no circulation beyond age): A_cyc above both the reversal null and W1*'s 95th percentile (p < 0.05 each) in at
     most 1 of the testable target unit-channels (round 1: 0/9 shared).                                     [0.80]
  C2 (excess, sign): m_2 > 0 in >= 2/3 of the testable target unit-channels (round 1: 30/37 positive).       [0.70]
  C3 (aging dwell, not geometric): dwell slope gamma < 0 with 95% CI < 0 in >= 2/3 of the testable target
     unit-channels (round 1: 32/39).                                                                         [0.80]
  C0 (HH370's literal kill repeats): A_3 reversal-null p >= 0.05 in >= 1/2 of the testable target unit-channels
     (round 1: 6/9).                                                                                         [0.55]
Reading: C1 + C3 confirm "project hopping carries no circulation beyond age drift, and dwell is not geometric".

Reuse policy (hypotheses/holdout.md): #45-#47 project choice is planned by H93 (project_potts), H75/H77/H78/H94/H95
(artifact_lineage, other). H129's statistic (within-agent hop-sequence irreversibility) is new; disclose in the card
and LOG.md before running. #47: H95's agent read #47 setup lines (disclosed in holdout.md item 30).

Guards: needs BOTH --confirm and H129_CONFIRM=1; refuses unless the sha256 of h129lib.py, run.py and this file match
analysis/confirm.sha256; calls holdout_ledger.check() per target. --dry-run runs the identical pipeline on non-holdout
stand-ins (#31, #38, #44; own-role stand-in #42), asserts that no held-out day is loaded, and writes to
data/processed/H129-project-cycle-currents/confirm_dryrun/.

Usage:
  uv run python hypotheses/H129-project-cycle-currents/analysis/confirm.py --dry-run
  H129_CONFIRM=1 uv run python hypotheses/H129-project-cycle-currents/analysis/confirm.py --confirm
  uv run python hypotheses/H129-project-cycle-currents/analysis/confirm.py --freeze
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import zlib
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h129lib as L  # noqa: E402
import run as R  # noqa: E402

FROZEN_FILES = [HERE / "h129lib.py", HERE / "run.py", Path(__file__).resolve()]
SHA_FILE = HERE / "confirm.sha256"
TARGETS = {45: "shared", 46: "shared", 47: "shared", 50: "report"}
STANDINS = {31: "shared", 38: "shared", 44: "shared", 42: "report"}


def digest() -> dict:
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in FROZEN_FILES}


def evaluate(codes: dict, allow: bool) -> dict:
    out = {}
    for g, code in codes.items():
        if not allow:
            days = L.RH.period_days(g)
            assert not L.RH.calendar().filter(pl.col("pt_date").is_in(days))["ho"].any(), "held-out day in a dry run"
        for ch in ("work", "attention"):
            d = L.work_hops(g, allow) if ch == "work" else L.attention_hops(g, allow)
            age = L.work_age(allow) if ch == "work" else L.attention_age(allow)
            h, v = d["hops"], d["visits"]
            if h.height < 3:
                out[f"G{g}|{ch}"] = {"code": code, "n_hops": h.height, "testable_tri": False}
                continue
            rank = L.rank_of(age, set(h["src"].to_list()) | set(h["dst"].to_list()) | set(v["repo"].to_list()))
            h = h.with_columns(pl.col("src").replace_strict(rank, return_dtype=pl.Int32).alias("src_rank"),
                               pl.col("dst").replace_strict(rank, return_dtype=pl.Int32).alias("dst_rank"))
            rng = np.random.default_rng(zlib.crc32(f"confirm|{g}|{ch}".encode()))
            r = R.analyse(g, ch, f"G{g}", h, v, 400, rng)
            r["code"] = code
            out[f"G{g}|{ch}"] = r
    return out


def score(res: dict) -> dict:
    sh = {k: r for k, r in res.items() if r.get("code") == "shared"}
    tri = [k for k, r in sh.items() if r.get("testable_tri")]
    c1 = [k for k in tri if sh[k]["p_flip"]["Acyc"] < 0.05 and sh[k].get("p_ref", {}).get("Acyc", 1) < 0.05]
    t4 = [k for k, r in sh.items() if r.get("testable_tri") or r.get("testable_curl")]
    c2 = [k for k in t4 if sh[k]["m2"] > 0]
    dw = [k for k, r in sh.items() if isinstance(r.get("dwell"), dict) and r["dwell"].get("testable")]
    c3 = [k for k in dw if sh[k]["dwell"]["gamma_ci"][1] < 0]
    c0 = [k for k in tri if sh[k]["p_flip"]["A3"] >= 0.05]
    nt = lambda n: "not testable" if n == 0 else None  # noqa: E731
    return {"C1": nt(len(tri)) or (len(c1) <= 1), "C1_units": c1, "testable_tri": tri,
            "C2": nt(len(t4)) or (len(c2) >= 2 / 3 * len(t4)), "C2_positive": c2, "testable_m2": t4,
            "C3": nt(len(dw)) or (len(c3) >= 2 / 3 * len(dw)), "C3_aging": c3, "testable_dwell": dw,
            "C0": nt(len(tri)) or (len(c0) >= 0.5 * len(tri)), "C0_inside_null": c0}


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
        if os.environ.get("H129_CONFIRM") != "1":
            sys.exit("refused: set H129_CONFIRM=1 (Vivian's sign-off) to touch the locked holdout")
        sys.path.insert(0, str(L.ROOT / "infra/shared"))
        import holdout_ledger as HL
        for g in TARGETS:
            chk = HL.check("H129", f"G{g}", "work", ["entropy_production", "project_potts"])
            if not chk["allowed"]:
                sys.exit(f"refused by the holdout ledger for G{g}: {chk}")
            if chk["needs_disclosure"]:
                print(f"disclosure needed for G{g}:", sorted({u["hypothesis"] for u in chk["competing_planned"] + chk["prior_runs"]}))
        codes, allow, out = TARGETS, True, L.D / "confirm"
    else:
        codes, allow, out = STANDINS, False, L.D / "confirm_dryrun"
    out.mkdir(parents=True, exist_ok=True)
    res = evaluate(codes, allow)
    sc = score(res)
    tag = "confirm" if a.confirm else "dryrun"
    dflt = lambda o: o.item() if isinstance(o, np.generic) else str(o)  # noqa: E731
    (out / f"{tag}.json").write_text(json.dumps({"units": res, "score": sc}, indent=1, default=dflt))
    print(json.dumps(sc, indent=1, default=dflt))


if __name__ == "__main__":
    main()
