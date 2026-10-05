"""H67 round-2 synthetic validation (before real data), on real call grids of non-reserved units.

  R3  units 27, 41, 51e; worlds null / burst / g015 / g030 (hop-1, h67lib.simulate): rung L1 (H50 pair RD), L4, the
      first stage (L6) and L9 (H67 main) against the planted truth.
  R4  units 27, 41, 51e; worlds hop1 (g 0.15), decay (J(1,.6,.4,.2,0), G5 0.22), plateau (J(1,.8,.8,.8,.8), G5 0.33),
      null, burst: the lagged in-flight gain G_1..G_5 and the round-1 uncorrected g3.
  R1  regime-I units 4c, 19a, 27; worlds chat (g_chat 0.15), null, burst, chat_err (start-time error): the chat-clock
      g_chat and the round-1 hop-1 estimator.
Output: data/processed/H67-lagged-criticality-dial/round2/synthetic/{r3,r4,r1}.parquet + summary.json

    uv run python hypotheses/H67-lagged-criticality-dial/analysis/r2_synthetic.py [--reps 8] [--workers 2] [--only r3,r4,r1]
"""
from __future__ import annotations

import argparse
import json
import zlib
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import polars as pl

import h67lib as L
import r2lib as R

OUT = R.R2 / "synthetic"
W50 = dict(pl.read_parquet(L.ROOT / "data/processed/H50-field-vs-coupling-transfer-lag/unit_table.parquet")
           .select("unit", "W").iter_rows())
U3 = ["27", "41", "51e"]
U1 = ["4c", "19a", "27"]
R3_WORLDS = [("null", 0.0, False), ("burst", 0.0, True), ("g015", 0.15, False), ("g030", 0.30, False)]
R4_WORLDS = [("hop1", [1.0], 0.15, False), ("decay", [1, .6, .4, .2, 0], 0.22, False),
             ("plateau", [1, .8, .8, .8, .8], 0.33, False), ("null", [0.0], 0.0, False), ("burst", [0.0], 0.0, True)]
R1_WORLDS = [("chat", 0.15, False, False), ("null", 0.0, False, False), ("burst", 0.0, True, False),
             ("chat_err", 0.15, False, True)]


def load(u):
    return (pl.read_parquet(L.OUT / "units" / f"{u}.parquet"), pl.read_parquet(L.OUT / "msgs" / f"{u}.parquet"))


def design_rbar(c, m, chat=False):
    d = R.chat_counts(c, m) if chat else L.counts(c, m)
    rows = L._rows(d, True)
    win = rows.group_by("day").agg(pl.col("ap_lo").first(), pl.col("ap_hi").first())
    n = m.join(win, on="day").filter((pl.col("t") >= pl.col("ap_lo")) & (pl.col("t") <= pl.col("ap_hi"))).height
    return float(rows["R_all"].sum()) / max(n, 1)


def seed_of(*a):
    return zlib.crc32("|".join(map(str, a)).encode())


def job_r3(args):
    u, world, g, burst, rep, rbar = args
    c, _ = load(u)
    rng = np.random.default_rng(seed_of("r3", u, world, rep))
    sim, m = L.simulate(c, g, rbar, rng, burst=burst)
    d = L.all_counts(sim, m)
    r9 = L.fit(d, m, "main", True, B=100, seed=rep)
    out = {"unit": u, "world": world, "rep": rep}
    if not r9.get("ok"):
        return out
    gm = r9["rbar"] * r9["mbar"]
    out.update({"gmul": gm, "g_true": (g / rbar) * gm, "g_L9": r9["g"], "g_L9_lo": r9.get("g_lo"),
                "g_L9_hi": r9.get("g_hi")})
    w_bar = float(L._rows(d, True)["w"].median())
    for tag, kw in (("L1", dict(W=W50[u], trim=False, demean=False, placebo=True)),
                    ("L2", dict(W=W50[u], trim=True, demean=False, placebo=True)),
                    ("L3", dict(W=w_bar, trim=True, demean=False, placebo=True)),
                    ("L4", dict(W=w_bar, trim=True, demean=True, placebo=True)),
                    ("L4W", dict(W=W50[u], trim=True, demean=True, placebo=True)),
                    ("L5", dict(W=w_bar, trim=True, demean=True, placebo=False)),
                    ("L6fs", dict(W=w_bar, trim=True, demean=True, placebo=True, outcome="R_all"))):
        r = R.pair_rd(d, m, B=100, seed=rep, **kw)
        if r.get("ok"):
            out[f"J_{tag}"] = r["J"]
            out[f"J_{tag}_lo"], out[f"J_{tag}_hi"] = r["J_lo"], r["J_hi"]
            out[f"g_{tag}"] = r["J"] * gm
    if out.get("J_L6fs"):
        out["g_L6"] = out.get("J_L4", np.nan) / out["J_L6fs"] * gm
    return out


