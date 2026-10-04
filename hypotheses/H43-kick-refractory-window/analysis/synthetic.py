"""H43 synthetic validation (axis F): a call-level kicked renewal agent with planted refractoriness, sampled like the
village and analyzed with the identical estimator (h43lib.analyze_class).

Agent (per agent-day): active task episodes (busy-loop calls every ~27 s, lognormal episode length, median 12 min)
alternate with PAUSE chains (declared durations lognormal, median 4 min). At each gate (pause expiry) the agent escapes
with probability sigmoid(b0 + shift - b1 ln(1 + age/5 min) + sum_k beta_c u r_k) over kicks read in the last 15 min
(H16 aging; base 0.15 at age 0, b1 = 0.8; H04/H08 response window). A kick read at an active call raises the chance that this call talks by
gamma_c u r_k (a reply). Kicks are read at the first call after they arrive (DQ1 visibility rule).
Kick schedules:
  N  nudger policy: fires at agents idle >= 10 min, at most once per 15 min per agent (the real nudger floor), p 0.012/min
     ("policy"); or replays real G51 nudge receipt times ("replay")
  A, H  replay of real receipt times and counts from a random real agent-day (G51 before 08-21, or G38)
Planted variants (r_k = recovery factor of kick k):
  null        r = 1
  time        r = 1 - exp(-(t - t_last_effective_read_c)/tau)      (clock from the last effective kick of the same class)
  time_any    r = 1 - exp(-(t - t_last_read_c)/tau)                (habituation: every kick of the class resets it)
  episode     r = 0 while the agent is inside an episode launched by an effective kick, else 1
  frailty     r = 1, but per agent-day responsiveness u in {0.15, 1.85} and baseline shift ~ N(0, 0.6): the nudger
              re-fires on non-responders (selection on non-response)
Usage:  uv run python hypotheses/H43-kick-refractory-window/analysis/synthetic.py [--reps 6] [--quick]
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import bisect  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
import zlib  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h43lib as L  # noqa: E402

SYN = L.OUT / "synthetic"
SCALES = {"G51": dict(n_agents=24, n_days=30, T_day=300, sched="G51"),
          "G38": dict(n_agents=12, n_days=17, T_day=240, sched="G38"),
          "tiny": dict(n_agents=8, n_days=6, T_day=240, sched="G38"),
          "big": dict(n_agents=40, n_days=45, T_day=300, sched="G51")}
BETA = {"N": 0.9, "A": 0.3, "H": 0.6}
GAMMA = {"N": 0.05, "A": 0.25, "H": 0.15}
TAU = 30.0 * 60
NUDGE_P = 0.012         # per idle minute after 10 min: ~250 isolated primers at G51 scale (real G51 before 08-21: 302)


def schedules(src: str) -> list[dict]:
    """Real receipt schedules per agent-day: offsets (s) from the agent-day's first call, with counts per class."""
    path = SYN / f"schedules_{src}.parquet"
    if not path.exists():
        c = pl.read_parquet(L.OUT / "calls.parquet")
        c = c.filter((pl.col("goal_no") == 51) & (pl.col("pt_date") < "2026-08-21")) if src == "G51" else \
            c.filter(pl.col("goal_no") == 38)
        c = c.sort("agent", "pt_date", "t_call").with_columns(
            (pl.col("t_call") - pl.col("t_call").min().over("agent", "pt_date")).alias("off"))
        s = c.filter((pl.col("nA") + pl.col("nH") + pl.col("nN")) > 0).select("agent", "pt_date", "off", "nA", "nH", "nN")
        SYN.mkdir(parents=True, exist_ok=True)
        s.write_parquet(path)
    s = pl.read_parquet(path)
    out = []
    for (_, _), g in s.group_by(["agent", "pt_date"]):
        out.append({cl: [(o, n) for o, n in zip(g["off"].to_list(), g[f"n{cl}"].to_list()) if n > 0] for cl in ("A", "H", "N")})
    return out


def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))


