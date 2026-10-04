"""H125 confirmatory test on the LOCKED HOLDOUT. Written 2026-10-04 after exploratory round 1; NOT RUN.

Guard: the holdout is touched only with BOTH flags, a clean git state for H125's code, and a holdout-ledger check:
  uv run python hypotheses/H125-kickoff-damped-oscillator/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
Without flags it prints the frozen predictions. --dry-run runs the identical in-memory pipeline on non-holdout stand-in
kickoffs (#11-#13, #38-#42) and writes data/processed/H125-kickoff-damped-oscillator/confirm_dryrun.json only.

Targets: held-out goal periods with a shared kickoff and >= 5 contiguous active days from day 1 in one regime (resolved at
run time from: #1, #9, #14, #15, #28, #29, #34, #43, #45, #46, #47, #48, #49, #50). Excluded: #22/#23 and #32 (H10's
confirmatory directions stay blind). Estimator identical to analysis/h125lib.py (bge-small, white32, decoys = the
exploratory non-holdout kickoffs except p-1, p+1, #23). Placebo: the exploratory placebo-day pool (NE34, bge_white, frozen).
Frozen predictions (the exploratory result is a powered negative, so C1 confirms the absence of an undershoot):
  C1  no undershoot: DL meta U 90% CI upper bound < +0.015 (the U a zeta = 0.5 oscillator gives at the observed overshoot,
      synthetic W_osc_0.5) AND Mann-Whitney (target U > exploratory placebo U) one-sided p >= 0.05. Credence 0.75.
      (Exploration: U -0.006 [-0.020, +0.008], p 0.79.)
  C2  overshoot replicates: DL meta E1 90% CI above 0 and E1 > 0 in >= 2/3 of targets. Credence 0.8.
      (Exploration: E1 +0.055 +/- 0.012, 22/27.)
Reuse policy (hypotheses/holdout.md): H97 and H54 plan the same held-out kickoffs with different statistics (cross-agent
memory across the boundary; day-1 target percentile); H125's statistic (within-agent day 2-3 vs 4-5 level along k-hat) is
different but shares the k-hat projection family with H54/H97: disclose in all three cards and LOG.md when run.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import mannwhitneyu

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h125lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
from embed_models import goal_vectors, load_whitener  # noqa: E402

FROZEN = {"targets": [1, 9, 14, 15, 28, 29, 34, 43, 45, 46, 47, 48, 49, 50], "exclude": [22, 23, 32],
          "standins": [11, 12, 13, 38, 39, 40, 41, 42], "cfg": "bge_white", "min_days": 5, "C1_U_hi": 0.015, "C1_p": 0.05,
          "C2_frac": 2 / 3, "exclude_agents": [19, 28, 30]}
FILES = ["hypotheses/H125-kickoff-damped-oscillator/analysis/confirm.py", "hypotheses/H125-kickoff-damped-oscillator/analysis/h125lib.py"]


def git_clean() -> bool:
    out = subprocess.run(["git", "-C", str(L.ROOT), "status", "--porcelain", "--", *FILES], capture_output=True, text=True).stdout
    return out.strip() == ""


def build(p: int, allow_holdout: bool):
    """In-memory equivalent of scheme/build.py for one kickoff (no files written)."""
    from common import holdout_mask
    st = pl.read_parquet(L.ED / "statements.parquet").with_row_index("row")
    st = st.filter((pl.col("goal_no") == p) & ~pl.col("agent").is_in(FROZEN["exclude_agents"]))
    cal = pl.read_parquet(L.S / "calendar.parquet").with_columns(pl.col("regime").cast(pl.String)).sort("pt_date")
    cal = cal.with_columns(pl.Series("ho", holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())),
                           (pl.col("window_s") / 3600).alias("day_h"))
    if not allow_holdout:
        st = st.filter(~pl.Series(holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list())))
    gd = cal.filter(pl.col("goal_no") == p)
    if not allow_holdout:
        gd = gd.filter(~pl.col("ho"))
    days = gd["pt_date"].to_list()
    if len(days) < FROZEN["min_days"] or gd.head(FROZEN["min_days"])["regime"].n_unique() > 1:
        return None
    goals = pl.read_parquet(L.ED / "goals.parquet").with_columns(pl.col("kind").cast(pl.String))
    kr = goals.filter((pl.col("goal_no") == p) & (pl.col("kind") == "kickoff"))
    if kr.height == 0:
        return None
    kr = kr.row(0, named=True)
    t0 = kr["win_start"]
    try:
        k54 = pl.read_parquet(L.ROOT / "data/processed/H54-kickoff-quench-target/kickoffs.parquet").filter(
            (pl.col("goal_no") == p) & pl.col("room").is_null())
        if k54.height:
            t0 = k54["t0"][0]
    except Exception:  # noqa: BLE001  (held-out kickoffs are not in H54's exploration table)
        pass
    calr = {r["pt_date"]: r for r in gd.iter_rows(named=True)}
    Hb = np.cumsum([0.0] + [calr[d]["day_h"] for d in days])[:-1]
    hb = dict(zip(days, Hb))

    def hc(t, d):
        r = calr[d]
        return hb[d] + min(max((t - r["win_start"]).total_seconds() / 3600, 0.0), r["day_h"])
    st = st.filter(pl.col("pt_date").is_in(days))
    inc = sorted(set(st.filter((pl.col("pt_date") == days[0]) & (pl.col("t") >= t0))["agent"].to_list()))
    st = st.filter(pl.col("agent").is_in(inc))
    h0 = hc(t0, days[0])
    di = {d: i + 1 for i, d in enumerate(days)}
    recs = st.select("row", "agent", "t", "pt_date").to_dicts()
    for r in recs:
        r["day_idx"] = di[r["pt_date"]]; r["h"] = hc(r["t"], r["pt_date"]) - h0
        f = (r["t"] - calr[r["pt_date"]]["win_start"]).total_seconds() / max(calr[r["pt_date"]]["window_s"], 1)
        r["slot"] = int(min(max(f, 0.0), 0.9999) * 4); r["seg"] = "pre" if r["t"] < t0 else "post"
    sdf = pl.DataFrame(recs).with_columns(pl.col("day_idx").cast(pl.Int16), pl.col("slot").cast(pl.Int8), pl.col("h").cast(pl.Float32)).sort("t")
    m = "bge_small"
    reg = gd["regime"][0]
    own = load_whitener(reg, 32, m)(goal_vectors(m)[kr["gid"]][None, :].astype(np.float64))[0]
    own = own / np.linalg.norm(own)
    V = L.vecs(); K = V[f"K|{m}|{reg}"]; kg = V["kick_goal_no"]
    D = K[[j for j, g in enumerate(kg) if g not in (p - 1, p, p + 1, 23)]]
    X = np.asarray(L.statement_matrix(m, "white")[sdf["row"].to_numpy()], dtype=np.float64)
    a = X @ own - (X @ D.T).mean(1)
    krow = dict(design=f"T{p:02d}", goal_no=p, regime=reg, n_days=len(days), day_h=[calr[d]["day_h"] for d in days], native=None)
    return sdf, krow, a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ok", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    print(json.dumps(FROZEN, indent=1))
    if a.dry_run:
        goals, allow = FROZEN["standins"], False
    elif a.confirm and a.ok:
        if not git_clean():
            sys.exit("H125 code has uncommitted changes; commit the frozen version first.")
        import holdout_ledger as HL
        for g in FROZEN["targets"]:
            chk = HL.check("H125", f"G{g:02d}", "content_kickoff_step_response", "embedding_content")
            if not chk["allowed"]:
                sys.exit(f"ledger refuses G{g:02d}: {chk['prior_runs_same_family']}")
            if chk["needs_disclosure"]:
                print("disclose:", g, [u["hypothesis"] for u in chk["prior_runs"] + chk["competing_planned"]])
        goals, allow = FROZEN["targets"], True
    else:
        print("Frozen predictions printed; nothing run (pass --dry-run, or both confirm flags with Vivian's sign-off).")
        return
    per = {}
    for g in goals:
        b = build(g, allow)
        if b is None:
            continue
        sdf, krow, av = b
        r = L.analyze_kickoff(sdf, krow, av, None, settled=(4, 5))
        per[g] = dict(U=r["U"], se_U=r["se_U"], E1=r["E1"], se_E1=r["se_E1"], n_u=r["n_u"])
    plc = pl.read_parquet(L.DATA / "NE34/placebo_all_configs.parquet").filter(pl.col("cfg") == FROZEN["cfg"])["U"].drop_nans().to_numpy()
    U = np.array([v["U"] for v in per.values()]); se = np.array([v["se_U"] for v in per.values()])
    m = L.dl_meta(U, se)
    p = float(mannwhitneyu(U[np.isfinite(U)], plc, alternative="greater").pvalue) if np.isfinite(U).sum() >= 2 else np.nan
    E = L.dl_meta([v["E1"] for v in per.values()], [v["se_E1"] for v in per.values()])
    Ev = np.array([v["E1"] for v in per.values()])
    out = dict(mode="dry-run" if a.dry_run else "CONFIRMATORY", goals=list(per), per=per,
               C1=dict(meta=m, U_hi=m["mean"] + 1.645 * m["se"], p_mw=p, pass_=bool(m["mean"] + 1.645 * m["se"] < FROZEN["C1_U_hi"] and p >= FROZEN["C1_p"])),
               C2=dict(meta=E, frac=float(np.mean(Ev > 0)) if len(Ev) else None,
                       pass_=bool(E["mean"] - 1.645 * E["se"] > 0 and np.mean(Ev > 0) >= FROZEN["C2_frac"])),
               run_at=dt.datetime.now(dt.timezone.utc).isoformat())
    name = "confirm_dryrun.json" if a.dry_run else "confirm_results.json"
    (L.DATA / name).write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps({k: v for k, v in out.items() if k != "per"}, indent=1, default=float))


if __name__ == "__main__":
    main()
