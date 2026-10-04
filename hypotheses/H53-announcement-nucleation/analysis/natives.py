"""H53 period-native tests: #26 election rounds (DQ6 ballots), #30 re-announcements of one shared repo, #31 waves vs
private projects, #40 frozen hub (negative control). Predictions are in each G<NN>/README.md (written before this ran).

Writes data/processed/H53-announcement-nucleation/natives/{g26,g30,g31,g40}.json (+ small parquet tables, codes only).
Usage: uv run python hypotheses/H53-announcement-nucleation/analysis/natives.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import nbinom, spearmanr

from h53core import (FU_S, OUT, agent_rr, auc_within, cpois_fit, cpois_robust, design, field_diagnostics, load, nb_fit,
                     prep)

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h53lib import SH, add_active, load_cal, project_map  # noqa: E402

NAT = OUT / "natives"


def calls_by_agent():
    cc = pl.read_parquet(OUT / "calls_cache.parquet").filter(pl.col("recv") & ~pl.col("ho_call"))
    return {int(a): (sub["t_call"].dt.epoch("us").to_numpy(), sub["a"].fill_null(np.nan).to_numpy(), sub["talk"].to_numpy())
            for (a,), sub in cc.sort("agent", "t_call").group_by(["agent"], maintain_order=True)}


def ledger_reads(message_ids):
    it = pl.scan_parquet(SH / "context_ledger_items.parquet").filter(pl.col("message_id").is_in(list(message_ids))).select(
        "turn_id", "message_id", "age_s").collect()
    cw = pl.read_parquet(SH / "call_windows.parquet", columns=["turn_id", "agent", "t_call", "holdout"])
    return it.join(cw, on="turn_id").filter(~pl.col("holdout"))


# ============================================================================ #26
def g26():
    gt = pl.read_parquet(SH / "ground_truth_labels.parquet").filter((pl.col("goal_no") == 26) & pl.col("preferred") & ~pl.col("holdout"))
    ph = gt.filter((pl.col("label_kind") == "phase") & pl.col("value").is_in(["approval_vote", "runoff", "confirmatory_vote"]))
    ph = ph.with_columns(pl.col("source_ref").str.replace("chat_core:message_id=", "").alias("mid"))
    chat = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "speaker_kind", "agent"])
    ph = ph.join(chat.rename({"message_id": "mid", "t": "t_msg", "agent": "announcer"}), on="mid", how="left")
    unit_of = {"approval_vote": "approval", "runoff": "runoff", "confirmatory_vote": "confirmatory"}
    ballots = gt.filter(pl.col("label_kind") == "ballot").group_by("unit", "agent_a").agg(pl.col("t_valid_from").min().alias("t_ballot"))
    reads = ledger_reads(ph["mid"].to_list())
    calls = calls_by_agent()
    out = {"rounds": {}}
    rows = []
    for p in ph.iter_rows(named=True):
        u = unit_of[p["value"]]
        b = ballots.filter(pl.col("unit") == u)
        rd = reads.filter(pl.col("message_id") == p["mid"]).select("agent", "t_call", "age_s")
        x = b.rename({"agent_a": "agent"}).join(rd, on="agent", how="full", coalesce=True)
        res = dict(seed_time=str(p["t_msg"]), window=[str(p["t_valid_from"]), str(p["t_valid_to"])], announcer=p["announcer"],
                   n_voters=int(b.height), n_readers=int(rd.height))
        after, ncalls, inflight = [], [], 0
        for r in x.iter_rows(named=True):
            row = dict(round=u, agent=r["agent"], t_read=r["t_call"], age_s=r["age_s"], t_ballot=r["t_ballot"])
            if r["t_ballot"] is not None and r["t_call"] is not None and r["agent"] in calls:
                tc = calls[r["agent"]][0]
                tb = int(r["t_ballot"].timestamp() * 1e6); tr = int(r["t_call"].timestamp() * 1e6)
                ib = np.searchsorted(tc, tb, "right") - 1   # call that produced the ballot (last call started before it)
                ir = np.searchsorted(tc, tr, "left")
                row["calls_read_to_ballot"] = int(ib - ir + 1)
                row["ballot_after_read"] = bool(tc[ib] >= tr)
                after.append(row["ballot_after_read"]); ncalls.append(row["calls_read_to_ballot"])
            rows.append(row)
        xx = x.drop_nulls(["t_ballot", "t_call"])
        rho = spearmanr(xx["t_call"].dt.epoch("us").to_numpy(), xx["t_ballot"].dt.epoch("us").to_numpy()).statistic if xx.height >= 4 else None
        res.update(frac_ballot_after_read=float(np.mean(after)) if after else None, n_scored=len(after),
                   median_calls_read_to_ballot=float(np.median(ncalls)) if ncalls else None, calls_list=sorted(ncalls),
                   spearman_read_ballot=None if rho is None else float(rho),
                   read_age_s=sorted([float(v) for v in rd["age_s"].to_list()]))
        w0, w1 = p["t_valid_from"], p["t_valid_to"]
        res["ballots_in_window"] = int(b.filter((pl.col("t_ballot") >= p["t_msg"]) & (pl.col("t_ballot") <= w1)).height)
        res["readers_in_window"] = int(rd.filter(pl.col("t_call") <= w1).height)
        nonv = rd.filter(~pl.col("agent").is_in(b["agent_a"].to_list()))
        res["nonvoter_read_age_s"] = sorted([float(v) for v in nonv["age_s"].to_list()])
        res["ballots_before_seed"] = int(b.filter(pl.col("t_ballot") < p["t_msg"]).height)
        out["rounds"][u] = res
    tab = pl.DataFrame(rows, infer_schema_length=None)
    tab.write_parquet(NAT / "g26_ballots_reads.parquet")
    # post hoc (labelled): the approval wave's effective seed = the first approval ballot (DQ2 threading: the next
    # ballots are top-1 replies to it); do the later ballots follow their read-out of it?
    ab = gt.filter((pl.col("label_kind") == "ballot") & (pl.col("unit") == "approval")).with_columns(
        pl.col("source_ref").str.extract(r"message_id=([0-9a-f-]+)").alias("mid")).sort("t_valid_from")
    first_mid = ab["mid"][0]
    bb = ab.group_by("agent_a").agg(pl.col("t_valid_from").min().alias("tb")).sort("tb")
    rd1 = ledger_reads([first_mid])
    ph_rows = []
    for rr in bb.iter_rows(named=True):
        q = rd1.filter(pl.col("agent") == rr["agent_a"])
        if q.height == 0 or rr["agent_a"] not in calls:
            continue
        tc = calls[rr["agent_a"]][0]
        tb = int(rr["tb"].timestamp() * 1e6); trr = int(q["t_call"][0].timestamp() * 1e6)
        ib = np.searchsorted(tc, tb, "right") - 1; ir = np.searchsorted(tc, trr, "left")
        ph_rows.append(dict(agent=int(rr["agent_a"]), age_s=float(q["age_s"][0]), calls=int(ib - ir + 1), after=bool(tc[ib] >= trr)))
    out["posthoc_approval_effective_seed"] = dict(n=len(ph_rows), frac_after=float(np.mean([x["after"] for x in ph_rows])),
                                                   calls=[x["calls"] for x in ph_rows], ages=[round(x["age_s"], 1) for x in ph_rows])
    return out


# ============================================================================ #30
def g30():
    cal = load_cal()
    pm = project_map()
    am = pl.read_parquet(SH / "artifact_mentions.parquet", columns=["artifact", "t", "agent", "speaker_kind", "source", "how", "room", "message_id"])
    am = am.join(pm, on="artifact")
    links = am.filter((pl.col("source").cast(pl.String) == "chat") & pl.col("how").cast(pl.String).is_in(["url", "bare"]))
    links = add_active(links, cal, keep_goal=True).filter((pl.col("a_goal") == 30) & ~pl.col("a_ho")).unique(["message_id", "project"]).sort("t")
    top = links.group_by("project").len().sort("len", descending=True).head(2)["project"].to_list()
    ps = pl.read_parquet(SH / "project_states.parquet").filter((pl.col("w_min") == 15) & (pl.col("sources").cast(pl.String) == "all")
                                                              & (pl.col("goal_no") == 30) & ~pl.col("holdout"))
    ps = ps.join(cal.select("pt_date", "win_start"), on="pt_date").with_columns(
        (pl.col("win_start") + pl.duration(seconds=pl.col("win").cast(pl.Int64) * 900)).alias("w0"), pl.col("project").cast(pl.String))
    ps = add_active(ps, cal, col="w0", out="aw")
    calls = calls_by_agent()
    cyc = (pl.read_parquet(OUT / "recipients.parquet").filter(pl.col("goal_no") == 30).group_by("agent").agg(pl.col("cyc_s").first()))
    cycd = dict(zip(cyc["agent"].to_list(), cyc["cyc_s"].to_list()))
    strict = am.filter((pl.col("speaker_kind").cast(pl.String) == "agent") & pl.col("how").cast(pl.String).is_in(["url", "output", "bare"]))
    strict = add_active(strict, cal, keep_goal=True).filter(pl.col("a_goal") == 30)
    rows, seeds_rows = [], []
    for X in top:
        lx = links.filter(pl.col("project") == X)
        prev = -1e18
        rs = []
        for r in lx.iter_rows(named=True):
            if r["a"] - prev >= 3600:
                rs.append(r)
            prev = r["a"]
        reads = ledger_reads([r["message_id"] for r in rs])
        labx = ps.filter(pl.col("project") == X)
        for r in rs:
            a_s = r["a"]
            rd = reads.filter(pl.col("message_id") == r["message_id"])
            rd = add_active(rd, cal, col="t_call", out="a_read")
            n_s = R = U = S = 0
            for q in rd.iter_rows(named=True):
                ag = q["agent"]
                if ag == r["agent"]:
                    continue
                on_before = labx.filter((pl.col("agent") == ag) & (pl.col("aw") >= a_s - 3600) & (pl.col("aw") < a_s)).height > 0
                if on_before:
                    continue
                n_s += 1
                oth = strict.filter((pl.col("agent") == ag) & (pl.col("a") >= a_s - 1800) & (pl.col("a") < a_s) & (pl.col("project") != X)).height
                unc = oth == 0
                timely = q["age_s"] <= (cycd.get(ag) or 15)
                ret = labx.filter((pl.col("agent") == ag) & (pl.col("aw") > a_s - 900) & (pl.col("aw") <= q["a_read"] + FU_S))
                y = ret.height > 0
                ret2 = labx.filter((pl.col("agent") == ag) & (pl.col("aw") > a_s - 900) & (pl.col("aw") <= a_s + 7200)).height > 0
                ca = calls.get(ag, (np.zeros(0), np.zeros(0), np.zeros(0)))
                lo, hi = np.searchsorted(ca[1], a_s - 1800), np.searchsorted(ca[1], a_s)
                rows.append(dict(project=top.index(X), sid=r["message_id"] + str(top.index(X)), agent=ag, y=float(y), x_timely=float(timely),
                                 x_unc=float(unc), lcalls=float(np.log1p(hi - lo)), talk=float(ca[2][lo:hi].any()) if hi > lo else 0.0,
                                 clu=r["a_pt_date"], age_s=q["age_s"]))
                R += int(timely and unc); U += int(unc); S += int(ret2)
            # pre-trend: returns (first X-label window after >= 60 min without X) in [-30, 0) vs (0, 30] min
            seeds_rows.append(dict(project=top.index(X), a=a_s, N=n_s, R=R, U=U, S=S, t=str(r["t"]), pt_date=r["a_pt_date"]))
    t = pl.DataFrame(rows)
    sd = pl.DataFrame(seeds_rows)
    # returns relative to re-seeds (pre-trend)
    pre = post = 0
    for X in top:
        labx = ps.filter(pl.col("project") == X).sort("agent", "aw")
        ret_times = []
        for (ag,), sub in labx.group_by(["agent"], maintain_order=True):
            aw = sub["aw"].to_numpy()
            gaps = np.diff(np.concatenate([[-1e18], aw]))
            ret_times += list(aw[gaps >= 3600 + 900])
        ret_times = np.array(ret_times)
        for a_s in sd.filter(pl.col("project") == top.index(X))["a"].to_list():
            pre += int(((ret_times >= a_s - 1800) & (ret_times < a_s)).sum())
            post += int(((ret_times > a_s) & (ret_times <= a_s + 1800)).sum())
    out = dict(n_reseeds=int(sd.height), projects=2, n_pairs=int(t.height), n_returns=int(t["y"].sum()))
    out["agent"] = agent_rr(t.with_columns(pl.col("sid").alias("sid")))
    sdd = sd.filter(pl.col("N") >= 3).with_columns(pl.col("R").log1p().alias("lR"), pl.col("N").log1p().alias("lN"), pl.lit(30).alias("goal_no"))
    y, X_, gi, G = design(sdd, ["lR", "lN"])
    th, ll = nb_fit(y, X_, gi, G)
    from h53core import nb_robust_se
    se = nb_robust_se(th, y, X_, gi, G, sdd["pt_date"].to_numpy())
    out["seed_slope_lR"] = dict(beta=float(th[1]), se=float(se[0]), lo=float(th[1] - 1.96 * se[0]), hi=float(th[1] + 1.96 * se[0]), n=int(sdd.height),
                                mean_S=float(sdd["S"].mean()), mean_R=float(sdd["R"].mean()))
    out["pretrend"] = dict(pre_30=pre, post_30=post, ratio=(post / pre) if pre else None)
    # H27 onsets in #30
    on = pl.read_parquet(ROOT27 / "onsets_round1.parquet").filter((pl.col("goal") == 30) & (pl.col("arm") == "W15") & (pl.col("rule") == "O1"))
    ser = pl.read_parquet(ROOT27 / "G30" / "series_w15.parquet").select("gwin", "pt_date", "win")
    on = on.join(ser, left_on="w0", right_on="gwin").join(cal.select("pt_date", "win_start"), on="pt_date").with_columns(
        (pl.col("win_start") + pl.duration(seconds=pl.col("win").cast(pl.Int64) * 900)).alias("t_on"))
    on = add_active(on, cal, col="t_on", out="a_on")
    lead = []
    for a_on in on["a_on"].to_list():
        prior = sd.filter((pl.col("a") <= a_on + 900) & (pl.col("a") >= a_on - 3600))
        lead.append(None if prior.height == 0 else float((a_on - prior["a"].max()) / 60))
    out["h27_onsets_min_since_reseed"] = lead
    t.write_parquet(NAT / "g30_pairs.parquet"); sd.write_parquet(NAT / "g30_reseeds.parquet")
    return out


ROOT27 = OUT.parents[0] / "H27-herding-early-warning"


# ============================================================================ #31 (from the round-1 tables)
def g31():
    seeds, rec = load()
    s, r = prep(seeds, rec)
    s = s.filter((pl.col("goal_no") == 31) & pl.col("eligible"))
    s = s.with_columns(pl.max_horizontal(pl.lit(3), (pl.col("n_room") / 3).ceil()).alias("thr"))
    pos, neg = pl.col("herd_kmax") >= pl.col("thr"), pl.col("herd_kmax") <= 1
    out = dict(n=int(s.height), n_herded=int(s.filter(pos).height), n_never=int(s.filter(neg).height),
               frac_never=float(s.filter(neg).height / s.height))
    out["auc"] = {c: auc_within(s, c, pos, neg)["auc"] for c in ("R", "N_sus", "U", "share", "lstat", "tod")}
    top = s.sort("S", descending=True).head(5).select("S", "R", "U", "N_sus", "share", "herd_kmax", "carried", "human")
    out["largest_waves"] = top.to_dicts()
    rr = r.filter(pl.col("sid").is_in(s.filter(pos)["sid"].to_list()))
    out["field_herded"] = field_diagnostics(s.filter(pos), rr)
    out["field_all"] = field_diagnostics(s, r.filter(pl.col("sid").is_in(s["sid"].to_list())))
    for k in ("field_herded", "field_all"):
        out[k]["F1"].pop("curve", None)
    return out


# ============================================================================ #40
def g40():
    cal = load_cal()
    ps30 = pl.read_parquet(SH / "project_states.parquet").filter((pl.col("w_min") == 30) & (pl.col("sources").cast(pl.String) == "all")
                                                                & (pl.col("goal_no") == 40) & ~pl.col("holdout"))
    d1 = ps30["pt_date"].min()
    hub = ps30.filter(pl.col("pt_date") == d1).group_by("project").len().sort("len", descending=True)["project"][0]
    hub = str(hub)
    pm = project_map()
    projs = pl.read_parquet(OUT / "projects.parquet")
    hub_code = int(projs.filter(pl.col("project") == hub)["proj"][0])
    ad = pl.read_parquet(OUT / "adoptions.parquet").filter((pl.col("goal_no") == 40) & (pl.col("proj") == hub_code)).drop_nulls("t_label")
    seeds = pl.read_parquet(OUT / "seeds.parquet").filter((pl.col("goal_no") == 40) & (pl.col("proj") == hub_code))
    am = pl.read_parquet(SH / "artifact_mentions.parquet", columns=["artifact", "t", "speaker_kind", "source", "how", "message_id"]).join(pm, on="artifact")
    links = am.filter((pl.col("project") == hub) & (pl.col("source").cast(pl.String) == "chat") & pl.col("how").cast(pl.String).is_in(["url", "bare"]))
    links = add_active(links, cal, keep_goal=True).filter(pl.col("a_goal") == 40)
    reads = ledger_reads(links["message_id"].unique().to_list())
    first_read = reads.group_by("agent").agg(pl.col("t_call").min().alias("t_fr"))
    x = ad.join(first_read, on="agent", how="left")
    t_seed = seeds["t_seed"][0] if seeds.height else None
    x = x.with_columns(((pl.col("t_label") < t_seed) if t_seed is not None else pl.lit(False)).alias("pre_seed"),
                       (pl.col("t_fr").is_null() | (pl.col("t_fr") > pl.col("t_label"))).alias("unexposed"))
    x = add_active(x, cal, col="t_label", out="a_lab")
    day1 = cal.filter(pl.col("pt_date") == d1)
    a_day1 = float(day1["active_offset_s"][0])
    out = dict(hub_is_carried=bool(seeds["carried"][0]) if seeds.height else None, n_adopters=int(x.height),
               frac_pre_seed=float(x["pre_seed"].mean()), frac_unexposed=float(x["unexposed"].mean()),
               frac_pre_or_unexposed=float((x["pre_seed"] | x["unexposed"]).mean()),
               frac_first_hour_day1=float((x["a_lab"] < a_day1 + 3600).mean()),
               seed_min_after_day_start=float((seeds["a_seed"][0] - a_day1) / 60) if seeds.height else None,
               seed_human=bool(seeds["human"][0]) if seeds.height else None)
    # wave of the hub seed vs M_N prediction (pooled NB with period intercepts, partial pooling)
    s0, r0 = load()
    s1, _ = prep(s0, r0)
    from h53core import eligible_periods
    el = s1.filter(pl.col("eligible") & pl.col("goal_no").is_in(eligible_periods(s1)))
    y, X_, gi, G = design(el, ["lN"])
    th, _ = nb_fit(y, X_, gi, G, ridge_tau=1.0)
    gk = np.unique(el["goal_no"].to_numpy())
    hs = s1.filter((pl.col("goal_no") == 40) & (pl.col("proj") == hub_code))
    if hs.height:
        g_ix = int(np.where(gk == 40)[0][0])
        mu = float(np.exp(th[g_ix] + th[G] * hs["lN"][0]))
        rr_ = float(np.exp(-th[-1]))
        sobs = int(hs["S"][0])
        out.update(hub_S=sobs, hub_N_sus=int(hs["N_sus"][0]), hub_R=int(hs["R"][0]), pred_mu=mu,
                   p_ge_obs=float(1 - nbinom.cdf(sobs - 1, rr_, rr_ / (rr_ + mu))), hub_eligible=bool(hs["eligible"][0]))
    return out


def main():
    NAT.mkdir(parents=True, exist_ok=True)
    for name, fn in (("g26", g26), ("g31", g31), ("g40", g40), ("g30", g30)):
        res = fn()
        (NAT / f"{name}.json").write_text(json.dumps(res, indent=1, default=str))
        print(name, json.dumps(res, default=str)[:1500], flush=True)
    from h53lib import provenance
    provenance("analysis/natives.py", ["ground_truth_labels", "context_ledger_items", "call_windows", "project_states", "artifact_mentions", "H27 onsets_round1 (read-only)"], dict(natives=[26, 30, 31, 40]), "hypotheses/H53-announcement-nucleation/analysis/natives.py")


if __name__ == "__main__":
    main()
