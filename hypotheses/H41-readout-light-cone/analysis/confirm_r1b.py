"""H41 confirmatory test on the LOCKED HOLDOUT, RE-FROZEN WITH TWO PIPELINE FIXES (written 2026-10-04). NOT RUN.

Re-freeze of `confirm.py` (left byte-for-byte untouched), written before any holdout use. H41 already ran on the
corrected inputs (context ledger, DQ2, statement_flags; no activity bins, embeddings, work, failures or nudges), so the
inputs do not change. Two bugs are fixed (details and evidence in `CONFIRM_R1B.md`):
  1. ROOM INDEX (new finding, 2026-10-04). `scheme/h41core.load_skeleton` keeps `rooms_timeline` rows with
     `te >= t_min - 1 day`; open segments (t_end null) fail that comparison and are dropped, so `RoomIndex.at` falls back
     to an agent's previous room. On non-holdout #51 windows 61% (07-06..07-24) and 70% (08-24..09-05) of sampled
     room lookups for agents in the table are stale (mostly #general read as an old onboarding room or #focus); #38 5%;
     #42 0%. This script re-sets `sk.rooms` to the window's rows INCLUDING open segments before any statistic, so
     room0 / room_t0 / cross-room labels (C2, C3) and the isolation check use the true rooms.
  2. C4 ISOLATION (holdout.md ledger item 16). `confirm.isolation` tested isolation only at the use time, against the
     stale room index and against `sk.agents` only, and flagged 671 "isolated" adoptions in the T4 stand-in with only 3
     acausal. C4-r1b uses the card's definition: the adopter sat in non-#general rooms only, with no other roster agent
     (Claude Code excluded) in any of its rooms at any time in [t0, t_use], and never in the item's first room.

  uv run python hypotheses/H41-readout-light-cone/analysis/confirm_r1b.py --dry-run           # stand-ins (non-holdout)
  uv run python hypotheses/H41-readout-light-cone/analysis/confirm_r1b.py --confirm --i-understand-this-uses-the-locked-holdout

Targets (unchanged): T1 #51 tail (primary), T2 #47 (two rooms), T3 #28 (regime I), T4 #46-#50 onboarding / isolation
rooms. Stand-ins: T1 #51 08-24 -> 09-04, T2 #42, T3 #30, T4 #51 07-06 -> 07-23.
The frozen predictions are hashed (SHA-256) into confirm/sealed_r1b_<mode>.json before any held-out text is read;
held-out chat text is read in memory only (H34's marker rule) and never written. The confirm path refuses unless the H41
folder is committed and clean and infra/shared/holdout_ledger.check() reports no same-family prior run of the same
modality on a target (H41 has no ledger entries yet; it is checked as message-content / cascade).

Reuse disclosure (unchanged): the #51 tail is also targeted by the unrun scripts of H14, H18, H20, H22, H29, H30, H34,
H39; #28 by H10, H32, H34, H36; #46-#50 by H04 (run, activity timing), S3, H26, H30, H35, H36, H38, H39.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
os.environ.setdefault("OMP_NUM_THREADS", "2")
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import confirm as C0  # noqa: E402  (round-1 frozen pipeline: markers_for, stats_for, TARGETS)

C, BLD, S = C0.C, C0.BLD, C0.S
ROOT = C0.ROOT
OUTD = C.OUT / "confirm"
HYP = "H41"
LEDGER_T = {"T1": ["#51-tail"], "T2": ["G47"], "T3": ["G28"], "T4": ["G46", "G47", "G48", "G49", "G50"]}

FROZEN = {
    "written": "2026-10-04 re-freeze (round-1 rule, room index fixed, C4 fixed), before any holdout use",
    "C1_gating_matched": "delay-matched J_mh (in-flight vs first post-entry talk call, MH over delay-since-t0 bins) has "
                         "day-bootstrap lower CI > 1 in T1, and in at least 2 of {T1, T2, T3} (unchanged)",
    "C2_within_room_cone": "robust acausal share among within-room adoptions <= 0.03 in T1, T2 and T3 (unchanged rule; "
                           "rooms from the full rooms_timeline including open segments)",
    "C3_cage": "T2: >= 0.60 of cross-room adoptions outside the logged cone AND cross/within adoption hazard per talk call "
               "(2 h) <= 0.20 (unchanged rule; rooms fixed)",
    "C4_r1b_isolation": "T4: every adoption by an agent isolated since t0 (only non-#general rooms, no other roster agent "
                        "in any of them during [t0, t_use], never in the item's first room) is outside the logged cone; "
                        "counts reported; the check passes vacuously if there are none",
    "C5_unmatched_report": "pre-registered unmatched J_in is reported; no criterion",
    "C6_velocity_talk": "median talk calls per hop <= 3 in T1 and T2 (unchanged)",
    "supported_if": "C1 and C2 pass; the cage claim is confirmed if C3 passes; C4-r1b is a pipeline check (a failure "
                    "voids the run's cone labels rather than refuting the claim)",
}


def full_rooms() -> pl.DataFrame:
    return pl.read_parquet(C.SH / "rooms_timeline.parquet").with_columns(C.ts("t_start").alias("ts"), C.ts("t_end").alias("te"))


def fix_rooms(sk, rt: pl.DataFrame):
    """Fix 1: the skeleton's room rows for its window, keeping open segments (te null)."""
    sk.rooms = rt.filter((pl.col("te").is_null() | (pl.col("te") >= sk.t_min - 86400)) & (pl.col("ts") <= sk.t_max + 86400))
    return sk


