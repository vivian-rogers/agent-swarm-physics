"""H46 synthetic validation (axis F), run before any real-data boundary statistic.

Village sampling: the real eligible-message schedule (agent, PT day, unit, regime), the real boundary catalog, the
real NE41 pair schedule (times, labels) and the real DQ4 agent-day output schedule. Message vectors are synthetic:
  x_m = q_i + B_{i,u} + eta_{i,d} + eps_m          (style; B = style shift per unit, zero unless scenario S2)
  y_m = c_i + G_u + A_{i,u} + w_{i,d} + xi_m       (content; G, A fresh per unit only in scenarios with a content shift)
eps and xi are resampled real within-agent-day residuals of the same agent (day structure destroyed: only the
noise distribution is borrowed). Day jitter eta, w ~ N(0, f * per-dimension message variance), f = 0.05.
Shift sizes delta are in units of that day-jitter SD, so a boundary with delta = 1 doubles the expected squared
displacement relative to a placebo day transition.
The estimator (day tables, unbiased D, placebo percentiles, class tests, Holm, verdict rules, fingerprint, ridge
information, NE41 stratified percentiles) is imported unchanged from h46lib.
Outputs: data/processed/H46-style-conserved-charge/synthetic/synthetic.json, figures/synthetic_validation.{pdf,png}
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h46lib as L  # noqa: E402

OUT = L.DATA / "synthetic"
FIG = L.ROOT / "hypotheses/H46-style-conserved-charge/figures"
F_JIT = 0.05


def residual_pools(m: pl.DataFrame, X: np.ndarray):
    """Within-agent-day residuals pooled per agent (real noise distribution, day structure removed)."""
    key = (m["agent"].cast(pl.Utf8) + "|" + m["pt_date"]).to_numpy()
    _, inv = np.unique(key, return_inverse=True)
    S = np.zeros((inv.max() + 1, X.shape[1]))
    np.add.at(S, inv, X)
    R = X - (S / np.bincount(inv)[:, None])[inv]
    ag = m["agent"].to_numpy()
    pools = {a: R[ag == a] for a in np.unique(ag)}
    means = {a: X[ag == a].mean(0) for a in np.unique(ag)}
    return pools, means, X.var(0)


def simulate(m, pools_s, mean_s, var_s, pools_c, mean_c, var_c, ds, dc, rng):
    ag = m["agent"].to_numpy()
    un = m["unit2"].to_numpy()
    key_d = (m["agent"].cast(pl.Utf8) + "|" + m["pt_date"]).to_numpy()
    _, dinv = np.unique(key_d, return_inverse=True)
    key_u = (m["agent"].cast(pl.Utf8) + "|" + m["unit2"]).to_numpy()
    _, uinv = np.unique(key_u, return_inverse=True)
    _, gu = np.unique(un, return_inverse=True)
    n = len(m)
    Xs = np.empty((n, len(var_s)))
    Xc = np.empty((n, len(var_c)))
    for a in np.unique(ag):
        ix = np.where(ag == a)[0]
        Xs[ix] = mean_s[a] + pools_s[a][rng.integers(0, len(pools_s[a]), len(ix))]
        Xc[ix] = mean_c[a] + pools_c[a][rng.integers(0, len(pools_c[a]), len(ix))]
    sd_s, sd_c = np.sqrt(F_JIT * var_s), np.sqrt(F_JIT * var_c)
    Xs += (rng.standard_normal((dinv.max() + 1, len(var_s))) * sd_s)[dinv]
    Xc += (rng.standard_normal((dinv.max() + 1, len(var_c))) * sd_c)[dinv]
    if ds > 0:
        Xs += (rng.standard_normal((uinv.max() + 1, len(var_s))) * sd_s * ds)[uinv]
    if dc > 0:   # half common (goal / unit field), half agent-specific
        Xc += (rng.standard_normal((gu.max() + 1, len(var_c))) * sd_c * dc / np.sqrt(2))[gu]
        Xc += (rng.standard_normal((uinv.max() + 1, len(var_c))) * sd_c * dc / np.sqrt(2))[uinv]
    return Xs, Xc


def run_day_level(m, bounds, first_day, pools, n_rep=100, seed=1):
    import os
    n_rep = int(os.environ.get("H46_NREP", n_rep))
    pools_s, mean_s, var_s, pools_c, mean_c, var_c = pools
    scen = {"S0 null": (0, 0), "S1 content d=1": (0, 1), "S1 content d=2": (0, 2),
            "S2 style d=0.5": (0.5, 2), "S2 style d=1": (1, 2), "S2 style d=2": (2, 2)}
    rng = np.random.default_rng(seed)
    res = {}
    fp = {}
    goal_b = bounds.filter(pl.col("cls") == "goal")
    for name, (ds, dc) in scen.items():
        t0 = time.time()
        rows = {c: {"content_moves": 0, "style_moves": 0, "conserved": 0, "broken": 0, "Ts": [], "Tc": []}
                for c in L.CLASSES}
        fps = {"style_cross": [], "style_ret": [], "content_cross": [], "content_ret": [], "chance": []}
        for rep in range(n_rep):
            Xs, Xc = simulate(m, pools_s, mean_s, var_s, pools_c, mean_c, var_c, ds, dc, rng)
            dt_ = L.day_table(m, {"style": Xs, "content": Xc})
            ev = L.eval_boundaries(bounds.filter(pl.col("cls").is_in(L.CLASSES)), dt_,
                                   {"style": "style", "content": "content"}, first_day)
            tests = {c: (L.class_test(ev.filter(pl.col("cls") == c), "content", n_rand=2000, n_boot=200, seed=rep),
                         L.class_test(ev.filter(pl.col("cls") == c), "style", n_rand=2000, n_boot=200, seed=rep))
                     for c in L.CLASSES}
            pc = L.holm([tests[c][0]["p_rand"] for c in L.CLASSES])
            ps = L.holm([tests[c][1]["p_rand"] for c in L.CLASSES])
            for k, c in enumerate(L.CLASSES):
                tc_, ts_ = tests[c]
                v = L.verdict(tc_, ts_, pc[k], ps[k])
                rows[c]["content_moves"] += int(L.moves(tc_, pc[k]))
                rows[c]["style_moves"] += int(L.moves(ts_, ps[k]))
                rows[c]["conserved"] += int(v == "conserved")
                rows[c]["broken"] += int(v == "broken")
                rows[c]["Ts"].append(ts_["T"])
                rows[c]["Tc"].append(tc_["T"])
            if rep < 20:   # fingerprint on goal switches (day-demeaned)
                L.add_demeaned(dt_, ["style", "content"])
                for b in goal_b.iter_rows(named=True):
                    fs = L.fingerprint_boundary(dt_, "style_dm", set(b["pre"]), set(b["post"]))
                    fc = L.fingerprint_boundary(dt_, "content_dm", set(b["pre"]), set(b["post"]))
                    if "cross" in fs:
                        fps["style_cross"].append(fs["cross"])
                        fps["content_cross"].append(fc["cross"])
                        fps["chance"].append(fs["chance"])
                        if np.isfinite(fs["ceiling"]):
                            fps["style_ret"].append(fs["cross"] / fs["ceiling"])
                        if np.isfinite(fc["ceiling"]) and fc["ceiling"] > 0:
                            fps["content_ret"].append(fc["cross"] / fc["ceiling"])
        res[name] = {c: {"P_content_moves": rows[c]["content_moves"] / n_rep, "P_style_moves": rows[c]["style_moves"] / n_rep,
                         "P_conserved": rows[c]["conserved"] / n_rep, "P_broken": rows[c]["broken"] / n_rep,
                         "Ts_mean": float(np.mean(rows[c]["Ts"])), "Tc_mean": float(np.mean(rows[c]["Tc"])),
                         "Ts_sd": float(np.std(rows[c]["Ts"])), "Tc_sd": float(np.std(rows[c]["Tc"]))}
                     for c in L.CLASSES}
        fp[name] = {k: float(np.mean(v)) if v else None for k, v in fps.items()}
        print(f"{name}: {time.time() - t0:.0f}s", {c: (res[name][c]['P_style_moves'], res[name][c]['P_content_moves'],
                                                        res[name][c]['P_conserved']) for c in L.CLASSES}, flush=True)
    return res, fp


def run_ne41(m, n_rep=40, seed=2):
    """OU content in time (tau = 20 min) with an optional jump at resets; style i.i.d. or with a jump."""
    pr = pl.read_parquet(L.DATA / "ne41_pairs.parquet").filter(pl.col("dedup"))
    pr = pr.sort("agent", "pt_date", "t")
    ag = pr["agent"].to_numpy()
    gap = np.maximum(pr["gap_s"].to_numpy().astype(float), 1.0)
    lab = pr["label"].to_numpy()
    unit = pr["unit2"].to_numpy()
    gb = np.floor(np.log10(gap) / L.GAP_BIN).astype(int)
    S1 = np.array([f"{a}|{u}|{g}" for a, u, g in zip(ag, unit, gb)])
    S2 = np.array([f"{u}|{g}" for u, g in zip(unit, gb)])
    cross = (lab == "forced") | (lab == "voluntary")
    rng = np.random.default_rng(seed)
    dim_c, dim_s = 32, 17
    scen = {"S0 OU, no jump": (0.0, 0.0), "S1 content jump 0.1": (0.1, 0.0), "S1 content jump 0.3": (0.3, 0.0),
            "S2 style jump 0.3": (0.3, 0.3)}
    out = {}
    tau = 1200.0
    for name, (jc, js) in scen.items():
        Tf_c, Tf_s, naive = [], [], []
        pw_c, pw_s = 0, 0
        for rep in range(n_rep):
            # pairs are consecutive messages; simulate pair endpoints directly from the OU transition
            z1 = rng.standard_normal((len(pr), dim_c))
            rho = np.exp(-gap / tau)[:, None]
            z2 = rho * z1 + np.sqrt(1 - rho ** 2) * rng.standard_normal((len(pr), dim_c))
            J = np.where(cross, jc, 0.0)[:, None]
            z2 = (1 - J) * z2 + np.sqrt(np.clip(J * (2 - J), 0, None)) * rng.standard_normal((len(pr), dim_c))
            y1 = z1 + 1.0 * rng.standard_normal((len(pr), dim_c))
            y2 = z2 + 1.0 * rng.standard_normal((len(pr), dim_c))
            y1 /= np.linalg.norm(y1, axis=1, keepdims=True)
            y2 /= np.linalg.norm(y2, axis=1, keepdims=True)
            dc = 1 - (y1 * y2).sum(1)
            s1 = rng.standard_normal((len(pr), dim_s))
            s2 = rng.standard_normal((len(pr), dim_s))
            if js > 0:   # style: persistent agent state with a jump at resets
                base = rng.standard_normal((len(pr), dim_s)) * 0.7
                Js = np.where(cross, js, 0.0)[:, None]
                base2 = (1 - Js) * base + np.sqrt(Js * (2 - Js)) * 0.7 * rng.standard_normal((len(pr), dim_s))
                s1, s2 = base + s1, base2 + s2
            dsty = ((s1 - s2) ** 2).sum(1)
            pc_, npc = L.pair_percentiles(lab, dc, S1, S2)
            ps_, nps = L.pair_percentiles(lab, dsty, S1, S2)
            f = lab == "forced"
            tc = L.mean_pct_test(pc_[f], npc[f], ag[f], n_rand=2000, n_boot=200, seed=rep)
            ts = L.mean_pct_test(ps_[f], nps[f], ag[f], n_rand=2000, n_boot=200, seed=rep)
            Tf_c.append(tc["T"])
            Tf_s.append(ts["T"])
            pw_c += int(tc["p_rand"] < 0.05 and tc["lo"] > 0.5)
            pw_s += int(ts["p_rand"] < 0.05 and ts["lo"] > 0.5)
            # naive (gap-unmatched) percentile vs all within pairs of the agent
            wd = dc[lab == "within"]
            naive.append(float(np.mean([(wd < v).mean() for v in dc[f][:2000]])))
        out[name] = {"T_forced_content": float(np.mean(Tf_c)), "T_forced_style": float(np.mean(Tf_s)),
                     "sd_content": float(np.std(Tf_c)), "sd_style": float(np.std(Tf_s)),
                     "P_content_moves": pw_c / n_rep, "P_style_moves": pw_s / n_rep,
                     "naive_unmatched_T_content": float(np.mean(naive)), "n_forced": int((lab == "forced").sum())}
        print("NE41", name, out[name], flush=True)
    return out


def run_kw(m, n_rep=30, seed=3):
    """Size and power of the within-agent information estimator on real agent-day schedules (#38, #41, #51)."""
    rng = np.random.default_rng(seed)
    dt0 = L.day_table(m.filter(pl.col("goal_no").is_in([38, 41, 51])), {"dummy": np.zeros((m.filter(
        pl.col("goal_no").is_in([38, 41, 51])).height, 1))})
    k = dt0.keys
    out = {}
    for g in (38, 41, 51):
        kk = k.filter(pl.col("goal_no") == g)
        a = kk["agent"].to_numpy()
        d = kk["pt_date"].to_numpy()
        n = kk.height
        res = {}
        for name, beta in {"null": 0.0, "content signal R2~0.05": 0.23, "content signal R2~0.15": 0.42}.items():
            hits, r2s = 0, []
            for rep in range(n_rep):
                X = rng.standard_normal((n, 17))
                y = beta * X[:, 0] + rng.standard_normal(n) + rng.standard_normal(len(np.unique(a)))[np.unique(a, return_inverse=True)[1]]
                r = L.info_within(X, y, a, d, n_perm=100, seed=rep)
                hits += int(r.get("p", 1) < 0.05)
                r2s.append(r.get("r2_cv", np.nan))
            res[name] = {"P_detect": hits / n_rep, "mean_r2_cv": float(np.nanmean(r2s))}
        out[f"G{g}"] = {"n_agent_days": n, **res}
        print("KW", g, out[f"G{g}"], flush=True)
    return out


def figure(day, ne41):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 2.6))
    scen = list(day)
    cls = L.CLASSES
    x = np.arange(len(scen))
    for c, mk in zip(cls, "osD^v"):
        axs[0].plot(x, [day[s][c]["P_style_moves"] for s in scen], marker=mk, lw=1, label=f"{c}: style moves")
    axs[0].plot(x, [day[s]["goal"]["P_content_moves"] for s in scen], "k--", lw=1, label="goal: content moves")
    axs[0].axhline(0.05, color="gray", lw=0.6, ls=":")
    axs[0].set_xticks(x, [s.replace(" ", "\n", 1) for s in scen], fontsize=6)
    axs[0].set_ylabel("detection rate (Holm, 100 reps)", fontsize=7)
    axs[0].set_title("(a) day-level classes, real schedule", fontsize=8)
    axs[0].legend(fontsize=5, ncol=1, frameon=False)
    axs[0].tick_params(labelsize=6)
    sc = list(ne41)
    xx = np.arange(len(sc))
    axs[1].bar(xx - 0.2, [ne41[s]["T_forced_content"] for s in sc], 0.2, label="content, gap-matched")
    axs[1].bar(xx, [ne41[s]["naive_unmatched_T_content"] for s in sc], 0.2, label="content, unmatched")
    axs[1].bar(xx + 0.2, [ne41[s]["T_forced_style"] for s in sc], 0.2, label="style, gap-matched")
    axs[1].axhline(0.5, color="k", lw=0.6)
    axs[1].set_ylim(0.4, 0.8)
    axs[1].set_xticks(xx, [s.replace(", ", "\n").replace(" jump", "\njump") for s in sc], fontsize=6)
    axs[1].set_ylabel("mean percentile T (forced erasures)", fontsize=7)
    axs[1].set_title("(b) NE41 pairs, OU recency confound", fontsize=8)
    axs[1].legend(fontsize=5, frameon=False)
    axs[1].tick_params(labelsize=6)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"synthetic_validation.{ext}", dpi=200)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    m = L.load_messages()
    bounds = pl.read_parquet(L.DATA / "boundaries.parquet")
    first_day = L.unit_first_days()
    Xs = L.style_matrix(m, "tc")
    Xc = L.content_matrix(m, "resid")
    ps, ms, vs = residual_pools(m, Xs)
    pc, mc, vc = residual_pools(m, Xc)
    t0 = time.time()
    day, fp = run_day_level(m, bounds, first_day, (ps, ms, vs, pc, mc, vc))
    ne41 = run_ne41(m)
    kw = run_kw(m)
    res = {"day_level": day, "fingerprint_goal_switches": fp, "ne41": ne41, "kw_info": kw,
           "params": {"f_jitter": F_JIT, "n_rep_day": 100, "n_rep_ne41": 40, "n_rep_kw": 30, "ou_tau_s": 1200},
           "runtime_s": time.time() - t0}
    (OUT / "synthetic.json").write_text(json.dumps(res, indent=1, default=float))
    figure(day, ne41)


if __name__ == "__main__":
    main()
