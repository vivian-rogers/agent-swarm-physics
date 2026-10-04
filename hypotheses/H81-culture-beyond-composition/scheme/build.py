"""H81 scheme: eligible agent-day content vectors, calendar-week blocks and exogenous field directions (no text; holdout
dropped).

Inputs (data/processed/shared/): embeddings/agent_day.parquet + DQ5 agent_day_{style_resid,white32,style_resid_period}
_<model>.npy (both models), embeddings/statements.parquet (dominant room per agent-day), embeddings/goals.parquet +
goal vectors (goal_fields), kicks_classified (human messages) + chat_index + chat_<model>.npy, regime whiteners,
roster, period_units, calendar.
Output (data/processed/H81-culture-beyond-composition/):
  agentdays.parquet      one row per eligible agent-day (row = index into the vector arrays): agent, pt_date, goal_no,
                         regime, unit_id, block, week, room, n_stat
  vecs_<model>_<variant>.npy   unit-normalized 32-d vectors (float32), rows of agentdays
  dirs_<model>.npz       exogenous unit directions: per goal period (kickoff, goal, room kickoffs, human centroid),
                         per PT day (human centroid), per agent (#51 agent goals); keys in dirs_index.json
  blocks.parquet         block id (goal × ISO week), goal_no, regime, first/last/mid date, n_days, members
  _provenance.json
Eligibility: non-holdout (calendar holdout and common.holdout_mask, asserted), regime I/II/III kept here (analyses pick),
n_chat + n_intent >= 5, agent not 19 (Claude Code), 28, 30 (fine-tuned leaders).
Usage: uv run python hypotheses/H81-culture-beyond-composition/scheme/build.py
"""
from __future__ import annotations

import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra" / "shared"))
from common import REVISION, holdout_mask  # noqa: E402
from embed_models import load_whitener, goal_vectors, MODELS  # noqa: E402

SH = ROOT / "data/processed/shared"
ED = SH / "embeddings"
OUT = ROOT / "data/processed/H81-culture-beyond-composition"
HYP = "hypotheses/H81-culture-beyond-composition"
MODEL_LIST = ["bge_small", "gte_modernbert"]
VARIANTS = ["style_resid", "white32", "style_resid_period"]
EXCLUDE = {19, 28, 30}
MIN_STAT = 5


def git_commit() -> str:
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    d = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", HYP], capture_output=True, text=True).stdout
    return (r.stdout.strip() or "none") + ("+uncommitted" if d.strip() else "")


def unit(X: np.ndarray) -> np.ndarray:
    X = np.asarray(X, dtype=np.float64)
    n = np.linalg.norm(X, axis=-1, keepdims=True)
    n[n == 0] = 1.0
    return X / n


def eligible_agentdays() -> pl.DataFrame:
    ad = pl.read_parquet(ED / "agent_day.parquet").with_row_index("src")
    hm = np.array(holdout_mask(ad["pt_date"].to_list(), ad["goal_no"].to_list()))
    ad = ad.with_columns(pl.Series("hm", hm), (pl.col("n_chat") + pl.col("n_intent")).alias("n_stat"))
    ad = ad.filter(~pl.col("hm") & ~pl.col("holdout") & (pl.col("n_stat") >= MIN_STAT)
                   & ~pl.col("agent").is_in(list(EXCLUDE)))
    assert not ad["hm"].any() and not ad["holdout"].any()
    # unit of analysis
    pu = pl.read_parquet(SH / "period_units.parquet").select("unit_id", "goal_no", "days").explode("days") \
        .rename({"days": "pt_date"})
    ad = ad.join(pu, on=["goal_no", "pt_date"], how="left").unique(subset=["src"], keep="first", maintain_order=True)
    # dominant room of the agent-day (chat statements)
    st = pl.read_parquet(ED / "statements.parquet", columns=["kind", "agent", "pt_date", "room"]) \
        .filter((pl.col("kind") == "chat") & pl.col("room").is_not_null())
    dom = (st.group_by("agent", "pt_date", "room").len().sort("len", descending=True)
           .group_by("agent", "pt_date", maintain_order=True).first().select("agent", "pt_date", "room"))
    ad = ad.join(dom, on=["agent", "pt_date"], how="left")
    d = ad["pt_date"].str.to_date()
    iso = d.dt.iso_year().cast(pl.Int32) * 100 + d.dt.week().cast(pl.Int32)
    ad = ad.with_columns(iso.alias("week"))
    ad = ad.with_columns((pl.col("goal_no").cast(pl.Utf8) + pl.col("regime") + "w" + pl.col("week").cast(pl.Utf8))
                         .alias("block"))
    return ad.sort("src")


def build_blocks(ad: pl.DataFrame) -> pl.DataFrame:
    b = (ad.group_by("block", "goal_no", "regime", "week")
         .agg(pl.col("pt_date").min().alias("first_day"), pl.col("pt_date").max().alias("last_day"),
              pl.col("pt_date").n_unique().alias("n_days"), pl.col("agent").unique().sort().alias("members"))
         .with_columns(pl.col("members").list.len().alias("n_agents")))
    mid = [(dt.date.fromisoformat(a) + (dt.date.fromisoformat(z) - dt.date.fromisoformat(a)) / 2)
           for a, z in zip(b["first_day"], b["last_day"])]
    t0 = dt.date(2025, 1, 1)
    b = b.with_columns(pl.Series("mid_day", [(m - t0).days for m in mid], dtype=pl.Float64))
    return b.sort("first_day")


