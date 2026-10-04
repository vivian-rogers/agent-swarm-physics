"""H34 synthetic validation (axis F), run before any real-data cascade statistic.

S1  finite-N branching: Reed-Frost chain binomial (N agents, per-pair T = R/(N-1)) and GW-NB trees capped at N.
    Recovery of R from offspring and from sizes alone; identifiability of tau and s_c; calibration tau_app(R);
    coverage of the unfitted GW-NB tail band; rejection of pure s^-3/2.
S2  contagion on real village timelines (#20, #42, a #51 segment): real message times, senders, rooms, `exposure`
    rows and turn times; synthetic markers seeded at real agent messages; adoption per talk turn
    1-(1-q)^k (simple; k = distinct sources whose use arrived within the agent's last 3 call windows) or a
    threshold (complex), plus a field eps per talk turn within 24 h of the seed; adopters re-use the marker.
    The full H34 pipeline (scheme/h34core.assemble) is run on the synthetic uses and compared with the truth.

  uv run python hypotheses/H34-idea-cascades/analysis/synthetic.py s1
  uv run python hypotheses/H34-idea-cascades/analysis/synthetic.py s2
Outputs: data/processed/H34-idea-cascades/synthetic/{s1.parquet, s2.parquet}
"""
from __future__ import annotations

import os
import sys
import time
import zlib
from multiprocessing import Pool
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h34stats as S  # noqa: E402
import h34core as C  # noqa: E402

OUT = C.OUT / "synthetic"
N_WORKERS = 2


# =============================================================================================== S1
def reed_frost_tree(N, T, rng):
    """Chain-binomial outbreak in a room of N from one root; returns (size, offspring per node)."""
    S_, I_ = N - 1, 1
    off = []
    size = 1
    while I_ > 0 and S_ > 0:
        # each infective independently hits each susceptible with prob T; a hit susceptible is assigned to one hitter
        hits = rng.random((I_, S_)) < T
        newly = hits.any(0)
        n_new = int(newly.sum())
        o = np.zeros(I_, dtype=int)
        if n_new:
            cols = np.where(newly)[0]
            for c in cols:
                h = np.where(hits[:, c])[0]
                o[rng.choice(h)] += 1
        off.extend(o.tolist())
        size += n_new
        S_ -= n_new
        I_ = n_new
    off.extend([0] * I_)
    return size, off


def gwnb_tree(R, k, cap, rng):
    size, act, off = 1, 1, []
    while act > 0:
        o = rng.negative_binomial(k, k / (k + R), size=act) if k < S.K_INF else rng.poisson(R, size=act)
        room = cap - size
        tot = int(o.sum())
        if tot > room:   # truncate at the room size, removing offspring at random
            keep = np.zeros(act, dtype=int)
            idx = np.repeat(np.arange(act), o)
            sel = rng.choice(len(idx), room, replace=False) if room > 0 else np.array([], dtype=int)
            np.add.at(keep, idx[sel], 1)
            o, tot = keep, room
        off.extend(o.tolist())
        size += tot
        act = tot
    return size, off


def s1_task(task):
    model, N, R, k, n_trees, rep = task
    rng = np.random.default_rng(zlib.crc32(repr((model, N, R, k, n_trees, rep)).encode()))
    sizes, offs = [], []
    for _ in range(n_trees):
        if model == "reedfrost":
            s, o = reed_frost_tree(N, R / (N - 1), rng)
        else:
            s, o = gwnb_tree(R, k, N, rng)
        sizes.append(s)
        offs.extend(o)
    sizes = np.array(sizes)
    fo = S.fit_offspring(np.array(offs))
    sm_inf = S.size_mle(sizes, N, k=S.K_INF)
    pf = S.powerlaw_fits(sizes, N)
    cdf, band = S.predict_tail(fo["R"], fo["k"], N, n_trees, B=400, seed=rep)
    obs3, obs5 = float((sizes >= 3).mean()), float((sizes >= 5).mean())
    cdf2, band2, R0 = S.predict_tail_fngw(fo["R"], min(fo["k"], S.K_INF), N, n_trees, B=400, n_param=0, seed=rep)
    return dict(model=model, N=N, R=R, k=k, n_trees=n_trees, rep=rep, R_off=fo["R"], k_off=fo["k"],
                R_size=sm_inf["R"], mean_size=float(sizes.mean()), p_ge2=float((sizes >= 2).mean()), p_ge3=obs3,
                p_ge5=obs5, tau_app=pf["tau_app"], tau=pf["tau"], tau_lo=pf["tau_lo"], tau_hi=pf["tau_hi"],
                s_c=pf["s_c"], p_cut=pf["p_cut"], lr_15pure=pf["lr_15pure_vs_cut"],
                cover3=bool(band[3][0] <= obs3 <= band[3][1]), cover5=bool(band[5][0] <= obs5 <= band[5][1]),
                fn_cover3=bool(band2[3][0] <= obs3 <= band2[3][1]), fn_cover5=bool(band2[5][0] <= obs5 <= band2[5][1]),
                fn_R0=R0, fn_pred3=cdf2[3], gw_pred3=cdf[3],
                s_c_borel=S.borel_cutoff(R) if R < 1 else np.inf)


