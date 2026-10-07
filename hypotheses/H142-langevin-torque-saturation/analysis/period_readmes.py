"""Fill the Result and Scorecard sections of the H142 period folders from results/*.json (round 1).
Usage: uv run python hypotheses/H142-langevin-torque-saturation/analysis/period_readmes.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
CARD = HERE.parent
RES = HERE.parents[2] / "data/processed/H142-langevin-torque-saturation/results"
SH = {"bge_small": "bge", "gte_modernbert": "gte"}
VMAP = {"supported": "supported", "failed": "failed", "narrowed": "mixed", "inconclusive": "mixed", "descriptive": "descriptive"}


def f3(x):
    return "—" if x is None else f"{x:.3f}"


def model_block(r: dict, m: str) -> list[str]:
    d = r["dll_langevin_linear"]; dp = r["dll_langevin_power"]; pl_ = r["dll_power_linear"]
    fd, fp = r["dummies"], r["profiles"]
    f = fd["f"]
    curve = ", ".join(f"f̂({k[1:].replace('_', '–').replace('p', '+')}) {v['est']:.4f} [{v['lo']:.4f}, {v['hi']:.4f}]" for k, v in f.items())
    dc = fd["dcurv"]
    dcs = f"{dc['est']:.2f} [{f3(dc.get('lo'))}, {f3(dc.get('hi'))}]" if dc.get("est") is not None else "undefined (a bin ≤ 0)"
    lg = fp["langevin"]
    inf = fd.get("inflight") or {}
    rules = r["rules"]
    pa = r.get("pooled_amplitude", {}).get("dll_langevin_linear", {})
    lines = [f"- **{SH[m]}** ({r['n_rows']:,} rows, {r['n_ge4']:,} with n_u ≥ 4, {r['n_days']} days; power vs W-L3 "
             f"{r.get('power_WL3') if r.get('power_WL3') is not None else '—'}; scored: {'yes' if r.get('scored') else 'no'}).",
             f"  - O1 step curve: {curve}.",
             f"  - O2 Δ_curv {dcs}. f̂(6+)/f̂(3) {f3((fd.get('ratio63') or {}).get('est'))} [{f3((fd.get('ratio63') or {}).get('lo'))}, {f3((fd.get('ratio63') or {}).get('hi'))}].",
             f"  - O3 out of fold (A1 form): ΔLL(L − line) {d['dll']:.1f} [{d['lo']:.1f}, {d['hi']:.1f}] nats; ΔLL(L − power) {dp['dll']:.1f} "
             f"[{dp['lo']:.1f}, {dp['hi']:.1f}]; ΔLL(power − line) {pl_['dll']:.1f} [{pl_['lo']:.1f}, {pl_['hi']:.1f}]. "
             f"Card's pooled-amplitude form: ΔLL(L − line) {pa.get('dll', float('nan')):.1f} [{pa.get('lo', float('nan')):.1f}, {pa.get('hi', float('nan')):.1f}].",
             f"  - Fits: ĉ {lg['theta']:.3f} [{f3(lg.get('theta_lo'))}, {f3(lg.get('theta_hi'))}], n̂_sat {lg['nsat']:.2f} [{f3(lg.get('nsat_lo'))}, {f3(lg.get('nsat_hi'))}] "
             f"(grid-edge share {lg.get('edge_share', 0):.2f}); power p̂ {fp['power']['theta']:.2f} [{f3(fp['power'].get('theta_lo'))}, {f3(fp['power'].get('theta_hi'))}].",
             f"  - Nuisance pulls: newest item {fd['nuis']['newest']['est']:.4f} [{fd['nuis']['newest']['lo']:.4f}, {fd['nuis']['newest']['hi']:.4f}]; "
             f"named count {fd['nuis'].get('nname', {}).get('est', float('nan')):.4f} [{fd['nuis'].get('nname', {}).get('lo', float('nan')):.4f}, {fd['nuis'].get('nname', {}).get('hi', float('nan')):.4f}] per aligned named item.",
             f"  - O4: ĝ(1) {f3(inf.get('g1'))} [{f3(inf.get('g1_lo'))}, {f3(inf.get('g1_hi'))}], ĝ(1)/f̂(1) "
             f"{f3(inf.get('ratio')) if f['n1']['lo'] > 0 else 'undefined (f̂(1) CI includes 0)'}, read − in-flight at n = 1 "
             f"{f3(inf.get('contrast'))} [{f3(inf.get('contrast_lo'))}, {f3(inf.get('contrast_hi'))}]. O5: largest n with ≥ 50 rows {r['n_max_50']}.",
             f"  - Rules: P1 {'pass' if rules['P1'] else 'fail'}, P2 {'pass' if rules['P2'] else 'fail'}, P3 {'pass' if rules['P3'] else 'fail'}, "
             f"P4 {'pass' if rules['P4'] else 'fail'}; kill (linear curve) {rules['kill_linear_curve']}, kill (line as good) {rules['kill_line_as_good']}"
             f"{'' if r.get('scored') else ' (not applied: unscored)'}; verdict by the card's rule: **{rules['verdict']}**."]
    for key, lab in (("sens_K12", "K = 12"), ("sens_noflag", "copies and templates removed")):
        if key in r:
            s = r[key]; dd = s["dll_langevin_linear"]
            lines.append(f"  - Sensitivity ({lab}): ΔLL(L − line) {dd['dll']:.1f} [{dd['lo']:.1f}, {dd['hi']:.1f}], Δ_curv "
                         f"{f3(s['dcurv'].get('est'))} [{f3(s['dcurv'].get('lo'))}, {f3(s['dcurv'].get('hi'))}], n̂_sat {s['nsat']:.2f}.")
    return lines


def write(folder: Path, verdict: str, body: list[str], score: str):
    p = folder / "README.md"
    s = p.read_text()
    s = re.sub(r"\*\*Verdict:\*\* .*", f"**Verdict:** {verdict}", s, count=1)
    s = re.sub(r"## Result\n.*?(?=\n## )", "## Result\n" + "\n".join(body) + "\n", s, count=1, flags=re.S)
    s = re.sub(r"## Scorecard \(period-specific axes\)\n.*?(?=\n## |\Z)", "## Scorecard (period-specific axes)\n" + score + "\n", s, count=1, flags=re.S)
    p.write_text(s)


def main():
    per = json.loads((RES / "periods.json").read_text())
    nat = json.loads((RES / "natives.json").read_text())
    nulls = json.loads((RES / "nulls.json").read_text())
    for key, p in per.items():
        g = int(key[1:])
        folder = CARD / "goalperiod-subhypotheses" / f"G{g:02d}"
        if not folder.exists():
            continue
        body = ["*Round 1, 2026-10-07 (exploratory). Amendments A1–A4 in the card apply. Figure: `figures/step_curve.pdf`.*"]
        vs = []
        for m in ("bge_small", "gte_modernbert"):
            if m in p:
                body += model_block(p[m], m)
                vs.append(p[m]["rules"]["verdict"])
            nk = f"G{g}|{m}"
            if nk in nulls:
                n = nulls[nk]
                body.append(f"  - Within room × hour permutation null ({n['perms']} perms, {SH[m]}): ΔLL(L − line) 2.5/50/97.5% "
                            f"{', '.join(f'{x:.1f}' for x in n['dll_L_lin_q'])}; f̂(1) {', '.join(f'{x:.4f}' for x in n.get('f_n1_q', [0, 0, 0]))}.")
        if g == 51:
            for m in ("bge_small", "gte_modernbert"):
                w = nat.get(f"G51_wakes|{m}")
                if w:
                    body.append(f"- **N1 timer wakes ({SH[m]})**:")
                    blk = model_block(dict(w, scored=True, rules={"P1": False, "P2": False, "P3": False, "P4": False, "kill_linear_curve": False, "kill_line_as_good": False, "verdict": "n/a"}), m)[1:]
                    body += ["  " + x for x in blk if "Rules:" not in x]
                    n1 = w["N1"]
                    body.append(f"  - N1: ΔLL CI > 0: {n1['dll_ci_gt0']}; n̂_sat(wakes)/n̂_sat(talk) {n1['nsat_ratio_wake_talk']:.2f} "
                                f"(ln ratio CI [{n1['ln_ratio_lo']:.2f}, {n1['ln_ratio_hi']:.2f}]); within ×1.5: {n1['within_x1_5']}; **N1 {'pass' if n1['pass'] else 'fail'}**.")
        scored = [v for m, v in zip(("bge_small", "gte_modernbert"), vs) if p.get(m, {}).get("scored")]
        if scored:
            v = scored[0] if len(set(scored)) == 1 else "mixed"
        else:
            v = "descriptive"
        ph = json.loads((RES / "posthoc.json").read_text()) if (RES / "posthoc.json").exists() else {}
        for kk, x in ph.items():
            gg, mm, var = kk.split("|")
            if gg == f"G{g}" and var != "card":
                body.append(f"- *Post hoc* ({SH[mm]}, {var}): f̂(1) {x['f']['n1'][0]:.4f} [{x['f']['n1'][1]:.4f}, {x['f']['n1'][2]:.4f}], "
                            f"newest {x['newest'][0]:.4f}, ΔLL(L − line) {x['dll_L_lin'][0]:.1f} [{x['dll_L_lin'][1]:.1f}, {x['dll_L_lin'][2]:.1f}].")
        sc = ("C 0 (the Langevin form does not beat the line out of fold); D 0 (no unfitted signature: Δ_curv undefined); "
              "F 2 (power vs W-L3 ≥ 0.8 on this skeleton; W-lin size ≤ 0.12); H 0 (does not beat the line or the power law)."
              if scored else "Descriptive (not scored: H113 identification, the 200-row count or power < 0.8). C, D, F, H: 0.")
        write(folder, VMAP.get(v, v), body, sc)
    # NE42
    folder = CARD / "goalperiod-subhypotheses/NE42"
    body = ["*Round 1, 2026-10-07 (exploratory). Descriptive by the folder's own rule: #40 is not field-identified by H113, and no NE42 side has power ≥ 0.8 (after A4: bge #39 0.47, #40 0.62, #41 0.63; gte 0.64, 0.70, 0.68). n̂_sat sits on a grid edge (0.1 or 150) on most sides, so no side has an identified saturation scale.*"]
    for m in ("bge_small", "gte_modernbert"):
        ne = nat.get(f"NE42|{m}")
        if not ne:
            continue
        km = ne["k_mean"]
        body.append(f"- **{SH[m]}**: mean ledger k {km['39']:.1f} (#39) → {km['40']:.1f} (#40) → {km['41']:.1f} (#41).")
        for t in ("39->40", "40->41"):
            x = ne[t]
            body.append(f"  - {t.replace('->', ' → ')}: n̂_sat {x['nsat_before']:.2f} → {x['nsat_after']:.2f}; Δ ln n̂_sat {x['dln']:.2f} [{x['lo']:.2f}, {x['hi']:.2f}]; "
                        f"|Δ| < ln 1.5: {x['within_ln1_5']}; counts against: {x['against']}.")
    write(folder, "descriptive", body, "E: 0 (descriptive; unpowered sides).")


if __name__ == "__main__":
    main()
