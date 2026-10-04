"""H130 replication: every non-holdout #51 unit x vector variant (A1 estimators), plus O5 pair co-movement vs reads.

    uv run python hypotheses/H130-ou-private-wells-51/analysis/run_units.py [--B 200]
Output: data/processed/H130-ou-private-wells-51/results/{units.parquet, units.json, comove.parquet}
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h130lib as L  # noqa: E402

RES = L.DATA / "results"
VARIANTS = [("bge_small", "style_resid_period"), ("gte_modernbert", "style_resid_period"), ("bge_small", "white32")]


def subset(D: L.Data, units: list[str]) -> L.Data:
    st = D.st.filter(pl.col("unit_id").is_in(units))
    i = st["i"].to_numpy()
    st2 = st.drop("i").with_row_index("i")
    Z, H, ok = D.Z[i], D.H[i], D.ok[i]
    pos = pl.DataFrame({"srow_m": st2["srow"], "mi": st2["i"]})
    rd = D.rd.filter(pl.col("unit_id").is_in(units)).drop("mi").join(pos, on="srow_m", how="inner")
    return L.Data(st=st2, rd=rd, Z=Z, H=H, ok=ok, W=D.W)


def comovement(units_days: dict, model: str, variant: str) -> pl.DataFrame:
    """O5: H22's J^c per unit pair (agent-day-centred win30 vectors, r over shared windows minus the cross-day
    surrogate) with log(1 + mean daily reads both ways) and same lab."""
    w = pl.read_parquet(L.SH / "embeddings/agent_win30.parquet").with_row_index("row")
    V = np.load(L.SH / f"embeddings/agent_win30_{variant}_{model}.npy", mmap_mode="r")
    lab = dict(pl.read_parquet(L.SH / "roster.parquet").select("agent", "lab").iter_rows())
    pdr = pl.read_parquet(L.SH / "pair_day_reads.parquet").filter(pl.col("goal_no") == 51)
    rows = []
    for u, days in units_days.items():
        ww = w.filter(pl.col("pt_date").is_in(days) & (pl.col("goal_no") == 51) & ((pl.col("n_chat") + pl.col("n_intent")) >= 2))
        if ww.height == 0:
            continue
        X = np.asarray(V[ww["row"].to_numpy()], dtype=np.float64)
        X /= np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-9)
        a, d, win = ww["agent"].to_numpy(), ww["pt_date"].to_numpy(), ww["win30"].to_numpy()
        # agent-day centring
        key = np.array([f"{x}|{y}" for x, y in zip(a, d)])
        for k in np.unique(key):
            m = key == k
            X[m] -= X[m].mean(0) if m.sum() > 1 else X[m]
        pos = {ag: {} for ag in np.unique(a)}
        for r, (ag, dd, wi) in enumerate(zip(a, d, win)):
            pos[ag][(dd, wi)] = r
        ags = sorted(pos)
        dl = sorted(set(d))
        min_sh = 10 if len(dl) >= 4 else 5
        rd = pdr.filter(pl.col("pt_date").is_in(days)).group_by("i", "j").agg(
            ((pl.col("reads_i_from_j") + pl.col("reads_j_from_i")).sum() / len(days)).alias("rpd"))
        rmap = {(x, y): v for x, y, v in rd.iter_rows()}
        for k, i in enumerate(ags):
            for j in ags[k + 1:]:
                sh = [(pos[i][q], pos[j][q]) for q in pos[i] if q in pos[j]]
                if len(sh) < min_sh:
                    continue
                ai = np.array([s[0] for s in sh]); bj = np.array([s[1] for s in sh])
                den = np.sqrt((X[ai] ** 2).sum() * (X[bj] ** 2).sum())
                r_ = float((X[ai] * X[bj]).sum() / den) if den > 0 else np.nan
                sn = si = sj = 0.0
                for (dd, wi), ri in pos[i].items():
                    for e in dl:
                        if e == dd:
                            continue
                        rj = pos[j].get((e, wi))
                        if rj is None:
                            continue
                        sn += float(X[ri] @ X[rj]); si += float(X[ri] @ X[ri]); sj += float(X[rj] @ X[rj])
                rs = sn / np.sqrt(si * sj) if si > 0 and sj > 0 else 0.0
                rp = rmap.get((min(i, j), max(i, j)), 0.0)
                rows.append((u, int(i), int(j), r_ - rs, np.log1p(rp), float(lab.get(i) == lab.get(j)), len(sh)))
    return pl.DataFrame(rows, schema={"unit": pl.String, "i": pl.Int8, "j": pl.Int8, "J": pl.Float64, "lr": pl.Float64,
                                      "same_lab": pl.Float64, "n_shared": pl.Int32}, orient="row")


def comove_fit(P: pl.DataFrame) -> dict:
    """Per-unit OLS J ~ lr + same_lab with agent-jackknife SE; DL pool over units."""
    out = {}
    for u in sorted(P["unit"].unique().to_list()):
        q = P.filter(pl.col("unit") == u).drop_nulls()
        if q.height < 10:
            continue
        def fit(qq):
            Xm = np.column_stack([np.ones(qq.height), qq["lr"].to_numpy(), qq["same_lab"].to_numpy()])
            return np.linalg.lstsq(Xm, qq["J"].to_numpy(), rcond=None)[0][1]
        b = fit(q)
        ags = sorted(set(q["i"].to_list()) | set(q["j"].to_list()))
        jk = np.array([fit(q.filter((pl.col("i") != g) & (pl.col("j") != g))) for g in ags])
        se = float(np.sqrt((len(jk) - 1) / len(jk) * ((jk - jk.mean()) ** 2).sum()))
        out[u] = {"beta_R": float(b), "se": se, "n_pairs": q.height}
    est = np.array([v["beta_R"] for v in out.values()]); se = np.array([v["se"] for v in out.values()])
    mu, smu, t2, i2 = L.dl_pool(est, se)
    return {"units": out, "pool": {"beta_R": mu, "se": smu, "ci": [mu - 1.96 * smu, mu + 1.96 * smu], "tau2": t2, "I2": i2}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--B", type=int, default=200)
    ap.add_argument("--variants", default="all")
    a = ap.parse_args()
    RES.mkdir(parents=True, exist_ok=True)
    pu = pl.read_parquet(L.SH / "period_units.parquet").filter((pl.col("goal_no") == 51) & ~pl.col("holdout"))
    units = sorted(pu["unit_id"].to_list())
    udays = {r["unit_id"]: r["days"] for r in pu.iter_rows(named=True)}
    rows, full = [], {}
    vs = VARIANTS if a.variants == "all" else [VARIANTS[int(k)] for k in a.variants.split(",")]
    for model, variant in vs:
        D = L.load(model, variant)
        for u in units:
            t0 = time.time()
            Du = subset(D, [u])
            if Du.st.height < 50:
                continue
            r = L.analyze(Du, B=a.B, seed=17, do_old=True, do_natives=True)
            r.update({"unit": u, "model": model, "variant": variant, "n_days": len(udays[u])})
            full[f"{model}|{variant}|{u}"] = r
            rows.append({k: v for k, v in r.items() if not isinstance(v, list)} |
                        {k: json.dumps(v) for k, v in r.items() if isinstance(v, list)})
            print(model, variant, u, f"g_auto {r['g_auto']:.4f} g_kick {r['g_kick']:.4f} rho {r['rho']:.2f} "
                  f"J {r['J']:.4f} {np.round(r.get('ci_J', [np.nan]*2), 3)} Jp {r['J_pair']:.4f} R_C {r['R_C']:.2f} "
                  f"R_K {r['R_K']:.2f} ({time.time() - t0:.0f}s)", flush=True)
            pl.DataFrame(rows).write_parquet(RES / "units.parquet")
            (RES / "units.json").write_text(json.dumps(full, default=float))
    # O5 co-movement
    cm = {}
    for model, variant in vs:
        P = comovement(udays, model, variant)
        P.with_columns(pl.lit(model).alias("model"), pl.lit(variant).alias("variant")).write_parquet(
            RES / f"comove_{model}_{variant}.parquet")
        cm[f"{model}|{variant}"] = comove_fit(P)
        print("comove", model, variant, cm[f"{model}|{variant}"]["pool"], flush=True)
    (RES / "comove.json").write_text(json.dumps(cm, indent=1, default=float))


if __name__ == "__main__":
    main()
