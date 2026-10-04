"""H01 round 2 on REAL data (non-holdout only): R4 candidate search, then R5-R8 and D2.6 on the candidates.

Definitions, predictions and amendment A1: the card ("Round 2 formal setup", "Round 2 predictions", "Amendment A1").
Unit of analysis = round-1 unit (goal period split at catalogued step changes); every statistic is computed per unit
and summarized across units by counts, Stouffer combination or DerSimonian-Laird (h15lib.dl_meta); exception (c) for
cross-boundary designs (goal changes, #focus), exception (d) for kernel pooling toward the regime kernel.

Sections (default all): r4 r5 d26 r6 r7 r8. Usage:
  uv run python hypotheses/H01-emergent-superagents-exist/analysis/r2_run.py [--only r4,r5] [--fast]
Writes data/processed/H01-emergent-superagents-exist/round2/{results.json, G##/results_round2.json}.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import r2lib as L  # noqa: E402  (thread caps)
from h01common import guard_holdout  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

R2 = L.ROOT / "data/processed/H01-emergent-superagents-exist/round2"
SH = L.ROOT / "data/processed/shared"
ARGS = sys.argv[1:]
ONLY = set(ARGS[ARGS.index("--only") + 1].split(",")) if "--only" in ARGS else {"r4", "r4d", "r5", "d26", "r6", "r7", "r8"}
FAST = "--fast" in ARGS
SEED = 20261004
FLOOR = 0.005          # A1.2 practical floor for Delta V_st
BIN = 30.0


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.ndarray):
        return clean(o.tolist())
    return o


# ============================================================================ loading
class Data:
    def __init__(self, base: Path = R2, allow_holdout: bool = False):
        """Exploration: base = round2/, holdout asserted absent. Only analysis/confirm_r2.py (behind its flags) passes
        base = round2/confirm/ and allow_holdout=True."""
        self.units = [u for u in json.loads((base / "units.json").read_text()) if u["eligible"]]
        self.w = pl.read_parquet(base / "writes.parquet")
        self.at = pl.read_parquet(base / "attention.parquet")
        self.bins = pl.read_parquet(base / "bins.parquet")
        self.pres = pl.read_parquet(base / "presence.parquet")
        self.rooms = pl.read_parquet(base / "rooms_period.parquet")
        self.ment = pl.read_parquet(base / "mentions.parquet")
        self.scr = pl.read_parquet(base / "scrambles.parquet")
        self.states = pl.read_parquet(SH / "states_min.parquet", columns=["pt_date", "minute", "agent", "lump4_min", "in_span",
                                                                           "holdout"]).filter(allow_holdout | ~pl.col("holdout"))
        self.states = self.states.filter(pl.col("pt_date").is_in(sorted({d for u in self.units for d in u["days"]})))
        self.roster = pl.read_parquet(SH / "roster.parquet")
        self.lab = dict(zip(self.roster["agent"].to_list(), self.roster["lab"].to_list()))
        self.name = dict(zip(self.roster["agent"].to_list(), self.roster["name"].to_list()))
        cal = pl.read_parquet(SH / "calendar.parquet")
        self.cal = cal
        for t in (self.w, self.at, self.bins, self.pres, self.scr, self.states):
            if "pt_date" in t.columns:
                guard_holdout(sorted(t["pt_date"].drop_nulls().unique().to_list()), allow=allow_holdout)
        self.periods = {}

    def period(self, u: dict) -> L.Period:
        name = u["unit"]
        if name in self.periods:
            return self.periods[name]
        days = u["days"]
        b = self.bins.filter(pl.col("unit") == name).sort("pt_date", "bin")
        dmap = {d: i for i, d in enumerate(days)}
        day_of_bin = np.array([dmap[d] for d in b["pt_date"].to_list()])
        pos_of_bin = b["bin"].to_numpy()
        offs = {}
        for i, d in enumerate(days):
            offs[d] = int(np.flatnonzero(day_of_bin == i)[0])
        nbd = {d: int((day_of_bin == i).sum()) for i, d in enumerate(days)}
        ws = self.w.filter((pl.col("unit") == name) & pl.col("strict"))
        agents = sorted(ws["agent"].unique().to_list())
        projects = sorted(ws["project"].unique().to_list())
        ai = {a: i for i, a in enumerate(agents)}
        ki = {k: i for i, k in enumerate(projects)}
        nB = len(day_of_bin)
        vec, Wn = {}, np.zeros((len(agents), len(projects)))
        any_w = np.zeros((len(agents), nB), bool)
        for a, k, d, bb in ws.select("agent", "project", "pt_date", "bin").iter_rows():
            bb = min(int(bb), nbd[d] - 1)
            gb = offs[d] + bb
            vec.setdefault((ai[a], ki[k]), np.zeros(nB, bool))[gb] = True
            Wn[ai[a], ki[k]] += 1
            any_w[ai[a], gb] = True
        active = np.zeros((len(agents), len(days)), bool)
        for a, d in self.pres.filter(pl.col("unit") == name).select("agent", "pt_date").iter_rows():
            if a in ai and d in dmap:
                active[ai[a], dmap[d]] = True
        P = L.Period(name, u["regime"], day_of_bin, pos_of_bin, agents, projects, vec, Wn, any_w, b["yh"].to_numpy(),
                     active, days=days)
        P.extra.update({"ai": ai, "ki": ki, "offs": offs, "nbd": nbd, "dmap": dmap, "stall": b["stall"].to_numpy(),
                        "win_start": dict(zip(b["pt_date"].to_list(), b["win_start"].to_list()))})
        self.periods[name] = P
        return P


# ============================================================================ coarse-grainings
def coarse_grainings(D: Data, u: dict, P: L.Period) -> dict:
    name = u["unit"]
    act = [i for i in range(P.nA) if P.act_a[i] > 0]
    out = {}
    out["crew"] = [{"members": c["members"], "seed": int(P.projects[[P.projects.index(c["seed_project"])][0]])}
                   for c in L.crews(P)]
    rp = D.rooms.filter(pl.col("unit") == name)
    room_of = {P.extra["ai"][a]: r for a, r in zip(rp["agent"].to_list(), rp["room"].to_list()) if a in P.extra["ai"]}
    rooms = {}
    for i in act:
        if i in room_of:
            rooms.setdefault(room_of[i], []).append(i)
    rooms = {r: m for r, m in rooms.items() if len(m) >= 2}
    out["room"] = [{"members": m, "room": int(r)} for r, m in rooms.items()] if len(rooms) >= 2 else []
    labs = {}
    for i in act:
        labs.setdefault(D.lab.get(P.agents[i]), []).append(i)
    out["lab"] = [{"members": m, "lab": l} for l, m in labs.items() if len(m) >= 2]
    M = np.zeros((P.nA, P.nA))
    for a, t, n in D.ment.filter(pl.col("unit") == name).select("agent", "target", "n").iter_rows():
        if a in P.extra["ai"] and t in P.extra["ai"]:
            M[P.extra["ai"][a], P.extra["ai"][t]] += n
    Ms = M + M.T
    sub = np.array(act)
    comms = L.greedy_modularity(Ms[np.ix_(sub, sub)]) if len(sub) >= 3 else []
    out["comm"] = [{"members": [int(sub[j]) for j in c]} for c in comms if len(c) >= 2]
    # A1.3 coordination-based candidates
    out["sync"] = [{"members": c} for c in sync_communities(D, u, P, act)]
    out["coalloc"] = [{"members": c} for c in coalloc_communities(D, u, P, act)]
    out["vil"] = [{"members": act}]
    out["sub"] = [{"members": [i]} for i in act]
    return out


def sync_communities(D, u, P, act, slot_min=5):
    """K_sync: greedy-modularity communities of positive correlations of agents' 5-min 'working' indicators, after
    subtracting the cross-agent mean per slot (drive-robust synchrony; A1.3)."""
    st = D.states.filter(pl.col("pt_date").is_in(u["days"]) & pl.col("in_span"))
    st = st.with_columns((pl.col("minute") // slot_min).alias("slot"), (pl.col("lump4_min") == 0).alias("work"))
    g = st.group_by("pt_date", "slot", "agent").agg(pl.col("work").mean())
    slots = g.select("pt_date", "slot").unique().sort("pt_date", "slot").with_row_index("j")
    g = g.join(slots, on=["pt_date", "slot"])
    nS = slots.height
    X = np.full((P.nA, nS), np.nan)
    for a, j, w in g.select("agent", "j", "work").iter_rows():
        if a in P.extra["ai"]:
            X[P.extra["ai"][a], j] = w
    X = X - np.nanmean(X, 0, keepdims=True)
    sub = [i for i in act if np.isfinite(X[i]).sum() >= 50]
    n = len(sub)
    W = np.zeros((n, n))
    for a in range(n):
        for b in range(a + 1, n):
            ok = np.isfinite(X[sub[a]]) & np.isfinite(X[sub[b]])
            if ok.sum() >= 50 and X[sub[a], ok].std() > 0 and X[sub[b], ok].std() > 0:
                r = np.corrcoef(X[sub[a], ok], X[sub[b], ok])[0, 1]
                W[a, b] = W[b, a] = max(r, 0.0)
    comms = L.greedy_modularity(W) if n >= 3 else []
    return [[sub[j] for j in c] for c in comms if len(c) >= 2]


def coalloc_communities(D, u, P, act, wd=None):
    """K_coalloc: greedy-modularity communities of the Jaccard overlap of agents' (project, day) strict-write sets."""
    if wd is None:
        wd = wrote_day(P, D.w.filter((pl.col("unit") == u["unit"]) & pl.col("strict")))
    sets = wd.reshape(P.nA, -1)
    n = len(act)
    W = np.zeros((n, n))
    for a in range(n):
        for b in range(a + 1, n):
            A_, B_ = sets[act[a]], sets[act[b]]
            un = (A_ | B_).sum()
            W[a, b] = W[b, a] = (A_ & B_).sum() / un if un else 0.0
    comms = L.greedy_modularity(W) if n >= 3 else []
    return [[act[j] for j in c] for c in comms if len(c) >= 2]


