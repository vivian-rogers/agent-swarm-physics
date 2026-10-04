"""H100 estimators: room separation S, relabel excess Q, composition / field / spontaneous shares, mover index phi,
room remanence R and swap-carry. Pure functions on (table, X) pairs; see the card's Observables O1-O7.

Conventions
- X rows align with data/processed/H100-room-symmetry-breaking/agent_days.parquet (agent-day vectors, 32-d).
- Day centering: x~_{i,d} = x_{i,d} - mean over agents present on d (same goal) -> removes the day field g_d.
- An analysis period P uses goal P's days in regime III (regime II for #35); #36 therefore uses 36b+36c only.
- Rooms: BEST = 2, REST = 3.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/processed/H100-room-symmetry-breaking"
BEST, REST = 2, 3
MULTI = [35, 36, 37, 38, 39, 41, 42, 44]          # non-holdout multi-room (#best/#rest) periods
REG3 = [36, 37, 38, 39, 40, 41, 42, 44, 51]        # regime-III periods used for agent constants
IDENTICAL = [36, 37, 39, 41, 42]                   # identical room kickoffs (H47)
FIELDED = [38, 44]                                 # room-specific kickoffs
MOVES = {  # boundary -> (pre period, post period, {mover: (from, to)})
    "04-02": (37, 38, {21: (REST, BEST)}),
    "04-27": (38, 39, {20: (BEST, REST), 21: (BEST, REST), 23: (BEST, REST)}),
    "05-25": (42, 44, {22: (BEST, REST)}),
}


def load(model: str = "bge_small", variant: str = "style_resid"):
    tab = pl.read_parquet(DATA / "agent_days.parquet")
    X = np.load(DATA / f"x_{variant}_{model}.npy").astype(np.float64)
    return tab, X


def day_center(tab: pl.DataFrame, X: np.ndarray) -> np.ndarray:
    Xc = X.copy()
    key = (tab["goal_no"].cast(pl.String) + "|" + tab["pt_date"]).to_numpy()
    for k in np.unique(key):
        m = key == k
        Xc[m] -= X[m].mean(0)
    return Xc


def period_rows(tab: pl.DataFrame, P: int) -> np.ndarray:
    reg = "II" if P == 35 else "III"
    return ((tab["goal_no"] == P) & (tab["regime"] == reg)).to_numpy()


def agent_period(tab: pl.DataFrame, Xc: np.ndarray, P: int, min_days: int = 2, days=None):
    """Per agent in period P: room (single room over its days; agents using two rooms as room-of-day are dropped),
    full mean, two alternating-day half means. Returns dict agent -> (room, xbar, h1, h2, n_days)."""
    m = period_rows(tab, P)
    if days is not None:
        m &= tab["pt_date"].is_in(list(days)).to_numpy()
    sub = tab.filter(pl.Series(m)).with_columns(pl.Series("ix", np.nonzero(m)[0]))
    out = {}
    for a, g in sub.sort("pt_date").group_by("agent", maintain_order=True):
        rooms = g["room"].unique().to_list()
        if len(rooms) != 1 or g.height < min_days:
            continue
        ix = g["ix"].to_numpy()
        h1, h2 = ix[0::2], ix[1::2]
        out[int(a[0])] = (int(rooms[0]), Xc[ix].mean(0), Xc[h1].mean(0),
                          Xc[h2].mean(0) if len(h2) else Xc[h1].mean(0), len(ix))
    return out


def constants(tab: pl.DataFrame, Xc: np.ndarray, exclude: set[int], periods=REG3, min_days: int = 1):
    """Leave-period-out agent constants: mean over regime-III periods not in `exclude` of the agent's period mean."""
    acc: dict[int, list] = {}
    for P in periods:
        if P in exclude:
            continue
        m = ((tab["goal_no"] == P) & (tab["regime"] == "III")).to_numpy()
        sub = tab.filter(pl.Series(m)).with_columns(pl.Series("ix", np.nonzero(m)[0]))
        for a, g in sub.group_by("agent"):
            if g.height >= min_days:
                acc.setdefault(int(a[0]), []).append(Xc[g["ix"].to_numpy()].mean(0))
    return {a: np.mean(v, 0) for a, v in acc.items()}, {a: len(v) for a, v in acc.items()}


