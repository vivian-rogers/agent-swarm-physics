"""POST HOC (after seeing the flat response curves of explore.py's leadership section): how fast does each room
switch? Per goal change and cohort: latency of each agent's first post-kickoff statement (minutes) and the shift
fraction y of that statement (same pre/post/u as the lead index). Descriptive only; no verdict depends on it.

Usage: uv run python hypotheses/H47-room-coherence-length/analysis/posthoc_first_statement.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h47lib as L  # noqa: E402
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("h47explore", HERE / "explore.py")   # not H26's explore.py on sys.path
E = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(E)

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402


def main():
    Dt = E.Data()
    sh = pl.read_parquet(L.SH / "embeddings/statements.parquet", columns=["kind", "src_row"]).with_row_index("st_row")
    st = Dt.st.join(sh, on="st_row", how="left").filter(~pl.col("dup"))
    chat_raw = np.load(L.SH / "embeddings/chat_bge_small.npy", mmap_mode="r")
    int_raw = np.load(L.SH / "embeddings/intentions_bge_small.npy", mmap_mode="r")
    kk = pl.read_parquet(L.OUT / "kickoffs.parquet")
    kick = {(g, r): t for g, r, t in kk.iter_rows()}
    lead = L.json.loads((E.RES / "leadership.json").read_text())

    def vec(row):
        arr = chat_raw if row["kind"] == "chat" else int_raw
        return np.asarray(arr[int(row["src_row"])], np.float32)
    out = {}
    for key, ev in lead.items():
        if not key.startswith("#"):
            continue
        g = int(key[1:])
        d0, pre, post = ev["day0"], ev["pre"], ev["post"]
        ref = st.filter(pl.col("pt_date") == (pre if g == 40 else d0))
        cm = dict(ref.group_by("agent").agg(pl.col("room").mode().sort().first()).iter_rows())
        coh = {int(a): (0 if r == 2 else 1) for a, r in cm.items() if r in (2, 3)}
        kt = {0: kick.get((41, 4)), 1: kick.get((41, 4))} if g == 41 else {0: kick.get((g, 2)), 1: kick.get((g, 3))}
        res = {}
        for c in (0, 1):
            ags = [a for a, v in coh.items() if v == c]
            sp = st.filter((pl.col("pt_date") == pre) & pl.col("agent").is_in(ags))
            so = st.filter(pl.col("pt_date").is_in(post) & pl.col("agent").is_in(ags))
            Xp = np.array([vec(r) for r in sp.iter_rows(named=True)]); Xo = np.array([vec(r) for r in so.iter_rows(named=True)])
            pre_m, post_m = Xp.mean(0), Xo.mean(0)
            dl = post_m - pre_m
            lat, yf = [], []
            for a in ags:
                s0 = st.filter((pl.col("pt_date") == d0) & (pl.col("agent") == a) & (pl.col("t") >= kt[c])).sort("t")
                if s0.height == 0:
                    continue
                r0 = s0.row(0, named=True)
                lat.append((r0["t"] - kt[c]).total_seconds() / 60)
                yf.append(float((vec(r0) - pre_m) @ dl / (dl @ dl)))
            res["best" if c == 0 else "rest"] = dict(n=len(lat), latency_med_min=float(np.median(lat)) if lat else None,
                                                    y_first_med=float(np.median(yf)) if yf else None)
        out[key] = res
        print(key, res, flush=True)
    L.jdump(out, E.RES / "posthoc_first_statement.json")


if __name__ == "__main__":
    main()
