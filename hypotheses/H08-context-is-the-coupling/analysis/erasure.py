"""C3 / NE41: does erasing the context (consolidation) cut the coupling to what was in it?

  uv run python hypotheses/H08-context-is-the-coupling/analysis/erasure.py

Units: (talk turn tau of i, agent sender j) where j's latest message in i's room before s(tau) is <= 30 min old.
- new: first visible at tau's call; old: read by an earlier call of i;
- erased: a consolidation turn of i lies strictly between the old message's read-out turn and tau (ambiguous units,
  where the read-out turn is the consolidation turn itself, are dropped); forced / voluntary from H15's catalog
  (data/processed/H15-semantic-information-scrambles/consolidations.parquet: CF = 41-42-turn segment, CV = 10-38);
- PC(tau): a consolidation of i in the 30 min before s(tau); engaged: i's previous talk turn addressed j.
Response: tau addresses j (chat_mentions_clean.mentions_roster). Linear probability model with agent x day effects,
age bins; day-cluster bootstrap (B = 200). Equation of state from H15's voluntary segments and H08 token inflow.
Writes G<NN>/c3.json and ne41_pooled.json (random-effects pooling, exception (c): each erasure is a transition object).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h08lib import *  # noqa: E402,F403
from scipy.stats import spearmanr  # noqa: E402

sys.path.insert(0, str(ROOT / "infra/shared"))
from common import mention_regexes  # noqa: E402

B = 200
C3_PERIODS = [36, 37, 38, 39, 40, 41, 42, 44, 51]
AGE_EDGES = [0, 2, 5, 10, 20, 30]
XN = ["erased_F", "erased_V", "erased_O", "new", "PC", "engaged", "age2", "age3", "age4", "age5"]
H15C = ROOT / "data/processed/H15-semantic-information-scrambles/consolidations.parquet"


def units_for_period(g: int, detectable: set, folder: Path | None = None, kinds: str = "h15"):
    tu = pl.read_parquet((folder or (OUT / gname(g))) / "turns.parquet")
    if g == 36:
        tu = tu.filter(pl.col("pt_date") >= "2026-03-24")
    days = sorted(tu["pt_date"].unique().to_list())
    chat = pl.read_parquet(SH / "chat_core.parquet", columns=["t", "pt_date", "speaker_kind", "agent"]).with_row_index("msg")
    chat = chat.filter(pl.col("pt_date").is_in(days) & (pl.col("speaker_kind").cast(pl.Utf8) == "agent"))
    ex = pl.read_parquet(SH / "exposure.parquet", columns=["msg", "agent"]).rename({"agent": "rec"})
    ex = ex.join(chat.select("msg", "t", "pt_date", pl.col("agent").alias("snd")), on="msg", how="inner")
    ex = ex.filter((pl.col("rec") != pl.col("snd")) & pl.col("snd").is_in(list(detectable)))
    h15 = pl.read_parquet(H15C).select("agent", "t", "kind")
    kind_at = {}
    for (a,), sub in h15.group_by(["agent"]):
        kind_at[int(a)] = (us(sub.sort("t")["t"]), sub.sort("t")["kind"].to_list())
    rows = []
    eos = []
    for (a, d), T in tu.group_by(["agent", "pt_date"], maintain_order=True):
        a = int(a)
        T = T.sort("t_us")
        t = T["t_us"].to_numpy(); s = T["s_us"].to_numpy(); talk = T["talk"].to_numpy(); cons = T["cons"].to_numpy()
        ment = T["ment"].to_numpy().astype(np.uint64); unc = T["unc"].to_numpy(); ctx = T["ctx"].to_numpy()
        cidx = np.nonzero(cons)[0]
        # kinds of the consolidation turns (H15 catalog, nearest within 2 s); kinds="segment" re-derives H15's rule
        # (41-42 computer-use turns since the previous consolidation = CF, 10-38 = CV) for days outside H15's catalog
        ckind = {}
        if kinds == "segment":
            act = T["act"].to_numpy() if "act" in T.columns else np.array([""] * len(t), dtype=object)
            cu = np.array([x != "" for x in act]) | T["pause"].to_numpy()
            prevc = -1
            for c in cidx:
                n = int(cu[prevc + 1:c].sum())
                ckind[c] = "CF" if 41 <= n <= 42 else ("CV" if 10 <= n <= 38 else "other")
                prevc = c
        elif a in kind_at:
            kt, kk = kind_at[a]
            for c in cidx:
                j = np.searchsorted(kt, t[c])
                best = None
                for jj in (j - 1, j):
                    if 0 <= jj < len(kt) and abs(kt[jj] - t[c]) <= 2 * US:
                        best = kk[jj]
                ckind[c] = best or "unknown"
        # equation of state: per consolidation, segment length (turns since previous cons) and mean uncached tokens
        prev = -1
        for c in cidx:
            seg = slice(prev + 1, c)
            n = c - prev - 1
            if n >= 5 and prev >= 0:
                u = unc[seg]
                eos.append((a, d, ckind.get(c, "unknown"), int(n), float(np.nanmean(u)) if np.isfinite(u).any() else np.nan,
                            float(ctx[c - 1]) if c >= 1 and np.isfinite(ctx[c - 1]) else np.nan))
            prev = c
        M = ex.filter((pl.col("rec") == a) & (pl.col("pt_date") == d)).sort("t")
        if not M.height:
            continue
        mt = us(M["t"]); ms = M["snd"].to_numpy().astype(int)
        tk = np.nonzero(talk)[0]
        prev_talk = -1
        for k in tk:
            sk = s[k]
            if sk < -(2 ** 61):
                prev_talk = k
                continue
            lo = np.searchsorted(mt, sk - 30 * 60 * US, side="left"); hi = np.searchsorted(mt, sk, side="left")
            if hi > lo:
                last = {}
                for q in range(lo, hi):
                    last[ms[q]] = mt[q]
                pc = bool(((t[cidx] > sk - 30 * 60 * US) & (t[cidx] <= sk)).any()) if len(cidx) else False
                for j, tmj in last.items():
                    if j == a:
                        continue
                    R = int(np.searchsorted(s, tmj, side="right"))
                    new = R == k
                    erased, amb, kind = False, False, ""
                    if R < k:
                        cs = cidx[(cidx >= R) & (cidx < k)]
                        if len(cs):
                            if (cs == R).any() and not (cs > R).any():
                                amb = True
                            else:
                                erased = True
                                kind = ckind.get(int(cs[cs > R][-1]), "unknown")
                    if amb:
                        continue
                    age = (sk - tmj) / US / 60
                    eng = prev_talk >= 0 and bool((ment[prev_talk] >> np.uint64(j)) & np.uint64(1))
                    y = bool((ment[k] >> np.uint64(j)) & np.uint64(1))
                    rows.append((a, d, int(k), int(j), bool(y), bool(new), bool(erased), kind, bool(pc), bool(eng), float(age)))
            prev_talk = k
    U = pl.DataFrame(rows, schema={"agent": pl.Int16, "pt_date": pl.Utf8, "k": pl.Int64, "snd": pl.Int16, "y": pl.Boolean,
                                   "new": pl.Boolean, "erased": pl.Boolean, "kind": pl.Utf8, "PC": pl.Boolean,
                                   "engaged": pl.Boolean, "age": pl.Float64}, orient="row")
    E = pl.DataFrame(eos, schema={"agent": pl.Int16, "pt_date": pl.Utf8, "kind": pl.Utf8, "seg_len": pl.Int64,
                                  "unc_mean": pl.Float64, "ctx_pre": pl.Float64}, orient="row")
    return U, E, days


def design(U: pl.DataFrame):
    age = U["age"].to_numpy()
    ab = np.digitize(age, AGE_EDGES[1:-1], right=True)          # 0..4
    kind = U["kind"].to_list()
    er = U["erased"].to_numpy()
    X = np.column_stack([er & np.array([k == "CF" for k in kind]), er & np.array([k == "CV" for k in kind]),
                         er & np.array([k not in ("CF", "CV") for k in kind]), U["new"].to_numpy(), U["PC"].to_numpy(),
                         U["engaged"].to_numpy()] + [(ab == b) for b in range(1, 5)]).astype(float)
    return X, U["y"].to_numpy().astype(float)


def fe_ols(U: pl.DataFrame, days: list[str], W: np.ndarray):
    X, y = design(U)
    dix = {d: i for i, d in enumerate(days)}
    grp = (U["agent"].cast(pl.Int64) * 10000 + U["pt_date"].replace_strict(dix, return_dtype=pl.Int64)).to_numpy()
    _, gi = np.unique(grp, return_inverse=True)
    cnt = np.bincount(gi).astype(float)
    Xd = X - (np.stack([np.bincount(gi, X[:, j]) for j in range(X.shape[1])], 1) / cnt[:, None])[gi]
    yd = y - (np.bincount(gi, y) / cnt)[gi]
    di = U["pt_date"].replace_strict(dix, return_dtype=pl.Int64).to_numpy()
    nd = len(days)
    XtX = np.zeros((nd, X.shape[1], X.shape[1])); Xty = np.zeros((nd, X.shape[1]))
    for dd in range(nd):
        m = di == dd
        XtX[dd] = Xd[m].T @ Xd[m]; Xty[dd] = Xd[m].T @ yd[m]
    betas = []
    for w in W:
        A = np.tensordot(w, XtX, 1); b = w @ Xty
        try:
            betas.append(np.linalg.solve(A + 1e-9 * np.eye(len(b)), b))
        except np.linalg.LinAlgError:
            betas.append(np.full(len(b), np.nan))
    return np.array(betas)


def run(g: int, detectable: set, folder: Path | None = None, kinds: str = "h15"):
    folder = folder or (OUT / gname(g))
    if not (folder / "turns.parquet").exists():
        return None
    U, E, days = units_for_period(g, detectable, folder, kinds)
    nd = len(days)
    rng = np.random.default_rng(g)
    W = np.vstack([np.ones((1, nd)), rng.multinomial(nd, np.full(nd, 1 / nd), size=B)]).astype(float)
    out = {"period": gname(g), "n_days": nd, "n_units": U.height}
    if U.height:
        er = U.filter(pl.col("erased"))
        out["n_erased"] = {k: int(v) for k, v in er.group_by("kind").len().iter_rows()}
        out["n_old_notErased_PC"] = int(U.filter(~pl.col("new") & ~pl.col("erased") & pl.col("PC")).height)
        ref = U.filter(~pl.col("new") & ~pl.col("erased") & pl.col("PC"))["y"].mean()
        out["ref_rate_old_inContext_PC"] = float(ref) if ref is not None else None
        out["rates"] = {"new": float(U.filter(pl.col("new"))["y"].mean() or 0),
                        "old_kept": float(U.filter(~pl.col("new") & ~pl.col("erased"))["y"].mean() or 0),
                        "old_erased_F": float(U.filter(pl.col("erased") & (pl.col("kind") == "CF"))["y"].mean() or 0),
                        "old_erased_V": float(U.filter(pl.col("erased") & (pl.col("kind") == "CV"))["y"].mean() or 0)}
        if U.filter(pl.col("erased")).height >= 50:
            bt = fe_ols(U, days, W)
            out["beta"] = {n: ci(bt[:, j]) for j, n in enumerate(XN)}
            if ref:
                out["rel_F"] = ci(bt[:, 0] / ref); out["rel_V"] = ci(bt[:, 1] / ref)
            out["F_minus_V"] = ci(bt[:, 0] - bt[:, 1])
    if E.height:
        cv = E.filter(pl.col("kind") == "CV").drop_nulls().filter(pl.col("unc_mean").is_not_nan())
        if cv.height >= 30:
            cv = cv.with_columns(pl.col("seg_len").log().alias("ls"), pl.col("unc_mean").log().alias("lu"))
            cv = cv.with_columns((pl.col("ls") - pl.col("ls").mean().over("agent")).alias("lsd"),
                                 (pl.col("lu") - pl.col("lu").mean().over("agent")).alias("lud"))
            out["eos_rho_voluntary"] = float(spearmanr(cv["lsd"].to_numpy(), cv["lud"].to_numpy()).statistic)
            out["eos_n_voluntary"] = cv.height
            # day bootstrap of rho
            dd = {d: i for i, d in enumerate(days)}
            di = cv["pt_date"].replace_strict(dd, default=-1, return_dtype=pl.Int64).to_numpy()
            rr = []
            for w in W[1:]:
                idx = np.concatenate([np.repeat(np.nonzero(di == k)[0], int(w[k])) for k in range(nd) if w[k] > 0])
                if len(idx) > 10:
                    rr.append(spearmanr(cv["lsd"].to_numpy()[idx], cv["lud"].to_numpy()[idx]).statistic)
            out["eos_rho_voluntary_ci"] = [out["eos_rho_voluntary"]] + [float(x) for x in np.nanpercentile(rr, [2.5, 97.5])]
        ctxs = {k: E.filter(pl.col("kind") == k)["ctx_pre"].drop_nans().drop_nulls().to_numpy() for k in ("CF", "CV")}
        out["ctx_pre_median"] = {k: (float(np.median(v)) if len(v) else None) for k, v in ctxs.items()}
        out["seg_len_median"] = {k: float(E.filter(pl.col("kind") == k)["seg_len"].median() or 0) for k in ("CF", "CV")}
        out["n_cons"] = {k: int(v) for k, v in E.group_by("kind").len().iter_rows()}
    jdump(out, folder / "c3.json")
    b = out.get("beta", {})
    print(f"{gname(g)}: units {U.height}, erased {out.get('n_erased')}, beta_F {b.get('erased_F')}, beta_V {b.get('erased_V')}, "
          f"rel_F {out.get('rel_F')}, eos rho {out.get('eos_rho_voluntary')}", flush=True)
    return out


def dl_meta(est, se):
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    if len(est) < 2:
        return None
    w = 1 / se ** 2
    mu_fe = np.sum(w * est) / np.sum(w)
    Q = np.sum(w * (est - mu_fe) ** 2)
    tau2 = max(0.0, (Q - (len(est) - 1)) / (np.sum(w) - np.sum(w ** 2) / np.sum(w)))
    ws = 1 / (se ** 2 + tau2)
    mu = np.sum(ws * est) / np.sum(ws)
    return {"mu": float(mu), "se": float(np.sqrt(1 / np.sum(ws))), "tau2": float(tau2), "k": int(len(est)),
            "I2": float(max(0.0, (Q - (len(est) - 1)) / Q)) if Q > 0 else 0.0}


def main():
    ros = pl.read_parquet(SH / "roster.parquet").select(pl.col("agent").alias("id"), "name").to_dicts()
    detectable = set(mention_regexes(ros).keys())
    res = {}
    for g in C3_PERIODS:
        r = run(g, detectable)
        if r:
            res[gname(g)] = r
    pooled = {}
    for key in ("erased_F", "erased_V"):
        est = [v["beta"][key][0] for v in res.values() if "beta" in v and v["n_erased"].get("CF" if key == "erased_F" else "CV", 0) >= 50]
        se = [(v["beta"][key][2] - v["beta"][key][1]) / 3.92 for v in res.values() if "beta" in v and v["n_erased"].get("CF" if key == "erased_F" else "CV", 0) >= 50]
        pooled[key] = dl_meta(est, se)
    for key in ("rel_F", "rel_V"):
        est = [v[key][0] for v in res.values() if key in v]
        se = [(v[key][2] - v[key][1]) / 3.92 for v in res.values() if key in v]
        pooled[key] = dl_meta(est, se)
    jdump({"periods": res, "pooled": pooled}, OUT / "ne41_pooled.json")
    print("POOLED", pooled, flush=True)
    write_provenance("c3 (G<NN>/c3.json, ne41_pooled.json)", "hypotheses/H08-context-is-the-coupling/analysis/erasure.py",
                     ["G<NN>/turns.parquet (H08 scheme)", "chat_core", "exposure (membership)",
                      "H15 consolidations.parquet (CF/CV catalog)"],
                     {"B": B, "age_edges_min": AGE_EDGES, "window_min": 30, "ambiguous": "read-out turn == consolidation turn dropped"})


if __name__ == "__main__":
    main()
