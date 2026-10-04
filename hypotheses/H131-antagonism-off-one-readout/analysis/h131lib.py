"""H131 library: read-gated settlement DiD, read-out relaxation kernel, switch-on kernel, permutation and cluster
bootstrap inference, and the synthetic stance worlds on the real reply skeleton.

The outcome y is binary (`disagree_validated_agent`) or soft (`p_disagree`). The DiD is a linear probability model
with speaker, target and debate x phase fixed effects (H64's design, on the read-gated prize state).
"""
from __future__ import annotations

import math

import numpy as np
import polars as pl

LOGIT = lambda p: math.log(p / (1 - p))  # noqa: E731


# ============================================================================================ data
class G12:
    """Arrays for the #12 replies (one row per reply)."""

    def __init__(self, rep: pl.DataFrame, reads: pl.DataFrame, outcome="y", period="12"):
        self.period = period
        d = rep.filter((pl.col("period") == period) & pl.col("phase").is_not_null()).sort("unit", "tB")
        if period == "26":
            d = d.with_columns(pl.col("phase").replace({"open": "deb", "settled": "post"}))
        self.df = d
        self.units = sorted(d["unit"].unique().to_list())
        umap = {u: n for n, u in enumerate(self.units)}
        self.u = np.array([umap[x] for x in d["unit"].to_list()])
        self.j = d["j"].to_numpy().astype(int)
        self.i = d["i"].to_numpy().astype(int)
        self.phase = np.array(d["phase"].to_list())
        self.read = d["read"].to_numpy()
        self.k = d["k"].fill_null(0).to_numpy()
        self.k_on = d["k_on"].fill_null(0).to_numpy()
        self.R = d["R"].to_numpy().astype(int)
        self.y = d[outcome].to_numpy().astype(float)
        self.tB = d["tB"].dt.epoch("us").to_numpy() / 1e6
        self.tv = d["t_verdict"].dt.epoch("us").to_numpy() / 1e6
        # sides per debate (for permutations)
        rr = reads.filter(pl.col("goal_no") == int(period))
        self.sides = {}
        for u in self.units:
            s = rr.filter(pl.col("unit") == u)
            self.sides[umap[u]] = dict(zip(s["agent"].to_list(), s["team"].to_list()))
        self.open = (self.phase != "post") | ((self.phase == "post") & ~self.read)
        # first post-read reply of each speaker to a rival in each unit (Amendment A1: the kernel's k = 1 cell held
        # 6 replies, so "first post-read rival reply" replaces "k = 1"); same for the switch-on after the assignment
        self.first = self._first((self.R == 1) & (self.phase == "post") & self.read)
        self.first_on = self._first((self.R == 1) & (self.phase != "post") & (self.k_on >= 1))

    def _first(self, mask):
        out = np.zeros(len(mask), bool)
        seen = set()
        for n in np.argsort(self.tB, kind="stable"):
            if mask[n] and (self.u[n], self.j[n]) not in seen:
                seen.add((self.u[n], self.j[n]))
                out[n] = True
        return out

    def R_from(self, sides):
        if self.period == "26":
            return np.array([int(sides[u].get(j) == "rival" and sides[u].get(i) == "rival")
                             for u, j, i in zip(self.u, self.j, self.i)])
        return np.array([int(sides[u][j] != sides[u][i]) for u, j, i in zip(self.u, self.j, self.i)])

    def permuted_sides(self, rng):
        out = {}
        for u, s in self.sides.items():
            ag = list(s)
            labs = [s[a] for a in ag]
            rng.shuffle(labs)
            out[u] = dict(zip(ag, labs))
        return out


# ============================================================================================ DiD
def _design(j, i, cell, cols):
    """Dummy matrix: one-hot speaker, target (drop first), cell (debate x phase; drop first), plus extra columns."""
    blocks = []
    for v in (j, i, cell):
        uv, inv = np.unique(v, return_inverse=True)
        M = np.zeros((len(v), len(uv)))
        M[np.arange(len(v)), inv] = 1
        blocks.append(M)
    X = np.hstack([blocks[0], blocks[1][:, 1:], blocks[2][:, 1:]] + [c[:, None] for c in cols])
    return X


