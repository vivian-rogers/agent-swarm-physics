"""H137 library: unit skeletons (calls, named reads, in-flight named messages, naming weights), follow hops from
per-call project labels, naming classes, and the statistics O1-O5. Shared by synthetic.py (simulated labels) and
run.py (real labels from infra/shared/project_calls.py).

Definitions (card, Data scheme):
  - call clock: DQ1 call_windows rows of non-Claude-Code agents on non-reserved days of the unit.
  - j's current project at i's call c: the label of j's latest call c' with t_call(c') < t_call(c) and
    t_first(c') <= t_call(c) (j has touched it by then). j is present if that call's t_first is within PRESENT_S of
    t_call(c) and on the same PT day.
  - follow hop: a hop of i at call c onto project b held by >= 1 other present agent j; weight 1/n_b(c) per j.
  - R_named[c, j]: messages by j naming i (ledger ment flag, kind agent, not omitted) received in i's last 10 calls
    (c included). R_all[c, j]: all agent messages by j received in the same calls.
  - in-flight named message at c: message by j naming i (chat_mentions_clean.mentions_roster) posted in
    (t_call(c), t_call(c) + d_c], d_c = clip(t_first - t_call, 1, 120) s (H67's matched-lag rule).
  - naming weights w[j, i]: agent messages by j whose mentions_roster contains i, per unit (H90's rule).
  - naming class per unordered pair: one-way (max >= 3, min <= max/3), mutual (both >= 3, within a factor 3),
    none (both 0), weak (else; left out of the class contrasts).
No message text is read.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
D = ROOT / "data/processed/H137-nonreciprocal-potts-named-pairs"
PRESENT_S = 3600.0
READ_WIN = 10
CLASSES = ("one", "mutual", "none", "weak")


# ============================================================================================ skeleton
def units_table() -> pl.DataFrame:
    pu = pl.read_parquet(SH / "period_units.parquet")
    return pu.filter(~pl.col("holdout"))


def claude_code_agents() -> set:
    r = pl.read_parquet(SH / "roster.parquet", columns=["agent", "claude_code"])
    return set(r.filter(pl.col("claude_code"))["agent"].to_list())


def lab_of() -> dict:
    r = pl.read_parquet(SH / "roster.parquet", columns=["agent", "lab"])
    return dict(r.iter_rows())


def unit_days(unit_id: str) -> tuple[int, list]:
    pu = units_table().filter(pl.col("unit_id") == unit_id)
    if pu.height != 1:
        raise KeyError(f"unit {unit_id} not found among non-reserved units")
    g = int(pu["goal_no"][0])
    days = sorted(pu["days"][0])
    mask = holdout_mask(days, [g] * len(days))
    days = [d for d, m in zip(days, mask) if not m]
    return g, days


def load_skeleton(unit_id: str) -> dict:
    """Calls, read counts, in-flight named counts and naming weights of one unit. Reserved rows are masked."""
    g, days = unit_days(unit_id)
    cc_ag = claude_code_agents()
    cw = (pl.scan_parquet(SH / "call_windows.parquet")
          .filter(pl.col("pt_date").is_in(days) & (pl.col("goal_no") == g) & ~pl.col("holdout"))
          .select("turn_id", "agent", "pt_date", "goal_no", "t_call", "t_first", "t_end", "kind")
          .collect())
    cw = cw.filter(~pl.col("agent").is_in(list(cc_ag)))
    m = holdout_mask(cw["pt_date"].to_list(), cw["goal_no"].to_list())
    cw = cw.filter(~pl.Series(m))
    cw = cw.filter(pl.col("t_call").is_not_null()).sort("t_call", "agent", "turn_id")
    agents = sorted(set(cw["agent"].to_list()))
    aidx = {a: k for k, a in enumerate(agents)}
    n, A = cw.height, len(agents)
    tc = cw["t_call"].dt.epoch("us").to_numpy() / 1e6
    tf = cw["t_first"].dt.epoch("us").to_numpy().astype(float) / 1e6
    tf = np.where(np.isfinite(tf), tf, tc)
    tf = np.maximum(tf, tc)
    ag = np.array([aidx[a] for a in cw["agent"].to_list()], dtype=np.int16)
    dayk = {d: k for k, d in enumerate(days)}
    day = np.array([dayk[d] for d in cw["pt_date"].to_list()], dtype=np.int16)
    turn = cw["turn_id"].to_numpy()
    cidx = {int(t): k for k, t in enumerate(turn)}

    # ---- reads received at each call (ledger), agent senders only
    li = (pl.scan_parquet(SH / "context_ledger_items.parquet")
          .filter(pl.col("turn_id").is_in(turn.tolist()) & (pl.col("kind") == "agent") & ~pl.col("omitted"))
          .select("turn_id", "sender", "ment").collect())
    li = li.filter(pl.col("sender").is_in(agents))
    rd = li.group_by("turn_id", "sender").agg(pl.len().alias("n_all"), pl.col("ment").sum().alias("n_nam"))
    r_nam1 = np.zeros((n, A), dtype=np.float32)
    r_all1 = np.zeros((n, A), dtype=np.float32)
    for t, s, na, nn in rd.select("turn_id", "sender", "n_all", "n_nam").iter_rows():
        c = cidx[int(t)]
        r_nam1[c, aidx[s]] += nn
        r_all1[c, aidx[s]] += na
    # rolling sum over the reader's last READ_WIN calls (c included)
    R_nam = np.zeros_like(r_nam1)
    R_all = np.zeros_like(r_all1)
    by_agent = [np.flatnonzero(ag == k) for k in range(A)]
    for k in range(A):
        ix = by_agent[k]
        if not ix.size:
            continue
        for M1, M in ((r_nam1, R_nam), (r_all1, R_all)):
            cs = np.cumsum(M1[ix], axis=0)
            lag = np.vstack([np.zeros((READ_WIN, A), dtype=np.float32), cs])[: len(ix)]
            M[ix] = cs - lag
    for k in range(A):  # own messages are never couplings
        R_nam[:, k][ag == k] = 0
        R_all[:, k][ag == k] = 0

    # ---- naming weights and in-flight named messages
    cc = (pl.scan_parquet(SH / "chat_core.parquet")
          .filter(pl.col("pt_date").is_in(days) & (pl.col("goal_no") == g) & (pl.col("speaker_kind") == "agent"))
          .select("message_id", "t", "pt_date", "goal_no", "agent").collect())
    mk = holdout_mask(cc["pt_date"].to_list(), cc["goal_no"].to_list())
    cc = cc.filter(~pl.Series(mk)).filter(pl.col("agent").is_in(agents))
    mc = pl.read_parquet(SH / "chat_mentions_clean.parquet", columns=["message_id", "mentions_roster"])
    nm = (cc.join(mc, on="message_id", how="inner").explode("mentions_roster").drop_nulls("mentions_roster")
          .filter(pl.col("mentions_roster").is_in(agents) & (pl.col("mentions_roster") != pl.col("agent"))))
    W = np.zeros((A, A), dtype=np.float64)  # W[j, i] = messages by j naming i
    for j, i, c in nm.group_by("agent", "mentions_roster").len().iter_rows():
        W[aidx[j], aidx[i]] = c
    # in-flight: for each named message j -> i at t, i's latest call with t_call < t; in flight if t <= t_call + d_c
    d_c = np.clip(tf - tc, 1.0, 120.0)
    IF = np.zeros((n, A), dtype=np.float32)
    nt = nm.with_columns((pl.col("t").dt.epoch("us") / 1e6).alias("ts")).select("agent", "mentions_roster", "ts")
    for j, i, ts in nt.iter_rows():
        ix = by_agent[aidx[i]]
        p = np.searchsorted(tc[ix], ts, side="left") - 1
        if p < 0:
            continue
        c = ix[p]
        if ts <= tc[c] + d_c[c]:
            IF[c, aidx[j]] += 1
    # ---- presence / current-call index: for each call c and agent j, j's latest call c' with t_call(c') < t_call(c)
    # and t_first(c') <= t_call(c); -1 if none. present if t_call(c) - t_first(c') <= PRESENT_S and same day.
    last = np.full((n, A), -1, dtype=np.int32)
    for k in range(A):
        ix = by_agent[k]
        if not ix.size:
            continue
        # t_first is non-decreasing within an agent in practice; use running max to be safe
        tfk = np.maximum.accumulate(tf[ix])
        p = np.searchsorted(tfk, tc, side="right") - 1
        ok = p >= 0
        cand = np.where(ok, ix[np.clip(p, 0, None)], -1)
        # strictly earlier t_call
        bad = ok & (tc[np.clip(cand, 0, None)] >= tc)
        while bad.any():
            p = np.where(bad, p - 1, p)
            ok = p >= 0
            cand = np.where(ok, ix[np.clip(p, 0, None)], -1)
            bad = ok & (tc[np.clip(cand, 0, None)] >= tc)
        last[:, k] = cand
    present = (last >= 0)
    lc = np.clip(last, 0, None)
    present &= (tc[:, None] - tf[lc] <= PRESENT_S) & (day[lc] == day[:, None])
    present[np.arange(n), ag] = False
    prev = np.full(n, -1, dtype=np.int32)  # previous call of the same agent
    for k in range(A):
        ix = by_agent[k]
        prev[ix[1:]] = ix[:-1]
    return {"unit": unit_id, "goal_no": g, "days": days, "agents": agents, "aidx": aidx, "n": n, "A": A,
            "tc": tc, "tf": tf, "ag": ag, "day": day, "turn": turn, "prev": prev, "by_agent": by_agent,
            "R_nam": R_nam, "R_all": R_all, "r_nam1": r_nam1, "IF": IF, "W": W, "last": last, "present": present}


# ============================================================================================ classes
def naming_classes(W: np.ndarray) -> dict:
    """{(a, b) a<b: (class, namer or -1)} over all agent pairs of the unit."""
    A = W.shape[0]
    out = {}
    for a in range(A):
        for b in range(a + 1, A):
            wab, wba = W[a, b], W[b, a]  # wab = a names b
            mx, mn = max(wab, wba), min(wab, wba)
            if mx == 0:
                out[(a, b)] = ("none", -1)
            elif mx >= 3 and mn <= mx / 3:
                out[(a, b)] = ("one", a if wab > wba else b)
            elif mn >= 3:
                out[(a, b)] = ("mutual", -1)
            else:
                out[(a, b)] = ("weak", -1)
    return out


# ============================================================================================ follow hops
def follow_hops(S: dict, cur: np.ndarray, label: np.ndarray, hop: np.ndarray) -> pl.DataFrame:
    """Rows (hopper, target, call, weight) for every follow hop. cur[c] = hopper's project before call c,
    label[c] = project after call c (carried), hop[c] = True if c is a project hop. Projects are ints, -1 = none."""
    rows_h, rows_t, rows_c, rows_w = [], [], [], []
    last, present = S["last"], S["present"]
    for c in np.flatnonzero(hop):
        b = label[c]
        if b < 0:
            continue
        lj = last[c]
        js = np.flatnonzero(present[c])
        if not js.size:
            continue
        held = label[lj[js]]
        on = js[held == b]
        if not on.size:
            continue
        w = 1.0 / on.size
        for j in on:
            rows_h.append(S["ag"][c]); rows_t.append(j); rows_c.append(c); rows_w.append(w)
    return pl.DataFrame({"hopper": np.array(rows_h, dtype=np.int16), "target": np.array(rows_t, dtype=np.int16),
                         "call": np.array(rows_c, dtype=np.int32), "w": np.array(rows_w, dtype=np.float64)})


def pair_table(S: dict, fh: pl.DataFrame, classes: dict | None = None) -> dict:
    """Per unordered pair: class, namer, F[a<-b], F[b<-a], leave-pair-out popularity and in-degree terms."""
    A = S["A"]
    classes = classes or naming_classes(S["W"])
    F = np.zeros((A, A))  # F[i, j] = weighted follow hops of i onto j's project (i <- j)
    Nf = np.zeros((A, A))
    if fh.height:
        np.add.at(F, (fh["hopper"].to_numpy(), fh["target"].to_numpy()), fh["w"].to_numpy())
        np.add.at(Nf, (fh["hopper"].to_numpy(), fh["target"].to_numpy()), 1)
    inF = F.sum(axis=0)  # follow hops onto j's projects by anyone
    outF = F.sum(axis=1)  # follow hops by i onto anyone's projects (hopper propensity)
    W = S["W"]
    indeg = W.sum(axis=0)
    pairs = []
    for (a, b), (cl, namer) in classes.items():
        pop_a = inF[a] - F[b, a]
        pop_b = inF[b] - F[a, b]
        ind_a = indeg[a] - W[b, a]
        ind_b = indeg[b] - W[a, b]
        act_a = outF[a] - F[a, b]
        act_b = outF[b] - F[b, a]
        pairs.append((a, b, cl, namer, F[a, b], F[b, a], Nf[a, b] + Nf[b, a], pop_a, pop_b, ind_a, ind_b, act_a, act_b))
    P = pl.DataFrame(pairs, schema={"a": pl.Int16, "b": pl.Int16, "cls": pl.String, "namer": pl.Int16,
                                    "F_ab": pl.Float64, "F_ba": pl.Float64, "n_follow": pl.Float64,
                                    "pop_a": pl.Float64, "pop_b": pl.Float64, "ind_a": pl.Float64,
                                    "ind_b": pl.Float64, "act_a": pl.Float64, "act_b": pl.Float64}, orient="row")
    return {"pairs": P, "F": F}


def hop_rows(S: dict, fh: pl.DataFrame, P: pl.DataFrame) -> pl.DataFrame:
    """O2 design rows: one per follow hop between members of a classified pair (one, mutual, none), oriented a<b.
    y = 1 if the hop is 'a joins b'. z = +1 if b names a one-way, -1 if a names b one-way, else 0."""
    if not fh.height:
        return pl.DataFrame(schema={"a": pl.Int16, "b": pl.Int16, "y": pl.Float64, "w": pl.Float64, "z": pl.Float64,
                                    "dpop": pl.Float64, "dind": pl.Float64, "dact": pl.Float64})
    h = fh.with_columns(pl.min_horizontal("hopper", "target").alias("a"), pl.max_horizontal("hopper", "target").alias("b"))
    h = h.with_columns((pl.col("hopper") == pl.col("a")).cast(pl.Float64).alias("y"))
    h = h.join(P.filter(pl.col("cls") != "weak"), on=["a", "b"], how="inner")
    h = h.with_columns(
        pl.when(pl.col("cls") != "one").then(0.0).when(pl.col("namer") == pl.col("b")).then(1.0).otherwise(-1.0).alias("z"),
        ((pl.col("pop_b") + 1).log() - (pl.col("pop_a") + 1).log()).alias("dpop"),
        ((pl.col("ind_b") + 1).log() - (pl.col("ind_a") + 1).log()).alias("dind"),
        ((pl.col("act_a") + 1).log() - (pl.col("act_b") + 1).log()).alias("dact"))
    return h.select("a", "b", "y", "w", "z", "dpop", "dind", "dact")


# ============================================================================================ estimators
def wlogit(X: np.ndarray, y: np.ndarray, w: np.ndarray, lam: float = 0.01, it: int = 25, beta0=None) -> np.ndarray:
    """Weighted logistic regression, no intercept (antisymmetric design), small ridge for separated samples.
    beta0: warm start (bootstrap and permutation refits)."""
    beta = np.zeros(X.shape[1]) if beta0 is None else np.array(beta0, dtype=float)
    for _ in range(it):
        eta = np.clip(X @ beta, -30, 30)
        p = 1 / (1 + np.exp(-eta))
        g = X.T @ (w * (y - p)) - lam * beta
        H = (X * (w * p * (1 - p))[:, None]).T @ X + lam * np.eye(X.shape[1])
        try:
            step = np.linalg.solve(H, g)
        except np.linalg.LinAlgError:
            break
        beta += step
        if np.max(np.abs(step)) < 1e-7:
            break
    return beta


COLS = {True: ["z", "dpop", "dind"], False: ["z"], "act": ["z", "dpop", "dind", "dact"]}


def theta_fit(R: pl.DataFrame, controls=True) -> float:
    if R.height < 3 or not np.any(R["z"].to_numpy() != 0):
        return np.nan
    cols = COLS[controls]
    X = R.select(cols).to_numpy()
    return float(wlogit(X, R["y"].to_numpy(), R["w"].to_numpy())[0])


def pair_ids(R: pl.DataFrame) -> np.ndarray:
    cols = [c for c in ("unit", "a", "b") if c in R.columns]
    key = R.select(cols).with_columns(pl.concat_str([pl.col(c).cast(pl.String) for c in cols], separator="|").alias("k"))["k"]
    return key.cast(pl.Categorical).to_physical().to_numpy()


def theta_boot(R: pl.DataFrame, rng, B: int = 200, controls=True) -> tuple:
    """Pair-cluster bootstrap (pairs resampled within unit when a unit column is present)."""
    if R.height < 3:
        return (np.nan, np.nan)
    pid = pair_ids(R)
    up = np.unique(pid)
    rows_of = [np.flatnonzero(pid == p) for p in up]
    unit_of = None
    if "unit" in R.columns:
        uu = R["unit"].to_numpy()
        unit_of = np.array([uu[r[0]] for r in rows_of])
    cols = COLS[controls]
    X, y, w = R.select(cols).to_numpy(), R["y"].to_numpy(), R["w"].to_numpy()
    b0 = wlogit(X, y, w)
    est = []
    for _ in range(B):
        if unit_of is None:
            pick = rng.integers(0, len(up), len(up))
        else:
            pick = np.concatenate([rng.choice(np.flatnonzero(unit_of == u), size=(unit_of == u).sum())
                                   for u in np.unique(unit_of)])
        ix = np.concatenate([rows_of[p] for p in pick])
        if not np.any(X[ix, 0] != 0):
            continue
        est.append(wlogit(X[ix], y[ix], w[ix], beta0=b0)[0])
    if len(est) < B // 2:
        return (np.nan, np.nan)
    return tuple(np.percentile(est, [2.5, 97.5]))


def theta_n2(R: pl.DataFrame, rng, draws: int = 1000, controls=True) -> float:
    """N2: permute the pair naming code z across pairs inside quintiles of |dpop| (within unit). One-sided p."""
    th0 = theta_fit(R, controls)
    if not np.isfinite(th0):
        return np.nan
    pid = pair_ids(R)
    up, first = np.unique(pid, return_index=True)
    z_p = R["z"].to_numpy()[first]
    adp = np.abs(R["dpop"].to_numpy()[first])
    unit_p = R["unit"].to_numpy()[first] if "unit" in R.columns else np.zeros(len(up))
    strata = np.zeros(len(up), dtype=np.int64)
    for k, u in enumerate(np.unique(unit_p)):
        m = np.flatnonzero(unit_p == u)
        if m.size >= 10:
            q = np.quantile(adp[m], [0.2, 0.4, 0.6, 0.8])
            strata[m] = k * 10 + np.searchsorted(q, adp[m], side="right")
        else:
            strata[m] = k * 10
    inv = np.searchsorted(up, pid)
    X = R.select(COLS[controls]).to_numpy().copy()
    y, w = R["y"].to_numpy(), R["w"].to_numpy()
    b0 = wlogit(X, y, w)
    groups = [np.flatnonzero(strata == s) for s in np.unique(strata)]
    ge = 0
    for _ in range(draws):
        zp = z_p.copy()
        for g_ in groups:
            zp[g_] = z_p[rng.permutation(g_)]
        X[:, 0] = zp[inv]
        if not np.any(X[:, 0] != 0):
            ge += 1
            continue
        if wlogit(X, y, w, beta0=b0)[0] >= th0:
            ge += 1
    return (ge + 1) / (draws + 1)


def sigma_pairs(P: pl.DataFrame) -> pl.DataFrame:
    """O1 and O3 per pair with >= 1 follow hop. A oriented named <- namer for one-way pairs."""
    Q = P.filter((pl.col("F_ab") + pl.col("F_ba")) > 0)
    Q = Q.with_columns(((pl.col("F_ab") - pl.col("F_ba")) *
                        ((pl.col("F_ab") + 0.5) / (pl.col("F_ba") + 0.5)).log()).alias("sigma"))
    # F_named<-namer: if namer == b, named = a: F_ab (a <- b); else F_ba
    Q = Q.with_columns(pl.when(pl.col("cls") != "one").then(None)
                       .when(pl.col("namer") == pl.col("b"))
                       .then(((pl.col("F_ab") + 0.5) / (pl.col("F_ba") + 0.5)).log())
                       .otherwise(((pl.col("F_ba") + 0.5) / (pl.col("F_ab") + 0.5)).log()).alias("A"))
    return Q


def flip_null(Q: pl.DataFrame, rng, draws: int = 2000, fh_rows: dict | None = None) -> dict:
    """N1 direction flip. Each pair's follow-hop rows are reassigned i<-j or j<-i with probability 1/2 (weights kept).
    fh_rows: {(unit, a, b): array of row weights}. Returns null draws of mean A (one-way) and class mean sigma."""
    keys = list(zip(*(Q[c].to_list() for c in (["unit", "a", "b"] if "unit" in Q.columns else ["a", "b"]))))
    cls = Q["cls"].to_numpy()
    namer_is_b = (Q["namer"].to_numpy() == Q["b"].to_numpy())
    wl = [fh_rows[k] for k in keys]
    out = {"A_one": np.empty(draws), **{f"sig_{c}": np.empty(draws) for c in CLASSES}}
    m_one = cls == "one"
    for d in range(draws):
        Fab = np.array([np.sum(wv[rng.random(wv.size) < 0.5]) for wv in wl])
        tot = np.array([wv.sum() for wv in wl])
        Fba = tot - Fab
        sig = (Fab - Fba) * np.log((Fab + 0.5) / (Fba + 0.5))
        Aab = np.log((Fab + 0.5) / (Fba + 0.5))
        Av = np.where(namer_is_b, Aab, -Aab)
        out["A_one"][d] = Av[m_one].mean() if m_one.any() else np.nan
        for c in CLASSES:
            mm = cls == c
            out[f"sig_{c}"][d] = sig[mm].mean() if mm.any() else np.nan
    return out


def fh_row_weights(fh: pl.DataFrame, unit: str | None = None) -> dict:
    d = {}
    if not fh.height:
        return d
    h = fh.with_columns(pl.min_horizontal("hopper", "target").alias("a"), pl.max_horizontal("hopper", "target").alias("b"))
    for (a, b), g in h.group_by(["a", "b"]):
        d[(unit, a, b) if unit is not None else (a, b)] = g["w"].to_numpy()
    return d


def pair_boot_contrast(Q: pl.DataFrame, rng, B: int = 1000) -> tuple:
    """sigma_one - sigma_none with a pair bootstrap (within unit). Returns (est, lo, hi)."""
    s = Q["sigma"].to_numpy()
    cls = Q["cls"].to_numpy()
    unit = Q["unit"].to_numpy() if "unit" in Q.columns else np.zeros(Q.height)
    one, non = (cls == "one"), (cls == "none")
    if not one.any() or not non.any():
        return (np.nan, np.nan, np.nan)
    est = s[one].mean() - s[non].mean()
    bs = []
    idx_u = {u: np.flatnonzero(unit == u) for u in np.unique(unit)}
    for _ in range(B):
        ix = np.concatenate([rng.choice(v, v.size) for v in idx_u.values()])
        o, n_ = ix[one[ix]], ix[non[ix]]
        if o.size and n_.size:
            bs.append(s[o].mean() - s[n_].mean())
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return (est, lo, hi)


def mean_boot(v: np.ndarray, unit: np.ndarray, rng, B: int = 1000) -> tuple:
    v = np.asarray(v, float)
    if not v.size:
        return (np.nan, np.nan, np.nan)
    idx_u = {u: np.flatnonzero(unit == u) for u in np.unique(unit)}
    bs = [v[np.concatenate([rng.choice(x, x.size) for x in idx_u.values()])].mean() for _ in range(B)]
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return (v.mean(), lo, hi)


# ============================================================================================ O4
def readout_rows(S: dict, cur: np.ndarray, label: np.ndarray, hop: np.ndarray) -> pl.DataFrame:
    """O4 rows: (call c of i, sender j) with j present on a project != i's current, and a named read from j received
    at c (read=1) or an in-flight named message from j at c and no named read from j at c (read=0).
    y = i hops at c onto j's current project."""
    r1, IF, last, present, ag = S["r_nam1"], S["IF"], S["last"], S["present"], S["ag"]
    cs, js = np.nonzero((r1 > 0) | (IF > 0))
    keep = present[cs, js]
    cs, js = cs[keep], js[keep]
    lj = last[cs, js]
    bj = label[lj]
    ok = (bj >= 0) & (bj != cur[cs]) & (cur[cs] >= 0)  # an unlabelled agent cannot hop (H133's hop rule)
    cs, js, bj = cs[ok], js[ok], bj[ok]
    rd = (r1[cs, js] > 0).astype(np.int8)
    y = (hop[cs] & (label[cs] == bj)).astype(np.int8)
    return pl.DataFrame({"call": cs.astype(np.int32), "j": js.astype(np.int16), "i": ag[cs].astype(np.int16),
                         "day": S["day"][cs], "read": rd, "y": y})