def room_diff(vecs: dict, labels: dict) -> np.ndarray:
    b = [vecs[a] for a in vecs if labels[a] == BEST]
    r = [vecs[a] for a in vecs if labels[a] == REST]
    return np.mean(b, 0) - np.mean(r, 0)


def _halves(ap):
    agents = sorted(ap)
    H1 = np.array([ap[a][2] for a in agents]); H2 = np.array([ap[a][3] for a in agents])
    lab = np.array([ap[a][0] for a in agents])
    return agents, H1, H2, lab


def S_stat(H1, H2, lab):
    b, r = lab == BEST, lab == REST
    d1 = H1[b].mean(0) - H1[r].mean(0); d2 = H2[b].mean(0) - H2[r].mean(0)
    return float(d1 @ d2), d1, d2


def relabel_null(H1, H2, lab, n: int = 2000, rng=None):
    rng = rng or np.random.default_rng(0)
    out = np.empty(n)
    for k in range(n):
        out[k] = S_stat(H1, H2, rng.permutation(lab))[0]
    return out


def Q_test(H1, H2, lab, n: int = 2000, seed: int = 0):
    S, d1, d2 = S_stat(H1, H2, lab)
    nul = relabel_null(H1, H2, lab, n, np.random.default_rng(seed))
    mu, sd = nul.mean(), nul.std()
    return {"S": S, "S_null_mean": float(mu), "S_null_sd": float(sd), "Q": float(S / mu) if mu > 0 else float("nan"),
            "z": float((S - mu) / sd) if sd > 0 else float("nan"), "p": float((1 + (nul >= S).sum()) / (1 + n))}


def field_basis(fields: pl.DataFrame, F: np.ndarray, P: int, cos_max: float = 0.95):
    """Unit field-difference directions for period P: room kickoff (if the rooms' kickoffs differ: cos < cos_max) and
    operator messages (if both rooms have >= 3). Returns (E: k x 32 orthonormal, info)."""
    info, dirs = {}, []
    for kind in ("kickoff_room", "operator"):
        f = fields.filter((pl.col("goal_no") == P) & (pl.col("kind") == kind))
        rb, rr = f.filter(pl.col("room") == BEST), f.filter(pl.col("room") == REST)
        if rb.height and rr.height:
            vb, vr = F[rb["frow"][0]], F[rr["frow"][0]]
            c = float(vb @ vr / np.linalg.norm(vb) / np.linalg.norm(vr))
            info[f"cos_{kind}"] = c
            if kind == "operator" or c < cos_max:
                d = vb - vr
                dirs.append(d / np.linalg.norm(d))
                info[f"use_{kind}"] = True
    if not dirs:
        return np.zeros((0, F.shape[1])), info
    Q, _ = np.linalg.qr(np.array(dirs).T)
    return Q.T, info


def proj_share(d1, d2, E, S):
    if E.shape[0] == 0:
        return 0.0
    return float(sum((d1 @ e) * (d2 @ e) for e in E) / S)


def remove_dirs(H, E):
    return H - (H @ E.T) @ E if E.shape[0] else H


def field_null(xbar, E_dim, d1, d2, S, n=2000, seed=1):
    """Share of S along random k-dim subspaces drawn from the empirical between-agent covariance (H20)."""
    rng = np.random.default_rng(seed)
    C = np.cov(xbar.T)
    L = np.linalg.cholesky(C + 1e-9 * np.eye(C.shape[0]))
    out = np.empty(n)
    for k in range(n):
        V = (L @ rng.standard_normal((C.shape[0], E_dim))).T
        Qm, _ = np.linalg.qr(V.T)
        out[k] = proj_share(d1, d2, Qm.T, S)
    return out


