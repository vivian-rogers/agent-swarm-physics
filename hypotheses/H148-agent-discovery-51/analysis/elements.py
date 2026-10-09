"""H148 element atoms from H145's frozen elements (run only after scratchpad/H145.READY exists).

Rules (fixed 2026-10-09 before any element data were read for H148; card Round 1, amendment A7):
  atoms    all 80 cluster elements (H145 k = 80, bge) + the 60 marker elements (coinages, rare words) with the most
           events, chosen without regard to H145's memeplexes (so the search stays autonomous). Repo elements are
           H148's artifact atoms already; project elements are skipped (the agent atoms carry projects).
  state    per bin: 0 no present agent expresses it, 1 one agent, 2 >= 2 agents (H145 expr panel, same bins).
  fields   (P5) role-text elements = the elements of H145's role patterns R0 (kickoff) and R1-R5 (role classes; 6
           nearest cluster elements each; memeplexes.json "role_patterns"); operator-topic elements = cluster elements
           whose centroid cosine to the mean automated operator message (H145 exo, src = automated) is in the top 10%
           of the 80 clusters. A discovered system is a role-text (operator-topic) system when >= half of its element
           atoms are role-text (operator-topic) elements.
  memeplex each element atom records the H145 memeplexes (K01-K15) that contain it (for P4's overlap report only).
Writes data/processed/H148-agent-discovery-51/elements_<w>.npz (S, K, names, meta).

Usage: uv run python hypotheses/H148-agent-discovery-51/analysis/elements.py --ready <path to H145.READY> [--width 30]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h148lib as L  # noqa: E402

H145 = L.ROOT / "data/processed/H145-ideology-egregores-51"
MAX_MARKERS = 60


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ready", required=True)
    ap.add_argument("--width", type=int, default=30)
    args = ap.parse_args()
    if not Path(args.ready).exists():
        raise SystemExit("H145.READY not present: element atoms wait for H145's frozen memeplexes")
    el = pl.read_parquet(H145 / "elements.parquet")
    MPJ = json.loads((H145 / "memeplexes.json").read_text())
    mps = {K["id"]: [int(e) for e in K["elements"]] for K in MPJ["memeplexes"]}
    roles = {R["id"]: [int(e) for e in R["elements"]] for R in MPJ["role_patterns"]}
    clusters = el.filter(pl.col("kind") == "cluster").sort("eid")
    markers = (el.filter(pl.col("kind") == "marker").sort(["n_events", "eid"], descending=[True, False])
               .head(MAX_MARKERS))
    use = pl.concat([clusters, markers])
    eids = use["eid"].to_list()
    # expression panel (H145 bins = H148 bins: same make_bins call; checked below)
    hb = pl.read_parquet(H145 / f"expr/bins_w{args.width}.parquet")
    mb = pl.read_parquet(L.OUT / f"bins_{args.width}.parquet")
    naive = lambda s: (s.dt.replace_time_zone(None) if getattr(s.dtype, "time_zone", None) else s).to_numpy()  # noqa
    t_h, t_m = naive(hb["t0"]), naive(mb["t0"])
    lut = {t: i for i, t in enumerate(t_m)}
    hmap = np.array([lut.get(t, -1) for t in t_h])
    assert (hmap >= 0).sum() == len(t_m), "H145 and H148 bins differ"
    ex = pl.read_parquet(H145 / f"expr/w{args.width}.parquet").filter(pl.col("eid").is_in(eids))
    pres = pl.read_parquet(H145 / f"expr/presence_w{args.width}.parquet")
    nB = mb.height
    col = {e: k for k, e in enumerate(eids)}
    b = hmap[ex["bin"].to_numpy()]
    ok = b >= 0
    ex = ex.with_columns(pl.Series("b", b)).filter(pl.Series(ok)).join(
        pres.with_columns(pl.Series("b", hmap[pres["bin"].to_numpy()])).select("agent_row", "b"),
        on=["agent_row", "b"], how="semi")
    cnt = ex.filter(pl.col("count") > 0).group_by("eid", "b").agg(pl.col("agent_row").n_unique().alias("n"))
    S = np.zeros((len(eids), nB), np.int8)
    for e, bb, n in cnt.iter_rows():
        S[col[e], bb] = 2 if n >= 2 else 1
    # field classification (clusters)
    C = np.load(H145 / "centroids_white32.npy")
    R = np.load(H145 / "roles_white32.npy")
    X = np.load(H145 / "exo_white32.npy")
    exo = pl.read_parquet(H145 / "exo.parquet")
    nz = lambda M: M / np.maximum(np.linalg.norm(M, axis=1, keepdims=True), 1e-12)  # noqa: E731
    Cn, Rn = nz(C), nz(R)
    op = nz(X[exo["src"].to_numpy() == "automated"].mean(0, keepdims=True))
    role_cos = (Cn @ Rn.T).max(1)
    op_cos = (Cn @ op.T)[:, 0]
    keys = use["key"].to_list()
    kidx = {f"c:{k}": k for k in range(C.shape[0])}
    oq = np.quantile(op_cos, 0.9)
    role_of = {e: [rid for rid, els in roles.items() if e in els] for e in eids}
    role_like = [bool(role_of[e]) for e in eids]
    oper_like = [bool(k in kidx and op_cos[kidx[k]] >= oq) for k in keys]
    in_mp = {e: [kid for kid, els in mps.items() if e in els] for e in eids}
    meta = {"eids": eids, "keys": keys, "kinds": use["kind"].to_list(), "role_like": role_like,
            "role_of": [role_of[e] for e in eids], "oper_like": oper_like, "memeplex_of": [in_mp[e] for e in eids],
            "role_cos_max": [float(role_cos[kidx[k]]) if k in kidx else None for k in keys],
            "h145_memeplexes_md5": "9b899c34009836b42774e010104f7dda"}
    np.savez_compressed(L.OUT / f"elements_{args.width}.npz", S=S, K=np.full(len(eids), 3), names=np.array(keys),
                        meta=json.dumps(meta))
    print(f"element atoms: {len(eids)} ({clusters.height} clusters, {markers.height} markers); role-text "
          f"{sum(role_like)}, operator-topic {sum(oper_like)}; in an H145 memeplex {sum(bool(v) for v in in_mp.values())}")


if __name__ == "__main__":
    main()
