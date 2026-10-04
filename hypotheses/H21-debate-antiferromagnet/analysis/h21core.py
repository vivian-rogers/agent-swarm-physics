"""H21 analysis pipeline shared by synthetic.py (axis F), g12_analysis.py (real data) and confirm_g34.py.

Inputs are plain numpy: X (n x D whitened statement vectors) and a statement dict `st` with arrays
  debate (int, -1 = none), agent (int), phase ('pre' | 'deb' | 'post' | 'other'), ts (float s), and
a list `debates` of dicts: debate, gov (agent ids), opp (agent ids), judge (id or None), winner (+1 Gov,
-1 Opp, 0 none), t_first_speech, t_verdict, t_post_end (all float s on the same clock as st['ts']).

Pre-registered choices (card "Observables", written before real data): agent-centring over the whole period,
debate-centring over the debaters, unit spins, unweighted statement means, min 2 statements per agent-window,
D = 32 whitened dims, 3-min bins for fluctuations, LOAO axes for every projection of an agent onto a team axis.
"""
from __future__ import annotations

import numpy as np

import afmlib as L


def team_of(deb, agent):
    if agent in deb["gov"]:
        return 1
    if agent in deb["opp"]:
        return -1
    return 0


# ------------------------------------------------------------------------------------------------ windows
def build_windows(X, st, debates, phase="deb", agent_centre=True, min_n=2, weights=None, Xc=None,
                  label_override=None):
    """One window per debate: debaters' mean vectors in `phase`, their sublattice labels and unit spins.

    label_override: optional {debate: {agent: +1/-1}} (e.g. lab partition placebo)."""
    if Xc is None:
        Xc = L.agent_center(X, st["agent"]) if agent_centre else np.asarray(X, dtype=np.float64)
    out = []
    for deb in debates:
        lab = label_override.get(deb["debate"]) if label_override else None
        members = set(deb["gov"]) | set(deb["opp"]) if lab is None else set(lab)
        m = (st["debate"] == deb["debate"]) & (st["phase"] == phase) & np.isin(st["agent"], list(members))
        ids, V, cnt = L.window_means(Xc, st["agent"], m, min_n, weights)
        if len(ids) == 0:
            continue
        eps = np.array([team_of(deb, a) if lab is None else lab[a] for a in ids])
        keep = eps != 0
        ids, V, cnt, eps = ids[keep], V[keep], cnt[keep], eps[keep]
        if len(ids) < 4 or (eps == 1).sum() < 1 or (eps == -1).sum() < 1:
            continue
        out.append({"debate": deb["debate"], "agents": ids, "V": V, "eps": eps, "S": L.spins(V), "cnt": cnt,
                    "winner": deb.get("winner", 0)})
    return out


# ------------------------------------------------------------------------------------------------ static tests
def static_tests(windows, n_perm=20000, rng=0):
    per = [L.debate_stats(w["V"], w["eps"]) for w in windows]
    if not per:
        return {"n_debates": 0}
    D_obs = float(np.mean([p["delta"] for p in per]))
    M_obs = float(np.mean([p["ms"] for p in per]))
    nD = L.perm_null(per, "delta_all", n_perm, rng)
    nM = L.perm_null(per, "ms_all", n_perm, rng + 1)
    rec = int(sum(p["recovered"] for p in per))
    p_rec = L.poisson_binomial_sf(rec, [1 / p["n_part"] for p in per])
    pct = [(p["rank"] - 1) / max(1, p["n_part"] - 1) for p in per]
    return {"n_debates": len(per), "delta": D_obs, "delta_null_mean": float(nD.mean()),
            "delta_null_q95": float(np.quantile(nD, 0.95)), "p_delta": L.p_upper(D_obs, nD),
            "ms": M_obs, "ms_null_mean": float(nM.mean()), "ms_null_q95": float(np.quantile(nM, 0.95)),
            "p_ms": L.p_upper(M_obs, nM), "recovered": rec, "recovered_expected_null": float(sum(1 / p["n_part"] for p in per)),
            "p_recovered": p_rec, "mean_rank_pct": float(np.mean(pct)),
            "per_debate": [{"debate": w["debate"], "delta": float(p["delta"]), "ms": float(p["ms"]), "rank": p["rank"],
                            "n_part": p["n_part"], "recovered": bool(p["recovered"]), "n_agents": int(len(w["eps"])),
                            "delta_all": [float(x) for x in p["delta_all"]], "true_idx": int(p["true_idx"])}
                           for w, p in zip(windows, per)]}


