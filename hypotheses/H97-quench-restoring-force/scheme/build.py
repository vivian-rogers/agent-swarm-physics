"""H97 scheme: statement selections for the kickoff restoring-force tests (codes only, no text).

Builds data/processed/H97-quench-restoring-force/ from shared tables:
  transitions.parquet  one row per kickoff transition p-1 -> p (eligible: both non-holdout, same regime, #23 excluded)
                       plus the native designs (G44 via #42, NE38, G26) flagged by `design`.
  stmt.parquet         statement rows (index into the shared statements arrays) with design, segment codes,
                       agent, day index, unit, room, time. Every row passes common.holdout_mask.
  vectors.npz          per design and model: kickoff k-hat (and goal-text g-hat) in the target regime's 32-d basis.
  _provenance.json
Usage: uv run python hypotheses/H97-quench-restoring-force/scheme/build.py
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import git_commit, holdout_mask, REVISION  # noqa: E402
from embed_models import goal_vectors, load_whitener  # noqa: E402

S = ROOT / "data/processed/shared"
ED = S / "embeddings"
OUT = ROOT / "data/processed/H97-quench-restoring-force"
H54 = ROOT / "data/processed/H54-kickoff-quench-target"
MODELS = ["bge_small", "gte_modernbert"]
CC_AGENT = 19            # Claude Code agent (separate scaffolding)
EXCLUDE_GOALS = {23}     # H10 keeps #23 blind for its confirmatory pair
NE38_T = dt.datetime(2026, 7, 29, 16, 51, tzinfo=dt.timezone.utc)
NE38_AGENT = 40
G26_ANN_T = dt.datetime(2026, 1, 5, 19, 36, 3, tzinfo=dt.timezone.utc)


def unitv(v):
    v = np.asarray(v, dtype=np.float64)
    return v / np.linalg.norm(v)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    st = pl.read_parquet(ED / "statements.parquet").with_row_index("row")
    ho = holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list())
    st = st.with_columns(pl.Series("ho", ho)).filter(~pl.col("ho") & (pl.col("agent") != CC_AGENT)
                                                     & ~pl.col("goal_no").is_in(list(EXCLUDE_GOALS))).drop("ho")
    pu = pl.read_parquet(S / "period_units.parquet")
    pa = pl.read_parquet(S / "period_affordances.parquet").select("goal_no", "mode").unique("goal_no")
    mode = dict(zip(pa["goal_no"].to_list(), pa["mode"].to_list()))
    goals = pl.read_parquet(ED / "goals.parquet")
    kick = goals.filter(pl.col("kind") == "kickoff")
    k54 = pl.read_parquet(H54 / "kickoffs.parquet").filter(pl.col("room").is_null()).select("goal_no", "t0")
    t0map = dict(zip(k54["goal_no"].to_list(), k54["t0"].to_list()))
    proj = pl.read_parquet(H54 / "projects.parquet")
    named_frozen = (proj.filter(pl.col("cls").is_in(["kickoff_frozen", "day1_dominant"])).group_by("goal_no")
                    .agg(pl.col("named_goal").sum().alias("n_frozen_named_goal"), pl.col("named").sum().alias("n_frozen_named")))
    nf = {r["goal_no"]: r for r in named_frozen.iter_rows(named=True)}
    GV = {m: goal_vectors(m).astype(np.float64) for m in MODELS}
    W = {(m, r): load_whitener(r, 32, m) for m in MODELS for r in ("I", "II", "III")}

    # unit lookup per (goal, day)
    unit_of = {}
    for r in pu.iter_rows(named=True):
        for d in r["days"]:
            unit_of[(r["goal_no"], d)] = r["unit_id"]
    days = st.group_by("goal_no").agg(pl.col("pt_date").unique().sort().alias("days"))
    dd = {r["goal_no"]: r["days"] for r in days.iter_rows(named=True)}

    trans, parts, vecs = [], [], {}

    def kvec(gid, regime):
        return {m: unitv(W[(m, regime)](GV[m][gid][None, :])[0]) for m in MODELS}

    def add_rows(sel: pl.DataFrame, design: str, seg_expr):
        parts.append(sel.with_columns(pl.lit(design).alias("design")).with_columns(seg_expr))

    # ---------------------------------------------------------------- kickoff transitions (replication)
    for r in kick.sort("goal_no").iter_rows(named=True):
        p = r["goal_no"]
        if p not in dd or (p - 1) not in dd or p in EXCLUDE_GOALS or (p - 1) in EXCLUDE_GOALS:
            continue
        if r["holdout"]:
            continue
        prev_reg = st.filter(pl.col("goal_no") == p - 1)["regime"][0]
        same_regime = prev_reg == r["regime"]
        d1 = r["first_day"]
        if d1 not in dd[p]:
            continue
        t0 = t0map.get(p, r["win_start"])
        design = f"T{p:02d}"
        sub = st.filter(pl.col("goal_no").is_in([p - 1, p]))
        dl = {p - 1: dd[p - 1], p: dd[p]}
        sub = sub.with_columns(
            pl.struct("goal_no", "pt_date").map_elements(lambda s: dl[s["goal_no"]].index(s["pt_date"]) + 1,
                                                        return_dtype=pl.Int16).alias("day_idx"),
            pl.struct("goal_no", "pt_date").map_elements(lambda s: unit_of.get((s["goal_no"], s["pt_date"]), "?"),
                                                        return_dtype=pl.String).alias("unit_id"))
        seg = (pl.when((pl.col("goal_no") == p - 1) & (pl.col("pt_date") == dd[p - 1][-1])).then(pl.lit("prev"))
               .when((pl.col("goal_no") == p) & (pl.col("pt_date") == d1) & (pl.col("t") >= t0)).then(pl.lit("day1"))
               .when((pl.col("goal_no") == p) & (pl.col("pt_date") == d1)).then(pl.lit("day1_pre"))
               .when((pl.col("goal_no") == p) & (pl.col("day_idx").is_between(2, 5))).then(pl.lit("plateau"))
               .otherwise(pl.lit("other")).alias("seg"))
        add_rows(sub, design, seg)
        vecs[design] = {"k": kvec(r["gid"], r["regime"]),
                        "g": kvec(goals.filter((pl.col("goal_no") == p) & (pl.col("kind") == "goal"))["gid"][0], r["regime"])}
        f = nf.get(p, {})
        trans.append(dict(design=design, kind="kickoff", p=p, prev=p - 1, regime=r["regime"], prev_regime=prev_reg,
                          same_regime=same_regime, mode=mode.get(p), prev_mode=mode.get(p - 1), first_day=d1,
                          prev_last_day=dd[p - 1][-1], t0=t0, kick_gid=r["gid"], fallback=r["fallback"],
                          n_frozen_named_goal=f.get("n_frozen_named_goal"), n_frozen_named=f.get("n_frozen_named")))

    # ---------------------------------------------------------------- native G44: #42 last day -> #44 day 1, rooms
    gt = pl.read_parquet(S / "ground_truth_labels.parquet").filter(pl.col("preferred") & ~pl.col("holdout"))
    ra = gt.filter((pl.col("goal_no") == 44) & (pl.col("label_kind") == "room_assignment"))
    room_of = {}
    for rr in ra.sort("t_valid_from").iter_rows(named=True):
        room_of.setdefault(rr["agent"], rr["value"])
    k44 = goals.filter(pl.col("goal_no") == 44)
    r44 = kick.filter(pl.col("goal_no") == 44).row(0, named=True)
    t0 = t0map.get(44, r44["win_start"])
    sub = st.filter(((pl.col("goal_no") == 42) & (pl.col("pt_date") == dd[42][-1]))
                    | ((pl.col("goal_no") == 44) & pl.col("pt_date").is_in(dd[44][:5])))
    sub = sub.with_columns(
        pl.struct("goal_no", "pt_date").map_elements(lambda s: (dd[s["goal_no"]].index(s["pt_date"]) + 1),
                                                    return_dtype=pl.Int16).alias("day_idx"),
        pl.lit("?").alias("unit_id"))
    seg = (pl.when(pl.col("goal_no") == 42).then(pl.lit("prev"))
           .when((pl.col("pt_date") == dd[44][0]) & (pl.col("t") >= t0)).then(pl.lit("day1"))
           .when(pl.col("pt_date") == dd[44][0]).then(pl.lit("day1_pre"))
           .otherwise(pl.lit("plateau")).alias("seg"))
    add_rows(sub, "G44", seg)
    vecs["G44"] = {"k": kvec(r44["gid"], "III"),
                   "k_best": kvec(k44.filter((pl.col("kind") == "kickoff_room") & (pl.col("room") == 2))["gid"][0], "III"),
                   "k_rest": kvec(k44.filter((pl.col("kind") == "kickoff_room") & (pl.col("room") == 3))["gid"][0], "III")}
    trans.append(dict(design="G44", kind="native", p=44, prev=42, regime="III", prev_regime="III", same_regime=True,
                      mode=mode.get(44), prev_mode=mode.get(42), first_day=dd[44][0], prev_last_day=dd[42][-1], t0=t0,
                      kick_gid=r44["gid"], fallback=r44["fallback"], n_frozen_named_goal=None, n_frozen_named=None,
                      room_map=json.dumps({int(k): v for k, v in room_of.items()})))

    # ---------------------------------------------------------------- native NE38: #51, 07-24..08-04 (non-holdout)
    sub = st.filter((pl.col("goal_no") == 51) & pl.col("pt_date").is_between(pl.lit("2026-07-24"), pl.lit("2026-08-04")))
    d51 = sorted(sub["pt_date"].unique().to_list())
    sub = sub.with_columns(pl.col("pt_date").map_elements(lambda d: d51.index(d) + 1, return_dtype=pl.Int16).alias("day_idx"),
                           pl.lit("51e/51f").alias("unit_id"))
    seg = (pl.when(pl.col("t") < NE38_T).then(pl.lit("pre")).otherwise(pl.lit("post")).alias("seg"))
    add_rows(sub, "NE38", seg)
    ag = goals.filter((pl.col("kind") == "agent_goal") & (pl.col("agent") == NE38_AGENT))
    vecs["NE38"] = {"k": kvec(ag["gid"][0], "III")}
    # other #51 agents' own goals (for controls)
    for rr in goals.filter((pl.col("kind") == "agent_goal") & pl.col("valid_to").is_null()).iter_rows(named=True):
        vecs["NE38"][f"agent_{rr['agent']}"] = kvec(rr["gid"], "III")
    trans.append(dict(design="NE38", kind="native", p=51, prev=51, regime="III", prev_regime="III", same_regime=True,
                      mode=mode.get(51), prev_mode=mode.get(51), first_day="2026-07-29", prev_last_day="2026-07-28",
                      t0=NE38_T, kick_gid=ag["gid"][0], fallback=False, n_frozen_named_goal=None, n_frozen_named=None))

    # ---------------------------------------------------------------- native G26: day 1..5 of #26, announcement split
    sub = st.filter((pl.col("goal_no") == 26) & pl.col("pt_date").is_in(dd[26][:5]))
    sub = sub.with_columns(pl.col("pt_date").map_elements(lambda d: dd[26].index(d) + 1, return_dtype=pl.Int16).alias("day_idx"),
                           pl.lit("26").alias("unit_id"))
    t0_26 = t0map.get(26)
    seg = (pl.when((pl.col("day_idx") == 1) & (pl.col("t") < t0_26)).then(pl.lit("day1_pre"))
           .when((pl.col("day_idx") == 1) & (pl.col("t") < G26_ANN_T)).then(pl.lit("pre"))
           .when(pl.col("day_idx") == 1).then(pl.lit("post"))
           .otherwise(pl.lit("later")).alias("seg"))
    add_rows(sub, "G26", seg)
    # the announcement's own statement vector is the agent-authored target (statement row from chat_index)
    ci = pl.read_parquet(ED / "chat_index.parquet")
    ann_rows = []
    if "message_id" in ci.columns:
        mid = json.loads((H54 / "g26_leader.json").read_text())["message_id"]
        hit = ci.with_row_index("src").filter(pl.col("message_id") == mid)
        if hit.height:
            src = int(hit["src"][0])
            stall = pl.read_parquet(ED / "statements.parquet").with_row_index("row")
            ann = stall.filter((pl.col("kind") == "chat") & (pl.col("src_row") == src))
            ann_rows = ann["row"].to_list()
    vecs["G26"] = {"k": kvec(kick.filter(pl.col("goal_no") == 26)["gid"][0], "I"), "ann_row": ann_rows}
    trans.append(dict(design="G26", kind="native", p=26, prev=26, regime="I", prev_regime="I", same_regime=True,
                      mode=mode.get(26), prev_mode=mode.get(26), first_day=dd[26][0], prev_last_day=dd[26][0],
                      t0=G26_ANN_T, kick_gid=None, fallback=False, n_frozen_named_goal=None, n_frozen_named=None))

    tr = pl.DataFrame(trans, infer_schema_length=None)
    allst = pl.concat([p.select("row", "design", "seg", "goal_no", "pt_date", "day_idx", "unit_id", "agent", "room",
                                "kind", "t") for p in parts])
    tr.write_parquet(OUT / "transitions.parquet", compression="zstd")
    allst.write_parquet(OUT / "stmt.parquet", compression="zstd")
    flat = {}
    for d, v in vecs.items():
        for k, x in v.items():
            if k == "ann_row":
                flat[f"{d}|ann_row"] = np.asarray(x, dtype=np.int64)
            else:
                for m, arr in x.items():
                    flat[f"{d}|{k}|{m}"] = arr
    np.savez_compressed(OUT / "vectors.npz", **flat)
    prov = {"built_by": "hypotheses/H97-quench-restoring-force/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["shared/embeddings/statements", "shared/embeddings/goals", "shared/period_units",
                                   "shared/period_affordances", "shared/ground_truth_labels", "shared/embeddings/chat_index",
                                   "H54/kickoffs (t0, read-only)", "H54/projects (naming tags, read-only)",
                                   "H54/g26_leader.json (message id, read-only)"]}],
            "params": {"exclude_goals": sorted(EXCLUDE_GOALS), "cc_agent": CC_AGENT, "models": MODELS,
                       "ne38_t": NE38_T.isoformat(), "g26_announcement_t": G26_ANN_T.isoformat()},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print(tr.select("design", "p", "regime", "same_regime", "mode", "first_day", "prev_last_day"))
    print("statements:", allst.height, allst.group_by("design").len().sort("design"))


if __name__ == "__main__":
    main()
