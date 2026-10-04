"""H26 scheme: builds data/processed/H26-content-near-critical/ from shared tables and H01's scheme (read-only).

Units: H01's analysis units (goal period split at step changes) for regime III plus #35 (regime II, descriptive).
Non-holdout only (asserted with H01's guard and infra holdout_mask).

Outputs
  statements.parquet   one row per H01 statement in the units: h01_row, unit, agent, pt_date, day (index in unit),
                       t, win30, n_win (windows that day), kind (0 chat, 1 intention), dup (self-repeat, H12 rule)
  vec32.npy            (n, 32) float32, unit-normalized 32-d whitened statement vectors (H01's vectors_w64[:, :32])
  activity.parquet     per unit x agent x pt_date x win30: n_min, n_act, n_talk, and for split s in 0..2 the counts in
                       half A (n_min_A{s}, n_act_A{s}, n_talk_A{s}); minutes from activity_bins (act = state >= 3)
  rooms.parquet        per unit x agent x pt_date x win30: room at the window midpoint (rooms_timeline)
  outage.parquet       per pt_date x win30: share of minutes with no active agent in the village
  exo.parquet + exo_vec32.npy   human and automated chat messages on unit days: unit, pt_date, t, win30, room,
                       speaker_kind; 32-d whitened unit vectors in the unit's regime basis
  static.npz           per unit: orthonormal static-field directions (goal, kickoff, room kickoffs, top-2 PCs of the
                       #51 private goals, top-3 PCs of the first-hour statements)
  _provenance.json

Usage: uv run python hypotheses/H26-content-near-critical/scheme/build.py
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_v] = "2"

import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(ROOT / "hypotheses/H01-emergent-superagents-exist/scheme"))
sys.path.insert(0, str(ROOT / "hypotheses/H01-emergent-superagents-exist/analysis"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402
from h01common import guard_holdout, load_basis, unit, whiten_apply  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

SH = ROOT / "data/processed/shared"
H01 = ROOT / "data/processed/H01-emergent-superagents-exist"
OUT = ROOT / "data/processed/H26-content-near-critical"
UNITS = ["35", "36b", "37", "38a", "38b", "38c", "39", "40", "41", "42", "44", "51a", "51b", "51c", "51d", "51e"]
SEED = 20261004
NSPLIT = 3


def main():
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    units = {u["unit"]: u for u in json.loads((H01 / "units.json").read_text()) if u["unit"] in UNITS}
    all_days = sorted({d for u in units.values() for d in u["days"]})
    guard_holdout(all_days)
    cal = pl.read_parquet(SH / "calendar.parquet")
    hm = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    held = set(cal.filter(pl.Series(hm) | pl.col("holdout"))["pt_date"].to_list())
    assert not (set(all_days) & held), "holdout day in H26 scheme"
    cal = cal.filter(pl.col("pt_date").is_in(all_days)).select(
        "pt_date", "win_start", "window_s").with_columns(
        (pl.col("window_s") / 1800).round().clip(1, None).cast(pl.Int16).alias("n_win"))
    dayidx = pl.DataFrame([{"unit": u, "pt_date": d, "day": i} for u, v in units.items() for i, d in enumerate(v["days"])])

    # ------------------------------------------------------------------ statements
    st = pl.read_parquet(H01 / "statements.parquet").with_row_index("h01_row")
    st = st.filter(pl.col("unit").is_in(UNITS)).join(dayidx, on=["unit", "pt_date"], how="inner").join(cal, on="pt_date")
    st = st.with_columns(
        (((pl.col("t") - pl.col("win_start")).dt.total_seconds() // 1800).clip(0, None).cast(pl.Int16)).alias("w"))
    st = st.with_columns(pl.min_horizontal("w", pl.col("n_win") - 1).alias("win30")).drop("w")
    Z = np.load(H01 / "vectors_w64.npy", mmap_mode="r")
    V = unit(np.asarray(Z[st["h01_row"].to_numpy()][:, :32], dtype=np.float32)).astype(np.float32)
    # self-repeat dedupe (H12 rule): chat statement with raw cosine > 0.95 to an earlier chat statement, same agent-day
    E = np.load(SH / "embeddings/chat_bge_small.npy", mmap_mode="r")
    st = st.with_row_index("i")
    dup = np.zeros(st.height, bool)
    ch = st.filter(pl.col("kind") == 0).sort("t")
    for (_a, _d), g in ch.group_by(["agent", "pt_date"]):
        if g.height < 2:
            continue
        g = g.sort("t")
        X = np.asarray(E[g["emb_row"].to_numpy()], dtype=np.float32)
        S = np.tril(X @ X.T, -1)
        dup[g["i"].to_numpy()[S.max(1) > 0.95]] = True
    st = st.with_columns(pl.Series("dup", dup))
    print(f"statements {st.height} (dup {dup.sum()}, {dup.sum() / max(1, (st['kind'] == 0).sum()):.3f} of chat)", flush=True)
    st.select("h01_row", "unit", "agent", "pt_date", "day", "t", "win30", "n_win", "kind", "n_chars", "dup") \
      .write_parquet(OUT / "statements.parquet", compression="zstd")
    np.save(OUT / "vec32.npy", V)

    # ------------------------------------------------------------------ activity minutes
    ab = (pl.scan_parquet(SH / "activity_bins.parquet").filter(pl.col("pt_date").is_in(all_days))
          .select("pt_date", "minute", "agent", "state").collect())
    ab = ab.join(cal.select("pt_date", "n_win"), on="pt_date").with_columns(
        pl.min_horizontal(pl.col("minute") // 30, pl.col("n_win").cast(pl.Int64) - 1).cast(pl.Int16).alias("win30"),
        (pl.col("state") >= 3).alias("act"), (pl.col("state") == 4).alias("talk"))
    # agents with >= 1 event that day
    present = ab.group_by("pt_date", "agent").agg((pl.col("state") >= 2).any().alias("present")).filter("present")
    ab = ab.join(present.select("pt_date", "agent"), on=["pt_date", "agent"])
    outage = (ab.group_by("pt_date", "minute").agg(pl.col("act").any().alias("any"), pl.col("win30").first())
              .group_by("pt_date", "win30").agg((1 - pl.col("any").cast(pl.Float32).mean()).alias("idle_share"),
                                                pl.len().alias("n_min")).sort("pt_date", "win30"))
    outage.write_parquet(OUT / "outage.parquet", compression="zstd")
    ab = ab.sort("pt_date", "agent", "minute")
    rng = np.random.default_rng(SEED)
    halves = {f"h{s}": rng.random(ab.height) < 0.5 for s in range(NSPLIT)}
    ab = ab.with_columns(*[pl.Series(k, v) for k, v in halves.items()])
    aggs = [pl.len().alias("n_min"), pl.col("act").sum().alias("n_act"), pl.col("talk").sum().alias("n_talk")]
    for s in range(NSPLIT):
        h = pl.col(f"h{s}")
        aggs += [h.sum().alias(f"n_min_A{s}"), (h & pl.col("act")).sum().alias(f"n_act_A{s}"),
                 (h & pl.col("talk")).sum().alias(f"n_talk_A{s}")]
    act = ab.group_by("pt_date", "agent", "win30").agg(aggs)
    act = act.join(dayidx, on="pt_date", how="inner")   # one row per unit containing the day
    act = act.with_columns(pl.col(pl.UInt32).cast(pl.Int16))
    act.sort("unit", "pt_date", "agent", "win30").write_parquet(OUT / "activity.parquet", compression="zstd")
    print(f"activity rows {act.height}", flush=True)

    # ------------------------------------------------------------------ rooms per agent-window (midpoint)
    rt = pl.read_parquet(SH / "rooms_timeline.parquet").sort("t_start")
    aw = pl.concat([act.select("unit", "pt_date", "agent", "win30"),
                    st.select("unit", "pt_date", "agent", "win30")]).unique()
    aw = aw.join(cal.select("pt_date", "win_start"), on="pt_date").with_columns(
        (pl.col("win_start") + pl.duration(seconds=pl.col("win30").cast(pl.Int64) * 1800 + 900)).alias("mid")).sort("mid")
    aw = aw.join_asof(rt.select("agent", "room", "t_start", "t_end"), left_on="mid", right_on="t_start", by="agent",
                      strategy="backward")
    aw = aw.with_columns(pl.when(pl.col("t_end").is_null() | (pl.col("mid") < pl.col("t_end"))).then(pl.col("room"))
                         .otherwise(None).alias("room"))
    aw.select("unit", "pt_date", "agent", "win30", "room").sort("unit", "pt_date", "agent", "win30") \
      .write_parquet(OUT / "rooms.parquet", compression="zstd")
    print(f"room rows {aw.height}, null room {aw['room'].null_count()}", flush=True)

    # ------------------------------------------------------------------ exogenous messages
    chat = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "pt_date", "room", "speaker_kind"]) \
             .filter(pl.col("pt_date").is_in(all_days) & pl.col("speaker_kind").is_in(["human", "automated"]))
    ci = pl.read_parquet(SH / "embeddings/chat_index.parquet").with_row_index("emb_row")
    chat = chat.join(ci, on="message_id", how="inner").join(cal, on="pt_date")
    chat = chat.with_columns(
        ((pl.col("t") - pl.col("win_start")).dt.total_seconds() // 1800).cast(pl.Int16).alias("win30"))
    exo = chat.join(dayidx, on="pt_date", how="inner")
    bases = {R: load_basis(R) for R in ("II", "III")}
    reg = {u: units[u]["regimes"][-1] for u in units}
    Xe = np.zeros((exo.height, 32), np.float32)
    raw = np.asarray(E[exo["emb_row"].to_numpy()], dtype=np.float32)
    for R in ("II", "III"):
        m = np.array([reg[u] == R for u in exo["unit"].to_list()])
        if m.any():
            Xe[m] = unit(whiten_apply(raw[m], bases[R], 32))
    exo.select("unit", "pt_date", "t", "win30", "room", "speaker_kind").write_parquet(OUT / "exo.parquet", compression="zstd")
    np.save(OUT / "exo_vec32.npy", Xe)
    print(f"exo messages {exo.height} ({(exo['speaker_kind'] == 'human').sum()} human)", flush=True)

    # ------------------------------------------------------------------ static field directions
    from h01data import Scheme
    S = Scheme(d=32)
    static, static_info = {}, {}
    for u, ui in units.items():
        R = reg[u]
        gh = S.ghat(ui["goal_no"], R)
        dirs, names = [gh["goal"]], ["goal"]
        if gh["kick"] is not None:
            dirs.append(gh["kick"]); names.append("kickoff")
        for r, v in gh["room"].items():
            dirs.append(v); names.append(f"room_kickoff_{r}")
        if ui["goal_no"] == 51:
            ag = S.agent_goals(ui["days"], R)
            if len(ag) >= 3:
                M = np.array(list(ag.values()))
                pcs = np.linalg.svd(M - M.mean(0), full_matrices=False)[2][:2]
                dirs += list(pcs); names += ["agent_goal_pc1", "agent_goal_pc2"]
        su = st.filter((pl.col("unit") == u) & (pl.col("day") == 0))
        fh = su.filter((pl.col("t") - pl.col("win_start")).dt.total_seconds() < 3600)
        if fh.height >= 6:
            Xf = V[fh["i"].to_numpy()]
            pcs = np.linalg.svd(Xf - Xf.mean(0), full_matrices=False)[2][:3]
            dirs += list(pcs); names += ["first_hour_pc1", "first_hour_pc2", "first_hour_pc3"]
        D = np.array(dirs, float)
        U_, s_, Wt = np.linalg.svd(D, full_matrices=False)
        static[u] = Wt[s_ > 1e-6 * s_.max()].astype(np.float32)
        static_info[u] = {"directions": names, "rank": int(static[u].shape[0]), "first_hour_statements": int(fh.height)}
    np.savez(OUT / "static.npz", **static)
    (OUT / "static_info.json").write_text(json.dumps(static_info, indent=1))

    prov = {"built_by": "hypotheses/H26-content-near-critical/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["H01 statements + vectors_w64 + basis_* + goals (read-only)", "chat_core",
                                   "embeddings/chat_bge_small", "embeddings/chat_index", "activity_bins",
                                   "rooms_timeline", "calendar"]}],
            "params": {"units": UNITS, "dedupe": "chat, raw cosine > 0.95 to earlier same agent-day (H12 rule)",
                       "nsplit_activity": NSPLIT, "seed": SEED, "active": "state >= 3", "talk": "state == 4",
                       "window": "30 min from calendar.win_start, tail stub merged into last window",
                       "holdout": "asserted absent"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print(f"done {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
