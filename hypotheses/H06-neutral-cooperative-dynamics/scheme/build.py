"""H06 scheme: project labels per agent slot per 30-min window, one folder per goal period.

Two label sources (card, "Data scheme"):
  art  H11's strict artifact-based project state (imported from hypotheses/H11-potts-labor-vs-herding/scheme/build.py,
       not modified): the raw project (repo / site / doc) an agent mentions most in the window, strict mentions only.
       H06 adds a carry-forward: an agent slot keeps its last project for up to CARRY-1 further windows of the same
       day when it has no strict mention (an agent slot holds one current project). Sensitivity: no carry-forward.
  int  clusters of self-written goals (intentions: session goals before 2026-03-24, CONSOLIDATE nextSessionGoal
       after), bge-small embeddings whitened per regime (common.load_whitener, 32 dims) and unit-normalized,
       clustered within the period. Ladder fixed a priori by the mean cluster size m in {8, 24, 64} intents:
       k-means (scipy kmeans2, k-means++ seeds) and Ward linkage, K = round(n_intents / m). The agent slot's label in
       a window is the cluster of its latest intention at or before the window end, the same day, written at most
       CARRY-1 windows earlier.

Outputs in data/processed/H06-neutral-cooperative-dynamics/<scope>/ (no text):
  windows.parquet      day, win, gwin (global window index), pt_date
  labels_art.parquet   gwin, day, win, agent, project_id (int32), carried (bool), carried0 label for no-carry
  labels_int.parquet   gwin, day, win, agent, age (windows since the intention), one int32 column per clustering
  intents.parquet      t, agent, day, win, regime, one int32 column per clustering (one row per intention)
  scope.json           agents, scope rule, counts
Scopes: G11, G16, G31, G37, G44 (#rest room only), G51 (non-holdout part), contrasts G19, G25, G30, G38, and the
spanning tests' sides G08, G10 (NE27).

Usage: uv run python hypotheses/H06-neutral-cooperative-dynamics/scheme/build.py [--scopes G31 G37 ...]
Holdout periods/days are refused unless --allow-holdout (used only by analysis/confirm_holdout.py).
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from infra.shared import common as C  # noqa: E402

H11_SCHEME = ROOT / "hypotheses/H11-potts-labor-vs-herding/scheme"
sys.path.append(str(H11_SCHEME))  # for h11common
_spec = importlib.util.spec_from_file_location("h11build", H11_SCHEME / "build.py")
h11build = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(h11build)

SHARED = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H06-neutral-cooperative-dynamics"
W = 30
CARRY = 4                      # a label is valid in its own window and the next 3 (2 h), same day
M_LADDER = (8, 24, 64)         # mean intents per cluster
METHODS = ("km", "wd")
CLUSTERINGS = [f"{m}{k}" for m in METHODS for k in M_LADDER]
PRIMARY = "km24"
REST_ROOM = 3
SEED = 20261004

# scope -> (goal, room filter or None, role)
SCOPES = {
    "G11": (11, None, "free"), "G16": (16, None, "free"), "G31": (31, None, "free"), "G37": (37, None, "free"),
    "G44": (44, REST_ROOM, "free (#rest)"), "G51": (51, None, "check (private goals)"),
    "G19": (19, None, "contrast (shared)"), "G25": (25, None, "contrast (shared)"), "G30": (30, None, "contrast (shared)"),
    "G38": (38, None, "contrast (shared)"),
    "G08": (8, None, "NE27 pre"), "G10": (10, None, "NE27 post"),
    "G22": (22, None, "CONFIRMATORY (holdout)"),
}
HOLDOUT_SCOPES = {"G22"}
# #51 is clustered within each analysis block (whole-period k-means on 28k intentions is O(n K^2) to seed);
# cluster ids are offset per block so they never coincide across blocks.
BLOCKS = {"G51": {"a": ("2026-07-06", "2026-07-10"), "b": ("2026-07-27", "2026-07-31"), "c": ("2026-08-24", "2026-08-28"),
                  "ne33": ("2026-08-31", "2026-09-04")}}


def calendar(goal: int, allow_holdout: bool) -> pl.DataFrame:
    cal = h11build.load_calendar([goal], allow_holdout)
    if not allow_holdout:
        cal = cal.filter(~pl.col("ho"))
    return cal


def windows(cal: pl.DataFrame) -> pl.DataFrame:
    w = h11build.window_table(cal, W).sort("day", "win").with_row_index("gwin")
    return w.with_columns(pl.col("gwin").cast(pl.Int32))


def room_at(df: pl.DataFrame, tcol: str) -> pl.DataFrame:
    """Attach each agent's room at time tcol from rooms_timeline."""
    rt = pl.read_parquet(SHARED / "rooms_timeline.parquet")
    keys = df.select("agent", tcol).unique()
    j = keys.join(rt, on="agent", how="left").filter(
        (pl.col("t_start") <= pl.col(tcol)) & (pl.col("t_end").is_null() | (pl.col(tcol) < pl.col("t_end"))))
    j = j.sort("t_start", descending=True).group_by("agent", tcol).agg(pl.col("room").first())
    return df.join(j, on=["agent", tcol], how="left").with_columns(pl.col("room").fill_null(0).cast(pl.Int8))