def decompose(tab, Xc, fields, F, P: int, n_null: int = 2000, n_boot: int = 500, seed: int = 0, with_comp=True):
    """O1-O4 for period P."""
    ap = agent_period(tab, Xc, P)
    agents, H1, H2, lab = _halves(ap)
    res = {"period": P, "n_best": int((lab == BEST).sum()), "n_rest": int((lab == REST).sum()),
           "agents": agents, "n_days_med": float(np.median([ap[a][4] for a in agents]))}
    res.update(Q_test(H1, H2, lab, n_null, seed))
    S, d1, d2 = S_stat(H1, H2, lab)
    xbar = np.array([ap[a][1] for a in agents])
    dfull = xbar[lab == BEST].mean(0) - xbar[lab == REST].mean(0)
    E, finfo = field_basis(fields, F, P)
    res.update(finfo); res["field_dim"] = int(E.shape[0])
    res["f_field"] = proj_share(d1, d2, E, S) if S > 0 else float("nan")
    if E.shape[0]:
        xw = xbar.copy()  # within-room centred agent means: the null covariance must not contain the room difference
        for rr in (BEST, REST):
            xw[lab == rr] -= xw[lab == rr].mean(0)
        fn = field_null(xw, E.shape[0], d1, d2, S, n_null, seed + 1)
        res["f_field_null_mean"] = float(fn.mean()); res["f_field_p"] = float((1 + (fn >= res["f_field"]).sum()) / (1 + n_null))
    if with_comp and P != 35:
        A, nper = constants(tab, Xc, exclude={P})
        Ahat = np.array([A.get(a, np.zeros(Xc.shape[1])) for a in agents])
        res["n_no_const"] = int(sum(a not in A for a in agents))
        dcomp = Ahat[lab == BEST].mean(0) - Ahat[lab == REST].mean(0)
        res["f_comp"] = float(dcomp @ dfull / S) if S > 0 else float("nan")
        res["f_spont"] = 1 - res["f_comp"] - res["f_field"]
        R1, R2 = H1 - Ahat, H2 - Ahat
        qr = Q_test(R1, R2, lab, n_null, seed + 2)
        res.update({f"{k}_res": v for k, v in qr.items()})
        qs = Q_test(remove_dirs(R1, E), remove_dirs(R2, E), lab, n_null, seed + 3)
        res.update({f"{k}_spont": v for k, v in qs.items()})
        # agent bootstrap (within rooms) for the shares
        rng = np.random.default_rng(seed + 4)
        bi, ri = np.nonzero(lab == BEST)[0], np.nonzero(lab == REST)[0]
        fc, ff = [], []
        for _ in range(n_boot):
            ix = np.concatenate([rng.choice(bi, len(bi)), rng.choice(ri, len(ri))])
            l2 = lab[ix]
            Sb, e1, e2 = S_stat(H1[ix], H2[ix], l2)
            if Sb <= 0:
                continue
            xb = xbar[ix]; df = xb[l2 == BEST].mean(0) - xb[l2 == REST].mean(0)
            dc = Ahat[ix][l2 == BEST].mean(0) - Ahat[ix][l2 == REST].mean(0)
            fc.append(dc @ df / Sb); ff.append(proj_share(e1, e2, E, Sb))
        fc, ff = np.array(fc), np.array(ff)
        res["n_boot_ok"] = int(len(fc))
        if len(fc) < 20:
            res["_d"] = (d1, d2, dfull, E)
            return res
        res["f_comp_ci"] = [float(np.percentile(fc, 2.5)), float(np.percentile(fc, 97.5))]
        res["f_field_ci"] = [float(np.percentile(ff, 2.5)), float(np.percentile(ff, 97.5))]
        fs = 1 - fc - ff
        res["f_spont_ci"] = [float(np.percentile(fs, 2.5)), float(np.percentile(fs, 97.5))]
        res["n_boot_ok"] = int(len(fc))
    res["_d"] = (d1, d2, dfull, E)
    return res


