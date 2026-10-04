"""H81 round 2 library: R1 record carrier, R2 exogenous-drift probe (operator directions, outside topics, clocks), R4 joint
OU fit with H82's boundary remanence. Panel, projectors and personal vectors come from the shared
infra/shared/culture_vectors.py (personal vectors: two-way agent + goal fixed effects, method="fe", Amendment A1; the R4
H82 arm keeps H82's leave-goals-out mean prior, culture_vectors.prior_mean). Statistics on pairs reuse h81lib (this
hypothesis's own round-1 code). No text; holdout already dropped by the shared tables and by scheme/build_r2.py.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import polars as pl
from scipy.optimize import curve_fit

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h81lib as L  # noqa: E402

ROOT = L.ROOT
sys.path.insert(0, str(ROOT / "infra" / "shared"))
import culture_vectors as CVM  # noqa: E402

CV = ROOT / "data/processed/shared/culture_vectors"
R2 = L.OUT / "round2"
MODELS = ["bge_small", "gte_modernbert"]
REC_GAP = 7          # record days must be <= block first day - 7
NEAR_OUT = 14        # R2b window (days) around the block mid-day
NEIGH, FAR_GAP = 21, 56   # R2a neighbour window and placebo distance (days)


# ================================================================================================ panel
@dataclass
class Ctx:
    model: str
    regime: str
    ad: pl.DataFrame
    X: np.ndarray
    pan: L.Panel
    kick: dict
    V: np.ndarray
    idx: list
    goals: list
    abg: dict
    rowmap: dict = field(default_factory=dict)   # global agentdays row -> panel index


def kickoffs(V, idx, regime, goals) -> dict:
    out = {}
    for g in goals:
        k = [e["i"] for e in idx if e["level"] == "goal" and e["goal_no"] == g and e["regime"] == regime and e["kind"] == "kickoff"]
        if not k:
            k = [e["i"] for e in idx if e["level"] == "goal" and e["goal_no"] == g and e["regime"] == regime and e["kind"] == "goal"]
        out[g] = V[k[0]] if k else np.zeros(32)
    return out


def load(model: str, regime: str, variant: str = "style_resid", use_human: bool = True, extra: dict | None = None) -> Ctx:
    ad = pl.read_parquet(CV / "agentdays.parquet").with_row_index("row").filter(pl.col("regime") == regime)
    X = np.load(CV / f"vecs_{model}_{variant}.npy").astype(np.float64)[ad["row"].to_numpy()]
    blocks = pl.read_parquet(CV / "blocks.parquet").filter(pl.col("regime") == regime)
    V = np.load(CV / f"dirs_{model}.npz")["V"].astype(np.float64)
    idx = json.loads((CV / f"dirs_index_{model}.json").read_text())
    goals = sorted(set(ad["goal_no"].to_list()))
    abg = {g: sorted(set(ad.filter(pl.col("goal_no") == g)["agent"].to_list())) for g in goals}
    P = projectors_extra(V, idx, regime, goals, abg, extra or {}, use_human)
    pan = L.Panel(ad, blocks, P)
    c = Ctx(model, regime, ad, X, pan, kickoffs(V, idx, regime, goals), V, idx, goals, abg)
    c.rowmap = {int(r): k for k, r in enumerate(ad["row"].to_list())}
    return c


def projectors_extra(V, idx, regime, goals, abg, extra: dict, use_human=True) -> dict:
    """culture_vectors.projectors plus extra directions per goal (R2a). With extra == {} it equals CVM.projectors."""
    if not extra:
        return CVM.projectors(V, idx, regime, goals, abg, use_human)
    P = {}
    for g in goals:
        base = [V[e["i"]] for e in idx if e["level"] == "goal" and e["goal_no"] == g and e["regime"] == regime
                and e["kind"] in ("kickoff", "goal", "kickoff_room")]
        if use_human:
            base += [V[e["i"]] for e in idx if e["level"] == "goal" and e["goal_no"] == g and e["regime"] == regime
                     and e["kind"] == "human"]
        ex = list(extra.get(g, []))
        P[(g, -1)] = CVM._proj(np.array(base + ex).reshape(-1, 32))
        for a in abg[g]:
            ag = [V[e["i"]] for e in idx if e["level"] == "goal" and e["goal_no"] == g and e["regime"] == regime
                  and e["kind"] == "agent_goal" and e["agent"] == a]
            P[(g, a)] = CVM._proj(np.array(base + ex + ag).reshape(-1, 32)) if ag else P[(g, -1)]
    return P


def with_projectors(c: Ctx, P: dict) -> Ctx:
    pan = L.Panel(c.ad, pl.read_parquet(CV / "blocks.parquet").filter(pl.col("regime") == c.regime), P)
    return Ctx(c.model, c.regime, c.ad, c.X, pan, c.kick, c.V, c.idx, c.goals, c.abg, c.rowmap)


# ================================================================================================ residuals
def residuals(pan: L.Panel, X: np.ndarray):
    """Day residuals Rd (rows without a personal vector are NaN) and agent-block residuals (A, B, R) = block means of Rd.
    Personal vectors: culture_vectors.personal_vectors(method='fe')."""
    Xp = L.project(pan, X)
    mu = CVM.personal_vectors(pan.agent, pan.goal, Xp, method="fe")
    M = np.full_like(Xp, np.nan)
    for k, key in enumerate(zip(pan.agent, pan.goal)):
        v = mu.get(key)
        if v is not None:
            M[k] = v
    Rd = np.einsum("nij,nj->ni", pan.Pi, Xp - M)
    ok = ~np.isnan(Rd[:, 0])
    keys = pan.agent.astype(np.int64) * 100000 + pan.block
    uk, inv = np.unique(keys[ok], return_inverse=True)
    S = np.zeros((len(uk), 32)); np.add.at(S, inv, Rd[ok]); n = np.bincount(inv)
    R = S / n[:, None]
    return (uk // 100000).astype(int), (uk % 100000).astype(int), R, Rd, M


def block_U(pan, A, B, R):
    U, members, cen = L.block_vectors(A, B, R, pan.nb, pan.block_goal)
    return U, members, cen


def pair_rows(pan: L.Panel, U: np.ndarray, members: list, kick: dict, clocks: dict | None = None) -> np.ndarray:
    """Cross-goal block pairs in h81lib.pair_table layout [b, c, dt, J, gs, s, s_perp(NaN), w] (goal-pair weights);
    extra columns: |clock_b - clock_c| for each clock in `clocks` (name -> per-block array), in insertion order."""
    rows = []
    ok = ~np.isnan(U[:, 0])
    for b in range(pan.nb):
        for c in range(b + 1, pan.nb):
            if pan.block_goal[b] == pan.block_goal[c] or not ok[b] or not ok[c]:
                continue
            mb, mc = members[b], members[c]
            J = len(mb & mc) / len(mb | mc)
            ex = [abs(v[b] - v[c]) for v in (clocks or {}).values()]
            rows.append([b, c, abs(pan.block_mid[b] - pan.block_mid[c]), J,
                         L._cos(kick[pan.block_goal[b]], kick[pan.block_goal[c]]), L._cos(U[b], U[c]), np.nan,
                         pan.block_goal[b] * 1000 + pan.block_goal[c]] + ex)
    T = np.array(rows, dtype=float).reshape(-1, 8 + len(clocks or {}))
    if len(T):
        _, inv, cnt = np.unique(T[:, 7], return_inverse=True, return_counts=True)
        T[:, 7] = 1.0 / cnt[inv]
    return T


def slow(pan, A, B, R, kick):
    U, members, cen = block_U(pan, A, B, R)
    T = pair_rows(pan, U, members, kick)
    return L.slow_stats(T), T, U, members, cen


# ================================================================================================ R1 record carrier
@dataclass
class R1Struct:
    """Static structure (does not depend on vectors): per agent-block the artifact lists and, per (artifact, agent,
    block first day), the panel indices of the artifact's record rows (agent != reader, day <= first - REC_GAP)."""
    ab: list                 # list of (agent, block_index, goal, {set_name: [artifacts]})
    rec_idx: dict            # (artifact, agent, first_day_num) -> np.ndarray of panel indices
    placebo: str             # name of the placebo set used as U


