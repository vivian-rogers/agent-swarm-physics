"""H38 confirmatory test on the LOCKED HOLDOUT, RE-FROZEN ON ROUND-1B INPUTS. Written 2026-10-04; NOT RUN.

Re-freeze of `confirm.py` (left byte-for-byte untouched), written before any holdout access. Details in
`CONFIRM_R1B.md`. Inputs switched (round-1b `--data-version fixed` path of run_period.py / h38lib.py):
  * activity: DQ8 `activity_bins_fixed` instead of `activity_bins` (which dropped about half of all events);
  * stalls: the shared `outages_fixed/{outages,stall_minutes,reasons}` sidecar (H38's outage rule on the fixed table;
    all days kept, holdout flagged);
  * DQ8 null: O4 `trim*` variants (rows outside the all-present window removed BEFORE the block-shift surrogates); the
    whole-day N1 null rejects 28-34% of independent swarms, the trimmed one 2-4%. New criteria C1t-r1b, C2t-r1b,
    C5t-r1b score the trimmed decomposition next to the unchanged C1-C6.
Infra bursts keep H38's own platform-error categories (`turn_errors` / `error_class`; Known issues 18, 56): these are
platform failures, not task failures, so `turn_outcomes.failed` does not apply. No content, nudges or work enter H38.

Refuses to touch held-out data unless called with BOTH flags:
    uv run python hypotheses/H38-platform-stalls/analysis/confirm_r1b.py --confirm --i-understand-this-uses-the-locked-holdout [--skip-blocked]
and only if the H38 folder is committed and clean and infra/shared/holdout_ledger.check() finds no same-family,
same-modality prior run on a target. The ledger blocks #45 (H02's Curie-Weiss betaJ0) and #46, #47, #49, #50 (H04's
NE21+NE23 run, tagged curie_weiss_gain), and #34 (H05). C6's NE21 weeks are #46-#49 days, so C6 is dropped whenever
any of those is blocked. `--skip-blocked` drops blocked targets (criteria needing them become n/a);
without it the script refuses. Using it, or overriding the ledger, is Vivian's decision.
Dry run (same code, non-holdout stand-ins):
    uv run python hypotheses/H38-platform-stalls/analysis/confirm_r1b.py --dry-run [--out DIR]

Frozen predictions (re-frozen 2026-10-04; f_v = 1 - E_v / E_raw, E = excess over the block-shift null):
  C1  regime III: in held-out regime-III periods with z_raw > 2 vs N1, median f_scaffold >= 0.5 and median
      f_edge >= 0.4. (unchanged; round 1b f_scaffold III 0.72)
  C1t-r1b regime III (new, DQ8 null): over the same periods, median f_trim >= 0.5 (round 1b 0.83), and at most half of
      all held-out regime-III periods keep z_trim > 2 (round 1b 3/8).
  C2  regime I: in held-out regime-I periods with z_raw > 2, median f_scaffold < 0.35. (unchanged; 1b 0.11)
  C2t-r1b regime I (new): over the same periods, median f_trim < 0.35 (1b 0.11).
  C3  the regime III - I difference in mean g_eq active shrinks by >= 50% under mask_scaffold. (unchanged)
  C4  median log OR(JS | infra burst in [t-10, t-1]) < 0 over held-out periods with >= 20 burst minutes. (unchanged;
      1b -0.96)
  C5  in held-out periods with z_raw(talk) > 2, median talk f_scaffold < 0.3. (unchanged)
  C5t-r1b (new): in held-out periods with z_trim(talk) > 2, median talk f_trim < 0.3 (1b 0.03; talk is coupling).
  C6  NE21 (8 h / 4 h / 8 h weeks): E_raw - E_mask_edge smaller in each 8-h week than in the 4-h week. (unchanged)
Holdout reuse: #45 used by H02 (activity couplings, CW betaJ0) and H04; #46-#50 by H04 (NE21+NE23); #32, #34 by H05.
H38's cause composition and stall-adjusted excess are different statistics; the ledger still tags the gain family as
shared with H02/H04 (curie_weiss_gain), and ledger item 5 notes H19 plans the same equal-time gain on 9 targets.
"""
from __future__ import annotations

