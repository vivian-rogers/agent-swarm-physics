"""H37 exploratory round 1 on non-holdout periods: #12 (positive control), #51, #26, #40 (contrast).

Implements the card's observables O1-O7 and predictions P1-P12 exactly as written (2026-10-04 01:50 UTC) plus
Amendment 1. Primary pair set: Jev responds >= 0.5; stance = soft s_e. Variants: all pairs; hard labels.
Outputs data/processed/H37-stance-spins/G<NN>/results.json and a cross-period summary.json. No text is read.

Usage: uv run python hypotheses/H37-stance-spins/analysis/explore.py [--only 12 51 26 40] [--nperm 5000]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
os.environ.setdefault("POLARS_MAX_THREADS", "2")
import numpy as np
import polars as pl
from scipy.stats import fisher_exact

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h37lib as L  # noqa: E402
import h37data as D  # noqa: E402
from synthetic import FWProj  # noqa: E402

SEED = 20261004


def jsonable(o):
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, (np.floating,)):
        return float(o) if np.isfinite(o) else None
    if isinstance(o, float):
        return o if np.isfinite(o) else None
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.ndarray):
        return jsonable(o.tolist())
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def codes(P):
    agents = sorted(set(P["agent_a"].to_list()) | set(P["agent_b"].to_list()))
    ix = {a: k for k, a in enumerate(agents)}
    spk = np.array([ix[a] for a in P["agent_b"]]); tgt = np.array([ix[a] for a in P["agent_a"]])
    return agents, ix, spk, tgt


def variants(P):
    """Primary (responds >= 0.5, soft) and the two robustness variants."""
    out = {"primary": (P.filter(pl.col("responds") >= 0.5), "s_soft"),
           "all_pairs": (P, "s_soft"),
           "hard": (P.filter(pl.col("responds") >= 0.5), "s_hard")}
    return out


def class_shares(P):
    n = P.height
    sh = {k: float((P["stance"] == k).mean()) for k in D.STANCES}
    return {"n": n, "shares": sh, "f_neg": float(P["s_hard"].eq(-1).mean()), "f_pos": float(P["s_hard"].eq(1).mean()),
            "s_mean": float(P["s_soft"].mean())}


def day_boot_fneg(P, nboot=1000, rng=None):
    rng = np.random.default_rng(rng)
    days = sorted(set(P["pt_date"].to_list()))
    neg = P.group_by("pt_date").agg(pl.col("s_hard").eq(-1).sum().alias("k"), pl.len().alias("n"))
    k = dict(zip(neg["pt_date"], neg["k"])); n = dict(zip(neg["pt_date"], neg["n"]))
    vals = []
    for _ in range(nboot):
        dd = rng.choice(days, len(days))
        vals.append(sum(k[d] for d in dd) / max(1, sum(n[d] for d in dd)))
    return [float(np.quantile(vals, 0.05)), float(np.quantile(vals, 0.95))]


def detector(P, scol="s_soft", fold_by="block", rng=None, nnull=200):
    """O6: operator-facing metrics, identical for every period."""
    rng = np.random.default_rng(rng)
    agents, ix, spk, tgt = codes(P)
    N = len(agents)
    s = P[scol].to_numpy().astype(float)
    out = {"N": N, "n_replies": P.height, **class_shares(P)}
    out["f_neg_ci90_dayboot"] = day_boot_fneg(P, rng=rng)
    sig, pvals = L.significant_negative_pairs(spk, tgt, s, N, nmin=3, q=0.1)
    out["n_pairs_tested"] = int(len(pvals))
    out["sig_negative_pairs"] = [{"a": agents[i], "b": agents[j], "n": n, "mean_resid": m, "p": p} for i, j, n, m, p in sig]
    Jr, C = L.residual_matrix(spk, tgt, s, N, nmin=3)
    Jraw, _ = L.pair_matrix(spk, tgt, s, N, nmin=3)
    out["p_neg_pairs_raw"] = float(np.nanmean(L.h22lib.triu_vals(Jraw) < 0))
    out["faction_resid"] = L.faction_score(Jr, nnull=nnull, rng=rng)
    out["faction_raw"] = L.faction_score(Jraw, nnull=nnull, rng=rng)
    tri = L.h22lib.sign_shuffle_null(np.nan_to_num(Jr), 2000, rng)
    out["triangle_resid"] = {k: tri[k] for k in ("F", "F_null_mean", "F_null_q05", "F_null_q95", "p_F_low", "p_neg")} if tri else {}
    if fold_by == "day":
        days = sorted(set(P["pt_date"].to_list()))
        fold = np.array([days.index(d) % 3 for d in P["pt_date"].to_list()])
    else:
        blk = P["t_b"].dt.epoch("s").to_numpy() // 600
        ub, inv = np.unique(blk, return_inverse=True)
        fold = (np.arange(len(ub)) % 3)[inv]
    t3, t3dc = L.tau3_folds(spk, tgt, s, N, fold, resid=False)
    t3r, t3rdc = L.tau3_folds(spk, tgt, s, N, fold, resid=True)
    out["tau3_raw"] = t3; out["tau3dc_raw"] = t3dc; out["tau3_resid"] = t3r; out["tau3dc_resid"] = t3rdc
    sc = L.agent_scores(spk, tgt, s, N)
    out["flagged_agents"] = [{"agent": agents[i], "z_received": sc["z_received"][i], "z_given": sc["z_given"][i]}
                             for i in range(N) if (sc["z_received"][i] < -2) or (sc["z_given"][i] < -2)]
    out["agent_scores"] = {int(agents[i]): {"z_received": sc["z_received"][i], "z_given": sc["z_given"][i],
                                            "n_given": int((spk == i).sum()), "n_received": int((tgt == i).sum())} for i in range(N)}
    return out, (agents, Jr, Jraw, C)


# ============================================================================= #12


def g12(nperm, rng):
    P0 = D.g12_relations(D.load_pairs(12))
    deb_keys = set()
    import build_debate_pairs as BDP
    for r in BDP.debater_adjacent()[0]:
        deb_keys.add((r["msg_a"], r["msg_b"]))
    P0 = P0.with_columns(pl.Series("debater_adj", [(a, b) in deb_keys for a, b in zip(P0["msg_a"], P0["msg_b"])]))
    teams = D.g12_teams()
    R = {"n_labelled": P0.height, "relation_counts": P0.group_by("phase", "rel").len().sort("phase", "rel").to_dicts()}
    for vname, (P, scol) in variants(P0).items():
        R[vname] = g12_core(P, scol, teams, nperm if vname == "primary" else 2000, rng, full=(vname == "primary"))
    Pv = P0.filter((pl.col("responds") >= 0.5) & pl.col("debater_adj"))
    R["debater_adjacent_only"] = g12_core(Pv, "s_soft", teams, 2000, rng, full=False)
    R["detector"], _ = detector(P0.filter(pl.col("responds") >= 0.5), rng=rng)
    return R


def g12_core(P, scol, teams, nperm, rng, full=True):
    out = {}
    for phase in ("deb", "pre", "post"):
        X = P.filter((pl.col("phase") == phase) & pl.col("rel").is_in(["same", "opposite"]))
        if X.height < 10:
            out[phase] = {"n": X.height}
            continue
        agents, ix, spk, tgt = codes(X)
        N = len(agents)
        s = X[scol].to_numpy().astype(float)
        topic = X["topic_cos"].to_numpy().astype(float)
        same = (X["rel"] == "same").to_numpy().astype(float)
        deb = X["debate"].to_numpy()
        debs = sorted(set(deb.tolist()))
        team_of = {d: {ix[a]: t for a, t in teams[d]["team"].items() if a in ix} for d in debs}
        proj = FWProj(spk, tgt, N)
        prng = np.random.default_rng(SEED + 1)
        perm_x = []
        for _ in range(nperm):
            tt = {}
            for d in debs:
                mem = list(team_of[d].keys()); lab = prng.permutation([team_of[d][m] for m in mem])
                tt[d] = dict(zip(mem, lab))
            pi = np.array([tt[d][i] for d, i in zip(deb, tgt)]); pj = np.array([tt[d][j] for d, j in zip(deb, spk)])
            perm_x.append((pi == pj).astype(float))
        perm_x = np.array(perm_x)
        perm_xr = perm_x - (perm_x @ proj.Q) @ proj.Q.T
        xr = proj.resid(same)

        def gam_p(y):
            yr = proj.resid(y)
            g = (xr @ yr) / (xr @ xr)
            gp = (perm_xr @ yr) / (perm_xr * perm_xr).sum(1)
            return float(g), float((1 + np.sum(gp >= g)) / (1 + nperm)), float((1 + np.sum(gp <= g)) / (1 + nperm))
        g_s, p_s, p_s_less = gam_p(s)
        g_t, p_t, p_t_less = gam_p(topic)
        # stance with topic covariate: residualize on FE + topic, then permutation on x
        Xc = np.column_stack([proj.Q, proj.resid(topic)])
        Qc, _ = np.linalg.qr(Xc)
        rc = lambda v: v - Qc @ (Qc.T @ v)
        xr_c = rc(same); sr_c = rc(s)
        g_c = (xr_c @ sr_c) / (xr_c @ xr_c)
        pxr_c = perm_x - (perm_x @ Qc) @ Qc.T
        gp_c = (pxr_c @ sr_c) / (pxr_c * pxr_c).sum(1)
        p_c = float((1 + np.sum(gp_c >= g_c)) / (1 + nperm))
        rs = proj.resid(s); rt = proj.resid(topic)
        auc_s = L.auc(rs[same == 1], rs[same == 0]); auc_t = L.auc(rt[same == 1], rt[same == 0])
        X2 = X.with_columns(pl.Series("sv", s))
        means = X2.group_by("rel").agg(pl.col("sv").mean().alias("s_mean"), pl.col("s_hard").eq(-1).mean().alias("f_neg"),
                                       pl.col("s_hard").eq(1).mean().alias("f_pos"), pl.col("topic_cos").mean().alias("topic_mean"),
                                       pl.len().alias("n")).sort("rel").to_dicts()
        res = {"n": X.height, "N": N, "gamma_stance": g_s, "p_gamma_stance": p_s, "gamma_topic": g_t, "p_gamma_topic_greater": p_t,
               "p_gamma_topic_less": p_t_less, "gamma_stance_topic_cov": float(g_c), "p_gamma_stance_topic_cov": p_c,
               "auc_stance": auc_s, "auc_topic": auc_t, "by_relation": means}
        if full and phase == "deb":
            res["recovery"] = g12_recovery(X, s, topic, agents, ix, spk, tgt, team_of, debs, rng)
            res["frustration"] = g12_frustration(X, s, agents, ix, spk, tgt, team_of, debs, rng)
            # per-debate gamma signs (heterogeneity)
            per = []
            for d in debs:
                m = deb == d
                if m.sum() >= 6 and len(set(same[m])) == 2:
                    per.append({"debate": int(d), "n": int(m.sum()), "s_same": float(s[m][same[m] == 1].mean()),
                                "s_opp": float(s[m][same[m] == 0].mean())})
            res["per_debate"] = per
        out[phase] = res
    return out


def g12_recovery(X, s, topic, agents, ix, spk, tgt, team_of, debs, rng):
    N = len(agents)
    deb = X["debate"].to_numpy()
    rs = L.two_way_resid(s, spk, tgt, N); rt = L.two_way_resid(topic, spk, tgt, N)
    acc_s, acc_t, chance, per = [], [], [], []
    for d in debs:
        m = deb == d
        mem = sorted(team_of[d]); truth = np.array([team_of[d][k] for k in mem])
        k = int((truth == 1).sum()); sizes = (k, len(mem) - k)
        ch = L.chance_accuracy(truth, sizes)
        out_d = {"debate": int(d), "n_replies": int(m.sum()), "chance_mean": float(ch.mean())}
        for name, r, acc in (("stance", rs, acc_s), ("topic", rt, acc_t)):
            M, C = L.pair_matrix(spk[m], tgt[m], r[m], N)
            sub = np.nan_to_num(M[np.ix_(mem, mem)])
            if np.all(sub == 0):
                a = float(ch.mean())
            else:
                x, _ = L.ground_state(sub, sizes=sizes)
                a = L.partition_accuracy(x, truth)
            acc.append(a); out_d[f"acc_{name}"] = a
        chance.append(ch); per.append(out_d)
    draws = np.mean([rng.choice(c, 20000) for c in chance], axis=0)
    ms, mt = float(np.mean(acc_s)), float(np.mean(acc_t))
    return {"acc_stance": ms, "acc_topic": mt, "chance": float(draws.mean()),
            "p_stance": float((1 + np.sum(draws >= ms - 1e-12)) / (1 + len(draws))),
            "p_topic": float((1 + np.sum(draws >= mt - 1e-12)) / (1 + len(draws))),
            "exact_recovery_stance": int(sum(p["acc_stance"] == 1.0 for p in per)), "per_debate": per}


def g12_frustration(X, s, agents, ix, spk, tgt, team_of, debs, rng, nnull=2000):
    """Pooled over debates: unsatisfied |J| weight of each debate graph's best split (residual J among debaters)."""
    N = len(agents)
    deb = X["debate"].to_numpy()
    rs = L.two_way_resid(s, spk, tgt, N)
    mats = []
    for d in debs:
        m = deb == d
        mem = sorted(team_of[d])
        M, C = L.pair_matrix(spk[m], tgt[m], rs[m], N)
        mats.append(np.nan_to_num(M[np.ix_(mem, mem)]))

    def unsat(Ms):
        u = t = 0.0
        for M in Ms:
            x, e = L.ground_state(M)
            tot = np.abs(L.h22lib.triu_vals(M)).sum()
            u += (tot - e) / 2; t += tot
        return u / t if t > 0 else np.nan
    f = unsat(mats)
    # team-split unsatisfied weight (truth) for reference
    ut = tt = 0.0
    for d, M in zip(debs, mats):
        mem = sorted(team_of[d]); x = np.array([team_of[d][k] for k in mem], float)
        tot = np.abs(L.h22lib.triu_vals(M)).sum(); e = 0.5 * x @ M @ x
        ut += (tot - e) / 2; tt += tot
    nulls = []
    for _ in range(nnull):
        Ms = []
        for M in mats:
            iu = np.triu_indices(M.shape[0], 1); v = M[iu]
            Q = np.zeros_like(M); Q[iu] = rng.permutation(np.sign(v)) * np.abs(v); Ms.append(Q + Q.T)
        nulls.append(unsat(Ms))
    nulls = np.array(nulls)
    return {"f_gs": f, "f_team_split": ut / tt if tt else None, "null_mean": float(nulls.mean()), "null_q05": float(np.quantile(nulls, 0.05)),
            "p_low": float((1 + np.sum(nulls <= f)) / (1 + nnull))}


