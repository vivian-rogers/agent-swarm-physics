"""H58 real-data pipeline, replication layer (card F1-F8, predictions P1-P5, P8): per unit of analysis, candidate units
from coordination (multi-layer communities, single-layer communities, the calibrated subset search), baselines (rooms,
labs, agent + own artifact), their coordination gain with both nulls, Krakauer decomposition against the aggregation
baseline, night gain, content gain, lagged (transfer-entropy) gain and bin-width variants.

Non-holdout only (asserted by the loader). Outputs data/processed/H58-coordinated-superagents/results/units/<unit>.json
and results/replication.json. Run: uv run python hypotheses/H58-coordinated-superagents/analysis/run.py [--only 40,44]
"""
from __future__ import annotations

import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ[_v] = "1"

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h58data as HD  # noqa: E402
import h58lib as L  # noqa: E402

OUT = HD.D / "results"
N_SURR = 19          # search calibration: p_search <= 0.05 iff the observed maximum beats all 19 surrogate maxima
MAX_EVALS = 2000      # A2.6: compute-scarce round


def jsonable(o):
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating, float)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, np.ndarray):
        return jsonable(o.tolist())
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def describe(U, members, cn, seed, rooms, labs, full=True):
    ev = L.evaluate(U, members, cn, n_shift=100, seed=seed)
    ev["agents"] = [int(U.agents[a]) for a in ev["members"]]
    ev["rooms"] = sorted({rooms[a] for a in ev["members"] if a in rooms})
    ev["labs"] = sorted({labs.get(int(U.agents[a]), "?") for a in ev["members"]})
    ev["repos"] = [int(U.repos[k]) for k in U.shared_artifacts(ev["members"])]
    if not full:
        return ev
    ev["g_lag"] = L.coord_gain(U, ev["members"], window=(0,))
    ev["g_content"] = L.content_gain(U, ev["members"])
    gn = L.coord_gain(U, ev["members"], night=True, return_parts=True)
    ev["g_night"], ev["n_night"] = gn["g"], gn["n"]
    if np.isfinite(gn["g"]):
        cnn = L.CompNull(U, n_draw=100, seed=seed, night=True)
        shn = L.shift_null(U, ev["members"], n_draw=60, seed=seed, g0=gn["g"], night=True)
        czn = cnn.z(ev["members"], gn["g"], sd_floor=shn["sd"] if np.isfinite(shn.get("sd", np.nan)) else 0.0)
        ev["z_night_comp"], ev["z_night_shift"] = czn["z"], shn["z"]
    ks = L.krakauer_shift(U, ev["members"], n_draw=40, seed=seed)
    if ks.get("ok"):
        ev.update({"iota": ks["iota"], "colonial": ks["colonial"], "organismal": ks["organismal"],
                   "environmental": ks["environmental"], "H": ks["H"], "iota_shift_mu": ks["iota_shift_mu"],
                   "z_iota_shift": ks["z_iota_shift"]})
    ev["iota_members"] = L.member_iota(U, ev["members"])
    return ev


