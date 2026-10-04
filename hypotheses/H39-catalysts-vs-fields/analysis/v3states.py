"""H39 round 1b: the second state space, Jev v3.1 behavior states (DQ3; 5-min windows, 11-state probability vectors).

V4 lumping (fixed before any v3 statistic was computed, to mirror B4):
  work  = execute_task + research_browse + debug_recover + verify_report + communicate_external
  coord = plan_coordinate + social + meta            (talking/coordinating with the village)
  wait  = idle + monitor_wait (+ windows inside the agent's span with no activity: idle by absence, p = 1)
  maint = self_maintenance                           (memory, reflection; the consolidation analog)
Markov statistics use the probability vectors (soft transitions p_t(i) p_{t+1}(j)), not the argmax (DQ3 rule);
strata use the argmax of the last pre-kick window. A kick at time t is placed at the last window that ends before
the window containing t, so the first counted transition is the one into the kick window. W = 6 windows (30 min),
quiet = 6 windows (30 min) with no directed/human kick, past-only control eligibility, windows cut at the next kick
(transitions) and at the end of the agent's span (presence; DQ8 lever_design).
"""
from __future__ import annotations

import numpy as np
import polars as pl

import h39lib as L

SH = L.ROOT / "data/processed/shared"
V4_NAMES = ["work", "coord", "wait", "maint"]
LUMP = {"work": ["execute_task", "research_browse", "debug_recover", "verify_report", "communicate_external"],
        "coord": ["plan_coordinate", "social", "meta"], "wait": ["idle", "monitor_wait"], "maint": ["self_maintenance"]}
W_V3 = 6
QUIET_V3 = 6


def load_v3(days: list[str]) -> pl.DataFrame:
    b = (pl.scan_parquet(SH / "behavior_states_v3.parquet").filter(pl.col("pt_date").is_in(days)).collect())
    if b["holdout"].any():
        raise RuntimeError("holdout rows in v3 states")
    cols = []
    for k in V4_NAMES:
        cols.append(pl.sum_horizontal([pl.col(f"p_{s}") for s in LUMP[k]]).alias(k))
    b = b.with_columns(cols)
    # inactive windows inside the span: idle by absence
    b = b.with_columns([pl.when(pl.col("active") & pl.col("labeled")).then(pl.col(k))
                        .otherwise(pl.lit(1.0 if k == "wait" else 0.0)).alias(k) for k in V4_NAMES])
    tot = pl.sum_horizontal([pl.col(k) for k in V4_NAMES])
    b = b.with_columns([(pl.col(k) / tot).alias(k) for k in V4_NAMES])
    return b.filter(pl.col("in_span")).select("pt_date", "agent", "w", "t0", "t1", *V4_NAMES, "n_errors").sort("pt_date", "agent", "w")


