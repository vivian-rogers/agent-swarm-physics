"""Render markdown result tables from the H10 JSON outputs (to paste into the card and period READMEs).

Usage: uv run python report.py > <scratch>/tables.md
"""
from __future__ import annotations

import json

import numpy as np

from h10data import DATA

PAIR_LABEL = {"11-12": "#11 → #12a", "16-17": "#16 → #17", "37-38": "#37 → #38a", "3-4": "#3 → #4a", "5-6": "#5 → #6a"}


def f(x, d=2):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "–"
    return f"{x:.{d}f}"


def ci(c, d=2):
    if not c or not all(np.isfinite(c)):
        return "–"
    return f"[{c[0]:.{d}f}, {c[1]:.{d}f}]"


def main():
    P = json.loads((DATA / "NE34/pairs.json").read_text())
    print("## Pair table\n")
    print("| Pair | N | windows F/A | Δ̄ | λ | ε | P1 r (perm p) | LOAO MSE tilt/transl | P2 ρ [90% CI] | ρ_Gauss | ρ⊥ | g_F → g_A | Δg [90% CI] | P4 D [90% CI] | verdicts P1 / P2 / P3 / P4 → pair |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for k, r in P["pairs"].items():
        print(f"| {PAIR_LABEL[k]}{'' if r['primary'] else ' (secondary)'} | {r['N']} | {r['n_win_F']}/{r['n_win_A']} | {f(r['Dbar'], 3)} | "
              f"{f(r['lam'], 1)} | {f(r['eps'])} | {f(r['P1_r'])} ({f(r['P1_p'], 3)}) | {f(r['P1_mse_tilt'] / r['P1_mse_trans'])} | "
              f"{f(r['P2_rho'])} {ci(r.get('P2_rho_ci90'))} | {f(r.get('P2_rho_gauss'))} | {f(r['P2_rho_perp'])} | "
              f"{f(r.get('gF'))} → {f(r.get('gA'))} | {f(r.get('dg'))} {ci(r.get('dg_ci90'))} | {f(r.get('P4_D'), 3)} {ci(r.get('P4_D_ci90'), 3)} | "
              f"{r['v1']} / {r['v2']} / {r['v3']} / {r['v4']} → **{r['v']}** |")
    print("\nCombined:", P["combined"], "\n")
    for k, r in P["pairs"].items():
        print(f"### {PAIR_LABEL[k]} extras: R2 slope on μ_F (cross-split) {f(r.get('R2_slope_muF'))}, r(κ2 odd, Δ even) "
              f"{f(r.get('R2_r_k2_cross'))}; γ_F {f(r['gammaF'])} → γ_A {f(r['gammaA'])}; κ3 pred/obs {f(r['P2_k3_pred'], 5)}/"
              f"{f(r['P2_k3_obs'], 5)}; swarm P2 ρ {f(r.get('P2swarm_rho'))} {ci(r.get('P2swarm_rho_ci90'))}; ρ̄ F→A "
              f"{f(r.get('rhobar_F'))} → {f(r.get('rhobar_A'))}; P4 cos ĝ {f(r.get('P4_cos_g'))}, Ĉĝ {f(r.get('P4_cos_Cg'))}, "
              f"raw Ĉĝ {f(r.get('P4_cos_Cg_raw'))}, α {f(r.get('P4_alpha'))}, rot p95 {f(r.get('P4_rot_p95'))}, placebo "
              f"{[round(x, 2) for x in (r.get('P4_cos_Cplacebo') or [])]}; Δ̄ CI {ci(r.get('Dbar_ci90'), 3)}")
    rp = DATA / "NE34/robustness.json"
    if rp.exists():
        R = json.loads(rp.read_text())
        print("\n## Robustness\n\n| Pair: variant | N | Δ̄ | ε | P1 r (p) | P2 ρ | Δg | P4 D | pair |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        for k, r in R.items():
            print(f"| {k} | {r['N']} | {f(r['Dbar'], 3)} | {f(r['eps'])} | {f(r['P1_r'])} ({f(r['P1_p'], 3)}) | {f(r['P2_rho'])} | "
                  f"{f(r.get('dg'))} | {f(r.get('P4_D'), 3)} | {r['v']} |")
    kp = DATA / "NE34/kickoffs.json"
    if kp.exists():
        K = json.loads(kp.read_text())
        print("\n## Kickoffs\n\n| Transition | regime | modes | N | Δm | v̄ (κ2) | ε = Δm/√v̄ |\n| --- | --- | --- | --- | --- | --- | --- |")
        for t in K["transitions"]:
            print(f"| #{t['old']} → #{t['new']} | {t['regime']} | {t['mode_old']} → {t['mode_new']} | {t['N']} | {f(t['Dm'], 3)} | "
                  f"{f(t['v'], 4)} | {f(t['eps'])} |")
        print("\n", {k: v for k, v in K.items() if k not in ("transitions", "course")})
    ps = DATA / "periods_summary.json"
    if ps.exists():
        print("\n## Periods\n")
        for k, v in json.loads(ps.read_text()).items():
            print(k, json.dumps(v)[:600])


if __name__ == "__main__":
    main()
