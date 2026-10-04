"""H103 library: clock comparison of remanence decay (night / active-hour / wall / reset) and the two-time night step.

O1  kickoff remanence: A_w = mean_i [cos(s_iw, k_P) - mean_q cos(s_iw, k_q)] over incumbents in window w;
    A_w = A_inf + dA f_clock(t_w) + s(slot_w), weighted LS (weights = agents in window), grid over the rate.
O2  previous-centroid remanence: the same with the field-orthogonal leave-i-out previous centroid minus placebos.
O3  pairs of one agent's windows: C = cos(s_w, s_w') on agent FE + slot(w) + slot(w') + dH bins + b_N N
    + b_G N (G - G_wk)/24 + b_gap gap_own (+ b_R dr), agent-cluster bootstrap.
No text. Thread caps: sitecustomize (2).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import OUT, load_holdout  # noqa: E402
from embed_models import agent_vectors, goal_vectors, load_whitener  # noqa: E402

DATA = ROOT / "data/processed/H103-nights-demagnetize"
CLOCKS = ["N", "H", "W", "R"]
GRID = {"N": np.linspace(0.02, 1.0, 50),                       # lambda per night
        "H": np.exp(np.linspace(np.log(0.1), np.log(300), 60)),  # tau, active hours
        "W": np.exp(np.linspace(np.log(0.5), np.log(3000), 60)),  # tau, wall hours
        "R": np.exp(np.linspace(np.log(0.1), np.log(3000), 60))}  # rho, resets
DH_EDGES = [0.5 + 0.5 * k for k in range(16)] + [12, 16, np.inf]   # 0.5-h bins to 8 h (coarse bins + slot FE bias beta_N)
EXCLUDE_GOALS = {23}


def unit(v, axis=-1):
    n = np.linalg.norm(v, axis=axis, keepdims=True)
    return np.where(n > 0, v / np.where(n > 0, n, 1), np.nan)


class Store:
    def __init__(self, model="bge_small", variant="style_resid", data_dir=None, extra_kickoffs=()):
        self.model, self.variant = model, variant
        D = DATA if data_dir is None else Path(data_dir)
        self.w = pl.read_parquet(D / "windows.parquet")
        V = agent_vectors("win30", model, variant)
        self.V = unit(V[self.w["gid"].to_numpy()].astype(np.float32))
        self.days = pl.read_parquet(D / "days.parquet")
        self.periods = pl.read_parquet(D / "periods.parquet")
        self.gaps = pl.read_parquet(D / "gaps.parquet")
        self.goals = pl.read_parquet(OUT / "embeddings/goals.parquet").with_columns(pl.col("kind").cast(pl.String))
        graw = goal_vectors(model).astype(np.float32)
        self.G = {r: unit(load_whitener(r, 32, model)(graw)) for r in ("I", "II", "III")}
        held = set(load_holdout()["goal_periods_held_out"])
        k = self.goals.filter((pl.col("kind") == "kickoff") & ~pl.col("holdout")
                              & ~pl.col("goal_no").is_in(list(held | EXCLUDE_GOALS)))
        self.kick = dict(zip(k["goal_no"].to_list(), k["gid"].to_list()))
        for g in extra_kickoffs:   # confirm.py only: a held-out period's own kickoff (decoys stay non-holdout)
            kk = self.goals.filter((pl.col("kind") == "kickoff") & (pl.col("goal_no") == g))
            if kk.height:
                self.kick[g] = kk["gid"][0]


# ------------------------------------------------------------------------------------------- O1 / O2 series
def period_windows(S: Store, rec: dict):
    """Windows of incumbents on the fit days after t0, with clocks. Returns frame and row indices into S.V."""
    t0 = rec["t0"]
    w = S.w.with_row_index("ri").filter(pl.col("pt_date").is_in(rec["fit_days"]) & pl.col("agent").is_in(
        rec["incumbents"]) & (pl.col("t_mid") >= t0) & (pl.col("goal_no") == rec["goal_no"]))
    d0 = S.days.filter(pl.col("pt_date") == rec["fit_days"][0])
    h0 = d0["h_before"][0] + (t0 - d0["win_start"][0]).total_seconds() / 3600
    w = w.with_columns((pl.col("hcum") - h0).clip(0, None).alias("H"),
                       (pl.col("day_idx") - d0["day_idx"][0]).alias("N"),
                       ((pl.col("t_mid") - t0).dt.total_seconds() / 3600).alias("W"),
                       pl.col("r_cum").cast(pl.Float64).alias("Ri"))
    return w


def kickoff_scores(S: Store, rec: dict, rows: np.ndarray, V=None):
    V = S.V if V is None else V
    reg = rec["regime"]; P = rec["goal_no"]
    kP = S.G[reg][S.kick[P]]
    dec = np.stack([S.G[reg][gid] for g, gid in S.kick.items() if g not in (P - 1, P, P + 1)])
    X = V[rows]
    return X @ kP - (X @ dec.T).mean(1)


def aggregate(w: pl.DataFrame, a: np.ndarray, agent_weight: dict | None = None):
    """Window-level mean of agent scores (optionally with bootstrap agent multiplicities)."""
    df = w.select("pt_date", "win30", "agent", "slot", "H", "N", "W", "Ri").with_columns(pl.Series("a", a))
    if agent_weight is not None:
        df = df.with_columns(pl.col("agent").replace_strict(agent_weight, default=0).cast(pl.Float64).alias("m"))
        df = df.filter(pl.col("m") > 0)
    else:
        df = df.with_columns(pl.lit(1.0).alias("m"))
    g = df.group_by("pt_date", "win30").agg(
        ((pl.col("a") * pl.col("m")).sum() / pl.col("m").sum()).alias("A"), pl.col("m").sum().alias("n"),
        pl.col("slot").first(), pl.col("H").mean(), pl.col("N").first(), pl.col("W").mean(),
        ((pl.col("Ri") * pl.col("m")).sum() / pl.col("m").sum()).alias("R")).sort("pt_date", "win30")
    return g


def _design(f, slot):
    n = len(f)
    S = np.zeros((n, 3))
    for k in (1, 2, 3):
        S[:, k - 1] = slot == k
    return np.column_stack([np.ones(n), f, S])


def fit_clock(g: pl.DataFrame, clock: str, slots: bool = True):
    """Grid-profiled weighted LS. Returns dict(rate, dA, Ainf, sse)."""
    y = g["A"].to_numpy(); wt = g["n"].to_numpy().astype(float); slot = g["slot"].to_numpy()
    x = g[{"N": "N", "H": "H", "W": "W", "R": "R"}[clock]].to_numpy().astype(float)
    best = None
    for r in GRID[clock]:
        f = r ** x if clock == "N" else np.exp(-x / r)
        X = _design(f, slot) if slots else np.column_stack([np.ones(len(f)), f])
        Xw = X * np.sqrt(wt)[:, None]; yw = y * np.sqrt(wt)
        beta, *_ = np.linalg.lstsq(Xw, yw, rcond=None)
        sse = float(((yw - Xw @ beta) ** 2).sum())
        if best is None or sse < best["sse"]:
            best = {"rate": float(r), "Ainf": float(beta[0]), "dA": float(beta[1]), "sse": sse}
    return best


def fit_const(g, slots=True):
    y = g["A"].to_numpy(); wt = g["n"].to_numpy().astype(float); slot = g["slot"].to_numpy()
    X = _design(np.zeros(len(y)), slot)[:, [0, 2, 3, 4]] if slots else np.ones((len(y), 1))
    Xw = X * np.sqrt(wt)[:, None]; yw = y * np.sqrt(wt)
    beta, *_ = np.linalg.lstsq(Xw, yw, rcond=None)
    return float(((yw - Xw @ beta) ** 2).sum())


def fit_nested(g, slots=True):
    """lambda^N exp(-H/tau): returns lambda, tau, sse."""
    y = g["A"].to_numpy(); wt = g["n"].to_numpy().astype(float); slot = g["slot"].to_numpy()
    N = g["N"].to_numpy().astype(float); H = g["H"].to_numpy().astype(float)
    best = None
    for lam in np.linspace(0.05, 1.5, 30):          # lambda > 1 allowed (a night *raises* remanence)
        for tau in GRID["H"][::2]:
            f = lam ** N * np.exp(-H / tau)
            X = _design(f, slot) if slots else np.column_stack([np.ones(len(f)), f])
            Xw = X * np.sqrt(wt)[:, None]; yw = y * np.sqrt(wt)
            beta, *_ = np.linalg.lstsq(Xw, yw, rcond=None)
            sse = float(((yw - Xw @ beta) ** 2).sum())
            if best is None or sse < best["sse"]:
                best = {"lam": float(lam), "tau": float(tau), "dA": float(beta[1]), "sse": sse}
    return best


def steps(g: pl.DataFrame, k: int = 2):
    """Model-free: night step S_N, day drift D, midday step S_mid (means over days, window-weighted)."""
    out = {"S_N": [], "D": [], "S_mid": []}
    days = g["pt_date"].unique().sort().to_list()
    per = {d: g.filter(pl.col("pt_date") == d).sort("win30") for d in days}
    for j, d in enumerate(days):
        x = per[d]["A"].to_numpy()
        if len(x) >= 2 * k:
            out["D"].append(x[-k:].mean() - x[:k].mean())
            mid = len(x) // 2
            if mid >= k and len(x) - mid >= k:
                out["S_mid"].append(x[mid:mid + k].mean() - x[mid - k:mid].mean())
        if j + 1 < len(days):
            y = per[days[j + 1]]["A"].to_numpy()
            if len(x) >= k and len(y) >= k:
                out["S_N"].append(y[:k].mean() - x[-k:].mean())
    return {kk: (float(np.mean(v)) if v else np.nan) for kk, v in out.items()}


def clock_compare(g: pl.DataFrame, slots=True):
    fits = {c: fit_clock(g, c, slots) for c in CLOCKS}
    fits["0"] = {"sse": fit_const(g, slots)}
    nest = fit_nested(g, slots)
    win = min(CLOCKS, key=lambda c: fits[c]["sse"])
    return {"fits": fits, "nested": nest, "winner": win, "steps": steps(g)}


def o1_period(S: Store, rec: dict, n_boot: int = 200, seed: int = 0, V=None, slots=True, scorer=None):
    w = period_windows(S, rec)
    rows = w["ri"].to_numpy()
    a = kickoff_scores(S, rec, rows, V) if scorer is None else scorer(w, rows)
    g = aggregate(w, a)
    est = clock_compare(g, slots)
    agents = sorted(set(w["agent"].to_list()))
    rng = np.random.default_rng(seed)
    bo = []
    for _ in range(n_boot):
        pick = rng.choice(agents, size=len(agents), replace=True)
        mult = {int(x): int(c) for x, c in zip(*np.unique(pick, return_counts=True))}
        gb = aggregate(w, a, mult)
        cc = clock_compare(gb, slots)
        d1 = gb.filter(pl.col("N") == 0)
        lvl = float((d1["A"] * d1["n"]).sum() / d1["n"].sum()) if d1.height else np.nan
        bo.append({"lvl1": lvl, "win": cc["winner"], "N_beats_H": cc["fits"]["N"]["sse"] < cc["fits"]["H"]["sse"],
                   "dA": cc["fits"][cc["winner"]]["dA"], "lam": cc["nested"]["lam"],
                   "SN_minus_Smid": cc["steps"]["S_N"] - cc["steps"]["S_mid"]})
    def ci(key):
        v = np.array([b[key] for b in bo], float)
        v = v[np.isfinite(v)]
        return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] if len(v) > 5 else [np.nan, np.nan]
    res = {"goal_no": rec["goal_no"], "regime": rec["regime"], "n_windows": g.height, "n_agents": len(agents),
           "n_days": len(rec["fit_days"]), "winner": est["winner"],
           "sse": {c: est["fits"][c]["sse"] for c in CLOCKS + ["0"]},
           "rate": {c: est["fits"][c]["rate"] for c in CLOCKS}, "dA": {c: est["fits"][c]["dA"] for c in CLOCKS},
           "Ainf": {c: est["fits"][c]["Ainf"] for c in CLOCKS},
           "nested": est["nested"], "steps": est["steps"],
           "level_day1": float((g.filter(pl.col("N") == 0)["A"] * g.filter(pl.col("N") == 0)["n"]).sum()
                               / max(g.filter(pl.col("N") == 0)["n"].sum(), 1)), "level_day1_ci": ci("lvl1"),
           "dA_best_ci": ci("dA"), "lam_ci": ci("lam"), "SN_minus_Smid_ci": ci("SN_minus_Smid"),
           "p_N_beats_H": float(np.mean([b["N_beats_H"] for b in bo])) if bo else np.nan,
           "boot_winner_share": {c: float(np.mean([b["win"] == c for b in bo])) for c in CLOCKS} if bo else {},
           "series": {"H": g["H"].to_list(), "N": g["N"].to_list(), "A": g["A"].to_list(), "n": g["n"].to_list(),
                      "slot": g["slot"].to_list()}}
    res["verdict"] = verdict_o1(res)
    return res


def verdict_o1(r):
    lo = r["dA_best_ci"][0]
    if not (np.isfinite(lo) and lo > 0):
        return "descriptive"
    if r["sse"]["H"] <= r["sse"]["N"]:
        return "failed"
    if r["winner"] == "N" and np.isfinite(r["lam_ci"][1]) and r["lam_ci"][1] < 1:
        return "supported"
    return "mixed"


# ------------------------------------------------------------------------------------------- O3 pairs
def unit_pairs(S: Store, w: pl.DataFrame, V=None, with_reset=False):
    """All eligible pairs of one agent's windows (same day dH >= 0.5, or consecutive active days)."""
    V = S.V if V is None else V
    nights = dict(zip(S.days["pt_date"].to_list(), S.days["night_before_h"].to_list()))
    gaps = S.gaps
    out = []
    for (agent,), wa in w.group_by(["agent"]):
        wa = wa.sort("t_mid")
        ri = wa["ri"].to_numpy(); di = wa["day_idx"].to_numpy(); h = wa["hcum"].to_numpy()
        sl = wa["slot"].to_numpy(); t = wa["t_mid"].to_numpy(); dd = wa["pt_date"].to_numpy()
        rc = wa["r_cum"].to_numpy().astype(float)
        X = V[ri]
        C = X @ X.T
        i, j = np.triu_indices(len(ri), 1)
        dN = di[j] - di[i]; dH = h[j] - h[i]
        keep = ((dN == 0) & (dH >= 0.5)) | ((dN == 1) & (dH >= 0.5))
        i, j = i[keep], j[keep]
        if len(i) == 0:
            continue
        ga = gaps.filter(pl.col("agent") == agent)
        gap = np.zeros(len(i), bool)
        if ga.height:
            gm = (ga["g_start"] + (ga["g_end"] - ga["g_start"]) / 2).to_numpy()
            gd = ga["pt_date"].to_numpy()
            same = di[i] == di[j]
            for k in np.flatnonzero(same):
                sel = gd == dd[i[k]]
                if sel.any():
                    gap[k] = np.any((gm[sel] > t[i[k]]) & (gm[sel] < t[j[k]]))
        G = np.array([nights.get(x, np.nan) if n == 1 else 0.0 for x, n in zip(dd[j], di[j] - di[i])])
        out.append(pl.DataFrame({"agent": np.full(len(i), agent), "C": C[i, j], "dH": h[j] - h[i],
                                 "N": (di[j] - di[i]).astype(np.int8), "G": G, "slot_a": sl[i], "slot_b": sl[j],
                                 "gap": gap, "dr": rc[j] - rc[i]}))
    return pl.concat(out) if out else None


