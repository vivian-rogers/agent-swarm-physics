"""H55 round-1 replication layer: the common estimators on every eligible non-holdout goal period.

  uv run python hypotheses/H55-norm-enforcer-immunity/analysis/explore.py
Outputs: data/processed/H55-norm-enforcer-immunity/replication/{per_period.parquet, summary.json, estimates_rows.parquet},
G<NN>/results.json for every period with any scorable estimator.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h55lib as L  # noqa: E402
from h55lib import H  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats, optimize  # noqa: E402

RD = H.OUT / "replication"
RD.mkdir(exist_ok=True)
RNG = np.random.default_rng(H.SEED + 10)


def load_steps(kind: str, version: str = "restate", sensor: str = "corr_jev"):
    if kind == "loop":
        st = pl.read_parquet(H.OUT / "loop_steps.parquet").filter((pl.col("version") == version) & pl.col("y").is_not_null())
        rd = pl.read_parquet(H.OUT / "reads_loop.parquet")
        vol = pl.read_parquet(H.OUT / "reads_loop_volume.parquet")
        return L.steps_with_reads(st, rd, vol, "anchor_id", sensor=sensor), rd
    st = pl.read_parquet(H.OUT / "blocked_steps.parquet").filter(pl.col("y").is_not_null())
    st = st.with_columns((pl.col("t0").cast(pl.Int64).cast(pl.Utf8) + "_" + pl.col("agent").cast(pl.Utf8)).alias("win_id"))
    rd = pl.read_parquet(H.OUT / "reads_blocked.parquet").with_columns(pl.lit(None, pl.Float32).alias("novelty"))
    vol = pl.read_parquet(H.OUT / "reads_blocked_volume.parquet")
    return L.steps_with_reads(st, rd, vol, "win_id", sensor=sensor), rd


def hazard_fe(s: pl.DataFrame):
    """Logistic escape ~ C + D + ln k + ln(1+items read) with agent fixed effects (robustness, O7)."""
    d = s.filter(pl.col("y").is_not_null())
    if d.filter(pl.col("treated")).height < 3:
        return None
    _, ag = np.unique(d["agent"].to_numpy(), return_inverse=True)
    X = np.c_[d["treated"].cast(int).to_numpy(), (d["n_dir"] > 0).cast(int).to_numpy(), np.log(d["k"].to_numpy()),
              np.log1p(d["items_read"].to_numpy())]
    y = d["y"].to_numpy().astype(float)
    nA = ag.max() + 1

    def nll(th):
        b, a = th[:4], th[4:]
        eta = X @ b + a[ag]
        p = 1 / (1 + np.exp(-eta))
        ll = y * np.log(p + 1e-12) + (1 - y) * np.log(1 - p + 1e-12)
        g = p - y
        return -ll.sum() + 0.01 * (a ** 2).sum(), np.r_[X.T @ g, np.bincount(ag, g, nA) + 0.02 * a]
    r = optimize.minimize(nll, np.zeros(4 + nA), jac=True, method="L-BFGS-B")
    # sandwich-free SE via observed information on the 4 slopes (agent FE profiled approximately)
    th = r.x
    eta = X @ th[:4] + th[4:][ag]
    p = 1 / (1 + np.exp(-eta))
    W = p * (1 - p)
    Xa = np.c_[X, np.eye(nA)[ag]]
    I = (Xa * W[:, None]).T @ Xa + np.diag(np.r_[np.zeros(4), 0.02 * np.ones(nA)])
    try:
        cov = np.linalg.inv(I)[:4, :4]
        se = np.sqrt(np.diag(cov))
    except np.linalg.LinAlgError:
        se = np.full(4, np.nan)
    return {"b_C": float(th[0]), "se_C": float(se[0]), "b_D": float(th[1]), "se_D": float(se[1]),
            "b_lnk": float(th[2]), "b_items": float(th[3]), "n": int(len(y))}


def main():
    msgs = pl.read_parquet(H.OUT / "messages.parquet")
    rates = L.sender_rates(msgs)
    pp = L.pair_table()
    periods = sorted(msgs["goal_no"].unique().to_list())
    loop_r, rd_loop = load_steps("loop", "restate")
    loop_c, _ = load_steps("loop", "copy")
    blk, rd_blk = load_steps("blocked")
    eps = pl.read_parquet(H.OUT / "loops.parquet").filter(pl.col("version") == "restate")
    reg = msgs.group_by("goal_no").agg(pl.col("regime").first().cast(pl.Utf8))
    regime = dict(reg.iter_rows())
    rows, est_rows = [], []
    for g in periods:
        r = {"goal_no": int(g), "regime": regime.get(g)}
        p = pp.filter(pl.col("goal_no") == g)
        rt = rates.filter(pl.col("goal_no") == g)
        fa = L.friction_agent(p, rt, R=5000, rng=RNG)
        fm = L.friction_message(p, rng=RNG)
        fml = L.friction_message(p.with_columns((pl.col("A_len") >= pl.col("A_len").quantile(2 / 3)).fill_null(False).alias("A_long")),
                                 xcol="A_long", rng=RNG, min_treated=20)
        r.update({f"P1_{k}": v for k, v in fa.items() if k in ("scorable", "n_agents", "rho", "p", "rho_partial", "p_partial", "why")})
        r.update({f"P2_{k}": v for k, v in fm.items() if k in ("scorable", "gamma", "se", "p", "lo", "hi", "n_treated", "raw_diff", "neg_share_diff", "why")})
        r["P2_placebo_len_gamma"] = fml.get("gamma")
        r["P2_placebo_len_p"] = fml.get("p")
        # P3: share of received hard opposes (conf >= 0.8) that are correction/decline subtypes
        op = p.filter(pl.col("y") == -1)
        r["P3_n_opp"] = op.height
        r["P3_corr_decl_share"] = float(op["opp_type"].is_in(["correction", "decline"]).mean()) if op.height else None
        r["P3_position_share"] = float((op["opp_type"] == "position").mean()) if op.height else None
        # sensor coverage
        am = msgs.filter((pl.col("goal_no") == g) & (pl.col("speaker_kind") == "agent"))
        r["n_agent_msgs"] = am.height
        r["n_parented"] = int(am["parent_id"].is_not_null().sum())
        r["n_corr_jev"] = int(am["corr_jev"].sum())
        r["S_p"] = 100 * r["n_corr_jev"] / max(r["n_parented"], 1)
        r["corr_per_100_addressed"] = 100 * r["n_corr_jev"] / max(int(am["addressed"].sum()), 1)
        # loops / blocked
        for nm, s in (("loopR", loop_r), ("loopC", loop_c), ("blk", blk)):
            sg = s.filter(pl.col("goal_no") == g)
            r[f"{nm}_steps"] = sg.height
            r[f"{nm}_dir_steps"] = int((sg["n_dir"] > 0).sum())
            r[f"{nm}_trt_steps"] = int(sg["treated"].sum())
            r[f"{nm}_escape"] = float(sg["y"].mean()) if sg.height else None
            ic = L.immune_contrast(sg, rng=RNG, min_treated=15) if sg.height else {"scorable": False}
            r[f"{nm}_immune_scorable"] = ic.get("scorable", False)
            r[f"{nm}_delta"] = ic.get("delta")
            r[f"{nm}_delta_p"] = ic.get("p")
            ad = L.address_contrast(sg, rng=RNG) if sg.height >= 30 else {"scorable": False}
            r[f"{nm}_addr_delta"] = ad.get("delta")
            r[f"{nm}_addr_lo"] = ad.get("lo")
            r[f"{nm}_addr_hi"] = ad.get("hi")
            r[f"{nm}_addr_p"] = ad.get("p")
            r[f"{nm}_addr_n"] = ad.get("n")
        # swarm: loop persistence and episode length
        eg = eps.filter(pl.col("goal_no") == g)
        r["loop_episodes"] = eg.height
        r["loop_mean_len"] = float(eg["length"].mean()) if eg.height else None
        r["pi_p"] = 1 - r["loopR_escape"] if r["loopR_escape"] is not None else None
        rows.append(r)
        # per-period estimate rows (schema of infra per_period_estimates; written locally, not to the shared table)
        for stat, val, se, pv, n in (("friction_rho", fa.get("rho"), None, fa.get("p"), fa.get("n_agents")),
                                     ("friction_gamma", fm.get("gamma"), fm.get("se"), fm.get("p"), fm.get("n_treated")),
                                     ("address_delta_loop", r["loopR_addr_delta"], None, r["loopR_addr_p"], r["loopR_addr_n"])):
            if val is not None:
                est_rows.append({"hypothesis": "H55", "goal_no": int(g), "statistic": stat, "value": float(val),
                                 "se": None if se is None else float(se), "p": None if pv is None else float(pv),
                                 "n": None if n is None else int(n), "role": "replication", "method": "h55lib"})
        gd = H.OUT / f"G{int(g):02d}"
        gd.mkdir(exist_ok=True)
        (gd / "results.json").write_text(json.dumps({"replication": r, "friction_agent": fa}, indent=1, default=str))
    df = pl.DataFrame(rows, infer_schema_length=None)
    df.write_parquet(RD / "per_period.parquet")
    pl.DataFrame(est_rows).write_parquet(RD / "estimates_rows.parquet")
    summ = {}
    # ---- P1 meta
    s1 = df.filter(pl.col("P1_scorable") == True)  # noqa: E712
    summ["P1"] = {"periods": s1["goal_no"].to_list(), "rho": s1["P1_rho"].to_list(), "p": s1["P1_p"].to_list(),
                  "n_pos": int((s1["P1_rho"] > 0).sum()), "k": s1.height,
                  "meta": L.fisher_z_meta(s1["P1_rho"].to_numpy(), s1["P1_n_agents"].to_numpy()),
                  "meta_partial": L.fisher_z_meta(s1["P1_rho_partial"].to_numpy(), s1["P1_n_agents"].to_numpy())}
    # ---- P2 meta
    s2 = df.filter(pl.col("P2_scorable") == True)  # noqa: E712
    summ["P2"] = {"periods": s2["goal_no"].to_list(), "gamma": s2["P2_gamma"].to_list(), "p": s2["P2_p"].to_list(),
                  "n_neg": int((s2["P2_gamma"] < 0).sum()), "k": s2.height,
                  "meta": L.random_effects(s2["P2_gamma"].to_numpy(), s2["P2_se"].to_numpy())}
    s2p = df.filter(pl.col("P2_placebo_len_gamma").is_not_null())
    summ["P2_placebo_len"] = {"k": s2p.height, "n_neg": int((s2p["P2_placebo_len_gamma"] < 0).sum()),
                              "median": float(s2p["P2_placebo_len_gamma"].median()) if s2p.height else None}
    s3 = df.filter(pl.col("P3_n_opp") >= 10)
    summ["P3"] = {"k": s3.height, "median_corr_decl_share": float(s3["P3_corr_decl_share"].median()) if s3.height else None,
                  "n_ge_half": int((s3["P3_corr_decl_share"] >= 0.5).sum()), "median_position_share": float(s3["P3_position_share"].median()) if s3.height else None}
    # ---- P4/P5 pooled within-unit matched contrasts (exception d), with variants
    for nm, s in (("P4_loop_restate", loop_r), ("P4_loop_copy", loop_c), ("P5_blocked", blk)):
        ic = L.immune_contrast(s, rng=RNG, B=2000)
        ic.pop("diffs", None); ic.pop("clusters", None)
        summ[nm] = ic
        if nm.startswith("P4"):
            icn = L.immune_contrast(s, novelty=True, rng=RNG, B=2000)
            icn.pop("diffs", None); icn.pop("clusters", None)
            summ[nm + "_novelty"] = icn
        summ[nm + "_hazard_fe"] = hazard_fe(s)
        summ[nm + "_counts"] = {"steps": s.height, "dir_steps": int((s["n_dir"] > 0).sum()), "trt_steps": int(s["treated"].sum())}
        # address effect pooled (P6)
        ad = L.address_contrast(s, rng=RNG, B=2000)
        summ[nm.replace("P4", "P6").replace("P5", "P6") + "_address"] = ad
    # soft dose and lexical (descriptive, attenuated) sensors for loops
    for sens in ("corr_lex",):
        s, _ = load_steps("loop", "restate", sensor=sens)
        ic = L.immune_contrast(s, rng=RNG, B=1000)
        ic.pop("diffs", None); ic.pop("clusters", None)
        summ[f"P4_loop_restate_sensor_{sens}"] = ic
        sb, _ = load_steps("blocked", sensor=sens)
        icb = L.immune_contrast(sb, rng=RNG, B=1000)
        icb.pop("diffs", None); icb.pop("clusters", None)
        summ[f"P5_blocked_sensor_{sens}"] = icb
    # k >= 1 loop robustness (any restatement, not only established loops)
    # ---- P7 swarm
    sw = df.filter((pl.col("loopR_steps") >= 30) & (pl.col("n_parented") >= 200))
    rho = stats.spearmanr(sw["S_p"], sw["pi_p"])
    swI = sw.filter(pl.col("regime") == "I")
    rhoI = stats.spearmanr(swI["S_p"], swI["pi_p"]) if swI.height >= 5 else None
    rho_len = stats.spearmanr(sw["S_p"], sw["loop_mean_len"])
    summ["P7"] = {"k": sw.height, "periods": sw["goal_no"].to_list(), "rho": float(rho.statistic), "p_two": float(rho.pvalue),
                  "p_one_less": float(rho.pvalue / 2 if rho.statistic < 0 else 1 - rho.pvalue / 2),
                  "rho_regimeI": None if rhoI is None else float(rhoI.statistic), "k_regimeI": swI.height,
                  "p_regimeI_two": None if rhoI is None else float(rhoI.pvalue),
                  "rho_len": float(rho_len.statistic), "p_len_two": float(rho_len.pvalue)}
    # ---- P8 HH210: share of restatement loop episodes with >= 1 Jev correction read during the episode
    st_all = pl.read_parquet(H.OUT / "loop_steps.parquet").filter(pl.col("version") == "restate")
    anc = pl.read_parquet(H.OUT / "stmt_anchors.parquet")
    lp = st_all.select("episode", "message_id", "goal_no")
    # include k=1 statement of each episode as an anchor too
    first = (pl.read_parquet(H.OUT / "loops.parquet").filter(pl.col("version") == "restate").select("episode"))
    ep_rd = rd_loop.group_by("anchor_id").agg(pl.col("corr_jev").sum().alias("nc"), pl.len().alias("nd"))
    e2 = lp.join(ep_rd, left_on="message_id", right_on="anchor_id", how="left").group_by("episode", "goal_no").agg(
        pl.col("nc").fill_null(0).sum(), pl.col("nd").fill_null(0).sum())
    summ["P8"] = {"episodes": e2.height, "share_with_jev_correction": float((e2["nc"] > 0).mean()),
                  "share_with_any_directed": float((e2["nd"] > 0).mean()),
                  "implied_true_share_upper": float(min(1.0, (e2["nc"] > 0).mean() / 0.107)),
                  "by_period": e2.group_by("goal_no").agg(pl.len(), (pl.col("nc") > 0).mean().alias("corr"), (pl.col("nd") > 0).mean().alias("dir")).sort("goal_no").to_dicts()}
    (RD / "summary.json").write_text(json.dumps(summ, indent=1, default=str))
    H.write_prov("replication", "hypotheses/H55-norm-enforcer-immunity/analysis/explore.py",
                 ["H55 messages/loops/blocked/reads", "reply_pairs"], {"min_sent": L.MIN_SENT, "min_recv": L.MIN_RECV,
                                                                      "immune_min_treated_per_period": 15})
    print(json.dumps({k: v for k, v in summ.items() if k != "P8"}, indent=1, default=str)[:6000])
    print("P8", {k: v for k, v in summ["P8"].items() if k != "by_period"})


if __name__ == "__main__":
    main()