def r1_struct(c: Ctx, placebo: str) -> R1Struct:
    sets = pl.read_parquet(R2 / "r1_sets.parquet").filter(pl.col("regime") == c.regime)
    rec = pl.read_parquet(R2 / "r1_record_rows.parquet").filter(pl.col("regime") == c.regime)
    bid = {b: k for k, b in enumerate(c.pan.block_name)}
    bfirst = dict(zip(pl.read_parquet(CV / "blocks.parquet")["block"].to_list(),
                      L.day_num(pl.read_parquet(CV / "blocks.parquet")["first_day"].to_list()).tolist()))
    by_art = {}
    for a, sub in rec.partition_by("artifact", as_dict=True).items():
        rows = np.array([c.rowmap[int(r)] for r in sub["row"].to_list()])
        by_art[a[0]] = (rows, sub["agent"].to_numpy().astype(int), c.pan.day[rows])
    ab, rec_idx = [], {}
    for r in sets.iter_rows(named=True):
        b = bid.get(r["block"])
        if b is None:
            continue
        f = bfirst[r["block"]]
        d = {"R": r["R"], "U": r[placebo]}
        for nm, arts in d.items():
            keep = []
            for x in arts:
                key = (x, r["agent"], f)
                if key not in rec_idx:
                    if x not in by_art:
                        continue
                    rows, ags, days = by_art[x]
                    m = (ags != r["agent"]) & (days <= f - REC_GAP)
                    rec_idx[key] = rows[m]
                if len(rec_idx[key]):
                    keep.append(x)
            d[nm] = keep
        ab.append((int(r["agent"]), b, int(c.pan.block_goal[b]), f, d))
    return R1Struct(ab, rec_idx, placebo)