def run_s1():
    tasks = []
    for N in (8, 15, 25):
        for R in (0.1, 0.3, 0.5, 0.7, 0.9, 1.0):
            for n_trees in (300, 3000):
                for rep in range(12):
                    tasks.append(("reedfrost", N, R, S.K_INF, n_trees, rep))
                    tasks.append(("gwnb", N, R, 0.5, n_trees, rep))
    t0 = time.time()
    with Pool(N_WORKERS) as pool:
        res = pool.map(s1_task, tasks, chunksize=4)
    OUT.mkdir(parents=True, exist_ok=True)
    df = pl.DataFrame(res)
    df.write_parquet(OUT / "s1.parquet", compression="zstd")
    print(f"S1: {len(res)} runs in {time.time() - t0:.0f}s")
    summ = (df.group_by("model", "N", "R", "n_trees")
            .agg(pl.col("R_off").mean(), pl.col("R_size").mean(), pl.col("tau").median(), (pl.col("tau_hi") - pl.col("tau_lo")).median().alias("tau_ci_w"),
                 pl.col("tau_app").mean(), (pl.col("p_cut") < 0.05).mean().alias("rej_pure"),
                 (pl.col("lr_15pure") > 3.84).mean().alias("rej_15pure"), pl.col("cover3").mean(), pl.col("cover5").mean(),
                 pl.col("fn_cover3").mean(), pl.col("fn_cover5").mean(), pl.col("fn_R0").mean())
            .sort("model", "N", "n_trees", "R"))
    with pl.Config(tbl_rows=200, tbl_cols=20, tbl_width_chars=250):
        print(summ)


# =============================================================================================== S2
S2_PERIODS = {20: None, 42: None, 51: ("2026-07-27", "2026-08-08")}
MEM_TURNS = 3
REUSE_N, REUSE_P = 8, 0.25


def simulate_ideas(inp, n_ideas, q, eps, mode, rng, q1=0.0):
    """Synthetic marker uses on the real timeline; returns use arrays, truth per adoption."""
    t, kind, sender, E = inp["t"], inp["kind"], inp["sender"], inp["E"]
    s_all, _ = C.call_starts(inp)
    cc = inp["cc"]
    am = np.where((kind == 0) & (sender >= 0) & ~np.isin(sender, list(cc)))[0]
    # per-agent talk positions, for the memory window (call start 3 turns back)
    prev_s = np.full(len(t), np.iinfo(np.int64).min, dtype=np.int64)
    for a in np.unique(sender[am]):
        p = am[sender[am] == a]
        sp = s_all[p]
        back = np.r_[np.full(MEM_TURNS, np.iinfo(np.int64).min), sp][: len(sp)]
        prev_s[p] = back
    seeds = rng.choice(am, n_ideas, replace=False if n_ideas < len(am) else True)
    U_pos, U_mk, truth = [], [], []
    for i, p0 in enumerate(seeds):
        a0 = int(sender[p0])
        uses = [int(p0)]
        users = {a0: REUSE_N}
        t_end = t[p0] + C.DAY_US
        j0 = np.searchsorted(am, p0, side="right")
        j1 = np.searchsorted(t[am], t_end, side="right")
        for m in am[j0:j1]:
            a = int(sender[m])
            if a in users:
                if users[a] > 0:
                    users[a] -= 1
                    if rng.random() < REUSE_P:
                        uses.append(int(m))
                continue
            up = np.array(uses)
            vis = (t[up] < s_all[m]) & (t[up] >= prev_s[m]) & E[up, a] & (sender[up] != a)
            k = len(set(sender[up[vis]].tolist()))
            if mode == "simple":
                pc = 1 - (1 - q) ** k
            else:
                pc = 0.0 if k == 0 else (q1 if k == 1 else q)
            c_ev = rng.random() < pc
            f_ev = rng.random() < eps
            if c_ev or f_ev:
                uses.append(int(m))
                users[a] = REUSE_N
                truth.append((i, a, bool(c_ev), k))
        U_pos.extend(uses)
        U_mk.extend([i] * len(uses))
    tr = pl.DataFrame(truth, schema=["idea", "agent", "contagion", "k_true"], orient="row") if truth else \
        pl.DataFrame(schema={"idea": pl.Int64, "agent": pl.Int64, "contagion": pl.Boolean, "k_true": pl.Int64})
    return np.array(U_pos, dtype=np.int64), np.array(U_mk, dtype=np.int64), tr


