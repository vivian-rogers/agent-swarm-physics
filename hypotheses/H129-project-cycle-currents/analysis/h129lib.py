"""H129 library: project hops per agent (work host labels; attention labels), project age ranks, triple affinities
(A_3, the rotation-summed cycle affinity A_cyc), net age flux m_2, Hodge curl magnitude C_2, dwell hazards, the
per-agent time-reversal null, the detailed-balance null, and the sticky Potts walker on the real skeleton.

Codes only: repo/project names stay in memory; outputs are hashed by the scheme.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import sys  # noqa: E402
from functools import lru_cache  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import replicator_hosts as RH  # noqa: E402
from common import OUT as SHARED, holdout_mask  # noqa: E402

D = ROOT / "data/processed/H129-project-cycle-currents"
GOALS = [30, 31, 33, 35, 36, 37, 38, 39, 40, 41, 42, 44, 51]
OWN = {39, 42, 51}
CLASSES = ["omn", "nmo", "mno", "onm", "nom", "mon"]   # L1 fwd/rev, L2 fwd/rev, L3 fwd/rev
FLIP = {"omn": "nmo", "nmo": "omn", "mno": "onm", "onm": "mno", "nom": "mon", "mon": "nom"}


# ============================================================================================ ages
@lru_cache(maxsize=2)
def work_age(allow_holdout: bool = False) -> dict:
    """First non-holdout agent-work commit time per repo (epoch s), all periods (held-out rows only if allow_holdout,
    which only confirm.py sets)."""
    c = (pl.scan_parquet(SHARED / "work_commits.parquet")
         .filter(pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind").cast(pl.String) == "agent")
                 & ~pl.col("automated") & pl.col("author_agent").is_not_null() & (pl.col("author_agent") != RH.CLAUDE_CODE))
         .select(pl.col("repo").cast(pl.String), "t", "pt_date", "goal_no").collect())
    if not allow_holdout:
        c = c.filter(~pl.Series(holdout_mask(c["pt_date"].to_list(), c["goal_no"].to_list())))
    g = c.group_by("repo").agg(pl.col("t").min())
    return {r: t.timestamp() for r, t in g.iter_rows()}


@lru_cache(maxsize=2)
def attention_rows(allow_holdout: bool = False) -> pl.DataFrame:
    ps = (pl.scan_parquet(SHARED / "project_states.parquet")
          .filter((pl.col("w_min") == 30) & (pl.col("sources").cast(pl.String) == "all")
                  & (pl.lit(allow_holdout) | ~pl.col("holdout")))
          .select("goal_no", "pt_date", "win", "agent", pl.col("project").cast(pl.String)).collect())
    cal = RH.calendar().select("pt_date", "win_start")
    ps = ps.join(cal, on="pt_date", how="inner").with_columns(
        (pl.col("win_start") + pl.duration(minutes=30) * pl.col("win")).alias("t"))
    return ps.filter(pl.col("agent") != RH.CLAUDE_CODE)


@lru_cache(maxsize=2)
def attention_age(allow_holdout: bool = False) -> dict:
    a = attention_rows(allow_holdout).group_by("project").agg(pl.col("t").min())
    return {p: t.timestamp() for p, t in a.iter_rows()}


def rank_of(age: dict, names) -> dict:
    """Strict age rank (older = smaller) with ties broken by the hashed name."""
    keys = sorted(set(names), key=lambda r: (age.get(r, np.inf), RH.rhash(r)))
    return {r: i for i, r in enumerate(keys)}


# ============================================================================================ hops
def units_of(goal_no: int, allow_holdout: bool = False) -> dict:
    if goal_no == 51:
        um = RH.unit_of_day(51)
        days = set(RH.period_days(51, allow_holdout))
        return {d: u for d, u in um.items() if d in days}
    return {d: f"G{goal_no:02d}" for d in RH.period_days(goal_no, allow_holdout)}


def work_hops(goal_no: int, allow_holdout: bool = False) -> dict:
    """Host replay (shared code, non-holdout days unless allow_holdout) -> hops and visits per unit."""
    days = RH.period_days(goal_no, allow_holdout)
    calls = RH.load_calls(goal_no, days)
    commits = RH.load_commits(goal_no, days)
    leave = RH.leave_times(goal_no, calls, days)
    lab = RH.window_labels(commits, 30)
    ev = RH.classify_arrivals(RH.replay_events(lab, calls, E=100, leave_t=leave))
    um = units_of(goal_no, allow_holdout)
    ev = ev.with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("pt_date"))
    ev = ev.with_columns(pl.col("pt_date").replace_strict(um, default=None).alias("unit")).filter(pl.col("unit").is_not_null())
    calls = calls.with_columns(pl.col("pt_date").replace_strict(um, default=None).alias("unit"))
    hops, visits = [], []
    ct = {(u, int(a)): g["t_call"].dt.epoch("us").to_numpy() / 1e6 for (u, a), g in calls.group_by(["unit", "agent"])}
    for (u, a), g in ev.sort("t").group_by(["unit", "agent"], maintain_order=True):
        a = int(a)
        last_repo, vis = None, None
        prev_depart = None
        for kind, repo, to_repo, t in g.select("kind", "repo", "to_repo", "t").iter_rows():
            ts = t.timestamp()
            if kind in ("birth", "recruit"):
                if last_repo is not None and repo != last_repo:
                    hops.append((u, a, ts, last_repo, repo, prev_depart == (ts, last_repo)))
                vis = [u, a, repo, ts, None, None]
                last_repo = repo
            elif kind in ("depart", "expire", "leave"):
                if vis is not None and vis[2] == repo and vis[4] is None:
                    vis[4], vis[5] = ts, kind
                    visits.append(tuple(vis))
                    vis = None
                if kind == "depart":
                    prev_depart = (ts, repo)
        if vis is not None:
            visits.append(tuple(vis[:4]) + (None, "end"))
    H = pl.DataFrame(hops, schema={"unit": pl.String, "agent": pl.Int16, "t": pl.Float64, "src": pl.String,
                                   "dst": pl.String, "direct": pl.Boolean}, orient="row")
    V = pl.DataFrame(visits, schema={"unit": pl.String, "agent": pl.Int16, "repo": pl.String, "t_arr": pl.Float64,
                                     "t_end": pl.Float64, "end": pl.String}, orient="row")
    # dwell in own calls: calls in (t_arr, t_end] (or to the unit's last own call if open)
    dw = []
    for u, a, t0, t1 in V.select("unit", "agent", "t_arr", "t_end").iter_rows():
        tc = ct.get((u, int(a)), np.array([]))
        hi = tc[-1] if t1 is None and len(tc) else (t1 if t1 is not None else t0)
        dw.append(int(np.searchsorted(tc, hi, side="right") - np.searchsorted(tc, t0, side="right")))
    V = V.with_columns(pl.Series("dwell", dw, dtype=pl.Int32), (pl.col("end") == "depart").alias("event"))
    return {"hops": H, "visits": V, "events": ev}


def attention_hops(goal_no: int, allow_holdout: bool = False) -> dict:
    ps = attention_rows(allow_holdout).filter(pl.col("goal_no") == goal_no)
    um = units_of(goal_no, allow_holdout)
    ps = ps.with_columns(pl.col("pt_date").replace_strict(um, default=None).alias("unit")).filter(pl.col("unit").is_not_null())
    hops, visits = [], []
    for (u, a), g in ps.sort("t").group_by(["unit", "agent"], maintain_order=True):
        a = int(a)
        last, start, n = None, None, 0
        for p, t in g.select("project", "t").iter_rows():
            ts = t.timestamp()
            if p != last:
                if last is not None:
                    hops.append((u, a, ts, last, p, True))
                    visits.append((u, a, last, start, ts, "depart", n))
                last, start, n = p, ts, 0
            n += 1
        if last is not None:
            visits.append((u, a, last, start, None, "end", n))
    H = pl.DataFrame(hops, schema={"unit": pl.String, "agent": pl.Int16, "t": pl.Float64, "src": pl.String,
                                   "dst": pl.String, "direct": pl.Boolean}, orient="row")
    V = pl.DataFrame(visits, schema={"unit": pl.String, "agent": pl.Int16, "repo": pl.String, "t_arr": pl.Float64,
                                     "t_end": pl.Float64, "end": pl.String, "dwell": pl.Int32}, orient="row")
    V = V.with_columns((pl.col("end") == "depart").alias("event"))
    return {"hops": H, "visits": V}


# ============================================================================================ statistics
def seqs(hops: pl.DataFrame) -> list[list[str]]:
    """Per-agent ordered project sequences (consecutive distinct) reconstructed from hops."""
    out = []
    for _, g in hops.sort("t").group_by(["agent"], maintain_order=True):
        s = [g["src"][0]] + g["dst"].to_list()
        out.append(s)
    return out


def agent_counts(seq_list, rank: dict) -> np.ndarray:
    """Per agent: counts of the 6 triple classes, then up, down hops (8 columns)."""
    M = np.zeros((len(seq_list), 8), dtype=np.int64)
    ci = {c: i for i, c in enumerate(CLASSES)}
    for k, s in enumerate(seq_list):
        r = [rank[x] for x in s]
        for i in range(len(r) - 1):
            if r[i + 1] > r[i]:
                M[k, 6] += 1
            elif r[i + 1] < r[i]:
                M[k, 7] += 1
        for i in range(len(r) - 2):
            a, b, c = r[i], r[i + 1], r[i + 2]
            if a == c or a == b or b == c:
                continue
            o, m, n = sorted((a, b, c))
            lab = {o: "o", m: "m", n: "n"}
            M[k, ci[lab[a] + lab[b] + lab[c]]] += 1
    return M


def stats_from_counts(tot: np.ndarray) -> dict:
    n = dict(zip(CLASSES + ["up", "down"], tot.tolist()))
    L1 = np.log((n["omn"] + .5) / (n["nmo"] + .5))
    L2 = np.log((n["mno"] + .5) / (n["onm"] + .5))
    L3 = np.log((n["nom"] + .5) / (n["mon"] + .5))
    ud = n["up"] + n["down"]
    return {"A3": float(L1), "L2": float(L2), "L3": float(L3), "Acyc": float(L1 + L2 + L3),
            "m2": float((n["up"] - n["down"]) / ud) if ud else np.nan, "n_mono": n["omn"] + n["nmo"],
            "n_tri": int(sum(n[c] for c in CLASSES)), "n_hops": int(ud), "counts": n}


def flip_null(M: np.ndarray, n_draw=2000, rng=None) -> dict:
    """Per-agent whole-sequence reversal with prob 1/2: class c <-> FLIP[c], up <-> down."""
    rng = rng or np.random.default_rng(0)
    perm = [CLASSES.index(FLIP[c]) for c in CLASSES] + [7, 6]
    Mf = M[:, perm]
    F = rng.integers(0, 2, size=(n_draw, M.shape[0])).astype(bool)
    tot = (~F).astype(np.int64) @ M + F.astype(np.int64) @ Mf
    keys = ("A3", "Acyc", "m2")
    vals = {k: np.empty(n_draw) for k in keys}
    for i in range(n_draw):
        s = stats_from_counts(tot[i])
        for k in keys:
            vals[k][i] = s[k]
    return vals


def hodge(hops: pl.DataFrame) -> dict:
    """Net flow F_ab on the pooled hop graph; gradient (potential) part by least squares; curl magnitude C_2."""
    if hops.height == 0:
        return {"C2": np.nan, "kappa_c": np.nan, "n_edges": 0, "n_nodes": 0, "cycle_rank": 0}
    pairs = hops.group_by("src", "dst").agg(pl.len().alias("n"))
    nodes = sorted(set(pairs["src"].to_list()) | set(pairs["dst"].to_list()))
    idx = {p: i for i, p in enumerate(nodes)}
    E = {}
    for s, d, n in pairs.iter_rows():
        a, b = idx[s], idx[d]
        if a == b:
            continue
        key = (min(a, b), max(a, b))
        f, tot = E.get(key, (0, 0))
        E[key] = (f + (n if a < b else -n), tot + n)
    keys = sorted(E)
    F = np.array([E[k][0] for k in keys], dtype=float)
    T = np.array([E[k][1] for k in keys], dtype=int)
    B = np.zeros((len(keys), len(nodes)))
    for r, (a, b) in enumerate(keys):
        B[r, a], B[r, b] = -1.0, 1.0
    comps = n_components(len(nodes), keys)
    rank = len(keys) - len(nodes) + comps
    out = {"n_edges": len(keys), "n_nodes": len(nodes), "cycle_rank": int(rank), "B": B, "T": T, "F": F}
    out.update(curl(B, F))
    return out


def curl(B, F) -> dict:
    if len(F) == 0:
        return {"C2": np.nan, "kappa_c": np.nan}
    phi, *_ = np.linalg.lstsq(B, F, rcond=None)
    R = F - B @ phi
    c2 = float(R @ R)
    f2 = float(F @ F)
    return {"C2": c2, "kappa_c": c2 / f2 if f2 > 0 else np.nan}


def db_null(h: dict, n_draw=2000, rng=None) -> np.ndarray:
    rng = rng or np.random.default_rng(0)
    if h["n_edges"] == 0:
        return np.array([])
    P = np.linalg.pinv(h["B"])
    Proj = np.eye(len(h["F"])) - h["B"] @ P
    k = rng.binomial(h["T"][None, :], 0.5, size=(n_draw, len(h["T"])))
    Fn = 2 * k - h["T"][None, :]
    Rn = Fn @ Proj.T
    return np.einsum("ij,ij->i", Rn, Rn)


def n_components(n, edges):
    par = list(range(n))

    def f(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    for a, b in edges:
        par[f(a)] = f(b)
    return len({f(i) for i in range(n)})


def dwell_hazard(V: pl.DataFrame) -> dict:
    """Discrete-time logistic hazard of a hop by dwell d (own calls, or windows): logit h = a + g ln d.
    Person-period expansion on log-spaced bins (d is long); censoring respected."""
    v = V.filter(pl.col("dwell") >= 1)
    if v.height < 30 or v["event"].sum() < 15:
        return {"testable": False, "n": v.height, "n_event": int(v["event"].sum())}
    d = v["dwell"].to_numpy()
    ev = v["event"].to_numpy()
    edges = np.unique(np.round(np.geomspace(1, max(d.max(), 2) + 1, 16)).astype(int))
    rows_x, rows_y, rows_w = [], [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        at_risk = d >= lo
        if at_risk.sum() == 0:
            continue
        ended_in = at_risk & (d < hi)
        n_ev = int((ended_in & ev).sum())
        exposure = np.minimum(d[at_risk], hi) - lo   # calls at risk in the bin
        expo = float(np.maximum(exposure, 1).sum())
        mid = np.sqrt(lo * hi)
        rows_x.append(np.log(mid)); rows_y.append(n_ev); rows_w.append(expo)
    x = np.array(rows_x); y = np.array(rows_y); w = np.array(rows_w)
    # Poisson regression of events on exposure: log rate = a + g ln d (piecewise-constant hazard)
    try:
        g, se = poisson_slope(x, y, np.log(w))
    except Exception:
        return {"testable": False}
    comp = d[ev]
    cv = float(comp.std() / comp.mean()) if len(comp) > 1 and comp.mean() > 0 else np.nan
    return {"testable": True, "gamma": g, "gamma_se": se, "gamma_ci": [g - 1.96 * se, g + 1.96 * se], "n": int(v.height),
            "n_event": int(ev.sum()), "cv_completed": cv, "median_dwell": float(np.median(comp)) if len(comp) else np.nan}


def poisson_slope(x, y, off):
    """Poisson GLM log mu = a + g x + off by Newton-Raphson; returns (g, se(g)) from the observed information."""
    X = np.column_stack([np.ones_like(x), x])
    beta = np.array([np.log(max(y.sum(), 0.5) / np.exp(off).sum()), 0.0])
    for _ in range(100):
        mu = np.exp(X @ beta + off)
        Hm = X.T @ (X * mu[:, None])
        step = np.linalg.solve(Hm, X.T @ (y - mu))
        beta = beta + step
        if np.max(np.abs(step)) < 1e-10:
            break
    mu = np.exp(X @ beta + off)
    cov = np.linalg.inv(X.T @ (X * mu[:, None]))
    return float(beta[1]), float(np.sqrt(cov[1, 1]))


# ============================================================================================ walker
def skeleton(hops: pl.DataFrame, visits: pl.DataFrame) -> dict:
    """Real skeleton of one unit-channel: per agent the initial project and the ordered real hop times; project
    availability windows [first arrival, last end] in the unit (projects held at the unit start are available from it)."""
    first = visits.group_by("repo").agg(pl.col("t_arr").min().alias("a0"))
    tmax = max(visits["t_arr"].max(), visits["t_end"].drop_nulls().max() or 0)
    last = visits.with_columns(pl.col("t_end").fill_null(tmax)).group_by("repo").agg(pl.col("t_end").max().alias("a1"))
    av = first.join(last, on="repo")
    agents = {}
    for (a,), g in hops.sort("t").group_by(["agent"], maintain_order=True):
        agents[int(a)] = {"init": g["src"][0], "t": g["t"].to_numpy()}
    return {"agents": agents, "avail": av, "names": av["repo"].to_list()}


def walk(sk: dict, rank: dict, lam: float, b: float, rng, kappa: float = 0.0, all_avail: bool = False,
         sigma_a: float = 1.0) -> list[list[str]]:
    """One sticky-walker realization on the skeleton: at each real hop, pick j != current among available projects
    with weight exp(alpha_j + b [held] + lam z_j(t) + kappa [j = age successor of current])."""
    names = sk["names"]
    a0 = sk["avail"]["a0"].to_numpy()
    a1 = sk["avail"]["a1"].to_numpy()
    if all_avail:
        a0 = np.full_like(a0, -np.inf); a1 = np.full_like(a1, np.inf)
    rk = np.array([rank[n] for n in names], dtype=float)
    alpha = rng.normal(0, sigma_a, len(names))
    pos = {n: i for i, n in enumerate(names)}
    # merge all agents' hops in time order (availability is time-dependent only)
    ev = sorted((t, a) for a, d in sk["agents"].items() for t in d["t"])
    cur = {a: pos[d["init"]] for a, d in sk["agents"].items()}
    held = {a: {cur[a]} for a in cur}
    seq = {a: [names[cur[a]]] for a in cur}
    for t, a in ev:
        av = np.where((a0 <= t) & (a1 >= t))[0]
        av = av[av != cur[a]]
        if len(av) == 0:
            continue
        r = rk[av]
        z = (r - r.mean()) / (r.std() if r.std() > 0 else 1.0)
        u = alpha[av] + lam * z + b * np.array([j in held[a] for j in av], dtype=float)
        if kappa:
            rc = rk[cur[a]]
            newer = av[r > rc]
            succ = newer[np.argmin(rk[newer])] if len(newer) else av[np.argmin(r)]
            u = u + kappa * (av == succ)
        p = np.exp(u - u.max()); p /= p.sum()
        j = av[rng.choice(len(av), p=p)]
        cur[a] = j
        held[a].add(j)
        seq[a].append(names[j])
    return list(seq.values())


def walk_stats(sk, rank, lam, b, rng, **kw) -> dict:
    s = walk(sk, rank, lam, b, rng, **kw)
    M = agent_counts(s, rank)
    st = stats_from_counts(M.sum(0))
    st["return_share"] = return_share(s)
    return st


def return_share(seq_list) -> float:
    n = r = 0
    for s in seq_list:
        seen = {s[0]}
        for x in s[1:]:
            n += 1
            r += x in seen
            seen.add(x)
    return r / n if n else np.nan


LAM_GRID = [-1.0, 0.0, 0.75, 1.5, 2.5, 4.0]
B_GRID = [0.0, 1.0, 2.0, 3.0, 4.5, 6.0]


def calibrate(sk, rank, m2_obs, ret_obs, rng, n_per=10):
    """Grid search (lam, b) matching the observed net age flux m_2 and return share (standardized distance)."""
    best = None
    tab = []
    for lam in LAM_GRID:
        for b in B_GRID:
            m2s, rts = [], []
            for _ in range(n_per):
                st = walk_stats(sk, rank, lam, b, rng)
                m2s.append(st["m2"]); rts.append(st["return_share"])
            m2m, rtm = np.nanmean(m2s), np.nanmean(rts)
            sd_m = max(np.nanstd(m2s), 0.02); sd_r = max(np.nanstd(rts), 0.02)
            dist = ((m2m - m2_obs) / sd_m) ** 2 + ((rtm - ret_obs) / sd_r) ** 2
            tab.append((lam, b, m2m, rtm, dist))
            if best is None or dist < best[4]:
                best = (lam, b, m2m, rtm, dist)
    return {"lam": best[0], "b": best[1], "m2_fit": best[2], "ret_fit": best[3], "dist": best[4]}


def reference(sk, rank, lam, b, rng, n=400, **kw) -> dict:
    vals = {k: [] for k in ("A3", "Acyc", "m2", "C2")}
    for _ in range(n):
        s = walk(sk, rank, lam, b, rng, **kw)
        M = agent_counts(s, rank)
        st = stats_from_counts(M.sum(0))
        for k in ("A3", "Acyc", "m2"):
            vals[k].append(st[k])
        vals["C2"].append(hodge(seq_to_hops(s))["C2"])
    return {k: np.array(v, dtype=float) for k, v in vals.items()}


def seq_to_hops(seq_list) -> pl.DataFrame:
    rows = []
    for k, s in enumerate(seq_list):
        for i in range(len(s) - 1):
            rows.append((k, float(i), s[i], s[i + 1]))
    return pl.DataFrame(rows, schema={"agent": pl.Int16, "t": pl.Float64, "src": pl.String, "dst": pl.String}, orient="row")
