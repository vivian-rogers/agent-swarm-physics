"""H04 round 1b native test NE43: forcing withdrawn inside #51 (bookends end after 2026-08-04 PT, nudges after 08-20).

  uv run python hypotheses/H04-reversible-forcing/analysis/r1b_native.py

Prediction (written before this run): goalperiod-subhypotheses/NE43/README.md. Windows (PT dates, non-holdout):
pre = 07-21 .. 08-04 (bookends and nudges on), on = 08-05 .. 08-20 (bookends gone, nudges on), off = 08-21 .. 09-04
(both gone). Statistics:
- Hawkes branching ratio n of agent chat (H04's fitter, unchanged; 10 s bins), day-bootstrap; plus every ISO week of
  #51 as the in-period week-to-week noise band;
- inactive runs (state < 3, inside each agent's presence, runs >= 10 min): mean length; idle fraction (state 2) and
  active fraction (state >= 3) of present minutes; from activity_bins_fixed; day-bootstrap differences.
Writes data/processed/H04-reversible-forcing/r1b/NE43.json.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2"
os.environ.setdefault("H04_ACTIVITY_TABLE", "activity_bins_fixed.parquet")

import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hawkes as H  # noqa: E402
import h04lib as L  # noqa: E402

NBOOT = 30
WIN = {"pre": ("2026-07-21", "2026-08-05"), "on": ("2026-08-05", "2026-08-21"), "off": ("2026-08-21", "2026-09-05")}


def days_between(d0, d1):
    return L.select_days(L.calendar(), date_from=d0, date_to=d1)


def hawkes_n(days, boot=NBOOT, seed=L.RNG_SEED):
    ser = H.build_series(days)
    m = H.fit_suite(ser)
    s = m.summary()
    rng = np.random.default_rng(seed)
    bs = []
    for _ in range(boot):
        idx = rng.integers(0, len(ser.days), len(ser.days))
        bs.append(H.Model(ser.subset(list(idx)), m.free).fit(x0=m.theta).summary()["n"])
    return {"n": float(s["n"]), "boot": [float(x) for x in bs], "n_events": int(ser.n_events), "a1": s.get("a1"), "a2": s.get("a2"),
            "eh": s.get("eh"), "en": s.get("en")}


def runs_stats(days):
    D = L.load_days(days)
    per_day = []
    for d in D:
        st = d.state
        act = st >= 3
        pres_any = st != 1
        lens, idle_m, act_m, pres_m = [], 0, 0, 0
        for i in range(st.shape[0]):
            p = pres_any[i]
            if not p.any():
                continue
            a0, a1 = int(np.argmax(p)), int(len(p) - 1 - np.argmax(p[::-1]))
            seg = act[i, a0:a1 + 1]
            pres_m += len(seg); act_m += int(seg.sum()); idle_m += int((st[i, a0:a1 + 1] == 2).sum())
            run = 0
            for x in seg:
                if not x:
                    run += 1
                else:
                    if run >= 10:
                        lens.append(run)
                    run = 0
            if run >= 10:
                lens.append(run)
        per_day.append((d.pt_date, float(np.sum(lens)), len(lens), idle_m, act_m, pres_m))
    return per_day


def main():
    t0 = time.time()
    out = {"windows": {}, "weeks": []}
    R = {}
    for k, (d0, d1) in WIN.items():
        days = days_between(d0, d1)
        assert all(not L.is_holdout_date(d, 51) for d in days)
        hn = hawkes_n(days)
        rs = runs_stats(days)
        R[k] = rs
        arr = np.array([r[1:] for r in rs], float)
        out["windows"][k] = {"days": [days[0], days[-1], len(days)], "hawkes": hn,
                             "n_ci": [hn["n"], float(np.percentile(hn["boot"], 2.5)), float(np.percentile(hn["boot"], 97.5))],
                             "mean_inactive_run_min": float(arr[:, 0].sum() / max(1, arr[:, 1].sum())),
                             "idle_frac": float(arr[:, 2].sum() / arr[:, 4].sum()), "active_frac": float(arr[:, 3].sum() / arr[:, 4].sum())}
        print(k, out["windows"][k]["n_ci"], out["windows"][k]["mean_inactive_run_min"], f"{time.time() - t0:.0f}s", flush=True)
    for a, b in (("on", "off"), ("pre", "on")):
        A, Bb = np.array([r[1:] for r in R[a]], float), np.array([r[1:] for r in R[b]], float)
        out[f"{a}_to_{b}"] = {
            "delta_n": out["windows"][b]["hawkes"]["n"] - out["windows"][a]["hawkes"]["n"],
            "delta_n_boot_ci": [float(np.percentile(np.array(out["windows"][b]["hawkes"]["boot"]) - np.array(out["windows"][a]["hawkes"]["boot"]), q)) for q in (2.5, 97.5)],
            "rel_mean_inactive_run": _rel(A, Bb, lambda x: x[:, 0].sum() / max(1, x[:, 1].sum())),
            "rel_idle_frac": _rel(A, Bb, lambda x: x[:, 2].sum() / x[:, 4].sum()),
            "rel_active_frac": _rel(A, Bb, lambda x: x[:, 3].sum() / x[:, 4].sum())}
    # in-period weekly noise band: every ISO week of #51 (non-holdout, >= 3 days)
    cal = L.calendar().filter((pl.col("goal_no") == 51) & ~pl.col("holdout") & (pl.col("window_s") > 0))
    cal = cal.with_columns(pl.col("pt_date").str.to_date().dt.strftime("%G-W%V").alias("wk"))
    wk_n = []
    for (wk,), g in cal.group_by(["wk"], maintain_order=True):
        ds = sorted(g["pt_date"].to_list())
        if len(ds) >= 3:
            s = H.fit_suite(H.build_series(ds)).summary()
            wk_n.append({"week": wk, "days": [ds[0], ds[-1], len(ds)], "n": float(s["n"])})
    wk_n.sort(key=lambda r: r["week"])
    out["weeks"] = wk_n
    dif = [abs(b["n"] - a["n"]) for a, b in zip(wk_n[:-1], wk_n[1:])]
    out["weekly_abs_delta_n"] = {"median": float(np.median(dif)) if dif else None, "p90": float(np.percentile(dif, 90)) if dif else None,
                                 "n_pairs": len(dif)}
    out["runtime_s"] = round(time.time() - t0, 1)
    (L.OUT / "r1b").mkdir(parents=True, exist_ok=True)
    L.jdump(out, L.OUT / "r1b" / "NE43.json")
    print({k: v for k, v in out.items() if k not in ("windows", "weeks")}, flush=True)


def _rel(A, Bb, f, B=2000, seed=1):
    rng = np.random.default_rng(seed)
    pt = f(Bb) / f(A) - 1
    bs = [f(Bb[rng.integers(0, len(Bb), len(Bb))]) / f(A[rng.integers(0, len(A), len(A))]) - 1 for _ in range(B)]
    return [float(pt), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]


if __name__ == "__main__":
    main()
