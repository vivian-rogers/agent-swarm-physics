"""H15 round 1b (improved data, 2026-10-04): analyses added on top of the rerun of the round-1 pipeline.

Run after `H15_ROUND=r1b` build.py / choose_v.py / run_scrambles.py:
    H15_ROUND=r1b uv run python hypotheses/H15-semantic-information-scrambles/analysis/r1b_extra.py

Writes data/processed/H15-semantic-information-scrambles/r1b/r1b_extra.json and figures/r1b/F_r1b.pdf.
  AS     artifact-store scramble (HH261, P11): repo switches vs continuation commit days, O1 estimator (kal)
  CTX    forced vs voluntary erasure on ledger calls: relative dips for work commits, real failures, write evidence;
         cost of the cap as a share of a forced segment's output
  NE41   native: stored memory dose at the wipe vs the work dip (Spearman per period, dose terciles)
  NE16   native: forced-erasure dip before (36b) vs after (36c) the memory-update fix
  NE29   native: incumbents' work commits on the day Claude 3.7 Sonnet retired, vs a day-contrast null (#30-#44)
Non-holdout only (refuse_holdout on every table). No text is read.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

os.environ.setdefault("H15_ROUND", "r1b")
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h15common import FIG, OUT, ROUND, SEED, SH, WORK_FROM, calendar_nonholdout, refuse_holdout, write_provenance  # noqa: E402
from h15lib import (Panel, agent_mu, autocov_params, dl_meta, event_delta, period_test, residual_panel,  # noqa: E402
                    spearman, unit_placebo_pool)

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

assert ROUND == "r1b", "r1b_extra.py runs on the round-1b tables only (H15_ROUND=r1b)"
T0 = time.time()
rng = np.random.default_rng(SEED + 11)


def log(m):
    print(f"[{time.time() - T0:6.1f}s] {m}", flush=True)


ad = pl.read_parquet(OUT / "agent_day.parquet")
cat = pl.read_parquet(OUT / "scramble_catalog.parquet")
sw = pl.read_parquet(OUT / "artifact_switches.parquet")
ce = pl.read_parquet(OUT / "consolidations.parquet")
calls = pl.read_parquet(OUT / "calls.parquet")
res1b = json.loads((OUT / "results.json").read_text())
for t, nm in ((ad, "agent_day"), (cat, "catalog"), (sw, "switches"), (ce, "consolidations"), (calls, "calls")):
    refuse_holdout(t["pt_date"].unique().to_list(), nm)
cal = calendar_nonholdout().sort("pt_date")
unit_days = {u: sorted(g["pt_date"].to_list()) for (u,), g in cal.group_by(["unit"])}
units = sorted(unit_days, key=lambda u: (int(re.match(r"\d+", u).group()), u))
regime_of = {u: str(cal.filter(pl.col("unit") == u)["regime"][0]) for u in units}
OUTJ = {}


def ukey(u):
    return (int(re.match(r"\d+", u).group()), u)


# ============================================================================ AS: artifact-store scramble (P11)
def run_as(V: str) -> dict:
    rp = residual_panel(ad, V)
    panel = Panel(rp, unit_days, "u")
    evidx: dict = {}
    for e in cat.iter_rows(named=True):
        u = e["unit"]
        if u in unit_days and e["pt_date"] in unit_days[u]:
            evidx.setdefault((int(e["agent"]), u), []).append(unit_days[u].index(e["pt_date"]))
    for e in sw.filter(pl.col("type") == "AS").iter_rows(named=True):
        u = e["unit"]
        if u in unit_days and e["pt_date"] in unit_days[u]:
            evidx.setdefault((int(e["agent"]), u), []).append(unit_days[u].index(e["pt_date"]))
    prm = {r: autocov_params(panel, [u for u in units if regime_of[u] == r], exclude=evidx) for r in ("I", "II", "III")}
    vals = {"AS": {}, "CONT": {}}
    for e in sw.iter_rows(named=True):
        a, u = int(e["agent"]), e["unit"]
        x = panel.get(a, u)
        if x is None or e["pt_date"] not in unit_days.get(u, []):
            continue
        i0 = unit_days[u].index(e["pt_date"])
        mine = evidx.get((a, u), [])
        r = event_delta(x, i0, [1, 2], agent_mu(x, mine), prm[regime_of[u]])
        if r is None:
            continue
        vals[e["type"]].setdefault(u, []).append({**r, "dose": e["dose"], "agent": a, "pt_date": e["pt_date"]})
    per = {}
    cache = {}
    for u in sorted(vals["AS"], key=ukey):
        ev = vals["AS"][u]
        cont = vals["CONT"].get(u, [])
        if len(ev) < 1 or len(cont) < 5:
            continue
        cn = [c["kal"] for c in cont]
        t_match = period_test([x["kal"] for x in ev], [cn] * len(ev), rng=rng)
        pool = unit_placebo_pool(panel, u, evidx, [1, 2], prm[regime_of[u]], cache)
        t_pool = period_test([x["kal"] for x in ev], [[p["kal"] for p in pool]] * len(ev), rng=rng)
        t_pre = period_test([x["pretrend"] for x in ev], [[c["pretrend"] for c in cont]] * len(ev), rng=rng)
        per[u] = {"n_as": len(ev), "n_cont": len(cont), "matched": t_match, "unit_pool": t_pool, "pretrend_vs_cont": t_pre,
                  "mean_dose": float(np.mean([x["dose"] for x in ev]))}
    ts = [(u, p["matched"]) for u, p in per.items() if p["matched"]]
    meta = dl_meta([t["effect"] for _, t in ts], [t["null_sd"] for _, t in ts])
    tsp = [p["unit_pool"] for p in per.values() if p["unit_pool"]]
    meta_pool = dl_meta([t["effect"] for t in tsp], [t["null_sd"] for t in tsp])
    tpr = [p["pretrend_vs_cont"] for p in per.values() if p["pretrend_vs_cont"]]
    meta_pre = dl_meta([t["effect"] for t in tpr], [t["null_sd"] for t in tpr])
    allv = [x for u in vals["AS"] for x in vals["AS"][u]]
    dose_rho = spearman([x["dose"] for x in allv], [x["kal"] for x in allv])
    ml = res1b["by_V"][V]["types"]["ML"]
    return {"per_unit": per, "meta_matched": meta, "meta_unit_pool": meta_pool, "meta_pretrend_vs_cont": meta_pre,
            "n_events": int(sum(p["n_as"] for p in per.values())), "dose_rho": dose_rho,
            "kappa_AS": (meta["mu"] / float(np.mean([x["dose"] for x in allv]))) if meta and allv else None,
            "ML_meta_kal": ml["meta"]["kal"], "kappa_ML": ml["kappa"]}


OUTJ["AS"] = {}
for V in ("V_out", "V_files", "V_eng", "V_rel", "V_prog"):
    OUTJ["AS"][V] = run_as(V)
    m = OUTJ["AS"][V]["meta_matched"]
    log(f"AS {V}: {m and round(m['mu'], 3)} z {m and round(m['z'], 2)} k {m and m['k']}")


# ============================================================================ CTX: ledger-timed erasure dips
def ratio_boot(post, far, cl, B=1000):
    uu, inv = np.unique(cl, return_inverse=True)
    sp = np.bincount(inv, weights=post)
    sf = np.bincount(inv, weights=far)
    est = sp.sum() / max(sf.sum(), 1e-12) - 1
    bs = np.empty(B)
    for b in range(B):
        ii = rng.integers(0, len(uu), len(uu))
        bs[b] = sp[ii].sum() / max(sf[ii].sum(), 1e-12) - 1
    return {"rel_dip": float(est), "lo": float(np.percentile(bs, 2.5)), "hi": float(np.percentile(bs, 97.5)),
            "se": float(bs.std(ddof=1)), "n": int(len(post)), "clusters": int(len(uu))}


cc = ce.filter(pl.col("kind").is_in(["CF", "CV"]) & (pl.col("n_far") >= 10) & (pl.col("n_post") >= 10)).with_columns(
    (pl.col("agent").cast(pl.Utf8) + "_" + pl.col("pt_date")).alias("cl"))
ctx = {}
for u in sorted(cc["unit"].unique().to_list(), key=ukey):
    g = cc.filter(pl.col("unit") == u)
    r = {}
    for kind in ("CF", "CV"):
        gg = g.filter(pl.col("kind") == kind)
        if gg.height < 20:
            continue
        r[kind] = {}
        for o in ("w", "e", "v"):
            r[kind][o] = ratio_boot(gg[f"{o}_post"].to_numpy(), gg[f"{o}_far"].to_numpy(), gg["cl"].to_numpy())
            r[kind][o]["far"] = float(gg[f"{o}_far"].mean())
            r[kind][o]["post"] = float(gg[f"{o}_post"].mean())
    # cost of the cap: work lost over the 10 post calls per forced erasure, as a share of a 40-call segment's work
    if "CF" in r:
        gg = g.filter(pl.col("kind") == "CF")
        lost = (gg["w_far"] - gg["w_post"]).mean() * 10
        seg = gg["w_base"].mean() * 40
        r["cap_cost_share"] = float(lost / seg) if seg and seg > 0 else None
    ctx[u] = r
OUTJ["CTX"] = ctx
for o in ("w", "e", "v"):
    for kind in ("CF", "CV"):
        ts = [r[kind][o] for r in ctx.values() if kind in r]
        OUTJ.setdefault("CTX_meta", {})[f"{kind}_{o}"] = dl_meta([t["rel_dip"] for t in ts], [t["se"] for t in ts])
        OUTJ["CTX_meta"][f"{kind}_{o}_below0"] = int(sum(t["hi"] < 0 for t in ts))
        OUTJ["CTX_meta"][f"{kind}_{o}_k"] = len(ts)
OUTJ["CTX_meta"]["cap_cost_share"] = {u: r.get("cap_cost_share") for u, r in ctx.items()}
log("ctx done")

# ============================================================================ NE41 native: memory dose at the wipe
cf = cc.filter((pl.col("kind") == "CF") & pl.col("stored_dose").is_not_null()).with_columns(
    (pl.col("w_post") - pl.col("w_far")).alias("dw"), (pl.col("v_post") - pl.col("v_far")).alias("dv"))
ne41 = {"per_unit": {}}
for u in sorted(cf["unit"].unique().to_list(), key=ukey):
    g = cf.filter(pl.col("unit") == u)
    rho, n = spearman(g["stored_dose"].to_numpy(), g["dw"].to_numpy())
    rhov, _ = spearman(g["stored_dose"].to_numpy(), g["dv"].to_numpy())
    ne41["per_unit"][u] = {"rho_work": rho, "rho_wev": rhov, "n": n, "mean_dose": float(g["stored_dose"].mean()),
                           "share_dose0": float((g["stored_dose"] == 0).mean())}
rho, n = spearman(cf["stored_dose"].to_numpy(), cf["dw"].to_numpy())
rhov, _ = spearman(cf["stored_dose"].to_numpy(), cf["dv"].to_numpy())
ne41["pooled_rho_work"], ne41["pooled_rho_wev"], ne41["n"] = rho, rhov, n
big = [u for u, r in ne41["per_unit"].items() if r["n"] >= 300]
ne41["max_abs_rho_big"] = float(max(abs(ne41["per_unit"][u]["rho_work"]) for u in big)) if big else None
# terciles of stored dose within unit (units with >= 100 forced erasures)
okU = [u for u, r in ne41["per_unit"].items() if r["n"] >= 100]
cfu = cf.filter(pl.col("unit").is_in(okU)).with_columns(
    (pl.col("stored_dose").rank("ordinal").over("unit") / pl.len().over("unit")).alias("q"))
lo_t, hi_t = cfu.filter(pl.col("q") <= 1 / 3), cfu.filter(pl.col("q") > 2 / 3)
rl = ratio_boot(lo_t["w_post"].to_numpy(), lo_t["w_far"].to_numpy(), lo_t["cl"].to_numpy())
rh = ratio_boot(hi_t["w_post"].to_numpy(), hi_t["w_far"].to_numpy(), hi_t["cl"].to_numpy())
dd = []
for _ in range(1000):
    a = lo_t.sample(lo_t.height, with_replacement=True, seed=int(rng.integers(1 << 30)))
    b = hi_t.sample(hi_t.height, with_replacement=True, seed=int(rng.integers(1 << 30)))
    dd.append((b["w_post"].sum() / b["w_far"].sum() - 1) - (a["w_post"].sum() / a["w_far"].sum() - 1))
ne41["tercile"] = {"low": rl, "high": rh, "high_minus_low": float(rh["rel_dip"] - rl["rel_dip"]),
                   "ci": [float(np.percentile(dd, 2.5)), float(np.percentile(dd, 97.5))],
                   "dose_low_mean": float(lo_t["stored_dose"].mean()), "dose_high_mean": float(hi_t["stored_dose"].mean()),
                   "units": okU}
cfm = OUTJ["CTX_meta"]["CF_w"]
ne41["N1"] = bool(abs(rho) <= 0.10 and (ne41["max_abs_rho_big"] is None or ne41["max_abs_rho_big"] < 0.15))
ne41["N2"] = bool(abs(ne41["tercile"]["high_minus_low"]) <= 0.10 and ne41["tercile"]["ci"][0] <= 0 <= ne41["tercile"]["ci"][1])
ne41["N3"] = bool(OUTJ["CTX_meta"]["CF_w_below0"] >= 7 and cfm and -0.50 <= cfm["mu"] <= -0.25)
OUTJ["NE41"] = ne41
log(f"NE41 rho {rho:.3f}; tercile diff {ne41['tercile']['high_minus_low']:+.3f} {ne41['tercile']['ci']}")

# ============================================================================ NE16 native: 36b vs 36c
c36 = ce.filter(pl.col("goal_no") == 36).with_columns(
    pl.when(pl.col("pt_date") < "2026-03-26").then(pl.lit("36b")).otherwise(pl.lit("36c")).alias("u36"),
    (pl.col("agent").cast(pl.Utf8) + "_" + pl.col("pt_date")).alias("cl"))
ne16 = {}
for side in ("36b", "36c"):
    g = c36.filter((pl.col("u36") == side) & (pl.col("kind") == "CF"))
    gw = g.filter((pl.col("n_far") >= 10) & (pl.col("n_post") >= 10))
    ne16[side] = {"n_forced": g.height, "n_window": gw.height,
                  "share_mem_added": float((g["lines_added"].fill_null(0) > 0).mean()) if g.height else None,
                  "mean_dose": float(g["stored_dose"].mean()) if g.height else None,
                  "work": ratio_boot(gw["w_post"].to_numpy(), gw["w_far"].to_numpy(), gw["cl"].to_numpy()) if gw.height >= 20 else None,
                  "wev": ratio_boot(gw["v_post"].to_numpy(), gw["v_far"].to_numpy(), gw["cl"].to_numpy()) if gw.height >= 20 else None,
                  "fail": ratio_boot(gw["e_post"].to_numpy(), gw["e_far"].to_numpy(), gw["cl"].to_numpy()) if gw.height >= 20 else None}


def diff_boot(col_post, col_far, B=1000):
    a = c36.filter((pl.col("u36") == "36b") & (pl.col("kind") == "CF") & (pl.col("n_far") >= 10) & (pl.col("n_post") >= 10))
    b = c36.filter((pl.col("u36") == "36c") & (pl.col("kind") == "CF") & (pl.col("n_far") >= 10) & (pl.col("n_post") >= 10))

    def agg(g):
        s = g.group_by("cl").agg(pl.col(col_post).sum().alias("p"), pl.col(col_far).sum().alias("f"))
        return s["p"].to_numpy(), s["f"].to_numpy()
    pa, fa = agg(a)
    pb, fb = agg(b)
    est = (pb.sum() / fb.sum() - 1) - (pa.sum() / fa.sum() - 1)
    bs = []
    for _ in range(B):
        ia, ib = rng.integers(0, len(pa), len(pa)), rng.integers(0, len(pb), len(pb))
        bs.append((pb[ib].sum() / max(fb[ib].sum(), 1e-12) - 1) - (pa[ia].sum() / max(fa[ia].sum(), 1e-12) - 1))
    return {"diff_c_minus_b": float(est), "lo": float(np.percentile(bs, 2.5)), "hi": float(np.percentile(bs, 97.5))}


ne16["diff_wev"] = diff_boot("v_post", "v_far")
ne16["diff_work"] = diff_boot("w_post", "w_far")
ne16["M"] = bool(ne16["36c"]["mean_dose"] is not None and ne16["36b"]["mean_dose"] is not None
                 and ne16["36c"]["mean_dose"] > ne16["36b"]["mean_dose"])
ne16["N1"] = bool(abs(ne16["diff_wev"]["diff_c_minus_b"]) <= 0.15 and ne16["diff_wev"]["lo"] <= 0 <= ne16["diff_wev"]["hi"])
ne16["against"] = bool(ne16["diff_wev"]["diff_c_minus_b"] > 0.15 and ne16["diff_wev"]["lo"] > 0)
OUTJ["NE16"] = ne16
log(f"NE16 dose {ne16['36b']['mean_dose']} -> {ne16['36c']['mean_dose']}; diff wev {ne16['diff_wev']}")

# ============================================================================ NE29 native: Claude 3.7 Sonnet retires
wc = (pl.read_parquet(SH / "work_commits.parquet",
                      columns=["t", "pt_date", "author_agent", "author_kind", "canonical", "imported", "automated", "holdout", "repo",
                               "goal_no"])
      .filter(pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind") == "agent") & ~pl.col("automated")
              & ~pl.col("holdout") & (pl.col("pt_date") >= WORK_FROM)))
refuse_holdout(wc["pt_date"].unique().to_list(), "work commits")
RET, NEWC = 0, None
roster = pl.read_parquet(SH / "roster.parquet")
NEWC = roster.filter(pl.col("joined") == "2026-02-18")["agent"].to_list()
act = ad.filter(pl.col("goal_no").is_between(30, 44)).select("pt_date", "agent", "goal_no", "unit")
wd = wc.group_by("pt_date", pl.col("author_agent").alias("agent")).agg(pl.len().alias("c"))
act = act.join(wd, on=["pt_date", "agent"], how="left").with_columns(pl.col("c").fill_null(0))
d31 = ["2026-02-16", "2026-02-17", "2026-02-18", "2026-02-19"]
inc = set(act.filter(pl.col("pt_date").is_in(d31)).group_by("agent").agg(pl.len().alias("n"))
          .filter(pl.col("n") == 4)["agent"].to_list()) - {RET} - set(NEWC)
day_val = {}
for d in d31:
    g = act.filter((pl.col("pt_date") == d) & pl.col("agent").is_in(list(inc)))
    day_val[d] = float(np.log1p(g["c"].mean()))
obs = day_val["2026-02-19"] - np.mean([day_val[d] for d in d31[:3]])
# null: same contrast for every day of #30-#44 (non-holdout) with three previous active days in the same unit
sw_day = act.group_by("pt_date", "unit").agg(pl.col("c").mean().alias("m")).sort("pt_date")
null = []
for u, g in sw_day.group_by("unit"):
    g = g.sort("pt_date")
    v = np.log1p(g["m"].to_numpy())
    ds = g["pt_date"].to_list()
    for i in range(3, len(v)):
        if ds[i] == "2026-02-19":
            continue
        null.append(float(v[i] - v[i - 3:i].mean()))
null = np.array(null)
z = float((obs - null.mean()) / null.std(ddof=1))
pre31 = wc.filter(pl.col("goal_no").is_in([30, 31]) & (pl.col("pt_date") < "2026-02-19"))
share_ret = float((pre31["author_agent"] == RET).mean())
ret_repos = set(pre31.filter(pl.col("author_agent") == RET)["repo"].cast(pl.Utf8).to_list())
oth = wc.filter(pl.col("goal_no") == 31).with_columns(pl.col("repo").cast(pl.Utf8))
rel = {"before_share_in_ret_repos": float(oth.filter((pl.col("pt_date") < "2026-02-19") & (pl.col("author_agent") != RET))
                                           ["repo"].is_in(list(ret_repos)).mean()),
       "on_0219_share_in_ret_repos": float(oth.filter((pl.col("pt_date") == "2026-02-19") & (pl.col("author_agent") != RET))
                                           ["repo"].is_in(list(ret_repos)).mean()),
       "n_ret_repos": len(ret_repos)}
OUTJ["NE29"] = {"incumbents": sorted(int(a) for a in inc), "day_log1p_commits_per_incumbent": day_val, "obs": float(obs),
                "null_mean": float(null.mean()), "null_sd": float(null.std(ddof=1)), "n_null": int(len(null)), "z": z,
                "retiree_share_of_commits_30_31": share_ret, "reliance": rel, "N1": bool(abs(z) < 2),
                "N2": bool(share_ret < 0.05)}
log(f"NE29 obs {obs:+.3f} z {z:+.2f} share {share_ret:.3f} rel {rel}")


# ============================================================================ write, figure
def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


(OUT / "r1b_extra.json").write_text(json.dumps(clean(OUTJ), indent=1))
write_provenance("r1b_extra", ["H15 r1b agent_day, scramble_catalog, artifact_switches, consolidations, calls", "work_commits",
                               "roster"], {"seed": SEED + 11, "AS": "matched CONT null + unit-pooled placebo"},
                 built_by="hypotheses/H15-semantic-information-scrambles/analysis/r1b_extra.py")

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

FIG.mkdir(parents=True, exist_ok=True)
fig, axs = plt.subplots(1, 2, figsize=(7.4, 2.8), gridspec_kw={"width_ratios": [1.25, 1]})
ax = axs[0]
prof = pl.read_parquet(OUT / "consolidation_profile.parquet")
for kind, col in (("CF", "#c0392b"), ("CV", "#2a6f97")):
    p = prof.filter(pl.col("kind") == kind).group_by("off").agg((pl.col("w_rate") * pl.col("n")).sum() / pl.col("n").sum()).sort("off")
    ref = p.filter(pl.col("off").is_between(-20, -11))["w_rate"].mean()
    ax.plot(p["off"], p["w_rate"] / ref, "o-", ms=2.5, lw=1.1, color=col, label={"CF": "forced (cap)", "CV": "voluntary"}[kind])
ax.axvline(0, color="k", lw=0.6)
ax.axhline(1, color="0.6", lw=0.6, ls=":")
ax.set_xlabel("call offset from the context erasure", fontsize=8)
ax.set_ylabel("work commits per call / calls −20…−11", fontsize=8)
ax.set_title(f"(a) erasure on the DQ1 ledger: forced dip {cfm['mu']:+.2f} [{cfm['lo']:+.2f}, {cfm['hi']:+.2f}]", fontsize=8)
ax.legend(fontsize=7, frameon=False)
ax.tick_params(labelsize=7)
ax = axs[1]
rows = []
vm = res1b["vstar_meta"]
for lab, m in (("memory loss (V*)", vm["ML"]["meta"]), ("newcomer (V*)", vm["MN"]["meta"]), ("rewrite ctrl (V*)", vm["MR"]["meta"]),
               ("chat cut (V*)", vm["CC"]["meta"]), ("memory loss (work)", res1b["by_V"]["V_out"]["types"]["ML"]["meta"]["kal"]),
               ("newcomer (work)", res1b["by_V"]["V_out"]["MN"]["meta"]), ("artifact switch (work)", OUTJ["AS"]["V_out"]["meta_matched"]),
               ("artifact switch (files)", OUTJ["AS"]["V_files"]["meta_matched"])):
    if m:
        rows.append((lab, m["mu"], m["lo"], m["hi"]))
for i, (lab, mu, lo, hi) in enumerate(rows[::-1]):
    ax.errorbar(mu, i, xerr=[[mu - lo], [hi - mu]], fmt="o", ms=3.5, color="#c0392b" if "artifact" in lab else "k", lw=0.9)
ax.set_yticks(range(len(rows)))
ax.set_yticklabels([r[0] for r in rows[::-1]], fontsize=7)
ax.axvline(0, color="0.5", lw=0.7)
ax.set_xlabel("ΔV, SD of same-day residual (meta, 95% CI)", fontsize=8)
ax.set_title("(b) day-scale scrambles, round 1b", fontsize=8)
ax.tick_params(labelsize=7)
fig.tight_layout()
fig.savefig(FIG / "F_r1b.pdf", bbox_inches="tight")
log("wrote r1b_extra.json and figures/r1b/F_r1b.pdf")
