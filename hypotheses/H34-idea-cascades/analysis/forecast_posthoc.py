"""H34 post-hoc forecast rule (amendment A6, written after the pre-registered P7 failed; NOT pre-registered).

Diagnosis of the P7 failure (explore.py): R-hat is higher on a period's kickoff day (median 0.30 vs 0.19) and drifts
down within periods (median Spearman rho(R_day, day) = -0.38); day-to-day spread of logit P(s>=2) is 0.46 vs 0.13
expected from sampling. The pre-registered PI ignored both.

Candidate rule (post hoc): tree sizes ~ GW-NB(R_d, k), truncated at N, with
  R_d = R_hat_recent * exp(eta), eta ~ N(0, sigma_eta^2),
  R_hat_recent from the previous days excluding the kickoff day (variants below),
  sigma_eta estimated leave-one-period-out from the other periods' daily log R deviations (minus sampling variance).
Variants scored on the same day-ahead design as P7: V1 all prior days; V2 prior days without the kickoff day; V3 the
previous two days. Writes results/forecast_posthoc_days.parquet, results/forecast_posthoc.json.

  uv run python hypotheses/H34-idea-cascades/analysis/forecast_posthoc.py
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h34stats as S  # noqa: E402
import h34core as C  # noqa: E402

DATA = C.OUT
RES = DATA / "results"
MIN_TRAIN, MIN_TEST = 30, 20


def load(g):
    od = DATA / f"G{g:02d}"
    meta = json.loads((od / "meta.json").read_text())
    tr = pl.read_parquet(od / "trees.parquet")
    fu = pl.read_parquet(od / "first_uses.parquet")
    return meta, tr, fu


def day_R(tr: pl.DataFrame) -> pl.DataFrame:
    """R per root day from tree sizes (forest identity: kids / nodes = sum(s-1)/sum(s))."""
    return (tr.group_by("day").agg(((pl.col("size") - 1).sum()).alias("kids"), pl.col("size").sum().alias("nodes"),
                                   pl.len().alias("n")).sort("day"))


def sigma_eta_from(periods_dr: dict[int, pl.DataFrame], exclude: int) -> float:
    devs, svar = [], []
    for g, d in periods_dr.items():
        if g == exclude:
            continue
        d = d.filter((pl.col("day") > 0) & (pl.col("day") < d["day"].max()) & (pl.col("kids") >= 5))
        if d.height < 3:
            continue
        R = (d["kids"] / d["nodes"]).to_numpy()
        lr = np.log(R)
        devs.extend((lr - lr.mean()).tolist())
        svar.extend(((1 - R) / (R * d["nodes"].to_numpy())).tolist())
    v = np.mean(np.square(devs)) - np.mean(svar)
    return float(math.sqrt(max(v, 0.0)))


def tail_band(R, k, N, n, sig, rng, B=800, boot=None):
    ge2, ge3 = [], []
    for _ in range(B):
        Rb, kb = (R, k) if not boot else boot[rng.integers(len(boot))]
        Rd = min(Rb * math.exp(rng.normal(0, sig)), 0.995)
        p = S.nb_gw_pmf_trunc(Rd, kb, N)
        c = rng.multinomial(n, p)
        ge2.append(c[1:].sum() / n)
        ge3.append(c[2:].sum() / n)
    return (np.percentile(ge2, 5), np.percentile(ge2, 95)), (np.percentile(ge3, 5), np.percentile(ge3, 95))


def main():
    periods = sorted(int(p.name[1:]) for p in DATA.glob("G*") if (p / "meta.json").exists())
    loaded = {g: load(g) for g in periods}
    drs = {g: day_R(loaded[g][1]) for g in periods}
    rows = []
    for g in periods:
        meta, tr, fu = loaded[g]
        N = max(int(meta["N_room"]), int(tr["size"].max()))
        sig = sigma_eta_from(drs, g)
        rng = np.random.default_rng(g)
        days = sorted(tr["day"].unique().to_list())
        for d in days[1:]:
            tst = tr.filter(pl.col("day") == d)
            if tst.height < MIN_TEST:
                continue
            s_te = np.minimum(tst["size"].to_numpy(), N)
            n = len(s_te)
            o2, o3 = float((s_te >= 2).mean()), float((s_te >= 3).mean())
            for v, sel in (("V1", pl.col("day") < d), ("V2", (pl.col("day") < d) & ((pl.col("day") > 0) | (d == 1))),
                           ("V3", (pl.col("day") < d) & (pl.col("day") >= d - 2))):
                trn = tr.filter(sel)
                if trn.height < MIN_TRAIN:
                    continue
                ids = trn.select("idea", "tree")
                fu_t = fu.join(ids, on=["idea", "tree"], how="inner")
                R = float((((fu_t["status"] == 1) & (fu_t["parent"] >= 0)).sum()) / fu_t.height)
                k = S.fit_offspring(fu_t["offspring"].to_numpy())["k"]
                p = S.nb_gw_pmf_trunc(R, k, N)
                ls = float(np.log(np.maximum(p[s_te - 1], 1e-9)).sum())
                b2, b3 = tail_band(R, k, N, n, sig, rng)
                b2_0, b3_0 = tail_band(R, k, N, n, 0.0, rng, B=400)
                rows.append(dict(goal=g, day=int(d), variant=v, n_test=n, R_train=R, k=k, sigma=sig, obs_p2=o2, obs_p3=o3,
                                 pred_p2=float(p[1:].sum()), pred_p3=float(p[2:].sum()), ls=ls,
                                 cover2=bool(b2[0] <= o2 <= b2[1]), cover3=bool(b3[0] <= o3 <= b3[1]),
                                 cover2_nodrift=bool(b2_0[0] <= o2 <= b2_0[1]), cover3_nodrift=bool(b3_0[0] <= o3 <= b3_0[1])))
    df = pl.DataFrame(rows)
    df.write_parquet(RES / "forecast_posthoc_days.parquet")
    pre = pl.read_parquet(RES / "forecast_days.parquet").select("goal", "day", "ls_emp", "ls_betabin", "ls_binom", "ls_h03", "ls_fngw")
    out = {}
    for v in ("V1", "V2", "V3"):
        sub = df.filter(pl.col("variant") == v).join(pre, on=["goal", "day"], how="inner")
        per = sub.group_by("goal").agg(pl.col("ls").sum(), *[pl.col(c).sum() for c in ("ls_emp", "ls_betabin", "ls_binom", "ls_h03", "ls_fngw")])
        out[v] = dict(days=sub.height, cover2=float(sub["cover2"].mean()), cover3=float(sub["cover3"].mean()),
                      cover2_nodrift=float(sub["cover2_nodrift"].mean()), cover3_nodrift=float(sub["cover3_nodrift"].mean()),
                      bias_p2=float((sub["obs_p2"] - sub["pred_p2"]).mean()), bias_p3=float((sub["obs_p3"] - sub["pred_p3"]).mean()),
                      mae_p2=float((sub["obs_p2"] - sub["pred_p2"]).abs().mean()),
                      beats={r: [int((per["ls"] > per[f"ls_{r}"]).sum()), per.height] for r in ("emp", "betabin", "binom", "h03", "fngw")},
                      dls={r: float((per["ls"] - per[f"ls_{r}"]).sum()) for r in ("emp", "betabin", "binom", "h03", "fngw")})
    out["sigma_eta_median"] = float(df["sigma"].median())
    (RES / "forecast_posthoc.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