# ============================================================================ R4
def r4_unit(D, u, P, K, rng_seed):
    nc = L.NullCache(P, n_draw=600 if FAST else 1500, seed=rng_seed)
    nca = L.NullCacheAlloc(P, n_draw=150 if FAST else 300, seed=rng_seed + 1)
    res = {}
    for kname in ("crew", "sync", "coalloc", "room", "lab", "comm", "vil"):
        rows = []
        for g in K[kname]:
            m = g["members"]
            r = L.composition_excess(P, m, nc)
            rec = {"members": [int(P.agents[i]) for i in m], "n": len(m), "z": r["z"], "iota": r["iota"],
                   "A": r["A"], "E": r["E"], "H": r["H"], "rate": r.get("rate"), "n_R": r["n_R"], "null_mu": r["null_mu"]}
            if kname != "vil" and len(m) < len(nc.pool) and len(K[kname]) <= 60:
                ism, frac = L.local_max(P, m, nc, r["z"], max_add=25 if FAST else 40)
                rec["local_max"], rec["frac_neighbors_beaten"] = ism, frac
            if kname != "vil" and len(m) >= 2:
                s = L.shift_excess(P, m, n_draw=60 if FAST else 200, seed=rng_seed)
                rec["shift_z"], rec["shift_excess"] = s["z"], s["excess"]
                ra = L.alloc_individuality(P, m)
                rec["iota_alloc"] = ra["iota_alloc"]
                if len(m) < len(nca.pool):
                    rec["alloc_z"] = nca.z(len(m), P.act_a[np.asarray(m)].sum(), ra["iota_alloc"])[0]
                if kname == "crew":
                    rec["alloc_shift_z"] = L.alloc_shift(P, m, n_draw=40 if FAST else 100, seed=rng_seed)["z"]
            if kname == "crew":
                rec["seed_project"] = g["seed"]
            rows.append(rec)
        res[kname] = rows
    summ = {}
    for kname in ("crew", "sync", "coalloc", "room", "lab", "comm"):
        zs = [r["z"] for r in res[kname] if r["z"] is not None and np.isfinite(r["z"])]
        lm = [r["local_max"] for r in res[kname] if r.get("local_max") is not None]
        az = [r["alloc_z"] for r in res[kname] if r.get("alloc_z") is not None and np.isfinite(r["alloc_z"])]
        sz = [r["shift_z"] for r in res[kname] if r.get("shift_z") is not None and np.isfinite(r["shift_z"])]
        summ[kname] = {"n_units": len(res[kname]), "n_z": len(zs), "median_z": float(np.median(zs)) if zs else None,
                       "frac_z_gt_1.64": float(np.mean([z > 1.64 for z in zs])) if zs else None,
                       "stouffer": L.stouffer(zs), "frac_local_max": float(np.mean(lm)) if lm else None, "n_lm": len(lm),
                       "median_alloc_z": float(np.median(az)) if az else None, "median_shift_z": float(np.median(sz)) if sz else None,
                       "frac_shift_z_gt_0": float(np.mean([z > 0 for z in sz])) if sz else None}
    vil = res["vil"][0] if res["vil"] else {}
    summ["vil_iota"] = vil.get("iota")
    return res, summ


def r4_verdict(per):
    """Card R4 criteria on the composition excess (pre-registered) and on iota_alloc (A1, reported separately)."""
    out = {}
    for stat in ("median_z", "median_alloc_z"):
        elig, wins, room_lab_first = 0, 0, 0
        for u, s in per.items():
            if s["crew"]["n_units"] < 2 or s["crew"][stat] is None:
                continue
            rivals = {k: s[k][stat] for k in ("room", "lab", "comm") if s[k]["n_units"] >= 2 and s[k][stat] is not None}
            if not rivals:
                continue
            elig += 1
            wins += all(s["crew"][stat] > v for v in rivals.values())
            best = max(list(rivals.items()) + [("crew", s["crew"][stat])], key=lambda kv: kv[1])[0]
            room_lab_first += best in ("room", "lab")
        out[stat] = {"eligible_units": elig, "crew_ranks_first": wins, "room_or_lab_first": room_lab_first,
                     "R4a": bool(elig and wins >= 2 / 3 * elig)}
    lm = {k: [] for k in ("crew", "sync", "coalloc", "room", "lab", "comm")}
    zc = []
    for u, s in per.items():
        for k in lm:
            if s[k]["frac_local_max"] is not None:
                lm[k] += [s[k]["frac_local_max"]] * s[k]["n_lm"]
        if s["crew"]["median_z"] is not None:
            zc.append(s["crew"]["median_z"])
    frac = {k: (float(np.mean(v)) if v else None) for k, v in lm.items()}
    out["coordination_based_median_z"] = {u: {k: s[k]["median_z"] for k in ("crew", "sync", "coalloc", "comm", "room", "lab")}
                                          for u, s in per.items()}
    out["R4b"] = {"frac_local_max": frac, "pass": bool(frac["crew"] is not None and frac["crew"] >= 0.5 and
                                                       all(frac["crew"] > (frac[k] if frac[k] is not None else -1) for k in ("room", "lab", "comm")))}
    return out, zc