# ============================================================================= #51


def g51(nperm, rng):
    P0 = D.g51_roles(D.load_pairs(51))
    R = {"n_labelled": P0.height}
    for vname, (P, scol) in variants(P0).items():
        R[vname] = g51_core(P, scol, nperm if vname == "primary" else 2000, rng, full=(vname == "primary"))
    for u in ("51b", "51c", "51d"):
        Pu = P0.filter((pl.col("unit") == u) & (pl.col("responds") >= 0.5))
        R[f"unit_{u}"] = g51_core(Pu, "s_soft", 2000, rng, full=False)
    R["detector"], _ = detector(P0.filter(pl.col("responds") >= 0.5), fold_by="day", rng=rng, nnull=100)
    return R


def g51_core(P, scol, nperm, rng, full=True):
    agents, ix, spk, tgt = codes(P)
    N = len(agents)
    s = P[scol].to_numpy().astype(float)
    topic = P["topic_cos"].to_numpy().astype(float)
    days = {a: sorted(set(P.filter((pl.col("agent_a") == a) | (pl.col("agent_b") == a))["pt_date"].to_list())) for a in agents}
    roles = D.g51_majority_roles(agents, days)
    rlist = sorted({r for r in roles.values() if r})
    role_idx = np.array([rlist.index(roles[a]) if roles[a] else -1 for a in agents])
    lookup = D.RR.lookup_table(rlist)
    labs = D.labs(); lab_arr = np.array([labs[a] for a in agents])
    codes_ = {"SR": 1, "OP": 2, "SY": 3, "NC": 4}
    Js, Cn = L.pair_matrix(spk, tgt, s, N, nmin=3)
    Jt, _ = L.pair_matrix(spk, tgt, topic, N, nmin=3)
    tt_s = L.h22lib.treatment_test(Js, role_idx, lookup, codes_, labs=lab_arr, nperm=nperm, rng=rng)
    tt_t = L.h22lib.treatment_test(Jt, role_idx, lookup, codes_, labs=lab_arr, nperm=nperm, rng=rng)
    C = L.h22lib.class_matrix(role_idx, lookup)
    out = {"N": N, "n": P.height, "roles": {int(a): roles[a] for a in agents}, "stance": tt_s, "topic": tt_t,
           "testable_pairs": {k: int(np.sum(np.triu(C == v, 1) & np.isfinite(Js))) for k, v in codes_.items()}}
    # reply-level shares per class (descriptive)
    out["class_shares"] = P.with_columns(pl.Series("sv", s)).group_by("cls").agg(
        pl.col("sv").mean().alias("s_mean"), pl.col("s_hard").eq(-1).mean().alias("f_neg"), pl.len().alias("n")).sort("cls").to_dicts()
    if full:
        # OP pairs individually (the H22 51a lead)
        ops = []
        for i in range(N):
            for j in range(i + 1, N):
                if C[i, j] == 2:
                    ops.append({"a": agents[i], "b": agents[j], "roles": [roles[agents[i]], roles[agents[j]]], "n": int(Cn[i, j]),
                                "J_stance": Js[i, j], "J_topic": Jt[i, j]})
        out["op_pairs"] = ops
        # P9 enrichment of significant negative pairs in OP u SR u NC
        sig, pvals = L.significant_negative_pairs(spk, tgt, s, N, nmin=3, q=0.1)
        tested = [(i, j) for i in range(N) for j in range(i + 1, N) if Cn[i, j] >= 3]
        conflict = {(i, j) for (i, j) in tested if C[i, j] in (1, 2, 4)}
        sigset = {(i, j) for i, j, *_ in sig}
        a = len(sigset & conflict); b = len(sigset - conflict); c = len(conflict - sigset); d = len(tested) - a - b - c
        orr, pf = fisher_exact([[a, b], [c, d]], alternative="greater") if (a + b) > 0 else (np.nan, 1.0)
        out["P9"] = {"n_sig_neg": len(sigset), "n_sig_conflict": a, "n_conflict_tested": len(conflict), "n_tested": len(tested),
                     "odds_ratio": float(orr) if np.isfinite(orr) else None, "p_fisher": float(pf),
                     "sig_pairs": [{"a": agents[i], "b": agents[j], "cls": int(C[i, j]), "n": n, "mean_resid": m} for i, j, n, m, p in sig]}
        # day-fold tau3 with day bootstrap
        dlist = sorted(set(P["pt_date"].to_list()))
        dix = np.array([dlist.index(d) for d in P["pt_date"].to_list()])
        fold = dix % 3
        t3, t3dc = L.tau3_folds(spk, tgt, s, N, fold, resid=False, nmin=1)
        t3r, t3rdc = L.tau3_folds(spk, tgt, s, N, fold, resid=True, nmin=1)
        bs = []
        for _ in range(200):
            dd = rng.choice(len(dlist), len(dlist))
            w = np.bincount(dd, minlength=len(dlist))
            idx = np.repeat(np.arange(len(s)), w[dix])
            f2 = np.arange(len(dlist))[dd]  # fold by original day index
            fold_b = (np.repeat(dix, w[dix]) % 3)
            bs.append(L.tau3_folds(spk[idx], tgt[idx], s[idx], N, fold_b, resid=True, nmin=1))
        bs = np.array(bs, float)
        out["tau3"] = {"raw": t3, "raw_dc": t3dc, "resid": t3r, "resid_dc": t3rdc,
                       "resid_ci90": np.nanquantile(bs[:, 0], [0.05, 0.95]).tolist(),
                       "resid_dc_ci90": np.nanquantile(bs[:, 1], [0.05, 0.95]).tolist()}
        Jr, _ = L.residual_matrix(spk, tgt, s, N, nmin=3)
        out["frustration_resid"] = L.frustration_gs(Jr, nnull=100, rng=rng)
        out["frustration_raw"] = L.frustration_gs(Js, nnull=100, rng=rng)
        # faction partition (descriptive): overlap with labs and modal rooms
        x, _ = L.ground_state(Jr, rng=rng)
        out["partition"] = {"camp": {int(a): int(v) for a, v in zip(agents, x)},
                            "same_camp_same_lab_rate": _same_rate(x, lab_arr)}
    return out


