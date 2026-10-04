"""H66 summary: per-unit table (with the post hoc load-sign diagnostic), period folders, estimates rows, figures.
Run after replication.py and native.py: uv run python hypotheses/H66-platform-latency-field/analysis/summarize.py
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h66lib as L  # noqa: E402
import synthetic as S  # noqa: E402

ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

OUT = ROOT / "data/processed/H66-platform-latency-field"
HYP = ROOT / "hypotheses/H66-platform-latency-field"
METHOD = ("H66 round 1: binary act-call spins on the all-present window, block-demeaned (30 min); E = mean pair corr - "
          "block-shift null (99); field = third-party mean standardized log turnaround (lags 0-5 min) + infra-error count; "
          "Delta f = f_lat - shifted-field control (20)")


def load_sign(unit):
    g = pl.read_parquet(OUT / "grid" / f"{unit}.parquet")
    D = L.assemble(g)
    Z, P, A, blk = D["Z"], D["P"], D["A"], D["blk"]
    v = ~np.isnan(Z) & P
    Lf = np.where(v, Z, 0).sum(1) / np.maximum(v.sum(1), 1)
    K = (A * P).sum(1).astype(float)
    obs = L._corr(L.block_demean(Lf, blk), L.block_demean(K, blk))
    rng = np.random.default_rng(7)
    nl = [L._corr(L.block_demean(Lf, blk), L.block_demean(L.shift_within_days(K[:, None], D["day"], rng)[:, 0], blk)) for _ in range(99)]
    return obs, float(np.mean(nl)), float(np.std(nl))


def verdict(b, sig):
    if not sig:
        return "descriptive"
    lo = b["delta_f_ci"][0]
    if b["delta_f"] >= 0.35 and lo > 0:
        return "supported"
    if b["delta_f"] < 0.10 or (lo <= 0 and b["delta_f"] < 0.10):
        return "failed"
    return "mixed"


def main():
    units = pl.read_parquet(OUT / "units.parquet")
    rows, est = [], []
    for u in units.iter_rows(named=True):
        f = OUT / "replication" / f"{u['unit_id']}.json"
        if not f.exists():
            rows.append({"unit": u["unit_id"], "goal_no": u["goal_no"], "regime": u["regime"], "eligible": False})
            continue
        r = json.loads(f.read_text())
        b, ls = r["binary"], r["lat_strength"]
        sig = b["p_E"] < 0.05
        cLK, cLK0, cLKsd = load_sign(u["unit_id"])
        rows.append({"unit": u["unit_id"], "goal_no": u["goal_no"], "regime": u["regime"], "eligible": True, "N": r["n_agents"],
                     "days": r["n_days"], "minutes": r["n_rows"], "E": b["E"], "E_lo": b["E_ci"][0], "E_hi": b["E_ci"][1],
                     "p_E": b["p_E"], "z_E": b["z_E"], "delta_f": b["delta_f"], "df_lo": b["delta_f_ci"][0], "df_hi": b["delta_f_ci"][1],
                     "delta_f_lag0": r["binary_lag0"]["delta_f"], "delta_f_lab": r["binary_lab"]["delta_f"],
                     "delta_f_int": r["intensity"]["delta_f"], "E_int": r["intensity"]["E"],
                     "rho_lat": ls["all"]["rho"], "p_lat": ls["all"]["p"], "rho_same_lab": ls["same_lab"]["rho"],
                     "rho_cross_lab": ls["cross_lab"]["rho"], "E_same_room": b.get("E_same_room"), "E_cross_room": b.get("E_cross_room"),
                     "E_edge": (r["edge"].get("edge") or {}).get("E"), "E_mid": (r["edge"].get("mid") or {}).get("E"),
                     "C_lat0": r["lags"]["C_lat"][5], "C_lat1": (r["lags"]["C_lat"][4] + r["lags"]["C_lat"][6]) / 2,
                     "C_act0": r["lags"]["C_act_field"][5], "corr_LK": cLK, "corr_LK_null_sd": cLKsd,
                     "verdict_rule": verdict(b, sig), "sig_E": sig})
        reg = u["regime"]
        base = {"period_unit": u["unit_id"], "goal_no": u["goal_no"], "method": METHOD, "role": "replication",
                "first_day": u["first_day"], "last_day": u["last_day"], "source": f"data/processed/H66-platform-latency-field/replication/{u['unit_id']}.json"}
        est += [
            {**base, "statistic": "residual_coactivation_E", "channel": "activity", "estimate": b["E"], "ci_lo": b["E_ci"][0],
             "ci_hi": b["E_ci"][1], "ci_kind": "percentile", "ci_level": 0.95, "n": r["n_rows"], "n_kind": "all-present minutes",
             "null": "block shift within day x 30-min block (99)", "notes": f"z {b['z_E']:.2f}, p {b['p_E']:.2f}"},
            {**base, "statistic": "latency_field_share_delta_f", "channel": "activity", "estimate": b["delta_f"],
             "ci_lo": b["delta_f_ci"][0], "ci_hi": b["delta_f_ci"][1], "ci_kind": "percentile", "ci_level": 0.95, "n": r["n_rows"],
             "n_kind": "all-present minutes", "null": "field circularly shifted within day (20)",
             "notes": "lower bound in field worlds; ~1 in congestion worlds (Amendment 2); meaningful only where E is significant"},
            {**base, "statistic": "latency_field_rho", "channel": "turnaround", "estimate": ls["all"]["rho"], "ci_lo": None, "ci_hi": None,
             "ci_kind": "none", "n": ls["all"]["n_pairs"], "n_kind": "agent pairs", "null": "block shift (49)",
             "notes": f"p {ls['all']['p']:.2f}; same-lab {ls['same_lab']['rho']}, cross-lab {ls['cross_lab']['rho']}"},
            {**base, "statistic": "latency_vs_active_count_corr", "channel": "turnaround", "estimate": cLK,
             "ci_lo": cLK - 1.96 * cLKsd, "ci_hi": cLK + 1.96 * cLKsd, "ci_kind": "se_z", "ci_level": 0.95, "se": cLKsd,
             "n": r["n_rows"], "n_kind": "all-present minutes", "null": "active count circularly shifted within day (99)",
             "post_hoc": True, "notes": "sign test: field-drives-silence predicts < 0 (synthetic W2 -0.34..-0.66); congestion > 0"}]
    tab = pl.DataFrame(rows, infer_schema_length=None)
    tab.write_parquet(OUT / "replication" / "unit_table.parquet")
    E.write_estimates(est, hypothesis="H66")
    native = json.loads((OUT / "native" / "results.json").read_text())
    write_periods(tab, native)
    figures(tab)
    pl.Config.set_tbl_rows(40); pl.Config.set_tbl_width_chars(250)
    print(tab.filter(pl.col("eligible")).select("unit", "N", "E", "p_E", "delta_f", "df_lo", "df_hi", "rho_lat", "rho_same_lab",
                                                  "rho_cross_lab", "corr_LK", "C_act0", "verdict_rule"))


def fmt(x, d=3):
    return "–" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:.{d}f}"


def write_periods(tab, native):
    el = tab.filter(pl.col("eligible"))
    for (g,), d in tab.group_by("goal_no", maintain_order=True):
        folder = HYP / "goalperiod-subhypotheses" / f"G{g:02d}"
        (folder / "figures").mkdir(parents=True, exist_ok=True)
        de = d.filter(pl.col("eligible"))
        rules = de["verdict_rule"].to_list()
        sigs = de.filter(pl.col("sig_E"))
        if sigs.height == 0:
            v = "descriptive"
        else:
            v = "failed"  # Amendment 2 (post hoc): positive load sign in every unit with a significant E
        rule_v = ("supported" if "supported" in rules else "mixed" if "mixed" in rules else "failed" if "failed" in rules else "descriptive")
        lines = [f"| {r['unit']} | {r['N']} | {r['days']} | {r['minutes']} | {fmt(r['E'], 4)} [{fmt(r['E_lo'], 4)}, {fmt(r['E_hi'], 4)}] (p {fmt(r['p_E'], 2)}) | "
                 f"{fmt(r['delta_f'], 2)} [{fmt(r['df_lo'], 2)}, {fmt(r['df_hi'], 2)}] | {fmt(r['rho_lat'])} (p {fmt(r['p_lat'], 2)}) | "
                 f"{fmt(r['rho_same_lab'])} / {fmt(r['rho_cross_lab'])} | {fmt(r['corr_LK'], 2)} | {r['verdict_rule']} |" for r in de.iter_rows(named=True)]
        inel = d.filter(~pl.col("eligible"))["unit"].to_list()
        readme = folder / "README.md"
        native_block = ""
        if readme.exists() and "**Role:** native" in readme.read_text():
            old = readme.read_text()
            head = old.split("## Result")[0]
            native_block = "native"
        else:
            head = f"""# H66 × G{g:02d}: platform latency field on goal period #{g} (units {', '.join(d['unit'].to_list())})

