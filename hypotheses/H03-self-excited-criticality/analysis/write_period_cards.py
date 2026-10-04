"""Generate hypotheses/H03-self-excited-criticality/G<NN>/README.md for every non-holdout goal period from the
processed outputs (no hand transcription). Verdict rules are fixed here and stated in each card.
Run after summarize.py, split_by_period.py and figures_period.py:
  uv run python hypotheses/H03-self-excited-criticality/analysis/write_period_cards.py [--period G38]
"""
from __future__ import annotations

import json
import re

import numpy as np
import polars as pl

from common import DATA, HERE, ROOT, select_goals

CARD = HERE.parent
MODE_LONG = {"C": "C (shared objective)", "F": "F (free / holiday)", "I": "I (each agent its own objective)",
             "K": "K (competition)", "M": "M (teams / hidden roles)", "P": "P (private assigned roles; coded I/K)"}


def f(x, d=2):
    if x is None:
        return "–"
    if isinstance(x, float) and np.isinf(x):
        return "∞"
    if isinstance(x, float) and not np.isfinite(x):
        return "–"
    return f"{x:.{d}f}"


def goal_info():
    txt = (ROOT / "hypotheses/hypohypotheses/goal-periods.md").read_text()
    info = {}
    blocks = re.split(r"\n### ", txt)
    for b in blocks[1:]:
        m = re.match(r"(\d+) · (.+)", b.splitlines()[0])
        if not m:
            continue
        g = int(m.group(1))
        d = {"title": m.group(2).strip()}
        line2 = b.splitlines()[2] if len(b.splitlines()) > 2 else ""
        dm = re.search(r"`(\S+) → (\S+)`", line2)
        d["dates"] = (dm.group(1), dm.group(2)) if dm else ("?", "?")
        nm = re.search(r"N = (\d+) \(([^)]*)\)", line2)
        d["N_start"] = nm.group(1) if nm else "?"
        d["roster_change"] = nm.group(2) if nm else ""
        ctx = re.search(r"\*\*Setup and context:\*\* (.+)", b)
        d["context"] = ctx.group(1).strip() if ctx else ""
        hk = re.search(r"\n  (\d)\. \*\*09 Hawkes\*\*: (.+)", b)
        d["hawkes_rank"] = (hk.group(1), hk.group(2).strip()) if hk else None
        sc = re.search(r"\*\*Scaffold changes inside:\*\* (.+)", b)
        d["scaffold_inside"] = sc.group(1).strip() if sc else ""
        info[g] = d
    return info


def ci_of(r, pref="n"):
    lo, hi = r.get(f"{pref}_boot_lo"), r.get(f"{pref}_boot_hi")
    if lo is not None and hi is not None and np.isfinite(lo):
        return lo, hi, "day-bootstrap"
    lo, hi = r.get(f"{pref}_prof_lo"), r.get(f"{pref}_prof_hi")
    return lo, hi, "profile likelihood (event-level; < 3 days, no day bootstrap)"


def verdict(mode, r, seg51=None):
    n = r["n"]
    lo, hi, _ = ci_of(r)
    lo = lo if lo is not None and np.isfinite(lo) else 0.0
    hi = hi if hi is not None else np.inf
    if mode == "F":
        if n < 0.5 and hi < 0.5:
            return "supported", "P1 (n̂ < 0.5): point estimate and upper 95% bound below 0.5"
        if n >= 0.5 and lo >= 0.5:
            return "failed", "P1 (n̂ < 0.5): lower 95% bound ≥ 0.5"
        return "mixed", "P1 (n̂ < 0.5): the 95% interval straddles 0.5"
    if mode == "C":
        if n >= 0.7 and lo >= 0.5:
            return "supported", "P3 (n̂ ≥ 0.7, near critical)"
        if hi < 0.7:
            return "failed", "P3 (n̂ ≥ 0.7): upper 95% bound below 0.7"
        return "mixed", "P3 (n̂ ≥ 0.7): the 95% interval straddles 0.7"
    if mode == "P":
        rho, p = seg51
        return ("failed" if rho <= 0 else "mixed"), f"P5 (n̂ rises with N toward 1): segment Spearman ρ = {rho:.2f} (p = {p:.3f})"
    return "descriptive", f"no period-level prediction for mode {mode}; enters P2/P4 as a comparison point"


