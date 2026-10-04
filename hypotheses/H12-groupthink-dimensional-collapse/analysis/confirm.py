"""H12 confirmatory test on the LOCKED HOLDOUT. Written 2026-10-03 after exploratory round 1; NOT RUN.

Pre-registered predictions (card, Amendment 2; thresholds fixed here before any holdout data is read):
  Held-out units (N >= 10 at period start, >= 2 days): #28, #29, #32a (02-23..02-24, regime I), #32b (02-25.., regime II),
  #34, #45, #46, #47, #49, #50, and the #51 tail (09-07 -> 09-21) as unit "51t". One-day periods #43 and #48 enter C4
  only if they have >= 3 days (they do not) and C5 as transition endpoints.
  C1  one collective activity mode: k_cd(activity) = 1 in >= 2/3 of held-out units.
  C2  Curie-Weiss shape: among units with k_cd >= 1, majority-sign share >= 0.8 AND VR/lambda1 >= 0.85 in >= 2/3.
  C3  lulls: Spearman(lull fraction, relative drop of lambda1/edge after the lull filter) >= 0.6 across held-out units.
  C4  content mode: k_cd(content) >= 1 in >= 2/3 of held-out units, AND it survives agent-day centering in >= 2/3.
  C5  kickoff-day expansion (the reversed P7): PRday(day 1) > median PRday(days 2+) in >= 2/3 of held-out periods
      with >= 3 days and a valid day 1 (28, 29, 32, 34, 45, 46, 47, 49, 50; #32 uses its first day, 02-23).
  C6  kickoffs do not collapse PR (the original P6, now predicted null-or-positive): over fully held-out transitions
      (28->29, 45->46, 46->47, 47->48, 48->49, 49->50) the median relative first-hour change is > 0.
  C7  original P9 test, kept as pre-registered before exploration: #22 (free, regime I) mean PRday above the median
      of the non-holdout regime-I shared weeks (14.82, fixed from round 1). Credence ~0.4.
  C8  looping confound: in held-out regime-III days, Spearman(within-agent near-duplicate share, PRday) <= -0.5.
Verdict: report each Ck pass/fail; no pooling with exploratory units.

Usage:
  uv run python .../analysis/confirm.py --dry-run          # same pipeline on NON-HOLDOUT stand-ins (allowed)
  uv run python .../analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout   # needs sign-off
Without one of these the script refuses to run.
"""
from __future__ import annotations

import json
import math
import sys

import h12lib as L
import numpy as np
import polars as pl
from scipy.stats import spearmanr

import run_units as R

FLAG_A, FLAG_B = "--confirm", "--i-understand-this-uses-the-locked-holdout"
HOLDOUT_GOALS = [28, 29, 32, 34, 45, 46, 47, 49, 50]
HOLDOUT_TAIL = ("2026-09-07", "2026-09-21")
SPLITS_HO = {32: ["2026-02-25"]}
TRANSITIONS_HO = [(28, 29), (45, 46), (46, 47), (47, 48), (48, 49), (49, 50)]
FREE_CHECK = 22
SHARED_I_MEDIAN_ROUND1 = 14.82
# Non-holdout stand-ins for --dry-run (same roles: units, transitions, a free week)
STANDIN_GOALS = [38, 39, 40, 41, 42]
STANDIN_TRANSITIONS = [(38, 39), (39, 40), (40, 41), (41, 42)]
STANDIN_FREE = 31
N_SURR = 200


def unit_name(g, d):
    if g == 51:
        return "51t"
    cuts = SPLITS_HO.get(g, [])
    k = sum(d >= c for c in cuts)
    return f"{g}{'ab'[k]}" if cuts else str(g)