def ci_debates(windows, key="delta", n=5000, rng=0):
    vals = [L.debate_stats(w["V"], w["eps"])[key] for w in windows]
    return L.boot_ci(vals, n, rng)


# ------------------------------------------------------------------------------------------------ generic vs specific
def _generic_sigma(windows, signs=None):
    """Generic transfer per debate: sigma_i = eps_i(d) * u_i(d) . g_{d,-i}.

    u = unit(agent-centred window mean), NOT debate-centred: any centring on a mean that contains agent i (in d or
    in another debate) links i's own residuals into the statistic through agent-centring.
    g_{d,-i} = unit(sum over d' != d of s_d' [mean_{Gov d' minus i} u - mean_{Opp d' minus i} u]); s = orientation signs."""
    n = len(windows)
    s = np.ones(n) if signs is None else signs
    U = [L.unit(w["V"]) for w in windows]
    out = []
    for k, w in enumerate(windows):
        eps = w["eps"]
        proj = []
        for i, a in enumerate(w["agents"]):
            tot = np.zeros(w["V"].shape[1])
            for kk, ww in enumerate(windows):
                if kk == k:
                    continue
                keep = ww["agents"] != a
                e = ww["eps"][keep]
                if (e == 1).any() and (e == -1).any():
                    tot += s[kk] * (U[kk][keep][e == 1].mean(0) - U[kk][keep][e == -1].mean(0))
            proj.append(U[k][i] @ L.unit(tot))
        out.append(s[k] * np.mean(eps * np.array(proj)))
    return np.array(out)


def generic_tests(windows, n_perm=20000, rng=0, n_flip=2000):
    """sigma along the cross-debate generic axis (transfer), and static tests after projecting it out.

    Null for the generic transfer: a random Gov/Opp orientation flip per debate (no consistent 'proposing vs
    opposing' direction), axes recomputed each draw. Earlier variants were miscalibrated at G12's design (synthetic
    E3): label permutation 14-16% false positives (agent-centring links an agent's residuals across debates and the
    design ties its sides together); per-agent rotation 13% under motion-specific stance."""
    if len(windows) < 3:
        return {}
    per = _generic_sigma(windows)
    G_obs = float(per.mean())
    r = np.random.default_rng(rng)
    nG = np.array([_generic_sigma(windows, r.choice([-1.0, 1.0], len(windows))).mean() for _ in range(n_flip)])
    gax = L.generic_axes(windows)  # debate-level axis (other debates, all agents) for the projection
    spec = []
    for w, g in zip(windows, gax):
        Vs = L.project_out(w["V"], g)
        spec.append(dict(w, V=Vs, S=L.spins(Vs)))
    st_spec = static_tests(spec, n_perm, rng + 7)
    return {"ms_generic": G_obs, "p_generic_flip": L.p_upper(G_obs, nG), "generic_null_q95": float(np.quantile(nG, 0.95)),
            "generic_null_mean": float(nG.mean()), "per_debate_generic": [float(x) for x in per],
            "specific": {k: st_spec[k] for k in ("delta", "p_delta", "ms", "p_ms", "recovered", "p_recovered")}}


# ------------------------------------------------------------------------------------------------ text axis
def text_axis_tests(windows, axes, n_perm=20000, rng=0):
    """Staggered order along an a-priori axis per debate (e.g. pro-minus-con motion templates)."""
    ws = [w for w in windows if w["debate"] in axes]
    if not ws:
        return {}
    sig, per = [], []
    for w in ws:
        a = L.unit(axes[w["debate"]])
        proj = w["S"] @ a
        sig.append(np.mean(w["eps"] * proj))
        kA = int((w["eps"] == 1).sum())
        alls = [np.mean(e * proj) for e in L.partitions(len(w["eps"]), kA)]
        if 2 * kA == len(w["eps"]):
            alls += [-x for x in alls]
        per.append({"all": np.array(alls)})
    obs = float(np.mean(sig))
    nul = L.perm_null(per, "all", n_perm, rng)
    return {"ms_text": obs, "p_text": L.p_upper(obs, nul), "n": len(ws), "per_debate": [float(x) for x in sig]}


