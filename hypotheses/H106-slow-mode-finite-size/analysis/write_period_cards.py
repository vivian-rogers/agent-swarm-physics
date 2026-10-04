"""H106 period folders. --predict writes the pre-run READMEs (Verdict pending, dated prediction); --results fills
Verdict and Result from replication/natives outputs, keeping the Prediction section verbatim.
Usage: uv run python hypotheses/H106-slow-mode-finite-size/analysis/write_period_cards.py --predict | --results
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h106lib as L  # noqa: E402

CARD = HERE.parent
GP = CARD / "goalperiod-subhypotheses"
import datetime as _dt
PRED_STAMP = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def period_rows():
    out = []
    for reg in ("I", "III"):
        b = pl.read_parquet(L.OUT / f"blocks_{reg}.parquet")
        for g, sub in b.group_by("goal_no", maintain_order=True):
            g = int(g[0])
            out.append({"goal": g, "regime": reg, "N": float(sub["N_b"].mean()), "n_blocks": sub.height,
                        "first": min(sub["first_day"]), "last": max(sub["last_day"]),
                        "days": int(sub["n_days"].sum()), "members": int(sub["n_members"].max())})
    return out


def replication_prediction(r):
    if r["regime"] == "I":
        return (f"Regime-I replication point. Observable: ρ_G, the goal-pair-weighted mean disattenuated similarity "
                f"(4-agent subsets, split-half R̂) between this period's blocks and other goals' blocks within 10 active "
                f"days, reported with N_G = {r['N']:.1f}. One period cannot test the slope, so the verdict is "
                f"**descriptive**. Under the finite magnet (α_k = −1) periods with larger N have larger ρ_G (slower "
                f"decorrelation); under an outside drift ρ_G does not depend on N. The card-level α_k decides.")
    if r["goal"] == 51:
        return ""
    return (f"Regime-III point (descriptive, separate phase-diagram point; never pooled with regime I). Observable: ρ_G "
            f"as in regime I, N_G = {r['N']:.1f}. H81 found the regime-III slow mode marginal, so ρ_G may be near 0. "
            f"No verdict.")


def write_predict():
    for r in period_rows():
        if r["goal"] == 51:
            continue
        d = GP / f"G{r['goal']:02d}"; (d / "figures").mkdir(parents=True, exist_ok=True)
        (d / "figures/.gitkeep").touch()
        txt = f"""# H106 × G{r['goal']:02d}: slow-mode decorrelation vs N ({r['first']} → {r['last']}, non-holdout days)

**Verdict:** pending
**Role:** exploratory
**Period:** regime {r['regime']} · active population N ≈ {r['N']:.1f} (block mean) · {r['n_blocks']} goal × week block(s) · {r['days']} eligible days. Splits: ISO weeks (blocks, H81).

## Why this period
A regime-{r['regime']} goal period with ≥ 1 block of ≥ 4 agents with residuals: one point (N_G, ρ_G) on the finite-size plot.

## Prediction
*Written {PRED_STAMP}, before running on this period.*
{replication_prediction(r)}

## Result
(filled after the run)

## Scorecard (period-specific axes)
C, D only at card level (the slope is a cross-period statistic).

## Notes
- Data: `data/processed/H106-slow-mode-finite-size/replication/periods.parquet`.
"""
        (d / "README.md").write_text(txt)
    # natives
    ne = GP / "NE27"; (ne / "figures").mkdir(parents=True, exist_ok=True); (ne / "figures/.gitkeep").touch()
    (ne / "README.md").write_text(f"""# H106 × NE27: batch join N 4 → 7 at the #10 kickoff (2025-08-18)

**Verdict:** pending
**Role:** exploratory
**Period:** regime I · before: #2–#8 (blocks 2025-05-10 → 08-12, N 4) · after: #10–#18 (08-18 → 10-31, N 6–7.6) · #9 (08-13 → 08-15) is held out and masked. Coincident steps: NE03 (08-20, chat messages in context limited), NE04 (09-05, history search and CoT consolidation).

## Why this period
N jumps from 4 to 7 on one day. An outside drift has no reason to change its rate on that day; a finite magnet slows by the N ratio. It is the partition contrast for P1 (STANDARDS §3).

## Prediction
*Written {PRED_STAMP}, before running on this period.*
- Two-rate fit (α fixed 0, rate step at 08-18) on the cross-goal pairs of the window, V1 similarities. Statistic Δln k = ln(k_post/k_pre).
- **Magnet:** Δln k ≈ −ln(N̄_post/N̄_pre) ≈ −0.5. **Drift:** Δln k ≈ 0.
- **Pass (P2, Amendment A1):** Δln k below the 5th percentile of the drift-world (synthetic D) distribution on the same window, and within ±0.5 of the magnet value, both models. Only two placebo breaks fit inside the N ≥ 6 era (2025-11-03, 2025-12-15); they are reported descriptively. **Against:** Δln k ≥ 0.
- NE03 and NE04 change memory and context in the after window; a rate change could come from them, so a pass is necessary, not sufficient. Prior 0.15.

