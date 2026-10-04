"""H11 confirmatory test on the LOCKED HOLDOUT -- ROUND-1B RE-FREEZE of `confirm_holdout.py`. Written 2026-10-04 after
round 1b, before any holdout data was read. NOT RUN. `confirm_holdout.py` stays byte-for-byte unchanged; its frozen
rules (FROZEN dict, verdict(), run_target()) are imported, not copied.

Targets and stand-ins: unchanged (#22 FM-free, #28 AF, #45 AF; dry-run stand-ins #31, #25, #38).

Input switches (round 1b):
  * attention (project) labels from the shared, deterministic `project_states` (W = 30, sources = all; exact ties to the
    earliest first-seen project, then the name), not H11's own files (whose modal() broke ties nondeterministically;
    infra Known issues). Held-out periods are labelled on their own rows (project_states' rule for fully held-out
    periods), exactly as build_r1b does for exploratory periods;
  * action-class labels with the shared deterministic tie-break (build_r1b.build_action);
  * NEW work-ledger state (DQ4 `work_commits`: canonical & ~imported & author_kind == agent & ~automated, author time):
    the repo with the most agent work commits per agent-window (build_r1b.build_work), for C4-r1b.
  activity_bins, embeddings, context-ledger visibility, failures and nudge targets are not inputs of this design.
  The labels are built in memory by functions of scheme/build_r1b.py (holdout rows admitted only under --confirm) and
  written to data/processed/H11-potts-labor-vs-herding/confirm_r1b[_dryrun]/G<NN>/ in the round-1b layout.

Predictions: C1, C2, C3 exactly as frozen in confirm_holdout.py (FROZEN, verdict(), overall()).
  DISCLOSURE (holdout ledger item 11, round 1b): #35 contradicts C2's frozen clause in exploration (a shared-artifact
  week, ownership 0.01, with z_N2(attention) = -2.5). C2 is kept as frozen; a C2 refutation on the holdout would agree
  with #35. Monte Carlo note: z_N2 moves by up to ~0.5 near z = 2 between null seeds with 99 nulls (round 1b); the
  frozen n_null = 199 is kept.
  C4-r1b (NEW, from round-1b R1b-2a/c, written before any holdout read): work-space herding follows ownership, on the
  targets with >= 15 room blocks of >= 3 work-labelled agents at W = 30 (in practice #45; regime-I #22/#28 have too few
  commits): work ownership < 0.5 -> betaJ_CW(work) > 0 with |t| > t_crit AND z_N2(work) >= 2; ownership >= 0.5 ->
  z_N2(work) < 2. Exploration: 4/6 shared weeks herd in work (a), 3/3 own-artifact weeks spread (c). Reported per
  target; "n/a" when the minimum-data rule fails.

Holdout reuse (infra/shared/holdout_ledger.check() before any confirm build): H02 (#45 activity couplings) and H04
(#45 kernels) ran in another modality; planned project/herding users of #45: H01 (crews), H27, H28; work-output users
H01, H15, H33. #22 and #28 have no executed run. Disclose in both cards and LOG.md.

Usage
  uv run python hypotheses/H11-potts-labor-vs-herding/analysis/confirm_r1b.py --dry-run
  uv run python hypotheses/H11-potts-labor-vs-herding/analysis/confirm_r1b.py --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2"
os.environ.setdefault("POLARS_MAX_THREADS", "2")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import h11common as HC  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import build_r1b as BR  # noqa: E402  (shared label builders; main() is not called)
import confirm_holdout as CH  # noqa: E402  (frozen FROZEN / run_target / verdict / overall)
import potts_core as P  # noqa: E402
from h11data import load_period, blocks_ge  # noqa: E402

PS = BR.PS
TARGETS = CH.TARGETS
STANDINS = CH.STANDINS
W = CH.FROZEN["W"]
LEDGER_TARGETS = {22: "G22", 28: "G28", 45: "G45"}


def ledger_checks():
    sys.path.insert(0, str(HC.ROOT / "infra/shared"))
    import holdout_ledger as HL
    out = {}
    for g, t in LEDGER_TARGETS.items():
        c = HL.check("H11", t, "artifacts", ["project_potts", "work_output"])
        out[t] = {"allowed": c["allowed"], "needs_disclosure": c["needs_disclosure"],
                  "prior_runs": sorted({u["hypothesis"] for u in c["prior_runs"]}),
                  "prior_runs_same_family": sorted({u["hypothesis"] for u in c["prior_runs_same_family"]}),
                  "competing_planned": sorted({u["hypothesis"] for u in c["competing_planned"]})}
    return out


def shared_labels_any(cal: pl.DataFrame, sources: str, allow_holdout: bool) -> pl.DataFrame:
    """build_r1b.shared_labels with held-out rows admitted only when allow_holdout (the --confirm path)."""
    ps = pl.scan_parquet(BR.SHARED / "project_states.parquet").filter(
        (pl.col("w_min") == W) & (pl.col("sources").cast(pl.String) == sources)
        & (pl.lit(True) if allow_holdout else ~pl.col("holdout"))).collect()
    ps = ps.drop("day").join(cal.select("pt_date", "goal_no", "day"), on=["pt_date", "goal_no"], how="inner")
    return ps.select(pl.col("goal_no").cast(pl.Int8), "pt_date", "day", "win", "agent", pl.col("project").cast(pl.String),
                     pl.col("n").cast(pl.UInt32), pl.col("n_all").cast(pl.UInt32), "n_tied", "room", "label")


def build_labels(goals: list[int], out: Path, allow_holdout: bool) -> dict:
    cal = PS.load_calendar(goals, allow_holdout=allow_holdout)
    if not allow_holdout:
        assert not cal["ho"].any(), "dry run touched held-out days"
    wins = PS.window_table(cal, W)
    lp = shared_labels_any(cal, "all", allow_holdout)
    la = BR.build_action(cal, W, wins)
    lw, _pw = PS.label_projects(BR.build_work(cal, W, wins))
    rows = {}
    for g in goals:
        f = out / f"G{g:02d}"
        f.mkdir(parents=True, exist_ok=True)
        lp.filter(pl.col("goal_no") == g).sort("day", "win", "agent").write_parquet(f / f"labels_project_w{W}.parquet")
        la.filter(pl.col("goal_no") == g).sort("day", "win", "agent").write_parquet(f / f"labels_action_w{W}.parquet")
        lw.filter(pl.col("goal_no") == g).sort("day", "win", "agent").write_parquet(f / f"labels_work_w{W}.parquet")
        wins.filter(pl.col("goal_no") == g).write_parquet(f / f"windows_w{W}.parquet")
        rows[g] = {"project_rows": lp.filter(pl.col("goal_no") == g).height}
    return rows


def run_work(g, base, n_null, rng):
    """C4-r1b statistics on the work state (same estimators and null construction as run_target)."""
    s, df = load_period(g, state="work", base=base)
    out = dict(goal=g, n_obs=int(len(s.label)), blocks3=blocks_ge(s, 3))
    if out["blocks3"] < CH.FROZEN["min_blocks3"]:
        out["tested"] = False
        return out
    out["tested"] = True
    from scipy import stats
    full, se, jk = P.jackknife_cw(s, "period")
    t = full["bj"] / se if se and se > 0 else np.nan
    out.update(bj_cw=full["bj"], t_cw=t, tcrit=float(stats.t.ppf(0.975, max(len(jk) - 1, 1))))
    bj_pl = P.fit_pl(s, "agent")["bj"]
    n2 = np.array([P.fit_pl(P.shift_snap(s, rng), "agent")["bj"] for _ in range(n_null)])
    out.update(bj_pl=bj_pl, z_pl_N2=float((bj_pl - n2.mean()) / n2.std(ddof=1)), ownership=CH.ownership(df))
    sig = bool(np.isfinite(t) and abs(t) > out["tcrit"])
    if out["ownership"] < CH.FROZEN["own_threshold"]:
        out["C4_pass"] = bool(full["bj"] > 0 and sig and out["z_pl_N2"] >= 2)
    else:
        out["C4_pass"] = bool(out["z_pl_N2"] < 2)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    a = ap.parse_args()
    if a.confirm and not a.ack:
        raise SystemExit("refusing: --confirm also needs --i-understand-this-uses-the-locked-holdout")
    if a.dry_run and a.confirm:
        raise SystemExit("choose either --dry-run or --confirm, not both")
    if not a.dry_run and not (a.confirm and a.ack):
        raise SystemExit("refusing: pass --dry-run (non-holdout stand-ins) or "
                         "--confirm --i-understand-this-uses-the-locked-holdout (locked holdout; needs sign-off)")
    led = ledger_checks()
    held = HC.held_goals()
    rng = np.random.default_rng(CH.FROZEN["seed"])
    if a.dry_run:
        goals = [STANDINS[g] for g in TARGETS]
        assert not set(goals) & held, "stand-ins must be non-holdout"
        base = HC.OUT / "confirm_r1b_dryrun"
        info = build_labels(goals, base, allow_holdout=False)
        # reproduction: the confirm builder must equal build_r1b's exploratory files on the stand-ins
        repro = {}
        for g in goals:
            for st in ("project", "action", "work"):
                x = pl.read_parquet(base / f"G{g:02d}/labels_{st}_w{W}.parquet").select("day", "win", "agent", "label").sort("day", "win", "agent")
                y = pl.read_parquet(HC.OUT / f"r1b/G{g:02d}/labels_{st}_w{W}.parquet").select("day", "win", "agent", "label").sort("day", "win", "agent")
                repro[f"G{g:02d}_{st}"] = bool(x.equals(y))
        n_null = 49
    else:
        blocked = [t for t, c in led.items() if not c["allowed"]]
        if blocked:
            raise SystemExit(f"holdout_ledger.check refuses {blocked} (same-family prior run); resolve before running.")
        assert set(TARGETS) <= held, "confirm targets must be holdout periods"
        goals = list(TARGETS)
        base = HC.OUT / "confirm_r1b"
        info = build_labels(goals, base, allow_holdout=True)
        repro = None
        n_null = CH.FROZEN["n_null"]
    results, work = [], []
    for g, cls in TARGETS.items():
        gg = STANDINS[g] if a.dry_run else g
        o = CH.run_target(gg, base, n_null, rng)
        o.update(target=g, cls=cls, verdict=CH.verdict(o, cls) if o.get("tested") else "n/a")
        if a.dry_run:
            o["standin"] = gg
        results.append(o)
        w = run_work(gg, base, n_null, rng)
        w["target"] = g
        work.append(w)
    ov = CH.overall(results)
    c4 = [w for w in work if w.get("tested")]
    rep = dict(mode="dry-run (round-1b re-freeze)" if a.dry_run else "CONFIRM (locked holdout, round-1b re-freeze)",
               run_at=dt.datetime.now(dt.timezone.utc).isoformat(), frozen=CH.FROZEN,
               disclosure="ledger item 11: #35 contradicts C2's frozen clause in exploration (z_N2 attention -2.5)",
               inputs="shared project_states (deterministic), deterministic action classes, DQ4 work state",
               label_rows=info, reproduction=repro, ledger=led, results=results, overall=ov,
               C4_r1b={"targets": work, "tested": len(c4), "pass_all_tested": bool(c4 and all(w["C4_pass"] for w in c4))})
    outf = base / "confirm_results.json"
    outf.write_text(json.dumps(rep, indent=1, default=lambda x: float(x) if hasattr(x, "item") else str(x)))
    for o in results:
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in o.items()})
    for w in work:
        print("C4-r1b", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in w.items()})
    print("overall:", ov, "| reproduction:", repro)
    print("ledger:", json.dumps({t: {k: v for k, v in c.items() if k != "competing_planned"} for t, c in led.items()}))


if __name__ == "__main__":
    main()
