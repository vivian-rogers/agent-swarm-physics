"""H130 natives and pooled #51 estimates (A1 estimators), primary variant style_resid_period x bge_small (+ gte).

  pooled  every non-holdout #51 unit at once, agent-day bootstrap stratified by unit (gamma_auto, gamma_kick, J, N2)
  N1      rival kicks: sender-specific dose coefficients split by DQ6 same-role rival pairs (bins 0-63 calls)
  N3      joiners: day-1 approach to the own well vs calls since the first #51 call; gamma_J vs gamma_auto
    uv run python hypotheses/H130-ou-private-wells-51/analysis/natives.py [--B 200]
Output: data/processed/H130-ou-private-wells-51/results/natives.json
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h130lib as L  # noqa: E402

RES = L.DATA / "results"


def rival_flags(D: L.Data, Ds: L.Dose) -> np.ndarray:
    g = pl.read_parquet(L.SH / "ground_truth_labels.parquet").filter(
        (pl.col("goal_no") == 51) & (pl.col("label_kind") == "rival_pair") & pl.col("preferred") & ~pl.col("holdout"))
    ag_all = np.unique(D.st["agent"].to_numpy())
    nA = len(ag_all)
    pc = Ds.pair % (nA * nA)
    i_ag = ag_all[pc // nA]
    j_ag = ag_all[pc % nA]
    t = D.st["t"].dt.epoch("us").to_numpy()[Ds.extra["bid"]]
    flag = np.zeros(len(Ds.y), bool)
    for r in g.iter_rows(named=True):
        lo = r["t_valid_from"].timestamp() * 1e6
        hi = r["t_valid_to"].timestamp() * 1e6
        a, b = r["agent_a"], r["agent_b"]
        flag |= (((i_ag == a) & (j_ag == b)) | ((i_ag == b) & (j_ag == a))) & (t >= lo) & (t < hi)
    return flag


def n1(D: L.Data, B: int) -> dict:
    X = np.where(D.ok[:, None], D.Z - np.nan_to_num(D.H), 0.0)
    Ds = L.dose_design(D, X)
    rv = rival_flags(D, Ds)
    cols = list(range(8))
    base = L.with_totals(Ds, cols)              # [R_j, T]
    Rj = Ds.R[:, :8]
    Xd = np.column_stack([Rj * rv[:, None], Rj * (~rv)[:, None], base[:, 8:]])
    D2 = L.Dose(pair=Ds.pair, ad=Ds.ad, unit=Ds.unit, y=Ds.y, R=Xd, tau=Ds.tau, extra={})
    Bw = L.boot_weights(Ds.unit, B, 5)
    f = L.dose_fit(D2, None, Bw)
    sel = [0, 1, 2, 3, 4]                       # R0m, R0o, R1_3, R4_15, R16_63
    kr = f["beta"][sel].sum()
    ko = f["beta"][[8 + s for s in sel]].sum()
    br = f["boot"][:, sel].sum(1)
    bo = f["boot"][:, [8 + s for s in sel]].sum(1)
    ratio = br / bo
    return {"kappa_rival": float(kr), "kappa_other": float(ko), "ratio": float(kr / ko) if ko else np.nan,
            "ci_ratio": np.nanpercentile(ratio, [2.5, 97.5]).tolist(), "ci_rival": np.percentile(br, [2.5, 97.5]).tolist(),
            "ci_other": np.percentile(bo, [2.5, 97.5]).tolist(), "rival_rows": int(rv.sum()),
            "rival_reads_0_63": float(Ds.R[rv][:, sel].sum()), "other_reads_0_63": float(Ds.R[~rv][:, sel].sum())}


def n3(D: L.Data, g_auto: float, B: int) -> dict:
    """Joiners: first #51 day; d = (z_B - mean of other agents' wells) . unit(h_J - that mean) / |h_J - that mean|."""
    ro = pl.read_parquet(L.SH / "roster.parquet").filter(pl.col("joined") > "2026-07-06").select("agent", "joined")
    st = D.st
    first_day = st.group_by("agent").agg(pl.col("pt_date").min().alias("d1"), pl.col("pt_date").n_unique().alias("nd"))
    J = ro.join(first_day, on="agent").filter(pl.col("nd") >= 2)
    rows = []
    for ag, joined, d1, nd in J.iter_rows():
        hJ = D.W.get((ag, d1))
        if hJ is None:
            continue
        others = [v for (a2, dd), v in D.W.items() if dd == d1 and a2 != ag]
        c = np.mean(others, 0)
        e = hJ - c
        ne = np.linalg.norm(e)
        sub = st.filter((pl.col("agent") == ag) & (pl.col("pt_date") == d1))
        z = D.Z[sub["i"].to_numpy()]
        d = (z - c) @ e / ne ** 2
        n0 = sub["n"].min()
        for nn, dv in zip(sub["n"].to_numpy(), d):
            rows.append((int(ag), d1, int(nn - n0), float(dv)))
    df = pl.DataFrame(rows, schema={"agent": pl.Int64, "day": pl.String, "n": pl.Int64, "d": pl.Float64}, orient="row")
    out = {"joiners": sorted(set(df["agent"].to_list())), "n_statements": df.height}
    def fit(dd):
        edges = np.array([0, 25, 50, 100, 200, 400, 800, 1600])
        b = np.searchsorted(edges, dd["n"].to_numpy(), "right") - 1
        m = (b >= 0) & (b < len(edges) - 1)
        y = dd["d"].to_numpy()[m]; bb = b[m]; nn = dd["n"].to_numpy()[m]
        tau = np.array([nn[bb == k].mean() if (bb == k).any() else np.nan for k in range(len(edges) - 1)])
        mu = np.array([y[bb == k].mean() if (bb == k).sum() >= 3 else np.nan for k in range(len(edges) - 1)])
        se = np.array([y[bb == k].std() / np.sqrt((bb == k).sum()) if (bb == k).sum() >= 3 else np.nan
                       for k in range(len(edges) - 1)])
        f = L.expfit(tau, mu, se, plateau=True)          # d = A e^{-g n} + B ; approach means A < 0
        return f, tau, mu, se
    f, tau, mu, se = fit(df)
    out.update({"fit": f, "tau": tau.tolist(), "d_bins": mu.tolist(), "se": se.tolist(),
                "gamma_J": f["g"], "ratio_to_gamma_auto": f["g"] / g_auto if f["ok"] else np.nan,
                "approach": bool(f["ok"] and f["A"] < 0)})
    rng = np.random.default_rng(3)
    ags = np.array(out["joiners"])
    gs = []
    for _ in range(B):
        pick = rng.choice(ags, len(ags))
        dd = pl.concat([df.filter(pl.col("agent") == a) for a in pick])
        gs.append(fit(dd)[0]["g"])
    out["ci_gamma_J"] = np.nanpercentile(np.array(gs, float), [2.5, 97.5]).tolist()
    # mean day-1 d vs day-2+ d of the same joiners (well reached?)
    later = []
    for ag in ags:
        sub = st.filter((pl.col("agent") == int(ag)))
        days = sorted(set(sub["pt_date"].to_list()))
        for dd in days[1:]:
            hJ = D.W.get((int(ag), days[0]))
            others = [v for (a2, d2), v in D.W.items() if d2 == days[0] and a2 != ag]
            c = np.mean(others, 0); e = hJ - c
            z = D.Z[sub.filter(pl.col("pt_date") == dd)["i"].to_numpy()]
            later.extend(((z - c) @ e / np.linalg.norm(e) ** 2).tolist())
    out["d_day1_mean"] = float(df["d"].mean())
    out["d_later_mean"] = float(np.mean(later)) if later else np.nan
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--B", type=int, default=200)
    a = ap.parse_args()
    out = {}
    for model in ("bge_small", "gte_modernbert"):
        D = L.load(model, "style_resid_period")
        pooled = L.analyze(D, B=a.B, seed=23, do_old=False, do_natives=True)
        out[f"pooled|{model}"] = pooled
        print(model, "pooled", {k: pooled[k] for k in ("g_auto", "g_kick", "rho", "J", "R_C", "R_K")},
              pooled.get("ci_rho90"), pooled.get("ci_R_K"), pooled.get("ci_R_C"), flush=True)
        out[f"N1|{model}"] = n1(D, a.B)
        print(model, "N1", out[f"N1|{model}"], flush=True)
        out[f"N3|{model}"] = n3(D, pooled["g_auto"], a.B)
        print(model, "N3", {k: v for k, v in out[f"N3|{model}"].items() if k not in ("tau", "se")}, flush=True)
        (RES / "natives.json").write_text(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