def job_r4(args):
    u, world, shape, G5, burst, rep, rbar = args
    c, _ = load(u)
    rng = np.random.default_rng(seed_of("r4", u, world, rep))
    J1 = G5 / sum(shape) / rbar if G5 > 0 else 0.0
    sim, m = R.simulate_kernel(c, [J1 * s for s in shape], rng, burst=burst)
    d = L.all_counts(sim, m)
    dl = R.add_lags(R.hw_counts(d, m))
    r = R.multihop(d, m, B=100, seed=rep, dl=dl)
    out = {"unit": u, "world": world, "rep": rep}
    if not r.get("ok"):
        return out
    out.update({k: v for k, v in r.items() if k.startswith(("G", "delta", "D")) or k == "gmul"})
    rn = R.multihop(d, m, B=0, seed=rep, dl=dl, slopes=False)
    out.update({f"{k}_noslope": rn.get(k, np.nan) for k in ("G1", "G3", "G5")})
    out["G5_true"] = J1 * sum(shape) * r["gmul"]
    out["G1_true"] = J1 * shape[0] * r["gmul"]
    r1 = L.fit(d, m, "main", True, B=0, seed=rep)
    out["g_r1"], out["g3_r1"] = r1.get("g", np.nan), r1.get("g3", np.nan)
    return out


def job_r1(args):
    u, world, g, burst, err, rep, rbar_chat, mbar = args
    c, _ = load(u)
    rng = np.random.default_rng(seed_of("r1", u, world, rep))
    J = g / rbar_chat if g > 0 else 0.0
    sim, m = R.simulate_chat(c, J, rng, burst=burst, start_err=err)
    dc = R.chat_counts(sim, m)
    r = L.fit(dc, m, "main", True, B=100, seed=rep)
    out = {"unit": u, "world": world, "rep": rep}
    if not r.get("ok"):
        return out
    out.update({"J1": r["J1"], "J1_lo": r.get("J1_lo"), "J1_hi": r.get("J1_hi"), "rbar_chat": r["rbar"]})
    out["g_chat"] = r["J1"] * r["rbar"]          # one message per talk call in the simulator
    out["g_chat_lo"] = r.get("J1_lo", np.nan) * r["rbar"]
    out["g_chat_hi"] = r.get("J1_hi", np.nan) * r["rbar"]
    out["g_true"] = J * r["rbar"]
    dh = dc.filter(pl.col("start_conf").cast(pl.String) == "high")
    rh = L.fit(dh, m, "main", True, B=100, seed=rep)
    if rh.get("ok"):
        out["g_chat_logged"] = rh["J1"] * r["rbar"]
        out["g_chat_logged_lo"], out["g_chat_logged_hi"] = rh.get("J1_lo", np.nan) * r["rbar"], rh.get("J1_hi", np.nan) * r["rbar"]
    ra = L.fit(dc, m, "all", True, B=0, seed=rep)
    out["g_chat_all"] = ra.get("J1", np.nan) * r["rbar"]
    d = L.all_counts(sim, m)
    r1 = L.fit(d, m, "main", True, B=0, seed=rep)
    out["g_hop1_allcalls"] = r1.get("g", np.nan)
    return out