def carry_forward(lab: pl.DataFrame, wins: pl.DataFrame, col: str, carry: int) -> pl.DataFrame:
    """Expand per-window labels so each labelled window also labels the next carry-1 windows of the same day,
    unless the agent has a newer label. Returns gwin, agent, <col>, age."""
    if lab.height == 0:
        return lab.select("gwin", "agent", col).with_columns(pl.lit(0, pl.Int16).alias("age"))
    gday = dict(zip(wins["gwin"].to_list(), wins["day"].to_list()))
    out = []
    for (agent,), d in lab.sort("gwin").group_by(["agent"], maintain_order=True):
        g = d["gwin"].to_list()
        v = d[col].to_list()
        nxt = g[1:] + [10 ** 9]
        for gi, vi, gn in zip(g, v, nxt):
            for a in range(carry):
                gg = gi + a
                if gg >= gn or gday.get(gg) != gday.get(gi):
                    break
                out.append((gg, agent, vi, a))
    return pl.DataFrame(out, schema={"gwin": pl.Int32, "agent": pl.Int8, col: lab.schema[col], "age": pl.Int16}, orient="row")


def build_art(goal, cal, wins, room_filter):
    wins_h11 = wins.drop("gwin")
    lab = h11build.build_project(cal, W, wins_h11)  # strict artifact mentions, modal project per (agent, window)
    lab = lab.join(wins.select("day", "win", "gwin"), on=["day", "win"], how="inner")
    if room_filter is not None:
        lab = lab.filter(pl.col("room") == room_filter)
    proj = lab.select("project").unique().sort("project").with_row_index("project_id")
    lab = lab.join(proj, on="project").with_columns(pl.col("project_id").cast(pl.Int32))
    base = lab.select("gwin", "agent", "project_id")
    cf = carry_forward(base, wins, "project_id", CARRY).rename({"age": "carried_age"})
    out = cf.join(wins.select("gwin", "day", "win"), on="gwin").sort("gwin", "agent")
    return out, proj


def cluster_intents(X: np.ndarray, n_points: int, seed: int) -> dict:
    from scipy.cluster.hierarchy import fcluster, linkage
    from scipy.cluster.vq import kmeans2
    res = {}
    big = n_points > 8000
    for m in M_LADDER:
        K = max(2, int(round(n_points / m)))
        _, lab = kmeans2(X.astype(np.float64), K, minit="++", seed=np.random.default_rng(seed + m), iter=30)
        res[f"km{m}"] = lab.astype(np.int32)
    if not big:
        Z = linkage(X.astype(np.float64), method="ward")
        for m in M_LADDER:
            K = max(2, int(round(n_points / m)))
            res[f"wd{m}"] = (fcluster(Z, K, criterion="maxclust") - 1).astype(np.int32)
    else:  # Ward needs the full distance matrix; too large for #51 (k-means only)
        for m in M_LADDER:
            res[f"wd{m}"] = np.full(n_points, -1, dtype=np.int32)
    return res


