"""H08 round 2, R4: does writing a sender's name into memory at a forced erasure protect the coupling to that sender?

  uv run python hypotheses/H08-context-is-the-coupling/analysis/r4_memory_dose.py synth     # synthetic guard first
  uv run python hypotheses/H08-context-is-the-coupling/analysis/r4_memory_dose.py real

Units: round 1b's NE41 units (`erasure_ledger.units`, same rules, re-derived here with the reset positions kept).
Dose z (card "Round 2", R4): j is an *added name* at the adjacent consolidation. For erased units the window runs from
the context assembly of the call before the first reset in (R, k] to the assembly of the last reset call <= k; for
non-erased units it is the next reset after k (placebo dose: same salience signal, cannot act on k). Added name = j is
named in a line new relative to the previous snapshot (scheme/build_memory_names.py) for some snapshot in the window,
and j is still named in the last snapshot of the window. z_stock = j named in the latest snapshot before k's assembly.
Model: round 1b's LPM with agent x day effects (CF, CV, new, PC, engaged, age bins) + z + CF*z + CV*z. Response y_auth
(primary) and y_men. Protection ratio pi = beta_CFz / (-beta_CF). Day bootstrap B = 200; DerSimonian-Laird pooling.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from h08lib import *  # noqa: E402,F403
from erasure import AGE_EDGES, C3_PERIODS, dl_meta  # noqa: E402

B = 200
OUT1B = OUT / "r1b"
OUT2 = OUT / "r2"
WIN_US = 30 * 60 * US
XN = ["CF", "CV", "new", "PC", "engaged", "age2", "age3", "age4", "age5", "z", "CFz", "CVz", "z_age2", "z_age3", "z_age4", "z_age5"]
# Amendment R4-A1 (2026-10-05, after the synthetic guard, before any real-data fit): z x age-bin terms (the dose's
# salience effect scales with the age-dependent base rate; without them CF x z is biased negative under every truth), and
# the protection ratio on the relative scale, pi_rel = 1 - (relative CF cut at z = 1) / (relative CF cut at z = 0), with
# the reference rates of non-erased old units by z re-weighted to the CF units' age distribution.
SYN_PERIODS = [38, 41, 51]


def memory_index():
    mn = pl.read_parquet(OUT2 / "memory_names.parquet")
    M = {}
    for (a,), sub in mn.group_by(["agent"], maintain_order=True):
        sub = sub.sort("t")
        M[int(a)] = (us(sub["t"]), sub["names_mask"].to_numpy().astype(np.uint64),
                     sub["added_mask"].fill_null(0).to_numpy().astype(np.uint64), sub["added_mask"].is_null().to_numpy())
    return M


def window_dose(M, a, t_lo, t_hi):
    """(added names in (S_before, S_after], names of S_after) or None when the window has no snapshot or a gap."""
    if a not in M:
        return None
    tm, nm, ad, nul = M[a]
    ib = np.searchsorted(tm, t_lo, "left") - 1     # latest snapshot strictly before t_lo
    ia = np.searchsorted(tm, t_hi, "right") - 1    # latest snapshot at or before t_hi
    if ia <= ib or ia < 0:
        return None
    sl = slice(ib + 1, ia + 1)
    if nul[sl].any():
        return None
    add = np.bitwise_or.reduce(ad[sl]) if ia > ib else np.uint64(0)
    return int(add) & int(nm[ia]), int(nm[ia])


def stock(M, a, t):
    if a not in M:
        return None
    tm, nm, _, _ = M[a]
    i = np.searchsorted(tm, t, "left") - 1
    return int(nm[i]) if i >= 0 else None


def units(g: int, M):
    tu = pl.read_parquet(OUT1B / gname(g) / "turns.parquet")
    if g == 36:
        tu = tu.filter(pl.col("pt_date") >= "2026-03-24")
    days = sorted(tu["pt_date"].unique().to_list())
    items = (pl.scan_parquet(SH / "context_ledger_items.parquet").filter(pl.col("turn_id").is_in(tu["turn_id"].implode()))
             .filter(pl.col("kind").cast(pl.Utf8) == "agent").select("turn_id", "message_id", "sender").collect())
    chat = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t"])
    items = items.join(chat, on="message_id", how="left").with_columns(pl.col("t").dt.epoch("us").alias("t_m"))
    rec_of = dict(zip(tu["turn_id"].to_list(), tu["agent"].to_list()))
    items = items.with_columns(pl.col("turn_id").replace_strict(rec_of, default=-1).alias("rcpt"))
    rows = []
    for (a, d), T in tu.group_by(["agent", "pt_date"], maintain_order=True):
        a = int(a)
        T = T.sort("s_us")
        tid = T["turn_id"].to_numpy(); s = T["s_us"].to_numpy()
        talk = T["talk"].fill_null(False).to_numpy() & T["msg"].is_not_null().to_numpy()
        ment = T["ment"].to_numpy().astype(np.uint64); pa = T["par_auth"].to_numpy().astype(np.uint64)
        rf = T["reset_forced"].fill_null(False).to_numpy(); rc = T["reset_consol"].fill_null(False).to_numpy()
        pos = {int(x): q for q, x in enumerate(tid)}
        I = items.filter((pl.col("rcpt") == a) & pl.col("turn_id").is_in(list(pos))).sort("t_m")
        if not I.height:
            continue
        it_t = I["t_m"].to_numpy(); it_s = I["sender"].to_numpy().astype(int)
        it_R = np.array([pos[int(x)] for x in I["turn_id"].to_numpy()])
        rmask = rf | rc
        rset = np.nonzero(rmask)[0]
        tk = np.nonzero(talk)[0]
        prev_talk = -1
        for k in tk:
            sk = s[k]
            sel = (it_R <= k) & (it_t >= sk - WIN_US) & (it_t < sk)
            if sel.any():
                last = {}
                for q in np.nonzero(sel)[0]:
                    last[it_s[q]] = (it_t[q], it_R[q])
                pc = bool(((s[rset] > sk - WIN_US) & (s[rset] <= sk)).any()) if len(rset) else False
                nxt = rset[rset > k]
                nxt = int(nxt[0]) if len(nxt) else -1
                st_k = stock(M, a, sk)
                dn = window_dose(M, a, s[nxt - 1], s[nxt]) if nxt > 0 else None
                for j, (tmj, R) in last.items():
                    if j == a or j < 0 or j > 63:
                        continue
                    new = R == k
                    kind = ""
                    dz = None
                    if R < k:
                        btw = np.arange(R + 1, k + 1)
                        rb = btw[rmask[btw]]
                        if len(rb):
                            kind = "CF" if rf[btw].any() else "CV"
                            dz = window_dose(M, a, s[rb[0] - 1], s[rb[-1]])
                    bit = 1 << j
                    eng_m = prev_talk >= 0 and bool((ment[prev_talk] >> np.uint64(j)) & np.uint64(1))
                    eng_a = prev_talk >= 0 and bool((pa[prev_talk] >> np.uint64(j)) & np.uint64(1))
                    y_m = bool((ment[k] >> np.uint64(j)) & np.uint64(1)); y_a = bool((pa[k] >> np.uint64(j)) & np.uint64(1))
                    if kind:
                        z = None if dz is None else bool(dz[0] & bit)
                    else:
                        z = None if dn is None else bool(dn[0] & bit)
                    zn = None if dn is None else bool(dn[0] & bit)       # next-consolidation dose for every unit
                    zs = None if st_k is None else bool(st_k & bit)
                    rows.append((a, d, int(k), int(j), y_m, y_a, bool(new), kind, pc, eng_m, eng_a,
                                 float((sk - tmj) / US / 60), z, zn, zs))
            prev_talk = k
    U = pl.DataFrame(rows, orient="row", schema={
        "agent": pl.Int16, "pt_date": pl.Utf8, "k": pl.Int64, "snd": pl.Int16, "y_men": pl.Boolean, "y_auth": pl.Boolean,
        "new": pl.Boolean, "kind": pl.Utf8, "PC": pl.Boolean, "eng_men": pl.Boolean, "eng_auth": pl.Boolean, "age": pl.Float64,
        "z": pl.Boolean, "z_next": pl.Boolean, "z_stock": pl.Boolean})
    return U, days


def design(U: pl.DataFrame, resp: str, zcol: str = "z"):
    age = U["age"].to_numpy()
    ab = np.digitize(age, AGE_EDGES[1:-1], right=True)
    kind = np.array(U["kind"].to_list())
    cf = (kind == "CF").astype(float); cv = (kind == "CV").astype(float)
    z = U[zcol].cast(pl.Float64).to_numpy()
    X = np.column_stack([cf, cv, U["new"].to_numpy(), U["PC"].to_numpy(), U[f"eng_{resp}"].to_numpy()]
                        + [(ab == b) for b in range(1, 5)] + [z, cf * z, cv * z] + [z * (ab == b) for b in range(1, 5)]).astype(float)
    return X


def fe_fit(X, y, U: pl.DataFrame, days, W):
    dix = {d: i for i, d in enumerate(days)}
    di = U["pt_date"].replace_strict(dix, return_dtype=pl.Int64).to_numpy()
    grp = U["agent"].cast(pl.Int64).to_numpy() * 10000 + di
    _, gi = np.unique(grp, return_inverse=True)
    cnt = np.bincount(gi).astype(float)
    Xd = X - (np.stack([np.bincount(gi, X[:, j]) for j in range(X.shape[1])], 1) / cnt[:, None])[gi]
    yd = y - (np.bincount(gi, y) / cnt)[gi]
    nd = len(days)
    XtX = np.zeros((nd, X.shape[1], X.shape[1])); Xty = np.zeros((nd, X.shape[1]))
    for dd in range(nd):
        m = di == dd
        XtX[dd] = Xd[m].T @ Xd[m]; Xty[dd] = Xd[m].T @ yd[m]
    A = np.einsum("bd,dij->bij", W, XtX) + 1e-9 * np.eye(X.shape[1])
    b = W @ Xty
    try:
        return np.linalg.solve(A, b[..., None])[..., 0]
    except np.linalg.LinAlgError:
        return np.full((W.shape[0], X.shape[1]), np.nan)


def boot_w(nd, seed):
    return np.vstack([np.ones((1, nd)), np.random.default_rng(seed).multinomial(nd, np.full(nd, 1 / nd), size=B)]).astype(float)


def rel_protection(V, days, W, bt, resp, zcol="z"):
    """pi_rel per bootstrap row: refs = non-erased old units' mean y by z, re-weighted to the CF age distribution."""
    dix = {d: i for i, d in enumerate(days)}
    di = V["pt_date"].replace_strict(dix, return_dtype=pl.Int64).to_numpy()
    ab = np.digitize(V["age"].to_numpy(), AGE_EDGES[1:-1], right=True)
    kind = np.array(V["kind"].to_list()); z = V[zcol].cast(pl.Float64).to_numpy(); y = V[f"y_{resp}"].cast(pl.Float64).to_numpy()
    kept = (kind == "") & ~V["new"].to_numpy()
    nd = len(days)
    S = np.zeros((2, 5, nd)); N = np.zeros((2, 5, nd)); C = np.zeros((5, nd))
    np.add.at(S, (z[kept].astype(int), ab[kept], di[kept]), y[kept]); np.add.at(N, (z[kept].astype(int), ab[kept], di[kept]), 1)
    cfm = kind == "CF"
    np.add.at(C, (ab[cfm], di[cfm]), 1)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.einsum("bd,zad->bza", W, S) / np.einsum("bd,zad->bza", W, N)
        wa = np.einsum("bd,ad->ba", W, C); wa = wa / wa.sum(1, keepdims=True)
        ref = np.nansum(r * wa[:, None, :], 2)
        c0 = bt[:, XN.index("CF")] / ref[:, 0]; c1 = (bt[:, XN.index("CF")] + bt[:, XN.index("CFz")]) / ref[:, 1]
        return 1 - c1 / c0, ref, c0, c1


