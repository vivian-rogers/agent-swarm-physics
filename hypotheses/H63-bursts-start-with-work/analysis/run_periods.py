"""H63 replication layer and natives on real (non-holdout) periods.

    uv run python hypotheses/H63-bursts-start-with-work/analysis/run_periods.py [--goals 31,39] [--workers 2]

Per period: herding bursts and matched non-burst clusters, precedence ORs (S, L, R, B), ordering, exogenous shares,
the S time-shift null (99 draws; 2x2 tables kept for pooling), and the arrival-hazard lead-lag model (with and without
the work terms). Writes data/processed/H63-bursts-start-with-work/results/{periods.parquet,clusters_G<NN>.parquet,
shift_tables.parquet}.
"""
from __future__ import annotations

import argparse
import json
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import polars as pl

import h63lib as L

N_SHIFT = 99


def run(g: int) -> dict:
    P = L.load(g)
    arr_all = L.arrivals(P, trim=False)
    arr = arr_all.filter(pl.col("trim"))
    out = {"goal_no": g, "n_arrivals_trim": arr.height, "n_arrivals_all": arr_all.height}
    res_dir = L.OUT / "results"
    res_dir.mkdir(parents=True, exist_ok=True)
    cl = L.clusters(arr, arr_all)
    pre = L.precedence(P, cl)
    pre.write_parquet(res_dir / f"clusters_G{g:02d}.parquet")
    q = pre.filter(pl.col("quiet"))
    bur = q.filter(pl.col("n_agents") >= 3)
    out["n_bursts"], out["n_controls"] = bur.height, q.height - bur.height
    out["n_S"] = int(P["signals"].filter(pl.col("cls") == "S").height)
    for col in ("S_pre", "L_pre", "R_pre", "B_pre", "SB_pre"):
        tb = L.table(pre, col)
        o = L.mh_or([tb])
        tag = col.replace("_pre", "")
        out[f"OR_{tag}"], out[f"OR_{tag}_lo"], out[f"OR_{tag}_hi"] = o["or"], o["lo"], o["hi"]
        out[f"tab_{tag}"] = json.dumps(tb)
        out[f"share_burst_{tag}"] = tb[0][0] / max(sum(tb[0]), 1)
        out[f"share_ctrl_{tag}"] = tb[1][0] / max(sum(tb[1]), 1)
    both = bur.filter(pl.col("first_S").is_not_nan() & pl.col("first_L").is_not_nan())
    out["n_both"] = both.height
    out["n_S_first"] = int((both["first_S"] < both["first_L"]).sum()) if both.height else 0
    out["share_kick_led"] = float(bur["kick_led"].mean()) if bur.height else np.nan
    out["share_human_led"] = float(bur["human_led"].mean()) if bur.height else np.nan
    out["share_exo_led"] = float((bur["kick_led"] | bur["human_led"]).mean()) if bur.height else np.nan
    # untrimmed precedence variant (scheduler impostor check)
    clu = L.clusters(arr_all, arr_all)
    preu = L.precedence(P, clu)
    ou = L.mh_or([L.table(preu, "S_pre")])
    out["OR_S_untrim"], out["n_bursts_untrim"] = ou["or"], preu.filter(pl.col("quiet") & (pl.col("n_agents") >= 3)).height
    # S time-shift null
    rng = np.random.default_rng(1000 + g)
    tabs = []
    for k in range(N_SHIFT):
        ss = L.shift_signals(P["signals"], P["days"], rng)
        tabs.append({"goal_no": g, "draw": k, "tab": json.dumps(L.table(L.precedence(P, cl, ss), "S_pre"))})
    pl.DataFrame(tabs).write_parquet(res_dir / f"shift_G{g:02d}.parquet")
    lor = [np.log(L.mh_or([json.loads(t["tab"])])["or"]) for t in tabs]
    lor = np.array([x for x in lor if np.isfinite(x)])
    if len(lor) > 10 and np.isfinite(out["OR_S"]):
        out["z_shift_OR_S"] = float((np.log(out["OR_S"]) - lor.mean()) / max(lor.std(ddof=1), 1e-9))
    # hazard
    D, uni = L.risk_panel(P, trim=True)
    if D is not None:
        B = 20 if g == 51 else 50
        h = L.hazard(D, B=B, seed=g)
        for k, v in h.items():
            if k != "regs":
                out[f"h_{k}"] = v
        h2 = L.hazard(D, regs=["L", "L_lead", "kick", "hum", "nud"], B=B, seed=g + 1)
        out["h_L_nowork"], out["h_L_nowork_se"] = h2.get("L", np.nan), h2.get("L_se", np.nan)
        out["n_universe"] = len(uni)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--goals", default="")
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    meta = pl.read_parquet(L.OUT / "meta.parquet")
    goals = meta["goal_no"].to_list()
    if a.goals:
        goals = [g for g in goals if g in {int(x) for x in a.goals.split(",")}]
    with ProcessPoolExecutor(a.workers) as ex:
        res = list(ex.map(run, goals))
    df = pl.DataFrame(res, infer_schema_length=None)
    path = L.OUT / "results" / "periods.parquet"
    if a.goals and path.exists():
        df = pl.concat([pl.read_parquet(path).filter(~pl.col("goal_no").is_in(goals)), df], how="diagonal_relaxed")
    df.sort("goal_no").write_parquet(path)
    print(df.select("goal_no", "n_bursts", "n_controls", "OR_S", "OR_S_lo", "OR_S_hi", "OR_L", "n_both", "n_S_first",
                    "h_dS", "h_dS_lo", "h_dS_hi", "h_dL").sort("goal_no"))


if __name__ == "__main__":
    main()
