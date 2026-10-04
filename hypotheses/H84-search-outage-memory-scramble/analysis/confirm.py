"""H84 confirmatory test on the locked holdout. WRITTEN 2026-10-04 after round 1, NOT RUN on the holdout.

  uv run python hypotheses/H84-search-outage-memory-scramble/analysis/confirm.py --dry-run
      runs the frozen pipeline on non-holdout stand-ins: C1 on the G37 outage (03-31/04-01, the round-1 event) and
      C2 on the round-1 replication periods. Safe: exploration data only.
  uv run python hypotheses/H84-search-outage-memory-scramble/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
      checks the holdout ledger, writes confirm/confirm_sealed.json (SHA-256 of the frozen predictions) BEFORE reading
      any held-out row, rebuilds search events and the panel on held-out days only, then scores. Refuses to run
      without BOTH flags.

Round-1 picture under test: losing or narrowing history search costs no continuity and no output; search answers
carry little allocation information.
Targets (locked holdout):
  T1 NE25 (2026-07-01, inside the held-out NE21+NE23 window): search scoped to the agent's own village.
     Dose = search calls per 100 ledger calls on the five held-out active days before 07-01 (agents with >= 3 of them).
     Treated days = the first two active days >= 07-01; recovery = the next two; placebo pairs = all other
     consecutive active-day pairs of the held-out regime-III panel outside dose, treated and recovery days.
  T2 held-out regime-III periods with >= 30 mapped search calls (#43, #45-#50, #51 tail).
Frozen predictions:
  C1 (T1) beta_V1 and beta_V4 (dose x treated days, agent and day FE) each inside the central 80% of placebo betas.
  C2 (T2) DerSimonian-Laird pooled I_Q <= 0.05 bits, and I_Q > 0 (permutation p < 0.05) in <= 1/2 of the periods.
  Overall: the round-1 picture is CONFIRMED if C1 and C2 pass.
Reuse disclosure (hypotheses/holdout.md policy): the NE21+NE23 window is the target of H04's executed run (activity
timing, kick responses) and of planned runs by H01, H12, H26, H38, H09, H30, H35, H36, H39; H84's observable (DQ4
commit continuity by search dose) is a different statistic and modality. The #51 tail and #43/#45-#50 are targeted by
many unrun scripts (holdout_ledger.json). Disclose in both cards and LOG.md if run.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h84lib as L  # noqa: E402
import run as R  # noqa: E402
import semantic_kappa as K  # noqa: E402

OUTD = L.DATA / "confirm"
PRED = {"C1": "NE25: beta_V1 and beta_V4 (dose x first two active days >= 07-01) inside the central 80% of placebo pairs",
        "C2": "held-out regime-III periods: DL-pooled I_Q <= 0.05 bits; I_Q p < 0.05 in <= 1/2 of periods (>= 30 calls)",
        "overall": "CONFIRMED if C1 and C2 pass"}
TARGETS = ["NE21+NE23", "G43", "G45", "G46", "G47", "G48", "G49", "G50", "#51-tail"]


def c1(panel: pl.DataFrame, dose_days: list[str], treat: list[str], rec: list[str]) -> dict:
    dose = L.dose_table(panel, dose_days)
    pan = panel.filter(pl.col("agent").is_in(dose["agent"].implode()))
    pairs = L.placebo_pairs(pan, dose_days + treat + rec)
    out = {"n_agents": dose.height, "n_searchers": int((dose["dose"] >= L.SEARCHER_MIN).sum()), "n_pairs": len(pairs)}
    ok = True
    for k in ("V1_continuity", "V4_commits_per20"):
        f = L.frame(pan, k, dose)
        b = L.beta(f, treat, [rec])
        pb = np.array([L.beta(f, p, [treat, rec]) for p in pairs])
        pb = pb[np.isfinite(pb)]
        q10, q90 = float(np.percentile(pb, 10)), float(np.percentile(pb, 90))
        inside = bool(q10 <= b <= q90)
        ok &= inside
        out[k] = {"beta": b, "q10": q10, "q90": q90, "inside_central80": inside}
    out["pass"] = bool(ok)
    return out


def c2(sc: pl.DataFrame) -> dict:
    rep = R.replication(sc)
    per = {k: v for k, v in rep.items() if not k.startswith("_")}
    pooled = rep["_pooled_I_Q"]
    share = float(np.mean([v["p_perm"] < 0.05 for v in per.values()])) if per else float("nan")
    return {"periods": {k: {"I": v["I"], "I_ci": v["I_ci"], "p": v["p_perm"], "n": v["n"]} for k, v in per.items()},
            "pooled": pooled, "share_significant": share,
            "pass": bool(per and pooled["est"] <= 0.05 and share <= 0.5)}


def dry_run():
    panel = L.load_panel()
    sc = pl.read_parquet(L.DATA / "search_calls.parquet")
    res = {"mode": "dry-run (non-holdout stand-ins)", "C1_standin_G37": c1(panel, L.DOSE_DAYS, L.OUTAGE, L.RECOVERY),
           "C2_standin_round1": c2(sc), "predictions": PRED}
    res["overall"] = "CONFIRMED" if res["C1_standin_G37"]["pass"] and res["C2_standin_round1"]["pass"] else "NOT confirmed"
    OUTD.mkdir(parents=True, exist_ok=True)
    (OUTD / "confirm_dryrun.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps({k: (v["pass"] if isinstance(v, dict) and "pass" in v else v) for k, v in res.items()}, indent=1))


def confirm():
    sys.path.insert(0, str(L.ROOT / "infra/shared"))
    import holdout_ledger as HL  # noqa: E402
    for t in TARGETS:
        chk = HL.check("H84", t, "work commits / search answers", ["work_output", "artifact_lineage"])
        print(t, "allowed" if chk["allowed"] else "BLOCKED", "disclosure needed" if chk["needs_disclosure"] else "")
        if not chk["allowed"]:
            sys.exit(f"holdout ledger blocks {t}; stop and ask Vivian")
    OUTD.mkdir(parents=True, exist_ok=True)
    sealed = {"predictions": PRED, "sha256": hashlib.sha256(json.dumps(PRED, sort_keys=True).encode()).hexdigest(),
              "sealed_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUTD / "confirm_sealed.json").write_text(json.dumps(sealed, indent=1))
    import build as B  # noqa: E402  (H84 scheme)
    import search_events as SE  # noqa: E402
    hold = json.loads((L.ROOT / "hypotheses/holdout.json").read_text())
    cal = pl.read_parquet(L.SH / "calendar.parquet").filter(pl.col("holdout") & (pl.col("regime").cast(pl.Utf8) == "III"))
    held_days = sorted(cal["pt_date"].to_list())
    se = SE.scan(held=True)
    se.write_parquet(L.DATA / "search_events_confirm.parquet", compression="zstd")
    B.main(held_days=held_days)
    panel = L.load_panel("_confirm")
    sc = pl.read_parquet(L.DATA / "search_calls_confirm.parquet")
    days = sorted(panel["pt_date"].unique().to_list())
    pre = [d for d in days if d < "2026-07-01"][-5:]
    post = [d for d in days if d >= "2026-07-01"]
    res = {"mode": "CONFIRMATORY", "holdout_json_locked": hold.get("locked", None),
           "C1": c1(panel, pre, post[:2], post[2:4]), "C2": c2(sc), "predictions": PRED, "sealed": sealed["sha256"]}
    res["overall"] = "CONFIRMED" if res["C1"]["pass"] and res["C2"]["pass"] else "NOT confirmed"
    (OUTD / "confirm_result.json").write_text(json.dumps(res, indent=1, default=float))
    print(res["overall"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", action="store_true", dest="ack")
    a = ap.parse_args()
    if a.confirm:
        if not a.ack:
            sys.exit("refusing: --confirm needs --i-understand-this-uses-the-locked-holdout (and Vivian's sign-off)")
        confirm()
    elif a.dry_run:
        dry_run()
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
