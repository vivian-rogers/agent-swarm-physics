"""H63 library: arrivals, herding bursts, burst-level precedence of work signals and links, the arrival-hazard
lead-lag model (Poisson with agent, project and day fields) and a point-process simulator for axis F.

Data contract (per period, all times float seconds): see scheme/build.py. Everything here runs unchanged on the
simulator's output (`simulate`).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data/processed/H63-bursts-start-with-work"
BIN = 300.0
OFF = 3600.0          # off-project spell before an arrival
LINK_GAP = 1200.0     # single-linkage gap between arrivals of one burst
QUIET = 3600.0        # no arrival onto the project before a cluster's first arrival
WIN = 3600.0          # precedence / hazard window
EDGE = 1800.0         # arrivals within 30 min of the agent's first call of the day are not counted (scheduler)
UNIVERSE_MAX = 30


def load(g: int, root: Path | None = None) -> dict:
    d = (root or OUT) / f"G{g:02d}"
    return {k: pl.read_parquet(d / f"{k}.parquet") for k in ("touches", "links", "signals", "bins", "days", "spans",
                                                              "kicks")}


# ============================================================================================ arrivals and bursts
def arrivals(P: dict, trim: bool = True) -> pl.DataFrame:
    """Agent i's first touch of X after >= 60 min without one (same day). trim: inside the all-present window and
    >= 30 min after the agent's first call of the day."""
    t = P["touches"].sort("agent", "project", "t")
    t = t.with_columns(pl.col("t").shift(1).over(["agent", "project", "day"]).alias("t_prev"))
    a = t.filter(pl.col("t_prev").is_null() | (pl.col("t") - pl.col("t_prev") >= OFF)).drop("t_prev")
    a = a.join(P["days"].select("day", "ap_lo", "ap_hi"), on="day", how="left").join(
        P["spans"].select("day", "agent", "first_call"), on=["day", "agent"], how="left")
    a = a.with_columns(((pl.col("t") >= pl.col("ap_lo")) & (pl.col("t") <= pl.col("ap_hi"))
                        & (pl.col("t") - pl.col("first_call") >= EDGE)).fill_null(False).alias("trim"))
    if trim:
        a = a.filter(pl.col("trim"))
    return a.select("t", "day", "agent", "project", "source", "trim").sort("project", "t")


def clusters(arr: pl.DataFrame, all_arr: pl.DataFrame) -> pl.DataFrame:
    """Single-linkage clusters of arrivals onto each project (gap <= 20 min). Columns: project, day, t0, tf (second
    distinct agent's arrival, or the only arrival), t_end, n_agents, quiet (no arrival, trimmed or not, onto the
    project in the 60 min before t0), agents (list)."""
    rows = []
    allp = {p: np.sort(g["t"].to_numpy()) for (p,), g in all_arr.group_by(["project"])}
    for (p, d), g in arr.group_by(["project", "day"]):
        g = g.sort("t")
        ts, ag = g["t"].to_numpy(), g["agent"].to_numpy()
        start = 0
        for k in range(1, len(ts) + 1):
            if k == len(ts) or ts[k] - ts[k - 1] > LINK_GAP:
                tt, aa = ts[start:k], ag[start:k]
                seen, tf = [], None
                for x, y in zip(tt, aa):
                    if y not in seen:
                        seen.append(y)
                        if len(seen) == 2:
                            tf = x
                if tf is None:
                    tf = tt[0]
                at = allp.get(p, np.zeros(0))
                prior = np.searchsorted(at, tt[0], "left") - np.searchsorted(at, tt[0] - QUIET, "left")
                rows.append({"project": p, "day": int(d), "t0": float(tt[0]), "tf": float(tf), "t_end": float(tt[-1]), "n_agents": len(seen),
                             "quiet": bool(prior == 0), "agents": [int(x) for x in seen]})
                start = k
    if not rows:
        return pl.DataFrame(schema={"project": pl.String, "day": pl.Int16, "t0": pl.Float64, "tf": pl.Float64,
                                    "t_end": pl.Float64, "n_agents": pl.Int64, "quiet": pl.Boolean,
                                    "agents": pl.List(pl.Int64)})
    return pl.DataFrame(rows)


