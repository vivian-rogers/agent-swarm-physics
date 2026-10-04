"""H108 estimators (card Observables O1-O6): noise-corrected persistence P(l) of the daily room difference, rotation
omega = 1 - P(1), angular decorrelation rate D = -ln P(1), the split-half variant, the persistence relabel test, the
group contrast R_D and the Goldstone scaling inputs. Built on rslib (joint-relabel excess cross-products)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rslib as R  # noqa: E402

DATA = R.ROOT / "data/processed/H108-goldstone-room-wandering"


def load_inputs():
    return pl.read_parquet(DATA / "statements.parquet")


def D_of(P1: float) -> float:
    if not np.isfinite(P1):
        return np.nan
    if P1 <= 0:
        return np.inf
    if P1 >= 1:
        return 0.0
    return float(-np.log(P1))


def sums(pan: R.Panel, n_perm: int = 2000, seed: int = 0, max_lag: int = 6) -> dict:
    """Per-lag sums of excess cross-products and excess norms over valid day pairs, plus the split-half sums."""
    nd = len(pan.bins)
    PI = R.perms(pan.lab, n_perm, seed)
    xs = [pan.X[b] for b in range(nd)]; ms = [pan.M[b] for b in range(nd)]
    C, obs, Z, Pv = R.excess_matrix(xs, ms, pan.lab, PI)
    E = np.diag(C)
    out = {"n_days": nd, "E": E.tolist(), "lags": {}}
    for l in range(1, min(max_lag, nd - 1) + 1):
        pairs = [(d, d + l) for d in range(nd - l) if np.isfinite(C[d, d + l]) and np.isfinite(E[d]) and np.isfinite(E[d + l])]
        out["lags"][l] = {"n_pairs": len(pairs), "sumC": float(sum(C[a, b] for a, b in pairs)),
                          "sumEa": float(sum(E[a] for a, b in pairs)), "sumEb": float(sum(E[b] for a, b in pairs))}
    # persistence relabel test on the lag-1 sum (joint relabel distribution of sum_d D_pi(d).D_pi(d+1))
    isb0 = (pan.lab == R.BEST)[None, :]
    D0 = np.array([R.deltas(x, m, isb0)[0] for x, m in zip(xs, ms)])
    Dp = np.array([R.deltas(x, m, PI) for x, m in zip(xs, ms)])
    pairs1 = [(d, d + 1) for d in range(nd - 1) if np.all(np.isfinite(D0[d])) and np.all(np.isfinite(D0[d + 1]))]
    if pairs1:
        o1 = sum(float(D0[a] @ D0[b]) for a, b in pairs1)
        n1 = np.nansum([np.einsum("ij,ij->i", Dp[a], Dp[b]) for a, b in pairs1], axis=0)
        out["persist_obs"] = o1; out["persist_p"] = float((1 + (n1 >= o1).sum()) / (1 + len(n1)))
        out["persist_z"] = float((o1 - n1.mean()) / n1.std()) if n1.std() > 0 else np.nan
    # split-half variant (HH338 literal): E_sh(d) = D1(d).D2(d), raw cross-day products
    if pan.X1 is not None:
        e = []
        for b in range(nd):
            d1 = R.deltas(pan.X1[b], pan.M12[b], isb0)[0]; d2 = R.deltas(pan.X2[b], pan.M12[b], isb0)[0]
            e.append(float(d1 @ d2) if np.all(np.isfinite(d1)) and np.all(np.isfinite(d2)) else np.nan)
        e = np.array(e)
        pr = [(a, b) for a, b in pairs1 if np.isfinite(e[a]) and np.isfinite(e[b])]
        out["sh"] = {"sumC": float(sum(D0[a] @ D0[b] for a, b in pr)), "sumEa": float(sum(e[a] for a, b in pr)),
                     "sumEb": float(sum(e[b] for a, b in pr)), "n_pairs": len(pr)}
    nb = pan.M[:, pan.lab == R.BEST].sum(1); nr = pan.M[:, pan.lab == R.REST].sum(1)
    ok = (nb >= 2) & (nr >= 2)
    out["N_eff"] = float(np.mean(1 / (1 / nb[ok] + 1 / nr[ok]))) if ok.any() else np.nan
    out["E_mean"] = float(np.nanmean(E))
    return out


def P_from(s: dict, lag: int = 1, key: str | None = None) -> float:
    d = s.get("sh") if key == "sh" else (s["lags"].get(lag) or s["lags"].get(str(lag)))
    if d is None or d["n_pairs"] == 0:
        return np.nan
    den = d["sumEa"] * d["sumEb"]
    return float(d["sumC"] / np.sqrt(den)) if den > 0 else np.nan


def pooled_P(list_of_sums: list[dict], lag: int = 1, key: str | None = None) -> float:
    c = ea = eb = 0.0; n = 0
    for s in list_of_sums:
        d = s.get("sh") if key == "sh" else (s["lags"].get(lag) or s["lags"].get(str(lag)))
        if not d or d["n_pairs"] == 0:
            continue
        c += d["sumC"]; ea += d["sumEa"]; eb += d["sumEb"]; n += d["n_pairs"]
    return float(c / np.sqrt(ea * eb)) if (n and ea > 0 and eb > 0) else np.nan


def boot_sums(pan: R.Panel, n_boot: int = 200, n_perm: int = 200, seed: int = 0) -> list[dict]:
    rng = np.random.default_rng(seed)
    out = []
    for b in range(n_boot):
        q = R.resample_agents(pan, rng)
        out.append(sums(q, n_perm=n_perm, seed=seed + 7 + b, max_lag=1))
    return out
