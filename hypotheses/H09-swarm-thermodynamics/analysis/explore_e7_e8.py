"""H09 round 2, light exploratory pass. NON-HOLDOUT days only.

E7 (one quick pass, simple estimator; the MaxEnt/held-out estimator is deferred to H05's EP code):
  plug-in Markov entropy production per step on 1-min activity states (silent/idle/act/talk), window
  2026-07-24 -> 08-28 (end exclusive), minutes 10-469 of each day. Single agent: 4-state chain. Pair:
  16-state joint chain. Collective term per pair: dS_ij = S_ij - S_i - S_j, compared with a day-mismatch
  null (agent j's days cyclically shifted against agent i's), which keeps each agent's own dynamics and
  the daily schedule and absorbs the plug-in bias of the larger state space.
E8 (descriptive): memory "equation of state" from consolidation_inflow.parquet (build_observables.py).

Usage: uv run python hypotheses/H09-swarm-thermodynamics/analysis/explore_e7_e8.py
"""
from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
SH = ROOT / "data/processed/shared"
OUTD = ROOT / "data/processed/H09-swarm-thermodynamics"
FIG = Path(__file__).resolve().parents[1] / "figures"
RNG = np.random.default_rng(20261003)
plt.rcParams.update({"font.family": "serif", "font.size": 7, "axes.linewidth": 0.5, "pdf.fonttype": 42})
R: dict = {}
cal = pl.read_parquet(SH / "calendar.parquet")
roster = pl.read_parquet(SH / "roster.parquet")
labs = dict(zip(roster["agent"].to_list(), roster["lab"].to_list()))

# ================================================================== E7
W0, W1 = "2026-07-24", "2026-08-28"
days = cal.filter((pl.col("pt_date") >= W0) & (pl.col("pt_date") < W1))
assert not days["holdout"].any(), "E7 window overlaps the holdout"
days = days["pt_date"].to_list()
ab = (pl.read_parquet(SH / "activity_bins.parquet", columns=["pt_date", "minute", "agent", "state"])
      .filter(pl.col("pt_date").is_in(days) & (pl.col("minute") >= 10) & (pl.col("minute") < 470)))
agents = sorted(ab.group_by("agent").len().filter(pl.col("len") == len(days) * 460)["agent"].to_list())
X = np.zeros((len(agents), len(days), 460), np.int64)
ai = {a: i for i, a in enumerate(agents)}; di = {d: i for i, d in enumerate(days)}
for d, m, a, s in ab.filter(pl.col("agent").is_in(agents)).select("pt_date", "minute", "agent", "state").iter_rows():
    X[ai[a], di[d], m - 10] = s - 1


def ep(codes, k):
    """Plug-in EP per step (nats) of a k-state chain; codes: (days, T) int; transitions within days."""
    codes = np.asarray(codes, dtype=np.int64)
    a, b = codes[:, :-1].ravel(), codes[:, 1:].ravel()
    n = np.bincount(a * k + b, minlength=k * k).reshape(k, k).astype(float)
    nt = n.T
    m = (n > 0) & (nt > 0)
    np.fill_diagonal(m, False)
    return float(np.sum(n[m] / n.sum() * np.log(n[m] / nt[m])))


S1 = np.array([ep(X[i], 4) for i in range(len(agents))])
# minute-shuffle null for single agents (within day)
S1_null = np.array([[ep(np.array([RNG.permutation(row) for row in X[i]]), 4) for _ in range(20)] for i in range(len(agents))])
pairs = list(combinations(range(len(agents)), 2))
dS = np.array([ep(X[i] * 4 + X[j], 16) - S1[i] - S1[j] for i, j in pairs])
NNULL = 20
dS_null = np.zeros((len(pairs), NNULL))
nd = len(days)
for r in range(NNULL):
    sh = RNG.integers(1, nd)
    for p, (i, j) in enumerate(pairs):
        Xj = np.roll(X[j], sh, axis=0)  # agent j's day d+sh paired with agent i's day d
        dS_null[p, r] = ep(X[i] * 4 + Xj, 16) - S1[i] - S1[j]