# ============================================================================ R4d / R6b: allocation continuity across nights
def units_leaveout(D, u, P, K, wd_cnt, d_ex, kname):
    """Units of coarse-graining kname with membership and R_G recomputed from writes excluding day d_ex (A1.2, A1.9)."""
    Wn_ex = wd_cnt.sum(2) - wd_cnt[:, :, d_ex]
    tot = Wn_ex.sum(0)

    def R_of(m):
        own = Wn_ex[np.asarray(m, int)].sum(0)
        return np.flatnonzero((tot >= L.MIN_PROJ_WRITES) & (own >= L.SHARE_RULE * tot) & (own > 0))
    act = [i for i in range(P.nA) if Wn_ex[i].sum() > 0]
    if kname == "crew":
        groups, seen = [], set()
        for k in range(Wn_ex.shape[1]):
            if tot[k] < 10:
                continue
            mem = tuple(int(a) for a in np.flatnonzero(Wn_ex[:, k] >= 2))
            if len(mem) >= 2 and mem not in seen:
                seen.add(mem)
                groups.append(list(mem))
    elif kname == "coalloc":
        wd = wd_cnt > 0
        wd = wd.copy()
        wd[:, :, d_ex] = False
        groups = coalloc_communities(D, u, P, act, wd=wd)
    elif kname == "sub":
        groups = [[i] for i in act]
    else:
        groups = [g["members"] for g in K[kname]]
    return [{"members": g, "R": R_of(g)} for g in groups if len(R_of(g))]


def continuity_leaveout(D, u, P, K, kname, n_perm=300, seed=0):
    rng = np.random.default_rng(seed)
    wu = D.w.filter((pl.col("unit") == u["unit"]) & pl.col("strict"))
    nd = len(P.days)
    wd_cnt = np.zeros((P.nA, len(P.projects), nd))
    for a, k, d in wu.select("agent", "project", "pt_date").iter_rows():
        wd_cnt[P.extra["ai"][a], P.extra["ki"][k], P.extra["dmap"][d]] += 1
    wd = wd_cnt > 0
    hits = n_tot = 0
    null = np.zeros(n_perm)
    for d in range(nd - 1):
        both = np.flatnonzero(P.active[:, d] & P.active[:, d + 1])
        if len(both) < 3:
            continue
        cl = units_leaveout(D, u, P, K, wd_cnt, d + 1, kname)
        if not cl:
            continue
        pos = {int(a): j for j, a in enumerate(both)}
        nxt = wd[both, :, d + 1]
        Hm = np.zeros((len(both), len(cl)), bool)
        Ms = []
        for g, c in enumerate(cl):
            Hm[:, g] = nxt[:, c["R"]].any(1)
            Ms.append([pos[int(a)] for a in c["members"] if int(a) in pos and wd[int(a), c["R"], d].any()])
        tot = sum(len(M) for M in Ms)
        if tot == 0:
            continue
        hits += sum(Hm[M, g].sum() for g, M in enumerate(Ms))
        n_tot += tot
        for t in range(n_perm):
            perm = rng.permutation(len(both))
            null[t] += sum(Hm[perm[M], g].sum() for g, M in enumerate(Ms) if M)
    if n_tot == 0:
        return None
    C, Cn = hits / n_tot, null / n_tot
    return {"C": float(C), "C_null": float(Cn.mean()), "dC": float(C - Cn.mean()), "p": float((Cn >= C).mean()), "n": int(n_tot)}


def r4d(D, K_all):
    per = {}
    for i, u in enumerate(D.units):
        P = D.period(u)
        if len(P.days) < 2:
            continue
        per[u["unit"]] = {k: continuity_leaveout(D, u, P, K_all[u["unit"]], k, n_perm=150 if FAST else 400, seed=SEED + 500 + i)
                          for k in ("crew", "coalloc", "sync", "comm", "room", "lab", "sub")}
        log("R4d", u["unit"], {k: (round(v["dC"], 3) if v else None) for k, v in per[u["unit"]].items()})
    elig = wins = 0
    for unit, r in per.items():
        art = [r[k]["dC"] for k in ("crew", "coalloc") if r.get(k)]
        base = [r[k]["dC"] for k in ("room", "lab") if r.get(k)]
        if art and base:
            elig += 1
            wins += min(art) > max(base)
    crew_dc = [r["crew"]["dC"] for r in per.values() if r.get("crew")]
    return {"per_unit": per, "eligible": elig, "n_artifact_units_beat_rooms_labs": wins,
            "R4d": bool(elig and wins >= 2 / 3 * elig),
            "R6b_leaveout": {"n_units": len(crew_dc), "n_dC_ge_0.2": int(sum(v >= 0.2 for v in crew_dc)),
                             "median_dC": float(np.median(crew_dc)) if crew_dc else None,
                             "pass": bool(crew_dc and sum(v >= 0.2 for v in crew_dc) >= 2 / 3 * len(crew_dc))}}


# ============================================================================ R5
def unit_series(P, members):
    x, y, S, R = P.unit_xy(members)
    return x, y, P.day_of_bin


def member_series_xy(P, members):
    S, R = P.member_series(members)
    out = []
    for j, a in enumerate(members):
        others = np.ones(P.nA, bool)
        others[a] = False
        yw = P.any_w[others].any(0)
        out.append((S[j], (yw.astype(np.int8) * 2 + P.yh.astype(np.int8)).astype(np.int8), P.day_of_bin))
    return out


def regime_prior(D, K_all, kname):
    """Exception (d): pooled kernel of a coarse-graining over all units of a regime (prior for partial pooling)."""
    priors = {}
    for reg in ("I", "II", "III"):
        T = []
        for u in D.units:
            if u["regime"] != reg or u["unit"] not in K_all:
                continue
            P = D.period(u)
            groups = K_all[u["unit"]][kname] if kname != "member" else K_all[u["unit"]]["crew"]
            for g in groups:
                if kname == "member":
                    xy = member_series_xy(P, g["members"])
                else:
                    xy = [unit_series(P, g["members"])]
                T1, _ = L.transitions_from_units(xy, P.trans, 1)
                T.append(T1)
        if T and sum(len(t) for t in T) > 50:
            T = np.concatenate(T)
            K = L.fit_kernel([(T[:, 0], T[:, 1], T[:, 2], T[:, 3])])
            priors[reg] = L.Kernel(K.Kx, K.Ky, K.nx)
    return priors


