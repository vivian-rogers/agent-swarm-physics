"""H19 scheme, part 2: the per-period table of loop-gain estimates, across hypotheses and methods (non-holdout).

Outputs (data/processed/H19-loop-gain-collapse/):
  estimates_window.parquet   one row per estimate window (chunk, ISO week, room window, whole period)
  estimates.parquet          one row per (goal period, method): windows combined by inverse-variance weighting
  validation_geq_vs_h02.parquet   H19's own Curie-Weiss estimator vs H02's published chunks
  G<NN>/inputs.json          per period: controls and every estimate (the per-period input record)

Sources (read-only; never modified):
  H02 mf_cw.parquet; H03 period_table.parquet; H04 explore_placebo_switch.json; H05 mf_blocks.json + its own
  block_J estimator called on pair_day_bin1.parquet (to get loop-gain SEs); shared activity_bins (H19's own g_eq).
  Ingest hook: data/processed/H*/per_period_estimates.parquet in the proposed shared schema (card, Notes).

Usage: uv run python hypotheses/H19-loop-gain-collapse/scheme/build_estimates.py
Round 1b (2026-10-04): H19_DATA=r1b uv run python .../build_estimates.py [--stale drop|keep]
  H19's own g_eq on activity_bins_fixed (+ DQ8-trimmed and H38-conditioned variants, scheme/geq_r1b.py); H02 and H03
  from their round-1b outputs (data/processed/H02-.../r1b/mf_cw.parquet, H03-.../r1b/period_table.parquet). H04's
  K_week and H05's two-block gains were built on the buggy activity_bins and are not yet re-run by their owners:
  dropped by default (--stale drop), kept with --stale keep (sensitivity). H04's Hawkes n_week reads chat, not
  activity_bins, and is kept. Results go to data/processed/H19-loop-gain-collapse/r1b/.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # never leave __pycache__ in other hypotheses' folders
sys.path.insert(0, str(Path(__file__).resolve().parent))
import h19common as C  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

SEED = 20261003
NBOOT_GEQ = 300
NBOOT_H05 = 500
SE_FLOOR = 0.02  # floor on SEs derived from CIs (n-hat CIs collapse at the n >= 0 boundary)

# H02 chunking / population / block rules (hypotheses/H02-couplings-are-real/scheme/build_spins.py, analysis/h02lib.py)
CHUNK_DAYS, MIN_TAIL_DAYS, MIN_ACTIVE_BINS = 5, 3, 30
BLOCK_MIN, MIN_LAST_BLOCK, MIN_BLOCK_N = 30, 10, 5

METHODS = {
    # method: (family, estimand, primary, validation_only, description)
    "H19.geq_active": ("E", "1-1/VR", True, False, "Curie-Weiss VR on 1-min active spins (state>=3), 30-min blocks, H02 rules, all periods"),
    "H19.geq_talk": ("E", "1-1/VR", False, False, "same on talk spins (state==4; agents with >=30 talk bins)"),
    "H02.gcw_active": ("E", "1-1/VR", False, True, "H02 published beta*J0*q (same estimator as H19.geq_active)"),
    "H04.K_week": ("E", "1-1/VR", False, False, "H04 detrended (61-min MA) active-spin K per ISO week"),
    "H05.g2b_talk": ("E", "v*sum_j J_ij (2-block)", False, False, "H05 two-block MF loop gain, talk spins, excess over cross-day surrogate"),
    "H05.g2b_active": ("E", "v*sum_j J_ij (2-block)", False, False, "H05 two-block MF loop gain, active spins"),
    "H03.n_talk": ("T", "hawkes n", True, False, "H03 M1 Hawkes n on AGENT_TALK, B2 baseline + exogenous drive"),
    "H03.n_all": ("T", "hawkes n", False, False, "H03 M1 Hawkes n on all agent turns, B2 baseline"),
    "H03.nx_fast": ("T", "hawkes n_cross fast", False, False, "H03 M3 fast (tau<=300 s) cross-agent offspring per TALK event"),
    "H04.n_week": ("T", "hawkes n", False, False, "H04 Hawkes n on agent chat per ISO week (4-step day profile)"),
    # round 1b (secondary): DQ8-trimmed and H38-conditioned versions of H19's own estimator
    "H19.geq_active_trim": ("E", "1-1/VR", False, False, "g_eq active on the all-present window, explained joint silences removed (DQ8)"),
    "H19.geq_talk_trim": ("E", "1-1/VR", False, False, "g_eq talk on the all-present window, explained joint silences removed (DQ8)"),
    "H19.geq_active_scaf": ("E", "1-1/VR", False, False, "g_eq active, H38 agent-state conditioning (mask_scaffold)"),
    "H19.geq_talk_scaf": ("E", "1-1/VR", False, False, "g_eq talk, H38 agent-state conditioning (mask_scaffold)"),
}


# ----------------------------------------------------------------------------- H19's own equal-time estimator
def block_ids(day: np.ndarray, minute: np.ndarray) -> np.ndarray:
    blk = minute // BLOCK_MIN
    out = np.empty_like(blk)
    for d in np.unique(day):
        m = day == d
        b = blk[m].copy()
        last = b.max()
        if last > 0 and (b == last).sum() < MIN_LAST_BLOCK:
            b[b == last] = last - 1
        out[m] = b
    return day.astype(np.int64) * 1000 + out


def block_suffstats(S: np.ndarray, day: np.ndarray, minute: np.ndarray):
    """Per (day, block): n, n*Var(M), n*sum_i Var(s_i), n*mean_i Var(s_i), and the block's day."""
    bid = block_ids(day, minute)
    rows = []
    for b in np.unique(bid):
        m = bid == b
        X = S[m].astype(float)
        n = X.shape[0]
        if n < MIN_BLOCK_N:
            continue
        v = X.var(0)
        rows.append((n, X.sum(1).var() * n, v.sum() * n, v.mean() * n, b // 1000))
    return np.array(rows, dtype=float)


def cw_from_stats(st: np.ndarray) -> dict:
    obs, exp_, qs, nt = st[:, 1].sum(), st[:, 2].sum(), st[:, 3].sum(), st[:, 0].sum()
    VR = obs / exp_
    q = qs / nt
    return {"VR": VR, "q": q, "g": 1 - 1 / VR, "bJ0": (1 - 1 / VR) / q}


def cw_boot(st: np.ndarray, rng: np.random.Generator, nboot: int) -> tuple[float, str]:
    days = np.unique(st[:, 4])
    gs = []
    if len(days) >= 4:
        idx = {d: np.flatnonzero(st[:, 4] == d) for d in days}
        for _ in range(nboot):
            pick = rng.choice(days, size=len(days), replace=True)
            gs.append(cw_from_stats(st[np.concatenate([idx[d] for d in pick])])["g"])
        return float(np.std(gs) * np.sqrt(len(days) / (len(days) - 1))), "day_boot"
    for _ in range(nboot):  # too few days: resample 30-min blocks (anti-conservative; flagged)
        gs.append(cw_from_stats(st[rng.integers(len(st), size=len(st))])["g"])
    return float(np.std(gs)), "block_boot"


def chunks_of(days: list[str]) -> list[list[str]]:
    ch = [days[i:i + CHUNK_DAYS] for i in range(0, len(days), CHUNK_DAYS)]
    if len(ch) > 1 and len(ch[-1]) < MIN_TAIL_DAYS:
        ch = ch[:-1]
    return ch


def own_geq(cal: pl.DataFrame, rng: np.random.Generator) -> pl.DataFrame:
    days = cal["pt_date"].to_list()
    ab = (pl.scan_parquet(C.SHARED / "activity_bins.parquet").filter(pl.col("pt_date").is_in(days))
          .select("pt_date", "minute", "agent", "state").collect())
    rows = []
    for g in sorted(cal["goal_no"].unique().to_list()):
        gdays = sorted(cal.filter(pl.col("goal_no") == g)["pt_date"].to_list())
        for k, ch in enumerate(chunks_of(gdays)):
            d = ab.filter(pl.col("pt_date").is_in(ch)).with_columns(
                pl.col("pt_date").replace_strict({x: i for i, x in enumerate(ch)}, return_dtype=pl.Int16).alias("day"))
            pres = (d.group_by("agent").agg(pl.col("pt_date").n_unique().alias("nd"), (pl.col("state") >= 3).sum().alias("nact"),
                                            (pl.col("state") == 4).sum().alias("ntalk"))
                    .filter((pl.col("nd") == len(ch)) & (pl.col("nact") >= MIN_ACTIVE_BINS)))
            for spin, thr in (("active", 3), ("talk", 4)):
                ok = pres if spin == "active" else pres.filter(pl.col("ntalk") >= MIN_ACTIVE_BINS)
                if ok.height < 3:
                    continue
                agents = sorted(ok["agent"].to_list())
                dd = d.filter(pl.col("agent").is_in(agents))
                piv = (dd.with_columns(pl.when(pl.col("state") >= thr).then(1).otherwise(-1).cast(pl.Int8).alias("s"))
                       .pivot(on="agent", index=["day", "minute"], values="s").sort("day", "minute"))
                S = piv.select([str(a) for a in agents]).to_numpy()
                if np.isnan(S.astype(float)).any():
                    S = np.nan_to_num(S.astype(float), nan=-1.0)
                st = block_suffstats(S, piv["day"].to_numpy(), piv["minute"].to_numpy())
                est = cw_from_stats(st)
                se, kind = cw_boot(st, rng, NBOOT_GEQ)
                rows.append({"goal_no": g, "window": f"g{g:02d}c{k}", "method": f"H19.geq_{spin}", "value": est["g"], "se": se,
                             "ci_kind": kind, "n_days": len(ch), "N": len(agents), "VR": est["VR"], "q": est["q"], "bJ0": est["bJ0"],
                             "occupancy": float((S > 0).mean())})
    return pl.DataFrame(rows)


# ----------------------------------------------------------------------------- other hypotheses
R1B = C.DATA_VERSION == "r1b"
H02_DIR = C.PROC / "H02-couplings-are-real" / ("r1b" if R1B else "")
H03_DIR = C.PROC / "H03-self-excited-criticality" / ("r1b" if R1B else "")


def h02_rows() -> pl.DataFrame:
    d = pl.read_parquet(H02_DIR / "mf_cw.parquet")
    gno = d["chunk"].str.slice(1, 2).cast(pl.Int64)
    return pl.DataFrame({"goal_no": gno, "window": d["chunk"], "method": "H02.gcw_active", "value": d["bJ0"] * d["q"],
                         "se": d["bJ0_null_sd"] * d["q"], "ci_kind": "null_sd", "N": d["N"].cast(pl.Float64),
                         "VR": d["VR"], "q": d["q"], "bJ0": d["bJ0"]})


def ci_se(lo, hi):
    if lo is None or hi is None or not np.isfinite(lo) or not np.isfinite(hi):
        return np.nan
    return max((hi - lo) / 3.92, SE_FLOOR)


def h03_rows() -> pl.DataFrame:
    d = pl.read_parquet(H03_DIR / "period_table.parquet")
    rows = []
    for r in d.iter_rows(named=True):
        boot = r["n_boot_lo"] is not None and r["n_boot_hi"] is not None
        lo, hi = (r["n_boot_lo"], r["n_boot_hi"]) if boot else (r["n_prof_lo"], r["n_prof_hi"])
        m = "H03.n_talk" if r["set"] == "TALK" else "H03.n_all"
        rows.append({"goal_no": r["goal_no"], "window": "period", "method": m, "value": r["n"], "se": ci_se(lo, hi),
                     "lo": lo, "hi": hi, "ci_kind": "day_boot95" if boot else "profile95", "n_days": r["n_days"],
                     "N": r["N_active"]})
        if r["set"] == "TALK":
            lo, hi = r["n_cross_fast_boot_lo"], r["n_cross_fast_boot_hi"]
            rows.append({"goal_no": r["goal_no"], "window": "period", "method": "H03.nx_fast", "value": r["n_cross_fast"],
                         "se": ci_se(lo, hi) if lo is not None else np.nan, "lo": lo, "hi": hi,
                         "ci_kind": "day_boot95", "n_days": r["n_days"], "N": r["N_active"]})
    return pl.DataFrame(rows)


def h03_aux() -> pl.DataFrame:
    """Auxiliary H03 quantities for P3 / P4 (not loop gains in the collapse)."""
    d = pl.read_parquet(H03_DIR / "period_table.parquet").filter(pl.col("set") == "TALK")
    return d.select("goal_no", "N_active", "n_cross_fast", "n_self_fast", "n_c_pair_fast", "n_cross_fast_boot_lo",
                    "n_cross_fast_boot_hi", "tau_cross", "n_B3")


def h04_rows(day_goal: dict) -> pl.DataFrame:
    d = json.loads((C.PROC / "H04-reversible-forcing/explore_placebo_switch.json").read_text())
    sd = {}
    for reg, s in d["adjacent_same_hours"].items():
        for k in ("n", "K"):
            diffs = np.abs(np.array(s[k]["diffs"], dtype=float))
            sd[(reg, k)] = float(1.4826 * np.median(diffs) / np.sqrt(2)) if len(diffs) else np.nan
    rows = []
    for w in d["weeks"]:
        gs = [day_goal.get(x) for x in w["days"]]
        if any(x is None for x in gs):
            continue  # a day outside the non-holdout calendar (should not happen: H04 masked the holdout)
        vals, cnt = np.unique(gs, return_counts=True)
        if cnt.max() / len(gs) < 0.8:
            continue
        g = int(vals[np.argmax(cnt)])
        for k, m in (("n", "H04.n_week"), ("K", "H04.K_week")):
            if w.get(k) is None:
                continue
            rows.append({"goal_no": g, "window": w["week"], "method": m, "value": float(w[k]), "se": sd[(w["regime"], k)],
                         "ci_kind": "adjacent_week_sd", "n_days": len(w["days"])})
    return pl.DataFrame(rows), sd


def load_h05_module():
    p = C.PROC.parent.parent / "hypotheses/H05-rooms-cut/analysis/mf_blocks.py"
    spec = importlib.util.spec_from_file_location("h05_mf_blocks_readonly", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def h05_rows(cal: pl.DataFrame) -> tuple[pl.DataFrame, list]:
    mod = load_h05_module()
    pub = json.loads((C.PROC / "H05-rooms-cut/mf_blocks.json").read_text())["MF1"]
    pdf = pl.read_parquet(C.PROC / "H05-rooms-cut/pair_day_bin1.parquet")
    ad = pl.read_parquet(C.PROC / "H05-rooms-cut/agent_day.parquet")
    ok_days = set(cal["pt_date"].to_list())
    goal = dict(ad.group_by("pt_date").agg(pl.col("goal_no").first()).iter_rows())
    rng = np.random.default_rng(SEED)
    rows, checks = [], []
    for spin in ("talk", "active"):
        for g in (35, 36, 37, 38, 39, 41, 42, 44):
            ds = sorted(d for d in goal if goal[d] == g)
            assert all(d in ok_days for d in ds), f"H05 window #{g} contains a held-out day"
            lab = mod.labels_from_agent_day(ad, ds)
            ai, aj, Rm, Sv, labv = mod.pair_day_arrays(pdf, ds, lab, spin)
            point = mod.block_J(ai, aj, np.nanmean(Rm, 1), np.nanmean(Sv, 1), labv)["loop_gain"]
            bs = []
            for _ in range(NBOOT_H05):
                c = rng.integers(len(ds), size=len(ds))
                bs.append(mod.block_J(ai, aj, np.nanmean(Rm[:, c], 1), np.nanmean(Sv[:, c], 1), labv)["loop_gain"])
            bs = np.array(bs)
            se = float(np.nanstd(bs) * np.sqrt(len(ds) / (len(ds) - 1)))
            checks.append({"spin": spin, "goal_no": g, "recomputed": point, "published": pub[spin][str(g)]["loop_gain"]})
            rows.append({"goal_no": g, "window": "period", "method": f"H05.g2b_{spin}", "value": float(point), "se": se,
                         "lo": float(np.nanpercentile(bs, 2.5)), "hi": float(np.nanpercentile(bs, 97.5)),
                         "ci_kind": "day_boot", "n_days": len(ds), "N": float(len(lab))})
    return pl.DataFrame(rows), checks


def ingest_shared_schema(nonholdout_goals: set[int]) -> pl.DataFrame:
    """Pick up per_period_estimates.parquet written by other hypotheses in the proposed shared schema."""
    req = {"goal_no", "method", "family", "estimand", "value", "se"}
    out = []
    for p in sorted(C.PROC.glob("H*/per_period_estimates.parquet")):
        if p.parent.name.startswith("H19"):
            continue
        d = pl.read_parquet(p)
        if not req <= set(d.columns):
            print(f"  ingest: {p} lacks {req - set(d.columns)}; skipped")
            continue
        d = d.filter(pl.col("goal_no").is_in(list(nonholdout_goals)))
        if "loop_gain" in d.columns:
            d = d.filter(pl.col("loop_gain"))
        hyp = p.parent.name.split("-")[0]
        d = d.with_columns(pl.concat_str([pl.lit(hyp + "."), pl.col("method")]).alias("method"),
                           pl.col("window").fill_null("period") if "window" in d.columns else pl.lit("period").alias("window"))
        out.append(d.select([c for c in ("goal_no", "window", "method", "family", "estimand", "value", "se", "lo", "hi", "n_days")
                             if c in d.columns]))
        print(f"  ingest: {p} -> {d.height} rows")
    return pl.concat(out, how="diagonal_relaxed") if out else pl.DataFrame()


# ----------------------------------------------------------------------------- assemble
def combine(win: pl.DataFrame) -> pl.DataFrame:
    w = win.filter(pl.col("value").is_finite() & pl.col("se").is_finite() & (pl.col("se") > 0))
    w = w.with_columns((1 / pl.col("se") ** 2).alias("w"))
    per = (w.group_by("goal_no", "method")
           .agg(((pl.col("w") * pl.col("value")).sum() / pl.col("w").sum()).alias("value"),
                (1 / pl.col("w").sum().sqrt()).alias("se"), pl.len().alias("n_windows"),
                pl.col("n_days").sum().alias("n_days"), pl.col("N").mean().alias("N_est"),
                pl.col("ci_kind").first().alias("ci_kind")))
    meta = pl.DataFrame([{"method": k, "family": v[0], "estimand": v[1], "primary": v[2], "validation_only": v[3]}
                         for k, v in METHODS.items()])
    per = per.join(meta, on="method", how="left")
    if "family" in win.columns:  # ingested methods carry their own family / estimand
        fam = win.filter(pl.col("family").is_not_null()).select("method", pl.col("family").alias("fam2"),
                                                              pl.col("estimand").alias("est2")).unique("method")
        per = (per.join(fam, on="method", how="left")
               .with_columns(pl.coalesce("family", "fam2").alias("family"), pl.coalesce("estimand", "est2").alias("estimand"),
                             pl.col("primary").fill_null(False), pl.col("validation_only").fill_null(False))
               .drop("fam2", "est2"))
    return per.with_columns(pl.col("goal_no").map_elements(C.pname, return_dtype=pl.Utf8).alias("period")).sort("method", "goal_no")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--stale", default="drop", choices=["drop", "keep"])
    stale = ap.parse_args().stale
    rng = np.random.default_rng(SEED)
    cal = C.calendar_nonholdout()
    C.assert_no_holdout(cal["pt_date"], cal["goal_no"])
    goals = set(cal["goal_no"].unique().to_list())
    day_goal = dict(zip(cal["pt_date"].to_list(), cal["goal_no"].to_list()))
    C.OUT.mkdir(parents=True, exist_ok=True)

    print("H19 own g_eq ...", flush=True)
    if R1B:
        from geq_r1b import own_geq_r1b
        own = own_geq_r1b(cal, rng, bins="fixed")
    else:
        own = own_geq(cal, rng)
    h02 = h02_rows()
    # validation: H19 g_eq vs H02 published on the same chunks
    val = (own.filter(pl.col("method") == "H19.geq_active").select("window", pl.col("value").alias("g_h19"), pl.col("se").alias("se_h19"),
                                                                  pl.col("N").alias("N_h19"))
           .join(h02.select("window", pl.col("value").alias("g_h02"), pl.col("se").alias("se_h02"), pl.col("N").alias("N_h02")),
                 on="window", how="inner"))
    val.write_parquet(C.OUT / "validation_geq_vs_h02.parquet")
    print(f"  validation on {val.height} H02 chunks: max |g_h19 - g_h02| = {np.abs(val['g_h19'] - val['g_h02']).max():.2e}; "
          f"median se_h19/se_h02 = {np.median(val['se_h19'] / val['se_h02']):.2f}", flush=True)

    print("H03, H04, H05 ...", flush=True)
    h03 = h03_rows()
    h04, h04_sd = h04_rows(day_goal)
    if R1B and stale == "drop":
        h04 = h04.filter(pl.col("method") == "H04.n_week")   # K_week is built on the buggy activity_bins
        h05 = pl.DataFrame()
        print("  r1b: H04.K_week and H05 two-block gains dropped (stale activity_bins inputs)", flush=True)
    else:
        h05, h05_checks = h05_rows(cal)
        for c in h05_checks:
            assert abs(c["recomputed"] - c["published"]) < 1e-9, f"H05 recomputation mismatch {c}"
        print(f"  H05 loop gains recomputed = published ({len(h05_checks)} windows); H04 week SDs {h04_sd}", flush=True)
    ing = ingest_shared_schema(goals) if not R1B else pl.DataFrame()

    win = pl.concat([own, h02, h03, h04] + ([h05] if h05.height else []) + ([ing] if ing.height else []), how="diagonal_relaxed")
    win = win.filter(pl.col("goal_no").is_in(list(goals)))
    assert not win.filter(~pl.col("goal_no").is_in(list(goals))).height
    win.write_parquet(C.OUT / "estimates_window.parquet", compression="zstd")
    per = combine(win)
    per.write_parquet(C.OUT / "estimates.parquet", compression="zstd")
    aux = h03_aux().filter(pl.col("goal_no").is_in(list(goals)))
    aux.write_parquet(C.OUT / "h03_aux.parquet", compression="zstd")

    # per-period input records
    ctr = pl.read_parquet(C.CTRL / "controls.parquet")
    for g in sorted(goals):
        d = C.OUT / C.pname(g)
        d.mkdir(parents=True, exist_ok=True)
        rec = {"period": C.pname(g), "controls": ctr.filter(pl.col("goal_no") == g).to_dicts()[0],
               "estimates": per.filter(pl.col("goal_no") == g).drop("goal_no").to_dicts(),
               "windows": win.filter(pl.col("goal_no") == g).drop("goal_no").to_dicts()}
        (d / "inputs.json").write_text(json.dumps(rec, indent=1, default=str))

    C.write_provenance("estimates.parquet", "hypotheses/H19-loop-gain-collapse/scheme/build_estimates.py",
                       [{"source": "ai-village", "revision": C.REVISION,
                         "tables": (["activity_bins_fixed", "outages_fixed/reasons", "outages_fixed/stall_minutes", "calendar"]
                                    if R1B else ["activity_bins", "calendar"])},
                        {"source": str(H02_DIR.relative_to(C.ROOT)), "tables": ["mf_cw.parquet"]},
                        {"source": str(H03_DIR.relative_to(C.ROOT)), "tables": ["period_table.parquet"]},
                        {"source": "data/processed/H04-reversible-forcing", "tables": ["explore_placebo_switch.json"]},
                        {"source": "data/processed/H05-rooms-cut", "tables": ["mf_blocks.json", "pair_day_bin1.parquet", "agent_day.parquet"]}],
                       {"data_version": C.DATA_VERSION, "stale_inputs": stale if R1B else "n/a", "seed": SEED, "nboot_geq": NBOOT_GEQ, "nboot_h05": NBOOT_H05, "se_floor": SE_FLOOR,
                        "h02_rules": {"chunk_days": CHUNK_DAYS, "min_tail_days": MIN_TAIL_DAYS, "min_active_bins": MIN_ACTIVE_BINS,
                                      "block_min": BLOCK_MIN, "min_last_block": MIN_LAST_BLOCK, "min_block_n": MIN_BLOCK_N},
                        "h04_week_assignment": ">= 80% of the week's days in one period", "h04_week_sd": {f"{k[0]}:{k[1]}": v for k, v in h04_sd.items()},
                        "methods": {k: v[4] for k, v in METHODS.items()}})
    with pl.Config(tbl_rows=40, tbl_cols=20, tbl_width_chars=220):
        print(per.group_by("method").agg(pl.len().alias("n_periods"), pl.col("value").median().alias("median"),
                                         pl.col("value").min().alias("min"), pl.col("value").max().alias("max"),
                                         pl.col("se").median().alias("median_se")).sort("method"))


if __name__ == "__main__":
    main()
