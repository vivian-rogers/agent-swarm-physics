"""H127 synthetic validation on the real skeleton (axis F), run before any real-data statistic along a kickoff direction.

For each of the 27 eligible kickoffs and each incumbent: the real day-1 statement times with their hour, call, and
read-out clocks, and the real numbers of pre and days 2-5 statements. A world plants
  a_s = P_i + Delta_i F(x_s) + u_{i,day} + v_{i,window} + e_s,  Delta_i ~ |N(0.10, 0.04)| >= 0.02,
with noise components from H125's decoy-direction calibration (read-only; no k-hat statistic). Worlds:
  W_0.15, W_0.7   hour clock, tau_H = 0.15 / 0.7 active h
  C_20, C_100     call clock from t0, tau_C = 20 / 100 calls
  L               step at the read-out call (H08 gating), no further relaxation
  LW_0.5          read-out gate, then hour relaxation (tau 0.5 h)
The card-level rules P1-P4 are applied exactly as on real data.
Writes data/processed/H127-content-trails-goal-call-clock/synthetic/results_<cfg>.json.
Usage: uv run python hypotheses/H127-content-trails-goal-call-clock/analysis/synthetic.py [--reps 30] [--cfg bge_white]
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h127lib as L  # noqa: E402

Z90 = 1.645
AMP_MEAN, AMP_SD = 0.10, 0.04   # settled rise Delta_i ~ |N(AMP_MEAN, AMP_SD)|; the amplitude sweep varies AMP_MEAN


def skeleton(cfg: str):
    T = L.tables()
    des = [d for d in T["k"].filter(pl.col("kind") == "kickoff")["design"].to_list() if d != "T51"] + ["T51"]
    sk = {}
    for d in des:
        units = L.build_units(d, cfg)      # uses real a only for shapes; a is overwritten below
        for u in units:
            u["a"] = np.zeros_like(u["a"])
        sk[d] = units
    return sk


def F_world(world, u):
    if world.startswith("W_"):
        return 1 - np.exp(-np.clip(u["h"], 0, None) / float(world[2:]))
    if world.startswith("C_"):
        return 1 - np.exp(-np.clip(u["c"], 0, None) / float(world[2:]))
    if world == "L":
        return (u["c_ro"] >= 1).astype(float)
    if world.startswith("LW_"):
        return np.where(u["c_ro"] >= 1, 1 - np.exp(-np.clip(u["h_ro"], 0, None) / float(world[3:])), 0.0)
    raise ValueError(world)


def draw_units(world, units, cal, rng):
    out = []
    sb, su, sv, se = (np.sqrt(cal[k]) for k in ("s2_b", "s2_u", "s2_v", "s2_e"))
    for u0 in units:
        u = copy.copy(u0)
        P = rng.normal(0, sb); D = max(0.02, abs(rng.normal(AMP_MEAN, AMP_SD * AMP_MEAN / 0.10)))
        def stm(n, mean):
            if n <= 0:
                return np.array([])
            nw = max(1, n // 5)
            v = rng.normal(0, sv, nw)[np.arange(n) % nw]
            return mean + v + rng.normal(0, se, n)
        pre = stm(u0["n_pre"], P + rng.normal(0, su))
        sett = np.concatenate([stm(u0["n_set"] // 4 + (1 if k < u0["n_set"] % 4 else 0), P + D + rng.normal(0, su)) for k in range(4)])
        n1 = len(u0["h"])
        win = np.floor(u0["h"] / 0.5).astype(int)
        uw, inv = np.unique(win, return_inverse=True) if n1 else (np.array([]), np.array([], int))
        a1 = P + D * F_world(world, u0) + rng.normal(0, su) + (rng.normal(0, sv, len(uw))[inv] if n1 else 0) + rng.normal(0, se, n1)
        pre_fb = len(pre) < L.MIN_PRE
        Pm = 0.0 if pre_fb else float(pre.mean())
        Sm = float(sett.mean()) if len(sett) else np.nan
        sed = np.sqrt((pre.var(ddof=1) / len(pre) if not pre_fb else 0.0) + (sett.var(ddof=1) / len(sett) if len(sett) > 1 else np.nan))
        u.update(a=a1, P=Pm, S=Sm, Delta=Sm - Pm, se_Delta=float(sed), pre_fallback=pre_fb)
        u["rising"] = bool(u["eligible"] and u["Delta"] > L.RISE_Z * u["se_Delta"])
        out.append(u)
    return out


def card_level(res: dict) -> dict:
    s = np.array([r["s"] for r in res.values()]); se = np.array([r["se_s"] for r in res.values()])
    m = L.dl_meta(s, se)
    lo, hi = m["mean"] - Z90 * m["se"], m["mean"] + Z90 * m["se"]
    CR = np.array([r["CR"] for r in res.values()])
    ds = np.array([r["dsse"] for r in res.values()])
    sro = np.array([r.get("s_ro", np.nan) for r in res.values()])
    imm = np.array([r.get("imm_ro", np.nan) for r in res.values()])
    nfit = np.array([r.get("n_fit", 0) for r in res.values()])
    dsm, dse = np.nanmean(ds), L.jack_meta_se(ds)
    srm, srse = np.nanmean(sro), L.jack_meta_se(sro)
    crs = CR[np.isfinite(CR)]
    pa = [x for r in res.values() for x in r.get("_per_agent", [])]
    po = L.pooled_slope(pa, n_boot=200) if pa else dict(s_pool=np.nan, s_pool_lo=np.nan, s_pool_hi=np.nan)
    dro = np.array([r.get("dsse_ro", np.nan) for r in res.values()])
    drm, drse = np.nanmean(dro), L.jack_meta_se(dro)
    return dict(s_pool=po["s_pool"], s_pool_lo=po["s_pool_lo"], s_pool_hi=po["s_pool_hi"],
                P1_pool=bool(po["s_pool_hi"] < 0 and po["s_pool_lo"] <= -0.5 and po["s_pool_hi"] >= -1.5),
                kill_pool=bool(abs(po["s_pool"]) < 0.25 and po["s_pool_lo"] <= 0 <= po["s_pool_hi"]),
                dsse_ro=float(drm), P3_ro=bool(drm - Z90 * drse > 0), P3_ro_neg=bool(drm + Z90 * drse < 0),
s=m["mean"], s_lo=lo, s_hi=hi,
                P1=bool(hi < 0 and lo <= -0.5 and hi >= -1.5), kill1=bool(abs(m["mean"]) < 0.25 and lo <= 0 <= hi),
                CR_med=float(np.median(crs)) if len(crs) else np.nan, CR_share=float(np.mean(crs < 1)) if len(crs) else np.nan,
                P2=bool(len(crs) and np.median(crs) < 1 and np.mean(crs < 1) >= 2 / 3 and L.sign_p(1 - crs) < 0.05),
                dsse=float(dsm), P3=bool(dsm - Z90 * dse > 0), s_ro=float(srm),
                imm_ro=float(np.nanmean(imm)), P4=bool(np.nanmean(imm) < 0.5 and srm + Z90 * srse < 0),
                rise_share=float(np.nanmean([r["rise_share"] for r in res.values()])),
                n_fit_tot=int(nfit.sum()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=30)
    ap.add_argument("--cfg", default="bge_white")
    ap.add_argument("--boot", type=int, default=100)
    ap.add_argument("--amp-fixed", action="store_true", help="the card's original fixed-Delta fit (pre-amendment)")
    ap.add_argument("--worlds", default="W_0.15,W_0.7,C_20,C_100,L,LW_0.5")
    ap.add_argument("--amps", default="0.1,0.2,0.4")
    a = ap.parse_args()
    L.AMP_FREE = not a.amp_fixed
    cal_all = json.loads((L.H125 / "synthetic/calibration.json").read_text())[a.cfg]
    sk = skeleton(a.cfg)
    worlds = a.worlds.split(",")
    out = {}
    t0 = time.time()
    global AMP_MEAN
    for amp in [float(x) for x in a.amps.split(",")]:
        AMP_MEAN = amp
        for wi, w in enumerate(worlds):
            rng = np.random.default_rng(2000 + wi + int(amp * 1000))
            reps = []
            for rep in range(a.reps):
                res = {}
                for d, units in sk.items():
                    if d == "T51":
                        continue
                    uu = draw_units(w, units, cal_all[units[0]["regime"]], rng)
                    res[d] = L.analyze_kickoff(uu, n_boot=a.boot, seed=rep)
                reps.append(card_level(res))
            summ = {}
            for kk in reps[0]:
                v = np.array([r[kk] for r in reps], dtype=float)
                summ[kk] = float(np.nanmean(v)) if kk.startswith(("P1", "P2", "P3", "P4", "kill")) else float(np.nanmedian(v))
            out[f"{w}|{amp}"] = summ
            print(f"amp {amp} {w:8s} meta s {summ['s']:+.2f} P1 {summ['P1']:.2f} | POOL {summ['s_pool']:+.2f} [{summ['s_pool_lo']:+.2f},{summ['s_pool_hi']:+.2f}] "
                  f"P1p {summ['P1_pool']:.2f} killp {summ['kill_pool']:.2f} | CR {summ['CR_med']:.2f} P2 {summ['P2']:.2f} | dSSE(t0) P3 {summ['P3']:.2f} | "
                  f"dSSE_ro {summ['dsse_ro']:+.3f} +{summ['P3_ro']:.2f} -{summ['P3_ro_neg']:.2f} | imm_ro {summ['imm_ro']:.2f} s_ro {summ['s_ro']:+.2f} P4 {summ['P4']:.2f} | "
                  f"rise {summ['rise_share']:.2f} [{time.time() - t0:.0f}s]", flush=True)
    (L.DATA / "synthetic").mkdir(parents=True, exist_ok=True)
    tag = "_ampfixed" if a.amp_fixed else ""
    (L.DATA / f"synthetic/results_{a.cfg}{tag}.json").write_text(json.dumps({"reps": a.reps, "amp_free": L.AMP_FREE, "worlds": out}, indent=1))


if __name__ == "__main__":
    main()
