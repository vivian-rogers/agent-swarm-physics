"""H127 estimators and loaders: per-agent levels (pre, settled), one-parameter rise fits on a clock, half times,
Theil-Sen slope on call rate, collapse ratio CR, common-tau clock comparison dSSE, read-out test.
The same code runs on real data (run.py, natives.py, confirm.py) and synthetic data (synthetic.py).
Projection code mirrors H125's excess alignment (no import across hypothesis folders)."""
from __future__ import annotations

import os

for _v, _n in (("POLARS_MAX_THREADS", "2"), ("OMP_NUM_THREADS", "2"), ("OPENBLAS_NUM_THREADS", "2"),
               ("MKL_NUM_THREADS", "2"), ("VECLIB_MAXIMUM_THREADS", "2")):
    os.environ.setdefault(_v, _n)

import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy.stats import theilslopes  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
S = ROOT / "data/processed/shared"
ED = S / "embeddings"
H125 = ROOT / "data/processed/H125-kickoff-damped-oscillator"
DATA = ROOT / "data/processed/H127-content-trails-goal-call-clock"
CFGS = {"bge_white": ("bge_small", "white"), "gte_white": ("gte_modernbert", "white"),
        "bge_style": ("bge_small", "style"), "gte_style": ("gte_modernbert", "style")}
MIN_PRE, MIN_DAY1, MIN_SET = 4, 8, 4
RISE_Z = 2.0
GRID = {"h": np.geomspace(0.0001, 50.0, 80), "c": np.geomspace(0.1, 5000.0, 64)}   # Amendment 1: hour floor 0.36 s (was 18 s)
_C: dict = {}


# ============================================================================================ loading and projections
def statement_matrix(model, variant):
    key = ("Z", model, variant)
    if key not in _C:
        name = {"white": "statements_white32", "style": "statements_style_resid_period32"}[variant]
        _C[key] = np.load(ED / f"{name}_{model}.npy", mmap_mode="r")
    return _C[key]


def tables(src125: Path = H125, data: Path = DATA):
    key = ("tab", str(src125), str(data))
    if key not in _C:
        _C[key] = dict(k=pl.read_parquet(src125 / "kickoffs.parquet"), st=pl.read_parquet(src125 / "stmt.parquet"),
                       v=dict(np.load(src125 / "vectors.npz")), ag=pl.read_parquet(data / "agents.parquet"),
                       d1=pl.read_parquet(data / "day1.parquet"))
    return _C[key]


def excess(rows: np.ndarray, agents: np.ndarray, krow: dict, cfg: str, V: dict) -> np.ndarray:
    """Per-statement excess alignment (own target minus mean decoy), linear; kickoff or own-role designs."""
    model, variant = CFGS[cfg]
    X = np.asarray(statement_matrix(model, variant)[rows], dtype=np.float64)
    if krow["native"] in ("G51", "NE38"):
        roles = {int(k): int(v) for k, v in json.loads(krow["role_gids"]).items()}
        R = V[f"R|{model}"]; rg = list(V["role_gid"])
        a = np.full(len(rows), np.nan)
        for i in np.unique(agents):
            if int(i) not in roles:
                continue
            own = R[rg.index(roles[int(i)])]
            others = [R[rg.index(g)] for j, g in roles.items() if j != int(i)]
            others = [o for o in others if float(o @ own) < 0.95]
            m = agents == i
            a[m] = X[m] @ own - np.mean([X[m] @ o for o in others], axis=0)
        return a
    K = V[f"K|{model}|{krow['regime']}"]; kg = list(V["kick_goal_no"])
    own = K[kg.index(krow["goal_no"])]
    D = K[[j for j, g in enumerate(kg) if g not in (krow["goal_no"] - 1, krow["goal_no"], krow["goal_no"] + 1, 23)]]
    return X @ own - (X @ D.T).mean(1)


