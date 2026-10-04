"""H26 round-1 summary: joint day-bootstrap of the content-activity and content-talk gaps per unit, per-unit verdicts
by the card's rules, pooled medians (hierarchical bootstrap: units, then days), and a robustness estimator.

Reads explore.py outputs (G<NN>/<unit>.json, for N2 p-values) and rebuilds the L2 contributions (no nulls) so that
content, activity and talk are resampled with the SAME day weights.

Robustness variant (post hoc, descriptive): rho_pooled = mean pair covariance / mean agent signal variance, which does
not explode when split-half signal variances of rare events (talk) are near zero.

Usage: uv run python hypotheses/H26-content-near-critical/analysis/summarize.py
Writes data/processed/H26-content-near-critical/summary.json and summary_units.parquet.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h26lib as L  # noqa: E402
import explore as EX  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = HERE.parents[2]
D = ROOT / "data/processed/H26-content-near-critical"
B = 400
REG3_TWO = ["36b", "37", "38a", "38b", "38c", "39", "41", "42", "44", "51c"]
EXTRA_TWO = ["35"]
SINGLE = ["40", "51a", "51b", "51d", "51e"]


def g_of(nm1, rho):
    if not np.isfinite(rho):
        return np.nan
    R = 1 + nm1 * rho
    return 1 - 1 / R if R > 0 else -np.inf


def pooled_rho(C, w):
    S = np.tensordot(w, C["s_sum"], 1); n = np.tensordot(w, C["s_cnt"], 1)
    Sm = S.sum() / max(n.sum(), 1e-12)
    out = {}
    for typ in ("w", "c"):
        num = np.tensordot(w, C["C" + typ], 1).sum(); cnt = np.tensordot(w, C["N" + typ], 1).sum()
        out[typ] = num / cnt / Sm if cnt > 0 and Sm > 0 else np.nan
    return out


def stats(C, w, two):
    g = L.gains(C, w)
    pr = pooled_rho(C, w)
    rp_ex = (pr["w"] - pr["c"]) / (1 - pr["c"]) if np.isfinite(pr["c"]) and pr["c"] < 1 else np.nan
    nm1 = g["Nr"] - 1
    return {"g": g["g_ex"] if two else g["g_room"], "rho": g["rho_ex"] if two else g["rho_w"],
            "g_pooled": g_of(nm1, rp_ex) if two else g_of(nm1, pr["w"]),
            "rho_w": g["rho_w"], "rho_c": g["rho_c"], "Nr": g["Nr"], "g_all_L0": None}  # g clipped to [-1, 1] in all summaries (VR >= 0.5)


def unit_summary(Dt, u, rng):
    panels, info = EX.build_panels(Dt, u, dedup=True)
    ex = json.loads((D / f"G{Dt.units[u]['goal_no']:02d}/{u}.json").read_text())
    two = u in REG3_TWO + EXTRA_TWO
    out = {"unit": u, "goal_no": Dt.units[u]["goal_no"], "two_room": two, "n_days": len(Dt.units[u]["days"])}
    for res in ("day", "w30"):
        Cs, days = {}, None
        for ch in ("c", "a", "k"):
            C, _, _ = L.run_level(panels[(ch, res)], 2)
            Cs[ch] = C
        all_days = sorted(set().union(*[set(C["days"].tolist()) for C in Cs.values()]))
        idx = {ch: np.searchsorted(all_days, C["days"]) for ch, C in Cs.items()}
        pt = {ch: stats(C, np.ones(len(C["days"])), two) for ch, C in Cs.items()}
        bs = {ch: {k: [] for k in ("g", "rho", "g_pooled")} for ch in Cs}
        for _ in range(B):
            wfull = np.bincount(rng.integers(0, len(all_days), len(all_days)), minlength=len(all_days)).astype(float)
            for ch, C in Cs.items():
                s = stats(C, wfull[idx[ch]], two)
                for k in bs[ch]:
                    bs[ch][k].append(s[k])
        for ch in Cs:
            for k in ("g", "rho", "g_pooled", "rho_w", "rho_c", "Nr"):
                out[f"{ch}_{res}_{k}"] = float(pt[ch][k]) if pt[ch][k] is not None and np.isfinite(pt[ch][k]) else (
                    -np.inf if pt[ch][k] == -np.inf else None)
            out[f"{ch}_{res}_g_ci"] = L.ci(np.clip(bs[ch]["g"], -1, 1))
        for o in ("a", "k"):
            dg = np.clip(np.array(bs["c"]["g"]), -1, 1) - np.clip(np.array(bs[o]["g"]), -1, 1)
            dr = np.array(bs["c"]["rho"]) - np.array(bs[o]["rho"])
            gc, go = pt["c"]["g"], pt[o]["g"]
            out[f"dg_c{o}_{res}"] = float(np.clip(gc, -1, 1) - np.clip(go, -1, 1)) if np.isfinite(gc) or gc == -np.inf else None
            out[f"dg_c{o}_{res}_ci"] = L.ci(dg)
            out[f"drho_c{o}_{res}"] = float(pt["c"]["rho"] - pt[o]["rho"]) if np.isfinite(pt["c"]["rho"]) and np.isfinite(pt[o]["rho"]) else None
            out[f"drho_c{o}_{res}_ci"] = L.ci(dr)
            out[f"_boot_dg_c{o}_{res}"] = dg.tolist()
        out[f"_boot_gc_{res}"] = np.clip(bs["c"]["g"], -1, 1).tolist()
    out["p_N2_content_day"] = (ex["c_day_dedup"].get("L2") or {}).get("p_N2_rho_ex")
    out["p_N2_content_w30"] = (ex["c_w30_dedup"].get("L2") or {}).get("p_N2_rho_ex")
    out["p_N2_activity_w30"] = (ex["a_w30"].get("L2") or {}).get("p_N2_rho_ex")
    out["h01_p9_raw"] = (ex["h01_p9"]["raw"] or {}).get("bJ_over_n")
    out["c_day_L0_g_all"] = (ex["c_day_dedup"].get("L0") or {}).get("g_all")
    out["c_day_L0_g_room"] = (ex["c_day_dedup"].get("L0") or {}).get("g_room")
    out["c_w30_L4_g_ex"] = (ex["c_w30_dedup"].get("L4") or {}).get("g_ex")
    out["drive_share_day_excess"] = ex["drive_share_day"].get("excess_share_of_all_room_variance")
    out["drive_share_w30_excess"] = ex["drive_share_w30"].get("excess_share_of_all_room_variance")
    out["n_eff_day"] = (ex["c_day_dedup"].get("L2") or {}).get("n_eff")
    out["iso_over_N1_sd"] = ((ex["c_day_dedup"].get("L2") or {}).get("iso_rho_w_sd") or np.nan) / \
        ((ex["c_day_dedup"].get("L2") or {}).get("N1_rho_w_sd") or np.nan)
    # card verdict (two-room units, day level, L3)
    if two:
        gc = out["c_day_g"]; dg = out["dg_ca_day"]; lo = out["dg_ca_day_ci"][0]; p = out["p_N2_content_day"]
        if gc is not None and gc >= 0.5 and dg is not None and dg > 0.15 and lo is not None and lo > 0 and p is not None and p < 0.05:
            v = "supported"
        elif (gc is None or gc < 0.5) and (dg is None or dg <= 0.15):
            v = "failed"
        else:
            v = "mixed"
        out["verdict"] = v
    else:
        out["verdict"] = "descriptive"
    return out


def pooled(rows, key, rng, boot_key=None):
    vals = np.array([r[key] for r in rows if r[key] is not None], float)
    vals = np.clip(vals, -1, 1)
    vals = vals[np.isfinite(vals)]
    med = float(np.median(vals)) if len(vals) else None
    if boot_key is None:
        return {"median": med, "n": int(len(vals))}
    meds = []
    for _ in range(2000):
        pick = rng.integers(0, len(rows), len(rows))
        draw = [rows[i][boot_key][rng.integers(len(rows[i][boot_key]))] for i in pick]
        draw = [x for x in draw if x is not None and np.isfinite(x)]
        meds.append(np.median(draw) if draw else np.nan)
    return {"median": med, "n": int(len(vals)), "ci": L.ci(meds)}


def main():
    Dt = EX.Data()
    rng = np.random.default_rng(20261004)
    rows = []
    for u in REG3_TWO + EXTRA_TWO + SINGLE:
        rows.append(unit_summary(Dt, u, rng))
        print(u, rows[-1]["verdict"], rows[-1]["c_day_g"], rows[-1]["dg_ca_day"], flush=True)
    two = [r for r in rows if r["unit"] in REG3_TWO]
    S = {"units_primary": REG3_TWO, "extra": EXTRA_TWO, "single": SINGLE}
    for res in ("day", "w30"):
        S[f"median_gc_{res}"] = pooled(two, f"c_{res}_g", rng, f"_boot_gc_{res}")
        S[f"median_ga_{res}"] = pooled(two, f"a_{res}_g", rng)
        S[f"median_gk_{res}"] = pooled(two, f"k_{res}_g", rng)
        for o in ("a", "k"):
            S[f"median_dg_c{o}_{res}"] = pooled(two, f"dg_c{o}_{res}", rng, f"_boot_dg_c{o}_{res}")
            S[f"median_drho_c{o}_{res}"] = pooled(two, f"drho_c{o}_{res}", rng)
            S[f"n_dg_c{o}_{res}_gt015"] = int(sum(1 for r in two if r[f"dg_c{o}_{res}"] is not None and r[f"dg_c{o}_{res}"] > 0.15))
            S[f"n_dg_c{o}_{res}_ci_gt0"] = int(sum(1 for r in two if r[f"dg_c{o}_{res}_ci"][0] is not None and r[f"dg_c{o}_{res}_ci"][0] > 0))
        S[f"n_gc_ge05_{res}"] = int(sum(1 for r in two if r[f"c_{res}_g"] is not None and r[f"c_{res}_g"] >= 0.5))
        S[f"median_gc_pooled_{res}"] = pooled(two, f"c_{res}_g_pooled", rng)
        S[f"median_ga_pooled_{res}"] = pooled(two, f"a_{res}_g_pooled", rng)
        S[f"median_gk_pooled_{res}"] = pooled(two, f"k_{res}_g_pooled", rng)
        S[f"median_rho_c_activity_{res}"] = pooled(two, f"a_{res}_rho_c", rng)
        S[f"median_rho_c_content_{res}"] = pooled(two, f"c_{res}_rho_c", rng)
        S[f"median_rho_w_activity_{res}"] = pooled(two, f"a_{res}_rho_w", rng)
        S[f"median_rho_w_content_{res}"] = pooled(two, f"c_{res}_rho_w", rng)
    S["n_N2_content_day_p05"] = int(sum(1 for r in two if r["p_N2_content_day"] is not None and r["p_N2_content_day"] < 0.05))
    S["n_N2_content_w30_p05"] = int(sum(1 for r in two if r["p_N2_content_w30"] is not None and r["p_N2_content_w30"] < 0.05))
    S["median_h01_p9"] = pooled(two, "h01_p9_raw", rng)
    S["median_c_day_L0_g_all"] = pooled(two, "c_day_L0_g_all", rng)
    S["median_c_w30_L4"] = pooled(two, "c_w30_L4_g_ex", rng)
    S["verdicts"] = {r["unit"]: r["verdict"] for r in rows}
    S["drive_share_day_excess_range"] = [min(r["drive_share_day_excess"] for r in two if r["drive_share_day_excess"] is not None),
                                         max(r["drive_share_day_excess"] for r in two if r["drive_share_day_excess"] is not None)]
    med_gc = S["median_gc_day"]["median"]; med_dg = S["median_dg_ca_day"]
    nsup = sum(1 for r in two if r["verdict"] == "supported")
    if nsup >= len(two) / 2 and med_gc >= 0.5:
        outcome = "H26 survives"
    elif med_dg["median"] > 0.15 and med_dg["ci"][0] > 0 and med_gc < 0.5:
        outcome = "gap real but content not near-critical"
    elif (med_dg["median"] <= 0.15 or med_dg["ci"][0] <= 0) and \
         (S["median_dg_ca_w30"]["median"] <= 0.15 or S["median_dg_ca_w30"]["ci"][0] <= 0):
        outcome = "failed (R2: no robust channel gap at either resolution)"
    else:
        outcome = "unresolved by the card's rules"
    S["outcome"] = outcome
    S["n_supported"] = nsup
    (D / "summary.json").write_text(json.dumps(S, indent=1, default=float))
    flat = [{k: (v if not isinstance(v, list) else json.dumps(v)) for k, v in r.items() if not k.startswith("_")} for r in rows]
    pl.DataFrame(flat, infer_schema_length=None).write_parquet(D / "summary_units.parquet", compression="zstd")
    (D / "summary_units.json").write_text(json.dumps([{k: v for k, v in r.items() if not k.startswith("_")} for r in rows],
                                                     indent=1, default=float))
    print(json.dumps({k: v for k, v in S.items() if k != "verdicts"}, indent=1, default=float))
    print(S["verdicts"])


if __name__ == "__main__":
    main()
