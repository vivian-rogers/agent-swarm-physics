"""Summarize the H50 synthetic validation: recovery table (JSON) and figure (full and column width)."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
D = ROOT / "data/processed/H50-field-vs-coupling-transfer-lag/synthetic"
FIG = ROOT / "hypotheses/H50-field-vs-coupling-transfer-lag/figures"
BLUE, ORANGE, AQUA, GRAY, INK = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984", "#0b0b0b"


def main():
    R = json.load(open(D / "synthetic_results.json"))

    def arr(n, f):
        return np.array([f(r) for r in R[n]], float)
    out = {}
    for n in R:
        j1 = arr(n, lambda r: r["gate_talk"]["jumps"][0])
        lo = arr(n, lambda r: r["gate_talk"]["j_lo"][0])
        hi = arr(n, lambda r: r["gate_talk"]["j_hi"][0])
        tr = arr(n, lambda r: r["truth_kernel"][0])
        # onset hop: first boundary whose jump CI is > 0
        ons = []
        for r in R[n]:
            o = next((k + 1 for k, l in enumerate(r["gate_talk"]["j_lo"]) if l > 0), np.nan)
            ons.append(o)
        hons = []
        for r in R[n]:
            g = r.get("human_gate_talk")
            hons.append(next((k + 1 for k, l in enumerate(g["j_lo"]) if l > 0), np.nan) if g else np.nan)
        row = dict(J1_mean=float(j1.mean()), J1_sd=float(j1.std()), truth1=float(tr.mean()),
                   bias_rel=float((j1.mean() - tr.mean()) / tr.mean()) if tr.mean() > 0 else None,
                   J1_pos_rate=float(np.mean(lo > 0)), J1_neg_rate=float(np.mean(hi < 0)),
                   onset_hop=[None if o != o else int(o) for o in ons],
                   human_onset_hop=[None if o != o else int(o) for o in hons],
                   actJ1_mean=float(arr(n, lambda r: r["gate_act_J1"][0]).mean()),
                   W=float(arr(n, lambda r: r["W"]).mean()), talk=float(arr(n, lambda r: r["talk"]).mean()))
        for which, var in (("A", "full"), ("A", "span"), ("T", "span"), ("T", "full")):
            k = f"c1_{which}_{var}"
            fF = arr(n, lambda r: r[k].get("f_F", np.nan))
            fN = arr(n, lambda r: r[k].get("f_F_null", np.nan))
            row[f"S_{which}_{var}"] = float(np.nanmean(arr(n, lambda r: r[k].get("S_raw", np.nan))))
            row[f"fF_{which}_{var}"] = float(np.nanmean(fF))
            row[f"fFex_{which}_{var}"] = float(np.nanmean(fF - fN))
        row["fC_T_span"] = float(np.nanmean(arr(n, lambda r: r["cf_T_span_k1"]["f_C"])))
        row["fC_T_span_sd"] = float(np.nanstd(arr(n, lambda r: r["cf_T_span_k1"]["f_C"])))
        row["fC_T_full"] = float(np.nanmean(arr(n, lambda r: r["cf_T_full_k1"]["f_C"])))
        out[n] = row
    # true shares (component switched off, same seeds)
    truth = {}
    for on, offc, offf in (("S3_both", "S1_field", "S2_coupling"), ("S5_all", "S5f_field_ou", "S5c_coup_ou"),
                           ("I3_both", "I1_field", "I2_coupling")):
        t = {}
        for which, var in (("T", "span"), ("T", "full"), ("A", "full")):
            s_on, s_c, s_f = (out[x][f"S_{which}_{var}"] for x in (on, offc, offf))
            t[f"coupling_{which}_{var}"] = 1 - s_c / s_on
            t[f"field_{which}_{var}"] = 1 - s_f / s_on
        truth[on] = t
    res = dict(scenarios=out, truth_shares=truth)
    (D / "synthetic_summary.json").write_text(json.dumps(res, indent=1))
    for n, r in out.items():
        print(f"{n:18s} J1 {r['J1_mean']:.4f}±{r['J1_sd']:.4f} truth {r['truth1']:.4f} pos {r['J1_pos_rate']:.1f} neg {r['J1_neg_rate']:.1f} "
              f"onset {r['onset_hop']} human_onset {r['human_onset_hop']} fFex_A_full {r['fFex_A_full']:.2f} fFex_T_span {r['fFex_T_span']:.2f} fC_T {r['fC_T_span']:.2f}")
    print(json.dumps(truth, indent=1))
    # ---------------------------------------------------------------- figure
    order = ["S0_null", "S1_field", "S4_ou", "S5f_field_ou", "S2_coupling", "S3_both", "S5_all", "S6_edge_clustered",
             "S7_dead", "S8_ungated"]
    labels = ["null", "field", "OU drive", "field+OU", "coupling", "field+coup.", "all", "all, edge-\nclustered",
              "dead time\n2 hops", "ungated"]
    for tag, size in (("synthetic_validation", (7.0, 2.8)), ("synthetic_col", (3.4, 2.1))):
        fig, axes = plt.subplots(1, 2, figsize=size, gridspec_kw=dict(width_ratios=[1.6, 1]))
        ax = axes[0]
        y = np.arange(len(order))
        for i, n in enumerate(order):
            js = [r["gate_talk"]["jumps"][0] for r in R[n]]
            ax.scatter(js, [i] * len(js), s=9, color=BLUE, alpha=0.6, lw=0, zorder=3)
            t = out[n]["truth1"]
            ax.scatter([t], [i], marker="|", s=90, color=INK, lw=1.6, zorder=4)
        ax.axvline(0, color=GRAY, lw=0.6)
        ax.set_yticks(y)
        ax.set_yticklabels(labels, fontsize=6 if tag.endswith("col") else 7)
        ax.invert_yaxis()
        ax.set_xlabel("read-out jump $J_1$ (talk)", fontsize=7)
        ax.tick_params(labelsize=6)
        ax.set_title("gate: estimate (dots) vs truth (bar)", fontsize=7)
        ax = axes[1]
        sc = ["S3_both", "S5_all", "S6_edge_clustered"]
        tl = ["field+coup.", "all", "edge-cl."]
        x = np.arange(len(sc))
        tc = [truth.get(s, truth["S5_all"])["coupling_T_span"] if s != "S6_edge_clustered" else np.nan for s in sc]
        est = [out[s]["fC_T_span"] for s in sc]
        esd = [out[s]["fC_T_span_sd"] for s in sc]
        ax.bar(x - 0.18, tc, 0.34, color=GRAY, label="true", zorder=2)
        ax.bar(x + 0.18, est, 0.34, yerr=esd, color=ORANGE, label="CF estimate", zorder=2,
               error_kw=dict(lw=0.8, capsize=1.5))
        ax.set_xticks(x)
        ax.set_xticklabels(tl, fontsize=6)
        ax.set_ylim(0, 1.2)
        ax.set_ylabel("coupling share of talk co-movement", fontsize=6.5)
        ax.tick_params(labelsize=6)
        ax.legend(fontsize=6, frameon=False, loc="upper right")
        ax.set_title("coupling share (regime-III world)", fontsize=7)
        for a in axes:
            for s in ("top", "right"):
                a.spines[s].set_visible(False)
        fig.tight_layout()
        FIG.mkdir(parents=True, exist_ok=True)
        fig.savefig(FIG / f"{tag}.pdf")
        plt.close(fig)


if __name__ == "__main__":
    main()
