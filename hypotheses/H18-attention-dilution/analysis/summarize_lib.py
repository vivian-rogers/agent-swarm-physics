"""Per-period verdicts and G-card sections for H18 (rules fixed in the G cards on 2026-10-03, before running)."""
from __future__ import annotations

import math

# Period-level P2 as written in the G cards (2026-10-03): "M_inv or M_sat best; if M_sat, k0 < 3".
BUDGET_LIKE = {"inv", "sat~inv"}
SATURATING = {"sat"}            # M_sat best with 3 <= k0 < k_q90: k-dependent but not a near-literal budget
CONST_LIKE = {"const", "sat~const", "rec~const"}


def ci(b, key="beta"):
    x = (b or {}).get(key) if isinstance(b, dict) else None
    return (x["lo"], x["hi"]) if x else (None, None)


def f2(x, nd=2):
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return "—"
    return f"{x:.{nd}f}"


def fci(v, lo, hi, nd=2):
    if v is None:
        return "—"
    s = f2(v, nd)
    if lo is not None and hi is not None:
        s += f" [{f2(lo, nd)}, {f2(hi, nd)}]"
    return s


def d1_checks(f):
    d1 = f["D1"]
    lo, hi = ci(d1["boot"])
    p1 = lo is not None and lo > 0
    cvb = d1.get("cv_block", {})
    eff = cvb.get("effective")
    p2 = eff in BUDGET_LIKE
    const_best = eff in CONST_LIKE
    rec_best = eff == "rec"
    return dict(p1=p1, p2=p2, const_best=const_best, rec_best=rec_best, beta=d1["beta"], lo=lo, hi=hi, eff=eff,
                ci_has0=(lo is not None and lo <= 0 <= hi))


def d2_check(f):
    d2 = f.get("D2") or {}
    if d2.get("n_units", 0) < 200 or "beta" not in d2:
        return dict(status="underpowered", beta=d2.get("beta"), lo=None, hi=None, n=d2.get("n_units", 0),
                    n_resp=d2.get("n_resp", 0))
    lo, hi = ci(d2.get("boot"))
    contradicts = d2["beta"] < 0.2
    return dict(status="contradicts" if contradicts else "consistent", beta=d2["beta"], lo=lo, hi=hi,
                n=d2["n_units"], n_resp=d2["n_resp"], excl0=(lo is not None and lo > 0))


def period_verdict(g, f):
    regime = (f.get("meta") or {}).get("regime", "")
    if f["D1"]["n_units"] < 300:
        return "descriptive"
    c = d1_checks(f)
    if c["ci_has0"] or c["const_best"]:
        return "failed"
    d2 = d2_check(f) if regime in ("III", "II/III") else dict(status="n/a")
    if c["p1"] and c["p2"] and d2["status"] in ("consistent", "underpowered", "n/a"):
        return "supported"
    return "mixed"


