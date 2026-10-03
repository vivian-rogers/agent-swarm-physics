"""H02 confirmatory test on the locked holdout: does the Fine-Tuned Leader (#45) top the net-outgoing-influence ranking?

*** DO NOT RUN on #45 until the H02 card's predictions and this file's FROZEN settings are final. ***
Written 2026-10-03, during exploratory round 1. Not run.

Pre-registered decision rule (card, "Prediction", #45):
  PASS if the Fine-Tuned Leader (roster agent 30) is ranked #1 of the present population by net outgoing influence
       I_k = sum_j (J_jk - J_kj) from the primary estimator, AND its z-score against the N1 (30-min block circular
       shift) surrogate distribution of I_k is >= 2.
  FAIL otherwise. If the leader fails the present-population rule (row on every day and >= 30 active bins), the
  result is FAIL (not identifiable), reported as such.
Secondary (reported, not decisive): KI-5 estimator; #best-room subset; EQ-PL hub rank (rival model);
the leader's rank by z(I_k); talk spin (state == 4, agents with >= 30 talk bins; added 2026-10-03 after exploratory
round 1, before any holdout data was read); held-out mean-field test (leave-one-day-out dLL of M2 and M3 over M1
vs 20 N1 surrogates; exploratory round 1 found z21 >= 2 in 3/5 regime-III mode-C chunks, so the card predicts
z21 >= 2 for #45).

Usage:
  dry run on a non-holdout goal (allowed during exploration):
      uv run python confirm_45.py --dry-run-goal 26 --leader 17
  confirmation (holdout; only when the project unlocks #45 for H02):
      uv run python confirm_45.py --confirm-holdout
"""
from __future__ import annotations

import os
os.environ["VECLIB_MAXIMUM_THREADS"] = "2"; os.environ["OMP_NUM_THREADS"] = "2"
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h02lib as L  # noqa: E402
import mf  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
SHARED = ROOT / "data/processed/shared"
DATA = ROOT / "data/processed/H02-couplings-are-real"
HOLDOUT = json.loads((ROOT / "hypotheses/holdout.json").read_text())

# ---------------------------------------------------------------- FROZEN settings (do not edit after unlocking)
FROZEN = {
    "goal": 45,
    "leader_agent": 30,              # roster: "Fine-Tuned Leader", Fine-tuned (Kimi), 2026-06-01 -> 2026-06-08
    "spin": "+1 if activity_bins.state >= 3 else -1",
    "bin": "1 min (activity_bins)",
    "population": "row on every day of the goal period and >= 30 active bins",
    "primary_estimator": "KI-1 block",    # set from exploratory round 1 (see card Results); alternatives: "KI-5 block"
    "secondary_estimators": ["KI-5 block", "KI-1 naive", "EQ-PL block"],
    "lambda_J": L.LAM_J, "lambda_D": L.LAM_D, "block_min": L.BLOCK_MIN,
    "null": "N1: independent circular shift of each agent within each (day, 30-min block)",
    "n_surrogates": 200,
    "seed": 20261003,
    "pass_rule": "leader rank by I_k == 1 AND z(I_k) vs N1 >= 2",
    "secondary_talk_spin": "state == 4; population: >= 30 talk bins and present every day",
    "secondary_meanfield": {"surrogates": 20, "prediction": "z21 >= 2 (regime III, mode C)"},
    "secondary_H02MF": {"leader_follower_surrogates": 50, "cw_surrogates": 100,
                        "prediction_MF_P6": "leader has the largest A = J_lf - J_fl of all agents and z_A >= 2",
                        "note": "H02-MF (HH80 Curie-Weiss, HH83 leader-follower), added 2026-10-03 before any holdout read"},
}


