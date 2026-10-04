"""H65 confirmatory test on the LOCKED HOLDOUT. Written and frozen 2026-10-04 after exploratory round 1; NOT RUN.

Refuses to touch held-out data without:  --confirm --i-understand-this-uses-the-locked-holdout
and refuses if the H65 folder has uncommitted changes. Default --dry-run uses non-holdout stand-ins, same code path.

Targets (reuse policy hypotheses/holdout.md; holdout_ledger.check() printed first):
  #45  "Follow your leader": the installed Fine-Tuned Leader (agent 30; DQ6 leader rows, preferred). Its window starts
       no earlier than 2026-06-01 17:15:40 UTC (DQ6: the first ~11 min ran a wrong model string).
       Reuse: #45 activity timing was run by H02 and H04; H23 plans #45 content. H65's statistic (read-gated
       inflow/outflow percentiles and reply rates of the leader) has not been computed on #45 by anyone.
  #28  replication point (mode C, regime I, 10 agents) for the attention alignment D_p.
Stand-ins for --dry-run: #45 -> #44 (agent 28, from 2026-05-26 19:15:47 UTC, all rooms); #28 -> #27.

Frozen predictions (exploration in brackets; bge-small primary):
  C1 (primary): the #45 leader is NOT a router: router index below the 90th percentile of its own skeleton null
     (40 synthetic null replicates on the #45 skeleton; no outcome data used for the null). [0 router calls in 4
     natives under bge]. Credence 0.8.
  C2: the #45 leader's reply-in rate RI is at or above the median agent (pct RI >= 0.5). [#26 0.89; #35 +0.39 and
     #12 judges +0.45 replies per statement]. Credence 0.6.
  C3: #28 attention alignment D_p has a block-bootstrap CI that includes 0. [40 units: median -0.04; CI excludes 0
     in 4/40]. Credence 0.75.
  C4: #28 rho(reply-out share, inflow chi) > 0. [36/46 units > 0, median 0.29]. Credence 0.75.
  C5: #28 median unread/read response ratio lambda/chi in [0.4, 0.8]. [median 0.61 over 46 units]. Credence 0.7.
  Decision: 'leaders are attention hubs, not content routers' confirmed if C1 and C2 pass; 'answering is absorbing
  and attention is unaligned with content flow' confirmed if C3 and C4 pass.
Output: data/processed/H65-leaders-are-routers/confirm/{results,dryrun}.json.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h65lib as L  # noqa: E402
import run as RUN  # noqa: E402

ROOT = L.ROOT
OUT = ROOT / "data/processed/H65-leaders-are-routers/confirm"
UTC = dt.timezone.utc
FLAG = "--i-understand-this-uses-the-locked-holdout"
G45_FIX = dt.datetime(2026, 6, 1, 17, 15, 40, tzinfo=UTC)


def guard(confirm: bool):
    if not confirm:
        return
    if FLAG not in sys.argv:
        raise SystemExit(f"refusing: add {FLAG}")
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "hypotheses/H65-leaders-are-routers"],
                           capture_output=True, text=True).stdout.strip()
    if dirty:
        raise SystemExit("refusing: commit the H65 folder (card + this script) before a confirmatory run")


def ledger():
    sys.path.insert(0, str(ROOT / "infra/shared"))
    import holdout_ledger as HL
    out = {}
    for tgt, fam in (("G45", ["content_transfer"]), ("G28", ["content_transfer"])):
        r = HL.check("H65", tgt, "message content", fam)
        out[tgt] = {"allowed": r["allowed"], "needs_disclosure": r["needs_disclosure"],
                    "prior_runs": [u["hypothesis"] for u in r["prior_runs"]],
                    "competing_planned": sorted({u["hypothesis"] for u in r["competing_planned"]})}
    return out


def build(goal: int, confirm: bool):
    if confirm:
        import build as B
        B.ALLOW_HOLDOUT = True
        B.build(goal)
        L.DATA = ROOT / "data/processed/H65-leaders-are-routers/confirm_build"


def leader_window(confirm: bool):
    if not confirm:
        return 44, 28, RUN.G44_START, None
    gt = pl.read_parquet(ROOT / "data/processed/shared/ground_truth_labels.parquet").filter(
        pl.col("preferred") & (pl.col("goal_no") == 45) & (pl.col("label_kind") == "leader"))
    a = int(gt["agent"][0])
    t0 = max(gt["t_valid_from"].min(), G45_FIX)
    return 45, a, t0, gt["t_valid_to"].max()


def c12(confirm: bool, reps: int = 40):
    import synthetic as S
    goal, leader, t0, t1 = leader_window(confirm)
    build(goal, confirm)
    tg, rd, Zs, pos, Hm, hpos, regime, block = RUN.load_period(goal, "bge_small")
    D = L.build_design(tg, rd, Zs, pos, Hm, hpos)
    Gr = L.build_grams(D)
    w = RUN.window_weights(Gr, t0, t1)
    r = RUN.leader_pct(Gr, w, leader, B=100, min_n=15, min_exp=15)
    tg = tg.sort("tgt")
    tt = tg["t"]
    lead = (tg["agent"].to_numpy() == leader) & (tt >= t0).to_numpy() & ((tt < t1).to_numpy() if t1 else True)
    nulls = []
    rng = np.random.default_rng(45)
    for _ in range(reps):
        Z, Hs, hp = S.synth_vectors(tg, rd, pos, len(Zs), lead, 1.0, 1.0, rng)
        Dn = L.build_design(tg, rd, Z, pos, Hs, hp)
        rn = RUN.leader_pct(L.build_grams(Dn), w, leader, B=5, min_n=15, min_exp=15)
        nulls.append(rn["router_index"])
    nulls = np.array(nulls, float)
    nulls = nulls[np.isfinite(nulls)]
    q90 = float(np.quantile(nulls, 0.9)) if len(nulls) else np.nan
    r.pop("agents", None)
    return {"goal": goal, "leader": leader, **r, "null_ri_q90": q90, "null_n": int(len(nulls)),
            "C1_pass": bool(not (np.isfinite(r["router_index"]) and r["router_index"] > q90)),
            "C2_pass": bool(np.isfinite(r["pct_RI"]) and r["pct_RI"] >= 0.5)}


def c345(confirm: bool):
    goal = 28 if confirm else 27
    build(goal, confirm)
    st, E = RUN.replication_job((goal, None, "bge_small", 100))
    lam = st["lam_over_chi_median"]
    return {"goal": goal, **{k: st[k] for k in ("D", "D_ci", "rho_RO_chi", "lam_over_chi_median", "n_agents")},
            "C3_pass": bool(st["D_ci"][0] is not None and st["D_ci"][0] <= 0 <= st["D_ci"][1]),
            "C4_pass": bool(np.isfinite(st["rho_RO_chi"]) and st["rho_RO_chi"] > 0),
            "C5_pass": bool(np.isfinite(lam) and 0.4 <= lam <= 0.8)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument(FLAG, action="store_true", dest="ack")
    ap.add_argument("--null-reps", type=int, default=40)
    a = ap.parse_args()
    guard(a.confirm)
    res = {"mode": "confirm" if a.confirm else "dryrun", "ledger": ledger(), "run_at": dt.datetime.now(UTC).isoformat()}
    res["C1_C2"] = c12(a.confirm, a.null_reps)
    res["C3_C5"] = c345(a.confirm)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / ("results.json" if a.confirm else "dryrun.json")).write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps({k: v for d in (res["C1_C2"], res["C3_C5"]) for k, v in d.items() if k.endswith("_pass")}))


if __name__ == "__main__":
    main()
