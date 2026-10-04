"""H48 period-native tests (role: native): NE42 (merge A-B-A), G38 (per-agent and per-room), G51 (newcomer
assimilation across joins), NE32 (isolated newcomers). Designs and dated predictions are in the folders' READMEs.

  uv run python hypotheses/H48-settling-mixing-time/analysis/natives.py [--only NE42,G38,G51,NE32]
Writes data/processed/H48-settling-mixing-time/{NE42,G38,G51,NE32}/natives.json (+ parquet tables)."""
from __future__ import annotations

import argparse
import datetime as dt
import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h48lib as L  # noqa: E402
from h48lib import hc  # noqa: E402
import settling as SE  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

MODELS = SE.MODELS
RNG = np.random.default_rng(hc.SEED)


def spearman_perm(x, y, n_perm=10000, alternative="greater"):
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    n = len(x)
    if n < 3:
        return {"n": n, "rho": None, "p": None}
    r = stats.spearmanr(x, y).statistic
    if n <= 7:
        perms = [stats.spearmanr(x, y[list(p)]).statistic for p in itertools.permutations(range(n))]
    else:
        perms = [stats.spearmanr(x, RNG.permutation(y)).statistic for _ in range(n_perm)]
    perms = np.asarray(perms)
    p = float(np.mean(perms >= r - 1e-12)) if alternative == "greater" else float(np.mean(perms <= r + 1e-12))
    return {"n": n, "rho": float(r), "p": p}


def stmts_period(g: int, model: str, a_max: float | None = None):
    P = L.load_period(g)
    st = P["stmts"].filter(~pl.col("pre_kick") & (pl.col("a") >= 0))
    if a_max is not None:
        st = st.filter(pl.col("a") <= a_max)
    Z = np.asarray(SE.stmt_vectors(model)[st["srow"].to_numpy()], dtype=np.float64)
    return P, st, Z


def a_max_of(g):
    de = L.day_ends(g)
    return float(de[min(hc.MAX_FIT_DAYS, len(de)) - 1])


def block_s1(g, agents, model, a_max, width=1.0, room_kick: int | None = None):
    P, st, Z = stmts_period(g, model, a_max)
    reg = P["meta"]["regime"]
    k = SE.gvec(g, reg, model) if room_kick is None else SE.gvec(g, reg, model, "kickoff_room", room_kick)
    Dq = SE.decoys(g, reg, model)
    if k is None:
        return None, (np.array([]), np.array([]), np.array([]))
    m = st["agent"].is_in(agents).to_numpy()
    f, ser = L.s1_fit(st["a"].to_numpy()[m].astype(float), st["agent"].to_numpy()[m], Z[m], k, Dq, a_max, width)
    return f, ser


