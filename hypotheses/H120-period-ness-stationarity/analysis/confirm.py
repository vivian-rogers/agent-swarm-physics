"""H120 confirmatory script (LOCKED HOLDOUT). FROZEN 2026-10-04 after exploratory round 1. NOT RUN.
DO NOT RUN without Vivian's sign-off.

Targets (held-out windows with >= 10 days):
  T51  the #51 tail, 2026-09-07 -> 09-18 (NE window "#51 tail"; regime III; core agents present on >= 90% of days);
  T1a  unit 1a, 2025-04-02 -> 04-14 (goal #1, held out; regime I; 4 agents).
Same frozen pipeline as round 1 (h120lib: kinetic Ising with weekday and session-length fields, ridge 1 on J; score
tests on (h, J) for the contiguous split (T1) and a linear trend (T2), 1000 permutations each; Holm over the four tests
(2 channels x T1, T2) within a target).
Frozen predictions (round 1: every regime-III window of >= 13 days drifted, R_split 1.5-2.2; the 8-day unit 38a did not):
  C1 the #51 tail drifts: T1 or T2 rejects at Holm 0.05 in the activity channel.                               [0.4]
  C2 the #51 tail's activity drift ratio R_split >= 1.3.                                                        [0.4]
     (Credences lowered after the dry run: the last 10 non-holdout #51 days, 08-24 -> 09-04, gave activity R 1.12,
     Holm 0.18, talk trend Holm 0.04; thresholds unchanged.)
  C3 1a (regime I, 4 agents): no test rejects at Holm 0.05 (regime-I 4-agent units drifted in 1/3 in round 1,
     talk only); reported with the round-1 synthetic power caveat (power < 0.8 at 4 agents).                    [0.5]

Reuse disclosure (hypotheses/holdout.md): the #51 tail is planned by many cards (activity families H02/H12/H19/H25/H38
equal-time gains; H90 EP; H72 behavior states). H120's statistic is a drift score of a kinetic Ising fit, a different
statistic from the equal-time gains; the activity modality overlaps. Disclose in both cards and LOG.md before running.

Guard: held-out data is touched only with BOTH --confirm and H120_CONFIRM=1, only if the SHA-256 of this file and its
dependencies match analysis/confirm.sha256 and the files are committed and unmodified, and only if
infra/shared/holdout_ledger.check() allows each target. --dry-run runs the same frozen pipeline on non-holdout
stand-ins (the last 10 days of 51main; unit 27), asserts that no held-out row is loaded, and writes
results/confirm_dryrun.json.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h120lib as L  # noqa: E402

ROOT = L.ROOT
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402
from nulls import all_present_window  # noqa: E402

CARD = HERE.parent
FILES = ["analysis/confirm.py", "analysis/h120lib.py"]
SH = ROOT / "data/processed/shared"
FROZEN = {"perm": 1000, "core_share": 0.9, "C2_R_min": 1.3, "alpha": 0.05, "seed": 20261004, "min_trim_min": 30}
TARGETS = {"T51": ("2026-09-07", "2026-09-18", 51), "T1a": ("2025-04-02", "2025-04-14", 1)}


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


def build_window(days, goal, allow_holdout: bool) -> dict:
    """The scheme's rules (core >= 90% of days, all-present trim over the core), re-implemented for held-out days."""
    hm = holdout_mask(days, [goal] * len(days))
    if not allow_holdout:
        assert not any(hm), "held-out day in dry run"
    ab = pl.scan_parquet(SH / "activity_bins_fixed.parquet").filter(pl.col("pt_date").is_in(days)).collect()
    cal = pl.read_parquet(SH / "calendar.parquet")
    rec = ab.filter(pl.col("state") >= 2).group_by("agent").agg(pl.col("pt_date").n_unique().alias("nd"))
    core = sorted(rec.filter(pl.col("nd") >= FROZEN["core_share"] * len(days))["agent"].to_list())
    wdm = dict(zip(cal["pt_date"].to_list(), cal["weekday"].to_list()))
    S = {"act": [], "talk": []}
    kept, wd, tl = [], [], []
    for d in days:
        x = ab.filter((pl.col("pt_date") == d) & pl.col("agent").is_in(core))
        if set(core) - set(x.filter(pl.col("state") >= 2)["agent"].unique().to_list()):
            continue
        T = int(x["minute"].max()) + 1
        st = np.ones((T, len(core)), np.int8)
        tk = np.zeros((T, len(core)), np.int16)
        ai = {a: i for i, a in enumerate(core)}
        st[x["minute"].to_numpy(), [ai[a] for a in x["agent"].to_list()]] = x["state"].to_numpy()
        tk[x["minute"].to_numpy(), [ai[a] for a in x["agent"].to_list()]] = x["talk"].to_numpy()
        pres = np.zeros(st.shape, bool)
        for j in range(len(core)):
            idx = np.flatnonzero(st[:, j] >= 2)
            pres[idx[0]: idx[-1] + 1, j] = True
        trim = np.flatnonzero(all_present_window(pres))
        if len(trim) < FROZEN["min_trim_min"]:
            continue
        S["act"].append((st[trim] >= 3).astype(float))
        S["talk"].append((tk[trim] > 0).astype(float))
        kept.append(d)
        wd.append(wdm[d])
        tl.append(len(trim))
    return {"days": kept, "core": core, "S": S, "weekday": np.array(wd), "trim_len": np.array(tl, float)}


