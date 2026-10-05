"""H15 round 2 synthetic validation (axis F), run before any round-2 statistic on real data.

    uv run python hypotheses/H15-semantic-information-scrambles/analysis/r2_synthetic.py [--reps 30]

Worlds on the real skeleton (real F/P events, agents, periods, windows, V_pre, first-read classes and trail classes;
base rates from pre-event commits V_pre only, never from post-event outcomes):
  R1b / R2 (Poisson FE interaction, sandwich test):
    null_main    every class raises V x1.3 in both arms (reading precedes writing); erasure x0.6
    null_latent  an event-level latent productivity correlated with the class flags raises V in both arms
    rr110 / rr115 / rr125  planted class x F interaction (each tested class at once)
  R1c: planted +0.05 / +0.10 read-or-search shifts on the real ML/MG skeleton (control segments resampled).
  R3: performative world (post windows swapped with same-agent windows >= 3 days away) and enacted worlds
      (q = 0.05 / 0.10 / 0.20 of the note's terms planted into the swapped window).
Writes data/processed/H15-semantic-information-scrambles/r2/synthetic.json.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r2lib as L  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

T0 = time.time()


def log(*a):
    print(f"[{time.time() - T0:7.1f}s]", *a, flush=True)


SAMPLES = {"pooled": None, "G51": "G51", "G38": "G38", "G40": "G40"}


def simulate(e: pl.DataFrame, classes: list[str], world: str, y: str, rng) -> np.ndarray:
    F = (e["etype"] == "F").to_numpy()
    nw = e["n_win"].to_numpy().astype(float)
    expo = {"V20": nw / 20, "V3": (nw - 2) / 18, "V6": (nw - 5) / 15}[y]
    vpre = e["V_pre"].to_numpy()
    st = L.codes(e["stratum"].to_numpy())
    base = np.bincount(st, weights=vpre) / np.bincount(st)
    lam = np.maximum(base[st], 0.05) * np.exp(0.3 * (np.log1p(vpre) - np.log1p(vpre).mean()))
    lam = lam * np.where(F, 0.6, 1.0)
    X = np.column_stack([e[c].cast(pl.Float64).to_numpy() for c in classes])
    rrv = {"rr110": 1.10, "rr115": 1.15, "rr125": 1.25}.get(world, 1.0)
    lam = lam * np.prod(np.where(X > 0, 1.3, 1.0), axis=1) * np.prod(np.where((X > 0) & F[:, None], rrv, 1.0), axis=1)
    if world == "null_latent":
        z = (X - X.mean(0)) / np.maximum(X.std(0), 1e-9)
        u = 0.6 * z.mean(1) + rng.normal(0, 0.4, len(lam))
        lam = lam * np.exp(u - u.mean())
    cl = L.codes(e["cluster"].to_numpy())
    g = rng.gamma(2.0, 0.5, cl.max() + 1)[cl] * rng.gamma(3.0, 1 / 3, len(lam))
    cnt = rng.poisson(lam * g * np.maximum(expo, 0.05))
    return cnt / np.maximum(expo, 0.05)


def run_model(e, classes, y, worlds, reps, rng, test_keys):
    out = {}
    for w in worlds:
        res = {s: {k: [] for k in test_keys} for s in SAMPLES}
        for r in range(reps):
            v = simulate(e, classes, w, y, rng)
            es = e.with_columns(pl.Series(y, v))
            for s, p in SAMPLES.items():
                sub = es if p is None else es.filter(pl.col("period") == p)
                f = L.fit(sub, y, classes)
                for k in test_keys:
                    b, se = f.get(k, {}).get("b", np.nan), f.get(k, {}).get("se", np.nan)
                    res[s][k].append((b, se))
        summ = {}
        for s in SAMPLES:
            summ[s] = {}
            for k in test_keys:
                a = np.array(res[s][k], float)
                ok = np.isfinite(a).all(1)
                a = a[ok]
                if len(a) == 0:
                    summ[s][k] = {"n_ok": 0}
                    continue
                lo, hi = a[:, 0] - 1.96 * a[:, 1], a[:, 0] + 1.96 * a[:, 1]
                summ[s][k] = {"mean_RR": float(np.exp(a[:, 0].mean())), "rej_gt1": float((lo > 0).mean()),
                              "rej_lt1": float((hi < 0).mean()), "n_ok": int(ok.sum()),
                              "cover_planted": float(((lo <= np.log({"rr110": 1.1, "rr115": 1.15, "rr125": 1.25}.get(w, 1.0)))
                                                      & (hi >= np.log({"rr110": 1.1, "rr115": 1.15, "rr125": 1.25}.get(w, 1.0)))).mean())}
        out[w] = summ
        log(" world", w, {s: {k: (round(v.get("mean_RR", np.nan), 3), v.get("rej_gt1")) for k, v in summ[s].items()}
                          for s in ("pooled", "G51")})
    return out


def r1c_synth(rng, reps=500):
    sg = pl.read_parquet(L.DATA / "segs.parquet")
    cat = pl.read_parquet(L.ROOT / "data/processed/H15-semantic-information-scrambles/r1b/scramble_catalog.parquet")
    ev = cat.filter(pl.col("type").is_in(["ML", "MG"]) & (pl.col("regime") == "III"))
    rows = []
    for a, t, gno in zip(ev["agent"].to_list(), ev["t"].to_list(), ev["goal_no"].to_list()):
        pool = sg.filter((pl.col("agent") == a) & (pl.col("goal_no") == gno) &
                         ((pl.col("t_first") - t).abs() > pl.duration(days=1)))["rs5"].to_numpy()
        if len(pool) >= 10:
            rows.append(pool)
    out = {"n_events": len(rows)}
    for d in (0.0, 0.05, 0.10):
        zs = []
        for _ in range(reps):
            z = []
            for pool in rows:
                x = rng.choice(pool) + d
                sd = pool.std()
                z.append((x - pool.mean()) / sd if sd > 0 else 0.0)
            zs.append(np.sum(z) / np.sqrt(len(z)))
        out[f"delta_{d:.2f}"] = {"rej_z2": float((np.array(zs) >= 2).mean())}
    log(" R1c", out)
    return out


def r3_synth(rng, reps=3):
    notes = pl.read_parquet(L.DATA / "notes.parquet").filter(pl.col("terms").list.len() > 0)
    ag = notes["agent"].to_numpy()
    per = np.array(notes["period"].to_list())
    dn = notes["pt_date"].str.to_date().to_numpy().astype("datetime64[D]").astype(np.int64)
    POST = [np.asarray(x, np.int64) for x in notes["post"].to_list()]
    P10 = [np.asarray(x, np.int64) for x in notes["post10"].to_list()]
    P31 = [np.asarray(x, np.int64) for x in notes["post31"].to_list()]
    T = [np.asarray(x, np.int64) for x in notes["terms"].to_list()]
    key = {}
    for i, (a, p) in enumerate(zip(ag, per)):
        key.setdefault((a, p), []).append(i)
    out = {}
    for q in (0.0, 0.05, 0.10, 0.20):
        stats = {k: [] for k in ("E_x", "E_s", "Enov_x", "Enov_s")}
        for r in range(reps):
            newp, n10, n31 = [], [], []
            for i in range(len(T)):
                cand = [k for k in key[(ag[i], per[i])] if abs(dn[k] - dn[i]) >= 3]
                k = rng.choice(cand) if cand else i
                plant = T[i][rng.random(len(T[i])) < q] if q > 0 else np.zeros(0, np.int64)
                newp.append(np.union1d(POST[k], plant))
                n10.append(np.union1d(P10[k], plant))
                n31.append(np.union1d(P31[k], plant) if len(P31[k]) else P31[k])
            tab = L.r3_table(notes, post=newp, post10=n10, post31=n31, seed=int(rng.integers(1e9)))
            for kk in stats:
                stats[kk].append(float(np.nanmean(tab[kk].to_numpy())))
        out[f"q{q:.2f}"] = {k: float(np.mean(v)) for k, v in stats.items()}
        log(" R3 world q", q, out[f"q{q:.2f}"])
    # sampling SE of the pooled mean at real cluster structure (observed-free: from the q=0 world)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=30)
    ap.add_argument("--only", default="r1b,r2,r1c,r3")
    a = ap.parse_args()
    rng = np.random.default_rng(20261005)
    e = L.load_events()
    out = {"reps": a.reps}
    todo = a.only.split(",")
    worlds = ["null_main", "null_latent", "rr110", "rr115", "rr125"]
    if "r2" in todo:
        log("R2 (V3; L, M, Gp, Gn)")
        out["R2"] = run_model(e, ["L", "M", "Gp", "Gn"], "V3", worlds, a.reps, rng, ["LxF", "MxF", "GpxF", "GnxF"])
        log("R2 concentration (V6; U12, U35)")
        eu = L.u_classes(e)
        out["R2_conc"] = run_model(eu, ["U12", "U35"], "V6", worlds, a.reps, rng, ["U12xF", "U35xF"])
    if "r1b" in todo:
        log("R1b (V20; T1, T2)")
        et = L.trail_classes(e)
        out["R1b"] = run_model(et, ["T1", "T2"], "V20", worlds, a.reps, rng, ["T1xF", "T2xF"])
    if "r1c" in todo:
        out["R1c"] = r1c_synth(rng)
    if "r3" in todo:
        out["R3"] = r3_synth(rng)
    p = L.DATA / "synthetic.json"
    old = json.loads(p.read_text()) if p.exists() else {}
    old.update(out)
    p.write_text(json.dumps(old, indent=1))
    log("written", p)


if __name__ == "__main__":
    main()
