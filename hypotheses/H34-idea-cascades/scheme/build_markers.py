"""H34 scheme, step 1: marker uses in every non-holdout chat message (hashed; no text written).

  uv run python hypotheses/H34-idea-cascades/scheme/build_markers.py

Outputs in data/processed/H34-idea-cascades/markers/:
  uses.parquet        msg (row in chat_core sorted by t), marker (int64 hash), cls (0 U, 1 D, 2 N, 3 W)
  first_seen.parquet  marker, cls, first_msg, first_t, first_goal, n_msgs, n_goals   (over the non-holdout corpus)
Held-out messages are filtered out on the chat_core side before any text is read (`holdout_mask` + calendar.holdout).
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(HERE))
from common import REVISION, git_commit, holdout_mask  # noqa: E402
import markers as M  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H34-idea-cascades"
N_WORKERS = 2
_ROS: frozenset = frozenset()


def _init(ros):
    global _ROS
    _ROS = ros
    M.dictionary()


def _work(chunk):
    rows, texts = chunk
    msg, mk, cl = [], [], []
    for r, t in zip(rows, texts):
        for c, x in M.extract(t, _ROS):
            msg.append(r)
            mk.append(M.marker_id(c, x))
            cl.append(M.CLS[c])
    return np.array(msg, np.uint32), np.array(mk, np.int64), np.array(cl, np.uint8)


def non_holdout_chat() -> pl.DataFrame:
    chat = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "pt_date", "goal_no"]).with_row_index("msg")
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "holdout"])
    chat = chat.join(cal, on="pt_date", how="left")
    hm = np.array(holdout_mask(chat["pt_date"].to_list(), chat["goal_no"].to_list()))
    keep = ~hm & ~chat["holdout"].fill_null(False).to_numpy()
    return chat.filter(pl.Series(keep)).drop("holdout")


def main():
    t0 = time.time()
    (OUT / "markers").mkdir(parents=True, exist_ok=True)
    chat = non_holdout_chat()
    ids = chat.select("message_id", "msg")
    # text only for non-holdout ids (semi-join before collecting)
    txt = (pl.scan_parquet(SH / "chat_text.parquet").select("message_id", "text")
           .join(ids.lazy(), on="message_id", how="inner").select("msg", "text").collect().sort("msg"))
    ros = M.roster_full_names(pl.read_parquet(SH / "roster.parquet")["name"].to_list())
    rows, texts = txt["msg"].to_list(), txt["text"].to_list()
    del txt
    step = 4000
    chunks = [(rows[i:i + step], texts[i:i + step]) for i in range(0, len(rows), step)]
    with Pool(N_WORKERS, initializer=_init, initargs=(ros,)) as pool:
        parts = pool.map(_work, chunks, chunksize=1)
    del texts, chunks
    dnw = pl.DataFrame({"msg": np.concatenate([p[0] for p in parts]), "marker": np.concatenate([p[1] for p in parts]),
                        "cls": np.concatenate([p[2] for p in parts])})
    # U: artifacts (repo / site / file) named in chat (url or bare)
    art = pl.read_parquet(SH / "artifacts.parquet", columns=["artifact", "kind"])
    am = (pl.read_parquet(SH / "artifact_mentions.parquet", columns=["artifact", "source", "how", "message_id"])
          .filter((pl.col("source") == "chat") & pl.col("how").cast(pl.Utf8).is_in(["url", "bare"]))
          .join(art, on="artifact").filter(pl.col("kind").cast(pl.Utf8).is_in(["repo", "site", "file"]))
          .join(ids, on="message_id", how="inner"))
    u = am.select("msg", pl.col("artifact").map_elements(lambda a: M.marker_id("U", str(a)), return_dtype=pl.Int64)
                  .alias("marker"), pl.lit(0, pl.UInt8).alias("cls"))
    uses = pl.concat([u.with_columns(pl.col("msg").cast(pl.UInt32)), dnw]).unique(["msg", "marker"]).sort("msg", "marker")
    uses.write_parquet(OUT / "markers/uses.parquet", compression="zstd")
    meta = chat.select("msg", "t", "goal_no")
    fs = (uses.join(meta, on="msg").group_by("marker")
          .agg(pl.col("cls").first(), pl.col("msg").min().alias("first_msg"), pl.col("t").min().alias("first_t"),
               pl.col("goal_no").sort_by("msg").first().alias("first_goal"), pl.len().alias("n_msgs"),
               pl.col("goal_no").n_unique().alias("n_goals")))
    fs.write_parquet(OUT / "markers/first_seen.parquet", compression="zstd")
    prov_path = OUT / "_provenance.json"
    prov = json.loads(prov_path.read_text()) if prov_path.exists() else {}
    prov["markers"] = {"built_by": "hypotheses/H34-idea-cascades/scheme/build_markers.py", "git_commit": git_commit(),
                       "inputs": [{"source": "ai-village", "revision": REVISION,
                                   "tables": ["shared/chat_core", "shared/chat_text (in memory, non-holdout only)",
                                              "shared/artifact_mentions", "shared/artifacts", "shared/roster",
                                              "shared/calendar"]}],
                       "params": {"dictionary": str(M.DICT_PATH), "dictionary_sha1": M.DICT_SHA1, "classes": M.CLS,
                                  "holdout": "excluded before reading text"},
                       "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    prov_path.write_text(json.dumps(prov, indent=1))
    print(f"{chat.height} non-holdout messages, {uses.height} marker uses, {fs.height} markers; "
          f"by class {uses.group_by('cls').len().sort('cls').to_dicts()}; {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
