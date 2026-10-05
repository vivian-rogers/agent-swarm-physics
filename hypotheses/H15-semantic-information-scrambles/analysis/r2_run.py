"""H15 round 2 on real (non-reserved) data: R1a, R1b, R1c, R2, R3.

    uv run python hypotheses/H15-semantic-information-scrambles/analysis/r2_run.py

Reads data/processed/H15-semantic-information-scrambles/r2/{events,segs,newcomer_days,notes}.parquet (build_r2.py) and
writes r2/results.json and r2/r3_notes.parquet (per-note recall statistics; hashes and numbers only).
Pre-registration, synthetic validation and amendments A1-A7: card section "Round 2".
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import r2lib as L  # noqa: E402
from h15common import refuse_holdout  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

T0 = time.time()
B = 300
SEED = 20261005


def log(*a):
    print(f"[{time.time() - T0:7.1f}s]", *a, flush=True)


def ci_rr(f, key, boot=None):
    b, se = f[key]["b"], f[key]["se"]
    d = {"RR": L.rr(b), "lo_sw": L.rr(b - 1.96 * se), "hi_sw": L.rr(b + 1.96 * se), "se": se,
         "MDE80": L.rr(2.8 * se) if np.isfinite(se) else float("nan")}
    if boot is not None and key in boot:
        d["lo_boot"], d["hi_boot"] = L.rr(boot[key]["lo"]), L.rr(boot[key]["hi"])
    return d


def per_period(e, y, classes, keys, min_F=200):
    per, out = {}, {}
    for p in L.PERIODS:
        sub = e.filter(pl.col("period") == p)
        if sub.filter(pl.col("etype") == "F").height < min_F:
            out[p] = {"n_F": sub.filter(pl.col("etype") == "F").height, "note": f"< {min_F} F events"}
            continue
        # fitting guard (added after the first real run, 2026-10-05): a class with < 10 F or < 10 P events carrying it
        # in this period is dropped from the period's model (its interaction is not estimable there)
        use = [c for c in classes if min(sub.filter((pl.col("etype") == a) & pl.col(c)).height for a in ("F", "P")) >= 10]
        f = L.fit(sub, y, use)
        per[p] = f
        out[p] = {"n": f["n"], "n_F": f["n_F"], "dropped": [c for c in classes if c not in use],
                  **{k: ci_rr(f, k) for k in keys if k in f}}
    pooled = {k: L.pool(per, k) for k in keys}
    return out, pooled, per


def fit_dip(e, y, on_col, other=()):
    """Stratum FE (not x arm), explicit F: dip with the class off vs on (share of the dip it carries)."""
    F = (e["etype"] == "F").to_numpy().astype(float)
    cols = [F]
    names = ["F"]
    for c in (on_col, *other):
        x = e[c].cast(pl.Float64).to_numpy()
        cols += [x, x * F]
        names += [c, f"{c}xF"]
    cols.append(np.log1p(np.clip(e["V_pre"].to_numpy(), 0, None)))
    X = np.column_stack(cols)
    V = e[y].to_numpy().astype(float)
    ok = np.isfinite(V)
    b = L.poisson_fe(V[ok], X[ok], e["stratum"].to_numpy()[ok])
    bF, bI = b[0], b[names.index(f"{on_col}xF")]
    off, on = 1 - math.exp(bF), 1 - math.exp(bF + bI)
    return {"dip_off": off, "dip_on": on, "share": (off - on) / off if off > 0 else float("nan")}


def boot_dip(e, y, on_col, other, B_, seed):
    rng = np.random.default_rng(seed)
    cl = L.codes(e["cluster"].to_numpy())
    K = cl.max() + 1
    order = np.argsort(cl, kind="stable")
    starts = np.searchsorted(cl[order], np.arange(K))
    ends = np.append(starts[1:], len(cl))
    sh = []
    for _ in range(B_):
        idx = np.concatenate([order[starts[p]:ends[p]] for p in rng.integers(0, K, K)])
        sh.append(fit_dip(e[idx], y, on_col, other)["share"])
    sh = np.array(sh)
    sh = sh[np.isfinite(sh)]
    return [float(np.percentile(sh, 2.5)), float(np.percentile(sh, 97.5))]


# ------------------------------------------------------------------------------------------------ R1a
def r1a(e):
    out, est, se = {}, [], []
    for p in L.PERIODS:
        sub = e.filter(pl.col("period") == p)
        F, P = sub.filter(pl.col("etype") == "F"), sub.filter(pl.col("etype") == "P")
        cF = L.cluster_mean_ci(F["rs5"].to_numpy(), F["cluster"].to_numpy(), seed=1)
        cP = L.cluster_mean_ci(P["rs5"].to_numpy(), P["cluster"].to_numpy(), seed=2)
        d = cF["est"] - cP["est"]
        s = math.sqrt(cF["se"] ** 2 + cP["se"] ** 2)
        out[p] = {"rs5_F": cF["est"], "rs5_P": cP["est"], "diff": d, "lo": d - 1.96 * s, "hi": d + 1.96 * s,
                  "touch5_F": float(F["touch5"].mean()), "touch5_P": float(P["touch5"].mean()),
                  "touchA5_F": float(F.filter(pl.col("A_prev") >= 0)["touchA5"].mean()),
                  "touchA5_P": float(P.filter(pl.col("A_prev") >= 0)["touchA5"].mean()),
                  "touch_any5_F": float((F["touch5"] | F["touchA5"]).mean()),
                  "first_read_med_F": float(F.filter(pl.col("first_read") <= 5)["first_read"].median()),
                  "n_F": F.height, "n_P": P.height}
        est.append(d)
        se.append(s)
    pd_ = L.dl_pool(est, se)
    allF = e.filter(pl.col("etype") == "F")
    allP = e.filter(pl.col("etype") == "P")
    return {"per": out, "pooled_diff": pd_, "n_pos": int(sum(v["lo"] > 0 for v in out.values())),
            "touch_any5_F": float((allF["touch5"] | allF["touchA5"]).mean()),
            "touch_any5_P": float((allP["touch5"] | allP["touchA5"]).mean()),
            "touch5_F": float(allF["touch5"].mean()), "touch5_P": float(allP["touch5"].mean()),
            "touchA5_F": float(allF.filter(pl.col("A_prev") >= 0)["touchA5"].mean()),
            "touchA5_P": float(allP.filter(pl.col("A_prev") >= 0)["touchA5"].mean())}


# ------------------------------------------------------------------------------------------------ R1c
def r1c():
    sg = pl.read_parquet(L.DATA / "segs.parquet")
    cat = pl.read_parquet(L.ROOT / "data/processed/H15-semantic-information-scrambles/r1b/scramble_catalog.parquet")
    refuse_holdout(cat["pt_date"].unique().to_list(), "catalog")
    ev = cat.filter(pl.col("type").is_in(["ML", "MG"]) & (pl.col("regime") == "III")).sort("t")
    rows = []
    for typ, a, t, gno in zip(ev["type"].to_list(), ev["agent"].to_list(), ev["t"].to_list(), ev["goal_no"].to_list()):
        s_a = sg.filter((pl.col("agent") == a) & (pl.col("goal_no") == gno))
        post = s_a.filter((pl.col("t_first") >= t) & (pl.col("t_first") <= t + pl.duration(minutes=30))).sort("t_first")
        pool = s_a.filter((pl.col("t_first") - t).abs() > pl.duration(days=1))["rs5"].to_numpy()
        if post.height == 0 or len(pool) < 10:
            continue
        x = float(post["rs5"][0])
        rows.append({"type": typ, "agent": a, "goal_no": gno, "x": x, "ctrl": float(pool.mean()),
                     "diff": x - float(pool.mean()), "z": (x - pool.mean()) / pool.std() if pool.std() > 0 else 0.0})
    df = pl.DataFrame(rows)
    out = {"n": df.height}
    for nm, sub in (("ML+MG", df), ("ML", df.filter(pl.col("type") == "ML")), ("MG", df.filter(pl.col("type") == "MG"))):
        if sub.height:
            d = sub["diff"].to_numpy()
            out[nm] = {"n": sub.height, "mean_diff": float(d.mean()),
                       "lo": float(d.mean() - 1.96 * d.std(ddof=1) / math.sqrt(len(d))) if len(d) > 1 else float("nan"),
                       "hi": float(d.mean() + 1.96 * d.std(ddof=1) / math.sqrt(len(d))) if len(d) > 1 else float("nan"),
                       "stouffer_z": float(sub["z"].sum() / math.sqrt(sub.height)),
                       "mean_ctrl": float(sub["ctrl"].mean())}
    # newcomers (regime III MN): read-or-search share per call, tenure days 1-3 vs 6-12
    nd = pl.read_parquet(L.DATA / "newcomer_days.parquet")
    mn = cat.filter((pl.col("type") == "MN") & (pl.col("regime") == "III"))
    nrows = []
    for a, d0 in zip(mn["agent"].to_list(), mn["pt_date"].to_list()):
        s = nd.filter((pl.col("agent") == a) & (pl.col("pt_date") >= d0)).sort("pt_date").with_row_index("ten", 1)
        e13, e612 = s.filter(pl.col("ten") <= 3), s.filter((pl.col("ten") >= 6) & (pl.col("ten") <= 12))
        if e13.height and e612.height >= 3:
            w = lambda q: float((q["rs_share"] * q["n_calls"]).sum() / q["n_calls"].sum())  # noqa: E731
            nrows.append({"agent": a, "d13": w(e13), "d612": w(e612)})
    if nrows:
        nn = pl.DataFrame(nrows).with_columns((pl.col("d13") - pl.col("d612")).alias("diff"))
        d = nn["diff"].to_numpy()
        sd_ctrl = float(nd.group_by("agent").agg(pl.col("rs_share").std())["rs_share"].median())
        out["MN"] = {"n": len(d), "mean_diff": float(d.mean()),
                     "lo": float(d.mean() - 1.96 * d.std(ddof=1) / math.sqrt(len(d))) if len(d) > 1 else float("nan"),
                     "hi": float(d.mean() + 1.96 * d.std(ddof=1) / math.sqrt(len(d))) if len(d) > 1 else float("nan"),
                     "n_positive": int((d > 0).sum()), "mean_d13": float(nn["d13"].mean()),
                     "mean_d612": float(nn["d612"].mean()),
                     "MDE80_from_spread": float(2.8 * d.std(ddof=1) / math.sqrt(len(d))) if len(d) > 1 else float("nan"),
                     "day_sd_median": sd_ctrl}
    return out


# ------------------------------------------------------------------------------------------------ R3
def r3():
    notes = pl.read_parquet(L.DATA / "notes.parquet").filter(pl.col("terms").list.len() > 0)
    refuse_holdout(notes["pt_date"].unique().to_list(), "notes")
    tab = L.r3_table(notes, seed=SEED)
    chat = [np.asarray(x, np.int64) for x in notes["chat_post"].to_list()]
    empty = [np.zeros(0, np.int64)] * len(chat)
    tabc = L.r3_table(notes, post=chat, post10=empty, post31=empty, seed=SEED + 1)
    tab = tab.with_columns(pl.format("{}|{}", "agent", "pt_date").alias("cluster"),
                           (pl.col("r_pre") - pl.col("r_post")).alias("pre_minus_post"),
                           (pl.col("E10_s") - pl.col("E31_s")).alias("decay"))
    keys = ["r_post", "r_pre", "pre_minus_post", "E_s", "Enov_s", "E_x", "Enov_x", "E10_s", "E31_s", "decay", "nov_w"]
    out = {"n_notes": tab.height, "per": {}, "pooled": {}}
    for p in L.PERIODS:
        sub = tab.filter(pl.col("period") == p)
        if sub.height < 30:
            continue
        out["per"][p] = {k: L.cluster_mean_ci(sub[k].to_numpy(), sub["cluster"].to_numpy(), B=300, seed=7)
                         for k in keys}
    for k in keys:
        est = [out["per"][p][k]["est"] for p in out["per"]]
        se = [out["per"][p][k]["se"] for p in out["per"]]
        out["pooled"][k] = L.dl_pool(est, se)
        out["pooled"][k]["n_ci_pos"] = int(sum(out["per"][p][k]["lo"] > 0 for p in out["per"]))
    tabc = tabc.with_columns(pl.format("{}|{}", "agent", "pt_date").alias("cluster"))
    has_chat = np.array([len(x) > 0 for x in chat])
    out["chat"] = {"share_notes_with_chat_terms": float(has_chat.mean())}
    for k in ("r_post", "E_s", "E_x"):
        out["chat"][k] = L.cluster_mean_ci(tabc[k].to_numpy(), tabc["cluster"].to_numpy(), B=300, seed=9)
    tab.drop("cluster").write_parquet(L.DATA / "r3_notes.parquet", compression="zstd")
    return out


def main():
    e = L.load_events()
    refuse_holdout(e["pt_date"].unique().to_list(), "events")
    res = {"n_F": e.filter(pl.col("etype") == "F").height, "n_P": e.filter(pl.col("etype") == "P").height}
    log("R1a")
    res["R1a"] = r1a(e)
    log("R1a pooled diff", res["R1a"]["pooled_diff"])

    log("R1b trail")
    et = L.trail_classes(e)
    per, pooled, _ = per_period(et, "V20", ["T1", "T2"], ["T1xF", "T2xF"])
    fN = L.fit(et, "V20", ["T1", "T2"])
    bN = L.boot_fit(et, "V20", ["T1", "T2"], B, SEED)
    res["R1b"] = {"per": per, "pooled_DL": pooled,
                  "NE41": {"n": fN["n"], "n_F": fN["n_F"], **{k: ci_rr(fN, k, bN) for k in ("T1xF", "T2xF")}},
                  "share_T": {c: float(et[c].mean()) for c in ("T1", "T2")}}
    cost = L.poisson_fe(et["V20"].to_numpy(), np.column_stack([(et["etype"] == "F").to_numpy().astype(float),
                                                              np.log1p(et["V_pre"].to_numpy())]), et["stratum"].to_numpy())
    res["R1b"]["erasure_cost"] = 1 - math.exp(cost[0])
    # by-class erasure cost (descriptive) and recovery time
    rec = {}
    for nm, cond in (("T0", ~pl.col("T1") & ~pl.col("T2")), ("T1", pl.col("T1")), ("T2", pl.col("T2"))):
        s = et.filter(cond)
        b = L.poisson_fe(s["V20"].to_numpy(), np.column_stack([(s["etype"] == "F").to_numpy().astype(float),
                                                              np.log1p(s["V_pre"].to_numpy())]), s["stratum"].to_numpy())
        rec[nm] = {"cost": 1 - math.exp(b[0]), "n": s.height,
                   "first_write_med_F": float(s.filter(pl.col("etype") == "F")["first_write"].median()),
                   "first_write_med_P": float(s.filter(pl.col("etype") == "P")["first_write"].median())}
    res["R1b"]["by_class"] = rec
    # secondary trail: distinct commit days to A_prev in the previous 7 days
    et2 = e.filter(pl.col("A_prev") >= 0).with_columns((pl.col("trail_days7") == 2).alias("D1"),
                                                       (pl.col("trail_days7") >= 3).alias("D2"))
    f2 = L.fit(et2, "V20", ["D1", "D2"])
    b2 = L.boot_fit(et2, "V20", ["D1", "D2"], B, SEED + 3)
    res["R1b"]["secondary_days7"] = {k: ci_rr(f2, k, b2) for k in ("D1xF", "D2xF")}
    log("R1b NE41", res["R1b"]["NE41"])

    log("R2 classes")
    keys = ["LxF", "MxF", "GpxF", "GnxF"]
    per, pooled, _ = per_period(e, "V3", ["L", "M", "Gp", "Gn"], keys)
    fN = L.fit(e, "V3", ["L", "M", "Gp", "Gn"])
    bN = L.boot_fit(e, "V3", ["L", "M", "Gp", "Gn"], B, SEED + 1)
    res["R2"] = {"per": per, "pooled_DL": pooled,
                 "NE41": {"n": fN["n"], "n_F": fN["n_F"], **{k: ci_rr(fN, k, bN) for k in keys}},
                 "prevalence": {c: {"F": float(e.filter(pl.col("etype") == "F")[c].mean()),
                                    "P": float(e.filter(pl.col("etype") == "P")[c].mean())} for c in ("L", "M", "Gp", "Gn")}}
    # scramble by proxy: F events with none of L, M, Gp in calls 1-2
    e_none = e.with_columns((~(pl.col("L") | pl.col("M") | pl.col("Gp"))).alias("NONE"))
    fn = L.fit(e_none, "V3", ["NONE"])
    bn = L.boot_fit(e_none, "V3", ["NONE"], B, SEED + 4)
    res["R2"]["proxy_none"] = {"share_F": float(e_none.filter(pl.col("etype") == "F")["NONE"].mean()),
                               **ci_rr(fn, "NONExF", bn)}
    log("R2 NE41", {k: (round(v["RR"], 3), round(v.get("lo_boot", np.nan), 3), round(v.get("hi_boot", np.nan), 3))
                    for k, v in res["R2"]["NE41"].items() if isinstance(v, dict)})
    log("R2 concentration")
    eu = L.u_classes(e)
    fc = L.fit(eu, "V6", ["U12", "U35"])
    bc = L.boot_fit(eu, "V6", ["U12", "U35"], B, SEED + 2)
    # ratio U12/U35: bootstrap of the difference of log coefficients
    rng = np.random.default_rng(SEED + 5)
    cl = L.codes(eu["cluster"].to_numpy())
    K = cl.max() + 1
    order = np.argsort(cl, kind="stable")
    starts = np.searchsorted(cl[order], np.arange(K))
    ends = np.append(starts[1:], len(cl))
    X, names = L.design(eu, ["U12", "U35"])
    V = eu["V6"].to_numpy().astype(float)
    grp = L.codes(L.fe_groups(eu))
    diffs = []
    for _ in range(B):
        idx = np.concatenate([order[starts[p]:ends[p]] for p in rng.integers(0, K, K)])
        bb = L.poisson_fe(V[idx], X[idx], grp[idx])
        diffs.append(bb[names.index("U12xF")] - bb[names.index("U35xF")])
    diffs = np.array(diffs)
    diffs = diffs[np.isfinite(diffs)]
    dip = fit_dip(eu, "V6", "U12", ("U35",))
    dip["share_ci"] = boot_dip(eu, "V6", "U12", ("U35",), 200, SEED + 6)
    dipL = fit_dip(e, "V3", "L", ("M", "Gp", "Gn"))
    dipM = fit_dip(e, "V3", "M", ("L", "Gp", "Gn"))
    res["R2"]["concentration"] = {"U12xF": ci_rr(fc, "U12xF", bc), "U35xF": ci_rr(fc, "U35xF", bc),
                                  "ratio": L.rr(fc["U12xF"]["b"] - fc["U35xF"]["b"]),
                                  "ratio_ci": [L.rr(np.percentile(diffs, 2.5)), L.rr(np.percentile(diffs, 97.5))],
                                  "dip_share_U12": dip, "dip_share_L": dipL, "dip_share_M": dipM,
                                  "share_U12_F": float(eu.filter(pl.col("etype") == "F")["U12"].mean()),
                                  "share_U35_F": float(eu.filter(pl.col("etype") == "F")["U35"].mean())}
    log("R2 conc", res["R2"]["concentration"]["ratio"], res["R2"]["concentration"]["ratio_ci"], dip)

    log("R1c")
    res["R1c"] = r1c()
    log("R1c", res["R1c"])
    log("R3")
    res["R3"] = r3()
    log("R3 pooled", {k: (round(v["est"], 4), round(v["lo"], 4), round(v["hi"], 4)) for k, v in res["R3"]["pooled"].items()})
    (L.DATA / "results.json").write_text(json.dumps(res, indent=1, default=float))
    log("written")


if __name__ == "__main__":
    main()
