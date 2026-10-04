"""H91 confirmatory test on the locked holdout. FROZEN 2026-10-04 (round 1). DO NOT RUN without Vivian's sign-off.

Guard: runs on held-out data only with BOTH `--confirm` and the environment variable H91_CONFIRM=1, and only after
infra/shared/holdout_ledger.check() reports the target as allowed. Without them, `--dry-run` applies the same frozen
pipeline and rules to the non-holdout days (stand-ins), so the mechanics can be checked; the dry run reads no held-out
row (daymat.ALLOW_HOLDOUT stays False).

Frozen design (round 1 estimators, unchanged): content day arrays (bge + gte, kind- and agent-day-centered), talk spins
in the all-present window; rotation delta_2 between consecutive active days (common agents >= 4); same-day block
bootstrap null (R = 199); trailing alarm A (B = 10, all active days in time order, as a live monitor would see them);
A_C = mean of the two models. Rival R1 is recomputed here for every day (H36 rule: 1 - cos of consecutive day centroids
of raw agent-day vectors centred on the non-holdout mean; day-present agents = agents with an agent-day vector; trailing
z), averaged over the two models.
Targets: day 0 of held-out goal kickoffs (H36 r1b catalog, holdout0) with a scored pair; held-out placebo days (>= 3
active days from every catalogued event date); held-out quiet pairs (>= 2 active days from any event) for C2/C3.

Frozen predictions (written 2026-10-04 after round 1; credences in brackets). They test the claim that stands:
  C1 (primary, negative): AUC(A_C, kickoff day 0 vs held-out placebo days) < 0.70 AND AUC(R1) - AUC(A_C) >= 0.15 [0.7].
  C2 (slow drift): median content z_boot over held-out quiet pairs is in [0.75, 1.5] [0.6].
  C3 (Dyson between events): share of held-out quiet content pairs with p_boot < 0.05 (mean of models) <= 0.20 [0.6].
  C4 (complement): Spearman(A_C, R1) over held-out scored days < 0.3 [0.7].
  Overall: CONFIRMED if C1 and C4 pass; PARTIAL if one passes; NOT CONFIRMED otherwise. C2 and C3 are reported.
Reuse disclosure: H36 (R1 on held-out kickoffs), H74 (content channel C = R1) and H12 (content modes on held-out units)
plan the same targets; R1 here is a rival, not a new test of R1.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import zlib

import numpy as np
import polars as pl

import h91lib as L

DM = L.DM
sys.path.insert(0, str(L.ROOT / "infra/shared"))
FROZEN = {"C1_auc_max": 0.70, "C1_gap_min": 0.15, "C2_lo": 0.75, "C2_hi": 1.5, "C3_max": 0.20, "C4_max": 0.3,
          "R": L.R_NULL, "k": L.K_PRIMARY, "B": L.BASE_DAYS, "placebo_dist": 3, "quiet_dist": 2}
H36 = L.ROOT / "data/processed/H36-reorganization-alarm/r1b/fixed_bge_none"
OUTC = L.OUT / "confirm"


def all_days() -> list[str]:
    cal = pl.read_parquet(DM.SH / "calendar.parquet").filter(pl.col("goal_no").is_not_null()).sort("pt_date")
    if not DM.ALLOW_HOLDOUT:
        cal = cal.filter(~pl.col("holdout"))
    return cal["pt_date"].to_list()


def r1_series(days: list[str], model: str) -> np.ndarray:
    ad = pl.read_parquet(DM.ED / "agent_day.parquet").with_row_index("r")
    V = np.load(DM.ED / ("agent_day_vec.npy" if model == "bge" else "agent_day_vec_gte_modernbert.npy"), mmap_mode="r")
    mu = np.asarray(V[ad.filter(~pl.col("holdout"))["r"].to_numpy()], dtype=np.float64).mean(0)
    cent = {}
    for d in days:
        rows = ad.filter(pl.col("pt_date") == d)["r"].to_numpy()
        if len(rows):
            X = np.asarray(V[rows], dtype=np.float64) - mu
            X /= np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-12)
            cent[d] = X.mean(0)
    out = np.full(len(days), np.nan)
    for i in range(1, len(days)):
        a, b = cent.get(days[i - 1]), cent.get(days[i])
        if a is not None and b is not None:
            out[i] = 1 - a @ b / (np.linalg.norm(a) * np.linalg.norm(b))
    return L.trailing_z(out)


def rotation(days: list[str], tmp) -> dict:
    out = {}
    for m in DM.MODELS:
        dd = DM.build_content(m)
        z = np.full(len(days), np.nan); p = np.full(len(days), np.nan)
        for i in range(1, len(days)):
            a, b = dd.get(days[i - 1]), dd.get(days[i])
            if a is None or b is None:
                continue
            com = np.intersect1d(a["agents"], b["agents"])
            if len(com) < DM.MIN_AGENTS:
                continue
            rng = np.random.default_rng(zlib.crc32(f"confirm|{m}|{days[i]}".encode()) + L.SEED)
            r = L.rot_content(a["Z"][np.searchsorted(a["agents"], com)].astype(float),
                              b["Z"][np.searchsorted(b["agents"], com)].astype(float), rng, R=FROZEN["R"])
            z[i], p[i] = r["z2_boot"], r["p2_boot"]
        out[m] = (z, p)
    return out


def distances(days: list[str]) -> np.ndarray:
    ev = pl.read_parquet(H36 / "allevents.parquet")
    edays = set(ev["t"].dt.convert_time_zone("America/Los_Angeles").dt.strftime("%Y-%m-%d").to_list())
    pos = [i for i, d in enumerate(days) if d in edays]
    return np.array([min([abs(i - j) for j in pos]) if pos else 99 for i in range(len(days))])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.confirm:
        if os.environ.get("H91_CONFIRM") != "1":
            sys.exit("refused: set H91_CONFIRM=1 (Vivian's sign-off) as well as --confirm")
        import holdout_ledger as HL
        for tgt in ("G28", "G29", "G45", "G46", "G47", "G48", "G49", "G50", "#51-tail"):
            chk = HL.check("H91", tgt, "content", ["spectral_mode"])
            if not chk["allowed"]:
                sys.exit(f"refused by the holdout ledger: {tgt} {chk}")
        DM.ALLOW_HOLDOUT = True
    elif not a.dry_run:
        sys.exit("use --dry-run (non-holdout stand-ins) or --confirm with H91_CONFIRM=1")
    OUTC.mkdir(parents=True, exist_ok=True)
    days = all_days()
    cal = pl.read_parquet(DM.SH / "calendar.parquet").select("pt_date", "holdout")
    hold = dict(zip(cal["pt_date"].to_list(), cal["holdout"].to_list()))
    target = np.array([hold[d] for d in days]) if a.confirm else np.ones(len(days), bool)
    rot = rotation(days, OUTC)
    A = np.nanmean([L.trailing_z(rot[m][0]) for m in DM.MODELS], axis=0)
    zc = np.nanmean([rot[m][0] for m in DM.MODELS], axis=0)
    pc = [rot[m][1] for m in DM.MODELS]
    R1 = np.nanmean([r1_series(days, m) for m in DM.MODELS], axis=0)
    dist = distances(days)
    ev = pl.read_parquet(H36 / "events.parquet").filter(pl.col("cls") == "goal")
    ev = ev.filter(pl.col("holdout0") if a.confirm else ~pl.col("holdout0"))
    kd = set(ev["pt_date0"].to_list())
    kick = np.array([d in kd for d in days]) & target
    plc = (dist >= FROZEN["placebo_dist"]) & target
    quiet = (dist >= FROZEN["quiet_dist"]) & target
    rng = np.random.default_rng(L.SEED)
    aucA = L.auc_ci(A[kick], A[plc], rng); aucR = L.auc_ci(R1[kick], R1[plc], rng)
    zq = zc[quiet]; zq = zq[np.isfinite(zq)]
    s3 = np.mean([np.nanmean(p[quiet][np.isfinite(p[quiet])] < 0.05) for p in pc])
    rho = L.spearman(A[target], R1[target])
    res = {"mode": "confirm" if a.confirm else "dry-run (non-holdout stand-ins)", "frozen": FROZEN,
           "n_kickoffs_scored": int(np.isfinite(A[kick]).sum()), "n_placebo": int(np.isfinite(A[plc]).sum()),
           "C1": {"auc_A_C": aucA, "auc_R1": aucR, "pass": bool(aucA[0] < FROZEN["C1_auc_max"] and aucR[0] - aucA[0] >= FROZEN["C1_gap_min"])},
           "C2": {"median_z": float(np.median(zq)) if len(zq) else None, "n": int(len(zq)),
                  "pass": bool(len(zq) and FROZEN["C2_lo"] <= np.median(zq) <= FROZEN["C2_hi"])},
           "C3": {"s_sig": float(s3), "pass": bool(s3 <= FROZEN["C3_max"])},
           "C4": {"spearman": rho, "pass": bool(rho < FROZEN["C4_max"])}}
    res["overall"] = ("CONFIRMED" if res["C1"]["pass"] and res["C4"]["pass"] else
                      "PARTIAL" if res["C1"]["pass"] or res["C4"]["pass"] else "NOT CONFIRMED")
    name = "confirm.json" if a.confirm else "dryrun.json"
    (OUTC / name).write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
