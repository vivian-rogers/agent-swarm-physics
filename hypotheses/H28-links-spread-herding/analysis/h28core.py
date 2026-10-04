"""H28 core: risk-set panel, Poisson fixed-effects hazard fits, link features, nulls, attributable infection rate,
and the counterfactual simulator. Shared by the synthetic validation and the real-data run.

A period P is a dict of numpy arrays (see `load_period` for real data, `synthetic.generate` for synthetic swarms):
  days        list of dicts {ws_ms, we_ms, nb}
  agents      agent codes (index = position)          K, projects   universe size and names
  touches     ai, x, t, src (0 action, 1 chat)        x = universe index or -1
  links       t, sender (code, -1 human), room, x, addressed (list of agent codes), lid
  expo        lid, ri, t_vis                           recipients (agent index) and visibility time
  turns       {ai: sorted turn times}; ev_turns {ai: sorted events_core turn times}; pre_ne09 flag
  active      ai, b, room                              active (agent, global bin) pairs and room at bin start
  roster      {day: set(ai)}
  plans       ai, t, pid; plan_proj set(pid * K + x)
  kicks       human (t, room), auto (t, room), kickoff (t)
All times are int64 ms (any common origin).
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import scipy.sparse as sp

BIN_MS = 300_000
GAP_MS = 3_600_000
BIG = np.int64(10 ** 12)          # composite-key stride (> any time span in ms)
W15, W60, W240 = 900_000, 3_600_000, 14_400_000

CONTROLS = ["log_occ", "own_ever", "log_own", "plan", "human30", "auto30", "kick60", "q1", "q2", "q3"]
SPECS = {
    "primary": ["E60", "Eold"] + CONTROLS,
    "kernel": ["lE015", "lE1560", "lE60240"] + CONTROLS,
    "dose": ["d11", "d12", "d13", "dS2", "Eold"] + CONTROLS,
    "simple": ["lE60", "Eold"] + CONTROLS,
    "complex": ["lE60", "dS2any", "Eold"] + CONTROLS,
    "threshold": ["dS2any", "Eold"] + CONTROLS,
    "lead": ["E60", "Eold", "lead60"] + CONTROLS,
    "room": ["E60", "Eold", "other60"] + CONTROLS,
    "addressed": ["E60", "addr60", "Eold"] + CONTROLS,
    "momentum": ["E60", "Eold", "mom30"] + CONTROLS,
    "fields": [c for c in CONTROLS if c != "log_occ"],
    "occ_only": CONTROLS,
}
LINK_FEATURES = {"E60", "Eold", "lE015", "lE1560", "lE60240", "d11", "d12", "d13", "dS2", "lE60", "dS2any", "addr60"}


# ----------------------------------------------------------------------------------------------- loading (real data)
def r1b_mode() -> tuple[bool, bool]:
    """Round 1b switches (2026-10-04). H28_DATA=r1b: link exposures and visibility from the DQ1 context ledger
    (r1b/G<NN>/exposures.parquet, calls.parquet). H28_TOUCH=work: touches are DQ4 agent work commits. Defaults: round 1."""
    import os
    return os.environ.get("H28_DATA", "") == "r1b", os.environ.get("H28_TOUCH", "") == "work"


def load_period(folder: Path, universe: str = "U") -> dict:
    import polars as pl
    led, work = r1b_mode()
    f1b = folder.parent / "r1b" / folder.name
    meta = json.loads((folder / "meta.json").read_text())
    days = meta["days"]
    tb = pl.read_parquet(folder / "turn_bins.parquet")
    agents = sorted(set(tb["agent"].to_list()))
    amap = np.full(128, -1, np.int64)
    amap[np.array(agents)] = np.arange(len(agents))
    touches = pl.read_parquet((f1b / "touches_work.parquet") if work else (folder / "touches.parquet"))
    links = pl.read_parquet(folder / "links.parquet")
    projects = [u["project"] for u in meta["universe"]]
    if universe == "U+":
        extra = links.filter(pl.col("sender") >= 0)["project"].unique().sort().to_list()
        projects = projects + [p for p in extra if p not in set(projects)]
    pidx = {p: i for i, p in enumerate(projects)}
    K = len(projects)
    ta = amap[touches["agent"].to_numpy().astype(np.int64)]
    tx = np.array([pidx.get(p, -1) for p in touches["project"].to_list()], np.int64)
    ok = ta >= 0
    T = dict(ai=ta[ok], x=tx[ok], t=touches["t_ms"].to_numpy()[ok], src=touches["source"].to_numpy()[ok])
    # links: one row per (message, project); lid indexes rows
    links = links.with_row_index("lid")
    L = dict(lid=links["lid"].to_numpy().astype(np.int64), msg=links["msg"].to_numpy().astype(np.int64),
             t=links["t_ms"].to_numpy(), sender=links["sender"].to_numpy().astype(np.int64),
             room=links["room"].to_numpy().astype(np.int64),
             x=np.array([pidx.get(p, -1) for p in links["project"].to_list()], np.int64),
             addressed=[set(a or []) for a in links["addressed"].to_list()])
    ex = pl.read_parquet((f1b if led else folder) / "exposures.parquet")
    exj = links.select("lid", "msg").join(ex, on="msg", how="inner")
    ri = amap[exj["recipient"].to_numpy().astype(np.int64)]
    ok = ri >= 0
    E = dict(lid=exj["lid"].to_numpy().astype(np.int64)[ok], ri=ri[ok], t_vis=exj["t_vis_ms"].to_numpy()[ok])
    turns = pl.read_parquet(folder / "turns.parquet")
    tdict, edict = {}, {}
    for (a,), sub in turns.group_by(["agent"], maintain_order=True):
        i = amap[int(a)]
        if i < 0:
            continue
        tdict[int(i)] = sub["t_ms"].to_numpy()
        edict[int(i)] = sub.filter(pl.col("is_event"))["t_ms"].to_numpy()
    A = dict(ai=amap[tb["agent"].to_numpy().astype(np.int64)], room=tb["room"].to_numpy().astype(np.int64))
    offs = np.cumsum([0] + [d["nb"] for d in days])
    A["b"] = offs[tb["day"].to_numpy().astype(np.int64)] + tb["bin"].to_numpy().astype(np.int64)
    roster = {di: set(int(amap[a]) for a in meta["roster_day"][d["pt_date"]] if amap[a] >= 0) for di, d in enumerate(days)}
    plans = pl.read_parquet(folder / "plans.parquet")
    pa = amap[plans["agent"].to_numpy().astype(np.int64)]
    pid = {int(p): i for i, p in enumerate(plans["plan"].to_list())}
    pp = pl.read_parquet(folder / "plan_projects.parquet")
    pproj = set()
    for r in pp.iter_rows(named=True):
        if r["project"] in pidx and int(r["plan"]) in pid:
            pproj.add(pid[int(r["plan"])] * K + pidx[r["project"]])
    okp = pa >= 0
    PL = dict(ai=pa[okp], t=plans["t_ms"].to_numpy()[okp], pid=np.arange(plans.height)[okp], proj=pproj)
    kk = pl.read_parquet(folder / "kicks.parquet")
    hm = kk.filter(pl.col("kind") == "human_message")
    am = kk.filter(pl.col("kind") == "automated_message")
    ko = kk.filter(pl.col("kind") == "goal_kickoff")
    KI = dict(human=(hm["t_ms"].to_numpy(), hm["room"].fill_null(-1).to_numpy().astype(np.int64)),
              auto=(am["t_ms"].to_numpy(), am["room"].fill_null(-1).to_numpy().astype(np.int64)),
              kickoff=ko["t_ms"].to_numpy())
    out = dict(goal=meta["goal"], days=days, agents=agents, K=K, projects=projects, touches=T, links=L, expo=E,
               turns=tdict, ev_turns=edict, pre_ne09=meta["pre_ne09"], active=A, roster=roster, plans=PL, kicks=KI,
               meta=meta)
    if led:
        cl = pl.read_parquet(f1b / "calls.parquet")
        vc = {}
        for (a,), sub in cl.group_by(["agent"], maintain_order=True):
            i = amap[int(a)]
            if i >= 0:
                vc[int(i)] = np.sort(sub["t_ms"].to_numpy())
        out["vis_calls"] = vc
    return out


# ----------------------------------------------------------------------------------------------- bins and grids
def bins(P):
    T, day, q, end = [], [], [], []
    for di, d in enumerate(P["days"]):
        nb = d["nb"]
        t = d["ws_ms"] + np.arange(nb, dtype=np.int64) * BIN_MS
        T.append(t)
        day.append(np.full(nb, di))
        span = max(1, d["we_ms"] - d["ws_ms"])
        q.append(np.clip((4 * (t - d["ws_ms"]) // span), 0, 3))
        end.append(np.minimum(t + BIN_MS, d["we_ms"] + 1))
    return dict(T=np.concatenate(T), day=np.concatenate(day), q=np.concatenate(q), end=np.concatenate(end),
                nD=len(P["days"]))


def _count(comp_sorted, qlo, qhi):
    """# of entries in [qlo, qhi)."""
    return np.searchsorted(comp_sorted, qhi, "left") - np.searchsorted(comp_sorted, qlo, "left")