def build_units(design: str, cfg: str, src125: Path = H125, data: Path = DATA) -> list[dict]:
    """Per agent: P, S, Delta, SE, rising flag, day-1 arrays (a, h, c, h_ro, c_ro), r, r_lpo, lab."""
    T = tables(src125, data)
    krow = T["k"].filter(pl.col("design") == design).row(0, named=True)
    src_des = "G51" if design == "G51" else design
    st = T["st"].filter(pl.col("design") == src_des)
    a_all = excess(st["row"].to_numpy(), st["agent"].to_numpy(), krow, cfg, T["v"])
    st = st.with_columns(pl.Series("a", a_all))
    d1 = T["d1"].filter(pl.col("design") == design).join(st.select("row", "a").unique("row"), on="row", how="left")
    units = []
    for r in T["ag"].filter(pl.col("design") == design).iter_rows(named=True):
        i = r["agent"]
        sa = st.filter(pl.col("agent") == i)
        pre = sa.filter(pl.col("seg") == "pre")["a"].drop_nans().drop_nulls().to_numpy()
        sett = sa.filter((pl.col("seg") == "post") & pl.col("day_idx").is_between(2, 5))["a"].drop_nans().drop_nulls().to_numpy()
        dd = d1.filter(pl.col("agent") == i).sort("h")
        u = dict(design=design, agent=i, regime=r["regime"], lab=r["lab"], r=r["r"], r_lpo=r["r_lpo"],
                 n_pre=len(pre), n_set=len(sett), n_day1=dd.height, ro_fallback=r["ro_fallback"], ro_delay_h=r["ro_delay_h"])
        pre_fb = len(pre) < MIN_PRE
        P = 0.0 if pre_fb else float(pre.mean())
        Sv = float(sett.mean()) if len(sett) else np.nan
        se = np.sqrt((pre.var(ddof=1) / len(pre) if not pre_fb else 0.0) + (sett.var(ddof=1) / len(sett) if len(sett) > 1 else np.nan))
        u.update(P=P, S=Sv, Delta=Sv - P, se_Delta=float(se), pre_fallback=pre_fb,
                 a=dd["a"].to_numpy().astype(float), h=dd["h"].to_numpy().astype(float), c=dd["c"].to_numpy().astype(float),
                 h_ro=dd["h_ro"].to_numpy().astype(float), c_ro=dd["c_ro"].to_numpy().astype(float))
        ok = np.isfinite(u["a"])
        for kk in ("a", "h", "c", "h_ro", "c_ro"):
            u[kk] = u[kk][ok]
        u["eligible"] = bool(len(sett) >= MIN_SET and ok.sum() >= MIN_DAY1 and r["calls_day1"] >= 3)
        u["rising"] = bool(u["eligible"] and u["Delta"] > RISE_Z * u["se_Delta"])
        units.append(u)
    return units


# ============================================================================================ fits
def _F(x, tau):
    x = np.clip(x, 0, None)
    return 1.0 - np.exp(-x[:, None] / tau[None, :])


AMP_FREE = True   # Amendment 1: the day-1 plateau amplitude is free (False = the card's fixed-Delta form)


def fit_tau(a, x, P, Delta, grid, amp_free=None):
    """LS fit of a = P + A (1 - exp(-x/tau)) on a tau grid. amp_free: A >= 0 solved per tau (half time of the day-1
    plateau); else A = Delta (the settled rise; the card's original form). Returns tau, at_floor, at_ceiling."""
    amp_free = AMP_FREE if amp_free is None else amp_free
    F = _F(x, grid)
    y = (a - P)
    if amp_free:
        A = np.clip((F * y[:, None]).sum(0) / np.maximum((F ** 2).sum(0), 1e-12), 0, None)
    else:
        A = np.full(F.shape[1], Delta)
    sse = ((y[:, None] - A * F) ** 2).sum(0)
    j = int(np.argmin(sse))
    return float(grid[j]), j == 0, j == len(grid) - 1


def unit_half_times(u: dict) -> dict:
    out = {}
    for key, clock, g in (("TH", "h", "h"), ("TC", "c", "c"), ("THro", "h_ro", "h"), ("TCro", "c_ro", "c")):
        x = u[clock]
        if not np.isfinite(x).all() or len(x) == 0:
            out[key] = np.nan; out[key + "_floor"] = False
            continue
        tau, fl, ce = fit_tau(u["a"], x, u["P"], u["Delta"], GRID[g])
        out[key] = tau * np.log(2); out[key + "_floor"] = fl; out[key + "_ceil"] = ce
    return out


