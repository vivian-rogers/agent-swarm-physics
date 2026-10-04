"""H57 period-native tests (layer 2): NE42 (merge/split A-B-A), NE41 (forced erasures), #51 (N sweep, high-k tail).

  uv run python hypotheses/H57-copy-under-backlog/analysis/native.py [--only NE42,NE41,G51]

Reads statements.parquet; writes results/native_<id>.json. Outcomes are the replication outcomes (chance-corrected
read-set echo e_bge / e_gte, marker near-copy mkn_all), each prepared within its own goal period.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h57lib as L  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from run_period import OUT, RES, jnum  # noqa: E402
from scipy import stats  # noqa: E402

Y = ["e_bge", "e_gte", "mkn_all", "er_bge", "er_gte", "elc_bge", "elc_gte", "mklc_all"]  # pre-registered + post hoc
REGIME_III = [36, 37, 38, 39, 40, 41, 42, 44, 51]


def load(g: int) -> pl.DataFrame:
    d = pl.read_parquet(OUT / "statements.parquet").filter(pl.col("goal_no") == g)
    return L.prepare(d)


def signflip_p(x: np.ndarray, n: int = 20000, seed: int = 0) -> float:
    x = x[np.isfinite(x)]
    if len(x) < 3:
        return np.nan
    rng = np.random.default_rng(seed)
    obs = x.mean()
    null = (rng.choice([-1, 1], size=(n, len(x))) * x).mean(1)
    return float((np.sum(null >= obs) + 1) / (n + 1))


# --------------------------------------------------------------------------------------------- NE42
def ne42() -> dict:
    ph = {39: "A1", 40: "B", 41: "A2"}
    parts = []
    for g in ph:
        d = load(g).with_columns(pl.lit(g, dtype=pl.Int8).alias("g"))
        parts.append(d)
    d = pl.concat(parts, how="diagonal_relaxed")
    agg = d.group_by("agent", "g").agg(pl.len().alias("n"), *[pl.col(y).mean().alias(y) for y in Y],
                                       pl.col("logk").mean().alias("logk"))
    wide = {}
    for col in Y + ["logk", "n"]:
        w = agg.pivot(values=col, index="agent", on="g").rename({str(g): f"{col}_{g}" for g in ph})
        wide[col] = w
    W = wide["n"]
    for col in Y + ["logk"]:
        W = W.join(wide[col], on="agent", how="left")
    W = W.filter((pl.col("n_39") >= 10) & (pl.col("n_40") >= 10) & (pl.col("n_41") >= 10))
    out = {"n_agents": W.height, "agents_dropped": int(agg["agent"].n_unique() - W.height)}
    dk = (W["logk_40"] - (W["logk_39"] + W["logk_41"]) / 2).to_numpy()
    out["dlogk"] = {"mean": float(dk.mean()), "p_signflip": signflip_p(dk),
                    "phase_means": {g: float(W[f"logk_{g}"].mean()) for g in ph}}
    for y in Y:
        did = (W[f"{y}_40"] - (W[f"{y}_39"] + W[f"{y}_41"]) / 2).to_numpy()
        up = (W[f"{y}_40"] - W[f"{y}_39"]).to_numpy()
        down = (W[f"{y}_40"] - W[f"{y}_41"]).to_numpy()
        rho, prho = stats.spearmanr(did, dk) if len(did) > 3 else (np.nan, np.nan)
        out[y] = {"phase_means": {g: float(W[f"{y}_{g}"].mean()) for g in ph},
                  "DiD": float(did.mean()), "DiD_se": float(did.std(ddof=1) / np.sqrt(len(did))),
                  "DiD_p_signflip": signflip_p(did), "merge_up": float(up.mean()), "split_down": float(down.mean()),
                  "n_agents_DiD_pos": int((did > 0).sum()), "dose_spearman": float(rho), "dose_p": float(prho)}
    # statement-level transition design (exception (c)): #40 dummy, agent FE, per-period chance correction
    dd = d.with_columns((pl.col("g") == 40).cast(pl.Float64).alias("merged"),
                        pl.col("agent").cast(pl.Utf8).alias("g_agent_only"))
    for y in Y:
        sub = dd.filter(pl.col(y).is_not_null())
        X = sub.select("merged", *L.CONTROLS).to_numpy()
        r = L.fe_ols(sub[y].to_numpy(), X, [sub["g_agent_only"].to_numpy()], sub["cl_agent_day"].to_numpy(),
                     ["merged"] + L.CONTROLS)
        out[y]["stmt_merged"] = r.get("merged")
        X2 = sub.select("merged", "logk", *L.CONTROLS).to_numpy()
        r2 = L.fe_ols(sub[y].to_numpy(), X2, [sub["g_agent_only"].to_numpy()], sub["cl_agent_day"].to_numpy(),
                      ["merged", "logk"] + L.CONTROLS)
        out[y]["stmt_merged_given_logk"] = r2.get("merged")
        out[y]["stmt_logk_given_merged"] = r2.get("logk")
    return out


# --------------------------------------------------------------------------------------------- NE41
def ne41() -> dict:
    out = {"periods": {}}
    rows = {f"{y}|{kind}": [] for y in Y for kind in ("forced", "vol")}
    for g in REGIME_III:
        d = load(g).filter(pl.col("ctx_mode") == "cu")
        per = {}
        for kind, last_c, next_c in (("forced", "last_forced", "next_forced"), ("vol", "last_vol", "next_vol")):
            after = pl.col(last_c).fill_null(False) & (pl.col("pos_after") <= 3)
            before = pl.col(next_c).fill_null(False) & pl.col("next_same_day").fill_null(False) & (pl.col("pos_before") <= 3)
            sub = d.filter(after | before).with_columns(after.cast(pl.Float64).alias("after"))
            per[kind] = {"n_after": int(sub["after"].sum()), "n_before": int((1 - sub["after"]).sum())}
            for y in Y:
                ss = sub.filter(pl.col(y).is_not_null())
                if ss.height < 60 or ss["after"].std() == 0:
                    rows[f"{y}|{kind}"].append((np.nan, np.nan))
                    continue
                cols = ["after", "logk"] + L.CONTROLS
                r = L.fe_ols(ss[y].to_numpy(), ss.select(cols).to_numpy(), [ss["g_agent_unit"].to_numpy()],
                             ss["cl_agent_day"].to_numpy(), cols)
                a = r.get("after", {})
                per[kind][y] = {"b_after": a.get("b"), "se": a.get("se"), "p": a.get("p"), "n": r.get("n"),
                                "mean_after": float(ss.filter(pl.col("after") == 1)[y].mean()),
                                "mean_before": float(ss.filter(pl.col("after") == 0)[y].mean()),
                                "logk_after": float(ss.filter(pl.col("after") == 1)["logk"].mean()),
                                "logk_before": float(ss.filter(pl.col("after") == 0)["logk"].mean())}
                rows[f"{y}|{kind}"].append((a.get("b", np.nan), a.get("se", np.nan)))
        # context-load slope at fixed backlog, all computer-use statements
        dc = d.with_columns((pl.col("k_ctx").cast(pl.Float64).fill_null(0) + 1).log(2).alias("logkctx"))
        for y in Y:
            r = L.slope(dc, y, "agent", x="logkctx", extra=["logk"])
            per.setdefault("kctx", {})[y] = r.get("logkctx")
        out["periods"][f"G{g:02d}"] = per
    out["pooled"] = {}
    for key, lst in rows.items():
        b = [x[0] for x in lst]; se = [x[1] for x in lst]
        out["pooled"][key] = L.random_effects(b, se)
    for y in Y:
        b = [L.bget({"x": out["periods"][p]["kctx"].get(y) or {}}, "x") for p in out["periods"]]
        se = [L.bget({"x": out["periods"][p]["kctx"].get(y) or {}}, "x", key="se") for p in out["periods"]]
        out["pooled"][f"{y}|kctx"] = L.random_effects(b, se)
    return out


# --------------------------------------------------------------------------------------------- G51
def g51() -> dict:
    d = load(51)
    pu = pl.read_parquet(L.ROOT / "data/processed/shared/period_units.parquet",
                         columns=["unit_id", "n_agents", "n_days"]).filter(pl.col("unit_id").str.starts_with("51"))
    u = (d.group_by("unit_id").agg(pl.len().alias("n"), pl.col("logk").median().alias("logk_med"),
                                    pl.col("k").median().alias("k_med"), *[pl.col(y).mean().alias(y) for y in Y])
         .join(pu, on="unit_id", how="left").sort("unit_id"))
    out = {"units": u.to_dicts()}
    for y in Y:
        for xv in ("logk_med", "n_agents"):
            rho, p = stats.spearmanr(u[y].to_numpy(), u[xv].to_numpy())
            rng = np.random.default_rng(1)
            null = [stats.spearmanr(rng.permutation(u[y].to_numpy()), u[xv].to_numpy())[0] for _ in range(5000)]
            out[f"{y}~{xv}"] = {"spearman": float(rho), "p_perm_one": float((np.sum(np.array(null) >= rho) + 1) / 5001)}
    rho, _ = stats.spearmanr(u["logk_med"].to_numpy(), u["n_agents"].to_numpy())
    out["logk_med~n_agents"] = float(rho)
    # high-k tail: within-agent bin contrasts
    dd = d.with_columns(
        pl.when(pl.col("k") <= 3).then(0).when(pl.col("k") <= 10).then(1).when(pl.col("k") <= 29).then(2)
        .otherwise(3).alias("kbin"))
    dd = dd.with_columns(*[(pl.col("kbin") == j).cast(pl.Float64).alias(f"kb{j}") for j in (1, 2, 3)])
    out["kbin_counts"] = dd.group_by("kbin").len().sort("kbin").to_dicts()
    for y in Y:
        sub = dd.filter(pl.col(y).is_not_null())
        cols = ["kb1", "kb2", "kb3"] + L.CONTROLS
        r = L.fe_ols(sub[y].to_numpy(), sub.select(cols).to_numpy(), [sub["g_agent_unit"].to_numpy()],
                     sub["cl_agent_day"].to_numpy(), cols)
        out[f"{y}|kbins"] = {c: r.get(c) for c in ("kb1", "kb2", "kb3")}
        out[f"{y}|bin_means"] = sub.group_by("kbin").agg(pl.col(y).mean(), pl.len()).sort("kbin").to_dicts()
    # family heterogeneity of the slope
    fam = {}
    for lab in d["lab"].unique().to_list():
        sub = d.filter(pl.col("lab") == lab)
        if sub.height >= 500:
            fam[lab] = {y: L.slope(sub, y, "agent").get("logk") for y in Y}
            fam[lab]["n"] = sub.height
    out["by_family"] = fam
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="NE42,NE41,G51")
    a = ap.parse_args()
    RES.mkdir(parents=True, exist_ok=True)
    fns = {"NE42": ne42, "NE41": ne41, "G51": g51}
    for k in a.only.split(","):
        r = fns[k]()
        (RES / f"native_{k}.json").write_text(json.dumps(jnum(r), indent=1, default=str))
        print(k, "done")


if __name__ == "__main__":
    main()