def grids(P, B):
    """on-state, arrival, prior-touch grids over (agent, project, bin)."""
    nA, K, nB = len(P["agents"]), P["K"], len(B["T"])
    T = P["touches"]
    m = T["x"] >= 0
    ai, x, t, src = T["ai"][m], T["x"][m], T["t"][m], T["src"][m]
    key = ai * K + x
    # bin containing each touch
    tb = np.searchsorted(B["T"], t, "right") - 1
    okb = (tb >= 0) & (t < B["end"][np.clip(tb, 0, nB - 1)])
    # on-state: bins with T_b in (t, t + GAP], same day
    day_last = np.zeros(B["nD"], np.int64)
    offs = np.cumsum([0] + [d["nb"] for d in P["days"]])
    day_last[:] = offs[1:]
    lo = np.searchsorted(B["T"], t, "right")
    hi = np.searchsorted(B["T"], t + GAP_MS, "right")
    dtouch = B["day"][np.clip(tb, 0, nB - 1)]
    hi = np.minimum(hi, day_last[dtouch])
    diff = np.zeros((nA * K, nB + 1), np.int32)
    v = okb & (hi > lo)
    np.add.at(diff, (key[v], lo[v]), 1)
    np.add.at(diff, (key[v], hi[v]), -1)
    on = np.cumsum(diff[:, :nB], axis=1) > 0
    yg = np.zeros((nA * K, nB), np.int16)
    np.add.at(yg, (key[okb], tb[okb]), 1)
    yga = np.zeros((nA * K, nB), np.int16)
    va = okb & (src == 0)
    np.add.at(yga, (key[va], tb[va]), 1)
    prev = np.cumsum(yg, axis=1, dtype=np.int32)
    prev = np.concatenate([np.zeros((nA * K, 1), np.int32), prev[:, :-1]], axis=1)
    return dict(on=on.reshape(nA, K, nB), y=(yg > 0).reshape(nA, K, nB), ya=(yga > 0).reshape(nA, K, nB),
                prev=prev.reshape(nA, K, nB))