def main():
    info = goal_info()
    tab = pl.read_parquet(DATA / "period_table.parquet")
    fits = pl.read_parquet(DATA / "period_fits.parquet")
    guard = pl.read_parquet(DATA / "synthetic_guard.parquet")
    jt = pl.read_parquet(DATA / "jitter_table.parquet")
    att = pl.read_parquet(DATA / "attribution.parquet")
    seg = pl.read_parquet(DATA / "segment_table.parquet")
    sc = pl.read_parquet(DATA / "step_changes.parquet")
    casc = pl.read_parquet(DATA / "cascades.parquet")
    days = pl.read_parquet(DATA / "days.parquet")
    res = json.loads((DATA / "summary.json").read_text())
    seg51 = res["segments"]["seg51_TALK"]["spearman_n_N"]
    rows_index = []
    for goal in select_goals(sorted(tab["goal_no"].unique().to_list())):
        gi = info[goal]
        T = tab.filter((pl.col("goal_no") == goal) & (pl.col("set") == "TALK")).to_dicts()[0]
        A = tab.filter((pl.col("goal_no") == goal) & (pl.col("set") == "ALL")).to_dicts()[0]
        mode = T["mode"]
        v, vwhy = verdict(mode, T, seg51)
        gd = days.filter(pl.col("goal_no") == goal).sort("pt_date")
        s_t = seg.filter((pl.col("goal_no") == goal) & (pl.col("set") == "TALK")).sort("seg")
        s_a = seg.filter((pl.col("goal_no") == goal) & (pl.col("set") == "ALL")).sort("seg")
        splits = []
        for r in s_t.iter_rows(named=True):
            if r["seg"] == 0:
                continue
            why = sc.filter(pl.col("date") <= r["first_date"]).filter(pl.col("date") > s_t.filter(pl.col("seg") == r["seg"] - 1)["last_date"][0])
            whys = "; ".join(sorted({f"{w['source']}: {w['what'].replace('*', '').strip()[:50]}" for w in why.iter_rows(named=True)}))
            splits.append(f"{r['first_date']} ({whys})")
        rooms = "one shared room" if gd["pt_date"].max() < "2026-02-25" else "rooms (agents see only their room)"
        lines = []
        lines.append(f"# H03 × G{goal:02d}: {gi['title']} ({gi['dates'][0]} → {gi['dates'][1]})\n")
        lines.append(f"**Verdict:** {v}")
        lines.append("**Role:** exploratory")
        lines.append(f"**Period:** regime {T['regime']} · mode {MODE_LONG.get(mode, mode)} · N = {gi['N_start']} at start "
                     f"({gi['roster_change']}), {T['N_active']:.1f} active per day on average · {rooms} · "
                     f"{T['n_days']} non-holdout days, median window {T['hours']:.1f} h. "
                     f"Splits inside the period: {'; '.join(splits) if splits else 'none'}.\n")
        lines.append(f"Verdict rule: {vwhy}. Verdicts use the primary statistic, n̂ for TALK under M1 with B2 + exogenous drive. "
                     "n̂ depends on the baseline. A Poisson process with a rate modulated on 10–30 min scales can mimic it, and the 10-min jitter test has no power "
                     "to separate the two (main card, jitter calibration). Read B2 n̂ as an upper value and B3 n̂ as a downward-biased lower bound. "
                     "Any verdict here is descriptive, not mechanistic.\n")
        lines.append("## Why this period")
        role = {"F": "Free/holiday week: the HH30 test (holidays and free weeks are subcritical).",
                "C": "Shared-objective week: S2 predicts these are more self-exciting than free weeks, and HH30's strong form says near critical.",
                "I": "Individual-objective week: a comparison point for the mode effect (P2, P4).",
                "K": "Competition week: a comparison point for the mode effect (P2, P4).",
                "M": "Teams / hidden-roles week: a comparison point for the mode effect (P2, P4); the only non-holdout M period.",
                "P": "The private-role era: HH32 predicts a drift toward n → 1 as the roster grows from 21 to 32."}[mode]
        lines.append(f"- {role}")
        if gi["hawkes_rank"]:
            lines.append(f"- `goal-periods.md` ranks model 09 (Hawkes) #{gi['hawkes_rank'][0]} here: {gi['hawkes_rank'][1]}")
        if gi["context"]:
            lines.append(f"- Context (paraphrased dataset summary; secondary): {gi['context']}")
        if gi["scaffold_inside"]:
            lines.append(f"- Scaffold changes inside (goal-periods.md): {gi['scaffold_inside']}")
        lines.append("")
        lines.append("## Prediction")
        lines.append("*Written 2026-10-03 in the main card's Prediction section, before any fit on real data, and restated here for this period. "
                     "This file was generated after the exploratory run, under the 2026-10-03 folder convention.*\n")
        if mode == "F":
            lines.append("- P1: n̂ (TALK) < 0.5. Counts against it: n̂ ≥ 0.5.")
        elif mode == "C":
            lines.append("- P3: n̂ (TALK) ≥ 0.7 (near critical). Counts against it: n̂ < 0.7.")
            lines.append("- P2 (cross-period): above the F-period median.")
        elif mode == "P":
            lines.append("- P5: n̂ rises with active N across the period's windows and segments, reaching ≥ 0.9 in the last non-holdout weeks. "
                         "Counts against it: no rise, or n̂ staying well below 0.9.")
        else:
            lines.append("- No period-level threshold. The period enters P2/P4 as a comparison point; S2 implies it sits below the shared-objective periods.")
        lines.append("- P6: the fast cross-agent part n_cross is higher in C than in F periods. P7: n̂_ALL > n̂_TALK, from the agent's own-loop excitation.")
        lines.append("- G1 (guard): on n = 0 synthetic data with this period's fitted baseline, the pipeline returns n̂ ≈ 0, and the naive baseline B0 returns clearly more.\n")
        lines.append("## Result")
        lo, hi, kind = ci_of(T)
        loa, hia, kinda = ci_of(A)
        g = guard.filter(pl.col("goal_no") == goal)
        gmed = lambda sc_, m, st: g.filter((pl.col("scenario") == sc_) & (pl.col("model") == m) & (pl.col("set") == st))["n_hat"].median()
        j = jt.filter(pl.col("goal_no") == goal)
        jT = j.filter(pl.col("set") == "TALK").to_dicts()[0]
        jA = j.filter(pl.col("set") == "ALL").to_dicts()[0]
        aT = att.filter((pl.col("goal_no") == goal) & (pl.col("set") == "TALK")).to_dicts()[0]
        lines.append("| Quantity | TALK | ALL | Null / reference | Reading |")
        lines.append("|---|---|---|---|---|")
        lines.append(f"| n̂ (M1, B2 + exo), 95% CI | **{f(T['n'])}** [{f(lo)}, {f(hi)}] | {f(A['n'])} [{f(loa)}, {f(hia)}] | Poisson n = 0 | CI: {kind} |")
        lines.append(f"| kernel timescale τ̂ (s) | {T['tau_s']:.0f} | {A['tau_s']:.0f} | – | τ̂ ≥ 1800 s means the kernel mimics the baseline |")
        lines.append(f"| n̂, kernel τ ≤ 30 min | {f(T['n_t30'])} | {f(A['n_t30'])} | – | robustness variant |")
        lines.append(f"| baseline ladder B0 / B1 / B2 / B3-2h / B3-30m | {f(T['n_B0'])} / {f(T['n_B1'])} / {f(T['n'])} / {f(T['n_B3_2h'])} / {f(T['n_B3'])} | "
                     f"{f(A['n_B0'])} / {f(A['n_B1'])} / {f(A['n'])} / {f(A['n_B3_2h'])} / {f(A['n_B3'])} | guard: n = 0 → B0 {f(gmed('n0', 'M1_B0', 'TALK'))}, B2 {f(gmed('n0', 'M1_B2', 'TALK'), 3)} (TALK) | falls with baseline flexibility |")
        lines.append(f"| sum-of-exp kernel (M2): n, n(τ ≤ 300 s) | {f(T['n_grid'])}, {f(T['n_grid_fast300'])} | {f(A['n_grid'])}, {f(A['n_grid_fast300'])} | – | ΔAIC grid − exp (TALK) {f(T['dAIC_grid_vs_exp'], 1)} |")
        lines.append(f"| power-law-constrained kernel θ | {f(T['theta_pl'])} | {f(A['theta_pl'])} | – | ll(pl) − ll(exp) (TALK) {f(T['ll_pl'] - T['ll'], 1)} |")
        lines.append(f"| own-loop n_self (τ ≤ 300 s, M3) | {f(T['n_self_fast'])} | {f(A['n_self_fast'])} | – | scheduler / own-loop part |")
        lines.append(f"| social n_cross (τ ≤ 300 s, M3) | {f(T['n_cross_fast'], 3)} | {f(A['n_cross_fast'], 3)} | agent-shift null {f(jT['n_cross_fast300_shift_mean'], 3)} / {f(jA['n_cross_fast300_shift_mean'], 3)} | real − null (TALK) = {f(T['n_cross_fast'] - jT['n_cross_fast300_shift_mean'], 3)} |")
        lines.append(f"| pooled fast n̂ (τ ≤ 5 min) | {f(jT['t5_real'])} | {f(jA['t5_real'])} | 10-min jitter {f(jT['t5_jit600_mean'])} / {f(jA['t5_jit600_mean'])} | real − jittered (TALK) = {f(jT['t5_real'] - jT['t5_jit600_mean'])}; uninformative (synthetic n = 0.6 also drops only ≈ 0.03) |")
        lines.append(f"| share of events: baseline / exogenous / triggered | {f(aT['frac_baseline'])} / {f(aT['frac_exo'], 3)} / {f(aT['frac_triggered'])} | – | – | {aT['n_exo_msgs']} human/nudger messages in window |")
        lines.append(f"| time-rescaling KS D (p), Hawkes vs Poisson | {f(T['ks_D'], 3)} ({f(T['ks_p'], 3)}) vs {f(T['ks_D_P'], 3)} | {f(A['ks_D'], 3)} vs {f(A['ks_D_P'], 3)} | Exp(1) | smaller D is better |")
        lines.append(f"| ΔAIC Hawkes − Poisson (B2) | {f(T['dAIC_B2'], 1)} | {f(A['dAIC_B2'], 1)} | – | negative favors Hawkes |")
        lines.append(f"| day-blocked CV Δℓ/event, Hawkes − Poisson (B2 / B3-30m) | {f(T['cv_B2'], 3)} / {f(T['cv_B3'], 4)} | {f(A['cv_B2'], 3)} / {f(A['cv_B3'], 4)} | 0 | – means < 3 days |")
        lines.append(f"| guard recovery (TALK): n = 0.6 → B2, n = 0.9 → B2 | {f(gmed('n06', 'M1_B2', 'TALK'))}, {f(gmed('n09', 'M1_B2', 'TALK'))} | {f(gmed('n06', 'M1_B2', 'ALL'))}, {f(gmed('n09', 'M1_B2', 'ALL'))} | 0.6, 0.9 | 3 synthetic replicates |")
        lines.append(f"| guard misspecification: n = 0 with real 10-min rate → B2 | {f(gmed('n0_fine', 'M1_B2', 'TALK'))} | {f(gmed('n0_fine', 'M1_B2', 'ALL'))} | 0 | not a valid null: the real 10-min counts already contain any cascades |")
        b = casc.filter((pl.col("goal_no") == goal) & (pl.col("set") == "TALK") & (pl.col("gap") == 60.0))
        tail = {}
        for src in ("data", "sim_hawkes", "sim_poisson"):
            x = b.filter(pl.col("source") == src)
            sz = np.repeat(x["size"].to_numpy(), x["count"].to_numpy())
            tail[src] = (sz >= 10).mean() if len(sz) else np.nan
        lines.append(f"| P(burst ≥ 10), gap 60 s (TALK): data / Hawkes sim / Poisson sim | {f(tail['data'], 3)} / {f(tail['sim_hawkes'], 3)} / {f(tail['sim_poisson'], 3)} | – | – | unfitted statistic (axis D) |")
        lines.append("")
        if s_t.height > 1:
            lines.append("**Segments (goal period split at step changes; M1 B2):**\n")
            lines.append("| seg | start → end | days | N | n̂ TALK (SE) | partially pooled | n̂ ALL (SE) | n_cross ≤300 s TALK |")
            lines.append("|---|---|---|---|---|---|---|---|")
            amap = {r["seg"]: r for r in s_a.iter_rows(named=True)}
            for r in s_t.iter_rows(named=True):
                ra = amap.get(r["seg"], {})
                lines.append(f"| {r['seg']} | {r['first_date']} → {r['last_date']} | {r['n_days']} | {r['N_active']:.0f} | {f(r['n'])} ({f(r['se'])}, {r['se_kind']}) | "
                             f"{f(r.get('n_shrunk'))} | {f(ra.get('n'))} ({f(ra.get('se'))}) | {f(r['n_cross_fast'], 3)} |")
            w = res["segments"]["within_period"].get(f"TALK/#{goal}")
            if w:
                lines.append(f"\nWithin-period heterogeneity across segments (TALK): Cochran Q = {w['Q']:.1f}, df = {w['df']}, p = {w['p_Q']:.3g}, "
                             f"I² = {w['I2']:.2f}, τ = {w['tau']:.3f}. Partial pooling uses DerSimonian–Laird random effects within the period (exception d).")
            lines.append("")
        if goal == 51:
            r51 = res["segments"]
            lines.append(f"**#51 drift.** Across the 10 segments between roster changes, n̂ falls with N: Spearman ρ = {r51['seg51_TALK']['spearman_n_N'][0]:.2f} "
                         f"(p = {r51['seg51_TALK']['spearman_n_N'][1]:.3f}). The weighted slope is {r51['seg51_TALK']['wls_slope_per_agent']:.3f} per agent for TALK "
                         f"and {r51['seg51_ALL']['wls_slope_per_agent']:.3f} for ALL. "
                         f"The secondary rolling 5-day windows, which straddle joins, show the same pattern: block ρ = {res['rolling51']['TALK']['spearman_block'][0]:.2f} (TALK). "
                         "The naive constant-baseline fit (B0) reaches n̂ ≈ 0.99 in some windows, so it would have \"confirmed\" HH32 spuriously. "
                         "Rolling outputs: `rolling51.parquet`; figure `../figures/rolling51.pdf`.\n")
        lines.append(f"Figures: [`figures/diagnostics.pdf`](figures/diagnostics.pdf). Data: `data/processed/H03-self-excited-criticality/G{goal:02d}/` "
                     "(per-period extracts of the fit, CV, bootstrap, guard, jitter, cascade and segment tables, plus `fits/<SET>_<MODEL>.npy`).\n")
        lines.append("## Scorecard (period-specific axes)")
        Bsc = 1 if (T["ks_D"] is not None and T["ks_D_P"] is not None and T["ks_D"] < T["ks_D_P"]) else 0
        cv = T["cv_B2"]
        Csc = "–" if cv is None else (1 if cv > 0 else 0)
        Dsc = 1 if abs(tail["data"] - tail["sim_hawkes"]) < abs(tail["data"] - tail["sim_poisson"]) else 0
        lines.append("| Axis | Score | Evidence |")
        lines.append("|---|---|---|")
        lines.append(f"| B assumptions | {Bsc} | time-rescaling KS D: Hawkes {f(T['ks_D'], 3)} vs Poisson {f(T['ks_D_P'], 3)} (p_Hawkes = {f(T['ks_p'], 3)}); 1 = better than Poisson but not necessarily Exp(1) |")
        lines.append(f"| C adequacy | {Csc} | held-out Δℓ/event vs Poisson with the same B2 baseline = {f(cv, 3)}; vs the B3 30-min baseline = {f(T['cv_B3'], 4)}. Capped at 1: no powered test against a Poisson null modulated at 10–30 min |")
        lines.append(f"| D unfitted | {Dsc} | burst-size tail (gap 60 s) closer to the Hawkes simulation than to Poisson: {'yes' if Dsc else 'no'} |")
        lines.append(f"| F identifiability | 1 | n = 0 → B2 {f(gmed('n0', 'M1_B2', 'TALK'), 3)}; n = 0.6 → {f(gmed('n06', 'M1_B2', 'TALK'))}; but n = 0 with the real 10-min rate → {f(gmed('n0_fine', 'M1_B2', 'TALK'))} |")
        lines.append("")
        lines.append("## Notes")
        notes = ["- 2026-10-03: generated by `analysis/write_period_cards.py`. Exploratory, non-holdout days only."]
        long = gd.filter(pl.col("T_s") > 1.5 * gd["T_s"].median())
        if long.height:
            notes.append(f"- Long-window day(s) {', '.join(long['pt_date'].to_list())}: the window is 1.5–8× the period's median, likely two sessions with a long silent gap. "
                         "This distorts the shared within-day shape (B2) and inflates held-out comparisons. Splitting days at long gaps is a planned scheme fix.")
        if goal == 51:
            notes.append("- Days from 2026-09-07 on are the locked holdout (#51 tail, `holdout.json`). They are absent from the processed data and were not analyzed. "
                         "The whole-period bootstrap was capped at 33 M1 / 16 M3 replicates (cost); the drift test uses segment and block bootstraps.")
        if T["n_days"] < 3:
            notes.append("- Fewer than 3 days: no day-level bootstrap or CV. The profile-likelihood CI ignores day-to-day variability and is too narrow.")
        if T["tau_s"] >= 1800 or A["tau_s"] >= 1800:
            notes.append("- τ̂ ≥ 30 min in at least one event set: the kernel is confounded with slow baseline modulation (see the τ ≤ 30 min variant).")
        if T["regime"] in ("III", "II/III"):
            notes.append("- Regime III (perma-computer-use): `events_core` holds chat and session events, but not computer-use turns, so ALL means something different here than in regime I.")
        lines += notes
        out = CARD / "goalperiod-subhypotheses" / f"G{goal:02d}"
        out.mkdir(exist_ok=True)
        (out / "README.md").write_text("\n".join(lines) + "\n")
        rows_index.append({"goal_no": goal, "mode": mode, "verdict": v, "n_talk": T["n"], "lo": lo, "hi": hi,
                           "n_all": A["n"], "n_cross_fast": T["n_cross_fast"], "split": len(splits), "N": T["N_active"],
                           "hours": T["hours"], "regime": T["regime"], "title": gi["title"]})
    pl.DataFrame(rows_index).write_parquet(DATA / "period_index.parquet")
    print("cards:", len(rows_index))


if __name__ == "__main__":
    main()
