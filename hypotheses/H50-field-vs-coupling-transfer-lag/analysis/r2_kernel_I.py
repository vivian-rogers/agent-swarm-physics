"""R2: regime-I dead-time kernel (card "Round 2", R2).
--synth: synthetic regime-I worlds on the real #27 and #24 skeletons (mixed chat-mode and computer-use calls). True call
  starts: logged and chained calls keep t_call; latency-placed calls get t* = t_first - L (L from the logged latency
  distribution of their mode). Talk is decided at t* from the real peer messages first visible at that call (true reads),
  with a mode base rate, agent effects and a planted kernel. The first record is redrawn t* + L(mode, talk), and the
  estimator sees the ledger's placement t_hat = first record - agent median chained latency. Kernel K = 6 boundary RD on
  all recipients and on logged-start recipients only.
--real: the K = 6 kernel on logged-start recipients in regime-I units with logged starts, pooled; split by the mode of
  the recipient's in-flight call at the message time.
Writes r2/synthetic_kernel_I.json, r2/kernel_I_units.parquet, r2/kernel_I_summary.json.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "2")
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h50lib as L  # noqa: E402
import r2lib as R2  # noqa: E402
import r2_relay as RR  # noqa: E402

OUT = RR.OUT
ROOT = RR.ROOT
K = 6
KERNELS = {
    "K0": dict(J=0.0),
    "K0flat": dict(J=0.0, flat=True),      # added (post hoc diagnostic): talk rate independent of the call mode
    "K1d0flat": dict(J=0.5, dead=0, shape="spike", flat=True),
    "K1d2flat": dict(J=0.5, dead=2, shape="spike", flat=True),
    "K1d0": dict(J=0.5, dead=0, shape="spike"),
    "K1d1": dict(J=0.5, dead=1, shape="spike"),
    "K1d2": dict(J=0.5, dead=2, shape="spike"),
    "K2": dict(J=0.5, dead=0, shape="ramp"),
}


def logged_latencies():
    cw = pl.read_parquet(ROOT / "data/processed/shared/call_windows.parquet",
                         columns=["regime", "holdout", "ctx_mode", "start_src", "talk", "latency_s"])
    cw = cw.filter(~pl.col("holdout") & (pl.col("regime") == "I") & (pl.col("start_src") == "logged")
                   & pl.col("latency_s").is_not_null() & (pl.col("latency_s") > 0) & (pl.col("latency_s") < 120))
    out = {}
    for mode in ("chat", "cu"):
        for talk in (False, True):
            v = cw.filter((pl.col("ctx_mode") == mode) & (pl.col("talk") == talk))["latency_s"].to_numpy()
            out[(mode == "cu", talk)] = v
        out[(mode == "cu", None)] = cw.filter(pl.col("ctx_mode") == mode)["latency_s"].to_numpy()
    return out


def kernel_vec(prm):
    k = np.zeros(K + 3)
    if prm["J"] == 0:
        return k
    d = prm.get("dead", 0)
    for h in range(1, K + 3):
        q = h - 1 - d
        if q < 0:
            continue
        k[h - 1] = prm["J"] * (np.exp(-q / 1.5) if prm["shape"] == "spike" else min(h, 5) / 5.0)
    return k


def logged_agents(U, R, thr=0.8):
    c = U["calls"]
    hi = (R["c_src"] == 0).astype(float)
    share = np.bincount(c["agent"], weights=hi, minlength=U["N"]) / np.maximum(np.bincount(c["agent"], minlength=U["N"]), 1)
    return np.where(share >= thr)[0]


def synth_world(U, R, lat, prm, seed):
    rng = np.random.default_rng(seed)
    c = U["calls"]
    n = len(c["tc"])
    mode = R["c_mode"].astype(int)
    latc = R["c_src"] == 4
    tstar = c["tc"].copy()
    for md in (0, 1):
        s = latc & (mode == md)
        tstar[s] = R["c_tfirst"][s] - rng.choice(lat[(md == 1, None)], s.sum())
    same = np.r_[False, (np.diff(c["agent"]) == 0) & (np.diff(c["day"]) == 0)]
    for i in np.where(same)[0]:          # keep order within an agent-day
        if tstar[i] <= tstar[i - 1]:
            tstar[i] = tstar[i - 1] + 0.5
    # true reads: first call with t* > t_m (same agent and day) for every ledger visibility pair
    keys_true = c["agent"].astype(np.float64) * L.KEYMUL + tstar
    o = np.argsort(keys_true, kind="stable")
    assert np.all(o == np.arange(n))
    tm = R["m_t"][R["p_msg"]]
    rec = R["p_rec"]
    idx = np.searchsorted(keys_true, rec * L.KEYMUL + tm, side="right")
    ok = idx < n
    idc = np.minimum(idx, n - 1)
    ok &= (c["agent"][idc] == rec) & (c["day"][idc] == R["m_day"][R["p_msg"]])
    S = np.bincount(idc[ok], minlength=n).astype(float)
    kv = kernel_vec(prm)
    eff = np.zeros(n)
    starts = np.where(~same)[0]
    ends = np.r_[starts[1:], n]
    for a, b in zip(starts, ends):
        eff[a:b] = np.convolve(S[a:b], kv)[: b - a]
    # base: mode rate (chat 0.78, computer use 0.04) + agent effect
    base = np.where(mode == 0, np.log(0.78 / 0.22), np.log(0.04 / 0.96))
    if prm.get("flat"):
        base = np.full(n, np.log(0.08 / 0.92))
    ae = rng.normal(0, 0.3, U["N"])[c["agent"]]
    Hh = base + ae + eff
    p = 1 / (1 + np.exp(-Hh))
    talk = rng.random(n) < p
    # truth kernel: mean marginal effect at hop h after the true read call, per pair
    truth = []
    for h in range(1, K + 1):
        ci = idc + h - 1
        okh = ok & (ci < n)
        cc = np.minimum(ci, n - 1)
        okh &= (c["agent"][cc] == rec) & (c["day"][cc] == c["day"][idc])
        me = p[cc[okh]] - 1 / (1 + np.exp(-(Hh[cc[okh]] - kv[h - 1])))
        truth.append(float(me.sum() / max(ok.sum(), 1)))
    # what the estimator sees: latency-placed starts re-estimated from the redrawn first record
    that = tstar.copy()
    for md in (0, 1):
        for tk in (False, True):
            s = latc & (mode == md) & (talk == tk)
            tf = tstar[s] + rng.choice(lat[(md == 1, tk)], s.sum())
            that[s] = tf - R["c_lat_agent"][s]
    for i in np.where(same)[0]:
        if that[i] <= that[i - 1]:
            that[i] = that[i - 1] + 0.5
    Us = dict(U)
    Us["calls"] = dict(c)
    Us["calls"]["tc"] = that
    Us["calls"]["talk"] = talk
    return Us, np.array(truth)


def kernel_est(U, R, sel_rec=None, nboot=100, sel_extra=None, y=None):
    m = R
    te, de, rec = m["m_t"][m["p_msg"]], m["m_day"][m["p_msg"]], m["p_rec"]
    sel = np.ones(len(te), bool)
    if sel_rec is not None:
        sel &= np.isin(rec, sel_rec)
    if sel_extra is not None:
        sel &= sel_extra
    keys = L.call_keys(U)
    W = 1.5 * L.median_call_interval(U)
    y = U["calls"]["talk"].astype(float) if y is None else y
    g = L.gate_kernel(U, keys, te[sel], de[sel], rec[sel], y, K=K, W=W, nboot=nboot)
    return g, int(sel.sum())


def synth(seeds):
    lat = logged_latencies()
    res = {}
    for u in ("27", "24"):
        U, R = RR.load(u)
        la = logged_agents(U, R)
        print(u, "logged agents", la.tolist(), "chat share", float((R["c_mode"] == 0).mean()), "latency-placed", float((R["c_src"] == 4).mean()))
        for kn, prm in KERNELS.items():
            key = f"{u}|{kn}"
            res[key] = []
            for sd in range(seeds):
                t0 = time.time()
                Us, truth = synth_world(U, R, lat, prm, 400 + sd)
                ga, na = kernel_est(Us, R)
                gl, nl = kernel_est(Us, R, la)
                r = dict(truth=truth.tolist(), all=dict(k=ga["kernel"].tolist(), lo=ga["k_lo"].tolist(), hi=ga["k_hi"].tolist(),
                                                        j_lo=ga["j_lo"].tolist(), se=ga["k_se"].tolist(), n=na),
                         logged=dict(k=gl["kernel"].tolist(), lo=gl["k_lo"].tolist(), hi=gl["k_hi"].tolist(),
                                     j_lo=gl["j_lo"].tolist(), se=gl["k_se"].tolist(), n=nl))
                res[key].append(r)
                f = lambda v: " ".join(f"{x:.3f}" for x in v)  # noqa: E731
                print(f"{key} s{sd} {time.time() - t0:.0f}s truth [{f(truth)}] | all [{f(ga['kernel'])}] | logged [{f(gl['kernel'])}]", flush=True)
            (OUT / "r2/synthetic_kernel_I.json").write_text(json.dumps(res))


def real():
    units = pl.read_parquet(OUT / "units.parquet").filter(pl.col("eligible") & (pl.col("kind") == "period_unit") & (pl.col("regime") == "I"))
    rows = []
    for u, g in zip(units["unit"], units["goal_no"]):
        U, R = RR.load(u)
        la = logged_agents(U, R)
        if len(la) == 0:
            continue
        c = U["calls"]
        te, rec = R["m_t"][R["p_msg"]], R["p_rec"]
        keys = L.call_keys(U)
        # Amendment R2-A1 (post hoc): the in-flight call is the RD's left anchor, so splitting on its mode biases the
        # jump mechanically. Split instead on the mode of the recipient's last call that started before t_m - W
        # (outside the anchor window, same agent and day).
        Wu = 1.5 * L.median_call_interval(U)
        ib = np.searchsorted(keys, rec * L.KEYMUL + te - Wu, side="right") - 1
        ibc = np.maximum(ib, 0)
        okb = (ib >= 0) & (c["agent"][ibc] == rec) & (c["day"][ibc] == R["m_day"][R["p_msg"]])
        inflight_chat = okb & (R["c_mode"][ibc] == 0)
        inflight_cu = okb & (R["c_mode"][ibc] == 1)
        row = dict(unit=u, goal_no=int(g), n_logged_agents=len(la))
        ychat = (R["c_mode"] == 0).astype(float)
        for lab, extra in (("logged", None), ("logged_chat", inflight_chat), ("logged_cu", inflight_cu), ("all", None),
                           ("all_chat", inflight_chat), ("all_cu", inflight_cu), ("mode_logged", None), ("mode_all", None)):
            sr = None if lab.startswith("all") or lab == "mode_all" else la
            selc = np.isin(rec, la) if sr is not None else np.ones(len(rec), bool)
            if extra is not None:
                selc &= extra
            if selc.sum() < 300:
                continue
            gk, n = kernel_est(U, R, sr, nboot=200, sel_extra=extra, y=ychat if lab.startswith("mode") else None)
            row[f"{lab}_n"] = n
            for h in range(K):
                row[f"{lab}_k{h + 1}"], row[f"{lab}_k{h + 1}_se"] = float(gk["kernel"][h]), float(gk["k_se"][h])
                row[f"{lab}_j{h + 1}_lo"] = float(gk["j_lo"][h])
            row[f"{lab}_d41"] = float(gk["kernel"][3] - gk["kernel"][0])
        rows.append(row)
        print(u, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items() if k.endswith(("k1", "k2", "k4", "_n"))}, flush=True)
    df = pl.DataFrame(rows, infer_schema_length=None)
    df.write_parquet(OUT / "r2/kernel_I_units.parquet")
    summ = {}
    for lab in ("logged", "logged_chat", "logged_cu", "all", "all_chat", "all_cu", "mode_logged", "mode_all"):
        if f"{lab}_k1" not in df.columns:
            continue
        s = df.filter(pl.col(f"{lab}_k1").is_not_null())
        d = dict(n_units=len(s))
        for h in range(1, K + 1):
            m, se = R2.ivw(s[f"{lab}_k{h}"].to_numpy(), s[f"{lab}_k{h}_se"].to_numpy())
            d[f"k{h}"] = (m, se)
        d["onset_hop1_units"] = int((s[f"{lab}_j1_lo"] > 0).sum())
        summ[lab] = d
        print(lab, json.dumps(d))
    (OUT / "r2/kernel_I_summary.json").write_text(json.dumps(summ, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--synth", action="store_true")
    ap.add_argument("--real", action="store_true")
    ap.add_argument("--seeds", type=int, default=5)
    a = ap.parse_args()
    if a.synth:
        synth(a.seeds)
    if a.real:
        real()


if __name__ == "__main__":
    main()