# ============================================================================================ NE42
def ne42():
    B = pl.read_parquet(hc.OUT / "readout_block.parquet")
    rows = []
    for g in (39, 40, 41):
        P = L.load_period(g)
        blocks = L.blocks_of(P["roster"])
        am = a_max_of(g)
        for b, ags in blocks.items():
            r = B.filter((pl.col("goal_no") == g) & (pl.col("room") == b)).row(0, named=True)
            rec = dict(goal_no=g, room=b, N=len(ags), T90=r["k1_room_T90"], T90_k5=r["k5_room_T90"],
                       tmix=r["tmix_batch_bulk"], dg=r["dg_bulk"], u=r["u"])
            for model in MODELS:
                f, _ = block_s1(g, ags, model, am)
                fr, _ = block_s1(g, ags, model, am, room_kick=b) if g != 40 else (None, None)
                rec[f"tau_{model}"] = f["tau"] if f else np.nan
                rec[f"det_{model}"] = bool(f and f["detected"])
                rec[f"dbic_{model}"] = f["dbic"] if f else np.nan
                rec[f"A0_{model}"] = f["A_0"] if f else np.nan
                rec[f"Ainf_{model}"] = f["A_inf"] if f else np.nan
                rec[f"tau_roomkick_{model}"] = fr["tau"] if fr else np.nan
            rows.append(rec)
    df = pl.DataFrame(rows)
    out = hc.OUT / "NE42"
    out.mkdir(parents=True, exist_ok=True)
    df.write_parquet(out / "blocks.parquet")
    res = {"blocks": df.to_dicts()}
    for model in MODELS:
        t = df[f"tau_{model}"].to_numpy()
        res[f"N1a_{model}"] = {"T90": spearman_perm(df["T90"].to_numpy(), t), "tmix": spearman_perm(df["tmix"].to_numpy(), t),
                               "dg": spearman_perm(df["dg"].to_numpy(), t), "T90_k5": spearman_perm(df["T90_k5"].to_numpy(), t)}
        A = df.filter(pl.col("goal_no") != 40)
        wmean_tau = float(np.exp(np.average(np.log(A[f"tau_{model}"].to_numpy()), weights=A["N"].to_numpy())))
        wmean_T90 = float(np.exp(np.average(np.log(A["T90"].to_numpy()), weights=A["N"].to_numpy())))
        m40 = df.filter(pl.col("goal_no") == 40).row(0, named=True)
        res[f"N1c_{model}"] = {"tau40": m40[f"tau_{model}"], "tauA_wmean": wmean_tau, "T90_40": m40["T90"],
                               "T90A_wmean": wmean_T90,
                               "same_sign": bool(np.sign(np.log(m40[f"tau_{model}"] / wmean_tau)) == np.sign(np.log(m40["T90"] / wmean_T90)))}
    X = pl.read_parquet(hc.OUT / "readout_period.parquet").filter(pl.col("goal_no").is_in([39, 40, 41]))
    res["N1b_all_pairs_T90"] = dict(zip(X["goal_no"].to_list(), X["k1_all_T90"].to_list()))
    hc.save_json(out / "natives.json", res)
    print("NE42", {k: v for k, v in res.items() if k != "blocks"})
    return res


