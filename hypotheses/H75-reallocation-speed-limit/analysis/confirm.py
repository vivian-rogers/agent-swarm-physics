"""H75 confirmatory tests on the LOCKED HOLDOUT. Written after exploratory round 1 (2026-10-04); NOT RUN.

Guard: the holdout is touched only with BOTH flags, a clean git state for H75's code, and a holdout-ledger check:
  uv run python hypotheses/H75-reallocation-speed-limit/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
Without the flags the script prints the frozen predictions and exits.

Targets (predictions frozen in FROZEN below and on the card, "Confirmatory predictions"):
  C1-C2  NE20 (2026-06-03, inside #45): one tool call per turn for Anthropic agents. Kickoff-settling DiD, Anthropic vs
         other labs, pre-NE20 kickoff #44 (non-holdout) vs post-NE20 kickoffs #46 and #47 (holdout). Per agent: t_i (first
         commit on the settled repo after the kickoff, 20-active-h horizon) and r_i (ledger calls per active hour).
         First stage: DiD in mean log r_i. Outcome: DiD in mean log t_i. Cadence elasticity eps = DiD log t / DiD log r.
  C3     transfer: kickoffs of #45, #46, #47 (W_pre; pre-kickoff days of #46/#47 are held out too, which the guard allows).
Reuse policy (hypotheses/holdout.md): #45-#47 are planned or used by H04, H30, H35 (activity / nudges) and H40 (reply hazard,
NE20). H75's statistic (repo re-allocation from DQ4 commits) is a different statistic and modality; disclose in both cards
and LOG.md when run. H40's NE20 confirm uses call rates as its first stage: the same first stage, a different outcome.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h75lib as L  # noqa: E402
import build as B  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))

FROZEN = {  # frozen 2026-10-04 after exploratory round 1 (card, "Confirmatory predictions")
    "horizon_h": 20.0,
    "C1_min_abs_did_logr": 0.10,     # NE20 first stage; otherwise C2 is not scored
    "C2_max_abs_eps": 0.3,           # |DiD log t / DiD log r| <= 0.3 and the DiD log t 95% CI contains 0
    "C2_kill_eps": -0.7,             # activity-limited: eps <= -0.7 with the DiD log t CI excluding 0
    "C3_freeze_S_max": 2.0,          # S_e <= 2 (instant freeze) in >= 2 of 3 holdout kickoffs (round 1: 3/4)
    "C3_tail_S90_min": 3.0,          # S_90 >= 3 (churn tail) in >= 2 of 3 holdout kickoffs (round 1: 3/4)
    "C3_freeze_T_max_h": 1.0,        # with T_e <= 1 active h
    "pre_goals": [44], "post_goals": [46, 47], "treated_lab": "Anthropic", "transfer_goals": [45, 46, 47],
}
FILES = ["hypotheses/H75-reallocation-speed-limit/analysis/confirm.py", "hypotheses/H75-reallocation-speed-limit/analysis/h75lib.py",
         "hypotheses/H75-reallocation-speed-limit/scheme/build.py"]


def git_clean() -> bool:
    out = subprocess.run(["git", "-C", str(L.ROOT), "status", "--porcelain", "--", *FILES], capture_output=True, text=True).stdout
    return out.strip() == ""


def agent_rows(goal: int) -> pl.DataFrame:
    clk = B.clock(goal, allow_holdout=True)
    E = B.ensemble(goal, "pre", FROZEN["horizon_h"], clk, allow_holdout=True)
    ag = L.agent_settling(E)
    cr = B.call_rates(clk, E.agents, 0.0, FROZEN["horizon_h"], allow_holdout=True)
    lab = dict(pl.read_parquet(L.SH / "roster.parquet").select("agent", "lab").iter_rows())
    return ag.with_columns(pl.col("agent").replace_strict(cr, default=None).alias("call_rate"),
                           pl.col("agent").replace_strict(lab, default=None).alias("lab"), pl.lit(goal).alias("goal"))


def did(df: pl.DataFrame, col: str, B_=500, seed=7) -> tuple[float, list]:
    d = df.filter(pl.col(col).is_not_null() & (pl.col(col) > 0)).with_columns(pl.col(col).log().alias("y"),
                                                                               (pl.col("lab") == FROZEN["treated_lab"]).alias("tr"))

    def est(x):
        m = x.group_by(["side", "tr"]).agg(pl.col("y").mean())
        g = {(r["side"], r["tr"]): r["y"] for r in m.iter_rows(named=True)}
        try:
            return (g[("post", True)] - g[("pre", True)]) - (g[("post", False)] - g[("pre", False)])
        except KeyError:
            return np.nan
    e = est(d)
    rng = np.random.default_rng(seed)
    bs = []
    for _ in range(B_):
        idx = rng.integers(0, d.height, d.height)
        bs.append(est(d[idx]))
    return float(e), [float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5))]


def run():
    import holdout_ledger as HL
    for tgt in ("G45", "G46", "G47", "NE21+NE23"):
        chk = HL.check("H75", tgt, "work_commits_reallocation", "artifact_lineage")
        print(tgt, "allowed" if chk["allowed"] else "NOT ALLOWED", "disclosure needed" if chk["needs_disclosure"] else "")
        if not chk["allowed"]:
            raise SystemExit("holdout ledger refuses a same-family reuse")
    rows = pl.concat([agent_rows(g).with_columns(pl.lit("pre").alias("side")) for g in FROZEN["pre_goals"]]
                     + [agent_rows(g).with_columns(pl.lit("post").alias("side")) for g in FROZEN["post_goals"]], how="diagonal_relaxed")
    fs, fs_ci = did(rows, "call_rate")
    out, out_ci = did(rows, "t_i")
    res = {"first_stage_did_logr": fs, "first_stage_ci": fs_ci, "did_logt": out, "did_logt_ci": out_ci}
    if abs(fs) < FROZEN["C1_min_abs_did_logr"]:
        res["C1"] = "first stage too weak: C2 not scored"
    else:
        eps = out / fs
        res["eps"] = eps
        res["C2_pass"] = bool(abs(eps) <= FROZEN["C2_max_abs_eps"] and out_ci[0] <= 0 <= out_ci[1])
        res["C2_kill"] = bool(eps <= FROZEN["C2_kill_eps"] and not (out_ci[0] <= 0 <= out_ci[1]))
    tr = {}
    for g in FROZEN["transfer_goals"]:
        E = B.ensemble(g, "pre", FROZEN["horizon_h"], B.clock(g, allow_holdout=True), allow_holdout=True)
        s = L.settle_stats(E)
        tr[g] = {k: s.get(k) for k in ("N", "T_e", "S_e", "T_90", "S_90", "W_e", "A_e")}
    nf = sum(1 for v in tr.values() if v["S_e"] is not None and v["S_e"] <= FROZEN["C3_freeze_S_max"]
             and v["T_e"] <= FROZEN["C3_freeze_T_max_h"])
    nt = sum(1 for v in tr.values() if v["S_90"] is not None and v["S_90"] >= FROZEN["C3_tail_S90_min"])
    res.update(transfer=tr, C3_freeze_pass=nf >= 2, C3_tail_pass=nt >= 2)
    L.write_json(L.OUTD / "confirm" / "confirm_results.json", res)
    print(res)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", action="store_true", dest="ack")
    a = ap.parse_args()
    if not (a.confirm and a.ack):
        print("H75 confirm.py: frozen predictions (not run):")
        for k, v in FROZEN.items():
            print(f"  {k}: {v}")
        print("Pass --confirm --i-understand-this-uses-the-locked-holdout to run on the holdout.")
        return
    if not git_clean():
        raise SystemExit("commit H75's code first (predictions and script must be committed before a confirmatory run)")
    run()


if __name__ == "__main__":
    main()
