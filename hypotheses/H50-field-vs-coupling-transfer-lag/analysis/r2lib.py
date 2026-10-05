"""H50 round-2 estimators (card: "Round 2").

R1 content gate: rows (source message m, recipient j, j's statement B after t_m) with hop h of B's producing call
   relative to j's read-out call of m; outcome y = cos(z_B, z_m) - cos(z_B, z_m') (m' = same sender, >= 2 h away);
   matched-age jump J^c_h = sum_b w_b [ybar(h, b) - ybar(0, b)] over 10-s age bins (H29's control).
R6 relay event study: see relay_* functions.
Synthetic generators that keep the real skeleton (messages, reads, producing calls) and replace only the vectors
(content) or the call outcomes (talk).

Inputs: U = round-1 unit (scheme/build.py load_unit), R = round-2 unit (scheme/build_r2.py npz as dict).
"""
from __future__ import annotations

import numpy as np

BINS = np.arange(0, 61, 10.0)        # age bins (s) for the matched-age jump
HMAX = 6


def load_r2(path):
    z = np.load(path)
    return {k: z[k] for k in z.files}


def blocks_for(U, t, d, min_days=3):
    """Day blocks if >= min_days days, else 1-hour blocks (as h50lib.blocks). min_days=None: always 1-hour blocks."""
    D = len(U["day_t0"])
    if min_days is not None and len(np.unique(d)) >= min_days:
        return d.astype(np.int64), D
    h = np.clip(((t - U["day_t0"][d]) // 3600).astype(np.int64), 0, 47)
    return d.astype(np.int64) * 48 + h, D * 48


def placebo_index(R, rng, min_sep=7200.0, n=2):
    """For each message: n random statements (message indices) of the same sender >= min_sep s away (or -1)."""
    t, s = R["m_t"], R["m_sender"]
    has = R["m_srow"] >= 0
    out = np.full((len(t), n), -1, np.int64)
    for a in np.unique(s[s >= 0]):
        idx = np.where((s == a) & has)[0]
        if len(idx) < 2:
            continue
        ta = t[idx]
        for i in idx:
            far = idx[np.abs(ta - t[i]) >= min_sep]
            if len(far):
                out[i] = rng.choice(far, n)
    return out


def content_rows(U, R, Zm, plc, max_next=8, max_age=1800.0):
    """Rows for the content gate. Zm: [n_msgs, d] unit vectors (nan rows = no vector). plc: placebo indices [n_msgs, k].
    Returns dict of arrays: pair, src, B, rec, h, age, lat, y_raw, y (placebo-corrected), ment, day."""
    c = U["calls"]
    t, snd, prod = R["m_t"], R["m_sender"], R["m_prod"]
    okv = ~np.isnan(Zm[:, 0])
    pm, pr, pp, pment = R["p_msg"], R["p_rec"], R["p_pos"], R["p_ment"]
    use = okv[pm] & (snd[pm] >= 0)
    rows = {k: [] for k in ("pair", "src", "B", "h", "age", "lat", "ment", "day")}
    for j in np.unique(pr[use]):
        S = np.where((snd == j) & okv & (prod >= 0))[0]          # j's statements (time-sorted)
        if len(S) == 0:
            continue
        TS = t[S]
        P = np.where(use & (pr == j))[0]
        tm = t[pm[P]]
        i0 = np.searchsorted(TS, tm, side="right")
        for k in range(max_next):
            ii = i0 + k
            ok = ii < len(S)
            Pk, Bk = P[ok], S[ii[ok]]
            age = t[Bk] - t[pm[Pk]]
            hb = prod[Bk] - pp[Pk] + 1
            ok2 = (age <= max_age) & (c["day"][prod[Bk]] == c["day"][pp[Pk]]) & (hb >= 0) & (hb <= HMAX)
            Pk, Bk, age, hb = Pk[ok2], Bk[ok2], age[ok2], hb[ok2]
            rows["pair"].append(Pk)
            rows["src"].append(pm[Pk])
            rows["B"].append(Bk)
            rows["h"].append(hb)
            rows["age"].append(age)
            rows["lat"].append(t[Bk] - c["tc"][prod[Bk]])
            rows["ment"].append(pment[Pk])
            rows["day"].append(c["day"][pp[Pk]])
    out = {k: (np.concatenate(v) if v else np.zeros(0)) for k, v in rows.items()}
    for k in ("pair", "src", "B", "h", "day"):
        out[k] = out[k].astype(np.int64)
    out["ment"] = out["ment"].astype(bool)
    out["t_src"] = t[out["src"]] if len(out["src"]) else np.zeros(0)
    zb, zs = Zm[out["B"]], Zm[out["src"]]
    out["y_raw"] = np.einsum("ij,ij->i", zb, zs)
    pc = []
    for q in range(plc.shape[1]):
        pi = plc[out["src"], q]
        v = np.where(pi >= 0, np.einsum("ij,ij->i", zb, Zm[np.maximum(pi, 0)]), np.nan)
        pc.append(v)
    out["y_pl"] = np.nanmean(np.vstack(pc), 0) if len(pc) else np.full(len(zb), np.nan)
    out["y"] = out["y_raw"] - out["y_pl"]
    return out


def _cells(rows, yname, blk, nblk, sel, bins=BINS, hs=(0, 1, 2, 3), lat_t=None):
    """Sum and count per (block, hop, age bin[, latency tercile]) for the selected rows."""
    y = rows[yname]
    ok = sel & np.isfinite(y) & (rows["age"] >= bins[0]) & (rows["age"] < bins[-1]) & np.isin(rows["h"], hs)
    b = np.digitize(rows["age"][ok], bins) - 1
    hh = np.searchsorted(np.array(hs), rows["h"][ok])
    nl = 1 if lat_t is None else 3
    li = np.zeros(ok.sum(), np.int64) if lat_t is None else lat_t[ok]
    shape = (nblk, len(hs), len(bins) - 1, nl)
    S = np.zeros(shape)
    N = np.zeros(shape)
    np.add.at(S, (blk[ok], hh, b, li), y[ok])
    np.add.at(N, (blk[ok], hh, b, li), 1.0)
    return S, N


def _jump_from_cells(S, N, w=None):
    """Matched-age jumps J_h (h index >= 1 vs index 0) from summed cells; w = block weights."""
    if w is None:
        Ss, Ns = S.sum(0), N.sum(0)
    else:
        Ss, Ns = np.tensordot(w, S, 1), np.tensordot(w, N, 1)
    out = []
    n0, s0 = Ns[0], Ss[0]
    for h in range(1, Ss.shape[0]):
        nh, sh = Ns[h], Ss[h]
        ok = (n0 > 0) & (nh > 0)
        if not ok.any():
            out.append(np.nan)
            continue
        wt = np.where(ok, n0 * nh / np.maximum(n0 + nh, 1e-9), 0.0)
        d = np.where(ok, sh / np.maximum(nh, 1e-9) - s0 / np.maximum(n0, 1e-9), 0.0)
        out.append(float((wt * d).sum() / wt.sum()))
    return np.array(out)


def matched_age_jump(rows, U, yname="y", sel=None, nboot=400, seed=0, bins=BINS, hs=(0, 1, 2, 3), lat_match=False):
    """J^c_h for h in hs[1:], with block-bootstrap CIs. Returns dict(J, lo, hi, se, n_cells)."""
    if sel is None:
        sel = np.ones(len(rows["h"]), bool)
    blk, nblk = blocks_for(U, rows["t_src"], rows["day"])
    lat_t = None
    if lat_match:
        q = np.nanpercentile(rows["lat"], [33.3, 66.7])
        lat_t = np.digitize(rows["lat"], q)
    S, N = _cells(rows, yname, blk, nblk, sel, bins, hs, lat_t)
    J = _jump_from_cells(S, N)
    rng = np.random.default_rng(seed)
    used = np.where(N.sum((1, 2, 3)) > 0)[0]
    bs = []
    if len(used) >= 2:
        for _ in range(nboot):
            w = np.bincount(rng.choice(used, len(used)), minlength=nblk).astype(float)
            bs.append(_jump_from_cells(S, N, w))
    bs = np.array(bs) if bs else np.full((1, len(J)), np.nan)
    Nh = N.sum((0, 2, 3))
    return dict(J=J, lo=np.nanpercentile(bs, 2.5, 0), hi=np.nanpercentile(bs, 97.5, 0), se=np.nanstd(bs, 0),
                n_h=Nh, n_blocks=int(len(used)))


def unmatched_contrast(rows, yname="y", sel=None, amax=60.0):
    """H29's naive visible-minus-invisible contrast (hop 1 minus hop 0, ages < amax, no matching)."""
    if sel is None:
        sel = np.ones(len(rows["h"]), bool)
    y = rows[yname]
    ok = sel & np.isfinite(y) & (rows["age"] < amax)
    a = y[ok & (rows["h"] == 1)]
    b = y[ok & (rows["h"] == 0)]
    return float(a.mean() - b.mean()) if len(a) and len(b) else np.nan


def hop_profile(rows, yname="y", sel=None, hmax=HMAX):
    if sel is None:
        sel = np.ones(len(rows["h"]), bool)
    y = rows[yname]
    out = []
    for h in range(hmax + 1):
        v = y[sel & (rows["h"] == h) & np.isfinite(y)]
        out.append((float(v.mean()) if len(v) else np.nan, int(len(v))))
    return out


def ivw(est, se):
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    if not ok.any():
        return np.nan, np.nan
    w = 1 / se[ok] ** 2
    m = float((w * est[ok]).sum() / w.sum())
    return m, float(1 / np.sqrt(w.sum()))


# ============================================================================ synthetic content on the real skeleton
def _ou_field(rng, n, d, dt, tau, sig):
    a = np.exp(-dt / tau)
    b = sig * np.sqrt(1 - a * a)
    z = np.empty((n, d))
    z[0] = rng.normal(0, sig, d)
    e = rng.normal(0, 1, (n, d))
    for k in range(1, n):
        z[k] = a * z[k - 1] + b * e[k]
    return z


def syn_content(U, R, prm, seed=0, d=32):
    """Synthetic statement vectors for every message of the unit, with the real skeleton.
    prm: rho (own persistence), sig_slow, tau_slow, sig_fast, tau_fast, sig_n, a (pull), named (multiplier), lam
    (decay of the pull accumulator per own statement), mode in {gated, dead1, ungated}.
    Returns Zm [n, d] (unit vectors) and truth dict {(src, B): marginal effect of src on cos(z_B, z_src)}."""
    rng = np.random.default_rng(seed)
    c = U["calls"]
    t, snd, room, day = R["m_t"], R["m_sender"], R["m_room"], R["m_day"]
    n = len(t)
    pm, pr, pp, pment = R["p_msg"], R["p_rec"], R["p_pos"], R["p_ment"]
    dt_ = 5.0
    fields = {}
    for dd in range(len(U["day_t0"])):
        t0, t1 = U["day_t0"][dd], U["day_t1"][dd]
        ng = int((t1 - t0) / dt_) + 2
        for r in np.unique(room[day == dd]):
            fields[(dd, r)] = (t0, _ou_field(rng, ng, d, dt_, prm["tau_slow"], prm["sig_slow"])
                               + _ou_field(rng, ng, d, dt_, prm["tau_fast"], prm["sig_fast"]))
    Zm = np.zeros((n, d))
    N = int(U["N"])
    prev = np.zeros((N, d))
    P = np.zeros((N, d))
    ptr = np.zeros(N, np.int64)                   # pointer into the agent's pair list (sorted by p_pos)
    pairs_by = [np.where(pr == j)[0] for j in range(N)]  # already sorted by (rec, p_pos)
    room_msgs = {}
    rptr = {}
    tc = c["tc"]
    truth = {}
    mode = prm.get("mode", "gated")
    for i in range(n):
        dd, r = day[i], room[i]
        t0, F = fields[(dd, r)]
        k = min(max(int((t[i] - t0) / dt_), 0), len(F) - 1)
        j = snd[i]
        v = F[k] + prm["sig_n"] * rng.normal(0, 1, d)
        new = []
        if j >= 0:
            if mode in ("gated", "dead1"):
                L = pairs_by[j]
                q = ptr[j]
                lim = t[i] if mode == "gated" else (tc[R["m_prod"][i]] if R["m_prod"][i] >= 0 else t[i])
                while q < len(L) and tc[pp[L[q]]] < lim:
                    m = pm[L[q]]
                    if day[m] == dd and m < i:
                        wgt = prm["named"] if pment[L[q]] else 1.0
                        new.append((m, wgt, pp[L[q]]))
                    q += 1
                ptr[j] = q
            else:   # ungated: every message by others in the agent's room posted before t_B, read or not
                key = (dd, r)
                if key not in room_msgs:
                    room_msgs[key] = np.where((day == dd) & (room == r))[0]
                    rptr[key] = {}
                lst = room_msgs[key]
                q = rptr[key].get(j, 0)
                while q < len(lst) and lst[q] < i:
                    m = lst[q]
                    if snd[m] != j:
                        new.append((m, 1.0, -1))
                    q += 1
                rptr[key][j] = q
            for (m, wgt, _) in new:
                P[j] += wgt * Zm[m]
            v = v + prm["rho"] * prev[j] + prm["a"] * P[j]
        nv = np.linalg.norm(v)
        z = v / nv
        Zm[i] = z
        if j >= 0:
            pr_i = R["m_prod"][i]
            for (m, wgt, ppos) in new:
                if ppos == pr_i and pr_i >= 0:          # read by the producing call: hop-1 truth
                    v0 = v - prm["a"] * wgt * Zm[m]
                    truth[(m, i)] = float(z @ Zm[m] - (v0 / np.linalg.norm(v0)) @ Zm[m])
            prev[j] = z
            P[j] *= prm["lam"]
    return Zm.astype(np.float32), truth


def truth_hop1(rows, truth, sel=None, amax=60.0):
    if sel is None:
        sel = np.ones(len(rows["h"]), bool)
    ok = sel & (rows["h"] == 1) & (rows["age"] < amax)
    v = [truth.get((int(s), int(b)), np.nan) for s, b in zip(rows["src"][ok], rows["B"][ok])]
    v = np.array(v, float)
    return float(np.nanmean(v)) if np.isfinite(v).any() else np.nan


# ============================================================================ R6 relay event study
EV_BINS = (-3, -2, -1, 0, 1, 2)      # event time e = h - rho, ends binned; e = -1 is the reference


def relay_pairs(U, R, rho_max=5, hmax=6):
    """(A, C) pairs with a relay: B (not A's sender) posts m_B at its read-out call of A; C (not a, not B) reads A and
    m_B. rho = C-hop (on A's clock) of the call that reads the earliest-read relay. Also returns (A, C) pairs that C
    read with no relay read by hop hmax (never-treated controls).
    Returns dict: A, C, posA, rho (0 = no relay by hmax), relay (msg idx or -1), named (relay names C), day, tA."""
    c = U["calls"]
    pm, pr, pp, pment = R["p_msg"], R["p_rec"], R["p_pos"], R["p_ment"]
    snd, prod = R["m_sender"], R["m_prod"]
    n = len(c["tc"])
    # relay messages: index (agent, prod position) -> first message posted by that call
    rel_by = {}
    for i in np.where((prod >= 0) & (snd >= 0))[0]:
        rel_by.setdefault((int(snd[i]), int(prod[i])), i)
    key = pm.astype(np.int64) * 64 + pr                       # (msg, rec) -> pair row
    order = np.argsort(key)
    ks = key[order]

    def lookup(msgs, recs):
        q = msgs.astype(np.int64) * 64 + recs
        i = np.searchsorted(ks, q)
        i = np.minimum(i, len(ks) - 1)
        ok = ks[i] == q
        return np.where(ok, order[i], -1)
    # relays: for each pair (A, B) whose read-out call posted a message
    relA, relB, relM = [], [], []
    for row in range(len(pm)):
        m = rel_by.get((int(pr[row]), int(pp[row])))
        if m is not None and snd[pm[row]] != pr[row] and m != pm[row]:
            relA.append(pm[row])
            relB.append(pr[row])
            relM.append(m)
    relA, relB, relM = np.array(relA, np.int64), np.array(relB, np.int64), np.array(relM, np.int64)
    # readers C of each relay message
    best = {}
    by_msg = {}
    for row in np.argsort(pm, kind="stable"):
        by_msg.setdefault(int(pm[row]), []).append(row)
    for A, B, M in zip(relA, relB, relM):
        for row in by_msg.get(int(M), []):
            C = int(pr[row])
            if C == snd[A] or C == B:
                continue
            ra = lookup(np.array([A]), np.array([C]))[0]
            if ra < 0:
                continue
            pa, pmb = int(pp[ra]), int(pp[row])
            if c["day"][pa] != c["day"][pmb]:
                continue
            rho = pmb - pa + 1
            k = (int(A), C)
            if rho >= 1 and (k not in best or rho < best[k][1]):
                best[k] = (pa, rho, int(M), bool(pment[row]))
    out = {k: [] for k in ("A", "C", "posA", "rho", "relay", "named")}
    for (A, C), (pa, rho, M, nm) in best.items():
        out["A"].append(A); out["C"].append(C); out["posA"].append(pa)
        out["rho"].append(rho if rho <= hmax else 0); out["relay"].append(M); out["named"].append(nm)
    # never-treated: C read A, A has at least one reader, no relay read by hop hmax
    have = set(best)
    okA = snd[pm] >= 0
    for row in np.where(okA)[0]:
        k = (int(pm[row]), int(pr[row]))
        if k in have:
            continue
        out["A"].append(k[0]); out["C"].append(k[1]); out["posA"].append(int(pp[row]))
        out["rho"].append(0); out["relay"].append(-1); out["named"].append(False)
    out = {k: np.asarray(v) for k, v in out.items()}
    out["day"] = c["day"][out["posA"]]
    out["tA"] = R["m_t"][out["A"]]
    del n
    return out


def relay_panel(U, P, y, sel, hmax=6):
    """Long panel (pair, h, y, e) for the selected pairs; calls posA + h - 1 of the same agent and day."""
    c = U["calls"]
    n = len(c["tc"])
    idx = np.where(sel)[0]
    rows_p, rows_h, rows_i = [], [], []
    for h in range(1, hmax + 1):
        ci = P["posA"][idx] + h - 1
        ok = ci < n
        cc = np.minimum(ci, n - 1)
        ok &= (c["agent"][cc] == P["C"][idx]) & (c["day"][cc] == P["day"][idx])
        rows_p.append(idx[ok]); rows_h.append(np.full(ok.sum(), h)); rows_i.append(cc[ok])
    p = np.concatenate(rows_p); h = np.concatenate(rows_h); ci = np.concatenate(rows_i)
    rho = P["rho"][p]
    e = np.where(rho > 0, np.clip(h - rho, EV_BINS[0], EV_BINS[-1]), 99)
    return dict(p=p, h=h, y=y[ci].astype(float), e=e, ci=ci)


def read_counts(U, R):
    """Agent items newly read at each call: [n_calls, 2] (unnamed, named)."""
    n = len(U["calls"]["tc"])
    S = np.zeros((n, 2))
    np.add.at(S, (R["p_pos"], R["p_ment"].astype(int)), 1.0)
    return S


def panel_controls(U, P, pan, S):
    """Other items read at the outcome call and at the call before (unnamed, named), excluding the relay itself."""
    c = U["calls"]
    ci = pan["ci"]
    rel_named = P["named"][pan["p"]].astype(int)
    X = np.zeros((len(ci), 4))
    for lag in (0, 1):
        cj = ci - lag
        ok = (cj >= 0) & (c["agent"][np.maximum(cj, 0)] == c["agent"][ci]) & (c["day"][np.maximum(cj, 0)] == c["day"][ci])
        v = np.where(ok[:, None], S[np.maximum(cj, 0)], 0.0)
        is_rel = (pan["e"] == lag) & ok
        v[np.arange(len(ci)), rel_named] -= is_rel
        X[:, 2 * lag:2 * lag + 2] = v
    return X


def _design(pan, hmax=6):
    h, e = pan["h"], pan["e"]
    cols = [(h == k).astype(float) for k in range(2, hmax + 1)]          # hop effects (h = 1 reference)
    evs = [k for k in EV_BINS if k != -1]
    cols += [(e == k).astype(float) for k in evs]
    return np.vstack(cols).T, evs


def _demean(X, y, g):
    """Within-group demeaning (pair fixed effects)."""
    ng = g.max() + 1
    cnt = np.bincount(g, minlength=ng).astype(float)
    def dm(v):
        s = np.bincount(g, weights=v, minlength=ng)
        return v - (s / np.maximum(cnt, 1))[g]
    return np.column_stack([dm(X[:, j]) for j in range(X.shape[1])]), dm(y)


def event_study(pan, blk, nblk, nboot=200, seed=0, hmax=6, Xc=None):
    """Pair-FE LPM; returns gamma per event bin (e = -1 reference) with block-bootstrap CIs. blk: block per pair row.
    Xc: optional extra covariates (appended after the event dummies)."""
    X, evs = _design(pan, hmax)
    if Xc is not None:
        X = np.hstack([X, Xc])
    _, g = np.unique(pan["p"], return_inverse=True)
    Xd, yd = _demean(X, pan["y"], g)
    b = blk[pan["p"]]
    G = np.zeros((nblk, X.shape[1], X.shape[1]))
    V = np.zeros((nblk, X.shape[1]))
    for j in range(X.shape[1]):
        np.add.at(G[:, j, :], b, Xd[:, j:j + 1] * Xd)
        np.add.at(V[:, j], b, Xd[:, j] * yd)

    def solve(w):
        A = np.tensordot(w, G, 1)
        v = np.tensordot(w, V, 1)
        try:
            return np.linalg.solve(A + 1e-9 * np.eye(len(v)), v)
        except np.linalg.LinAlgError:
            return np.full(len(v), np.nan)
    est = solve(np.ones(nblk))
    used = np.unique(b)
    rng = np.random.default_rng(seed)
    bs = np.array([solve(np.bincount(rng.choice(used, len(used)), minlength=nblk).astype(float)) for _ in range(nboot)])
    nh = hmax - 1
    out = {}
    for k, ev in enumerate(evs):
        j = nh + k
        out[ev] = (float(est[j]), float(np.nanpercentile(bs[:, j], 2.5)), float(np.nanpercentile(bs[:, j], 97.5)),
                   float(np.nanstd(bs[:, j])))
    out["hop"] = [float(x) for x in est[:nh]]
    out["n_pairs"] = int(len(np.unique(pan["p"])))
    out["n_rows"] = int(len(pan["y"]))
    return out


# ============================================================================ synthetic talk on the real skeleton
def syn_talk(U, R, prm, seed=0):
    """Synthetic talk outcome for every call; real calls, real reads. Logit = logit(agent-day talk rate) + phi*Y_prev
    + OU(t) + sum_k dec[k] * S[c - k - dead], S[c] = sum over items read at call c of J (named: J_named).
    Returns y [n_calls] and truth: dict (msg, rec) -> marginal effect of that item on P(talk) at its first effect call."""
    rng = np.random.default_rng(seed)
    c = U["calls"]
    n = len(c["tc"])
    pm, pr, pp, pment = R["p_msg"], R["p_rec"], R["p_pos"], R["p_ment"]
    Jit = np.where(pment, prm["J_named"], prm["J"])
    S = np.zeros(n)
    np.add.at(S, pp, Jit)
    dec = np.exp(-np.arange(prm.get("K", 5)) / prm.get("tau_h", 1.0))
    dead = prm.get("dead", 0)
    eff = np.zeros(n)
    same = np.r_[False, (np.diff(c["agent"]) == 0) & (np.diff(c["day"]) == 0)]
    run_start = np.where(~same)[0]
    run_end = np.r_[run_start[1:], n]
    for a, b in zip(run_start, run_end):
        s = S[a:b]
        full = np.convolve(s, np.r_[np.zeros(dead), dec])[: b - a]
        eff[a:b] = full
    # agent-day base rate (real talk rate, clipped)
    key = c["agent"] * 1000 + c["day"]
    uk, inv = np.unique(key, return_inverse=True)
    rate = np.bincount(inv, weights=c["talk"].astype(float)) / np.bincount(inv)
    rate = np.clip(rate, 0.01, 0.95)
    base = np.log(rate / (1 - rate))[inv] - prm.get("phi", 0.0) * rate[inv]
    if prm.get("len_beta", 0.0):
        # talk depends on the call's own interval to the next call start (pauses are long; chat-mode calls are long)
        nxt = np.r_[c["tc"][1:], np.nan]
        dl = np.where(np.r_[same[1:], False], nxt - c["tc"], np.nan)
        lg = np.log(np.maximum(dl, 1.0))
        lg = np.where(np.isfinite(lg), lg, np.nanmedian(lg))
        base = base + prm["len_beta"] * (lg - lg.mean()) / lg.std()
    ou = np.zeros(n)
    if prm.get("ou_sig", 0) > 0:
        for d in range(len(U["day_t0"])):
            t0, t1 = U["day_t0"][d], U["day_t1"][d]
            ng = int((t1 - t0) / 10) + 2
            z = _ou_field(rng, ng, 1, 10.0, prm.get("ou_tau", 900.0), prm["ou_sig"])[:, 0]
            sel = c["day"] == d
            ou[sel] = z[np.clip(((c["tc"][sel] - t0) // 10).astype(int), 0, ng - 1)]
    H = base + eff + ou
    y = np.zeros(n, bool)
    u = rng.random(n)
    phi = prm.get("phi", 0.0)
    prev = 0.0
    Hf = np.zeros(n)
    for i in range(n):
        if not same[i]:
            prev = 0.0
        Hf[i] = H[i] + phi * prev
        y[i] = u[i] < 1 / (1 + np.exp(-Hf[i]))
        prev = float(y[i])
    truth = {}
    first = pp + dead
    ok = first < n
    fc = np.minimum(first, n - 1)
    ok &= (c["agent"][fc] == pr) & (c["day"][fc] == c["day"][pp])
    p1 = 1 / (1 + np.exp(-Hf[fc]))
    p0 = 1 / (1 + np.exp(-(Hf[fc] - Jit * dec[0])))
    me = np.where(ok, p1 - p0, np.nan)
    for m, r, v in zip(pm, pr, me):
        truth[(int(m), int(r))] = float(v)
    return y, truth


def relay_triples(U, R):
    """All relay read pairs: (A, B, M = B's message posted at its read-out call of A, C reads A and M; C not a, not B).
    Returns arrays A, M, C, posA (C's read-out call of A), posM (C's read call of M), named (M names C), day."""
    c = U["calls"]
    pm, pr, pp, pment = R["p_msg"], R["p_rec"], R["p_pos"], R["p_ment"]
    snd, prod = R["m_sender"], R["m_prod"]
    rel_by = {}
    for i in np.where((prod >= 0) & (snd >= 0))[0]:
        rel_by.setdefault((int(snd[i]), int(prod[i])), i)
    pos_of = {(int(m), int(r)): int(p) for m, r, p in zip(pm, pr, pp)}
    by_msg = {}
    for row in range(len(pm)):
        by_msg.setdefault(int(pm[row]), []).append(row)
    out = {k: [] for k in ("A", "M", "C", "posA", "posM", "named")}
    seen = set()
    for row in range(len(pm)):
        M = rel_by.get((int(pr[row]), int(pp[row])))
        A = int(pm[row])
        if M is None or M == A or snd[A] == pr[row]:
            continue
        for r2 in by_msg.get(int(M), []):
            C = int(pr[r2])
            if C == snd[A] or C == pr[row] or (A, M, C) in seen:
                continue
            pa = pos_of.get((A, C))
            if pa is None or c["day"][pa] != c["day"][pp[r2]]:
                continue
            seen.add((A, M, C))
            out["A"].append(A); out["M"].append(int(M)); out["C"].append(C)
            out["posA"].append(pa); out["posM"].append(int(pp[r2])); out["named"].append(bool(pment[r2]))
    out = {k: np.asarray(v) for k, v in out.items()}
    out["day"] = c["day"][out["posA"]] if len(out["posA"]) else np.zeros(0, np.int64)
    return out


def relay_rd(U, R, T, y, sel=None, min_ahop=2, W=None, nboot=200, seed=0, n_pl=2):
    """Start-time RD at the relay posting time t_M on C's calls (h50lib boundary-1 RD, placebo-corrected), with the
    anchor calls restricted to C-hops >= min_ahop on A's clock (pos >= posA + min_ahop - 1), on both sides and in the
    placebo. 1-hour blocks. Returns J, lo, hi, se, n_rows."""
    import h50lib as L
    if sel is None:
        sel = np.ones(len(T["M"]), bool)
    keys = L.call_keys(U)
    if W is None:
        W = 1.5 * L.median_call_interval(U)
    te = R["m_t"][T["M"][sel]]
    de = T["day"][sel]
    rec = T["C"][sel]
    minpos = T["posA"][sel] + min_ahop - 1
    blk, nblk = blocks_for(U, te, de, min_days=None)
    rng = np.random.default_rng(seed)

    def stats(t_e):
        P, idx, s = L.rd_rows(U, keys, t_e, de, rec, W, k=1)
        ok = idx >= minpos[P]
        return L.rd_day_stats(P[ok], idx[ok], s[ok], blk, y, nblk), int(ok.sum())
    sr, nrows = stats(te)
    sp = sum(stats(L.placebo_times(U, te, de, rng))[0] for _ in range(n_pl)) / n_pl
    est = L.rd_summary(sr, sp)
    used = np.where(sr[:, :, 0].sum(1) > 0)[0]
    bs = np.array([L.rd_summary(sr, sp, np.bincount(rng.choice(used, len(used)), minlength=nblk).astype(float))["J"]
                   for _ in range(nboot)]) if len(used) >= 2 else np.array([np.nan])
    return dict(J=float(est["J"]), lo=float(np.nanpercentile(bs, 2.5)), hi=float(np.nanpercentile(bs, 97.5)),
                se=float(np.nanstd(bs)), n_rows=nrows, n_pairs=int(sel.sum()))
