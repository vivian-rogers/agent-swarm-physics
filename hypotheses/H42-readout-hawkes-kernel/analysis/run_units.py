"""H42 replication pipeline: per period unit, TALK (three worlds) and ACTIVITY Hawkes fits, held-out CV, nulls, sensitivity.

Writes data/processed/H42-readout-hawkes-kernel/G<NN>/units/<unit>.json (one per unit; resumable).

Worlds (TALK):
  pr  pre-registered specs (own call-clock pulse in every spec): S0, A, A_H03, A_g, B, B_t, C
  A   amendment 1, H03 world (no call clock): S0, A, A_H03, B_t
  B   amendment 1, call-clock world (pulse-gated baseline per call class, gated self/exo): S0, B, A_g, C, C_g
ACTIVITY: S0, A, B, C (visible + invisible source families).
Nulls: 5 shift surrogates (in sample), 2 shift surrogates through CV, up to 3 day-block surrogates; activity: 2 shifts.
Sensitivity (TALK): read-outs and pulses on t_call_lo / t_call_hi; spans trimmed by 10 min at each end.

Usage: uv run python hypotheses/H42-readout-hawkes-kernel/analysis/run_units.py [--period G38] [--unit 38a]
       [--workers 2] [--force] [--no-act]
"""
from __future__ import annotations

import json
import sys
import time
import traceback
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import h42lib as L  # noqa: E402

N_SHIFT, N_SHIFT_CV, N_DAYBLOCK, N_SHIFT_ACT = 5, 2, 3, 2
WORLDS = {"pr": L.TALK_SPECS, "A": L.WORLD_A_SPECS, "B": L.WORLD_B_SPECS}
NULL_SPECS = {"pr": ["A", "B", "A_g"], "A": ["A", "B_t"], "B": ["B", "A_g", "C"]}
NULL_CV_SPECS = {"pr": ["A", "B"], "B": ["B", "A_g"]}
SENS_SPECS = {"pr": ["S0", "B"], "B": ["S0", "B", "A_g"]}
ACT_CV_MAX = 60_000       # activity CV (S0, A, B only) skipped above this many events (cost; shared machine)


