"""H01 round 1b native tests (2026-10-04; predictions in goalperiod-subhypotheses/{G12,NE42}/README.md, written first).

G12  #12 drafted teams as known coarse-grained content units: T = mean over debates of (mean within-team minus mean
     cross-team pair cosine) of debaters' agent-debate mean statement vectors (team windows from DQ6
     ground_truth_labels; judge and bench excluded; >= 2 statements). Null: random re-partitions of each debate's
     debaters into groups of the observed team sizes, independent per debate (20,000 draws). Also a centered variant
     (each debate's mean vector over its debaters removed before the cosines).
NE42 #39 -> #40 -> #41 with each agent's modal #39 room as the label in all three periods (GPT-5 excluded):
     (1) P1's room-order dH per day (k = 40 clusters, 8 statements per agent-day, 20 rarefaction draws, 1,000
     size-keeping label permutations), median per period; (2) P6's within-minus-cross residual cosine of rarefied
     agent-day vectors (first-day agent field), pair means, with an agent-level label permutation p.

Instruments: scheme folders r1b/<tag>/ from scheme/build_r1b.py (default: bge_restate, gte_restate and the
style-residualized bge_restate_style, gte_restate_style for G12; bge_restate, gte_restate for NE42).
Writes data/processed/H01-emergent-superagents-exist/r1b/native.json. Non-holdout only (#12, #39-#41).

Usage: uv run python hypotheses/H01-emergent-superagents-exist/analysis/r1b_native.py
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h01data import Scheme  # noqa: E402
from h01lib import pair_table, partition_test, rarefied_counts, rarefied_vectors, unit  # noqa: E402
from h01common import OUT, SEED, SH, guard_holdout  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

GPT5 = 10
G12_TAGS = ["bge_restate", "gte_restate", "bge_restate_style", "gte_restate_style"]
NE42_TAGS = ["bge_restate", "gte_restate"]
N_DRAW = 20000


# ============================================================================ G12
def g12(S: Scheme, rng) -> dict:
    gt = pl.read_parquet(SH / "ground_truth_labels.parquet").filter(
        (pl.col("goal_no") == 12) & pl.col("preferred") & ~pl.col("holdout") & (pl.col("label_kind") == "team"))
    st = S.st.filter(pl.col("goal_no") == 12)
    guard_holdout(sorted(st["pt_date"].unique().to_list()))
    debates = []
    for (deb,), g in sorted(gt.group_by(["unit"]), key=lambda x: x[0][0]):
        t0, t1 = g["t_valid_from"].min(), g["t_valid_to"].max()
        s = st.filter((pl.col("t") >= t0) & (pl.col("t") < t1))
        vecs, side = [], []
        for a, v in g.filter(pl.col("value").is_in(["gov", "opp"])).select("agent", "value").iter_rows():
            rows = s.filter(pl.col("agent") == a)["row"].to_numpy()
            if len(rows) >= 2:
                vecs.append(unit(S.U[rows].mean(0))); side.append(v)
        if len(set(side)) < 2 or min(side.count("gov"), side.count("opp")) < 1 or len(side) < 4:
            debates.append({"debate": deb, "skip": f"{len(side)} debaters with >= 2 statements"}); continue
        V = np.array(vecs); lab = np.array([0 if x == "gov" else 1 for x in side])
        debates.append({"debate": deb, "V": V, "lab": lab})

    def wc(V, lab):
        C = V @ V.T
        iu = np.triu_indices(len(lab), 1)
        same = (lab[:, None] == lab[None, :])[iu]
        c = C[iu]
        if same.sum() == 0 or (~same).sum() == 0:
            return np.nan
        return float(c[same].mean() - c[~same].mean())

    out = {}
    for variant in ("raw", "centered"):
        obs, parts, per = [], [], []
        for db in debates:
            if "skip" in db:
                continue
            V = db["V"] if variant == "raw" else db["V"] - db["V"].mean(0)
            if variant == "centered":
                V = V / np.maximum(np.linalg.norm(V, axis=1, keepdims=True), 1e-9)
            o = wc(V, db["lab"]); obs.append(o)
            n, k = len(db["lab"]), int((db["lab"] == 0).sum())
            alls = []
            for comb in itertools.combinations(range(n), k):
                lb = np.ones(n, int); lb[list(comb)] = 0
                alls.append(wc(V, lb))
            parts.append(np.array(alls))
            per.append({"debate": db["debate"], "n": n, "excess": o, "pct_in_exact_null": float(np.mean(np.array(alls) < o))})
        T = float(np.mean(obs))
        draws = np.mean([p[rng.integers(0, len(p), N_DRAW)] for p in parts], 0)
        out[variant] = {"T": T, "p": float((1 + np.sum(draws >= T)) / (1 + N_DRAW)), "null_mean": float(draws.mean()),
                        "null_q95": float(np.quantile(draws, 0.95)), "n_debates": len(obs),
                        "n_positive": int(np.sum(np.array(obs) > 0)), "per_debate": per}
    out["skipped"] = [db for db in debates if "skip" in db]
    return out


# ============================================================================ NE42
def ne42(S: Scheme, rng) -> dict:
    u39 = S.unit("39")
    lab39 = {}
    for a in np.unique(u39.agents):
        m = (u39.agents == a) & (u39.room >= 0)
        if m.any() and a != GPT5:
            lab39[int(a)] = int(np.bincount(u39.room[m]).argmax())
    out = {"labels": {str(k): v for k, v in lab39.items()}}
    for name in ("39", "40", "41"):
        u = S.unit(name)
        old = np.array([lab39.get(int(a), -1) for a in u.agents])
        days, rec = [], {}
        for t in range(int(u.day.max()) + 1):
            idx = np.where((u.day == t) & (u.nstmt >= 8) & (old >= 0))[0]
            labs = old[idx]
            if len(idx) < 4 or (np.unique(labs, return_counts=True)[1] >= 2).sum() < 2:
                continue
            cnt = rarefied_counts(u, idx, 40, 8, 20, rng)
            r = partition_test(cnt, labs, 1000, rng)
            days.append({"day": u.day_names[t], "n": int(len(idx)), **r})
        rec["p1_days"] = days
        rec["p1_median_dH"] = float(np.median([d["dH"] for d in days])) if days else None
        rec["p1_frac_neg"] = float(np.mean([d["dH"] < 0 for d in days])) if days else None
        # real-room P1 for comparison (#39, #41 two rooms; #40 merged -> none)
        Vr = rarefied_vectors(u, 8, 10, rng)
        ptr = pair_table(u, n_min=8, Vover=Vr)
        if ptr is not None:
            li = np.array([lab39.get(int(a), -1) for a in ptr["i"]]); lj = np.array([lab39.get(int(a), -1) for a in ptr["j"]])
            ok = (li >= 0) & (lj >= 0)
            pk = (ptr["i"] * 1000 + ptr["j"])[ok]; rr = ptr["r"][ok]; same = (li == lj)[ok]
            pairs = np.unique(pk)
            pm = np.array([rr[pk == q].mean() for q in pairs]); ps = np.array([same[pk == q].mean() > 0.5 for q in pairs])
            wc = float(pm[ps].mean() - pm[~ps].mean())
            ags = sorted(lab39); labv = np.array([lab39[a] for a in ags])
            pi_, pj_ = pairs // 1000, pairs % 1000
            nul = []
            for _ in range(2000):
                mp = dict(zip(ags, rng.permutation(labv)))
                sm = np.array([mp[int(a)] == mp[int(b)] for a, b in zip(pi_, pj_)])
                if sm.any() and (~sm).any():
                    nul.append(float(pm[sm].mean() - pm[~sm].mean()))
            rec["wc_old_labels"] = wc
            rec["wc_p_agent_perm"] = float((1 + np.sum(np.array(nul) >= wc)) / (1 + len(nul)))
            rec["n_pairs_within"] = int(ps.sum()); rec["n_pairs_cross"] = int((~ps).sum())
        out[name] = rec
    m = {n: out[n]["p1_median_dH"] for n in ("39", "40", "41")}
    w = {n: out[n].get("wc_old_labels") for n in ("39", "40", "41")}
    out["N2a_pass"] = bool(None not in m.values() and m["40"] > m["39"] and m["40"] > m["41"])
    out["N2b_pass"] = bool(None not in w.values() and w["40"] < w["39"] and w["40"] < w["41"])
    return out


def main():
    path = OUT / "r1b" / "native.json"
    res = json.loads(path.read_text()) if path.exists() else {}
    for tag in G12_TAGS:
        S = Scheme(d=32, base=OUT / "r1b" / tag)
        res.setdefault("G12", {})[tag] = g12(S, np.random.default_rng(SEED + 12))
        r = res["G12"][tag]
        print("G12", tag, {v: (round(r[v]["T"], 4), round(r[v]["p"], 4), f"{r[v]['n_positive']}/{r[v]['n_debates']}") for v in ("raw", "centered")}, flush=True)
    for tag in NE42_TAGS:
        S = Scheme(d=32, base=OUT / "r1b" / tag)
        res.setdefault("NE42", {})[tag] = ne42(S, np.random.default_rng(SEED + 42))
        r = res["NE42"][tag]
        print("NE42", tag, {n: (r[n]["p1_median_dH"], r[n].get("wc_old_labels"), r[n].get("wc_p_agent_perm")) for n in ("39", "40", "41")},
              r["N2a_pass"], r["N2b_pass"], flush=True)
    path.write_text(json.dumps(res, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)))


if __name__ == "__main__":
    main()
