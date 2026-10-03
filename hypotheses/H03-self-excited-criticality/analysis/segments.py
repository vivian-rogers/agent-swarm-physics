"""Amendment 2026-10-03 (project rule: the goal period is the unit of analysis, split at every step change inside it).

Segments = maximal runs of a goal period's non-holdout days between step-change dates. A change dated D starts a new
segment at day D. Step changes:
  - every dated entry in hypotheses/natural-experiments.md (scaffold, roster, operator tables; ranges give both ends);
  - roster joined / left dates (data/processed/shared/roster.parquet);
  - "Scaffold changes inside" dates in hypotheses/hypohypotheses/goal-periods.md.
Per segment: M1_B2 (+ profile CI, + day-level bootstrap B if >= 3 days), P_B2 (LR), M3_sc (fast self/cross).

Output: data/processed/H03-self-excited-criticality/segments.parquet, segments_boot.parquet, step_changes.parquet
Run: uv run python hypotheses/H03-self-excited-criticality/analysis/segments.py [B] [workers]
"""
from __future__ import annotations

import re
import sys
import time
from multiprocessing import Pool

import numpy as np
import polars as pl

from common import DATA, ROOT, fit_model, hc, load, select_goals, specs, write_output, write_provenance

G = {}


def step_changes() -> pl.DataFrame:
    rows = []
    txt = (ROOT / "hypotheses/natural-experiments.md").read_text()
    for line in txt.splitlines():
        m = re.match(r"^\| (NE\d+) \| ([^|]+) \| ([^|]+) \|", line)
        if not m:
            continue
        ne, dfield, change = m.group(1), m.group(2), m.group(3).strip()
        full = re.findall(r"(\d{4})-(\d{2})-(\d{2})", dfield)
        if not full:
            continue
        y = full[0][0]
        dates = {f"{a}-{b}-{c}" for a, b, c in full}
        rest = re.sub(r"\d{4}-\d{2}-\d{2}", "", dfield)
        for mm, dd in re.findall(r"(\d{2})-(\d{2})", rest):            # "→ 03-24", "/ 06-15"
            dates.add(f"{y}-{mm}-{dd}")
        base_m = full[0][1]
        for dd in re.findall(r"/(\d{2})(?!-)", rest):                    # "2025-11-20/25"
            dates.add(f"{y}-{base_m}-{dd}")
        for d in dates:
            rows.append({"date": d, "source": ne, "what": change[:80]})
    ros = pl.read_parquet(ROOT / "data/processed/shared/roster.parquet")
    for r in ros.iter_rows(named=True):
        for k in ("joined", "left"):
            if r[k]:
                rows.append({"date": r[k], "source": f"roster_{k}", "what": r["name"]})
    gp = (ROOT / "hypotheses/hypohypotheses/goal-periods.md").read_text()
    for line in gp.splitlines():
        if line.startswith("- **Scaffold changes inside:**"):
            for d in re.findall(r"\((\d{4}-\d{2}-\d{2})\)", line):
                rows.append({"date": d, "source": "goal-periods scaffold", "what": line[30:110]})
    return pl.DataFrame(rows).unique().sort("date")


def segment_days(days: pl.DataFrame, sc: pl.DataFrame) -> pl.DataFrame:
    """Assign seg index within each goal period: a step date strictly after the period's first day splits it."""
    out = []
    cdates = sorted(set(sc["date"].to_list()))
    for g, sub in days.sort("pt_date").group_by("goal_no", maintain_order=True):
        sub = sub.sort("pt_date")
        d0 = sub["pt_date"][0]
        seg, segs, prev = 0, [], d0
        for d in sub["pt_date"].to_list():
            if d != d0 and any(prev < c <= d for c in cdates):
                seg += 1
            segs.append(seg); prev = d
        out.append(sub.with_columns(seg=pl.Series(segs, dtype=pl.Int32)))
    return pl.concat(out)


def _init():
    days, ev, exo = load()
    G["days"] = days
    G["dm"] = {s: hc.make_days(ev, exo, days, s) for s in ("TALK", "ALL")}


def run_seg(task):
    goal, seg, keys, eset, B = task
    t0 = time.time()
    days, dm = G["days"], G["dm"][eset]
    sub = days.filter(pl.col("day_id").is_in(keys))
    meta = {"goal_no": goal, "seg": seg, "set": eset, "first_date": sub["pt_date"].min(),
            "last_date": sub["pt_date"].max(), "n_days": len(keys), "mode": sub["mode"][0],
            "regime": "/".join(sorted(set(sub["regime"].to_list()))),
            "N_active": float(sub["n_active"].mean()), "hours": float(sub["T_s"].median() / 3600)}
    sp = specs()
    rows, boots = [], []
    fits = {}
    for m in ("M1_B2", "P_B2", "M3_sc"):
        ds = hc.Dataset(dm, keys, sp[m])
        if ds.n < 20:
            return rows, boots
        f = fit_model(m, ds)
        fits[m] = f
        s = f.summary(); s.update(meta); s["model"] = m
        if m == "M1_B2":
            s["n_prof_lo"], s["n_prof_hi"] = hc.profile_ci_n(f)
        rows.append(s)
    if B and len(keys) >= 3:
        rng = np.random.default_rng(goal * 100 + seg * 7 + (eset == "ALL"))
        for b in range(B):
            bk = list(rng.choice(keys, len(keys), replace=True))
            ds = hc.Dataset(dm, bk, sp["M1_B2"])
            p0, _ = hc.transfer_params(fits["M1_B2"], ds)
            f = fit_model("M1_B2", ds, p0=p0, beta_starts=[1 / 10, 1 / 1000])
            boots.append({**meta, "rep": b, "n": f.summary()["n"]})
    print(f"seg {goal}.{seg} {eset} ({len(keys)} d): {time.time() - t0:.0f}s", flush=True)
    return rows, boots


def main():
    B = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    W = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    days, _, _ = load()
    sc = step_changes()
    sc.write_parquet(DATA / "step_changes.parquet")
    sd = segment_days(days, sc)
    sd.select("day_id", "pt_date", "goal_no", "seg").write_parquet(DATA / "segment_days.parquet")
    tasks = []
    keep = set(select_goals(sorted(sd["goal_no"].unique().to_list())))
    for (g, seg), sub in sd.filter(pl.col("goal_no").is_in(list(keep))).group_by("goal_no", "seg"):
        keys = sub.sort("day_id")["day_id"].to_list()
        for eset in ("ALL", "TALK"):
            tasks.append((g, seg, keys, eset, B))
    tasks.sort(key=lambda t: -len(t[2]))
    with Pool(W, initializer=_init) as pool:
        out = pool.map(run_seg, tasks, chunksize=1)
    write_output(pl.DataFrame([r for o in out for r in o[0]], infer_schema_length=None), "segments.parquet")
    write_output(pl.DataFrame([r for o in out for r in o[1]]), "segments_boot.parquet")
    write_provenance({"segments.parquet": {"built_by": "analysis/segments.py", "B": B,
                                           "rule": "goal period split at every dated step change (NE table, roster "
                                                   "join/leave, goal-periods scaffold dates); change on D starts a "
                                                   "segment at D"}})


if __name__ == "__main__":
    main()
