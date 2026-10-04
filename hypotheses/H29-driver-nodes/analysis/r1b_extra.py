"""H29 round 1b (2026-10-04): the reply-graph influence network, the reply-parent premium in content pull, and three
period-native tests (NE38 relay, #35 designated leaders, #26 elected leader). Predictions for the natives are dated
in their folders. Ledger-visibility units from scheme/build.py --data r1b.

  H29_DATA=r1b H29_EMB=bge_small uv run python hypotheses/H29-driver-nodes/analysis/r1b_extra.py
  (repeat with H29_EMB=gte_modernbert; outputs go to OUT/r1b[_gte]/r1b_extra.json)
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h29lib as L  # noqa: E402
from explore import COUNTED, DESCRIPTIVE  # noqa: E402

assert L.DATA_VERSION == "r1b", "run with H29_DATA=r1b"
SH = L.SH
B = 500
RG = pl.read_parquet(SH / "reply_graph.parquet").filter(pl.col("scale") == "day")
RP = None


def reply_pairs():
    global RP
    if RP is None:
        RP = (pl.read_parquet(SH / "reply_pairs.parquet", columns=["b_msg", "a_msg", "pair_set", "p_reply", "parent", "labelled",
                                                                   "a_agent", "b_agent", "a_kind", "pt_date", "holdout"])
              .filter((pl.col("pair_set") == "cand") & ~pl.col("holdout")))
    return RP


# ----------------------------------------------------------------------------- reply network

def reply_rates(U, agents, day_set=None, col="reply_hard"):
    days = U["meta"]["days"]
    dsel = days if day_set is None else [days[d] for d in sorted(day_set)]
    g = RG.filter(pl.col("pt_date").is_in(dsel) & pl.col("replier").is_in(agents) & pl.col("target").is_in(agents))
    pos = {a: i for i, a in enumerate(agents)}
    M = np.zeros((len(agents), len(agents)))
    for t, r, v in g.select("target", "replier", col).iter_rows():
        if t != r:
            M[pos[int(t)], pos[int(r)]] += float(v or 0)
    return M / max(L.active_hours(U, dsel), 1e-9)          # M[i, j]: replies by j to i's messages per active hour


def parent_premium(R, U):
    """Field-corrected pull of visible rows whose message is the recipient's reply parent (DQ2 `parent`) minus that of
    other visible rows, within matched time-to-reply bins (DT_BINS_ADJ); agent senders; day bootstrap."""
    T = U["turns"].select("talk_id", pl.col("msg").cast(pl.Int64).alias("b_msg"))
    par = reply_pairs().filter(pl.col("parent")).select(pl.col("b_msg").cast(pl.Int64), pl.col("a_msg").cast(pl.Int64)).with_columns(
        pl.lit(True).alias("is_parent"))
    Rv = (R.filter(pl.col("vis") & (pl.col("kind") == 0) & pl.col("yu_x").is_not_nan()).join(T, on="talk_id", how="left")
          .with_columns(pl.col("msg").cast(pl.Int64).alias("a_msg")).join(par, on=["b_msg", "a_msg"], how="left")
          .with_columns(pl.col("is_parent").fill_null(False)))
    bins = np.array(L.DT_BINS_ADJ)
    days = sorted(set(Rv["day_idx"].to_list()))
    dpos = {d: i for i, d in enumerate(days)}
    nb = len(bins) - 1
    S = np.zeros((len(days), 2, nb, 5))
    for v, flt in ((0, pl.col("is_parent")), (1, ~pl.col("is_parent"))):
        sub = Rv.filter(flt)
        if not sub.height:
            continue
        b = np.clip(np.searchsorted(bins, sub["dt_talk"].to_numpy(), side="right") - 1, 0, nb - 1)
        di = np.array([dpos[d] for d in sub["day_idx"].to_list()])
        for c, col in enumerate(("yu", "uu", "yu_x", "uu_x")):
            np.add.at(S[:, v, :, c], (di, b), sub[col].to_numpy())
        np.add.at(S[:, v, :, 4], (di, b), 1)

    def est(Tt):
        with np.errstate(invalid="ignore", divide="ignore"):
            pull = Tt[:, :, 0] / Tt[:, :, 1] - Tt[:, :, 2] / Tt[:, :, 3]
        n = Tt[:, :, 4]
        w = np.where((n[0] >= 5) & (n[1] >= 5), 2 * n[0] * n[1] / np.maximum(n[0] + n[1], 1), 0)
        ok = w > 0
        if not ok.any():
            return np.nan, np.nan, np.nan
        d = pull[0] - pull[1]
        return float((w[ok] * d[ok]).sum() / w[ok].sum()), float((w[ok] * pull[0][ok]).sum() / w[ok].sum()), \
            float((w[ok] * pull[1][ok]).sum() / w[ok].sum())
    tot = S.sum(0)
    prem, pp, pn = est(tot)
    rng = np.random.default_rng(L.SEED)
    bs = []
    if len(days) >= 2:
        for _ in range(B):
            wd = np.bincount(rng.integers(len(days), size=len(days)), minlength=len(days)).astype(float)
            bs.append(est((S * wd[:, None, None, None]).sum(0)))
    bs = np.array([x for x in bs if np.isfinite(x[0])])
    q = (lambda j: [float(np.percentile(bs[:, j], 2.5)), float(np.percentile(bs[:, j], 97.5))] if len(bs) else None)
    return dict(premium=prem, premium_ci=q(0), pull_parent=pp, pull_parent_ci=q(1), pull_other=pn, pull_other_ci=q(2),
                n_parent=int(tot[0, :, 4].sum()), n_other=int(tot[1, :, 4].sum()))


def reply_network_unit(name):
    t0 = time.time()
    emb = L.Emb()
    U = L.attach_vectors(L.load_unit(name), emb)
    R = L.add_timing(U, L.row_stats(U))
    agents = L.network_agents(U)
    days = U["meta"]["days"]
    nd = len(days)
    even = {d for d in range(nd) if d % 2 == 0}
    odd = set(range(nd)) - even
    res = dict(unit=name, n_days=nd, n_agents=len(agents))
    res["parent"] = parent_premium(R, U)
    c = res["parent"]["pull_parent"]
    c = max(c, 0.01) if np.isfinite(c) else 0.01
    g = L.gamma_unit(U)["gamma"]

    def fit(ds):
        r = reply_rates(U, agents, ds)
        A = c * r
        sc = L.gramian_scores(L.build_Q(A, g))
        return dict(D=sc["D"], inrate=r.sum(1), out=A.sum(1), net=A.sum(1) - A.sum(0),
                    vol=L.message_rates(U, agents, ds))
    F = fit(None)
    res["rho_D_inrate"] = L.spearman(F["D"], F["inrate"])
    res["rho_D_vol"] = L.spearman(F["D"], F["vol"])
    if even and odd:
        Fe, Fo = fit(even), fit(odd)
        res["split_half"] = {k: L.spearman(Fe[k], Fo[k]) for k in ("D", "inrate", "vol")}
        dmap = {d: i for i, d in enumerate(days)}
        am = U["msgs"].filter(pl.col("kind") == 0).with_columns(pl.col("pt_date").replace_strict(dmap, default=None,
                                                                                                 return_dtype=pl.Int16).alias("day_idx"))
        am = am.filter(pl.col("day_idx").is_not_null())
        hs = L.horizon_spread(U, am)
        folds = []
        for train, test, Ftr in ((even, odd, Fe), (odd, even, Fo)):
            H = L.hourly_spread(hs, agents, L.active_hours(U, [days[d] for d in test]), day_set=test)
            folds.append(dict(V2_Drep=L.spearman(Ftr["D"], H), V2_inrate=L.spearman(Ftr["inrate"], H), V2_vol=L.spearman(Ftr["vol"], H)))
        res["V"] = {k: float(np.nanmean([f[k] for f in folds])) for k in folds[0]}
    res["secs"] = time.time() - t0
    return res


# ----------------------------------------------------------------------------- natives

def statements_by_agent(U, X):
    m = U["msgs"].filter(pl.col("kind") == 0).sort("t_us")
    out = {}
    for (a,), g in m.group_by(["sender"], maintain_order=True):
        idx = L.vec_index(U, g["msg"].to_numpy())
        out[int(a)] = (g["t_us"].to_numpy(), X[idx])
    return out


def displacement(st, a, t0, u, H_us=2 * 3600 * 1e6):
    if a not in st:
        return np.nan
    ts, V = st[a]
    i = np.searchsorted(ts, t0, "left") - 1
    j0, j1 = np.searchsorted(ts, t0, "right"), np.searchsorted(ts, t0 + H_us, "right")
    if i < 0 or j1 <= j0 or not np.isfinite(V[i]).all():
        return np.nan
    after = V[j0:j1]
    after = after[np.isfinite(after).all(1)]
    if not len(after):
        return np.nan
    return float((after.mean(0) - V[i]) @ u)


def native_ne38(emb):
    """Opus 5 reassignment (2026-07-29 16:50:01 UTC): target pull and bystander spread vs every other named human
    message in G51b-d (pseudo-true pool)."""
    items = (pl.scan_parquet(SH / "context_ledger_items.parquet").filter(pl.col("kind") == "human").select("turn_id", "message_id").collect()
             .join(pl.read_parquet(SH / "call_windows.parquet", columns=["turn_id", "agent", "t_call", "holdout"]).filter(~pl.col("holdout")),
                   on="turn_id", how="inner"))
    chat = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id"]).with_row_index("msg")
    items = items.join(chat.with_columns(pl.col("msg").cast(pl.Int64)), on="message_id", how="left")
    rc = {(int(m), int(a)): t for m, a, t in items.select("msg", "agent", pl.col("t_call").dt.epoch("us")).iter_rows()}
    rows = []
    star = None
    for name in ("G51b", "G51c", "G51d"):
        U = L.attach_vectors(L.load_unit(name), emb)
        X = U["X"]
        st = statements_by_agent(U, X)
        hm = U["msgs"].filter((pl.col("kind") == 1) & (pl.col("mentions").list.len() > 0))
        present = {d: set(U["turns"].filter(pl.col("pt_date") == d)["agent"].to_list()) for d in U["meta"]["days"]}
        for m, t, d, men in hm.select("msg", "t_us", "pt_date", "mentions").iter_rows():
            u = X[L.vec_index(U, [m])][0]
            if not np.isfinite(u).all():
                continue
            tgt = [int(x) for x in men]
            T = [displacement(st, a, rc.get((int(m), a), t), u) for a in tgt]
            T = [x for x in T if np.isfinite(x)]
            by = [displacement(st, a, rc.get((int(m), a), t), u) for a in present.get(d, set()) if a not in tgt]
            by = [x for x in by if np.isfinite(x)]
            row = dict(unit=name, msg=int(m), t_us=int(t), T=float(np.mean(T)) if T else np.nan,
                       S=float(np.mean(by)) if by else np.nan, n_by=len(by), targets=tgt)
            rows.append(row)
            if 40 in tgt and d == "2026-07-29" and abs(t - 1785343801718572) < 5e6:
                star = row
    df = pl.DataFrame([{k: v for k, v in r.items() if k != "targets"} for r in rows])
    if star is None:   # fall back: the 07-29 human message naming agent 40
        cand = [r for r in rows if 40 in r["targets"] and r["unit"] == "G51b"]
        star = min(cand, key=lambda r: abs(r["t_us"] - 1785343801718572)) if cand else None
    pool = df.filter(pl.col("msg") != (star["msg"] if star else -1))
    Tp = pool["T"].drop_nans().to_numpy()
    Sp = pool["S"].drop_nans().to_numpy()
    out = dict(n_pool=int(pool.height), n_pool_T=int(len(Tp)), n_pool_S=int(len(Sp)), star=star)
    if star:
        out["T_pct"] = float((Tp < star["T"]).mean() * 100) if np.isfinite(star["T"]) else None
        out["S_pct"] = float((Sp < star["S"]).mean() * 100) if np.isfinite(star["S"]) else None
        out["pool_T_median"] = float(np.median(Tp)) if len(Tp) else None
        out["pool_S_median"] = float(np.median(Sp)) if len(Sp) else None
        out["pool_S_p05_p95"] = [float(np.percentile(Sp, 5)), float(np.percentile(Sp, 95))] if len(Sp) else None
    return out


def leader_stats(name, regime, leader_days: dict, pre_post=None):
    """Per (sender, day or phase): R reply attention per message, P_u broadcast pull per message (unnamed recipients),
    P_n named pull, Vol; ledger rows."""
    emb = L.Emb(regime=regime)
    U = L.attach_vectors(L.load_unit(name), emb)
    R = L.add_timing(U, L.row_stats(U))
    msgs = U["msgs"].filter(pl.col("kind") == 0)
    days = U["meta"]["days"]
    rp = reply_pairs().filter(pl.col("pt_date").is_in(days) & pl.col("labelled") & (pl.col("a_kind") == 0)
                              & (pl.col("a_agent") != pl.col("b_agent")))
    tm = dict(zip(msgs["msg"].to_list(), msgs["t_us"].to_list()))
    if pre_post is None:
        key_msg = lambda m, d: d                                            # noqa: E731
    else:
        key_msg = lambda m, d: "post" if tm.get(m, 0) >= pre_post else "pre"   # noqa: E731
    msgs = msgs.with_columns(pl.struct("msg", "pt_date").map_elements(lambda s: key_msg(s["msg"], s["pt_date"]),
                                                                       return_dtype=pl.Utf8).alias("key"))
    kmap = dict(zip(msgs["msg"].to_list(), msgs["key"].to_list()))
    nmsg = msgs.group_by("sender", "key").len()
    rep = (rp.with_columns(pl.col("a_msg").cast(pl.Int64).replace_strict(kmap, default=None).alias("key"))
           .filter(pl.col("key").is_not_null()).group_by(pl.col("a_agent").cast(pl.Int16).alias("sender"), "key")
           .agg(pl.col("p_reply").fill_null(0).sum().alias("rep")))
    Rv = R.filter(pl.col("vis") & (pl.col("kind") == 0) & pl.col("yu_x").is_not_nan()).with_columns(
        pl.col("msg").cast(pl.Int64).replace_strict(kmap, default=None).alias("key")).filter(pl.col("key").is_not_null())
    agg = Rv.group_by("sender", "key", "ment_j").agg(pl.col("yu").sum(), pl.col("uu").sum(), pl.col("yu_x").sum(),
                                                       pl.col("uu_x").sum(), pl.len().alias("n"))
    hours = {d: L.active_hours(U, [d]) for d in days}
    tab = {}
    for s, k, n in nmsg.iter_rows():
        tab[(int(s), k)] = dict(n_msg=n, rep=0.0)
    for s, k, r_ in rep.iter_rows():
        if (int(s), k) in tab:
            tab[(int(s), k)]["rep"] = float(r_)
    for s, k, mj, yu, uu, yx, ux, n in agg.iter_rows():
        if (int(s), k) not in tab:
            continue
        tab[(int(s), k)]["P_n" if mj else "P_u"] = (yu / uu - yx / ux) if uu > 0 and ux > 0 else np.nan
        tab[(int(s), k)]["n_" + ("named" if mj else "unnamed")] = n
        tab[(int(s), k)]["sums_" + ("n" if mj else "u")] = [yu, uu, yx, ux]
    for (s, k), v in tab.items():
        v["R"] = v["rep"] / max(v["n_msg"], 1)
        v["vol"] = v["n_msg"] / max(hours.get(k, sum(hours.values()) if pre_post is None else 1.0), 1e-9) if pre_post is None else v["n_msg"]
    return tab, hours


def native_g35():
    leaders = {"2026-03-16": [18, 23], "2026-03-17": [19, 20], "2026-03-18": [6, 22]}
    tab, hours = leader_stats("G35", "II", leaders)
    rows = []
    for d, ags in leaders.items():
        for a in ags:
            own = [k for (s, k) in tab if s == a]
            other = [k for k in own if k != d]
            if d not in own or not other:
                continue
            L_ = tab[(a, d)]
            O = [tab[(a, k)] for k in other]

            def pooled_pull(lst, key):
                sums = np.sum([x.get(key, [0, 0, 0, 0]) for x in lst], 0)
                return (sums[0] / sums[1] - sums[2] / sums[3]) if sums[1] > 0 and sums[3] > 0 else np.nan
            rows.append(dict(agent=a, day=d, R_lead=L_["R"], R_other=float(np.mean([o["R"] for o in O])),
                             vol_lead=L_["vol"], vol_other=float(np.mean([o["vol"] for o in O])),
                             Pu_lead=pooled_pull([L_], "sums_u"), Pu_other=pooled_pull(O, "sums_u"),
                             Pn_lead=pooled_pull([L_], "sums_n"), Pn_other=pooled_pull(O, "sums_n"),
                             n_u_lead=L_.get("n_unnamed", 0), n_n_lead=L_.get("n_named", 0)))
    df = pl.DataFrame(rows)
    rng = np.random.default_rng(L.SEED)

    def boot(f):
        vals = []
        for _ in range(2000):
            idx = rng.integers(0, df.height, df.height)
            vals.append(f(df[idx.tolist()]))
        vals = np.array([v for v in vals if np.isfinite(v)])
        return [float(f(df)), float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))] if len(vals) else [float(f(df)), None, None]
    lr = lambda a, b: (lambda d: float(np.exp(np.mean(np.log(np.maximum(d[a].to_numpy(), 1e-9) / np.maximum(d[b].to_numpy(), 1e-9))))))  # noqa: E731
    out = dict(rows=rows, R_ratio=boot(lr("R_lead", "R_other")), vol_ratio=boot(lr("vol_lead", "vol_other")),
               Pu_diff=boot(lambda d: float(np.nanmean(d["Pu_lead"].to_numpy() - d["Pu_other"].to_numpy()))),
               Pu_ratio=boot(lambda d: float(np.nanmean(d["Pu_lead"].to_numpy()) / np.nanmean(d["Pu_other"].to_numpy()))),
               Pn_diff=boot(lambda d: float(np.nanmean(d["Pn_lead"].to_numpy() - d["Pn_other"].to_numpy()))))
    return out


def native_g26():
    t_res = 1767641722589746      # 2026-01-05 19:35:22.589746 UTC (DQ6 'result')
    tab, _ = leader_stats("G26", "I", {}, pre_post=t_res)
    agents = sorted({s for s, k in tab})
    def lr(a, key):
        pre, post = tab.get((a, "pre")), tab.get((a, "post"))
        if not pre or not post:
            return np.nan
        if key in ("R",):
            return float(np.log(max(post["R"], 1e-6) / max(pre["R"], 1e-6)))
        su, sp = pre.get("sums_u"), post.get("sums_u")
        if su is None or sp is None:
            return np.nan
        f = lambda s: s[0] / s[1] - s[2] / s[3]   # noqa: E731
        return float(f(sp) - f(su))
    res = {}
    for key in ("R", "Pu"):
        vals = {a: lr(a, key) for a in agents}
        others = np.array([v for a, v in vals.items() if a != 17 and np.isfinite(v)])
        v17 = vals.get(17, np.nan)
        res[key] = dict(leader=v17, others_median=float(np.median(others)) if len(others) else None,
                        did=float(v17 - np.median(others)) if len(others) and np.isfinite(v17) else None,
                        leader_rank_pct=float((others < v17).mean() * 100) if len(others) and np.isfinite(v17) else None,
                        n_others=int(len(others)), others=[float(x) for x in others])
    res["leader_pre"] = {k: tab.get((17, "pre"), {}).get(k) for k in ("n_msg", "R", "P_u", "P_n", "n_unnamed")}
    res["leader_post"] = {k: tab.get((17, "post"), {}).get(k) for k in ("n_msg", "R", "P_u", "P_n", "n_unnamed")}
    return res


def main():
    t0 = time.time()
    out = {"embedding": L.EMB_MODEL, "units": {}}
    for name in COUNTED + DESCRIPTIVE:
        r = reply_network_unit(name)
        out["units"][name] = r
        print(name, "parent premium", round(r["parent"]["premium"], 4), r["parent"]["premium_ci"], "| split", r.get("split_half"),
              "| V", r.get("V"), f"({time.time() - t0:.0f}s)", flush=True)
    emb = L.Emb()
    out["NE38"] = native_ne38(emb)
    print("NE38", {k: v for k, v in out["NE38"].items() if k != "star"}, out["NE38"].get("star"), flush=True)
    out["G35"] = native_g35()
    print("G35", {k: v for k, v in out["G35"].items() if k != "rows"}, flush=True)
    out["G26"] = native_g26()
    print("G26", out["G26"], flush=True)
    L.jdump(out, L.OUT / "r1b_extra.json")
    print(f"done {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
