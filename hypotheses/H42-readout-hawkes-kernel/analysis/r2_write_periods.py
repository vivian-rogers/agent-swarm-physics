"""H42 round 2: add a 'Round 2 (2026-10-05)' block and a '**Round 2 verdict:**' line to every goal-period README.
Idempotent: an earlier round-2 block (from its heading to the end of the file) and verdict line are replaced. The round-1
'**Verdict:**' line stays on top (OVERVIEW.md reads it).
Usage: uv run python hypotheses/H42-readout-hawkes-kernel/analysis/r2_write_periods.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import r2lib as L  # noqa: E402

HYP = HERE.parent
HEAD = "## Round 2 (2026-10-05)"


def f(x, d=3):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "–"
    return f"{x:.{d}f}"


def ci(r, k, d=3, sc=1.0):
    e, lo, hi = r.get(k), r.get(k + "_lo"), r.get(k + "_hi")
    if e is None or (isinstance(e, float) and not np.isfinite(e)):
        return "–"
    return f"{sc * e:.{d}f} [{sc * lo:.{d}f}, {sc * hi:.{d}f}]"


def unit_rows(z: pl.DataFrame, r3: pl.DataFrame, g: int) -> list[str]:
    zg = z.filter(pl.col("goal_no") == g)
    out = ["| unit | calls | talk J named | cold | thread | unnamed | pause J named (excess) | log gap J named (excess) | "
           "chat next J unnamed (excess) | R3 n_x(A) r1 → Cox | R3 n_x(B) r1 → Cox | R3 named per msg r1 → Cox | "
           "R3 Δcv(Bmu − S0), Cox (mnats/event) |", "| " + " | ".join(["---"] * 13) + " |"]
    ids = sorted(set(zg["unit_id"].to_list()) | set(r3.filter(pl.col("goal_no") == g)["unit_id"].to_list()))
    for u in ids:
        def pick(o, sp, X, ex=False):
            q = zg.filter((pl.col("unit_id") == u) & (pl.col("outcome") == o) & (pl.col("spec") == sp)
                          & (~pl.col("field")) & (pl.col("X") == X))
            if len(q) == 0:
                return "–"
            r = q.to_dicts()[0]
            if ex:
                return f"{r['ex']:.4f} ± {1.96 * r['se_ex']:.4f}"
            return f"{r['J']:.3f} [{r['lo']:.3f}, {r['hi']:.3f}]"
        q = zg.filter((pl.col("unit_id") == u) & (pl.col("outcome") == "talk") & (pl.col("spec") == "r2"))
        n = q["n"][0] if len(q) else None
        rr = r3.filter(pl.col("unit_id") == u).to_dicts()
        rr = rr[0] if rr else {}
        g_ = rr.get("gBmu_fld")
        out.append(f"| {u} | {n if n is not None else '–'} | {pick('talk', 'r2', 'named')} | {pick('talk', 'r1', 'cold')} | "
                   f"{pick('talk', 'r1', 'thrn')} | {pick('talk', 'r2', 'un')} | {pick('pause', 'r2', 'named', True)} | "
                   f"{pick('loggap', 'r2', 'named', True)} | {pick('chatnext', 'r2', 'un', True)} | "
                   f"{f(rr.get('nxA_r1'))} → {f(rr.get('nxA_cox10'))} | {f(rr.get('nxB_r1'))} → {f(rr.get('nxB_fld'))} | "
                   f"{f(rr.get('pn_r1'))} → {f(rr.get('pn_fld'))} | "
                   f"{f(g_ * 1000 if g_ is not None and rr.get('cv') else None, 2)} |")
    return out


def block(r: dict, z, r3) -> str:
    g = int(r["goal_no"])
    reg = r["regime"]
    lines = [HEAD, "",
             "*Prediction (templated from the card's round-2 pre-registration, 2026-10-05 04:05 UTC, written before any "
             "round-2 statistic):* in regime III a named read raises talk at the read-out call (≈ 0.08 per read, H67), "
             "cold-named messages carry at least half the thread-named jump, the named Hawkes kernel survives a fitted "
             "Cox field, and reads move call timing only through the reading call's own decision. In regimes I–II no "
             "class switch beyond the call-skeleton null. Round-2 verdict rule: *supported* if the Cox-field named model "
             "beats field-only S0 held out (summed over the period's CV units) with n_named > 0 **and** the pooled "
             "cold-named talk J has its CI above 0; *failed* if neither; *mixed* otherwise; *descriptive* without a CV unit.",
             "",
             f"**Round 2 verdict:** {r['r2_verdict']}. Period pools (random effects over units, 95% CI): talk J named "
             f"{ci(r, 'talk_named')}, cold {ci(r, 'talk_cold')}, thread {ci(r, 'talk_thrn')}, unnamed "
             f"{ci(r, 'talk_un', 4)}."]
    if reg == "III":
        lines.append(f"Call timing (excess over the call-skeleton null): pause J named {ci(r, 'pause_named_ex', 4)}; "
                     f"log gap J named {ci(r, 'loggap_named_ex', 4)} (fragile, Amendment R2-A).")
    else:
        lines.append(f"Call class (excess over the call-skeleton null): chat next J unnamed {ci(r, 'chatnext_un_ex', 4)}, "
                     f"named {ci(r, 'chatnext_named_ex', 4)}.")
    if r.get("units_right") is not None or r.get("pn_fld") is not None:
        gs = r.get("gBmu_sum_fld")
        lines.append(f"R3 (Cox field; event-weighted): exponential n_x {f(r.get('nxA_r1'))} → {f(r.get('nxA_cox'))}; "
                     f"read-out n_x {f(r.get('nxB_r1'))} → {f(r.get('nxB_fld'))}; named per message {f(r.get('pn_r1'))} → "
                     f"{f(r.get('pn_fld'))}; summed held-out gain of the named model over field-only S0 "
                     f"{f(gs, 1) if r.get('cv_units') else '– (no CV unit)'} nats.")
    lines += ["", *unit_rows(z, r3, g), "",
              "J = β(read) − β(in flight) per read message (OLS within agent × day × call-class cells; 1-h block "
              "bootstrap). Excess = J minus the call-skeleton null mean (8 synthetic message streams on the real call "
              "skeleton). R3: 'r1' = round 1's shared 30-min baseline refitted; 'Cox' = free log-rate per day × 10 min "
              "(per day × room × 10 min in multi-room units). Data: `data/processed/H42-readout-hawkes-kernel/round2/`."]
    return "\n".join(lines) + "\n"


def main():
    z = pl.read_parquet(L.R2 / "r2_long.parquet")
    r3 = pl.read_parquet(L.R2 / "r3_units.parquet")
    PT = pl.read_parquet(L.R2 / "r2_periods.parquet")
    n = 0
    for r in PT.iter_rows(named=True):
        p = HYP / "goalperiod-subhypotheses" / f"G{int(r['goal_no']):02d}" / "README.md"
        if not p.exists():
            print("missing", p)
            continue
        t = p.read_text()
        if HEAD in t:
            t = t[:t.index(HEAD)].rstrip() + "\n"
        t = re.sub(r"\n\*\*Round 2 verdict:\*\*[^\n]*", "", t)
        t = re.sub(r"(\n\*\*Role:\*\*[^\n]*)", lambda m: m.group(1) + f"\n**Round 2 verdict:** {r['r2_verdict']} "
                   "(Round 2 below; the line above is round 1's)", t, count=1)
        t = t.rstrip() + "\n\n" + block(r, z, r3)
        p.write_text(t)
        n += 1
    print("updated", n)


if __name__ == "__main__":
    main()
