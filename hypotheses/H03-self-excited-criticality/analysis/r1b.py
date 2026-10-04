"""H03 round 1b (improved data, 2026-10-04): round 1's specification re-run on corrected inputs.

H03 never read `activity_bins` (its events come from `events_core`, which the DQ8 join bug did not touch), so the
round-1b corrections are the ones the shared tables added since round 1:
  C1 exogenous drive   `kicks_classified` human_message + nudge. Round 1 used every human and `automated` USER_TALK,
                       which also counted the operator's 662 daily pause/resume bookends as exogenous kicks.
  C2 realizations      calendar days split at operator village-off gaps >= 60 min (`outages_fixed`, village_off), the
                       card's "next step 1": six long-window days had two sessions and a dead gap in one realization.
  C3 splits            segments by H03's own step-change rule (`segments.py`) AND by the shared `period_units`.
The model specification (M1_B2 primary, P_B2, M1_B3, M3_sc, day bootstrap, agent-shift null) is round 1's.

Switches keep the round-1 path runnable: --exo r1|kc, --split none|offgap (defaults kc / offgap = round 1b);
`--exo r1 --split none` reproduces round 1's inputs exactly (checked by `check`).

Subcommands (outputs in data/processed/H03-self-excited-criticality/r1b[_<variant>]/):
  build                 days / events / exo for the chosen variant
  check                 r1-variant inputs vs round 1's files (must be identical)
  fit [B1 B2 R]         per-period M1_B2 (+profile CI), P_B2, M1_B3, M3_sc; day bootstrap (B1 for M1_B2, B2 for
                        M3_sc); agent-shift null for M3_sc (R surrogates)        -> period_fits, period_boot, shift_null
  table                 period_table.parquet in round 1's column names (read by H19)
  segments [B]          M1_B2 + profile CI (+ bootstrap B for >= 3 days) and M3_sc per segment, both split rules
  native                period-native tests (NE43 drive withdrawal, NE14 with/without day-edge trim, #2 human-free)
Run: OMP_NUM_THREADS=2 uv run python hypotheses/H03-self-excited-criticality/analysis/r1b.py build
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("POLARS_MAX_THREADS", "2")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from multiprocessing import Pool  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DATA, ROOT, fit_model, hc, specs  # noqa: E402

SH = ROOT / "data/processed/shared"
OFFGAP_MIN = 60          # village-off gap that splits a day into two realizations
EXO_LEAD_S = 3600.0
WORKERS = 2
G: dict = {}


def _seed(*parts) -> int:
    import zlib
    return zlib.crc32("|".join(map(str, parts)).encode())


def out_dir(exo: str, split: str) -> Path:
    tag = "" if (exo, split) == ("kc", "offgap") else f"_{exo}_{split}"
    return DATA / f"r1b{tag}"


def holdout_guard(days: pl.DataFrame):
    h = json.loads((ROOT / "hypotheses/holdout.json").read_text())
    assert not set(days["goal_no"].unique().to_list()) & set(h["goal_periods_held_out"]), "holdout goal leaked"
    for w in h["ne_windows"]:
        assert days.filter((pl.col("pt_date") >= w["start"]) & (pl.col("pt_date") < w["end"])).height == 0, w["id"]


# ------------------------------------------------------------------------------------------------- build
def build(exo_kind: str, split: str):
    od = out_dir(exo_kind, split)
    od.mkdir(parents=True, exist_ok=True)
    days0 = pl.read_parquet(DATA / "days.parquet")          # round-1 realizations (non-holdout, asserted there)
    ev0 = pl.read_parquet(DATA / "events.parquet")
    holdout_guard(days0)
    cal = pl.read_parquet(SH / "calendar.parquet").select("pt_date", "win_start", "win_end")
    d0 = days0.join(cal, on="pt_date")
    # ---- exogenous messages
    if exo_kind == "r1":
        exo0 = pl.read_parquet(DATA / "exo.parquet")
    else:
        k = (pl.read_parquet(SH / "kicks_classified.parquet", columns=["t", "kind"])
             .filter(pl.col("kind").cast(pl.String).is_in(["human_message", "nudge"])))
        rows = []
        for r in d0.iter_rows(named=True):
            lo = r["win_start"] - __import__("datetime").timedelta(seconds=EXO_LEAD_S)
            sub = k.filter((pl.col("t") >= lo) & (pl.col("t") <= r["win_end"]))
            if sub.height:
                rows.append(sub.select(pl.lit(r["day_id"], dtype=pl.Int32).alias("day_id"),
                                       ((pl.col("t") - r["win_start"]).dt.total_microseconds() / 1e6).alias("t_s"),
                                       pl.col("kind").cast(pl.String).alias("kind")))
        exo0 = pl.concat(rows).sort("day_id", "t_s")
    # ---- realizations (pieces)
    gaps = {}
    if split == "offgap":
        o = (pl.read_parquet(SH / "outages_fixed/outages.parquet")
             .filter(pl.col("village_off") & (pl.col("dur_min") >= OFFGAP_MIN)))
        for r in o.iter_rows(named=True):
            gaps.setdefault(r["pt_date"], []).append((r["m_start"] * 60.0, r["m_end"] * 60.0))
    prow, pev, pex, dropped = [], [], [], 0
    new_id = 0
    for r in days0.sort("day_id").iter_rows(named=True):
        T = r["T_s"]
        cuts = sorted(gaps.get(r["pt_date"], []))
        pieces, a = [], 0.0
        for (gs, ge) in cuts:
            if gs - a >= 600:
                pieces.append((a, min(gs, T)))
            a = max(a, ge)
        if T - a >= 600:
            pieces.append((a, T))
        if not cuts:
            pieces = [(0.0, T)]
        e = ev0.filter(pl.col("day_id") == r["day_id"])
        x = exo0.filter(pl.col("day_id") == r["day_id"])
        n_in = 0
        for pi, (s0, s1) in enumerate(pieces):
            ee = e.filter((pl.col("t_s") >= s0) & (pl.col("t_s") <= s1))
            n_in += ee.height
            xx = x.filter((pl.col("t_s") >= s0 - EXO_LEAD_S) & (pl.col("t_s") <= s1))
            if ee.height == 0:
                continue
            pev.append(ee.with_columns(pl.lit(new_id, dtype=pl.Int32).alias("day_id"), (pl.col("t_s") - s0).alias("t_s")))
            if xx.height:
                pex.append(xx.with_columns(pl.lit(new_id, dtype=pl.Int32).alias("day_id"), (pl.col("t_s") - s0).alias("t_s")))
            prow.append({**{k: r[k] for k in ("pt_date", "goal_no", "regime", "mode", "weekday", "documented_hours")},
                         "day_id": new_id, "day_id_r1": r["day_id"], "piece": pi, "offset_s": s0, "T_s": s1 - s0,
                         "first_day": bool(r["first_day"] and pi == 0), "n_active": ee["agent"].n_unique(),
                         "n_talk": int(ee["talk"].sum()), "n_all": int(ee["turn_first"].sum()),
                         "n_exo": int(xx.filter(pl.col("t_s") >= s0).height)})
            new_id += 1
        dropped += e.height - n_in
    days = pl.DataFrame(prow).with_columns(pl.col("day_id").cast(pl.Int32))
    events = pl.concat(pev).select("day_id", "t_s", "agent", "talk", "turn_first").sort("day_id", "t_s")
    exo = pl.concat(pex).select("day_id", "t_s", "kind").sort("day_id", "t_s")
    holdout_guard(days)
    days.write_parquet(od / "days.parquet", compression="zstd")
    events.write_parquet(od / "events.parquet", compression="zstd")
    exo.write_parquet(od / "exo.parquet", compression="zstd")
    info = {"variant": {"exo": exo_kind, "split": split}, "n_realizations": days.height, "n_days_r1": days0.height,
            "split_days": sorted({d for d in gaps if d in set(days0["pt_date"].to_list())}),
            "events_dropped_in_gaps": int(dropped), "n_exo_in_window": int(days["n_exo"].sum()),
            "n_exo_r1_in_window": int(days0["n_exo"].sum()), "exo_kinds": exo.group_by("kind").len().to_dicts()}
    (od / "build_info.json").write_text(json.dumps(info, indent=1, default=str))
    print(json.dumps(info, indent=1, default=str))


def check():
    """The r1/none variant must reproduce round 1's inputs (same events per day, same exo)."""
    od = out_dir("r1", "none")
    a = pl.read_parquet(od / "events.parquet"); b = pl.read_parquet(DATA / "events.parquet")
    x = pl.read_parquet(od / "exo.parquet"); y = pl.read_parquet(DATA / "exo.parquet")
    ok = a.shape == b.shape and (a["t_s"] - b["t_s"]).abs().max() < 1e-9 and x.shape == y.shape
    print("round-1 reproduction:", ok, a.shape, b.shape, x.shape, y.shape)
    return ok


