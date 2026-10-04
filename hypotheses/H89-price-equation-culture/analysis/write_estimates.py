"""Write H89 per-period rows to data/processed/shared/per_period_estimates.parquet (write_estimates).

  uv run python hypotheses/H89-price-equation-culture/analysis/write_estimates.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

DATA = ROOT / "data/processed/H89-price-equation-culture"
SRC_R = "data/processed/H89-price-equation-culture/replication/replication.json"
SRC_N = "data/processed/H89-price-equation-culture/natives/natives.json"
CH = {"content_bge": "content (bge, style_resid_period)", "content_gte": "content (gte, style_resid_period)",
      "style": "style (20 H13 features)", "conv": "conventions (top-50 N ideas)"}
METHOD = "H89.price_xfit (cross-fitted energy share over day transitions; leave-one-agent-out jackknife)"


def unit_of(g: int) -> str:
    pu = pl.read_parquet(ROOT / "data/processed/shared/period_units.parquet").filter(pl.col("goal_no") == g)
    return pu["unit_id"][0] if pu.height == 1 else f"G{g:02d}"


def fin(x):
    return x is not None and isinstance(x, (int, float)) and math.isfinite(x)


def row(base, stat, r, key, null, notes=None):
    est, se = r.get(key), r.get(f"{key}.se")
    if not fin(est):
        return None
    ok = fin(se)
    return dict(base, statistic=stat, estimate=float(est), se=float(se) if ok else None,
                ci_lo=float(est - 1.96 * se) if ok else None, ci_hi=float(est + 1.96 * se) if ok else None,
                ci_kind="jackknife_z" if ok else "none", null=null, notes=notes)


def main():
    rep = json.loads((DATA / "replication/replication.json").read_text())["periods"]
    out = []
    for g, r in rep.items():
        g = int(g)
        if not r.get("eligible"):
            continue
        for tag, ch in CH.items():
            rel = r.get("reliable", {}).get(tag, False)
            base = dict(period_unit=unit_of(g), goal_no=g, channel=ch, role="replication", ci_level=0.95, source=SRC_R,
                        confirmatory=False, post_hoc=False, n=float(r["n_agents"]), n_kind="agents (jackknife units)",
                        method=METHOD, first_day=r["first_day"], last_day=r["last_day"],
                        status="ok" if rel else "unreliable (rho < 0.3, A1)")
            for stat, key, null in (("price_share_migration", f"{tag}.s_mig", "composition-only: 1"),
                                    ("price_share_transmission", f"{tag}.s_trans", "field-only rival R1"),
                                    ("price_share_selection", f"{tag}.s_sel", "w-permutation within transition")):
                x = row(base, stat, r, key, null,
                        notes=(f"perm p {r[f'{tag}.perm_p']:.3f}" if stat == "price_share_selection" else None))
                if x:
                    out.append(x)
            if tag.startswith("content"):
                for stat, key, null in (("price_residual_R", f"{tag}.R", "kill: R = 0 (migration + kickoff)"),
                                        ("price_kickoff_share", f"{tag}.s_kick", "0"),
                                        ("price_persistence_C", f"{tag}.C", "iid day topics: C = -0.5")):
                    x = row(base, stat, r, key, null)
                    if x:
                        out.append(x)
            phi = r.get(f"{tag}.phi_hat")
            if fin(phi):
                out.append(dict(base, statistic="price_implied_field_fraction", estimate=float(phi), ci_lo=None,
                                ci_hi=None, ci_kind="none", null="calibration curve s_Mig(phi), noise-free (A3)",
                                notes="derived reading aid, not a test"))
        out.append(dict(period_unit=unit_of(g), goal_no=g, channel="parentage (in-cone adoption)", role="replication",
                        statistic="price_mean_social_weight_lambda", estimate=float(r["lam_mean"]), ci_lo=None,
                        ci_hi=None, ci_kind="none", n=float(r["n_in"]), n_kind="in-cone adoptions by stayers",
                        method=METHOD, null="none", source=SRC_R, confirmatory=False, post_hoc=False, ci_level=0.95))
    nat = json.loads((DATA / "natives/natives.json").read_text())
    n1 = nat["NE29"]
    for lab, key in (("entry 02-18", "NE29:entry"), ("retirement 02-19", "NE29:retirement")):
        t = n1["transitions"][lab]
        for tag in ("style", "content_bge"):
            out.append(dict(period_unit=unit_of(31), goal_no=31, channel=CH[tag], role="native",
                            statistic="price_share_roster_migration_transition", estimate=float(t[f"{tag}.s_mig_roster"]),
                            ci_lo=None, ci_hi=None, ci_kind="none", n=1.0, n_kind="transitions",
                            method="H89.price_xfit single transition", null="0", source=SRC_N, confirmatory=False,
                            post_hoc=False, unit_local=key, first_day=t["d0"], last_day=t["d1"], ci_level=0.95))
    out.append(dict(period_unit=unit_of(31), goal_no=31, channel=CH["content_bge"], role="native",
                    statistic="price_retirement_change_percentile", estimate=float(n1["b"]["percentile"]), ci_lo=None,
                    ci_hi=None, ci_kind="none", n=float(n1["b"]["n_placebo"]), n_kind="placebo transitions (#30-#31)",
                    method="H89 stayer change energy rank", null="< 0.9", source=SRC_N, confirmatory=False,
                    post_hoc=False, unit_local="NE29", ci_level=0.95))
    n2 = nat["NE32"]
    for tag in ("style", "content_bge", "content_gte"):
        out.append(dict(period_unit="G51", goal_no=51, channel=CH[tag], role="native",
                        statistic="price_newcomer_entry_share", estimate=float(n2["pooled_entry_share"][tag]), ci_lo=None,
                        ci_hi=None, ci_kind="none", n=3.0, n_kind="newcomers", method="H89 newcomer Mig_in share (energy-pooled)",
                        null="0", source=SRC_N, confirmatory=False, post_hoc=False, unit_local="NE32", ci_level=0.95))
        out.append(dict(period_unit="G51", goal_no=51, channel=CH[tag], role="native",
                        statistic="price_newcomer_cos_to_veterans", estimate=float(n2["cos"][tag]), ci_lo=None,
                        ci_hi=None, ci_kind="none", n=3.0, n_kind="newcomers", method="H89 cross-fitted cosine",
                        null="0", source=SRC_N, confirmatory=False, post_hoc=False, unit_local="NE32", ci_level=0.95))
    n3 = nat["N3"]
    for tag in ("style", "content_bge", "content_gte", "conv"):
        k = f"{tag}.cum_roster"
        out.append(dict(period_unit="G51", goal_no=51, channel=CH[tag], role="native",
                        statistic="price_cumulative_roster_share", estimate=float(n3["full"][k]),
                        se=float(n3["se"][k]), ci_lo=float(n3["full"][k] - 1.96 * n3["se"][k]),
                        ci_hi=float(n3["full"][k] + 1.96 * n3["se"][k]), ci_kind="jackknife_z", n=32.0,
                        n_kind="agents (jackknife units)", method="H89.price_xfit cumulative share", null="0.5 (N3-a)",
                        source=SRC_N, confirmatory=False, post_hoc=False, unit_local="G51 growth", ci_level=0.95,
                        first_day="2026-07-06", last_day="2026-09-04"))
    df = E.write_estimates(out, hypothesis="H89")
    print(f"wrote {df.height} H89 rows")


if __name__ == "__main__":
    main()
