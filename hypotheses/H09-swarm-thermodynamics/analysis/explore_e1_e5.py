"""H09 exploratory measurements E1-E5 on NON-HOLDOUT windows only.

Reads data/processed/shared/*. Writes figures to ../figures/ and a JSON of numbers to
data/processed/H09-swarm-thermodynamics/explore_e1_e5.json.

Usage: uv run python hypotheses/H09-swarm-thermodynamics/analysis/explore_e1_e5.py
Round 1b (2026-10-04): H09_DATA=r1b reads activity_bins_fixed (activity_bins dropped ~half of all events, DQ8), also
masks days with infra holdout_mask, adds a trimmed E1 (each day cut to its all-present window, the DQ8 / H38 rule
for synchrony statistics) and writes to data/processed/H09-swarm-thermodynamics/r1b/; figures get an r1b_ prefix.
H09_DATA=r1 (default) reproduces round 1. E2-E4 read events_core only, so they do not change.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import polars as pl

import os  # noqa: E402
import sys  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
SH = ROOT / "data/processed/shared"
DATA_VERSION = os.environ.get("H09_DATA", "r1")
assert DATA_VERSION in ("r1", "r1b"), DATA_VERSION
OUTD = ROOT / "data/processed/H09-swarm-thermodynamics" / ("" if DATA_VERSION == "r1" else "r1b")
BINS = "activity_bins.parquet" if DATA_VERSION == "r1" else "activity_bins_fixed.parquet"
FIG = Path(__file__).resolve().parents[1] / "figures"
FP = "" if DATA_VERSION == "r1" else "r1b_"
OUTD.mkdir(parents=True, exist_ok=True); FIG.mkdir(parents=True, exist_ok=True)
RNG = np.random.default_rng(20261003)
plt.rcParams.update({"font.family": "serif", "font.size": 7, "axes.linewidth": 0.5, "pdf.fonttype": 42})

cal = pl.read_parquet(SH / "calendar.parquet")
keep_days = cal.filter(~pl.col("holdout")).select("pt_date", "regime", "gap_before_s", "weekday", "window_s")
if DATA_VERSION == "r1b":
    sys.path.insert(0, str(ROOT / "infra/shared"))
    from common import holdout_mask  # noqa: E402
    _c = cal.filter(~pl.col("holdout"))
    _hm = holdout_mask(_c["pt_date"].to_list(), _c["goal_no"].to_list())
    keep_days = keep_days.filter(~pl.Series(_hm))
roster = pl.read_parquet(SH / "roster.parquet")
results: dict = {"holdout_excluded_days": int(cal["holdout"].sum()), "days_used": keep_days.height}

CLASS = {"AGENT_TALK": "talk", "WAIT": "wait", "PAUSE": "pause", "CONSOLIDATE": "consolidate",
         "START_USING_COMPUTER": "start_cu", "STOP_USING_COMPUTER": "stop_cu", "SEARCH_HISTORY": "search"}

# ------------------------------------------------------------------ E1: activity landscape
bins = (pl.read_parquet(SH / BINS, columns=["pt_date", "minute", "agent", "state"])
        .join(keep_days.select("pt_date", "regime"), on="pt_date"))
bins = bins.with_columns((pl.col("state") >= 3).cast(pl.Int8).alias("on"),
                         (pl.col("minute") // 30).alias("block"))
# independent-agent null with a time-varying field: p_i(day, 30-min block)
p = bins.group_by("pt_date", "block", "agent").agg(pl.col("on").mean().alias("p"))
b = bins.join(p, on=["pt_date", "block", "agent"])
per_min = b.group_by("pt_date", "minute", "regime").agg(pl.col("on").sum().alias("K"), pl.len().alias("N"),
                                                        (pl.col("p") * (1 - pl.col("p"))).sum().alias("var_ind"),
                                                        pl.col("p").sum().alias("mean_ind"))
day = per_min.group_by("pt_date", "regime").agg(pl.col("K").var().alias("varK"), pl.col("var_ind").mean().alias("var_ind"),
                                                pl.col("N").median().alias("N"))
day = day.filter(pl.col("var_ind") > 0).with_columns((pl.col("varK") / pl.col("var_ind")).alias("VR"))
e1 = {}
for reg in ("I", "II", "III"):
    d = day.filter(pl.col("regime") == reg)["VR"].drop_nulls().to_numpy()
    if len(d):
        e1[reg] = {"days": int(len(d)), "VR_median": float(np.median(d)), "VR_iqr": [float(np.percentile(d, 25)), float(np.percentile(d, 75))],
                   "frac_days_VR_gt_1.5": float(np.mean(d > 1.5))}
results["E1_variance_ratio_vs_independent_with_halfhour_field"] = e1
if DATA_VERSION == "r1b":
    # trimmed E1: per day keep the all-present window [max first-active minute, min last-active minute]
    span = (bins.filter(pl.col("on") == 1).group_by("pt_date", "agent").agg(pl.col("minute").min().alias("m0"), pl.col("minute").max().alias("m1"))
            .group_by("pt_date").agg(pl.col("m0").max().alias("lo"), pl.col("m1").min().alias("hi")))
    act_agents = bins.filter(pl.col("on") == 1).select("pt_date", "agent").unique()
    bt = (bins.join(act_agents, on=["pt_date", "agent"]).join(span, on="pt_date")
          .filter((pl.col("minute") >= pl.col("lo")) & (pl.col("minute") <= pl.col("hi"))))
    pt = bt.group_by("pt_date", "block", "agent").agg(pl.col("on").mean().alias("p"))
    pmt = (bt.join(pt, on=["pt_date", "block", "agent"]).group_by("pt_date", "minute", "regime")
           .agg(pl.col("on").sum().alias("K"), (pl.col("p") * (1 - pl.col("p"))).sum().alias("var_ind")))
    dayt = (pmt.group_by("pt_date", "regime").agg(pl.col("K").var().alias("varK"), pl.col("var_ind").mean().alias("var_ind"), pl.len().alias("L"))
            .filter((pl.col("var_ind") > 0) & (pl.col("L") >= 60)).with_columns((pl.col("varK") / pl.col("var_ind")).alias("VR")))
    e1t = {}
    for reg in ("I", "II", "III"):
        d = dayt.filter(pl.col("regime") == reg)["VR"].drop_nulls().to_numpy()
        if len(d):
            e1t[reg] = {"days": int(len(d)), "VR_median": float(np.median(d)), "VR_iqr": [float(np.percentile(d, 25)), float(np.percentile(d, 75))],
                        "frac_days_VR_gt_1.5": float(np.mean(d > 1.5))}
    results["E1_trimmed_all_present_window"] = e1t
    results["E1_per_day"] = day.join(dayt.select("pt_date", pl.col("VR").alias("VR_trim")), on="pt_date", how="left").sort("pt_date").to_dicts()
# landscape G(K) = -ln P(K) at each regime's most common roster size N (integer K avoids binning artifacts)
fig, ax = plt.subplots(1, 1, figsize=(3.3, 2.2))
e1_land = {}
for reg, col in (("I", "#3f6fb5"), ("III", "#c2662d")):
    pr = per_min.filter(pl.col("regime") == reg)
    n_mode = int(pr.group_by("N").len().sort("len", descending=True)["N"][0])
    pm = pr.filter(pl.col("N") == n_mode)
    K = pm["K"].to_numpy(); Ks = np.arange(n_mode + 1)
    P = np.bincount(K, minlength=n_mode + 1) / len(K)
    mu, var = pm["mean_ind"].to_numpy(), pm["var_ind"].to_numpy()
    Kn = np.clip(np.rint(RNG.normal(mu, np.sqrt(np.maximum(var, 1e-9)))), 0, n_mode).astype(int)
    Pn = np.bincount(Kn, minlength=n_mode + 1) / len(Kn)
    ok, okn = P > 0, Pn > 0
    ax.plot(Ks[ok] / n_mode, -np.log(P[ok]), "-o", ms=2, color=col, lw=0.8, label=f"regime {reg}, N={n_mode} ({len(K):,} min)")
    ax.plot(Ks[okn] / n_mode, -np.log(Pn[okn]), "--", color=col, lw=0.8, alpha=0.7, label=f"regime {reg}, independent null")
    e1_land[reg] = {"N": n_mode, "minutes": int(len(K))}
results["E1_landscape_N"] = e1_land
ax.set_xlabel("fraction of agents active per minute, K/N"); ax.set_ylabel(r"$G(K)=-\ln P(K)$")
ax.legend(frameon=False, fontsize=5.5); fig.tight_layout(); fig.savefig(FIG / f"{FP}E1_activity_landscape.pdf"); plt.close(fig)

# ------------------------------------------------------------------ E2: currents in action-class space
ev = (pl.read_parquet(SH / "events_core.parquet", columns=["event_index", "t", "pt_date", "regime", "actor_kind", "agent", "action_type"])
      .filter((pl.col("actor_kind") == "agent") & pl.col("agent").is_not_null())
      .join(keep_days.select("pt_date"), on="pt_date")
      .with_columns(pl.col("action_type").cast(pl.Utf8).replace_strict(CLASS, default="other").alias("cls"))
      .sort("agent", "event_index"))
classes = sorted(set(CLASS.values()) | {"other"}); ci = {c: i for i, c in enumerate(classes)}


def ep_rate(seq):
    n = np.zeros((len(classes), len(classes)))
    for a, b2 in zip(seq[:-1], seq[1:]):
        n[a, b2] += 1
    tot = n.sum()
    s = 0.0
    for i in range(len(classes)):
        for j in range(len(classes)):
            if i != j and n[i, j] > 0 and n[j, i] > 0:
                s += (n[i, j] / tot) * math.log(n[i, j] / n[j, i])
    return s, n


e2 = []
flux_total = np.zeros((len(classes), len(classes)))
for (a, reg), g in ev.group_by(["agent", "regime"]):
    seq = [ci[c] for c in g["cls"].to_list()]
    if len(seq) < 300:
        continue
    s, n = ep_rate(seq)
    null = [ep_rate(list(RNG.permutation(seq)))[0] for _ in range(20)]
    e2.append({"agent": int(a), "regime": reg, "n": len(seq), "ep_per_step": s, "null_p95": float(np.percentile(null, 95))})
    if reg == "III":
        flux_total += n - n.T
results["E2_entropy_production"] = {
    "agent_regime_cells": len(e2),
    "frac_cells_above_null_p95": float(np.mean([r["ep_per_step"] > r["null_p95"] for r in e2])) if e2 else None,
    "median_ep_per_step": {reg: float(np.median([r["ep_per_step"] for r in e2 if r["regime"] == reg]))
                           for reg in ("I", "II", "III") if any(r["regime"] == reg for r in e2)}}
top = sorted(((flux_total[i, j], classes[i], classes[j]) for i in range(len(classes)) for j in range(len(classes)) if flux_total[i, j] > 0), reverse=True)[:6]
results["E2_regime_III_top_net_fluxes"] = [{"from": f, "to": t, "net": float(x)} for x, f, t in top]

# ------------------------------------------------------------------ E3: ergodicity breaking
daymix = (ev.group_by("agent", "pt_date", "regime").agg(*[(pl.col("cls") == c).mean().alias(c) for c in classes], pl.len().alias("n"))
          .filter(pl.col("n") >= 20))
labs = dict(zip(roster["agent"].to_list(), roster["lab"].to_list()))
e3 = {}
for reg in ("I", "III"):
    dm = daymix.filter(pl.col("regime") == reg)
    out = {}
    for c in ("talk", "wait", "pause", "consolidate", "start_cu", "search"):
        per_agent = dm.group_by("agent").agg(pl.col(c).mean().alias("m"), pl.col(c).var().alias("v"), pl.len().alias("days")).filter(pl.col("days") >= 5)
        if per_agent.height < 3:
            continue
        between = float(per_agent["m"].var()); within = float(per_agent["v"].mean())
        # share of between-agent variance explained by lab (one-way ANOVA on agent means)
        pa = per_agent.with_columns(pl.col("agent").replace_strict(labs, default="?").alias("lab"))
        grand = pa["m"].mean()
        ss_tot = float(((pa["m"] - grand) ** 2).sum())
        ss_lab = float(pa.group_by("lab").agg(pl.col("m").mean().alias("lm"), pl.len().alias("k")).select(((pl.col("lm") - grand) ** 2 * pl.col("k")).sum()).item())
        out[c] = {"between_over_within": between / within if within else None, "lab_share": ss_lab / ss_tot if ss_tot else None, "agents": per_agent.height}
    e3[reg] = out
results["E3_ergodicity"] = e3

# ------------------------------------------------------------------ E4: idle traps and the nudger
evt = ev.select("agent", "t", "cls", "pt_date")
evt = evt.with_columns(pl.col("cls").is_in(["wait", "pause"]).alias("idle"))
evt = evt.with_columns((pl.col("idle") != pl.col("idle").shift(1).over("agent")).fill_null(True).cum_sum().over("agent").alias("run"))
runs = (evt.group_by("agent", "run").agg(pl.col("idle").first(), pl.col("t").min().alias("t0"), pl.col("pt_date").first())
        .sort("agent", "t0").with_columns(pl.col("t0").shift(-1).over("agent").alias("t_next"),
                                          pl.col("pt_date").shift(-1).over("agent").alias("d_next")))
dw = runs.filter(pl.col("idle") & (pl.col("pt_date") == pl.col("d_next"))).with_columns(
    ((pl.col("t_next") - pl.col("t0")).dt.total_seconds()).alias("dwell_s"))
d = dw["dwell_s"].to_numpy()
results["E4_idle_dwell"] = {"n_runs": int(len(d)), "mean_s": float(d.mean()), "median_s": float(np.median(d)),
                            "cv": float(d.std() / d.mean()), "p90_s": float(np.percentile(d, 90))}
ne10 = "2026-02-10"
def window(s, e):
    w = dw.filter((pl.col("pt_date") >= s) & (pl.col("pt_date") < e))["dwell_s"].to_numpy()
    idle_frac = ev.filter((pl.col("pt_date") >= s) & (pl.col("pt_date") < e)).select(pl.col("cls").is_in(["wait", "pause"]).mean()).item()
    return {"runs": int(len(w)), "mean_dwell_s": float(w.mean()) if len(w) else None, "idle_event_frac": float(idle_frac) if idle_frac is not None else None}
results["E4_nudger_on_NE10"] = {"before_2wk": window("2026-01-27", ne10), "after_2wk": window(ne10, "2026-02-23")}
fig, ax = plt.subplots(figsize=(3.3, 2.2))
x = np.sort(d); ccdf = 1 - np.arange(len(x)) / len(x)
ax.loglog(x, ccdf, lw=0.8, color="#3a7d6b", label="idle dwell (data)")
ax.loglog(x, np.exp(-x / d.mean()), "--", lw=0.8, color="0.4", label="exponential, same mean")
ax.set_ylim(1e-5, 1.5); ax.set_xlabel("idle run duration (s)"); ax.set_ylabel("P(dwell > t)"); ax.legend(frameon=False, fontsize=6)
fig.tight_layout(); fig.savefig(FIG / f"{FP}E4_idle_dwell_ccdf.pdf"); plt.close(fig)

# ------------------------------------------------------------------ E5: daily restarts
pm = per_min.join(keep_days.select("pt_date", "gap_before_s", "weekday"), on="pt_date").with_columns((pl.col("K") / pl.col("N")).alias("k"))
curves = {}
for label, cond in (("overnight (<30 h gap)", pl.col("gap_before_s") < 30 * 3600), ("weekend (>48 h gap)", pl.col("gap_before_s") > 48 * 3600)):
    c = pm.filter(cond & (pl.col("minute") < 180)).group_by("minute").agg(pl.col("k").mean()).sort("minute")
    curves[label] = (c["minute"].to_numpy(), c["k"].to_numpy())
def half_time(m, k):
    plateau = np.median(k[(m >= 90) & (m < 180)]); start = k[0]
    target = start + 0.5 * (plateau - start)
    idx = np.argmax((k >= target) if plateau >= start else (k <= target))
    return float(m[idx]), float(plateau)
results["E5_restart_half_time_min"] = {lab: dict(zip(("half_time_min", "plateau_k"), half_time(*v))) for lab, v in curves.items()}
fig, ax = plt.subplots(figsize=(3.3, 2.2))
for (lab, (m, k)), col in zip(curves.items(), ("#3f6fb5", "#c2662d")):
    ax.plot(m, k, lw=0.8, color=col, label=lab)
ax.set_xlabel("minutes since the day's first agent event"); ax.set_ylabel("mean fraction active, k")
ax.legend(frameon=False, fontsize=6); fig.tight_layout(); fig.savefig(FIG / f"{FP}E5_restart_relaxation.pdf"); plt.close(fig)

(OUTD / "explore_e1_e5.json").write_text(json.dumps(results, indent=1, default=str))
print(json.dumps({k: v for k, v in results.items() if k != "E1_per_day"}, indent=1, default=str))