def r5_unit(D, u, P, K, priors, rng_seed):
    res = {}
    for kname in ("crew", "member", "room", "lab", "comm"):
        groups = K["crew"] if kname == "member" else K[kname]
        if not groups:
            continue
        xy = []
        for g in groups:
            xy += member_series_xy(P, g["members"]) if kname == "member" else [unit_series(P, g["members"])]
        pr = priors.get(kname, {}).get(u["regime"])
        r = L.kw_semantic(xy, P.trans, tau=4, prior=pr, n_boot=60 if FAST else 200, seed=rng_seed)
        r.pop("curve", None)
        res[kname] = r
    # day-level landscape variant (crews)
    x0, y0, v = [], [], []
    for g in K["crew"]:
        x, y, S, R = P.unit_xy(g["members"])
        nd = len(P.days)
        Vd = np.array([x[P.day_of_bin == d].mean() for d in range(nd)])
        ywd = np.array([(y[P.day_of_bin == d] >= 2).mean() for d in range(nd)])
        yhd = np.array([(y[P.day_of_bin == d] % 2).mean() for d in range(nd)])
        med = np.median(Vd)
        for d in range(nd - 1):
            x0.append(int(Vd[d] > med)); y0.append(int(ywd[d] > np.median(ywd)) * 2 + int(yhd[d] > np.median(yhd))); v.append(Vd[d + 1])
    res["crew_day"] = L.kw_day_landscape(np.array(x0, int), np.array(y0, int), np.array(v, float))
    return res


def r5_verdict(per5):
    ok, pos, gt = 0, 0, 0
    obs = 0
    rows = {}
    for u, r in per5.items():
        c, m = r.get("crew"), r.get("member")
        if not c or not c.get("ok"):
            continue
        ok += 1
        p = bool((c.get("dV_st_lo") or -1) > 0 and c["dV_st"] >= FLOOR)
        pos += p
        po = bool((c.get("dV_obs_lo") or -1) > 0 and c["dV_obs"] >= FLOOR)
        obs += po
        g = bool(m and m.get("ok") and c["dV_st"] > m["dV_st"])
        gt += g
        rows[u] = {"dV_st": c["dV_st"], "lo": c.get("dV_st_lo"), "hi": c.get("dV_st_hi"), "dV_obs": c["dV_obs"],
                   "obs_lo": c.get("dV_obs_lo"), "I": c["I"], "pinsker": c["pinsker"], "eta": c.get("eta"),
                   "member_dV_st": m.get("dV_st") if m else None, "pos": p, "obs_pos": po, "crew_gt_member": g,
                   "positivity_low_mass": c.get("positivity_low_mass"), "ck_err": c.get("ck_err"),
                   "V": c["V"], "V_emp": c.get("V_emp")}
    return {"eligible": ok, "n_dV_st_pos": pos, "n_dV_obs_pos": obs, "n_crew_gt_member": gt,
            "R5a": bool(ok and pos >= ok / 2 and gt >= 2 / 3 * ok), "R5b": bool(ok and obs >= ok / 2), "per_unit": rows}


# ============================================================================ cross-boundary designs (R5c, R7c)
BOUNDARIES = [("30", 31, "new"), ("35", 36, "new"), ("36b", 37, "new"), ("37", 38, "new"), ("38c", 39, "new"),
              ("39", 40, "continuation"), ("40", 41, "new"), ("41", 42, "new")]


def goal_change(D, K_all):
    """Goal change as a full scramble of the unit-goal correlation (F6): crews' V_adv on R_G (any writer) over the next
    goal's first 2 active days vs the crew's last 2 days; probability that R_G is written at all."""
    out = {}
    w = D.w.filter(pl.col("strict"))
    for (uname, g_next, kind) in BOUNDARIES:
        u = next((x for x in D.units if x["unit"] == uname), None)
        if u is None or uname not in K_all:
            continue
        P = D.period(u)
        nd = [d for d in sorted(D.cal.filter(pl.col("goal_no") == g_next)["pt_date"].to_list())
              if d in set(w["pt_date"].unique().to_list())][:2]
        last = u["days"][-2:]
        nbins = {d: int(np.ceil(D.cal.filter(pl.col("pt_date") == d)["window_s"][0] / 1800)) for d in last + nd}
        rows = []
        for g in K_all[uname]["crew"]:
            R = [P.projects[k] for k in P.shared_artifacts(g["members"])]
            if not R:
                continue
            wr = w.filter(pl.col("project").is_in(R))
            def vadv(days):
                x = wr.filter(pl.col("pt_date").is_in(days)).select("pt_date", "bin").unique()
                return x.height / max(sum(nbins[d] for d in days), 1)
            v_pre, v_post = vadv(last), vadv(nd)
            mem = {P.agents[i] for i in g["members"]}
            n_mem_post = wr.filter(pl.col("pt_date").is_in(nd) & pl.col("agent").is_in(list(mem)))["agent"].n_unique()
            rows.append({"members": len(g["members"]), "v_pre": v_pre, "v_post": v_post, "dV": v_post - v_pre,
                         "written_post": bool(v_post > 0), "members_writing_post": n_mem_post})
        if rows:
            dv = np.array([r["dV"] for r in rows])
            out[f"{uname}->{g_next}"] = {"kind": kind, "next_days": nd, "n_crews": len(rows), "mean_dV": float(dv.mean()),
                                        "se": float(dv.std(ddof=1) / np.sqrt(len(dv))) if len(dv) > 1 else None,
                                        "mean_v_pre": float(np.mean([r["v_pre"] for r in rows])),
                                        "p_written_post": float(np.mean([r["written_post"] for r in rows])), "crews": rows}
    new = [v for v in out.values() if v["kind"] == "new" and v["se"]]
    meta = L.h15lib.dl_meta([v["mean_dV"] for v in new], [v["se"] for v in new]) if new else None
    cont = [v for v in out.values() if v["kind"] == "continuation"]
    return {"boundaries": out, "meta_new": meta,
            "p_written_new": float(np.mean([v["p_written_post"] for v in out.values() if v["kind"] == "new"])) if new else None,
            "p_written_cont": cont[0]["p_written_post"] if cont else None,
            "R5c": bool(meta and meta["z"] <= -2 and (not cont or cont[0]["mean_dV"] > meta["mu"]))}


def focus_cut(D, K_all):
    """#focus (08-05): crews of 51b whose members were split across #general / #focus vs crews kept together."""
    u = next((x for x in D.units if x["unit"] == "51b"), None)
    if u is None:
        return None
    P = D.period(u)
    pres = D.pres.filter(pl.col("pt_date").is_in(["2026-08-05", "2026-08-06"]))
    room = {}
    for a, r in pres.select("agent", "room").iter_rows():
        room.setdefault(a, set()).add(r)
    w = D.w.filter(pl.col("strict"))
    last = u["days"][-2:]
    nd = ["2026-08-05", "2026-08-06"]
    nb = {d: int(np.ceil(D.cal.filter(pl.col("pt_date") == d)["window_s"][0] / 1800)) for d in last + nd}
    rows = []
    for g in K_all["51b"]["crew"]:
        R = [P.projects[k] for k in P.shared_artifacts(g["members"])]
        if not R:
            continue
        rs = set()
        for i in g["members"]:
            rs |= room.get(P.agents[i], set())
        split = 15 in rs and 0 in rs
        wr = w.filter(pl.col("project").is_in(R))
        vd = lambda days: wr.filter(pl.col("pt_date").is_in(days)).select("pt_date", "bin").unique().height / sum(nb[d] for d in days)
        rows.append({"split": split, "dV": vd(nd) - vd(last), "v_pre": vd(last)})
    sp = [r["dV"] for r in rows if r["split"]]
    ns = [r["dV"] for r in rows if not r["split"]]
    return {"n_split": len(sp), "n_together": len(ns), "mean_dV_split": float(np.mean(sp)) if sp else None,
            "mean_dV_together": float(np.mean(ns)) if ns else None,
            "did": float(np.mean(sp) - np.mean(ns)) if sp and ns else None}


