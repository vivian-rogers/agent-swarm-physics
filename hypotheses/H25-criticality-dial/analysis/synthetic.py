"""H25 synthetic validation (axis F): does the daily dial recover a known loop gain under village sampling?

Design days: 120 real non-holdout village days (holdout asserted out), stratified by regime. Each design day keeps its
real population N, its real minutes T, each agent's real activity and talk schedule (30-min moving average of its own
spins, used only as a field), and for content its real (agent, 30-min window, statement count) structure.

Simulated swarms (known truth):
  CW-gibbs   equilibrium Curie-Weiss with the real schedule as fields; one Gibbs sweep per minute (persistent spins).
  CW-async   asynchronous Glauber (each agent updates with prob 0.35 per minute): same equilibrium, slower.
  CW-delay   asynchronous, but each agent reads the others' states from L_i in {2..8} minutes ago (context lag, H04):
             breaks detailed balance; the DC loop gain is unchanged, equal-time correlation is not.
     truth: g = beta J0 q_bar (N-1)/N, q_bar the within-block single-spin variance of the clean simulated spins.
  Hawkes     talk events, exponential kernels (tau 20 s or 180 s), cross offspring n_x shared over N-1 partners, self
             n_s, baseline = the real talk schedule; binned into 1-min talk spins.
     truth: DC cross loop gain g_DC = n_x / (1 - n_s); H19 mapping K = 2 w n_x / (1 + 2 w (n_x + n_s)).
  Content    O(32) soft spins with anisotropic fluctuations (~8 effective dims), agent fields, a day field, a
             time-varying exogenous field along 3 directions (observed only through noisy exogenous messages), mean-field
             coupling with g = J (N-1)/N, statements = normalized (state + large isotropic noise).
Stalls: half the days get 1-3 outages of 5-45 min (everyone silent, no events). Idle events: inactive minutes carry an
idle event with prob p_idle (0.3 main; 0 sensitivity).

Outputs: data/processed/H25-criticality-dial/synthetic/{design_days.parquet, binary.parquet, hawkes.parquet,
content.parquet, summary.json}; figure figures/fig_synthetic.png.
Usage: uv run python hypotheses/H25-criticality-dial/analysis/synthetic.py [--quick]
"""
from __future__ import annotations

import json
import math
import sys
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h25common as C  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import dial as D  # noqa: E402

SYN = C.OUT / "synthetic"
N_DESIGN = 120
N_BOOT, N_NULL = 200, 50
P_UPD = 0.35


