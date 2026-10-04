"""H89 replication layer: the Price partition on every eligible non-holdout goal period.

  uv run python hypotheses/H89-price-equation-culture/analysis/replication.py
Outputs: data/processed/H89-price-equation-culture/replication/{replication.json, periods.parquet}
Pre-registered rules: card "Prediction" (2026-10-04 20:15 UTC) and amendments A1-A5 (20:30 UTC).
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl
from scipy import stats as sst

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h89lib as L  # noqa: E402

OUT = L.DATA / "replication"
RHO_MIN = 0.3
PHIS = [0.0, 0.01, 0.03, 0.1, 0.3, 0.5]
MAIN = ("sel", "trans", "mig", "mig_roster", "mig_presence", "sel_self", "sel_named", "sel_unnamed", "trans_self",
        "trans_social")


def stats_all(P: L.Period) -> dict:
    res, dg = L.run_period(P)
    out = {}
    for tag in L.TRAITS:
        k = P.kick.get(tag)
        e = L.shares(res, tag, kick=k)
        c = L.shares(res, tag, kick=k, cumulative=True)
        for g in MAIN:
            out[f"{tag}.s_{g}"] = e.get(f"s_{g}", np.nan)
        for g in ("sel", "trans", "mig", "mig_roster"):
            out[f"{tag}.cum_s_{g}"] = c.get(f"s_{g}", np.nan)
        out[f"{tag}.rho"] = e.get("rho", np.nan)
        out[f"{tag}.rho_cum"] = c.get("rho", np.nan)
        out[f"{tag}.den"] = e.get("den", np.nan)
        if k is not None:
            out[f"{tag}.s_kick"] = e["s_kick"]
            out[f"{tag}.R"] = e["R"]
            out[f"{tag}.C"] = L.persistence(res, tag, k) if len(res) >= 2 else np.nan
    out["style.C"] = L.persistence(res, "style", None) if len(res) >= 2 else np.nan
    return out


def jk(P: L.Period, full: dict) -> dict:
    agents = sorted({a for v in P.active.values() for a in v})
    vals = []
    for a in agents:
        Q = P.drop({a})
        if not L.transitions(Q):
            continue
        vals.append(stats_all(Q))
    se = {}
    for key in full:
        v = np.array([x.get(key, np.nan) for x in vals], dtype=float)
        v = v[np.isfinite(v)]
        n = len(v)
        se[key] = float(np.sqrt((n - 1) / n * ((v - v.mean()) ** 2).sum())) if n >= 4 else np.nan
    return se, len(vals)


def calibrate(P: L.Period, reps: int = 30, D: int = 20, seed: int = 7) -> dict:
    """Noise-free curve: energy s_Mig as a function of the day-field fraction phi (real populations)."""
    rng = np.random.default_rng(seed + P.goal)
    agents = sorted({a for v in P.active.values() for a in v})
    ds = sorted(P.active)
    curve = {}
    for phi in PHIS:
        vals = []
        for _ in range(reps):
            q = {a: rng.normal(0, np.sqrt(1 - phi), D) for a in agents}
            f = {d: rng.normal(0, np.sqrt(phi), D) for d in ds}
            arr = np.zeros((len(P.keys), 3, D))
            for d in ds:
                for a in P.active[d]:
                    arr[P.keys[(a, d)]] = q[a] + f[d]
            Q = L.Period(P.goal, P.days, P.keys, {"syn": arr}, P.active, P.F, P.adop, {})
            res, _ = L.run_period(Q, tags=["syn"])
            vals.append(L.shares(res, "syn")["s_mig"])
        curve[phi] = float(np.nanmean(vals))
    return curve


def implied_phi(curve: dict, s: float):
    if not np.isfinite(s):
        return None
    xs = [p for p in PHIS if p > 0]
    ys = [curve[p] for p in xs]
    if not np.isfinite(ys[0]) or ys[0] <= 0:
        return None
    if s >= ys[0]:
        return "<0.01"
    if s <= ys[-1]:
        return ">0.5"
    for (x0, y0), (x1, y1) in zip(zip(xs, ys), zip(xs[1:], ys[1:])):
        if y1 <= s <= y0:
            fr = (y0 - s) / (y0 - y1) if y0 != y1 else 0.0
            return float(np.exp(np.log(x0) + fr * (np.log(x1) - np.log(x0))))
    return None


def ok(r: dict, tag: str) -> bool:
    return bool(np.isfinite(r.get(f"{tag}.rho", np.nan)) and r[f"{tag}.rho"] >= RHO_MIN and r[f"{tag}.den"] > 0)


def period_verdict(r: dict) -> tuple[str, dict]:
    if not (ok(r, "content_bge") and ok(r, "style")):
        return "n/a", {}
    c1 = r["style.s_mig"] > r["content_bge.s_mig"]
    t = r["content_bge.s_trans"]
    c2 = t >= 0.5 and t >= max(r["content_bge.s_sel"], r["content_bge.s_mig"])
    c3 = all(abs(r[f"{tag}.s_sel"]) <= 0.2 for tag in ("content_bge", "style", "conv") if ok(r, tag))
    n = int(c1) + int(c2) + int(c3)
    v = "supported" if n == 3 else ("failed" if n == 0 else "mixed")
    return v, dict(c1=bool(c1), c2=bool(c2), c3=bool(c3))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ad = pl.read_parquet(L.DATA / "agent_days.parquet")
    adop = pl.read_parquet(L.DATA / "adoptions.parquet")
    kick = np.load(L.DATA / "kickoff.npz")
    goals = sorted(ad["goal"].unique().to_list())
    t0 = time.time()
    per = {}
    for g in goals:
        P = L.load_period(g, ad, adop, kick)
        res, dg = L.run_period(P)
        n_in = sum(d["n_in"] for d in dg)
        elig = len(res) >= 2 and n_in >= 20
        rec = dict(goal=g, n_trans=len(res), n_in=n_in, n_ext=sum(d["n_ext"] for d in dg), eligible=elig,
                   n_agents=len({a for v in P.active.values() for a in v}),
                   n_agent_days=sum(len(v) for v in P.active.values()),
                   lam_mean=float(np.mean([d["lam_mean"] for d in dg])) if dg else np.nan,
                   w_sd=float(np.mean([d["w_sd"] for d in dg])) if dg else np.nan,
                   w_named=float(sum(d["w_named"] for d in dg)), w_unnamed=float(sum(d["w_unnamed"] for d in dg)),
                   n_roster_events=int(sum(d["nE_roster"] + d["nI_roster"] for d in dg)),
                   n_presence_events=int(sum(d["nE"] + d["nI"] - d["nE_roster"] - d["nI_roster"] for d in dg)),
                   first_day=P.days[0], last_day=P.days[-1])
        if not elig:
            rec["verdict"] = "n/a"
            per[g] = rec
            print(f"G{g:02d}: not eligible ({len(res)} transitions, {n_in} adoptions)")
            continue
        full = stats_all(P)
        se, n_jk = jk(P, full)
        rec.update({k: v for k, v in full.items()})
        rec.update({f"{k}.se": v for k, v in se.items()})
        rec["n_jk"] = n_jk
        # selection permutation (energy share; A2) and convergence placebo, leave-trait-out
        for tag in ("content_bge", "content_gte", "style", "conv"):
            pt = L.perm_sel_all(P, tag, n_perm=500, seed=g)
            rec[f"{tag}.perm_p"] = pt["energy"]["p"]
        resp, dgp = L.run_period(P, kind="plc")
        rec["n_plc"] = int(sum(d["n_in"] for d in dgp))
        sp = L.shares(resp, "content_bge")
        rec["content_bge.plc_s_sel"] = sp.get("s_sel", np.nan)
        rec["content_bge.plc_s_trans_social"] = sp.get("s_trans_social", np.nan)
        rl, _ = L.run_period(P, exclude_trait=True, tags=["conv"])
        rec["conv.lto_s_sel"] = L.shares(rl, "conv").get("s_sel", np.nan)
        # implied field fraction (A3)
        curve = calibrate(P)
        rec["calib_curve"] = curve
        for tag in L.TRAITS:
            rec[f"{tag}.phi_hat"] = implied_phi(curve, rec.get(f"{tag}.s_mig", np.nan))
        # drift ratio (A4)
        for tag in ("content_bge", "content_gte", "style"):
            C = rec.get(f"{tag}.C", np.nan)
            rec[f"{tag}.drift_ratio"] = float((1 + 2 * C) / (1 - C)) if np.isfinite(C) and C < 1 else np.nan
        v, crit = period_verdict(rec)
        rec["verdict"] = v
        rec["criteria"] = crit
        rec["reliable"] = {tag: ok(rec, tag) for tag in L.TRAITS}
        per[g] = rec
        print(f"G{g:02d} [{time.time() - t0:.0f}s] {v}: style mig {rec['style.s_mig']:+.2f} | content trans "
              f"{rec['content_bge.s_trans']:+.2f} mig {rec['content_bge.s_mig']:+.2f} sel {rec['content_bge.s_sel']:+.3f} | "
              f"rho c/s {rec['content_bge.rho']:.2f}/{rec['style.rho']:.2f} | R {rec['content_bge.R']:+.2f} C {rec['content_bge.C']:+.2f}",
              flush=True)
    # ---------------- card-level tallies
    E = [r for r in per.values() if r["eligible"]]
    card = {}

    def both(tag1, tag2):
        return [r for r in E if ok(r, tag1) and ok(r, tag2)]
    b = both("style", "content_bge")
    k1 = sum(r["style.s_mig"] > r["content_bge.s_mig"] for r in b)
    card["P1a"] = dict(n=len(b), k=k1, sign_p=float(sst.binomtest(k1, len(b), 0.5, alternative="greater").pvalue) if b else None,
                       pass_=bool(b and k1 >= 2 / 3 * len(b) and sst.binomtest(k1, len(b), 0.5, alternative="greater").pvalue < 0.05))
    s = [r for r in E if ok(r, "style")]
    k1b = sum(r["style.s_mig"] >= max(r["style.s_sel"], r["style.s_trans"]) for r in s)
    card["P1b"] = dict(n=len(s), k=k1b, pass_=bool(s and k1b >= 0.5 * len(s)))
    for tag in ("content_bge", "content_gte"):
        s = [r for r in E if ok(r, tag)]
        k = sum(r[f"{tag}.s_trans"] >= 0.5 and r[f"{tag}.s_trans"] >= max(r[f"{tag}.s_sel"], r[f"{tag}.s_mig"]) for r in s)
        card[f"P2_{tag}"] = dict(n=len(s), k=k, pass_=bool(s and k >= 2 / 3 * len(s)),
                                 median_trans=float(np.median([r[f"{tag}.s_trans"] for r in s])) if s else None)
    card["P2"] = dict(pass_=card["P2_content_bge"]["pass_"] and card["P2_content_gte"]["pass_"])
    p3 = {}
    for tag in ("content_bge", "style", "conv"):
        s = [r for r in E if ok(r, tag)]
        a = np.array([abs(r[f"{tag}.s_sel"]) for r in s])
        p3[tag] = dict(n=len(s), k=int((a <= 0.2).sum()), median_abs=float(np.median(a)) if len(a) else None,
                       pass_=bool(len(a) and (a <= 0.2).sum() >= 2 / 3 * len(a) and np.median(a) <= 0.2))
    card["P3"] = dict(per_trait=p3, pass_=all(v["pass_"] for v in p3.values()))
    p4 = {}
    for tag in ("content_bge", "content_gte", "style", "conv"):
        s = [r for r in E if ok(r, tag)]
        p4[tag] = dict(n=len(s), n_p05=int(sum(r[f"{tag}.perm_p"] < 0.05 for r in s)))
    on = [r for r in E if ok(r, "content_bge") and (r["w_named"] + r["w_unnamed"]) > 0]
    k_named = 0; n_named = 0
    for r in on:
        sn, su = abs(r["content_bge.s_sel_named"]), abs(r["content_bge.s_sel_unnamed"])
        if sn + su > 0:
            n_named += 1
            k_named += int(sn / (sn + su) > r["w_named"] / (r["w_named"] + r["w_unnamed"]))
    p4["named"] = dict(n=n_named, k=k_named)
    card["P4"] = p4
    p5 = {}
    for tag in ("content_bge", "content_gte"):
        s = [r for r in E if ok(r, tag)]
        k = sum(r[f"{tag}.R"] >= 0.1 and np.isfinite(r[f"{tag}.R.se"]) and r[f"{tag}.R"] - 1.96 * r[f"{tag}.R.se"] > 0 for r in s)
        kill = sum(not (np.isfinite(r[f"{tag}.R.se"]) and r[f"{tag}.R"] - 1.96 * r[f"{tag}.R.se"] > 0) for r in s)
        p5[tag] = dict(n=len(s), k=k, n_ci_includes0=kill, median_R=float(np.median([r[f"{tag}.R"] for r in s])) if s else None,
                       median_kick=float(np.median([r[f"{tag}.s_kick"] for r in s])) if s else None,
                       pass_=bool(s and k >= 2 / 3 * len(s)), killed=bool(s and kill >= 2 / 3 * len(s)))
    card["P5"] = dict(per_model=p5, pass_=all(v["pass_"] for v in p5.values()))
    s = [r for r in E if ok(r, "content_bge") and r["n_trans"] >= 4]
    k6 = sum(r["content_bge.C"] > 0 and np.isfinite(r["content_bge.C.se"]) and r["content_bge.C"] - 1.96 * r["content_bge.C.se"] > 0 for r in s)
    card["P6"] = dict(n=len(s), k=k6, median_C=float(np.median([r["content_bge.C"] for r in s])) if s else None,
                      pass_=bool(s and k6 >= 0.5 * len(s)))
    vs = [r["verdict"] for r in per.values()]
    card["verdicts"] = {v: vs.count(v) for v in set(vs)}
    n_pass = int(card["P1a"]["pass_"]) + int(card["P2"]["pass_"]) + int(card["P3"]["pass_"])
    card["overall"] = "supported" if n_pass == 3 else ("failed" if n_pass == 0 else "mixed")
    card["egregore"] = bool(card["P5"]["pass_"] and card["P6"]["pass_"])
    (OUT / "replication.json").write_text(json.dumps(dict(periods=per, card=card), indent=1, default=float))
    flat = []
    for g, r in per.items():
        flat.append({k: (v if not isinstance(v, (dict, list)) else json.dumps(v, default=float)) for k, v in r.items()})
    pl.DataFrame(flat, infer_schema_length=None).write_parquet(OUT / "periods.parquet")
    print(json.dumps(card, indent=1, default=float))
    print(f"done in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
