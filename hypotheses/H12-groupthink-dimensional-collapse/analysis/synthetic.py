"""H12 synthetic validation (axis F), run before any real-data H12 statistic.

Calibration (nuisance parameters only, from non-holdout scored units): per-agent activity fraction and within-day
switching rate (-> latent AR(1) coefficient), the shared minute-of-window activity profile, content presence and
statement-count distributions, and whitened (d = 32) variance components (within agent-window, between windows,
between agents). No eigenvalue, PR, spread or content-overlap statistic is computed on real data here.

Experiments:
  A  activity spins: recovery of k planted collective modes (market / room / family) at village N, D, L;
     false-positive rates of the MP, T_eff-MP, circular-shift and cross-day edges under a shared schedule,
     heterogeneous daily profiles and platform stalls (lulls).
  B  content overlap matrix: recovery at regime-I/III sparsity; dependence on statement counts; #51-like units.
  C  participation-ratio estimators: bias vs n (Gaussian spectra), the PR30 procedure on clustered windows,
     between-agent PR vs number of agents N (naive, noise-corrected, noise + finite-N corrected), PRday ruler.
  D  power of the NE34 kickoff design (P6) and of the PRday free-vs-shared contrast.

Usage: uv run python hypotheses/H12-groupthink-dimensional-collapse/analysis/synthetic.py [A|B|C|D|calib|all]
"""
from __future__ import annotations

import json
import sys
import time
from multiprocessing import Pool

import h12lib as L
import numpy as np
import polars as pl
from scipy.optimize import brentq
from scipy.stats import mannwhitneyu, multivariate_normal, norm

SYN = L.OUT / "synthetic"
D32 = 32


# ======================================================================================================
# Calibration
# ======================================================================================================
def load_stmts(d=D32):
    idx = pl.read_parquet(L.OUT / "stmt_index.parquet")
    W = np.load(L.OUT / "stmt_white_d64.npy", mmap_mode="r")[:, :d].astype(np.float32)
    return idx, W


def phi_from(p, pc):
    """Latent AR(1) coefficient giving switching probability pc for a thresholded Gaussian with marginal p."""
    th = norm.ppf(1 - p)

    def f(phi):
        both = multivariate_normal(mean=[0, 0], cov=[[1, phi], [phi, 1]]).cdf([-th, -th])  # P(z1>th, z2>th)
        return 2 * (p - both) - pc
    try:
        return brentq(f, -0.2, 0.9999)
    except ValueError:
        return 0.95


