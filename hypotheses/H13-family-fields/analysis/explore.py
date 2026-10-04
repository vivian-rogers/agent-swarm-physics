"""H13 exploratory round 1 (non-holdout only; asserted): family fields, K x K family couplings, family vs room.

One pipeline run per goal-period unit (card: Observables a1-a5, b1-b2, c, d1), then the cross-unit steps the card
allows: the invariance check (a3), the fixed-offset rival (a4), newcomer classification (d2), NE32 (d3), and
random-effects summaries of the per-unit estimates.

Usage: uv run python hypotheses/H13-family-fields/analysis/explore.py [--fast] [--units 37,41]
Reads data/processed/H13-family-fields/G<NN>/u<unit>_*; writes G<NN>/results_u<unit>.json and explore.json.
"""
from __future__ import annotations

import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "infra/shared"))
import h13lib as L  # noqa: E402
from common import holdout_mask  # noqa: E402

ROOT = HERE.parents[2]
DATA = ROOT / "data/processed/H13-family-fields"
SH = ROOT / "data/processed/shared"
FAST = "--fast" in sys.argv
NP_FIELD = 1000 if FAST else 5000
NP = 400 if FAST else 2000
NBOOT = 100 if FAST else 500
warnings.simplefilter("ignore", RuntimeWarning)

TWO_ROOM = {"35", "36b", "37", "38a", "38b", "38c", "39", "41", "42", "44"}
ONE_ROOM = {"40", "51a", "51b", "51c", "51d", "51e"}
COUNTED = ["35", "36b", "37", "38a", "38b", "38c", "39", "40", "41", "42", "44", "51a", "51b", "51c", "51d"]
DESCRIPTIVE = ["51e"]
EXCLUDE_B = {"40": {10}, "51c": {6, 29}}          # agents alone in another room (GPT-5 in #rest; #focus pair)
BIG3 = ["Anthropic", "OpenAI", "Google"]
MIN_WORDS = 200


def roster():
    r = pl.read_parquet(SH / "roster.parquet", columns=["agent", "name", "lab"])
    return dict(zip(r["agent"].to_list(), r["lab"].to_list())), dict(zip(r["agent"].to_list(), r["name"].to_list()))


def load_unit(meta, u, base=DATA):
    g = meta[u]["gdir"]
    ad = pl.read_parquet(base / g / f"u{u}_agent_day.parquet")
    Vr = np.load(base / g / f"u{u}_agent_day_raw.npy").astype(np.float64)
    Vs = np.load(base / g / f"u{u}_agent_day_sty.npy").astype(np.float64)
    w = pl.read_parquet(base / g / f"u{u}_win30.parquet")
    Vw = np.load(base / g / f"u{u}_win30_raw.npy").astype(np.float64)
    tp = pl.read_parquet(base / g / f"u{u}_talk_pairday.parquet") if (base / g / f"u{u}_talk_pairday.parquet").exists() else None
    return ad, Vr, Vs, w, Vw, tp


def guard(days, goal):
    assert not any(holdout_mask(days, [goal] * len(days))), "holdout day in exploration"


# ----------------------------------------------------------------------------- per-unit pieces
def content_fields(ad, V, min_n=3, min_days=2, days_sel=None):
    m = (ad["n"] >= min_n).to_numpy()
    if days_sel is not None:
        m &= ad["pt_date"].is_in(days_sel).to_numpy()
    a = ad.filter(pl.Series(m))
    X = V[m]
    D = L.day_demean(X, a["pt_date"].to_numpy(), a["agent"].to_numpy())
    ags, H, nd = L.agent_means(D, a["agent"].to_numpy(), min_days=min_days)
    return ags, H, nd


def role_keep(ags, roles):
    n = len(ags)
    K = np.ones((n, n), bool)
    for i in range(n):
        for j in range(n):
            ri, rj = roles.get(str(ags[i])), roles.get(str(ags[j]))
            if i != j and ri is not None and ri == rj:
                K[i, j] = False
    return K


def agent_rooms(ad, ags, purity=0.9):
    out = []
    for a in ags:
        t = ad.filter((pl.col("agent") == a) & (pl.col("n") >= 1))
        rs = [r for r in t["room"].to_list() if r is not None]
        if not rs or len(set(rs)) != 1 or t["purity"].mean() < purity:
            out.append(-1)
        else:
            out.append(int(rs[0]))
    return np.array(out)