def constants_invariance(tab, Xc, n_perm: int = 2000, seed: int = 0):
    """O2a: agent constants from odd vs even regime-III periods; pooled cosine-type reliability + permutation null."""
    odd = [P for k, P in enumerate(REG3) if k % 2 == 0]
    even = [P for k, P in enumerate(REG3) if k % 2 == 1]
    A, _ = constants(tab, Xc, exclude=set(even))
    B, _ = constants(tab, Xc, exclude=set(odd))
    ag = sorted(set(A) & set(B))
    a = np.array([A[x] for x in ag]); b = np.array([B[x] for x in ag])
    a -= a.mean(0); b -= b.mean(0)

    def rel(a, b):
        return float((a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum()))
    r = rel(a, b)
    rng = np.random.default_rng(seed)
    nul = np.array([rel(a, b[rng.permutation(len(ag))]) for _ in range(n_perm)])
    return {"r": r, "null_mean": float(nul.mean()), "null_p95": float(np.percentile(nul, 95)),
            "p": float((1 + (nul >= r).sum()) / (1 + n_perm)), "n_agents": len(ag), "odd": odd, "even": even}


def mover_index(tab, Xc, boundary: str, n_boot: int = 1000, seed: int = 0):
    """O5: phi for each mover at a boundary (post period), its pre-period value, its composition prediction,
    the stayers' leave-one-out distribution, and day-1 phi."""
    pre, post, movers = MOVES[boundary]
    ap_pre, ap_post = agent_period(tab, Xc, pre, 1), agent_period(tab, Xc, post, 1)
    out = {"boundary": boundary, "pre": pre, "post": post, "movers": {}}
    A, _ = constants(tab, Xc, exclude={pre, post})
    for k, (frm, to) in movers.items():
        st_new = [a for a in ap_post if a in ap_pre and a != k and ap_post[a][0] == to and ap_pre[a][0] == to]
        st_old = [a for a in ap_post if a in ap_pre and a != k and ap_post[a][0] == frm and ap_pre[a][0] == frm]
        # stayers' native contrast (post), leave-one-out
        def contrast(ap, j):
            own = [a for a in (st_new if ap_post[j][0] == to else st_old) if a != j]
            oth = st_old if ap_post[j][0] == to else st_new
            return np.mean([ap[j][1] @ ap[a][1] for a in own]) - np.mean([ap[j][1] @ ap[a][1] for a in oth])

        def M(ap, kk, vec=None):
            v = ap[kk][1] if vec is None else vec
            return np.mean([v @ ap[a][1] for a in st_new]) - np.mean([v @ ap[a][1] for a in st_old])
        res = {"from": frm, "to": to, "n_new_stayers": len(st_new), "n_old_stayers": len(st_old)}
        if k not in ap_post or len(st_new) < 2 or len(st_old) < 2:
            res["skip"] = True; out["movers"][k] = res; continue
        C_post = np.mean([contrast(ap_post, j) for j in st_new + st_old])
        stayer_phi = [contrast(ap_post, j) / C_post for j in st_new + st_old]
        res["C_post"] = float(C_post)
        # is the native contrast real? permute stayers between the two rooms (sizes kept)
        st_all = st_new + st_old
        V = np.array([ap_post[a][1] for a in st_all]); G = V @ V.T
        lab0 = np.array([1] * len(st_new) + [0] * len(st_old))

        def Cperm(lb):
            vals = []
            for j in range(len(lb)):
                own = (lb == lb[j]); own[j] = False
                vals.append(G[j, own].mean() - G[j, lb != lb[j]].mean())
            return np.mean(vals)
        rngc = np.random.default_rng(seed + 100 + k)
        cn = np.array([Cperm(rngc.permutation(lab0)) for _ in range(500)])
        res["C_post_z"] = float((C_post - cn.mean()) / cn.std())
        res["C_post_p"] = float((1 + (cn >= C_post).sum()) / 501)
        res["phi_post"] = float(M(ap_post, k) / C_post)
        res["stayers_phi"] = [float(x) for x in stayer_phi]
        res["stayers_phi_p05"] = float(np.percentile(stayer_phi, 5))
        if k in ap_pre:
            C_pre = np.mean([contrast(ap_pre, j) for j in st_new + st_old])
            res["phi_pre"] = float(M(ap_pre, k) / C_pre); res["C_pre"] = float(C_pre)
            Vp = np.array([ap_pre[a][1] for a in st_all]); Gp = Vp @ Vp.T

            def Cperm_pre(lb):
                return np.mean([Gp[j, (lb == lb[j]) & (np.arange(len(lb)) != j)].mean() - Gp[j, lb != lb[j]].mean()
                                for j in range(len(lb))])
            cnp = np.array([Cperm_pre(rngc.permutation(lab0)) for _ in range(500)])
            res["C_pre_z"] = float((C_pre - cnp.mean()) / cnp.std())
            res["C_pre_p"] = float((1 + (cnp >= C_pre).sum()) / 501)
        if k in A and all(a in A for a in st_new + st_old):
            Mc = np.mean([A[k] @ A[a] for a in st_new]) - np.mean([A[k] @ A[a] for a in st_old])
            res["phi_comp"] = float(Mc / C_post)
        # day-1 phi
        m = period_rows(tab, post) & (tab["agent"] == k).to_numpy()
        days = sorted(tab.filter(pl.Series(m))["pt_date"].to_list())
        ix = np.nonzero(m & (tab["pt_date"] == days[0]).to_numpy())[0]
        res["phi_day1"] = float(M(ap_post, k, Xc[ix].mean(0)) / C_post)
        res["phi_by_day"] = {}
        for d in days:
            ixd = np.nonzero(m & (tab["pt_date"] == d).to_numpy())[0]
            res["phi_by_day"][d] = float(M(ap_post, k, Xc[ixd].mean(0)) / C_post)
        # bootstrap over post days
        pdays = sorted(tab.filter(pl.Series(period_rows(tab, post)))["pt_date"].unique().to_list())
        rng = np.random.default_rng(seed + k)
        bs = []
        pm = period_rows(tab, post); ag_np = tab["agent"].to_numpy(); dt_np = tab["pt_date"].to_numpy()
        rowmap = {(a, d): np.nonzero(pm & (ag_np == a) & (dt_np == d))[0] for a in set(st_new + st_old + [k])
                  for d in pdays}
        for _ in range(n_boot):
            dd = rng.choice(pdays, len(pdays))
            sub = {}
            for a in set(st_new + st_old + [k]):
                rows = np.concatenate([rowmap[(a, d)] for d in dd])
                if len(rows) == 0:
                    break
                sub[a] = (ap_post[a][0], Xc[rows].mean(0))
            else:
                Cb = np.mean([(np.mean([sub[j][1] @ sub[a][1] for a in (st_new if sub[j][0] == to else st_old) if a != j])
                               - np.mean([sub[j][1] @ sub[a][1] for a in (st_old if sub[j][0] == to else st_new)]))
                              for j in st_new + st_old])
                Mb = np.mean([sub[k][1] @ sub[a][1] for a in st_new]) - np.mean([sub[k][1] @ sub[a][1] for a in st_old])
                if Cb > 0:
                    bs.append(Mb / Cb)
        if bs:
            res["phi_post_ci"] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
            res["n_boot_ok"] = len(bs)
        out["movers"][k] = res
    return out