def simulate(variant: str, scale: str, seed: int, n_mode: str = "policy") -> tuple:
    rng = np.random.default_rng(seed)
    sc = SCALES[scale]
    sched = schedules(sc["sched"])
    T = sc["T_day"] * 60.0
    b0, b1 = math.log(0.15 / 0.85), 0.8
    rows = {k: [] for k in ("agent", "day", "t", "tend", "kind", "talk", "nN", "nH", "nA")}
    writes = []
    for day in range(sc["n_days"]):
        t0 = 1.7e9 + day * 86400.0
        for a in range(sc["n_agents"]):
            rep = sched[rng.integers(len(sched))]
            msgs = []
            for cl in ("A", "H") + (("N",) if n_mode == "replay" else ()):
                for off, cnt in rep[cl]:
                    for _ in range(int(cnt)):
                        msgs.append((t0 + off - rng.uniform(1, 20), cl))
            msgs.sort()
            mt = [m[0] for m in msgs]
            u, shift = 1.0, 0.0
            if variant == "frailty":
                u = 0.15 if rng.random() < 0.5 else 1.85
                shift = rng.normal(0, 0.6)
            t = t0 + rng.uniform(0, 300)
            mode = "active"
            ep_end = t + rng.lognormal(math.log(12 * 60), 0.8)
            launched_eff = False
            last_eff = {"N": -1e18, "H": -1e18, "A": -1e18}
            last_any = {"N": -1e18, "H": -1e18, "A": -1e18}
            recent = []          # (t_read, cls, r)
            ptr = 0
            idle_since = t
            last_nudge = -1e18
            gate = False
            while t < t0 + T:
                j = bisect.bisect_left(mt, t, lo=ptr)
                cnt = {"N": 0, "H": 0, "A": 0}
                reads = msgs[ptr:j]
                ptr = j
                rr = []
                for _, cl in reads:
                    cnt[cl] += 1
                    if variant == "time":
                        r = 1 - math.exp(-(t - last_eff[cl]) / TAU)
                    elif variant == "time_any":
                        r = 1 - math.exp(-(t - last_any[cl]) / TAU)
                    elif variant == "episode":
                        r = 0.0 if (mode == "active" and launched_eff) else 1.0
                    else:
                        r = 1.0
                    rr.append((cl, r))
                for _, cl in reads:
                    last_any[cl] = t
                    recent = [x for x in recent if t - x[0] <= 900] + [(t, cl, r) for cl, r in rr]
                if mode == "idle" and gate:
                    age = t - idle_since
                    lg = b0 + shift - b1 * math.log1p(age / 300.0)
                    kicks = [x for x in recent if t - x[0] <= 900]
                    lg += sum(BETA[cl] * u * r for _, cl, r in kicks)
                    if rng.random() < sigmoid(lg):
                        mode = "active"
                        ep_end = t + rng.lognormal(math.log(12 * 60), 0.8)
                        eff = [x for x in kicks if x[2] > 0]
                        launched_eff = bool(eff)
                        for x in eff:
                            last_eff[x[1]] = max(last_eff[x[1]], x[0])
                if mode == "active":
                    p_talk = 0.04 + sum(GAMMA[cl] * u * r for cl, r in rr)
                    talk = rng.random() < min(p_talk, 0.95)
                    dur = max(3.0, rng.exponential(25.0))
                    for k, v in (("agent", a), ("day", day), ("t", t), ("tend", t + dur), ("kind", 1 if talk else 0),
                                 ("talk", talk), ("nN", cnt["N"]), ("nH", cnt["H"]), ("nA", cnt["A"])):
                        rows[k].append(v)
                    if rng.random() < 0.01:
                        writes.append((a, t + dur))
                    t = t + dur + 1.7
                    gate = False
                    if t >= ep_end:
                        mode = "idle"
                        idle_since = t
                        launched_eff = False
                    continue
                # idle: log a pause call
                d = rng.lognormal(math.log(240.0), 0.7)
                for k, v in (("agent", a), ("day", day), ("t", t), ("tend", t + d), ("kind", 2), ("talk", False),
                             ("nN", cnt["N"]), ("nH", cnt["H"]), ("nA", cnt["A"])):
                    rows[k].append(v)
                if n_mode == "policy":
                    m = t
                    while m < t + d:
                        if (m - idle_since >= 600) and (m - last_nudge >= 900) and rng.random() < NUDGE_P:
                            tm = m + rng.uniform(0, 60)
                            if tm < t + d:
                                bisect.insort(msgs, (tm, "N"))
                                mt = [x[0] for x in msgs]
                                last_nudge = tm
                        m += 60
                t = t + d + 3.0
                gate = True
    df = pl.DataFrame(rows).with_columns(pl.col("agent").cast(pl.Int8))
    dates = [f"2030-01-{d + 1:02d}" if d < 31 else f"2030-02-{d - 30:02d}" for d in range(sc["n_days"])]
    df = df.with_columns(pl.col("day").map_elements(lambda d: dates[d], return_dtype=pl.Utf8).alias("pt_date"))
    calls = df.with_columns(
        pl.int_range(pl.len()).cast(pl.Int32).alias("turn_id"), pl.lit("S").alias("unit_id"),
        pl.col("kind").cast(pl.Int8).alias("kind_c"), pl.lit(False).alias("first_of_day"),
        pl.col("t").alias("t_call"), pl.col("tend").alias("t_end"),
        pl.col("nN").cast(pl.Int16), pl.col("nH").cast(pl.Int16), pl.col("nA").cast(pl.Int16))
    calls = calls.sort("agent", "pt_date", "t_call").with_columns(
        (pl.col("t_call") == pl.col("t_call").min().over("agent", "pt_date")).alias("first_of_day"))
    cal = pl.DataFrame({"pt_date": dates, "win_start": [1.7e9 + d * 86400.0 for d in range(sc["n_days"])],
                        "win_end": [1.7e9 + d * 86400.0 + T for d in range(sc["n_days"])]})
    states = states_from_calls(calls, cal, sc["T_day"])
    wr = pl.DataFrame({"agent": [w[0] for w in writes], "t": [w[1] for w in writes]}).with_columns(pl.col("agent").cast(pl.Int8)) \
        if writes else pl.DataFrame({"agent": [], "t": []}, schema={"agent": pl.Int8, "t": pl.Float64})
    return calls, states, wr, cal


