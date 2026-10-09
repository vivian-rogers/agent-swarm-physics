"""H146 per-pattern statistics P1-P6 on a Coding + element set K (used by run_real.py and the synthetic checks)."""
from __future__ import annotations

import numpy as np
import polars as pl

import h146lib as L

H2 = 2 * 3600 * L.US


# ------------------------------------------------------------------------------------------------- P1, P2, O1b
def p1_all(ev, cod, pn, ctrl, K_slugs=()):
    at, y, info = L.adoption_rows(ev, cod, pn)
    Xd = L.exposures(ev, pn, host_only=True)
    out = {"adoption": info}
    o = L.p1_fit(ev, Xd, at, y, ctrl=ctrl)
    out["P1_adopt"] = o
    o2 = L.p1_fit(ev, Xd, at, y, split_named=True, ctrl=ctrl)
    out["P2_adopt"] = o2
    # O1b (Amendment A1): expression response of non-hosts (no host bin in the previous 2-h bin and earlier today)
    nh = nonhost_rows(ev, cod, pn)
    ye = pn.row_own > 0
    out["O1b"] = L.p1_fit(ev, Xd, nh, ye, ctrl=ctrl)
    out["O1b_named"] = L.p1_fit(ev, Xd, nh, ye, split_named=True, ctrl=ctrl)
    Xh = L.exposures(ev, pn, host_only=True, nohub=True)
    out["O1b_nohub"] = L.p1_fit(ev, Xh, nh, ye, ctrl=ctrl)
    Xa = L.exposures(ev, pn, host_only=False)
    out["O1b_anysender"] = L.p1_fit(ev, Xa, nh, ye, ctrl=ctrl)
    out["n_nonhost_rows"] = int(nh.sum()); out["n_nonhost_events"] = int((ye & nh).sum())
    return out


def nonhost_rows(ev, cod, pn):
    """Talk rows whose agent had no host bin of K earlier the same PT day (expression-response risk set)."""
    a = ev.a
    out = np.zeros(a["n_rows"], bool)
    for g in np.unique(a["row_agent"]):
        rows = np.where(a["row_agent"] == g)[0]
        s = (cod.ab_agent == g) & pn.host_ab
        hb = np.sort(cod.ab_bin[s]); hd = cod.ab_day[s][np.argsort(cod.ab_bin[s])]
        j = np.searchsorted(hb, a["row_bin"][rows], "left") - 1
        last_d = np.where(j >= 0, hd[np.clip(j, 0, None)], -1) if hb.size else np.full(len(rows), -1)
        out[rows] = last_d < a["row_day"][rows]
    return out


# --------------------------------------------------------------------------------------------------------- P3
def p3_newcomers(ev, cod, pn, ctrl, days=2):
    a = ev.a
    nc = {n["agent"]: n for n in ev.newcomers}
    act = L.agent_days(ev)
    rows = np.zeros(a["n_rows"], bool)
    for g, n in nc.items():
        ad = act.get(int(g), np.array([], dtype=int))[:days]
        rows |= (a["row_agent"] == g) & np.isin(a["row_day"], ad)
    ye = pn.row_own > 0
    Xd = L.exposures(ev, pn, host_only=True)
    fit = L.p1_fit(ev, Xd, rows, ye, ctrl=ctrl) if rows.sum() > 20 and (ye & rows).sum() >= 3 else None
    # descriptive O2: per newcomer, share of first-2-day talk rows carrying K, and K share of items read / in flight
    desc = {}
    for g in nc:
        r = rows & (a["row_agent"] == g)
        if r.sum() == 0:
            continue
        desc[int(g)] = {"rows": int(r.sum()), "expr_share": float(ye[r].mean()),
                        "read_K": float(Xd["Rm"][r].sum() + Xd["Rc_rest"][r].sum()),
                        "fly_K": float(Xd["P"][r].sum()), "first_row_t": int(a["row_t"][r & ye].min())
                        if (r & ye).any() else None}
    return {"fit": fit, "rows": int(rows.sum()), "events": int((ye & rows).sum()), "per_newcomer": desc}


