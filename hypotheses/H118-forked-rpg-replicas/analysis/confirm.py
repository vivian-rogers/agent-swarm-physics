"""H118 confirmatory script (LOCKED HOLDOUT). FROZEN 2026-10-04 after exploratory round 1. NOT RUN.
DO NOT RUN without Vivian's sign-off.

Targets: held-out two-room #best/#rest periods #45, #46, #47, #50 (rooms 2 and 3; >= 3 one-room agents per room;
>= 3 days). Each kickoff restarts both rooms from one shared state (the replication design of round 1).
Primary instrument: bge_small style_resid32, leave-own-period-out regime-III reference (non-holdout, #51 excluded),
1-h active bins, agent x bin bootstrap (300). gte reported, not scored.
Frozen predictions (thresholds fixed from round 1, before any holdout data is loaded):
  C1 fast forgetting of the shared kickoff state: the equal-time memory M_late (mean M(d), d >= 2) has an
     agent x bin 95% interval covering 0 in >= FROZEN["C1_share"] of scorable targets.
  C2 the shared static overlap is goal-like: q_late of each target lies inside the frozen non-holdout band
     [min, max] of round-1 q_late over G36, G37, G39, G41, G42 (bge), widened by FROZEN["C2_margin"], in
     >= FROZEN["C2_share"] of scorable targets.
  C3 rooms are not identical replicas: q_late < the joint-relabel reference q_rel_late in >= FROZEN["C3_share"] of
     scorable targets.
Scorable = >= 3 days with usable bins and >= 3 agents per room.

Reuse disclosure (hypotheses/holdout.md): #45-#47 content is planned by H23, H26, H47, H81-H83, H100, H102, H107;
#50 by H70/H84/H87 (other modalities). H107's and H100's room-separation family is the closest (same statement
vectors, different statistic: cross-room overlap including the shared component). Disclose in both cards and LOG.md
before running; whoever runs second is the second user.

Guard: held-out data is touched only with BOTH --confirm and H118_CONFIRM=1, only if the SHA-256 of this file and its
dependencies match analysis/confirm.sha256 and the files are committed and unmodified, and only if
infra/shared/holdout_ledger.check() allows each target. --dry-run runs the same frozen pipeline on non-holdout
stand-ins (#39, #41, #42, #44), asserts that no held-out row is loaded, and writes results/confirm_dryrun.json.
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
import h118lib as L  # noqa: E402

ROOT = L.ROOT
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402
import rooms_asof  # noqa: E402

CARD = HERE.parent
FILES = ["analysis/confirm.py", "analysis/h118lib.py"]
TARGETS = [45, 46, 47, 50]
STANDIN = [39, 41, 42, 44]
FROZEN = {"C1_share": 0.75, "C2_margin": 0.05, "C2_share": 0.75, "C3_share": 0.75,
          "boot": 300, "relabel": 300, "min_days": 3, "min_room_agents": 3, "seed": 20261004}
BAND_FILE = HERE / "confirm_band.json"   # frozen round-1 band (bge q_late of G36, G37, G39, G41, G42)


def sha(f: Path) -> str:
    return hashlib.sha256(f.read_bytes()).hexdigest()


def frozen_ok() -> bool:
    rec = json.loads((HERE / "confirm.sha256").read_text())
    for f in FILES + ["analysis/confirm_band.json"]:
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


def build_period(goal: int, allow_holdout: bool, model: str = "bge_small") -> dict:
    """Statement-level period data (the scheme's rules, re-implemented here so held-out rows pass only on --confirm)."""
    st = pl.read_parquet(L.EMB / "statements.parquet").with_row_index("srow").filter(pl.col("goal_no") == goal)
    roster = pl.read_parquet(L.SH / "roster.parquet")
    st = st.filter(~pl.col("agent").is_in(roster.filter(pl.col("claude_code"))["agent"].to_list()))
    hm = np.array(holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list()))
    if not allow_holdout:
        assert not hm.any(), f"held-out row in dry run (G{goal})"
    st = rooms_asof.statement_rooms(st)
    st = st.filter(pl.col("room_at").is_in([2, 3]))
    cal = pl.read_parquet(L.SH / "calendar.parquet").select("pt_date", "win_start", "win_end", "window_s")
    st = st.join(cal, on="pt_date", how="left").with_columns(
        ((pl.col("t") - pl.col("win_start")).dt.total_seconds() / 3600).floor().clip(0, None).cast(pl.Int16).alias("hour"))
    st = st.with_columns(pl.min_horizontal(pl.col("hour"), (pl.col("window_s") / 3600).floor().cast(pl.Int16)).alias("hour"))
    days = st.select("pt_date").unique().sort("pt_date").with_row_index("day", offset=1)
    st = st.join(days, on="pt_date")
    ar = (st.group_by("agent", "room_at").len().with_columns((pl.col("len") / pl.col("len").sum().over("agent")).alias("s"))
          .sort("agent", "s", "room_at", descending=[False, True, False]).group_by("agent", maintain_order=True).first())
    keep = ar.filter(pl.col("s") >= 0.8).select("agent", pl.col("room_at").alias("rp"))
    st = st.join(keep, on="agent").filter(pl.col("room_at") == pl.col("rp")).sort("t")
    st = st.with_columns((pl.col("day").cast(pl.Int32) * 100 + pl.col("hour")).alias("bin"))
    st = st.with_columns(pl.col("t").rank("ordinal").over("agent", "bin").alias("r"), pl.len().over("agent", "bin").alias("nab"))
    st = st.with_columns(pl.when(pl.col("nab") == 1).then((pl.col("agent").cast(pl.Int32) % 2) + 1)
                         .otherwise(((pl.col("r") - 1) % 2) + 1).alias("half"))
    X = np.load(L.EMB / f"statements_style_resid32_{model}.npy", mmap_mode="r")
    allst = pl.read_parquet(L.EMB / "statements.parquet").with_row_index("srow")
    hma = holdout_mask(allst["pt_date"].to_list(), allst["goal_no"].to_list())
    ref_rows = allst.with_columns(pl.Series("hm", hma)).filter(
        ~pl.col("hm") & ~pl.col("holdout") & (pl.col("regime").cast(pl.String) == "III") & (pl.col("goal_no") != goal)
        & (pl.col("goal_no") != 51))["srow"].to_numpy()
    ref = np.asarray(X[np.sort(ref_rows)], dtype=np.float64).mean(0)
    V = np.asarray(X[st["srow"].to_numpy()], dtype=np.float64) - ref
    dd = days.join(cal, on="pt_date")
    hrs = np.floor(dd["window_s"].to_numpy() / 3600).clip(1, None)
    start = dict(zip(dd["day"].to_list(), np.concatenate([[0], np.cumsum(hrs)[:-1]]).tolist()))
    tmid = np.array([start[d] + h + 0.5 for d, h in zip(st["day"].to_list(), st["hour"].to_list())])
    return {"period": str(goal), "agent": st["agent"].to_numpy(), "room": st["room_at"].to_numpy(), "bin": st["bin"].to_numpy(),
            "half": st["half"].to_numpy(), "day": st["day"].to_numpy(), "hour": st["hour"].to_numpy(), "t": tmid, "X": V,
            "n_days": int(st["day"].max()) if st.height else 0}


