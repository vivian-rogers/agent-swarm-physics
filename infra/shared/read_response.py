"""Read-gated linear response (RGLR) with per-block Gram aggregation: content inflow chi_j, unread-placebo lam_j and
outflow kappa_i per agent, plus reply-channel rates, so any window, block bootstrap or reweighting is a weighted sum.

Copied from H65 (hypotheses/H65-leaders-are-routers/analysis/h65lib.py, 2026-10-04; STANDARDS §8). The functions are
verbatim; H65's file is untouched. Could serve H29 (seen-vs-unseen content), H32 (information currents) and H52
(read-out susceptibility): any design that regresses a statement vector on what its author had read.

Model (H65 card): z_B = a z_P + a' e + b f + h H + lam U + chi R + xi   (inflow: own regression of each target agent j)
                  z_B = [same nuisance with R^{-i}] + kappa_i S_i + xi  (outflow: one kappa_i shared over targets j != i,
                                                                          target-specific nuisance partialled out, FWL)
  z_B  target statement vector (32-d whitened, or style_resid_period), goal / kickoff / period-mean field projected out
  z_P, e  own previous statement and own EWMA (same agent, PT day; half-life 5 statements)
  f    day x room leave-agent-out mean of others' statements
  R    read agent statements, weights exp(-age / 900 s), R = sum w z / (1 + sum w);  H read human messages (same form)
  U    in-flight placebo: same-room agent statements posted in [t_call, t_B) by others (cannot have been read)
  S_i  the part of R from sender i. Scalar (isotropic) coefficients on the stacked 32 coordinates.
Blocks: room x 30-min bins (BLOCK_S) unless the caller passes its own block codes.

Inputs (the H65 scheme's per-period tables; any builder that writes these columns can use the estimator):
  targets  tgt (row id), srow (embeddings/statements row), agent, t, pt_date, room, unit_id, t_call (producing call;
           rows with null t_call are dropped by the caller), parent_agent (DQ2 parent author or null)
  reads    tgt, src_kind (0 agent read, 1 human read, 2 in-flight unread), sender, vrow (statements row for kinds 0/2;
           embeddings/chat_index row for kind 1), age_s (t_B - t_A)
Holdout: the estimator reads only what it is given; the input builder masks the holdout (H65's does, with its own
confirm-only switch).

  load_unit(data_dir, goal, model, unit=None) -> tg, reads, Zs, pos, Hm, hpos, regime   (H65 run.load_period)
  build_design -> Design;  build_grams(Design) -> Grams;  estimate(Grams, w) -> per-agent frame;  bootstrap;  pct
Verify: uv run python infra/shared/read_response.py --verify   (H65 replication point estimates, several units x models)
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json  # noqa: E402
import sys  # noqa: E402
from dataclasses import dataclass, field  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SH = ROOT / "data/processed/shared"
H65 = ROOT / "data/processed/H65-leaders-are-routers"
sys.path.insert(0, str(Path(__file__).resolve().parent))

TAU = 900.0          # 15 min
HALF_LIFE = 5        # own EWMA, statements
BLOCK_S = 1800
NUIS = ["zP", "e", "f", "H", "U"]          # nuisance regressors (in order)
IN_COLS = NUIS + ["R"]                      # inflow design; chi = last
OUT_COLS = NUIS + ["Rm", "S"]               # outflow design; kappa = last


# ------------------------------------------------------------------------------------------------ vectors
def field_basis(goal: int, regime: str, model: str, Zper: np.ndarray) -> np.ndarray:
    """Orthonormal field directions (rows): goal_whole, kickoff_room(s) whitened in the regime basis, and the period
    mean of the agent statement vectors."""
    from embed_models import goal_vectors, load_whitener
    g = pl.read_parquet(SH / "embeddings/goals.parquet").with_row_index("gi")
    sel = g.filter((pl.col("goal_no") == goal) & pl.col("kind").cast(pl.String).is_in(["goal_whole", "kickoff_room"]))
    raw = goal_vectors("bge_small" if model == "style" else model)[sel["gi"].to_numpy()].astype(np.float32)
    W = load_whitener(regime, 32, "bge_small" if model == "style" else model)
    G = W(raw) if len(raw) else np.zeros((0, 32))
    G = G / np.maximum(np.linalg.norm(G, axis=1, keepdims=True), 1e-9)
    m = Zper.mean(0, keepdims=True)
    M = np.vstack([G, m / max(np.linalg.norm(m), 1e-9)])
    U_, s, Vt = np.linalg.svd(M, full_matrices=False)
    return Vt[s > 1e-6 * s.max()]


def load_vectors(goal: int, model: str, tg: pl.DataFrame, reads: pl.DataFrame):
    """Returns (Z_target (n x 32), lookup for agent statement rows, human vectors by chat_index row), field-projected."""
    from embed_models import load_whitener
    if model == "style":
        V = np.load(SH / "embeddings/statements_style_resid_period32_bge_small.npy", mmap_mode="r")
    else:
        V = np.load(SH / f"embeddings/statements_white32_{model}.npy", mmap_mode="r")
    srows = np.unique(np.concatenate([tg["srow"].to_numpy(),
                                      reads.filter(pl.col("src_kind") != 1)["vrow"].to_numpy()]))
    srows = srows[srows >= 0]
    Zs = np.asarray(V[srows], dtype=np.float64)
    pos = {int(r): k for k, r in enumerate(srows)}
    hrows = np.unique(reads.filter(pl.col("src_kind") == 1)["vrow"].to_numpy())
    hrows = hrows[hrows >= 0]
    regime = tg["regime"][0] if "regime" in tg.columns else None
    st = pl.read_parquet(SH / "embeddings/statements.parquet", columns=["regime"]).with_row_index("srow")
    regime = st.filter(pl.col("srow") == int(tg["srow"][0]))["regime"][0]
    if len(hrows):
        raw = np.load(SH / f"embeddings/chat_{'bge_small' if model == 'style' else model}.npy", mmap_mode="r")
        W = load_whitener(regime, 32, "bge_small" if model == "style" else model)
        Hm = W(np.asarray(raw[hrows], dtype=np.float32)).astype(np.float64)
        Hm = Hm / np.maximum(np.linalg.norm(Hm, axis=1, keepdims=True), 1e-9)
    else:
        Hm = np.zeros((0, 32))
    hpos = {int(r): k for k, r in enumerate(hrows)}
    Zt = Zs[[pos[int(r)] for r in tg["srow"].to_numpy()]]
    B = field_basis(goal, regime, model, Zt)
    proj = lambda X: X - (X @ B.T) @ B  # noqa: E731
    return proj(Zs), pos, proj(Hm), hpos, regime


# ------------------------------------------------------------------------------------------------ design
@dataclass
class Design:
    tg: pl.DataFrame
    agent: np.ndarray
    block: np.ndarray            # block code per target
    z: np.ndarray
    X: dict                      # name -> (n x 32)
    S: dict                      # (target k) -> {sender: (Svec, W, SWvec)}
    SW: np.ndarray               # pooled sum w z (agents)
    W: np.ndarray                # pooled sum w
    parent: np.ndarray
    extra: dict = field(default_factory=dict)


def build_design(tg: pl.DataFrame, reads: pl.DataFrame, Zs, pos, Hm, hpos, block=None) -> Design:
    tg = tg.sort("tgt")
    n = tg.height
    agent = tg["agent"].to_numpy()
    t = tg["t"].dt.epoch("us").to_numpy() / 1e6
    day = tg["pt_date"].to_numpy()
    room = tg["room"].to_numpy()
    z = Zs[[pos[int(r)] for r in tg["srow"].to_numpy()]]
    if block is None:
        block = room.astype(np.int64) * 10_000_000 + (t // BLOCK_S).astype(np.int64)
    # own past and EWMA (same agent, same PT day, time order)
    zP = np.zeros_like(z)
    e = np.zeros_like(z)
    alpha = 1 - 2 ** (-1 / HALF_LIFE)
    order = np.argsort(t, kind="stable")
    last = {}
    ew = {}
    for k in order:
        key = (agent[k], day[k])
        if key in last:
            zP[k] = z[last[key]]
            e[k] = ew[key]
            ew[key] = (1 - alpha) * ew[key] + alpha * z[k]
        else:
            ew[key] = z[k].copy()
        last[key] = k
    # day x room leave-j-out mean of other agents' statements
    f = np.zeros_like(z)
    dr = np.array([f"{d}|{r}" for d, r in zip(day, room)])
    for key in np.unique(dr):
        idx = np.flatnonzero(dr == key)
        tot = z[idx].sum(0)
        cnt = len(idx)
        for a in np.unique(agent[idx]):
            ia = idx[agent[idx] == a]
            m = cnt - len(ia)
            if m > 0:
                f[ia] = (tot - z[ia].sum(0)) / m
    # read inputs
    H = np.zeros_like(z)
    U = np.zeros_like(z)
    SW = np.zeros_like(z)
    Wt = np.zeros(n)
    S = {}
    tk = reads["tgt"].to_numpy()
    kind = reads["src_kind"].to_numpy()
    snd = reads["sender"].to_numpy()
    vr = reads["vrow"].to_numpy()
    w = np.exp(-np.maximum(reads["age_s"].to_numpy().astype(float), 0) / TAU)
    tg_index = {int(x): k for k, x in enumerate(tg["tgt"].to_numpy())}
    acc_h, acc_u = {}, {}
    for r in range(len(tk)):
        k = tg_index.get(int(tk[r]))
        if k is None:
            continue
        if kind[r] == 1:
            p = hpos.get(int(vr[r]))
            if p is None:
                continue
            a = acc_h.setdefault(k, [np.zeros(z.shape[1]), 0.0])
            a[0] += w[r] * Hm[p]
            a[1] += w[r]
            continue
        p = pos.get(int(vr[r]))
        if p is None:
            continue
        if kind[r] == 2:
            a = acc_u.setdefault(k, [np.zeros(z.shape[1]), 0.0])
            a[0] += w[r] * Zs[p]
            a[1] += w[r]
            continue
        SW[k] += w[r] * Zs[p]
        Wt[k] += w[r]
        d = S.setdefault(k, {})
        if snd[r] in d:
            d[snd[r]][0] += w[r] * Zs[p]
            d[snd[r]][1] += w[r]
        else:
            d[snd[r]] = [w[r] * Zs[p], w[r]]
    for k, (v, ww) in acc_h.items():
        H[k] = v / (1 + ww)
    for k, (v, ww) in acc_u.items():
        U[k] = v / (1 + ww)
    R = SW / (1 + Wt)[:, None]
    X = {"zP": zP, "e": e, "f": f, "H": H, "U": U, "R": R}
    parent = tg["parent_agent"].fill_null(-1).to_numpy()
    return Design(tg, agent, np.asarray(block), z, X, S, SW, Wt, parent)


# ------------------------------------------------------------------------------------------------ block Grams
def _gram_rows(cols: list, z: np.ndarray):
    """Per-row inner products: G (n x p x p), c (n x p)."""
    M = np.stack(cols, axis=1)                         # n x p x 32
    G = np.einsum("npd,nqd->npq", M, M)
    c = np.einsum("npd,nd->np", M, z)
    return G, c


@dataclass
class Grams:
    blocks: np.ndarray                  # unique block codes
    bmeta: pl.DataFrame                 # block -> (day, room, t0)
    Gin: dict                           # agent j -> (nb x 6 x 6), cin (nb x 6), cnt (nb)
    Gout: dict                          # (i, j) -> (nb x 7 x 7), (nb x 7), exposed count (nb)
    rep: dict                           # agent -> arrays per block: n_stmt, n_reply_out, n_reply_in
    rep_auth: dict                      # agent j -> {parent author: per-block counts}
    agents: np.ndarray


def build_grams(D: Design) -> Grams:
    ub, binv = np.unique(D.block, return_inverse=True)
    nb = len(ub)
    t = D.tg["t"].dt.epoch("us").to_numpy() / 1e6
    meta = pl.DataFrame({"block": ub, "t0": [t[binv == b].min() for b in range(nb)],
                         "day": [D.tg["pt_date"][int(np.flatnonzero(binv == b)[0])] for b in range(nb)],
                         "room": [int(D.tg["room"][int(np.flatnonzero(binv == b)[0])]) for b in range(nb)]})
    G6, c6 = _gram_rows([D.X[k] for k in IN_COLS], D.z)
    agents = np.unique(D.agent)
    Gin = {}
    for j in agents:
        m = D.agent == j
        bj = binv[m]
        Gin[int(j)] = (np.stack([np.bincount(bj, G6[m][:, p, q], nb) for p in range(6) for q in range(6)], 1)
                       .reshape(nb, 6, 6), np.stack([np.bincount(bj, c6[m][:, p], nb) for p in range(6)], 1),
                       np.bincount(bj, None, nb))
    # outflow: base design with S = 0 is the inflow design (R in place of Rm); corrections where i was read
    Gout = {}
    nucols = [D.X[k] for k in NUIS]
    for j in agents:
        mj = np.flatnonzero(D.agent == j)
        Gb = np.zeros((nb, 7, 7))
        cb = np.zeros((nb, 7))
        Gb[:, :6, :6] = Gin[int(j)][0]
        cb[:, :6] = Gin[int(j)][1]
        senders = set()
        for k in mj:
            senders.update(D.S.get(int(k), {}).keys())
        for i in senders:
            if i == j or i < 0:
                continue
            ks = [k for k in mj if i in D.S.get(int(k), {})]
            ks = np.array(ks)
            Svec = np.stack([D.S[int(k)][i][0] / (1 + D.S[int(k)][i][1]) for k in ks])
            Rm = np.stack([(D.SW[k] - D.S[int(k)][i][0]) / (1 + D.W[k] - D.S[int(k)][i][1]) for k in ks])
            Gnew, cnew = _gram_rows([D.X[c][ks] for c in NUIS] + [Rm, Svec], D.z[ks])
            Gold, cold = G6[ks], c6[ks]
            dG = Gnew.copy()
            dG[:, :6, :6] -= Gold
            dc = cnew.copy()
            dc[:, :6] -= cold
            bk = binv[ks]
            G = Gb.copy()
            c = cb.copy()
            for p in range(7):
                c[:, p] += np.bincount(bk, dc[:, p], nb)
                for q in range(7):
                    G[:, p, q] += np.bincount(bk, dG[:, p, q], nb)
            Gout[(int(i), int(j))] = (G, c, np.bincount(bk, None, nb))
    # reply channel
    rep, rep_auth = {}, {}
    for a in agents:
        m = D.agent == a
        rep[int(a)] = {"n": np.bincount(binv[m], None, nb),
                       "ro": np.bincount(binv[m], (D.parent[m] >= 0).astype(float), nb),
                       "ri": np.bincount(binv, (D.parent == a).astype(float), nb)}
        auth = {}
        for p_ in np.unique(D.parent[m]):
            if p_ < 0:
                continue
            auth[int(p_)] = np.bincount(binv[m & (D.parent == p_)], None, nb)
        rep_auth[int(a)] = auth
    return Grams(ub, meta, Gin, Gout, rep, rep_auth, agents)


def _solve(G, c, ridge=1e-8):
    p = G.shape[0]
    tr = np.trace(G) / p if np.trace(G) > 0 else 1.0
    return np.linalg.solve(G + ridge * tr * np.eye(p), c)


def _partial(G, c, last: int):
    """Partial (FWL) numerator and denominator for the last regressor given the others."""
    Gxx = G[:last, :last]
    gxs = G[:last, last]
    tr = np.trace(Gxx) / max(last, 1) if np.trace(Gxx) > 0 else 1.0
    A = np.linalg.solve(Gxx + 1e-8 * tr * np.eye(last), np.c_[gxs, c[:last]])
    num = c[last] - gxs @ A[:, 1]
    den = G[last, last] - gxs @ A[:, 0]
    return num, den


def estimate(Gr: Grams, w: np.ndarray, min_n: int = 30, min_exp: int = 30) -> pl.DataFrame:
    """Per-agent chi (inflow), lam (unread), kappa (outflow), RO, BO, RI under block weights w (0 = block excluded,
    integers = bootstrap multiplicities)."""
    present = [a for a in Gr.agents if (Gr.rep[int(a)]["n"] * w).sum() > 0]
    Np = len(present)
    rows = []
    for a in Gr.agents:
        a = int(a)
        n = float((Gr.rep[a]["n"] * w).sum())
        G, c, cnt = Gr.Gin[a]
        Gs = np.tensordot(w, G, 1)
        cs = w @ c
        chi = lam = np.nan
        if n >= min_n and Gs[5, 5] > 0:
            beta = _solve(Gs, cs)
            chi, lam = float(beta[5]), float(beta[4])
        num = den = 0.0
        nexp = 0.0
        for (i, j), (Go, co, ce) in Gr.Gout.items():
            if i != a:
                continue
            e_ = float(ce @ w)
            if e_ < 3:
                continue
            nn, dd = _partial(np.tensordot(w, Go, 1), w @ co, 6)
            if dd > 0:
                num += nn
                den += dd
                nexp += e_
        kap = float(num / den) if (den > 0 and nexp >= min_exp) else np.nan
        ro = float((Gr.rep[a]["ro"] * w).sum() / n) if n > 0 else np.nan
        ri = float((Gr.rep[a]["ri"] * w).sum() / n) if n > 0 else np.nan
        cnts = np.array([float(v @ w) for v in Gr.rep_auth[a].values()])
        cnts = cnts[cnts > 0]
        if cnts.sum() > 0 and Np > 1:
            p = cnts / cnts.sum()
            bo = float(np.exp(-(p * np.log(p)).sum()) / (Np - 1))
        else:
            bo = 0.0 if n > 0 else np.nan
        rows.append({"agent": a, "n": n, "n_exposed": nexp, "chi": chi, "lam": lam, "kappa": kap, "RO": ro,
                     "BO": bo, "RI": ri})
    return pl.DataFrame(rows)


def pct(x: np.ndarray) -> np.ndarray:
    """Rank percentile (0 lowest, 1 highest) among finite entries; NaN elsewhere."""
    x = np.asarray(x, float)
    out = np.full(len(x), np.nan)
    m = np.isfinite(x)
    if m.sum() < 2:
        return out
    from scipy.stats import rankdata
    out[m] = (rankdata(x[m]) - 1) / (m.sum() - 1)
    return out


def bootstrap(Gr: Grams, w0: np.ndarray, B: int = 100, rng=None, **kw):
    """Block bootstrap among blocks with w0 > 0. Returns list of estimate frames."""
    rng = np.random.default_rng(0) if rng is None else rng
    idx = np.flatnonzero(w0 > 0)
    out = []
    for _ in range(B):
        pick = rng.choice(idx, len(idx), replace=True)
        w = np.bincount(pick, None, len(w0)).astype(float)
        out.append(estimate(Gr, w, **kw))
    return out


# ------------------------------------------------------------------------------------------------ loader + verify
def load_unit(data_dir: Path, goal: int, model: str, unit: str | None = None):
    """Read a period's targets/reads (H65 scheme layout: <data_dir>/G<NN>/) and the vectors (H65 run.load_period)."""
    d = Path(data_dir) / f"G{goal:02d}"
    tg = pl.read_parquet(d / "targets.parquet").filter(pl.col("t_call").is_not_null())
    rd = pl.read_parquet(d / "reads.parquet")
    if unit is not None:
        tg = tg.filter(pl.col("unit_id") == unit)
        rd = rd.join(tg.select("tgt"), on="tgt", how="semi")
    Zs, pos, Hm, hpos, regime = load_vectors(goal, model, tg, rd)
    return tg, rd, Zs, pos, Hm, hpos, regime


