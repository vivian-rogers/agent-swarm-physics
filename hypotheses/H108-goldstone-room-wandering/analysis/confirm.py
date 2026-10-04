"""H108 confirmatory script (LOCKED HOLDOUT). FROZEN 2026-10-04 after exploratory round 1. NOT RUN.
DO NOT RUN without Vivian's sign-off.

Frozen predictions (thresholds fixed from round 1, before any holdout data is loaded). Targets: held-out two-room
#best/#rest periods among #45-#48 with >= 3 one-room agents per room (>= 2 days) and >= 3 regime-III days ("scorable").
Primary instrument: bge_small style_resid daily agent vectors, day-centred, leave-period-out constants removed;
noise-corrected persistence P(1) (lag-1 ratio of sums of joint-relabel excess cross-products, 2000 relabels).
  C1 persistence: P(1) >= 0.6 in >= 2/3 of scorable periods; void if none.                                      [0.65]
  C2 field contrast: pooled P(1) of scorable room-kickoff periods (whitened kickoff cos < 0.95) > pooled P(1) of
     scorable identical-kickoff periods; void if either kind is absent.                                          [0.55]
  C3 no mechanical rotation: pooled P(1) over all scorable periods >= 0.5; void if none.                         [0.7]

Reuse disclosure (hypotheses/holdout.md): #45-#48 content is planned by H23, H26, H47, H81-H83, H100, H102 and H107;
H100's C2/C4, H102's C1 and H107's C1-C4 use the same #best/#rest separation family. Disclose in both cards and
LOG.md before running.

Guard: held-out data is touched only with BOTH --confirm and H108_CONFIRM=1, only if the SHA-256 of this file and its
dependencies match analysis/confirm.sha256 and the files are committed and unmodified, and only if
infra/shared/holdout_ledger.check() allows each target. --dry-run applies the same frozen pipeline to non-holdout
stand-ins (#37, #41, #42, #44), asserts that no held-out row is loaded, and writes confirm/confirm_dryrun.json.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h108lib as L  # noqa: E402
import rslib as R  # noqa: E402

ROOT = R.ROOT
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402
from embed_models import load_whitener  # noqa: E402

FILES = ["analysis/confirm.py", "analysis/rslib.py", "analysis/h108lib.py", "scheme/build.py"]
CARD = HERE.parent
TARGETS = [45, 46, 47, 48]
STANDIN = [37, 41, 42, 44]
FROZEN = {"C1_P1_min": 0.6, "C1_share": 2 / 3, "C3_P1_min": 0.5, "kick_cos": 0.95, "n_perm": 2000, "min_days": 3,
          "min_room": 3}


def sha(f: Path) -> str:
    return hashlib.sha256(f.read_bytes()).hexdigest()


def frozen_ok() -> bool:
    rec = json.loads((HERE / "confirm.sha256").read_text())
    for f in FILES:
        if rec.get(f) != sha(CARD / f):
            print(f"refusing: {f} does not match its frozen SHA-256", file=sys.stderr)
            return False
        rel = str((CARD / f).relative_to(ROOT))
        tracked = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--error-unmatch", rel], capture_output=True).returncode == 0
        dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", rel], capture_output=True, text=True).stdout.strip()
        if not tracked or dirty:
            print(f"refusing: {rel} is untracked or modified", file=sys.stderr)
            return False
    return True


def scheme():
    spec = importlib.util.spec_from_file_location("h108build", CARD / "scheme/build.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def kickoff_cos(P: int, allow) -> float:
    g = pl.read_parquet(R.ED / "goals.parquet").with_columns(pl.col("kind").cast(pl.String))
    k = g.filter((pl.col("kind") == "kickoff_room") & (pl.col("goal_no") == P) & pl.col("room").is_in([R.BEST, R.REST])
                 & (~pl.col("holdout") | pl.col("goal_no").is_in(list(allow))))
    if k.height < 2:
        return 1.0
    gv = np.load(R.ED / "goal_vectors.npy").astype(np.float32)
    W = load_whitener("III", 32, "bge_small")
    v = [W(gv[r][None])[0] for r in k.sort("room")["gid"].to_list()[:2]]
    return float(v[0] @ v[1] / np.linalg.norm(v[0]) / np.linalg.norm(v[1]))


def evaluate(periods, allow=()):
    b = scheme()
    roster = pl.read_parquet(ROOT / "data/processed/shared/roster.parquet")
    cc = roster.filter(pl.col("claude_code"))["agent"].to_list()
    st = b.build_statements(cc, allow_holdout_goals=allow, goals=sorted(set(list(range(33, 52)) + list(allow))))
    if not allow:
        assert not any(holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list())), "held-out row in dry run"
    out = {}
    for model in ("bge_small", "gte_modernbert"):
        V = R.load_vectors(model, "style_resid")
        ad, Xc = R.day_centered_agent_days(st, V, R.REG3)
        res = {}
        for P in periods:
            consts = R.constants(ad, Xc, exclude={P})
            pan = R.build_panel(st, V, P, "day", consts, halves=True)
            ok = len(pan.bins) >= FROZEN["min_days"] and min(pan.info["n_best"], pan.info["n_rest"]) >= FROZEN["min_room"]
            if not ok:
                res[P] = {"scorable": False}; continue
            s = L.sums(pan, n_perm=FROZEN["n_perm"], seed=P, max_lag=1)
            res[P] = {"scorable": True, "sums": s, "P1": L.P_from(s), "kickoff_cos": kickoff_cos(P, allow)}
        out[model] = res
    return out


def score(res: dict) -> dict:
    r = res["bge_small"]
    sc = [P for P, x in r.items() if x.get("scorable")]
    c1 = [np.isfinite(r[P]["P1"]) and r[P]["P1"] >= FROZEN["C1_P1_min"] for P in sc]
    fld = [P for P in sc if r[P]["kickoff_cos"] < FROZEN["kick_cos"]]
    idn = [P for P in sc if r[P]["kickoff_cos"] >= FROZEN["kick_cos"]]
    pf = L.pooled_P([r[P]["sums"] for P in fld]) if fld else np.nan
    pi = L.pooled_P([r[P]["sums"] for P in idn]) if idn else np.nan
    pall = L.pooled_P([r[P]["sums"] for P in sc]) if sc else np.nan
    return {"C1": "void" if not sc else ("pass" if np.mean(c1) >= FROZEN["C1_share"] else "fail"),
            "C1_detail": {str(P): float(r[P]["P1"]) for P in sc},
            "C2": "void" if not (fld and idn) else ("pass" if pf > pi else "fail"), "C2_detail": {"fielded": pf, "identical": pi},
            "C3": "void" if not sc else ("pass" if pall >= FROZEN["C3_P1_min"] else "fail"), "C3_detail": pall}


def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, np.integer, np.bool_)):
        o = o.item()
    if isinstance(o, float) and not np.isfinite(o):
        return None
    return o


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    a = ap.parse_args()
    if a.confirm:
        if os.environ.get("H108_CONFIRM") != "1":
            sys.exit("refusing: set H108_CONFIRM=1 (and get Vivian's sign-off)")
        if not frozen_ok():
            sys.exit(1)
        import holdout_ledger as HL
        for P in TARGETS:
            chk = HL.check("H108", f"G{P}", "content", ["content_alignment"])
            if not chk["allowed"]:
                sys.exit(f"refused by the holdout ledger: G{P} {chk}")
            if chk["needs_disclosure"]:
                print(f"G{P}: disclosure needed ({len(chk['competing_planned'])} planned users)")
        res = evaluate(TARGETS, allow=tuple(TARGETS))
        out = {"mode": "CONFIRM", "frozen": FROZEN, "results": res, "score": score(res)}
        path = L.DATA / "confirm" / "confirm_holdout.json"
    elif a.dry_run:
        res = evaluate(STANDIN)
        out = {"mode": "DRY RUN on non-holdout stand-ins", "frozen": FROZEN, "results": res, "score": score(res)}
        path = L.DATA / "confirm" / "confirm_dryrun.json"
    else:
        sys.exit("use --dry-run (non-holdout stand-ins) or --confirm with H108_CONFIRM=1")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean(out), indent=1))
    print(json.dumps(clean(out["score"]), indent=1), "->", path)


if __name__ == "__main__":
    main()