def _unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 0 and np.isfinite(n) else None


def set_vector(Rdc: np.ndarray, st: R1Struct, agent: int, first: float, arts: list):
    vs = []
    for x in arts:
        rows = st.rec_idx[(x, agent, first)]
        v = np.nanmean(Rdc[rows], axis=0) if len(rows) else None
        if v is not None and np.isfinite(v).all():
            u = _unit(v)
            if u is not None:
                vs.append(u)
    return _unit(np.mean(vs, axis=0)) if vs else None


def r1_stats(c: Ctx, X: np.ndarray, st: R1Struct, boot: int = 0, rng=None) -> dict:
    pan = c.pan
    A, B, R, Rd, _ = residuals(pan, X)
    st_slow, T, U, members, cen = slow(pan, A, B, R, c.kick)
    Rdc = Rd - cen
    rpos = {(a, b): k for k, (a, b) in enumerate(zip(A, B))}
    per_goal, comps, blockR, blockU = {}, [], {}, {}
    n_R = n_U = n_both = 0
    for agent, b, g, f, d in st.ab:
        k = rpos.get((agent, b))
        if k is None:
            continue
        aR = set_vector(Rdc, st, agent, f, d["R"]) if d["R"] else None
        aU = set_vector(Rdc, st, agent, f, d["U"]) if d["U"] else None
        n_R += aR is not None; n_U += aU is not None
        if aR is not None:
            blockR.setdefault(b, []).append(aR)
        if aU is not None:
            blockU.setdefault(b, []).append(aU)
        if aR is None or aU is None:
            continue
        n_both += 1
        r = R[k] - cen
        cr, cu = L._cos(r, aR), L._cos(r, aU)
        per_goal.setdefault(g, []).append(cr - cu)
        comps.append((cr, cu))
    gm = np.array([np.mean(v) for v in per_goal.values()]) if per_goal else np.array([])
    out = {"C_R1": float(gm.mean()) if len(gm) else np.nan, "n_agent_blocks_both": n_both, "n_goals": len(gm),
           "n_with_R": int(n_R), "n_with_U": int(n_U),
           "mean_cos_R": float(np.mean([x[0] for x in comps])) if comps else np.nan,
           "mean_cos_U": float(np.mean([x[1] for x in comps])) if comps else np.nan,
           "D_adjg": st_slow["D_adjg"]}
    if boot and len(gm) >= 3:
        bs = [rng.choice(gm, len(gm), replace=True).mean() for _ in range(boot)]
        out["C_R1_lo"], out["C_R1_hi"] = float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))
    # mediation: remove each block's read-record (placebo-record) direction from u_b
    for nm, bl in (("M_R", blockR), ("M_U", blockU)):
        U2 = U.copy()
        for b, vs in bl.items():
            a = _unit(np.mean(vs, axis=0))
            if a is not None and np.isfinite(U2[b, 0]):
                U2[b] = U2[b] - (U2[b] @ a) * a
        D2 = L.slow_stats(pair_rows(pan, U2, members, c.kick))["D_adjg"]
        out[nm] = float(1 - D2 / st_slow["D_adjg"]) if st_slow["D_adjg"] else np.nan
        out[nm + "_nblocks"] = len(bl)
    out["M_diff"] = out["M_R"] - out["M_U"]
    return out


