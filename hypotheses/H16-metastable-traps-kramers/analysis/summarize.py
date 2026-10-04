"""H16 cross-period summary: table, prediction tallies, cross-period figure and the one-page summary PDF.

Reads data/processed/H16-metastable-traps-kramers/<period>/results.json and period_scores.json (write_period_folders
--results must run first). Writes summary.json there, figures/cross_period.pdf and figures/H16_summary.pdf.
Comparing periods by their fitted parameters (one point per period) is the allowed cross-period use; nothing is
pooled across periods.

Usage: uv run python hypotheses/H16-metastable-traps-kramers/analysis/summarize.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h16lib as L  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

PERIODS = ["G27", "G30", "G31", "G37", "G38", "G39", "G40", "G41", "G42", "G44", "G51"]
REG = {p: ("I" if p in ("G27", "G30", "G31") else "III") for p in PERIODS}
nan = float("nan")


def g(d, *ks, default=nan):
    for k in ks:
        if not isinstance(d, dict) or k not in d or d[k] is None:
            return default
        d = d[k]
    return d


def main():
    R = {p: json.loads((L.OUT / p / "results.json").read_text()) for p in PERIODS if (L.OUT / p / "results.json").exists()}
    S = json.loads((L.OUT / "period_scores.json").read_text()) if (L.OUT / "period_scores.json").exists() else {}
    rows = []
    for p, r in R.items():
        a, b, c, d = r["a"], r["b"], r["c"], r["d"]
        ts2k = "TS2r"
        rows.append({
            "period": p, "regime": r["regime"], "days": r["n_days"], "agents": r["n_agents"],
            "ts1r_deep_beta": g(a, "TS1r", "deep", "beta_agentFE"), "ts1r_deep_ci": g(a, "TS1r", "deep", "ci", default=[nan, nan]),
            "ts1r_deep_wald": g(a, "TS1r", "deep", "ci_wald", default=[nan, nan]), "ts1r_deep_events": g(a, "TS1r", "deep", "events"),
            "ts1r_deep_pooled": g(a, "TS1r", "deep", "beta_pooled"),
            "a3_ts1r_deep_beta": g(r, "A3_outages", "TS1r", "deep", "beta_agentFE"),
            "ts2_beta": g(a, "TS2", "beta_lnk_agentFE"), "ts2r_beta": g(a, ts2k, "beta_lnk_agentFE"),
            "ts2r_ci": g(a, ts2k, "ci", default=[nan, nan]), "ts2r_gates": g(a, ts2k, "n_gates"),
            "ts2r_pooled": g(a, ts2k, "beta_lnk_pooled"),
            "ts2r_deepening": g(a, ts2k, "deepening", "median_log_ratio_next_over_current"),
            "ts3_beta": g(a, "TS3", "deep", "beta_agentFE"), "ts3_ci": g(a, "TS3", "deep", "ci", default=[nan, nan]),
            "ts3_wald": g(a, "TS3", "deep", "ci_wald", default=[nan, nan]), "ts3_events": g(a, "TS3", "deep", "events"),
            "ts4_beta": g(a, "TS4", "deep", "beta_agentFE"), "ts4_wald": g(a, "TS4", "deep", "ci_wald", default=[nan, nan]),
            "ts4_events": g(a, "TS4", "deep", "events"),
            "kick_dir": g(c, "TS1", "any_directed_lnHR"), "kick_dir_se": g(c, "TS1", "any_directed_se"),
            "kick_dir_null95": g(c, "TS1", "null_directed_lnHR_p95"),
            "kick_und": g(c, "TS1", "any_undirected_lnHR"), "kick_und_se": g(c, "TS1", "any_undirected_se"),
            "kick_und_null95": g(c, "TS1", "null_undirected_lnHR_p95"), "kick_und_nullmed": g(c, "TS1", "null_undirected_lnHR_median"),
            "a2_dir": g(c, "TS1", "A2_exact_time", "directed_lnHR"), "a2_dir_se": g(c, "TS1", "A2_exact_time", "directed_se"),
            "a2_dir_null95": g(c, "TS1", "A2_exact_time", "null_directed_p95"),
            "a2_und": g(c, "TS1", "A2_exact_time", "undirected_lnHR"), "a2_und_se": g(c, "TS1", "A2_exact_time", "undirected_se"),
            "a2_und_null95": g(c, "TS1", "A2_exact_time", "null_undirected_p95"),
            "gate_dir1": g(c, ts2k, "dose_directed", "lnOR", default=[nan])[0], "gate_dir1_se": g(c, ts2k, "dose_directed", "se", default=[nan])[0],
            "gate_und1": g(c, ts2k, "dose_undirected", "lnOR", default=[nan])[0], "gate_und1_se": g(c, ts2k, "dose_undirected", "se", default=[nan])[0],
            "nudge15": g(c, "TS1", "nudge_slow15_lnHR"), "nudge15_se": g(c, "TS1", "nudge_slow15_se"),
            "frac_dw": g(b, "frac_double_well"), "n_cells": g(b, "n_cells"),
            "msm2_med": g(b, "closure", "mfpt_msm2", "median_abs_ln_ratio"), "msm2_sign": g(b, "closure", "mfpt_msm2", "median_ln_obs_over_pred"),
            "msm2_n": g(b, "closure", "mfpt_msm2", "n"), "oned_med": g(b, "closure", "mfpt_1d", "median_abs_ln_ratio"),
            "arrh_slope": g(b, "arrhenius_ln_kts1r_on_dG", "slope"), "arrh_n": g(b, "arrhenius_ln_kts1r_on_dG", "n"),
            "pooled_dG": g(b, "pooled", "landscape", "dG"), "pooled_dw": g(b, "pooled", "landscape", "double_well"),
            "bj_all": g(d, "all", "betaJ0"), "bj_nostall": g(d, "no_stalls", "betaJ0"), "stall": g(d, "all", "stall_frac"),
            "pv_all": g(d, "all", "p_valley"), "pv_nostall": g(d, "no_stalls", "p_valley"), "pv_circ": g(d, "A4_circ_no_stalls", "p_valley"),
            "acf_obs": g(d, "no_stalls", "acf_obs"), "acf_null95": g(d, "no_stalls", "acf_null_p95"),
            "verdict": S.get(p, {}).get("verdict", "pending")})
    # tallies per prediction id
    tally = defaultdict(Counter)
    for p, sc in S.items():
        for pid, stmt, obs, verd in sc["rows"]:
            tally[pid][verd.split(" ")[0]] += 1
    out = {"rows": rows, "tally": {k: dict(v) for k, v in tally.items()}}
    L.jdump(out, L.OUT / "summary.json")
    cross_figure(rows)
    summary_page(rows, tally)
    for k, v in sorted(tally.items()):
        print(k, dict(v))


def cross_figure(rows):
    plt.rcParams.update({"font.family": "serif", "font.size": 6.5, "axes.linewidth": 0.5, "pdf.fonttype": 42})
    fig, ax = plt.subplots(2, 3, figsize=(7.2, 4.6))
    P = [r["period"] for r in rows]
    y = np.arange(len(P))
    col = ["C3" if r["regime"] == "I" else "C0" for r in rows]

    def forest(axx, key, cikey=None, se=None, title="", band=None, xl=None):
        for i, r in enumerate(rows):
            v = r[key]
            if v is None or not np.isfinite(v):
                continue
            if cikey:
                lo, hi = r[cikey]
            elif se:
                lo, hi = v - 1.96 * r[se], v + 1.96 * r[se]
            else:
                lo = hi = v
            lo = max(lo, -4) if np.isfinite(lo) else v
            hi = min(hi, 4) if np.isfinite(hi) else v
            axx.plot([lo, hi], [i, i], c=col[i], lw=0.8)
            axx.plot(v, i, "o", c=col[i], ms=3)
        if band:
            axx.axvspan(*band, color="grey", alpha=0.15, lw=0)
        axx.axvline(0, c="k", lw=0.4)
        axx.set_yticks(y); axx.set_yticklabels(P); axx.invert_yaxis(); axx.set_title(title)
        if xl:
            axx.set_xlabel(xl)
    forest(ax[0, 0], "ts1r_deep_beta", "ts1r_deep_wald", title="(a) TS1r deep slope (agent FE; Wald CI)", band=(-0.3, 0.3), xl="β on ln elapsed")
    forest(ax[0, 1], "ts2r_beta", "ts2r_ci", title="(a) TS2r gate slope (agent FE; boot CI)", xl="β on ln k")
    forest(ax[0, 2], "ts3_beta", "ts3_wald", title="(a) TS3 error-loop slope (Wald CI)", band=(-0.3, 0.3), xl="β on ln k")
    forest(ax[1, 0], "kick_und", se="kick_und_se", title="(c) undirected kick ln HR (TS1, 30 s)", xl="ln HR")
    for i, r in enumerate(rows):
        if np.isfinite(r["kick_und_null95"]):
            ax[1, 0].plot(r["kick_und_null95"], i, "|", c="k", ms=6)
    forest(ax[1, 1], "gate_dir1", se="gate_dir1_se", title="(c) directed kick during pause: ln OR (TS2r)", xl="ln OR")
    for i, r in enumerate(rows):
        v = r["bj_nostall"]
        if np.isfinite(v):
            ax[1, 2].plot(v, i, "o", c=col[i], ms=3)
            ax[1, 2].plot(r["bj_all"], i, "x", c=col[i], ms=3)
    ax[1, 2].axvline(1, c="k", lw=0.6, ls="--")
    ax[1, 2].set_yticks(y); ax[1, 2].set_yticklabels(P); ax[1, 2].invert_yaxis()
    ax[1, 2].set_title("(d) βJ₀ (o: stalls excl., x: incl.)"); ax[1, 2].set_xlabel("βJ₀")
    fig.suptitle("H16 round 1: per-period estimates (red: regime I, blue: regime III; '|' = day-swap null p95)", fontsize=7.5)
    fig.tight_layout()
    fig.savefig(L.HDIR / "figures" / "cross_period.pdf")
    plt.close(fig)


def summary_page(rows, tally):
    plt.rcParams.update({"font.family": "serif", "font.size": 6.5, "axes.linewidth": 0.5, "pdf.fonttype": 42})
    fig = plt.figure(figsize=(8.27, 11.69))
    fig.text(0.05, 0.965, "H16 · Metastable traps and Kramers escape: exploratory round 1 (non-holdout)", fontsize=11, weight="bold")
    fig.text(0.05, 0.948, "AI Village (AI Digest) data · 11 goal periods (3 regime I, 8 regime III) · synthetic validation first · predictions written 2026-10-03 before real data",
             fontsize=7)
    txt = SUMMARY_TEXT
    fig.text(0.05, 0.935, txt, fontsize=7.6, va="top", family="serif")
    gs = fig.add_gridspec(2, 3, left=0.07, right=0.97, bottom=0.06, top=0.40, hspace=0.45, wspace=0.45)
    P = [r["period"] for r in rows]; y = np.arange(len(P))
    col = ["C3" if r["regime"] == "I" else "C0" for r in rows]
    panels = [("ts1r_deep_beta", "ts1r_deep_wald", None, "TS1r deep slope", (-0.3, 0.3)),
              ("ts2r_beta", "ts2r_ci", None, "TS2r gate slope", None),
              ("ts3_beta", "ts3_wald", None, "TS3 error-loop slope", (-0.3, 0.3)),
              ("kick_und", None, "kick_und_se", "undirected kick ln HR (TS1)", None),
              ("gate_dir1", None, "gate_dir1_se", "directed kick ln OR at gate", None),
              ("bj_nostall", None, None, "βJ₀ (stalls excluded)", None)]
    for k, (key, cik, sek, title, band) in enumerate(panels):
        axx = fig.add_subplot(gs[k // 3, k % 3])
        for i, r in enumerate(rows):
            v = r[key]
            if v is None or not np.isfinite(v):
                continue
            if cik:
                lo, hi = r[cik]
            elif sek:
                lo, hi = v - 1.96 * r[sek], v + 1.96 * r[sek]
            else:
                lo = hi = v
            lo = max(lo, -4) if np.isfinite(lo) else v
            hi = min(hi, 4) if np.isfinite(hi) else v
            axx.plot([lo, hi], [i, i], c=col[i], lw=0.8); axx.plot(v, i, "o", c=col[i], ms=3)
            if key == "kick_und" and np.isfinite(r["kick_und_null95"]):
                axx.plot(r["kick_und_null95"], i, "|", c="k", ms=6)
        if band:
            axx.axvspan(*band, color="grey", alpha=0.15, lw=0)
        axx.axvline(1 if key == "bj_nostall" else 0, c="k", lw=0.5, ls="--" if key == "bj_nostall" else "-")
        axx.set_yticks(y); axx.set_yticklabels(P, fontsize=5.5); axx.invert_yaxis(); axx.set_title(title, fontsize=7)
    fig.text(0.05, 0.025, "Red: regime I; blue: regime III. Grey band: memoryless (|β| ≤ 0.3). '|': day-swap null p95. Bars: 95% CI (Wald for slopes; boot for TS2r).\n"
             "Code: hypotheses/H16-metastable-traps-kramers/analysis/  ·  numbers: data/processed/H16-metastable-traps-kramers/summary.json", fontsize=6)
    fig.savefig(L.HDIR / "figures" / "H16_summary.pdf")
    plt.close(fig)


SUMMARY_TEXT = "(filled by main after the run)"

if __name__ == "__main__":
    tf = L.HDIR / "analysis" / "summary_text.txt"
    if tf.exists():
        SUMMARY_TEXT = tf.read_text()
    main()
