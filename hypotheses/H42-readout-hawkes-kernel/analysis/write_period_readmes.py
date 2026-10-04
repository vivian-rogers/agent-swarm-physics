"""Write the replication READMEs (goalperiod-subhypotheses/G<NN>/README.md) from units.parquet and periods.parquet.

Native folders (G19, G51, NE14, NE41) are written by hand; for G19 and G51 this script prints their replication rows
but never overwrites them. Prediction text is the card's templated replication prediction (labelled as such).
Usage: uv run python hypotheses/H42-readout-hawkes-kernel/analysis/write_period_readmes.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import h42lib as L  # noqa: E402

HYP = HERE.parent
NATIVE = {19, 51}


def goal_info():
    txt = (L.ROOT / "hypotheses/hypohypotheses/goal-periods.md").read_text()
    info = {}
    for b in re.split(r"\n### ", txt)[1:]:
        m = re.match(r"(\d+) · (.+)", b.splitlines()[0])
        if not m:
            continue
        line2 = b.splitlines()[2] if len(b.splitlines()) > 2 else ""
        dm = re.search(r"`(\S+) → (\S+)`", line2)
        info[int(m.group(1))] = {"title": m.group(2).strip(), "dates": (dm.group(1), dm.group(2)) if dm else ("?", "?")}
    return info


def f(x, d=3):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "–"
    return f"{x:.{d}f}"


def unit_table(sub: pl.DataFrame) -> str:
    hdr = ("| unit | days | N | msgs | read-out lag med / q90 (s) | pr: n_x(B) [shift q95] · Δcv(B−A) | "
           "world A: n_x(A) · n_x(A_H03) · n_x(B_t) | world B: n_x(B) [shift q95 / day-block max] · n_x(A_g) · "
           "gain(B) · Δcv(B−A_g) | activity: n_Bv · n_Bi [null max] · Δcv(B−A) |")
    lines = [hdr, "| " + " | ".join(["---"] * 9) + " |"]
    for r in sub.sort("unit_id").iter_rows(named=True):
        cv = bool(r.get("cv"))
        dBA = (r["pr:B:cv"] - r["pr:A:cv"]) * 1e3 if cv else None
        gB = (r["B:B:cv"] - r["B:S0:cv"]) * 1e3 if cv else None
        dBAg = (r["B:B:cv"] - r["B:A_g:cv"]) * 1e3 if cv else None
        aBA = (r.get("act:B:cv", np.nan) - r.get("act:A:cv", np.nan)) * 1e3 if cv and r.get("act:B:cv") is not None else None
        dbm = r.get("B:B:dayblock_max")
        lines.append(
            f"| {r['unit_id']} | {r['n_days']} | {r['n_agents']} | {r['n_talk']} | {f(r['lag_med'], 0)} / {f(r['lag_q90'], 0)} | "
            f"{f(r['pr:B:nx'])} [{f(r.get('pr:B:shift_q95'))}] · {f(dBA, 1)} | "
            f"{f(r['A:A:nx'])} · {f(r['A:A_H03:nx'])} · {f(r['A:B_t:nx'])} | "
            f"{f(r['B:B:nx'])} [{f(r.get('B:B:shift_q95'))} / {f(dbm)}] · {f(r['B:A_g:nx'])} · {f(gB, 1)} · {f(dBAg, 1)} | "
            f"{f(r.get('act:B:n_Bv'))} · {f(r.get('act:B:n_Bi'))} [{f(r.get('act:B:null_n_Bi_max'))}] · {f(aBA, 1)} |")
    return "\n".join(lines)


PRED = """*Templated replication prediction, written 2026-10-04 06:40 UTC (card), before running on this period:* B (read-out kernel, call-index tail) beats A (exponential from arrival) on day-blocked held-out likelihood; n_cross(B) > n_cross(A); n_cross(B) above its shift-null 95th percentile; ≥ 60% of B's cross mass at the read-out call and the next one. Regime I was predicted weaker (H08's regime-I talk clause failed). Counts against: Δℓ(B − A) ≤ 0 and n_cross(B) ≤ n_cross(A).
*Amended reading (A1 07:20 UTC and A3 08:25 UTC, before the full run):* compare each world's own cross spec. Read-out cross gain in the call-clock world (world B, class baselines) vs exponential cross gain in the H03 world (world A); world B's n_cross(B) against its shift and day-block nulls and against the synthetic shared-field floor (0.05)."""


def readme(g, info, sub, pv):
    gi = info.get(g, {"title": f"goal {g}", "dates": ("?", "?")})
    vam, vpr = pv["verdict_am"], pv["verdict_pr"]
    reg = ",".join(sorted(set(sub["regime"].to_list())))
    modes = ",".join(sorted(set(x for x in sub["mode"].to_list() if x)))
    N = f"{int(sub['n_agents'].min())}–{int(sub['n_agents'].max())}" if len(sub) > 1 else f"{int(sub['n_agents'][0])}"
    days = int(sub["n_days"].sum())
    units = ", ".join(sorted(sub["unit_id"].to_list()))
    cvs = sub.filter(pl.col("cv") == True)  # noqa: E712
    out = [f"# H42 × G{g:02d}: {gi['title']} ({gi['dates'][0]} → {gi['dates'][1]})", "",
           (f"**Verdict:** {vam} (n_x read-out {pv['nxB_w']:.3f} vs exponential {pv['nxA_w']:.3f}; held-out cross gain {pv['gainB']:+.1f} vs {pv['gainA']:+.1f} nats; nulls beaten: {'yes' if pv['beats_null_B'] else 'no'}; amended rule A1/A3; pre-registered rule {vpr}, void)"
            if len(cvs) else f"**Verdict:** {vam} (1-day units only: in-sample fits; pre-registered rule {vpr})"),
           "**Role:** replication (exploratory, non-holdout)",
           f"**Period:** regime {reg} · mode {modes} · N {N} · {days} non-holdout days in units {units}.", "",
           "## Why this period",
           f"Layer-1 replication: the common estimator on every eligible unit. {len(cvs)} of {len(sub)} unit(s) have ≥ 2 days (held-out likelihood); 1-day units are fitted in sample only (descriptive).", "",
           "## Prediction", PRED, "", "## Result",
           "Units below. n_x = cross-branching ratio (compensator share: extra talk events per message, all recipients). "
           "Δcv and gain are day-blocked held-out log-likelihood differences in millinats per event (positive favours the first spec; gain = vs the world's own S0). "
           "'world pr' = pre-registered specs (own call-clock pulse in every spec, which drives every continuous kernel, A included, to zero; see card A1).", "",
           unit_table(sub), ""]
    if len(cvs):
        out += [f"- Pre-registered rule: summed Δℓ(B − A) = {f(pv.get('dBA_pr'), 1)} nats; event-weighted n_x(B) {f(pv.get('nxB_pr'))} vs n_x(A) {f(pv.get('nxA_pr'))}; B above shift q95 in most units: {pv.get('beats_null_pr')} → **{vpr}**.",
                f"- Amended reading: world-B read-out gain {f(pv.get('gainB'), 1)} nats vs world-A exponential gain {f(pv.get('gainA'), 1)} nats; event-weighted n_x {f(pv.get('nxB_w'))} (world B, B) vs {f(pv.get('nxA_w'))} (world A, A); world-B B above both nulls in most units: {pv.get('beats_null_B')}; above the 0.05 field floor: {pv.get('above_field_floor')} → **{vam}**."]
    out += ["", "Data: `data/processed/H42-readout-hawkes-kernel/" + f"G{g:02d}/units/*.json`; cross-period tables in the card.", "",
            "## Scorecard (period-specific axes)",
            "- **C (adequacy):** world-B held-out gain over S0 and the null comparison above.",
            "- **H (comparative):** B vs A_g (call index since read-out vs wall-clock time since arrival) in world B; read-out vs exponential cross gains across worlds.", "",
            "## Notes",
            "- Generated by `analysis/write_period_readmes.py` from the unit fits (`analysis/run_units.py`).",
            "- Masks: village-off gaps rebuilt from `call_windows` (A2); the shared stall tables were not used."]
    return "\n".join(out) + "\n"


def main():
    info = goal_info()
    df = pl.read_parquet(L.DATA / "units.parquet")
    pvs = pl.read_parquet(L.DATA / "periods.parquet")
    for pv in pvs.iter_rows(named=True):
        g = pv["goal_no"]
        sub = df.filter(pl.col("goal_no") == g)
        text = readme(g, info, sub, pv)
        d = HYP / "goalperiod-subhypotheses" / f"G{g:02d}"
        if g in NATIVE:
            (L.DATA / f"G{g:02d}" / "replication_block.md").write_text(text)
            print(f"G{g:02d}: native folder, replication block written to data folder")
            continue
        d.mkdir(parents=True, exist_ok=True)
        (d / "README.md").write_text(text)
    print("done")


if __name__ == "__main__":
    main()