def _times(df: pl.DataFrame, cond=None) -> dict:
    if cond is not None:
        df = df.filter(cond)
    return {p: np.sort(g["t"].to_numpy()) for (p,), g in df.group_by(["project"])}


def _has(tdict, p, lo, hi) -> bool:
    a = tdict.get(p)
    if a is None or not len(a):
        return False
    return bool(np.searchsorted(a, hi, "left") - np.searchsorted(a, lo, "left") > 0)


def _first(tdict, p, lo, hi):
    a = tdict.get(p)
    if a is None or not len(a):
        return np.nan
    i = np.searchsorted(a, lo, "left")
    return a[i] if i < len(a) and a[i] < hi else np.nan


def precedence(P: dict, cl: pl.DataFrame, sig: pl.DataFrame | None = None) -> pl.DataFrame:
    """Per cluster: indicators of an S / R / B signal and a link on its project in [tf - 60 min, tf), the ordering
    of the first S and the first link in [t0 - 60 min, t_end], and exogenous flags."""
    sig = P["signals"] if sig is None else sig
    S = _times(sig, pl.col("cls") == "S")
    R = _times(sig, pl.col("cls") == "R")
    Bt = _times(sig, pl.col("cls") == "B")
    Lk = _times(P["links"], pl.col("speaker_kind") == "agent")
    Hk = _times(P["links"], pl.col("speaker_kind") == "human")
    days = P["days"]
    kick_t = None
    kk = P["kicks"].filter(pl.col("kind") == "goal_kickoff")
    if kk.height:
        kick_t = float(kk["t"].min())
    else:
        kick_t = float(days["win_start"].min())
    out = []
    for r in cl.iter_rows(named=True):
        p, tf, t0, te = r["project"], r["tf"], r["t0"], r["t_end"]
        fs, fl = _first(S, p, t0 - WIN, te + 1), _first(Lk, p, t0 - WIN, te + 1)
        out.append({"S_pre": _has(S, p, tf - WIN, tf), "R_pre": _has(R, p, tf - WIN, tf),
                    "B_pre": _has(Bt, p, tf - WIN, tf), "L_pre": _has(Lk, p, tf - WIN, tf),
                    "SB_pre": _has(S, p, tf - WIN, tf) or _has(Bt, p, tf - WIN, tf),
                    "first_S": fs, "first_L": fl,
                    "kick_led": (t0 - kick_t) >= 0 and (t0 - kick_t) < WIN,
                    "human_led": _has(Hk, p, tf - WIN, tf)})
    return pl.concat([cl, pl.DataFrame(out)], how="horizontal") if out else cl


def mh_or(tables: list) -> dict:
    """Mantel-Haenszel pooled odds ratio over 2x2 tables [[a, b], [c, d]] (a = burst & signal, b = burst & none,
    c = control & signal, d = control & none), with the Robins-Breslow-Greenland 95% CI."""
    R = S = PR = PS_QR = QS = 0.0
    for (a, b), (c, d) in tables:
        n = a + b + c + d
        if n == 0 or (a + b) == 0 or (c + d) == 0:
            continue
        if min(a, b, c, d) == 0:                      # Haldane correction for zero cells
            a, b, c, d = a + 0.5, b + 0.5, c + 0.5, d + 0.5
            n = a + b + c + d
        r, s = a * d / n, b * c / n
        p, q = (a + d) / n, (b + c) / n
        R += r
        S += s
        PR += p * r
        PS_QR += p * s + q * r
        QS += q * s
    if R == 0 or S == 0:
        return {"or": np.nan, "lo": np.nan, "hi": np.nan, "log_se": np.nan}
    orr = R / S
    v = PR / (2 * R * R) + PS_QR / (2 * R * S) + QS / (2 * S * S)
    se = np.sqrt(v)
    return {"or": orr, "lo": float(np.exp(np.log(orr) - 1.96 * se)), "hi": float(np.exp(np.log(orr) + 1.96 * se)),
            "log_se": float(se), "p": float(2 * stats.norm.sf(abs(np.log(orr)) / se))}


