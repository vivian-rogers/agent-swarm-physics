"""H01 CONFIRMATORY test of D3.2 (coupling) on the LOCKED HOLDOUT: the real channel cuts (#voted-out inside #34,
the NE15 #best/#rest split on 2026-03-16) with NE12 (2026-02-25, no pair separated) as a placebo, plus transfer of
P1/P6/P9 to held-out two-room periods (#45-#47). WRITTEN 2026-10-03 after exploratory round 1. NOT RUN.

!!! Running with --confirm consumes the holdout for H01. It refuses unless BOTH flags are given:
!!!     --confirm --i-understand-this-uses-the-locked-holdout
!!! --dry-run runs every code path on NON-holdout stand-in windows and asserts that no holdout day is touched.

Design (reuses the exploratory estimators in h01lib / explore; one whitening basis per window, fitted on non-holdout
data only and loaded from the scheme: regime II basis for the 02-09..03-20 window, regime III for the transfer window):
  A  NE12 placebo (02-25). Assert from room membership that no pair is separated across 02-25. All-pair mean residual
     cosine, post (02-25..03-04) - pre (02-16..02-24), with a day-block bootstrap CI.
  B  #voted-out (03-05..03-13): pairs (voted-out agent x others) are separated on the days the agent sat in room 1;
     enters the pooled TWFE (D) through the daily co-location indicator.
  C  NE15 split: cut arm = pairs in different rooms over 03-16..03-20 that were co-located before; stay = co-located
     before and after. Pre = #33 + #34 days, post = #35. DiD of the rarefied residual cosine with pair and day fixed
     effects; pair-clustered SE; assignment permutation of the post-split room labels (sizes kept).
  D  Pooled TWFE over 02-09..03-20: r_ij,d = a_ij + g_d + b * coloc_ij,d.
  E  Transfer (axis I): P1 room-vs-random entropy on held-out two-room days (#45-#47), P6 exposure slope per held-out
     unit (RE summary), P9 mean-field fit per held-out unit.
Residual cosine r_ij = cos of the agent-day vectors (8 statements, 10 draws) after projecting out span{g-hat,
h_i, h_j}; h_i = the agent's first day in the analysis window (Amendment 3 rule, one h across each boundary; that day
is dropped).

Usage:
  UV_OFFLINE=1 HF_HUB_OFFLINE=1 uv run --with sentence-transformers python \\
      hypotheses/H01-emergent-superagents-exist/analysis/confirm_d32.py --dry-run
  ... --confirm --i-understand-this-uses-the-locked-holdout        # CONSUMES THE HOLDOUT; needs sign-off
Writes data/processed/H01-emergent-superagents-exist/confirm[_dryrun]/ (window tables + confirm_d32.json).
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "scheme"))
DRY = "--dry-run" in sys.argv
CONFIRM = "--confirm" in sys.argv and "--i-understand-this-uses-the-locked-holdout" in sys.argv
if not (DRY or CONFIRM):
    sys.exit("Refusing to run: pass --dry-run (non-holdout stand-ins) or "
             "--confirm --i-understand-this-uses-the-locked-holdout (consumes the H01 holdout; needs sign-off).")
if DRY and CONFIRM:
    sys.exit("Pass either --dry-run or --confirm, not both.")
sys.argv = [sys.argv[0]]  # keep explore's CLI parser at its defaults

from h01common import OUT, SEED, assign, guard_holdout, holdout_days, load_basis, unit, unit_of, whiten_apply  # noqa: E402
from h01data import Scheme  # noqa: E402
from h01lib import (fe_slope, mf_fit, pair_table, partition_test, random_effects, rarefied_counts,  # noqa: E402
                    rarefied_vectors, rotate_agents)
import build  # noqa: E402
import explore  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

CARD = HERE.parent / "README.md"
ODIR = OUT / ("confirm_dryrun" if DRY else "confirm")

# ============================================================================ pre-registered predictions
# Written 2026-10-03 after exploratory round 1 (see the card's Results), before any holdout outcome was computed.
PREDICTIONS = {
    "C1_ne15_cut_did": "NE15 cut arm (pairs separated by the 03-16 split) vs stay pairs: DiD of the rarefied residual cosine < 0, "
                       "pair-clustered 95% CI excluding 0 AND assignment-permutation one-sided p < 0.05. Exploration: the 05-04 merge "
                       "(an 'add') gave +0.18 (first-day h) / +0.10 (cross-fitted h); expected size here -0.05 to -0.20.",
    "C2_stay_hold": "Descriptive: stay-pair change post - pre (a goal change, #34 -> #35, shifts every pair; exploration's merge week "
                    "raised stay pairs by +0.2). Not decisive.",
    "C3_twfe": "Pooled TWFE over 02-09..03-20: beta(co-location) > 0 with pair-clustered z > 1.96.",
    "C4_ne12_placebo": "No pair is separated across 02-25 (asserted). The all-pair mean residual cosine does not drop at 02-25: the "
                       "day-block bootstrap 95% CI of post - pre includes 0 or lies above it.",
    "C5_toward_field_only": "After the split the cut arm's mean residual cosine moves toward the rotation-null (field-only) level: "
                            "|post - null| < |pre - null|.",
    "C6_transfer": "Held-out two-room days (#45-#47): P1 rule (>= 60% of days dH < 0 AND median dH <= -0.1 nats); exploration gave "
                   "96% and -0.098, so the size part is a coin flip. P6 RE exposure slope over held-out units > 0 (direction only; "
                   "exploration +0.013, p = 0.02). P9: beta*J0/n >= 0.5 expected in most held-out units (P9's original prediction is "
                   "expected to FAIL again; exploration median 0.74).",
    "overall": "D3.2 (coupling) confirmed if C1 and C3 pass and C4 holds. Refuted if C1 and C3 both have the wrong sign, or both CIs "
               "contain 0 with |effect| < 0.05 (half the smaller exploratory merge DiD). Otherwise inconclusive. Power is low: ~40 cut "
               "pairs and 5 post days.",
}

if CONFIRM:
    W = {"A_pre": ("2026-02-16", "2026-02-24"), "A_post": ("2026-02-25", "2026-03-04"),
         "C_pre": ("2026-03-02", "2026-03-13"), "C_post": ("2026-03-16", "2026-03-20"),
         "D_all": ("2026-02-09", "2026-03-20"), "E_all": ("2026-06-01", "2026-06-19")}
    BASIS = {"D_all": "II", "E_all": "III"}
    EXTRA_SPLITS = {32: ["2026-02-25"]}
    GPT5_LIKE = []
else:  # stand-ins: placebo = #41 -> #42 (goal change, no room change); split = 05-11 (#40 merged -> #41 split);
    #        voted-out analogue = #focus (two agents leave #general 08-05) is not in this window; TWFE window #39-#42.
    W = {"A_pre": ("2026-05-11", "2026-05-15"), "A_post": ("2026-05-18", "2026-05-22"),
         "C_pre": ("2026-05-04", "2026-05-08"), "C_post": ("2026-05-11", "2026-05-15"),
         "D_all": ("2026-04-27", "2026-05-22"), "E_all": ("2026-05-11", "2026-05-22")}
    BASIS = {"D_all": "III", "E_all": "III"}
    EXTRA_SPLITS = {}
    GPT5_LIKE = [10]   # GPT-5 sat alone in #rest during the merge week; excluded from the stand-in arms


def card_hash():
    txt = CARD.read_text()
    a = txt.index("## Prediction"); b = txt.index("## Results")
    return hashlib.sha256(txt[a:b].encode()).hexdigest()[:16]


def cal_days(lo, hi):
    cal = pl.read_parquet(build.SH / "calendar.parquet")
    return sorted(cal.filter((pl.col("pt_date") >= lo) & (pl.col("pt_date") <= hi) & (pl.col("goal_no") > 0))["pt_date"].to_list())


# ============================================================================ window tables (scheme layout)
def build_window(key, days, rng):
    held = holdout_days()
    if DRY:
        guard_holdout(days)
        assert not (set(days) & held), "dry run touched a holdout day"
    out = ODIR / key
    out.mkdir(parents=True, exist_ok=True)
    st = build.load_statements(days, allow_holdout=CONFIRM)
    if DRY:
        guard_holdout(sorted(st["pt_date"].unique().to_list()))
    st = st.with_columns(pl.struct("goal_no", "pt_date").map_elements(
        lambda s: (f"{s['goal_no']}{'ab'[int(s['pt_date'] >= EXTRA_SPLITS[s['goal_no']][0])]}" if s["goal_no"] in EXTRA_SPLITS
                   else unit_of(s["goal_no"], s["pt_date"])), return_dtype=pl.Utf8).alias("unit"),
        pl.lit(BASIS[key]).alias("regime"))
    b = load_basis(BASIS[key])
    X = build.raw_embeddings(st)
    Z = whiten_apply(X, b, 64)
    lab = assign(unit(Z[:, :32]).astype(np.float32), b["centroids_k40_d32"])
    st.write_parquet(out / "statements.parquet")
    np.save(out / "vectors_w64.npy", Z.astype(np.float16))
    pl.DataFrame({"k20": lab, "k40": lab, "k80": lab, "k40_d16": lab, "k40_d64": lab}).write_parquet(out / "clusters.parquet")
    for R in ("I", "II", "III"):
        shutil.copy(OUT / f"basis_{BASIS[key]}.npz", out / f"basis_{R}.npz")
    cnt = st.group_by("agent", "pt_date").agg(pl.len().alias("n_stmt"), pl.col("unit").first(), pl.col("goal_no").first(),
                                              pl.col("regime").first())
    rm = build.room_membership(st, days)
    cnt.join(rm, on=["agent", "pt_date"], how="left").write_parquet(out / "agent_day.parquet")
    build.pair_exposure(days).write_parquet(out / "pair_day_exposure.parquet")
    meta, texts = build.goal_texts(st, days)
    G = build.embed_goal_texts(texts)
    np.save(out / "goals_raw.npy", G)
    rows = [{**m, "regime": BASIS[key], "gid": i} for i, m in enumerate(meta)]
    pl.DataFrame(rows, infer_schema_length=None).write_parquet(out / "goals.parquet")
    units = (st.group_by("unit").agg(pl.col("goal_no").first(), pl.col("pt_date").unique().sort().alias("days"),
                                     pl.col("agent").n_unique().alias("n_agents")).sort(pl.col("days").list.first()))
    (out / "units.json").write_text(json.dumps([{"unit": u, "goal_no": int(g), "regimes": [BASIS[key]], "days": list(d), "n_agents": int(n)}
                                                for u, g, d, n in units.iter_rows()], indent=1))
    return Scheme(d=32, allow_holdout=CONFIRM, base=out)


def panel(S: Scheme, days, rng):
    """Pair-day panel over `days`: rarefied residual cosine with one h per agent (its first window day, dropped)."""
    ad = S.ad.filter(pl.col("pt_date").is_in(days)).sort("pt_date")
    first, ndays = {}, {}
    for a, d in ad.select("agent", "pt_date").iter_rows():
        first.setdefault(a, d); ndays[a] = ndays.get(a, 0) + 1
    parts = []
    for name, ui in S.units.items():
        ud = [d for d in ui["days"] if d in days]
        if not ud:
            continue
        u = S.unit(name, days=ud)
        u.h = {a: S.adV[(a, first[a])] for a in np.unique(u.agents) if ndays.get(a, 0) >= 2}
        u.h_firstday = {a for a in u.h if first[a] in ud}
        Vr = rarefied_vectors(u, 8, 10, rng)
        pt = pair_table(u, n_min=8, Vover=Vr)
        if pt is None:
            continue
        pt["pt_date"] = np.array([ud[t] for t in pt["day"]]); pt["unit"] = np.array([name] * len(pt["r"]))
        Vrot, hrot, Vrr = rotate_agents(u, rng, extra=Vr)
        p0 = pair_table(u, n_min=8, Vover=Vrr, hover=hrot)
        pt["r_rot"] = p0["r"] if p0 is not None and len(p0["r"]) == len(pt["r"]) else np.full(len(pt["r"]), np.nan)
        parts.append(pt)
    P = {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}
    dmap = {d: i for i, d in enumerate(sorted(set(P["pt_date"])))}
    P["day"] = np.array([dmap[d] for d in P["pt_date"]])
    return P


def room_by_period(S: Scheme, days):
    """Each agent's modal room over `days` (time-weighted day rooms)."""
    ad = S.ad.filter(pl.col("pt_date").is_in(days) & pl.col("room_mode").is_not_null())
    out = {}
    for a, g in ad.group_by("agent"):
        out[int(a[0])] = int(g["room_mode"].mode().sort()[0])
    return out


