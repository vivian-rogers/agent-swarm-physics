"""H58 period-native tests (card N1-N3). Needs run.py's per-unit results.

N1 NE42 (#39 -> #40 -> #41): best-unit size and qualification across the A-B-A; in #40 the shared repo at FILE
   granularity (file groups from read-only git log, scheme files40.parquet): the coordination gain of its crew, the
   multi-layer communities and a calibrated file-level search, against the agent + own file null.
N2 #44: the coordination-first search vs the #best team (DQ6 room_assignment, preferred, non-holdout): Jaccard, its
   R_G (fine-tuning repo?), qualification; the known team evaluated directly; qualifying units inside #rest.
N3 #51 #focus cut (08-05 -> 08-24; units 51b -> 51c): pair coordination gain on joint artifacts, DiD for pairs split
   by the cut (one member mostly in #focus in 51c) vs pairs kept together; qualifying 51c units spanning both rooms.
Output: data/processed/H58-coordinated-superagents/results/natives.json
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ[_v] = "2"

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h58data as HD  # noqa: E402
import h58lib as L  # noqa: E402
from run import describe, jsonable  # noqa: E402

OUT = HD.D / "results"
FOCUS_ROOM = 15


def unit_res(name):
    return json.loads((OUT / "units" / f"{name}.json").read_text())


def best_summary(r):
    s = r["candidates"]["search"]
    multi = r["candidates"]["multi"]
    q_multi = [c for c in multi if c["qualifies"]]
    return {"search_agents": s[0]["agents"] if s else None, "search_n": s[0]["n"] if s else 0,
            "search_qual": bool(s and s[0].get("qualifies_search")), "search_g": s[0]["g"] if s else None,
            "search_p": s[0].get("p_search") if s else None, "search_z_comp": s[0]["z_comp"] if s else None,
            "search_z_shift": s[0]["z_shift"] if s else None, "search_spec": s[0].get("specificity") if s else None,
            "multi_qual_sizes": [c["n"] for c in q_multi],
            "largest_qual": max([c["n"] for c in q_multi] + ([s[0]["n"]] if (s and s[0].get("qualifies_search")) else []),
                                default=0)}


def n1():
    out = {u: best_summary(unit_res(u)) for u in ("39", "40", "41")}
    # file-level #40
    f = pl.read_parquet(HD.D / "files40.parquet")
    files = f.select("file").unique().sort("file").with_row_index("file_id").with_columns(pl.col("file_id").cast(pl.Int32))
    f = f.join(files, on="file").with_columns(pl.lit("40").alias("unit"))
    U = HD.load_unit("40", commits=f, repo_col="file_id")
    rooms = HD.modal_rooms(U)
    labs = HD.labs()
    cn = L.CompNull(U, n_draw=200, seed=40)
    crew = [a for a in range(U.nA) if U.act_a[a] >= 2]
    fl = {"n_files": len(U.repos), "n_writers": U.nA, "crew": describe(U, crew, cn, 40, rooms, labs, full=True)}
    M = L.layer_matrices(list(U.agents), HD.layer_rows("40"))
    comms = L.communities(M["multi"]) if M["multi"].sum() > 0 else []
    fl["multi"] = [describe(U, c, cn, 41 + i, rooms, labs, full=False) for i, c in enumerate(comms)]
    sr = L.search_calibrated(U, n_surr=19, seed=40, max_evals=3000, seeds=comms)
    if sr["members"]:
        ev = describe(U, sr["members"], cn, 49, rooms, labs, full=True)
        ev["p_search"] = sr["p_search"]
        ev["qualifies_search"] = bool(ev["qualifies"] and sr["p_search"] <= 0.05)
        fl["search"] = ev
    # own-file persistence and the hub file
    fname = dict(files.select("file_id", "file").iter_rows())
    hub = [k for k, r in enumerate(U.repos) if fname[r] == "main.js"]
    work = U.S >= 0
    fl["hub_share_of_working_bins"] = float((np.isin(U.S, hub) & work).sum() / max(work.sum(), 1))
    own_share = []
    for a in range(U.nA):
        w = U.S[a][U.S[a] >= 0]
        if len(w) >= 5:
            v, c = np.unique(w, return_counts=True)
            own_share.append(float(c.max() / len(w)))
    fl["median_top_file_share"] = float(np.median(own_share)) if own_share else None
    out["file_level_40"] = fl
    return out


def n2():
    r = unit_res("44")
    gt = pl.read_parquet(HD.SH / "ground_truth_labels.parquet").filter(
        (pl.col("goal_no") == 44) & pl.col("preferred") & ~pl.col("holdout") & (pl.col("label_kind") == "room_assignment"))
    team = sorted(gt.filter(pl.col("value") == "best")["agent"].to_list())
    rest = sorted(gt.filter(pl.col("value") == "rest")["agent"].to_list())
    repos = dict(pl.read_parquet(HD.D / "repos.parquet").select("repo_id", "repo").iter_rows())
    out = {"team": team, "n_rest": len(rest)}
    s = r["candidates"]["search"]
    if s:
        sa = set(s[0]["agents"])
        out["search"] = {"agents": s[0]["agents"], "jaccard_team": len(sa & set(team)) / len(sa | set(team)),
                         "qualifies_search": s[0].get("qualifies_search"), "g": s[0]["g"], "z_comp": s[0]["z_comp"],
                         "z_shift": s[0]["z_shift"], "specificity": s[0].get("specificity"), "p_search": s[0].get("p_search"),
                         "repos": [repos.get(k, str(k)).split("/")[-1] for k in s[0]["repos"]]}
    # the known team evaluated directly
    U = HD.load_unit("44")
    rooms = HD.modal_rooms(U)
    labs = HD.labs()
    cn = L.CompNull(U, n_draw=200, seed=44)
    tm = [U.agents.index(a) for a in team if a in U.agents]
    ev = describe(U, tm, cn, 44, rooms, labs, full=True)
    ev["repo_names"] = [repos.get(k, str(k)).split("/")[-1] for k in ev["repos"]]
    out["team_eval"] = ev
    # with the later-joining Opus 4.8 (agent 29) if it wrote on the team's repos
    if 29 in U.agents:
        ev2 = describe(U, sorted(tm + [U.agents.index(29)]), cn, 45, rooms, labs, full=False)
        out["team_plus_29"] = ev2
    # qualifying units entirely inside #rest (size >= 3)
    rest_q = []
    for key in ("multi", "w_sync", "w_coad", "w_reply", "w_coart", "crew", "search"):
        for c in r["candidates"].get(key, []):
            if c["n"] >= 3 and set(c["agents"]) <= set(rest) and (c["qualifies"] if key != "search" else c.get("qualifies_search")):
                rest_q.append({"from": key, "agents": c["agents"], "g": c["g"]})
    out["rest_qualifying_ge3"] = rest_q
    out["multi"] = [{"agents": c["agents"], "qualifies": c["qualifies"], "g": c["g"], "z_comp": c["z_comp"],
                     "z_shift": c["z_shift"], "specificity": c.get("specificity")} for c in r["candidates"]["multi"]]
    return out


def pair_gains(U, rmin=3):
    """Pair coordination gain on the pair's joint artifacts (repos both committed to, >= rmin commits in all)."""
    out = {}
    for i in range(U.nA):
        for j in range(i + 1, U.nA):
            joint = np.flatnonzero((U.Wn[i] > 0) & (U.Wn[j] > 0) & (U.tot_k >= rmin))
            if len(joint) == 0:
                continue
            g = L.coord_gain(U, [i, j], R=joint)
            if np.isfinite(g):
                out[(int(U.agents[i]), int(U.agents[j]))] = g
    return out