def table(pre: pl.DataFrame, col: str, min_burst: int = 3):
    q = pre.filter(pl.col("quiet"))
    b = q.filter(pl.col("n_agents") >= min_burst)
    c = q.filter(pl.col("n_agents") < min_burst)
    a = int(b[col].sum())
    cc = int(c[col].sum())
    return [[a, b.height - a], [cc, c.height - cc]]


def shift_signals(sig: pl.DataFrame, days: pl.DataFrame, rng, cls="S") -> pl.DataFrame:
    """Time-shift null: each S signal moved by +-U(30, 120) min, circularly within its day's window."""
    s = sig.filter(pl.col("cls") == cls).join(days.select("day", "win_start", "win_end"), on="day")
    off = rng.uniform(1800, 7200, s.height) * rng.choice([-1, 1], s.height)
    L = (s["win_end"] - s["win_start"]).to_numpy()
    t = s["win_start"].to_numpy() + ((s["t"].to_numpy() - s["win_start"].to_numpy() + off) % np.maximum(L, 1))
    s = s.with_columns(pl.Series("t", t)).select(sig.columns)
    return pl.concat([sig.filter(pl.col("cls") != cls), s]).sort("project", "t")


# ============================================================================================ hazard model
def risk_panel(P: dict, trim: bool = True, sig: pl.DataFrame | None = None) -> tuple:
    """Rows (agent, project, bin) with the agent active (>= 1 call) in the bin, the project existing and in the
    period's universe (touched by >= 2 agents; top 30 by distinct agents), the agent off the project at bin start;
    y = arrival in the bin. Regressors: S/R/L past (last 60 min) and lead (next 60 min after the bin), signals by
    other agents only, links by other agents in the agent's room; kickoff (60 min), human message in room (30 min),
    nudge to the agent (30 min)."""
    sig = P["signals"] if sig is None else sig
    tch = P["touches"]
    uni = (tch.group_by("project").agg(pl.col("agent").n_unique().alias("na")).filter(pl.col("na") >= 2)
           .sort("na", descending=True).head(UNIVERSE_MAX)["project"].to_list())
    if not uni:
        return None, None
    pidx = {p: k for k, p in enumerate(uni)}
    days = P["days"]
    b = P["bins"].join(days.select("day", "win_start", "ap_lo", "ap_hi"), on="day")
    b = b.with_columns((pl.col("win_start") + pl.col("bin") * BIN).alias("tb"))
    b = b.join(P["spans"].select("day", "agent", "first_call"), on=["day", "agent"], how="left")
    if trim:
        b = b.filter((pl.col("tb") >= pl.col("ap_lo")) & (pl.col("tb") + BIN <= pl.col("ap_hi"))
                     & (pl.col("tb") - pl.col("first_call") >= EDGE))
    if b.height == 0:
        return None, None
    tb = b["tb"].to_numpy()
    ag = b["agent"].to_numpy().astype(int)
    dy = b["day"].to_numpy().astype(int)
    rm = b["room"].fill_null(-1).to_numpy().astype(int)
    nb, npj = len(tb), len(uni)
    # project existence: first touch or first signal
    first = {}
    for (p,), g in pl.concat([tch.select("project", "t"), sig.select("project", "t")]).group_by(["project"]):
        first[p] = float(g["t"].min())
    # touches by agent-project for on/off and arrivals
    T = {}
    for (a, p), g in tch.filter(pl.col("project").is_in(uni)).group_by(["agent", "project"]):
        T[(int(a), p)] = np.sort(g["t"].to_numpy())
    arr = arrivals(P, trim=False)
    A = {}
    for (a, p), g in arr.filter(pl.col("project").is_in(uni)).group_by(["agent", "project"]):
        A[(int(a), p)] = np.sort(g["t"].to_numpy())
    # event times per project with actor
    def ev(df):
        out = {}
        for (p,), g in df.filter(pl.col("project").is_in(uni)).group_by(["project"]):
            g = g.sort("t")
            out[p] = (g["t"].to_numpy(), g["agent"].fill_null(-1).to_numpy().astype(int),
                      g["room"].fill_null(-1).to_numpy().astype(int) if "room" in g.columns else None)
        return out
    Sx = ev(sig.filter(pl.col("cls") == "S"))
    Rx = ev(sig.filter(pl.col("cls") == "R"))
    Lx = ev(P["links"].filter(pl.col("speaker_kind") == "agent"))
    kk = P["kicks"]
    kick = np.sort(kk.filter(pl.col("kind") == "goal_kickoff")["t"].to_numpy())
    if not len(kick):
        kick = np.array([float(days["win_start"].min())])
    hum = {}
    for (r,), g in kk.filter(pl.col("kind") == "human_message").group_by(["room"]):
        hum[int(r) if r is not None else -1] = np.sort(g["t"].to_numpy())
    nud = {}
    for r in kk.filter(pl.col("kind") == "nudge").iter_rows(named=True):
        for a in (r["targets"] or []):
            nud.setdefault(int(a), []).append(r["t"])
    nud = {a: np.sort(np.array(v)) for a, v in nud.items()}

    def cnt(arrt, lo, hi):
        return np.searchsorted(arrt, hi, "left") - np.searchsorted(arrt, lo, "left")

    kick_x = (cnt(kick, tb - WIN, tb) > 0).astype(float)
    hum_x = np.array([cnt(hum.get(r, np.zeros(0)), t - 1800, t) > 0 for r, t in zip(rm, tb)], float)
    nud_x = np.array([cnt(nud.get(a, np.zeros(0)), t - 1800, t) > 0 for a, t in zip(ag, tb)], float)
    cols = {k: [] for k in ("y", "agent", "proj", "day", "S", "S_lead", "R", "R_lead", "L", "L_lead", "kick", "hum",
                            "nud", "row")}
    for p in uni:
        j = pidx[p]
        exists = tb >= first.get(p, np.inf)
        # off at bin start: no touch of p by the agent in [tb - 60 min, tb)
        off = np.ones(nb, bool)
        y = np.zeros(nb)
        for a in np.unique(ag):
            ia = np.flatnonzero(ag == a)
            tt = T.get((int(a), p))
            if tt is not None:
                off[ia] = cnt(tt, tb[ia] - OFF, tb[ia]) == 0
            at = A.get((int(a), p))
            if at is not None:
                y[ia] = cnt(at, tb[ia], tb[ia] + BIN) > 0
        keep = exists & off
        if not keep.any():
            continue
        idx = np.flatnonzero(keep)

        def by_others(E, lead):
            if p not in E:
                return np.zeros(len(idx))
            et, ea, er = E[p]
            lo = tb[idx] + (BIN if lead else -WIN)
            hi = tb[idx] + (BIN + WIN if lead else 0.0)
            i0 = np.searchsorted(et, lo, "left")
            i1 = np.searchsorted(et, hi, "left")
            out = np.zeros(len(idx))
            for k in np.flatnonzero(i1 > i0):
                out[k] = float(np.any(ea[i0[k]:i1[k]] != ag[idx[k]]))
            return out

        def links_room(lead):
            if p not in Lx:
                return np.zeros(len(idx))
            et, ea, er = Lx[p]
            lo = tb[idx] + (BIN if lead else -WIN)
            hi = tb[idx] + (BIN + WIN if lead else 0.0)
            i0 = np.searchsorted(et, lo, "left")
            i1 = np.searchsorted(et, hi, "left")
            out = np.zeros(len(idx))
            for k in np.flatnonzero(i1 > i0):
                sl = slice(i0[k], i1[k])
                ok = (ea[sl] != ag[idx[k]]) & ((er[sl] == rm[idx[k]]) | (er[sl] < 0) | (rm[idx[k]] < 0))
                out[k] = float(np.any(ok))
            return out

        cols["y"].append(y[idx])
        cols["agent"].append(ag[idx])
        cols["proj"].append(np.full(len(idx), j))
        cols["day"].append(dy[idx])
        cols["S"].append(by_others(Sx, False))
        cols["S_lead"].append(by_others(Sx, True))
        cols["R"].append(by_others(Rx, False))
        cols["R_lead"].append(by_others(Rx, True))
        cols["L"].append(links_room(False))
        cols["L_lead"].append(links_room(True))
        cols["kick"].append(kick_x[idx])
        cols["hum"].append(hum_x[idx])
        cols["nud"].append(nud_x[idx])
        cols["row"].append(idx)
    if not cols["y"]:
        return None, None
    D = {k: np.concatenate(v) for k, v in cols.items()}
    return D, uni