def load_goal(goal, allow_holdout, spin="active"):
    cal = pl.read_parquet(SHARED / "calendar.parquet").filter(pl.col("goal_no") == goal).sort("pt_date")
    if cal["holdout"].any() and not allow_holdout:
        sys.exit(f"goal {goal} is in the locked holdout; refusing without --confirm-holdout")
    if not cal["holdout"].any() and goal in HOLDOUT["goal_periods_held_out"]:
        sys.exit("calendar and holdout.json disagree; stop and check")
    days = cal["pt_date"].to_list()
    ab = (pl.scan_parquet(SHARED / "activity_bins.parquet").filter(pl.col("pt_date").is_in(days))
          .select("pt_date", "minute", "agent", "state").collect())
    nd = len(days)
    thr = 3 if spin == "active" else 4
    pres = (ab.group_by("agent").agg(pl.col("pt_date").n_unique().alias("nd"), (pl.col("state") >= thr).sum().alias("nact"))
            .filter((pl.col("nd") == nd) & (pl.col("nact") >= 30)))
    agents = sorted(pres["agent"].to_list())
    ab = ab.filter(pl.col("agent").is_in(agents)).with_columns(
        pl.col("pt_date").replace_strict({d: i for i, d in enumerate(days)}, return_dtype=pl.Int32).alias("day"),
        pl.when(pl.col("state") >= thr).then(1).otherwise(-1).cast(pl.Int8).alias("s"))
    piv = ab.pivot(on="agent", index=["day", "minute"], values="s").sort("day", "minute")
    S = piv.select([str(a) for a in agents]).to_numpy().astype(np.int8)
    return S, piv["day"].to_numpy(), piv["minute"].to_numpy(), agents, days


def best_room_agents(days, agents):
    """Agents seen in the #best room during the period (rooms_timeline + rooms names)."""
    try:
        rooms = pl.read_parquet(SHARED / "rooms.parquet")
        rtl = pl.read_parquet(SHARED / "rooms_timeline.parquet")
    except Exception:
        return None
    best = rooms.filter(pl.col("name") == "best")["room"].to_list()
    lo = dt.datetime.fromisoformat(days[0] + "T00:00:00+00:00")
    hi = dt.datetime.fromisoformat(days[-1] + "T23:59:59+00:00") + dt.timedelta(days=1)
    rtl = rtl.with_columns(pl.coalesce("t_end", "t_last").alias("t_stop"))
    rtl = rtl.filter(pl.col("room").is_in(best) & (pl.col("t_start") < hi) & (pl.col("t_stop") > lo))
    sel = sorted(set(rtl["agent"].to_list()) & set(agents))
    return sel or None


def estimator(name, S, day, minute):
    if name == "KI-1 block":
        return L.fit_kinetic(S, day, minute, "block", "1")[0]
    if name == "KI-5 block":
        return L.fit_kinetic(S, day, minute, "block", "box", 5)[0]
    if name == "KI-1 naive":
        return L.fit_kinetic(S, day, minute, "none", "1")[0]
    if name == "EQ-PL block":
        return L.fit_equal(S, day, minute, "block")[1]
    raise ValueError(name)


def influence_test(S, day, minute, agents, leader, name, B, rng):
    J = estimator(name, S, day, minute)
    segs = L.segments(day, minute, "block")
    stat = L.hub_strength if name.startswith("EQ") else L.net_influence
    nul = np.array([stat(estimator(name, L.circular_shift(S, segs, rng), day, minute)) for _ in range(B)])
    I = stat(J)
    z = (I - nul.mean(0)) / nul.std(0)
    k = agents.index(leader)
    table = sorted([{"agent": a, "I": float(I[i]), "z": float(z[i]), "act": float((S[:, i] > 0).mean())}
                    for i, a in enumerate(agents)], key=lambda r: -r["I"])
    return {"estimator": name, "N": len(agents), "leader_rank": L.rank_of(I, k), "leader_I": float(I[k]),
            "leader_z": float(z[k]), "leader_rank_by_z": L.rank_of(z, k),
            "pass": bool(L.rank_of(I, k) == 1 and z[k] >= 2), "ranking": table}


def meanfield_test(S, day, minute, agents, K, rng):
    """Held-out dLL (M3 - M1, M2 - M1) per bin vs K N1 surrogates (exploratory round 1 statistic)."""
    roster = pl.read_parquet(SHARED / "roster.parquet")
    labs = dict(zip(roster["agent"].to_list(), roster["lab"].to_list()))
    lab_arr = np.array([labs[a] for a in agents])

    def stat(X):
        ho = L.heldout(X, day, minute, lab_arr)
        T = sum(r["T"] for r in ho)
        return sum(r["M3"] - r["M1"] for r in ho) / T, sum(r["M2"] - r["M1"] for r in ho) / T

    r31, r21 = stat(S)
    segs = L.segments(day, minute, "block")
    nul = np.array([stat(L.circular_shift(S, segs, rng)) for _ in range(K)])
    return {"d31": r31, "z31": float((r31 - nul[:, 0].mean()) / nul[:, 0].std()),
            "d21": r21, "z21": float((r21 - nul[:, 1].mean()) / nul[:, 1].std()),
            "p21": float((1 + (nul[:, 1] >= r21).sum()) / (K + 1))}


