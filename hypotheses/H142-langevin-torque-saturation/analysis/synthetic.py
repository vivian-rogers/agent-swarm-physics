"""H142 synthetic validation on real skeletons (axis F; runs before any real-data step statistic).

Skeleton (real, structural): every scored talk call of the period with its real batch, in-flight set, aligned counts
n_cu / nF_cu, newest and named indicators, rooms, hours, agents, days, the day-fold centroids u_hat, and the real
projected batch vectors x_perp (bge). The real step y_cu is never read (the `y` column is dropped on load); only the
period mean of |y_perp|^2 is used to calibrate the noise. Synthetic reader statements (32-d):
  Y_c = A_w * s_w(c) + e_c,   e_c ~ N(0, sigma^2 I_32),   sigma^2 = (mean|y_perp|^2 - E_lin) / 32
  W0       s = 0 (no coupling)
  W-lin    s = k^-0.75 * sum_{m in B_c} x_m                (H113's channel, b = 0.75, gamma_1 = 0.15)
  W-sel    s = x_J, J one batch item at random              (H113-R2)
  W-L1/L3  s = sum_u L(c n_cu) u_hat_u, c = 3 / n_sat        (n_sat = 1, 3)
  W-pow    s = sum_u n_cu^0.3 u_hat_u
  W-recent s = x_newest
  W-field  s = sum_u theta_{room,u}(t) u_hat_u: a hot-topic field with no read uptake. theta = (i) a two-sided
           exponential (tau = 30 min) rate of the room's own statements labelled u (all statements, read or not)
           plus (ii) an independent room x topic OU random walk (tau = 30 min), equal energy.
Amplitudes: every world except W0 has the same directional signal energy (the within-call variance of the signal's
projections on the K directions, which the call FE leaves) as W-lin with gamma_1 = 0.15 (calibrated to H113's measured
per-message uptake); W-field has 4x that (a strong field) and W-field1 1x (fixed before running). An 'amp3' set repeats W-L3 at
3x amplitude to show the power curve.
Decision rules (card, fixed before data): O3 prefers Langevin (ΔLL(L - lin) CI > 0) in >= 80% of W-L3 runs and <= 10%
of W-lin and W-sel runs; Δ_curv false '> 0' rate <= 0.10 in W-pow, W-lin, W-recent; W-field f(n) CI includes 0 at
every n in >= 90% of runs. Power at each period's real counts = the W-L3 pass rate on that period's own skeleton.

Usage: uv run python hypotheses/H142-langevin-torque-saturation/analysis/synthetic.py --set main|power [--runs 100]
Output: data/processed/H142-langevin-torque-saturation/synthetic/{runs_<set>.parquet, summary_<set>.json}
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h142lib as L  # noqa: E402

ROOT = HERE.parents[2]
DATA = ROOT / "data/processed/H142-langevin-torque-saturation"
OUT = DATA / "synthetic"
G1, B_LIN = 0.15, 0.75
TAU_US = 30 * 60 * 1_000_000
FIELD_X = 4.0
MAIN_WORLDS = ["W0", "W-lin", "W-sel", "W-L1", "W-L3", "W-pow", "W-recent", "W-field", "W-field1"]
MAIN_SKELETONS = [(13, "bge_small"), (38, "bge_small"), (51, "bge_small")]
POWER_SKELETONS = [(g, m) for g in (13, 16, 35, 36, 37, 38, 39, 40, 41, 51) for m in ("bge_small", "gte_modernbert")] + \
                  [(51, "wake_bge_small"), (51, "wake_gte_modernbert")]


class Skeleton:
    def __init__(self, g: int, tag: str, pooled: bool = False):
        d = DATA / f"G{g:02d}"
        self.g, self.tag = g, tag
        rows = pl.read_parquet(d / f"rows_{tag}.parquet").drop("y")      # the real step is never read
        self.rows = rows
        calls = pl.read_parquet(d / f"calls_{tag}.parquet")
        self.n_calls = len(calls)
        self.K = int(rows["u"].max()) + 1
        self.mean_yy = float(calls["yy"].mean())                         # calibration only
        self.k = calls["k"].to_numpy()
        self.t = calls["t_post_us"].to_numpy(); self.room = calls["room"].to_numpy()
        cz = np.load(d / f"centroids_{tag.replace('wake_', '')}.npz")
        dpos = {str(x): i for i, x in enumerate(cz["days"])}
        self.Cday = cz["C"][[dpos[x] for x in calls["pt_date"].to_list()]]   # (n_calls, K, 32)
        self.nmat = rows["n"].to_numpy().reshape(self.n_calls, self.K)
        it = pl.read_parquet(d / f"items_{tag}.parquet")
        self.it_call = it["call"].to_numpy(); self.it_rank = it["rank"].to_numpy()
        base = tag.replace("gte_modernbert", "bge_small")
        xb_path = d / f"xb_{base}.npy"
        # x vectors only exist for bge; gte skeletons use bge's energy calibration and the label-based worlds only
        self.XB = np.load(xb_path).astype(np.float64) if tag == base else None
        if self.XB is not None:
            order = np.lexsort((self.it_rank, self.it_call))
            first = order[np.r_[True, np.diff(self.it_call[order]) != 0]] if len(order) else order
            self.newest_idx = np.full(self.n_calls, -1); self.newest_idx[self.it_call[first]] = first
        self.D = L.Design(rows)
        self.Dp = L.Design(rows, amplitude="pooled") if pooled else None
        self.ml_path = d / f"msglabels_{base.replace('wake_', '')}.parquet"

    def lin_signal(self) -> np.ndarray:
        S = np.zeros((self.n_calls, 32))
        np.add.at(S, self.it_call, self.XB)
        kk = np.maximum(self.k, 1).astype(float)
        return G1 * kk[:, None] ** (-B_LIN) * S

    def dir_signal(self, w: np.ndarray) -> np.ndarray:
        """sum_u w[c, u] u_hat_u (w: n_calls x K)."""
        return np.einsum("ck,ckd->cd", w, self.Cday)

    def field_counts(self) -> np.ndarray:
        ml = pl.read_parquet(self.ml_path).filter(pl.col("lab") >= 0)
        th = np.zeros((self.n_calls, self.K))
        for room in np.unique(self.room):
            m = ml.filter(pl.col("room") == int(room))
            tm = m["t_us"].to_numpy(); lab = m["lab"].to_numpy()
            ci = np.flatnonzero(self.room == room)
            for c in ci:
                lo = np.searchsorted(tm, self.t[c] - 4 * TAU_US); hi = np.searchsorted(tm, self.t[c] + 4 * TAU_US)
                if hi > lo:
                    w = np.exp(-np.abs(tm[lo:hi] - self.t[c]) / TAU_US)
                    np.add.at(th[c], lab[lo:hi], w)
        return th - th.mean(1, keepdims=True) * 0      # raw rates (call FE removes the call mean anyway)

    def field_ou(self, rng) -> np.ndarray:
        th = np.zeros((self.n_calls, self.K))
        for room in np.unique(self.room):
            ci = np.flatnonzero(self.room == room)
            ci = ci[np.argsort(self.t[ci])]
            cur = rng.normal(0, 1, self.K); tp = None
            for c in ci:
                if tp is not None:
                    r = np.exp(-max(self.t[c] - tp, 0) / TAU_US)
                    cur = r * cur + np.sqrt(1 - r * r) * rng.normal(0, 1, self.K)
                th[c] = cur; tp = self.t[c]
        return th


def energy(S: np.ndarray) -> float:
    return float((S ** 2).sum(1).mean())


def dir_energy(sk: "Skeleton", S: np.ndarray) -> float:
    """Mean within-call variance of the signal's projections on the K directions (what the call FE leaves)."""
    P = np.einsum("cd,ckd->ck", S, sk.Cday)
    return float(((P - P.mean(1, keepdims=True)) ** 2).sum(1).mean())