# ----------------------------------------------------------------------------- design days
def build_design_days(seed=C.SEED) -> pl.DataFrame:
    cal = C.calendar_nonholdout()
    rng = np.random.default_rng(seed)
    days = []
    for reg, k in (("I", 64), ("II", 8), ("III", 48)):
        pool = cal.filter(pl.col("regime") == reg)["pt_date"].to_list()
        days += list(rng.choice(pool, size=min(k, len(pool)), replace=False))
    sub = cal.filter(pl.col("pt_date").is_in(days))
    C.assert_no_holdout(sub["pt_date"], sub["goal_no"])
    ab = (pl.scan_parquet(C.SHARED / "activity_bins.parquet").filter(pl.col("pt_date").is_in(days))
          .select("pt_date", "minute", "agent", "state").collect())
    st = pl.read_parquet(C.SHARED / "embeddings/statements.parquet").filter((pl.col("kind") == "chat") & pl.col("pt_date").is_in(days))
    rows, crow = [], []
    for i, d in enumerate(sorted(days)):
        a = ab.filter(pl.col("pt_date") == d)
        nact = a.group_by("agent").agg((pl.col("state") >= 3).sum().alias("na"), (pl.col("state") == 4).sum().alias("nt"))
        pop = nact.filter(pl.col("na") >= 10)["agent"].to_list()
        if len(pop) < 3:
            continue
        piv_a = a.filter(pl.col("agent").is_in(pop)).with_columns((pl.col("state") >= 3).cast(pl.Float32).alias("x")) \
            .pivot(on="agent", index="minute", values="x").sort("minute")
        piv_t = a.filter(pl.col("agent").is_in(pop)).with_columns((pl.col("state") == 4).cast(pl.Float32).alias("x")) \
            .pivot(on="agent", index="minute", values="x").sort("minute")
        cols = [str(x) for x in pop]
        A = piv_a.select(cols).to_numpy(); Tt = piv_t.select(cols).to_numpy()
        def smooth(X, L):
            k = np.ones(L) / L
            return np.column_stack([np.convolve(np.pad(X[:, j], L // 2, mode="edge"), k, "valid") for j in range(X.shape[1])])
        pa, pt = smooth(A, 121), smooth(Tt, 121)    # slow schedule (2-h moving average): the main field
        pa31, pt31 = smooth(A, 31), smooth(Tt, 31)  # fast field (31-min): stress test, carries real 30-60 min drives
        for j, ag in enumerate(pop):
            rows.append(pl.DataFrame({"dd": i, "pt_date": d, "agent": ag, "minute": piv_a["minute"].to_numpy(),
                                      "p_act": np.clip(pa[:, j], 0.02, 0.98).astype(np.float32),
                                      "p_talk": np.clip(pt[:, j], 0.005, 0.9).astype(np.float32),
                                      "p_act31": np.clip(pa31[:, j], 0.02, 0.98).astype(np.float32),
                                      "p_talk31": np.clip(pt31[:, j], 0.005, 0.9).astype(np.float32)}))
        c = st.filter((pl.col("pt_date") == d) & pl.col("win30").is_not_null() & pl.col("agent").is_not_null()).group_by("agent", "win30").len()
        crow.append(c.with_columns(pl.lit(i).alias("dd"), pl.lit(d).alias("pt_date")))
    out = pl.concat(rows)
    SYN.mkdir(parents=True, exist_ok=True)
    out.write_parquet(SYN / "design_days.parquet", compression="zstd")
    pl.concat(crow).write_parquet(SYN / "design_content.parquet", compression="zstd")
    return out


def load_design():
    dd = pl.read_parquet(SYN / "design_days.parquet")
    cd = pl.read_parquet(SYN / "design_content.parquet")
    des = {}
    for i in sorted(dd["dd"].unique().to_list()):
        x = dd.filter(pl.col("dd") == i)
        pa = x.pivot(on="agent", index="minute", values="p_act").sort("minute")
        pt = x.pivot(on="agent", index="minute", values="p_talk").sort("minute")
        pa31 = x.pivot(on="agent", index="minute", values="p_act31").sort("minute")
        pt31 = x.pivot(on="agent", index="minute", values="p_talk31").sort("minute")
        cols = [c for c in pa.columns if c != "minute"]
        des[i] = {"pt_date": x["pt_date"][0], "minute": pa["minute"].to_numpy(), "p_act": pa.select(cols).to_numpy(),
                  "p_talk": pt.select(cols).to_numpy(), "p_act31": pa31.select(cols).to_numpy(),
                  "p_talk31": pt31.select(cols).to_numpy(),
                  "content": cd.filter(pl.col("dd") == i).select("agent", "win30", "len").to_numpy()}
    return des


# ----------------------------------------------------------------------------- simulators
def outages(T, rng, p_day=0.5):
    m = np.zeros(T, bool)
    if rng.random() < p_day:
        for _ in range(rng.integers(1, 4)):
            L = int(rng.integers(5, 46)); a = int(rng.integers(0, max(1, T - L)))
            m[a:a + L] = True
    return m


def sim_cw(p, J, mode, rng):
    """Return clean +-1 spins (T x N) for a Curie-Weiss swarm with schedule fields from p (T x N activity probs)."""
    T, N = p.shape
    m0 = 2 * p - 1
    h = np.arctanh(np.clip(m0, -0.96, 0.96)) - J * (m0.sum(1, keepdims=True) - m0) / N  # mean-field compensation
    S = np.empty((T, N))
    s = np.where(rng.random(N) < p[0], 1.0, -1.0)
    U = rng.random((T + 30, N)); O = [rng.permutation(N) for _ in range(T + 30)]
    U2 = rng.random((T + 30, N))
    L = rng.integers(2, 9, size=N)
    for t in range(-30, T):
        tt = max(t, 0); ht = h[tt]
        tot = s.sum()
        for i in O[t + 30]:
            if mode != "gibbs" and t >= 0 and U2[t + 30, i] > P_UPD:
                continue
            if mode == "delay" and t >= 0:
                lag = t - L[i]
                others = (S[lag].sum() - S[lag, i]) if lag >= 0 else (tot - s[i])
            else:
                others = tot - s[i]
            loc = ht[i] + J * others / N
            new = 1.0 if U[t + 30, i] < 1 / (1 + math.exp(-2 * loc)) else -1.0
            tot += new - s[i]; s[i] = new
        if t >= 0:
            S[t] = s
    return S


def truth_cw(S, minute, J):
    blk = D._blocks(minute, 30)
    v = []
    for b in np.unique(blk):
        X = S[blk == b]
        if len(X) >= 5:
            v.append(X.var(0) * len(X))
    q = np.sum(v, 0) / len(S)
    N = S.shape[1]
    return J * q.mean() * (N - 1) / N, float(q.mean())


def sim_hawkes(pt, n_x, n_s, tau, rng, out_mask):
    """1-s Bernoulli Hawkes with exponential kernel; returns talk spins (T x N, bool) per minute."""
    T, N = pt.shape
    r_min = -np.log(1 - np.clip(pt, 0, 0.9))  # events per minute (Poisson)
    mu = np.repeat(r_min / 60.0 * max(1e-3, 1 - n_s - n_x), 60, axis=0)  # per second
    mu[np.repeat(out_mask, 60)] = 0.0
    dec = math.exp(-1.0 / tau)
    E = np.zeros(N)
    A = np.full((N, N), n_x / max(N - 1, 1)); np.fill_diagonal(A, n_s)
    spins = np.zeros((T, N), bool)
    U = rng.random((T * 60, N))
    offm = np.repeat(out_mask, 60)
    for k in range(T * 60):
        lam = mu[k] + (A @ E) / tau
        if offm[k]:
            lam = mu[k]
        ev = U[k] < 1 - np.exp(-lam)
        E = E * dec + ev
        if ev.any():
            spins[k // 60] |= ev
    return spins


def w_kernel(tau, Delta=60.0):
    return 1 - (tau / Delta) * (1 - math.exp(-Delta / tau))


# ----------------------------------------------------------------------------- estimation on one simulated day
def estimate_binary(S, minute, any_event, out_mask, rng, extra=False):
    res = {}
    if extra:  # detrending block sensitivity and the multi-scale diagnostic, on the oracle stall mask
        for bm in (15, 60):
            res[f"oracle_b{bm}"] = D.binary_day(S, minute, valid=~out_mask, block_min=bm, n_boot=N_BOOT, n_null=10, rng=rng)
        for dl in (5, 10):
            res[f"scale{dl}"] = D.vr_scale(S, minute, valid=~out_mask, delta=dl, block_min=60)
    for var in ("none", "auto", "lull", "oracle"):
        if var == "none":
            valid = None
        elif var == "auto":
            m, _ = D.find_stalls(any_event, minute, rng)
            valid = ~m
        elif var == "lull":
            valid = (S > 0).sum(1) >= 2
        else:
            valid = ~out_mask
        r = D.binary_day(S, minute, valid=valid, n_boot=N_BOOT, n_null=N_NULL, rng=rng)
        res[var] = r
        if var == "auto":
            res["auto_masked"] = int((~valid).sum()); res["auto_hit"] = int(((~valid) & out_mask).sum())
    return res


def job_binary(args):
    dd, des, J, mode, with_out, p_idle, field, seed = args
    rng = np.random.default_rng(seed)
    p, minute = des["p_act" if field == "slow" else "p_act31"], des["minute"]
    S = sim_cw(p, J, mode, rng)
    g_true, q = truth_cw(S, minute, J)
    om = outages(len(minute), rng) if with_out else np.zeros(len(minute), bool)
    S2 = S.copy(); S2[om] = -1.0
    idle = (rng.random(S.shape) < p_idle) & (S2 < 0)
    anyev = (S2 > 0) | idle
    anyev[om] = False
    res = estimate_binary(S2, minute, anyev, om, rng, extra=(p_idle > 0 and field == "slow"))
    rows = []
    sc = {f"g_scale{dl}": res.get(f"scale{dl}", (np.nan, np.nan))[0] for dl in (5, 10)}
    sc.update({f"g_scale{dl}_long": res.get(f"scale{dl}", (np.nan, np.nan))[1] for dl in (5, 10)})
    for var in ("none", "auto", "lull", "oracle", "oracle_b15", "oracle_b60"):
        r = res.get(var)
        if r is None:
            continue
        rows.append({"dd": dd, "J": J, "mode": mode, "outages": with_out, "p_idle": p_idle, "field": field, "variant": var,
                     "N": S.shape[1], **(sc if var == "oracle" else {k: np.nan for k in sc}),
                     "T": len(minute), "out_min": int(om.sum()), "g_true": g_true, "q_true": q, "g": r.g, "lo": r.lo, "hi": r.hi,
                     "se": r.se, "null_q95": r.null_q95, "q_bar": r.q_bar,
                     "auto_masked": res.get("auto_masked") if var == "auto" else None,
                     "auto_hit": res.get("auto_hit") if var == "auto" else None})
    return rows


def job_hawkes(args):
    dd, des, n_x, n_s, tau, with_out, seed = args
    rng = np.random.default_rng(seed)
    pt, minute = des["p_talk"], des["minute"]
    keep = pt.mean(0) * len(minute) >= 5  # talk population (>= ~5 talk minutes expected)
    if keep.sum() < 3:
        return []
    pt = pt[:, keep]
    om = outages(len(minute), rng) if with_out else np.zeros(len(minute), bool)
    sp = sim_hawkes(pt, n_x, n_s, tau, rng, om)
    S = np.where(sp, 1.0, -1.0)
    idle = (rng.random(S.shape) < 0.3) & ~sp
    anyev = sp | idle; anyev[om] = False
    res = estimate_binary(S, minute, anyev, om, rng, extra=True)
    w = w_kernel(tau)
    rows = []
    sc = {f"g_scale{dl}": res.get(f"scale{dl}", (np.nan, np.nan))[0] for dl in (5, 10)}
    sc.update({f"g_scale{dl}_long": res.get(f"scale{dl}", (np.nan, np.nan))[1] for dl in (5, 10)})
    for var in ("none", "auto", "lull", "oracle", "oracle_b15", "oracle_b60"):
        r = res.get(var)
        if r is None:
            continue
        rows.append({"dd": dd, "n_x": n_x, "n_s": n_s, "tau": tau, "outages": with_out, "variant": var, "N": S.shape[1],
                     **(sc if var == "oracle" else {k: np.nan for k in sc}),
                     "T": len(minute), "occ": float(sp.mean()), "g_DC": n_x / (1 - n_s),
                     "g_map": 2 * w * n_x / (1 + 2 * w * (n_x + n_s)), "g": r.g, "lo": r.lo, "hi": r.hi, "se": r.se,
                     "null_q95": r.null_q95})
    return rows


# ----------------------------------------------------------------------------- content
def sim_content(cstruct, J, exo_amp, rng, d=32, sig_noise=2.2):
    """cstruct: rows (agent, win30, count) of a real day. Returns U (unit statement vectors), agent, window, exo vectors."""
    agents = np.unique(cstruct[:, 0]); wins = np.unique(cstruct[:, 1])
    N, W = len(agents), len(wins)
    lam = np.exp(-np.arange(d) / 4.0); lam = lam / lam.sum() * d  # anisotropic: ~8 effective dims
    R = np.linalg.qr(rng.standard_normal((d, d)))[0]
    def draw(*shape):
        return (rng.standard_normal(shape + (d,)) * np.sqrt(lam)) @ R.T
    h0 = draw()[None, None] * 0.8
    hi = draw(N)[:, None] * 0.8
    eps = draw(N, W) * 0.6
    b = 1 / math.sqrt(1 - J) - 1
    x = eps + b * eps.mean(0, keepdims=True)
    # exogenous field: 3 directions, step changes at random windows, common to everyone
    E_dirs = draw(3); E_dirs /= np.linalg.norm(E_dirs, axis=1, keepdims=True)
    amp = np.zeros((W, 3))
    for k in range(3):
        a = int(rng.integers(0, W)); amp[a:, k] = rng.normal(0, 1)
    f = exo_amp * (amp @ E_dirs) * np.sqrt(lam.mean()) * 1.2
    V = h0 + hi + f[None] + x
    U, ag, wn = [], [], []
    ai = {a: i for i, a in enumerate(agents)}; wi = {w: j for j, w in enumerate(wins)}
    for a, w, c in cstruct:
        i, j = ai[a], wi[w]
        for _ in range(int(c)):
            z = V[i, j] + sig_noise * rng.standard_normal(d)
            U.append(z / np.linalg.norm(z)); ag.append(i); wn.append(j)
    U = np.array(U); ag = np.array(ag); wn = np.array(wn)
    o = np.lexsort((wn, ag)); U, ag, wn = U[o], ag[o], wn[o]
    # observed exogenous messages: 2 noisy copies per direction that changed
    ex = []
    for k in range(3):
        for _ in range(2):
            z = E_dirs[k] + 0.5 * rng.standard_normal(d) / math.sqrt(d) * 3
            ex.append(z / np.linalg.norm(z))
    g_true = J * (N - 1) / N
    return U, ag, wn, np.array(ex) if exo_amp > 0 else np.zeros((0, d)), g_true


def job_content(args):
    dd, cstruct, J, exo_amp, noise, seed = args
    rng = np.random.default_rng(seed)
    if len(np.unique(cstruct[:, 0])) < 3 or len(np.unique(cstruct[:, 1])) < 3:
        return []
    U, ag, wn, ex, g_true = sim_content(cstruct, J, exo_amp, rng, sig_noise=noise)
    rows = []
    for var in ("F1", "F2", "F2split", "noSH"):
        rd = D.exo_directions(ex, 5) if (var.startswith("F2") and len(ex)) else None
        if var == "noSH":  # no split-half correction: independent term = full-window variance (attenuated)
            r = content_nosplit(U, ag, wn)
            if r is None:
                continue
            rows.append({"dd": dd, "J": J, "exo": exo_amp, "noise": noise, "variant": var, "g_true": g_true, "g": r, "lo": np.nan,
                         "hi": np.nan, "null_q95": np.nan, "N": int(len(np.unique(ag)))})
            continue
        r = D.content_day(U, ag, wn, remove_dirs=rd, n_boot=N_BOOT, n_null=N_NULL, rng=rng,
                          method="split" if var == "F2split" else "moment")
        if r is None:
            rows.append({"dd": dd, "J": J, "exo": exo_amp, "noise": noise, "variant": var, "g_true": g_true, "g": np.nan,
                         "lo": np.nan, "hi": np.nan, "null_q95": np.nan, "N": 0})
            continue
        rows.append({"dd": dd, "J": J, "exo": exo_amp, "noise": noise, "variant": var, "g_true": g_true, "g": r.g, "lo": r.lo,
                     "hi": r.hi, "null_q95": r.null_q95, "N": r.N})
    return rows


def content_nosplit(U, ag, wn):
    """Naive estimator: window means, agent-day centering, VR from full covariances (statement noise not removed)."""
    N, W = ag.max() + 1, wn.max() + 1
    d = U.shape[1]
    S = np.zeros((N, W, d)); c = np.zeros((N, W))
    np.add.at(S, (ag, wn), U); np.add.at(c, (ag, wn), 1)
    has = c > 0
    V = np.where(has[..., None], S / np.maximum(c, 1)[..., None], 0)
    Tn = has.sum(1)
    if (Tn < 2).sum() > N - 3:
        return None
    mu = V.sum(1) / np.maximum(Tn, 1)[:, None]
    Rr = np.where(has[..., None], V - mu[:, None], 0)
    var = np.einsum("iwd,iwd->i", Rr, Rr) / np.maximum(Tn - 1, 1)
    G = np.einsum("iwd,jwd->ij", Rr, Rr); Cc = has.astype(float) @ has.T.astype(float)
    a, b = Tn[:, None].astype(float), Tn[None, :].astype(float)
    with np.errstate(divide="ignore", invalid="ignore"):
        cij = G / (Cc * (1 - 1 / a - 1 / b + Cc / (a * b)))
    ok = (Cc >= 2) & np.isfinite(cij) & ~np.eye(N, dtype=bool)
    sp = 0.5 * (var[:, None] + var[None, :])
    VR = 1 + (N - 1) * cij[ok].mean() / sp[ok].mean()
    return 1 - 1 / VR


# ----------------------------------------------------------------------------- summaries
def summarize(b: pl.DataFrame, h: pl.DataFrame, c: pl.DataFrame) -> dict:
    out = {}

    def cell(df, keys, truth):
        return (df.with_columns((pl.col("g") - pl.col(truth)).alias("err"),
                                ((pl.col("lo") <= pl.col(truth)) & (pl.col("hi") >= pl.col(truth))).alias("cov"),
                                (pl.col("lo") > 0).alias("pos"), (pl.col("g") > pl.col("null_q95")).alias("above_null"))
                .group_by(keys).agg(pl.len().alias("n"), pl.col(truth).median().alias("truth"), pl.col("g").median().alias("g_med"),
                                    pl.col("err").median().alias("bias"), (pl.col("err") ** 2).mean().sqrt().alias("rmse"),
                                    pl.col("cov").mean().alias("coverage90"), pl.col("pos").mean().alias("frac_lo_gt0"),
                                    pl.col("above_null").mean().alias("frac_above_null"), pl.col("se").median().alias("se_med"))
                .sort(keys))
    bs = b.filter((pl.col("p_idle") == 0.3) & (pl.col("field") == "slow"))
    out["binary"] = cell(bs, ["mode", "outages", "variant", "J"], "g_true").to_dicts()
    out["binary_pidle0"] = cell(b.filter(pl.col("p_idle") == 0.0), ["mode", "outages", "variant", "J"], "g_true").to_dicts()
    out["binary_fastfield"] = cell(b.filter(pl.col("field") == "fast"), ["mode", "outages", "variant", "J"], "g_true").to_dicts()
    out["binary_scale"] = (bs.filter(pl.col("variant") == "oracle").group_by("mode", "J")
                           .agg(pl.col("g_true").median(), pl.col("g").median().alias("g_eq"),
                                pl.col("g_scale5").median(), pl.col("g_scale10").median(),
                                pl.col("g_scale5_long").median(), pl.col("g_scale10_long").median()).sort("mode", "J").to_dicts())
    out["hawkes"] = cell(h.with_columns(pl.lit(None, dtype=pl.Float64).alias("dummy")), ["tau", "outages", "variant", "n_x", "n_s"], "g_DC").to_dicts()
    hh = (h.filter(pl.col("variant") == "auto").group_by("tau", "n_x", "n_s")
          .agg(pl.col("g").median().alias("g_med"), pl.col("g_map").first(), pl.col("g_DC").first(), pl.col("occ").median()).sort("tau", "n_x"))
    out["hawkes_vs_map"] = hh.to_dicts()
    out["hawkes_scale"] = (h.filter(pl.col("variant") == "oracle").group_by("tau", "n_x", "n_s")
                           .agg(pl.col("g_DC").first(), pl.col("g").median().alias("g_eq"), pl.col("g_scale5").median(),
                                pl.col("g_scale10").median(), pl.col("g_scale5_long").median(), pl.col("g_scale10_long").median())
                           .sort("tau", "n_x").to_dicts())
    cc = c.with_columns(pl.lit(np.nan).alias("se"))
    out["content"] = (cc.with_columns((pl.col("g") - pl.col("g_true")).alias("err"),
                                      ((pl.col("lo") <= pl.col("g_true")) & (pl.col("hi") >= pl.col("g_true"))).alias("cov"),
                                      (pl.col("lo") > 0).alias("pos"))
                      .group_by("exo", "noise", "variant", "J").agg(pl.len().alias("n"), pl.col("g_true").median().alias("truth"),
                                                          pl.col("g").median().alias("g_med"), pl.col("err").median().alias("bias"),
                                                          (pl.col("err") ** 2).mean().sqrt().alias("rmse"),
                                                          pl.col("cov").mean().alias("coverage90"), pl.col("pos").mean().alias("frac_lo_gt0"),
                                                          pl.col("g").is_nan().mean().alias("frac_nan"))
                      .sort("exo", "noise", "variant", "J").to_dicts())
    return out


def main():
    quick = "--quick" in sys.argv
    SYN.mkdir(parents=True, exist_ok=True)
    if not (SYN / "design_days.parquet").exists():
        build_design_days()
    des = load_design()
    keys = sorted(des)
    rng = np.random.default_rng(C.SEED)
    nd = 8 if quick else 40
    jobs_b, jobs_h, jobs_c = [], [], []
    for J in (0.0, 0.2, 0.4, 0.6, 0.8):
        for mode in ("gibbs", "async", "delay"):
            for with_out in (False, True):
                for dd in rng.choice(keys, size=nd, replace=False):
                    jobs_b.append((int(dd), des[dd], J, mode, with_out, 0.3, "slow", int(rng.integers(1 << 30))))
        for with_out in (False, True):  # stall detector without idle events
            for dd in rng.choice(keys, size=nd // 2, replace=False):
                jobs_b.append((int(dd), des[dd], J, "async", with_out, 0.0, "slow", int(rng.integers(1 << 30))))
        for dd in rng.choice(keys, size=nd // 2, replace=False):  # fast (31-min) real-drive field: stress test
            jobs_b.append((int(dd), des[dd], J, "gibbs", False, 0.3, "fast", int(rng.integers(1 << 30))))
    for n_x, n_s in ((0.0, 0.2), (0.1, 0.2), (0.2, 0.2), (0.4, 0.2), (0.6, 0.1)):
        for tau in (20.0, 180.0):
            for with_out in (False, True):
                for dd in rng.choice(keys, size=nd // 2, replace=False):
                    jobs_h.append((int(dd), des[dd], n_x, n_s, tau, with_out, int(rng.integers(1 << 30))))
    for J in (0.0, 0.2, 0.4, 0.6, 0.8):
        for exo in (0.0, 1.0):
            for noise in (1.2, 2.2):
                for dd in rng.choice(keys, size=nd, replace=False):
                    jobs_c.append((int(dd), des[dd]["content"], J, exo, noise, int(rng.integers(1 << 30))))
    print(f"jobs: binary {len(jobs_b)}, hawkes {len(jobs_h)}, content {len(jobs_c)}", flush=True)
    with Pool(2) as pool:
        c = pl.DataFrame([r for rr in pool.map(job_content, jobs_c, chunksize=4) for r in rr])
        print("content done", flush=True)
        b = pl.DataFrame([r for rr in pool.map(job_binary, jobs_b, chunksize=4) for r in rr], infer_schema_length=None)
        print("binary done", flush=True)
        h = pl.DataFrame([r for rr in pool.map(job_hawkes, jobs_h, chunksize=2) for r in rr])
        print("hawkes done", flush=True)
    sfx = "_quick" if quick else ""
    b.write_parquet(SYN / f"binary{sfx}.parquet"); h.write_parquet(SYN / f"hawkes{sfx}.parquet"); c.write_parquet(SYN / f"content{sfx}.parquet")
    summ = summarize(b, h, c)
    (SYN / f"summary{sfx}.json").write_text(json.dumps(summ, indent=1, default=float))
    C.write_provenance(f"synthetic{sfx}", "hypotheses/H25-criticality-dial/analysis/synthetic.py",
                       ["activity_bins", "calendar", "embeddings/statements"],
                       {"n_design": N_DESIGN, "per_cell_days": nd, "n_boot": N_BOOT, "n_null": N_NULL, "p_upd": P_UPD, "seed": C.SEED},
                       out=SYN)
    pl.Config.set_tbl_rows(200); pl.Config.set_tbl_cols(20)
    for k in ("binary", "binary_fastfield", "binary_scale", "hawkes_vs_map", "hawkes_scale", "content"):
        print(k); print(pl.DataFrame(summ[k]).with_columns(pl.col(pl.Float64).round(3)))


if __name__ == "__main__":
    main()
