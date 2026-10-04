"""H33 real-data analysis (exploratory, non-holdout, eligible units only): T1-T7 of the card.

T1 pooled within-unit shape (quadratic, natural spline, two-lines with Robin Hood breakpoint; cluster agent x unit);
T2 per period (two-lines at the pooled breakpoint, 3-df spline, quadratic; DerSimonian-Laird meta of b1, b2);
T3 day-blocked CV; T4 half-day cross-lag; T5 with/without activity controls; T6 self-repetition slope;
T7 swarm-day. Robustness: other outcomes, TV10/PR6/PR15, without #51, by regime, cluster bootstrap of the breakpoint.
Writes data/processed/H33-diversity-productivity/results.json, per-period figures and figures/curve_pooled.pdf.

Usage: uv run python hypotheses/H33-diversity-productivity/analysis/evaluate.py
"""
from __future__ import annotations

import datetime as dt
import json

import h33lib as H  # noqa: I001
import h33common as C
import numpy as np
import polars as pl

RUN_DATE = dt.datetime.now(dt.timezone.utc).date().isoformat()


def lin_slope(D, y_dm, x):
    b, V, e, G = D.fit(y_dm, D.dm(x))
    p, z = H.pval(b[0], np.sqrt(V[0, 0]), G)
    return float(b[0]), float(np.sqrt(V[0, 0])), p


def shape_block(x, y, Z, au, day, df=4, boot=0, seed=0):
    """T1 on one sample. Returns quadratic, two-lines, spline summary, linear slope, (bootstrap of xc and x_max)."""
    D = H.Design([au, day], au, Z)
    y_dm = D.dm(y)
    q = H.quad_test(D, y_dm, x)
    tl, sp = H.two_lines(D, y_dm, x, df)
    lb, lse, lp = lin_slope(D, y_dm, x)
    out = {"n": int(len(x)), "clusters": int(len(np.unique(au))), "quad": q, "quad_U": H.quad_supported(q, x),
           "two_lines": {k: v for k, v in tl.items()}, "linear": {"b": lb, "se": lse, "p": lp},
           "spline": {"x_max": sp["x_max"], "interior": sp["interior"],
                      "flat_range": [float(sp["flat_obs"].min()), float(sp["flat_obs"].max())] if len(sp["flat_obs"]) else None},
           "x_q10_50_90": np.quantile(x, [0.1, 0.5, 0.9]).tolist()}
    out["P1"] = bool(tl["u_supported"] and sp["interior"])
    if boot:
        rng = np.random.default_rng(seed)
        ua = np.unique(au)
        xcs, xms = [], []
        for _ in range(boot):
            pick = rng.choice(ua, len(ua), replace=True)
            idx = np.concatenate([np.flatnonzero(au == a) for a in pick])
            newau = np.concatenate([np.full((au == a).sum(), i) for i, a in enumerate(pick)])
            Db = H.Design([newau, H.codes(day[idx])], newau, Z[idx])
            tb, sb = H.two_lines(Db, Db.dm(y[idx]), x[idx], df)
            xcs.append(tb["xc"]); xms.append(sb["x_max"])
        out["boot"] = {"B": boot, "xc_90ci": np.quantile(xcs, [0.05, 0.95]).tolist(),
                       "xmax_90ci": np.quantile(xms, [0.05, 0.95]).tolist(),
                       "xmax_interior_share": float(np.mean([(np.quantile(x, 0.1) < v < np.quantile(x, 0.9)) for v in xms]))}
    return out, sp, D, y_dm


