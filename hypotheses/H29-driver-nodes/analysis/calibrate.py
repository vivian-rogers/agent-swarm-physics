"""Nuisance calibration for the synthetic generator (run before the predictions were written; disclosed in the card).

Computes ONLY variance shares and persistence of agents' own statement vectors (unit-normalized whitened bge):
agent-mean share, day-mean share (common drive), agent-day share, residual (readout noise + fast dynamics),
lag-1 cosine between an agent's consecutive centered statements, and the noise-corrected restoring rate Gamma.
It does NOT compute any pull toward received messages, any placebo contrast or any cross-agent statistic.

  uv run python hypotheses/H29-driver-nodes/analysis/calibrate.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h29lib as L  # noqa: E402


def shares(U: dict) -> dict:
    T = U["turns"]
    X = U["X"][L.vec_index(U, T["msg"].to_numpy())]
    ok = np.isfinite(X).all(1)
    T = T.filter(pl.Series(ok))
    X = X[ok]
    mu = X.mean(0)
    Xc = X - mu
    tot = (Xc ** 2).sum(1).mean()

    def share(keys):
        _, inv = np.unique(keys, return_inverse=True)
        M = np.zeros((inv.max() + 1, X.shape[1]))
        np.add.at(M, inv, Xc)
        M /= np.bincount(inv)[:, None]
        return float((M[inv] ** 2).sum(1).mean() / tot)

    a = T["agent"].to_numpy()
    d = T["day_idx"].to_numpy()
    s_agent = share(a)
    s_day = share(d)
    s_ad = share(a.astype(np.int64) * 1000 + d)
    # lag-1 cosine of consecutive own statements after removing the agent mean
    lag1 = []
    for (ag,), sub in T.with_row_index("r").group_by(["agent"], maintain_order=True):
        r = sub["r"].to_numpy()
        dd = sub["day_idx"].to_numpy()
        Z = Xc[r] - Xc[r].mean(0)
        same = dd[1:] == dd[:-1]
        num = (Z[1:] * Z[:-1]).sum(1)[same]
        den = (np.linalg.norm(Z[1:], axis=1) * np.linalg.norm(Z[:-1], axis=1))[same]
        lag1.extend((num / np.where(den > 0, den, 1)).tolist())
    g = L.gamma_unit(U)
    # statements per agent per active hour and visible messages per turn (sampling, not content)
    hours = L.active_hours(U)
    return dict(unit=U["name"], n_turns=int(len(X)), total_var=float(tot), share_agent=s_agent, share_day=s_day,
                share_agent_day=s_ad, residual=1 - s_ad, lag1_cos=float(np.mean(lag1)), gamma_per_h=g["gamma"],
                rho_30min=g["rho_med"], turns_per_agent_hour=float(len(X) / hours / len(set(a.tolist()))),
                k_median=float(U["rows"].filter(pl.col("vis")).group_by("talk_id").len()["len"].median()))


def main():
    emb = L.Emb()
    res = []
    for name in ("G38", "G41", "G51b"):
        U = L.attach_vectors(L.load_unit(name), emb)
        r = shares(U)
        res.append(r)
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()}, flush=True)
    L.jdump(res, L.OUT / "calibration.json")


if __name__ == "__main__":
    main()
