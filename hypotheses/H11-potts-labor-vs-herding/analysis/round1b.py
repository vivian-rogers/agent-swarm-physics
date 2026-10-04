"""H11 round 1b (improved data, 2026-10-04): replication on the shared deterministic labels, the work-space version
of the coupling statistics, and the native tests (#26 per election round; #31 and #40 in work). Predictions were
written in the card ("Round 1b") and the period READMEs before this script was run.

  uv run python hypotheses/H11-potts-labor-vs-herding/analysis/round1b.py replicate   # 17 round-1 periods, shared labels
  uv run python hypotheses/H11-potts-labor-vs-herding/analysis/round1b.py work        # attention vs work, #30 onward
  uv run python hypotheses/H11-potts-labor-vs-herding/analysis/round1b.py g26         # #26 per election round (DQ6)
  uv run python hypotheses/H11-potts-labor-vs-herding/analysis/round1b.py assemble    # verdicts, cross-period, estimates

Reads data/processed/H11-potts-labor-vs-herding/r1b/ (scheme/build_r1b.py); writes there:
  G<NN>/round1b.json, local_shift_r1b.json, verdicts_round1b.parquet, cross_period_round1b.json,
  work_vs_attention_r1b.parquet / .json, g26_rounds_r1b.json. No text is read except none (codes only).
"""
from __future__ import annotations

import os

os.environ["H11_LABELS"] = "shared"          # round 1b uses the shared labels; spawned workers inherit this

import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
from multiprocessing import Pool  # noqa: E402
from pathlib import Path  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h11common as HC  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import potts_core as P  # noqa: E402
import explore as X  # noqa: E402
from h11data import load_period, blocks_ge  # noqa: E402

R1B = HC.OUT / "r1b"
ALLC = {**HC.CANDIDATES, **HC.TRANSFER}
PERIODS_R1 = sorted(ALLC)
WORK_GOALS = [30, 31, 33, 35, 37, 38, 39, 40, 41, 42, 44]
OWN_ARTIFACT = {39, 40, 42}                     # round 1's own-artifact weeks (post hoc class, frozen in round 1)
NNULL = 99


def jdump(obj, f: Path):
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(obj, indent=1, default=lambda x: None if (isinstance(x, float) and not math.isfinite(x))
                            else (x.item() if hasattr(x, "item") else str(x))))


def units_51() -> list[tuple[str, list[str]]]:
    """Non-holdout #51 period units with >= 3 active label days (unit of analysis: a period split at step changes)."""
    pu = pl.read_parquet(HC.SHARED / "period_units.parquet").filter((pl.col("goal_no") == 51) & ~pl.col("holdout")).sort("seq")
    wins = pl.read_parquet(R1B / "G51" / "windows_w30.parquet")
    have = set(wins["pt_date"].unique().to_list())
    out = []
    for r in pu.iter_rows(named=True):
        d = sorted(set(r["days"]) & have)
        if len(d) >= 3:
            out.append((r["unit_id"], d))
    return out


# ============================================================================================ replication
def replicate_job(args):
    g, nnull = args
    R = X.analyze((g, nnull))
    if R.get("tested"):
        rng = np.random.default_rng(777 + g)
        s, _ = load_period(g)
        obs = P.fit_pl(s, "agent")["bj"]
        nl = [P.fit_pl(P.shift_snap(s, rng, max_shift=1), "agent")["bj"] for _ in range(nnull)]
        z, p, m, sd = X.zscore(obs, nl)
        R["local1"] = dict(z=z, mean=m, sd=sd)
    jdump(R, R1B / f"G{g:02d}" / "round1b.json")
    return g, R.get("tested"), (R["O1"]["bj"] if R.get("tested") else None)


def replicate(nnull=NNULL):
    with Pool(2) as pool:
        for g, tested, bj in pool.imap_unordered(replicate_job, [(g, nnull) for g in PERIODS_R1]):
            print(f"G{g:02d} tested={tested} bj_cw={bj}", flush=True)


