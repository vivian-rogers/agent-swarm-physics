"""H104 summary: per-period estimate rows (write_estimates), the peri-step figure (#51) and the synthetic
identifiability figure.

    uv run python hypotheses/H104-barkhausen-avalanches/analysis/summarize.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h104lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
import estimates as E  # noqa: E402

RES = L.DATA / "results"
FIG = HERE.parent / "figures"
SRC = "data/processed/H104-barkhausen-avalanches/results/periods.parquet"


def rows_for(df: pl.DataFrame) -> list[dict]:
    rows = []
    for r in df.filter(pl.col("eligible")).iter_rows(named=True):
        g = r["g"]
        pu = E.map_unit(g)
        ch = f"project switches ({r['channel']})"
        v = r["variant"]
        base = {"period_unit": pu, "goal_no": g, "channel": ch, "role": "replication", "source": SRC,
                "n": r["n_steps"], "n_kind": "isolated human steps"}
        meth_sfx = "" if v == "primary" else f" [variant {v}]"
        rows.append({**base, "statistic": "step_response_X" + ("" if v == "primary" else f"_{v}"), "estimate": r["X"],
                     "ci_lo": r["X_lo"], "ci_hi": r["X_hi"], "ci_kind": "percentile", "ci_level": 0.95,
                     "method": "mean distinct switching agents in (t, t+W] after human steps / time-shuffle null" + meth_sfx,
                     "null": f"per-agent-day circular rotation within at-risk spans (p = {r['p_X']:.3f})"})
        if v != "primary":
            continue
        if r.get("V") is not None and np.isfinite(r["V"]):
            rows.append({**base, "statistic": "burst_variance_ratio_V", "estimate": r["V"], "ci_lo": r["V_lo"], "ci_hi": r["V_hi"],
                         "ci_kind": "percentile", "ci_level": 0.95, "status": "not identifiable at these counts (H104 A1)",
                         "method": "Var(S) after steps / mean null Var(S)", "null": f"time-shuffle (p = {r['p_V']:.3f})"})
        if r.get("D") is not None and np.isfinite(r["D"]):
            rows.append({**base, "statistic": "quiet_dispersion_D", "estimate": r["D"], "ci_kind": "none", "n": r["n_quiet"],
                         "n_kind": "quiet 60-min windows", "method": "Var(S) in quiet windows / mean null Var(S)",
                         "null": f"time-shuffle band [{r['D_lo']:.2f}, {r['D_hi']:.2f}] (p = {r['p_D']:.3f})"})
        if r.get("BR") is not None and np.isfinite(r["BR"]):
            rows.append({**base, "statistic": "burst_ratio_BR", "estimate": r["BR"], "ci_lo": r["BR_lo"], "ci_hi": r["BR_hi"],
                         "ci_kind": "percentile", "ci_level": 0.95,
                         "status": None if g == 51 else "invalid with < 10 steps (H104 A1)",
                         "method": "P(S > null q95 | post-step) / P(S > null q95 | quiet window)", "null": "1"})
        if r.get("rho_m") is not None and np.isfinite(r["rho_m"]):
            rows.append({**base, "statistic": "dose_rho_messages", "estimate": r["rho_m"], "ci_kind": "none",
                         "method": "Spearman(session message count, excess S)", "null": f"0 (p = {r['p_rho_m']:.3f})"})
        if r.get("K") is not None and np.isfinite(r["K"]):
            rows.append({**base, "statistic": "kickoff_ratio_K", "estimate": r["K"], "ci_kind": "none", "n": None, "n_kind": None,
                         "method": "share of agents switching in the first 120 min of the kickoff day / other days",
                         "null": "1 (day-start-matched placebo)"})
        if r.get("X_pre") is not None and np.isfinite(r["X_pre"]):
            rows.append({**base, "statistic": "prestep_placebo_X", "estimate": r["X_pre"], "ci_kind": "none",
                         "method": "X in (t-W, t] before steps", "null": f"1 (p = {r['p_X_pre']:.3f})"})
        if r.get("tau") is not None:
            rows.append({**base, "statistic": "avalanche_tau_mle", "estimate": r["tau"], "ci_lo": r["tau_lo"], "ci_hi": r["tau_hi"],
                         "ci_kind": "profile", "ci_level": 0.95, "status": "not identifiable at these counts (H104 A1)",
                         "method": "deconvolution MLE: S = A + B, A ~ pi*delta0 + (1-pi)*truncated power law",
                         "null": f"pi = {r['pi']:.2f}; LLR vs null {r['llr']:.2f}"})
    return rows


def native_rows(nat: dict) -> list[dict]:
    src = "data/processed/H104-barkhausen-avalanches/results/natives.json"
    rows = []
    n38 = nat["NE38"]
    for ch in ("work", "attn"):
        x = n38[ch]
        rows.append({"period_unit": "51f", "goal_no": 51, "statistic": "NE38_others_switching", "channel": f"project switches ({ch})",
                     "estimate": x["others_switching"], "ci_lo": x["null_q05"], "ci_hi": x["null_q95"], "ci_kind": "none",
                     "n": x["others_at_risk"], "n_kind": "agents at risk", "role": "native", "source": src,
                     "method": "other agents switching in 120 min after the reassignment step (band = null 5-95%)",
                     "null": f"time-shuffle mean {x['null_mean']:.2f}"})
        y = nat["NE43"][ch]
        rows.append({"period_unit": "G51", "goal_no": 51, "statistic": "NE43_switch_rate_ratio", "channel": f"project switches ({ch})",
                     "estimate": y["ratio"], "ci_lo": y["ci"][0], "ci_hi": y["ci"][1], "ci_kind": "percentile", "ci_level": 0.95,
                     "n": 10, "n_kind": "days", "role": "native", "source": src,
                     "method": "switches per agent-hour at risk, 5 days after the nudger stops / 5 days before",
                     "null": f"placebo splits band [{y['placebo_q05']:.2f}, {y['placebo_q95']:.2f}]"})
        z = nat["G44"][ch]
        if z.get("testable"):
            rows.append({"period_unit": "G44", "goal_no": 44, "statistic": "G44_step_response_X_allsteps", "channel": f"project switches ({ch})",
                         "estimate": z["X"], "ci_kind": "none", "n": z["n_steps"], "n_kind": "human steps (all)", "role": "native",
                         "source": src, "method": "all eligible steps (A1); room locality uninformative without a response",
                         "null": "time-shuffle"})
    return rows


def peristep(g=51, n_draw=199):
    P = L.load_period(g)
    out = {}
    for ch in ("work", "attn"):
        ad = L.agent_days(P, "span")
        sw = L.switches_in(P, ch, ad)
        st = L.eligible_steps(P, ad, 3600.0)
        offs = np.arange(-60, 120, 10) * 60.0
        ratio, lo, hi = [], [], []
        for o in offs:
            pan = L.Panel(ad, sw, st["t"].to_numpy() + o, 600.0, st["pt_date"].to_numpy())
            S, _ = pan.counts(pan.sw_t)
            Sn, _ = pan.null(n_draw, seed=int(o) % 1000 + 7)
            ratio.append(S.mean() / Sn.mean())
            nd = Sn.mean(1) / Sn.mean()
            lo.append(np.percentile(nd, 5))
            hi.append(np.percentile(nd, 95))
        out[ch] = (offs / 60 + 5, np.array(ratio), np.array(lo), np.array(hi), st.height)
    return out


def figures(df, syn):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    FIG.mkdir(parents=True, exist_ok=True)
    ps = peristep()
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.5))
    for k, (ch, lab) in enumerate((("work", "work switches"), ("attn", "attention switches"))):
        x, r, lo, hi, n = ps[ch]
        ax[k].fill_between(x, lo, hi, color="0.85", label="time-shuffle null 90%")
        ax[k].plot(x, r, "-o", color="#c0392b", ms=3, lw=1, label="observed / null")
        ax[k].axvline(0, color="#2c3e50", lw=0.8, ls="--")
        ax[k].axhline(1, color="0.5", lw=0.5)
        ax[k].set_title(f"#51 {lab} ({n} isolated human steps)", fontsize=6.5)
        ax[k].set_xlabel("minutes from the human step (10-min bins)", fontsize=7)
        ax[k].tick_params(labelsize=6)
        ax[k].set_ylim(0.3, 2.2)
    ax[0].set_ylabel("switching agents per bin / null", fontsize=7)
    ax[0].legend(fontsize=5.5, frameon=False, loc="upper left")
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs_col.pdf")
    fig.savefig(FIG / "summary_obs_col.png", dpi=160)
    plt.close(fig)
    # synthetic identifiability, #51
    t = pl.DataFrame(syn["table"]).filter(pl.col("g") == 51)
    fig, ax = plt.subplots(1, 2, figsize=(3.4, 2.2), sharey=True)
    worlds = ["W0", "W1", "W2", "W3"]
    names = ["Poisson", "τ = 3/2", "thin", "endog."]
    for k, ch in enumerate(("work", "attn")):
        q = t.filter(pl.col("channel") == ch)
        get = lambda w, c: float(q.filter(pl.col("world") == w)[c][0])  # noqa: E731
        xx = np.arange(4)
        ax[k].bar(xx - 0.27, [get(w, "rate_X") for w in worlds], 0.27, color="#2c3e50", label="step response X")
        ax[k].bar(xx, [get(w, "rate_tail") for w in worlds], 0.27, color="#c0392b", label="tail (V, F_A)")
        ax[k].bar(xx + 0.27, [get(w, "rate_tau_band") for w in worlds], 0.27, color="#e6a23c", label="tau in [1.2, 1.8]")
        ax[k].set_xticks(xx, names, fontsize=5.5)
        ax[k].set_title(f"#51 {ch}", fontsize=6.5)
        ax[k].tick_params(labelsize=5.5)
    ax[0].set_ylabel("pass rate (20 runs)", fontsize=6)
    h, lb = ax[0].get_legend_handles_labels()
    fig.legend(h, lb, fontsize=5, frameon=False, loc="upper center", ncol=3)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig(FIG / "synthetic_col.pdf")
    fig.savefig(FIG / "synthetic_col.png", dpi=160)
    plt.close(fig)


def main():
    df = pl.read_parquet(RES / "periods.parquet")
    nat = json.loads((RES / "natives.json").read_text())
    syn = json.loads((L.DATA / "synthetic/summary.json").read_text())
    rows = rows_for(df) + native_rows(nat)
    E.write_estimates(rows, hypothesis="H104")
    print("estimates rows:", len(rows))
    figures(df, syn)


if __name__ == "__main__":
    main()
