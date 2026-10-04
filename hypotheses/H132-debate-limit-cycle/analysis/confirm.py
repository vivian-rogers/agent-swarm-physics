"""H132 confirmatory run on the LOCKED HOLDOUT (#34, saboteurs vs villagers with hidden, daily die-rolled roles).
Written and frozen 2026-10-04 after round 1; NOT RUN.

Guard: held-out rows are read only with BOTH `--confirm` and H132_CONFIRM=1, only if the SHA-256 of this file and
h132lib.py match confirm.sha256, and only if `holdout_ledger.check` allows the target. `--dry-run` runs the identical
generic pipeline on G12 (non-holdout; debates as blocks, drafted teams as sublattices) and writes to a scratch folder
whose name contains "dry".

Design (no motion text exists in #34, so the issue axis is data-driven and cross-fitted):
  sublattices  A = saboteur, B = villager (DQ6 `saboteur` rows, preferred; per agent-day; regex 'sab' -> A)
  blocks       PT days (each day re-rolls the roles)
  messages     agent chat of #34 days (shared statements_white32_bge_small; agents with a role that day)
  axis         a_d = unit(mean A vectors - mean B vectors) over the OTHER days (leave-block-out)
  turns        runs of consecutive messages from one sublattice inside a block; statistics as in round 1 (h132lib)
Frozen predictions (turn-shuffled null, 5000 draws):
  C1  HH375 as posed: Lambda = rho2 - rho1 > 0 with shuffle p_hi < 0.05. Expected to FAIL (round-1 kill).
  C2  Round-1 finding: no anti-correlation at lag 1 on the issue axis (rho1 shuffle p_lo >= 0.05).
  C3  Round-1 finding: topic echo, full-vector rho1_vec > 0 with shuffle p_hi < 0.05.
Reading: C2 + C3 confirm "turn-to-turn content persists and echoes across sides; no limit cycle".

Reuse policy: #34 was used by H05 (activity, NE12/#34 days; executed); H21 and H37 plan #34 (team recovery from
content / stance). H132's turn-alternation statistic is different; same content modality as H21: disclose.

Usage:
  uv run python hypotheses/H132-debate-limit-cycle/analysis/confirm.py --dry-run
  H132_CONFIRM=1 uv run python hypotheses/H132-debate-limit-cycle/analysis/confirm.py --confirm
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h132lib as L  # noqa: E402

ROOT = HERE.parents[2]
SH = ROOT / "data/processed/shared"
sys.path.insert(0, str(ROOT / "infra/shared"))
OUT = ROOT / "data/processed/H132-debate-limit-cycle/confirm"
SCRATCH = Path(os.environ.get("TMPDIR", "/tmp")) / "h132_confirm_dryrun"
FROZEN = {"n_perm": 5000, "alpha": 0.05, "seed": 34}
HASHED = [HERE / "confirm.py", HERE / "h132lib.py"]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def generic_turns(df: pl.DataFrame, X: np.ndarray) -> L.Turns:
    """df: block, team (+1/-1), agent, t, sorted by (block, t); X rows aligned. Leave-block-out team axis."""
    blk = df["block"].to_numpy()
    tm = df["team"].to_numpy()
    ya = np.zeros(len(df))
    for b in np.unique(blk):
        o = blk != b
        ax = X[o & (tm == 1)].mean(0) - X[o & (tm == -1)].mean(0)
        ax /= max(np.linalg.norm(ax), 1e-9)
        m = blk == b
        ya[m] = X[m] @ ax
    out = {k: [] for k in ("blk", "team", "ya", "V")}
    i, n = 0, len(df)
    while i < n:
        j = i
        while j + 1 < n and blk[j + 1] == blk[i] and tm[j + 1] == tm[i]:
            j += 1
        out["blk"].append(blk[i]); out["team"].append(tm[i]); out["ya"].append(ya[i:j + 1].mean())
        out["V"].append(X[i:j + 1].mean(0))
        i = j + 1
    bk = np.array(out["blk"])
    codes = {b: k for k, b in enumerate(sorted(set(out["blk"])))}
    z = np.zeros(len(bk))
    return L.Turns(debate=bk, phase=np.array(["blk"] * len(bk)), team=np.array(out["team"]),
                   blk=np.array([codes[b] for b in out["blk"]]), ya=np.array(out["ya"]), yg=z, V=np.vstack(out["V"]),
                   vis=np.zeros(len(bk), bool), first_agent=z, last_agent=z)


def standin():
    M = L.load("bge_small", "unmasked")
    df = M.df.filter(pl.col("phase") == "deb").sort("debate", "t").rename({"debate": "block"})
    return df.select("block", "team", "agent", "t"), M.X[df["r"].to_numpy()]


def held():
    lab = pl.read_parquet(SH / "ground_truth_labels.parquet").filter(
        (pl.col("goal_no") == 34) & (pl.col("label_kind") == "saboteur") & pl.col("preferred"))
    lab = lab.with_columns(pl.col("t_valid_from").dt.convert_time_zone("America/Los_Angeles").dt.strftime("%Y-%m-%d").alias("pt_date"),
                           pl.when(pl.col("value").str.to_lowercase().str.contains("sab")).then(1).otherwise(-1).alias("team"))
    st = (pl.scan_parquet(SH / "embeddings/statements.parquet").with_row_index("srow")
          .filter((pl.col("kind") == "chat") & (pl.col("goal_no") == 34)).collect())
    df = st.join(lab.select("agent", "pt_date", "team"), on=["agent", "pt_date"], how="inner").sort("pt_date", "t")
    V = np.load(SH / "embeddings/statements_white32_bge_small.npy", mmap_mode="r")
    X = np.asarray(V[df["srow"].to_numpy()], dtype=np.float64)
    return df.rename({"pt_date": "block"}).select("block", "team", "agent", "t"), X


def score(res: dict) -> dict:
    return {"C1_hh_as_posed": bool(res["Lam"]["p_hi"] < FROZEN["alpha"]),
            "C2_no_lag1_anticorrelation": bool(res["rho1"]["p_lo"] >= FROZEN["alpha"]),
            "C3_topic_echo": bool(res["rho1_vec"]["p_hi"] < FROZEN["alpha"]),
            "round1_claim_confirmed": bool(res["rho1"]["p_lo"] >= FROZEN["alpha"] and res["rho1_vec"]["p_hi"] < FROZEN["alpha"])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.confirm == a.dry_run:
        sys.exit("choose exactly one of --confirm / --dry-run")
    if a.confirm:
        if os.environ.get("H132_CONFIRM") != "1":
            sys.exit("refused: set H132_CONFIRM=1 (Vivian's sign-off) to touch the locked holdout")
        ref = json.loads((HERE / "confirm.sha256").read_text())
        for p in HASHED:
            if ref.get(p.name) != sha(p):
                sys.exit(f"refused: {p.name} changed since the freeze")
        import holdout_ledger as HL
        chk = HL.check("H132", "G34", "message content", ["content_alignment"])
        if not chk["allowed"]:
            sys.exit(f"refused by the holdout ledger: {chk}")
        if chk["needs_disclosure"]:
            print("disclosure needed:", sorted({u["hypothesis"] for u in chk["competing_planned"] + chk["prior_runs"]}))
        df, X, root = *held(), OUT
    else:
        df, X, root = *standin(), SCRATCH
    T = generic_turns(df, X)
    r = L.shuffle_test(T, FROZEN["n_perm"], seed=FROZEN["seed"], keys=("rho1", "rho2", "Lam", "A", "rho1_vec"))
    res = {"mode": "confirm" if a.confirm else "dry-run", "frozen": FROZEN, "n_turns": int(len(T.ya)),
           "script_sha": {p.name: sha(p)[:12] for p in HASHED},
           "result": {k: r[k] for k in ("rho1", "rho2", "Lam", "A", "rho1_vec") if k in r}, "score": score(r)}
    root.mkdir(parents=True, exist_ok=True)
    (root / ("confirm_result.json" if a.confirm else "dryrun_result.json")).write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
