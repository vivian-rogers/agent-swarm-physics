"""H48 read-out predictors per goal period (and per kickoff-room block): coverage times, read-out chain mixing times,
time-respecting DeGroot, reading rates, lambda_2 variants, room structure. Uses no content (no outcome).

  uv run python hypotheses/H48-settling-mixing-time/analysis/readout.py [--periods 38,39] [--workers 2]

Writes data/processed/H48-settling-mixing-time/:
  readout_period.parquet   one row per period (card observables (a)-(e) + rivals)
  readout_block.parquet    one row per (period, kickoff-room block)
  G<NN>/coverage_curves.parquet   coverage C(t) on a log grid for the figures
"""
from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h48lib as L  # noqa: E402
from h48lib import hc  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

GRID = np.r_[0.0, np.geomspace(0.01, 1000.0, 121)]


def unit_predictors(P: dict, agents: list[int], blocks: dict, a2: float, a_max: float, seed: int = 0,
                    with_dg: bool = True) -> tuple[dict, dict]:
    calls, reads = P["calls"], P["reads"]
    N = len(agents)
    out: dict = {"N": N, "n_blocks": len(blocks), "a2": a2}
    if N < 3:
        return out, {}
    allm = ~np.eye(N, dtype=bool)
    roomm = L.same_block_mask(agents, blocks)
    out["share_same"] = float(roomm.sum() / max(allm.sum(), 1))
    T1 = L.pair_cover_times(reads, agents, 1)
    T5 = L.pair_cover_times(reads, agents, 5)
    R = L.reach_times(reads, agents)
    Rt = R.T.copy()                              # Rt[i, j] = time info from j reached i (reader rows)
    np.fill_diagonal(Rt, np.nan)
    curves = {}
    for name, T in (("k1", T1), ("k5", T5), ("tr", Rt)):
        for pname, m in (("room", roomm), ("all", allm)):
            s = L.coverage_stats(T, m)
            for k, v in s.items():
                out[f"{name}_{pname}_{k}"] = v
            curves[f"{name}_{pname}"] = L.coverage_curve(T, m, GRID)
    # rates in the early window
    wr = L.window_rates(calls, reads, agents, a2)
    out.update(call_rate=float(np.median(wr["call_rate"])), u=float(np.median(wr["u"])),
               read_rate=float(np.median(wr["read_rate"])), ici_h=float(np.nanmedian(wr["ici_h"])),
               u_min=float(np.min(wr["u"])), u_mean=float(np.mean(wr["u"])))
    for key in ("k1_room_T90", "k1_room_T50", "tr_room_T90"):
        out[key + "_cyc"] = out[key] / out["ici_h"] if out["ici_h"] > 0 else np.nan
        out[key + "_rcyc"] = out[key] * out["u"]
    # read-out chains per block
    W = L.read_graph(reads, agents, a2)
    pos = {a: n for n, a in enumerate(agents)}
    tb_b, tb_c, l2s, l2d, l2rw, ul2rw, rel_b, sizes = [], [], [], [], [], [], [], []
    for b, ags in blocks.items():
        ix = [pos[a] for a in ags if a in pos]
        if len(ix) < 3:
            continue
        Wb = W[np.ix_(ix, ix)]
        ub = wr["u"][ix]
        Qb = L.generator(Wb, "batch", ub)
        Qc = L.generator(Wb, "count")
        tb_b.append(L.mixing_times(Qb))
        tb_c.append(L.mixing_times(Qc))
        rel_b.append(L.relaxation_rate(Qb))
        H = L.h31lib()
        l2s.append(H.lam2_sym(Wb))
        l2d.append(H.lam2_dir(Wb))
        l2rw.append(H.lam2_rw(Wb))
        ul2rw.append(float(np.median(ub)) * H.lam2_rw(Wb))
        sizes.append(len(ix))
    if tb_b:
        ab, ac = np.concatenate(tb_b), np.concatenate(tb_c)
        out.update(tmix_batch_bulk=float(np.median(ab)), tmix_batch_worst=float(np.max(ab)),
                   tmix_count_bulk=float(np.median(ac)), tmix_count_worst=float(np.max(ac)),
                   relax_batch_min=float(np.min(rel_b)),
                   l2_sym_min=float(np.min(l2s)), l2_dir_min=float(np.min(l2d)), l2_rw_min=float(np.min(l2rw)),
                   ul2_rw_min=float(np.min(ul2rw)),
                   l2_sym_wmean=float(np.average(l2s, weights=sizes)),
                   l2_sym_whole=float(L.h31lib().lam2_sym(W)))
    if with_dg:
        for alpha, tag in ((0.1, "dg"), (0.03, "dg03"), (0.3, "dg30"), (0.5, "dg50")):
            dg = L.degroot_tr(calls, reads, agents, blocks, alpha=alpha, seed=seed, a_max=a_max)
            out[f"{tag}_bulk"], out[f"{tag}_worst"], out[f"{tag}_gamma"] = dg["bulk"], dg["worst"], dg["gamma"]
    return out, curves


