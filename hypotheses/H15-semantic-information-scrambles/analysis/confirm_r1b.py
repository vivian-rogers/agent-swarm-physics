"""H15 confirmatory test on the LOCKED HOLDOUT -- ROUND-1B RE-FREEZE of `confirm_ne30.py`. Written 2026-10-04 after
round 1b, before any holdout outcome was computed. NOT RUN. `confirm_ne30.py` stays byte-for-byte unchanged.

Refuses to touch holdout data unless BOTH flags are given:
    --confirm --i-understand-this-uses-the-locked-holdout
`--dry-run` runs the identical pipeline on non-holdout stand-ins (the round-1b exploratory tables).

What changes vs confirm_ne30.py (inputs only, via H15_ROUND=r1b, set below before any H15 import):
  * V_eng from activity_bins_fixed (not the buggy activity_bins);
  * V_rel = 1 - real-failure fraction (DQ3 turn_outcomes.failed; error_class platform failures on GUI turns), not
    actions.error (stderr);
  * V_out = DQ4 agent work commits per window hour (canonical & ~imported & author_kind == agent & ~automated);
  * context erasures from the DQ1 ledger (reset_forced vs reset_consol, per-call timing), outcome per call = work
    commits mapped forward <= 10 min (round 1: H15's own turn counts and write turns);
  * V* re-chosen by the pre-registered D2.6 rule on the corrected candidates (round 1b): regime I (and II, by the
    regime-II rule) V_eng, regime III V_rel.
  Leading-@ targets, embeddings and the DQ8 trim are not inputs of this design (no nudge, content or synchrony term).
  The scramble catalog (ML, MG, MR, MN, CC) is unchanged by round 1b except where it reads V*.

Re-frozen criteria (ids kept where unchanged; "-r1b" = changed because round 1b changed the input or the result):
  C1-r1b  NE30 successor (Gemini 3.1 Pro, regime II): deficit z > -2 on V_eng (the new V* for regime II) AND on V_rel
          (now real failures). Refutation-only, as before. Reason: V* and V_rel changed definition.
  C2-r1b  NE33 batch join: period-mean deficit z > -2 on V_rel (the new V* for regime III) AND on V_eng.
          Refutation-only. Reason: V*(III) moved from V_eng to V_rel.
  C3-r1b  Context erasure on the ledger: in every holdout regime-III unit with >= 200 forced resets, WORK COMMITS per
          call in calls +1..+10 after a forced reset fall relative to calls -20..-11 of the preceding segment;
          DerSimonian-Laird meta of the per-unit relative dip <= -0.25 with 95% CI below 0, AND per-unit CI below 0 in
          >= 2/3 of those units. Reason: round 1 measured write turns on H15's own turn clock; round 1b replicated the
          dip on independent timing (ledger) and output (git) data: -0.39 [-0.42, -0.35], 7/9 periods.
  C4      Memory loss (ML) on V*: meta dV is NOT <= -0.3 SD with z <= -2. Inconclusive with < 2 units. (Unchanged rule;
          V* per regime as above.)
  C5      Check only (unchanged): forced-minus-voluntary post-reset dip vs the agent-day base > 0 (round 1b: weaker on
          work commits, CI > 0 in 2/9).
  C3e     Descriptive (new, not a criterion): the real-failure rate after a forced reset (calls +1..+10 vs -20..-11);
          round 1b +0.27 [+0.12, +0.42].
Overall (unchanged rule): CONFIRMED if C3-r1b and C4 pass and neither C1-r1b nor C2-r1b refutes; REFUTED if C3-r1b
fails, C4's opposite holds, or C1-r1b/C2-r1b show a significant deficit; INCONCLUSIVE otherwise.

Holdout reuse: infra/shared/holdout_ledger.check() is called for every target before the confirm build (NE30, #43,
#45-#50, NE21+NE23, #51-tail). H04 ran activity timing on #45-#50 and H05 talk on NE30's #34 days: this script's
statistics are within-agent scramble responses on V* and work commits (a different statistic); disclose in both
cards and LOG.md. H01's confirm_r2.py plans crew-level continuity on NE30 and work output on #43-#51 tail.

Usage:
  uv run python hypotheses/H15-semantic-information-scrambles/analysis/confirm_r1b.py --dry-run
  ... --confirm --i-understand-this-uses-the-locked-holdout        # CONSUMES THE HOLDOUT; needs sign-off
"""
from __future__ import annotations

import os

os.environ["H15_ROUND"] = "r1b"           # corrected inputs; must be set before h15common is imported
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
import h15common as C  # noqa: E402
import confirm_ne30 as CN  # noqa: E402  (frozen helpers: newcomer_deficits, ml_meta, ctx_tests, full_calendar)
from h15lib import dl_meta  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

