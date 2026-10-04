"""H36 confirmatory test on the locked holdout, RE-FROZEN ON ROUND-1B INPUTS (written 2026-10-04; NOT RUN).

Re-freeze of `confirm.py` (left byte-for-byte untouched), written before any holdout access. Details in
`CONFIRM_R1B.md`. Inputs switched (round-1b switches of scheme/build.py, set in CFG below):
  * activity: `activity_bins_fixed` and the shared `outages_fixed/outages.parquet` stall mask (data_version = fixed);
  * DQ8 trim: each day cut to its all-present window before the circular-shift surrogates (`_trim` variants); the
    activity-dependent criteria now score the trimmed alarm (C1-r1b, C4-r1b, C5-r1b);
  * content: BOTH models (bge-small; gte-modernbert with its own regime whiteners), window and agent-day vectors without
    restatements (each model's own DQ5 self_repeat flag, chat only; dedupe = restate); R1 on the same vectors;
  * catalog r1b: corrected and new NE dates (class r1b) join the placebo exclusion list; held-out r1b events (NE44)
    join the descriptive C6 table.

Refuses to touch held-out days unless called with BOTH --confirm --i-understand-this-uses-the-locked-holdout, the H36
folder is committed and clean, and infra/shared/holdout_ledger.check() shows no same-family run of the same modality on
a target. Without the flags it DRY-RUNS on non-holdout stand-ins (exploratory kickoffs and placebo days); dry-run
output: --out (default data/processed/H36-reorganization-alarm/r1b/confirm_r1b_dryrun/).

Frozen rules (re-frozen 2026-10-04). Statistics, masks, surrogates, trailing baseline (10 days, Gaussian-consistent
trimmed SD), families and thresholds are h36lib/build.py as in round 1b. In confirm mode the trailing baseline runs
over ALL active days in time order (held-out and not). Targets: goal kickoffs whose day 0 is held out (#9, #14, #15,
#22, #28, #29, #32, #34, #43, #45-#50). Placebos: held-out active days >= 3 active days from every catalogued event.
"Both" = the criterion must pass with bge AND with gte.
- C1-r1b (primary): AUC(Z_phys_trim day 0 vs placebo) >= 0.60 AND hit rate (Z_phys_trim >= 2.0 on days -1..+1) >
  placebo window FAR, both models. (was untrimmed Z_phys, bge; round 1b Z_phys_trim AUC 0.67 / 0.65)
- C2-r1b (primary): AUC(Z_cont day 0) >= 0.65 with bootstrap 95% CI lower bound > 0.5, both models.
  (was bge only; round 1b 0.78 / 0.74)
- C3 (secondary, operator rule): alarm if R1 >= 3.0 or Z_cont >= 2.0 on any of days -1..+1: hit rate >= 0.40 AND
  placebo window FAR <= 0.10, bge (unchanged; gte reported: round 1b gte FAR 0.13).
- C4-r1b (secondary): AUC(R1 day 0) > AUC(Z_phys_trim day 0), both models.
- C5-r1b (secondary): AUC(Z_act_trim day 0) <= 0.65 (bge; activity is model-free). (was untrimmed Z_act; 1b 0.50)
- C6 (descriptive): alarm table for held-out NEs (as before, plus held-out class-r1b events: NE44).
Overall: CONFIRMED if C1-r1b and C2-r1b pass; PARTIAL if exactly one passes; NOT CONFIRMED otherwise.
Expectation from round 1b (not a criterion): C2-r1b passes; C1-r1b at its boundary (random-date p 0.08 / 0.21).

Reuse (ledger L221-L238): no prior run of H36's statistics on any target. H04 (kick-response, activity timing) ran on
#45-#50 and NE21+NE23, H05 (room couplings, activity) on #32, #34, NE12, NE30; H02 on #45. H36 computes a different
statistic (within-day surrogate-excess co-fluctuation, trailing z), so policy item 2 holds; the ledger's family tag for
H36 ("kick_response") comes from the word "kickoff" and needs the human pass. Disclose in the cards and LOG.md.

Usage: uv run python hypotheses/H36-reorganization-alarm/analysis/confirm_r1b.py [--out DIR]   # dry run (non-holdout)
       uv run python hypotheses/H36-reorganization-alarm/analysis/confirm_r1b.py --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h36lib as L  # noqa: E402
import build as B  # noqa: E402
import evaluate as E  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HYP = "H36"
GOAL_TARGETS_HOLDOUT = [9, 14, 15, 22, 28, 29, 32, 34, 43, 45, 46, 47, 48, 49, 50]
NE_TARGETS_HOLDOUT = ["NE12", "NE35", "NE-voted-out", "NE30", "NE13", "NE14", "NE19", "NE20", "NE21", "NE22", "NE23",
                      "NE24", "NE25", "NE26", "NE37", "NE01", "NE05", "NE08"]
RULES = {"C1_auc": 0.60, "C2_auc": 0.65, "C3_hit": 0.40, "C3_far": 0.10, "C5_auc": 0.65}
MODELS = ("bge_small", "gte_modernbert")
LEDGER_T = [f"G{g:02d}" for g in GOAL_TARGETS_HOLDOUT] + ["NE12", "NE30", "NE21+NE23"]


def ledger_gate(strict: bool) -> list[str]:
    sys.path.insert(0, str(L.ROOT))
    from infra.shared import holdout_ledger as hl
    led = hl.load()
    bad = []
    for t in LEDGER_T:
        mine = [e for e in led["entries"] if e["hypothesis"] == HYP and e["target"] == t]
        mod = mine[0]["modality"] if mine else "message content"
        fam = sorted({f for e in mine for f in e["estimator_family"]}) or ["content_alignment"]
        r = hl.check(HYP, t, mod, fam)
        same_mod = sorted({u["hypothesis"] for u in r["prior_runs_same_family"] if u["modality"] == mod})
        print(f"ledger {t} [{mod}]: allowed={r['allowed']} same_family_same_modality_runs={same_mod} "
              f"prior_runs={sorted({u['hypothesis'] for u in r['prior_runs']})} "
              f"n_competing_planned={len({u['hypothesis'] for u in r['competing_planned']})}", flush=True)
        if same_mod:
            bad.append(f"{t}: {same_mod}")
    return bad if strict else []


def day_scores(model: str, days: pl.DataFrame, cal: pl.DataFrame, confirm: bool, workers: int):
    """Build the per-day statistics for one embedding model with the round-1b switches; return (st, sc, meta)."""
    B.CFG.update(data_version="fixed", model=model, dedupe="restate", trim=True)
    payloads, use_h38, h38prov, cons = B.make_payloads(days)
    with ProcessPoolExecutor(max_workers=min(2, workers)) as ex:
        res = list(ex.map(B.day_worker, payloads, chunksize=4))
    st = pl.DataFrame(res, infer_schema_length=None)
    base = days.select("aday", "pt_date", "goal_no", "regime", "weekday", "gap_days", "monday", "window_s", "documented_hours", "holdout")
    st = base.join(st, on="aday", how="inner").join(cons, on="pt_date", how="left").sort("aday")
    st = B.add_rivals(st, cal, days["pt_date"].to_list(), allow_holdout_prev=confirm)
    if not confirm:
        assert not st["holdout"].any()
    return st, E.compute_scores(st), {"mask": "outages_fixed" if use_h38 else "fallback", "built_at": h38prov}


def evaluate_model(st, sc, ev, allev, confirm, rng) -> dict:
    aday = st["aday"].to_numpy(); pos = {int(x): i for i, x in enumerate(aday)}
    hold = st["holdout"].to_numpy()
    ev_days = np.unique(allev["aday0"].drop_nulls().to_numpy())
    dist = np.array([np.min(np.abs(ev_days - x)) for x in aday])
    okz = np.isfinite(sc["Z_phys_trim"])
    role = hold if confirm else ~hold
    placebo = role & (dist >= L.PLACEBO_DIST) & okz
    if confirm:
        tg = ev.filter((pl.col("cls") == "goal") & pl.col("ref").is_in([f"#{g}" for g in GOAL_TARGETS_HOLDOUT]))
    else:
        tg = ev.filter((pl.col("cls") == "goal") & ~pl.col("holdout0"))

    def v(k, c):
        i = pos.get(int(c))
        return np.nan if i is None else float(sc[k][i])

    def win(k, c, thr):
        vals = [v(k, c + o) for o in (-1, 0, 1)]
        fin = [x for x in vals if np.isfinite(x)]
        return (any(x >= thr for x in fin), len(fin))

    def rule3(c):
        return any((v("R1", c + o) >= 3.0) or (v("Z_cont", c + o) >= 2.0) for o in (-1, 0, 1))

    cent = tg["aday0"].drop_nulls().to_list()
    keys = ["Z_phys", "Z_phys_trim", "Z_cont", "Z_act", "Z_act_trim", "R1"]
    d0 = {k: np.array([v(k, c) for c in cent]) for k in keys}
    pc = aday[placebo]
    out = {"n_targets": len(cent), "n_placebo": int(placebo.sum())}
    for k in keys:
        out[f"auc_{k}"] = L.auc(d0[k], sc[k][placebo])
        out[f"auc_{k}_ci"] = L.auc_ci(d0[k], sc[k][placebo], rng, 2000)
    for k in ("Z_phys", "Z_phys_trim"):
        hits = [win(k, c, 2.0) for c in cent]
        out[f"hit_{k}"] = float(np.mean([h for h, n in hits if n])) if any(n for _, n in hits) else float("nan")
        out[f"far_win_{k}"] = float(np.mean([win(k, c, 2.0)[0] for c in pc])) if len(pc) else float("nan")
    out["C3_hit"] = float(np.mean([rule3(c) for c in cent])) if cent else float("nan")
    out["C3_far_win"] = float(np.mean([rule3(c) for c in pc])) if len(pc) else float("nan")
    out["C1"] = bool(out["auc_Z_phys_trim"] >= RULES["C1_auc"] and out["hit_Z_phys_trim"] > out["far_win_Z_phys_trim"])
    out["C1_untrimmed_r1_rule"] = bool(out["auc_Z_phys"] >= RULES["C1_auc"] and out["hit_Z_phys"] > out["far_win_Z_phys"])
    out["C2"] = bool(out["auc_Z_cont"] >= RULES["C2_auc"] and out["auc_Z_cont_ci"][0] > 0.5)
    out["C3"] = bool(out["C3_hit"] >= RULES["C3_hit"] and out["C3_far_win"] <= RULES["C3_far"])
    out["C4"] = bool(out["auc_R1"] > out["auc_Z_phys_trim"])
    out["C5"] = bool(out["auc_Z_act_trim"] <= RULES["C5_auc"])
    netab = []
    if confirm:
        sub = ev.filter(pl.col("ref").is_in(NE_TARGETS_HOLDOUT) | ((pl.col("cls") == "r1b") & pl.col("holdout0").fill_null(False)))
    else:
        sub = ev.filter(pl.col("cls").is_in(["room", "scaffold", "r1b"]) & ~pl.col("holdout0").fill_null(True))
    for r in sub.iter_rows(named=True):
        c = r["aday0"]
        if c is None:
            continue
        netab.append({"ref": r["ref"], "pt_date0": r["pt_date0"], "Z_phys_trim": [v("Z_phys_trim", c + o) for o in (-1, 0, 1)],
                      "Z_cont": [v("Z_cont", c + o) for o in (-1, 0, 1)], "R1": [v("R1", c + o) for o in (-1, 0, 1)],
                      "alarm": win("Z_phys_trim", c, 2.0)[0], "rule3": rule3(c)})
    out["C6"] = netab
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--out", type=Path, default=None, help="dry-run output directory")
    a = ap.parse_args()
    confirm = a.confirm and a.ack
    if a.confirm != a.ack:
        sys.exit("refusing: the confirmatory run needs BOTH --confirm and --i-understand-this-uses-the-locked-holdout")
    if confirm:
        dirty = subprocess.run(["git", "-C", str(L.ROOT), "status", "--porcelain", "--", "hypotheses/H36-reorganization-alarm"],
                               capture_output=True, text=True).stdout.strip()
        if dirty:
            sys.exit("refusing: commit the H36 card, confirm_r1b.py and CONFIRM_R1B.md before the holdout run")
    bad = ledger_gate(strict=confirm)
    if bad:
        sys.exit("refusing (holdout ledger, same family and modality): " + "; ".join(bad))
    out_dir = L.OUT / "r1b" / "confirm_r1b" if confirm else (a.out or L.OUT / "r1b" / "confirm_r1b_dryrun")
    out_dir.mkdir(parents=True, exist_ok=True)
    B.R1B_CATALOG = True
    cal = B.calendar()
    ev, allev = B.catalog(cal)
    if confirm:
        print("CONFIRMATORY r1b RUN on the locked holdout (reuse policy: see docstring).")
        days = cal.filter(pl.col("goal_no") > 0)
    else:
        print("DRY RUN r1b on non-holdout stand-ins (no held-out day is read).", flush=True)
        days = cal.filter(~pl.col("holdout") & (pl.col("goal_no") > 0))
        assert not any(L.holdout_mask(days["pt_date"].to_list(), days["goal_no"].to_list()))
    res = {"mode": "confirm_r1b" if confirm else "dryrun_r1b", "rules": RULES}
    for m in MODELS:
        st, sc, meta = day_scores(m, days, cal, confirm, a.workers)
        res[m] = evaluate_model(st, sc, ev, allev, confirm, np.random.default_rng(L.SEED + 99)) | meta
        print(m, {k: res[m][k] for k in ("auc_Z_phys_trim", "auc_Z_cont", "auc_R1", "auc_Z_act_trim", "C1", "C2")}, flush=True)
    b, g = res["bge_small"], res["gte_modernbert"]
    res["C1_r1b"] = bool(b["C1"] and g["C1"])
    res["C2_r1b"] = bool(b["C2"] and g["C2"])
    res["C3"] = bool(b["C3"]); res["C3_gte"] = bool(g["C3"])
    res["C4_r1b"] = bool(b["C4"] and g["C4"])
    res["C5_r1b"] = bool(b["C5"])
    res["overall"] = ("CONFIRMED" if res["C1_r1b"] and res["C2_r1b"] else
                      "PARTIAL" if res["C1_r1b"] or res["C2_r1b"] else "NOT CONFIRMED")
    fin = lambda o: None if isinstance(o, float) and not np.isfinite(o) else str(o)  # noqa: E731
    (out_dir / "confirm_r1b.json").write_text(json.dumps(res, indent=1, default=fin))
    L.write_provenance(f"hypotheses/H36-reorganization-alarm/analysis/confirm_r1b.py ({res['mode']})",
                       ["activity_bins_fixed", "outages_fixed/outages", "calendar", "kicks", "rooms", "rooms_timeline",
                        "embeddings (bge_small, gte_modernbert)", "statement_flags"],
                       {"mode": res["mode"], "rules": RULES, "cfg": "fixed, restate, trim, catalog r1b"},
                       path=out_dir / "_provenance.json")
    print(json.dumps({k: v_ for k, v_ in res.items() if k not in MODELS}, indent=1, default=str))


if __name__ == "__main__":
    main()