def did(y, R, O, j, i, cell):
    """LPM y ~ FE(j) + FE(i) + FE(cell) + R + R*O. O must be constant within cell or nearly so (absorbed).
    Returns (Delta = coef on R*O, gamma_set = coef on R, gamma_open = gamma_set + Delta)."""
    X = _design(j, i, cell, [R.astype(float), (R * O).astype(float)])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    g_set, delta = beta[-2], beta[-1]
    return float(delta), float(g_set), float(g_set + delta)


def g12_cell(g: G12):
    return g.u * 10 + np.select([g.phase == "pre", g.phase == "deb", g.phase == "post"], [0, 1, 2], 3)


def g12_did(g: G12, y=None, R=None):
    y = g.y if y is None else y
    R = g.R if R is None else R
    return did(y, R, g.open.astype(int), g.j, g.i, g12_cell(g))


def g12_perm(g: G12, rng, B=5000, y=None):
    y = g.y if y is None else y
    obs = g12_did(g, y)[0]
    null = np.empty(B)
    for b in range(B):
        null[b] = g12_did(g, y, g.R_from(g.permuted_sides(rng)))[0]
    # one-sided: the conflict flag predicts Delta > 0 (more disagreement between rivals while the prize is open)
    return obs, null, float((np.sum(null >= obs) + 1) / (B + 1))


def cluster_boot(g: G12, stat, rng, B=1000):
    """Resample debates with replacement; stat(idx) -> float or tuple."""
    U = len(g.units)
    out = []
    for _ in range(B):
        if U == 1:   # one structural unit (#26): resample replies within phase
            idx = np.concatenate([rng.choice(np.flatnonzero(g.phase == ph), (g.phase == ph).sum())
                                  for ph in np.unique(g.phase)])
        else:
            pick = rng.integers(0, U, U)
            idx = np.concatenate([np.flatnonzero(g.u == p) for p in pick])
        try:
            out.append(stat(idx))
        except Exception:
            continue
    return np.array(out)


def did_idx(g: G12, idx, y=None):
    y = g.y if y is None else y
    # re-key debates so repeated draws are distinct cells
    cell = g12_cell(g)[idx] + 1000 * np.arange(len(idx)) * 0
    return did(y[idx], g.R[idx], g.open[idx].astype(int), g.j[idx], g.i[idx], cell)


# ============================================================================================ kernels
def kernel_stats(g: G12, y=None):
    """Read-out relaxation kernel (post phase, read replies) and the open rate."""
    y = g.y if y is None else y
    riv = g.R == 1
    post_read = (g.phase == "post") & g.read
    k1 = g.first
    k2 = riv & post_read & ~g.first
    op = riv & (g.phase == "deb")
    mate_post = (g.R == 0) & post_read
    m = lambda s: float(y[s].mean()) if s.sum() else np.nan  # noqa: E731
    return dict(r_k1=m(k1), r_k2=m(k2), r_open=m(op), r_mate_post=m(mate_post), n_k1=int(k1.sum()), n_k2=int(k2.sum()),
                n_open=int(op.sum()), n_mate_post=int(mate_post.sum()))


def kernel_tests(g: G12, rng, B=2000, y=None):
    y = g.y if y is None else y
    ks = kernel_stats(g, y)
    riv = g.R == 1
    k1 = g.first
    op = riv & (g.phase == "deb")
    # permutation of group labels (open vs k1) within debates: statistic r_open - r_k1
    pool = np.flatnonzero(k1 | op)
    lab = op[pool].copy()
    uu = g.u[pool]
    obs = ks["r_open"] - ks["r_k1"]
    null = np.empty(B)
    for b in range(B):
        lb = lab.copy()
        for u in np.unique(uu):
            s = np.flatnonzero(uu == u)
            lb[s] = rng.permutation(lb[s])
        yo, yk = y[pool][lb], y[pool][~lb]
        null[b] = (yo.mean() if len(yo) else 0) - (yk.mean() if len(yk) else 0)
    p_open_gt_k1 = float((np.sum(null >= obs) + 1) / (B + 1))
    bs = cluster_boot(g, lambda idx: _kdiff(g, idx, y), rng, B=1000)
    bs = bs[np.isfinite(bs)]
    lo, hi = (np.percentile(bs, [5, 95]) if len(bs) > 20 else (np.nan, np.nan))
    return dict(**ks, d_k1_k2=ks["r_k1"] - ks["r_k2"], d_k1_k2_lo=float(lo), d_k1_k2_hi=float(hi),
                d_open_k1=obs, p_open_gt_k1=p_open_gt_k1)


