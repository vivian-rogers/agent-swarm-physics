"""H82 natives (non-holdout).

N1 NE27  #10 kickoff (2025-08-18): veterans vs three newcomers (9, 10, 11) on days 1-3; endogenous field = #8 centroid
         (#9 held out). Newcomer split; placebo = other regime-I centroids.
N2 NE32  #51 newcomers 35, 36, 37 (isolated rooms 07-09) and 38 (07-10): history centroid H (non-holdout #36-#44) vs
         single-period placebo centroids, beyond the #51 fields, own agent goal, the family prior (same-lab
         incumbents' #51 mean) and the #51 village centroid (leave-i-out). Incumbents (present in #44) as the reference.
N3 NE15  regime-III room boundaries (37->38, 38->39, 39->40, 41->42): gamma_read - gamma_unread for veterans on day 1,
         with sender-prior-residualized statement centroids of P-1's last two active days, matched posting hours.

Output: data/processed/H82-remanence-endogenous-field/natives/natives.json
Usage: uv run python hypotheses/H82-remanence-endogenous-field/analysis/natives.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h82lib as L  # noqa: E402

ROOT = L.ROOT
SH = ROOT / "data/processed/shared"
ED = SH / "embeddings"
MODELS = ["bge_small", "gte_modernbert"]
SUFFIX = {"bge_small": "bge_small", "gte_modernbert": "gte_modernbert"}


# ---------------------------------------------------------------------------------------------------- N1 NE27
def ne27(D, rng, boot=500):
    days10 = sorted(set(D.date[(D.goal == 10)].tolist()))[:3]
    brow = {"P": 10, "prev": 8, "next": 11, "regime": "I", "days_P": days10}
    des = L.boundary_designs(D, brow, days=3, newcomer_split=True)
    rows = L.boundary_stats(brow, des, n_boot=boot, rng=rng)
    df = pl.DataFrame(rows)
    out = {"days": days10, "rows": rows}
    for term in ("e_vet", "e_new"):
        d = df.filter(pl.col("term") == term)
        out[term] = {"mean_dgamma_d1_3": float(np.nanmean(d["dgamma"].to_numpy())),
                     "re": L.re_meta(d["dgamma"].to_numpy(), d["dgamma_se"].to_numpy()),
                     "n_group": d["n_group"].to_list()}
    return out


# ---------------------------------------------------------------------------------------------------- N2 NE32
def ne32(D, rng, boot=500):
    reg = "III"
    newc = [35, 36, 37, 38]
    days = sorted(d for d in set(D.date[(D.goal == 51)].tolist()) if "2026-07-09" <= d <= "2026-07-16")
    hist_goals = [g for g in D.goals_in_regime(reg) if 36 <= g <= 44]
    mh = (D.regime == reg) & np.isin(D.goal, hist_goals)
    H = L.unit(D.X[mh].mean(0))
    plc = {g: D.centroid(g, reg) for g in hist_goals}
    roster = pl.read_parquet(SH / "roster.parquet").select("agent", "lab")
    lab = dict(zip(roster["agent"].to_list(), roster["lab"].to_list()))
    inc44 = set(D.agent[(D.goal == 44) & (D.regime == reg)].tolist())
    kP = D.goal_dir.get((51, reg, "kickoff")); gP = D.goal_dir.get((51, reg, "goal"))
    rooms = D.room_dir.get((51, reg), {})
    m51 = (D.goal == 51) & (D.regime == reg)
    ys, Zs, grp, ags = [], [], [], []
    for day in days:
        rows = np.flatnonzero(m51 & (D.date == day))
        hum = D.day_human.get((day, reg))
        for r in rows:
            a = int(D.agent[r])
            if a not in newc and a not in inc44:
                continue
            fam = [b for b in set(D.agent[m51].tolist()) if lab.get(b) == lab.get(a) and b != a and b not in newc]
            fm = m51 & np.isin(D.agent, fam)
            if fm.sum() < 3:
                continue
            famp = L.unit(D.X[fm].mean(0))
            vil = L.unit(D.X[m51 & (D.agent != a)].mean(0))
            ag = D.agent_goal.get((a, reg))
            base = [kP, gP, hum if hum is not None else np.zeros(32), rooms.get(int(D.room[r]), np.zeros(32)),
                    L.unit(np.mean(ag, axis=0)) if ag else np.zeros(32), famp, vil]
            ys.append(D.X[r]); Zs.append(np.stack(base, 1)); grp.append(a in newc); ags.append(a)
    Y = np.array(ys); Zb = np.array(Zs); grp = np.array(grp); ags = np.array(ags)

    def coefs(field, idx):
        fn = grp[:, None].astype(float) * field[None, :]
        fi = (~grp)[:, None].astype(float) * field[None, :]
        Z = np.concatenate([Zb, fn[:, :, None], fi[:, :, None]], axis=2)
        b = L.fit(Y, Z, idx)
        return b[-2], b[-1]  # newcomers, incumbents

    def stats(idx):
        gn, gi = coefs(H, idx)
        pl_ = np.array([coefs(plc[g], idx) for g in hist_goals if plc[g] is not None])
        return np.array([gn - np.nanmedian(pl_[:, 0]), gi - np.nanmedian(pl_[:, 1]), gn, gi])

    allidx = np.arange(len(Y))
    real = stats(allidx)
    ua = np.unique(ags); boots = []
    for _ in range(boot):
        draw = rng.choice(ua, len(ua), replace=True)
        idx = np.concatenate([np.flatnonzero(ags == x) for x in draw])
        boots.append(stats(idx))
    boots = np.array(boots)
    lab_ = ["dgamma_new", "dgamma_inc", "gamma_new", "gamma_inc"]
    return {"days": days, "n_obs_new": int(grp.sum()), "n_obs_inc": int((~grp).sum()),
            "newcomers_present": sorted(set(ags[grp].tolist())),
            **{lab_[k]: float(real[k]) for k in range(4)},
            **{lab_[k] + "_ci": [float(np.nanquantile(boots[:, k], 0.025)), float(np.nanquantile(boots[:, k], 0.975))]
               for k in range(4)},
            "diff_new_minus_inc": float(real[0] - real[1]),
            "diff_ci": [float(np.nanquantile(boots[:, 0] - boots[:, 1], 0.025)),
                        float(np.nanquantile(boots[:, 0] - boots[:, 1], 0.975))]}


# ---------------------------------------------------------------------------------------------------- N3 NE15
def statement_table(model):
    st = pl.read_parquet(ED / "statements.parquet").with_row_index("srow").filter(pl.col("kind") == "chat")
    ci = pl.read_parquet(ED / "chat_index.parquet").with_row_index("src_row")
    st = st.join(ci.with_columns(pl.col("src_row").cast(pl.UInt32)), on="src_row", how="left")
    S = np.load(ED / f"statements_style_resid32_{SUFFIX[model]}.npy", mmap_mode="r")
    return st, S


def ne15(D, model, rng, boot=500):
    reg = "III"
    st, S = statement_table(model)
    turns = pl.read_parquet(SH / "context_ledger_turns.parquet", columns=["turn_id", "agent", "goal_no", "holdout"]) \
        .filter(pl.col("goal_no").is_in([37, 38, 39, 40, 41, 42]) & ~pl.col("holdout"))
    items = pl.scan_parquet(SH / "context_ledger_items.parquet").select("turn_id", "message_id") \
        .join(turns.lazy().select("turn_id", "agent"), on="turn_id", how="inner").collect()
    res = {}
    for prev, P in ((37, 38), (38, 39), (39, 40), (41, 42)):
        pdays = sorted(set(D.date[(D.goal == prev) & (D.regime == reg)].tolist()))[-2:]
        day1 = sorted(set(D.date[(D.goal == P) & (D.regime == reg)].tolist()))[0]
        w = st.filter(pl.col("pt_date").is_in(pdays) & ~pl.col("holdout") & pl.col("message_id").is_not_null())
        w = w.with_columns(pl.col("t").dt.truncate("1h").alias("hour"))
        Xs = np.asarray(S[w["srow"].to_numpy()], dtype=np.float64)
        senders = w["agent"].to_numpy()
        # sender-prior residualization (project out the sender's prior direction)
        for a in np.unique(senders):
            p = D.prior(int(a), reg, {prev, P})
            if p is not None:
                m = senders == a
                Xs[m] -= (Xs[m] @ p)[:, None] * p[None, :]
        mids = w["message_id"].to_list(); hours = w["hour"].to_numpy()
        read_by = items.filter(pl.col("message_id").is_in(mids)).group_by("agent").agg(pl.col("message_id").unique())
        read_by = {int(r["agent"]): set(r["message_id"]) for r in read_by.iter_rows(named=True)}
        rows = D.day_rows(P, reg, day1)
        kP = D.goal_dir.get((P, reg, "kickoff")); gP = D.goal_dir.get((P, reg, "goal"))
        kprev = D.goal_dir.get((prev, reg, "kickoff")); hum = D.day_human.get((day1, reg))
        rooms = D.room_dir.get((P, reg), {})
        prev_agents = set(D.agent[(D.goal == prev) & (D.regime == reg)].tolist())
        ys, Zs, ags, nr, nu = [], [], [], [], []
        for r in rows:
            a = int(D.agent[r])
            if a not in prev_agents or a not in read_by:
                continue
            pr = D.prior(a, reg, {prev, P})
            if pr is None:
                continue
            isread = np.array([m in read_by[a] for m in mids]) & (senders != a)
            isun = ~np.array([m in read_by[a] for m in mids]) & (senders != a)
            hr = set(hours[isread].tolist()) & set(hours[isun].tolist())
            hm = np.isin(hours, list(hr))
            if (isread & hm).sum() < 5 or (isun & hm).sum() < 5:
                continue
            er = L.unit(Xs[isread & hm].mean(0)); eu = L.unit(Xs[isun & hm].mean(0))
            cols = [kP, gP if gP is not None else np.zeros(32), kprev if kprev is not None else np.zeros(32),
                    hum if hum is not None else np.zeros(32),
                    rooms.get(int(D.room[r]), np.zeros(32)) if len(rooms) >= 2 else np.zeros(32), pr, er, eu]
            ys.append(D.X[r]); Zs.append(np.stack(cols, 1)); ags.append(a)
            nr.append(int((isread & hm).sum())); nu.append(int((isun & hm).sum()))
        if len(ys) < 3:
            res[f"{prev}->{P}"] = {"n_agents": len(ys), "skipped": True}
            continue
        Y = np.array(ys); Z = np.array(Zs)
        b = L.fit(Y, Z)
        diffs = []
        for _ in range(boot):
            idx = rng.integers(0, len(Y), len(Y))
            bb = L.fit(Y, Z, idx); diffs.append(bb[-2] - bb[-1])
        diffs = np.array(diffs)
        res[f"{prev}->{P}"] = {"n_agents": len(ys), "gamma_read": float(b[-2]), "gamma_unread": float(b[-1]),
                               "diff": float(b[-2] - b[-1]), "diff_se": float(np.nanstd(diffs)),
                               "diff_ci": [float(np.nanquantile(diffs, 0.025)), float(np.nanquantile(diffs, 0.975))],
                               "median_n_read": float(np.median(nr)), "median_n_unread": float(np.median(nu))}
    ok = [v for v in res.values() if not v.get("skipped")]
    if ok:
        e = np.array([v["diff"] for v in ok]); s = np.array([v["diff_se"] for v in ok])
        w = 1 / s ** 2
        mu = float((w * e).sum() / w.sum()); se = float(np.sqrt(1 / w.sum()))
        res["fixed_effect"] = {"mu": mu, "se": se, "lo": mu - 1.96 * se, "hi": mu + 1.96 * se, "k": len(ok)}
    return res


def main():
    out = L.OUT / "natives"; out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(8252)
    res = {"NE27": {}, "NE32": {}, "NE15": {}}
    for model in MODELS:
        D = L.Data(model)
        res["NE27"][model] = ne27(D, rng)
        res["NE32"][model] = ne32(D, rng)
        res["NE15"][model] = ne15(D, model, rng)
        print(model, "NE27", {t: res["NE27"][model][t]["mean_dgamma_d1_3"] for t in ("e_vet", "e_new")}, flush=True)
        print(model, "NE32", {k: v for k, v in res["NE32"][model].items() if k != "days"}, flush=True)
        print(model, "NE15", res["NE15"][model].get("fixed_effect"), flush=True)
    (out / "natives.json").write_text(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