def build_int(goal, cal, wins, room_filter, allow_holdout, scope=None):
    blocks = BLOCKS.get(scope)
    if blocks:
        parts_l, parts_i = [], []
        for bi, (bname, (d0, d1)) in enumerate(blocks.items()):
            cb = cal.filter((pl.col("pt_date") >= d0) & (pl.col("pt_date") <= d1))
            lab, ints = build_int(goal, cb, wins, room_filter, allow_holdout, scope=None)
            off = (bi + 1) * 1_000_000
            lab = lab.with_columns([(pl.col(k) + off).alias(k) for k in CLUSTERINGS])
            ints = ints.with_columns([(pl.col(k) + off).alias(k) for k in CLUSTERINGS] + [pl.lit(bname).alias("block")])
            parts_l.append(lab)
            parts_i.append(ints)
        return pl.concat(parts_l), pl.concat(parts_i)
    st = pl.read_parquet(SHARED / "embeddings/statements.parquet").filter(
        (pl.col("kind") == "intent") & (pl.col("goal_no") == goal))
    if not allow_holdout:
        st = st.filter(~pl.col("holdout"))
    st = st.join(cal.select("pt_date", "day", "win_start", "win_end"), on="pt_date", how="inner")
    st = st.filter((pl.col("t") >= pl.col("win_start")) & (pl.col("t") <= pl.col("win_end")))
    st = st.with_columns(((pl.col("t") - pl.col("win_start")).dt.total_seconds() // (W * 60)).cast(pl.Int16).alias("win"))
    if room_filter is not None:
        st = room_at(st.drop("room"), "t").filter(pl.col("room") == room_filter)
    st = st.join(wins.select("day", "win", "gwin"), on=["day", "win"], how="inner").sort("t")
    E = np.load(SHARED / "embeddings/intentions_bge_small.npy", mmap_mode="r")
    rows = st["src_row"].to_numpy()
    Xraw = np.asarray(E[np.sort(rows)], dtype=np.float32)[np.argsort(np.argsort(rows))]
    regimes = st["regime"].unique().to_list()
    assert len(regimes) == 1, f"period spans regimes {regimes}"
    Wh = C.load_whitener(regimes[0], 32)
    X = Wh(Xraw)
    X /= np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-9)
    cl = cluster_intents(X, len(X), SEED + goal)
    intents = st.select("t", "agent", "day", "win", "gwin", "regime").with_columns(
        [pl.Series(k, v) for k, v in cl.items()])
    # window labels: latest intention at or before the window end (same day), valid for CARRY windows
    last = intents.sort("t").group_by("gwin", "agent", maintain_order=True).agg([pl.col(k).last() for k in CLUSTERINGS])
    lab = None
    for k in CLUSTERINGS:
        cf = carry_forward(last.select("gwin", "agent", k), wins, k, CARRY)
        lab = cf if lab is None else lab.join(cf.drop("age"), on=["gwin", "agent"], how="full", coalesce=True)
    lab = lab.join(wins.select("gwin", "day", "win"), on="gwin").sort("gwin", "agent")
    return lab, intents


def build_scope(scope: str, allow_holdout: bool):
    goal, room_filter, role = SCOPES[scope]
    if scope in HOLDOUT_SCOPES and not allow_holdout:
        raise SystemExit(f"refusing: {scope} is in the locked holdout (hypotheses/holdout.json)")
    if not allow_holdout:
        held = set(C.load_holdout()["goal_periods_held_out"])
        if goal in held:
            raise SystemExit(f"refusing: goal #{goal} is held out")
    cal = calendar(goal, allow_holdout)
    wins = windows(cal)
    out = OUT / scope
    out.mkdir(parents=True, exist_ok=True)
    art, proj = build_art(goal, cal, wins, room_filter)
    lint, intents = build_int(goal, cal, wins, room_filter, allow_holdout, scope=scope)
    wins.write_parquet(out / "windows.parquet", compression="zstd")
    art.write_parquet(out / "labels_art.parquet", compression="zstd")
    lint.write_parquet(out / "labels_int.parquet", compression="zstd")
    intents.drop("t").with_columns(pl.col("agent")).write_parquet(out / "intents.parquet", compression="zstd")
    info = {"scope": scope, "goal": goal, "room_filter": room_filter, "role": role, "days": int(cal.height),
            "windows": int(wins.height), "pt_dates": cal["pt_date"].to_list(),
            "agents_art": sorted(set(art["agent"].to_list())), "agents_int": sorted(set(lint["agent"].to_list())),
            "labelled_aw_art": int(art.height), "labelled_aw_art_nocarry": int(art.filter(pl.col("carried_age") == 0).height),
            "labelled_aw_int": int(lint.height), "n_intents": int(intents.height),
            "mean_labelled_per_window_art": art.height / max(wins.height, 1),
            "mean_labelled_per_window_int": lint.height / max(wins.height, 1)}
    (out / "scope.json").write_text(json.dumps(info, indent=1))
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scopes", nargs="*", default=None)
    ap.add_argument("--allow-holdout", action="store_true", help="only for analysis/confirm_holdout.py")
    a = ap.parse_args()
    scopes = a.scopes or [s for s in SCOPES if s not in HOLDOUT_SCOPES]
    if any(s in HOLDOUT_SCOPES for s in scopes) and not a.allow_holdout:
        raise SystemExit("refusing: holdout scope requested without --allow-holdout")
    infos = {}
    for s in scopes:
        infos[s] = build_scope(s, a.allow_holdout)
        i = infos[s]
        print(f"{s}: days {i['days']} windows {i['windows']} | art {i['labelled_aw_art']} aw ({i['mean_labelled_per_window_art']:.1f}/win) "
              f"| int {i['n_intents']} intents, {i['labelled_aw_int']} aw ({i['mean_labelled_per_window_int']:.1f}/win)", flush=True)
    if not a.allow_holdout:
        prov = {"built_by": "hypotheses/H06-neutral-cooperative-dynamics/scheme/build.py", "git_commit": C.git_commit(),
                "inputs": [{"source": "ai-village", "revision": C.REVISION,
                            "tables": ["artifacts", "artifact_mentions", "calendar", "rooms_timeline", "intentions",
                                       "embeddings/statements", "embeddings/intentions_bge_small", "embeddings/whitening_<regime>"],
                            "via": "data/processed/shared; H11 scheme imported (hypotheses/H11-potts-labor-vs-herding/scheme/build.py: "
                                   "load_calendar, window_table, build_project)"}],
                "params": {"window_min": W, "carry_windows": CARRY, "m_ladder": list(M_LADDER), "methods": list(METHODS),
                           "primary": PRIMARY, "whitening_dims": 32, "seed": SEED, "rest_room": REST_ROOM,
                           "scopes": {k: list(SCOPES[k]) for k in scopes}},
                "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
        p = OUT / "_provenance.json"
        old = json.loads(p.read_text()) if p.exists() else {}
        old["scheme"] = prov
        p.write_text(json.dumps(old, indent=1))


if __name__ == "__main__":
    main()
