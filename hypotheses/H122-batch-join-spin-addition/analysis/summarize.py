"""H122 summary: prediction table, figures, estimates rows, period READMEs.

    uv run python hypotheses/H122-batch-join-spin-addition/analysis/summarize.py [--no-estimates] [--no-readmes]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
D = ROOT / "data/processed/H122-batch-join-spin-addition"
RES = D / "results"
HYP = ROOT / "hypotheses/H122-batch-join-spin-addition"
FIG = HYP / "figures"
COL = {"I": "#2a78d6", "II": "#eb6834", "III": "#1baf7a"}
MK = {"I": "o", "II": "s", "III": "^"}


def ci(x, lo, hi, nd=2):
    f = f"{{:+.{nd}f}}"
    return f"{f.format(x)} [{f.format(lo)}, {f.format(hi)}]"


def figures(E: pl.DataFrame, P: pl.DataFrame | None):
    FIG.mkdir(exist_ok=True)
    plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False})
    e = E.sort("day1")
    fig, ax = plt.subplots(figsize=(3.4, 2.8))
    y = np.arange(e.height)
    for i, r in enumerate(e.to_dicts()):
        ax.errorbar(r["d_C_J"], i, xerr=[[r["d_C_J"] - r["d_C_J_lo"]], [r["d_C_J_hi"] - r["d_C_J"]]], fmt=MK[r["regime"]],
                    color=COL[r["regime"]], ms=4, elinewidth=0.8)
    ax.axvline(0, color="#52514e", lw=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{r['event']} (+{r['n_new']})" for r in e.to_dicts()], fontsize=6)
    ax.set_xlabel("ΔLL = LL(constant shift) − LL(couplings)\n(nats per 1,000 incumbent calls on days 1–2)")
    for reg in ("I", "II", "III"):
        ax.plot([], [], MK[reg], color=COL[reg], label=f"regime {reg}")
    ax.legend(fontsize=6, frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(FIG / "dLL_events_col.pdf")
    fig.savefig(FIG / "dLL_events_col.png", dpi=150)
    plt.close(fig)
    # coupling per newcomer read in F37 vs P12
    fig, ax = plt.subplots(figsize=(3.4, 2.6))
    for r in e.to_dicts():
        ax.errorbar(r["J_N"], r["J_N_p12"], xerr=[[r["J_N"] - r["J_N_lo"]], [r["J_N_hi"] - r["J_N"]]],
                    yerr=[[r["J_N_p12"] - r["J_N_p12_lo"]], [r["J_N_p12_hi"] - r["J_N_p12"]]], fmt=MK[r["regime"]],
                    color=COL[r["regime"]], ms=4, elinewidth=0.6)
        ax.annotate(r["event"].replace("J20", "'"), (r["J_N"], r["J_N_p12"]), fontsize=5, xytext=(2, 2),
                    textcoords="offset points", color="#52514e")
    lim = [min(e["J_N_lo"].min(), e["J_N_p12_lo"].min()), max(e["J_N_hi"].max(), e["J_N_p12_hi"].max())]
    ax.plot(lim, lim, color="#85847e", lw=0.8, ls="--", label="J(days 1–2) = J(days 3–7)")
    ax.axhline(0, color="#ecebe6", lw=0.6); ax.axvline(0, color="#ecebe6", lw=0.6)
    ax.set_xlabel("J_N fitted on days 3–7 (logit per newcomer read)")
    ax.set_ylabel("J_N fitted on days 1–2")
    ax.legend(fontsize=6, frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "J_stability_col.pdf")
    fig.savefig(FIG / "J_stability_col.png", dpi=150)
    plt.close(fig)


def estimates(E: pl.DataFrame):
    import estimates as Es
    pu = pl.read_parquet(ROOT / "data/processed/shared/period_units.parquet")
    rows = []
    for r in E.to_dicts():
        role = "native" if r["event"] in ("NE27", "NE32") else "replication"
        hit = pu.filter(pl.col("days").list.contains(r["day1"]) & (pl.col("goal_no") == r["goal_no"]))
        unit = hit["unit_id"][0] if hit.height else f"local:{r['event']}"
        base = dict(period_unit=unit, goal_no=r["goal_no"], role=role, n=r["n_calls_p12"], n_kind="incumbent calls on days 1-2",
                    ci_level=0.95, ci_kind="percentile", channel="talk_call", first_day=r["day1"],
                    source="data/processed/H122-batch-join-spin-addition/results/events.parquet",
                    notes=f"join event {r['event']} ({r['names']})")
        rows.append({**base, "statistic": "join_dLL_shift_minus_coupling", "estimate": r["d_C_J"], "ci_lo": r["d_C_J_lo"],
                     "ci_hi": r["d_C_J_hi"], "method": "cross-fit in time (PRE+F37 fit, P12 scored), block bootstrap",
                     "null": "0 (constant shift = couplings); kill if < 0"})
        rows.append({**base, "statistic": "join_J_newcomer_read", "estimate": r["J_N"], "ci_lo": r["J_N_lo"], "ci_hi": r["J_N_hi"],
                     "n": r["n_calls_f37"], "n_kind": "incumbent calls on days 3-7",
                     "method": "logit coefficient per newcomer read (days 3-7, M0D offset)", "null": "0"})
        rows.append({**base, "statistic": "join_delta_shift", "estimate": r["delta"], "ci_lo": r["delta_lo"], "ci_hi": r["delta_hi"],
                     "n": r["n_calls_f37"], "n_kind": "incumbent calls on days 3-7",
                     "method": "constant logit shift of incumbents (days 3-7, M0D offset)", "null": "0"})
    Es.write_estimates(rows, hypothesis="H122")
    return len(rows)


def readmes(E: pl.DataFrame, P: pl.DataFrame | None, syn: list):
    pdir = HYP / "goalperiod-subhypotheses"
    for (g,), s in E.filter(~pl.col("event").is_in(["NE27", "NE32"])).group_by(["goal_no"]):
        f = pdir / f"G{g:02d}" / "README.md"
        t = f.read_text()
        vs = s["verdict"].to_list()
        v = vs[0] if len(set(vs)) == 1 else "mixed"
        t = t.replace("**Verdict:** pending", f"**Verdict:** {v}", 1)
        t = t.replace("## Result\n(pending)", "## Result\n" + table(s), 1)
        f.write_text(t)
    for ev in ("NE27", "NE32"):
        s = E.filter(pl.col("event") == ev)
        f = pdir / ev / "README.md"
        t = f.read_text().replace("**Verdict:** pending", f"**Verdict:** {s['verdict'][0]}", 1)
        extra = ""
        if ev == "NE27" and P is not None and P.height:
            d = s["delta_p12"][0]
            q = P["delta_p12"].to_numpy()
            extra = (f"\n\n**Kickoff-matched placebo** ({P.height} non-holdout regime-I kickoffs without a join): δ_P12 range "
                     f"[{q.min():+.2f}, {q.max():+.2f}], median {np.median(q):+.2f}; NE27 δ_P12 = {d:+.2f} "
                     f"(percentile {100 * np.mean(q <= d):.0f}).")
        t = t.replace("## Result\n(pending)", "## Result\n" + table(s) + extra, 1)
        f.write_text(t)


def table(s: pl.DataFrame) -> str:
    out = ["| Event | incumbents | P12 calls (with newcomer read) | ΔLL MC−MJ [95%] | ΔLL MJ_pl−MJ | ΔLL M_same−MJ | ΔLL M0−M0D | J_N F37 [95%] | J_N P12 [95%] | δ F37 | R²_h MC / MJ | verdict |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in s.to_dicts():
        out.append(f"| {r['event']} | {r['n_incumbents']} | {r['n_calls_p12']} ({r['n_p12_with_newcomer_read']}) | "
                   f"{ci(r['d_C_J'], r['d_C_J_lo'], r['d_C_J_hi'])} | {ci(r['d_PL_J'], r['d_PL_J_lo'], r['d_PL_J_hi'])} | "
                   f"{ci(r['d_SAME_J'], r['d_SAME_J_lo'], r['d_SAME_J_hi'])} | {ci(r['d_M0_M0D'], r['d_M0_M0D_lo'], r['d_M0_M0D_hi'])} | "
                   f"{ci(r['J_N'], r['J_N_lo'], r['J_N_hi'], 3)} | {ci(r['J_N_p12'], r['J_N_p12_lo'], r['J_N_p12_hi'], 3)} | "
                   f"{r['delta']:+.2f} | {r['R2h_MC']:.2f} / {r['R2h_MJ']:.2f} | {r['verdict']} |")
    out.append("\nΔLL in nats per 1,000 incumbent calls on days 1–2 (positive: the second model is better). J in logit per newcomer read. "
               "Data: `data/processed/H122-batch-join-spin-addition/results/events.parquet`.")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-estimates", action="store_true")
    ap.add_argument("--no-readmes", action="store_true")
    a = ap.parse_args()
    E = pl.read_parquet(RES / "events.parquet")
    P = pl.read_parquet(RES / "placebo.parquet") if (RES / "placebo.parquet").exists() else None
    syn = json.loads((D / "synthetic/summary.json").read_text()) if (D / "synthetic/summary.json").exists() else []
    r3 = E.filter(pl.col("regime") == "III")
    r1 = E.filter(pl.col("regime") == "I")
    resolved = E.filter((pl.col("J_N_lo") > 0) & (pl.col("J_N_p12_lo") > 0))
    summ = {
        "n_events": E.height, "verdicts": E.group_by("verdict").len().to_dicts(),
        "P1_NE32": E.filter(pl.col("event") == "NE32").select("d_C_J", "d_C_J_lo", "d_C_J_hi", "verdict").to_dicts(),
        "P2_NE27": E.filter(pl.col("event") == "NE27").select("J_N", "J_N_lo", "J_N_hi", "d_C_J", "d_C_J_lo", "d_C_J_hi", "delta_p12").to_dicts(),
        "P3_ratio": resolved.select("event", "ratio_lo", "ratio_hi", pl.col("J_N_p12") / pl.col("J_N")).to_dicts(),
        "P4_pl": E.filter(pl.col("d_C_J_lo") > 0).select("event", "d_PL_J", "d_PL_J_lo", "d_PL_J_hi").to_dicts(),
        "P5_M0D_beats_M0_share": float((E["d_M0_M0D"] > 0).mean()),
        "P6_NE32_same": E.filter(pl.col("event") == "NE32").select("d_SAME_J", "d_SAME_J_lo", "d_SAME_J_hi").to_dicts(),
        "P7_III_MJ_wins": float((r3["d_C_J_lo"] > 0).mean()) if r3.height else None,
        "P7_III_MC_wins": float((r3["d_C_J_hi"] < 0).mean()) if r3.height else None,
        "P7_I_ci_incl0": float(((r1["d_C_J_lo"] <= 0) & (r1["d_C_J_hi"] >= 0)).mean()) if r1.height else None,
        "J_N_prob_med_III": float(r3["J_N_prob"].median()) if r3.height else None,
        "placebo": None if P is None else {"n": P.height, "min": float(P["delta_p12"].min()), "max": float(P["delta_p12"].max()),
                                           "median": float(P["delta_p12"].median())},
    }
    (RES / "summary.json").write_text(json.dumps(summ, indent=1, default=float))
    print(json.dumps(summ, indent=1, default=float))
    figures(E, P)
    if not a.no_estimates:
        print("estimates rows", estimates(E))
    if not a.no_readmes:
        readmes(E, P, syn)


if __name__ == "__main__":
    main()