def load(od: Path):
    days = pl.read_parquet(od / "days.parquet")
    ev = pl.read_parquet(od / "events.parquet")
    exo = pl.read_parquet(od / "exo.parquet")
    holdout_guard(days)
    return days, ev, exo


def _init(od):
    days, ev, exo = load(Path(od))
    G["days"] = days
    G["dm"] = {s: hc.make_days(ev, exo, days, s) for s in ("TALK", "ALL")}


# ------------------------------------------------------------------------------------------------- fits
FIT_MODELS = ("M1_B2", "P_B2", "M1_B3", "M3_sc")


def meta_of(days, keys):
    sub = days.filter(pl.col("day_id").is_in(keys))
    return {"n_days": sub["pt_date"].n_unique(), "n_real": sub.height, "N_active": float(sub["n_active"].mean()),
            "hours": float(sub.group_by("pt_date").agg(pl.col("T_s").sum())["T_s"].median() / 3600),
            "regime": "/".join(sorted(set(sub["regime"].to_list()))), "mode": sub["mode"][0],
            "first_date": sub["pt_date"].min(), "last_date": sub["pt_date"].max()}


def shift_day(d, rng):
    t = d.t.copy()
    for a in np.unique(d.agent):
        m = d.agent == a
        t[m] = np.mod(t[m] + rng.uniform(300, 1800) * rng.choice([-1, 1]), d.T)
    o = np.argsort(t, kind="stable")
    return hc.Day(t=t[o], agent=d.agent[o], T=d.T, first=d.first, x=d.x, active=d.active)


