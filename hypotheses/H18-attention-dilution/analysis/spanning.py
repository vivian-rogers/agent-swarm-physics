"""H18 spanning tests (the transition is the object, CLAUDE.md exception (c)).

  uv run python hypotheses/H18-attention-dilution/analysis/spanning.py

1. Merge 05-04 / split 05-11 (#39 -> #40 -> #41, A-B-A): for the agents merged on 05-04 (all but GPT-5), per side:
   k-bar per talk turn (k >= 1), per-pair addressing rate p-bar, S per talk (senders addressed), within-side beta.
   Per-agent paired contrasts (B vs A and B vs A') and a day bootstrap of the side means.
2. NE15 (exploratory side only): the #35 same-day small-room vs large-room contrast (from G35/fits.json) and its
   replication on the two-room days of #36-#44.
Writes data/processed/H18-attention-dilution/spanning.json.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from h18lib import Units, fit  # noqa: E402

ROOT = HERE.parents[2]
DATA = ROOT / "data/processed/H18-attention-dilution"


def side(gp, keep_agents=None):
    talks = pl.read_parquet(DATA / gp / "talks.parquet")
    pend = pl.read_parquet(DATA / gp / "pending.parquet")
    U = Units(talks, pend, "talk_id")
    u = U.df
    if keep_agents is not None:
        u = u.filter(pl.col("agent").is_in(keep_agents))
        talks = talks.filter(pl.col("agent").is_in(keep_agents))
    tk = talks.filter(pl.col("k") >= 1)
    S = u.group_by("talk_id", "agent", "pt_date").agg(pl.col("r").sum().alias("S"))
    per_agent = (tk.group_by("agent").agg(pl.col("k").mean().alias("kbar"), pl.col("n_room").mean().alias("nroom"),
                                          pl.len().alias("n_talks"))
                 .join(u.group_by("agent").agg(pl.col("r").cast(pl.Float64).mean().alias("pbar"), pl.len().alias("n_units")),
                       on="agent")
                 .join(S.group_by("agent").agg(pl.col("S").cast(pl.Float64).mean().alias("Sbar")), on="agent"))
    per_day = (tk.group_by("pt_date").agg(pl.col("k").mean().alias("kbar"))
               .join(u.group_by("pt_date").agg(pl.col("r").cast(pl.Float64).sum().alias("rs"), pl.len().alias("nu")), on="pt_date")
               .join(S.group_by("pt_date").agg(pl.col("S").cast(pl.Float64).sum().alias("Ss"), pl.len().alias("nt")), on="pt_date"))
    if keep_agents is not None:
        m = np.isin(U.agent, keep_agents)
        Us = U.subset(m)
    else:
        Us = U
    beta = fit("pow", Us)["params"]["beta"]
    return dict(per_agent=per_agent, per_day=per_day, beta=beta, kbar=float(tk["k"].mean()),
                pbar=float(u["r"].cast(pl.Float64).mean()), Sbar=float(S["S"].mean()), nroom=float(tk["n_room"].mean()),
                n_units=u.height)


def boot_ratio(dA, dB, key_num, key_den, rng, B=2000):
    """Day bootstrap of (sum num / sum den) in B over the same in A."""
    a_n, a_d = dA[key_num].to_numpy(), dA[key_den].to_numpy()
    b_n, b_d = dB[key_num].to_numpy(), dB[key_den].to_numpy()
    out = []
    for _ in range(B):
        ia = rng.integers(len(a_n), size=len(a_n))
        ib = rng.integers(len(b_n), size=len(b_n))
        out.append((b_n[ib].sum() / b_d[ib].sum()) / (a_n[ia].sum() / a_d[ia].sum()))
    out = np.array(out)
    return float(np.quantile(out, 0.025)), float(np.quantile(out, 0.975))


def merge_test(rng):
    ros = pl.read_parquet(ROOT / "data/processed/shared/roster.parquet")
    gpt5 = int(ros.filter(pl.col("name") == "GPT-5")["agent"][0])
    t39 = pl.read_parquet(DATA / "G39/talks.parquet")["agent"].unique().to_list()
    t40 = pl.read_parquet(DATA / "G40/talks.parquet")["agent"].unique().to_list()
    t41 = pl.read_parquet(DATA / "G41/talks.parquet")["agent"].unique().to_list()
    merged = sorted(set(t39) & set(t40) & set(t41) - {gpt5})
    sides = {gp: side(gp, merged) for gp in ("G39", "G40", "G41")}
    res = {"merged_agents": merged, "gpt5": gpt5, "sides": {}}
    for gp, s in sides.items():
        res["sides"][gp] = {k: s[k] for k in ("beta", "kbar", "pbar", "Sbar", "nroom", "n_units")}
    # per-agent paired contrasts
    pa = {gp: s["per_agent"] for gp, s in sides.items()}
    j = pa["G40"].join(pa["G39"], on="agent", suffix="_A").join(pa["G41"], on="agent", suffix="_A2")
    pairs = {}
    for key in ("kbar", "pbar", "Sbar"):
        dA = (j[key] / j[f"{key}_A"]).to_numpy()
        dA2 = (j[key] / j[f"{key}_A2"]).to_numpy()
        pairs[key] = dict(median_ratio_vs_39=float(np.nanmedian(dA)), n_up_vs_39=int(np.sum(dA > 1)),
                          median_ratio_vs_41=float(np.nanmedian(dA2)), n_up_vs_41=int(np.sum(dA2 > 1)), n=int(len(dA)))
    res["per_agent"] = pairs
    # day-bootstrap ratios of side means (B over A, B over A')
    for key_num, key_den, lab in (("rs", "nu", "pbar"), ("Ss", "nt", "Sbar")):
        for gpA in ("G39", "G41"):
            lo, hi = boot_ratio(sides[gpA]["per_day"], sides["G40"]["per_day"], key_num, key_den, rng)
            res.setdefault("boot", {})[f"{lab}_40_over_{gpA[1:]}"] = dict(
                ratio=sides["G40"][lab] / sides[gpA][lab], lo=lo, hi=hi)
    kr = {gpA: sides["G40"]["kbar"] / sides[gpA]["kbar"] for gpA in ("G39", "G41")}
    res["k_ratio_40_over"] = kr
    # GPT-5 (left alone in #rest during #40)
    try:
        g5 = {gp: side(gp, [gpt5]) for gp in ("G39", "G40", "G41")}
        res["gpt5"] = {gp: {k: s[k] for k in ("kbar", "pbar", "Sbar", "nroom", "n_units")} for gp, s in g5.items()}
    except Exception as e:  # too few units
        res["gpt5"] = str(e)
    pb = res["boot"]
    res["P7"] = dict(
        k_up=all(v > 1 for v in kr.values()),
        p_down_both=pb["pbar_40_over_39"]["ratio"] < 1 and pb["pbar_40_over_41"]["ratio"] < 1,
        p_down_both_ci=pb["pbar_40_over_39"]["hi"] < 1 and pb["pbar_40_over_41"]["hi"] < 1,
        S_within_30=all(0.7 <= pb[f"Sbar_40_over_{x}"]["ratio"] <= 1 / 0.7 for x in ("39", "41")),
        drop_vs_kratio={x: (1 / pb[f"pbar_40_over_{x}"]["ratio"]) / kr[f"G{x}"] for x in ("39", "41")},
        beta_spread=float(max(s["beta"] for s in sides.values()) - min(s["beta"] for s in sides.values())))
    return res


def ne15():
    out = {}
    for gp in ("G35", "G36", "G37", "G38", "G39", "G41", "G42", "G44"):
        f = DATA / gp / "fits.json"
        if not f.exists():
            continue
        r = json.loads(f.read_text()).get("rooms")
        if not r:
            continue
        out[gp] = {k: r[k] for k in ("n_days", "effect_const", "effect_const_ci", "effect_pow", "effect_pow_ci",
                                     "median_k_ratio", "median_p_ratio", "median_S_ratio", "beta_roomfe")}
    return out


if __name__ == "__main__":
    rng = np.random.default_rng(18)
    res = {"merge": merge_test(rng), "ne15": ne15()}
    (DATA / "spanning.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res["merge"]["sides"], indent=1))
    print(json.dumps(res["merge"]["P7"], indent=1, default=float))
