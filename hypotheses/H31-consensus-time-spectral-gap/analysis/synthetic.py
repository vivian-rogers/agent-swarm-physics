"""H31 synthetic validation (axis F), run before any real-data event detection.

S0  generic: Poisson schedules on two-cluster graphs with a tunable bridge -> does the time-respecting DeGroot gap
    track lambda2, and does the count-contagion consensus time scale as 1/lambda2_sym?
S2  village schedules: on every E-P-eligible block's REAL reading schedule, simulate five truth models
    (D count contagion, A fraction contagion, V voter, H herding wave, F field), observe through the E-P pipeline
    (period-specific label coverage, W = 30 min, carry-forward 4, the card's detection rule), then regress log tau on
    each predictor across blocks with one event per block. Power = P(slope CI excludes 0 and includes 1);
    model choice = which fixed-slope model wins leave-one-period-out RMSE. Also at subsampled n = 8, 12, 16.
S3  content: DeGroot vectors on the real schedules with measurement noise -> alignment series -> relaxation fit ->
    slope of log tau_C on log(1/g_tr).

  uv run python hypotheses/H31-consensus-time-spectral-gap/analysis/synthetic.py [--quick]
Outputs: data/processed/H31-consensus-time-spectral-gap/synthetic/*.json|parquet. Uses label COVERAGE (structure)
but no label timing or alignment values.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h31lib as L  # noqa: E402

OUTD = L.DATA / "synthetic"
PRED = ["l2_sym", "l2_sym_core", "l2_dir", "ul2_rw", "g_tr", "u", "tau_wave", "tau_V", "N_b"]
# sign: tau ~ x^sign  (rates -> 1/x, times -> x, N -> x)
SIGN = {"l2_sym": -1, "l2_sym_core": -1, "g_tr_core": -1, "l2_dir": -1, "ul2_rw": -1, "g_tr": -1, "u": -1,
        "tau_wave": 1, "tau_V": 1, "N_b": 1, "l2_bin": -1, "l2_ment": -1}


def eligible_blocks() -> list[tuple[int, int]]:
    """E-P eligibility (card): >= 50% of the period's labeled room-windows have >= 3 labeled agents (H11 w30)."""
    out = []
    for p in sorted(L.DATA.glob("G*")):
        g = int(p.name[1:])
        P = L.load_period(g)
        s = P["states30"]
        if s is None or s.height == 0:
            continue
        per = s.group_by("day", "win", "room").agg(pl.len().alias("n"))
        if (per["n"] >= 3).mean() < 0.5:
            continue
        for b in L.blocks_of(P):
            out.append((g, b))
    return out


def coverage(P, b) -> float:
    s = P["states30"].filter(pl.col("room") == b)
    bw = P["block_windows"].filter(pl.col("room") == b)
    return float(s.height / max(bw.height, 1))


def grid_for(P, b, start_s, S, horizon_h=40.0):
    am = np.unique(P["block_windows"].filter(pl.col("room") == b)["act_mid"].to_numpy())
    T = S.a1 - S.a0
    reps = int(np.ceil(horizon_h * 3600 / T)) + 2
    g = np.concatenate([am + k * T for k in range(reps)])
    g = g[(g >= start_s - 1e-6)]
    return g[g <= start_s + horizon_h * 3600]


def block_job(args):
    g, b, params, R, n_starts, seed = args
    rng = np.random.default_rng(seed)
    P = L.load_period(g)
    S = L.make_schedule(P, b)
    if S is None:
        return []
    pobs = coverage(P, b)
    rows = []
    others = (2 + np.arange(S.N) % 4).astype(np.int16)
    for model, prm in params.items():
        for si in range(n_starts):
            st = rng.uniform(S.a0, S.a0 + 0.4 * (S.a1 - S.a0))
            grid = grid_for(P, b, st, S)
            states, t50 = L.simulate_states(S, model, prm, st, R, rng, grid, max_cycles=12)
            lab = L.observe(states, pobs, rng, others)
            act_h = grid / 3600.0
            Nb = np.full(len(grid), S.N, float)
            for r in range(R):
                ev = L.detect_project_events(lab[r], act_h, Nb, restrict_label=1)
                e = ev[0] if ev else None
                rows.append(dict(goal_no=g, room=b, model=model, start=si, rep=r, t50_true=float(t50[r]),
                                 consensus=bool(e and e["consensus"]), frozen=bool(e and e["frozen"]),
                                 tau_obs=float(e["tau_h"]) if e and e["consensus"] else np.nan,
                                 rise=(e["rise"] if e and e["consensus"] and e["rise"] is not None else -1),
                                 p_obs=pobs, N=S.N))
    return rows


