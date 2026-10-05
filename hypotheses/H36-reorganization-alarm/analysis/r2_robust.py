"""H36 round 2 (2026-10-05): robustness of the frozen operator rule C3 (R1 >= 3 or Z_cont >= 2 on days -1..+1).

Reads the 6 content variants built by r2_content.py and scored by evaluate.py (--r1b ../r2/rob_<model>_<dedupe>):
  - C3 hit and window FAR, R1 AUC (day 0 vs placebo days), per variant (no re-tuning);
  - Monday-matched placebos: M1 = round-1b placebo days after a >= 2-calendar-day gap; M2 = every scored day after
    such a gap that is >= 2 active days from every goal kickoff and is not day 0 of any catalogued event;
    stratified Monday / other comparison;
  - shared-prior variant: R1_sr (style-residualized agent-day vectors), its AUC and the rule C3_sr;
  - seed sensitivity: the restate variants against the stored round-1b builds.
Output: data/processed/H36-reorganization-alarm/r2/robust.json

Usage: uv run python hypotheses/H36-reorganization-alarm/analysis/r2_robust.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h36lib as L  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

R2 = L.OUT / "r2"
VARS = [(m, d) for m in ("bge", "gte") for d in ("none", "restate", "copies")]


def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n; den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (float(max(0, c - h)), float(min(1, c + h)))


def evaluate_variant(tag: str, rng) -> dict:
    d = R2 / tag
    sc = pl.read_parquet(d / "scores.parquet").sort("aday")
    ds = pl.read_parquet(d / "day_stats.parquet").sort("aday")
    ev = pl.read_parquet(d / "events.parquet")
    allev = pl.read_parquet(d / "allevents.parquet")
    res = json.loads((d / "results.json").read_text())
    aday = sc["aday"].to_numpy()
    pos = {int(a): i for i, a in enumerate(aday)}
    R1 = sc["R1"].to_numpy().astype(float); ZC = sc["Z_cont"].to_numpy().astype(float)
    R1sr = L.trailing_z(ds["R1_sr"].to_numpy().astype(float))
    rules = {"C3": np.fmax(R1 - 1.0, ZC), "C3_sr": np.fmax(R1sr - 1.0, ZC), "R1": R1, "R1_sr": R1sr, "Z_cont": ZC}
    placebo = sc["placebo"].to_numpy(); monday = sc["monday"].to_numpy()
    goal = ev.filter((pl.col("cls") == "goal") & ~pl.col("holdout0"))
    gday = goal["aday0"].drop_nulls().to_numpy()
    ev_d0 = set(allev["aday0"].drop_nulls().to_list())
    dist_goal = np.array([np.min(np.abs(gday - a)) for a in aday])
    anyfin = np.isfinite(rules["C3"])
    M1 = placebo & monday
    M2 = monday & (dist_goal >= 2) & np.array([int(a) not in ev_d0 for a in aday]) & anyfin

    def val(k, a):
        i = pos.get(int(a))
        return np.nan if i is None else rules[k][i]

    def wmax(k, c):
        v = [val(k, c + o) for o in (-1, 0, 1)]
        v = [x for x in v if np.isfinite(x)]
        return max(v) if v else np.nan

    kick = [int(a) for a in gday if any(np.isfinite(val("C3", a + o)) for o in (-1, 0, 1))]
    kmon = np.array([bool(monday[pos[a]]) if a in pos else False for a in kick])
    out = {"n_kickoffs": len(kick), "n_monday_kickoffs": int(kmon.sum()), "n_placebo": int(placebo.sum()),
           "n_M1": int(M1.sum()), "n_M2": int(M2.sum())}
    for k in rules:
        kw = np.array([wmax(k, c) for c in kick])
        hit = np.nan_to_num(kw, nan=-9) >= 2.0
        r = {"hit": float(hit.mean()), "hit_monday": float(hit[kmon].mean()) if kmon.any() else None,
             "hit_other": float(hit[~kmon].mean()) if (~kmon).any() else None}
        for nm, mask in (("placebo", placebo), ("M1", M1), ("M2", M2), ("nonmonday_placebo", placebo & ~monday)):
            cents = aday[mask]
            pw = np.array([wmax(k, c) for c in cents])
            fa = int(np.sum(np.nan_to_num(pw, nan=-9) >= 2.0))
            r[f"far_win_{nm}"] = fa / max(1, cents.size)
            r[f"far_win_{nm}_k"] = fa
            r[f"far_win_{nm}_wilson"] = wilson(fa, cents.size)
            d0 = np.array([val(k, c) for c in kick])
            r[f"auc_d0_vs_{nm}"] = L.auc(d0, rules[k][mask])
            r[f"auc_win_vs_{nm}"] = L.auc(kw, pw)
        # stratified: Monday kickoffs vs Monday placebo windows (M2), other kickoffs vs other placebo windows
        pwM2 = np.array([wmax(k, c) for c in aday[M2]])
        pwO = np.array([wmax(k, c) for c in aday[placebo & ~monday]])
        r["auc_win_monday_vs_M2"] = L.auc(kw[kmon], pwM2) if kmon.any() else None
        r["auc_win_other_vs_nonmonday"] = L.auc(kw[~kmon], pwO) if (~kmon).any() else None
        r["auc_d0_ci"] = L.auc_ci(np.array([val(k, c) for c in kick]), rules[k][placebo], rng, 1000)
        out[k] = r
    out["evaluate_json"] = {"C3_hit": res["classes"]["goal"]["C3"]["hit"], "C3_far_win": res["classes"]["goal"]["C3"]["far_win"],
                            "R1_auc_d0": res["classes"]["goal"]["R1"]["auc_d0"], "Zcont_auc_d0": res["classes"]["goal"]["Z_cont"]["auc_d0"],
                            "Zphys_auc_d0": res["classes"]["goal"]["Z_phys"]["auc_d0"],
                            "Zphys_random_date_p": res["random_date"]["Z_phys"]["p"],
                            "R1_auc_vs_monday": res["classes"]["goal"]["R1"]["auc_d0_vs_monday"]}
    return out


def seed_check(m: str) -> dict:
    a = pl.read_parquet(R2 / f"rob_{m}_restate" / "scores.parquet").sort("aday")
    b = pl.read_parquet(L.OUT / "r1b" / f"fixed_{m}_restate" / "scores.parquet").sort("aday")
    x = a["Z_cont"].to_numpy().astype(float); y = b["Z_cont"].to_numpy().astype(float)
    ok = np.isfinite(x) & np.isfinite(y)
    rb = json.loads((L.OUT / "r1b" / f"fixed_{m}_restate" / "results.json").read_text())["classes"]["goal"]["C3"]
    ra = json.loads((R2 / f"rob_{m}_restate" / "results.json").read_text())["classes"]["goal"]["C3"]
    return {"median_abs_dZcont": float(np.median(np.abs(x[ok] - y[ok]))), "max_abs_dZcont": float(np.max(np.abs(x[ok] - y[ok]))),
            "corr": float(np.corrcoef(x[ok], y[ok])[0, 1]), "C3_hit_stored": rb["hit"], "C3_hit_new": ra["hit"],
            "C3_farwin_stored": rb["far_win"], "C3_farwin_new": ra["far_win"]}


def seed_spread(m: str) -> dict:
    """Post hoc (2026-10-05): C3 hit and window FAR over the round-2 seed, the stored 1b seed and 8 extra seeds."""
    dirs = [L.OUT / "r1b" / f"fixed_{m}_restate", R2 / f"rob_{m}_restate"] + sorted(R2.glob(f"rob_{m}_restate_s*"))
    hit, far, auc = [], [], []
    for d in dirs:
        c = json.loads((d / "results.json").read_text())["classes"]["goal"]
        hit.append(c["C3"]["hit"]); far.append(c["C3"]["far_win"]); auc.append(c["Z_cont"]["auc_d0"])
    q = lambda x: [float(np.min(x)), float(np.median(x)), float(np.max(x))]  # noqa: E731
    return {"n_seeds": len(dirs), "C3_hit_min_med_max": q(hit), "C3_farwin_min_med_max": q(far),
            "Zcont_auc_min_med_max": q(auc), "C3_hit": hit, "C3_farwin": far}


def main():
    rng = np.random.default_rng(L.SEED + 2)
    out = {"variants": {}, "seed": {m: seed_check(m) for m in ("bge", "gte")},
           "seed_spread": {m: seed_spread(m) for m in ("bge", "gte")}}
    for m, d in VARS:
        out["variants"][f"{m}_{d}"] = evaluate_variant(f"rob_{m}_{d}", rng)
    v = out["variants"]
    robust = all(v[k]["C3"]["hit"] >= 0.45 and v[k]["C3"]["far_win_placebo"] <= 0.15 for k in v) and \
        all(v[k]["C3"]["far_win_M1"] <= 0.20 and v[k]["C3"]["far_win_M2"] <= 0.20 for k in v)
    out["kill_rule_robust"] = bool(robust)
    (R2 / "robust.json").write_text(json.dumps(out, indent=1, default=float))
    print(f"{'variant':12s} {'C3 hit':>7s} {'FARwin':>7s} {'M1':>9s} {'M2':>9s} {'hitMon':>7s} {'hitOth':>7s} {'R1auc':>6s} "
          f"{'R1vM2':>6s} {'R1sr':>6s} {'C3sr hit/FAR':>13s} {'Zph p':>6s}")
    for k, r in v.items():
        c = r["C3"]
        print(f"{k:12s} {c['hit']:7.2f} {c['far_win_placebo']:7.2f} {c['far_win_M1']:5.2f}/{r['n_M1']:<3d} {c['far_win_M2']:5.2f}/{r['n_M2']:<3d} "
              f"{c['hit_monday']:7.2f} {c['hit_other']:7.2f} {r['R1']['auc_d0_vs_placebo']:6.2f} {r['R1']['auc_d0_vs_M2']:6.2f} "
              f"{r['R1_sr']['auc_d0_vs_placebo']:6.2f} {r['C3_sr']['hit']:6.2f}/{r['C3_sr']['far_win_placebo']:.2f} "
              f"{r['evaluate_json']['Zphys_random_date_p']:6.3f}")
    print("seed", json.dumps(out["seed"], indent=None))
    print("seed spread", json.dumps({m: {k: v for k, v in r.items() if "min_med" in k or k == "n_seeds"} for m, r in out["seed_spread"].items()}))
    print("robust by kill rule:", robust)


if __name__ == "__main__":
    main()
