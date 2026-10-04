"""H49 confirmatory test on the LOCKED HOLDOUT, RE-FROZEN ON THE CORRECTED INPUTS (written 2026-10-04; NOT RUN).

Re-freeze of `confirm.py` (left byte-for-byte untouched; holdout.md ledger item 17). Written before any holdout data
was read. Details and reasons: `CONFIRM_R1B.md`.

What changed vs confirm.py
  * Inputs: the loader read the buggy `activity_bins`, `reasons` and `stall_minutes`, although round 1 (Amendment 2)
    ran on the fixed tables. It now reads `activity_bins_fixed` and the `outages_fixed/{reasons,stall_minutes}`
    sidecar (H38's rule rebuilt from the fixed bins), exactly as `scheme/build_units.py` does for exploration.
    The scheduler is removed by H38's agent-state conditioning (PL-c), which infra/README.md accepts in place of the
    DQ8 all-present trim; the infra_err silence reason comes from `turn_errors` platform-error classes (H38), not from
    `actions.error`. No content, visibility, work or nudge-target input is used.
  * Predictions: C1-C6 unchanged. They were set on the fixed-bin exploration (Amendment 2), so the corrected loader
    makes the script test what the card says; no exploratory result changed.
  * Guards added: commit check (reuse policy item 1) and a holdout-ledger gate (infra/shared/holdout_ledger.check):
    a target with a same-family, same-modality prior confirmatory run is EXCLUDED by default. The ledger gives
    #45 (H02: Curie-Weiss gain and pairwise couplings, activity) and #47, #49 (H04: MF coupling, activity) as such
    collisions. `--include-ledger-blocked` re-includes them; use it only on Vivian's written override (LOG.md).
  * Head bonds for C5 come from the round-1 fixed-bin `bonds/<unit>.parquet` (as before).

Frozen predictions (card "Confirmatory predictions"; unchanged):
  C1  median share of pairs with a significant positive conditioned bond <= 0.03 over regime-III holdout units, and
      pooled significant positive bonds per unit <= 3 (about 1 false per unit expected).
  C2  raw -> conditioned loss of significant positive bonds: regime-III median >= 0.5; regime-I median smaller.
  C3  among regime-III units with conditioned excess z_g > 2: >= 2/3 have CV-C10 <= 0.25 and none >= 0.5.
  C4  kappa < 2 in >= 2/3 of regime-III units (power-limited; reported).
  C5  |r| < 0.15 between the #51 tail (51m) bond z and the head (51h, 51i, 51j mean z).
  C6  same-lab Mantel-Haenszel OR of significant positive bonds < 2 over regime-III units.

Holdout units: regime III 45a, 45b, 47, 49, 51m; regime I 14, 15b, 22a, 22b (>= 2 days, >= 6 present agents).
Guard: refuses to touch the holdout without BOTH --confirm and --i-understand-this-uses-the-locked-holdout, refuses
if the H49 card or this script has uncommitted changes. --dry-run runs the identical code on non-holdout stand-ins
(III: 39, 41, 42b, 51h with head 51f, 51g; I: 17, 23, 26) into data/processed/H49-dilute-ferromagnet/confirm_r1b_dryrun/.

Usage: uv run python hypotheses/H49-dilute-ferromagnet/analysis/confirm_r1b.py --dry-run [--n-surr 200 --n-boot 200]
       uv run python hypotheses/H49-dilute-ferromagnet/analysis/confirm_r1b.py --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "2")
import argparse  # noqa: E402
import importlib.util  # noqa: E402
import json  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
import zlib  # noqa: E402
from pathlib import Path  # noqa: E402

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "infra/shared"))
import h49lib as L  # noqa: E402

import holdout_ledger as HL  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from common import holdout_mask  # noqa: E402

HYP = "H49"
HOLDOUT = {"III": ["45a", "45b", "47", "49", "51m"], "I": ["14", "15b", "22a", "22b"]}
STANDINS = {"III": ["39", "41", "42b", "51h"], "I": ["17", "23", "26"]}
LEDGER_TARGET = {"45a": "G45", "45b": "G45", "47": "G47", "49": "G49", "51m": "#51-tail", "14": "G14", "15b": "G15",
                 "22a": "G22", "22b": "G22"}
MODALITY = "activity timing"
STATISTIC = ("conditioned equal-time pseudolikelihood pairwise coupling bonds J_ij, excess-covariance concentration "
             "CV-C10, conditioned variance ratio gain g")
INPUTS = {"bins": "activity_bins_fixed.parquet", "reasons": "outages_fixed/reasons.parquet",
          "stall": "outages_fixed/stall_minutes.parquet"}
FROZEN = {
    "frozen_at": "2026-10-04 (confirm.py, after exploratory round 1 on fixed bins); re-frozen on corrected loader "
                 "2026-10-04 (confirm_r1b.py); thresholds unchanged",
    "C1_median_frac_pos_max": 0.03, "C1_pooled_ratio_max": 3.0,
    "C2_loss_III_min": 0.5,
    "C3_dense_cv_max": 0.25, "C3_frac_min": 2 / 3, "C3_dilute_cv": 0.5,
    "C4_frac_below_min": 2 / 3,
    "C5_tail_head_abs_r_max": 0.15,
    "C6_same_lab_or_max": 2.0,
}


def scheme():
    spec = importlib.util.spec_from_file_location("h49_build_units", L.HYP / "scheme/build_units.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def committed_or_die():
    paths = [str(L.HYP / "README.md"), str(HERE / "confirm_r1b.py")]
    for p in paths:
        tracked = subprocess.run(["git", "-C", str(L.ROOT), "ls-files", "--error-unmatch", p], capture_output=True).returncode == 0
        dirty = subprocess.run(["git", "-C", str(L.ROOT), "status", "--porcelain", "--", p], capture_output=True, text=True).stdout
        if not tracked or dirty.strip():
            raise SystemExit(f"refusing (reuse policy item 1): commit {p} unmodified before the confirmatory run")


def ledger_gate(units, include_blocked: bool):
    """Ledger check per target. Returns (units kept, report). A same-family, same-modality prior run blocks a target."""
    fam = HL.family_of(STATISTIC)
    rep, keep = {}, []
    for u in units:
        t = LEDGER_TARGET[u]
        r = HL.check(HYP, t, MODALITY, fam)
        same = sorted({x["hypothesis"] for x in r["prior_runs_same_family"] if x["modality"] == MODALITY})
        rep[u] = {"target": t, "allowed": r["allowed"], "same_family_same_modality_runs": same,
                  "prior_runs": sorted({x["hypothesis"] for x in r["prior_runs"]}),
                  "competing_planned": sorted({x["hypothesis"] for x in r["competing_planned"]}),
                  "needs_disclosure": r["needs_disclosure"]}
        if same and not include_blocked:
            rep[u]["used"] = False
            continue
        rep[u]["used"] = True
        keep.append(u)
    return keep, {"family": fam, "modality": MODALITY, "units": rep}


_TABLES = {}


def tables():
    """Corrected inputs (read once). Columns as the exploratory scheme."""
    if not _TABLES:
        _TABLES["ab"] = pl.read_parquet(L.SH / INPUTS["bins"], columns=["pt_date", "minute", "agent", "state"]).with_columns(
            pl.col("minute").cast(pl.Int32))
        _TABLES["rs"] = pl.read_parquet(L.SH / INPUTS["reasons"])
        _TABLES["sm"] = pl.read_parquet(L.SH / INPUTS["stall"], columns=["pt_date", "minute", "scheduled"])
    return _TABLES


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
    T = tables()
    agents = B.present(T["ab"], days)
    if len(days) < B.MIN_DAYS or len(agents) < B.MIN_N:
        return None
    S, Tk, R, day, minute, sched = B.matrices(T["ab"], T["rs"], T["sm"], days, agents)
    return {"S": S, "Tk": Tk, "R": R, "day": day, "minute": minute, "sched": sched, "agents": np.array(agents),
            "days": days, "regime": pu["regime"]}


def run_units(units, allow_holdout, n_surr, n_boot):
    out = {}
    for u in units:
        t0 = time.time()
        m = load_unit_mats(u, allow_holdout)
        if m is None:
            out[u] = None
            continue
        res = L.run_dataset(m["S"], m["R"], m["sched"], m["day"], m["minute"], m["Tk"], n_surr=n_surr,
                            seed=L.SEED + 777 + zlib.crc32(u.encode()) % 100_000, n_boot=n_boot)
        v = res["variants"]
        iu = L.triu(res["N"])
        ag = m["agents"]
        out[u] = {"regime": m["regime"], "N": res["N"], "days": len(m["days"]), "n_pairs": res["n_pairs"],
                  "agents": ag.tolist(),
                  "n_pos": v["scaffold"]["bonds"]["n_pos"], "n_pos_raw": v["raw"]["bonds"]["n_pos"],
                  "kappa": v["scaffold"]["graph"]["kappa"], "S1": v["scaffold"]["graph"]["S1"],
                  "z_g": v["scaffold"]["z_g"], "cv_c10": v["scaffold"]["cv_c10"], "mean_z": v["scaffold"]["bonds"]["mean_z"],
                  "z": dict(zip([f"{a}-{b}" for a, b in zip(ag[iu[0]], ag[iu[1]])], v["scaffold"]["bonds"]["z"].tolist())),
                  "sig": [f"{a}-{b}" for a, b, s_ in zip(ag[iu[0]], ag[iu[1]], v["scaffold"]["bonds"]["sig_pos"]) if s_],
                  "secs": round(time.time() - t0, 1)}
        if not allow_holdout:
            print(f"  {u}: N {res['N']}, n_pos {out[u]['n_pos']} (raw {out[u]['n_pos_raw']}), kappa {out[u]['kappa']:.2f}, "
                  f"z_g {out[u]['z_g']:.2f}, cv_c10 {out[u]['cv_c10']}, {out[u]['secs']} s", flush=True)
    return out


def score(res, head_units):
    r3 = {k: r for k, r in res.items() if r and r["regime"] == "III"}
    r1 = {k: r for k, r in res.items() if r and r["regime"] == "I"}
    frac = [r["n_pos"] / r["n_pairs"] for r in r3.values()]

    def loss(rs):
        return [(r["n_pos_raw"] - r["n_pos"]) / r["n_pos_raw"] for r in rs.values() if r["n_pos_raw"] >= 1]
    l3, l1 = loss(r3), loss(r1)
    pooled = sum(r["n_pos"] for r in r3.values()) / max(len(r3), 1)
    sc = {"C1": {"median_frac_pos": float(np.median(frac)) if frac else None, "pooled_ratio": pooled},
          "C2": {"median_loss_III": float(np.median(l3)) if l3 else None, "median_loss_I": float(np.median(l1)) if l1 else None}}
    sc["C1"]["pass"] = bool(frac and np.median(frac) <= FROZEN["C1_median_frac_pos_max"] and pooled <= FROZEN["C1_pooled_ratio_max"])
    sc["C2"]["pass"] = bool(l3 and np.median(l3) >= FROZEN["C2_loss_III_min"] and (not l1 or np.median(l1) < np.median(l3)))
    ex = {k: r for k, r in r3.items() if r["z_g"] > 2 and r["cv_c10"] is not None and np.isfinite(r["cv_c10"])}
    cvs = [r["cv_c10"] for r in ex.values()]
    sc["C3"] = {"excess_units": list(ex), "cv_c10": cvs,
                "pass": (bool(np.mean([c <= FROZEN["C3_dense_cv_max"] for c in cvs]) >= FROZEN["C3_frac_min"]
                              and not any(c >= FROZEN["C3_dilute_cv"] for c in cvs)) if cvs else None)}
    sc["C4"] = {"frac_below": float(np.mean([r["kappa"] < 2 for r in r3.values()])) if r3 else None}
    sc["C4"]["pass"] = None if sc["C4"]["frac_below"] is None else sc["C4"]["frac_below"] >= FROZEN["C4_frac_below_min"]
    tail = [k for k in res if k in ("51m", "51h") and res[k]]
    sc["C5"] = {"pass": None, "note": "tail or head missing"}
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
            sc["C5"] = {"r": r, "n_pairs": len(common), "head": head_units, "pass": abs(r) < FROZEN["C5_tail_head_abs_r_max"]}
    lab = dict(pl.read_parquet(L.SH / "roster.parquet").select("agent", "lab").iter_rows())
    num = den = 0.0
    for r in r3.values():
        A, S_ = [], []
        sig = set(r["sig"])
        for k in r["z"]:
            a, c = map(int, k.split("-"))
            A.append(lab.get(a) == lab.get(c))
            S_.append(k in sig)
        A, S_ = np.array(A), np.array(S_)
        n = A.size
        num += (A & S_).sum() * (~A & ~S_).sum() / n
        den += (A & ~S_).sum() * (~A & S_).sum() / n
    orr = num / den if den > 0 else None
    sc["C6"] = {"same_lab_OR_MH": orr, "pass": bool(orr is None or orr < FROZEN["C6_same_lab_or_max"])}
    return sc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ok", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--include-ledger-blocked", action="store_true",
                    help="re-include #45/#47/#49 (same-family same-modality prior runs); only on Vivian's written override")
    ap.add_argument("--n-surr", type=int, default=200)
    ap.add_argument("--n-boot", type=int, default=200)
    a = ap.parse_args()
    t0 = time.time()
    if a.dry_run and not (a.confirm or a.ok):
        units = STANDINS["III"] + STANDINS["I"]
        outdir = L.DATA / "confirm_r1b_dryrun"
        gate = {"note": "dry run: stand-ins are not held out; ledger gate exercised on the holdout target list"}
        _, gate["holdout_targets"] = ledger_gate(HOLDOUT["III"] + HOLDOUT["I"], a.include_ledger_blocked)
        print("DRY RUN (non-holdout stand-ins), corrected inputs:", INPUTS, flush=True)
        res = run_units(units, False, a.n_surr, a.n_boot)
        heads = ["51f", "51g"]
    elif a.confirm and a.ok and not a.dry_run:
        committed_or_die()
        units, gate = ledger_gate(HOLDOUT["III"] + HOLDOUT["I"], a.include_ledger_blocked)
        print("CONFIRMATORY RUN on the locked holdout. Ledger gate:", json.dumps(gate, indent=1))
        print("DISCLOSE in the H49, H02 and H04 cards and LOG.md: #45 (H02), #47/#49 (H04, NE21+NE23) were used for "
              "activity statistics; H49 computes conditioned pairwise bonds and their concentration.")
        outdir = L.DATA / "confirm_r1b"
        res = run_units(units, True, a.n_surr, a.n_boot)
        heads = ["51h", "51i", "51j"]
    else:
        raise SystemExit("refusing: pass --dry-run, or --confirm --i-understand-this-uses-the-locked-holdout")
    sc = score(res, heads)
    outdir.mkdir(parents=True, exist_ok=True)
    meta = {"script": "hypotheses/H49-dilute-ferromagnet/analysis/confirm_r1b.py", "inputs": INPUTS, "ledger": gate,
            "n_surr": a.n_surr, "n_boot": a.n_boot, "secs": round(time.time() - t0, 1),
            "built_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    (outdir / "results.json").write_text(json.dumps({"frozen": FROZEN, "meta": meta, "units": res, "score": sc},
                                                    indent=1, default=float))
    print(json.dumps(sc, indent=1, default=float))
    print(f"-> {outdir / 'results.json'} ({meta['secs']} s)")


if __name__ == "__main__":
    main()