def fit_dataset(df: pl.DataFrame, pred: pl.DataFrame, rng):
    """One synthetic dataset: one uncensored event per block -> slopes and LOPO model choice."""
    d = df.join(pred, on=["goal_no", "room"], how="inner")
    y = np.log(d["tau_obs"].to_numpy())
    cl = d["goal_no"].to_numpy()
    res = {}
    for p in PRED:
        x = SIGN[p] * np.log(np.maximum(d[p].to_numpy(), 1e-6)) * (1 if SIGN[p] > 0 else 1)
        # regressor oriented so that the theory slope is +1: log(1/rate) or log(time) or log N
        b, ci = L.cluster_boot_slope(x, y, cl, B=300, seed=int(rng.integers(1 << 30)))
        res[p] = dict(b=b, lo=ci[0], hi=ci[1])
    pr = {"M0": L.lopo(y, cl)}
    for p in ["l2_sym", "l2_sym_core", "g_tr", "ul2_rw", "tau_wave", "tau_V"]:
        x = SIGN[p] * np.log(np.maximum(d[p].to_numpy(), 1e-6))
        pr["M_" + p] = L.lopo(y, cl, offset=x)
    pr["M_N"] = L.lopo(y, cl, X=np.log(d["N_b"].to_numpy())[:, None])
    rm = {k: L.rmse(y, v) for k, v in pr.items()}
    res["lopo"] = rm
    res["best"] = min(rm, key=lambda k: rm[k] if np.isfinite(rm[k]) else 1e9)
    res["n"] = len(y)
    res["sd_logtau"] = float(np.std(y))
    return res


def s2_power(sim: pl.DataFrame, pred: pl.DataFrame, n_datasets=200, sizes=(None, 8, 12, 16), seed=1):
    rng = np.random.default_rng(seed)
    out = {}
    ok = sim.filter(pl.col("consensus") & ~pl.col("frozen") & pl.col("tau_obs").is_finite())
    for model in sorted(ok["model"].unique().to_list()):
        sm = ok.filter(pl.col("model") == model)
        blocks = sm.select("goal_no", "room").unique().sort("goal_no", "room").rows()
        for n in sizes:
            fits = []
            for _ in range(n_datasets):
                bl = blocks if n is None or n >= len(blocks) else [blocks[i] for i in rng.choice(len(blocks), n, replace=False)]
                pick = []
                for (g, b) in bl:
                    sub = sm.filter((pl.col("goal_no") == g) & (pl.col("room") == b))
                    pick.append(sub.row(int(rng.integers(sub.height)), named=True))
                d = pl.DataFrame(pick).select("goal_no", "room", "tau_obs")
                fits.append(fit_dataset(d, pred, rng))
            key = f"{model}|n={n or len(blocks)}"
            summ = {"n_blocks": fits[0]["n"], "sd_logtau_med": float(np.median([f["sd_logtau"] for f in fits]))}
            for p in PRED:
                bs = np.array([f[p]["b"] for f in fits])
                pw = np.mean([(f[p]["lo"] > 0) and (f[p]["lo"] <= 1 <= f[p]["hi"]) for f in fits])
                ex0 = np.mean([(f[p]["lo"] > 0) or (f[p]["hi"] < 0) for f in fits])
                summ[p] = dict(b_med=float(np.nanmedian(bs)), b_q10=float(np.nanquantile(bs, .1)),
                               b_q90=float(np.nanquantile(bs, .9)), p1_pass=float(pw), excl0=float(ex0))
            best = [f["best"] for f in fits]
            summ["best_model_freq"] = {k: best.count(k) / len(best) for k in sorted(set(best))}
            summ["lopo_med"] = {k: float(np.median([f["lopo"][k] for f in fits])) for k in fits[0]["lopo"]}
            out[key] = summ
            print(key, "n", summ["n_blocks"], "P1-pass(l2_sym)", round(summ["l2_sym"]["p1_pass"], 2),
                  "b_l2sym", round(summ["l2_sym"]["b_med"], 2), "b_N", round(summ["N_b"]["b_med"], 2),
                  "best", {k: round(v, 2) for k, v in summ["best_model_freq"].items()}, flush=True)
    return out


