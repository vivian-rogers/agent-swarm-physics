"""H01 robustness instrument: a LEXICAL representation of the same statements, standing in for the embedding-model
swap (no second sentence-embedding model is cached locally and the network is off).

Hashed TF-IDF over lowercase word unigrams (2^18 buckets, sublinear tf, smooth idf, L2) -> truncated SVD to 128
dims (fitted on all non-holdout statements) -> the same per-regime centering + PCA whitening (d = 64 stored) and
k-means (k = 40 at d = 32) as scheme/build.py. Goal texts and kickoffs are mapped through the same transform.
Writes a parallel scheme folder data/processed/H01-emergent-superagents-exist/lexical/ that analysis/h01data.Scheme
can load with base=.../lexical (statements, units, exposure and agent-day tables are copied unchanged).

Usage: uv run python hypotheses/H01-emergent-superagents-exist/scheme/build_lexical.py
"""
from __future__ import annotations

import re
import shutil
import sys
import time
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h01common import OUT, SH, SEED, guard_holdout, kmeans, unit, whiten_apply, write_provenance  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import sparse  # noqa: E402
from scipy.sparse.linalg import svds  # noqa: E402

LEX = OUT / "lexical"
NB = 2 ** 18
TOK = re.compile(r"[a-z][a-z0-9']+")


def hash_rows(texts):
    indptr, idx, val = [0], [], []
    for s in texts:
        toks = TOK.findall((s or "").lower()[:4000])
        if toks:
            h = np.fromiter((zlib.crc32(t.encode()) % NB for t in toks), dtype=np.int64, count=len(toks))
            u, c = np.unique(h, return_counts=True)
            idx.append(u); val.append(1 + np.log(c))
            indptr.append(indptr[-1] + len(u))
        else:
            indptr.append(indptr[-1])
    idx = np.concatenate(idx) if idx else np.array([], np.int64)
    val = np.concatenate(val) if val else np.array([], float)
    return sparse.csr_matrix((val, idx, np.array(indptr)), shape=(len(texts), NB))


def main():
    t0 = time.time()
    LEX.mkdir(parents=True, exist_ok=True)
    st = pl.read_parquet(OUT / "statements.parquet")
    guard_holdout(sorted(st["pt_date"].unique().to_list()))
    ct = pl.read_parquet(SH / "chat_text.parquet", columns=["message_id", "text"])
    it = pl.read_parquet(SH / "intentions_text.parquet", columns=["event_index", "goal_text"]).rename({"goal_text": "text"})
    a = st.with_row_index("r").filter(pl.col("kind") == 0).join(ct, on="message_id", how="left").select("r", "text")
    b = st.with_row_index("r").filter(pl.col("kind") == 1).join(it, on="event_index", how="left").select("r", "text")
    txt = pl.concat([a, b]).sort("r")["text"].to_list()
    assert len(txt) == st.height
    X = hash_rows(txt)
    df = np.asarray((X > 0).sum(0)).ravel()
    idf = np.log((1 + X.shape[0]) / (1 + df)) + 1
    X = X @ sparse.diags(idf)
    nrm = np.sqrt(np.asarray(X.multiply(X).sum(1)).ravel()); nrm[nrm == 0] = 1
    X = sparse.diags(1 / nrm) @ X
    print("tfidf", X.shape, X.nnz, f"{time.time()-t0:.0f}s", flush=True)
    U_, S_, Vt = svds(X.astype(np.float32), k=128, random_state=SEED)
    o = np.argsort(S_)[::-1]; Vt = Vt[o]
    Y = (X @ Vt.T).astype(np.float32)                     # (n, 128)
    print("svd", f"{time.time()-t0:.0f}s", flush=True)
    Z64 = np.zeros((st.height, 64), np.float32)
    lab = np.full(st.height, -1, np.int16)
    reg = st["regime"].to_numpy(); bases = {}
    for R in ("I", "II", "III"):
        m = reg == R
        mu = Y[m].mean(0); C = np.cov((Y[m] - mu).T)
        w, V = np.linalg.eigh(C); oo = np.argsort(w)[::-1][:64]
        b_ = {"mean": mu, "components": V[:, oo].T.astype(np.float32), "eigvals": w[oo].astype(np.float32)}
        Z = whiten_apply(Y[m], b_, 64); Z64[m] = Z
        Cc, lb, _ = kmeans(unit(Z[:, :32]).astype(np.float32), 40, seed=SEED + 40)
        lab[m] = lb
        np.savez(LEX / f"basis_{R}.npz", **b_, centroids_k40_d32=Cc)
        bases[R] = b_
        print("regime", R, f"{time.time()-t0:.0f}s", flush=True)
    np.save(LEX / "vectors_w64.npy", Z64.astype(np.float16))
    pl.DataFrame({"k20": lab, "k40": lab, "k80": lab, "k40_d16": lab, "k40_d64": lab}).write_parquet(LEX / "clusters.parquet")
    for f in ("statements.parquet", "agent_day.parquet", "units.json", "pair_day_exposure.parquet", "goals.parquet"):
        shutil.copy(OUT / f, LEX / f)
    # goal vectors through the same lexical transform ("raw" = 128-d SVD space; the loader whitens per regime)
    from build import goal_texts  # noqa: E402
    from h01common import nonholdout_days  # noqa: E402
    meta, texts = goal_texts(st, nonholdout_days())
    G = np.zeros((len(texts), 128), np.float32)
    for i, ch in enumerate(texts):
        Xg = hash_rows(ch) @ sparse.diags(idf)
        n_ = np.sqrt(np.asarray(Xg.multiply(Xg).sum(1)).ravel()); n_[n_ == 0] = 1
        G[i] = np.asarray((sparse.diags(1 / n_) @ Xg) @ Vt.T).mean(0)
    np.save(LEX / "goals_raw.npy", G)
    write_provenance("lexical", "hypotheses/H01-emergent-superagents-exist/scheme/build_lexical.py",
                     ["shared/chat_text", "shared/intentions_text", "H01 statements"],
                     {"representation": "hashed tf-idf unigrams 2^18 -> svds 128 -> per-regime PCA whitening 64", "kmeans": "k40 d32",
                      "note": "k20/k80/d16/d64 label columns are copies of k40 (lexical robustness covers k40/d32 only)"})
    print("done", f"{time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