def poisson_fe(y, X, groups, iters=60, tol=1e-7):
    """Poisson regression with several additive fixed-effect families (absorbed by alternating updates) and a Newton
    step for beta. Groups with zero outcomes are dropped first (exact for the Poisson conditional likelihood)."""
    keep = np.ones(len(y), bool)
    for _ in range(3):
        for gi in groups:
            s = np.bincount(gi[keep], weights=y[keep], minlength=gi.max() + 1)
            keep &= s[gi] > 0
    y, X = y[keep], X[keep]
    groups = [g[keep] for g in groups]
    groups = [np.unique(g, return_inverse=True)[1] for g in groups]
    k = X.shape[1]
    beta = np.zeros(k)
    fe = [np.zeros(g.max() + 1) for g in groups]
    eta_fe = np.zeros(len(y)) + np.log(max(y.mean(), 1e-9))
    for it in range(iters):
        xb = X @ beta
        for gi, (g, f) in enumerate(zip(groups, fe)):
            eta = xb + eta_fe
            mu = np.exp(np.clip(eta, -50, 50))
            sy = np.bincount(g, weights=y, minlength=len(f))
            sm = np.bincount(g, weights=mu, minlength=len(f))
            upd = np.log(np.maximum(sy, 1e-12)) - np.log(np.maximum(sm, 1e-300))
            f += upd
            eta_fe += upd[g]
        mu = np.exp(np.clip(X @ beta + eta_fe, -50, 50))
        grad = X.T @ (y - mu)
        H = (X * mu[:, None]).T @ X + 1e-8 * np.eye(k)
        step = np.clip(np.linalg.solve(H, grad), -2, 2)
        beta += step
        if np.max(np.abs(step)) < tol:
            break
    mu = np.exp(X @ beta + eta_fe)
    return beta, {"n": int(keep.sum()), "events": float(y.sum()), "mu": mu, "keep": keep}


