"""H101 summary: unit classes (Amendment A1 reading), period verdicts, prediction scoring, estimates rows, figures and
goal-period READMEs.

Usage: uv run python hypotheses/H101-pairwise-vs-multi-information/analysis/summarize.py [--no-estimates]
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
ROOT = HERE.parents[2]
HYP = ROOT / "hypotheses/H101-pairwise-vs-multi-information"
BASE = ROOT / "data/processed/H101-pairwise-vs-multi-information"
FIG = HYP / "figures"
sys.path.insert(0, str(ROOT / "infra/shared"))
NATIVE_FOLDERS = {"G12", "G51"}


def _ok(x):
    return x is not None and isinstance(x, (int, float)) and math.isfinite(x)


def unit_class(r):
    if r["N_med"] is not None and r["N_med"] < 6:
        return "no power (N < 6)"
    if not _ok(r.get("I_N_z")) or r["I_N_z"] < 2.33:
        return "unresolved"
    rf, z, rh, fr = r.get("rho_F"), r.get("ho_excess_z"), r.get("r_HO"), r.get("field_r_HO")
    if not _ok(rf):
        return "unresolved"
    beyond = _ok(z) and z >= 2.33 and _ok(rh) and _ok(fr) and rh > fr
    if rf >= 0.9:
        return "pairs + fields" + (" (remainder above field ref.)" if beyond else "")
    if rf >= 0.8:
        return "partial (0.8-0.9)" + (" (remainder above field ref.)" if beyond else "")
    return "higher-order candidate" if beyond else "low rho_F (within field ref.)"


def period_verdict(classes):
    c = [x for x in classes if x not in ("no power (N < 6)", "unresolved")]
    if not c:
        return "descriptive"
    if any(x == "higher-order candidate" for x in c):
        return "failed"
    if all(x == "pairs + fields" for x in c):
        return "descriptive"
    if sum(x.startswith("pairs + fields") for x in c) / len(c) >= 0.5 and not any("above" in x for x in c):
        return "descriptive"
    return "mixed"


def fmt(x, nd=3):
    return "–" if not _ok(x if not isinstance(x, (np.floating,)) else float(x)) else f"{x:.{nd}f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-estimates", action="store_true")
    a = ap.parse_args()
    C = pl.read_parquet(BASE / "results" / "units_conv.parquet")
    Pj = pl.read_parquet(BASE / "results" / "units_proj.parquet")
    rows = C.to_dicts()
    for r in rows:
        r["class"] = unit_class(r)
    C = pl.DataFrame(rows, infer_schema_length=None)
    C.write_parquet(BASE / "results" / "units_conv_classed.parquet")
    m = C.filter(pl.col("variant") == "main")
    prow = Pj.filter(pl.col("ok")).to_dicts()
    for r in prow:
        r["class"] = unit_class(r)
    Pj = pl.DataFrame(prow, infer_schema_length=None)
    # ------------------------------------------------------------------ scoring
    sc = {}
    big = m.filter(pl.col("N_med") >= 6)
    res = big.filter(pl.col("I_N_z") >= 2.33)
    sc["n_units"] = m.height
    sc["resolved_IN"] = int((m["I_N_z"] >= 2.33).sum())
    sc["N_ge_6_resolved"] = res.height
    for reg in ("I", "II", "III"):
        x = m.filter(pl.col("regime") == reg)
        sc[f"regime_{reg}"] = {"units": x.height, "rho_raw_med": x["rho_raw"].median(), "phi_med": x["phi"].median(),
                               "rho_F_med": x["rho_F"].median(), "rho_F_ge_0.9": float((x["rho_F"] >= 0.9).mean()),
                               "rho_F_lt_0.8": float((x["rho_F"] < 0.8).mean()), "r_HO_med": x["r_HO"].median(),
                               "field_r_HO_med": x["field_r_HO"].median(), "I_N_med": x["I_N"].median(),
                               "z_ge_2.33": float((x["ho_excess_z"] >= 2.33).mean())}
    sc["R1_share_rhoF_ge_0.9_resolved"] = float((m.filter(pl.col("I_N_z") >= 2.33)["rho_F"] >= 0.9).mean())
    sc["R1_median_rhoF"] = m["rho_F"].median()
    sc["R2_median_phi"] = m["phi"].median()
    sc["R3_median_rho_raw"] = m["rho_raw"].median()
    sc["R4_R7_share_z_ge_2.33_Nge6"] = float((res["ho_excess_z"] >= 2.33).mean())
    zz = res.filter(pl.col("ho_excess_z") >= 2.33)
    sc["R8_share_rHO_le_field"] = float((zz["r_HO"] <= zz["field_r_HO"]).mean())
    sc["egregore_rule_units"] = m.filter(pl.col("class") == "higher-order candidate")["unit"].to_list()
    pr = Pj.filter(pl.col("I_N_z") >= 2.33) if Pj.height else Pj
    sc["R5_projects"] = {"ok_units": Pj.height, "resolved": pr.height, "rho_F_med": pr["rho_F"].median() if pr.height else None,
                         "share_ge_0.9": float((pr["rho_F"] >= 0.9).mean()) if pr.height else None,
                         "z_ge_2.33": float((pr["ho_excess_z"] >= 2.33).mean()) if pr.height else None,
                         "higher_order_candidates": Pj.filter(pl.col("class") == "higher-order candidate")["unit"].to_list()}
    for v in ("noexo", "noW"):
        x = C.filter(pl.col("variant") == v)
        sc[f"variant_{v}"] = {"rho_F_med": x["rho_F"].median(), "phi_med": x["phi"].median(), "r_HO_med": x["r_HO"].median(),
                              "z_share": float((x["ho_excess_z"] >= 2.33).mean())}
    sc["classes"] = {k: int(v) for k, v in zip(*np.unique(m["class"].to_list(), return_counts=True))}
    (BASE / "results" / "scoring.json").write_text(json.dumps(sc, indent=1, default=float))
    print(json.dumps(sc, indent=1, default=float))
    figures(m)
    if not a.no_estimates:
        estimates(m, Pj)
    period_folders(m, Pj)


def estimates(m, Pj):
    import estimates as E
    rows = []
    for fam, df in (("conventions", m), ("projects", Pj)):
        for r in df.to_dicts():
            base = {"period_unit": r["unit"], "goal_no": r["goal_no"], "role": "replication", "ci_kind": "none",
                    "n_kind": "items x subsets (T-weighted)", "n": r["T_total"], "channel": f"co-usage ({fam})",
                    "source": f"data/processed/H101-pairwise-vs-multi-information/results/units_{'conv' if fam == 'conventions' else 'proj'}.parquet",
                    "status": "exploratory", "post_hoc": False,
                    "method": "max-ent hierarchy on 6-agent subsets per day (K>=1 support), parametric-bootstrap bias correction",
                    "notes": f"class={r['class']}; z_HO={fmt(r.get('ho_excess_z'), 2)}; field r_HO={fmt(r.get('field_r_HO'))}"}
            for stat, key, null in (("pairwise_sufficiency_after_field_rhoF", "rho_F", "pairwise truth (1)"),
                                    ("schneidman_I2_over_IN_raw", "rho_raw", "pairwise truth (1); uninformative here (A1)"),
                                    ("shared_field_share_phi", "phi", "none"),
                                    ("higher_order_remainder_rHO", "r_HO", "pairwise-truth bootstrap (z in notes); latent-field reference"),
                                    ("multi_information_IN", "I_N", "independent model (bootstrap)")):
                v = r.get(key)
                if _ok(v):
                    rows.append({**base, "statistic": stat, "estimate": v, "ci_lo": None, "ci_hi": None, "null": null})
    E.write_estimates(rows, hypothesis="H101")
    print("estimates rows:", len(rows))


def figures(m):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    FIG.mkdir(parents=True, exist_ok=True)
    col = {"I": "#2c7fb8", "II": "#7f8c8d", "III": "#c0392b"}
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.8))
    for reg in ("I", "II", "III"):
        s = m.filter((pl.col("regime") == reg) & (pl.col("N_med") >= 6))
        ax[0].scatter(s["phi"], s["rho_F"], s=12, color=col[reg], alpha=0.8, label=f"regime {reg}", edgecolor="none")
        ax[1].scatter(s["field_r_HO"], s["r_HO"], s=12, color=col[reg], alpha=0.8, edgecolor="none")
    ax[0].axhline(0.9, color="k", lw=0.6, ls="--")
    ax[0].axhline(0.8, color="k", lw=0.6, ls=":")
    ax[0].set_xlabel(r"shared-field share $\phi$ of $I_N$", fontsize=7)
    ax[0].set_ylabel(r"pairwise sufficiency after fields $\rho_F$", fontsize=7)
    ax[0].set_ylim(0.6, 1.05)
    ax[0].legend(fontsize=6, frameon=False)
    ax[0].set_title("conventions, units with N >= 6", fontsize=7)
    lim = [-0.02, 0.26]
    ax[1].plot(lim, lim, "k--", lw=0.6)
    ax[1].set_xlim(lim)
    ax[1].set_ylim(-0.02, 0.16)
    ax[1].set_xlabel(r"heterogeneous-field reference $r_{HO}$", fontsize=7)
    ax[1].set_ylabel(r"measured higher-order remainder $r_{HO}$", fontsize=7)
    ax[1].set_title("remainder vs field-only reference", fontsize=7)
    for a_ in ax:
        a_.tick_params(labelsize=6)
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs.pdf")
    plt.close(fig)
    s = pl.read_parquet(BASE / "synthetic" / "synthetic.parquet")
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.1))
    worlds = ["Y1", "Y3", "Y2"]
    lab = {"Y1": "pairwise", "Y3": "group term", "Y2": "uniform field"}
    units = ["4c", "27", "40", "51g"]
    for i, u in enumerate(units):
        for j, w in enumerate(worlds):
            x = s.filter((pl.col("unit") == u) & (pl.col("world") == w))
            ax[0].scatter(np.full(x.height, i + (j - 1) * 0.22), x["rho_F"].clip(0.5, 1.3), s=6,
                          color=["#2c7fb8", "#c0392b", "#7f8c8d"][j], label=lab[w] if i == 0 else None)
            ax[1].scatter(np.full(x.height, i + (j - 1) * 0.22), x["ho_excess_z"].clip(-5, 15), s=6,
                          color=["#2c7fb8", "#c0392b", "#7f8c8d"][j])
    ax[0].axhline(0.9, color="k", lw=0.5, ls="--")
    ax[0].axhline(0.8, color="k", lw=0.5, ls=":")
    ax[0].set_ylabel(r"$\rho_F$ (clipped)", fontsize=7)
    ax[1].axhline(2.33, color="k", lw=0.5, ls="--")
    ax[1].set_ylabel(r"remainder $z$ vs pairwise bootstrap", fontsize=7)
    for a_ in ax:
        a_.set_xticks(range(len(units)), [f"{u} (N~{n})" for u, n in zip(units, (4, 10, 13, 19))], fontsize=6)
        a_.tick_params(labelsize=6)
    ax[0].legend(fontsize=6, frameon=False, loc="lower left")
    fig.tight_layout()
    fig.savefig(FIG / "synthetic.pdf")
    plt.close(fig)


def period_folders(m, Pj):
    for g in sorted(m["goal_no"].unique().to_list()):
        tag = f"G{g:02d}"
        if tag in NATIVE_FOLDERS:
            continue
        d = HYP / "goalperiod-subhypotheses" / tag
        d.mkdir(parents=True, exist_ok=True)
        s = m.filter(pl.col("goal_no") == g).sort("unit")
        verdict = period_verdict(s["class"].to_list())
        units = s["unit"].to_list()
        lines = [f"# H101 × {tag}: goal period #{g}", "", f"**Verdict:** {verdict}", "**Role:** replication (exploratory)",
                 f"**Period:** goal #{g} · regime {s['regime'][0]} · units {', '.join(units)} · active agents per day (median) "
                 f"{', '.join(f'{x:g}' for x in s['N_med'].to_list())} · {int(s['T_total'].sum())} item-subset rows.", "",
                 "## Why this period", "Eligible for the replication layer (a day with ≥ 3 active agents and ≥ 30 convention items).", "",
                 "## Prediction",
                 "*The card's rule, written 2026-10-04 20:24 UTC before any H101 statistic, read through Amendment A1 (20:37 UTC, after the synthetic, before real data); this folder was written after the run and copies it.* "
                 "Pairwise sufficiency after field removal ρ_F ≥ 0.9 (HH322). A1: ρ_F ≥ 0.9 cannot exclude a planted group term, so it is *descriptive*; "
                 "a unit is a higher-order candidate only if ρ_F < 0.8, the remainder z ≥ 2.33 against the pairwise bootstrap and r_HO exceeds the heterogeneous-field reference (verdict *failed* for the HH). "
                 "Units with median N_d < 6 have no power (A1).", "",
                 "## Result", "",
                 "| Unit | N_d | I_N (nats/item) | I₂/I_N raw | φ (field share) | ρ_F | r_HO | z (remainder) | field-ref r_HO | class |",
                 "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for r in s.to_dicts():
            lines.append(f"| {r['unit']} | {r['N_med']:g} | {fmt(r['I_N'])} | {fmt(r['rho_raw'])} | {fmt(r['phi'])} | {fmt(r['rho_F'])} | "
                         f"{fmt(r['r_HO'])} | {fmt(r['ho_excess_z'], 1)} | {fmt(r['field_r_HO'])} | {r['class']} |")
        pj = Pj.filter(pl.col("goal_no") == g) if Pj.height else Pj
        if pj.height:
            lines += ["", "Projects (artifact markers; days pooled on agents active every day, so the agent-day field is not removed):", "",
                      "| Unit | items | I_N | ρ_F | r_HO | z | class |", "| --- | --- | --- | --- | --- | --- | --- |"]
            for r in pj.sort("unit").to_dicts():
                lines.append(f"| {r['unit']} | {int(r['T_total'])} | {fmt(r['I_N'])} | {fmt(r['rho_F'])} | {fmt(r['r_HO'])} | "
                             f"{fmt(r['ho_excess_z'], 1)} | {r['class']} |")
        lines += ["", "Data: `data/processed/H101-pairwise-vs-multi-information/results/units_conv_classed.parquet`, `units_proj.parquet`.", "",
                  "## Scorecard (period-specific axes)",
                  "C: multi-information against the independent bootstrap; remainder against the pairwise bootstrap. H: pairwise + uniform field against the heterogeneous-field reference. F: power by N (A1).", ""]
        (d / "README.md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
