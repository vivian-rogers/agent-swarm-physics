"""H129 synthetic validation (axis F): sticky Potts walkers on the real skeleton (real agents, real hop times, real
project availability windows, real initial projects, real age ranks). No real-data statistic is computed here: the
real hops are used only as the skeleton.

Worlds: W0 fixed Markov (all projects available, no habit), W0h fixed with habit b = 2, W1 age walker (availability
windows, b = 2, lam = 0), W2 age walker with recency (lam = 1.5), W3 / W3s planted age-oriented rotation (kappa 1 / 2).
For each synthetic dataset: per-agent reversal-null p (A_3, A_cyc, m_2), DB-null p (C_2), and the "beyond age" test
against the walker W1* recalibrated on that dataset's own m_2 and return share.

Output: data/processed/H129-project-cycle-currents/synthetic/{tests.parquet, summary.json}
Usage: uv run python hypotheses/H129-project-cycle-currents/analysis/synthetic.py [--tests 30]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import zlib
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h129lib as L  # noqa: E402

WORLDS = {"W0": dict(lam=0.0, b=0.0, all_avail=True), "W0h": dict(lam=0.0, b=2.0, all_avail=True),
          "W1": dict(lam=0.0, b=2.0), "W2": dict(lam=1.5, b=2.0),
          "W3": dict(lam=0.0, b=2.0, kappa=1.0), "W3s": dict(lam=0.0, b=2.0, kappa=2.0)}
SKELETONS = [("G31", 31, "work", None), ("G38", 38, "work", None), ("G41", 41, "work", None),
             ("G44", 44, "work", None), ("51c", 51, "work", "51c"), ("G38att", 38, "attention", None)]


def load_skeleton(g, channel, unit):
    d = L.work_hops(g) if channel == "work" else L.attention_hops(g)
    h, v = d["hops"], d["visits"]
    if unit:
        h, v = h.filter(pl.col("unit") == unit), v.filter(pl.col("unit") == unit)
    age = L.work_age() if channel == "work" else L.attention_age()
    sk = L.skeleton(h, v)
    rank = L.rank_of(age, sk["names"])
    return sk, rank


def test_one(sk, rank, world, rng, n_null=500, n_ref=80, n_cal=5):
    kw = dict(WORLDS[world])
    lam, b = kw.pop("lam"), kw.pop("b")
    s = L.walk(sk, rank, lam, b, rng, **kw)
    M = L.agent_counts(s, rank)
    st = L.stats_from_counts(M.sum(0))
    fn = L.flip_null(M, n_null, rng)
    h = L.hodge(L.seq_to_hops(s))
    dbn = L.db_null(h, n_null, rng)
    ret = L.return_share(s)
    cal = L.calibrate(sk, rank, st["m2"], ret, rng, n_per=n_cal)
    ref = L.reference(sk, rank, cal["lam"], cal["b"], rng, n=n_ref)
    p = lambda null, x: float((np.sum(null >= x) + 1) / (len(null) + 1)) if len(null) else np.nan  # noqa: E731
    return {"world": world, "A3": st["A3"], "Acyc": st["Acyc"], "m2": st["m2"], "C2": h["C2"], "n_mono": st["n_mono"],
            "n_tri": st["n_tri"], "n_hops": st["n_hops"], "ret": ret, "lam_hat": cal["lam"], "b_hat": cal["b"],
            "p_flip_A3": p(fn["A3"], st["A3"]), "p_flip_Acyc": p(fn["Acyc"], st["Acyc"]), "p_flip_m2": p(fn["m2"], st["m2"]),
            "p_db_C2": p(dbn, h["C2"]), "p_ref_Acyc": p(ref["Acyc"], st["Acyc"]), "p_ref_A3": p(ref["A3"], st["A3"]),
            "p_ref_C2": p(ref["C2"], h["C2"])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tests", type=int, default=30)
    a = ap.parse_args()
    out = L.D / "synthetic"
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    t0 = time.time()
    for name, g, ch, unit in SKELETONS:
        sk, rank = load_skeleton(g, ch, unit)
        meta = {"agents": len(sk["agents"]), "hops": int(sum(len(d["t"]) for d in sk["agents"].values())),
                "projects": len(sk["names"])}
        for w in WORLDS:
            rng = np.random.default_rng(zlib.crc32(f"{name}|{w}".encode()))
            for i in range(a.tests):
                r = test_one(sk, rank, w, rng)
                r.update({"skeleton": name, "run": i, **meta})
                rows.append(r)
            print(f"{name} {w} {time.time() - t0:.0f}s", flush=True)
    df = pl.DataFrame(rows, infer_schema_length=None)
    df.write_parquet(out / "tests.parquet")
    summ = {}
    for (name,), g in df.group_by(["skeleton"], maintain_order=True):
        r = {"meta": {k: int(g[k][0]) for k in ("agents", "hops", "projects")}}
        for (w,), x in g.group_by(["world"], maintain_order=True):
            r[w] = {"rej_flip_A3": float((x["p_flip_A3"] < 0.05).mean()), "rej_flip_Acyc": float((x["p_flip_Acyc"] < 0.05).mean()),
                    "rej_flip_m2": float((x["p_flip_m2"] < 0.05).mean()), "rej_db_C2": float((x["p_db_C2"] < 0.05).mean()),
                    "rej_ref_Acyc": float((x["p_ref_Acyc"] < 0.05).mean()), "rej_ref_A3": float((x["p_ref_A3"] < 0.05).mean()),
                    "rej_ref_C2": float((x["p_ref_C2"] < 0.05).mean()),
                    "rej_both_Acyc": float(((x["p_ref_Acyc"] < 0.05) & (x["p_flip_Acyc"] < 0.05)).mean()),
                    "Acyc_median": float(x["Acyc"].median()), "A3_median": float(x["A3"].median()),
                    "m2_median": float(x["m2"].median()), "n_tri_median": float(x["n_tri"].median()),
                    "lam_hat_median": float(x["lam_hat"].median()), "b_hat_median": float(x["b_hat"].median())}
        fpr = max(r[w]["rej_both_Acyc"] for w in ("W0h", "W1", "W2"))
        fpr_c2 = max(float(((g.filter(pl.col("world") == w)["p_ref_C2"] < 0.05) & (g.filter(pl.col("world") == w)["p_db_C2"] < 0.05)).mean())
                     for w in ("W0h", "W1", "W2"))
        r["rule"] = {"Acyc_fpr_max": fpr, "Acyc_power_k2": r["W3s"]["rej_both_Acyc"],
                     "Acyc_valid": bool(fpr <= 0.10 and r["W3s"]["rej_both_Acyc"] >= 0.5),
                     "C2_fpr_max": fpr_c2, "C2_power_k2": float(((g.filter(pl.col("world") == "W3s")["p_ref_C2"] < 0.05)
                                                                 & (g.filter(pl.col("world") == "W3s")["p_db_C2"] < 0.05)).mean()),
                     "flip_A3_size_W0": r["W0"]["rej_flip_A3"]}
        r["rule"]["C2_valid"] = bool(r["rule"]["C2_fpr_max"] <= 0.10 and r["rule"]["C2_power_k2"] >= 0.5)
        summ[name] = r
    (out / "summary.json").write_text(json.dumps(summ, indent=1, default=float))
    print(json.dumps({k: v["rule"] for k, v in summ.items()}, indent=1))


if __name__ == "__main__":
    main()
