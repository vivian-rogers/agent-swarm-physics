"""H18 confirmatory test on the LOCKED HOLDOUT -- ROUND-1B RE-FREEZE of `confirm_holdout.py`. Written 2026-10-04
after round 1b, before any holdout outcome was computed. NOT RUN. `confirm_holdout.py` stays byte-for-byte unchanged.

  uv run python hypotheses/H18-attention-dilution/analysis/confirm_r1b.py --dry-run
  uv run python hypotheses/H18-attention-dilution/analysis/confirm_r1b.py --confirm --i-understand-this-uses-the-locked-holdout

Without both confirm flags the script refuses to touch held-out days. --dry-run runs the identical pipeline on the same
non-holdout stand-ins as confirm_holdout.py (asserting every stand-in day is outside the holdout).

What changes vs confirm_holdout.py: the INPUTS only (holdout ledger item 10). The pending sets, talk turns and timer
wakes are built by the round-1b ledger scheme (`scheme/build_ledger.py`) instead of round 1's call-start rule:
  * talk turn = a ledger talk call (`call_windows`, message -> call through its AGENT_TALK event, as DQ2);
  * pending set P(tau) = ledger items received since the previous talk call (= `context_ledger_turns.k_since_talk`);
  * D2 timer wakes = ledger calls with gap_kind = pause (not early wakes), batch = that call's items;
  * the response stays the pre-registered @-mention of the sender (`chat_mentions_clean`), as in round 1b's primary
    column; the DQ2 reply-parent response is reported as a descriptive variant (it builds in a one-parent budget, so it
    cannot test dilution as posed: infra/README Known issues, RE-V1);
  * C5's post side is the round-1b G35 folder (ledger inputs), not round 1's.
activity_bins, embeddings, failures, the work ledger and nudge targets are not inputs of this design.
build_ledger.py hard-codes `~holdout` filters, so under --confirm the builder reads a temporary view of the shared
folder in which call_windows / context_ledger_turns / reply_pairs rows of the TARGET days only carry holdout = False;
the dry run goes through the same view (it changes nothing there, asserted). The view is deleted after the build.

Predictions: C1-C6 are kept exactly as frozen in confirm_holdout.py. Round 1b moved every period exponent by <= 0.1
(pooled 0.63 -> 0.66; regime I 0.55 -> 0.61, III 0.68; #51 0.61 [0.58, 0.62]; #51 D2 0.45 [0.41, 0.50]), so every
band still sits where it was set; no prediction needed changing. No band was moved toward any exploratory value.

Holdout reuse (hypotheses/holdout.md; infra/shared/holdout_ledger.py check() is called before any confirm build):
#45 was used by H02 (activity couplings), #46-#50 by H04 (hours / Hawkes, NE21+NE23), #34 by H05 (activity/talk on
03-05..03-13). H18's observable (mention responses vs ledger pending count) has not been computed on these days.
Planned same-family users (dilution/addressing): H08 (#28, #29, #45-#50, #51 tail), H11, H28, H29, H34, H39.
Disclose in both cards and LOG.md; commit this script and the card first.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2"

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import json  # noqa: E402
import shutil  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H18-attention-dilution"
R1B_G35 = OUT / "r1b" / "G35"
VIEW_TABLES = ("call_windows", "context_ledger_turns", "reply_pairs")

# targets, stand-ins and predictions: identical to confirm_holdout.py (frozen 2026-10-03)
TARGETS = {
    "T51tail": (51, ("2026-09-07", "2026-09-21")), "T45": (45, ("2026-06-01", "2026-06-08")),
    "T46": (46, ("2026-06-08", "2026-06-15")), "T47": (47, ("2026-06-15", "2026-06-22")),
    "T49": (49, ("2026-06-23", "2026-06-29")), "T50": (50, ("2026-06-29", "2026-07-06")),
    "T28": (28, ("2026-01-26", "2026-02-02")), "T29": (29, ("2026-02-02", "2026-02-09")),
    "T34pre": (34, ("2026-03-09", "2026-03-14")),
}
STANDINS = {
    "T51tail": (51, ("2026-08-24", "2026-09-05")), "T45": (41, ("2026-05-11", "2026-05-18")),
    "T46": (42, ("2026-05-18", "2026-05-25")), "T47": (44, ("2026-05-26", "2026-06-01")),
    "T49": (39, ("2026-04-27", "2026-05-04")), "T50": (40, ("2026-05-04", "2026-05-11")),
    "T28": (30, ("2026-02-09", "2026-02-16")), "T29": (31, ("2026-02-16", "2026-02-23")),
    "T34pre": (39, ("2026-04-27", "2026-05-04")),
}
LEDGER_TARGETS = {"T51tail": "#51-tail", "T45": "G45", "T46": "G46", "T47": "G47", "T49": "G49", "T50": "G50",
                  "T28": "G28", "T29": "G29", "T34pre": "G34"}
PREDICTIONS = {
    "C1": "T51tail: D1 beta-hat CI excludes 0 and beta-hat in [0.35, 0.85]; effective CV winner M_sat or M_rec (unchanged)",
    "C2": "T45-T50 (each >= 300 units): beta-hat CI excludes 0 in >= 4 of 5; pooled RE beta-hat in [0.45, 0.95]; M_const "
          "never the effective CV winner (unchanged)",
    "C3": "T51tail + T45-T50: Spearman(p-bar, N_room) < 0 over the 6 points and CV(B-hat) < CV(p-bar) (unchanged)",
    "C4": "T28, T29: beta-hat in [0.3, 0.8] with CI excluding 0 in both (unchanged)",
    "C5": "NE15 (T34pre vs G35, round-1b ledger folder): #best agents' per-pair uptake rises, S changes < 50%, #rest change "
          "less (unchanged rule; post side switched to the ledger build)",
    "C6": "T51tail timer wakes: beta-hat_D2 > 0 with CI excluding 0 (unchanged)",
    "inputs": "round-1b ledger scheme (build_ledger.py): ledger talk calls, k = k_since_talk, ledger timer wakes; response = "
              "mention (pre-registered); reply-parent response descriptive only",
}


def ledger_checks():
    import holdout_ledger as HL
    out = {}
    for name, t in LEDGER_TARGETS.items():
        c = HL.check("H18", t, "other", ["dilution_addressing"])
        out[t] = {"allowed": c["allowed"], "needs_disclosure": c["needs_disclosure"],
                  "prior_runs": sorted({u["hypothesis"] for u in c["prior_runs"]}),
                  "prior_runs_same_family": sorted({u["hypothesis"] for u in c["prior_runs_same_family"]}),
                  "competing_planned": sorted({u["hypothesis"] for u in c["competing_planned"]})}
    return out


def target_days(g, dates, holdout: bool):
    cal = pl.read_parquet(SH / "calendar.parquet").filter(
        (pl.col("goal_no") == g) & (pl.col("pt_date") >= dates[0]) & (pl.col("pt_date") < dates[1]) & (pl.col("window_s") > 0))
    days = sorted(cal["pt_date"].to_list())
    hm = holdout_mask(days, [g] * len(days))
    hc = dict(zip(cal["pt_date"].to_list(), cal["holdout"].to_list()))
    if holdout:
        return [d for d, m in zip(days, hm) if m or hc[d]]          # only_holdout, as confirm_holdout.py
    assert not any(hm) and not any(hc.values()), "stand-in touches held-out days"
    return days


def make_view(view: Path, days: list[str], holdout: bool):
    """Shared folder view: symlinks to every shared table, plus row-filtered copies of the three ledger tables in which
    the target days carry holdout = False (only under --confirm can any such row have been True)."""
    if view.exists():
        shutil.rmtree(view)
    view.mkdir(parents=True)
    for p in SH.iterdir():
        if p.stem in VIEW_TABLES and p.suffix == ".parquet":
            continue
        (view / p.name).symlink_to(p)
    for t in VIEW_TABLES:
        lf = pl.scan_parquet(SH / f"{t}.parquet")
        if t != "reply_pairs":
            lf = lf.filter(pl.col("pt_date").is_in(days))
        df = lf.collect()
        flip = df["pt_date"].is_in(days) & df["holdout"]
        if not holdout:
            assert not bool(flip.any()), f"dry run: {t} has held-out rows on stand-in days"
        df.with_columns(pl.when(pl.col("pt_date").is_in(days)).then(False).otherwise(pl.col("holdout")).alias("holdout")
                        ).write_parquet(view / f"{t}.parquet")


def build_all(names, holdout: bool, base: Path):
    import build_ledger as BL
    spec = {n: (TARGETS[n] if holdout else STANDINS[n]) for n in names}
    days = {n: target_days(g, d, holdout) for n, (g, d) in spec.items()}
    view = base / "_shared_view"
    make_view(view, sorted({d for v in days.values() for d in v}), holdout)
    BL.SH = view
    sh = BL.Shared()
    built = {}
    for n, (g, _d) in spec.items():
        if not days[n]:
            print(n, "no days")
            continue
        BL.period_days = (lambda _sh, _g, _days=days[n]: list(_days))
        res = BL.build_period(sh, g, verbose=True)
        if res is None:
            continue
        BL.OUT = base / n
        BL.write_period(g, res)
        built[n] = (base / n, BL.gname(g), g)
    shutil.rmtree(view)
    return built


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--boot", type=int, default=200)
    ap.add_argument("--only", default=None, help="comma-separated target names")
    a = ap.parse_args()
    if a.dry_run and (a.confirm or a.ack):
        sys.exit("choose either --dry-run or --confirm, not both")
    if not a.dry_run and not (a.confirm and a.ack):
        sys.exit("REFUSED: this script reads the locked holdout. Pass --confirm --i-understand-this-uses-the-locked-holdout "
                 "(only after the card's confirmatory predictions and this script are committed), or --dry-run.")
    holdout = not a.dry_run
    led = ledger_checks()
    if holdout:
        blocked = [t for t, c in led.items() if not c["allowed"]]
        if blocked:
            sys.exit(f"holdout_ledger.check refuses {blocked} (same-family prior run); resolve before running.")
    import confirm_holdout as CH       # frozen evaluator (C1-C6 rules); main() is not called
    from fit_periods import run
    base = OUT / ("confirm_r1b" if holdout else "confirm_r1b_dryrun")
    base.mkdir(parents=True, exist_ok=True)
    names = a.only.split(",") if a.only else list(TARGETS)
    built = build_all(names, holdout, base)
    F, Frep = {}, {}
    for name, (folder, gp, g) in built.items():
        two_room = g in (35, 36, 37, 38, 39, 41, 42, 44, 45, 46, 47, 49, 50)
        B = a.boot if name != "T51tail" else min(a.boot, 60)
        B = B if holdout else min(B, 20)
        F[name] = run(gp, B, base=folder, two_room=two_room, resp="resp")
        Frep[name] = run(gp, min(B, 40), base=folder, two_room=two_room, resp="resp_reply", tag="reply")
    CH.OUT = OUT / "r1b"                       # C5's post side: OUT/"G35" -> the round-1b ledger build of G35
    if "T34pre" in built:
        tp = base / "T34pre"
        (tp / "_c5").mkdir(exist_ok=True)
        for f in ("talks.parquet", "pending.parquet"):
            src = built["T34pre"][0] / built["T34pre"][1] / f
            dst = tp / "_c5" / f
            if not dst.exists():
                dst.symlink_to(src)
    R = CH.evaluate(F, base) if "T34pre" not in built else evaluate_c5_fix(CH, F, base)
    R["reply_variant_descriptive"] = {n: {"beta": f["D1"]["beta"], "eff": (f["D1"].get("cv_block") or {}).get("effective")}
                                      for n, f in Frep.items()}
    R["_meta"] = dict(mode="CONFIRMATORY (holdout)" if holdout else "dry-run (non-holdout stand-ins)",
                      script="confirm_r1b.py (re-freeze of confirm_holdout.py)", inputs="round-1b ledger scheme",
                      run_at=dt.datetime.now(dt.timezone.utc).isoformat(), predictions=PREDICTIONS, ledger=led)
    (base / "results.json").write_text(json.dumps(R, indent=1, default=float))
    for k, v in R.items():
        if k.startswith("C"):
            print(k, "PASS" if v.get("pass_") else "FAIL", {kk: vv for kk, vv in v.items() if kk not in ("rows", "pooled")})
    print("reply variant (descriptive):", R["reply_variant_descriptive"])
    print("ledger:", json.dumps({t: {k: v for k, v in c.items() if k != "competing_planned"} for t, c in led.items()}))


def evaluate_c5_fix(CH, F, base):
    """confirm_holdout.evaluate() reads T34pre from base/'T34pre' (talks/pending directly there); the ledger build writes
    them one level down (base/T34pre/G<NN>/). Point C5 at the symlinked copy; every rule is the frozen one."""
    R = CH.evaluate({k: v for k, v in F.items() if k != "T34pre"}, base)
    if (CH.OUT / "G35/talks.parquet").exists():
        R["C5"] = CH.ne15_before_after(base / "T34pre" / "_c5", CH.OUT / "G35")
    return R


if __name__ == "__main__":
    main()
