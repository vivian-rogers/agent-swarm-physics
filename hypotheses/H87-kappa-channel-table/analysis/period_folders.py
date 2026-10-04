"""Write the H87 replication period READMEs (one per regime-III period with >= 300 forced erasures) from results.json.
Usage: uv run python hypotheses/H87-kappa-channel-table/analysis/period_folders.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
H = ROOT / "hypotheses/H87-kappa-channel-table/goalperiod-subhypotheses"
RES = ROOT / "data/processed/H87-kappa-channel-table/results/results.json"
NATIVE = {"G37"}  # native folder (N2); its replication numbers are written into it by write_g37()
NAMES = {"A": "own artifact", "M": "memory note", "G": "chat reads", "Q": "history search", "C": "context window"}


def titles() -> dict:
    t = {}
    for line in (ROOT / "hypotheses/hypohypotheses/goal-periods.md").read_text().splitlines():
        m = re.match(r"^### (\d+) · (.+)$", line)
        if m:
            t[int(m.group(1))] = m.group(2).strip()
    return t


def isfinite(x) -> bool:
    return x is not None and x == x and abs(x) != float("inf")


def f3(x):
    return "n.i." if x is None or x != x else f"{x:.3f}"


def ci(c):
    return "—" if not c or c[0] is None else f"[{c[0]:.3f}, {c[1]:.3f}]"


def verdict_a1(t: dict) -> str:
    """Per-period verdict with Amendment A1 applied to the context row too (clarified 2026-10-04 after the run):
    supported if C is identified, kappa_C's CI excludes 0 and kappa_C exceeds every other identified row's kappa;
    mixed if the erasure cost's CI excludes 0 but kappa_C is not identified (the cost carries no measurable bits);
    failed otherwise."""
    c = t["rows"]["C"]
    if t["identified"]["C"] and c["kappa_ci"][0] is not None and c["kappa_ci"][0] > 0:
        others = [t["rows"][k]["kappa"] for k in ("A", "M", "G", "Q") if t["identified"][k]]
        return "supported" if all(c["kappa"] > k for k in others) else "mixed"
    if c["dV_ci"][0] is not None and c["dV_ci"][0] > 0:
        return "mixed"
    return "failed"


def main():
    rep = json.loads(RES.read_text())["replication"]
    tt = titles()
    for p, t in rep.items():
        if p in NATIVE:
            continue
        g = int(p[1:])
        pre = t["verdict"]
        t["verdict"] = verdict_a1(t)
        d = H / p
        (d / "figures").mkdir(parents=True, exist_ok=True)
        lines = []
        for c in ("C", "A", "M", "G", "Q"):
            r = t["rows"][c]
            k = f"{f3(r['kappa'])} {ci(r['kappa_ci'])}" if t["identified"][c] else "n.i."
            dv = "—" if not isfinite(r["dV"]) else f"{r['dV']:.3f} {ci(r['dV_ci'])}"
            rel = "—" if not isfinite(r["dV_rel"]) else f"{r['dV_rel']:.3f}"
            lines.append(f"| {c} {NAMES[c]} | {f3(r['I'])} {ci(r['I_ci'])} | {dv} | {rel} | {k} | "
                         f"{'yes' if t['identified'][c] else 'no'} |")
        txt = f"""# H87 × {p}: {tt.get(g, f'goal #{g}')} ({t['days'][0]} → {t['days'][-1]})

**Verdict:** {t['verdict']}
**Role:** replication (exploratory)
**Period:** regime III · {t['agents']} agents · {len(t['days'])} days · {t['n_scramble']} forced erasures (F) and {t['n_placebo']} pseudo-erasures (P) with an own artifact.

## Why this period
A replication point for the common estimator (layer 1): the call-scale κ table on every regime-III non-holdout period with ≥ 300 forced erasures, so periods are comparable points, not independent tests.

## Prediction
*Templated replication prediction, written 2026-10-04 ~20:07 UTC in the card (row R), before running on this period.*
- Rows C (context), A (own artifact), M (memory note), G (chat reads), Q (history search) on F vs P events; I_c in bits (Miller–Madow, within agent × period permutation floor), ΔV_c in commits per 20 calls (Poisson DiD or scramble cost), κ_c = ΔV_c / I_c with a paired agent-day bootstrap (200 draws).
- **Verdict rule:** supported if κ_C > 0 with CI excluding 0 and κ_C exceeds every identified row's κ (Amendment A1: identified = I CI lower bound > 0.02 bits); failed if κ_C's CI includes 0; mixed otherwise.
- *Clarification after the run (2026-10-04, disclosed):* A1 is applied to the context row as well, so κ_C counts only when I_C is identified. A period whose erasure cost is positive (CI excluding 0) but whose I_C is not identified is *mixed*. Verdict under the original point rule: {pre}.
- *Counts against:* the context row is not the most valuable channel per bit.

## Result
*Run 2026-10-04 (`analysis/run.py` → `data/processed/H87-kappa-channel-table/results/results.json`, block `replication`).*

| Row | I (bits) [95% CI] | ΔV (commits per 20 calls) [95% CI] | ΔV_rel | κ (commits per 20 calls per bit) | identified |
| --- | --- | --- | --- | --- | --- |
""" + "\n".join(lines) + f"""

- For C, ΔV is the erasure cost (placebo minus scramble) and ΔV_rel its share of placebo output; I_C = I_P − I_F ({f3(t['rows']['C']['I_placebo'])} − {f3(t['rows']['C']['I_scramble'])}).
- **Templated verdict:** {t['verdict']}.

## Scorecard (period-specific axes)
- Replication point only (layer 1): informs C (the context row beats its placebo) and I (consistency of the channel ranking across periods) in the main card.
"""
        (d / "README.md").write_text(txt)
        print("wrote", d)


if __name__ == "__main__":
    main()