def build_rows(P, B=None, G=None):
    """Risk set (active, off-X agent-project-bins) with the link-independent covariates."""
    B = B or bins(P)
    G = G or grids(P, B)
    nA, K, nB = len(P["agents"]), P["K"], len(B["T"])
    A = P["active"]
    okr = np.array([a in P["roster"][B["day"][b]] for a, b in zip(A["ai"], A["b"])], bool) if len(A["ai"]) else np.zeros(0, bool)
    ai_a, b_a, room_a = A["ai"][okr], A["b"][okr], A["room"][okr]
    ai = np.repeat(ai_a, K)
    b = np.repeat(b_a, K)
    room = np.repeat(room_a, K)
    x = np.tile(np.arange(K), len(ai_a))
    risk = ~G["on"][ai, x, b]
    ai, b, x, room = ai[risk], b[risk], x[risk], room[risk]
    Tb = B["T"][b]
    occ = G["on"].sum(0)          # (K, nB)
    R = dict(ai=ai, x=x, b=b, room=room, T=Tb, day=B["day"][b], q=B["q"][b],
             y=G["y"][ai, x, b].astype(np.float64), ya=G["ya"][ai, x, b].astype(np.float64))
    R["log_occ"] = np.log1p(occ[x, b])
    # momentum: arrivals at x by others in the previous 30 min (same day), a within-day common-drive proxy
    arr = (G["y"] & ~G["on"]).sum(0).astype(np.int32)          # (K, nB) arrivals per project-bin
    ca = np.concatenate([np.zeros((K, 1), np.int32), np.cumsum(arr, axis=1)], axis=1)
    offs = np.cumsum([0] + [d["nb"] for d in P["days"]])
    b0 = np.maximum(b - 6, offs[B["day"][b]])
    R["mom30"] = np.log1p(ca[x, b] - ca[x, b0])
    prevc = G["prev"][ai, x, b]
    R["own_ever"] = (prevc > 0).astype(float)
    R["log_own"] = np.log1p(prevc)
    # plan: latest intention of i before T names x
    PL = P["plans"]
    plan = np.zeros(len(ai))
    if len(PL["t"]) and PL["proj"]:
        projcodes = np.array(sorted(PL["proj"]), np.int64)
        for a in np.unique(ai):
            mi = ai == a
            ma = PL["ai"] == a
            if not ma.any():
                continue
            order = np.argsort(PL["t"][ma])
            pt, pid = PL["t"][ma][order], PL["pid"][ma][order]
            j = np.searchsorted(pt, Tb[mi], "left") - 1
            code = np.where(j >= 0, pid[np.clip(j, 0, None)] * K + x[mi], -1)
            plan[mi] = np.isin(code, projcodes)
    R["plan"] = plan
    # pulses
    KI = P["kicks"]

    def room_pulse(times, rooms, w):
        if len(times) == 0:
            return np.zeros(len(ai))
        comp = np.sort((rooms + 2) * BIG + times)
        return (_count(comp, (room + 2) * BIG + Tb - w, (room + 2) * BIG + Tb) > 0).astype(float)
    R["human30"] = room_pulse(*KI["human"], 1_800_000)
    R["auto30"] = room_pulse(*KI["auto"], 1_800_000)
    ko = np.sort(KI["kickoff"])
    R["kick60"] = (_count(ko, Tb - W60, Tb) > 0).astype(float) if len(ko) else np.zeros(len(ai))
    for qq in (1, 2, 3):
        R[f"q{qq}"] = (R["q"] == qq).astype(float)
    nD = B["nD"]
    R["fe_agent"] = ai
    R["fe_pd"] = x * nD + R["day"]
    R["fe_pdq"] = (x * nD + R["day"]) * 4 + R["q"]
    R["fe_p"] = x
    R["fe_d"] = R["day"]
    R["fe_dq"] = R["day"] * 4 + R["q"]
    R["cl"] = ai * nD + R["day"]
    R["nA"], R["K"], R["nB"], R["nD"] = nA, K, nB, nD
    return R, B, G


# ----------------------------------------------------------------------------------------------- link features
def visibility(P, t_post, ri):
    """Visibility time of a link posted at t_post for recipient ri: first logged turn at/after the post."""
    out = np.full(len(t_post), -1, np.int64)
    led = "vis_calls" in P      # round 1b: the recipient's first receiving call with t_call > t_post (DQ1 ledger rule)
    src = P["vis_calls"] if led else (P["ev_turns"] if P["pre_ne09"] else P["turns"])
    for a in np.unique(ri):
        m = ri == a
        tv = src.get(int(a), np.zeros(0, np.int64))
        if len(tv) == 0:
            continue
        j = np.searchsorted(tv, t_post[m], "right" if led else "left")
        ok = j < len(tv)
        out[np.where(m)[0][ok]] = tv[j[ok]]
    return out


