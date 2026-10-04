"""H51 natives (layer 2): NE14 (#36 regime II -> III), NE42 (#39 -> #40 -> #41 merge A-B-A), G51 (roster growth).

Slopes b_j (Y_j on g_lag) and c_j (Y_j on log N) are fitted across periods with the native's own periods excluded, so
each native prediction is out of sample. Outputs data/processed/H51-one-dial-collapse/natives/{NE14,NE42,G51}.json.
Usage: uv run python hypotheses/H51-one-dial-collapse/analysis/natives.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h51lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "hypotheses/H51-one-dial-collapse/scheme"))
import build as B  # noqa: E402  (own scheme module: R_hat rule, loop flags, herding estimator)

OUTD = L.DATA / "natives"
TRANS = {"Y3_branch": L.logit, "Y4_loop": L.logit, "Y2_herd": lambda x: np.asarray(x, float)}


def slope(d: pl.DataFrame, j: str, x: str, exclude: list[int]):
    s = L.common_sample(d).filter(~pl.col("goal_no").is_in(exclude) & pl.col(j).is_not_null())
    X = np.column_stack([np.ones(s.height), s[x].to_numpy().astype(float)])
    y = s[j].to_numpy().astype(float)
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    r = y - X @ coef
    s2 = r @ r / (len(y) - 2)
    cov = s2 * np.linalg.inv(X.T @ X)
    return float(coef[1]), float(np.sqrt(cov[1, 1])), float(np.sqrt(s2)), s.height


def daily_obs(goal: int, days: list[str]) -> pl.DataFrame:
    """Per day: loop-rate counts and R_hat counts (for day-block bootstraps)."""
    fl = B.stmt_flags().filter((pl.col("goal_no") == goal) & pl.col("pt_date").is_in(days))
    lr = fl.group_by("pt_date").agg(pl.len().alias("n_stmt"), pl.col("self_repeat").sum().alias("n_rep"))
    fu = B.first_uses(goal)
    pu = pl.read_parquet(B.SH / "period_units.parquet").filter(pl.col("goal_no") == goal).explode("days")
    # map first uses to PT days via unit day lists is not possible directly; use calendar-free UTC->PT shift (UTC-7/8)
    fu = fu.with_columns(pl.from_epoch("t_us", time_unit="us").dt.replace_time_zone("UTC")
                         .dt.convert_time_zone("America/Los_Angeles").dt.strftime("%Y-%m-%d").alias("pt_date"))
    fr = fu.filter(pl.col("pt_date").is_in(days)).group_by("pt_date").agg(
        pl.len().alias("n_fu"), ((pl.col("status") == 1) & (pl.col("parent") >= 0)).sum().alias("n_par"))
    del pu
    return lr.join(fr, on="pt_date", how="full", coalesce=True).fill_null(0).sort("pt_date")


def boot_delta(dA: pl.DataFrame, dB: pl.DataFrame, num: str, den: str, n=2000, seed=0):
    rng = np.random.default_rng(seed)

    def val(x):
        return L.logit(x[num].sum() / max(x[den].sum(), 1))

    obs = float(val(dB) - val(dA))
    a, b = dA.to_dicts(), dB.to_dicts()
    bs = []
    for _ in range(n):
        sa = pl.DataFrame([a[i] for i in rng.integers(0, len(a), len(a))])
        sb = pl.DataFrame([b[i] for i in rng.integers(0, len(b), len(b))])
        bs.append(val(sb) - val(sa))
    return obs, float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))


def ne14(d: pl.DataFrame, nu: pl.DataFrame) -> dict:
    pu = pl.read_parquet(B.SH / "period_units.parquet").filter(pl.col("goal_no") == 36)
    days = {r["unit_id"]: list(r["days"]) for r in pu.iter_rows(named=True)}
    A, Bd = days["36a"], days["36b"] + days["36c"]
    daily = daily_obs(36, A + Bd)
    dA, dB = daily.filter(pl.col("pt_date").is_in(A)), daily.filter(pl.col("pt_date").is_in(Bd))
    u = nu.filter(pl.col("goal_no") == 36)
    gA = u.filter(pl.col("unit_id") == "36a")["g_lag"][0]
    gb = u.filter(pl.col("unit_id").is_in(["36b", "36c"]))
    w = gb["n_days"].to_numpy()
    gB = float(np.sum(w * gb["g_lag"].to_numpy()) / w.sum())
    dK = gB - gA
    res = {"g_lag_36a": gA, "g_lag_36bc": gB, "dK": dK, "obs": {}}
    for j, num, den in (("Y4_loop", "n_rep", "n_stmt"), ("Y3_branch", "n_par", "n_fu")):
        b, bse, sres, n = slope(d, j, "K", [36])
        o, lo, hi = boot_delta(dA, dB, num, den, seed=14)
        pred = b * dK
        band = 1.96 * np.hypot(bse * abs(dK), 0.0)
        # placebo: 36b vs 36c (no K step by construction of the contrast)
        pb, pc = daily.filter(pl.col("pt_date").is_in(days["36b"])), daily.filter(pl.col("pt_date").is_in(days["36c"]))
        po, plo, phi = boot_delta(pb, pc, num, den, seed=15)
        res["obs"][j] = {"observed": o, "obs_lo": lo, "obs_hi": hi, "pred_D1": pred, "pred_band95": band,
                         "slope_b": b, "slope_se": bse, "n_periods_fit": n,
                         "sign_agrees": bool(np.sign(o) == np.sign(pred)),
                         "within_band": bool(lo <= pred + band and hi >= pred - band),
                         "obs_outside_pred": bool(abs(o - pred) > band and not (lo <= pred <= hi)),
                         "placebo_36b_vs_36c": {"delta": po, "lo": plo, "hi": phi}}
    # herding share: point values only (no day bootstrap)
    hA = u.filter(pl.col("unit_id") == "36a")["herd_own"][0]
    hB = gb.select((pl.col("herd_own") * pl.col("n_days")).sum() / pl.col("n_days").sum()).item()
    b, bse, _, n = slope(d, "Y2_herd", "K", [36])
    res["obs"]["Y2_herd"] = {"observed": (hB - hA) if hA is not None and hB is not None else None, "pred_D1": b * dK,
                             "pred_band95": 1.96 * bse * abs(dK), "slope_b": b, "n_periods_fit": n,
                             "note": "point values; no day bootstrap"}
    return res


def ne42(d: pl.DataFrame) -> dict:
    dc = L.common_sample(d)
    sub = dc.filter(pl.col("goal_no").is_in([39, 40, 41])).sort("goal_no")
    K = dict(zip(sub["goal_no"].to_list(), sub["K"].to_list()))
    dK = K[40] - 0.5 * (K[39] + K[41])
    dlogNroom = float(np.log(2.0))
    res = {"K": K, "dK": dK, "dlogN_room": dlogNroom, "obs": {}}
    nfollow, ninside = 0, 0
    for j in L.OBS:
        y = dict(zip(sub["goal_no"].to_list(), sub[j].to_list()))
        if any(y.get(g) is None for g in (39, 40, 41)):
            res["obs"][j] = {"available": False}
            continue
        dev = y[40] - 0.5 * (y[39] + y[41])
        b, bse, sres, n = slope(d, j, "K", [39, 40, 41])
        c, cse, _, _ = slope(d, j, "logN", [39, 40, 41])
        pred = b * dK
        band = 1.96 * np.sqrt((bse * dK) ** 2 + 1.5 * sres ** 2)
        follow = bool(np.sign(dev) == np.sign(pred))
        inside = bool(abs(dev - pred) <= band)
        nfollow += follow
        ninside += inside
        res["obs"][j] = {"available": True, "values": y, "deviation_40": dev, "pred_D1": pred, "band95": band,
                         "pred_N": c * dlogNroom, "slope_b": b, "slope_se": bse, "slope_c": c, "resid_sd": sres,
                         "follows_D1_sign": follow, "follows_N_sign": bool(np.sign(dev) == np.sign(c * dlogNroom)),
                         "inside_band": inside, "exceeds_D1_size": bool(abs(dev) > abs(pred))}
    res["n_follow_D1"] = nfollow
    res["n_available"] = sum(1 for v in res["obs"].values() if v.get("available"))
    return res


def g51(d: pl.DataFrame, nu: pl.DataFrame) -> dict:
    u = nu.filter(pl.col("goal_no") == 51).sort("start")
    res = {"units": u.select("unit_id", "N_active", "g_lag", "c_x_trim", "R_hat", "R_n", "loop_rate", "n_stmt", "herd",
                             "herd_own").to_dicts(), "obs": {}}
    N = u["N_active"].to_numpy().astype(float)
    K = u["g_lag"].to_numpy().astype(float)

    def sp(a, b):
        m = np.isfinite(a) & np.isfinite(b)
        if m.sum() < 4:
            return {"rho": None, "n": int(m.sum())}
        r = spearmanr(a[m], b[m])
        n = int(m.sum())
        z, se = np.arctanh(np.clip(r.statistic, -0.999, 0.999)), 1 / np.sqrt(max(n - 3, 1))
        return {"rho": float(r.statistic), "p": float(r.pvalue), "n": n, "lo": float(np.tanh(z - 1.96 * se)),
                "hi": float(np.tanh(z + 1.96 * se))}

    res["rho_K_N"] = sp(K, N)
    flat = 0
    nav = 0
    for j, col in (("Y3_branch", "R_hat"), ("Y4_loop", "loop_rate"), ("Y2_herd", "herd_own"), ("Y2_herd_h11", "herd")):
        y = u[col].to_numpy().astype(float)
        rN, rK = sp(y, N), sp(y, K)
        jj = j.replace("_h11", "")
        b = slope(d, jj, "K", [51])[0]
        c = slope(d, jj, "logN", [51])[0]
        is_flat = rN["rho"] is not None and abs(rN["rho"]) < 0.3
        res["obs"][j] = {"rho_N": rN, "rho_K": rK, "across_period_slope_K": b, "across_period_slope_logN": c,
                         "flat_in_N": bool(is_flat),
                         "follows_K_sign": bool(rK["rho"] is not None and np.sign(rK["rho"]) == np.sign(b)),
                         "N_trend_with_N_slope_sign": bool(rN["rho"] is not None and abs(rN["rho"]) >= 0.5
                                                           and np.sign(rN["rho"]) == np.sign(c))}
        if j != "Y2_herd_h11" and rN["rho"] is not None:
            nav += 1
            flat += is_flat
    res["n_flat"], res["n_available"] = flat, nav
    return res


def main():
    OUTD.mkdir(parents=True, exist_ok=True)
    d = L.load("primary")
    nu = pl.read_parquet(L.DATA / "natives_units.parquet")
    for name, fn in (("NE14", lambda: ne14(d, nu)), ("NE42", lambda: ne42(d)), ("G51", lambda: g51(d, nu))):
        r = fn()
        L.jdump(r, OUTD / f"{name}.json")
        print(name, {k: v for k, v in r.items() if k not in ("units",)})


if __name__ == "__main__":
    main()