def _same_rate(x, labels):
    iu = np.triu_indices(len(x), 1)
    sc = (x[:, None] == x[None, :])[iu]; sl = (labels[:, None] == labels[None, :])[iu]
    return {"P(same camp | same lab)": float(sc[sl].mean()) if sl.any() else None, "P(same camp | diff lab)": float(sc[~sl].mean())}


# ============================================================================= #26


def g26(nperm, rng):
    P0 = D.load_pairs(26)
    R = {"n_labelled": P0.height}
    for vname, (P, scol) in variants(P0).items():
        R[vname] = g26_core(P, scol, nperm if vname == "primary" else 2000, rng, full=(vname == "primary"))
    R["detector"], _ = detector(P0.filter(pl.col("responds") >= 0.5), rng=rng)
    return R


def g26_core(P, scol, nperm, rng, full=True):
    from synthetic import vote_similarity
    agents, ix, spk, tgt = codes(P)
    N = len(agents)
    s = P[scol].to_numpy().astype(float)
    topic = P["topic_cos"].to_numpy().astype(float)
    V, sets = vote_similarity(agents)
    Js, _ = L.residual_matrix(spk, tgt, s, N, nmin=3)
    Jt, _ = L.residual_matrix(spk, tgt, topic, N, nmin=3)
    ms = L.mantel(Js, V, nperm=nperm, rng=rng); mt = L.mantel(Jt, V, nperm=nperm, rng=rng)
    # rival candidates: named by >= 2 distinct voters in first-person declarations
    v = D.g26_votes()
    voters_by_cand = {}
    for a, named in zip(v["agent"].to_list(), v["named"].to_list()):
        for c in named:
            voters_by_cand.setdefault(c, set()).add(a)
    cands = sorted(c for c, vs in voters_by_cand.items() if len(vs) >= 2 and c in ix)
    isc = np.array([a in cands for a in agents])
    Jraw, Cn = L.pair_matrix(spk, tgt, s, N, nmin=3)
    iu = np.triu_indices(N, 1)

    def T(mask_c, J):
        rv = (mask_c[:, None] & mask_c[None, :])[iu]
        vals = J[iu]; ok = np.isfinite(vals)
        if (rv & ok).sum() == 0 or (~rv & ok).sum() == 0:
            return np.nan
        return vals[rv & ok].mean() - vals[~rv & ok].mean()
    t_obs = T(isc, Js)
    null = np.array([T(rng.permutation(isc), Js) for _ in range(nperm)])
    null = null[np.isfinite(null)]
    out = {"N": N, "n": P.height, "mantel_stance": ms, "mantel_topic": mt, "candidates": [int(c) for c in cands],
           "T_rival": float(t_obs) if np.isfinite(t_obs) else None,
           "p_rival_less": float((1 + np.sum(null <= t_obs)) / (1 + len(null))) if np.isfinite(t_obs) else None,
           "n_rival_pairs": int(((isc[:, None] & isc[None, :])[iu] & np.isfinite(Js[iu])).sum())}
    if full:
        # vote blocs = modal (1/k-weighted) declared candidate; ARI with the stance ground-state split (descriptive)
        w = {}
        for a, named in zip(v["agent"].to_list(), v["named"].to_list()):
            for c in named:
                w.setdefault(a, {}).setdefault(c, 0.0)
                w[a][c] += 1 / len(named)
        bloc = {a: max(w[a], key=w[a].get) for a in w}
        x, _ = L.ground_state(Js)
        out["bloc"] = {int(a): int(b) for a, b in bloc.items()}
        out["partition"] = {int(a): int(xx) for a, xx in zip(agents, x)}
        common = [k for k, a in enumerate(agents) if a in bloc]
        out["ARI_partition_vs_bloc"] = L.adjusted_rand([bloc[agents[k]] for k in common], [x[k] for k in common]) if len(common) > 2 else None
        out["frustration_resid"] = L.frustration_gs(Js, nnull=500, rng=rng)
        # stance toward the eventual winner (17) by day (descriptive)
        out["stance_toward_winner_by_day"] = P.with_columns(pl.Series("sv", s)).filter(pl.col("agent_a") == 17).group_by("pt_date").agg(
            pl.col("sv").mean().alias("s_mean"), pl.len().alias("n")).sort("pt_date").to_dicts()
    return out