def remanence(tab, Xc, fields, F, P1: int, P2: int, n_null: int = 2000, seed: int = 0, spont=True):
    """O7: cos of the room-difference vectors of two periods (composition and field removed if spont)."""
    vs, labs, ags = [], [], []
    for P in (P1, P2):
        ap = agent_period(tab, Xc, P, 1)
        agents = sorted(ap)
        x = np.array([ap[a][1] for a in agents]); lab = np.array([ap[a][0] for a in agents])
        if spont:
            A, _ = constants(tab, Xc, exclude={P1, P2})
            x = x - np.array([A.get(a, np.zeros(x.shape[1])) for a in agents])
            E, _ = field_basis(fields, F, P)
            x = remove_dirs(x, E)
        vs.append(x); labs.append(lab); ags.append(agents)

    def cosd(l1, l2):
        d1 = vs[0][l1 == BEST].mean(0) - vs[0][l1 == REST].mean(0)
        d2 = vs[1][l2 == BEST].mean(0) - vs[1][l2 == REST].mean(0)
        return float(d1 @ d2 / np.linalg.norm(d1) / np.linalg.norm(d2))
    R = cosd(labs[0], labs[1])
    rng = np.random.default_rng(seed)
    # joint relabel: an agent present in both periods keeps the same pseudo-room in both (its leftover constant is
    # shared by the two periods; independent relabels would break that and make the null too narrow)
    pos2 = {a: j for j, a in enumerate(ags[1])}
    nul = []
    for _ in range(n_null):
        l1 = rng.permutation(labs[0])
        l2 = rng.permutation(labs[1])
        for i, a in enumerate(ags[0]):
            if a in pos2:
                l2[pos2[a]] = l1[i]
        if (l2 == BEST).sum() == 0 or (l2 == REST).sum() == 0:
            continue
        nul.append(cosd(l1, l2))
    nul = np.array(nul)
    return {"P1": P1, "P2": P2, "R": R, "null_sd": float(nul.std()), "z": float((R - nul.mean()) / nul.std()),
            "p_two": float((1 + (np.abs(nul) >= abs(R)).sum()) / (1 + n_null))}


