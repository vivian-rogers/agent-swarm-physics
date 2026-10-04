"""Write / update the H16 G<NN>/README.md files.

`--predictions` writes each folder's header, "Why this period" and dated "Prediction" (only if the README does not exist
yet; an existing Prediction section is never rewritten). `--results` fills Verdict, Result and Scorecard from
data/processed/H16-metastable-traps-kramers/<period>/results.json, keeping the Prediction section verbatim.

Usage: uv run python hypotheses/H16-metastable-traps-kramers/analysis/write_period_folders.py --predictions | --results
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h16lib as L  # noqa: E402

PRED_DATE = "2026-10-03"
INFO = {
    "G27": ("Hack the OWASP Juice Shop (competition)", "2026-01-12 → 2026-01-23", "I", "K", "10 agents · #general only · 10 days",
            "Longest clean regime-I period before the nudger (NE10). Message-triggered escape (H09) can be tested without "
            "nudges; competition mode (K) gives individual work with bursty room chat. N_tgt is untestable here."),
    "G30": ("Adopt a park and get it cleaned", "2026-02-09 → 2026-02-13", "I", "C", "11 agents · #general · 5 days",
            "Regime I with the nudger switching on (first nudges 02-13, NE10). Shared objective (C): more directed chat "
            "than G27. Nudge effects rest on one day only."),
    "G31": ("Pick your own goal (farewell to 3.7 Sonnet)", "2026-02-16 → 2026-02-19 (02-20 excluded: NE11)", "I", "F",
            "12 agents · #general · 4 days",
            "Free period in regime I with the nudger on; the last non-holdout regime-I days before the 100-turn session cap "
            "(NE11) and before the held-out #32. Closest regime-I stand-in for the #32 confirmation."),
    "G37": ("Pick your own goal!", "2026-03-30 → 2026-04-01", "III", "F", "13 agents · #best / #rest · 3 days",
            "First regime-III goal (timer-gated PAUSE chains, H09). Only 3 days: low power; descriptive weight."),
    "G38": ("Choose a charity and raise money", "2026-04-02 → 2026-04-24", "III", "C", "12–14 agents · #best / #rest · 17 days",
            "Longest 4-h regime-III period; a shared objective with outreach waiting (approval system from 04-14, NE17), a "
            "natural source of waiting traps. NE17 split is a sensitivity check."),
    "G39": ("Build your own interactive world", "2026-04-27 → 2026-05-01", "III", "I", "15 agents · reshuffled rooms · 5 days",
            "Individual objectives (I): traps should be individual, swarm coupling weak; a clean regime-III replicate."),
    "G40": ("Connect your worlds into a 3D universe", "2026-05-04 → 2026-05-08", "III", "C", "15 agents · #universe-coordination · 5 days",
            "Shared objective with one coordination room: the most directed chat in regime III (H02/H05 found the "
            "strongest collective co-activation here), so the best regime-III case for kick effects and for any swarm bimodality."),
    "G41": ("Perform novel research", "2026-05-11 → 2026-05-15", "III", "I", "15 agents · 5 days",
            "Individual research projects: long solo work, plausible theory spirals and error loops."),
    "G42": ("Run your own YouTube channel", "2026-05-18 → 2026-05-22", "III", "I", "15–16 agents · 5 days",
            "Individual production work with tooling (video pipelines): a candidate for error and command loops."),
    "G44": ("Finetune your leader", "2026-05-26 → 2026-05-29", "III", "C", "16–18 agents · #best fine-tunes / #rest creative · 4 days",
            "Mixed: #best runs a fine-tuning pipeline (waiting on jobs: polling loops), #rest does creative work; many "
            "human messages (59). Last non-holdout period before the held-out #45."),
    "G51": ("Private roles (long goal)", "2026-07-06 → 2026-09-02 (non-holdout, pre-NE33)", "III", "P (I/K)",
            "21–32 agents · 8-h days · ~40 days",
            "The private-role era: 8-h days, largest roster, most nudges (773 automated messages). By far the most power "
            "for every test; plans hidden from others (NE26), so coupling should be weakest."),
}

PRED = {
    "I": """*Written {d}, before running on this period.* The card's predictions as they apply to a regime-I period:
