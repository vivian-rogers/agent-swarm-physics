"""H35 round 1b (improved data, 2026-10-04): work bought per nudge on glance, sustained and work-commit outcomes.

The round-1 grids (scheme/build.py: leading-@ targets, h16lib active rows from events_core + actions; activity_bins
is not used, so its event-drop bug does not touch H35) get new outcome columns, written to
data/processed/H35-nudger-maxwell-demon/<period>/r1b/grid_outcomes.parquet:
  y_glance30  any active row in minutes m+1..m+30 (= y30 > 0)
  y_sust30    a run of >= 3 consecutive active DQ1 ledger calls starts in m+1..m+30 (H43's sustained escape)
  y_work30/60 DQ4 agent work commits (canonical & ~imported & agent & ~automated) in m+1..m+30 / m+1..m+60
  *_pre       the same in the placebo window m-30..m-16
Then, per period: past-only first-nudge ATT on every outcome (round-1 strata and day-block CIs), the minute-level
trap-age efficiency (eta_SU, eta_KW, kappa, once-early ratio) per outcome, and for gate periods the gate model refit on
a sustained escape (a sustained run starting within 15 min of the gate). Native tests NE10, NE43 on the work ledger.
Writes <period>/r1b/results_r1b.json and r1b/r1b_summary.json. Non-holdout only.

Usage: uv run python hypotheses/H35-nudger-maxwell-demon/analysis/r1b_outcomes.py [--B 200]
       ... r1b_outcomes.py --did   (post hoc rate difference-in-differences; results_r1b_did.json)
"""
from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h35lib as L  # noqa: E402
from h35lib import h16lib  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

_spec = importlib.util.spec_from_file_location("h35_run_period", HERE / "run_period.py")  # avoid h16lib path collision
RP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(RP)

PERIODS = ["G51", "G38", "G41", "G37", "G39", "G40", "G42", "G44", "G30", "G31", "G33", "G35", "G36", "G51off"]
GATE_PERIODS = ["G51", "G38", "G41"]
ACTIVE_KINDS = ["cu_action", "talk", "search", "room_move", "request"]
OUTCOMES = ["y30", "y_glance30", "y_sust30", "y_work30", "y_work60"]
R1B = L.OUT / "r1b"
T0 = time.time()


def log(m):
    print(f"[{time.time() - T0:6.1f}s] {m}", flush=True)


def load_sources():
    led = (pl.scan_parquet(L.SH / "context_ledger_turns.parquet").filter(~pl.col("holdout"))
           .select("agent", "pt_date", "t_first", "kind").collect()
           .with_columns(pl.col("kind").cast(pl.Utf8).is_in(ACTIVE_KINDS).alias("act"),
                         (pl.col("t_first").dt.epoch("us") / 1e6).alias("ts"))
           .sort("agent", "pt_date", "ts"))
    # run starts: first call of a maximal run of active calls of length >= 3
    led = led.with_columns((pl.col("act") != pl.col("act").shift(1).over("agent", "pt_date")).fill_null(True).alias("brk"))
    led = led.with_columns(pl.col("brk").cast(pl.Int32).cum_sum().over("agent", "pt_date").alias("run"))
    runs = (led.filter(pl.col("act")).group_by("agent", "pt_date", "run")
            .agg(pl.len().alias("n"), pl.col("ts").min().alias("t_start")).filter(pl.col("n") >= 3))
    sust = {(int(a), d): np.sort(g["t_start"].to_numpy()) for (a, d), g in runs.group_by(["agent", "pt_date"])}
    wc = (pl.read_parquet(L.SH / "work_commits.parquet", columns=["t", "pt_date", "author_agent", "author_kind", "canonical",
                                                                   "imported", "automated", "holdout"])
          .filter(pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind") == "agent") & ~pl.col("automated")
                  & ~pl.col("holdout") & pl.col("author_agent").is_not_null())
          .with_columns((pl.col("t").dt.epoch("us") / 1e6).alias("ts")))
    work = {(int(a), d): np.sort(g["ts"].to_numpy()) for (a, d), g in wc.group_by(["author_agent", "pt_date"])}
    return sust, work, wc


