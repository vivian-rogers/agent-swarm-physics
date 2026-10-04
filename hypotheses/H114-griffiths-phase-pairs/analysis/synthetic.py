"""H114 synthetic validation (axis F) on real message skeletons, before any real-data statistic.

Real agent messages (times, authors, rooms, days, all-present flags) and real ledger reads; parents planted:
  W0 homogeneous: a message with candidates has a parent with prob 0.45; parent chosen by recency exp(-age/180 s)
  W1 agent heterogeneity: agent parent shares logit-normal (sd 0.8 around 0.45), author attractiveness lognormal 0.7
  W2 W1 + 4 planted strong dyads among the 8 most active agents (partner's latest message within 5 min -> parent
     with prob 0.85)
  W2s as W2 but stronger (partner's latest message within 15 min -> parent with prob 0.97)
  W3 W1 + thread momentum: when the newest candidate has a parent, q = 0.85 and it is the parent with prob 0.7;
     otherwise q = 0.30
Candidates: same day and room, other authors, posted 5 s to 30 min before.
Usage: uv run python hypotheses/H114-griffiths-phase-pairs/analysis/synthetic.py [--reps 10]
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h114lib as L  # noqa: E402

UNITS = {"27": 10, "35": 5, "41": 5, "51c": 5}     # unit -> n_days
WORLDS = ["W0", "W1", "W2", "W3", "W2s"]


def plant(m: pl.DataFrame, world: str, rng):
    t = m["t"].to_numpy()
    day = m["day"].to_numpy()
    room = m["room"].fill_null(-1).to_numpy()
    au = m["author"].to_numpy().astype(int)
    agents, counts = np.unique(au, return_counts=True)
    expit = lambda x: 1 / (1 + np.exp(-x))  # noqa: E731
    q_ag = {a: 0.45 for a in agents}
    b_ag = {a: 1.0 for a in agents}
    if world != "W0":
        z = rng.normal(size=len(agents))
        q_ag = {a: float(expit(np.log(0.45 / 0.55) + 0.8 * z[k])) for k, a in enumerate(agents)}
        b_ag = {a: float(np.exp(0.7 * rng.normal())) for a in agents}
    partner = {}
    planted = []
    if world in ("W2", "W2s"):
        top = agents[np.argsort(-counts)][:8]
        top = rng.permutation(top)
        for k in range(0, min(len(top), 8) - 1, 2):
            a, b = int(top[k]), int(top[k + 1])
            partner[a], partner[b] = b, a
            planted += [(a, b), (b, a)]
    par = np.full(len(t), -1, np.int64)
    recent = {}
    for k in range(len(t)):
        key = (day[k], room[k])
        lst = recent.setdefault(key, [])
        while lst and t[lst[0]] < t[k] - 1800:
            lst.pop(0)
        cand = [j for j in lst if au[j] != au[k] and t[j] <= t[k] - 5]
        i = au[k]
        if cand:
            if world in ("W2", "W2s") and i in partner:
                win, pp = (300, 0.85) if world == "W2" else (900, 0.97)
                pc = [j for j in cand if au[j] == partner[i] and t[j] >= t[k] - win]
                if pc and rng.random() < pp:
                    par[k] = pc[-1]
                    lst.append(k)
                    continue
            q = q_ag[i]
            if world == "W3":
                newest = cand[-1]
                if par[newest] >= 0:
                    q = 0.85
                    if rng.random() < q:
                        par[k] = newest if rng.random() < 0.7 else par[k]
                        if par[k] < 0:
                            w = np.array([b_ag[au[j]] * np.exp(-(t[k] - t[j]) / 180) for j in cand])
                            par[k] = cand[rng.choice(len(cand), p=w / w.sum())]
                    lst.append(k)
                    continue
                q = 0.30
            if rng.random() < q:
                w = np.array([b_ag[au[j]] * np.exp(-(t[k] - t[j]) / 180) for j in cand])
                par[k] = cand[rng.choice(len(cand), p=w / w.sum())]
        lst.append(k)
    depth = L.depth_pass(par)
    names = rng.random(len(t)) < 0.7
    sim = m.with_columns(pl.Series("par", par), pl.Series("depth", depth), pl.Series("names", names & (par >= 0)))
    return sim, planted


def run_one(args):
    uid, world, rep = args
    m, R = L.load_unit(uid)
    rng = np.random.default_rng(1000 * rep + WORLDS.index(world) * 17 + int(sum(map(ord, uid))))
    sim, planted = plant(m, world, rng)
    st = L.unit_stats(sim, R, UNITS[uid], B=200, n_rand=100, seed=rep)
    P = st.pop("_pairs")
    det = P.filter(pl.col("strong")).select("reader", "author").to_numpy().tolist()
    det = set(map(tuple, det))
    pl_set = set(planted)
    pg = P.filter(pl.struct("reader", "author").map_elements(lambda s: (s["reader"], s["author"]) in pl_set,
                                                              return_dtype=pl.Boolean)) if planted else P.head(0)
    out = {k: v for k, v in st.items() if not isinstance(v, list)}
    out.update({"unit_id": uid, "world": world, "rep": rep, "n_planted": len(planted),
                "n_planted_detected": len(det & pl_set), "n_false_strong": len(det - pl_set),
                "planted_g_med": float(pg["g"].median()) if pg.height else float("nan")})
    return out


def summarize(df: pl.DataFrame) -> dict:
    S = {}
    for w in WORLDS:
        x = df.filter(pl.col("world") == w)
        per = {}
        for u in UNITS:
            y = x.filter(pl.col("unit_id") == u)
            if not y.height:
                continue
            f = lambda e: float(y.select(e.mean()).item())  # noqa: E731
            per[u] = {
                "g_rep": f(pl.col("g_rep")), "h_tail": f(pl.col("h_tail")), "dh": f(pl.col("dh")),
                "dh_excl0": f((pl.col("dh_lo") > 0) | (pl.col("dh_hi") < 0)),
                "dh_pos": f(pl.col("dh_lo") > 0),
                "delta_h_pos": f(pl.col("delta_h_lo") > 0),
                "M1_inside": f((pl.col("h_tail_lo") <= pl.col("h_tail_M1")) & (pl.col("h_tail_M1") <= pl.col("h_tail_hi"))),
                "M2_inside": f((pl.col("h_tail_lo") <= pl.col("h_tail_M2")) & (pl.col("h_tail_M2") <= pl.col("h_tail_hi"))),
                "M1_below": f(pl.col("h_tail_lo") > pl.col("h_tail_M1")),
                "M2_below": f(pl.col("h_tail_lo") > pl.col("h_tail_M2")),
                "n_strong": f(pl.col("n_strong")), "false_strong": f(pl.col("n_false_strong")),
                "detect_rate": float((y["n_planted_detected"].sum() / max(y["n_planted"].sum(), 1))),
                "planted_g_med": f(pl.col("planted_g_med")),
                "cut_ok": f(pl.col("dh_cut_lo").is_not_null() & (pl.col("dh_cut_lo") <= 0) & (pl.col("dh_cut_hi") >= 0)
                            & (pl.col("dh_cut") < pl.col("dh_rand_q05"))) if "dh_cut_lo" in y.columns else 0.0,
                "vuong_pl": f(pl.col("vuong_z") > 1.645), "alpha_mean": f(pl.col("alpha")),
                "alpha_sd": float(y["alpha"].std()), "n_tail": f(pl.col("n_tail")), "max_depth": f(pl.col("max_depth")),
            }
        S[w] = per
    return S


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=10)
    a = ap.parse_args()
    jobs = [(u, w, r) for u in UNITS for w in WORLDS for r in range(a.reps)]
    with ProcessPoolExecutor(max_workers=2) as ex:
        res = list(ex.map(run_one, jobs))
    df = pl.DataFrame(res, infer_schema_length=None)
    out = L.OUT / "synthetic"
    out.mkdir(parents=True, exist_ok=True)
    df.write_parquet(out / "runs.parquet")
    S = summarize(df)
    (out / "summary.json").write_text(json.dumps(S, indent=1))
    for w, per in S.items():
        for u, v in per.items():
            print(w, u, " ".join(f"{k}={v[k]:.3f}" for k in v))


if __name__ == "__main__":
    main()
