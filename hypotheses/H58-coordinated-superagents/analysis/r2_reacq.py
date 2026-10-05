"""H58 round-2 R3: the agent + own-artifact pair as the Kolchinsky-Wolpert agent (card "Round 2 design", R3).

Input: data/processed/H58-coordinated-superagents/r2/r3_events.parquet (scheme/build_r2.py). Codes: 0 r1, 1 r2, 2 r3,
3 r45, 4 own-old, 5 oth, 6 xrepo, 7 none. Events: forced erasures (scramble) and placebo calls; voluntary as variant.
  kappa rows   semantic_kappa.kappa_row per channel class (own files, others' files, goal documents, any file of A),
               pooled (NE41: strata agent x unit) and per goal period
  in-flight    I_F - I_P at a matched first-read lag (placebo resampled to the forced lag distribution)
  read/unread  log-OR(return to r1 | r1 read vs r1 unread), forced minus placebo (Mantel-Haenszel over agents)
  I_store      KL(p(X) || p(X coded against a time-shifted artifact state)) on forced and placebo events
--synthetic: the same estimators on the real event skeleton with X permuted (null), X := S planted (q), and a planted
read x erasure interaction on Y. Outputs r2/r3_synthetic.json, r2/r3_results.json.
Run: uv run python hypotheses/H58-coordinated-superagents/analysis/r2_reacq.py [--synthetic] [--real]
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "2")

import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r2lib58 as R  # noqa: E402

sys.path.insert(0, str(R.ROOT / "infra/shared"))
import semantic_kappa as SK  # noqa: E402

NONE = 7
LAG_BINS = [(1, 2), (3, 5), (6, 10)]


def load_events():
    ev = pl.read_parquet(R.R2 / "r3_events.parquet")
    meta = {x["unit"]: x for x in R.units_meta()}
    R.assert_no_reserved([meta[u] for u in ev["unit"].unique().to_list()])
    ev = ev.with_columns(pl.col("unit").replace_strict({u: m["goal_no"] for u, m in meta.items()},
                                                       return_dtype=pl.Int64).alias("goal_no"))
    ev = ev.with_columns((pl.col("agent").cast(pl.Utf8) + "|" + pl.col("pt_date")).alias("cluster"),
                         (pl.col("agent").cast(pl.Utf8) + "|" + pl.col("unit")).alias("stratum"))
    lag = pl.when(pl.col("first_read_call") < 1).then(0)
    for i, (lo, hi) in enumerate(LAG_BINS):
        lag = lag.when((pl.col("first_read_call") >= lo) & (pl.col("first_read_call") <= hi)).then(i + 1)
    return ev.with_columns(lag.otherwise(0).alias("lag_bin"))


def ev_dict(df, cls):
    if cls == "own":
        flag = df["open_own"].to_numpy()
        S = np.where(flag, df["S"].to_numpy(), NONE)
    elif cls == "oth":
        flag = df["open_oth"].to_numpy()
        S = np.where(flag, df["S"].to_numpy(), NONE)
    elif cls == "goal":
        flag = df["open_goal"].to_numpy()
        S = flag.astype(int)
    else:                                   # any file of A
        flag = df["S"].to_numpy() != NONE
        S = df["S"].to_numpy()
    return {"cluster": df["cluster"].to_numpy(), "stratum": df["stratum"].to_numpy(),
            "scramble": (df["etype"] == "forced").to_numpy(), "X": df["X"].to_numpy(), "S": S,
            "open": flag.astype(bool), "V": df["V"].to_numpy().astype(float), "V_pre": df["V_pre"].to_numpy().astype(float)}


def matched_placebo(F, P, rng):
    """Resample placebo rows to the forced events' first-read-lag distribution (global bins)."""
    pf = np.bincount(F["lag_bin"].to_numpy(), minlength=4) / F.height
    pp = np.bincount(P["lag_bin"].to_numpy(), minlength=4) / max(P.height, 1)
    w = np.where(pp > 0, pf / np.maximum(pp, 1e-12), 0)[P["lag_bin"].to_numpy()]
    if w.sum() == 0:
        return P
    idx = rng.choice(P.height, P.height, replace=True, p=w / w.sum())
    return P[idx]


def info(X, S, strata, n_perm=50, seed=0):
    r = SK.mi_corrected(np.asarray(X), np.asarray(S), np.asarray(strata), n_perm=n_perm, rng=np.random.default_rng(seed))
    return r["I"]