def add_outcomes(grid: pl.DataFrame, W: dict, sust: dict, work: dict) -> pl.DataFrame:
    parts = []
    for (a, d), g in grid.group_by(["agent", "pt_date"], maintain_order=True):
        a, t0, t1 = int(a), W[d]["t0"], W[d]["t1"]
        n_min = int(np.ceil((t1 - t0) / 60.0))
        m = g["minute"].to_numpy().astype(int)

        def counts(arr):
            if arr is None or len(arr) == 0:
                return np.zeros(n_min + 1)
            q = np.floor((arr - t0) / 60.0).astype(int)
            q = q[(q >= 0) & (q < n_min)]
            return np.r_[0, np.cumsum(np.bincount(q, minlength=n_min))].astype(float)

        cs, cw = counts(sust.get((a, d))), counts(work.get((a, d)))
        hi30 = np.clip(m + 31, 0, n_min)
        hi60 = m + 61
        lo1 = np.clip(m + 1, 0, n_min)
        pre_lo, pre_hi = np.clip(m - 30, 0, n_min), np.clip(m - 15, 0, n_min)
        w60 = np.where(hi60 <= n_min, cw[np.clip(hi60, 0, n_min)] - cw[lo1], np.nan)
        parts.append(pl.DataFrame({
            "agent": g["agent"], "pt_date": g["pt_date"], "minute": g["minute"],
            "y_glance30": (g["y30"].to_numpy() > 0).astype(np.int8),
            "y_sust30": ((cs[hi30] - cs[lo1]) > 0).astype(np.int8),
            "y_work30": (cw[hi30] - cw[lo1]).astype(np.int16),
            "y_work60": w60.astype(np.float32),
            "y_glance_pre": (g["ypre"].to_numpy() > 0).astype(np.int8),
            "y_sust_pre": ((cs[pre_hi] - cs[pre_lo]) > 0).astype(np.int8),
            "y_work_pre": (cw[pre_hi] - cw[pre_lo]).astype(np.int16)}))
    return pl.concat(parts)


PRE = {"y30": "ypre", "y_glance30": "y_glance_pre", "y_sust30": "y_sust_pre", "y_work30": "y_work_pre", "y_work60": "y_work_pre"}


def designs(df):
    M = df["M"].to_numpy() > 0
    past, dirnow = df["past_dir"].to_numpy(), df["dir_now"].to_numpy()
    return {"first": M & (past == 0) & (dirnow == 0), "repeat": M & (df["past_n60"].to_numpy() > 0) & (dirnow == 0),
            "ctrl": (~M) & (past == 0) & (dirnow == 0)}


def att_block(df, rng, B):
    D = designs(df)
    days = df["pt_date"].to_numpy()
    out, resid = {}, {}
    for y in OUTCOMES:
        ok = df[y].is_not_null().to_numpy() & np.isfinite(df[y].cast(pl.Float64).fill_null(np.nan).to_numpy())
        sub = df.filter(pl.Series(ok))
        Ds = {k: v[ok] for k, v in D.items()}
        dsub = days[ok]
        r = L.matched_att(sub, Ds["first"], Ds["ctrl"], y)
        rp = L.matched_att(sub, Ds["first"], Ds["ctrl"], PRE[y])
        rr = L.matched_att(sub, Ds["repeat"], Ds["ctrl"], y)
        ctrl_mean = float(sub[y].cast(pl.Float64).to_numpy()[Ds["ctrl"]].mean()) if Ds["ctrl"].any() else float("nan")
        out[y] = {"first": L.day_boot_mean(r["resid"], dsub[r["idx"]], rng, B), "n_first": int(len(r["idx"])),
                  "placebo": L.day_boot_mean(rp["resid"], dsub[rp["idx"]], rng, B),
                  "repeat": L.day_boot_mean(rr["resid"], dsub[rr["idx"]], rng, B), "n_repeat": int(len(rr["idx"])),
                  "control_mean": ctrl_mean}
        # map residual indices back to the full grid rows (for the trap-age efficiency)
        full_idx = np.flatnonzero(ok)[r["idx"]]
        resid[y] = (full_idx, r["resid"])
    return out, resid