def swap_carry(tab, Xc, pre: int = 38, post: int = 39, n_null: int = 2000, seed: int = 0):
    """O6: does the post-swap room difference follow the rooms (R_room) or the agents (R_agent)?"""
    ap1, ap2 = agent_period(tab, Xc, pre, 1), agent_period(tab, Xc, post, 1)
    a1 = sorted(ap1); a2 = sorted(ap2); both = sorted(set(a1) & set(a2))
    x1 = np.array([ap1[a][1] for a in a1]); l1 = np.array([ap1[a][0] for a in a1])
    x2 = np.array([ap2[a][1] for a in a2]); l2 = np.array([ap2[a][0] for a in a2])
    xb1 = np.array([ap1[a][1] for a in both]); lb2 = np.array([ap2[a][0] for a in both])
    d38 = x1[l1 == BEST].mean(0) - x1[l1 == REST].mean(0)

    def stats(l2p, lb2p):
        d39 = x2[l2p == BEST].mean(0) - x2[l2p == REST].mean(0)
        dag = xb1[lb2p == BEST].mean(0) - xb1[lb2p == REST].mean(0)
        c = lambda u, v: float(u @ v / np.linalg.norm(u) / np.linalg.norm(v))  # noqa: E731
        return c(d39, d38), c(d39, dag)
    Rr, Ra = stats(l2, lb2)
    rng = np.random.default_rng(seed)
    pos = {a: k for k, a in enumerate(a2)}
    nr, na = [], []
    for _ in range(n_null):
        lp = rng.permutation(l2)
        r1, r2 = stats(lp, np.array([lp[pos[a]] for a in both]))
        nr.append(r1); na.append(r2)
    nr, na = np.array(nr), np.array(na)
    return {"R_room": Rr, "R_room_z": float((Rr - nr.mean()) / nr.std()), "R_agent": Ra,
            "R_agent_z": float((Ra - na.mean()) / na.std()), "n_both": len(both),
            "p_room_two": float((1 + (np.abs(nr) >= abs(Rr)).sum()) / (1 + n_null)),
            "p_agent_two": float((1 + (np.abs(na) >= abs(Ra)).sum()) / (1 + n_null))}
