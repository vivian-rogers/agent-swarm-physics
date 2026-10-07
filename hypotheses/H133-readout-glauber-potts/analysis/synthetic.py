"""H133 synthetic validation on the real skeletons (card: "Synthetic validation plan"). Run before any real-data statistic.

Skeletons: 38a (G38), 31a (G31), 51c, 51h (real risk calls, real option sets, real reads with naming flags, real
project activity and dwell). Outcomes are simulated per call; the destination follows the world's option utilities.
Worlds: W0 null (constant per-call hop rate, destination ~ share), W1 (gamma_nam 1.0; and 0.5), W2 broadcast
(gamma_nam = gamma_un = 1), W3 attention burst (two-sided 30-min half-life kernel of all project-linking messages about
b drives hops to b; no read effect), W4 wall clock (P(hop) = 1 - exp(-lambda span)), W5 share (beta_J = 2 on s_b).
The hop rate is calibrated to the skeleton's observed non-birth hop rate (a structural count).

Parts:
  A  O1-O3 eligibility bound (all four skeletons, and the G51 / regime-II-III stacks): the expected number of chosen
     option rows with a named read under W1, and P(>= 5) (Poisson). A read term enters only with >= 5 such rows, so
     this bounds the power of O1 and O2 from above.
  B  O1-O3 fitted runs (38a, 31a; RUNS_FIT per world): eligibility, estimates, sandwich CIs, size and power.
  C  O4 (eta_sw) runs (all four skeletons; RUNS_ETA per world W0, W1, W3, W4, W5): bias, size (CI excludes 0 when the
     truth is per call), power (excludes 0 in W4; excludes 1 in W1); the card's model and the variant with
     ln(1 + n options). Timer-wake subsets (51c, 51h) for N2.
Writes data/processed/H133-readout-glauber-potts/synthetic/*.json.

Usage: uv run python hypotheses/H133-readout-glauber-potts/analysis/synthetic.py [A|B|C ...]
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h133lib as L  # noqa: E402

SK = ["38a", "31a", "51c", "51h"]
RUNS_FIT = 50
RUNS_ETA = 200
OUT = L.D / "synthetic"
SH = L.ROOT / "data/processed/shared"


def target_rate(sk):
    return float((sk.y >= 0).mean())


def messages_by_project(sk):
    pm = pl.read_parquet(SH / "project_mentions_chat.parquet", columns=["t", "project", "holdout"]).filter(~pl.col("holdout"))
    lo, hi = sk.t.min() - 6 * 3600, sk.t.max() + 6 * 3600
    pm = pm.with_columns(pl.col("t").dt.epoch("ms").truediv(1000).alias("ts")).filter((pl.col("ts") >= lo) & (pl.col("ts") <= hi))
    out = {}
    for p, ts in pm.group_by("project").agg(pl.col("ts")).iter_rows():
        out[hashlib.sha1(p.encode()).hexdigest()[:10]] = np.array(ts)
    return out


def expected_chosen(sk, g, kappa_sd=0.0, rng=None, target=None):
    C = sk.n_calls
    ub = g * sk.X["nam"]
    if kappa_sd and rng is not None:
        cells, cinv = np.unique(sk.row_cell, return_inverse=True)
        ub = ub + rng.normal(0, kappa_sd, cells.size)[cinv]
    mx = np.full(C, -np.inf)
    np.maximum.at(mx, sk.row_call, ub)
    e = np.exp(ub - mx[sk.row_call])
    se = np.zeros(C)
    np.add.at(se, sk.row_call, e)
    lse = np.where(se > 0, mx + np.log(np.where(se > 0, se, 1)), -np.inf)
    a0 = L.calibrate_alpha(target, None, sk, lse)
    has = np.isfinite(lse)
    ph = np.where(has, 1 / (1 + np.exp(a0 - np.where(has, lse, 0))), 0)
    pr = e / np.where(se > 0, se, 1)[sk.row_call]
    w = ph[sk.row_call] * pr
    return float(np.sum(w * (sk.X["nam"] > 0))), float(np.sum(w * (sk.X["un"] > 0))), float(np.sum(w * (sk.X["if"] > 0)))


def part_a():
    res = {}
    rng = np.random.default_rng(11)
    for u in SK:
        sk = L.load_skeleton(u)
        tr = target_rate(sk)
        r = {"calls": sk.n_calls, "option_rows": int(sk.row_call.size), "rows_nam": int((sk.X["nam"] > 0).sum()),
             "rows_un": int((sk.X["un"] > 0).sum()), "rows_if": int((sk.X["if"] > 0).sum()), "hop_rate": tr}
        for g in (0.0, 0.5, 1.0, 2.0, 3.0):
            ev = [expected_chosen(sk, g, 1.0, rng, tr) for _ in range(20)]
            en = float(np.mean([e[0] for e in ev]))
            r[f"g{g}"] = {"E_chosen_nam": en, "P_ge5": float(stats.poisson.sf(4, en)),
                          "E_chosen_un": float(np.mean([e[1] for e in ev])), "E_chosen_if": float(np.mean([e[2] for e in ev]))}
        res[u] = r
        print(u, json.dumps(r), flush=True)
    return res


def part_a_stacks(units_by_group: dict):
    rng = np.random.default_rng(12)
    res = {}
    for name, us in units_by_group.items():
        tot = {g: 0.0 for g in (0.0, 0.5, 1.0, 2.0, 3.0)}
        for u in us:
            sk = L.load_skeleton(u)
            tr = target_rate(sk)
            for g in tot:
                tot[g] += float(np.mean([expected_chosen(sk, g, 1.0, rng, tr)[0] for _ in range(5)]))
        # a Poisson count test of the stacked named-row count: reject when count > the 95% quantile at g = 0
        q = int(stats.poisson.ppf(0.95, tot[0.0]))
        res[name] = {"units": us, **{f"g{g}": {"E_chosen_nam": v, "P_ge5": float(stats.poisson.sf(4, v)),
                                               "power_count_test": float(stats.poisson.sf(q, v))} for g, v in tot.items()}}
        print(name, json.dumps(res[name]), flush=True)
    return res


def summarize_fits(rows, key, truth=0.0):
    est = np.array([r[key][0] if r.get(key) else np.nan for r in rows])
    lo = np.array([r[key][1] if r.get(key) else np.nan for r in rows])
    hi = np.array([r[key][2] if r.get(key) else np.nan for r in rows])
    elig = np.isfinite(est)
    return {"runs": len(rows), "eligible": float(elig.mean()),
            "reject_pos": float(np.mean(np.where(elig, lo > 0, False))),
            "reject_any": float(np.mean(np.where(elig, (lo > 0) | (hi < 0), False))),
            "median": float(np.nanmedian(est)) if elig.any() else None,
            "bias": float(np.nanmedian(est) - truth) if elig.any() else None}


def part_b():
    res = {}
    worlds = [("W0", {}), ("W1", {"g_nam": 1.0}), ("W1h", {"g_nam": 0.5}), ("W2", {"g": 1.0}), ("W3", {"lam": 1.0}),
              ("W5", {"bJ": 2.0})]
    for u in ("38a", "31a"):
        sk = L.load_skeleton(u)
        tr = target_rate(sk)
        burst = L.burst_intensity(sk, messages_by_project(sk))
        res[u] = {}
        for w, prm in worlds:
            rng = np.random.default_rng(hash((u, w)) % 2 ** 32)
            rows = []
            t0 = time.time()
            for r in range(RUNS_FIT):
                y = L.simulate(sk, "W1" if w == "W1h" else w, rng, tr, params=prm, burst=burst)
                f = L.fit_logit(sk, y)
                row = {"elig": f.chosen_pos}
                for n in ("nam", "un", "if", "share"):
                    if f.ok and n in f.beta:
                        row[n] = (f.beta[n], f.ci[n][0], f.ci[n][1])
                if f.ok and "nam" in f.beta and "un" in f.beta:
                    d = f.beta["nam"] - f.beta["un"]
                    i, j = f.names.index("nam"), f.names.index("un")
                    s = math.sqrt(max(f.cov[i, i] + f.cov[j, j] - 2 * f.cov[i, j], 0))
                    row["d_addr"] = (d, d - f.info["tq"] * s, d + f.info["tq"] * s)
                if f.ok and "nam" in f.beta and "if" in f.beta:
                    d = f.beta["nam"] - f.beta["if"]
                    i, j = f.names.index("nam"), f.names.index("if")
                    s = math.sqrt(max(f.cov[i, i] + f.cov[j, j] - 2 * f.cov[i, j], 0))
                    row["d_if"] = (d, d - f.info["tq"] * s, d + f.info["tq"] * s)
                rows.append(row)
            truth = {"W1": 1.0, "W1h": 0.5, "W2": 1.0}.get(w, 0.0)
            res[u][w] = {"O1_nam": summarize_fits(rows, "nam", truth), "O2_addr": summarize_fits(rows, "d_addr", 0.0 if w == "W2" else truth),
                         "O3_if": summarize_fits(rows, "d_if", 0.0 if w == "W3" else truth), "un": summarize_fits(rows, "un"),
                         "share": summarize_fits(rows, "share", 2.0 if w == "W5" else 0.0),
                         "mean_chosen_nam": float(np.mean([r["elig"]["nam"] for r in rows])),
                         "mean_chosen_un": float(np.mean([r["elig"]["un"] for r in rows])),
                         "mean_chosen_if": float(np.mean([r["elig"]["if"] for r in rows]))}
            print(u, w, f"{time.time() - t0:.0f}s", json.dumps(res[u][w]), flush=True)
    return res


def part_c():
    res = {}
    worlds = [("W0", {}), ("W1", {"g_nam": 1.0}), ("W3", {"lam": 1.0}), ("W4", {}), ("W5", {"bJ": 2.0})]
    for u in SK:
        sk = L.load_skeleton(u)
        tr = target_rate(sk)
        burst = L.burst_intensity(sk, messages_by_project(sk))
        nopt = L.n_options(sk)
        res[u] = {"n_bg": int(sk.bg.sum()), "n_timer_bg": int((sk.bg & sk.timer).sum())}
        for w, prm in worlds:
            rng = np.random.default_rng(hash((u, w, "c")) % 2 ** 32)
            out = {"card": [], "nopt": [], "timer": []}
            t0 = time.time()
            for r in range(RUNS_ETA):
                y = L.simulate(sk, w, rng, tr, params=prm, burst=burst, dest=False)
                hop = y >= 0
                a = L.fit_cloglog(sk, hop, sk.bg)
                b = L.fit_cloglog(sk, hop, sk.bg, extra=nopt)
                out["card"].append((a.get("eta", np.nan), *a.get("ci", (np.nan, np.nan))))
                out["nopt"].append((b.get("eta", np.nan), *b.get("ci", (np.nan, np.nan))))
                if u.startswith("51"):
                    c = L.fit_cloglog(sk, hop, sk.bg & sk.timer)
                    out["timer"].append((c.get("eta", np.nan), *c.get("ci", (np.nan, np.nan))))
            truth = 1.0 if w == "W4" else 0.0
            summ = {}
            for k, v in out.items():
                if not v:
                    continue
                a_ = np.array(v, float)
                ok = np.isfinite(a_[:, 0])
                summ[k] = {"runs": len(v), "fit_ok": float(ok.mean()), "median": float(np.nanmedian(a_[:, 0])),
                           "bias": float(np.nanmedian(a_[:, 0]) - truth), "sd": float(np.nanstd(a_[:, 0])),
                           "excl0": float(np.mean(ok & ((a_[:, 1] > 0) | (a_[:, 2] < 0)))),
                           "excl1": float(np.mean(ok & ((a_[:, 1] > 1) | (a_[:, 2] < 1)))),
                           "cover_truth": float(np.mean(ok & (a_[:, 1] <= truth) & (a_[:, 2] >= truth)))}
            res[u][w] = summ
            print(u, w, f"{time.time() - t0:.0f}s", json.dumps(summ), flush=True)
    return res


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    parts = sys.argv[1:] or ["A", "B", "C"]
    parts = [p for p in parts if p in ("A", "B", "C", "S")]
    if "A" in parts:
        (OUT / "partA_eligibility.json").write_text(json.dumps(part_a(), indent=1))
    if "S" in parts:
        st = json.loads((L.D / "structural_counts.json").read_text())
        t23 = [r["unit"] for r in st if r["testable"] and r["regime"] != "I"]
        g51 = [u for u in t23 if u.startswith("51")]
        t1 = [r["unit"] for r in st if r["testable"] and r["regime"] == "I"]
        (OUT / "partA_stacks.json").write_text(json.dumps(part_a_stacks({"G51_units": g51, "regime_II_III": t23,
                                                                          "regime_I": t1}), indent=1))
    if "B" in parts:
        (OUT / "partB_logit.json").write_text(json.dumps(part_b(), indent=1))
    if "C" in parts:
        (OUT / "partC_eta.json").write_text(json.dumps(part_c(), indent=1))


if __name__ == "__main__":
    main()
