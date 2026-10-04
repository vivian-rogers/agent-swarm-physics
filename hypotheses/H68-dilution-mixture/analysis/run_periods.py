"""H68 round 1 on real data: per-agent exponents, mixture tests, family, trait, natives (G51, NE42).

  uv run python hypotheses/H68-dilution-mixture/analysis/run_periods.py [--B 200]

Reads data/processed/H68-dilution-mixture/G<NN>/units.parquet (non-holdout; asserted again here) and the synthetic
power table (synthetic/summary.json) for the powered-period rule. Writes per-period agents.parquet and period.json,
results.json (cross-period), and per_period_estimates rows (write_estimates).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "infra/shared"))
import h68lib as L  # noqa: E402
from common import holdout_mask  # noqa: E402

D = ROOT / "data/processed/H68-dilution-mixture"
PERIODS = ["G10", "G24", "G25", "G26", "G27", "G30", "G31", "G35", "G36", "G37", "G38", "G39", "G40", "G41", "G42",
           "G44", "G51"]


def load_units(p):
    u = pl.read_parquet(D / p / "units.parquet")
    hm = holdout_mask(u["pt_date"].to_list(), [int(p[1:])] * u.height)
    assert not any(hm), f"{p}: held-out rows in units"
    return u


def agent_table(u: pl.DataFrame) -> pl.DataFrame:
    rows = []
    for (a,), g in u.group_by(["agent"], maintain_order=True):
        el = L.eligible(g, "resp")
        row = dict(agent=int(a), lab=g["lab"][0], n=g.height, n_resp=int(g["resp"].sum()), eligible=bool(el),
                   after_pause=float(g["after_pause"].cast(pl.Float64).mean()) if "after_pause" in g.columns else None,
                   k_med=float(np.exp(g["logk"].median())))
        if el:
            f = L.agent_fit(g, "resp")
            row.update(beta=f["beta"], se=f["se"], gamma=f["gamma"], converged=f["converged"])
            fe = L.agent_fit(g, "resp", engaged=True)
            row.update(beta_eng=fe["beta"], se_eng=fe["se"])
            if int(g["resp_reply"].sum()) >= 15:
                fr = L.agent_fit(g, "resp_reply")
                row.update(beta_reply=fr["beta"], se_reply=fr["se"])
            c, nd = L.thread_concentration(g, "resp")
            row.update(C=c, C_days=nd)
        rows.append(row)
    return pl.DataFrame(rows, infer_schema_length=None)


def pooled_beta(u: pl.DataFrame) -> dict:
    g = (u["agent"].cast(pl.Int64) * 1000 + u["day"].cast(pl.Int64)).to_numpy()
    g = np.unique(g, return_inverse=True)[1]
    X, off = L.design(u)
    r = L.fit_cll(u["resp"].to_numpy(), X, off, g)
    return dict(beta=float(r["b"][0]), se=float(r["se"][0]))


def run_period(args):
    p, B = args
    t0 = time.time()
    u = load_units(p)
    at = agent_table(u)
    el = at.filter(pl.col("eligible"))
    out = dict(period=p, n_agents=at.height, n_eligible=el.height, units=u.height)
    if el.height >= 4:
        b, s = el["beta"].to_numpy(), el["se"].to_numpy()
        mt = L.mixture_test(b, s, B=B, seed=int(p[1:]))
        lo, hi = L.tau_profile_ci(b, s)
        pb = pooled_beta(u.filter(pl.col("agent").is_in(el["agent"].implode())))
        wmean = float(np.sum(b / s ** 2) / np.sum(1 / s ** 2))
        out.update(mix={k: v for k, v in mt.items() if k != "post_hi"}, p1=L.p1_pass(mt), tau=mt["U"]["tau"],
                   tau_ci=[lo, hi], mu=mt["U"]["mu"], pooled=pb, wmean=wmean, gap=wmean - pb["beta"],
                   mid_share=float(np.mean((b >= 0.3) & (b <= 0.7))), beta_range=[float(b.min()), float(b.max())])
        at = at.join(pl.DataFrame({"agent": el["agent"], "post_hi": mt["post_hi"]}), on="agent", how="left")
    # G51 native extras: timer-wake exponents and shape
    if p == "G51":
        wu = pl.read_parquet(D / p / "wake_units.parquet")
        d2 = []
        for (a,), g in wu.group_by(["agent"], maintain_order=True):
            if L.eligible(g, "resp", min_units=150, min_resp=15, min_sd=0.3):
                f = L.agent_fit(g, "resp")
                d2.append(dict(agent=int(a), beta_d2=f["beta"], se_d2=f["se"], n_d2=f["n"], resp_d2=f["n_resp"]))
        if d2:
            at = at.join(pl.DataFrame(d2), on="agent", how="left")
        shp = []
        for (a,), g in u.filter(pl.col("agent").is_in(el["agent"].implode())).group_by(["agent"], maintain_order=True):
            r = L.floor_vs_pow(g, "resp")
            shp.append(dict(agent=int(a), rho_floor=r["rho"], dll_floor_pow=r["dll_floor_pow"]))
        at = at.join(pl.DataFrame(shp), on="agent", how="left")
    (D / p).mkdir(parents=True, exist_ok=True)
    at.write_parquet(D / p / "agents.parquet")
    out["secs"] = round(time.time() - t0, 1)
    (D / p / "period.json").write_text(json.dumps(out, indent=1, default=float))
    print(p, {k: out.get(k) for k in ("n_eligible", "p1", "tau", "tau_ci", "mu", "gap")}, flush=True)
    return out


def spearman(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    if ok.sum() < 5:
        return dict(rho=float("nan"), p=float("nan"), n=int(ok.sum()))
    r = stats.spearmanr(x[ok], y[ok])
    return dict(rho=float(r.statistic), p=float(r.pvalue), n=int(ok.sum()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--B", type=int, default=200)
    ap.add_argument("--procs", type=int, default=2)
    a = ap.parse_args()
    with ProcessPoolExecutor(a.procs) as ex:
        outs = list(ex.map(run_period, [(p, a.B) for p in PERIODS]))
    per = {o["period"]: o for o in outs}
    # powered rule from the synthetic table (W2 P1 rate >= 0.8 and >= 6 eligible)
    syn = json.loads((D / "synthetic/summary.json").read_text())
    pw = {r["period"]: r["p1_rate"] for r in syn if r["world"] == "W2"}
    size = {r["period"]: r["p1_rate"] for r in syn if r["world"] == "W1"}
    for p, o in per.items():
        o["power_W2"] = pw.get(p)
        o["size_W1"] = size.get(p)
        o["powered"] = bool(o["n_eligible"] >= 6 and (pw.get(p) or 0) >= 0.8)
        if "mix" not in o:
            o["verdict"] = "descriptive"
        elif o["p1"]:
            o["verdict"] = "supported"
        elif not o["powered"]:
            o["verdict"] = "descriptive"
        elif o["mix"]["p"] < 0.05 or o["tau_ci"][1] >= 0.35:
            o["verdict"] = "mixed"
        else:
            o["verdict"] = "failed"
    # cross-period agent table
    ag = []
    for p in PERIODS:
        t = pl.read_parquet(D / p / "agents.parquet").filter(pl.col("eligible")).with_columns(pl.lit(p).alias("period"))
        ag.append(t)
    ag = pl.concat(ag, how="diagonal_relaxed")
    ag.write_parquet(D / "agents_all.parquet")
    tau2 = float(np.median([o["tau"] for o in outs if "tau" in o]) ** 2)
    labsh = L.lab_share(ag.select("agent", "period", "lab", "beta", "se"), n_perm=2000, seed=1, tau2=tau2)
    trait = L.trait_icc(ag.select("agent", "period", "beta", "se"), n_boot=2000, seed=1)
    g51 = ag.filter(pl.col("period") == "G51")
    lab51 = L.lab_share(g51.select("agent", "period", "lab", "beta", "se"), n_perm=2000, seed=2,
                        tau2=per["G51"]["tau"] ** 2) if g51.height >= 6 else None
    res = dict(
        periods=per,
        P1=dict(n_powered=sum(o["powered"] for o in outs), n_pass_powered=sum(o["powered"] and o.get("p1", False)
                                                                            for o in outs),
                n_pass_any=sum(bool(o.get("p1")) for o in outs),
                n_tauhi_lt035_powered=sum(o["powered"] and o["tau_ci"][1] < 0.35 for o in outs if "tau_ci" in o)),
        P2=dict(lab_all=labsh, trait=trait, lab_G51=lab51),
        P3=dict(gaps={p: o.get("gap") for p, o in per.items()},
                n_within_01=sum(abs(o["gap"]) <= 0.1 for o in outs if "gap" in o),
                n=sum("gap" in o for o in outs)),
        P4=spearman(ag["beta"].to_numpy(), ag["C"].to_numpy()),
        P5=spearman(ag["beta"].to_numpy(), ag["beta_reply"].to_numpy() if "beta_reply" in ag.columns else []),
        eng=spearman(ag["beta"].to_numpy(), ag["beta_eng"].to_numpy()),
        tau_pooled_median=float(np.sqrt(tau2)),
    )
    # G51 native
    t51 = pl.read_parquet(D / "G51/agents.parquet").filter(pl.col("eligible"))
    res["N_G51"] = dict(
        mixture=per["G51"].get("mix"), p1=per["G51"].get("p1"), lab=lab51,
        d2=spearman(t51["beta"].to_numpy(), t51["beta_d2"].to_numpy()) if "beta_d2" in t51.columns else None,
        mid_share=per["G51"].get("mid_share"),
        floor_better=int((t51["dll_floor_pow"] > 2).sum()) if "dll_floor_pow" in t51.columns else None,
        pow_better=int((t51["dll_floor_pow"] < -2).sum()) if "dll_floor_pow" in t51.columns else None,
        n=t51.height)
    # NE42 native
    tt = {p: pl.read_parquet(D / p / "agents.parquet").filter(pl.col("eligible")).select("agent", "beta", "se")
          for p in ("G39", "G40", "G41")}
    j = tt["G39"].rename({"beta": "b39", "se": "s39"}).join(tt["G40"].rename({"beta": "b40", "se": "s40"}), on="agent",
                                                              how="inner").join(
        tt["G41"].rename({"beta": "b41", "se": "s41"}), on="agent", how="inner")
    if j.height >= 4:
        side = (j["b39"].to_numpy() + j["b41"].to_numpy()) / 2
        db = j["b40"].to_numpy() - side
        sd = np.sqrt(j["s40"].to_numpy() ** 2 + (j["s39"].to_numpy() ** 2 + j["s41"].to_numpy() ** 2) / 4)
        w = 1 / sd ** 2
        mdb = float(np.sum(w * db) / np.sum(w))
        res["N_NE42"] = dict(n=j.height, rho=spearman(j["b40"].to_numpy(), side),
                             rho_39_41=spearman(j["b39"].to_numpy(), j["b41"].to_numpy()), mean_dbeta=mdb,
                             se_dbeta=float(np.sqrt(1 / np.sum(w))), agents=j.to_dicts())
    (D / "results.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps({k: res[k] for k in ("P1", "P3", "P4", "P5", "eng")}, indent=1, default=float))
    print(json.dumps(res["P2"], indent=1, default=float))
    print(json.dumps({k: v for k, v in res.get("N_NE42", {}).items() if k != "agents"}, indent=1, default=float))
    print(json.dumps({k: v for k, v in res["N_G51"].items() if k != "mixture"}, indent=1, default=float))


if __name__ == "__main__":
    main()
