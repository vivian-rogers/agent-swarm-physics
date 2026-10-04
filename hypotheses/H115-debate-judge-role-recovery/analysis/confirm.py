"""H115 confirmatory run on the LOCKED HOLDOUT. Written and frozen 2026-10-04 after round 1; NOT RUN.

Guard: held-out data are touched only with BOTH `--confirm` and H115_CONFIRM=1, only if
`holdout_ledger.check("H115", "G48", "talk timing", "kinetic_ising_couplings")` allows it, and only with `--focal`
(the focal agent of #48, supplied by the coordinator from the #48 goal record at run time; this script never reads
held-out text). Otherwise it refuses. `--dry-run` runs the identical pipeline on a non-holdout stand-in (goal #26,
2026-01-07, focal = agent 17, the elected leader), built from scratch into a scratch directory.

Target: NE37 / goal #48 (2026-06-22, one day, regime III): "the whole village redirected to help one agent".
Statistic (frozen = round 1): per-call talk spins on the ledger call clock; read-gated inputs (same room, since the
recipient's previous call); additive in/out kinetic Ising (lambda 4, A1) on the day's all-present trimmed calls;
agent x call-mode intercepts; the focal agent's normalized sink rank u_F = (rank - 1)/(n - 1) (0 = top sink).
Field-only skeleton null: 200 worlds on the real skeleton, J = 0, each agent's real talk rate per call mode.

Frozen predictions (round 1: the #26 elected leader is the top talk source in 4/6 windows, mean u_L 0.80 vs skeleton
0.55; judges lean sink-ward, mean u 0.38; #35 / #44 leaders null):
  C1  The focal agent is in the source half: u_F >= 0.5.
  C2  The focal agent's u_F exceeds the 90th percentile of its field-only skeleton-null distribution.
Reading: C1 + C2 confirm "an operator-designated focal agent is a read-gated talk source" (H115 R1 transfer).
C1 without C2 is "consistent, not beyond the field". C1 failing contradicts the leader-as-source reading.

Reuse policy (hypotheses/holdout.md): G48 was run by H04 (kick-response / Hawkes / Curie-Weiss families, activity
timing); planned users H01, H08, H09, H12, H15, H30, H33, H36, H38, H39 (none in the kinetic-Ising-coupling family).
H116's confirm plans a different statistic (the focal agent's out-coupling step across #47 -> #48) on the same
family: whichever runs second discloses. #45 was the first choice but is blocked: H02 ran the same family there.

Usage:
  uv run python hypotheses/H115-debate-judge-role-recovery/analysis/confirm.py --dry-run
  H115_CONFIRM=1 uv run python hypotheses/H115-debate-judge-role-recovery/analysis/confirm.py --confirm --focal <agent code>
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h115lib as L  # noqa: E402

CS = L.CS
sys.path.insert(0, str(L.ROOT / "infra/shared"))
SCRATCH = Path(os.environ.get("TMPDIR", "/tmp")) / "h115_confirm_dryrun"
OUT = L.DATA / "confirm"
FROZEN = dict(lam=4.0, C1_u=0.5, C2_q=0.90, skel_reps=200, min_calls=5)
TARGET = dict(goal=48, days=["2026-06-22"], ledger_target="G48")
STANDIN = dict(goal=26, days=["2026-01-07"], focal=17)

_S = {}


def build(goal, days, include_holdout):
    CS.ALLOW_HOLDOUT = bool(include_holdout)
    calls = CS.load_calls([goal], days=days, include_holdout=include_holdout)
    msgs = CS.load_messages([goal], days=days, include_holdout=include_holdout)
    agents = sorted(int(a) for a in calls["agent"].unique().to_list())
    calls, XR, XP = CS.build_inputs(calls, msgs, agents)
    keep = CS.all_present_trim(calls)
    return calls.filter(pl.Series(keep)), XR[keep], XP[keep], agents, calls, XR, XP


def _init(payload):
    _S.update(payload)


def skel(seed):
    calls, agents, h, focal = _S["calls_all"], _S["agents"], _S["h"], _S["focal"]
    A = len(agents)
    Z = np.zeros((A, A))
    s, XRs, XPs = CS.simulate(calls, agents, h, lambda k: Z, np.zeros(A), seed=seed)
    m = _S["keep"]
    cw = calls.filter(pl.Series(m))
    pres = L.present_agents(cw, FROZEN["min_calls"])
    f = L.fit_additive(cw, XRs[m], XPs[m], agents, pres, FROZEN["lam"], s_override=s[m])
    if focal not in pres:
        return np.nan
    return (L.ranks_desc(f["S"])[pres.index(focal)] - 1) / (len(pres) - 1)


def run(goal, days, focal, include_holdout, out: Path):
    out.mkdir(parents=True, exist_ok=True)
    cw, XRk, XPk, agents, calls_all, XR, XP = build(goal, days, include_holdout)
    pres = L.present_agents(cw, FROZEN["min_calls"])
    if focal not in pres:
        raise SystemExit(f"focal agent {focal} has < {FROZEN['min_calls']} trimmed calls; C1/C2 not scorable")
    f = L.fit_additive(cw, XRk, XPk, agents, pres, FROZEN["lam"])
    q = pres.index(focal)
    uF = (L.ranks_desc(f["S"])[q] - 1) / (len(pres) - 1)
    uFP = (L.ranks_desc(f["SP"])[q] - 1) / (len(pres) - 1)
    s = calls_all["s"].to_numpy()
    a = calls_all["agent"].to_numpy()
    md = calls_all["mode"].to_numpy()
    h = np.zeros(calls_all.height)
    for ag in np.unique(a):
        for mm in (0, 1):
            sel = (a == ag) & (md == mm)
            if sel.sum():
                p = ((s[sel] > 0).sum() + 0.5) / (sel.sum() + 1.0)
                h[sel] = 0.5 * np.log(p / (1 - p))
    keep = CS.all_present_trim(calls_all)
    payload = dict(calls_all=calls_all, agents=agents, h=h, focal=focal, keep=keep)
    with ProcessPoolExecutor(max_workers=2, initializer=_init, initargs=(payload,)) as ex:
        null = np.array(list(ex.map(skel, range(31000, 31000 + FROZEN["skel_reps"]), chunksize=8)), float)
    q90 = float(np.nanpercentile(null, 100 * FROZEN["C2_q"]))
    res = {"goal": goal, "days": days, "focal": focal, "n_present": len(pres), "n_calls": f["n"],
           "u_F": float(uF), "u_F_inflight": float(uFP), "null_mean": float(np.nanmean(null)), "null_q90": q90,
           "C1": {"pass": bool(uF >= FROZEN["C1_u"])}, "C2": {"pass": bool(uF > q90)}, "frozen": FROZEN,
           "include_holdout": include_holdout, "run_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (out / "confirm_result.json").write_text(json.dumps(res, indent=1))
    return res


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--confirm", action="store_true")
    ap.add_argument("--focal", type=int)
    a = ap.parse_args()
    if a.dry_run:
        res = run(STANDIN["goal"], STANDIN["days"], STANDIN["focal"], False, SCRATCH)
        print("DRY RUN (stand-in, non-holdout):", json.dumps(res, indent=1))
        return
    if os.environ.get("H115_CONFIRM") != "1":
        raise SystemExit("refusing: set H115_CONFIRM=1 (and get Vivian's sign-off) to touch the locked holdout")
    if a.focal is None:
        raise SystemExit("refusing: --focal (the #48 focal agent code, from the goal record) is required")
    import holdout_ledger as HL
    chk = HL.check("H115", TARGET["ledger_target"], "talk timing", "kinetic_ising_couplings")
    if not chk["allowed"]:
        raise SystemExit(f"refusing: holdout ledger does not allow this use: {chk}")
    if chk["needs_disclosure"]:
        print("NOTE: disclosure required (holdout.md reuse policy):", [u["hypothesis"] for u in chk["prior_runs"]])
    res = run(TARGET["goal"], TARGET["days"], a.focal, True, OUT)
    print(json.dumps(res, indent=1))
    print("Record the run: holdout_ledger.record_run(<entry id>, evidence=<output path + LOG.md date>)")


if __name__ == "__main__":
    main()