# ============================================================================= #40


def g40(nperm, rng):
    P0 = D.load_pairs(40)
    R = {"n_labelled": P0.height}
    for vname, (P, scol) in variants(P0).items():
        R[vname], _ = detector(P, scol, rng=rng, nnull=500 if vname == "primary" else 100)
    return R


# ============================================================================= summary


def holm(ps):
    names = list(ps); p = np.array([ps[k] for k in names], float)
    o = np.argsort(p); m = len(p)
    adj = np.empty(m); run = 0
    for r, k in enumerate(o):
        run = max(run, min(1, (m - r) * p[k])); adj[k] = run
    return {n: float(a) for n, a in zip(names, adj)}


def summarize(R):
    S = {}
    if "12" in R:
        d = R["12"]["primary"]["deb"]
        byr = {x["rel"]: x for x in d["by_relation"]}
        S["P1"] = {"s_same": byr["same"]["s_mean"], "s_opp": byr["opposite"]["s_mean"], "gamma": d["gamma_stance"], "p": d["p_gamma_stance"],
                   "pass": bool(byr["opposite"]["s_mean"] < 0 < byr["same"]["s_mean"] and d["gamma_stance"] > 0 and d["p_gamma_stance"] < 0.01)}
        S["P2"] = {"auc_stance": d["auc_stance"], "auc_topic": d["auc_topic"], "p_cov": d["p_gamma_stance_topic_cov"],
                   "pass": bool(d["auc_stance"] >= 0.65 and 0.40 <= d["auc_topic"] <= 0.60 and d["p_gamma_stance_topic_cov"] < 0.01)}
        rc = d["recovery"]
        S["P3"] = {"acc_stance": rc["acc_stance"], "acc_topic": rc["acc_topic"], "chance": rc["chance"], "p_stance": rc["p_stance"],
                   "p_topic": rc["p_topic"], "pass": bool(rc["acc_stance"] >= 0.80 and rc["p_stance"] < 0.05 and rc["p_topic"] > 0.05)}
        fr = d["frustration"]
        S["P4"] = {**fr, "pass": bool(fr["p_low"] < 0.05)}
        post = R["12"]["primary"]["post"]
        S["P5"] = {"gamma_deb": d["gamma_stance"], "gamma_post": post.get("gamma_stance"),
                   "pass": bool(post.get("gamma_stance") is not None and post["gamma_stance"] < d["gamma_stance"])}
    if "51" in R:
        g = R["51"]["primary"]
        op = g["stance"]["family_adjusted"]["OP"]; sr = g["stance"]["family_adjusted"]["SR"]; srt = g["topic"]["family_adjusted"]["SR"]
        S["P6"] = {"T_OP": op["T"], "p_less": op["p_less"], "n": op["n"], "pass": bool(op["T"] is not None and op["T"] < 0 and op["p_less"] < 0.05)}
        S["P7"] = {"T_SR_stance": sr["T"], "p_less": sr["p_less"], "n": sr["n"], "T_SR_topic": srt["T"],
                   "pass": bool(sr["T"] is not None and sr["T"] < 0 and sr["p_less"] < 0.05 and (srt["T"] or 0) >= 0)}
        det = R["51"]["detector"]
        S["P8"] = {"f_neg": det["f_neg"], "tau3_raw": g["tau3"]["raw"], "pass": bool(det["f_neg"] < 0.10 and g["tau3"]["raw"] > 0.5)}
        S["P9"] = {**{k: g["P9"][k] for k in ("n_sig_neg", "n_sig_conflict", "odds_ratio", "p_fisher")},
                   "pass": bool((g["P9"]["odds_ratio"] or 0) >= 2 and g["P9"]["p_fisher"] < 0.05)}
    if "26" in R:
        g = R["26"]["primary"]
        S["P10"] = {"r_stance": g["mantel_stance"].get("r"), "p": g["mantel_stance"].get("p_greater"), "r_topic": g["mantel_topic"].get("r"),
                    "pass": bool((g["mantel_stance"].get("r") or 0) > 0 and (g["mantel_stance"].get("p_greater") or 1) < 0.05
                                 and (g["mantel_stance"].get("r") or 0) > (g["mantel_topic"].get("r") or 0))}
        S["P11"] = {"T_rival": g["T_rival"], "p_less": g["p_rival_less"], "n_pairs": g["n_rival_pairs"],
                    "pass": bool(g["T_rival"] is not None and g["p_rival_less"] < 0.05)}
    if "40" in R and "12" in R:
        det = R["40"]["primary"]
        byr = {x["rel"]: x for x in R["12"]["primary"]["deb"]["by_relation"]}
        S["P12"] = {"f_neg_40": det["f_neg"], "f_neg_12_opp": byr["opposite"]["f_neg"], "n_sig_neg": len(det["sig_negative_pairs"]),
                    "faction_p": det["faction_resid"].get("p_factional"),
                    "pass": bool(det["f_neg"] <= 0.5 * byr["opposite"]["f_neg"] and len(det["sig_negative_pairs"]) <= 1
                                 and (det["faction_resid"].get("p_factional") or 1) > 0.05)}
    ps = {}
    for k, key in (("P1", "p"), ("P2", "p_cov"), ("P3", "p_stance"), ("P6", "p_less"), ("P7", "p_less"), ("P10", "p")):
        if k in S and S[k].get(key) is not None:
            ps[k] = S[k][key]
    S["holm"] = holm(ps) if ps else {}
    return S


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", default=["12", "51", "26", "40"])
    ap.add_argument("--nperm", type=int, default=5000)
    a = ap.parse_args()
    rng = np.random.default_rng(SEED)
    fs = D.DATA / "summary.json"
    R = json.loads(fs.read_text()).get("results", {}) if fs.exists() else {}
    fn = {"12": g12, "51": g51, "26": g26, "40": g40}
    for g in a.only:
        t0 = time.time()
        R[g] = jsonable(fn[g](a.nperm, rng))
        (D.DATA / f"G{int(g):02d}").mkdir(parents=True, exist_ok=True)
        (D.DATA / f"G{int(g):02d}" / "results.json").write_text(json.dumps(R[g], indent=1))
        print(f"G{g} done in {time.time() - t0:.0f}s", flush=True)
    S = jsonable(summarize(R))
    fs.write_text(json.dumps({"results": R, "predictions": S}, indent=1))
    D.record("explore", "hypotheses/H37-stance-spins/analysis/explore.py", {"nperm": a.nperm, "goals": a.only, "seed": SEED})
    print(json.dumps(S, indent=1))


if __name__ == "__main__":
    main()