assert C.ROUND == "r1b", "H15_ROUND must be r1b before h15common is imported"
V_STAR_R1B = {"I": "V_eng", "II": "V_eng", "III": "V_rel"}      # round-1b D2.6 choice (r1b/v_choice.json)
CN.V_STAR = V_STAR_R1B                                           # ml_meta reads the module-level V_STAR
HOLDOUT_UNITS_III = ["43", "45", "46", "47", "48", "49", "50", "51"]
LEDGER_TARGETS = ["NE30", "G34", "G43", "G45", "G46", "G47", "G48", "G49", "G50", "NE21+NE23", "#51-tail"]

FROZEN = {
    "frozen_on": "2026-10-04 (round-1b re-freeze of confirm_ne30.py; no holdout data read)",
    "V_star": V_STAR_R1B,
    "C1-r1b": "NE30 successor deficit z > -2 on V_eng AND V_rel (refutation-only)",
    "C2-r1b": "NE33 batch deficit z > -2 on V_rel AND V_eng (refutation-only)",
    "C3-r1b": "forced-reset work-commit dip (calls +1..+10 vs -20..-11): DL meta <= -0.25, CI < 0, per-unit CI < 0 in >= 2/3 "
              "of holdout regime-III units with >= 200 forced resets",
    "C4": "ML meta dV on V* not (<= -0.3 SD and z <= -2); inconclusive if < 2 units",
    "C5": "check: CF - CV vs agent-day base > 0",
    "C3e": "descriptive: real-failure rate change after forced resets",
}


def ledger_checks():
    sys.path.insert(0, str(C.ROOT / "infra/shared"))
    import holdout_ledger as HL
    out = {}
    for t in LEDGER_TARGETS:
        c = HL.check("H15", t, "work ledger x context ledger", ["behavior_states", "work_output"])
        out[t] = {"allowed": c["allowed"], "needs_disclosure": c["needs_disclosure"],
                  "prior_runs": sorted({u["hypothesis"] for u in c["prior_runs"]}),
                  "prior_runs_same_family": sorted({u["hypothesis"] for u in c["prior_runs_same_family"]}),
                  "competing_planned": sorted({u["hypothesis"] for u in c["competing_planned"]})}
    return out


