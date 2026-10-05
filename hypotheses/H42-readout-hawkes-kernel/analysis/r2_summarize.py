"""H42 round 2: pools, prediction scoring, estimates rows and per-period numbers for R2 / R1 (call level) and R3 (Cox
field Hawkes).

Inputs: round2/r2_units.parquet (r2_run.py), round2/r3/*.json (r3_run.py), round-1 posthoc_mention.parquet (round-1
named kernel, for the reproduction check), synthetic summaries.
Outputs: round2/r2_pools.parquet, r2_periods.parquet, r3_units.parquet, r3_periods.parquet, summary.json; rows in
per_period_estimates (with --write-estimates).
Usage: uv run python hypotheses/H42-readout-hawkes-kernel/analysis/r2_summarize.py [--write-estimates]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import r2lib as L  # noqa: E402

ROOT = HERE.parents[2]
R2 = L.R2
MIN_READS = 20
H67_NAMED = (0.079, 0.069, 0.089)
COX_ATTEN = 0.75          # synthetic: Cox-field n_x / truth in the planted read-out world (Amendment R2-A)
COX_REF_SURV = 0.67       # synthetic: survival of a real read-out kernel


# ============================================================================================ R2 / R1
def long_r2(d: pl.DataFrame) -> pl.DataFrame:
    rows = []
    for X in ("named", "un", "cold", "thrn"):
        if f"J_{X}" not in d.columns:
            continue
        x = d.filter(pl.col(f"J_{X}").is_not_null() & pl.col(f"J_{X}").is_not_nan() & (pl.col(f"se_{X}") > 1e-6)
                     & (pl.col(f"nRm_{X}") >= MIN_READS))
        rows.append(x.select(
            "unit_id", "goal_no", "regime", "outcome", "spec", "field", "n", "ybar", pl.lit(X).alias("X"),
            pl.col(f"J_{X}").alias("J"), pl.col(f"se_{X}").alias("se"), pl.col(f"lo_{X}").alias("lo"),
            pl.col(f"hi_{X}").alias("hi"), pl.col(f"nRm_{X}").alias("nRm"),
            pl.col(f"null_mean_{X}").fill_null(0.0).alias("null_mean"),
            pl.col(f"null_sd_{X}").fill_null(0.0).alias("null_sd")))
    z = pl.concat(rows)
    return z.with_columns((pl.col("J") - pl.col("null_mean")).alias("ex"),
                          (pl.col("se") ** 2 + pl.col("null_sd") ** 2 / 8).sqrt().alias("se_ex"))


def pools(z: pl.DataFrame, by: list[str]) -> pl.DataFrame:
    out = []
    for key, g in z.group_by(by):
        p = L.dl_pool(g["J"].to_numpy(), g["se"].to_numpy())
        q = L.dl_pool(g["ex"].to_numpy(), g["se_ex"].to_numpy())
        if p["k"] == 0:
            continue
        r = dict(zip(by, key))
        r.update({"k": p["k"], "re": p["re"], "re_lo": p["re_lo"], "re_hi": p["re_hi"], "ivw": p["ivw"],
                  "ivw_lo": p["ivw_lo"], "ivw_hi": p["ivw_hi"], "tau2": p["tau2"],
                  "null_mean": float(g["null_mean"].mean()), "ex": q["re"], "ex_lo": q["re_lo"], "ex_hi": q["re_hi"],
                  "ex_ivw": q["ivw"], "n_pos": int((g["lo"] > 0).sum()), "n_neg": int((g["hi"] < 0).sum()),
                  "reads": float(g["nRm"].sum())})
        out.append(r)
    return pl.DataFrame(out).sort(by)


# ============================================================================================ R3
def load_r3() -> pl.DataFrame:
    rows = []
    for f in sorted((R2 / "r3").glob("*.json")):
        r = json.loads(f.read_text())
        if "error" in r:
            print("R3 error", r["unit_id"], r["error"])
            continue
        rows.append(r)
    d = pl.DataFrame(rows, infer_schema_length=None)

    def g(c):
        return pl.col(c) if c in d.columns else pl.lit(None, pl.Float64)

    nn = pl.col("n_named_items").clip(1)
    nu = (pl.col("n_items") - pl.col("n_named_items")).clip(1)
    ex = []
    for b in ("r1", "cox10", "room10", "cox5"):
        ev = g(f"B:{b}:n_events")
        ex += [g(f"B:{b}:B:nx").alias(f"nxB_{b}"),
               (g(f"B:{b}:Bmu:n_Bm") * ev / nn).alias(f"pn_{b}"),
               (g(f"B:{b}:Bmu:n_Bu") * ev / nu).alias(f"pu_{b}"),
               (g(f"B:{b}:Bmu:n_Bm")).alias(f"nBm_{b}"),
               (g(f"B:{b}:B:cv") - g(f"B:{b}:S0:cv")).alias(f"gB_{b}"),
               (g(f"B:{b}:Bmu:cv") - g(f"B:{b}:S0:cv")).alias(f"gBmu_{b}"),
               (g(f"B:{b}:Bmu:cv_sum") - g(f"B:{b}:S0:cv_sum")).alias(f"gBmu_sum_{b}"),
               (g(f"B:{b}:B:cv_sum") - g(f"B:{b}:S0:cv_sum")).alias(f"gB_sum_{b}"),
               ev.alias(f"ev_{b}")]
    for b in ("r1", "cox10"):
        ex += [g(f"A:{b}:A:nx").alias(f"nxA_{b}"), (g(f"A:{b}:A:cv") - g(f"A:{b}:S0:cv")).alias(f"gA_{b}"),
               (g(f"A:{b}:A:cv_sum") - g(f"A:{b}:S0:cv_sum")).alias(f"gA_sum_{b}")]
    d = d.with_columns(ex)
    # the field used for verdicts: per-room field where the unit has > 1 room, else the per-day field
    multi = pl.col("n_rooms") > 1
    for s in ("nxB", "pn", "pu", "nBm", "gB", "gBmu", "gBmu_sum", "gB_sum"):
        d = d.with_columns(pl.when(multi & pl.col(f"{s}_room10").is_not_null()).then(pl.col(f"{s}_room10"))
                           .otherwise(pl.col(f"{s}_cox10")).alias(f"{s}_fld"))
    d = d.with_columns((pl.col("nxA_cox10") / pl.col("nxA_r1")).alias("survA"),
                       (pl.col("nxB_fld") / pl.col("nxB_r1")).alias("survB"),
                       (pl.col("pn_fld") / pl.col("pn_r1")).alias("survN"),
                       (pl.col("pn_fld") / COX_ATTEN).alias("pn_fld_corr"),
                       (pl.col("n_days") >= 2).alias("cv"))
    return d


def r3_period(d: pl.DataFrame) -> pl.DataFrame:
    w = pl.col("ev_r1")
    return (d.group_by("goal_no").agg(
        pl.col("regime").first(), pl.len().alias("units"), pl.col("cv").sum().alias("cv_units"),
        ((pl.col("nxA_r1") * w).sum() / w.sum()).alias("nxA_r1"), ((pl.col("nxA_cox10") * w).sum() / w.sum()).alias("nxA_cox"),
        ((pl.col("nxB_r1") * w).sum() / w.sum()).alias("nxB_r1"), ((pl.col("nxB_fld") * w).sum() / w.sum()).alias("nxB_fld"),
        ((pl.col("pn_r1") * pl.col("n_named_items")).sum() / pl.col("n_named_items").sum().clip(1)).alias("pn_r1"),
        ((pl.col("pn_fld") * pl.col("n_named_items")).sum() / pl.col("n_named_items").sum().clip(1)).alias("pn_fld"),
        pl.col("gBmu_sum_fld").filter(pl.col("cv")).sum().alias("gBmu_sum_fld"),
        pl.col("gB_sum_fld").filter(pl.col("cv")).sum().alias("gB_sum_fld"),
        pl.col("gA_sum_cox10").filter(pl.col("cv")).sum().alias("gA_sum_cox"),
        pl.col("unit_id").sort().str.join(",").alias("unit_ids"))
        .sort("goal_no"))


# ============================================================================================ scoring
def get(P, **kw):
    q = P
    for k, v in kw.items():
        q = q.filter(pl.col(k) == v)
    return q.to_dicts()[0] if len(q) else {}


def score(P: pl.DataFrame, r3: pl.DataFrame) -> dict:
    S = {}
    pn = get(P, regime="III", outcome="pause", spec="r2", field=False, X="named")
    S["R2-P1"] = {"ex": pn.get("ex"), "ci": [pn.get("ex_lo"), pn.get("ex_hi")], "raw": pn.get("re"),
                  "outcome": "supported" if pn.get("ex_hi", 1) < 0 else "inconclusive (CI includes 0; power < 0.8)"}
    lg = get(P, regime="III", outcome="loggap", spec="r2", field=False, X="named")
    S["R2-P2"] = {"ex": lg.get("ex"), "ci": [lg.get("ex_lo"), lg.get("ex_hi")], "raw": lg.get("re"),
                  "outcome": "supported (fragile)" if lg.get("ex_hi", 1) < 0 else "failed"}
    pu = get(P, regime="III", outcome="pause", spec="r2", field=False, X="un")
    lu = get(P, regime="III", outcome="loggap", spec="r2", field=False, X="un")
    ok3 = (pu.get("ex_lo", -1) < 0.001 and pu.get("ex_hi", 1) > -0.001 and abs(pu.get("ex", 1)) <= 0.001
           and abs(lu.get("ex", 1)) <= 0.005 and lu.get("ex_lo", -1) < 0.005 and lu.get("ex_hi", 1) > -0.005)
    S["R2-P3"] = {"pause_un": [pu.get("ex"), pu.get("ex_lo"), pu.get("ex_hi")],
                  "loggap_un": [lu.get("ex"), lu.get("ex_lo"), lu.get("ex_hi")], "outcome": "supported" if ok3 else "failed"}
    cu = get(P, regime="I", outcome="chatnext", spec="r2", field=False, X="un")
    cn = get(P, regime="I", outcome="chatnext", spec="r2", field=False, X="named")
    sn = get(P, regime="I", outcome="start", spec="r2", field=False, X="named")
    su = get(P, regime="I", outcome="start", spec="r2", field=False, X="un")
    ok4 = (max(abs(cu.get("ex_lo", 1)), abs(cu.get("ex_hi", 1))) <= 0.005
           and max(abs(cn.get("ex_lo", 1)), abs(cn.get("ex_hi", 1))) <= 0.02 + 1e-9
           and max(abs(sn.get("ex_lo", 1)), abs(sn.get("ex_hi", 1))) <= 0.02 + 1e-9)
    S["R2-P4"] = {"chatnext_un": [cu.get("ex"), cu.get("ex_lo"), cu.get("ex_hi")],
                  "chatnext_named": [cn.get("ex"), cn.get("ex_lo"), cn.get("ex_hi")],
                  "start_named": [sn.get("ex"), sn.get("ex_lo"), sn.get("ex_hi")],
                  "start_un_descriptive": [su.get("ex"), su.get("ex_lo"), su.get("ex_hi")],
                  "outcome": "supported" if ok4 else "failed"}
    tn = get(P, regime="III", outcome="talk", spec="r2", field=False, X="named")
    S["R2-P5"] = {"talk_named": tn.get("ex"), "pause_named": pn.get("ex"),
                  "ratio": (tn.get("ex", 0) / abs(pn.get("ex"))) if pn.get("ex") else None,
                  "outcome": "supported" if tn.get("ex", 0) >= 3 * abs(pn.get("ex", 1)) else "failed"}
    h = get(P, regime="III", outcome="talk", spec="h67", field=False, X="named")
    S["R1-P1"] = {"ivw": h.get("ivw"), "ivw_ci": [h.get("ivw_lo"), h.get("ivw_hi")], "re": h.get("re"),
                  "re_ci": [h.get("re_lo"), h.get("re_hi")],
                  "outcome": "supported" if 0.059 <= h.get("ivw", 0) <= 0.099 else
                  ("failed" if not 0.04 <= h.get("ivw", 0) <= 0.12 else "between")}
    c = get(P, regime="III", outcome="talk", spec="r1", field=False, X="cold")
    t = get(P, regime="III", outcome="talk", spec="r1", field=False, X="thrn")
    ratio = c.get("re", 0) / t.get("re", 1) if t.get("re") else None
    S["R1-P2"] = {"cold": [c.get("re"), c.get("re_lo"), c.get("re_hi")], "thread": [t.get("re"), t.get("re_lo"), t.get("re_hi")],
                  "ratio_re": ratio, "ratio_ivw": c.get("ivw", 0) / t.get("ivw", 1) if t.get("ivw") else None,
                  "ratio_ex": c.get("ex", 0) / t.get("ex", 1) if t.get("ex") else None,
                  "outcome": "supported" if (c.get("re_lo", -1) > 0 and ratio is not None and ratio >= 0.5) else
                  ("failed" if (c.get("re_lo", 1) <= 0 or (ratio is not None and ratio <= 0.25)) else "between")}
    f = get(P, regime="III", outcome="talk", spec="r2", field=True, X="named")
    ch = abs(f.get("re", 0) - tn.get("re", 0)) / max(abs(tn.get("re", 1)), 1e-9)
    S["R1-P3"] = {"no_field": tn.get("re"), "field": f.get("re"), "rel_change": ch,
                  "outcome": "supported" if ch < 0.2 else ("failed" if ch >= 0.4 else "between")}
    # R3
    cvu = r3.filter(pl.col("cv"))
    sA = r3.filter(pl.col("nxA_r1") > 0.005)["survA"]
    S["R3-P1"] = {"survA_median": float(sA.median()) if len(sA) else None, "units": len(sA),
                  "nxA_r1_median": float(r3["nxA_r1"].median()), "nxA_cox_median": float(r3["nxA_cox10"].median()),
                  "outcome": "supported" if len(sA) and sA.median() <= 0.5 else ("failed" if len(sA) and sA.median() >= 0.8 else "between")}
    share = float((cvu["gB_fld"] > 0).mean()) if len(cvu) else None
    S["R3-P2"] = {"share_B_beats_S0": share, "cv_units": len(cvu),
                  "outcome": "supported" if share is not None and share <= 0.5 else ("failed" if share and share > 0.65 else "between")}
    r3c = r3.filter(pl.col("regime") == "III")
    cv3 = r3c.filter(pl.col("cv"))
    med = float(r3c["pn_fld"].median()) if len(r3c) else None
    shr = float((cv3["gBmu_fld"] > 0).mean()) if len(cv3) else None
    S["R3-P3"] = {"pn_fld_median": med, "pn_fld_corr_median": (med / COX_ATTEN) if med is not None else None,
                  "pn_r1_median": float(r3c["pn_r1"].median()), "share_Bmu_beats_S0": shr, "cv_units": len(cv3),
                  "units": len(r3c), "survN_median": float(r3c.filter(pl.col("pn_r1") > 0)["survN"].median()),
                  "outcome": ("supported" if (med is not None and med >= 0.10 and shr >= 0.7) else
                              "supported on the corrected scale" if (med is not None and med / COX_ATTEN >= 0.10 and shr >= 0.7)
                              else "failed" if (med is not None and (med < 0.05 or shr <= 0.5)) else "between")}
    return S


def period_table(z: pl.DataFrame, r3p: pl.DataFrame | None) -> pl.DataFrame:
    keys = [("talk", "r2", False, "named"), ("talk", "r2", False, "un"), ("talk", "r1", False, "cold"),
            ("talk", "r1", False, "thrn"), ("pause", "r2", False, "named"), ("loggap", "r2", False, "named"),
            ("chatnext", "r2", False, "un"), ("chatnext", "r2", False, "named")]
    rows = []
    for g in sorted(z["goal_no"].unique().to_list()):
        zg = z.filter(pl.col("goal_no") == g)
        r = {"goal_no": g, "regime": zg["regime"][0], "units": zg["unit_id"].n_unique()}
        for o, sp, fd, X in keys:
            q = zg.filter((pl.col("outcome") == o) & (pl.col("spec") == sp) & (pl.col("field") == fd) & (pl.col("X") == X))
            nm = f"{o}_{X}"
            if len(q) == 0:
                continue
            p = L.dl_pool(q["J"].to_numpy(), q["se"].to_numpy())
            e = L.dl_pool(q["ex"].to_numpy(), q["se_ex"].to_numpy())
            r.update({nm: p["re"], nm + "_lo": p["re_lo"], nm + "_hi": p["re_hi"],
                      nm + "_ex": e["re"], nm + "_ex_lo": e["re_lo"], nm + "_ex_hi": e["re_hi"]})
        rows.append(r)
    P = pl.DataFrame(rows, infer_schema_length=None)
    if r3p is not None:
        P = P.join(r3p.drop("regime"), on="goal_no", how="left")
    # round-2 period verdict
    def verdict(r):
        if r.get("cv_units") in (None, 0):
            return "descriptive"
        a = (r.get("gBmu_sum_fld") or 0) > 0 and (r.get("pn_fld") or 0) > 1e-3   # numerical zero below 1e-3
        lo = r.get("talk_cold_lo")
        b = lo is not None and lo > 0
        return "supported" if (a and b) else ("failed" if not (a or b) else "mixed")
    P = P.with_columns(pl.Series("r2_verdict", [verdict(r) for r in P.iter_rows(named=True)]))
    return P


# ============================================================================================ estimates
def estimate_rows(z: pl.DataFrame, r3: pl.DataFrame) -> list[dict]:
    pu = pl.read_parquet(ROOT / "data/processed/shared/period_units.parquet").select("unit_id", "days")
    span = {r["unit_id"]: (min(r["days"]), max(r["days"])) for r in pu.iter_rows(named=True)}
    rows = []
    method_r2 = ("H42 r2: call-level matched-lag in-flight design (window min(latency, previous gap, 120 s)), OLS within "
                 "agent x day x call-class cells, all-present window; J = beta(read) - beta(in flight) per read")
    spec = [("talk", "r2", "named", "readout_talk_jump_named_callclock", False, "ok"),
            ("talk", "r2", "un", "readout_talk_jump_unnamed_callclock", False, "ok"),
            ("talk", "r1", "cold", "readout_talk_jump_cold_named", False, "ok"),
            ("talk", "r1", "thrn", "readout_talk_jump_thread_named", False, "ok"),
            ("pause", "r2", "named", "readout_pause_jump_named_excess", True, "underpowered"),
            ("loggap", "r2", "named", "readout_loggap_jump_named_excess", True, "fragile"),
            ("chatnext", "r2", "un", "readout_chatnext_jump_unnamed_excess", True, "ok"),
            ("chatnext", "r2", "named", "readout_chatnext_jump_named_excess", True, "ok")]
    for o, sp, X, stat, excess, status in spec:
        q = z.filter((pl.col("outcome") == o) & (pl.col("spec") == sp) & (~pl.col("field")) & (pl.col("X") == X))
        if o == "pause" or o == "loggap":
            q = q.filter(pl.col("regime") == "III")
        if o == "chatnext":
            q = q.filter(pl.col("regime") != "III")
        for r in q.iter_rows(named=True):
            f, l_ = span.get(r["unit_id"], (None, None))
            if excess:
                est, se = r["ex"], r["se_ex"]
                lo, hi, kind = est - 1.96 * se, est + 1.96 * se, "se_z"
                null = "in-flight placebo (matched lag) minus the call-skeleton null mean (8 synthetic streams)"
            else:
                est, se, lo, hi, kind = r["J"], r["se"], r["lo"], r["hi"], "percentile"
                null = "in-flight placebo (matched lag)"
            rows.append({"period_unit": r["unit_id"], "goal_no": int(r["goal_no"]), "statistic": stat,
                         "channel": "talk" if o == "talk" else o, "estimate": float(est), "ci_lo": float(lo),
                         "ci_hi": float(hi), "n": float(r["n"]), "method": method_r2, "null": null,
                         "role": "replication", "ci_level": 0.95, "ci_kind": kind, "se": float(se), "n_kind": "calls",
                         "first_day": f, "last_day": l_, "confirmatory": False, "post_hoc": False, "status": status,
                         "source": "data/processed/H42-readout-hawkes-kernel/round2/r2_units.parquet",
                         "notes": f"reads in matched window {int(r['nRm'])}"})
    method_r3 = ("H42 r3: round-1 world-B Hawkes (call-clock world) with a Cox field baseline (free log-rate per day x "
                 "10-min bin; per day x room x 10 min in multi-room units); named / unnamed read-out kernels")
    for r in r3.iter_rows(named=True):
        f, l_ = span.get(r["unit_id"], (None, None))
        for stat, col, ch, meth in (("cox_field_named_talk_per_message", "pn_fld", "talk", method_r3),
                                    ("cox_field_readout_nx", "nxB_fld", "talk", method_r3),
                                    ("cox_field_exponential_nx", "nxA_cox10", "talk",
                                     "H42 r3: round-1 world-A Hawkes (exponential kernel from posting) with a per-day "
                                     "10-min Cox field baseline")):
            v = r.get(col)
            if v is None or not np.isfinite(v):
                continue
            rows.append({"period_unit": r["unit_id"], "goal_no": int(r["goal_no"]), "statistic": stat, "channel": ch,
                         "estimate": float(v), "ci_lo": None, "ci_hi": None, "n": float(r.get("ev_r1") or 0),
                         "method": meth, "null": "fitted Cox field (latent common rate); synthetic attenuation 0.75",
                         "role": "replication", "ci_kind": "none", "n_kind": "events", "first_day": f, "last_day": l_,
                         "confirmatory": False, "post_hoc": False, "status": "ok",
                         "source": "data/processed/H42-readout-hawkes-kernel/round2/r3_units.parquet"})
    return rows


def main():
    d = pl.read_parquet(R2 / "r2_units.parquet")
    z = long_r2(d)
    z.write_parquet(R2 / "r2_long.parquet")
    P = pools(z, ["regime", "outcome", "spec", "field", "X"])
    P.write_parquet(R2 / "r2_pools.parquet")
    r3 = load_r3() if (R2 / "r3").exists() else None
    if r3 is not None:
        r3.write_parquet(R2 / "r3_units.parquet")
        r3p = r3_period(r3)
        r3p.write_parquet(R2 / "r3_periods.parquet")
    else:
        r3p = None
    PT = period_table(z, r3p)
    PT.write_parquet(R2 / "r2_periods.parquet")
    S = score(P, r3) if r3 is not None else {}
    # R3 descriptives
    if r3 is not None:
        desc = {}
        for reg in ("I", "II", "III"):
            x = r3.filter(pl.col("regime") == reg)
            if len(x) == 0:
                continue
            cvx = x.filter(pl.col("cv"))
            desc[reg] = {c: float(x[c].median()) for c in ("nxA_r1", "nxA_cox10", "nxB_r1", "nxB_cox10", "nxB_fld",
                                                           "pn_r1", "pn_cox10", "pn_fld", "pu_r1", "pu_fld", "pn_cox5")
                         if c in x.columns and x[c].drop_nulls().len()}
            desc[reg].update({"units": len(x), "cv_units": len(cvx),
                              "share_gA_cox_pos": float((cvx["gA_cox10"] > 0).mean()) if len(cvx) else None,
                              "share_gA_r1_pos": float((cvx["gA_r1"] > 0).mean()) if len(cvx) else None,
                              "share_gB_fld_pos": float((cvx["gB_fld"] > 0).mean()) if len(cvx) else None,
                              "share_gBmu_fld_pos": float((cvx["gBmu_fld"] > 0).mean()) if len(cvx) else None,
                              "share_gBmu_r1_pos": float((cvx["gBmu_r1"] > 0).mean()) if len(cvx) else None,
                              "median_gBmu_fld_mnats": float(cvx["gBmu_fld"].median() * 1000) if len(cvx) else None,
                              "median_gA_cox_mnats": float(cvx["gA_cox10"].median() * 1000) if len(cvx) else None})
        S["R3_descriptive"] = desc
        # reproduction of round 1's named kernel (round-1 baseline refitted here vs round-1 posthoc)
        ph = pl.read_parquet(L.DATA / "posthoc_mention.parquet").select(
            "unit_id", (pl.col("n_named") * pl.col("n_events") / pl.col("n_named_items").clip(1)).alias("pn_round1"))
        j = r3.join(ph, on="unit_id").filter(pl.col("regime") == "III")
        S["R3_reproduction"] = {"pn_round1_median": float(j["pn_round1"].median()), "pn_r1_median": float(j["pn_r1"].median()),
                                "spearman": float(j.select(pl.corr("pn_round1", "pn_r1", method="spearman")).item())}
    S["periods"] = {"verdicts": PT.group_by("r2_verdict").len().to_dicts()}
    (R2 / "summary.json").write_text(json.dumps(S, indent=1, default=float))
    pl.Config.set_tbl_rows(200); pl.Config.set_tbl_width_chars(250); pl.Config.set_tbl_cols(24)
    print(P.filter(~pl.col("field") | pl.col("outcome").is_in(["talk", "pause"])).select(
        "regime", "outcome", "spec", "field", "X", "k", "re", "re_lo", "re_hi", "ivw", "null_mean", "ex", "ex_lo",
        "ex_hi", "n_pos", "n_neg").with_columns(pl.col(pl.Float64).round(4)))
    print(json.dumps(S, indent=1, default=float))
    if "--write-estimates" in sys.argv:
        sys.path.insert(0, str(ROOT / "infra/shared"))
        import estimates as E
        rows = estimate_rows(z, r3)
        E.write_estimates(rows, hypothesis="H42")
        print("estimates rows", len(rows))


if __name__ == "__main__":
    main()