HAZ_REGS = ["S", "S_lead", "R", "R_lead", "L", "L_lead", "kick", "hum", "nud"]


def hazard(D: dict, regs=None, B: int = 100, seed: int = 0) -> dict:
    """Fit with agent, project and day fields; day-block bootstrap (resample days, refit) for SEs of each coefficient
    and the contrasts S - S_lead, L - L_lead, S - R."""
    regs = regs or HAZ_REGS
    regs = [r for r in regs if D[r].std() > 0]
    X = np.column_stack([D[r] for r in regs])
    y = D["y"]
    groups = [D["agent"], D["proj"], D["day"]]
    if y.sum() < 10:
        return {"ok": False}
    beta, info = poisson_fe(y, X, groups)
    res = {"ok": True, "n_rows": info["n"], "n_events": info["events"], "regs": regs}
    b = dict(zip(regs, beta))

    def contrasts(bd):
        c = dict(bd)
        if "S" in bd and "S_lead" in bd:
            c["dS"] = bd["S"] - bd["S_lead"]
        if "L" in bd and "L_lead" in bd:
            c["dL"] = bd["L"] - bd["L_lead"]
        if "S" in bd and "R" in bd:
            c["S_minus_R"] = bd["S"] - bd["R"]
        return c

    pt = contrasts(b)
    ud = np.unique(D["day"])
    rng = np.random.default_rng(seed)
    boots = []
    if len(ud) >= 3 and B > 0:
        for _ in range(B):
            dd = rng.choice(ud, len(ud))
            ix = np.concatenate([np.flatnonzero(D["day"] == d) for d in dd])
            newday = np.concatenate([np.full((D["day"] == d).sum(), k) for k, d in enumerate(dd)])
            g2 = [D["agent"][ix], D["proj"][ix], newday]
            try:
                bb, _ = poisson_fe(y[ix], X[ix], g2, iters=40)
                boots.append(contrasts(dict(zip(regs, bb))))
            except np.linalg.LinAlgError:
                continue
    for k, v in pt.items():
        res[k] = float(v)
        bv = np.array([bb[k] for bb in boots if k in bb and np.isfinite(bb[k])])
        bv = bv[np.abs(bv) < 20]
        if len(bv) >= 10:
            res[k + "_se"] = float(bv.std(ddof=1))
            res[k + "_lo"], res[k + "_hi"] = (float(x) for x in np.percentile(bv, [2.5, 97.5]))
    return res