def inflight(df, B=200, seed=0, Xcol="X"):
    rng = np.random.default_rng(seed)
    F = df.filter(pl.col("etype") == "forced")
    P = df.filter(pl.col("etype") == "placebo")
    Pm = matched_placebo(F, P, rng)
    IF = info(F[Xcol], F["S"], F["stratum"], seed=seed)
    IP = info(Pm[Xcol], Pm["S"], Pm["stratum"], seed=seed + 1)
    cl = df["cluster"].unique().to_list()
    parts = {c: g for (c,), g in df.partition_by("cluster", as_dict=True).items()}
    bs = []
    for b in range(B):
        pick = rng.choice(len(cl), len(cl))
        d = pl.concat([parts[cl[i]] for i in pick])
        Fb, Pb = d.filter(pl.col("etype") == "forced"), d.filter(pl.col("etype") == "placebo")
        if Fb.height < 30 or Pb.height < 30:
            continue
        Pmb = matched_placebo(Fb, Pb, rng)
        bs.append(info(Fb[Xcol], Fb["S"], Fb["stratum"], n_perm=10, seed=b) -
                  info(Pmb[Xcol], Pmb["S"], Pmb["stratum"], n_perm=10, seed=b + 7))
    bs = np.asarray(bs)
    return {"I_F": IF, "I_P": IP, "dI": IF - IP, "dI_ci": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
            if len(bs) > 20 else [None, None], "n_F": F.height, "n_P": P.height}


def mh(tables):
    Rr = Ss = PR = PSQR = QS = 0.0
    for a, b, c, d in tables:
        n = a + b + c + d
        if n == 0:
            continue
        r_, s_ = a * d / n, b * c / n
        p_, q_ = (a + d) / n, (b + c) / n
        Rr += r_; Ss += s_; PR += p_ * r_; PSQR += p_ * s_ + q_ * r_; QS += q_ * s_
    if Rr <= 0 or Ss <= 0:
        return np.nan, np.nan
    var = PR / (2 * Rr * Rr) + PSQR / (2 * Rr * Ss) + QS / (2 * Ss * Ss)
    return math.log(Rr / Ss), math.sqrt(var)


def read_unread(df, Y=None, B=200, seed=0):
    """Interaction = MH log-OR(Y | r1 read vs unread) in forced minus the same in placebo (events with a commit)."""
    d = df.filter(pl.col("X") != NONE)
    y = (d["X"] == 0).to_numpy() if Y is None else Y
    d = d.with_columns(pl.Series("Y", y.astype(bool)))

    def lor(dd, et):
        tabs = []
        for (_a,), g in dd.filter(pl.col("etype") == et).partition_by("agent", as_dict=True).items():
            e = g["r1_read"].to_numpy()
            yy = g["Y"].to_numpy()
            tabs.append((float((e & yy).sum()), float((e & ~yy).sum()), float((~e & yy).sum()), float((~e & ~yy).sum())))
        return mh(tabs)
    lf, sf = lor(d, "forced")
    lp, sp = lor(d, "placebo")
    out = {"lor_F": lf, "lor_P": lp, "inter": lf - lp, "se_inter": math.sqrt(sf ** 2 + sp ** 2)
           if np.isfinite(sf) and np.isfinite(sp) else np.nan,
           "n_F": int((d["etype"] == "forced").sum()), "n_P": int((d["etype"] == "placebo").sum()),
           "read_share_F": float(d.filter(pl.col("etype") == "forced")["r1_read"].mean()),
           "read_share_P": float(d.filter(pl.col("etype") == "placebo")["r1_read"].mean()),
           "Y_F": float(d.filter(pl.col("etype") == "forced")["Y"].mean()),
           "Y_P": float(d.filter(pl.col("etype") == "placebo")["Y"].mean())}
    if B:
        rng = np.random.default_rng(seed)
        cl = d["cluster"].unique().to_list()
        parts = {c: g for (c,), g in d.partition_by("cluster", as_dict=True).items()}
        bs = []
        for _ in range(B):
            pick = rng.choice(len(cl), len(cl))
            dd = pl.concat([parts[cl[i]] for i in pick])
            a, _ = lor(dd, "forced")
            b, _ = lor(dd, "placebo")
            if np.isfinite(a) and np.isfinite(b):
                bs.append(a - b)
        bs = np.asarray(bs)
        out["inter_ci"] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))] if len(bs) > 20 else [None, None]
    return out


