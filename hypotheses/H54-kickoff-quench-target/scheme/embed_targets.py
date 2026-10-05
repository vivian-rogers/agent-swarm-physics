"""H54 round 2 (R1): embed the two-target texts locally with both DQ5 models. Vectors only; no text is stored.

Targets
  #12 motions   per DQ6 debate: the first quoted string (>= 20 chars) after the word "motion" in any agent message of the
                window [draft - 5 min, end of the deb phase]
                (amended before any outcome: a 30-min margin picked up the previous debate's motion in #02 and #08); else the first "This House / THW / THBT" sentence.
  #19 options   kickoff clauses "A) ..." and "B) ..." (verbatim clauses, cut at the comma / full stop)
  #21 options   kickoff paragraphs "a) ..." and "b) ..." (verbatim paragraphs)
Embedding: bge-small (normalize, max_seq 256) and gte-modernbert (pinned revision, CLS pooling, max_seq 256), text cut at
2,000 characters, as in build_embeddings.py / build_embeddings_v2.py.

Outputs (data/processed/H54-kickoff-quench-target/r2/):
  targets.parquet          tid, goal_no, unit (debate_NN | A | B), rule, message_id (codes only), n_chars, found
  targets_bge_small.npy    (n, 384) raw unit vectors (rows = tid); whiten downstream
  targets_gte_modernbert.npy (n, 768)

Usage: UV_OFFLINE=1 HF_HUB_OFFLINE=1 uv run --with sentence-transformers python hypotheses/H54-kickoff-quench-target/scheme/embed_targets.py
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
           "TOKENIZERS_PARALLELISM"):
    os.environ.setdefault(_v, "2" if _v != "TOKENIZERS_PARALLELISM" else "false")

import datetime as dt  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis"))
import h54lib as L  # noqa: E402
import embed_models as EM  # noqa: E402  (h54lib put infra/shared on the path)

OUT = L.OUT_BASE / "r2"
MAX_CHARS = 2000
RX_Q = re.compile(r"motion[^\"“\n]{0,80}[\"“]([^\"”\n]{20,250})[\"”]", re.I)
RX_TH = re.compile(r"\b(This House|THW|THBT|TH would|TH believes|TH prefers)\b[^.\n\"”]{15,250}", re.I)


def motions() -> list[dict]:
    gt = pl.read_parquet(L.SHARED / "ground_truth_labels.parquet").filter(
        (pl.col("goal_no") == 12) & pl.col("preferred") & ~pl.col("holdout"))
    cc = pl.read_parquet(L.SHARED / "chat_core.parquet", columns=["message_id", "t", "speaker_kind", "goal_no"]).filter(
        (pl.col("goal_no") == 12) & (pl.col("speaker_kind").cast(pl.String) == "agent"))
    tx = pl.read_parquet(L.SHARED / "chat_text.parquet", columns=["message_id", "text"]).filter(
        pl.col("message_id").is_in(cc["message_id"].to_list()))
    cc = cc.join(tx, on="message_id").sort("t")
    out = []
    for unit in sorted(gt["unit"].unique().to_list()):
        g = gt.filter(pl.col("unit") == unit)
        t0 = g.filter(pl.col("label_kind") == "team")["t_valid_from"].min()
        deb = g.filter((pl.col("label_kind") == "phase") & (pl.col("value") == "deb"))
        t1 = deb["t_valid_to"].max() if deb.height else g["t_valid_to"].max()
        w = cc.filter((pl.col("t") >= t0 - dt.timedelta(minutes=5)) & (pl.col("t") <= t1))
        rec = {"goal_no": 12, "unit": unit, "rule": None, "message_id": None, "text": None}
        for rule, rx in (("quoted_after_motion", RX_Q), ("this_house_sentence", RX_TH)):
            for mid, text in zip(w["message_id"].to_list(), w["text"].to_list()):
                m = rx.search(text or "")
                if m:
                    rec.update({"rule": rule, "message_id": mid, "text": m.group(1) if rule == "quoted_after_motion" else m.group(0)})
                    break
            if rec["text"]:
                break
        out.append(rec)
    return out


def options() -> list[dict]:
    km = pl.read_parquet(L.OUT_BASE / "kick_msgs.parquet").filter(pl.col("goal_no").is_in([19, 21]))
    tx = pl.read_parquet(L.SHARED / "chat_text.parquet", columns=["message_id", "text"]).filter(
        pl.col("message_id").is_in(km["message_id"].to_list()))
    k = km.join(tx, on="message_id").sort("t")
    out = []
    b19 = "\n".join(k.filter(pl.col("goal_no") == 19)["text"].to_list())
    m = re.search(r"\bA\)\s*(.+?),?\s+and\s+B\)\s*(.+?)[.!]", b19)
    for u, i in (("A", 1), ("B", 2)):
        out.append({"goal_no": 19, "unit": u, "rule": "kickoff_clause", "message_id": None, "text": m.group(i) if m else None})
    b21 = "\n".join(k.filter(pl.col("goal_no") == 21)["text"].to_list())
    m = re.search(r"(?:^|\n)\s*a\)\s*(.+?)\n\s*\n\s*b\)\s*(.+?)\n\s*\n", b21, re.S)
    for u, i in (("A", 1), ("B", 2)):
        out.append({"goal_no": 21, "unit": u, "rule": "kickoff_paragraph", "message_id": None, "text": m.group(i) if m else None})
    return out


def main():
    rows = motions() + options()
    texts = [(r["text"] or "")[:MAX_CHARS] for r in rows]
    found = [bool(r["text"]) for r in rows]
    OUT.mkdir(parents=True, exist_ok=True)
    from sentence_transformers import SentenceTransformer
    import torch
    dev = "mps" if torch.backends.mps.is_available() else "cpu"
    torch.set_num_threads(2)
    for model in ("bge_small", "gte_modernbert"):
        spec = EM.MODELS[model]
        m = SentenceTransformer(spec["hf"], revision=spec.get("revision"), device=dev)
        m.max_seq_length = 256
        V = np.zeros((len(rows), spec["dim"]), dtype=np.float32)
        idx = [i for i, f in enumerate(found) if f]
        V[idx] = m.encode([texts[i] for i in idx], batch_size=16, normalize_embeddings=True, convert_to_numpy=True)
        np.save(OUT / f"targets_{model}.npy", V.astype(np.float16))
        del m
    df = pl.DataFrame([{"tid": i, "goal_no": r["goal_no"], "unit": r["unit"], "rule": r["rule"], "message_id": r["message_id"],
                        "n_chars": len(r["text"] or ""), "found": found[i]} for i, r in enumerate(rows)])
    df.write_parquet(OUT / "targets.parquet")
    print(df)
    L.provenance("scheme/embed_targets.py", ["ground_truth_labels (#12 teams/phases)", "chat_core", "chat_text (in memory)",
                                             "H54 kick_msgs", "BAAI/bge-small-en-v1.5", "Alibaba-NLP/gte-modernbert-base"],
                 {"window": "draft - 5 min .. end of deb", "max_chars": MAX_CHARS, "max_seq_length": 256})


if __name__ == "__main__":
    main()
