"""H56 confirmatory test on the LOCKED HOLDOUT. Written 2026-10-04 after exploratory round 1; NOT RUN.

Refuses to run on the holdout without BOTH flags:  --confirm --i-understand-this-uses-the-locked-holdout
--dry-run runs exactly the same code on non-holdout regime-III stand-ins (round-1 data; numbers mean nothing).

Holdout targets (classes by the card's rule, from event_catalog.parquet rows with holdout0 = True):
  scaffold_tool / scaffold_prompt: changelog entries inside #22, #28, the NE12 and NE30 windows (incl. the NE14 rollout
    03-11 -> 03-13), and the NE21+NE23 window (06-01, 06-10/11 incl. the pause-default change, 06-29 GitLab, 07-01, 07-03)
  scaffold_family: NE20 (06-03, Anthropic one tool call per turn; 06-02 history rebuild), 07-02 (Anthropic)
  goal: kickoffs #9, #14, #15, #22, #28, #29, #32, #34, #43, #45-#50
  operator: NE23 nudger off (06-13) / on (06-15), NE35, NE37
  roster / room: holdout joins and structural room changes
Same pipeline as round 1 (states V1, V5; within-agent count-matched Newton; k = 3; min 100 transitions; >= 4 agents;
Amendment-3 null = holdout days of the same regime > 2 days from same-class events). Window days may include
non-holdout neighbours (e.g. #45's pre-window in #44); that is disclosed, not avoided.

Frozen criteria (exploratory basis in brackets):
  C1 H56 core, scaffold_tool on V1: class mean |t| vs the random-date null.  H56 CONFIRMED if p < 0.05 AND hit rate
     >= 0.30; REFUTATION CONFIRMED if p > 0.20 AND hit rate <= 0.10; otherwise inconclusive.  [p 0.23, hits 0/17]
  C2 NE20 family DiD (Anthropic vs others, V1): |t_DiD| above the 95th percentile of the same split at N2 days.
     H56 predicts a hit (the strongest single-family harness change).                    [no family event testable]
  C3 R1 task mix vs scaffold: goal-class mean |t| >= scaffold_tool mean |t| on V5.        [1.23 vs 1.14]
  C4 R4 agent signature: stratified family eta2 test on V5 over holdout periods #45, #46, #47, #49, #50, p < 0.05.
     [V5 p 0.0005, mean eta2 0.40]
  C5 NE23 nudger off/on (operator): no jump, p > 0.05 on V1 for both dates.               [NE43 p 0.38-0.89]
  C6 post hoc lead (sign synchrony S = |f+ - 0.5|) at scaffold_tool events > random-date null, p < 0.05.
     [V1 p 0.047, V5 p 0.013; post hoc in round 1]
Verdict: H56 is confirmed only if C1 (confirmed) and C2 pass; it stays refuted if C1 gives "refutation confirmed".
C3-C6 are reported either way.

Reuse disclosure: H14's unrun confirm script also targets #45-#47, #49, #50 with action-class EP *levels* (per-agent
arrows, regime contrast). H56 computes *changes* at step dates and a family contrast on the agent-only chain: a
different statistic on the same modality. Both cards and LOG.md must disclose the reuse before either runs.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import event_study as ES  # noqa: E402
import h56lib as L  # noqa: E402

V1, V5 = "act_all", "act_agent_b3"
STANDIN_GOALS = [37, 38, 39, 40, 41, 42, 44]        # regime-III non-holdout stand-ins (dry run)
HOLDOUT_FAMILY_PERIODS = [45, 46, 47, 49, 50]


class ConfirmData(ES.Data):
    """Same arrays as ES.Data, but over a chosen list of active days (holdout included in confirm mode)."""

    def __init__(self, counts, days_df, use_dates):
        self.days = days_df
        dd = days_df.filter(pl.col("pt_date").is_in(use_dates)).sort("pt_date")
        self.nh_dates = dd["pt_date"].to_list()
        self.nh_regime = dd["regime"].to_list()
        self.nh_weekday = dd["weekday"].to_list()
        self.nh_goal = dd["goal_no"].to_list()
        self.is_holdout = dd["holdout"].to_list()
        self.nd = len(self.nh_dates)
        self.idx_of = {d: i for i, d in enumerate(self.nh_dates)}
        roster = pl.read_parquet(L.DATA.parent / "shared/roster.parquet")
        self.lab = dict(zip(roster["agent"].to_list(), roster["lab"].to_list()))
        self.name = dict(zip(roster["agent"].to_list(), roster["name"].to_list()))
        self.n_agents = 46
        self.C = []
        for vi, q in enumerate(L.QV):
            arr = np.zeros((self.n_agents, self.nd, 4, q, q), dtype=np.int32)
            cv = counts.filter((pl.col("variant") == vi) & pl.col("pt_date").is_in(self.nh_dates))
            di = np.array([self.idx_of[d] for d in cv["pt_date"].to_list()], dtype=np.int64)
            np.add.at(arr, (cv["agent"].to_numpy(), di, cv["block"].to_numpy(), cv["a"].to_numpy(), cv["b"].to_numpy()),
                      cv["n"].to_numpy())
            self.C.append(arr)
        self.Cday = [a.sum(2) for a in self.C]
        self.ntr = [a.sum((2, 3)) for a in self.Cday]


def stat_at(D, d, v, rng, agents=None, allow_cross=False):
    w = D.windows(d, allow_cross=allow_cross)
    if w is None:
        return None, None
    vi = L.VARIANTS.index(v)
    st, rows = ES.window_stat(D, vi, w[0], w[1], rng, agents=agents, est=("newton",))
    return st["newton"], rows


def run(mode, out_dir):
    rng = np.random.default_rng(20261010)
    days = pl.read_parquet(L.DATA / "days.parquet")
    ev = pl.read_parquet(L.DATA / "event_catalog.parquet")
    if mode == "confirm":
        import build as B  # scheme builder; include_holdout only in memory, never written
        counts, _, _ = B.build_counts(days, include_holdout=True)
        use_dates = days["pt_date"].to_list()
        D = ConfirmData(counts, days, use_dates)
        target_day = {d: h for d, h in zip(D.nh_dates, D.is_holdout)}
        targets = ev.filter(pl.col("holdout0").fill_null(False) & pl.col("cls").is_in(ES.TESTED + ["operator"]))
        fam_periods = HOLDOUT_FAMILY_PERIODS
    else:
        counts = pl.read_parquet(L.DATA / "counts.parquet")
        use_dates = days.filter(~pl.col("holdout"))["pt_date"].to_list()
        D = ConfirmData(counts, days, use_dates)
        target_day = {d: g in STANDIN_GOALS for d, g in zip(D.nh_dates, D.nh_goal)}
        targets = ev.filter(~pl.col("holdout0").fill_null(True) & pl.col("goal0").is_in(STANDIN_GOALS)
                            & pl.col("cls").is_in(ES.TESTED + ["operator"]))
        fam_periods = STANDIN_GOALS
    # statistic at every target-pool day (pool = days flagged as targets, i.e. holdout days in confirm mode)
    pool_rows = []
    for d in range(D.nd):
        if not target_day[D.nh_dates[d]]:
            continue
        for v in (V1, V5):
            st, rows = stat_at(D, d, v, rng)
            if st is None or st["n"] < ES.MIN_AGENTS:
                continue
            pool_rows.append({"nidx": d, "pt_date": D.nh_dates[d], "regime": D.nh_regime[d], "weekday": D.nh_weekday[d],
                              "variant": v, "newton_t": st["t"], "newton_fpos": st["fpos"], "agents": rows})
    pool = pl.DataFrame([{k: r[k] for k in r if k != "agents"} for r in pool_rows])
    ev_rows = []
    for r in targets.iter_rows(named=True):
        d = D.idx_of.get(r["day0"])
        if d is None:
            continue
        for v in (V1, V5):
            m = [x for x in pool_rows if x["nidx"] == d and x["variant"] == v]
            if not m:
                continue
            ev_rows.append({"ref": r["ref"], "cls": r["cls"], "family_target": r["family_target"], "nidx": d,
                            "regime": D.nh_regime[d], "weekday": D.nh_weekday[d], "variant": v,
                            "t": m[0]["newton_t"], "fpos": m[0]["newton_fpos"], "agents": m[0]["agents"]})
    res = {"mode": mode, "n_pool_days": int(pool.filter(pl.col("variant") == V1).height) if pool.height else 0,
           "n_events": len(ev_rows)}

    def cls_test(cls, v, col="t", f=np.abs):
        ee = [x for x in ev_rows if x["cls"] == cls and x["variant"] == v and np.isfinite(x[col])]
        if not ee or pool.height == 0:
            return None
        cls_days = [x["nidx"] for x in ev_rows if x["cls"] == cls]
        obs = float(np.mean([f(x[col] if col == "t" else x["fpos"] - 0.5) for x in ee]))
        pools, hits = [], 0
        for x in ee:
            pp = pool.filter((pl.col("variant") == v) & (pl.col("regime") == x["regime"]) & ~pl.col("nidx").is_in(cls_days))
            vals = f(pp["newton_t"].to_numpy() if col == "t" else pp["newton_fpos"].to_numpy() - 0.5)
            pools.append(vals)
            if col == "t" and len(vals):
                hits += ((1 + (vals >= abs(x["t"])).sum()) / (1 + len(vals))) < 0.05
        draws = np.array([np.mean([p[rng.integers(len(p))] for p in pools if len(p)]) for _ in range(5000)])
        return {"n": len(ee), "mean": obs, "p": float((1 + (draws >= obs).sum()) / 5001), "hit_rate": hits / len(ee)}

    c1 = cls_test("scaffold_tool", V1)
    res["C1"] = c1
    if c1:
        res["C1"]["verdict"] = ("H56 confirmed" if (c1["p"] < 0.05 and c1["hit_rate"] >= 0.30) else
                                "refutation confirmed" if (c1["p"] > 0.20 and c1["hit_rate"] <= 0.10) else "inconclusive")
    # C2 NE20 family DiD (dry run: stand-in = the 03-26 Anthropic entry is outside the stand-ins; uses any family event)
    fam = [x for x in ev_rows if x["cls"] == "scaffold_family" and x["variant"] == V1]
    c2 = []
    for x in fam:
        tg = x["family_target"]
        isT = np.array([ES.is_target(D, a["agent"], tg) for a in x["agents"]])
        dl = np.array([a["newton_post"] - a["newton_pre"] for a in x["agents"]])
        if isT.sum() < 2 or (~isT).sum() < 2:
            c2.append({"ref": x["ref"], "testable": False})
            continue
        t = L.did_stats(dl[isT], dl[~isT])["t"]
        nulls = []
        for prow in [r for r in pool_rows if r["variant"] == V1 and abs(r["nidx"] - x["nidx"]) > 2]:
            iT = np.array([ES.is_target(D, a["agent"], tg) for a in prow["agents"]])
            dd = np.array([a["newton_post"] - a["newton_pre"] for a in prow["agents"]])
            if iT.sum() >= 2 and (~iT).sum() >= 2:
                nulls.append(abs(L.did_stats(dd[iT], dd[~iT])["t"]))
        q95 = float(np.nanpercentile(nulls, 95)) if nulls else None
        c2.append({"ref": x["ref"], "t_did": float(t), "null_q95": q95, "pass": bool(q95 is not None and abs(t) > q95)})
    res["C2"] = c2
    g, s = cls_test("goal", V5), cls_test("scaffold_tool", V5)
    res["C3"] = {"goal_mean_abs_t": g["mean"] if g else None, "scaffold_tool_mean_abs_t": s["mean"] if s else None,
                 "R1_wins": bool(g and s and g["mean"] >= s["mean"])}
    # C4 family eta2 on V5 over the family periods
    h = L.h14()
    vi = L.VARIANTS.index(V5)
    recs = []
    for gno in fam_periods:
        didx = [i for i, gg in enumerate(D.nh_goal) if gg == gno]
        if len(didx) < 2:
            continue
        nt = D.ntr[vi][:, didx]
        ag = [a for a in range(D.n_agents) if nt[a].sum() >= 300 and (nt[a] > 0).sum() >= 2]
        if len(ag) < 3:
            continue
        m = int(min(nt[a].sum() for a in ag))
        vals = {a: float(np.nanmean([L.newton_counts(L.stratified_subsample(D.Cday[vi][a, [i for i in didx if D.ntr[vi][a, i] > 0]], m, rng))
                                     for _ in range(ES.R)])) for a in ag}
        labs = [D.lab[a] for a in ag]
        keep = [i for i, a in enumerate(ag) if labs.count(labs[i]) >= 2 and labs[i] not in ES.FAMILY_EXCLUDE]
        if len({labs[i] for i in keep}) < 2:
            continue
        recs.append((np.array([vals[ag[i]] for i in keep]), np.array([labs[i] for i in keep])))
    if recs:
        obs = sum(h.eta2(x, lb) for x, lb in recs)
        null = [sum(h.eta2(x, rng.permutation(lb)) for x, lb in recs) for _ in range(2000)]
        res["C4"] = {"periods": len(recs), "mean_eta2": obs / len(recs), "p": float((1 + (np.array(null) >= obs).sum()) / 2001)}
    # C5 operator (NE23 off/on in confirm mode; NE43-free stand-ins in the dry run)
    res["C5"] = [{"ref": x["ref"], "t": x["t"]} for x in ev_rows if x["cls"] == "operator" and x["variant"] == V1]
    res["C5_class"] = cls_test("operator", V1)
    # C6 sign synchrony
    res["C6"] = {v: cls_test("scaffold_tool", v, col="fpos") for v in (V1, V5)}
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "results.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res, indent=1, default=float))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.dry_run:
        run("dry", L.DATA / "confirm_dryrun")
        return
    if not (a.confirm and a.ack):
        sys.exit("Refusing: the confirmatory run needs --confirm --i-understand-this-uses-the-locked-holdout "
                 "(and Vivian's sign-off). Use --dry-run to test the code on non-holdout stand-ins.")
    run("confirm", L.DATA / "confirm")


if __name__ == "__main__":
    main()
