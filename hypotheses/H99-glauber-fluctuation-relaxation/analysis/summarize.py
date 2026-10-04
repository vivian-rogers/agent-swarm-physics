"""H99 summary: per-unit calls (A1/A2 rules), per-period verdicts, prediction scoring, estimates rows, figures and
the goal-period READMEs.

Usage: uv run python hypotheses/H99-glauber-fluctuation-relaxation/analysis/summarize.py [--no-estimates]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h99lib as L  # noqa: E402

ROOT = HERE.parents[2]
HYP = ROOT / "hypotheses/H99-glauber-fluctuation-relaxation"
BASE = ROOT / "data/processed/H99-glauber-fluctuation-relaxation"
FIG = HYP / "figures"
sys.path.insert(0, str(ROOT / "infra/shared"))

A1_T = 0.08
A2_T = 0.03
RHO_SPLIT = 0.15
NATIVE = {"NE42": ["39", "40", "41"], "NE14": ["36a", "36b", "36c"]}


def call_of(r: dict) -> tuple[str, str]:
    """(rule, call) for one unit-channel row."""
    if r["g_chi_lo"] is None or not np.isfinite(r["g_chi_lo"] if r["g_chi_lo"] is not None else np.nan):
        return ("-", "undefined")
    rp = r["rho_p1"]
    if rp is not None and np.isfinite(rp) and rp < RHO_SPLIT:
        rule = "A2"
        d1, l1, h1 = r["drho1"], r["drho1_lo"], r["drho1_hi"]
        d2, l2 = r["drho2"], r["drho2_lo"]
        fast = _ok(d1) and _ok(h1) and d1 <= -A2_T and h1 < 0
        slow = (_ok(d1) and _ok(l1) and d1 >= A2_T and l1 > 0) or (_ok(d2) and _ok(l2) and d2 >= A2_T and l2 > 0)
    else:
        rule = "A1"
        d1, h1 = r["dg"], r["dg_hi"]
        d2, l2 = r["dg2"], r["dg2_lo"]
        fast = _ok(d1) and _ok(h1) and d1 < -A1_T and h1 < 0
        slow = _ok(d2) and _ok(l2) and d2 > A1_T and l2 > 0
    resolved = r["g_chi_lo"] > 0
    if fast and slow:
        c = "both"
    elif fast:
        c = "fast"
    elif slow:
        c = "slow"
    else:
        c = "consistent"
    if not resolved:
        c = c + " (g unresolved)" if c != "consistent" else "unresolved"
    if rule == "A1" and rp is not None and _ok(rp) and rp >= 0.6 and c == "consistent":
        c = "consistent (low power)"
    if rule == "A2" and c == "consistent":
        c = "consistent (low power)"  # A2 power check: a sub-minute field of the real size is flagged in <= 6%
    return rule, c


def _ok(x):
    return x is not None and isinstance(x, (int, float)) and math.isfinite(x)


def period_verdict(calls: list[str]) -> str:
    res = [c for c in calls if not c.startswith("unresolved") and c != "undefined" and "unresolved" not in c]
    if not res:
        return "descriptive"
    cons = sum(c.startswith("consistent") for c in res)
    if cons == len(res):
        return "supported" if all(c == "consistent" for c in res) else "descriptive"
    if cons == 0 or (len(res) - cons) / len(res) > 0.5:
        return "failed"
    return "mixed"


def fmt(x, nd=3):
    return "–" if x is None or not _ok(float(x)) else f"{x:.{nd}f}"


def ci(r, k, nd=3):
    return f"{fmt(r.get(k), nd)} [{fmt(r.get(k + '_lo'), nd)}, {fmt(r.get(k + '_hi'), nd)}]"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-estimates", action="store_true")
    a = ap.parse_args()
    U = pl.read_parquet(BASE / "results" / "units.parquet")
    meta = pl.read_parquet(BASE / "unit_meta.parquet")
    K = pl.read_parquet(BASE / "results" / "kicks.parquet") if (BASE / "results" / "kicks.parquet").exists() else None
    rows = U.to_dicts()
    for r in rows:
        r["rule"], r["call"] = call_of(r)
    U = pl.DataFrame(rows, infer_schema_length=None)
    U.write_parquet(BASE / "results" / "units_called.parquet")
    main_ = U.filter(pl.col("variant") == "main")
    # ------------------------------------------------------------------ per-period verdicts and pooled numbers
    per = []
    for g in sorted(main_["goal_no"].unique().to_list()):
        for ch in ("talk", "act", "content"):
            s = main_.filter((pl.col("goal_no") == g) & (pl.col("channel") == ch))
            if not s.height:
                continue
            stat = "drho1" if ch == "talk" else "dg"
            p_g = L.re_pool(s["g_chi"].to_numpy(), s["g_chi_se"].to_numpy())
            p_d = L.re_pool(s[stat].to_numpy(), s[f"{stat}_se"].to_numpy()) if f"{stat}_se" in s.columns else {}
            per.append({"goal_no": g, "channel": ch, "regime": s["regime"][0], "units": s["unit"].to_list(),
                        "calls": s["call"].to_list(), "verdict": period_verdict(s["call"].to_list()),
                        "g_chi": p_g["mean"], "g_chi_lo": p_g["lo"], "g_chi_hi": p_g["hi"],
                        "stat": stat, "d": p_d.get("mean"), "d_lo": p_d.get("lo"), "d_hi": p_d.get("hi"),
                        "rho_p1_med": float(np.nanmedian(s["rho_p1"].to_numpy())),
                        "rho_c1_med": float(np.nanmedian(s["rho_c1"].to_numpy())),
                        "n_min": float(s["n_min"].sum())})
    P = pl.DataFrame(per, infer_schema_length=None)
    P.write_parquet(BASE / "results" / "periods.parquet")
    # ------------------------------------------------------------------ prediction scoring
    sc = {}
    tp = P.filter(pl.col("channel") == "talk")
    for reg in ("I", "II", "III"):
        t = tp.filter(pl.col("regime") == reg)
        res = t.filter(pl.col("verdict") != "descriptive")
        sc[f"talk_{reg}"] = {"periods": t.height, "resolved": res.height,
                             "verdicts": dict(zip(*np.unique(t["verdict"].to_list(), return_counts=True))) if t.height else {},
                             "median_drho1": float(np.nanmedian(t["d"].to_numpy())) if t.height else None}
    ucalls = {}
    for ch in ("talk", "act", "content"):
        s = main_.filter(pl.col("channel") == ch)
        ucalls[ch] = {reg: dict(zip(*np.unique(s.filter(pl.col("regime") == reg)["call"].to_list(), return_counts=True)))
                      for reg in ("I", "II", "III") if s.filter(pl.col("regime") == reg).height}
    sc["unit_calls"] = {ch: {reg: {k: int(v) for k, v in d.items()} for reg, d in dd.items()} for ch, dd in ucalls.items()}
    for ch in ("talk", "act"):
        s = main_.filter(pl.col("channel") == ch)
        sc[f"P6_{ch}_max_g_chi_hi"] = float(np.nanmax(s["g_chi_hi"].to_numpy()))
        sc[f"P6_{ch}_n_g_chi_hi_ge_0.6"] = int((s["g_chi_hi"].fill_nan(0) >= 0.6).sum())
    for ch in ("talk", "act", "content"):
        s = main_.filter(pl.col("channel") == ch)
        sc[f"{ch}_median_g_chi"] = float(np.nanmedian(s["g_chi"].to_numpy()))
        sc[f"{ch}_median_rho_p1"] = float(np.nanmedian(s["rho_p1"].to_numpy()))
        sc[f"{ch}_median_rho_c1"] = float(np.nanmedian(s["rho_c1"].to_numpy()))
        sc[f"{ch}_median_drho1"] = float(np.nanmedian(s["drho1"].to_numpy()))
        sc[f"{ch}_median_dg"] = float(np.nanmedian(s["dg"].to_numpy()))
    # variants: share of talk calls unchanged
    for v in ("stall", "untrimmed"):
        vv = U.filter(pl.col("variant") == v).select("unit", "channel", pl.col("call").alias("call_v"))
        j = main_.select("unit", "channel", "call").join(vv, on=["unit", "channel"])
        sc[f"variant_{v}_same_call"] = {ch: float((j.filter(pl.col("channel") == ch)["call"] == j.filter(pl.col("channel") == ch)["call_v"]).mean())
                                        for ch in ("talk", "act")}
    gte = U.filter((pl.col("channel") == "content") & (pl.col("variant") == "gte")).select("unit", pl.col("call").alias("call_g"), pl.col("dg").alias("dg_g"))
    j = main_.filter(pl.col("channel") == "content").select("unit", "call", "dg").join(gte, on="unit")
    sc["content_gte_same_call"] = float((j["call"] == j["call_g"]).mean()) if j.height else None
    sc["content_gte_dg_spearman"] = float(np.corrcoef(np.argsort(np.argsort(j["dg"].to_numpy())), np.argsort(np.argsort(j["dg_g"].to_numpy())))[0, 1]) if j.height > 3 else None
    if K is not None:
        kk = K.filter(pl.col("ok"))
        if kk.height:
            res_ = kk.filter(pl.col("lam_kick_lo").is_finite() & (pl.col("lam_kick_hi") - pl.col("lam_kick_lo") < 1.5))
            sc["P5"] = {"units_with_kicks": kk["unit"].to_list(), "n_units": kk.height,
                        "decay_resolved_units": res_["unit"].to_list(),
                        "resolved": res_.select("unit", "n_kicks", "lam_kick", "lam_kick_lo", "lam_kick_hi", "lam_pred_c",
                                                "lam_meas_c", "lam_perp").to_dicts(),
                        "amplitude_resolved": kk.filter(pl.col("resp01_lo") > 0)["unit"].to_list()}
    (BASE / "results" / "scoring.json").write_text(json.dumps(sc, indent=1, default=float))
    print(json.dumps(sc, indent=1, default=float)[:4000])
    figures(main_, P)
    if not a.no_estimates:
        estimates(main_)
    period_folders(main_, P, meta, K)


def estimates(m):
    import estimates as E
    rows = []
    for r in m.to_dicts():
        base = {"period_unit": r["unit"], "goal_no": r["goal_no"], "role": "replication", "ci_kind": "percentile",
                "ci_level": 0.95, "n_kind": "trimmed minutes" if r["channel"] != "content" else "agent-window pairs",
                "source": "data/processed/H99-glauber-fluctuation-relaxation/results/units_called.parquet",
                "post_hoc": r["channel"] == "talk", "status": "exploratory"}
        ch = {"talk": "talk", "act": "activity", "content": "content"}[r["channel"]]
        n = r["n_min"]
        rows.append({**base, "statistic": "g_chi_meanfield", "channel": ch, "estimate": r["g_chi"], "ci_lo": r["g_chi_lo"],
                     "ci_hi": r["g_chi_hi"], "n": n, "method": "mean-field split, 30-min block centring, all-present trim, 1-h block bootstrap",
                     "null": "independent agents (g_chi = 0); block-shift p in units_called", "notes": f"call={r['call']}"})
        if r["channel"] == "talk":
            rows.append({**base, "statistic": "drho1_collective_memory_excess", "channel": ch, "estimate": r["drho1"],
                         "ci_lo": r["drho1_lo"], "ci_hi": r["drho1_hi"], "n": n,
                         "method": "rho_c(1) - rho_perp(1)^(1-g_chi) (A2, post hoc), 1-h block bootstrap",
                         "null": "mean-field Glauber (0)", "notes": f"call={r['call']}; rule {r['rule']}"})
        else:
            rows.append({**base, "statistic": "dg_fluct_relax_gap", "channel": ch, "estimate": r["dg"], "ci_lo": r["dg_lo"],
                         "ci_hi": r["dg_hi"], "n": n, "method": "g_tau(lag 1) - g_chi (A1), 1-h (binary) / 2-h (content) block bootstrap",
                         "null": "mean-field Glauber (0)", "notes": f"call={r['call']}; rule {r['rule']}"})
    rows = [r for r in rows if r["estimate"] is not None and _ok(float(r["estimate"]))]
    for r in rows:
        for k in ("ci_lo", "ci_hi"):
            if r[k] is not None and not _ok(float(r[k])):
                r[k] = None
            if r["ci_lo"] is None or r["ci_hi"] is None:
                r["ci_kind"] = "none"
    E.write_estimates(rows, hypothesis="H99")
    print("estimates rows:", len(rows))


def figures(m, P):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    FIG.mkdir(parents=True, exist_ok=True)
    col = {"I": "#2c7fb8", "II": "#7f8c8d", "III": "#c0392b"}
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.8))
    t = m.filter(pl.col("channel") == "talk")
    for reg in ("I", "II", "III"):
        s = t.filter(pl.col("regime") == reg)
        pred = np.clip(s["rho_p1"].to_numpy(), 1e-3, 0.999) ** (1 - s["g_chi"].to_numpy())
        yv = s["rho_c1"].to_numpy()
        ax[0].scatter(pred, yv, s=10 + s["n_min"].to_numpy() / 150, color=col[reg], alpha=0.75, label=f"regime {reg}",
                      edgecolor="none")
    lim = [-0.02, 0.32]
    ax[0].plot(lim, lim, "k--", lw=0.6)
    ax[0].set_xlim(lim)
    ax[0].set_ylim([-0.17, 0.32])
    ax[0].axhline(0, color="k", lw=0.3)
    ax[0].set_xlabel(r"Glauber prediction $\rho_\perp(1)^{1-g_\chi}$", fontsize=7)
    ax[0].set_ylabel(r"measured collective $\rho_c(1)$ (talk)", fontsize=7)
    ax[0].set_title("talk: collective memory beyond the prediction", fontsize=7)
    ax[0].legend(fontsize=6, frameon=False, loc="lower right")
    for ch, mk in (("act", "o"), ("content", "s")):
        s = m.filter(pl.col("channel") == ch)
        for reg in ("I", "II", "III"):
            q = s.filter(pl.col("regime") == reg)
            ax[1].scatter(q["g_chi"], q["dg"], marker=mk, s=12, color=col[reg], alpha=0.7, edgecolor="none" if mk == "o" else col[reg],
                          facecolor=col[reg] if mk == "o" else "none")
    ax[1].axhline(0, color="k", lw=0.5)
    ax[1].axhspan(-A1_T, A1_T, color="0.9", zorder=0)
    ax[1].set_xlabel(r"fluctuation gain $g_\chi$", fontsize=7)
    ax[1].set_ylabel(r"gap $\Delta g = g_\tau - g_\chi$ (lag 1)", fontsize=7)
    ax[1].set_title("activity (filled) and content (open)", fontsize=7)
    ax[1].set_ylim(-0.8, 0.5)
    for a_ in ax:
        a_.tick_params(labelsize=6)
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs.pdf")
    plt.close(fig)
    # synthetic figure
    s1 = pl.read_parquet(BASE / "synthetic" / "synthetic_a2.parquet").filter(pl.col("tau0") == 0.25)
    s0 = pl.read_parquet(BASE / "synthetic" / "synthetic.parquet").filter((pl.col("obs") == "or") & (pl.col("tau0") == 1.0))
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.1))
    order = [("ind", 0.0), ("glauber", 0.2), ("glauber", 0.4), ("fast", 0.0), ("slow", 0.0), ("delay", 0.15)]
    labels = ["indep.", "Glauber .2", "Glauber .4", "fast field", "slow field", "delay"]
    for i, (w, g) in enumerate(order):
        y = s1.filter((pl.col("world") == w) & (pl.col("g_true").cast(pl.Float64).round(2) == g))["drho1"].to_numpy()
        y2 = s1.filter((pl.col("world") == w) & (pl.col("g_true").cast(pl.Float64).round(2) == g))["drho2"].to_numpy()
        ax[0].scatter(np.full(len(y), i - 0.12), y, s=6, color="#2c7fb8")
        ax[0].scatter(np.full(len(y2), i + 0.12), y2, s=6, color="#e67e22")
        z = s0.filter((pl.col("world") == w) & (pl.col("g_true").cast(pl.Float64).round(2) == g))
        ax[1].scatter(np.full(z.height, i - 0.12), z["dg"].to_numpy(), s=6, color="#2c7fb8")
        ax[1].scatter(np.full(z.height, i + 0.12), z["dg2"].to_numpy(), s=6, color="#e67e22")
    for a_, ttl, thr in ((ax[0], r"A2: $\Delta\rho_1$ (blue), $\Delta\rho_2$ (orange); $\tau_0$ = 15 s", A2_T),
                         (ax[1], r"A1: $\Delta g_1$ (blue), $\Delta g_2$ (orange); $\tau_0$ = 1 min", A1_T)):
        a_.axhline(0, color="k", lw=0.5)
        a_.axhspan(-thr, thr, color="0.9", zorder=0)
        a_.set_xticks(range(len(labels)), labels, fontsize=6, rotation=20)
        a_.set_title(ttl, fontsize=7)
        a_.tick_params(labelsize=6)
    ax[1].set_ylim(-0.6, 0.6)
    fig.tight_layout()
    fig.savefig(FIG / "synthetic.pdf")
    plt.close(fig)


def period_folders(m, P, meta, K):
    gp = pl.read_parquet(ROOT / "data/processed/shared/goal_periods.parquet") if (ROOT / "data/processed/shared/goal_periods.parquet").exists() else None
    for g in sorted(m["goal_no"].unique().to_list()):
        tag = f"G{g:02d}"
        d = HYP / "goalperiod-subhypotheses" / tag
        if tag == "G51":
            continue  # native folder; written by natives.py
        d.mkdir(parents=True, exist_ok=True)
        s = m.filter(pl.col("goal_no") == g)
        reg = s["regime"][0]
        pv = P.filter((pl.col("goal_no") == g) & (pl.col("channel") == "talk")).to_dicts()
        verdict = pv[0]["verdict"] if pv else "n/a"
        units = sorted(s["unit"].unique().to_list())
        N = meta.filter(pl.col("unit_id").is_in(units))["N_med"].to_list()
        title = ""
        if gp is not None and "goal_no" in gp.columns:
            r = gp.filter(pl.col("goal_no") == g)
            for c in ("title", "goal", "slug", "name"):
                if r.height and c in r.columns:
                    title = str(r[c][0])
                    break
        lines = [f"# H99 × {tag}: goal period #{g}" + (f" ({title[:80]})" if title else ""), "",
                 f"**Verdict:** {verdict}", "**Role:** replication (exploratory)",
                 f"**Period:** goal #{g} · regime {reg} · units {', '.join(units)} · N {', '.join(f'{x:g}' for x in N)} · "
                 f"{int(s.filter(pl.col('channel') == 'talk')['n_min'].sum())} trimmed minutes.", "",
                 "## Why this period",
                 "Eligible for the replication layer (≥ 3 agents with ≥ 30 record minutes, ≥ 60 trimmed minutes per day).", "",
                 "## Prediction",
                 "*The card's rule, written 2026-10-04 20:22 UTC before any H99 statistic and amended before real data (A1, 20:41 UTC) and after the first run (A2, 20:45 UTC, post hoc for talk); this folder was written after the run and copies it.* "
                 "Glauber consistency: no field call on the talk channel (A2 rule: |Δρ| < 0.03 or CI covering 0) in units with a resolved fluctuation gain. "
                 "Supported if every resolved talk unit is consistent; failed if most resolved units carry a field call; descriptive if no unit has a resolved g_χ; mixed otherwise. "
                 + ("Regime I is predicted to fail in the fast-field direction (P2)." if reg == "I" else
                    "Regime III is predicted to be consistent (P1)." if reg == "III" else ""), "",
                 "## Result", "",
                 "| Unit | channel | g_χ [95%] | ρ_c(1) | ρ_⊥(1) | gap (Δρ₁ talk / Δg₁ other) [95%] | lag 2 | call |",
                 "| --- | --- | --- | --- | --- | --- | --- | --- |"]
        for r in s.sort("unit", "channel").to_dicts():
            if r["channel"] == "talk":
                gap, g2 = ci(r, "drho1"), fmt(r.get("drho2"))
            else:
                gap, g2 = ci(r, "dg"), fmt(r.get("dg2"))
            lines.append(f"| {r['unit']} | {r['channel']} | {ci(r, 'g_chi')} | {fmt(r['rho_c1'], 2)} | {fmt(r['rho_p1'], 2)} | "
                         f"{gap} | {g2} | {r['call']} |")
        if K is not None:
            kk = K.filter(pl.col("unit").is_in(units) & pl.col("ok"))
            if kk.height:
                lines += ["", "Talk kick layer (human messages as a field on the room; distributed-lag kernel of the room's talk count; "
                          "decay ratio λ = Σβ₁…₅ / Σβ₀…₄; A2 estimator):", "",
                          "| Unit | kicks | response at lags 0–1 [95%] | λ_kick [95%] | Glauber λ_c | measured ρ_c(1) | ρ_⊥(1) |",
                          "| --- | --- | --- | --- | --- | --- | --- |"]
                for r in kk.to_dicts():
                    lines.append(f"| {r['unit']} | {r['n_kicks']} | {fmt(r['resp01'], 2)} [{fmt(r['resp01_lo'], 2)}, {fmt(r['resp01_hi'], 2)}] | "
                                 f"{fmt(r['lam_kick'], 2)} [{fmt(r['lam_kick_lo'], 2)}, {fmt(r['lam_kick_hi'], 2)}] | "
                                 f"{fmt(r['lam_pred_c'], 3)} | {fmt(r['lam_meas_c'], 3)} | {fmt(r['lam_perp'], 3)} |")
        if pv:
            p = pv[0]
            lines += ["", f"Period pool (random effects over units, talk): g_χ = {fmt(p['g_chi'])} [{fmt(p['g_chi_lo'])}, {fmt(p['g_chi_hi'])}], "
                          f"Δρ₁ = {fmt(p['d'])} [{fmt(p['d_lo'])}, {fmt(p['d_hi'])}]."]
        lines += ["", "Data: `data/processed/H99-glauber-fluctuation-relaxation/results/units_called.parquet`, `periods.parquet`.", "",
                  "## Scorecard (period-specific axes)",
                  "C: g_χ against independence (bootstrap CI and block-shift null). D: the collective relaxation predicted from fluctuations (Δρ, Δg). H: Glauber against fast-field, slow-field and delayed-coupling readings.", ""]
        (d / "README.md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