# ============================================================================================ G38
def g38():
    g = 38
    am = a_max_of(g)
    P = L.load_period(g)
    blocks = L.blocks_of(P["roster"])
    out = hc.OUT / "G38"
    out.mkdir(parents=True, exist_ok=True)
    res = {"blocks": {b: ags for b, ags in blocks.items()}}
    # per-agent coverage time: 90% of room-mates read at least once
    cover = {}
    for b, ags in blocks.items():
        T1 = L.pair_cover_times(P["reads"], ags, 1)
        for n, a in enumerate(ags):
            v = np.sort(np.delete(T1[n], n))
            cover[a] = float(v[int(np.ceil(0.9 * len(v))) - 1])
    wr = L.window_rates(P["calls"], P["reads"], sorted(cover), float(L.day_ends(g)[1]))
    urate = dict(zip(sorted(cover), wr["u"]))
    rows = []
    for model in MODELS:
        _, st, Z = stmts_period(g, model, am)
        reg = P["meta"]["regime"]
        k = SE.gvec(g, reg, model)
        Dq = SE.decoys(g, reg, model)
        a = st["agent"].to_numpy()
        tt = st["a"].to_numpy().astype(float)
        for ag in sorted(cover):
            m = a == ag
            mids, bins = L.bin_vectors(tt[m], a[m], Z[m], 2.0, am, 2)
            ex = np.array([float((V @ k).mean() - (V @ Dq.T).mean()) if len(ags_) else np.nan for ags_, V in bins])
            f = L.exp_plateau_fit(mids, ex)
            rows.append(dict(model=model, agent=ag, T_cover=cover[ag], u=urate[ag], tau=f["tau"] if f else np.nan,
                             detected=bool(f and f["detected"]), dbic=f["dbic"] if f else np.nan,
                             n_bins=int(np.isfinite(ex).sum())))
    df = pl.DataFrame(rows)
    df.write_parquet(out / "agents.parquet")
    for model in MODELS:
        d = df.filter((pl.col("model") == model) & pl.col("detected"))
        res[f"N2a_{model}"] = {**spearman_perm(d["T_cover"].to_numpy(), d["tau"].to_numpy()),
                               "n_agents": df.filter(pl.col("model") == model).height,
                               "rho_u": spearman_perm(-d["u"].to_numpy(), d["tau"].to_numpy())}
    # room contrast (N2b) and per-room H20 tau_q (N2c)
    B = pl.read_parquet(hc.OUT / "readout_block.parquet").filter(pl.col("goal_no") == g)
    rr = {}
    for b, ags in blocks.items():
        r = B.filter(pl.col("room") == b).row(0, named=True)
        rec = {"N": len(ags), "T90": r["k1_room_T90"], "tmix": r["tmix_batch_bulk"], "u": r["u"]}
        for model in MODELS:
            f, ser = block_s1(g, ags, model, am)
            fr, _ = block_s1(g, ags, model, am, room_kick=b)
            rec[f"tau_{model}"] = f["tau"] if f else None
            rec[f"det_{model}"] = bool(f and f["detected"])
            rec[f"tau_roomkick_{model}"] = fr["tau"] if fr else None
            _, st_all, Zall = stmts_period(g, model)
            srow = pl.read_parquet(hc.ED / "statements.parquet", columns=["pt_date"]).with_row_index("srow")
            sb = st_all.join(srow, on="srow", how="left")
            m = sb["agent"].is_in(ags).to_numpy()
            s2 = SE.h20_tau_q(sb.filter(pl.Series(m)), Zall[m], g)
            rec[f"tau_q_days_{model}"] = s2["tau_q_days"]
            rec[f"tau_q_det_{model}"] = s2["detected"]
            rec[f"lag1_{model}"] = s2.get("lag1")
            pl.DataFrame({"a": ser[0], "excess": ser[1], "n_agents": ser[2]}).write_parquet(out / f"s1_room{b}_{model}.parquet")
        rr[b] = rec
    res["rooms"] = rr
    b_small, b_big = sorted(rr, key=lambda b: rr[b]["N"])[:2]
    for model in MODELS:
        dl_tau = np.log(rr[b_big][f"tau_{model}"] / rr[b_small][f"tau_{model}"])
        dl_T = np.log(rr[b_big]["T90"] / rr[b_small]["T90"])
        dq = (np.log(rr[b_big][f"tau_q_days_{model}"] / rr[b_small][f"tau_q_days_{model}"])
              if rr[b_big][f"tau_q_days_{model}"] and rr[b_small][f"tau_q_days_{model}"] else np.nan)
        res[f"N2b_{model}"] = {"dlog_tau": float(dl_tau), "dlog_T90": float(dl_T), "same_sign": bool(np.sign(dl_tau) == np.sign(dl_T))}
        res[f"N2c_{model}"] = {"dlog_tau_q": float(dq), "same_sign": bool(np.sign(dq) == np.sign(dl_T)) if np.isfinite(dq) else None}
    hc.save_json(out / "natives.json", res)
    print("G38", {k: v for k, v in res.items() if k.startswith("N2")})
    return res


