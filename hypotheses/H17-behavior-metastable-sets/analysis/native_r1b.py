"""H17 round 1b native tests (layer 2; predictions on the card, "Round 1b", written before running).

N1  NE41 forced erasures as quasi-random kicks (G51 primary, G38 secondary): relaxation of the v3 macro-state vector
    after the first call following a forced erasure vs the MSM's t2*; control = mid-segment calls.
N2  NE43 drive withdrawal inside #51: t2* (shifted, macro states) on A (07-24 -> 08-04), B (08-05 -> 08-20),
    C (08-21 -> 09-02), with agent-day bootstrap CIs; placebo 07-06 -> 07-14 vs 07-15 -> 07-23.
N3  #27 change point: best single split of the 10 days on day-level soft macro transition counts vs day-order permutations.
Writes data/processed/H17-behavior-metastable-sets/r1b/native_r1b.json.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("POLARS_MAX_THREADS", "2")

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h17lib as L  # noqa: E402
import v3lib as V  # noqa: E402
import round1b as RB  # noqa: E402

SH = V.SH
OUT = RB.OUT


def macro_table(goal, days=None):
    v = V.load_v3_table(goals=[goal], days=days)
    P6, names = RB.macro(RB.p12(v))
    return v, P6, names


# ============================================================================ N1
def n1_relaxation(goal, rng, kmax=4, B=200):
    v, P, names = macro_table(goal)
    q = P.shape[1]
    ag = v["agent"].to_numpy()
    dy = v["pt_date"].to_numpy()
    w = v["w"].to_numpy()
    # agent means (stationary reference per agent)
    mu = {a: P[ag == a].mean(0) for a in np.unique(ag)}
    E = P - np.array([mu[a] for a in ag])
    led = (pl.read_parquet(SH / "context_ledger_turns.parquet",
                           columns=["agent", "pt_date", "goal_no", "holdout", "t_call", "reset_consol", "reset_forced", "ctx_pos"])
           .filter((pl.col("goal_no") == goal) & ~pl.col("holdout")).sort("agent", "t_call"))
    # window of each call: join on (agent, pt_date) with t0 <= t_call
    win = v.select(pl.col("agent").cast(pl.Int8), "pt_date", "w", "t0").with_row_index("row").sort("t0")
    led = led.with_columns(pl.col("agent").cast(pl.Int8)).sort("t_call")
    j = led.join_asof(win, left_on="t_call", right_on="t0", by=["agent", "pt_date"], strategy="backward")
    j = j.filter(pl.col("row").is_not_null()).sort("agent", "t_call")
    # next consolidation window per call (censoring)
    j = j.with_columns(pl.when(pl.col("reset_consol")).then(pl.col("row")).otherwise(None).alias("_rr"))
    j = j.with_columns(pl.col("_rr").shift(-1).backward_fill().over(["agent", "pt_date"]).alias("next_reset_row"))
    pos = {}
    rows_idx = np.arange(v.height)
    seg_start_ok = np.r_[False, (ag[1:] == ag[:-1]) & (dy[1:] == dy[:-1]) & (w[1:] - w[:-1] == 1)]

    def trajectories(sel):
        anchors = sel.select("row", "next_reset_row").unique("row").to_numpy()
        T = np.full((len(anchors), kmax + 1, q), np.nan)
        for n, (r0, rn) in enumerate(anchors):
            r0 = int(r0)
            lim = int(rn) if rn is not None and not np.isnan(rn) else 10 ** 9
            for k in range(kmax + 1):
                r = r0 + k
                if r >= v.height or r >= lim and k > 0:
                    break
                if k > 0 and not seg_start_ok[r]:
                    break
                T[n, k] = E[r]
        return T, anchors[:, 0].astype(int)

    forced = j.filter(pl.col("reset_forced"))
    control = j.filter(~pl.col("reset_consol") & (pl.col("ctx_pos") >= 15))
    if control.height > 4 * max(forced.height, 1):
        control = control.sample(4 * forced.height, seed=int(rng.integers(1 << 30)))
    res = {"goal": goal, "names": names, "n_forced": forced.height, "n_control": control.height}
    for tag, sel in (("forced", forced), ("control", control)):
        T, a_rows = trajectories(sel)
        seg_ad = np.array([f"{ag[r]}|{dy[r]}" for r in a_rows])
        m = np.nanmean(T, 0)
        d = 0.5 * np.nansum(np.abs(m), 1)
        nk = np.sum(np.isfinite(T[:, :, 0]), 0)
        # agent-day bootstrap of d(k)
        uad, inv = np.unique(seg_ad, return_inverse=True)
        bs = []
        for _ in range(B):
            pick = rng.integers(0, len(uad), len(uad))
            wgt = np.bincount(pick, minlength=len(uad))[inv].astype(float)
            mm = np.nansum(T * wgt[:, None, None], 0) / np.maximum(np.sum(np.isfinite(T[:, :, 0]) * wgt[:, None], 0), 1)[:, None]
            bs.append(0.5 * np.abs(mm).sum(1))
        bs = np.array(bs)
        res[tag] = {"d": d.tolist(), "n_k": nk.tolist(), "d_ci": np.percentile(bs, [2.5, 97.5], axis=0).tolist(),
                    "mean_dev_k0": dict(zip(names, m[0].round(4).tolist())), "mean_dev_k1": dict(zip(names, m[1].round(4).tolist()))}
        kk = np.arange(1, kmax + 1)
        y = np.log(np.clip(d[1:], 1e-6, None))
        slope = np.polyfit(kk, y, 1)[0]
        res[tag]["slope_lnd_k1_4"] = float(slope)
        res[tag]["tau_relax_min"] = float(-5.0 / slope) if slope < 0 else None
        bsl = [np.polyfit(kk, np.log(np.clip(b[1:], 1e-6, None)), 1)[0] for b in bs]
        res[tag]["slope_ci"] = np.percentile(bsl, [2.5, 97.5]).tolist()
        res[tag]["_bs_d1"] = bs[:, 1]
    diff = res["forced"].pop("_bs_d1") - res["control"].pop("_bs_d1")
    res["d1_forced_minus_control_ci"] = np.percentile(diff, [2.5, 97.5]).tolist()
    # the MSM's t2* for the same period (round-1b q6 run)
    r = json.loads((OUT / f"G{goal:02d}.json").read_text())["v3_q6"]
    res["t2_bc"] = r["t2_bc"]
    res["t2_raw"] = r["t2"]
    tr = res["forced"]["tau_relax_min"]
    res["ratio_tau_relax_over_t2bc"] = (tr / r["t2_bc"]) if tr and r["t2_bc"] else None
    res["transient"] = bool(res["d1_forced_minus_control_ci"][0] > 0)
    res["factor2"] = bool(res["ratio_tau_relax_over_t2bc"] is not None and 0.5 <= res["ratio_tau_relax_over_t2bc"] <= 2)
    return res


# ============================================================================ N2
def t2_block(goal, d0, d1, rng, R=200):
    cal = pl.read_parquet(SH / "calendar.parquet")
    days = [d for d in cal.filter(pl.col("goal_no") == goal)["pt_date"].to_list() if d0 <= d <= d1]
    v, P, names = macro_table(goal, days=days)
    S = V.sequences(v, P)
    nseg = int(S["seg"].max()) + 1
    Csk = RB.seg_C(S, [1, 2])
    lam = RB.t2_shift_from(Csk)
    Wb = L.boot_weights(nseg, R, rng)
    lb = np.array([RB.t2_shift_from(Csk, w) for w in Wb])
    lam_bc = float(np.clip(2 * lam - np.nanmedian(lb), 1e-6, 1 - 1e-9))
    tb = np.array([RB.t2_of_lam(float(np.clip(2 * lam - x, 1e-6, 1 - 1e-9))) for x in lb])  # basic bootstrap draws
    lab = v.filter(pl.col("labeled"))
    return {"days": [days[0], days[-1]], "n_days": len(days), "n_windows": v.height, "names": names,
            "t2": RB.t2_of_lam(lam), "t2_bc": RB.t2_of_lam(lam_bc), "t2_bc_boot": tb,
            "p_blocked": float(lab["p_blocked"].mean()), "occupancy": dict(zip(names, P.mean(0).round(4).tolist())),
            "fail_share": float(lab["n_errors"].sum() / max(lab["n_actions"].sum(), 1))}


def n2_ne43(rng):
    blocks = {"A": ("2026-07-24", "2026-08-04"), "B": ("2026-08-05", "2026-08-20"), "C": ("2026-08-21", "2026-09-02"),
              "P1": ("2026-07-06", "2026-07-14"), "P2": ("2026-07-15", "2026-07-23")}
    res = {k: t2_block(51, a, b, rng) for k, (a, b) in blocks.items()}
    out = {k: {kk: vv for kk, vv in r.items() if kk != "t2_bc_boot"} for k, r in res.items()}
    for x, y in (("C", "A"), ("B", "A"), ("C", "B"), ("P2", "P1")):
        dd = np.asarray(res[x]["t2_bc_boot"]) - np.asarray(res[y]["t2_bc_boot"])
        dd = dd[np.isfinite(dd)]
        out[f"{x}_minus_{y}"] = {"t2_bc_diff": res[x]["t2_bc"] - res[y]["t2_bc"],
                                 "ci": np.percentile(dd, [2.5, 97.5]).tolist() if len(dd) > 20 else None,
                                 "p_blocked_diff": res[x]["p_blocked"] - res[y]["p_blocked"]}
    ci = out["C_minus_A"]["ci"]
    out["prediction_holds"] = bool(ci is not None and ci[0] > 0 and out["C_minus_A"]["p_blocked_diff"] > 0)
    return out


# ============================================================================ N3
def n3_changepoint(rng, n_perm=1000):
    v, P, names = macro_table(27)
    S = V.sequences(v, P)
    days = sorted(np.unique(S["seg_day"]))
    q = P.shape[1]
    Cd = np.zeros((len(days), q, q))
    occ = np.zeros((len(days), q))
    seg_day = S["seg_day"]
    Cs = V.seg_soft_counts(S["P"], S["seg"], 1)
    di = {d: i for i, d in enumerate(days)}
    for s in range(len(seg_day)):
        Cd[di[seg_day[s]]] += Cs[s]
    for d in days:
        m = S["day"] == d
        occ[di[d]] = P[m].mean(0)

    def ll(C):
        T = (C + 0.5) / (C + 0.5).sum(1, keepdims=True)
        return float((C * np.log(T)).sum())

    def best_split(order):
        C = Cd[order]
        tot = ll(C.sum(0))
        best, bs = -np.inf, None
        for s in range(2, len(order) - 1):          # split after day s (s = 2..8 of 10)
            lr = ll(C[:s].sum(0)) + ll(C[s:].sum(0)) - tot
            if lr > best:
                best, bs = lr, s
        return best, bs

    obs, s_obs = best_split(np.arange(len(days)))
    null = np.array([best_split(rng.permutation(len(days)))[0] for _ in range(n_perm)])
    p = float((1 + np.sum(null >= obs)) / (n_perm + 1))
    ti = names.index("talk") if "talk" in names else None
    before, after = occ[:s_obs].mean(0), occ[s_obs:].mean(0)
    return {"days": days, "best_split_after_day_index": s_obs, "split_date": days[s_obs], "lr": obs, "p_perm": p,
            "talk_before": float(before[ti]) if ti is not None else None, "talk_after": float(after[ti]) if ti is not None else None,
            "occ_before": dict(zip(names, before.round(4).tolist())), "occ_after": dict(zip(names, after.round(4).tolist())),
            "daily_occupancy": {d: dict(zip(names, occ[i].round(3).tolist())) for i, d in enumerate(days)},
            "prediction_holds": bool(p < 0.05 and ti is not None and after[ti] > before[ti])}


def main():
    rng = np.random.default_rng(20261004)
    res = {"N1_G51": n1_relaxation(51, rng), "N1_G38": n1_relaxation(38, rng), "N2_NE43": n2_ne43(rng),
           "N3_G27": n3_changepoint(rng)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "native_r1b.json").write_text(json.dumps(L.jsonable(res), indent=1))
    for k, r in res.items():
        print(k, json.dumps(L.jsonable({kk: vv for kk, vv in r.items() if kk not in ("daily_occupancy",)}))[:1500], flush=True)


if __name__ == "__main__":
    main()
