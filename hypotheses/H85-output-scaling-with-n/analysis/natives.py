"""H85 natives: N1 NE42 (G40 room merge, same agents), N2 G51 roster sweep (day level), N3 G38 room-size contrast.

Reads agent_units.parquet, days.parquet, room_days.parquet, units.parquet (scheme/build.py). Non-holdout only.
Writes natives/natives.json.
Usage: uv run python hypotheses/H85-output-scaling-with-n/analysis/natives.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h85lib as L  # noqa: E402

B = 2000
RNG = np.random.default_rng(20261006)


def q(a):
    a = np.asarray(a, float)
    a = a[np.isfinite(a)]
    return [float(np.quantile(a, 0.025)), float(np.quantile(a, 0.975))] if len(a) > 20 else [np.nan, np.nan]


# ------------------------------------------------------------------------------------------------ N1 NE42
def ne42():
    au = pl.read_parquet(L.DATA / "agent_units.parquet").filter(pl.col("unit_id").is_in(["39", "40", "41"]))
    agents = (au.group_by("agent").agg(pl.col("unit_id").n_unique().alias("nu")).filter(pl.col("nu") == 3)["agent"].to_list())
    au = au.filter(pl.col("agent").is_in(agents) & (pl.col("present_h") > 0))
    rates = {}
    for k in ("msg", "ment", "reply", "commit", "talk_calls"):
        rates[k] = (au.with_columns((pl.col(k) / pl.col("present_h")).alias("rate"))
                    .pivot(on="unit_id", index="agent", values="rate").sort("agent"))
    kk = au.pivot(on="unit_id", index="agent", values=pl.col("k_sum"), aggregate_function="sum").sort("agent")
    kn = au.pivot(on="unit_id", index="agent", values=pl.col("k_n"), aggregate_function="sum").sort("agent")
    n = len(agents)

    def ratios(idx):
        out = {}
        for k, df in rates.items():
            m = {u: df[u].to_numpy()[idx].mean() for u in ("39", "40", "41")}
            out[k] = (m["40"] / ((m["39"] + m["41"]) / 2), m["41"] / m["39"])
        ks = {u: kk[u].to_numpy()[idx].sum() / max(kn[u].to_numpy()[idx].sum(), 1) for u in ("39", "40", "41")}
        out["k_talk"] = (ks["40"] / ((ks["39"] + ks["41"]) / 2), ks["41"] / ks["39"])
        return out

    base = ratios(np.arange(n))
    boots = [ratios(RNG.integers(0, n, n)) for _ in range(B)]
    res = {"n_agents": n}
    for k in base:
        res[k] = {"merge_ratio": float(base[k][0]), "merge_ci": q([b[k][0] for b in boots]),
                  "placebo_41_39": float(base[k][1]), "placebo_ci": q([b[k][1] for b in boots])}
    pred = base["k_talk"][0] ** (1 - L.BETA_D)
    res["pred_ment_ratio"] = float(pred)
    res["pred_ment_ci"] = q([b["k_talk"][0] ** (1 - L.BETA_D) for b in boots])
    res["ment_per_msg_ratio"] = float(base["ment"][0] / base["msg"][0])
    res["ment_per_msg_ci"] = q([b["ment"][0] / b["msg"][0] for b in boots])
    rd = pl.read_parquet(L.DATA / "room_days.parquet").filter(pl.col("unit_id").is_in(["39", "41"]) & pl.col("room").is_in([2, 3]))
    res["room_n_split_mean"] = float(rd["n_room"].mean())
    res["unit_N"] = {u: float(v) for u, v in pl.read_parquet(L.DATA / "units.parquet").filter(
        pl.col("unit_id").is_in(["39", "40", "41"])).select("unit_id", "N").iter_rows()}
    return res


# ------------------------------------------------------------------------------------------------ N2 G51 sweep
def g51():
    d = pl.read_parquet(L.DATA / "days.parquet").filter(pl.col("unit_id").str.starts_with("51")).sort("pt_date")
    d = d.filter((pl.col("h_d") >= 2) & (pl.col("msg") > 0))
    lnn = np.log(d["n_d"].to_numpy())
    s1 = (d["pt_date"] >= "2026-08-05").to_numpy().astype(float)
    s2 = (d["pt_date"] >= "2026-08-21").to_numpy().astype(float)
    dayi = np.arange(d.height, dtype=float)
    cl = d["unit_id"].to_numpy()
    out = {"n_days": d.height, "n_range": [int(d["n_d"].min()), int(d["n_d"].max())], "sd_lnn": float(lnn.std())}

    def slopes(ii, trend):
        X = np.column_stack([lnn[ii], np.ones(len(ii)), s1[ii], s2[ii]] + ([dayi[ii]] if trend else []))
        r = {}
        for k in ("msg", "ment", "reply", "commit", "talk_calls"):
            y = d[k].to_numpy()[ii].astype(float)
            ok = y > 0
            r[k] = L.ols(X[ok], np.log(y[ok] / d["h_d"].to_numpy()[ii][ok]))[0] if ok.sum() > 6 else np.nan
        ok = (d["ment"].to_numpy()[ii] > 0)
        r["ment_per_msg"] = L.ols(X[ok], np.log(d["ment"].to_numpy()[ii][ok] / d["msg"].to_numpy()[ii][ok]))[0]
        kk = d["k_n"].to_numpy()[ii] > 0
        r["k"] = L.ols(X[kk], np.log(d["k_sum"].to_numpy()[ii][kk] / d["k_n"].to_numpy()[ii][kk]))[0]
        return r

    groups = sorted(set(cl))
    idx_by = {g: np.where(cl == g)[0] for g in groups}
    for trend in (False, True):
        base = slopes(np.arange(d.height), trend)
        bs = [slopes(np.concatenate([idx_by[groups[p]] for p in RNG.choice(len(groups), len(groups))]), trend) for _ in range(B)]
        tag = "trend" if trend else "main"
        out[tag] = {k: {"est": float(v), "ci": q([b[k] for b in bs])} for k, v in base.items()}
        out[tag]["dbeta_ment_minus_pred"] = {"est": float(base["ment_per_msg"] - (1 - L.BETA_D) * base["k"]),
                                             "ci": q([b["ment_per_msg"] - (1 - L.BETA_D) * b["k"] for b in bs])}
    return out


# ------------------------------------------------------------------------------------------------ N3 room contrast
def rooms():
    rd = pl.read_parquet(L.DATA / "room_days.parquet")
    u = pl.read_parquet(L.DATA / "units.parquet").select("unit_id", "goal_no", "rooms")
    rd = rd.join(u, on="unit_id").filter(pl.col("room").is_in([2, 3]) & (pl.col("n_room") >= 2) & (pl.col("msg") > 0))
    res = {}
    for g in sorted(rd["goal_no"].unique().to_list()):
        sub = rd.filter(pl.col("goal_no") == g)
        w = sub.pivot(on="room", index="pt_date", values=["n_room", "msg", "ment", "k_talk"], aggregate_function="sum").drop_nulls()
        if w.height < 3 or "n_room_2" not in w.columns:
            continue
        dn = np.log(w["n_room_2"].to_numpy() / w["n_room_3"].to_numpy())
        out = {"n_days": w.height, "sd_dlnN": float(dn.std()), "mean_dlnN": float(dn.mean())}

        def sl(ii):
            r = {}
            for k in ("msg", "ment", "k_talk"):
                a, b_ = w[f"{k}_2"].to_numpy()[ii], w[f"{k}_3"].to_numpy()[ii]
                ok = (a > 0) & (b_ > 0)
                x = dn[ii][ok]
                r[k] = float((x @ np.log(a[ok] / b_[ok])) / (x @ x)) if ok.sum() >= 3 and (x @ x) > 0 else np.nan
            r["ment_per_msg"] = r["ment"] - r["msg"]
            return r

        base = sl(np.arange(w.height))
        bs = [sl(RNG.integers(0, w.height, w.height)) for _ in range(B)]
        out |= {k: {"est": v, "ci": q([b[k] for b in bs]), "se": float(np.nanstd([b[k] for b in bs]))} for k, v in base.items()}
        out["identified"] = bool(out["sd_dlnN"] >= 0.1)
        res[f"G{g:02d}"] = out
    # partial pooling (exception (d)): inverse-variance random-effects mean over identified periods
    pooled = {}
    for k in ("msg", "ment", "ment_per_msg", "k_talk"):
        est = np.array([v[k]["est"] for v in res.values() if v["identified"] and np.isfinite(v[k]["est"]) and v[k]["se"] > 0])
        se = np.array([v[k]["se"] for v in res.values() if v["identified"] and np.isfinite(v[k]["est"]) and v[k]["se"] > 0])
        if len(est) >= 2:
            w0 = 1 / se ** 2
            m0 = (w0 * est).sum() / w0.sum()
            Q = (w0 * (est - m0) ** 2).sum()
            tau2 = max(0.0, (Q - (len(est) - 1)) / (w0.sum() - (w0 ** 2).sum() / w0.sum()))
            w1 = 1 / (se ** 2 + tau2)
            m1 = (w1 * est).sum() / w1.sum()
            s1 = np.sqrt(1 / w1.sum())
            pooled[k] = {"est": float(m1), "ci": [float(m1 - 1.96 * s1), float(m1 + 1.96 * s1)], "k": int(len(est)), "tau2": float(tau2)}
    res["pooled_RE"] = pooled
    return res


def main():
    res = {"NE42": ne42(), "G51": g51(), "rooms": rooms()}
    out = L.DATA / "natives"
    out.mkdir(parents=True, exist_ok=True)
    (out / "natives.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
