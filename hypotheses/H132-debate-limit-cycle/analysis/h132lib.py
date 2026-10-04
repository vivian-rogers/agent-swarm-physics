"""H132 estimators: turn alternation of the issue projection in #12 debates, with a turn-shuffled null.

Turn = maximal run of consecutive debater messages from one team inside one (debate, phase). Turn vector = mean of
the run's whitened message vectors; y_a = projection on the issue axis a_d, y_g = on the topic axis g_d.
z = team-centred y within (debate, phase). Statistics (card O1-O5):
  rho1, rho2  pooled lag-1 / lag-2 correlation of z over turns (sums of products over sums of squares)
  Lam         rho2 - rho1
  A           rho1 over (Gov turn -> Opp turn) minus rho1 over (Opp -> Gov)
  L           mean signed area per turn in the (a, g) plane (standardized per debate)
  rho1_vec    lag-1 correlation of team-centred 32-d turn vectors (topic channel)
  rho_same, rho_cross  message-level lag-1 correlations for same-team / cross-team consecutive messages
Null: permute turn contents within (debate, phase, team); message null: permute message contents within the same.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

from dataclasses import dataclass  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/processed/H132-debate-limit-cycle/G12"


@dataclass
class Msgs:
    df: pl.DataFrame          # debater messages (sorted by debate, t), columns debate, phase, team, agent, t, t_call_prod
    X: np.ndarray             # 32-d whitened vectors
    a: dict                   # debate -> issue axis
    g: dict                   # debate -> topic axis


def load(model: str = "bge_small", src: str = "masked") -> Msgs:
    df = pl.read_parquet(DATA / "messages.parquet")
    X = np.load(DATA / f"msg_white_{model}_{src}.npy").astype(np.float64)
    ax = np.load(DATA / f"axes_{model}.npz")
    a = {int(d): v for d, v in zip(ax["debates"], ax["a"])}
    g = {int(d): v for d, v in zip(ax["debates"], ax["g"])}
    keep = np.isfinite(X).all(1)
    return Msgs(df=df.with_row_index("r").filter(pl.Series(keep)), X=X, a=a, g=g)


@dataclass
class Turns:
    debate: np.ndarray
    phase: np.ndarray
    team: np.ndarray
    blk: np.ndarray           # block id (debate, phase)
    ya: np.ndarray
    yg: np.ndarray
    V: np.ndarray             # turn vectors
    vis: np.ndarray           # responding turn's first message produced after the previous turn's last message (N2)
    first_agent: np.ndarray
    last_agent: np.ndarray


def turns(M: Msgs, phases=("deb",), ya_msg: np.ndarray | None = None, yg_msg: np.ndarray | None = None) -> Turns:
    """Collapse runs. ya_msg/yg_msg override the message projections (synthetic)."""
    df = M.df.filter(pl.col("phase").is_in(list(phases))).sort("debate", "phase", "t")
    r = df["r"].to_numpy()
    deb, ph, tm, ag = df["debate"].to_numpy(), df["phase"].to_numpy(), df["team"].to_numpy(), df["agent"].to_numpy()
    t = df["t"].dt.epoch("us").to_numpy() / 1e6
    tcp = df["t_call_prod"].dt.epoch("us").to_numpy() / 1e6
    X = M.X[r] if ya_msg is None else None
    if ya_msg is None:
        ya = np.array([X[k] @ M.a[int(d)] for k, d in enumerate(deb)])
        yg = np.array([X[k] @ M.g[int(d)] for k, d in enumerate(deb)])
    else:
        ya, yg = ya_msg[r], yg_msg[r]
    out = {k: [] for k in ("debate", "phase", "team", "ya", "yg", "V", "vis", "fa", "la")}
    i = 0
    n = len(r)
    prev_end_t = None
    prev_key = None
    while i < n:
        j = i
        while j + 1 < n and deb[j + 1] == deb[i] and ph[j + 1] == ph[i] and tm[j + 1] == tm[i]:
            j += 1
        key = (deb[i], ph[i])
        out["debate"].append(deb[i]); out["phase"].append(ph[i]); out["team"].append(tm[i])
        out["ya"].append(ya[i:j + 1].mean()); out["yg"].append(yg[i:j + 1].mean())
        out["V"].append(X[i:j + 1].mean(0) if X is not None else np.zeros(1))
        out["vis"].append(bool(prev_key == key and prev_end_t is not None and tcp[i] > prev_end_t))
        out["fa"].append(ag[i]); out["la"].append(ag[j])
        prev_end_t, prev_key = t[j], key
        i = j + 1
    blk_keys = {k: b for b, k in enumerate(sorted(set(zip(out["debate"], out["phase"]))))}
    return Turns(debate=np.array(out["debate"]), phase=np.array(out["phase"]), team=np.array(out["team"]),
                 blk=np.array([blk_keys[k] for k in zip(out["debate"], out["phase"])]), ya=np.array(out["ya"]),
                 yg=np.array(out["yg"]), V=np.vstack(out["V"]), vis=np.array(out["vis"]),
                 first_agent=np.array(out["fa"]), last_agent=np.array(out["la"]))


def _centre(y, blk, team, detrend=False):
    z = y.astype(float).copy()
    for b in np.unique(blk):
        for s in (1, -1):
            m = (blk == b) & (team == s)
            if m.any():
                z[m] -= z[m].mean()
        if detrend:
            m = blk == b
            if m.sum() > 3:
                x = np.arange(m.sum())
                c = np.polyfit(x, z[m], 1)
                z[m] -= np.polyval(c, x) - np.polyval(c, x).mean()
    return z


def _pairs(blk, lag):
    i = np.arange(len(blk) - lag)
    return i[blk[i] == blk[i + lag]]


def _corr(z, i, j):
    den = np.sqrt((z[i] ** 2).sum() * (z[j] ** 2).sum())
    return float((z[i] * z[j]).sum() / den) if den > 0 else np.nan


def stats(T: Turns, ya=None, yg=None, V=None, detrend=False) -> dict:
    ya = T.ya if ya is None else ya
    yg = T.yg if yg is None else yg
    z = _centre(ya, T.blk, T.team, detrend)
    w = _centre(yg, T.blk, T.team, detrend)
    p1, p2 = _pairs(T.blk, 1), _pairs(T.blk, 2)
    r1, r2 = _corr(z, p1, p1 + 1), _corr(z, p2, p2 + 2)
    go = p1[T.team[p1] == 1]
    og = p1[T.team[p1] == -1]
    out = {"rho1": r1, "rho2": r2, "Lam": r2 - r1, "A": _corr(z, go, go + 1) - _corr(z, og, og + 1),
           "n1": len(p1), "n2": len(p2)}
    # cycle area in (a, g), standardized per block
    zs, ws = z.copy(), w.copy()
    for b in np.unique(T.blk):
        m = T.blk == b
        zs[m] /= max(z[m].std(), 1e-9)
        ws[m] /= max(w[m].std(), 1e-9)
    out["L"] = float(np.mean(zs[p1] * ws[p1 + 1] - ws[p1] * zs[p1 + 1])) if len(p1) else np.nan
    # visibility split (N2)
    vis = T.vis[p1 + 1]
    out["rho1_vis"] = _corr(z, p1[vis], p1[vis] + 1) if vis.sum() > 2 else np.nan
    out["rho1_if"] = _corr(z, p1[~vis], p1[~vis] + 1) if (~vis).sum() > 2 else np.nan
    out["dRho_vis"] = out["rho1_vis"] - out["rho1_if"]
    out["n_vis"], out["n_if"] = int(vis.sum()), int((~vis).sum())
    V = T.V if V is None else V
    if V.shape[1] > 1:
        Vc = V.copy()
        for b in np.unique(T.blk):
            for s in (1, -1):
                m = (T.blk == b) & (T.team == s)
                if m.any():
                    Vc[m] -= Vc[m].mean(0)
        num = (Vc[p1] * Vc[p1 + 1]).sum()
        out["rho1_vec"] = float(num / np.sqrt((Vc[p1] ** 2).sum() * (Vc[p1 + 1] ** 2).sum()))
    return out


def perm_index(blk, team, rng):
    """Permutation of turn indices within (block, team)."""
    p = np.arange(len(blk))
    for b in np.unique(blk):
        for s in (1, -1):
            m = np.flatnonzero((blk == b) & (team == s))
            if len(m) > 1:
                p[m] = m[rng.permutation(len(m))]
    return p


def shuffle_test(T: Turns, n_perm=5000, seed=0, detrend=False, keys=("rho1", "rho2", "Lam", "A", "L", "rho1_vec",
                                                                       "dRho_vis")) -> dict:
    obs = stats(T, detrend=detrend)
    rng = np.random.default_rng(seed)
    null = {k: [] for k in keys}
    for _ in range(n_perm):
        p = perm_index(T.blk, T.team, rng)
        s = stats(T, T.ya[p], T.yg[p], T.V[p], detrend=detrend)
        for k in keys:
            null[k].append(s.get(k, np.nan))
    res = {"obs": obs}
    for k in keys:
        nv = np.array(null[k], float)
        o = obs.get(k, np.nan)
        if not np.isfinite(o) or not np.isfinite(nv).any():
            continue
        nv = nv[np.isfinite(nv)]
        res[k] = {"obs": o, "null_mean": float(nv.mean()), "null_sd": float(nv.std()),
                  "p_lo": float((1 + (nv <= o).sum()) / (1 + len(nv))), "p_hi": float((1 + (nv >= o).sum()) / (1 + len(nv))),
                  "p_two": float((1 + (np.abs(nv - nv.mean()) >= abs(o - nv.mean())).sum()) / (1 + len(nv))),
                  "q05": float(np.quantile(nv, 0.05)), "q95": float(np.quantile(nv, 0.95))}
    return res


def message_level(M: Msgs, phase="deb", ya_msg=None, n_perm=5000, seed=1) -> dict:
    """O3 and N3 at message level: team-centred message projections, consecutive pairs within (debate, phase)."""
    df = M.df.filter(pl.col("phase") == phase).sort("debate", "t")
    r = df["r"].to_numpy()
    deb, tm, ag = df["debate"].to_numpy(), df["team"].to_numpy(), df["agent"].to_numpy()
    y = np.array([M.X[k] @ M.a[int(d)] for k, d in zip(r, deb)]) if ya_msg is None else ya_msg[r]
    blk = deb
    def st(yv):
        z = _centre(yv, blk, tm)
        p = _pairs(blk, 1)
        same = p[tm[p] == tm[p + 1]]
        cross = p[tm[p] != tm[p + 1]]
        out = {"rho_same": _corr(z, same, same + 1), "rho_cross": _corr(z, cross, cross + 1),
               "n_same": len(same), "n_cross": len(cross)}
        # N3 within-pair re-drafting: pairs (a then b), a != b
        q = p[ag[p] != ag[p + 1]]
        prod = z[q] * z[q + 1]
        opp = tm[q] != tm[q + 1]
        key = np.minimum(ag[q], ag[q + 1]) * 100 + np.maximum(ag[q], ag[q + 1])
        diffs = []
        for k in np.unique(key):
            m = key == k
            if (m & opp).sum() >= 1 and (m & ~opp).sum() >= 1:
                diffs.append(prod[m & opp].mean() - prod[m & ~opp].mean())
        out["N3_contrast"] = float(np.mean(diffs)) if diffs else np.nan
        out["N3_pairs"] = len(diffs)
        out["N3_diffs"] = diffs
        return out
    obs = st(y)
    rng = np.random.default_rng(seed)
    nulls = {"rho_same": [], "rho_cross": [], "N3_contrast": []}
    for _ in range(n_perm):
        yp = y.copy()
        for b in np.unique(blk):
            for s in (1, -1):
                m = np.flatnonzero((blk == b) & (tm == s))
                yp[m] = y[m][rng.permutation(len(m))]
        s = st(yp)
        for k in nulls:
            nulls[k].append(s[k])
    res = {"obs": {k: v for k, v in obs.items() if k != "N3_diffs"}}
    for k, nv in nulls.items():
        nv = np.array(nv)
        nv = nv[np.isfinite(nv)]
        o = obs[k]
        res[k] = {"obs": o, "null_mean": float(nv.mean()), "p_lo": float((1 + (nv <= o).sum()) / (1 + len(nv))),
                  "p_hi": float((1 + (nv >= o).sum()) / (1 + len(nv)))}
    d = np.array(obs["N3_diffs"])
    if len(d):
        flips = np.array([np.mean(d * rng.choice([-1, 1], len(d))) for _ in range(n_perm)])
        res["N3_signflip_p_lo"] = float((1 + (flips <= d.mean()).sum()) / (1 + n_perm))
    return res


def per_debate(T: Turns) -> list[dict]:
    out = []
    for d in np.unique(T.debate):
        m = T.debate == d
        sub = Turns(debate=T.debate[m], phase=T.phase[m], team=T.team[m], blk=T.blk[m], ya=T.ya[m], yg=T.yg[m],
                    V=T.V[m], vis=T.vis[m], first_agent=T.first_agent[m], last_agent=T.last_agent[m])
        s = stats(sub)
        raw = float(T.ya[m][T.team[m] == 1].mean() - T.ya[m][T.team[m] == -1].mean())
        out.append({"debate": int(d), "turns": int(m.sum()), "rho1": s["rho1"], "rho2": s["rho2"], "Lam": s["Lam"],
                    "gov_minus_opp": raw})
    return out
