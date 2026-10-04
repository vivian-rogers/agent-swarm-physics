"""H35 confirmatory test on the locked holdout, RE-FROZEN ON ROUND-1B OUTCOMES (written 2026-10-04). NOT RUN.

Re-freeze of `confirm.py` (left byte-for-byte untouched), written before any held-out outcome was read. Details in
`CONFIRM_R1B.md`. H35's inputs were already correct (leading-@ targets; active rows from events_core + actions via
h16lib, so the activity_bins event drop never touched it). What changes is the OUTCOME (round 1b,
analysis/r1b_outcomes.py): active minutes measure attention, so work claims move to
  * glance  = any active row in m+1..m+30 (placebo-clean attention outcome);
  * sustained = a run of >= 3 consecutive active DQ1 ledger calls starts in m+1..m+30 (H43's definition);
  * work    = DQ4 agent work commits (canonical & ~imported & agent & ~automated), rate difference-in-differences
              (post 60 min minus placebo m-30..m-16), because the matched design fails its placebo for work and
              sustained outcomes (round 1b; Known issue 82).
The information criteria (C1, C2, C6) and the attention-side gate criteria (C3, C4, C7) are unchanged.

Refuses to touch held-out data unless called with BOTH --confirm --i-understand-this-uses-the-locked-holdout, the H35
folder is committed and clean, and infra/shared/holdout_ledger.check() reports no same-family run of the same modality
on a target. NOTE: the ledger tags H04's executed NE21+NE23 / #45 runs (nudge A30, activity timing) as kick_response,
the same family as H35's #45/#47/#50 entries, so this guard refuses those targets until Vivian re-tags or overrides the
ledger (H35's statistics there are bits per nudge, the gate slope and the policy ratio, not A30).
`--dry-run` runs the identical code on non-holdout stand-ins into data/processed/H35-nudger-maxwell-demon/r1b/
confirm_r1b_dryrun/ (never evidence): #45 -> G44, #47 -> G51a, #50 -> G51b, #32 -> G31, #34 -> G35.

Targets (unchanged): #45 (long pause), #47 and #50 (short pause), #32 (regime I), #34 (regime II).
Predictions ("-r1b" = changed or new; reasons in CONFIRM_R1B.md):
  C1  (primary; 45, 47, 50) I(M; D,G,K) above its permutation null and b in [0.8, 3.0] bits per nudge. (unchanged)
  C2  (primary; 47, 50) I(M;K) + I(M;K|D,G) > I(M;G|D). (unchanged)
  C3  (primary; 47, 50) gate model, glance escapes: gate-once (k*=2) / logged ratio > 1. (unchanged; attention claim)
  C4  (primary; 47, 50) gate model, glance escapes: nudge x ln k < 0. (unchanged)
  C7  (secondary; 45) long pause: escape at nudged gates >= 0.8, at un-nudged gates <= 0.6 (glance). (unchanged)
  C5-r1b (secondary; 32, 34) first-nudge GLANCE ATT (past-only matched, 30 min) point > 0. (was: A30 active minutes)
  C6  (secondary; 32, 34) the nudger's state information above the permutation null. (unchanged)
  C8-r1b (primary, new; 47 + 50 pooled) nudges buy no detectable work: first-nudge work-commit DiD (commits/h, 60 min)
         pooled 95% CI includes 0, with CI half-width <= 1.0 commit/h (else "inconclusive", underpowered).
         [round 1b G51: +0.22 [-0.29, +0.82]]
  C9-r1b (secondary, new; 47, 50) gate model refit on SUSTAINED escapes: gate-once / logged ratio <= 1.25 (the
         once-early gain does not reach sustained runs). [round 1b G51 x1.03]
Overall: supported if every testable primary passes; failed if none passes; mixed otherwise.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import h35lib as L  # noqa: E402
from h35lib import h16lib  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
HYP = "H35"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


RP = _load("h35_run_period", HERE / "run_period.py")
X = _load("h35_r1b_outcomes", HERE / "r1b_outcomes.py")
C0 = _load("h35_confirm_r1", HERE / "confirm.py")      # round-1 predictions C1-C4, C6, C7 (unchanged functions)

TARGETS = C0.TARGETS
LEDGER_T = {"45": "G45", "47": "G47", "50": "G50", "32": "G32", "34": "G34"}
PREDICTIONS = {k: v for k, v in C0.PREDICTIONS.items() if k in ("C1", "C2", "C3", "C4", "C6", "C7")}


def register(pid, targets, primary, statement):
    def deco(f):
        PREDICTIONS[pid] = dict(targets=targets, primary=primary, statement=statement, fn=f)
        return f
    return deco


@register("C5-r1b", ["32", "34"], False, "first-nudge GLANCE ATT (past-only matched, 30 min) point > 0")
def c5r(r):
    a = r.get("r1b", {}).get("att", {}).get("y_glance30")
    if not a or not a.get("n_first"):
        return "n/a", {}
    pt = a["first"][0]
    return ("pass" if pt is not None and pt > 0 else "fail"), {"glance_att": a["first"], "placebo": a["placebo"], "n": a["n_first"]}


@register("C9-r1b", ["47", "50"], False, "gate model on SUSTAINED escapes: gate-once / logged ratio <= 1.25")
def c9r(r):
    g = r.get("r1b", {}).get("gate_sustained", {}).get("eff_escapes_separate", {})
    x = g.get("ratio_gate_once2_vs_logged")
    if x is None:
        return "n/a", {}
    return ("pass" if x <= 1.25 else "fail"), {"ratio_sustained": x}


def c8_pooled(results: dict) -> tuple[str, dict]:
    """C8-r1b: inverse-variance pool of the first-nudge work DiD over #47 and #50 (or their stand-ins)."""
    est = []
    for tid in ("47", "50"):
        w = results[tid].get("r1b", {}).get("did", {}).get("work_did_h", {}).get("first")
        if w and w[1] is not None and np.isfinite(w[1]) and w[2] > w[1]:
            est.append((w[0], (w[2] - w[1]) / 3.92))
    if not est:
        return "n/a", {}
    e, s = np.array([x[0] for x in est]), np.array([x[1] for x in est])
    wts = 1 / s ** 2
    m, se = float((wts * e).sum() / wts.sum()), float(np.sqrt(1 / wts.sum()))
    lo, hi = m - 1.96 * se, m + 1.96 * se
    if 1.96 * se > 1.0:
        return "inconclusive", {"pooled": [m, lo, hi], "k": len(est)}
    return ("pass" if lo <= 0 <= hi else "fail"), {"pooled": [m, lo, hi], "k": len(est)}


