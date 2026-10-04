"""H105 confirmatory tests on the LOCKED HOLDOUT. Written 2026-10-04 after exploratory round 1; NOT RUN.

Guard: both flags, a clean git state for H105's code, and a holdout-ledger check:
  uv run python hypotheses/H105-two-state-goal-order/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
--dry-run runs the identical in-memory pipeline on non-holdout stand-ins (kickoffs #12, #17, #21, #25, #39, #40, #41; unit 51g
for C3). Without flags it prints the frozen predictions.

After Amendment 1 the tilt's variance test (P1) and the coupling change (P3) are not identifiable at village sampling, so
the confirmatory tests use what exploration showed is measurable:
  C1  two-state variance scaling across held-out kickoff transitions (#9, #14, #15, #28, #29, #34, #43, #45-#50 where
      eligible: same regime, A's first unit has >= 2 days after day 1): Spearman(observed ln V_A/V_F, tilt-predicted) > 0,
      one-sided p < 0.05 (exploration: 0.86, p = 0.0003, n = 16). The fraction with |rho_V| < ln 1.5 is reported (0.44).
  C2  field specificity: median transverse occupancy in A within 0.03 of F in >= 2/3 of those transitions (exploration 3/3).
  C3  private fields carry no collective switching: in the #51 tail (unit 51m), own-goal loop gain g2 < 0.2 (bge-small)
      (exploration: median -0.08 bge, +0.19 gte over 12 units; model-dependent).
Excluded: #22/#23 and #32 (H10's confirmatory directions stay blind). Reuse: H54's confirm uses the same held-out kickoffs
(day-1 target percentile, a different statistic); H22/H98 plan #51-tail content tests. Disclose in both cards and LOG.md.
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
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h105lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
from embed_models import goal_vectors, load_whitener  # noqa: E402

ED = L.ROOT / "data/processed/shared/embeddings"
SH = L.ROOT / "data/processed/shared"
FROZEN = {"targets": [9, 14, 15, 28, 29, 34, 43, 45, 46, 47, 48, 49, 50], "standins": [12, 17, 21, 25, 39, 40, 41],
          "tail_unit": "51m", "standin_unit": "51g", "model": "bge_small", "q": 95, "C1_p": 0.05, "C2_tol": 0.03,
          "C2_frac": 2 / 3, "C3_max_g": 0.2, "exclude": [22, 23, 32], "seed": 20261004}
FILES = ["hypotheses/H105-two-state-goal-order/analysis/confirm.py", "hypotheses/H105-two-state-goal-order/analysis/h105lib.py"]


def git_clean():
    out = subprocess.run(["git", "-C", str(L.ROOT), "status", "--porcelain", "--", *FILES], capture_output=True, text=True).stdout
    return out.strip() == ""


def unitv(v):
    return v / np.linalg.norm(v)


def statements(allow_holdout):
    st = pl.read_parquet(ED / "statements.parquet").with_row_index("row").filter(
        (pl.col("agent") != 19) & ~pl.col("goal_no").is_in(FROZEN["exclude"]) & pl.col("win30").is_not_null())
    if not allow_holdout:
        from common import holdout_mask
        st = st.filter(~pl.Series(holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list())))
    return st


def decoy_rows(regime, excl, rng):
    from common import holdout_mask
    st = pl.read_parquet(ED / "statements.parquet").with_row_index("row").filter(
        (pl.col("regime") == regime) & ~pl.col("goal_no").is_in(list(excl) + FROZEN["exclude"]))
    st = st.filter(~pl.Series(holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list())))   # decoys never held out
    r = st["row"].to_numpy()
    return np.sort(rng.choice(r, min(10000, len(r)), replace=False))


def transition(A, st, Z, rng):
    m = FROZEN["model"]
    goals = pl.read_parquet(ED / "goals.parquet")
    pu = pl.read_parquet(SH / "period_units.parquet").sort("goal_no", "seq")
    F = A - 1
    sF, sA = st.filter(pl.col("goal_no") == F), st.filter(pl.col("goal_no") == A)
    if sF.height == 0 or sA.height == 0 or sF["regime"][0] != sA["regime"][0]:
        return None
    reg = sA["regime"][0]
    uA = pu.filter(pl.col("goal_no") == A).row(0, named=True)
    dA = sorted(set(uA["days"]) & set(sA["pt_date"].to_list()))[1:]
    uF = pu.filter(pl.col("goal_no") == F).row(-1, named=True)
    dF = sorted(set(uF["days"]) & set(sF["pt_date"].to_list()))[-5:]
    if len(dA) < 2 or not dF:
        return None
    W = load_whitener(reg, 32, m); GV = goal_vectors(m).astype(np.float64)
    parts = [unitv(W(GV[g][None, :])[0]) for g in goals.filter((pl.col("goal_no") == A) & pl.col("kind").is_in(["goal", "kickoff"]))["gid"].to_list()]
    g = unitv(np.sum(parts, axis=0))
    sub = st.filter(((pl.col("goal_no") == F) & pl.col("pt_date").is_in(dF)) | ((pl.col("goal_no") == A) & pl.col("pt_date").is_in(dA)))
    sub = sub.with_columns(pl.when(pl.col("goal_no") == F).then(pl.lit("F")).otherwise(pl.lit("A")).alias("seg"))
    Zs = np.asarray(Z[sub["row"].to_numpy()], dtype=np.float64)
    Zd = np.asarray(Z[decoy_rows(reg, {A - 1, A, A + 1}, rng)], dtype=np.float64)
    on = Zs @ g > np.percentile(Zd @ g, FROZEN["q"])
    TF = L.spin_tables(sub, on, "F"); TA = L.spin_tables(sub, on, "A")
    ag = L.common_agents(TF, TA)
    if len(ag) < 4:
        return None
    TF, TA = L.restrict(TF, ag), L.restrict(TA, ag)
    core = L.pair_core(TF["S"], TA["S"])
    R = rng.normal(size=(50, 32)); R = R - (R @ g)[:, None] * g; R = R / np.linalg.norm(R, axis=1, keepdims=True)
    q = np.percentile(Zd @ R.T, 95, axis=0); Y = Zs @ R.T
    pf, pa = [], []
    for j in range(50):
        c = L.pair_core(L.restrict(L.spin_tables(sub, Y[:, j] > q[j], "F"), ag)["S"], L.restrict(L.spin_tables(sub, Y[:, j] > q[j], "A"), ag)["S"])
        pf.append(c["pF"]); pa.append(c["pA"])
    return dict(A=A, n_agents=len(ag), rho=core["rho"], growth_obs=core["growth_obs"], growth_pred=core["growth_pred"],
                pF=core["pF"], pA=core["pA"], perp_pF=float(np.median(pf)), perp_pA=float(np.median(pa)))


def own_goal_g(unit, st, Z, rng):
    m = FROZEN["model"]
    pu = pl.read_parquet(SH / "period_units.parquet").filter(pl.col("unit_id") == unit).row(0, named=True)
    sub = st.filter((pl.col("goal_no") == 51) & pl.col("pt_date").is_in(pu["days"]))
    goals = pl.read_parquet(ED / "goals.parquet").filter((pl.col("kind") == "agent_goal") & pl.col("valid_to").is_null())
    W = load_whitener("III", 32, m); GV = goal_vectors(m).astype(np.float64)
    Zd = np.asarray(Z[decoy_rows("III", {50, 51}, rng)], dtype=np.float64)
    Zs = np.asarray(Z[sub["row"].to_numpy()], dtype=np.float64)
    on = np.zeros(sub.height, bool); has = np.zeros(sub.height, bool); ag = sub["agent"].to_numpy()
    for r in goals.iter_rows(named=True):
        g = unitv(W(GV[r["gid"]][None, :])[0]); msk = ag == r["agent"]
        on[msk] = Zs[msk] @ g > np.percentile(Zd @ g, FROZEN["q"]); has[msk] = True
    s2 = sub.filter(pl.Series(has)).with_columns(pl.lit("X").alias("seg"))
    T = L.spin_tables(s2, on[has], "X")
    keep = [a for j, a in enumerate(T["agents"]) if np.isfinite(T["S"][:, j]).sum() >= L.MIN_WINDOWS]
    T = L.restrict(T, keep)
    s = L.seg_stats(T["S"])
    return dict(unit=unit, N=len(keep), T=s["T"], g_own=s["g"], R_own=s["R"], p_own=s["p"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ok", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    print(json.dumps(FROZEN, indent=1))
    if a.dry_run:
        goals, unit, allow = FROZEN["standins"], FROZEN["standin_unit"], False
    elif a.confirm and a.ok:
        if not git_clean():
            sys.exit("H105 code has uncommitted changes; commit the frozen version first.")
        import holdout_ledger as HL
        for tgt in [f"G{g:02d}" for g in FROZEN["targets"]] + ["#51-tail"]:
            chk = HL.check("H105", tgt, "content_goal_occupancy", "embedding_content")
            if not chk["allowed"]:
                sys.exit(f"ledger refuses {tgt}")
            if chk["needs_disclosure"]:
                print("disclose:", tgt, [u["hypothesis"] for u in chk["prior_runs"] + chk["competing_planned"]])
        goals, unit, allow = FROZEN["targets"], FROZEN["tail_unit"], True
    else:
        print("Frozen predictions printed; nothing run.")
        return
    rng = np.random.default_rng(FROZEN["seed"])
    st = statements(allow)
    Z = np.load(ED / f"statements_white32_{FROZEN['model']}.npy", mmap_mode="r")
    rows = [r for g in goals if (r := transition(g, st, Z, rng)) is not None]
    df = pl.DataFrame(rows)
    ok = df.filter(pl.col("growth_obs").is_finite() & pl.col("growth_pred").is_finite())
    sp = spearmanr(ok["growth_obs"], ok["growth_pred"], alternative="greater") if ok.height >= 4 else None
    c1 = dict(n=ok.height, rho=float(sp.statistic) if sp else None, p=float(sp.pvalue) if sp else None,
              frac_inside=float((df["rho"].abs() < L.LN15).mean()), pass_=bool(sp and sp.pvalue < FROZEN["C1_p"]))
    flat = ((df["perp_pA"] - df["perp_pF"]).abs() <= FROZEN["C2_tol"])
    c2 = dict(frac=float(flat.mean()), pass_=bool(flat.mean() >= FROZEN["C2_frac"]))
    t = own_goal_g(unit, st, Z, rng)
    c3 = dict(**t, pass_=bool(np.isfinite(t["g_own"]) and t["g_own"] < FROZEN["C3_max_g"]))
    out = dict(mode="dry-run" if a.dry_run else "CONFIRMATORY", transitions=rows, C1=c1, C2=c2, C3=c3,
               run_at=dt.datetime.now(dt.timezone.utc).isoformat())
    (L.DATA / ("confirm_dryrun.json" if a.dry_run else "confirm_results.json")).write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps({k: v for k, v in out.items() if k != "transitions"}, indent=1, default=float))


if __name__ == "__main__":
    main()
