"""H38 cross-period synthesis: scores P1-P9, writes period_results.json (for write_period_folders.py results),
outcomes.json, the NE14 folder result, and the cross-period figures.

Usage: uv run python hypotheses/H38-platform-stalls/analysis/summarize.py [--data-version fixed]
Round 1b: --data-version fixed reads/writes data/processed/H38-platform-stalls/r1b/, writes figures with an `_r1b`
suffix, never touches the NE14 README (the 1b section is written by hand from r1b/NE14/result.json), and adds the
DQ8-design variants (trim*, lambda_1 trim + block shift) to the tables and scores.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
if "--data-version" in sys.argv:
    os.environ["H38_DATA_VERSION"] = sys.argv[sys.argv.index("--data-version") + 1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import h38lib as L  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402

FIG = L.HYP / "figures"
SUF = "_r1b" if L.DATA_VERSION == "fixed" else ""
TRIMV = ("trim", "trim_stall", "trim_scaffold", "trim_all")
H02_MODES = {10: "I", 17: "I", 20: "I", 39: "I", 41: "I", 42: "I", 13: "C", 18: "C", 19: "C", 24: "C", 25: "C", 26: "C",
             38: "C", 40: "C", 44: "C"}


def frac(eadj, eraw):
    return 1 - eadj / eraw if (eraw is not None and np.isfinite(eraw) and eraw > 0) else np.nan


def load():
    R = {}
    for f in sorted(L.RES.glob("G*/result.json")):
        R[f.parent.name] = json.loads(f.read_text())
    return R


def flat(R):
    rows = []
    for p, r in R.items():
        o1 = r["o123"] or {}
        a = (r["o4"] or {}).get("active", {})
        t = (r["o4"] or {}).get("talk", {})
        reg = r["regime"][-1] if len(r["regime"]) == 1 else "/".join(r["regime"])
        row = {"period": p, "goal_no": r["goal_no"], "regime": reg, "days": r["days"],
               "js": o1.get("js_share"), "js_exp": o1.get("js_expected_indep"), "js_surr": o1.get("js_share_surr"),
               "expl": o1.get("explained_share"), "expl_strict": o1.get("explained_share_strict"),
               "expl_surr": o1.get("explained_share_surr"), "expl_surr_q95": o1.get("explained_share_surr_q95"),
               "n_burst": o1.get("n_burst_min"), "burst_lor": o1.get("burst_logOR"), "burst_p_gt": o1.get("burst_p_greater"),
               "burst_p_lt": o1.get("burst_p_less"), "voff_n": (o1.get("village_off") or {}).get("n"),
               "voff_min": (o1.get("village_off") or {}).get("minutes"),
               "voff_sched": (o1.get("village_off") or {}).get("share_scheduled_minutes"),
               "o6_g_pred": (r["o4"] or {}).get("o6_g_pred")}
        for c in L.CAUSES:
            row[f"cause_{c}"] = (o1.get("cause_shares") or {}).get(c)
        for v in ("raw", "lull", "stall", "stall_strict", "field", "exo", "mask_edge", "mask_infra", "mask_scaffold",
                  "mask_all", *[f"drop_{c}" for c in L.CAUSES], *TRIMV):
            x = a.get(v, {})
            row[f"g_{v}"] = x.get("g"); row[f"E_{v}"] = x.get("E"); row[f"z_{v}"] = x.get("z"); row[f"bJ0_{v}"] = x.get("bJ0")
            y = t.get(v, {})
            row[f"tE_{v}"] = y.get("E"); row[f"tz_{v}"] = y.get("z")
        for v in ("stall", "lull", "field", "exo", "mask_edge", "mask_infra", "mask_scaffold", "mask_all",
                  *[f"drop_{c}" for c in L.CAUSES], *TRIMV):
            row[f"f_{v}"] = frac(row[f"E_{v}"], row["E_raw"])
            row[f"tf_{v}"] = frac(row[f"tE_{v}"], row["tE_raw"])
        rows.append(row)
    return pl.DataFrame(rows, infer_schema_length=None).sort("goal_no")


def units(R):
    rows = []
    for p, r in R.items():
        for u, x in (r["o5"] or {}).items():
            rows.append({"period": p, "unit": u, "regime": r["regime"][-1], "days": x["days"], "N": x["N"],
                         "js": x["js_share"], "stall_share": x["stall_share"],
                         **{f"{k}_{m}": x[k][m] for k in ("raw", "lull", "stall", "mask_scaffold") for m in ("l1", "edge", "ratio")},
                         **{f"{k}_{m}": (x.get(k) or {}).get(m) for k in ("trim_bs", "trim_stall_bs") for m in ("l1", "edge", "ratio", "T")}})
    return pl.DataFrame(rows)


def chunks(R):
    rows = []
    for p, r in R.items():
        for c in (r["o4"] or {}).get("chunks", []):
            rows.append({"period": p, "goal_no": r["goal_no"], "regime": r["regime"][-1], **c})
    return pl.DataFrame(rows, infer_schema_length=None)


def fmt(x, nd=2):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "–"
    return f"{x:.{nd}f}"


def score(D, U, C):
    S = {}
    js = D["js"].drop_nulls()
    S["P1"] = {"median_js": float(js.median()), "in_range": bool(0.05 <= js.median() <= 0.30),
               "frac_above_indep": float((D["js"] > D["js_exp"]).mean()),
               "n_periods_village_off": int((D["voff_n"] > 0).sum())}
    S["P1"]["pass"] = S["P1"]["in_range"] and S["P1"]["frac_above_indep"] >= 2 / 3 and S["P1"]["n_periods_village_off"] <= 6
    ok = D.filter(pl.col("expl").is_not_null())
    S["P2a"] = {"median_expl": float(ok["expl"].median()), "median_expl_strict": float(ok["expl_strict"].median()),
                "frac_above_surr_mean": float((ok["expl"] > ok["expl_surr"]).mean()),
                "frac_above_surr_q95": float((ok["expl"] > ok["expl_surr_q95"]).mean())}
    S["P2a"]["pass"] = S["P2a"]["median_expl"] >= 0.5 and S["P2a"]["frac_above_surr_mean"] >= 2 / 3
    cc = [f"cause_{c}" for c in L.CAUSES]
    top = []
    for r in ok.iter_rows(named=True):
        vals = {c: r[f"cause_{c}"] or 0 for c in L.CAUSES}
        top.append(max(vals, key=vals.get))
    ok = ok.with_columns(pl.Series("top_cause", top))
    r3 = ok.filter(pl.col("regime") == "III")
    r12 = ok.filter(pl.col("regime") != "III")
    S["P2b"] = {"regIII_top_causes": r3["top_cause"].value_counts().to_dicts(),
                "regI_II_top_causes": r12["top_cause"].value_counts().to_dicts(),
                "regIII_frac_pause_top": float((r3["top_cause"] == "pause").mean()),
                "regI_II_frac_edge_or_wait_top": float(r12["top_cause"].is_in(["edge", "pause"]).mean())}
    S["P2b"]["pass"] = S["P2b"]["regIII_frac_pause_top"] >= 2 / 3 and S["P2b"]["regI_II_frac_edge_or_wait_top"] >= 2 / 3
    S["P2c"] = {"max_infra_share": float(ok["cause_infra_error"].max()), "pass": bool(ok["cause_infra_error"].max() < 0.10)}
    v = D.filter(pl.col("voff_n") > 0)
    vm = (v["voff_sched"] * v["voff_min"]).sum() / v["voff_min"].sum() if v.height else None
    S["P2d"] = {"pooled_sched_share_of_village_off_minutes": vm, "n_periods": v.height,
                "pass": bool(vm is not None and vm >= 0.8)}
    b = D.filter(pl.col("n_burst") >= 20)
    S["P3"] = {"n_periods": b.height, "frac_lor_pos": float((b["burst_lor"] > 0).mean()) if b.height else None,
               "frac_p_gt_05": float((b["burst_p_gt"] < 0.05).mean()) if b.height else None,
               "frac_p_lt_05": float((b["burst_p_lt"] < 0.05).mean()) if b.height else None,
               "median_lor": float(b["burst_lor"].median()) if b.height else None}
    S["P3"]["pass"] = bool(b.height and S["P3"]["frac_lor_pos"] >= 2 / 3 and S["P3"]["frac_p_gt_05"] >= 0.5)
    sig = D.filter(pl.col("z_raw") > 2)
    S["P4"] = {"n_raw_sig": sig.height, "n_periods": D.height,
               "median_f_stall": float(sig["f_stall"].median()), "median_f_lull": float(sig["f_lull"].median()),
               "median_f_field": float(sig["f_field"].median()),
               "median_f_mask_scaffold": float(sig["f_mask_scaffold"].median()),
               "median_f_mask_all": float(sig["f_mask_all"].median()),
               "median_f_mask_edge": float(sig["f_mask_edge"].median()), "median_f_mask_infra": float(sig["f_mask_infra"].median()),
               "n_sig_stall": int((D["z_stall"] > 2).sum()), "n_sig_lull": int((D["z_lull"] > 2).sum()),
               "n_sig_mask_scaffold": int((D["z_mask_scaffold"] > 2).sum()), "n_sig_mask_all": int((D["z_mask_all"] > 2).sum()),
               "frac_f_lull_ge_f_stall": float((sig["f_lull"] >= sig["f_stall"]).mean())}
    hc = C.filter(pl.col("goal_no").is_in(list(H02_MODES)))
    S["P4"]["h02_chunks"] = {"n": hc.height, "n_sig_raw": int((hc["z_raw"] > 2).sum()), "n_sig_lull": int((hc["z_lull"] > 2).sum()),
                             "n_sig_stall": int((hc["z_stall"] > 2).sum()), "n_sig_mask_scaffold": int((hc["z_mask_scaffold"] > 2).sum()),
                             "n_sig_mask_all": int((hc["z_mask_all"] > 2).sum())}
    S["P4"]["pass"] = (S["P4"]["median_f_stall"] >= 0.5 and S["P4"]["n_sig_stall"] <= S["P4"]["n_raw_sig"] / 2
                       and S["P4"]["frac_f_lull_ge_f_stall"] >= 2 / 3 and S["P4"]["h02_chunks"]["n_sig_stall"] <= 7)
    S["P4"]["pass_secondary_mask_scaffold"] = (S["P4"]["median_f_mask_scaffold"] >= 0.5
                                               and S["P4"]["n_sig_mask_scaffold"] <= S["P4"]["n_raw_sig"] / 2)
    S["P4"]["by_cause_median_f"] = {c: float(sig[f"f_drop_{c}"].median()) for c in L.CAUSES}
    if "z_trim" in D.columns and D["z_trim"].drop_nulls().len():  # round 1b: DQ8 design (trim before surrogates)
        S["P4"]["dq8"] = {"n_sig_trim": int((D["z_trim"] > 2).sum()), "n_sig_trim_stall": int((D["z_trim_stall"] > 2).sum()),
                          "n_sig_trim_scaffold": int((D["z_trim_scaffold"] > 2).sum()), "n_sig_trim_all": int((D["z_trim_all"] > 2).sum()),
                          "median_f_trim": float(sig["f_trim"].median()), "median_f_trim_stall": float(sig["f_trim_stall"].median()),
                          "median_f_trim_scaffold": float(sig["f_trim_scaffold"].median()),
                          "by_regime": (sig.group_by("regime").agg(pl.len(), pl.col("f_trim").median(), pl.col("f_trim_stall").median(),
                                                                   pl.col("f_trim_scaffold").median(), (pl.col("z_trim") > 2).sum().alias("n_sig_trim"),
                                                                   (pl.col("z_trim_scaffold") > 2).sum().alias("n_sig_trim_scaffold"))
                                        .sort("regime").to_dicts()),
                          "talk_median_tf_trim": float(sig["tf_trim"].median()) if "tf_trim" in sig.columns else None,
                          "talk_n_sig_trim": int((D["tz_trim"] > 2).sum()) if "tz_trim" in D.columns else None,
                          "talk_n_sig_raw": int((D["tz_raw"] > 2).sum())}
    S["P4"]["by_regime"] = (sig.group_by("regime").agg(pl.len(), pl.col("f_stall").median(), pl.col("f_mask_scaffold").median(),
                                                       pl.col("f_mask_all").median(), pl.col("f_lull").median()).sort("regime").to_dicts())
    if U.height:
        uu = U.filter(pl.col("raw_ratio") > 1)
        drop_stall = uu["raw_ratio"] - uu["stall_ratio"]
        drop_lull = uu["raw_ratio"] - uu["lull_ratio"]
        rel = drop_stall / drop_lull
        rel_drop = drop_stall / uu["raw_ratio"]
        rho = spearmanr(uu["stall_share"], rel_drop).statistic if uu.height > 3 else np.nan
        S["P5"] = {"n_units_mode": uu.height, "n_units": U.height, "median_stall_over_lull_drop": float(rel.median()),
                   "spearman_stallshare_reldrop": float(rho),
                   "n_above_raw": int((U["raw_ratio"] > 1).sum()), "n_above_lull": int((U["lull_ratio"] > 1).sum()),
                   "n_above_stall": int((U["stall_ratio"] > 1).sum()), "n_above_mask": int((U["mask_scaffold_ratio"] > 1).sum()),
                   "median_ratio_raw": float(uu["raw_ratio"].median()), "median_ratio_stall": float(uu["stall_ratio"].median()),
                   "median_ratio_lull": float(uu["lull_ratio"].median()), "median_ratio_mask": float(uu["mask_scaffold_ratio"].median())}
        S["P5"]["pass"] = S["P5"]["median_stall_over_lull_drop"] >= 0.5 and S["P5"]["spearman_stallshare_reldrop"] >= 0.6
    if U.height and "trim_bs_ratio" in U.columns:
        S["P5"]["dq8"] = {"n_above_trim_bs": int((U["trim_bs_ratio"] > 1).sum()), "n_above_trim_stall_bs": int((U["trim_stall_bs_ratio"] > 1).sum()),
                          "median_ratio_trim_bs": float(U["trim_bs_ratio"].median()), "median_ratio_trim_stall_bs": float(U["trim_stall_bs_ratio"].median()),
                          "n_units": U.height}
    rng = np.random.default_rng(6)
    S["P6"] = {}
    for v in ("raw", "stall", "mask_scaffold", "mask_all", "lull") + (("trim", "trim_scaffold") if "g_trim" in D.columns else ()):
        g3 = D.filter(pl.col("regime") == "III")[f"g_{v}"].drop_nulls().to_numpy()
        g1 = D.filter(pl.col("regime") == "I")[f"g_{v}"].drop_nulls().to_numpy()
        d = g3.mean() - g1.mean()
        bs = [rng.choice(g3, len(g3)).mean() - rng.choice(g1, len(g1)).mean() for _ in range(2000)]
        S["P6"][v] = {"diff": float(d), "lo": float(np.quantile(bs, 0.025)), "hi": float(np.quantile(bs, 0.975))}
    S["P6"]["shrink_stall"] = 1 - S["P6"]["stall"]["diff"] / S["P6"]["raw"]["diff"]
    S["P6"]["shrink_mask_scaffold"] = 1 - S["P6"]["mask_scaffold"]["diff"] / S["P6"]["raw"]["diff"]
    S["P6"]["pass"] = S["P6"]["shrink_stall"] >= 0.5
    big = D.filter(pl.col("E_raw") >= 0.05)
    ratio = (big["o6_g_pred"] - big["g_stall"]) / (big["g_raw"] - big["g_stall"])
    S["P7"] = {"n": big.height, "median_ratio": float(ratio.median()),
               "frac_within_2x": float(((ratio >= 0.5) & (ratio <= 2)).mean()), "note": "consistency check (Amendment 1)"}
    S["P7"]["pass"] = S["P7"]["frac_within_2x"] >= 2 / 3
    e = pl.read_parquet(L.ROOT / "data/processed/H19-loop-gain-collapse/estimates.parquet").filter(
        pl.col("method") == "H03.nx_fast").select("goal_no", pl.col("value").alias("nx"))
    j = D.join(e, on="goal_no", how="inner")
    S["P8"] = {"n": j.height}
    for v in ("raw", "stall", "mask_scaffold", "mask_all", "lull") + (("trim", "trim_scaffold") if "g_trim" in D.columns else ()):
        S["P8"][f"rho_{v}"] = float(spearmanr(j[f"g_{v}"], j["nx"], nan_policy="omit").statistic)
    S["P8"]["pass"] = S["P8"]["rho_stall"] > S["P8"]["rho_raw"] and S["P8"]["rho_stall"] > 0.3
    S["P8"]["pass_mask_scaffold"] = S["P8"]["rho_mask_scaffold"] > S["P8"]["rho_raw"] and S["P8"]["rho_mask_scaffold"] > 0.3
    ne = L.RES / "NE14/result.json"
    if ne.exists():
        n = json.loads(ne.read_text())
        dr = n["delta"]["raw"]["dE"]
        S["P9"] = {k: n["delta"][k] for k in ("raw", "stall", "mask_scaffold", "mask_all", "lull", *TRIMV) if k in n["delta"]}
        S["P9"]["pass"] = dr > 0 and n["delta"]["stall"]["dE"] <= dr / 2
        S["P9"]["pass_mask_scaffold"] = dr > 0 and n["delta"]["mask_scaffold"]["dE"] <= dr / 2
    return S, ok


NOTES = {
    "G02": "- 2026-10-04: only 2 non-holdout days with N = 3–4 present agents; z and f are noisy (read as descriptive).",
    "G03": "- 2026-10-04: 3 days, N = 4; raw gain not significant.",
    "G04": "- 2026-10-04: 2025-06-18 has a mid-day operator pause → resume pair (a 300-min village-off gap inside the calendar window); 2025-06-12 a 40-min edge gap.",
    "G06": "- 2026-10-04: 2025-06-29 (a Sunday) has a stray early event, so its window spans a 774-min operator-scheduled gap.",
    "G07": "- 2026-10-04: 2 days, N = 4; descriptive.",
    "G24": "- 2026-10-04: joint silences almost absent (0.1% of minutes); explained share rests on 1–2 minutes.",
    "G33": "- 2026-10-04: 3 days; a single joint-silence minute, so P2 is not informative.",
    "G36": "- 2026-10-04: computed as one H19 chunk across the 2026-03-24 regime boundary; the boundary itself is tested in `NE14/`.",
    "G37": "- 2026-10-04: 2026-03-31 has a stray early-morning event, so its calendar window contains a 513-min operator-scheduled gap (H16's outage); 99.6% of those minutes are `scheduled`.",
    "G38": "- 2026-10-04: 2026-04-16 has a 213-min operator-scheduled gap; λ₁ unit 38b loses its market mode under the stall filter.",
    "G51": "- 2026-10-04: 45 non-holdout days (the #51 tail is held out). Village-off gaps on 07-07, 07-10, 07-28 are operator-scheduled; three short K = 0 runs (07-09, 07-17, 07-24; 10–15 min) are unexplained. The residual gain survives every adjustment (z ≈ 23).",
}


def period_records(D, U):
    out = {}
    for r in D.iter_rows(named=True):
        p = r["period"]
        sig = r["z_raw"] is not None and r["z_raw"] > 2
        i_ok = r["expl"] is not None and r["expl"] >= 0.5 and r["expl"] > r["expl_surr"]
        i_bad = r["expl"] is not None and r["expl"] <= r["expl_surr"]
        ii_ok = (not sig) or (r["f_stall"] is not None and r["f_stall"] >= 0.5)
        ii_bad = sig and r["f_stall"] is not None and r["f_stall"] < 0.25
        if r["expl"] is None:
            verdict = "n/a"
        elif i_bad or ii_bad:
            verdict = "failed"
        elif i_ok and ii_ok:
            verdict = "supported"
        else:
            verdict = "mixed"
        causes = {c: r[f"cause_{c}"] or 0 for c in L.CAUSES}
        topc = max(causes, key=causes.get)
        lines = ["| Prediction | Observed | Null / reference | Verdict |", "| --- | --- | --- | --- |"]
        reg = r["regime"]
        lo, hi = (0.10, 0.40) if reg == "III" else (0.05, 0.30)
        lines.append(f"| P1 JS share in [{lo}, {hi}], above independence | {fmt(r['js'], 3)} | independent {fmt(r['js_exp'], 3)}; N1 surrogates {fmt(r['js_surr'], 3)} | "
                     f"{'✓' if (r['js'] is not None and lo <= r['js'] <= hi and r['js'] > r['js_exp']) else '✗'} |")
        lines.append(f"| P2 explained share ≥ 0.5 and above surrogate | {fmt(r['expl'])} (strict rule {fmt(r['expl_strict'])}) | surrogate {fmt(r['expl_surr'])} (q95 {fmt(r['expl_surr_q95'])}) | "
                     f"{'✓' if i_ok else '✗'} |")
        want = "pause" if reg == "III" else "edge or pause (wait)"
        good = (topc == "pause") if reg == "III" else (topc in ("edge", "pause"))
        lines.append(f"| P2 largest cause {want} | {topc} ({fmt(causes[topc])}); " +
                     ", ".join(f"{c} {fmt(causes[c])}" for c in L.CAUSES if c != topc) + f" | – | {'✓' if good else '✗'} |")
        lines.append(f"| P2 infra_error < 10% | {fmt(causes['infra_error'])} | – | {'✓' if causes['infra_error'] < 0.10 else '✗'} |")
        if r["voff_n"]:
            lines.append(f"| P2 village-off minutes ≥ 80% scheduled | {r['voff_n']} gaps, {r['voff_min']} min, {fmt(r['voff_sched'])} scheduled | – | "
                         f"{'✓' if (r['voff_sched'] or 0) >= 0.8 else '✗'} |")
        if (r["n_burst"] or 0) >= 20:
            lines.append(f"| P3 JS more likely after an infra burst | log OR {fmt(r['burst_lor'])} ({r['n_burst']} burst min) | within-block shift: p(>) {fmt(r['burst_p_gt'], 3)}, p(<) {fmt(r['burst_p_lt'], 3)} | "
                         f"{'✓' if (r['burst_lor'] or 0) > 0 else '✗'} |")
        lines.append(f"| P4 raw gain (H02/H19 g_eq) | g {fmt(r['g_raw'], 3)}, E {fmt(r['E_raw'], 3)}, z {fmt(r['z_raw'], 1)} | N1 joint shift | {'significant' if sig else 'not significant'} |")
        if sig:
            lines.append(f"| P4 f_infra (stall filter) ≥ 0.5 | E {fmt(r['E_stall'], 3)} (z {fmt(r['z_stall'], 1)}), f {fmt(r['f_stall'])} | lull filter f {fmt(r['f_lull'])} | "
                         f"{'✓' if (r['f_stall'] or 0) >= 0.5 else '✗'} |")
            lines.append(f"| (Amendment 2) agent-state conditioning | scaffold E {fmt(r['E_mask_scaffold'], 3)} (z {fmt(r['z_mask_scaffold'], 1)}), f {fmt(r['f_mask_scaffold'])}; all incl. pauses f {fmt(r['f_mask_all'])} | edge only f {fmt(r['f_mask_edge'])}; + infra f {fmt(r['f_mask_infra'])} | "
                         f"{'✓' if (r['f_mask_scaffold'] or 0) >= 0.5 else '✗'} |")
            lines.append(f"| per-cause drop (f) | " + ", ".join(f"{c} {fmt(r[f'f_drop_{c}'])}" for c in L.CAUSES) + " | – | descriptive |")
        if r["E_raw"] is not None and r["E_raw"] >= 0.05:
            pr = (r["o6_g_pred"] - r["g_stall"]) / (r["g_raw"] - r["g_stall"]) if (r["g_raw"] - r["g_stall"]) else np.nan
            lines.append(f"| P7 (consistency) O6 formula / observed Δg | {fmt(pr)} | within 2× | {'✓' if 0.5 <= pr <= 2 else '✗'} |")
        if r["tE_raw"] is not None:
            lines.append(f"| talk spin (secondary) | E raw {fmt(r['tE_raw'], 3)} (z {fmt(r['tz_raw'], 1)}); stall {fmt(r['tE_stall'], 3)}; scaffold-masked {fmt(r['tE_mask_scaffold'], 3)} | N1 | descriptive |")
        uu = U.filter(pl.col("period") == p) if U.height else U
        for x in uu.iter_rows(named=True):
            lines.append(f"| O5 λ₁/edge, unit {x['unit']} | raw {fmt(x['raw_ratio'])}, lull {fmt(x['lull_ratio'])}, stall {fmt(x['stall_ratio'])}, scaffold-masked {fmt(x['mask_scaffold_ratio'])} | cross-day surrogate edge (95%) | descriptive |")
        res = "\n".join(lines)
        res += (f"\n\nData: `data/processed/H38-platform-stalls/{p}/result.json`; minutes and runs in the shared "
                f"`stall_minutes.parquet` / `outages.parquet`.")
        sc = []
        sc.append(f"- **C:** explained share {'above' if i_ok else 'not above'} its N1 surrogate level; raw gain "
                  f"{'significant' if sig else 'not significant'} vs N1" + (f"; stall-adjusted z {fmt(r['z_stall'], 1)}, scaffold-masked z {fmt(r['z_mask_scaffold'], 1)}." if sig else "."))
        if r["voff_n"]:
            sc.append(f"- **G:** {r['voff_n']} village-off gap(s), {fmt(r['voff_sched'])} of their minutes inside the operator's pause → resume interval.")
        key = (f"JS {fmt(r['js'], 3)} (indep {fmt(r['js_exp'], 3)}); explained {fmt(r['expl'])} vs surr {fmt(r['expl_surr'])}; "
               f"top cause {topc}; raw g {fmt(r['g_raw'])} z {fmt(r['z_raw'], 1)}"
               + (f"; f_stall {fmt(r['f_stall'])}, f_scaffold {fmt(r['f_mask_scaffold'])}" if sig else ""))
        out[p] = {"verdict": verdict, "result_md": res, "scorecard_md": "\n".join(sc), "key_numbers": key,
                  "notes": [NOTES[p]] if p in NOTES else []}
    return out


def ne14_record():
    f = L.DATA / "NE14/result.json"
    if not f.exists():
        return
    n = json.loads(f.read_text())
    A, B, d = n["II"], n["III"], n["delta"]
    dr = d["raw"]["dE"]
    ok_s = dr > 0 and d["stall"]["dE"] <= dr / 2
    ok_m = dr > 0 and d["mask_scaffold"]["dE"] <= dr / 2
    verdict = "supported" if (ok_s and ok_m) else ("failed" if dr <= 0 or (not ok_s and not ok_m) else "mixed")
    rows = ["| Variant | E regime II (z) | E regime III (z) | Δ = III − II [95% CI, day bootstrap] |", "| --- | --- | --- | --- |"]
    for v in ("raw", "lull", "stall", "field", "mask_edge", "mask_infra", "mask_scaffold", "mask_all"):
        rows.append(f"| {v} | {fmt(A[v]['E'], 3)} ({fmt(A[v]['z'], 1)}) | {fmt(B[v]['E'], 3)} ({fmt(B[v]['z'], 1)}) | "
                    f"{d[v]['dE']:+.3f} [{d[v]['lo']:+.3f}, {d[v]['hi']:+.3f}] |")
    if "delta_no0331" in n:
        B2, d2 = n["III_no0331"], n["delta_no0331"]
        rows.append(f"| *sensitivity (post hoc): regime-III side without 2026-03-31 (513-min scheduled gap); stall share {fmt(B2['stall_share'], 3)}* | | | |")
        for v in ("raw", "stall", "mask_edge", "mask_scaffold", "mask_all"):
            rows.append(f"| {v} (no 03-31) | {fmt(A[v]['E'], 3)} ({fmt(A[v]['z'], 1)}) | {fmt(B2[v]['E'], 3)} ({fmt(B2[v]['z'], 1)}) | "
                        f"{d2[v]['dE']:+.3f} [{d2[v]['lo']:+.3f}, {d2[v]['hi']:+.3f}] |")
    res = (f"Regime II side: {len(A['days'])} days, N = {A['N']}, JS share {fmt(A['js_share'], 3)}, stall share {fmt(A['stall_share'], 3)}. "
           f"Regime III side: {len(B['days'])} days, N = {B['N']}, JS share {fmt(B['js_share'], 3)}, stall share {fmt(B['stall_share'], 3)}.\n\n"
           + "\n".join(rows) + "\n\n"
           f"Prediction: Δ_raw > 0 ({'✓' if dr > 0 else '✗'}); Δ_stall ≤ Δ_raw/2 ({'✓' if ok_s else '✗'}); "
           f"Δ_mask_scaffold ≤ Δ_raw/2 ({'✓' if ok_m else '✗'}). Data: `data/processed/H38-platform-stalls/NE14/result.json`.")
    sc = (f"- **E:** {'the raw jump is carried by scaffold states' if (ok_s or ok_m) else 'the adjusted jump keeps most of the raw jump'} "
          "(one boundary; 6 vs 7 days). Conditioning on day edges alone (`mask_edge`: off-schedule minutes dropped, not-started / "
          "finished agent-minutes imputed) already removes the jump, with or without 03-31: the regime-III rise is agents starting and "
          "stopping together, not consolidation or pause synchrony.")
    fp = L.HYP / "goalperiod-subhypotheses/NE14/README.md"
    t = fp.read_text()
    t = re.sub(r"\*\*Verdict:\*\* .*", f"**Verdict:** {verdict}", t, count=1)
    t = re.sub(r"## Result\n.*?\n## Scorecard", "## Result\n" + res + "\n\n## Scorecard", t, flags=re.S)
    t = re.sub(r"## Scorecard \(period-specific axes\)\n.*?\n## Notes", "## Scorecard (period-specific axes)\n" + sc + "\n\n## Notes", t, flags=re.S)
    fp.write_text(t)
    return verdict


def figures(D, U, ok):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    FIG.mkdir(parents=True, exist_ok=True)
    regc = {"I": "#4c78a8", "II": "#9c6ade", "III": "#e45756"}
    d = D.sort("goal_no")
    x = np.arange(d.height)
    # 1. decomposition per period
    fig, ax = plt.subplots(figsize=(10, 3.6))
    w = 0.2
    series = [("E_raw", "raw", "#8c8c8c"), ("E_lull", "lull filter", "#d08c2a"), ("E_stall", "stall filter", "#2a6fb0"),
              ("E_mask_scaffold", "scaffold-conditioned", "#5aa469")]
    for k, (c, lab, col) in enumerate(series):
        ax.bar(x + (k - 1.5) * w, d[c].fill_null(np.nan).to_numpy(), w, color=col, label=lab)
    sig = d["z_mask_scaffold"].fill_null(0).to_numpy() > 2
    ax.scatter(x[sig] + 1.5 * w, d["E_mask_scaffold"].to_numpy()[sig] + 0.015, marker="*", s=18, color="#2d6a3e", zorder=3)
    ax.axhline(0, color="k", lw=0.5)
    ax.set_xticks(x, [f"{p[1:]}" for p in d["period"]], fontsize=7)
    for t_, r in zip(ax.get_xticklabels(), d["regime"]):
        t_.set_color(regc.get(r[-3:] if r.endswith("III") else r, "k"))
    ax.set_ylabel("excess equal-time gain over N1")
    ax.set_xlabel("goal period (label color: regime I blue, II purple, III red); ★ scaffold-conditioned z > 2")
    ax.legend(fontsize=7, frameon=False, ncol=4)
    fig.tight_layout(); fig.savefig(FIG / f"decomposition{SUF}.png", dpi=150); plt.close(fig)
    # 2. cause composition
    fig, ax = plt.subplots(figsize=(10, 3.2))
    bottom = np.zeros(d.height)
    ccol = {"scheduled": "#6b6b6b", "edge": "#c9a227", "infra_error": "#d62728", "pause": "#1f77b4",
            "consolidation": "#2ca02c", "unexplained": "#e5e5e5"}
    for c in L.CAUSES:
        v = d[f"cause_{c}"].fill_null(0).to_numpy()
        ax.bar(x, v, 0.8, bottom=bottom, color=ccol[c], label=c, edgecolor="white", lw=0.3)
        bottom += v
    ax2 = ax.twinx()
    ax2.plot(x, d["js"].to_numpy(), "k.-", lw=0.8, ms=4, label="JS share")
    ax2.plot(x, d["js_exp"].to_numpy(), color="k", ls=":", lw=0.8, label="independent")
    ax2.set_ylabel("joint-silence share of minutes", fontsize=8)
    ax.set_xticks(x, [f"{p[1:]}" for p in d["period"]], fontsize=7)
    ax.set_ylabel("share of JS minutes by cause")
    ax.legend(fontsize=6.5, frameon=False, ncol=6, loc="upper center", bbox_to_anchor=(0.5, 1.13))
    ax2.legend(fontsize=6.5, frameon=False, loc="upper right")
    fig.tight_layout(); fig.savefig(FIG / f"causes{SUF}.png", dpi=150); plt.close(fig)
    # 3. summary observable: raw vs scaffold-conditioned excess per period
    fig, ax = plt.subplots(1, 2, figsize=(7.6, 3.2), gridspec_kw={"width_ratios": [1.15, 1]})
    for r in d.iter_rows(named=True):
        reg = "III" if r["regime"].endswith("III") else r["regime"]
        ax[0].scatter(r["E_raw"], r["E_mask_scaffold"], s=14 + 2 * r["days"] ** 0.5 * 4, color=regc[reg], alpha=0.8,
                      edgecolor="k" if (r["z_mask_scaffold"] or 0) > 2 else "none", lw=0.6)
    lim = [min(-0.05, float(np.nanmin(d["E_mask_scaffold"].to_numpy()))) - 0.02, float(np.nanmax(d["E_raw"].to_numpy())) + 0.03]
    ax[0].plot(lim, lim, "k-", lw=0.6); ax[0].plot(lim, [l / 2 for l in lim], "k--", lw=0.6)
    ax[0].axhline(0, color="k", lw=0.4); ax[0].axvline(0, color="k", lw=0.4)
    ax[0].set_xlabel("raw excess gain (H02/H19 g_eq − null)", fontsize=8)
    ax[0].set_ylabel("after conditioning on scaffold states", fontsize=8)
    ax[0].text(lim[1], lim[1] * 0.98, "no change", fontsize=6.5, ha="right", va="top")
    ax[0].text(lim[1], lim[1] / 2 * 0.95, "half removed", fontsize=6.5, ha="right", va="top")
    for reg, col in regc.items():
        ax[0].scatter([], [], color=col, s=14, label=f"regime {reg}")
    ax[0].legend(fontsize=6.5, frameon=False, loc="upper left")
    ax[0].set_title("per goal period (black edge: still z > 2)", fontsize=8)
    agg = ok.group_by(pl.when(pl.col("regime").str.ends_with("III")).then(pl.lit("III")).otherwise(pl.col("regime")).alias("reg")).agg(
        *[pl.col(f"cause_{c}").mean() for c in L.CAUSES]).sort("reg")
    bottom = np.zeros(agg.height)
    for c in L.CAUSES:
        v = agg[f"cause_{c}"].to_numpy()
        ax[1].bar(np.arange(agg.height), v, 0.6, bottom=bottom, color=ccol[c], label=c, edgecolor="white", lw=0.3)
        bottom += v
    ax[1].set_xticks(np.arange(agg.height), [f"regime {r}" for r in agg["reg"]], fontsize=8)
    ax[1].set_ylabel("share of joint-silence minutes", fontsize=8)
    ax[1].legend(fontsize=6, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3)
    ax[1].set_title("why everyone is quiet (mean over periods)", fontsize=8)
    fig.tight_layout(); fig.savefig(FIG / f"summary_obs{SUF}.png", dpi=170); fig.savefig(FIG / f"summary_obs{SUF}.pdf"); plt.close(fig)


def main():
    R = load()
    D = flat(R); U = units(R); C = chunks(R)
    D.write_parquet(L.RES / "period_table.parquet")
    if U.height:
        U.write_parquet(L.RES / "unit_table.parquet")
    C.write_parquet(L.RES / "chunk_table.parquet")
    S, ok = score(D, U, C)
    (L.RES / "outcomes.json").write_text(json.dumps(S, indent=1, default=float))
    recs = period_records(D, U)
    (L.RES / "period_results.json").write_text(json.dumps(recs, indent=1, default=float))
    v = ne14_record() if L.DATA_VERSION == "r1" else "(1b: README section written by hand)"
    figures(D, U, ok)
    with pl.Config(tbl_rows=60, tbl_cols=30, tbl_width_chars=300, float_precision=3):
        print(D.select("period", "regime", "js", "js_exp", "expl", "expl_surr", "g_raw", "z_raw", "E_raw", "E_lull", "E_stall",
                       "E_mask_scaffold", "E_mask_all", "z_stall", "z_mask_scaffold", "f_stall", "f_mask_scaffold", "f_mask_all"))
        if U.height:
            print(U.select("period", "unit", "stall_share", "raw_ratio", "lull_ratio", "stall_ratio", "mask_scaffold_ratio"))
    print(json.dumps(S, indent=1, default=float))
    print("NE14 verdict:", v)
    print("verdicts:", pl.Series([r["verdict"] for r in recs.values()]).value_counts().to_dicts())


if __name__ == "__main__":
    main()