def select_days(holdout: bool, goals):
    cal = pl.read_parquet(L.SH / "calendar.parquet").with_columns(pl.col("regime").cast(pl.String))
    hm = L.holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    cal = cal.with_columns(pl.Series("hm", hm))
    if holdout:
        sel = cal.filter(pl.col("hm") & (pl.col("goal_no").is_in(goals) | ((pl.col("goal_no") == 51) & (pl.col("pt_date") >= HOLDOUT_TAIL[0])
                                                                            & (pl.col("pt_date") < HOLDOUT_TAIL[1]))))
    else:
        sel = cal.filter(~pl.col("hm") & pl.col("goal_no").is_in(goals))
        assert not any(L.holdout_mask(sel["pt_date"].to_list(), sel["goal_no"].to_list())), "dry run touched the holdout"
    return sel.with_columns(pl.struct("goal_no", "pt_date").map_elements(lambda r: unit_name(r["goal_no"], r["pt_date"]),
                                                                        return_dtype=pl.String).alias("unit")).sort("pt_date")


def load_data(sel: pl.DataFrame):
    ab = (pl.scan_parquet(L.SH / "activity_bins.parquet").select("pt_date", "minute", "agent", "state")
          .filter(pl.col("pt_date").is_in(sel["pt_date"].to_list())).collect().join(sel.select("pt_date", "unit"), on="pt_date"))
    st = (pl.read_parquet(L.SH / "embeddings/statements.parquet").filter(pl.col("pt_date").is_in(sel["pt_date"].to_list()))
          .join(sel.select("pt_date", "unit"), on="pt_date"))
    Ec = np.load(L.SH / "embeddings/chat_bge_small.npy", mmap_mode="r"); Ei = np.load(L.SH / "embeddings/intentions_bge_small.npy", mmap_mode="r")
    sys.path.insert(0, str(L.ROOT / "infra/shared"))
    from common import load_whitener
    Wv = np.zeros((st.height, 64), dtype=np.float32)
    kind = st["kind"].to_numpy(); src = st["src_row"].to_numpy(); reg = st["regime"].to_numpy()
    for r in np.unique(reg):
        Wr = load_whitener(r, 64)
        for k, E in (("chat", Ec), ("intent", Ei)):
            m = (reg == r) & (kind == k)
            if m.any():
                Wv[m] = Wr(np.asarray(E[src[m]], dtype=np.float32))
    st = st.with_row_index("row")
    return ab, st, Wv


def spin_days_mem(ab_u: pl.DataFrame, which: str):
    nd = ab_u["pt_date"].n_unique()
    pres = ab_u.group_by("agent").agg(pl.col("pt_date").n_unique().alias("nd"), (pl.col("state") >= 3).sum().alias("na"))
    agents = sorted(pres.filter((pl.col("nd") == nd) & (pl.col("na") >= 30))["agent"].to_list())
    days = []
    for d in sorted(ab_u["pt_date"].unique().to_list()):
        x = ab_u.filter((pl.col("pt_date") == d) & pl.col("agent").is_in(agents))
        S = np.ones((len(agents), int(x["minute"].max()) + 1), dtype=np.int8)
        S[np.searchsorted(agents, x["agent"].to_numpy()), x["minute"].to_numpy()] = x["state"].to_numpy()
        days.append(np.where(S >= 3, 1, -1).astype(np.int8) if which == "act" else np.where(S == 4, 1, -1).astype(np.int8))
    X = np.concatenate(days, 1); keep = X.std(1) > 0
    return [d[keep] for d in days]