def kl_store(df, B=200, seed=0):
    """I_store = KL(p(X) || p(X_shift)) in bits over the 8 codes (events with X_shift defined), forced and placebo."""
    rng = np.random.default_rng(seed)

    def kl(dd):
        x = dd["X"].to_numpy()
        xs = dd["X_shift"].to_numpy()
        p = (np.bincount(x, minlength=8) + 0.5) / (len(x) + 4)
        q = (np.bincount(xs, minlength=8) + 0.5) / (len(xs) + 4)
        return float((p * np.log2(p / q)).sum())
    d = df.filter(pl.col("X_shift").is_not_null()).with_columns(pl.col("X_shift").cast(pl.Int64))
    F, P = d.filter(pl.col("etype") == "forced"), d.filter(pl.col("etype") == "placebo")
    out = {"I_store_F": kl(F), "I_store_P": kl(P), "n_F": F.height, "n_P": P.height,
           "p_r1_F": float((F["X"] == 0).mean()), "p_r1_shift_F": float((F["X_shift"] == 0).mean()),
           "p_r1_P": float((P["X"] == 0).mean()), "p_r1_shift_P": float((P["X_shift"] == 0).mean())}
    cl = d["cluster"].unique().to_list()
    parts = {c: g for (c,), g in d.partition_by("cluster", as_dict=True).items()}
    bf, bp, br = [], [], []
    for _ in range(B):
        pick = rng.choice(len(cl), len(cl))
        dd = pl.concat([parts[cl[i]] for i in pick])
        f = kl(dd.filter(pl.col("etype") == "forced"))
        p = kl(dd.filter(pl.col("etype") == "placebo"))
        bf.append(f); bp.append(p); br.append(f / p if p > 0 else np.nan)
    ci = lambda a: [float(np.nanpercentile(a, 2.5)), float(np.nanpercentile(a, 97.5))]  # noqa: E731
    out.update({"I_store_F_ci": ci(bf), "I_store_P_ci": ci(bp), "ratio": out["I_store_F"] / out["I_store_P"]
                if out["I_store_P"] > 0 else np.nan, "ratio_ci": ci(br)})
    return out


def kappa_rows(df, B=300):
    rows = {}
    d = df.filter(pl.col("etype").is_in(["forced", "placebo"]) & pl.col("V").is_not_null() & pl.col("V").is_not_nan())
    for cls in ("own", "oth", "goal", "any"):
        r = SK.kappa_row(ev_dict(d, cls), n_perm=100, B=B, n_perm_boot=5, seed=58)
        rows[cls] = r
    return rows


# ============================================================================ synthetic
def synthetic(reps=30):
    ev = load_events().filter(pl.col("etype").is_in(["forced", "placebo"]))
    rng = np.random.default_rng(5858)
    out = {"I_null": [], "I_plant": {}, "dI_null": [], "inter": {}}
    F = ev.filter(pl.col("etype") == "forced")
    st = F["stratum"].to_numpy()
    S = F["S"].to_numpy()
    X = F["X"].to_numpy()
    t0 = time.time()
    for r in range(reps):
        Xp = SK.permute_within(X, SK._codes(st), rng)
        ci = SK.mi_jackknife(Xp, S, st, F["cluster"].to_numpy(), n_perm=10, rng=rng)
        Ival = info(Xp, S, st, n_perm=30, seed=r)
        out["I_null"].append({"I": Ival, "lo_jk": Ival - 1.96 * ci["se"]})
        for q in (0.05, 0.1, 0.2):
            Xq = np.where((rng.random(len(X)) < q) & (S != NONE), S, Xp)
            cq = SK.mi_jackknife(Xq, S, st, F["cluster"].to_numpy(), n_perm=10, rng=rng)
            Iq = info(Xq, S, st, n_perm=30, seed=r)
            out["I_plant"].setdefault(str(q), []).append({"I": Iq, "lo_jk": Iq - 1.96 * cq["se"]})
        # in-flight null: permute X within stratum in both arms
        evn = ev.with_columns(pl.Series("Xn", SK.permute_within(ev["X"].to_numpy(), SK._codes(ev["stratum"].to_numpy()), rng)))
        if r < 10:
            fl = inflight(evn, B=60, seed=r, Xcol="Xn")
            out["dI_null"].append(fl)
        # read x erasure interaction: Y from agent base rates, read effect 0.8, planted interaction d
        d = ev.filter(pl.col("X") != NONE)
        base = d.group_by("agent").agg(((pl.col("X") == 0).mean()).alias("p0"))
        p0 = d.join(base, on="agent")["p0"].to_numpy().clip(0.02, 0.98)
        e = d["r1_read"].to_numpy().astype(float)
        f = (d["etype"] == "forced").to_numpy().astype(float)
        for dd in (0.0, 0.5, 1.0):
            lp = np.log(p0 / (1 - p0)) + 0.8 * e - 0.4 * e.mean() + dd * e * f
            Y = rng.random(len(lp)) < 1 / (1 + np.exp(-lp))
            ru = read_unread(ev, Y=Y, B=0)
            z = ru["inter"] / ru["se_inter"] if ru["se_inter"] and np.isfinite(ru["se_inter"]) else np.nan
            out["inter"].setdefault(str(dd), []).append({"inter": ru["inter"], "z": z})
        print(f"synthetic rep {r} {time.time() - t0:.0f}s", flush=True)
    # summaries
    s = {"I_null_mean": float(np.mean([x["I"] for x in out["I_null"]])),
         "I_null_identified_rate": float(np.mean([x["lo_jk"] > 0.02 for x in out["I_null"]]))}
    for q, v in out["I_plant"].items():
        s[f"I_plant_{q}_mean"] = float(np.mean([x["I"] for x in v]))
        s[f"I_plant_{q}_identified_rate"] = float(np.mean([x["lo_jk"] > 0.02 for x in v]))
    if out["dI_null"]:
        s["dI_null_mean"] = float(np.mean([x["dI"] for x in out["dI_null"]]))
        s["dI_null_ci_excludes0_rate"] = float(np.mean([(x["dI_ci"][0] or 0) > 0 or (x["dI_ci"][1] or 0) < 0
                                                        for x in out["dI_null"]]))
    for dd, v in out["inter"].items():
        z = np.array([x["z"] for x in v], float)
        s[f"inter_{dd}_mean"] = float(np.nanmean([x["inter"] for x in v]))
        s[f"inter_{dd}_rate_z_ge2"] = float(np.nanmean(z >= 1.96))
    out["summary"] = s
    (R.R2 / "r3_synthetic.json").write_text(json.dumps(R.jsonable(out), indent=1))
    print(json.dumps(R.jsonable(s), indent=1))