# ============================================================================================ work vs attention
def cowork(s) -> tuple[float, int]:
    """Share of labelled agents (blocks with N >= 2) whose state is held by >= 1 block-mate; raw-label snaps.
    Returns (rate, peak count of one state in one block)."""
    m = s.N >= 2
    c = s.counts[m][:, s.coupled]
    shared = (c * (c >= 2)).sum()
    return float(shared / max(s.N[m].sum(), 1)), int(s.counts[:, s.coupled].max()) if s.counts.size else 0


def ownership(df) -> float:
    d = df.filter(pl.col("project").is_not_null())
    c = d.group_by("project", "agent").agg(pl.len().alias("n"))
    t = c.group_by("project").agg(pl.col("n").sum().alias("tot"), pl.col("n").max().alias("top"))
    t = t.with_columns((pl.col("top") / pl.col("tot")).alias("own"))
    return float(t.filter(pl.col("own") >= 0.8)["tot"].sum() / max(t["tot"].sum(), 1))


def space_stats(g, state, nnull, pt_dates=None, seed=0):
    rng = np.random.default_rng(seed)
    s, df = load_period(g, state=state, pt_dates=pt_dates)
    R = dict(state=state, n_obs=int(len(s.label)), n_agents=int(s.n_agents), n_days=int(s.n_days), blocks3=blocks_ge(s, 3),
             q=int(s.S - 1), other_frac=float((s.label == 0).mean()) if len(s.label) else np.nan,
             own=ownership(df) if df.height else np.nan)
    if len(s.label) == 0:
        R["tested"] = False
        return R
    sr, _ = load_period(g, state=state, variant="raw", pt_dates=pt_dates)
    cw_obs, peak = cowork(sr)
    cn = [cowork(P.shift_snap(sr, rng))[0] for _ in range(nnull)]
    z, p, m, sd = X.zscore(cw_obs, cn)
    R["cowork"] = dict(rate=cw_obs, N2_mean=m, z_N2=z, excess=cw_obs - m if m == m else np.nan, peak_block=peak)
    R["tested"] = R["blocks3"] >= X.MIN_BLOCKS3
    if R["blocks3"] < 5:
        return R
    o = np.lexsort((s.win, s.day, s.agent))
    a_, d_, w_, l_ = s.agent[o], s.day[o], s.win[o], s.label[o]
    nxt = (a_[1:] == a_[:-1]) & (d_[1:] == d_[:-1]) & (w_[1:] == w_[:-1] + 1)
    R["persist"] = float((l_[1:][nxt] == l_[:-1][nxt]).mean()) if nxt.any() else np.nan
    R["O1"] = X.cw_block(s)
    bj_pl = P.fit_pl(s, "agent")["bj"]
    R["O2"] = dict(bj=bj_pl)
    for nm, gen in (("N2", lambda: P.shift_snap(s, rng)), ("N1d", lambda: s.with_labels(P.null_labels(s, "perm_day", rng))),
                    ("local1", lambda: P.shift_snap(s, rng, max_shift=1))):
        nl = [P.fit_pl(gen(), "agent")["bj"] for _ in range(nnull)]
        z, p, m, sd = X.zscore(bj_pl, nl)
        R["O2"].update({f"z_{nm}": z, f"{nm}_mean": m})
    R["O2"]["excess"] = bj_pl - R["O2"]["N2_mean"] if R["O2"]["N2_mean"] is not None else np.nan
    R["O3"] = dict(zip(("R", "obs", "exp"), X.agreement_ratio(s)))
    R["O7"] = X.heldout_pl(s)
    return R


