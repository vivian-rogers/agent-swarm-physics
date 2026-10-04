"""H76 period pipeline: the same code runs on real `load_v3` days and on synthetic days.

A `days` dict maps a date key -> {'agents', 'X' (n_ag, n_win, n_states), 'span' (n_ag, n_win) bool}.
"""
from __future__ import annotations

import numpy as np

import h76lib as L

KICK_STEPS = 24      # 2 active hours of 5-min steps
DECAY_BLOCK = 12     # 1 active hour
DECAY_HOURS = 20


def _blocks_for_day(day, trimmed, size=6):
    return L.chunk_steps(L.steps_of(day, trimmed), size)


class Block:
    __slots__ = ("kind", "Jper", "M", "raw", "floor", "p95")

    def __init__(self, day, steps, rng, R, alpha):
        Jper = L.block_flux(day, steps)
        self.Jper = Jper
        self.M = len(steps)                       # steps per agent
        self.raw, self.floor, self.p95 = L.eval_block(Jper, self.M * Jper.shape[0], rng, R, alpha)

    def value(self, w=None, alpha=L.ALPHA, rng=None, Rb=5):
        """Debiased (sigma, sigma_ex, sigma_hk) per agent-step and the agent-steps; w = agent weights (bootstrap).
        With weights, the block-flip floor is recomputed on the weighted sample (Rb surrogates): duplicated agents
        raise the plug-in bias, so the full-sample floor would under-correct (amendment A2)."""
        if w is None:
            return np.asarray(self.raw) - self.floor, self.M * self.Jper.shape[0]
        Mtot = self.M * w.sum()
        if Mtot <= 0:
            return np.full(3, np.nan), 0.0
        J = np.tensordot(w, self.Jper, 1)
        raw = np.asarray(L.split(J, Mtot, alpha))
        rng = np.random.default_rng() if rng is None else rng
        JT = np.transpose(self.Jper, (0, 2, 1))
        fl = np.zeros(3)
        for _ in range(Rb):
            s = rng.random(len(w)) < 0.5
            Js = np.tensordot(w * s, self.Jper, 1) + np.tensordot(w * ~s, JT, 1)
            fl += np.asarray(L.split(Js, Mtot, alpha))
        return raw - fl / Rb, Mtot


