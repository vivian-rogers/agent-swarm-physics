"""H42 round 2, R3 on real data (non-reserved): round 1's world-B (S0, B, Bmu) and world-A (S0, A) Hawkes fits with
the round-1 shared 30-min baseline ('r1') and with Cox fields ('cox10' per day x 10 min; 'room10' per day x room x
10 min for multi-room units; 'cox5' per day x 5 min, in sample only). Day-blocked CV refits agent levels and the field
on test days (r3lib.heldout_field).

Writes data/processed/H42-readout-hawkes-kernel/round2/r3/<unit>.json (resumable) and r3_units.parquet.
Usage: uv run python hypotheses/H42-readout-hawkes-kernel/analysis/r3_run.py [--units 38b] [--force]
"""
from __future__ import annotations

import json
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import r3lib as R  # noqa: E402
import h42lib as H  # noqa: E402

sys.path.insert(0, str(H.ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402

OUT = H.DATA / "round2" / "r3"


def run(uid):
    f = OUT / f"{uid}.json"
    if f.exists() and "--force" not in sys.argv:
        return json.loads(f.read_text())
    t0 = time.time()
    try:
        u = H.load_unit(uid)
        days = u.days["pt_date"].to_list()
        assert not any(holdout_mask(days, [u.goal] * len(days))), "reserved day"
        nrooms = len(set(R.rooms_by_turn(u).values()) - {-1})
        res = {"unit_id": uid, "goal_no": u.goal, "regime": u.regime, "n_days": u.n_days, "n_rooms": nrooms,
               "n_items": int(u.items.filter(pl.col("kind") == "agent").height),
               "n_named_items": int(u.items.filter((pl.col("kind") == "agent") & pl.col("ment")).height)}
        dsb = R.world_b(u, split=True)
        calls = R.b_call_index(u, dsb)
        bases = ["r1", "cox10"] + (["room10"] if nrooms > 1 else []) + ["cox5"]
        for base in bases:
            resl, mode = R.BASES[base]
            db = R.b_field(dsb, calls, resl, mode)
            o = R.fit_block(db, R.SPECS_B, ["S0", "B", "Bmu"], cv=(base != "cox5"))
            res.update({f"B:{base}:{k}": v for k, v in o.items()})
            res[f"B:{base}:nbins"] = db.meta["field"][2]
        dsa = H.build_talk(u, world="A", specs=("A",))
        for base in ("r1", "cox10"):
            resl, mode = R.BASES[base]
            da = R.a_field(dsa, resl, mode)
            o = R.fit_block(da, R.SPECS_A, ["S0", "A"], cv=True)
            res.update({f"A:{base}:{k}": v for k, v in o.items()})
        res["secs"] = time.time() - t0
    except Exception as e:  # noqa: BLE001
        res = {"unit_id": uid, "error": repr(e), "tb": traceback.format_exc()}
    OUT.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps({k: (None if isinstance(v, float) and not np.isfinite(v) else v) for k, v in res.items()}))
    print(uid, {k: round(v, 4) for k, v in res.items() if k.endswith(":nx") or k.endswith("n_Bm")},
          f"{res.get('secs', 0):.0f}s", res.get("error", ""), flush=True)
    return res


def main():
    ul = H.list_units().filter(pl.col("eligible")).sort("n_calls")
    ids = ul["unit_id"].to_list() if "--units" not in sys.argv else sys.argv[sys.argv.index("--units") + 1].split(",")
    rows = []
    with ProcessPoolExecutor(2) as ex:
        for r in ex.map(run, ids):
            rows.append(r)
    pl.DataFrame(rows, infer_schema_length=None).write_parquet(H.DATA / "round2" / "r3_units.parquet")


if __name__ == "__main__":
    main()
