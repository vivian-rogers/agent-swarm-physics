"""H50 round-2 scheme: per-unit message, statement and read tables for the content gate (R1), the relay graph (R6)
and the regime-I kernel (R2). Shared tables only; no text.

For every round-1 unit file units/<unit>.npz (calls keep their order there), writes r2/units/<unit>.npz with:
  m_t, m_day, m_sender (calling-agent index or -1), m_room, m_srow (statements.parquet row or -1),
  m_prod (position of the producing call in the unit's call arrays, or -1: summary call, other agent, other day)
  p_msg, p_rec, p_pos (receiving-call position), p_ment       (context_ledger_items, kind agent)
  c_tfirst, c_mode (0 chat, 1 computer use), c_src (call_windows.start_src code), c_lat_agent (agent median chained-call
  latency, s; the ledger's placement constant)
Messages are agent chat messages (chat_core speaker_kind agent) of the unit's days, sorted by (t, message_id).
Reserved data: every day is checked with common.holdout_mask (hard assertion).

Usage: uv run python hypotheses/H50-field-vs-coupling-transfer-lag/scheme/build_r2.py [--only 51b,27]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import REVISION, holdout_mask  # noqa: E402
from build import load_unit  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H50-field-vs-coupling-transfer-lag"
R2 = OUT / "r2"
BASE = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc).timestamp()
SRC = ["logged", "prev_end", "pause_expiry", "marker", "latency"]


def secs(s: pl.Series) -> np.ndarray:
    return s.dt.epoch("us").to_numpy() / 1e6 - BASE


def git_commit() -> str:
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip() or "none"


def load_tabs():
    st = pl.read_parquet(SH / "embeddings/statements.parquet", columns=["kind", "src_row"]).with_row_index("srow")
    ci = pl.read_parquet(SH / "embeddings/chat_index.parquet").with_row_index("src_row")
    st = st.filter(pl.col("kind") == "chat").join(ci, on="src_row").select("message_id", "srow")
    cw = pl.read_parquet(SH / "call_windows.parquet", columns=["turn_id", "agent", "pt_date", "holdout", "ctx_mode", "start_src",
                                                               "gap_kind", "t_first", "t_call"])
    # the ledger's placement constant: agent median latency on chained computer-use calls (start_src prev_end, busy)
    lat = (cw.filter((pl.col("start_src") == "prev_end") & (pl.col("ctx_mode") == "cu") & (pl.col("gap_kind") == "busy"))
           .with_columns(((pl.col("t_first") - pl.col("t_call")).dt.total_microseconds() / 1e6).alias("l"))
           .filter(pl.col("l") > 0).group_by("agent").agg(pl.col("l").median().alias("lat_agent"), pl.len().alias("n"))
           .filter(pl.col("n") >= 20))
    return dict(
        chat=pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "pt_date", "room", "speaker_kind", "agent"]),
        st=st,
        prod=pl.read_parquet(SH / "producing_calls.parquet", columns=["message_id", "turn_id_prod"]),
        items=pl.read_parquet(SH / "context_ledger_items.parquet", columns=["turn_id", "message_id", "kind", "ment"]),
        cw=cw.select("turn_id", "ctx_mode", "start_src", "t_first", "agent"),
        lat=lat,
    )


def build(unit: str, tabs):
    U = load_unit(OUT / "units" / f"{unit}.npz")
    days = [str(d) for d in U["days"]]
    goal = int(U["goal_no"])
    assert not any(holdout_mask(days, [goal] * len(days))), f"reserved day in {unit}"
    c = U["calls"]
    dix = {d: i for i, d in enumerate(days)}
    codes = U["agent_codes"]
    aix = {int(a): i for i, a in enumerate(codes)}
    pos = {int(t): i for i, t in enumerate(c["turn_id"])}
    ch = (tabs["chat"].filter(pl.col("pt_date").is_in(days) & (pl.col("speaker_kind") == "agent")).sort("t", "message_id")
          .join(tabs["st"], on="message_id", how="left").join(tabs["prod"], on="message_id", how="left"))
    snd = np.array([aix.get(int(a), -1) if a is not None else -1 for a in ch["agent"].to_list()], np.int64)
    prod = np.array([pos.get(int(t), -1) if t is not None else -1 for t in ch["turn_id_prod"].to_list()], np.int64)
    mday = np.array([dix[d] for d in ch["pt_date"].to_list()], np.int64)
    ok = (prod >= 0)
    ok &= np.where(prod >= 0, c["agent"][np.maximum(prod, 0)] == snd, False)
    ok &= np.where(prod >= 0, c["day"][np.maximum(prod, 0)] == mday, False)
    prod = np.where(ok, prod, -1)
    mid = ch["message_id"].to_list()
    midx = {m: i for i, m in enumerate(mid)}
    it = tabs["items"].filter((pl.col("kind") == "agent") & pl.col("turn_id").is_in(c["turn_id"]) & pl.col("message_id").is_in(mid))
    p_pos = np.array([pos[int(t)] for t in it["turn_id"].to_list()], np.int64)
    p_msg = np.array([midx[m] for m in it["message_id"].to_list()], np.int64)
    o = np.lexsort((p_pos, c["agent"][p_pos]))
    cwu = pl.DataFrame({"turn_id": c["turn_id"]}).join(tabs["cw"], on="turn_id", how="left")
    assert cwu["turn_id"].to_list() == c["turn_id"].tolist()
    lat = dict(zip(tabs["lat"]["agent"].to_list(), tabs["lat"]["lat_agent"].to_list()))
    glat = float(np.median(tabs["lat"]["lat_agent"].to_numpy()))
    out = dict(
        m_t=secs(ch["t"]), m_day=mday, m_sender=snd, m_room=ch["room"].fill_null(-1).to_numpy().astype(np.int64),
        m_srow=ch["srow"].fill_null(-1).to_numpy().astype(np.int64), m_prod=prod,
        p_msg=p_msg[o], p_rec=c["agent"][p_pos][o], p_pos=p_pos[o], p_ment=it["ment"].to_numpy()[o].astype(bool),
        c_tfirst=secs(cwu["t_first"]), c_mode=(cwu["ctx_mode"].cast(pl.String) == "cu").to_numpy().astype(np.int8),
        c_src=np.array([SRC.index(s) for s in cwu["start_src"].cast(pl.String).to_list()], np.int8),
        c_lat_agent=np.array([lat.get(int(codes[a]), glat) for a in c["agent"]], np.float32),
    )
    R2.joinpath("units").mkdir(parents=True, exist_ok=True)
    np.savez_compressed(R2 / "units" / f"{unit}.npz", **out)
    return dict(unit=unit, n_msgs=len(mid), n_stmt=int((out["m_srow"] >= 0).sum()), n_prod=int((prod >= 0).sum()),
                n_pairs=len(p_msg), n_pairs_r1=int(len(U["mpairs"]["msg"])))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    units = sorted(p.stem for p in (OUT / "units").glob("*.npz"))
    if args.only:
        units = [u for u in units if u in args.only.split(",")]
    tabs = load_tabs()
    rows = []
    for u in units:
        r = build(u, tabs)
        rows.append(r)
        print(r, flush=True)
    df = pl.DataFrame(rows)
    p = R2 / "units.parquet"
    if args.only and p.exists():
        df = pl.concat([pl.read_parquet(p).filter(~pl.col("unit").is_in(df["unit"])), df])
    df.write_parquet(p)
    prov = dict(built_by="hypotheses/H50-field-vs-coupling-transfer-lag/scheme/build_r2.py", git_commit=git_commit(),
                inputs=[dict(source="ai-village", revision=REVISION,
                             tables=["chat_core", "embeddings/statements", "embeddings/chat_index", "producing_calls",
                                     "context_ledger_items", "call_windows"])],
                params=dict(messages="agent chat messages of the round-1 unit days, sorted (t, message_id)",
                            pairs="context_ledger_items kind agent", lat_agent="median t_first - t_call, prev_end busy cu calls"),
                built_at=dt.datetime.now(dt.timezone.utc).isoformat())
    (R2 / "_provenance.json").write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    main()