def result_section(g, f):
    d1 = f["D1"]
    c = d1_checks(f)
    cvb, cvd = d1.get("cv_block", {}), d1.get("cv_day", {})
    comp = cvb.get("comp", {})
    lines = []
    lines.append(f"*Run 2026-10-03 (`analysis/fit_periods.py --period {f['period']}`); data in "
                 f"`data/processed/H18-attention-dilution/{f['period']}/` (`fits.json`). Figure: `figures/curves.pdf`.*\n")
    lines.append(f"Sample: {f['n_days']} days, {f['n_agents']} recipients, {f['n_talks']} talk turns "
                 f"({f['n_talks_k1']} with k ≥ 1), {d1['n_units']} scored (talk, sender) units, {d1['n_resp']} addressed "
                 f"(rate {f2(d1['rate'], 3)}). k: median {f2(f['k_median'], 0)}, mean {f2(f['k_mean'], 1)}, q90 {f2(f['k_q90'], 0)}; "
                 f"mean room size {f2(f['n_room_mean'], 1)}.\n")
    lines.append("| Prediction | Observed | Null / rival | Verdict |")
    lines.append("| --- | --- | --- | --- |")
    lines.append(f"| P1 β̂ > 0, CI excl. 0 (expect 0.5–1.2) | β̂ = {fci(c['beta'], c['lo'], c['hi'])} | M_const: β = 0 | "
                 f"{'pass' if c['p1'] else 'fail'} |")
    mean = cvb.get("mean", {})
    best_s = (f"{cvb.get('best')} (effective: {cvb.get('effective')}; k̂₀ = {f2(cvb.get('k0'), 2)}, ρ̂ = {f2(cvb.get('rho'), 2)})"
              if cvb else "—")
    ivr = comp.get("inv_vs_rec")
    ivc = comp.get("inv_vs_const")
    lines.append(f"| P2 budget beats const and recency (within-day-block CV) | best {best_s}; Δℓ/unit inv − const "
                 f"{fci(*(ivc[:3] if ivc else (None, None, None)), nd=4)}, inv − rec {fci(*(ivr[:3] if ivr else (None, None, None)), nd=4)} | "
                 f"M_const, M_rec | {'pass' if c['p2'] else 'fail'} |")
    if cvd:
        lines.append(f"| (secondary) day-blocked CV, agent propensities | best {cvd.get('best')} ({cvd.get('effective')}) | | — |")
    eps = f.get("eps_S", {})
    eb = eps.get("boot") or {}
    lines.append(f"| P3 ε_S ∈ [−0.2, 0.5] | ε_S = {fci(eps.get('eps'), eb.get('lo'), eb.get('hi'))}; B̂ = {f2(f.get('B_hat'), 2)} senders addressed per talk | ε_S ≈ 1 (no budget) | "
                 f"{'pass' if eps.get('eps') is not None and -0.2 <= eps['eps'] <= 0.5 else 'fail'} |")
    bp = d1["fits"].get("bypass")
    bb = d1["boot"]
    if bp and d1["n_mention_units"] >= 100:
        bl, bh = ci(bb, "beta_byp")
        ml, mh = ci(bb, "betaM_byp")
        eg = math.exp(d1["gamma"])
        p4 = eg >= 3 and bp["params"]["betaM"] < bp["params"]["beta"] - 0.3
        lines.append(f"| P4 mentions: e^γ ≥ 3, β_M < β_other − 0.3 | e^γ = {f2(eg, 1)}; β_other = {fci(bp['params']['beta'], bl, bh)}, "
                     f"β_M = {fci(bp['params']['betaM'], ml, mh)} ({d1['n_mention_units']} mention units) | β_M = β_other | {'pass' if p4 else 'fail'} |")
    else:
        lines.append(f"| P4 mentions | {d1['n_mention_units']} mention units (< 100) | | n/a |")
    pl_ = f.get("placebo", {})
    inv, nonp, pend = pl_.get("invisible"), pl_.get("nonpending"), pl_.get("pending_same_talks")
    p10 = (inv is not None and nonp is not None and pend is not None and not math.isnan(inv)
           and inv <= max(1.5 * nonp, 1e-9) and inv <= 0.5 * pend) if inv is not None else None
    lines.append(f"| P10 invisible ≤ 1.5× non-pending, ≤ ½ pending | invisible {f2(inv, 3)} (n = {pl_.get('n_invisible')}), "
                 f"non-pending {f2(nonp, 3)}, pending (same talks) {f2(pend, 3)} | | {'pass' if p10 else ('fail' if p10 is False else 'n/a')} |")
    regime = (f.get("meta") or {}).get("regime", "")
    if regime in ("III", "II/III"):
        d2 = d2_check(f)
        st = f.get("D2_struct", {})
        if d2["status"] == "underpowered":
            lines.append(f"| P5 D2 timer wakes (300 s) | {d2['n']} units, {d2['n_resp']} responses | | underpowered |")
        else:
            w60, wst = f.get("D2w60") or {}, f.get("D2stint") or {}
            lines.append(f"| P5 D2 β̂ > 0, within ±0.4 of D1 | β̂_D2 = {fci(d2['beta'], d2['lo'], d2['hi'])} ({d2['n']} units, "
                         f"{d2['n_resp']} resp.; wakes talking within 300 s: {f2(st.get('talk300'), 2)}); 60 s: {f2(w60.get('beta'))}, "
                         f"stint: {f2(wst.get('beta'))} | reactive-constant agents: ≈ 0 | "
                         f"{'pass' if d2.get('excl0') and abs(d2['beta'] - c['beta']) <= 0.4 else ('contradicts' if d2['status'] == 'contradicts' else 'partial')} |")
    rm = f.get("rooms")
    if rm:
        ec, ep = rm.get("effect_const_ci") or {}, rm.get("effect_pow_ci") or {}
        p6 = (rm.get("median_p_ratio") or 0) > 1 and ep.get("lo") is not None and ep["lo"] <= 0 <= ep["hi"]
        lines.append(f"| P6 room size (same days) | k̄ ratio large/small {f2(rm.get('median_k_ratio'))}, p̄ ratio small/large "
                     f"{f2(rm.get('median_p_ratio'))}, S ratio {f2(rm.get('median_S_ratio'))}; room log-effect {fci(rm['effect_const'], ec.get('lo'), ec.get('hi'))} "
                     f"without k → {fci(rm['effect_pow'], ep.get('lo'), ep.get('hi'))} with k ({rm['n_days']} days) | room effect survives k | {'pass' if p6 else 'fail'} |")
    ct = f.get("content")
    if ct:
        lines.append(f"| P11 content-reply excess slope ≈ −β̂ (secondary) | overall excess {f2(ct['overall_excess'], 3)}; log-log slope "
                     f"{f2(ct.get('slope'))} | slope 0 | {'pass' if ct.get('slope') is not None and abs(ct['slope'] + c['beta']) <= 0.4 else 'fail'} |")
    sg = f.get("segments")
    if sg and sg.get("segments"):
        segs = [s for s in sg["segments"] if s.get("beta") is not None]
        po = sg.get("pooled")
        lines.append("")
        lines.append(f"Segments at step changes ({len(sg['segments'])}): " + "; ".join(
            f"{s['start']}–{s['end']}: β̂ {f2(s['beta'])}" + (f" ± {f2(s['beta_se'])}" if s.get('beta_se') else "") for s in segs)
                     + (f". Random-effects pooled {f2(po['mean'])} ± {f2(po['se'])}, I² = {f2(po['I2'])}." if po else "."))
    return "\n".join(lines) + "\n"