def unit_stats(u, ab, st, Wv, sel, rng):
    ab_u = ab.filter(pl.col("unit") == u)
    days = spin_days_mem(ab_u, "act")
    out = {"unit": u, "N": days[0].shape[0], "D": len(days)}
    if out["N"] >= 4 and len(days) >= 2:
        X = np.concatenate(days, 1)
        w, V, C = L.corr_eig(X, vectors=True)
        cd = L.spectrum_test(days, N_SURR, rng, "spin", "crossday")
        lu = L.spectrum_test(days, N_SURR, rng, "spin", "crossday", lull=True)
        u_ = np.ones(len(w)) / np.sqrt(len(w))
        out.update({"k_cd": cd["k"], "l1_edge": float(w[0] / cd["edge"]), "l1_edge_lull": float(lu["eig"][0] / lu["edge"]),
                    "lull_frac": float(1 - L.lull_filter(X).shape[1] / X.shape[1]), "sign_share": L.mode_summary(V[:, 0])["sign_share"],
                    "VR_l1": float(u_ @ C @ u_ / w[0])})
        out["lull_drop"] = 1 - out["l1_edge_lull"] / out["l1_edge"]
        cal_u = pl.read_parquet(L.SH / "calendar.parquet").filter(pl.col("pt_date").is_in(sel.filter(pl.col("unit") == u)["pt_date"].to_list()))
        rows = st.filter(pl.col("unit") == u)
        cdays, cag = R.content_days(u, rows, Wv, cal_u)
        if len(cag) >= 4:
            cc = L.spectrum_test(cdays, N_SURR, rng, "content", "crossday")
            dc = []
            for A in cdays:
                pres = np.abs(A).sum(2) > 0; mu = A.sum(1) / np.maximum(pres.sum(1), 1)[:, None]
                dc.append(np.where(pres[:, :, None], A - mu[:, None, :], 0.0))
            ccd = L.spectrum_test(dc, N_SURR, rng, "content", "crossday")
            out.update({"k_content": cc["k"], "k_content_dc": ccd["k"]})
    return out


