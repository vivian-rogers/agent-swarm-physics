"""H70 helpers: event frames per channel and scale, rows of the kappa table, return probabilities.

The estimator itself is shared: infra/shared/semantic_kappa.py (kappa_row, mi_corrected, did_value, dl_pool).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
import semantic_kappa as K  # noqa: E402

OUT = ROOT / "data/processed/H70-artifact-store-semantic-info"
SCALES = {"call": ("F", "P"), "day": ("N", "PN")}
CHANNELS = {"A": ("A_prev", "openA"), "M": ("S_M", "openM"), "R": ("S_R", "openR")}
MIN_WIN = 10


def load_events(path: Path | None = None) -> pl.DataFrame:
    ev = pl.read_parquet(path or OUT / "events.parquet")
    return ev.filter((pl.col("n_win") >= MIN_WIN) & pl.col("V").is_not_null())


def frame(ev: pl.DataFrame, scale: str, channel: str, need_artifact: bool = True) -> dict:
    """Event frame (numpy dict) for semantic_kappa.kappa_row. Population: events whose agent has an artifact
    (A_prev >= 0), so that every channel is compared on the same agents and moments."""
    s_type, p_type = SCALES[scale]
    e = ev.filter(pl.col("etype").is_in([s_type, p_type]))
    if need_artifact:
        e = e.filter(pl.col("A_prev") >= 0)
    scol, ocol = CHANNELS[channel]
    return {"cluster": (e["agent"].cast(pl.Utf8) + "|" + e["pt_date"]).to_numpy(),
            "stratum": (e["agent"].cast(pl.Utf8) + "|" + e["period"]).to_numpy(),
            "scramble": (e["etype"] == s_type).to_numpy(),
            "X": e["X_next"].to_numpy(), "S": e[scol].to_numpy(), "open": e[ocol].to_numpy(),
            "V": e["V"].to_numpy(), "V_pre": e["V_pre"].to_numpy()}


def context_row(ev: pl.DataFrame, scale: str, B: int = 300, n_perm: int = 200, seed: int = 0) -> dict:
    """Context row: dV_C = V(placebo) - V(scramble) with agent-period FE; I_C = I_placebo(X; S_C) - I_scramble(X; S_C)
    (each permutation-corrected within agent-period): the allocation information that only the context held."""
    s_type, p_type = SCALES[scale]
    e = ev.filter(pl.col("etype").is_in([s_type, p_type]) & (pl.col("A_prev") >= 0))
    rng = np.random.default_rng(seed)
    st = (e["agent"].cast(pl.Utf8) + "|" + e["period"]).to_numpy()
    cl = (e["agent"].cast(pl.Utf8) + "|" + e["pt_date"]).to_numpy()
    sc = (e["etype"] == s_type).to_numpy()
    X, S, V, Vp = e["X_next"].to_numpy(), e["S_C"].to_numpy(), e["V"].to_numpy(), e["V_pre"].to_numpy()

    def stat(idx, n_p, strata):
        a = K.mi_corrected(X[idx][~sc[idx]], S[idx][~sc[idx]], strata[~sc[idx]], n_perm=n_p, rng=rng)["I"]
        b = K.mi_corrected(X[idx][sc[idx]], S[idx][sc[idx]], strata[sc[idx]], n_perm=n_p, rng=rng)["I"]
        return a, b, K.scramble_cost(V[idx], sc[idx], strata, Vp[idx])["cost"]

    all_idx = np.arange(len(X))
    Ip, Is, dV = stat(all_idx, n_perm, st)
    cost = K.scramble_cost(V, sc, st, Vp)
    codes = np.unique(cl, return_inverse=True)[1]
    ncl = codes.max() + 1
    order = np.argsort(codes, kind="stable")
    members = np.split(order, np.flatnonzero(np.diff(codes[order])) + 1)
    draws = []
    for _ in range(B):
        pick = rng.integers(0, ncl, size=ncl)
        idx = np.concatenate([members[j] for j in pick])
        strata = st[idx]
        cb = K.scramble_cost(V[idx], sc[idx], strata, Vp[idx])
        draws.append(stat(idx, 8, st[idx])[:2] + (cb["cost"], cb["cost_rel"]))
    d = np.array(draws)
    Ipb = d[:, 0] - (d[:, 0].mean() - Ip)
    Isb = d[:, 1] - (d[:, 1].mean() - Is)
    IC = Ipb - Isb
    dVb = d[:, 2]
    relb = d[:, 3]
    kap = np.where(IC > 0.02, dVb / np.where(IC > 0.02, IC, 1), np.nan)

    def ci(a):
        a = a[np.isfinite(a)]
        return [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))] if len(a) > 10 else [None, None]

    I_C = Ip - Is
    return {"I_placebo": Ip, "I_scramble": Is, "I": I_C, "I_ci": ci(IC), "I_se": float(np.std(IC)),
            "dV": dV, "dV_ci": ci(dVb), "dV_se": float(np.std(dVb)),
            "dV_rel": cost["cost_rel"], "dV_rel_ci": ci(relb), "dV_rel_se": float(np.std(relb)),
            "kappa": float(dV / I_C) if I_C > 0.02 else float("nan"), "kappa_ci": ci(kap),
            "kappa_undefined_share": float(np.mean(~np.isfinite(kap))),
            "V_mean_placebo": float(np.nanmean(V[~sc])), "V_mean_scramble": float(np.nanmean(V[sc])),
            "n_scramble": int(sc.sum()), "n_placebo": int((~sc).sum()), "n_clusters": int(ncl), "B": B}


def return_prob(ev: pl.DataFrame) -> dict:
    """P(X_next = A_prev | a commit in the window, A_prev known), per event type."""
    e = ev.filter((pl.col("A_prev") >= 0) & (pl.col("X_next") >= 0))
    out = {}
    for t in ("F", "P", "N", "PN"):
        g = e.filter(pl.col("etype") == t)
        if g.height:
            out[t] = {"p_return": float((g["X_next"] == g["A_prev"]).mean()), "n": g.height}
    return out


def row_or_none(ev: pl.DataFrame, scale: str, channel: str, min_events: int = 30, **kw) -> dict | None:
    s_type, p_type = SCALES[scale]
    e = ev.filter(pl.col("etype").is_in([s_type, p_type]) & (pl.col("A_prev") >= 0))
    ns = e.filter(pl.col("etype") == s_type).height
    npl = e.filter(pl.col("etype") == p_type).height
    if ns < min_events or npl < min_events:
        return None
    if channel == "C":
        return context_row(ev, scale, **kw)
    return K.kappa_row(frame(ev, scale, channel), **kw)
