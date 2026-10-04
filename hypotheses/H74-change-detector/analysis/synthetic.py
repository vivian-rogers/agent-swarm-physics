"""H74 synthetic validation (axis F): daily channel tables at real counts with planted steps, scored by the same
functions as the real data (h74lib). Card, "Synthetic validation".

Step types (each planted 3 times per run, >= 7 days apart, persistent unless noted):
  schema     one turn_action signature (5% share) renamed for every agent
  mix3/mix5  a synchronous shift of one per-call number (3 or 5 within-agent SD) for every agent
  oracle     search answers switch bullet marker ('*   ' -> '- ')
  drive      bookends stop, or the start time moves +30 min
  content    a goal step (R1 spike on day 0)
  roster     3 agents of a new provider join (own API signature, own mix)        [nuisance]
  goalmix    a goal step plus a talk-share shift in half the agents             [nuisance]
Run: uv run python hypotheses/H74-change-detector/analysis/synthetic.py [--runs 20]
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h74lib as L  # noqa: E402

ROOT = HERE.parents[2]
OUT = ROOT / "data/processed/H74-change-detector"
TYPES = ["schema", "mix3", "mix5", "oracle", "drive", "content", "roster", "goalmix"]
KINDS = ["cu_action", "talk", "pause", "wait", "consolidate", "search", "session_start", "session_stop", "room_move"]
BASE_SH = np.array([0.62, 0.10, 0.12, 0.02, 0.05, 0.01, 0.0005, 0.0005, 0.01])
# per-call numbers: (mean, day-to-day within-agent SD); SDs set to the real non-holdout medians (rec_per_call at its floor)
NUM = {"rec_per_call": (1.1, 0.05), "log_turnaround": (2.5, 0.13), "log_prompt": (10.5, 0.10), "log_out": (5.0, 0.11),
       "log_reason": (6.0, 0.1), "cache_share": (0.8, 0.02), "tok_null_share": (0.4, 0.02), "infra_err_share": (0.01, 0.004),
       "bash_share": (0.5, 0.04)}


def marginals():
    p = OUT / "agent_day_features.parquet"
    if p.exists():
        a = pl.read_parquet(p)
        nc = a["n_calls"].to_numpy()
        s = pl.read_parquet(OUT / "search_daily.parquet")["n_search"].to_numpy()
        return {"calls_logmu": float(np.log(np.median(nc))), "calls_logsd": float(np.std(np.log(nc + 1))),
                "search_mu": float(np.median(s))}
    return {"calls_logmu": np.log(600), "calls_logsd": 0.9, "search_mu": 8.0}


def run(seed, T=200, marg=None):
    rng = np.random.default_rng(seed)
    marg = marg or marginals()
    days = [f"s{t:03d}" for t in range(T)]
    # events
    centers = list(range(14, T - 5, 7))[: 3 * len(TYPES)]
    types = list(np.repeat(TYPES, 3)[: len(centers)])
    rng.shuffle(types)
    ev = dict(zip(centers, types))
    # roster path
    agents = list(range(6))
    joins = {c: [] for c in centers}
    nxt = 6
    roster_on = {a: 0 for a in agents}
    provider = {a: int(rng.integers(0, 3)) for a in agents}
    for t in sorted(rng.choice(np.arange(20, T - 10), 8, replace=False)):
        if t in ev:
            continue
        k = int(rng.integers(1, 3))
        for _ in range(k):
            roster_on[nxt] = int(t); provider[nxt] = int(rng.integers(0, 3)); nxt += 1
    for c, ty in ev.items():
        if ty == "roster":
            for _ in range(3):
                roster_on[nxt] = c; provider[nxt] = 3; nxt += 1
    A = list(roster_on)
    p_ag = {a: rng.dirichlet(80 * BASE_SH + 0.05) for a in A}
    mu_ag = {a: {f: m + rng.normal(0, 4 * s) for f, (m, s) in NUM.items()} for a in A}
    shifts = {a: np.ones(len(KINDS)) for a in A}
    num_shift = {a: {f: 0.0 for f in NUM} for a in A}
    drift = {a: {f: 0.0 for f in NUM} for a in A}
    rows_agd, rows_day, rows_s, rows_sig = [], [], [], []
    bookends, start_tod, r1_mu = 2, 600.0, 0.04
    star3, dash = 4.0, 0.3
    renamed = False
    newprov = set()
    for t in range(T):
        ty = ev.get(t)
        if ty in ("mix3", "mix5"):
            f = str(rng.choice(["rec_per_call", "log_prompt", "log_turnaround", "log_out"]))
            k = 3.0 if ty == "mix3" else 5.0
            for a in A:
                num_shift[a][f] += k * NUM[f][1] * (1 if rng.random() < 0.5 or True else -1)
        if ty == "goalmix":
            for a in rng.choice(A, len(A) // 2, replace=False):
                shifts[a][KINDS.index("talk")] *= 1.3
        if ty == "drive":
            if rng.random() < 0.5:
                bookends = 2 - bookends
            else:
                start_tod += 30
        if ty == "oracle":
            star3, dash = dash, star3
        if ty == "schema":
            renamed = not renamed
        present = [a for a in A if roster_on[a] <= t]
        sig_counts = {}
        for a in present:
            n = int(np.exp(rng.normal(marg["calls_logmu"], 0.5)))
            p = p_ag[a] * shifts[a]
            p = p / p.sum()
            pdaily = rng.dirichlet(400 * p + 1e-3)
            cnt = rng.multinomial(n, pdaily)
            r = {"agent": a, "pt_date": days[t], "n_calls": n}
            r.update({f"sh_{k}": c / n for k, c in zip(KINDS, cnt)})
            for f, (m, s) in NUM.items():
                drift[a][f] += rng.normal(0, 0.1 * s)   # slow random-walk drift
                r[f] = mu_ag[a][f] + num_shift[a][f] + drift[a][f] + rng.normal(0, s)
            rows_agd.append(r)
            # signatures: turn_action family (10 sigs), env (3), api by provider; ev family (12)
            pa = np.array([0.3, 0.2, 0.15, 0.1, 0.05, 0.05, 0.05, 0.04, 0.03, 0.03])
            ca = rng.multinomial(n, pa)
            for k, c in enumerate(ca):
                name = f"A{k}" + ("x" if (k == 4 and renamed) else "")
                sig_counts.setdefault(("turn_action", name), {}).setdefault(a, 0)
                sig_counts[("turn_action", name)][a] += int(c)
            for k, c in enumerate(rng.multinomial(n, [0.6, 0.3, 0.1])):
                sig_counts.setdefault(("turn_env", f"E{k}"), {}).setdefault(a, 0)
                sig_counts[("turn_env", f"E{k}")][a] += int(c)
            sig_counts.setdefault(("turn_api", f"P{provider[a]}"), {}).setdefault(a, 0)
            sig_counts[("turn_api", f"P{provider[a]}")][a] += n
            for k, c in enumerate(rng.multinomial(max(n // 5, 1), np.r_[np.full(10, 0.098), 0.01, 0.01])):
                sig_counts.setdefault(("ev:X", f"V{k}"), {}).setdefault(a, 0)
                sig_counts[("ev:X", f"V{k}")][a] += int(c)
        # rare one-agent signatures
        if rng.random() < 0.2 and present:
            a = int(rng.choice(present))
            sig_counts[("ev:Y", f"R{t}")] = {a: int(rng.integers(1, 12))}
        for (rt, sg), ags in sig_counts.items():
            ags = {a: c for a, c in ags.items() if c > 0}
            if ags:
                rows_sig.append({"pt_date": days[t], "rtype": rt, "sig": sg, "n": sum(ags.values()), "n_agents": len(ags),
                                 "agents": sorted(ags)})
        # day features
        r1 = rng.gamma(16, r1_mu / 16)
        if ty in ("content", "goalmix"):
            r1 = 0.15 + rng.normal(0, 0.02)
        rows_day.append({"pt_date": days[t], "start_tod_min": start_tod + rng.normal(0, 3), "window_min": 240 + rng.normal(0, 10),
                         "documented_hours": 4.0, "n_bookends": bookends, "n_nudges": rng.poisson(20), "n_human": rng.poisson(5),
                         "js_share": rng.beta(2, 60), "start_iqr_min": abs(rng.normal(3, 1)), "n_present": len(present),
                         "r1_bge": r1, "r1_gte": r1 * (1 + rng.normal(0, 0.1))})
        ns = rng.poisson(marg["search_mu"])
        if ns >= 1:
            s = {"pt_date": days[t], "n_search": ns}
            for f in L.O_FEATURES:
                s[f] = float(np.median(rng.poisson(5, ns)))
            s["f_b_star3"] = float(np.median(rng.poisson(star3, ns)))
            s["f_b_dash"] = float(np.median(rng.poisson(dash, ns)))
            s["f_chars"] = float(np.median(rng.normal(1500, 300, ns)))
            s["f_nonascii"] = float(np.median(rng.beta(2, 400, ns)))
            rows_s.append(s)
    agd = pl.DataFrame(rows_agd)
    newcomer = {}
    first_day = {a: roster_on[a] for a in A}
    for a in A:
        for k in range(3):
            if first_day[a] + k < T:
                newcomer[(a, days[first_day[a] + k])] = True
    dfeat = pl.DataFrame(rows_day)
    sd = pl.DataFrame(rows_s)
    sigs = pl.DataFrame(rows_sig, schema={"pt_date": pl.String, "rtype": pl.String, "sig": pl.String, "n": pl.Int64,
                                          "n_agents": pl.Int32, "agents": pl.List(pl.Int16)})
    sc = channel_scores(agd, dfeat, sd, sigs, days, newcomer)
    F, _ = L.fused(sc)
    sc["F"] = F
    out = []
    evd = sorted(ev)
    for c, ty in ev.items():
        w = {ch: float(np.nanmax(sc[ch][max(0, c - 1):c + 2])) if np.isfinite(sc[ch][max(0, c - 1):c + 2]).any() else np.nan
             for ch in sc}
        out.append({"seed": seed, "type": ty, **{f"w_{k}": v for k, v in w.items()}})
    clean = [t for t in range(L.B + 1, T) if min(abs(t - c) for c in evd) >= 3 and t not in set(roster_on.values())]
    far = {ch: float(np.nanmean(sc[ch][clean] >= L.TAU)) for ch in sc}
    return out, far


def channel_scores(agd, dfeat, sd, sigs, days, newcomer):
    zM, _ = L.score_M(agd, days)
    zD, _ = L.score_series(dfeat, days, L.D_FEATURES)
    zO, _ = L.score_series(sd, days, L.O_FEATURES, min_count_col="n_search", min_count=3)
    zC, _ = L.score_C(dfeat, days)
    zS, _ = L.score_S(sigs, days, newcomer)
    return {"S": zS.astype(float), "M": zM, "O": zO, "D": zD, "C": zC}


def job(seed):
    return run(seed)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=20)
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    with ProcessPoolExecutor(a.workers) as ex:
        res = list(ex.map(job, range(a.runs)))
    hits = pl.DataFrame([r for out, _ in res for r in out])
    fars = pl.DataFrame([f for _, f in res])
    (OUT / "synthetic").mkdir(parents=True, exist_ok=True)
    hits.write_parquet(OUT / "synthetic" / "hits.parquet")
    summ = {"hit_rate": {}, "far_per_day": {k: float(fars[k].mean()) for k in fars.columns}}
    for (ty,), g in hits.group_by("type", maintain_order=True):
        summ["hit_rate"][ty] = {ch: float((g[f"w_{ch}"].fill_nan(None).fill_null(-1) >= L.TAU).mean()) for ch in ["S", "M", "O", "D", "C", "F"]}
    (OUT / "synthetic" / "summary.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
