"""H112 round 1: per-period contrasts, pooled tests (P1, P1', P2-P5), sensitivity variants and natives (G44, G51, G42).

Usage: uv run python hypotheses/H112-crossing-claims-two-cycles/analysis/run.py
Reads data/processed/H112-crossing-claims-two-cycles/G<NN>/ (built by scheme/build.py; non-holdout only).
Writes .../results/{periods.json, pooled.json, natives.json, pairs_all.parquet}.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "scheme"))
import h112lib as L  # noqa: E402
import h112scheme as S  # noqa: E402

D = S.ROOT / "data/processed/H112-crossing-claims-two-cycles"
RES = D / "results"
SHARED_WEEKS = [31, 36, 38, 41]       # H93 beta J > 0 (work); #33 and #40 have < 10 pairs
AF_WEEKS = [42, 51]                   # H93 beta J < 0
NATIVE = {44, 51, 42}


def load(g: int) -> tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame]:
    d = D / f"G{g:02d}"
    p = pl.read_parquet(d / "pairs.parquet"); s = pl.read_parquet(d / "solo.parquet")
    w = pl.read_parquet(d / "work_pairs.parquet") if (d / "work_pairs.parquet").exists() else pl.DataFrame()
    return p, s, w


def planted_power(n_read: int, n_un: int, p0: float = 0.3, rr: float = 2.0, reps: int = 400, seed: int = 0) -> float:
    """Power of the (single-stratum) RR CI > 1 for a planted RR at base rate p0 with the period's class counts."""
    rng = np.random.default_rng(seed); hit = 0
    if n_read < 5 or n_un < 5:
        return float("nan")
    for _ in range(reps):
        a = rng.binomial(n_un, min(1, rr * p0)); c = rng.binomial(n_read, p0)
        y = np.r_[np.ones(a), np.zeros(n_un - a), np.ones(c), np.zeros(n_read - c)]
        x = np.r_[np.ones(n_un, bool), np.zeros(n_read, bool)]
        r = L.mh_rr(y, x, np.zeros(len(y)))
        hit += np.isfinite(r["lo"]) and r["lo"] > 1
    return hit / reps


def verdict(c: dict, testable: bool, power: float) -> str:
    if not testable:
        return "descriptive"
    r = c["rr_u"]
    if not np.isfinite(r.get("rr", np.nan)):
        return "descriptive"
    if r["rr"] >= 2 and r["lo"] > 1:
        return "supported"
    if np.isfinite(r["hi"]) and r["hi"] < 1:
        return "failed"
    if np.isfinite(r["lo"]) and r["lo"] <= 1 and power >= 0.8:
        return "failed"
    return "mixed"


