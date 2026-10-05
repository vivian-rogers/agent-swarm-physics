"""H44 round-2 synthetic validation (axis F), run before any round-2 statistic on real data.

Real skeletons (G51, G38, G37): real complete sawtooths (agents, agent-days, positions), real events, real pre-window
object sets, real loop strata. Planted worlds:
  R2  W curves: two timescales + ramp (A2r), one timescale + ramp (A1r), two timescales without ramp (A2n), interior
      optimum (INT); R curves: spike + tail (R2), spike only + ramp (R1). Agent (sd 0.4) and agent-day (sd 0.3)
      log-normal multipliers make the counts overdispersed.
  R3  recency null: a post-reset read call re-opens an object of the pre set with probability q * frac_e, where frac_e is
      the recency-weighted (tau 15 calls) share of the agent-day's earlier objects that sit in the pre window (real
      sets); planted: forced read calls get an extra re-open probability delta = 0.15.
  R4  multiplicative-dip null: the reset multiplies writes by d(k) = 1 - 0.6 exp(-(k-1)/3) in both strata; loops
      persist into the post window with probability 0.6 after a forced reset and after a pseudo boundary alike
      (loop calls write at lambda = 0.5 of the base). Planted: a forced reset ends the loop (persistence 0.15).
Outputs: data/processed/H44-erasure-reacquisition-thrash/r2/synthetic.json
Usage: uv run python hypotheses/H44-erasure-reacquisition-thrash/analysis/r2_synthetic.py [--reps 40] [--periods G51,G38,G37]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import h44lib as L  # noqa: E402
import r2lib as R  # noqa: E402
from h44lib import C  # noqa: E402

OUTD = C.OUT / "r2"


def curve(k, c, beta=0.0, gamma=0.0, A1=0.0, l1=1.0, A2=0.0, l2=5.0):
    x = np.asarray(k, float) - 1
    return c + beta * x + gamma * x ** 2 + A1 * np.exp(-x / l1) + A2 * np.exp(-x / l2)


WORLDS_W = {"A2r": dict(c=0.11, beta=0.0006, A1=-0.07, l1=0.8, A2=-0.025, l2=5.0),
            "A1r": dict(c=0.11, beta=0.0006, A1=-0.085, l1=2.0),
            "A2n": dict(c=0.12, A1=-0.07, l1=0.8, A2=-0.025, l2=5.0),
            "INT34": dict(c=0.075, beta=0.004, gamma=-0.0001, A1=-0.06, l1=0.8, A2=-0.02, l2=5.0),
            "INT25": dict(c=0.10, beta=0.004, gamma=-0.00015, A1=-0.06, l1=0.8, A2=-0.02, l2=5.0)}
WORLDS_R = {"R2": dict(c=0.24, beta=-0.0008, A1=0.20, l1=0.8, A2=0.06, l2=6.0),
            "R1": dict(c=0.24, beta=-0.0008, A1=0.24, l1=1.2)}


def planted_Lstar(par):
    W = np.clip(curve(np.arange(1, 41), **par), 0, 1)
    Y = R.cap_curve(W, 1.0)
    return int(np.arange(5, 41)[np.argmax(Y[4:])])


def r2_worlds(saw: pl.DataFrame, reps: int, rng) -> dict:
    ag = saw["agent"].to_numpy(); cl = saw["cl"].to_numpy(); k = saw["k"].to_numpy()
    ag_u, ag_i = np.unique(ag, return_inverse=True); cl_u, cl_i = np.unique(cl, return_inverse=True)
    out = {}
    for fam, worlds in (("W", WORLDS_W), ("R", WORLDS_R)):
        for wn, par in worlds.items():
            p0 = np.clip(curve(k, **par), 0.001, 0.999)
            rows = []
            for r in range(reps):
                ma = np.exp(rng.normal(0, 0.4, len(ag_u)) - 0.08)[ag_i]
                mc = np.exp(rng.normal(0, 0.3, len(cl_u)) - 0.045)[cl_i]
                y = rng.random(len(k)) < np.clip(p0 * ma * mc, 0, 0.999)
                s = saw.with_columns(pl.Series("y", y))
                num, den, _ = R.curve_sums(s, "y")
                Bw = L.boot_weights(num.shape[0], 100, rng)
                fc = R.fit_compare(num, den, True, Bw)
                row = {k_: fc[k_] for k_ in fc if k_.startswith("dAIC") or k_.startswith("dQAIC")}
                row["chat"] = fc["chat"]
                row["l1"] = fc["fits"]["M2"]["l1"]; row["l2"] = fc["fits"]["M2"]["l2"]
                row["beta"] = fc["fits"]["M2"]["beta"]
                pb = R.param_boot(num, den, Bw, "M2", True, 12.0)
                row["beta12"] = pb["beta"]; row["l1_12"] = pb["l1"][0]; row["l2_12"] = pb["l2"][0]
                if fam == "W":
                    cs = R.cap_stats(num, den, Bw, 1.0)
                    row.update({"L_star": cs["L_star"], "P_edge": cs["P_edge"], "P_lt35": cs["P_lt35"]})
                rows.append(row)
            res = {"planted": par, "n_calls": int(len(k)), "reps": rows}
            for crit in ("dAIC", "dQAIC"):
                res[f"{crit}_M2_vs_M1_ge4"] = float(np.mean([x[f"{crit}_M2_vs_M1"] >= 4 for x in rows]))
                res[f"{crit}_ramp_ge4"] = float(np.mean([max(x[f"{crit}_M2_vs_M0"], x[f"{crit}_M1_vs_M0"]) >= 4 for x in rows]))
            res["beta_pos_mean"] = float(np.mean([x["beta"] for x in rows]))
            res["beta12_mean"] = float(np.mean([x["beta12"][0] for x in rows]))
            res["beta12_cipos_rate"] = float(np.mean([x["beta12"][1] > 0 for x in rows]))
            res["beta12_cineg_rate"] = float(np.mean([x["beta12"][2] < 0 for x in rows]))
            res["l2_12_med"] = float(np.median([x["l2_12"] for x in rows]))
            res["chat_mean"] = float(np.mean([x["chat"] for x in rows]))
            res["l1_med"] = float(np.median([x["l1"] for x in rows])); res["l2_med"] = float(np.median([x["l2"] for x in rows]))
            if fam == "W":
                res["planted_L_star"] = planted_Lstar(par)
                res["edge_rule_rate"] = float(np.mean([x["P_edge"] >= 0.8 for x in rows]))
                res["lt35_rule_rate"] = float(np.mean([x["P_lt35"] >= 0.8 for x in rows]))
                res["L_star_med"] = float(np.median([x["L_star"] for x in rows]))
            out[f"{fam}:{wn}"] = res
            C.log("R2", wn, {k_: v for k_, v in res.items() if k_ not in ("reps", "planted")})
    return out


def r3_worlds(calls, ev, obj, reps, rng, q=0.6, delta=0.15, tau=15.0) -> dict:
    p = R.object_panel(calls, ev, obj, "paths")
    # frac_e at the boundary from the agent-day's real object history (last touch before the event's first post call)
    ev2 = ev.filter(pl.col("ev_id").is_in(p["ev_id"].unique().implode())).select("ev_id", "agent", "pt_date", "seq")
    hist = (calls.select("turn_id", "agent", "pt_date", "seq").join(obj.select("turn_id", "paths"), on="turn_id")
            .explode("paths").drop_nulls("paths"))
    j = hist.join(ev2, on=["agent", "pt_date"]).filter(pl.col("seq") < pl.col("seq_right"))
    j = j.group_by("ev_id", "paths").agg((pl.col("seq_right") - pl.col("seq")).min().alias("age"))
    j = j.with_columns((-pl.col("age") / tau).exp().alias("w"), (pl.col("age") <= 20).alias("inpre"))
    fr = j.group_by("ev_id").agg((pl.col("w") * pl.col("inpre")).sum().alias("wp"), pl.col("w").sum().alias("wa"))
    fr = fr.with_columns((pl.col("wp") / pl.col("wa")).alias("frac"))
    pre_obj = (p.filter(pl.col("k") < 0).select("ev_id", "obj").explode("obj").drop_nulls("obj")
               .group_by("ev_id").agg(pl.col("obj").first().alias("o1")))
    is_post = (pl.col("k").is_between(1, 10) & pl.col("cat").is_in(R.READ_IDX) & pl.col("obj").is_not_null()
               & (pl.col("obj").list.len() > 0))
    base = p.join(fr.select("ev_id", "frac"), on="ev_id", how="left").join(pre_obj, on="ev_id", how="left")
    base = base.with_columns(pl.col("frac").fill_null(0.0), is_post.alias("is_post"))
    frdf = R.recency_frac(calls, ev, obj, "paths", p["ev_id"].unique().to_list())
    out = {}
    for world in ("null", "planted"):
        rows = []
        for r in range(reps):
            u = rng.random(base.height)
            ph = q * base["frac"].to_numpy()
            forced = (base["ev_kind"] == "forced").to_numpy()
            if world == "planted":
                ph = np.where(forced, ph + (1 - ph) * delta, ph)
            hit = (u < ph) & base["o1"].is_not_null().to_numpy()
            newo = (rng.integers(1, 2 ** 62, base.height)).astype(np.int64)
            o1 = base["o1"].fill_null(0).to_numpy()
            isp = base["is_post"].to_numpy()
            synth = np.where(hit, o1, newo)
            s = base.with_columns(pl.Series("synth", synth, dtype=pl.Int64)).with_columns(
                pl.when(pl.col("is_post")).then(pl.concat_list([pl.col("synth")])).otherwise(pl.col("obj")).alias("obj"))
            st = R.reopen_stats(s, B=200, seed=int(rng.integers(1e9)))
            ra = R.recency_adjusted(s, frdf, st, B=200, seed=int(rng.integers(1e9)))
            rows.append({"ex_FP": ra["excess_FP"], "ex_FV": ra["excess_FV"],
                         "d_FP": st.get("d_forced_pseudo31"), "d_FV": st.get("d_forced_voluntary"),
                         "rho_F": st["forced"].get("rho"), "rho_P": st["pseudo31"].get("rho")})
        res = {"reps": rows,
               "dFP_pos_rate": float(np.mean([x["d_FP"][1] > 0 for x in rows if x["d_FP"]])),
               "dFP_neg_rate": float(np.mean([x["d_FP"][2] < 0 for x in rows if x["d_FP"]])),
               "dFP_mean": float(np.mean([x["d_FP"][0] for x in rows if x["d_FP"]])),
               "dFV_pos_rate": float(np.mean([x["d_FV"][1] > 0 for x in rows if x["d_FV"]])),
               "exFP_pos_rate": float(np.mean([x["ex_FP"][1] > 0 for x in rows])),
               "exFP_neg_rate": float(np.mean([x["ex_FP"][2] < 0 for x in rows])),
               "exFP_mean": float(np.mean([x["ex_FP"][0] for x in rows])),
               "exFV_pos_rate": float(np.mean([x["ex_FV"][1] > 0 for x in rows])),
               "exFV_neg_rate": float(np.mean([x["ex_FV"][2] < 0 for x in rows])),
               "exFV_mean": float(np.mean([x["ex_FV"][0] for x in rows])),
               "dFV_mean": float(np.mean([x["d_FV"][0] for x in rows if x["d_FV"]])),
               "frac_mean": {k_: float(base.filter((pl.col("ev_kind") == k_) & pl.col("is_post"))["frac"].mean() or 0)
                             for k_ in ("forced", "voluntary", "pseudo31")}}
        out[world] = res
        C.log("R3", world, {k_: v for k_, v in res.items() if k_ != "reps"})
    return out


def r4_worlds(calls, ev, reps, rng, lam=0.5, pers_null=0.6, pers_plant=0.15) -> dict:
    g0 = R.loop_strata(calls, ev)
    p = L.panel(calls, ev.filter(pl.col("ev_kind").is_in(["forced", "pseudo31"])), -10, 10)
    p = p.join(g0.select("ev_id", "stratum"), on="ev_id")
    mid = calls.filter(pl.col("pos").is_between(11, 30)).group_by("agent").agg(pl.col("any_write").mean().alias("b"))
    p = p.join(mid, on="agent", how="left").with_columns(pl.col("b").fill_null(0.1))
    k = p["k"].to_numpy(); b = p["b"].to_numpy(); forced = (p["ev_kind"] == "forced").to_numpy()
    loop = (p["stratum"] == "loop").to_numpy()
    evid = p["ev_id"].to_numpy(); ev_u, ev_i = np.unique(evid, return_inverse=True)
    dip = np.where(forced & (k > 0), 1 - 0.6 * np.exp(-(np.maximum(k, 1) - 1) / 3.0), 1.0)
    out = {}
    for world in ("null", "planted"):
        rows = []
        for r in range(reps):
            u_e = rng.random(len(ev_u))[ev_i]
            pers = np.where(forced & (world == "planted"), pers_plant, pers_null)
            state = np.where(k < 0, loop, loop & (u_e < pers))
            pw = np.clip(b * np.where(state, lam, 1.0) * dip, 0, 1)
            w = rng.random(len(k)) < pw
            s = calls  # placeholder for schema
            pp = p.with_columns(pl.Series("any_write", w))
            g = pp.group_by("ev_id").agg(
                pl.col("ev_kind").first(), pl.col("cl").first(), pl.col("stratum").first(),
                pl.col("any_write").filter(pl.col("k") < 0).sum().alias("w_pre"), (pl.col("k") < 0).sum().alias("n_pre"),
                pl.col("any_write").filter(pl.col("k") > 0).sum().alias("w_post"), (pl.col("k") > 0).sum().alias("n_post"))
            st = R.lever_stats(g, B=200, seed=int(rng.integers(1e9)))
            rows.append({k_: st[k_] for k_ in ("E_loop", "E_free", "DDD", "logDDD")})
            del s
        res = {"reps": rows, "n": R.lever_stats(g, B=10)["n"]}
        for stat in ("DDD", "logDDD", "E_loop"):
            v = np.array([x[stat][0] for x in rows])
            res[f"{stat}_mean"] = float(v.mean()); res[f"{stat}_q95"] = float(np.quantile(v, 0.95))
            res[f"{stat}_cipos_rate"] = float(np.mean([x[stat][1] > 0 for x in rows]))
        out[world] = res
        C.log("R4", world, {k_: v for k_, v in res.items() if k_ != "reps"})
    # power of DDD > null q95 under the planted world
    q95 = out["null"]["DDD_q95"]
    out["planted"]["DDD_gt_nullq95_rate"] = float(np.mean([x["DDD"][0] > q95 for x in out["planted"]["reps"]]))
    out["null"]["DDD_gt_nullq95_rate"] = 0.05
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=40)
    ap.add_argument("--periods", default="G51,G38,G37")
    ap.add_argument("--only", default="r2,r3,r4")
    a = ap.parse_args()
    only = set(a.only.split(","))
    calls_all = pl.read_parquet(C.OUT / "calls.parquet")
    ev_all = pl.read_parquet(C.OUT / "events.parquet")
    obj = pl.read_parquet(OUTD / "objects.parquet")
    C.refuse_holdout(calls_all["pt_date"].unique().to_list(), "calls")
    path = OUTD / "synthetic.json"
    res = json.loads(path.read_text()) if path.exists() else {}
    for per in a.periods.split(","):
        t0 = time.time()
        rng = np.random.default_rng(abs(hash(per)) % 2 ** 31 if False else {"G51": 51, "G38": 38, "G37": 37}.get(per, 1))
        calls = calls_all.filter(pl.col("period") == per)
        ev = ev_all.filter(pl.col("period") == per)
        r = res.get(per, {})
        if "r2" in only:
            r["r2"] = r2_worlds(R.sawtooth_calls(calls), a.reps, rng)
        if "r3" in only:
            r["r3"] = r3_worlds(calls, ev, obj, max(10, a.reps // 2), rng)
        if "r4" in only:
            r["r4"] = r4_worlds(calls, ev, a.reps, rng)
        res[per] = r
        path.write_text(json.dumps(res, indent=1, default=float))
        C.log(per, "done", f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
