"""H83 confirmatory test on the locked holdout. WRITTEN 2026-10-04 after round 1, FROZEN, NOT RUN on the holdout.

  uv run python hypotheses/H83-enculturation-of-newcomers/analysis/confirm.py --dry-run
      runs the full scoring on non-holdout stand-ins (the 19 round-1 joins). Safe: exploration data only.
  uv run python hypotheses/H83-enculturation-of-newcomers/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
      needs Vivian's sign-off. Checks the holdout ledger, writes confirm/confirm_sealed.json (SHA-256 of the frozen
      predictions below) BEFORE reading any held-out row, rebuilds the statement table in memory with held-out rows
      (scheme/build.py build(include_holdout=True, write=False); style standardization fitted on non-holdout rows only),
      and scores the held-out joins with the round-1 estimators (h83lib, windows E = tenure 2-4, L = 8-14).

Round-1 picture under test: newcomers sit near the veterans' alignment from tenure day 2 (small gap), do not show a
calibrated move toward the veterans over two weeks, start with a family signature in style-free content that fades.

Targets (joins whose day 1 or windows fall in the locked holdout; eligibility as in round 1):
  #1: GPT-4.1 (4, 2025-04-15), o3 (5, 04-16), Gemini 2.5 Pro (6, 04-24); #14: Claude Sonnet 4.5 (12, 09-30);
  #22: GPT-5.2 (18, 12-12); #29: Claude Opus 4.6 (20, 02-06); NE30: Gemini 3.1 Pro (22, 03-09);
  NE21+NE23: Claude Fable 5 (31, 06-09), Claude Sonnet 5 (32, 06-30), DeepSeek-V4-Pro (33, 07-02), GLM-5.2 (34, 07-03);
  #51 tail (NE33): Muse Spark 1.3 (43), Gemini 3.8 Flash (44), GPT-6 Astra (45), and the L windows of GLM-5.3 Flash (41)
  and Claude Fable 5.1 (42).
Frozen predictions (bge primary; gte reported):
  C1 the mean window-E gap over eligible held-out joins lies in [-0.05, +0.02].
  C2 no calibrated enculturation: the mean Delta G < +0.032 (the round-1 synthetic null 95th percentile).
  C3 family signature at entry: mean K_E > 0 over held-out joins with a family baseline (baselines built from all
     newcomers, held-out and not, same regime), and K_E > 0 in more than half of them.
  C4 the family signature fades: mean Delta K < 0.
  C5 (NE30, descriptive) Gemini 3.1 Pro's K_E > 0 (closer to Google newcomers' first-day baseline).
  Overall: the round-1 picture is CONFIRMED if C1, C2 and C3 pass.
Reuse disclosure: NE21+NE23 has an executed run (H04, activity) and planned content users; NE30 and the #51 tail are
targeted by several unrun scripts (H01, H13, H46, H73, ...). This test reads chat content embeddings (style-free) and
style features; disclose in both cards and LOG.md if run.
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
import h83lib as L  # noqa: E402

OUTD = L.DATA / "confirm"
PRED = {"C1": "mean gap_E in [-0.05, +0.02]", "C2": "mean Delta G < +0.032", "C3": "mean K_E > 0 and > half positive",
        "C4": "mean Delta K < 0", "C5": "agent 22 K_E > 0 (descriptive)", "overall": "C1 & C2 & C3"}
TARGET_AGENTS = [4, 5, 6, 12, 18, 20, 22, 31, 32, 33, 34, 41, 42, 43, 44, 45]
LEDGER_TARGETS = ["G01", "G14", "G22", "G29", "NE30", "NE21+NE23", "#51-tail"]


def score(joins: dict, agents) -> dict:
    J = {a: r for a, r in joins.items() if a in agents}
    g = L.summarize(J, "G"); ge = L.summarize(J, "G", "gap_E")
    k = L.summarize(J, "K"); ke = L.summarize(J, "K", "gap_E")
    out = {"n_joins": len(J), "G": g, "gap_E": ge, "K": k, "K_E": ke}
    out["C1"] = bool(ge["mean"] is not None and -0.05 <= ge["mean"] <= 0.02)
    out["C2"] = bool(g["mean"] is not None and g["mean"] < 0.032)
    out["C3"] = bool(ke["mean"] is not None and ke["mean"] > 0 and ke["n_pos"] > ke["n"] / 2)
    out["C4"] = bool(k["mean"] is not None and k["mean"] < 0)
    out["C5"] = (J[22]["K"]["gap_E"] > 0) if (22 in J and J[22].get("K")) else None
    out["overall"] = bool(out["C1"] and out["C2"] and out["C3"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    a = ap.parse_args()
    OUTD.mkdir(parents=True, exist_ok=True)
    days = L.calendar_days()
    if a.dry_run:
        st, X, F = L.load("bge", "vec")
        newc = L.newcomers(); doses = pl.read_parquet(L.DATA / "doses.parquet")
        res = L.run_all(st, X, F, newc, days, doses, with_mm=False)
        stand = [int(x) for x in res["joins"]]
        out = {"mode": "dry-run (non-holdout stand-ins: the round-1 joins)", "frozen": PRED,
               "bge": score(res["joins"], stand), "run_at": dt.datetime.now(dt.timezone.utc).isoformat()}
        (OUTD / "confirm_dryrun.json").write_text(json.dumps(out, indent=1, default=float))
        print(json.dumps(out, indent=1, default=float)[:2500])
        return
    if not (a.confirm and a.ack):
        sys.exit("refusing: needs --confirm --i-understand-this-uses-the-locked-holdout (and Vivian's sign-off)")
    sys.path.insert(0, str(L.ROOT / "infra/shared"))
    import holdout_ledger as HL
    for tgt in LEDGER_TARGETS:
        chk = HL.check("H83", tgt, "chat content embeddings", None)
        print(tgt, "allowed" if chk["allowed"] else "NOT ALLOWED", "disclose" if chk["needs_disclosure"] else "")
        if not chk["allowed"]:
            sys.exit(f"holdout ledger forbids {tgt}")
    seal = json.dumps(PRED, sort_keys=True)
    (OUTD / "confirm_sealed.json").write_text(json.dumps({"sha256": hashlib.sha256(seal.encode()).hexdigest(), "pred": PRED,
                                                          "sealed_at": dt.datetime.now(dt.timezone.utc).isoformat()}, indent=1))
    import build as B
    st, vecs, newc, doses = B.build(include_holdout=True, write=False)
    newc = newc.with_columns(pl.lit(False).alias("join_holdout"))   # score held-out joins
    out = {"mode": "CONFIRMATORY", "frozen": PRED, "run_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    for m in ("bge", "gte"):
        X = vecs[f"vec_{m}"].astype(np.float32)
        res = L.run_all(st, X, vecs["style"] if m == "bge" else None, newc, days, doses, with_mm=False,
                        agents=set(TARGET_AGENTS))
        out[m] = score(res["joins"], TARGET_AGENTS)
    (OUTD / "confirm_results.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, indent=1, default=float)[:3000])


if __name__ == "__main__":
    main()