- **(a)** TS1r deep-window slope β (agent FE, ≥ 10 min) < −0.3 with CI below −0.3 (aging; P-a2). With kick covariates added,
  |β| shrinks toward 0 (P-a3: driven Kramers). TS3/TS4 loops: aging (P-a5/a6) if ≥ 15 deep escapes. TS2 not applicable.
- **(b)** ≥ 50% of agents have a double well in G(x) (P-b0). Markov-embedding closure holds: median |ln(k_obs/k_MSM2)| ≤ 0.3
  (P-b2, regime I). 1D closure misses by > 2× (P-b3, not diagnostic). Arrhenius slope of ln k_TS1r,deep on ΔG in
  [−1.2, −0.2] if ≥ 6 eligible agents (P-b1).
- **(c)** Undirected kicks: HR ≥ 1.5 and above the day-swap null p95 (P-c1); directed HR ≥ 1.5 (ordering low confidence).
  Dose law, if powered: additive or saturating preferred over Kramers (P-c4).
- **(d)** βJ₀ < 1 (expected 0–0.6); no valley bimodality beyond the null with joint silences excluded; no branch-memory
  excess (P-d1–d3).
- **Against:** a memoryless deep slope (|β| ≤ 0.3, CI inside the band) supports Kramers; undirected HR ≤ 1 contradicts
  message-triggered escape; βJ₀ < 1 with significant bimodality after stall exclusion falsifies the mean-field claim.""",
    "III": """*Written {d}, before running on this period.* The card's predictions as they apply to a regime-III period:
- **(a)** TS1r deep-window slope β (agent FE, ≥ 10 min) < −0.3 with CI below −0.3 (aging; P-a1). TS2 per-gate escape falls
  with gate index after declared duration (β_lnk < 0, CI excluding 0) and re-pauses keep or lengthen the declared duration
  (median log ratio ≥ 0) (P-a4). TS3/TS4 loops: aging if ≥ 15 deep escapes (P-a5/a6).
- **(b)** ≥ 50% of agents with a double well (P-b0). Markov-embedding closure fails with k_obs < k_pred (median
  |ln ratio| > 0.3; memory from timers/aging; P-b2). 1D closure misses by > 2× (P-b3). Arrhenius slope in [−1.2, −0.2] if
  ≥ 6 eligible agents (P-b1).
- **(c)** TS1: undirected HR within [0.8, 1.25] or CI including 1; directed HR ≥ 1.3 above the day-swap null p95 (P-c2).
  TS2: directed kicks during the pause raise gate escape odds, OR ≥ 1.5 (P-c3); undirected OR CI includes 1. N_tgt in the
  15-min window: ln HR > 0 (P-c5). Dose law, if powered: not Kramers (P-c4).
- **(d)** βJ₀ < 1 (expected 0–0.6); no valley bimodality beyond the null with joint silences excluded; no branch-memory
  excess (P-d1–d3).