excess = dS - dS_null.mean(1)
p95 = np.percentile(dS_null, 95, axis=1)
# mentions between pair members within the window
ch = (pl.read_parquet(SH / "chat_core.parquet", columns=["pt_date", "speaker_kind", "agent", "mentions"])
      .filter(pl.col("pt_date").is_in(days) & (pl.col("speaker_kind") == "agent")).explode("mentions").drop_nulls("mentions"))
mc = {(a, b): n for a, b, n in ch.group_by("agent", "mentions").len().iter_rows()}
ment = np.array([mc.get((agents[i], agents[j]), 0) + mc.get((agents[j], agents[i]), 0) for i, j in pairs])
rho = stats.spearmanr(excess, ment)
R["E7"] = {
    "window": [W0, W1], "days": nd, "agents": len(agents), "minutes_per_day": 460,
    "estimator": "plug-in Markov EP per 1-min step; single 4-state, pair 16-state; day-mismatch null (20 cyclic day shifts)",
    "single_agent": {"median_nats_per_min": float(np.median(S1)), "sum_over_agents": float(S1.sum()),
                     "frac_agents_above_shuffle_p95": float(np.mean(S1 > np.percentile(S1_null, 95, axis=1))),
                     "shuffle_null_median": float(np.median(S1_null))},
    "pairs": {"n": len(pairs), "dS_obs_median": float(np.median(dS)), "dS_null_median": float(np.median(dS_null)),
              "excess_median": float(np.median(excess)), "excess_sum_over_pairs": float(excess.sum()),
              "frac_pairs_above_null_p95": float(np.mean(dS > p95)),
              "median_excess_over_SiSj": float(np.median(excess / (S1[[i for i, _ in pairs]] + S1[[j for _, j in pairs]]))),
              "pairwise_sum_excess_over_S1sum": float(excess.sum() / S1.sum()),
              "spearman_excess_vs_mentions": float(rho.statistic), "spearman_p": float(rho.pvalue)},
    "by_lab_median_S1": {lb: float(np.median([S1[i] for i, a in enumerate(agents) if labs[a] == lb]))
                         for lb in sorted({labs[a] for a in agents})},
}
print("E7 done", flush=True)

# ================================================================== E8
ci = (pl.read_parquet(OUTD / "consolidation_inflow.parquet").filter(~pl.col("holdout"))
      .with_columns(pl.col("agent").replace_strict(labs, default="?").alias("lab")))
c3 = ci.filter((pl.col("regime") == "III") & pl.col("consolidate_event_120s") & pl.col("same_day_prev") & (pl.col("dt_s") > 0)
               & (pl.col("n_chars") > 0))
c3 = c3.with_columns(pl.col("n_chars").log().alias("lnV"), (pl.col("n_exposed") + 1).log().alias("lnPm"),
                     (pl.col("tok_uncached").clip(lower_bound=0) + 1).log().alias("lnPt"),
                     (1 - pl.col("jaccard_prev")).alias("turn"),
                     (pl.col("n_chars") - pl.col("d_chars")).alias("V_prev"),
                     (pl.col("agent").cast(pl.Utf8) + "_" + pl.col("goal_no").cast(pl.Utf8)).alias("ag"))


def demean(df, cols, by="ag"):
    return df.with_columns(*[(pl.col(c) - pl.col(c).mean().over(by)).alias(c + "_w") for c in cols])


def slope(df, y, x):
    d = df.drop_nulls([y, x]); xv, yv = d[x].to_numpy(), d[y].to_numpy()
    return float(np.sum(xv * yv) / np.sum(xv * xv)), int(len(xv))


e8 = {"n_snapshots_regIII": c3.height, "agents": int(c3["agent"].n_unique()),
      "median_interval_s": float(c3["dt_s"].median()), "median_n_exposed": float(c3["n_exposed"].median()),
      "median_tok_uncached": float(c3["tok_uncached"].median()), "frac_with_tokens": float(c3["tok_uncached"].is_not_null().mean())}