def n3():
    Ub, Uc = HD.load_unit("51b"), HD.load_unit("51c")
    rc = HD.modal_rooms(Uc)
    focus_share = {int(Uc.agents[a]): float((Uc.rooms[a] == FOCUS_ROOM).mean()) for a in range(Uc.nA)}
    focus = sorted(a for a, s in focus_share.items() if s >= 0.5)
    gb, gc = pair_gains(Ub), pair_gains(Uc)
    common = sorted(set(gb) & set(gc))
    split = [p for p in common if (p[0] in focus) != (p[1] in focus)]
    kept = [p for p in common if (p[0] in focus) == (p[1] in focus)]
    def dd(ps):
        return np.array([gc[p] - gb[p] for p in ps])
    ds, dk = dd(split), dd(kept)
    rng = np.random.default_rng(51)
    boots = []
    for _ in range(2000):
        a = ds[rng.integers(0, len(ds), len(ds))] if len(ds) else np.array([np.nan])
        b = dk[rng.integers(0, len(dk), len(dk))] if len(dk) else np.array([np.nan])
        boots.append(a.mean() - b.mean())
    boots = np.asarray(boots)
    pre_split = float(np.mean([gb[p] for p in split])) if split else None
    out = {"focus_agents": focus, "n_common_pairs": len(common), "n_split": len(split), "n_kept": len(kept),
           "pre_mean_split": pre_split, "pre_mean_kept": float(np.mean([gb[p] for p in kept])) if kept else None,
           "post_mean_split": float(np.mean([gc[p] for p in split])) if split else None,
           "post_mean_kept": float(np.mean([gc[p] for p in kept])) if kept else None,
           "did": float(ds.mean() - dk.mean()) if (len(ds) and len(dk)) else None,
           "did_ci": [float(np.nanpercentile(boots, 2.5)), float(np.nanpercentile(boots, 97.5))]}
    # qualifying 51c units spanning #focus and #general
    r = unit_res("51c")
    span = []
    for key in ("multi", "search"):
        for c in r["candidates"].get(key, []):
            q = c["qualifies"] if key == "multi" else c.get("qualifies_search")
            if q:
                ag = set(c["agents"])
                span.append({"from": key, "agents": c["agents"], "has_focus": bool(ag & set(focus)),
                             "has_general": bool(ag - set(focus)), "g": c["g"]})
    out["qualifying_51c"] = span
    return out


def main():
    res = {"N1": n1(), "N2": n2(), "N3": n3()}
    (OUT / "natives.json").write_text(json.dumps(jsonable(res), indent=1))
    print(json.dumps(jsonable(res), indent=1)[:8000])


if __name__ == "__main__":
    main()