def lexical(ad, ags_all, lab_of, rng):
    mk = [c for c in ad.columns if c.startswith("m_")]
    g = ad.group_by("agent").agg(pl.col("words").sum(), *[pl.col(c).sum() for c in mk]).filter(pl.col("words") >= MIN_WORDS).sort("agent")
    ags = g["agent"].to_numpy()
    W = g["words"].to_numpy().astype(float)
    C = g.select(mk).to_numpy().astype(float)
    rate = C / W[:, None] * 1000
    labs = [lab_of[a] for a in ags]
    fam, multi = L.fam_labels(labs)
    K = len(multi)
    out = {"n_agents": int(len(ags))}
    gi = mk.index("m_genuinely")
    isA = np.array([l == "Anthropic" for l in labs])
    if isA.sum() >= 1 and (~isA).sum() >= 1:
        ga, go = rate[isA, gi].mean(), rate[~isA, gi].mean()
        obs = ga - go
        null = []
        for _ in range(NP_FIELD):
            p = rng.permutation(isA)
            null.append(rate[p, gi].mean() - rate[~p, gi].mean())
        out["genuinely"] = {"rate_anthropic": float(ga), "rate_others": float(go),
                            "ratio": float(ga / go) if go > 0 else float("inf"), "diff": float(obs),
                            "p": float((1 + np.sum(np.array(null) >= obs)) / (1 + len(null)))}
        out["genuinely_by_family"] = {l: float(rate[[x == l for x in labs], gi].mean()) for l in sorted(set(labs))}
    # profile family structure
    P = np.log1p(rate)
    sd = P.std(0)
    P = (P[:, sd > 0] - P[:, sd > 0].mean(0)) / sd[sd > 0]
    R = np.corrcoef(P) if len(P) >= 3 else np.full((len(P), len(P)), np.nan)
    ii, jj = L.pairs(len(ags))
    out["T_lex"] = L.wa_perm(R[ii, jj], ii, jj, fam, K, nperm=NP_FIELD, rng=rng) if K >= 1 and len(ags) >= 4 else None
    out["markers_rate_by_family"] = {l: {m[2:]: float(rate[[x == l for x in labs], k].mean()) for k, m in enumerate(mk)}
                                     for l in multi}
    return out, ags, R


def talk_kxk(tp, lab_of, excl, rng):
    t = tp.with_columns((pl.col("c0") - pl.col("c0_sur")).alias("c0_x")).filter(
        pl.col("c0_x").is_not_nan() & ~pl.col("i").is_in(list(excl)) & ~pl.col("j").is_in(list(excl)))
    ags = np.array(sorted(set(t["i"].to_list()) | set(t["j"].to_list())))
    days = sorted(t["pt_date"].unique().to_list())
    labs = [lab_of[a] for a in ags]
    fam, multi = L.fam_labels(labs)
    K = len(multi)
    pairs = sorted(set(zip(t["i"].to_list(), t["j"].to_list())))
    pk = {p: k for k, p in enumerate(pairs)}; dk = {d: k for k, d in enumerate(days)}
    Rm = np.full((len(pairs), len(days)), np.nan); Sv = np.full_like(Rm, np.nan)
    for i, j, d, r, ai, aj in t.select("i", "j", "pt_date", "c0_x", "act_i", "act_j").iter_rows():
        Rm[pk[(i, j)], dk[d]] = r
        Sv[pk[(i, j)], dk[d]] = np.sqrt(4 * ai * (1 - ai) * 4 * aj * (1 - aj))
    pa = np.array(pairs)
    ai = np.searchsorted(ags, pa[:, 0]); aj = np.searchsorted(ags, pa[:, 1])
    res = L.kxk_test(Rm, Sv, ai, aj, fam, K, nboot=NBOOT, nperm=NP, rng=rng)
    res.update({"families": multi, "n_agents": int(len(ags)), "n_days": len(days), "K": K})
    Y = np.full((len(ags), len(ags)), np.nan)
    with np.errstate(invalid="ignore"):
        rb = np.nanmean(Rm, 1)
    Y[ai, aj] = Y[aj, ai] = rb
    return res, ags, Y