def fit_keys(dm, keys, models=FIT_MODELS, prof=True):
    sp = specs()
    out, fits = [], {}
    for m in models:
        ds = hc.Dataset(dm, keys, sp[m])
        if ds.n < 20:
            continue
        f = fit_model(m, ds)
        fits[m] = f
        s = f.summary(); s["model"] = m
        if m == "M1_B2" and prof:
            s["n_prof_lo"], s["n_prof_hi"] = hc.profile_ci_n(f)
        out.append(s)
    return out, fits


def boot_keys(dm, keys, fits, B1, B2, rng):
    sp = specs()
    rows = []
    real_days = sorted(set(keys))
    if len(real_days) < 3:
        return rows
    for name, nb in (("M1_B2", B1), ("M3_sc", B2)):
        if name not in fits:
            continue
        for b in range(nb):
            bk = list(rng.choice(real_days, len(real_days), replace=True))
            ds = hc.Dataset(dm, bk, sp[name])
            if ds.n < 20:
                continue
            p0, _ = hc.transfer_params(fits[name], ds)
            f = fit_model(name, ds, p0=p0, beta_starts=[1 / 10, 1 / 1000] if ds.free_beta else None)
            s = f.summary()
            rows.append({"model": name, "rep": b, "n": s["n"], "n_cross": s.get("n_cross", np.nan),
                         "n_self": s.get("n_self", np.nan), "n_cross_fast300": s.get("n_cross_fast300", np.nan),
                         "n_self_fast300": s.get("n_self_fast300", np.nan)})
    return rows