def agreement(g, pt_dates=None) -> dict:
    """Agent-windows labelled in both spaces: does the work repo equal the attention project? Also hub shares."""
    a = pl.read_parquet(R1B / f"G{g:02d}" / "labels_project_w30.parquet")
    w = pl.read_parquet(R1B / f"G{g:02d}" / "labels_work_w30.parquet")
    if pt_dates is not None:
        a = a.filter(pl.col("pt_date").is_in(pt_dates))
        w = w.filter(pl.col("pt_date").is_in(pt_dates))
    j = a.join(w, on=["pt_date", "win", "agent"], suffix="_w")
    top_a = a.group_by("project").len().sort(["len", "project"], descending=[True, False])
    top_w = w.group_by("project").len().sort(["len", "project"], descending=[True, False])
    hub = top_a["project"][0] if top_a.height else None
    return dict(n_both=j.height, same_project=float((j["project"] == j["project_w"]).mean()) if j.height else np.nan,
                frac_work_windows_with_attention=float(j.height / max(w.height, 1)),
                attention_top=hub, attention_top_share=float(top_a["len"][0] / a.height) if a.height else np.nan,
                work_share_of_attention_top=float(w.filter(pl.col("project") == hub).height / max(w.height, 1)) if hub else np.nan,
                work_top_is_attention_top=bool(top_w.height and top_w["project"][0] == hub),
                work_top_share=float(top_w["len"][0] / w.height) if w.height else np.nan)


def work_job(args):
    unit, g, days, nnull = args
    seed = 11000 + g * 100 + (0 if days is None else len(days))
    out = dict(unit=unit, goal=g, days=days)
    for state in ("project", "work"):
        out[state] = space_stats(g, state, nnull, days, seed)
    out["agree"] = agreement(g, days)
    jdump(out, R1B / "work" / f"{unit}.json")
    return unit


