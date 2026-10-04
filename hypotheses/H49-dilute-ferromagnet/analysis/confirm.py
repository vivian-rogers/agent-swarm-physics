"""H49 confirmatory test on the LOCKED HOLDOUT. Written and dry-run in round 1; NOT RUN.

Frozen predictions (see the card, "Confirmatory predictions"): FROZEN dict below. They confirm round 1's findings
(bonds at the false floor, trimming removes bonds in regime III, a dense not dilute residual, no stable pair
structure, no provider field), not H49's original claims, which round 1 refuted. The same pipeline as round 1
(h49lib.run_dataset: conditioned / edge / raw pseudolikelihood bonds, 200 joint block-shift surrogates,
one-sided empirical p < 1/n_pairs, 200 day-block bootstraps) on the holdout units:
  regime III: 45a, 45b (#45), 47, 49 (#47, #49; inside the NE21+NE23 window), 51m (#51 tail);
  regime I contrast: 14, 15b, 22a, 22b.
Eligibility as round 1 (>= 2 days, >= 6 present agents).

Reuse policy: H02 used #45's activity couplings (KI-1 leader influence and the EQ-PL hub rank, i.e. the raw PL-r
variant at the hub level); H23 used #45's content. Nobody has looked at #45's conditioned bond distribution,
significant-bond graph or concentration. #47, #49, #51m, #14, #15, #22: no activity-coupling analysis has read them.

Guard: refuses to touch the holdout without both --confirm and --i-understand-this-uses-the-locked-holdout.
--dry-run runs the identical code on non-holdout stand-ins (III: 39, 41, 42b, 51h; I: 17, 23, 26) and writes to
data/processed/H49-dilute-ferromagnet/confirm_dryrun/.

Usage: uv run python hypotheses/H49-dilute-ferromagnet/analysis/confirm.py --dry-run
       uv run python hypotheses/H49-dilute-ferromagnet/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse  # noqa: E402
import importlib.util  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import zlib  # noqa: E402
from pathlib import Path  # noqa: E402

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "infra/shared"))
import h49lib as L  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from common import holdout_mask  # noqa: E402

HOLDOUT = {"III": ["45a", "45b", "47", "49", "51m"], "I": ["14", "15b", "22a", "22b"]}
STANDINS = {"III": ["39", "41", "42b", "51h"], "I": ["17", "23", "26"]}
FROZEN = {
    "frozen_at": "2026-10-04 after exploratory round 1 (fixed activity bins); confirms round 1's findings, see card",
    # C1 bonds at the floor: median share of pairs with a significant positive conditioned bond <= 0.03 over
    #    holdout regime-III units, and pooled significant positive bonds <= 3 x the expected false count (1 per unit)
    "C1_median_frac_pos_max": 0.03, "C1_pooled_ratio_max": 3.0,
    # C2 trimming: raw -> conditioned loss of significant positive bonds, median over regime-III units >= 0.5; the
    #    regime-I median loss is below the regime-III median loss
    "C2_loss_III_min": 0.5,
    # C3 dense, not dilute (R1): among regime-III holdout units with conditioned excess z_g > 2, >= 2/3 have
    #    CV-C10 (pooled) <= 0.25 and none has CV-C10 >= 0.5
    "C3_dense_cv_max": 0.25, "C3_frac_min": 2 / 3, "C3_dilute_cv": 0.5,
    # C4 below percolation (power-limited, reported): kappa < 2 in >= 2/3 of regime-III units
    "C4_frac_below_min": 2 / 3,
    # C5 no stable pair structure: |r| < 0.15 between #51-tail (51m) bond z and the head (51h, 51i, 51j mean z)
    "C5_tail_head_abs_r_max": 0.15,
    # C6 no provider field: same-lab Mantel-Haenszel OR of significant positive bonds < 2 over regime-III holdout units
    "C6_same_lab_or_max": 2.0,
}


def scheme():
    p = L.HYP / "scheme/build_units.py"
    spec = importlib.util.spec_from_file_location("h49_build_units", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def load_unit_mats(uid, allow_holdout):
    B = scheme()
    pu = pl.read_parquet(L.SH / "period_units.parquet").filter(pl.col("unit_id") == uid).to_dicts()[0]
    cal = pl.read_parquet(L.SH / "calendar.parquet")
    days = sorted(pu["days"])
    held = cal.filter(pl.col("pt_date").is_in(days))["holdout"].any() or any(
        holdout_mask(days, [pu["goal_no"]] * len(days)))
    if held and not allow_holdout:
        raise SystemExit(f"refusing: {uid} is in the locked holdout")
    if not held and allow_holdout and uid in sum(HOLDOUT.values(), []):
        raise SystemExit(f"{uid} expected to be holdout but is not; check holdout.json")
    ab = pl.read_parquet(L.SH / "activity_bins.parquet", columns=["pt_date", "minute", "agent", "state"]).with_columns(
        pl.col("minute").cast(pl.Int32))
    rs = pl.read_parquet(L.SH / "reasons.parquet")
    sm = pl.read_parquet(L.SH / "stall_minutes.parquet", columns=["pt_date", "minute", "scheduled"])
    agents = B.present(ab, days)
    if len(days) < B.MIN_DAYS or len(agents) < B.MIN_N:
        return None
    S, Tk, R, day, minute, sched = B.matrices(ab, rs, sm, days, agents)
    return {"S": S, "Tk": Tk, "R": R, "day": day, "minute": minute, "sched": sched, "agents": np.array(agents),
            "days": days, "regime": pu["regime"]}


def run_units(units, allow_holdout, n_surr, n_boot):
    out = {}
    for u in units:
        m = load_unit_mats(u, allow_holdout)
        if m is None:
            out[u] = None
            continue
        res = L.run_dataset(m["S"], m["R"], m["sched"], m["day"], m["minute"], m["Tk"], n_surr=n_surr,
                            seed=L.SEED + 777 + zlib.crc32(u.encode()) % 100_000, n_boot=n_boot)
        v = res["variants"]
        iu = L.triu(res["N"])
        out[u] = {"regime": m["regime"], "N": res["N"], "days": len(m["days"]), "n_pairs": res["n_pairs"],
                  "agents": m["agents"].tolist(),
                  "n_pos": v["scaffold"]["bonds"]["n_pos"], "n_pos_raw": v["raw"]["bonds"]["n_pos"],
                  "kappa": v["scaffold"]["graph"]["kappa"], "S1": v["scaffold"]["graph"]["S1"],
                  "z_g": v["scaffold"]["z_g"], "cv_c10": v["scaffold"]["cv_c10"], "mean_z": v["scaffold"]["bonds"]["mean_z"],
                  "z": dict(zip([f"{a}-{b}" for a, b in zip(m["agents"][iu[0]], m["agents"][iu[1]])],
                                v["scaffold"]["bonds"]["z"].tolist())),
                  "sig": [f"{a}-{b}" for a, b, s_ in zip(m["agents"][iu[0]], m["agents"][iu[1]],
                                                         v["scaffold"]["bonds"]["sig_pos"]) if s_]}
    return out


def score(res, head_units):
    r3 = {k: r for k, r in res.items() if r and r["regime"] == "III"}
    r1 = {k: r for k, r in res.items() if r and r["regime"] == "I"}
    frac = [r["n_pos"] / r["n_pairs"] for r in r3.values()]
    loss = lambda rs: [(r["n_pos_raw"] - r["n_pos"]) / r["n_pos_raw"] for r in rs.values() if r["n_pos_raw"] >= 1]
    l3, l1 = loss(r3), loss(r1)
    pooled = sum(r["n_pos"] for r in r3.values()) / max(len(r3), 1)
    sc = {"C1": {"median_frac_pos": float(np.median(frac)) if frac else None, "pooled_ratio": pooled},
          "C2": {"median_loss_III": float(np.median(l3)) if l3 else None, "median_loss_I": float(np.median(l1)) if l1 else None}}
    sc["C1"]["pass"] = bool(frac and np.median(frac) <= FROZEN["C1_median_frac_pos_max"] and pooled <= FROZEN["C1_pooled_ratio_max"])
    sc["C2"]["pass"] = bool(l3 and np.median(l3) >= FROZEN["C2_loss_III_min"] and (not l1 or np.median(l1) < np.median(l3)))
    ex = {k: r for k, r in r3.items() if r["z_g"] > 2 and r["cv_c10"] is not None and np.isfinite(r["cv_c10"])}
    cvs = [r["cv_c10"] for r in ex.values()]
    sc["C3"] = {"excess_units": list(ex), "cv_c10": cvs,
                "pass": bool(cvs and np.mean([c <= FROZEN["C3_dense_cv_max"] for c in cvs]) >= FROZEN["C3_frac_min"]
                             and not any(c >= FROZEN["C3_dilute_cv"] for c in cvs))}
    sc["C4"] = {"frac_below": float(np.mean([r["kappa"] < 2 for r in r3.values()])) if r3 else None}
    sc["C4"]["pass"] = sc["C4"]["frac_below"] is not None and sc["C4"]["frac_below"] >= FROZEN["C4_frac_below_min"]
    tail = [k for k in res if k in ("51m", "51h") and res[k]]
    if tail and head_units:
        zt = res[tail[0]]["z"]
        hz = {}
        for hu in head_units:
            b = pl.read_parquet(L.DATA / "bonds" / f"{hu}.parquet").filter(
                (pl.col("variant") == "scaffold") & (pl.col("channel") == "activity"))
            for a, c, z in zip(b["a"].to_list(), b["b"].to_list(), b["z"].to_list()):
                hz.setdefault(f"{a}-{c}", []).append(z)
        common = [k for k in zt if k in hz]
        if len(common) > 10:
            r = float(np.corrcoef([zt[k] for k in common], [np.mean(hz[k]) for k in common])[0, 1])
            sc["C5"] = {"r": r, "n_pairs": len(common), "pass": abs(r) < FROZEN["C5_tail_head_abs_r_max"]}
    lab = dict(pl.read_parquet(L.SH / "roster.parquet").select("agent", "lab").iter_rows())
    num = den = 0.0
    for r in r3.values():
        A = []; S_ = []
        sig = set(r["sig"])
        for k in r["z"]:
            a, c = map(int, k.split("-"))
            A.append(lab.get(a) == lab.get(c)); S_.append(k in sig)
        A = np.array(A); S_ = np.array(S_); n = A.size
        num += (A & S_).sum() * (~A & ~S_).sum() / n; den += (A & ~S_).sum() * (~A & S_).sum() / n
    orr = num / den if den > 0 else None
    sc["C6"] = {"same_lab_OR_MH": orr, "pass": bool(orr is None or orr < FROZEN["C6_same_lab_or_max"])}
    return sc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ok", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--n-surr", type=int, default=200)
    ap.add_argument("--n-boot", type=int, default=200)
    a = ap.parse_args()
    if a.dry_run:
        units = STANDINS["III"] + STANDINS["I"]
        outdir = L.DATA / "confirm_dryrun"
        res = run_units(units, False, a.n_surr, a.n_boot)
        heads = ["51f", "51g"]  # stand-in "head" for the stand-in tail 51h
    elif a.confirm and a.ok:
        units = HOLDOUT["III"] + HOLDOUT["I"]
        outdir = L.DATA / "confirm"
        res = run_units(units, True, a.n_surr, a.n_boot)
        heads = ["51h", "51i", "51j"]
    else:
        raise SystemExit("refusing: pass --dry-run, or --confirm --i-understand-this-uses-the-locked-holdout")
    sc = score(res, heads)
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "results.json").write_text(json.dumps({"frozen": FROZEN, "units": res, "score": sc}, indent=1, default=float))
    print(json.dumps(sc, indent=1, default=float))


if __name__ == "__main__":
    main()