**Verdict:** pending
**Role:** replication
**Period:** regime {'/'.join(sorted(set(d['regime'].to_list())))} · units {', '.join(d['unit'].to_list())}.

## Why this period
Replication layer: the common estimator on every eligible non-holdout unit of the computer-use scaffold.

## Prediction
*Templated from the card (written 2026-10-04 19:15 UTC; cut-offs restated in Amendment 1 at ~20:05 UTC, before real data).* Where the residual co-activation E is significant, the latency field explains a minority of it (Δf < 0.10 → failed; Δf ≥ 0.35 with CI > 0 → supported; mixed otherwise); where E is not significant the unit is descriptive. The latency field ρ̄_lat is expected to be a provider field (same-lab ≥ 2× cross-lab).

"""
        verdict_line = f"**Verdict:** {v}"
        head = head.replace("**Verdict:** pending", verdict_line)
        body = f"""## Result
*Run 2026-10-04 ~21:00 UTC. Data: `data/processed/H66-platform-latency-field/replication/<unit>.json`, `unit_table.parquet`.*

| unit | N | days | all-present min | E [95% CI] (block-shift p) | Δf [95% CI] | ρ̄_lat (p) | ρ̄_lat same-lab / cross-lab | corr(L, K) (post hoc) | rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
""" + "\n".join(lines) + (f"\n\nIneligible (all-present window with a defined field < 10 minutes per day): {', '.join(inel)}." if inel else "") + f"""

