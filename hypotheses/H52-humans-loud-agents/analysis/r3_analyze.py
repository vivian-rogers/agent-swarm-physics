"""H52 round 2, R3 statistics from the hand codes (analysis/r3_codes_pass1.csv, analysis/r3_codes_pass2.csv) plus
objective outcomes (DQ2 reply parent; DQ4 agent work commits 3 h after vs 3 h before the receiving call).

Writes data/processed/H52-humans-loud-agents/r2/r3_results.json and r3_units.parquet (ids, codes, numbers only).
Usage: uv run python hypotheses/H52-humans-loud-agents/analysis/r3_analyze.py
"""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h52lib as L  # noqa: E402
import r3_code as C  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

SH = L.SH
OUT = L.OUT / "r2"
GEMINI25 = 6


def receiving_calls(units: pl.DataFrame) -> dict:
    it = pl.read_parquet(SH / "context_ledger_items.parquet", columns=["turn_id", "message_id"]).filter(
        pl.col("message_id").is_in(units["message_id"].unique().to_list()))
    tu = pl.read_parquet(SH / "context_ledger_turns.parquet", columns=["turn_id", "agent", "t_call"]).filter(
        pl.col("turn_id").is_in(it["turn_id"].to_list()))
    j = it.join(tu, on="turn_id").group_by("message_id", "agent").agg(pl.col("t_call").min())
    return {(m, int(a)): t for m, a, t in j.iter_rows()}


def objective(units: pl.DataFrame) -> pl.DataFrame:
    rc = receiving_calls(units)
    cc = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t"]).filter(
        pl.col("message_id").is_in(units["message_id"].to_list()))
    tm = dict(zip(cc["message_id"].to_list(), cc["t"].to_list()))
    rp = (pl.scan_parquet(SH / "reply_pairs.parquet")
          .filter(pl.col("A_message_id").is_in(units["message_id"].to_list()) & (pl.col("pair_set").cast(pl.Utf8) == "cand")
                  & pl.col("parent"))
          .select("A_message_id", "b_agent").collect())
    rep = set((m, int(a)) for m, a in rp.iter_rows())
    wc = pl.read_parquet(SH / "work_commits.parquet", columns=["t", "author_agent", "author_kind", "automated", "canonical",
                                                               "imported", "holdout"]).filter(
        pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind").cast(pl.Utf8) == "agent") & ~pl.col("automated")
        & ~pl.col("holdout"))
    out = []
    for r in units.iter_rows(named=True):
        a = int(r["target"])
        t0 = rc.get((r["message_id"], a)) or tm.get(r["message_id"])
        w = wc.filter(pl.col("author_agent") == a)
        n_after = w.filter((pl.col("t") >= t0) & (pl.col("t") < t0 + dt.timedelta(hours=3))).height
        n_before = w.filter((pl.col("t") >= t0 - dt.timedelta(hours=3)) & (pl.col("t") < t0)).height
        out.append(dict(unit=r["unit"], rep=int((r["message_id"], a) in rep), commits_after=n_after, commits_before=n_before,
                        has_rc=int((r["message_id"], a) in rc)))
    return pl.DataFrame(out)


def share(x):
    x = np.asarray(x, float)
    return float(x.mean()) if len(x) else np.nan


def newcombe(x1, x0):
    """Difference of proportions with a Newcombe (Wilson) 95% interval."""
    def wilson(k, n, z=1.96):
        if n == 0:
            return np.nan, np.nan
        p = k / n
        d = 1 + z * z / n
        c = (p + z * z / (2 * n)) / d
        h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
        return c - h, c + h
    k1, n1, k0, n0 = int(np.sum(x1)), len(x1), int(np.sum(x0)), len(x0)
    if n1 == 0 or n0 == 0:
        return dict(diff=np.nan, ci=[np.nan, np.nan])
    p1, p0 = k1 / n1, k0 / n0
    l1, u1 = wilson(k1, n1)
    l0, u0 = wilson(k0, n0)
    d = p1 - p0
    lo = d - np.sqrt((p1 - l1) ** 2 + (u0 - p0) ** 2)
    hi = d + np.sqrt((u1 - p1) ** 2 + (p0 - l0) ** 2)
    fisher_g = stats.fisher_exact([[k1, n1 - k1], [k0, n0 - k0]], alternative="greater").pvalue
    fisher_2 = stats.fisher_exact([[k1, n1 - k1], [k0, n0 - k0]]).pvalue
    return dict(p1=p1, n1=n1, k1=k1, p0=p0, n0=n0, k0=k0, diff=d, ci=[lo, hi], fisher_greater_p=fisher_g, fisher_two_p=fisher_2)


def cluster_collapse(df: pl.DataFrame, col: str) -> np.ndarray:
    """Gemini 2.5 Pro units count as one unit (their mean, rounded half up)."""
    g = df.filter(pl.col("target") == GEMINI25)
    o = df.filter(pl.col("target") != GEMINI25)[col].to_numpy().astype(float)
    if g.height:
        o = np.r_[o, float(g[col].mean() >= 0.5)]
    return o


def power_fisher(n1, n0, p0, d, reps=2000, seed=1):
    rng = np.random.default_rng(seed)
    p1 = min(1.0, p0 + d)
    hit = 0
    for _ in range(reps):
        k1, k0 = rng.binomial(n1, p1), rng.binomial(n0, p0)
        hit += stats.fisher_exact([[k1, n1 - k1], [k0, n0 - k0]], alternative="greater").pvalue < 0.05
    return hit / reps