def content_kxk(w, Vw, lab_of, excl, rng):
    m = (w["n"] >= 2).to_numpy() & ~w["agent"].is_in(list(excl)).to_numpy()
    ww = w.filter(pl.Series(m))
    V = Vw[m]
    agent = ww["agent"].to_numpy()
    win = (ww["pt_date"] + "_" + ww["win30"].cast(pl.String)).to_numpy()
    ags, X, keep = L.comove_matrix(agent, win, V)
    R = L.comove_r(ags, agent, win, X, keep)
    labs = [lab_of[a] for a in ags]
    fam, multi = L.fam_labels(labs)
    K = len(multi)
    ii, jj = L.pairs(len(ags))
    r = R[ii, jj]; ok = np.isfinite(r)
    out = {"families": multi, "n_agents": int(len(ags)), "K": K, "n_windows": int(len(np.unique(win[keep]))),
           "mean_r": float(np.nanmean(r))}
    if ok.sum() < 5 or K < 1:
        return out, ags, R
    q = L.kxk_from_pairs(ii[ok], jj[ok], r[ok], np.ones(ok.sum()), fam, K)
    out.update({"J_in": q["J_in"], "J_out": q["J_out"], "delta": q["J_in_minus_out"], "loop_gain": q["loop_gain"],
                "M": q["M"].tolist()})
    null = np.array([L.block_J(ii[ok], jj[ok], r[ok], np.ones(ok.sum()), rng.permutation(fam))["J_in_minus_out"] for _ in range(NP)])
    null = null[np.isfinite(null)]
    out["p_perm"] = float((1 + np.sum(null >= q["J_in_minus_out"])) / (1 + len(null)))

    def jk(mm):
        sub = np.flatnonzero(mm)
        i2, j2 = L.pairs(len(sub))
        rr = R[np.ix_(sub, sub)][i2, j2]; o2 = np.isfinite(rr)
        if o2.sum() < 5:
            return np.nan
        return L.block_J(i2[o2], j2[o2], rr[o2], np.ones(o2.sum()), fam[sub])["J_in_minus_out"]
    out["delta_se_jack"] = L.jackknife_se(jk, len(ags))
    out["r_within_minus_across"] = L.wa_perm(r[ok], ii[ok], jj[ok], fam, K, nperm=NP, rng=rng)
    # variant: window-demeaned contrast
    ags2, X2, keep2 = L.comove_matrix(agent, win, V, window_demean=True)
    R2 = L.comove_r(ags2, agent, win, X2, keep2)
    f2 = L.fam_labels([lab_of[a] for a in ags2])[0]
    i2, j2 = L.pairs(len(ags2)); r2 = R2[i2, j2]; o2 = np.isfinite(r2)
    out["variant_windowdemeaned_contrast"] = L.wa_perm(r2[o2], i2[o2], j2[o2], f2, K, nperm=NP, rng=rng)
    return out, ags, R


def embed_matrix(Y, ags_y, ags):
    """re-index a pair matrix Y (over ags_y) onto ags (NaN where absent)."""
    pos = {a: k for k, a in enumerate(ags_y)}
    n = len(ags)
    Z = np.full((n, n), np.nan)
    for x in range(n):
        for y in range(n):
            if x != y and ags[x] in pos and ags[y] in pos:
                Z[x, y] = Y[pos[ags[x]], pos[ags[y]]]
    return Z


