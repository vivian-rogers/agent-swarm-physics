"""H31 round-1 robustness and post hoc analyses (all flagged post hoc in the card; run after explore.py).

1. Confounds of the E-P slope: regime fixed effect, period length, N, excluding pre-NE09 periods (#17-#21),
   one observation per block (geometric-mean tau), leave-one-period-out influence.
2. Instant-consensus split of the 'frozen' class: criterion met in the onset window with onset after the block's
   first two windows (a one-window herding wave) vs frozen at the period start.
3. E-C divergence (alignment relaxing after the kickoff): relaxation time vs predictors (descriptive).
4. E-V (#26): rise time of the winner's declared share (last < 0.25 -> first >= 0.5), event time.

  uv run python hypotheses/H31-consensus-time-spectral-gap/analysis/robustness.py
Writes data/processed/H31-consensus-time-spectral-gap/robustness_w30.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h31lib as L  # noqa: E402


def boot_coef(X, y, cl, j=1, B=2000, seed=5):
    rng = np.random.default_rng(seed)
    u = np.unique(cl)
    groups = {c: np.flatnonzero(cl == c) for c in u}
    X1 = np.c_[np.ones(len(y)), X]
    b0 = np.linalg.lstsq(X1, y, rcond=None)[0][j]
    bs = []
    for _ in range(B):
        ii = np.concatenate([groups[c] for c in rng.choice(u, len(u), replace=True)])
        Xi = X1[ii]
        if np.linalg.matrix_rank(Xi) < X1.shape[1]:
            continue
        bs.append(np.linalg.lstsq(Xi, y[ii], rcond=None)[0][j])
    return dict(b=float(b0), lo=float(np.quantile(bs, .025)), hi=float(np.quantile(bs, .975)), n=int(len(y)),
                n_periods=int(len(u)))


def main():
    ep = pl.read_parquet(L.DATA / "events_ep_w30.parquet")
    out = {}
    unc = ep.filter(pl.col("consensus") & ~pl.col("frozen"))
    y = np.log(unc["tau_h"].to_numpy())
    x = -np.log(unc["l2_sym"].to_numpy())
    cl = unc["goal_no"].to_numpy()
    reg1 = (unc["regime"].to_numpy() == "I").astype(float)
    out["base"] = boot_coef(x[:, None], y, cl)
    out["regime_FE"] = boot_coef(np.c_[x, reg1], y, cl)
    out["regime_only_effect"] = boot_coef(reg1[:, None], y, cl)
    out["period_length"] = boot_coef(np.c_[x, np.log(unc["T_h"].to_numpy())], y, cl)
    out["with_logN"] = boot_coef(np.c_[x, np.log(unc["N_b"].to_numpy())], y, cl)
    out["with_t0"] = boot_coef(np.c_[x, unc["t0_h"].to_numpy() / unc["T_h"].to_numpy()], y, cl)
    for name, mask in (("regime_I_only", reg1 == 1), ("regime_II_III_only", reg1 == 0),
                       ("excl_preNE09", ~np.isin(cl, [17, 18, 19, 20, 21]))):
        if mask.sum() >= 5 and len(np.unique(cl[mask])) >= 3:
            out[name] = boot_coef(x[mask][:, None], y[mask], cl[mask])
    # one observation per block
    blk = unc.group_by("goal_no", "room").agg(pl.col("tau_h").log().mean().alias("ly"), pl.col("l2_sym").first(),
                                              pl.col("regime").first())
    out["block_level"] = boot_coef((-np.log(blk["l2_sym"].to_numpy()))[:, None], blk["ly"].to_numpy(), blk["goal_no"].to_numpy())
    # leave-one-period-out influence on the slope
    infl = {}
    for g in np.unique(cl):
        m = cl != g
        infl[int(g)] = float(L.ols(x[m], y[m])[1])
    out["loo_slope_range"] = [min(infl.values()), max(infl.values())]
    out["loo_slopes"] = infl

    # 2. instant vs frozen-at-start
    fr = ep.filter(pl.col("consensus") & pl.col("frozen"))
    inst = fr.filter(pl.col("t0_h") > 0.75 + 1e-6)
    start = fr.filter(pl.col("t0_h") <= 0.75 + 1e-6)
    out["frozen_split"] = dict(frozen_total=fr.height, frozen_at_start=start.height, instant_mid_period=inst.height,
                               instant_kick_locked=int(inst["kick_locked"].sum()),
                               start_kick_locked=int(start["kick_locked"].sum()),
                               instant_by_period={int(k): int(v) for k, v in inst.group_by("goal_no").len().rows()})
    # P4 recomputed counting instant events as abrupt (rise <= 1)
    rise = unc["rise"].drop_nulls().to_numpy()
    out["abrupt_incl_instant"] = float((np.sum(rise <= 1) + inst.height) / (len(rise) + inst.height))
    # instant share per block vs lambda2 (does a better-connected room produce more one-window waves?)
    pb = ep.filter(pl.col("consensus")).with_columns(
        (pl.col("frozen") & (pl.col("t0_h") > 0.75 + 1e-6)).alias("instant")).group_by("goal_no", "room").agg(
        pl.col("instant").mean().alias("f_inst"), pl.len().alias("n"), pl.col("l2_sym").first())
    if pb.height >= 5:
        r = np.corrcoef(np.log(pb["l2_sym"].to_numpy()), pb["f_inst"].to_numpy())[0, 1]
        out["instant_share_vs_log_l2"] = dict(r=float(r), n_blocks=pb.height)
    # kick locking of gradual (uncensored) events only
    out["kick_locked_uncensored"] = float(unc["kick_locked"].mean())
    out["kick_locked_instant"] = float(inst["kick_locked"].mean()) if inst.height else None
    out["kick_locked_start"] = float(start["kick_locked"].mean()) if start.height else None

    # 3. E-C divergence
    ec = pl.read_parquet(L.DATA / "events_ec.parquet")
    dv = ec.filter(pl.col("kind") == "divergence")
    out["ec_kinds"] = {k: int(v) for k, v in ec.group_by("kind").len().rows()}
    if dv.height >= 4:
        yd = np.log(dv["tau"].to_numpy())
        res = {}
        for p in ("l2_sym", "g_tr", "ul2_rw", "u", "N_b"):
            v = dv[p].to_numpy().astype(float)
            sgn = 1 if p == "N_b" else -1
            ok = np.isfinite(v) & (v > 0)
            if ok.sum() >= 4 and len(np.unique(dv["goal_no"].to_numpy()[ok])) >= 3:
                res[p] = boot_coef((sgn * np.log(v[ok]))[:, None], yd[ok], dv["goal_no"].to_numpy()[ok])
        out["ec_divergence_slopes"] = res
        out["ec_divergence_tau"] = dict(median=float(np.median(dv["tau"])), q10=float(np.quantile(dv["tau"], .1)),
                                        q90=float(np.quantile(dv["tau"], .9)), dA_median=float(np.median(dv["dA"])),
                                        A0_median=float(np.median(dv["A0"])), Ainf_median=float(np.median(dv["Ainf"])),
                                        periods=sorted(set(dv["goal_no"].to_list())))
    nn = ec.filter(pl.col("kind") == "none")
    out["ec_none_periods"] = sorted(set(nn["goal_no"].to_list()))

    # 4. E-V rise time (post hoc)
    e26 = json.loads((L.DATA / "ev26.json").read_text())
    tr = e26.get("trajectory", [])
    if tr:
        t = np.array([a[0] for a in tr])
        sh = np.array([a[1] for a in tr])
        n = np.array([a[2] for a in tr])
        ok = n >= 3
        tc_i = np.flatnonzero(ok & (sh >= 0.5))
        if len(tc_i):
            tc = tc_i[0]
            pre = np.flatnonzero(ok[:tc] & (sh[:tc] < 0.25))
            out["ev26_posthoc"] = dict(t_cons_h=float(t[tc]), t_last_below_025_h=float(t[pre[-1]]) if len(pre) else None,
                                       rise_h=float(t[tc] - t[pre[-1]]) if len(pre) else None,
                                       n_declarations_post_onset=int(len(t)),
                                       share_before=float(sh[pre[-1]]) if len(pre) else None,
                                       share_final=float(sh[-1]))
    (L.DATA / "robustness_w30.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps({k: v for k, v in out.items() if k != "loo_slopes"}, indent=1, default=float))


if __name__ == "__main__" and "--clock" not in sys.argv:
    main()


def activity_clock():
    """Post hoc: split log(1/lambda2) into an activity clock, log(1/msg_rate), and a structure term,
    log(msg_rate/lambda2). Also tau in message-count time (block agent messages between onset and consensus)."""
    ep = pl.read_parquet(L.DATA / "events_ep_w30.parquet")
    unc = ep.filter(pl.col("consensus") & ~pl.col("frozen"))
    y = np.log(unc["tau_h"].to_numpy())
    cl = unc["goal_no"].to_numpy()
    lr = np.log(unc["msg_rate"].to_numpy())
    l2 = np.log(unc["l2_sym"].to_numpy())
    out = {"corr_log_l2_log_msgrate_blocks": float(np.corrcoef(
        np.log(pl.read_parquet(L.DATA / "predictors_period.parquet").filter(pl.col("variant") == "all")["l2_sym"].to_numpy()),
        np.log(pl.read_parquet(L.DATA / "predictors_period.parquet").filter(pl.col("variant") == "all")["msg_rate"].to_numpy()))[0, 1])}
    out["clock_only"] = boot_coef((-lr)[:, None], y, cl)
    out["clock_plus_structure_clock"] = boot_coef(np.c_[-lr, lr - l2], y, cl, j=1)
    out["clock_plus_structure_structure"] = boot_coef(np.c_[-lr, lr - l2], y, cl, j=2)
    # tau in message-count time
    ntau = []
    for row in unc.iter_rows(named=True):
        P = L.load_period(row["goal_no"])
        m = P["msgs"].filter((pl.col("kind") == 0) & (pl.col("room") == row["room"]) & (pl.col("act") >= row["t0_h"] * 3600)
                             & (pl.col("act") < row["tc_h"] * 3600))
        ntau.append(max(m.height, 1))
    ym = np.log(np.array(ntau, float))
    out["msgtime_tau_median"] = float(np.median(ntau))
    out["msgtime_slope_on_log_inv_l2"] = boot_coef((-l2)[:, None], ym, cl)
    out["msgtime_slope_on_structure"] = boot_coef((lr - l2)[:, None], ym, cl)
    r = json.loads((L.DATA / "robustness_w30.json").read_text())
    r["activity_clock"] = out
    (L.DATA / "robustness_w30.json").write_text(json.dumps(r, indent=1, default=float))
    print(json.dumps(out, indent=1))


if __name__ == "__main__" and "--clock" in sys.argv:
    activity_clock()
