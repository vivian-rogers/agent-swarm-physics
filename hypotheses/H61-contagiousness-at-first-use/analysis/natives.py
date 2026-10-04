"""H61 native tests (predictions in the period READMEs, written 2026-10-04 19:30 UTC before running).

  G26   elected leader (DQ6 term1, agent 17): raw vs feature-adjusted odds ratio for Y
  G35   designated lead designers (DQ6, 6 agent-days): lead-day OR without and with poster terms
  NE42  #39 -> #40 -> #41: transfer of F+ (receptive count) vs B3 across the merge and the split
  uv run python hypotheses/H61-contagiousness-at-first-use/analysis/natives.py
Output: data/processed/H61-contagiousness-at-first-use/results/natives.json
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2"

import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h61lib as L  # noqa: E402

ROOT = HERE.parents[2]
OUT = ROOT / "data/processed/H61-contagiousness-at-first-use"
SH = ROOT / "data/processed/shared"
ADJ = ["lg_novel", "lg_len", "spec", "f_rec", "addressed", "threaded", "kick", "lg_npres"]


def gt(goal: int, kind: str) -> pl.DataFrame:
    g = pl.read_parquet(SH / "ground_truth_labels.parquet")
    return g.filter((pl.col("goal_no") == goal) & (pl.col("label_kind") == kind) & pl.col("preferred") & ~pl.col("holdout"))


def or_fit(df: pl.DataFrame, flag: str, feats: list[str], poster: bool, B: int = 500, seed: int = 0) -> dict:
    """Near-MLE logistic (ridge 1e-3) for y on flag + class + feats (+ poster dummies); OR with a seed-message
    cluster bootstrap CI and a Wald CI."""
    spec = dict(cls=bool(feats), poster=poster, feats=feats)
    tr = np.ones(df.height, bool)
    X, names, pen = L._design(df, spec, tr)
    X = np.column_stack([X, df[flag].to_numpy().astype(float)])
    pen = np.r_[pen, True]
    y = df["y"].to_numpy().astype(float)
    b = L.fit_logit(X, y, pen, lam=1e-3)
    se = L.hess_se(X, y, b, pen, lam=1e-3)[-1]
    cl = df["seed_msg"].to_numpy()
    rng = np.random.default_rng(seed)
    uc, inv = np.unique(cl, return_inverse=True)
    members = [np.where(inv == k)[0] for k in range(len(uc))]
    bs = []
    for _ in range(B):
        idx = np.concatenate([members[k] for k in rng.integers(0, len(uc), len(uc))])
        if y[idx].sum() < 3 or X[idx, -1].sum() < 3:
            continue
        bb = L.fit_logit(X[idx], y[idx], pen, lam=1e-3)
        bs.append(bb[-1])
    q = np.percentile(bs, [2.5, 97.5]) if len(bs) > 50 else (np.nan, np.nan)
    return dict(OR=float(np.exp(b[-1])), lo=float(np.exp(q[0])), hi=float(np.exp(q[1])),
                wald_lo=float(np.exp(b[-1] - 1.96 * se)), wald_hi=float(np.exp(b[-1] + 1.96 * se)),
                n=int(df.height), n_flag=int(df[flag].sum()), y_flag=float(df.filter(pl.col(flag) == 1)["y"].mean()),
                y_other=float(df.filter(pl.col(flag) == 0)["y"].mean()), n_boot=len(bs))


def native_g26() -> dict:
    lt = gt(26, "leader").sort("t_valid_from")
    t_from = lt["t_valid_from"][0]
    leader = int(lt["agent"][0])
    df = L.prep(pl.read_parquet(OUT / "G26/ideas.parquet"))
    t_us = int(t_from.timestamp() * 1e6)
    d = df.filter(pl.col("t0_us") >= t_us).with_columns((pl.col("poster") == leader).cast(pl.Int8).alias("lead"))
    raw = or_fit(d, "lead", [], poster=False, seed=26)
    adj = or_fit(d, "lead", ADJ, poster=False, seed=27)
    nov = d.group_by("lead").agg(pl.col("n_novel").mean().alias("novel_per_seed_msg_item"),
                                 pl.col("seed_msg").n_unique().alias("seed_msgs"), pl.len().alias("ideas")).sort("lead")
    a_pass = raw["OR"] < 1
    b_pass = adj["OR"] >= 0.7 or (adj["lo"] <= 1 <= adj["hi"])
    b_fail = adj["OR"] <= 0.5 and adj["hi"] < 0.7
    v = "supported" if (a_pass and b_pass) else ("failed" if not b_pass else "mixed")
    nv = {int(r["lead"]): r for r in nov.to_dicts()}
    text = (f"*Run 2026-10-04 after the prediction above.* Leader = agent {leader}; ideas seeded from {t_from} to the end of "
            f"the non-holdout period: {d.height} ({raw['n_flag']} by the leader, from {nv[1]['seed_msgs']} messages; "
            f"{nv[0]['ideas']} by the other agents, from {nv[0]['seed_msgs']} messages). Mean novel items per seeding item's "
            f"message: leader {nv[1]['novel_per_seed_msg_item']:.1f}, others {nv[0]['novel_per_seed_msg_item']:.1f}.\n\n"
            "| Prediction | Observed (OR, seed-message cluster bootstrap 95% CI) | Verdict |\n| --- | --- | --- |\n"
            f"| N26-a raw OR < 1 | {raw['OR']:.2f} [{raw['lo']:.2f}, {raw['hi']:.2f}]; P(Y) leader {raw['y_flag']:.3f} vs others {raw['y_other']:.3f} | {'pass' if a_pass else 'fail'} |\n"
            f"| N26-b adjusted OR ≥ 0.7 or CI ∋ 1 | {adj['OR']:.2f} [{adj['lo']:.2f}, {adj['hi']:.2f}] (Wald [{adj['wald_lo']:.2f}, {adj['wald_hi']:.2f}]) | "
            f"{'pass' if b_pass else ('fail' if b_fail else 'fail (between thresholds)')} |\n\n**Native verdict: {v}.**\n")
    return dict(verdict=v, text=text, raw=raw, adj=adj, leader=leader)


def native_g35() -> dict:
    lt = gt(35, "leader")
    df = L.prep(pl.read_parquet(OUT / "G35/ideas.parquet"))
    rows = []
    for r in lt.to_dicts():
        a = int(r["agent"]); lo = int(r["t_valid_from"].timestamp() * 1e6); hi = int(r["t_valid_to"].timestamp() * 1e6)
        rows.append((a, lo, hi))
    lo_all = min(x[1] for x in rows); hi_all = max(x[2] for x in rows)
    d = df.filter((pl.col("t0_us") >= lo_all) & (pl.col("t0_us") < hi_all))
    t0 = d["t0_us"].to_numpy(); po = d["poster"].to_numpy()
    lead = np.zeros(d.height, np.int8)
    for a, lo, hi in rows:
        lead |= ((po == a) & (t0 >= lo) & (t0 < hi)).astype(np.int8)
    d = d.with_columns(pl.Series("lead", lead))
    raw = or_fit(d, "lead", [], poster=False, seed=35)
    adj = or_fit(d, "lead", ADJ, poster=True, seed=36)
    a_pass = raw["lo"] <= 1 <= raw["hi"]
    b_pass = adj["lo"] <= 1 <= adj["hi"]
    b_fail = adj["OR"] > 1.5 and adj["lo"] > 1
    v = "supported" if (a_pass and b_pass) else ("failed" if b_fail or not b_pass else "mixed")
    text = (f"*Run 2026-10-04 after the prediction above.* Lead-designer days 2026-03-16 → 03-18: {d.height} seeded ideas, "
            f"{raw['n_flag']} seeded by an agent on its lead day.\n\n"
            "| Prediction | Observed (OR, seed-message cluster bootstrap 95% CI) | Verdict |\n| --- | --- | --- |\n"
            f"| N35-a raw OR CI ∋ 1 | {raw['OR']:.2f} [{raw['lo']:.2f}, {raw['hi']:.2f}]; P(Y) lead {raw['y_flag']:.3f} vs others {raw['y_other']:.3f} | {'pass' if a_pass else 'fail'} |\n"
            f"| N35-b OR with features + poster terms, CI ∋ 1 | {adj['OR']:.2f} [{adj['lo']:.2f}, {adj['hi']:.2f}] (Wald [{adj['wald_lo']:.2f}, {adj['wald_hi']:.2f}]) | "
            f"{'pass' if b_pass else 'fail'} |\n\n**Native verdict: {v}.**\n")
    return dict(verdict=v, text=text, raw=raw, adj=adj)


def transfer(tr_df: pl.DataFrame, te_df: pl.DataFrame, models: dict, B: int = 1000, seed: int = 0) -> dict:
    both = pl.concat([tr_df, te_df], how="diagonal_relaxed")
    tr = np.r_[np.ones(tr_df.height, bool), np.zeros(te_df.height, bool)]
    y = both["y"].to_numpy().astype(float)
    out = {}
    for name, spec in models.items():
        X, names, pen = L._design(both, spec, tr)
        b = L.fit_logit(X[tr], y[tr], pen)
        p = L.predict(b, X[~tr])
        out[name] = dict(ll=L.ll(y[~tr], p), mean_p=float(p.mean()))
    yt = y[~tr]
    d = (out["Fplus"]["ll"] - out["B3"]["ll"]) * 1000
    bs = L.cluster_boot(lambda idx: d[idx].mean(), te_df["seed_msg"].to_numpy(), B, np.random.default_rng(seed))
    return dict(dll=float(d.mean()), lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5)),
                obs=float(yt.mean()), p_F=out["Fplus"]["mean_p"], p_B3=out["B3"]["mean_p"], n=int(len(yt)))


def native_ne42() -> dict:
    W = {}
    for g in (39, 40, 41):
        W[g] = L.prep(pl.read_parquet(OUT / f"G{g:02d}/ideas.parquet")).with_columns(
            (pl.col("n_receptive").cast(pl.Float64) + 1).log().alias("lg_nrec"))
    fplus = ["lg_novel", "lg_len", "spec", "indeg", "lg_nrec", "addressed", "threaded", "kick", "lg_npres"]
    models = {"B3": dict(cls=True, poster=True, feats=[]), "Fplus": dict(cls=True, poster=True, feats=fplus)}
    t1 = transfer(W[39], W[40], models, seed=4240)
    t2 = transfer(W[40], W[41], models, seed=4241)
    coef = {}
    for g in (39, 40, 41):
        X, names, pen = L._design(W[g], models["Fplus"], np.ones(W[g].height, bool))
        y = W[g]["y"].to_numpy().astype(float)
        b = L.fit_logit(X, y, pen)
        se = L.hess_se(X, y, b, pen)
        i = names.index("lg_nrec")
        coef[g] = (float(b[i]), float(se[i]))
    npres = {g: float(W[g]["n_present"].median()) for g in W}
    nrec = {g: float(W[g]["n_receptive"].mean()) for g in W}
    a_pass = [t["lo"] > 0 for t in (t1, t2)]
    b_pass = abs(t1["p_F"] - t1["obs"]) < abs(t1["p_B3"] - t1["obs"])
    c_pass = all(coef[g][0] > 0 for g in coef)
    v = "supported" if (all(a_pass) and b_pass) else ("failed" if not any(a_pass) else "mixed")
    text = (f"*Run 2026-10-04 after the prediction above.* Agents present per room-day (median): #39 {npres[39]:.0f}, "
            f"#40 {npres[40]:.0f}, #41 {npres[41]:.0f}; mean receptive count (5 min): {nrec[39]:.1f}, {nrec[40]:.1f}, {nrec[41]:.1f}.\n\n"
            "| Prediction | Observed | Verdict |\n| --- | --- | --- |\n"
            f"| N42-a #39 → #40: ΔLL(F⁺ − B3) > 0, CI > 0 | {t1['dll']:.1f} [{t1['lo']:.1f}, {t1['hi']:.1f}] millinats/idea ({t1['n']} ideas) | {'pass' if a_pass[0] else 'fail'} |\n"
            f"| N42-a #40 → #41 | {t2['dll']:.1f} [{t2['lo']:.1f}, {t2['hi']:.1f}] ({t2['n']} ideas) | {'pass' if a_pass[1] else 'fail'} |\n"
            f"| N42-b #40 calibration: F⁺ closer to observed than B3 | observed {t1['obs']:.3f}; F⁺ {t1['p_F']:.3f}; B3 {t1['p_B3']:.3f} | {'pass' if b_pass else 'fail'} |\n"
            f"| N42-c receptive-count coefficient > 0 in each week | #39 {coef[39][0]:+.2f} ± {coef[39][1]:.2f}; #40 {coef[40][0]:+.2f} ± {coef[40][1]:.2f}; #41 {coef[41][0]:+.2f} ± {coef[41][1]:.2f} | {'pass' if c_pass else 'fail'} |\n\n"
            f"**Native verdict: {v}.** #41 calibration (descriptive): observed {t2['obs']:.3f}; F⁺ {t2['p_F']:.3f}; B3 {t2['p_B3']:.3f}.\n")
    return dict(verdict=v, text=text, t39_40=t1, t40_41=t2, coef=coef, npres=npres, nrec=nrec)


def main():
    res = {"G26": native_g26(), "G35": native_g35(), "NE42": native_ne42()}
    (OUT / "results").mkdir(parents=True, exist_ok=True)
    (OUT / "results/natives.json").write_text(json.dumps(res, indent=1, default=float))
    for k, v in res.items():
        print(k, v["verdict"])
        print(v["text"])


if __name__ == "__main__":
    main()
