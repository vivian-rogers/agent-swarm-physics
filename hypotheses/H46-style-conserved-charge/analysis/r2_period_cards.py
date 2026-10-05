"""Append (or replace) a dated "Round 2" block in the goal-period READMEs that round 2 touched. Idempotent.
Round-1 verdict lines are left as they are (they score strict conservation); each block states its own round-2 result."""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h46lib as L  # noqa: E402
import r2lib as R  # noqa: E402

PDIR = L.ROOT / "hypotheses/H46-style-conserved-charge/goalperiod-subhypotheses"
TAG = "## Round 2 (2026-10-05)"


def f(x, n=3):
    return f"{x:.{n}f}"


def ci(lo, hi, n=3):
    return f"[{lo:.{n}f}, {hi:.{n}f}]"


def put(folder: str, body: str):
    p = PDIR / folder / "README.md"
    s = p.read_text()
    s = re.sub(r"\n" + re.escape(TAG) + r".*?(?=\n## |\Z)", "", s, flags=re.S).rstrip() + "\n"
    p.write_text(s + "\n" + TAG + "\n" + body.strip() + "\n")


def main():
    r1 = json.loads((R.R2 / "r1.json").read_text())
    r2 = json.loads((R.R2 / "r2.json").read_text())
    r3 = json.loads((R.R2 / "r3.json").read_text())
    ph = json.loads((R.R2 / "posthoc.json").read_text())
    pre = ("*Pre-registered in the card (Round 2, 2026-10-05 02:44 UTC), synthetic validation and amendments R2-A1..A5 "
           "before this run; `analysis/r2_run.py` → `data/processed/H46-style-conserved-charge/r2/`. Non-reserved data.*")
    ne = r1["NE41"]
    gpU = ne["gp"]["forced"]["per_unit"]
    fwU = r3["NE41"]["fw"]["forced"]["per_unit"]
    put("NE41", f"""
**Round-2 result:** the erasure effect on style survives genre and position control (R1-P1 passed); function words move less (R3-P2 passed, marginal); the OU drift-and-reset form fails (R2 kill fired), a reset-and-hold offset fits (post hoc).
{pre}
- **Predictions (R1-P1, R3-P2, R2-P1..P3):** T_s(gp) ≥ 0.54 with cluster CI > ½; function words T_fw ≤ 0.53 or CI ∋ ½; variance growth Δ̄ > 0, ΔC(1) > 0 with OU decay, self-pull within > erased.
- **Estimator change (R2-A5):** pair distances are scaled by the agent × unit median within-pair distance (most pairs fall into agent-free strata; unscaled null T is 0.507 for style, 0.530 for function words).

| Channel (forced pairs, scaled) | T [agent-cluster 95% CI] | unscaled (round-1 method) | voluntary |
| --- | --- | --- | --- |
| style, round-1 type control (tc) | {f(ne['tc']['forced']['T'])} {ci(ne['tc']['forced']['lo'], ne['tc']['forced']['hi'])} | {f(ne['tc_unscaled']['forced']['T'])} | {f(ne['tc']['voluntary']['T'])} |
| style, genre-controlled (g) | {f(ne['g']['forced']['T'])} {ci(ne['g']['forced']['lo'], ne['g']['forced']['hi'])} | {f(ne['g_unscaled']['forced']['T'])} | {f(ne['g']['voluntary']['T'])} |
| **style, genre + position (gp)** | **{f(ne['gp']['forced']['T'])} {ci(ne['gp']['forced']['lo'], ne['gp']['forced']['hi'])}** | {f(ne['gp_unscaled']['forced']['T'])} | {f(ne['gp']['voluntary']['T'])} |
| style gp, genre-matched strata | {f(ne['gp_genre_matched']['forced']['T'])} {ci(ne['gp_genre_matched']['forced']['lo'], ne['gp_genre_matched']['forced']['hi'])} | – | {f(ne['gp_genre_matched']['voluntary']['T'])} |
| function words (≥ 10 tokens) | {f(r3['NE41']['fw']['forced']['T'])} {ci(r3['NE41']['fw']['forced']['lo'], r3['NE41']['fw']['forced']['hi'])} | {f(r3['NE41']['fw_unscaled']['forced']['T'])} | {f(r3['NE41']['fw']['voluntary']['T'])} |
| content bge | {f(ne['content_bge']['forced']['T'])} {ci(ne['content_bge']['forced']['lo'], ne['content_bge']['forced']['hi'])} | {f(ne['content_bge_unscaled']['forced']['T'])} | {f(ne['content_bge']['voluntary']['T'])} |
| content gte (second model) | {f(ne['content_gte']['forced']['T'])} {ci(ne['content_gte']['forced']['lo'], ne['content_gte']['forced']['hi'])} | – | {f(ne['content_gte']['voluntary']['T'])} |

- **Per unit (gp, forced, ≥ 30 pairs):** {', '.join(f'{u} {v["T"]:.2f}' for u, v in gpU.items())}. Two-room periods #36–#42: 0.56–0.71; #44 and #51: 0.46–0.58.
- **Per unit (function words):** {', '.join(f'{u} {v["T"]:.2f}' for u, v in fwU.items())}.
- **Drift and reset (R2, regime III pooled, gp):** variance growth Δ̄ {f(r2['gp']['pooled']['growth']['dbar'], 2)} {ci(*r2['gp']['pooled']['growth']['dbar_ci'], 2)} (fails); ΔC(1) {f(r2['gp']['pooled']['cross']['lags']['1']['dC'], 2)} {ci(*r2['gp']['pooled']['cross']['lags']['1']['dC_ci'], 2)} (> 0), but ΔC(l) does not decay over l = 1…8 (φ_C {f(r2['gp']['pooled']['cross']['phi_C'], 2)} > 1); self-pull ρ in context {f(r2['gp']['pooled']['pull']['rho_within'], 2)} vs erased {f(r2['gp']['pooled']['pull']['rho_forced'], 2)}, difference {f(r2['gp']['pooled']['pull']['diff'], 3)} {ci(*r2['gp']['pooled']['pull']['diff_ci'])}.
- **Post hoc (PH-R2a):** ΔC(1) is already {f(ph['PH_R2a']['dC1_by_j']['j=1']['dC'], 2)} {ci(*ph['PH_R2a']['dC1_by_j']['j=1']['ci'], 2)} for the first message after a reset: the context state is set at the segment start and held, as in a synthetic per-segment offset (≈ 4–5% of the per-message style variance), not grown from zero.
- **Post hoc (PH-R3b), per lab, gp:** {', '.join(f'{k} {v["gp"]["T"]:.2f}' for k, v in ph['PH_R3b'].items())} (Anthropic CI includes ½).
""")
    g12 = r1["G12"]
    put("G12", f"""
**Round-2 result:** the judge register survives genre control (R1-P2 passed).
{pre}
- **Prediction (R1-P2):** agent 9's judge-vs-debater accuracy from genre- and position-controlled style (gp) ≥ 0.7 and above content's; ≥ 2 of 4 one-time judges at percentile ≥ 0.9.
- **Result:** agent 9: gp {f(g12['role9_style']['acc'], 2)} (permutation p {f(g12['role9_style']['p_perm'], 2)}), round-1 style {f(g12['role9_tc']['acc'], 2)}, content {f(g12['role9_content']['acc'], 2)}. One-time judges (gp): {', '.join(f'agent {a} {v["pct"]:.2f}' for a, v in g12['onetime_judges_style'].items())}; content {', '.join(f'{v["pct"]:.2f}' for v in g12['onetime_judges_content'].values())}.
- Assigned side still does not move style (gp p {f(g12['side_style']['p_perm'], 2)}). Debate fingerprint (debates 1–5 → 6–10): gp {f(g12['fp_style']['acc'], 2)}, content {f(g12['fp_content']['acc'], 2)} (chance {f(g12['fp_style']['chance'], 2)}).
- Reading: judging writes in a register that the DQ2 reply/mention flags and DQ3 window states do not explain. It is register, not speech-act genre as those labels see it.
""")
    pk = list(r1["G51"]["prankster"].values())[0]
    s = r1["G51"]["summary_style"]
    n38 = r1["G51"]["NE38"]
    p51 = r2["gp"]["periods"]["51"]
    put("G51", f"""
**Round-2 result:** the Prankster's onset shift survives genre and position control (R1-P3 passed).
{pre}
- **Prediction (R1-P3):** percentile ≥ 0.95 under gp style. **Result:** gp {f(pk['pct_style'], 2)} ({f(pk['ratio_style'], 1)}× the median placebo); g {f(pk['pct_g'], 2)}; round-1 style {f(pk['pct_tc'], 2)}; content {f(pk['pct_content'], 2)} ({f(pk['ratio_content'], 1)}×).
- Incumbents at ≥ 0.9 (gp): {f(s['share_ge_0.9'], 2)} of 17; media roles {', '.join(f'{x:.2f}' for x in s['media'])} (media vs other p {f(s['media_vs_other_MW_p'], 2)}). NE38 (agent 40): day level gp {f(n38['day_pct_style'], 2)}, content {f(n38['day_pct_content'], 2)}.
- **Context-held state in #51 (R2, gp):** ΔC(1) {f(p51['cross']['lags']['1']['dC'], 2)} {ci(*p51['cross']['lags']['1']['dC_ci'], 2)}; self-pull difference (context minus erased) {f(p51['pull']['diff'], 3)} {ci(*p51['pull']['diff_ci'])}. NE41 per #51 unit: see NE41.
""")
    gt = r1["goal"]["tests"]["goal"]
    t3 = r3["classes"]["tests"]["goal"]
    fp3 = r3["classes"]["fingerprint"]
    put("NE34", f"""
**Round-2 result:** the goal-switch style shift is not speech-act genre (R1-P4 passed); function words move more than formatting (R3-P1 failed); topic-adjacent features carry a small part (R3-P4 passed, marginal); function words plus style identify agents best.
{pre}

| Channel (24 switches) | T [boundary-bootstrap 95% CI] |
| --- | --- |
| style tc (round 1) | {f(gt['tc']['T'])} {ci(gt['tc']['lo'], gt['tc']['hi'])} |
| style g (genre) | {f(gt['g']['T'])} {ci(gt['g']['lo'], gt['g']['hi'])} |
| style gp (genre + position) | {f(gt['gp']['T'])} {ci(gt['gp']['lo'], gt['gp']['hi'])} |
| style core (no digits, uppercase, colons) | {f(t3['core']['T'])} {ci(t3['core']['lo'], t3['core']['hi'])} |
| function words | {f(t3['fw']['T'])} {ci(t3['fw']['lo'], t3['fw']['hi'])} |
| function words, genre-controlled | {f(t3['fw_g']['T'])} {ci(t3['fw_g']['lo'], t3['fw_g']['hi'])} |
| content bge / gte | {f(gt['content']['T'])} / {f(gt['content_gte']['T'])} |

- **Identity across the switch (train before, test after):** content {f(fp3['content']['cross'], 2)}, style {f(fp3['tc']['cross'], 2)}, function words {f(fp3['fw']['cross'], 2)}, function words + style {f(fp3['fw_tc']['cross'], 2)} (chance {f(fp3['tc']['chance'], 2)}); function words ≥ 3× chance at {fp3['fw']['share_ge_3x']*24:.0f}/24 and above content at 24/24; function words + style beat style at {fp3['share_fw_tc_gt_tc']*24:.0f}/24. gp style {f(r1['goal']['fingerprint']['gp']['cross'], 2)}.
- **Post hoc (PH-R3a):** pronouns carry the function-word shift: {', '.join(f'{w} {s_:.2f}' for w, s_ in ph['PH_R3a']['top_words'][:6])} (shares of the excess). Who the agent writes about changes with the task.
""")
    for g, v in r2["gp"]["periods"].items():
        g = int(g)
        folder = f"G{g:02d}"
        if not (PDIR / folder).exists() or g == 51:
            continue
        c1 = v["cross"]["lags"]["1"]
        u = {k: x for k, x in gpU.items() if k.startswith(str(g))}
        put(folder, f"""
**Round-2 result (replication, regime III):** context-held style state ΔC(1) {f(c1['dC'], 2)} {ci(*c1['dC_ci'], 2)}; self-pull context minus erased {f(v['pull']['diff'], 3)} {ci(*v['pull']['diff_ci'])}.
{pre}
- Templated R2 statistics (no period verdict): cross-product of the 17-d style (genre + position removed) for lag-1 message pairs within a context segment minus pairs across a forced erasure, gap-matched ({c1['n_across']} across pairs, {v['n_agents']} agents); the pull coefficient toward the agent's last ≤ 3 messages in context vs erased.
- NE41 forced-erasure style percentile (gp) in this period's units: {', '.join(f'{k} {x["T"]:.2f}' for k, x in u.items()) or 'fewer than 30 pairs'}.
""")
    print("period READMEs updated")


if __name__ == "__main__":
    main()
