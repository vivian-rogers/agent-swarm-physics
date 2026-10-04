"""DQ5: style-residualized statement and agent vectors, for each embedding model (bge_small, gte_modernbert).

Per statement (rows of embeddings/statements.parquet: agent chat + intentions):
  1. whiten with the model's regime whitener at d = 32 (embed_models.load_whitener; non-holdout fit) and unit-normalize
     -> statements_white32_<model>.npy
  2. OLS of those 32 coordinates on an intercept + the 20 standardized numeric style features of H13
     (text_features.STYLE; chat from text_features.parquet, intentions computed in memory from intentions_text, never
     written). Standardization and coefficients are fit on NON-HOLDOUT statements only and applied to all rows.
     Only the style-explained deviation (slopes x standardized features) is subtracted; the fitted intercept (the
     group's mean direction, i.e. the kind offset or the period's topic) is kept. Residuals are re-normalized.
     Two fit groupings:
       style_resid          within (regime, kind)                -> statements_style_resid32_<model>.npy
       style_resid_period   within (goal_no, regime, kind), the unit-of-analysis rule; groups with fewer than
                            MIN_FIT_PERIOD non-holdout statements (all of a held-out period) use the regime fit
                                                                 -> statements_style_resid_period32_<model>.npy
     Fit groups, sizes and style R^2 are in embeddings/style_resid_fit.json.
  3. agent_{day,win30}_{white32,style_resid,style_resid_period}_<model>.npy: plain means of the unit vectors over each
     row of the existing agent_day.parquet / agent_win30.parquet (chat + intentions, like agent_day_vec). Not
     re-normalized, so the norm keeps the within-group coherence (H13's v_{i,d}); normalize downstream if needed.
     Already whitened: do not whiten again.
Because OLS is column-wise, residualizing 32 coordinates equals the first 32 of a wider residualization (before the
re-normalization). Chat-only aggregates: average the statement-level arrays over chat rows.

check runs H13's family-field test (a1/a2) on its 15 exploratory units with both variants and both models, plus
topic-structure checks (day-field share, cross-unit period classification), and writes
embeddings/style_resid_check.parquet + style_resid_check.json (numbers only, non-holdout days only).

Usage: uv run python infra/shared/style_resid.py [build|check|all] [--models bge_small,gte_modernbert]
       (default: build. check imports H13's estimators read-only from hypotheses/H13-family-fields/.)
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT, ROOT, write_provenance  # noqa: E402
from embed_models import (ED, MODELS, STYLE_DIM, group_ids, group_plain_means, load_whitener,  # noqa: E402
                          statement_embeddings)
from text_features import STYLE, text_features  # noqa: E402

FCOLS = [f"f_{k}" for k in STYLE]
MIN_FIT_PERIOD = 300  # non-holdout statements needed for a period-level fit (21 x 32 coefficients)


def style_matrix(st: pl.DataFrame) -> np.ndarray:
    """(n_statements x 20) style features aligned to statements rows (float64; nulls -> 0)."""
    ci = pl.read_parquet(ED / "chat_index.parquet").with_row_index("src_row")
    tf = pl.read_parquet(OUT / "text_features.parquet", columns=["message_id", *FCOLS])
    chat = ci.join(tf, on="message_id", how="left", maintain_order="left").drop("message_id")
    ii = pl.read_parquet(ED / "intentions_index.parquet").with_row_index("src_row")
    it = (pl.read_parquet(OUT / "intentions_text.parquet", columns=["event_index", "goal_text"]).drop_nulls("goal_text")
          .rename({"event_index": "message_id", "goal_text": "text"}))
    itf = text_features(it).select("message_id", *FCOLS).rename({"message_id": "event_index"})
    del it
    intent = ii.join(itf, on="event_index", how="left", maintain_order="left").drop("event_index")
    key = st.select(pl.int_range(pl.len()).alias("srow"), "kind", "src_row")
    a = key.filter(pl.col("kind") == "chat").join(chat, on="src_row", how="left", maintain_order="left")
    b = key.filter(pl.col("kind") == "intent").join(intent, on="src_row", how="left", maintain_order="left")
    F = pl.concat([a, b]).sort("srow")
    assert F.height == st.height and (F["srow"].to_numpy() == np.arange(st.height)).all()
    n_missing = int(F.select(pl.col(FCOLS[0]).is_null().sum()).item())
    assert n_missing == 0, f"{n_missing} statements without style features"
    return np.nan_to_num(F.select(FCOLS).to_numpy().astype(np.float64))


def fit_style(U: np.ndarray, F: np.ndarray, fitm: np.ndarray):
    """OLS of unit vectors U[fitm] on an intercept + standardized style features F[fitm].
    Returns ((mu, sd, B), style R^2 on the fit rows)."""
    mu = F[fitm].mean(0); sd = F[fitm].std(0); sd = np.where(sd > 0, sd, 1.0)
    Xf = np.column_stack([np.ones(fitm.sum()), (F[fitm] - mu) / sd])
    Uf = U[fitm].astype(np.float64)
    B, *_ = np.linalg.lstsq(Xf, Uf, rcond=None)
    rf = Uf - Xf @ B
    return (mu, sd, B), float(1 - (rf ** 2).sum() / ((Uf - Uf.mean(0)) ** 2).sum())


def apply_style(U: np.ndarray, F: np.ndarray, m: np.ndarray, c) -> np.ndarray:
    """Subtract only the style-explained deviation (slopes x standardized features) from U[m] and re-normalize. The
    intercept (the group's mean direction: kind offset, the period's topic) is kept, so cross-group structure survives.
    For a confirmatory run on a held-out period, refit with fit_style on that period's rows, then apply_style."""
    mu, sd, B = c
    Rm = U[m] - ((F[m] - mu) / sd) @ B[1:]
    return Rm / np.linalg.norm(Rm, axis=1, keepdims=True)