# ------------------------------------------------------------------------------------------------ S0 generic
def poisson_schedule(Wb, u, rate, T_h, rng):
    """Synthetic Schedule: N agents, messages Poisson(rate_j), agent i reads at Poisson(u) turns and sees each new
    message from j with probability Wb[i, j] (0/1 adjacency or weights in [0,1])."""
    N = len(rate)
    T = T_h * 3600
    msg_t, msg_s = [], []
    for j in range(N):
        n = rng.poisson(rate[j] * T_h)
        msg_t.extend(rng.uniform(0, T, n))
        msg_s.extend([j] * n)
    o = np.argsort(msg_t)
    msg_t = np.array(msg_t)[o]
    msg_s = np.array(msg_s, np.int16)[o]
    upd_t, upd_i, ptr, um = [], [], [0], []
    for i in range(N):
        turns = np.sort(rng.uniform(0, T, rng.poisson(u * T_h)))
        last = 0.0
        for k in range(1, len(turns)):
            s0, s1 = turns[k - 1], turns[k]
            lo, hi = np.searchsorted(msg_t, last), np.searchsorted(msg_t, s0)
            cand = np.arange(lo, hi)
            cand = cand[(msg_s[cand] != i)]
            cand = cand[rng.random(len(cand)) < Wb[i, msg_s[cand]]]
            last = s0
            if len(cand):
                upd_t.append(s1)
                upd_i.append(i)
                um.extend(cand.tolist())
                ptr.append(len(um))
    o = np.argsort(upd_t, kind="stable")
    lens = np.diff(np.array(ptr))
    st = np.array(ptr[:-1])
    um_a = np.array(um, np.int64)
    um2 = np.concatenate([um_a[st[k]:st[k] + lens[k]] for k in o]) if len(o) else np.zeros(0, np.int64)
    ptr2 = np.r_[0, np.cumsum(lens[o])]
    S = L.Schedule(np.arange(N), 0.0, T, msg_t, msg_s, np.array(upd_t)[o], np.array(upd_i, np.int16)[o],
                   ptr2.astype(np.int64), um2)
    W = np.zeros((N, N))
    for k in range(len(S.upd_t)):
        np.add.at(W[S.upd_i[k]], S.msg_s[S.upd_m[S.upd_ptr[k]:S.upd_ptr[k + 1]]], 1.0)
    S.W = W / T_h
    S.turns = []
    return S


def s0_generic(seed=0, quick=False):
    rng = np.random.default_rng(seed)
    rows = []
    for N in (6, 10, 14):
        for bridge in (1.0, 0.3, 0.1, 0.03):
            for rep in range(2 if quick else 3):
                cl3 = np.arange(N) * 3 // N          # three clusters: 50% needs a second cluster
                Wb = np.where(cl3[:, None] == cl3[None, :], 1.0, bridge)
                rate = rng.uniform(3, 12, N)
                S = poisson_schedule(Wb, 30.0, rate, 30.0, rng)
                l2s = L.lam2_sym(S.W)
                gtr = L.gamma_tr(S, alpha=0.5, seed=rep)
                # count contagion consensus (true t50) from one seed
                st = 0.5 * 3600
                grid = st + 3600 * np.arange(0, 100, 0.25)
                states, t50 = L.simulate_states(S, "D", {"beta": 0.02}, st, 60, rng, grid, max_cycles=8)
                frac = states.mean(2)                                   # (R, G)
                t90 = np.array([grid[np.argmax(f >= 0.9)] - st if (f >= 0.9).any() else np.nan for f in frac]) / 3600
                rows.append(dict(N=N, bridge=bridge, rep=rep, l2_sym=l2s, l2_rw=L.lam2_rw(S.W), g_tr=gtr,
                                 t50_D=float(np.nanmedian(t50)), t90_D=float(np.nanmedian(t90)),
                                 frac_reached=float(np.isfinite(t50).mean())))
    df = pl.DataFrame(rows)
    x = np.log(1 / df["l2_sym"].to_numpy())
    out = {}
    for c in ("t50_D", "t90_D"):
        y = np.log(df[c].to_numpy())
        ok = np.isfinite(x) & np.isfinite(y)
        out[f"slope_log{c}_on_log_inv_l2sym"] = float(np.polyfit(x[ok], y[ok], 1)[0])
    ok = np.isfinite(df["g_tr"].to_numpy()) & (df["g_tr"].to_numpy() > 0)
    out["corr_log_gtr_log_u_l2rw"] = float(np.corrcoef(np.log(df["g_tr"].to_numpy()[ok]),
                                                       np.log(df["l2_rw"].to_numpy()[ok] * 30))[0, 1])
    return df, out