import os
import sys

os.environ["H38_DATA_VERSION"] = "fixed"     # must precede the h38lib import (inherited by spawned workers)
sys.dont_write_bytecode = True

import argparse  # noqa: E402
import json  # noqa: E402
import subprocess  # noqa: E402
from pathlib import Path  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h38lib as L  # noqa: E402
import run_period as RP  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

assert L.DATA_VERSION == "fixed"
HYP = "H38"
FLAG = "--i-understand-this-uses-the-locked-holdout"
HELD = {"III": [45, 46, 47, 49, 50], "I": [1, 9, 14, 15, 22, 28, 29], "II": [32, 34]}
STANDIN = {"III": [39, 40, 41], "I": [10, 17, 18], "II": [35]}
NE21 = {"8h_a": ("2026-06-08", "2026-06-13"), "4h": ("2026-06-15", "2026-06-27"), "8h_b": ("2026-06-29", "2026-07-04")}
NE21_STANDIN = {"8h_a": ("2026-07-06", "2026-07-11"), "4h": ("2026-05-11", "2026-05-23"), "8h_b": ("2026-07-13", "2026-07-18")}
N_SURR = 200


def days_of(g: int, allow_holdout: bool) -> list[str]:
    cal = pl.read_parquet(L.SH / "calendar.parquet").filter(pl.col("goal_no") == g).sort("pt_date")
    if not allow_holdout:
        cal = cal.filter(~pl.col("holdout"))
        assert not cal["holdout"].any()
    return cal["pt_date"].to_list()


def days_between(a: str, b: str, allow_holdout: bool) -> list[str]:
    cal = pl.read_parquet(L.SH / "calendar.parquet").filter((pl.col("pt_date") >= a) & (pl.col("pt_date") < b)).sort("pt_date")
    if not allow_holdout:
        cal = cal.filter(~pl.col("holdout"))
        assert not cal["holdout"].any()
    return cal["pt_date"].to_list()


def period_stats(days: list[str], rng) -> dict:
    ab, sm = RP.load(days)
    o4 = RP.o4_gains(ab, sm, days, rng, N_SURR)
    o1 = RP.o123(ab, sm, days, rng, 100)
    if o4 is None:
        return {"days": len(days), "ok": False}
    a, t = o4["active"], o4.get("talk", {})
    f = lambda v, src=a: 1 - src[v]["E"] / src["raw"]["E"] if (src.get("raw", {}).get("E", 0) > 0 and v in src) else np.nan  # noqa: E731
    return {"days": len(days), "ok": True, "g_raw": a["raw"]["g"], "E_raw": a["raw"]["E"], "z_raw": a["raw"]["z"],
            "E_mask_edge": a["mask_edge"]["E"], "E_mask_scaffold": a["mask_scaffold"]["E"], "g_mask_scaffold": a["mask_scaffold"]["g"],
            "z_mask_scaffold": a["mask_scaffold"]["z"], "f_scaffold": f("mask_scaffold"), "f_edge": f("mask_edge"),
            "f_trim": f("trim"), "z_trim": a.get("trim", {}).get("z", np.nan), "E_trim": a.get("trim", {}).get("E", np.nan),
            "t_E_raw": t.get("raw", {}).get("E"), "t_z_raw": t.get("raw", {}).get("z"),
            "t_f_scaffold": f("mask_scaffold", t) if t else np.nan,
            "t_f_trim": f("trim", t) if t else np.nan, "t_z_trim": t.get("trim", {}).get("z") if t else None,
            "burst_lor": (o1 or {}).get("burst_logOR"), "n_burst": (o1 or {}).get("n_burst_min"),
            "cause_shares": (o1 or {}).get("cause_shares"), "js_share": (o1 or {}).get("js_share")}