# ============================================================================ minute-level helpers
def clock(D, P, pt_dates, minutes):
    return np.array([P.extra["dmap"][d] * 1440.0 + m for d, m in zip(pt_dates, minutes)])


def day_bounds(D, P):
    out = []
    for d in P.days:
        nb = P.extra["nbd"][d]
        out.append((P.extra["dmap"][d] * 1440.0, P.extra["dmap"][d] * 1440.0 + nb * BIN))
    return out


# ============================================================================ D2.6 (group level) and stall effects
def d26_and_stalls(D, K_all, rng_seed):
    rng = np.random.default_rng(rng_seed)
    outs = pl.read_parquet(SH / "outages.parquet").filter(~pl.col("holdout") & (pl.col("village_off") | pl.col("infra_burst"))
                                                         & ~pl.col("at_day_edge"))
    cands = ["V_adv", "V_cnt", "V_mem", "V_foc", "V_ord", "V_rel"]
    by_reg = {"I/II": {c: {"D0": [], "D3": [], "P0": [], "P3": []} for c in cands},
              "III": {c: {"D0": [], "D3": [], "P0": [], "P3": []} for c in cands}}
    rec_obs, rec_exp = [], []
    for u in D.units:
        P = D.period(u)
        reg = "III" if u["regime"] == "III" else "I/II"
        st = outs.filter(pl.col("pt_date").is_in(u["days"]))
        if st.height == 0:
            continue
        ws_ = P.extra["win_start"]
        sc = [(P.extra["dmap"][d] * 1440.0 + (s0 - ws_[d]).total_seconds() / 60, P.extra["dmap"][d] * 1440.0 + (s1 - ws_[d]).total_seconds() / 60)
              for d, s0, s1 in st.select("pt_date", "t_start", "t_end").iter_rows()]
        bounds = day_bounds(D, P)
        wu = D.w.filter((pl.col("unit") == u["unit"]) & pl.col("strict"))
        au = D.at.filter(pl.col("unit") == u["unit"])
        wt = clock(D, P, wu["pt_date"].to_list(), wu["minute"].to_list())
        at_t = clock(D, P, au["pt_date"].to_list(), au["minute"].to_list())
        wa, wk, wc = wu["agent"].to_numpy(), wu["project"].to_numpy(), wu["confirmed"].to_numpy()
        wpush = (wu["vclass"] == "push").to_numpy()
        aa, ak = au["agent"].to_numpy(), au["project"].to_numpy()
        for g in K_all[u["unit"]]["crew"]:
            mem = np.array([P.agents[i] for i in g["members"]])
            R = np.array([P.projects[k] for k in P.shared_artifacts(g["members"])])
            if len(R) == 0:
                continue
            mw = np.isin(wa, mem)
            if (mw & np.isin(wk, R)).sum() < 20:
                continue
            mwR = mw & np.isin(wk, R)
            ma = np.isin(aa, mem)

            def V(lo, hi):
                inw = (wt >= lo) & (wt < hi)
                ina = (at_t >= lo) & (at_t < hi) & ma
                vals = {"V_adv": float((inw & mwR).any()), "V_cnt": float((inw & mwR).sum()),
                        "V_mem": float(len(set(wa[inw & mwR])) / len(mem))}
                na = ina.sum()
                vals["V_foc"] = float(np.isin(ak[ina], R).mean()) if na >= 2 else np.nan
                if na >= 3:
                    _, cnt = np.unique(ak[ina], return_counts=True)
                    vals["V_ord"] = -L._H_counts(cnt.astype(float))
                else:
                    vals["V_ord"] = np.nan
                pu = inw & mwR & wpush
                vals["V_rel"] = float(wc[pu].mean()) if pu.sum() >= 1 else np.nan
                return vals

            def disp(t0, t1):
                pre = V(t0 - 20, t0)
                p0 = V(t1, t1 + 10)
                p3 = V(t1 + 30, t1 + 40)
                return {c: (p0[c] - pre[c], p3[c] - pre[c]) for c in cands}
            for (t0, t1) in sc:
                if not any(lo <= t0 - 20 and t1 + 40 <= hi for lo, hi in bounds):
                    continue
                dd = disp(t0, t1)
                for c in cands:
                    by_reg[reg][c]["D0"].append(dd[c][0]); by_reg[reg][c]["D3"].append(dd[c][1])
                # R8c: unit recovery in the 30 min after the stall vs the aggregation (independent members) baseline
                inw = (wt >= t1) & (wt < t1 + 30) & mwR
                rec_obs.append(float(inw.any()))
                # members' individual post-stall write probabilities in this unit (all stalls), then 1 - prod(1 - p)
                rec_exp.append((u["unit"], tuple(mem), t1))
            # placebo pseudo-stalls
            for _ in range(len(sc) * (2 if FAST else 6)):
                lo, hi = bounds[rng.integers(len(bounds))]
                dur = sc[rng.integers(len(sc))][1] - sc[rng.integers(len(sc))][0]
                dur = max(dur, 1.0)
                t0 = rng.uniform(lo + 20, hi - 40 - dur) if hi - lo > 60 + dur else None
                if t0 is None or any(abs(t0 - s0) < 30 or abs(t0 - s1) < 30 for s0, s1 in sc):
                    continue
                dd = disp(t0, t0 + dur)
                for c in cands:
                    by_reg[reg][c]["P0"].append(dd[c][0]); by_reg[reg][c]["P3"].append(dd[c][1])
    choice = {}
    for reg, cc in by_reg.items():
        rows = {}
        for c, v in cc.items():
            D0 = np.array(v["D0"], float); D3 = np.array(v["D3"], float)
            ok = np.isfinite(D0) & np.isfinite(D3)
            P0 = np.array(v["P0"], float); P3 = np.array(v["P3"], float)
            okp = np.isfinite(P0) & np.isfinite(P3)
            if ok.sum() < 10 or okp.sum() < 30:
                rows[c] = {"n": int(ok.sum())}
                continue
            delta = float(np.median(np.abs(D0[ok])))
            Rv = float(1 - np.median(np.abs(D3[ok])) / delta) if delta > 0 else np.nan
            # placebo distribution of (delta, R) by resampling pseudo-events in groups of the real size
            pd_, pr_ = [], []
            idx = np.flatnonzero(okp)
            for _ in range(200):
                s = rng.choice(idx, ok.sum(), replace=True)
                dlt = np.median(np.abs(P0[s]))
                pd_.append(dlt)
                pr_.append(1 - np.median(np.abs(P3[s])) / dlt if dlt > 0 else np.nan)
            pd_, pr_ = np.array(pd_), np.array(pr_)
            pr_ = pr_[np.isfinite(pr_)]
            homeo = bool(delta > np.percentile(pd_, 95) and len(pr_) and Rv > np.percentile(pr_, 95) and Rv >= 0.5)
            rows[c] = {"n": int(ok.sum()), "delta": delta, "R": Rv, "delta_p95": float(np.percentile(pd_, 95)),
                       "R_p95": float(np.percentile(pr_, 95)) if len(pr_) else None,
                       "R_minus_placebo_median": float(Rv - np.median(pr_)) if len(pr_) else None, "homeostatic": homeo}
        hom = [c for c, r in rows.items() if r.get("homeostatic")]
        if hom:
            vstar = max(hom, key=lambda c: rows[c]["R_minus_placebo_median"])
            verdict = "chosen"
        else:
            vstar, verdict = "V_adv", "inconclusive (V_adv by the pre-registered default)"
        choice[reg] = {"candidates": rows, "V_star": vstar, "verdict": verdict}
    return choice, (rec_obs, rec_exp)