def link_features(P, R, link_t=None, t_vis=None, keep=None):
    """Exposure covariates for the rows R. link_t: per-link posting time override (shift null); t_vis: per-exposure
    visibility override; keep: boolean mask over links (thinning)."""
    L, E = P["links"], P["expo"]
    K = P["K"]
    lt = L["t"] if link_t is None else link_t
    tv = E["t_vis"] if t_vis is None else t_vis
    lid = E["lid"]
    ex_x = L["x"][lid]
    m = (ex_x >= 0) & (tv >= 0)
    if keep is not None:
        m &= keep[lid]
    ri, x, tv_, sender, tpost = E["ri"][m], ex_x[m], tv[m], L["sender"][lid[m]], lt[lid[m]]
    key = ri * K + x
    rkey = R["ai"] * K + R["x"]
    T = R["T"]
    comp = np.sort(key * BIG + tv_)
    base = rkey * BIG + T
    c015 = _count(comp, base - W15, base)
    c1560 = _count(comp, base - W60, base - W15)
    c60240 = _count(comp, base - W240, base - W60)
    c60 = c015 + c1560
    F = {}
    F["E60"] = (c60 > 0).astype(float)
    F["Eold"] = np.log1p(c60240)
    F["lE015"], F["lE1560"], F["lE60240"], F["lE60"] = np.log1p(c015), np.log1p(c1560), np.log1p(c60240), np.log1p(c60)
    # distinct senders in the last 60 min
    ns = np.zeros(len(T), np.int64)
    for s in np.unique(sender):
        ms_ = sender == s
        cs = np.sort(key[ms_] * BIG + tv_[ms_])
        ns += (_count(cs, base - W60, base) > 0)
    F["c60"], F["s60"] = c60, ns
    F["d11"] = ((ns == 1) & (c60 == 1)).astype(float)
    F["d12"] = ((ns == 1) & (c60 == 2)).astype(float)
    F["d13"] = ((ns == 1) & (c60 >= 3)).astype(float)
    F["dS2"] = (ns >= 2).astype(float)
    F["dS2any"] = F["dS2"]
    # addressed links
    agents = np.array(P["agents"])
    addr = np.array([agents[r] in L["addressed"][l] for r, l in zip(ri, lid[m])], bool) if len(ri) else np.zeros(0, bool)
    ca = np.sort(key[addr] * BIG + tv_[addr])
    F["addr60"] = (_count(ca, base - W60, base) > 0).astype(float)
    # lead placebo: links to x posted by others in (T, T + 60 min] that i will receive
    cp = np.sort(key * BIG + tpost)
    F["lead60"] = (np.searchsorted(cp, base + W60, "right") - np.searchsorted(cp, base, "right") > 0).astype(float)
    # other-room placebo: links to x posted (last 60 min) where i was not a recipient (on roster that day, not sender)
    F["other60"] = other_room(P, R, lt, keep)
    return F


def other_room(P, R, lt, keep=None):
    L, E = P["links"], P["expo"]
    K = P["K"]
    if "other_pairs" not in P:
        rec = {}
        for l, r in zip(E["lid"], E["ri"]):
            rec.setdefault(int(l), set()).add(int(r))
        B = P.get("_B") or bins(P)
        pairs_l, pairs_a = [], []
        agents = P["agents"]
        acode = {c: i for i, c in enumerate(agents)}
        for l in range(len(L["t"])):
            if L["x"][l] < 0:
                continue
            di = int(np.clip(np.searchsorted(B["T"], L["t"][l], "right") - 1, 0, len(B["T"]) - 1))
            day = B["day"][di]
            snd = acode.get(int(L["sender"][l]), -9)
            rs = rec.get(l, set())
            for a in P["roster"][day]:
                if a != snd and a not in rs:
                    pairs_l.append(l)
                    pairs_a.append(a)
        P["other_pairs"] = (np.array(pairs_l, np.int64), np.array(pairs_a, np.int64))
    pl_, pa = P["other_pairs"]
    if len(pl_) == 0:
        return np.zeros(len(R["T"]))
    m = np.ones(len(pl_), bool) if keep is None else keep[pl_]
    comp = np.sort((pa[m] * K + L["x"][pl_[m]]) * BIG + lt[pl_[m]])
    base = (R["ai"] * K + R["x"]) * BIG + R["T"]
    return (_count(comp, base - W60, base) > 0).astype(float)


def shift_links(P, rng, lo_ms=1_800_000, hi_ms=7_200_000):
    """N1: shift each link (message) by +-U[30, 120] min within its own day's active window; recompute visibility."""
    L, E = P["links"], P["expo"]
    days = P["days"]
    ws = np.array([d["ws_ms"] for d in days])
    we = np.array([d["we_ms"] for d in days])
    msgs, inv = np.unique(L.get("msg", L["lid"]), return_inverse=True)
    tm = np.zeros(len(msgs), np.int64)
    tm[inv] = L["t"]
    di = np.clip(np.searchsorted(ws, tm, "right") - 1, 0, len(ws) - 1)
    d = rng.uniform(lo_ms, hi_ms, len(msgs)) * rng.choice([-1, 1], len(msgs))
    t_new = tm + d.astype(np.int64)
    bad = (t_new < ws[di]) | (t_new > we[di])
    t_new[bad] = tm[bad] - d[bad].astype(np.int64)
    bad = (t_new < ws[di]) | (t_new > we[di])
    t_new[bad] = (ws[di][bad] + rng.uniform(0, 1, bad.sum()) * (we[di][bad] - ws[di][bad])).astype(np.int64)
    lt = t_new[inv]
    tv = visibility(P, lt[E["lid"]], E["ri"])
    return lt, tv


# ----------------------------------------------------------------------------------------------- Poisson FE fit
def _demean(Z, w, Ms, tol=1e-9, maxit=2000):
    """Weighted within-transformation by alternating projections (Z is modified in place and returned)."""
    scale = max(1.0, float(np.abs(Z).max()) if Z.size else 1.0)
    for _ in range(maxit):
        delta = 0.0
        for M, ws in Ms:
            means = (M.T @ (Z * w[:, None])) / ws[:, None]
            Z -= M @ means
            delta = max(delta, float(np.abs(means).max()) if means.size else 0.0)
        if delta < tol * scale:
            break
    return Z


def _relabel(f):
    u, inv = np.unique(f, return_inverse=True)
    return inv, len(u)