def evaluate(P: dict, W: dict) -> dict:
    out = {}
    med = lambda xs: float(np.nanmedian(xs)) if xs else np.nan  # noqa: E731
    all3 = [x for x in P.values() if x["regime"] == "III" and x["ok"]]
    r3 = [x for x in all3 if x["z_raw"] > 2]
    r1 = [x for x in P.values() if x["regime"] == "I" and x["ok"] and x["z_raw"] > 2]
    out["C1"] = {"n": len(r3), "median_f_scaffold": med([x["f_scaffold"] for x in r3]), "median_f_edge": med([x["f_edge"] for x in r3])}
    out["C1"]["pass"] = bool(r3) and out["C1"]["median_f_scaffold"] >= 0.5 and out["C1"]["median_f_edge"] >= 0.4
    ztr = [x["z_trim"] for x in all3 if np.isfinite(x["z_trim"])]
    out["C1t_r1b"] = {"n": len(r3), "median_f_trim": med([x["f_trim"] for x in r3]),
                      "n_sig_trim": int(sum(z > 2 for z in ztr)), "n_regime_III": len(ztr)}
    out["C1t_r1b"]["pass"] = (bool(r3) and out["C1t_r1b"]["median_f_trim"] >= 0.5
                              and out["C1t_r1b"]["n_sig_trim"] <= len(ztr) / 2) if ztr else None
    out["C2"] = {"n": len(r1), "median_f_scaffold": med([x["f_scaffold"] for x in r1])}
    out["C2"]["pass"] = bool(r1) and out["C2"]["median_f_scaffold"] < 0.35
    out["C2t_r1b"] = {"n": len(r1), "median_f_trim": med([x["f_trim"] for x in r1])}
    out["C2t_r1b"]["pass"] = bool(r1) and out["C2t_r1b"]["median_f_trim"] < 0.35
    g1 = [x for x in P.values() if x["regime"] == "I" and x["ok"]]
    if all3 and g1:
        d_raw = np.mean([x["g_raw"] for x in all3]) - np.mean([x["g_raw"] for x in g1])
        d_adj = np.mean([x["g_mask_scaffold"] for x in all3]) - np.mean([x["g_mask_scaffold"] for x in g1])
        out["C3"] = {"diff_raw": float(d_raw), "diff_mask_scaffold": float(d_adj), "shrink": float(1 - d_adj / d_raw) if d_raw else np.nan}
        out["C3"]["pass"] = bool(d_raw > 0 and out["C3"]["shrink"] >= 0.5)
    else:
        out["C3"] = {"pass": None, "note": "n/a (needs regime III and I targets)"}
    b = [x for x in P.values() if x["ok"] and (x["n_burst"] or 0) >= 20 and x["burst_lor"] is not None]
    out["C4"] = {"n": len(b), "median_lor": med([x["burst_lor"] for x in b])}
    out["C4"]["pass"] = bool(b) and out["C4"]["median_lor"] < 0
    tt = [x for x in P.values() if x["ok"] and x["t_z_raw"] is not None and x["t_z_raw"] > 2]
    out["C5"] = {"n": len(tt), "median_talk_f_scaffold": med([x["t_f_scaffold"] for x in tt])}
    out["C5"]["pass"] = bool(tt) and out["C5"]["median_talk_f_scaffold"] < 0.3
    t2 = [x for x in P.values() if x["ok"] and x["t_z_trim"] is not None and np.isfinite(x["t_z_trim"]) and x["t_z_trim"] > 2]
    out["C5t_r1b"] = {"n": len(t2), "median_talk_f_trim": med([x["t_f_trim"] for x in t2])}
    out["C5t_r1b"]["pass"] = bool(t2) and out["C5t_r1b"]["median_talk_f_trim"] < 0.3
    if all(k in W and W[k]["ok"] for k in NE21):
        ei = {k: W[k]["E_raw"] - W[k]["E_mask_edge"] for k in NE21}
        out["C6"] = {"edge_excess": ei, "pass": bool(ei["8h_a"] < ei["4h"] and ei["8h_b"] < ei["4h"])}
    else:
        out["C6"] = {"pass": None, "note": "n/a"}
    return out


