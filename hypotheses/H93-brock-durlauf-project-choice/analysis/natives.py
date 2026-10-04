"""H93 native tests (predictions in goalperiod-subhypotheses/G37, G44, G51 READMEs).

  uv run python hypotheses/H93-brock-durlauf-project-choice/analysis/natives.py --g37 --g44 --g51 [--sims 200]

G37  rooms with identical kickoff text as same-field replicas. Fit M4 on the whole period; simulate the fitted model on
     the real event skeleton; compare the observed room difference of the order parameter (Delta m = m_room2 - m_room3)
     with the simulated distribution; BD fixed points per room.
G44  the room-goal split: per-arm M4/M2 fits, P_multi and order parameters.
G51  twelve same-goal units: per-unit M4 fits, P_multi, m; each unit simulated from the pooled fit; count of units
     whose observed m falls outside its simulated 95% band (multiple equilibria would put herded units outside).
Writes results/native_G<NN>.json.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
sys.path.insert(0, str(ROOT / "infra/shared"))
import build as B  # noqa: E402
import h93lib as L  # noqa: E402
import h93scheme as S  # noqa: E402
import synthetic as SY  # noqa: E402

DATA = ROOT / "data/processed/H93-brock-durlauf-project-choice"


def room_m(stream: pl.DataFrame, room_of, min_hosts: int = 2) -> dict:
    """Per room: mean over arrivals by choosers in the room of the largest-option share among the other hosts in the same
    room (>= min_hosts of them)."""
    host: dict[int, str] = {}
    acc: dict = {}
    for r in stream.iter_rows(named=True):
        a = int(r["agent"])
        if r["op"] == "drop":
            if host.get(a) == r["repo"]:
                del host[a]
            continue
        ra = room_of(a, r["t"])
        hs = [rep for b, rep in host.items() if b != a and room_of(b, r["t"]) == ra]
        if len(hs) >= min_hosts:
            c: dict = {}
            for rep in hs:
                c[rep] = c.get(rep, 0) + 1
            acc.setdefault(ra, []).append(max(c.values()) / len(hs))
        host[a] = r["repo"]
    return {k: float(np.mean(v)) for k, v in acc.items() if v}


def unit_m(stream: pl.DataFrame, min_hosts: int = 3) -> dict:
    host: dict[int, str] = {}
    acc: dict = {}
    for r in stream.iter_rows(named=True):
        a = int(r["agent"])
        if r["op"] == "drop":
            if host.get(a) == r["repo"]:
                del host[a]
            continue
        hs = [rep for b, rep in host.items() if b != a]
        if len(hs) >= min_hosts:
            c: dict = {}
            for rep in hs:
                c[rep] = c.get(rep, 0) + 1
            acc.setdefault(r["unit"], []).append(max(c.values()) / len(hs))
        host[a] = r["repo"]
    return {k: float(np.mean(v)) for k, v in acc.items() if v}


def params(f: dict) -> dict:
    g = lambda nm: (L.coef(f, nm)[0] or 0.0)  # noqa: E731
    newk = [nm for nm in f["names"] if nm.startswith("new")]
    an = float(np.mean([f["theta"][f["names"].index(k)] for k in newk])) if newk else 0.0
    return {"bJ": g("s"), "b_named": g("named"), "b_own": g("prev"), "b_cum": g("logcum"), "a_new": an}


def simulate_fit(stream, n_named, p, sims, seed, stat):
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(sims):
        st, _ = SY.simulate(stream, n_named, p["bJ"], 0.0, p["a_new"], rng, b_named=p["b_named"], b_own=p["b_own"],
                            b_cum=p["b_cum"])
        out.append(stat(st))
    return out


def g37(sims: int) -> dict:
    d = B.build_period(37, write=False)
    room_of = S.rooms_lookup(pl.read_parquet(ROOT / "data/processed/shared/rooms_timeline.parquet"))
    res = {}
    for ch in ("work", "attention"):
        st = d["streams"][ch]
        ev, lt, _ = d[ch]
        if lt is None:
            continue
        lt = L.add_features(lt)
        f = L.fit(lt, "M4")
        p = params(f)
        obs = room_m(st, room_of)
        rooms = sorted(obs)
        r = {"fit": {k: v for k, v in f.items() if not k.startswith("_")}, "params": p, "m_obs": obs}
        if len(rooms) == 2:
            dm_obs = obs[rooms[0]] - obs[rooms[1]]
            named = d["named_work"] if ch == "work" else d["named_att"]
            nn = sum(bool(v) for v in named.values())
            sim = simulate_fit(st, nn, p, sims, 37, lambda s: room_m(s, room_of))
            dms = [x.get(rooms[0], np.nan) - x.get(rooms[1], np.nan) for x in sim]
            dms = np.array([x for x in dms if np.isfinite(x)])
            r["dm_obs"] = dm_obs
            r["dm_sim_q"] = [float(np.quantile(dms, q)) for q in (0.025, 0.5, 0.975)] if len(dms) else None
            r["p_two_sided"] = float(np.mean(np.abs(dms - np.median(dms)) >= abs(dm_obs - np.median(dms)))) if len(dms) else None
            r["sim_m_room_q"] = {str(rm): [float(np.nanquantile([x.get(rm, np.nan) for x in sim], q)) for q in (0.025, 0.5, 0.975)]
                                 for rm in rooms}
        # per-room BD equilibria (choosers in the room)
        evr = ev.with_columns(pl.Series("room", [room_of(a, t) for a, t in ev.select("agent", "t").iter_rows()]))
        per = {}
        for rm in rooms:
            ids = evr.filter(pl.col("room") == rm)["eid"]
            sub = lt.filter(pl.col("eid").is_in(ids.implode()))
            try:
                fr = L.fit(sub, "M4")
                per[str(rm)] = {"events": int(ids.len()), "gamma": fr.get("gamma"), "gamma_lo": fr.get("gamma_lo"),
                                "gamma_hi": fr.get("gamma_hi"), "eq": L.p_multi(sub, fr, None, draws=200),
                                "eq_pooled_fit": L.p_multi(sub, f, None, draws=200)}
            except Exception as e:  # noqa: BLE001
                per[str(rm)] = {"error": str(e)}
        r["per_room"] = per
        res[ch] = r
    return res


def g44(sims: int) -> dict:
    d = B.build_period(44, write=False)
    room_of = S.rooms_lookup(pl.read_parquet(ROOT / "data/processed/shared/rooms_timeline.parquet"))
    res = {}
    for ch in ("work", "attention"):
        st = d["streams"][ch]
        ev, lt, _ = d[ch]
        if lt is None:
            continue
        lt = L.add_features(lt)
        obs = room_m(st, room_of)
        evr = ev.with_columns(pl.Series("room", [room_of(a, t) for a, t in ev.select("agent", "t").iter_rows()]))
        arms = {}
        for rm in sorted(obs):
            e2 = evr.filter(pl.col("room") == rm)
            sub = lt.filter(pl.col("eid").is_in(e2["eid"].implode()))
            a = {"events": e2.height, "m_obs": obs[rm], "new_frac": float(e2["is_new"].mean()),
                 "prev_frac": float(e2["prev_chosen"].mean()), "named_frac": float(e2["named_chosen"].mean())}
            try:
                for m in ("M2", "M4"):
                    fr = L.fit(sub, m)
                    a[m] = {k: v for k, v in fr.items() if not k.startswith("_")}
                a["eq"] = L.p_multi(sub, L.fit(sub, "M4"), None, draws=200)
                a["testable"] = L.testable(sub)
            except Exception as e:  # noqa: BLE001
                a["error"] = str(e)
            arms[str(rm)] = a
        res[ch] = arms
    return res


def g51(sims: int) -> dict:
    d = B.build_period(51, write=False)
    res = {}
    for ch in ("work", "attention"):
        st = d["streams"][ch]
        ev, lt, _ = d[ch]
        if lt is None:
            continue
        lt = L.add_features(lt)
        units = sorted(lt["unit"].unique().to_list())
        obs = unit_m(st)
        per = {}
        fits = {}
        for u in units:
            sub = lt.filter(pl.col("unit") == u)
            ok = L.testable(sub)
            row = {"events": int(sub["eid"].n_unique()), "testable": ok, "m_obs": obs.get(u)}
            if ok:
                fr = L.fit(sub, "M4")
                fits[u] = fr
                row.update({"gamma": fr.get("gamma"), "gamma_lo": fr.get("gamma_lo"), "gamma_hi": fr.get("gamma_hi"),
                            "eq": L.p_multi(sub, fr, u, draws=100)})
            per[u] = row
        pool = L.dl_pool([f.get("gamma") for f in fits.values()], [f.get("gamma_se") for f in fits.values()])
        # simulate the whole period from the pooled parameters (mean of unit fits for the fields)
        pm = {k: float(np.mean([params(f)[k] for f in fits.values()])) for k in ("b_named", "b_own", "b_cum", "a_new")}
        pm["bJ"] = pool["est"] if pool else 0.0
        named = d["named_work"] if ch == "work" else d["named_att"]
        sims_m = simulate_fit(st, sum(bool(v) for v in named.values()), pm, max(20, sims // 4), 51, unit_m)
        out_band = 0
        tested = 0
        for u in units:
            vals = [x.get(u) for x in sims_m if x.get(u) is not None]
            if obs.get(u) is None or len(vals) < 10:
                continue
            lo, hi = np.quantile(vals, [0.025, 0.975])
            per[u]["sim_band"] = [float(lo), float(hi)]
            tested += 1
            out_band += not (lo <= obs[u] <= hi)
        res[ch] = {"units": per, "pool": pool, "pooled_params": pm, "units_outside_band": out_band, "units_banded": tested,
                   "m_obs_all": [obs.get(u) for u in units]}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--g37", action="store_true")
    ap.add_argument("--g44", action="store_true")
    ap.add_argument("--g51", action="store_true")
    ap.add_argument("--sims", type=int, default=200)
    a = ap.parse_args()
    (DATA / "results").mkdir(parents=True, exist_ok=True)
    for flag, fn, g in ((a.g37, g37, 37), (a.g44, g44, 44), (a.g51, g51, 51)):
        if flag:
            r = fn(a.sims)
            (DATA / "results" / f"native_G{g}.json").write_text(json.dumps(r, indent=1, default=float))
            print(g, "done", flush=True)


if __name__ == "__main__":
    main()