def simulate_rec(c: Ctx, sc: dict, rng, st: R1Struct, lam: float):
    """S_rec: composition null plus planted record carriage. Blocks in time order; each member's days in block b get
    lam x the mean situational content (vector minus the author's personal part) of the record rows of the artifacts in
    its read set R (rows >= REC_GAP days older than the block)."""
    pan = c.pan

    def mvn(S, n):
        w, Vv = np.linalg.eigh((S + S.T) / 2); w = np.clip(w, 0, None)
        return rng.standard_normal((n, len(w))) * np.sqrt(w) @ Vv.T
    agents = np.unique(pan.agent); goals = np.unique(pan.goal)
    a = dict(zip(agents, mvn(sc["Sa"], len(agents))))
    g = dict(zip(goals, mvn(sc["Sg"], len(goals))))
    bf = mvn(sc["Sb"], pan.nb)
    Z = np.stack([g[x] for x in pan.goal]) + bf[pan.block] + sc["E"][rng.permutation(len(sc["E"]))]
    order = sorted(range(len(st.ab)), key=lambda k: st.ab[k][3])
    for k in order:
        agent, b, _, f, d = st.ab[k]
        if not d["R"]:
            continue
        vs = [Z[st.rec_idx[(x, agent, f)]].mean(0) for x in d["R"]]
        rows = np.flatnonzero((pan.agent == agent) & (pan.block == b))
        Z[rows] += lam * np.mean(vs, axis=0)
    return np.stack([a[x] for x in pan.agent]) + Z


# ================================================================================================ R2a operator beyond centroid
def human_dirs(c: Ctx):
    """Per goal: its human centroid (round-1 direction) and top-3 human PCs; goal spans (day numbers)."""
    cen = {e["goal_no"]: c.V[e["i"]] for e in c.idx if e["level"] == "goal" and e["kind"] == "human" and e["regime"] == c.regime}
    z = np.load(R2 / f"human_pcs_{c.model}.npz")
    pcs = {int(k.split("|")[0]): p for k, p in zip(z["keys"], z["pcs"]) if k.split("|")[1] == c.regime}
    span = {g: (c.pan.day[c.pan.goal == g].min(), c.pan.day[c.pan.goal == g].max()) for g in c.goals}
    return cen, pcs, span


def _gap(s1, s2):
    return max(0.0, max(s1[0], s2[0]) - min(s1[1], s2[1]))


def r2a_extra(c: Ctx, rng=None, placebo: bool = False) -> dict:
    cen, pcs, span = human_dirs(c)
    extra = {}
    for g in c.goals:
        neigh = [h for h in c.goals if h != g and h in cen and _gap(span[g], span[h]) <= NEIGH]
        far = [h for h in c.goals if h != g and _gap(span[g], span[h]) >= FAR_GAP]
        if not placebo:
            ex = list(pcs.get(g, [])) + [cen[h] for h in neigh]
        else:
            ex = []
            fp = [h for h in far if h in pcs]
            if g in pcs and fp:
                ex += list(pcs[fp[rng.integers(len(fp))]])
            fc = [h for h in far if h in cen]
            if neigh and fc:
                ex += [cen[h] for h in rng.choice(fc, len(neigh), replace=len(fc) < len(neigh))]
        extra[g] = ex
    return extra


# ================================================================================================ R2b outside topics
@dataclass
class OutStruct:
    rows: np.ndarray        # panel indices of agent-days used
    S: list                 # per used agent-day: statement matrix (n x 32), outside first (m rows)
    m: np.ndarray           # number of outside statements
    W: np.ndarray           # nb x n_used block aggregation weights (other goals, |day - mid| <= NEAR_OUT)


