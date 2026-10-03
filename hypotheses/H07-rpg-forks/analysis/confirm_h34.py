"""H07 CONFIRMATORY test on the held-out #34 lineage (2026-03-05 15:51 UTC -> fork point A). NOT RUN.

Predictions C1-C2 are written in the card (section "Confirmatory predictions", 2026-10-03) before any #34 commit,
author, message or file list was looked at. Running this script on #34 requires the explicit flag
    uv run python hypotheses/H07-rpg-forks/analysis/confirm_h34.py --i-am-confirming
Without it, the script only does a DRY RUN on non-holdout stand-ins (#35 data) to test the code path.

C1  Persistent mutation propensity ("hot files"). Per-file touch counts on rpg-game/main during #34 (non-merge
    commits; files present in the ancestor A) predict which ancestor files were changed in BOTH forks by the end of
    #35: AUC >= 0.65; the top quartile of #34 touches has >= 2x the both-changed rate of the bottom half; and the
    co-change excess (observed both-changed / independence expectation; 2.4 for all files in exploration) falls
    to <= 1.5 once the expectation is computed within #34-touch quartiles.
C2  Touch clock transfers. In the second half of #34, the src-file copy fraction relative to the mid-#34 snapshot
    (end of 2026-03-10 PT), against cumulative touches to those reference files, has a single-exponential rate
    mu_ref within a factor 1.5 of the #35 value computed by the same function (pooled best+rest).
Inputs: the bare partial clone data/raw/repos/rpg-game.git (commit metadata and trees only), plus H07 processed
tables. Outputs (only when confirming): data/processed/H07-rpg-forks/confirm_h34.json.
"""
from __future__ import annotations

import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import polars as pl
from scipy.optimize import curve_fit
from scipy.stats import rankdata

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h07lib import P, ROOT, T0, T35_END, UTC

REPOS = ROOT / "data/raw/repos"
T34_START = dt.datetime(2026, 3, 5, 15, 51, 21, 731000, tzinfo=UTC)
MID34_END = dt.datetime(2026, 3, 11, 7, 0, tzinfo=UTC)  # end of PT day 2026-03-10
SEP = "\x1f"


def git(repo, *a):
    return subprocess.run(["git", "-C", str(REPOS / f"{repo}.git"), *a], capture_output=True, text=True,
                          check=True).stdout


def commit_log(repo, rev_range, since=None, until=None):
    """[(sha, t_commit, is_merge, [(status, path)])] on a range, oldest first (trees only)."""
    args = ["log", "--no-renames", "--name-status", "--reverse", f"--format=@@%H{SEP}%P{SEP}%cI"]
    if since:
        args.append(f"--since={since.isoformat()}")
    if until:
        args.append(f"--until={until.isoformat()}")
    out, cur = [], None
    for line in git(repo, *args, rev_range).splitlines():
        if line.startswith("@@"):
            h, par, tc = line[2:].split(SEP)
            cur = [h, dt.datetime.fromisoformat(tc).astimezone(UTC), len(par.split()) > 1, []]
            out.append(cur)
        elif line.strip() and cur is not None:
            st, path = line.split("\t", 1)
            cur[3].append((st[0], path))
    return out


def tree(repo, sha):
    return dict((ln.split("\t", 1)[1], ln.split()[2]) for ln in git(repo, "ls-tree", "-r", sha).splitlines())