def pois_fe(y, X, fes, cl=None, maxit=60, tol=1e-10, names=None):
    """Poisson regression with high-dimensional fixed effects (IRLS + alternating projections, ppmlhdfe-style).

    Rows in FE groups with no events are dropped (they carry no information about beta). Returns beta, cluster-robust
    covariance (by `cl`), log-likelihood and fitted means on the kept rows."""
    n = len(y)
    keep = np.ones(n, bool)
    for _ in range(20):
        changed = False
        for f in fes:
            s = np.bincount(f[keep], weights=y[keep], minlength=f.max() + 1)
            k2 = keep & (s[f] > 0)
            if k2.sum() != keep.sum():
                changed = True
            keep = k2
        if not changed:
            break
    yk = y[keep]
    Xk = X[keep] if X.shape[1] else np.zeros((keep.sum(), 0))
    fk = [_relabel(f[keep]) for f in fes]
    nk = len(yk)
    if nk == 0 or yk.sum() == 0:
        return None
    # drop constant / empty columns
    colok = np.array([Xk[:, j].std() > 0 for j in range(Xk.shape[1])], bool) if Xk.shape[1] else np.zeros(0, bool)
    Xk = Xk[:, colok]
    mats = [sp.csr_matrix((np.ones(nk), (np.arange(nk), inv)), shape=(nk, G)) for inv, G in fk]
    mu = (yk + yk.mean()) / 2
    eta = np.log(mu)
    beta = np.zeros(Xk.shape[1])
    dev_old = np.inf
    Zraw_prev = Zt_prev = None
    for it in range(maxit):
        w = mu
        z = eta + (yk - mu) / mu
        Ms = [(M, np.asarray(M.T @ w).ravel()) for M in mats]
        Zraw = np.column_stack([z, Xk])
        start = Zraw.copy() if Zraw_prev is None else Zraw - (Zraw_prev - Zt_prev)   # warm start (same FE-span class)
        Zt = _demean(start, w, Ms)
        Zraw_prev, Zt_prev = Zraw, Zt.copy()
        zt, Xt = Zt[:, 0], Zt[:, 1:]
        if Xt.shape[1]:
            XtW = Xt * w[:, None]
            H = XtW.T @ Xt
            beta = np.linalg.solve(H + 1e-10 * np.eye(len(H)), XtW.T @ zt)
            resid = zt - Xt @ beta
        else:
            resid = zt
        eta = z - resid
        eta = np.clip(eta, -50, 30)
        mu = np.exp(eta)
        with np.errstate(divide="ignore", invalid="ignore"):
            dev = 2 * np.sum(np.where(yk > 0, yk * np.log(yk / mu), 0) - (yk - mu))
        if abs(dev - dev_old) / (abs(dev) + 0.1) < tol:
            break
        dev_old = dev
    p = Xt.shape[1]
    V = np.full((p, p), np.nan)
    if p:
        Hinv = np.linalg.inv(H + 1e-10 * np.eye(p))
        sc = Xt * (yk - mu)[:, None]
        if cl is not None:
            c, Gc = _relabel(cl[keep])
            S = np.zeros((Gc, p))
            np.add.at(S, c, sc)
            meat = S.T @ S * Gc / max(Gc - 1, 1)
        else:
            meat = sc.T @ sc
        V = Hinv @ meat @ Hinv
    full_beta = np.full(len(colok), np.nan)
    full_beta[colok] = beta
    fullV = np.full((len(colok), len(colok)), np.nan)
    idx = np.where(colok)[0]
    fullV[np.ix_(idx, idx)] = V
    from scipy.special import gammaln
    ll = float(np.sum(yk * np.log(np.maximum(mu, 1e-300)) - mu - gammaln(yk + 1)))
    return dict(beta=full_beta, V=fullV, se=np.sqrt(np.diag(fullV)), ll=ll, mu=mu, keep=keep, eta=eta, n=nk,
                events=float(yk.sum()), names=names, colok=colok, xb=(Xk @ beta if p else np.zeros(nk)))


def design(R, F, spec, extra_rows=None):
    names = SPECS[spec] if isinstance(spec, str) else spec
    cols = []
    for nme in names:
        cols.append(F[nme] if nme in F else R[nme])
    X = np.column_stack(cols).astype(np.float64) if cols else np.zeros((len(R["T"]), 0))
    return X, list(names)


FE_SETS = {"pd": ("fe_agent", "fe_pd"), "pdq": ("fe_agent", "fe_pdq"), "p+d": ("fe_agent", "fe_p", "fe_d"),
           "p": ("fe_agent", "fe_p"), "p+dq": ("fe_agent", "fe_p", "fe_dq"), "p+pd": ("fe_agent", "fe_pd")}


def fit(R, F, spec="primary", fe="p+d", rows=None, y="y"):
    X, names = design(R, F, spec)
    fes = [R[f] for f in FE_SETS[fe]]
    yy = R[y]
    cl = R["cl"]
    if rows is not None:
        X, yy, cl = X[rows], yy[rows], cl[rows]
        fes = [f[rows] for f in fes]
    res = pois_fe(yy, X, fes, cl, names=names)
    return res


def coef(res, name):
    if res is None or name not in res["names"]:
        return np.nan, np.nan
    j = res["names"].index(name)
    return float(res["beta"][j]), float(res["se"][j])


# ----------------------------------------------------------------------------------------------- derived quantities
def attributable(res, R, F, nexp, link_names=("E60", "Eold"), draws=300, rng=None):
    """lambda (extra arrivals per link exposure) and R_link (fraction of arrivals attributable to links)."""
    rng = rng or np.random.default_rng(0)
    keep = res["keep"]
    names = res["names"]
    idx = [names.index(n) for n in link_names if n in names and not np.isnan(res["beta"][names.index(n)])]
    Xl = np.column_stack([(F[names[j]] if names[j] in F else R[names[j]])[keep] for j in idx]) if idx else np.zeros((keep.sum(), 0))
    b = res["beta"][idx]
    mu = res["mu"]
    mu0 = mu * np.exp(-(Xl @ b)) if idx else mu
    attr = float(np.sum(mu - mu0))
    out = dict(attr=attr, n_exp=nexp, events=res["events"], lam=attr / max(nexp, 1), R_link=attr / max(res["events"], 1))
    if idx and draws:
        Vb = res["V"][np.ix_(idx, idx)]
        if np.all(np.isfinite(Vb)):
            bs = rng.multivariate_normal(b, Vb, size=draws)
            lin = Xl @ bs.T
            a = np.sum(mu0[:, None] * np.exp(lin), axis=0) - mu0.sum()
            out["lam_ci"] = [float(np.percentile(a, 5) / max(nexp, 1)), float(np.percentile(a, 95) / max(nexp, 1))]
            out["R_ci"] = [float(np.percentile(a, 5) / res["events"]), float(np.percentile(a, 95) / res["events"])]
    return out