def summarise(df: pl.DataFrame, est: str, truth: str, lo: str | None, hi: str | None, worlds_pos, worlds_null):
    s = {}
    for w in worlds_pos:
        x = df.filter((pl.col("world") == w) & pl.col(est).is_not_null())
        rel = (x[est] - x[truth]) / x[truth]
        d = {"median_rel_err": float(rel.median()), "median_est": float(x[est].median()),
             "median_truth": float(x[truth].median()), "n": x.height,
             "by_unit": {k: float(v) for k, v in x.with_columns(rel.alias("re")).group_by("unit")
                         .agg(pl.col("re").median()).iter_rows()}}
        if lo and hi and lo in x.columns:
            d["coverage"] = float(((x[lo] <= x[truth]) & (x[hi] >= x[truth])).mean())
        s[w] = d
    for w in worlds_null:
        x = df.filter((pl.col("world") == w) & pl.col(est).is_not_null())
        d = {"median_est": float(x[est].median()), "n": x.height}
        if lo and hi and lo in x.columns:
            d["ci_excl0"] = float(((x[lo] > 0) | (x[hi] < 0)).mean())
        s[w] = d
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=8)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--only", default="r3,r4,r1")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    todo = a.only.split(",")
    sp = OUT / "summary.json"
    summ = json.loads(sp.read_text()) if sp.exists() else {}
    with ProcessPoolExecutor(min(a.workers, 2)) as ex:
        if "r3" in todo:
            rb = {u: design_rbar(*load(u)) for u in U3}
            jobs = [(u, w, g, b, k, rb[u]) for u in U3 for (w, g, b) in R3_WORLDS for k in range(a.reps)]
            df = pl.DataFrame(list(ex.map(job_r3, jobs)), infer_schema_length=None)
            df.write_parquet(OUT / "r3.parquet")
            summ["r3"] = {"design_rbar": rb}
            for est, lo, hi in (("g_L9", "g_L9_lo", "g_L9_hi"), ("g_L1", None, None), ("g_L2", None, None),
                                ("g_L3", None, None), ("g_L4", None, None), ("g_L4W", None, None),
                                ("g_L5", None, None), ("g_L6", None, None)):
                summ["r3"][est] = summarise(df, est, "g_true", lo, hi, ["g015", "g030"], ["null", "burst"])
            for est in ("J_L1", "J_L4"):
                x = df.filter(pl.col("world").is_in(["null", "burst"]))
                summ["r3"][est + "_ci_excl0_null"] = float(((x[est + "_lo"] > 0) | (x[est + "_hi"] < 0)).mean())
            summ["r3"]["first_stage_median"] = {w: float(df.filter(pl.col("world") == w)["J_L6fs"].median())
                                                for w, *_ in R3_WORLDS}
            print(json.dumps(summ["r3"], indent=1), flush=True)
        if "r4" in todo:
            rb = {u: design_rbar(*load(u)) for u in U3}
            jobs = [(u, w, sh, G5, b, k, rb[u]) for u in U3 for (w, sh, G5, b) in R4_WORLDS for k in range(a.reps)]
            df = pl.DataFrame(list(ex.map(job_r4, jobs)), infer_schema_length=None)
            df.write_parquet(OUT / "r4.parquet")
            summ["r4"] = {"design_rbar": rb,
                          "G5": summarise(df, "G5", "G5_true", "G5_lo", "G5_hi", ["hop1", "decay", "plateau"],
                                          ["null", "burst"]),
                          "G1": summarise(df, "G1", "G1_true", "G1_lo", "G1_hi", ["hop1", "decay", "plateau"],
                                          ["null", "burst"]),
                          "g3_r1_median": {w: float(df.filter(pl.col("world") == w)["g3_r1"].median())
                                           for w, *_ in R4_WORLDS},
                          "G5_noslope_median": {w: float(df.filter(pl.col("world") == w)["G5_noslope"].median())
                                                for w, *_ in R4_WORLDS},
                          "G5_true_median": {w: float(df.filter(pl.col("world") == w)["G5_true"].median())
                                             for w, *_ in R4_WORLDS},
                          "G3_median": {w: float(df.filter(pl.col("world") == w)["G3"].median())
                                        for w, *_ in R4_WORLDS}}
            print(json.dumps(summ["r4"], indent=1), flush=True)
        if "r1" in todo:
            rb = {u: design_rbar(*load(u), chat=True) for u in U1}
            jobs = [(u, w, g, b, e, k, rb[u], 1.0) for u in U1 for (w, g, b, e) in R1_WORLDS for k in range(a.reps)]
            df = pl.DataFrame(list(ex.map(job_r1, jobs)), infer_schema_length=None)
            df.write_parquet(OUT / "r1.parquet")
            summ["r1"] = {"design_rbar_chat": rb,
                          "g_chat": summarise(df, "g_chat", "g_true", "g_chat_lo", "g_chat_hi", ["chat", "chat_err"],
                                              ["null", "burst"]),
                          "g_chat_all": summarise(df, "g_chat_all", "g_true", None, None, ["chat", "chat_err"],
                                                  ["null", "burst"]),
                          "g_chat_logged": summarise(df, "g_chat_logged", "g_true", "g_chat_logged_lo",
                                                     "g_chat_logged_hi", ["chat", "chat_err"], ["null", "burst"]),
                          "hop1_allcalls_over_truth_chat": float(
                              (df.filter(pl.col("world") == "chat")["g_hop1_allcalls"]
                               / df.filter(pl.col("world") == "chat")["g_true"]).median()),
                          "hop1_allcalls_median": {w: float(df.filter(pl.col("world") == w)["g_hop1_allcalls"]
                                                            .median()) for w, *_ in R1_WORLDS}}
            print(json.dumps(summ["r1"], indent=1), flush=True)
    sp.write_text(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