def per_period(ad, x, y, Z, xc):
    rows = []
    units = ad["unit"].to_numpy()
    for u in sorted(np.unique(units), key=lambda s: (int(s.rstrip("ab")), s)):
        m = units == u
        ag = ad["agent"].to_numpy()[m]
        D = H.Design([H.codes(ag), H.codes(ad["pt_date"].to_numpy()[m])], ag, Z[m])
        xu, yu = x[m], y[m]
        y_dm = D.dm(yu)
        rec = {"unit": u, "n": int(m.sum()), "G": int(len(np.unique(ag))), "mean_writes": float(np.expm1(yu).mean())}
        if (xu < xc).sum() >= 5 and (xu >= xc).sum() >= 5:
            r = H.interrupted(D, y_dm, xu, xc)
            rec.update({k: r[k] for k in ("b1", "se1", "p1", "b2", "se2", "p2", "n_lo", "n_hi")})
        else:
            rec.update({"b1": np.nan, "se1": np.nan, "p1": np.nan, "b2": np.nan, "se2": np.nan, "p2": np.nan,
                        "n_lo": int((xu < xc).sum()), "n_hi": int((xu >= xc).sum())})
        sp = H.spline_fit(D, y_dm, xu, df=3)
        q = H.quad_test(D, y_dm, xu)
        lb, lse, lp = lin_slope(D, y_dm, xu)
        sr = ad["selfrep"].to_numpy()[m].astype(float)
        sb, sse, spv = lin_slope(D, y_dm, sr)
        rec.update({"x_max": sp["x_max"], "interior": sp["interior"], "q_b2": q["b2"], "q_p2": q["p2"], "q_vertex": q["vertex"],
                    "lin_b": lb, "lin_p": lp, "sr_b": sb, "sr_se": sse, "sr_p": spv, "_sp": sp, "_resid": (xu, y_dm, D)})
        b1, b2 = rec["b1"], rec["b2"]
        if not np.isfinite(b1):
            v, why = "n/a", "fewer than 5 agent-days on one side of the pooled breakpoint"
        elif b1 > 0 and b2 < 0 and (rec["p1"] < 0.05 or rec["p2"] < 0.05):
            v, why = "supported", "inverted-U signs with at least one significant slope"
        elif (b1 > 0) == (b2 > 0):
            v = "failed"
            why = f"both slopes {'positive' if b1 > 0 else 'negative'}" + ("" if sp["interior"] else "; spline maximum at the edge")
        elif not sp["interior"]:
            v = "failed"
            why = "spline maximum at the edge of the period's PR10 range" + (" (b₁ > 0, b₂ < 0, neither significant)" if b1 > 0 else " (U-shaped signs)")
        else:
            v, why = "mixed", ("inverted-U signs, neither slope significant" if (b1 > 0 and b2 < 0) else "U-shaped signs with an interior spline maximum")
        rec["verdict"], rec["why"] = v, why
        rows.append(rec)
    return rows


def half_day(ad_all, el):
    h = ad_all.filter(pl.col("unit").is_in(el) & pl.col("pr6_am").is_not_null() & pl.col("pr6_pm").is_not_null())
    C.refuse_holdout(h["pt_date"].unique().to_list(), "half-day rows")
    au = H.codes(h["agent"].to_numpy(), h["unit"].to_numpy())
    day = H.codes(h["pt_date"].to_numpy())
    Z = np.column_stack([np.log(h["n_chat_raw"].to_numpy().astype(float)), np.log1p(h["engaged_min"].to_numpy().astype(float))])
    D = H.Design([au, day], au, Z)
    pam, ppm = h["pr6_am"].to_numpy().astype(float), h["pr6_pm"].to_numpy().astype(float)
    am_c, pm_c = ("commits_w_am", "commits_w_pm") if C.ROUND == "r1b" else ("writes_am", "writes_pm")
    wam, wpm = np.log1p(h[am_c].to_numpy().astype(float)), np.log1p(h[pm_c].to_numpy().astype(float))
    sd = lambda v: float(D.dm(v).std())  # noqa: E731
    # forward: diversity (am) -> output (pm) | output (am)
    bf, Vf, _, G = D.fit(D.dm(wpm), D.dm(np.column_stack([pam, wam])))
    pf, zf = H.pval(bf[0], np.sqrt(Vf[0, 0]), G)
    # forward, nonlinear: + pam^2
    bq, Vq, _, _ = D.fit(D.dm(wpm), D.dm(np.column_stack([pam, pam ** 2, wam])))
    pq, zq = H.pval(bq[1], np.sqrt(Vq[1, 1]), G)
    # reverse: output (am) -> diversity (pm) | diversity (am)
    br, Vr, _, _ = D.fit(D.dm(ppm), D.dm(np.column_stack([wam, pam])))
    pr_, zr = H.pval(br[0], np.sqrt(Vr[0, 0]), G)
    return {"n": int(h.height), "clusters": int(len(np.unique(au))),
            "fwd": {"b": float(bf[0]), "se": float(np.sqrt(Vf[0, 0])), "p": pf, "z": zf, "std_b": float(bf[0]) * sd(pam) / sd(wpm)},
            "fwd_quad": {"b2": float(bq[1]), "se": float(np.sqrt(Vq[1, 1])), "p": pq, "z": zq},
            "rev": {"b": float(br[0]), "se": float(np.sqrt(Vr[0, 0])), "p": pr_, "z": zr, "std_b": float(br[0]) * sd(wam) / sd(ppm)},
            "persistence": {"writes_am_on_pm": float(bf[1]), "pr_am_on_pm": float(br[1])}}


