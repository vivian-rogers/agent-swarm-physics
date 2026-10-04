"""H46 period-native tests (layer 2): G51 personas + NE38, G12 debates, G44 distilled leader.

Outputs: data/processed/H46-style-conserved-charge/{G51,G12,G44}/native.json
"""
from __future__ import annotations
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h46lib as L  # noqa: E402

CH = ("style", "style_raw", "content")


def mats_for(m: pl.DataFrame) -> dict:
    return {"style": L.style_matrix(m, "tc"), "style_raw": L.style_matrix(m, "raw"), "content": L.content_matrix(m, "resid")}


def set_stats(X: np.ndarray):
    n = len(X)
    mu = X.mean(0)
    v = X.var(0, ddof=1).sum() / n if n > 1 else np.nan
    return mu, v


def d_unb(a, b):
    return float(((a[0] - b[0]) ** 2).sum() - a[1] - b[1])


def pct(Db, Dp):
    Dp = np.asarray(Dp)
    return float(((Dp < Db).sum() + 0.5 * (Dp == Db).sum()) / len(Dp)) if len(Dp) else np.nan


# ---------------------------------------------------------------------------------------------------- G51
def g51(m: pl.DataFrame) -> dict:
    gt = pl.read_parquet(L.SH / "ground_truth_labels.parquet").filter(pl.col("preferred") & ~pl.col("holdout"))
    roles = gt.filter((pl.col("label_kind") == "role") & pl.col("value").is_not_null())
    rclass = gt.filter(pl.col("label_kind") == "role_class")
    m3 = m.filter((pl.col("regime") == "III") & ((pl.col("goal_no").is_between(36, 44)) | (pl.col("goal_no") == 51)))
    M = mats_for(m3)
    dt_ = L.day_table(m3, M)
    k = dt_.keys
    ag_msgs = m3.with_row_index("i")
    res = {"agents": {}}
    # message index per (agent, day) for block pooling
    day_ix = {(a, d): g["i"].to_numpy() for (a, d), g in ag_msgs.group_by(["agent", "pt_date"])}
    elig = {(r["agent"], r["pt_date"]) for r in k.iter_rows(named=True)}

    def block(a, days):
        ix = np.concatenate([day_ix[(a, d)] for d in days])
        return {c: set_stats(M[c][ix]) for c in CH}

    incumbents = []
    for a in sorted(k["agent"].unique().to_list()):
        days = sorted(d for (x, d) in elig if x == a)
        pre = [d for d in days if d < "2026-06-01"]
        post = [d for d in days if "2026-07-06" <= d <= "2026-07-08"]
        if len(pre) >= 1 and len(post) >= 1:
            incumbents.append(a)
    for a in incumbents:
        days = sorted(d for (x, d) in elig if x == a)
        pre = [d for d in days if d < "2026-06-01"][-3:]
        post = [d for d in days if "2026-07-06" <= d <= "2026-07-08"][:3]
        Bb = (block(a, pre), block(a, post))
        # placebo blocks: first <= 3 eligible days of each ISO week, both blocks pre-#45 or both in #51
        weeks: dict = {}
        for d in days:
            wk = dt.date.fromisoformat(d).isocalendar()[:2]
            weeks.setdefault(wk, []).append(d)
        wl = [(wk, ds[:3]) for wk, ds in sorted(weeks.items())]
        Dp = {c: [] for c in CH}
        Dp_side = {c: {"pre45": [], "in51": []} for c in CH}
        cache = {}
        for x in range(len(wl)):
            for y in range(x + 1, len(wl)):
                d1, d2 = wl[x][1], wl[y][1]
                gap = (dt.date.fromisoformat(d2[0]) - dt.date.fromisoformat(d1[-1])).days
                side = "pre45" if d2[-1] < "2026-06-01" else ("in51" if d1[0] >= "2026-07-06" else None)
                if gap < 21 or side is None:
                    continue
                if (x not in cache):
                    cache[x] = block(a, d1)
                if (y not in cache):
                    cache[y] = block(a, d2)
                for c in CH:
                    v = d_unb(cache[x][c], cache[y][c])
                    Dp[c].append(v)
                    Dp_side[c][side].append(v)
        if len(Dp["style"]) < 4:
            continue
        role = roles.filter((pl.col("agent") == a) & (pl.col("t_valid_from") <= dt.datetime(2026, 7, 8, 23, tzinfo=dt.UTC)))
        rname = role["value"][0] if role.height else None
        rc = rclass.filter(pl.col("agent") == a)
        grp = "prankster" if rname == "prankster" else ("media" if rc.height and rc["value"][0] == "media" else "other")
        r = {"role": rname, "group": grp, "n_placebo": len(Dp["style"]), "pre_days": pre, "post_days": post}
        for c in CH:
            Db = d_unb(Bb[0][c], Bb[1][c])
            r[f"pct_{c}"] = pct(Db, Dp[c])
            r[f"pct_{c}_pre45"] = pct(Db, Dp_side[c]["pre45"])
            r[f"pct_{c}_in51"] = pct(Db, Dp_side[c]["in51"])
            r[f"ratio_{c}"] = float(Db / np.median(Dp[c])) if np.median(Dp[c]) > 0 else np.nan
        res["agents"][int(a)] = r
    A = res["agents"]
    for c in CH:
        vals = {g: [v[f"pct_{c}"] for v in A.values() if v["group"] == g] for g in ("prankster", "media", "other")}
        allv = [v[f"pct_{c}"] for v in A.values()]
        res[f"summary_{c}"] = {"mean_all": float(np.mean(allv)), "n": len(allv),
                               "share_ge_0.9": float(np.mean(np.array(allv) >= 0.9)),
                               "prankster": vals["prankster"], "media": vals["media"],
                               "other_mean": float(np.mean(vals["other"])) if vals["other"] else None,
                               "media_vs_other_MW_p": float(stats.mannwhitneyu(vals["media"], vals["other"], alternative="greater").pvalue)
                               if vals["media"] and vals["other"] else None,
                               "p_rand_mean_gt_half": rand_p(allv, [v["n_placebo"] for v in A.values()])}
    # NE38: agent 40, 07-29
    res["NE38"] = ne38(m)
    return res


