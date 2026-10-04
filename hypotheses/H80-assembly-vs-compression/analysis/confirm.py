"""H80 CONFIRMATORY test on the LOCKED HOLDOUT. Written 2026-10-04 after exploratory round 1. NOT RUN.

Refuses to read any holdout day unless BOTH flags are given:
    --confirm --i-understand-this-uses-the-locked-holdout
`--dry-run` computes the identical statistics on non-holdout stand-ins (G31, G41, G51); no holdout day is read.

Frozen criteria (machine-readable in PREDICTIONS; the claims that stand after round 1):
  Units: #46, #47, #48, #49, #50 (automation-dense; NE21+NE23 window) and the #51 tail (2026-09-07 -> 09-18).
  Windows, features and classifier exactly as round 1 (scheme/build.py, analysis/h80lib.py; L = 16, cap 20 per
  stream-day). Folds: repo-blocked if the unit has >= 3 automated streams, else day-blocked, else window-level.
  C1  Assembly adds nothing: AUC(C + A) - AUC(C) < 0.02 in every unit with >= 50 windows per class.
      KILL (the AT-positive reading): >= 0.05 in any such unit.
  C2  Spearman(a_RP, LZ78) over windows >= 0.8 in every unit with >= 50 windows.
  C3  The scheduler carries the label: AUC(T) >= 0.9 and AUC(T + C) - AUC(T) < 0.01 in >= 2/3 of eligible units.
  C4  High-index command motifs are single-agent habits: within each regime-III unit (motifs with >= 20 session
      copies), Spearman(a, number of agents using the motif) < 0, and the median number of agents at a >= 6 is <= 3.
  Supported if C1, C2 and C4 hold; failed if C1's kill fires.

Holdout reuse: #46-#50 and the #51 tail are targeted by many scripts. No run has computed commit-window compression
or command-motif statistics there. holdout_ledger.check() is called before reading; disclose in the card and LOG.md
and commit the script first.

Run:   uv run python hypotheses/H80-assembly-vs-compression/analysis/confirm.py --dry-run
Real:  ... --confirm --i-understand-this-uses-the-locked-holdout     (only after Vivian signs off)
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ[_v] = "2"

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "infra/shared"))
import h80lib as L  # noqa: E402
from run import SETS  # noqa: E402

D = ROOT / "data/processed/H80-assembly-vs-compression"
CONF = D / "confirm"
PREDICTIONS = {
    "C1": "AUC(C+A) - AUC(C) < 0.02 in every unit with >= 50 windows per class; KILL if >= 0.05 in any",
    "C2": "Spearman(a_RP, LZ78) >= 0.8 in every unit with >= 50 windows",
    "C3": "AUC(T) >= 0.9 and AUC(T+C) - AUC(T) < 0.01 in >= 2/3 of eligible units",
    "C4": "per regime-III unit: Spearman(a, n_agents) < 0 and median n_agents at a >= 6 <= 3",
}
HOLDOUT = [("G46", 46, None), ("G47", 47, None), ("G48", 48, None), ("G49", 49, None), ("G50", 50, None),
           ("51-tail", 51, "2026-09-07")]
STANDINS = [("G31", 31, None), ("G41", 41, None), ("G51", 51, None)]


def unit_cls(w: pl.DataFrame) -> dict:
    y = w["y"].to_numpy()
    npos = int(w.filter(pl.col("y") == 1)["stream"].n_unique())
    ndays = w["day"].n_unique()
    if npos >= 3:
        g, block = w["repo_h"].to_numpy(), "repo"
    elif ndays >= 3 and w.filter(pl.col("y") == 1)["day"].n_unique() >= 2:
        g, block = np.array([int(x.replace("-", "")) for x in w["day"].to_list()]), "day"
    else:
        g, block = np.arange(w.height), "window"
    out = {"block": block, "n_pos": int(y.sum()), "n_neg": int((1 - y).sum()), "pos_streams": npos}
    if y.sum() == 0 or y.sum() == len(y):
        return out
    sc = {k: L.oof_scores(w.select(f).to_numpy().astype(float), y, g) for k, f in SETS.items()}
    ok = ~np.isnan(np.column_stack(list(sc.values()))).any(1)
    out["auc"] = {k: L.auc(y[ok], v[ok]) for k, v in sc.items()}
    out["dA"] = out["auc"]["C+A"] - out["auc"]["C"]
    out["dC_over_T"] = out["auc"]["T+C"] - out["auc"]["T"]
    out["rho"] = float(spearmanr(w["a_rp"].to_numpy(), w["lz78"].to_numpy())[0])
    return out


def motif_stats(m: pl.DataFrame) -> dict:
    if m.height < 10:
        return {}
    hi = m.filter(pl.col("a") >= 6)["n_agents"]
    return {"rho_a_agents": float(spearmanr(m["a"].to_numpy(), m["n_agents"].to_numpy())[0]),
            "median_agents_a_ge6": float(hi.median()) if hi.len() else None, "n_motifs": m.height}


def evaluate(cls: dict, mot: dict) -> dict:
    el = {u: r for u, r in cls.items() if r.get("auc") and r["n_pos"] >= 50 and r["n_neg"] >= 50}
    big = [r for r in cls.values() if r.get("auc") and r["n_pos"] + r["n_neg"] >= 50]
    ms = [m for m in mot.values() if m]
    c = {"C1": bool(all(r["dA"] < 0.02 for r in el.values())) if el else None,
         "KILL": bool(any(r["dA"] >= 0.05 for r in el.values())),
         "C2": bool(all(r["rho"] >= 0.8 for r in big)) if big else None,
         "C3": bool(np.mean([r["auc"]["T"] >= 0.9 and r["dC_over_T"] < 0.01 for r in el.values()]) >= 2 / 3) if el else None,
         "C4": bool(all(m["rho_a_agents"] < 0 and (m["median_agents_a_ge6"] or 0) <= 3 for m in ms)) if ms else None,
         "eligible_units": sorted(el)}
    c["verdict"] = "failed" if c["KILL"] else ("supported" if (c["C1"] and c["C2"] and c["C4"]) else "mixed")
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    a = ap.parse_args()
    if a.dry_run:
        w = pl.read_parquet(D / "windows.parquet")
        cls = {u: unit_cls(w.filter(pl.col("goal_no") == g)) for u, g, _ in STANDINS}
        mot = {"G51": motif_stats(pl.read_parquet(D / "motifs.parquet"))}
        print(json.dumps({"DRY_RUN_on_non_holdout_standins": {"cls": cls, "motifs": mot},
                          "criteria": evaluate(cls, mot)}, indent=1, default=float))
        return
    if not (a.confirm and a.ack):
        sys.exit("Refusing: this script reads the locked holdout. Pass --dry-run, or both --confirm and "
                 "--i-understand-this-uses-the-locked-holdout after sign-off.")
    import holdout_ledger as HL
    for u, _g, _s in HOLDOUT:
        print(u, HL.check("H80", "#51-tail" if u == "51-tail" else u, "commit-window compression; command motifs", None))
    sys.path.insert(0, str(HERE.parent / "scheme"))
    import build as B
    CONF.mkdir(parents=True, exist_ok=True)
    w = B.build_windows(periods=[46, 47, 48, 49, 50, 51], allow_holdout=True)
    w.write_parquet(CONF / "windows.parquet")
    tk = B.command_tokens(allow_holdout=True)
    cls, mot = {}, {}
    for u, g, since in HOLDOUT:
        wu = w.filter((pl.col("goal_no") == g) & (pl.col("unit") != "G51post"))
        tku = tk.filter(pl.col("goal_no") == g)
        if since:
            wu = wu.filter(pl.col("day") >= since)
            tku = tku.filter(pl.col("pt_date") >= since)
        cls[u] = unit_cls(wu)
        mot[u] = motif_stats(B.build_motifs(tku, g)[0]) if tku.height else {}
    out = {"run_at": dt.datetime.now(dt.timezone.utc).isoformat(), "predictions": PREDICTIONS, "cls": cls,
           "motifs": mot, "criteria": evaluate(cls, mot)}
    (CONF / "confirm_result.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
