"""H126 round-1 run on real data (after the synthetic and Amendment A1).

Replication: every eligible unit design (U*): telegraph fits (M2a two-stage, M2s, M4p), held-out-day shape test against
the unit's own parametric bootstrap (N0), held-out-day occupancy prediction (P2), call vs wall clock (P5), raw runs
(P6, P7); variants gte / style / no-dedupe for the headline statistics (no bootstrap).
Kickoff designs (K*, assigned destinations only): segment rates F vs A with an agent-cluster bootstrap (P3).
Natives: N12 (debate windows), N51 (own goals, per unit), NE38 (one agent, parametric bootstrap).
Outputs: data/processed/H126-telegraph-goal-occupancy/results/{units,kick,natives}.json(l)
Usage: uv run --with numba python hypotheses/H126-telegraph-goal-occupancy/analysis/run.py [--workers 2] [--B 30]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h126lib as L  # noqa: E402

ROOT = HERE.parents[2]
D = ROOT / "data/processed/H126-telegraph-goal-occupancy"
RES = D / "results"
QMODE = "free"   # Amendment A1 (card M2a: per-agent rates, emissions fitted jointly)
B_NULL = 30
B_SEG = 200
N_SIM = 100


def _clean(r):
    return {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in r.items() if not k.startswith("_")}


def frame(design):
    return pl.read_parquet(D / "stmts.parquet").filter(pl.col("design") == design)


def unit_job(*a):
    try:
        return _unit_job(*a)
    except Exception as e:  # recorded, not silently dropped
        return dict(design=str(a[0]) if a else "?", unit=str(a[0]) if a else "?", eligible=False, error=repr(e)[:300])


def _unit_job(design):
    rng = np.random.default_rng(abs(hash(design)) % (2 ** 32))
    df = frame(design)
    out = dict(design=design)
    S, meta = L.design_seq(df, variant="bge", dedupe=True)
    if S is None:
        return dict(design=design, eligible=False)
    r = L.evaluate_unit(S, meta, rng, n_sim=N_SIM, qmode=QMODE)
    if not r.get("eligible"):
        return dict(design=design, eligible=False)
    null = L.bootstrap_shape_null(r["_S"], r["_meta"], r["_fit2"], rng, B=B_NULL, qmode=QMODE)
    p1, q95 = L.p1_verdict(r["dll4_held"], null, r["cv_on"], r["cv_off"])
    out.update(_clean(r), null_q95=q95, null_med=float(np.median(null)), P1=p1,
               P2=("within20" if abs(r["rho_p"]) <= math.log(1.2) else ("off30" if abs(r["rho_p"]) > math.log(1.3)
                                                                         else "between")))
    # agent-cluster bootstrap CI for rho_p and the shared rates (cheap: shared fits + one occupancy simulation set)
    var = {}
    for v, dd in (("gte", True), ("sty", True), ("bge_nodedupe", False)):
        vv = "bge" if v == "bge_nodedupe" else v
        Sv, mv = L.design_seq(df, variant=vv, dedupe=dd)
        if Sv is None:
            continue
        rv = L.evaluate_unit(Sv, mv, rng, n_sim=40, do_wall=False, qmode=QMODE)
        if rv.get("eligible"):
            var[v] = dict(dll4_held=rv["dll4_held"], cv_on=rv["cv_on"], cv_off=rv["cv_off"], rho_p=rv["rho_p"],
                          p_dw=rv["p_dw"], p_win=rv["p_win"], tau_on_med=rv["tau_on_med"], q0=rv["q0"], q1=rv["q1"])
    out["variants"] = var
    return out


def seg_frame_build(min_seg, base_label):
    def build(fr):
        S, m = L.design_seq(fr, rg_mode="seg", seg_split=True, min_seg=min_seg)
        if S is None or len(m["segs"]) < 2:
            return None
        if m["segs"].index(base_label) != 0:
            S.rg[:] = 1 - S.rg
        return S
    return build


def kick_job(*a):
    try:
        return _kick_job(*a)
    except Exception as e:  # recorded, not silently dropped
        return dict(design=str(a[0]) if a else "?", unit=str(a[0]) if a else "?", eligible=False, error=repr(e)[:300])


def _kick_job(design):
    rng = np.random.default_rng(abs(hash(design)) % (2 ** 32))
    df = frame(design)
    build = seg_frame_build(20, "F")
    S = build(df)
    if S is None:
        return dict(design=design, eligible=False)
    S0, m0 = L.design_seq(df, rg_mode="seg", seg_split=True, min_seg=20)
    n_ag = len(m0["agents"])
    if n_ag < 3:
        return dict(design=design, eligible=False, n_agents=n_ag)
    f = L.fit2(S)
    dla, dlb = math.log(f["a"][1] / f["a"][0]), math.log(f["b"][1] / f["b"][0])
    bs = L.seg_bootstrap(m0["frame"], build, rng, B=B_SEG)
    lo, hi = np.percentile(bs, 5, axis=0), np.percentile(bs, 95, axis=0)
    a_up, b_null = lo[0] > 0, lo[1] <= 0 <= hi[1]
    b_excl = hi[1] < 0 or lo[1] > 0
    verdict = "k_on" if (a_up and b_null) else ("k_off" if (b_excl and abs(dlb) >= abs(dla)) else "inconclusive")
    pF = f["a"][0] / (f["a"][0] + f["b"][0])
    pA = f["a"][1] / (f["a"][1] + f["b"][1])
    return dict(design=design, eligible=True, n_agents=n_ag, n_stmt=int(S.n), a_F=float(f["a"][0]), b_F=float(f["b"][0]),
                a_A=float(f["a"][1]), b_A=float(f["b"][1]), q0=f["q0"], q1=f["q1"], p_F=float(pF), p_A=float(pA),
                dln_a=dla, dln_b=dlb, a_lo=float(lo[0]), a_hi=float(hi[0]), b_lo=float(lo[1]), b_hi=float(hi[1]),
                n_boot=int(len(bs)), P3=verdict)


def n12_job(*a):
    try:
        return _n12_job(*a)
    except Exception as e:  # recorded, not silently dropped
        return dict(design=str(a[0]) if a else "?", unit=str(a[0]) if a else "?", eligible=False, error=repr(e)[:300])


def _n12_job(design):
    """Debate windows: rate group = segment of the statement (D debate on / O outside); sequences not split."""
    rng = np.random.default_rng(12)
    df = frame(design)
    S, m = L.design_seq(df, rg_mode="seg", seg_split=False, min_stmt=30)
    if S is None or len(m["segs"]) < 2:
        return dict(design=design, eligible=False, reason="no debate windows in this unit")
    base = m["segs"].index("O")
    if base != 0:
        S.rg[:] = 1 - S.rg
    f = L.fit2(S)
    dla, dlb = math.log(f["a"][1] / f["a"][0]), math.log(f["b"][1] / f["b"][0])

    def build(fr):
        Sx, mx = L.design_seq(fr, rg_mode="seg", seg_split=False, min_stmt=30)
        if Sx is None or len(mx["segs"]) < 2:
            return None
        if mx["segs"].index("O") != 0:
            Sx.rg[:] = 1 - Sx.rg
        return Sx
    bs = L.seg_bootstrap(m["frame"], build, rng, B=B_SEG)
    lo, hi = np.percentile(bs, 5, axis=0), np.percentile(bs, 95, axis=0)
    verdict = ("supported" if (lo[0] > 0 and lo[1] <= 0 <= hi[1]) else
               ("failed" if (hi[1] < 0 and abs(dlb) >= abs(dla)) else "inconclusive"))
    return dict(design=design, eligible=True, n_stmt=int(S.n), n_agents=len(m["agents"]), a_O=float(f["a"][0]), b_O=float(f["b"][0]),
                a_D=float(f["a"][1]), b_D=float(f["b"][1]), q0=f["q0"], q1=f["q1"], dln_a=dla, dln_b=dlb,
                a_lo=float(lo[0]), a_hi=float(hi[0]), b_lo=float(lo[1]), b_hi=float(hi[1]), N1=verdict,
                share_D=float((S.rg == 1).mean()))


def n51_job(*a):
    try:
        return _n51_job(*a)
    except Exception as e:  # recorded, not silently dropped
        return dict(design=str(a[0]) if a else "?", unit=str(a[0]) if a else "?", eligible=False, error=repr(e)[:300])


def _n51_job(unit):
    rng = np.random.default_rng(abs(hash(unit)) % (2 ** 32))
    st = pl.read_parquet(D / "stmts.parquet").filter(pl.col("design").str.starts_with(f"N51_{unit}_"))
    S, meta = L.design_seq(st, variant="bge", dedupe=True)
    if S is None:
        return dict(unit=unit, eligible=False)
    r = L.evaluate_unit(S, meta, rng, n_sim=60, qmode=QMODE)
    if not r.get("eligible"):
        return dict(unit=unit, eligible=False)
    null = L.bootstrap_shape_null(r["_S"], r["_meta"], r["_fit2"], rng, B=20, qmode=QMODE)
    p1, q95 = L.p1_verdict(r["dll4_held"], null, r["cv_on"], r["cv_off"])
    return dict(unit=unit, **_clean(r), null_q95=q95, P1=p1,
                P2=("within20" if abs(r["rho_p"]) <= math.log(1.2) else ("off30" if abs(r["rho_p"]) > math.log(1.3)
                                                                         else "between")))


def ne38_job(_=None):
    rng = np.random.default_rng(38)
    df = frame("NE38")
    S, m = L.design_seq(df, rg_mode="seg", seg_split=True, min_seg=10)
    base = m["segs"].index("F")
    if base != 0:
        S.rg[:] = 1 - S.rg
    f = L.fit2(S)
    dla, dlb = math.log(f["a"][1] / f["a"][0]), math.log(f["b"][1] / f["b"][0])
    bs = []
    for _ in range(B_SEG):
        ob, _ = L.simulate2(S, f["a"], f["b"], f["q0"], f["q1"], rng)
        fx = L.fit2(L.Seq(ob, S.step, S.rg, S.ptr, S.n_rg))
        bs.append((math.log(fx["a"][1] / fx["a"][0]), math.log(fx["b"][1] / fx["b"][0])))
    bs = np.array(bs)
    lo, hi = np.percentile(bs, 5, axis=0), np.percentile(bs, 95, axis=0)
    verdict = ("supported" if (lo[0] > 0 and lo[1] <= 0 <= hi[1]) else ("failed" if hi[1] < 0 else "inconclusive"))
    f_on = [float(S.obs[S.rg == g].mean()) for g in (0, 1)]
    return dict(design="NE38", n_stmt=int(S.n), n_F=int((S.rg == 0).sum()), n_A=int((S.rg == 1).sum()), f_on_F=f_on[0],
                f_on_A=f_on[1], a_F=float(f["a"][0]), b_F=float(f["b"][0]), a_A=float(f["a"][1]), b_A=float(f["b"][1]),
                q0=f["q0"], q1=f["q1"], dln_a=dla, dln_b=dlb, a_lo=float(lo[0]), a_hi=float(hi[0]), b_lo=float(lo[1]),
                b_hi=float(hi[1]), N3=verdict)


def n51_stability(r51):
    """Spearman across agents of ln k_on (and ln k_off) between consecutive #51 units (agents in both)."""
    from scipy.stats import spearmanr
    el = [r for r in r51 if r.get("eligible")]
    rk, rf = [], []
    for x, y in zip(el[:-1], el[1:]):
        ax = dict(zip(x["agents"], zip(x["a_i"], x["b_i"])))
        ay = dict(zip(y["agents"], zip(y["a_i"], y["b_i"])))
        common = sorted(set(ax) & set(ay))
        if len(common) < 5:
            continue
        rk.append(spearmanr([math.log(ax[a][0]) for a in common], [math.log(ay[a][0]) for a in common])[0])
        rf.append(spearmanr([math.log(ax[a][1]) for a in common], [math.log(ay[a][1]) for a in common])[0])
    return dict(n_pairs=len(rk), median_rho_kon=float(np.median(rk)) if rk else None,
                median_rho_koff=float(np.median(rf)) if rf else None, rho_kon=rk, rho_koff=rf)


