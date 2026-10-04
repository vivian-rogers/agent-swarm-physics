"""H53 round 1 on real data (non-holdout): pooled and per-period estimators, sensitivity grid, placebos, field diagnostics.

Writes data/processed/H53-announcement-nucleation/round1/{round1.json, period_GNN.json, agent_table.parquet, seed_table.parquet}.
Usage: uv run python hypotheses/H53-announcement-nucleation/analysis/run_round1.py [--quick]
"""
from __future__ import annotations

import argparse
import json
import math
import time

import numpy as np
import polars as pl

from h53core import (FU_S, H_S, OUT, MODELS, agent_rr, agent_table, auc_within, cv_compare, dersimonian_laird, design,
                     eligible_periods, field_diagnostics, load, nb_fit, nb_robust_se, prep, seed_models, shift_slopes)
from synthetic import classify_v2

R1 = OUT / "round1"


def log(*a):
    print(f"[{time.strftime('%H:%M:%S')}]", *a, flush=True)


def add_prior_and_placebo(t: pl.DataFrame, r: pl.DataFrame, seeds: pl.DataFrame) -> pl.DataFrame:
    """k_prior: in-room susceptible adopters of X between the seed and i's read-out. y_other: i adopts another new project
    (seeded within +-2 h in the period, i not adopted before the seed) within FU after its read-out."""
    ad = r.filter(pl.col("sus_in") & pl.col("a_label").is_not_null()).select("sid", pl.col("a_label").alias("a_adj"))
    kp = (t.select("sid", "agent", "a_read", "a_seed").join(ad, on="sid", how="left")
          .with_columns(((pl.col("a_adj") > pl.col("a_seed")) & (pl.col("a_adj") < pl.col("a_read"))).fill_null(False).alias("pr"))
          .group_by("sid", "agent").agg(pl.col("pr").sum().alias("k_prior")))
    t = t.join(kp, on=["sid", "agent"], how="left").with_columns(pl.col("k_prior").fill_null(0))
    adopt = pl.read_parquet(OUT / "adoptions.parquet").select("goal_no", "agent", "proj", "a_label").drop_nulls("a_label")
    sd = seeds.select("goal_no", pl.col("proj").alias("proj2"), pl.col("a_seed").alias("a_seed2"))
    x = t.select("sid", "agent", "goal_no", "a_seed", "a_read").join(seeds.select("sid", "proj"), on="sid").join(sd, on="goal_no", how="inner").filter(
        (pl.col("proj2") != pl.col("proj")) & ((pl.col("a_seed2") - pl.col("a_seed")).abs() <= 7200))
    x = x.join(adopt.rename({"proj": "proj2", "a_label": "a2"}), on=["goal_no", "agent", "proj2"], how="inner").filter(
        (pl.col("a2") >= pl.col("a_seed")) & (pl.col("a2") > pl.col("a_read") - 1e-6) & (pl.col("a2") <= pl.col("a_read") + FU_S))
    yo = x.group_by("sid", "agent").agg(pl.len().alias("n_other"))
    t = t.join(yo, on=["sid", "agent"], how="left").with_columns((pl.col("n_other").fill_null(0) > 0).cast(pl.Float64).alias("y_other"))
    return t.with_columns(pl.col("k_prior").cast(pl.Float64).log1p().alias("lkprior"))


def rr_summary(res, key="x_timely"):
    v = res.get(key)
    return None if v is None else dict(rr=v["rr"], lo=v["lo"], hi=v["hi"], n=res["n"], n_adopt=res["n_adopt"])


def per_period_rr(t, goals, xcols=("x_timely", "x_unc", "lcalls", "talk")):
    out = {}
    for g in goals:
        d = t.filter(pl.col("goal_no") == g)
        try:
            out[int(g)] = agent_rr(d, xcols=xcols)
        except Exception as e:  # noqa: BLE001
            out[int(g)] = dict(error=str(e), n=d.height)
    return out


