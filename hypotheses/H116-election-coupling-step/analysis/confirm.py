"""H116 confirmatory run on the LOCKED HOLDOUT. Written and frozen 2026-10-04 after round 1; NOT RUN.

Guard: held-out data are touched only with BOTH `--confirm` and H116_CONFIRM=1, only if `holdout_ledger.check` allows
H116 on G47 and G48 (family kinetic_ising_couplings), and only with `--focal` (the focal agent of #48, supplied by the
coordinator from the #48 goal record at run time; this script never reads held-out text). Otherwise it refuses.
`--dry-run` runs the identical pipeline on a non-holdout stand-in (#26, 2026-01-07 -> 01-08, focal = agent 17; placebo
pairs from #24, #25, #27), built from scratch into a scratch directory.

Target: NE37, the step from the focal agent's last active day of #47 (held out) to #48 (2026-06-22, held out), when
the whole village was redirected to help that one agent: an operator designation of a focal node.
Statistic (frozen = round 1, A1): per-call talk spins on the ledger clock; winner-focused event model with
pre = the focal agent's last #47 day (all-present trim), post = 2026-06-22 (all-present trim); agent x call mode x side
intercepts; lambda 4 for tests, 0.01 for the magnitude. Time placebos: every consecutive pair of non-holdout days in
the placebo goals (regime III: #38, #39, #40, #41, #42, #44) where the focal agent has >= 30 trimmed calls on both
days. Skeleton null: 200 field-only worlds (J = 0, real talk rate per agent x call mode x side) on the target skeleton.

Frozen predictions (round 1: the #26 result gave dJ_out +0.09 +- 0.33, a step >= 0.75 excluded; judges and lead
designers carry no role step, -0.04 +- 0.10 and -0.02 +- 0.11; the post hoc re-election step +1.03 +- 0.47 is excluded
from the claim):
  C1  No coupling step at a designation: the A1 detection rule does NOT fire (dJout >= 0.05 and above both q95), and the
      unpenalized dJout point estimate is < 0.75 Ising units.
  C2  The focal agent's in-coupling step dJin lies inside the central 90% of the time placebos.
Reading: C1 confirms "designation is a field, not a per-call coupling step of >= 0.75"; a detection contradicts it.

Reuse policy (hypotheses/holdout.md): G48 was run by H04 (other families); G47 has planned users (see the ledger).
H115's confirm plans a different statistic (the focal agent's sink rank on #48 alone) in the same family: whichever
runs second discloses. The first choice (NE31, #45) is blocked: H02 ran the same family on #45.

Usage:
  uv run python hypotheses/H116-election-coupling-step/analysis/confirm.py --dry-run
  H116_CONFIRM=1 uv run python hypotheses/H116-election-coupling-step/analysis/confirm.py --confirm --focal <agent code>
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
import h116lib as L  # noqa: E402

CS = L.CS
sys.path.insert(0, str(L.ROOT / "infra/shared"))
SCRATCH = Path(os.environ.get("TMPDIR", "/tmp")) / "h116_confirm_dryrun"
OUT = L.DATA / "confirm"
FROZEN = dict(lam=4.0, lam_mag=0.01, thr=0.05, max_mag=0.75, skel_reps=200, min_focal_calls=30, band=(5, 95))
TARGET = dict(pre_goal=47, post_goal=48, post_day="2026-06-22", placebo_goals=[38, 39, 40, 41, 42, 44],
              ledger_targets=["G47", "G48"])
STANDIN = dict(pre_goal=26, post_goal=26, pre_day="2026-01-07", post_day="2026-01-08", placebo_goals=[24, 25, 27],
               focal=17)

_S = {}


def day_frame(goals, days, include_holdout):
    CS.ALLOW_HOLDOUT = bool(include_holdout)
    calls = CS.load_calls(goals, days=days, include_holdout=include_holdout)
    msgs = CS.load_messages(goals, days=days, include_holdout=include_holdout)
    agents = sorted(int(a) for a in calls["agent"].unique().to_list())
    calls, XR, XP = CS.build_inputs(calls, msgs, agents)
    calls = calls.with_columns(pl.Series("trim", CS.all_present_trim(calls)))
    return calls, XR, XP, agents


def pair_masks(calls, d0, d1):
    tr = calls["trim"].to_numpy()
    d = calls["pt_date"].to_numpy()
    return (d == d0) & tr, (d == d1) & tr


def last_focal_day(goal, focal, include_holdout):
    CS.ALLOW_HOLDOUT = bool(include_holdout)
    c = CS.load_calls([goal], include_holdout=include_holdout)
    vc = c.filter(pl.col("agent") == focal).group_by("pt_date").len()
    days = sorted(d for d, n in vc.iter_rows() if n >= FROZEN["min_focal_calls"])
    return days[-1] if days else None


def placebo_pairs(goals, focal):
    vals = []
    for g in goals:
        calls, XR, XP, agents = day_frame([g], None, False)
        days = sorted(calls["pt_date"].unique().to_list())
        a = calls["agent"].to_numpy()
        for d0, d1 in zip(days[:-1], days[1:]):
            pre, post = pair_masks(calls, d0, d1)
            if ((a == focal) & pre).sum() < FROZEN["min_focal_calls"] or ((a == focal) & post).sum() < FROZEN["min_focal_calls"]:
                continue
            f = L.fit_event(calls, XR, XP, agents, focal, pre, post, FROZEN["lam"], se=False)
            if f is not None:
                vals.append((g, d0, d1, f["coef"]["dJout"], f["coef"]["dJin"]))
    return vals


def _init(payload):
    _S.update(payload)


def skel(seed):
    calls, agents, h = _S["calls"], _S["agents"], _S["h"]
    A = len(agents)
    Z = np.zeros((A, A))
    s, XRs, XPs = CS.simulate(calls, agents, h, lambda k: Z, np.zeros(A), seed=seed)
    f = L.fit_event(calls, XRs, XPs, agents, _S["focal"], _S["pre"], _S["post"], FROZEN["lam"], se=False, s_override=s)
    return np.nan if f is None else f["coef"]["dJout"]


def run(cfg, focal, include_holdout, out: Path):
    out.mkdir(parents=True, exist_ok=True)
    pre_day = cfg.get("pre_day") or last_focal_day(cfg["pre_goal"], focal, include_holdout)
    if pre_day is None:
        raise SystemExit("focal agent has no qualifying pre day; not scorable")
    goals = sorted({cfg["pre_goal"], cfg["post_goal"]})
    calls, XR, XP, agents = day_frame(goals, [pre_day, cfg["post_day"]], include_holdout)
    pre, post = pair_masks(calls, pre_day, cfg["post_day"])
    f = L.fit_event(calls, XR, XP, agents, focal, pre, post, FROZEN["lam"], se=True)
    fm = L.fit_event(calls, XR, XP, agents, focal, pre, post, FROZEN["lam_mag"], se=True)
    if f is None:
        raise SystemExit("focal agent below the presence threshold in a window; not scorable")
    s = calls["s"].to_numpy()
    a = calls["agent"].to_numpy()
    md = calls["mode"].to_numpy()
    side = np.where(pre, "pre", np.where(post, "post", "out"))
    keys = np.char.add(np.char.add(a.astype(str), "|"), np.char.add(side, np.char.add("|", md.astype(str))))
    h = np.zeros(calls.height)
    for k in np.unique(keys):
        sel = keys == k
        p = ((s[sel] > 0).sum() + 0.5) / (sel.sum() + 1.0)
        h[sel] = 0.5 * np.log(p / (1 - p))
    payload = dict(calls=calls, agents=agents, h=h, focal=focal, pre=pre, post=post)
    with ProcessPoolExecutor(max_workers=2, initializer=_init, initargs=(payload,)) as ex:
        sk = np.array(list(ex.map(skel, range(41000, 41000 + FROZEN["skel_reps"]), chunksize=8)), float)
    pp = placebo_pairs(cfg["placebo_goals"], focal)
    tp_out = np.array([v[3] for v in pp])
    tp_in = np.array([v[4] for v in pp])
    d = f["coef"]["dJout"]
    q_t = float(np.percentile(tp_out, 95)) if len(tp_out) else np.nan
    q_s = float(np.nanpercentile(sk, 95))
    detect = bool(d >= FROZEN["thr"] and d > q_t and d > q_s)
    lo, hi = (np.percentile(tp_in, FROZEN["band"]) if len(tp_in) else (np.nan, np.nan))
    res = {"focal": focal, "pre_day": pre_day, "post_day": cfg["post_day"], "n_calls": f["n"],
           "dJout": d, "dJin": f["coef"]["dJin"], "magnitude_dJout": fm["coef"]["dJout"], "magnitude_se": fm["se"]["dJout"],
           "n_time_placebos": len(pp), "time_q95": q_t, "skeleton_q95": q_s, "detect_A1": detect,
           "C1": {"pass": bool((not detect) and fm["coef"]["dJout"] < FROZEN["max_mag"])},
           "C2": {"pass": bool(lo <= f["coef"]["dJin"] <= hi), "band": [float(lo), float(hi)]},
           "frozen": FROZEN, "include_holdout": include_holdout,
           "run_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (out / "confirm_result.json").write_text(json.dumps(res, indent=1, default=float))
    return res


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--confirm", action="store_true")
    ap.add_argument("--focal", type=int)
    a = ap.parse_args()
    if a.dry_run:
        res = run(STANDIN, STANDIN["focal"], False, SCRATCH)
        print("DRY RUN (stand-in, non-holdout):", json.dumps(res, indent=1, default=float))
        return
    if os.environ.get("H116_CONFIRM") != "1":
        raise SystemExit("refusing: set H116_CONFIRM=1 (and get Vivian's sign-off) to touch the locked holdout")
    if a.focal is None:
        raise SystemExit("refusing: --focal (the #48 focal agent code, from the goal record) is required")
    import holdout_ledger as HL
    for t in TARGET["ledger_targets"]:
        chk = HL.check("H116", t, "talk timing", "kinetic_ising_couplings")
        if not chk["allowed"]:
            raise SystemExit(f"refusing: holdout ledger does not allow {t}: {chk}")
        if chk["needs_disclosure"]:
            print(f"NOTE: disclosure required on {t}:", [u["hypothesis"] for u in chk["prior_runs"]])
    res = run(TARGET, a.focal, True, OUT)
    print(json.dumps(res, indent=1, default=float))
    print("Record the run: holdout_ledger.record_run(<entry id>, evidence=<output path + LOG.md date>)")


if __name__ == "__main__":
    main()