def directions(model: str, ad: pl.DataFrame, include_holdout: bool = False) -> tuple[dict, dict]:
    """Unit exogenous directions in each regime's 32-d whitened space for this model. include_holdout is used only by
    the guarded analysis/confirm.py."""
    g = pl.read_parquet(ED / "goals.parquet").with_row_index("row")
    GV = goal_vectors(model).astype(np.float32)
    W = {r: load_whitener(r, 32, model) for r in ("I", "II", "III")}
    goals_keep = set(ad["goal_no"].unique().to_list())
    regimes_of_goal = {gn: sorted(set(ad.filter(pl.col("goal_no") == gn)["regime"].to_list())) for gn in goals_keep}
    vecs, index = [], []

    def add(key: dict, raw: np.ndarray, regime: str):
        v = unit(W[regime](raw[None, :]))[0]
        index.append({**key, "regime": regime, "i": len(vecs)})
        vecs.append(v)

    for r in g.filter((include_holdout | ~pl.col("holdout")) & pl.col("goal_no").is_in(list(goals_keep))).iter_rows(named=True):
        kind = str(r["kind"])
        if kind == "goal_whole":
            continue
        for reg in regimes_of_goal[r["goal_no"]]:
            key = {"level": "goal", "goal_no": r["goal_no"], "kind": kind, "room": r["room"], "agent": r["agent"],
                   "valid_from": r["valid_from"], "valid_to": r["valid_to"], "pt_date": None}
            add(key, GV[r["row"]], reg)
    # human messages: per goal period and per PT day
    k = pl.read_parquet(SH / "kicks_classified.parquet").filter(pl.col("kind") == "human_message") \
        .select("message_id", "goal_no", "pt_date")
    hm = np.array(holdout_mask(k["pt_date"].to_list(), k["goal_no"].to_list()))
    if not include_holdout:
        k = k.filter(~pl.Series(hm))
    ci = pl.read_parquet(ED / "chat_index.parquet").with_row_index("row")
    k = k.join(ci, on="message_id", how="inner")
    C = np.load(ED / f"chat_{MODELS[model]['suffix']}.npy", mmap_mode="r")
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "regime"]).with_columns(pl.col("regime").cast(pl.Utf8))
    k = k.join(cal, on="pt_date", how="left").filter(pl.col("goal_no").is_in(list(goals_keep)))
    for (gn, reg), sub in k.group_by(["goal_no", "regime"]):
        rows = np.sort(sub["row"].to_numpy())
        Xw = unit(W[reg](np.asarray(C[rows], dtype=np.float32)))
        index.append({"level": "goal", "goal_no": gn, "kind": "human", "room": None, "agent": None,
                      "valid_from": None, "valid_to": None, "pt_date": None, "regime": reg, "i": len(vecs)})
        vecs.append(unit(Xw.mean(0)))
    for (day, gn, reg), sub in k.group_by(["pt_date", "goal_no", "regime"]):
        rows = np.sort(sub["row"].to_numpy())
        Xw = unit(W[reg](np.asarray(C[rows], dtype=np.float32)))
        index.append({"level": "day", "goal_no": gn, "kind": "human", "room": None, "agent": None,
                      "valid_from": None, "valid_to": None, "pt_date": day, "regime": reg, "i": len(vecs)})
        vecs.append(unit(Xw.mean(0)))
    return np.array(vecs, dtype=np.float32), index


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ad = eligible_agentdays()
    src = ad["src"].to_numpy()
    for m in MODEL_LIST:
        for v in VARIANTS:
            X = np.load(ED / f"agent_day_{v}_{MODELS[m]['suffix']}.npy").astype(np.float32)[src]
            np.save(OUT / f"vecs_{m}_{v}.npy", unit(X).astype(np.float32))
        V, idx = directions(m, ad)
        np.savez_compressed(OUT / f"dirs_{m}.npz", V=V)
        (OUT / f"dirs_index_{m}.json").write_text(json.dumps(idx))
        print(m, "directions", len(idx), flush=True)
    ad.drop("hm").write_parquet(OUT / "agentdays.parquet")
    blocks = build_blocks(ad)
    blocks.write_parquet(OUT / "blocks.parquet")
    print("agent-days", ad.height, "blocks", blocks.height, flush=True)
    prov = {"built_by": f"{HYP}/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["embeddings/agent_day", "agent_day_{style_resid,white32,style_resid_period}_<model>",
                                   "embeddings/statements", "embeddings/goals", "goal_vectors", "kicks_classified",
                                   "chat_index", "chat_<model>", "whitening_<model>_<regime>", "period_units",
                                   "calendar"]}],
            "params": {"min_statements": MIN_STAT, "exclude_agents": sorted(EXCLUDE), "models": MODEL_LIST,
                       "variants": VARIANTS, "block": "goal_no x ISO week", "holdout": "dropped (holdout_mask)"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    main()
