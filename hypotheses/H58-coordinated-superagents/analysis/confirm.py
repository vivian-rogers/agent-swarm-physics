"""H58 CONFIRMATORY test on the LOCKED HOLDOUT. Written 2026-10-04 after exploratory round 1. NOT RUN.

Refuses to read any holdout day unless BOTH flags are given:
    --confirm --i-understand-this-uses-the-locked-holdout
`--dry-run` runs the identical statistics on non-holdout stand-ins (no holdout day is read).

Frozen criteria (also in the card, "Confirmatory design"; machine-readable in PREDICTIONS below):
  C1  Re-acquisition after forced erasures (NE41) in the holdout regime-III units (#45, #46, #47, #49, #50, #51 tail):
      among divergent events (k_pre != k_G) with a commit before the next reset, the erasure does NOT raise P(group)
      vs placebo: pooled MH log-OR (by agent) for "group" has z < 2; and the erasure does not lower P(own): MH log-OR
      for "own" > -0.2. (Round 1: P(group) z +1.5, P(own) log-OR -0.03.) Supported (agent + own artifact holds) if
      both; failed if the group log-OR z >= 2.
  C2  Others do not compensate a member's forced erasure: the change in the other community members' commits on R_G
      in the 15 min after, vs placebo, is <= 0 (point estimate) and its z < 2. (Round 1: -0.60 commits, z -5.9, i.e.
      others dip too, in step.)
  C3  Replication (layer 1) in the holdout units with >= 2 days, >= 100 agent work commits, >= 4 committing agents:
      number of units with an effective-superagent candidate under the round-1 decision rule (amended A1/A2) <= 1/3 of
      units (H58 refuted at these units) -- counted as refuting only in units with >= 100 active bins (the powered
      regime of the synthetic); the #51 tail is the main one.
  C4  NE24 artifact migration (GitHub -> GitLab, 2026-06-29; inside #50, NE21+NE23 window): the store-scramble test of
      "agent + own artifact". For each agent with an own repo (>= 50% of its commits, >= 3 commits) in the 2 active
      days before the migration day: the share of agents whose first gitlab.com commits within the 3 active days after
      go to a repo with the same name stem (repo basename, lowercase, '-'/'_' removed) as their own pre-migration repo
      is >= 0.5 ("the individual + its artifact identity survive the medium change"); and the coordination gain of
      the pre-migration multi-layer communities computed on the post-migration days (gitlab repos) does not qualify
      (no group store re-forms on the new medium beyond the individual threads).
  (P4/P5, the Krakauer unit-individuality and night-gain tests, are not confirmed: A2.2 found them not identifiable.)

Holdout reuse (hypotheses/holdout.md policy; infra/shared/holdout_ledger.py check()): H01's confirm_r2.py targets
NE24 (crew re-formation rate on gitlab, C4 there) and NE30 (not used here). This script's NE24 statistic is per-agent
own-artifact continuity by repo-name stem plus the coordination gain of the allocation state: a different statistic,
not examined by anyone. #45-#50 and the #51 tail are targeted by many scripts for other modalities (activity timing,
content, kicks); C1-C3 use the work ledger x context ledger re-acquisition and allocation-state statistics, which no
run has computed there. Disclose in the H58 and H01 cards and LOG.md before running; commit the script first.

Run:   uv run python hypotheses/H58-coordinated-superagents/analysis/confirm.py --dry-run
Real:  ... --confirm --i-understand-this-uses-the-locked-holdout     (only after Vivian signs off)
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ[_v] = "2"

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h58data as HD  # noqa: E402
import h58lib as L  # noqa: E402

PREDICTIONS = {
    "C1": "NE41 re-acquisition (holdout regime-III units): MH log-OR(group | erasure vs placebo) z < 2 AND MH log-OR(own) > -0.2",
    "C2": "others' commits on R_G in 15 min after a member's forced erasure vs placebo: estimate <= 0 and z < 2",
    "C3": "units with an effective-superagent candidate <= 1/3 of eligible holdout units (refuting only where >= 100 bins)",
    "C4": "NE24: share of agents whose first gitlab commits (3 active days) continue their own repo stem >= 0.5 AND pre-migration communities do not qualify on post-migration days",
}
HOLDOUT_UNITS = [("45", 45, None, None), ("46", 46, None, None), ("47", 47, None, None), ("49", 49, None, None),
                 ("50", 50, None, None), ("51m", 51, "2026-09-07", None)]
STANDIN_UNITS = ["39", "40", "41", "51c", "51d"]     # dry-run stand-ins for C1-C3; #39 -> #40 store reorganization for C4
NE24_DAY = "2026-06-29"
CONF_DIR = HD.D / "confirm"


def stem(repo: str) -> str:
    return re.sub(r"[-_]", "", repo.rstrip("/").split("/")[-1].lower().removesuffix(".git"))


def build_holdout_panels():
    """Re-run the round-1 scheme on the holdout units into data/processed/H58-coordinated-superagents/confirm/ (guard
    lifted only here, only behind the two flags)."""
    import build as B
    B.UNIT_SPEC = HOLDOUT_UNITS
    B.OUT = CONF_DIR
    B.guard = lambda df, name, **kw: df                  # noqa: E731  holdout allowed (confirmatory)
    orig_units = B.units

    def units_holdout():
        cal = pl.read_parquet(B.SH / "calendar.parquet").sort("pt_date")
        out = []
        for (u, g, lo, hi) in HOLDOUT_UNITS:
            c = cal.filter(pl.col("goal_no") == g)
            if lo:
                c = c.filter(pl.col("pt_date") >= lo)
            if hi:
                c = c.filter(pl.col("pt_date") < hi)
            out.append({"unit": u, "goal_no": g, "regime": str(c["regime"][0]), "days": c["pt_date"].to_list(),
                        "n_days": c.height, "win_start": [t.isoformat() for t in c["win_start"].to_list()],
                        "win_end": [t.isoformat() for t in c["win_end"].to_list()]})
        return out
    B.units = units_holdout
    B.INCLUDE_HOLDOUT = True        # the scheme's _nh() filters pass holdout rows only in this build
    # notes: H34's markers exist for the non-holdout corpus only (co-adoption layer empty here); content k-means is
    # refit on all windows (descriptive g_content only)
    B.main()
    B.units = orig_units


def c1_c2(units: list[str]) -> dict:
    import reacq as RQ
    meta = [x for x in HD.units_meta() if x["unit"] in units]
    E = pl.read_parquet(HD.D / "erasures.parquet")
    ev = RQ.collect_events(meta, E) if hasattr(RQ, "collect_events") else None
    if ev is None:
        return {"note": "reacq.collect_events not available"}
    res = RQ.statistics(ev, meta)
    c1 = res.get("P6c_forced_group", {}), res.get("P6c_forced_own", {})
    ok1 = bool(c1[0].get("z") is not None and c1[0]["z"] < 2 and c1[1].get("logor") is not None and c1[1]["logor"] > -0.2)
    p7 = res.get("P7_forced", {})
    ok2 = bool(p7.get("d_others") is not None and p7["d_others"] <= 0 and (p7.get("z_others") or 0) < 2)
    return {"C1": {"group": c1[0], "own": c1[1], "pass": ok1}, "C2": {**p7, "pass": ok2}}


def c3(units: list[str]) -> dict:
    import run as RUN
    rows = []
    for u in units:
        r = RUN.run_unit(u)
        rows.append({"unit": u, "nB": r["nB"], "any_candidate": r["summary"]["any_candidate"]})
    n = len(rows)
    k = sum(r["any_candidate"] for r in rows)
    powered = [r for r in rows if r["nB"] >= 100]
    return {"rows": rows, "n_units": n, "n_candidate": k, "pass": bool(k <= n / 3),
            "powered": {"n": len(powered), "n_candidate": sum(r["any_candidate"] for r in powered)}}


def c4(pre_unit: str, post_unit: str, cut_day: str | None, dry: bool) -> dict:
    """Own-artifact continuity across a store change. Dry run: #39 (own worlds) -> #40 (one universe repo)."""
    repos = dict(pl.read_parquet(HD.D / "repos.parquet").select("repo_id", "repo").iter_rows())
    C = pl.read_parquet(HD.D / "commits.parquet")
    pre = C.filter(pl.col("unit") == pre_unit)
    post = C.filter(pl.col("unit") == post_unit)
    if cut_day:
        pre = pre.filter(pl.col("pt_date") < cut_day)
        post = post.filter(pl.col("pt_date") >= cut_day)
    pre_days = sorted(pre["pt_date"].unique().to_list())[-2:]
    post_days = sorted(post["pt_date"].unique().to_list())[:3]
    pre = pre.filter(pl.col("pt_date").is_in(pre_days))
    post = post.filter(pl.col("pt_date").is_in(post_days))
    tot = pre.group_by("repo_id").agg(pl.len().alias("tot"))
    own = pre.group_by("agent", "repo_id").agg(pl.len().alias("n")).join(tot, on="repo_id") \
        .filter((pl.col("n") >= 3) & (pl.col("n") >= 0.5 * pl.col("tot")))
    rows = []
    for a in own["agent"].unique().to_list():
        stems = {stem(repos[r]) for r in own.filter(pl.col("agent") == a)["repo_id"].to_list()}
        pa = post.filter(pl.col("agent") == a).sort("pt_date", "m")
        if not dry:
            pa = pa.filter(pl.col("repo_id").map_elements(lambda r: repos[r].startswith("gitlab.com"), return_dtype=pl.Boolean))
        if pa.height == 0:
            rows.append({"agent": a, "continues": None})
            continue
        first = [stem(repos[r]) for r in pa["repo_id"].head(5).to_list()]
        rows.append({"agent": a, "continues": bool(set(first) & stems)})
    ev = [r for r in rows if r["continues"] is not None]
    share = float(np.mean([r["continues"] for r in ev])) if ev else None
    return {"pre_days": pre_days, "post_days": post_days, "rows": rows, "share_continue": share,
            "pass_continuity": bool(share is not None and share >= 0.5)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    a = ap.parse_args()
    if a.confirm and not a.ack:
        sys.exit("refusing: --confirm needs --i-understand-this-uses-the-locked-holdout")
    if not a.confirm and not a.dry_run:
        sys.exit("give --dry-run (non-holdout stand-ins) or --confirm --i-understand-this-uses-the-locked-holdout")
    out = {"predictions": PREDICTIONS, "mode": "confirm" if a.confirm else "dry-run",
           "run_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    if a.confirm:
        sys.path.insert(0, str(ROOT / "infra/shared"))
        import holdout_ledger as HL
        for tgt in ("NE21+NE23", "#51-tail", "G45"):
            out[f"ledger_{tgt}"] = HL.check("H58", tgt, "work ledger x context ledger", ["work_output", "artifact_lineage"])
        build_holdout_panels()
        HD.set_base(CONF_DIR)
        HD.ALLOW_HOLDOUT = True
        units = [u for (u, *_r) in HOLDOUT_UNITS]
        r3 = [u for u in units]
        out.update(c1_c2(r3))
        out["C3"] = c3(units)
        out["C4"] = c4("50", "50", NE24_DAY, dry=False)
        dest = HD.D.parent / "H58-coordinated-superagents" / "results" / "confirm.json"
    else:
        out.update(c1_c2(STANDIN_UNITS))
        out["C3"] = c3(["38b", "51e"])                 # small stand-ins to exercise the code path
        out["C4"] = c4("39", "40", None, dry=True)
        dest = HD.D / "results" / "confirm_dryrun.json"
    from run import jsonable
    dest.write_text(json.dumps(jsonable(out), indent=1))
    print(json.dumps(jsonable({k: v for k, v in out.items() if k != "predictions"}), indent=1)[:4000])


if __name__ == "__main__":
    main()
