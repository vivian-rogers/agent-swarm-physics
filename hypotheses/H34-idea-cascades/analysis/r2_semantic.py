"""H34 round 2, R4: statistics of semantic-idea cascades (built by scheme/build_semantic.py build), per period, with the
round-1b estimators (explore.class_stats: R, k, tails, HR10, H57 seen/unread placebo, room contrast).

  uv run python hypotheses/H34-idea-cascades/analysis/r2_semantic.py sem_bge_small [sem_gte_modernbert ...]
Outputs: data/processed/H34-idea-cascades/r2/<tag>/results/period_table.parquet and r2/semantic/summary_r4.json
"""
from __future__ import annotations

import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import explore as X  # noqa: E402
import h34core as C  # noqa: E402

R2 = C.OUT / "r2"


def task(t):
    tag, g = t
    t0 = time.time()
    od = R2 / tag / f"G{g:02d}"
    meta = json.loads((od / "meta.json").read_text())
    rd = {k: pl.read_parquet(od / f"{k}.parquet") for k in ("first_uses", "trees", "atrisk", "jitter", "roomx")}
    N = int(meta["N_room"])
    st = X.class_stats(rd["first_uses"], rd["trees"], rd["atrisk"], rd["jitter"], rd["roomx"], N, "S", seed=g, full=True)
    st.update(goal=g, tag=tag, N_room=N, n_days=meta["n_days"], n_agents=meta["n_agents"])
    for k, v in list(st.items()):
        if isinstance(v, list):
            st[k] = json.dumps(v)
    print(f"G{g:02d} [{tag}] R {st.get('R', np.nan):.3f} HR10 {st.get('hr10', np.nan):.1f} {time.time() - t0:.0f}s", flush=True)
    return st


def run(tags: list[str]):
    rows = []
    for tag in tags:
        periods = sorted(int(p.name[1:]) for p in (R2 / tag).glob("G*") if (p / "meta.json").exists())
        order = sorted(periods, key=lambda x: -1 if x == 51 else x)
        with Pool(2) as pool:
            out = pool.map(task, [(tag, g) for g in order], chunksize=1)
        pt = pl.DataFrame(out, infer_schema_length=None).sort("goal")
        (R2 / tag / "results").mkdir(parents=True, exist_ok=True)
        pt.write_parquet(R2 / tag / "results" / "period_table.parquet")
        rows.append(pt)
    summarize(tags)


def sp(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    m = np.isfinite(a) & np.isfinite(b)
    r = stats.spearmanr(a[m], b[m])
    return dict(rho=float(r.statistic), p=float(r.pvalue), n=int(m.sum()))


def summarize(tags: list[str]):
    mk = pl.read_parquet(C.OUT / "r1b" / "results" / "period_table.parquet").filter(pl.col("cls") == "ALL").select(
        "goal", pl.col("R").alias("R_marker"), pl.col("hr_unread5").alias("hu_m"), pl.col("hr_seen5").alias("hs_m"))
    summ = {}
    tabs = {}
    for tag in tags:
        p = R2 / tag / "results" / "period_table.parquet"
        if not p.exists():
            continue
        pt = pl.read_parquet(p).join(mk, on="goal", how="left")
        tabs[tag] = pt
        ratio = (pt["hr_unread5"] / pt["hr_seen5"]).to_numpy()
        d = dict(n=pt.height, R_median=float(pt["R"].median()), R_range=[float(pt["R"].min()), float(pt["R"].max())],
                 P1_R_hi_lt1=[int((pt["R_hi"] < 1).sum()), pt.height], R_lo_ge1=int((pt["R_lo"] >= 1).sum()),
                 P2_vs_marker=sp(pt["R"], pt["R_marker"]),
                 R_sem_over_marker_median=float(np.nanmedian((pt["R"] / pt["R_marker"]).to_numpy())),
                 P4_hr10_lo_gt1=[int((pt["hr10_lo"] > 1).sum()), pt.height],
                 P4_seen_gt_unread=[int((pt["hr_seen5"] > pt["hr_unread5"]).sum()), pt.height],
                 P5_unread_over_seen_median=float(np.nanmedian(ratio)),
                 unread_over_seen_marker_median=float(np.nanmedian((pt["hu_m"] / pt["hs_m"]).to_numpy())),
                 Rc_median=float(pt["R_c"].median()), hr10_median=float(pt["hr10"].median()),
                 ideas_median=float(pt["ideas"].median()), nodes_total=int(pt["nodes"].sum()), trees_total=int(pt["trees"].sum()),
                 p2_median=float(pt["p2"].median()), p5_median=float(pt["p5"].median()),
                 fn_cover_both=[int(pt["shape_pass"].fill_null(False).sum()), int(pt["shape_pass"].is_not_null().sum())],
                 root_field_median=float(pt["root_field"].median()))
        summ[tag] = d
    if "sem_bge_small" in tabs and "sem_gte_modernbert" in tabs:
        a = tabs["sem_bge_small"].select("goal", pl.col("R").alias("Rb")).join(
            tabs["sem_gte_modernbert"].select("goal", pl.col("R").alias("Rg")), on="goal")
        summ["P3_models"] = dict(spearman=sp(a["Rb"], a["Rg"]), ratio_median=float((a["Rg"] / a["Rb"]).median()))
    (R2 / "semantic").mkdir(parents=True, exist_ok=True)
    (R2 / "semantic" / "summary_r4.json").write_text(json.dumps(summ, indent=1, default=float))
    print(json.dumps(summ, indent=1, default=float))


if __name__ == "__main__":
    if sys.argv[1] == "summary":
        summarize(sys.argv[2:])
    else:
        run(sys.argv[1:])
