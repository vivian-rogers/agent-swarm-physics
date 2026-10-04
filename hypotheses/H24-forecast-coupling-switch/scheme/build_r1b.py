"""H24 round 1b inputs (improved data, 2026-10-04). Writes data/processed/H24-forecast-coupling-switch/G21/r1b/ and
placebo/r1b/; the round-1 files are left untouched so the old path still runs.

What changes:
  * goal direction from the shared goal fields (embeddings/goals.parquet, goal_fields.py) for #21 and the N2 placebo
    weeks, instead of H24's own goal + kickoff embedding (a slightly different boilerplate filter);
  * a multi-direction goal field: the whitened vectors of every goal-text and kickoff chunk (goal_fields chunking),
    so the field can be removed along all of them (vector-spins pitfall: one-direction removal leaks field into
    "coupling");
  * a second embedding model (gte-modernbert, DQ5) for statements (shared vectors) and the #21 document chunks
    (re-embedded here from the gitignored text sidecar, same chunking as scheme/build.py);
  * DQ5 statement flags for dedupe; style-residualized (within goal period) 32-d statement vectors.

Outputs (no text):
  G21/r1b/stmt.parquet                   row (round-1 statements row), srow, DQ5 flags
  G21/r1b/stmt_w64_gte_modernbert.npy    regime-I whitened gte coordinates (64), row-aligned with G21/statements.parquet
  G21/r1b/stmt_sr32_<model>.npy          style-residualized 32-d statement vectors (both models)
  G21/r1b/docs_w64_gte_modernbert.npy    regime-I whitened gte document-chunk coordinates, row-aligned with docs.parquet
  G21/r1b/field_<model>.npz              ghat (shared goal + kickoff, 64), goal, kickoff, chunks (k x 64, all goal-text and
                                         kickoff chunks), for #21
  placebo/r1b/field_<model>.npz          the same per N2 placebo week (goal_no array, ghat (W x 64), chunk lists)
  G21/r1b/check.json                     row alignment, doc re-chunking check, cos(H24 ghat, shared ghat)
Usage: UV_OFFLINE=1 HF_HUB_OFFLINE=1 uv run --offline --with sentence-transformers python \
           hypotheses/H24-forecast-coupling-switch/scheme/build_r1b.py
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h24lib import H24, unit  # noqa: E402
from build import chunk_text, doc_content  # noqa: E402
from common import REVISION, git_commit, load_holdout  # noqa: E402
import embed_models as EM  # noqa: E402
import goal_fields as GF  # noqa: E402

G = H24 / "G21"
DEST = G / "r1b"
PDEST = H24 / "placebo" / "r1b"
MODELS = ("bge_small", "gte_modernbert")


def st_model(model: str):
    import torch
    from sentence_transformers import SentenceTransformer
    torch.set_num_threads(2)
    dev = "mps" if torch.backends.mps.is_available() else "cpu"
    spec = EM.MODELS[model]
    m = SentenceTransformer(spec["hf"], revision=spec.get("revision"), device=dev)
    m.max_seq_length = 256
    return m


def encode(m, texts, bs=16):
    order = np.argsort([len(s) for s in texts])
    out = None
    for k in range(0, len(texts), bs):
        idx = order[k:k + bs]
        e = m.encode([texts[j][:2000] for j in idx], batch_size=bs, normalize_embeddings=True, convert_to_numpy=True)
        if out is None:
            out = np.zeros((len(texts), e.shape[1]), dtype=np.float32)
        out[idx] = e
    return out


def main():
    DEST.mkdir(parents=True, exist_ok=True); PDEST.mkdir(parents=True, exist_ok=True)
    check = {}
    # ---------------- statements: srow, flags, gte, style ----------------
    S = pl.read_parquet(G / "statements.parquet").with_row_index("row")
    sh = pl.read_parquet(EM.ED / "statements.parquet").with_row_index("srow").select("kind", "src_row", "srow")
    S2 = S.join(sh, on=["kind", "src_row"], how="left", maintain_order="left")
    assert S2["srow"].null_count() == 0 and S2.height == S.height
    srow = S2["srow"].to_numpy().astype(np.int64)
    fl = pl.read_parquet(EM.OUT / "statement_flags.parquet",
                         columns=["srow", "self_repeat_bge", "self_repeat_gte", "self_repeat_both", "cross_echo_bge",
                                  "cross_echo_gte", "cross_echo_both"]).sort("srow")
    f = fl[srow].drop("srow")
    pl.DataFrame({"row": S["row"], "srow": srow.astype(np.uint32)}).hstack(f).write_parquet(DEST / "stmt.parquet")
    check["n_statements"] = S.height
    check["flag_rates"] = {c: float(f[c].mean()) for c in f.columns}
    E = EM.statement_embeddings("gte_modernbert")
    Wg = EM.load_whitener("I", 64, "gte_modernbert")
    np.save(DEST / "stmt_w64_gte_modernbert.npy", Wg(E[srow]).astype(np.float16))
    del E
    X0 = np.load(G / "stmt_w64.npy").astype(np.float64)[:, :32]
    w32 = np.load(EM.ED / "statements_white32_bge_small.npy", mmap_mode="r")
    check["bge_white32_cos_min"] = float((unit(X0) * unit(np.asarray(w32[srow], np.float64))).sum(1).min())
    for m in MODELS:
        A = np.load(EM.ED / f"statements_style_resid_period32_{EM.MODELS[m]['suffix']}.npy", mmap_mode="r")
        np.save(DEST / f"stmt_sr32_{m}.npy", np.asarray(A[srow], dtype=np.float16))

    # ---------------- documents: same chunks as round 1, embedded with gte ----------------
    D = pl.read_parquet(G / "docs.parquet")
    present = sorted(pl.read_parquet(G / "switch_on.parquet")["agent"].to_list())
    cu = pl.read_parquet(G / "cu_turns_text.parquet").filter(pl.col("agent").is_in(present))
    rows, dtexts = [], []
    for x in cu.sort("t").iter_rows(named=True):
        c = doc_content(x)
        if not c:
            continue
        for k, ch in enumerate(chunk_text(c)):
            rows.append((x["agent"], x["t"], k, len(ch))); dtexts.append(ch)
    ok = (len(rows) == D.height and [r[0] for r in rows] == D["agent"].to_list() and [r[2] for r in rows] == D["part"].to_list()
          and [r[3] for r in rows] == D["n_chars"].to_list())
    check["docs_rechunk_matches_round1"] = bool(ok)
    assert ok, "document chunks differ from round 1"

    # ---------------- goal fields (#21 and the N2 placebo weeks), chunk level ----------------
    held = set(load_holdout()["goal_periods_held_out"])
    weeks = pl.read_parquet(H24 / "placebo/placebo_weeks.parquet")
    want = [21] + weeks["goal_no"].to_list()
    meta, texts = GF.goal_texts()
    sel = {}
    for mrow, tx in zip(meta, texts):
        if mrow["goal_no"] in want and mrow["kind"] in ("goal", "kickoff") and not mrow["holdout"]:
            assert mrow["goal_no"] not in held
            sel.setdefault(mrow["goal_no"], {})[mrow["kind"]] = tx
    del texts
    gm = pl.read_parquet(EM.ED / "goals.parquet").with_columns(pl.col("kind").cast(pl.String))

    for model in MODELS:
        mdl = st_model(model)
        W = EM.load_whitener("I", 64, model)
        V = EM.goal_vectors(model).astype(np.float32)
        if model == "gte_modernbert":
            Ed = encode(mdl, dtexts)
            np.save(DEST / "docs_w64_gte_modernbert.npy", W(Ed).astype(np.float16))
        out = {}
        for gno in want:
            rec = sel.get(gno, {})
            ch_vecs = []
            for kind in ("goal", "kickoff"):
                if rec.get(kind):
                    e = encode(mdl, rec[kind])
                    ch_vecs.append(unit(W(e)))
            q = gm.filter((pl.col("goal_no") == gno) & (pl.col("kind") == "goal"))
            gv = unit(W(V[q["gid"][0]][None])[0])
            q = gm.filter((pl.col("goal_no") == gno) & (pl.col("kind") == "kickoff"))
            kv = unit(W(V[q["gid"][0]][None])[0]) if q.height else None
            gh = unit(gv + kv) if kv is not None else gv
            out[gno] = dict(ghat=gh.astype(np.float32), goal=gv.astype(np.float32),
                            kickoff=(kv if kv is not None else np.full_like(gv, np.nan)).astype(np.float32),
                            chunks=np.vstack(ch_vecs).astype(np.float32) if ch_vecs else np.zeros((0, 64), np.float32))
        o = out[21]
        np.savez(DEST / f"field_{model}.npz", **o)
        ws = [g for g in weeks["goal_no"].to_list() if g in out]
        np.savez(PDEST / f"field_{model}.npz", goal_no=np.array(ws), ghat=np.array([out[g]["ghat"] for g in ws]),
                 n_chunks=np.array([len(out[g]["chunks"]) for g in ws]),
                 chunks=np.vstack([out[g]["chunks"] for g in ws]))
        check[f"n_field_chunks_21_{model}"] = int(len(o["chunks"]))
        if model == "bge_small":
            old = np.load(G / "goal_vec.npz")
            for k in ("ghat", "goal", "kickoff"):
                check[f"cos_h24_vs_shared_{k}_n32"] = float(unit(old[k][:32].astype(np.float64)) @ unit(o[k][:32].astype(np.float64)))
            pg = np.load(H24 / "placebo/placebo_ghat.npy")
            pw = weeks["goal_no"].to_list()
            check["placebo_ghat_cos_n32"] = {int(g): round(float(unit(pg[i][:32].astype(np.float64)) @ unit(out[g]["ghat"][:32].astype(np.float64))), 4)
                                             for i, g in enumerate(pw) if g in out}
        del mdl
    (DEST / "check.json").write_text(json.dumps(check, indent=1))
    prov_p = H24 / "_provenance.json"
    prov = json.loads(prov_p.read_text())
    prov["r1b"] = {"built_by": "hypotheses/H24-forecast-coupling-switch/scheme/build_r1b.py", "git_commit": git_commit(),
                   "inputs": [{"source": "ai-village", "revision": REVISION,
                               "tables": ["shared/embeddings/statements", "shared/embeddings/*_gte_modernbert.npy",
                                          "shared/embeddings/whitening_gte_modernbert_I", "shared/statement_flags",
                                          "shared/embeddings/goals + goal_vectors*", "shared/chat_text (goal/kickoff chunks, memory only)",
                                          "G21/cu_turns_text (document chunks, memory only)"]}],
                   "params": {"models": list(MODELS), "dim": 64, "max_seq_length": 256},
                   "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    prov_p.write_text(json.dumps(prov, indent=1))
    print(json.dumps(check, indent=1))


if __name__ == "__main__":
    main()
