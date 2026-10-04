"""H97 native tests (predictions in each folder README, written before running):
  N1 NE38  Claude Opus 5's reassignment (2026-07-29 16:51 UTC) as a one-agent kickoff
  N2 G44   #42 last day -> #44 day 1, assigned named-target room (#best) vs free-choice room (#rest)
  N3 G26   the elected leader's goal announcement (2026-01-05 19:36 UTC) as an agent-authored second target
Writes data/processed/H97-quench-restoring-force/natives/{NE38,G44,G26}.json.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h97lib as L  # noqa: E402

OPUS5 = 40
OUT = L.DATA / "natives"


def chi_mem_all(bd, seed=0):
    XA, XB, Y, agents = L.split_arrays(bd, n_splits=50, seed=seed)
    return dict(zip(agents, L.agent_chi_mem(XA, XB, Y))), (XA, XB, Y, agents)


def agent_mem_sub(XA, XB, Y, j, k, sub):
    """One agent's memory of its offset from the others, in a subspace (1 - chi)."""
    N = Y.shape[0]; o = np.r_[0:j, j + 1:N]
    a = L._proj(XA[:, j] - XA[:, o].mean(1), k, sub); b = L._proj(XB[:, j] - XB[:, o].mean(1), k, sub)
    y = L._proj(Y[j] - Y[o].mean(0), k, sub)
    num = (a * y).sum() + (b * y).sum(); den = 2 * (a * b).sum()
    return num / den if den > 0 else np.nan


def ne38(model="bge_small"):
    stmt, tr = L.load_design("NE38")
    k = L.vectors("NE38", "k", model)
    sv = lambda m: L.seg_vectors(stmt, m, model)  # noqa: E731
    t0 = dt.datetime(2026, 7, 29, 16, 51, tzinfo=dt.timezone.utc)
    pre = sv(pl.col("pt_date") == "2026-07-28")
    post = sv((pl.col("t") >= t0) & pl.col("pt_date").is_in(["2026-07-29", "2026-07-30"]))
    bd = L.boundary(pre, post)
    cm, (XA, XB, Y, agents) = chi_mem_all(bd)
    j = agents.index(OPUS5) if OPUS5 in agents else None
    others = np.array([v for a, v in cm.items() if a != OPUS5 and np.isfinite(v)])
    res = dict(model=model, N=len(agents), opus5_present=j is not None)
    if j is not None:
        X, P = bd[OPUS5]
        disp = P.mean(0) - X.mean(0)
        res.update(chi_opus5=float(cm[OPUS5]), others_q90=float(np.percentile(others, 90)),
                   others_median=float(np.median(others)),
                   pct_among_others=float((others < cm[OPUS5]).mean()),
                   move_cos_new_goal=float(disp @ k / np.linalg.norm(disp)),
                   mem_par=float(agent_mem_sub(XA, XB, Y, j, k, "par")), mem_perp=float(agent_mem_sub(XA, XB, Y, j, k, "perp")))
        # Opus 5 at ordinary day boundaries in the same window (placebo)
        days = sorted(stmt["pt_date"].unique().to_list())
        plc = []
        for d0, d1 in zip(days[:-1], days[1:]):
            if d1 in ("2026-07-29", "2026-07-30") or d0 == "2026-07-29":
                continue
            b2 = L.boundary(sv(pl.col("pt_date") == d0), sv(pl.col("pt_date") == d1))
            if OPUS5 in b2 and len(b2) >= L.MIN_N_TRANSITION:
                c2, _ = chi_mem_all(b2, seed=3)
                plc.append(dict(d0=d0, d1=d1, chi=float(c2[OPUS5])))
        res["opus5_placebo"] = plc
    res["prediction_N1"] = bool(j is not None and res["chi_opus5"] > res["others_q90"] and res["move_cos_new_goal"] > 0)
    return res


