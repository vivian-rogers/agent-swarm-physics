"""H24 round 1b period-native tests (predictions in goalperiod-subhypotheses/G21/README.md, "Round 1b native test", and
G41/README.md, written before this script ran on real data). Non-holdout only.

  G21  pair-level reading DiD: does i's content move toward j's after i reads j's document (vs agents i did not read)?
  G41  one kickoff, two rooms after the split: within-room minus cross-room residual alignment by block, room-label
       permutation null; the same among each agent's "independent drafts" (statements before its first context-ledger
       read of a room-mate's message)

Outputs data/processed/H24-forecast-coupling-switch/{G21,G41}/r1b/native_<tag>.json.
Usage: uv run python natives_r1b.py --emb bge_small [--dedupe restate] [--style] [--only g21,g41]
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h24lib import H24, mention_regexes, project_out, record_reads, unit  # noqa: E402
from common import OUT, holdout_mask  # noqa: E402
import embed_models as EM  # noqa: E402

SEED = 20261004
UTC = dt.timezone.utc


def tag_of(a):
    t = a.emb
    if a.dedupe != "none":
        t += f"_dd-{a.dedupe}"
    if a.style:
        t += "_style"
    return t


def keep_mask(fl, dedupe):
    if dedupe == "none":
        return np.ones(fl.height, bool)
    if dedupe == "copies":
        return ~fl["self_repeat_both"].to_numpy()
    drop = fl["self_repeat_bge"] | fl["self_repeat_gte"]
    if dedupe == "echo":
        drop = drop | fl["cross_echo_bge"] | fl["cross_echo_gte"]
    return ~drop.to_numpy()


def residual(X, field, dim=32):
    Z = unit(np.asarray(X, np.float64)[:, :dim])
    F = [field["ghat"][:dim]] + list(field["chunks"][:, :dim])
    return unit(project_out(Z, np.array(F)))


# ============================================================================================ G21
def g21(a, rng, n_perm=2000):
    G = H24 / "G21"
    S = pl.read_parquet(G / "statements.parquet").with_row_index("i")
    if a.style:
        X = np.load(G / "r1b" / f"stmt_sr32_{a.emb}.npy").astype(np.float32)
    else:
        X = (np.load(G / "stmt_w64.npy") if a.emb == "bge_small" else np.load(G / "r1b" / f"stmt_w64_{a.emb}.npy")).astype(np.float32)
    keep = keep_mask(pl.read_parquet(G / "r1b" / "stmt.parquet"), a.dedupe)
    D = pl.read_parquet(G / "docs.parquet")
    Y = (np.load(G / "docs_w64.npy") if a.emb == "bge_small" else np.load(G / "r1b" / f"docs_w64_{a.emb}.npy")).astype(np.float32)
    field = dict(np.load(G / "r1b" / f"field_{a.emb}.npz"))
    Z = residual(X, field)[keep]
    S = S.filter(pl.Series(keep))
    Zd = residual(Y, field)
    cal = pl.read_parquet(OUT / "calendar.parquet").filter(pl.col("goal_no") == 21)
    assert not any(holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list()))
    sw = pl.read_parquet(G / "switch_on.parquet")
    present = sorted(sw["agent"].to_list())
    roster = pl.read_parquet(OUT / "roster.parquet")
    pats = mention_regexes([{"id": x, "name": n} for x, n in zip(roster["agent"].to_list(), roster["name"].to_list())])
    cu = pl.read_parquet(G / "cu_turns_text.parquet").filter(pl.col("agent").is_in(present) & pl.col("reasoning").is_not_null())
    ev = []
    for x in cu.sort("t").iter_rows(named=True):
        for sent in re.split(r"(?<=[.!?\n])\s+", x["reasoning"]):
            if not record_reads(sent):
                continue
            hits = [b for b in present if b != x["agent"] and pats[b].search(sent)]
            if hits:
                ev.append({"agent": x["agent"], "t": x["t"], "whose": hits[0]})
                break
    E = pl.DataFrame(ev, schema={"agent": pl.Int8, "t": pl.Datetime("us", "UTC"), "whose": pl.Int8})
    E = E.with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("pt_date"))
    first = E.sort("t").group_by("agent", "whose", "pt_date", maintain_order=True).first()
    tS = S["t"].to_numpy().astype("datetime64[us]").astype(np.int64) / 6e7      # minutes
    aS = S["agent"].to_numpy()
    tD = D["t"].to_numpy().astype("datetime64[us]").astype(np.int64) / 6e7
    aD = D["agent"].to_numpy()
    allE = E.with_columns((pl.col("t").cast(pl.Int64) / 6e7).alias("m"))

    def vec(Zx, sel):
        return unit(Zx[sel].mean(0)) if sel.sum() >= 2 else None

    def event_terms(i, tm, out_kind):
        """Per-agent delta a(i, k) = a_post - a_pre for every k with a reference; output = statements or docs."""
        if out_kind == "stmt":
            pre = vec(Z, (aS == i) & (tS >= tm - 60) & (tS < tm)); post = vec(Z, (aS == i) & (tS >= tm) & (tS < tm + 60))
        else:
            pre = vec(Zd, (aD == i) & (tD >= tm - 60) & (tD < tm)); post = vec(Zd, (aD == i) & (tD >= tm) & (tD < tm + 60))
        if pre is None or post is None:
            return None
        d = {}
        for k in present:
            if k == i:
                continue
            ref = vec(Z, (aS == k) & (tS >= tm - 180) & (tS < tm))
            if ref is not None:
                d[k] = float(post @ ref - pre @ ref)
        return d

    out = {"n_events_all": E.height, "n_first_events": first.height}
    for out_kind in ("stmt", "doc"):
        rows = []
        for r in first.iter_rows(named=True):
            i, j = int(r["agent"]), int(r["whose"])
            tm = r["t"].timestamp() / 60
            d = event_terms(i, tm, out_kind)
            if d is None or j not in d:
                continue
            read_near = set(allE.filter((pl.col("agent") == i) & ((pl.col("m") - tm).abs() <= 60))["whose"].to_list())
            ctrl = [k for k in d if k != j and k not in read_near]
            if not ctrl:
                continue
            rows.append({"i": i, "j": j, "t": r["t"].isoformat(), "d": d, "ctrl": ctrl, "read_near": sorted(read_near),
                         "did": d[j] - float(np.mean([d[k] for k in ctrl]))})
        if not rows:
            out[out_kind] = {"n": 0}
            continue
        obs = float(np.mean([x["did"] for x in rows]))
        null = []
        for _ in range(n_perm):
            vals = []
            for x in rows:
                cand = [k for k in x["d"] if k != x["j"] and k not in x["read_near"]]
                jj = cand[rng.integers(len(cand))]
                cc = [k for k in x["d"] if k != jj and k not in x["read_near"] and k != x["j"]]
                if not cc:
                    continue
                vals.append(x["d"][jj] - float(np.mean([x["d"][k] for k in cc])))
            null.append(np.mean(vals) if vals else np.nan)
        null = np.array(null, float)
        dids = np.array([x["did"] for x in rows])
        out[out_kind] = {"n": len(rows), "mean_did": obs, "median_did": float(np.median(dids)), "frac_pos": float((dids > 0).mean()),
                         "perm_p": float((1 + np.nansum(null >= obs)) / (1 + np.isfinite(null).sum())),
                         "null_q95": float(np.nanquantile(null, 0.95)),
                         "sign_p": float(stats.binomtest(int((dids > 0).sum()), len(dids), 0.5, alternative="greater").pvalue),
                         "events": [{k: x[k] for k in ("i", "j", "t", "did")} for x in rows]}
    out["N1a"] = bool(out["stmt"].get("n", 0) and out["stmt"]["mean_did"] > 0 and out["stmt"]["perm_p"] < 0.05)
    out["N1b"] = bool(out["doc"].get("n", 0) and out["doc"]["mean_did"] > 0 and out["doc"]["perm_p"] < 0.05)
    return out


# ============================================================================================ G41
def g41(a, rng, B=200, n_perm=2000, k=3):
    goal = 41
    cal = pl.read_parquet(OUT / "calendar.parquet").filter(pl.col("goal_no") == goal).sort("pt_date")
    assert not any(holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list()))
    win0 = cal["win_start"][0]
    st = pl.read_parquet(EM.ED / "statements.parquet").with_row_index("srow").filter(
        (pl.col("goal_no") == goal) & ~pl.col("holdout"))
    fl = pl.read_parquet(OUT / "statement_flags.parquet",
                         columns=["srow", "self_repeat_bge", "self_repeat_gte", "self_repeat_both", "cross_echo_bge",
                                  "cross_echo_gte"]).sort("srow")
    st = st.filter(pl.Series(keep_mask(fl, a.dedupe)[st["srow"].to_numpy()]))
    V = EM.statement_vectors(a.emb, "style_resid_period32" if a.style else "white32")
    field = dict(np.load(H24 / "G41" / "r1b" / f"field_{a.emb}.npz"))
    Zall = residual(np.asarray(V[st["srow"].to_numpy()], np.float32), field)
    rt = pl.read_parquet(OUT / "rooms_timeline.parquet")
    t_mid = win0 + dt.timedelta(minutes=30)
    room = {int(r["agent"]): int(r["room"]) for r in rt.filter((pl.col("t_start") <= t_mid) & (pl.col("t_end") > t_mid)
                                                              & pl.col("room").is_in([2, 3])).iter_rows(named=True)}
    st = st.with_columns(pl.col("agent").replace_strict(room, default=None).alias("prm"))
    ok = st["prm"].is_not_null().to_numpy()
    st, Zall = st.filter(pl.Series(ok)), Zall[ok]
    opens = dict(zip(cal["pt_date"].to_list(), cal["win_start"].to_list()))
    mins = np.array([(t - opens[d]).total_seconds() / 60 for t, d in zip(st["t"].to_list(), st["pt_date"].to_list())])
    agents = st["agent"].to_numpy()
    days = cal["pt_date"].to_list()

    def block_dw(sel, label):
        ags = sorted(a_ for a_ in set(agents[sel].tolist()) if (sel & (agents == a_)).sum() >= k)
        if len(ags) < 4:
            return None
        rm = np.array([room[a_] for a_ in ags])
        if (rm == 2).sum() < 2 or (rm == 3).sum() < 2:
            return None
        groups = [np.flatnonzero(sel & (agents == a_)) for a_ in ags]
        Cm = np.zeros((len(ags), len(ags)))
        for _ in range(B):
            Vv = np.array([unit(Zall[rng.choice(g, k, replace=False)].mean(0)) for g in groups])
            Cm += Vv @ Vv.T
        Cm /= B

        def dw(rmx):
            same = rmx[:, None] == rmx[None, :]
            off = ~np.eye(len(rmx), dtype=bool)
            return float(Cm[same & off].mean() - Cm[~same].mean()), float(Cm[same & off].mean()), float(Cm[~same].mean())
        obs, aw, ac = dw(rm)
        null = np.array([dw(rng.permutation(rm))[0] for _ in range(n_perm)])
        return {"block": label, "n_best": int((rm == 2).sum()), "n_rest": int((rm == 3).sum()), "dW": obs, "A_within": aw,
                "A_cross": ac, "null_q95": float(np.quantile(null, 0.95)), "perm_p": float((1 + (null >= obs).sum()) / (1 + n_perm))}

    out = {"rooms": {str(x): y for x, y in sorted(room.items())}, "day1_blocks": [], "days": []}
    d1 = (st["pt_date"] == days[0]).to_numpy()
    for b in range(8):
        r = block_dw(d1 & (mins >= 30 * b) & (mins < 30 * (b + 1)), f"day1 {30 * b}-{30 * (b + 1)} min")
        if r:
            out["day1_blocks"].append(r)
    for d in days:
        r = block_dw((st["pt_date"] == d).to_numpy(), d)
        if r:
            out["days"].append(r)
    bl = out["day1_blocks"]
    if len(bl) >= 3:
        rho, p = stats.spearmanr(np.arange(len(bl)), [x["dW"] for x in bl])
        out["day1_trend"] = {"rho": float(rho), "p": float(p)}
    # independent drafts: statements before the agent's first ledger read of a room-mate's post-open message
    t = pl.scan_parquet(OUT / "context_ledger_turns.parquet").filter(pl.col("pt_date") == days[0]).select("turn_id", "agent", "t_call").collect()
    it = (pl.scan_parquet(OUT / "context_ledger_items.parquet").filter(pl.col("turn_id").is_in(t["turn_id"].implode()))
          .filter(pl.col("kind") == "agent").collect().join(t, on="turn_id")
          .with_columns((pl.col("t_call") - pl.duration(seconds=pl.col("age_s"))).alias("t_post")))
    it = it.filter(pl.col("t_post") >= win0)
    it = it.filter(pl.col("sender").replace_strict(room, default=-1) == pl.col("agent").replace_strict(room, default=-2))
    fr = dict(it.group_by("agent").agg(pl.col("t_call").min()).iter_rows())
    tt = st["t"].to_list()
    pre = np.array([d1[n] and (agents[n] in fr) and tt[n] < fr[agents[n]] for n in range(len(tt))])
    draft_counts = {str(a_): int((pre & (agents == a_)).sum()) for a_ in sorted(room)}
    out["drafts"] = {"first_read_min": {str(a_): round((fr[a_] - win0).total_seconds() / 60, 2) for a_ in sorted(fr)},
                     "n_statements": draft_counts}
    ags = [a_ for a_ in sorted(room) if draft_counts[str(a_)] >= 1]
    rm = np.array([room[a_] for a_ in ags])
    if len(ags) >= 4 and (rm == 2).sum() >= 2 and (rm == 3).sum() >= 2:
        Vv = np.array([unit(Zall[pre & (agents == a_)].mean(0)) for a_ in ags])
        Cm = Vv @ Vv.T

        def dw(rmx):
            same = rmx[:, None] == rmx[None, :]
            off = ~np.eye(len(rmx), dtype=bool)
            return float(Cm[same & off].mean() - Cm[~same].mean())
        obs = dw(rm)
        null = np.array([dw(rng.permutation(rm)) for _ in range(n_perm)])
        out["drafts"].update(dW=obs, null_q95=float(np.quantile(null, 0.95)), perm_p=float((1 + (null >= obs).sum()) / (1 + n_perm)),
                             n_best=int((rm == 2).sum()), n_rest=int((rm == 3).sum()))
        out["N2c"] = bool(abs(obs) < float(np.quantile(np.abs(null), 0.95)))
    else:
        out["N2c"] = None
        out["drafts"]["note"] = "fewer than 2 agents per room have any statement before their first read: untestable"
    out["N2a"] = bool(bl and bl[0]["dW"] > bl[0]["null_q95"])
    d2 = [x for x in out["days"] if x["block"] == days[1]]
    out["N2b"] = bool(out.get("day1_trend", {}).get("rho", 0) > 0 and d2 and d2[0]["dW"] > d2[0]["null_q95"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emb", default="bge_small", choices=["bge_small", "gte_modernbert"])
    ap.add_argument("--dedupe", default="none", choices=["none", "copies", "restate", "echo"])
    ap.add_argument("--style", action="store_true")
    ap.add_argument("--only", default="g21,g41")
    a = ap.parse_args()
    tag = tag_of(a)
    rng = np.random.default_rng(SEED)
    if "g21" in a.only:
        r = g21(a, rng)
        (H24 / "G21" / "r1b").mkdir(parents=True, exist_ok=True)
        (H24 / "G21" / "r1b" / f"native_{tag}.json").write_text(json.dumps(r, indent=1, default=str))
        print("G21", tag, {k: (v if not isinstance(v, dict) else {kk: vv for kk, vv in v.items() if kk != "events"})
                           for k, v in r.items()}, flush=True)
    if "g41" in a.only:
        r = g41(a, rng)
        (H24 / "G41" / "r1b").mkdir(parents=True, exist_ok=True)
        (H24 / "G41" / "r1b" / f"native_{tag}.json").write_text(json.dumps(r, indent=1, default=str))
        print("G41", tag, json.dumps({k: v for k, v in r.items() if k != "rooms"}, default=str)[:2500], flush=True)


if __name__ == "__main__":
    main()