def evaluate(goals, allow_holdout: bool) -> dict:
    rng = np.random.default_rng(FROZEN["seed"])
    out = {}
    for g in goals:
        p = build_period(g, allow_holdout)
        na = [len(np.unique(p["agent"][p["room"] == r])) for r in (2, 3)]
        r = L.overlap_stats(p)
        scorable = p["n_days"] >= FROZEN["min_days"] and min(na) >= FROZEN["min_room_agents"] and len(r["q_eq_d"]) >= 3
        rec = {"n_days": p["n_days"], "agents": na, "scorable": bool(scorable)}
        if scorable:
            bs = L.bootstrap(p, kind="agent_bin", B=FROZEN["boot"], rng=rng)
            rel = L.relabel_ref(p, R=FROZEN["relabel"], rng=rng)
            ft = L.fit_tau(r["t"], r["q_bin"], r["w_bin"])
            rec |= {"M_late": r["M_late"], "M_late_ci": L.ci([b["M_late"] for b in bs]), "q_late": r["q_late"],
                    "q_late_ci": L.ci([b["q_late"] for b in bs]), "q_rel_late": rel["q_rel_late"], "tau": ft["tau"]}
        out[f"G{g}"] = rec
    return out


def score(res: dict, band) -> dict:
    sc = [v for v in res.values() if v["scorable"]]
    if not sc:
        return {"C1": "void", "C2": "void", "C3": "void"}
    c1 = [v["M_late_ci"][0] <= 0 <= v["M_late_ci"][1] for v in sc]
    lo, hi = band[0] - FROZEN["C2_margin"], band[1] + FROZEN["C2_margin"]
    c2 = [lo <= v["q_late"] <= hi for v in sc]
    c3 = [v["q_late"] < v["q_rel_late"] for v in sc]
    f = lambda xs, s: "pass" if np.mean(xs) >= s else "fail"  # noqa: E731
    return {"C1": f(c1, FROZEN["C1_share"]), "C2": f(c2, FROZEN["C2_share"]), "C3": f(c3, FROZEN["C3_share"]),
            "n_scorable": len(sc)}


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    a = ap.parse_args()
    band = json.loads(BAND_FILE.read_text())["band_q_late_bge"]
    if a.confirm:
        if os.environ.get("H118_CONFIRM") != "1":
            sys.exit("refusing: set H118_CONFIRM=1 (and get Vivian's sign-off)")
        if not frozen_ok():
            sys.exit(1)
        import holdout_ledger as HL
        for g in TARGETS:
            chk = HL.check("H118", f"G{g}", "content", ["content_alignment"])
            if not chk["allowed"]:
                sys.exit(f"refused by the holdout ledger: G{g} {chk}")
            if chk.get("needs_disclosure"):
                print(f"G{g}: disclosure needed")
        res = evaluate(TARGETS, allow_holdout=True)
        out = {"mode": "CONFIRM", "frozen": FROZEN, "band": band, "results": res, "score": score(res, band)}
        path = L.DATA / "confirm" / "confirm_holdout.json"
    elif a.dry_run:
        res = evaluate(STANDIN, allow_holdout=False)
        out = {"mode": "DRY RUN on non-holdout stand-ins", "frozen": FROZEN, "band": band, "results": res,
               "score": score(res, band)}
        path = L.DATA / "confirm" / "confirm_dryrun.json"
    else:
        sys.exit("use --dry-run (non-holdout stand-ins) or --confirm with H118_CONFIRM=1")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean(out), indent=1))
    print(json.dumps(clean(out["score"]), indent=1), "->", path)


if __name__ == "__main__":
    main()
