"""H99 scheme: trimmed minute grids (talk, activity), content window vectors and human-message kicks per non-holdout
period unit (codes only, no text).

Per unit-day: agents with >= 30 record minutes (state >= 2) that day; each agent's presence span = first..last record
minute; all-present window (DQ8 rule) = minutes where every such agent is inside its span. Spins: talk = talk > 0;
activity = state >= 3. Days with < 60 kept minutes or < 3 agents are dropped. Stall minutes (outages_fixed) are
flagged for the stall-masked variant. Human messages (kicks_classified kind human_message) are mapped to the day's
minute index and room; each agent's modal chat room that day gives room membership.
Content: DQ5 agent_win30 rows (n_chat >= 1) of the unit's days with style_resid_period vectors (bge, gte).

Output data/processed/H99-glauber-fluctuation-relaxation/:
  grids/<unit>.npz      per day k: talk_k, act_k (int8 N x L), keep_k (bool L), stall_k (bool L), agents_k, rooms_k,
                        minute0_k; days
  content/<unit>.npz    rows: agent, day index, win30, vec_bge (float32 x 32), vec_gte
  kicks/<unit>.parquet  day index, minute, room (human messages inside the day's grid)
Usage: uv run python hypotheses/H99-glauber-fluctuation-relaxation/scheme/build.py
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
from common import git_commit, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
ED = SH / "embeddings"
OUT = ROOT / "data/processed/H99-glauber-fluctuation-relaxation"
MIN_REC = 30
MIN_KEEP = 60


def nonholdout_days(days, goal):
    hm = holdout_mask(days, [goal] * len(days))
    return [d for d, h in zip(days, hm) if not h]


def main():
    pu = pl.read_parquet(SH / "period_units.parquet").filter(~pl.col("holdout"))
    build(pu)


def build(pu, allow_holdout: bool = False):
    """Build every unit of `pu`. allow_holdout=True only from analysis/confirm.py (Vivian's sign-off)."""
    cal = pl.read_parquet(SH / "calendar.parquet")
    calh = dict(zip(cal["pt_date"].to_list(), cal["holdout"].fill_null(False).to_list()))
    ws = dict(zip(cal["pt_date"].to_list(), cal["win_start"].to_list()))
    ab = pl.scan_parquet(SH / "activity_bins_fixed.parquet")
    stall = pl.read_parquet(SH / "outages_fixed" / "stall_minutes.parquet")
    kc = (pl.read_parquet(SH / "kicks_classified.parquet", columns=["t", "kind", "room", "pt_date", "goal_no", "holdout"])
          .filter((pl.col("kind") == "human_message") & (pl.lit(allow_holdout) | ~pl.col("holdout").fill_null(False))))
    ch = pl.read_parquet(SH / "chat_core.parquet", columns=["pt_date", "speaker_kind", "agent", "room"])
    room = (ch.filter(pl.col("speaker_kind") == "agent").group_by("pt_date", "agent", "room").agg(pl.len().alias("k"))
            .sort("k", descending=True).group_by("pt_date", "agent").agg(pl.col("room").first()))
    w30 = pl.read_parquet(ED / "agent_win30.parquet")
    Vb = np.load(ED / "agent_win30_style_resid_period_bge_small.npy", mmap_mode="r")
    Vg = np.load(ED / "agent_win30_style_resid_period_gte_modernbert.npy", mmap_mode="r")
    for sub in ("grids", "content", "kicks"):
        (OUT / sub).mkdir(parents=True, exist_ok=True)
    meta = []
    stall_cols = list(stall.columns)
    for r in pu.iter_rows(named=True):
        uid, g = r["unit_id"], r["goal_no"]
        if allow_holdout:
            days = list(r["days"])
        else:
            days = nonholdout_days(list(r["days"]), g)
            days = [d for d in days if not calh.get(d, False)]
            assert not any(holdout_mask(days, [g] * len(days)))
        arrs, kept, krows = {}, [], []
        for d in days:
            x = ab.filter(pl.col("pt_date") == d).select("minute", "agent", "talk", "state").collect()
            if x.height == 0:
                continue
            rec = x.filter(pl.col("state") >= 2).group_by("agent").agg(pl.len().alias("k"), pl.col("minute").min().alias("f"),
                                                                        pl.col("minute").max().alias("l"))
            rec = rec.filter(pl.col("k") >= MIN_REC).sort("agent")
            if rec.height < 3:
                continue
            agents = rec["agent"].to_list()
            L = int(x["minute"].max()) + 1
            f, l = rec["f"].to_numpy(), rec["l"].to_numpy()
            idx = np.arange(L)
            keep = ((idx[None, :] >= f[:, None]) & (idx[None, :] <= l[:, None])).all(0)
            if keep.sum() < MIN_KEEP:
                continue
            apos = {a: i for i, a in enumerate(agents)}
            xx = x.filter(pl.col("agent").is_in(agents))
            T = np.zeros((len(agents), L), np.int8)
            A = np.zeros((len(agents), L), np.int8)
            ai = np.array([apos[a] for a in xx["agent"].to_list()])
            mi = xx["minute"].to_numpy()
            T[ai, mi] = (xx["talk"].to_numpy() > 0)
            A[ai, mi] = (xx["state"].to_numpy() >= 3)
            k = len(kept)
            kept.append(d)
            st = np.zeros(L, bool)
            sd = stall.filter((pl.col("pt_date") == d) & pl.col("js"))
            if sd.height and "minute" in stall_cols:
                mm = sd["minute"].to_numpy()
                mm = mm[(mm >= 0) & (mm < L)]
                st[mm] = True
            rr = room.filter(pl.col("pt_date") == d)
            rmap = dict(zip(rr["agent"].to_list(), rr["room"].to_list()))
            arrs.update({f"talk_{k}": T, f"act_{k}": A, f"keep_{k}": keep, f"stall_{k}": st,
                         f"agents_{k}": np.array(agents, np.int16),
                         f"rooms_{k}": np.array([rmap.get(a) if rmap.get(a) is not None else -1 for a in agents], np.int16)})
            kd = kc.filter((pl.col("pt_date") == d) & (pl.col("goal_no") == g))
            if kd.height:
                mins = ((kd["t"] - ws[d]).dt.total_seconds() // 60).to_numpy().astype(int)
                for m_, rm in zip(mins, kd["room"].to_list()):
                    if 0 <= m_ < L:
                        krows.append({"day": k, "minute": int(m_), "room": int(rm) if rm is not None else -1})
        if not kept:
            continue
        arrs["days"] = np.array(kept)
        np.savez_compressed(OUT / "grids" / f"{uid}.npz", **arrs)
        pl.DataFrame(krows, schema={"day": pl.Int32, "minute": pl.Int32, "room": pl.Int32}).write_parquet(OUT / "kicks" / f"{uid}.parquet")
        # content
        wd = w30.filter(pl.col("pt_date").is_in(kept) & (pl.col("goal_no") == g) & (pl.lit(allow_holdout) | ~pl.col("holdout"))
                        & (pl.col("n_chat") >= 1))
        if wd.height:
            gid = wd["gid"].to_numpy()
            dmap = {d: i for i, d in enumerate(kept)}
            np.savez_compressed(OUT / "content" / f"{uid}.npz", agent=wd["agent"].to_numpy().astype(np.int16),
                                day=np.array([dmap[d] for d in wd["pt_date"].to_list()], np.int16),
                                win=wd["win30"].to_numpy().astype(np.int16),
                                vec_bge=np.asarray(Vb[gid], np.float32), vec_gte=np.asarray(Vg[gid], np.float32))
        meta.append({"unit_id": uid, "goal_no": g, "regime": r["regime"], "n_days": len(kept),
                     "N_med": float(np.median([len(arrs[f"agents_{k}"]) for k in range(len(kept))])),
                     "kept_min": int(sum(arrs[f"keep_{k}"].sum() for k in range(len(kept)))),
                     "n_kicks": len(krows), "content_rows": int(wd.height)})
    md = pl.DataFrame(meta)
    md.write_parquet(OUT / "unit_meta.parquet")
    prov = {"built_by": "hypotheses/H99-glauber-fluctuation-relaxation/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "tables": ["activity_bins_fixed", "outages_fixed/stall_minutes", "calendar",
                                                           "period_units", "kicks_classified", "chat_core",
                                                           "embeddings/agent_win30 (+ style_resid_period bge, gte)"]}],
            "params": {"min_record_minutes": MIN_REC, "min_kept_minutes": MIN_KEEP, "talk": "talk > 0",
                       "activity": "state >= 3", "presence": "state >= 2 span", "content": "n_chat >= 1"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print(md)


if __name__ == "__main__":
    main()
