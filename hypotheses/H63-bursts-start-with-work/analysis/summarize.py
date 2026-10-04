"""H63 synthesis: pooled statistics, period verdicts, natives (G31, G39, G40), per-period estimates, figures.

    uv run python hypotheses/H63-bursts-start-with-work/analysis/summarize.py
"""
from __future__ import annotations

import json
import sys

import numpy as np
import polars as pl

import h63lib as L

sys.path.insert(0, str(L.ROOT / "infra/shared"))
import estimates as E  # noqa: E402

RES = L.OUT / "results"
FIG = L.ROOT / "hypotheses/H63-bursts-start-with-work/figures"


def tables(d, tag):
    return [json.loads(x) for x in d[f"tab_{tag}"].to_list()]


def main():
    d = pl.read_parquet(RES / "periods.parquet").sort("goal_no")
    d = d.with_columns(((pl.col("n_bursts") >= 3) & (pl.col("n_S") >= 5)).alias("tested"))
    T = d.filter(pl.col("tested"))
    out = {"tested_periods": T["goal_no"].to_list(), "n_bursts_tested": int(T["n_bursts"].sum()),
           "n_controls_tested": int(T["n_controls"].sum())}
    for tag in ("S", "L", "R", "B", "SB"):
        o = L.mh_or(tables(T, tag))
        out[f"pooled_OR_{tag}"] = o
        tb = np.array(tables(T, tag)).sum(0)
        out[f"counts_{tag}"] = tb.tolist()
    # shift null for pooled OR_S
    draws = pl.concat([pl.read_parquet(RES / f"shift_G{g:02d}.parquet") for g in T["goal_no"].to_list()])
    lor = []
    for k in range(draws["draw"].max() + 1):
        tb = [json.loads(x) for x in draws.filter(pl.col("draw") == k)["tab"].to_list()]
        o = L.mh_or(tb)
        if np.isfinite(o["or"]):
            lor.append(np.log(o["or"]))
    lor = np.array(lor)
    obs = np.log(out["pooled_OR_S"]["or"])
    out["shift_null"] = {"mean_logOR": float(lor.mean()), "sd": float(lor.std(ddof=1)),
                         "z": float((obs - lor.mean()) / lor.std(ddof=1)), "p_one_sided": float((lor >= obs).mean()),
                         "n": int(len(lor))}
    # ordering
    out["ordering"] = {"n_both": int(d["n_both"].sum()), "n_S_first": int(d["n_S_first"].sum())}
    from scipy.stats import binomtest
    nb = out["ordering"]["n_both"]
    out["ordering"]["p_two_sided"] = float(binomtest(out["ordering"]["n_S_first"], nb, 0.5).pvalue) if nb else None
    # hazard pooling (periods with finite SEs and >= 50 events)
    H = d.filter((pl.col("h_n_events") >= 50) & pl.col("h_dS_se").is_not_null())
    for k in ("dS", "dL", "S_minus_R", "S", "L"):
        out[f"re_{k}"] = L.re_pool(H[f"h_{k}"].to_numpy(), H[f"h_{k}_se"].to_numpy())
    out["re_periods"] = H["goal_no"].to_list()
    out["re_L_nowork"] = L.re_pool(H["h_L_nowork"].to_numpy(), H["h_L_nowork_se"].to_numpy())
    out["kappa_drop_share"] = 1 - out["re_L"]["mean"] / out["re_L_nowork"]["mean"]
    # period verdicts
    verdicts = {}
    for r in d.iter_rows(named=True):
        g = r["goal_no"]
        if not r["tested"]:
            verdicts[g] = "descriptive"
            continue
        p = L.mh_or([json.loads(r["tab_S"])]).get("p", 1.0)
        s_ok = (r["OR_S"] > 1) and (p < 0.05)
        h_ok = (r.get("h_dS_lo") or -1) > 0
        if s_ok and h_ok:
            verdicts[g] = "supported"
        elif (r["OR_S"] <= 1) and ((r.get("h_dS") or 0) <= 0):
            verdicts[g] = "failed"
        elif (not s_ok) and (not h_ok):
            verdicts[g] = "failed"
        else:
            verdicts[g] = "mixed"
    out["verdicts"] = verdicts
    # ---------------------------------------------------------------- natives
    nat = {}
    # G31: largest burst (trimmed primary; untrimmed reported)
    P = L.load(31)
    for tag, trim in (("trim", True), ("untrim", False)):
        aa = L.arrivals(P, trim=False)
        arr = aa.filter(pl.col("trim")) if trim else aa
        cl = L.clusters(arr, aa)
        pre = L.precedence(P, cl).filter(pl.col("quiet")).sort("n_agents", descending=True)
        top = pre.row(0, named=True)
        S = P["signals"].filter(pl.col("project") == top["project"])
        fsb = S.filter(pl.col("cls").is_in(["S", "B"]) & (pl.col("t") < top["tf"]) & (pl.col("t") >= top["tf"] - 3600))
        any_sb_before = S.filter(pl.col("cls").is_in(["S", "B", "D"]) & (pl.col("t") < top["tf"]))
        first_sb = S.filter(pl.col("cls").is_in(["S", "B"]))["t"].min()
        lk = P["links"].filter((pl.col("project") == top["project"]) & (pl.col("speaker_kind") == "agent"))
        first_l = lk.filter(pl.col("t") >= top["t0"] - 3600)["t"].min()
        nat[f"G31_{tag}"] = {"n_agents": top["n_agents"], "S_or_B_in_60min_before_tf": fsb.height > 0,
                            "any_S_B_D_before_tf": any_sb_before.height,
                            "min_from_first_SB_to_tf": (top["tf"] - first_sb) / 60 if first_sb is not None else None,
                            "first_SB_before_first_link": (first_sb is not None and first_l is not None
                                                           and first_sb < first_l),
                            "min_link_to_tf": (top["tf"] - first_l) / 60 if first_l is not None else None,
                            "S_pre": top["S_pre"], "L_pre": top["L_pre"], "B_pre": top["B_pre"]}
    # G39: worlds
    P = L.load(39)
    sig = P["signals"]
    births = sig.filter(pl.col("cls") == "B").select("project", pl.col("agent").alias("builder"),
                                                       pl.col("t").alias("t_birth"))
    aa = L.arrivals(P, trim=False)
    rows = []
    for r in births.iter_rows(named=True):
        p, b = r["project"], r["builder"]
        vis = aa.filter((pl.col("project") == p) & (pl.col("agent") != b)).sort("t")
        if vis["agent"].n_unique() < 2:
            continue
        dep = sig.filter((pl.col("project") == p) & pl.col("cls").is_in(["S", "D"]))
        dep_b = dep.filter(pl.col("agent") == b)
        fdep = dep["t"].min()
        lk = P["links"].filter((pl.col("project") == p) & (pl.col("agent") == b))
        rows.append({"project_idx": len(rows), "n_visitors": vis["agent"].n_unique(),
                     "deploy_before_first_visit": fdep is not None and fdep < vis["t"].min(),
                     "builder_deploy_before_builder_link": (dep_b["t"].min() is not None and lk["t"].min() is not None
                                                            and dep_b["t"].min() < lk["t"].min()),
                     "has_builder_link": lk.height > 0, "has_deploy": fdep is not None,
                     "min_deploy_to_first_visit": ((vis["t"].min() - fdep) / 60) if fdep is not None else None})
    W = pl.DataFrame(rows)
    nat["G39"] = {"n_worlds": W.height,
                  "share_deploy_before_first_visit": float(W["deploy_before_first_visit"].mean()) if W.height else None,
                  "share_deploy_before_link_among_linked": float(W.filter(pl.col("has_builder_link"))[
                      "builder_deploy_before_builder_link"].mean()) if W.filter(pl.col("has_builder_link")).height else None,
                  "n_linked": W.filter(pl.col("has_builder_link")).height,
                  "median_min_deploy_to_first_visit": float(W["min_deploy_to_first_visit"].drop_nulls().median())
                  if W.height else None,
                  "hazard_dS": d.filter(pl.col("goal_no") == 39)["h_dS"][0],
                  "hazard_dS_ci": [d.filter(pl.col("goal_no") == 39)["h_dS_lo"][0],
                                   d.filter(pl.col("goal_no") == 39)["h_dS_hi"][0]]}
    # G40: hub
    P = L.load(40)
    hub = P["touches"].group_by("project").agg(pl.col("agent").n_unique().alias("na")).sort("na", descending=True)[
        "project"][0]
    aa = L.arrivals(P, trim=False)
    cl = L.clusters(aa, aa)
    pre = L.precedence(P, cl).filter((pl.col("project") == hub)).sort("t0")
    hb = pre.filter(pl.col("n_agents") >= 3)
    first_dep = P["signals"].filter((pl.col("project") == hub) & pl.col("cls").is_in(["S", "D"]))["t"].min()
    kick = P["days"]["win_start"].min()
    if hb.height:
        h0 = hb.row(0, named=True)
        nat["G40"] = {"hub_burst_n_agents": h0["n_agents"], "t0_min_after_first_window": (h0["t0"] - kick) / 60,
                      "kick_led_60min": (h0["t0"] - kick) < 3600, "tf_before_first_deploy": first_dep is None or h0["tf"] < first_dep,
                      "min_first_deploy_after_tf": (first_dep - h0["tf"]) / 60 if first_dep is not None else None,
                      "OR_S_period": d.filter(pl.col("goal_no") == 40)["OR_S"][0],
                      "OR_S_ci": [d.filter(pl.col("goal_no") == 40)["OR_S_lo"][0], d.filter(pl.col("goal_no") == 40)["OR_S_hi"][0]]}
    out["natives"] = nat
    (RES / "summary.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, indent=1, default=float))
    # ---------------------------------------------------------------- estimates
    rows = []
    for r in d.iter_rows(named=True):
        g = r["goal_no"]
        unit = E.map_unit(g)
        role = "replication"
        tb = json.loads(r["tab_S"])
        o = L.mh_or([tb])
        nb = r["n_bursts"] + r["n_controls"]
        if np.isfinite(o.get("or", np.nan)):
            rows.append({"period_unit": unit, "goal_no": g, "statistic": "burst_OR_state_change_60min",
                         "channel": "attention", "estimate": float(np.log(o["or"])), "ci_lo": float(np.log(o["lo"])),
                         "ci_hi": float(np.log(o["hi"])), "ci_kind": "se_z", "se": o["log_se"], "n": float(nb),
                         "n_kind": "clusters (bursts + matched non-burst arrival clusters)",
                         "method": "H63 log Mantel-Haenszel OR of a deploy-type state change in the 60 min before the follower onset, herding bursts (>= 3 agents) vs 1-2-agent clusters; trimmed window; Haldane 0.5",
                         "null": "matched non-burst clusters; S time-shift +-30-120 min", "role": role,
                         "source": "data/processed/H63-bursts-start-with-work/results/periods.parquet",
                         "notes": f"verdict {verdicts[g]}"})
        if r.get("h_dS_se") is not None and np.isfinite(r.get("h_dS") or np.nan):
            for k, desc in (("dS", "h_S - h_S' (state change last 60 min minus next 60 min)"),
                            ("dL", "kappa - kappa' (link last 60 min minus next 60 min)")):
                rows.append({"period_unit": unit, "goal_no": g, "statistic": f"arrival_hazard_{k}_leadlag",
                             "channel": "attention", "estimate": r[f"h_{k}"], "ci_lo": r[f"h_{k}_lo"],
                             "ci_hi": r[f"h_{k}_hi"], "ci_kind": "percentile", "se": r[f"h_{k}_se"],
                             "n": float(r["h_n_events"]), "n_kind": "arrivals in the risk set",
                             "method": f"H63 Poisson arrival hazard, agent+project+day fields, 5-min bins, trimmed; {desc}; day-block bootstrap",
                             "null": "lead terms; day-block bootstrap", "role": role,
                             "source": "data/processed/H63-bursts-start-with-work/results/periods.parquet"})
    nat_rows = [{"period_unit": E.map_unit(39), "goal_no": 39, "statistic": "share_worlds_deploy_before_first_visit",
                 "channel": "attention", "estimate": nat["G39"]["share_deploy_before_first_visit"], "ci_lo": None,
                 "ci_hi": None, "ci_kind": "none", "n": float(nat["G39"]["n_worlds"]), "n_kind": "worlds",
                 "method": "H63 native: builder-born projects with >= 2 visitors; first deploy-type event before the first non-builder arrival",
                 "null": "none (descriptive)", "role": "native",
                 "source": "data/processed/H63-bursts-start-with-work/results/summary.json"}]
    E.write_estimates(rows + nat_rows, hypothesis="H63")
    print("estimates rows:", len(rows) + len(nat_rows))
    figures(d, out)


def figures(d, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    FIG.mkdir(parents=True, exist_ok=True)
    T = d.filter(pl.col("tested"))
    # Fig 1: share of bursts vs controls preceded by S and by a link, pooled; per-period ORs
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.6))
    cats = [("S", "state change"), ("R", "routine commit"), ("L", "chat link"), ("B", "birth")]
    xb, xc = [], []
    for tag, _ in cats:
        tb = np.array(out[f"counts_{tag}"])
        xb.append(tb[0, 0] / tb[0].sum())
        xc.append(tb[1, 0] / tb[1].sum())
    x = np.arange(len(cats))
    ax[0].bar(x - 0.18, xb, 0.36, color="#c0392b", label="herding bursts")
    ax[0].bar(x + 0.18, xc, 0.36, color="#7f8c8d", label="1-2 agent clusters")
    ax[0].set_xticks(x, [c[1] for c in cats], fontsize=7)
    ax[0].set_ylabel("share with event in 60 min\nbefore follower onset", fontsize=7)
    ax[0].legend(fontsize=6, frameon=False)
    ax[0].tick_params(labelsize=7)
    H = d.filter((pl.col("h_n_events") >= 50) & pl.col("h_dS_se").is_not_null())
    g = H["goal_no"].to_numpy()
    for k, (col, c) in enumerate((("dS", "#c0392b"), ("dL", "#2c7fb8"))):
        est, lo, hi = H[f"h_{col}"].to_numpy(), H[f"h_{col}_lo"].to_numpy(), H[f"h_{col}_hi"].to_numpy()
        yy = np.arange(len(g)) + (k - 0.5) * 0.3
        ax[1].errorbar(np.clip(est, -3, 3), yy, xerr=[np.clip(est - lo, 0, 3), np.clip(hi - est, 0, 3)], fmt="o",
                       ms=3, color=c, lw=0.8, label={"dS": "state change: past − next", "dL": "link: past − next"}[col])
    ax[1].axvline(0, color="k", lw=0.6)
    ax[1].set_yticks(np.arange(len(g)), [f"#{x}" for x in g], fontsize=6)
    ax[1].set_xlabel("lead–lag contrast (log hazard)", fontsize=7)
    ax[1].tick_params(labelsize=7)
    ax[1].legend(fontsize=6, frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs.pdf")
    plt.close(fig)
    # Fig 2: synthetic
    s = json.loads((L.OUT / "synthetic/summary.json").read_text())
    fig, ax = plt.subplots(figsize=(3.4, 2.0))
    ws = ["work", "burst", "link", "null"]
    ax.bar(np.arange(4) - 0.25, [s[w]["P1_pass"] for w in ws], 0.25, label="P1 (OR$_S$)", color="#e67e22")
    ax.bar(np.arange(4), [s[w]["P3_pass"] for w in ws], 0.25, label="P3 (lead–lag)", color="#8e44ad")
    ax.bar(np.arange(4) + 0.25, [s[w]["P1_and_P3"] for w in ws], 0.25, label="both", color="#2c3e50")
    ax.set_xticks(np.arange(4), ["work-led", "co-burst", "link-led", "null"], fontsize=7)
    ax.set_ylabel("pass rate (15 runs)", fontsize=7)
    ax.tick_params(labelsize=7)
    ax.legend(fontsize=6, frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "synthetic.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()