def _kdiff(g, idx, y):
    riv = g.R[idx] == 1
    pr = (g.phase[idx] == "post") & g.read[idx]
    a = g.first[idx]
    b = riv & pr & ~g.first[idx]
    if a.sum() == 0 or b.sum() == 0:
        return np.nan
    return y[idx][a].mean() - y[idx][b].mean()


def switch_on_tests(g: G12, rng, y=None):
    """Rival rate at k_on = 1 (first post-read talk call after the team assignment, pre or deb phase) vs the deb-phase
    rival rate at k_on >= 2."""
    y = g.y if y is None else y
    riv = g.R == 1
    on1 = g.first_on
    later = riv & (g.phase == "deb") & ~g.first_on

    def st(idx):
        a = on1[idx]
        b = later[idx]
        if a.sum() == 0 or b.sum() == 0:
            return np.nan
        return y[idx][a].mean() - y[idx][b].mean()
    obs = st(np.arange(len(y)))
    bs = cluster_boot(g, st, rng, B=1000)
    bs = bs[np.isfinite(bs)]
    lo, hi = (np.percentile(bs, [5, 95]) if len(bs) > 20 else (np.nan, np.nan))
    return dict(r_on1=float(y[on1].mean()) if on1.sum() else np.nan, r_deb_later=float(y[later].mean()) if later.sum() else np.nan,
                n_on1=int(on1.sum()), n_deb_later=int(later.sum()), d_on=float(obs), d_on_lo=float(lo), d_on_hi=float(hi))


# ============================================================================================ synthetic
def simulate_g12(g: G12, world, rng, p_base=0.03, p_open=0.3, rho=None, eps=None, sd_agent=0.4):
    """Latent conflict on the real skeleton -> observed flag through the labeller's confusion."""
    rho = rng.uniform(0.55, 0.65) if rho is None else rho
    eps = rng.uniform(0.004, 0.006) if eps is None else eps
    h = LOGIT(p_open) - LOGIT(p_base)
    agents = np.unique(np.r_[g.j, g.i])
    uj = dict(zip(agents, rng.normal(0, sd_agent, len(agents))))
    vi = dict(zip(agents, rng.normal(0, sd_agent, len(agents))))
    eta = LOGIT(p_base) + np.array([uj[a] for a in g.j]) + np.array([vi[a] for a in g.i])
    pre_on = (g.phase != "post")  # field on during pre/deb (assignment read)
    if world == "W0":
        O = np.zeros(len(g.y))
    elif world in ("W1", "W2"):   # read-gated / clock-gated at the verdict: identical partitions here
        O = (pre_on | ((g.phase == "post") & ~g.read)).astype(float) if world == "W1" else (g.tB < g.tv).astype(float)
    elif world.startswith("W3"):  # clock with a common delay (s)
        dly = float(world.split("_")[1])
        O = (g.tB < g.tv + dly).astype(float)
    elif world.startswith("W4"):  # remanence over post-read talk calls
        kap = float(world.split("_")[1])
        O = np.where(pre_on, 1.0, np.where(g.read, np.exp(-(np.maximum(g.k, 1) - 1) / kap), 1.0))
    elif world.startswith("W5"):  # clock decay
        tau = float(world.split("_")[1])
        O = np.where(pre_on, 1.0, np.exp(-np.maximum(g.tB - g.tv, 0) / tau))
    elif world == "W6":           # relation-bound: no settlement effect
        O = np.ones(len(g.y))
    elif world == "WON2":         # switch-on builds up over 3 talk calls after the assignment read
        O = np.where(pre_on, 1 - np.exp(-np.maximum(g.k_on, 0) / 3.0), 0.0)
    else:
        raise ValueError(world)
    eta = eta + h * g.R * O
    z = rng.random(len(eta)) < 1 / (1 + np.exp(-eta))
    y = np.where(z, rng.random(len(eta)) < rho, rng.random(len(eta)) < eps).astype(float)
    return y
