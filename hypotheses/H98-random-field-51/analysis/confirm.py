"""H98 confirmatory run on the LOCKED HOLDOUT (#51 tail, 2026-09-07 -> 09-21). Written and frozen 2026-10-04 after
round 1; NOT RUN.

Guard: held-out data are read only with BOTH `--confirm` and H98_CONFIRM=1, and only if `holdout_ledger.check` allows
the target. `--dry-run` runs the identical pipeline on a non-holdout stand-in unit (51g days, 2026-08-05 -> 08-21) and
writes to a scratch directory.

Frozen predictions (round-1 estimators, Amendments A0-A1; primary variant style_resid_period x bge_small):
  C1  Random-field dominance: R(tail) > R_CONTRAST_MAX (the largest round-1 contrast-unit R, frozen below).
  C2  No collective switching: lag-residualized W has p_W >= 0.05, and BC < 0.555.
  C3  Niche: beta_n (squared role-text overlap, non-rival pairs, covariates same lab + log reads) > 0 with
      jackknife z > 1.645, and the mediation gap G has a 95% CI including 0.
  C4  Not a direct coupling: beta_n with reads and replies (model B) >= 0.7 x beta_n without them (model A).
  C5  Weak pull: b_ex < 0.5.
  C6  (post hoc pattern from round 1, flagged) The niche acts through conversation: beta_n with reads and replies
      < 0.5 x beta_n without them.
Reading: C1, C2 and C3 together confirm the original claim ("#51 is a random-field system whose rival homophily is a
niche effect"). C3 failing with G > 0 (CI excluding 0) would move the reading to direct rival coupling (R3).
Round-1 expectation (dry run on the 51g stand-in, 2026-10-04): C1, C3, C5 and C6 pass; C2 and C4 fail, so the original
claim is expected NOT to confirm; the round-1 claim that stands is C1 + C3 + C6.

Reuse policy (hypotheses/holdout.md): the #51 tail has planned content users (H12, H13, H20, H22, H33). H22's
confirm_tail.py tests T_SR on the same co-movement estimator (C3r): whichever runs first makes the other a second user
of that statistic. H98's C1, C2, C3's niche slope and C4 are different statistics. Disclose in both cards and in LOG.md
before running.

Usage:
  uv run python hypotheses/H98-random-field-51/analysis/confirm.py --dry-run
  H98_CONFIRM=1 uv run python hypotheses/H98-random-field-51/analysis/confirm.py --confirm
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
import h98lib as L  # noqa: E402

ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
OUT = ROOT / "data/processed/H98-random-field-51/confirm"
SCRATCH = Path(os.environ.get("TMPDIR", "/tmp")) / "h98_confirm_dryrun"
TAIL = ("2026-09-07", "2026-09-21")
STANDIN = ("2026-08-05", "2026-08-21")
FROZEN = {"R_CONTRAST_MAX": 0.531,  # round 1: unit 41, style_resid_period x bge_small
           "BC": 0.555, "p_W": 0.05, "z_beta": 1.645, "C4_share": 0.7, "b_ex": 0.5}


def unit_days(lo: str, hi: str, allow_holdout: bool) -> list[str]:
    cal = pl.read_parquet(ROOT / "data/processed/shared/calendar.parquet").filter(
        (pl.col("goal_no") == 51) & (pl.col("n_agent_events") > 0) & (pl.col("pt_date") >= lo) & (pl.col("pt_date") < hi))
    if not allow_holdout:
        cal = cal.filter(~pl.col("holdout"))
    return sorted(cal["pt_date"].to_list())


def evaluate(root: Path, u: str) -> dict:
    U = L.load_unit(u, root=root)
    ad, hv, wn = U["ad"], U["hv"], U["wn"]
    import run_units as R  # noqa: E402  (same estimators and reference as round 1)
    refs = R.period_refs("style_resid_period", "bge_small")
    a, d = ad["agent"].to_numpy(), ad["day"].to_numpy()
    out = {"unit": u, "n_days": int(ad["day"].n_unique()), "n_agents": int(ad["agent"].n_unique())}
    out["R"] = L.disorder(U["S"], a, d, c_ref=refs[51])["R"]
    D = int(ad["day"].max()) + 1
    H1d, H2d = L.delta_halves(U["H1"], U["H2"], U["S"], hv["agent"].to_numpy(), hv["day"].to_numpy(), a, d)
    t = L.pq_test(H1d, H2d, hv["agent"].to_numpy(), hv["day"].to_numpy(), D, n_shift=2000, seed=4)
    out.update({"W": t["W"], "p_W": t["p_W"], "bc": t["bc"]})
    gg = L.gain(U["X"], wn["agent"].to_numpy(), wn["day"].to_numpy(), wn["win30"].to_numpy(), wn["room"].to_numpy(), B=200, seed=3)
    out.update({"b_ex": gg["b_ex"], "b_lo": gg["ci"][0], "b_hi": gg["ci"][1]})
    rv_all = L.role_table("bge_small", root)
    rv = {ag: rv_all[(ag, ro)] for ag, ro in zip(U["roles"]["agent"].to_list(), U["roles"]["role"].to_list()) if (ag, ro) in rv_all}
    J = L.comovement(U["X"], wn["agent"].to_numpy(), wn["day"].to_numpy(), wn["win30"].to_numpy(), min_shared=10)
    P = L.niche_overlap(U["pairs"].join(J, on=["i", "j"], how="inner"), rv)
    f = L.jackknife(P, lambda Q: L.niche_fit(Q, ("same_lab", "log_reads")), ["beta_n", "G"])
    fa = L.niche_fit(P, ("same_lab",))
    fb = L.niche_fit(P, ("same_lab", "log_reads", "log_replies"))
    out.update({"beta_n": f.get("beta_n"), "beta_n_se": f.get("beta_n_se"), "G": f.get("G"), "G_se": f.get("G_se"),
                "beta_A": fa.get("beta_n"), "beta_B": fb.get("beta_n"), "n_SR": f.get("n_SR")})
    return out


def score(r: dict) -> dict:
    s = {}
    s["C1"] = bool(FROZEN["R_CONTRAST_MAX"] is not None and r["R"] > FROZEN["R_CONTRAST_MAX"])
    s["C2"] = bool(r["p_W"] >= FROZEN["p_W"] and r["bc"] < FROZEN["BC"])
    z = r["beta_n"] / r["beta_n_se"] if r.get("beta_n_se") else np.nan
    g_lo, g_hi = r["G"] - 1.96 * r["G_se"], r["G"] + 1.96 * r["G_se"]
    s["C3"] = bool(np.isfinite(z) and z > FROZEN["z_beta"] and g_lo <= 0 <= g_hi)
    s["C3_detail"] = {"z_beta": z, "G_ci": [g_lo, g_hi]}
    s["C4"] = bool(r["beta_A"] and r["beta_B"] is not None and r["beta_A"] > 0 and r["beta_B"] >= FROZEN["C4_share"] * r["beta_A"])
    s["C5"] = bool(r["b_ex"] < FROZEN["b_ex"])
    s["C6_post_hoc"] = bool(r["beta_A"] and r["beta_A"] > 0 and r["beta_B"] is not None and r["beta_B"] < 0.5 * r["beta_A"])
    s["round1_claim"] = bool(s["C1"] and s["C3"] and s["C6_post_hoc"])
    s["confirmed"] = bool(s["C1"] and s["C2"] and s["C3"])
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.confirm == a.dry_run:
        sys.exit("choose exactly one of --confirm / --dry-run")
    me = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:12]
    if a.confirm:
        if os.environ.get("H98_CONFIRM") != "1":
            sys.exit("refused: set H98_CONFIRM=1 (Vivian's sign-off) to touch the locked holdout")
        import holdout_ledger as HL
        chk = HL.check("H98", "#51-tail", "message content", ["content_alignment"])
        if not chk["allowed"]:
            sys.exit(f"refused by the holdout ledger: {chk}")
        if chk["needs_disclosure"]:
            print("disclosure needed (holdout.md reuse policy):", [u["hypothesis"] for u in chk["competing_planned"]])
        days, root, allow = unit_days(*TAIL, allow_holdout=True), OUT, True
        days = [d for d in days if d >= TAIL[0]]
    else:
        days, root, allow = unit_days(*STANDIN, allow_holdout=False), SCRATCH, False
    if FROZEN["R_CONTRAST_MAX"] is None:
        sys.exit("FROZEN['R_CONTRAST_MAX'] is not set")
    u = "51T" if a.confirm else "51S"
    extra = [{"unit_id": u, "goal_no": 51, "first_day": days[0], "last_day": days[-1], "n_days": len(days), "days": days,
              "rooms": [0], "n_agents": 0}]
    B.main(allow_holdout=allow, out_root=root, extra_units=extra, only_units=[u])
    r = evaluate(root, u)
    s = score(r)
    res = {"mode": "confirm" if a.confirm else "dry-run", "script_sha": me, "frozen": FROZEN, "result": r, "score": s}
    root.mkdir(parents=True, exist_ok=True)
    (root / "confirm_result.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