def run_unit(meta, u, lab_of, rng, base=DATA):
    t0 = time.time()
    m = meta[u]
    guard(m["days"], m["goal_no"]) if base == DATA else None
    ad, Vr, Vs, w, Vw, tp = load_unit(meta, u, base)
    roles = m.get("roles", {})
    res = {"unit": u, "gdir": m["gdir"], "goal_no": m["goal_no"], "regime": m["regime"], "n_days": len(m["days"]),
           "counted": u in COUNTED}
    # (a1) raw field
    ags, H, nd = content_fields(ad, Vr)
    labs = [lab_of[a] for a in ags]
    fam, multi = L.fam_labels(labs)
    K = len(multi)
    keep = role_keep(ags, roles) if roles else None
    res["N"] = int(len(ags)); res["families"] = {f: int(labs.count(f)) for f in multi}; res["K"] = K
    res["a1"] = L.field_test(H, fam, K, keep_pairs=keep, nperm=NP_FIELD, rng=rng)
    res["a1"]["R2_fam"] = L.r2_perm(H, fam, K, nperm=NP, rng=rng)
    hf = L.family_fields(H, fam, K)
    res["a1"]["h_norm"] = {multi[k]: float(np.linalg.norm(v)) for k, v in hf.items()}
    # rotation sanity floor
    rot = []
    for _ in range(200):
        Hr = np.array([L.random_rotation(H.shape[1], rng) @ h for h in H])
        ii, jj = L.pairs(len(H)); C = L.unit(Hr) @ L.unit(Hr).T
        rot.append(L.wa_stat(C[ii, jj], ii, jj, fam, K, keep[ii, jj] if keep is not None else None))
    res["a1"]["rotation_null_mean"] = float(np.nanmean(rot)); res["a1"]["rotation_null_sd"] = float(np.nanstd(rot))
    # (a2) style residualized
    ags_s, Hs, _ = content_fields(ad, Vs)
    assert np.array_equal(ags_s, ags)
    res["a2"] = L.field_test(Hs, fam, K, keep_pairs=keep, nperm=NP_FIELD, rng=rng)
    res["a2"]["retention"] = float(res["a2"]["obs"] / res["a1"]["obs"]) if res["a1"]["obs"] > 0 else np.nan
    res["style_r2"] = m["style_r2"]
    # (d1) leave-one-agent-out classification
    res["d1"] = L.loo_perm(H, fam, K, nperm=NP, rng=rng)
    res["d1"]["chance_mean"] = res["d1"]["null_mean"]
    res["d1_style"] = L.loo_perm(Hs, fam, K, nperm=NP // 2, rng=rng)
    # B: within-unit stationarity (first vs second half of days)
    days = sorted(m["days"])
    if len(days) >= 4:
        h1, h2 = days[: len(days) // 2], days[len(days) // 2:]
        a1_, H1, _ = content_fields(ad, Vr, days_sel=h1, min_days=1)
        a2_, H2, _ = content_fields(ad, Vr, days_sel=h2, min_days=1)
        st = {}
        for f in multi:
            m1 = [H1[k] for k, a in enumerate(a1_) if lab_of[a] == f]; m2 = [H2[k] for k, a in enumerate(a2_) if lab_of[a] == f]
            if m1 and m2:
                st[f] = float(L.unit(np.mean(L.unit(np.array(m1)), 0)) @ L.unit(np.mean(L.unit(np.array(m2)), 0)))
        res["B_splithalf_family_cos"] = st
    # (a5) lexical
    lex, ags_lex, Rlex = lexical(ad, ags, lab_of, rng)
    res["a5"] = lex
    # (b1) talk
    excl = EXCLUDE_B.get(u, set())
    if tp is not None and tp.height:
        tk, ags_t, Yt = talk_kxk(tp, lab_of, excl, rng)
        res["b1"] = tk
    else:
        ags_t, Yt = np.array([]), np.zeros((0, 0))
    # (b2) content co-movement
    ck, ags_c, Rc = content_kxk(w, Vw, lab_of, excl, rng)
    res["b2"] = ck
    # (c) family vs room
    if u in TWO_ROOM:
        rooms = agent_rooms(ad, ags)
        res["rooms"] = {str(a): int(r) for a, r in zip(ags, rooms)}
        Y2 = L.unit(H) @ L.unit(H).T
        outc = {"y1_talk": embed_matrix(Yt, ags_t, ags) if len(ags_t) else None, "y2_field": Y2,
                "y3_comove": embed_matrix(Rc, ags_c, ags), "y4_lexical": embed_matrix(Rlex, ags_lex, ags)}
        res["c"] = {}
        for k, Y in outc.items():
            if Y is None:
                continue
            res["c"][k] = L.famroom(Y, fam, rooms, K, nperm=NP, rng=rng)
        res["c"]["n_room_known"] = int((rooms >= 0).sum())
        # lab x room table
        res["c"]["lab_room"] = {f"{lab_of[a]}|{r}": 0 for a, r in zip(ags, rooms)}
        for a, r in zip(ags, rooms):
            res["c"]["lab_room"][f"{lab_of[a]}|{r}"] += 1
    res["_H"] = {int(a): L.unit(h).tolist() for a, h in zip(ags, H)}
    res["_Hs"] = {int(a): L.unit(h).tolist() for a, h in zip(ags, Hs)}
    res["seconds"] = round(time.time() - t0, 1)
    print(f"unit {u}: N={res['N']} K={K} T={res['a1']['obs']:.3f} p={res['a1']['p']:.4f} | sty T={res['a2']['obs']:.3f} "
          f"p={res['a2']['p']:.4f} | loo={res['d1']['obs']:.2f} p={res['d1']['p']:.3f} | "
          f"talk d={res.get('b1', {}).get('delta', np.nan):.3f} p={res.get('b1', {}).get('p_perm', np.nan):.3f} | "
          f"content d={res['b2'].get('delta', np.nan):.3f} p={res['b2'].get('p_perm', np.nan):.3f} | {res['seconds']}s", flush=True)
    return res


# ----------------------------------------------------------------------------- cross-unit steps
def cross_unit(results, meta, lab_of, name_of, rng):
    out = {}
    r3 = [u for u in COUNTED if meta[u]["regime"] == "III" and u in results]
    Hu = [{int(a): np.array(v) for a, v in results[u]["_H"].items()} for u in r3]
    out["a3"] = L.invariance(Hu, lab_of, BIG3, nperm=NP, rng=rng)
    out["a3"]["units_order"] = r3
    Hus = [{int(a): np.array(v) for a, v in results[u]["_Hs"].items()} for u in r3]
    out["a3_style"] = L.invariance(Hus, lab_of, BIG3, nperm=NP // 2, rng=rng)
    fam_pass = (out["a3"]["family_median"] >= 0.5) and (out["a3"]["p_regroup"] < 0.05)
    out["a3"]["pass_family"] = bool(fam_pass)
    out["a3"]["pass_agent"] = bool(out["a3"]["agent_median"] >= 0.5)
    print("a3 invariance:", {k: out["a3"][k] for k in ("family_cos", "family_median", "null_regroup_median_mean", "p_regroup", "agent_median")}, flush=True)
    # (a4) fixed-offset rival S-b
    out["a4"] = {}
    for k, u in enumerate(r3):
        h = Hu[k]
        ags = sorted(a for a in h if any(a in Hu[j] for j in range(len(r3)) if j != k))
        if len(ags) < 5:
            continue
        S = np.array([np.mean([Hu[j][a] for j in range(len(r3)) if j != k and a in Hu[j]], 0) for a in ags])
        Hn = np.array([h[a] for a in ags])
        proj, sub = L.fixed_offset_residual(Hn, S)
        labs = [lab_of[a] for a in ags]
        fam, multi = L.fam_labels(labs)
        K = len(multi)
        roles = meta[u].get("roles", {})
        keep = role_keep(np.array(ags), roles) if roles else None
        t0 = L.field_test(Hn, fam, K, keep_pairs=keep, nperm=NP, rng=rng, jack=False)
        tp = L.field_test(proj, fam, K, keep_pairs=keep, nperm=NP_FIELD, rng=rng, jack=True)
        ts = L.field_test(sub, fam, K, keep_pairs=keep, nperm=NP, rng=rng, jack=False)
        out["a4"][u] = {"n": len(ags), "T_subset": t0["obs"], "T_proj": tp["obs"], "p_proj": tp["p"], "se_proj": tp.get("se_jack"),
                        "T_sub": ts["obs"], "p_sub": ts["p"],
                        "ratio_proj": float(tp["obs"] / t0["obs"]) if t0["obs"] > 0 else np.nan}
    # (d2) newcomers: classified by incumbent family fields of earlier regime III units (counted only if a3 passes)
    first = {}
    for k, u in enumerate(r3 + [x for x in DESCRIPTIVE if x in results]):
        for a in results[u]["_H"]:
            first.setdefault(int(a), u)
    order = r3 + [x for x in DESCRIPTIVE if x in results]
    newcomers = [a for a, u in first.items() if results[u]["goal_no"] == 51]
    d2 = []
    for a in newcomers:
        u = first[a]
        k = order.index(u)
        prev = order[:k]
        if not prev:
            continue
        # incumbent family fields: mean over earlier units of unit(mean of members' H)
        flds = {}
        for pu in prev:
            hh = results[pu]["_H"]
            byl = {}
            for b, v in hh.items():
                byl.setdefault(lab_of[int(b)], []).append(np.array(v))
            for l, vs in byl.items():
                flds.setdefault(l, []).append(L.unit(np.mean(vs, 0)))
        flds = {l: L.unit(np.mean(v, 0)) for l, v in flds.items()}
        if lab_of[a] not in flds:
            continue
        # newcomer vector: first <= 3 eligible days in its first unit
        ad, Vr, *_ = load_unit(meta, u)
        mm = (ad["n"] >= 3).to_numpy()
        a_ad = ad.filter(pl.Series(mm))
        X = Vr[mm]
        D = L.day_demean(X, a_ad["pt_date"].to_numpy(), a_ad["agent"].to_numpy())
        rows = np.flatnonzero((a_ad["agent"].to_numpy() == a) & np.isfinite(D).all(1))[:3]
        if len(rows) == 0:
            continue
        x = L.unit(D[rows].mean(0))
        sims = {l: float(x @ v) for l, v in flds.items()}
        pred = max(sims, key=sims.get)
        rank = sorted(sims, key=sims.get, reverse=True).index(lab_of[a]) + 1
        d2.append({"agent": a, "name": name_of[a], "lab": lab_of[a], "unit": u, "days_used": int(len(rows)),
                   "pred": pred, "correct": pred == lab_of[a], "rank": rank, "n_candidates": len(flds),
                   "sim_own": sims[lab_of[a]]})
    acc = float(np.mean([x["correct"] for x in d2])) if d2 else np.nan
    chance = float(np.mean([1 / x["n_candidates"] for x in d2])) if d2 else np.nan
    from scipy.stats import binomtest
    ncorr = int(sum(x["correct"] for x in d2))
    out["d2"] = {"newcomers": d2, "accuracy": acc, "chance": chance, "n": len(d2),
                 "p_binom": float(binomtest(ncorr, len(d2), chance, alternative="greater").pvalue) if d2 else np.nan,
                 "mean_rank": float(np.mean([x["rank"] for x in d2])) if d2 else np.nan,
                 "counted": bool(fam_pass)}
    print("d2 newcomers:", out["d2"]["accuracy"], "chance", chance, "n", len(d2), flush=True)
    # (d3) NE32: GPT-5.6 triplet on 07-09 vs incumbent family fields of 51b (excluding 07-09/07-10)
    if "51b" in results:
        ad, Vr, *_ = load_unit(meta, "51b")
        mm = (ad["n"] >= 3).to_numpy()
        a_ad = ad.filter(pl.Series(mm)); X = Vr[mm]
        D = L.day_demean(X, a_ad["pt_date"].to_numpy(), a_ad["agent"].to_numpy())
        ag = a_ad["agent"].to_numpy(); dd = a_ad["pt_date"].to_numpy()
        trip = [35, 36, 37]
        later = ~np.isin(dd, ["2026-07-09", "2026-07-10"]) & ~np.isin(ag, trip) & np.isfinite(D).all(1)
        byl = {}
        for b in np.unique(ag[later]):
            byl.setdefault(lab_of[int(b)], []).append(L.unit(D[later & (ag == b)].mean(0)))
        flds = {l: L.unit(np.mean(v, 0)) for l, v in byl.items() if l in BIG3}
        d3 = {}
        for t in trip:
            r = np.flatnonzero((ag == t) & (dd == "2026-07-09") & np.isfinite(D).all(1))
            if len(r):
                x = L.unit(D[r[0]])
                d3[name_of[t]] = {l: float(x @ v) for l, v in flds.items()}
        # pairwise among the triplet on 07-09 (unexposed to each other)
        r = [np.flatnonzero((ag == t) & (dd == "2026-07-09") & np.isfinite(D).all(1)) for t in trip]
        vv = [L.unit(D[x[0]]) for x in r if len(x)]
        inc = np.flatnonzero((dd == "2026-07-09") & ~np.isin(ag, trip) & np.isfinite(D).all(1))
        d3["_triplet_mutual_cos"] = float(np.mean([vv[i] @ vv[j] for i in range(len(vv)) for j in range(i + 1, len(vv))])) if len(vv) > 1 else None
        d3["_triplet_vs_incumbent_cos"] = float(np.mean([v @ L.unit(D[k]) for v in vv for k in inc])) if vv else None
        d3["_n_statements_0709"] = {name_of[t]: int(a_ad.filter((pl.col("agent") == t) & (pl.col("pt_date") == "2026-07-09"))["n"].sum()) for t in trip}
        out["d3"] = d3
    return out


def meta_summaries(results):
    cu = [u for u in COUNTED if u in results]
    S = {}

    def add(name, f_est, f_se, units):
        e = [f_est(results[u]) for u in units]; s = [f_se(results[u]) for u in units]
        S[name] = L.dl_meta(e, s); S[name]["units"] = units
        S[name]["per_unit"] = {u: [x, y] for u, x, y in zip(units, e, s)}
    g = lambda d, *ks: (lambda r: _get(r, ks))
    add("T_field", lambda r: r["a1"]["obs"], lambda r: r["a1"]["se_jack"], cu)
    add("T_field_style", lambda r: r["a2"]["obs"], lambda r: r["a2"]["se_jack"], cu)
    add("delta_talk", lambda r: r.get("b1", {}).get("delta", np.nan), lambda r: r.get("b1", {}).get("delta_se", np.nan), cu)
    add("delta_talk_oneroom", lambda r: r.get("b1", {}).get("delta", np.nan), lambda r: r.get("b1", {}).get("delta_se", np.nan),
        [u for u in cu if u in ONE_ROOM])
    add("delta_content", lambda r: r["b2"].get("delta", np.nan), lambda r: r["b2"].get("delta_se_jack", np.nan), cu)
    tr = [u for u in cu if u in TWO_ROOM]
    for y in ("y1_talk", "y2_field", "y3_comove", "y4_lexical"):
        add(f"b_lab_{y}", lambda r, y=y: r["c"].get(y, {}).get("b_lab", np.nan), lambda r, y=y: r["c"].get(y, {}).get("se_lab", np.nan), tr)
        add(f"b_room_{y}", lambda r, y=y: r["c"].get(y, {}).get("b_room", np.nan), lambda r, y=y: r["c"].get(y, {}).get("se_room", np.nan), tr)
    return S


def _get(r, ks):
    for k in ks:
        r = r.get(k, {}) if isinstance(r, dict) else {}
    return r if not isinstance(r, dict) else np.nan


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


def main():
    t0 = time.time()
    rng = np.random.default_rng(20261004)
    meta = json.loads((DATA / "units.json").read_text())
    lab_of, name_of = roster()
    sel = sys.argv[sys.argv.index("--units") + 1].split(",") if "--units" in sys.argv else COUNTED + DESCRIPTIVE
    results = {}
    for u in sel:
        results[u] = run_unit(meta, u, lab_of, rng)
        r = {k: v for k, v in results[u].items() if not k.startswith("_")}
        (DATA / meta[u]["gdir"] / f"results_u{u}.json").write_text(json.dumps(clean(r), indent=1))
    out = {"units": {u: {k: v for k, v in r.items() if not k.startswith("_")} for u, r in results.items()}}
    if "--units" not in sys.argv:
        out["cross"] = cross_unit(results, meta, lab_of, name_of, rng)
        out["meta"] = meta_summaries(results)
        for k, v in out["meta"].items():
            if "mu" in v:
                print(f"meta {k}: mu={v['mu']:.4f} [{v['lo']:.4f}, {v['hi']:.4f}] I2={v['I2']:.2f} k={v['k']}", flush=True)
        # keep unit-normalized agent fields for the confirmatory transfer test (regime III, counted units)
        np.savez_compressed(DATA / "agent_fields_explore.npz",
                            **{f"u{u}": np.array([[a] + v for a, v in results[u]["_H"].items()]) for u in results})
    out["seconds"] = round(time.time() - t0, 1)
    out["settings"] = {"NP_FIELD": NP_FIELD, "NP": NP, "NBOOT": NBOOT, "fast": FAST}
    (DATA / ("explore_fast.json" if FAST else "explore.json")).write_text(json.dumps(clean(out), indent=1))
    print("done", out["seconds"], "s")


if __name__ == "__main__":
    main()