def mf_tests(S, day, minute, agents, leader, rng):
    """HH83 leader-follower mean field for the named leader + HH80 Curie-Weiss beta*J0, both vs N1 surrogates."""
    cfg = FROZEN["secondary_H02MF"]
    segs = L.segments(day, minute, "block")
    lf = mf.lf_all(S, day, minute)
    nl = np.array([mf.lf_all(L.circular_shift(S, segs, rng), day, minute) for _ in range(cfg["leader_follower_surrogates"])])
    A, An = lf[:, 1] - lf[:, 2], nl[:, :, 1] - nl[:, :, 2]
    zA = (A - An.mean(0)) / An.std(0)
    zlf = (lf[:, 1] - nl[:, :, 1].mean(0)) / nl[:, :, 1].std(0)
    k = agents.index(leader)
    cw = mf.cw_stats(S, day, minute)
    cwn = np.array([mf.cw_stats(L.circular_shift(S, segs, rng), day, minute)["bJ0"] for _ in range(cfg["cw_surrogates"])])
    return {"leader_J_lf": float(lf[k, 1]), "leader_J_fl": float(lf[k, 2]), "leader_A": float(A[k]),
            "leader_z_A": float(zA[k]), "leader_rank_A": L.rank_of(A, k), "leader_z_lf": float(zlf[k]),
            "leader_rank_lf": L.rank_of(lf[:, 1], k), "J_ff_median": float(np.median(lf[:, 0])),
            "pass_MF_P6": bool(L.rank_of(A, k) == 1 and zA[k] >= 2),
            "cw_bJ0": float(cw["bJ0"]), "cw_VR": float(cw["VR"]), "cw_z": float((cw["bJ0"] - cwn.mean()) / cwn.std())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm-holdout", action="store_true")
    ap.add_argument("--dry-run-goal", type=int)
    ap.add_argument("--leader", type=int)
    ap.add_argument("--surrogates", type=int, default=FROZEN["n_surrogates"])
    a = ap.parse_args()
    if a.confirm_holdout == (a.dry_run_goal is not None):
        sys.exit("choose exactly one of --confirm-holdout or --dry-run-goal G")
    if a.confirm_holdout:
        goal, leader, allow, tag = FROZEN["goal"], FROZEN["leader_agent"], True, "confirm_45"
    else:
        goal, leader, allow, tag = a.dry_run_goal, a.leader, False, f"dryrun_g{a.dry_run_goal:02d}"
        if goal in HOLDOUT["goal_periods_held_out"]:
            sys.exit("dry runs must use a non-holdout goal")
    S, day, minute, agents, days = load_goal(goal, allow)
    out = {"goal": goal, "leader": leader, "days": days, "agents": agents, "frozen": FROZEN,
           "run_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    rng = np.random.default_rng(FROZEN["seed"])
    if leader not in agents:
        out["primary"] = {"pass": False, "reason": "leader not in present population (not identifiable)"}
    else:
        out["primary"] = influence_test(S, day, minute, agents, leader, FROZEN["primary_estimator"], a.surrogates, rng)
        out["secondary"] = [influence_test(S, day, minute, agents, leader, e, a.surrogates, rng)
                            for e in FROZEN["secondary_estimators"] if e != FROZEN["primary_estimator"]]
        sub = best_room_agents(days, agents)
        if sub and leader in sub and len(sub) >= 3:
            idx = [agents.index(x) for x in sub]
            out["best_room"] = influence_test(S[:, idx], day, minute, sub, leader, FROZEN["primary_estimator"],
                                              a.surrogates, rng)
        out["meanfield"] = meanfield_test(S, day, minute, agents, FROZEN["secondary_meanfield"]["surrogates"], rng)
        out["H02MF"] = mf_tests(S, day, minute, agents, leader, rng)
    St, dt_, mt, at, _ = load_goal(goal, allow, spin="talk")
    if leader in at:
        out["talk_spin"] = influence_test(St, dt_, mt, at, leader, FROZEN["primary_estimator"], a.surrogates, rng)
    else:
        out["talk_spin"] = {"pass": False, "reason": "leader has < 30 talk bins or missing days"}
    (DATA / f"{tag}.json").write_text(json.dumps(out, indent=1))
    p = out["primary"]
    print(tag, "N", len(agents), "leader", leader, {k: p.get(k) for k in ("leader_rank", "leader_z", "pass", "reason")})


if __name__ == "__main__":
    main()