# ------------------------------------------------------------------------------------------------ verdict
def verdict_tests(X, st, debates, agent_centre=True, min_n=1, n_perm=5000, rng=0, Xc=None):
    """Staggered remanence after the verdict and the judge-as-field (winner) asymmetry.

    Frame: for agent i, the debate-phase mean of the OTHER debaters c_{-i} is subtracted from both i's debate and
    post vectors (fixed frame), so a uniform post-verdict shift toward the winner is kept (that IS the field
    signal). Axes are LOAO from the debate phase. sigma = eps_i * s_i . a_{-i}. Winner field: sigma rises for
    winners, falls for losers."""
    if Xc is None:
        Xc = L.agent_center(X, st["agent"]) if agent_centre else np.asarray(X, dtype=np.float64)
    rows = []
    for deb in debates:
        members = list(set(deb["gov"]) | set(deb["opp"]))
        md = (st["debate"] == deb["debate"]) & (st["phase"] == "deb") & np.isin(st["agent"], members)
        mp = (st["debate"] == deb["debate"]) & (st["phase"] == "post") & np.isin(st["agent"], members)
        ids, V, _ = L.window_means(Xc, st["agent"], md, 2)
        if len(ids) < 4:
            continue
        eps = np.array([team_of(deb, a) for a in ids])
        if (eps == 1).sum() < 1 or (eps == -1).sum() < 1:
            continue
        idp, Vp, cp = L.window_means(Xc, st["agent"], mp, min_n)
        post = dict(zip(idp, Vp))
        for i, a in enumerate(ids):
            c, ax = L.loao_frame(V, eps, i)
            sd = eps[i] * (L.unit(V[i] - c) @ ax)
            sp = eps[i] * (L.unit(post[a] - c) @ ax) if a in post else np.nan
            rows.append({"debate": deb["debate"], "agent": int(a), "eps": int(eps[i]), "winner": int(deb.get("winner", 0)),
                         "sigma_deb": float(sd), "sigma_post": float(sp)})
    if not rows:
        return {"n": 0}
    r = rows
    sd = np.array([x["sigma_deb"] for x in r]); sp = np.array([x["sigma_post"] for x in r])
    dbs = np.array([x["debate"] for x in r]); win = np.array([x["eps"] * x["winner"] for x in r])  # +1 winner, -1 loser
    ok = np.isfinite(sp)
    # per-debate means, then over debates
    U = sorted(set(dbs[ok]))
    md_ = np.array([sd[ok & (dbs == u)].mean() for u in U])
    mp_ = np.array([sp[ok & (dbs == u)].mean() for u in U])
    R = float(mp_.mean() / md_.mean()) if md_.mean() != 0 else np.nan
    R_ci = L.ratio_boot_ci(mp_, md_, 5000, rng)
    # winner asymmetry per debate (needs both sides present after verdict)
    asym = []
    for u in U:
        w_ = ok & (dbs == u) & (win == 1); l_ = ok & (dbs == u) & (win == -1)
        if w_.any() and l_.any():
            asym.append((sp[w_] - sd[w_]).mean() - (sp[l_] - sd[l_]).mean())
    asym = np.array(asym)
    loser_post = sp[ok & (win == -1)]
    return {"n_agent_debates": int(ok.sum()), "n_debates": len(U), "sigma_deb": float(md_.mean()), "sigma_post": float(mp_.mean()),
            "remanence": R, "remanence_ci": R_ci, "sigma_post_ci": L.boot_ci(mp_, 5000, rng),
            "winner_asym": float(asym.mean()) if len(asym) else np.nan,
            "winner_asym_ci": L.boot_ci(asym, 5000, rng) if len(asym) else (np.nan, np.nan),
            "winner_asym_pos_frac": float((asym > 0).mean()) if len(asym) else np.nan, "n_asym": int(len(asym)),
            "loser_sigma_post": float(loser_post.mean()) if len(loser_post) else np.nan,
            "loser_flip_frac": float((loser_post < 0).mean()) if len(loser_post) else np.nan, "rows": rows}


def judge_check(Xc, st, debates, verdict_rows):
    """Manipulation check: does the judge's verdict message point toward the winner along the debate axis?"""
    out = []
    for deb in debates:
        if not deb.get("winner"):
            continue
        members = list(set(deb["gov"]) | set(deb["opp"]))
        md = (st["debate"] == deb["debate"]) & (st["phase"] == "deb") & np.isin(st["agent"], members)
        ids, V, _ = L.window_means(Xc, st["agent"], md, 2)
        if len(ids) < 4:
            continue
        eps = np.array([team_of(deb, a) for a in ids])
        c = V.mean(0)
        S = L.unit(V - c)
        ax = L.team_axis(S, eps)
        r = verdict_rows.get(deb["debate"])
        if r is None:
            continue
        out.append(float(deb["winner"] * (L.unit(Xc[r] - c) @ ax)))
    out = np.array(out)
    return {"n": int(len(out)), "mean": float(out.mean()) if len(out) else np.nan,
            "pos_frac": float((out > 0).mean()) if len(out) else np.nan, "values": out.tolist()}