# ------------------------------------------------------------------------------------------------ S3 content
def content_job(args):
    g, b, alpha_true, sigma, n_rep, seed = args
    rng = np.random.default_rng(seed)
    P = L.load_period(g)
    S = L.make_schedule(P, b)
    if S is None or P["alignment"] is None:
        return []
    am = np.unique(P["block_windows"].filter(pl.col("room") == b)["act_mid"].to_numpy())
    cov = P["alignment"].filter(pl.col("room") == b)
    p_present = float(np.clip(cov["n_agents"].mean() / max(S.N, 1), 0.2, 1.0)) if cov.height else 0.6
    out = []
    d = 8
    t, typ, idx = S.events()
    for rep in range(n_rep):
        X = rng.standard_normal((S.N, d)) * 1.0 + 0.3 * rng.standard_normal(d)
        MS = np.zeros((len(S.msg_t), d))
        rec = np.zeros((len(am), S.N, d))
        gi = 0
        for k in range(len(t)):
            while gi < len(am) and am[gi] <= t[k]:
                rec[gi] = X
                gi += 1
            if typ[k] == 0:
                MS[idx[k]] = X[S.msg_s[idx[k]]]
            else:
                u = idx[k]
                ms = S.upd_m[S.upd_ptr[u]:S.upd_ptr[u + 1]]
                if len(ms):
                    i = S.upd_i[u]
                    X[i] = (1 - alpha_true) * X[i] + alpha_true * MS[ms].mean(0)
        while gi < len(am):
            rec[gi] = X
            gi += 1
        rows = []
        for w in range(len(am)):
            pres = np.flatnonzero(rng.random(S.N) < p_present)
            if len(pres) < 3:
                continue
            V = rec[w, pres] + sigma * rng.standard_normal((len(pres), d))
            V /= np.linalg.norm(V, axis=1, keepdims=True)
            C = V @ V.T
            n = len(pres)
            rows.append(dict(day=0, win=w, room=b, n_agents=n, A=float((C.sum() - n) / (n * (n - 1))), act_mid=float(am[w])))
        if not rows:
            continue
        ev = L.detect_content_event(pl.DataFrame(rows), b, S.T_h)
        out.append(dict(goal_no=g, room=b, rep=rep, kind=ev.get("kind"), tau_C=ev.get("tau", np.nan),
                        dBIC=ev.get("dBIC", np.nan)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    OUTD.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    pp = pl.read_parquet(L.DATA / "predictors_period.parquet")
    core = pp.filter(pl.col("variant") == "core").select("goal_no", "room", pl.col("l2_sym").alias("l2_sym_core"),
                                                         pl.col("g_tr").alias("g_tr_core"))
    pred = pp.filter(pl.col("variant") == "all").join(core, on=["goal_no", "room"], how="left")

    # ---- S0
    s0df, s0 = s0_generic(quick=a.quick)
    s0df.write_parquet(OUTD / "s0_generic.parquet")
    print("S0", s0, f"{time.time() - t0:.0f}s", flush=True)

    # ---- S2
    blocks = eligible_blocks()
    pe = pred.join(pl.DataFrame(blocks, schema=["goal_no", "room"], orient="row"), on=["goal_no", "room"])
    med = lambda c: float(np.median(pe[c].to_numpy()))
    params = {
        "D": {"beta": float(np.median(np.log(pe["N_b"].to_numpy()) / (2.0 * pe["msg_rate"].to_numpy())))},
        "A": {"beta": float(np.median(np.log(pe["N_b"].to_numpy()) / (2.0 * pe["u"].to_numpy())))},
        "V": {"alpha": float(np.clip(med("tau_V") / 2.0, 0.005, 1.0))},
        "H": {"p_h": 0.8},
        "F": {"d_h": 2.5},
    }
    print("E-P eligible blocks", len(blocks), "params", params, flush=True)
    R, ns = (20, 3) if a.quick else (40, 4)
    jobs = [(g, b, params, R, ns, 1000 + 7 * k) for k, (g, b) in enumerate(blocks)]
    rows = []
    with ProcessPoolExecutor(max_workers=2) as ex:
        for r in ex.map(block_job, jobs):
            rows.extend(r)
    sim = pl.DataFrame(rows)
    sim.write_parquet(OUTD / "s2_sims.parquet", compression="zstd")
    summ = sim.group_by("model").agg(pl.col("consensus").mean().alias("p_cons"), pl.col("frozen").mean().alias("p_frozen"),
                                     pl.col("tau_obs").median().alias("tau_med"), pl.col("t50_true").median().alias("t50_med"),
                                     (pl.col("rise").is_between(0, 1)).sum().alias("abrupt"),
                                     (pl.col("rise") >= 0).sum().alias("n_rise"))
    print(summ, f"{time.time() - t0:.0f}s", flush=True)
    power = s2_power(sim, pe.select(["goal_no", "room"] + PRED), n_datasets=60 if a.quick else 150)

    # ---- S3 content
    cblocks = []
    for p in sorted(L.DATA.glob("G*")):
        g = int(p.name[1:])
        P = L.load_period(g)
        if P["alignment"] is None:
            continue
        for b in L.blocks_of(P):
            cblocks.append((g, b))
    pc = pred.join(pl.DataFrame(cblocks, schema=["goal_no", "room"], orient="row"), on=["goal_no", "room"])
    # alpha_true chosen so the median block relaxes in ~ 4 active h, assuming rate ~ alpha * u
    alpha_true = float(np.clip(1.0 / (4.0 * np.median(pc["u"].to_numpy())), 1e-4, 0.5))
    s3 = {}
    for sigma in (0.5, 1.0):
        cjobs = [(g, b, alpha_true, sigma, 3 if a.quick else 6, 5000 + k) for k, (g, b) in enumerate(cblocks)]
        crow = []
        with ProcessPoolExecutor(max_workers=2) as ex:
            for r in ex.map(content_job, cjobs):
                crow.extend(r)
        cs = pl.DataFrame(crow)
        cs.write_parquet(OUTD / f"s3_content_sigma{sigma}.parquet")
        s3[f"sigma={sigma}"] = s3_power(cs, pc, alpha_true)
        print("S3", sigma, s3[f"sigma={sigma}"], flush=True)

    res = {"S0": s0, "S2_params": params, "S2_blocks": len(blocks),
           "S2_summary": summ.to_dicts(), "S2_power": power, "S3": s3, "elapsed_s": time.time() - t0}
    (OUTD / "synthetic_results.json").write_text(json.dumps(res, indent=1, default=float))
    print(f"done {time.time() - t0:.0f}s")


def s3_power(cs, pc, alpha_true, n_datasets=200, seed=3):
    rng = np.random.default_rng(seed)
    conv = cs.filter(pl.col("kind") == "convergence")
    out = {"alpha_true": alpha_true, "frac_convergence": float((cs["kind"] == "convergence").mean()),
           "kinds": cs.group_by("kind").len().to_dicts()}
    blocks = conv.select("goal_no", "room").unique().rows()
    if len(blocks) < 3:
        out.update(n_blocks=len(blocks), b_med=np.nan, p1_pass=0.0, excl0=0.0)
        return out
    fits = []
    for _ in range(n_datasets):
        pick = []
        for (g, b) in blocks:
            sub = conv.filter((pl.col("goal_no") == g) & (pl.col("room") == b))
            pick.append(sub.row(int(rng.integers(sub.height)), named=True))
        d = pl.DataFrame(pick).join(pc, on=["goal_no", "room"])
        y = np.log(d["tau_C"].to_numpy())
        x = -np.log(np.maximum(d["g_tr"].to_numpy(), 1e-6))
        ok = np.isfinite(x) & np.isfinite(y)
        b, ci = L.cluster_boot_slope(x[ok], y[ok], d["goal_no"].to_numpy()[ok], B=300, seed=int(rng.integers(1 << 30)))
        fits.append((b, ci[0], ci[1]))
    f = np.array(fits)
    out.update(n_blocks=len(blocks), b_med=float(np.nanmedian(f[:, 0])),
               p1_pass=float(np.mean((f[:, 1] > 0) & (f[:, 1] <= 1) & (f[:, 2] >= 1))),
               excl0=float(np.mean((f[:, 1] > 0) | (f[:, 2] < 0))))
    return out


if __name__ == "__main__":
    main()