def fail_dip(ce, units, rng):
    """C3e: relative change of the real-failure rate after forced resets (e_post vs e_far), cluster bootstrap."""
    c = (ce.filter((pl.col("kind") == "CF") & (pl.col("n_far") >= 10) & (pl.col("n_post") >= 10))
         .with_columns((pl.col("agent").cast(pl.Utf8) + "_" + pl.col("pt_date")).alias("cl")))
    res = {}
    for u in units:
        g = c.filter(pl.col("unit") == u)
        if g.height < 200:
            continue
        uu, inv = np.unique(g["cl"].to_numpy(), return_inverse=True)
        sp = np.bincount(inv, weights=g["e_post"].fill_null(0).to_numpy())
        sf = np.bincount(inv, weights=g["e_far"].fill_null(0).to_numpy())
        est = sp.sum() / max(sf.sum(), 1e-12) - 1
        bs = [sp[ii].sum() / max(sf[ii].sum(), 1e-12) - 1 for ii in (rng.integers(0, len(uu), len(uu)) for _ in range(500))]
        res[u] = {"rel": float(est), "se": float(np.std(bs, ddof=1))}
    return dl_meta([v["rel"] for v in res.values()], [v["se"] for v in res.values()]), res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.dry_run and (a.confirm or a.ack):
        raise SystemExit("choose either --dry-run or the two confirmation flags, not both")
    if not a.dry_run and not (a.confirm and a.ack):
        raise SystemExit("REFUSED: this script uses the locked holdout (NE30, NE33 tail, #43, #45-#50, #51 tail).\n"
                         "Run with --dry-run on non-holdout stand-ins, or with BOTH --confirm and "
                         "--i-understand-this-uses-the-locked-holdout once Vivian has signed off.")
    mode = "dry" if a.dry_run else "confirm"
    led = ledger_checks()
    if mode == "confirm":
        blocked = [t for t, c in led.items() if not c["allowed"]]
        if blocked:
            raise SystemExit(f"holdout_ledger.check refuses {blocked} (same-family prior run); resolve before running.")
    rng = np.random.default_rng(C.SEED)
    ad, cat, ce, cal = CN.load_tables(mode)        # r1b tables (dry) or the r1b build on the full calendar (confirm)
    roster = pl.read_parquet(C.SH / "roster.parquet")
    code = {n: int(c) for c, n in roster.select("agent", "name").rows()}
    if mode == "dry":
        c1_agents = [code["GPT-5.4"]]
        c2_agents = [code["GPT-5.6 Sol"], code["GPT-5.6 Terra"], code["GPT-5.6 Luna"]]
        u3 = ["36b", "37", "38", "39", "40", "41", "42", "44", "51"]
        hd = C.holdout_days()
        assert not set(ad["pt_date"].to_list()) & set(hd), "dry run touched a holdout day"
        u4 = sorted(set(cat.filter(pl.col("type") == "ML")["unit"].to_list()))
    else:
        c1_agents = [code["Gemini 3.1 Pro"]]
        c2_agents = [code["Muse Spark 1.3"], code["Gemini 3.8 Flash"], code["GPT-6 Astra"]]
        u3 = HOLDOUT_UNITS_III
        hdays = C.holdout_days()
        ce = ce.filter(pl.col("pt_date").is_in(list(hdays)))
        cat = cat.filter((pl.col("type") != "ML") | pl.col("pt_date").is_in(list(hdays)))
        u4 = sorted(set(cat.filter(pl.col("type") == "ML")["unit"].to_list()))
    out = {"mode": mode, "run_at": dt.datetime.now(dt.timezone.utc).isoformat(), "frozen": FROZEN, "ledger": led,
           "criteria": {}}
    c1 = {V: CN.newcomer_deficits(ad, cat, cal, c1_agents, V, rng) for V in ("V_eng", "V_rel")}
    out["C1"] = {V: {"test": t, "rows": r} for V, (t, r) in c1.items()}
    out["criteria"]["C1-r1b"] = (None if any(t is None for t, _ in c1.values()) else all(t["z"] > -2 for t, _ in c1.values()))
    c2 = {V: CN.newcomer_deficits(ad, cat, cal, c2_agents, V, rng) for V in ("V_rel", "V_eng")}
    out["C2"] = {V: {"test": t, "rows": r} for V, (t, r) in c2.items()}
    out["criteria"]["C2-r1b"] = (None if any(t is None for t, _ in c2.values()) else all(t["z"] > -2 for t, _ in c2.values()))
    m_rd, rd, m_diff, diff = CN.ctx_tests(ad, ce, u3, rng)       # w_* = work commits per call under r1b
    out["C3"] = {"meta": m_rd, "units": rd, "outcome": "work commits per call (ledger timing)"}
    frac = np.mean([v["hi"] < 0 for v in rd.values()]) if rd else 0.0
    out["criteria"]["C3-r1b"] = bool(m_rd and m_rd["mu"] <= -0.25 and m_rd["hi"] < 0 and frac >= 2 / 3)
    m4, t4 = CN.ml_meta(ad, cat, cal, u4, rng)
    out["C4"] = {"meta": m4, "units": t4}
    out["criteria"]["C4"] = (None if (m4 is None or m4["k"] < 2) else not (m4["mu"] <= -0.3 and m4["z"] <= -2))
    out["C5_check"] = {"meta": m_diff, "units": diff, "holds": bool(m_diff and m_diff["lo"] > 0)}
    me, te = fail_dip(ce, u3, rng)
    out["C3e_descriptive"] = {"meta": me, "units": te}
    cr = out["criteria"]
    if cr["C3-r1b"] is False or cr["C4"] is False or cr["C1-r1b"] is False or cr["C2-r1b"] is False:
        overall = "REFUTED"
    elif cr["C3-r1b"] is True and cr["C4"] is True:
        overall = "CONFIRMED"
    else:
        overall = "INCONCLUSIVE"
    out["overall"] = overall
    dest = C.OUT / ("confirm_r1b_dryrun.json" if mode == "dry" else "confirm/confirm_r1b_result.json")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=1, default=lambda o: None if o != o else float(o)))
    print(json.dumps({"mode": mode, "criteria": cr, "overall": overall,
                      "C1": {V: (round(t["effect"], 3), round(t["z"], 2)) if t else None for V, (t, _) in c1.items()},
                      "C2": {V: (round(t["effect"], 3), round(t["z"], 2)) if t else None for V, (t, _) in c2.items()},
                      "C3": (round(m_rd["mu"], 3), round(m_rd["lo"], 3), round(m_rd["hi"], 3), m_rd["k"]) if m_rd else None,
                      "C4": (round(m4["mu"], 3), round(m4["z"], 2), m4["k"]) if m4 else None,
                      "C5": (round(m_diff["mu"], 4), round(m_diff["lo"], 4)) if m_diff else None,
                      "C3e": (round(me["mu"], 3), me["k"]) if me else None}, indent=1))
    print("ledger:", json.dumps({t: {k: v for k, v in c.items() if k != "competing_planned"} for t, c in led.items()}))
    print("wrote", dest)


if __name__ == "__main__":
    main()
