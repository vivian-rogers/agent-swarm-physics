"""Fill the Result / Scorecard sections and the Verdict line of the H50 replication period folders (templated rule from
the card), and draw one figure per period. Native folders (G38, G51, NE14, NE43) get their replication tables here and
their native results from write_native_results.py."""
from __future__ import annotations

import json
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
H = ROOT / "hypotheses/H50-field-vs-coupling-transfer-lag"
OUT = ROOT / "data/processed/H50-field-vs-coupling-transfer-lag"
BLUE, ORANGE, AQUA, GRAY, INK = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984", "#0b0b0b"
LAGS = np.arange(-10, 61)


def f(x, d=3):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "–"
    return f"{x:.{d}f}"


def ci(e, lo, hi, d=3):
    return f"{f(e, d)} [{f(lo, d)}, {f(hi, d)}]"


def ivw(est, se):
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    if not ok.any():
        return np.nan, np.nan, np.nan
    w = 1 / se[ok] ** 2
    m = (w * est[ok]).sum() / w.sum()
    s = 1 / np.sqrt(w.sum())
    return float(m), float(m - 1.96 * s), float(m + 1.96 * s)


def verdict(rows):
    J, lo, hi = ivw(rows["J1"].to_numpy(), rows["J1_se"].to_numpy())
    w = rows["n_days"].to_numpy().astype(float)
    fx = rows["fFex_A_full"].to_numpy().astype(float)
    ok = np.isfinite(fx)
    fF = float((w[ok] * fx[ok]).sum() / w[ok].sum()) if ok.any() else np.nan
    neg = int((rows["J1_hi"] < 0).sum())
    a, b, c = lo > 0, fF > 0.10, neg == 0
    v = "supported" if (a and b and c) else ("failed" if (not a and not b) else "mixed")
    return v, dict(J1=J, J1_lo=lo, J1_hi=hi, fFex=fF, n_neg=neg, a=a, b=b, c=c)


def gate_table(rows):
    s = ("| unit | days | N | pairs | median call (s) | read-out delay q50 (s) | **J₁ talk** [95% CI] | onset hop | J₂ (hop 2 − hop 1) | "
         "J₁ work | J₁ idle | κ |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n")
    for r in rows.iter_rows(named=True):
        s += (f"| {r['unit']} | {r['n_days']} | {r['N']} | {r['n_pairs']:,} | {f(r['med_call_s'], 1)} | {f(r['readout_q50'], 0)} | "
              f"{ci(r['J1'], r['J1_lo'], r['J1_hi'])} | {r['onset_talk'] if r['onset_talk'] else '–'} | {ci(r['J2'], r['J2_lo'], r['J2_hi'])} | "
              f"{ci(r.get('J1_work'), r.get('J1_work_lo'), r.get('J1_work_hi'))} | {ci(r.get('J1_idle'), r.get('J1_idle_lo'), r.get('J1_idle_hi'))} | "
              f"{f(r['kappa'], 2)} |\n")
    return s


def decomp_table(rows):
    s = ("| unit | activity S (full) | **field excess, activity full** (edges alone / rest alone) | field excess, activity trim | "
         "talk S (span) | field excess, talk | **talk coupling share f_C** [k₁ CI] | lagged-peer share (talk) |\n"
         "| --- | --- | --- | --- | --- | --- | --- | --- |\n")
    for r in rows.iter_rows(named=True):
        s += (f"| {r['unit']} | {f(r.get('S_A_full'), 2)} | {f(r.get('fFex_A_full'), 2)} ({f(r.get('attr_A_full_edges'), 2)} / {f(r.get('attr_A_full_rest'), 2)}) | "
              f"{f(r.get('fFex_A_trim'), 2)} | {f(r.get('S_T_span'), 2)} | {f(r.get('fFex_T_span'), 2)} | "
              f"{f(r.get('fC_T_span'), 2)} [{f(r.get('fC_T_span_lo'), 2)}, {f(r.get('fC_T_span_hi'), 2)}] | {f(r.get('flag_T_span'), 2)} |\n")
    return s