def rand_p(x, npl, n=20000, seed=0):
    rng = np.random.default_rng(seed)
    npl = np.asarray(npl)
    sims = (rng.integers(0, npl[None, :] + 1, size=(n, len(npl))) / npl[None, :]).mean(1)
    return float((1 + (sims >= np.mean(x)).sum()) / (1 + n))


def ne38(m: pl.DataFrame) -> dict:
    a = 40
    ma = m.filter((pl.col("agent") == a) & (pl.col("goal_no") == 51))
    M = mats_for(ma)
    dt_ = L.day_table(ma, M)
    k = dt_.keys.sort("pt_date")
    days = k["pt_date"].to_list()
    rows = k["row"].to_numpy()
    units = k["unit2"].to_list()
    sw = "2026-07-29"
    pre = [i for i, d in enumerate(days) if d < sw]
    post = [i for i, d in enumerate(days) if d >= sw]
    out = {"n_pre_days": len(pre), "n_post_days": len(post)}
    if not pre or not post:
        return out
    ib, jb = rows[pre[-1]], rows[post[0]]
    pairs = [(rows[i], rows[i + 1]) for i in range(len(days) - 1)
             if units[i] == units[i + 1] and not (days[i] < sw <= days[i + 1])]
    pi = np.array([p[0] for p in pairs])
    pj = np.array([p[1] for p in pairs])
    for c in CH:
        Db = L.D_unb(dt_, c, np.array([ib]), np.array([jb]))[0]
        Dp = L.D_unb(dt_, c, pi, pj)
        out[f"day_pct_{c}"] = pct(Db, Dp)
        out[f"day_ratio_{c}"] = float(Db / np.median(Dp)) if np.median(Dp) > 0 else np.nan
    out["n_placebo_day"] = len(pairs)
    # 3-day blocks (message pooled): pre = last 3 before, post = first 3 from 07-29; placebo = sliding 3|3 splits
    mi = ma.with_row_index("i")
    dix = {d: g["i"].to_numpy() for (d,), g in mi.group_by(["pt_date"])}

    def blk(ds):
        ix = np.concatenate([dix[d] for d in ds])
        return {c: set_stats(M[c][ix]) for c in CH}
    bpre, bpost = blk([days[i] for i in pre[-3:]]), blk([days[i] for i in post[:3]])
    plc = {c: [] for c in CH}
    for s in range(len(days) - 5):
        d6 = days[s:s + 6]
        if d6[2] < sw <= d6[3] or any(x < sw <= y for x, y in zip(d6[:-1], d6[1:])):
            continue
        b1, b2 = blk(d6[:3]), blk(d6[3:])
        for c in CH:
            plc[c].append(d_unb(b1[c], b2[c]))
    for c in CH:
        out[f"block_pct_{c}"] = pct(d_unb(bpre[c], bpost[c]), plc[c])
    out["n_placebo_block"] = len(plc["style"])
    return out


