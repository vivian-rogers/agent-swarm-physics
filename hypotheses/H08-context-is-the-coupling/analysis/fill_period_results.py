"""Fill Result / Scorecard / Verdict of the H08 period cards from the JSON outputs (called by write_period_cards.py
results). The verdict rule is the one fixed in each card's Prediction section; nothing here is tuned after the fact.
Also writes data/processed/H08-context-is-the-coupling/period_table.json (for the main card)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h08lib import *  # noqa: E402,F403

FAM = {"imm": ["imm", "imm_hr"], "delay": ["delay", "delay_hr"], "hawkes": ["hawkes"]}


def load(p):
    p = OUT / p
    return json.loads(p.read_text()) if p.exists() else None


def f(x, k=3):
    if x is None:
        return "—"
    if isinstance(x, (list, tuple)):
        if len(x) == 3 and all(v is not None for v in x):
            return f"{x[0]:.{k}f} [{x[1]:.{k}f}, {x[2]:.{k}f}]"
        return "—"
    return f"{x:.{k}f}"


def pp(x):
    return f"{100 * x[0]:+.2f} [{100 * x[1]:+.2f}, {100 * x[2]:+.2f}]" if x and None not in x else "—"


def t_c9(d):
    p = d.get("primary", {})
    if "talk" not in p:
        return "n/a", {}
    v1 = p["talk"]["D"][1] > 0
    v2 = p["addr"]["D"][1] > 0
    floor = p["addr"]["G"]["0"][0]; top = p["addr"]["G"]["1"][0]
    return ("pass" if (v1 and v2) else "fail"), {"V1": v1, "V2": v2, "floor_ok": (floor > 0) and (floor < 0.5 * top),
                                                 "V4": p["talk"]["G"]["2"][0] < p["talk"]["G"]["1"][0]}


def t_c8(d):
    s = (d or {}).get("sets", {}).get("nudge_target_iso", {})
    if not s or s.get("n_cells", 0) < 30 or "shape" not in s:
        return "n/a (< 30 cells)", {}
    diff = s["shape"]["phi_1_5_diff_hr"]
    band = diff[2] >= -0.3 and diff[1] <= 0.1
    cv = s.get("cv", {})
    w = cv.get("ctx_wins_share", {})
    fam_win = {k: min(w.get(m, 0) for m in ms) for k, ms in FAM.items()}
    p3 = all(v >= 0.6 for v in fam_win.values()) and cv.get("ratio_to_ctx", {}).get("gamma", 0) >= 1 / 1.1
    rival_fail = any((1 - v) >= 0.6 for v in fam_win.values())
    out = "pass" if (band and p3) else ("fail" if (not band or rival_fail) else "inconclusive")
    return out, {"band": band, "P3": p3, "fam_win": fam_win, "rival_fail": rival_fail}


def t_c3(d):
    if not d or "beta" not in d:
        return "n/a", {}
    if d.get("n_erased", {}).get("CF", 0) < 300:
        return "n/a (< 300 forced-erased units)", {}
    b = d["beta"]["erased_F"]
    return ("pass" if b[2] < 0 else ("fail" if b[1] > 0 else "inconclusive")), {}


def t_c1(g, d):
    r = (d or {}).get("periods", {}).get(gname(g))
    if not r or not r.get("n_fetches"):
        return "n/a (no fetches)", {}
    rec = r["recall"]; oth = r.get("other_room_coverage")
    two = g in TWO_ROOM
    if rec >= 0.9 and (not two or (oth is not None and oth <= 0.05)):
        return "pass", {}
    if rec < 0.7 or (two and oth is not None and oth > 0.2):
        return "fail", {}
    return "partial", {}


def verdict(tests):
    c9 = tests["C9"]
    if c9 != "pass":
        return "failed"
    others = [v for k, v in tests.items() if k != "C9"]
    return "mixed" if any(v == "fail" for v in others) else "supported"


def result_md(g, applies):
    a = applies(g)
    c9, c8, c3, c2, c10 = (load(f"{gname(g)}/{x}.json") for x in ("c9", "c8", "c3", "c2", "c10"))
    c1 = load("cc/c1.json")
    tests = {}
    rows = []
    T, info = t_c9(c9)
    tests["C9"] = T
    p = c9["primary"]
    rows.append(f"| C9-V1 talk jump D_talk (pp) | {pp(p['talk']['D'])} | pseudo-message null | {'pass' if info['V1'] else 'fail'} |")
    rows.append(f"| C9-V2 addressing jump D_addr (pp) | {pp(p['addr']['D'])}; floor G_addr(0) {100 * p['addr']['G']['0'][0]:+.2f}, "
                f"G_addr(1) {100 * p['addr']['G']['1'][0]:+.2f} | | {'pass' if info['V2'] else 'fail'}"
                f"{'' if info['floor_ok'] else ' (floor clause fails)'} |")
    rows.append(f"| A6 pre = G(0) − G(−1), talk / addr (pp) | {pp(p['talk']['pre'])} / {pp(p['addr']['pre'])} | ≈ 0 (common cause is flat) | "
                f"{'ok' if (p['talk']['pre'][1] <= 0 <= p['talk']['pre'][2]) else 'not ≈ 0'} |")
    rows.append(f"| C9-V4 G_talk(2) < G_talk(1) | {100 * p['talk']['G']['2'][0]:+.2f} vs {100 * p['talk']['G']['1'][0]:+.2f} | | {'pass' if info['V4'] else 'fail'} |")
    ph = c9.get("posthoc_clean", {})
    if "talk" in ph:
        rows.append(f"| *post hoc:* recipient did not talk at o = −2, −1 | D_talk {pp(ph['talk']['D'])}; D_addr {pp(ph['addr']['D'])}; "
                    f"G_addr(0) {100 * ph['addr']['G']['0'][0]:+.2f} | | (descriptive) |")
    if "other_room" in c9 and "talk" in c9["other_room"]:
        o = c9["other_room"]
        okv3 = all(abs(o[k]["D"][0]) < abs(p[k]["D"][0]) / 3 and o[k]["D"][1] <= 0 <= o[k]["D"][2] for k in ("talk", "addr"))
        rows.append(f"| C9-V3 other-room placebo D_talk / D_addr (pp) | {pp(o['talk']['D'])} / {pp(o['addr']['D'])} | ≈ 0 | {'pass' if okv3 else 'fail'} |")
    if a["C2"] or PERIODS[g]["regime"] == "III":
        w = c9["W_active_s"]
        rows.append(f"| C9-V5 median read-out delay, active recipients | {w[1]:.0f} s (IQR {w[0]:.0f}–{w[2]:.0f}) | 10–40 s | {'pass' if 10 <= w[1] <= 40 else 'fail'} |")
    else:
        w = c9["W_active_s"]
        rows.append(f"| read-out delay, active recipients (descriptive) | median {w[1]:.0f} s (IQR {w[0]:.0f}–{w[2]:.0f}) | | — |")
    if a["C8"]:
        T8, i8 = t_c8(c8)
        tests["C8"] = T8 if not T8.startswith("n/a") else "n/a"
        s = (c8 or {}).get("sets", {}).get("nudge_target_iso", {})
        if "shape" in s:
            sh = s["shape"]
            rows.append(f"| C8 nudge → target, cells | {s['n_cells']}; A30 {f(sh['A30'], 2)}; read-out median "
                        f"{s['readout']['W_obs_s_q'][2]:.0f} s; paused at kick {100 * s['readout']['paused_share']:.0f}% | | {T8} |")
            rows.append(f"| C8-P1 Φ(1,5) measured vs F_hr | {f(sh['phi_1_5'], 2)} vs {f(sh['phi_1_5_pred_hr'], 2)}; diff {f(sh['phi_1_5_diff_hr'], 2)} | "
                        f"band [−0.3, +0.1] | {'consistent' if i8.get('band') else ('inconsistent' if i8 else 'descriptive')} |")
            rows.append(f"| C8-P2 t½ of F_hr | {sh.get('t_half_hr')} min | 3–15 min | {'pass' if sh.get('t_half_hr') and 3 <= sh['t_half_hr'] <= 15 else 'fail'} |")
            rows.append(f"| C8-P4 Φ_ren(1,5) > Φ_obs(1,5) | {sh['phi_1_5_pred_hr_ren'][0]:.2f} vs {sh['phi_1_5_pred_hr'][0]:.2f} | | "
                        f"{'pass' if sh['phi_1_5_pred_hr_ren'][0] > sh['phi_1_5_pred_hr'][0] else 'fail'} |")
            cv = s.get("cv", {})
            if cv.get("best_share"):
                best = ", ".join(f"{k} {v:.2f}" for k, v in sorted(cv["best_share"].items(), key=lambda x: -x[1])[:3])
                fw = i8.get("fam_win") or {}
                rows.append(f"| C8-P3 day-split CV (100 splits) | best: {best}; ctx beats imm {fw.get('imm', 0):.2f}, delay {fw.get('delay', 0):.2f}, "
                            f"Hawkes {fw.get('hawkes', 0):.2f}; gamma/ctx SSE {cv['ratio_to_ctx'].get('gamma', float('nan')):.2f} | ≥ 0.60 each | "
                            f"{'pass' if i8.get('P3') else 'fail'} |")
            pm = (c8 or {}).get("pause_matched", {})
            if g == 51 and pm.get("early_diff_notpaused_minus_paused"):
                rows.append(f"| C8-P5 early response, not paused − paused ≥ 5 min | {f(pm['early_diff_notpaused_minus_paused'], 3)} "
                            f"(n = {pm['not_paused']['n_cells']} / {pm['paused_ge5min']['n_cells']}) | > 0 | "
                            f"{'pass' if pm['early_diff_notpaused_minus_paused'][1] > 0 else 'fail'} |")
        else:
            rows.append(f"| C8 nudge → target | {s.get('n_cells', 0)} isolated cells | | descriptive (pooled) |")
    if a["C1"]:
        T1, _ = t_c1(g, c1)
        tests["C1"] = T1 if not T1.startswith("n/a") else "n/a"
        r = (c1 or {}).get("periods", {}).get(gname(g), {})
        if r.get("n_fetches"):
            rows.append(f"| C1 room rule recall / precision | {r['recall']:.3f} / {r['precision']:.3f} ({r['n_seen']} events seen, "
                        f"{r['n_fetches']} fetches) | recall ≥ 0.9 | {T1} |")
            rows.append(f"| C1 history replay share (> 1 day old) | {100 * (r.get('replay_share') or 0):.0f}%; recall on the current feed "
                        f"{f(r.get('recall_current_feed'))} | | — |")
            if r.get("other_room_coverage") is not None:
                rows.append(f"| C1 other-room coverage | {100 * r['other_room_coverage']:.1f}% | ≤ 5% | "
                            f"{'pass' if r['other_room_coverage'] <= 0.05 else 'fail'} |")
            if r.get("delay_s"):
                rows.append(f"| C1 delay (current feed) | median {r['delay_s']['50']:.0f} s, 90th {r['delay_s']['90']:.0f} s | minutes | "
                            f"{'pass' if r['delay_s']['50'] >= 60 else 'fail'} |")
            cov = r.get("coverage_by_type_own_room", {})
            if cov:
                vals = [v["coverage"] for v in cov.values() if v["n"] >= 30]
                rows.append(f"| C1 coverage by type (n ≥ 30) | {min(vals):.2f}–{max(vals):.2f} (WAIT "
                            f"{cov.get('WAIT', {}).get('coverage', float('nan')):.2f}, talk {cov.get('AGENT_TALK', {}).get('coverage', float('nan')):.2f}) | "
                            f"WAIT/PAUSE invisible | {'fail' if cov.get('WAIT', {}).get('coverage', 0) > 0.2 else 'pass'} |")
        else:
            rows.append("| C1 | no fetches by the Claude Code agent in this period | | n/a |")
    if a["C2"] and c2:
        rows.append(f"| C2-I1 elasticity b (raw) / partial R² | {f(c2.get('slope_b'), 2)} / {f(c2.get('partial_R2'), 3)} | b > 0, R² < 0.05 | "
                    f"{'pass' if c2.get('slope_b', [0, -1, 0])[1] > 0 and c2['partial_R2'][0] < 0.05 else 'fail'} |")
        if c2.get("posthoc_slope_b_prevaction"):
            rows.append(f"| *post hoc:* b with previous-action control | {f(c2['posthoc_slope_b_prevaction'], 2)} | | (descriptive) |")
        rows.append(f"| C2-I2 talk ratio / ρ(uncached, latency) | {f(c2.get('talk_ratio'), 2)} / {f(c2.get('rho_unc_latency'), 2)} | > 1.2 / > 0 | "
                    f"{'pass' if c2['talk_ratio'][0] > 1.2 and c2.get('rho_unc_latency', [0, 0, 0])[1] > 0 else 'partial'} |")
    if a["C3"] and c3:
        T3, _ = t_c3(c3)
        tests["C3"] = T3 if not T3.startswith("n/a") else "n/a"
        if "beta" in c3:
            rows.append(f"| C3-E1 β_F (forced erasure, pp) / relative | {pp(c3['beta']['erased_F'])} / {f(c3.get('rel_F'), 2)} "
                        f"(CF units {c3['n_erased'].get('CF', 0)}) | < 0; rel ≤ −0.30 | {T3} |")
            rows.append(f"| C3-E2 β_V (pp) | {pp(c3['beta']['erased_V'])} | within ±50% of β_F | "
                        f"{'pass' if abs(c3['beta']['erased_V'][0] - c3['beta']['erased_F'][0]) <= 0.5 * abs(c3['beta']['erased_F'][0]) else 'fail'} |")
        if c3.get("eos_rho_voluntary") is not None:
            ci_ = c3.get("eos_rho_voluntary_ci")
            rows.append(f"| C3-E3 ρ(voluntary segment length, inflow per turn) | {f(ci_, 2) if ci_ else f(c3['eos_rho_voluntary'], 2)} "
                        f"(n = {c3['eos_n_voluntary']}) | < 0 | {'pass' if c3['eos_rho_voluntary'] < 0 else 'fail'} |")
    if a["C10"] and c10:
        rows.append(f"| C10-L1 slope of log(1 + k) per session hour / ρ | {f(c10['slope_logk_per_hour'], 3)} / {c10['rho_k_hour']:+.3f} | > 0 | "
                    f"{'pass' if c10['slope_logk_per_hour'][1] > 0 and c10['rho_k_hour'] > 0 else 'fail'} |")
        hk = load("c10_hawkes.json")
        if hk and gname(g) in hk.get("halves", {}):
            h = hk["halves"][gname(g)]
            rows.append(f"| C10-L2 Hawkes n̂ second − first half | {h['n_second']:.3f} − {h['n_first']:.3f} = {f(h['delta_n'], 3)} | > 0 | "
                        f"{'pass' if h['delta_n'][1] > 0 else 'fail'} |")
        if g == 51 and hk and hk.get("weeks_51", {}).get("rho_n_k") is not None:
            rows.append(f"| C10-L3 weeks: ρ(n̂, mean k) | {hk['weeks_51']['rho_n_k']:+.2f} ({hk['weeks_51']['n_weeks']} weeks) | > 0 | "
                        f"{'pass' if hk['weeks_51']['rho_n_k'] > 0 else 'fail'} |")
    v = verdict(tests)
    hdr = (f"*Run 2026-10-04 (`analysis/visibility.py`, `kernels.py`, `cc_exposure.py`, `inflow.py`, `erasure.py`, `sessions.py`). "
           f"Data: `data/processed/H08-context-is-the-coupling/{gname(g)}/` (c9/c8/c2/c3/c10.json). Figure: `figures/c9_offsets.pdf`. "
           f"pp = percentage points; brackets are day-bootstrap 95% CIs.*\n\n"
           f"Read-out pairs: {c9['n_pairs_own']} own-room (+ {c9['n_pairs_other']} other-room); in-flight share "
           f"{100 * c9['share_inflight']:.0f}%, wake share {100 * c9['share_wake']:.0f}%.\n\n"
           "| Prediction | Observed | Null / rival | Verdict |\n| --- | --- | --- | --- |\n")
    tests_line = "\n\n**Tests:** " + ", ".join(f"T_{k} = {val}" for k, val in tests.items()) + f" → **{v}**."
    return hdr + "\n".join(rows) + tests_line, v, tests


def score_md(g, tests):
    lines = ["| Axis | This period |", "| --- | --- |"]
    lines.append(f"| C adequacy | C9 discontinuity vs pseudo-message null: {tests['C9']}"
                 + (f"; C8 CV vs rivals: {tests.get('C8')}" if tests.get("C8") not in (None, "n/a") else "") + " |")
    if "C1" in tests and tests["C1"] != "n/a":
        lines.append(f"| G ground truth | Claude Code fetch log vs room rule: {tests['C1']} |")
    if "C3" in tests and tests["C3"] != "n/a":
        lines.append(f"| E interventional | NE41 forced erasure (exogenous timing): {tests['C3']} |")
    lines.append("| D unfitted | read-out turn and the zero-parameter kernel come from turn timing only |")
    return "\n".join(lines)


def main(card, ne41_card, applies):
    table = {}
    for g in sorted(PERIODS):
        md, v, tests = result_md(g, applies)
        card(g, result_md=md, verdict=v, score_md=score_md(g, tests))
        table[gname(g)] = {"verdict": v, "tests": tests}
    # NE41
    d = load("ne41_pooled.json")
    pz = d["pooled"]
    rows = ["| Period | forced-erased units | β_F (pp) | relative | β_V (pp) | ρ E3 |", "| --- | --- | --- | --- | --- | --- |"]
    for g, r in d["periods"].items():
        if "beta" in r:
            rows.append(f"| {g} | {r['n_erased'].get('CF', 0)} | {pp(r['beta']['erased_F'])} | {f(r.get('rel_F'), 2)} | "
                        f"{pp(r['beta']['erased_V'])} | {r.get('eos_rho_voluntary', float('nan')):+.2f} |")
    bf, rf, bv = pz["erased_F"], pz["rel_F"], pz["erased_V"]
    lo, hi = bf["mu"] - 1.96 * bf["se"], bf["mu"] + 1.96 * bf["se"]
    rel_ok = rf["mu"] <= -0.30
    v = "supported" if (hi < 0 and rel_ok) else ("failed" if hi >= 0 else "mixed")
    neg_eos = sum(1 for r in d["periods"].values() if r.get("eos_rho_voluntary", 1) < 0)
    md = ("*Run 2026-10-04 (`analysis/erasure.py`). Linear probability model with agent×day effects, 5 age bins, engaged flag, "
          "post-consolidation turn and new-sender indicators; day-bootstrap CIs; random-effects pooling.*\n\n" + "\n".join(rows) +
          f"\n\n| Prediction | Observed | Verdict |\n| --- | --- | --- |\n"
          f"| E1 pooled β_F < 0, relative drop ≥ 30% | β_F = {100 * bf['mu']:+.2f} pp [{100 * lo:+.2f}, {100 * hi:+.2f}] (k = {bf['k']}, I² = {bf['I2']:.2f}); "
          f"relative {100 * rf['mu']:+.0f}% ± {100 * 1.96 * rf['se']:.0f}%; CI excludes 0 in "
          f"{sum(1 for r in d['periods'].values() if 'beta' in r and r['beta']['erased_F'][2] < 0)}/{len(d['periods'])} periods | "
          f"{'pass' if hi < 0 and rel_ok else ('sign only' if hi < 0 else 'fail')} |\n"
          f"| E2 β_V within ±50% of β_F | β_V = {100 * bv['mu']:+.2f} ± {100 * 1.96 * bv['se']:.2f} pp | "
          f"{'pass' if abs(bv['mu'] - bf['mu']) <= 0.5 * abs(bf['mu']) else 'fail'} |\n"
          f"| E3 ρ < 0 in ≥ 2/3 of periods | {neg_eos}/{len(d['periods'])} | {'pass' if neg_eos >= 2 / 3 * len(d['periods']) else 'fail'} |")
    ne41_card(result_md=md + f"\n\n**Verdict: {v}** (rule fixed in Prediction). Figure: `figures/ne41.pdf`.", verdict=v,
              score_md="| Axis | |\n| --- | --- |\n| E interventional | forced erasures at the scaffold's 41-turn cap: exogenous timing; "
                       f"pooled β_F {100 * bf['mu']:+.2f} pp |\n| H comparative | memory-mediated coupling (β_F ≈ 0) rejected; restart overhead absorbed by PC and the new-sender contrast |")
    table["NE41"] = {"verdict": v}
    jdump(table, OUT / "period_table.json")
    print(json.dumps({k: v["verdict"] for k, v in table.items()}, indent=0))