def readout_contrast(O: pl.DataFrame, rng, B: int = 1000) -> tuple:
    """Rate after a read named message minus rate after an in-flight named message; agent-day cluster bootstrap."""
    if not O.height or O["read"].sum() == 0 or (O["read"] == 0).sum() == 0:
        return (np.nan, np.nan, np.nan, 0, 0)
    keycols = [c for c in ("unit", "i", "day") if c in O.columns]
    k = O.select(pl.concat_str([pl.col(c).cast(pl.String) for c in keycols], separator="|").alias("k"))["k"]
    kid = k.cast(pl.Categorical).to_physical().to_numpy()
    rd, y = O["read"].to_numpy(), O["y"].to_numpy().astype(float)
    nk = kid.max() + 1
    s1 = np.bincount(kid, weights=y * rd, minlength=nk); n1 = np.bincount(kid, weights=rd, minlength=nk)
    s0 = np.bincount(kid, weights=y * (1 - rd), minlength=nk); n0 = np.bincount(kid, weights=1 - rd, minlength=nk)
    est = s1.sum() / n1.sum() - s0.sum() / n0.sum()
    bs = []
    for _ in range(B):
        p = rng.integers(0, nk, nk)
        a1, b1, a0, b0 = s1[p].sum(), n1[p].sum(), s0[p].sum(), n0[p].sum()
        if b1 > 0 and b0 > 0:
            bs.append(a1 / b1 - a0 / b0)
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return (est, lo, hi, int(n1.sum()), int(n0.sum()))