# ============================================================================================ G51 / NE32
def newcomer_gaps(P, st, Z, newcomer: int, a_join: float, incumbents: list[int], width: float, span: float,
                  a_from: float | None = None):
    """Assimilation gap per bin: b(t) - s_n(t). b = incumbents' mean leave-one-out alignment."""
    a_from = a_join if a_from is None else a_from
    tt = st["a"].to_numpy().astype(float) - a_from
    ag = st["agent"].to_numpy()
    keep = (tt >= 0) & (tt < span) & (np.isin(ag, incumbents) | (ag == newcomer))
    mids, bins = L.bin_vectors(tt[keep], ag[keep], Z[keep], width, span, 2)
    gap, sn, bb = np.full(len(mids), np.nan), np.full(len(mids), np.nan), np.full(len(mids), np.nan)
    for k_, (ags, V) in enumerate(bins):
        if newcomer not in set(ags.tolist()):
            continue
        inc = [n for n, x in enumerate(ags) if x != newcomer]
        if len(inc) < 3:
            continue
        Vi = V[inc]
        S = Vi.sum(0)
        vn = V[list(ags).index(newcomer)]
        sn[k_] = float(vn @ L.unit(S))
        loo = [float(Vi[j] @ L.unit(S - Vi[j])) for j in range(len(inc))]
        bb[k_] = float(np.mean(loo))
        gap[k_] = bb[k_] - sn[k_]
    return mids, gap, sn, bb