def main():
    global B_NULL
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--B", type=int, default=30)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    B_NULL = a.B
    RES.mkdir(parents=True, exist_ok=True)
    des = pl.read_parquet(D / "designs.parquet")
    units = des.filter(pl.col("kind") == "unit")["design"].to_list()
    kicks = des.filter((pl.col("kind") == "kickoff") & (pl.col("mode") != "F"))["design"].to_list()
    n51 = sorted(des.filter(pl.col("kind") == "native_g51")["unit"].unique().to_list())
    with Pool(a.workers) as pool:
        if a.only in ("", "units"):
            rows = pool.map(unit_job, units, chunksize=1)
            (RES / "units.json").write_text(json.dumps(rows, indent=1, default=float))
            print("units done")
        if a.only in ("", "kick"):
            rows = pool.map(kick_job, kicks, chunksize=1)
            (RES / "kick.json").write_text(json.dumps(rows, indent=1, default=float))
            print("kick done")
        if a.only in ("", "natives"):
            n12 = pool.map(n12_job, ["N12_12a", "N12_12b"], chunksize=1)
            r51 = pool.map(n51_job, n51, chunksize=1)
            r38 = ne38_job()
            stab = n51_stability(r51)
            (RES / "natives.json").write_text(json.dumps(dict(N12=n12, N51=r51, N51_stability=stab, NE38=r38), indent=1,
                                                         default=float))
            print("natives done")


if __name__ == "__main__":
    main()