# --------------------------------------------------------------------------------------------------------- P5
def p5_repair(ev, cod, pn, E4, B=300, seed=0, skel_only=False):
    """Named K messages from other hosts to host i in the 2 h after (a) a forced wipe vs placebo call, (b) a challenge
    vs a non-challenge reply to i's K statement, (c) a lapse vs a continuing host day (window at the start of the
    following active day; Amendment A3)."""
    a = ev.a
    rep = L.repair_times(ev, pn)
    out = {}
    skel = {}   # per subtest: (event mask, agent, strata, cluster, counts) for the power check (power146.p5_power)
    # (a) wipes: host events from P4
    if E4 is not None and len(E4["F"]):
        cnt = np.array([L.count_in(rep, g, t, t + H2) for g, t in zip(E4["agent"], E4["t"])], dtype=float)
        s = L.strata_codes(E4["agent"], E4["unit"])
        cl = E4["agent"] * 1000 + E4["day"]
        F = E4["F"]
        skel["wipe"] = (F, E4["agent"], s, cl, cnt)
        if not skel_only:
          rr, lo, hi, _ = L.cluster_boot_rr(np.where(F, cnt, 0), F.astype(float), np.where(~F, cnt, 0),
                                            (~F).astype(float), s, cl, B=B, seed=seed)
          out["wipe"] = {"rr": rr, "ci": [lo, hi], "n_F": int(F.sum()), "n_P": int((~F).sum()),
                       "msgs_F": float(cnt[F].sum()), "msgs_P": float(cnt[~F].sum())}
    # (b) challenges
    ch = ev.chg
    am = ch["a_msg"].to_numpy(); ag = ch["a_agent"].to_numpy().astype(np.int64); tb = ch["t_b"].to_numpy()
    bm = ch["b_msg"].to_numpy()
    kk = pn.carries[am] > 0
    st2 = ch["stance2"].to_list()
    neutral = np.array([x in ("agree", "acknowledge", "coordinate", "inform", "ask") for x in st2]) & \
        ~ch["opposes"].to_numpy()
    bm_rep = pn.carries_host[bm] & np.array([ag_ in (a["msg_mentions"][m] or []) for m, ag_ in zip(bm, ag)])
    dix = {d: i for i, d in enumerate(a["days"])}
    for lab, ev_mask in (("challenge_val", ch["disagree_val"].to_numpy()), ("challenge_dq2", ch["opposes"].to_numpy())):
        e = kk & ev_mask; p = kk & neutral & ~ch["disagree_val"].to_numpy()
        sel = e | p
        if e.sum() < 3 or p.sum() < 3:
            out[lab] = {"n_events": int(e.sum()), "n_placebo": int(p.sum()), "rr": None}
            continue
        cnt = np.array([L.count_in(rep, g, t, t + H2) for g, t in zip(ag[sel], tb[sel])], dtype=float)
        cnt = cnt - bm_rep[sel]  # the challenging / placebo reply itself does not count
        E_ = e[sel]
        day = (tb[sel] // (24 * 3600 * L.US))
        s = L.strata_codes(ag[sel])
        skel[lab] = (E_, ag[sel], s, ag[sel] * 100000 + day, cnt)
        if skel_only:
            continue
        rr, lo, hi, _ = L.cluster_boot_rr(np.where(E_, cnt, 0), E_.astype(float), np.where(~E_, cnt, 0),
                                          (~E_).astype(float), s, ag[sel] * 100000 + day, B=B, seed=seed + 1)
        out[lab] = {"rr": rr, "ci": [lo, hi], "n_events": int(E_.sum()), "n_placebo": int((~E_).sum()),
                    "msgs_events": float(cnt[E_].sum()), "msgs_placebo": float(cnt[~E_].sum())}
    # (c) lapses
    act = L.agent_days(ev)
    ct = L.call_times(ev)
    car_t = np.sort(a["msg_t"][pn.carries > 0])
    rows = []
    for g in np.unique(cod.ab_agent):
        s_ = (cod.ab_agent == g) & pn.host_ab
        hdays = set(cod.ab_day[s_].tolist())
        ad = act.get(int(g), np.array([], dtype=int))
        cts = ct.get(int(g))
        if cts is None or len(ad) < 3:
            continue
        for k in range(len(ad) - 2):
            if ad[k] not in hdays:
                continue
            lapse = ad[k + 1] not in hdays
            # window: the first 2 h from the agent's first call on day ad[k+2]
            d2 = ad[k + 2]
            t0 = first_call_on_day(ev, g, d2)
            if t0 is None:
                continue
            n = L.count_in(rep, g, t0, t0 + H2)
            act_k = np.searchsorted(car_t, t0 + H2, "right") - np.searchsorted(car_t, t0, "right")
            rows.append((lapse, g, d2, n, act_k))
    if rows:
        R = np.array(rows, dtype=float)
        lap = R[:, 0] > 0; g = R[:, 1].astype(int); d2 = R[:, 2].astype(int); n = R[:, 3]; ak = R[:, 4]
        terc = np.digitize(ak, np.quantile(ak, [1 / 3, 2 / 3])) if len(ak) > 3 else np.zeros(len(ak), int)
        s = L.strata_codes(g, terc)
        skel["lapse"] = (lap, g, s, g * 1000 + d2, n)
        if skel_only:
            pass
        elif lap.sum() >= 3 and (~lap).sum() >= 3:
            rr, lo, hi, _ = L.cluster_boot_rr(np.where(lap, n, 0), lap.astype(float), np.where(~lap, n, 0),
                                              (~lap).astype(float), s, g * 1000 + d2, B=B, seed=seed + 2)
        else:
            rr = lo = hi = None
        if not skel_only:
            out["lapse"] = {"rr": rr, "ci": [lo, hi], "n_lapse": int(lap.sum()), "n_cont": int((~lap).sum()),
                            "msgs_lapse": float(n[lap].sum()), "msgs_cont": float(n[~lap].sum())}
    if skel_only:
        return skel
    return out


def first_call_on_day(ev, g, day):
    a = ev.a
    if "first_call" not in a:
        c = ev.calls.group_by("agent", "pt_date").agg(pl.col("t_call").min())
        dix = {d: i for i, d in enumerate(a["days"])}
        a["first_call"] = {(int(r[0]), dix[r[1]]): int(r[2]) for r in c.iter_rows() if r[1] in dix}
    return a["first_call"].get((int(g), int(day)))


# --------------------------------------------------------------------------------------------------------- P6
def spec_triples(cod, pn, K):
    rows = np.where(pn.host_ab)[0]
    sub = cod.M_ab[rows][:, K].tocoo()
    h = cod.ab_agent[rows][sub.row]; b = cod.ab_bin[rows][sub.row]; e = K[sub.col]
    # bins with >= 2 hosts
    ub, inv, cnt = np.unique(b, return_inverse=True, return_counts=False), None, None
    hb = np.unique(np.column_stack([b, h]), axis=0)
    bb, nh = np.unique(hb[:, 0], return_counts=True)
    keep = np.isin(b, bb[nh >= 2])
    return h[keep], e[keep], b[keep]


def p6_spec(cod, pn, K, rng, n_perm=200, h_stop=10):
    h, e, b = spec_triples(cod, pn, K)
    if len(h) < 20:
        return None
    S = L.mi_host_element(h, e)
    null = []
    exc = 0
    for i in range(n_perm):
        v = L.mi_host_element(L.perm_within_bin(e, b, rng, h), e)
        null.append(v)
        exc += v >= S
        if exc >= h_stop:
            break
    null = np.array(null)
    sd = null.std() if null.std() > 0 else np.nan
    return {"S_bits": S, "null_mean": float(null.mean()), "z": float((S - null.mean()) / sd),
            "p": float((exc + 1) / (len(null) + 1)), "n_perm": len(null), "n_triples": int(len(h)),
            "n_bins": int(len(np.unique(b))), "n_hosts": int(len(np.unique(h)))}


def presence(ev):
    a = ev.a
    if "pres" not in a:
        c = ev.calls.select("agent", "t_call")
        ag = c["agent"].to_numpy().astype(np.int64); b = c["t_call"].to_numpy() // L.BIN_US
        k = np.unique(ag * 10**9 + b)
        a["pres"] = k
        # bin covariates: time of day (2-h of UTC day), exogenous items, village agent messages
        mb = a["msg_bin"]; sk = ev.msgs["skind"].to_numpy()
        a["bin_exo"] = dict(zip(*np.unique(mb[sk != 0], return_counts=True)))
        a["bin_msgs"] = dict(zip(*np.unique(mb[sk == 0], return_counts=True)))
    return a["pres"]


def omega_matrix(ev, cod, pn, max_hosts=8, min_host_bins=10):
    pres = presence(ev)
    hosts_ab = np.where(pn.host_ab)[0]
    ag, cnt = np.unique(cod.ab_agent[hosts_ab], return_counts=True)
    top = np.array([g for g, c in zip(ag[np.argsort(-cnt)][:max_hosts], np.sort(cnt)[::-1][:max_hosts])
                    if c >= min_host_bins])
    if len(top) < 3:
        return None
    # bins where all selected hosts are present
    bins = None
    for g in top:
        bg = pres[(pres // 10**9) == g] % 10**9
        bins = set(bg.tolist()) if bins is None else bins & set(bg.tolist())
    bins = np.array(sorted(bins))
    if len(bins) < 30:
        return None
    key_ab = cod.ab_agent.astype(np.int64) * 10**9 + cod.ab_bin
    X = np.zeros((len(bins), len(top)))
    for j, g in enumerate(top):
        kk = g * 10**9 + bins
        pos = np.clip(np.searchsorted(key_ab, kk), 0, len(key_ab) - 1)
        ok = key_ab[pos] == kk
        X[ok, j] = pn.host_ab[pos[ok]]
    a = ev.a
    tod = (bins % 12)
    Z = np.column_stack([(tod == k).astype(float) for k in np.unique(tod)[1:]] +
                        [np.array([a["bin_exo"].get(b, 0) for b in bins], float),
                         np.log1p(np.array([a["bin_msgs"].get(b, 0) for b in bins], float))])
    return X, Z, top, bins


def p6_omega(ev, cod, pn, rng, n_surr=100):
    M = omega_matrix(ev, cod, pn)
    if M is None:
        return None
    X, Z, top, bins = M
    keep = X.std(0) > 0
    if keep.sum() < 3:
        return None
    X = X[:, keep]; top = top[keep]
    n = X.shape[1]
    om = L.o_information_discrete(X) / (n - 2)
    om_g = L.o_information(L.field_removed(X, Z)) / (n - 2)
    sur = []
    B = X.T.astype(np.int8)
    for _ in range(n_surr):
        Bs = L.curveball(B, rng, n_iter=20 * n)
        Xs = Bs.T.astype(float)
        if (Xs.std(0) == 0).any():
            continue
        sur.append(L.o_information_discrete(Xs) / (n - 2))
    sur = np.array(sur)
    return {"omega_per": om, "omega_gauss_fieldremoved_per": om_g, "n_hosts": int(n), "n_bins": int(len(bins)),
            "sur_p05": float(np.percentile(sur, 5)) if len(sur) else None,
            "sur_p95": float(np.percentile(sur, 95)) if len(sur) else None,
            "sur_mean": float(sur.mean()) if len(sur) else None, "hosts": [int(x) for x in top]}