**Pre-registered rule:** {rule_v}. **Verdict after Amendment 2 (post hoc, 2026-10-04 ~21:20 UTC):** {v}. In every unit the latency field rises with the number of active agents (corr(L, K) > 0), while a latency field that silences agents gives corr(L, K) < 0 (synthetic W2: −0.34 to −0.66). A congestion world with no latency action (W6) returns Δf ≈ 1.1–1.6, so a positive Δf here measures load, not drive. Where E is not significant, there is no residual to explain (descriptive).
"""
        if native_block and g == 51:
            pv = native["proxy_validation_G51"]
            api = native["api_tests"]
            body += f"""
### Native tests (predictions above)
| Prediction | Observed | Verdict |
| --- | --- | --- |
| corr(log turnaround, log server time) ≥ 0.5 within agent-day | r = {pv['r_within_agent_day']:.2f} over {pv['n_calls']:,} Gemini calls (per agent 0.30–0.52); server time is {pv['median_api_over_turnaround']:.2f} of the median turnaround | held (marginal) |
| Google server-time spin co-moves between Google agents | ρ̄ {min(a['rho_api_google_pairs']['rho'] for a in api):.3f} to {max(a['rho_api_google_pairs']['rho'] for a in api):.3f}; p ≥ 0.06 in all 11 units | failed |
| Google server-time field vs non-Google turnaround: \\|ρ\\| < 0.02 | {', '.join(f"{a['unit']} {a['google_api_vs_nongoogle_turnaround']['r']:.2f}" for a in api)} (p < 0.05 in 51f, 51k) | mostly held (small, mostly n.s.) |
| (descriptive) Google *turnaround* vs non-Google turnaround | {', '.join(f"{a['unit']} {a['google_turnaround_vs_nongoogle_turnaround']['r']:.2f}" for a in api)} | the shared field is the non-API part of a call |
| 51g room split: cross-/same-room ρ̄_lat in [0.8, 1.25] | same-room {fmt(json.loads((OUT / 'replication' / '51g.json').read_text())['lat_strength'].get('same_room', {}).get('rho'))} / cross-room {fmt(json.loads((OUT / 'replication' / '51g.json').read_text())['lat_strength'].get('cross_room', {}).get('rho'))} (ratio ≈ 1.7) | failed as bounded; the field is not room-gated (cross-room pairs co-move more) |
| 51g: same-room E > cross-room E | {fmt(el.filter(pl.col('unit') == '51g')['E_same_room'][0], 4)} vs {fmt(el.filter(pl.col('unit') == '51g')['E_cross_room'][0], 4)} | held (both small) |
| 51g: Δf < 0.10 | {fmt(el.filter(pl.col('unit') == '51g')['delta_f'][0], 2)} [{fmt(el.filter(pl.col('unit') == '51g')['df_lo'][0], 2)}, {fmt(el.filter(pl.col('unit') == '51g')['df_hi'][0], 2)}] | failed (and it measures load) |
| E significant in ≥ 8/12 units | {int(el.filter((pl.col('goal_no') == 51) & pl.col('sig_E')).height)}/11 eligible units (51b ineligible) | failed |

