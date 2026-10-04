"""H35 O7: NE10, the nudger switched on (CHANGELOG 2026-02-10; first nudges 2026-02-13, inside #30), regime I.

Before = G27 (01-12 .. 01-23; #28-#29 are held out) + G30's nudge-free days 02-09 .. 02-12.
After  = G30's 02-13 + G31 (02-16 .. 02-19; 02-20 = NE11 excluded).
Work accounting (the transition is the object, a named cross-period exception): the switch-on can change the active
fraction by at most nudges/day x per-nudge work / present agent-minutes. Per-nudge work: the pooled regime-I first-nudge
ATT (G30 + G31) and, as a ceiling, G51's ATT transported. Observed: active-fraction change with day bootstraps, and a
placebo split inside the before period. Information: per-period results (G30, G31) are in their results.json.

Usage: uv run python hypotheses/H35-nudger-maxwell-demon/analysis/ne10.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h35lib as L  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

B = 2000


def daily(g: pl.DataFrame) -> pl.DataFrame:
    return g.group_by("pt_date").agg(pl.len().alias("epochs"), pl.col("a_now").sum().alias("active"),
                                     pl.col("M").sum().alias("nudges")).sort("pt_date")


def boot_diff(a, b, wa, wb, rng):
    pt = np.sum(b * wb) / np.sum(wb) - np.sum(a * wa) / np.sum(wa)
    bs = []
    for _ in range(B):
        ia = rng.integers(0, len(a), len(a)); ib = rng.integers(0, len(b), len(b))
        bs.append(np.sum(b[ib] * wb[ib]) / np.sum(wb[ib]) - np.sum(a[ia] * wa[ia]) / np.sum(wa[ia]))
    return float(pt), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def main():
    rng = np.random.default_rng(L.SEED)
    g27 = pl.read_parquet(L.OUT / "G27" / "grid.parquet")
    g30 = pl.read_parquet(L.OUT / "G30" / "grid.parquet")
    g31 = pl.read_parquet(L.OUT / "G31" / "grid.parquet")
    pre = pl.concat([g27, g30.filter(pl.col("pt_date") < "2026-02-13")], how="diagonal")
    post = pl.concat([g30.filter(pl.col("pt_date") >= "2026-02-13"), g31], how="diagonal")
    out = {"pre_days": sorted(pre["pt_date"].unique().to_list()), "post_days": sorted(post["pt_date"].unique().to_list()),
           "pre_nudges": int(pre["M"].sum()), "post_nudges": int(post["M"].sum())}
    # pooled regime-I first-nudge ATT across the transition (G30 + G31 after the switch-on)
    w = L.work_minute(post, rng, B=1000)
    out["att_first_regimeI_pooled_strict"] = w["first_pastonly"]["y30"]
    out["att_first_regimeI_n_strict"] = w["first_pastonly"]["n"]
    # strict isolation leaves ~1 nudge in regime I; the accounting uses H04's isolation set (nudges + human messages)
    att_I = w["first_pastonly_H04iso"]["y30"]
    out["att_first_regimeI_pooled"] = att_I
    out["att_first_regimeI_n"] = w["first_pastonly_H04iso"]["n"]
    out["placebo_regimeI_pooled"] = w["first_pastonly_H04iso"]["ypre"]
    out["att_variant_used"] = "first_pastonly_H04iso"
    att51 = None
    p51 = L.OUT / "G51" / "results.json"
    if p51.exists():
        att51 = json.loads(p51.read_text())["work"]["first_pastonly"]["y30"]
    dpre, dpost = daily(pre), daily(post)
    npd = dpost["nudges"].mean()
    epd = dpost["epochs"].mean()
    out["nudges_per_day_post"] = float(npd)
    out["predicted_change_active_fraction_regimeI_att"] = [float(npd * x / epd) for x in att_I]
    if att51:
        out["predicted_change_active_fraction_G51_att"] = [float(npd * x / epd) for x in att51]
    fa = (dpre["active"] / dpre["epochs"]).to_numpy(); fb = (dpost["active"] / dpost["epochs"]).to_numpy()
    out["active_fraction_pre"] = float(np.average(fa, weights=dpre["epochs"]))
    out["active_fraction_post"] = float(np.average(fb, weights=dpost["epochs"]))
    out["observed_change"] = boot_diff(fa, fb, dpre["epochs"].to_numpy().astype(float), dpost["epochs"].to_numpy().astype(float), rng)
    k = len(fa) // 2
    out["placebo_split_change"] = boot_diff(fa[:k], fa[k:], dpre["epochs"].to_numpy()[:k].astype(float),
                                            dpre["epochs"].to_numpy()[k:].astype(float), rng)
    out["day_sd_active_fraction_pre"] = float(np.std(fa, ddof=1))
    out["detectable_change_2sd_of_mean"] = float(2 * np.std(fa, ddof=1) * np.sqrt(1 / len(fa) + 1 / len(fb)))
    for p in ("G30", "G31"):
        rp = L.OUT / p / "results.json"
        if rp.exists():
            r = json.loads(rp.read_text())
            if "info" in r:
                out[f"info_{p}"] = {"bits_per_nudge": r["info"]["I_X"]["bits_per_nudge"], "above_null": r["info"]["I_X"]["above_null"],
                                    "n_nudge_epochs": r["info"]["n_nudge_epochs"]}
    (L.OUT / "NE10").mkdir(parents=True, exist_ok=True)
    L.jdump(out, L.OUT / "NE10" / "ne10_results.json")
    L.write_provenance(L.OUT / "NE10", "hypotheses/H35-nudger-maxwell-demon/analysis/ne10.py",
                       ["data/processed/H35-nudger-maxwell-demon/{G27,G30,G31}/grid.parquet"], {"B": B, "seed": L.SEED})
    print(json.dumps({k: v for k, v in out.items() if k not in ("pre_days", "post_days")}, indent=1, default=str))


if __name__ == "__main__":
    main()
