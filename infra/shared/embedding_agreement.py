"""DQ5: agreement between the two embedding models (bge_small vs gte_modernbert), per goal period. Numbers only.

Non-holdout statements only (periods entirely held out are omitted). Per goal period x kind (chat, intent):
  cka_raw            linear CKA of the raw embeddings (384-d vs 768-d), centered within the period (all statements)
  cka_w32            linear CKA of the regime-whitened 32-d unit vectors (statements_white32_<model>.npy)
  pair_rho_raw/_w32  Spearman correlation of pairwise cosines over a random sample of <= SAMPLE statements
  knn10_jaccard_w32  mean Jaccard overlap of the 10 nearest neighbours (same sample, whitened cosine)
  pr_w32_bge/_gte    participation ratio of the whitened statement cloud (effective dimension, H12/H20 style)
Per goal period, agent-day level (the standard pipeline: agent_day_vec[_<model>] -> regime whitener, d = 32 ->
unit-normalize; agent-days with >= 3 statements, days with >= 3 agents):
  ad_cka                         linear CKA of the agent-day vectors
  ad_pair_rho / ad_pair_r        Spearman / Pearson between models of same-day agent-pair cosines
  ad_align_bge / ad_align_gte    mean same-day agent-pair cosine (alignment) under each model
  ad_dm_pair_rho, ad_dm_align_*  the same after day-demeaning (H13's delta = v - mean of agents that day)
  ag_rho                         Spearman of agent x agent similarity of period mean day-demeaned vectors (H01/H13)
  ad_pr_bge / ad_pr_gte          participation ratio of the centered agent-day vectors
  w30_pair_rho                   Spearman of same-window agent-pair cosines from agent_win30 (>= 2 statements)
Cross-period: Spearman over periods of each per-period statistic computed with both models (does the phase-diagram
ordering survive the swap?).
Outputs: embeddings/agreement_gte_modernbert.parquet and .json.
Usage: uv run python infra/shared/embedding_agreement.py   (after build_embeddings_v2 and style_resid build)
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2"

import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy.stats import pearsonr, spearmanr  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import write_provenance  # noqa: E402
from embed_models import ED, agent_vectors, load_whitener, statement_embeddings, statement_vectors  # noqa: E402

M2 = "gte_modernbert"
SAMPLE = 1500
SEED = 20261004


def cka(X: np.ndarray, Y: np.ndarray) -> float:
    X = np.asarray(X, np.float64); Y = np.asarray(Y, np.float64)
    X = X - X.mean(0); Y = Y - Y.mean(0)
    xy = np.linalg.norm(X.T @ Y) ** 2
    return float(xy / (np.linalg.norm(X.T @ X) * np.linalg.norm(Y.T @ Y)))


def pr(X: np.ndarray) -> float:
    X = np.asarray(X, np.float64); X = X - X.mean(0)
    w = np.clip(np.linalg.eigvalsh(X.T @ X / len(X)), 0, None)
    return float(w.sum() ** 2 / (w ** 2).sum())


def unit(X):
    X = np.asarray(X, np.float64)
    n = np.linalg.norm(X, axis=1, keepdims=True)
    return X / np.where(n > 0, n, 1)


def knn_jaccard(A: np.ndarray, B: np.ndarray, k: int = 10) -> float:
    SA = A @ A.T; SB = B @ B.T
    np.fill_diagonal(SA, -np.inf); np.fill_diagonal(SB, -np.inf)
    na = np.argpartition(-SA, k, axis=1)[:, :k]; nb = np.argpartition(-SB, k, axis=1)[:, :k]
    return float(np.mean([len(set(a) & set(b)) / len(set(a) | set(b)) for a, b in zip(na, nb)]))


def whiten_rows(V: np.ndarray, regimes: np.ndarray, model: str) -> np.ndarray:
    out = np.zeros((len(V), 32))
    for r in np.unique(regimes):
        m = regimes == r
        out[m] = load_whitener(r, 32, model)(V[m])
    return unit(out)


def pair_day(Vb, Vg, days, min_agents=3, demean=False):
    cb, cg = [], []
    for d in np.unique(days):
        k = np.flatnonzero(days == d)
        if len(k) < min_agents:
            continue
        A, B = Vb[k], Vg[k]
        if demean:
            A = A - A.mean(0); B = B - B.mean(0)
        A, B = unit(A), unit(B)
        iu = np.triu_indices(len(k), 1)
        cb.append((A @ A.T)[iu]); cg.append((B @ B.T)[iu])
    if not cb:
        return np.array([]), np.array([])
    return np.concatenate(cb), np.concatenate(cg)


def main():
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    st = pl.read_parquet(ED / "statements.parquet").with_row_index("srow")
    nh = st.filter(~pl.col("holdout"))
    Eb = statement_embeddings("bge_small", st)
    Eg = statement_embeddings(M2, st)
    Wb = statement_vectors("bge_small", "white32").astype(np.float64)
    Wg = statement_vectors(M2, "white32").astype(np.float64)
    rows = []
    for (g, kind), sub in sorted(nh.group_by("goal_no", "kind"), key=lambda x: (x[0][0], x[0][1])):
        idx = sub["srow"].to_numpy()
        if len(idx) < 50:
            continue
        s = rng.choice(idx, min(SAMPLE, len(idx)), replace=False)
        iu = np.triu_indices(len(s), 1)
        rb, rg = unit(Eb[s]), unit(Eg[s])
        wb, wg = unit(Wb[s]), unit(Wg[s])
        rows.append({"goal_no": int(g), "kind": kind, "n": int(len(idx)),
                     "cka_raw": cka(Eb[idx], Eg[idx]), "cka_w32": cka(Wb[idx], Wg[idx]),
                     "pair_rho_raw": float(spearmanr((rb @ rb.T)[iu], (rg @ rg.T)[iu]).statistic),
                     "pair_rho_w32": float(spearmanr((wb @ wb.T)[iu], (wg @ wg.T)[iu]).statistic),
                     "knn10_jaccard_w32": knn_jaccard(wb, wg),
                     "pr_w32_bge": pr(Wb[idx]), "pr_w32_gte": pr(Wg[idx])})
        print(g, kind, len(idx), f"{time.time() - t0:.0f}s", flush=True)
    stmt = pl.DataFrame(rows)

    # agent-day and agent-window level
    ad = pl.read_parquet(ED / "agent_day.parquet").with_row_index("row")
    keep = (~ad["holdout"].to_numpy()) & ((ad["n_chat"] + ad["n_intent"]).to_numpy() >= 3)
    Vb = whiten_rows(agent_vectors("day", "bge_small").astype(np.float32), ad["regime"].to_numpy(), "bge_small")
    Vg = whiten_rows(agent_vectors("day", M2).astype(np.float32), ad["regime"].to_numpy(), M2)
    w30 = pl.read_parquet(ED / "agent_win30.parquet").with_row_index("row")
    keepw = (~w30["holdout"].to_numpy()) & ((w30["n_chat"] + w30["n_intent"]).to_numpy() >= 2)
    Ub = whiten_rows(agent_vectors("win30", "bge_small").astype(np.float32), w30["regime"].to_numpy(), "bge_small")
    Ug = whiten_rows(agent_vectors("win30", M2).astype(np.float32), w30["regime"].to_numpy(), M2)
    arows = []
    for g in sorted(set(ad.filter(pl.Series(keep))["goal_no"].to_list())):
        m = keep & (ad["goal_no"].to_numpy() == g)
        if m.sum() < 10:
            continue
        days = ad["pt_date"].to_numpy()[m]; agents = ad["agent"].to_numpy()[m]
        A, B = Vb[m], Vg[m]
        cb, cg = pair_day(A, B, days)
        db, dg = pair_day(A, B, days, demean=True)
        r = {"goal_no": int(g), "n_agent_days": int(m.sum()), "ad_cka": cka(A, B), "ad_pr_bge": pr(A), "ad_pr_gte": pr(B)}
        if len(cb) >= 10:
            r.update({"ad_pair_rho": float(spearmanr(cb, cg).statistic), "ad_pair_r": float(pearsonr(cb, cg).statistic),
                      "ad_align_bge": float(cb.mean()), "ad_align_gte": float(cg.mean()),
                      "ad_dm_pair_rho": float(spearmanr(db, dg).statistic),
                      "ad_dm_align_bge": float(db.mean()), "ad_dm_align_gte": float(dg.mean())})
            # agent x agent similarity of period-mean day-demeaned vectors
            Db = np.full_like(A, np.nan); Dg = np.full_like(B, np.nan)
            for d in np.unique(days):
                k = days == d
                if k.sum() >= 3:
                    Db[k] = A[k] - A[k].mean(0); Dg[k] = B[k] - B[k].mean(0)
            ok = np.isfinite(Db).all(1)
            ags = [a for a in np.unique(agents[ok]) if (ok & (agents == a)).sum() >= 2]
            if len(ags) >= 4:
                Hb = unit(np.stack([Db[ok & (agents == a)].mean(0) for a in ags]))
                Hg = unit(np.stack([Dg[ok & (agents == a)].mean(0) for a in ags]))
                iu = np.triu_indices(len(ags), 1)
                r["ag_rho"] = float(spearmanr((Hb @ Hb.T)[iu], (Hg @ Hg.T)[iu]).statistic)
                r["n_agents"] = len(ags)
        mw = keepw & (w30["goal_no"].to_numpy() == g)
        if mw.sum() >= 10:
            win = (w30["pt_date"].cast(pl.String) + "/" + w30["win30"].cast(pl.String)).to_numpy()[mw]
            wb_, wg_ = pair_day(Ub[mw], Ug[mw], win, min_agents=2)
            if len(wb_) >= 10:
                r["w30_pair_rho"] = float(spearmanr(wb_, wg_).statistic)
                r["w30_align_bge"] = float(wb_.mean()); r["w30_align_gte"] = float(wg_.mean())
        arows.append(r)
    agd = pl.DataFrame(arows)
    res = stmt.join(agd, on="goal_no", how="left")
    res.write_parquet(ED / "agreement_gte_modernbert.parquet", compression="zstd")

    summ = {"sample": SAMPLE, "n_periods": int(agd.height)}
    for kind in ("chat", "intent"):
        x = stmt.filter(pl.col("kind") == kind)
        summ[f"statements_{kind}"] = {c: {"median": float(x[c].median()), "min": float(x[c].min()), "max": float(x[c].max())}
                                      for c in ("cka_raw", "cka_w32", "pair_rho_raw", "pair_rho_w32", "knn10_jaccard_w32")}
        summ[f"statements_{kind}"]["cross_period_rho_pr_w32"] = float(spearmanr(x["pr_w32_bge"], x["pr_w32_gte"]).statistic)
    for c in ("ad_cka", "ad_pair_rho", "ad_pair_r", "ad_dm_pair_rho", "ag_rho", "w30_pair_rho"):
        v = agd[c].drop_nulls() if c in agd.columns else pl.Series([])
        if len(v):
            summ[c] = {"median": float(v.median()), "min": float(v.min()), "max": float(v.max()), "n": len(v)}
    for a, b in (("ad_align_bge", "ad_align_gte"), ("ad_dm_align_bge", "ad_dm_align_gte"), ("ad_pr_bge", "ad_pr_gte"),
                 ("w30_align_bge", "w30_align_gte")):
        x = agd.select(a, b).drop_nulls()
        summ[f"cross_period_rho_{a[:-4]}"] = {"spearman": float(spearmanr(x[a], x[b]).statistic), "n": x.height,
                                              "median_bge": float(x[a].median()), "median_gte": float(x[b].median())}
    (ED / "agreement_gte_modernbert.json").write_text(json.dumps(summ, indent=1))
    write_provenance("embedding_agreement", ["embeddings/statements", "embeddings/*_bge_small.npy",
                                             "embeddings/*_gte_modernbert.npy", "embeddings/agent_day*", "embeddings/agent_win30*"],
                     {"sample": SAMPLE, "seed": SEED, "rows": "non-holdout statements", "dim": 32})
    print(json.dumps(summ, indent=1))
    print(f"done {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