def run_period(task):
    goal, eset, B1, B2, R = task
    t0 = time.time()
    days, dm = G["days"], G["dm"][eset]
    keys = days.filter(pl.col("goal_no") == goal).sort("day_id")["day_id"].to_list()
    meta = meta_of(days, keys)
    rows, fits = fit_keys(dm, keys)
    for s in rows:
        s.update({"goal_no": goal, "set": eset, **meta})
    big = days.filter(pl.col("goal_no") == goal)[("n_talk" if eset == "TALK" else "n_all")].sum() > 30000
    rng = np.random.default_rng(1000 * goal + (eset == "ALL"))
    b1, b2 = (max(B1 // 3, 10), max(B2 // 3, 5)) if big else (B1, B2)
    boots = [{"goal_no": goal, "set": eset, **r} for r in boot_keys(dm, keys, fits, b1, b2, rng)]
    shifts = []
    if "M3_sc" in fits:
        for r in range(R):
            dms = {k: shift_day(dm[k], rng) for k in keys}
            f = fit_model("M3_sc", hc.Dataset(dms, keys, specs()["M3_sc"]))
            s = f.summary()
            shifts.append({"goal_no": goal, "set": eset, "rep": r, "n_cross_fast300": s["n_cross_fast300"],
                           "n_cross": s["n_cross"], "n_self_fast300": s["n_self_fast300"]})
    print(f"r1b fit goal {goal} {eset}: {len(rows)} fits, {len(boots)} boots, {len(shifts)} shifts, {time.time() - t0:.0f}s",
          flush=True)
    return rows, boots, shifts


def fit_all(od: Path, B1: int, B2: int, R: int, goals=None):
    days, _, _ = load(od)
    size = days.group_by("goal_no").agg(pl.col("n_all").sum()).sort("n_all", descending=True)["goal_no"].to_list()
    if goals:
        size = [g for g in size if g in goals]
    tasks = [(g, s, B1, B2, R) for g in size for s in ("TALK", "ALL")]
    with Pool(WORKERS, initializer=_init, initargs=(str(od),)) as pool:
        out = pool.map(run_period, tasks, chunksize=1)
    suf = "" if not goals else "_" + "_".join(map(str, goals))
    pl.DataFrame([r for o in out for r in o[0]], infer_schema_length=None).write_parquet(od / f"period_fits{suf}.parquet")
    pl.DataFrame([r for o in out for r in o[1]]).write_parquet(od / f"period_boot{suf}.parquet")
    pl.DataFrame([r for o in out for r in o[2]]).write_parquet(od / f"shift_null{suf}.parquet")


def _cat(od: Path, stem: str) -> pl.DataFrame:
    fs = sorted(od.glob(f"{stem}*.parquet"))
    return pl.concat([pl.read_parquet(f) for f in fs], how="diagonal_relaxed").unique(
        subset=[c for c in ("goal_no", "set", "model", "rep") if c in pl.read_parquet(fs[0]).columns], keep="last")


def table(od: Path) -> pl.DataFrame:
    fits = _cat(od, "period_fits")
    boot = _cat(od, "period_boot")
    sh = _cat(od, "shift_null")

    def col(model, c, alias):
        return fits.filter(pl.col("model") == model).select("goal_no", "set", pl.col(c).alias(alias))
    fast = ["10", "30", "100", "300"]
    sc = fits.filter(pl.col("model") == "M3_sc").select(
        "goal_no", "set", "m_bar", pl.col("tau_cross_s").alias("tau_cross"), pl.col("n_self").alias("n_self"),
        pl.col("n_cross").alias("n_cross"),
        n_self_fast=pl.sum_horizontal([pl.col(f"self_{k}") for k in fast]),
        n_c_pair_fast=pl.sum_horizontal([pl.col(f"cross_{k}") for k in fast]))
    sc = sc.with_columns(n_cross_fast=pl.col("n_c_pair_fast") * (pl.col("m_bar") - 1))
    base = fits.filter(pl.col("model") == "M1_B2").select(
        "goal_no", "set", "mode", "regime", "n_days", "n_real", "N_active", "hours", "n_events", "n", "tau_s",
        "n_prof_lo", "n_prof_hi", "ll", "exo_total")
    for model, c, alias in (("M1_B3", "n", "n_B3"), ("P_B2", "ll", "ll_P_B2"), ("M1_B3", "ll", "ll_B3")):
        base = base.join(col(model, c, alias), on=["goal_no", "set"], how="left")
    base = base.join(sc, on=["goal_no", "set"], how="left").with_columns(dAIC_B2=-2 * (pl.col("ll") - pl.col("ll_P_B2")) + 4)
    if boot.height:
        bs = boot.group_by("goal_no", "set", "model").agg(
            lo=pl.col("n").quantile(0.025), hi=pl.col("n").quantile(0.975), B=pl.len(),
            xflo=pl.col("n_cross_fast300").quantile(0.025), xfhi=pl.col("n_cross_fast300").quantile(0.975))
        base = base.join(bs.filter(pl.col("model") == "M1_B2").select("goal_no", "set", pl.col("lo").alias("n_boot_lo"),
                                                                    pl.col("hi").alias("n_boot_hi"), pl.col("B").alias("B_boot")),
                         on=["goal_no", "set"], how="left")
        base = base.join(bs.filter(pl.col("model") == "M3_sc").select("goal_no", "set", pl.col("xflo").alias("n_cross_fast_boot_lo"),
                                                                    pl.col("xfhi").alias("n_cross_fast_boot_hi")),
                         on=["goal_no", "set"], how="left")
    if sh.height:
        base = base.join(sh.group_by("goal_no", "set").agg(pl.col("n_cross_fast300").mean().alias("shift_null_fast"),
                                                          pl.col("n_cross_fast300").max().alias("shift_null_fast_max")),
                         on=["goal_no", "set"], how="left")
    base = base.sort("set", "goal_no")
    base.write_parquet(od / "period_table.parquet", compression="zstd")
    return base


# ------------------------------------------------------------------------------------------------- segments
def h03_segment_days(days: pl.DataFrame) -> pl.DataFrame:
    """Round-1 rule (segments.py) on the round-1b realizations: step dates from step_changes.parquet."""
    sc = pl.read_parquet(DATA / "step_changes.parquet")
    cdates = sorted(set(sc["date"].to_list()))
    out = []
    for g in sorted(days["goal_no"].unique().to_list()):
        sub = days.filter(pl.col("goal_no") == g).sort("day_id")
        dates = sub["pt_date"].to_list()
        d0, seg, prev, segs = dates[0], 0, dates[0], []
        for d in dates:
            if d != d0 and d != prev and any(prev < c <= d for c in cdates):
                seg += 1
            segs.append(seg); prev = d
        out.append(sub.with_columns(pl.Series("seg", segs, dtype=pl.Int32)))
    return pl.concat(out).select("day_id", "pt_date", "goal_no", pl.col("seg").cast(pl.String).alias("seg"))


def pu_segment_days(days: pl.DataFrame) -> pl.DataFrame:
    pu = pl.read_parquet(SH / "period_units.parquet").filter(~pl.col("holdout")).select("unit_id", "goal_no", "days").explode("days")
    m = pu.rename({"days": "pt_date"}).with_columns(pl.col("goal_no").cast(pl.Int64))
    d = days.select("day_id", "pt_date", pl.col("goal_no").cast(pl.Int64)).join(m, on=["pt_date", "goal_no"], how="left")
    assert d["unit_id"].null_count() == 0, d.filter(pl.col("unit_id").is_null())
    return d.select("day_id", "pt_date", "goal_no", pl.col("unit_id").alias("seg"))


def run_seg(task):
    rule, goal, seg, keys, eset, B = task
    t0 = time.time()
    days, dm = G["days"], G["dm"][eset]
    meta = {"rule": rule, "goal_no": goal, "seg": seg, "set": eset, **meta_of(days, keys)}
    rows, fits = fit_keys(dm, keys, models=("M1_B2", "M3_sc"))
    for s in rows:
        s.update(meta)
    boots = []
    if B and len(set(days.filter(pl.col("day_id").is_in(keys))["pt_date"].to_list())) >= 3:
        rng = np.random.default_rng(_seed(rule, goal, seg, eset))
        boots = [{**meta, **r} for r in boot_keys(dm, keys, fits, B, 0, rng)]
    print(f"seg {rule} {goal}.{seg} {eset} ({meta['n_days']} d): {time.time() - t0:.0f}s", flush=True)
    return rows, boots


def segments(od: Path, B: int):
    days, _, _ = load(od)
    tasks = []
    for rule, sd in (("h03", h03_segment_days(days)), ("pu", pu_segment_days(days))):
        nseg = sd.group_by("goal_no").agg(pl.col("seg").n_unique().alias("k"))
        split_goals = nseg.filter(pl.col("k") > 1)["goal_no"].to_list()
        for (g, seg), sub in sd.filter(pl.col("goal_no").is_in(split_goals)).group_by("goal_no", "seg"):
            keys = sub.sort("day_id")["day_id"].to_list()
            for eset in ("TALK", "ALL"):
                tasks.append((rule, int(g), str(seg), keys, eset, B))
    tasks.sort(key=lambda t: -len(t[3]))
    with Pool(WORKERS, initializer=_init, initargs=(str(od),)) as pool:
        out = pool.map(run_seg, tasks, chunksize=1)
    pl.DataFrame([r for o in out for r in o[0]], infer_schema_length=None).write_parquet(od / "segments.parquet")
    pl.DataFrame([r for o in out for r in o[1]]).write_parquet(od / "segments_boot.parquet")


# ------------------------------------------------------------------------------------------------- native
def trim_daymap(dm: dict, days: pl.DataFrame) -> dict:
    """Day-edge adjustment for Hawkes realizations: cut each realization to its all-present window (every agent
    active that day is between its first and last active minute in `activity_bins_fixed`; H38's operator rule)."""
    ab = (pl.scan_parquet(SH / "activity_bins_fixed.parquet").filter(pl.col("state") >= 3)
          .filter(pl.col("pt_date").is_in(days["pt_date"].unique().to_list()))
          .group_by("pt_date", "agent").agg(pl.col("minute").min().alias("m0"), pl.col("minute").max().alias("m1")).collect())
    win = ab.group_by("pt_date").agg(pl.col("m0").max().alias("lo"), pl.col("m1").min().alias("hi"))
    w = dict((r[0], (r[1] * 60.0, (r[2] + 1) * 60.0)) for r in win.iter_rows())
    out = {}
    for r in days.iter_rows(named=True):
        d = dm[r["day_id"]]
        lo, hi = w.get(r["pt_date"], (0.0, d.T))
        lo, hi = lo - r["offset_s"], hi - r["offset_s"]
        lo, hi = max(lo, 0.0), min(hi, d.T)
        if hi - lo < 1800:
            continue
        m = (d.t >= lo) & (d.t <= hi)
        x = d.x - lo
        x = x[x <= hi - lo]   # exogenous messages after the trimmed window end would give negative compensators
        out[r["day_id"]] = hc.Day(t=d.t[m] - lo, agent=d.agent[m], T=hi - lo, first=False, x=x, active=d.active)
    return out


def native(od: Path, B: int, R: int, only=None):
    days, ev, exo = load(od)
    res = json.loads((od / "native.json").read_text()) if (only and (od / "native.json").exists()) else {}
    sp = specs()

    def side_fit(dm, keys, eset, label, boot=True, shifts=0):
        rows, fits = fit_keys(dm, keys, models=("M1_B2", "P_B2", "M3_sc"))
        out = {"label": label, "set": eset, "n_real": len(keys),
               "days": sorted(set(days.filter(pl.col("day_id").is_in(keys))["pt_date"].to_list()))}
        for s in rows:
            if s["model"] == "M1_B2":
                out.update({"n": s["n"], "tau_s": s["tau_s"], "n_prof_lo": s.get("n_prof_lo"), "n_prof_hi": s.get("n_prof_hi"),
                            "exo_total": s["exo_total"], "n_events": s["n_events"]})
            if s["model"] == "M3_sc":
                out.update({"n_cross_fast": s["n_cross_fast300"], "n_self_fast": s["n_self_fast300"], "m_bar": s["m_bar"]})
        # event rate per active agent-hour, exogenous / triggered shares (model-based)
        T = sum(dm[k].T for k in keys)
        out["rate_per_h"] = float(sum(len(dm[k].t) for k in keys) / (T / 3600))
        out["rate_per_agent_h"] = float(np.mean([len(dm[k].t) / max(len(dm[k].active), 1) / (dm[k].T / 3600) for k in keys]))
        if "M1_B2" in fits:
            f = fits["M1_B2"]
            mu, ex, ker = f.intensity_parts()[:3]
            tot = mu + ex + ker
            out.update({"share_base": float((mu / tot).mean()), "share_exo": float((ex / tot).mean()),
                        "share_trig": float((ker / tot).mean())})
        if boot:
            rng = np.random.default_rng(_seed(label, eset))
            bs = boot_keys(dm, keys, fits, B, max(B // 2, 5), rng)
            nb = np.array([b["n"] for b in bs if b["model"] == "M1_B2"])
            xb = np.array([b["n_cross_fast300"] for b in bs if b["model"] == "M3_sc"])
            if len(nb):
                out.update({"n_boot_sd": float(nb.std()), "n_boot_lo": float(np.quantile(nb, 0.025)),
                            "n_boot_hi": float(np.quantile(nb, 0.975))})
            if len(xb):
                out.update({"xf_boot_sd": float(xb.std())})
        if shifts:
            rng = np.random.default_rng(_seed(label, eset, "shift"))
            v = []
            for _ in range(shifts):
                dms = {k: shift_day(dm[k], rng) for k in keys}
                v.append(fit_model("M3_sc", hc.Dataset(dms, keys, sp["M3_sc"])).summary()["n_cross_fast300"])
            out["shift_null_fast"] = float(np.mean(v))
            out["shift_null_fast_max"] = float(np.max(v))
        return out

    dmaps = {s: hc.make_days(ev, exo, days, s) for s in ("TALK", "ALL")}
    # ---- NE43: drive withdrawal inside #51 at a fixed roster (07-29 .. 08-27: no join between Opus 5 and GLM-5.3)
    seg = days.filter((pl.col("goal_no") == 51) & (pl.col("pt_date") >= "2026-07-29") & (pl.col("pt_date") <= "2026-08-27"))
    sides = {"A_bookends+nudges": ("2026-07-29", "2026-08-04"), "B_nudges_only": ("2026-08-05", "2026-08-20"),
             "C_no_drive": ("2026-08-21", "2026-08-27")}
    ne43 = {}
    for eset in (("TALK", "ALL") if not only or "NE43" in only else ()):
        for lab, (a, b) in sides.items():
            keys = seg.filter((pl.col("pt_date") >= a) & (pl.col("pt_date") <= b)).sort("day_id")["day_id"].to_list()
            ne43[f"{lab}|{eset}"] = side_fit(dmaps[eset], keys, eset, lab)
            print("NE43", lab, eset, {k: ne43[f'{lab}|{eset}'].get(k) for k in ("n", "n_boot_sd", "rate_per_agent_h", "share_exo")},
                  flush=True)
    if ne43:
        res["NE43"] = ne43
    # ---- NE14: last regime-II days (#35, #36 before 03-24) vs first regime-III days (#36 from 03-24, #37), raw and
    #      trimmed to the all-present window (the day-edge adjustment for event-time models)
    ii = days.filter((pl.col("goal_no") == 35) | ((pl.col("goal_no") == 36) & (pl.col("pt_date") < "2026-03-24")))
    iii = days.filter(((pl.col("goal_no") == 36) & (pl.col("pt_date") >= "2026-03-24")) | (pl.col("goal_no") == 37))
    ne14 = {}
    for eset in (("TALK", "ALL") if not only or "NE14" in only else ()):
        tm = trim_daymap(dmaps[eset], pl.concat([ii, iii]))
        for lab, sd in (("II", ii), ("III", iii)):
            keys = sd.sort("day_id")["day_id"].to_list()
            ne14[f"{lab}|raw|{eset}"] = side_fit(dmaps[eset], keys, eset, f"{lab}-raw", shifts=R)
            kt = [k for k in keys if k in tm]
            ne14[f"{lab}|trim|{eset}"] = side_fit(tm, kt, eset, f"{lab}-trim", shifts=R)
            ne14[f"{lab}|trim|{eset}"]["kept_share"] = float(sum(tm[k].T for k in kt) / sum(dmaps[eset][k].T for k in keys))
            print("NE14", lab, eset, ne14[f"{lab}|raw|{eset}"].get("n"), ne14[f"{lab}|trim|{eset}"].get("n"), flush=True)
    if ne14:
        res["NE14"] = ne14
    # ---- #2: the only human-free, operator-free window: fast cross-triggering vs agent-shift null, exo absent
    if not only or "G02" in only:
        k2 = days.filter(pl.col("goal_no") == 2).sort("day_id")["day_id"].to_list()
        res["G02"] = {eset: side_fit(dmaps[eset], k2, eset, "G02", shifts=max(R, 10)) for eset in ("TALK", "ALL")}
        res["G02"]["n_exo"] = int(days.filter(pl.col("goal_no") == 2)["n_exo"].sum())
    (od / "native.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res["G02"], indent=1, default=float))


# ------------------------------------------------------------------------------------------------- DQ8 null
def run_trim(task):
    goal, eset, R = task
    t0 = time.time()
    days, dm = G["days"], G["dm"][eset]
    sub = days.filter(pl.col("goal_no") == goal)
    tm = trim_daymap(dm, sub)
    keys = [k for k in sub.sort("day_id")["day_id"].to_list() if k in tm]
    out = {"goal_no": goal, "set": eset, "n_real_trim": len(keys),
           "kept_share": float(sum(tm[k].T for k in keys) / max(sum(dm[k].T for k in sub["day_id"].to_list()), 1))}
    if len(keys) == 0:
        return out
    rows, fits = fit_keys(tm, keys, models=("M1_B2", "M3_sc"), prof=False)
    for s_ in rows:
        if s_["model"] == "M1_B2":
            out["n_trim"] = s_["n"]
        else:
            out["nx_trim"] = s_["n_cross_fast300"]
    rng = np.random.default_rng(_seed("trimnull", goal, eset))
    v = []
    if "M3_sc" in fits:
        for _ in range(R):
            dms = {k: shift_day(tm[k], rng) for k in keys}
            v.append(fit_model("M3_sc", hc.Dataset(dms, keys, specs()["M3_sc"])).summary()["n_cross_fast300"])
    out.update({"shift_trim_mean": float(np.mean(v)) if v else None, "shift_trim_max": float(np.max(v)) if v else None})
    print(f"trim null {goal} {eset}: {time.time() - t0:.0f}s", flush=True)
    return out


def trim_null(od: Path, R: int):
    """DQ8 correction for H03's surrogate test: realizations cut to the all-present window BEFORE the agent-shift
    surrogates are drawn (round 1 shifted on the whole window). Writes <od>/trim_null.parquet."""
    days, _, _ = load(od)
    size = days.group_by("goal_no").agg(pl.col("n_all").sum()).sort("n_all", descending=True)["goal_no"].to_list()
    tasks = [(g, s_, R) for g in size for s_ in ("TALK", "ALL")]
    with Pool(WORKERS, initializer=_init, initargs=(str(od),)) as pool:
        out = pool.map(run_trim, tasks, chunksize=1)
    pl.DataFrame(out).write_parquet(od / "trim_null.parquet")


# ------------------------------------------------------------------------------------------------- summary
def summary(od: Path):
    """Round 1 vs round 1b: per-period verdicts (round-1 rules), P1-P7, fast cross-triggering vs the agent-shift
    null, #51 drift under both split rules, native tests. Writes <od>/summary.json."""
    from scipy import stats
    import summarize as SU
    import write_period_cards as WP
    t1 = pl.read_parquet(DATA / "period_table.parquet")
    tb = pl.read_parquet(od / "period_table.parquet")
    res = {"tests_r1": SU.tests(t1), "tests_r1b": SU.tests(tb)}
    seg = pl.read_parquet(od / "segments.parquet")
    drift = {}
    for rule in ("h03", "pu"):
        for eset in ("TALK", "ALL"):
            d = seg.filter((pl.col("rule") == rule) & (pl.col("goal_no") == 51) & (pl.col("model") == "M1_B2") & (pl.col("set") == eset)).sort("first_date")
            rho, p = stats.spearmanr(d["n"], d["N_active"])
            m3 = seg.filter((pl.col("rule") == rule) & (pl.col("goal_no") == 51) & (pl.col("model") == "M3_sc") & (pl.col("set") == eset))
            m3 = m3.with_columns(pl.sum_horizontal([pl.col(f"cross_{k}") for k in ("10", "30", "100", "300")]).alias("pair"))
            rp, pp = stats.spearmanr(m3["pair"], m3["N_active"])
            drift[f"{rule}|{eset}"] = {"n_seg": d.height, "rho_n_N": float(rho), "p": float(p), "max_n": float(d["n"].max()),
                                       "last_n": d["n"].to_list()[-3:], "rho_pair_N": float(rp), "p_pair": float(pp),
                                       "segs": d.select("seg", "first_date", "N_active", "n", "n_prof_lo", "n_prof_hi").to_dicts()}
    res["drift51"] = drift
    verd = {}
    for g in sorted(tb["goal_no"].unique().to_list()):
        out = {}
        for lab, tab, sd in (("r1", t1, None), ("r1b", tb, drift["h03|TALK"])):
            r = tab.filter((pl.col("goal_no") == g) & (pl.col("set") == "TALK")).to_dicts()[0]
            s51 = (sd["rho_n_N"], sd["p"]) if sd else (-0.64, 0.044)
            v, why = WP.verdict(r["mode"], r, s51)
            out[lab] = {"verdict": v, "n": r["n"], "why": why}
        verd[g] = out
    res["verdicts"] = verd
    res["verdict_changes"] = {g: (v["r1"]["verdict"], v["r1b"]["verdict"]) for g, v in verd.items() if v["r1"]["verdict"] != v["r1b"]["verdict"]}
    for eset in ("TALK", "ALL"):
        t = tb.filter(pl.col("set") == eset)
        real, nul, mx = t["n_cross_fast"].to_numpy(), t["shift_null_fast"].to_numpy(), t["shift_null_fast_max"].to_numpy()
        ok = np.isfinite(real) & np.isfinite(nul)
        res[f"shift_{eset}"] = {"median_real": float(np.median(real[ok])), "median_null": float(np.median(nul[ok])),
                                "frac_real_gt_max": float(np.mean(real[ok] > mx[ok])),
                                "wilcoxon_p": float(stats.wilcoxon(real[ok], nul[ok], alternative="greater").pvalue)}
        fC = t.filter((pl.col("mode") == "C"))["n_cross_fast"].drop_nulls().to_numpy()
        fF = t.filter((pl.col("mode") == "F"))["n_cross_fast"].drop_nulls().to_numpy()
        res[f"P6_{eset}"] = {"median_C": float(np.median(fC)), "median_F": float(np.median(fF)),
                             "p_MW_C_gt_F": float(stats.mannwhitneyu(fC, fF, alternative="greater").pvalue)}
        res[f"rho_pair_N_{eset}"] = [float(v) for v in stats.spearmanr(t["n_c_pair_fast"].to_numpy(), t["N_active"].to_numpy(), nan_policy="omit")]
    d = t1.join(tb.select("goal_no", "set", pl.col("n").alias("n1b")), on=["goal_no", "set"])
    res["delta_n"] = {s: {"median_abs": float((d.filter(pl.col("set") == s)["n1b"] - d.filter(pl.col("set") == s)["n"]).abs().median()),
                          "big": d.filter((pl.col("set") == s) & ((pl.col("n1b") - pl.col("n")).abs() > 0.1)).select("goal_no", "n", "n1b").to_dicts()}
                      for s in ("TALK", "ALL")}
    if (od / "native.json").exists():
        res["native"] = json.loads((od / "native.json").read_text())
    (od / "summary.json").write_text(json.dumps(res, indent=1, default=float))
    return res


# ------------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["build", "check", "fit", "table", "segments", "native", "trimnull", "summary", "time"])
    ap.add_argument("args", nargs="*", type=int)
    ap.add_argument("--exo", default="kc", choices=["r1", "kc"])
    ap.add_argument("--split", default="offgap", choices=["none", "offgap"])
    ap.add_argument("--goals", default="")
    a = ap.parse_args()
    od = out_dir(a.exo, a.split)
    goals = [int(x) for x in a.goals.split(",") if x.isdigit()]
    if a.cmd == "build":
        build(a.exo, a.split)
    elif a.cmd == "check":
        check()
    elif a.cmd == "fit":
        B1, B2, R = (a.args + [50, 20, 5][len(a.args):])[:3]
        fit_all(od, B1, B2, R, goals or None)
        table(od)
    elif a.cmd == "table":
        print(table(od).select("goal_no", "set", "n", "n_boot_lo", "n_boot_hi", "n_cross_fast", "shift_null_fast"))
    elif a.cmd == "segments":
        segments(od, (a.args + [20])[0])
    elif a.cmd == "native":
        B, R = (a.args + [30, 5][len(a.args):])[:2]
        native(od, B, R, only=[x for x in a.goals.split(",") if x] or None)
    elif a.cmd == "trimnull":
        trim_null(od, (a.args + [5])[0])
    elif a.cmd == "summary":
        r = summary(od)
        print(json.dumps({k: v for k, v in r.items() if k not in ("verdicts", "native", "drift51")}, indent=1, default=float)[:6000])
        print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "segs"} for k, v in r["drift51"].items()}, indent=1, default=float))
    elif a.cmd == "time":
        _init(str(od))
        for g in goals:
            for eset in ("TALK", "ALL"):
                t0 = time.time()
                keys = G["days"].filter(pl.col("goal_no") == g)["day_id"].to_list()
                rows, fits = fit_keys(G["dm"][eset], keys)
                print(g, eset, f"{time.time() - t0:.1f}s", {r["model"]: round(r.get("n", np.nan), 3) for r in rows}, flush=True)


if __name__ == "__main__":
    main()