def ledger_blocked(targets: list[str]) -> list[str]:
    sys.path.insert(0, str(L.ROOT))
    from infra.shared import holdout_ledger as hl
    led = hl.load()
    bad = []
    for t in targets:
        mine = [e for e in led["entries"] if e["hypothesis"] == HYP and e["target"] == t]
        mod = mine[0]["modality"] if mine else "activity timing"
        fam = sorted({f for e in mine for f in e["estimator_family"]}) or ["curie_weiss_gain"]
        r = hl.check(HYP, t, mod, fam)
        same_mod = sorted({u["hypothesis"] for u in r["prior_runs_same_family"] if u["modality"] == mod})
        print(f"ledger {t} [{mod}]: allowed={r['allowed']} same_family_same_modality_runs={same_mod} "
              f"prior_runs={sorted({u['hypothesis'] for u in r['prior_runs']})} "
              f"competing_planned={sorted({u['hypothesis'] for u in r['competing_planned']})}", flush=True)
        if same_mod:
            bad.append(t)
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument(FLAG, dest="understand", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-blocked", action="store_true", help="confirm only: drop ledger-blocked targets (Vivian's call)")
    ap.add_argument("--out", type=Path, default=None, help="dry-run output directory")
    a = ap.parse_args()
    if a.confirm and not a.understand:
        sys.exit(f"Refusing: --confirm also needs {FLAG}.")
    if not a.confirm and not a.dry_run:
        sys.exit(f"Nothing to do. Use --dry-run (non-holdout stand-ins) or --confirm {FLAG} (locked holdout).")
    live = a.confirm and a.understand
    ltargets = [f"G{g:02d}" for gs in HELD.values() for g in gs] + ["NE21+NE23"]
    blocked = ledger_blocked(ltargets)
    sets, weeks = (HELD, NE21) if live else (STANDIN, NE21_STANDIN)
    if live:
        dirty = subprocess.run(["git", "-C", str(L.ROOT), "status", "--porcelain", "--", "hypotheses/H38-platform-stalls"],
                               capture_output=True, text=True).stdout.strip()
        if dirty:
            sys.exit("Refusing: commit the H38 card, confirm_r1b.py and CONFIRM_R1B.md before the holdout run.")
        if blocked and not a.skip_blocked:
            sys.exit(f"Refusing (holdout ledger, same family and modality): {blocked}. Re-run with --skip-blocked only on "
                     "Vivian's decision.")
        sets = {reg: [g for g in gs if f"G{g:02d}" not in blocked] for reg, gs in sets.items()}
        if "NE21+NE23" in blocked or {"G46", "G47", "G48", "G49"} & set(blocked):
            weeks = {}      # the NE21 weeks are #46-#49 days: blocked with those periods (the NE tag alone passes)
    out_dir = L.DATA / "r1b" / "confirm_r1b" if live else (a.out or L.DATA / "r1b" / "confirm_r1b_dryrun")
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng([L.SEED, 9092 if live else 9093])
    P = {}
    for reg, gs in sets.items():
        for g in gs:
            d = days_of(g, allow_holdout=live)
            if not d:
                continue
            st = period_stats(d, rng)
            st["regime"] = reg
            P[f"G{g:02d}"] = st
            print(f"G{g:02d} ({reg}): z_raw {st.get('z_raw', float('nan')):.1f}, f_scaffold {st.get('f_scaffold', float('nan')):.2f}, "
                  f"f_trim {st.get('f_trim', float('nan')):.2f}", flush=True)
    W = {}
    for k, (s, e) in weeks.items():
        d = days_between(s, e, allow_holdout=live)
        W[k] = period_stats(d, rng) if d else {"ok": False}
    res = {"live": live, "data_version": L.DATA_VERSION, "blocked_skipped": blocked if live else [],
           "periods": P, "ne21_weeks": W, "evaluation": evaluate(P, W)}
    (out_dir / "result_r1b.json").write_text(json.dumps(res, indent=1, default=lambda x: float(x) if isinstance(x, (np.floating, np.integer)) else str(x)))
    print(json.dumps(res["evaluation"], indent=1, default=float))


if __name__ == "__main__":
    main()