d = demean(c3, ["lnV", "lnPm", "lnPt", "turn", "V_prev", "lines_removed", "d_chars", "n_exposed"])
b_m, n_m = slope(d, "lnV_w", "lnPm_w")
b_t, n_t = slope(d.filter(pl.col("tok_uncached").is_not_null()), "lnV_w", "lnPt_w")
# variance shares of ln V: agent identity and lab (eta^2), lab with a label-permutation baseline
tot = float(((c3["lnV"] - c3["lnV"].mean()) ** 2).sum())
ag_m = c3.group_by("agent").agg(pl.col("lnV").mean().alias("m"), pl.len().alias("n"), pl.col("lab").first())
eta_agent = float((ag_m["n"] * (ag_m["m"] - c3["lnV"].mean()) ** 2).sum()) / tot
am = ag_m["m"].to_numpy(); al = ag_m["lab"].to_numpy()


def lab_share(lab_arr):
    g = am.mean(); ss = np.sum((am - g) ** 2)
    return sum(np.sum(lab_arr == l) * (am[lab_arr == l].mean() - g) ** 2 for l in np.unique(lab_arr)) / ss


ls_obs = lab_share(al); ls_null = [lab_share(RNG.permutation(al)) for _ in range(2000)]
e8["E8a"] = {"elasticity_lnV_lnPmsg_within_agent_goal": b_m, "n": n_m, "elasticity_lnV_lnPtok_within_agent_goal": b_t, "n_tok": n_t,
             "eta2_agent_lnV": eta_agent, "lab_share_between_agent_lnV": float(ls_obs),
             "lab_share_perm_null_median": float(np.median(ls_null)), "lab_share_perm_p": float(np.mean(np.array(ls_null) >= ls_obs))}
