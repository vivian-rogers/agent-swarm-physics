"""H141 replication and natives on every non-reserved regime-III unit of #37-#42, #44 and #51 (51a-51l), three vector
variants. Writes per unit x variant rows, checkpointed.

    uv run python hypotheses/H141-easy-plane-anisotropy/analysis/run_units.py [--variants 0,1,2] [--periods 38,44] [--B 200]
Output: data/processed/H141-easy-plane-anisotropy/results/{units.parquet, units.json, kick.json}
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import pickle  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "infra/shared"))
import h141lib as L  # noqa: E402
import kick as K  # noqa: E402
from common import holdout_mask  # noqa: E402

RES = L.DATA / "results"
PERIODS = [37, 38, 39, 40, 41, 42, 44, 51]
N_SWAP = 20


def unit_days(goal: int) -> dict:
    pu = pl.read_parquet(L.SH / "period_units.parquet").filter((pl.col("goal_no") == goal) & ~pl.col("holdout"))
    out = {}
    for r in pu.iter_rows(named=True):
        ds = [d for d in r["days"] if not holdout_mask([d], [goal])[0]]
        out[r["unit_id"]] = ds
    return out


def mhat_by_day(D: L.Data) -> dict:
    """Cross-fitted data room direction per day: unit(mean z of room-2 statements on other days of the period - mean z
    of room-3 statements on other days)."""
    room = D.st["room"].fill_null(-1).to_numpy()
    day = D.st["pt_date"].to_numpy()
    out = {}
    for d in np.unique(day):
        m2 = (room == 2) & (day != d)
        m3 = (room == 3) & (day != d)
        if m2.sum() < 20 or m3.sum() < 20:
            continue
        v = D.Z[m2].mean(0) - D.Z[m3].mean(0)
        out[d] = (v / np.linalg.norm(v))[:, None]
    return out


def swap_specs(D: L.Data, seed: int) -> list[dict]:
    """N_SWAP derangements: each agent's plane key is mapped to the plane of an agent with a different role text."""
    rng = np.random.default_rng(seed)
    keys = sorted(set(D.st["plane"].to_list()))
    texts_by_key = {k: D.texts[k] for k in keys}
    specs = []
    for _ in range(N_SWAP):
        spec = {"__boot__": False}
        for k in keys:
            others = [o for o in D.planes if o not in (k,) and o.startswith("a")
                      and abs(float(D.texts.get(o, np.zeros(32)) @ texts_by_key[k])) < 0.999]
            spec[k] = D.planes[others[rng.integers(len(others))]]
        specs.append(spec)
    return specs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variants", default="0,1,2")
    ap.add_argument("--periods", default=",".join(map(str, PERIODS)))
    ap.add_argument("--B", type=int, default=200)
    ap.add_argument("--n_rand", type=int, default=200)
    ap.add_argument("--kick", action="store_true", help="also run O5 (P4) on #51 units, primary variant only")
    a = ap.parse_args()
    RES.mkdir(parents=True, exist_ok=True)
    path = RES / "units.parquet"
    full_path = RES / "units.pkl"
    rows = pl.read_parquet(path).to_dicts() if path.exists() else []
    full = pickle.loads(full_path.read_bytes()) if full_path.exists() else {}
    kick_res = json.loads((RES / "kick.json").read_text()) if (RES / "kick.json").exists() else {}
    for vi in [int(x) for x in a.variants.split(",")]:
        model, variant = L.VARIANTS[vi]
        for goal in [int(x) for x in a.periods.split(",")]:
            D = L.load(goal, model, variant)
            ud = unit_days(goal)
            extra_common = {"khat": {k: D.texts["kickoff"][:, None] for k in set(D.st["plane"].to_list())}}
            if goal == 51:
                extra_common["own"] = {k: D.texts[k][:, None] for k in set(D.st["plane"].to_list())}
            if goal in (38, 44):
                mh = mhat_by_day(D)
                extra_common["roomdiff"] = {"P": D.texts["roomdiff"][:, None]}
                extra_common["mhat"] = {"__by_day__": mh}
                extra_common["Emhat"] = {"__by_day__": {d: np.column_stack([D.planes["P"], v]) for d, v in mh.items()}}
            for u, days in sorted(ud.items()):
                key = f"{model}|{variant}|{u}"
                if key in full:
                    continue
                t0 = time.time()
                Du = L.subset(D, [u])
                if Du.st.height < 50:
                    continue
                A = L.accumulate(Du)
                extra = dict(extra_common)
                if goal == 51 and vi == 0:
                    for s, spec in enumerate(swap_specs(Du, 1000 + s)):
                        extra[f"swap{s}"] = spec
                r = L.analyze_unit(Du, A, days, B=a.B, n_rand=a.n_rand, seed=17, extra_planes=extra)
                r.update({"unit": u, "goal": goal, "model": model, "variant": variant,
                          "testable": bool(len(days) >= 3 and r["n_agents"] >= 4)})
                full[key] = r
                rows.append({k: (json.dumps(v) if isinstance(v, (list, tuple)) else v) for k, v in r.items()
                             if not isinstance(v, np.ndarray)})
                print(f"{key} rho {r['rho']:.2f} {np.round(r.get('ci90', [np.nan] * 2), 2)} pct {r['rand_pct']:.2f} "
                      f"V {r['V_A']:.2f} Pd {r.get('P_diff', np.nan):.3f} ({time.time() - t0:.0f}s)", flush=True)
                pl.DataFrame(rows, infer_schema_length=None).write_parquet(path)
                full_path.write_bytes(pickle.dumps(full))
            if a.kick and goal == 51 and vi == 0:
                rd = pl.read_parquet(L.DATA / "G51/reads.parquet")
                W = K.day_wells(D)
                for u, days in sorted(ud.items()):
                    if u in kick_res:
                        continue
                    Du = L.subset(D, [u])
                    if Du.st.height < 50:
                        continue
                    rdu = rd.filter(pl.col("unit_id") == u)
                    srow_pos = Du.st.select(pl.col("srow").alias("srow_m"))
                    rdu = rdu.join(srow_pos, on="srow_m", how="semi")
                    t0 = time.time()
                    kr = K.kick_unit(Du, rdu, W, a.B, 23)
                    kick_res[u] = {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in kr.items()}
                    kick_res[u]["n_days"] = len(days)
                    print("kick", u, kr["ratio_par"], kr["ratio_perp"], f"({time.time() - t0:.0f}s)", flush=True)
                    (RES / "kick.json").write_text(json.dumps(kick_res, default=float))


if __name__ == "__main__":
    main()