# ---------------------------------------------------------------------------------------------------- G12
def g12(m: pl.DataFrame) -> dict:
    gt = pl.read_parquet(L.SH / "ground_truth_labels.parquet").filter(pl.col("preferred") & ~pl.col("holdout")
                                                                       & (pl.col("goal_no") == 12))
    win = (gt.filter(pl.col("label_kind").is_in(["team", "judge"])).group_by("unit")
           .agg(pl.col("t_valid_from").min().alias("t0"), pl.col("t_valid_to").max().alias("t1")).sort("t0"))
    lab = gt.filter(pl.col("label_kind").is_in(["team", "judge"])).select(
        "unit", "agent", pl.when(pl.col("label_kind") == "judge").then(pl.lit("judge")).otherwise(pl.col("value")).alias("side"))
    m12 = m.filter(pl.col("goal_no") == 12)
    M = mats_for(m12)
    t = m12["t"].to_list()
    ag = m12["agent"].to_numpy()
    tt = np.array([x.timestamp() for x in t])
    sets = []   # (debate index, agent, side, idx array)
    for di, r in enumerate(win.iter_rows(named=True)):
        msk = (tt >= r["t0"].timestamp()) & (tt <= r["t1"].timestamp())
        for a in np.unique(ag[msk]):
            ix = np.where(msk & (ag == a))[0]
            s = lab.filter((pl.col("unit") == r["unit"]) & (pl.col("agent") == a))
            side = s["side"][0] if s.height else "none"
            sets.append((di, int(a), side, ix))
    out = {"n_sets": len(sets), "sets_per_agent": {}}
    for _, a, _, _ in sets:
        out["sets_per_agent"][a] = out["sets_per_agent"].get(a, 0) + 1
    S3 = [s for s in sets if len(s[3]) >= 3]
    out["n_sets_ge3"] = len(S3)
    # (a) fingerprint: debates 0-4 -> 5-9, debate-demeaned set means
    for c in CH:
        mu = {(d, a): M[c][ix].mean(0) for d, a, _, ix in S3}
        dm = {}
        for d in range(10):
            keys = [key for key in mu if key[0] == d]
            if keys:
                cen = np.mean([mu[key] for key in keys], 0)
                for key in keys:
                    dm[key] = mu[key] - cen
        tr = [(key, v) for key, v in dm.items() if key[0] < 5]
        te = [(key, v) for key, v in dm.items() if key[0] >= 5]
        common = {key[1] for key, _ in tr} & {key[1] for key, _ in te}
        tr = [(key, v) for key, v in tr if key[1] in common]
        te = [(key, v) for key, v in te if key[1] in common]
        yhat = L.nc_classify(np.stack([v for _, v in tr]), np.array([key[1] for key, _ in tr]), np.stack([v for _, v in te]))
        y = np.array([key[1] for key, _ in te])
        out[f"fp_{c}"] = {"acc": L.balanced_acc(y, yhat), "chance": 1 / len(common), "n_agents": len(common),
                          "n_test": len(te)}
    # (b) debate switch vs within-debate split halves
    for c in CH:
        rs, nps = [], []
        for a in sorted({s[1] for s in S3}):
            sa = sorted([s for s in S3 if s[1] == a], key=lambda s: s[0])
            halves = []
            for s in sa:
                ix = s[3]
                if len(ix) >= 6:
                    h = len(ix) // 2
                    halves.append(d_unb(set_stats(M[c][ix[:h]]), set_stats(M[c][ix[h:]])))
            if len(halves) < 3:
                continue
            for s1, s2 in zip(sa[:-1], sa[1:]):
                Db = d_unb(set_stats(M[c][s1[3]]), set_stats(M[c][s2[3]]))
                rs.append(pct(Db, halves))
                nps.append(len(halves))
        out[f"switch_{c}"] = {"T": float(np.mean(rs)) if rs else None, "n": len(rs),
                              "p_rand": rand_p(rs, nps) if rs else None}
    # (c) assigned role: agent 9 judge vs debater, leave-one-debate-out nearest centroid
    s9 = [s for s in S3 if s[1] == 9 and s[2] != "none"]
    for c in CH:
        X = np.stack([M[c][s[3]].mean(0) for s in s9])
        y = np.array([s[2] == "judge" for s in s9])
        def loo_acc(yy):
            hits = []
            for q in range(len(yy)):
                msk = np.arange(len(yy)) != q
                if yy[msk].all() or (~yy[msk]).all():
                    continue
                cj, cd = X[msk & yy].mean(0), X[msk & ~yy].mean(0)
                sd = X[msk].std(0, ddof=1)
                sd = np.where(sd > 1e-9, sd, 1)
                pj = (((X[q] - cj) / sd) ** 2).sum() < (((X[q] - cd) / sd) ** 2).sum()
                hits.append(pj == yy[q])
            return float(np.mean(hits))
        acc = loo_acc(y)
        rng = np.random.default_rng(0)
        null = np.array([loo_acc(rng.permutation(y)) for _ in range(2000)])
        out[f"role9_{c}"] = {"acc": acc, "n_sets": int(len(y)), "n_judge": int(y.sum()),
                             "p_perm": float((1 + (null >= acc).sum()) / 2001)}
    # one-time judges: judge-window distance to own debater centroid vs leave-one-out debater distances
    for c in CH:
        res_j = {}
        for a in sorted({s[1] for s in S3 if s[2] == "judge" and s[1] != 9}):
            sa = [s for s in S3 if s[1] == a]
            J = [s for s in sa if s[2] == "judge"]
            Dd = [s for s in sa if s[2] in ("gov", "opp")]
            if not J or len(Dd) < 3:
                continue
            Xd = np.stack([M[c][s[3]].mean(0) for s in Dd])
            dj = float(((M[c][J[0][3]].mean(0) - Xd.mean(0)) ** 2).sum())
            loo = [float(((Xd[q] - np.delete(Xd, q, 0).mean(0)) ** 2).sum()) for q in range(len(Xd))]
            res_j[a] = {"pct": pct(dj, loo), "n_debater_sets": len(Dd)}
        out[f"onetime_judges_{c}"] = res_j
    # (d) assigned side: within-agent permutation of gov/opp on pairwise set distances
    for c in CH:
        stat, null_stats = 0.0, np.zeros(2000)
        rng = np.random.default_rng(1)
        for a in sorted({s[1] for s in S3}):
            sa = [s for s in S3 if s[1] == a and s[2] in ("gov", "opp")]
            if len(sa) < 4 or len({s[2] for s in sa}) < 2:
                continue
            X = np.stack([M[c][s[3]].mean(0) for s in sa])
            side = np.array([s[2] == "gov" for s in sa])
            Dm = ((X[:, None] - X[None]) ** 2).sum(2)
            iu = np.triu_indices(len(sa), 1)

            def f(sd):
                diff = sd[iu[0]] != sd[iu[1]]
                return Dm[iu][diff].mean() - Dm[iu][~diff].mean() if diff.any() and (~diff).any() else 0.0
            stat += f(side)
            null_stats += np.array([f(rng.permutation(side)) for _ in range(2000)])
        out[f"side_{c}"] = {"stat": float(stat), "p_perm": float((1 + (null_stats >= stat).sum()) / 2001)}
    return out