def g44(model="bge_small"):
    stmt, tr = L.load_design("G44")
    room = {int(a): v for a, v in json.loads(tr["room_map"]).items()}
    sv = lambda m: L.seg_vectors(stmt, m, model)  # noqa: E731
    bd = L.boundary(sv(pl.col("seg") == "prev"), sv(pl.col("seg") == "day1"))
    cm, (XA, XB, Y, agents) = chi_mem_all(bd)
    kb, kr = L.vectors("G44", "k_best", model), L.vectors("G44", "k_rest", model)
    rows = []
    for a in agents:
        X, P = bd[a]; disp = P.mean(0) - X.mean(0)
        own, oth = (kb, kr) if room.get(a) == "best" else (kr, kb)
        rows.append(dict(agent=a, room=room.get(a), chi=float(cm[a]),
                         own_minus_other=float(disp @ own - disp @ oth)))
    df = pl.DataFrame(rows).filter(pl.col("room").is_not_null())
    best = df.filter(pl.col("room") == "best")["chi"].to_numpy(); rest = df.filter(pl.col("room") == "rest")["chi"].to_numpy()
    diff = float(np.mean(best) - np.mean(rest))
    rng = np.random.default_rng(5); allc = df["chi"].to_numpy(); nb = len(best)
    null = [np.mean(p[:nb]) - np.mean(p[nb:]) for p in (rng.permutation(allc) for _ in range(5000))]
    return dict(model=model, N=len(agents), n_best=int(nb), n_rest=int(len(rest)), chi_best=best.tolist(), chi_rest=rest.tolist(),
                diff=diff, p_perm=float((np.sum(np.array(null) >= diff) + 1) / 5001),
                own_minus_other_best=float(df.filter(pl.col("room") == "best")["own_minus_other"].mean()),
                own_minus_other_rest=float(df.filter(pl.col("room") == "rest")["own_minus_other"].mean()),
                prediction_N2=bool(diff > 0))


def g26(model="bge_small"):
    stmt, tr = L.load_design("G26")
    sv = lambda m: L.seg_vectors(stmt, m, model)  # noqa: E731
    k = L.vectors("G26", "k", model)
    ann_row = np.load(L.DATA / "vectors.npz")["G26|ann_row"]
    Z = L.statement_matrix(model, "white")
    ann = np.asarray(Z[int(ann_row[0])], dtype=np.float64) if len(ann_row) else None

    def mem(bd, seed):
        XA, XB, Y, ag, YA, YB = L.split_arrays(bd, n_splits=30, seed=seed, with_y_halves=True)
        r = L.memory_corr(XA, XB, Y, YA, YB, k, "full")
        mv = None
        if ann is not None:
            mv = float(np.mean([(bd[a][1].mean(0) - bd[a][0].mean(0)) @ ann for a in ag]))
        return r, mv, len(ag)

    bd = L.boundary(sv(pl.col("seg") == "pre"), sv(pl.col("seg") == "post"))
    r_ann, mv_ann, n_ann = mem(bd, 1)
    cut = dt.time(19, 36, 3)
    plc = []
    for d in sorted(stmt.filter(pl.col("day_idx").is_between(2, 5))["pt_date"].unique().to_list()):
        day = stmt.filter(pl.col("pt_date") == d)
        tcut = dt.datetime.combine(dt.date.fromisoformat(d), cut, tzinfo=dt.timezone.utc)
        b2 = L.boundary(L.seg_vectors(day, pl.col("t") < tcut, model), L.seg_vectors(day, pl.col("t") >= tcut, model))
        if len(b2) >= L.MIN_N_TRANSITION:
            r2, mv2, n2 = mem(b2, 2)
            plc.append(dict(day=d, rho=float(r2), move_ann=mv2, N=n2))
    pr = np.array([p["rho"] for p in plc])
    pct = float((np.sum(pr < r_ann) + 0.5 * np.sum(pr == r_ann)) / len(pr)) if len(pr) else np.nan
    return dict(model=model, N=n_ann, rho_announcement=float(r_ann), move_toward_announcement=mv_ann, placebo=plc,
                percentile_among_placebo=pct, prediction_N3=bool(0.1 <= pct <= 0.9) if np.isfinite(pct) else None)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in (("NE38", ne38), ("G44", g44), ("G26", g26)):
        res = {m: fn(m) for m in ("bge_small", "gte_modernbert")}
        (OUT / f"{name}.json").write_text(json.dumps(res, indent=1, default=float))
        print(name, json.dumps(res, default=float)[:900])


if __name__ == "__main__":
    main()