def world_signal(sk: Skeleton, w: str, rng, cache: dict) -> np.ndarray:
    if w == "W0":
        return np.zeros((sk.n_calls, 32))
    if w == "W-lin":
        return cache["lin"]
    if w == "W-sel":
        S = np.zeros((sk.n_calls, 32))
        has = np.flatnonzero(sk.k >= 1)
        # one random batch item per call
        starts = np.r_[0, np.cumsum(np.bincount(sk.it_call, minlength=sk.n_calls))]
        pick = starts[has] + (rng.random(len(has)) * (starts[has + 1] - starts[has])).astype(int)
        order = np.argsort(sk.it_call, kind="stable")
        S[has] = sk.XB[order[pick]]
        return S
    if w == "W-recent":
        S = np.zeros((sk.n_calls, 32)); h = sk.newest_idx >= 0
        S[h] = sk.XB[sk.newest_idx[h]]
        return S
    if w in ("W-L1", "W-L3", "W-L3x3"):
        ns = 1.0 if w == "W-L1" else 3.0
        return sk.dir_signal(L.langevin((3.0 / ns) * sk.nmat))
    if w == "W-pow":
        return sk.dir_signal(sk.nmat.astype(float) ** 0.3)
    if w in ("W-field", "W-field1"):
        a = sk.dir_signal(cache["fc"]); b = sk.dir_signal(sk.field_ou(rng))
        a *= np.sqrt(1.0 / max(energy(a), 1e-12)); b *= np.sqrt(1.0 / max(energy(b), 1e-12))
        return a + b
    raise ValueError(w)