def work(nnull=NNULL):
    jobs = [(f"G{g:02d}", g, None, nnull) for g in WORK_GOALS]
    jobs += [(u, 51, d, max(nnull // 2, 49)) for u, d in units_51()]
    with Pool(2) as pool:
        for u in pool.imap_unordered(work_job, jobs):
            print("done", u, flush=True)


# ============================================================================================ #26 per round
def snapshot_bj(counts, q):
    """Profile likelihood of the symmetric-field Curie-Weiss Potts on one snapshot (H11 explore.votes_g26 logic)."""
    nvec = np.array(sorted(counts, reverse=True) + [0] * (q - len(counts)))
    Nn = int(nvec.sum())
    grid = np.linspace(-10, 15, 501)
    coupled = np.ones(q, bool)
    ll = []
    for bj in grid:
        snap = P.Snap(np.arange(Nn), np.repeat(np.arange(q), nvec), np.zeros(Nn, int), np.zeros(Nn, int), q, coupled)
        gC = P.CWGroups(snap, "period")
        gC.present[:] = True
        gC.free[:] = True
        gC.free[0, gC.ref[0]] = False
        gC.n_par = 1 + int(gC.free.sum())
        th = np.zeros(gC.n_par)
        th[0] = bj
        ll.append(-gC.negll(th, ridge=0.0)[0])
    ll = np.array(ll)
    i = int(np.argmax(ll))
    ci = grid[ll >= ll[i] - 1.92]
    rng = np.random.default_rng(26)
    sims = rng.multinomial(Nn, np.ones(q) / q, size=400000).max(1)
    return dict(q=q, counts=nvec.tolist(), N=Nn, bj_mle=float(grid[i]), bj_ci=[float(ci.min()), float(ci.max())],
                mle_at_bound=bool(i == len(grid) - 1), bj_s=P.bj_spinodal(q) if q >= 3 else 2.0,
                p_max_indep=float((sims >= nvec.max()).mean()))


def ballot_calls(b: pl.DataFrame) -> pl.DataFrame:
    """The voter's call that cast each ballot: a talk call whose logged span contains the ballot message time."""
    cw = pl.scan_parquet(HC.SHARED / "call_windows.parquet").filter(pl.col("goal_no") == 26).select(
        "turn_id", "agent", "t_call", "t_first", "t_log", "talk").collect()
    rows = []
    for r in b.iter_rows(named=True):
        c = cw.filter((pl.col("agent") == r["voter"]) & (pl.col("t_first") <= r["t"] + pl.duration(seconds=2))
                      & (pl.col("t_log") >= r["t"] - pl.duration(seconds=2))).sort(pl.col("talk"), descending=True)
        if c.height == 0:   # fall back to the last call starting before the message
            c = cw.filter((pl.col("agent") == r["voter"]) & (pl.col("t_call") <= r["t"])).sort("t_call", descending=True)
        rows.append(dict(message_id=r["message_id"], turn_id=int(c["turn_id"][0]), t_call=c["t_call"][0]))
    return pl.DataFrame(rows)


def g26():
    b = pl.read_parquet(R1B / "G26" / "ballots.parquet")
    ph = pl.read_parquet(R1B / "G26" / "phases.parquet")
    chat = pl.scan_parquet(HC.SHARED / "chat_core.parquet").filter(pl.col("goal_no") == 26).select(
        "message_id", "t", "speaker_kind", "agent").collect()
    men = pl.read_parquet(HC.SHARED / "chat_mentions_clean.parquet", columns=["message_id", "mentions_roster"])
    chat = chat.join(men, on="message_id", how="left")
    items = pl.scan_parquet(HC.SHARED / "context_ledger_items.parquet").select("turn_id", "message_id").collect()
    turns = pl.scan_parquet(HC.SHARED / "context_ledger_turns.parquet").filter(pl.col("goal_no") == 26).select(
        "turn_id", "agent", "t_call").collect()
    items = items.join(turns, on="turn_id", how="inner")
    ballot_ids = set(b["message_id"].to_list())
    out = {}
    tal = ph.filter(pl.col("label_kind") == "tally")
    out["tallies"] = {u: {int(a): int(v) for a, v in zip(d["agent"].to_list(), d["value"].to_list())}
                      for (u,), d in tal.group_by(["unit"], maintain_order=True)}
    # N26-a: symmetric point
    ap = b.filter(pl.col("round") == "approval")
    sets = ap.group_by("voter").agg(pl.col("candidate").sort())
    top3 = [0, 6, 17]
    out["N26a"] = dict(n_voters=sets.height, all_approve_top3=int(sum(set(top3) <= set(x) for x in sets["candidate"].to_list())),
                       approvals={int(k): int(v) for k, v in ap.group_by("candidate").len().iter_rows()})
    # N26-b/c per round
    for rnd, q in (("runoff", 3), ("confirmatory", 2)):
        d = b.filter(pl.col("round") == rnd).sort("t")
        cnt = d.group_by("candidate").len().sort("len", descending=True)
        counts = cnt["len"].to_list()
        win = int(cnt["candidate"][0])
        t0 = ph.filter((pl.col("label_kind") == "phase") & (pl.col("value") == ("runoff" if rnd == "runoff" else "confirmatory_vote"))
                       & pl.col("preferred"))["t_valid_from"][0]
        traj, k = [], 0
        for i, c in enumerate(d["candidate"].to_list()):
            k += int(c == win)
            traj.append(dict(n=i + 1, share=k / (i + 1), t_s=(d["t"][i] - t0).total_seconds()))
        out[rnd] = dict(winner=win, counts=counts, share_final=counts[0] / sum(counts), start_share=1 / q,
                        jump=counts[0] / sum(counts) - 1 / q, span_s=(d["t"][-1] - d["t"][0]).total_seconds(),
                        first_ballot_after_open_s=(d["t"][0] - t0).total_seconds(), trajectory=traj,
                        snapshot=snapshot_bj(counts, q))
    # N26-d: visible earlier ballots and the visible candidate field at each ballot call
    t_tally = ph.filter((pl.col("label_kind") == "tally") & (pl.col("unit") == "approval"))["t_valid_from"][0]
    t_first_appr = ap["t"].min()
    for rnd in ("runoff", "confirmatory"):
        d = b.filter(pl.col("round") == rnd).sort("t")
        bc = ballot_calls(d)
        d = d.join(bc, on="message_id")
        same_round = d.select("message_id", pl.col("t").alias("t_b"))
        rows = []
        for r in d.iter_rows(named=True):
            vis = items.filter((pl.col("agent") == r["voter"]) & (pl.col("t_call") <= r["t_call"]))
            vis = vis.join(chat.select("message_id", pl.col("t").alias("t_msg"), "speaker_kind", "mentions_roster"), on="message_id")
            seen_b = vis.join(same_round, on="message_id").filter(pl.col("t_b") < r["t"])
            seen_win = int(seen_b.join(d.select("message_id", "candidate"), on="message_id").filter(pl.col("candidate") == out[rnd]["winner"]).height)
            row = dict(voter=int(r["voter"]), candidate=int(r["candidate"]), t_s=(r["t"] - d["t"][0]).total_seconds(),
                       call_lag_s=(r["t"] - r["t_call"]).total_seconds(), earlier_ballots=int(d.filter(pl.col("t") < r["t"]).height),
                       seen_earlier=int(seen_b.height), seen_earlier_for_winner=seen_win)
            if rnd == "runoff":
                for nm, t_lo in (("tally", t_tally), ("approval", t_first_appr)):
                    f = vis.filter((pl.col("t_msg") >= t_lo) & ~pl.col("message_id").is_in(list(ballot_ids)))
                    cnt = {c: int(sum(c in (m or []) for m in f["mentions_roster"].to_list())) for c in top3}
                    row[f"field_{nm}"] = cnt
                    row[f"field_{nm}_n_msgs"] = f.height
                    best = max(cnt.values())
                    row[f"field_{nm}_leader"] = (max(cnt, key=cnt.get) if best > 0 and list(cnt.values()).count(best) == 1 else None)
            rows.append(row)
        win = out[rnd]["winner"]
        r0 = [x for x in rows if x["seen_earlier"] == 0]
        out[rnd]["visibility"] = dict(
            ballots=rows, n=len(rows), n_seen_le1=int(sum(x["seen_earlier"] <= 1 for x in rows)),
            n_seen0=len(r0), winner_share_seen0=(sum(x["candidate"] == win for x in r0) / len(r0)) if r0 else None,
            winner_share_seen_ge1=(sum(x["candidate"] == win for x in rows if x["seen_earlier"] >= 1)
                                   / max(sum(x["seen_earlier"] >= 1 for x in rows), 1)),
            mean_seen=float(np.mean([x["seen_earlier"] for x in rows])))
        if rnd == "runoff":
            for nm in ("tally", "approval"):
                out[rnd]["visibility"][f"n_field_{nm}_leader_is_winner"] = int(sum(x.get(f"field_{nm}_leader") == win for x in rows))
    jdump(out, R1B / "g26_rounds_r1b.json")
    print(json.dumps({k: (v if k in ("tallies", "N26a") else {kk: vv for kk, vv in v.items() if kk not in ("trajectory",)})
                      for k, v in out.items()}, indent=1, default=str)[:6000])


# ============================================================================================ assemble
def _g(R, *ks):
    x = R
    for k in ks:
        if not isinstance(x, dict) or k not in x or x[k] is None:
            return np.nan
        x = x[k]
    return x


def assemble():
    import assemble as A
    old = {json.loads(f.read_text())["goal"]: json.loads(f.read_text()) for f in HC.OUT.glob("G*/round1.json")}
    new = {json.loads(f.read_text())["goal"]: json.loads(f.read_text()) for f in R1B.glob("G*/round1b.json")}
    LS = {int(k): v for k, v in json.loads((HC.OUT / "local_shift_posthoc.json").read_text()).items()}
    rows = []
    for g in sorted(new):
        R, O = new[g], old.get(g, {})
        row = dict(goal=g, cls=R["cls"], tested=bool(R.get("tested")), blocks3=R["blocks3"], q=R["q"], q_old=O.get("q"))
        if R.get("tested"):
            s, df = load_period(g)
            own = ownership(df)
            row.update(bj_cw=R["O1"]["bj"], se_cw=R["O1"]["se"], t_cw=R["O1"]["t"], tcrit=R["O1"]["tcrit"], z_cw_N1=R["O1"]["z_N1"],
                       bj_pl=R["O2"]["bj"], z_N2=R["O2"]["z_N2"], z_N1d=R["O2"]["z_N1d"], excess=R["O2"]["bj"] - R["O2"]["N2_mean"],
                       z_loc1=_g(R, "local1", "z"), R=R["O3"]["R"], act_bj=R["O6"]["bj_cw"], act_t=R["O6"]["t_cw"],
                       dll_pos=R["O7"].get("dll_pos"), folds=R["O7"].get("folds"), jump=R["O45"].get("verdict"), own=own,
                       p1=A.p1_verdict(R["cls"], R["O1"]), p2=A.p2_verdict(R["cls"], R["O2"]["z_N2"]),
                       bj_cw_old=_g(O, "O1", "bj"), t_cw_old=_g(O, "O1", "t"), z_N2_old=_g(O, "O2", "z_N2"),
                       z_loc1_old=LS.get(g, {}).get("z_local1", np.nan), dll_pos_old=_g(O, "O7", "dll_pos"),
                       p1_old=A.p1_verdict(O["cls"], O["O1"]) if O.get("tested") else None,
                       p2_old=A.p2_verdict(O["cls"], O["O2"]["z_N2"]) if O.get("tested") else None)
        rows.append(row)
    df = pl.DataFrame(rows, infer_schema_length=None)
    df.write_parquet(R1B / "verdicts_round1b.parquet")
    t = df.filter(pl.col("tested"))
    af = t.filter(pl.col("cls") == "AF")
    fm = t.filter(pl.col("cls").str.starts_with("FM"))
    pred = t.filter(~pl.col("cls").str.starts_with("none"))
    correct = int(((pred["cls"] == "AF") & (pred["bj_cw"] < 0)).sum() + ((pred["cls"] != "AF") & (pred["bj_cw"] > 0)).sum())
    shared = t.filter(~pl.col("goal").is_in(list(OWN_ARTIFACT)))
    cross = dict(
        n_tested=t.height, n_pos=int((t["bj_cw"] > 0).sum()),
        sign_correct=correct, sign_n=pred.height, sign_p=float(stats.binomtest(correct, pred.height, 0.5, alternative="greater").pvalue),
        mw_af_lt_fm_bjcw_p=float(stats.mannwhitneyu(af["bj_cw"], fm["bj_cw"], alternative="less").pvalue),
        mw_af_lt_fm_zN2_p=float(stats.mannwhitneyu(af["z_N2"], fm["z_N2"], alternative="less").pvalue),
        spearman_own_zN2=list(map(float, stats.spearmanr(t["own"], t["z_N2"]))),
        shared_weeks=shared.height, shared_zN2_ge2=int((shared["z_N2"] >= 2).sum()), shared_zloc_ge2=int((shared["z_loc1"] >= 2).sum()),
        same_sign_all=bool(((t["bj_cw"] > 0) == (t["bj_cw_old"] > 0)).all()),
        n_abs_dbj_le1=int(((t["bj_cw"] - t["bj_cw_old"]).abs() <= 1).sum()), max_abs_dbj=float((t["bj_cw"] - t["bj_cw_old"]).abs().max()),
        p1_same=int((t["p1"] == t["p1_old"]).sum()), p2_same=int((t["p2"] == t["p2_old"]).sum()),
        p3=None)
    # P3 on project labels (candidates with consensus, as in round 1)
    p3 = {}
    for g in (19, 26, 31, 40):
        R = new[g]
        o = R["O45"]
        p3a = (o.get("verdict") == "jump") and ((o.get("persistence_below_mid") or 1) <= 0.15)
        p3[g] = "supported" if (p3a and o.get("first_order_region")) else ("field-driven step" if p3a else "failed")
    cross["p3"] = p3
    cross["p4_act_af_vs_fm_p"] = float(stats.mannwhitneyu(af["act_bj"], fm["act_bj"], alternative="two-sided").pvalue)
    cross["p5_gain"] = [int(r["goal"]) for r in t.iter_rows(named=True) if r["folds"] and abs(r["z_N2"]) >= 2 and r["dll_pos"] / r["folds"] >= 0.8]
    cross["p5_n"] = int((t["z_N2"].abs() >= 2).sum())
    cross["p7_abs_lt2"] = int((t["bj_cw"].abs() < 2).sum())
    # work vs attention
    W = []
    for f in sorted((R1B / "work").glob("*.json")):
        d = json.loads(f.read_text())
        for st in ("project", "work"):
            R = d[st]
            W.append(dict(unit=d["unit"], goal=d["goal"], space="attention" if st == "project" else "work", n_obs=R["n_obs"],
                          blocks3=R["blocks3"], q=R["q"], own=R["own"], tested=bool(R.get("tested")),
                          bj_cw=_g(R, "O1", "bj"), se_cw=_g(R, "O1", "se"), t_cw=_g(R, "O1", "t"), tcrit=_g(R, "O1", "tcrit"),
                          bj_pl=_g(R, "O2", "bj"), z_N2=_g(R, "O2", "z_N2"), z_N1d=_g(R, "O2", "z_N1d"), z_loc1=_g(R, "O2", "z_local1"),
                          excess=_g(R, "O2", "excess"), R=_g(R, "O3", "R"), cowork=_g(R, "cowork", "rate"),
                          cowork_N2=_g(R, "cowork", "N2_mean"), cowork_z=_g(R, "cowork", "z_N2"), cowork_excess=_g(R, "cowork", "excess"),
                          peak=_g(R, "cowork", "peak_block"), dll_pos=_g(R, "O7", "dll_pos"), folds=_g(R, "O7", "folds"),
                          persist=_g(R, "persist"), same_project=d["agree"]["same_project"],
                          hub_share_att=d["agree"]["attention_top_share"], hub_share_work=d["agree"]["work_share_of_attention_top"]))
    wv = pl.DataFrame(W, infer_schema_length=None)
    wv.write_parquet(R1B / "work_vs_attention_r1b.parquet")
    a = wv.filter(pl.col("space") == "attention").drop("space")
    w = wv.filter(pl.col("space") == "work").drop("space")
    j = a.join(w, on=["unit", "goal"], suffix="_w")
    both = j.filter(pl.col("tested") & pl.col("tested_w"))
    sh = both.filter(~pl.col("goal").is_in(list(OWN_ARTIFACT)) & (pl.col("own") < 0.5))
    herd_att = sh.filter(pl.col("z_N2") >= 2)
    hh = dict(
        units_tested_both=both.height, shared_units=sh.height, shared_att_herd=herd_att.height,
        shared_att_herd_work_zN2_lt2=int((herd_att["z_N2_w"] < 2).sum()),
        shared_work_herd=int(((sh["bj_cw_w"] > 0) & (sh["z_N2_w"] >= 2)).sum()),
        excess_work_lt_att=int((both["excess_w"] < both["excess"]).sum()),
        cowork_excess_pos_att=int((sh["cowork_z"] >= 2).sum()), cowork_excess_pos_work=int((sh["cowork_z_w"] >= 2).sum()),
        median_same_project=float(j["same_project"].median()), min_same_project=float(j["same_project"].min()),
        own_units=both.filter(pl.col("goal").is_in(list(OWN_ARTIFACT)) | (pl.col("own") >= 0.5)).select("unit", "bj_cw_w", "z_N2_w").to_dicts())
    hh["hh266_supported"] = bool(herd_att.height and hh["shared_att_herd_work_zN2_lt2"] >= 2 / 3 * herd_att.height)
    hh["r1b2a_supported"] = bool(sh.height and hh["shared_work_herd"] >= sh.height / 2)
    cross["work"] = hh
    jdump(cross, R1B / "cross_period_round1b.json")
    pl.Config.set_tbl_rows(60)
    pl.Config.set_tbl_cols(30)
    pl.Config.set_tbl_width_chars(260)
    pl.Config.set_float_precision(2)
    print(df.select("goal", "cls", "blocks3", "bj_cw_old", "bj_cw", "t_cw", "z_N2_old", "z_N2", "z_loc1_old", "z_loc1", "own", "p1_old", "p1", "p2_old", "p2"))
    print(j.select("unit", "n_obs", "n_obs_w", "blocks3", "blocks3_w", "bj_cw", "bj_cw_w", "t_cw_w", "z_N2", "z_N2_w", "excess", "excess_w",
                   "cowork", "cowork_N2", "cowork_w", "cowork_N2_w", "cowork_z_w", "peak", "peak_w", "own", "own_w", "same_project"))
    print(json.dumps(cross, indent=1, default=float))
    write_estimates_r1b(t, j)


def write_estimates_r1b(t: pl.DataFrame, j: pl.DataFrame):
    sys.path.insert(0, str(HC.C.ROOT / "infra/shared"))
    import estimates as E
    pu = pl.read_parquet(HC.SHARED / "period_units.parquet")
    rows = []
    src = "data/processed/H11-potts-labor-vs-herding/r1b/"
    for r in t.iter_rows(named=True):
        g = int(r["goal"])
        R = json.loads((R1B / f"G{g:02d}" / "round1b.json").read_text())
        df_ = R["O1"]["df"]
        lo, hi = E.ci_from_se(r["bj_cw"], r["se_cw"], 0.95, df=df_)
        common = dict(period_unit=E.map_unit(g), goal_no=g, role="replication", source=src + f"G{g:02d}/round1b.json", post_hoc=False,
                      status="exploratory round 1b (shared deterministic labels)")
        rows.append(dict(common, statistic="potts_coupling_bJ_CW", channel="project", estimate=r["bj_cw"], ci_lo=lo, ci_hi=hi,
                         se=r["se_cw"], ci_kind="jackknife_z", n=R["n_days"], n_kind="days", null="betaJ=0 (independent interchangeable agents)",
                         method="exact finite-N Curie-Weiss Potts MLE, uniform period fields, room blocks, W=30, leave-one-day-out jackknife (round 1b)"))
        rows.append(dict(common, statistic="potts_coupling_beyond_fields_zN2", channel="project", estimate=r["z_N2"], ci_lo=None, ci_hi=None,
                         ci_kind="none", n=99, n_kind="null draws", null="N2 circular shift within agent-day",
                         method="pseudo-likelihood betaJ with agent fields, z vs 99 circular shifts (round 1b)"))
    for r in j.iter_rows(named=True):
        g = int(r["goal"])
        unit = r["unit"] if not r["unit"].startswith("G") else E.map_unit(g)
        for sp, sfx in (("project", ""), ("work", "_w")):
            if not r["tested" + sfx]:
                continue
            common = dict(period_unit=unit, goal_no=g, role="replication", source=src + f"work/{r['unit']}.json", post_hoc=False,
                          status="exploratory round 1b (work vs attention)")
            rows.append(dict(common, statistic="potts_coupling_beyond_fields_zN2_unit", channel=sp, estimate=r["z_N2" + sfx], ci_kind="none",
                             n=r["n_obs" + sfx], n_kind="labelled agent-windows", null="N2 circular shift within agent-day",
                             method="pseudo-likelihood betaJ with agent fields vs circular shifts; attention = strict artifact mentions, work = DQ4 agent work commits (round 1b)"))
            rows.append(dict(common, statistic="cowork_excess", channel=sp, estimate=r["cowork_excess" + sfx], ci_kind="none",
                             n=r["n_obs" + sfx], n_kind="labelled agent-windows", null="N2 circular shift within agent-day (mean subtracted)",
                             method="share of labelled agents sharing their raw project with >= 1 block-mate, minus the circular-shift mean (round 1b)"))
    # #26 native
    g26 = json.loads((R1B / "g26_rounds_r1b.json").read_text())
    for rnd in ("runoff", "confirmatory"):
        sn = g26[rnd]["snapshot"]
        rows.append(dict(period_unit=E.map_unit(26), goal_no=26, role="native", statistic=f"potts_snapshot_bJ_{rnd}", channel="ballots",
                         estimate=sn["bj_mle"], ci_lo=sn["bj_ci"][0], ci_hi=sn["bj_ci"][1], ci_kind="profile", n=sn["N"], n_kind="ballots",
                         null="independent symmetric voters", method=f"symmetric-field Curie-Weiss Potts profile likelihood on the DQ6 {rnd} tally (q={sn['q']})",
                         source=src + "g26_rounds_r1b.json", post_hoc=False, status="exploratory round 1b native"))
    E.write_estimates(rows, hypothesis="H11", replace_keys=("statistic", "channel", "method", "role"))
    print(f"estimates written: {len(rows)} rows")


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("replicate", "all"):
        replicate()
    if what in ("work", "all"):
        work()
    if what in ("g26", "all"):
        g26()
    if what in ("assemble", "all"):
        assemble()