def run(holdout: bool):
    goals = HOLDOUT_GOALS if holdout else STANDIN_GOALS
    trans = TRANSITIONS_HO if holdout else STANDIN_TRANSITIONS
    free = FREE_CHECK if holdout else STANDIN_FREE
    tgoals = sorted(set(goals) | {g for t in trans for g in t} | {free})
    sel = select_days(holdout, tgoals)
    ab, st, Wv = load_data(sel)
    rng = np.random.default_rng([L.SEED, 7 if holdout else 8])
    units = [u for u in sel["unit"].unique().sort().to_list() if int(u.rstrip("abt")) in goals or u == "51t"]
    res = [unit_stats(u, ab, st, Wv, sel, rng) for u in units]
    res = [r for r in res if r["N"] >= 10 and r["D"] >= 2]
    df = pl.DataFrame(res, infer_schema_length=None)
    # PR tables for all selected days
    p30s, pdays = [], []
    for u in sel["unit"].unique().to_list():
        a, b = R.pr_unit(u, st.filter(pl.col("unit") == u), Wv, rng)
        p30s.append(a); pdays.append(b)
    p30 = pl.concat(p30s, how="diagonal_relaxed"); pday = pl.concat(pdays, how="diagonal_relaxed")
    O = {"mode": "CONFIRM (holdout)" if holdout else "DRY RUN (non-holdout stand-ins)", "units": df.to_dicts()}
    O["C1"] = {"frac_k1": float((df["k_cd"] == 1).mean())}; O["C1"]["pass"] = O["C1"]["frac_k1"] >= 2 / 3
    s1 = df.filter(pl.col("k_cd") >= 1)
    O["C2"] = {"frac": float(((s1["sign_share"] >= 0.8) & (s1["VR_l1"] >= 0.85)).mean()) if s1.height else None}
    O["C2"]["pass"] = bool(O["C2"]["frac"] is not None and O["C2"]["frac"] >= 2 / 3)
    rho = spearmanr(df["lull_frac"], df["lull_drop"]).statistic if df.height >= 4 else float("nan")
    O["C3"] = {"rho": float(rho), "pass": bool(rho >= 0.6)}
    cc = df.filter(pl.col("k_content").is_not_null()) if "k_content" in df.columns else df.head(0)
    O["C4"] = {"frac_k": float((cc["k_content"] >= 1).mean()) if cc.height else None,
               "frac_dc": float((cc["k_content_dc"] >= 1).mean()) if cc.height else None}
    O["C4"]["pass"] = bool(cc.height and O["C4"]["frac_k"] >= 2 / 3 and O["C4"]["frac_dc"] >= 2 / 3)
    hi = n = 0
    for g in goals:
        dd = sorted(sel.filter(pl.col("goal_no") == g)["pt_date"].to_list())
        if len(dd) < 3:
            continue
        d1 = pday.filter(pl.col("pt_date") == dd[0])["prday"]; later = pday.filter(pl.col("pt_date").is_in(dd[1:]))["prday"].drop_nans()
        if len(d1) and d1[0] == d1[0] and len(later):
            n += 1; hi += int(d1[0] > later.median())
    O["C5"] = {"n": n, "day1_higher": hi, "pass": bool(n and hi / n >= 2 / 3)}
    rels = []
    for a, b in trans:
        da = sorted(sel.filter(pl.col("goal_no") == a)["pt_date"].to_list()); db = sorted(sel.filter(pl.col("goal_no") == b)["pt_date"].to_list())
        if not da or not db:
            continue
        fa = p30.filter((pl.col("pt_date") == da[-1]) & (pl.col("win30") <= 1))["pr"].drop_nans()
        fb = p30.filter((pl.col("pt_date") == db[0]) & (pl.col("win30") <= 1))["pr"].drop_nans()
        if len(fa) and len(fb):
            rels.append((fb.mean() - fa.mean()) / fa.mean())
    O["C6"] = {"n": len(rels), "median_rel": float(np.median(rels)) if rels else None, "pass": bool(rels and np.median(rels) > 0)}
    fd = sorted(sel.filter(pl.col("goal_no") == free)["pt_date"].to_list())
    fm = pday.filter(pl.col("pt_date").is_in(fd))["prday"].drop_nans().mean()
    O["C7"] = {"free_week": free, "prday_mean": fm, "threshold": SHARED_I_MEDIAN_ROUND1, "pass": bool(fm is not None and fm > SHARED_I_MEDIAN_ROUND1)}
    # C8: within-agent near-duplicate share per regime-III day, from the in-memory statements (works on holdout days)
    E = np.load(L.SH / "embeddings/chat_bge_small.npy", mmap_mode="r")
    rows8 = []
    for d in sel.filter(pl.col("regime") == "III")["pt_date"].to_list():
        x = st.filter((pl.col("pt_date") == d) & (pl.col("kind") == "chat"))
        if x.height < 20:
            continue
        V = np.asarray(E[x["src_row"].to_numpy()], dtype=np.float32); S = V @ V.T; np.fill_diagonal(S, 0)
        a = x["agent"].to_numpy(); same = a[:, None] == a[None, :]
        rows8.append({"pt_date": d, "dup_within": float((np.where(same, S, 0).max(1) > 0.95).mean())})
    if rows8:
        j = pday.join(pl.DataFrame(rows8), on="pt_date").filter(pl.col("prday").is_not_nan())
        r8 = spearmanr(j["dup_within"], j["prday"]).statistic
        O["C8"] = {"n_days": j.height, "rho": float(r8), "pass": bool(r8 <= -0.5)}
    else:
        O["C8"] = {"n_days": 0, "pass": None}
    outdir = L.OUT / ("confirm" if holdout else "confirm_dryrun")
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "confirm_results.json").write_text(json.dumps(O, indent=1, default=float))
    print(json.dumps({k: (v.get("pass") if isinstance(v, dict) else None) for k, v in O.items() if k.startswith("C")}, indent=1))
    return O


def main():
    argv = sys.argv[1:]
    if "--dry-run" in argv:
        run(holdout=False)
        return
    if FLAG_A in argv and FLAG_B in argv:
        print("CONFIRMATORY RUN ON THE LOCKED HOLDOUT (H12, Amendment 2).", flush=True)
        run(holdout=True)
        return
    print("Refusing to run: this script reads the locked holdout. Use --dry-run for non-holdout stand-ins, or\n"
          f"  {FLAG_A} {FLAG_B}\nafter sign-off (predictions: card Amendment 2).", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
