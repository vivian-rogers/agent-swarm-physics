"""H52 round 2, synthetic world v2 (card section "Round 2"): which quote-free DiD candidate is admissible, and does
the read vs in-flight contrast resist convergence and quoting?

Part A (content candidates) on the round-1 G51 and G04 row skeletons (real calls, ages, naming, idleness, room sizes)
plus the round-2 skeleton (real ages of each row's pre and post statements):
- room topic T(t): OU process (tau = 60 min, stationary norm ~1), shared by all recipients and by agent messages;
- recipient state c_j(t) = Tday + z_j + z_jd + T(t); statement = unit(c_j(t) + sigma eps), sigma calibrated to the real
  consecutive-statement cosine (G51 0.42, G04 0.68);
- message u = unit(b unit(Tday + T(t_m)) + sqrt(1 - b^2) r), b = 0.6 agents, 0.35 humans; nudges are a template;
  a named message quotes its recipient's last statement (agents 0.6, humans 0.3);
- post statements = unit(c_j(t) + sigma eta + kappa sum_i g_i unit(u_i perp S_1..S_k)), g = round-1 salience
  (named x4) + pi [human];
- worlds N0 (kappa = 0, pi = 0), S0 (kappa, pi = 0), S1 (kappa, pi); truths by common random numbers.
Part B (partition contrast) on the real round-2 pair skeletons of G51 and G04 (humans + agents): synthetic vectors,
worlds W0, WH (read pulse), WC (shared OU topic, pure convergence), WQ (quoting of named readers' before message).

Usage: uv run python hypotheses/H52-humans-loud-agents/analysis/r2_synthetic.py A|B [--reps 10] [--B 200]
Writes data/processed/H52-humans-loud-agents/r2/synthetic/{A_replicates.parquet, A_summary.json, B_summary.json}.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h52lib as L  # noqa: E402
import r2lib as R  # noqa: E402
import synthetic as S  # noqa: E402  (round-1 skeleton loader and relabeller, same hypothesis)
import estimate as E  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

D = 32
OUT = R.R2OUT / "synthetic"
SIGMA = {"G51": 2.26, "G04": 1.32}
KAPPA = 0.09
PI = 0.9
CANDS = ("chi_q1", "chi_qm", "chi_qa", "chi_q1_jd", "chi_qm_jd", "chi_dd", "chi")


def ou_topic(times: np.ndarray, rng, tau: float = 3600.0) -> np.ndarray:
    """OU process in D dims sampled at sorted unique times; stationary per-dim sd 1/sqrt(D)."""
    o = np.argsort(times)
    t = times[o]
    X = np.zeros((len(t), D))
    x = rng.normal(size=D) / np.sqrt(D)
    prev = t[0] if len(t) else 0.0
    for i, ti in enumerate(t):
        dt = max(ti - prev, 0.0)
        if dt > 6 * 3600:
            x = rng.normal(size=D) / np.sqrt(D)
        else:
            a = np.exp(-dt / tau)
            x = a * x + np.sqrt(1 - a * a) * rng.normal(size=D) / np.sqrt(D)
        X[i] = x
        prev = ti
    out = np.empty_like(X)
    out[o] = X
    return out


def unit_vec(rng, n=None):
    v = rng.normal(size=(D,) if n is None else (n, D))
    return L.unit(v)


# per-skeleton world parameters (Amendment R2-A1: calibrated to structural moments of the real rows; see card)
PARAMS = {
    "G51": dict(a_s=0.05, a_T=1.0, sigma=1.46, b_a=0.6, b_h=0.3, wn_a=0.27, wq_a=0.05, wn_h=0.12, wq_h=0.05),
    "G04": dict(a_s=1.0, a_T=0.55, sigma=1.7, b_a=0.35, b_h=0.21, wn_a=0.18, wq_a=0.05, wn_h=0.0, wq_h=0.03),
}
# uncalibrated first draft (kept for the record; produced the A_draft run)
PARAMS_DRAFT = dict(a_s=1.0, a_T=1.0, b_a=0.6, b_h=0.35, wn_a=0.0, wq_a=0.6, wn_h=0.0, wq_h=0.3)


def simulate_A(Rk: pl.DataFrame, cls: np.ndarray, world: str, rng, prm: dict, B: int, moments_only: bool = False) -> dict:
    sigma = prm["sigma"]
    n = Rk.height
    day = Rk["day_idx"].to_numpy(); recv = Rk["recv"].to_numpy().astype(int)
    named = Rk["named"].to_numpy().astype(bool); age = Rk["age_s"].to_numpy().astype(float)
    idle = Rk["idle"].to_numpy().astype(bool); nrecv = Rk["n_recv"].to_numpy().astype(float)
    tc = Rk["tc"].to_numpy(); msg = Rk["msg"].to_numpy().astype(np.int64)
    tm = tc - age
    calls, call_idx = np.unique(Rk["turn_id"].to_numpy(), return_inverse=True)
    nc = len(calls)
    first = np.zeros(nc, int); first[call_idx[::-1]] = np.arange(n)[::-1]
    pre_age = np.stack([Rk[f"pre{k}"].to_numpy() for k in range(L.K_BASIS)], 1)[first]      # (nc, K) right-aligned
    post_age = np.stack([Rk[f"post{k}"].to_numpy() for k in range(L.K_POST)], 1)[first]
    pm_cnt = Rk["pmask"].to_numpy()[first]
    ctc = tc[first]; cday = day[first]; crecv = recv[first]
    # topic at all needed times (per day, one OU path)
    need_t = [ctc[:, None] - np.nan_to_num(pre_age, nan=0.0), ctc[:, None] + np.nan_to_num(post_age, nan=0.0)]
    T_pre = np.zeros((nc, L.K_BASIS, D)); T_post = np.zeros((nc, L.K_POST, D)); T_msg = np.zeros((n, D))
    for dd in np.unique(day):
        cm = cday == dd
        rm = day == dd
        times = np.concatenate([need_t[0][cm].ravel(), need_t[1][cm].ravel(), tm[rm]])
        Tt = ou_topic(times, rng)
        a = need_t[0][cm].size; b = need_t[1][cm].size
        T_pre[cm] = Tt[:a].reshape(-1, L.K_BASIS, D)
        T_post[cm] = Tt[a:a + b].reshape(-1, L.K_POST, D)
        T_msg[rm] = Tt[a + b:]
    agents = np.unique(recv); days = np.unique(day)
    Tday = {int(d_): unit_vec(rng) for d_ in days}
    zj = {int(a): 1.2 * unit_vec(rng) for a in agents}
    zjd = {(int(a), int(d_)): 0.5 * unit_vec(rng) for a in agents for d_ in days}
    a_s, a_T = prm["a_s"], prm["a_T"]
    TD = np.stack([Tday[int(d_)] for d_ in cday])
    stable = a_s * TD + np.stack([zj[int(crecv[i])] + zjd[(int(crecv[i]), int(cday[i]))] for i in range(nc)])
    kpre = (~np.isnan(pre_age)).sum(1)
    Vpre = L.unit(stable[:, None, :] + a_s * a_T * T_pre + sigma * rng.normal(size=(nc, L.K_BASIS, D)) / np.sqrt(D))
    Vpre[np.isnan(pre_age)] = 0.0
    # messages
    template = unit_vec(rng)
    umsg, mcls, mday = {}, {}, {}
    for i in range(n):
        m = msg[i]
        if m in umsg:
            continue
        c = cls[i]
        if c == 2:
            umsg[m] = L.unit(0.8 * template + 0.6 * unit_vec(rng))
        else:
            b = prm["b_a"] if c == 0 else prm["b_h"]
            umsg[m] = L.unit(b * L.unit(Tday[int(day[i])] + a_T * T_msg[i]) + np.sqrt(1 - b * b) * unit_vec(rng))
        mcls[m] = c; mday[m] = day[i]
    quoted = set()
    for i in np.flatnonzero(named & (cls != 2)):
        m = msg[i]
        ci = call_idx[i]
        if m in quoted or kpre[ci] == 0:
            continue
        cj = L.unit(stable[ci] + a_s * a_T * T_msg[i])          # the named recipient's state at t_m
        wn, wq = (prm["wn_a"], prm["wq_a"]) if cls[i] == 0 else (prm["wn_h"], prm["wq_h"])
        umsg[m] = L.unit(umsg[m] + wn * cj + wq * Vpre[ci, -1])
        quoted.add(m)
    if moments_only:
        U = np.stack([umsg[m] for m in msg])
        Sk = Vpre[call_idx, -1]; Sk1 = Vpre[call_idx, -2]
        okk = kpre[call_idx] >= 1; okk1 = kpre[call_idx] >= 2
        ck = np.where(okk, (U * Sk).sum(1), np.nan); ck1 = np.where(okk1, (U * Sk1).sum(1), np.nan)
        gap = pre_age[:, -2] - pre_age[:, -1]
        css = np.where(kpre >= 2, (Vpre[:, -1] * Vpre[:, -2]).sum(1), np.nan)
        out = {"cos_SS": float(np.nanmean(css)), "cos_SS_short": float(np.nanmean(css[gap < 120])),
               "cos_SS_long": float(np.nanmean(css[gap > 1200]))}
        for lab, mk in (("ag_named", (cls == 0) & named), ("ag_unnamed", (cls == 0) & ~named), ("human", cls == 1),
                        ("human_named", (cls == 1) & named)):
            out[lab] = (round(float(np.nanmean(ck[mk])), 3), round(float(np.nanmean(ck1[mk])), 3))
        return out
    U = np.stack([umsg[m] for m in msg])
    Bas = L.orth_basis_batched(Vpre[call_idx])
    uh, nrm = L.perp(U.astype(np.float64), Bas)
    nov = np.where(kpre[call_idx] > 0, nrm, np.nan)
    sal = (1 + 3 * named) * np.exp(-age / 600) * (1 + 0.5 * idle) * np.sqrt(4 / (nrecv + 3)) * (0.3 + np.nan_to_num(nov, nan=1.0))
    eta = sigma * rng.normal(size=(nc, L.K_POST, D)) / np.sqrt(D)
    has_post = ~np.isnan(post_age)
    kap = 0.0 if world == "N0" else KAPPA
    pi = PI if world == "S1" else 0.0

    def post(kappa, pi_):
        g = sal + pi_ * (cls == 1)
        push = np.zeros((nc, D))
        np.add.at(push, call_idx, (kappa * g)[:, None] * uh)
        Q = L.unit(stable[:, None, :] + a_s * a_T * T_post + eta + push[:, None, :])
        Q[~has_post] = 0.0
        return Q
    # statement store: pre (nc*K) then post (nc*K_POST)
    nb = nc * L.K_BASIS
    Vall = np.zeros((nb + nc * L.K_POST, D), np.float32)
    Vall[:nb] = Vpre.reshape(-1, D)
    bidx_c = np.where(~np.isnan(pre_age), np.arange(nc)[:, None] * L.K_BASIS + np.arange(L.K_BASIS)[None, :], -1)
    pmask_c = (bidx_c >= 0) & (np.arange(L.K_BASIS)[None, :] >= L.K_BASIS - np.minimum(pm_cnt, L.K_PRE)[:, None])
    qidx_c = np.where(has_post, nb + np.arange(nc)[:, None] * L.K_POST + np.arange(L.K_POST)[None, :], -1)
    bidx, pmask, qidx = bidx_c[call_idx], pmask_c[call_idx], qidx_c[call_idx]
    pool = {}
    for c in (0, 1, 2):
        ms = np.array([m for m in umsg if mcls[m] == c], np.int64)
        if len(ms):
            pool[c] = (ms, np.array([mday[m] for m in ms]))
    plx = L.draw_placebos(cls, day, recv, pool, rng)
    Up = np.full(plx.shape + (D,), np.nan, np.float32)
    okp = plx >= 0
    Up[okp] = np.stack([umsg[m] for m in plx[okp]])
    stats = {}
    for tag, (kk, pp) in (("obs", (kap, pi)), ("cfpi", (kap, 0.0)), ("cfk", (0.0, 0.0))):
        if tag != "obs" and world == "N0":
            stats[tag] = stats["obs"]
            continue
        if tag == "cfpi" and pi == 0.0:
            stats[tag] = stats["obs"]
            continue
        Vall[nb:] = post(kk, pp).reshape(-1, D)
        pc = R.content_rows_r2(Vall, bidx, pmask, qidx, U.astype(np.float32), Up, call_id=call_idx)
        cand = R.candidates(pc)
        r1 = L.content_rows(Vall, bidx, pmask, qidx, U.astype(np.float32), Up)
        cand["chi_dd"] = r1["chi_dd"]; cand["chi"] = r1["chi"]
        stats[tag] = cand
    df = Rk.with_columns(pl.Series("cls", cls.astype(np.int8)), pl.Series("nov", nov).fill_nan(None),
                         pl.Series("y30", np.zeros(n)), pl.Series("rep", np.zeros(n, bool)), pl.Series("st", np.zeros(n)),
                         pl.Series("chi", np.zeros(n)))
    d = E.prepare(df)
    s_con = d["s_con"].to_numpy(); s_nn = d["s_nn"].to_numpy()
    c_ = d["cls"].to_numpy(); nm = d["named"].to_numpy().astype(bool)
    clu, rule = E.cluster_ids(d, 1)
    cl_day = d["day_idx"].to_numpy().astype(np.int64)
    keep = ~Rk["kickoff"].to_numpy()
    out = {"alpha": stats["obs"]["alpha"]}
    for cnd in CANDS:
        y = np.asarray(stats["obs"][cnd], float)[keep]
        prem = L.att(y, c_ == 1, c_ == 0, s_con, clu, B=B, naive=False)
        nam = L.att(y, (c_ == 0) & nm, (c_ == 0) & ~nm, s_nn, cl_day, B=B, naive=False)
        dpi = y - np.asarray(stats["cfpi"][cnd], float)[keep]
        hm = (c_ == 1) & np.isfinite(dpi)
        dk = y - np.asarray(stats["cfk"][cnd], float)[keep]
        tn = L.att(dk, (c_ == 0) & nm, (c_ == 0) & ~nm, s_nn, cl_day, B=2, naive=False)
        out[cnd] = dict(prem=prem["att"], prem_lo=prem["ci"][0], prem_hi=prem["ci"][1], prem_truth=float(dpi[hm].mean()) if hm.any() else np.nan,
                        nam=nam["att"], nam_lo=nam["ci"][0], nam_hi=nam["ci"][1], nam_truth=tn["att"], n_h=prem.get("n_t"))
    return out


def calibrate(max_rows: int):
    for sk in ("G51", "G04"):
        Rk = S.load_skeleton(sk, max_rows, np.random.default_rng(L.SEED))
        Rk = Rk.join(pl.read_parquet(R.R2OUT / sk / "r2_skel.parquet"), on="item", how="left")
        rng = np.random.default_rng(7)
        print(sk, simulate_A(Rk, Rk["cls"].to_numpy(), "N0", rng, PARAMS[sk], 0, moments_only=True))


def run_A(reps: int, B: int, max_rows: int):
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    t0 = time.time()
    for sk in ("G51", "G04"):
        rng0 = np.random.default_rng(L.SEED)
        Rk = S.load_skeleton(sk, max_rows, rng0)
        skel = pl.read_parquet(R.R2OUT / sk / "r2_skel.parquet")
        Rk = Rk.join(skel, on="item", how="left")
        share = 0.03 if sk == "G51" else 0.25
        for labels in ("real", "confounded"):
            for world in ("N0", "S0", "S1"):
                for rep in range(reps):
                    rng = np.random.default_rng([L.SEED, 52, hash((sk, labels, world)) % 10_000, rep])
                    cls = S.relabel(Rk, labels, rng, share)
                    o = simulate_A(Rk, cls, world, rng, PARAMS[sk], B)
                    for cnd in CANDS:
                        rows.append(dict(skeleton=sk, labels=labels, world=world, rep=rep, cand=cnd, alpha=o["alpha"], **o[cnd]))
                    print(f"A {sk} {labels} {world} {rep} ({time.time() - t0:.0f} s)", flush=True)
                pl.DataFrame(rows).write_parquet(OUT / "A_replicates.parquet")
    df = pl.DataFrame(rows)
    df.write_parquet(OUT / "A_replicates.parquet")
    summarize_A(df)


def summarize_A(df: pl.DataFrame) -> dict:
    df = df.with_columns((pl.col("prem") - pl.col("prem_truth")).alias("perr"), (pl.col("nam") - pl.col("nam_truth")).alias("nerr"),
                         ((pl.col("nam_lo") <= 0) & (pl.col("nam_hi") >= 0)).alias("nam_cov0"),
                         (pl.col("nam_hi") < 0).alias("nam_below0"),
                         ((pl.col("prem_lo") <= pl.col("prem_truth")) & (pl.col("prem_hi") >= pl.col("prem_truth"))).alias("pcov"),
                         (pl.col("prem_lo") > 0).alias("ppow"))
    g = df.group_by("skeleton", "labels", "world", "cand").agg(
        pl.len().alias("reps"), pl.col("prem_truth").mean(), pl.col("perr").mean().alias("prem_bias"),
        (pl.col("perr") ** 2).mean().sqrt().alias("prem_rmse"), pl.col("pcov").mean().alias("prem_cov"), pl.col("ppow").mean().alias("prem_power"),
        pl.col("nam_truth").mean(), pl.col("nam").mean().alias("nam_mean"), pl.col("nerr").mean().alias("nam_bias"),
        pl.col("nam_cov0").mean().alias("nam_cov0"), pl.col("nam_below0").mean().alias("nam_below0"), pl.col("alpha").mean()
    ).sort("cand", "skeleton", "labels", "world")
    # admissibility (card's selection rule)
    adm = {}
    for cnd in ("chi_q1", "chi_qm", "chi_qa", "chi_q1_jd", "chi_qm_jd"):
        s = g.filter(pl.col("cand") == cnd)
        a = s.filter(pl.col("world").is_in(["S0", "S1"]))["prem_bias"].abs().max() <= 0.006
        b = s.filter(pl.col("world") == "N0")["nam_cov0"].min() >= 0.8
        s1 = s.filter((pl.col("world") == "S1") & (pl.col("skeleton") == "G51"))
        c = bool(((s1["prem_bias"].abs() / s1["prem_truth"].abs()) <= 0.3).all())
        rm = df.filter((pl.col("cand") == cnd) & pl.col("world").is_in(["S0", "S1"]))["perr"]
        adm[cnd] = dict(a_bias=bool(a), b_naming_null=bool(b), c_recovery=c, admissible=bool(a and b and c),
                        rmse=float(np.sqrt((rm.to_numpy() ** 2).mean())))
    ok = {k: v for k, v in adm.items() if v["admissible"]}
    primary = None
    if ok:
        best = min(ok, key=lambda k: ok[k]["rmse"])
        primary = "chi_q1" if ("chi_q1" in ok and ok["chi_q1"]["rmse"] <= 1.1 * ok[best]["rmse"]) else best
    S_ = {"table": g.to_dicts(), "admissibility": adm, "primary": primary}
    L.jdump(S_, OUT / "A_summary.json")
    with pl.Config(tbl_rows=100, tbl_cols=20, tbl_width_chars=250, float_precision=4):
        print(g.select("cand", "skeleton", "labels", "world", "prem_truth", "prem_bias", "prem_cov", "prem_power", "nam_truth",
                       "nam_mean", "nam_bias", "nam_cov0", "nam_below0", "alpha"))
    print(adm, "primary:", primary)
    return S_


# ============================================================================ Part B: partition contrast
def run_B(reps: int, n_boot: int, amp: float = 0.15):
    OUT.mkdir(parents=True, exist_ok=True)
    res = {}
    t0 = time.time()
    for sk in ("G51", "G04"):
        P = pl.read_parquet(R.R2OUT / sk / "r2_pairs.parquet")
        P = P.with_columns(pl.col("named").fill_null(False))
        msgs = P["msg"].to_numpy(); bm = P["before_msg"].to_numpy(); am = P["after_msg"].to_numpy()
        agent = P["recv"].to_numpy()
        tmm = P["t_m"].to_numpy(); lag = P["lag_s"].to_numpy().astype(float); age = P["age_s"].to_numpy().astype(float)
        t_before = tmm - age; t_after = tmm + lag
        stm_ids = np.unique(np.concatenate([bm, am]))
        st_t = {}
        for ids, ts in ((bm, t_before), (am, t_after)):
            for i, t in zip(ids, ts):
                st_t[int(i)] = t
        st_agent = {}
        for ids in (bm, am):
            for i, a in zip(ids, agent):
                st_agent[int(i)] = a
        um = np.unique(msgs)
        m_t = dict(zip(msgs.tolist(), tmm.tolist()))
        for world in ("W0", "WH", "WC", "WQ"):
            for cl in (1, 0):
                sel = (P["cls"] == cl).to_numpy()
                if sel.sum() < 50:
                    continue
                fires, Cs, As = {"delta": 0, "delta_q": 0}, {"delta": [], "delta_q": []}, []
                for rep in range(reps):
                    rng = np.random.default_rng([52, rep, hash((sk, world, cl)) % 10_000])
                    times = np.array([st_t[int(i)] for i in stm_ids] + [m_t[m] for m in um])
                    Tt = ou_topic(times, rng) if world == "WC" else np.zeros((len(times), D))
                    Tst = dict(zip(stm_ids.tolist(), Tt[:len(stm_ids)])); Tm = dict(zip(um.tolist(), Tt[len(stm_ids):]))
                    agents = np.unique(agent)
                    off = {int(a): 1.0 * unit_vec(rng) for a in agents}
                    Z = {int(i): off[int(st_agent[int(i)])] + 1.5 * rng.normal(size=D) / np.sqrt(D) + 2.0 * Tst[int(i)] for i in stm_ids}
                    Em = {int(m): L.unit(unit_vec(rng) + 2.0 * Tm[int(m)]) for m in um}
                    if world == "WQ":
                        for k in np.flatnonzero(P["named"].to_numpy()):
                            Em[int(msgs[k])] = L.unit(Em[int(msgs[k])] + 0.6 * L.unit(Z[int(bm[k])]))
                    if world == "WH":
                        for k in np.flatnonzero((P["arm"] == "read").to_numpy()):
                            Z[int(am[k])] = Z[int(am[k])] + amp * np.linalg.norm(Z[int(am[k])]) * Em[int(msgs[k])]
                    Zu = {i: L.unit(v) for i, v in Z.items()}
                    pool = np.unique(msgs[sel])
                    e = np.stack([Em[int(m)] for m in msgs]); zb = np.stack([Zu[int(i)] for i in bm]); za = np.stack([Zu[int(i)] for i in am])
                    dec_idx = rng.integers(len(pool), size=(len(um), 50))
                    mpos = {int(m): k for k, m in enumerate(um)}
                    Dm = np.stack([Em[int(m)] for m in pool])
                    rowsD = Dm[dec_idx[[mpos[int(m)] for m in msgs]]]           # (n, 50, D)
                    dz = za - zb
                    dl = {}
                    dl["delta"] = (dz * e).sum(1) - np.einsum("nkd,nd->nk", rowsD, dz).mean(1)
                    eq = L.unit(e - (e * zb).sum(1, keepdims=True) * zb)
                    Dq = rowsD - np.einsum("nkd,nd->nk", rowsD, zb)[..., None] * zb[:, None, :]
                    Dq = Dq / np.maximum(np.linalg.norm(Dq, axis=2, keepdims=True), 1e-9)
                    dl["delta_q"] = (za * eq).sum(1) - np.einsum("nkd,nd->nk", Dq, za).mean(1)
                    for col in ("delta", "delta_q"):
                        Q = P.with_columns(pl.Series(col, dl[col])).filter(pl.Series(sel))
                        r = R.partition_contrast(Q, col, n_boot=n_boot, seed=rep)
                        fires[col] += int(r["C_ci"][0] > 0 or r["C_ci"][1] < 0) if world != "WH" else int(r["C_ci"][0] > 0)
                        Cs[col].append(r["C"])
                        if col == "delta":
                            As.append(r["A"])
                res[f"{sk}_{world}_cls{cl}"] = dict(reps=reps, rate=fires["delta"] / reps, rate_q=fires["delta_q"] / reps,
                                                    mean_C=float(np.nanmean(Cs["delta"])), mean_C_q=float(np.nanmean(Cs["delta_q"])),
                                                    mean_A=float(np.nanmean(As)),
                                                    n_inflight=int(((P["arm"] == "inflight").to_numpy() & sel).sum()))
                print(sk, world, cl, res[f"{sk}_{world}_cls{cl}"], f"({time.time() - t0:.0f} s)", flush=True)
    L.jdump(res, OUT / "B_summary.json")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("part")
    ap.add_argument("--reps", type=int, default=10)
    ap.add_argument("--B", type=int, default=200)
    ap.add_argument("--max-rows", type=int, default=60000)
    a = ap.parse_args()
    if a.part == "A":
        run_A(a.reps, a.B, a.max_rows)
    elif a.part == "calib":
        calibrate(a.max_rows)
    elif a.part == "Asum":
        summarize_A(pl.read_parquet(OUT / "A_replicates.parquet"))
    elif a.part == "B":
        run_B(a.reps, a.B)


if __name__ == "__main__":
    main()
