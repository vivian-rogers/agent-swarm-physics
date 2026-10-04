"""H43 confirmatory test on the LOCKED HOLDOUT, RE-FROZEN ON THE LEADING-@ NUDGE TARGET (written 2026-10-04; NOT RUN).

Re-freeze of `confirm.py` (left byte-for-byte untouched; holdout.md ledger item 17). Written before any holdout data
was read. Details and reasons: `CONFIRM_R1B.md`.

What changed vs confirm.py
  * Nudge target (class N): the leading @ only (H35 rule, STANDARDS §2; shared helper
    infra/shared/idle_gates.leading_targets). round 1 counted a nudge for every agent it named (`ment`), so 29% of
    nudges also "kicked" agents named second. A nudge read by an agent who is named but is not its leading @ is now
    `nNo`: it is not a class-N kick, but it marks the 30-min quiet window and excludes the call as a control
    (H39 round-1b N_oth rule). The per-call counts are rebuilt from `context_ledger_items` in memory for both modes.
  * Other inputs are already current: receiving-call timing and visibility from the DQ1 context ledger
    (`call_windows`, `context_ledger_items`), DQ4 work ledger writes, shared `states_min`; no activity_bins, outages,
    failures or embeddings. @-mentions (class A) keep the ledger `ment` flag: the leading-@ rule is for nudges.
  * Predictions: C1, C2, C3, C5 unchanged (mentions and humans do not depend on the nudge target). C4's thresholds are
    unchanged; it is now computed on leading-@ nudges and is relabelled C4-r1b. The dry run adds a G51 stand-in
    (non-holdout days 2026-07-27 -> 08-20, nudger on) so that C4's code path is exercised at a powered size.
  * Guards added: a holdout-ledger gate. H04's executed confirmatory run measured nudge -> activity responses
    (kick_response family, activity timing) on #45 and #46-#50, so C4 on those periods is a same-family,
    same-modality second use (policy item 2). C4 is n/a by default; `--include-ledger-blocked` re-enables it, only on
    Vivian's written override (LOG.md). Overall rule then rests on C5 for the "C4 or C5" clause.

Frozen predictions (card "Confirmatory plan"; unchanged except as labelled):
  C1  mentions, #51 tail (2026-09-07 -> 09-21), busy recipients, O2c: E1 > 0 (95% CI above 0); R(0,15] point in
      [0.5, 1.1] with lower CI > 0.3; R(60,240] >= 0.7; delta_half < 2 min in >= 80% of draws.
  C2  mentions, #51 tail: batched R (O2c) <= 0.5.
  C3  mentions, #51 tail, O2: R_in >= 0.4.
  C4-r1b nudges (leading @), #45-#50 pooled: E1(O1a) > 0 and E1(O1) < 0.3; R(15,60] on O1a >= 0.7; n/a if < 50 idle
      primers. Blocked by the ledger unless overridden.
  C5  human messages, #1, #9, #14, #15 (5-min quiet): E1(O2c) > 0 and R(0,2] (O2c) >= 0.7; n/a if < 50 busy primers.
Overall: "no refractory window beyond the read-out" is confirmed if C1, C2 and at least one of C4-r1b/C5 pass and no
scored C fails.

Guard: refuses to touch the holdout without BOTH --confirm and --i-understand-this-uses-the-locked-holdout, and refuses
if hypotheses/H43-kick-refractory-window/ has uncommitted changes. Without the flags it is a DRY RUN on non-holdout
stand-ins (C1-C3: #51 2026-08-24 -> 09-05; C4: G38, G41, G42, G44, plus G51 07-27 -> 08-20 reported separately;
C5: G04 4a/4c, G05, G06) into data/processed/H43-kick-refractory-window/confirm_r1b_dryrun/confirm_results.json.

Usage:  uv run python hypotheses/H43-kick-refractory-window/analysis/confirm_r1b.py                    (dry run)
        uv run python hypotheses/H43-kick-refractory-window/analysis/confirm_r1b.py --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import json  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h43lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
import holdout_ledger as HL  # noqa: E402
from idle_gates import leading_targets  # noqa: E402

HYP = "H43"
TARGETS = {
    "tail": {"goals": [51], "date_from": "2026-09-07", "date_to": "2026-09-21"},
    "nudge": {"goals": [45, 46, 47, 48, 49, 50]},
    "human": {"goals": [1, 9, 14, 15]},
}
STANDINS = {
    "tail": {"goals": [51], "date_from": "2026-08-24", "date_to": "2026-09-05"},
    "nudge": {"goals": [38, 41, 42, 44]},
    "human": {"goals": [4, 5, 6], "units": ["4a", "4c", "5", "6a", "6b"]},
}
STANDIN_NUDGE_G51 = {"goals": [51], "date_from": "2026-07-27", "date_to": "2026-08-21"}
LEDGER = {  # block: (ledger targets, modality, families)
    "tail": (["#51-tail"], "activity timing", ["kick_response", "dilution_addressing"]),
    "nudge": ([f"G{g}" for g in TARGETS["nudge"]["goals"]], "activity timing", ["kick_response"]),
    "human": ([f"G{g:02d}" for g in TARGETS["human"]["goals"]], "activity timing", ["kick_response"]),
}


def ledger_gate(include_blocked: bool) -> tuple[dict, dict]:
    """Per block: blocked if any target has a same-family prior run of the same modality."""
    rep, blocked = {}, {}
    for blk, (targets, mod, fam) in LEDGER.items():
        rows = {}
        for t in targets:
            r = HL.check(HYP, t, mod, fam)
            same = sorted({x["hypothesis"] for x in r["prior_runs_same_family"] if x["modality"] == mod})
            rows[t] = {"allowed": r["allowed"], "same_family_same_modality_runs": same,
                       "prior_runs": sorted({x["hypothesis"] for x in r["prior_runs"]}),
                       "competing_planned": sorted({x["hypothesis"] for x in r["competing_planned"]})}
        hit = any(v["same_family_same_modality_runs"] for v in rows.values())
        blocked[blk] = bool(hit and not include_blocked)
        rep[blk] = {"modality": mod, "family": fam, "targets": rows, "blocked": blocked[blk]}
    return rep, blocked


def kick_counts_r1b(calls: pl.DataFrame) -> pl.DataFrame:
    """Replace nN by leading-@ nudges; add nNo (nudges naming the recipient, not as its leading @)."""
    it = (pl.scan_parquet(L.SH / "context_ledger_items.parquet")
          .select("turn_id", "message_id", "kind", "ment")
          .filter(pl.col("turn_id").is_in(calls["turn_id"].implode()) & (pl.col("kind").cast(pl.Utf8) == "nudge"))
          .collect())
    lt = leading_targets(it["message_id"].unique().to_list())
    it = (it.with_columns(pl.col("message_id").replace_strict(lt, default=None, return_dtype=pl.Int64).alias("lead"))
          .join(calls.select("turn_id", pl.col("agent").cast(pl.Int64).alias("rcpt")), on="turn_id", how="inner"))
    agg = (it.group_by("turn_id")
           .agg((pl.col("lead") == pl.col("rcpt")).fill_null(False).sum().cast(pl.Int16).alias("nN_lead"),
                (pl.col("ment") & (pl.col("lead") != pl.col("rcpt")).fill_null(True)).sum().cast(pl.Int16).alias("nNo")))
    out = calls.join(agg, on="turn_id", how="left").with_columns(
        pl.col("nN").alias("nN_ment"), pl.col("nN_lead").fill_null(0).alias("nN"), pl.col("nNo").fill_null(0))
    return out.drop("nN_lead")


class PrepR1b(L.Prep):
    """h43lib.Prep plus nNo: non-leading nudges block the quiet window and controls but are not class-N kicks."""

    def __init__(self, calls, states, writes, cal):
        super().__init__(calls, states, writes, cal)
        no = self.c["nNo"].to_numpy().astype(np.int64) if "nNo" in self.c.columns else np.zeros(self.n, np.int64)
        self.k_noth = no
        self.anyk = self.anyk | (no > 0)
        self.any_key = self.gt[self.anyk]


def load_frames(spec: dict, holdout: bool):
    """Calls / states / writes / calendar for a target or stand-in. Held-out rows only when holdout=True."""
    if holdout:
        import build as B
        calls, _ = B.calls_frame(include_holdout=True, goal_nos=spec["goals"])
        writes = B.writes_frame(include_holdout=True)
    else:
        calls = pl.read_parquet(L.OUT / "calls.parquet").filter(pl.col("goal_no").is_in(spec["goals"]))
        writes = pl.read_parquet(L.OUT / "writes.parquet")
    if spec.get("date_from"):
        calls = calls.filter(pl.col("pt_date") >= spec["date_from"])
    if spec.get("date_to"):
        calls = calls.filter(pl.col("pt_date") < spec["date_to"])
    if spec.get("units"):
        calls = calls.filter(pl.col("unit_id").is_in(spec["units"]) | ~pl.col("goal_no").is_in([4, 5, 6]))
    days = sorted(calls["pt_date"].unique().to_list())
    if not holdout:
        assert not any(L.is_holdout(d, g) for d, g in calls.select("pt_date", "goal_no").unique().iter_rows()), \
            "dry run touched a held-out day"
    calls = kick_counts_r1b(calls)
    hcol = pl.col("holdout") if holdout else ~pl.col("holdout")
    states = (pl.scan_parquet(L.SH / "states_min.parquet").filter(pl.col("pt_date").is_in(days) & hcol)
              .select("pt_date", "minute", "agent", "lump4_min", "in_span", "present").collect())
    writes = writes.filter(pl.col("pt_date").is_in(days)).select("agent", "t")
    cal = (pl.read_parquet(L.SH / "calendar.parquet").filter(pl.col("pt_date").is_in(days))
           .select("pt_date", (pl.col("win_start").dt.epoch("us") / 1e6).alias("win_start"),
                   (pl.col("win_end").dt.epoch("us") / 1e6).alias("win_end")))
    return calls, states, writes, cal


def get(od, *path):
    for p in path:
        if od is None:
            return None
        od = od.get(p) if isinstance(od, dict) else None
    return od


def score_tail(P, rng, B):
    res = L.analyze_class(P, "A", rng, B=B, outcomes=("O2", "O2c"))
    oc, o2 = res["outcomes"].get("O2c", {}), res["outcomes"].get("O2", {})
    out = {"n_primers": get(oc, "E1", "n"), "E1_O2c": oc.get("E1"), "R_pool_O2c": oc.get("R_pool"),
           "batched_O2c": oc.get("batched"), "fit_O2c": oc.get("fit"), "in_O2": get(o2, "by_status", "in")}
    e1 = oc.get("E1") or {}
    r15 = get(oc, "R_pool", "0-15", "R") or {}
    r60 = get(oc, "R_pool", "60-240", "R") or {}
    db = get(oc, "fit", "draw_bins") or {}
    tot = sum(db.values())
    share = (db.get("none", 0) + db.get("0-2", 0)) / tot if tot else None
    c1 = None
    if e1.get("lo") is not None and r15.get("est") is not None:
        c1 = bool(e1["lo"] > 0 and 0.5 <= r15["est"] <= 1.1 and (r15.get("lo") or -9) > 0.3
                  and (r60.get("est") is None or r60["est"] >= 0.7) and (share is None or share >= 0.8))
    bt = get(oc, "batched", "R", "est")
    c2 = None if bt is None else bool(bt <= 0.5)
    rin = get(o2, "by_status", "in", "R", "est")
    c3 = None if rin is None else bool(rin >= 0.4)
    out.update({"share_window_lt_2min": share, "C1": c1, "C2": c2, "C3": c3})
    return out


def score_nudge(P, rng, B):
    res = L.analyze_class(P, "N", rng, B=B, outcomes=("O1", "O1a"))
    o1, o1a = res["outcomes"].get("O1", {}), res["outcomes"].get("O1a", {})
    n = get(o1a, "E1", "n") or 0
    out = {"n_idle_primers": n, "E1_O1": o1.get("E1"), "E1_O1a": o1a.get("E1"), "R_pool_O1a": o1a.get("R_pool")}
    if n < 50:
        out["C4"] = None
        out["why"] = "fewer than 50 idle nudge primers"
        return out
    r = get(o1a, "R_pool", "15-60", "R", "est")
    out["C4"] = bool((get(o1a, "E1", "lo") or -9) > 0 and (get(o1, "E1", "est") or 9) < 0.3 and r is not None and r >= 0.7)
    return out


def score_human(P, rng, B):
    D = L.build_design(P, "H", quiet_s=300)
    out = {"n_primers": int(len(D.get("primer", [])))}
    if not len(D.get("primer", [])):
        out["C5"] = None
        return out
    C = L.day_draws(len(P.days), B, rng)
    e1 = L.e1_table(P, D, "O2c", C)
    out["E1_O2c"] = e1["summary"]
    if e1["summary"]["n"] < 50 or "sec" not in D:
        out["C5"] = None
        out["why"] = "fewer than 50 busy human primers"
        return out
    r, _ = L.ratio_for(P, D, "O2c", (D["d_t"] > 0) & (D["d_t"] <= 2), e1, C)
    out["R_0_2_O2c"] = r
    out["C5"] = bool(e1["summary"]["lo"] > 0 and get(r, "R", "est") is not None and r["R"]["est"] >= 0.7)
    return out


def nudge_block(spec, holdout, rng, B):
    calls, states, writes, cal = load_frames(spec, holdout)
    pooled = score_nudge(PrepR1b(calls, states, writes, cal), rng, B)
    pooled["kick_calls_lead_vs_ment"] = None if holdout else [int((calls["nN"] > 0).sum()), int((calls["nN_ment"] > 0).sum())]
    per = {}
    for g in spec["goals"]:
        sub = calls.filter(pl.col("goal_no") == g)
        if sub.height == 0:
            continue
        d = sub["pt_date"].unique().to_list()
        per[f"G{g:02d}"] = score_nudge(PrepR1b(sub, states.filter(pl.col("pt_date").is_in(d)), writes,
                                               cal.filter(pl.col("pt_date").is_in(d))), rng, B)
    return pooled, per


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--include-ledger-blocked", action="store_true",
                    help="re-enable C4-r1b on #45-#50 (same-family same-modality prior run by H04); Vivian's override only")
    ap.add_argument("--B", type=int, default=L.B_BOOT)
    a = ap.parse_args()
    holdout = bool(a.confirm and a.ack)
    if (a.confirm or a.ack) and not holdout:
        sys.exit("refusing: the confirmatory run needs BOTH --confirm and --i-understand-this-uses-the-locked-holdout")
    gate, blocked = ledger_gate(a.include_ledger_blocked)
    if holdout:
        dirty = subprocess.run(["git", "-C", str(L.ROOT), "status", "--porcelain", "hypotheses/H43-kick-refractory-window"],
                               capture_output=True, text=True).stdout.strip()
        if dirty:
            sys.exit("refusing: commit the H43 card and scripts before the confirmatory run (holdout reuse policy, "
                     "condition 1). Uncommitted:\n" + dirty)
        print("CONFIRMATORY RUN on the locked holdout. Ledger gate:", json.dumps(gate, indent=1))
        print("DISCLOSE in the H43, H02 and H04 cards and LOG.md: #45 (H02, H04) and #46-#50 (H04) carry executed "
              "activity runs; H43 computes second-kick marginal effects at the receiving call.")
    specs = TARGETS if holdout else STANDINS
    rng = np.random.default_rng(L.SEED + 9999)
    t0 = time.time()
    out = {"mode": "confirm (r1b)" if holdout else "dry_run r1b (non-holdout stand-ins)", "specs": specs,
           "nudge_target": "leading @ (infra/shared/idle_gates.leading_targets); non-leading named nudges = nNo",
           "ledger": gate, "git_commit": L.git_commit(), "built_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    calls, states, writes, cal = load_frames(specs["tail"], holdout)
    out["tail"] = score_tail(PrepR1b(calls, states, writes, cal), rng, a.B)
    if blocked["nudge"] and holdout:
        out["nudge_pooled"] = {"C4": None, "why": "blocked by the holdout ledger (H04 kick_response, activity timing)"}
        out["nudge_per_period"] = {}
    else:
        out["nudge_pooled"], out["nudge_per_period"] = nudge_block(specs["nudge"], holdout, rng, a.B)
    if not holdout:
        out["nudge_g51_standin"], _ = nudge_block(STANDIN_NUDGE_G51, False, rng, a.B)
        out["nudge_g51_standin"]["spec"] = STANDIN_NUDGE_G51
    calls, states, writes, cal = load_frames(specs["human"], holdout)
    out["human_pooled"] = score_human(PrepR1b(calls, states, writes, cal), rng, a.B)
    sc = {"C1": out["tail"]["C1"], "C2": out["tail"]["C2"], "C3": out["tail"]["C3"],
          "C4-r1b": out["nudge_pooled"]["C4"], "C5": out["human_pooled"]["C5"]}
    scored = {k: v for k, v in sc.items() if v is not None}
    overall = bool(sc["C1"] and sc["C2"] and (sc["C4-r1b"] or sc["C5"]) and all(scored.values()))
    out["scores"] = {k: ("n/a" if v is None else ("pass" if v else "fail")) for k, v in sc.items()}
    if not holdout:
        c4g = out["nudge_g51_standin"]["C4"]
        out["scores_extra"] = {"C4-r1b on G51 07-27..08-20 stand-in": "n/a" if c4g is None else ("pass" if c4g else "fail")}
    out["overall_no_window_confirmed"] = overall
    out["secs"] = round(time.time() - t0, 1)
    dest = L.OUT / ("confirm_r1b" if holdout else "confirm_r1b_dryrun") / "confirm_results.json"
    L.jdump(out, dest)
    print(out["mode"], out["scores"], out.get("scores_extra", ""), "overall:", overall, f"({out['secs']} s) ->", dest)


if __name__ == "__main__":
    main()