def main():
    RES.mkdir(parents=True, exist_ok=True)
    periods = sorted(int(p.name[1:]) for p in D.glob("G*") if p.is_dir())
    per, frames, solos, works = {}, [], [], []
    for g in periods:
        p, s, w = load(g)
        pf = L.pair_frame(p, unit=f"G{g:02d}")
        if len(pf):
            frames.append(pf)
        if len(s):
            solos.append(s.with_columns(pl.lit(f"G{g:02d}").alias("unit")))
        n_read = int(pf["read"].sum()) if len(pf) else 0
        n_un = int(pf["unaware"].sum()) if len(pf) else 0
        testable = len(pf) >= 30 and n_read >= 5 and n_un >= 5
        c = L.contrasts(pf, n_perm=2000, seed=g) if len(pf) else {"n_pairs": 0}
        pw = planted_power(n_read, n_un)
        out = {"goal_no": g, "testable": testable, "power_rr2_p03": pw, **c}
        for K in (10, 20):
            pk = L.pair_frame(p, K=K, unit=f"G{g:02d}")
            if len(pk) and pk["read"].sum() and pk["unaware"].sum():
                out[f"rr_u_K{K}"] = L.mh_rr(pk["any"].to_numpy(), pk["unaware"].to_numpy(), L.strata_of(pk))
        if len(w) and "wdep_i" in w.columns:
            ww = w.filter((pl.col("wdep_i") >= 0) & (pl.col("wdep_j") >= 0))
            if len(ww):
                ww = ww.with_columns(((pl.col("wdep_i") + pl.col("wdep_j")) >= 1).cast(pl.Int8).alias("any"),
                                     (pl.col("cls") != "read").alias("unaware"), pl.lit(f"G{g:02d}").alias("unit"))
                works.append(ww)
                out["work"] = {"n": len(ww), "n_read": int((~ww["unaware"]).sum()), "n_unaware": int(ww["unaware"].sum()),
                               "p_any_read": float(ww.filter(~pl.col("unaware"))["any"].mean() or np.nan) if (~ww["unaware"]).sum() else None,
                               "p_any_unaware": float(ww.filter(pl.col("unaware"))["any"].mean() or np.nan) if ww["unaware"].sum() else None}
        out["verdict"] = verdict(c, testable, pw) if len(pf) else "descriptive"
        per[g] = out
        print(g, out["verdict"], {k: (round(v["rr"], 2) if isinstance(v, dict) and "rr" in v and np.isfinite(v["rr"]) else None)
                                  for k, v in out.items() if k.startswith("rr_")}, "n", out.get("n_pairs"), "testable", testable,
              "power", round(pw, 2) if np.isfinite(pw) else None, flush=True)
    allp = pl.concat(frames, how="diagonal_relaxed")
    allp.write_parquet(RES / "pairs_all.parquet")
    solo = pl.concat(solos, how="diagonal_relaxed")
    testable_units = [f"G{g:02d}" for g, o in per.items() if o["testable"]]
    tp = allp.filter(pl.col("unit").is_in(testable_units))
    pooled = {"testable_units": testable_units}
    # P1 pooled (testable), and all periods
    for name, df in (("testable", tp), ("all", allp)):
        st = L.strata_of(df); y = df["any"].to_numpy()
        r = L.mh_rr(y, df["unaware"].to_numpy(), st)
        r["p_perm"] = L.perm_p(y, df["unaware"].to_numpy(), st, r["rr"], 2000, 7)
        pooled[f"rr_u_{name}"] = r
        sub = df.filter(pl.col("cls") != "silent")
        pooled[f"rr_f_{name}"] = L.mh_rr(sub["any"].to_numpy(), sub["inflight"].to_numpy(), L.strata_of(sub)) \
            if sub["inflight"].sum() else {"rr": None}
        pooled[f"n_{name}"] = {"pairs": len(df), "read": int(df["read"].sum()), "silent": int((df["cls"] == "silent").sum()),
                               "inflight": int(df["inflight"].sum())}
        pooled[f"p_any_{name}"] = {c: float(df.filter(pl.col("cls") == c)["any"].mean() or np.nan) for c in ("read", "silent", "inflight")
                                   if (df["cls"] == c).sum()}
        days = (df["unit"] + "|" + df["pt_date"]).to_numpy()
        for lab, m in (("unaware", df["unaware"].to_numpy()), ("read", df["read"].to_numpy())):
            pooled[f"M_{lab}_{name}"] = L.mutual_excess(df["di"].to_numpy()[m], df["dj"].to_numpy()[m], days[m], seed=3)
        pooled[f"stick_{name}"] = L.stick_ratio(df, solo.filter(pl.col("unit").is_in(df["unit"].unique().implode())))
    # P5 per-period direction
    rrs = [o["rr_u"]["rr"] for g, o in per.items() if o["testable"] and np.isfinite(o["rr_u"].get("rr", np.nan))]
    pooled["P5_share_rr_gt1"] = {"k": int(np.sum(np.array(rrs) > 1)), "n": len(rrs)}
    # P4 phase contrast
    def pool_units(units):
        df = allp.filter(pl.col("unit").is_in(units))
        return L.mh_rr(df["any"].to_numpy(), df["unaware"].to_numpy(), L.strata_of(df)) if len(df) else {"rr": None}
    pooled["P4_af"] = pool_units([f"G{g:02d}" for g in AF_WEEKS]); pooled["P4_shared"] = pool_units([f"G{g:02d}" for g in SHARED_WEEKS])
    if pooled["P4_af"].get("rr") and pooled["P4_shared"].get("rr"):
        a, b = pooled["P4_af"], pooled["P4_shared"]
        lr = np.log(a["rr"]) - np.log(b["rr"]); se = np.sqrt(a.get("se_log", np.nan) ** 2 + b.get("se_log", np.nan) ** 2)
        pooled["P4_ratio"] = {"ratio": float(np.exp(lr)), "lo": float(np.exp(lr - 1.96 * se)), "hi": float(np.exp(lr + 1.96 * se))}
    # sensitivity: same-lab vs cross-lab, regime III only, pair strata (pair fixed effects)
    for lab_name, cond in (("same_lab", pl.col("same_lab")), ("cross_lab", ~pl.col("same_lab"))):
        df = tp.filter(cond)
        pooled[f"rr_u_{lab_name}"] = L.mh_rr(df["any"].to_numpy(), df["unaware"].to_numpy(), L.strata_of(df)) if len(df) else {}
    r3 = [f"G{g:02d}" for g in per if g >= 37]
    df = tp.filter(pl.col("unit").is_in(r3))
    pooled["rr_u_regime3"] = L.mh_rr(df["any"].to_numpy(), df["unaware"].to_numpy(), L.strata_of(df)) if len(df) else {}
    pairkey = tp.select(pl.col("unit") + "|" + pl.min_horizontal("ai", "aj").cast(pl.String) + "-"
                        + pl.max_horizontal("ai", "aj").cast(pl.String)).to_series().to_numpy()
    disc = 0
    for k in np.unique(pairkey):
        m = pairkey == k
        disc += int(tp["read"].to_numpy()[m].any() and tp["unaware"].to_numpy()[m].any())
    pooled["pair_fe"] = {"pairs_with_both_classes": disc,
                         "rr": L.mh_rr(tp["any"].to_numpy(), tp["unaware"].to_numpy(), pairkey) if disc >= 20 else "n.i. (< 20 pairs with both classes)"}
    for K in (10, 20):
        pk = pl.concat([L.pair_frame(load(int(u[1:]))[0], K=K, unit=u) for u in testable_units], how="diagonal_relaxed")
        pooled[f"rr_u_testable_K{K}"] = L.mh_rr(pk["any"].to_numpy(), pk["unaware"].to_numpy(), L.strata_of(pk))
    if works:
        wk = pl.concat(works, how="diagonal_relaxed")
        st = (wk["unit"] + "|" + wk["lag_bin"].cast(pl.String) + "|" + wk["named"].cast(pl.String)).to_numpy()
        pooled["rr_u_work"] = {**L.mh_rr(wk["any"].to_numpy(), wk["unaware"].to_numpy(), st), "n": len(wk),
                               "n_read": int((~wk["unaware"]).sum())}
    (RES / "periods.json").write_text(json.dumps(per, indent=1, default=float))
    (RES / "pooled.json").write_text(json.dumps(pooled, indent=1, default=float))
    print(json.dumps(pooled, indent=1, default=float)[:6000])


if __name__ == "__main__":
    main()
