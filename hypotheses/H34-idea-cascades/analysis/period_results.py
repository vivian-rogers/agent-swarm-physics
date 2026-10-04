"""Assemble per-period result rows (verdict, prediction-vs-observed table, scorecard, notes) for the G cards.

  uv run python hypotheses/H34-idea-cascades/analysis/period_results.py
Reads results/period_table.parquet, results/forecast_days.parquet, results/forecast_posthoc_days.parquet;
writes results/periods.json (consumed by write_period_cards.py results).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scheme"))
import h34core as C  # noqa: E402

RES = C.OUT / "results"
MULTI_ROOM = {35, 36, 37, 38, 39, 40, 41, 42, 44}   # two rooms active (#best / #rest; #40 merged with GPT-5 alone)


def f(x, nd=2):
    if x is None or (isinstance(x, float) and (math.isnan(x))):
        return "–"
    if x == float("inf"):
        return "∞"
    return f"{x:.{nd}f}"


def verdict(r):
    if (r.get("nonseed") or 0) < 20:
        return "n/a"
    if r["R_lo"] >= 1:
        return "failed"
    cp = bool(r.get("contagion_pass"))
    sp = r.get("shape_pass")
    if sp is None:
        return "mixed" if cp else "failed"
    return "supported" if (cp and sp) else ("mixed" if (cp or sp) else "failed")


def main():
    pt = pl.read_parquet(RES / "period_table.parquet")
    fd = pl.read_parquet(RES / "forecast_days.parquet")
    fp = pl.read_parquet(RES / "forecast_posthoc_days.parquet").filter(pl.col("variant") == "V3")
    out = {}
    for r in pt.filter(pl.col("cls") == "ALL").sort("goal").to_dicts():
        g = r["goal"]
        v = verdict(r)
        n03 = r.get("n03")
        rows = [
            ["P1 R̂ < 1 (upper CI < 1)", f"R̂ = {f(r['R'], 3)} [{f(r['R_lo'], 3)}, {f(r['R_hi'], 3)}]", "critical R = 1",
             "pass" if r["R_hi"] < 1 else "fail"],
            ["P2 R̂ < H03 n̂_talk", f"R̂ {f(r['R'], 3)} vs n̂ {f(n03)}; R_c = {f(r.get('R_c'), 3)}", "HH108: R̂ > n̂",
             ("pass" if (n03 is not None and r["R"] < n03) else "fail") if n03 is not None else "n/a"],
            ["P3a FN-GW band covers P(s ≥ 3), P(s ≥ 5)",
             f"P(s≥3) {f(r['p3'], 3)} (band {f(r.get('fn_lo3'), 3)}–{f(r.get('fn_hi3'), 3)}); P(s≥5) {f(r['p5'], 3)} "
             f"(band {f(r.get('fn_lo5'), 3)}–{f(r.get('fn_hi5'), 3)})",
             f"GW-NB band covers both: {'yes' if (r.get('gw_cover3') and r.get('gw_cover5')) else 'no'}",
             "pass" if r.get("shape_pass") else "fail" + (" (s≥5 heavier than FN-GW)" if (r.get("p5", 0) > (r.get("fn_hi5") or 1)) else "")],
            ["P3b pure s^−3/2 rejected; τ_app ≥ 2", f"LR {f(r.get('lr_15pure'), 1)}; τ_app {f(r.get('tau_app'))}",
             "critical branching", "pass" if (r.get("p_15pure", 1) < 0.05 and r.get("tau_app", 0) >= 2) else "fail"],
            ["P5 HR₁₀ > 1, lower CI > 1 (A2)", f"HR₁₀ = {f(r.get('hr10'))} [{f(r.get('hr10_lo'))}, {f(r.get('hr10_hi'))}] "
             f"({int(r.get('n_k0_adopts') or 0)} adoptions at k = 0)", "field: HR₁₀ ≤ 1",
             "pass" if r.get("contagion_pass") else "fail"],
            ["P5a jitter excess (pre-registered; failed guard)", f"exposed {f(r.get('jit_obs'), 3)} vs null {f(r.get('jit_null'), 3)}, "
             f"p = {f(r.get('jit_p'), 2)}", "uninterpretable (S2)", "n/a"],
            ["P6 pooled HR(2 vs 1) ≤ 2.5", f"{f(r.get('hr21'))} [{f(r.get('hr21_lo'))}, {f(r.get('hr21_hi'))}]",
             "complex > 3; heterogeneity inflates", "pass" if (r.get("hr21") or 9) <= 2.5 else "ambiguous"],
        ]
        if g in MULTI_ROOM and r.get("rx_ratio") is not None:
            rows.append(["P5c cross-room ratio > 3", f"{f(r.get('rx_ratio'), 1)} [{f(r.get('rx_ratio_lo'), 1)}, {f(r.get('rx_ratio_hi'), 1)}] "
                         f"(P(adopt) {f(r.get('rx_p_exp'), 3)} vs {f(r.get('rx_p_unexp'), 4)})", "field ≈ 1–1.8 (S2)",
                         "pass (room fields confound)" if (r.get("rx_ratio") or 0) > 3 else "fail"])
        fdg = fd.filter(pl.col("goal") == g)
        fpg = fp.filter(pl.col("goal") == g)
        if fdg.height:
            rows.append(["P7 day-ahead 90% PI coverage (pre-registered FN-GW)",
                         f"P(s≥2) {f(fdg['cover2'].mean(), 2)}, P(s≥3) {f(fdg['cover3'].mean(), 2)} over {fdg.height} days",
                         f"post-hoc V3: {f(fpg['cover2'].mean(), 2)}, {f(fpg['cover3'].mean(), 2)}" if fpg.height else "–",
                         "pass" if fdg["cover3"].mean() >= 0.8 and fdg["cover2"].mean() >= 0.8 else "fail"])
        cls_by = {c["cls"]: c for c in pt.filter((pl.col("goal") == g) & (pl.col("cls") != "ALL")).to_dicts()}
        if g == 20:
            U, N_, D = (cls_by.get(x, {}).get("R", float("nan")) for x in ("U", "N", "D"))
            rows.append(["G20-a R̂_U, R̂_N > R̂_D", f"U {f(U)}, N {f(N_)}, D {f(D)}", "–", "pass" if (U > D and N_ > D) else "fail (numbers spread most)"])
            rows.append(["G20-b ≥ 90% of non-seed first uses exposed; R_c ≤ 0.6 R̂", f"exposed {f(r['exposed_frac'], 2)}; R_c/R̂ = {f(r['R_c'] / r['R'], 2)}",
                         "–", "fail (0.87 exposed); R_c/R̂ borderline" if r["exposed_frac"] < 0.9 else "pass"])
        if g == 42:
            rows.append(["G42-a cross-room ratio > 3", f"{f(r.get('rx_ratio'), 1)} [{f(r.get('rx_ratio_lo'), 1)}, {f(r.get('rx_ratio_hi'), 1)}]",
                         "field ≈ 1–1.8 (S2)", "pass (room fields confound)" if (r.get("rx_ratio") or 0) > 3 else "fail"])
            rows.append(["G42-b R̂ ≤ 0.3", f"{f(r['R'], 3)}", "–", "pass" if r["R"] <= 0.3 else "fail"])
        if g == 51:
            rows.append(["G51-a pure s^−3/2 rejected; τ_app ≥ 2", f"LR {f(r.get('lr_15pure'), 0)}; τ_app {f(r.get('tau_app'))}", "–",
                         "pass" if (r.get("p_15pure", 1) < 0.05 and r.get("tau_app", 0) >= 2) else "fail"])
            rows.append(["G51-b day-ahead coverage ≥ 80% (P7)", f"P(s≥2) {f(fdg['cover2'].mean(), 2)}, P(s≥3) {f(fdg['cover3'].mean(), 2)}",
                         f"post-hoc V3: {f(fpg['cover2'].mean(), 2)}, {f(fpg['cover3'].mean(), 2)}", "fail (post-hoc V3 passes)"])
        notes = []
        if r["N_room"] <= 4:
            notes.append(f"Median room size {r['N_room']}: trees cannot exceed {r['smax']} agents, so P(s ≥ 5) = 0 and the shape test is uninformative here.")
        if g in MULTI_ROOM:
            notes.append("Two rooms active: the cross-room contrast is available but confounded by room-specific fields (rooms often worked on different projects).")
        if r.get("R_uncensored") is not None:
            notes.append(f"Censoring check: R̂ without trees rooted on the last day = {f(r['R_uncensored'], 3)}.")
        notes.append(f"Root vs non-root mean offspring {f(r.get('off_root'), 3)} vs {f(r.get('off_nonroot'), 3)} (GW assumes equal).")
        notes.append(f"Root types: invented {f(r.get('root_invented'), 2)}, from humans {f(r.get('root_human'), 3)}, field (unexposed) {f(r.get('root_field'), 3)}; "
                     f"{f(r.get('exposed_frac'), 2)} of non-seed first uses were visibly exposed.")
        summ = (f"**{v}.** {r['ideas']} ideas, {r['nodes']} agent first uses, {r['trees']} trees, N_room {r['N_room']}; "
                f"R̂ = {f(r['R'], 3)}, contagion share R_c = {f(r.get('R_c'), 3)}, HR₁₀ = {f(r.get('hr10'))}; "
                f"P(s ≥ 2) = {f(r['p2'], 3)}, largest tree {r['smax']}.")
        sc = (f"C (adequacy): HR₁₀ {'beats' if r.get('contagion_pass') else 'does not beat'} the field null (lower CI {f(r.get('hr10_lo'))}). "
              f"D (unfitted shape): FN-GW band {'covers' if r.get('shape_pass') else 'misses'} the tail; pure s^−3/2 "
              f"{'rejected' if r.get('p_15pure', 1) < 0.05 else 'not rejected'}. "
              + ("G (rooms): never-exposed agents adopt far less (ratio " + f(r.get('rx_ratio'), 1) + "), confounded by room fields. "
                 if g in MULTI_ROOM else "") + "E: no natural experiment inside this period was used.")
        cl = pt.filter((pl.col("goal") == g) & (pl.col("cls") != "ALL")).sort("cls").to_dicts()
        out[str(g)] = dict(verdict=v, summary_line=summ, rows=rows, scorecard=sc, notes=notes,
                           classes=[dict(cls=c["cls"], ideas=c["ideas"], nodes=c["nodes"], R=c.get("R"), R_lo=c.get("R_lo"),
                                         R_hi=c.get("R_hi"), R_c=c.get("R_c"), p2=c.get("p2"), p3=c.get("p3"),
                                         smax=c.get("smax", 0)) for c in cl],
                           N_room=r["N_room"], n_days=r["n_days"])
    (RES / "periods.json").write_text(json.dumps(out, indent=1, default=float))
    print({k: v["verdict"] for k, v in out.items()})


if __name__ == "__main__":
    main()
