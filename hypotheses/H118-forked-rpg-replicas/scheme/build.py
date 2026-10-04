"""H118 scheme: room-bin content centroids (split halves) for two-room periods, and the hourly code overlap of the RPG forks.

Outputs (data/processed/H118-forked-rpg-replicas/):
  statements.parquet        non-holdout statements of goals 35-44 in rooms #best (2) / #rest (3), with srow, agent, period
                            room, day index, active-hour bin, half (split-half label)
  ref_centres_<model>.npz   leave-own-period-out regime reference centre per period key
  centroids_<model>.npz     per (period, room, bin, half): agent-weighted centroid (float32, 32-d); index in centroids.parquet
  centroids.parquet         period, room, bin, day, hour, half, n_stmt, n_agent, row
  code_hourly.parquet       hourly (and later daily) code overlap of rpg-game-best vs rpg-game-rest on ancestor keys
  _provenance.json

Rules (card, Data scheme): room at a statement from infra/shared/rooms_asof.statement_rooms; agents keep the room
holding >= 80% of their in-room statements in the period (else dropped for that period); bins = active hours since the
day's calendar win_start (capped at the window end); halves = statement parity within (agent, bin), single-statement
agent-bins by agent-code parity. Period keys: '35', '36' (regime-III days 36b-c), '36a' (regime II, one day), '37',
'38', '39', '41', '42', '44'. Holdout rows are never read beyond the mask (asserted).

Usage: uv run python hypotheses/H118-forked-rpg-replicas/scheme/build.py
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import git_commit, holdout_mask  # noqa: E402
import rooms_asof  # noqa: E402

SH = ROOT / "data/processed/shared"
EMB = SH / "embeddings"
H07 = ROOT / "data/processed/H07-rpg-forks"
OUT = ROOT / "data/processed/H118-forked-rpg-replicas"
MODELS = ("bge_small", "gte_modernbert")
GOALS = (35, 36, 37, 38, 39, 41, 42, 44)
ROOMS = (2, 3)  # 2 = #best, 3 = #rest
T0 = dt.datetime(2026, 3, 16, 16, 20, 5, tzinfo=dt.timezone.utc)  # #35 kickoff = fork instant (H07)
END35 = dt.datetime(2026, 3, 23, 11, 17, tzinfo=dt.timezone.utc)   # H07's "end of #35"


def period_key(goal: int, regime: str) -> str | None:
    if goal == 36:
        return "36a" if regime == "II" else "36"
    return str(goal)


def statements() -> pl.DataFrame:
    st = pl.read_parquet(EMB / "statements.parquet").with_row_index("srow")
    roster = pl.read_parquet(SH / "roster.parquet")
    cc = roster.filter(pl.col("claude_code"))["agent"].to_list()
    st = st.filter(pl.col("goal_no").is_in(GOALS), ~pl.col("agent").is_in(cc))
    hm = holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list())
    st = st.filter(~pl.Series(hm)).filter(~pl.col("holdout"))
    assert not any(holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list()))
    st = rooms_asof.statement_rooms(st)
    st = st.with_columns(pl.when(pl.col("kind") == "chat").then(pl.col("room")).otherwise(pl.col("room_at")).alias("room_s"))
    st = st.filter(pl.col("room_s").is_in(ROOMS))
    cal = pl.read_parquet(SH / "calendar.parquet").select("pt_date", "win_start", "win_end")
    st = st.join(cal, on="pt_date", how="left")
    st = st.with_columns(
        ((pl.col("t") - pl.col("win_start")).dt.total_seconds() / 3600).floor().clip(0, None).cast(pl.Int16).alias("hour"),
        pl.struct("goal_no", "regime").map_elements(lambda r: period_key(r["goal_no"], str(r["regime"])),
                                                    return_dtype=pl.String).alias("period"))
    # cap hour at the window's last full hour
    st = st.with_columns(pl.min_horizontal(pl.col("hour"),
                                           ((pl.col("win_end") - pl.col("win_start")).dt.total_seconds() / 3600)
                                           .floor().cast(pl.Int16)).alias("hour"))
    # day index within period
    days = st.select("period", "pt_date").unique().sort("period", "pt_date").with_columns(
        pl.col("pt_date").rank("dense").over("period").cast(pl.Int16).alias("day"))
    st = st.join(days, on=["period", "pt_date"], how="left")
    # agent period room (>= 80% rule)
    ar = (st.group_by("period", "agent", "room_s").len().with_columns(
        (pl.col("len") / pl.col("len").sum().over("period", "agent")).alias("share"))
          .sort("period", "agent", "share", "room_s", descending=[False, False, True, False])
          .group_by("period", "agent", maintain_order=True).first())
    keep = ar.filter(pl.col("share") >= 0.8).select("period", "agent", pl.col("room_s").alias("room_p"))
    st = st.join(keep, on=["period", "agent"], how="inner").filter(pl.col("room_s") == pl.col("room_p"))
    # global bin index per period: (day, hour)
    st = st.sort("period", "t").with_columns((pl.col("day").cast(pl.Int32) * 100 + pl.col("hour")).alias("bin"))
    # halves: parity within (period, agent, bin)
    st = st.with_columns(pl.col("t").rank("ordinal").over("period", "agent", "bin").alias("r"),
                         pl.len().over("period", "agent", "bin").alias("nab"))
    st = st.with_columns(pl.when(pl.col("nab") == 1).then((pl.col("agent").cast(pl.Int32) % 2) + 1)
                         .otherwise(((pl.col("r") - 1) % 2) + 1).cast(pl.Int8).alias("half"))
    return st.select("srow", "kind", "agent", "t", "pt_date", "goal_no", "regime", "period", "day", "hour", "bin",
                     pl.col("room_s").alias("room"), "half")


def ref_centres(st: pl.DataFrame, model: str) -> dict:
    allst = pl.read_parquet(EMB / "statements.parquet").with_row_index("srow")
    hm = holdout_mask(allst["pt_date"].to_list(), allst["goal_no"].to_list())
    allst = allst.with_columns(pl.Series("hm", hm)).filter(~pl.col("hm") & ~pl.col("holdout"))
    X = np.load(EMB / f"statements_style_resid32_{model}.npy", mmap_mode="r")
    out = {}
    for pk in st["period"].unique().to_list():
        g = int(pk.rstrip("a"))
        reg = "II" if pk in ("35", "36a") else "III"
        sel = allst.filter((pl.col("regime").cast(pl.String) == reg) & (pl.col("goal_no") != g) & (pl.col("goal_no") != 51))
        idx = np.sort(sel["srow"].to_numpy())
        out[pk] = np.asarray(X[idx], dtype=np.float64).mean(0)
        out[pk + "_n"] = np.array([len(idx)])
    return out


def centroids(st: pl.DataFrame, model: str, ref: dict):
    X = np.load(EMB / f"statements_style_resid32_{model}.npy", mmap_mode="r")
    rows, vecs = [], []
    grp = st.sort("period", "room", "bin", "half", "agent").partition_by(["period", "room", "bin", "half"], as_dict=True,
                                                                       maintain_order=True)
    for (pk, room, b, h), g in sorted(grp.items()):
        V = np.asarray(X[g["srow"].to_numpy()], dtype=np.float64) - ref[pk]
        ag = g["agent"].to_numpy()
        means = np.stack([V[ag == a].mean(0) for a in np.unique(ag)])
        rows.append({"period": pk, "room": int(room), "bin": int(b), "day": int(b) // 100, "hour": int(b) % 100,
                     "half": int(h), "n_stmt": len(g), "n_agent": len(means), "row": len(vecs)})
        vecs.append(means.mean(0))
    return pl.DataFrame(rows), np.asarray(vecs, dtype=np.float32)


def code_hourly() -> pl.DataFrame:
    """Hourly code overlap of the two main forks on ancestor keys (files, src files, functions)."""
    fp = pl.read_parquet(H07 / "fp_trees.parquet")
    bf = pl.read_parquet(H07 / "blob_functions.parquet")
    cal = pl.read_parquet(SH / "calendar.parquet").select("pt_date", "win_start", "win_end", "holdout")
    anc = fp.filter(pl.col("lineage") == "ancestor").select("path", "blob")
    commits = (fp.filter(pl.col("lineage").is_in(["best", "rest"])).select("lineage", "sha", "k", "t_commit")
               .unique().sort("lineage", "k"))
    trees = {(r["lineage"], r["k"]): None for r in commits.iter_rows(named=True)}
    fpl = fp.filter(pl.col("lineage").is_in(["best", "rest"])).partition_by(["lineage", "k"], as_dict=True)
    # function key -> body hash for a tree: functions of src .js blobs keyed (path, qualname, k)
    def funcs(tree: pl.DataFrame) -> dict:
        j = tree.filter(pl.col("path").str.starts_with("src/") & pl.col("path").str.ends_with(".js")).select(
            "path", "blob").join(bf, on="blob", how="inner")  # select first: the tree's commit index k must not shadow bf.k
        return {(p, q, kk): h for p, q, kk, h in zip(j["path"], j["qualname"], j["k"], j["body_hash"])}
    anc_files = dict(zip(anc["path"], anc["blob"]))
    anc_src = {p: b for p, b in anc_files.items() if p.startswith("src/") and p.endswith(".js")}
    anc_fn = funcs(anc)
    # evaluation times: end of every active hour from T0 to END35, then end of each later non-holdout window to 05-28
    times = []
    for r in cal.filter((pl.col("win_start") >= T0 - dt.timedelta(hours=1)) & (pl.col("win_start") < END35)).sort("pt_date").iter_rows(named=True):
        t = r["win_start"]
        h = 0
        while t < r["win_end"]:
            t = min(r["win_start"] + dt.timedelta(hours=h + 1), r["win_end"])
            times.append((r["pt_date"], h, t, "hour"))
            h += 1
    for r in cal.filter((pl.col("win_start") >= END35) & (pl.col("pt_date") <= "2026-05-28") & ~pl.col("holdout")).sort("pt_date").iter_rows(named=True):
        times.append((r["pt_date"], -1, r["win_end"], "day"))
    cache = {}

    def state_at(lin: str, t):
        c = commits.filter((pl.col("lineage") == lin) & (pl.col("t_commit") <= t))
        if c.height == 0:
            return None, None, None, 0
        k = int(c["k"].max())
        if (lin, k) not in cache:
            tr = fpl[(lin, k)]
            files = dict(zip(tr["path"], tr["blob"]))
            cache[(lin, k)] = (files, funcs(tr))
        files, fn = cache[(lin, k)]
        return files, fn, k, c.height
    rows = []
    for pt, h, t, kind in times:
        sb = state_at("best", t)
        sr = state_at("rest", t)
        rec = {"pt_date": pt, "hour": h, "t": t, "kind": kind, "k_best": sb[2] or 0, "k_rest": sr[2] or 0}
        for fam, ancd, get in (("files", anc_files, 0), ("src", anc_src, 0), ("functions", anc_fn, 1)):
            vb = sb[get] if sb[0] is not None else None
            vr = sr[get] if sr[0] is not None else None
            if vb is None:
                vb = anc_files if get == 0 else anc_fn
            if vr is None:
                vr = anc_files if get == 0 else anc_fn
            keys = list(ancd)
            ub = np.array([vb.get(k) == ancd[k] for k in keys])
            ur = np.array([vr.get(k) == ancd[k] for k in keys])
            same = np.array([vb.get(k) is not None and vb.get(k) == vr.get(k) for k in keys])
            rec |= {f"{fam}_K": len(keys), f"{fam}_cA": ub.mean(), f"{fam}_cB": ur.mean(), f"{fam}_q": same.mean(),
                    f"{fam}_both_unch": (ub & ur).mean(), f"{fam}_both_changed_same": (same & ~ub & ~ur).mean()}
            rec[f"{fam}_unch_best_bits"] = "".join("1" if x else "0" for x in ub)
            rec[f"{fam}_unch_rest_bits"] = "".join("1" if x else "0" for x in ur)
        rows.append(rec)
    return pl.DataFrame(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    st = statements()
    st.write_parquet(OUT / "statements.parquet", compression="zstd")
    print("statements", st.height, st.group_by("period", "room").len().sort("period", "room").rows())
    for m in MODELS:
        ref = ref_centres(st, m)
        np.savez_compressed(OUT / f"ref_centres_{m}.npz", **ref)
        idx, V = centroids(st, m, ref)
        np.savez_compressed(OUT / f"centroids_{m}.npz", V=V)
        idx.write_parquet(OUT / "centroids.parquet", compression="zstd")
        print(m, "centroid rows", idx.height)
    ch = code_hourly()
    ch.write_parquet(OUT / "code_hourly.parquet", compression="zstd")
    print("code rows", ch.height)
    prov = {"built_by": "hypotheses/H118-forked-rpg-replicas/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "tables": ["embeddings/statements", "statements_style_resid32_*",
                                                           "rooms_timeline", "calendar", "roster"]},
                       {"source": "data/processed/H07-rpg-forks", "tables": ["fp_trees", "blob_functions"]}],
            "params": {"goals": list(GOALS), "rooms": list(ROOMS), "room_share_min": 0.8, "bins": "active hour",
                       "ref": "leave-own-period-out regime centre (regime III excludes #51)"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    main()
