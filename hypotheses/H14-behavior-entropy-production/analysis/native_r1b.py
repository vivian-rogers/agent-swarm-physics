"""H14 round 1b native tests (layer 2; predictions on the card, "Round 1b", written before running).

N1  NE43 inside #51 (expected null): pooled v3s and act_sh_b3 EP per transition, 7 days before vs after the bookend
    step (08-05) and the nudger-off step (08-21), against placebo boundaries 07-13, 07-20, 07-27, 08-12.
N2  NE14 inside #36: 03-23 (regime II) vs 03-24 -> 03-27 (regime III), pooled EP with agent folds (coarse, act_sh, v3s).
N3  Loops vs progress in #38-#40: pooled v3s EP on transitions inside productive vs stuck windows.
Writes data/processed/H14-behavior-entropy-production/r1b/native_r1b.json.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r1b_lib as B  # noqa: E402
import round1b as RB  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

OUT = RB.OUT


def days_of(goal):
    cal = pl.read_parquet(RB.SH / "calendar.parquet").filter((pl.col("goal_no") == goal) & ~pl.col("holdout"))
    return sorted(cal["pt_date"].to_list())


def shift(d, n):
    return (dt.date.fromisoformat(d) + dt.timedelta(days=n)).isoformat()


# ---------------------------------------------------------------------------- pooled estimators on a day set
def pooled_v3s(v, P, sel_days, fold="day", mask=None):
    m = np.isin(v["pt_date"].to_numpy(), list(sel_days))
    vv = v.filter(pl.Series(m))
    Pv = P[m]
    msk = mask[m] if mask is not None else None
    i0, i1 = RB.v3_pairs(vv, mask=msk)
    if len(i0) < 50:
        return np.nan, len(i0), None
    G = B.soft_G(Pv[i0], Pv[i1])
    if fold == "day":
        lab = np.unique(vv["pt_date"].to_numpy()[i1], return_inverse=True)[1]
    else:
        lab = np.unique(vv["agent"].to_numpy()[i1], return_inverse=True)[1]
    return B.newton_G(G, lab), len(i0), (G, lab, vv["agent"].to_numpy()[i1], vv["pt_date"].to_numpy()[i1])


def pooled_turn(rec, variant, sel_days, code_map, fold="day"):
    r = rec.filter(pl.col("pt_date").is_in(list(sel_days)))
    q = 6 if variant.startswith("coarse") else int(code_map.max()) + 1
    labs = sorted(r["pt_date"].unique().to_list()) if fold == "day" else sorted(r["agent"].unique().to_list())
    li = {x: i for i, x in enumerate(labs)}
    C = np.zeros((len(labs), q, q))
    n = 0
    per_agent = {}
    for (ag,), g in r.group_by(["agent"]):
        g = g.sort("t")
        dmap = {d_: i for i, d_ in enumerate(sorted(g["pt_date"].unique().to_list()))}
        g = g.with_columns(pl.col("pt_date").replace_strict(dmap, return_dtype=pl.Int64).alias("dayc"))
        a, b, d, seg = RB.turn_chains(g, variant, code_map)
        if len(a) == 0:
            continue
        inv = {v_: k_ for k_, v_ in dmap.items()}
        if fold == "day":
            idx = np.array([li[inv[x]] for x in d])
        else:
            idx = np.full(len(a), li[ag])
        np.add.at(C, (idx, a, b), 1)
        n += len(a)
        Ca = np.zeros((len(dmap), q, q))
        np.add.at(Ca, (d, a, b), 1)
        per_agent[int(ag)] = Ca
    return B.newton_counts(C), n, per_agent, C


def code_map_for(rec):
    xs = RB.act_sh_code(rec["act"].to_numpy().astype(np.int64), rec["sh"].to_numpy().astype(np.int64))
    cnt = np.bincount(xs, minlength=len(RB.ACT_SH))
    other = RB.ACT_SH.index("other")
    m = np.array([other if cnt[k] < 0.01 * len(xs) else k for k in range(len(RB.ACT_SH))])
    used = sorted(set(m.tolist()))
    remap = {u: i for i, u in enumerate(used)}
    return np.array([remap[m[k]] for k in range(len(RB.ACT_SH))])


# ---------------------------------------------------------------------------- N1
def n1_ne43():
    days = days_of(51)
    days = [d for d in days if d <= "2026-09-02"]
    rec = pl.read_parquet(OUT / "records_r1b.parquet").filter(pl.col("goal_no") == 51)
    cm = code_map_for(rec)
    v, P, names = RB.load_v3([51])
    res = {"names": names, "boundaries": {}}
    for b, kind in (("2026-08-05", "real_bookends"), ("2026-08-21", "real_nudger_off"), ("2026-07-13", "placebo"),
                    ("2026-07-20", "placebo"), ("2026-07-27", "placebo"), ("2026-08-12", "placebo")):
        pre = [d for d in days if shift(b, -7) <= d < b]
        post = [d for d in days if b <= d < shift(b, 7)]
        e0, n0, _ = pooled_v3s(v, P, pre)
        e1, n1, _ = pooled_v3s(v, P, post)
        a0, m0, pa0, _ = pooled_turn(rec, "act_sh_b3", pre, cm)
        a1, m1, pa1, _ = pooled_turn(rec, "act_sh_b3", post, cm)
        # per-agent paired act_sh_b3 change (agents with >= 300 transitions on both sides)
        ch = []
        for ag in set(pa0) & set(pa1):
            if pa0[ag].sum() >= 300 and pa1[ag].sum() >= 300 and len(pa0[ag]) >= 2 and len(pa1[ag]) >= 2:
                x0, x1 = B.newton_counts(pa0[ag]), B.newton_counts(pa1[ag])
                if np.isfinite(x0) and np.isfinite(x1):
                    ch.append(x1 - x0)
        res["boundaries"][b] = {"kind": kind, "pre_days": len(pre), "post_days": len(post),
                                "v3s_pre": e0, "v3s_post": e1, "v3s_rel_change": (e1 - e0) / e0 if e0 and e0 > 0 else None,
                                "act_sh_b3_pre": a0, "act_sh_b3_post": a1,
                                "act_sh_b3_rel_change": (a1 - a0) / a0 if a0 and a0 > 0 else None,
                                "act_sh_b3_agent_median_change": float(np.median(ch)) if ch else None, "n_agents_paired": len(ch),
                                "n_trans_v3": [n0, n1], "n_trans_act": [m0, m1]}
    pl_ = [x for x in res["boundaries"].values() if x["kind"] == "placebo"]
    for key in ("v3s_rel_change", "act_sh_b3_rel_change"):
        vals = [x[key] for x in pl_ if x[key] is not None]
        lo, hi = (min(vals), max(vals)) if vals else (None, None)
        res[f"placebo_range_{key}"] = [lo, hi]
        for b in ("2026-08-05", "2026-08-21"):
            r = res["boundaries"][b][key]
            res["boundaries"][b][f"{key}_inside_placebo"] = bool(r is not None and lo is not None and lo <= r <= hi)
    res["prediction_holds"] = all(res["boundaries"][b][f"{k}_inside_placebo"] for b in ("2026-08-05", "2026-08-21")
                                  for k in ("v3s_rel_change", "act_sh_b3_rel_change"))
    return res


# ---------------------------------------------------------------------------- N2
def n2_ne14(rng, B_=200):
    rec = pl.read_parquet(OUT / "records_r1b.parquet").filter(pl.col("goal_no") == 36)
    cm = code_map_for(rec)
    v, P, names = RB.load_v3([36])
    pre, post = ["2026-03-23"], ["2026-03-24", "2026-03-25", "2026-03-26", "2026-03-27"]
    res = {"names": names}
    boots = {}
    for var in ("coarse", "act_sh"):
        e0, n0, pa0, C0 = pooled_turn(rec, var, pre, cm, fold="agent")
        e1, n1, pa1, C1 = pooled_turn(rec, var, post, cm, fold="agent")
        res[var] = {"pre": e0, "post": e1, "ratio": e1 / e0 if e0 and e0 > 0 else None, "n": [n0, n1]}
        bs = []
        for _ in range(B_):
            k0 = rng.integers(0, len(C0), len(C0))
            k1 = rng.integers(0, len(C1), len(C1))
            x0, x1 = B.newton_counts(C0[k0]), B.newton_counts(C1[k1])
            bs.append(x1 / x0 if x0 > 0 else np.nan)
        boots[var] = np.array(bs)
        res[var]["ratio_ci"] = np.nanpercentile(boots[var], [2.5, 97.5]).tolist()
    e0, n0, d0 = pooled_v3s(v, P, pre, fold="agent")
    e1, n1, d1 = pooled_v3s(v, P, post, fold="agent")
    res["v3s"] = {"pre": e0, "post": e1, "ratio": e1 / e0 if e0 and e0 > 0 else None, "n": [n0, n1]}
    bs = []
    for _ in range(B_):
        vals = []
        for (G, lab, ag, dd) in (d0, d1):
            ua = np.unique(lab)
            pick = rng.choice(ua, len(ua), replace=True)
            rows = np.concatenate([np.flatnonzero(lab == p) for p in pick])
            newlab = np.concatenate([np.full((lab == p).sum(), i) for i, p in enumerate(pick)])
            vals.append(B.newton_G(G[rows], newlab))
        bs.append(vals[1] / vals[0] if vals[0] and vals[0] > 0 else np.nan)
    boots["v3s"] = np.array(bs)
    res["v3s"]["ratio_ci"] = np.nanpercentile(boots["v3s"], [2.5, 97.5]).tolist()
    res["coarse_drop_ge30"] = bool(res["coarse"]["ratio"] is not None and res["coarse"]["ratio"] <= 0.7)
    res["act_sh_drop_ge30"] = bool(res["act_sh"]["ratio"] is not None and res["act_sh"]["ratio"] <= 0.7)
    res["v3s_ratio_gt_coarse"] = bool(res["v3s"]["ratio"] is not None and res["coarse"]["ratio"] is not None
                                      and res["v3s"]["ratio"] > res["coarse"]["ratio"])
    d = boots["v3s"] - boots["coarse"]
    res["v3s_minus_coarse_ratio_ci"] = np.nanpercentile(d, [2.5, 97.5]).tolist()
    return res


# ---------------------------------------------------------------------------- N3
def n3_loops(rng, B_=200):
    out = {}
    for goal in (38, 39, 40):
        v, P, names = RB.load_v3([goal])
        prod = ((v["n_commit_ok"].fill_null(0) + v["n_push_ok"].fill_null(0)) > 0) | (v["progress_score"].fill_null(0) >= 3)
        stuck = (v["p_blocked"].fill_null(0) >= 0.5) | (v["longest_run"].fill_null(0) >= 5)
        lab_ = v["labeled"]
        prod_np = (prod & ~stuck & lab_).to_numpy()
        stuck_np = (stuck & ~prod & lab_).to_numpy()
        prod, stuck = prod_np, stuck_np
        days = sorted(v["pt_date"].unique().to_list())
        r = {"n_prod_windows": int(prod.sum()), "n_stuck_windows": int(stuck.sum())}
        data = {}
        for tag, msk in (("productive", prod), ("stuck", stuck)):
            e, n, d = pooled_v3s(v, P, days, mask=msk)
            r[tag] = {"newton": e, "n_trans": n}
            data[tag] = d
        if data["productive"] is not None and data["stuck"] is not None:
            bs = []
            for _ in range(B_):
                vals = []
                for tag in ("productive", "stuck"):
                    G, lab, ag, dd = data[tag]
                    key = np.array([f"{a}|{x}" for a, x in zip(ag, dd)])
                    uk = np.unique(key)
                    pick = rng.choice(uk, len(uk), replace=True)
                    rows = np.concatenate([np.flatnonzero(key == p) for p in pick])
                    vals.append(B.newton_G(G[rows], lab[rows]))
                bs.append(vals[0] - vals[1])
            bs = np.array(bs)
            r["diff"] = r["productive"]["newton"] - r["stuck"]["newton"]
            r["diff_ci"] = np.nanpercentile(bs, [2.5, 97.5]).tolist()
            r["holds"] = bool(r["diff"] > 0 and r["diff_ci"][0] > 0)
        out[f"G{goal}"] = r
    out["periods_holding"] = sum(1 for k in ("G38", "G39", "G40") if out[k].get("holds"))
    out["prediction_holds"] = out["periods_holding"] >= 2
    return out


def main():
    rng = np.random.default_rng(20261004)
    res = {"N1_NE43": n1_ne43(), "N2_NE14": n2_ne14(rng), "N3_loops": n3_loops(rng)}
    (OUT / "native_r1b.json").write_text(json.dumps(RB.jsonable(res), indent=1))
    print(json.dumps(RB.jsonable(res), indent=1)[:6000])


if __name__ == "__main__":
    main()