def fit_period(U, days, W, resp, zcol="z"):
    V = U.filter(pl.col(zcol).is_not_null())
    X = design(V, resp, zcol); y = V[f"y_{resp}"].cast(pl.Float64).to_numpy()
    bt = fe_fit(X, y, V, days, W)
    out = {"n": V.height, "beta": {n: ci(bt[:, i]) for i, n in enumerate(XN)}}
    with np.errstate(divide="ignore", invalid="ignore"):
        out["pi_abs"] = ci(bt[:, XN.index("CFz")] / -bt[:, XN.index("CF")])
    pr, ref, c0, c1 = rel_protection(V, days, W, bt, resp, zcol)
    out["pi_rel"] = ci(pr); out["ref_kept_z0"] = ci(ref[:, 0]); out["ref_kept_z1"] = ci(ref[:, 1])
    out["rel_cut_z0"] = ci(c0); out["rel_cut_z1"] = ci(c1)
    ref_ = V.filter((pl.col("kind") == "") & ~pl.col("new"))[f"y_{resp}"].mean()
    out["ref_old_kept"] = float(ref_) if ref_ is not None else None
    return out, bt


def describe(U):
    d = {}
    for kind, lab in (("CF", "CF"), ("CV", "CV"), ("", "kept")):
        V = U.filter((pl.col("kind") == kind) & (~pl.col("new") if kind == "" else pl.lit(True)))
        Vz = V.filter(pl.col("z").is_not_null())
        d[lab] = {"n": V.height, "n_with_dose": Vz.height, "dose_rate": float(Vz["z"].mean()) if Vz.height else None,
                  "stock_rate": float(V.filter(pl.col("z_stock").is_not_null())["z_stock"].mean() or 0),
                  "y_auth_z1": float(Vz.filter(pl.col("z"))["y_auth"].mean() or 0) if Vz.height else None,
                  "y_auth_z0": float(Vz.filter(~pl.col("z"))["y_auth"].mean() or 0) if Vz.height else None}
    return d


