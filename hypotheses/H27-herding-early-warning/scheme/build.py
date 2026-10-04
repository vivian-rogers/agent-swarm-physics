"""H27 scheme: per-window project-occupancy series, one folder per goal period.

Builds data/processed/H27-herding-early-warning/G<NN>/ from H11's project labels (agent state (categorical,
project/artifact strict); H11 card, Data scheme), imported, never modified:
  series_w{15,30}.parquet   gwin, day, win, pt_date, n (labeled agents, incl. 'other'), k1..k8 (agents per real project)
  projects_w{15,30}.parquet label -> project (artifact name), agent-windows, share (copied from H11)
For periods H11 did not build (#51) the labels are made with H11's own builder functions (same parameters), into
this folder (G<NN>/h11labels/). #51 loses its locked tail (09-07 -> 09-21) through common.holdout_mask.

Also writes coverage.json (structural only: windows, fraction with n >= 3 at W = 15 and W = 30) used by the
pre-registered coverage rule, and _provenance.json.

Usage:  uv run python hypotheses/H27-herding-early-warning/scheme/build.py [--goals 31 37 ...]
Holdout periods are refused unless --allow-holdout (only analysis/confirm_holdout.py passes it, with --out).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
ROOT = Path(__file__).resolve().parents[3]
H11_SCHEME = ROOT / "hypotheses/H11-potts-labor-vs-herding/scheme"
sys.path.insert(0, str(H11_SCHEME))
import h11common as HC  # noqa: E402
import polars as pl  # noqa: E402

OUT = ROOT / "data/processed/H27-herding-early-warning"
H11_OUT = HC.OUT
QCOLS = [f"k{a}" for a in range(1, HC.Q_MAX + 1)]
WINDOWS = (15, 30)


def default_goals() -> list[int]:
    """Non-holdout single-regime periods with H11 labels (#2-#44 minus #36, which crosses 2026-03-24), plus #51."""
    gs = [g for g in HC.nonholdout_goals() if g != 36]
    return gs + [51]


def _h11_build():
    """H11's scheme/build.py as a module (functions only; its main() is not run). Loaded by path because this
    file is also called build.py."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("h11_scheme_build", H11_SCHEME / "build.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def h11_labels_for(goal: int, W: int, allow_holdout: bool, labdir: Path):
    """Return (labels, windows, projects) for one period at window W, from H11's folder or built with H11's code."""
    f = H11_OUT / f"G{goal:02d}"
    if (f / f"labels_project_w{W}.parquet").exists() and not allow_holdout:
        return (pl.read_parquet(f / f"labels_project_w{W}.parquet"), pl.read_parquet(f / f"windows_w{W}.parquet"),
                pl.read_parquet(f / f"projects_w{W}.parquet"))
    H11B = _h11_build()
    cal = H11B.load_calendar([goal], allow_holdout)
    if cal.height == 0:
        return None
    wins = H11B.window_table(cal, W)
    lp, proj = H11B.label_projects(H11B.build_project(cal, W, wins))
    labdir.mkdir(parents=True, exist_ok=True)
    lp.write_parquet(labdir / f"labels_project_w{W}.parquet", compression="zstd")
    wins.write_parquet(labdir / f"windows_w{W}.parquet", compression="zstd")
    proj.write_parquet(labdir / f"projects_w{W}.parquet", compression="zstd")
    return lp, wins, proj


def series(lab: pl.DataFrame, wins: pl.DataFrame) -> pl.DataFrame:
    wins = wins.sort("day", "win").with_row_index("gwin").with_columns(pl.col("gwin").cast(pl.Int32))
    n = lab.group_by("day", "win").agg(pl.len().cast(pl.Int16).alias("n"))
    real = lab.filter(pl.col("label") > 0)
    k = real.group_by("day", "win", "label").agg(pl.len().cast(pl.Int16).alias("k"))
    kw = k.pivot(on="label", index=["day", "win"], values="k") if k.height else pl.DataFrame({"day": [], "win": []})
    kw = kw.rename({c: f"k{c}" for c in kw.columns if c not in ("day", "win")})
    s = wins.select("gwin", "day", "win", "pt_date").join(n, on=["day", "win"], how="left").join(
        kw, on=["day", "win"], how="left") if kw.height else wins.select("gwin", "day", "win", "pt_date").join(
        n, on=["day", "win"], how="left")
    for c in QCOLS:
        if c not in s.columns:
            s = s.with_columns(pl.lit(0).alias(c))
    s = s.with_columns([pl.col(c).fill_null(0).cast(pl.Int16) for c in QCOLS] + [pl.col("n").fill_null(0).cast(pl.Int16)])
    return s.select("gwin", "day", "win", "pt_date", "n", *QCOLS).sort("gwin")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--goals", type=int, nargs="*", default=None)
    ap.add_argument("--allow-holdout", action="store_true", help="only for analysis/confirm_holdout.py")
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()
    goals = a.goals or default_goals()
    HC.assert_not_holdout(goals, a.allow_holdout)
    out = Path(a.out)
    if a.allow_holdout and out.resolve() == OUT.resolve():
        raise SystemExit("refusing: holdout builds must go to a separate --out folder")
    cov = {}
    for g in goals:
        f = out / f"G{g:02d}"
        cg = {}
        for W in WINDOWS:
            r = h11_labels_for(g, W, a.allow_holdout, f / "h11labels")
            if r is None:
                continue
            lab, wins, proj = r
            # guard: drop any held-out day that slipped in (exploration only)
            if not a.allow_holdout:
                m = HC.C.holdout_mask(wins["pt_date"].to_list(), [g] * wins.height)
                if any(m):
                    raise SystemExit(f"G{g}: holdout days present in labels; refusing")
            s = series(lab, wins)
            f.mkdir(parents=True, exist_ok=True)
            s.write_parquet(f / f"series_w{W}.parquet", compression="zstd")
            proj.filter(pl.col("label") > 0).select("label", "project", "aw", "share", "n_agents").sort("label").write_parquet(
                f / f"projects_w{W}.parquet", compression="zstd")
            q = int(proj.filter(pl.col("label") > 0)["label"].max() or 0)
            cg[f"w{W}"] = dict(windows=s.height, days=int(s["day"].n_unique()), q=q,
                               frac_n_ge3=float((s["n"] >= 3).mean()), mean_n=float(s["n"].mean()))
        if cg:
            cov[g] = cg
            print(g, cg)
    (out / "coverage.json").write_text(json.dumps(cov, indent=1))
    prov = {"built_by": "hypotheses/H27-herding-early-warning/scheme/build.py", "git_commit": HC.C.git_commit(),
            "inputs": [{"source": "ai-village", "revision": HC.C.REVISION,
                        "tables": ["artifacts", "artifact_mentions", "calendar", "rooms_timeline"],
                        "via": "data/processed/H11-potts-labor-vs-herding (H11 scheme/build.py; #51 built here with H11's functions)"}],
            "params": {"windows_min": list(WINDOWS), "goals": goals, "allow_holdout": a.allow_holdout,
                       "h11_params": {"q_max": HC.Q_MAX, "min_share": HC.MIN_SHARE, "strict_how": list(HC.STRICT_HOW)}},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (out / "_provenance.json").write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    main()
