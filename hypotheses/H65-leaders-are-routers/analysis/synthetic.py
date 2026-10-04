"""H65 synthetic validation (axis F), run before any real-data outcome. Real skeletons (statement times, rooms, ledger
read sets and their ages, unread in-flight sets) of G26, G35, G44, G12; synthetic content vectors from the card's
linear-response model with a planted router, a planted source, or no leader effect; then the unchanged native code.

    uv run python hypotheses/H65-leaders-are-routers/analysis/synthetic.py [--reps 20]
Writes data/processed/H65-leaders-are-routers/synthetic/natives.json (+ replication D_p check on G26/G38).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
           "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from multiprocessing import Pool  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h65lib as L  # noqa: E402
import run as RUN  # noqa: E402

PAR = {"a": 0.3, "a2": 0.2, "b": 0.4, "chi0": 0.4, "h": 0.2, "sigma": 1.0}
SCEN = {"null": (1.0, 1.0), "router": (2.0, 0.2), "router_weak": (1.3, 0.6), "source": (1.0, 3.0)}


def leader_mask(name: str, tg: pl.DataFrame) -> np.ndarray:
    """True where the author holds the leader role at that statement (tg sorted by tgt)."""
    t = tg["t"]
    a = tg["agent"].to_numpy()
    if name == "G26":
        return (a == 17) & ((t >= RUN.G26_TERM[0]) & (t < RUN.G26_TERM[1])).to_numpy()
    if name == "G44":
        return (a == 28) & (t >= RUN.G44_START).to_numpy() & (tg["room"].to_numpy() == RUN.G44_BEST_ROOM)
    g = RUN.gt()
    if name == "G35":
        m = np.zeros(len(a), bool)
        day = tg["pt_date"].to_numpy()
        room = tg["room"].to_numpy()
        for u, ag, det in g.filter((pl.col("goal_no") == 35) & (pl.col("label_kind") == "leader")).select(
                "unit", "agent", "detail").iter_rows():
            r = RUN.ROOMS35["rest" if "room=rest" in det else "best"]
            m |= (a == ag) & (day == u.replace("day_", "")) & (room == r)
        return m
    if name == "G12":
        m = np.zeros(len(a), bool)
        j = dict(g.filter((pl.col("goal_no") == 12) & (pl.col("label_kind") == "judge")).select("unit", "agent")
                 .iter_rows())
        for u, t0, t1 in RUN.g12_windows().iter_rows():
            m |= (a == j[u]) & ((t >= t0) & (t < t1)).to_numpy()
        return m
    raise ValueError(name)


def synth_vectors(tg, rd, pos, nZ, lead, chi_mult, w_mult, rng):
    """Sequential generation in time order. Returns (Zs_syn (nZ x 32), Hm_syn, hpos_syn)."""
    d = 32
    Z = rng.normal(0, 1 / np.sqrt(d), (nZ, d))
    tg = tg.sort("tgt")
    n = tg.height
    kpos = np.array([pos[int(r)] for r in tg["srow"].to_numpy()])
    lead_row = np.zeros(nZ, bool)
    lead_row[kpos[lead]] = True
    agent = tg["agent"].to_numpy()
    day = tg["pt_date"].to_numpy()
    room = tg["room"].to_numpy()
    tt = tg["t"].dt.epoch("us").to_numpy()
    g = {}
    hrows = np.unique(rd.filter(pl.col("src_kind") == 1)["vrow"].to_numpy())
    Hm = rng.normal(0, 1 / np.sqrt(d), (len(hrows), d))
    hpos = {int(r): k for k, r in enumerate(hrows)}
    # read lists per target
    rd0 = rd.filter(pl.col("src_kind") != 2).sort("tgt")
    tk = rd0["tgt"].to_numpy()
    kd = rd0["src_kind"].to_numpy()
    vr = rd0["vrow"].to_numpy()
    w = np.exp(-np.maximum(rd0["age_s"].to_numpy().astype(float), 0) / L.TAU)
    starts = np.searchsorted(tk, np.arange(int(tg["tgt"].max()) + 2))
    tgt_ids = tg["tgt"].to_numpy()
    last, ew = {}, {}
    alpha = 1 - 2 ** (-1 / L.HALF_LIFE)
    for k in np.argsort(tt, kind="stable"):
        key = (agent[k], day[k])
        gk = (day[k], room[k])
        if gk not in g:
            g[gk] = rng.normal(0, 1 / np.sqrt(d), d)
        tid = tgt_ids[k]
        lo, hi = starts[tid], starts[tid + 1]
        inp = np.zeros(d)
        hin = np.zeros(d)
        W = 0.0
        WH = 0.0
        for r in range(lo, hi):
            if kd[r] == 1:
                p = hpos.get(int(vr[r]))
                if p is not None:
                    hin += w[r] * Hm[p]
                    WH += w[r]
                continue
            p = pos.get(int(vr[r]))
            if p is None:
                continue
            m = w_mult if lead_row[p] else 1.0
            inp += w[r] * m * Z[p]
            W += w[r] * m
        inp /= (1 + W)
        hin /= (1 + WH)
        chi = PAR["chi0"] * (chi_mult if lead[k] else 1.0)
        zP = Z[kpos[last[key]]] if key in last else np.zeros(d)
        e = ew.get(key, np.zeros(d))
        z = (PAR["a"] * zP + PAR["a2"] * e + PAR["b"] * g[gk] + chi * inp + PAR["h"] * hin
             + rng.normal(0, PAR["sigma"] / np.sqrt(d), d))
        Z[kpos[k]] = z
        ew[key] = (1 - alpha) * ew[key] + alpha * z if key in ew else z.copy()
        last[key] = k
    return Z, Hm, hpos


def job(args):
    name, scen, rep = args
    goal = int(name[1:])
    rng = np.random.default_rng(1000 * rep + 17 * len(scen) + goal)
    tg, rd, Zs, pos, Hm, hpos, regime, block = RUN.load_period(goal, "bge_small", g12_blocks=(name == "G12"))
    tg = tg.sort("tgt")
    lead = leader_mask(name, tg)
    cm, wm = SCEN[scen]
    Z, Hs, hp = synth_vectors(tg, rd, pos, len(Zs), lead, cm, wm, rng)
    D = L.build_design(tg, rd, Z, pos, Hs, hp, block=block)
    Gr = L.build_grams(D)
    if name in ("G26", "G44"):
        f = RUN.native_g26 if name == "G26" else RUN.native_g44
        r = f(Gr, B=30, rng=rng)
        return {"native": name, "scen": scen, "rep": rep, "router_call": r["router_call"],
                "pct_chi": r["pct_chi"], "pct_kappa": r["pct_kappa"], "router_index": r["router_index"],
                "boot_share": r["router_call_boot_share"]}
    f = RUN.native_g35 if name == "G35" else RUN.native_g12
    r = f(Gr, R=500, rng=rng)
    return {"native": name, "scen": scen, "rep": rep, "router_call": r.get("router_call", False),
            "b_chi": r["chi"]["beta"], "p_chi": r["chi"]["p_greater"], "b_kappa": r["kappa"]["beta"],
            "p_kappa_g": r["kappa"]["p_greater"], "source_call": bool(np.isfinite(r["kappa"]["beta"])
                                                                      and r["kappa"]["p_greater"] < 0.10)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--natives", default="G26,G35,G44,G12")
    ap.add_argument("--scen", default=",".join(SCEN))
    ap.add_argument("--rep0", type=int, default=0)
    ap.add_argument("--tag", default="natives")
    a = ap.parse_args()
    jobs = [(n, s, k) for n in a.natives.split(",") for s in a.scen.split(",")
            for k in range(a.rep0, a.rep0 + a.reps)]
    t0 = time.time()
    with Pool(a.workers) as p:
        res = p.map(job, jobs, chunksize=1)
    df = pl.DataFrame(res, infer_schema_length=None)
    aggs = [pl.len().alias("reps"), pl.col("router_call").mean()]
    for c in ("pct_chi", "pct_kappa", "router_index", "b_chi", "b_kappa", "p_chi"):
        if c in df.columns:
            aggs.append(pl.col(c).mean())
    if "source_call" in df.columns:
        aggs.append(pl.col("source_call").mean())
    summ = df.group_by("native", "scen").agg(aggs).sort("native", "scen")
    with pl.Config(tbl_rows=40, tbl_width_chars=220):
        print(summ)
    out = L.DATA / "synthetic"
    out.mkdir(parents=True, exist_ok=True)
    df.write_parquet(out / f"{a.tag}_reps.parquet")
    (out / f"{a.tag}.json").write_text(json.dumps({"summary": summ.to_dicts(), "params": PAR, "scenarios": SCEN,
                                                  "runtime_s": time.time() - t0}, indent=1, default=float))


if __name__ == "__main__":
    main()
