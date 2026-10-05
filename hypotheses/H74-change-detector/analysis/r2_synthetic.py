"""H74 round 2 synthetic validation (card: Round 2, P3.0 and P2.0). 100 worlds each, on the real skeleton.

(a) D counters (R3): the real 282-day sequence; each feature = the real rolling median (9 scored days) + day noise
    block-bootstrapped (blocks of 5) from the feature's real residuals on days >= 2 active days from every catalogued
    event, so the real tails are kept. 12 planted steps per world (bookends, nudges, human messages, window length,
    joint silence), each held for up to 15 days. Scores G (round-1 Gaussian z, raw), L (log + Gaussian), Q (log +
    empirical quantiles, 30 days); channel D = max over the six features; LOPO conformal thresholds (alpha 0.02) on the
    real P2 days that stay clean.
(b) Presence rule (R2): the real search-day skeleton (answers and agents per day); 12 markers with baseline shares
    U(0.05, 0.9), a logit random walk (0.03/day) and beta-binomial day noise at the real day-to-day overdispersion of
    marker presence; 6 planted retirements (share -> 0) and 6 halvings per world.
Run: uv run python hypotheses/H74-change-detector/analysis/r2_synthetic.py [--worlds 100]
Outputs: data/processed/H74-change-detector/r2/synthetic_D.json, synthetic_presence.json
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h74lib as L  # noqa: E402
import r2lib as R  # noqa: E402
from r2_common import MARKERS, load_frame, marker_day_table  # noqa: E402

ROOT = HERE.parents[2]
OUT = ROOT / "data/processed/H74-change-detector/r2"
STEPS = ["bookends", "nudges", "human", "window", "js"]
D3 = ["n_bookends", "n_nudges", "n_human"]
# pre-registered G, L, Q (six features, one day) and the amendment candidates (after the first synthetic pass):
# counters only (D3) and/or a two-day persistence score (min of day t-1 and day t, dated t)
VARIANTS = {"G": ("G", R.D2_FEATURES, False), "L": ("L", R.D2_FEATURES, False), "Q": ("Q", R.D2_FEATURES, False),
            "Q_D3": ("Q", D3, False), "Q_p2": ("Q", R.D2_FEATURES, True), "Q_D3_p2": ("Q", D3, True),
            "L_D3_p2": ("L", D3, True), "G_D3_p2": ("G", D3, True)}
STEP_FEAT = {"bookends": "n_bookends", "nudges": "n_nudges", "human": "n_human", "window": "window_min", "js": "js_share"}


def rolling_median(x: np.ndarray, w: int = 9) -> np.ndarray:
    out = np.full(x.size, np.nan)
    h = w // 2
    for t in range(x.size):
        if np.isfinite(x[t]):
            seg = x[max(0, t - h):t + h + 1]
            seg = seg[np.isfinite(seg)]
            out[t] = np.median(seg)
    return out


def skeleton_D():
    fr = load_frame()
    df = pl.read_parquet(ROOT / "data/processed/H74-change-detector/day_features.parquet")
    df = pl.DataFrame({"pt_date": fr.dl}).join(df, on="pt_date", how="left")
    quiet = fr.dist >= 2
    sk = {"period": fr.period, "P2": fr.P2, "T": fr.T, "eligible": fr.eligible, "feat": {}}
    for f in R.D2_FEATURES:
        raw = df[f].cast(pl.Float64).fill_null(np.nan).to_numpy()
        x = R.transform(f, raw)
        lev = rolling_median(x)
        res = (x - lev)[quiet & np.isfinite(x)]
        sk["feat"][f] = {"level": lev, "res": res, "nan": ~np.isfinite(x)}
    return sk


def inv(f, x):
    t = R.TRANSFORM.get(f)
    if t == "log1p":
        return np.round(np.expm1(np.clip(x, 0, None)))
    if t == "log":
        return np.exp(x)
    if f == "js_share":
        return np.clip(x, 0, 1)
    return x


def world_D(args):
    seed, sk = args
    rng = np.random.default_rng(seed)
    T = sk["T"]
    # planted steps
    # planted days avoid the real P2 days (>= 2 days away), so the calibration pool stays clean (as in the real data,
    # where P2 days are >= 2 days from every catalogued event)
    p2 = np.where(sk["P2"])[0]
    far_p2 = np.array([np.min(np.abs(p2 - t)) >= 2 for t in range(T)])
    cand = np.where(sk["eligible"] & (np.arange(T) >= 15) & far_p2)[0]
    chosen = []
    for d in rng.permutation(cand):
        if all(abs(d - c) >= 10 for c in chosen):
            chosen.append(int(d))
        if len(chosen) == 12:
            break
    chosen.sort()
    types = [STEPS[i % 5] for i in rng.permutation(len(chosen))]
    raw = {}
    for f in R.D2_FEATURES:
        s = sk["feat"][f]
        r = s["res"]
        starts = rng.integers(0, max(1, r.size - 5), T // 5 + 2)
        noise = np.concatenate([r[a:a + 5] for a in starts])[:T]
        x = s["level"] + noise
        x[s["nan"]] = np.nan
        raw[f] = x
    spans = []
    for j, (d, ty) in enumerate(zip(chosen, types)):
        nxt = chosen[j + 1] if j + 1 < len(chosen) else T
        nxt_p2 = p2[p2 > d]
        Lh = max(1, min(15, nxt - d - 3, (int(nxt_p2[0]) - d - 2) if nxt_p2.size else 15))
        sl = slice(d, d + Lh)
        f = STEP_FEAT[ty]
        x = raw[f]
        lev = sk["feat"][f]["level"][d]
        if ty == "bookends":
            x[sl] = 0.0 if lev > 0.5 else np.log1p(2)
        elif ty == "nudges":
            x[sl] = 0.0 if lev > np.log1p(2) else np.log1p(20)
        elif ty == "human":
            fac = 0.03 if lev > np.log1p(10) else 30.0
            x[sl] = np.log1p(np.expm1(np.clip(x[sl], 0, None)) * fac)
        elif ty == "window":
            x[sl] = x[sl] + np.log(0.75)
        elif ty == "js":
            x[sl] = x[sl] + 0.3
        spans.append((d, d + Lh, ty))
    rawv = {f: inv(f, raw[f]) for f in R.D2_FEATURES}
    clean = sk["P2"].copy()
    for a, b, _ in spans:
        clean[max(0, a - 1):min(T, b + 2)] = False
    out = {"n_clean": int(clean.sum())}
    for kind in VARIANTS:
        base, fset, persist = VARIANTS[kind]
        fs = R.feature_scores({f: rawv[f] for f in fset}, base, floors_g=L.FLOOR)
        if persist:
            fs = {f: R.persist2(v) for f, v in fs.items()}
        D, _ = R.nanmax_stack(fs)
        nominal = np.where(np.isfinite(D), D >= 4, False)
        alarm, th = R.lopo_alarm(D, sk["period"], clean)
        rec = {"far_nominal": float(nominal[clean].mean()), "far_lopo": float(alarm[clean].mean()),
               "th_median": float(np.nanmedian(th[np.isfinite(th)])) if np.isfinite(th).any() else None, "hits": {}}
        for a, b, ty in spans:
            w = slice(max(0, a - 1), a + 2)
            rec["hits"].setdefault(ty, []).append(bool(alarm[w].any()))
            rec["hits"].setdefault(ty + "_nominal", []).append(bool(nominal[w].any()))
        out[kind] = rec
    return out


def presence_skeleton():
    tab, n, nag, _ = marker_day_table()
    # real day-to-day overdispersion of marker presence (from day-to-day differences, which remove slow drift)
    rhos = []
    sc = n >= 3
    for m in MARKERS:
        k = tab[m]
        p = np.where(sc, k / np.maximum(n, 1), np.nan)[sc]
        nn = n[sc]
        pbar = np.nanmean(p)
        if not (0.05 < pbar < 0.9):
            continue
        dv = np.nanvar(np.diff(p)) / 2
        binom = np.mean(pbar * (1 - pbar) / nn)
        denom = pbar * (1 - pbar) * np.mean((nn - 1) / nn)
        rhos.append(max(0.0, (dv - binom) / denom))
    return {"n": n, "nag": nag, "rho": float(np.median(rhos)) if rhos else 0.05, "rhos": [float(r) for r in rhos]}


def world_P(args):
    seed, sk = args
    rng = np.random.default_rng(seed)
    n, nag, rho = sk["n"], sk["nag"], max(sk["rho"], 1e-3)
    T = n.size
    M = 12
    s0 = rng.uniform(0.05, 0.9, M)
    sc = np.where(n >= 3)[0]
    cand = sc[12:]
    days = []
    for d in rng.permutation(cand):
        if all(abs(np.searchsorted(sc, d) - np.searchsorted(sc, c)) >= 5 for c in days):
            days.append(int(d))
        if len(days) == 12:
            break
    mk = rng.permutation(M)
    retire = dict(zip(mk[:6], days[:6]))
    halve = dict(zip(mk[6:12], days[6:12]))
    logit = np.log(s0 / (1 - s0))
    kappa = 1 / rho - 1
    K = np.zeros((M, T), int)
    for t in range(T):
        logit = logit + rng.normal(0, 0.03, M)
        s = 1 / (1 + np.exp(-logit))
        for m in range(M):
            if m in retire and t >= retire[m]:
                s[m] = 0.0
            elif m in halve and t >= halve[m]:
                s[m] = s[m] * 0.5
        if n[t] == 0:
            continue
        a, b = np.clip(s * kappa, 1e-6, None), np.clip((1 - s) * kappa, 1e-6, None)
        p = np.where(s > 0, rng.beta(a, b), 0.0)
        K[:, t] = rng.binomial(n[t], p)
    pos = {d: j for j, d in enumerate(sc)}
    out = {}
    for rule in ("pre", "acc"):
        alarms = np.zeros((M, T), bool)
        for m in range(M):
            alarms[m] = R.presence_retire(n, K[m]) if rule == "pre" else R.presence_retire_acc(n, K[m], sk["rho"])
        out[rule] = _score_presence(alarms, retire, halve, s0, sc, pos)
    return out


def _score_presence(alarms, retire, halve, s0, sc, pos):

    def near(t, d):
        return t in pos and d in pos and abs(pos[t] - pos[d]) <= 1

    hits = []
    for m, d in retire.items():
        hit = any(alarms[m, t] for t in sc if near(t, d))
        later = [pos[t] - pos[d] for t in sc if alarms[m, t] and pos[t] >= pos[d] - 1]
        hits.append({"s0": float(s0[m]), "hit": bool(hit), "delay": (min(later) if later else None)})
    halv = [bool(any(alarms[m, t] for t in sc if near(t, d))) for m, d in halve.items()]
    any_alarm = alarms.any(0)
    excl = set()
    for d in list(retire.values()) + list(halve.values()):
        j = pos[d]
        excl.update(sc[max(0, j - 1):j + 2].tolist())
    clean = [t for t in sc[10:] if t not in excl]
    return {"hits": hits, "halving_alarm": halv, "far": float(np.mean([any_alarm[t] for t in clean])), "n_clean": len(clean)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", type=int, default=100)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    skD = skeleton_D()
    with ProcessPoolExecutor(2) as ex:
        resD = list(ex.map(world_D, [(1000 + i, skD) for i in range(a.worlds)]))
    summ = {"worlds": a.worlds, "n_clean_median": float(np.median([r["n_clean"] for r in resD]))}
    for kind in VARIANTS:
        fn = np.array([r[kind]["far_nominal"] for r in resD]); fl = np.array([r[kind]["far_lopo"] for r in resD])
        hits = {}
        for ty in STEPS + [s + "_nominal" for s in STEPS]:
            v = [h for r in resD for h in r[kind]["hits"].get(ty, [])]
            hits[ty] = {"hit": float(np.mean(v)) if v else None, "n": len(v)}
        summ[kind] = {"far_nominal_mean": float(fn.mean()), "far_nominal_p5_p95": [float(np.percentile(fn, 5)), float(np.percentile(fn, 95))],
                      "far_lopo_mean": float(fl.mean()), "far_lopo_p5_p95": [float(np.percentile(fl, 5)), float(np.percentile(fl, 95))],
                      "th_median": float(np.median([r[kind]["th_median"] for r in resD if r[kind]["th_median"] is not None])),
                      "hits": hits}
    (OUT / "synthetic_D.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))
    skP = presence_skeleton()
    with ProcessPoolExecutor(2) as ex:
        resP = list(ex.map(world_P, [(5000 + i, skP) for i in range(a.worlds)]))
    sp = {"worlds": a.worlds, "rho_median": skP["rho"], "rhos": skP["rhos"]}
    for rule in ("pre", "acc"):
        hits = [h for r in resP for h in r[rule]["hits"]]
        s0 = np.array([h["s0"] for h in hits]); hh = np.array([h["hit"] for h in hits])
        dl = np.array([h["delay"] if h["delay"] is not None else 99 for h in hits])
        far = np.array([r[rule]["far"] for r in resP])
        sp[rule] = {"hit": float(hh.mean()), "hit_within_5": float(np.mean(dl <= 5)),
                    "hit_by_s0": {f"{lo:.2f}-{hi:.2f}": float(hh[(s0 >= lo) & (s0 < hi)].mean())
                                  for lo, hi in ((0.05, 0.2), (0.2, 0.4), (0.4, 0.9))},
                    "within5_by_s0": {f"{lo:.2f}-{hi:.2f}": float(np.mean(dl[(s0 >= lo) & (s0 < hi)] <= 5))
                                      for lo, hi in ((0.05, 0.2), (0.2, 0.4), (0.4, 0.9))},
                    "far_mean": float(far.mean()), "far_p5_p95": [float(np.percentile(far, 5)), float(np.percentile(far, 95))],
                    "halving_alarm": float(np.mean([x for r in resP for x in r[rule]["halving_alarm"]]))}
    (OUT / "synthetic_presence.json").write_text(json.dumps(sp, indent=1))
    print(json.dumps(sp, indent=1))


if __name__ == "__main__":
    main()