def count_exposures(P, t_vis=None, keep=None):
    """Link exposures that reach a susceptible recipient: (link, recipient) pairs with the project in the universe and
    the recipient off X (no touch of X in the 60 min before t_vis)."""
    L, E, T = P["links"], P["expo"], P["touches"]
    K = P["K"]
    tv = E["t_vis"] if t_vis is None else t_vis
    ex_x = L["x"][E["lid"]]
    m = (ex_x >= 0) & (tv >= 0)
    if keep is not None:
        m &= keep[E["lid"]]
    mt = T["x"] >= 0
    tcomp = np.sort((T["ai"][mt] * K + T["x"][mt]) * BIG + T["t"][mt])
    kk = E["ri"][m] * K + ex_x[m]
    off = _count(tcomp, kk * BIG + tv[m] - GAP_MS, kk * BIG + tv[m]) == 0
    return float(off.sum())


def plan_grid(P, B):
    """X named in agent i's latest plan before each bin start: bool (nA, K, nB)."""
    nA, K, nB = len(P["agents"]), P["K"], len(B["T"])
    g = np.zeros((nA, K, nB), bool)
    PL = P["plans"]
    if not len(PL["t"]) or not PL["proj"]:
        return g
    byplan = {}
    for code in PL["proj"]:
        byplan.setdefault(code // K, []).append(code % K)
    for a in range(nA):
        ma = PL["ai"] == a
        if not ma.any():
            continue
        o = np.argsort(PL["t"][ma])
        pt, pid = PL["t"][ma][o], PL["pid"][ma][o]
        j = np.searchsorted(pt, B["T"], "left") - 1
        for b in np.nonzero(j >= 0)[0]:
            for x in byplan.get(int(pid[j[b]]), []):
                g[a, x, b] = True
    return g


def cv_quarters(R, F, specs=("fields", "occ_only", "primary"), y="y", fe="p+d"):
    """Quarter-blocked held-out log-likelihood: train on 3 quarters of every day, test on the 4th (FE estimable)."""
    from scipy.special import gammaln
    out = {s: 0.0 for s in specs}
    fnames = FE_SETS[fe]
    for qq in range(4):
        tr, te = R["q"] != qq, R["q"] == qq
        for s in specs:
            X, names = design(R, F, s)
            res = pois_fe(R[y][tr], X[tr], [R[f][tr] for f in fnames], R["cl"][tr], names=names)
            if res is None:
                continue
            b = np.nan_to_num(res["beta"])
            fev = fe_solve(R[y][tr], X[tr] @ b, [R[f][tr] for f in fnames], [int(R[f].max()) + 1 for f in fnames])
            eta = X[te] @ b + sum(v[R[f][te]] for v, f in zip(fev, fnames))
            mu = np.exp(np.clip(eta, -50, 30))
            yy = R[y][te]
            out[s] += float(np.sum(yy * np.log(np.maximum(mu, 1e-300)) - mu - gammaln(yy + 1)))
    return out


def fe_solve(y, xb, fes, sizes, iters=300, pseudo=0.5):
    """Closed-form alternating Poisson FE given x*beta; a pseudo-count shrink keeps empty groups finite."""
    vals = [np.zeros(n) for n in sizes]
    rate = (y.sum() + pseudo) / (np.exp(xb).sum() + pseudo)
    vals[0][:] = math.log(rate)
    for _ in range(iters):
        delta = 0.0
        for k, (f, n) in enumerate(zip(fes, sizes)):
            other = xb + sum(v[ff] for j, (v, ff) in enumerate(zip(vals, fes)) if j != k)
            s_ = np.bincount(f, weights=np.exp(other), minlength=n)
            yy = np.bincount(f, weights=y, minlength=n)
            new = np.log((yy + pseudo * (1 if k == 0 else 0.2)) / (s_ + pseudo * (1 if k == 0 else 0.2) / max(rate, 1e-12)))
            delta = max(delta, float(np.max(np.abs(new - vals[k]))))
            vals[k] = new
        if delta < 1e-8:
            break
    return vals


def event_study(P, R, F, res_fields):
    """Naive agents: observed/expected arrivals in 5-min bins relative to their first visible link to X (from others).

    Expected = fitted fields-only model (no link terms). Returns O/E for (-60, 0] and (0, 60] min and per bin."""
    L, E = P["links"], P["expo"]
    K = P["K"]
    ex_x = L["x"][E["lid"]]
    m = (ex_x >= 0) & (E["t_vis"] >= 0)
    key = E["ri"][m] * K + ex_x[m]
    tv = E["t_vis"][m]
    first = {}
    for k_, t_ in zip(key, tv):
        if k_ not in first or t_ < first[k_]:
            first[k_] = t_
    keep = res_fields["keep"]
    naive = R["own_ever"][keep] == 0
    rk = (R["ai"] * K + R["x"])[keep]
    Tb = R["T"][keep]
    f1 = np.array([first.get(int(k_), -1) for k_ in rk], np.int64)
    ok = naive & (f1 >= 0)
    rel = np.floor((Tb - f1) / BIN_MS).astype(np.int64)    # bin start relative to first visibility
    yk = R["y"][keep]
    mu = res_fields["mu"]
    out = {}
    for lab, lo_, hi_ in [("pre", -12, 0), ("post", 0, 12)]:
        w = ok & (rel >= lo_) & (rel < hi_)
        out[lab] = dict(O=float(yk[w].sum()), E=float(mu[w].sum()))
    prof = []
    for r_ in range(-12, 12):
        w = ok & (rel == r_)
        prof.append((r_, float(yk[w].sum()), float(mu[w].sum())))
    out["profile"] = prof
    return out


def latency(P, shifts=None):
    """Excess arrivals of susceptible recipients vs time since link posting (5-min bins, 0-240 min).

    Observed counts minus the mean over shifted-link draws; recipients off X at posting time, same day."""
    L, E, T = P["links"], P["expo"], P["touches"]
    K = P["K"]
    # arrival times per (agent, project): first touch after >= 60 min without one
    m = T["x"] >= 0
    key = T["ai"][m] * K + T["x"][m]
    t = T["t"][m]
    o = np.lexsort((t, key))
    key, t = key[o], t[o]
    newk = np.r_[True, key[1:] != key[:-1]]
    gap = np.r_[np.inf, np.diff(t)]
    arr = newk | (gap > GAP_MS)
    ak, at = key[arr], t[arr]
    acomp = ak * BIG + at
    tcomp = key * BIG + t

    def counts(lt):
        ex_x = L["x"][E["lid"]]
        mm = ex_x >= 0
        kk = E["ri"][mm] * K + ex_x[mm]
        tp = lt[E["lid"][mm]]
        # recipient off X at posting
        off = _count(tcomp, kk * BIG + tp - GAP_MS, kk * BIG + tp) == 0
        kk, tp = kk[off], tp[off]
        j = np.searchsorted(acomp, kk * BIG + tp, "left")
        ok = j < len(acomp)
        lag = np.full(len(kk), np.inf)
        same = ok & (ak[np.clip(j, 0, len(ak) - 1)] == kk)
        lag[same] = (at[j[same]] - tp[same]) / 60000.0
        h = np.histogram(lag[np.isfinite(lag) & (lag < 240)], bins=np.arange(0, 245, 5))[0]
        return h, len(kk)
    h_obs, n_obs = counts(L["t"])
    hs = []
    rng = np.random.default_rng(28)
    for _ in range(shifts or 0):
        lt, _tv = shift_links(P, rng)
        hs.append(counts(lt)[0])
    base = np.mean(hs, 0) if hs else np.zeros_like(h_obs)
    exc = h_obs - base
    cum = np.cumsum(np.clip(exc, 0, None))
    med = float(np.searchsorted(cum, cum[-1] / 2) * 5 + 2.5) if cum[-1] > 0 else float("nan")
    return dict(h_obs=h_obs.tolist(), h_null=np.round(base, 2).tolist(), n_pairs=int(n_obs), median_excess_lag=med,
                excess_0_15=float(exc[:3].sum()), excess_15_60=float(exc[3:12].sum()), excess_60_240=float(exc[12:].sum()))


# ----------------------------------------------------------------------------------------------- spells (for simulation)
def spells(P):
    """Observed on-spells per (agent, project): start, end, touches, and own link offsets (ms after start)."""
    T, L = P["touches"], P["links"]
    K = P["K"]
    m = T["x"] >= 0
    key = T["ai"][m] * K + T["x"][m]
    t = T["t"][m]
    o = np.lexsort((t, key))
    key, t = key[o], t[o]
    newk = np.r_[True, key[1:] != key[:-1]]
    gap = np.r_[np.inf, np.diff(t)]
    start = newk | (gap > GAP_MS)
    sid = np.cumsum(start) - 1
    nS = sid[-1] + 1 if len(sid) else 0
    s_key = key[start]
    s_t0 = t[start]
    s_t1 = np.zeros(nS, np.int64)
    np.maximum.at(s_t1, sid, t)
    s_n = np.bincount(sid, minlength=nS)
    agents = np.array(P["agents"])
    acode = {c: i for i, c in enumerate(agents)}
    s_links = [[] for _ in range(nS)]
    comp = s_key * BIG + s_t0
    for l in range(len(L["t"])):
        if L["x"][l] < 0 or int(L["sender"][l]) not in acode:
            continue
        kk = acode[int(L["sender"][l])] * K + L["x"][l]
        j = np.searchsorted(comp, kk * BIG + L["t"][l], "right") - 1
        if j >= 0 and s_key[j] == kk and L["t"][l] <= s_t1[j] + 1:
            s_links[j].append(int(L["t"][l] - s_t0[j]))
    return dict(key=s_key, t0=s_t0, t1=s_t1, n=s_n, links=s_links)


def observed_pileups(P, B, G):
    """Peak single-project occupancy, peak 60-min arrival burst, and distinct visitors of the top project."""
    on = G["on"]                                  # (nA, K, nB) on at bin start
    occ = on.sum(0)
    arr = G["y"] & ~on
    burst = 0
    nB = occ.shape[1]
    for b0 in range(nB):
        b1 = min(nB, b0 + 12)
        same = B["day"][b0:b1] == B["day"][b0]
        burst = max(burst, int((arr[:, :, b0:b1][:, :, same].any(2)).sum(0).max()))
    vis = arr.any(2).sum(0)
    return dict(peak_occ=int(occ.max()), burst60=burst, top_visitors=int(vis.max()))


# ----------------------------------------------------------------------------------------------- counterfactual simulator
class Simulator:
    """Generative replay of a period: fitted hazard (primary spec) + empirical spells and link offsets.

    Exogenous (kept as observed): who is active in each bin and in which room, plans, pulses, quarters.
    Endogenous: arrivals, on-spells, own links, link exposures, occupancy, own history."""

    def __init__(self, P, R, B, G, res, F):
        self.P, self.B = P, B
        nA, K, nB = len(P["agents"]), P["K"], len(B["T"])
        self.nA, self.K, self.nB = nA, K, nB
        names = res["names"]
        self.names = names
        self.beta = np.nan_to_num(res["beta"])
        self.V = np.nan_to_num(res["V"])
        X, _ = design(R, F, names)
        xb = X @ self.beta
        self.fa, self.fg = fe_solve(R["y"], xb, [R["fe_agent"], R["fe_pd"]], [nA, K * B["nD"]])
        # exogenous grids
        self.active = np.zeros((nA, nB), bool)
        self.room = np.full((nA, nB), -1, np.int64)
        A = P["active"]
        for a, b, r in zip(A["ai"], A["b"], A["room"]):
            if a in P["roster"][B["day"][b]]:
                self.active[a, b] = True
            self.room[a, b] = r
        for a in range(nA):                       # carry room forward/backward over inactive bins
            rr = self.room[a]
            last = -1
            for b in range(nB):
                if rr[b] >= 0:
                    last = rr[b]
                else:
                    rr[b] = last
            first = next((v for v in rr if v >= 0), 0)
            rr[rr < 0] = first
        # exogenous covariates on the full grid (agent, project, bin), taken from R where available
        self.exo = {}
        for nme in ("human30", "auto30", "kick60", "q1", "q2", "q3"):
            g = np.zeros((nA, K, nB), np.float32)
            g[R["ai"], R["x"], R["b"]] = R[nme]
            g[:] = g.max(1, keepdims=True)        # agent-level: broadcast over projects
            self.exo[nme] = g
        self.exo["plan"] = plan_grid(P, B).astype(np.float32)
        self.sp = spells(P)
        lags = []
        L, E = P["links"], P["expo"]
        lt = L["t"][E["lid"]]
        ok = E["t_vis"] >= 0
        lags = (E["t_vis"][ok] - lt[ok]).astype(np.int64)
        self.lags = lags[lags >= 0] if len(lags) else np.zeros(1, np.int64)
        self.dur = (self.sp["t1"] - self.sp["t0"]).astype(np.int64)
        self.day_of = B["day"]

    def run(self, rng, f=1.0, cap_ms=None, draw_beta=True):
        nA, K, nB = self.nA, self.K, self.nB
        names = self.names
        beta = rng.multivariate_normal(self.beta, self.V) if draw_beta and np.all(np.isfinite(self.V)) else self.beta
        bi = {n: beta[names.index(n)] for n in names}
        T = self.B["T"]
        on_until = np.full((nA, K), -1, np.int64)
        touches = np.zeros((nA, K))
        vis_cum = np.zeros((nA, K), np.int32)
        snaps = np.zeros((nB + 1, nA, K), np.int32)
        pending = {}
        last_kept = {}
        occ_hist = np.zeros((K, nB), np.int16)
        arr_hist = np.zeros((nA, K, nB), bool)
        nS = len(self.dur)
        for b in range(nB):
            for (j, x) in pending.pop(b, []):
                vis_cum[j, x] += 1
            snaps[b] = vis_cum
            d = self.day_of[b]
            b60 = max(b - 12, 0)
            while b60 < b and self.day_of[b60] != d:
                b60 += 1
            b240 = max(b - 48, 0)
            while b240 < b and self.day_of[b240] != d:
                b240 += 1
            c60 = snaps[b] - snaps[b60]
            cold = snaps[b60] - snaps[b240]
            on = on_until > T[b]
            occ = on.sum(0)
            occ_hist[:, b] = occ
            eta = self.fa[:, None] + self.fg[np.arange(K) * self.B["nD"] + d][None, :]
            feats = {"E60": (c60 > 0).astype(float), "Eold": np.log1p(cold), "mom30": np.zeros((nA, K)), "log_occ": np.broadcast_to(np.log1p(occ)[None, :], (nA, K)),
                     "own_ever": (touches > 0).astype(float), "log_own": np.log1p(touches)}
            for nme, g in self.exo.items():
                feats[nme] = g[:, :, b]
            for nme in names:
                v = feats[nme]
                eta = eta + bi[nme] * v
            mu = np.exp(np.clip(eta, -50, 20))
            risk = self.active[:, b][:, None] & ~on
            hit = risk & (rng.random((nA, K)) < 1 - np.exp(-mu))
            for j, x in zip(*np.nonzero(hit)):
                s = rng.integers(nS)
                t0 = T[b] + int(rng.integers(BIN_MS))
                on_until[j, x] = t0 + self.dur[s] + GAP_MS
                touches[j, x] += self.sp["n"][s]
                arr_hist[j, x, b] = True
                for off in self.sp["links"][s]:
                    if f < 1 and rng.random() >= f:
                        continue
                    tl = t0 + off
                    bl = int(np.searchsorted(T, tl, "right") - 1)
                    if bl < 0 or bl >= nB or self.day_of[bl] != d:
                        continue
                    r = self.room[j, bl]
                    if cap_ms is not None:
                        lk = last_kept.get((x, r))
                        if lk is not None and tl - lk < cap_ms:
                            continue
                        last_kept[(x, r)] = tl
                    for jj in np.nonzero(self.room[:, bl] == r)[0]:
                        if jj == j:
                            continue
                        tv = tl + int(self.lags[rng.integers(len(self.lags))])
                        bv = int(np.searchsorted(T, tv, "right"))   # first bin starting after visibility
                        if bv < nB and self.day_of[min(bv, nB - 1)] == d:
                            pending.setdefault(bv, []).append((jj, x))
        burst = 0
        for b0 in range(nB):
            b1 = min(nB, b0 + 12)
            same = self.day_of[b0:b1] == self.day_of[b0]
            burst = max(burst, int(arr_hist[:, :, b0:b1][:, :, same].any(2).sum(0).max()))
        return dict(peak_occ=int(occ_hist.max()), burst60=burst, top_visitors=int(arr_hist.any(2).sum(0).max()),
                    arrivals=int(arr_hist.sum()))
