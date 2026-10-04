"""Write H97 replication period READMEs (goalperiod-subhypotheses/G<NN>/) from the run outputs. Natives are written by hand."""
from __future__ import annotations

import sys
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h97lib as L  # noqa: E402

GP = Path(__file__).resolve().parents[1] / "goalperiod-subhypotheses"
Z = 1.645


def verdict(r):
    if r["N"] < L.MIN_N_TRANSITION or not r["n_placebo"] or r["drho_full"] != r["drho_full"]:
        return "descriptive", "N < 5 or no placebo boundary: no test"
    lo = r["drho_full"] - Z * r["se_drho_full"]
    if r["drho_full"] <= 0:
        return "failed", "Δρ ≤ 0"
    if lo > 0 and r["drho_par"] > 0:
        return "supported", "Δρ 90% CI above 0 and Δρ∥ > 0"
    return "mixed", ("Δρ > 0 but its 90% CI includes 0" if lo <= 0 else "Δρ CI above 0 but Δρ∥ ≤ 0")


def main():
    pa = pl.read_parquet(L.S / "period_affordances.parquet").unique("goal_no")
    meta = {r["goal_no"]: r for r in pa.iter_rows(named=True)}
    d = pl.read_parquet(L.DATA / "NE34/transitions_all_configs.parquet")
    for r in d.filter(pl.col("cfg") == "primary").sort("p").iter_rows(named=True):
        p = r["p"]; m = meta[p]
        v, why = verdict(r)
        if not r["same_regime"]:
            v, why = "descriptive", "cross-regime transition (#36 regime II → #37 regime III): variant only"
        g = d.filter((pl.col("p") == p) & (pl.col("cfg") == "gte"))
        c = d.filter((pl.col("p") == p) & (pl.col("cfg") == "center"))
        f = lambda x: "–" if x is None or x != x else f"{x:+.2f}"  # noqa: E731
        se = lambda x: "–" if x is None or x != x else f"{x:.2f}"  # noqa: E731
        lines = [f"# H97 × G{p:02d}: {m['goal_slug']} (kickoff {r['first_day']})", "",
                 f"**Verdict:** {v}", "**Role:** replication",
                 f"**Period:** regime {r['regime']} · mode {m['mode']} · {r['N']} agents with ≥ 4 statements on #{p-1}'s last day and on day 1 · "
                 f"{m['n_rooms']} room(s). Transition #{p-1} → #{p}; the kickoff boundary is the object (exception (c)).", "",
                 "## Why this period", "One eligible kickoff transition (both neighbours non-holdout, same regime). Common estimator, templated rule.", "",
                 "## Prediction",
                 "*Templated from the card (written 2026-10-04 ~20:25 UTC, amended ~20:48 UTC before any real-data statistic), labelled as such.*",
                 "Extra forgetting Δρ = ρ0 − ρ_kick > 0 (the kickoff erases more of each agent's relative position than an ordinary day), "
                 "with Δρ∥ > 0. Rule: supported if Δρ's 90% CI (jackknife SE) is above 0 and Δρ∥ > 0; failed if Δρ ≤ 0; mixed otherwise.", "",
                 "## Result",
                 "| Statistic | bge-small | gte-modernbert | agent-centered (bge) |", "| --- | --- | --- | --- |"]
        def row(name, key, sek=None):
            vals = []
            for dd in (r, g.row(0, named=True) if g.height else None, c.row(0, named=True) if c.height else None):
                if dd is None:
                    vals.append("–"); continue
                x = dd.get(key)
                s = f" ± {se(dd.get(sek))}" if sek else ""
                vals.append(f(x) + (s if x == x and x is not None else ""))
            lines.append(f"| {name} | " + " | ".join(vals) + " |")
        row("kickoff memory ρ_kick", "rho_full", "se_rho_full")
        row("placebo memory ρ0 (median)", "rho0_full")
        row("extra forgetting Δρ", "drho_full", "se_drho_full")
        row("Δρ along k̂ (∥)", "drho_par")
        row("Δρ transverse (⊥)", "drho_perp")
        row("isotropy β∥ − β⊥", "iso_diff", "se_iso_diff")
        row("overshoot intercept a (plateau target)", "shape_a", "se_shape_a")
        lines += ["", f"Verdict reason: {why}. Placebo boundaries: {r['n_placebo']}. Within-transition reliability of χ^mem (upper bound): "
                  f"{se(r.get('noise_ceiling'))}.",
                  "Data: `data/processed/H97-quench-restoring-force/G%02d/results.json`; all configurations in `NE34/transitions_all_configs.parquet`." % p, "",
                  "## Scorecard (period-specific axes)",
                  f"- C: {'Δρ beats the placebo-day null' if v == 'supported' else 'not beyond the placebo null at this N' if v in ('mixed', 'failed') else 'not tested'}.",
                  "- D: the intercept a is an unfitted statistic of the HH-literal law (0 under the law).", "",
                  "## Notes", "- Holdout masked (`holdout_mask`); #23 excluded throughout."]
        out = GP / f"G{p:02d}"
        if p in (26,):   # native folder (announcement test) holds this replication too; edited by hand
            continue
        out.mkdir(parents=True, exist_ok=True)
        (out / "README.md").write_text("\n".join(lines) + "\n")
        print(p, v)


if __name__ == "__main__":
    main()