def pool(res, key, resp):
    vv = [v[resp] for v in res.values() if resp in v and v["describe"]["CF"]["n_with_dose"] >= 50]
    est = [v["beta"][key][0] for v in vv]; se = [(v["beta"][key][2] - v["beta"][key][1]) / 3.92 for v in vv]
    return dl_meta(est, se)


def run_real():
    M = memory_index()
    res = {}
    for g in C3_PERIODS:
        if not (OUT1B / gname(g) / "turns.parquet").exists():
            continue
        U, days = units(g, M)
        W = boot_w(len(days), g)
        out = {"period": gname(g), "n_days": len(days), "n_units": U.height, "describe": describe(U)}
        for resp in ("auth", "men"):
            out[resp], _ = fit_period(U, days, W, resp)
        out["auth_stock"], _ = fit_period(U, days, W, "auth", "z_stock")
        od = OUT2 / gname(g); od.mkdir(parents=True, exist_ok=True)
        jdump(out, od / "r4_dose.json")
        res[gname(g)] = out
        b = out["auth"]["beta"]
        print(f"{gname(g)}: units {U.height}; CF dose rate {out['describe']['CF']['dose_rate']}; "
              f"auth CF {b['CF'][0]:+.4f} z {b['z'][0]:+.4f} [{b['z'][1]:+.4f},{b['z'][2]:+.4f}] CFz {b['CFz'][0]:+.4f} "
              f"[{b['CFz'][1]:+.4f},{b['CFz'][2]:+.4f}]", flush=True)
    pooled = {resp: {k: pool(res, k, resp) for k in ("CF", "CV", "z", "CFz", "CVz")} for resp in ("auth", "men", "auth_stock")}
    for resp in pooled:
        p = pooled[resp]
        if p["CF"] and p["CFz"]:
            p["pi_pooled"] = p["CFz"]["mu"] / -p["CF"]["mu"]
    jdump({"periods": res, "pooled": pooled}, OUT2 / "r4_pooled.json")
    for resp in ("auth", "men"):
        print("POOLED", resp, {k: (round(v["mu"], 4), round(v["se"], 4), v["k"]) if isinstance(v, dict) else v
                               for k, v in pooled[resp].items()})
    write_provenance("r2 R4 (r2/G<NN>/r4_dose.json, r2/r4_pooled.json)", "hypotheses/H08-context-is-the-coupling/analysis/r4_memory_dose.py",
                     ["r1b/G<NN>/turns.parquet", "context_ledger_items", "chat_core", "r2/memory_names.parquet"],
                     {"B": B, "age_edges_min": AGE_EDGES, "window_min": 30, "dose": "added name at the adjacent consolidation"},
                     folder=OUT2)