def load_sources(allow_holdout: bool):
    """r1b_outcomes.load_sources with the holdout filter only for exploration (dry run)."""
    hf = pl.lit(True) if allow_holdout else ~pl.col("holdout")
    led = (pl.scan_parquet(L.SH / "context_ledger_turns.parquet").filter(hf)
           .select("agent", "pt_date", "t_first", "kind").collect()
           .with_columns(pl.col("kind").cast(pl.Utf8).is_in(X.ACTIVE_KINDS).alias("act"),
                         (pl.col("t_first").dt.epoch("us") / 1e6).alias("ts"))
           .sort("agent", "pt_date", "ts"))
    led = led.with_columns((pl.col("act") != pl.col("act").shift(1).over("agent", "pt_date")).fill_null(True).alias("brk"))
    led = led.with_columns(pl.col("brk").cast(pl.Int32).cum_sum().over("agent", "pt_date").alias("run"))
    runs = (led.filter(pl.col("act")).group_by("agent", "pt_date", "run")
            .agg(pl.len().alias("n"), pl.col("ts").min().alias("t_start")).filter(pl.col("n") >= 3))
    sust = {(int(a), d): np.sort(g["t_start"].to_numpy()) for (a, d), g in runs.group_by(["agent", "pt_date"])}
    wc = (pl.read_parquet(L.SH / "work_commits.parquet", columns=["t", "pt_date", "author_agent", "author_kind", "canonical",
                                                                   "imported", "automated", "holdout"])
          .filter(pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind") == "agent") & ~pl.col("automated")
                  & hf & pl.col("author_agent").is_not_null())
          .with_columns((pl.col("t").dt.epoch("us") / 1e6).alias("ts")))
    work = {(int(a), d): np.sort(g["ts"].to_numpy()) for (a, d), g in wc.group_by(["author_agent", "pt_date"])}
    return sust, work


