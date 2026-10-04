"""H66 native tests.
G51 (i) proxy validation: within agent-day, corr(log turnaround, log server time) over Gemini chained calls;
    (ii) provider vs platform: Google server-time spins between Google agents (block-shift null) and the Google
         server-time field vs the non-Google turnaround field (day circular-shift null), per unit 51a-51l;
    (iii) room split (51g) and replication numbers are read from replication/51*.json.
G44 the fine-tuned leader's loading on the leave-one-out turnaround field vs the other agents (replication/44b.json).
Run after replication.py: uv run python hypotheses/H66-platform-latency-field/analysis/native.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h66lib as L  # noqa: E402

ROOT = HERE.parents[2]
OUT = ROOT / "data/processed/H66-platform-latency-field"
SH = ROOT / "data/processed/shared"
LEADER = 28


def proxy_validation():
    cw = (pl.scan_parquet(SH / "call_windows.parquet")
          .filter(~pl.col("holdout") & (pl.col("goal_no") == 51) & pl.col("dur_api_s").is_not_null()
                  & (pl.col("gap_kind").cast(pl.String) == "busy") & (pl.col("ctx_mode").cast(pl.String) == "cu"))
          .select("agent", "pt_date", ((pl.col("t_first") - pl.col("t_prev_end")).dt.total_microseconds() / 1e6).alias("ta"), "dur_api_s")
          .filter((pl.col("ta") > 0) & (pl.col("ta") < 600) & (pl.col("dur_api_s") > 0)).collect())
    cw = cw.with_columns(pl.col("ta").log().alias("lt"), pl.col("dur_api_s").log().alias("la"))
    cw = cw.with_columns((pl.col("lt") - pl.col("lt").mean().over("agent", "pt_date")).alias("lt_c"),
                         (pl.col("la") - pl.col("la").mean().over("agent", "pt_date")).alias("la_c"))
    r = float(np.corrcoef(cw["lt_c"], cw["la_c"])[0, 1])
    per = cw.group_by("agent").agg(pl.corr("lt_c", "la_c").alias("r"), pl.len().alias("n")).sort("agent")
    share = float((cw["dur_api_s"].median()) / cw["ta"].median())
    return {"n_calls": cw.height, "r_within_agent_day": r, "per_agent": per.to_dicts(), "median_api_over_turnaround": share}


def api_field_tests(unit, rng, R=99):
    g = pl.read_parquet(OUT / "grid" / f"{unit}.parquet")
    D = L.assemble(g)
    if D is None:
        return None
    labs = json.loads((OUT / "labs.json").read_text())
    lab_of = dict(zip(g["agent"].to_list(), g["lab"].to_list()))
    goog = np.array([labs[lab_of[a]] == "Google" for a in D["agents"]])
    Api, Z, P, blk, day = D["Api"], D["Z"], D["P"], D["blk"], D["day"]
    gi = np.flatnonzero(goog & (~np.isnan(Api)).sum(0).astype(bool))
    out = {"unit": unit, "n_google": int(gi.size)}
    if gi.size >= 2:
        # Google-Google pairs only: give every non-Google agent its own code so "same_lab" = Google pairs
        codes = np.where(goog, -1, np.arange(Api.shape[1]))
        res = L.latency_strength(Api, P, blk, L._pairs(Api.shape[1]), codes, np.full(Api.shape[1], -1), rng, R=R)
        out["rho_api_google_pairs"] = res["same_lab"]
    # Google server-time field vs non-Google turnaround field
    va = ~np.isnan(Api) & P & goog[None, :]
    vz = ~np.isnan(Z) & P & ~goog[None, :]
    Fa = np.where(va.sum(1) > 0, np.where(va, Api, 0).sum(1) / np.maximum(va.sum(1), 1), np.nan)
    Fz = np.where(vz.sum(1) >= 3, np.where(vz, Z, 0).sum(1) / np.maximum(vz.sum(1), 1), np.nan)
    ok = np.isfinite(Fa) & np.isfinite(Fz)
    if ok.sum() >= 50:
        a = L.block_demean(np.where(ok, Fa, np.nan), blk, ok); z = L.block_demean(np.where(ok, Fz, np.nan), blk, ok)
        obs = L._corr(a[ok], z[ok])
        nl = []
        for _ in range(R):
            zs = L.shift_within_days(np.where(ok, Fz, np.nan), day, rng)
            okk = ok & np.isfinite(zs)
            zz = L.block_demean(zs, blk, okk)
            nl.append(L._corr(a[okk], zz[okk]))
        nl = np.array(nl)
        out["google_api_vs_nongoogle_turnaround"] = {"r": obs, "null_mean": float(np.nanmean(nl)), "null_sd": float(np.nanstd(nl)),
                                                     "p_two_sided": float((1 + np.sum(np.abs(nl - np.nanmean(nl)) >= abs(obs - np.nanmean(nl)))) / (1 + R)),
                                                     "n_minutes": int(ok.sum())}
    # Google turnaround field vs non-Google turnaround field (the proxy's own cross-provider correlation)
    vg = ~np.isnan(Z) & P & goog[None, :]
    Fg = np.where(vg.sum(1) > 0, np.where(vg, Z, 0).sum(1) / np.maximum(vg.sum(1), 1), np.nan)
    ok2 = np.isfinite(Fg) & np.isfinite(Fz)
    if ok2.sum() >= 50:
        a = L.block_demean(np.where(ok2, Fg, np.nan), blk, ok2); z = L.block_demean(np.where(ok2, Fz, np.nan), blk, ok2)
        out["google_turnaround_vs_nongoogle_turnaround"] = {"r": L._corr(a[ok2], z[ok2]), "n_minutes": int(ok2.sum())}
    return out


def main():
    rng = np.random.default_rng(66)
    res = {"proxy_validation_G51": proxy_validation()}
    res["api_tests"] = [x for x in (api_field_tests(u, rng) for u in
                                    ["51a", "51b", "51c", "51d", "51e", "51f", "51g", "51h", "51i", "51j", "51k", "51l"]) if x]
    r44 = json.loads((OUT / "replication" / "44b.json").read_text())
    loads = r44.get("loadings", [])
    lead = [x for x in loads if x["agent"] == LEADER]
    others = [x["g"] for x in loads if x["agent"] != LEADER and x["g"] is not None]
    res["G44_leader"] = {"leader": lead[0] if lead else None, "others_median": float(np.median(others)) if others else None,
                         "others_q25_q75": [float(np.percentile(others, 25)), float(np.percentile(others, 75))] if others else None,
                         "leader_rank_from_top": (sorted(others + [lead[0]["g"]], reverse=True).index(lead[0]["g"]) + 1) if lead else None,
                         "n_agents": len(loads)}
    (OUT / "native").mkdir(exist_ok=True)
    (OUT / "native" / "results.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res["proxy_validation_G51"], default=float)[:600])
    for x in res["api_tests"]:
        print(json.dumps(x, default=float)[:500])
    print(res["G44_leader"])


if __name__ == "__main__":
    main()