def re_pool(est, se):
    """DerSimonian-Laird random-effects mean."""
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    if len(est) == 0:
        return {"mean": np.nan, "se": np.nan, "k": 0}
    w = 1 / se ** 2
    m = np.sum(w * est) / np.sum(w)
    Q = np.sum(w * (est - m) ** 2)
    tau2 = max(0.0, (Q - (len(est) - 1)) / (np.sum(w) - np.sum(w ** 2) / np.sum(w))) if len(est) > 1 else 0.0
    ws = 1 / (se ** 2 + tau2)
    mm = np.sum(ws * est) / np.sum(ws)
    s = np.sqrt(1 / np.sum(ws))
    return {"mean": float(mm), "se": float(s), "lo": float(mm - 1.96 * s), "hi": float(mm + 1.96 * s),
            "p": float(2 * stats.norm.sf(abs(mm) / s)), "k": int(len(est)), "tau2": float(tau2)}


# ============================================================================================ simulator
def simulate(world: str, rng, N: int = 12, D: int = 5, P_: int = 15, base_rate: float = 1 / 7200.0,
             h: float = 2.0, link_h: float = 0.5, n_events: int = 20) -> dict:
    """Point-process village at real counts. Worlds:
      work   S signals at random times on random projects (author = a random agent); other agents' arrival rate on
             the project x e^h for 60 min; the author posts a link after Exp(10 min) w.p. 0.7 (link adds x e^link_h)
      burst  latent attention pulses (same count) on random projects: all agents' arrival rate x e^h for 60 min;
             agents on the project emit S signals (rate 1/60 min) and links (1/30 min) while on it
      link   links at random times on random projects: arrival rate x e^h for 60 min after the link; agents on the
             project emit S signals (1/60 min)
      null   S signals and links at random times; baseline arrivals only
    Touches: an arrival opens a session (touches every 5-15 min for Exp(40 min)); routine commits during sessions
    (1/20 min). Days of 4 or 8 h; every agent active all day; all-present window = the day."""
    day_len = np.where(rng.random(D) < 0.5, 4 * 3600.0, 8 * 3600.0)
    starts = np.cumsum(np.r_[0, day_len[:-1] + 16 * 3600.0])
    touches, links, sigs = [], [], []
    for d in range(D):
        s0, L = starts[d], day_len[d]
        n_ev = rng.poisson(n_events / D)
        ev_t = np.sort(rng.uniform(s0 + 1800, s0 + L - 1800, n_ev))
        ev_p = rng.integers(0, P_, n_ev)
        ev_a = rng.integers(0, N, n_ev)
        boost = np.zeros((P_, int(L // 60) + 1))       # log-rate boost per project per minute
        if world == "work":
            for t, p, a in zip(ev_t, ev_p, ev_a):
                sigs.append((t, d, int(a), f"p{p}", "S"))
                m0 = int((t - s0) // 60)
                boost[p, m0:m0 + 60] += h
                if rng.random() < 0.7:
                    tl = t + rng.exponential(600)
                    if tl < s0 + L:
                        links.append((tl, d, int(a), f"p{p}", "agent", 0))
                        m1 = int((tl - s0) // 60)
                        boost[p, m1:m1 + 60] += link_h
        elif world in ("burst", "link"):
            for t, p, a in zip(ev_t, ev_p, ev_a):
                m0 = int((t - s0) // 60)
                boost[p, m0:m0 + 60] += h
                if world == "link":
                    links.append((t, d, int(a), f"p{p}", "agent", 0))
        elif world == "null":
            for t, p, a in zip(ev_t, ev_p, ev_a):
                sigs.append((t, d, int(a), f"p{p}", "S"))
            for t in rng.uniform(s0 + 1800, s0 + L - 1800, n_ev):
                links.append((t, d, int(rng.integers(0, N)), f"p{rng.integers(0, P_)}", "agent", 0))
        # arrivals: thinning per agent-project-minute
        for a in range(N):
            busy_until = {}
            for p in range(P_):
                rate = base_rate * 60 * np.exp(boost[p])           # per minute
                mins = np.flatnonzero(rng.random(len(rate)) < rate)
                for m in mins:
                    t = s0 + m * 60 + rng.uniform(0, 60)
                    if t < busy_until.get(p, -1):
                        continue
                    dur = rng.exponential(2400)
                    tt = t
                    while tt < min(t + dur, s0 + L):
                        touches.append((tt, d, a, f"p{p}", "action", 0))
                        if rng.random() < 0.5:
                            sigs.append((tt + 1, d, a, f"p{p}", "R"))
                        if world == "burst" and boost[p, int((tt - s0) // 60)] > 0:
                            if rng.random() < 10 / 60:
                                sigs.append((tt + 2, d, a, f"p{p}", "S"))
                            if rng.random() < 10 / 30:
                                links.append((tt + 3, d, a, f"p{p}", "agent", 0))
                        if world == "link" and rng.random() < 10 / 60:
                            sigs.append((tt + 2, d, a, f"p{p}", "S"))
                        tt += rng.uniform(300, 900)
                    busy_until[p] = tt + 3600
    T = pl.DataFrame(touches, schema=["t", "day", "agent", "project", "source", "room"], orient="row").with_columns(
        pl.col("day").cast(pl.Int16))
    Lk = (pl.DataFrame(links, schema=["t", "day", "agent", "project", "speaker_kind", "room"], orient="row")
          if links else pl.DataFrame(schema={"t": pl.Float64, "day": pl.Int64, "agent": pl.Int64, "project": pl.String,
                                             "speaker_kind": pl.String, "room": pl.Int64}))
    Lk = Lk.with_columns(pl.col("day").cast(pl.Int16))
    S = pl.DataFrame(sigs, schema=["t", "day", "agent", "project", "cls"], orient="row").with_columns(
        pl.col("day").cast(pl.Int16))
    days = pl.DataFrame({"day": np.arange(D).astype(np.int16), "win_start": starts, "win_end": starts + day_len,
                         "ap_lo": starts, "ap_hi": starts + day_len})
    spans = pl.DataFrame([(d, a, starts[d] - EDGE) for d in range(D) for a in range(N)],
                         schema=["day", "agent", "first_call"], orient="row").with_columns(pl.col("day").cast(pl.Int16))
    bins = pl.DataFrame([(d, b, a, 1, 0) for d in range(D) for b in range(int(day_len[d] // BIN)) for a in range(N)],
                        schema=["day", "bin", "agent", "n_calls", "room"], orient="row").with_columns(
        pl.col("day").cast(pl.Int16))
    kicks = pl.DataFrame({"t": [starts[0] - 7200.0], "day": [0], "kind": ["goal_kickoff"], "subkind": [None],
                          "room": [0], "targets": [[]]}, schema={"t": pl.Float64, "day": pl.Int16, "kind": pl.String,
                                                                 "subkind": pl.String, "room": pl.Int64,
                                                                 "targets": pl.List(pl.Int64)})
    return {"touches": T, "links": Lk, "signals": S, "bins": bins, "days": days, "spans": spans, "kicks": kicks}