def mad2(x):
    x = x[np.isfinite(x)]
    if len(x) < 3:
        return np.nan
    return float((1.4826 * np.median(np.abs(x - np.median(x)))) ** 2)


def ts_slope(y, x):
    ok = np.isfinite(y) & np.isfinite(x)
    if ok.sum() < 4 or np.ptp(x[ok]) == 0:
        return np.nan
    return float(theilslopes(y[ok], x[ok])[0])


def common_sse(units, clock, grid, amp_free=None):
    """Common-tau fit across agents (each agent weighted 1/n_i; per-agent amplitude free if AMP_FREE).
    Returns min SSE, SSE(step at the clock origin), SSE(no rise), best tau."""
    amp_free = AMP_FREE if amp_free is None else amp_free
    tot = np.zeros(len(grid)); s1 = 0.0; s0 = 0.0
    for u in units:
        x = u[clock]; n = len(x)
        if n == 0 or not np.isfinite(x).all():
            continue
        y = u["a"] - u["P"]
        F = _F(x, grid)
        if amp_free:
            A = np.clip((F * y[:, None]).sum(0) / np.maximum((F ** 2).sum(0), 1e-12), 0, None)
            st = (x > 0).astype(float); A1 = max(0.0, float(st @ y) / max(st @ st, 1e-12))
        else:
            A = np.full(F.shape[1], u["Delta"]); st = (x > 0).astype(float); A1 = u["Delta"]
        tot += ((y[:, None] - A * F) ** 2).sum(0) / n
        s1 += ((y - A1 * st) ** 2).sum() / n
        s0 += (y ** 2).sum() / n
    return float(tot.min()), float(s1), float(s0), float(grid[int(np.argmin(tot))])


def analyze_kickoff(units: list[dict], n_boot: int = 500, seed: int = 0, rate: str = "r") -> dict:
    elig = [u for u in units if u["eligible"]]
    ris = [u for u in elig if u["rising"]]
    res = dict(n_agents=len(units), n_elig=len(elig), n_rise=len(ris), rise_share=len(ris) / len(elig) if elig else np.nan)
    if not ris:
        res.update(n_fit=0, s=np.nan, s_lo=np.nan, s_hi=np.nan, se_s=np.nan, CR=np.nan, dsse=np.nan)
        return res
    ht = [unit_half_times(u) for u in ris]
    TH = np.array([h["TH"] for h in ht]); TC = np.array([h["TC"] for h in ht])
    THro = np.array([h["THro"] for h in ht])
    lr = np.log(np.array([u[rate] if u[rate] else np.nan for u in ris], dtype=float))
    lTH, lTC, lTHro = np.log(TH), np.log(TC), np.log(THro)
    res["n_fit"] = int(np.isfinite(lTH).sum())
    res["s"] = ts_slope(lTH, lr)
    res["s_ro"] = ts_slope(lTHro, lr)
    res["CR"] = mad2(lTC) / mad2(lTH) if mad2(lTH) and mad2(lTH) > 0 else np.nan
    res["med_T_H"] = float(np.nanmedian(TH)); res["med_T_C"] = float(np.nanmedian(TC)); res["med_T_Hro"] = float(np.nanmedian(THro))
    res["imm_t0"] = float(np.mean([h["TH_floor"] for h in ht]))
    res["imm_ro"] = float(np.mean([h["THro_floor"] for h in ht]))
    res["ceil_t0"] = float(np.mean([h.get("TH_ceil", False) for h in ht]))
    sH, s1, s0, tH = common_sse(ris, "h", GRID["h"]); sC, _, _, tC = common_sse(ris, "c", GRID["c"])
    den = s0 - min(sH, sC)
    res["dsse"] = (sH - sC) / den if den > 0 else np.nan
    res["dsse_step"] = (sH - sC) / (s1 - min(sH, sC)) if (s1 - min(sH, sC)) > 0 else np.nan
    res["tau_common_H"], res["tau_common_C"] = tH, tC
    sHr, _, s0r, _ = common_sse(ris, "h_ro", GRID["h"]); sCr, _, _, _ = common_sse(ris, "c_ro", GRID["c"])
    den = s0r - min(sHr, sCr)
    res["dsse_ro"] = (sHr - sCr) / den if den > 0 else np.nan
    res["_per_agent"] = [dict(design=u["design"], agent=u["agent"], lab=u["lab"], r=u["r"], r_lpo=u["r_lpo"], TH=h["TH"], TC=h["TC"], THro=h["THro"],
                              TH_floor=h["TH_floor"], THro_floor=h["THro_floor"], Delta=u["Delta"], S=u["S"], P=u["P"],
                              pre_fallback=u["pre_fallback"], ro_delay_h=u["ro_delay_h"]) for u, h in zip(ris, ht)]
    if n_boot and res["n_fit"] >= 4:
        rng = np.random.default_rng(seed)
        bs, bc = [], []
        n = len(ris)
        for _ in range(n_boot):
            ix = rng.integers(0, n, n)
            if len(np.unique(ix)) < 3:
                continue
            bs.append(ts_slope(lTH[ix], lr[ix]))
            m = mad2(lTH[ix])
            bc.append(mad2(lTC[ix]) / m if m and m > 0 else np.nan)
        bs = np.array(bs); bs = bs[np.isfinite(bs)]
        if len(bs) > 20:
            res["s_lo"], res["s_hi"] = float(np.percentile(bs, 5)), float(np.percentile(bs, 95))
            res["se_s"] = float(bs.std(ddof=1))
        else:
            res["s_lo"] = res["s_hi"] = res["se_s"] = np.nan
    else:
        res["s_lo"] = res["s_hi"] = res["se_s"] = np.nan
    return res