def main():
    rng = np.random.default_rng(SEED)
    res = {"mode": "dry_run" if DRY else "CONFIRM", "run_at": dt.datetime.now(dt.timezone.utc).isoformat(),
           "card_prediction_hash": card_hash(), "predictions": PREDICTIONS, "windows": W, "basis": BASIS}
    if CONFIRM:
        print("!!! CONFIRMATORY RUN: consuming the H01 holdout.", flush=True)
    ODIR.mkdir(parents=True, exist_ok=True)
    days_D = cal_days(*W["D_all"])
    S = build_window("D_all", days_D, rng)
    P = panel(S, days_D, rng)
    # ---------------- A placebo
    dA0, dA1 = cal_days(*W["A_pre"]), cal_days(*W["A_post"])
    rA = room_by_period(S, dA0); rA1 = room_by_period(S, dA1)
    agents_both = sorted(set(rA) & set(rA1))
    separated = [(int(a), int(b)) for i, a in enumerate(agents_both) for b in agents_both[i + 1:]
                 if rA[a] == rA[b] and rA1[a] != rA1[b]]
    daymean = {d: float(P["r"][P["pt_date"] == d].mean()) for d in dA0 + dA1 if (P["pt_date"] == d).any()}
    pre = np.array([daymean[d] for d in dA0 if d in daymean]); post = np.array([daymean[d] for d in dA1 if d in daymean])
    boots = [rng.choice(post, len(post)).mean() - rng.choice(pre, len(pre)).mean() for _ in range(2000)]
    res["A_placebo"] = {"n_pairs_separated": len(separated), "separated_pairs": separated[:20],
                        "post_minus_pre": float(post.mean() - pre.mean()), "ci95": [float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))]}
    res["C4_pass"] = bool(len(separated) == 0 and res["A_placebo"]["ci95"][1] >= 0 and not res["A_placebo"]["ci95"][1] < 0)
    if CONFIRM:
        assert len(separated) == 0, "NE12 premise violated: a pair was separated across 02-25"
    # ---------------- D pooled TWFE (B enters through daily co-location)
    P["coloc"] = P["same"].astype(float)
    f = fe_slope(P, ["coloc"])
    res["D_twfe"] = None if f is None else {"beta": float(f["b"][0]), "se": float(f["se"][0]), "z": float(f["b"][0] / f["se"][0]),
                                             "n": f["n"], "n_pairs": f["n_pairs"]}
    res["C3_pass"] = bool(f is not None and f["b"][0] / f["se"][0] > 1.96)
    # ---------------- C split DiD
    dC0, dC1 = cal_days(*W["C_pre"]), cal_days(*W["C_post"])
    r0 = room_by_period(S, dC0); r1 = room_by_period(S, dC1)
    mC = np.isin(P["pt_date"], dC0 + dC1)
    post_ind = np.isin(P["pt_date"], dC1).astype(float)

    def arms(rpost):
        g = []
        for i, j in zip(P["i"], P["j"]):
            if i in GPT5_LIKE or j in GPT5_LIKE or i not in r0 or j not in r0 or i not in rpost or j not in rpost:
                g.append("na"); continue
            s0 = r0[i] == r0[j]; s1 = rpost[i] == rpost[j]
            g.append("stay" if s0 and s1 else ("cut" if s0 and not s1 else "other"))
        return np.array(g)
    G = arms(r1)
    m = mC & np.isin(G, ["stay", "cut"])
    P["treat"] = ((G == "cut") & (post_ind == 1)).astype(float)
    fC = fe_slope(P, ["treat"], mask=m)
    C = {"n_cut_pairs": int(len(np.unique((P["i"] * 1000 + P["j"])[m & (G == "cut")]))),
         "n_stay_pairs": int(len(np.unique((P["i"] * 1000 + P["j"])[m & (G == "stay")])))}
    if fC is not None:
        C.update({"did": float(fC["b"][0]), "se": float(fC["se"][0]), "ci95": [float(fC["b"][0] - 1.96 * fC["se"][0]), float(fC["b"][0] + 1.96 * fC["se"][0])]})
        ags = [a for a in r1 if a not in GPT5_LIKE]; labs = [r1[a] for a in ags]
        nulls = []
        for _ in range(500):
            rp = dict(r1); rp.update(dict(zip(ags, rng.permutation(labs))))
            Gp = arms(rp); mp = mC & np.isin(Gp, ["stay", "cut"])
            if (Gp[mp] == "cut").sum() == 0 or (Gp[mp] == "stay").sum() == 0:
                continue
            P["treat"] = ((Gp == "cut") & (post_ind == 1)).astype(float)
            fp = fe_slope(P, ["treat"], mask=mp)
            if fp is not None:
                nulls.append(float(fp["b"][0]))
        C["p_perm_one_sided"] = float((1 + np.sum(np.array(nulls) <= C["did"])) / (1 + len(nulls)))
        for g_ in ("cut", "stay"):
            for k, dd in (("pre", dC0), ("post", dC1)):
                mm = (G == g_) & np.isin(P["pt_date"], dd)
                C[f"{g_}_{k}_mean"] = float(P["r"][mm].mean()) if mm.any() else None
                C[f"{g_}_{k}_rot_mean"] = float(np.nanmean(P["r_rot"][mm])) if mm.any() else None
    res["C_split"] = C
    res["C1_pass"] = bool("did" in C and C["did"] < 0 and C["ci95"][1] < 0 and C["p_perm_one_sided"] < 0.05)
    if "cut_pre_mean" in C and C["cut_pre_mean"] is not None and C["cut_post_mean"] is not None:
        null = np.nanmean([C["cut_pre_rot_mean"], C["cut_post_rot_mean"]])
        res["C5_pass"] = bool(abs(C["cut_post_mean"] - null) < abs(C["cut_pre_mean"] - null))
    # ---------------- E transfer
    days_E = cal_days(*W["E_all"])
    SE = build_window("E_all", days_E, rng)
    E = {"P1_days": [], "P6": {}, "P9": {}}
    for name, ui in SE.units.items():
        u = SE.unit(name)
        for t in range(int(u.day.max()) + 1):
            idx = np.where((u.day == t) & (u.nstmt >= 8) & (u.room >= 0))[0]
            labs_ = u.room[idx]
            if len(idx) < 4 or (np.bincount(np.unique(labs_, return_inverse=True)[1]) >= 2).sum() < 2:
                continue
            E["P1_days"].append({"unit": name, "day": u.day_names[t], **partition_test(rarefied_counts(u, idx, 40, 8, 20, rng), labs_, 1000, rng)})
        two = len([r for r in np.unique(u.room) if r >= 0 and (u.room == r).sum() >= 2]) >= 2
        r6 = explore.unit_p56(u, rng, two)
        E["P6"][name] = {k: v for k, v in r6.items() if not isinstance(v, list)}
        f9 = mf_fit(u, rng)
        if f9 is not None:
            E["P9"][name] = f9
    dH = np.array([d["dH"] for d in E["P1_days"]])
    E["P1"] = {"n_days": int(len(dH)), "frac_dH_neg": float((dH < 0).mean()) if len(dH) else None,
               "median_dH": float(np.median(dH)) if len(dH) else None,
               "pass": bool(len(dH) and (dH < 0).mean() >= 0.6 and np.median(dH) <= -0.1)}
    s6 = [(v["slope"], v["slope_se"]) for v in E["P6"].values() if "slope" in v]
    E["P6_re"] = random_effects([a for a, _ in s6], [b for _, b in s6]) if len(s6) >= 2 else None
    E["P9_bJn"] = {k: v["bJ_over_n"] for k, v in E["P9"].items()}
    res["E_transfer"] = E
    res["overall"] = ("confirmed" if res["C1_pass"] and res["C3_pass"] and res["C4_pass"] else
                      "refuted" if ("did" in C and res["D_twfe"] and C["did"] >= 0 and res["D_twfe"]["beta"] <= 0) else "inconclusive")
    (ODIR / "confirm_d32.json").write_text(json.dumps(res, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    print(json.dumps({k: v for k, v in res.items() if k not in ("predictions", "E_transfer")}, indent=1, default=str))
    print("E_transfer P1", E["P1"], "P6_re", E["P6_re"], "P9", E["P9_bJn"])


if __name__ == "__main__":
    main()