def states_from_calls(calls: pl.DataFrame, cal: pl.DataFrame, T_day: int) -> pl.DataFrame:
    c = calls.join(cal.select("pt_date", "win_start"), on="pt_date").with_columns(
        ((pl.col("t_call") - pl.col("win_start")) // 60).cast(pl.Int64).alias("m0"),
        ((pl.col("t_end") - pl.col("win_start")) // 60).cast(pl.Int64).clip(None, T_day).alias("m1"),
        pl.when(pl.col("talk")).then(1).when(pl.col("kind_c") == 2).then(2).otherwise(0).alias("code"))
    c = c.with_columns(pl.when(pl.col("code") == 2).then(3).when(pl.col("code") == 1).then(1).otherwise(2).alias("prio"))
    ex = c.with_columns(pl.int_ranges("m0", pl.col("m1") + 1).alias("minute")).explode("minute")
    st = (ex.group_by("pt_date", "agent", "minute").agg(pl.col("prio").min().alias("prio"))
          .with_columns(pl.col("prio").replace_strict({1: 1, 2: 0, 3: 2}).alias("lump4_min")))
    span = c.group_by("pt_date", "agent").agg(pl.col("m0").min().alias("lo"), pl.col("m1").max().alias("hi"))
    grid = span.with_columns(pl.int_ranges("lo", pl.col("hi") + 1).alias("minute")).explode("minute")
    st = (grid.join(st, on=["pt_date", "agent", "minute"], how="left")
          .with_columns(pl.col("lump4_min").fill_null(2).cast(pl.Int8), pl.lit(True).alias("in_span"),
                        pl.lit(True).alias("present"), pl.col("minute").cast(pl.Int16))
          .select("pt_date", "minute", "agent", "lump4_min", "in_span", "present"))
    return st


def summarize_run(res: dict) -> dict:
    """Compact per-class summary for the validation table."""
    out = {}
    for cl, r in res.items():
        o = r.get("outcomes", {}).get(L.PRIMARY[cl], {})
        s = {"n_primers": r.get("n_primers"), "n_second": r.get("n_second"), "L_median": r.get("L_median"),
             "E1": o.get("E1", {}), "E1_positive": o.get("E1_positive"),
             "R_bins": {k: (v.get("R", {}).get("est"), v.get("R", {}).get("lo"), v.get("R", {}).get("hi"), v.get("n"))
                        for k, v in o.get("E2_bins", {}).items() if v.get("n", 0) > 0},
             "fit": o.get("fit"), "R_short": o.get("R_short"), "R_long": o.get("R_long"),
             "by_status": {k: (v["R"]["est"], v["R"]["lo"], v["R"]["hi"], v["n"]) for k, v in o.get("by_status", {}).items()},
             "batched": o.get("batched"),
             "R_pool": {k: (v["R"]["est"], v["R"]["lo"], v["R"]["hi"], v["n"]) for k, v in o.get("R_pool", {}).items()}}
        if cl in ("A", "H"):
            o1 = r.get("outcomes", {}).get("O1", {})
            s["O1_by_status"] = {k: (v["R"]["est"], v["R"]["lo"], v["R"]["hi"], v["n"]) for k, v in o1.get("by_status", {}).items()}
            s["O1_E1"] = o1.get("E1", {})
        if cl == "N":
            o2 = r.get("outcomes", {}).get("O2", {})
            s["O2_by_status"] = {k: (v["R"]["est"], v["R"]["lo"], v["R"]["hi"], v["n"]) for k, v in o2.get("by_status", {}).items()}
        out[cl] = s
    return out


def one(args):
    variant, scale, rep, n_mode, B = args
    seed = L.SEED + 1000 * rep + zlib.crc32(f"{variant}|{scale}|{n_mode}".encode()) % 997
    t1 = time.time()
    calls, states, writes, cal = simulate(variant, scale, seed, n_mode)
    P = L.Prep(calls, states, writes, cal)
    rng = np.random.default_rng(seed + 1)
    draws = L.day_draws(len(P.days), B, rng)
    res = {}
    for cl in ("N", "A", "H"):
        res[cl] = L.analyze_class(P, cl, rng, B=B, outcomes=("O1", "O2"), draws=draws)
    return {"variant": variant, "scale": scale, "rep": rep, "n_mode": n_mode, "seed": seed, "n_calls": calls.height,
            "secs": round(time.time() - t1, 1), "summary": summarize_run(res)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=6)
    ap.add_argument("--B", type=int, default=200)
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--variants", default="null,time,time_any,episode,frailty")
    ap.add_argument("--scales", default="G51,G38,big")
    ap.add_argument("--out", default="synthetic_results.json")
    a = ap.parse_args()
    variants = a.variants.split(",")
    jobs = []
    plan = {"G51": a.reps, "G38": max(2, a.reps * 2 // 3), "big": max(2, a.reps // 2)}
    for sc in a.scales.split(","):
        vs = variants if sc != "big" else [v for v in variants if v in ("null", "time_any", "episode", "frailty")]
        for v in vs:
            for r in range(plan.get(sc, a.reps)):
                jobs.append((v, sc, r, "policy", a.B))
    if "G51" in a.scales:
        for v in ("null", "time_any"):
            for r in range(2):
                jobs.append((v, "G51", r, "replay", a.B))
    if a.quick:
        jobs = jobs[:1]
    t0 = time.time()
    results = []
    if a.workers > 1:
        with ProcessPoolExecutor(max_workers=min(2, a.workers)) as ex:
            for res in ex.map(one, jobs):
                results.append(res)
                print(res["variant"], res["scale"], res["rep"], res["n_mode"], res["n_calls"], res["secs"], flush=True)
    else:
        for j in jobs:
            res = one(j)
            results.append(res)
            print(res["variant"], res["scale"], res["rep"], res["n_mode"], res["n_calls"], res["secs"], flush=True)
    L.jdump({"built_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "git_commit": L.git_commit(),
             "params": {"BETA": BETA, "GAMMA": GAMMA, "TAU_min": TAU / 60, "scales": SCALES, "B": a.B},
             "runs": results, "elapsed_s": round(time.time() - t0, 1)}, SYN / a.out)
    print("done", round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