# E8b saturation over tenure (regime III, all non-holdout snapshots of the agent)
sat = []
for (a,), g in c3.sort("t").group_by("agent"):
    if g.height < 200:
        continue
    v = g["lnV"].to_numpy(); n = len(v); th = n // 3
    def growth(seg):
        k = max(len(seg) // 5, 5)
        return float(np.median(seg[-k:]) - np.median(seg[:k]))
    g1, g3 = growth(v[:th]), growth(v[2 * th:])
    sat.append({"agent": int(a), "lab": labs[a], "n": n, "growth_first_third": g1, "growth_last_third": g3,
                "saturated": bool(g1 > 0 and g3 < 0.2 * g1)})
e8["E8b"] = {"agents": len(sat), "frac_saturated_rule": float(np.mean([s["saturated"] for s in sat])),
             "frac_first_third_growth_positive": float(np.mean([s["growth_first_third"] > 0 for s in sat])),
             "median_growth_first_third": float(np.median([s["growth_first_third"] for s in sat])),
             "median_growth_last_third": float(np.median([s["growth_last_third"] for s in sat])),
             "per_agent": sat}
# E8c compression under pressure (within agent x goal)
r1 = stats.spearmanr(d["n_exposed_w"].to_numpy(), d["turn_w"].to_numpy(), nan_policy="omit")
r2 = stats.spearmanr(d["V_prev_w"].to_numpy(), d["lines_removed_w"].to_numpy(), nan_policy="omit")
dd = d.drop_nulls(["d_chars_w", "n_exposed_w", "V_prev_w"])
A = np.c_[dd["n_exposed_w"].to_numpy(), dd["V_prev_w"].to_numpy()]
coef = np.linalg.lstsq(A, dd["d_chars_w"].to_numpy(), rcond=None)[0]
d2 = demean(c3.with_columns(pl.col("n_turns").cast(pl.Float64), pl.col("dt_s").cast(pl.Float64)), ["turn", "n_turns", "dt_s", "lnPt"])
r_turns = stats.spearmanr(d2["n_turns_w"].to_numpy(), d2["turn_w"].to_numpy(), nan_policy="omit")
r_dt = stats.spearmanr(d2["dt_s_w"].to_numpy(), d2["turn_w"].to_numpy(), nan_policy="omit")
d2t = d2.filter(pl.col("tok_uncached").is_not_null())
r_tok = stats.spearmanr(d2t["lnPt_w"].to_numpy(), d2t["turn_w"].to_numpy(), nan_policy="omit")
r_pm_dt = stats.spearmanr(d["n_exposed_w"].to_numpy(), demean(c3.with_columns(pl.col("dt_s").cast(pl.Float64)), ["dt_s"])["dt_s_w"].to_numpy(), nan_policy="omit")
e8["E8c_controls"] = {"spearman_turnover_vs_own_turns": float(r_turns.statistic), "spearman_turnover_vs_interval_s": float(r_dt.statistic),
                      "spearman_turnover_vs_lnPtok": float(r_tok.statistic), "spearman_Pmsg_vs_interval_s": float(r_pm_dt.statistic)}
e8["E8c"] = {"spearman_Pmsg_turnover": float(r1.statistic), "spearman_Vprev_lines_removed": float(r2.statistic),
             "dV_on_P_beta_chars_per_msg": float(coef[0]), "dV_on_Vprev_minus_gamma": float(coef[1]),
             "implied_relaxation_snapshots": float(-1 / coef[1]) if coef[1] < 0 else None,
             "median_turnover_1_minus_jaccard": float(c3["turn"].median()),
             "median_lines_removed": float(c3["lines_removed"].median()), "median_lines_added": float(c3["lines_added"].median())}
# E8d NE14 jump (non-holdout days either side)
win = {"before_0316_0323": ("2026-03-16", "2026-03-24"), "after_0324_0325": ("2026-03-24", "2026-03-26"),
       "after_0326_0401": ("2026-03-26", "2026-04-02")}
assert not cal.filter((pl.col("pt_date") >= "2026-03-16") & (pl.col("pt_date") < "2026-04-02"))["holdout"].any()
hrs = cal.select("pt_date", (pl.col("window_s") / 3600).alias("h"))
per = {}
for name, (s, e) in win.items():
    w = ci.filter((pl.col("pt_date") >= s) & (pl.col("pt_date") < e)).join(hrs, on="pt_date")
    hours = hrs.filter((pl.col("pt_date") >= s) & (pl.col("pt_date") < e))["h"].sum()
    per[name] = (w.group_by("agent").agg((pl.len() / hours).alias("rate_per_h"), pl.col("n_chars").median().alias("V"),
                                         (1 - pl.col("jaccard_prev")).median().alias("turn"), pl.col("lines_removed").median().alias("rm"))
                 .with_columns(pl.lit(name).alias("w")))
both = per["before_0316_0323"].join(per["after_0326_0401"], on="agent", suffix="_a").join(per["after_0324_0325"], on="agent", suffix="_b", how="left")
ne = {"agents_both_sides": both.height}
for m in ("rate_per_h", "V", "turn", "rm"):
    r = np.log(np.maximum(both[m + "_a"].to_numpy().astype(float), 1e-6) / np.maximum(both[m].to_numpy().astype(float), 1e-6))
    rb = np.log(np.maximum(both[m + "_b"].fill_null(np.nan).to_numpy().astype(float), 1e-6) / np.maximum(both[m].to_numpy().astype(float), 1e-6))
    ne[m] = {"median_dln_after_0326": float(np.median(r)), "frac_abs_dln_gt_0.22": float(np.mean(np.abs(r) > 0.22)),
             "frac_increase": float(np.mean(r > 0)), "median_dln_0324_0325": float(np.nanmedian(rb))}
ne["raw_medians_across_agents"] = {w_: {m: float(per[w_][m].median()) for m in ("rate_per_h", "V", "turn", "rm")} for w_ in per}
ne["per_agent"] = both.select("agent", "rate_per_h", "rate_per_h_a", "V", "V_a", "turn", "turn_a").to_dicts()
e8["E8d_NE14"] = ne
R["E8"] = e8

# ================================================================== figures
fig, axs = plt.subplots(1, 2, figsize=(5.0, 2.2))
ax = axs[0]
ax.hist(dS_null.ravel(), bins=60, density=True, color="0.7", label="day-mismatch null")
ax.hist(dS, bins=60, density=True, histtype="step", color="#c2662d", lw=0.9, label="observed pairs")
ax.set_xlabel(r"$\Delta S_{ij}=S_{ij}-S_i-S_j$ (nats/min)"); ax.set_ylabel("density"); ax.legend(frameon=False, fontsize=5.5)
ax = axs[1]
ax.scatter(ment + 1, excess, s=3, color="#3f6fb5", alpha=0.6, lw=0)
ax.set_xscale("log"); ax.axhline(0, color="0.5", lw=0.4)
ax.set_xlabel("mentions between the pair + 1"); ax.set_ylabel("excess over null (nats/min)")
ax.set_title(f"Spearman {rho.statistic:.2f}", fontsize=6)
fig.tight_layout(); fig.savefig(FIG / "E7_pairwise_irreversibility.pdf"); plt.close(fig)

fig, axs = plt.subplots(1, 3, figsize=(7.0, 2.2))
ax = axs[0]
dm = (ci.filter((pl.col("pt_date") >= "2026-03-02") & (pl.col("pt_date") < "2026-04-30"))
      .group_by("pt_date", "agent").agg(pl.col("n_chars").median().alias("V"), (1 - pl.col("jaccard_prev")).median().alias("turn"), pl.len().alias("n"))
      .group_by("pt_date").agg(pl.col("V").median(), pl.col("turn").median(), pl.col("n").median()).sort("pt_date"))
xd = np.array([np.datetime64(x) for x in dm["pt_date"].to_list()])
ax.plot(xd, dm["V"].to_numpy() / 1000, "o-", ms=1.5, lw=0.7, color="#3f6fb5", label="median memory size (k chars)")
ax2 = ax.twinx(); ax2.plot(xd, dm["turn"].to_numpy(), "s-", ms=1.5, lw=0.7, color="#c2662d", label="median turnover 1-J")
for dte, lab_, fy in (("2026-03-24", "NE14", 0.97), ("2026-03-26", "NE16", 0.90)):
    ax.axvline(np.datetime64(dte), color="0.4", lw=0.5, ls="--")
    ax.text(np.datetime64(dte), ax.get_ylim()[0] + fy * (ax.get_ylim()[1] - ax.get_ylim()[0]), " " + lab_, fontsize=5)
ax.set_ylabel("k chars", color="#3f6fb5"); ax2.set_ylabel("1 - jaccard_prev", color="#c2662d")
ax.tick_params(axis="x", labelrotation=45, labelsize=5); ax.set_title("non-holdout days (gaps = holdout)", fontsize=6)
ax = axs[1]
dz = d.drop_nulls(["lnV_w", "lnPm_w"])
q = np.quantile(dz["lnPm_w"].to_numpy(), np.linspace(0, 1, 16))
qb = np.clip(np.searchsorted(q, dz["lnPm_w"].to_numpy(), side="right") - 1, 0, 14)
ax.plot([dz["lnPm_w"].to_numpy()[qb == i].mean() for i in range(15)], [dz["lnV_w"].to_numpy()[qb == i].mean() for i in range(15)], "o-", ms=2, lw=0.8, color="#3a7d6b")
ax.set_xlabel(r"$\ln(1+P_{msg})$, within agent$\times$goal"); ax.set_ylabel(r"$\ln V$, within agent$\times$goal")
ax.set_title(f"elasticity {b_m:.3f}", fontsize=6)
ax = axs[2]
dz = d.drop_nulls(["V_prev_w", "lines_removed_w"])
q = np.quantile(dz["V_prev_w"].to_numpy(), np.linspace(0, 1, 16))
qb = np.clip(np.searchsorted(q, dz["V_prev_w"].to_numpy(), side="right") - 1, 0, 14)
ax.plot([dz["V_prev_w"].to_numpy()[qb == i].mean() / 1000 for i in range(15)], [dz["lines_removed_w"].to_numpy()[qb == i].mean() for i in range(15)], "o-", ms=2, lw=0.8, color="#7a4b9c")
ax.set_xlabel(r"$V_{prev}$ (k chars), within agent$\times$goal"); ax.set_ylabel("lines removed, within")
fig.tight_layout(); fig.savefig(FIG / "E8_memory_eos.pdf"); plt.close(fig)

(OUTD / "explore_e7_e8.json").write_text(json.dumps(R, indent=1, default=str))
out = {k: v for k, v in R["E8"].items() if k not in ("E8b", "E8d_NE14")}
print(json.dumps(R["E7"], indent=1)); print(json.dumps(out, indent=1))
print(json.dumps({k: v for k, v in R["E8"]["E8b"].items() if k != "per_agent"}, indent=1))
print(json.dumps({k: v for k, v in R["E8"]["E8d_NE14"].items() if k != "per_agent"}, indent=1))
print(json.dumps(R["E8"]["E8c_controls"], indent=1))