# ------------------------------------------------------------------------------------------------ fluctuations
def fluct_series(X, st, debates, bin_s=180, agent_centre=True, Xc=None):
    """Time-binned sublattice magnetisations along a cross-fitted debate axis (odd/even bins).

    For each debate: bins of `bin_s` from the first speech to the verdict. The axis used for the even bins is
    fitted on the odd bins' team means (agent-level, debate-centred) and vice versa. m_X(b) = mean over block X's
    statements in bin b of x . a."""
    if Xc is None:
        Xc = L.agent_center(X, st["agent"]) if agent_centre else np.asarray(X, dtype=np.float64)
    series = []
    for deb in debates:
        members = list(set(deb["gov"]) | set(deb["opp"]))
        m = (st["debate"] == deb["debate"]) & (st["phase"] == "deb") & np.isin(st["agent"], members)
        idx = np.flatnonzero(m)
        if len(idx) < 8:
            continue
        b = ((st["ts"][idx] - deb["t_first_speech"]) // bin_s).astype(int)
        team = np.array([team_of(deb, a) for a in st["agent"][idx]])
        axes = {}
        for par in (0, 1):
            sel = idx[(b % 2) == par]
            ids, V, _ = L.window_means(Xc, st["agent"], np.isin(np.arange(len(st["agent"])), sel), 1)
            e = np.array([team_of(deb, a) for a in ids])
            if (e == 1).sum() < 1 or (e == -1).sum() < 1:
                axes[par] = None
                continue
            S = L.unit(V - V.mean(0))
            axes[par] = L.team_axis(S, e)
        mA, mB, par = [], [], []
        for bb in np.unique(b):
            ax = axes.get(1 - (bb % 2))
            if ax is None:
                continue
            ia = idx[(b == bb) & (team == 1)]
            ib = idx[(b == bb) & (team == -1)]
            if len(ia) == 0 or len(ib) == 0:
                continue
            mA.append(float((Xc[ia] @ ax).mean()))
            mB.append(float((Xc[ib] @ ax).mean()))
            par.append(bb % 2)
        mA, mB, par = np.array(mA), np.array(mB), np.array(par)
        # demean WITHIN parity: odd and even bins use different cross-fitted axes, so their common-mode offsets differ;
        # demeaning over all bins leaves an alternating offset shared by both blocks (rho biased +0.10 in synthetic E4)
        keep = np.zeros(len(par), dtype=bool)
        for q in (0, 1):
            m = par == q
            if m.sum() >= 2:
                mA[m] -= mA[m].mean(); mB[m] -= mB[m].mean(); keep |= m
        if keep.sum() >= 2:
            series.append((mA[keep], mB[keep]))
    return series


def fluct_tests(series, n_perm=5000, rng=0):
    r = L.sublattice_fluct(series)
    if not np.isfinite(r["rho"]):
        return r
    nul = L.fluct_perm_null(series, n_perm, rng)
    r["p_rho_neg"] = L.p_lower(r["rho"], nul)
    r["rho_null_q05"] = float(np.quantile(nul, 0.05))
    r["n_debates"] = len(series)
    return r


# ------------------------------------------------------------------------------------------------ family confound
def lab_overlap(debates, lab_of):
    """Were teams lab-sorted? Observed share of same-lab pairs within teams vs. its expectation over partitions."""
    obs, exp = [], []
    for deb in debates:
        ag = list(deb["gov"]) + list(deb["opp"])
        eps = np.array([1] * len(deb["gov"]) + [-1] * len(deb["opp"]))
        labs = np.array([lab_of[a] for a in ag])

        def stat(e):
            iu = np.triu_indices(len(e), 1)
            same_team = e[iu[0]] == e[iu[1]]
            same_lab = labs[iu[0]] == labs[iu[1]]
            return same_lab[same_team].mean() - same_lab[~same_team].mean() if same_lab.any() else 0.0

        obs.append(stat(eps))
        exp.append(np.mean([stat(e) for e in L.partitions(len(eps), len(deb["gov"]))]))
    return {"lab_sorting_obs": float(np.mean(obs)), "lab_sorting_null": float(np.mean(exp)), "per_debate": [float(x) for x in obs]}


def pair_regression(windows, lab_of, n_perm=5000, rng=0):
    """cos_ij = b0 + b_team * same_team + b_lab * same_lab (+ debate FE via within-debate demeaning).
    p for b_team from re-partitioning teams within debates (labs fixed)."""
    rng = np.random.default_rng(rng)

    def fit(eps_list):
        y, xt, xl = [], [], []
        for w, eps in zip(windows, eps_list):
            G = w["S"] @ w["S"].T
            iu = np.triu_indices(len(eps), 1)
            labs = np.array([lab_of[a] for a in w["agents"]])
            yy = G[iu]; tt = (eps[iu[0]] == eps[iu[1]]).astype(float); ll = (labs[iu[0]] == labs[iu[1]]).astype(float)
            y.append(yy - yy.mean()); xt.append(tt - tt.mean()); xl.append(ll - ll.mean())
        y, xt, xl = map(np.concatenate, (y, xt, xl))
        Xm = np.column_stack([xt, xl])
        beta, *_ = np.linalg.lstsq(Xm, y, rcond=None)
        return beta

    b = fit([w["eps"] for w in windows])
    parts = [L.partitions(len(w["eps"]), int((w["eps"] == 1).sum())) for w in windows]
    nul = np.array([fit([p[rng.integers(0, len(p))] for p in parts])[0] for _ in range(n_perm)])
    return {"b_team": float(b[0]), "b_lab": float(b[1]), "p_team": L.p_upper(b[0], nul)}


def to_np(st_pl):
    """polars statements -> dict of numpy arrays used above."""
    return {"debate": st_pl["debate"].to_numpy().astype(int), "agent": st_pl["agent"].to_numpy().astype(int),
            "phase": np.array(st_pl["phase"].to_list(), dtype=object), "ts": st_pl["ts"].to_numpy().astype(float)}


def pair_fe_regression(windows, n_perm=5000, rng=0, n_iter=50):
    """Within-pair contrast: cos_ij(d) = a_ij + g_d + b * same_team_ij(d) (two-way demeaned).

    Controls ANY persistent pair similarity (shared family, style, participation offsets): b is identified only
    from pairs that are team-mates in some debates and opponents in others. p from re-partitioning teams
    within debates (pair and debate effects re-estimated each draw)."""
    rng = np.random.default_rng(rng)
    recs = []
    for k, w in enumerate(windows):
        G = w["S"] @ w["S"].T
        iu = np.triu_indices(len(w["eps"]), 1)
        for a, b in zip(*iu):
            p = (min(w["agents"][a], w["agents"][b]), max(w["agents"][a], w["agents"][b]))
            recs.append((k, p, a, b, G[a, b]))
    deb = np.array([r[0] for r in recs])
    pairs = sorted({r[1] for r in recs})
    pid = np.array([pairs.index(r[1]) for r in recs])
    y = np.array([r[4] for r in recs])
    ia = np.array([r[2] for r in recs]); ib = np.array([r[3] for r in recs])

    def demean2(v):
        v = v.astype(float).copy()
        for _ in range(n_iter):
            for g in (pid, deb):
                m = np.bincount(g, v) / np.bincount(g)
                v -= m[g]
        return v

    yd = demean2(y)

    def beta(eps_list):
        x = np.array([eps_list[k][a] == eps_list[k][b] for k, a, b in zip(deb, ia, ib)], dtype=float)
        xd = demean2(x)
        den = (xd * xd).sum()
        return (xd * yd).sum() / den if den > 0 else np.nan, x

    b_obs, x_obs = beta([w["eps"] for w in windows])
    # identification: pairs that are sometimes team-mates and sometimes opponents
    switch = sum(1 for q in range(len(pairs)) if 0 < x_obs[pid == q].mean() < 1)
    parts = [L.partitions(len(w["eps"]), int((w["eps"] == 1).sum())) for w in windows]
    nul = np.array([beta([p[rng.integers(0, len(p))] for p in parts])[0] for _ in range(n_perm)])
    return {"b_team_pairFE": float(b_obs), "p_team_pairFE": L.p_upper(b_obs, nul[np.isfinite(nul)]),
            "n_pairs": len(pairs), "n_switching_pairs": int(switch), "n_obs": int(len(y))}