# ============================================================================================ meta-analysis
def dl_meta(est, se):
    est = np.asarray(est, float); se = np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    if len(est) < 2:
        return dict(mean=float(est[0]) if len(est) else np.nan, se=np.nan, tau2=np.nan, k=len(est))
    w = 1 / se ** 2
    m0 = (w * est).sum() / w.sum()
    Q = (w * (est - m0) ** 2).sum()
    c = w.sum() - (w ** 2).sum() / w.sum()
    tau2 = max(0.0, (Q - (len(est) - 1)) / c)
    ws = 1 / (se ** 2 + tau2)
    return dict(mean=float((ws * est).sum() / ws.sum()), se=float(np.sqrt(1 / ws.sum())), tau2=float(tau2), k=int(len(est)))


def sign_p(x, alternative="greater"):
    from scipy.stats import binomtest
    x = np.asarray(x, float); x = x[np.isfinite(x) & (x != 0)]
    if not len(x):
        return np.nan
    return float(binomtest(int((x > 0).sum()), len(x), 0.5, alternative=alternative).pvalue)


def jack_meta_se(vals):
    v = np.asarray(vals, float); v = v[np.isfinite(v)]
    n = len(v)
    if n < 3:
        return np.nan
    loo = (v.sum() - v) / (n - 1)
    return float(np.sqrt((n - 1) / n * ((loo - loo.mean()) ** 2).sum()))


def pooled_slope(per_agent: list[dict], rate: str = "r", key: str = "TH", n_boot: int = 500, seed: int = 0,
                 controls: list[str] | None = None) -> dict:
    """Pooled within-kickoff slope (exception (d) companion): OLS of log T on log rate with kickoff fixed effects
    (both demeaned within kickoff), optional controls (demeaned within kickoff). CI: bootstrap over kickoffs."""
    df = pl.DataFrame([{k: v for k, v in r.items() if k in ("design", "agent", "lab", rate, key, *(controls or []))}
                       for r in per_agent], infer_schema_length=None)
    df = df.filter(pl.col(rate).is_not_null() & pl.col(key).is_not_null())
    df = df.with_columns(pl.col(rate).log().alias("lx"), pl.col(key).log().alias("ly"))
    df = df.filter(pl.col("lx").is_finite() & pl.col("ly").is_finite())
    cols = ["lx"] + (controls or [])
    df = df.drop_nulls(cols)
    des = df["design"].to_numpy()

    def est(ix_designs):
        parts = [df.filter(pl.col("design") == d) for d in ix_designs]
        parts = [p for p in parts if p.height >= 2]
        if len(parts) < 3:
            return np.nan
        Xs, ys = [], []
        for p in parts:
            X = p.select(cols).to_numpy().astype(float); y = p["ly"].to_numpy().astype(float)
            Xs.append(X - X.mean(0)); ys.append(y - y.mean())
        X = np.vstack(Xs); y = np.concatenate(ys)
        b, *_ = np.linalg.lstsq(X, y, rcond=None)
        return float(b[0])
    ud = np.unique(des)
    b0 = est(ud)
    rng = np.random.default_rng(seed)
    bs = np.array([est(rng.choice(ud, len(ud), replace=True)) for _ in range(n_boot)])
    bs = bs[np.isfinite(bs)]
    return dict(s_pool=b0, s_pool_lo=float(np.percentile(bs, 5)) if len(bs) > 20 else np.nan,
                s_pool_hi=float(np.percentile(bs, 95)) if len(bs) > 20 else np.nan, n_agents=int(df.height), n_kick=int(len(ud)))


