"""H67 confirmatory run on the LOCKED HOLDOUT. Written and frozen 2026-10-04 after round 1; NOT RUN.

Guard: runs on held-out data only with BOTH `--confirm` and H67_CONFIRM=1, and only if `holdout_ledger.check` allows
every target. Otherwise it refuses. `--dry-run` runs the identical pipeline on non-holdout stand-in units and writes to
a scratch directory, so the code path is tested without touching the holdout.

Targets (period units of): #22, #28 (regime I), #43 and the #51 tail (regime III).

Frozen predictions (thresholds fixed from round 1; estimator = round 1's primary: matched-lag in-flight placebo,
agent x day x call-class fields, all-present window, 1-h block bootstrap B = 200):
  C1  Subcritical: every target unit's g_lag upper 95% bound < 1, and every point estimate < 0.5.
  C2  Regime split: the regime-III targets' random-effects pooled g_lag has a 95% CI excluding 0 and a point estimate
      in [0.05, 0.35]; the regime-I targets' pooled g_lag has |g| < 0.05 or a CI including 0.
  C3  Address gating (regime III): pooled named J1* >= 5 x pooled unnamed J1*.
  C4  The equal-time dial overstates read-out coupling in regime I: unit-weighted g_eq - g_lag > 0.05 (regime-I targets).
  C5  (post hoc pattern from round 1, flagged) #51 tail: g_lag in [0.05, 0.30] and the named part >= 40% of g_lag.
Reading: C1 + C2 + C3 confirm "subcritical read-out coupling, regime-III and address-gated"; C4 confirms that the
equal-time talk dial reads a field in regime I. The original HH262 claim (lagged gain larger than the equal-time
dial everywhere) is predicted REFUTED (round 1: 20% of periods).

Reuse policy (hypotheses/holdout.md): planned users of these targets include H03, H08, H19, H25 (equal-time dial;
H25 Stage B gated on H19), H12, H18, H29, H34, H39. Nobody has run on them. H67's g_eq on #22/#43 is H25's estimator
family: if H25/H19 run first, C4 is a second use of their statistic and must be disclosed (C1-C3 are a different
statistic: the call-level read-out jump). Disclose in the card and LOG.md before running.

Usage:
  uv run python hypotheses/H67-lagged-criticality-dial/analysis/confirm.py --dry-run
  H67_CONFIRM=1 uv run python hypotheses/H67-lagged-criticality-dial/analysis/confirm.py --confirm
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import build as B  # noqa: E402
import h67lib as L  # noqa: E402

ROOT = HERE.parents[2]
SH = ROOT / "data/processed/shared"
sys.path.insert(0, str(SH.parents[1] / "infra/shared"))
OUT = ROOT / "data/processed/H67-lagged-criticality-dial/confirm"
SCRATCH = Path(os.environ.get("TMPDIR", "/tmp")) / "h67_confirm_dryrun"
TARGET_GOALS = {22: "I", 28: "I", 43: "III", 51: "III"}
STANDINS = {"27": "I", "24": "I", "42a": "III", "51j": "III"}
FROZEN = dict(C1=dict(g_hi=1.0, g_point=0.5), C2=dict(III=(0.05, 0.35), I_abs=0.05), C3=dict(ratio=5.0),
              C4=dict(diff=0.05), C5=dict(range=(0.05, 0.30), named_share=0.40))


def re_pool(est, se):
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    if not len(est):
        return {"mean": np.nan, "lo": np.nan, "hi": np.nan}
    w = 1 / se ** 2
    m = (w * est).sum() / w.sum()
    Q = (w * (est - m) ** 2).sum()
    tau2 = max(0.0, (Q - (len(est) - 1)) / (w.sum() - (w ** 2).sum() / w.sum())) if len(est) > 1 else 0.0
    ws = 1 / (se ** 2 + tau2)
    mm = (ws * est).sum() / ws.sum()
    s = np.sqrt(1 / ws.sum())
    return {"mean": float(mm), "lo": float(mm - 1.96 * s), "hi": float(mm + 1.96 * s)}


def unit_stats(base: Path, uid: str) -> dict:
    c = pl.read_parquet(base / "units" / f"{uid}.parquet")
    m = pl.read_parquet(base / "msgs" / f"{uid}.parquet")
    d = L.all_counts(c, m)
    r = L.fit(d, m, "main", True, B=200, seed=1)
    rn = L.fit(d, m, "named", True, B=200, seed=4)
    eq = L.equal_time(d, B=0)
    if not r.get("ok"):
        return {"unit": uid, "ok": False}
    rows = L._rows(d, True)
    sn = float(rows["R_all_n"].sum() / max(rows["R_all"].sum(), 1))
    return {"unit": uid, "ok": True, "g": r["g"], "g_lo": r.get("g_lo"), "g_hi": r.get("g_hi"), "g_se": r.get("g_se"),
            "J1_named": rn.get("J1_named"), "J1_named_se": rn.get("J1_named_se"), "J1_unnamed": rn.get("J1_unnamed"),
            "J1_unnamed_se": rn.get("J1_unnamed_se"), "g_eq": eq.get("g_eq"),
            "g_named": r["rbar"] * r["mbar"] * sn * rn.get("J1_named", np.nan), "n_rows": r["n_rows"]}


def score(res: list, regime_of: dict, tail_units: set) -> dict:
    df = pl.DataFrame([r for r in res if r.get("ok")])
    df = df.with_columns(pl.col("unit").replace_strict(regime_of, default=None).alias("regime"))
    out = {}
    out["C1"] = bool((df["g_hi"] < FROZEN["C1"]["g_hi"]).all() and (df["g"] < FROZEN["C1"]["g_point"]).all())
    s3, s1 = df.filter(pl.col("regime") == "III"), df.filter(pl.col("regime") == "I")
    p3 = re_pool(s3["g"].to_numpy(), s3["g_se"].to_numpy())
    p1 = re_pool(s1["g"].to_numpy(), s1["g_se"].to_numpy())
    lo, hi = FROZEN["C2"]["III"]
    out["C2"] = bool(p3["lo"] > 0 and lo <= p3["mean"] <= hi and (abs(p1["mean"]) < FROZEN["C2"]["I_abs"] or p1["lo"] <= 0))
    out["C2_detail"] = {"III": p3, "I": p1}
    a = re_pool(s3["J1_named"].to_numpy(), s3["J1_named_se"].to_numpy())
    b = re_pool(s3["J1_unnamed"].to_numpy(), s3["J1_unnamed_se"].to_numpy())
    out["C3"] = bool(a["mean"] >= FROZEN["C3"]["ratio"] * max(b["mean"], 1e-9))
    out["C3_detail"] = {"named": a, "unnamed": b}
    w = s1["n_rows"].to_numpy().astype(float)
    diff = float(((s1["g_eq"] - s1["g"]).to_numpy() * w).sum() / max(w.sum(), 1)) if s1.height else np.nan
    out["C4"] = bool(diff > FROZEN["C4"]["diff"])
    out["C4_detail"] = diff
    t = df.filter(pl.col("unit").is_in(list(tail_units)))
    if t.height:
        pt = re_pool(t["g"].to_numpy(), t["g_se"].to_numpy())
        nshare = float(np.nanmean(t["g_named"].to_numpy()) / pt["mean"]) if pt["mean"] else np.nan
        lo, hi = FROZEN["C5"]["range"]
        out["C5"] = bool(lo <= pt["mean"] <= hi and nshare >= FROZEN["C5"]["named_share"])
        out["C5_detail"] = {"g": pt, "named_share": nshare}
    out["units"] = df.to_dicts()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if a.dry_run:
        res = [unit_stats(L.OUT, u) for u in STANDINS]
        out = score(res, STANDINS, {"51j"})
        SCRATCH.mkdir(parents=True, exist_ok=True)
        (SCRATCH / "dryrun.json").write_text(json.dumps({"sha256": sha, **out}, indent=1, default=float))
        print(json.dumps({k: v for k, v in out.items() if k != "units"}, indent=1, default=float))
        return
    if not (a.confirm and os.environ.get("H67_CONFIRM") == "1"):
        sys.exit("refusing: confirmatory run needs --confirm and H67_CONFIRM=1 (Vivian's sign-off)")
    import holdout_ledger as HL
    for g in TARGET_GOALS:
        tgt = "#51-tail" if g == 51 else f"G{g}"
        chk = HL.check("H67", tgt, "talk", ["dilution_addressing", "curie_weiss_gain"])
        if not chk["allowed"]:
            sys.exit(f"refusing: holdout ledger blocks {tgt}: {chk['prior_runs_same_family']}")
    pu = pl.read_parquet(SH / "period_units.parquet").filter(pl.col("holdout") & pl.col("goal_no").is_in(list(TARGET_GOALS)))
    cal = pl.read_parquet(SH / "calendar.parquet")
    cw, lt, it, cc = B.load_shared(allow_holdout=True)
    regime_of, tail = {}, set()
    res = []
    for u in pu.to_dicts():
        r = B.build_unit(u, cw, lt, it, cc, cal, out_dir=OUT, allow_holdout=True)
        if r is None:
            continue
        regime_of[u["unit_id"]] = TARGET_GOALS[u["goal_no"]]
        if u["goal_no"] == 51:
            tail.add(u["unit_id"])
        res.append(unit_stats(OUT, u["unit_id"]))
    out = score(res, regime_of, tail)
    (OUT / "confirm_result.json").write_text(json.dumps({"sha256": sha, **out}, indent=1, default=float))
    print(json.dumps({k: v for k, v in out.items() if k != "units"}, indent=1, default=float))


if __name__ == "__main__":
    main()