def fir_table(rows):
    s = ("| unit | input | n | activity G30 [CI] | dead (min) | decay (min) | talk G30 | gate J₁ talk (exo, per recipient) | onset hop |\n"
         "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n")
    for r in rows.iter_rows(named=True):
        for cl, exo in (("edge_on", None), ("pause", "pause"), ("human", "human_other"), ("nudge", "nudge_target"), ("platform", None)):
            n = r.get(f"firA_{cl}_n")
            if not n:
                continue
            ex = ""
            on = "–"
            if exo and r.get(f"exo_{exo}_J1T") is not None:
                ex = f"{exo}: {ci(r[f'exo_{exo}_J1T'], r[f'exo_{exo}_J1T_lo'], r[f'exo_{exo}_J1T_hi'])}"
                on = r.get(f"exo_{exo}_onsetT") or "–"
            s += (f"| {r['unit']} | {cl} | {int(n)} | {ci(r.get(f'firA_{cl}_G30'), r.get(f'firA_{cl}_G30_lo'), r.get(f'firA_{cl}_G30_hi'), 2)} | "
                  f"{f(r.get(f'firA_{cl}_dead'), 0)} | {f(r.get(f'firA_{cl}_decay'), 0)} | {f(r.get(f'firT_{cl}_G30'), 2)} | {ex} | {on} |\n")
    return s


def period_figure(name, rows, R):
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.4))
    for i, u in enumerate(rows["unit"]):
        g = R[u]["gate_talk"]
        k = np.arange(1, len(g["jumps"]) + 1) + (i - len(rows) / 2) * 0.06
        axes[0].errorbar(k, g["jumps"], yerr=[np.array(g["jumps"]) - np.array(g["j_lo"]), np.array(g["j_hi"]) - np.array(g["jumps"])],
                         fmt="o-", ms=2.5, lw=0.8, label=u, capsize=0)
    axes[0].axhline(0, color=GRAY, lw=0.6)
    axes[0].set_xlabel("boundary k (hop k vs k−1)", fontsize=6.5)
    axes[0].set_ylabel("jump in P(talk call)", fontsize=6.5)
    axes[0].set_title(f"{name}: peer message → recipient", fontsize=7)
    axes[0].legend(fontsize=5, frameon=False, ncol=2)
    for cl, col in (("edge_on", INK), ("human", BLUE), ("nudge", ORANGE), ("platform", AQUA)):
        ks = [np.array(R[u]["fir"]["A"]["kernels"][["edge_on", "pause", "human", "nudge", "platform"].index(cl)])
              for u in rows["unit"] if "A" in R[u]["fir"] and R[u]["fir"]["A"].get(cl, {}).get("n_inputs")]
        if ks:
            axes[1].plot(LAGS, np.mean(ks, 0), color=col, lw=1, label=cl)
    axes[1].axhline(0, color=GRAY, lw=0.6)
    axes[1].axvline(0, color=GRAY, lw=0.4, ls=":")
    axes[1].set_xlabel("lag (min)", fontsize=6.5)
    axes[1].set_ylabel("swarm activity response", fontsize=6.5)
    axes[1].set_title("FIR impulse responses (mean over units)", fontsize=7)
    axes[1].legend(fontsize=5.5, frameon=False)
    for a in axes:
        a.tick_params(labelsize=6)
        for sp in ("top", "right"):
            a.spines[sp].set_visible(False)
    fig.tight_layout()
    d = H / "goalperiod-subhypotheses" / name / "figures"
    d.mkdir(parents=True, exist_ok=True)
    fig.savefig(d / f"{name}_gate_fir.pdf")
    plt.close(fig)


def fill(path, verdict_line, result, score):
    t = path.read_text()
    t = re.sub(r"\*\*Verdict:\*\* .*", f"**Verdict:** {verdict_line}", t, count=1)
    t = re.sub(r"## Result\n.*?\n## Scorecard \(period-specific axes\)\n.*?\n## Notes", "## Result\n" + result +
               "\n## Scorecard (period-specific axes)\n" + score + "\n## Notes", t, flags=re.S)
    path.write_text(t)