def build(model: str, st: pl.DataFrame, F: np.ndarray) -> dict:
    t0 = time.time()
    E = statement_embeddings(model, st, mmap=True)
    reg = st["regime"].to_numpy(); kind = st["kind"].to_numpy(); hold = st["holdout"].to_numpy()
    U = np.zeros((st.height, STYLE_DIM), dtype=np.float32)
    for r in np.unique(reg):
        m = reg == r
        Z = load_whitener(r, STYLE_DIM, model)(E[m])
        U[m] = Z / np.linalg.norm(Z, axis=1, keepdims=True)
    del E
    goal = st["goal_no"].to_numpy()
    sfx = MODELS[model]["suffix"]
    np.save(ED / f"statements_white32_{sfx}.npy", U.astype(np.float16))
    fit_stats = {"regime": {}, "period": {}}
    coef = {}

    R = np.zeros_like(U)
    for r in np.unique(reg):
        for k in np.unique(kind):
            m = (reg == r) & (kind == k)
            coef[(r, k)], r2 = fit_style(U, F, m & ~hold)
            R[m] = apply_style(U, F, m, coef[(r, k)])
            fit_stats["regime"][f"{r}/{k}"] = {"n_fit": int((m & ~hold).sum()), "n_all": int(m.sum()), "style_r2_fit": r2}
            print(f"{model} regime {r}/{k}: n_fit={(m & ~hold).sum()} style R2={r2:.3f}", flush=True)
    Rp = np.zeros_like(U)
    for g in np.unique(goal):
        for r in np.unique(reg[goal == g]):
            for k in np.unique(kind):
                m = (goal == g) & (reg == r) & (kind == k)
                if not m.any():
                    continue
                fm = m & ~hold
                if fm.sum() >= MIN_FIT_PERIOD:
                    c, r2 = fit_style(U, F, fm); level = "period"
                else:
                    c, r2 = coef[(r, k)], None; level = "regime_fallback"
                Rp[m] = apply_style(U, F, m, c)
                fit_stats["period"][f"{g}/{r}/{k}"] = {"n_fit": int(fm.sum()), "n_all": int(m.sum()), "fit": level,
                                                       "style_r2_fit": r2}
    n_fb = sum(v["n_all"] for v in fit_stats["period"].values() if v["fit"] != "period")
    print(f"{model} period-level fit: {n_fb} of {st.height} statements use the regime fallback", flush=True)
    for name, A in (("style_resid", R), ("style_resid_period", Rp)):
        np.save(ED / f"statements_{name}32_{sfx}.npy", A.astype(np.float16))
    for level in ("day", "win30"):
        idx, gid, n = group_ids(st, level)
        np.save(ED / f"agent_{level}_white32_{sfx}.npy", group_plain_means(U[idx], gid, n))
        np.save(ED / f"agent_{level}_style_resid_{sfx}.npy", group_plain_means(R[idx], gid, n))
        np.save(ED / f"agent_{level}_style_resid_period_{sfx}.npy", group_plain_means(Rp[idx], gid, n))
    print(f"{model} style_resid built {time.time() - t0:.0f}s", flush=True)
    return fit_stats