# ============================================================================ R6
def r6_spillover(D, K_all, rng_seed):
    """NE41: other members' writes on R_G around a member's forced consolidation (A1.3 edge-trimmed, rotation null)."""
    out = {}
    for u in D.units:
        if u["regime"] != "III":
            continue
        P = D.period(u)
        sc = D.scr.filter((pl.col("unit") == u["unit"]) & (pl.col("kind") == "CF"))
        if sc.height == 0:
            continue
        wu = D.w.filter((pl.col("unit") == u["unit"]) & pl.col("strict"))
        wt = clock(D, P, wu["pt_date"].to_list(), wu["minute"].to_list())
        wa, wk = wu["agent"].to_numpy(), wu["project"].to_numpy()
        ct = clock(D, P, sc["pt_date"].to_list(), sc["minute"].to_list())
        ca = sc["agent"].to_numpy()
        bounds = day_bounds(D, P)
        events = []
        shares = []
        for g in K_all[u["unit"]]["crew"]:
            mem = [P.agents[i] for i in g["members"]]
            R = [P.projects[k] for k in P.shared_artifacts(g["members"])]
            if not R:
                continue
            mR = np.isin(wk, R) & np.isin(wa, mem)
            tot = mR.sum()
            for a in mem:
                events.append({"t_cons": ct[ca == a], "w_self": wt[mR & (wa == a)], "w_other": wt[mR & (wa != a)],
                               "day_bounds": bounds})
                shares.append((mR & (wa == a)).sum() / max(tot, 1))
        sp = L.spillover(events, n_rot=60 if FAST else 200, seed=rng_seed)
        if sp.get("ok"):
            s, o = sp["self"], sp["other"]
            beta = (s["effect_per_event"] + o["effect_per_event"]) / s["effect_per_event"] if s["effect_per_event"] != 0 else np.nan
            sp["beta"] = beta
            out[u["unit"]] = sp
    effs = [v["other"]["rel"] for v in out.values() if v["other"]["rel"] is not None and np.isfinite(v["other"]["rel"])]
    zs = [v["other"]["z"] for v in out.values()]
    return {"per_unit": out, "median_other_rel": float(np.median(effs)) if effs else None,
            "stouffer_other": L.stouffer(zs), "median_self_rel": float(np.median([v["self"]["rel"] for v in out.values()])) if out else None,
            "median_beta": float(np.nanmedian([v["beta"] for v in out.values()])) if out else None}


def wrote_day(P, w_unit):
    nd = len(P.days)
    out = np.zeros((P.nA, len(P.projects), nd), bool)
    for a, k, d in w_unit.select("agent", "project", "pt_date").iter_rows():
        if a in P.extra["ai"] and k in P.extra["ki"] and d in P.extra["dmap"]:
            out[P.extra["ai"][a], P.extra["ki"][k], P.extra["dmap"][d]] = True
    return out


def r6_night_and_memory(D, K_all, rng_seed):
    night, mem = {}, {"event": [], "base": [], "rows": []}
    for u in D.units:
        P = D.period(u)
        wu = D.w.filter((pl.col("unit") == u["unit"]) & pl.col("strict"))
        wd = wrote_day(P, wu)
        cl = [{"members": g["members"], "R": P.shared_artifacts(g["members"])} for g in K_all[u["unit"]]["crew"]]
        cl = [c for c in cl if len(c["R"])]
        if not cl or len(P.days) < 2:
            continue
        r = L.night_continuity(P, cl, wd, n_perm=200 if FAST else 500, seed=rng_seed)
        if r.get("ok"):
            r.pop("pairs", None)
            night[u["unit"]] = r
        ev = D.scr.filter((pl.col("unit") == u["unit"]) & pl.col("kind").is_in(["ML", "MG"]))
        evset = {(a, d) for a, d in ev.select("agent", "pt_date").iter_rows()}
        for c in cl:
            for i in c["members"]:
                a = P.agents[i]
                for d in range(1, len(P.days)):
                    if not (P.active[i, d] and P.active[i, d - 1] and wd[i, c["R"], d - 1].any()):
                        continue
                    hit = bool(wd[i, c["R"], d].any())
                    if (a, P.days[d]) in evset:
                        mem["event"].append(hit)
                        mem["rows"].append({"unit": u["unit"], "agent": int(a), "day": P.days[d], "hit": hit})
                    else:
                        mem["base"].append(hit)
    dCs = [v["dC"] for v in night.values()]
    mem_s = {"n_event": len(mem["event"]), "event_rate": float(np.mean(mem["event"])) if mem["event"] else None,
             "base_rate": float(np.mean(mem["base"])) if mem["base"] else None, "rows": mem["rows"]}
    # A2 (2026-10-04, after the first real run): overlapping crews count one memory event several times; the
    # unique-agent-day version is the correct implementation of the pre-registered statistic (both reported)
    uq = {(x["agent"], x["day"]): x["hit"] for x in mem["rows"]}
    mem_s["n_unique_agent_days"] = len(uq)
    mem_s["unique_event_rate"] = float(np.mean(list(uq.values()))) if uq else None
    mem_s["n_unique_agents"] = len({a for a, _ in uq})
    if mem["event"]:
        mem_s["diff"] = mem_s["event_rate"] - mem_s["base_rate"]
        mem_s["unique_diff"] = mem_s["unique_event_rate"] - mem_s["base_rate"]
        # binomial SE of the event rate
        mem_s["se"] = float(np.sqrt(mem_s["event_rate"] * (1 - mem_s["event_rate"]) / len(mem["event"]))) if 0 < mem_s["event_rate"] < 1 else None
    return {"night": night, "n_units": len(night), "n_dC_ge_0.2": int(sum(v >= 0.2 for v in dCs)),
            "median_dC": float(np.median(dCs)) if dCs else None,
            "R6b": bool(dCs and sum(v >= 0.2 for v in dCs) >= 2 / 3 * len(dCs))}, mem_s