- **Against:** memoryless TS1r/TS2 slopes support Kramers; undirected kicks raising escape contradict the timer-gate picture;
  βJ₀ < 1 with significant bimodality after stall exclusion falsifies the mean-field claim.""",
}
EXTRA = {
    "G27": "\n- Period-specific: no nudges (N_tgt/c5 untestable); 7 human messages only, so human kicks are underpowered.",
    "G30": "\n- Period-specific: nudges exist on 02-13 only; N_tgt effects are not scored.",
    "G31": "\n- Period-specific: 4 days; nudger on; power for directed kicks low.",
    "G37": "\n- Period-specific: 3 days; most per-period tests are expected to be underpowered (verdict likely mixed/descriptive).",
    "G38": "\n- Period-specific: the NE17 split (04-14) is a sensitivity check; same sign of the TS1r and TS2 slopes is expected on both sides.",
    "G40": "\n- Period-specific: the strongest collective co-activation in regime III (H02/H05) → the largest βJ₀ of regime III expected here, still < 1.",
    "G44": "\n- Period-specific: #best's fine-tuning pipeline makes TS4 (polling/identical-command loops) more common than elsewhere.",
    "G51": "\n- Period-specific: 8-h days; highest power, so the per-period verdicts here carry the most weight; plans hidden (NE26) → βJ₀ expected among the lowest.",
}


NOTES = {
    "G37": "- 2026-10-03 (post hoc): the 03-31 window spans 755 min with a 513-min village-off gap (all agents silent). It inflates βJ₀ "
           "(1.10 with K = 0 minutes excluded; 0.35 against the within-day circular-shift null, A4) and makes the pre-registered valley "
           "test fire with stalls included. TS1r slopes are unchanged by outage censoring (A3), because spells > 4 h were already censored.",
    "G38": "- 2026-10-03: one 213-min village-off gap (A3). Stall minutes (5.4%) drive βJ₀ 0.71 → 0.09 and the stall-included "
           "bimodality, as anticipated from synthetic data. NE17 split: aging on both sides (TS1r −1.85 / −1.39; TS2r −0.50 / −0.38).",
    "G44": "- 2026-10-03 (post hoc): the pre-registered valley test fails (p = 0.005, stalls excluded; also against the A4 circular-shift "
           "null). Diagnostic: neither room alone is bimodal, and the 'second mode' is about three near-silent minutes (K = 1 of 17) that "
           "the K = 0 stall rule misses. With a ≥ 5%-mass rule per mode (A5; synthetic: still detects βJ₀ ≥ 1.3) the period is unimodal. "
           "Reported as a pre-registered failure with this diagnosis. The 4-day bootstrap CIs here are degenerate (the full-sample "
           "estimate sits at the edge of its own bootstrap distribution); see the Wald CIs.",
    "G51": "- 2026-10-03: 6 days with village-off gaps (7 outages, 930 min). A3 outage censoring changes the TS1r deep slope from "
           "−0.77 to −0.65. Branch memory (residual ACF at 30 min 0.53 vs null p95 0.23) without bimodality: slow collective "
           "persistence, not bistability.",
    "G30": "- 2026-10-03: the timer-like TS1r deep slope (+2.61) rests on 24 deep escapes in 5 days; treat as noise-limited.",
    "G27": "- 2026-10-03: no nudges (N_tgt untestable); kicks are almost all agent room messages (A_und 3,692 kicked bins).",
}


def header(p, verdict="pending"):
    t, dates, reg, mode, size, _ = INFO[p]
    return (f"# H16 × {p}: {t} ({dates})\n\n**Verdict:** {verdict}\n**Role:** exploratory (round 1, non-holdout)\n"
            f"**Period:** regime {reg} · mode {mode} · {size}. Splits or exclusions: see the main card's period table.\n")


def write_predictions():
    for p, (t, dates, reg, mode, size, why) in INFO.items():
        f = L.HDIR / p / "README.md"
        (L.HDIR / p / "figures").mkdir(parents=True, exist_ok=True)
        if f.exists():
            print("exists, kept:", f)
            continue
        body = header(p) + f"\n## Why this period\n{why}\n\n## Prediction\n" + PRED[reg].format(d=PRED_DATE) + EXTRA.get(p, "") + \
            "\n\n## Result\n(pending)\n\n## Scorecard (period-specific axes)\n(pending)\n\n## Notes\n"
        f.write_text(body)
        print("wrote", f)


def fmt(x, n=2):
    try:
        if x is None or (isinstance(x, float) and x != x):
            return "–"
        return f"{x:.{n}f}"
    except Exception:
        return str(x)


def ci(v):
    if not v or any(z is None for z in v):
        return ""
    return f" [{fmt(v[0])}, {fmt(v[1])}]"


def score_period(R, reg):
    """Per-prediction outcomes for one period: returns list of (id, prediction, observed, verdict)."""
    rows = []
    a = R["a"]
    t1r = a["TS1r"].get("deep", {})
    if t1r.get("ok"):
        b, lo, hi = t1r["beta_agentFE"], *t1r["ci"]
        v = "supported" if hi < -0.3 else ("failed (memoryless)" if (lo >= -0.3 and hi <= 0.3) else ("failed (timer-like)" if lo > 0.3 else "inconclusive"))
        wl, wh = t1r.get("ci_wald", [None, None])
        vw = "supported" if wh < -0.3 else ("failed (memoryless)" if (wl >= -0.3 and wh <= 0.3) else ("failed (timer-like)" if wl > 0.3 else "inconclusive"))
        rows.append(("P-a1" if reg == "III" else "P-a2", "TS1r deep slope < −0.3 (aging)",
                     f"β = {fmt(b)}; boot CI{ci(t1r['ci'])}; Wald CI{ci(t1r.get('ci_wald'))} [Wald verdict: {vw}]; {t1r['events']} deep escapes; pooled β {fmt(t1r.get('beta_pooled'))}", v))
    else:
        rows.append(("P-a1" if reg == "III" else "P-a2", "TS1r deep slope < −0.3", "too few deep escapes", "n/a"))
    c1 = R["c"]["TS1"]
    if reg == "I" and c1.get("ok") and "a2_deep_slope_with_kicks" in c1:
        w, wo = c1["a2_deep_slope_with_kicks"], c1["a2_deep_slope_without_kicks"]
        rows.append(("P-a3", "|β| shrinks with kick covariates (TS1 deep)", f"{fmt(wo)} → {fmt(w)}", "supported" if abs(w) < abs(wo) else "failed"))
    if reg == "III":
        t2 = a["TS2"]
        if not t2.get("ok"):
            rows.append(("P-a4", "gate escape falls with k, strict TS2", f"n/a: {t2.get('reason', 'too few')} ({t2.get('n_repause', '?')} re-pauses)", "n/a (no strict chains)"))
        t2r = a.get("TS2r", {})
        if t2r.get("ok"):
            b, lo, hi = t2r["beta_lnk_agentFE"], *t2r["ci"]
            v = "supported" if hi < 0 else ("failed" if lo > 0 else "inconclusive")
            wl, wh = t2r.get("ci_wald", [None, None])
            vw = "supported" if wh < 0 else ("failed" if wl > 0 else "inconclusive")
            rows.append(("P-a4 (TS2r, amended)", "gate escape falls with k (agent FE)", f"β_lnk = {fmt(b)}; boot CI{ci(t2r['ci'])}; Wald CI{ci(t2r.get('ci_wald'))} [Wald verdict: {vw}]; {t2r['n_gates']} gates; pooled {fmt(t2r.get('beta_lnk_pooled'))}", v))
            dpr = t2r.get("deepening", {})
            if dpr:
                rows.append(("P-a4b (TS2r, amended)", "re-pause keeps/lengthens declared duration", f"median ln(next/cur) = {fmt(dpr['median_log_ratio_next_over_current'])}; longer {fmt(dpr['frac_longer'])}, shorter {fmt(dpr['frac_shorter'])}",
                             "supported" if dpr["median_log_ratio_next_over_current"] >= 0 else "failed"))
        if t2.get("ok"):
            b, lo, hi = t2["beta_lnk_agentFE"], *t2["ci"]
            v = "supported" if hi < 0 else ("failed" if lo > 0 else "inconclusive")
            dp = t2.get("deepening", {})
            rows.append(("P-a4", "gate escape falls with k (agent FE), strict TS2", f"β_lnk = {fmt(b)}; boot CI{ci(t2['ci'])}; Wald CI{ci(t2.get('ci_wald'))}; {t2['n_gates']} gates", v))
            if dp:
                rows.append(("P-a4b", "re-pause keeps/lengthens declared duration", f"median ln(next/cur) = {fmt(dp['median_log_ratio_next_over_current'])}; longer {fmt(dp['frac_longer'])}, shorter {fmt(dp['frac_shorter'])}",
                             "supported" if dp["median_log_ratio_next_over_current"] >= 0 else "failed"))
    for key, pid in (("TS3", "P-a5"), ("TS4", "P-a6")):
        d = a[key].get("deep", {}) if a[key].get("ok") else {}
        if d.get("ok"):
            b, lo, hi = d["beta_agentFE"], *d["ci"]
            v = "supported" if hi < -0.3 else ("failed (memoryless)" if (lo >= -0.3 and hi <= 0.3) else ("failed (timer-like)" if lo > 0.3 else "inconclusive"))
            wl, wh = d.get("ci_wald", [None, None])
            vw = "supported" if wh < -0.3 else ("failed (memoryless)" if (wl >= -0.3 and wh <= 0.3) else ("failed (timer-like)" if wl > 0.3 else "inconclusive"))
            rows.append((pid, f"{key} loop aging (k ≥ 3)", f"β = {fmt(b)}; boot CI{ci(d['ci'])}; Wald CI{ci(d.get('ci_wald'))} [Wald verdict: {vw}]; {d['events']} escapes", v))
        else:
            rows.append((pid, f"{key} loop aging", "too few", "n/a"))
    b = R["b"]
    if b.get("ok"):
        fd = b.get("frac_double_well")
        rows.append(("P-b0", "≥ 50% agents double well", f"{fmt(fd)} of {b['n_cells']} agents", ("supported" if (fd is not None and fd >= 0.5) else ("failed" if b['n_cells'] else "n/a")) + " (not diagnostic: coordinate artifact)"))
        m2 = b["closure"].get("mfpt_msm2", {})
        if m2.get("n", 0) >= 3:
            med, sgn = m2["median_abs_ln_ratio"], m2["median_ln_obs_over_pred"]
            if reg == "I":
                v = "supported" if med <= 0.3 else "failed"
            else:
                v = "supported" if (med > 0.3 and sgn < 0) else "failed"
            rows.append(("P-b2", "MSM2 closure " + ("holds (≤ 0.3)" if reg == "I" else "fails, obs slower"), f"median |ln| = {fmt(med)}, median ln(obs/pred) = {fmt(sgn)} (n = {m2['n']})", v + " (not diagnostic: one-step passage, tautological)"))
        else:
            rows.append(("P-b2", "MSM2 closure", f"n = {m2.get('n', 0)} agents with ≥ 15 passages", "n/a"))
        m1 = b["closure"].get("mfpt_1d", {})
        if m1.get("n", 0) >= 3:
            rows.append(("P-b3", "1D closure misses > 2× (not diagnostic)", f"median |ln| = {fmt(m1['median_abs_ln_ratio'])}", ("supported" if m1["median_abs_ln_ratio"] > 0.7 else "failed") + " (not diagnostic)"))
        ar = b.get("arrhenius_ln_kts1r_on_dG")
        if ar and ar["n"] >= 6:
            rows.append(("P-b1", "Arrhenius slope in [−1.2, −0.2]", f"slope {fmt(ar['slope'])} (n = {ar['n']}, Spearman {fmt(ar['spearman'])})",
                         ("supported" if -1.2 <= ar["slope"] <= -0.2 else "failed") + " (weak: largely mechanical)"))
        else:
            rows.append(("P-b1", "Arrhenius slope", f"n = {ar['n'] if ar else 0} eligible agents (< 6)", "n/a"))
    if c1.get("ok"):
        ud, us = c1["any_undirected_lnHR"], c1["any_undirected_se"]
        dd, ds = c1["any_directed_lnHR"], c1["any_directed_se"]
        np95u, np95d = c1.get("null_undirected_lnHR_p95"), c1.get("null_directed_lnHR_p95")
        if reg == "I":
            v = "supported" if (ud >= 0.405 and ud > np95u) else "failed"
            rows.append(("P-c1", "undirected HR ≥ 1.5, > null p95", f"HR {fmt(2.718281828 ** ud)} (ln {fmt(ud)} ± {fmt(1.96 * us)}); null p95 ln {fmt(np95u)}", v))
            rows.append(("P-c1b", "directed HR ≥ 1.5", f"HR {fmt(2.718281828 ** dd)} (ln {fmt(dd)} ± {fmt(1.96 * ds)}); null p95 ln {fmt(np95d)}",
                         "supported" if dd >= 0.405 and dd > np95d else "failed"))
        else:
            ok_u = (abs(ud) <= 0.223) or (abs(ud) < 1.96 * us)
            rows.append(("P-c2", "undirected ≈ 1 (TS1)", f"HR {fmt(2.718281828 ** ud)} (ln {fmt(ud)} ± {fmt(1.96 * us)})", "supported" if ok_u else "failed"))
            rows.append(("P-c2b", "directed HR ≥ 1.3, > null p95 (TS1)", f"HR {fmt(2.718281828 ** dd)} (ln {fmt(dd)} ± {fmt(1.96 * ds)}); null p95 ln {fmt(np95d)}",
                         "supported" if dd >= 0.262 and dd > np95d else "failed"))
            if "nudge_slow15_lnHR" in c1:
                rows.append(("P-c5", "N_tgt 15-min window ln HR > 0", f"ln HR {fmt(c1['nudge_slow15_lnHR'])} ± {fmt(1.96 * c1['nudge_slow15_se'])} ({c1['nudge_slow15_bins']} bins)",
                             "supported" if c1["nudge_slow15_lnHR"] - 1.96 * c1["nudge_slow15_se"] > 0 else ("failed" if c1["nudge_slow15_lnHR"] <= 0 else "inconclusive")))
        for grp in ("directed", "undirected"):
            dl = c1.get(f"dose_{grp}", {})
            if dl.get("powered"):
                rows.append(("P-c4", f"dose law {grp} (TS1): not Kramers", f"best {dl['best']}; κ = {fmt(dl.get('kappa'))}; escapes at dose ≥ 2: {dl['events_dose_ge2']}",
                             "supported" if dl["best"] in ("additive", "saturating") else "failed"))
    if reg == "III":
        c2r = R["c"].get("TS2r", {})
        if c2r.get("ok"):
            ddr = c2r.get("dose_directed", {})
            lo = ddr.get("lnOR", [None])[0]; se = ddr.get("se", [None])[0]
            if lo is not None and lo == lo:
                rows.append(("P-c3 (TS2r, amended)", "directed kick during pause: gate OR ≥ 1.5", f"OR(dose 1) {fmt(2.718281828 ** lo)} (ln {fmt(lo)} ± {fmt(1.96 * se)}); kicked gates by dose {ddr['n_gates'][1:]}",
                             "supported" if (lo >= 0.405 and lo - 1.96 * se > 0) else "failed"))
            udr = c2r.get("dose_undirected", {})
            lu = udr.get("lnOR", [None])[0]; su = udr.get("se", [None])[0]
            if lu is not None and lu == lu:
                rows.append(("P-c3b (TS2r, amended)", "undirected kick during pause: gate OR CI includes 1", f"ln OR(dose 1) {fmt(lu)} ± {fmt(1.96 * su)}",
                             "supported" if abs(lu) < 1.96 * su else "failed"))
        c2 = R["c"]["TS2"]
        if c2.get("ok"):
            pc = c2.get("per_class", {})
            dd = c2.get("dose_directed", {})
            lo = dd.get("lnOR", [None])[0]
            se = dd.get("se", [None])[0]
            if lo is not None and lo == lo:
                rows.append(("P-c3", "directed kick during pause: gate OR ≥ 1.5", f"OR(dose 1) {fmt(2.718281828 ** lo)} (ln {fmt(lo)} ± {fmt(1.96 * se)}); gates kicked {dd['n_gates'][1:]}",
                             "supported" if (lo >= 0.405 and lo - 1.96 * se > 0) else "failed"))
            if dd.get("powered"):
                rows.append(("P-c4", "dose law directed (TS2): not Kramers", f"best {dd['best']}; κ = {fmt(dd.get('kappa'))}", "supported" if dd["best"] in ("additive", "saturating") else "failed"))
    a2 = c1.get("A2_exact_time", {}) if c1.get("ok") else {}
    if a2:
        rows.append(("A2 (post hoc)", "exact-time kick model: directed / undirected ln HR vs null p95",
                     f"dir {fmt(a2['directed_lnHR'])} ± {fmt(1.96 * a2['directed_se'])} (null p95 {fmt(a2.get('null_directed_p95'))}); "
                     f"und {fmt(a2['undirected_lnHR'])} ± {fmt(1.96 * a2['undirected_se'])} (null p95 {fmt(a2.get('null_undirected_p95'))})", "sensitivity"))
    a3 = R.get("A3_outages", {})
    if a3.get("n"):
        d3 = (a3.get("TS1r") or {}).get("deep", {})
        rows.append(("A3 (post hoc)", "outage-censored TS1r deep slope", f"{a3['n']} outages ({fmt(a3['minutes'], 0)} min); β = {fmt(d3.get('beta_agentFE'))} Wald CI{ci(d3.get('ci_wald'))}", "sensitivity"))
    a4 = R["d"].get("A4_circ_no_stalls", {})
    if a4.get("ok"):
        rows.append(("A4 (post hoc)", "valley bimodality vs within-day circular-shift null", f"p = {fmt(a4['p_valley'])}", "sensitivity"))
    a5f = L.OUT / "A5_valley_minmass.json"
    if a5f.exists():
        a5 = json.loads(a5f.read_text()).get(R.get("label", ""), {})
        if a5:
            rows.append(("A5 (post hoc)", "valley with ≥ 5% mass per mode (stalls excl. / incl.)",
                         f"{fmt(a5['no_stalls']['valley_minmass'])} ({a5['no_stalls']['modes']} mode) / {fmt(a5['all']['valley_minmass'])} ({a5['all']['modes']} modes)", "sensitivity"))
    for key in ("TS3",):
        cl = R["c"][key]
        if cl.get("ok") and cl["directed_rows"] >= 30:
            rows.append(("P-c6", "directed kicks break error loops (HR > 1)", f"ln HR {fmt(cl['directed_lnHR'])} ± {fmt(1.96 * cl['directed_se'])} ({cl['directed_rows']} rows)",
                         "supported" if cl["directed_lnHR"] - 1.96 * cl["directed_se"] > 0 else ("failed" if cl["directed_lnHR"] <= 0 else "inconclusive")))
    d, dn = R["d"]["all"], R["d"]["no_stalls"]
    if d.get("ok"):
        rows.append(("P-d1", "βJ₀ < 1", f"βJ₀ = {fmt(dn['betaJ0'])} (stalls excl.; {fmt(d['betaJ0'])} incl.)", "supported" if dn["betaJ0"] < 1 else "failed"))
        rows.append(("P-d2", "no valley bimodality (stalls excl.)", f"p = {fmt(dn['p_valley'])} (incl.: {fmt(d['p_valley'])}); stall minutes {fmt(d['stall_frac'], 3)}",
                     "supported" if dn["p_valley"] > 0.05 else "failed"))
        rows.append(("P-d3", "no branch-memory excess", f"ACF30 {fmt(dn['acf_obs'])} vs null p95 {fmt(dn['acf_null_p95'])}", "supported" if dn["acf_obs"] <= dn["acf_null_p95"] else "failed"))
    return rows


def period_verdict(rows):
    core = [r for r in rows if r[0] in ("P-a1", "P-a2", "P-a4", "P-c1", "P-c2", "P-c2b", "P-c3", "P-d1", "P-d2")]
    # P-a4 / P-c3 fall back to the amended TS2r rows when strict TS2 has no chains
    ids = {r[0] for r in core if not r[3].startswith("n/a")}
    for amended, orig in (("P-a4 (TS2r, amended)", "P-a4"), ("P-c3 (TS2r, amended)", "P-c3")):
        if orig not in ids:
            core += [r for r in rows if r[0] == amended]
    s = sum(r[3].startswith("supported") for r in core)
    f = sum(r[3].startswith("failed") for r in core)
    if s + f == 0:
        return "descriptive"
    if f == 0:
        return "supported"
    if s == 0:
        return "failed"
    return "mixed"


def write_results():
    sys.path.insert(0, str(L.HDIR / "scheme"))
    from build import PERIODS  # noqa: E402
    summary = {}
    for p in INFO:
        rf = L.OUT / p / "results.json"
        f = L.HDIR / p / "README.md"
        if not rf.exists() or not f.exists():
            continue
        R = json.loads(rf.read_text())
        reg = PERIODS[p]["regime"]
        rows = score_period(R, reg)
        verdict = period_verdict(rows)
        txt = f.read_text()
        pred = re.search(r"## Prediction\n(.*?)\n## Result", txt, re.S).group(1)
        notes = txt.split("## Notes\n", 1)[1] if "## Notes\n" in txt else ""
        why = re.search(r"## Why this period\n(.*?)\n## Prediction", txt, re.S).group(1)
        a = R["a"]
        tab = "| Prediction | Statement | Observed | Verdict |\n| --- | --- | --- | --- |\n" + "\n".join(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} |" for r in rows)
        cnt = R["counts"]
        res = (f"Run {R.get('run_date', '2026-10-03')} with `analysis/run_period.py --period {p}`; numbers in "
               f"`data/processed/H16-metastable-traps-kramers/{p}/results.json`; figure `figures/period.pdf`.\n\n"
               f"Data: {R['n_days']} days, {R['n_agents']} agents; TS1 {cnt['ts1']} / TS1r {cnt['ts1r']} spells, TS2 {cnt['ts2_gates']} gates, "
               f"TS3 {cnt['ts3_rows']} and TS4 {cnt['ts4_rows']} loop-turn rows; kicks {cnt['kicks']}.\n\n" + tab +
               "\n\nPeriod verdict rule: core predictions (P-a1/a2, P-a4, P-c1/c2/c3, P-d1, P-d2): all supported → supported; none → failed; "
               "otherwise mixed. Underpowered rows are n/a.\n")
        if p == "G38" and "split_NE17" in R:
            sp = R["split_NE17"]
            res += "\n**NE17 split (sensitivity):** " + "; ".join(
                f"{k}: TS1r β = {fmt((v.get('TS1r') or {}).get('beta_agentFE'))}, TS2 β_lnk = {fmt((v.get('TS2') or {}).get('beta_lnk_agentFE'))}" for k, v in sp.items()) + "\n"
        sc = ("- **C (adequacy):** kick effects vs. the day-swap null and the memoryless null within agent (rows P-a*, P-c*).\n"
              "- **D (unfitted):** dwell-law shape and the swarm bimodality prediction from βJ₀ (P-d*).\n"
              "- **G (ground truth):** the regime difference in what ends idling (H09) is the known structure tested by P-c1/P-c2.\n")
        if p in NOTES and NOTES[p][:40] not in notes:
            notes = notes.rstrip("\n") + ("\n" if notes.strip() else "") + NOTES[p] + "\n"
        new = header(p, verdict) + f"\n## Why this period\n{why}\n## Prediction\n{pred}\n## Result\n{res}\n## Scorecard (period-specific axes)\n{sc}\n## Notes\n{notes}"
        f.write_text(new)
        summary[p] = {"verdict": verdict, "rows": rows}
        print(p, verdict)
    L.jdump(summary, L.OUT / "period_scores.json")


if __name__ == "__main__":
    if "--predictions" in sys.argv:
        write_predictions()
    if "--results" in sys.argv:
        write_results()