VERIFY_UNITS = [(26, None), (38, None), (41, None), (12, None), (2, None), (51, "51c")]
COLS = ["n", "n_exposed", "chi", "lam", "kappa", "RO", "BO", "RI"]


def verify(units=VERIFY_UNITS, models=("bge_small", "gte_modernbert", "style"), tol: float = 1e-9) -> dict:
    """Recompute H65's replication point estimates (all blocks, w = 1) and compare with
    data/processed/H65-leaders-are-routers/replication/<model>/agents.parquet (read-only)."""
    res, ok = {}, True
    for model in models:
        ref = pl.read_parquet(H65 / "replication" / model / "agents.parquet")
        for g, u in units:
            key = f"{model}/{u or g}"
            r = ref.filter((pl.col("goal") == g) & (pl.col("unit") == (u or f"{g}"))).sort("agent")
            if r.height == 0:
                res[key] = "not in H65 replication"
                continue
            tg, rd, Zs, pos, Hm, hpos, regime = load_unit(H65, g, model, u)
            Gr =build_grams(build_design(tg, rd, Zs, pos, Hm, hpos))
            E = estimate(Gr, np.ones(len(Gr.blocks))).sort("agent")
            if E["agent"].to_list() != r["agent"].to_list():
                res[key] = {"agents_differ": [E.height, r.height]}
                ok = False
                continue
            dmax = 0.0
            for c in COLS:
                a, b = E[c].to_numpy().astype(float), r[c].to_numpy().astype(float)
                if not np.array_equal(np.isnan(a), np.isnan(b)):
                    dmax = np.inf
                    break
                m = ~np.isnan(a)
                if m.any():
                    dmax = max(dmax, float(np.max(np.abs(a[m] - b[m]) / np.maximum(1.0, np.abs(b[m])))))
            res[key] = {"agents": E.height, "max_rel_diff": dmax, "identical": dmax == 0.0}
            ok &= dmax <= tol
    res["ok"] = bool(ok)
    print(json.dumps(res, indent=1, default=str), flush=True)
    return res


if __name__ == "__main__":
    if "--verify" in sys.argv:
        sys.exit(0 if verify()["ok"] else 1)
    print(__doc__)
