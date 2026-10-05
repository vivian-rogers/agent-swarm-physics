"""H34 round 2, R1: heterogeneous branching. Gamma mixture over idea-level R0 on finite-N GW trees (Gamma-FN).

Model (card, "Round 2 / R1"): idea i draws R0_i ~ Gamma(shape alpha, mean mu); each tree of idea i is an FN-GW tree with
Poisson offspring and depletion on N_fit nodes (offspring of a generation ~ Poisson(R0 * a * S / (N - 1)), capped at S).
The size law P(s | R0) is computed exactly by dynamic programming on (S, a); R0 is integrated on a fixed log grid.

  uv run python hypotheses/H34-idea-cascades/analysis/r2_mixture.py synth_a      # S-R1a: pure Gamma-FN / NB worlds
  uv run python hypotheses/H34-idea-cascades/analysis/r2_mixture.py synth_b      # S-R1b: S2 skeleton worlds (#20, #42, #51 seg)
  uv run python hypotheses/H34-idea-cascades/analysis/r2_mixture.py real [--src r1b|sem_bge_small|sem_gte_modernbert]
Outputs: data/processed/H34-idea-cascades/r2/mixture/
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
import zlib
from functools import lru_cache
from multiprocessing import Pool
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import optimize, special, stats  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h34stats as S  # noqa: E402
import h34core as C  # noqa: E402

R2 = C.OUT / "r2"
OUTM = R2 / "mixture"
N_WORKERS = 2
GRID = np.geomspace(0.002, 8.0, 600)
EDGES = np.r_[0.0, np.sqrt(GRID[1:] * GRID[:-1]), np.inf]
ALPHA_MAX = 500.0
MIN_TRAIN_TREES, MIN_TEST_TREES = 30, 20     # round-1 day-ahead eligibility
MIN_TREES_SHAPE = 50


# ============================================================================================ exact FN-GW (Poisson) size law
@lru_cache(maxsize=64)
def fngw_table(N: int) -> np.ndarray:
    """P[j, s-1] = P(tree size = s | R0 = GRID[j]) for the finite-N GW with Poisson offspring and depletion (fngw_sim rule:
    the generation's total offspring ~ Poisson(R0 * a * S / (N - 1)), capped at the S susceptibles left)."""
    G = len(GRID)
    out = np.zeros((G, N))
    if N <= 1:
        out[:, 0] = 1.0
        return out
    A = {(N - 1, 1): np.ones(G)}
    for _ in range(N + 1):
        if not A:
            break
        B = {}
        for (Sx, a), p in A.items():
            lam = GRID * (a * Sx / (N - 1))
            n = np.arange(Sx)
            pn = stats.poisson.pmf(n[None, :], lam[:, None])           # (G, Sx)
            tail = np.clip(1.0 - pn.sum(1), 0.0, 1.0)
            out[:, N - Sx - 1] += p * pn[:, 0]                          # n = 0: absorbed at size N - Sx
            out[:, N - 1] += p * tail                                   # n = Sx: everyone reached
            for k in range(1, Sx):
                key = (Sx - k, k)
                B[key] = B.get(key, 0.0) + p * pn[:, k]
        A = {k: v for k, v in B.items() if v.max() > 1e-16}
    return out / out.sum(1, keepdims=True)


def gamma_weights(mu: float, alpha: float) -> np.ndarray:
    cdf = stats.gamma.cdf(EDGES, a=alpha, scale=mu / alpha)
    w = np.diff(cdf)
    return np.maximum(w, 0.0) / max(w.sum(), 1e-300)


# ============================================================================================ forests -> signatures
def signatures(trees: pl.DataFrame, N: int) -> tuple[list[tuple], np.ndarray]:
    """Group ideas by the multiset of their tree sizes (capped at N). Returns signature tuples and counts."""
    g = (trees.with_columns(pl.col("size").clip(1, N))
         .group_by("idea").agg(pl.col("size").sort().alias("sz")))
    c = g.group_by("sz").len()
    sig = [tuple(x) for x in c["sz"].to_list()]
    return sig, c["len"].to_numpy().astype(float)


def sig_loglik(sig: list[tuple], N: int) -> np.ndarray:
    """L[k, j] = sum over the trees of signature k of log P(s | GRID[j])."""
    lP = np.log(np.maximum(fngw_table(N), 1e-300))                    # (G, N)
    L = np.zeros((len(sig), len(GRID)))
    for k, t in enumerate(sig):
        for s in t:
            L[k] += lP[:, s - 1]
    return L


def fit_gamma(L: np.ndarray, cnt: np.ndarray, x0=None) -> dict:
    def nll(th):
        mu, al = math.exp(th[0]), math.exp(min(th[1], math.log(ALPHA_MAX)))
        lw = np.log(np.maximum(gamma_weights(mu, al), 1e-300))
        return -float(np.sum(cnt * special.logsumexp(L + lw[None, :], axis=1)))
    starts = [x0] if x0 is not None else [[math.log(m), math.log(a)] for m in (0.1, 0.3) for a in (0.3, 2.0, 30.0)]
    best = None
    for s0 in starts:
        r = optimize.minimize(nll, x0=s0, method="Nelder-Mead", options=dict(xatol=1e-4, fatol=1e-5, maxiter=2000))
        if best is None or r.fun < best.fun:
            best = r
    mu, al = math.exp(best.x[0]), math.exp(min(best.x[1], math.log(ALPHA_MAX)))
    return dict(mu=mu, alpha=al, nll=float(best.fun), x=list(best.x))


def fit_h0(L: np.ndarray, cnt: np.ndarray) -> dict:
    """Homogeneous FN-GW-Poisson: one R0 for all ideas (maximum over the grid, parabolic refinement in log R0)."""
    ll = (cnt[:, None] * L).sum(0)
    j = int(np.argmax(ll))
    R0 = GRID[j]
    if 0 < j < len(GRID) - 1:
        x = np.log(GRID[j - 1:j + 2]); y = ll[j - 1:j + 2]
        den = (y[0] - 2 * y[1] + y[2])
        if den < 0:
            R0 = float(math.exp(x[1] - 0.5 * (x[2] - x[1]) * (y[2] - y[0]) / den))
    return dict(R0=float(R0), nll=float(-ll.max()))


def marginal(mu: float, alpha: float, N: int) -> np.ndarray:
    return gamma_weights(mu, alpha) @ fngw_table(N)


def h0_pmf(R0: float, N: int) -> np.ndarray:
    P = fngw_table(N)
    j = int(np.clip(np.searchsorted(GRID, R0), 1, len(GRID) - 1))
    w = (math.log(R0) - math.log(GRID[j - 1])) / (math.log(GRID[j]) - math.log(GRID[j - 1]))
    w = min(max(w, 0.0), 1.0)
    return (1 - w) * P[j - 1] + w * P[j]


# ============================================================================================ simulation
def sim_forest(R0: np.ndarray, N: int, rng, k: float | None = None):
    """FN-GW trees (one per entry of R0). Returns sizes and root offspring (the first generation)."""
    M = len(R0)
    size = np.ones(M, dtype=np.int64)
    act = np.ones(M, dtype=np.int64)
    Sx = np.full(M, N - 1, dtype=np.int64)
    root_off = np.zeros(M, dtype=np.int64)
    for gen in range(N + 1):
        live = (act > 0) & (Sx > 0)
        if not live.any():
            break
        mu = R0[live] * Sx[live] / max(N - 1, 1) * act[live]
        if k is None:
            o = rng.poisson(mu)
        else:
            sh = k * act[live]
            o = rng.negative_binomial(sh, sh / (sh + np.maximum(mu, 1e-12)))
        o = np.minimum(o, Sx[live])
        a2 = np.zeros(M, dtype=np.int64)
        a2[live] = o
        if gen == 0:
            root_off = a2.copy()
        size += a2
        Sx -= a2
        act = a2
    return size, root_off


def root_ratio(sizes: np.ndarray, root_off: np.ndarray) -> float:
    n_tr = len(sizes)
    nr = sizes.sum() - n_tr
    if nr <= 0 or root_off.sum() <= 0:
        return np.nan
    return float(((nr - root_off.sum()) / nr) / (root_off.sum() / n_tr))


def draw_R0(mu, alpha, M, rng):
    return rng.gamma(alpha, mu / alpha, size=M) if np.isfinite(alpha) else np.full(M, mu)


# ============================================================================================ one data set
def boot_counts(trees: pl.DataFrame, N: int, B: int, seed: int):
    """Idea-cluster bootstrap: signature counts re-drawn as multinomial over ideas (same signature list)."""
    sig, cnt = signatures(trees, N)
    rng = np.random.default_rng(seed)
    n = int(cnt.sum())
    return sig, cnt, [rng.multinomial(n, cnt / n).astype(float) for _ in range(B)]


def analyze_trees(trees: pl.DataFrame, fu: pl.DataFrame | None, N: int, seed: int = 0, B_par: int = 25,
                  n_band: int = 1000, n_ratio: int = 200) -> dict:
    sizes = np.minimum(trees["size"].to_numpy(), N)
    sig, cnt, bcnt = boot_counts(trees, N, B_par, seed)
    L = sig_loglik(sig, N)
    fg = fit_gamma(L, cnt)
    h0 = fit_h0(L, cnt)
    lr = max(0.0, 2 * (h0["nll"] - fg["nll"]))
    p_lr = 0.5 * stats.chi2.sf(lr, 1) if lr > 0 else 1.0
    out = dict(N_fit=N, n_trees=int(len(sizes)), n_ideas=int(cnt.sum()), n_sig=len(sig), mu=fg["mu"], alpha=fg["alpha"],
               nll_gamma=fg["nll"], R0_h0=h0["R0"], nll_h0=h0["nll"], LR=lr, p_LR=p_lr,
               obs_p2=float((sizes >= 2).mean()), obs_p3=float((sizes >= 3).mean()), obs_p5=float((sizes >= 5).mean()))
    # parameter bootstrap
    pars = []
    for bc in bcnt:
        f = fit_gamma(L, bc, x0=fg["x"])
        pars.append((f["mu"], f["alpha"]))
    pars = np.array(pars)
    out.update(alpha_lo=float(np.percentile(pars[:, 1], 2.5)), alpha_hi=float(np.percentile(pars[:, 1], 97.5)),
               mu_lo=float(np.percentile(pars[:, 0], 2.5)), mu_hi=float(np.percentile(pars[:, 0], 97.5)),
               cv2=1 / fg["alpha"], cv2_lo=1 / float(np.percentile(pars[:, 1], 97.5)), cv2_hi=1 / float(np.percentile(pars[:, 1], 2.5)))
    # tail band (90%)
    rng = np.random.default_rng(seed + 1)
    pm = marginal(fg["mu"], fg["alpha"], N)
    pms = [pm] + [marginal(m, a, N) for m, a in pars]
    n = len(sizes)
    dr = {x: [] for x in (2, 3, 5)}
    for b in range(n_band):
        p = pms[rng.integers(len(pms))]
        c = rng.multinomial(n, p / p.sum())
        for x in dr:
            dr[x].append(c[x - 1:].sum() / n)
    for x in dr:
        lo, hi = np.percentile(dr[x], [5, 95])
        out.update({f"pred_p{x}": float(pm[x - 1:].sum()), f"lo_p{x}": float(lo), f"hi_p{x}": float(hi),
                    f"cover_p{x}": bool(lo <= out[f"obs_p{x}"] <= hi)})
    out["cover_both"] = bool(out["cover_p3"] and out["cover_p5"])
    ph0 = h0_pmf(h0["R0"], N)
    out.update(h0_pred_p3=float(ph0[2:].sum()), h0_pred_p5=float(ph0[4:].sum()))
    # unfitted: non-root / root offspring ratio
    if fu is not None and fu.height:
        roots = fu.filter(pl.col("gen") == 0); kids = fu.filter(pl.col("gen") > 0)
        o_r = float(roots["offspring"].mean()) if roots.height else np.nan
        o_n = float(kids["offspring"].mean()) if kids.height else np.nan
        out.update(off_root=o_r, off_nonroot=o_n, ratio_obs=o_n / o_r if o_r and o_r > 0 else np.nan)
        rs, rh = [], []
        for b in range(n_ratio):
            m, a = (fg["mu"], fg["alpha"]) if b == 0 else tuple(pars[rng.integers(len(pars))])
            sz, ro = sim_forest(draw_R0(m, a, n, rng), N, rng)
            rs.append(root_ratio(sz, ro))
            if b < 50:
                sz0, ro0 = sim_forest(np.full(n, h0["R0"]), N, rng)
                rh.append(root_ratio(sz0, ro0))
        rs = np.array(rs, float); rs = rs[np.isfinite(rs)]
        if len(rs) > 20:
            lo, hi = np.percentile(rs, [5, 95])
            out.update(ratio_pred=float(np.median(rs)), ratio_lo=float(lo), ratio_hi=float(hi),
                       ratio_cover=bool(lo <= out["ratio_obs"] <= hi), ratio_h0=float(np.nanmedian(rh)))
    return out


# ============================================================================================ day-ahead forecasts
def _betabin(sizes, N):
    sys.path.insert(0, str(HERE))
    from explore import betabin_fit
    return betabin_fit(sizes, N)


def forecast_period(fu: pl.DataFrame, tr: pl.DataFrame, N: int, seed: int) -> list[dict]:
    """Round-1 P7 design (train: trees rooted before day d; test: trees rooted on day d) plus the V3 window (d-2, d-1)."""
    rows = []
    days = sorted(tr["day"].unique().to_list())
    Nf = max(N, int(tr["size"].max()))
    for d in days[1:]:
        tst = tr.filter(pl.col("day") == d)
        s_te = np.minimum(tst["size"].to_numpy(), Nf)
        for win, trn in (("all", tr.filter(pl.col("day") < d)), ("v3", tr.filter((pl.col("day") < d) & (pl.col("day") >= d - 2)))):
            fu_t = fu.join(trn.select("idea", "tree"), on=["idea", "tree"], how="inner")
            if trn.height < MIN_TRAIN_TREES or tst.height < MIN_TEST_TREES or (fu_t["status"] > 0).sum() < 10:
                continue
            s_tr = np.minimum(trn["size"].to_numpy(), Nf)
            sig, cnt = signatures(trn, Nf)
            L = sig_loglik(sig, Nf)
            fg = fit_gamma(L, cnt)
            p_g = marginal(fg["mu"], fg["alpha"], Nf)
            p_bb = _betabin(s_tr, Nf)
            R = float((((fu_t["status"] == 1) & (fu_t["parent"] >= 0)).sum()) / fu_t.height)
            k = S.fit_offspring(fu_t["offspring"].to_numpy())["k"]
            p_fn, _ = S.fngw_pmf(R, k, Nf, seed=seed + d)
            emp = np.bincount(s_tr, minlength=Nf + 1)[1:Nf + 1] + 1.0
            p_emp = emp / emp.sum()
            p_h0 = h0_pmf(fit_h0(L, cnt)["R0"], Nf)

            def ls(p):
                p = np.maximum(np.asarray(p, float), 1e-9)
                p = p / p.sum()
                return float(np.log(p[s_te - 1]).sum())
            rows.append(dict(day=int(d), win=win, n_test=int(len(s_te)), n_train=int(trn.height), mu=fg["mu"], alpha=fg["alpha"],
                             ls_gamma=ls(p_g), ls_betabin=ls(p_bb), ls_fngw=ls(p_fn), ls_emp=ls(p_emp), ls_h0=ls(p_h0),
                             obs_p5=float((s_te >= 5).mean()), pred_p5_gamma=float(p_g[4:].sum()), pred_p5_bb=float(p_bb[4:].sum())))
    return rows


# ============================================================================================ real data
def src_dir(src: str) -> Path:
    return C.OUT / "r1b" if src == "r1b" else R2 / src


def real_task(task):
    g, src = task
    t0 = time.time()
    d = src_dir(src) / f"G{g:02d}"
    meta = json.loads((d / "meta.json").read_text())
    tr = pl.read_parquet(d / "trees.parquet")
    fu = pl.read_parquet(d / "first_uses.parquet")
    N = max(int(meta["N_room"]), int(tr["size"].max()))
    res = analyze_trees(tr, fu, N, seed=g)
    res.update(goal=g, src=src, N_room=int(meta["N_room"]))
    fc = forecast_period(fu, tr, int(meta["N_room"]), seed=g)
    for r in fc:
        r.update(goal=g, src=src)
    print(f"G{g:02d} [{src}] alpha {res['alpha']:.2f} LR {res['LR']:.1f} cover {res['cover_both']} "
          f"ratio {res.get('ratio_obs', np.nan):.2f} in [{res.get('ratio_lo', np.nan):.2f},{res.get('ratio_hi', np.nan):.2f}] "
          f"{len(fc)} fc rows {time.time() - t0:.0f}s", flush=True)
    return res, fc


def run_real(src: str):
    base = src_dir(src)
    periods = sorted(int(p.name[1:]) for p in base.glob("G*") if (p / "meta.json").exists())
    order = sorted(periods, key=lambda x: -1 if x == 51 else x)
    OUTM.mkdir(parents=True, exist_ok=True)
    with Pool(N_WORKERS) as pool:
        outs = pool.map(real_task, [(g, src) for g in order], chunksize=1)
    per = pl.DataFrame([o for o, _ in outs], infer_schema_length=None).sort("goal")
    fc = pl.DataFrame([r for _, f in outs for r in f], infer_schema_length=None)
    per.write_parquet(OUTM / f"periods_{src}.parquet")
    fc.write_parquet(OUTM / f"forecast_{src}.parquet")
    summ = summarize(per, fc)
    (OUTM / f"summary_{src}.json").write_text(json.dumps(summ, indent=1, default=float))
    print(json.dumps(summ, indent=1, default=float))


def summarize(per: pl.DataFrame, fc: pl.DataFrame) -> dict:
    sh = per.filter(pl.col("n_trees") >= MIN_TREES_SHAPE)
    out = dict(n_periods=per.height, n_shape=sh.height,
               P1_cover_both=[int(sh["cover_both"].sum()), sh.height], cover_p3=[int(sh["cover_p3"].sum()), sh.height],
               cover_p5=[int(sh["cover_p5"].sum()), sh.height],
               P2_LR_sig=[int((per["LR"] > 2.71).sum()), per.height], alpha_median=float(per["alpha"].median()),
               alpha_range=[float(per["alpha"].min()), float(per["alpha"].max())])
    if "ratio_cover" in per.columns:
        rc = per.filter(pl.col("ratio_cover").is_not_null())
        out["P4_ratio_cover"] = [int(rc["ratio_cover"].sum()), rc.height]
        out["ratio_obs_median"] = float(rc["ratio_obs"].median()); out["ratio_pred_median"] = float(rc["ratio_pred"].median())
        out["ratio_h0_median"] = float(rc["ratio_h0"].median())
    if fc.height:
        for win in ("all", "v3"):
            f = fc.filter(pl.col("win") == win).group_by("goal").agg(
                *[pl.col(c).sum() for c in ("ls_gamma", "ls_betabin", "ls_fngw", "ls_emp", "ls_h0")], pl.len().alias("days"))
            out[f"P3_{win}"] = dict(periods=f.height, days=int(f["days"].sum()),
                                    beats={r: [int((f["ls_gamma"] > f[f"ls_{r}"]).sum()), f.height] for r in ("betabin", "fngw", "emp", "h0")},
                                    dls_total={r: float((f["ls_gamma"] - f[f"ls_{r}"]).sum()) for r in ("betabin", "fngw", "emp", "h0")})
    return out


# ============================================================================================ synthetic S-R1a
def synth_a_task(task):
    world, N, mu, alpha, n_trees, rep, k = task
    rng = np.random.default_rng(zlib.crc32(repr(task).encode()))
    R0 = draw_R0(mu, alpha, n_trees, rng)
    sizes, ro = sim_forest(R0, N, rng, k=k)
    # offspring per node is needed for the observed ratio: root offspring known, non-root via totals
    tr = pl.DataFrame({"idea": np.arange(n_trees), "tree": np.zeros(n_trees, dtype=np.int64), "size": sizes})
    res = analyze_trees(tr, None, N, seed=rep, B_par=15, n_band=400)
    obs_ratio = root_ratio(sizes, ro)
    # model band for the ratio
    rs = []
    for b in range(100):
        sz, r_ = sim_forest(draw_R0(res["mu"], res["alpha"], n_trees, rng), N, rng)
        rs.append(root_ratio(sz, r_))
    rs = np.array(rs); rs = rs[np.isfinite(rs)]
    lo, hi = (np.percentile(rs, [5, 95]) if len(rs) > 20 else (np.nan, np.nan))
    res.update(world=world, N=N, mu_true=mu, alpha_true=alpha, n_trees_true=n_trees, rep=rep, k_true=k if k else np.inf,
               ratio_obs=obs_ratio, ratio_lo=float(lo), ratio_hi=float(hi), ratio_cover=bool(lo <= obs_ratio <= hi))
    return res


def run_synth_a():
    tasks = []
    for N in (8, 14, 25):
        for mu in (0.15, 0.3):
            for n_trees in (1000, 5000):
                for rep in range(8):
                    for alpha in (0.5, 1.0, 3.0, np.inf):
                        tasks.append(("gammaFN", N, mu, alpha, n_trees, rep, None))
                    tasks.append(("nbFN_k0.5", N, mu, np.inf, n_trees, rep, 0.5))
    t0 = time.time()
    with Pool(N_WORKERS) as pool:
        res = pool.map(synth_a_task, tasks, chunksize=4)
    OUTM.mkdir(parents=True, exist_ok=True)
    df = pl.DataFrame(res, infer_schema_length=None)
    df.write_parquet(OUTM / "synth_a.parquet")
    print(f"S-R1a: {len(res)} runs in {time.time() - t0:.0f}s")
    summ = (df.group_by("world", "alpha_true", "n_trees_true")
            .agg(pl.col("alpha").median().alias("alpha_med"), pl.col("alpha").quantile(0.25).alias("a_q25"),
                 pl.col("alpha").quantile(0.75).alias("a_q75"), (pl.col("mu") / pl.col("mu_true")).median().alias("mu_ratio"),
                 (pl.col("LR") > 2.71).mean().alias("LR_rej"), pl.col("cover_both").mean(), pl.col("cover_p5").mean(),
                 pl.col("ratio_cover").mean(), pl.col("ratio_obs").median(), pl.len())
            .sort("world", "n_trees_true", "alpha_true"))
    with pl.Config(tbl_rows=100, tbl_cols=20, tbl_width_chars=250, float_precision=3):
        print(summ)
    summ.write_parquet(OUTM / "synth_a_summary.parquet")


# ============================================================================================ synthetic S-R1b (skeleton)
S2_PERIODS = {20: None, 42: None, 51: ("2026-07-27", "2026-08-08")}
_INP = {}
REUSE_N, REUSE_P, MEM_TURNS = 8, 0.25, 3


def _sb_init():
    sh = C.Shared()
    for g, dates in S2_PERIODS.items():
        days = sh.period_days(g)
        if dates:
            days = [d for d in days if dates[0] <= d < dates[1]]
        empty = pl.DataFrame(schema={"msg": pl.UInt32, "marker": pl.Int64, "cls": pl.UInt8})
        _INP[g] = C.period_inputs(sh, g, days=days, uses=empty)


def simulate_ideas_het(inp, n_ideas, q_idea, eps, rng):
    """S2 simulator (analysis/synthetic.py, simple contagion) with an idea-specific q (array of length n_ideas)."""
    t, kind, sender, E = inp["t"], inp["kind"], inp["sender"], inp["E"]
    s_all, _ = C.call_starts(inp)
    cc = inp["cc"]
    am = np.where((kind == 0) & (sender >= 0) & ~np.isin(sender, list(cc)))[0]
    prev_s = np.full(len(t), np.iinfo(np.int64).min, dtype=np.int64)
    for a in np.unique(sender[am]):
        p = am[sender[am] == a]
        sp = s_all[p]
        prev_s[p] = np.r_[np.full(MEM_TURNS, np.iinfo(np.int64).min), sp][: len(sp)]
    seeds = rng.choice(am, n_ideas, replace=n_ideas >= len(am))
    U_pos, U_mk = [], []
    for i, p0 in enumerate(seeds):
        q = float(q_idea[i])
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
            if rng.random() < 1 - (1 - min(q, 1.0)) ** k or rng.random() < eps:
                uses.append(int(m))
                users[a] = REUSE_N
        U_pos.extend(uses)
        U_mk.extend([i] * len(uses))
    return np.array(U_pos, dtype=np.int64), np.array(U_mk, dtype=np.int64)


def synth_b_task(task):
    g, q, eps, alpha_q, rep, n_ideas = task
    inp = dict(_INP[g])
    rng = np.random.default_rng(zlib.crc32(repr(task).encode()))
    qi = rng.gamma(alpha_q, q / alpha_q, n_ideas) if np.isfinite(alpha_q) else np.full(n_ideas, q)
    upos, umk = simulate_ideas_het(inp, n_ideas, qi, eps, rng)
    inp.update(use_pos=upos, use_marker=umk, use_cls=np.full(len(upos), 2, dtype=np.int8))
    res = C.assemble(inp, atrisk_cap=1, seed=rep, with_null=False)
    tr, fu = res["trees"], res["first_uses"]
    N = max(int(res["meta"]["n_agents"]), int(tr["size"].max()))
    out = analyze_trees(tr, fu, N, seed=rep, B_par=10, n_band=400, n_ratio=100)
    R_hat = float(((fu["status"] == 1) & (fu["parent"] >= 0)).mean())
    out.update(goal=g, q=q, eps=eps, alpha_q=alpha_q, rep=rep, R_hat=R_hat)
    return out


def run_synth_b():
    tasks = []
    n_id = {20: 900, 42: 900, 51: 600}
    for g in S2_PERIODS:
        for q in (0.005, 0.015, 0.04):
            for eps in (0.0005, 0.002):
                for rep in range(3):
                    tasks.append((g, q, eps, np.inf, rep, n_id[g]))
            for rep in range(2):
                tasks.append((g, q, 0.0005, 1.0, rep, n_id[g]))
    t0 = time.time()
    with Pool(N_WORKERS, initializer=_sb_init) as pool:
        res = pool.map(synth_b_task, tasks, chunksize=1)
    OUTM.mkdir(parents=True, exist_ok=True)
    df = pl.DataFrame(res, infer_schema_length=None)
    df.write_parquet(OUTM / "synth_b.parquet")
    print(f"S-R1b: {len(res)} runs in {time.time() - t0:.0f}s")
    cols = ["goal", "q", "eps", "alpha_q", "rep", "n_trees", "R_hat", "mu", "alpha", "LR", "cover_both", "ratio_obs",
            "ratio_lo", "ratio_hi", "ratio_cover", "obs_p5", "pred_p5"]
    with pl.Config(tbl_rows=200, tbl_cols=20, tbl_width_chars=250, float_precision=3):
        print(df.select(cols).sort("goal", "alpha_q", "q", "eps", "rep"))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "synth_a":
        run_synth_a()
    elif cmd == "synth_b":
        run_synth_b()
    elif cmd == "real":
        src = sys.argv[sys.argv.index("--src") + 1] if "--src" in sys.argv else "r1b"
        run_real(src)