def evaluate(windows: dict, allow_holdout: bool) -> dict:
    rng = np.random.default_rng(FROZEN["seed"])
    out = {}
    for name, (days, goal) in windows.items():
        w = build_window(days, goal, allow_holdout)
        rec = {"n_days": len(w["days"]), "n_core": len(w["core"])}
        ps = []
        for ch in ("act", "talk"):
            win = {"name": name, "channel": ch, "days": w["days"], "core": w["core"], "S": w["S"][ch],
                   "weekday": w["weekday"], "trim_len": w["trim_len"]}
            des = L.design(win)
            F = L.fit(des)
            n = len(des["days"])
            t1 = L.perm_test(F, L.contiguous_tau(n), L.random_splits(n, FROZEN["perm"], rng))
            t2 = L.perm_test(F, L.trend_tau(n), [L.trend_tau(n)[rng.permutation(n)] for _ in range(FROZEN["perm"])])
            rec[ch] = {"T1_R": t1["R"], "T1_p": t1["p"], "T2_R": t2["R"], "T2_p": t2["p"]}
            ps += [t1["p"], t2["p"]]
        rec["holm"] = dict(zip(["act_T1", "act_T2", "talk_T1", "talk_T2"], L.holm(ps).tolist()))
        out[name] = rec
    return out


def score(res: dict, t51: str, t1a: str) -> dict:
    a = FROZEN["alpha"]
    r51, r1 = res[t51], res[t1a]
    c1 = "pass" if min(r51["holm"]["act_T1"], r51["holm"]["act_T2"]) < a else "fail"
    c2 = "pass" if r51["act"]["T1_R"] >= FROZEN["C2_R_min"] else "fail"
    c3 = "pass" if min(r1["holm"].values()) >= a else "fail"
    return {"C1": c1, "C2": c2, "C3": c3}


def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, np.integer)):
        o = o.item()
    if isinstance(o, float) and not np.isfinite(o):
        return None
    return o


def days_between(a, b):
    cal = pl.read_parquet(SH / "calendar.parquet")
    return sorted(cal.filter(pl.col("pt_date").is_between(pl.lit(a), pl.lit(b)))["pt_date"].to_list())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    a = ap.parse_args()
    if a.confirm:
        if os.environ.get("H120_CONFIRM") != "1":
            sys.exit("refusing: set H120_CONFIRM=1 (and get Vivian's sign-off)")
        if not frozen_ok():
            sys.exit(1)
        import holdout_ledger as HL
        for tgt, unit in (("T51", "#51-tail"), ("T1a", "G01")):
            chk = HL.check("H120", unit, "activity", ["kinetic_ising_couplings"])
            if not chk["allowed"]:
                sys.exit(f"refused by the holdout ledger: {unit} {chk}")
        wins = {k: (days_between(s, e), g) for k, (s, e, g) in TARGETS.items()}
        res = evaluate(wins, allow_holdout=True)
        out = {"mode": "CONFIRM", "frozen": FROZEN, "results": res, "score": score(res, "T51", "T1a")}
        path = L.DATA / "confirm" / "confirm_holdout.json"
    elif a.dry_run:
        main_days = days_between("2026-07-10", "2026-09-04")
        cal = pl.read_parquet(SH / "calendar.parquet")
        nh = set(cal.filter(~pl.col("holdout"))["pt_date"].to_list())
        stand = {"S51": ([d for d in main_days if d in nh][-10:], 51),
                 "S27": (days_between("2026-01-12", "2026-01-23"), 27)}
        res = evaluate(stand, allow_holdout=False)
        out = {"mode": "DRY RUN on non-holdout stand-ins", "frozen": FROZEN, "results": res, "score": score(res, "S51", "S27")}
        path = L.DATA / "confirm" / "confirm_dryrun.json"
    else:
        sys.exit("use --dry-run (non-holdout stand-ins) or --confirm with H120_CONFIRM=1")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean(out), indent=1))
    print(json.dumps(clean(out["score"]), indent=1), "->", path)


if __name__ == "__main__":
    main()