def swarm(el):
    sw = C.load_swarm_day().filter(pl.col("unit").is_in(el) & pl.col("prday_dd").is_not_null()).sort("pt_date")
    C.refuse_holdout(sw["pt_date"].unique().to_list(), "swarm-day rows")
    x = sw["prday_dd"].to_numpy().astype(float)
    y = np.log1p(sw["commits_per_agent" if C.ROUND == "r1b" else "writes_per_agent"].to_numpy().astype(float))
    un = H.codes(sw["unit"].to_numpy())
    D = H.Design([un], un, None)
    y_dm = D.dm(y)
    q = H.quad_test(D, y_dm, x)
    tl, sp = H.two_lines(D, y_dm, x, df=3)
    lb, lse, lp = lin_slope(D, y_dm, x)
    return {"n_days": int(sw.height), "units": int(len(np.unique(un))), "quad": q, "two_lines": tl,
            "linear": {"b": lb, "se": lse, "p": lp}, "pattern": bool(tl["b1"] > 0 and tl["b2"] < 0)}


def figures(res, sp, D, y_dm, x, per, ad):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    k = len(sp["beta"])
    B = H.ns_basis(x, sp["knots"])
    Bdm = D.dm(B, key=("spline", 4, hash(np.asarray(x, np.float64).tobytes())))
    X = np.column_stack([Bdm, D.Z])
    beta = np.linalg.lstsq(X, y_dm, rcond=None)[0]
    e = y_dm - X @ beta
    fx = B @ beta[:k]
    pr = fx - fx.mean() + e
    bins = np.quantile(x, np.linspace(0, 1, 11))
    bi = np.clip(np.digitize(x, bins[1:-1]), 0, 9)
    bx = [x[bi == i].mean() for i in range(10)]
    by = [pr[bi == i].mean() for i in range(10)]
    be = [pr[bi == i].std() / np.sqrt((bi == i).sum()) for i in range(10)]
    grid = sp["grid"]
    Bg = H.ns_basis(grid, sp["knots"])
    fg = Bg @ beta[:k]
    off = fx.mean()
    dBc = Bg - B.mean(0)  # pointwise SE of f(x) - mean_data f
    se = np.sqrt(np.einsum("ij,jk,ik->i", dBc, sp["V"], dBc))
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 2.9), gridspec_kw={"width_ratios": [1.15, 1]})
    ax = axes[0]
    ax.fill_between(grid, fg - off - 1.96 * se, fg - off + 1.96 * se, color="#4e79a7", alpha=0.15, lw=0)
    ax.plot(grid, fg - off, color="#4e79a7", lw=1.6, label="spline (4 df)")
    ax.errorbar(bx, by, yerr=1.96 * np.array(be), fmt="o", ms=3.5, color="k", lw=0.8, capsize=0, label="decile means")
    tl = res["pooled"]["two_lines"]
    ax.axvline(tl["xc"], color="#e15759", ls="--", lw=0.9)
    ax.text(tl["xc"] + 0.2, ax.get_ylim()[0] + 0.05 * (ax.get_ylim()[1] - ax.get_ylim()[0]), f"$x_c$={tl['xc']:.1f}",
            color="#e15759", fontsize=7.5)
    ax.set_xlabel("agent-day content PR10 (self-repeats removed)", fontsize=8.5)
    ax.set_ylabel("partial residual, log(1+" + ("work commits" if C.ROUND == "r1b" else "write turns") + ")", fontsize=8.5)
    ax.set_title(f"(a) pooled, {res['pooled']['n']} agent-days, {len(res['units'])} periods\n"
                 f"b$_1$={tl['b1']:+.3f} (p {tl['p1']:.2f}), b$_2$={tl['b2']:+.3f} (p {tl['p2']:.2f})", fontsize=8.5)
    ax.legend(fontsize=7, frameon=False, loc="upper left")
    ax.tick_params(labelsize=7.5)
    ax = axes[1]
    ok = [p for p in per if np.isfinite(p["b1"])]
    yy = np.arange(len(ok))[::-1]
    for j, p in zip(yy, ok):
        ax.errorbar(p["b1"], j + 0.15, xerr=1.96 * p["se1"], fmt="o", ms=3, color="#59a14f", lw=0.8)
        ax.errorbar(p["b2"], j - 0.15, xerr=1.96 * p["se2"], fmt="s", ms=3, color="#e15759", lw=0.8)
    m1, m2 = res["meta"]["b1"], res["meta"]["b2"]
    ax.errorbar(m1["est"], -1.2, xerr=1.96 * m1["se"], fmt="D", ms=4.5, color="#59a14f", lw=1.4, label="b$_1$ (below $x_c$)")
    ax.errorbar(m2["est"], -1.6, xerr=1.96 * m2["se"], fmt="D", ms=4.5, color="#e15759", lw=1.4, label="b$_2$ (above $x_c$)")
    ax.axvline(0, color="0.5", lw=0.8)
    ax.set_yticks(list(yy) + [-1.4])
    ax.set_yticklabels([f"#{p['unit']}" for p in ok] + ["RE meta"], fontsize=6.5)
    ax.set_xlim(-0.6, 0.6)
    ax.set_xlabel("slope per PR unit (95% CI; clipped)", fontsize=8.5)
    ax.set_title(f"(b) per period at $x_c$ ({len(ok)} of {len(per)} estimable)", fontsize=8.5)
    ax.legend(fontsize=6.5, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2)
    ax.tick_params(labelsize=7.5)
    fig.tight_layout()
    fig.savefig(C.FIG / "curve_pooled.pdf", bbox_inches="tight")
    plt.close(fig)
    # per-period small figures
    for p in per:
        xu, ydm, Du = p["_resid"]
        s = p["_sp"]
        kk = len(s["beta"])
        Bu = H.ns_basis(xu, s["knots"])
        Xu = np.column_stack([Du.dm(Bu), Du.Z])
        bu = np.linalg.lstsq(Xu, ydm, rcond=None)[0]
        eu = ydm - Xu @ bu
        fxu = Bu @ bu[:kk]
        pru = fxu - fxu.mean() + eu
        g = int(p["unit"].rstrip("ab"))
        fig, ax = plt.subplots(figsize=(3.4, 2.4))
        ax.scatter(xu, pru, s=6, color="0.6", lw=0)
        fgu = H.ns_basis(s["grid"], s["knots"]) @ bu[:kk]
        ax.plot(s["grid"], fgu - fxu.mean(), color="#4e79a7", lw=1.5)
        ax.axvline(res["pooled"]["two_lines"]["xc"], color="#e15759", ls="--", lw=0.8)
        ax.set_title(f"H33 #{p['unit']}: {p['verdict']} (b1 {p['b1']:+.2f}, b2 {p['b2']:+.2f})", fontsize=8)
        ax.set_xlabel("PR10", fontsize=8); ax.set_ylabel("partial resid. log(1+writes)", fontsize=7.5)
        ax.tick_params(labelsize=7)
        fig.tight_layout()
        (C.HYP / "goalperiod-subhypotheses" / f"G{g:02d}" / "figures").mkdir(parents=True, exist_ok=True)
        fig.savefig(C.HYP / "goalperiod-subhypotheses" / f"G{g:02d}" / "figures" / f"G{g:02d}_curve{C.SFX}.pdf")
        plt.close(fig)


