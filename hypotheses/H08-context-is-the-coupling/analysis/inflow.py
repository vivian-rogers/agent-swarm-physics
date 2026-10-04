"""C2: information inflow. Does new context per call (provider-aware uncached input tokens) track the room messages
first visible at that call, and does the inflow drive the next action?

  uv run python hypotheses/H08-context-is-the-coupling/analysis/inflow.py

Per regime-III period (turns.parquet from scheme/build_turns.py; non-holdout only):
- b: within-agent-day OLS slope of log(1 + uncached) on log(1 + n_new); partial R^2 (within);
- talk ratio: P(talk | n_new >= 1) / P(talk | n_new = 0);
- latency: Spearman rho(uncached, t - s) within agent-days (>= 30 turns; wake turns excluded), mean over agent-days.
Day-cluster bootstrap B = 200. Writes G<NN>/c2.json.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h08lib import *  # noqa: E402,F403
from scipy.stats import spearmanr  # noqa: E402

B = 200
C2_PERIODS = [36, 37, 38, 39, 40, 41, 42, 44, 51]


def run(g: int):
    f = OUT / gname(g) / "turns.parquet"
    if not f.exists():
        return None
    tu = pl.read_parquet(f)
    if g == 36:
        tu = tu.filter(pl.col("pt_date") >= "2026-03-24")
    tu = tu.sort("agent", "t_us").with_columns(pl.col("pause").shift(1).over("agent", "pt_date").fill_null(False).alias("prev_pause"))
    tu = tu.filter(pl.col("s_us") > -(2 ** 61))
    tok = tu.filter(pl.col("unc").is_not_nan() & (pl.col("unc") >= 0))
    days = sorted(tu["pt_date"].unique().to_list())
    dix = {d: i for i, d in enumerate(days)}
    nd = len(days)
    rng = np.random.default_rng(g)
    W = np.vstack([np.ones((1, nd)), rng.multinomial(nd, np.full(nd, 1 / nd), size=B)]).astype(float)
    out = {"period": gname(g), "n_days": nd, "n_turns": tu.height, "n_token_turns": tok.height,
           "token_share": tok.height / max(1, tu.height)}
    # within-agent-day regression, per-day sufficient statistics
    if tok.height > 500:
        x = np.log1p(tok["n_new"].to_numpy().astype(float)); y = np.log1p(tok["unc"].to_numpy().astype(float))
        grp = (tok["agent"].cast(pl.Int64) * 10000 + tok["pt_date"].replace_strict(dix, return_dtype=pl.Int64)).to_numpy()
        _, gi = np.unique(grp, return_inverse=True)
        xm = np.bincount(gi, x) / np.bincount(gi); ym = np.bincount(gi, y) / np.bincount(gi)
        xd, yd = x - xm[gi], y - ym[gi]
        di = tok["pt_date"].replace_strict(dix, return_dtype=pl.Int64).to_numpy()
        sxy = np.bincount(di, xd * yd, minlength=nd); sxx = np.bincount(di, xd * xd, minlength=nd)
        syy = np.bincount(di, yd * yd, minlength=nd)
        bb = (W @ sxy) / (W @ sxx)
        r2 = bb ** 2 * (W @ sxx) / (W @ syy)
        out["slope_b"] = ci(bb); out["partial_R2"] = ci(r2)
        out["mean_unc"] = float(np.mean(tok["unc"].to_numpy())); out["median_unc"] = float(np.median(tok["unc"].to_numpy()))
        out["n_new_share_pos"] = float(np.mean(tok["n_new"].to_numpy() > 0))
        # tokens per new message (slope in levels, within agent-day)
        xl = tok["n_new"].to_numpy().astype(float); yl = tok["unc"].to_numpy().astype(float)
        xlm = np.bincount(gi, xl) / np.bincount(gi); ylm = np.bincount(gi, yl) / np.bincount(gi)
        sl = np.bincount(di, (xl - xlm[gi]) * (yl - ylm[gi]), minlength=nd); sll = np.bincount(di, (xl - xlm[gi]) ** 2, minlength=nd)
        out["tokens_per_message"] = ci((W @ sl) / (W @ sll))
    # talk ratio (all turns)
    di = tu["pt_date"].replace_strict(dix, return_dtype=pl.Int64).to_numpy()
    talk = tu["talk"].to_numpy().astype(float); pos = tu["n_new"].to_numpy() > 0
    a1 = np.bincount(di, talk * pos, minlength=nd); n1 = np.bincount(di, pos.astype(float), minlength=nd)
    a0 = np.bincount(di, talk * ~pos, minlength=nd); n0 = np.bincount(di, (~pos).astype(float), minlength=nd)
    with np.errstate(invalid="ignore", divide="ignore"):
        out["talk_ratio"] = ci(((W @ a1) / (W @ n1)) / ((W @ a0) / (W @ n0)))
        out["p_talk_new"] = float(a1.sum() / n1.sum()); out["p_talk_nonew"] = float(a0.sum() / n0.sum())
    # dose: P(talk) by n_new bins
    bins = [0, 1, 2, 3, 5, 9, 17, 10 ** 6]
    nn = tu["n_new"].to_numpy()
    out["p_talk_by_new"] = {f"{bins[i]}-{bins[i + 1] - 1}": float(talk[(nn >= bins[i]) & (nn < bins[i + 1])].mean())
                            for i in range(len(bins) - 1) if ((nn >= bins[i]) & (nn < bins[i + 1])).sum() > 50}
    # latency vs uncached tokens, within agent-day Spearman (non-wake turns)
    lt = tok.filter(~pl.col("prev_pause")).with_columns(((pl.col("t_us") - pl.col("s_us")) / US).alias("lat"))
    rows = []
    for (a, d), sub in lt.group_by(["agent", "pt_date"]):
        if sub.height >= 30:
            rho = spearmanr(sub["unc"].to_numpy(), sub["lat"].to_numpy()).statistic
            if np.isfinite(rho):
                rows.append((dix[d], rho))
    if rows:
        dd = np.array([r[0] for r in rows]); rr = np.array([r[1] for r in rows])
        s = np.bincount(dd, rr, minlength=nd); n = np.bincount(dd, minlength=nd).astype(float)
        with np.errstate(invalid="ignore", divide="ignore"):
            out["rho_unc_latency"] = ci((W @ s) / (W @ n))
        out["n_agentdays_latency"] = len(rows)
    # POST HOC (2026-10-04, after b < 0 everywhere): control for the previous turn's action (its tool result is part of
    # this call's new input: screenshots vs bash output vs chat), and for whether the call follows a pause (cache expiry)
    if tok.height > 500 and "act" in tu.columns:
        tu2 = tu.with_columns(pl.col("act").shift(1).over("agent", "pt_date").fill_null("").alias("prev_act"))
        tok2 = tu2.filter(pl.col("unc").is_not_nan() & (pl.col("unc") >= 0))
        cls = {"bash": 1, "send_message_back_to_chat": 2, "": 3, "wait": 4, "get_pixel_coords_of_element": 5}
        pc = np.array([cls.get(a, 0) for a in tok2["prev_act"].to_list()])        # 0 = GUI / screenshot actions
        X = np.column_stack([np.log1p(tok2["n_new"].to_numpy().astype(float))] + [(pc == c).astype(float) for c in range(1, 6)]
                            + [tok2["prev_pause"].to_numpy().astype(float)])
        y = np.log1p(tok2["unc"].to_numpy().astype(float))
        grp = (tok2["agent"].cast(pl.Int64) * 10000 + tok2["pt_date"].replace_strict(dix, return_dtype=pl.Int64)).to_numpy()
        _, gi = np.unique(grp, return_inverse=True)
        cnt = np.bincount(gi).astype(float)
        Xd = X - (np.stack([np.bincount(gi, X[:, j]) for j in range(X.shape[1])], 1) / cnt[:, None])[gi]
        yd = y - (np.bincount(gi, y) / cnt)[gi]
        di2 = tok2["pt_date"].replace_strict(dix, return_dtype=pl.Int64).to_numpy()
        XtX = np.stack([Xd[di2 == k].T @ Xd[di2 == k] for k in range(nd)]); Xty = np.stack([Xd[di2 == k].T @ yd[di2 == k] for k in range(nd)])
        bs = np.array([np.linalg.lstsq(np.tensordot(w, XtX, 1), w @ Xty, rcond=None)[0] for w in W])
        out["posthoc_slope_b_prevaction"] = ci(bs[:, 0])
        out["posthoc_prev_action_effects"] = {n: ci(bs[:, j + 1]) for j, n in enumerate(["bash", "chat", "event_only", "wait", "pixel", "after_pause"])}
    jdump(out, OUT / gname(g) / "c2.json")
    print(f"{gname(g)}: b {out.get('slope_b')} | b|prev-action {out.get('posthoc_slope_b_prevaction')} R2 {out.get('partial_R2')} "
          f"talk ratio {out['talk_ratio']} rho_lat {out.get('rho_unc_latency')}", flush=True)
    return out


def main():
    for g in C2_PERIODS:
        run(g)
    write_provenance("c2 (G<NN>/c2.json)", "hypotheses/H08-context-is-the-coupling/analysis/inflow.py",
                     ["G<NN>/turns.parquet (H08 scheme)"], {"B": B, "token_rule": "H09 provider-aware"})


if __name__ == "__main__":
    main()