def k_eff(df, resid, rng):
    out = {}
    for y, (idx, res) in resid.items():
        try:
            e = RP.minute_k_efficiency(df, {"first_pastonly": {"_idx": idx, "_resid": res}}, rng, B=500)
        except Exception as ex:  # too few first nudges per bin
            e = {"error": repr(ex)}
        if "g_shrunk" in e and e.get("V_log_per_nudge"):
            e["ratio_k23_vs_logged"] = float(e["g_shrunk"][2] / e["V_log_per_nudge"])
        out[y] = e
    return out


def gate_sustained(gates: pl.DataFrame, sust: dict, rng, B: int) -> dict:
    """Gate model refit with escape := a sustained run starts within [t_gate - 60 s, t_gate + 15 min)."""
    es = []
    for a, d, tg, oc in gates.select("agent", "pt_date", "t_gate", "outcome_r").iter_rows():
        arr = sust.get((int(a), d))
        if oc == "censored" or tg is None or not np.isfinite(tg):
            es.append(0)
            continue
        hit = arr is not None and len(arr) and np.any((arr >= tg - 60) & (arr < tg + 900))
        es.append(int(bool(hit)))
    g2 = gates.with_columns(pl.Series("escape_glance", gates["escape"]), pl.Series("escape", es, dtype=pl.Int8))
    blk = RP.gate_block(g2, rng, B)
    blk["share_sustained_escape"] = float(np.mean([e for e, o in zip(es, gates["outcome_r"].to_list()) if o != "censored"]))
    blk["share_glance_escape"] = float(gates.filter(pl.col("outcome_r") != "censored")["escape"].mean())
    return blk


def day_contrast_null(daily: pl.DataFrame, target_day: str, k: int = 3) -> dict:
    """log(1 + commits per active agent) on target_day minus the mean of its k previous active days in the same unit,
    vs the same contrast at every other eligible day (#30-#44 + #51 non-holdout)."""
    obs, null = None, []
    for u, g in daily.group_by("unit"):
        g = g.sort("pt_date")
        v = np.log1p(g["cpa"].to_numpy())
        ds = g["pt_date"].to_list()
        for i in range(k, len(v)):
            c = float(v[i] - v[i - k:i].mean())
            if ds[i] == target_day:
                obs = c
            else:
                null.append(c)
    null = np.array(null)
    return {"obs": obs, "null_mean": float(null.mean()), "null_sd": float(null.std(ddof=1)), "n_null": int(len(null)),
            "z": float((obs - null.mean()) / null.std(ddof=1)) if obs is not None else None}


def run_did(sust: dict, work: dict, rng, B: int):
    """POST HOC (2026-10-04, after the first round-1b run showed non-zero placebos for sustained runs and work commits):
    rate difference-in-differences per epoch, (post count / post minutes - placebo count / 15) x 60, for sustained-run
    starts (post 30 min) and work commits (post 60 min). Same matched past-only design; then the trap-age efficiency."""
    out = {}
    for p in ("G51", "G38", "G41", "G30"):
        d = L.OUT / p
        grid = pl.read_parquet(d / "grid.parquet")
        days = sorted(grid["pt_date"].unique().to_list())
        h16lib.assert_no_holdout(days)
        W = h16lib.windows(days)
        parts = []
        for (a, dd), g in grid.group_by(["agent", "pt_date"], maintain_order=True):
            a, t0, t1 = int(a), W[dd]["t0"], W[dd]["t1"]
            n_min = int(np.ceil((t1 - t0) / 60.0))
            m = g["minute"].to_numpy().astype(int)

            def cum(arr):
                if arr is None or len(arr) == 0:
                    return np.zeros(n_min + 1)
                q = np.floor((arr - t0) / 60.0).astype(int)
                q = q[(q >= 0) & (q < n_min)]
                return np.r_[0, np.cumsum(np.bincount(q, minlength=n_min))].astype(float)
            cs, cw = cum(sust.get((a, dd))), cum(work.get((a, dd)))
            lo1 = np.clip(m + 1, 0, n_min)
            pre = lambda c: c[np.clip(m - 15, 0, n_min)] - c[np.clip(m - 30, 0, n_min)]  # noqa: E731
            s_post = cs[np.clip(m + 31, 0, n_min)] - cs[lo1]
            w_post = np.where(m + 61 <= n_min, cw[np.clip(m + 61, 0, n_min)] - cw[lo1], np.nan)
            parts.append(pl.DataFrame({"agent": g["agent"], "pt_date": g["pt_date"], "minute": g["minute"],
                                       "sust_did_h": (s_post / 30 - pre(cs) / 15) * 60,
                                       "work_did_h": (w_post / 60 - pre(cw) / 15) * 60,
                                       "sust_rate_h": s_post / 30 * 60, "work_rate_h": w_post / 60 * 60}))
        df = grid.join(pl.concat(parts), on=["agent", "pt_date", "minute"], how="left")
        Ds = designs(df)
        days_a = df["pt_date"].to_numpy()
        res = {}
        for y in ("sust_did_h", "work_did_h", "sust_rate_h", "work_rate_h"):
            ok = np.isfinite(df[y].fill_null(np.nan).to_numpy())
            sub = df.filter(pl.Series(ok))
            D2 = {k: v[ok] for k, v in Ds.items()}
            r = L.matched_att(sub, D2["first"], D2["ctrl"], y)
            res[y] = {"first": L.day_boot_mean(r["resid"], days_a[ok][r["idx"]], rng, B), "n_first": int(len(r["idx"]))}
            if p == "G51" and y.endswith("did_h"):
                full_idx = np.flatnonzero(ok)[r["idx"]]
                try:
                    e = RP.minute_k_efficiency(df, {"first_pastonly": {"_idx": full_idx, "_resid": r["resid"]}}, rng, B=500)
                    if "g_shrunk" in e and e.get("V_log_per_nudge"):
                        e["ratio_k23_vs_logged"] = float(e["g_shrunk"][2] / e["V_log_per_nudge"])
                except Exception as ex:
                    e = {"error": repr(ex)}
                res[y]["k_eff"] = e
        out[p] = res
        L.jdump(res, d / "r1b" / "results_r1b_did.json")
        log(f"did {p}: done")
    return out


