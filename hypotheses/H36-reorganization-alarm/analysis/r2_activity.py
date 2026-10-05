"""H36 round 2, R3 (2026-10-05): sampling-invariant activity statistics (pre-registered in the card, Round 2).

Z_act_inv: the four activity members (I_act, I_beh, chi_act, C_act; h36lib._act_one) on fixed-size samples. Per day:
the DQ8 all-present window with the stall mask (outages_fixed) removed, cut into non-overlapping blocks of 120 kept
minutes (days with < 120 kept minutes are missing); in each block K = 20 random subsets of n_s = 4 agents (agents
with spin variance in the block; >= 4 needed); 10 independent circular-shift surrogates per subset and block; the
surrogate excess is averaged over subsets and blocks. Then the round-1 trailing z and Z_act_inv = mean of the 4 z.

Readouts: alarm rate (z >= 2) on sampling-change vs other placebo days (PH3 rule), AUC on goal kickoffs (day 0 vs
placebo days), and the decision rule P3.3 (does Z_act_inv >= 2 add hits to C3 at <= +0.02 window FAR?).

Synthetic (--synthetic): the real sequence of present counts n, day lengths T and all-present lengths; independent
kinetic-Ising agents (synthetic.py dynamics, beta J0 0.2, day-level jitter) with beta J0 0.7 planted on 15 random
days per run; old Z_act (full day, all agents) vs Z_act_inv, 20 runs.

Usage: uv run python hypotheses/H36-reorganization-alarm/analysis/r2_activity.py [--synthetic] [--workers 2]
Outputs: data/processed/H36-reorganization-alarm/r2/activity_inv.parquet, activity_inv.json, activity_synthetic.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h36lib as L  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

R2 = L.OUT / "r2"
BLOCK, NS, KSUB, NSURR = 120, 4, 20, 10
SRC = L.OUT / "r1b" / "fixed_bge_restate"


def inv_stats(X: np.ndarray, Bh: np.ndarray, keep: np.ndarray, rng) -> np.ndarray:
    """X: n x T spins, Bh: n x T 0..3, keep: T bool. Returns mean surrogate excess of the 4 members (NaN if none)."""
    idx = np.flatnonzero(keep)
    nb = idx.size // BLOCK
    acc = []
    for b in range(nb):
        cols = idx[b * BLOCK:(b + 1) * BLOCK]
        S, Bb = X[:, cols].astype(float), Bh[:, cols]
        ok = np.flatnonzero(S.std(1) > 0)
        if ok.size < NS:
            continue
        t0 = np.arange(BLOCK)
        for _ in range(KSUB):
            sub = rng.choice(ok, NS, replace=False)
            Ss, Bs = S[sub], Bb[sub]
            obs = L._act_one(Ss, Bs)
            sur = np.empty((NSURR, 4))
            for k in range(NSURR):
                lag = rng.integers(0, BLOCK, size=NS)
                ii = (t0[None, :] + lag[:, None]) % BLOCK
                sur[k] = L._act_one(Ss[np.arange(NS)[:, None], ii], Bs[np.arange(NS)[:, None], ii])
            acc.append(obs - sur.mean(0))
    return np.nanmean(np.array(acc), 0) if acc else np.full(4, np.nan)


def real_worker(p: dict) -> dict:
    rng = np.random.default_rng([L.SEED, int(p["aday"]), 36])
    keep = ~p["stall"] & p["allpres"]
    v = inv_stats(p["X"], p["Bh"], keep, rng)
    out = {"aday": p["aday"], "kept_min": int(keep.sum()), "n_blocks": int(keep.sum() // BLOCK)}
    out.update({s + "_inv": float(x) for s, x in zip(L.ACT_STATS, v)})
    return out


def z_inv(df: pl.DataFrame) -> np.ndarray:
    Z = [L.trailing_z(df[s + "_inv"].to_numpy().astype(float)) for s in L.ACT_STATS]
    with np.errstate(all="ignore"):
        return np.nanmean(np.vstack(Z), 0)


def sampling_change(d: pl.DataFrame) -> np.ndarray:
    """PH3 rule: |dn| >= 2, |d log T| >= log 1.25, or the previous active day held out / a >= 4-day break."""
    n = d["n_present"].to_numpy().astype(float); T = d["T_act"].to_numpy().astype(float)
    aday = d["aday"].to_numpy()
    dn = np.r_[np.nan, np.abs(np.diff(n))]; dT = np.r_[np.nan, np.abs(np.diff(np.log(T)))]
    big = np.r_[False, np.diff(aday) > 1] | (d["gap_days"].to_numpy().astype(float) >= 4)
    return (np.nan_to_num(dn) >= 2) | (np.nan_to_num(dT) >= np.log(1.25)) | big


# ---------------------------------------------------------------------------------------------- synthetic
def sim_day(rng, n, T, J0):
    import synthetic as SY
    h = rng.normal(SY.BASE["h_mu"], SY.BASE["h_sd"], size=n) + rng.normal(0, SY.BASE["jit"], size=n)
    X = SY.sim_activity(rng, h, J0, SY.BASE["K"], T, SY.BASE["b_sd"])
    act = X > 0
    Bh = np.where(act, np.where(rng.random(X.shape) < 0.3, 3, 2), np.where(rng.random(X.shape) < 0.3, 1, 0)).astype(np.int8)
    return X, Bh


def syn_run(args) -> dict:
    run, sk = args
    rng = np.random.default_rng([L.SEED, 3600, run])
    D = len(sk["n"])
    planted = set(rng.choice(np.arange(20, D), 15, replace=False).tolist())
    old, inv = [], []
    for i in range(D):
        n, T, tr = int(sk["n"][i]), int(sk["T"][i]), int(sk["trim"][i])
        X, Bh = sim_day(rng, n, T, 0.7 if i in planted else 0.2)
        a = L.activity_stats(X.astype(float), Bh, rng, n_surr=10)
        old.append([a.get(s, np.nan) for s in L.ACT_STATS])
        keep = np.zeros(T, bool); s0 = (T - min(tr, T)) // 2; keep[s0:s0 + min(tr, T)] = True
        inv.append(inv_stats(X, Bh, keep, rng))
    old, inv = np.array(old), np.array(inv)
    with np.errstate(all="ignore"):
        zo = np.nanmean(np.vstack([L.trailing_z(old[:, j]) for j in range(4)]), 0)
        zi = np.nanmean(np.vstack([L.trailing_z(inv[:, j]) for j in range(4)]), 0)
    return {"zo": zo.tolist(), "zi": zi.tolist(), "planted": sorted(planted)}


def synthetic(workers: int) -> dict:
    d = pl.read_parquet(SRC / "day_stats.parquet").sort("aday")
    sk = {"n": d["n_present"].to_numpy(), "T": d["T_act"].fill_null(120).to_numpy(), "trim": d["trim_min"].fill_null(0).to_numpy()}
    samp = sampling_change(d)
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=min(2, workers)) as ex:
        runs = list(ex.map(syn_run, [(r, sk) for r in range(20)]))
    res = {"runs": len(runs), "sec": time.time() - t0}
    for k in ("zo", "zi"):
        rs, rn, aucs, far = [], [], [], []
        for r in runs:
            z = np.array(r[k], float); pm = np.zeros(z.size, bool); pm[r["planted"]] = True
            near = pm | np.r_[False, pm[:-1]]  # day after a planted day also changes its trailing baseline
            clean = ~near & np.isfinite(z)
            rs.append(np.mean(z[clean & samp] >= 2)); rn.append(np.mean(z[clean & ~samp] >= 2))
            far.append(np.mean(z[clean] >= 2)); aucs.append(L.auc(z[pm], z[clean]))
        res[k] = {"alarm_rate_sampling_change": float(np.mean(rs)), "alarm_rate_other": float(np.mean(rn)),
                  "ratio": float(np.mean(rs) / max(1e-9, np.mean(rn))), "per_day_far": float(np.mean(far)),
                  "auc_planted_coupling_up": float(np.nanmean(aucs))}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    R2.mkdir(parents=True, exist_ok=True)
    if a.synthetic:
        s = synthetic(a.workers)
        (R2 / "activity_synthetic.json").write_text(json.dumps(s, indent=1))
        print(json.dumps(s, indent=1)); return
    import build as B
    B.CFG.update(data_version="fixed", model="bge_small", dedupe="none", trim=True)
    base = pl.read_parquet(SRC / "day_stats.parquet").sort("aday")
    cal = B.calendar()
    days = cal.filter(pl.col("aday").is_in(base["aday"].implode()))
    assert not any(L.holdout_mask(days["pt_date"].to_list(), days["goal_no"].to_list()))
    t0 = time.time()
    pays, *_ = B.make_payloads(days)
    pays = [{k: p[k] for k in ("aday", "X", "Bh", "stall", "allpres")} for p in pays]
    print(f"{len(pays)} payloads ({time.time() - t0:.0f}s)", flush=True)
    with ProcessPoolExecutor(max_workers=min(2, a.workers)) as ex:
        res = list(ex.map(real_worker, pays, chunksize=4))
    inv = pl.DataFrame(res)
    d = base.join(inv, on="aday", how="left").sort("aday")
    zi = z_inv(d)
    sc = pl.read_parquet(SRC / "scores.parquet").sort("aday")
    assert sc["aday"].to_list() == d["aday"].to_list()
    placebo = sc["placebo"].to_numpy(); samp = sampling_change(d)
    za_old = sc["Z_act"].to_numpy().astype(float); za_trim = sc["Z_act_trim"].to_numpy().astype(float)
    ev = pl.read_parquet(SRC / "events.parquet").filter(~pl.col("holdout0") & (pl.col("cls") == "goal"))
    pos = {int(x): i for i, x in enumerate(d["aday"].to_list())}
    aday = d["aday"].to_numpy()
    rng = np.random.default_rng(L.SEED + 36)

    def summary(z, name):
        fin = np.isfinite(z)
        k0 = np.array([z[pos[a]] if a in pos else np.nan for a in ev["aday0"].to_list()])
        pz = z[placebo & fin]
        r = {"auc_d0": L.auc(k0, pz), "auc_d0_ci": L.auc_ci(k0, pz, rng, 1000), "n_kick": int(np.isfinite(k0).sum()),
             "placebo_far_day": float(np.mean(pz >= 2)), "n_placebo": int(pz.size),
             "far_sampling_change_placebo": float(np.mean(z[placebo & fin & samp] >= 2)) if (placebo & fin & samp).any() else None,
             "far_other_placebo": float(np.mean(z[placebo & fin & ~samp] >= 2)),
             "n_sc_placebo": int((placebo & fin & samp).sum()),
             "rate_sampling_change_alldays": float(np.mean(z[fin & samp] >= 2)), "rate_other_alldays": float(np.mean(z[fin & ~samp] >= 2)),
             "n_sc_alldays": int((fin & samp).sum()), "n_other_alldays": int((fin & ~samp).sum())}
        r["ratio_alldays"] = r["rate_sampling_change_alldays"] / max(1e-9, r["rate_other_alldays"])
        from scipy.stats import spearmanr
        n = d["n_present"].to_numpy().astype(float); T = d["T_act"].to_numpy().astype(float)
        dn = np.r_[np.nan, np.abs(np.diff(n))]; dT = np.r_[np.nan, np.abs(np.diff(np.log(T)))]
        ok = fin & np.isfinite(dn) & np.isfinite(dT)
        r["spearman_dn"] = float(spearmanr(z[ok], dn[ok]).statistic); r["spearman_dlogT"] = float(spearmanr(z[ok], dT[ok]).statistic)
        return r

    out = {"Z_act_inv": summary(zi, "inv"), "Z_act_r1b": summary(za_old, "old"), "Z_act_trim_r1b": summary(za_trim, "trim"),
           "n_days_inv": int(np.isfinite(zi).sum())}
    # decision rule P3.3: C3 union Z_act_inv >= 2 vs C3 alone (window -1..+1, round-1b placebo windows)
    c3 = sc["C3"].to_numpy().astype(float)

    def wmax(z, c):
        v = [z[pos[c + o]] for o in (-1, 0, 1) if (c + o) in pos and np.isfinite(z[pos[c + o]])]
        return max(v) if v else np.nan
    union = np.fmax(c3, zi)
    kick = [a for a in ev["aday0"].to_list() if np.isfinite(wmax(c3, a))]
    pc = aday[placebo]
    for nm, z in (("C3", c3), ("C3_or_Zactinv", union)):
        out[nm] = {"hit": float(np.mean([wmax(z, a) >= 2 for a in kick])), "far_win": float(np.mean([np.nan_to_num(wmax(z, c), nan=-9) >= 2 for c in pc])),
                   "n_kick": len(kick), "n_placebo": int(pc.size)}
    out["decision_drop_activity"] = bool((out["Z_act_inv"]["auc_d0_ci"][0] <= 0.5 <= out["Z_act_inv"]["auc_d0_ci"][1]) and
                                         (out["C3_or_Zactinv"]["hit"] - out["C3"]["hit"] < 0.05 or
                                          out["C3_or_Zactinv"]["far_win"] - out["C3"]["far_win"] > 0.02))
    # post hoc (2026-10-05, after the run): the pre-registered placebo ratio is not estimable (no scored sampling-change
    # placebo day), so rates on days >= 2 active days from every catalogued event; and the kickoffs Z_act_inv adds to C3
    allev = pl.read_parquet(SRC / "allevents.parquet")
    evd = np.unique(allev["aday0"].drop_nulls().to_numpy()); dist = np.array([np.min(np.abs(evd - x)) for x in aday])
    ph = {}
    for nm, z in (("Z_act_inv", zi), ("Z_act_r1b", za_old), ("Z_act_trim_r1b", za_trim)):
        f = np.isfinite(z) & (dist >= 2)
        ph[nm] = {"rate_sampling_change": float(np.mean(z[f & samp] >= 2)) if (f & samp).any() else None, "n_sc": int((f & samp).sum()),
                  "rate_other": float(np.mean(z[f & ~samp] >= 2)), "n_other": int((f & ~samp).sum())}
    added = []
    for r in ev.iter_rows(named=True):
        c = r["aday0"]
        if np.nan_to_num(wmax(union, c), nan=-9) >= 2 and not np.nan_to_num(wmax(c3, c), nan=-9) >= 2:
            added.append({"ref": r["ref"], "pt_date0": r["pt_date0"], "same_day": r["all_refs_same_day"],
                          "sampling_change_in_window": any(bool(samp[pos[c + o]]) for o in (-1, 0, 1) if (c + o) in pos)})
    ph["added_kickoffs"] = added
    out["posthoc"] = ph
    d.select("aday", "pt_date", "goal_no", "regime", "n_present", "T_act", "kept_min", "n_blocks",
             *[s + "_inv" for s in L.ACT_STATS]).with_columns(pl.Series("Z_act_inv", zi), pl.Series("sampling_change", samp)) \
        .write_parquet(R2 / "activity_inv.parquet", compression="zstd")
    (R2 / "activity_inv.json").write_text(json.dumps(out, indent=1))
    L.write_provenance("hypotheses/H36-reorganization-alarm/analysis/r2_activity.py",
                       ["activity_bins_fixed", "outages_fixed/outages", "calendar", "(r1b day_stats, scores, events)"],
                       {"block_min": BLOCK, "n_sub": NS, "k_sub": KSUB, "n_surr": NSURR}, path=R2 / "_provenance.json")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