def run_synth(n_rep=50, periods=None, tag=""):
    M = memory_index()
    SYN = periods or SYN_PERIODS
    res = {}
    per = {}
    for g in SYN:
        U, days = units(g, M)
        V = U.filter(pl.col("z").is_not_null())
        ab = np.digitize(V["age"].to_numpy(), AGE_EDGES[1:-1], right=True)
        y0 = V["y_auth"].cast(pl.Float64).to_numpy()
        p0 = np.array([y0[ab == b].mean() for b in range(5)])[ab]
        cf = (np.array(V["kind"].to_list()) == "CF").astype(float)
        z = V["z"].cast(pl.Float64).to_numpy()
        X = design(V, "auth")
        per[gname(g)] = {"n": V.height, "n_CF": int(cf.sum()), "n_CF_z1": int((cf * z).sum()), "p0_mean": float(p0.mean())}
        for pi in (0.0, 0.5, 1.0):
            for r in range(n_rep):
                rng = np.random.default_rng(10000 * g + 100 * int(pi * 10) + r)
                p = np.clip(p0 * (1 + 0.5 * z) * (1 - 0.21 * cf * (1 - pi * z)), 0, 1)
                y = (rng.random(len(p)) < p).astype(float)
                Wb = boot_w(len(days), r)
                bt = fe_fit(X, y, V, days, Wb)
                est = ci(bt[:, XN.index("CFz")])
                Vy = V.with_columns(pl.Series("y_auth", y.astype(bool)))
                pr = ci(rel_protection(Vy, days, Wb, bt, "auth")[0])
                res.setdefault(pi, {}).setdefault(r, {})[gname(g)] = (est, pr)
    summary = {"periods": per, "truths": {}}
    for pi, reps in res.items():
        out = {}
        for idx, lab in ((0, "CFz"), (1, "pi_rel")):
            pos = {gn: float(np.mean([reps[r][gn][idx][1] > 0 for r in reps])) for gn in per}
            pooled_pos = []; pooled_mu = []
            for r in reps:
                est = [reps[r][gn][idx][0] for gn in per]; se = [(reps[r][gn][idx][2] - reps[r][gn][idx][1]) / 3.92 for gn in per]
                m = dl_meta(est, se)
                pooled_pos.append(m is not None and m["mu"] - 1.96 * m["se"] > 0); pooled_mu.append(m["mu"] if m else np.nan)
            med = {gn: float(np.nanmedian([reps[r][gn][idx][0] for r in reps])) for gn in per}
            out[lab] = {"per_period_CI_pos": pos, "pooled_CI_pos": float(np.mean(pooled_pos)), "median": med,
                        "pooled_median": float(np.nanmedian(pooled_mu))}
        summary["truths"][str(pi)] = out
        print("pi", pi, out, flush=True)
    jdump(summary | {"n_rep": n_rep, "model": "y ~ Bern(p0(age) (1 + 0.5 z)(1 - 0.21 CF (1 - pi z))) on real units"},
          OUT2 / f"r4_synthetic{tag}.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["synth", "real"])
    ap.add_argument("--reps", type=int, default=50)
    ap.add_argument("--all-periods", action="store_true", help="synthetic power on all nine NE41 skeletons (added after the guard)")
    a = ap.parse_args()
    if a.mode == "synth":
        run_synth(a.reps, C3_PERIODS if a.all_periods else None, "_all9" if a.all_periods else "")
    else:
        run_real()


if __name__ == "__main__":
    main()