def main():
    args = sys.argv[1:]
    if "--did" in args:
        sust, work, _ = load_sources()
        run_did(sust, work, np.random.default_rng(L.SEED + 8), int(args[args.index("--B") + 1]) if "--B" in args else 200)
        return
    B = int(args[args.index("--B") + 1]) if "--B" in args else 200
    rng = np.random.default_rng(L.SEED + 7)
    sust, work, wc = load_sources()
    log(f"sources: {sum(len(v) for v in sust.values())} sustained-run starts, {wc.height} work commits")
    summary = {}
    for p in PERIODS:
        d = L.OUT / p
        if not (d / "grid.parquet").exists():
            continue
        grid = pl.read_parquet(d / "grid.parquet")
        days = sorted(grid["pt_date"].unique().to_list())
        h16lib.assert_no_holdout(days)
        W = h16lib.windows(days)
        add = add_outcomes(grid, W, sust, work)
        (d / "r1b").mkdir(exist_ok=True)
        add.write_parquet(d / "r1b" / "grid_outcomes.parquet", compression="zstd")
        df = grid.join(add, on=["agent", "pt_date", "minute"], how="left")
        res = {"period": p, "n_epochs": df.height, "nudge_epochs": int(df["M"].sum()),
               "work_commits_in_period": int(wc.filter(pl.col("pt_date").is_in(days)).height)}
        if df["M"].sum() >= 3:
            att, resid = att_block(df, rng, B)
            res["att"] = att
            if p in ("G51", "G38", "G41"):
                res["k_eff"] = k_eff(df, resid, rng)
            if p in GATE_PERIODS and (d / "gates.parquet").exists():
                gates = pl.read_parquet(d / "gates.parquet")
                if gates["M"].sum() >= 5:
                    try:
                        res["gate_sustained"] = gate_sustained(gates, sust, rng, B)
                    except Exception as ex:
                        res["gate_sustained"] = {"error": repr(ex)}
            n_nudges = int(df["M"].sum())
            wa = att["y_work60"]["first"][0]
            res["accounting_work"] = {"nudges": n_nudges, "first_att_work60": wa,
                                      "share_of_period_commits": (wa * n_nudges / res["work_commits_in_period"])
                                      if res["work_commits_in_period"] else None}
        L.jdump(res, d / "r1b" / "results_r1b.json")
        summary[p] = res
        log(f"{p}: done")
    # ---------------------------------------------------------------- natives on the work ledger (swarm level)
    cal = pl.read_parquet(L.SH / "calendar.parquet").select("pt_date", "goal_no", "holdout", "n_agent_events")
    ad = (pl.read_parquet(L.SH / "work_daily.parquet").filter((pl.col("level") == "agent") & pl.col("active") & ~pl.col("holdout"))
          .select("pt_date", "agent", "goal_no", "commits"))
    daily = (ad.filter(((pl.col("goal_no") >= 30) & (pl.col("goal_no") <= 44)) | (pl.col("goal_no") == 51))
             .group_by("pt_date", "goal_no").agg(pl.col("commits").mean().alias("cpa"), pl.len().alias("n_active"))
             .with_columns(pl.col("goal_no").cast(pl.Utf8).alias("unit")).sort("pt_date"))
    h16lib.assert_no_holdout(daily["pt_date"].to_list())
    nat = {"NE10": day_contrast_null(daily, "2026-02-13")}
    d51 = daily.filter(pl.col("goal_no") == "51" if daily["goal_no"].dtype == pl.Utf8 else pl.col("goal_no") == 51).sort("pt_date")

    def window(a, b):
        g = d51.filter((pl.col("pt_date") >= a) & (pl.col("pt_date") <= b))
        return np.log1p(g["cpa"].to_numpy()), g["pt_date"].to_list()
    pre2, _ = window("2026-08-10", "2026-08-20")
    post2, dpost = window("2026-08-21", "2026-09-02")
    pre1, _ = window("2026-07-29", "2026-08-04")
    post1, _ = window("2026-08-05", "2026-08-11")
    sd51 = float(np.std(np.log1p(d51.filter(pl.col("pt_date") <= "2026-08-20")["cpa"].to_numpy()), ddof=1))
    g51 = summary.get("G51", {})
    acc = g51.get("accounting_work", {})
    days51 = d51.filter((pl.col("pt_date") >= "2026-07-06") & (pl.col("pt_date") <= "2026-08-20"))
    nat["NE43"] = {"step2_nudger_off": {"pre_mean": float(pre2.mean()), "post_mean": float(post2.mean()),
                                        "delta": float(post2.mean() - pre2.mean()), "n_pre": len(pre2), "n_post": len(post2),
                                        "day_sd": sd51, "delta_in_day_sd": float((post2.mean() - pre2.mean()) / sd51)},
                   "step1_bookends_off": {"pre_mean": float(pre1.mean()), "post_mean": float(post1.mean()),
                                          "delta": float(post1.mean() - pre1.mean()), "n_pre": len(pre1), "n_post": len(post1),
                                          "delta_in_day_sd": float((post1.mean() - pre1.mean()) / sd51)},
                   "accounting_share_of_work": acc.get("share_of_period_commits"),
                   "nudges_per_day_G51": (acc.get("nudges") or 0) / max(1, days51.height)}
    nat["NE43"]["N1"] = bool(abs(nat["NE43"]["step2_nudger_off"]["delta_in_day_sd"]) < 2
                             and (acc.get("share_of_period_commits") is None or acc["share_of_period_commits"] <= 0.01))
    nat["NE43"]["N2"] = bool(abs(nat["NE43"]["step1_bookends_off"]["delta_in_day_sd"]) < 2)
    nat["NE10"]["N1"] = bool(nat["NE10"]["z"] is not None and abs(nat["NE10"]["z"]) < 2)
    summary["natives"] = nat
    R1B.mkdir(parents=True, exist_ok=True)
    L.jdump({"natives": nat, "periods": {p: {k: v for k, v in r.items() if k in ("att", "accounting_work", "n_epochs", "nudge_epochs")}
                                         for p, r in summary.items() if p != "natives"}}, R1B / "r1b_summary.json")
    L.write_provenance(R1B, "hypotheses/H35-nudger-maxwell-demon/analysis/r1b_outcomes.py",
                       ["H35 round-1 grids and gates", "context_ledger_turns (active-call runs)", "work_commits", "work_daily",
                        "calendar"],
                       {"B": B, "active_kinds": ACTIVE_KINDS, "sustained": ">= 3 consecutive active ledger calls",
                        "work": "canonical & ~imported & author_kind=='agent' & ~automated", "seed": L.SEED + 7})
    log("done")


if __name__ == "__main__":
    main()
