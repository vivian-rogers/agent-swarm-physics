"""H125 synthetic validation on the real skeleton (axis F), run before any real-data statistic along a kickoff direction.

Each world plants a per-statement excess alignment a = b_i + f(h) + profile(slot) + u_{i,day} + v_{i,window} + e at the
real statement times, agents, active-hour clocks and slots of the 27 eligible kickoffs (post-t0 statements, all days, so
the long periods also carry placebo origins). Noise components come from calibrate.py (decoy directions only).
Worlds: W_fade (tau 3, 8 h), W_drift, W_tod (time-of-day profile), W_rekick (day-4 operator re-kick), W_noisy (day noise
x2), W_osc (zeta 0.2, 0.5; trough at the day 2/3 boundary), W_osc_weak (amplitude 0.06, zeta 0.5).
The card-level rules P1 (meta U 90% CI > 0 and Mann-Whitney kickoff U > placebo U, p < 0.05), P2 (M_osc wins in >= 2/3,
sign p < 0.05), S1 (E1 meta CI > 0) and the zeta estimates are applied exactly as on real data.
Writes data/processed/H125-kickoff-damped-oscillator/synthetic/results.json.
Usage: uv run python hypotheses/H125-kickoff-damped-oscillator/analysis/synthetic.py [--reps 40]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import mannwhitneyu

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h125lib as L  # noqa: E402

Z90 = 1.645
AMP = 0.12   # H97's overshoot intercept a_K (bge), same linear units


def skeletons():
    k = L.kickoffs().filter(pl.col("kind") == "kickoff")
    out = []
    for kr in k.iter_rows(named=True):
        st = L.stmt(kr["design"]).filter(pl.col("seg") == "post")
        d = st["day_idx"].to_numpy()
        h = st["h"].to_numpy().astype(float)
        h_end1 = float(h[d == 1].max()) if (d == 1).any() else kr["day_h"][0]
        h_mid23 = h_end1 + kr["day_h"][1]
        h_day4 = float(h[d >= 4].min()) if (d >= 4).any() else np.inf
        out.append(dict(kr=kr, st=st, agent=st["agent"].to_numpy(), day=d, h=h, slot=st["slot"].to_numpy(),
                        win=np.floor(h / 0.5).astype(int), h_mid23=h_mid23, h_day4=h_day4,
                        dhm=float(np.median(kr["day_h"][:5]))))
    return out


def signal(world: str, sk: dict) -> np.ndarray:
    h = sk["h"]
    if world.startswith("W_fade"):
        tau = float(world.split("_")[-1])
        return AMP * np.exp(-h / tau)
    if world == "W_drift":
        return AMP * np.exp(-h / 4) - 0.02 * h / sk["dhm"]
    if world == "W_tod":
        prof = np.array([0.03, 0.0, -0.01, -0.02])
        return AMP * np.exp(-h / 4) + prof[sk["slot"]]
    if world == "W_rekick":
        x = h - sk["h_day4"]
        return AMP * np.exp(-h / 4) + np.where(x >= 0, 0.04 * np.exp(-np.clip(x, 0, None) / 4), 0.0)
    if world == "W_noisy":
        return AMP * np.exp(-h / 4)
    if world.startswith("W_osc"):
        amp = 0.06 if "weak" in world else AMP
        zeta = float(world.split("_")[-1])
        om = np.pi / sk["h_mid23"]
        lam = zeta * om / np.sqrt(1 - zeta ** 2)
        return amp * np.exp(-lam * h) * np.cos(om * h)
    raise ValueError(world)


def draw(world: str, sk: dict, cal: dict, rng) -> np.ndarray:
    c = cal[sk["kr"]["regime"]]
    mult_u = 2.0 if world == "W_noisy" else 1.0
    mult_v = 1.5 if world == "W_noisy" else 1.0
    ag, dy, wn = sk["agent"], sk["day"], sk["win"]
    a = signal(world, sk)
    ua = np.unique(ag)
    b = dict(zip(ua, rng.normal(0, np.sqrt(c["s2_b"]), len(ua))))
    a = a + np.array([b[i] for i in ag])
    kd = ag.astype(np.int64) * 1000 + dy
    u, inv = np.unique(kd, return_inverse=True)
    a = a + rng.normal(0, mult_u * np.sqrt(c["s2_u"]), len(u))[inv]
    kw = ag.astype(np.int64) * 100000 + wn
    u, inv = np.unique(kw, return_inverse=True)
    a = a + rng.normal(0, mult_v * np.sqrt(c["s2_v"]), len(u))[inv]
    a = a + rng.normal(0, np.sqrt(c["s2_e"]), len(a))
    return a


def card_level(res: list[dict]) -> dict:
    U = np.array([r["U"] for r in res]); se = np.array([r["se_U"] for r in res])
    m = L.dl_meta(U, se)
    plc = np.array([u for r in res for u in r["placebo_u"]])
    ok = np.isfinite(U)
    p_mw = float(mannwhitneyu(U[ok], plc[np.isfinite(plc)], alternative="greater").pvalue) if len(plc) >= 3 else np.nan
    E = np.array([r["E1"] for r in res]); seE = np.array([r["se_E1"] for r in res])
    mE = L.dl_meta(E, seE)
    ds = np.array([r["dsse"] for r in res])
    win = np.nanmean(ds > 0)
    zf = np.array([r["zeta_fit"] for r in res])
    return dict(U=m["mean"], U_lo=m["mean"] - Z90 * m["se"], p_mw=p_mw,
                P1=bool(m["mean"] - Z90 * m["se"] > 0 and p_mw < 0.05),
                E1=mE["mean"], S1=bool(mE["mean"] - Z90 * mE["se"] > 0),
                osc_win_share=float(win), P2=bool(win >= 2 / 3 and L.sign_p(ds) < 0.05),
                zeta_fit_med_osc=float(np.nanmedian(zf[ds > 0])) if (ds > 0).any() else np.nan,
                zeta_pk=L.zeta_pk(mE["mean"], m["mean"]),
                n_placebo=int(len(plc)), plc_q95=float(np.nanpercentile(plc, 95)) if len(plc) else np.nan,
                share_kick_supported=float(np.mean([(r["U"] - Z90 * r["se_U"] > 0) and (r["U"] > np.nanpercentile(plc, 95))
                                                    for r in res if np.isfinite(r["U"])])))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=40)
    ap.add_argument("--cfg", default="bge_white")
    a = ap.parse_args()
    cal = json.loads((L.DATA / "synthetic/calibration.json").read_text())[a.cfg]
    sks = skeletons()
    worlds = ["W_fade_3", "W_fade_8", "W_drift", "W_tod", "W_rekick", "W_noisy", "W_osc_0.2", "W_osc_0.5", "W_osc_weak_0.5"]
    cache: dict = {}
    out = {}
    t0 = time.time()
    for wi, w in enumerate(worlds):
        rng = np.random.default_rng(1000 + wi)
        reps = []
        for rep in range(a.reps):
            res = []
            for sk in sks:
                y = draw(w, sk, cal, rng)
                r = L.analyze_kickoff(sk["st"], sk["kr"], y, None, fitter_cache=cache)
                r.pop("_series", None)
                res.append(r)
            reps.append(card_level(res))
        keys = reps[0].keys()
        summ = {}
        for kk in keys:
            v = np.array([r[kk] for r in reps], dtype=float)
            summ[kk] = float(np.nanmean(v)) if kk in ("P1", "P2", "S1") else float(np.nanmedian(v))
        out[w] = summ
        print(f"{w:16s} P1 {summ['P1']:.2f}  U {summ['U']:+.4f}  p_mw {summ['p_mw']:.3f}  P2 {summ['P2']:.2f} win {summ['osc_win_share']:.2f}  "
              f"S1 {summ['S1']:.2f}  E1 {summ['E1']:+.3f}  zfit {summ['zeta_fit_med_osc']:.2f}  zpk {summ['zeta_pk']:.2f}  "
              f"kick-supp {summ['share_kick_supported']:.2f}  [{time.time() - t0:.0f}s]", flush=True)
    (L.DATA / "synthetic").mkdir(parents=True, exist_ok=True)
    (L.DATA / f"synthetic/results_{a.cfg}.json").write_text(json.dumps({"reps": a.reps, "amp": AMP, "worlds": out}, indent=1))


if __name__ == "__main__":
    main()