## Result
(filled after the run)

## Scorecard (period-specific axes)
E (interventional), D (unfitted: the jump size follows from N alone).

## Notes
- Data: `data/processed/H106-slow-mode-finite-size/natives/natives.json`.
""")
    g51 = GP / "G51"; (g51 / "figures").mkdir(parents=True, exist_ok=True); (g51 / "figures/.gitkeep").touch()
    (g51 / "README.md").write_text(f"""# H106 × G51: #51 common mode and the batch joins NE32 + NE33 (2026-07-06 → 09-04, non-holdout)

**Verdict:** pending
**Role:** exploratory
**Period:** regime III · private goals (one goal period, one scaffold) · active population ≈ 22 → 30 over nine weeks · NE32 (07-09, three newcomers in isolated rooms, merged 07-10) and NE33 (09-03/04, three newcomers). The #51 tail from 09-07 is held out.

## Why this period
H81 found a #51 cross-agent common mode with τ ≈ 3 active days. #51 has one goal and one scaffold, and N jumps twice. If that mode has magnet inertia, its daily decorrelation slows after each join.

## Prediction
*Written {PRED_STAMP}, before running on this period.*
- Day residuals as H81's #51 native (own #51 mean removed, own agent goal and #51 directions projected). Cross-agent lagged alignment L(k) (i ≠ j pairs; expectation free of N). Per window φ_W = L_W(1)/L_W(0⁺), k_W = −ln φ_W.
- **NE32:** pre 07-06 → 07-08 vs post 07-10 → 07-17. **NE33:** pre 08-27 → 09-02 vs post 09-03 → 09-04. Magnet: Δln k = −ln(N_post/N_pre) ≈ −0.1 to −0.2. Drift: 0.
- **Pass (N2):** Δln k < 0 at both joins, placebo percentile ≤ 0.10 for at least one (placebo = every other #51 day boundary with the same window lengths). **Against:** both ≥ 0.5 percentile. Expected unpowered (N rises ×1.1–1.2); if the planted-mode power is < 0.8 the verdict is **inconclusive** whatever the sign. Prior 0.1.
- Within-#51 weekly slope of k_w on ln N_w: descriptive.
- Also reported: the regime-III block-level ρ_G for #51 weeks (descriptive).

## Result
(filled after the run)

## Scorecard (period-specific axes)
E (two joins), F (planted-mode power on the #51 panel).

## Notes
- Data: `data/processed/H106-slow-mode-finite-size/natives/natives.json`.
""")


def write_results():
    per = pl.read_parquet(L.OUT / "replication/periods.parquet")
    nat = json.loads((L.OUT / "natives/natives.json").read_text())
    for r in period_rows():
        if r["goal"] == 51:
            continue
        f = GP / f"G{r['goal']:02d}/README.md"
        txt = f.read_text()
        sub = per.filter(pl.col("goal_no") == r["goal"])
        lines = ["| Model | N_G | ρ_G (disattenuated, ≤ 10 active days) | SE | pairs | implied k (per active day) |",
                 "| --- | --- | --- | --- | --- | --- |"]
        for x in sub.iter_rows(named=True):
            kk = f"{x['k_implied']:.3f}" if x["k_implied"] == x["k_implied"] and x["k_implied"] is not None else "n/a"
            rho = f"{x['rho']:.3f}" if x["rho"] == x["rho"] else "n/a"
            se = f"{x['rho_se']:.3f}" if x["rho_se"] == x["rho_se"] else "n/a"
            lines.append(f"| {x['model']} | {x['N_G']:.1f} | {rho} | {se} | {x['n_pairs']} | {kk} |")
        res = ("\n".join(lines) + "\n\nVerdict **descriptive**: one period cannot test the slope; the card-level α_k "
               "decides (see the card). The implied k uses the card-level amplitude Â of the same model.")
        txt = re.sub(r"\*\*Verdict:\*\* pending", "**Verdict:** descriptive", txt)
        txt = re.sub(r"## Result\n.*?\n## Scorecard", "## Result\n" + res + "\n\n## Scorecard", txt, flags=re.S)
        f.write_text(txt)
    for name, key in (("NE27", "NE27"), ("G51", "G51")):
        f = GP / name / "README.md"
        txt = f.read_text()
        v = nat[key]["verdict"]
        txt = re.sub(r"\*\*Verdict:\*\* pending", f"**Verdict:** {v}", txt)
        txt = re.sub(r"## Result\n.*?\n## Scorecard", "## Result\n" + nat[key]["result_md"] + "\n\n## Scorecard", txt,
                     flags=re.S)
        f.write_text(txt)


if __name__ == "__main__":
    if "--predict" in sys.argv:
        write_predict()
    elif "--results" in sys.argv:
        write_results()