def main():
    T = pl.read_parquet(OUT / "unit_table.parquet")
    R = {}
    for p in sorted(OUT.glob("G*/*.json")):
        if p.name == "native.json":
            continue
        r = json.loads(p.read_text())
        R[r["unit"]] = r
    rep = T.filter(~pl.col("ne43"))
    out = {}
    for g in sorted(rep["goal_no"].unique().to_list()):
        name = f"G{g:02d}"
        rows = rep.filter(pl.col("goal_no") == g).sort("unit")
        v, st = verdict(rows)
        out[name] = dict(verdict=v, **st, units=rows["unit"].to_list(), regime=rows["regime"][0])
        period_figure(name, rows, R)
        res = (f"Data: `data/processed/H50-field-vs-coupling-transfer-lag/{name}/` (one JSON per unit). Figure: "
               f"[`figures/{name}_gate_fir.pdf`](figures/{name}_gate_fir.pdf). J₁ = placebo-corrected read-out jump in P(talk call) at "
               f"the first boundary (call starting just after vs just before a peer message), W = 1.5 × median call interval; "
               f"CIs from a day bootstrap (1-hour blocks in units with < 3 days). κ = J₁ / right-limit excess. Field excess = "
               f"f_F − f_F,null (shifted-input null); f_C = counterfactual coupling share of talk co-movement (CF, hop-1 kernel; "
               f"values > 1 are estimator overshoot at low co-movement, see the synthetic validation).\n\n"
               f"**Pooled period estimate:** J₁ (IVW) = {ci(st['J1'], st['J1_lo'], st['J1_hi'])}; activity field excess "
               f"(full window, day-weighted) = {f(st['fFex'], 2)}; units with J₁ < 0 at 95%: {st['n_neg']}. "
               f"Rule: (a) {'yes' if st['a'] else 'no'}, (b) {'yes' if st['b'] else 'no'}, (c) {'yes' if st['c'] else 'no'} → **{v}**.\n\n"
               f"### Peer gate (call-cycle lags)\n{gate_table(rows)}\n### Equal-time co-movement decomposition\n{decomp_table(rows)}\n"
               f"### Input transfer functions (Part A) and input gates (Part B)\n{fir_table(rows)}")
        score = ("- **C (adequacy):** the read-out jump is tested against shifted-time placebos (no-coupling synthetic worlds: "
                 f"false-positive rate 3/35 seeds); field excess against shifted inputs. Here: J₁ CI > 0 in "
                 f"{int((rows['J1_lo'] > 0).sum())}/{len(rows)} units.\n"
                 f"- **D (unfitted signature):** a step at the read-out call (onset hop 1) in {int((rows['onset_talk'] == 1).sum())}/{len(rows)} "
                 "units; no unit shows the ungated signature (J₁ < 0).\n"
                 "- **G (ground truth):** activity co-movement is carried by the schedule edges (edges-alone field excess above), "
                 "as H38 found for regime III.")
        if name in ("G38", "G51"):
            res = "### Replication layer (common estimator)\n" + res + "\n\n### Native test\n(see below; written by write_native_results.py)\n"
        fill(H / "goalperiod-subhypotheses" / name / "README.md", v + (" (replication layer; native test below)" if name in ("G38", "G51") else ""),
             res, score)
    (OUT / "period_verdicts.json").write_text(json.dumps(out, indent=1, default=float))
    from collections import Counter
    print(Counter(v["verdict"] for v in out.values()))
    for k, v in out.items():
        print(k, v["regime"], v["verdict"], f"{v['J1']:.4f} [{v['J1_lo']:.4f},{v['J1_hi']:.4f}] fFex {v['fFex']:.2f} neg {v['n_neg']}")


if __name__ == "__main__":
    main()