def main():
    p1 = pl.read_csv(L.HYP / "analysis/r3_codes_pass1.csv")
    p2 = pl.read_csv(L.HYP / "analysis/r3_codes_pass2.csv")
    d = p1.filter((pl.col("directive") == 1) & (pl.col("broadcast") == 0) & (pl.col("target") >= 0))
    ob = objective(d)
    d = d.join(ob, on="unit", how="left").join(p2, on="unit", how="left")
    d = d.with_columns(pl.col("comply").is_in(["verified", "partial"]).cast(pl.Int8).alias("complied"),
                       pl.col("comply").is_in(["verified", "partial", "claimed"]).cast(pl.Int8).alias("complied_or_claimed"),
                       (pl.col("commits_after") - pl.col("commits_before")).alias("dcommits"))
    OUT.mkdir(parents=True, exist_ok=True)
    d.drop([c for c in d.columns if c in ("category",)]).write_parquet(OUT / "r3_units.parquet")
    H = d.filter(pl.col("cls") == "human")
    A = d.filter(pl.col("cls") == "agent")
    hc, hn = H.filter(pl.col("conflict") == 1), H.filter(pl.col("conflict") == 0)
    ac = A.filter(pl.col("conflict") == 1)
    res = {"counts": {"human_directives": H.height, "human_conflict": hc.height, "human_congruent": hn.height,
                      "agent_directives": A.height, "agent_conflict": ac.height, "agent_units_read": int((p1["cls"] == "agent").sum())},
           "comply_codes": {k: d.filter(pl.col("cls") == k[0]).filter(pl.col("conflict") == k[1]).group_by("comply").len().sort("comply").rows()
                            for k in []}}
    tab = {}
    for lab, sub in (("human_conflict", hc), ("human_congruent", hn), ("agent_conflict", ac)):
        tab[lab] = {c: int(n) for c, n in sub.group_by("comply").len().iter_rows()}
    res["comply_table"] = tab
    res["P1_human_conflict_complied"] = dict(share=share(hc["complied"]), n=hc.height, k=int(hc["complied"].sum()))
    res["P2_human_vs_agent_conflict"] = newcombe(hc["complied"].to_numpy(), ac["complied"].to_numpy())
    res["P2_task_only"] = newcombe(hc.filter(pl.col("task_conflict") == 1)["complied"].to_numpy(),
                                   ac.filter(pl.col("task_conflict") == 1)["complied"].to_numpy())
    res["P2_cluster_gemini_as_one"] = newcombe(cluster_collapse(hc, "complied"), ac["complied"].to_numpy())
    res["P2_drop_leak"] = newcombe(hc.filter(pl.col("leak") == 0)["complied"].to_numpy(), ac["complied"].to_numpy())
    res["P2_agent_not_offered"] = newcombe(hc["complied"].to_numpy(), ac.filter(pl.col("offered") == 0)["complied"].to_numpy())
    res["P2_complied_or_claimed"] = newcombe(hc["complied_or_claimed"].to_numpy(), ac["complied_or_claimed"].to_numpy())
    res["P2_prefiltered_humans"] = newcombe(hc.filter(pl.col("prefilter") == 1)["complied"].to_numpy(), ac["complied"].to_numpy())
    res["P3_human_conflict_vs_congruent"] = newcombe(hc["complied"].to_numpy(), hn["complied"].to_numpy())
    hn_x = hn.filter(~pl.col("category").is_in(["goal_assign", "permission"]))
    res["P3_excl_goal_assign_permission"] = newcombe(hc["complied"].to_numpy(), hn_x["complied"].to_numpy())
    res["P3_cluster_gemini_as_one"] = newcombe(cluster_collapse(hc, "complied"), cluster_collapse(hn, "complied"))
    res["P4_reply_human_vs_agent_conflict"] = newcombe(hc["rep"].to_numpy(), ac["rep"].to_numpy())
    res["decline_or_ignore"] = {lab: share(sub["comply"].is_in(["decline", "ignore"]).to_numpy())
                                for lab, sub in (("human_conflict", hc), ("human_congruent", hn), ("agent_conflict", ac))}
    res["gemini25_human_conflict"] = {c: int(n) for c, n in hc.filter(pl.col("target") == GEMINI25).group_by("comply").len().iter_rows()}
    res["human_conflict_excl_gemini25"] = dict(share=share(hc.filter(pl.col("target") != GEMINI25)["complied"]),
                                               n=hc.filter(pl.col("target") != GEMINI25).height)
    res["commits"] = {lab: dict(mean_after=float(sub["commits_after"].mean()), mean_before=float(sub["commits_before"].mean()),
                                mean_diff=float(sub["dcommits"].mean()), n=sub.height)
                      for lab, sub in (("human_conflict", hc), ("human_congruent", hn), ("agent_conflict", ac))}
    res["commits_diff_mwu"] = dict(p=float(stats.mannwhitneyu(hc["dcommits"].to_numpy(), ac["dcommits"].to_numpy()).pvalue))
    res["power_note"] = {f"d={dd}": power_fisher(hc.height, ac.height, share(ac["complied"]), dd) for dd in (0.2, 0.3)}
    L.jdump(res, OUT / "r3_results.json")
    L.write_provenance(OUT, "hypotheses/H52-humans-loud-agents/analysis/r3_analyze.py",
                       ["analysis/r3_codes_pass1.csv", "analysis/r3_codes_pass2.csv", "context_ledger_items", "context_ledger_turns",
                        "chat_core", "reply_pairs", "work_commits"], {"window_h": 3})
    import json
    print(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