# ============================================================================ R7
def r7(D, K_all, rng_seed):
    deps, placebo, theseus = [], [], []
    for u in D.units:
        P = D.period(u)
        nd = len(P.days)
        wu = D.w.filter((pl.col("unit") == u["unit"]) & pl.col("strict"))
        wd_cnt = np.zeros((P.nA, len(P.projects), nd))
        for a, k, d in wu.select("agent", "project", "pt_date").iter_rows():
            wd_cnt[P.extra["ai"][a], P.extra["ki"][k], P.extra["dmap"][d]] += 1
        nbins = np.array([P.extra["nbd"][d] for d in P.days], float)
        for g in K_all[u["unit"]]["crew"]:
            m = np.array(g["members"])
            R = P.shared_artifacts(m)
            if len(R) == 0:
                continue
            cnt = wd_cnt[m][:, R].sum(1)          # [members, days]
            tot = cnt.sum(0) / nbins              # writes per bin (V_cnt)
            x, _, S, _ = P.unit_xy(list(m))
            vadv = np.array([x[P.day_of_bin == d].mean() for d in range(nd)])
            alive = np.flatnonzero(tot > 0)
            # Ship of Theseus
            if len(alive) and alive[-1] - alive[0] + 1 >= 6:
                life = np.arange(alive[0], alive[-1] + 1)
                k3 = max(1, len(life) // 3)
                f = set(m[cnt[:, life[:k3]].sum(1) > 0]); l_ = set(m[cnt[:, life[-k3:]].sum(1) > 0])
                jac = len(f & l_) / len(f | l_) if f | l_ else np.nan
                slope = float(np.polyfit(np.arange(len(life)), vadv[life], 1)[0])
                theseus.append({"unit": u["unit"], "n_members": len(m), "life_days": int(len(life)), "jaccard_first_last": jac,
                                "vadv_slope_per_day": slope})
            for d0 in range(2, nd - 1):
                pre = cnt[:, d0 - 2:d0].sum(1)
                if pre.sum() < 5 or tot[d0 - 2:d0].mean() <= 0:
                    continue
                share = pre / pre.sum()
                dep_i = [j for j in range(len(m)) if share[j] >= 0.2 and cnt[j, d0:d0 + 2].sum() == 0
                         and P.active[m[j], d0 - 2:d0].any()]
                rel = (tot[d0:d0 + 2].mean() - tot[d0 - 2:d0].mean()) / tot[d0 - 2:d0].mean()
                drel_adv = vadv[d0:d0 + 2].mean() - vadv[d0 - 2:d0].mean()
                died = bool(tot[d0:].sum() == 0)
                rec = {"unit": u["unit"], "rel_V_cnt": float(rel), "dV_adv": float(drel_adv), "died": died}
                if dep_i:
                    j = max(dep_i, key=lambda j: share[j])
                    rec.update({"share": float(share[j]), "left_village": bool(not P.active[m[j], d0:d0 + 2].any())})
                    deps.append(rec)
                else:
                    placebo.append(rec)
    out = {"n_departures": len(deps), "departures": deps, "n_placebo": len(placebo), "theseus": theseus}
    if deps:
        excess = np.array([d["rel_V_cnt"] + d["share"] for d in deps])
        prel = np.array([p["rel_V_cnt"] for p in placebo])
        out["mean_rel_V_cnt"] = float(np.mean([d["rel_V_cnt"] for d in deps]))
        out["mean_share"] = float(np.mean([d["share"] for d in deps]))
        out["mean_excess_over_minus_share"] = float(excess.mean())
        out["se_excess"] = float(excess.std(ddof=1) / np.sqrt(len(excess))) if len(excess) > 1 else None
        out["placebo_mean_rel_V_cnt"] = float(prel.mean()) if len(prel) else None
        out["death_rate_after_departure"] = float(np.mean([d["died"] for d in deps]))
        pdie = np.array([p["died"] for p in placebo], float)
        out["death_rate_placebo"] = float(pdie.mean()) if len(pdie) else None
        if len(pdie):
            rng = np.random.default_rng(rng_seed)
            sims = [rng.choice(pdie, len(deps)).mean() for _ in range(2000)]
            out["death_placebo_band95"] = [float(np.percentile(sims, 2.5)), float(np.percentile(sims, 97.5))]
        lo = out["mean_excess_over_minus_share"] - 1.96 * (out["se_excess"] or 0)
        out["R7a"] = bool(lo > -0.0 or out["mean_excess_over_minus_share"] >= 0) and bool(
            "death_placebo_band95" not in out or out["death_rate_after_departure"] <= out["death_placebo_band95"][1])
    if theseus:
        js = [t["jaccard_first_last"] for t in theseus]
        out["theseus_median_jaccard"] = float(np.nanmedian(js))
        out["theseus_frac_jacc_lt_0.5"] = float(np.nanmean(np.array(js) < 0.5))
        out["theseus_median_slope"] = float(np.median([t["vadv_slope_per_day"] for t in theseus]))
        out["R7b"] = bool(out["theseus_frac_jacc_lt_0.5"] >= 0.5 and out["theseus_median_slope"] >= -0.02)
    return out


# ============================================================================ R8
def r8_response(D, K_all):
    """A1.5: other members' write ATTEMPTS on R_G within 30 min after a member's unconfirmed vs confirmed push.
    The confirmed-outcome version is reported but uninterpretable (common platform state)."""
    out = {}
    for u in D.units:
        P = D.period(u)
        wu = D.w.filter((pl.col("unit") == u["unit"]) & pl.col("strict"))
        wt = clock(D, P, wu["pt_date"].to_list(), wu["minute"].to_list())
        wa, wk, wc = wu["agent"].to_numpy(), wu["project"].to_numpy(), wu["confirmed"].to_numpy()
        push = (wu["vclass"] == "push").to_numpy()
        cnt = {"u": [0, 0], "c": [0, 0], "u_conf": [0, 0], "c_conf": [0, 0]}
        n_un = 0
        for g in K_all[u["unit"]]["crew"]:
            mem = [P.agents[i] for i in g["members"]]
            R = [P.projects[k] for k in P.shared_artifacts(g["members"])]
            if not R:
                continue
            sel = np.isin(wk, R) & np.isin(wa, mem)
            ts, as_, cs, ps = wt[sel], wa[sel], wc[sel], push[sel]
            order = np.argsort(ts)
            ts, as_, cs, ps = ts[order], as_[order], cs[order], ps[order]
            last_ev = {}
            for i in range(len(ts)):
                if not ps[i]:
                    continue
                key = (as_[i], cs[i])
                if key in last_ev and ts[i] - last_ev[key] < 10:   # one event per agent and outcome per 10 min
                    continue
                last_ev[key] = ts[i]
                j = np.searchsorted(ts, ts[i], "right")
                k2 = np.searchsorted(ts, ts[i] + 30, "right")
                oth = (as_[j:k2] != as_[i])
                anyo = bool(oth.any())
                anyo_c = bool((oth & cs[j:k2]).any())
                tag = "c" if cs[i] else "u"
                cnt[tag][0] += anyo; cnt[tag][1] += 1
                cnt[tag + "_conf"][0] += anyo_c; cnt[tag + "_conf"][1] += 1
                n_un += (not cs[i])
        if cnt["u"][1] >= 1 and cnt["c"][1] >= 1:
            ra = (cnt["u"][0] / cnt["u"][1]) / (cnt["c"][0] / cnt["c"][1]) if cnt["c"][0] else np.nan
            rc = (cnt["u_conf"][0] / cnt["u_conf"][1]) / (cnt["c_conf"][0] / cnt["c_conf"][1]) if cnt["c_conf"][0] else np.nan
            out[u["unit"]] = {"n_unconfirmed": cnt["u"][1], "n_confirmed": cnt["c"][1], "ratio_attempt": ra,
                              "ratio_confirmed_uninterpretable": rc}
    el = {k: v for k, v in out.items() if v["n_unconfirmed"] >= 10 and np.isfinite(v["ratio_attempt"])}
    n12 = sum(v["ratio_attempt"] >= 1.2 for v in el.values())
    return {"per_unit": out, "eligible": len(el), "n_ratio_ge_1.2": int(n12),
            "median_ratio_attempt": float(np.median([v["ratio_attempt"] for v in el.values()])) if el else None,
            "R8a": bool(el and n12 >= 2 / 3 * len(el))}


def r8_stall_recovery(D, rec):
    """Unit recovery after stalls vs the aggregation baseline 1 - prod_i(1 - p_i), p_i = member i's own probability of
    writing on R_G in the 30 min after a stall in that unit (estimated over the unit's stalls)."""
    obs, keys = rec
    if not obs:
        return None
    # member-level post-stall write probability per unit (any project write as a proxy for R_G-level availability)
    by_unit = {}
    for (uname, mem, t1), o in zip(keys, obs):
        by_unit.setdefault(uname, []).append((mem, t1, o))
    exp_all, obs_all = [], []
    for uname, rows in by_unit.items():
        u = next(x for x in D.units if x["unit"] == uname)
        P = D.period(u)
        wu = D.w.filter((pl.col("unit") == uname) & pl.col("strict"))
        wt = clock(D, P, wu["pt_date"].to_list(), wu["minute"].to_list())
        wa = wu["agent"].to_numpy()
        stalls = sorted({t1 for _, t1, _ in rows})
        p_i = {}
        for a in set(a for mem, _, _ in rows for a in mem):
            hits = [((wt >= t1) & (wt < t1 + 30) & (wa == a)).any() for t1 in stalls]
            p_i[a] = float(np.mean(hits))
        for mem, t1, o in rows:
            exp_all.append(1 - np.prod([1 - p_i[a] for a in mem]))
            obs_all.append(o)
    return {"n": len(obs_all), "obs": float(np.mean(obs_all)), "aggregation_baseline": float(np.mean(exp_all)),
            "R8c": bool(np.mean(obs_all) > np.mean(exp_all) + 0.05)}


# ============================================================================ main
def main():
    t0 = time.time()
    D = Data()
    path = R2 / "results.json"
    res = json.loads(path.read_text()) if path.exists() else {}
    K_all = {}
    for u in D.units:
        P = D.period(u)
        K_all[u["unit"]] = coarse_grainings(D, u, P)
    res["coarse_grainings"] = {u: {k: len(v) for k, v in K.items()} for u, K in K_all.items()}
    log("coarse-grainings", res["coarse_grainings"])
    if "r4" in ONLY:
        per, full = {}, {}
        for i, u in enumerate(D.units):
            t1 = time.time()
            P = D.period(u)
            full[u["unit"]], per[u["unit"]] = r4_unit(D, u, P, K_all[u["unit"]], SEED + i)
            log("R4", u["unit"], {k: (v["median_z"], v["frac_local_max"], v["median_alloc_z"]) if isinstance(v, dict) else v
                                  for k, v in per[u["unit"]].items()}, f"{time.time() - t1:.0f}s")
        verdict, zc = r4_verdict(per)
        allcrew = [r["z"] for s in full.values() for r in s["crew"] if r["z"] is not None and np.isfinite(r["z"])]
        verdict["R4c"] = {"stouffer_all_crews": L.stouffer(allcrew), "n_crews": len(allcrew),
                          "n_units_crew_median_z_le_0": int(sum(z <= 0 for z in zc)), "n_units": len(zc),
                          "pass": bool(L.stouffer(allcrew)[1] < 0.01)}
        res["r4"] = {"per_unit_summary": per, "verdict": verdict}
        res["r4_units"] = full
        log("R4 verdict", verdict)
    if "r4d" in ONLY:
        res["r4d"] = r4d(D, K_all)
        log("R4d verdict", {k: v for k, v in res["r4d"].items() if k != "per_unit"})
    if "r5" in ONLY:
        priors = {k: regime_prior(D, K_all, k) for k in ("crew", "member", "room", "lab", "comm")}
        per5 = {}
        for i, u in enumerate(D.units):
            t1 = time.time()
            per5[u["unit"]] = r5_unit(D, u, D.period(u), K_all[u["unit"]], priors, SEED + 100 + i)
            c = per5[u["unit"]].get("crew", {})
            log("R5", u["unit"], {k: round(c[k], 4) for k in ("dV_st", "dV_st_lo", "dV_obs", "I", "pinsker") if c.get(k) is not None},
                f"{time.time() - t1:.0f}s")
        res["r5"] = {"per_unit": per5, "verdict": r5_verdict(per5), "goal_change": goal_change(D, K_all),
                     "focus_cut": focus_cut(D, K_all)}
        log("R5 verdict", {k: v for k, v in res["r5"]["verdict"].items() if k != "per_unit"},
            {k: v for k, v in res["r5"]["goal_change"].items() if k != "boundaries"}, res["r5"]["focus_cut"])
    rec = None
    if "d26" in ONLY or "r8" in ONLY:
        choice, rec = d26_and_stalls(D, K_all, SEED + 200)
        res["d26"] = choice
        log("D2.6", {r: (c["V_star"], c["verdict"]) for r, c in choice.items()})
    if "r6" in ONLY:
        sp = r6_spillover(D, K_all, SEED + 300)
        night, mem = r6_night_and_memory(D, K_all, SEED + 301)
        shift = None
        if "r4_units" in res:
            zs = {u: [r.get("shift_z") for r in v["crew"] if r.get("shift_z") is not None] for u, v in res["r4_units"].items()}
            med = {u: float(np.median(v)) for u, v in zs.items() if v}
            shift = {"per_unit_median_shift_z": med, "n_units_pos": int(sum(v > 0 for v in med.values())), "n_units": len(med),
                     "R6d": bool(med and sum(v > 0 for v in med.values()) >= 2 / 3 * len(med))}
        res["r6"] = {"spillover": sp, "night": night, "memory_loss": mem, "shift": shift}
        log("R6", {k: sp[k] for k in ("median_other_rel", "median_self_rel", "median_beta", "stouffer_other")},
            {k: night[k] for k in ("n_units", "n_dC_ge_0.2", "median_dC", "R6b")}, {k: mem.get(k) for k in ("n_event", "event_rate", "base_rate", "diff")}, shift and {k: shift[k] for k in ("n_units_pos", "n_units", "R6d")})
    if "r7" in ONLY:
        res["r7"] = r7(D, K_all, SEED + 400)
        log("R7", {k: v for k, v in res["r7"].items() if k not in ("departures", "theseus")})
    if "r8" in ONLY:
        res["r8"] = {"response": r8_response(D, K_all), "stall_recovery": r8_stall_recovery(D, rec)}
        log("R8", {k: v for k, v in res["r8"]["response"].items() if k != "per_unit"}, res["r8"]["stall_recovery"])
    res["runtime_s"] = time.time() - t0
    path.write_text(json.dumps(clean(res), indent=1))
    log("done", f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
