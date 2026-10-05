"""H36 round 2 (2026-10-05): content-only rebuild for the robustness pass on the frozen operator rule C3.

For one variant (embedding model x dedupe rule) this recomputes, on the round-1b day set (non-holdout days only):
  - the content statistics I_cont, chi_cont, C_cont (surrogate excess, h36lib.content_stats, own surrogate seed),
  - R1_shift and R3_polar on agent-day vectors (scheme/build.py add_rivals, unchanged),
  - R1_sr: R1 on the style-residualized agent-day vectors (agent_day_style_resid_<model>; style removed within regime,
    topic kept; STANDARDS section 1 row 3). Never deduped (the shared vectors use all statements).
The activity columns are copied from the round-1b build r1b/fixed_bge_restate (activity does not depend on the content
variant). Output: data/processed/H36-reorganization-alarm/r2/rob_<model>_<dedupe>/{day_stats,events,allevents}.parquet,
so that analysis/evaluate.py runs on it unchanged:  evaluate.py --r1b ../r2/rob_<model>_<dedupe>

Usage: uv run python hypotheses/H36-reorganization-alarm/analysis/r2_content.py --model bge_small --dedupe restate
       [--seed K]  (post hoc seed check, 2026-10-05: surrogate seed SEED_R2 + K; writes rob_<model>_<dedupe>_sK/)
"""
from __future__ import annotations

import argparse
import shutil
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h36lib as L  # noqa: E402
import build as B  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

SEED_R2 = 20261005
SRC = L.OUT / "r1b" / "fixed_bge_restate"
CONT_COLS = [c for s in L.CONT_STATS for c in (s, s + "_obs", s + "_sm", s + "_ss")] + ["n_cont", "W_cont"]


def cont_worker(p: dict) -> dict:
    rng = np.random.default_rng([p["seed"], int(p["aday"])])
    W = B.whitener(p["regime"], p["model"])
    V = W(p["V"].reshape(-1, p["V"].shape[-1])).reshape(p["V"].shape[0], p["V"].shape[1], 32)
    V = V / np.clip(np.linalg.norm(V, axis=2, keepdims=True), 1e-9, None)
    out = {"aday": p["aday"]}
    out.update(L.content_stats(V, p["M"], rng))
    return out


def r1_style_resid(st: pl.DataFrame, cal: pl.DataFrame, model: str) -> np.ndarray:
    """R1 on style-residualized 32-d agent-day vectors (plain means of unit vectors; normalized per agent-day here),
    centered on the non-holdout mean of the regime, NaN when the previous active day is held out."""
    ad = pl.read_parquet(B.EMB / "agent_day.parquet")
    av = np.load(B.EMB / f"agent_day_style_resid_{model}.npy").astype(np.float32)
    av = av / np.clip(np.linalg.norm(av, axis=1, keepdims=True), 1e-9, None)
    nh = ad.filter(~pl.col("holdout"))
    mu = {rg: av[g["gid"].to_numpy()].mean(0) for (rg,), g in nh.group_by(["regime"])}
    days = set(st["pt_date"].to_list())
    mbar = {}
    for (d, rg), g in nh.filter(pl.col("pt_date").is_in(list(days))).group_by(["pt_date", "regime"]):
        x = av[g["gid"].to_numpy()] - mu[rg]
        x /= np.clip(np.linalg.norm(x, axis=1, keepdims=True), 1e-9, None)
        mbar[d] = x.mean(0)
    prev = {r[0]: r for r in cal.select("aday", "pt_date", "holdout").iter_rows()}
    out = []
    for aday, d in st.select("aday", "pt_date").iter_rows():
        m = mbar.get(d); pv = prev.get(aday - 1)
        if m is None or pv is None or pv[2] or pv[1] not in mbar:
            out.append(np.nan); continue
        m0 = mbar[pv[1]]
        out.append(float(1 - m @ m0 / (np.linalg.norm(m) * np.linalg.norm(m0))))
    return np.array(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=["bge_small", "gte_modernbert"])
    ap.add_argument("--dedupe", required=True, choices=["none", "restate", "copies"])
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--seed", type=int, default=0, help="post hoc seed check: surrogate seed offset (0 = the round-2 seed)")
    a = ap.parse_args()
    global SEED_R2
    SEED_R2 = SEED_R2 + a.seed
    t0 = time.time()
    B.CFG.update(data_version="fixed", model=a.model, dedupe=a.dedupe, trim=False)
    tag = f"rob_{a.model.split('_')[0]}_{a.dedupe}" + (f"_s{a.seed}" if a.seed else "")
    OUTD = L.OUT / "r2" / tag
    OUTD.mkdir(parents=True, exist_ok=True)
    base = pl.read_parquet(SRC / "day_stats.parquet").sort("aday")
    assert not any(L.holdout_mask(base["pt_date"].to_list(), base["goal_no"].to_list()))
    cal = B.calendar()
    dl = base["pt_date"].to_list()
    aw, vec = B.window_vectors(dl)
    awd = {d: g for (d,), g in aw.group_by(["pt_date"])}
    pays = []
    for aday, d, rg in base.select("aday", "pt_date", "regime").iter_rows():
        w = awd.get(d)
        if w is None or w.height == 0:
            continue
        agents = sorted(set(w["agent"].to_list())); Wn = int(w["win30"].max()) + 1
        V = np.zeros((len(agents), Wn, vec.shape[1]), np.float32); M = np.zeros((len(agents), Wn), bool)
        ia = {x: i for i, x in enumerate(agents)}
        for ag, wi, gid in w.select("agent", "win30", "gid").iter_rows():
            V[ia[ag], wi] = vec[gid]; M[ia[ag], wi] = True
        pays.append({"aday": aday, "V": V, "M": M, "regime": rg, "model": a.model, "seed": SEED_R2})
    print(f"{tag}: {len(pays)} content days ({time.time() - t0:.0f}s)", flush=True)
    with ProcessPoolExecutor(max_workers=min(2, a.workers)) as ex:
        res = list(ex.map(cont_worker, pays, chunksize=4))
    cs = pl.DataFrame(res, infer_schema_length=None)
    keep = [c for c in base.columns if c not in CONT_COLS + ["R1_shift", "R3_polar"]]
    st = base.select(keep).join(cs, on="aday", how="left").sort("aday")
    for c in CONT_COLS:
        if c not in st.columns:
            st = st.with_columns(pl.lit(None, dtype=pl.Float64).alias(c))
    st = B.add_rivals(st, cal, dl, allow_holdout_prev=False)
    st = st.with_columns(pl.Series("R1_sr", r1_style_resid(st, cal, a.model)))
    assert not st["pt_date"].is_in(cal.filter(pl.col("holdout"))["pt_date"]).any()
    st.write_parquet(OUTD / "day_stats.parquet", compression="zstd")
    for f in ("events.parquet", "allevents.parquet"):
        shutil.copy(SRC / f, OUTD / f)
    L.write_provenance("hypotheses/H36-reorganization-alarm/analysis/r2_content.py",
                       ["embeddings/agent_win30, agent_day, statements, agent_day_style_resid", "statement_flags",
                        "(activity columns from r1b/fixed_bge_restate)"],
                       {"model": a.model, "dedupe": a.dedupe, "seed": SEED_R2, "n_surr": L.N_SURR, "days": st.height},
                       path=OUTD / "_provenance.json")
    print(f"{tag}: done, {st.height} days, {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