# ----------------------------------------------------------------------------- check (H13 family field, topic structure)
def _h13():
    sys.path.insert(0, str(ROOT / "hypotheses/H13-family-fields/analysis"))
    sys.path.insert(0, str(ROOT / "hypotheses/H13-family-fields/scheme"))
    import build as h13build  # noqa: E402  (read-only import: UNITS, unit_days, roles_for)
    import h13lib  # noqa: E402
    return h13build, h13lib


def _ss_share(V: np.ndarray, labels: np.ndarray) -> float:
    """Between-label share of the total sum of squares of the rows of V."""
    mu = V.mean(0)
    tot = ((V - mu) ** 2).sum()
    btw = sum((labels == g).sum() * ((V[labels == g].mean(0) - mu) ** 2).sum() for g in np.unique(labels))
    return float(btw / tot) if tot > 0 else np.nan


def VARIANTS(U, R, P):
    return (("raw", U), ("sty", R), ("styp", P))


def check(models: list[str], nperm: int = 2000) -> None:
    from scipy.stats import spearmanr
    h13build, L = _h13()
    st = pl.read_parquet(ED / "statements.parquet").with_row_index("srow")
    roster = pl.read_parquet(OUT / "roster.parquet", columns=["agent", "lab"])
    lab_of = dict(zip(roster["agent"].to_list(), roster["lab"].to_list()))
    rows, unit_vecs = [], {}
    for model in models:
        sfx = MODELS[model]["suffix"]
        Uall = np.load(ED / f"statements_white32_{sfx}.npy").astype(np.float32)
        Rall = np.load(ED / f"statements_style_resid32_{sfx}.npy").astype(np.float32)
        Pall = np.load(ED / f"statements_style_resid_period32_{sfx}.npy").astype(np.float32)
        for u, spec in h13build.UNITS.items():
            days = h13build.unit_days(spec)  # asserts no holdout day
            s = st.filter((pl.col("kind") == "chat") & pl.col("pt_date").is_in(days))
            ad = (s.group_by("agent", "pt_date").agg(pl.col("srow"), pl.len().alias("n"))
                  .filter(pl.col("n") >= 3).sort("agent", "pt_date"))
            agents = ad["agent"].to_numpy(); dd = ad["pt_date"].to_numpy()
            roles = h13build.roles_for(days) if spec[1] >= 51 else {}
            rng = np.random.default_rng([20261004, sum(map(ord, u))])
            out = {"model": model, "unit": u, "goal_no": spec[1], "n_agent_days": ad.height}
            for var, A in VARIANTS(Uall, Rall, Pall):
                V = np.stack([A[r].mean(0) for r in ad["srow"].to_list()]).astype(np.float64)
                unit_vecs[(model, var, u)] = (V, dd)
                D = L.day_demean(V, dd, agents, min_agents=3)
                ags, H, nd = L.agent_means(D, agents, min_days=2)
                fam, multi = L.fam_labels([lab_of.get(int(a)) for a in ags])
                K = len(multi)
                keep = None
                if roles:
                    rl = [roles.get(int(a)) for a in ags]
                    keep = np.array([[not (rl[i] is not None and rl[i] == rl[j]) for j in range(len(ags))]
                                     for i in range(len(ags))])
                if K >= 1 and len(ags) >= 4:
                    r = L.field_test(H, fam, K, keep_pairs=keep, nperm=nperm, rng=rng, jack=True)
                    out.update({f"T_{var}": r["obs"], f"p_{var}": r["p"], f"se_{var}": r.get("se_jack", np.nan)})
                else:
                    out.update({f"T_{var}": np.nan, f"p_{var}": np.nan, f"se_{var}": np.nan})
                out[f"n_agents_{var}"] = int(len(ags)); out["K"] = K
                out[f"day_share_{var}"] = _ss_share(V, dd)
                out[f"agent_share_{var}"] = _ss_share(V, agents)
            Vr, _ = unit_vecs[(model, "raw", u)]
            iu = np.triu_indices(len(Vr), 1)
            cr = (L.unit(Vr) @ L.unit(Vr).T)[iu]
            for var in ("sty", "styp"):
                Vs, _ = unit_vecs[(model, var, u)]
                cs = (L.unit(Vs) @ L.unit(Vs).T)[iu]
                out[f"pair_spearman_raw_{var}"] = float(spearmanr(cr, cs).statistic)
            rows.append(out)
            print(model, u, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in out.items()
                             if k.startswith(("T_", "p_", "day_share", "agent_share", "pair"))}, flush=True)
    res = pl.DataFrame(rows)
    # cross-period topic structure (regime III): between-goal share of agent-day vectors and leave-one-day-out
    # nearest-centroid classification of the goal period (balanced accuracy; sub-units of a goal merged)
    cls = {}
    us = [u for u, sp in h13build.UNITS.items() if sp[2] == "III"]
    for model in models:
        for var in ("raw", "sty", "styp"):
            V = np.concatenate([L.unit(unit_vecs[(model, var, u)][0]) for u in us])
            goals = sorted({h13build.UNITS[u][1] for u in us})
            lab = np.concatenate([[goals.index(h13build.UNITS[u][1])] * len(unit_vecs[(model, var, u)][0]) for u in us])
            day = np.concatenate([unit_vecs[(model, var, u)][1] for u in us])
            pred = np.empty(len(lab), dtype=int)
            for d in np.unique(day):
                te = day == d; tr = ~te
                C = np.stack([L.unit(V[tr & (lab == i)].mean(0)) if (tr & (lab == i)).any() else np.zeros(V.shape[1])
                              for i in range(len(goals))])
                pred[te] = np.argmax(V[te] @ C.T, axis=1)
            bal = float(np.mean([(pred[lab == i] == i).mean() for i in range(len(goals))]))
            cls[f"{model}/{var}"] = {"balanced_acc": bal, "chance": 1 / len(goals), "goal_share": _ss_share(V, lab),
                                     "n": int(len(lab)), "goals": goals}
    summ = {"nperm": nperm, "unit_classification": cls}
    for model in models:
        r = res.filter(pl.col("model") == model)
        for var in ("raw", "sty", "styp"):
            ok = r.filter(pl.col(f"T_{var}").is_not_nan() & (pl.col(f"se_{var}") > 0))
            summ[f"{model}/{var}"] = {"n_units": ok.height,
                                      "n_p05": int((ok[f"p_{var}"] < 0.05).sum()),
                                      "re": L.dl_meta(ok[f"T_{var}"].to_numpy(), ok[f"se_{var}"].to_numpy()),
                                      "median_day_share": float(r[f"day_share_{var}"].median()),
                                      "median_agent_share": float(r[f"agent_share_{var}"].median())}
        sig = r.filter(pl.col("p_raw") < 0.05)
        for var in ("sty", "styp"):
            summ[f"{model}/{var}/retention_in_raw_p05_units"] = {
                "n": sig.height, "median": float((sig[f"T_{var}"] / sig["T_raw"]).median()) if sig.height else None,
                "survive_p05": int((sig[f"p_{var}"] < 0.05).sum())}
            summ[f"{model}/{var}/median_pair_spearman_vs_raw"] = float(r[f"pair_spearman_raw_{var}"].median())
    res.write_parquet(ED / "style_resid_check.parquet", compression="zstd")
    (ED / "style_resid_check.json").write_text(json.dumps(summ, indent=1, default=float))
    print(json.dumps(summ, indent=1, default=float), flush=True)


