"""H47 scheme: builds data/processed/H47-room-coherence-length/ from shared tables only (no text), non-holdout only.

Outputs:
  statements.parquet   one row per kept statement (agent chat + intentions, 2026-03-16 on, Claude Code agent dropped,
                       holdout days dropped), in shared-statements row order: sid (row in vec arrays), st_row (row in
                       shared embeddings/statements), kind, agent, t, pt_date, goal_no, regime, unit_id, win30,
                       room (presence: chat room, or the agent's room from rooms_timeline for intentions),
                       room_assigned (DQ6 operator assignment, null where undefined), dup (self-repeat: raw bge
                       cos > 0.95 to an earlier chat statement by the same agent that PT day), voff (the 30-min window
                       has >= 15 minutes inside a village_off outage run)
  vec32.npy            fp16 (n, 32): regime-whitened (common.load_whitener) raw bge vector, unit-normalized
  vec32_style.npy      fp16 (n, 32): DQ5 style-residualized vector (statements_style_resid32_bge_small), copied
  mentions.parquet     unit_id, a, b (a < b), w = clean roster mentions a->b + b->a among agent chat in the unit
  static.npz           per unit: 'all_<unit>' orthonormal static-field basis (goal chunks, kickoff, per-room kickoffs;
                       whitened) and 'instr_<unit>' orthonormal basis of the per-room kickoff differences
  agent_room_day.parquet  agent, pt_date, room (modal room of the agent's chat that day; fallback rooms_timeline),
                       n_chat; every non-holdout active day from 2026-02-25 on
  kickoffs.parquet     goal_no, room, t (first human kickoff message per room, kicks_classified)
  units.parquet        period_units rows from #35 on (non-holdout) with n_rooms_struct and a multiroom flag

Usage: uv run python hypotheses/H47-room-coherence-length/scheme/build.py
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ[_v] = "2"

import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, holdout_mask, load_whitener  # noqa: E402

sys.path.insert(0, str(ROOT / "hypotheses/H47-room-coherence-length/analysis"))
import h47lib as L  # noqa: E402

SH = ROOT / "data/processed/shared"
ED = SH / "embeddings"
OUT = ROOT / "data/processed/H47-room-coherence-length"
START = "2026-03-16"
ROOMS_ERA = "2026-02-25"
DUP_COS = 0.95


def calendar():
    cal = pl.read_parquet(SH / "calendar.parquet").with_columns(pl.col("regime").cast(pl.String))
    hm = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    assert cal["holdout"].to_list() == hm, "calendar.holdout disagrees with holdout_mask"
    return cal


def gather_rows(arr, idx):
    """arr[idx] for a memory-mapped array with unsorted idx (sorted read, then restore order)."""
    o = np.argsort(idx, kind="stable")
    out = np.empty((len(idx), arr.shape[1]), np.float32)
    out[o] = np.asarray(arr[idx[o]], np.float32)
    return out


def main():
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    cal = calendar()
    ok_days = set(cal.filter(~pl.col("holdout"))["pt_date"].to_list())
    ro = pl.read_parquet(SH / "roster.parquet")
    cc = set(ro.filter(pl.col("claude_code"))["agent"].to_list())
    rooms = pl.read_parquet(SH / "rooms.parquet")
    name2room = dict(zip(rooms["name"].to_list(), rooms["room"].to_list()))

    # ------------------------------------------------------------------ units
    pu = pl.read_parquet(SH / "period_units.parquet").filter((pl.col("goal_no") >= 35) & ~pl.col("holdout"))
    pu = pu.with_columns(pl.col("rooms").list.len().alias("n_rooms_struct"))
    pu = pu.with_columns((pl.col("n_rooms_struct") >= 2).alias("multiroom"))
    pu.write_parquet(OUT / "units.parquet")
    day2unit = {}
    for u, days in pu.select("unit_id", "days").iter_rows():
        for d in days:
            day2unit.setdefault(d, u)

    # ------------------------------------------------------------------ statements (fixed order: shared st_row)
    st = pl.read_parquet(ED / "statements.parquet").with_row_index("st_row")
    st = st.filter((pl.col("pt_date") >= START) & ~pl.col("holdout") & pl.col("pt_date").is_in(list(ok_days))
                   & ~pl.col("agent").is_in(list(cc)))
    st = st.with_columns(pl.col("pt_date").replace_strict(day2unit, default=None).alias("unit_id")).filter(pl.col("unit_id").is_not_null())
    assert not any(holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list())), "holdout row in H47 statements"
    rt = pl.read_parquet(SH / "rooms_timeline.parquet")
    asof = (st.select("st_row", "agent", "t").sort("t")
            .join_asof(rt.select("agent", "room", pl.col("t_start").alias("t")).sort("t"), on="t", by="agent", strategy="backward"))
    st = st.join(asof.select("st_row", pl.col("room").alias("room_tl")), on="st_row", how="left")
    st = st.with_columns(pl.coalesce(pl.col("room").cast(pl.Int8), pl.col("room_tl").cast(pl.Int8)).alias("room")).drop("room_tl")
    st = st.sort("st_row")
    n = st.height
    # DQ6 assigned room
    gt = pl.read_parquet(SH / "ground_truth_labels.parquet").filter(
        pl.col("preferred") & ~pl.col("holdout") & (pl.col("label_kind") == "room_assignment"))
    gt = gt.with_columns(pl.col("value").replace_strict(name2room, default=None).cast(pl.Int8).alias("aroom"))
    ag_arr = st["agent"].to_numpy(); t_arr = st["t"].dt.epoch("us").to_numpy()
    aroom = np.full(n, -1, np.int16)
    big = np.iinfo(np.int64).max
    for a, r, f, tt in gt.select("agent", "aroom", pl.col("t_valid_from").dt.epoch("us"),
                                 pl.col("t_valid_to").dt.epoch("us")).iter_rows():
        if r is None or a is None:
            continue
        m = (ag_arr == a) & (t_arr >= f) & (t_arr < (tt if tt is not None else big))
        aroom[m] = r
    st = st.with_columns(pl.Series("room_assigned", [None if x < 0 else int(x) for x in aroom], dtype=pl.Int8))

    # raw vectors (same row order as st)
    kind = st["kind"].to_numpy(); src = st["src_row"].to_numpy().astype(np.int64)
    raw = np.zeros((n, 384), np.float32)
    mc = kind == "chat"
    raw[mc] = gather_rows(np.load(ED / "chat_bge_small.npy", mmap_mode="r"), src[mc])
    raw[~mc] = gather_rows(np.load(ED / "intentions_bge_small.npy", mmap_mode="r"), src[~mc])
    V = np.zeros((n, 32), np.float32)
    reg = st["regime"].to_numpy()
    for r in np.unique(reg):
        m = reg == r
        V[m] = load_whitener(str(r), 32)(raw[m])
    V /= np.clip(np.linalg.norm(V, axis=1, keepdims=True), 1e-9, None)
    # self-repeat flag
    rn = raw / np.clip(np.linalg.norm(raw, axis=1, keepdims=True), 1e-9, None)
    dup = np.zeros(n, bool)
    keys = (st.with_row_index("i").filter(pl.Series(mc)).group_by("agent", "pt_date").agg(pl.col("i")))
    for idx in keys["i"].to_list():
        idx = np.asarray(idx)
        idx = idx[np.argsort(t_arr[idx], kind="stable")]
        if len(idx) < 2:
            continue
        G = np.tril(rn[idx] @ rn[idx].T, -1)
        dup[idx[(G > DUP_COS).any(1)]] = True
    st = st.with_columns(pl.Series("dup", dup))
    Vs = gather_rows(np.load(ED / "statements_style_resid32_bge_small.npy", mmap_mode="r"), st["st_row"].to_numpy().astype(np.int64))
    # village-off windows
    outg = pl.read_parquet(SH / "outages.parquet").filter(pl.col("village_off"))
    sm = pl.read_parquet(SH / "stall_minutes.parquet", columns=["pt_date", "t", "outage_id"]).filter(
        pl.col("outage_id").is_in(outg["outage_id"].to_list()) & pl.col("pt_date").is_in(list(ok_days)))
    sm = sm.join(cal.select("pt_date", "win_start"), on="pt_date").with_columns(
        ((pl.col("t") - pl.col("win_start")).dt.total_seconds() // 1800).cast(pl.Int16).alias("win30"))
    voff = sm.group_by("pt_date", "win30").len().filter(pl.col("len") >= 15).select("pt_date", "win30", pl.lit(True).alias("voff"))
    st = st.join(voff, on=["pt_date", "win30"], how="left", maintain_order="left").with_columns(pl.col("voff").fill_null(False))
    st = st.with_row_index("sid")
    st.select("sid", "st_row", "kind", "agent", "t", "pt_date", "goal_no", "regime", "unit_id", "win30", "room",
              "room_assigned", "dup", "voff").write_parquet(OUT / "statements.parquet", compression="zstd")
    np.save(OUT / "vec32.npy", V.astype(np.float16))
    np.save(OUT / "vec32_style.npy", Vs.astype(np.float16))

    # ------------------------------------------------------------------ mentions per unit
    ch = (pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "pt_date", "speaker_kind", "agent", "room"])
          .filter((pl.col("speaker_kind") == "agent") & pl.col("pt_date").is_in(list(ok_days)) & (pl.col("pt_date") >= START))
          .join(pl.read_parquet(SH / "chat_mentions_clean.parquet", columns=["message_id", "mentions_roster"]), on="message_id"))
    ch = ch.with_columns(pl.col("pt_date").replace_strict(day2unit, default=None).alias("unit_id")).filter(pl.col("unit_id").is_not_null())
    me = (ch.select("unit_id", pl.col("agent").alias("src"), pl.col("mentions_roster").alias("dst")).explode("dst")
          .filter(pl.col("dst").is_not_null() & (pl.col("dst") != pl.col("src")) & ~pl.col("src").is_in(list(cc)) & ~pl.col("dst").is_in(list(cc))))
    me = (me.with_columns(pl.min_horizontal("src", "dst").alias("a"), pl.max_horizontal("src", "dst").alias("b"))
          .group_by("unit_id", "a", "b").agg(pl.len().cast(pl.Float32).alias("w")).sort("unit_id", "a", "b"))
    me.write_parquet(OUT / "mentions.parquet")

    # ------------------------------------------------------------------ static fields per unit
    gl = pl.read_parquet(ED / "goals.parquet")
    gv = np.load(ED / "goal_vectors.npy").astype(np.float32)
    stat = {}
    for u, g, regime in pu.select("unit_id", "goal_no", "regime").iter_rows():
        rows = gl.filter((pl.col("goal_no") == g) & pl.col("kind").is_in(["goal", "kickoff", "kickoff_room"]) & ~pl.col("holdout"))
        if rows.height == 0:
            stat[f"all_{u}"] = np.zeros((0, 32)); stat[f"instr_{u}"] = np.zeros((0, 32)); continue
        W = load_whitener(str(regime), 32)
        X = W(gv[rows["gid"].to_numpy()])
        stat[f"all_{u}"] = L.orthobasis(X)
        kr = rows.filter(pl.col("kind") == "kickoff_room")
        if kr.height >= 2:
            Xr = W(gv[kr["gid"].to_numpy()])
            stat[f"instr_{u}"] = L.orthobasis(Xr[1:] - Xr[:1])
        else:
            stat[f"instr_{u}"] = np.zeros((0, 32))
    np.savez_compressed(OUT / "static.npz", **stat)

    # ------------------------------------------------------------------ agent room per day (detector)
    chd = (pl.read_parquet(SH / "chat_core.parquet", columns=["t", "pt_date", "speaker_kind", "agent", "room"])
           .filter((pl.col("speaker_kind") == "agent") & (pl.col("pt_date") >= ROOMS_ERA) & pl.col("pt_date").is_in(list(ok_days))))
    ard = (chd.group_by("agent", "pt_date").agg(pl.col("room").mode().sort().first().alias("room"), pl.len().alias("n_chat")))
    ad = pl.read_parquet(ED / "agent_day.parquet").filter((pl.col("pt_date") >= ROOMS_ERA) & ~pl.col("holdout"))
    ad = ad.join(ard, on=["agent", "pt_date"], how="left")
    miss = ad.filter(pl.col("room").is_null()).join(cal.select("pt_date", "win_start", "win_end"), on="pt_date")
    miss = miss.with_columns((pl.col("win_start") + (pl.col("win_end") - pl.col("win_start")) / 2).alias("t"))
    fill = (miss.select("agent", "pt_date", "t").sort("t")
            .join_asof(rt.select("agent", "room", pl.col("t_start").alias("t")).sort("t"), on="t", by="agent", strategy="backward"))
    ad = ad.join(fill.select("agent", "pt_date", pl.col("room").alias("room_f")), on=["agent", "pt_date"], how="left")
    ad = ad.with_columns(pl.coalesce(pl.col("room").cast(pl.Int8), pl.col("room_f").cast(pl.Int8), pl.lit(0, pl.Int8)).alias("room"),
                         pl.col("n_chat").fill_null(0))
    ad.select("gid", "agent", "pt_date", "goal_no", "room", "n_chat", "n_intent").write_parquet(OUT / "agent_room_day.parquet")

    # ------------------------------------------------------------------ kickoffs per room
    kk = (pl.read_parquet(SH / "kicks_classified.parquet").filter((pl.col("kind") == "human_message") & (pl.col("subkind") == "kickoff")
                                                                   & (pl.col("goal_no") >= 35) & ~pl.col("holdout"))
          .group_by("goal_no", "room").agg(pl.col("t").min()).sort("goal_no", "room"))
    kk.write_parquet(OUT / "kickoffs.parquet")

    prov = {"built_by": "hypotheses/H47-room-coherence-length/scheme/build.py", "git_commit": L.git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["shared/embeddings/statements", "chat_bge_small", "intentions_bge_small", "whitening_<regime>",
                                   "statements_style_resid32_bge_small (DQ5)", "agent_day", "goals + goal_vectors", "rooms",
                                   "rooms_timeline", "period_units", "calendar", "roster", "chat_core", "chat_mentions_clean",
                                   "outages", "stall_minutes", "kicks_classified", "ground_truth_labels (DQ6)"]}],
            "params": {"start": START, "rooms_era": ROOMS_ERA, "dup_cos": DUP_COS, "whiten_dim": 32,
                       "voff_rule": ">= 15 village_off minutes in the 30-min window", "claude_code_excluded": True,
                       "holdout": "excluded (calendar.holdout == holdout_mask asserted)"},
            "counts": {"statements": n, "dup": int(dup.sum()), "voff_statements": int(st["voff"].sum()),
                       "units": pu.height, "mention_pairs": me.height},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print(json.dumps(prov["counts"]), round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
