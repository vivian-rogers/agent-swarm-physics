"""H18 cross-period summary: per-period table, pooled estimates (reported next to per-period ones), P1-P11 scoring.

  uv run python hypotheses/H18-attention-dilution/analysis/summarize.py

Periods are compared only through their fitted parameters (CLAUDE.md). Random-effects (DerSimonian-Laird) pooling
uses the day-bootstrap SD of each period's estimate; it is reported next to the per-period values (exception (d)).
Writes data/processed/H18-attention-dilution/summary.json and card_tables.md.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fit_periods import dl_pool  # noqa: E402
from periods import PERIODS, REGIME_I, gname  # noqa: E402
from summarize_lib import BUDGET_LIKE, CONST_LIKE, SATURATING, d1_checks, d2_check, f2, fci, period_verdict  # noqa: E402

ROOT = HERE.parents[2]
DATA = ROOT / "data/processed/H18-attention-dilution"
R3 = [36, 37, 38, 39, 40, 41, 42, 44, 51]


def load_all():
    out = {}
    for g in PERIODS:
        f = DATA / gname(g) / "fits.json"
        if f.exists():
            out[g] = json.loads(f.read_text())
    return out


def sd_of(b, key="beta"):
    x = (b or {}).get(key)
    return x["sd"] if x and x.get("sd") else None


def pooled(F, gs, getter):
    est, se = [], []
    for g in gs:
        if g not in F:
            continue
        e, s = getter(F[g])
        if e is not None and s is not None and math.isfinite(e) and s > 0:
            est.append(e)
            se.append(s)
    return dl_pool(est, se)


def main():
    F = load_all()
    gs = [g for g in PERIODS if g in F and F[g]["D1"]["n_units"] >= 300]
    rows = []
    for g in PERIODS:
        if g not in F:
            continue
        f = F[g]
        d1 = f["D1"]
        c = d1_checks(f)
        cvb = d1.get("cv_block", {})
        comp = cvb.get("comp", {})
        d2 = d2_check(f) if f["meta"]["regime"] in ("III", "II/III") else {"status": "n/a"}
        bp = d1["fits"].get("bypass")
        eps = f.get("eps_S", {})
        pl_ = f.get("placebo", {})
        ct = f.get("content") or {}
        rows.append(dict(
            g=g, regime=f["meta"]["regime"], mode=f["meta"]["mode"], n_days=f["n_days"], n_agents=f["n_agents"],
            n_room=f["n_room_mean"], k_median=f["k_median"], k_mean=f["k_mean"], n_units=d1["n_units"], rate=d1["rate"],
            beta=c["beta"], beta_lo=c["lo"], beta_hi=c["hi"], beta_sd=sd_of(d1["boot"]),
            cv_best=cvb.get("best"), cv_eff=cvb.get("effective"), k0=cvb.get("k0"), rho=cvb.get("rho"),
            d_inv_const=(comp.get("inv_vs_const") or [None])[0], d_inv_const_lo=(comp.get("inv_vs_const") or [None, None])[1],
            d_inv_rec=(comp.get("inv_vs_rec") or [None])[0], d_inv_rec_lo=(comp.get("inv_vs_rec") or [None, None])[1],
            d_inv_rec_hi=(comp.get("inv_vs_rec") or [None, None, None])[2],
            d_recbud_rec=(comp.get("recbud_vs_rec") or [None])[0],
            cv_day_eff=(d1.get("cv_day") or {}).get("effective"),
            eps=eps.get("eps"), eps_lo=(eps.get("boot") or {}).get("lo"), eps_hi=(eps.get("boot") or {}).get("hi"),
            eps_sd=(eps.get("boot") or {}).get("sd"),
            B_hat=f.get("B_hat"), p_bar=f.get("p_bar"), egamma=math.exp(d1["gamma"]), gamma=d1["gamma"],
            gamma_sd=sd_of(d1["boot"], "gamma"), n_mention_units=d1["n_mention_units"],
            beta_other=bp["params"]["beta"] if bp else None, betaM=bp["params"]["betaM"] if bp else None,
            beta_other_sd=sd_of(d1["boot"], "beta_byp"), betaM_sd=sd_of(d1["boot"], "betaM_byp"),
            d2_status=d2["status"], d2_beta=d2.get("beta"), d2_lo=d2.get("lo"), d2_hi=d2.get("hi"), d2_n=d2.get("n"),
            d2_resp=d2.get("n_resp"), d2_sd=sd_of((f.get("D2") or {}).get("boot")),
            inv_rate=pl_.get("invisible"), nonp_rate=pl_.get("nonpending"), pend_same=pl_.get("pending_same_talks"),
            content_slope=ct.get("slope"), content_excess=ct.get("overall_excess"),
            verdict=period_verdict(g, f)))
    R = {r["g"]: r for r in rows}
    S = {"rows": rows}
    # ---------------- P1
    elig = [r for r in rows if r["n_units"] >= 300]
    n_excl = sum(1 for r in elig if r["beta_lo"] is not None and r["beta_lo"] > 0)
    pb_all = pooled(F, [r["g"] for r in elig], lambda f: (f["D1"]["beta"], sd_of(f["D1"]["boot"])))
    pb_I = pooled(F, [g for g in REGIME_I if g in R], lambda f: (f["D1"]["beta"], sd_of(f["D1"]["boot"])))
    pb_III = pooled(F, [g for g in R3 if g in R], lambda f: (f["D1"]["beta"], sd_of(f["D1"]["boot"])))
    pb_2room = pooled(F, [g for g in (35, 36, 37, 38, 39, 40, 41, 42, 44) if g in R],
                      lambda f: (f["D1"]["beta"], sd_of(f["D1"]["boot"])))
    S["P1"] = dict(n_eligible=len(elig), n_ci_excl0=n_excl, share=n_excl / max(1, len(elig)), pooled=pb_all,
                   pooled_regI=pb_I, pooled_regIII=pb_III, pooled_two_room=pb_2room,
                   median_beta=float(np.median([r["beta"] for r in elig])),
                   pass_=(n_excl / max(1, len(elig)) >= 0.7 and pb_all and 0.5 <= pb_all["mean"] <= 1.2))
    # ---------------- P2
    effs = [r["cv_eff"] for r in elig]
    nb = sum(1 for e in effs if e in BUDGET_LIKE)
    nc = sum(1 for e in effs if e in CONST_LIKE)
    nr = sum(1 for e in effs if e == "rec")
    ns = sum(1 for e in effs if e in SATURATING)
    n_ivr = sum(1 for r in elig if r["d_inv_rec"] is not None and r["d_inv_rec"] > 0)
    n_ivr_ci = sum(1 for r in elig if r["d_inv_rec_lo"] is not None and r["d_inv_rec_lo"] > 0)
    n_rvi_ci = sum(1 for r in elig if r["d_inv_rec_hi"] is not None and r["d_inv_rec_hi"] < 0)
    k0s = [r["k0"] for r in elig if r["cv_best"] == "sat"]
    S["P2"] = dict(budget_like=nb, saturating=ns, const_like=nc, rec=nr, n=len(elig), effective=dict(zip([r["g"] for r in elig], effs)),
                   inv_beats_rec=n_ivr, inv_beats_rec_ci=n_ivr_ci, rec_beats_inv_ci=n_rvi_ci,
                   sat_k0=k0s, n_sat_k0_lt3=sum(1 for k in k0s if k < 3),
                   pass_=nb / max(1, len(elig)) >= 0.7 and (nc + nr) / max(1, len(elig)) <= 0.3)
    S["P2b"] = dict(recbud_beats_rec=sum(1 for r in elig if r["d_recbud_rec"] is not None and r["d_recbud_rec"] > 0),
                    n=len(elig))
    # ---------------- P3
    pe = pooled(F, [r["g"] for r in elig], lambda f: (f["eps_S"]["eps"], (f["eps_S"].get("boot") or {}).get("sd")))
    in_band = sum(1 for r in elig if r["eps"] is not None and -0.2 <= r["eps"] <= 0.5)
    sratio = {}
    for g in [r["g"] for r in elig]:
        cv_ = {c["kbin"]: c for c in F[g]["curves"]}
        lo = [cv_[b] for b in ("3-4", "5-8") if b in cv_ and cv_[b]["n_talks"] > 0]
        hi = [cv_[b] for b in ("17-32", "33-64", "65+") if b in cv_ and cv_[b]["n_talks"] > 0]
        if lo and hi:
            sl = sum(c["S"] * c["n_talks"] for c in lo) / sum(c["n_talks"] for c in lo)
            sh = sum(c["S"] * c["n_talks"] for c in hi) / sum(c["n_talks"] for c in hi)
            sratio[g] = sh / sl if sl > 0 else None
    S["P3"] = dict(pooled=pe, in_band=in_band, n=len(elig), S_ratio_high_over_mid=sratio,
                   n_S_within_1p5=sum(1 for v in sratio.values() if v is not None and 1 / 1.5 <= v <= 1.5),
                   pass_=bool(pe and -0.2 <= pe["mean"] - 1.96 * pe["se"] and pe["mean"] + 1.96 * pe["se"] <= 0.5))
    # ---------------- P4
    pg = pooled(F, [r["g"] for r in elig], lambda f: (f["D1"]["gamma"], sd_of(f["D1"]["boot"], "gamma")))
    diffs, dses = [], []
    for r in elig:
        if r["betaM"] is not None and r["betaM_sd"] and r["beta_other_sd"] and r["n_mention_units"] >= 100:
            diffs.append(r["betaM"] - r["beta_other"])
            dses.append(math.sqrt(r["betaM_sd"] ** 2 + r["beta_other_sd"] ** 2))
    pdif = dl_pool(diffs, dses)
    S["P4"] = dict(pooled_gamma=pg, pooled_egamma=math.exp(pg["mean"]) if pg else None,
                   pooled_betaM_minus_beta=pdif, n=len(diffs),
                   pass_=bool(pg and math.exp(pg["mean"]) >= 3 and pdif and pdif["mean"] < -0.3))
    # ---------------- P5
    r3 = [g for g in R3 if g in R]
    d2ok = [g for g in r3 if R[g]["d2_status"] != "underpowered"]
    n_d2_excl = sum(1 for g in d2ok if R[g]["d2_lo"] is not None and R[g]["d2_lo"] > 0)
    pd2 = pooled(F, d2ok, lambda f: (f["D2"]["beta"], sd_of(f["D2"].get("boot"))))
    S["P5"] = dict(periods_powered=d2ok, n_excl0=n_d2_excl, pooled_D2=pd2, pooled_D1_regIII=pb_III,
                   diff=(pd2["mean"] - pb_III["mean"]) if pd2 and pb_III else None,
                   pass_=bool(pd2 and pb_III and n_d2_excl >= 0.5 * max(1, len(d2ok)) and abs(pd2["mean"] - pb_III["mean"]) <= 0.4),
                   timing_artifact=bool(pd2 and pb_III and pd2["mean"] < 0.2 and pd2["mean"] - 1.96 * pd2["se"] <= 0 and pb_III["mean"] > 0.5))
    # ---------------- P6 (rooms)
    p6 = {}
    for g in (35, 36, 37, 38, 39, 41, 42, 44):
        rm = (F.get(g) or {}).get("rooms")
        if rm:
            ep = rm.get("effect_pow_ci") or {}
            ec = rm.get("effect_const_ci") or {}
            p6[g] = dict(k_ratio=rm["median_k_ratio"], p_ratio=rm["median_p_ratio"], S_ratio=rm["median_S_ratio"],
                         eff_const=rm["effect_const"], eff_const_lo=ec.get("lo"), eff_const_hi=ec.get("hi"),
                         eff_pow=rm["effect_pow"], eff_pow_lo=ep.get("lo"), eff_pow_hi=ep.get("hi"), n_days=rm["n_days"],
                         p_higher_small=(rm["median_p_ratio"] or 0) > 1,
                         ratio_within_2=(rm["median_p_ratio"] and rm["median_k_ratio"] and
                                         0.5 <= rm["median_p_ratio"] / rm["median_k_ratio"] <= 2),
                         shrinks=(ep.get("lo") is not None and ep["lo"] <= 0 <= ep["hi"]))
    S["P6"] = p6
    # ---------------- P7
    sp = DATA / "spanning.json"
    S["P7"] = json.loads(sp.read_text())["merge"]["P7"] if sp.exists() else None
    # ---------------- P8
    S["P8"] = dict(regI=pb_I, regIII=pb_III, diff=(pb_I["mean"] - pb_III["mean"]) if pb_I and pb_III else None,
                   diff_se=math.sqrt(pb_I["se"] ** 2 + pb_III["se"] ** 2) if pb_I and pb_III else None,
                   pass_=bool(pb_I and pb_III and abs(pb_I["mean"] - pb_III["mean"]) <= 0.3))
    # ---------------- P9
    xs = [r for r in elig]
    N = np.array([r["n_room"] for r in xs])
    pbar = np.array([r["p_bar"] for r in xs])
    Bh = np.array([r["B_hat"] for r in xs])
    rp = spearmanr(N, pbar)
    rb = spearmanr(N, Bh)
    cvp = float(np.std(pbar) / np.mean(pbar))
    cvb_ = float(np.std(Bh) / np.mean(Bh))
    seg = (F.get(51) or {}).get("segment_S") or []
    if len(seg) >= 4:
        sN = [s["n_room"] for s in seg]
        s51p = spearmanr(sN, [s["p_bar"] for s in seg])
        s51b = spearmanr(sN, [s["B_hat"] for s in seg])
        seg51 = dict(rho_p=float(s51p.statistic), p_p=float(s51p.pvalue), rho_B=float(s51b.statistic),
                     p_B=float(s51b.pvalue), segments=seg)
    else:
        seg51 = None
    S["P9"] = dict(rho_p_N=float(rp.statistic), p_p_N=float(rp.pvalue), rho_B_N=float(rb.statistic), p_B_N=float(rb.pvalue),
                   cv_pbar=cvp, cv_Bhat=cvb_, seg51=seg51,
                   pass_=bool(rp.statistic < -0.5 and abs(rb.statistic) < 0.3 and cvb_ < cvp))
    # ---------------- P10
    p10 = {}
    for r in elig:
        if r["inv_rate"] is None or (isinstance(r["inv_rate"], float) and math.isnan(r["inv_rate"])):
            continue
        p10[r["g"]] = dict(inv=r["inv_rate"], nonp=r["nonp_rate"], pend=r["pend_same"],
                           pass_=r["inv_rate"] <= max(1.5 * r["nonp_rate"], 1e-9) and r["inv_rate"] <= 0.5 * r["pend_same"])
    S["P10"] = dict(per_period=p10, n_pass=sum(1 for v in p10.values() if v["pass_"]), n=len(p10))
    # ---------------- P11
    p11 = {r["g"]: dict(slope=r["content_slope"], beta=r["beta"],
                        pass_=r["content_slope"] is not None and abs(r["content_slope"] + r["beta"]) <= 0.4)
           for r in elig}
    S["P11"] = dict(per_period=p11, n_pass=sum(1 for v in p11.values() if v["pass_"]),
                    n_with_slope=sum(1 for v in p11.values() if v["slope"] is not None))
    S["verdicts"] = {gname(r["g"]): r["verdict"] for r in rows}
    (DATA / "summary.json").write_text(json.dumps(S, indent=1, default=float))
    write_tables(S, R)
    for k in ("P1", "P2", "P2b", "P3", "P4", "P5", "P8", "P9", "P10", "P11"):
        v = {kk: vv for kk, vv in S[k].items() if kk not in ("per_period", "segments", "effective", "S_ratio_high_over_mid")} \
            if isinstance(S[k], dict) else S[k]
        print(k, json.dumps(v, default=float)[:600])
    print("P6", json.dumps(S["P6"], default=float)[:1500])
    print("P7", S["P7"])
    print(S["verdicts"])


def write_tables(S, R):
    L = ["| G | regime · mode | days | N_room | k med / mean | units (rate) | β̂ [95% CI] | CV best (effective) | Δℓ inv−rec ×10³ | ε_S | e^γ | β̂_D2 [CI] (units, resp.) | verdict |",
         "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for g in PERIODS:
        if g not in R:
            continue
        r = R[g]
        d2 = ("—" if r["d2_status"] == "n/a" else
              (f"underpowered ({r['d2_n']}, {r['d2_resp']})" if r["d2_status"] == "underpowered" else
               f"{fci(r['d2_beta'], r['d2_lo'], r['d2_hi'])} ({r['d2_n']}, {r['d2_resp']})"))
        L.append(f"| [{gname(g)}]({gname(g)}/README.md) | {r['regime']} · {r['mode']} | {r['n_days']} | {f2(r['n_room'], 1)} | "
                 f"{f2(r['k_median'], 0)} / {f2(r['k_mean'], 1)} | {r['n_units']} ({f2(r['rate'], 3)}) | "
                 f"{fci(r['beta'], r['beta_lo'], r['beta_hi'])} | {r['cv_best']} ({r['cv_eff']}) | "
                 f"{f2(1000 * r['d_inv_rec'] if r['d_inv_rec'] is not None else None, 1)} | {f2(r['eps'])} | {f2(r['egamma'], 1)} | {d2} | {r['verdict']} |")
    (DATA / "card_tables.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
