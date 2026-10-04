"""DQ5: a second sentence-embedding model over every embedded chat message and intention, plus its agent vectors
and per-regime whitening (mirrors build_embeddings.py + build_agent_vectors.py for bge-small).

Model: Alibaba-NLP/gte-modernbert-base (pinned revision in embed_models.MODELS), 768-d, CLS pooling, no prefix.
Inputs are identical to the bge-small run: chat_text / intentions_text rows in chat_index / intentions_index order,
text cut at 2,000 characters, max 256 tokens. Computed in float32 on MPS, stored float16, L2-normalized.

Stages
  embed    chat_gte_modernbert.npy (rows of chat_index.parquet, 183,485 incl. human/automated messages, so the array
           is a drop-in for chat_bge_small.npy) and intentions_gte_modernbert.npy (rows of intentions_index.parquet).
           Resumable: length-sorted chunks of CHUNK rows are written to embeddings/_dq5_work/<kind>/c<k>.npy and
           skipped on restart; the final array is assembled at the end and the work folder removed.
  vectors  agent_day_vec_gte_modernbert.npy / agent_win30_vec_gte_modernbert.npy (rows of the EXISTING
           agent_day.parquet / agent_win30.parquet; the grouping is recomputed and asserted identical) and
           whitening_gte_modernbert_<regime>.npz (mean, top-128 components, eigenvalues; non-holdout statements only).
           statements.parquet and the bge files are read, never rewritten.

  goals    goal_vectors_gte_modernbert.npy: rows of goals.parquet (goal_fields.py's texts and chunking, mean of unit
           chunk embeddings), so goal-field projections (H01, H10, H24) can be swapped too.

Usage: uv run --with sentence-transformers python infra/shared/build_embeddings_v2.py [embed|vectors|goals|all]
Threads: CPU capped at 2 (torch, BLAS, polars, tokenizers).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import shutil  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_agent_vectors import N_COMP, group_means  # noqa: E402
from common import OUT, write_provenance  # noqa: E402
from embed_models import ED, MODELS, emb_path, group_ids, statement_embeddings, whitening_path  # noqa: E402

MODEL = "gte_modernbert"
CHUNK = 4096
BATCH = 128
MAX_CHARS = 2000
MAX_SEQ = 256
WORK = ED / "_dq5_work"


def load_jobs() -> dict[str, pl.DataFrame]:
    chat = pl.read_parquet(OUT / "chat_text.parquet", columns=["message_id", "text"])
    ci = pl.read_parquet(ED / "chat_index.parquet")
    assert chat["message_id"].equals(ci["message_id"]), "chat_text order differs from chat_index"
    it = pl.read_parquet(OUT / "intentions_text.parquet", columns=["event_index", "goal_text"]).drop_nulls("goal_text")
    ii = pl.read_parquet(ED / "intentions_index.parquet")
    assert it["event_index"].equals(ii["event_index"]), "intentions_text order differs from intentions_index"
    return {"chat": chat["text"], "intentions": it["goal_text"]}


def embed():
    import torch
    torch.set_num_threads(2)
    from sentence_transformers import SentenceTransformer
    spec = MODELS[MODEL]
    dev = "mps" if torch.backends.mps.is_available() else "cpu"
    m = SentenceTransformer(spec["hf"], revision=spec["revision"], device=dev)
    m.max_seq_length = MAX_SEQ
    jobs = load_jobs()
    for name, ser in jobs.items():
        final = emb_path(name, MODEL)
        if final.exists():
            print(f"{name}: {final.name} exists, skipping", flush=True)
            continue
        t0 = time.time()
        texts = [s[:MAX_CHARS] for s in ser.to_list()]
        order = np.argsort(np.array([len(s) for s in texts]), kind="stable")
        wd = WORK / name
        wd.mkdir(parents=True, exist_ok=True)
        n_chunks = (len(order) + CHUNK - 1) // CHUNK
        for k in range(n_chunks):
            f = wd / f"c{k:04d}.npy"
            if f.exists():
                continue
            idx = order[k * CHUNK:(k + 1) * CHUNK]
            e = m.encode([texts[j] for j in idx], batch_size=BATCH, normalize_embeddings=True, convert_to_numpy=True)
            tmp = wd / f"c{k:04d}.tmp.npy"
            np.save(tmp, e.astype(np.float16))
            tmp.rename(f)
            print(f"{name} chunk {k + 1}/{n_chunks} {time.time() - t0:.0f}s", flush=True)
        emb = np.zeros((len(texts), spec["dim"]), dtype=np.float16)
        filled = np.zeros(len(texts), dtype=bool)
        for k in range(n_chunks):
            idx = order[k * CHUNK:(k + 1) * CHUNK]
            emb[idx] = np.load(wd / f"c{k:04d}.npy")
            filled[idx] = True
        assert filled.all()
        nrm = np.linalg.norm(emb.astype(np.float32), axis=1)
        assert np.isfinite(nrm).all() and abs(nrm.mean() - 1) < 1e-2, "embedding norms off"
        tmp = final.with_suffix(".tmp.npy")
        np.save(tmp, emb)
        tmp.rename(final)
        shutil.rmtree(wd)
        print(f"{name} {emb.shape} {time.time() - t0:.0f}s", flush=True)
    if WORK.exists() and not any(WORK.iterdir()):
        WORK.rmdir()
    write_provenance("build_embeddings_v2:embed", ["chat_text", "intentions_text", "embeddings/chat_index",
                                                  "embeddings/intentions_index"],
                     {"model": spec["hf"], "revision": spec["revision"], "device": dev, "compute_dtype": "float32",
                      "dtype": "float16", "normalized": True, "pooling": "cls", "prefix": None,
                      "max_seq_length": MAX_SEQ, "max_chars": MAX_CHARS, "rows": "all chat_index and intentions_index rows"})


def vectors():
    t0 = time.time()
    st = pl.read_parquet(ED / "statements.parquet")
    E = statement_embeddings(MODEL, st, mmap=False)
    print(f"statements {E.shape}", flush=True)
    for level in ("day", "win30"):
        idx, gid, n_groups = group_ids(st, level)
        V = group_means(E[idx], gid, n_groups)
        np.save(ED / f"agent_{level}_vec{MODELS[MODEL]['vec_suffix']}.npy", V)
        print(f"agent_{level}: {n_groups} rows", flush=True)
    hold = st["holdout"].to_numpy(); reg = st["regime"].to_numpy()
    for r in sorted(set(reg)):
        sel = (reg == r) & ~hold
        X = E[sel].astype(np.float64); mu = X.mean(0)
        C = np.cov((X - mu).T, bias=True)
        w, U = np.linalg.eigh(C)
        o = np.argsort(w)[::-1][:N_COMP]
        np.savez(whitening_path(r, MODEL), mean=mu.astype(np.float32), components=U[:, o].astype(np.float32),
                 eigenvalues=w[o].astype(np.float32), n=int(sel.sum()))
        print(f"whitening {r}: n={sel.sum()}, top-5 eigenvalue share {w[o][:5].sum() / w.sum():.3f}", flush=True)
    write_provenance("build_embeddings_v2:vectors", [f"embeddings/{{chat,intentions}}_{MODELS[MODEL]['suffix']}.npy",
                                                    "embeddings/statements", "embeddings/agent_day",
                                                    "embeddings/agent_win30"],
                     {"model": MODELS[MODEL]["hf"], "window_min": 30, "whitening_components": N_COMP,
                      "whitening_fit": "non-holdout statements per regime", "rows": "existing agent_day / agent_win30"})
    print(f"vectors done {time.time() - t0:.0f}s", flush=True)


def goals():
    """Goal fields (goal_fields.py rows: goal, goal_whole, kickoff, kickoff_room, agent_goal) with the second model:
    the same texts and chunking (imported from goal_fields.goal_texts, read-only), mean of unit chunk embeddings."""
    import torch
    torch.set_num_threads(2)
    from sentence_transformers import SentenceTransformer
    from goal_fields import goal_texts
    spec = MODELS[MODEL]
    meta, texts = goal_texts()
    ref = pl.read_parquet(ED / "goals.parquet")
    chk = pl.DataFrame({"goal_no": [m["goal_no"] for m in meta], "kind": [m["kind"] for m in meta],
                        "n_chunks": [len(t) for t in texts]})
    assert chk.equals(ref.select(pl.col("goal_no").cast(pl.Int64), pl.col("kind").cast(pl.String),
                                 pl.col("n_chunks").cast(pl.Int64))), "goal texts differ from goals.parquet"
    dev = "mps" if torch.backends.mps.is_available() else "cpu"
    m = SentenceTransformer(spec["hf"], revision=spec["revision"], device=dev)
    m.max_seq_length = MAX_SEQ
    V = np.zeros((len(texts), spec["dim"]), dtype=np.float32)
    for i, ch in enumerate(texts):
        V[i] = m.encode(ch, batch_size=32, normalize_embeddings=True, convert_to_numpy=True).mean(0)
    del texts
    np.save(ED / f"goal_vectors_{spec['suffix']}.npy", V.astype(np.float16))
    print(f"goal vectors {V.shape}", flush=True)
    write_provenance("build_embeddings_v2:goals", ["goal_fields.goal_texts (village_goals, agent_goals, chat_text in memory)",
                                                  "embeddings/goals"],
                     {"model": spec["hf"], "revision": spec["revision"], "max_seq_length": MAX_SEQ,
                      "normalized": "chunks unit, mean not renormalized", "rows": "goals.parquet"})


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    if stage in ("embed", "all"):
        embed()
    if stage in ("vectors", "all"):
        vectors()
    if stage in ("goals", "all"):
        goals()