def group_stretch(units: list[dict], rate: str = "r", origin: str = "t0") -> dict:
    """Amendment 1 (group-level time-rescaling, P1g/P2g): split the kickoff's rising agents at the median call rate;
    fit one common tau per half on each clock (agents weighted 1/n_i, amplitude free per agent).
    Returns dlr = log(r_slow / r_fast) (geometric means), dlt_H = log(tau_H,slow / tau_H,fast), dlt_C likewise.
    Call clock: dlt_H = -dlr, dlt_C = 0. Hour clock: dlt_H = 0, dlt_C = +dlr."""
    ris = [u for u in units if u["rising"] and u.get(rate)]
    if len(ris) < 4:
        return dict(dlr=np.nan, dlt_H=np.nan, dlt_C=np.nan, n=len(ris))
    r = np.array([u[rate] for u in ris], float)
    o = np.argsort(r)
    half = len(ris) // 2
    slow, fast = [ris[j] for j in o[:half]], [ris[j] for j in o[-half:]]
    hk, ck = ("h", "c") if origin == "t0" else ("h_ro", "c_ro")
    tH_s = common_sse(slow, hk, GRID["h"])[3]; tH_f = common_sse(fast, hk, GRID["h"])[3]
    tC_s = common_sse(slow, ck, GRID["c"])[3]; tC_f = common_sse(fast, ck, GRID["c"])[3]
    g = lambda us: float(np.exp(np.mean(np.log([u[rate] for u in us]))))  # noqa: E731
    return dict(dlr=float(np.log(g(slow) / g(fast))), dlt_H=float(np.log(tH_s / tH_f)), dlt_C=float(np.log(tC_s / tC_f)),
                n=len(ris), floor=bool(min(tH_s, tH_f) <= GRID["h"][0]))


def stretch_card(rows: list[dict], n_boot: int = 1000, seed: int = 0) -> dict:
    """Across kickoffs: s_g = sum(dlt_H dlr) / sum(dlr^2) (through the origin; -1 call clock, 0 hour clock);
    collapse gain G = mean|dlt_H| - mean|dlt_C| (> 0: calls collapse the halves). Bootstrap over kickoffs."""
    d = [x for x in rows if np.isfinite(x["dlr"]) and np.isfinite(x["dlt_H"]) and np.isfinite(x["dlt_C"])]
    if len(d) < 3:
        return dict(s_g=np.nan, s_g_lo=np.nan, s_g_hi=np.nan, G=np.nan, G_lo=np.nan, G_hi=np.nan, k=len(d))
    dr = np.array([x["dlr"] for x in d]); dh = np.array([x["dlt_H"] for x in d]); dc = np.array([x["dlt_C"] for x in d])
    f = lambda ix: (float((dh[ix] * dr[ix]).sum() / (dr[ix] ** 2).sum()), float(np.abs(dh[ix]).mean() - np.abs(dc[ix]).mean()))  # noqa: E731
    s0, G0 = f(np.arange(len(d)))
    rng = np.random.default_rng(seed)
    bs = np.array([f(rng.integers(0, len(d), len(d))) for _ in range(n_boot)])
    return dict(s_g=s0, s_g_lo=float(np.percentile(bs[:, 0], 5)), s_g_hi=float(np.percentile(bs[:, 0], 95)),
                G=G0, G_lo=float(np.percentile(bs[:, 1], 5)), G_hi=float(np.percentile(bs[:, 1], 95)), k=len(d))
