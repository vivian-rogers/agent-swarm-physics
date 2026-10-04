"""H38 confirmatory test on the LOCKED HOLDOUT. Written 2026-10-04 after exploratory round 1; NOT RUN.

Refuses to touch held-out data unless called with BOTH flags:
    uv run python hypotheses/H38-platform-stalls/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
Dry run (same code, non-holdout stand-ins, output to data/processed/H38-platform-stalls/confirm_dryrun/):
    uv run python hypotheses/H38-platform-stalls/analysis/confirm.py --dry-run

Frozen predictions (card, "Confirmatory predictions"):
  C1 regime III: in held-out regime-III periods with a significant raw gain (z > 2 vs N1), median f_scaffold >= 0.5, and
     day-edge conditioning alone (mask_edge) removes >= 0.4 of the excess (median f_edge >= 0.4).
  C2 regime I: in held-out regime-I periods with a significant raw gain, median f_scaffold < 0.35.
  C3 the regime III - I difference in mean g_eq active over held-out periods shrinks by >= 50% under mask_scaffold.
  C4 errors mark busy minutes, not stalls: median log OR(JS | infra burst in [t-10, t-1]) < 0 over held-out periods with
     >= 20 burst minutes.
  C5 talk co-activation is not infrastructure: in held-out periods with a significant raw talk gain, median talk
     f_scaffold < 0.3.
  C6 hours reversal (NE21, ABAB 8 h / 4 h / 8 h weeks inside the window): the edge-induced excess E_raw - E_mask_edge is
     smaller in each 8-h week than in each adjacent 4-h week (edges are a fixed-length ramp, so longer days dilute them).
Holdout reuse (policy in hypotheses/holdout.md): #45 was used by H02 (activity-timing couplings and CW beta*J0) and H23
(message content). H38's observables (cause composition of joint silences, stall-adjusted excess) are different
statistics; disclosed in the card. The rest of the regime-III holdout (#46-#50) is used here for the first time.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import h38lib as L  # noqa: E402
import run_period as RP  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

FLAG = "--i-understand-this-uses-the-locked-holdout"
HELD = {"III": [45, 46, 47, 49, 50], "I": [1, 9, 14, 15, 22, 28, 29], "II": [32, 34]}
STANDIN = {"III": [39, 40, 41], "I": [10, 17, 18], "II": [35]}
# NE21 weeks (documented hours): 8 h 06-08..06-12, 4 h 06-15..06-26, 8 h 06-29..07-03
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
    f = lambda v, src=a: 1 - src[v]["E"] / src["raw"]["E"] if src.get("raw", {}).get("E", 0) > 0 else np.nan
    return {"days": len(days), "ok": True, "g_raw": a["raw"]["g"], "E_raw": a["raw"]["E"], "z_raw": a["raw"]["z"],
            "E_mask_edge": a["mask_edge"]["E"], "E_mask_scaffold": a["mask_scaffold"]["E"], "g_mask_scaffold": a["mask_scaffold"]["g"],
            "z_mask_scaffold": a["mask_scaffold"]["z"], "f_scaffold": f("mask_scaffold"), "f_edge": f("mask_edge"),
            "t_E_raw": t.get("raw", {}).get("E"), "t_z_raw": t.get("raw", {}).get("z"),
            "t_f_scaffold": f("mask_scaffold", t) if t else np.nan,
            "burst_lor": (o1 or {}).get("burst_logOR"), "n_burst": (o1 or {}).get("n_burst_min"),
            "cause_shares": (o1 or {}).get("cause_shares"), "js_share": (o1 or {}).get("js_share")}


def evaluate(P: dict, W: dict) -> dict:
    out = {}
    r3 = [x for g, x in P.items() if x["regime"] == "III" and x["ok"] and x["z_raw"] > 2]
    r1 = [x for g, x in P.items() if x["regime"] == "I" and x["ok"] and x["z_raw"] > 2]
    med = lambda xs: float(np.nanmedian(xs)) if xs else np.nan
    out["C1"] = {"n": len(r3), "median_f_scaffold": med([x["f_scaffold"] for x in r3]), "median_f_edge": med([x["f_edge"] for x in r3])}
    out["C1"]["pass"] = bool(r3) and out["C1"]["median_f_scaffold"] >= 0.5 and out["C1"]["median_f_edge"] >= 0.4
    out["C2"] = {"n": len(r1), "median_f_scaffold": med([x["f_scaffold"] for x in r1])}
    out["C2"]["pass"] = bool(r1) and out["C2"]["median_f_scaffold"] < 0.35
    g3 = [x for x in P.values() if x["regime"] == "III" and x["ok"]]
    g1 = [x for x in P.values() if x["regime"] == "I" and x["ok"]]
    if g3 and g1:
        d_raw = np.mean([x["g_raw"] for x in g3]) - np.mean([x["g_raw"] for x in g1])
        d_adj = np.mean([x["g_mask_scaffold"] for x in g3]) - np.mean([x["g_mask_scaffold"] for x in g1])
        out["C3"] = {"diff_raw": float(d_raw), "diff_mask_scaffold": float(d_adj), "shrink": float(1 - d_adj / d_raw) if d_raw else np.nan}
        out["C3"]["pass"] = d_raw > 0 and out["C3"]["shrink"] >= 0.5
    b = [x for x in P.values() if x["ok"] and (x["n_burst"] or 0) >= 20 and x["burst_lor"] is not None]
    out["C4"] = {"n": len(b), "median_lor": med([x["burst_lor"] for x in b])}
    out["C4"]["pass"] = bool(b) and out["C4"]["median_lor"] < 0
    tt = [x for x in P.values() if x["ok"] and x["t_z_raw"] is not None and x["t_z_raw"] > 2]
    out["C5"] = {"n": len(tt), "median_talk_f_scaffold": med([x["t_f_scaffold"] for x in tt])}
    out["C5"]["pass"] = bool(tt) and out["C5"]["median_talk_f_scaffold"] < 0.3
    if all(k in W and W[k]["ok"] for k in NE21):
        ei = {k: W[k]["E_raw"] - W[k]["E_mask_edge"] for k in NE21}
        out["C6"] = {"edge_excess": ei, "pass": bool(ei["8h_a"] < ei["4h"] and ei["8h_b"] < ei["4h"])}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument(FLAG, dest="understand", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.confirm and not a.understand:
        sys.exit(f"Refusing: --confirm also needs {FLAG}.")
    if not a.confirm and not a.dry_run:
        sys.exit(f"Nothing to do. Use --dry-run (non-holdout stand-ins) or --confirm {FLAG} (locked holdout).")
    live = a.confirm and a.understand
    sets, weeks = (HELD, NE21) if live else (STANDIN, NE21_STANDIN)
    out_dir = L.DATA / ("confirm" if live else "confirm_dryrun")
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng([L.SEED, 9090 if live else 9091])
    P = {}
    for reg, gs in sets.items():
        for g in gs:
            d = days_of(g, allow_holdout=live)
            if not d:
                continue
            st = period_stats(d, rng)
            st["regime"] = reg
            P[f"G{g:02d}"] = st
            print(f"G{g:02d} ({reg}): {st.get('z_raw', float('nan')):.1f} raw z, f_scaffold {st.get('f_scaffold', float('nan')):.2f}", flush=True)
    W = {}
    for k, (s, e) in weeks.items():
        d = days_between(s, e, allow_holdout=live)
        W[k] = period_stats(d, rng) if d else {"ok": False}
    res = {"live": live, "periods": P, "ne21_weeks": W, "evaluation": evaluate(P, W)}
    (out_dir / "result.json").write_text(json.dumps(res, indent=1, default=lambda x: float(x) if isinstance(x, (np.floating, np.integer)) else str(x)))
    print(json.dumps(res["evaluation"], indent=1, default=float))


if __name__ == "__main__":
    main()