def summarize_assembly(res, smax):
    """The same statistics explore.py computes on real data (subset)."""
    fu, tr, jt = res["first_uses"], res["trees"], res["jitter"]
    nodes = fu.height
    kids = fu.filter((pl.col("status") == 1) & (pl.col("parent") >= 0)).height
    R_hat = kids / nodes if nodes else np.nan
    jtest = S.jitter_test(jt["obs_exposed"].to_numpy(), jt["p_exp_1h"].to_numpy(), jt["idea"].to_numpy(), B=500)
    exp_null = float(jt["p_exp_1h"].sum()) if jt.height else 0.0
    exp_obs = float(jt["obs_exposed"].sum()) if jt.height else 0.0
    # R under the jitter null: replace observed exposed adoptions with their null expectation
    exp_obs_agent = fu.filter((pl.col("status") == 1) & (pl.col("parent") >= 0)).height
    frac_agent_parent = exp_obs_agent / exp_obs if exp_obs else 0.0
    R_jit = (exp_null * frac_agent_parent) / nodes if nodes else np.nan
    off = fu["offspring"].to_numpy()
    fo = S.fit_offspring(off)
    sizes = tr["size"].to_numpy()
    out = dict(nodes=nodes, trees=tr.height, R_hat=R_hat, R_jit=R_jit, k_hat=fo["k"], p_ge2=float((sizes >= 2).mean()),
               p_ge3=float((sizes >= 3).mean()), p_ge5=float((sizes >= 5).mean()),
               jit_excess=jtest.get("excess", np.nan), jit_p=jtest.get("p_boot", np.nan),
               jit_obs=jtest.get("obs_frac", np.nan), jit_null=jtest.get("null_frac", np.nan),
               first_turn_obs=float(jt["obs_first_turn"].mean()) if jt.height else np.nan,
               first_turn_null=float(jt["p_first_1h"].mean()) if jt.height else np.nan)
    if tr.height >= 30:
        cdf, band = S.predict_tail(fo["R"], fo["k"], smax, tr.height, B=400)
        out.update(cover3=bool(band[3][0] <= out["p_ge3"] <= band[3][1]), cover5=bool(band[5][0] <= out["p_ge5"] <= band[5][1]))
        cdf2, band2, R0 = S.predict_tail_fngw(R_hat, fo["k"], smax, tr.height, B=400, n_param=0)
        out.update(fn_cover3=bool(band2[3][0] <= out["p_ge3"] <= band2[3][1]),
                   fn_cover5=bool(band2[5][0] <= out["p_ge5"] <= band2[5][1]), fn_R0=R0, fn_pred3=cdf2[3])
    ar = res["atrisk"]
    nan2 = (np.nan, np.nan)
    dr = S.dose_response(ar, B=200, kcol="kbin") if ar.height else {}      # cumulative k
    drr = S.dose_response(ar, B=200, kcol="krbin") if ar.height else {}    # recency k (A2)
    hr10, (lo10, hi10) = drr.get("hr10", np.nan), drr.get("hr10_ci", nan2)
    out.update(hr21=dr.get("hr21", np.nan), hr21r=drr.get("hr21", np.nan), hr21r_lo=drr.get("hr21_ci", nan2)[0],
               hr21r_hi=drr.get("hr21_ci", nan2)[1], hr10=hr10, hr10_lo=lo10, hr10_hi=hi10,
               n_k0_adopts=drr.get("n_k0_adopts", np.nan),
               R_c=R_hat * max(0.0, 1 - 1 / hr10) if np.isfinite(hr10) and hr10 > 0 else (R_hat if hr10 == np.inf else np.nan),
               R_c_lo=R_hat * max(0.0, 1 - 1 / lo10) if np.isfinite(lo10) and lo10 > 0 else 0.0)
    rx = res["roomx"]
    if rx.height:
        ne, na, ue, ua = (rx[c].sum() for c in ("n_exposed", "n_exposed_adopt", "n_unexposed", "n_unexposed_adopt"))
        out.update(p_adopt_exp=na / ne if ne else np.nan, p_adopt_unexp=ua / ue if ue else np.nan, n_unexp=int(ue))
    return out


