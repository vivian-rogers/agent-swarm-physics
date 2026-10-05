"""H74 round 2, R1 + R3 on real data (card: Round 2 and Amendment R2-A1). Non-reserved days only.

Precision monitor = S (shared schema diff) ∪ D3 (operator counters, log + Gaussian z, two-day persistence) ∪ C (H36's
frozen C3, bge-small restate, read as data). S and D3 use leave-one-period-out conformal thresholds (alpha 0.02) on
the P2 placebo days (>= 2 active days from every catalogued event), so every reported FAR is out-of-sample.
Also: pre-registered D variants (G, L, Q; six features, one day), the NE39/NE43 readouts, round 1's fused alarm on the
same pools, rival C3 alone, the seed spread of C3 over H36's nine bge surrogate seeds, the intraday C variant, and
M/O with quantile baselines as candidate add-ons.
Run: uv run python hypotheses/H74-change-detector/analysis/r2_monitor.py
Outputs: data/processed/H74-change-detector/r2/{monitor.json, monitor_days.parquet}
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h74lib as L  # noqa: E402
import r2lib as R  # noqa: E402
from r2_common import CLASSES, H36, LABEL_MAP, OUT, OUT1, PLATFORM_POOL, ROOT, SH, d_raw, load_frame  # noqa: E402

sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit  # noqa: E402

NAMED = {"NE39": "2025-07-01", "OUT0331": "2026-03-31", "NE40": "2026-04-20", "NE45": "2026-07-29",
         "NE43a": "2026-08-05", "NE43b": "2026-08-21", "NE14": "2026-03-24"}
M_LOGIT = [f for f in L.M_FEATURES if f.startswith("sh_") or f.endswith("_share")]


def on_days(fr, df: pl.DataFrame, col: str) -> np.ndarray:
    return pl.DataFrame({"pt_date": fr.dl}).join(df.select("pt_date", col), on="pt_date", how="left")[col] \
        .cast(pl.Float64).fill_null(np.nan).fill_nan(np.nan).to_numpy()


def c3_from(fr, path: Path) -> np.ndarray:
    return on_days(fr, pl.read_parquet(path / "scores.parquet"), "C3")


def window_max(fr, x, d):
    i = fr.day_pos.get(d)
    if i is None:
        return None
    v = x[fr.nbr[i]]
    v = v[np.isfinite(v)]
    return float(v.max()) if v.size else None


def score_MQ(fr) -> tuple[np.ndarray, list]:
    agd = pl.read_parquet(OUT1 / "agent_day_features.parquet")
    T = fr.T
    per = {f: [[] for _ in range(T)] for f in L.M_FEATURES}
    for (a,), g in agd.sort("pt_date").group_by("agent", maintain_order=True):
        idx = np.array([fr.day_pos[d] for d in g["pt_date"].to_list()])
        for f in L.M_FEATURES:
            x = g[f].cast(pl.Float64).fill_null(np.nan).fill_nan(np.nan).to_numpy()
            if f in M_LOGIT:
                p = np.clip(x, 1e-3, 1 - 1e-3)
                x = np.log(p / (1 - p))
            e = R.quant_e(x, 0.05)
            for t, v in zip(idx, e):
                if np.isfinite(v):
                    per[f][t].append(v)
    med = {f: np.abs(np.array([np.median(v) if len(v) >= 3 else np.nan for v in per[f]])) for f in L.M_FEATURES}
    return R.nanmax_stack(med)


def score_OQ(fr) -> tuple[np.ndarray, list]:
    sd = pl.read_parquet(OUT1 / "search_daily.parquet").filter(pl.col("n_search") >= 3)
    out = {}
    for f in L.O_FEATURES:
        x = on_days(fr, sd, f)
        out[f] = np.abs(R.quant_e(x, L.FLOOR.get(f, 1.0)))
    return R.nanmax_stack(out)


def summarize(fr, alarm, rng, n_rand=2000):
    return {"far": fr.far(alarm), "classes": fr.class_hits(alarm, CLASSES, rng, n_rand, LABEL_MAP),
            "pooled_platform": fr.class_hits(alarm, ["pool"], rng, n_rand, {"pool": PLATFORM_POOL})["pool"]}


def compact(s):
    c = {k: (v["k"], v["n"], round(v["hit"], 2), round(v.get("p_rand", np.nan), 3)) for k, v in s["classes"].items()}
    p = s["pooled_platform"]
    return {"FAR_P2": (s["far"]["P2"]["k"], s["far"]["P2"]["n"], round(s["far"]["P2"]["per_day"], 3)),
            "FAR_P3_win": round(s["far"]["P3"]["window"], 3), "alarm_days": s["far"]["n_alarm_days"],
            "pool": (p["k"], p["n"], round(p["hit"], 2), round(p["p_rand"], 3)), **c}


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", choices=["prereg", "ext"], default="prereg",
                    help="prereg: round-1 catalog (pre-registered); ext: + round-1 provider format changes (post hoc)")
    cat = ap.parse_args().catalog
    sfx = "" if cat == "prereg" else "_ext"
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20261005)
    fr = load_frame(cat)
    P2, per = fr.P2, fr.period
    raw = d_raw(fr)
    res = {"n_days": fr.T, "n_P2": int(P2.sum()), "n_P3": int(fr.P3.sum()),
           "P2_monday": int((P2 & fr.monday).sum())}

    # ---------------- channels
    zS = on_days(fr, pl.read_parquet(SH / "schema_diff/schema_diff_daily.parquet"), "z_S")
    aS, thS = R.lopo_alarm(zS, per, P2)
    D3, argD3, psD3 = R.d3_channel(raw)
    aD, thD = R.lopo_alarm(D3, per, P2)
    c3 = c3_from(fr, H36 / "rob_bge_restate")
    aC = np.where(np.isfinite(c3), c3 >= 2.0, False)
    mon = aS | aD | aC
    res["thresholds"] = {"S": sorted(set(np.round(thS, 3).tolist())), "D3": sorted(set(np.round(thD, 3).tolist()))}
    res["channels"] = {nm: summarize(fr, a, rng) for nm, a in (("S", aS), ("D3", aD), ("C3", aC))}
    res["monitor"] = summarize(fr, mon, rng)

    # ---------------- round 1 fused alarm on the same pools; rival C3 alone is res["channels"]["C3"]
    r1 = pl.read_parquet(OUT1 / "scores.parquet")
    zF = on_days(fr, r1, "z_F")
    res["round1_fused"] = summarize(fr, np.where(np.isfinite(zF), zF >= 4, False), rng)
    # matched-FAR comparison: round-1 fused with a LOPO threshold
    aF2, _ = R.lopo_alarm(zF, per, P2)
    res["round1_fused_lopo"] = summarize(fr, aF2, rng)

    # ---------------- C variants: seeds, gte, recalibrated C3, intraday
    seeds = {}
    for p in sorted(H36.glob("rob_bge_restate*")):
        c = c3_from(fr, p)
        a = np.where(np.isfinite(c), c >= 2.0, False)
        s = summarize(fr, aS | aD | a, rng, n_rand=500)
        seeds[p.name] = {"far_P2": s["far"]["P2"]["per_day"], "goal_hit": s["classes"]["goal"]["hit"],
                         "pool_hit": s["pooled_platform"]["hit"], "C3_far_P2": fr.far(a)["P2"]["per_day"],
                         "C3_goal_hit": fr.class_hits(a, ["goal"])["goal"]["hit"]}
    res["seed_spread_bge"] = seeds
    cg = c3_from(fr, H36 / "rob_gte_restate")
    aCg = np.where(np.isfinite(cg), cg >= 2.0, False)
    res["monitor_gte"] = summarize(fr, aS | aD | aCg, rng)
    aCr, thC = R.lopo_alarm(c3, per, P2)
    res["monitor_C3_lopo"] = summarize(fr, aS | aD | aCr, rng)
    res["thresholds"]["C3_lopo"] = sorted(set(np.round(thC, 3).tolist()))
    intr = pl.read_parquet(H36 / "intraday_bge.parquet").filter(pl.col("win30") <= 1).group_by("pt_date") \
        .agg(pl.col("z").fill_nan(None).max().alias("zi"))
    zi = on_days(fr, intr, "zi")
    aI, thI = R.lopo_alarm(zi, per, P2)
    res["thresholds"]["intraday_lopo"] = sorted(set(np.round(thI, 3).tolist()))
    res["intraday_frozen"] = summarize(fr, np.where(np.isfinite(zi), zi >= 3, False), rng)
    res["intraday_lopo"] = summarize(fr, aI, rng)
    res["monitor_intraday"] = summarize(fr, aS | aD | aI, rng)
    res["monitor_C3_or_intraday"] = summarize(fr, mon | aI, rng)

    # ---------------- R3: D variants (pre-registered and amendment candidates)
    var = {}
    for kind, fset, persist in (("G", R.D2_FEATURES, False), ("L", R.D2_FEATURES, False), ("Q", R.D2_FEATURES, False),
                                ("Q", R.D3_FEATURES, False), ("Q", R.D2_FEATURES, True), ("Q", R.D3_FEATURES, True),
                                ("L", R.D3_FEATURES, True), ("G", R.D3_FEATURES, True)):
        name = kind + ("_D6" if len(fset) == 6 else "_D3") + ("_p2" if persist else "")
        fs = R.feature_scores({f: raw[f] for f in fset}, kind, floors_g=L.FLOOR)
        if persist:
            fs = {f: R.persist2(v) for f, v in fs.items()}
        Dv, _ = R.nanmax_stack(fs)
        a, th = R.lopo_alarm(Dv, per, P2)
        nominal = np.where(np.isfinite(Dv), Dv >= 4, False)
        s = summarize(fr, a, rng, n_rand=500)
        var[name] = {"P2_exceed_nominal4": float(nominal[P2].mean()), "lopo_threshold_median": float(np.median(th[np.isfinite(th)])) if np.isfinite(th).any() else None,
                     "far_P2": s["far"]["P2"]["per_day"], "drive_hit": s["classes"]["drive"]["hit"],
                     "undoc_hit": s["classes"]["undocumented"]["hit"],
                     "features": {f: {"P2_exceed_nominal4": float(np.nanmean(np.where(np.isfinite(v), v >= 4, False)[P2])),
                                      "P2_max": float(np.nanmax(v[P2])) if np.isfinite(v[P2]).any() else None}
                                  for f, v in fs.items()},
                     "named": {}}
        for ne, d in NAMED.items():
            i = fr.day_pos.get(d)
            if i is None:
                continue
            th_i = th[i]
            var[name]["named"][ne] = {"window_max": window_max(fr, Dv, d), "threshold": float(th_i),
                                      "alarm": bool(fr.window_any(a)[i]),
                                      "n_human_window_max": window_max(fr, fs["n_human"], d) if "n_human" in fs else None}
    res["R3_variants"] = var
    # NE39 raw context: n_human on days -3..+3
    i39 = fr.day_pos["2025-07-01"]
    res["NE39_n_human"] = {fr.dl[j]: raw["n_human"][j] for j in range(i39 - 5, i39 + 4)}

    # stall/schedule flag (descriptive, Q nominal)
    st = R.feature_scores({f: raw[f] for f in R.STALL_FEATURES}, "Q")
    stall, stall_arg = R.nanmax_stack(st)
    stall_a = np.where(np.isfinite(stall), stall >= 4, False)
    res["stall_flag"] = {"far": fr.far(stall_a), "days": [(fr.dl[j], stall_arg[j], round(float(stall[j]), 1))
                                                          for j in np.where(stall_a)[0]]}

    # ---------------- secondary: M and O with quantile baselines as add-ons
    MQ, argM = score_MQ(fr)
    OQ, argO = score_OQ(fr)
    aM, _ = R.lopo_alarm(MQ, per, P2)
    aO, _ = R.lopo_alarm(OQ, per, P2)
    res["M_Q"] = summarize(fr, aM, rng, n_rand=500)
    res["O_Q"] = summarize(fr, aO, rng, n_rand=500)
    res["monitor_plus_M"] = summarize(fr, mon | aM, rng, n_rand=500)
    res["monitor_plus_O"] = summarize(fr, mon | aO, rng, n_rand=500)
    res["M_Q_P2_exceed_nominal4"] = float(np.nanmean(np.where(np.isfinite(MQ), MQ >= 4, False)[P2]))
    res["O_Q_P2_exceed_nominal4"] = float(np.nanmean(np.where(np.isfinite(OQ), OQ >= 4, False)[P2 & np.isfinite(OQ)]))

    # ---------------- named events, per channel
    res["named"] = {ne: {"S": window_max(fr, zS, d), "S_alarm": bool(fr.window_any(aS)[fr.day_pos[d]]),
                         "D3": window_max(fr, D3, d), "D3_alarm": bool(fr.window_any(aD)[fr.day_pos[d]]),
                         "D3_threshold": float(thD[fr.day_pos[d]]),
                         "C3": window_max(fr, c3, d), "C3_alarm": bool(fr.window_any(aC)[fr.day_pos[d]]),
                         "monitor": bool(fr.window_any(mon)[fr.day_pos[d]])}
                    for ne, d in NAMED.items() if d in fr.day_pos}

    # ---------------- unexplained monitor alarms (no catalogued event within +-1 day)
    rows = []
    for j in np.where(mon)[0]:
        rows.append({"pt_date": fr.dl[j], "goal_no": int(per[j]), "S": bool(aS[j]), "D3": bool(aD[j]), "C3": bool(aC[j]),
                     "D3_feature": argD3[j] if aD[j] else None, "explained": bool(fr.dist[j] <= 1), "P2": bool(P2[j])})
    res["alarm_days"] = rows

    # ---------------- day table
    tab = fr.days.select("pt_date", "goal_no", "regime", "weekday").with_columns(
        pl.Series("P2", P2), pl.Series("P3", fr.P3), pl.Series("dist_event", fr.dist),
        pl.Series("z_S", zS), pl.Series("th_S", thS), pl.Series("alarm_S", aS),
        pl.Series("D3", D3), pl.Series("th_D3", thD), pl.Series("alarm_D3", aD),
        pl.Series("D3_feature", argD3), pl.Series("C3", c3), pl.Series("alarm_C3", aC),
        pl.Series("C3_gte", cg), pl.Series("intraday_z01", zi), pl.Series("th_intraday", thI),
        pl.Series("alarm_monitor", mon), pl.Series("stall_Q", stall), pl.Series("M_Q", MQ), pl.Series("O_Q", OQ))
    tab.write_parquet(OUT / f"monitor_days{sfx}.parquet")
    res["catalog"] = cat
    (OUT / f"monitor{sfx}.json").write_text(json.dumps(res, indent=1, default=float))
    prov_p = OUT / "_provenance.json"
    prov = json.loads(prov_p.read_text()) if prov_p.exists() else {}
    prov["r2_monitor" + sfx] = {"built_by": "hypotheses/H74-change-detector/analysis/r2_monitor.py", "git_commit": git_commit(),
                          "inputs": [{"source": "ai-village", "revision": REVISION,
                                      "tables": ["H74 days/day_features/agent_day_features/search_daily/events/scores",
                                                 "shared/schema_diff/schema_diff_daily", "shared/calendar",
                                                 "H36-reorganization-alarm/r2/rob_*_restate*/scores.parquet (data)",
                                                 "H36-reorganization-alarm/r2/intraday_bge.parquet (data)"]}],
                          "params": {"alpha": R.ALPHA, "placebo": "P2: >= 2 active days from every catalogued event",
                                     "calibration": "leave-one-goal-period-out conformal", "non_reserved_only": True},
                          "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    prov_p.write_text(json.dumps(prov, indent=1))

    # ---------------- print
    print("P2", res["n_P2"], "P3", res["n_P3"])
    print("thresholds", {k: v[:6] for k, v in res["thresholds"].items()})
    for k in ("monitor", "round1_fused", "round1_fused_lopo", "monitor_gte", "monitor_C3_lopo", "intraday_frozen",
              "intraday_lopo", "monitor_intraday", "monitor_C3_or_intraday", "M_Q", "O_Q", "monitor_plus_M", "monitor_plus_O"):
        print(k, compact(res[k]))
    for k, v in res["channels"].items():
        print("ch", k, compact(v))
    print("seeds", {k: (round(v["far_P2"], 3), round(v["goal_hit"], 2), round(v["pool_hit"], 2)) for k, v in seeds.items()})
    for k, v in var.items():
        print("R3", k, round(v["P2_exceed_nominal4"], 3), v["lopo_threshold_median"], round(v["far_P2"], 3),
              round(v["drive_hit"], 2), round(v["undoc_hit"], 2),
              {n: (round(x["window_max"], 1) if x["window_max"] is not None else None, x["alarm"]) for n, x in v["named"].items()})
    print("NE39 n_human", res["NE39_n_human"])
    print("named", json.dumps(res["named"]))
    print("stall", res["stall_flag"]["far"]["P2"], len(res["stall_flag"]["days"]))
    print("unexplained", [r for r in rows if not r["explained"]])


if __name__ == "__main__":
    main()
