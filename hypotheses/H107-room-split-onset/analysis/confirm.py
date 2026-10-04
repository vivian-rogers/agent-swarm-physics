"""H107 confirmatory script (LOCKED HOLDOUT). FROZEN 2026-10-04 after exploratory round 1. NOT RUN.
DO NOT RUN without Vivian's sign-off.

Frozen predictions (thresholds fixed from round 1, before any holdout data is loaded). Targets: held-out two-room
#best/#rest periods among #45-#48 with >= 3 one-room agents per room (>= 2 days) and >= 3 regime-III days.
Primary instrument: bge_small style_resid, bin-centred, agent constants removed (P and P- left out); gte reported.
  C1 no hidden-field step: among scorable identical-kickoff periods (final split E_F joint-relabel p < 0.05;
     whitened room-kickoff cos >= 0.95), the HH337 onset kill (r1 >= 0.8 and c1 >= 0.7) fires in <= 1/3;
     void if none is scorable.                                                                                    [0.7]
  C2 day 1 is a transient: among scorable identical-kickoff periods (whitened room-kickoff cos >= 0.95) with day-1
     E relabel p < 0.2, c1 < 0.7 in >= 2/3; void if none qualifies.                                             [0.6]
  C3 repos rarely set the week: period-level f_repo >= 0.15 with direction-null p < 0.05 in <= 1/3 of the periods
     with a defined inherited repo field; void if none has one.                                                  [0.7]
  C4 reshuffle onset (the G39 analog): in scorable identical-kickoff periods that open with an operator move (>= 1 eligible agent in a
     different room than in P-, with both rooms of P- holding >= 3 eligible agents; NE19 opens #45), r1 <= 0.3.
     Pass if all such periods meet it; void if none.                                                             [0.4]

Reuse disclosure (hypotheses/holdout.md): #45-#48 content is planned by H23, H26, H47, H81-H83, H100 and H102; NE19
(#45) is H23's, H65's and H100's target. H100's C2/C4 and H102's C1 use the same #best/#rest separation family.
Disclose in both cards and LOG.md before running; whoever runs second is the second user.

Guard: held-out data is touched only with BOTH --confirm and the environment variable H107_CONFIRM=1, only if the
SHA-256 of this file and its dependencies match analysis/confirm.sha256 and the files are committed and unmodified,
and only if infra/shared/holdout_ledger.check() allows each target. --dry-run applies the same frozen pipeline to
non-holdout stand-ins (#39, #41, #42, #44), asserts that no held-out row is loaded, and writes
results/confirm_dryrun.json.
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
import h107lib as L  # noqa: E402
import rslib as R  # noqa: E402

ROOT = R.ROOT
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402
from embed_models import load_whitener  # noqa: E402

FILES = ["analysis/confirm.py", "analysis/rslib.py", "analysis/h107lib.py", "scheme/build.py"]
CARD = HERE.parent
TARGETS = [45, 46, 47, 48]
PRE_HELD = {45: 44, 46: 45, 47: 46, 48: 47}
STANDIN = [39, 41, 42, 44]
FROZEN = {"C1_kill_share_max": 1 / 3, "C4_r1_max": 0.3, "C2_c1_max": 0.7, "C2_p1_max": 0.2,
          "C2_share": 2 / 3, "C3_share_max": 1 / 3, "kick_cos": 0.95, "n_perm": 2000, "min_days": 3, "min_room": 3}


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
    spec = importlib.util.spec_from_file_location("h107build", CARD / "scheme/build.py")
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


def evaluate(periods, pre: dict, allow=()):
    b = scheme()
    roster = pl.read_parquet(R.ROOT / "data/processed/shared/roster.parquet")
    cc = roster.filter(pl.col("claude_code"))["agent"].to_list()
    goals = sorted(set(list(range(33, 52)) + list(allow)))
    st = b.build_statements(cc, allow_holdout_goals=allow, goals=goals)
    if not allow:
        assert not any(holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list())), "held-out row in dry run"
    rm = b.build_repo_mentions(st); arp = b.build_agent_repo(allow_holdout_goals=allow)
    R.PRE.update(pre)
    out = {}
    for model in ("bge_small", "gte_modernbert"):
        V = R.load_vectors(model, "style_resid")
        ad, Xc = R.day_centered_agent_days(st, V, R.REG3 + [33, 35])
        res = {}
        for P in periods:
            consts = R.constants(ad, Xc, exclude={P, pre[P]})
            pday = R.build_panel(st, V, P, "day", consts, halves=True)
            if len(pday.bins) < FROZEN["min_days"] or min(pday.info["n_best"], pday.info["n_rest"]) < FROZEN["min_room"]:
                res[P] = {"scorable": False, "reason": "size"}; continue
            phalf = R.build_panel(st, V, P, "half", consts)
            o = L.onset(pday, phalf, n_perm=FROZEN["n_perm"], seed=P)
            prev = R.build_panel(st, V, pre[P], "day", None)
            lab_prev = {int(a): int(r) for a, r in zip(prev.agents, prev.lab)}
            moved = [int(a) for a, r in zip(pday.agents, pday.lab) if int(a) in lab_prev and lab_prev[int(a)] != int(r)]
            two_room_prev = min(int((prev.lab == R.BEST).sum()), int((prev.lab == R.REST).sum())) >= 3
            reshuffle = bool(moved) and two_room_prev
            u, info = L.inherited_repo_field(st, V, rm, arp, P, pday.agents, pday.lab)
            fa = L.field_alignment(pday, u, n_null=2000, seed=P + 1) if u is not None else None
            res[P] = {"scorable": bool(o["p_F"] < 0.05), "r1": o["r1"], "c1": o["c1"], "p1": o["p1"], "p_F": o["p_F"],
                      "pi1": o["pi1"], "kill": o["kill_onset"], "reshuffle": reshuffle, "n_moved": len(moved),
                      "kickoff_cos": kickoff_cos(P, allow), "repo": fa, "repo_info": info}
        out[model] = res
    return out


def score(res: dict) -> dict:
    r = res["bge_small"]
    sc = [P for P, x in r.items() if x.get("scorable")]
    q1 = [P for P in sc if r[P]["kickoff_cos"] >= FROZEN["kick_cos"]]
    c1 = [bool(r[P]["kill"]) for P in q1]
    q4 = [P for P in sc if r[P]["reshuffle"] and r[P]["kickoff_cos"] >= FROZEN["kick_cos"]]
    c4 = [r[P]["r1"] <= FROZEN["C4_r1_max"] for P in q4]
    q2 = [P for P in sc if r[P]["kickoff_cos"] >= FROZEN["kick_cos"] and r[P]["p1"] < FROZEN["C2_p1_max"]
          and r[P]["c1"] is not None and np.isfinite(r[P]["c1"])]
    c2 = [r[P]["c1"] < FROZEN["C2_c1_max"] for P in q2]
    q3 = [P for P, x in r.items() if x.get("repo")]
    c3 = [bool(r[P]["repo"]["rule_period"]) for P in q3]
    v = lambda ok, n, share, le=False: ("void" if n == 0 else ("pass" if ((ok / n <= share) if le else (ok / n >= share)) else "fail"))  # noqa: E731
    return {"C1": v(sum(c1), len(c1), FROZEN["C1_kill_share_max"], le=True), "C1_detail": dict(zip(map(str, q1), c1)),
            "C4": ("void" if not q4 else ("pass" if all(c4) else "fail")), "C4_detail": dict(zip(map(str, q4), c4)),
            "C2": v(sum(c2), len(c2), FROZEN["C2_share"]), "C2_detail": dict(zip(map(str, q2), c2)),
            "C3": v(sum(c3), len(c3), FROZEN["C3_share_max"], le=True), "C3_detail": dict(zip(map(str, q3), c3))}


def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, np.integer, np.bool_)):
        return o.item()
    if isinstance(o, float) and not np.isfinite(o):
        return None
    return o


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    a = ap.parse_args()
    if a.confirm:
        if os.environ.get("H107_CONFIRM") != "1":
            sys.exit("refusing: set H107_CONFIRM=1 (and get Vivian's sign-off)")
        if not frozen_ok():
            sys.exit(1)
        import holdout_ledger as HL
        for P in TARGETS:
            chk = HL.check("H107", f"G{P}", "content", ["content_alignment"])
            if not chk["allowed"]:
                sys.exit(f"refused by the holdout ledger: G{P} {chk}")
            if chk["needs_disclosure"]:
                print(f"G{P}: disclosure needed ({len(chk['competing_planned'])} planned users)")
        res = evaluate(TARGETS, PRE_HELD, allow=tuple(TARGETS))
        out = {"mode": "CONFIRM", "frozen": FROZEN, "results": res, "score": score(res)}
        path = L.DATA / "confirm" / "confirm_holdout.json"
    elif a.dry_run:
        pre = {P: R.PRE[P] for P in STANDIN}
        res = evaluate(STANDIN, pre)
        out = {"mode": "DRY RUN on non-holdout stand-ins", "frozen": FROZEN, "results": res, "score": score(res)}
        path = L.DATA / "confirm" / "confirm_dryrun.json"
    else:
        sys.exit("use --dry-run (non-holdout stand-ins) or --confirm with H107_CONFIRM=1")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean(out), indent=1))
    print(json.dumps(clean(out["score"]), indent=1), "->", path)


if __name__ == "__main__":
    main()
