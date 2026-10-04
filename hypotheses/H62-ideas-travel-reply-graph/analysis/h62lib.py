"""H62 estimators: idea-stratified conditional Poisson hazard ratios on aggregated cells, per-edge transmissibility,
branching decomposition. Definitions: ../README.md ("Operational definitions", 2026-10-04 19:25 UTC)."""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

MODEL_A = ["rec_rep", "rec_room", "rec_hum"]
MODEL_G = ["recg_rep", "recg_room", "rec_hum"]
# Amendment A1 (2026-10-04, from synthetic S1, before real data): unread indicators are exclusive (unread-only = an
# unread use of that channel in the 300-s window and no seen one), so a thread field does not fake copying.
MODEL_B = ["s_rep5", "u_rep5x", "s_room5", "u_room5x", "hum5", "old"]
MODEL_B_ADDITIVE = ["s_rep5", "u_rep5", "s_room5", "u_room5", "hum5", "old"]
PRIOR_SD = 3.0


def derive(cells: pl.DataFrame) -> pl.DataFrame:
    add = []
    for ch in ("rep", "room"):
        for suf in [""] + [c[len(f"u_{ch}5"):] for c in cells.columns if c.startswith(f"u_{ch}5_g")]:
            u, s_, x = f"u_{ch}5{suf}", f"s_{ch}5{suf}", f"u_{ch}5x{suf}"
            if u in cells.columns and x not in cells.columns:
                add.append((pl.col(u) & ~pl.col(s_)).alias(x))
    return cells.with_columns(add) if add else cells


def _arrays(cells: pl.DataFrame, terms: list[str]):
    cells = derive(cells)
    c = cells.group_by(["idea"] + terms).agg(pl.col("calls").sum(), pl.col("adopts").sum())
    ys = c.group_by("idea").agg(pl.col("adopts").sum().alias("Y"))
    c = c.join(ys.filter(pl.col("Y") > 0), on="idea", how="inner").sort("idea")
    X = c.select(terms).to_numpy().astype(float)
    n = c["calls"].to_numpy().astype(float)
    y = c["adopts"].to_numpy().astype(float)
    sid = c["idea"].to_numpy()
    starts = np.r_[0, np.where(np.diff(sid) != 0)[0] + 1]
    Y = np.add.reduceat(y, starts)
    return X, n, y, starts, Y


def fit_cpois(X, n, y, starts, Y, w=None, prior_sd=PRIOR_SD, iters=60):
    """Damped Newton (step halving, step capped at 3) for
    sum_s w_s [sum_r y_r x_r b - Y_s log sum_r n_r e^{x_r b}] - |b|^2 / (2 sd^2).
    The log-sum-exp is computed per stratum with a stabilising shift, so no overflow."""
    k = X.shape[1]
    ws = np.ones(len(starts)) if w is None else w
    sizes = np.diff(np.r_[starts, len(y)])
    wr = np.repeat(ws, sizes)
    lam = 1.0 / prior_sd ** 2
    ln = np.log(n)

    def parts(b):
        z = X @ b + ln
        m = np.maximum.reduceat(z, starts)
        e = np.exp(z - np.repeat(m, sizes))
        S0 = np.add.reduceat(e, starts)
        ll = (wr * y * (X @ b)).sum() - (ws * Y * (np.log(S0) + m)).sum() - 0.5 * lam * (b ** 2).sum()
        return ll, e, S0

    b = np.zeros(k)
    ll, e, S0 = parts(b)
    H = -lam * np.eye(k)
    for _ in range(iters):
        S1 = np.add.reduceat(e[:, None] * X, starts)
        Ex = S1 / S0[:, None]
        g = (wr[:, None] * y[:, None] * X).sum(0) - ((ws * Y)[:, None] * Ex).sum(0) - lam * b
        S2 = np.add.reduceat(e[:, None, None] * X[:, :, None] * X[:, None, :], starts)
        Exx = S2 / S0[:, None, None]
        H = -((ws * Y)[:, None, None] * (Exx - Ex[:, :, None] * Ex[:, None, :])).sum(0) - lam * np.eye(k)
        step = np.linalg.solve(H, g)
        mx = np.abs(step).max()
        if mx > 3:
            step *= 3 / mx
        t = 1.0
        while True:
            nb = b - t * step
            nll, ne, nS0 = parts(nb)
            if nll >= ll - 1e-10 or t < 1e-4:
                break
            t /= 2
        b, ll, e, S0 = nb, nll, ne, nS0
        if np.abs(t * step).max() < 1e-8:
            break
    cov = np.linalg.inv(-H)
    return b, cov