# ---------------------------------------------------------------------------------------------------- G44
def g44() -> dict:
    allm = pl.read_parquet(L.DATA / "messages.parquet").filter(~pl.col("self_repeat"))
    ref = allm.filter(pl.col("main") & (pl.col("regime") == "III") & pl.col("goal_no").is_between(38, 44))
    led = allm.filter(pl.col("agent") == 28).sort("t")
    final_t = dt.datetime(2026, 5, 29, 18, 24, 51, tzinfo=dt.UTC)
    out = {"n_leader_msgs": led.height, "n_leader_final": int((led["t"] >= final_t).sum())}
    roster = pl.read_parquet(L.SH / "roster.parquet")
    names = dict(zip(roster["agent"].to_list(), roster["name"].to_list()))
    for c, fn in (("style", lambda d: L.style_matrix(d, "tc")), ("style_raw", lambda d: L.style_matrix(d, "raw")),
                  ("content", lambda d: L.content_matrix(d, "resid"))):
        Xr, Xl = fn(ref), fn(led)
        ar = ref["agent"].to_numpy()
        agents = np.unique(ar)
        C = np.stack([Xr[ar == a].mean(0) for a in agents])
        # diagonal scale: pooled within-agent SD of agent-day means
        keyd = (ref["agent"].cast(pl.Utf8) + "|" + ref["pt_date"]).to_numpy()
        ud, inv = np.unique(keyd, return_inverse=True)
        S = np.zeros((len(ud), Xr.shape[1]))
        np.add.at(S, inv, Xr)
        dm = S / np.bincount(inv)[:, None]
        dag = np.array([int(u.split("|")[0]) for u in ud])
        res = dm - C[np.searchsorted(agents, dag)]
        sd = res.std(0, ddof=1)
        sd = np.where(sd > 1e-9, sd, 1)

        def ranks(x):
            d = (((x - C) / sd) ** 2).sum(1)
            return agents[np.argsort(d)], d
        r = {}
        for tag, sel in (("all", np.ones(led.height, bool)), ("final", (led["t"] >= final_t).to_numpy())):
            if sel.sum() == 0:
                continue
            order, d = ranks(Xl[sel].mean(0))
            r[tag] = {"nearest": [names[int(a)] for a in order[:3]],
                      "rank_kimi_k2.6": int(np.where(order == 25)[0][0]) + 1, "n_ref_agents": len(agents),
                      "n_msgs": int(sel.sum())}
        # power: self-rank of random n-message samples of each reference agent (#44 days), own centroid leave-out
        rng = np.random.default_rng(0)
        n_s = int(r["final"]["n_msgs"]) if "final" in r else 16
        selfranks = []
        for a in agents:
            ix = np.where((ar == a) & (ref["goal_no"].to_numpy() == 44))[0]
            if len(ix) < n_s + 5:
                continue
            for _ in range(20):
                samp = rng.choice(ix, n_s, replace=False)
                keep = np.setdiff1d(np.where(ar == a)[0], samp)
                C2 = C.copy()
                C2[np.searchsorted(agents, a)] = Xr[keep].mean(0)
                d = (((Xr[samp].mean(0) - C2) / sd) ** 2).sum(1)
                selfranks.append(int(np.where(agents[np.argsort(d)] == a)[0][0]) + 1)
        r["power_selfrank"] = {"n_msgs": n_s, "share_rank1": float(np.mean(np.array(selfranks) == 1)),
                               "share_rank_le2": float(np.mean(np.array(selfranks) <= 2)),
                               "median_rank": float(np.median(selfranks)), "n_draws": len(selfranks)}
        out[c] = r
    return out


def main():
    m = L.load_messages()
    for name, fn in (("G51", lambda: g51(m)), ("G12", lambda: g12(m)), ("G44", g44)):
        r = fn()
        (L.DATA / name).mkdir(parents=True, exist_ok=True)
        (L.DATA / name / "native.json").write_text(json.dumps(r, indent=1, default=float))
        print(name, json.dumps({k: v for k, v in r.items() if k != "agents"}, default=float)[:2500], flush=True)


if __name__ == "__main__":
    main()