def run_one(sk: Skeleton, w: str, seed: int, cache: dict, B: int = 300) -> dict:
    rng = np.random.default_rng(seed)
    S = world_signal(sk, w, rng, cache)
    e_lin = cache["e_lin"]
    if w != "W0":
        # amplitude: the directional energy (within-call variance across the K directions) equals W-lin's
        target = cache["d_lin"] * (FIELD_X if w == "W-field" else 9.0 if w == "W-L3x3" else 1.0)   # amplitude x3 = energy x9
        S = S * np.sqrt(target / max(dir_energy(sk, S), 1e-12))
    sig2 = max(sk.mean_yy - e_lin, 0.1 * sk.mean_yy) / 32
    Y = S + rng.normal(0, np.sqrt(sig2), S.shape)
    y = np.einsum("cd,ckd->ck", Y, sk.Cday).ravel()
    st = sk.D.y_stats(y)
    ll = L.oof_loglik(sk.D, st)
    row = {"period": sk.g, "tag": sk.tag, "world": w, "seed": seed}
    for a, b in (("langevin", "linear"), ("langevin", "power"), ("power", "linear"), ("dummies", "linear")):
        dd = L.dll_summary(ll, a, b, B=1000, seed=seed)
        row[f"dll_{a[:3]}_{b[:3]}"] = dd["dll"]; row[f"dll_{a[:3]}_{b[:3]}_lo"] = dd["lo"]; row[f"dll_{a[:3]}_{b[:3]}_hi"] = dd["hi"]
    if sk.Dp is not None:      # the card's original pooled-amplitude form (pre-A1)
        st2 = sk.Dp.y_stats(y); ll2 = L.oof_loglik(sk.Dp, st2)
        dd = L.dll_summary(ll2, "langevin", "linear", B=1000, seed=seed)
        row["pooled_dll_lan_lin"] = dd["dll"]; row["pooled_dll_lan_lin_lo"] = dd["lo"]; row["pooled_dll_lan_lin_hi"] = dd["hi"]
    ff = L.fit_dummies(sk.D, st, B=B, seed=seed)
    for nm, v in ff["f"].items():
        row[f"f_{nm}"] = v["est"]; row[f"f_{nm}_lo"] = v["lo"]; row[f"f_{nm}_hi"] = v["hi"]
    row["any_f_excl0"] = any((v["lo"] > 0) or (v["hi"] < 0) for v in ff["f"].values())
    dc = ff["dcurv"]
    row["dcurv"] = dc["est"]; row["dcurv_lo"] = dc["lo"]; row["dcurv_hi"] = dc["hi"]; row["dcurv_valid"] = dc["valid_share"]
    fday = L.fit_dummies(sk.D, st, B=B, seed=seed, cluster="day")
    row["any_f_excl0_day"] = any((v["lo"] > 0) or (v["hi"] < 0) for v in fday["f"].values())
    row["dcurv_lo_day"] = fday["dcurv"]["lo"]
    inf = ff.get("inflight")
    row["contrast1_lo"] = inf["contrast_lo"] if inf else None; row["contrast1"] = inf["contrast"] if inf else None
    fp = L.fit_profiles(sk.D, st, boot=False)
    row["nsat"] = fp["langevin"]["nsat"]; row["pow_p"] = fp["power"]["theta"]
    return row