def auc(score, label):
    score, label = np.asarray(score, float), np.asarray(label, bool)
    pos, neg = score[label], score[~label]
    if len(pos) == 0 or len(neg) == 0:
        return np.nan
    gt = (pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()
    return float(gt / (len(pos) * len(neg)))


def c1(touch: dict, files_A: list, changed_b: set, changed_r: set) -> dict:
    """Hot-file test: touch counts (predictor) vs. changed in both forks (outcome), over ancestor files."""
    x = np.array([touch.get(f, 0) for f in files_A], float)
    yb = np.array([f in changed_b for f in files_A])
    yr = np.array([f in changed_r for f in files_A])
    both = yb & yr
    ranks = rankdata(x, method="average")  # tied files share a quartile
    q = np.minimum(3, ((ranks - 0.5) / len(x) * 4).astype(int))
    top, bottom = both[q == 3], both[q <= 1]
    exp_global = len(files_A) * yb.mean() * yr.mean()
    exp_strat = sum((q == k).sum() * yb[q == k].mean() * yr[q == k].mean() for k in range(4) if (q == k).any())
    return {"n_files": len(files_A), "n_both": int(both.sum()), "auc": auc(x, both),
            "rate_top_q": float(top.mean()) if len(top) else None,
            "rate_bottom_half": float(bottom.mean()) if len(bottom) else None,
            "ratio_top_vs_bottom": float(top.mean() / bottom.mean()) if len(bottom) and bottom.mean() > 0 else None,
            "excess_global": float(both.sum() / exp_global) if exp_global else None,
            "excess_stratified": float(both.sum() / exp_strat) if exp_strat else None,
            "pass": None}


def mu_ref(ref_tree: dict, commits: list, snapshots: list) -> float:
    """Single-exponential rate of the src-file copy fraction vs. cumulative touches to reference src files.
    commits: [(t, [(status, path)])] non-merge, in order; snapshots: [(t, tree)] along the lineage, in order."""
    ref = {p: b for p, b in ref_tree.items() if p.startswith("src/") and p.endswith(".js")}
    xs, ys = [0.0], [1.0]
    for ts, tr in snapshots:
        n = sum(1 for t, files in commits if t <= ts for st, p in files if p in ref)
        xs.append(float(n))
        ys.append(float(np.mean([tr.get(p) == b for p, b in ref.items()])))
    xs, ys = np.array(xs), np.array(ys)
    p, _ = curve_fit(lambda x, mu: np.exp(-mu * x), xs, ys, p0=[0.001], bounds=([0], [10]))
    return float(p[0])


def lineage_snapshots(repo, base, head, until):
    chain = git(repo, "rev-list", "--first-parent", "--reverse", f"{base}..{head}").split()
    out = []
    for sha in chain:
        t = dt.datetime.fromisoformat(git(repo, "show", "-s", "--format=%cI", sha).strip()).astimezone(UTC)
        if t <= until:
            out.append((t, tree(repo, sha)))
    return out


def end35_changed(A_tree):
    fp = pl.read_parquet(P / "fp_trees.parquet")
    cc = pl.read_parquet(P / "curves_commit.parquet")
    res = {}
    for lin in ("best", "rest"):
        sha = cc.filter((pl.col("lineage") == lin) & (pl.col("t") <= T35_END)).sort("k")["sha"][-1]
        tr = dict(fp.filter(pl.col("sha") == sha).select("path", "blob").iter_rows())
        res[lin] = {p for p, b in A_tree.items() if tr.get(p) != b}
    return res


def mu35_pooled(A, A_tree):
    vals = []
    for lin, repo in (("best", "rpg-game-best"), ("rest", "rpg-game-rest")):
        cm = [(t, files) for _, t, m, files in commit_log(repo, f"{A}..main") if not m and t <= T35_END]
        snaps = lineage_snapshots(repo, A, "main", T35_END)
        vals.append(mu_ref(A_tree, cm, snaps))
    return float(np.mean(vals)), vals


def main():
    confirming = "--i-am-confirming" in sys.argv
    prov = json.loads((P / "_provenance.json").read_text())
    A = prov["build_lineages"]["params"]["ancestor"]
    A_tree = tree("rpg-game", A)
    changed = end35_changed(A_tree)
    files_A = sorted(A_tree)
    mu35, mu35_each = mu35_pooled(A, A_tree)
    out = {"mu35_pooled": mu35, "mu35_best_rest": mu35_each}
    if not confirming:
        # DRY RUN on non-holdout stand-ins: predictor = rest-lineage touches on #35 day 1 (03-16 PT);
        # C2 stand-in = rest lineage with the end of 03-17 PT as pseudo-midpoint.
        print("DRY RUN (no #34 data touched).")
        rest = commit_log("rpg-game-rest", f"{A}..main")
        d1_end = dt.datetime(2026, 3, 17, 7, 0, tzinfo=UTC)
        touch = {}
        for _, t, m, files in rest:
            if not m and t <= d1_end:
                for st, p in files:
                    touch[p] = touch.get(p, 0) + 1
        out["C1_standin"] = c1(touch, files_A, changed["best"], changed["rest"])
        mid = dt.datetime(2026, 3, 18, 7, 0, tzinfo=UTC)
        snaps = lineage_snapshots("rpg-game-rest", A, "main", T35_END)
        ref_t = [tr for t, tr in snaps if t <= mid][-1]
        later = [(t, tr) for t, tr in snaps if t > mid]
        cm = [(t, files) for _, t, m, files in rest if not m and mid < t <= T35_END]
        out["C2_standin_mu"] = mu_ref(ref_t, cm, later)
        print(json.dumps(out, indent=1, default=str))
        return
    # ---------------- CONFIRMATORY (#34 held out): run once, after the card's predictions are locked
    log34 = [(sha, t, m, files) for sha, t, m, files in commit_log("rpg-game", A, since=T34_START)
             if T34_START <= t]
    touch = {}
    for _, t, m, files in log34:
        if not m:
            for st, p in files:
                touch[p] = touch.get(p, 0) + 1
    r1 = c1(touch, files_A, changed["best"], changed["rest"])
    r1["pass"] = bool(r1["auc"] >= 0.65 and (r1["ratio_top_vs_bottom"] or 0) >= 2 and
                      (r1["excess_stratified"] or 9) <= 1.5)
    # C2: second half of #34 relative to the mid-#34 snapshot
    first = [s for s, t, m, f in log34]
    base = git("rpg-game", "rev-list", "-1", f"--until={MID34_END.isoformat()}", A).strip()
    ref_t = tree("rpg-game", base)
    later = lineage_snapshots("rpg-game", base, A, T0)
    cm = [(t, files) for _, t, m, files in log34 if not m and t > MID34_END]
    mu34 = mu_ref(ref_t, cm, later)
    r2 = {"mu34_second_half": mu34, "mu35_pooled": mu35, "ratio": mu34 / mu35 if mu35 else None}
    r2["pass"] = bool(r2["ratio"] is not None and 1 / 1.5 <= r2["ratio"] <= 1.5)
    out.update({"C1": r1, "C2": r2, "n_commits_34": len(first), "run_at": dt.datetime.now(UTC).isoformat()})
    (P / "confirm_h34.json").write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
