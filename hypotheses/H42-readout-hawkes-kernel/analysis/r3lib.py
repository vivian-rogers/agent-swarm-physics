"""H42 round 2, R3: a Cox (latent common rate) baseline for round 1's Hawkes worlds.

Round 1's baseline is c_{i,d,kappa} s_b with one within-day shape s_b (30-min bins) shared across days. Here s is a
piecewise-constant common log-rate per (day, bin) ['cox10': 600 s, 'cox5': 300 s] or per (day, room, bin) ['room10'],
fitted jointly with the cross terms. 'r1' = round 1's shared 30-min shape, refitted here with the same code (world B:
an event takes its call's bin). Cross specs: world B S0 / B / Bmu (ledger `ment` split, as round 1's post hoc test);
world A S0 / A. Held-out: day-blocked folds; on test days the agent levels AND the field are refitted, cross weights
fixed from the training days.
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import h42lib as H  # noqa: E402

H.BIN_S = 300.0          # fine base bins (world A exposure / event bins); world B bins are rebuilt from call starts
R2 = H.DATA / "round2"
SPECS_B = {"S0": H.W_BASE, "B": H.W_BASE + ("B",), "Bmu": H.W_BASE + ("Bm", "Bu")}
SPECS_A = {"S0": H.W_BASE, "A": H.W_BASE + ("A",)}
BASES = {"r1": (1800.0, "shared"), "cox10": (600.0, "day"), "cox5": (300.0, "day"), "room10": (600.0, "room")}


def rooms_by_turn(u: H.Unit) -> dict:
    p = R2 / f"G{u.goal:02d}/calls.parquet"
    if not p.exists():
        return {}
    c = pl.read_parquet(p, columns=["unit_id", "turn_id", "room"]).filter(pl.col("unit_id") == u.unit_id)
    return dict(zip(c["turn_id"].to_list(), c["room"].fill_null(-1).to_list()))


def world_b(u: H.Unit, items: pl.DataFrame | None = None, split: bool = True):
    """world-B design (base + B, Bm, Bu cross columns) and per-call internals for field binning."""
    base = H.build_talk(u, world="B", specs=(), internals=True)
    it = u.items if items is None else items
    cols, names, Zs = [base.F], list(base.names), [base.Zd]
    fams = [("B", it.filter(pl.col("kind") == "agent"))]
    if split:
        ag = it.filter(pl.col("kind") == "agent")
        fams += [("Bm", ag.filter(pl.col("ment"))), ("Bu", ag.filter(~pl.col("ment")))]
    for tag, sub in fams:
        d = H.build_talk(u, world="B", items_override=sub, only_cross=True, specs=("B",))
        k = [i for i, nm in enumerate(d.names) if nm.startswith("B_")]
        cols.append(d.F[:, k]); Zs.append(d.Zd[:, k])
        names += [f"{tag}_{d.names[i].split('_')[1]}" for i in k]
    base.F = np.column_stack(cols); base.Zd = np.column_stack(Zs); base.names = names
    return base


def b_call_index(u: H.Unit, ds: H.Design):
    """per grid call of each agent-day unit k: start, pulse mass, class, room; and each event's call (k, k*)."""
    G = ds.meta["_G"]
    rb = rooms_by_turn(u)
    sp = u.spans
    key = {(d, a): k for k, (d, a) in enumerate(zip(sp["day"].to_list(), sp["agent"].to_list()))}
    a_ = sp["a"].to_numpy(); b_ = sp["b"].to_numpy()
    rc = u.calls.filter(pl.col("recv")).sort("day", "agent", "t_call")
    calls = {}
    for (d, ag), grp in rc.group_by(["day", "agent"], maintain_order=True):
        k = key.get((d, ag))
        if k is None or G.get(k) is None:
            continue
        g = np.maximum.accumulate(grp["t_call"].to_numpy().astype(float))
        inr = (g >= a_[k] - 1e-6) & (g <= b_[k])
        cls = (2 * (grp["ctx_mode"].to_numpy() == "cu") + grp["wake"].to_numpy()).astype(np.int64)[inr]
        room = np.array([rb.get(t, -1) for t in grp["turn_id"].to_list()], np.int64)[inr]
        gg, e, Fm, mu, sg = G[k]
        assert len(gg) == len(cls), "grid mismatch"
        calls[k] = (gg, Fm, cls, room, int(d))
    return calls


