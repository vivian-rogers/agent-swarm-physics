"""H15 viability choice by the D2.6 homeostasis rule (pre-registered in the card).

Shocks are goal-period boundaries (NE34 quenches) between consecutive non-holdout periods of the same regime, NOT
H15 scrambles. For each candidate V (agent-day, z-scored within agent x regime):
  D0 = V(day 0) - mean V(days -2, -1);  D3 = V(day 3) - same mean   (village active-day indices; days 0..3 in the
  new period, days -2, -1 in the old one)
  displacement delta = median |D0|;  recovery R = 1 - median |D3| / median |D0|
Placebo: 200 draws of as many pseudo-boundaries as real shocks, at mid-period days >= 3 active days from a real
boundary. Homeostatic: delta > placebo p95, R > placebo p95, R >= 0.5. Eligible: non-missing and non-zero on >= 50%
of agent-days in >= 80% of the regime's non-holdout units.

Outputs: data/processed/H15-semantic-information-scrambles/v_choice.json, figures/F2_viability_choice.pdf
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h15common import FIG, OUT, SEED, SH, V_CANDIDATES, V_LABEL, calendar_nonholdout, write_provenance  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

rng = np.random.default_rng(SEED)
ad = pl.read_parquet(OUT / "agent_day.parquet")
cal = calendar_nonholdout().sort("pt_date")
full = pl.read_parquet(SH / "calendar.parquet").filter((pl.col("n_agent_events") > 0) & (pl.col("goal_no") > 0)).sort("pt_date")
seq = cal["pt_date"].to_list()
unit = cal["unit"].to_list()
goal = cal["goal_no"].to_list()
reg = [str(r) for r in cal["regime"].to_list()]
# first/last active day of each goal in the FULL calendar (to require true adjacency across the boundary)
first_day = {g: d for g, d in full.group_by("goal_no").agg(pl.col("pt_date").min()).rows()}
last_day = {g: d for g, d in full.group_by("goal_no").agg(pl.col("pt_date").max()).rows()}

shocks = {"I": [], "III": []}
for b in range(2, len(seq) - 3):
    if unit[b] == unit[b - 1] or reg[b] != reg[b - 1] or reg[b] not in shocks:
        continue
    if goal[b] != goal[b - 1] + 1 or seq[b] != first_day[goal[b]] or seq[b - 1] != last_day[goal[b - 1]]:
        continue
    if unit[b - 2] != unit[b - 1] or len({unit[b + k] for k in range(4)}) != 1:
        continue
    shocks[reg[b]].append(b)
bounds = [b for b in range(1, len(seq)) if unit[b] != unit[b - 1]]
pseudo = {r: [p for p in range(2, len(seq) - 3) if reg[p] == r and len({unit[p + k] for k in range(-2, 4)}) == 1
              and min(abs(p - b) for b in bounds) >= 3] for r in shocks}
day_index = {d: i for i, d in enumerate(seq)}


def zpanel(V, r):
    d = ad.filter((pl.col("regime") == r) & pl.col(V).is_not_null() & pl.col(V).is_finite())
    d = d.with_columns(((pl.col(V) - pl.col(V).mean().over("agent")) / pl.col(V).std().over("agent")).alias("z"))
    d = d.filter(pl.col("z").is_finite())
    Z = {}
    for a, day, z in d.select("agent", "pt_date", "z").rows():
        Z[(a, day_index[day])] = z
    return Z, sorted(d["agent"].unique().to_list())


def stats(points, Z, agents):
    D0, D3 = [], []
    for b in points:
        for a in agents:
            v = [Z.get((a, b + k)) for k in (-2, -1, 0, 3)]
            if any(x is None for x in v):
                continue
            m = (v[0] + v[1]) / 2
            D0.append(v[2] - m)
            D3.append(v[3] - m)
    if len(D0) < 5:
        return None
    m0, m3 = float(np.median(np.abs(D0))), float(np.median(np.abs(D3)))
    return {"n": len(D0), "delta": m0, "R": 1 - m3 / m0 if m0 > 0 else float("nan")}


def eligibility(V, r):
    d = ad.filter(pl.col("regime") == r)
    per = d.group_by("unit").agg(((pl.col(V).is_not_null()) & (pl.col(V) != 0) & pl.col(V).is_finite()).mean().alias("f"))
    return float((per["f"] >= 0.5).mean()), {u: float(f) for u, f in per.rows()}


res = {}
for r in ("I", "III"):
    res[r] = {"n_shocks": len(shocks[r]), "shock_days": [seq[b] for b in shocks[r]], "candidates": {}}
    for V in V_CANDIDATES:
        frac_ok, per_unit = eligibility(V, r)
        Z, agents = zpanel(V, r)
        real = stats(shocks[r], Z, agents)
        draws = []
        for _ in range(200):
            pts = list(rng.choice(pseudo[r], size=len(shocks[r]), replace=True))
            s = stats(pts, Z, agents)
            if s:
                draws.append(s)
        dd = np.array([s["delta"] for s in draws])
        RR = np.array([s["R"] for s in draws])
        c = {"eligible": frac_ok >= 0.8, "frac_units_ok": frac_ok, "real": real,
             "placebo_delta_p95": float(np.percentile(dd, 95)) if len(dd) else None,
             "placebo_R_p95": float(np.percentile(RR, 95)) if len(RR) else None,
             "placebo_R_median": float(np.median(RR)) if len(RR) else None,
             "placebo_delta_median": float(np.median(dd)) if len(dd) else None}
        if real and len(dd):
            c["homeostatic"] = bool(c["eligible"] and real["delta"] > c["placebo_delta_p95"]
                                    and real["R"] > c["placebo_R_p95"] and real["R"] >= 0.5)
            c["score"] = real["R"] - c["placebo_R_median"]
        else:
            c["homeostatic"], c["score"] = False, float("nan")
        res[r]["candidates"][V] = c
    cands = res[r]["candidates"]
    homeo = [V for V, c in cands.items() if c["homeostatic"]]
    pool = homeo or [V for V, c in cands.items() if c["eligible"] and np.isfinite(c["score"])]
    best = max(pool, key=lambda V: cands[V]["score"]) if pool else None
    res[r]["chosen"] = best
    res[r]["d26_conclusive"] = bool(homeo)
    print(r, "shocks", len(shocks[r]), "chosen", best, "conclusive", bool(homeo))
    for V, c in cands.items():
        rr = c["real"] or {}
        print(f"  {V:6s} elig {c['eligible']!s:5s} delta {rr.get('delta', float('nan')):.3f} (p95 {c['placebo_delta_p95']:.3f})"
              f"  R {rr.get('R', float('nan')):+.3f} (p95 {c['placebo_R_p95']:+.3f}, med {c['placebo_R_median']:+.3f})"
              f"  n {rr.get('n')}  homeo {c['homeostatic']}")
res["regime_II_uses"] = res["I"]["chosen"]
(OUT / "v_choice.json").write_text(json.dumps(res, indent=1))
write_provenance("choose_v", ["H15 agent_day", "calendar"], {"shocks": "goal-period boundaries", "placebo_draws": 200},
                 built_by="hypotheses/H15-semantic-information-scrambles/analysis/choose_v.py")

# figure
fig, axs = plt.subplots(1, 2, figsize=(10, 3.6))
for ax, r in zip(axs, ("I", "III")):
    cands = res[r]["candidates"]
    for i, V in enumerate(V_CANDIDATES):
        c = cands[V]
        if not c["real"] or not c["placebo_delta_median"]:
            continue
        col = "#2a6f97" if V == res[r]["chosen"] else "#999999"
        ax.scatter(c["real"]["delta"] / c["placebo_delta_median"], c["real"]["R"], color=col, s=40, zorder=3)
        ax.annotate(V, (c["real"]["delta"] / c["placebo_delta_median"], c["real"]["R"]), fontsize=8,
                    xytext=(4, 3), textcoords="offset points")
        ax.plot([c["placebo_delta_p95"] / c["placebo_delta_median"]] * 2, [c["placebo_R_p95"] - 0.03, c["placebo_R_p95"] + 0.03],
                color=col, lw=0.8)
        ax.scatter([1], [c["placebo_R_median"]], marker="x", color=col, s=15)
    ax.axhline(0.5, color="k", lw=0.5, ls=":")
    ax.axvline(1, color="k", lw=0.5, ls=":")
    ax.set_xlabel("displacement at goal change / placebo median")
    ax.set_ylabel("recovery R by day 3")
    ax.set_title(f"regime {r}: {len(shocks[r])} goal-change shocks; chosen {res[r]['chosen']}"
                 + ("" if res[r]["d26_conclusive"] else " (inconclusive)"), fontsize=9)
fig.suptitle("D2.6 homeostasis rule (x = placebo median; tick = placebo p95 of R at the p95 displacement)", fontsize=9)
fig.tight_layout()
FIG.mkdir(exist_ok=True)
fig.savefig(FIG / "F2_viability_choice.pdf")
print("wrote v_choice.json and F2")