def calibrate():
    units = pl.read_parquet(L.OUT / "units.parquet").filter("scored")
    sp = (pl.read_parquet(L.OUT / "spins.parquet").join(units.select("unit", "regime"), on="unit")
          .sort("unit", "agent", "day", "minute").with_columns((pl.col("state") >= 3).alias("a")))
    sp = sp.with_columns(pl.col("a").shift(1).over("unit", "agent", "day").alias("prev"))
    ag = (sp.filter(pl.col("prev").is_not_null()).group_by("regime", "unit", "agent")
          .agg(pl.col("a").mean().alias("p"), (pl.col("a") != pl.col("prev")).mean().alias("pc")))
    ag = ag.filter((pl.col("p") > 0.02) & (pl.col("p") < 0.98))
    rng = np.random.default_rng(L.SEED)
    sub = ag.sample(min(400, ag.height), seed=L.SEED)
    phis = [phi_from(p, pc) for p, pc in zip(sub["p"], sub["pc"])]
    sub = sub.with_columns(pl.Series("phi", phis))
    Lday = sp.group_by("unit", "day").agg((pl.col("minute").max() + 1).alias("L"))
    prof = (sp.join(Lday, on=["unit", "day"]).with_columns((pl.col("minute") * 10 // pl.col("L")).clip(0, 9).alias("dec"))
            .group_by("regime", "dec").agg(pl.col("a").mean()).sort("regime", "dec"))
    cal = {"activity": {}}
    for r in ["I", "II", "III"]:
        s = sub.filter(pl.col("regime") == r)
        pr = prof.filter(pl.col("regime") == r)["a"].to_numpy()
        cal["activity"][r] = {"p": s["p"].to_list(), "phi": s["phi"].to_list(), "profile": (pr / pr.mean()).tolist(),
                              "median_L": float(Lday.join(units.select("unit", "regime"), on="unit").filter(pl.col("regime") == r)["L"].median())}

    # ---- content
    idx, W = load_stmts()
    idx = idx.with_row_index("i").join(units.select("unit", "regime"), on=["unit", "regime"]).filter(pl.col("win30").is_not_null())
    cal["content"] = {}
    for r in ["I", "II", "III"]:
        x = idx.filter(pl.col("regime") == r)
        nwin = x.group_by("unit", "pt_date").agg((pl.col("win30").max() + 1).alias("W"))
        cnt = x.group_by("unit", "agent", "pt_date", "win30").agg(pl.len().alias("n"))
        tot = (cnt.group_by("unit", "agent").agg(pl.len().alias("nw"), pl.col("pt_date").n_unique().alias("nd"))
               .join(nwin.group_by("unit").agg(pl.col("W").sum().alias("Wtot"), pl.len().alias("D")), on="unit"))
        tot = tot.with_columns((pl.col("nw") / pl.col("Wtot")).alias("pres"))
        keep = tot.filter((pl.col("nd") >= 0.8 * pl.col("D")) & (pl.col("pres") >= 0.2))
        cntk = cnt.join(keep.select("unit", "agent"), on=["unit", "agent"], how="semi")
        pmf = np.bincount(np.minimum(cntk["n"].to_numpy(), 40), minlength=41)[1:].astype(float)
        # variance components (kind-centered, per dim)
        xi = x.join(keep.select("unit", "agent"), on=["unit", "agent"], how="semi")
        V = W[xi["i"].to_numpy()].astype(np.float64)
        keys_ak = (xi["unit"] + "|" + xi["agent"].cast(pl.String) + "|" + xi["kind"]).to_numpy()
        _, inv = np.unique(keys_ak, return_inverse=True)
        mu = np.zeros((inv.max() + 1, D32)); np.add.at(mu, inv, V); mu /= np.bincount(inv)[:, None]
        Vc = V - mu[inv]
        keys_w = (xi["unit"] + "|" + xi["agent"].cast(pl.String) + "|" + xi["pt_date"] + "|" + xi["win30"].cast(pl.String)).to_numpy()
        _, iw = np.unique(keys_w, return_inverse=True)
        nw_ = np.bincount(iw); m = np.zeros((iw.max() + 1, D32)); np.add.at(m, iw, Vc); m /= nw_[:, None]
        resid = Vc - m[iw]
        s2w = (resid ** 2).sum() / ((nw_ - 1).clip(0).sum() * D32)
        s2t = max((m ** 2).mean() - (s2w / nw_).mean(), 0.0)
        cal["content"][r] = {"pmf": (pmf / pmf.sum()).tolist(), "pres": keep["pres"].to_list(),
                             "W_med": float(nwin["W"].median()), "s2w": float(s2w), "s2t": float(s2t),
                             "n_agents_med": float(keep.group_by("unit").len()["len"].median())}
    SYN.mkdir(parents=True, exist_ok=True)
    (SYN / "calibration.json").write_text(json.dumps(cal))
    for r in ["I", "II", "III"]:
        a = cal["activity"][r]; c = cal["content"][r]
        print(f"[{r}] activity p med {np.median(a['p']):.2f}, phi med {np.median(a['phi']):.3f} (q10 {np.quantile(a['phi'], .1):.3f}, "
              f"q90 {np.quantile(a['phi'], .9):.3f}), L {a['median_L']:.0f}, profile {np.round(a['profile'], 2)}")
        print(f"[{r}] content pres med {np.median(c['pres']):.2f}, mean n|present {np.dot(np.arange(1, 41), c['pmf']):.2f}, "
              f"W {c['W_med']:.0f}, s2w {c['s2w']:.3f}, s2t {c['s2t']:.3f}, ratio s2t/s2w {c['s2t'] / c['s2w']:.3f}, N {c['n_agents_med']}")
    return cal


def load_cal():
    return json.loads((SYN / "calibration.json").read_text())


# ======================================================================================================
# Generators
# ======================================================================================================
def ar1(rng, shape_lead, T, phi):
    """AR(1) unit-variance series; phi scalar or array broadcastable to shape_lead. Returns shape_lead + (T,)."""
    phi = np.broadcast_to(np.asarray(phi, float), shape_lead)
    x = np.empty(shape_lead + (T,))
    x[..., 0] = rng.standard_normal(shape_lead)
    s = np.sqrt(1 - phi ** 2)
    e = rng.standard_normal(shape_lead + (T,))
    for t in range(1, T):
        x[..., t] = phi * x[..., t - 1] + s * e[..., t]
    return x


def loadings(N, k, rng):
    """Mode 1 market (uniform), mode 2 room (+-1 halves), mode 3 family (a third of agents)."""
    V = np.zeros((N, k))
    if k >= 1:
        V[:, 0] = 1.0
    if k >= 2:
        V[:, 1] = np.where(rng.permutation(N) < N // 2, 1.0, -1.0)
    if k >= 3:
        V[rng.permutation(N)[: max(3, N // 3)], 2] = 1.0
    return V


def gen_spins(rng, N, D, Lmin, k, a, cal_r, profile="shared", lulls=0.0, tau_f=10.0, lull_len=(3, 10)):
    """Days list of N x L spins (+-1). Latent z = sum_m a v_im f_m + sqrt(1 - sum a^2 v^2) eta_i; s = z > theta_i(t)."""
    p = rng.choice(cal_r["p"], N); phi = rng.choice(cal_r["phi"], N)
    V = loadings(N, k, rng)
    load2 = (a ** 2) * (V ** 2).sum(1)
    load2 = np.minimum(load2, 0.95)
    prof = np.interp(np.linspace(0, 9, Lmin), np.arange(10), cal_r["profile"])
    days = []
    for _ in range(D):
        eta = ar1(rng, (N,), Lmin, phi)
        z = np.sqrt(1 - load2)[:, None] * eta
        if k:
            f = ar1(rng, (k,), Lmin, np.exp(-1 / tau_f))
            z += a * V @ f
        if profile == "shared":
            pt = np.clip(p[:, None] * prof[None, :], 0.01, 0.99)
        else:  # heterogeneous: each agent active in its own part of the day
            c = rng.uniform(0, Lmin, N); w = rng.uniform(0.15, 0.35, N) * Lmin
            bump = np.exp(-0.5 * ((np.arange(Lmin)[None, :] - c[:, None]) / w[:, None]) ** 2)
            pt = np.clip(p[:, None] * (0.25 + 1.5 * bump / bump.mean(1, keepdims=True)), 0.01, 0.99)
        S = np.where(z > norm.ppf(1 - pt), 1, -1).astype(np.int8)
        if lulls > 0:
            n_ep = rng.poisson(lulls * Lmin / (0.5 * (lull_len[0] + lull_len[1])))
            for _ in range(n_ep):
                s0 = rng.integers(0, Lmin); S[:, s0:s0 + rng.integers(lull_len[0], lull_len[1])] = -1
        days.append(S)
    return days


def gen_content(rng, N, D, Wd, k, a, cal_c, d=D32, mult=1.0, phi_f=0.5, phi_g=0.5):
    """Days list of N x Wd x d window means of agent-centered statements (zeros where silent).
    Window signal x_i(t) = sqrt(s2t d) [sum_m a v_im f_m(t) u_m + sqrt(1 - sum a^2 v^2) g_i(t)], statements add
    N(0, s2w I); the agent field is static and removed by agent-centering."""
    V = loadings(N, k, rng)
    load2 = np.minimum((a ** 2) * (V ** 2).sum(1), 0.95)
    U = np.linalg.qr(rng.standard_normal((d, max(k, 1))))[0][:, :max(k, 1)]
    pres = np.clip(rng.choice(cal_c["pres"], N) * min(mult, 1.0) if mult < 1 else rng.choice(cal_c["pres"], N), 0.02, 1)
    pmf = np.asarray(cal_c["pmf"])
    s_t = np.sqrt(cal_c["s2t"] * d); s_w = np.sqrt(cal_c["s2w"])
    raw, cnts = [], []
    for _ in range(D):
        g = ar1(rng, (N, d), Wd, phi_g).transpose(0, 2, 1) / np.sqrt(d)  # N x W x d, E|g|^2 = 1
        x = np.sqrt(1 - load2)[:, None, None] * g
        if k:
            f = ar1(rng, (k,), Wd, phi_f)  # k x W
            x += a * np.einsum("im,mw,dm->iwd", V, f, U)
        x *= s_t
        n = np.where(rng.random((N, Wd)) < pres[:, None], rng.choice(np.arange(1, 41), (N, Wd), p=pmf), 0)
        if mult > 1:
            n = np.where(n > 0, np.maximum(1, np.round(n * mult)).astype(int), 0)
        noise = rng.standard_normal((N, Wd, d)) * s_w / np.sqrt(np.maximum(n, 1))[:, :, None]
        raw.append(np.where(n[:, :, None] > 0, x + noise, 0.0)); cnts.append(n)
    # agent-centering over present windows (as on real data)
    allx = np.concatenate(raw, 1); alln = np.concatenate(cnts, 1)
    w = alln > 0
    mu = (allx * w[:, :, None]).sum(1) / np.maximum(w.sum(1), 1)[:, None]
    return [np.where(c[:, :, None] > 0, r - mu[:, None, :], 0.0) for r, c in zip(raw, cnts)]


# ======================================================================================================
# A: activity spins
# ======================================================================================================
def job_A(args):
    cond, rep = args
    rng = np.random.default_rng([L.SEED, L.stable_seed(cond), rep])
    cal = load_cal()["activity"][cond["reg"]]
    days = gen_spins(rng, cond["N"], cond["D"], cond["L"], cond["k"], cond["a"], cal, cond.get("profile", "shared"),
                     cond.get("lulls", 0.0), lull_len=tuple(cond.get("lull_len", (3, 10))))
    keep = np.concatenate(days, 1).std(1) > 0
    days = [x[keep] for x in days]
    N = int(keep.sum()); T = sum(x.shape[1] for x in days)
    cd = L.spectrum_test(days, cond.get("n_surr", 200), rng, "spin", "crossday")
    tau = L.bartlett_tau(days)
    out = {**cond, "rep": rep, "N_eff": N, "k_cd": cd["k"], "k_rank": cd["k_rank"], "l1": float(cd["eig"][0]), "edge_cd": cd["edge"],
           "k_mp": int((cd["eig"] > L.mp_edge(N, T)).sum()), "k_mpeff": int((cd["eig"] > L.mp_edge(N, T / tau)).sum()),
           "tauB": tau}
    if cond.get("extra"):
        ci = L.spectrum_test(days, cond.get("n_surr", 200), rng, "spin", "circ")
        cl = L.spectrum_test(days, cond.get("n_surr", 200), rng, "spin", "crossday", lull=True)
        out.update({"k_circ": ci["k"], "edge_circ": ci["edge"], "k_cd_lull": cl["k"], "l1_lull": float(cl["eig"][0]),
                    "edge_lull": cl["edge"]})
    return out


def run_A():
    conds = []
    for k in [0, 1, 2, 3]:
        for a in ([0.0] if k == 0 else [0.15, 0.25, 0.35, 0.5]):
            conds.append({"exp": "A1", "reg": "III", "N": 15, "D": 5, "L": 240, "k": k, "a": a})
    for N in [10, 15, 21]:
        for D in [3, 5, 10, 19]:
            conds.append({"exp": "A2", "reg": "III", "N": N, "D": D, "L": 480 if N == 21 else 240, "k": 1, "a": 0.3})
    for prof, lul, k in [("shared", 0.0, 0), ("hetero", 0.0, 0), ("shared", 0.05, 0), ("hetero", 0.05, 0), ("shared", 0.05, 1),
                         ("shared", 0.0, 1), ("shared", 0.15, 0)]:
        conds.append({"exp": "A3", "reg": "III", "N": 15, "D": 5, "L": 240, "k": k, "a": 0.3 if k else 0.0,
                      "profile": prof, "lulls": lul, "extra": True})
    conds.append({"exp": "A3", "reg": "I", "N": 10, "D": 5, "L": 240, "k": 0, "a": 0.0, "profile": "shared", "lulls": 0.0, "extra": True})
    jobs = [(c, r) for c in conds for r in range(50 if c["exp"] != "A2" else 30)]
    with Pool(2) as pool:
        res = pool.map(job_A, jobs, chunksize=4)
    df = pl.DataFrame(res, infer_schema_length=None)
    df.write_parquet(SYN / "A_activity.parquet")
    return df


# ======================================================================================================
# B: content
# ======================================================================================================
def job_B(args):
    cond, rep = args
    rng = np.random.default_rng([L.SEED, L.stable_seed(cond), rep])
    cal = load_cal()["content"][cond["reg"]]
    days = gen_content(rng, cond["N"], cond["D"], cond["W"], cond["k"], cond["a"], cal, mult=cond.get("mult", 1.0))
    X = np.concatenate(days, 1)
    keep = (np.abs(X).sum((1, 2)) > 0)
    days = [x[keep] for x in days]
    N = int(keep.sum()); T = X.shape[1]
    cd = L.spectrum_test(days, cond.get("n_surr", 200), rng, "content", "crossday")
    return {**cond, "rep": rep, "N_eff": N, "k_cd": cd["k"], "k_rank": cd["k_rank"], "l1": float(cd["eig"][0]), "edge_cd": cd["edge"],
            "k_mp": int((cd["eig"] > L.mp_edge(N, T * D32)).sum())}


def run_B():
    conds = []
    for reg, N in [("I", 10), ("III", 15)]:
        for k in [0, 1, 2]:
            for a in ([0.0] if k == 0 else [0.2, 0.3, 0.45, 0.6]):
                conds.append({"exp": "B1", "reg": reg, "N": N, "D": 5, "W": 8, "k": k, "a": a})
        for mult in [0.5, 2.0, 4.0]:
            conds.append({"exp": "B2", "reg": reg, "N": N, "D": 5, "W": 8, "k": 1, "a": 0.3, "mult": mult})
    conds.append({"exp": "B3", "reg": "III", "N": 24, "D": 19, "W": 16, "k": 1, "a": 0.3})
    conds.append({"exp": "B3", "reg": "III", "N": 24, "D": 19, "W": 16, "k": 0, "a": 0.0})
    conds.append({"exp": "B3", "reg": "III", "N": 12, "D": 3, "W": 8, "k": 1, "a": 0.3})
    jobs = [(c, r) for c in conds for r in range(50)]
    with Pool(2) as pool:
        res = pool.map(job_B, jobs, chunksize=4)
    df = pl.DataFrame(res, infer_schema_length=None)
    df.write_parquet(SYN / "B_content.parquet")
    return df


# ======================================================================================================
# C: participation-ratio estimators
# ======================================================================================================
def spectrum_for_pr(target, d=D32):
    """Power-law spectrum lambda_k ~ k^-alpha with PR = target (alpha solved)."""
    def pr(al):
        lam = np.arange(1, d + 1) ** (-al); return lam.sum() ** 2 / (lam ** 2).sum()
    if target >= d - 1e-6:
        return np.ones(d)
    al = brentq(lambda x: pr(x) - target, 0.0, 10.0)
    lam = np.arange(1, d + 1) ** (-al)
    return lam / lam.mean()


def run_C():
    rng = np.random.default_rng(L.SEED)
    rows = []
    # C1 Gaussian: flat-r and power-law spectra
    specs = [("flat", r, np.r_[np.ones(r), np.full(D32 - r, 1e-12)]) for r in [4, 8, 16, 24, 32]]
    specs += [("power", round(float(t), 1), spectrum_for_pr(t)) for t in [3.0, 6.0, 12.0, 20.0]]
    for name, par, lam in specs:
        prt = lam.sum() ** 2 / (lam ** 2).sum()
        for n in [10, 15, 20, 30, 45, 60, 90, 150, 300]:
            est = [L.pr_from_samples(rng.standard_normal((n, D32)) * np.sqrt(lam)) for _ in range(300)]
            for key in ["pr", "pr_naive", "erank"]:
                v = np.array([e[key] for e in est])
                rows.append({"exp": "C1", "spec": name, "par": par, "pr_true": prt, "n": n, "est": key,
                             "mean": float(np.nanmean(v)), "sd": float(np.nanstd(v))})
    # C2w clustered windows: agents with own means; PR30 procedure (cap 8, n 30, 20 draws) vs population truth
    cal = load_cal()["content"]
    for reg in ["I", "III"]:
        pmf = np.asarray(cal[reg]["pmf"])
        for Na in [6, 10, 15, 19]:
            for rb in [2, 6, 16]:
                for share_b in [0.2, 0.5]:
                    for rep in range(40):
                        lam_b = np.r_[np.ones(rb), np.zeros(D32 - rb)] / rb * D32 * share_b
                        mu = rng.standard_normal((Na, D32)) * np.sqrt(lam_b)
                        n = rng.choice(np.arange(1, 41), Na, p=pmf)
                        ag = np.repeat(np.arange(Na), n)
                        Y = mu[ag] + rng.standard_normal((len(ag), D32)) * np.sqrt(1 - share_b)
                        w = np.minimum(n, 8); w = w / w.sum()
                        mbar = w @ mu
                        Sig = ((mu - mbar).T * w) @ (mu - mbar) + np.eye(D32) * (1 - share_b)
                        prt = np.trace(Sig) ** 2 / (Sig * Sig).sum()
                        r30 = L.pr_rarefied(Y, ag, 30, 8, 20, rng, erank=False)
                        rows.append({"exp": "C2w", "reg": reg, "Na": Na, "rb": rb, "share_b": share_b, "rep": rep,
                                     "pr_true": prt, "pr30": r30["pr"], "pr30_naive": r30["pr_naive"], "n_pool": int(len(Y))})
    # C2d clustered days: PRday (m = 6 agents x 15) and the between-agent PR, vs truth
    m_ = 6
    for Na in [7, 10, 15, 24]:
        for rb in [2, 6, 16]:
            for share_b in [0.2, 0.5]:
                for rep in range(40):
                    lam_b = np.r_[np.ones(rb), np.zeros(D32 - rb)] / rb * D32 * share_b
                    mu = rng.standard_normal((Na, D32)) * np.sqrt(lam_b)
                    n = np.maximum(rng.poisson(36, Na), 4)
                    ag = np.repeat(np.arange(Na), n)
                    Y = mu[ag] + rng.standard_normal((len(ag), D32)) * np.sqrt(1 - share_b)
                    el = n >= 15
                    mc = mu[el] - mu[el].mean(0); Sb = mc.T @ mc / max(el.sum() - 1, 1)
                    Sig = (m_ - 1) / m_ * Sb + np.eye(D32) * (1 - share_b)
                    prt = np.trace(Sig) ** 2 / (Sig * Sig).sum()
                    mca = mu - mu.mean(0); Sba = mca.T @ mca / (Na - 1)
                    rd = L.pr_balanced(Y, ag, m_, 15, 50, rng, erank=False)
                    bt = L.between_pr(Y, ag, rng, splits=10)
                    rows.append({"exp": "C2d", "Na": Na, "rb": rb, "share_b": share_b, "rep": rep, "pr_true": prt,
                                 "prday": rd["pr"], "btw_true_finite": float(np.trace(Sba) ** 2 / (Sba * Sba).sum()),
                                 "btw_naive": bt["pr_between_naive"], "btw_noise": bt["pr_between"], "btw_pop": bt["pr_between_pop"]})
    # C3 between-agent PR vs N agents
    for rb in [2, 5, 10]:
        for Na in [6, 8, 10, 15, 20, 30]:
            for k in [8, 15, 40]:
                for rep in range(60):
                    lam_b = np.r_[np.ones(rb), np.zeros(D32 - rb)] * 0.3 * D32 / rb
                    mu = rng.standard_normal((Na, D32)) * np.sqrt(lam_b)
                    ag = np.repeat(np.arange(Na), k)
                    Y = mu[ag] + rng.standard_normal((len(ag), D32))
                    mc = mu - mu.mean(0); Sb = mc.T @ mc / (Na - 1)
                    pr_fin = np.trace(Sb) ** 2 / (Sb * Sb).sum()
                    b = L.between_pr(Y, ag, rng, splits=10, min_per=8)
                    # finite-N (Wishart over agents) correction of the noise-corrected moments
                    rows.append({"exp": "C3", "rb": rb, "Na": Na, "k": k, "rep": rep, "pr_pop": float(rb),
                                 "pr_finite": float(pr_fin), "naive": b["pr_between_naive"], "noise_corr": b["pr_between"],
                                 "full_corr": b.get("pr_between_pop", np.nan)})
    df = pl.DataFrame(rows, infer_schema_length=None)
    df.write_parquet(SYN / "C_pr.parquet")
    return df


# ======================================================================================================
# D: power of the kickoff design and the free-vs-shared contrast
# ======================================================================================================
def window_pr30(rng, pr_target, n_pool, d=D32):
    lam = spectrum_for_pr(min(pr_target, d))
    Y = rng.standard_normal((n_pool, d)) * np.sqrt(lam)
    return L.pr_rarefied(Y, np.zeros(n_pool, int), 30, None, 5, rng, erank=False)["pr"]


def run_D():
    rng = np.random.default_rng(L.SEED + 1)
    rows = []
    n_kick, n_plac = 22, 90
    for s_day in [0.05, 0.10, 0.20]:
        for drop in [0.0, 0.1, 0.2, 0.3]:
            for rep in range(30):
                def first_hour(base, dr):
                    return np.mean([window_pr30(rng, base * (1 - dr), int(rng.integers(30, 120))) for _ in range(2)])
                dk = []
                for _ in range(n_kick):
                    base = 12.0
                    pre = first_hour(base * np.exp(rng.normal(0, s_day)), 0)
                    post = first_hour(base * np.exp(rng.normal(0, s_day)), drop)
                    dk.append(post - pre)
                dp = []
                for _ in range(n_plac):
                    base = 12.0
                    dp.append(first_hour(base * np.exp(rng.normal(0, s_day)), 0) - first_hour(base * np.exp(rng.normal(0, s_day)), 0))
                dk = np.array(dk); dp = np.array(dp)
                p = mannwhitneyu(dk, dp, alternative="less").pvalue
                rows.append({"exp": "D1", "s_day": s_day, "drop": drop, "rep": rep, "p": p, "med_dk": float(np.median(dk)),
                             "frac_neg": float((dk < 0).mean()),
                             "pass": bool(p < 0.05 and np.median(dk) < 0 and (dk < 0).mean() >= 2 / 3)})
    df = pl.DataFrame(rows, infer_schema_length=None)
    df.write_parquet(SYN / "D_power.parquet")
    return df


def summarize():
    out = {}
    A = pl.read_parquet(SYN / "A_activity.parquet")
    out["A1"] = (A.filter(pl.col("exp") == "A1").group_by("k", "a")
                 .agg((pl.col("k_cd") == pl.col("k")).mean().alias("P_exact"), pl.col("k_cd").mean().alias("k_cd"),
                      pl.col("k_mp").mean().alias("k_mp"), pl.col("k_mpeff").mean().alias("k_mpeff"),
                      pl.col("l1").mean(), pl.col("edge_cd").mean()).sort("k", "a"))
    out["A2"] = (A.filter(pl.col("exp") == "A2").group_by("N", "D")
                 .agg((pl.col("k_cd") >= 1).mean().alias("P_detect"), (pl.col("k_cd") == 1).mean().alias("P_exact"))
                 .sort("N", "D"))
    out["A3"] = (A.filter(pl.col("exp") == "A3").group_by("reg", "profile", "lulls", "k")
                 .agg(*[pl.col(c).mean() for c in ["k_cd", "k_circ", "k_mp", "k_mpeff", "k_cd_lull"]],
                      (pl.col("k_cd") > 0).mean().alias("FP_cd"), (pl.col("k_circ") > 0).mean().alias("FP_circ"),
                      (pl.col("k_mp") > 0).mean().alias("FP_mp"), (pl.col("k_mpeff") > 0).mean().alias("FP_mpeff"),
                      (pl.col("l1") / pl.col("edge_cd")).mean().alias("l1_edge"),
                      (pl.col("l1_lull") / pl.col("edge_lull")).mean().alias("l1_edge_lull")).sort("reg", "profile", "lulls", "k"))
    B = pl.read_parquet(SYN / "B_content.parquet")
    out["B"] = (B.group_by("exp", "reg", "N", "D", "W", "k", "a", "mult")
                .agg((pl.col("k_cd") >= pl.col("k")).mean().alias("P_ge_k"), (pl.col("k_cd") == pl.col("k")).mean().alias("P_exact"),
                     (pl.col("k_cd") >= 1).mean().alias("P_any"), pl.col("k_cd").mean(), pl.col("k_mp").mean())
                .sort("exp", "reg", "k", "a", "mult"))
    C = pl.read_parquet(SYN / "C_pr.parquet")
    out["C1"] = (C.filter(pl.col("exp") == "C1").with_columns((pl.col("mean") / pl.col("pr_true")).alias("rel"))
                 .select("spec", "par", "pr_true", "n", "est", "rel", "sd").sort("spec", "par", "est", "n"))
    out["C2w"] = (C.filter(pl.col("exp") == "C2w").group_by("reg", "Na", "rb", "share_b")
                  .agg(pl.col("pr_true").mean(), (pl.col("pr30") / pl.col("pr_true")).mean().alias("pr30_rel"),
                       (pl.col("pr30") / pl.col("pr_true")).std().alias("pr30_rel_sd"),
                       (pl.col("pr30_naive") / pl.col("pr_true")).mean().alias("naive_rel"), pl.col("pr30").is_nan().mean().alias("frac_nan"))
                  .sort("reg", "Na", "rb", "share_b"))
    out["C2d"] = (C.filter(pl.col("exp") == "C2d").group_by("Na", "rb", "share_b")
                  .agg(pl.col("pr_true").mean(), (pl.col("prday") / pl.col("pr_true")).mean().alias("prday_rel"),
                       (pl.col("prday") / pl.col("pr_true")).std().alias("prday_rel_sd"),
                       pl.col("btw_true_finite").mean(), pl.col("btw_naive").mean(), pl.col("btw_noise").mean(), pl.col("btw_pop").mean())
                  .sort("Na", "rb", "share_b"))
    out["C3"] = (C.filter(pl.col("exp") == "C3").group_by("rb", "Na", "k")
                 .agg(pl.col("pr_finite").mean(), pl.col("naive").mean(), pl.col("noise_corr").mean(),
                      pl.col("full_corr").mean(), pl.col("noise_corr").std().alias("noise_corr_sd")).sort("rb", "Na", "k"))
    D = pl.read_parquet(SYN / "D_power.parquet")
    out["D1"] = D.group_by("s_day", "drop").agg(pl.col("pass").mean().alias("power"), (pl.col("p") < 0.05).mean().alias("P_p05"),
                                                pl.col("med_dk").mean()).sort("s_day", "drop")
    with pl.Config(tbl_rows=200, tbl_cols=20, tbl_width_chars=250, float_precision=3):
        for k, v in out.items():
            print(f"\n=== {k}"); print(v)
    for k, v in out.items():
        v.write_csv(SYN / f"summary_{k}.csv")
    return out


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    t0 = time.time()
    SYN.mkdir(parents=True, exist_ok=True)
    if which in ("calib", "all"):
        calibrate()
    if which in ("A", "all"):
        run_A(); print(f"A done {time.time() - t0:.0f}s", flush=True)
    if which in ("B", "all"):
        run_B(); print(f"B done {time.time() - t0:.0f}s", flush=True)
    if which in ("C", "all"):
        run_C(); print(f"C done {time.time() - t0:.0f}s", flush=True)
    if which in ("D", "all"):
        run_D(); print(f"D done {time.time() - t0:.0f}s", flush=True)
    if which in ("summary", "all"):
        summarize()
    L.write_provenance("hypotheses/H12-groupthink-dimensional-collapse/analysis/synthetic.py",
                       ["H12 spins.parquet, stmt_index.parquet, stmt_white_d64.npy (calibration marginals only)"],
                       {"seed": L.SEED, "surrogates": 200}, path=SYN / "_provenance.json")


if __name__ == "__main__":
    main()