def seal(mode: str) -> str:
    OUTD.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha256(json.dumps(FROZEN, sort_keys=True).encode()).hexdigest()
    (OUTD / f"sealed_r1b_{mode}.json").write_text(json.dumps({"sha256": h, "frozen": FROZEN,
                                                              "sealed_at": dt.datetime.now(dt.timezone.utc).isoformat()}, indent=1))
    return h


def run_target(spec: dict, include_holdout: bool, rt: pl.DataFrame):
    cal = C.calendar()
    goals = spec.get("goals", [spec.get("goal")])
    out = []
    for g in goals:
        df = None
        if spec.get("days"):
            a, b = spec["days"]
            df = lambda d, a=a, b=b: a <= d < b  # noqa: E731
        sk = C.load_skeleton(g, cal, days_filter=df, include_holdout=include_holdout)
        if len(sk.c_t) == 0:
            continue
        fix_rooms(sk, rt)
        u, nov = C0.markers_for(sk, sk.t_min)
        ri = C.RoomIndex(sk)
        items, adf, hz, _ = BLD.analyze(sk, u, nov, cal, ri)
        out.append((g, sk, adf, hz, ri))
    return out


def isolation_r1b(parts, rt: pl.DataFrame) -> dict:
    """Fix 2: adoptions by agents isolated since t0 (card definition), and how many are outside the logged cone."""
    cc = set(int(x) for x in C.cc_agents())
    rows = rt.select("agent", "room", "ts", pl.col("te").fill_null(np.inf)).filter(~pl.col("agent").is_in(list(cc)))
    by_agent, by_room = {}, {}
    for a, r, s, e in rows.iter_rows():
        by_agent.setdefault(int(a), []).append((float(s), float(e), int(r)))
        by_room.setdefault(int(r), []).append((int(a), float(s), float(e)))
    for v in by_agent.values():
        v.sort()
    n = acaus = 0
    rooms_used = set()
    for g, sk, adf, hz, ri in parts:
        if adf.height == 0:
            continue
        for a, t, t0, r0, ic in zip(adf["agent"].to_list(), adf["t_use"].to_list(), adf["t0"].to_list(),
                                    adf["room0"].to_list(), adf["in_cone"].to_list()):
            a = int(a)
            if t0 < C.ROOMS_START or a in cc:
                continue
            segs = [(max(s, t0), min(e, t), r) for s, e, r in by_agent.get(a, []) if s <= t and e >= t0]
            if not segs or min(s for s, _, _ in by_agent[a] if s <= t) > t0:
                continue                      # room unknown for part of [t0, t_use]
            if any(r == 0 for _, _, r in segs) or any(r == r0 for _, _, r in segs):
                continue                      # in #general or in the item's first room during the interval
            alone = all(not (b != a and bs <= e and be >= s) for s, e, r in segs for b, bs, be in by_room.get(r, []))
            if alone:
                n += 1
                acaus += int(not ic)
                rooms_used.update(r for _, _, r in segs)
    return dict(n_isolated=n, n_isolated_acausal=acaus, isolated_rooms=sorted(rooms_used))


