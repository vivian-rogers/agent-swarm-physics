"""H112 natives (G44 arms, G51 post-read onset, phase contrast lives in run.py) and the post hoc A2 checks.

A2 (post hoc, disclosed): (a) claimed co-switches only: both agents posted a claim naming P within +-15 min of their
own switch, so both classes have chat engagement; (b) risk differences next to the risk ratios (departure rates
near ceiling cap any RR).
Usage: uv run python hypotheses/H112-crossing-claims-two-cycles/analysis/natives.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "scheme"))
import h112lib as L  # noqa: E402
import h112scheme as S  # noqa: E402

D = S.ROOT / "data/processed/H112-crossing-claims-two-cycles"
RES = D / "results"


def rebuild(g: int):
    """Rebuild the period in memory (unhashed project names) for the native joins."""
    r = S.build_period(g, with_work=False)
    days = r["days"]
    return r, S.load_claims(g, days), S.load_touches(g, days), S.load_calls_period(g, days), days


def claimed_flags(pairs: pl.DataFrame, claims: pl.DataFrame) -> pl.DataFrame:
    c = claims.select(pl.col("agent"), "project", pl.col("t").alias("tc"))
    out = pairs
    for who, tcol, flag in (("ai", "ti", "claim_i"), ("aj", "tj", "claim_j")):
        j = pairs.select("pid", pl.col(who).alias("agent"), "project", pl.col(tcol).alias("tsw")).join(c, on=["agent", "project"])
        j = j.filter(((pl.col("tc") - pl.col("tsw")).dt.total_seconds().abs() <= 900)).select("pid").unique() \
            .with_columns(pl.lit(True).alias(flag))
        out = out.join(j, on="pid", how="left").with_columns(pl.col(flag).fill_null(False))
    return out


def risk_diff(y, x) -> dict:
    y = np.asarray(y, float); x = np.asarray(x, bool)
    if x.sum() == 0 or (~x).sum() == 0:
        return {}
    p1, p0 = y[x].mean(), y[~x].mean()
    se = np.sqrt(p1 * (1 - p1) / x.sum() + p0 * (1 - p0) / (~x).sum())
    return {"rd": float(p1 - p0), "lo": float(p1 - p0 - 1.96 * se), "hi": float(p1 - p0 + 1.96 * se), "p1": float(p1), "p0": float(p0),
            "n1": int(x.sum()), "n0": int((~x).sum())}


def post_read_onset(r, claims, touches, calls, days, before: int = 3, after: int = 3) -> dict:
    """G51 N2: departures in the `after` calls following an agent's first read (after its own switch) of a partner
    claim naming P, vs the `before` calls preceding it, among agents still on P at the window start."""
    from visibility import receipts
    pairs = r["pairs"]
    cd = S.calls_dict(calls)
    tt = {int(a): (g.sort("t")["t"].dt.epoch("us").to_numpy(), g.sort("t")["project"].to_numpy())
          for (a,), g in touches.group_by(["agent"], maintain_order=True)}
    cl = claims.select(pl.col("agent").alias("sender"), "message_id", "project", pl.col("t").alias("tm"))
    rows = []
    for who, partner, tsw in (("ai", "aj", "ti"), ("aj", "ai", "tj")):
        q = pairs.select("pid", "project", "pt_date", pl.col(who).alias("a"), pl.col(partner).alias("sender"),
                         pl.col(tsw).alias("tsw"), "tj")
        q = q.join(cl, on=["sender", "project"]).filter((pl.col("tm") >= pl.col("tsw") - pl.duration(seconds=900))
                                                       & (pl.col("tm") <= pl.col("tj") + pl.duration(seconds=1800)))
        rows.append(q)
    q = pl.concat(rows)
    if len(q) == 0:
        return {}
    rc = receipts(q["message_id"].unique().to_list()).select("message_id", pl.col("recipient").alias("a"), pl.col("t_call").alias("tr"))
    q = q.join(rc.with_columns(pl.col("a").cast(q.schema["a"])), on=["message_id", "a"], how="inner")
    q = q.filter(pl.col("tr") > pl.col("tsw")).group_by("pid", "a", "project", "pt_date").agg(pl.col("tr").min())
    n_before = n_after = n_risk = 0
    for row in q.iter_rows(named=True):
        a = int(row["a"]); v = cd.get(a); w = tt.get(a)
        if v is None or w is None:
            continue
        ca, cdays = v
        kr = int(np.searchsorted(ca, int(row["tr"].timestamp() * 1e6), side="left"))  # index of the read call
        lo, hi = kr - before, kr + after
        if lo < 0 or hi + 1 >= len(ca) or cdays[lo] != row["pt_date"] or cdays[hi + 1] != row["pt_date"]:
            continue
        def label_at(k):
            p = np.searchsorted(w[0], ca[k], side="left") - 1
            return w[1][p] if p >= 0 else None
        if label_at(lo) != row["project"]:
            continue
        n_risk += 1
        dep = None
        for k in range(lo + 1, hi + 2):
            if label_at(k) != row["project"]:
                dep = k; break
        if dep is None:
            continue
        if dep <= kr:
            n_before += 1
        else:
            n_after += 1
    tot = n_before + n_after
    out = {"n_at_risk": n_risk, "dep_before": n_before, "dep_after": n_after}
    if tot:
        ci = stats.binomtest(n_after, tot).proportion_ci()
        # rate ratio after/before (equal windows) = p/(1-p); CI from the binomial share
        f = lambda p: p / (1 - p) if p < 1 else float("inf")  # noqa: E731
        out.update(ratio=f(n_after / tot), lo=f(ci.low), hi=f(ci.high))
    return out


def main():
    out = {}
    # ---- A2 (post hoc): claimed-only co-switches and risk differences, testable periods
    per = json.loads((RES / "periods.json").read_text())
    testable = [int(g) for g, o in per.items() if o["testable"]]
    frames = []
    cache = {}
    for g in testable:
        r, claims, touches, calls, days = rebuild(g)
        cache[g] = (r, claims, touches, calls, days)
        p = claimed_flags(r["pairs"], claims)
        pf = L.pair_frame(p, unit=f"G{g:02d}")
        frames.append(pf)
    allp = pl.concat(frames, how="diagonal_relaxed")
    cp = allp.filter(pl.col("claim_i") & pl.col("claim_j"))
    out["A2_claimed"] = {"n": len(cp), "n_read": int(cp["read"].sum()), "n_unaware": int(cp["unaware"].sum()),
                         "n_inflight": int(cp["inflight"].sum()),
                         "rr_u": L.mh_rr(cp["any"].to_numpy(), cp["unaware"].to_numpy(), L.strata_of(cp)) if len(cp) else {},
                         "rd_u": risk_diff(cp["any"].to_numpy(), cp["unaware"].to_numpy())}
    one = allp.filter(pl.col("claim_i") | pl.col("claim_j"))
    out["A2_any_claim"] = {"n": len(one), "rr_u": L.mh_rr(one["any"].to_numpy(), one["unaware"].to_numpy(), L.strata_of(one)),
                           "rd_u": risk_diff(one["any"].to_numpy(), one["unaware"].to_numpy())}
    nocl = allp.filter(~pl.col("claim_i") & ~pl.col("claim_j"))
    out["A2_no_claims"] = {"n": len(nocl), "p_any": float(nocl["any"].mean()) if len(nocl) else None,
                           "n_read": int(nocl["read"].sum())}
    out["A2_rd_all"] = risk_diff(allp["any"].to_numpy(), allp["unaware"].to_numpy())
    # ---- G51 N2: post-read onset
    if 51 in cache:
        r, claims, touches, calls, days = cache[51]
        out["G51_N2_post_read"] = post_read_onset(r, claims, touches, calls, days)
    # ---- G44 N3: assigned (#best) vs free (#rest) arms by the second mover's room
    r, claims, touches, calls, days = cache.get(44) or rebuild(44)
    rt = pl.read_parquet(S.SHARED / "rooms_timeline.parquet").with_columns(
        pl.col("t_end").fill_null(pl.datetime(2100, 1, 1, time_zone="UTC")))
    rooms = pl.read_parquet(S.SHARED / "rooms.parquet")
    p = L.pair_frame(r["pairs"], unit="G44")
    if len(p):
        rr = []
        for row in p.select("pid", "aj", "tj").iter_rows():
            m = rt.filter((pl.col("agent") == row[1]) & (pl.col("t_start") <= row[2]) & (pl.col("t_end") > row[2]))
            rr.append(int(m["room"][0]) if len(m) else -1)
        p = p.with_columns(pl.Series("room_j", rr))
        names = {int(a): "#" + str(b) for a, b in rooms.select("room", "name").iter_rows()}
        out["G44_arms"] = {}
        for room in sorted(set(rr)):
            sub = p.filter(pl.col("room_j") == room)
            out["G44_arms"][names.get(room, str(room))] = {
                "n": len(sub), "n_read": int(sub["read"].sum()), "n_unaware": int(sub["unaware"].sum()),
                "rr_u": L.mh_rr(sub["any"].to_numpy(), sub["unaware"].to_numpy(), L.strata_of(sub)) if len(sub) else {},
                "p_any_read": float(sub.filter(pl.col("read"))["any"].mean()) if sub["read"].sum() else None,
                "p_any_unaware": float(sub.filter(pl.col("unaware"))["any"].mean()) if sub["unaware"].sum() else None}
    # ---- G42 descriptive
    p42 = L.pair_frame(pl.read_parquet(D / "G42/pairs.parquet"), unit="G42")
    out["G42"] = {"n": len(p42), "classes": dict(p42.group_by("cls").len().iter_rows()) if len(p42) else {},
                  "p_any": float(p42["any"].mean()) if len(p42) else None, "p_both": float(p42["both"].mean()) if len(p42) else None}
    (RES / "natives.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