def build_blocks(days: dict, kickoff_key, rng, R=20, alpha=L.ALPHA):
    """All blocks needed for the period statistics."""
    keys = list(days)
    out = {"kick": None, "dstart": {}, "untrim": {}, "trim": {}, "decay": []}
    for k in keys:
        d = days[k]
        ts = L.steps_of(d, True)
        if len(ts) >= KICK_STEPS:
            b = Block(d, ts[:KICK_STEPS], rng, R, alpha)
            if k == kickoff_key:
                out["kick"] = b
            else:
                out["dstart"][k] = b
        if k != kickoff_key:
            out["untrim"][k] = [(kind, Block(d, s, rng, R, alpha)) for kind, s in _blocks_for_day(d, False)]
            out["trim"][k] = [(kind, Block(d, s, rng, R, alpha)) for kind, s in _blocks_for_day(d, True)]
    # decay: hourly trimmed blocks from the kickoff, through DECAY_HOURS active hours
    i0 = keys.index(kickoff_key) if kickoff_key in keys else None
    if i0 is not None:
        need = DECAY_HOURS
        for k in keys[i0:]:
            ts = L.steps_of(days[k], True)
            for j in range(len(ts) // DECAY_BLOCK):
                if need == 0:
                    break
                out["decay"].append((k, Block(days[k], ts[j * DECAY_BLOCK:(j + 1) * DECAY_BLOCK], rng, R, alpha)))
                need -= 1
            if need == 0:
                break
    return out


def _w_for(day_agents, wmap):
    if wmap is None:
        return None
    return np.array([wmap.get(a, 0.0) for a in day_agents], float)


def fit_decay(y: np.ndarray, t: np.ndarray):
    """y = c + A exp(-t/tau), least squares over a tau grid; returns (tau, A, c, rss)."""
    best = (np.nan, np.nan, np.nan, np.inf)
    ok = np.isfinite(y)
    if ok.sum() < 5:
        return best
    for tau in np.geomspace(0.25, 40, 120):
        X = np.c_[np.ones(ok.sum()), np.exp(-t[ok] / tau)]
        coef, *_ = np.linalg.lstsq(X, y[ok], rcond=None)
        r = float(((X @ coef - y[ok]) ** 2).sum())
        if r < best[3]:
            best = (tau, coef[1], coef[0], r)
    return best


def stats(blocks, days, kick_key, wmap=None, rng=None):
    """Period statistics from built blocks; wmap: agent -> bootstrap weight (None = original sample)."""
    res = {}
    # kickoff and day-start placebo (trimmed, 2 h)
    def val(b, k):
        return b.value(_w_for(days[k]["agents"], wmap), rng=rng)[0]
    if blocks["kick"] is not None:
        v = val(blocks["kick"], kick_key)
        res["kick_sigma"], res["kick_ex"], res["kick_hk"] = map(float, v)
        res["kick_share"] = float(v[1] / v[0]) if v[0] > 0 else np.nan
        res["kick_sigma_db"] = float(v[0])
        ds = np.array([val(b, k) for k, b in blocks["dstart"].items()])
        if len(ds):
            res["dstart_ex_median"] = float(np.median(ds[:, 1]))
            res["dstart_ex_max"] = float(ds[:, 1].max())
            res["dstart_share_median"] = float(np.median(ds[:, 1] / np.where(ds[:, 0] > 0, ds[:, 0], np.nan)))
            res["kick_ratio"] = float(v[1] / res["dstart_ex_median"]) if res["dstart_ex_median"] > 0 else np.nan
            res["kick_rank"] = float((ds[:, 1] < v[1]).mean())   # share of day starts below the kickoff
    # decay
    if blocks["decay"]:
        y = np.array([val(b, k)[1] for k, b in blocks["decay"]])
        t = np.arange(len(y)) + 0.5
        tau, A, c, _ = fit_decay(y, t)
        res.update(decay_tau=float(tau), decay_A=float(A), decay_c=float(c), decay_y=y.tolist())
    # per-day sums (debiased, agent-steps weighted): edge share, trimming, housekeeping share; pooled over days
    D = []
    for k in blocks["untrim"]:
        w = _w_for(days[k]["agents"], wmap)
        U = [(kind, *b.value(w, rng=rng)) for kind, b in blocks["untrim"][k]]
        T = [(kind, *b.value(w, rng=rng)) for kind, b in blocks["trim"][k]]
        if not U:
            continue
        isE = np.array([kind in ("start", "end") for kind, _, _ in U])
        su = np.array([v * m for _, v, m in U])          # (blocks, 3) totals in nats
        st = np.array([v * m for _, v, m in T]) if T else np.full((1, 3), np.nan)
        D.append(dict(day=k, ex_u=su[:, 1].sum(), ex_edge=su[isE, 1].sum(), hk_u=su[:, 2].sum(), s_u=su[:, 0].sum(),
                      ex_t=st[:, 1].sum(), hk_t=st[:, 2].sum(), s_t=st[:, 0].sum(), has_t=bool(T),
                      m_t=sum(m for _, _, m in T) if T else 0.0, m_u=sum(m for _, _, m in U),
                      n_ag=len(days[k]["agents"])))
    if D:
        g = {c: np.array([d[c] for d in D]) for c in D[0] if c != "day"}
        t = g["has_t"].astype(bool)
        res.update(edge_share=float(g["ex_edge"].sum() / g["ex_u"].sum()),
                   trim_rm_ex=float(1 - g["ex_t"][t].sum() / g["ex_u"][t].sum()),
                   trim_rm_hk=float(1 - g["hk_t"][t].sum() / g["hk_u"][t].sum()),
                   trim_rm_steps=float(1 - g["m_t"][t].sum() / g["m_u"][t].sum()),
                   hk_share=float(g["hk_t"][t].sum() / g["s_t"][t].sum()),
                   hk_per_step=float(g["hk_t"][t].sum() / g["m_t"][t].sum()),
                   ex_per_step_trim=float(g["ex_t"][t].sum() / g["m_t"][t].sum()),
                   ex_per_step_untrim=float(g["ex_u"].sum() / g["m_u"].sum()),
                   hk_per_step_untrim=float(g["hk_u"].sum() / g["m_u"].sum()),
                   edge_share_day_median=float(np.median(g["ex_edge"] / g["ex_u"])),
                   n_days=len(D), n_days_trimmed=int(t.sum()), days=[d["day"] for d in D],
                   ex_edge_by_day=g["ex_edge"].tolist(), ex_day_untrim=g["ex_u"].tolist(), n_agents_by_day=g["n_ag"].tolist(),
                   hk_day_trim=[float(x) if h else float("nan") for x, h in zip(g["hk_t"], t)],
                   steps_day_trim=g["m_t"].tolist(), hk_day_untrim=g["hk_u"].tolist(), steps_day_untrim=g["m_u"].tolist())
    return res


def edge_time_share(days, kickoff_key):
    sh = []
    for k, d in days.items():
        if k == kickoff_key:
            continue
        n = d["X"].shape[1] - 1
        sh.append(min(12, n) / n if n > 0 else np.nan)
    return float(np.nanmedian(sh)) if sh else np.nan


def bootstrap(blocks, days, kick_key, B, rng):
    ags = sorted({a for d in days.values() for a in d["agents"]})
    keys = ["kick_share", "kick_ratio", "kick_ex", "edge_share", "trim_rm_ex", "trim_rm_hk", "trim_rm_steps", "hk_share", "hk_per_step",
            "decay_tau"]
    out = {k: [] for k in keys}
    for _ in range(B):
        draw = rng.choice(len(ags), len(ags), replace=True)
        cnt = np.bincount(draw, minlength=len(ags))
        wmap = {a: float(c) for a, c in zip(ags, cnt)}
        s = stats(blocks, days, kick_key, wmap, rng)
        for k in keys:
            out[k].append(s.get(k, np.nan))
    return {k: [float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))] if np.isfinite(v).any() else [np.nan, np.nan]
            for k, v in ((k, np.array(v, float)) for k, v in out.items())}