def scorecard_section(g, f):
    c = d1_checks(f)
    cvb = f["D1"].get("cv_block", {})
    regime = (f.get("meta") or {}).get("regime", "")
    lines = ["| Axis | Score | Evidence |", "| --- | --- | --- |"]
    C = 2 if (c["p2"] and (cvb.get("comp", {}).get("inv_vs_const", [0, 0])[1] or 0) > 0) else (1 if c["p1"] else 0)
    lines.append(f"| C adequacy | {C} | within-day-block CV: best {cvb.get('effective')}; inv − const Δℓ CI lower bound "
                 f"{f2((cvb.get('comp', {}).get('inv_vs_const') or [None, None])[1], 4)} |")
    H = 2 if (c["p2"] and (cvb.get("comp", {}).get("inv_vs_rec", [0, 0])[1] or 0) > 0) else (1 if c["p2"] else 0)
    lines.append(f"| H comparative | {H} | budget vs. recency: inv − rec Δℓ {f2((cvb.get('comp', {}).get('inv_vs_rec') or [None])[0], 4)} |")
    if regime in ("III", "II/III"):
        d2 = d2_check(f)
        lines.append(f"| B assumptions (timing) | {1 if d2['status'] == 'consistent' else 0} | D2 {d2['status']} (β̂_D2 {f2(d2.get('beta'))}) |")
    pl_ = f.get("placebo", {})
    lines.append(f"| G ground truth | {1 if (pl_.get('invisible') or 1) <= 0.5 * (pl_.get('pending_same_talks') or 0) else 0} | invisible-message placebo |")
    return "\n".join(lines) + "\n"


def notes_section(g, f, old):
    old = old.rstrip("\n")
    add = f"- 2026-10-03: results filled by `write_period_cards.py results` from `fits.json` (run time {f.get('secs')} s)."
    if add.split(" (run time")[0] in old:
        return old + "\n"
    return old + "\n" + add + "\n"