def seed_slope(s, cols, cl="day"):
    y, X, gi, G = design(s, cols)
    th, ll = nb_fit(y, X, gi, G)
    day = (s["goal_no"].cast(pl.String) + "_" + s["pt_date"]).to_numpy()
    se = nb_robust_se(th, y, X, gi, G, day)
    return {c: dict(beta=float(th[G + i]), se=float(se[i]), lo=float(th[G + i] - 1.96 * se[i]), hi=float(th[G + i] + 1.96 * se[i]))
            for i, c in enumerate(cols)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    R1.mkdir(parents=True, exist_ok=True)
    seeds0, rec0 = load()
    s, r = prep(seeds0, rec0)
    goals = eligible_periods(s)
    s = s.filter(pl.col("goal_no").is_in(goals))
    r = r.filter(pl.col("goal_no").is_in(goals))
    out = dict(goals=goals, n_seeds=int(s.filter(pl.col("eligible")).height))
    log("periods", goals, "eligible seeds", out["n_seeds"])

    # ---------------- P1 agent level
    t = agent_table(s, r)
    t = add_prior_and_placebo(t, r, s)
    t.write_parquet(R1 / "agent_table.parquet", compression="zstd")
    p1 = agent_rr(t)
    out["P1"] = p1
    out["P1_int"] = agent_rr(t, xcols=("x_recept", "x_timely", "x_unc", "lcalls", "talk"))
    out["P1_agentFE"] = agent_rr(t, extra_fe="agent")
    out["P1_prior"] = agent_rr(t, xcols=("x_timely", "x_unc", "lcalls", "talk", "lkprior"))
    out["P1_nocontrols"] = agent_rr(t, xcols=("x_timely",))
    pp = per_period_rr(t, goals)
    out["P1_by_period"] = pp
    est = [math.log(v["x_timely"]["rr"]) if "x_timely" in v else np.nan for v in pp.values()]
    se = [v["x_timely"]["se"] if "x_timely" in v else np.nan for v in pp.values()]
    out["P1_meta"] = dersimonian_laird(est, se)
    log("P1", rr_summary(p1), "meta", out["P1_meta"])
    log("P1_int", rr_summary(out["P1_int"], "x_recept"))
    # placebo outcome O9
    to = t.with_columns(pl.col("y_other").alias("y"))
    out["O9_placebo_outcome"] = agent_rr(to)
    log("O9", rr_summary(out["O9_placebo_outcome"]))

    # ---------------- sensitivity grid (agent level)
    grid = {}
    for lab, kw in [("c0.5", dict(c_mult=0.5)), ("c1", dict(c_mult=1.0)), ("c2", dict(c_mult=2.0)), ("c4", dict(c_mult=4.0)),
                    ("f60", dict(c_fixed=60)), ("f120", dict(c_fixed=120)), ("f300", dict(c_fixed=300)), ("f600", dict(c_fixed=600)),
                    ("f1800", dict(c_fixed=1800))]:
        for unc in ("u0", "u2", "none"):
            for var in ("label", "action", "mention"):
                s2, r2 = prep(seeds0, rec0, variant=var, unc=unc, **kw)
                s2 = s2.filter(pl.col("goal_no").is_in(goals)); r2 = r2.filter(pl.col("goal_no").is_in(goals))
                t2 = agent_table(s2, r2, variant=var)
                key = f"{lab}|{unc}|{var}"
                res = agent_rr(t2)
                grid[key] = dict(timely=rr_summary(res), unc=rr_summary(res, "x_unc"))
                if lab in ("c1", "f600") and unc == "u0":
                    rint = agent_rr(t2, xcols=("x_recept", "x_timely", "x_unc", "lcalls", "talk"))
                    grid[key]["recept_int"] = rr_summary(rint, "x_recept")
                    if lab == "f600" and var == "label":
                        t2b = add_prior_and_placebo(t2, r2, s2)
                        grid[key]["placebo_outcome"] = rr_summary(agent_rr(t2b.with_columns(pl.col("y_other").alias("y"))))
                        grid[key]["by_period"] = {g: rr_summary(v) for g, v in per_period_rr(t2, goals).items() if "x_timely" in v}
        log("grid", lab, grid[f"{lab}|u0|label"]["timely"])
    out["grid"] = grid
    # commits (periods >= 30)
    gc = [g for g in goals if g >= 30]
    s3, r3 = prep(seeds0, rec0, variant="commit")
    s3 = s3.filter(pl.col("goal_no").is_in(gc)); r3 = r3.filter(pl.col("goal_no").is_in(gc))
    t3 = agent_table(s3, r3, variant="commit")
    out["P7_commit"] = agent_rr(t3)
    out["P7_commit_seed"] = dict(mean_S=float(s3.filter(pl.col("eligible"))["S"].mean()), n=int(s3.filter(pl.col("eligible")).height),
                                 frac_zero=float((s3.filter(pl.col("eligible"))["S"] == 0).mean()))
    log("P7 commit", rr_summary(out["P7_commit"]))

    # ---------------- P2 seed level
    se_ = s.filter(pl.col("eligible"))
    se_.write_parquet(R1 / "seed_table.parquet", compression="zstd")
    out["seed_desc"] = dict(mean_S=float(se_["S"].mean()), frac_zero=float((se_["S"] == 0).mean()), max_S=int(se_["S"].max()),
                            q90=float(se_["S"].quantile(0.9)), mean_R=float(se_["R"].mean()), mean_N=float(se_["N_sus"].mean()),
                            corr_R_N=float(np.corrcoef(se_["R"], se_["N_sus"])[0, 1]), corr_R_U=float(np.corrcoef(se_["R"], se_["U"])[0, 1]))
    for tag, tau in (("", 1.0), ("_fe", None)):   # primary: partial pooling of period intercepts (tau = 1); literal FE alongside
        mod, cvll, cg = seed_models(s, cv="lodo", ridge_tau=tau)
        out["P2_models" + tag] = {k: dict(cv_ll=v["cv_ll"], coef=v["coef"], se=v["se"], cols=v["cols"], ll=v["ll"], n=v["n"], phi=v["phi"]) for k, v in mod.items()}
        cmpd = {f"M_R-{b}": cv_compare(cvll, cg, "M_R", b) for b in ("M0", "M_N", "M_U", "M_status", "M_share", "M_tod")}
        cmpd["M_full+R-M_full"] = cv_compare(cvll, cg, "M_full+R", "M_full")
        for b in ("M_N", "M_U", "M_status", "M_share", "M_tod", "M_full"):
            cmpd[f"{b}-M0"] = cv_compare(cvll, cg, b, "M0")
        out["P2_cmp" + tag] = cmpd
        log("P2 cv" + tag, {k: round(v["cv_ll"], 1) for k, v in mod.items()})
    # per-period slopes of S on lR (with lN) and DL
    ps = {}
    for g in goals:
        d = se_.filter(pl.col("goal_no") == g)
        if d["S"].sum() == 0 or d.height < 10:
            continue
        try:
            ps[int(g)] = seed_slope(d, ["lR", "lN"])
        except Exception as e:  # noqa: BLE001
            ps[int(g)] = dict(error=str(e))
    out["P2_by_period"] = ps
    out["P2_meta_lR"] = dersimonian_laird([v["lR"]["beta"] for v in ps.values() if "lR" in v], [v["lR"]["se"] for v in ps.values() if "lR" in v])
    # horizons
    hz = {}
    for H in (3600, 7200, 14400):
        sH, _ = prep(seeds0, rec0, H=H)
        sH = sH.filter(pl.col("goal_no").is_in(goals))
        hz[H] = seed_slope(sH.filter(pl.col("eligible")), ["lN", "lU", "lstat", "human", "share", "tod", "first30", "lR"])
    out["P2_horizons"] = hz

    # ---------------- P3 status: from P2 models
    # ---------------- P4 placebo: herded vs never-herded seeds
    se2 = se_.with_columns(pl.max_horizontal(pl.lit(3), (pl.col("n_room") / 3).ceil()).alias("thr"))
    pos = pl.col("herd_kmax") >= pl.col("thr")
    neg = pl.col("herd_kmax") <= 1
    out["P4"] = {c: auc_within(se2, c, pos, neg) for c in ("R", "N_sus", "U", "lstat", "share", "tod", "S")}
    out["P4"]["n_herded"] = int(se2.filter(pos).height); out["P4"]["n_never"] = int(se2.filter(neg).height)
    log("P4", {k: v for k, v in out["P4"].items()})

    # ---------------- P5/P10 shift slopes
    out["P10_shift"] = shift_slopes(s, r)
    out["P10_shift_noN"] = shift_slopes(s, r, adjust_N=False)
    log("P10", {k: round(v["beta"], 2) for k, v in out["P10_shift"].items()})

    # ---------------- P6 field diagnostics
    out["P6"] = field_diagnostics(s, r)
    out["P6_action"] = field_diagnostics(*prep(seeds0.filter(pl.col("goal_no").is_in(goals)), rec0.filter(pl.col("goal_no").is_in(goals)), variant="action"), variant="action")
    log("P6", {k: (v if k != "F1" else {kk: vv for kk, vv in v.items() if kk != "curve"}) for k, v in out["P6"].items()})
    # classification v2 (pooled)
    synth_like = dict(agent=p1, field=out["P6"], models=out["P2_models"])
    out["label_v2"] = classify_v2(synth_like)

    # ---------------- P9 operator rule
    mfr = out["P2_models"]["M_full+R"]
    bR = mfr["coef"][mfr["cols"].index("lR")]
    q = se_.group_by("goal_no").agg(pl.col("R").quantile(0.9).alias("r90"), pl.col("R").quantile(0.5).alias("r50"),
                                    (pl.col("R") <= pl.col("R").quantile(0.25)).mean().alias("low"))
    q = q.with_columns((((1 + pl.col("r90")) / (1 + pl.col("r50"))) ** bR).alias("gain"))
    out["P9"] = dict(beta_R=bR, median_gain=float(q["gain"].median()), by_period={int(g): float(v) for g, v in zip(q["goal_no"], q["gain"])},
                     rr_timely_c1=rr_summary(p1))

    # ---------------- human seeds (descriptive)
    hs = se_.filter(pl.col("human") > 0)
    out["human_seeds"] = dict(n=hs.height, mean_S=float(hs["S"].mean()) if hs.height else None, agent_mean_S=float(se_.filter(pl.col("human") == 0)["S"].mean()))

    # ---------------- post hoc (labelled; after seeing the primary results)
    ph = {}
    tl = t.with_columns((pl.col("age_s") / 60).log1p().alias("lage"))
    ph["lateness_log_age_min"] = agent_rr(tl, xcols=("lage", "x_unc", "lcalls", "talk"))
    ph["lateness_with_kprior"] = agent_rr(tl, xcols=("lage", "x_unc", "lcalls", "talk", "lkprior"))
    ph["rank_in_batch"] = agent_rr(tl.with_columns(pl.col("k_new").cast(pl.Float64).log1p().alias("lknew")), xcols=("x_timely", "lknew", "x_unc", "lcalls", "talk"))
    for lab, flt in (("new_projects", ~pl.col("carried")), ("carried_projects", pl.col("carried"))):
        sc_ = s.filter(flt)
        ph[f"F_{lab}"] = field_diagnostics(sc_, r.filter(pl.col("sid").is_in(sc_["sid"].to_list())))
        ph[f"P1_{lab}"] = agent_rr(t.filter(pl.col("sid").is_in(sc_["sid"].to_list())))
    by_reg = {}
    for reg in ("I", "II", "III"):
        sr = s.filter(pl.col("regime") == reg)["sid"].to_list()
        by_reg[reg] = dict(P1=rr_summary(agent_rr(t.filter(pl.col("sid").is_in(sr)))),
                           P1_f300=None)
    ph["by_regime"] = by_reg
    out["posthoc"] = ph
    log("posthoc lateness", rr_summary(ph["lateness_log_age_min"], "lage"), "F new", ph["F_new_projects"]["F1"]["ratio"], "F carried", ph["F_carried_projects"]["F1"]["ratio"])

    # ---------------- per period package
    for g in goals:
        sg, rg = s.filter(pl.col("goal_no") == g), r.filter(pl.col("goal_no") == g)
        tg = t.filter(pl.col("goal_no") == g)
        el = sg.filter(pl.col("eligible"))
        fd = field_diagnostics(sg, rg)
        pkg = dict(goal=g, n_seeds=int(el.height), mean_S=float(el["S"].mean()), max_S=int(el["S"].max()), mean_R=float(el["R"].mean()),
                   frac_zero=float((el["S"] == 0).mean()), agent=pp.get(int(g)), agent_n_adopt=int(tg["y"].sum()),
                   agent_f600=grid["f600|u0|label"].get("by_period", {}).get(int(g)),
                   field=fd, seed_slope=ps.get(int(g)),
                   herded=int(el.with_columns(pl.max_horizontal(pl.lit(3), (pl.col("n_room") / 3).ceil()).alias("thr")).filter(pl.col("herd_kmax") >= pl.col("thr")).height),
                   never=int(el.filter(pl.col("herd_kmax") <= 1).height))
        pkg["label_v2"] = classify_v2(dict(agent=pp.get(int(g), {}), field=fd, models=out["P2_models"])) if pp.get(int(g), {}).get("x_timely") else "n/a"
        (R1 / f"period_G{g:02d}.json").write_text(json.dumps(pkg, indent=1, default=str))
    (R1 / "round1.json").write_text(json.dumps(out, indent=1, default=str))
    from h53lib import provenance
    provenance("analysis/run_round1.py", ["seeds (H53)", "recipients (H53)", "adoptions (H53)"], dict(primary="c=1 cycle, u0, label, H=2h, FU=60min, NB ridge tau=1"), "hypotheses/H53-announcement-nucleation/analysis/run_round1.py")
    log("done; label_v2", out["label_v2"])


if __name__ == "__main__":
    main()