def did_block(df: pl.DataFrame, W: dict, sust: dict, work: dict, rng, B: int) -> dict:
    """r1b_outcomes.run_did's per-period block (now pre-registered): first-nudge rate DiD for sustained runs and work."""
    parts = []
    for (a, dd), g in df.select("agent", "pt_date", "minute").group_by(["agent", "pt_date"], maintain_order=True):
        a, t0, t1 = int(a), W[dd]["t0"], W[dd]["t1"]
        n_min = int(np.ceil((t1 - t0) / 60.0))
        m = g["minute"].to_numpy().astype(int)

        def cum(arr):
            if arr is None or len(arr) == 0:
                return np.zeros(n_min + 1)
            q = np.floor((arr - t0) / 60.0).astype(int)
            q = q[(q >= 0) & (q < n_min)]
            return np.r_[0, np.cumsum(np.bincount(q, minlength=n_min))].astype(float)
        cs, cw = cum(sust.get((a, dd))), cum(work.get((a, dd)))
        lo1 = np.clip(m + 1, 0, n_min)
        pre = lambda c: c[np.clip(m - 15, 0, n_min)] - c[np.clip(m - 30, 0, n_min)]  # noqa: E731
        s_post = cs[np.clip(m + 31, 0, n_min)] - cs[lo1]
        w_post = np.where(m + 61 <= n_min, cw[np.clip(m + 61, 0, n_min)] - cw[lo1], np.nan)
        parts.append(pl.DataFrame({"agent": g["agent"], "pt_date": g["pt_date"], "minute": g["minute"],
                                   "sust_did_h": (s_post / 30 - pre(cs) / 15) * 60,
                                   "work_did_h": (w_post / 60 - pre(cw) / 15) * 60}))
    d2 = df.join(pl.concat(parts), on=["agent", "pt_date", "minute"], how="left")
    Ds = X.designs(d2)
    days_a = d2["pt_date"].to_numpy()
    res = {}
    for y in ("sust_did_h", "work_did_h"):
        ok = np.isfinite(d2[y].fill_null(np.nan).to_numpy())
        sub = d2.filter(pl.Series(ok))
        D2 = {k: v[ok] for k, v in Ds.items()}
        r = L.matched_att(sub, D2["first"], D2["ctrl"], y)
        res[y] = {"first": L.day_boot_mean(r["resid"], days_a[ok][r["idx"]], rng, B), "n_first": int(len(r["idx"]))}
    return res


def r1b_block(out_dir: Path, days: list[str], gate: bool, sust: dict, work: dict, B: int) -> dict:
    rng = np.random.default_rng(L.SEED + 7)
    grid = pl.read_parquet(out_dir / "grid.parquet")
    W = h16lib.windows(days)
    add = X.add_outcomes(grid, W, sust, work)
    df = grid.join(add, on=["agent", "pt_date", "minute"], how="left")
    res = {"nudge_epochs": int(df["M"].sum())}
    if df["M"].sum() < 3:
        return res
    att, _ = X.att_block(df, rng, B)
    res["att"] = att
    res["did"] = did_block(df, W, sust, work, np.random.default_rng(L.SEED + 8), B)
    if gate and (out_dir / "gates.parquet").exists():
        gates = pl.read_parquet(out_dir / "gates.parquet")
        if gates["M"].sum() >= 5:
            try:
                res["gate_sustained"] = X.gate_sustained(gates, sust, rng, B)
            except Exception as ex:
                res["gate_sustained"] = {"error": repr(ex)}
    return res


def committed() -> bool:
    out = subprocess.run(["git", "-C", str(L.ROOT), "status", "--porcelain", "--", "hypotheses/H35-nudger-maxwell-demon"],
                         capture_output=True, text=True).stdout
    return out.strip() == ""