def ledger_gate(strict: bool) -> list[str]:
    sys.path.insert(0, str(ROOT))
    from infra.shared import holdout_ledger as hl
    bad = []
    for tn, ts_ in LEDGER_T.items():
        for t in ts_:
            r = hl.check(HYP, t, "message content", ["cascade", "dilution_addressing"])
            same = sorted({u["hypothesis"] for u in r["prior_runs_same_family"] if u["modality"] == "message content"})
            print(f"ledger {tn} {t}: allowed={r['allowed']} same_family_same_modality_runs={same} "
                  f"prior_runs={sorted({u['hypothesis'] for u in r['prior_runs']})}", flush=True)
            if same:
                bad.append(f"{t}: {same}")
    return bad if strict else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--out", type=Path, default=None, help="dry-run result file (default confirm/result_r1b_dry.json)")
    a = ap.parse_args()
    if a.confirm and not a.ack:
        sys.exit("refusing: --confirm needs --i-understand-this-uses-the-locked-holdout")
    if not a.confirm and not a.dry_run:
        sys.exit("choose --dry-run (stand-ins) or --confirm --i-understand-this-uses-the-locked-holdout")
    mode = "confirm" if a.confirm else "dry"
    if a.confirm:
        dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--", "hypotheses/H41-readout-light-cone"],
                               capture_output=True, text=True).stdout.strip()
        if dirty:
            sys.exit("refusing: commit the H41 card, confirm_r1b.py and CONFIRM_R1B.md before the holdout run")
    bad = ledger_gate(strict=a.confirm)
    if bad:
        sys.exit("refusing (holdout ledger): " + "; ".join(bad))
    h = seal(mode)
    print("sealed predictions sha256", h, flush=True)
    rt = full_rooms()
    res = {"mode": mode, "sha256": h}
    for tname, spec in C0.TARGETS[mode].items():
        parts = run_target(spec, include_holdout=(mode == "confirm"), rt=rt)
        r, adf = C0.stats_for(parts)
        if tname == "T4":
            r.update(isolation_r1b(parts, rt))
            if mode == "dry":     # transparency: the round-1 check on the same parts (now with fixed rooms)
                r["round1_isolation_check_fixed_rooms"] = C0.isolation(parts)
        res[tname] = r
        print(tname, json.dumps(r, default=str)[:600], flush=True)
    t1, t2, t3, t4 = (res.get(k, {}) for k in ("T1", "T2", "T3", "T4"))
    lo = lambda r: (r.get("J_mh_ci") or (np.nan, np.nan))[0]  # noqa: E731
    c1 = bool(lo(t1) > 1 and sum(lo(r) > 1 for r in (t1, t2, t3)) >= 2)
    c2 = all((r.get("acaus_rob_within") is not None and r["acaus_rob_within"] <= 0.03) for r in (t1, t2, t3))
    c3 = bool((t2.get("acaus_rob_cross") or 0) >= 0.60 and (t2.get("cage_ratio") or np.inf) <= 0.20)
    c4 = bool(t4.get("n_isolated", 0) == t4.get("n_isolated_acausal", -1))
    c6 = all((r.get("velocity", {}).get("talk_med") or 99) <= 3 for r in (t1, t2))
    res["checks"] = dict(C1=c1, C2=c2, C3=c3, C4_r1b=c4, C6=c6)
    res["supported"] = bool(c1 and c2)
    res["cage_confirmed"] = c3
    res["pipeline_ok"] = c4
    dest = (OUTD / "result_r1b_confirm.json") if a.confirm else (a.out or OUTD / "result_r1b_dry.json")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(res, indent=1, default=lambda o: float(o) if isinstance(o, (np.floating, np.integer)) else str(o)))
    print(json.dumps(res["checks"]), "supported" if res["supported"] else "not supported")


if __name__ == "__main__":
    main()