def out_struct(c: Ctx) -> OutStruct:
    fl = pl.read_parquet(R2 / "outside_flags.parquet").filter(pl.col("regime") == c.regime)
    S_all = np.load(ROOT / f"data/processed/shared/embeddings/statements_style_resid32_{c.model}.npy", mmap_mode="r")
    key = {(int(a), d): k for k, (a, d) in enumerate(zip(c.pan.agent, c.pan.date))}
    rows, S, m = [], [], []
    for (a, d), sub in fl.group_by(["agent", "pt_date"], maintain_order=True):
        k = key.get((int(a), d))
        if k is None:
            continue
        o = sub["outside"].to_numpy(); sr = sub["srow"].to_numpy()
        mo = int(o.sum()); n = len(o)
        if mo == 0 or n < 2 * mo:
            continue
        Xs = np.asarray(S_all[np.concatenate([sr[o], sr[~o]])], dtype=np.float64)
        rows.append(k); S.append(Xs); m.append(mo)
    rows = np.array(rows); m = np.array(m)
    pan = c.pan
    W = np.zeros((pan.nb, len(rows)))
    for b in range(pan.nb):
        sel = (pan.goal[rows] != pan.block_goal[b]) & (np.abs(pan.day[rows] - pan.block_mid[b]) <= NEAR_OUT)
        if sel.any():
            W[b, sel] = 1.0 / sel.sum()
    return OutStruct(rows, S, m, W)


def _sub_resid(c: Ctx, os_: OutStruct, M: np.ndarray, cen: np.ndarray, picks: list) -> np.ndarray:
    """picks[j]: (D, k) index array into os_.S[j]; returns residuals (D, n_used, 32)."""
    D = picks[0].shape[0]
    out = np.zeros((D, len(os_.rows), 32))
    for j, k in enumerate(os_.rows):
        v = os_.S[j][picks[j]].mean(1)
        v /= np.maximum(np.linalg.norm(v, axis=1, keepdims=True), 1e-12)
        out[:, j] = (v - M[k]) @ c.pan.Pi[k].T - cen
    return out


