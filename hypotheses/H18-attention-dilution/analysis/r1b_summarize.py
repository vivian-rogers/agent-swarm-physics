"""H18 round 1b: old-vs-new per-period table, verdicts (1b) by the G cards' rule, pooled exponents, figure, estimates.

  uv run python hypotheses/H18-attention-dilution/analysis/r1b_summarize.py [--write-estimates]

Inputs: round-1 G<NN>/fits.json; round-1b r1b/G<NN>/fits_mention.json (ledger k, mention response: the like-for-like
replication) and fits_reply.json (ledger k, reply-parent response); r1b/placebo_reply.json; r1b/native.json.
Verdict rule (G cards, 2026-10-03, unchanged; summarize_lib.period_verdict): supported needs P1 (beta CI > 0), P2
(effective CV winner M_inv or M_sat with k0 < 3) and no D2 contradiction (beta_D2 >= 0.2 or < 200 D2 units).
Writes r1b/summary_r1b.json and figures/r1b_summary.pdf.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from periods import PERIODS, gname  # noqa: E402
from summarize_lib import d1_checks, d2_check, period_verdict  # noqa: E402
from fit_periods import dl_pool  # noqa: E402

ROOT = HERE.parents[2]
DATA = ROOT / "data/processed/H18-attention-dilution"
R1B = DATA / "r1b"
FIG = HERE.parent / "figures"


def load(p):
    return json.loads(p.read_text()) if p.exists() else None


def brief(f):
    if not f:
        return None
    c = d1_checks(f)
    d2 = d2_check(f)
    cvb = f["D1"].get("cv_block", {})
    b = f["D1"]["boot"]["beta"]
    pl_ = f.get("placebo", {})
    return {"units": f["D1"]["n_units"], "rate": f["D1"]["rate"], "beta": f["D1"]["beta"], "beta_lo": b["lo"] if b else None,
            "beta_hi": b["hi"] if b else None, "beta_sd": b["sd"] if b else None, "eff": c["eff"],
            "inv_vs_rec": (cvb.get("comp") or {}).get("inv_vs_rec"), "eps_S": f["eps_S"]["eps"], "d2": d2,
            "k_median": f.get("k_median"), "k_mean": f.get("k_mean"), "p_bar": f.get("p_bar"), "B_hat": f.get("B_hat"),
            "n_room": f.get("n_room_mean"), "placebo": pl_, "verdict": period_verdict(int(f["period"][1:]), f)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-estimates", action="store_true")
    a = ap.parse_args()
    rows = []
    for g in list(PERIODS) + [10]:
        gp = gname(g)
        r = {"period": gp, "regime": (PERIODS.get(g) or {"regime": "I"})["regime"],
             "old": brief(load(DATA / gp / "fits.json")), "mention": brief(load(R1B / gp / "fits_mention.json")),
             "reply": brief(load(R1B / gp / "fits_reply.json"))}
        rows.append(r)
    out = {"periods": rows}
    for var in ("old", "mention", "reply"):
        ok = [r[var] for r in rows if r[var] and r[var]["beta_sd"] and r["period"] != "G10"]
        out[f"pooled_{var}"] = dl_pool([x["beta"] for x in ok], [x["beta_sd"] for x in ok])
        for reg in ("I", "III"):
            sub = [r[var] for r in rows if r[var] and r[var]["beta_sd"] and r["period"] != "G10"
                   and (r["regime"] == reg or (reg == "III" and r["regime"] == "II/III"))]
            out[f"pooled_{var}_{reg}"] = dl_pool([x["beta"] for x in sub], [x["beta_sd"] for x in sub])
        vs = [r[var]["verdict"] for r in rows if r[var] and r["period"] != "G10"]
        out[f"verdicts_{var}"] = {v: vs.count(v) for v in set(vs)}
        out[f"P1_{var}"] = sum(1 for r in rows if r[var] and r["period"] != "G10" and r[var]["beta_lo"] and r[var]["beta_lo"] > 0)
        effs = [r[var]["eff"] for r in rows if r[var] and r["period"] != "G10"]
        out[f"cv_{var}"] = {e: effs.count(e) for e in set(effs)}
        out[f"eps_S_{var}"] = [r[var]["eps_S"] for r in rows if r[var] and r["period"] != "G10"]
        pls = [(r[var]["placebo"] or {}) for r in rows if r[var] and r["period"] != "G10"]
        p10 = [p for p in pls if p.get("invisible") is not None and p.get("n_invisible", 0) >= 20]
        out[f"P10_{var}"] = {"pass": sum(1 for p in p10 if p["invisible"] <= 1.5 * p["nonpending"] and p["invisible"] <= 0.5 * p["pending_same_talks"]),
                             "n": len(p10),
                             "inv_over_pending_same": float(np.median([p["invisible"] / p["pending_same_talks"] for p in p10 if p["pending_same_talks"]])) if p10 else None,
                             "inv_over_nonpending": float(np.median([p["invisible"] / p["nonpending"] for p in p10 if p["nonpending"]])) if p10 else None}
    out["placebo_reply"] = load(R1B / "placebo_reply.json")
    out["native"] = load(R1B / "native.json")
    (R1B / "summary_r1b.json").write_text(json.dumps(out, indent=1, default=float))
    f = lambda x, nd=2: "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{nd}f}"
    for r in rows:
        cells = [r["period"], r["regime"]]
        for var in ("old", "mention", "reply"):
            x = r[var]
            if not x:
                cells.append("—"); continue
            d2 = x["d2"]
            cells.append(f"{f(x['beta'])} [{f(x['beta_lo'])}, {f(x['beta_hi'])}] · {x['eff']} · ε_S {f(x['eps_S'])} · D2 "
                         f"{f(d2.get('beta')) if d2['status'] != 'underpowered' else 'u/p'} · {x['verdict']}")
        print("| " + " | ".join(cells) + " |")
    for k in ("pooled_old", "pooled_mention", "pooled_reply", "pooled_old_I", "pooled_mention_I", "pooled_reply_I",
              "pooled_old_III", "pooled_mention_III", "pooled_reply_III", "verdicts_old", "verdicts_mention", "verdicts_reply",
              "P1_old", "P1_mention", "P1_reply", "cv_old", "cv_mention", "cv_reply", "P10_old", "P10_mention", "P10_reply"):
        print(k, out[k])
    # figure
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rr = [r for r in rows if r["old"] or r["mention"]]
    xs = np.arange(len(rr))
    plt.rcParams.update({"font.size": 5.6, "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42,
                         "axes.titlesize": 6.0, "legend.frameon": False})
    fig, axs = plt.subplots(1, 2, figsize=(3.45, 1.75), dpi=200, gridspec_kw={"width_ratios": [2.3, 1]})
    for j, (var, lab, col) in enumerate((("old", "round 1 (call-start rule, mentions)", "gray"),
                                         ("mention", "ledger k, mentions", "#1f77b4"),
                                         ("reply", "ledger k, reply parent", "#2ca02c"))):
        b = [r[var] for r in rr]
        axs[0].errorbar(xs + 0.2 * (j - 1), [x["beta"] if x else np.nan for x in b],
                        yerr=[[x["beta"] - x["beta_lo"] if x and x["beta_lo"] is not None else 0 for x in b],
                              [x["beta_hi"] - x["beta"] if x and x["beta_hi"] is not None else 0 for x in b]],
                        fmt="o", ms=1.8, lw=0.6, color=col, label=lab)
    axs[0].axhline(1, color="k", lw=0.5, ls=":"); axs[0].axhline(0, color="k", lw=0.5)
    axs[0].set_xticks(xs); axs[0].set_xticklabels([r["period"].replace("G", "#") for r in rr], rotation=90, fontsize=4.6)
    axs[0].set_ylabel(r"dilution exponent $\hat\beta$"); axs[0].legend(fontsize=4.4, loc="lower left", handletextpad=0.2)
    axs[0].set_ylim(-0.05, 1.3)
    axs[0].set_title("(a) per-period exponent", loc="left")
    pr = out["placebo_reply"] or {}
    regs = [k for k in ("I", "II", "III") if k in pr.get("by_regime", {})]
    vals = [pr["by_regime"][k]["ratio"] for k in regs]
    lo = [pr["by_regime"][k]["ratio_ci"][0] for k in regs]; hi = [pr["by_regime"][k]["ratio_ci"][1] for k in regs]
    axs[1].errorbar(np.arange(len(regs)), vals, yerr=[np.array(vals) - lo, np.array(hi) - vals], fmt="s", color="#2ca02c", ms=2.5, lw=0.7)
    pm = [r["mention"]["placebo"] for r in rows if r["mention"] and r["mention"]["placebo"].get("pending_same_talks")]
    axs[1].axhline(0.5, color="#d62728", lw=0.8, ls="--", label="P10 threshold (½)")
    axs[1].set_xticks(np.arange(len(regs))); axs[1].set_xticklabels([f"{k}" for k in regs], fontsize=5)
    axs[1].set_xlabel("regime"); axs[1].set_xlim(-0.5, len(regs) - 0.5)
    axs[1].set_ylim(0, 1.2); axs[1].set_ylabel("invisible / visible p_reply")
    axs[1].set_title("(b) placebo, replies", loc="left"); axs[1].legend(fontsize=4.4, loc="lower right")
    fig.tight_layout(pad=0.3, w_pad=0.5); fig.savefig(FIG / "r1b_summary.pdf"); plt.close(fig)
    # page-1 figure: observed / expected (M_const, agent x day) addressing vs k, per period, both responses
    fig, axs = plt.subplots(1, 2, figsize=(3.45, 1.7), dpi=200, sharey=True)
    for ax, var, title in ((axs[0], "mention", "(a) ledger k, mentions"), (axs[1], "reply", "(b) ledger k, reply parent")):
        for r in rows:
            fpath = R1B / r["period"] / f"fits_{var}.json"
            if r["period"] == "G10" or not fpath.exists():
                continue
            cv = json.loads(fpath.read_text()).get("curves") or []
            k = [c["kmean"] for c in cv if c["n"] >= 30 and c["oe"] > 0]
            o = [c["oe"] for c in cv if c["n"] >= 30 and c["oe"] > 0]
            if len(k) >= 3:
                col = "#eb6834" if r["regime"] == "I" else "#2a78d6"
                ax.plot(k, o, color=col, lw=0.6, alpha=0.6)
        kk = np.array([1, 100])
        ax.plot(kk, 3.0 / kk ** 1.0 * 1, color="k", lw=0.6, ls=":", label="slope −1 (1/k)")
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_xlabel("pending messages k"); ax.set_title(title, loc="left")
    axs[0].set_ylabel("observed / no-budget expected")
    axs[0].plot([], [], color="#eb6834", lw=0.8, label="regime I"); axs[0].plot([], [], color="#2a78d6", lw=0.8, label="regimes II/III")
    axs[0].legend(fontsize=4.4, loc="lower left")
    fig.tight_layout(pad=0.3, w_pad=0.4); fig.savefig(FIG / "r1b_summary_obs.pdf"); plt.close(fig)
    if a.write_estimates:
        sys.path.insert(0, str(ROOT / "infra/shared"))
        import estimates as E
        est = []
        for r in rows:
            g = int(r["period"][1:])
            for var, ch in (("mention", "addressing (mention), ledger k"), ("reply", "reply parent, ledger k")):
                x = r[var]
                if not x or x["beta_lo"] is None:
                    continue
                est.append(dict(period_unit=E.map_unit(g), goal_no=g, statistic="dilution_exponent_beta", channel=ch, ci_kind="percentile",
                                estimate=float(x["beta"]), ci_lo=float(x["beta_lo"]), ci_hi=float(x["beta_hi"]), se=float(x["beta_sd"]),
                                n=float(x["units"]), n_kind="(talk, pending sender) units",
                                method="M_pow cloglog with ridge agent x day propensities; context-ledger pending sets (k_since_talk); day bootstrap",
                                null="M_const (no budget)", role="native" if g in (10, 51) else "replication",
                                source=f"data/processed/H18-attention-dilution/r1b/G{g:02d}/fits_{var}.json", status="round 1b"))
        E.write_estimates(est, hypothesis="H18")
        print(f"wrote {len(est)} estimates")


if __name__ == "__main__":
    main()
