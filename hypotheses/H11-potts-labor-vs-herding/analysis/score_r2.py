"""Score H11 round 2 against the pre-registered rules (card, "Round 2"; amendment A1). Prints tables, writes
r2/results/score_r2.json.  Usage: uv run python hypotheses/H11-potts-labor-vs-herding/analysis/score_r2.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402

import r2lib as L  # noqa: E402

RES = HERE.parents[2] / "data/processed/H11-potts-labor-vs-herding/r2/results"


def f(x, d=2):
    return "–" if x is None else f"{x:+.{d}f}"


def ci(w, d=2):
    if not w or w.get("est") is None:
        return "n.e."
    if w.get("lo") is None:
        return f(w["est"], d)
    return f"{w['est']:+.{d}f} [{w['lo']:+.{d}f}, {w['hi']:+.{d}f}]"


def main():
    js = json.loads((RES / "real_r2.json").read_text())
    out = {"R1": {}, "R2": {}, "R3": {}}
    # ------------------------------------------------------------------ R1
    print("R1  unit  grp  n  alpha  alpha_PA  alpha_FE  lag-lead | replay fit / yule / uniform (top, effN)")
    by = {}
    for key, r in js["R1"].items():
        ch, u = key.split(":")
        rp = js["R1_replay"][key]
        row = {"ch": ch, "unit": u, "group": r["group"], "n": r["n_recruits"], "births": r["n_births"],
               "alpha": r["full"]["alpha"], "alpha_pa": r["pa"]["alpha"], "alpha_fe": r["fe"]["alpha"],
               "habit": r["full"]["habit"], "log_size": r["full"]["log_size"], "lag_minus_lead": r["lead"]["lag_minus_lead"],
               "lag": r["lead"]["lag"], "lead": r["lead"]["lead"],
               "replay": {k: {s: rp[k][s]["inside"] for s in ("top_share", "eff_n", "shared_share")} for k in ("fit", "yule", "uniform")},
               "replay_pct": {k: {s: rp[k][s]["pct"] for s in ("top_share", "eff_n", "shared_share")} for k in ("fit", "yule", "uniform")},
               "observed": rp["observed"]}
        by[key] = row
        rr = row["replay"]
        print(f"{ch:4s} {u:4s} {r['group'][:3]} {row['n']:4d} {ci(row['alpha'])}  {f(row['alpha_pa']['est'])}  {ci(row['alpha_fe'])}  "
              f"{ci(row['lag_minus_lead'])} | " + " / ".join(f"{int(rr[k]['top_share'])}{int(rr[k]['eff_n'])}{int(rr[k]['shared_share'])}" for k in ("fit", "yule", "uniform")))
    out["R1"]["rows"] = by
    for ch in ("work", "att"):
        for grp in ("shared", "own", "all"):
            rows = [r for r in by.values() if r["ch"] == ch and (grp == "all" or r["group"] == grp)]
            if not rows:
                continue
            k = len(rows)
            sig = sum(1 for r in rows if r["alpha"]["lo"] is not None and r["alpha"]["lo"] > 0)
            pool = L.dl_pool([r["alpha"]["est"] for r in rows], [r["alpha"]["se"] for r in rows])
            pool_fe = L.dl_pool([r["alpha_fe"]["est"] for r in rows], [r["alpha_fe"]["se"] for r in rows])
            pool_ll = L.dl_pool([r["lag_minus_lead"]["est"] for r in rows], [r["lag_minus_lead"]["se"] for r in rows])
            ci1 = sum(1 for r in rows if r["alpha"]["lo"] is not None and r["alpha"]["lo"] <= 1 <= r["alpha"]["hi"])
            fe_lt = sum(1 for r in rows if r["alpha_fe"]["est"] < r["alpha"]["est"])
            fe_sig = sum(1 for r in rows if r["alpha_fe"]["lo"] is not None and r["alpha_fe"]["lo"] > 0)
            ll_inc0 = sum(1 for r in rows if r["lag_minus_lead"]["lo"] <= 0 <= r["lag_minus_lead"]["hi"])
            ll_pos = sum(1 for r in rows if r["lag_minus_lead"]["lo"] > 0)
            ll_neg = sum(1 for r in rows if r["lag_minus_lead"]["hi"] < 0)
            both = sum(1 for r in rows if (r["alpha_fe"]["lo"] or -1) > 0 and (r["lag_minus_lead"]["lo"] or -1) > 0)
            rep = {kern: {"both": sum(1 for r in rows if r["replay"][kern]["top_share"] and r["replay"][kern]["eff_n"]),
                          "top": sum(1 for r in rows if r["replay"][kern]["top_share"]),
                          "effn": sum(1 for r in rows if r["replay"][kern]["eff_n"]),
                          "shared": sum(1 for r in rows if r["replay"][kern]["shared_share"]),
                          "top_above": sum(1 for r in rows if r["replay_pct"][kern]["top_share"] > 0.95)}
                   for kern in ("fit", "yule", "uniform")}
            s = {"k": k, "alpha_sig_pos": sig, "alpha_pool": pool, "alpha_fe_pool": pool_fe, "lag_lead_pool": pool_ll,
                 "ci_contains_1": ci1, "fe_lt_alpha": fe_lt, "fe_sig_pos": fe_sig, "lag_lead_ci_inc0": ll_inc0,
                 "lag_gt_lead": ll_pos, "lead_gt_lag": ll_neg, "fe_and_lag_pos": both, "replay": rep}
            out["R1"][f"{ch}:{grp}"] = s
            print(f"  {ch}:{grp} k={k} alpha>0 {sig}; pooled {ci(pool)}; CI∋1 {ci1}; FE<alpha {fe_lt}, FE>0 {fe_sig} (pool {ci(pool_fe)}); "
                  f"lag-lead: inc0 {ll_inc0}, lag>lead {ll_pos}, lead>lag {ll_neg} (pool {ci(pool_ll)}); FE&lag {both}; replay {rep}")
    # ------------------------------------------------------------------ R2
    print("\nR2 unit grp | dLL_CM [CI] | OR_M|act  OR_C|M | Mread-Munread  Mread-Mlead  C-Clead | events")
    r2rows = {}
    for key, r in js["R2"].items():
        ch, u = key.split(":")
        jt = r["joint"]
        hd = r["heldout"]
        mh = r["mh"]
        row = {"ch": ch, "unit": u, "group": r["group"], "dll": hd, "or_m": mh["OR_M_given_act"], "or_c": mh["OR_C_given_M"],
               "ru": jt["M_read-M_unread"], "rl": jt["M_read-M_lead"], "cl": jt["C-C_lead"], "events": jt["_events"],
               "b": {k: jt[k] for k in ("C", "C_lead", "M_read", "M_unread", "M_lead", "habit", "log_size")},
               "single": {"C": r["C"]["C"], "M": r["M"]["M_read"]}}
        r2rows[key] = row
        dl = "–" if hd.get("dll") is None else f"{hd['dll']:+.3f} [{hd['lo']:+.3f},{hd['hi']:+.3f}]"
        o1 = row["or_m"].get("or")
        o2 = row["or_c"].get("or")
        print(f"{ch:4s} {u:4s} {r['group'][:3]} | {dl} | {o1 and round(o1, 2)}  {o2 and round(o2, 2)} | {ci(row['ru'])}  {ci(row['rl'])}  "
              f"{ci(row['cl'])} | {jt['_events']}")
    out["R2"]["rows"] = r2rows
    for ch in ("work", "att"):
        for grp in ("shared", "own", "all"):
            rows = [r for r in r2rows.values() if r["ch"] == ch and (grp == "all" or r["group"] == grp)]
            if not rows:
                continue
            dl = [r for r in rows if r["dll"].get("dll") is not None]
            s = {"k": len(rows), "k_dll": len(dl),
                 "dll_pos": sum(1 for r in dl if r["dll"]["dll"] > 0),
                 "dll_pos_ci": sum(1 for r in dl if r["dll"]["lo"] > 0), "dll_neg_ci": sum(1 for r in dl if r["dll"]["hi"] < 0),
                 "dll_pool": L.dl_pool([r["dll"]["dll"] for r in dl], [r["dll"]["se"] for r in dl]),
                 "orc_gt_orm": sum(1 for r in rows if r["or_c"].get("or") and r["or_m"].get("or") and r["or_c"]["or"] > r["or_m"]["or"]),
                 "k_or": sum(1 for r in rows if r["or_c"].get("or") and r["or_m"].get("or"))}
            for nm in ("ru", "rl", "cl"):
                est = [r[nm] for r in rows if r[nm].get("est") is not None]
                s[nm + "_pool"] = L.dl_pool([w["est"] for w in est], [w["se"] for w in est])
                s[nm + "_k"] = len(est)
                s[nm + "_pos"] = sum(1 for w in est if w.get("lo") is not None and w["lo"] > 0)
                s[nm + "_neg"] = sum(1 for w in est if w.get("hi") is not None and w["hi"] < 0)
            for nm in ("C", "C_lead", "M_read", "M_unread", "M_lead"):
                est = [r["b"][nm] for r in rows]
                s["b_" + nm + "_pool"] = L.dl_pool([w["est"] for w in est], [w["se"] for w in est])
            # pooled MH log OR
            for nm in ("or_m", "or_c"):
                est = [r[nm] for r in rows if r[nm].get("or")]
                s[nm + "_pool"] = L.dl_pool([w["log_or"] for w in est], [w["se_log"] for w in est])
            out["R2"][f"{ch}:{grp}"] = s
            print(f"  {ch}:{grp} k={s['k']} dLL>0 {s['dll_pos']}/{s['k_dll']} (CI>0 {s['dll_pos_ci']}, CI<0 {s['dll_neg_ci']}; pool {ci(s['dll_pool'], 3)}); "
                  f"OR_C>OR_M {s['orc_gt_orm']}/{s['k_or']} (logOR pools M {ci(s['or_m_pool'])}, C {ci(s['or_c_pool'])}); "
                  f"read-unread {ci(s['ru_pool'])} k{s['ru_k']}; read-lead {ci(s['rl_pool'])} k{s['rl_k']} (+{s['rl_pos']}/-{s['rl_neg']}); "
                  f"C-Clead {ci(s['cl_pool'])} k{s['cl_k']} (+{s['cl_pos']}/-{s['cl_neg']})")
            print("     pooled betas:", {nm: ci(s['b_' + nm + '_pool']) for nm in ("C", "C_lead", "M_read", "M_unread", "M_lead")})
    # R2d paths (work recruits)
    import polars as pl
    j = pl.read_parquet(RES.parent / "joins_work.parquet").filter(pl.col("kind") == "recruit")
    pth = j.group_by("unit").agg(pl.len().alias("n"), (pl.col("p_read") & ~pl.col("p_seen")).sum().alias("read_only"),
                                 (pl.col("p_seen") & ~pl.col("p_read")).sum().alias("seen_only"),
                                 (pl.col("p_read") & pl.col("p_seen")).sum().alias("both"),
                                 (~pl.col("p_read") & ~pl.col("p_seen")).sum().alias("neither"),
                                 (pl.col("p_first") == "read").sum().alias("read_first"),
                                 (pl.col("p_first") == "seen").sum().alias("seen_first"))
    tot = pth.select(pl.exclude("unit").sum()).to_dicts()[0]
    out["R2"]["paths"] = {"by_unit": pth.to_dicts(), "total": tot}
    print("\nR2d paths (work recruits):", tot)
    # ------------------------------------------------------------------ R3
    print("\nR3 unit grp | logRR_herd commits [CI] | landed | deployed | matched | theta [CI] | n_herd/n_solo")
    r3rows = {}
    for u, r in js["R3"].items():
        c, l_, d = r["n_commit"], r["n_land"], r["n_deploy"]
        if not c.get("testable") and not r["theta"].get("testable"):
            continue
        row = {"unit": u, "group": r["group"], "commit": c.get("log_RR_herd"), "land": l_.get("log_RR_herd"),
               "deploy": d.get("log_RR_herd"), "pair": c.get("log_RR_pair"), "matched": c.get("matched"), "theta": r["theta"].get("theta"),
               "n_herd": c.get("n_herd"), "n_solo": c.get("n_solo"), "by_class": r["by_class"], "testable_rr": c.get("testable")}
        r3rows[u] = row
        print(f"{u:4s} {r['group'][:3]} | {ci(row['commit'])} | {ci(row['land'])} | {ci(row['deploy'])} | "
              f"{row['matched'] and round(row['matched']['mean_log_ratio'], 2)} | {ci(row['theta'])} | {row['n_herd']}/{row['n_solo']}")
    out["R3"]["rows"] = r3rows
    for grp in ("shared", "own", "all"):
        rows = [r for r in r3rows.values() if grp == "all" or r["group"] == grp]
        s = {}
        for nm in ("commit", "land", "deploy"):
            est = [r[nm] for r in rows if r.get(nm) and r[nm].get("est") is not None]
            s[nm + "_pool"] = L.dl_pool([w["est"] for w in est], [w["se"] for w in est])
            s[nm + "_k"] = len(est)
            s[nm + "_neg"] = sum(1 for w in est if w.get("sig") and w["est"] < 0)
            s[nm + "_pos"] = sum(1 for w in est if w.get("sig") and w["est"] > 0)
        th = [r["theta"] for r in rows if r.get("theta")]
        s["theta_k"] = len(th)
        s["theta_lt1"] = sum(1 for w in th if w["hi"] < 1)
        s["theta_gt1"] = sum(1 for w in th if w["lo"] > 1)
        s["theta_pool"] = L.dl_pool([w["est"] for w in th], [w["se"] for w in th])
        mt = [r["matched"] for r in rows if r.get("matched")]
        s["matched_pool"] = L.dl_pool([w["mean_log_ratio"] for w in mt], [w["se"] for w in mt])
        out["R3"][grp] = s
        print(f"  {grp}: logRR commits {ci(s['commit_pool'])} k{s['commit_k']} (-{s['commit_neg']}/+{s['commit_pos']}); landed {ci(s['land_pool'])}; "
              f"deployed {ci(s['deploy_pool'])}; matched {ci(s['matched_pool'])}; theta {ci(s['theta_pool'])} k{s['theta_k']} (<1: {s['theta_lt1']}, >1: {s['theta_gt1']})")
    out["R3c"] = js["R3c"]
    print("\nR3c:", js["R3c"]["spearman"], js["R3c"]["mannwhitney_own_vs_shared"])
    (RES / "score_r2.json").write_text(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