def run_unit(name: str) -> dict:
    t0 = time.time()
    U = HD.load_unit(name)
    rooms = HD.modal_rooms(U)
    labs = HD.labs()
    seed = sum(map(ord, name))
    cn = L.CompNull(U, n_draw=200, seed=seed)
    out = {"unit": name, "goal_no": U.extra["goal_no"], "regime": U.regime, "nA": U.nA, "nB": U.nB, "nD": U.nD,
           "n_repos": len(U.repos), "n_commits": int(U.Wn.sum()), "agents": [int(a) for a in U.agents]}
    # ---- singletons: agent + own artifact (the null unit)
    sing = []
    for a in range(U.nA):
        Ra = U.shared_artifacts([a])
        rec = {"agent": int(U.agents[a]), "n_own": int(len(Ra)), "commits": int(U.act_a[a])}
        if len(Ra):
            k = L.krakauer(U, L.unit_state(U, [a], Ra), L.env_state(U, [a], Ra))
            if k.get("ok"):
                rec.update({"iota": k["iota"], "colonial": k["colonial"], "organismal": k["organismal"],
                            "environmental": k["environmental"]})
        sing.append(rec)
    out["singletons"] = sing
    # ---- coordination layers -> communities
    M = L.layer_matrices(list(U.agents), HD.layer_rows(name))
    cands = {}
    for key in ("multi", "w_sync", "w_coad", "w_reply", "w_coart"):
        cs = L.communities(M[key]) if M[key].sum() > 0 else []
        cands[key] = cs
    # baselines
    rgroups = {}
    for a, r in rooms.items():
        rgroups.setdefault(r, []).append(a)
    room_units = [sorted(v) for v in rgroups.values() if len(v) >= 2]
    cands["room"] = room_units if len(room_units) >= 2 else []
    lgroups = {}
    for a in range(U.nA):
        lgroups.setdefault(labs.get(int(U.agents[a]), "?"), []).append(a)
    cands["lab"] = [sorted(v) for v in lgroups.values() if len(v) >= 2]
    cands["crew"] = L.crew_seeds(U)
    # ---- calibrated subset search (seeded with crews, multi-layer communities, best pairs)
    sr = L.search_calibrated(U, n_surr=N_SURR, seed=seed, max_evals=MAX_EVALS, seeds=cands["multi"])
    out["search"] = {"members": sr["members"], "agents": [int(U.agents[a]) for a in (sr["members"] or [])],
                     "J": sr["J"], "null_J": sr["null_J"], "p_search": sr["p_search"], "n_eval": sr["n_eval"],
                     "pruned": sr.get("pruned", 0)}
    # ---- evaluate every candidate
    res = {}
    for key, cs in cands.items():
        full = key in ("multi", "room", "lab")
        res[key] = [describe(U, c, cn, seed + i, rooms, labs, full=full) for i, c in enumerate(cs)]
    if sr["members"]:
        ev = describe(U, sr["members"], cn, seed + 99, rooms, labs, full=True)
        ev["p_search"] = sr["p_search"]
        ev["qualifies_search"] = bool(ev["qualifies"] and sr["p_search"] <= 0.05)
        res["search"] = [ev]
    else:
        res["search"] = []
    out["candidates"] = res
    # ---- bin-width variants for the search result and qualifying units
    var = {}
    targets = [("search", c["members"]) for c in res["search"]] + \
              [(k, c["members"]) for k in ("multi",) for c in res[k] if c["qualifies"]]
    for bm in (15, 60):
        Ub = HD.load_unit(name, bin_min=bm)
        cnb = L.CompNull(Ub, n_draw=100, seed=seed)
        var[str(bm)] = [{"from": k, "members": m, **{kk: vv for kk, vv in L.evaluate(Ub, m, cnb, n_shift=60, seed=seed)
                                                      .items() if kk in ("g", "z_comp", "z_shift", "specificity",
                                                                         "qualifies")}} for (k, m) in targets]
    out["variants"] = var
    # ---- unit-level summary
    multi_q = [c for c in res["multi"] if c["qualifies"]]
    search_q = [c for c in res["search"] if c.get("qualifies_search")]
    out["summary"] = {
        "any_candidate": bool(multi_q or search_q),
        "n_multi": len(res["multi"]), "n_multi_qual": len(multi_q), "search_qual": bool(search_q),
        "median_z": {k: (float(np.nanmedian([c["z_comp"] for c in res[k] if c["z_comp"] is not None
                                             and np.isfinite(c["z_comp"])])) if any(
            c["z_comp"] is not None and np.isfinite(c["z_comp"]) for c in res[k]) else None) for k in res},
        "secs": time.time() - t0}
    return jsonable(out)


def main():
    only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
    meta = HD.units_meta()
    HD.assert_no_holdout(meta)
    names = [x["unit"] for x in meta if (only is None or x["unit"] in only)]
    # largest first for load balance
    names = sorted(names, key=lambda n: -sum(len(x["days"]) for x in meta if x["unit"] == n))
    (OUT / "units").mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    with ProcessPoolExecutor(2) as ex:
        for r in ex.map(run_unit, names):
            (OUT / "units" / f"{r['unit']}.json").write_text(json.dumps(r, indent=1))
            s = r["summary"]
            print(f"{r['unit']}: candidate={s['any_candidate']} multi {s['n_multi_qual']}/{s['n_multi']} "
                  f"search={s['search_qual']} ({s['secs']:.0f}s; total {time.time() - t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
