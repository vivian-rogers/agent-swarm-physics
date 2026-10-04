"""H97 confirmatory tests on the LOCKED HOLDOUT. Written 2026-10-04 after exploratory round 1; NOT RUN.

Guard: the holdout is touched only with BOTH flags, a clean git state for H97's code, and a holdout-ledger check:
  uv run python hypotheses/H97-quench-restoring-force/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
Without flags it prints the frozen predictions. --dry-run runs the identical pipeline on non-holdout stand-in kickoffs
(#38-#42 and #11-#13) and writes nothing to the holdout ledger.

Targets: held-out kickoff transitions whose previous period is in the same regime: #9, #14, #15, #28, #29, #34, #43, #45,
#46, #47, #48, #49, #50. Excluded: #22/#23 and #32 (H10's confirmatory directions g-hat_23 and g-hat_32 stay blind).
Statistics (frozen, identical to analysis/run.py and h97lib after Amendment 1):
  C1  extra forgetting at the kickoff: meta-analytic mean drho_full with 90% CI above 0 AND drho > 0 in >= 2/3 of
      transitions with N >= 5 and >= 1 placebo boundary (exploration: 0.26 +/- 0.04, 16/18).
  C2  anisotropy (the exploratory counter-finding to P2): drho_par > drho_perp in >= 2/3 of those transitions, sign test
      one-sided p < 0.05 (exploration: 0.63 vs 0.25 meta means).
  C3  overshoot: intercept a (agent-centered variant) meta 90% CI above 0 (exploration: +0.12 +/- 0.02).
  C4  agent constancy out of sample: Spearman between agents' mean exploratory chi_mem rank (NE34/chi_agents.parquet,
      primary) and their mean held-out rank, agents with >= 3 exploratory and >= 2 held-out transitions; one-sided p < 0.05.
      Expected to fail (credence 0.3; exploration r = 0.30, p = 0.14, power 0.30).
Reuse policy (hypotheses/holdout.md): H54's confirm uses the same held-out kickoffs for a day-1 target percentile; H97's
statistic (cross-agent memory across the kickoff boundary vs placebo days) is different. #34 was used by H05 (activity),
#45 by H02/H04 (activity); #28/#29/#45-#50 have content plans by other cards. Disclose in both cards and LOG.md when run.
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
from scipy.stats import binomtest, spearmanr

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h97lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
from embed_models import goal_vectors, load_whitener  # noqa: E402

FROZEN = {"targets": [9, 14, 15, 28, 29, 34, 43, 45, 46, 47, 48, 49, 50], "standins": [11, 12, 13, 38, 39, 40, 41, 42],
          "model": "bge_small", "C1_frac": 2 / 3, "C2_frac": 2 / 3, "C2_p": 0.05, "C4_p": 0.05, "C4_min_expl": 3, "C4_min_hold": 2,
          "exclude": [22, 23, 32]}
FILES = ["hypotheses/H97-quench-restoring-force/analysis/confirm.py", "hypotheses/H97-quench-restoring-force/analysis/h97lib.py",
         "hypotheses/H97-quench-restoring-force/analysis/calibrate.py"]


def git_clean() -> bool:
    out = subprocess.run(["git", "-C", str(L.ROOT), "status", "--porcelain", "--", *FILES], capture_output=True, text=True).stdout
    return out.strip() == ""


def build_transition(p: int, allow_holdout: bool):
    """In-memory equivalent of scheme/build.py for one kickoff transition (no files written)."""
    st = pl.read_parquet(L.ED / "statements.parquet").with_row_index("row")
    st = st.filter((pl.col("agent") != 19) & ~pl.col("goal_no").is_in(FROZEN["exclude"]) & pl.col("goal_no").is_in([p - 1, p]))
    if not allow_holdout:
        from common import holdout_mask
        st = st.filter(~pl.Series(holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list())))
    goals = pl.read_parquet(L.ED / "goals.parquet")
    kr = goals.filter((pl.col("goal_no") == p) & (pl.col("kind") == "kickoff"))
    if kr.height == 0 or st.filter(pl.col("goal_no") == p - 1).height == 0:
        return None
    kr = kr.row(0, named=True)
    if st.filter(pl.col("goal_no") == p - 1)["regime"][0] != kr["regime"]:
        return None
    pu = pl.read_parquet(L.S / "period_units.parquet")
    unit_of = {(r["goal_no"], d): r["unit_id"] for r in pu.iter_rows(named=True) for d in r["days"]}
    dd = {g: sorted(st.filter(pl.col("goal_no") == g)["pt_date"].unique().to_list()) for g in (p - 1, p)}
    t0 = kr["win_start"]
    try:
        k54 = pl.read_parquet(L.ROOT / "data/processed/H54-kickoff-quench-target/kickoffs.parquet").filter(
            (pl.col("goal_no") == p) & pl.col("room").is_null())
        if k54.height:
            t0 = k54["t0"][0]
    except Exception:  # noqa: BLE001  (held-out kickoffs are not in H54's exploration table)
        pass
    d1 = kr["first_day"]
    sub = st.with_columns(
        pl.struct("goal_no", "pt_date").map_elements(lambda s: dd[s["goal_no"]].index(s["pt_date"]) + 1, return_dtype=pl.Int16).alias("day_idx"),
        pl.struct("goal_no", "pt_date").map_elements(lambda s: unit_of.get((s["goal_no"], s["pt_date"]), "?"), return_dtype=pl.String).alias("unit_id"))
    sub = sub.with_columns(
        pl.when((pl.col("goal_no") == p - 1) & (pl.col("pt_date") == dd[p - 1][-1])).then(pl.lit("prev"))
        .when((pl.col("goal_no") == p) & (pl.col("pt_date") == d1) & (pl.col("t") >= t0)).then(pl.lit("day1"))
        .when((pl.col("goal_no") == p) & (pl.col("day_idx").is_between(2, 5))).then(pl.lit("plateau"))
        .otherwise(pl.lit("other")).alias("seg"), pl.lit(f"T{p:02d}").alias("design"))
    m = FROZEN["model"]
    k = load_whitener(kr["regime"], 32, m)(goal_vectors(m)[kr["gid"]][None, :].astype(np.float64))[0]
    k = k / np.linalg.norm(k)
    tr = dict(design=f"T{p:02d}", p=p, prev=p - 1, regime=kr["regime"], first_day=d1)
    return sub, tr, k


def analyze(p, allow_holdout):
    from calibrate import placebo_boundaries
    b = build_transition(p, allow_holdout)
    if b is None:
        return None
    stmt, tr, k = b
    res = {}
    for cfg, center in (("primary", None), ("center", L.agent_center_means(tr["regime"], {p, p - 1}, FROZEN["model"], "white"))):
        sv = lambda mm: L.seg_vectors(stmt, mm, FROZEN["model"], "white", False, center)  # noqa: E731
        kick = L.boundary(sv(pl.col("seg") == "prev"), sv(pl.col("seg") == "day1"))
        if len(kick) < L.MIN_N_AGENT:
            return None
        plac = []
        for g, d0, d1 in placebo_boundaries(stmt, tr):
            bd = L.boundary(sv((pl.col("goal_no") == g) & (pl.col("pt_date") == d0)), sv((pl.col("goal_no") == g) & (pl.col("pt_date") == d1)))
            if len(bd) >= L.MIN_N_TRANSITION:
                plac.append(bd)
        pT = L.plateau_targets(sv(pl.col("seg") == "plateau"), k)
        res[cfg] = L.analyze_transition(kick, plac, pT, k, seed=p)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ok", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    print(json.dumps(FROZEN, indent=1, default=str))
    if a.dry_run:
        goals, allow = FROZEN["standins"], False
    elif a.confirm and a.ok:
        if not git_clean():
            sys.exit("H97 code has uncommitted changes; commit the frozen version first.")
        import holdout_ledger as HL
        for g in FROZEN["targets"]:
            chk = HL.check("H97", f"G{g:02d}", "content_kickoff_memory", "embedding_content")
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
        r = analyze(g, allow)
        if r is not None:
            per[g] = r
    big = {g: r for g, r in per.items() if r["primary"]["N"] >= L.MIN_N_TRANSITION and r["primary"]["n_placebo"] > 0}
    d = np.array([r["primary"]["drho_full"] for r in big.values()]); se = np.array([r["primary"]["se_drho_full"] for r in big.values()])
    m = L.dl_meta(d, se)
    c1 = bool(m["mean"] - 1.645 * m["se"] > 0 and np.mean(d > 0) >= FROZEN["C1_frac"])
    dp = np.array([r["primary"]["drho_par"] - r["primary"]["drho_perp"] for r in big.values()])
    c2p = float(binomtest(int((dp > 0).sum()), len(dp), 0.5, alternative="greater").pvalue) if len(dp) else np.nan
    c2 = bool(len(dp) and np.mean(dp > 0) >= FROZEN["C2_frac"] and c2p < FROZEN["C2_p"])
    sa = L.dl_meta([r["center"].get("shape_a", np.nan) for r in big.values()], [r["center"].get("se_shape_a", np.nan) for r in big.values()])
    c3 = bool(sa["mean"] - 1.645 * sa["se"] > 0)
    # C4 out-of-sample agent constancy
    ex = pl.read_parquet(L.DATA / "NE34/chi_agents.parquet").filter((pl.col("cfg") == "primary") & pl.col("same_regime")
                                                                    & pl.col("chi_mem").is_finite())
    ex = L.rank_within(ex, "chi_mem").group_by("agent").agg(pl.col("rk").mean().alias("ex"), pl.len().alias("nex"))
    hold = []
    for g, r in per.items():
        ch = r["primary"]["chi_mem_i"]; ag = r["primary"]["agents"]
        order = np.argsort(np.argsort(ch)); n = len(ch)
        hold += [dict(agent=a, rk=(o + 1) / (n + 1)) for a, o in zip(ag, order)]
    ho = pl.DataFrame(hold).group_by("agent").agg(pl.col("rk").mean().alias("ho"), pl.len().alias("nho")) if hold else None
    c4 = dict(n=0)
    if ho is not None:
        j = ex.join(ho, on="agent").filter((pl.col("nex") >= FROZEN["C4_min_expl"]) & (pl.col("nho") >= FROZEN["C4_min_hold"]))
        if j.height >= 5:
            sp = spearmanr(j["ex"], j["ho"], alternative="greater")
            c4 = dict(n=j.height, rho=float(sp.statistic), p=float(sp.pvalue), pass_=bool(sp.pvalue < FROZEN["C4_p"]))
    out = dict(mode="dry-run" if a.dry_run else "CONFIRMATORY", goals=list(per), n_big=len(big), C1=dict(meta=m, frac=float(np.mean(d > 0)) if len(d) else None, pass_=c1),
               C2=dict(frac=float(np.mean(dp > 0)) if len(dp) else None, p=c2p, pass_=c2), C3=dict(meta=sa, pass_=c3), C4=c4,
               run_at=dt.datetime.now(dt.timezone.utc).isoformat())
    name = "confirm_dryrun.json" if a.dry_run else "confirm_results.json"
    (L.DATA / name).write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
