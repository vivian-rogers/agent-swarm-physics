"""H06 round 1b scheme: the round-1 label sets rebuilt on the corrected shared inputs (2026-10-04).

Writes data/processed/H06-neutral-cooperative-dynamics/r1b/<scope>/ (no text, no project names except the id map):
  windows.parquet     identical window grid to round 1 (H11 window_table on the non-holdout calendar)
  labels_int.parquet  gwin, day, win, agent, room, age; intention clusters for four embedding variants:
                        gte_sr (PRIMARY, unprefixed columns km8 km24 km64 wd8 wd24 wd64): DQ5 gte-modernbert,
                               style_resid_period32 (H13 style features regressed out within goal period)
                        gte_w_*, bge_w_*, bge_sr_*: gte whitened only; bge whitened (round-1 basis, rebuilt from the
                               shared statement array); bge style-residualized
                      All variants cluster the same intents with the same rules (build.py: cluster_intents), so they
                      share one observation mask.
  labels_art.parquet  gwin, day, win, agent, room, project_id, carried_age: shared deterministic project_states
                      (w_min 30, sources all) with H06's carry-forward (round 1 used H11's nondeterministic files)
  labels_work.parquet gwin, day, win, agent, room, project_id, carried_age: agent state (categorical, project, work
                      ledger): repo with the most DQ4 agent work commits in the window (canonical & ~imported &
                      author_kind == agent & ~automated; author time), project_states tie rule, H06 carry-forward
  projects_{art,work}.parquet  project_id -> project (gitignored data only)
  scope.json
Scopes: the round-1 scopes (except the held-out G22) plus G35 (native: both rooms, room column kept) and G44best
(native: #best arm of #44, room 2).

Usage: H06_DATA=r1b uv run python hypotheses/H06-neutral-cooperative-dynamics/scheme/build_r1b.py [--scopes G31 ...]
Holdout periods and days are refused (no --allow-holdout here).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2"

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build as B  # noqa: E402  (round-1 scheme: calendar, windows, carry_forward, cluster_intents, room_at)

ROOT = B.ROOT
sys.path.insert(0, str(ROOT / "infra/shared"))
import project_states as PS  # noqa: E402

from infra.shared import common as C  # noqa: E402

SHARED = ROOT / "data/processed/shared"
EMB = SHARED / "embeddings"
OUT = ROOT / "data/processed/H06-neutral-cooperative-dynamics/r1b"
VARIANTS = {"gte_sr": "statements_style_resid_period32_gte_modernbert", "gte_w": "statements_white32_gte_modernbert",
            "bge_w": "statements_white32_bge_small", "bge_sr": "statements_style_resid_period32_bge_small"}
PRIMARY_VAR = "gte_sr"
WORK_FILTER = (pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind").cast(pl.String) == "agent")
               & ~pl.col("automated") & pl.col("author_agent").is_not_null())

SCOPES = {k: v for k, v in B.SCOPES.items() if k not in B.HOLDOUT_SCOPES}
SCOPES["G35"] = (35, None, "native (known project universe; both rooms)")
SCOPES["G44best"] = (44, 2, "native (#44 #best arm)")


def col(var: str, k: str) -> str:
    return k if var == PRIMARY_VAR else f"{var}_{k}"


def int_labels(goal, cal, wins, room_filter, scope):
    """Intention clusters for every embedding variant (same intents, same mask)."""
    blocks = B.BLOCKS.get(scope)
    if blocks:
        parts = []
        for bi, (bname, (d0, d1)) in enumerate(blocks.items()):
            cb = cal.filter((pl.col("pt_date") >= d0) & (pl.col("pt_date") <= d1))
            lab = int_labels(goal, cb, wins, room_filter, None)
            off = (bi + 1) * 1_000_000
            ccols = [c for c in lab.columns if c.split("_")[-1] in B.CLUSTERINGS]
            parts.append(lab.with_columns([(pl.col(c) + off).alias(c) for c in ccols]))
        return pl.concat(parts)
    st = pl.read_parquet(EMB / "statements.parquet").with_row_index("srow").filter(
        (pl.col("kind") == "intent") & (pl.col("goal_no") == goal) & ~pl.col("holdout"))
    st = st.join(cal.select("pt_date", "day", "win_start", "win_end"), on="pt_date", how="inner")
    st = st.filter((pl.col("t") >= pl.col("win_start")) & (pl.col("t") <= pl.col("win_end")))
    st = st.with_columns(((pl.col("t") - pl.col("win_start")).dt.total_seconds() // (B.W * 60)).cast(pl.Int16).alias("win"))
    st = B.room_at(st.drop("room"), "t")
    if room_filter is not None:
        st = st.filter(pl.col("room") == room_filter)
    st = st.join(wins.select("day", "win", "gwin"), on=["day", "win"], how="inner").sort("t", "srow")
    assert len(st["regime"].unique()) == 1
    rows = st["srow"].to_numpy()
    cl_all = {}
    for var, fname in VARIANTS.items():
        E = np.load(EMB / f"{fname}.npy", mmap_mode="r")
        X = np.asarray(E[np.sort(rows)], dtype=np.float64)[np.argsort(np.argsort(rows))]
        X /= np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-9)
        cl = B.cluster_intents(X, len(X), B.SEED + goal)
        cl_all.update({col(var, k): v for k, v in cl.items()})
    intents = st.select("t", "agent", "room", "day", "win", "gwin").with_columns([pl.Series(k, v) for k, v in cl_all.items()])
    cols = list(cl_all)
    last = intents.sort("t").group_by("gwin", "agent", maintain_order=True).agg(
        [pl.col("room").last()] + [pl.col(k).last() for k in cols])
    lab = None
    for k in ["room"] + cols:
        cf = B.carry_forward(last.select("gwin", "agent", k), wins, k, B.CARRY)
        lab = cf if lab is None else lab.join(cf.drop("age"), on=["gwin", "agent"], how="full", coalesce=True)
    return lab.join(wins.select("gwin", "day", "win"), on="gwin").sort("gwin", "agent")


def project_labels(lab: pl.DataFrame, wins: pl.DataFrame, room_filter):
    """lab: pt_date, win, agent, room, project -> carried labels with project ids."""
    lab = lab.join(wins.select("pt_date", "win", "gwin"), on=["pt_date", "win"], how="inner")
    if room_filter is not None:
        lab = lab.filter(pl.col("room") == room_filter)
    proj = lab.select(pl.col("project").cast(pl.String)).unique().sort("project").with_row_index("project_id")
    lab = lab.with_columns(pl.col("project").cast(pl.String)).join(proj, on="project").with_columns(
        pl.col("project_id").cast(pl.Int32), pl.col("gwin").cast(pl.Int32))
    cf = B.carry_forward(lab.select("gwin", "agent", "project_id"), wins, "project_id", B.CARRY).rename({"age": "carried_age"})
    room = B.carry_forward(lab.select("gwin", "agent", "room"), wins, "room", B.CARRY).drop("age")
    cf = cf.join(room, on=["gwin", "agent"], how="left")
    return cf.join(wins.select("gwin", "day", "win"), on="gwin").sort("gwin", "agent"), proj


def art_labels(goal, wins, room_filter):
    ps = pl.read_parquet(SHARED / "project_states.parquet").filter(
        (pl.col("w_min") == 30) & (pl.col("sources").cast(pl.String) == "all") & (pl.col("goal_no") == goal)
        & ~pl.col("holdout")).select("pt_date", "win", "agent", "room", "project")
    return project_labels(ps, wins, room_filter)


def work_labels(goal, cal, wins, room_filter):
    wc = pl.scan_parquet(SHARED / "work_commits.parquet").filter(WORK_FILTER).select(
        pl.col("repo").cast(pl.String).alias("project"), "t", pl.col("author_agent").alias("agent")).collect()
    calg = cal.select("pt_date", "goal_no", "day", "win_start", "win_end")
    wc = PS.assign_windows(wc, calg, B.W)
    fs = pl.read_parquet(SHARED / "work_repos.parquet").select(pl.col("repo").cast(pl.String).alias("project"),
                                                               pl.col("first_commit_t").alias("first_seen")).drop_nulls()
    lab = PS.modal(wc, "project", fs)
    w = wins.select("goal_no", "pt_date", "day", "win", "t_mid")
    lab = PS.attach_rooms(lab, w)
    return project_labels(lab.select("pt_date", "win", "agent", "room", "project"), wins, room_filter)


def build_scope(scope):
    goal, room_filter, role = SCOPES[scope]
    held = set(C.load_holdout()["goal_periods_held_out"])
    if goal in held:
        raise SystemExit(f"refusing: #{goal} is held out")
    cal = B.calendar(goal, allow_holdout=False)
    assert not cal["ho"].any()
    wins = B.windows(cal)
    out = OUT / scope
    out.mkdir(parents=True, exist_ok=True)
    lint = int_labels(goal, cal, wins, room_filter, scope)
    art, pa = art_labels(goal, wins, room_filter)
    work, pw = work_labels(goal, cal, wins, room_filter)
    wins.write_parquet(out / "windows.parquet", compression="zstd")
    lint.write_parquet(out / "labels_int.parquet", compression="zstd")
    art.write_parquet(out / "labels_art.parquet", compression="zstd")
    work.write_parquet(out / "labels_work.parquet", compression="zstd")
    pa.write_parquet(out / "projects_art.parquet", compression="zstd")
    pw.write_parquet(out / "projects_work.parquet", compression="zstd")
    T = max(wins.height, 1)
    info = {"scope": scope, "goal": goal, "room_filter": room_filter, "role": role, "days": int(cal.height),
            "windows": int(wins.height), "pt_dates": cal["pt_date"].to_list(),
            "labelled_aw": {"int": lint.height, "art": art.height, "work": work.height},
            "per_window": {"int": lint.height / T, "art": art.height / T, "work": work.height / T}}
    (out / "scope.json").write_text(json.dumps(info, indent=1))
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scopes", nargs="*", default=None)
    a = ap.parse_args()
    if os.environ.get("H06_DATA") != "r1b":
        raise SystemExit("round-1b scheme: set H06_DATA=r1b (round 1 is scheme/build.py)")
    scopes = a.scopes or list(SCOPES)
    for s in scopes:
        i = build_scope(s)
        pw = i["per_window"]
        print(f"{s}: days {i['days']} windows {i['windows']} | per window int {pw['int']:.1f} art {pw['art']:.1f} "
              f"work {pw['work']:.1f}", flush=True)
    prov_p = OUT / "_provenance.json"
    prov = json.loads(prov_p.read_text()) if prov_p.exists() else {}
    prov["labels"] = {
        "built_by": "hypotheses/H06-neutral-cooperative-dynamics/scheme/build_r1b.py", "git_commit": C.git_commit(),
        "inputs": [{"source": "ai-village", "revision": C.REVISION,
                    "tables": ["calendar", "rooms_timeline", "project_states", "work_commits", "work_repos",
                               "embeddings/statements", "embeddings/statements_white32_{bge_small,gte_modernbert}",
                               "embeddings/statements_style_resid_period32_{bge_small,gte_modernbert}"]}],
        "params": {"W": B.W, "carry": B.CARRY, "ladder": list(B.M_LADDER), "variants": VARIANTS, "primary": PRIMARY_VAR,
                   "work_filter": "canonical & ~imported & author_kind == agent & ~automated (DQ4 default); author time",
                   "art": "project_states w_min 30 sources all", "scopes": {k: list(v) for k, v in SCOPES.items()},
                   "scopes_built": sorted(set(prov.get("labels", {}).get("params", {}).get("scopes_built", [])) | set(scopes))},
        "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    prov_p.write_text(json.dumps(prov, indent=1, default=str))


if __name__ == "__main__":
    main()
