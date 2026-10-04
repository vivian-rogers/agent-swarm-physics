"""H32 scheme: per-message whitened content vectors for the non-holdout goal periods H32 analyzes.

Inclusion: non-holdout goal periods (calendar flag AND common.holdout_mask, asserted) with >= 3 active days and
>= 4 agents with >= 20 chat messages; #51 deferred (round 2). One unit = one goal period (no splits).

Rows (messages.parquet), one per item, sorted by time within period:
  kind      0 = chat message, 1 = agent intention (self-written session goal / nextSessionGoal; private, own-past only)
  spk       speaker code: agent code (0..45), 100 = human, 101 = automated
  goal_no, pt_date, day (0-based index within the period), t (UTC), a (active seconds since the period's first window
  start, from calendar.active_offset_s), room (chat room; null for intentions), message_id / event_index, n_chars
Vectors (vec_w64.npy, fp16, row-aligned): raw bge-small embedding whitened in the period's basis (majority regime of
  its days; common.load_whitener(regime, 64)); NOT unit-normalized (nested PCA: first 32 columns = the n = 32 basis).
fields.npz: per period, the raw 384-d goal-text vector and per-room kickoff vectors (+ room codes) from the shared
  goal fields (embeddings/goals.parquet + goal_vectors.npy, kinds goal_whole and kickoff_room); whitened downstream.
periods.json: the analyzed periods with regime basis, mode, days, rooms, roster counts.

No text is written. Usage: uv run python hypotheses/H32-information-current-leaders/scheme/build.py
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
HYP = HERE.parent
ROOT = HYP.parents[1]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask, load_holdout, load_whitener  # noqa: E402

SH = ROOT / "data/processed/shared"
EMB = SH / "embeddings"
H01 = ROOT / "data/processed/H01-emergent-superagents-exist"
OUT = ROOT / "data/processed/H32-information-current-leaders"
PT = "America/Los_Angeles"
MIN_DAYS, MIN_AGENTS, MIN_MSGS = 3, 4, 20
EXCLUDE = {51}
HUMAN, AUTO = 100, 101


def goal_modes() -> dict[int, str]:
    """Coupling-mode code per goal from hypotheses/hypohypotheses/goal-periods.md ('At a glance' table)."""
    txt = (ROOT / "hypotheses/hypohypotheses/goal-periods.md").read_text()
    out = {}
    for line in txt.splitlines():
        m = re.match(r"^\|\s*(\d+)\s*\|[^|]*\|[^|]*\|[^|]*\|[^|]*\|\s*(I{1,3})\s*\|\s*(\w)\s*\|\s*([\w/]+)\s*\|", line)
        if m:
            out[int(m.group(1))] = m.group(4)
    return out


def nonholdout_calendar() -> pl.DataFrame:
    cal = pl.read_parquet(SH / "calendar.parquet").with_columns(pl.col("regime").cast(pl.String))
    hm = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    return cal.with_columns(pl.Series("hm", hm)).filter(~pl.col("holdout") & ~pl.col("hm") & (pl.col("goal_no") > 0)).drop("hm")


def guard(days, goals):
    h = load_holdout()
    held = set(h["goal_periods_held_out"])
    assert not (set(goals) & held), f"held-out goal in H32 exploration: {set(goals) & held}"
    for d in days:
        assert not any(w["start"] <= d < w["end"] for w in h["ne_windows"]), f"NE-window day {d} in H32 exploration"
    assert not any(holdout_mask(list(days), [0] * len(days))), "holdout day"


def select_periods(cal: pl.DataFrame, cc: pl.DataFrame) -> pl.DataFrame:
    per = (cc.filter(pl.col("speaker_kind") == "agent").group_by("goal_no", "agent").len()
           .filter(pl.col("len") >= MIN_MSGS).group_by("goal_no").agg(pl.len().alias("n_agents20")))
    nd = cal.group_by("goal_no").agg(pl.col("pt_date").n_unique().alias("n_days"))
    return per.join(nd, on="goal_no").filter((pl.col("n_agents20") >= MIN_AGENTS) & (pl.col("n_days") >= MIN_DAYS)
                                             & ~pl.col("goal_no").is_in(list(EXCLUDE))).sort("goal_no")


def chat_table(cal: pl.DataFrame) -> pl.DataFrame:
    cc = pl.read_parquet(SH / "chat_core.parquet").with_row_index("chat_row").filter(
        pl.col("speaker_kind").cast(pl.String).is_in(["agent", "human", "automated"]))
    cc = cc.join(cal.select("pt_date", pl.col("goal_no").alias("cal_goal")), on="pt_date", how="inner")
    cc = cc.filter(pl.col("goal_no") == pl.col("cal_goal")).drop("cal_goal")
    roster = pl.read_parquet(SH / "roster.parquet")
    return cc.filter(~pl.col("agent").is_in(roster.filter(pl.col("claude_code"))["agent"].implode()) | pl.col("agent").is_null())


def assemble(goals: list[int], cal: pl.DataFrame, cc: pl.DataFrame, per: pl.DataFrame, out_dir: Path, with_text_fields=True,
             allow_holdout_fields=False):
    """Build messages.parquet, vec_w64.npy, periods.json (+ fields.npz) for `goals` into out_dir. Returns n rows."""
    modes = goal_modes()
    roster = pl.read_parquet(SH / "roster.parquet")
    ci = pl.read_parquet(EMB / "chat_index.parquet").with_row_index("emb_row")
    chat = (cc.filter(pl.col("goal_no").is_in(goals)).join(ci, on="message_id", how="inner")
            .with_columns(pl.when(pl.col("speaker_kind") == "agent").then(pl.col("agent").cast(pl.Int16))
                          .when(pl.col("speaker_kind") == "human").then(pl.lit(HUMAN, pl.Int16))
                          .otherwise(pl.lit(AUTO, pl.Int16)).alias("spk"),
                          pl.lit(0, pl.Int8).alias("kind"), pl.lit(None, pl.Int64).alias("event_index"))
            .select("kind", "spk", "goal_no", "pt_date", "t", "room", "message_id", "event_index",
                    pl.col("length").cast(pl.Int32).alias("n_chars"), "emb_row"))
    it = pl.read_parquet(SH / "intentions.parquet").with_columns(
        pl.col("t").dt.convert_time_zone(PT).dt.date().cast(pl.String).alias("pt_date"))
    ii = pl.read_parquet(EMB / "intentions_index.parquet").with_row_index("emb_row")
    it = (it.join(ii, on="event_index", how="inner").join(cal.select("pt_date", "goal_no"), on="pt_date", how="inner")
          .filter(pl.col("goal_no").is_in(goals))
          .filter(~pl.col("agent").is_in(roster.filter(pl.col("claude_code"))["agent"].implode()))
          .select(pl.lit(1, pl.Int8).alias("kind"), pl.col("agent").cast(pl.Int16).alias("spk"), "goal_no", "pt_date", "t",
                  pl.lit(None, pl.Int8).alias("room"), pl.lit(None, pl.String).alias("message_id"), "event_index",
                  pl.lit(None, pl.Int32).alias("n_chars"), "emb_row"))
    allm = pl.concat([chat, it.with_columns(pl.col("goal_no").cast(chat.schema["goal_no"]))])
    allm = allm.join(cal.select("pt_date", "win_start", "active_offset_s", "regime"), on="pt_date", how="inner")

    reg_of = {}
    pinfo = []
    for g in goals:
        cg = cal.filter(pl.col("goal_no") == g).sort("pt_date")
        r = cg["regime"].mode().sort()[-1]
        reg_of[g] = r
        a0 = int(cg["active_offset_s"][0])
        rooms = (chat.filter((pl.col("goal_no") == g) & (pl.col("spk") < 100)).group_by("room").len()
                 .filter(pl.col("len") >= 20)["room"].sort().to_list())
        pinfo.append({"goal_no": int(g), "mode": modes.get(int(g), "?"), "regime_basis": r,
                      "regimes": sorted(set(cg["regime"].to_list())), "days": cg["pt_date"].to_list(),
                      "day_len_s": [int(x) for x in cg["window_s"].to_list()],
                      "day_offset_s": [int(x) - a0 for x in cg["active_offset_s"].to_list()],
                      "win_start": [x.isoformat() for x in cg["win_start"].to_list()],
                      "a_total_s": int(cg["active_offset_s"][-1] - a0 + cg["window_s"][-1]),
                      "rooms_populated": [int(x) for x in rooms],
                      "n_agents20": int(per.filter(pl.col("goal_no") == g)["n_agents20"][0])})
    a0s = pl.DataFrame({"goal_no": goals, "a0": [cal.filter(pl.col("goal_no") == g)["active_offset_s"].min() for g in goals],
                        "regime_basis": [reg_of[g] for g in goals]}).with_columns(pl.col("goal_no").cast(allm.schema["goal_no"]))
    dayidx = pl.concat([pl.DataFrame({"pt_date": p["days"], "day": list(range(len(p["days"])))}) for p in pinfo])
    allm = (allm.join(a0s, on="goal_no").join(dayidx.with_columns(pl.col("day").cast(pl.Int16)), on="pt_date")
            .with_columns((pl.col("active_offset_s") - pl.col("a0") + (pl.col("t") - pl.col("win_start")).dt.total_seconds())
                          .cast(pl.Float64).alias("a"))
            .sort("goal_no", "t", "kind").drop("win_start", "active_offset_s", "a0"))

    Ec = np.load(EMB / "chat_bge_small.npy", mmap_mode="r")
    Ei = np.load(EMB / "intentions_bge_small.npy", mmap_mode="r")
    kind = allm["kind"].to_numpy(); er = allm["emb_row"].to_numpy().astype(np.int64)
    X = np.zeros((allm.height, 384), np.float32)
    X[kind == 0] = Ec[er[kind == 0]]
    X[kind == 1] = Ei[er[kind == 1]]
    V = np.zeros((allm.height, 64), np.float32)
    rb = allm["regime_basis"].to_numpy()
    for R in sorted(set(rb)):
        W = load_whitener(R, 64)
        V[rb == R] = W(X[rb == R])
    allm = allm.drop("emb_row")
    out_dir.mkdir(parents=True, exist_ok=True)
    allm.write_parquet(out_dir / "messages.parquet", compression="zstd")
    np.save(out_dir / "vec_w64.npy", V.astype(np.float16))
    fz = {}
    if with_text_fields:  # goal text (one string) + first-day kickoff per room, raw 384-d: shared goal fields
        # (infra/shared/goal_fields.py; replaces H01's goals_raw.npy, whose #36-#42 kickoff rows differ, coordinator
        # bug notice 2026-10-03). Exploration uses non-holdout rows only.
        gm = pl.read_parquet(EMB / "goals.parquet").with_columns(pl.col("kind").cast(pl.String))
        graw = np.load(EMB / "goal_vectors.npy").astype(np.float32)
        for p in pinfo:
            g = p["goal_no"]
            rows_ = gm.filter((pl.col("goal_no") == g) & pl.col("kind").is_in(["goal_whole", "kickoff_room"])
                              & (~pl.col("holdout") | pl.lit(allow_holdout_fields))).sort("gid")
            fz[f"g{g}_raw"] = graw[rows_["gid"].to_numpy()] if rows_.height else np.zeros((0, 384), np.float32)
            fz[f"g{g}_kind"] = np.array([0 if k == "goal_whole" else 1 for k in rows_["kind"].to_list()], np.int8)
            fz[f"g{g}_room"] = rows_["room"].fill_null(-1).to_numpy().astype(np.int16) if rows_.height else np.zeros(0, np.int16)
            p["n_field_texts"] = int(rows_.height)
    np.savez(out_dir / "fields.npz", **fz)
    (out_dir / "periods.json").write_text(json.dumps(pinfo, indent=1))
    return allm, kind


def main():
    t0 = dt.datetime.now()
    cal = nonholdout_calendar()
    cc = chat_table(cal)
    per = select_periods(cal, cc)
    goals = per["goal_no"].to_list()
    days_all = cal.filter(pl.col("goal_no").is_in(goals))["pt_date"].to_list()
    guard(days_all, goals)
    print("periods", goals, flush=True)
    allm, kind = assemble(goals, cal, cc, per, OUT)
    guard(sorted(allm["pt_date"].unique().to_list()), sorted(allm["goal_no"].unique().to_list()))
    prov = {"scheme": {"built_by": "hypotheses/H32-information-current-leaders/scheme/build.py", "git_commit": git_commit(),
                       "inputs": [{"source": "ai-village", "revision": REVISION,
                                   "tables": ["shared/chat_core", "shared/embeddings/chat_bge_small+chat_index",
                                              "shared/embeddings/intentions_bge_small+intentions_index", "shared/intentions",
                                              "shared/embeddings/whitening_<regime> (load_whitener)", "shared/calendar",
                                              "shared/roster", "shared/embeddings/goals.parquet+goal_vectors.npy (goal_whole, kickoff_room)"]}],
                       "params": {"min_days": MIN_DAYS, "min_agents": MIN_AGENTS, "min_msgs": MIN_MSGS, "excluded": sorted(EXCLUDE),
                                  "periods": goals, "whitening_dim": 64, "basis": "majority regime of the period's days",
                                  "holdout": "excluded: calendar.holdout OR holdout_mask; asserted",
                                  "n_rows": allm.height, "n_chat": int((kind == 0).sum()), "n_intent": int((kind == 1).sum())},
                       "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}}
    pp = OUT / "_provenance.json"
    old = json.loads(pp.read_text()) if pp.exists() else {}
    old.update(prov)
    pp.write_text(json.dumps(old, indent=1))
    print("rows", allm.height, "chat", int((kind == 0).sum()), "intent", int((kind == 1).sum()),
          f"{(dt.datetime.now() - t0).total_seconds():.0f}s", flush=True)


if __name__ == "__main__":
    main()
