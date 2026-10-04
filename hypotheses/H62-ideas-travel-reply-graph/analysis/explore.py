"""H62 replication layer: channel-resolved contagion on every eligible period (non-holdout only).

  uv run python hypotheses/H62-ideas-travel-reply-graph/analysis/explore.py [--goals 38,51]
Output: data/processed/H62-ideas-travel-reply-graph/results/{periods.json, period_table.parquet, summary.json}
Verdict rule (card): supported = Lambda lower 95% CI > 1 and T_rep/T_room lower 95% CI > 1; failed = Lambda <= 1 and
T ratio <= 1 (points); mixed otherwise; n/a = < 20 adoptions at RecRep or at RecRoom calls.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from multiprocessing import Pool  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h62lib as L  # noqa: E402

ROOT = HERE.parents[2]
OUT = ROOT / "data/processed/H62-ideas-travel-reply-graph"
RES = OUT / "results"
GOALS = [5, 6, 7, 8, 10, 11, 12, 13, 16, 17, 18, 19, 20, 21, 23, 24, 25, 26, 27, 30, 31, 33, 35, 36, 37, 38, 39, 40,
         41, 42, 44, 51]


def verdict(r: dict) -> str:
    """Card rule with amendment A2 (the C_rep clause)."""
    if not r.get("eligible"):
        return "n/a"
    lam_ok = r.get("Lam_lo", 0) > 1
    t_ok = r.get("T_ratio_lo", 0) > 1
    c_ok = bool(r.get("B_rep_power")) and r.get("C_rep_wlo", 0) > 1
    if lam_ok and t_ok and c_ok:
        return "supported"
    if r.get("Lam", 0) <= 1 and r.get("T_ratio", 0) <= 1:
        return "failed"
    return "mixed"


def run(g: int) -> dict:
    d = OUT / f"G{g:02d}"
    meta = json.loads((d / "meta.json").read_text())
    cells = pl.read_parquet(d / "cells.parquet")
    ev = pl.read_parquet(d / "events.parquet")
    ad = pl.read_parquet(d / "adopters.parquet")
    out = dict(goal=g, regime=meta["regime"], N_room=meta["N_room"], n_rooms=meta["n_rooms"], n_days=meta["n_days"],
               n_ideas=meta["n_ideas"], n_parent_edges=meta["n_parent_edges"], first_day=meta["first_day"],
               last_day=meta["last_day"])
    A = L.hr_fit(cells, L.MODEL_A, B=200, seed=g, contrasts={"Lam": ("rec_rep", "rec_room")})
    G = L.hr_fit(cells, L.MODEL_G, B=200, seed=g + 1, contrasts={"LamG": ("recg_rep", "recg_room")})
    Bm = L.hr_fit(cells, L.MODEL_B, B=200, seed=g + 2, contrasts={"C_rep": ("s_rep5", "u_rep5x"),
                                                                   "C_room": ("s_room5", "u_room5x"),
                                                                   "S5": ("s_rep5", "s_room5")})
    out.update({f"A_{k}": v for k, v in A.items() if not k.startswith("Lam")})
    out.update({k: v for k, v in A.items() if k.startswith("Lam")})
    out.update({f"G_{k}": v for k, v in G.items() if not k.startswith("LamG")})
    out.update({k: v for k, v in G.items() if k.startswith("LamG")})
    out.update({f"B_{k}": v for k, v in Bm.items() if not k.startswith(("C_", "S5"))})
    out.update({k: v for k, v in Bm.items() if k.startswith(("C_", "S5"))})
    out["eligible"] = bool(A.get("adopt_rec_rep", 0) >= 20 and A.get("adopt_rec_room", 0) >= 20)
    out["B_rep_power"] = bool(Bm.get("adopt_s_rep5", 0) >= 10 and Bm.get("adopt_u_rep5x", 0) >= 10)
    out["B_room_power"] = bool(Bm.get("adopt_s_room5", 0) >= 10 and Bm.get("adopt_u_room5x", 0) >= 10)
    T = L.transmissibility(ev, "chan", B=1000, seed=g)
    TG = L.transmissibility(ev, "chan_g", B=1000, seed=g + 5)
    out.update(T)
    out.update({f"G_{k}": v for k, v in TG.items()})
    br = L.branching(ad)
    out.update(br)
    if T:
        out["exp_share_rep"] = T["n_rep"] / (T["n_rep"] + T["n_room"])
    hr_rep, hr_room = A.get("hr_rec_rep"), A.get("hr_rec_room")
    if hr_rep and hr_room and br:
        rc_rep = br["R_rep"] * max(0.0, 1 - 1 / hr_rep)
        rc_room = br["R_room"] * max(0.0, 1 - 1 / hr_room)
        out["Rc_rep"], out["Rc_room"] = rc_rep, rc_room
        out["Rc_share_rep"] = rc_rep / (rc_rep + rc_room) if rc_rep + rc_room > 0 else np.nan
        out["P4_ratio"] = out["Rc_share_rep"] / out["exp_share_rep"] if out.get("exp_share_rep") else np.nan
    out["verdict"] = verdict(out)
    return out


def summarize(rows: list[dict]) -> dict:
    el = [r for r in rows if r.get("eligible")]
    sm = dict(n_periods=len(rows), n_eligible=len(el),
              verdicts={v: sum(r["verdict"] == v for r in rows) for v in ("supported", "mixed", "failed", "n/a")})
    sm["P1_Lam_ci_gt1"] = sum(r.get("Lam_lo", 0) > 1 for r in el)
    sm["P1_Lam_ci_lt1"] = sum(r.get("Lam_hi", 9) < 1 for r in el)
    sm["P1_Lam_median"] = float(np.median([r["Lam"] for r in el]))
    sm["P1_pool_logLam"] = L.dl_pool([r["Lam_log"] for r in el], [r.get("Lam_bse", r["Lam_se"]) for r in el])
    sm["HR_rep_median"] = float(np.median([r["A_hr_rec_rep"] for r in el]))
    sm["HR_room_median"] = float(np.median([r["A_hr_rec_room"] for r in el]))
    te = [r for r in el if np.isfinite(r.get("T_ratio", np.nan))]
    sm["P2_T_ci_gt1"] = sum(r.get("T_ratio_lo", 0) > 1 for r in te)
    sm["P2_T_ci_lt1"] = sum(r.get("T_ratio_hi", 9) < 1 for r in te)
    sm["P2_T_median"] = float(np.median([r["T_ratio"] for r in te]))
    sm["P2_pool_logT"] = L.dl_pool([np.log(r["T_ratio"]) for r in te], [r.get("T_ratio_logse", np.nan) for r in te])
    sm["T_rep_median"] = float(np.median([r["T_rep"] for r in te]))
    sm["T_room_median"] = float(np.median([r["T_room"] for r in te]))
    br_ = [r for r in el if r.get("B_room_power")]
    bp_ = [r for r in el if r.get("B_rep_power")]
    sm["P3_n_room_power"] = len(br_)
    sm["P3_C_room_field"] = sum((r["C_room_lo"] <= 1) or (r["C_room"] < 1.5) for r in br_) if br_ else 0
    sm["P3_C_room_ci_gt1"] = sum(r.get("C_room_lo", 0) > 1 for r in br_)
    sm["P3_C_room_median"] = float(np.median([r["C_room"] for r in br_])) if br_ else np.nan
    sm["P3_n_rep_power"] = len(bp_)
    sm["P3_C_rep_ci_gt1"] = sum(r.get("C_rep_lo", 0) > 1 for r in bp_)
    sm["P3_C_rep_median"] = float(np.median([r["C_rep"] for r in bp_])) if bp_ else np.nan
    sm["P3_pool_logC_room"] = L.dl_pool([r["C_room_log"] for r in el if "C_room_log" in r],
                                        [r.get("C_room_bse", r.get("C_room_se")) for r in el if "C_room_log" in r])
    sm["P3_pool_logC_rep"] = L.dl_pool([r["C_rep_log"] for r in el if "C_rep_log" in r],
                                       [r.get("C_rep_bse", r.get("C_rep_se")) for r in el if "C_rep_log" in r])
    p4 = [r for r in el if np.isfinite(r.get("P4_ratio", np.nan))]
    sm["P4_ratio_ge2"] = sum(r["P4_ratio"] >= 2 for r in p4)
    sm["P4_ratio_median"] = float(np.median([r["P4_ratio"] for r in p4])) if p4 else np.nan
    sm["exp_share_rep_median"] = float(np.median([r["exp_share_rep"] for r in te]))
    sm["Rc_share_rep_median"] = float(np.median([r["Rc_share_rep"] for r in p4])) if p4 else np.nan
    sm["share_rep_parent_median"] = float(np.median([r["share_rep_parent"] for r in el]))
    N = [r["N_room"] for r in te]
    for k in ("T_room", "T_rep", "T_ratio"):
        s = stats.spearmanr(N, [r[k] for r in te])
        sm[f"P5_rho_{k}_N"] = (float(s.statistic), float(s.pvalue))
    sm["P6_LamG_ci_gt1"] = sum(r.get("LamG_lo", 0) > 1 for r in el)
    sm["P6_LamG_median"] = float(np.median([r["LamG"] for r in el]))
    sm["G_T_ratio_median"] = float(np.median([r["G_T_ratio"] for r in el if "G_T_ratio" in r]))
    by = {}
    for reg in ("I", "II", "III"):
        rr = [r for r in el if r["regime"] == reg]
        if rr:
            by[reg] = dict(n=len(rr), Lam_ci_gt1=sum(r["Lam_lo"] > 1 for r in rr),
                           Lam_median=float(np.median([r["Lam"] for r in rr])),
                           T_ratio_median=float(np.median([r["T_ratio"] for r in rr if np.isfinite(r.get("T_ratio", np.nan))])),
                           HR_rep_median=float(np.median([r["A_hr_rec_rep"] for r in rr])),
                           HR_room_median=float(np.median([r["A_hr_rec_room"] for r in rr])))
    sm["by_regime"] = by
    return sm


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--goals", default="")
    a = ap.parse_args()
    goals = [int(x) for x in a.goals.split(",")] if a.goals else GOALS
    RES.mkdir(parents=True, exist_ok=True)
    goals = sorted(goals, key=lambda g: -1 if g == 51 else g)
    with Pool(2) as pool:
        rows = pool.map(run, goals, chunksize=1)
    rows = sorted(rows, key=lambda r: r["goal"])
    (RES / "periods.json").write_text(json.dumps(rows, indent=1, default=float))
    pl.DataFrame([{k: v for k, v in r.items() if not isinstance(v, (dict, list))} for r in rows],
                 infer_schema_length=None).write_parquet(RES / "period_table.parquet")
    if not a.goals:
        sm = summarize(rows)
        (RES / "summary.json").write_text(json.dumps(sm, indent=1, default=float))
        print(json.dumps(sm, indent=1, default=float))
    for r in rows:
        print(f"G{r['goal']:02d} {r['regime']:>3} {r['verdict']:>9} Lam {r.get('Lam', np.nan):6.2f} "
              f"[{r.get('Lam_lo', np.nan):5.2f}, {r.get('Lam_hi', np.nan):5.2f}] HRrep {r.get('A_hr_rec_rep', np.nan):6.1f} "
              f"HRroom {r.get('A_hr_rec_room', np.nan):6.1f} T {r.get('T_ratio', np.nan):5.2f} "
              f"[{r.get('T_ratio_lo', np.nan):5.2f}, {r.get('T_ratio_hi', np.nan):5.2f}] Crep {r.get('C_rep', np.nan):5.2f} "
              f"Croom {r.get('C_room', np.nan):5.2f}")


if __name__ == "__main__":
    main()