_INP = {}


def _s2_init():
    sh = C.Shared()
    for g, dates in S2_PERIODS.items():
        days = sh.period_days(g)
        if dates:
            days = [d for d in days if dates[0] <= d < dates[1]]
        empty = pl.DataFrame(schema={"msg": pl.UInt32, "marker": pl.Int64, "cls": pl.UInt8})
        _INP[g] = C.period_inputs(sh, g, days=days, uses=empty)


def s2_task(task):
    g, q, eps, mode, q1, rep, n_ideas = task
    inp = dict(_INP[g])
    rng = np.random.default_rng(zlib.crc32(repr((g, q, eps, mode, q1, rep)).encode()))
    t0 = time.time()
    upos, umk, truth = simulate_ideas(inp, n_ideas, q, eps, mode, rng, q1=q1)
    inp.update(use_pos=upos, use_marker=umk, use_cls=np.full(len(upos), 2, dtype=np.int8))
    res = C.assemble(inp, atrisk_cap=n_ideas, seed=rep)
    smax = res["meta"]["n_agents"]
    out = summarize_assembly(res, smax)
    nodes = out["nodes"]
    n_c = int(truth["contagion"].sum()) if truth.height else 0
    # classification of true field adoptions
    fu = res["first_uses"].join(truth.rename({"idea": "idea_t"}).with_columns(pl.col("idea_t").alias("idea")),
                                on=["idea", "agent"], how="left")
    f_true = fu.filter(pl.col("contagion") == False)  # noqa: E712
    c_true = fu.filter(pl.col("contagion") == True)  # noqa: E712
    out.update(goal=g, q=q, eps=eps, mode=mode, q1=q1, rep=rep, n_ideas=n_ideas, R_true=n_c / nodes if nodes else np.nan,
               n_field_true=f_true.height, field_called_exposed=float((f_true["status"] == 1).mean()) if f_true.height else np.nan,
               contagion_called_exposed=float((c_true["status"] == 1).mean()) if c_true.height else np.nan,
               n_agents=smax, secs=time.time() - t0)
    return out


def run_s2():
    tasks = []
    n_ideas = {20: 900, 42: 900, 51: 600}
    for g in S2_PERIODS:
        for q in (0.0, 0.005, 0.015, 0.04):
            for eps in (0.0005, 0.002):
                reps = 6 if q == 0.0 else (3 if q == 0.005 else 1)
                for rep in range(reps):
                    tasks.append((g, q, eps, "simple", 0.0, rep, n_ideas[g]))
        tasks.append((g, 0.06, 0.0005, "complex", 0.002, 0, n_ideas[g]))
        tasks.append((g, 0.015, 0.0, "simple", 0.0, 0, n_ideas[g]))
    t0 = time.time()
    with Pool(N_WORKERS, initializer=_s2_init) as pool:
        res = pool.map(s2_task, tasks, chunksize=1)
    OUT.mkdir(parents=True, exist_ok=True)
    df = pl.DataFrame(res)
    df.write_parquet(OUT / "s2.parquet", compression="zstd")
    print(f"S2: {len(res)} runs in {time.time() - t0:.0f}s")
    cols = ["goal", "mode", "q", "eps", "rep", "nodes", "R_true", "R_hat", "R_c", "R_c_lo", "field_called_exposed", "jit_excess",
            "jit_p", "hr10", "hr10_lo", "hr10_hi", "n_k0_adopts", "hr21", "hr21r", "hr21r_lo", "hr21r_hi",
            "p_adopt_exp", "p_adopt_unexp", "cover3", "cover5", "fn_cover3", "fn_cover5", "fn_R0", "p_ge2", "p_ge3"]
    with pl.Config(tbl_rows=200, tbl_cols=30, tbl_width_chars=300, float_precision=3):
        print(df.select([c for c in cols if c in df.columns]).sort("goal", "mode", "q", "eps", "rep"))


if __name__ == "__main__":
    {"s1": run_s1, "s2": run_s2}[sys.argv[1]]()