def hr_fit(cells: pl.DataFrame, terms: list[str], B: int = 200, seed: int = 0, contrasts: dict | None = None) -> dict:
    """Hazard ratios (exp b) with Wald CIs; contrasts {name: (term_a, term_b)} = exp(b_a - b_b) with Wald and
    idea-bootstrap CIs. Cell counts per term are reported."""
    X, n, y, starts, Y = _arrays(cells, terms)
    out = dict(n_strata=int(len(starts)), n_adopt=int(y.sum()), n_calls=float(n.sum()))
    if len(starts) < 5:
        return out
    b, cov = fit_cpois(X, n, y, starts, Y)
    se = np.sqrt(np.clip(np.diag(cov), 0, None))
    for i, tname in enumerate(terms):
        out[f"b_{tname}"] = float(b[i])
        out[f"se_{tname}"] = float(se[i])
        out[f"hr_{tname}"] = float(np.exp(b[i]))
        out[f"hr_{tname}_lo"], out[f"hr_{tname}_hi"] = float(np.exp(b[i] - 1.96 * se[i])), float(np.exp(b[i] + 1.96 * se[i]))
        out[f"adopt_{tname}"] = int(y[X[:, i] > 0].sum())
        out[f"calls_{tname}"] = float(n[X[:, i] > 0].sum())
    contrasts = contrasts or {}
    rng = np.random.default_rng(seed)
    boots = {c: [] for c in contrasts}
    for _ in range(B):
        w = rng.multinomial(len(starts), np.full(len(starts), 1 / len(starts))).astype(float)
        try:
            bb, _ = fit_cpois(X, n, y, starts, Y, w=w, iters=25)
        except np.linalg.LinAlgError:
            continue
        for c, (ta, tb) in contrasts.items():
            boots[c].append(bb[terms.index(ta)] - bb[terms.index(tb)])
    for c, (ta, tb) in contrasts.items():
        ia, ib = terms.index(ta), terms.index(tb)
        d = b[ia] - b[ib]
        sd = np.sqrt(max(cov[ia, ia] + cov[ib, ib] - 2 * cov[ia, ib], 0))
        out[c] = float(np.exp(d))
        out[f"{c}_log"] = float(d)
        out[f"{c}_se"] = float(sd)
        out[f"{c}_wlo"], out[f"{c}_whi"] = float(np.exp(d - 1.96 * sd)), float(np.exp(d + 1.96 * sd))
        if boots[c]:
            q = np.percentile(boots[c], [2.5, 97.5])
            out[f"{c}_lo"], out[f"{c}_hi"] = float(np.exp(q[0])), float(np.exp(q[1]))
            out[f"{c}_bse"] = float(np.std(boots[c]))
    return out


def transmissibility(ev: pl.DataFrame, col: str = "chan", B: int = 1000, seed: int = 0, out_col: str = "adopt3") -> dict:
    """T_rep, T_room = adoption within 3 talk calls of the first exposed call; ratio with an idea bootstrap CI."""
    e = ev.filter(pl.col(col).is_in([1, 2]))
    a = e.group_by("idea", col).agg(pl.len().alias("n"), pl.col(out_col).sum().alias("k"))
    ideas = a["idea"].unique().to_numpy()
    if len(ideas) < 5:
        return {}
    idx = {v: i for i, v in enumerate(ideas)}
    N = np.zeros((len(ideas), 2)); K = np.zeros((len(ideas), 2))
    for i_, c_, n_, k_ in zip(a["idea"].to_list(), a[col].to_list(), a["n"].to_list(), a["k"].to_list()):
        N[idx[i_], c_ - 1] = n_; K[idx[i_], c_ - 1] = k_
    def ratio(w):
        n1, n2 = (w[:, None] * N).sum(0)
        k1, k2 = (w[:, None] * K).sum(0)
        return (k1 / n1) / (k2 / n2) if n1 > 0 and n2 > 0 and k2 > 0 else np.nan, k1 / max(n1, 1), k2 / max(n2, 1)
    r, t1, t2 = ratio(np.ones(len(ideas)))
    rng = np.random.default_rng(seed)
    bs = [ratio(rng.multinomial(len(ideas), np.full(len(ideas), 1 / len(ideas))).astype(float))[0] for _ in range(B)]
    bs = np.array([x for x in bs if np.isfinite(x) and x > 0])
    out = dict(T_rep=float(t1), T_room=float(t2), n_rep=int(N[:, 0].sum()), n_room=int(N[:, 1].sum()),
               k_rep=int(K[:, 0].sum()), k_room=int(K[:, 1].sum()), T_ratio=float(r))
    if len(bs) > 20:
        out["T_ratio_lo"], out["T_ratio_hi"] = (float(x) for x in np.percentile(bs, [2.5, 97.5]))
        out["T_ratio_logse"] = float(np.std(np.log(bs)))
    return out


def branching(ad: pl.DataFrame) -> dict:
    n = ad.height
    if n == 0:
        return {}
    ex = ad.filter(pl.col("status") == 2)
    r_rep = ex.filter(pl.col("chan") == 1).height / n
    r_room = ex.filter(pl.col("chan") == 2).height / n
    r_hum = ex.filter(pl.col("chan") == 3).height / n
    return dict(R_hat=r_rep + r_room, R_rep=r_rep, R_room=r_room, R_hum=r_hum, nodes=n,
                share_rep_parent=r_rep / (r_rep + r_room) if r_rep + r_room > 0 else np.nan)


def dl_pool(est, se):
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    if len(est) == 0:
        return np.nan, np.nan, np.nan
    w = 1 / se ** 2
    mu_f = (w * est).sum() / w.sum()
    Q = (w * (est - mu_f) ** 2).sum()
    c = w.sum() - (w ** 2).sum() / w.sum()
    tau2 = max(0.0, (Q - (len(est) - 1)) / c) if c > 0 else 0.0
    ws = 1 / (se ** 2 + tau2)
    return float((ws * est).sum() / ws.sum()), float(np.sqrt(1 / ws.sum())), float(tau2)