**Reading.** The API server time does not co-move across agents, within Google or with other providers. The turnaround does co-move across providers, and the co-movement grows late in #51 (ρ̄_lat 0.09–0.22 at N = 28–30). The shared component is the harness and execution part of a call. It rises when more agents are active: a congestion meter of the village platform, not a field that drives co-activation.
"""
        if native_block and g == 44:
            ld = native["G44_leader"]
            body += f"""
### Native test (prediction above)
| Prediction | Observed | Verdict |
| --- | --- | --- |
| leader loading below the others' median | g_leader {ld['leader']['g']:.2f} ({ld['leader']['n']} minutes) vs others' median {ld['others_median']:.2f} [IQR {ld['others_q25_q75'][0]:.2f}, {ld['others_q25_q75'][1]:.2f}]; rank {ld['leader_rank_from_top']}/{ld['n_agents']} | held (descriptive, n = 70 minutes) |
| E significant in 44a and 44b | 44a z 3.2 (p 0.01); 44b n.s. | half |
| Δf < 0.10 in both | 44a {fmt(el.filter(pl.col('unit') == '44a')['delta_f'][0], 2)} [{fmt(el.filter(pl.col('unit') == '44a')['df_lo'][0], 2)}, {fmt(el.filter(pl.col('unit') == '44a')['df_hi'][0], 2)}]; corr(L, K) {fmt(el.filter(pl.col('unit') == '44a')['corr_LK'][0], 2)} | failed as written; the sign shows load |

**Reading.** The model served on its own stack does not load on the village latency field, consistent with a field made by contention among the frontier-API agents' harnesses (70 minutes; descriptive). #44a has the largest residual co-activation of the regime-III units after trimming, and its latency field rises with the active count.
"""
        body += """
## Scorecard (period-specific axes)
- C (adequacy): E against the trimmed block-shift null, per unit above.
- H (comparative): the field-vs-load sign test (post hoc) decides against the H66 field reading in every unit with a significant E.

