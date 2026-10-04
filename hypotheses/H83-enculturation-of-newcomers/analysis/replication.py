"""H83 replication layer: the enculturation index and its companions on every eligible join (non-holdout only).

  uv run python hypotheses/H83-enculturation-of-newcomers/analysis/replication.py
Output: data/processed/H83-enculturation-of-newcomers/replication/replication.json
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h83lib as L  # noqa: E402

OUTD = L.DATA / "replication"
CRIT = 0.032   # Amendment A1.1: larger synthetic null 95th percentile of the mean Delta G


def jsonable(r):
    out = {}
    for k, v in r.items():
        if isinstance(v, dict):
            out[k] = {kk: (float(vv) if isinstance(vv, (np.floating, float)) else vv) for kk, vv in v.items()}
        elif isinstance(v, (np.integer,)):
            out[k] = int(v)
        elif isinstance(v, (np.floating,)):
            out[k] = float(v)
        else:
            out[k] = v
    return out


def dose_regression(res, days, doses, B=2000, seed=1):
    """Day-level: G_{i,d} (tau 2-14) on log1p(cumulative veteran reads before d) and log tau, newcomer FE."""
    ad, vill = res["ad"], res["vill"]
    rows = []
    for a, r in res["joins"].items():
        dd = doses.filter(pl.col("agent") == a)
        m = dict(zip(dd["pt_date"].to_list(), dd["items_vet"].to_list()))
        after = [d for d in days if d >= r["join_day"]][:14]
        cum = 0
        for t, d in enumerate(after, start=1):
            if t >= 2 and (a, d) in ad.loc:
                k = ad.loc[(a, d)]
                g = L.day_gap(ad, vill, [a], d)
                if g is not None:
                    rows.append((a, r["join_day"], t, np.log1p(cum), g[0]))
            cum += m.get(d, 0)
    if len(rows) < 20:
        return None
    df = pl.DataFrame(rows, schema=["agent", "join_day", "tau", "ldose", "gap"], orient="row")

    def fit(df_):
        y = df_["gap"].to_numpy().copy(); x1 = df_["ldose"].to_numpy().copy(); x2 = np.log(df_["tau"].to_numpy().astype(float))
        ag = df_["agent"].to_numpy()
        for arr in (y, x1, x2):
            for a in np.unique(ag):
                m = ag == a
                arr[m] = arr[m] - arr[m].mean()
        X = np.column_stack([x1, x2])
        b, *_ = np.linalg.lstsq(X, y, rcond=None)
        return b
    b = fit(df.clone())
    rng = np.random.default_rng(seed)
    jd = sorted(set(df["join_day"].to_list()))
    bs = []
    for _ in range(B):
        pick = rng.choice(jd, len(jd))
        parts = []
        for i, j in enumerate(pick):
            parts.append(df.filter(pl.col("join_day") == j).with_columns((pl.col("agent").cast(pl.Int64) * 1000 + i)
                                                                         .alias("agent")))
        bs.append(fit(pl.concat(parts)))
    bs = np.array(bs)
    return {"b_dose": float(b[0]), "b_dose_ci": [float(np.quantile(bs[:, 0], .025)), float(np.quantile(bs[:, 0], .975))],
            "b_logtau": float(b[1]), "b_logtau_ci": [float(np.quantile(bs[:, 1], .025)), float(np.quantile(bs[:, 1], .975))],
            "n_obs": df.height, "n_joins": df["agent"].n_unique()}


def card_stats(res):
    J = res["joins"]
    out = {"G": L.summarize(J, "G"), "G_gapE": L.summarize(J, "G", "gap_E"), "G_gapL": L.summarize(J, "G", "gap_L"),
           "G_mm": L.summarize(J, "G_mm"), "K": L.summarize(J, "K"), "K_E": L.summarize(J, "K", "gap_E"),
           "K_style": L.summarize(J, "K_style"), "K_style_E": L.summarize(J, "K_style", "gap_E"),
           "S": L.summarize(J, "S"), "S_gapE": L.summarize(J, "S", "gap_E")}
    g1 = [r["G1"] for r in J.values() if "G1" in r and r.get("G")]
    out["G1"] = dict(zip(("mean", "lo", "hi", "n"), L.boot_mean(g1)))
    x = [np.log1p(r["dose_vet_1_7"]) for r in J.values() if r.get("G")]
    y = [r["G"]["delta"] for r in J.values() if r.get("G")]
    if len(x) > 4:
        rho, p = L.spearman_perm(x, y)
        out["dose_rho"] = {"rho": rho, "p_one_sided": p, "n": len(x)}
    return out


def main():
    OUTD.mkdir(parents=True, exist_ok=True)
    days = L.calendar_days(); newc = L.newcomers()
    doses = pl.read_parquet(L.DATA / "doses.parquet")
    out = {"run_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), "crit_G": L.E_WIN and CRIT,
           "windows": {"E": L.E_WIN, "L": L.L_WIN}, "variants": {}}
    st, X, F = L.load("bge", "vec")
    res = L.run_all(st, X, F, newc, days, doses)
    out["joins"] = {str(a): L_json for a, L_json in ((a, jsonable(r)) for a, r in res["joins"].items())}
    out["card"] = card_stats(res)
    out["dose_regression"] = dose_regression(res, days, doses)
    g = out["card"]["G"]
    out["card"]["P1_calibrated_pass"] = bool(g["mean"] is not None and g["mean"] > CRIT)
    print("bge G", g, flush=True)
    # gte
    st2, X2, _ = L.load("gte", "vec")
    res2 = L.run_all(st2, X2, None, newc, days, doses, with_family=True, with_mm=True)
    for a, r in res2["joins"].items():
        if str(a) in out["joins"]:
            out["joins"][str(a)]["G_gte"] = jsonable(r)["G"]
            out["joins"][str(a)]["G_mm_gte"] = jsonable(r).get("G_mm")
            out["joins"][str(a)]["K_gte"] = jsonable(r).get("K")
    out["variants"]["gte"] = card_stats(res2)
    print("gte G", out["variants"]["gte"]["G"], flush=True)
    # variants (bge): no kickoff projection; not style-residualized; onboarding day in E; longer L
    for name, variant in (("no_projection", "vecraw"), ("white32", "white")):
        st3, X3, _ = L.load("bge", variant)
        r3 = L.run_all(st3, X3, None, newc, days, doses, with_family=True, with_mm=False)
        out["variants"][name] = card_stats(r3)
        print(name, out["variants"][name]["G"], flush=True)
    for name, ew, lw in (("E_tau1_4", (1, 4), L.L_WIN), ("L_tau8_20", L.E_WIN, (8, 20))):
        e0, l0 = L.E_WIN, L.L_WIN
        L.E_WIN, L.L_WIN = ew, lw
        r4 = L.run_all(st, X, F, newc, days, doses, with_family=False, with_mm=False)
        L.E_WIN, L.L_WIN = e0, l0
        out["variants"][name] = card_stats(r4)
        print(name, out["variants"][name]["G"], flush=True)
    # post hoc PH1 (2026-10-04, after seeing K): family baselines without same-day joins (NE27, NE32 batches
    # share their tau-1 day field, which inflates K_E for the GPT-5.6 triplet and deflates it for NE27)
    L.EXCLUDE_SAME_DAY = True
    for model in ("bge", "gte"):
        st5, X5, F5 = L.load(model, "vec")
        r5 = L.run_all(st5, X5, F5 if model == "bge" else None, newc, days, doses, with_family=True, with_mm=False)
        cs = card_stats(r5)
        out["variants"][f"PH1_K_no_same_day_{model}"] = {k: cs[k] for k in ("K", "K_E", "K_style", "K_style_E")
                                                          if k in cs}
        out["variants"][f"PH1_K_no_same_day_{model}"]["per_join"] = {
            str(a): {"K_E": r["K"]["gap_E"], "dK": r["K"]["delta"]} for a, r in r5["joins"].items() if r.get("K")}
        print("PH1", model, out["variants"][f"PH1_K_no_same_day_{model}"]["K"],
              out["variants"][f"PH1_K_no_same_day_{model}"]["K_E"], flush=True)
    L.EXCLUDE_SAME_DAY = False
    (OUTD / "replication.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out["card"], indent=1, default=float)[:3000])
    print("dose regression", out["dose_regression"])


if __name__ == "__main__":
    main()
