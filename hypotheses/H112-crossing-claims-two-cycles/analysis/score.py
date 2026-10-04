"""H112: write per_period_estimates rows and the summary figures from results/*.json.

Usage: uv run python hypotheses/H112-crossing-claims-two-cycles/analysis/score.py [--no-write]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
D = ROOT / "data/processed/H112-crossing-claims-two-cycles"
RES = D / "results"
FIG = HERE.parent / "figures"
BLUE, ORANGE, INK, MUTED = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e"


def unit_name(g: int) -> str:
    pu = pl.read_parquet(ROOT / "data/processed/shared/period_units.parquet").filter((pl.col("goal_no") == g) & ~pl.col("holdout"))
    return pu["unit_id"][0] if len(pu) == 1 else f"G{g:02d}"


def rows() -> list[dict]:
    per = json.loads((RES / "periods.json").read_text()); nat = json.loads((RES / "natives.json").read_text())
    out = []
    ch = "project switch (action touches, call level)"
    for g, o in per.items():
        g = int(g)
        r = o.get("rr_u", {})
        if not o.get("n_pairs"):
            continue
        base = dict(period_unit=unit_name(g), goal_no=g, channel=ch, role="replication", ci_level=0.95, n_kind="co-switch pairs",
                    null="permutation of awareness labels within lag-bin x named strata; synthetic no-coupling band 0.83-1.05",
                    status="testable" if o["testable"] else "descriptive", source="results/periods.json")
        if r.get("rr") is not None and np.isfinite(r.get("rr", np.nan)):
            out.append({**base, "statistic": "crossing_departure_rr_unaware_vs_read", "estimate": r["rr"],
                        "ci_lo": r.get("lo"), "ci_hi": r.get("hi"), "n": o["n_pairs"], "se": r.get("se_log"),
                        "ci_kind": "se_z", "method": "Mantel-Haenszel RR of >=1 departure within 5 calls, unaware vs read (Greenland-Robins)"})
        for cls in ("read", "silent"):
            v = o.get(f"p_any_{cls}")
            if v is not None and np.isfinite(v):
                out.append({**base, "statistic": f"crossing_departure_rate_{cls}", "estimate": v, "ci_lo": None, "ci_hi": None,
                            "n": o.get(f"n_{cls}"), "ci_kind": "none", "method": "share of pairs with >=1 departure within 5 calls"})
    a = nat.get("G51_N2_post_read", {})
    if a.get("ratio") is not None:
        out.append(dict(period_unit="G51", goal_no=51, channel=ch, role="native", statistic="crossing_post_read_departure_ratio",
                        estimate=a["ratio"], ci_lo=a.get("lo"), ci_hi=a.get("hi"), n=a["n_at_risk"], n_kind="agent-pair reads",
                        ci_kind="parametric", ci_level=0.95, method="departures in 3 calls after vs 3 before the first read of the partner's claim (binomial CI)",
                        null="ratio 1 (no read-out onset)", source="results/natives.json"))
    for arm, v in nat.get("G44_arms", {}).items():
        r = v.get("rr_u", {})
        if r.get("rr") is not None and np.isfinite(r.get("rr", np.nan)):
            out.append(dict(period_unit=unit_name(44), goal_no=44, channel=f"{ch}; arm {arm}", role="native",
                            statistic="crossing_departure_rr_unaware_vs_read", estimate=r["rr"], ci_lo=r["lo"], ci_hi=r["hi"],
                            n=v["n"], n_kind="co-switch pairs", ci_kind="se_z", ci_level=0.95, se=r.get("se_log"),
                            method="MH RR by the second mover's room", null="RR 1", source="results/natives.json"))
    return out


def figure():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    per = json.loads((RES / "periods.json").read_text()); po = json.loads((RES / "pooled.json").read_text())
    nat = json.loads((RES / "natives.json").read_text())
    plt.rcParams.update({"font.size": 7.5, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                         "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(7.0, 2.5), gridspec_kw={"width_ratios": [1.7, 1]})
    labs, xs = [], []
    tests = [(int(g), o) for g, o in per.items() if o["testable"]]
    for i, (g, o) in enumerate(tests):
        r = o["rr_u"]
        ax.errorbar(i, r["rr"], yerr=[[r["rr"] - r["lo"]], [r["hi"] - r["rr"]]], fmt="o", color=BLUE, ms=4, lw=1.2, capsize=0)
        labs.append(f"#{g}"); xs.append(i)
    i0 = len(tests) + 0.8
    for j, (key, lab, col) in enumerate((("rr_u_testable", "pool", BLUE), ("A2_any_claim", "claim\nexists", ORANGE),
                                          ("rr_f_testable", "in flight\n/ read", MUTED))):
        r = po[key] if key in po else nat[key]["rr_u"]
        x = i0 + j * 1.5
        ax.errorbar(x, r["rr"], yerr=[[r["rr"] - r["lo"]], [r["hi"] - r["rr"]]], fmt="D", color=col, ms=4.5, lw=1.4, capsize=0)
        labs.append(lab); xs.append(x)
    ax.axhspan(0.83, 1.05, color="#e9e7e1", zorder=0, lw=0)
    ax.axhline(1, color=MUTED, lw=0.6); ax.axhline(2, color=ORANGE, lw=0.8, ls="--")
    ax.text(xs[-1] + 0.5, 2.0, "HH343: 2×", color=INK, va="bottom", ha="right", fontsize=6.5)
    ax.text(-0.4, 0.85, "no-coupling band (synthetic)", color=MUTED, fontsize=6, va="bottom")
    ax.set_xticks(xs); ax.set_xticklabels(labs, fontsize=6.3)
    ax.set_ylabel("departure risk ratio,\nunaware / read (K = 5 calls)"); ax.set_ylim(0.3, 2.6)
    # right: departure rates by class, with and without claims
    cats = [("read", po["p_any_testable"]["read"], po["n_testable"]["read"]),
            ("silent", po["p_any_testable"]["silent"], po["n_testable"]["silent"]),
            ("in flight", po["p_any_testable"]["inflight"], po["n_testable"]["inflight"]),
            ("unaware,\nclaim exists", nat["A2_any_claim"]["rd_u"]["p1"], nat["A2_any_claim"]["rd_u"]["n1"])]
    for k, (lab, p, n) in enumerate(cats):
        se = np.sqrt(p * (1 - p) / n)
        bx.errorbar(k, p, yerr=1.96 * se, fmt="o", color=ORANGE if "claim" in lab else BLUE, ms=4, lw=1.2, capsize=0)
        bx.text(k, 0.04, f"n={n}", ha="center", fontsize=5.8, color=MUTED)
    bx.set_xticks(range(len(cats))); bx.set_xticklabels([c[0] for c in cats], fontsize=6.3)
    bx.set_ylim(0, 1.02); bx.set_ylabel("P(≥ 1 of the pair departs)")
    fig.tight_layout()
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "summary_obs.pdf"); plt.close(fig)
    # synthetic figure
    s = json.loads((D / "synthetic/summary.json").read_text())
    fig, ax = plt.subplots(figsize=(3.4, 2.3))
    worlds = ["W0", "W3", "W6", "W2", "W1", "W4", "W5"]
    names = {"W0": "J=0", "W3": "J=0 +field", "W6": "J=0 +artifact", "W2": "J=+2", "W1": "J=−2", "W4": "J=−2 +field", "W5": "J=−2 +artifact"}
    for k, w in enumerate(worlds):
        for g, mk in ((18, "o"), (31, "s"), (38, "^"), (51, "v")):
            v = s.get(f"G{g}|{w}", {}).get("rr_u_med")
            if v is not None and np.isfinite(v):
                ax.plot(k + (g - 34) / 60, v, mk, color=BLUE, ms=3.5, alpha=0.8)
        pv = s.get(f"pooled|{w}", {}).get("rr_u_med")
        if pv is not None:
            ax.plot([k - 0.3, k + 0.3], [pv, pv], color=INK, lw=1.2)
    ax.axhline(po["rr_u_testable"]["rr"], color=ORANGE, lw=1, ls="--")
    ax.text(6.4, po["rr_u_testable"]["rr"] + 0.02, "observed", color=INK, ha="right", fontsize=6)
    ax.axhline(2, color=MUTED, lw=0.6, ls=":")
    ax.set_xticks(range(len(worlds))); ax.set_xticklabels([names[w] for w in worlds], rotation=35, ha="right", fontsize=6)
    ax.set_ylabel("median RR_U (40 runs)"); ax.set_ylim(0.4, 2.2)
    fig.tight_layout(); fig.savefig(FIG / "summary_synth.pdf"); plt.close(fig)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--no-write", action="store_true"); a = ap.parse_args()
    figure()
    rs = rows()
    print(len(rs), "rows")
    if not a.no_write:
        import estimates as E
        E.write_estimates(rs, hypothesis="H112")


if __name__ == "__main__":
    main()
