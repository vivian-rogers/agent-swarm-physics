"""H13 round 1b: the behavioral family test (HH267; card Amendment 2) and the three native tests (G35, NE32, NE06).

Behavior state of an agent-day (card Amendment 2): from behavior_states_v3 windows that are active and labelled
(non-holdout only, asserted), the mean of the 11 Jev v3.1 state probabilities p_*, plus four rates:
log(1 + actions per window), real failure rate (n_errors + 1) / (n_actions + 15), log(1 + commits per window),
log(1 + file writes per window). Agent-days need >= 6 windows. Variant B+tools adds the agent-day shares of bash,
GUI and other tool calls (actions.action). Features are z-scored within the unit, day-demeaned (H13's day_demean),
and averaged per agent over >= 2 days (H^B), exactly like the content state of a1.

Replication (B1-B4) on H13's 16 units; natives: G35 (room x lab, behavior vs style-free words), NE32 (newcomer
classification by incumbents' behavioral family fields), NE06 (Google-only scaffold change, DiD with exact relabeling).

Usage: uv run python hypotheses/H13-family-fields/analysis/r1b_behavior.py [--fast]
Reads data/processed/H13-family-fields/r1b/{bge_small,gte_modernbert}_none/ (scheme/build.py --r1b) and shared
tables; writes data/processed/H13-family-fields/r1b/behavior.json (numbers only).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import itertools  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
import warnings  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "infra/shared"))
import h13lib as L  # noqa: E402
from common import holdout_mask  # noqa: E402

warnings.simplefilter("ignore", RuntimeWarning)
SH = ROOT / "data/processed/shared"
DATA = ROOT / "data/processed/H13-family-fields"
R1B = DATA / "r1b"
FAST = "--fast" in sys.argv
NP = 1000 if FAST else 5000
NP2 = 500 if FAST else 2000
PCOLS = ["p_plan_coordinate", "p_execute_task", "p_research_browse", "p_communicate_external", "p_debug_recover",
         "p_verify_report", "p_monitor_wait", "p_self_maintenance", "p_social", "p_meta", "p_idle"]
RATES = ["log_actions_pw", "fail_rate", "log_commits_pw", "log_writes_pw"]
TOOLS = ["tool_bash", "tool_gui", "tool_other"]
GUI = {"left_click", "key", "scroll", "type", "mouse_move", "double_click", "right_click", "triple_click",
       "left_click_drag", "left_mouse_down", "left_mouse_up", "middle_click", "cursor_position", "hold_key"}
MIN_WIN = 6
COUNTED = ["35", "36b", "37", "38a", "38b", "38c", "39", "40", "41", "42", "44", "51a", "51b", "51c", "51d"]
TWO_ROOM = {"35", "36b", "37", "38a", "38b", "38c", "39", "41", "42", "44"}
BIG3 = ["Anthropic", "OpenAI", "Google"]


def roster():
    r = pl.read_parquet(SH / "roster.parquet", columns=["agent", "name", "lab"])
    return dict(zip(r["agent"].to_list(), r["lab"].to_list())), dict(zip(r["agent"].to_list(), r["name"].to_list()))


# ----------------------------------------------------------------------------- behavior agent-days
def behavior_agent_days(days=None) -> pl.DataFrame:
    b = pl.read_parquet(SH / "behavior_states_v3.parquet",
                        columns=["pt_date", "agent", "goal_no", "holdout", "active", "labeled", "n_actions", "n_errors",
                                 "n_turns", "n_commit_ok", "n_file_write", *PCOLS])
    b = b.filter(pl.col("active") & pl.col("labeled") & ~pl.col("holdout"))
    if days is not None:
        b = b.filter(pl.col("pt_date").is_in(days))
    ad = (b.group_by("agent", "pt_date")
          .agg(pl.len().alias("n_win"), *[pl.col(c).mean() for c in PCOLS],
               pl.col("n_actions").sum().alias("act"), pl.col("n_errors").sum().alias("err"),
               pl.col("n_turns").sum().alias("turns"), pl.col("n_commit_ok").sum().alias("com"),
               pl.col("n_file_write").sum().alias("wri"), pl.col("goal_no").first())
          .with_columns((pl.col("act") / pl.col("n_win")).log1p().alias("log_actions_pw"),
                        ((pl.col("err") + 1) / (pl.col("act") + 15)).alias("fail_rate"),
                        (pl.col("com") / pl.col("n_win")).log1p().alias("log_commits_pw"),
                        (pl.col("wri") / pl.col("n_win")).log1p().alias("log_writes_pw"),
                        (pl.col("act") / pl.col("turns").clip(1, None)).alias("actions_per_turn"))
          .sort("agent", "pt_date"))
    return ad


def tool_mix(days) -> pl.DataFrame:
    a = pl.read_parquet(SH / "actions.parquet", columns=["t", "agent", "action"])
    a = a.with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("pt_date"))
    a = a.filter(pl.col("pt_date").is_in(days))
    act = pl.col("action").cast(pl.String)
    a = a.with_columns(pl.when(act == "bash").then(pl.lit("tool_bash"))
                       .when(act.is_in(list(GUI))).then(pl.lit("tool_gui")).otherwise(pl.lit("tool_other")).alias("k"))
    g = a.group_by("agent", "pt_date", "k").len().pivot(on="k", index=["agent", "pt_date"], values="len").fill_null(0)
    for c in TOOLS:
        if c not in g.columns:
            g = g.with_columns(pl.lit(0).alias(c))
    tot = sum(pl.col(c) for c in TOOLS)
    return g.with_columns(*[(pl.col(c) / tot).alias(c) for c in TOOLS]).select("agent", "pt_date", *TOOLS)


def zscore(X):
    mu, sd = np.nanmean(X, 0), np.nanstd(X, 0)
    return (X - mu) / np.where(sd > 0, sd, 1)


def unit_behavior(bad, days, feats):
    """Agent-day rows of the unit with >= MIN_WIN windows; z-scored features; day-demeaned; agent means (>= 2 days)."""
    a = bad.filter(pl.col("pt_date").is_in(days) & (pl.col("n_win") >= MIN_WIN))
    X = zscore(a.select(feats).to_numpy().astype(np.float64))
    D = L.day_demean(X, a["pt_date"].to_numpy(), a["agent"].to_numpy())
    ags, H, nd = L.agent_means(D, a["agent"].to_numpy(), min_days=2)
    return a, D, ags, H


def content_H(base, gdir, u, kind):
    ad = pl.read_parquet(base / gdir / f"u{u}_agent_day.parquet")
    V = np.load(base / gdir / f"u{u}_agent_day_{kind}.npy").astype(np.float64)
    m = (ad["n"] >= 3).to_numpy()
    a = ad.filter(pl.Series(m))
    D = L.day_demean(V[m], a["pt_date"].to_numpy(), a["agent"].to_numpy())
    ags, H, _ = L.agent_means(D, a["agent"].to_numpy(), min_days=2)
    return ags, H


def style_vectors(base, gdir, u):
    """Agent mean of standardized style features (statement-weighted), for the B2 covariate."""
    ad = pl.read_parquet(base / gdir / f"u{u}_agent_day.parquet")
    fc = [c for c in ad.columns if c.startswith("f_")]
    F = ad.select(fc).to_numpy().astype(np.float64)
    F = np.nan_to_num(zscore(F))
    w = ad["n"].to_numpy().astype(float)
    out = {}
    for a in np.unique(ad["agent"].to_numpy()):
        k = ad["agent"].to_numpy() == a
        out[int(a)] = (F[k] * w[k, None]).sum(0) / w[k].sum()
    return out


def role_keep(ags, roles):
    n = len(ags)
    K = np.ones((n, n), bool)
    for i in range(n):
        for j in range(n):
            ri, rj = roles.get(str(ags[i])), roles.get(str(ags[j]))
            if i != j and ri is not None and ri == rj:
                K[i, j] = False
    return K


def lab_style_regression(H, fam, K, S, keep, rng, nperm):
    """B2: y = cos(H_i, H_j) ~ 1 + same_lab + style_sim over kept pairs; node permutation of lab labels."""
    n = len(H)
    ii, jj = L.pairs(n)
    y = (L.unit(H) @ L.unit(H).T)[ii, jj]
    Sn = L.unit(S)
    ss = (Sn @ Sn.T)[ii, jj]
    ok = keep[ii, jj] if keep is not None else np.ones(len(ii), bool)
    ii, jj, y, ss = ii[ok], jj[ok], y[ok], ss[ok]

    def fit(f, sub=None):
        i2, j2, yy, s2 = (ii, jj, y, ss) if sub is None else sub
        sl = ((f[i2] == f[j2]) & (f[i2] < K)).astype(float)
        X = np.column_stack([np.ones(len(yy)), sl, s2])
        if np.linalg.matrix_rank(X) < 3:
            return np.nan, np.nan
        b = np.linalg.lstsq(X, yy, rcond=None)[0]
        return b[1], b[2]
    bl, bs = fit(fam)
    nl = np.array([fit(rng.permutation(fam))[0] for _ in range(nperm)])

    def jk(m):
        sub_ok = m[ii] & m[jj]
        return fit(fam, (ii[sub_ok], jj[sub_ok], y[sub_ok], ss[sub_ok]))[0]
    return {"b_lab": float(bl), "b_style": float(bs), "n_pairs": int(len(y)),
            "p_lab": float((1 + np.sum(nl >= bl)) / (1 + np.sum(np.isfinite(nl)))) if np.isfinite(bl) else None,
            "se_lab": L.jackknife_se(jk, n)}


def feature_eta2(Hraw, fam, K, rng, feats, nperm):
    """Per-feature between-family share of the agent-mean variance (multi-member labs), lab-permutation p."""
    m = fam < K
    out = {}
    if m.sum() < 4 or len(np.unique(fam[m])) < 2:
        return out
    X, f = Hraw[m], fam[m]

    def eta(x, ff):
        tot = ((x - x.mean()) ** 2).sum()
        btw = sum((ff == k).sum() * (x[ff == k].mean() - x.mean()) ** 2 for k in np.unique(ff))
        return btw / tot if tot > 0 else np.nan
    for c, name in enumerate(feats):
        o = eta(X[:, c], f)
        null = np.array([eta(X[:, c], rng.permutation(f)) for _ in range(nperm)])
        out[name] = {"eta2": float(o), "p": float((1 + np.sum(null >= o)) / (1 + nperm))}
    return out


# ----------------------------------------------------------------------------- replication per unit
def run_unit(u, meta, bad, lab_of, rng, base_bge, base_gte):
    import explore as E  # H13's own helpers (agent_rooms)
    m = meta[u]
    days = m["days"]
    assert not any(holdout_mask(days, [m["goal_no"]] * len(days))), "holdout day in exploration"
    roles = m.get("roles", {})
    res = {"unit": u, "n_days": len(days), "counted": u in COUNTED}
    for name, feats in (("B", PCOLS + RATES), ("B_tools", PCOLS + RATES + TOOLS)):
        a, D, ags, H = unit_behavior(bad, days, feats)
        if len(ags) < 5:
            res[name] = {"N": int(len(ags))}
            continue
        labs = [lab_of[x] for x in ags]
        fam, multi = L.fam_labels(labs)
        K = len(multi)
        keep = role_keep(ags, roles) if roles else None
        r = {"N": int(len(ags)), "K": K, "families": {f: int(labs.count(f)) for f in multi}}
        r["field"] = L.field_test(H, fam, K, keep_pairs=keep, nperm=NP, rng=rng)
        r["loo"] = L.loo_perm(H, fam, K, nperm=NP2 // 2, rng=rng)
        if name == "B":
            res["_H"] = {int(x): L.unit(h).tolist() for x, h in zip(ags, H)}
            res["_ags"] = ags.tolist()
            r["R2_fam"] = L.r2_perm(H, fam, K, nperm=NP2, rng=rng)
            r["eta2"] = feature_eta2(H, fam, K, rng, feats, NP2 // 4)
            sv = style_vectors(base_bge, m["gdir"], u)
            have = np.array([x in sv for x in ags])
            if have.sum() >= 5:
                sub = np.flatnonzero(have)
                S = np.array([sv[int(ags[k])] for k in sub])
                fs, ms = L.fam_labels([labs[k] for k in sub])
                ks = role_keep(ags[sub], roles) if roles else None
                r["B2_lab_given_style"] = lab_style_regression(H[sub], fs, len(ms), S, ks, rng, NP2)
            # word channel on the same agents: LOO and field from style-residualized content (bge, gte) and raw
            for tag, base, kind in (("styp_bge", base_bge, "styp"), ("styp_gte", base_gte, "styp"), ("raw_bge", base_bge, "raw")):
                ca, cH = content_H(base, m["gdir"], u, kind)
                common = [x for x in ags if x in set(ca.tolist())]
                if len(common) >= 5:
                    ib = [int(np.flatnonzero(ags == x)[0]) for x in common]
                    ic = [int(np.flatnonzero(ca == x)[0]) for x in common]
                    fc, mc = L.fam_labels([lab_of[x] for x in common])
                    kc = role_keep(np.array(common), roles) if roles else None
                    r[f"loo_{tag}"] = L.loo_perm(cH[ic], fc, len(mc), nperm=NP2 // 2, rng=rng)
                    r[f"loo_behavior_same_agents_{tag}"] = L.loo_perm(H[ib], fc, len(mc), nperm=NP2 // 2, rng=rng)
                    r[f"field_{tag}"] = L.field_test(cH[ic], fc, len(mc), keep_pairs=kc, nperm=NP2, rng=rng, jack=False)
            if u in TWO_ROOM:
                ad = pl.read_parquet(base_bge / m["gdir"] / f"u{u}_agent_day.parquet")
                rooms = E.agent_rooms(ad, ags)
                Y = L.unit(H) @ L.unit(H).T
                r["famroom"] = L.famroom(Y, fam, rooms, K, nperm=NP2, rng=rng)
                for tag, base in (("styp_bge", base_bge), ("styp_gte", base_gte)):
                    ca, cH = content_H(base, m["gdir"], u, "styp")
                    pos = {int(x): k for k, x in enumerate(ca)}
                    keepa = np.array([int(x) in pos for x in ags])
                    if keepa.sum() >= 5:
                        sub = np.flatnonzero(keepa)
                        Yc = np.full((len(ags), len(ags)), np.nan)
                        Hc = L.unit(np.array([cH[pos[int(ags[k])]] for k in sub]))
                        Yc[np.ix_(sub, sub)] = Hc @ Hc.T
                        r[f"famroom_{tag}"] = L.famroom(Yc, fam, rooms, K, nperm=NP2, rng=rng)
        res[name] = r
    b = res.get("B", {})
    print(f"unit {u}: N={b.get('N')} T_B={b.get('field', {}).get('obs', np.nan):.3f} p={b.get('field', {}).get('p', np.nan):.4f} "
          f"loo={b.get('loo', {}).get('obs', np.nan):.2f} p={b.get('loo', {}).get('p', np.nan):.3f} "
          f"B2 b_lab={b.get('B2_lab_given_style', {}).get('b_lab', np.nan):.3f} p={b.get('B2_lab_given_style', {}).get('p_lab', np.nan)}",
          flush=True)
    return res


# ----------------------------------------------------------------------------- native NE32: newcomers
def ne32(meta, bad, lab_of, name_of, base_bge, base_gte):
    units51 = [u for u in ("51a", "51b", "51c", "51d", "51e")]
    feats = PCOLS + RATES
    first = {}
    for u in units51:
        for d in meta[u]["days"]:
            for x in bad.filter((pl.col("pt_date") == d) & (pl.col("n_win") >= MIN_WIN))["agent"].to_list():
                first.setdefault(int(x), d)
    start = min(meta["51a"]["days"])
    newcomers = sorted([a for a, d in first.items() if d > start], key=lambda a: first[a])
    out_rows = []
    for a in newcomers:
        u = next(x for x in units51 if first[a] in meta[x]["days"])
        days = meta[u]["days"]
        row = {"agent": a, "name": name_of[a], "lab": lab_of[a], "unit": u, "first_day": first[a]}
        # behavior
        ab = bad.filter(pl.col("pt_date").is_in(days) & (pl.col("n_win") >= MIN_WIN))
        X = zscore(ab.select(feats).to_numpy().astype(np.float64))
        D = L.day_demean(X, ab["pt_date"].to_numpy(), ab["agent"].to_numpy())
        for tag, (agv, dd, DD) in {"behavior": (ab["agent"].to_numpy(), ab["pt_date"].to_numpy(), D)}.items():
            row.update(classify_newcomer(a, agv, dd, DD, first, lab_of, tag))
        # content (style-residualized and raw), same rule
        for tag, base, kind in (("styp_bge", base_bge, "styp"), ("styp_gte", base_gte, "styp"), ("raw_bge", base_bge, "raw")):
            ad = pl.read_parquet(base / meta[u]["gdir"] / f"u{u}_agent_day.parquet")
            V = np.load(base / meta[u]["gdir"] / f"u{u}_agent_day_{kind}.npy").astype(np.float64)
            mm = (ad["n"] >= 3).to_numpy()
            a_ad = ad.filter(pl.Series(mm))
            Dc = L.day_demean(V[mm], a_ad["pt_date"].to_numpy(), a_ad["agent"].to_numpy())
            row.update(classify_newcomer(a, a_ad["agent"].to_numpy(), a_ad["pt_date"].to_numpy(), Dc, first, lab_of, tag))
        out_rows.append(row)
    from scipy.stats import binomtest
    summ = {}
    for tag in ("behavior", "styp_bge", "styp_gte", "raw_bge"):
        rr = [r for r in out_rows if r.get(f"{tag}_pred") is not None]
        if not rr:
            continue
        nc = sum(r[f"{tag}_correct"] for r in rr)
        ch = float(np.mean([1 / r[f"{tag}_ncand"] for r in rr]))
        summ[tag] = {"n": len(rr), "correct": int(nc), "accuracy": nc / len(rr), "chance": ch,
                     "p_binom": float(binomtest(int(nc), len(rr), ch, alternative="greater").pvalue),
                     "mean_rank": float(np.mean([r[f"{tag}_rank"] for r in rr]))}
    # same newcomers for behavior vs styp_bge
    both = [r for r in out_rows if r.get("behavior_pred") is not None and r.get("styp_bge_pred") is not None]
    summ["paired_behavior_vs_styp_bge"] = {"n": len(both), "behavior": int(sum(r["behavior_correct"] for r in both)),
                                           "styp_bge": int(sum(r["styp_bge_correct"] for r in both))}
    # NE32 triplet (descriptive): 07-09 / 07-10 behavior vectors vs OpenAI incumbent field and the role-mate
    trip = {35: 20, 36: 18, 37: 17}  # GPT-5.6 Sol/Terra/Luna -> incumbent role-mate (forecaster, YouTuber, diplomat)
    days = meta["51b"]["days"]
    ab = bad.filter(pl.col("pt_date").is_in(days) & (pl.col("n_win") >= MIN_WIN))
    X = zscore(ab.select(feats).to_numpy().astype(np.float64))
    D = L.day_demean(X, ab["pt_date"].to_numpy(), ab["agent"].to_numpy())
    agv, dd = ab["agent"].to_numpy(), ab["pt_date"].to_numpy()
    inc = [x for x in np.unique(agv) if first.get(int(x), "9") < "2026-07-09"]
    fields = {}
    for x in inc:
        k = (agv == x) & np.isfinite(D).all(1) & ~np.isin(dd, ["2026-07-09", "2026-07-10"])
        if k.sum() >= 2:
            fields.setdefault(lab_of[int(x)], []).append(L.unit(D[k].mean(0)))
    fields = {l: L.unit(np.mean(v, 0)) for l, v in fields.items()}
    tri = {}
    for t, mate in trip.items():
        r = {}
        for d in ("2026-07-09", "2026-07-10"):
            k = np.flatnonzero((agv == t) & (dd == d) & np.isfinite(D).all(1))
            km = np.flatnonzero((agv == mate) & ~np.isin(dd, ["2026-07-09", "2026-07-10"]) & np.isfinite(D).all(1))
            if len(k):
                x = L.unit(D[k[0]])
                sims = {l: float(x @ v) for l, v in fields.items()}
                r[d] = {"sim_openai": sims.get("OpenAI"), "best_family": max(sims, key=sims.get),
                        "rank_openai": sorted(sims, key=sims.get, reverse=True).index("OpenAI") + 1 if "OpenAI" in sims else None,
                        "sim_rolemate": float(x @ L.unit(D[km].mean(0))) if len(km) else None,
                        "rolemate_lab": lab_of[mate]}
        tri[name_of[t]] = r
    return {"newcomers": out_rows, "summary": summ, "triplet": tri}


def classify_newcomer(a, agv, dd, D, first, lab_of, tag):
    ok = np.isfinite(D).all(1)
    rows = np.flatnonzero((agv == a) & ok)
    rows = rows[np.argsort(dd[rows], kind="stable")][:3]
    out = {f"{tag}_pred": None}
    if len(rows) == 0:
        return out
    x = L.unit(D[rows].mean(0))
    fields = {}
    for b in np.unique(agv):
        if b == a or first.get(int(b), "9999") >= first[a]:
            continue
        k = (agv == b) & ok
        if k.sum() >= 2:
            fields.setdefault(lab_of[int(b)], []).append(L.unit(D[k].mean(0)))
    fields = {l: L.unit(np.mean(v, 0)) for l, v in fields.items()}
    if lab_of[a] not in fields:
        return {f"{tag}_pred": None, f"{tag}_note": "no incumbent of own lab"}
    sims = {l: float(x @ v) for l, v in fields.items()}
    pred = max(sims, key=sims.get)
    return {f"{tag}_pred": pred, f"{tag}_correct": pred == lab_of[a], f"{tag}_ncand": len(fields),
            f"{tag}_rank": sorted(sims, key=sims.get, reverse=True).index(lab_of[a]) + 1, f"{tag}_days": int(len(rows))}


# ----------------------------------------------------------------------------- native NE06
def ne06(lab_of, name_of):
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "goal_no"])
    days20 = sorted(cal.filter(pl.col("goal_no") == 20)["pt_date"].to_list())
    assert not any(holdout_mask(days20, [20] * len(days20)))
    pre, post = [d for d in days20 if d <= "2025-11-19"], [d for d in days20 if "2025-11-20" <= d <= "2025-11-24"]
    bad = behavior_agent_days(pre + post).filter(pl.col("n_win") >= MIN_WIN)
    feats = PCOLS + RATES
    X = zscore(bad.select(feats).to_numpy().astype(np.float64))
    ag, dd = bad["agent"].to_numpy(), bad["pt_date"].to_numpy()
    apt = bad["actions_per_turn"].to_numpy()

    def deltas(X, pre_d, post_d, exclude=()):
        out = {}
        for a in np.unique(ag):
            if a in exclude:
                continue
            k1, k2 = (ag == a) & np.isin(dd, pre_d), (ag == a) & np.isin(dd, post_d)
            if k1.sum() >= 1 and k2.sum() >= 1:
                out[int(a)] = X[k2].mean(0) - X[k1].mean(0)
        return out

    def did(dl, treated, norm=True):
        t = [dl[a] for a in dl if a in treated]
        c = [dl[a] for a in dl if a not in treated]
        v = np.mean(t, 0) - np.mean(c, 0)
        return float(np.linalg.norm(v)) if norm else float(np.atleast_1d(v)[0])

    goog = {a for a in np.unique(ag) if lab_of[int(a)] == "Google"}
    res = {"pre": pre, "post": post, "google": [name_of[int(a)] for a in goog]}
    dl = deltas(X, pre, post)
    obs = did(dl, goog)
    null = [did(dl, set(c)) for c in itertools.combinations(sorted(dl), len(goog & set(dl)))]
    res["behavior"] = {"D_norm": obs, "percentile": float(np.mean(np.array(null) <= obs)), "n_relabelings": len(null),
                       "n_agents": len(dl),
                       "per_feature_D": dict(zip(feats, (np.mean([dl[a] for a in dl if a in goog], 0)
                                                         - np.mean([dl[a] for a in dl if a not in goog], 0)).round(3).tolist()))}
    # manipulation check: actions per turn (one-sided: Google decreases)
    dla = deltas(apt[:, None], pre, post)
    obs_a = did(dla, goog, norm=False)
    null_a = [did(dla, set(c), norm=False) for c in itertools.combinations(sorted(dla), len(goog & set(dla)))]
    res["actions_per_turn"] = {"DiD": obs_a, "p_lower": float(np.mean(np.array(null_a) <= obs_a)), "n": len(null_a),
                               "google_pre": {name_of[int(a)]: float(np.mean(apt[(ag == a) & np.isin(dd, pre)])) for a in goog},
                               "google_post": {name_of[int(a)]: float(np.mean(apt[(ag == a) & np.isin(dd, post)])) for a in goog},
                               "others_pre": float(np.mean(apt[~np.isin(ag, list(goog)) & np.isin(dd, pre)])),
                               "others_post": float(np.mean(apt[~np.isin(ag, list(goog)) & np.isin(dd, post)]))}
    # placebo date: 11-17/18 -> 11-19, Gemini 3 Pro (joins 11-19) excluded
    g3 = {a for a in goog if name_of[int(a)] == "Gemini 3 Pro"}
    dlp = deltas(X, ["2025-11-17", "2025-11-18"], ["2025-11-19"], exclude=g3)
    tp = goog - g3
    obs_p = did(dlp, tp)
    null_p = [did(dlp, set(c)) for c in itertools.combinations(sorted(dlp), len(tp & set(dlp)))]
    res["placebo_date"] = {"D_norm": obs_p, "percentile": float(np.mean(np.array(null_p) <= obs_p)), "n": len(null_p)}
    # content channel (descriptive): chat statements, regime-I white32, agent-day means, day-demeaned
    st = pl.read_parquet(SH / "embeddings/statements.parquet").with_row_index("srow").filter(
        (pl.col("kind") == "chat") & pl.col("pt_date").is_in(pre + post))
    for model, sfx in (("bge", "bge_small"), ("gte", "gte_modernbert")):
        W = np.load(SH / f"embeddings/statements_white32_{sfx}.npy", mmap_mode="r")
        U = np.asarray(W[st["srow"].to_numpy()], dtype=np.float64)
        g = st.with_columns(pl.Series("r", np.arange(st.height))).group_by("agent", "pt_date").agg(pl.col("r"), pl.len().alias("n")).filter(pl.col("n") >= 3)
        V = np.stack([U[r].mean(0) for r in g["r"].to_list()])
        a2, d2 = g["agent"].to_numpy(), g["pt_date"].to_numpy()
        Dc = L.day_demean(V, d2, a2)
        dlc = {}
        for a in np.unique(a2):
            k1 = (a2 == a) & np.isin(d2, pre) & np.isfinite(Dc).all(1)
            k2 = (a2 == a) & np.isin(d2, post) & np.isfinite(Dc).all(1)
            if k1.sum() and k2.sum():
                dlc[int(a)] = Dc[k2].mean(0) - Dc[k1].mean(0)
        oc = did(dlc, goog)
        nc = [did(dlc, set(c)) for c in itertools.combinations(sorted(dlc), len(goog & set(dlc)))]
        res[f"content_{model}"] = {"D_norm": oc, "percentile": float(np.mean(np.array(nc) <= oc)), "n": len(nc)}
    return res


def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items() if not str(k).startswith("_")}
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
    base_bge, base_gte = R1B / "bge_small_none", R1B / "gte_modernbert_none"
    meta = json.loads((base_bge / "units.json").read_text())
    lab_of, name_of = roster()
    alldays = sorted({d for u in meta for d in meta[u]["days"]})
    bad = behavior_agent_days(alldays).join(tool_mix(alldays), on=["agent", "pt_date"], how="left").fill_null(0)
    results = {}
    for u in COUNTED + ["51e"]:
        results[u] = run_unit(u, meta, bad, lab_of, rng, base_bge, base_gte)
    out = {"units": results}
    # cross-unit: RE summaries and counts
    cu = [u for u in COUNTED if "field" in results[u].get("B", {})]
    S = {}
    for key, get_e, get_s in (
            ("T_B", lambda r: r["B"]["field"]["obs"], lambda r: r["B"]["field"].get("se_jack")),
            ("T_B_tools", lambda r: r["B_tools"]["field"]["obs"], lambda r: r["B_tools"]["field"].get("se_jack")),
            ("B2_b_lab", lambda r: r["B"].get("B2_lab_given_style", {}).get("b_lab", np.nan),
             lambda r: r["B"].get("B2_lab_given_style", {}).get("se_lab", np.nan))):
        e = [get_e(results[u]) for u in cu]
        s = [get_s(results[u]) for u in cu]
        S[key] = L.dl_meta(e, [np.nan if x is None else x for x in s])
    cnt = lambda f: int(sum(1 for u in cu if f(results[u])))
    S["counts"] = {
        "n_units": len(cu),
        "B1_field_p05": cnt(lambda r: r["B"]["field"]["p"] < 0.05),
        "B_tools_field_p05": cnt(lambda r: r["B_tools"]["field"]["p"] < 0.05),
        "B2_lab_p05": cnt(lambda r: (r["B"].get("B2_lab_given_style", {}).get("p_lab") or 1) < 0.05),
        "B4_loo_p05": cnt(lambda r: r["B"]["loo"]["p"] < 0.05),
        "B4_loo_beh_gt_styp_bge": cnt(lambda r: "loo_styp_bge" in r["B"] and r["B"]["loo_behavior_same_agents_styp_bge"]["obs"] > r["B"]["loo_styp_bge"]["obs"]),
        "B4_loo_beh_lt_styp_bge": cnt(lambda r: "loo_styp_bge" in r["B"] and r["B"]["loo_behavior_same_agents_styp_bge"]["obs"] < r["B"]["loo_styp_bge"]["obs"]),
        "styp_bge_field_p05": cnt(lambda r: "field_styp_bge" in r["B"] and r["B"]["field_styp_bge"]["p"] < 0.05),
        "styp_gte_field_p05": cnt(lambda r: "field_styp_gte" in r["B"] and r["B"]["field_styp_gte"]["p"] < 0.05),
        "raw_bge_field_p05": cnt(lambda r: "field_raw_bge" in r["B"] and r["B"]["field_raw_bge"]["p"] < 0.05),
        "loo_styp_bge_p05": cnt(lambda r: "loo_styp_bge" in r["B"] and r["B"]["loo_styp_bge"]["p"] < 0.05),
        "loo_raw_bge_p05": cnt(lambda r: "loo_raw_bge" in r["B"] and r["B"]["loo_raw_bge"]["p"] < 0.05)}
    tr = [u for u in cu if "famroom" in results[u]["B"]]
    S["famroom"] = {"n": len(tr), "lab_gt_room": sum(results[u]["B"]["famroom"]["b_lab"] > results[u]["B"]["famroom"]["b_room"] for u in tr),
                    "lab_p05": sum(results[u]["B"]["famroom"]["p_lab"] < 0.05 for u in tr),
                    "room_p05": sum(results[u]["B"]["famroom"]["p_room"] < 0.05 for u in tr),
                    "RE_b_lab": L.dl_meta([results[u]["B"]["famroom"]["b_lab"] for u in tr], [results[u]["B"]["famroom"].get("se_lab") for u in tr]),
                    "RE_b_room": L.dl_meta([results[u]["B"]["famroom"]["b_room"] for u in tr], [results[u]["B"]["famroom"].get("se_room") for u in tr])}
    # B3 invariance over regime-III counted units
    r3 = [u for u in cu if meta[u]["regime"] == "III"]
    Hu = [{int(a): np.array(v) for a, v in results[u]["_H"].items()} for u in r3]
    S["B3_invariance"] = L.invariance(Hu, lab_of, BIG3, nperm=NP2 // 2, rng=rng)
    S["B3_invariance"]["units"] = r3
    out["summary"] = S
    print("SUMMARY", json.dumps(clean(S["counts"])), flush=True)
    print("RE T_B", json.dumps(clean(S["T_B"])), "B2", json.dumps(clean(S["B2_b_lab"])), flush=True)
    print("B3", {k: S["B3_invariance"][k] for k in ("family_cos", "family_median", "null_regroup_median_mean", "p_regroup", "agent_median")}, flush=True)
    # natives
    out["native_NE32"] = ne32(meta, bad, lab_of, name_of, base_bge, base_gte)
    print("NE32", json.dumps(clean(out["native_NE32"]["summary"])), flush=True)
    out["native_NE06"] = ne06(lab_of, name_of)
    print("NE06", json.dumps(clean({k: v for k, v in out["native_NE06"].items() if k not in ("pre", "post")}))[:1500], flush=True)
    out["native_G35"] = {k: results["35"]["B"].get(k) for k in ("famroom", "famroom_styp_bge", "famroom_styp_gte", "field", "loo")}
    out["settings"] = {"NP": NP, "NP2": NP2, "fast": FAST, "min_windows": MIN_WIN, "features": PCOLS + RATES, "tools": TOOLS}
    out["seconds"] = round(time.time() - t0, 1)
    (R1B / ("behavior_fast.json" if FAST else "behavior.json")).write_text(json.dumps(clean(out), indent=1))
    # keep agent behavioral fields (unit-normalized) for later use
    np.savez_compressed(R1B / "behavior_fields.npz", **{f"u{u}": np.array([[int(a)] + v for a, v in results[u]["_H"].items()])
                                                        for u in results if "_H" in results[u]})
    print("done", out["seconds"], "s")


if __name__ == "__main__":
    main()