def main():
    args = sys.argv[1:]
    stage = args[0] if args and not args[0].startswith("--") else "build"
    models = list(MODELS)
    if "--models" in args:
        models = args[args.index("--models") + 1].split(",")
    if stage in ("build", "all"):
        st = pl.read_parquet(ED / "statements.parquet")
        F = style_matrix(st)
        stats = {m: build(m, st, F) for m in models}
        prov_path = ED / "style_resid_fit.json"
        prev = json.loads(prov_path.read_text()) if prov_path.exists() else {}
        prev.update(stats)
        prov_path.write_text(json.dumps(prev, indent=1))
        write_provenance("style_resid", ["embeddings/statements", "embeddings/{chat,intentions}_<model>.npy",
                                         "embeddings/whitening[_<model>]_<regime>.npz", "text_features",
                                         "intentions_text (style counts only)"],
                         {"models": sorted(prev), "dim": STYLE_DIM, "features": STYLE,
                          "fit": "OLS within (regime, kind) [style_resid] or (goal_no, regime, kind) [style_resid_period, "
                                 f">= {MIN_FIT_PERIOD} non-holdout statements, else the regime fit]; standardization and "
                                 "coefficients on non-holdout statements only",
                          "aggregation": "plain mean of unit vectors per existing agent_day / agent_win30 row"})
    if stage in ("check", "all"):
        check(models)


if __name__ == "__main__":
    main()