def pair_design(p: pl.DataFrame, g_wk: float, with_reset=False):
    dH = p["dH"].to_numpy()
    B = np.column_stack([(dH >= DH_EDGES[k]) & (dH < DH_EDGES[k + 1]) for k in range(1, len(DH_EDGES) - 1)])
    # unordered slot-pair fixed effects (10 classes, {0,0} baseline): a time-of-day field makes pairs from
    # different quarters of the day less alike, which additive slot effects cannot absorb (synthetic T-ToD)
    a_, b_ = p["slot_a"].to_numpy().astype(int), p["slot_b"].to_numpy().astype(int)
    lo_, hi_ = np.minimum(a_, b_), np.maximum(a_, b_)
    code = lo_ * 4 + hi_
    classes = [x * 4 + y for x in range(4) for y in range(x, 4)][1:]
    sp = np.column_stack([code == c for c in classes])
    N = p["N"].to_numpy().astype(float)
    G = np.nan_to_num(p["G"].to_numpy(), nan=g_wk)
    wkend = (G > 30).astype(float)          # only real weekend breaks carry the break-length term
    cols = [N, N * wkend * (G - g_wk) / 24.0, p["gap"].to_numpy().astype(float)]
    names = ["beta_N", "beta_G", "beta_gap"]
    if with_reset:
        same = (N == 0).astype(float)
        cols.append(same * p["dr"].to_numpy()); names.append("beta_R")
    dHc = np.minimum(dH, 8.0)   # within-bin slope: a continuous lag term on top of the 0.5-h bins (synthetic T-H bias)
    X = np.column_stack(cols + [B, sp, dHc, dHc ** 2]).astype(float)
    return X, names