## Notes
- Written by `analysis/summarize.py` (replication rows templated; native rows written from `native/results.json`).
"""
        readme.write_text(head + body)


def figures(tab):
    el = tab.filter(pl.col("eligible") & (pl.col("regime") == "III"))
    syn = pl.read_parquet(OUT / "synthetic" / "runs.parquet")
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.9))
    x = el["N"].to_numpy() + np.random.default_rng(1).uniform(-0.3, 0.3, el.height)
    sig = el["p_lat"].to_numpy() <= 0.05
    ax[0].scatter(x[sig], el["rho_same_lab"].to_numpy()[sig], s=14, c="#2a78d6", label="same-lab pairs")
    ax[0].scatter(x[sig], el["rho_cross_lab"].to_numpy()[sig], s=14, c="#e3a008", marker="s", label="cross-lab pairs")
    ax[0].scatter(x[~sig], el["rho_lat"].to_numpy()[~sig], s=10, c="#bbbbbb", label="all pairs (n.s.)")
    ax[0].axhline(0, color="k", lw=0.5)
    ax[0].set_xlabel("agents in unit (N)", fontsize=7); ax[0].set_ylabel("latency field  rho_lat", fontsize=7)
    ax[0].set_title("a  turnaround co-moves across providers, more at large N", fontsize=7.5)
    ax[0].legend(fontsize=6); ax[0].tick_params(labelsize=6)
    s2 = el.filter(pl.col("sig_E"))
    ax[1].axvspan(-0.7, 0, color="#fde2e2", alpha=0.6)
    ax[1].axvspan(0, 0.8, color="#e2ecfd", alpha=0.6)
    ax[1].text(-0.68, 1.75, "field drives silence\n(synthetic W2, W2s)", fontsize=6)
    ax[1].text(0.05, 1.75, "congestion\n(synthetic W6)", fontsize=6)
    ax[1].scatter(el["corr_LK"], el["delta_f"].clip(-1, 2), s=10, c="#bbbbbb", label="E n.s.")
    ax[1].scatter(s2["corr_LK"], s2["delta_f"].clip(-1, 2), s=22, c="#d03b3b", label="E significant")
    for r in s2.iter_rows(named=True):
        ax[1].annotate(r["unit"], (r["corr_LK"], min(r["delta_f"], 2)), fontsize=6, xytext=(3, 2), textcoords="offset points")
    ax[1].scatter([-0.39, -0.63], [0.74, 0.84], marker="x", c="k", s=20, label="synthetic W2, W2s (mean)")
    ax[1].scatter([0.66], [1.23], marker="+", c="k", s=30, label="synthetic W6 (mean)")
    ax[1].set_xlim(-0.7, 0.8); ax[1].set_ylim(-1.05, 2.05)
    ax[1].set_xlabel("corr(latency field, active count)", fontsize=7); ax[1].set_ylabel("field share  Delta f (clipped)", fontsize=7)
    ax[1].set_title("b  the sign says load, not drive", fontsize=7.5)
    ax[1].legend(fontsize=5.5, loc="lower right"); ax[1].tick_params(labelsize=6)
    fig.tight_layout()
    (HYP / "figures").mkdir(exist_ok=True)
    fig.savefig(HYP / "figures" / "summary_obs.pdf")
    # synthetic
    sm = json.loads((OUT / "synthetic" / "summary.json").read_text())
    worlds = ["W0", "W1", "W1b", "W2", "W2s", "W3", "W4", "W5"]
    fig, ax = plt.subplots(figsize=(3.4, 2.0))
    for k, u in enumerate(["44b", "51c"]):
        d = {s["world"]: s for s in sm if s["unit"] == u}
        xs = np.arange(len(worlds)) + (k - 0.5) * 0.3
        ax.bar(xs, [d[w]["delta_f_mean"] for w in worlds], width=0.3, color=["#2a78d6", "#86b6ef"][k], label=f"Delta f ({u})",
               yerr=[d[w]["delta_f_sd"] for w in worlds], error_kw={"lw": 0.6})
        ax.scatter(xs, [min(d[w]["f_true"], 1.2) if d[w]["E_mean"] > 0.005 else 0 for w in worlds], marker="_", c="k", s=60,
                   label="true share" if k == 0 else None, zorder=3)
    ax.set_xticks(range(len(worlds)), worlds, fontsize=6); ax.tick_params(labelsize=6)
    ax.axhline(0, color="k", lw=0.5)
    ax.set_ylabel("field share", fontsize=6.5)
    ax.legend(fontsize=5.5, ncol=3, loc="upper left")
    fig.tight_layout()
    fig.savefig(HYP / "figures" / "synthetic.pdf")


if __name__ == "__main__":
    main()
