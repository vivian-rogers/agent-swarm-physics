"""H62 core: channel-resolved at-risk cells, exposure events and parent channels for one period (no text).

assemble(P, ...) works on a period dict from infra/shared/idea_ledger.load_period (real data) or on a synthetic dict
with the same keys (t, kind, sender, cc, TS, cs, parent, use_pos, use_marker, use_cls, rows). Definitions:
../README.md, "Operational definitions" (written 2026-10-04 19:25 UTC).

Indicators per at-risk talk call c of agent j for idea i (u = another speaker's use of i):
  Model A (recency: uses j read between the start of its 3rd-previous talk call and c's producing call):
    rec_rep   >= 1 agent use read in the window that is reply-channel for j
    rec_room  read agent uses in the window, none reply-channel
    rec_hum   a human / operator use read in the window
    recg_rep, recg_room   the same under the tie-only guard
  Model B (matched lag: uses posted in (t_c - 300 s, t_c)):
    s_rep5, u_rep5, s_room5, u_room5   seen (read by the producing call) / unread (in flight, read later) by channel
    hum5      a human use posted in the window
    old       read agent uses in the recency window posted before t_c - 300 s
Channel of an agent use m by k for recipient j: direct (m's DQ2 parent is j's message) or tie (a DQ2 parent edge
joined k and j, either direction, with the replying message posted in [t_m - 2 h, t_m)). Guard: tie only, with edges
posted before the idea's first use.
"""
from __future__ import annotations

import numpy as np
import polars as pl

US = 1_000_000
INF_US = np.iinfo(np.int64).max // 4
DAY_US = 24 * 3600 * US
LAG5 = 300 * US
TIE_US = 2 * 3600 * US
H_TURNS = 15
MEM_TURNS = 3
T_CALLS = 3
IND = ["rec_rep", "rec_room", "rec_hum", "recg_rep", "recg_room", "s_rep5", "u_rep5", "s_room5", "u_room5", "hum5", "old"]


def reply_ties(P: dict) -> dict:
    """{(min(a, b), max(a, b)): sorted times of DQ2 parent edges between agents a and b}."""
    par, kind, sender, t = P["parent"], P["kind"], P["sender"], P["t"]
    ties = {}
    for b in np.where(par >= 0)[0]:
        a = par[b]
        if kind[b] != 0 or kind[a] != 0:
            continue
        x, y = int(sender[b]), int(sender[a])
        if x < 0 or y < 0 or x == y:
            continue
        ties.setdefault((min(x, y), max(x, y)), []).append(int(t[b]))
    return {k: np.sort(np.array(v, dtype=np.int64)) for k, v in ties.items()}


def _tie(ties: dict, k: int, j: int, lo: np.ndarray, hi: np.ndarray) -> np.ndarray:
    """Vector: an edge between k and j with time in [lo, hi)."""
    arr = ties.get((min(k, j), max(k, j)))
    if arr is None:
        return np.zeros(len(lo), bool)
    return np.searchsorted(arr, hi, side="left") > np.searchsorted(arr, lo, side="left")