def ols_fe(X, y, agent, w=None):
    """Agent fixed effects by within-transformation (weighted); returns coefficients."""
    w = np.ones(len(y)) if w is None else w
    ua, inv = np.unique(agent, return_inverse=True)
    sw = np.bincount(inv, weights=w)
    def demean(Z):
        m = np.zeros((len(ua), Z.shape[1]))
        np.add.at(m, inv, Z * w[:, None])
        return Z - (m / np.where(sw > 0, sw, 1)[:, None])[inv]
    Xd = demean(X); yd = demean(y[:, None])[:, 0]
    keep = Xd.std(0) > 1e-9
    sq = np.sqrt(w)
    beta = np.full(X.shape[1], np.nan)
    b, *_ = np.linalg.lstsq(Xd[:, keep] * sq[:, None], yd * sq, rcond=None)
    beta[keep] = b
    return beta


def o3_fit(p: pl.DataFrame, n_boot=200, seed=0, with_reset=False):
    nights = p.filter(pl.col("N") == 1)["G"].to_numpy()
    wk = nights[np.isfinite(nights) & (nights <= 30)]
    g_wk = float(np.median(wk)) if len(wk) else 20.0
    X, names = pair_design(p, g_wk, with_reset)
    y = p["C"].to_numpy().astype(float); agent = p["agent"].to_numpy()
    est = ols_fe(X, y, agent)
    rng = np.random.default_rng(seed)
    ua = np.unique(agent)
    boots = []
    for _ in range(n_boot):
        pick = rng.choice(ua, size=len(ua), replace=True)
        u, c = np.unique(pick, return_counts=True)
        m = dict(zip(u.tolist(), c.tolist()))
        wts = np.array([m.get(a, 0) for a in agent], float)
        sel = wts > 0
        boots.append(ols_fe(X[sel], y[sel], agent[sel], wts[sel])[:len(names)])
    boots = np.array(boots)
    out = {"n_pairs": int(len(y)), "n_agents": int(len(ua)), "n_cross_night": int((p["N"] == 1).sum()),
           "n_weekend": int(((p["N"] == 1) & (p["G"] > 30)).sum()), "n_gap": int(p["gap"].sum()), "g_wk": g_wk}
    for k, nm in enumerate(names):
        v = boots[:, k][np.isfinite(boots[:, k])]
        out[nm] = {"est": float(est[k]), "lo": float(np.percentile(v, 2.5)) if len(v) > 5 else np.nan,
                   "hi": float(np.percentile(v, 97.5)) if len(v) > 5 else np.nan,
                   "se": float(np.std(v)) if len(v) > 5 else np.nan}
    return out


def re_mean(est, se):
    """DerSimonian-Laird random-effects mean."""
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    if len(est) == 0:
        return {"est": np.nan, "lo": np.nan, "hi": np.nan, "k": 0, "tau2": np.nan}
    w = 1 / se ** 2
    mu = (w * est).sum() / w.sum()
    Q = (w * (est - mu) ** 2).sum()
    tau2 = max(0.0, (Q - (len(est) - 1)) / (w.sum() - (w ** 2).sum() / w.sum())) if len(est) > 1 else 0.0
    ws = 1 / (se ** 2 + tau2)
    m = (ws * est).sum() / ws.sum(); s = np.sqrt(1 / ws.sum())
    return {"est": float(m), "lo": float(m - 1.96 * s), "hi": float(m + 1.96 * s), "k": int(len(est)),
            "tau2": float(tau2)}
