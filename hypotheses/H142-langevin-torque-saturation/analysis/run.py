"""H142 round 1 on exploration data: O1-O5 per period and model, the replication layer (P1-P4, the kill), the natives
(N1 #51 timer wakes, N2 NE42) and the within-hour permutation null (N2-null, card "Null / baseline").

Eligibility (fixed before any outcome; card "Two layers" and Round 1 structural count):
  identified  H113's field-identified periods (bge #13 #36 #37 #38 #39 #51; gte #13 #16 #35 #36 #37 #38 #51);
  rows        >= 200 call-direction rows with n_u >= 4 (counts.json, structural);
  powered     synthetic W-L3 pass rate >= 0.8 on the period's own skeleton (summary_power/main.json).
A period that is identified, has the rows and is powered is 'scored'; any other period is descriptive.

Usage: uv run python hypotheses/H142-langevin-torque-saturation/analysis/run.py [--perms 50] [--only 38]
Output: data/processed/H142-langevin-torque-saturation/results/{periods.json, pooled.json, natives.json, nulls.json}
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h142lib as L  # noqa: E402

ROOT = HERE.parents[2]
DATA = ROOT / "data/processed/H142-langevin-torque-saturation"
RES = DATA / "results"
MODELS = ("bge_small", "gte_modernbert")
IDENT = {"bge_small": {13, 36, 37, 38, 39, 51}, "gte_modernbert": {13, 16, 35, 36, 37, 38, 51}}
MIN_ROWS = 200
POWER_MIN = 0.8
LN15 = math.log(1.5)


def power_table() -> dict:
    out = {}
    for f in ("summary_main.json", "summary_power.json"):
        p = DATA / "synthetic" / f
        if not p.exists():
            continue
        for k, v in json.loads(p.read_text()).items():
            g, tag, w = k.split("|")
            if w == "W-L3":
                out[(int(g[1:]), tag)] = v["prefer_L_over_lin"]
    return out


def clean(o):
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items() if not k.startswith("_") and k not in ("boot", "theta_boot", "ln_nsat_boot")}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, float) and not math.isfinite(o):
        return None
    return o


def analyse(rows: pl.DataFrame, seed: int, pooled_variant: bool = True) -> tuple[dict, dict]:
    D = L.Design(rows)
    st = D.y_stats(rows["y"].to_numpy().astype(float))
    ll = L.oof_loglik(D, st)
    res = {"n_rows": len(rows), "n_ge4": int((rows["n"] >= 4).sum()), "n_days": int(D.n_day), "n_clusters": int(D.n_cl),
           "n_max_50": None}
    vals, cnt = np.unique(rows["n"].to_numpy(), return_counts=True)
    res["n_max_50"] = int(vals[cnt >= 50].max()) if (cnt >= 50).any() else 0
    boots = {}
    for a, b in (("langevin", "linear"), ("langevin", "power"), ("power", "linear"), ("dummies", "linear"), ("langevin", "dummies")):
        dd = L.dll_summary(ll, a, b, B=1000, seed=seed)
        res[f"dll_{a}_{b}"] = dd
        boots[f"dll_{a}_{b}"] = dd["boot"]
    res["oof_theta_langevin_median"] = float(np.median(ll["theta"]["langevin"])) if ll["theta"]["langevin"] else None
    fd = L.fit_dummies(D, st, B=300, seed=seed)
    fp = L.fit_profiles(D, st, B=300, seed=seed)
    res["dummies"] = fd; res["profiles"] = fp
    boots["fboot"] = fd["_fboot"]; boots["ln_nsat"] = fp["langevin"].get("ln_nsat_boot")
    if pooled_variant:
        Dp = L.Design(rows, amplitude="pooled")
        stp = Dp.y_stats(rows["y"].to_numpy().astype(float))
        llp = L.oof_loglik(Dp, stp)
        res["pooled_amplitude"] = {"dll_langevin_linear": L.dll_summary(llp, "langevin", "linear", B=1000, seed=seed),
                                   "dll_langevin_power": L.dll_summary(llp, "langevin", "power", B=1000, seed=seed),
                                   "nsat": L.fit_profiles(Dp, stp, boot=False)["langevin"]["nsat"]}
    return res, boots


def verdict(res: dict, scored: bool) -> dict:
    """P1-P4 and the kill on one unit (card rules applied literally)."""
    d = res["dll_langevin_linear"]; fd = res["dummies"]; fp = res["profiles"]
    dc = fd["dcurv"]; r63 = fd.get("ratio63") or {}
    P1 = d["lo"] > 0
    P2 = bool(dc.get("lo") is not None and dc["lo"] > 0)
    ns = fp["langevin"]["nsat"]
    P3 = bool(1.5 <= ns <= 6 and fp["langevin"].get("edge_share", 1) < 0.5)
    inf = fd.get("inflight")
    P4 = bool(inf and inf["ratio"] is not None and inf["ratio"] <= 0.5 and inf["contrast_lo"] > 0)
    lin_a = bool(r63 and r63.get("lo") is not None and r63["lo"] <= 2 <= r63["hi"]
                 and (dc.get("lo") is None or dc["lo"] <= 0 <= dc["hi"]))
    lin_b = d["lo"] <= 0
    kill = (lin_a or lin_b) and scored
    narrowed = P1 and not P2 and res["dll_power_linear"]["lo"] > 0
    if not scored:
        v = "descriptive"
    elif kill:
        v = "failed"
    elif P1 and P2:
        v = "supported"
    elif narrowed:
        v = "narrowed"
    else:
        v = "inconclusive"
    return {"P1": bool(P1), "P2": P2, "P3": P3, "P4": P4, "kill_linear_curve": bool(lin_a), "kill_line_as_good": bool(lin_b),
            "kill": bool(kill), "narrowed": bool(narrowed), "verdict": v}


def perm_null(rows: pl.DataFrame, perms: int, seed: int) -> dict:
    """N2-null: permute each call's aligned-count vector across calls of the same room and hour (keeps the field,
    breaks the link to the reader's step); ΔLL(L - lin) and the dummies curve under the null."""
    rng = np.random.default_rng(seed)
    K = int(rows["u"].max()) + 1
    calls = rows.filter(pl.col("u") == 0).select("call", "room", "hour").with_row_index("ci")
    grp = calls.group_by(["room", "hour"], maintain_order=True).agg(pl.col("ci"))
    cols = ["n", "nF", "newest", "nname", "k"]
    mats = {c: rows[c].to_numpy().reshape(-1, K) for c in cols}
    out = []
    for _ in range(perms):
        perm = np.arange(len(calls))
        for ids in grp["ci"].to_list():
            ids = np.asarray(ids)
            if len(ids) > 1:
                perm[ids] = rng.permutation(ids)
        r2 = rows.with_columns([pl.Series(c, mats[c][perm].ravel()) for c in cols])
        D = L.Design(r2)
        st = D.y_stats(r2["y"].to_numpy().astype(float))
        ll = L.oof_loglik(D, st)
        fd = L.fit_dummies(D, st, B=50, seed=seed)
        out.append({"dll_L_lin": L.dll_summary(ll, "langevin", "linear", B=200)["dll"],
                    **{f"f_{k}": v["est"] for k, v in fd["f"].items()}})
    df = pl.DataFrame(out)
    return {"perms": perms, **{f"{c}_q": [float(df[c].quantile(q)) for q in (0.025, 0.5, 0.975)] for c in df.columns}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perms", type=int, default=50)
    ap.add_argument("--only", type=int, action="append")
    a = ap.parse_args()
    RES.mkdir(parents=True, exist_ok=True)
    pw = power_table()
    periods = sorted(int(p.name[1:]) for p in DATA.glob("G*") if p.is_dir())
    if a.only:
        periods = [g for g in periods if g in a.only]
    per, natives, nulls = {}, {}, {}
    boots_all = {}
    pu = pl.read_parquet(ROOT / "data/processed/shared/period_units.parquet")
    for g in periods:
        d = DATA / f"G{g:02d}"
        cnt = json.loads((d / "counts.json").read_text())
        n_units = int((pu["goal_no"] == g).sum())
        per[g] = {"goal_no": g, "period_unit": str(g) if n_units == 1 else f"G{g:02d}"}
        for m in MODELS:
            t0 = time.time()
            rows = pl.read_parquet(d / f"rows_{m}.parquet")
            ident = g in IDENT[m]; enough = cnt[m]["n_ge4"] >= MIN_ROWS
            power = pw.get((g, m)); powered = power is not None and power >= POWER_MIN
            scored = ident and enough and powered
            res, boots = analyse(rows, seed=1000 * g + (0 if m == "bge_small" else 1))
            res.update({"identified_H113": ident, "rows_ge200": enough, "power_WL3": power, "powered": powered, "scored": scored})
            res["rules"] = verdict(res, scored)
            # sensitivities (bge, eligible periods): K = 12 directions; responses not flagged as copies
            if m == "bge_small" and enough and ident:
                r12 = pl.read_parquet(d / "rows_bge_small_K12.parquet").join(
                    rows.select("call", "agent", "pt_date", "room", "hour", "k").unique("call"), on="call")
                s12, _ = analyse(r12, seed=7 + g, pooled_variant=False)
                res["sens_K12"] = {"dll_langevin_linear": s12["dll_langevin_linear"], "dcurv": s12["dummies"]["dcurv"],
                                   "nsat": s12["profiles"]["langevin"]["nsat"]}
                rf = rows.filter(~(pl.col("f_self") | pl.col("f_echo") | pl.col("f_templ")))
                sf, _ = analyse(rf, seed=9 + g, pooled_variant=False)
                res["sens_noflag"] = {"n_rows": len(rf), "dll_langevin_linear": sf["dll_langevin_linear"],
                                      "dcurv": sf["dummies"]["dcurv"], "nsat": sf["profiles"]["langevin"]["nsat"]}
                if a.perms:
                    nulls[f"G{g}|{m}"] = perm_null(rows, a.perms if g != 51 else max(a.perms // 2, 20), seed=g)
            per[g][m] = res
            boots_all[(g, m)] = boots
            print(f"G{g} {m}: rows {len(rows)} n>=4 {res['n_ge4']} scored {scored} dll(L-lin) {res['dll_langevin_linear']['dll']:.1f} "
                  f"[{res['dll_langevin_linear']['lo']:.1f}, {res['dll_langevin_linear']['hi']:.1f}] nsat {res['profiles']['langevin']['nsat']:.2f} "
                  f"verdict {res['rules']['verdict']} {time.time() - t0:.0f}s", flush=True)
            (RES / "periods.json").write_text(json.dumps(clean({f"G{k}": v for k, v in per.items()}), indent=1))
        # natives: #51 timer wakes (N1)
        if g == 51:
            for m in MODELS:
                rows = pl.read_parquet(d / f"rows_wake_{m}.parquet")
                res, boots = analyse(rows, seed=5100 + (0 if m == "bge_small" else 1))
                power = pw.get((51, f"wake_{m}"))
                res["power_WL3"] = power
                ln_t = per[51][m]["profiles"]["langevin"]["nsat"]; ln_w = res["profiles"]["langevin"]["nsat"]
                lb_t = boots_all[(51, m)]["ln_nsat"]; lb_w = boots["ln_nsat"]
                dl = lb_w - lb_t
                res["N1"] = {"dll_ci_gt0": res["dll_langevin_linear"]["lo"] > 0,
                             "nsat_ratio_wake_talk": ln_w / ln_t, "ln_ratio_lo": float(np.percentile(dl, 2.5)),
                             "ln_ratio_hi": float(np.percentile(dl, 97.5)),
                             "within_x1_5": abs(math.log(ln_w / ln_t)) < LN15}
                res["N1"]["pass"] = bool(res["N1"]["dll_ci_gt0"] and res["N1"]["within_x1_5"])
                natives[f"G51_wakes|{m}"] = res
                print(f"G51 wakes {m}: dll {res['dll_langevin_linear']['dll']:.1f} [{res['dll_langevin_linear']['lo']:.1f}, "
                      f"{res['dll_langevin_linear']['hi']:.1f}] nsat {ln_w:.2f} (talk {ln_t:.2f})", flush=True)
    # NE42 (N2): n_sat across #39 -> #40 -> #41
    for m in MODELS:
        if all((g, m) in boots_all for g in (39, 40, 41)):
            ne = {}
            for a_, b_ in ((39, 40), (40, 41)):
                la = per[a_][m]["profiles"]["langevin"]["nsat"]; lb = per[b_][m]["profiles"]["langevin"]["nsat"]
                db = boots_all[(b_, m)]["ln_nsat"] - boots_all[(a_, m)]["ln_nsat"]
                lo, hi = float(np.percentile(db, 2.5)), float(np.percentile(db, 97.5))
                dln = math.log(lb / la)
                ne[f"{a_}->{b_}"] = {"nsat_before": la, "nsat_after": lb, "dln": dln, "lo": lo, "hi": hi,
                                     "within_ln1_5": abs(dln) < LN15, "against": abs(dln) >= LN15 and (lo > 0 or hi < 0)}
            ne["k_mean"] = {str(g): float(pl.read_parquet(DATA / f"G{g:02d}" / f"calls_{m}.parquet")["k"].mean()) for g in (39, 40, 41)}
            ne["identified_40"] = 40 in IDENT[m]
            natives[f"NE42|{m}"] = ne
    # pooled (exception (d)): scored periods per model
    pooled = {}
    for m in MODELS:
        sc = [g for g in per if per[g][m]["scored"]]
        idn = [g for g in per if per[g][m]["identified_H113"]]
        out = {"scored_periods": sc, "identified_periods": idn}
        for setname, gs in (("scored", sc), ("identified_all", idn)):
            if not gs:
                continue
            o = {}
            bs = sum(boots_all[(g, m)]["dll_langevin_linear"] for g in gs)
            tot = sum(per[g][m]["dll_langevin_linear"]["dll"] for g in gs)
            o["dll_langevin_linear"] = {"dll": tot, "lo": float(np.percentile(bs, 2.5)), "hi": float(np.percentile(bs, 97.5)),
                                        "n_pos": sum(per[g][m]["dll_langevin_linear"]["dll"] > 0 for g in gs), "k": len(gs)}
            bs = sum(boots_all[(g, m)]["dll_langevin_power"] for g in gs)
            o["dll_langevin_power"] = {"dll": sum(per[g][m]["dll_langevin_power"]["dll"] for g in gs),
                                       "lo": float(np.percentile(bs, 2.5)), "hi": float(np.percentile(bs, 97.5))}
            bs = sum(boots_all[(g, m)]["dll_power_linear"] for g in gs)
            o["dll_power_linear"] = {"dll": sum(per[g][m]["dll_power_linear"]["dll"] for g in gs),
                                     "lo": float(np.percentile(bs, 2.5)), "hi": float(np.percentile(bs, 97.5))}
            # random-effects pooled step curve and the curvature contrast from it
            fpool, fdraw = {}, {}
            for nm in L.BIN_NAMES:
                have = [g for g in gs if nm in per[g][m]["dummies"]["f"]]
                if not have:
                    continue
                est = [per[g][m]["dummies"]["f"][nm]["est"] for g in have]; se = [per[g][m]["dummies"]["f"][nm]["se"] for g in have]
                rp = L.re_pool(est, se)
                fpool[nm] = rp
                w = 1 / (np.asarray(se) ** 2 + (rp["tau2"] or 0)); w = w / w.sum()
                fdraw[nm] = sum(wi * boots_all[(g, m)]["fboot"][nm] for wi, g in zip(w, have))
            o["f_pooled"] = fpool
            if all(x in fdraw for x in ("n1", "n2", "n3", "n6p")):
                with np.errstate(divide="ignore", invalid="ignore"):
                    dcb = np.log(fdraw["n2"] / fdraw["n1"]) - np.log(fdraw["n6p"] / fdraw["n3"])
                    r63 = fdraw["n6p"] / fdraw["n3"]
                valid = np.isfinite(dcb)
                f_ = {k: fpool[k]["est"] for k in ("n1", "n2", "n3", "n6p")}
                est = math.log(f_["n2"] / f_["n1"]) - math.log(f_["n6p"] / f_["n3"]) if min(f_.values()) > 0 else None
                o["dcurv"] = {"est": est, "lo": float(np.percentile(dcb[valid], 2.5)) if valid.mean() >= 0.5 else None,
                              "hi": float(np.percentile(dcb[valid], 97.5)) if valid.mean() >= 0.5 else None,
                              "valid_share": float(valid.mean())}
                o["ratio63"] = {"est": f_["n6p"] / f_["n3"] if f_["n3"] else None, "lo": float(np.nanpercentile(r63, 2.5)),
                                "hi": float(np.nanpercentile(r63, 97.5))}
            # ln n_sat RE pool
            lns = [math.log(per[g][m]["profiles"]["langevin"]["nsat"]) for g in gs]
            ses = [float(np.std(boots_all[(g, m)]["ln_nsat"])) for g in gs]
            rp = L.re_pool(lns, ses)
            o["nsat_pooled"] = {k: (math.exp(v) if k in ("est", "lo", "hi") and v is not None else v) for k, v in rp.items()}
            # P4 pooled: g(1) and f(1), contrast
            hv = [g for g in gs if per[g][m]["dummies"].get("inflight")]
            if hv:
                ci = [per[g][m]["dummies"]["inflight"] for g in hv]
                f1 = L.re_pool([per[g][m]["dummies"]["f"]["n1"]["est"] for g in hv], [per[g][m]["dummies"]["f"]["n1"]["se"] for g in hv])
                g1 = L.re_pool([c["g1"] for c in ci], [(c["g1_hi"] - c["g1_lo"]) / 3.92 for c in ci])
                cc = L.re_pool([c["contrast"] for c in ci], [(c["contrast_hi"] - c["contrast_lo"]) / 3.92 for c in ci])
                o["inflight"] = {"f1": f1, "g1": g1, "ratio": g1["est"] / f1["est"] if f1["est"] else None, "contrast": cc}
            out[setname] = o
        pooled[m] = out
    (RES / "periods.json").write_text(json.dumps(clean({f"G{k}": v for k, v in per.items()}), indent=1))
    (RES / "natives.json").write_text(json.dumps(clean(natives), indent=1))
    (RES / "pooled.json").write_text(json.dumps(clean(pooled), indent=1))
    (RES / "nulls.json").write_text(json.dumps(clean(nulls), indent=1))
    print(json.dumps(clean(pooled), indent=1)[:6000])


if __name__ == "__main__":
    main()