def build_segments(days, cal, kicks, erasures=None, classes=("N_tgt", "H_men", "H_und", "H_any", "A_men"),
                   busy_only=("N_oth",), time_col="t"):
    """Per agent-day V4 probability arrays, swarm bins, day thirds, kick events (pre-kick window index) and busy."""
    b = load_v3(days)
    if b.height == 0:
        return None
    nwin = {r["pt_date"]: int(r["window_s"] // 300) + 1 for r in cal.filter(pl.col("pt_date").is_in(days)).iter_rows(named=True)}
    # swarm: fraction of the other in-span agents that are working or coordinating, per (day, w)
    sw = b.group_by("pt_date", "w").agg((pl.col("work") + pl.col("coord")).sum().alias("act"), pl.len().alias("n"))
    swd = {(d, int(w)): (a, n) for d, w, a, n in sw.iter_rows()}
    kk = kicks.filter(pl.col("pt_date").is_in(days)).filter(pl.col(time_col).is_not_null())
    kg = {k: g for k, g in kk.group_by(["pt_date", "agent"])}
    eg = {}
    if erasures is not None:
        eg = {k: g for k, g in erasures.filter(pl.col("pt_date").is_in(days)).group_by(["pt_date", "agent"])}
    dix = {d: i for i, d in enumerate(days)}
    seg = dict(P=[], agent=[], day=[], date=[], third=[], swarm=[], ev={c: [] for c in classes}, busy=[],
               er={"CF": [], "CV": []}, er_busy=[], nerr=[])
    for (d, a), g in b.group_by(["pt_date", "agent"], maintain_order=True):
        if g.height < 3:
            continue
        w = g["w"].to_numpy()
        P = g.select(V4_NAMES).to_numpy()
        t0 = g["t0"].dt.epoch("us").to_numpy() / 1e6
        own = (g["work"] + g["coord"]).to_numpy()
        f = np.array([((swd[(d, int(x))][0] - o) / max(swd[(d, int(x))][1] - 1, 1)) if swd[(d, int(x))][1] > 1 else 0.0
                      for x, o in zip(w, own)])
        seg["P"].append(P)
        seg["agent"].append(int(a))
        seg["day"].append(dix[d])
        seg["date"].append(d)
        seg["third"].append(((w * 3) // max(nwin.get(d, w.max() + 1), 1)).clip(0, 2).astype(np.int8))
        seg["swarm"].append(np.digitize(f, [1 / 3, 2 / 3]).astype(np.int8))
        seg["nerr"].append(g["n_errors"].fill_null(0).to_numpy())
        busy = np.zeros(len(w), bool)
        kg_ = kg.get((d, a))

        def to_pre(ts):
            j = np.searchsorted(t0, ts, side="right") - 1      # window containing ts
            return j - 1                                        # last pre-kick window
        for c in classes:
            if kg_ is None:
                seg["ev"][c].append(np.zeros(0, np.int64))
                continue
            sub = kg_.filter(pl.col("cls").cast(pl.Utf8).is_in(["H_men", "H_und"] if c == "H_any" else [c]))
            loc = to_pre(sub[time_col].dt.epoch("us").to_numpy() / 1e6)
            loc = loc[(loc >= 0) & (loc < len(w))]
            seg["ev"][c].append(np.unique(loc).astype(np.int64))
            if c != "H_any":
                busy[loc] = True
        if kg_ is not None:
            for c in busy_only:
                sub = kg_.filter(pl.col("cls").cast(pl.Utf8) == c)
                loc = to_pre(sub[time_col].dt.epoch("us").to_numpy() / 1e6)
                busy[loc[(loc >= 0) & (loc < len(w))]] = True
        seg["busy"].append(busy)
        eb = busy.copy()
        eg_ = eg.get((d, a))
        for kind in ("CF", "CV"):
            if eg_ is None:
                seg["er"][kind].append(np.zeros(0, np.int64))
                continue
            loc = to_pre(eg_.filter(pl.col("kind") == kind)["t"].dt.epoch("us").to_numpy() / 1e6)
            loc = loc[(loc >= 0) & (loc < len(w))]
            seg["er"][kind].append(np.unique(loc).astype(np.int64))
            eb[loc] = True
        seg["er_busy"].append(eb)
    return seg


def make_unit(seg, erasure=False):
    if erasure:
        return L.build_soft_unit(seg["P"], seg["agent"], seg["day"], seg["third"], 4, events=seg["er"], busy=seg["er_busy"],
                                 swarm=seg["swarm"])
    return L.build_soft_unit(seg["P"], seg["agent"], seg["day"], seg["third"], 4, events=seg["ev"], busy=seg["busy"],
                             swarm=seg["swarm"])


def run_v3(days, cal, kicks, erasures, regime, gno, B=300, P=200, classes=("N_tgt", "H_any", "H_men", "H_und", "A_men")):
    seg = build_segments(days, cal, kicks, erasures if regime == "III" else None)
    if seg is None or not seg["P"]:
        return {"status": "no v3 windows"}
    U = make_unit(seg)
    out = {"states": V4_NAMES, "n_agent_days": len(seg["P"]), "n_windows": int(len(U.x)),
           "occupancy": (U.ocum[-1] / U.ocum[-1].sum()).tolist(), "W_windows": W_V3}
    for c in classes:
        r = L.run_point(U, c, W=W_V3, B=B, P=P, seed=L.SEED + gno + 31, keep_draws=True, quiet=QUIET_V3)
        out[c] = r
    if regime == "III":
        Ue = make_unit(seg, erasure=True)
        pool = L.control_pool(Ue, W_V3, quiet=2)
        for kind in ("CF", "CV"):
            g = np.unique(Ue.events.get(kind, np.zeros(0, np.int64)))
            need = 1 if L.LEVER["presence_cut"] else W_V3 + 1
            g = g[(Ue.left[g] >= need) & (Ue.busy_in(-2, -1)[g] == 0)]
            out[f"erasure_{kind}"] = L.run_point(Ue, kind, W=W_V3, B=max(B // 2, 50), P=max(P // 2, 50),
                                                 seed=L.SEED + gno + 37, g_override=g, pool_mask=pool, quiet=2,
                                                 keep_draws=True)
    return out
