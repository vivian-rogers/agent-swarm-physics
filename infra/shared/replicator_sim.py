"""Synthetic replicator worlds on a period's real call schedule (H77, H78 axis F).

At each real model call of agent i (time order), with the current true host counts n_k:
  - a host goes idle (true dilution) with probability eps;
  - i is recruited by repo k != cur(i) (n_k >= 1) with hazard c * A_k * n_k^p / N_ref, or founds a new repo with hazard beta;
    one event at most per call (competing hazards); a recruitment is a switch (departure from cur(i)) if i hosted a repo;
  - a host emits a work commit to its repo with probability pi_c.
Worlds: neutral (p = 1, A = 1: the Hubbell limit of model 06), conformist (p > 1), parabolic (p < 1), field-only (p = 0:
every existing repo recruits at the same rate whatever its size). Repo fitness A_k ~ lognormal(0, sigma_A).
The synthetic commits then go through the same label builder (replicator_hosts.build_from_frames), so measurement
(30-min modal labels, carry-forward, call-clock expiry) is reproduced. True events are returned too.
"""
from __future__ import annotations

import math

import numpy as np
import polars as pl


def simulate(calls: pl.DataFrame, p: float, c: float, beta: float, eps: float, pi_c: float, sigma_A: float = 0.0,
             seed: int = 0, n_ref: int | None = None):
    rng = np.random.default_rng(seed)
    ag = calls["agent"].to_numpy()
    tt = calls["t_call"].to_list()
    pdates = calls["pt_date"].to_list()
    n_ref = n_ref or len(set(ag.tolist()))
    host: dict[int, int] = {}
    n: dict[int, int] = {}
    A: dict[int, float] = {}
    w: dict[int, float] = {}   # A_k n_k^p for repos with n >= 1
    S = 0.0
    nxt = 0
    commits_a, commits_r, commits_t, commits_d = [], [], [], []
    ev = []  # (agent, t, kind, repo, to_repo)
    U = rng.random((len(ag), 4))

    def setw(k):
        nonlocal S
        old = w.get(k, 0.0)
        new = A[k] * n[k] ** p if n[k] >= 1 else 0.0
        S += new - old
        if new > 0:
            w[k] = new
        else:
            w.pop(k, None)

    for idx in range(len(ag)):
        a = int(ag[idx])
        t = tt[idx]
        u = U[idx]
        cur = host.get(a)
        if cur is not None and u[0] < eps:
            n[cur] -= 1
            setw(cur)
            del host[a]
            ev.append((a, t, "expire", str(cur), None))
            cur = None
        own = w.get(cur, 0.0) if cur is not None else 0.0
        H = c * max(S - own, 0.0) / n_ref
        tot = H + beta
        if tot > 0 and u[1] < 1 - math.exp(-tot):
            if u[2] * tot < beta:
                k = nxt
                nxt += 1
                A[k] = float(np.exp(sigma_A * rng.standard_normal())) if sigma_A > 0 else 1.0
                n[k] = 0
                kind = "birth"
            else:
                keys = [kk for kk in w if kk != cur]
                if not keys:
                    continue
                ws = np.array([w[kk] for kk in keys])
                k = keys[int(np.searchsorted(np.cumsum(ws), u[3] * ws.sum()))] if len(keys) > 1 else keys[0]
                kind = "recruit"
            if cur is not None:
                n[cur] -= 1
                setw(cur)
                ev.append((a, t, "depart", str(cur), str(k)))
            n[k] += 1
            setw(k)
            host[a] = k
            ev.append((a, t, kind, str(k), None))
            cur = k
        if cur is not None and rng.random() < pi_c:
            commits_a.append(a); commits_r.append(f"sim/{cur}"); commits_t.append(t); commits_d.append(pdates[idx])
    commits = pl.DataFrame({"agent": pl.Series(commits_a, dtype=pl.Int8), "repo": commits_r,
                            "t": pl.Series(commits_t, dtype=pl.Datetime("us", "UTC")), "pt_date": commits_d})
    tev = pl.DataFrame(ev, schema={"agent": pl.Int8, "t": pl.Datetime("us", "UTC"), "kind": pl.String, "repo": pl.String,
                                   "to_repo": pl.String}, orient="row")
    tev = tev.with_columns(pl.col("repo").map_elements(lambda r: f"sim/{r}", return_dtype=pl.String),
                           pl.col("to_repo").map_elements(lambda r: f"sim/{r}", return_dtype=pl.String),
                           pl.when(pl.col("kind").is_in(["recruit", "birth"])).then(pl.lit("none")).otherwise(None).alias("cls"),
                           pl.when(pl.col("kind").is_in(["recruit", "birth"])).then(pl.lit(False)).otherwise(None).alias("named"))
    return commits, tev
