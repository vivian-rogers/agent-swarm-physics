"""H41 round 2: per-period rows for the shared estimates table, and the round-2 summary figure.

  uv run python hypotheses/H41-readout-light-cone/analysis/r2_write.py [--no-estimates]

Reads data/processed/H41-readout-light-cone/r2/{R2,R3,R4}/results_real.json (non-reserved data only).
Round-1 rows are untouched (write_estimates replaces rows only with the same statistic/channel/method/role/source).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
R2D = ROOT / "data/processed/H41-readout-light-cone/r2"
FIG = HERE.parent / "figures"
NOTE = "round 2 (2026-10-05)"


def num(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def ci(x):
    if not x:
        return None, None
    lo, hi = num(x[0]), num(x[1])
    return (lo, hi) if lo is not None and hi is not None else (None, None)


def rows():
    import estimates as E
    out = []
    r2 = json.loads((R2D / "R2/results_real.json").read_text())
    r3 = json.loads((R2D / "R3/results_real.json").read_text())
    r4 = json.loads((R2D / "R4/results_real.json").read_text())

    def add(g, stat, channel, est, c, n, n_kind, method, null, role="replication", ci_kind="percentile", post_hoc=False,
            notes="", src="r2/R2/results_real.json"):
        if num(est) is None:
            return
        lo, hi = ci(c)
        out.append(dict(period_unit=E.map_unit(g), goal_no=g, statistic=stat, channel=channel, estimate=num(est),
                        ci_lo=lo, ci_hi=hi, ci_level=0.95, ci_kind=ci_kind if lo is not None else "none", n=num(n),
                        n_kind=n_kind, method=method, null=null, role=role, confirmatory=False, post_hoc=post_hoc,
                        source=f"data/processed/H41-readout-light-cone/{src}", notes=(notes + "; " if notes else "") + NOTE))

    for g in (35, 36, 38, 42, 51):
        x = r2.get(str(g))
        if not x:
            continue
        m = "case-control within items: cross-room robustly acausal adopter vs same-window cross-room non-adopters; MH"
        add(g, "r2_lambda_ordered_read", "artifact_read", x["Lambda"], x.get("Lambda_ci"), x["n_strata"], "strata",
            m + " OR(ordered read)/OR(post-use read), 1-h block bootstrap B=400", "1 (shared project or busy adopter)",
            role="native" if g in (38, 51) else "replication")
        add(g, "r2_or_ordered", "artifact_read", x["OR_ord"], x.get("OR_ord_ci"), x["n_strata"], "strata",
            m + " OR of a read of a source-written artifact in (t0, t_use)", "1", role="native" if g in (38, 51) else "replication")
        add(g, "r2_ordered_share_cross", "artifact_read", x["share_ord"], None, x["n_strata"], "cross-room acausal adoptions",
            "share with a read of a source-written artifact after the post and before use", "none", ci_kind="none",
            role="native" if g in (38, 51) else "replication")
    for k, x in r3.items():
        g = int(k[1:])
        role = "native" if g in (51,) else "replication"
        add(g, "r3_phase_R_m", "hop_lag", x.get("R_m"), None, x.get("n_phase"), "hop events",
            "Rayleigh phase concentration of (t_use - t_m)/tau_loc", "uniform phase (R ~ 0)", role=role, ci_kind="none",
            src="r2/R3/results_real.json")
        add(g, "r3_phase_R_e", "hop_lag", x.get("R_e"), None, x.get("n_phase"), "hop events",
            "Rayleigh phase concentration of (t_use - t_call(entry call))/tau_loc", "uniform phase (R ~ 0)", role=role,
            ci_kind="none", src="r2/R3/results_real.json")
        if x.get("dM") is not None:
            add(g, "r3_M2_excess", "hop_lag", x.get("dM"), None, x.get("n_H2"), "in-cone adoptions at H = 2",
                "median recipient calls (t0, t_use] at H=2 over H=1, minus entry-conditioned permutation mean (500)",
                "0; NOT SCORED: field worlds give p<0.05 in 3/8 synthetic runs", role=role, ci_kind="none",
                notes=f"p_perm {x.get('p_perm')}", src="r2/R3/results_real.json")
    for k, x in r4.items():
        if not k.startswith("G"):
            continue
        g, cls = int(k[1:3]), k.split("_")[1]
        add(g, f"r4_J_rd_{cls}", "talk_adoption", x.get("J_rd60"), x.get("J_rd60_ci"), x.get("n_inflight"),
            "in-flight units", "start-time RD at t0, local-linear (triangular, |s|<=60 s), 1-h block bootstrap B=200",
            "1; NOT VALIDATED: length field gives 0.89-1.48 (size 4/12)", ci_kind="percentile", src="r2/R4/results_real.json",
            notes="descriptive (kill rule i)")
        if cls == "D":
            add(g, "r4_J_mh_cs0_D", "talk_adoption", x.get("J_mh_cs0"), x.get("J_mh_cs0_ci"), x.get("n_inflight"),
                "in-flight units", "delay-matched J (MH over delay bins) on units without a shared specific artifact touch",
                "1 (field); length field biases it low (0.29-0.53)", src="r2/R4/results_real.json")
            add(g, "r4_psi_D", "talk_adoption", x.get("psi"), x.get("psi_ci"), x.get("adopt_inflight"),
                "in-flight adoptions", "MH ratio of in-flight hazard, shared specific artifact touch (30 min) vs none",
                "1 (no common-stimulus field)", src="r2/R4/results_real.json")
    return out


def figure():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    r2 = json.loads((R2D / "R2/results_real.json").read_text())
    r4 = json.loads((R2D / "R4/results_real.json").read_text())
    r3 = json.loads((R2D / "R3/results_real.json").read_text())
    fig, ax = plt.subplots(1, 3, figsize=(10.5, 3.2))
    # (a) R2
    keys = ["35", "36", "38", "42", "51", "pooled"]
    for i, k in enumerate(keys):
        x = r2.get(k)
        if not x:
            continue
        for j, (stat, col) in enumerate((("OR_ord_eq", "#b2182b"), ("OR_post", "#878787"))):
            v = x[stat]
            c = list(x.get(stat + "_ci") or [np.nan, np.nan])
            c[1] = min(c[1], 1e4) if np.isfinite(c[1]) else 1e4
            ax[0].errorbar(i + (j - 0.5) * 0.25, v, yerr=[[max(v - c[0], 0)], [max(c[1] - v, 0)]] if np.isfinite(c[0]) and np.isfinite(c[1]) else None,
                           fmt="o", color=col, ms=4, lw=1, label=("ordered read" if j == 0 else "post-use read") if i == 0 else None)
    ax[0].set_yscale("log")
    ax[0].axhline(1, color="k", lw=0.5)
    ax[0].set_xticks(range(len(keys)))
    ax[0].set_xticklabels(["#35", "#36", "#38", "#42", "#51", "pool"])
    ax[0].set_ylabel("odds ratio, adopter vs non-adopter")
    ax[0].set_title("(a) R2: reads of the source's artifacts", fontsize=9)
    ax[0].legend(fontsize=7, frameon=False)
    # (b) R4 J_mh vs J_rd by class, pooled regime III and I
    cl = ["N", "D", "W", "U"]
    for i, c in enumerate(cl):
        for j, (reg, mk) in enumerate((("III", "o"), ("I", "s"))):
            x = r4.get(f"pooled_{reg}_{c}")
            if not x:
                continue
            for kk, (stat, col) in enumerate((("J_mh", "#2166ac"), ("J_rd60", "#b2182b"))):
                v = x.get(stat)
                cc = x.get(stat + "_ci") or [np.nan, np.nan]
                if v is None or not np.isfinite(v):
                    continue
                pos = i + (j * 2 + kk - 1.5) * 0.15
                lo = cc[0] if np.isfinite(cc[0]) else v
                hi = min(cc[1], 1e3) if np.isfinite(cc[1]) else 1e3
                ax[1].errorbar(pos, v, yerr=[[max(v - lo, 0)], [max(hi - v, 0)]], fmt=mk, color=col, ms=4, lw=1,
                               label=f"{'J_mh' if kk == 0 else 'J_rd'} regime {reg}" if i == 0 else None)
    ax[1].axhspan(0.29, 0.53, color="#2166ac", alpha=0.12, lw=0)
    ax[1].axhspan(0.89, 1.48, color="#b2182b", alpha=0.10, lw=0)
    ax[1].axhline(1, color="k", lw=0.5)
    ax[1].set_yscale("log")
    ax[1].set_xticks(range(4))
    ax[1].set_xticklabels(["names", "numbers", "rare words", "links"])
    ax[1].set_ylabel("entry / in-flight hazard")
    ax[1].set_title("(b) R4: jump by item class (bands: length world)", fontsize=9)
    ax[1].legend(fontsize=6, frameon=False, ncol=2)
    # (c) R3: n by hop count, M2 observed vs permutation null
    ks = [k for k in r3 if r3[k].get("M2") is not None and r3[k].get("M2_null_mean") is not None]
    for i, k in enumerate(ks):
        x = r3[k]
        ax[2].plot(i, x["M2"], "o", color="#b2182b", ms=5, label="observed M2" if i == 0 else None)
        ax[2].plot(i, x["M2_null_mean"], "s", color="#878787", ms=5, label="entry-conditioned null" if i == 0 else None)
    ax[2].set_xticks(range(len(ks)))
    ax[2].set_xticklabels(["#" + k[1:] for k in ks])
    ax[2].set_ylabel("median n(H=2) / median n(H=1)")
    ax[2].set_title("(c) R3: lag vs cone hops (not scored)", fontsize=9)
    ax[2].legend(fontsize=7, frameon=False)
    fig.tight_layout()
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "r2_summary.pdf")
    fig.savefig(FIG / "r2_summary.png", dpi=150)
    # column version for the 2-page summary: panels (a) and (b) only
    fig2, a2 = plt.subplots(1, 2, figsize=(7.0, 2.7))
    _panel_r2(a2[0], r2)
    _panel_r4(a2[1], r4)
    fig2.tight_layout()
    fig2.savefig(FIG / "r2_summary_col.pdf")
    fig2.savefig(FIG / "r2_summary_col.png", dpi=150)
    print("figure written")


def _panel_r2(axx, r2):
    keys = ["35", "36", "38", "42", "51", "pooled"]
    for i, k in enumerate(keys):
        x = r2.get(k)
        if not x:
            continue
        for j, (stat, col) in enumerate((("OR_ord_eq", "#b2182b"), ("OR_post", "#878787"))):
            v = x[stat]
            c = list(x.get(stat + "_ci") or [np.nan, np.nan])
            c[1] = min(c[1], 1e4) if np.isfinite(c[1]) else 1e4
            lo = max(c[0], 1e-2) if np.isfinite(c[0]) else v
            axx.errorbar(i + (j - 0.5) * 0.25, v, yerr=[[max(v - lo, 0)], [max(c[1] - v, 0)]], fmt="o", color=col,
                         ms=4, lw=1, label=("before use (ordered)" if j == 0 else "after use (placebo)") if i == 0 else None)
    axx.set_yscale("log")
    axx.set_ylim(1e-2, 2e4)
    axx.axhline(1, color="k", lw=0.5)
    axx.set_xticks(range(len(keys)))
    axx.set_xticklabels(["#35", "#36", "#38", "#42", "#51", "pool"], fontsize=8)
    axx.set_ylabel("OR: adopter vs non-adopter", fontsize=8)
    axx.set_title("(a) reads of the source's new artifacts", fontsize=8)
    axx.legend(fontsize=6.5, frameon=False, loc="upper left")


def _panel_r4(axx, r4):
    cl = ["N", "D"]
    names = ["names", "numbers"]
    for i, c in enumerate(cl):
        for j, (reg, mk) in enumerate((("III", "o"), ("I", "s"))):
            x = r4.get(f"pooled_{reg}_{c}")
            if not x:
                continue
            v = x["J_mh"]
            cc = x["J_mh_ci"]
            axx.errorbar(i + (j - 0.5) * 0.3, v, yerr=[[v - cc[0]], [cc[1] - v]], fmt=mk, color="#2166ac", ms=4, lw=1,
                         label=f"regime {reg}, pooled" if i == 0 else None)
    for g, col in (("38", "#4d4d4d"), ("40", "#b2182b"), ("51", "#4d4d4d")):
        x = r4.get(f"G{g}_D")
        if x and x["J_mh"] is not None and np.isfinite(x["J_mh"]):
            axx.errorbar(1.45, x["J_mh"], yerr=[[x["J_mh"] - x["J_mh_ci"][0]], [x["J_mh_ci"][1] - x["J_mh"]]], fmt="d",
                         color=col, ms=3.5, lw=0.8)
            axx.annotate(f"#{g}", (1.52, x["J_mh"]), fontsize=6.5, va="center")
    axx.axhspan(0.29, 0.53, color="#878787", alpha=0.25, lw=0, label="length world, no coupling")
    axx.axhline(1, color="k", lw=0.5)
    axx.set_yscale("log")
    axx.set_xlim(-0.5, 1.8)
    axx.set_xticks([0, 1])
    axx.set_xticklabels(names, fontsize=8)
    axx.set_ylabel("$J_{mh}$ (entry / in-flight)", fontsize=8)
    axx.set_title("(b) read-out jump by item class", fontsize=8)
    axx.legend(fontsize=6.5, frameon=False, loc="upper right")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-estimates", action="store_true")
    a = ap.parse_args()
    figure()
    if not a.no_estimates:
        import estimates as E
        rs = rows()
        df = E.write_estimates(rs, hypothesis="H41")
        print(f"wrote {len(rs)} round-2 rows; H41 total {df.height}")


if __name__ == "__main__":
    main()