def jsonable(x):
    if isinstance(x, dict):
        return {str(k): jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [jsonable(v) for v in x]
    if isinstance(x, (np.floating, float)):
        return None if not np.isfinite(x) else float(x)
    if isinstance(x, (np.integer,)):
        return int(x)
    return x


def fit_block(ds, SP, specs, cv_specs=None, seed=0):
    out = {}
    fits = {}
    for s in specs:
        f = L.fit_spec(ds, SP, s, warm=fits.get("S0"))
        fits[s] = f
        br = L.branching(ds, f)
        out[s] = {"ll": f.ll, "n": f.n, **{k: v for k, v in br.items() if k not in ("weights",)}}
    if cv_specs and ds.D >= 2:
        cvr = L.cv(ds, SP, cv_specs, seed=seed)
        for s, (ll, n) in cvr.items():
            out[s]["cv_ll"] = ll
            out[s]["cv_n"] = n
    return out, fits


def null_fits(u, world, SP, base_ds, specs, items, cv_specs=None, seed=0):
    ds = L.build_talk(u, world=world, items_override=items, only_cross=True, base=base_ds)
    res = {}
    fits = {}
    for s in ["S0"] + specs:
        f = L.fit_spec(ds, SP, s, warm=fits.get("S0"), restart=False)
        fits[s] = f
        br = L.branching(ds, f)
        res[s] = {"ll": f.ll, "n_cross": br["n_cross"],
                  "contrib": {k: v for k, v in br["contrib"].items() if L.colfam(k) in L.CROSS_PREFIX}}
    if cv_specs:
        cvr = L.cv(ds, SP, ["S0"] + cv_specs, seed=seed)
        for s, (ll, n) in cvr.items():
            res.setdefault(s, {})
            res[s]["cv_ll"] = ll
            res[s]["cv_n"] = n
    return res


def run_unit(uid: str, goal: int, do_act=True, force=False):
    out_dir = L.DATA / f"G{goal:02d}" / "units"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{uid}.json"
    if path.exists() and not force:
        return uid, "skip"
    t0 = time.time()
    u = L.load_unit(uid, goal)
    rng = np.random.default_rng(abs(hash(uid)) % (2**32))
    res = {"unit_id": uid, "goal_no": goal, "regime": u.regime, "n_days": u.n_days,
           "n_agents": int(u.calls["agent"].n_unique()), "n_talk": len(u.talk), "talk": {}, "talk_nulls": {},
           "sens": {}}
    base = {}
    for world, SP in WORLDS.items():
        ds = L.build_talk(u, world=world)
        base[world] = ds
        blk, _ = fit_block(ds, SP, list(SP), list(SP))
        res["talk"][world] = {"meta": ds.meta, "specs": blk}
    # nulls
    shifts = [L.shift_items(u, rng)[0] for _ in range(N_SHIFT)]
    for world in WORLDS:
        SP = WORLDS[world]
        nl = {"shift": [], "shift_cv": [], "dayblock": []}
        for i, items in enumerate(shifts):
            nl["shift"].append(null_fits(u, world, SP, base[world], NULL_SPECS[world], items))
            if i < N_SHIFT_CV and world in NULL_CV_SPECS and u.n_days >= 2:
                nl["shift_cv"].append(null_fits(u, world, SP, base[world], [], items,
                                                cv_specs=NULL_CV_SPECS[world]))
        if world in ("pr", "B"):
            for k in range(1, min(N_DAYBLOCK, u.n_days - 1) + 1):
                items = L.dayblock_items(u, k)
                nl["dayblock"].append(null_fits(u, world, SP, base[world], NULL_SPECS[world], items))
        res["talk_nulls"][world] = nl
    # sensitivity
    for var, kw in (("lo", {"variant": "lo"}), ("hi", {"variant": "hi"}), ("trim", {"trim": 600.0})):
        res["sens"][var] = {}
        for world, specs in SENS_SPECS.items():
            ds = L.build_talk(u, world=world, **kw)
            cvs = specs if (world == "B" and u.n_days >= 2 and len(u.talk) <= 6000) else None
            blk, _ = fit_block(ds, WORLDS[world], specs, cvs)
            res["sens"][var][world] = blk
    res["t_talk_s"] = time.time() - t0
    # activity
    if do_act:
        t1 = time.time()
        da = L.build_act(u)
        cvs = ["S0", "A", "B"] if da.meta["n_events"] <= ACT_CV_MAX else None
        blk, _ = fit_block(da, L.ACT_SPECS, list(L.ACT_SPECS), cvs)
        res["act"] = {"meta": da.meta, "specs": blk}
        anl = []
        for i in range(N_SHIFT_ACT):
            items, keys = L.shift_items(u, rng)
            inv = L.shift_inv(u, keys, rng)
            dn = L.build_act(u, items_override=items, inv_override=inv, only_cross=True, base=da)
            r = {}
            fits = {}
            for s in ["S0", "A", "B"]:
                f = L.fit_spec(dn, L.ACT_SPECS, s, warm=fits.get("S0"), restart=False)
                fits[s] = f
                br = L.branching(dn, f)
                r[s] = {"ll": f.ll, "n_cross": br["n_cross"], **{k: br.get(k, 0.0) for k in ("n_Av", "n_Ai", "n_Bv", "n_Bi")}}
            anl.append(r)
        res["act_nulls"] = {"shift": anl}
        res["t_act_s"] = time.time() - t1
    path.write_text(json.dumps(jsonable(res)))
    return uid, f"done {time.time() - t0:.0f}s"


def _task(args):
    uid, goal, do_act, force = args
    try:
        return run_unit(uid, goal, do_act, force)
    except Exception:
        return uid, "ERROR " + traceback.format_exc()[-1500:]


def main():
    argv = sys.argv
    units = L.list_units().filter(pl.col("eligible"))
    if "--period" in argv:
        want = {int(x.strip().lstrip("Gg#")) for x in argv[argv.index("--period") + 1].split(",")}
        units = units.filter(pl.col("goal_no").is_in(list(want)))
    if "--unit" in argv:
        units = units.filter(pl.col("unit_id").is_in(argv[argv.index("--unit") + 1].split(",")))
    workers = int(argv[argv.index("--workers") + 1]) if "--workers" in argv else 2
    do_act = "--no-act" not in argv
    force = "--force" in argv
    units = units.sort("n_calls", descending="--big-first" in argv)
    tasks = [(r["unit_id"], r["goal_no"], do_act, force) for r in units.iter_rows(named=True)]
    print(f"{len(tasks)} units, workers={workers}", flush=True)
    if workers <= 1:
        for t in tasks:
            print(*_task(t), flush=True)
    else:
        with Pool(workers, maxtasksperchild=4) as pool:
            for uid, msg in pool.imap_unordered(_task, tasks):
                print(uid, msg, flush=True)


if __name__ == "__main__":
    main()
