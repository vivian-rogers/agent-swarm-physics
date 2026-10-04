"""H93 synthetic validation (axis F): Brock-Durlauf choice worlds on each period's real work-event skeleton.

The skeleton is the real work stream of a period (who arrives when, paired switches, departures, expiries, units and
days). Each arrival's destination is redrawn from the H93 model:
  v_j = alpha_j + b_named named_j + b_own prev_ij + bJ s_j,  v_NEW = alpha_new,
with repo fitness alpha_j ~ N(0, sigma_A^2) drawn at birth and n_named kickoff-named repos available (dormant) from the
start. The synthetic stream then goes through the same long_table builder and estimators as the real data.

  uv run python hypotheses/H93-brock-durlauf-project-choice/analysis/synthetic.py --period 31 --reps 40
Writes data/processed/H93-brock-durlauf-project-choice/synthetic/G<NN>.parquet (one row per world x rep x model).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h93lib as L  # noqa: E402
import h93scheme as S  # noqa: E402

DATA = ROOT / "data/processed/H93-brock-durlauf-project-choice"
WORLDS = {
    "W0": dict(bJ=0.0, sA=0.0),
    "W1": dict(bJ=0.0, sA=0.5),
    "W2": dict(bJ=0.0, sA=1.0),
    "W3": dict(bJ=3.0, sA=0.0),
    "W4": dict(bJ=3.0, sA=1.0),
    "W5": dict(bJ=6.0, sA=0.5),
    # A2 (post hoc, after the first real run): time-varying repo fitness ("attention bursts", H28), no coupling
    "W6": dict(bJ=0.0, sA=0.5, burst=1.0, tau=20),
    "W7": dict(bJ=0.0, sA=0.5, burst=2.0, tau=20),
    "W8": dict(bJ=0.0, sA=0.5, burst=1.0, tau=100),
    "W9": dict(bJ=3.0, sA=0.5, burst=1.0, tau=20),
}
B_NAMED, B_OWN = 1.5, 2.0
FIT_MODELS = ["M0", "M1", "M2", "M3a", "M3b", "M4", "R3"]


def skeleton(g: int) -> tuple[pl.DataFrame, dict]:
    """Real work stream rebuilt from shared tables (non-holdout), plus target counts."""
    sys.path.insert(0, str(ROOT / "infra/shared"))
    import replicator_hosts as R  # noqa: E402
    from common import holdout_mask  # noqa: E402
    d = R.build_period(g)
    cal = R.calendar().filter(pl.col("pt_date").is_in(d["days"]))
    ws = S.attach_unit(S.work_stream(d["events"], d["unit_map"]), cal, d["unit_map"])
    ws = ws.filter(~pl.Series(holdout_mask(ws["pt_date"].to_list(), [g] * ws.height)))
    ev = pl.read_parquet(DATA / f"G{g:02d}" / "events_work.parquet")
    tgt = {"new_frac": float(ev["is_new"].mean()), "n_named": int(sum(bool(v) for v in d["named"].values())),
           "events": ev.height}
    return ws, tgt


def simulate(ws: pl.DataFrame, n_named: int, bJ: float, sA: float, a_new: float, rng, b_named=B_NAMED, b_own=B_OWN,
             b_cum: float = 0.0, burst: float = 0.0, tau: float = 20.0):
    alpha: dict[str, float] = {}
    named: dict[str, bool] = {}
    for k in range(n_named):
        alpha[f"K{k}"] = rng.normal(0, sA) if sA > 0 else 0.0
        named[f"K{k}"] = True
    dormant_named = set(alpha)
    host: dict[int, str] = {}
    held: dict[int, set] = {}
    seen_unit: set = set()
    syn_prev: dict[int, str] = {}
    cur_unit = None
    nid = 0
    cumc: dict[str, int] = {}
    xb: dict[str, float] = {}
    rho = float(np.exp(-1.0 / tau)) if burst > 0 else 0.0
    out = []
    for r in ws.iter_rows(named=True):
        a = int(r["agent"])
        if r["unit"] != cur_unit:
            cur_unit = r["unit"]
            seen_unit = set()
        if r["op"] == "drop":
            if a in host:
                rep = host.pop(a)
                syn_prev[a] = rep
                out.append({**r, "repo": rep, "prev": None, "paired": False})
            continue
        excl = syn_prev.get(a) if r["paired"] else None
        others = {b: rep for b, rep in host.items() if b != a}
        nact = len(others)
        cnt: dict[str, int] = {}
        for rep in others.values():
            cnt[rep] = cnt.get(rep, 0) + 1
        opts = sorted((seen_unit | set(cnt) | dormant_named) - {excl, None})
        hs = held.get(a, set())
        if burst > 0:  # OU fitness fluctuation per repo on the arrival clock
            for o in list(alpha):
                xb[o] = rho * xb.get(o, rng.normal(0, burst)) + np.sqrt(1 - rho * rho) * burst * rng.normal()
        v = np.array([alpha[o] + xb.get(o, 0.0) + b_named * named.get(o, False) + b_own * (o in hs) + b_cum * np.log1p(cumc.get(o, 0))
                      + bJ * (cnt.get(o, 0) / nact if nact else 0.0) for o in opts] + [a_new])
        p = np.exp(v - v.max())
        p /= p.sum()
        k = rng.choice(len(p), p=p)
        if k == len(opts):
            rep = f"R{nid}"
            nid += 1
            alpha[rep] = rng.normal(0, sA) if sA > 0 else 0.0
        else:
            rep = opts[k]
        dormant_named.discard(rep)
        if a in host:  # unpaired arrival while hosting cannot happen in the real stream; guard
            host.pop(a)
        host[a] = rep
        held.setdefault(a, set()).add(rep)
        seen_unit.add(rep)
        cumc[rep] = cumc.get(rep, 0) + 1
        out.append({**r, "repo": rep, "prev": excl if r["paired"] else None, "paired": bool(r["paired"]) and excl is not None})
    st = pl.DataFrame(out, schema=ws.schema)
    return st, named


def calibrate(ws, tgt, bJ, sA, rng, iters=7, burst=0.0, tau=20.0):
    lo, hi = -6.0, 4.0
    for _ in range(iters):
        mid = (lo + hi) / 2
        fr = []
        for _ in range(2):
            st, named = simulate(ws, tgt["n_named"], bJ, sA, mid, rng, burst=burst, tau=tau)
            ev, lt, _ = S.long_table(st, named)
            fr.append(float(ev["is_new"].mean()) if ev is not None else 0.0)
        if np.mean(fr) > tgt["new_frac"]:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def one(ws, tgt, world, a_new, seed):
    rng = np.random.default_rng(seed)
    st, named = simulate(ws, tgt["n_named"], world["bJ"], world["sA"], a_new, rng, burst=world.get("burst", 0.0),
                         tau=world.get("tau", 20.0))
    ev, lt, occ = S.long_table(st, named)
    if lt is None:
        return []
    lt = L.add_features(lt)
    rows = []
    units = sorted(lt["unit"].unique().to_list())
    per_unit = [u for u in units if L.testable(lt.filter(pl.col("unit") == u))]
    for m in FIT_MODELS:
        try:
            if per_unit and len(units) > 1:
                fs = [L.fit(lt.filter(pl.col("unit") == u), m) for u in per_unit]
                pool = L.dl_pool([f.get("gamma") for f in fs], [f.get("gamma_se") for f in fs])
                est = pool
                scope = f"pooled {len(per_unit)} units"
            else:
                f = L.fit(lt, m)
                est = {"est": f.get("gamma"), "se": f.get("gamma_se"), "lo": f.get("gamma_lo"), "hi": f.get("gamma_hi")}
                scope = "period"
        except Exception as e:  # noqa: BLE001
            est, scope = None, f"error {e}"
        rows.append({"model": m, "scope": scope, "est": None if not est else est["est"], "se": None if not est else est["se"],
                     "lo": None if not est else est["lo"], "hi": None if not est else est["hi"],
                     "events": ev.height, "new_frac": float(ev["is_new"].mean())})
    return rows


def run(g: int, reps: int, seed0: int = 1000, worlds=None, tag=""):
    ws, tgt = skeleton(g)
    out = []
    rng = np.random.default_rng(seed0)
    for wname, w in WORLDS.items():
        if worlds and wname not in worlds:
            continue
        t0 = time.time()
        a_new = calibrate(ws, tgt, w["bJ"], w["sA"], rng, burst=w.get("burst", 0.0), tau=w.get("tau", 20.0))
        for r in range(reps):
            for row in one(ws, tgt, w, a_new, seed0 + 7919 * r + 101 * list(WORLDS).index(wname)):
                out.append({"period": g, "world": wname, "rep": r, "bJ_true": w["bJ"], "sA": w["sA"], "a_new": a_new, **row})
        print(g, wname, f"{time.time() - t0:.0f}s", flush=True)
    df = pl.DataFrame(out)
    (DATA / "synthetic").mkdir(parents=True, exist_ok=True)
    df.write_parquet(DATA / "synthetic" / f"G{g:02d}{tag}.parquet")
    return df


def summarize(df: pl.DataFrame) -> pl.DataFrame:
    d = df.filter(pl.col("est").is_not_null() & pl.col("se").is_not_null())
    return (d.group_by("period", "world", "model").agg(
        pl.col("bJ_true").first(), pl.col("sA").first(), pl.len().alias("n"),
        (pl.col("est") - pl.col("bJ_true")).median().alias("bias_med"),
        pl.col("est").median().alias("est_med"),
        ((pl.col("lo") <= pl.col("bJ_true")) & (pl.col("hi") >= pl.col("bJ_true"))).mean().alias("cover"),
        (pl.col("lo") > 0).mean().alias("pos_rate"),
        pl.col("events").median().alias("events"), pl.col("new_frac").median().alias("new_frac"))
        .sort("period", "world", "model"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", type=int, action="append")
    ap.add_argument("--reps", type=int, default=40)
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--worlds", nargs="*")
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    if a.summary:
        df = pl.concat([pl.read_parquet(p) for p in sorted((DATA / "synthetic").glob("G*.parquet"))], how="diagonal_relaxed")
        s = summarize(df)
        s.write_parquet(DATA / "synthetic" / "summary.parquet")
        with pl.Config(tbl_rows=400, tbl_cols=20):
            print(s)
    else:
        for g in a.period:
            run(g, a.reps, worlds=a.worlds, tag=a.tag)
