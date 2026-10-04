"""H96 natives on real (non-holdout) data.

N1 G39: two #38 rooms (DQ6 room assignments) meet one new field (#39). Domain memory
   Delta(u) = < s_iu . P_perp e_own^(-i) - s_iu . P_perp e_other >, per room of origin; room order q_room.
N2 NE38 (G51, 2026-07-29): agent 40's role reassignment. Own old state (2 active days before), field = #51 kickoff,
   #51 goal, the agent's own agent_goal; placebo = every other #51 agent with the same windows and its own old state
   and goal. M_j(u) = s_ju . P_perp e_j - median_k s_ju . P_perp e_k (k: other agents' old states).
Usage: uv run python hypotheses/H96-goal-switch-hysteresis/analysis/natives.py [--models ...]
Writes data/processed/H96-goal-switch-hysteresis/natives/natives_<model>.json
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h96lib as L  # noqa: E402

OUTD = L.DATA / "natives"


def g39(S: L.Store, X, n_boot=500, seed=0):
    rec = [r for r in L.transition_records() if r["P"] == 39][0]
    gt = pl.read_parquet(L.OUT / "ground_truth_labels.parquet").filter(
        (pl.col("goal_no") == 38) & (pl.col("label_kind") == "room_assignment"))
    room = dict(zip(gt["agent"].to_list(), gt["value"].to_list()))
    Q = S.field_basis(rec["field_gids"], rec["regime"])
    agents, V, Hc = L.unit_vectors(S, X, rec["t0"], rec["pre_day"], rec["post_days"], rec["first_day"])
    adv = L.agent_day_vectors(S, X, rec["old_days"])
    by = {rm: {k: v for k, v in adv.items() if room.get(k[0]) == rm} for rm in ("best", "rest")}
    lo = {rm: L.leave_out_dirs(by[rm], agents) for rm in by}
    q_room = {rm: float(L.order_q(by[rm])) for rm in by}
    vet = [a for a in agents if a in room]
    D = np.full((len(vet), V.shape[1]), np.nan)
    for j, a in enumerate(vet):
        own, oth = room[a], ("rest" if room[a] == "best" else "best")
        eo = L.unit(S.perp(lo[own][a], Q)); ex = L.unit(S.perp(lo[oth][-1], Q))
        D[j] = V[agents.index(a)] @ eo - V[agents.index(a)] @ ex
    rng = np.random.default_rng(seed)
    movers = {20, 21, 23}
    groups = {"all": list(range(len(vet))), "from_best": [j for j, a in enumerate(vet) if room[a] == "best"],
              "from_rest": [j for j, a in enumerate(vet) if room[a] == "rest"],
              "movers": [j for j, a in enumerate(vet) if a in movers],
              "stayers": [j for j, a in enumerate(vet) if a not in movers]}
    out = {"q_room": q_room, "n_veterans": len(vet), "H_centres": [L_(x) for x in Hc], "groups": {}}
    for gname, idx in groups.items():
        if not idx:
            continue
        idx = np.array(idx)
        def st(ix):
            with np.errstate(all="ignore"):
                M = np.nanmean(D[ix], axis=0)
            return M
        M = st(idx)
        bo = np.array([st(rng.choice(idx, len(idx))) for _ in range(n_boot)])
        with np.errstate(all="ignore"):
            ratio = bo[:, 1] / bo[:, 0]
        out["groups"][gname] = {"n": int(len(idx)), "series": [L_(x) for x in M],
                                "lo": [L_(x) for x in np.nanpercentile(bo, 2.5, axis=0)],
                                "hi": [L_(x) for x in np.nanpercentile(bo, 97.5, axis=0)],
                                "Delta_pre": L_(M[0]), "Delta_1": L_(M[1]),
                                "ratio": L_(M[1] / M[0]) if M[0] > 0 else None,
                                "ratio_ci": [L_(np.nanpercentile(ratio, 2.5)), L_(np.nanpercentile(ratio, 97.5))]}
    gb, gr = out["groups"].get("from_best"), out["groups"].get("from_rest")
    hi_q = max(q_room, key=q_room.get)
    out["higher_q_room"] = hi_q
    if gb and gr and gb["ratio"] is not None and gr["ratio"] is not None:
        out["higher_q_room_keeps_more"] = bool((gb["ratio"] > gr["ratio"]) == (hi_q == "best"))
    a = out["groups"]["all"]
    pre_pos = a["lo"][0] is not None and a["lo"][0] > 0
    d1_pos = a["lo"][1] is not None and a["lo"][1] > 0
    if pre_pos and not d1_pos:
        v = "failed"
    elif pre_pos and d1_pos and out.get("higher_q_room_keeps_more"):
        v = "supported"
    elif not pre_pos:
        v = "descriptive"
    else:
        v = "mixed"
    out["verdict"] = v
    return out


def L_(x):
    return None if (x is None or not np.isfinite(x)) else float(x)


def ne38(S: L.Store, X, n_boot=500, seed=0):
    gt = pl.read_parquet(L.OUT / "ground_truth_labels.parquet").filter(
        (pl.col("goal_no") == 51) & (pl.col("label_kind") == "role") & (pl.col("agent") == 40) & pl.col("preferred"))
    ts = gt.filter(pl.col("source_kind") == "operator message")["t_valid_to"][0]
    sday = "2026-07-29"
    days51 = sorted(set(S.day[S.goal == 51].tolist()))
    before = [d for d in days51 if d < sday]
    after = [d for d in days51 if d >= sday][:3]
    pre_rows = S.rows([sday], t_hi=ts)
    # agents with enough data on the needed days
    goals = S.goals
    ag = goals.filter((pl.col("kind") == "agent_goal") & (pl.col("goal_no") == 51))
    agoal = dict(zip(ag["agent"].to_list(), ag["gid"].to_list()))
    base = goals.filter((pl.col("goal_no") == 51) & pl.col("kind").is_in(["kickoff", "goal"]))["gid"].to_list()
    reg = "III"
    post_rows = S.rows(after, t_lo=ts)
    h = S.active_hours(post_rows, ts, after)
    # pre window: statements on the switch day before ts; old state: the two active days before
    old_days = before[-2:]
    cand = sorted(set(S.agent[pre_rows].tolist()) & set(S.agent[post_rows].tolist()))
    adv = L.agent_day_vectors(S, X, old_days)
    olds = {}
    for a in cand:
        vs = [v for (b, d), v in adv.items() if b == a]
        if vs:
            olds[a] = L.unit(np.mean(vs, 0))
    cand = [a for a in cand if a in olds and a in agoal]
    units = ["pre", "day1"] + [f"b{i}" for i in range(len(L.BINS) - 1)]
    def vecs(a, rows_pre, rows_post, hh):
        Vv = np.full((len(units), 32), np.nan)
        r = rows_pre[S.agent[rows_pre] == a]
        if len(r) >= L.MIN_BIN:
            Vv[0] = L.unit(X[r].mean(0))
        m = S.agent[rows_post] == a
        r1 = rows_post[m & (S.day[rows_post] == after[0])]
        if len(r1) >= L.MIN_BIN:
            Vv[1] = L.unit(X[r1].mean(0))
        for b in range(len(L.BINS) - 1):
            mm = m & (hh >= L.BINS[b]) & (hh < L.BINS[b + 1])
            if mm.sum() >= L.MIN_BIN:
                Vv[2 + b] = L.unit(X[rows_post[mm]].mean(0))
        return Vv
    res = {}
    for a in cand:
        Q = S.field_basis(base + [agoal[a]], reg)
        Vv = vecs(a, pre_rows, post_rows, h)
        own = Vv @ L.unit(S.perp(olds[a], Q))
        oth = np.array([Vv @ L.unit(S.perp(olds[k], Q)) for k in cand if k != a])
        M = own - np.nanmedian(oth, axis=0)
        R1 = M[1] / M[0] if M[0] > 0 else np.nan
        res[a] = {"M": M, "R1": R1}
    # bootstrap agent 40 over its statements (within units)
    rng = np.random.default_rng(seed)
    a = 40
    Q = S.field_basis(base + [agoal[a]], reg)
    eo = L.unit(S.perp(olds[a], Q)); ex = [L.unit(S.perp(olds[k], Q)) for k in cand if k != a]
    pr = pre_rows[S.agent[pre_rows] == a]; po = post_rows[S.agent[post_rows] == a]; hpo = h[S.agent[post_rows] == a]
    boots = []
    for _ in range(n_boot):
        bpr = rng.choice(pr, len(pr)); ib = rng.integers(0, len(po), len(po))
        Vv = vecs(a, bpr, po[ib], hpo[ib])
        M = Vv @ eo - np.nanmedian(np.array([Vv @ e for e in ex]), axis=0)
        boots.append(M[1] / M[0] if M[0] > 0 else np.nan)
    boots = np.array(boots)
    plac = np.array([v["R1"] for k, v in res.items() if k != 40 and np.isfinite(v["R1"])])
    r40 = res[40]["R1"]
    Hc = [None] * 2 + [L_(np.mean(h[(h >= L.BINS[b]) & (h < L.BINS[b + 1])])) if np.any((h >= L.BINS[b]) & (h < L.BINS[b + 1])) else None for b in range(len(L.BINS) - 1)]
    M40 = res[40]["M"]
    tau40 = L.fit_tau(M40, np.where(np.isfinite(M40), 2, 0), np.array([np.nan if x is None else x for x in Hc]), M40[0])
    pct = float(np.mean(plac < r40)) if len(plac) and np.isfinite(r40) else None
    out = {"t_switch": str(ts), "old_days": old_days, "post_days": after, "n_placebo_agents": int(len(plac)),
           "agent40": {"M_series": [L_(x) for x in M40], "M_pre": L_(M40[0]), "M_1": L_(M40[1]), "R1": L_(r40),
                       "R1_ci": [L_(np.nanpercentile(boots, 2.5)), L_(np.nanpercentile(boots, 97.5))],
                       "tau": L_(tau40)},
           "placebo_R1": {"median": L_(np.median(plac)), "p10": L_(np.percentile(plac, 10)),
                          "p90": L_(np.percentile(plac, 90))} if len(plac) else None,
           "agent40_percentile": pct, "H_centres": Hc}
    if not (M40[0] > 0):
        v = "descriptive"
    elif pct is not None and pct < 0.10:
        v = "failed"
    elif pct is not None and np.isfinite(r40) and np.percentile(plac, 10) <= r40 <= np.percentile(plac, 90):
        v = "supported"
    else:
        v = "mixed"
    out["verdict"] = v
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="bge_small,gte_modernbert")
    a = ap.parse_args()
    OUTD.mkdir(parents=True, exist_ok=True)
    for model in a.models.split(","):
        S = L.Store(model, "style_resid32")
        res = {"G39": g39(S, S.X), "NE38": ne38(S, S.X)}
        (OUTD / f"natives_{model}.json").write_text(json.dumps(res, indent=1, default=float))
        print(model, json.dumps({k: {kk: vv for kk, vv in v.items() if kk not in ("groups",)} for k, v in res.items()},
                                default=float)[:2000])
        print(model, "G39 groups", json.dumps({g: {k: d[k] for k in ("n", "Delta_pre", "Delta_1", "ratio", "ratio_ci")}
                                               for g, d in res["G39"]["groups"].items()}, default=float))


if __name__ == "__main__":
    main()
