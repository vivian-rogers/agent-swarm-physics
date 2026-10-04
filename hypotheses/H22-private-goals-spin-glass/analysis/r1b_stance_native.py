"""H22 round 1b: the stance channel (DQ2 reply labels, calibrated agent-field null) and the native tests NE38 and G23.

Stance coupling J^s_ij (card round-1b pre-registration): DQ2 reply_pairs (cand, labelled, agent -> agent, non-holdout),
soft stance s = p_supports - p_opposes weighted by p_reply, mean over replies in both directions, pairs with >= 3
replies. Per unit (H22's 51a-51e and the shared pu51* splits, roles from DQ6 ground truth via the r1b build):
  - P4s treatment test (h22lib.treatment_test: T_SR, T_OP, T_SY, T_NC; raw and same-lab adjusted; role permutation);
  - P3s: tau3 and tau3(dc) on three day folds (missing pairs = 0), day-bootstrap CI; the camp score and the count of
    significantly negative pairs against the calibrated agent-field null (ordered logit, infra/shared/nulls.py);
  - heterogeneity beyond agent fields: split-half (even/odd days) correlation of double-centred J^s vs the same null.
Natives (predictions in goalperiod-subhypotheses/NE38 and G23, written before running):
  - NE38: Opus 5's content couplings with its game-dev rivals before (07-24 -> 07-28) vs after (07-30 -> 08-04) its
    role change, DiD vs its other couplings, placebo rivals (exact); static alignment check; stance counts.
  - G23: chess opponents (pairs linking the same Lichess game id) vs other pairs, in stance and content co-movement.

Usage: uv run python hypotheses/H22-private-goals-spin-glass/analysis/r1b_stance_native.py [--fast]
Needs scheme/build.py --r1b (bge_small/gte_modernbert white32) first. Writes data/processed/H22-.../r1b/stance_native.json.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import itertools  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
import warnings  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
sys.path.insert(0, str(ROOT / "infra/shared"))
import h22lib as L  # noqa: E402
import role_relations as RR  # noqa: E402
import build as B  # noqa: E402
from common import holdout_mask  # noqa: E402
from nulls import fit_ordinal, simulate_ordinal  # noqa: E402

warnings.simplefilter("ignore", RuntimeWarning)
SH = ROOT / "data/processed/shared"
R1B = ROOT / "data/processed/H22-private-goals-spin-glass/r1b"
FAST = "--fast" in sys.argv
NPERM = 1000 if FAST else 5000
NSIM = 60 if FAST else 200
SEED = 20261004
MIN_N = 3


def jdump(o):
    def d(x):
        if isinstance(x, dict):
            return {str(k): d(v) for k, v in x.items()}
        if isinstance(x, (list, tuple)):
            return [d(v) for v in x]
        if isinstance(x, np.ndarray):
            return d(x.tolist())
        if isinstance(x, (np.floating, float)):
            return None if not np.isfinite(x) else float(x)
        if isinstance(x, (np.integer,)):
            return int(x)
        if isinstance(x, np.bool_):
            return bool(x)
        return x
    return json.dumps(d(o), indent=1)


def replies(goal, days=None):
    r = pl.read_parquet(SH / "reply_pairs.parquet",
                        columns=["B_message_id", "b_agent", "a_agent", "a_kind", "pair_set", "labelled", "p_reply",
                                 "p_supports", "p_opposes", "stance", "pt_date", "goal_no", "holdout"])
    r = r.filter((pl.col("goal_no") == goal) & (pl.col("pair_set") == "cand") & pl.col("labelled") & (pl.col("a_kind") == 0)
                 & ~pl.col("holdout") & (pl.col("b_agent") != pl.col("a_agent")))
    if days is not None:
        r = r.filter(pl.col("pt_date").is_in(days))
    assert r["holdout"].sum() == 0
    return r.with_columns((pl.col("p_supports") - pl.col("p_opposes")).alias("s"),
                          pl.when(pl.col("stance") == "supports").then(1).when(pl.col("stance") == "opposes").then(-1)
                          .otherwise(0).alias("h"))


def pair_J(b, a, s, w, agents, min_n=MIN_N):
    pos = {x: k for k, x in enumerate(agents)}
    n = len(agents)
    S = np.zeros((n, n)); W = np.zeros((n, n)); N = np.zeros((n, n))
    for bb, aa, ss, ww in zip(b, a, s, w):
        if bb in pos and aa in pos:
            i, j = pos[bb], pos[aa]
            S[i, j] += ss * ww; S[j, i] += ss * ww; W[i, j] += ww; W[j, i] += ww; N[i, j] += 1; N[j, i] += 1
    J = np.where((N >= min_n) & (W > 0), S / np.where(W > 0, W, 1), np.nan)
    np.fill_diagonal(J, np.nan)
    return J, N


def dc_nan(J):
    M = J.copy()
    for _ in range(20):
        r = np.nanmean(M, 1, keepdims=True); r[~np.isfinite(r)] = 0
        M = M - r
        c = np.nanmean(M, 0, keepdims=True); c[~np.isfinite(c)] = 0
        M = M - c
    return (M + M.T) / 2


def camp_score(J, rng, restarts=60):
    """Satisfied |J| weight of the best two-camp split (exact for n <= 16, else multi-restart descent)."""
    n = len(J)
    A = np.nan_to_num(J); np.fill_diagonal(A, 0)
    tot = np.abs(A[np.triu_indices(n, 1)]).sum()
    if tot == 0:
        return np.nan
    return 1 - L.gs_frustration(A, restarts, rng)


def residual_neg_pairs(spk, tgt, s, n, return_pairs=False):
    """Pairs whose two-way-FE residual stance is significantly negative (z < -2, >= 3 replies). Replies are treated as
    independent given agent fields (the calibrated null makes the same assumption), so within-pair clustering of
    replies (threads) inflates the count; read it against the null and the enrichment test, not alone."""
    us, ut = np.unique(spk), np.unique(tgt)
    X = np.column_stack([np.ones(len(s))] + [(spk == a).astype(float) for a in us[1:]] + [(tgt == a).astype(float) for a in ut[1:]])
    res = s - X @ np.linalg.lstsq(X, s, rcond=None)[0]
    cnt, plist = 0, []
    key = np.minimum(spk, tgt) * 1000 + np.maximum(spk, tgt)
    for k in np.unique(key):
        m = key == k
        if m.sum() >= 3:
            sd = res[m].std(ddof=1)
            if sd > 0 and res[m].mean() / (sd / np.sqrt(m.sum())) < -2:
                cnt += 1
                plist.append((int(k // 1000), int(k % 1000)))
    return (cnt, plist) if return_pairs else cnt


def tau3_folds(r, days, agents, rng, nboot=200):
    """tau3 and tau3(dc) of J^s on three day folds (missing = 0), with a fold-preserving day bootstrap."""
    D = len(days)
    if D < 3:
        return {}
    didx = {d: k for k, d in enumerate(days)}
    dk = np.array([didx[d] for d in r["pt_date"]])
    b, a, s, w = r["b_agent"].to_numpy(), r["a_agent"].to_numpy(), r["s"].to_numpy(), r["p_reply"].to_numpy()

    def Js(weights):
        out = []
        for f in range(3):
            m = (dk % 3) == f
            ww = w[m] * weights[dk[m]]
            J, _ = pair_J(b[m], a[m], s[m], ww, agents, min_n=1)
            out.append(np.nan_to_num(J))
        return out
    J1, J2, J3 = Js(np.ones(D))
    t3 = L.tau3_from(J1, J2, J3)[0]
    t3dc = L.tau3_from(L.double_center(J1), L.double_center(J2), L.double_center(J3))[0]
    bs, bsdc = [], []
    fidx = [np.flatnonzero(np.arange(D) % 3 == f) for f in range(3)]
    for _ in range(nboot):
        wts = np.zeros(D)
        for ix in fidx:
            wts += np.bincount(rng.choice(ix, len(ix)), minlength=D)
        j = Js(wts)
        bs.append(L.tau3_from(*j)[0]); bsdc.append(L.tau3_from(*[L.double_center(x) for x in j])[0])
    q = lambda v: [float(np.nanquantile(v, 0.05)), float(np.nanquantile(v, 0.95))] if np.isfinite(v).any() else None
    return {"tau3": t3, "tau3_ci90": q(np.array(bs, float)), "tau3_dc": t3dc, "tau3_dc_ci90": q(np.array(bsdc, float))}


def stance_unit(name, period, base, rng):
    p = base / period / name
    meta = json.loads((p / "meta.json").read_text())
    days = meta["days"]
    goal = int(period[1:])
    assert not any(holdout_mask(days, [goal] * len(days)))
    ag = pl.read_parquet(p / "agents.parquet")
    agents = ag["agent"].to_list()
    labs = ag["lab"].fill_null("?").to_numpy()
    roles = ag["role"].to_list()
    r = replies(goal, days).filter(pl.col("b_agent").is_in(agents) & pl.col("a_agent").is_in(agents))
    out = {"unit": name, "days": len(days), "n_replies": r.height}
    if r.height < 30:
        return out
    b, a, s, w = r["b_agent"].to_numpy(), r["a_agent"].to_numpy(), r["s"].to_numpy(), r["p_reply"].to_numpy()
    J, N = pair_J(b, a, s, w, agents)
    out["n_pairs"] = int(np.isfinite(J[np.triu_indices(len(agents), 1)]).sum())
    out["mean_s"] = float(np.average(s, weights=w))
    out["opposes_share"] = float((r["h"] == -1).mean())
    out["p_neg_pairs_raw"] = float(np.mean(J[np.triu_indices(len(agents), 1)][np.isfinite(J[np.triu_indices(len(agents), 1)])] < 0))
    # P4s treatment test on J^s (roles from GT via the r1b build)
    if period == "G51":
        role_names = sorted({x for x in roles if x is not None})
        lookup = RR.lookup_table(role_names)
        ridx = np.array([role_names.index(x) if x is not None else -1 for x in roles])
        out["treatment"] = L.treatment_test(J, ridx, lookup, {"SR": 1, "OP": 2, "K": [1, 2], "SY": 3, "NC": 4},
                                            labs=labs, nperm=NPERM, rng=rng)
        out["sr_pairs"] = [[int(agents[i]), int(agents[j])] for i, j in zip(*np.triu_indices(len(agents), 1))
                           if roles[i] is not None and roles[i] == roles[j]]
        out["sr_pairs_with_J"] = [[int(agents[i]), int(agents[j]), float(J[i, j])] for i, j in zip(*np.triu_indices(len(agents), 1))
                                  if roles[i] is not None and roles[i] == roles[j] and np.isfinite(J[i, j])]
    # P3s balance on three day folds (D >= 3)
    out["balance"] = tau3_folds(r, days, agents, rng, nboot=50 if FAST else 200)
    # calibrated agent-field null for camps, negative pairs, split-half heterogeneity of double-centred J
    pos = {x: k for k, x in enumerate(agents)}
    spk, tgt = np.array([pos[x] for x in b]), np.array([pos[x] for x in a])
    h = r["h"].to_numpy()
    c, aa, bb, ok = fit_ordinal(spk, tgt, h + 1, len(agents))
    didx = {d: k for k, d in enumerate(days)}
    dk = np.array([didx[d] for d in r["pt_date"]])

    def stats_for(lbl, wts):
        Jh, _ = pair_J(b, a, lbl, wts, agents)
        cs = camp_score(dc_nan(Jh), rng, restarts=30)
        neg = residual_neg_pairs(spk, tgt, lbl.astype(float), len(agents))
        JA, _ = pair_J(b[dk % 2 == 0], a[dk % 2 == 0], lbl[dk % 2 == 0], wts[dk % 2 == 0], agents, min_n=2)
        JB, _ = pair_J(b[dk % 2 == 1], a[dk % 2 == 1], lbl[dk % 2 == 1], wts[dk % 2 == 1], agents, min_n=2)
        iu = np.triu_indices(len(agents), 1)
        x, y = dc_nan(JA)[iu], dc_nan(JB)[iu]
        okp = np.isfinite(x) & np.isfinite(y)
        rho = float(np.corrcoef(x[okp], y[okp])[0, 1]) if okp.sum() >= 5 else np.nan
        return cs, neg, rho
    ones = np.ones(len(h))
    cs_o, neg_o, rho_o = stats_for(h.astype(float), ones)
    # which pairs are negative, and are they enriched in conflict classes (SR, OP)? (H37's P9 on DQ2 labels)
    _, negl = residual_neg_pairs(spk, tgt, h.astype(float), len(agents), return_pairs=True)
    if period == "G51":
        cls = RR.lookup_table(role_names)
        def pcls(i, j):
            return 0 if ridx[i] < 0 or ridx[j] < 0 else int(cls[ridx[i], ridx[j]])
        key = np.minimum(spk, tgt) * 1000 + np.maximum(spk, tgt)
        u, c3 = np.unique(key, return_counts=True)
        tested = [(int(k // 1000), int(k % 1000)) for k, c_ in zip(u, c3) if c_ >= 3]
        negset = set(negl)
        conflict = lambda p: pcls(*p) in (1, 2)
        a11 = sum(1 for p in tested if p in negset and conflict(p)); a12 = sum(1 for p in tested if p in negset and not conflict(p))
        a21 = sum(1 for p in tested if p not in negset and conflict(p)); a22 = sum(1 for p in tested if p not in negset and not conflict(p))
        from scipy.stats import fisher_exact
        out["neg_pair_enrichment"] = {"neg_conflict": a11, "neg_other": a12, "nonneg_conflict": a21, "nonneg_other": a22,
                                      "fisher_p_greater": float(fisher_exact([[a11, a12], [a21, a22]], alternative="greater")[1]),
                                      "neg_pairs_classes": {RR.CLASS_NAMES[c_]: sum(1 for p in negl if pcls(*p) == c_) for c_ in range(5)}}
    sims = [simulate_ordinal(spk, tgt, c, aa, bb, rng) for _ in range(NSIM)]
    nul = np.array([stats_for(y, ones) for y in sims], float)
    pv = lambda o, col: float((1 + np.sum(nul[:, col] >= o)) / (1 + np.sum(np.isfinite(nul[:, col])))) if np.isfinite(o) else None
    out["agent_field_null"] = {"camp_score": cs_o, "camp_null_mean": float(np.nanmean(nul[:, 0])), "p_camp": pv(cs_o, 0),
                               "neg_pairs": int(neg_o), "neg_null_mean": float(np.nanmean(nul[:, 1])), "p_neg": pv(neg_o, 1),
                               "rho_split_dc": rho_o, "rho_null_mean": float(np.nanmean(nul[:, 2])), "p_rho": pv(rho_o, 2),
                               "n_sims": NSIM, "fit_ok": ok}
    t = out.get("treatment", {}).get("family_adjusted", {})
    print(f"{name}: replies {r.height} pairs {out['n_pairs']} mean_s {out['mean_s']:.3f} | T_SR {t.get('SR', {}).get('T')} "
          f"(n {t.get('SR', {}).get('n')}, p< {t.get('SR', {}).get('p_less')}, p> {t.get('SR', {}).get('p_greater')}) "
          f"T_OP {t.get('OP', {}).get('T')} | tau3_dc {out['balance'].get('tau3_dc')} | camp p {out['agent_field_null']['p_camp']} "
          f"neg {neg_o} vs {out['agent_field_null']['neg_null_mean']:.2f} p {out['agent_field_null']['p_neg']}", flush=True)
    return out


# ============================================================================================ NE38
def ne38(rng, min_shared=5):
    import explore as X
    out = {"min_shared_windows": min_shared}
    rivals, opus5 = {24, 26}, 40
    pre_unit, post_unit = "pu51e", "pu51f"
    for model in ("bge_small", "gte_modernbert"):
        base = R1B / f"{model}_white32_none"
        X.BASE = base
        Jm, Hm = {}, {}
        for side, unit, drop in (("pre", pre_unit, []), ("post", post_unit, ["2026-07-29"])):
            meta, ag, wi, wv, di, dv, tk = X.load_unit("G51", unit)
            keepd = [k for k, d in enumerate(meta["days"]) if d not in drop]
            code = ag["agent"].to_numpy()
            idx = np.arange(len(code))
            Xt, Ot = X.window_tensor(meta, wi, wv, idx)
            Xt, Ot = Xt[keepd], Ot[keepd]
            wpd = [meta["wins_per_day"][k] for k in keepd]
            Xp, Op = L.to_pseudo_days(Xt, Ot, 3, wpd)
            st = L.ContentStats(Xp, Op, min_shared=min_shared)
            J = st.J(np.ones(Xp.shape[0], bool))
            i40 = int(np.flatnonzero(code == opus5)[0]) if opus5 in code else None
            if i40 is not None:
                out.setdefault(model + "_shared_windows", {})[side] = {int(code[j]): int(st.Cr[:, i40, j].sum()) for j in range(len(code))
                                                                       if int(code[j]) in rivals}
            Jm[side] = {int(code[i]): {int(code[j]): J[i, j] for j in range(len(code)) if np.isfinite(J[i, j])} for i in range(len(code))}
            Hf, H1, H2, P = X.day_tensor(meta, di, dv, idx)
            Hf, P = Hf[keepd], P[keepd]
            Pm = P[..., None].astype(float)
            mday = (Hf * Pm).sum(1) / np.maximum(Pm.sum(1), 1)
            Dl = (Hf - mday[:, None]) * Pm
            cnt = P.sum(0)
            Hm[side] = {int(code[i]): L.unit(Dl[:, i].sum(0) / cnt[i]) for i in range(len(code)) if cnt[i] >= 1}
        others = sorted((set(Jm["pre"].get(opus5, {})) & set(Jm["post"].get(opus5, {}))) - {opus5})
        res = {"n_others_both": len(others), "rivals_present": sorted(rivals & set(others))}
        if not rivals <= set(others):
            res["note"] = "a rival lacks a coupling on one side"
        def did(group, J=Jm):
            g = [x for x in others if x in group]; o = [x for x in others if x not in group]
            if not g or not o:
                return np.nan
            dg = np.mean([J["post"][opus5][x] - J["pre"][opus5][x] for x in g])
            do = np.mean([J["post"][opus5][x] - J["pre"][opus5][x] for x in o])
            return float(dg - do)
        obs = did(rivals & set(others))
        null = np.array([did(set(c)) for c in itertools.combinations(others, len(rivals & set(others)))])
        res["J_pre_rivals"] = {x: float(Jm["pre"][opus5][x]) for x in rivals if x in Jm["pre"].get(opus5, {})}
        res["J_post_rivals"] = {x: float(Jm["post"][opus5][x]) for x in rivals if x in Jm["post"].get(opus5, {})}
        res["J_pre_others_mean"] = float(np.mean([Jm["pre"][opus5][x] for x in others if x not in rivals]))
        res["J_post_others_mean"] = float(np.mean([Jm["post"][opus5][x] for x in others if x not in rivals]))
        res["DiD"] = obs
        res["placebo_pct"] = float(np.mean(null <= obs)) if np.isfinite(obs) else None
        res["p_two_sided"] = float(np.mean(np.abs(null - np.nanmean(null)) >= abs(obs - np.nanmean(null)))) if np.isfinite(obs) else None
        res["n_placebo"] = int(len(null))
        # static alignment manipulation check
        oth_h = sorted((set(Hm["pre"]) & set(Hm["post"])) - {opus5})
        if opus5 in Hm["pre"] and opus5 in Hm["post"]:
            def sdid(group):
                g = [x for x in oth_h if x in group]; o = [x for x in oth_h if x not in group]
                f = lambda side, xs: np.mean([Hm[side][opus5] @ Hm[side][x] for x in xs])
                return float((f("post", g) - f("pre", g)) - (f("post", o) - f("pre", o)))
            so = sdid(rivals)
            sn = np.array([sdid(set(c)) for c in itertools.combinations(oth_h, 2)])
            res["static_alignment"] = {"cos_rivals_pre": float(np.mean([Hm["pre"][opus5] @ Hm["pre"][x] for x in rivals if x in Hm["pre"]])),
                                       "cos_rivals_post": float(np.mean([Hm["post"][opus5] @ Hm["post"][x] for x in rivals if x in Hm["post"]])),
                                       "DiD": so, "placebo_pct": float(np.mean(sn <= so)), "n_placebo": int(len(sn))}
        out[model] = res
    # stance counts
    r = replies(51, None)
    pre_d = ["2026-07-24", "2026-07-27", "2026-07-28"]
    post_d = ["2026-07-30", "2026-07-31", "2026-08-03", "2026-08-04"]
    m40 = (pl.col("b_agent") == opus5) | (pl.col("a_agent") == opus5)
    rr = r.filter(m40)
    st = {}
    for side, dd in (("pre", pre_d), ("post", post_d)):
        x = rr.filter(pl.col("pt_date").is_in(dd))
        other = np.where(x["b_agent"].to_numpy() == opus5, x["a_agent"].to_numpy(), x["b_agent"].to_numpy())
        isr = np.isin(other, list(rivals))
        st[side] = {"n_rivals": int(isr.sum()), "n_others": int((~isr).sum()),
                    "s_rivals": float(np.average(x["s"].to_numpy()[isr], weights=x["p_reply"].to_numpy()[isr])) if isr.sum() else None,
                    "s_others": float(np.average(x["s"].to_numpy()[~isr], weights=x["p_reply"].to_numpy()[~isr])) if (~isr).sum() else None}
    st["testable"] = bool(st["pre"]["n_rivals"] >= 10 and st["post"]["n_rivals"] >= 10)
    out["stance"] = st
    return out


# ============================================================================================ G23
GAME = re.compile(r"lichess\.org/([A-Za-z0-9]{8})(?:[A-Za-z0-9]{4})?(?![A-Za-z0-9])")
STOP = {"analysis", "training", "practice", "tutorial", "blog", "streamer", "learn", "coordinates", "broadcast",
        "tournament", "playwith", "features", "inbox", "settings", "editor", "account", "insights", "storm", "racer"}


def g23_opponents():
    cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("goal_no") == 23)
    days = sorted(cal["pt_date"].to_list())
    assert not any(holdout_mask(days, [23] * len(days)))
    links = []  # (agent, game id)
    cc = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "agent", "speaker_kind", "goal_no"]).filter(
        (pl.col("goal_no") == 23) & (pl.col("speaker_kind") == "agent"))
    tx = pl.read_parquet(SH / "chat_text.parquet", columns=["message_id", "text"]).join(cc.select("message_id", "agent"), on="message_id")
    for a, t in tx.select("agent", "text").iter_rows():
        links += [(int(a), g) for g in GAME.findall(t or "")]
    it = pl.read_parquet(SH / "intentions.parquet")
    keycol = "event_index"
    it = it.with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("d")).filter(pl.col("d").is_in(days))
    itx = pl.read_parquet(SH / "intentions_text.parquet").join(it.select(keycol, "agent"), on=keycol)
    for a, g1, g2 in itx.select("agent", "goal_text", "short_text").iter_rows():
        links += [(int(a), g) for g in GAME.findall((g1 or "") + " " + (g2 or ""))]
    ac = pl.read_parquet(SH / "artifact_commands_text.parquet", columns=["t", "agent", "cmd", "urls"])
    ac = ac.with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("d")).filter(pl.col("d").is_in(days))
    for a, cmd, urls in ac.select("agent", "cmd", "urls").iter_rows():
        links += [(int(a), g) for g in GAME.findall((cmd or "") + " " + " ".join(urls or []))]
    keep = [(a, g) for a, g in links if g.lower() not in STOP and (any(ch.isdigit() for ch in g) or any(ch.isupper() for ch in g))]
    by = {}
    for a, g in keep:
        by.setdefault(g, set()).add(a)
    pairs = set()
    for g, ags in by.items():
        if len(ags) >= 2:
            pairs |= {tuple(sorted(p)) for p in itertools.combinations(sorted(ags), 2)}
    return {"n_links": len(keep), "n_games": len(by), "n_games_multi_agent": sum(len(v) >= 2 for v in by.values()),
            "n_games_gt2_agents": sum(len(v) > 2 for v in by.values()), "pairs": sorted(pairs), "days": days}


def g23(rng):
    import explore as X
    opp = g23_opponents()
    out = {k: v for k, v in opp.items() if k != "days"}
    out["n_opponent_pairs"] = len(opp["pairs"])
    if len(opp["pairs"]) < 5:
        out["verdict_note"] = "untestable (< 5 opponent pairs)"
        return out
    oppset = set(opp["pairs"])
    # stance: two-way-FE residual stance per unordered pair (>= 2 replies)
    r = replies(23, opp["days"])
    agents = sorted(set(r["b_agent"].to_list()) | set(r["a_agent"].to_list()))
    pos = {x: k for k, x in enumerate(agents)}
    spk, tgt = np.array([pos[x] for x in r["b_agent"]]), np.array([pos[x] for x in r["a_agent"]])
    s = r["s"].to_numpy().astype(float)
    Xd = np.column_stack([np.ones(len(s))] + [(spk == k).astype(float) for k in range(1, len(agents))] + [(tgt == k).astype(float) for k in range(1, len(agents))])
    res = s - Xd @ np.linalg.lstsq(Xd, s, rcond=None)[0]
    pr = {}
    for i, j, v in zip(spk, tgt, res):
        pr.setdefault((min(i, j), max(i, j)), []).append(v)
    pv = {p: np.mean(v) for p, v in pr.items() if len(v) >= 2}

    def T(lab_perm):
        o, n = [], []
        for (i, j), v in pv.items():
            a_, b_ = lab_perm[agents[i]], lab_perm[agents[j]]
            (o if tuple(sorted((a_, b_))) in oppset else n).append(v)
        return (np.mean(o) - np.mean(n)) if o and n else np.nan, len(o), len(n)
    ident = {x: x for x in agents}
    obs, no, nn = T(ident)
    null = np.array([T(dict(zip(agents, rng.permutation(agents))))[0] for _ in range(10000 if not FAST else 2000)])
    out["stance"] = {"n_replies": r.height, "T_opp": obs, "n_opp_pairs": no, "n_other_pairs": nn,
                     "p_less": float((1 + np.sum(null <= obs)) / (1 + np.sum(np.isfinite(null)))),
                     "p_greater": float((1 + np.sum(null >= obs)) / (1 + np.sum(np.isfinite(null)))),
                     "mean_s": float(np.average(s, weights=r["p_reply"].to_numpy()))}
    # content: H22 within-day co-movement on day-thirds pseudo-days (regime I white32), unit '23' built by build.py
    for model in ("bge_small", "gte_modernbert"):
        base = R1B / f"{model}_white32_none"
        X.BASE = base
        meta, ag, wi, wv, di, dv, tk = X.load_unit("G23", "23")
        code = ag["agent"].to_numpy()
        idx = np.arange(len(code))
        Xt, Ot = X.window_tensor(meta, wi, wv, idx)
        Xp, Op = L.to_pseudo_days(Xt, Ot, 3, meta["wins_per_day"])
        st = L.ContentStats(Xp, Op, min_shared=5)
        J = st.J(np.ones(Xp.shape[0], bool))
        cmap = list(code)
        vals = {(min(cmap[i], cmap[j]), max(cmap[i], cmap[j])): J[i, j] for i, j in zip(*np.triu_indices(len(code), 1)) if np.isfinite(J[i, j])}
        ags2 = sorted({x for p in vals for x in p})

        def Tc(perm):
            o, n = [], []
            for (a_, b_), v in vals.items():
                (o if tuple(sorted((perm[a_], perm[b_]))) in oppset else n).append(v)
            return (np.mean(o) - np.mean(n)) if o and n else np.nan, len(o), len(n)
        oc, noc, nnc = Tc({x: x for x in ags2})
        nc = np.array([Tc(dict(zip(ags2, rng.permutation(ags2))))[0] for _ in range(10000 if not FAST else 2000)])
        out[f"content_{model}"] = {"T_opp": oc, "n_opp_pairs": noc, "n_other_pairs": nnc,
                                   "p_less": float((1 + np.sum(nc <= oc)) / (1 + np.sum(np.isfinite(nc)))),
                                   "p_greater": float((1 + np.sum(nc >= oc)) / (1 + np.sum(np.isfinite(nc)))),
                                   "Jbar": float(np.mean(list(vals.values())))}
    return out


def main():
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    if "--ne38-min2" in sys.argv:  # disclosed variant: Amendment 1's short-unit pair threshold (>= 2 shared windows)
        prev = json.loads((R1B / "stance_native.json").read_text())
        prev["native_NE38_min2"] = json.loads(jdump(ne38(rng, min_shared=2)))
        prev["native_NE38_min5_shared_windows"] = json.loads(jdump({k: v for k, v in ne38(rng, min_shared=5).items() if k.endswith("_shared_windows")}))
        (R1B / "stance_native.json").write_text(jdump(prev))
        print("NE38 min2", jdump(prev["native_NE38_min2"]).replace("\n", " ")[:3000])
        return
    out = {"stance": {}}
    base = R1B / "bge_small_white32_none"
    # G23 unit for the native content test (regime I), built with the same r1b settings
    for model in ("bge_small", "gte_modernbert"):
        B.R1B.update(model=model, vectors="white32", dedupe="none", talk="activity_bins_fixed", roles="gt")
        if not (R1B / f"{model}_white32_none/G23/23/meta.json").exists():
            B.build_unit("23", units={"23": ("G23", "2025-12-15", "2025-12-19")}, out_root=R1B / f"{model}_white32_none")
    units = ["51a", "51b", "51c", "51d", "51e"] + sorted(B.shared_units_51())
    for u in units:
        out["stance"][u] = stance_unit(u, "G51", base, rng)
    # pooled non-holdout #51 (roles = majority over present days), like H37's pooled run
    out["stance"]["51all"] = stance_pooled(rng)
    for u in ("38a", "40", "44"):
        out["stance"][u] = stance_unit(u, {"38a": "G38", "40": "G40", "44": "G44"}[u], base, rng)
    out["native_NE38"] = ne38(rng)
    print("NE38", jdump(out["native_NE38"]).replace("\n", " ")[:2000], flush=True)
    out["native_G23"] = g23(rng)
    print("G23", jdump({k: v for k, v in out["native_G23"].items() if k != "pairs"}).replace("\n", " ")[:2000], flush=True)
    out["settings"] = {"NPERM": NPERM, "NSIM": NSIM, "min_replies_per_pair": MIN_N, "fast": FAST}
    out["seconds"] = round(time.time() - t0, 1)
    (R1B / ("stance_native_fast.json" if FAST else "stance_native.json")).write_text(jdump(out))
    print("done", out["seconds"])


def stance_pooled(rng):
    """All non-holdout #51 days as one stance graph (roles: GT majority over present days), unit-level tests only."""
    pu = pl.read_parquet(SH / "period_units.parquet").filter((pl.col("goal_no") == 51) & ~pl.col("holdout"))
    days = sorted({d for ds in pu["days"].to_list() for d in ds})
    r = replies(51, days)
    agents = sorted(set(r["b_agent"].to_list()) | set(r["a_agent"].to_list()))
    spells = RR.load_role_spells_gt()
    present = {a: sorted(set(r.filter((pl.col("b_agent") == a))["pt_date"].to_list())) or days for a in agents}
    roles = RR.unit_roles(spells, agents, days, present)
    lab = dict(zip(*[pl.read_parquet(SH / "roster.parquet")[c].to_list() for c in ("agent", "lab")]))
    J, N = pair_J(r["b_agent"].to_numpy(), r["a_agent"].to_numpy(), r["s"].to_numpy(), r["p_reply"].to_numpy(), agents)
    role_names = sorted({x for x in roles.values() if x is not None})
    lookup = RR.lookup_table(role_names)
    ridx = np.array([role_names.index(roles[a]) if roles[a] is not None else -1 for a in agents])
    t = L.treatment_test(J, ridx, lookup, {"SR": 1, "OP": 2, "K": [1, 2], "SY": 3, "NC": 4},
                         labs=np.array([lab[a] for a in agents]), nperm=NPERM, rng=rng)
    out = {"n_replies": r.height, "n_agents": len(agents), "n_pairs": int(np.isfinite(J[np.triu_indices(len(agents), 1)]).sum()),
           "mean_s": float(np.average(r["s"], weights=r["p_reply"])), "treatment": t,
           "opus5_role": roles.get(40)}
    fa = t["family_adjusted"]
    print(f"51all: replies {r.height} T_SR {fa['SR']['T']} (n {fa['SR']['n']}, p< {fa['SR']['p_less']}, p> {fa['SR']['p_greater']}) "
          f"T_OP {fa['OP']['T']} (n {fa['OP']['n']}) T_SY {fa['SY']['T']} T_NC {fa['NC']['T']}", flush=True)
    return out


if __name__ == "__main__":
    main()
