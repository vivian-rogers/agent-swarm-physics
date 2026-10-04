"""H25 round 1b, period-native tests (DQ9 cross-index), on the round-1b daily dials (activity_bins_fixed).
Predictions were written in the folders before this script was run:
  NE43  goalperiod-subhypotheses/NE43/README.md  drive withdrawal inside #51 (bookends stop 08-05, nudges stop 08-21)
  G51   goalperiod-subhypotheses/G51/README.md   N as a control parameter inside #51 (constant rho-bar vs constant g)
  G40   goalperiod-subhypotheses/G40/README.md   NE42 room merge / split at a fixed roster (#39 -> #40 -> #41)
Input: data/processed/H25-criticality-dial/r1b/dial_daily.parquet (explore.py --data-version fixed).
Output: data/processed/H25-criticality-dial/r1b/native/{native.json, ne43_steps.parquet, g51_days.parquet}.
Usage: uv run python hypotheses/H25-criticality-dial/analysis/r1b_native.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ["H25_DATA_VERSION"] = "fixed"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import h25common as C  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

import dial as D  # noqa: E402

OUT = C.RESD / "native"
PRIM = {"activity": "auto", "talk": "auto", "content": "F2"}


def ok_days(daily, ch, v):
    return (daily.filter((pl.col("channel") == ch) & (pl.col("variant") == v) & (pl.col("flag") == "ok")
                         & pl.col("se").is_finite() & (pl.col("se") > 0))
            .with_columns(((pl.col("VR") - 1) / (pl.col("N") - 1)).alias("rho")).sort("pt_date"))


def re_mean(d):
    if d.height == 0:
        return None
    a = D.aggregate_days(d["g"].to_numpy(), d["se"].to_numpy())
    return {"re": float(a["re"]), "se_re": float(a["se_re"]), "k": int(a["k"]), "rho_med": float(d["rho"].median()),
            "N_med": float(d["N"].median())}


def step(left, right):
    a, b = re_mean(left), re_mean(right)
    if a is None or b is None:
        return None
    dlt = b["re"] - a["re"]; se = float(np.hypot(a["se_re"], b["se_re"]))
    return {"left": a, "right": b, "delta": float(dlt), "se": se, "z": float(dlt / se) if se > 0 else np.nan,
            "lo90": float(dlt - 1.645 * se), "hi90": float(dlt + 1.645 * se), "d_rho_med": b["rho_med"] - a["rho_med"]}


def ne43(daily) -> tuple[dict, pl.DataFrame]:
    res, rows = {}, []
    cuts = ["2026-08-05", "2026-08-21"]
    for ch, v in list(PRIM.items()) + [("activity", "trim"), ("talk", "trim")]:
        d = ok_days(daily, ch, v).filter(pl.col("goal_no") == 51)
        days = d["pt_date"].to_list()
        A = d.filter(pl.col("pt_date") < cuts[0]); B = d.filter((pl.col("pt_date") >= cuts[0]) & (pl.col("pt_date") < cuts[1]))
        Cc = d.filter(pl.col("pt_date") >= cuts[1])
        sAB, sBC = step(A, B), step(B, Cc)
        # placebo: every other within-#51 boundary with >= 2 days each side; segments run to the neighbouring real
        # boundary (or the period edge), so no placebo segment spans a real step
        plac = []
        edges = [days[0]] + cuts + ["9999"]
        for k in range(1, len(days)):
            b = days[k]
            if b in cuts:
                continue
            lo = max(e for e in edges if e <= days[k - 1]); hi = min(e for e in edges if e > b)
            left = d.filter((pl.col("pt_date") >= lo) & (pl.col("pt_date") < b))
            right = d.filter((pl.col("pt_date") >= b) & (pl.col("pt_date") < hi))
            if left.height >= 2 and right.height >= 2:
                s = step(left, right)
                if s and np.isfinite(s["z"]):
                    plac.append(abs(s["z"]))
        q95 = float(np.quantile(plac, 0.95)) if plac else np.nan
        key = f"{ch}_{v}"
        res[key] = {"A_to_B": sAB, "B_to_C": sBC, "placebo_n": len(plac), "placebo_absz_q95": q95,
                    "A_to_B_within_placebo": bool(sAB and abs(sAB["z"]) < q95), "B_to_C_within_placebo": bool(sBC and abs(sBC["z"]) < q95)}
        for nm, s in (("A_to_B", sAB), ("B_to_C", sBC)):
            if s:
                rows.append({"series": key, "step": nm, "delta": s["delta"], "se": s["se"], "z": s["z"], "lo90": s["lo90"],
                             "hi90": s["hi90"], "placebo_q95": q95, "left_re": s["left"]["re"], "right_re": s["right"]["re"],
                             "d_rho_med": s["d_rho_med"]})
    ok3 = all(res[f"{c}_auto"]["A_to_B_within_placebo"] for c in ("activity", "talk"))
    ok4 = all(res[f"{c}_auto"]["B_to_C_within_placebo"] for c in ("activity", "talk"))
    a = res["activity_auto"]
    rival = any(s and s["z"] < 0 and abs(s["z"]) >= a["placebo_absz_q95"] for s in (a["A_to_B"], a["B_to_C"]))
    res["N3a"], res["N3b"], res["rival_activity_drop"] = bool(ok3), bool(ok4), bool(rival)
    res["verdict"] = "supported" if (ok3 and ok4) else ("failed" if rival else "mixed")
    return res, pl.DataFrame(rows)


def loo_models(N, g):
    x = N - 1.0
    vr1 = 1 / (1 - g) - 1
    e_rho, e_g = [], []
    for i in range(len(g)):
        m = np.arange(len(g)) != i
        c = np.sum(x[m] * vr1[m]) / np.sum(x[m] ** 2)
        e_rho.append((g[i] - c * x[i] / (1 + c * x[i])) ** 2)
        e_g.append((g[i] - g[m].mean()) ** 2)
    return float(np.sum(e_rho)), float(np.sum(e_g))


def g51(daily) -> tuple[dict, pl.DataFrame]:
    res, frames = {}, []
    for ch in ("activity", "talk", "content"):
        d = ok_days(daily, ch, PRIM[ch]).filter((pl.col("goal_no") == 51) & (pl.col("g") < 0.999))
        N, g = d["N"].to_numpy().astype(float), d["g"].to_numpy()
        sse_rho, sse_g = loo_models(N, g)
        res[ch] = {"n_days": d.height, "N_range": [float(N.min()), float(N.max())],
                   "spearman_g_N": float(stats.spearmanr(N, g)[0]), "spearman_rho_N": float(stats.spearmanr(N, d["rho"].to_numpy())[0]),
                   "median_rho": float(d["rho"].median()), "loo_sse_const_rho": sse_rho, "loo_sse_const_g": sse_g,
                   "const_rho_wins": bool(sse_rho < sse_g)}
        frames.append(d.select("pt_date", pl.lit(ch).alias("channel"), "N", "g", "se", "rho"))
    n1a = res["activity"]["const_rho_wins"] and res["activity"]["spearman_g_N"] > 0
    n1b = (not res["talk"]["const_rho_wins"]) and abs(res["talk"]["spearman_g_N"]) < 0.3
    res["N1a"], res["N1b"] = bool(n1a), bool(n1b)
    res["verdict"] = "supported" if (n1a and n1b) else ("failed" if not (n1a or n1b) else "mixed")
    return res, pl.concat(frames)


def ne42(daily) -> dict:
    res = {}
    for ch in ("activity", "talk", "content"):
        d = ok_days(daily, ch, PRIM[ch])
        m = {g: re_mean(d.filter(pl.col("goal_no") == g)) for g in (39, 40, 41)}
        if any(v is None for v in m.values()):
            res[ch] = None
            continue
        dl = m[40]["re"] - (m[39]["re"] + m[41]["re"]) / 2
        se = float(np.sqrt(m[40]["se_re"] ** 2 + (m[39]["se_re"] ** 2 + m[41]["se_re"] ** 2) / 4))
        vr1 = {g: m[g]["re"] / (1 - m[g]["re"]) for g in m}
        res[ch] = {"periods": m, "delta": float(dl), "se": se, "lo90": float(dl - 1.645 * se), "hi90": float(dl + 1.645 * se),
                   "vr1_ratio_40_over_mean_39_41": float(vr1[40] / ((vr1[39] + vr1[41]) / 2))}
    t, c, a = res["talk"], res["content"], res["activity"]
    res["N2a"] = bool(abs(t["delta"]) < 0.05 or (t["lo90"] <= 0 <= t["hi90"]))
    res["N2b"] = bool(c["vr1_ratio_40_over_mean_39_41"] >= 1.5)
    res["N2c"] = bool(abs(a["delta"]) < 0.05 or (a["lo90"] <= 0 <= a["hi90"]))
    k = sum([res["N2a"], res["N2b"], res["N2c"]])
    res["verdict"] = "supported" if k == 3 else ("failed" if k == 0 else "mixed")
    return res


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    daily = pl.read_parquet(C.RESD / "dial_daily.parquet")
    C.assert_no_holdout(daily["pt_date"], daily["goal_no"])
    r43, s43 = ne43(daily)
    s43.write_parquet(OUT / "ne43_steps.parquet")
    r51, d51 = g51(daily)
    d51.write_parquet(OUT / "g51_days.parquet")
    r42 = ne42(daily)
    R = {"NE43": r43, "G51_size_law": r51, "NE42": r42}
    (OUT / "native.json").write_text(json.dumps(R, indent=1, default=float))
    C.write_provenance("r1b_native", "hypotheses/H25-criticality-dial/analysis/r1b_native.py", ["(H25 r1b dial_daily)"],
                       {"tests": ["NE43 steps vs within-#51 placebo", "G51 constant rho vs constant g (LOO)", "NE42 A-B-A"]},
                       out=C.RESD)
    print(json.dumps(R, indent=1, default=float))


if __name__ == "__main__":
    main()