def period_job(g: int) -> tuple[list, list, int]:
    t0 = time.time()
    P = L.load_period(g)
    ro = P["roster"].filter(pl.col("on_day1"))
    agents = sorted(int(a) for a in ro["agent"].to_list())
    blocks = L.blocks_of(P["roster"])
    de = L.day_ends(g)
    a2 = float(de[min(1, len(de) - 1)])
    a_max = float(de[min(hc.MAX_FIT_DAYS, len(de)) - 1])
    meta = P["meta"]
    row, curves = unit_predictors(P, agents, blocks, a2, a_max, seed=g)
    row.update(goal_no=g, regime=meta["regime"], n_days=meta["n_days"], T_h=meta["T_h"],
               hours_per_day=meta["hours_per_day"], t0_src=meta["t0_src"], n_rooms=len(blocks),
               rooms=",".join(str(b) for b in blocks))
    # H31's published predictors (read-only), weakest link over blocks, 'all' variant
    try:
        h31 = pl.read_parquet(hc.H31 / "predictors_period.parquet").filter((pl.col("goal_no") == g)
                                                                            & (pl.col("variant") == "all"))
        if h31.height:
            row["h31_l2_sym_min"] = float(h31["l2_sym"].min())
            row["h31_g_tr_min"] = float(h31["g_tr"].min())
            row["h31_ul2_rw_min"] = float(h31["ul2_rw"].min())
    except Exception:
        pass
    brows = []
    for b, ags in blocks.items():
        r, _ = unit_predictors(P, ags, {b: ags}, a2, a_max, seed=g * 10 + b, with_dg=True)
        r.update(goal_no=g, room=b)
        brows.append(r)
    out = hc.OUT / f"G{g:02d}"
    out.mkdir(parents=True, exist_ok=True)
    pl.DataFrame({"a": GRID, **{k: v for k, v in curves.items()}}).write_parquet(out / "coverage_curves.parquet")
    print(f"#{g}: N={row['N']} T90={row.get('k1_room_T90', np.nan):.3f}h tmix={row.get('tmix_batch_bulk', np.nan):.3f}h"
          f" dg={row.get('dg_bulk', np.nan):.2f}h ({time.time() - t0:.0f}s)", flush=True)
    return [row], brows, g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--periods", default=None)
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    periods = [int(x) for x in a.periods.split(",")] if a.periods else hc.ALL_PERIODS
    rows, brows = [], []
    order = sorted(periods, key=lambda g: -1 if g == 51 else g)       # start the long one first
    with ProcessPoolExecutor(max_workers=min(a.workers, 2)) as ex:
        for r, b, g in ex.map(period_job, order):
            rows += r
            brows += b
    df = pl.DataFrame(rows, infer_schema_length=None).sort("goal_no")
    bf = pl.DataFrame(brows, infer_schema_length=None).sort("goal_no", "room")
    if a.periods:
        old = hc.OUT / "readout_period.parquet"
        if old.exists():
            o = pl.read_parquet(old).filter(~pl.col("goal_no").is_in(periods))
            df = pl.concat([o, df], how="diagonal_relaxed").sort("goal_no")
        oldb = hc.OUT / "readout_block.parquet"
        if oldb.exists():
            o = pl.read_parquet(oldb).filter(~pl.col("goal_no").is_in(periods))
            bf = pl.concat([o, bf], how="diagonal_relaxed").sort("goal_no", "room")
    df.write_parquet(hc.OUT / "readout_period.parquet")
    bf.write_parquet(hc.OUT / "readout_block.parquet")
    pp = hc.OUT / "_provenance.json"
    prov = hc.load_json(pp)
    prov.setdefault("derived", {})["readout"] = {"built_by": "hypotheses/H48-settling-mixing-time/analysis/readout.py",
                                                 "git_commit": hc.common.git_commit(), "periods": sorted(periods)}
    hc.save_json(pp, prov)


if __name__ == "__main__":
    main()