def g51_ne32():
    g = 51
    P = L.load_period(g)
    ro = P["roster"]
    out51, out32 = hc.OUT / "G51", hc.OUT / "NE32"
    out51.mkdir(parents=True, exist_ok=True)
    out32.mkdir(parents=True, exist_ok=True)
    de = L.day_ends(g)
    a_end = float(de[-1])
    newc = ro.filter(~pl.col("on_day1")).sort("a_first")
    first_seen = dict(zip(ro["agent"].to_list(), ro["a_first"].to_list()))
    # merge times (onboarding / isolated rooms -> #general) from rooms_timeline
    rt = pl.read_parquet(hc.SH / "rooms_timeline.parquet").filter(
        pl.col("agent").is_in(newc["agent"].to_list()) & (pl.col("room") == 0)
        & (pl.col("t_start") > pl.datetime(2026, 7, 6, time_zone="UTC"))).group_by("agent").agg(pl.col("t_start").min())
    merge_a = {}
    for agent, t in rt.iter_rows():
        pd_ = hc.common.pt_date(t)
        merge_a[int(agent)] = float(hc.active_hours([t], [pd_], g)[0])
    # isolated arms (NE32 + Grok 4.5's onboarding room): rooms #sol, #terra, #luna (10-12) and grok onboarding (13)
    iso_rooms = pl.read_parquet(hc.SH / "rooms_timeline.parquet").filter(pl.col("room").is_in([10, 11, 12, 13])
                                                                          & pl.col("agent").is_in(newc["agent"].to_list()))
    iso_start = {}
    for agent, t in iso_rooms.group_by("agent").agg(pl.col("t_start").min()).iter_rows():
        iso_start[int(agent)] = float(hc.active_hours([t], [hc.common.pt_date(t)], g)[0])
    first_seen.update({a: min(first_seen[a], t) for a, t in iso_start.items()})
    newc = newc.with_columns(pl.col("agent").map_elements(lambda a: first_seen[a], return_dtype=pl.Float64).alias("a_first"))
    span, width = 16.0, 2.0
    rows, series = [], []
    for model in MODELS:
        _, st, Z = stmts_period(g, model)
        for n_, a_j in zip(newc["agent"].to_list(), newc["a_first"].to_list()):
            a_j = float(a_j)
            if a_j > a_end - 4:
                continue
            incumbents = [a for a, f0 in first_seen.items() if f0 is not None and f0 < a_j - 16.0 and a != n_]
            Np = P["calls"].filter((pl.col("a") >= a_j - 8) & (pl.col("a") < a_j) & pl.col("agent").is_in(incumbents))["agent"].n_unique()
            iso = n_ in iso_start
            a_from = merge_a.get(n_, a_j) if iso else a_j
            mids, gap, sn, bb = newcomer_gaps(P, st, Z, n_, a_j, incumbents, width, span, a_from)
            f = L.exp_plateau_fit(mids, gap)
            mids_j, gap_j, _, _ = newcomer_gaps(P, st, Z, n_, a_j, incumbents, width, span, a_j)
            fj = L.exp_plateau_fit(mids_j, gap_j)
            # coverage (from the join): T90_in (newcomer reads incumbents), T90_out (incumbents read newcomer)
            r = P["reads"].filter(pl.col("a_msg") >= a_j)
            rin = r.filter((pl.col("reader") == n_) & pl.col("sender").is_in(incumbents)).group_by("sender").agg(pl.col("a_read").min())
            rout = r.filter((pl.col("sender") == n_) & pl.col("reader").is_in(incumbents)).group_by("reader").agg(pl.col("a_read").min())

            def q90(times, n_all):
                v = np.sort(np.r_[np.asarray(times, float) - a_j, np.full(max(n_all - len(times), 0), np.inf)])
                return float(v[int(np.ceil(0.9 * len(v))) - 1]) if len(v) else np.nan
            n_present = Np
            rows.append(dict(model=model, agent=n_, a_join=a_j, a_merge=merge_a.get(n_), isolated=iso, N_join=n_present,
                             T90_in=q90(rin["a_read"].to_list(), n_present), T90_out=q90(rout["a_read"].to_list(), n_present),
                             tau_a=f["tau"] if f else np.nan, det=bool(f and f["detected"]), g0=f["A_0"] if f else np.nan,
                             ginf=f["A_inf"] if f else np.nan, dbic=f["dbic"] if f else np.nan,
                             tau_a_from_join=fj["tau"] if fj else np.nan, det_from_join=bool(fj and fj["detected"]),
                             n_bins=int(np.isfinite(gap).sum())))
            for m_, g_, s_, b_ in zip(mids, gap, sn, bb):
                series.append(dict(model=model, agent=n_, t=m_, gap=g_, s_n=s_, b=b_, clock="merge" if iso else "join"))
    df = pl.DataFrame(rows)
    df.write_parquet(out51 / "newcomers.parquet")
    pl.DataFrame(series).write_parquet(out51 / "newcomer_series.parquet")
    res = {"newcomers": df.to_dicts()}
    for model in MODELS:
        d = df.filter((pl.col("model") == model) & pl.col("det"))
        res[f"N3a_{model}"] = spearman_perm(d["T90_in"].to_numpy(), d["tau_a"].to_numpy())
        res[f"N3a_out_{model}"] = spearman_perm(d["T90_out"].to_numpy(), d["tau_a"].to_numpy())
        res[f"N3b_{model}"] = spearman_perm(d["N_join"].to_numpy().astype(float), d["tau_a"].to_numpy())
        a_ = df.filter(pl.col("model") == model)
        res[f"N3c_{model}"] = {"share_g0_gt_ginf": float(np.mean((a_["g0"] > a_["ginf"]).fill_null(False).to_numpy())),
                               "n": a_.height, "n_detected": d.height}
    hc.save_json(out51 / "natives.json", res)
    print("G51", {k: v for k, v in res.items() if k != "newcomers"})

    # NE32: isolated arms in fine bins around the merge
    iso_ag = [a for a in df.filter(pl.col("isolated"))["agent"].unique().to_list()]
    r32 = {"isolated": iso_ag, "merge_a": {a: merge_a.get(a) for a in iso_ag}}
    fine = []
    for model in MODELS:
        _, st, Z = stmts_period(g, model)
        for n_ in iso_ag:
            a_j = float(first_seen[n_])
            a_m = merge_a[n_]
            incumbents = [a for a, f0 in first_seen.items() if f0 is not None and f0 < a_j - 16.0 and a != n_]
            # gap in 0.5-h bins from the join to merge + 4 h; newcomer statements in isolation
            mids, gap, sn, bb = newcomer_gaps(P, st, Z, n_, a_j, incumbents, 0.5, (a_m - a_j) + 4.0, a_j)
            n_iso = int(((st["agent"] == n_) & (st["a"] >= a_j) & (st["a"] < a_m)).sum())
            iso_m = mids < (a_m - a_j)
            post = (mids >= (a_m - a_j)) & (mids < (a_m - a_j) + 2.0)
            half = (a_m - a_j) / 2
            g_iso, g_post = np.nanmean(gap[iso_m]) if iso_m.any() else np.nan, np.nanmean(gap[post]) if post.any() else np.nan
            g_iso1 = np.nanmean(gap[iso_m & (mids < half)]) if (iso_m & (mids < half)).any() else np.nan
            g_iso2 = np.nanmean(gap[iso_m & (mids >= half)]) if (iso_m & (mids >= half)).any() else np.nan
            items = pl.read_parquet(hc.OUT / "reads.parquet").filter((pl.col("goal_no") == g) & (pl.col("reader") == n_)
                                                                     & (pl.col("a_read") >= a_j) & (pl.col("a_read") < a_m)).height
            fine.append(dict(model=model, agent=n_, iso_h=a_m - a_j, n_stmts_iso=n_iso, agent_reads_iso=items,
                             gap_iso=g_iso, gap_iso_first=g_iso1, gap_iso_second=g_iso2, gap_post2h=g_post,
                             no_closing_in_iso=bool(np.isfinite(g_iso2) and np.isfinite(g_iso1) and (g_iso2 - g_iso1) >= -0.02),
                             closes_after_merge=bool(np.isfinite(g_post) and np.isfinite(g_iso) and g_post < g_iso)))
            for m_, g_ in zip(mids, gap):
                series.append(dict(model=model, agent=n_, t=m_ - (a_m - a_j), gap=g_, s_n=np.nan, b=np.nan, clock="ne32_fine"))
    fd = pl.DataFrame(fine)
    fd.write_parquet(out32 / "isolated.parquet")
    pl.DataFrame([s for s in series if s["clock"] == "ne32_fine"]).write_parquet(out32 / "series.parquet")
    r32["arms"] = fd.to_dicts()
    for model in MODELS:
        a_ = fd.filter(pl.col("model") == model)
        powered = a_.filter(pl.col("n_stmts_iso") >= 4)
        r32[f"N4a_{model}"] = {"no_closing_in_iso": int(powered["no_closing_in_iso"].sum()), "closes_after_merge": int(powered["closes_after_merge"].sum()),
                               "n_powered": powered.height, "n_arms": a_.height}
        d = df.filter(pl.col("model") == model)
        non = d.filter(~pl.col("isolated") & pl.col("det"))["tau_a"].to_numpy()
        isod = d.filter(pl.col("isolated") & pl.col("det"))
        r32[f"N4b_{model}"] = {"tau_from_merge": dict(zip(isod["agent"].to_list(), isod["tau_a"].to_list())),
                               "tau_from_join": dict(zip(d.filter(pl.col("isolated"))["agent"].to_list(),
                                                         d.filter(pl.col("isolated"))["tau_a_from_join"].to_list())),
                               "non_isolated_range": [float(non.min()), float(non.max())] if len(non) else None,
                               "inside": int(sum(1 for t in isod["tau_a"].to_list() if len(non) and non.min() <= t <= non.max()))}
    hc.save_json(out32 / "natives.json", r32)
    print("NE32", {k: v for k, v in r32.items() if k != "arms"})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="NE42,G38,G51")
    a = ap.parse_args()
    todo = a.only.split(",")
    if "NE42" in todo:
        ne42()
    if "G38" in todo:
        g38()
    if "G51" in todo or "NE32" in todo:
        g51_ne32()
    pp = hc.OUT / "_provenance.json"
    prov = hc.load_json(pp)
    prov.setdefault("derived", {})["natives"] = {"built_by": "hypotheses/H48-settling-mixing-time/analysis/natives.py",
                                                 "git_commit": hc.common.git_commit(), "tests": todo}
    hc.save_json(pp, prov)


if __name__ == "__main__":
    main()