# ============================================================================ real
def real():
    ev = load_events()
    res = {"n_events": ev.group_by("etype").len().rows()}
    d = ev.filter(pl.col("etype").is_in(["forced", "placebo"]))
    # descriptive: re-read code distribution and outcome distribution
    for et in ("forced", "placebo", "voluntary"):
        g = ev.filter(pl.col("etype") == et)
        res[f"S_dist_{et}"] = (np.bincount(g["S"].to_numpy(), minlength=8) / max(g.height, 1)).tolist()
        res[f"X_dist_{et}"] = (np.bincount(g["X"].to_numpy(), minlength=8) / max(g.height, 1)).tolist()
        res[f"goal_read_{et}"] = float(g["open_goal"].mean()) if g.height else None
    t0 = time.time()
    res["store"] = kl_store(d)
    print("store", time.time() - t0, flush=True)
    res["read_unread"] = read_unread(d)
    print("read_unread", time.time() - t0, flush=True)
    res["inflight"] = inflight(d)
    print("inflight", time.time() - t0, flush=True)
    res["kappa_pooled"] = kappa_rows(d, B=300)
    print("kappa pooled", time.time() - t0, flush=True)
    # voluntary variant (scramble = voluntary consolidation), store and read/unread only
    dv = ev.filter(pl.col("etype").is_in(["voluntary", "placebo"])).with_columns(
        pl.when(pl.col("etype") == "voluntary").then(pl.lit("forced")).otherwise(pl.col("etype")).alias("etype"))
    res["voluntary"] = {"store": kl_store(dv, B=100), "read_unread": read_unread(dv, B=100)}
    # per goal period
    res["per_period"] = {}
    for g in sorted(d["goal_no"].unique().to_list()):
        dg = d.filter(pl.col("goal_no") == g)
        if (dg["etype"] == "forced").sum() < 100:
            continue
        rp = {"n_F": int((dg["etype"] == "forced").sum()), "n_P": int((dg["etype"] == "placebo").sum()),
              "store": kl_store(dg, B=100), "read_unread": read_unread(dg, B=100),
              "kappa": kappa_rows(dg, B=150)}
        res["per_period"][str(g)] = rp
        print("period", g, time.time() - t0, flush=True)
    (R.R2 / "r3_results.json").write_text(json.dumps(R.jsonable(res), indent=1))


def main():
    if "--synthetic" in sys.argv:
        reps = int(sys.argv[sys.argv.index("--reps") + 1]) if "--reps" in sys.argv else 30
        synthetic(reps)
    if "--real" in sys.argv:
        real()


if __name__ == "__main__":
    main()