def main():
    el = pl.read_parquet(C.OUT / "eligibility.parquet").filter("eligible")["unit"].to_list()
    ad, x, y, Z, au, day = H.load_pooled("pr10", C.Y_PRIMARY)
    res = {"run_date": RUN_DATE, "units": el, "round": C.ROUND, "y_primary": C.Y_PRIMARY}
    # T1 primary
    pooled, sp, D, y_dm = shape_block(x, y, Z, au, day, boot=200, seed=C.SEED)
    res["pooled"] = pooled
    xc = pooled["two_lines"]["xc"]
    print("T1", json.dumps({k: pooled[k] for k in ("n", "quad_U", "P1")}), pooled["two_lines"], pooled["linear"], pooled["spline"], pooled.get("boot"))
    # T5 no controls
    nc, _, _, _ = shape_block(x, y, np.zeros((len(x), 0)), au, day)
    res["no_controls"] = nc
    # T6 self-repetition
    sb, sse, spv = lin_slope(D, y_dm, ad["selfrep"].to_numpy().astype(float))
    res["selfrep"] = {"b": sb, "se": sse, "p": spv, "mean_selfrep": float(ad["selfrep"].mean()),
                      "share_days_selfrep_ge_0.2": float((ad["selfrep"] >= 0.2).mean())}
    # T3 CV (5 seeds)
    cvs = [H.cv_day_blocked(y, x, Z, np.array([f"{a}" for a in au]), day, k=5, seed=s) for s in range(5)]
    res["cv"] = {m: float(np.mean([c[m] for c in cvs])) for m in ("fe_controls", "linear", "quadratic", "spline")}
    res["cv"]["n"] = cvs[0]["n"]
    res["cv"]["d_quad_vs_lin"] = res["cv"]["quadratic"] - res["cv"]["linear"]
    res["cv"]["d_spline_vs_lin"] = res["cv"]["spline"] - res["cv"]["linear"]
    res["cv"]["d_lin_vs_fe"] = res["cv"]["linear"] - res["cv"]["fe_controls"]
    res["cv"]["fold_seeds_quad_better"] = int(sum(c["quadratic"] < c["linear"] for c in cvs))
    res["cv"]["fold_seeds_spline_better"] = int(sum(c["spline"] < c["linear"] for c in cvs))
    # T2 per period + meta
    per = per_period(ad, x, y, Z, xc)
    res["meta"] = {"b1": H.dersimonian_laird([p["b1"] for p in per], [p["se1"] for p in per]),
                   "b2": H.dersimonian_laird([p["b2"] for p in per], [p["se2"] for p in per])}
    okp = [p for p in per if np.isfinite(p["b1"])]
    res["meta"]["pattern_frac"] = float(np.mean([p["b1"] > 0 and p["b2"] < 0 for p in okp]))
    res["meta"]["verdicts"] = {v: sum(p["verdict"] == v for p in per) for v in ("supported", "mixed", "failed", "n/a")}
    res["meta"]["P2"] = bool(res["meta"]["b1"]["est"] > 0 and res["meta"]["b2"]["est"] < 0 and res["meta"]["pattern_frac"] >= 0.5)
    res["meta"]["selfrep"] = H.dersimonian_laird([p["sr_b"] for p in per], [p["sr_se"] for p in per])
    # T4 half-day
    res["half_day"] = half_day(C.load_agent_day(), el)
    # T7 swarm-day
    res["swarm"] = swarm(el)
    # Robustness
    rob = {}
    for ycol in C.Y_ROBUST:
        a2, x2, y2, Z2, au2, d2 = H.load_pooled("pr10", ycol)
        rob[f"y={ycol}"] = shape_block(x2, y2, Z2, au2, d2)[0]
    for xcol in C.X_ROBUST:
        a2, x2, y2, Z2, au2, d2 = H.load_pooled(xcol, C.Y_PRIMARY)
        rob[f"x={xcol}"] = shape_block(x2, y2, Z2, au2, d2)[0]
    m = ad["unit"].to_numpy() != "51"
    rob["without_51"] = shape_block(x[m], y[m], Z[m], H.codes(au[m]), H.codes(day[m]))[0]
    for reg in ("I", "III"):
        m = ad["regime"].to_numpy() == reg
        rob[f"regime_{reg}"] = shape_block(x[m], y[m], Z[m], H.codes(au[m]), H.codes(day[m]))[0]
    res["robustness"] = {k: {"n": v["n"], "P1": v["P1"], "quad_U": v["quad_U"], "b1": v["two_lines"]["b1"], "p1": v["two_lines"]["p1"],
                             "b2": v["two_lines"]["b2"], "p2": v["two_lines"]["p2"], "xc": v["two_lines"]["xc"],
                             "x_max": v["spline"]["x_max"], "interior": v["spline"]["interior"],
                             "lin_b": v["linear"]["b"], "lin_p": v["linear"]["p"], "q_b2": v["quad"]["b2"], "q_p2": v["quad"]["p2"]}
                         for k, v in rob.items()}
    figures(res, sp, D, y_dm, x, per, ad)
    res["per_period"] = [{k: (None if isinstance(v, float) and not np.isfinite(v) else v) for k, v in p.items() if not k.startswith("_")} for p in per]

    def clean(o):
        if isinstance(o, dict):
            return {k: clean(v) for k, v in o.items() if not isinstance(v, np.ndarray)}
        if isinstance(o, (list, tuple)):
            return [clean(v) for v in o]
        if isinstance(o, (np.floating, float)):
            return None if not np.isfinite(o) else float(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, np.bool_):
            return bool(o)
        return o
    res = clean(res)
    (C.OUT / "results.json").write_text(json.dumps(res, indent=1))
    C.write_provenance("hypotheses/H33-diversity-productivity/analysis/evaluate.py", ["H33 agent_day, swarm_day, eligibility"],
                       {"exploratory": True, "non_holdout_only": True, "boot": 200, "cv_seeds": 5})
    print(json.dumps({k: res[k] for k in ("selfrep", "cv", "meta", "half_day", "swarm")}, indent=1)[:6000])
    print(json.dumps(res["robustness"], indent=1))


if __name__ == "__main__":
    main()