def ledger_gate(strict: bool) -> list[str]:
    sys.path.insert(0, str(L.ROOT))
    from infra.shared import holdout_ledger as hl
    led = hl.load()
    bad = []
    for tid, t in LEDGER_T.items():
        mine = [e for e in led["entries"] if e["hypothesis"] == HYP and e["target"] == t]
        mod = mine[0]["modality"] if mine else "activity timing"
        fam = sorted({f for e in mine for f in e["estimator_family"]}) or ["kick_response"]
        r = hl.check(HYP, t, mod, fam)
        same_mod = sorted({u["hypothesis"] for u in r["prior_runs_same_family"] if u["modality"] == mod})
        print(f"ledger {t} [{mod}]: allowed={r['allowed']} same_family_same_modality_runs={same_mod} "
              f"prior_runs={sorted({u['hypothesis'] for u in r['prior_runs']})} "
              f"competing_planned={sorted({u['hypothesis'] for u in r['competing_planned']})}", flush=True)
        if same_mod:
            bad.append(f"{t}: same-family same-modality prior run by {same_mod}")
    return bad if strict else []


def main():
    args = sys.argv[1:]
    dry = "--dry-run" in args
    real = "--confirm" in args and "--i-understand-this-uses-the-locked-holdout" in args
    if not dry and not real:
        sys.exit("refusing: pass --dry-run (stand-ins) or --confirm --i-understand-this-uses-the-locked-holdout")
    if real and not committed():
        sys.exit("refusing: commit the H35 card, confirm_r1b.py and CONFIRM_R1B.md first (holdout reuse policy)")
    bad = ledger_gate(strict=real)
    if real and bad:
        sys.exit("refusing (holdout ledger):\n  " + "\n  ".join(bad))
    B = 200
    SB = _load("h35_build", HERE.parent / "scheme" / "build.py")
    base = L.OUT / "r1b" / ("confirm_r1b_dryrun" if dry else "confirm_r1b")
    sust, work = load_sources(allow_holdout=real)
    results, verdicts = {}, {}
    for tid, t in TARGETS.items():
        name = t["stand_in"] if dry else f"C{tid}"
        if dry:
            p = SB.PERIODS[t["stand_in"]]
            days = SB.period_days(p)
            h16lib.assert_no_holdout(days)
        else:
            days = h16lib.period_days(t["goal"], allow_holdout=True)
        out = base / name
        SB.build_period(name, days, out, t["gate"], allow_holdout=not dry)
        results[tid] = RP.run(str(out.relative_to(L.OUT)), B=B)
        results[tid]["r1b"] = r1b_block(out, days, t["gate"], sust, work, B)
        print(tid, name, "done", flush=True)
    for pid, pr in PREDICTIONS.items():
        verdicts[pid] = {}
        for tid in pr["targets"]:
            try:
                v, obs = pr["fn"](results[tid])
            except Exception as ex:
                v, obs = "n/a", {"error": repr(ex)}
            verdicts[pid][tid] = {"verdict": v, "observed": obs}
    v8, o8 = c8_pooled(results)
    verdicts["C8-r1b"] = {"47+50": {"verdict": v8, "observed": o8}}
    prim_ids = [pid for pid, pr in PREDICTIONS.items() if pr["primary"]]
    prim = [v["verdict"] for pid in prim_ids for v in verdicts[pid].values()] + [v8]
    tested = [x for x in prim if x in ("pass", "fail")]
    overall = ("untestable" if not tested else "supported" if all(x == "pass" for x in tested) else
               "failed" if not any(x == "pass" for x in tested) else "mixed")
    summary = {"mode": "dry-run r1b (stand-ins; not evidence)" if dry else "CONFIRMATORY r1b (locked holdout)",
               "predictions": {pid: {k: v for k, v in pr.items() if k != "fn"} for pid, pr in PREDICTIONS.items()}
               | {"C8-r1b": {"targets": ["47", "50"], "primary": True,
                             "statement": "pooled first-nudge work-commit DiD CI includes 0, half-width <= 1/h"}},
               "verdicts": verdicts, "overall": overall,
               "r1b_blocks": {tid: r.get("r1b") for tid, r in results.items()}}
    L.jdump(summary, base / "confirm_r1b_summary.json")
    print(json.dumps(summary["verdicts"], indent=1, default=str))
    print("overall:", overall, "|", summary["mode"])


if __name__ == "__main__":
    main()
