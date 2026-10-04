"""H73 period-native tests: NE41 (forced erasures), G12 (#12 judges), G51 (#51 private roles), G44 (fine-tuned leader).

Output: data/processed/H73-style-three-components/natives/natives.json (raw numbers + README lines and verdicts).
Usage: uv run python hypotheses/H73-style-three-components/analysis/natives.py [--only NE41,G12,G51,G44]
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ[_v] = "4"
import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import json  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import h73lib as L  # noqa: E402

OUTP = L.DATA / "natives" / "natives.json"


def f2(x, nd=2):
    return "nan" if x is None or not np.isfinite(x) else f"{x:.{nd}f}"


# ============================================================================================ NE41
def ne41() -> dict:
    m3 = L.load_messages().filter(pl.col("regime") == "III")
    a3 = L.arrays(m3)
    pairs = L.ne41_pairs(m3)
    res = {"pooled": L.ne41_fit(a3, pairs)}
    res["pair_counts"] = pairs.group_by("label").len().sort("label").to_dicts()
    # per goal (forced beta), descriptive
    per = {}
    goals = m3["goal_no"].to_numpy()
    for g in sorted(np.unique(goals)):
        pg = pairs.filter(pl.col("unit_id").str.extract(r"^(\d+)").cast(pl.Int64) == int(g))
        if (pg["label"] == "forced").sum() < 50:
            continue
        f = L.ne41_fit(a3, pg, n_boot=150)
        if "forced" in f:
            per[f"G{g:02d}"] = {"beta": f["forced"]["beta"], "lo": f["forced"]["lo"], "hi": f["forced"]["hi"],
                                "n": f["forced"]["n"]}
    res["per_goal"] = per
    # restatement dedupe sensitivity
    m3r = L.load_messages(dedupe="restate").filter(pl.col("regime") == "III")
    res["restate"] = L.ne41_fit(L.arrays(m3r), L.ne41_pairs(m3r), n_boot=150)
    F = res["pooled"]["forced"]
    V = res["pooled"].get("voluntary", {})
    Tr, Tc = F.get("T_raw", {}), F.get("T_corr", {})
    exc_raw, exc_cor = Tr.get("T", np.nan) - 0.5, Tc.get("T", np.nan) - 0.5
    beta_ok = 0.3 <= F["beta"] <= 1.5 and F["lo"] > 0
    halves = exc_raw > 0 and exc_cor <= exc_raw / 2
    verdict = "supported" if beta_ok and halves else ("failed" if F["lo"] <= 0 else "mixed")
    pos = sum(1 for v in per.values() if v["lo"] > 0)
    lines = [f"*Run {dt.datetime.now(dt.UTC):%Y-%m-%d %H:%M} UTC (`analysis/natives.py` → `data/processed/H73-style-three-components/natives/natives.json`).*", "",
             f"- **Pairs** (regime III, non-holdout, copies removed): " + ", ".join(f"{r['label']} {r['len']:,}" for r in res["pair_counts"]) + ".",
             f"- **Forced erasures:** β = {f2(F['beta'])} [{f2(F['lo'])}, {f2(F['hi'])}] (agent-cluster bootstrap; {F['n']:,} pairs). Predicted jump ‖Δx̂‖² = {f2(F['pred_norm2'], 3)} vs observed ‖Δx‖² = {f2(F['obs_norm2'])} (17-d units).",
             f"- **Voluntary consolidations:** β = {f2(V.get('beta', np.nan))} [{f2(V.get('lo', np.nan))}, {f2(V.get('hi', np.nan))}] ({V.get('n', 0):,} pairs).",
             f"- **Gap-matched style percentile of forced pairs:** T_s raw {f2(Tr.get('T', np.nan), 3)} [{f2(Tr.get('lo', np.nan), 3)}, {f2(Tr.get('hi', np.nan), 3)}] → after removing the predicted jump {f2(Tc.get('T', np.nan), 3)} [{f2(Tc.get('lo', np.nan), 3)}, {f2(Tc.get('hi', np.nan), 3)}] (H46: 0.564).",
             f"- **Per goal (forced β, descriptive):** CI above 0 in {pos}/{len(per)} goals; " + "; ".join(f"{k} {f2(v['beta'])}" for k, v in per.items()) + ".",
             f"- **Restatements removed (either model):** forced β = {f2(res['restate']['forced']['beta'])} [{f2(res['restate']['forced']['lo'])}, {f2(res['restate']['forced']['hi'])}].",
             f"- **Verdict rule (fixed in the card, 19:13 UTC):** β ∈ [0.3, 1.5] with CI > 0 and the T_s excess at least halved → supported; β CI including 0 → failed; otherwise mixed. **Verdict: {verdict}.**"]
    score = ("- **E (interventional):** the scaffold-timed erasure is the intervention; " +
             ("the drift fitted inside segments predicts the erasure jump." if beta_ok else "the drift fitted inside segments does not predict the erasure jump in the stated range.") +
             "\n- **D (unfitted):** β is an out-of-fold, unfitted statistic (Amendment A1).\n- **H (rivals):** R5 (directionless excursion) predicts β ≈ 0 with T_s ≈ 0.556 (synthetic S2).")
    res.update({"verdict": verdict, "lines": lines, "score": score})
    return res


# ============================================================================================ G12
def g12(n_perm: int = 1000) -> dict:
    m = L.load_messages().filter(pl.col("goal_no") == 12)
    a = L.arrays(m)
    deb = m["debate"].to_numpy()
    reg = a["register"].copy()
    Y = a["X"] - a["X"].mean(0)
    G, A, C = L.block_G(a), L.block_A(a), L.block_C(a)
    base = L.decompose(a, n_perm=0)
    r_gac = base["r2a"]["GAC"]
    den = base["kappa"] - base["r2a"]["G"]
    # residuals after G + A + C (no register)
    _, _, _, Res, _, _ = L.fit_r2(Y, [G, A, C], return_resid=True)
    judges = sorted(set(a["agent"][reg == "judge"]))

    def shifts(rg):
        out = {}
        for j in judges:
            jj = (a["agent"] == j) & (rg == "judge")
            dd = (a["agent"] == j) & (rg == "debater")
            if jj.sum() >= 3 and dd.sum() >= 3:
                out[j] = Res[jj].mean(0) - Res[dd].mean(0)
        return out

    def coh(sh):
        cs = []
        for j, v in sh.items():
            oth = [w for k, w in sh.items() if k != j]
            if not oth:
                continue
            mo = np.mean(oth, axis=0)
            cs.append(float(v @ mo / (np.linalg.norm(v) * np.linalg.norm(mo) + 1e-12)))
        return float(np.mean(cs)) if cs else np.nan, cs

    def dR(rg):
        b = dict(a); b["register"] = rg
        return L.fit_r2(Y, [G, A, C, L.block_R(b)])[1] - r_gac

    # permutation: shuffle judge/debater roles over each judge's debate windows (count kept)
    win = {}
    for j in judges:
        ws = sorted(set(deb[(a["agent"] == j) & np.isin(reg, ["judge", "debater"])]))
        nj = len(set(deb[(a["agent"] == j) & (reg == "judge")]))
        win[j] = (ws, nj)
    rng = np.random.default_rng(12)

    def perm_reg():
        rg = reg.copy()
        for j, (ws, nj) in win.items():
            jw = set(rng.choice(ws, nj, replace=False))
            for w in ws:
                msk = (a["agent"] == j) & (deb == w) & np.isin(reg, ["judge", "debater"])
                rg[msk] = "judge" if w in jw else "debater"
        return rg

    obs_dR = dR(reg)
    sh = shifts(reg)
    obs_coh, cos_list = coh(sh)
    null_dR, null_coh = [], []
    for _ in range(n_perm):
        rg = perm_reg()
        null_dR.append(dR(rg))
        null_coh.append(coh(shifts(rg))[0])
    null_dR, null_coh = np.array(null_dR), np.array(null_coh)
    p_R = float((1 + (null_dR >= obs_dR).sum()) / (1 + n_perm))
    p_coh = float((1 + (np.nan_to_num(null_coh, nan=-9) >= obs_coh).sum()) / (1 + n_perm))
    # attribution of judge-window messages: centroids from non-judge messages; + LOAO judge shift on every centroid
    X0 = a["X"].copy()
    for d in np.unique(a["day"]):
        ix = a["day"] == d
        X0[ix] -= X0[ix].mean(0)
    agents = np.unique(a["agent"])
    acc = {"k5": {"blind": [], "reg": []}, "window": {"blind": [], "reg": []}}
    for j in judges:
        trm = ~((a["agent"] == j) & (reg == "judge"))
        mu = np.stack([X0[trm & (a["agent"] == g)].mean(0) for g in agents])
        R = X0[trm] - mu[np.searchsorted(agents, a["agent"][trm])]
        sd = np.sqrt((R ** 2).mean(0)) + 1e-9
        oth = [v for k, v in sh.items() if k != j]
        if not oth:
            continue
        rho = np.mean(oth, axis=0)
        te = np.where((a["agent"] == j) & (reg == "judge"))[0]
        te = te[np.argsort(a["t"][te])]
        blocks = {"k5": [te[i:i + 5] for i in range(0, len(te) - 4, 5)],
                  "window": [te[deb[te] == w] for w in sorted(set(deb[te]))]}
        for kk, bl in blocks.items():
            for b in bl:
                x = X0[b]
                s0 = (((x[:, None] - mu[None]) / sd) ** 2).sum(2).mean(0)
                s1 = (((x[:, None] - (mu + rho)[None]) / sd) ** 2).sum(2).mean(0)
                acc[kk]["blind"].append((j, agents[np.argmin(s0)] == j))
                acc[kk]["reg"].append((j, agents[np.argmin(s1)] == j))

    def bal(lst):
        if not lst:
            return np.nan
        arr = np.array(lst, dtype=float)
        return float(np.mean([arr[arr[:, 0] == j, 1].mean() for j in np.unique(arr[:, 0])]))
    att = {kk: {"blind": bal(v["blind"]), "reg": bal(v["reg"]), "n": len(v["blind"])} for kk, v in acc.items()}
    gain5 = att["k5"]["reg"] - att["k5"]["blind"]
    n_reg = {r: int((reg == r).sum()) for r in ("judge", "debater", "none")}
    ok_i = obs_dR > 0 and p_R < 0.05
    ok_ii = obs_coh > 0 and p_coh < 0.05
    ok_iii = gain5 >= 0.05
    verdict = "supported" if (ok_i and ok_ii and ok_iii) else ("failed" if obs_coh <= 0 else "mixed")
    lines = [f"*Run {dt.datetime.now(dt.UTC):%Y-%m-%d %H:%M} UTC (`analysis/natives.py` → `natives.json`, key G12).*", "",
             f"- **Messages:** {a['X'].shape[0]:,} (judge {n_reg['judge']}, debater {n_reg['debater']}, outside {n_reg['none']}); judges with ≥ 3 judge and ≥ 3 debater messages: {len(sh)} of {len(judges)}.",
             f"- **(i) Register share:** ΔR²_adj(R | G, A, C) = {obs_dR:.4f} (u_R = {obs_dR / den:.3f} of the non-day systematic variance); judge-window permutation p = {p_R:.3f} ({n_perm} draws).",
             f"- **(ii) Shared judge direction:** mean leave-agent-out cosine = {obs_coh:+.2f} (per judge: " + ", ".join(f"{c:+.2f}" for c in cos_list) + f"); permutation p = {p_coh:.3f}; null mean {np.nanmean(null_coh):+.2f}.",
             f"- **(iii) Attribution of judge messages:** blocks of 5: blind {f2(att['k5']['blind'])} → with the shared judge shift {f2(att['k5']['reg'])} (Δ = {gain5:+.2f}; {att['k5']['n']} blocks); whole judge windows: {f2(att['window']['blind'])} → {f2(att['window']['reg'])} ({att['window']['n']} windows). Chance {1 / len(agents):.2f}.",
             f"- **Verdict (rule fixed 19:28 UTC):** (i) {'pass' if ok_i else 'fail'}, (ii) {'pass' if ok_ii else 'fail'}, (iii) {'pass' if ok_iii else 'fail'} → **{verdict}**."]
    score = ("- **G (ground truth):** DQ6 judge and team windows define the register.\n- **E (interventional):** the judge draw assigns the register from outside; "
             + ("judging moves style in a shared direction." if ok_ii else "the register shift is not shared across judges.")
             + "\n- **H (rivals):** a shared direction separates an assigned register from agent-specific responses.")
    return {"verdict": verdict, "lines": lines, "score": score, "dR": obs_dR, "u_R": obs_dR / den, "p_R": p_R,
            "coh": obs_coh, "cos": cos_list, "p_coh": p_coh, "att": att, "n_reg": n_reg}


# ============================================================================================ G51
def _era_fit(a: dict, post: np.ndarray, with_C: bool, incumbents: np.ndarray):
    """Fit G + C + agent x era FE; return centred R_i (post - pre) and unbiased squared norms for incumbents."""
    Y = a["X"] - a["X"].mean(0)
    G = L.block_G(a)
    C = L.block_C(a) if with_C else np.zeros((len(Y), 0))
    lab = np.array([f"{g}|{int(p)}" for g, p in zip(a["agent"], post)])
    E = L.dummies(lab, drop=None)
    lv = np.unique(lab)
    X = np.column_stack([np.ones(len(Y)), G, C, E])
    B, *_ = np.linalg.lstsq(X, Y, rcond=None)
    Res = Y - X @ B
    trS = float((Res ** 2).sum() / max(len(Y) - np.linalg.matrix_rank(X[:: max(1, len(Y) // 4000)]), 1))
    off = 1 + G.shape[1] + C.shape[1]
    coef = {l: B[off + k] for k, l in enumerate(lv)}
    R, var = {}, {}
    for g in incumbents:
        k0, k1 = f"{g}|0", f"{g}|1"
        if k0 in coef and k1 in coef:
            R[g] = coef[k1] - coef[k0]
            var[g] = trS * (1 / (lab == k0).sum() + 1 / (lab == k1).sum())
    keys = list(R)
    M = np.mean([R[g] for g in keys], axis=0)
    Rc = {g: R[g] - M for g in keys}
    n2 = {g: float((Rc[g] ** 2).sum() - var[g]) for g in keys}
    return Rc, n2


def g51() -> dict:
    mall = L.load_messages()
    pre = mall.filter((pl.col("regime") == "III") & pl.col("goal_no").is_between(36, 44))
    p51 = mall.filter(pl.col("goal_no") == 51)
    ONSET, END1, LAST = "2026-07-06", "2026-07-24", "2026-09-06"
    m = pl.concat([pre, p51.filter(pl.col("pt_date") <= END1)])
    cnt_pre = pre.group_by("agent").len().filter(pl.col("len") >= 20)["agent"].to_list()
    cnt_51 = p51.filter(pl.col("pt_date") <= END1).group_by("agent").len().filter(pl.col("len") >= 20)["agent"].to_list()
    inc = np.array(sorted(set(cnt_pre) & set(cnt_51)))
    m = m.filter(pl.col("agent").is_in(inc.tolist()))
    a = L.arrays(m)
    post = a["day"] >= ONSET
    real = {wc: _era_fit(a, post, wc, inc) for wc in (True, False)}
    # placebo splits (3-week post window), none straddling the onset
    pdays = sorted(pre.filter(pl.col("agent").is_in(inc.tolist()))["pt_date"].unique().to_list())
    d0, d1 = dt.date.fromisoformat(pdays[0]), dt.date.fromisoformat(pdays[-1])
    splits = []
    s = d0 + dt.timedelta(days=14)
    while s <= d1 - dt.timedelta(days=7):
        splits.append(("pre", s)); s += dt.timedelta(days=7)
    for s in ("2026-07-27", "2026-08-03", "2026-08-10", "2026-08-17"):
        splits.append(("51", dt.date.fromisoformat(s)))
    plac = {True: {g: [] for g in inc}, False: {g: [] for g in inc}}
    used = []
    for era, s in splits:
        e = s + dt.timedelta(days=21)
        if era == "pre":
            mm = pre.filter(pl.col("agent").is_in(inc.tolist()) & (pl.col("pt_date") < e.isoformat()))
        else:
            mm = p51.filter(pl.col("agent").is_in(inc.tolist()) & (pl.col("pt_date") < min(e.isoformat(), "2026-09-07")))
        b = L.arrays(mm)
        pp = b["day"] >= s.isoformat()
        if pp.sum() < 200 or (~pp).sum() < 200:
            continue
        used.append(f"{era}:{s.isoformat()}")
        for wc in (True, False):
            _, n2 = _era_fit(b, pp, wc, inc)
            for g, v in n2.items():
                plac[wc][g].append(v)
    pct = {wc: {int(g): (float(np.mean(np.array(plac[wc][g]) < real[wc][1][g])) if len(plac[wc][g]) else np.nan,
                         len(plac[wc][g])) for g in real[wc][1]} for wc in (True, False)}
    # media coherence (centred R_i, with C)
    Rc = real[True][0]
    media = [g for g in (12, 16, 18, 22) if g in Rc]
    keys = sorted(Rc)
    U = {g: Rc[g] / (np.linalg.norm(Rc[g]) + 1e-12) for g in keys}

    def mean_cos(S):
        S = list(S)
        return float(np.mean([U[x] @ U[y] for i, x in enumerate(S) for y in S[i + 1:]]))
    obs = mean_cos(media)
    others = [g for g in keys if g not in media]
    oth_pairs = float(np.mean([U[x] @ U[y] for i, x in enumerate(keys) for y in keys[i + 1:]
                               if not (x in media and y in media)]))
    rng = np.random.default_rng(51)
    null = np.array([mean_cos(rng.choice(keys, len(media), replace=False)) for _ in range(5000)])
    p_coh = float((1 + (null >= obs).sum()) / 5001)
    # post hoc PH3 (labelled): H46's design, 3-day blocks (last 3 eligible days before #45 vs 07-06..07-08),
    # placebo = 3-day block pairs >= 21 days apart inside one era, same era fit (with and without C)
    def blocks_of(days, k=3):
        return [days[i:i + k] for i in range(0, len(days) - k + 1, k)]
    pre_days = sorted(pre.filter(pl.col("agent").is_in(inc.tolist()))["pt_date"].unique().to_list())
    d51 = sorted(p51.filter(pl.col("agent").is_in(inc.tolist()) & (pl.col("pt_date") <= LAST))["pt_date"].unique().to_list())
    allm = pl.concat([pre, p51.filter(pl.col("pt_date") <= LAST)]).filter(pl.col("agent").is_in(inc.tolist()))

    def blk_fit(b0, b1, wc):
        mm = allm.filter(pl.col("pt_date").is_in(b0 + b1))
        b = L.arrays(mm)
        return _era_fit(b, np.isin(b["day"], b1), wc, inc)[1]
    ph3 = {}
    for g0 in (10,):    # agent-time blocks, as in H46: the agent's own eligible days
        ad_pre = sorted(pre.filter(pl.col("agent") == g0)["pt_date"].unique().to_list())
        ad_51 = sorted(p51.filter((pl.col("agent") == g0) & (pl.col("pt_date") <= LAST))["pt_date"].unique().to_list())
        for wc in (True, False):
            real3 = blk_fit(ad_pre[-3:], ad_51[:3], wc).get(g0, np.nan)
            vals = []
            for days in (ad_pre, ad_51):
                bl = blocks_of(days)
                for i in range(len(bl)):
                    for j in range(i + 1, len(bl)):
                        if (dt.date.fromisoformat(bl[j][0]) - dt.date.fromisoformat(bl[i][-1])).days >= 21:
                            v = blk_fit(bl[i], bl[j], wc).get(g0)
                            if v is not None:
                                vals.append(v)
            ph3["withC" if wc else "noC"] = {str(g0): (float(np.mean(np.array(vals) < real3)) if vals else np.nan, len(vals))}
    pr_c, npl = pct[True].get(10, (np.nan, 0))
    pr_n, _ = pct[False].get(10, (np.nan, 0))
    ok_i = pr_c >= 0.95
    ok_ii = p_coh < 0.05
    verdict = "supported" if (ok_i and ok_ii) else ("failed" if (pr_c < 0.9 and not ok_ii) else "mixed")
    roster = pl.read_parquet(L.SH / "roster.parquet").select("agent", "name", "lab")
    lab = dict(zip(roster["agent"].to_list(), roster["lab"].to_list()))
    ranks = sorted(((int(g), real[True][1][g]) for g in keys), key=lambda t: -t[1])
    lines = [f"*Run {dt.datetime.now(dt.UTC):%Y-%m-%d %H:%M} UTC (`analysis/natives.py` → `natives.json`, key G51).*", "",
             f"- **Sample:** {len(inc)} incumbents with ≥ 20 eligible messages in #36–#44 (regime III, non-holdout) and in #51 07-06 → 07-24; {a['X'].shape[0]:,} messages. Placebo splits: {len(used)} ({', '.join(used)}).",
             f"- **(i) Prankster (agent 10):** unbiased ‖R‖² = {real[True][1].get(10, np.nan):.3f} with the context component, {real[False][1].get(10, np.nan):.3f} without; percentile among its {npl} placebo shifts {f2(pr_c)} (with C) and {f2(pr_n)} (without C). Its rank among incumbents by ‖R‖²: {[g for g, _ in ranks].index(10) + 1 if 10 in Rc else 'n/a'} of {len(ranks)}.",
             f"- **Incumbents at percentile ≥ 0.95 (with C):** " + ", ".join(f"{g} ({lab.get(g, '')})" for g, (p, n) in pct[True].items() if p >= 0.95) + ".",
             f"- **(ii) Media coherence:** mean pairwise cosine of the centred R_i among media incumbents {media} = {obs:+.2f}; other incumbent pairs {oth_pairs:+.2f}; random 4-sets {null.mean():+.2f}; permutation p = {p_coh:.3f}.",
             f"- **Verdict (rule fixed 19:28 UTC):** (i) {'pass' if ok_i else 'fail'}, (ii) {'pass' if ok_ii else 'fail'} → **{verdict}**.",
             f"- *Post hoc PH3 (H46's 3-day-block design, same era fit):* Prankster percentile {f2(ph3['withC'].get('10', (np.nan, 0))[0])} with C, {f2(ph3['noC'].get('10', (np.nan, 0))[0])} without C, among {ph3['withC'].get('10', (np.nan, 0))[1]} of its own 3-day block pairs ≥ 21 days apart (H46: 1.00 among 15)."]
    score = ("- **E (interventional):** the 07-06 role assignment is the intervention; the Prankster's shift "
             + ("survives the context component." if ok_i else "does not exceed its placebo band once context is removed.")
             + "\n- **G (ground truth):** DQ6 roles and role classes.\n- **H (rivals):** class coherence tests an assigned register against agent-specific responses.")
    return {"verdict": verdict, "lines": lines, "score": score, "incumbents": inc.tolist(), "placebos": used,
            "pct_withC": {str(k): v for k, v in pct[True].items()}, "pct_noC": {str(k): v for k, v in pct[False].items()},
            "n2_withC": {str(k): v for k, v in real[True][1].items()}, "media_cos": obs, "other_cos": oth_pairs,
            "p_coh": p_coh, "null_mean": float(null.mean()), "ph3_blocks": ph3}


# ============================================================================================ G44
def g44() -> dict:
    mall = L.load_messages(main_only=False)
    m = mall.filter((pl.col("regime") == "III") & pl.col("goal_no").is_between(36, 44) & (pl.col("main") | (pl.col("agent") == 28)))
    a = L.arrays(m)
    X0 = a["X"].copy()
    for d in np.unique(a["day"]):
        ix = a["day"] == d
        X0[ix] -= X0[ix].mean(0)
    lead = a["agent"] == 28
    tr = ~lead
    agents = np.array([g for g in np.unique(a["agent"][tr]) if (a["agent"][tr] == g).sum() >= 20])
    trm = tr & np.isin(a["agent"], agents)
    mu = np.stack([X0[trm & (a["agent"] == g)].mean(0) for g in agents])
    ai = np.searchsorted(agents, a["agent"][trm])
    R = X0[trm] - mu[ai]
    sd = np.sqrt((R ** 2).mean(0)) + 1e-9
    bins = a["bin"]
    prof = np.zeros((len(L.BIN_NAMES), X0.shape[1]))
    for b in range(len(L.BIN_NAMES)):
        mb = bins[trm] == b
        if mb.sum() >= 5:
            prof[b] = R[mb].mean(0)
    Xd = X0 - prof[bins]
    mud = np.stack([Xd[trm & (a["agent"] == g)].mean(0) for g in agents])
    Rd = Xd[trm] - mud[ai]
    z = a["z"]
    lam = 20 * float((z[trm] ** 2).mean())
    bsl = np.stack([(Rd[ai == k] * z[trm][ai == k, None]).sum(0) / ((z[trm][ai == k] ** 2).sum() + lam) for k in range(len(agents))])
    x, xd, zl = X0[lead], Xd[lead], z[lead]
    s_bl = (((x[:, None] - mu[None]) / sd) ** 2).sum(2).mean(0)
    s_dt = (((xd[:, None] - mud[None]) / sd) ** 2).sum(2).mean(0)
    s_ag = (((xd[:, None] - (mud[None] + bsl[None] * zl[:, None, None])) / sd) ** 2).sum(2).mean(0)
    roster = pl.read_parquet(L.SH / "roster.parquet")
    nm = dict(zip(roster["agent"].to_list(), roster["name"].to_list()))

    def rank(s, g=25):
        o = agents[np.argsort(s)]
        return int(np.where(o == g)[0][0]) + 1, [nm[int(k)] for k in o[:3]]
    rb, rd, ra = rank(s_bl), rank(s_dt), rank(s_ag)
    ok = rb[0] <= 2 and rd[0] <= 2 and rd[0] <= rb[0]
    verdict = "descriptive"
    lines = [f"*Run {dt.datetime.now(dt.UTC):%Y-%m-%d %H:%M} UTC (`analysis/natives.py` → `natives.json`, key G44).*", "",
             f"- **Sample:** {int(lead.sum())} eligible leader messages (agent 28, #44); {len(agents)} candidate centroids from regime-III #36–#44 (non-holdout, ≥ 20 messages).",
             f"- **Rank of base Kimi K2.6:** blind {rb[0]}, common-detrended {rd[0]}, agent-specific context {ra[0]} of {len(agents)}. Top 3 blind: {', '.join(rb[1])}; detrended: {', '.join(rd[1])}.",
             f"- **N4 (descriptive):** Kimi rank ≤ 2 in both variants and no loss from detrending: {'met' if ok else 'not met'}. Verdict: descriptive (one block of {int(lead.sum())} messages)."]
    score = "- **G (ground truth):** the leader's base model is known (H23, DQ6); the weights component should point to it."
    return {"verdict": verdict, "lines": lines, "score": score, "rank_blind": rb[0], "rank_det": rd[0], "rank_agent": ra[0],
            "n_leader": int(lead.sum()), "n_cand": int(len(agents)), "met": ok}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="NE41,G12,G51,G44")
    args = ap.parse_args()
    out = json.loads(OUTP.read_text()) if OUTP.exists() else {}
    fns = {"NE41": ne41, "G12": g12, "G51": g51, "G44": g44}
    for k in args.only.split(","):
        out[k] = fns[k]()
        print(k, "\n".join(out[k]["lines"]), flush=True)
    OUTP.parent.mkdir(parents=True, exist_ok=True)
    OUTP.write_text(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
