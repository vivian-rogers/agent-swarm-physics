"""H70 confirmatory script (LOCKED HOLDOUT). Written 2026-10-04 after exploratory round 1. NOT RUN.

Frozen predictions (thresholds fixed from round 1 before any holdout data is loaded):
  C1 NE24 (GitHub -> GitLab, 2026-06-29, inside #50): on the first two migration days (06-29, 06-30 PT), the share of
     agents' first work commits of the day that go to their own project (repo-name stem of the last commit before the
     day, matched across hosts) is >= 0.5. Allocation survives the medium change.                                 [0.6]
  C2 NE24: agent-paired daily work commits on 06-29..06-30 fall below each agent's mean over the 5 preceding weekdays
     by >= 20% (paired mean ratio - 1 <= -0.2, bootstrap CI below 0). Replacing the artifact medium costs output.   [0.55]
  C3 call-scale context cost (Poisson, F vs P) pooled over the held-out regime-III targets lies in [0.25, 0.55] with
     the CI excluding 0 (round 1: 0.41 [0.38, 0.44]).                                                             [0.85]
  C4 no artifact-channel value: pooled DeltaV_rel,A (open x scramble, Poisson) has its CI including 0 or below 0
     (round 1: -0.05 [-0.13, +0.01]).                                                                              [0.7]
  C5 the artifact pointer carries allocation bits: pooled I_A > 0 with the CI above 0 (round 1: 0.14 [0.12, 0.16]). [0.8]
Targets: NE24 (#50), G43, G45, G46, G47, G48, G49, G50, #51 tail (2026-09-07 -> 09-21).

Reuse disclosure (hypotheses/holdout.md): NE21+NE23 (#46-#50) was run by H04 (Hawkes, activity) and is planned by many
(H01 C4 and H58 C4 also target NE24 with allocation-continuity statistics: H70's C1 is a close cousin of theirs and
must be disclosed as such); #45 by H02/H04. H70's statistics (allocation bits and Poisson value of channels at forced
erasures; output across the migration) are work-ledger statistics. Disclose in the card and LOG.md before running.

Safeguards: refuses without --confirm --i-understand-this-uses-the-locked-holdout; refuses unless this file, the card,
h70lib.py, run.py, scheme/build.py and infra/shared/semantic_kappa.py are tracked and unmodified; calls
holdout_ledger.check() per target; --dry-run uses non-holdout stand-ins (G41, G42, G44, #51 08-24 -> 09-04; for NE24
the #39 -> #40 boundary, 2026-05-04) from the exploratory tables and asserts that no held-out day is present.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h70lib as L  # noqa: E402

K = L.K
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
SH = ROOT / "data/processed/shared"
FILES = ["hypotheses/H70-artifact-store-semantic-info/analysis/confirm.py",
         "hypotheses/H70-artifact-store-semantic-info/README.md",
         "hypotheses/H70-artifact-store-semantic-info/analysis/h70lib.py",
         "hypotheses/H70-artifact-store-semantic-info/analysis/run.py",
         "hypotheses/H70-artifact-store-semantic-info/scheme/build.py", "infra/shared/semantic_kappa.py"]


def git_clean() -> bool:
    for f in FILES:
        tracked = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--error-unmatch", f],
                                 capture_output=True).returncode == 0
        dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", f], capture_output=True,
                               text=True).stdout.strip()
        if not tracked or dirty:
            print(f"refusing: {f} is untracked or modified", file=sys.stderr)
            return False
    return True


def stem(name: str | None) -> str | None:
    return None if name is None else name.rstrip("/").split("/")[-1].lower().replace("_", "-")


def migration_tests(ev: pl.DataFrame, repo_ids: pl.DataFrame, days: list[str], held: bool) -> dict:
    """C1 (stem-matched return on the migration days) and C2 (paired output ratio vs 5 preceding weekdays)."""
    names = dict(zip(repo_ids["rid"].to_list(), repo_ids["repo"].to_list()))
    n = ev.filter((pl.col("etype") == "N") & pl.col("pt_date").is_in(days) & (pl.col("A_prev") >= 0)
                  & (pl.col("X_next") >= 0))
    same = [stem(names.get(a)) == stem(names.get(x)) for a, x in zip(n["A_prev"].to_list(), n["X_next"].to_list())]
    c1 = {"n": n.height, "share_own_project": float(np.mean(same)) if same else None}
    wc = pl.read_parquet(SH / "work_commits.parquet", columns=["t", "pt_date", "author_agent", "author_kind", "canonical",
                                                             "imported", "automated", "holdout"])
    wc = wc.filter(pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind") == "agent") & ~pl.col("automated"))
    if not held:
        assert not wc.filter(pl.col("pt_date").is_in(days))["holdout"].any(), "holdout day in a dry run"
    d0 = dt.date.fromisoformat(min(days))
    pre, k = [], 1
    while len(pre) < 5:
        d = d0 - dt.timedelta(days=k)
        if d.weekday() < 5:
            pre.append(d.isoformat())
        k += 1
    daily = wc.group_by("author_agent", "pt_date").len()
    post = daily.filter(pl.col("pt_date").is_in(days)).group_by("author_agent").agg((pl.col("len").sum() / len(days)).alias("post"))
    base = daily.filter(pl.col("pt_date").is_in(pre)).group_by("author_agent").agg((pl.col("len").sum() / 5).alias("pre"))
    w = base.join(post, on="author_agent", how="left").with_columns(pl.col("post").fill_null(0)).filter(pl.col("pre") > 0)
    r = (w["post"] / w["pre"]).to_numpy() - 1
    bs = np.random.default_rng(24).choice(r, (2000, len(r))).mean(1) if len(r) else np.array([np.nan])
    c2 = {"n_agents": int(len(r)), "ratio_minus_1": float(np.mean(r)) if len(r) else None,
          "ci": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))], "pre_days": pre}
    return {"C1": c1, "C1_pass": bool(c1["share_own_project"] is not None and c1["share_own_project"] >= 0.5),
            "C2": c2, "C2_pass": bool(c2["ratio_minus_1"] is not None and c2["ratio_minus_1"] <= -0.2 and c2["ci"][1] < 0)}


def pooled_tests(ev: pl.DataFrame) -> dict:
    a = K.kappa_row(L.frame(ev, "call", "A"), B=300, seed=70)
    c = L.context_row(ev, "call", B=300, seed=71)
    out = {"A": {k: a[k] for k in ("I", "I_ci", "p_perm", "dV_rel", "dV_rel_ci", "n_scramble", "n_placebo")},
           "C": {k: c[k] for k in ("dV_rel", "dV_rel_ci", "I", "I_ci")}}
    out["C3_pass"] = bool(0.25 <= c["dV_rel"] <= 0.55 and c["dV_rel_ci"][0] is not None and c["dV_rel_ci"][0] > 0)
    out["C4_pass"] = bool(a["dV_rel_ci"][0] is not None and a["dV_rel_ci"][0] <= 0)
    out["C5_pass"] = bool(a["I_ci"][0] is not None and a["I_ci"][0] > 0)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    a = ap.parse_args()
    if a.dry_run:
        ev = L.load_events()
        from common import holdout_mask
        assert not any(holdout_mask(ev["pt_date"].to_list(), ev["goal_no"].to_list())), "holdout row in stand-ins"
        sel = ev.filter(pl.col("period").is_in(["G41", "G42", "G44"])
                        | ((pl.col("period") == "G51") & (pl.col("pt_date") >= "2026-08-24")))
        out = pooled_tests(sel)
        out.update(migration_tests(ev, pl.read_parquet(L.OUT / "repo_ids.parquet"), ["2026-05-04", "2026-05-05"], False))
        (L.OUT / "confirm_dryrun.json").write_text(json.dumps(out, indent=1, default=float))
        print(json.dumps(out, indent=1, default=float))
        return
    if not (a.confirm and a.ack):
        sys.exit("refusing: confirmatory runs need --confirm --i-understand-this-uses-the-locked-holdout")
    if not git_clean():
        sys.exit(2)
    import holdout_ledger as HL
    for t in ["NE21+NE23", "G43", "G45", "G46", "G47", "G48", "G49", "G50", "#51-tail"]:
        chk = HL.check("H70", t, "work_ledger", ["work_output", "artifact_lineage"])
        print(t, "allowed" if chk["allowed"] else "BLOCKED", "disclose" if chk["needs_disclosure"] else "")
        if not chk["allowed"]:
            sys.exit(f"refusing: {t} already used by the same estimator family")
    hold = json.loads((ROOT / "hypotheses/holdout.json").read_text())
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "goal_no"])
    tail = [w for w in hold["ne_windows"] if w["id"] == "#51-tail"][0]
    days = cal.filter(pl.col("goal_no").is_in([43, 45, 46, 47, 48, 49, 50])
                      | pl.col("pt_date").is_between(tail["start"], tail["end"], closed="left"))["pt_date"].to_list()
    spec = importlib.util.spec_from_file_location("h70build", ROOT / "hypotheses/H70-artifact-store-semantic-info/scheme/build.py")
    B = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(B)
    outdir = L.OUT / "confirm"
    B.build(days=days, held=True, out=outdir)
    ev = L.load_events(outdir / "events_confirm.parquet")
    out = pooled_tests(ev.filter(pl.col("regime") == "III"))
    out.update(migration_tests(ev, pl.read_parquet(outdir / "repo_ids.parquet"), ["2026-06-29", "2026-06-30"], True))
    (outdir / "confirm_results.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