def r2b_stats(c: Ctx, X: np.ndarray, os_: OutStruct, rng, n_ctl=20, n_perm=200) -> dict:
    pan = c.pan
    A, B, R, Rd, M = residuals(pan, X)
    U, members, cen = block_U(pan, A, B, R)
    okb = ~np.isnan(U[:, 0]) & (os_.W.sum(1) > 0)
    okd = ~np.isnan(M[os_.rows, 0])
    W = os_.W * okd[None, :]
    W = np.divide(W, W.sum(1, keepdims=True), out=np.zeros_like(W), where=W.sum(1, keepdims=True) > 0)
    okb &= W.sum(1) > 0
    gw = np.zeros(pan.nb)
    for g in np.unique(pan.block_goal[okb]):
        sel = okb & (pan.block_goal == g); gw[sel] = 1.0 / sel.sum()
    gw /= gw.sum()

    def A_of(Rsub):   # Rsub (D, n_used, 32) -> (D,) goal-weighted mean cosine with u_b
        Rsub = np.where(okd[None, :, None], Rsub, 0.0)
        C = np.einsum("bn,dnk->dbk", W, Rsub)
        num = np.einsum("dbk,bk->db", C, np.nan_to_num(U))
        den = np.linalg.norm(C, axis=2) * np.linalg.norm(np.nan_to_num(U), axis=1)[None, :]
        cs = np.divide(num, den, out=np.zeros_like(num), where=den > 0)
        return (cs * gw[None, :]).sum(1)
    out_pick = [np.arange(mo)[None, :] for mo in os_.m]
    ctl_pick = [mo + np.argsort(rng.random((n_ctl, len(S) - mo)), axis=1)[:, :mo] for S, mo in zip(os_.S, os_.m)]
    a_out = A_of(_sub_resid(c, os_, M, cen, out_pick))[0]
    a_ctl = A_of(_sub_resid(c, os_, M, cen, ctl_pick))
    L_out = float(a_out - a_ctl.mean())
    perm = []
    for _ in range(max(1, n_perm // 50)):
        D = min(50, n_perm)
        pp, pc = [], []
        for S, mo in zip(os_.S, os_.m):
            o = np.argsort(rng.random((D, len(S))), axis=1)
            pp.append(o[:, :mo]); pc.append(o[:, mo:2 * mo])
        perm.append(A_of(_sub_resid(c, os_, M, cen, pp)) - A_of(_sub_resid(c, os_, M, cen, pc)))
    perm = np.concatenate(perm)
    return {"L_out": L_out, "A_out": float(a_out), "A_ctl": float(a_ctl.mean()), "perm_q95": float(np.quantile(perm, 0.95)),
            "perm_mean": float(perm.mean()), "p_perm": float((np.sum(perm >= L_out) + 1) / (len(perm) + 1)),
            "n_agentdays": int(okd.sum()), "n_blocks": int(okb.sum()), "share_outside": float(np.mean(os_.m / np.array([len(s) for s in os_.S])))}


# ================================================================================================ R2c clocks
def block_clocks(c: Ctx) -> dict:
    ck = pl.read_parquet(R2 / "clocks.parquet")
    H = dict(zip(ck["pt_date"].to_list(), ck["cum_hours"].to_list()))
    bl = pl.read_parquet(CV / "blocks.parquet").filter(pl.col("regime") == c.regime)
    bl = {b: (f, l) for b, f, l in zip(bl["block"].to_list(), bl["first_day"].to_list(), bl["last_day"].to_list())}
    hrs = np.array([(H[bl[b][0]] + H[bl[b][1]]) / 2 for b in c.pan.block_name])
    return {"calendar": c.pan.block_mid.astype(float), "hours": hrs, "goals": c.pan.block_goal.astype(float)}


def ou_fit(x, y, w, scale):
    ok = np.isfinite(y)
    x, y, w = x[ok], y[ok], w[ok]
    f = lambda t, A, tau, c0: A * np.exp(-t / tau) + c0  # noqa: E731
    try:
        p, cov = curve_fit(f, x, y, p0=(0.1, scale, 0.0), sigma=1 / np.sqrt(w), bounds=([-2, scale / 50, -1], [2, scale * 20, 1]),
                           maxfev=20000)
        sse = float((w * (y - f(x, *p)) ** 2).sum())
        se = float(np.sqrt(cov[1, 1])) if np.isfinite(cov[1, 1]) else np.nan
        return {"A": float(p[0]), "tau": float(p[1]), "c": float(p[2]), "tau_se": se, "sse": sse, "n": int(len(y))}
    except Exception as e:  # noqa: BLE001
        return {"A": np.nan, "tau": np.nan, "c": np.nan, "tau_se": np.nan, "sse": np.nan, "n": int(len(y)), "err": str(e)}


def clock_scales(c: Ctx, clocks: dict, tau_days: float = 28.0) -> dict:
    span_days = clocks["calendar"].max() - clocks["calendar"].min()
    return {"calendar": tau_days, "hours": tau_days * (clocks["hours"].max() - clocks["hours"].min()) / span_days,
            "goals": tau_days * (clocks["goals"].max() - clocks["goals"].min()) / span_days}


def r2c_stats(c: Ctx, X: np.ndarray, clocks: dict, scales: dict) -> dict:
    pan = c.pan
    A, B, R, _, _ = residuals(pan, X)
    U, members, _ = block_U(pan, A, B, R)
    T = pair_rows(pan, U, members, c.kick, clocks)
    out = {}
    for j, nm in enumerate(clocks):
        out[nm] = ou_fit(T[:, 8 + j], T[:, 5], T[:, 7], scales[nm])
    sse = {k: v["sse"] for k, v in out.items()}
    out["best"] = min(sse, key=lambda k: sse[k] if np.isfinite(sse[k]) else np.inf)
    return out


def simulate_clock(c: Ctx, sc: dict, rng, share: float, clock: np.ndarray, tau: float):
    """h81lib.simulate with the OU slow mode indexed by an arbitrary per-block clock (ties: identical state)."""
    pan = c.pan

    def mvn(S, n):
        w, Vv = np.linalg.eigh((S + S.T) / 2); w = np.clip(w, 0, None)
        return rng.standard_normal((n, len(w))) * np.sqrt(w) @ Vv.T
    agents = np.unique(pan.agent); goals = np.unique(pan.goal)
    a = dict(zip(agents, mvn(sc["Sa"], len(agents))))
    g = dict(zip(goals, mvn(sc["Sg"], len(goals)) * np.sqrt(1 - share)))
    bf = mvn(sc["Sb"], pan.nb)
    Xs = np.stack([a[x] for x in pan.agent]) + np.stack([g[x] for x in pan.goal]) + bf[pan.block]
    order = np.argsort(clock, kind="stable"); z = mvn(sc["Sg"], pan.nb) * np.sqrt(share)
    u = np.zeros_like(z); prev = None
    for k in order:
        if prev is None:
            u[k] = z[k]
        else:
            rho = np.exp(-(clock[k] - clock[prev]) / tau)
            u[k] = rho * u[prev] + np.sqrt(max(1 - rho ** 2, 0)) * z[k]
        prev = k
    Xs = Xs + u[pan.block]
    return Xs + sc["E"][rng.permutation(len(sc["E"]))]


# ================================================================================================ R4 H82 arm
class H82Arm:
    """H82's boundary regression (h82lib design, reimplemented on the shared tables): v (unit) on kickoff k_P, goal text
    g_P, previous kickoff, the day's human centroid, the agent's room kickoff (if P has >= 2), #51 agent goal, the H82
    prior (culture_vectors.prior_mean, leave {P, Q} out) and the leave-i-out centroid e_Q of goal Q; gamma = coef(e_Q)."""

    def __init__(self, model: str, regime: str, X: np.ndarray | None = None):
        ad = pl.read_parquet(CV / "agentdays.parquet").with_row_index("row").filter(pl.col("regime") == regime)
        Xall = np.load(CV / f"vecs_{model}_style_resid.npy").astype(np.float64)[ad["row"].to_numpy()]
        self.X = Xall if X is None else X
        self.agent = ad["agent"].to_numpy().astype(int); self.goal = ad["goal_no"].to_numpy().astype(int)
        self.date = np.array(ad["pt_date"].to_list()); self.day = L.day_num(self.date)
        self.regime_arr = np.array([regime] * len(ad)); self.regime = regime
        self.room = ad["room"].fill_null(-1).to_numpy().astype(int)
        V = np.load(CV / f"dirs_{model}.npz")["V"].astype(np.float64)
        idx = json.loads((CV / f"dirs_index_{model}.json").read_text())
        self.gd, self.rd, self.dh, self.ag = {}, {}, {}, {}
        for e in idx:
            if e["regime"] != regime:
                continue
            if e["level"] == "goal" and e["kind"] in ("kickoff", "goal"):
                self.gd[(e["goal_no"], e["kind"])] = V[e["i"]]
            elif e["level"] == "goal" and e["kind"] == "kickoff_room":
                self.rd.setdefault(e["goal_no"], {})[e["room"]] = V[e["i"]]
            elif e["level"] == "goal" and e["kind"] == "agent_goal":
                self.ag.setdefault(e["agent"], []).append(V[e["i"]])
            elif e["level"] == "day" and e["kind"] == "human":
                self.dh[e["pt_date"]] = V[e["i"]]
        self.goals = sorted(set(self.goal.tolist()))
        self.gdate = {g: float(self.day[self.goal == g].mean()) for g in self.goals}
        bd = pl.read_parquet(R2 / "boundaries.parquet").filter(pl.col("regime") == regime)
        self.bd = list(bd.iter_rows(named=True))
        self._cent, self._prior = {}, {}

    def set_X(self, X):
        self.X = X; self._cent, self._prior = {}, {}

    def centroid(self, g, a):
        k = (g, a)
        if k not in self._cent:
            m = (self.goal == g) & (self.agent != a)
            self._cent[k] = CVM.unit(self.X[m].mean(0)) if m.sum() >= 3 else None
        return self._cent[k]

    def prior(self, a, leave):
        k = (a, leave)
        if k not in self._prior:
            self._prior[k] = CVM.prior_mean(self.X, self.agent, self.goal, self.regime_arr, a, self.regime, set(leave))
        return self._prior[k]

    def gammas(self, ndays: int = 5) -> np.ndarray:
        """Rows: P, d, Q, lag (day d - mean date of Q), gamma, n_agents."""
        out = []
        z = np.zeros(32)
        for b in self.bd:
            P, prev = b["P"], b["prev"]
            kP, gP, kprev = self.gd.get((P, "kickoff"), z), self.gd.get((P, "goal"), z), self.gd.get((prev, "kickoff"), z)
            rooms = self.rd.get(P, {})
            for di, day in enumerate(b["days_P"][:ndays]):
                rows = np.flatnonzero((self.goal == P) & (self.date == day))
                hum = self.dh.get(day, z)
                dnum = float(L.day_num([day])[0])
                for Q in self.goals:
                    if Q == P:
                        continue
                    ys, Zs = [], []
                    for r in rows:
                        a = self.agent[r]
                        pr = self.prior(a, (P, Q)); e = self.centroid(Q, a)
                        if pr is None or e is None:
                            continue
                        ag = self.ag.get(a)
                        cols = [kP, gP, kprev, hum, rooms.get(self.room[r], z) if len(rooms) >= 2 else z,
                                CVM.unit(np.mean(ag, axis=0)) if (ag and P == 51) else z, pr, e]
                        ys.append(self.X[r]); Zs.append(np.stack(cols, 1))
                    if len(ys) < 2:
                        continue
                    y = np.concatenate(ys); Zf = np.concatenate(Zs)
                    keep = np.abs(Zf).sum(0) > 0
                    if not keep[-1] or len(y) <= keep.sum():
                        continue
                    beta, *_ = np.linalg.lstsq(Zf[:, keep], y, rcond=None)
                    out.append((P, di + 1, Q, dnum - self.gdate[Q], float(beta[-1]), len(ys)))
        return np.array(out, dtype=float)


def h82_weights(G: np.ndarray) -> np.ndarray:
    """Each boundary (P) carries total weight 1."""
    _, inv, cnt = np.unique(G[:, 0], return_inverse=True, return_counts=True)
    return 1.0 / cnt[inv]


def joint_fit(x1, y1, w1, x2, y2, w2, scale=28.0) -> dict:
    """Separate and shared-tau OU fits; Gaussian likelihood with a variance per data set (weights normalized to n).
    LR = 2 (l_sep - l_joint)."""
    f1 = ou_fit(x1, y1, w1, scale); f2 = ou_fit(x2, y2, w2, scale)
    n1, n2 = len(y1), len(y2)
    w1n = w1 * n1 / w1.sum(); w2n = w2 * n2 / w2.sum()
    x = np.concatenate([x1, x2]); y = np.concatenate([y1, y2]); ds = np.r_[np.zeros(n1), np.ones(n2)]

    def model(_, A1, c1, A2, c2, tau):
        return np.where(ds == 0, A1 * np.exp(-x / tau) + c1, A2 * np.exp(-x / tau) + c2)
    # per-dataset residual variance on the normalized-weight scale
    s1 = f1["sse"] / w1.sum() if np.isfinite(f1["sse"]) else 1.0
    s2 = f2["sse"] / w2.sum() if np.isfinite(f2["sse"]) else 1.0
    out = {"sep81": f1, "sep82": f2}
    try:
        # iterate: fit with per-dataset variance, update the variances (3 passes)
        v1, v2 = max(s1, 1e-12), max(s2, 1e-12)
        p = (f1["A"] if np.isfinite(f1["A"]) else 0.1, f1["c"] if np.isfinite(f1["c"]) else 0,
             f2["A"] if np.isfinite(f2["A"]) else 0.1, f2["c"] if np.isfinite(f2["c"]) else 0, scale)
        for _ in range(3):
            sig = np.sqrt(np.r_[v1 / w1n, v2 / w2n])
            p, cov = curve_fit(model, x, y, p0=p, sigma=sig, bounds=([-2, -1, -2, -1, scale / 50], [2, 1, 2, 1, scale * 20]),
                               maxfev=40000)
            r = y - model(x, *p)
            v1 = float((w1n * r[:n1] ** 2).sum() / n1); v2 = float((w2n * r[n1:] ** 2).sum() / n2)
        sse1_sep = f1["sse"] * n1 / w1.sum(); sse2_sep = f2["sse"] * n2 / w2.sum()
        lr = n1 * np.log(v1 / (sse1_sep / n1)) + n2 * np.log(v2 / (sse2_sep / n2))
        out["joint"] = {"tau": float(p[4]), "tau_se": float(np.sqrt(cov[4, 4])), "A81": float(p[0]), "A82": float(p[2]),
                        "c81": float(p[1]), "c82": float(p[3]), "LR": float(lr)}
    except Exception as e:  # noqa: BLE001
        out["joint"] = {"tau": np.nan, "tau_se": np.nan, "LR": np.nan, "err": str(e)}
    out["dtau"] = f2["tau"] - f1["tau"]
    return out