def b_field(ds: H.Design, calls: dict, res: float, mode: str) -> H.Design:
    """replace world-B baseline bins: rows = (agent-day, class), columns = field bins."""
    NC = 4
    U = len(ds.L) // NC
    D = ds.D
    Tmax = max(float(np.max(v[0])) for v in calls.values()) + res
    nb = int(np.ceil(Tmax / res)) + 1
    rooms = sorted({int(r) for v in calls.values() for r in np.unique(v[3])})
    rix = {r: i for i, r in enumerate(rooms)}
    nr = len(rooms) if mode == "room" else 1

    def col(day, room, t):
        b = np.minimum((t // res).astype(np.int64), nb - 1)
        if mode == "shared":
            return b
        rr = np.array([rix[int(x)] for x in room]) if mode == "room" else 0
        return (day * nr + rr) * nb + b

    K = nb if mode == "shared" else D * nr * nb
    L = np.zeros((U * NC, K))
    for k, (gg, Fm, cls, room, d) in calls.items():
        c = col(d, room, gg)
        np.add.at(L, (k * NC + cls, c), Fm)
    ev_u = ds.meta["_ev_u"]; kst = ds.meta["_kstar"]
    ev_bin = np.zeros(len(ev_u), np.int64)
    for k in np.unique(ev_u):
        sel = np.flatnonzero(ev_u == k)
        gg, Fm, cls, room, d = calls[k]
        kk = kst[sel]
        ev_bin[sel] = col(d, room[kk], gg[kk])
    # drop empty columns (keeps the problem small); column 0 must be occupied (its scale is fixed to 1)
    occ = np.flatnonzero(L.sum(0) > 0)
    remap = -np.ones(K, np.int64); remap[occ] = np.arange(len(occ))
    out = copy.copy(ds)
    out.L = L[:, occ]
    out.ev_bin = remap[ev_bin]
    assert (out.ev_bin >= 0).all()
    out.meta = {k: v for k, v in ds.meta.items() if not k.startswith("_")} | {"field": (res, mode, len(occ))}
    return out


def a_field(ds: H.Design, res: float, mode: str) -> H.Design:
    """world A: ds built with BIN_S = 300 (shared 300-s columns); regroup columns to (day, res) or shared res."""
    f = int(round(res / H.BIN_S))
    K0 = ds.L.shape[1]
    nb = int(np.ceil(K0 / f))
    bcol = np.arange(K0) // f
    if mode == "shared":
        K = nb
        L = np.zeros((ds.L.shape[0], K))
        for j in range(K0):
            L[:, bcol[j]] += ds.L[:, j]
        ev = bcol[np.minimum(ds.ev_bin, K0 - 1)]
    else:
        K = ds.D * nb
        L = np.zeros((ds.L.shape[0], K))
        for j in range(K0):
            L[np.arange(len(ds.unit_day)), ds.unit_day * nb + bcol[j]] += ds.L[:, j]
        ev = ds.ev_day * nb + bcol[np.minimum(ds.ev_bin, K0 - 1)]
    occ = np.flatnonzero(L.sum(0) > 0)
    remap = -np.ones(K, np.int64); remap[occ] = np.arange(len(occ))
    out = copy.copy(ds)
    out.L = L[:, occ]; out.ev_bin = remap[ev]
    assert (out.ev_bin >= 0).all()
    out.meta = {k: v for k, v in ds.meta.items() if not k.startswith("_")} | {"field": (res, mode, len(occ))}
    return out


def heldout_field(ds: H.Design, f: H.Fit, test_days) -> tuple[float, int]:
    """test days: refit agent levels and the field; cross / self / exo weights fixed from training."""
    pr = H.Problem(ds, f.cols, test_days)
    if pr.n == 0:
        return 0.0, 0
    trU = len(f.U_sel)
    p = pr.init()
    p[pr.U + pr.Kb - 1:] = f.p[trU + f.Kb - 1:]
    fixed = np.zeros(len(p), bool)
    fixed[pr.U + pr.Kb - 1:] = True
    _, ll = pr.fit(p, fixed=fixed, maxiter=3000)
    return ll, pr.n


def fit_block(ds: H.Design, SP: dict, specs, cv: bool) -> dict:
    out, fits = {}, {}
    for s in specs:
        f = H.fit_spec(ds, SP, s, warm=fits.get("S0"))
        fits[s] = f
        br = H.branching(ds, f)
        out[f"{s}:ll"] = f.ll
        out[f"{s}:nx"] = br["n_cross"]
        for fam in ("B", "Bm", "Bu", "A"):
            if f"n_{fam}" in br:
                out[f"{s}:n_{fam}"] = br[f"n_{fam}"]
    out["n_events"] = fits[specs[0]].n
    if cv and ds.D >= 2:
        acc = {s: [0.0, 0] for s in specs}
        for fold in H.folds_for(ds.D):
            train = [d for d in range(ds.D) if d not in fold]
            f0 = None
            for s in specs:
                f = H.fit_spec(ds, SP, s, train, warm=f0 if s != "S0" else None, restart=False)
                if s == "S0":
                    f0 = f
                ll, n = heldout_field(ds, f, fold)
                acc[s][0] += ll; acc[s][1] += n
        for s, (ll, n) in acc.items():
            out[f"{s}:cv"] = ll / max(n, 1)
            out[f"{s}:cv_sum"] = ll
        out["cv_n"] = acc[specs[0]][1]
    return out