def summarize(df: pl.DataFrame) -> dict:
    out = {}
    for (g, tag, w), d in df.group_by(["period", "tag", "world"], maintain_order=True):
        s = {"runs": len(d),
             "prefer_L_over_lin": float((d["dll_lan_lin_lo"] > 0).mean()),
             "prefer_L_over_pow": float((d["dll_lan_pow_lo"] > 0).mean()),
             "prefer_pow_over_lin": float((d["dll_pow_lin_lo"] > 0).mean()),
             "dll_L_lin_med": float(d["dll_lan_lin"].median()),
             "dcurv_gt0": float((d["dcurv_lo"].fill_null(-1e9) > 0).mean()),
             "contrast1_gt0": float((d["contrast1_lo"].fill_null(-1e9) > 0).mean()) if "contrast1_lo" in d.columns else None,
             "dcurv_med": d["dcurv"].fill_nan(None).median(),
             "any_f_excl0": float(d["any_f_excl0"].mean()),
             "all_f_incl0": float((~d["any_f_excl0"]).mean()),
             "all_f_incl0_day": float((~d["any_f_excl0_day"]).mean()),
             "dcurv_gt0_day": float((d["dcurv_lo_day"].fill_null(-1e9) > 0).mean()),
             "pooled_prefer_L_over_lin": float((d["pooled_dll_lan_lin_lo"] > 0).mean()) if "pooled_dll_lan_lin_lo" in d.columns else None,
             "nsat_med": float(d["nsat"].median()), "nsat_q25": float(d["nsat"].quantile(0.25)),
             "nsat_q75": float(d["nsat"].quantile(0.75)), "pow_p_med": float(d["pow_p"].median())}
        for nm in L.BIN_NAMES:
            if f"f_{nm}" in d.columns:
                s[f"f_{nm}_med"] = d[f"f_{nm}"].median()
        out[f"G{g}|{tag}|{w}"] = s
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", choices=["main", "power"], default="main")
    ap.add_argument("--runs", type=int, default=100)
    ap.add_argument("--B", type=int, default=300)
    ap.add_argument("--worlds", default=None, help="comma list (test runs only)")
    ap.add_argument("--period", type=int, action="append", help="test runs only")
    ap.add_argument("--tag", default="", help="suffix for output files")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if a.set == "main":
        jobs = [(g, t, MAIN_WORLDS + ["W-L3x3"]) for g, t in MAIN_SKELETONS]
    else:
        jobs = [(g, t, ["W-L3", "W-lin", "W-L3x3"]) for g, t in POWER_SKELETONS if (g, t) not in MAIN_SKELETONS]
    if a.period:
        jobs = [j for j in jobs if j[0] in a.period]
    if a.worlds:
        jobs = [(g, t, a.worlds.split(",")) for g, t, _ in jobs]
    a.set_out = a.set + a.tag
    rows = []
    e_lin_bge = {}
    for g, tag, worlds in jobs:
        t0 = time.time()
        sk = Skeleton(g, tag, pooled=(a.set == "main"))
        cache = {}
        if sk.XB is not None:
            cache["lin"] = sk.lin_signal(); cache["e_lin"] = energy(cache["lin"]); cache["d_lin"] = dir_energy(sk, cache["lin"])
            e_lin_bge[(g, "wake" in tag)] = (cache["e_lin"], cache["d_lin"])
        else:
            key = (g, "wake" in tag)
            if key not in e_lin_bge:
                bsk = Skeleton(g, tag.replace("gte_modernbert", "bge_small"))
                del bsk.D
                ls = bsk.lin_signal()
                e_lin_bge[key] = (energy(ls), dir_energy(bsk, ls))
            cache["e_lin"], cache["d_lin"] = e_lin_bge[key]
            worlds = [w for w in worlds if w not in ("W-lin", "W-sel", "W-recent")]
        if "W-field" in worlds or "W-field1" in worlds:
            cache["fc"] = sk.field_counts()
        print(f"G{g} {tag}: calls {sk.n_calls} rows {len(sk.rows)} n>=4 {(sk.nmat >= 4).sum()} e_lin {cache['e_lin']:.4f} d_lin {cache['d_lin']:.5f} "
              f"mean_yy {sk.mean_yy:.3f} setup {time.time() - t0:.0f}s", flush=True)
        for w in worlds:
            t1 = time.time()
            nr = a.runs if w != "W-L3x3" else max(a.runs // 2, 20)
            for s in range(nr):
                rows.append(run_one(sk, w, 10_000 * g + 100 * MAIN_WORLDS.index(w) + s if w in MAIN_WORLDS else 10_000 * g + 999 + s,
                                    cache, B=a.B))
            print(f"  {w}: {nr} runs {time.time() - t1:.0f}s", flush=True)
            pl.DataFrame(rows).write_parquet(OUT / f"runs_{a.set_out}.parquet")
    df = pl.DataFrame(rows)
    df.write_parquet(OUT / f"runs_{a.set_out}.parquet")
    summ = summarize(df)
    (OUT / f"summary_{a.set_out}.json").write_text(json.dumps(summ, indent=1, default=float))
    for k, v in summ.items():
        print(k, json.dumps({kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in v.items()}))


if __name__ == "__main__":
    main()