def assemble(P: dict, cap: int = 4000, seed: int = 0, group=None, ng: int = 2) -> dict:
    """group(k, j, t_use) -> 0..ng-1 (optional) splits every channel indicator by a pair attribute (natives)."""
    t, kind, sender, TS, cs, par = P["t"], P["kind"], P["sender"], P["TS"], P["cs"], P["parent"]
    cc = P["cc"]
    ties = reply_ties(P)
    agents = sorted(int(a) for a in np.unique(sender[kind == 0]) if a >= 0 and int(a) not in cc)
    talk = {a: np.where((kind == 0) & (sender == a))[0] for a in agents}
    order = np.lexsort((P["use_pos"], P["use_marker"]))
    um, up, uc = P["use_marker"][order], P["use_pos"][order], P["use_cls"][order]
    brk = np.r_[0, np.where(np.diff(um) != 0)[0] + 1, len(um)]
    ids, cls_of = um[brk[:-1]], uc[brk[:-1]]
    rng = np.random.default_rng(seed)
    keep_ideas = set()
    for c in np.unique(cls_of):
        x = ids[cls_of == c]
        keep_ideas.update(int(v) for v in (x if len(x) <= cap else rng.choice(x, cap, replace=False)))
    CELLS, EV, AD = [], [], []
    for b in range(len(brk) - 1):
        lo, hi = brk[b], brk[b + 1]
        mk, cl = int(um[lo]), int(uc[lo])
        pos = up[lo:hi]
        tp = t[pos]
        is_ag = (kind[pos] == 0) & (sender[pos] >= 0)
        spk = np.where(is_ag, sender[pos].astype(np.int64), -100 - kind[pos].astype(np.int64))
        first = int(pos[0])
        t_first = int(t[first])
        fu = {}
        for p_, s_ in zip(pos, spk):
            if s_ >= 0 and int(s_) not in cc and int(s_) not in fu:
                fu[int(s_)] = int(p_)
        # ---------------- adopters: parent channel (all ideas)
        for a, u in fu.items():
            if u == first:
                AD.append((mk, cl, a, 0, 0, 0))
                continue
            oth = (pos < u) & (spk != a)
            tsj = TS[pos[oth], a]
            rd = tsj <= cs[u]
            if not rd.any():
                AD.append((mk, cl, a, 1, 0, 0))
                continue
            k_last = np.where(rd)[0][np.argmax(tsj[rd])]
            p_last = pos[oth][k_last]
            s_last = spk[oth][k_last]
            if s_last < 0:
                AD.append((mk, cl, a, 2, 3, 3))
                continue
            dr = bool(par[p_last] >= 0 and kind[par[p_last]] == 0 and sender[par[p_last]] == a)
            ti = bool(_tie(ties, int(s_last), a, np.array([t[p_last] - TIE_US]), np.array([t[p_last]]))[0])
            tg = bool(_tie(ties, int(s_last), a, np.array([t[p_last] - TIE_US]),
                           np.array([min(int(t[p_last]), t_first)]))[0])
            AD.append((mk, cl, a, 2, 1 if (dr or ti) else 2, 1 if tg else 2))
        if mk not in keep_ideas:
            continue
        # ---------------- at-risk calls
        for j in agents:
            if j in fu and fu[j] == first:
                continue
            xs = talk[j]
            sel = t[xs] > t_first
            if j in fu:
                sel &= xs <= fu[j]
            if not sel.any():
                continue
            ii = np.where(sel)[0]
            x = xs[ii]
            sx = cs[x]
            tx = t[x]
            s_all = cs[xs]
            s_back = np.r_[np.full(MEM_TURNS, np.iinfo(np.int64).min // 2), s_all][: len(s_all)][ii]
            oth = spk != j
            if not oth.any():
                continue
            po, so, tpo = pos[oth], spk[oth], tp[oth]
            tsj = TS[po, j]
            ag = so >= 0
            # channel of each use for j
            dr = np.array([bool(par[p] >= 0 and kind[par[p]] == 0 and sender[par[p]] == j) for p in po])
            rep = np.zeros(len(po), bool)
            repg = np.zeros(len(po), bool)
            for q in np.where(ag)[0]:
                k = int(so[q])
                tie = _tie(ties, k, j, np.array([tpo[q] - TIE_US]), np.array([tpo[q]]))[0]
                rep[q] = dr[q] or tie
                repg[q] = _tie(ties, k, j, np.array([tpo[q] - TIE_US]), np.array([min(int(tpo[q]), t_first)]))[0]
            grp = np.zeros(len(po), np.int8)
            if group is not None:
                for q in np.where(ag)[0]:
                    grp[q] = group(int(so[q]), j, int(tpo[q]))
            # matrices: calls x uses
            read_by = tsj[None, :] <= sx[:, None]
            recent = read_by & (tsj[None, :] > s_back[:, None])
            post5 = (tpo[None, :] > (tx - LAG5)[:, None]) & (tpo[None, :] < tx[:, None])
            seen5 = post5 & read_by
            unr5 = post5 & ~read_by & (tsj[None, :] < INF_US)
            agr, agrm = ag & rep, ag & ~rep
            exposed = read_by.any(1)
            adopt = (x == fu[j]) if j in fu else np.zeros(len(x), bool)
            keep = (~exposed) & (tx - t_first <= DAY_US)
            e_i = np.where(exposed)[0]
            if len(e_i):
                e0 = e_i[0]
                keep[e0:e0 + H_TURNS] |= exposed[e0:e0 + H_TURNS]
            gsplit = [np.ones(len(po), bool)] if group is None else [grp == k_ for k_ in range(ng)]
            cols = []
            for gm in gsplit:
                cols += [(recent & (agr & gm)[None, :]).any(1),
                         (recent & (ag & gm)[None, :]).any(1) & ~(recent & agr[None, :]).any(1)]
            cols += [(recent & (~ag)[None, :]).any(1),
                     (recent & (ag & repg)[None, :]).any(1),
                     (recent & ag[None, :]).any(1) & ~(recent & (ag & repg)[None, :]).any(1)]
            for gm in gsplit:
                cols += [(seen5 & (agr & gm)[None, :]).any(1), (unr5 & (agr & gm)[None, :]).any(1),
                         (seen5 & (agrm & gm)[None, :]).any(1), (unr5 & (agrm & gm)[None, :]).any(1)]
            cols += [(post5 & (~ag)[None, :]).any(1),
                     (recent & ~post5 & ag[None, :]).any(1)]
            M = np.column_stack(cols)[keep]
            ad = adopt[keep]
            for row, a_ in zip(M, ad):
                CELLS.append((mk, cl) + tuple(bool(v) for v in row) + (bool(a_),))
            # ---------------- exposure event (first exposed call), adoption within T_CALLS talk calls
            if len(e_i):
                e0 = e_i[0]
                rb = read_by[e0]
                if (rb & ag).any():
                    ch = 1 if (rb & agr).any() else 2
                    chg = 1 if (rb & ag & repg).any() else 2
                    g_ = int(grp[rb & ag].max()) if group is not None else 0
                    win = x[e0:e0 + T_CALLS]
                    a3 = bool(j in fu and fu[j] in set(win.tolist()))
                    EV.append((mk, cl, j, ch, chg, g_, a3, bool(adopt[e0])))
    gnames = [""] if group is None else [f"_g{k_}" for k_ in range(ng)]
    names = []
    for s in gnames:
        names += [f"rec_rep{s}", f"rec_room{s}"]
    names += ["rec_hum", "recg_rep", "recg_room"]
    for s in gnames:
        names += [f"s_rep5{s}", f"u_rep5{s}", f"s_room5{s}", f"u_room5{s}"]
    names += ["hum5", "old"]
    cells = pl.DataFrame(CELLS, schema=["idea", "cls"] + names + ["adopt"], orient="row")
    gk = ["idea", "cls"] + names
    cells = cells.group_by(gk).agg(pl.len().alias("calls"), pl.col("adopt").sum().alias("adopts")).sort(gk)
    ev = pl.DataFrame(EV, schema=["idea", "cls", "agent", "chan", "chan_g", "grp", "adopt3", "adopt1"], orient="row")
    ad = pl.DataFrame(AD, schema=["idea", "cls", "agent", "status", "chan", "chan_g"], orient="row")
    return dict(cells=cells, events=ev, adopters=ad,
                meta=dict(n_ideas=int(len(ids)), n_ideas_atrisk=len(keep_ideas), n_agents=len(agents),
                          n_tie_pairs=len(ties), n_parent_edges=int((par >= 0).sum())))
