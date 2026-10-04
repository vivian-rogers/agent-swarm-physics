"""H45 library: room-token calibration, context share, and the estimators shared by real and synthetic data.

All estimators take a polars DataFrame of cu-mode receiving calls with at least:
  agent, lab, goal_no, unit_id, pt_date, seg, ctx_pos, k_new, chars_new, n_oev, P (nullable), talk,
  k_since_talk, eng_pending (talk calls), first_talk_day, open_forced, open_consol, end_forced, end_consol,
  seg_len_calls
and add r, R, W, s with `add_share`. No text anywhere.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/processed/H45-context-homeostasis"
BAND = (15, 35)                 # positions defining the set point (avoids the reset transient and the 41-call cap)
LABS_ACT = ("Anthropic", "Google")


# ============================================================================ loading and calibration

def load_calls(columns=None) -> pl.DataFrame:
    return pl.read_parquet(DATA / "calls.parquet", columns=columns)


def huber_irls(X: np.ndarray, y: np.ndarray, c: float = 1.345, iters: int = 30) -> np.ndarray:
    """Huber M-estimator by iteratively reweighted least squares (scale = MAD of residuals)."""
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    for _ in range(iters):
        r = y - X @ b
        s = np.median(np.abs(r - np.median(r))) / 0.6745 + 1e-9
        u = np.abs(r) / (c * s)
        w = np.where(u <= 1, 1.0, 1.0 / u)
        sw = np.sqrt(w)
        b_new = np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)[0]
        if np.max(np.abs(b_new - b)) < 1e-6:
            b = b_new
            break
        b = b_new
    return b


def calibrate_room_tokens(c: pl.DataFrame, max_rows: int = 400_000, seed: int = 0) -> dict:
    """Per lab: dP_c = alpha_agent + a*k_new + b*chars_new + e*n_oev (Huber), on consecutive cu calls of one segment
    whose prompt tokens come from action rows. Agent intercepts are removed by demeaning (own-content growth)."""
    d = (c.filter((pl.col("ctx_mode") == "cu") & pl.col("seg").is_not_null())
         .sort("agent", "t_first")
         .with_columns(pl.col("P").shift(1).over("seg").alias("P_prev"),
                       pl.col("p_src").cast(pl.Utf8).shift(1).over("seg").alias("src_prev"))
         .filter((pl.col("p_src").cast(pl.Utf8) == "act") & (pl.col("src_prev") == "act") & (pl.col("ctx_pos") > 1)
                 & pl.col("lab").cast(pl.Utf8).is_in(list(LABS_ACT)))
         .with_columns((pl.col("P") - pl.col("P_prev")).alias("dP"))
         .filter(pl.col("dP").abs() < 50_000))
    out = {}
    rng = np.random.default_rng(seed)
    for lab in LABS_ACT:
        x = d.filter(pl.col("lab").cast(pl.Utf8) == lab)
        if x.height > max_rows:
            x = x[np.sort(rng.choice(x.height, max_rows, replace=False))]
        cols = ["k_new", "chars_new", "n_oev"]
        # demean by agent (agent-specific own-content growth)
        x = x.with_columns([(pl.col(v) - pl.col(v).mean().over("agent")).alias(v + "_d") for v in cols + ["dP"]])
        X = x.select([v + "_d" for v in cols]).to_numpy().astype(float)
        y = x["dP_d"].to_numpy().astype(float)
        b = huber_irls(X, y)
        out[lab] = {"a_per_item": float(b[0]), "b_per_char": float(b[1]), "e_per_other_event": float(b[2]),
                    "n": int(x.height)}
    pooled = {k: float(np.mean([out[l][k] for l in LABS_ACT])) for k in ("a_per_item", "b_per_char", "e_per_other_event")}
    out["other_labs"] = {**pooled, "rule": "mean of Anthropic and Google"}
    return out


def save_calibration(cal: dict):
    (DATA / "calibration.json").write_text(json.dumps(cal, indent=1))


def load_calibration() -> dict:
    return json.loads((DATA / "calibration.json").read_text())


def room_tokens_expr(cal: dict, scale_other: float = 1.0) -> pl.Expr:
    def lin(k):
        q = cal[k]
        return (max(q["a_per_item"], 0) * pl.col("k_new") + max(q["b_per_char"], 0) * pl.col("chars_new")
                + max(q["e_per_other_event"], 0) * pl.col("n_oev"))
    lab = pl.col("lab").cast(pl.Utf8)
    return (pl.when(lab == "Anthropic").then(lin("Anthropic")).when(lab == "Google").then(lin("Google"))
            .otherwise(lin("other_labs") * scale_other)).clip(0, None)


def add_share(c: pl.DataFrame, cal: dict | None = None, scale_other: float = 1.0, r_col: str | None = None) -> pl.DataFrame:
    """r (room tokens of the call's new items), R (segment cumulative), W = P - R, s = R / P. Rows with W <= 0 get
    s = null (calibration exceeds the measured prompt). Also R_old: room content in context before the pending batch
    (R at the previous talk call of the same segment, else 0)."""
    if r_col is None:
        c = c.with_columns(room_tokens_expr(cal, scale_other).alias("r"))
    else:
        c = c.with_columns(pl.col(r_col).alias("r"))
    c = c.sort("agent", "t_first") if "t_first" in c.columns else c.sort("agent", "seg", "ctx_pos")
    c = c.with_columns(pl.col("r").cum_sum().over("seg").alias("R"))
    c = c.with_columns((pl.col("P") - pl.col("R")).alias("W"))
    c = c.with_columns(pl.when(pl.col("W") > 0).then(pl.col("R") / pl.col("P")).otherwise(None).alias("s"))
    # R at the previous talk call within the segment
    c = c.with_columns(pl.when(pl.col("talk")).then(pl.col("R")).otherwise(None).alias("_Rt"))
    c = c.with_columns(pl.col("_Rt").shift(1).forward_fill().over("seg").alias("_Rprev_talk_any"))
    # forward fill within seg of R at talk calls, shifted: value at previous talk strictly before this call
    c = c.with_columns(pl.col("_Rt").forward_fill().over("seg").shift(1).over("seg").alias("R_old"))
    c = c.with_columns(pl.col("R_old").fill_null(0.0)).drop("_Rt", "_Rprev_talk_any")
    return c


# ============================================================================ helpers: fixed effects and bootstrap

def demean(groups: np.ndarray, *arrays, w: np.ndarray | None = None):
    """Subtract (weighted) group means. groups: int codes 0..G-1."""
    G = int(groups.max()) + 1 if len(groups) else 0
    w = np.ones(len(groups)) if w is None else w
    sw = np.bincount(groups, weights=w, minlength=G)
    out = []
    for a in arrays:
        if a.ndim == 1:
            m = np.bincount(groups, weights=w * a, minlength=G) / np.where(sw > 0, sw, 1)
            out.append(a - m[groups])
        else:
            cols = []
            for j in range(a.shape[1]):
                m = np.bincount(groups, weights=w * a[:, j], minlength=G) / np.where(sw > 0, sw, 1)
                cols.append(a[:, j] - m[groups])
            out.append(np.column_stack(cols))
    return out


def codes(*cols) -> np.ndarray:
    keys = list(zip(*[np.asarray(c).tolist() for c in cols]))
    u = {}
    return np.array([u.setdefault(k, len(u)) for k in keys], dtype=np.int64)


def wls(X: np.ndarray, y: np.ndarray, w: np.ndarray | None = None) -> np.ndarray:
    if w is None:
        return np.linalg.lstsq(X, y, rcond=None)[0]
    sw = np.sqrt(w)
    return np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)[0]


def day_weights(days: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Cluster bootstrap weights: resample unique days with replacement; each row gets its day's multiplicity."""
    u, inv = np.unique(days, return_inverse=True)
    draw = rng.integers(0, len(u), len(u))
    mult = np.bincount(draw, minlength=len(u)).astype(float)
    return mult[inv]


def ci(x: np.ndarray, lo=2.5, hi=97.5):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    if len(x) < 5:
        return [float("nan"), float("nan")]
    return [float(np.percentile(x, lo)), float(np.percentile(x, hi))]


# ============================================================================ (a) regulation: share elasticity

def band_segments(c: pl.DataFrame, band=BAND) -> pl.DataFrame:
    """Per segment: mean share, inflow per call, own content and position over band calls with an observed share."""
    b = c.filter(pl.col("ctx_pos").is_between(band[0], band[1]) & pl.col("s").is_not_null() & (pl.col("R") > 0))
    return (b.group_by("seg").agg(
        pl.col("agent").first(), pl.col("lab").first(), pl.col("goal_no").first(), pl.col("unit_id").first(),
        pl.col("pt_date").first(), pl.col("s").mean().alias("s_bar"), (pl.col("R") / pl.col("ctx_pos")).mean().alias("lam"),
        pl.col("W").mean().alias("W_bar"), pl.col("ctx_pos").mean().alias("j_bar"), pl.len().alias("n_band"),
        pl.col("P").mean().alias("P_bar"))
        .filter((pl.col("lam") > 0) & (pl.col("W_bar") > 0)))


def elasticities(bs: pl.DataFrame, group_cols=("agent",), B: int = 200, seed: int = 1) -> dict:
    """eps (ln s_bar on ln lam), eta_W (ln W_bar on ln lam), controlling j_bar, with agent (x period, by caller) FE.
    RI = 1 - eps/(1 - s_mean). Day-cluster bootstrap."""
    if bs.height < 20:
        return {"n_seg": bs.height}
    g = codes(*[bs[cn].to_numpy() for cn in group_cols])
    ls, ll, lw, jb = (np.log(bs["s_bar"].to_numpy()), np.log(bs["lam"].to_numpy()), np.log(bs["W_bar"].to_numpy()),
                      bs["j_bar"].to_numpy().astype(float))
    days = bs["pt_date"].to_numpy()
    sm = float(bs["s_bar"].mean())

    def fit(w=None):
        y1, y2, x1, x2 = demean(g, ls, lw, ll, jb, w=w)
        X = np.column_stack([x1, x2])
        e = wls(X, y1, w)[0]
        h = wls(X, y2, w)[0]
        smw = sm if w is None else float(np.average(bs["s_bar"].to_numpy(), weights=w))
        return e, h, 1 - e / (1 - smw)

    e, h, ri = fit()
    rng = np.random.default_rng(seed)
    bt = np.array([fit(day_weights(days, rng)) for _ in range(B)])
    return {"n_seg": int(bs.height), "n_agents": int(bs["agent"].n_unique()), "s_mean": sm,
            "s_median": float(bs["s_bar"].median()), "eps": float(e), "eps_ci": ci(bt[:, 0]),
            "eta_W": float(h), "eta_W_ci": ci(bt[:, 1]), "RI": float(ri), "RI_ci": ci(bt[:, 2]),
            "eps_passive": 1 - sm}


def cv_band(bs: pl.DataFrame) -> float:
    """Within-agent CV of segment band shares (mean over agents with >= 10 segments)."""
    x = bs.group_by("agent").agg(pl.col("s_bar").std().alias("sd"), pl.col("s_bar").mean().alias("m"), pl.len().alias("n"))
    x = x.filter(pl.col("n") >= 10)
    return float((x["sd"] / x["m"]).mean()) if x.height else float("nan")


def segment_length_lever(c: pl.DataFrame, B: int = 200, seed: int = 2, group_cols=("agent",)) -> dict:
    """Segments that end in a voluntary consolidation and last >= 12 calls: ln L on ln(early inflow R_10/10),
    agent FE. Controller (consolidate at a share ceiling): negative; passive: 0."""
    s10 = (c.filter(pl.col("ctx_pos") == 10).select("seg", (pl.col("R") / 10).alias("lam10")))
    seg = (c.group_by("seg").agg(pl.col("agent").first(), pl.col("pt_date").first(), pl.col("seg_len_calls").first(),
                                 pl.col("end_consol").first(), pl.col("end_forced").first(), pl.col("goal_no").first())
           .join(s10, on="seg", how="inner")
           .filter(pl.col("end_consol").fill_null(False) & ~pl.col("end_forced").fill_null(False)
                   & (pl.col("seg_len_calls") >= 12) & (pl.col("lam10") > 0)))
    if seg.height < 30:
        return {"n_seg": seg.height}
    g = codes(*[seg[cn].to_numpy() for cn in group_cols])
    y, x = np.log(seg["seg_len_calls"].to_numpy().astype(float)), np.log(seg["lam10"].to_numpy())
    days = seg["pt_date"].to_numpy()

    def fit(w=None):
        yy, xx = demean(g, y, x, w=w)
        return wls(xx[:, None], yy, w)[0]

    b = fit()
    rng = np.random.default_rng(seed)
    bt = np.array([fit(day_weights(days, rng)) for _ in range(B)])
    return {"n_seg": int(seg.height), "slope": float(b), "slope_ci": ci(bt)}


def p_growth(c: pl.DataFrame) -> dict:
    """Median over segments of mean P at j 30-35 / mean P at j 8-12 (truncation plateau if ~1)."""
    x = (c.filter(pl.col("P").is_not_null())
         .with_columns(pl.when(pl.col("ctx_pos").is_between(8, 12)).then(pl.lit("e"))
                       .when(pl.col("ctx_pos").is_between(30, 35)).then(pl.lit("l")).otherwise(None).alias("w"))
         .filter(pl.col("w").is_not_null())
         .group_by("seg", "w").agg(pl.col("P").mean()).pivot(on="w", index="seg", values="P").drop_nulls())
    if x.height < 10 or "e" not in x.columns or "l" not in x.columns:
        return {"n_seg": x.height}
    r = (x["l"] / x["e"]).to_numpy()
    return {"n_seg": int(x.height), "ratio_median": float(np.median(r)), "ratio_q25": float(np.percentile(r, 25)),
            "ratio_q75": float(np.percentile(r, 75))}


def set_points(c: pl.DataFrame, by=("agent", "goal_no"), band=BAND, min_calls: int = 50) -> pl.DataFrame:
    b = c.filter(pl.col("ctx_pos").is_between(band[0], band[1]) & pl.col("s").is_not_null())
    return (b.group_by(list(by)).agg(pl.col("lab").first(), pl.col("s").median().alias("s_star"),
                                     pl.col("s").quantile(0.25).alias("s_q25"), pl.col("s").quantile(0.75).alias("s_q75"),
                                     (pl.col("R") / pl.col("ctx_pos")).median().alias("lam_med"),
                                     pl.col("P").median().alias("P_med"), pl.len().alias("n"))
            .filter(pl.col("n") >= min_calls))


# ============================================================================ (b) engagement

def talk_rows(c: pl.DataFrame) -> pl.DataFrame:
    """Talk calls with engagement defined, excluding each agent's first talk call of the day."""
    t = c.filter(pl.col("talk") & pl.col("eng_pending").is_not_null())
    t = t.sort("agent", "t_first") if "t_first" in t.columns else t
    t = t.with_columns(pl.int_range(pl.len()).over("agent", "pt_date").alias("_ti"))
    return t.filter((pl.col("_ti") > 0) & (pl.col("k_since_talk") >= 1)).drop("_ti")


def _theta_mle(x: np.ndarray, y: np.ndarray, g: np.ndarray, G: int, w: np.ndarray, iters: int = 40):
    """Per-group MLE of theta in P(y=1) = 1 - exp(-theta x) (Newton in log theta, vectorized)."""
    lt = np.zeros(G)
    for _ in range(iters):
        th = np.exp(lt)[g]
        z = np.clip(th * x, 1e-9, 50)
        q = np.exp(-z)
        # d ll / d log theta = sum [ y z q/(1-q) - (1-y) z ]
        d1 = w * (y * z * q / (1 - q) - (1 - y) * z)
        # second derivative wrt log theta
        d2 = w * (y * (z * q / (1 - q) - z * z * q / (1 - q) ** 2) - (1 - y) * z)
        g1 = np.bincount(g, weights=d1, minlength=G)
        g2 = np.bincount(g, weights=d2, minlength=G)
        step = np.where(g2 < -1e-12, -g1 / g2, 0.0)
        lt = np.clip(lt + np.clip(step, -3, 3), -25, 10)
    th = np.exp(lt)[g]
    z = np.clip(th * x, 1e-9, 50)
    ll = w * (y * np.log(1 - np.exp(-z)) - (1 - y) * z)
    return ll.sum()


def fit_beta(t: pl.DataFrame, B: int = 100, seed: int = 3, grid=None) -> dict:
    """Profile-likelihood beta for P(E1) = 1 - exp(-theta_{agent-day} k^(1-beta)); groups without variation dropped."""
    y = t["eng_pending"].cast(pl.Float64).to_numpy()
    k = t["k_since_talk"].to_numpy().astype(float)
    g = codes(t["agent"].to_numpy(), t["pt_date"].to_numpy())
    G = int(g.max()) + 1
    m = np.bincount(g, weights=y, minlength=G) / np.bincount(g, minlength=G)
    keep = (m[g] > 0) & (m[g] < 1)
    y, k, g = y[keep], k[keep], codes(g[keep])
    if len(y) < 200:
        return {"n": int(len(y))}
    G = int(g.max()) + 1
    days = t["pt_date"].to_numpy()[keep]
    grid = np.round(np.arange(-0.4, 1.41, 0.05), 3) if grid is None else grid
    lk = np.log(k)

    def prof(w):
        lls = np.array([_theta_mle(np.exp((1 - b) * lk), y, g, G, w) for b in grid])
        i = int(np.argmax(lls))
        # quadratic refinement
        if 0 < i < len(grid) - 1:
            a, bb, cc = np.polyfit(grid[i - 1:i + 2], lls[i - 1:i + 2], 2)
            if a < 0:
                return float(np.clip(-bb / (2 * a), grid[i - 1], grid[i + 1])), lls
        return float(grid[i]), lls

    b0, lls = prof(np.ones(len(y)))
    rng = np.random.default_rng(seed)
    coarse = np.round(np.arange(-0.4, 1.41, 0.1), 3)
    bt = []
    for _ in range(B):
        w = day_weights(days, rng)
        ll = np.array([_theta_mle(np.exp((1 - b) * lk), y, g, G, w) for b in coarse])
        i = int(np.argmax(ll))
        if 0 < i < len(coarse) - 1:
            a, bb, cc = np.polyfit(coarse[i - 1:i + 2], ll[i - 1:i + 2], 2)
            bt.append(float(np.clip(-bb / (2 * a), coarse[i - 1], coarse[i + 1])) if a < 0 else float(coarse[i]))
        else:
            bt.append(float(coarse[i]))
    return {"n": int(len(y)), "n_groups": G, "beta": b0, "beta_ci": ci(np.array(bt)), "rate": float(y.mean())}


def _cll(eta, y, w):
    mu = np.exp(np.clip(eta, -30, 6))
    return float((w * np.where(y > 0, np.log(np.maximum(-np.expm1(-mu), 1e-300)), -mu)).sum())


def _cderiv(eta, y):
    mu = np.exp(np.clip(eta, -30, 6))
    om = np.maximum(-np.expm1(-mu), 1e-300)          # 1 - exp(-mu)
    a = mu * np.exp(-mu) / om                         # mu q / (1 - q)
    r1 = np.where(y > 0, a, -mu)
    r2 = np.where(y > 0, a - a * a * np.exp(mu) * np.exp(-mu) / 1.0 * 0 - a * (a - 0) + a * (1 - mu) - a, -mu)
    # exact second derivative of y log(1-exp(-mu)) - (1-y) mu wrt eta: y [a (1 - mu) - a^2] - (1 - y) mu
    r2 = np.where(y > 0, a * (1 - mu) - a * a, -mu)
    return r1, r2


def cloglog_fe(y: np.ndarray, X: np.ndarray, g: np.ndarray, w: np.ndarray | None = None, b0=None, lt0=None,
               outer: int = 50, tol: float = 1e-7) -> tuple[np.ndarray, np.ndarray]:
    """P(y=1) = 1 - exp(-exp(lt_g + X b)): agent-day effects lt_g and slopes b by block Newton (Schur complement for
    b, vectorized Newton for lt), with step-halving on the log-likelihood. Returns (b, lt)."""
    n, p = X.shape
    G = int(g.max()) + 1
    w = np.ones(n) if w is None else w
    b = np.zeros(p) if b0 is None else b0.copy()
    lt = np.full(G, -1.0) if lt0 is None else lt0.copy()

    def inner(lt, b):
        xb = X @ b
        for _ in range(30):
            r1, r2 = _cderiv(lt[g] + xb, y)
            g1 = np.bincount(g, weights=w * r1, minlength=G)
            g2 = np.bincount(g, weights=w * r2, minlength=G)
            st = np.clip(np.where(g2 < -1e-12, -g1 / g2, 0.0), -2, 2)
            lt = np.clip(lt + st, -30, 6)
            if np.max(np.abs(st)) < 1e-8:
                break
        return lt

    lt = inner(lt, b)
    ll = _cll(lt[g] + X @ b, y, w)
    for it in range(outer):
        r1, r2 = _cderiv(lt[g] + X @ b, y)
        hw = -w * r2
        sw = np.bincount(g, weights=hw, minlength=G)
        Xm = np.column_stack([np.bincount(g, weights=hw * X[:, j], minlength=G) / np.maximum(sw, 1e-12)
                              for j in range(p)])
        Xc = X - Xm[g]
        H = (Xc * hw[:, None]).T @ Xc + 1e-8 * np.eye(p)
        step = np.linalg.solve(H, X.T @ (w * r1))
        t = 1.0
        while t > 1e-4:
            bn = b + t * step
            ltn = inner(lt, bn)
            lln = _cll(ltn[g] + X @ bn, y, w)
            if lln >= ll - 1e-10:
                break
            t /= 2
        if t <= 1e-4:
            break
        b, lt, dll, ll = bn, ltn, lln - ll, lln
        if np.max(np.abs(t * step)) < tol:
            break
    return b, lt


def _drop_constant_groups(y, g):
    G = int(g.max()) + 1
    m = np.bincount(g, weights=y, minlength=G) / np.maximum(np.bincount(g, minlength=G), 1)
    return (m[g] > 0) & (m[g] < 1)


def fit_beta_glm(t: pl.DataFrame, B: int = 100, seed: int = 3) -> dict:
    """beta = 1 - b_k in P(E1) = 1 - exp(-theta_{agent-day} k^(b_k)) (H18's model aggregated over the pending set)."""
    y = t["eng_pending"].cast(pl.Float64).to_numpy()
    k = t["k_since_talk"].to_numpy().astype(float)
    g = codes(t["agent"].to_numpy(), t["pt_date"].to_numpy())
    keep = _drop_constant_groups(y, g)
    y, k, g, days = y[keep], k[keep], codes(g[keep]) if keep.any() else g[keep], t["pt_date"].to_numpy()[keep]
    if len(y) < 200:
        return {"n": int(len(y))}
    X = np.log(k)[:, None]
    b, lt = cloglog_fe(y, X, g)
    rng = np.random.default_rng(seed)
    bt = [cloglog_fe(y, X, g, w=day_weights(days, rng), b0=b, lt0=lt, outer=15)[0][0] for _ in range(B)]
    return {"n": int(len(y)), "n_groups": int(g.max()) + 1, "beta": float(1 - b[0]),
            "beta_ci": ci(1 - np.array(bt)), "rate": float(y.mean())}


def share_dependence(t: pl.DataFrame, B: int = 100, seed: int = 4) -> dict:
    """cloglog GLM with agent-day FE: eng_pending ~ ln k + ln(1 + R_old/500) + ln(W/1000) + position bands, on talk
    calls with an observed share. Controller: g_R < 0, g_W > 0. Competition: both < 0. Passive: ~0."""
    t = t.filter(pl.col("W").is_not_null() & (pl.col("W") > 0) & pl.col("ctx_pos").is_not_null())
    if t.height < 300:
        return {"n": t.height}
    y = t["eng_pending"].cast(pl.Float64).to_numpy()
    j = t["ctx_pos"].to_numpy()
    bands = np.minimum((j - 1) // 5, 8)
    X = np.column_stack([np.log(t["k_since_talk"].to_numpy().astype(float)),
                         np.log1p(t["R_old"].to_numpy().astype(float) / 500),
                         np.log(t["W"].to_numpy().astype(float) / 1000)]
                        + [(bands == q).astype(float) for q in range(1, 9)])
    g = codes(t["agent"].to_numpy(), t["pt_date"].to_numpy())
    keep = _drop_constant_groups(y, g)
    y, X, g, days = y[keep], X[keep], codes(g[keep]), t["pt_date"].to_numpy()[keep]
    X = X[:, [0, 1, 2] + [3 + q for q in range(8) if X[:, 3 + q].any()]]
    if len(y) < 300:
        return {"n": int(len(y))}
    b, lt = cloglog_fe(y, X, g)
    rng = np.random.default_rng(seed)
    bt = np.array([cloglog_fe(y, X, g, w=day_weights(days, rng), b0=b, lt0=lt, outer=15)[0][:3] for _ in range(B)])
    return {"n": int(len(y)), "g_k": float(b[0]), "g_k_ci": ci(bt[:, 0]), "g_R": float(b[1]), "g_R_ci": ci(bt[:, 1]),
            "g_W": float(b[2]), "g_W_ci": ci(bt[:, 2]), "rate": float(y.mean())}


# ============================================================================ (c) post-erasure dynamics

def reset_profile(c: pl.DataFrame, opener: str = "open_forced", outcome: str = "talk", max_j: int = 40,
                  B: int = 200, seed: int = 5, kcol: str = "k_new", rows: pl.DataFrame | None = None) -> dict:
    """k-adjusted position profile after a reset of a given type: outcome ~ sum_j delta_j 1[j] (j = 1..19) +
    ln(1+k) + agent-day FE; baseline j in [20, max_j]. Overshoot = (base + mean delta_1..3) / base. tau from an
    exponential fit to delta_1..19."""
    x = c if rows is not None else c
    x = x.filter(pl.col(opener).fill_null(False) & pl.col("ctx_pos").is_between(1, max_j))
    if outcome == "eng_pending":
        x = x.filter(pl.col("eng_pending").is_not_null())
    if x.height < 500:
        return {"n": x.height}
    y = x[outcome].cast(pl.Float64).to_numpy()
    j = x["ctx_pos"].to_numpy()
    kv = x[kcol].to_numpy().astype(float)
    edges = [0.5, 1.5, 2.5, 4.5, 8.5, 16.5, 32.5]
    kb = np.digitize(kv, edges)
    xk = np.column_stack([(kb == q).astype(float) for q in range(1, len(edges) + 1)])
    D = np.column_stack([(j == q).astype(float) for q in range(1, 20)])
    g = codes(x["agent"].to_numpy(), x["pt_date"].to_numpy())
    days = x["pt_date"].to_numpy()
    base_mask = j >= 20

    def fit(w=None):
        yy, X = demean(g, y, np.column_stack([D, xk]), w=w)
        b = wls(X, yy, w)
        ww = np.ones(len(y)) if w is None else w
        base = float(np.average(y[base_mask], weights=ww[base_mask])) if base_mask.any() else float("nan")
        return b[:19], float(b[19:].mean()), base

    d, bk, base = fit()
    over = (base + d[:3].mean()) / base if base > 0 else float("nan")
    tau = _tau(d)
    rng = np.random.default_rng(seed)
    bo, bt, bks = [], [], []
    for _ in range(B):
        dd, kk, bb = fit(day_weights(days, rng))
        bo.append((bb + dd[:3].mean()) / bb if bb > 0 else np.nan)
        bt.append(_tau(dd))
        bks.append(kk)
    # raw (unadjusted) profile for figures
    raw = (x.group_by("ctx_pos").agg(pl.col(outcome).cast(pl.Float64).mean().alias("m"), pl.len().alias("n"),
                                     pl.col(kcol).mean().alias("k")).sort("ctx_pos"))
    return {"n": int(x.height), "n_segments": int(x["seg"].n_unique()), "baseline": base, "overshoot": float(over),
            "overshoot_ci": ci(np.array(bo)), "tau": tau, "tau_ci": ci(np.array(bt)), "delta": [float(v) for v in d],
            "b_lnk": float(bk), "b_lnk_ci": ci(np.array(bks)),
            "raw": {"j": raw["ctx_pos"].to_list(), "mean": raw["m"].to_list(), "n": raw["n"].to_list(),
                    "k": raw["k"].to_list()}}


def _tau(d: np.ndarray) -> float:
    """Fit d_j = A exp(-(j-1)/tau), j = 1..len(d), by grid search on tau (least squares in A)."""
    jj = np.arange(len(d))
    best, bt = np.inf, float("nan")
    if not np.isfinite(d).all() or abs(d[0]) < 1e-12:
        return float("nan")
    for tau in np.exp(np.linspace(np.log(0.3), np.log(60), 120)):
        f = np.exp(-jj / tau)
        A = (f @ d) / (f @ f)
        sse = ((d - A * f) ** 2).sum()
        if sse < best:
            best, bt = sse, tau
    return float(bt)


def share_profile(c: pl.DataFrame, opener: str = "open_forced", max_j: int = 41) -> dict:
    x = c.filter(pl.col(opener).fill_null(False) & pl.col("ctx_pos").is_between(1, max_j) & pl.col("s").is_not_null())
    p = x.group_by("ctx_pos").agg(pl.col("s").median().alias("s_med"), pl.col("P").median().alias("P_med"),
                                  pl.col("R").median().alias("R_med"), pl.len().alias("n")).sort("ctx_pos")
    return {k: p[k].to_list() for k in ("ctx_pos", "s_med", "P_med", "R_med", "n")}


# ============================================================================ (d) heterogeneity

def variance_shares(sp: pl.DataFrame, n_perm: int = 2000, seed: int = 6) -> dict:
    """eta^2 of lab and of goal period for ln s* across agent-period rows; lab permutation over agents."""
    sp = sp.filter(pl.col("s_star") > 0)
    y = np.log(sp["s_star"].to_numpy())
    labs = sp["lab"].cast(pl.Utf8).to_numpy()
    agents = sp["agent"].to_numpy()

    def eta2(lbl):
        cc = codes(lbl)
        m = np.bincount(cc, weights=y) / np.bincount(cc)
        return 1 - ((y - m[cc]) ** 2).sum() / ((y - y.mean()) ** 2).sum()

    obs = eta2(labs)
    ua = np.unique(agents)
    amap = dict(zip(agents, labs))
    alab = np.array([amap[a] for a in ua])
    rng = np.random.default_rng(seed)
    perm = []
    for _ in range(n_perm):
        pm = dict(zip(ua, rng.permutation(alab)))
        perm.append(eta2(np.array([pm[a] for a in agents])))
    return {"n_rows": int(len(y)), "eta2_lab": float(obs), "perm_q95": float(np.percentile(perm, 95)),
            "p_lab": float((np.sum(np.array(perm) >= obs) + 1) / (n_perm + 1)),
            "eta2_agent": float(eta2(agents)), "eta2_period": float(eta2(sp["goal_no"].to_numpy()))}