def adj_null(R: pl.DataFrame, Q: pl.DataFrame, rng, draws: int = 500) -> dict:
    """N1b (candidate amendment; propensity-adjusted direction null). Each follow-hop row of a classified pair gets its
    direction from the control-only logit (dpop, dind, dact; no naming term), weights kept. Returns null draws of the
    class mean sigma, the one-way mean A and the contrast sigma_one - sigma_none, over the pairs in Q."""
    out = {"A_one": np.full(draws, np.nan), "contrast": np.full(draws, np.nan),
           **{f"sig_{c}": np.full(draws, np.nan) for c in CLASSES}}
    if R.height < 3:
        return out
    X = R.select("dpop", "dind", "dact").to_numpy()
    b = wlogit(X, R["y"].to_numpy(), R["w"].to_numpy())
    p = 1 / (1 + np.exp(-np.clip(X @ b, -30, 30)))
    keycols = [c for c in ("unit", "a", "b") if c in R.columns]
    kr = R.select(pl.concat_str([pl.col(c).cast(pl.String) for c in keycols], separator="|").alias("k"))["k"].to_list()
    Qc = Q.filter(pl.col("cls") != "weak")
    kq = Qc.select(pl.concat_str([pl.col(c).cast(pl.String) for c in keycols], separator="|").alias("k"))["k"].to_list()
    qi = {k: n for n, k in enumerate(kq)}
    row_q = np.array([qi.get(k, -1) for k in kr])
    ok = row_q >= 0
    row_q, w, p = row_q[ok], R["w"].to_numpy()[ok], p[ok]
    cls = Qc["cls"].to_numpy()
    namer_is_b = (Qc["namer"].to_numpy() == Qc["b"].to_numpy())
    nq = Qc.height
    tot = np.bincount(row_q, weights=w, minlength=nq)
    for d in range(draws):
        y = rng.random(p.size) < p
        Fab = np.bincount(row_q, weights=w * y, minlength=nq)
        Fba = tot - Fab
        sig = (Fab - Fba) * np.log((Fab + 0.5) / (Fba + 0.5))
        Aab = np.log((Fab + 0.5) / (Fba + 0.5))
        Av = np.where(namer_is_b, Aab, -Aab)
        for c in ("one", "mutual", "none"):
            m = (cls == c) & (tot > 0)
            if m.any():
                out[f"sig_{c}"][d] = sig[m].mean()
        m1 = (cls == "one") & (tot > 0)
        if m1.any():
            out["A_one"][d] = Av[m1].mean()
        out["contrast"][d] = out["sig_one"][d] - out["sig_none"][d]
    return out
