"""Assemble H06 round 1: one table over all scopes and label sets, cross-period tallies, and the card's
"Results by goal period" rows. Writes data/processed/H06-neutral-cooperative-dynamics/results_round1.parquet and
cross_period_round1.json; prints markdown rows.
Usage: uv run python hypotheses/H06-neutral-cooperative-dynamics/analysis/assemble.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import period_folders as PF  # noqa: E402

DATA = PF.DATA
FREE = ["G11", "G16", "G31", "G37", "G44"]
CONTRAST = ["G19", "G25", "G30", "G38"]
CHECK = ["G51a", "G51b", "G51c"]
LABELSETS = PF.CLUST + ["art", "art_nocarry"]


def main():
    rows = []
    allr = {}
    for s in FREE + CONTRAST + CHECK + ["G08", "G10", "NE33pre", "NE33post"]:
        r = PF.load(s)
        if not r:
            continue
        allr[s] = r
        for k in LABELSETS:
            v = r["sets"].get(k)
            if not v:
                continue
            row = {"scope": s, "labelset": k, "testable": bool(v.get("testable")), "N": v.get("N"), "mean_per_win": v.get("mean_per_win")}
            if v.get("testable"):
                f = v["fits"]
                row.update({"LLR_NH": v["LLR_NH"], "LLR_NC": v["LLR_NC"], "best": v["best_model"], "mu_ncd": f["ncd"]["mu"],
                            "mu_B": v["mu_B"], "mu_L": v["mu_L"], "copyfrac": v["copyfrac"], "n_changes": v["n_changes"],
                            "n_events": v["n_events"], "lam_star_asym": v["lambda_star_asym"]})
                row.update({f"obs_{a}": b for a, b in v["obs"].items()})
                for m in ("ncd", "hubbell", "conformist"):
                    row[f"ppcj_{m}"] = f[m]["ppc_joint"]
                    row[f"adequate_{m}"] = f[m]["adequate"]
                    row[f"repro_{m}"] = PF.n_repro(v, m)
                    for st in ("lam", "single", "beta", "copyfrac"):
                        pr = f[m]["pred"][st]
                        row[f"{st}_pred_{m}"], row[f"{st}_lo_{m}"], row[f"{st}_hi_{m}"] = pr[0], pr[1], pr[2]
                    if "moment_fit" in f[m]:
                        row[f"mom_mu_{m}"] = f[m]["moment_fit"]["mu"]
                        row[f"mom_lam_{m}"] = f[m]["moment_fit"]["lam_pred"][0]
                        row[f"mom_lam_ppc_{m}"] = f[m]["moment_fit"]["ppc_lam"]
                if v.get("null_ind"):
                    row.update({f"null_{a}": b for a, b in v["null_ind"].items()})
            rows.append(row)
    df = pl.DataFrame(rows, infer_schema_length=None)
    df.write_parquet(DATA / "results_round1.parquet", compression="zstd")
    t = df.filter(pl.col("testable"))
    cross = {}
    for grp, ss in (("free", FREE), ("contrast", CONTRAST), ("check", CHECK)):
        x = t.filter(pl.col("scope").is_in(ss))
        xi = x.filter(pl.col("labelset").is_in(PF.CLUST))
        xa = x.filter(pl.col("labelset") == "art")
        cross[grp] = {
            "P1_verdicts": {s: allr[s]["P1"]["verdict"] for s in ss if s in allr},
            "art_verdicts": {s: allr[s]["P1_art"] for s in ss if s in allr},
            "P2": {s: allr[s]["P2"] for s in ss if s in allr}, "P2_art": {s: allr[s]["P2_art"] for s in ss if s in allr},
            "P3": {s: allr[s]["P3"] for s in ss if s in allr}, "P3_art": {s: allr[s]["P3_art"] for s in ss if s in allr},
            "intent_sets": xi.height,
            "intent_best_counts": {m: int((xi["best"] == m).sum()) for m in ("ncd", "hubbell", "conformist")},
            "intent_all_inadequate": int(((xi["ppcj_ncd"] < 0.01) & (xi["ppcj_hubbell"] < 0.01) & (xi["ppcj_conformist"] < 0.01)).sum()),
            "intent_ncd_adequate": int(xi["adequate_ncd"].sum()),
            "intent_single_above_ncd_hi": int((xi["obs_single"] > xi["single_hi_ncd"]).sum()),
            "intent_copy_below_ncd_lo": int((xi["copyfrac"] < xi["copyfrac_lo_ncd"]).sum()),
            "intent_lam_below_ncd_lo": int((xi["obs_lam"] < xi["lam_lo_ncd"]).sum()),
            "intent_median_copyfrac": float(xi["copyfrac"].median()) if xi.height else None,
            "intent_median_single": float(xi["obs_single"].median()) if xi.height else None,
            "art_sets": xa.height,
            "art_ncd_adequate": int(xa["adequate_ncd"].sum()) if xa.height else 0,
            "art_beta_below_hub_median": int((xa["obs_beta"] < xa["beta_pred_hubbell"]).sum()) if xa.height else 0,
        }
    (DATA / "cross_period_round1.json").write_text(json.dumps(cross, indent=1, default=float))
    print(json.dumps(cross, indent=1, default=float))


if __name__ == "__main__":
    main()
