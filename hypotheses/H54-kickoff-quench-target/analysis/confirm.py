"""H54 confirmatory test on the LOCKED HOLDOUT. Written 2026-10-04 after exploratory round 1; NOT RUN.

Refuses to run on held-out data without:  --confirm --i-understand-this-uses-the-locked-holdout
Dry run (exploration data, stand-in targets, identical code path):  --dry-run

Predictions (frozen 2026-10-04, after exploration, before any holdout statistic):
  C1 (P1 transfer, primary): on the held-out kickoffs T1, the day-1 centroid identifies its own kickoff: median
     genericness-corrected own percentile >= 0.90, own kickoff top-1 in >= 50%, one-sided Wilcoxon p < 0.01.
     Decoys: every exploration-eligible kickoff plus the other held-out targets.
     Credence 0.75 (exploration: median 1.0, top-1 0.55; failures only where the kickoff names no shared target).
  C1b: targets whose kickoff names a shared object (not free / own-goal; i.e. all of T1 except #9) reach pi >= 0.9 in >= 75%.
  C2 (private-goal remanence, #51 tail 09-07 -> 09-20): role-swap accuracy >= 0.80 with permutation p < 0.01
     (exploration: 0.90-0.96 every week of the head). Credence 0.85.
  C3 (frozen = goal-named, own rule): pooled over held-out periods P3set, day-1 dominant projects (own rule on shared
     deterministic project_states) are named by the goal text with enrichment >= 2 over the period's candidate projects
     and Fisher one-sided p < 0.05 (exploration own rule: enrichment 2.68, p 0.001; H31 events: goal-text enrichment 3.2).
     Credence 0.5 (few dominant projects expected).
  C4 (HH180 re-quench): held-out mid-period human messages (>= 250 chars) move the room centroid toward themselves beyond
     decoy messages: median excess > 0 and sign test p < 0.05 (exploration: 57% positive, p 0.03). Credence 0.5.
  C5 (secondary, exploratory counter-finding): Spearman(S_emb, day-1 spread) < 0 on T1 (one-sided p < 0.10). Credence 0.4.
Target sets (reuse policy, hypotheses/holdout.md):
  T1 = held-out kickoffs {1, 9, 14, 15, 28, 29, 34, 43, 45, 46, 47, 48, 49, 50}. Excluded: #22, #32 (H10's confirmatory
     free -> assigned directions) and #23 (kept blind for H10). Reuse disclosed: #34 (H01/H05/H07/H12/H19/H21 confirm
     scripts), #45 (H02 activity timing; H23 message content), #28/#45 (H11 projects), #29/#46/#47/#50 (H31 E-P), #49
     (H31 E-C). H54's statistics (own-kickoff percentile among decoy kickoffs, goal-text naming of day-1 dominant
     projects, re-quench excess) are different statistics from all of these.
  P3set (C3 primary) = T1 minus H11/H31 project-statistic targets {28, 29, 45, 46, 47, 50}; the rest reported secondary.
Output: data/processed/H54-kickoff-quench-target/confirm/results.json (or confirm_dryrun.json).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys

import numpy as np
import polars as pl
from scipy import stats

import h54est as E
import h54lib as L

T1 = [1, 9, 14, 15, 28, 29, 34, 43, 45, 46, 47, 48, 49, 50]
FREE_T1 = [9]
P3SET_EXCL = {28, 29, 45, 46, 47, 50}
TAIL = ("2026-09-07", "2026-09-21")
STANDIN = {"T1": [30, 31, 33, 35, 36, 37, 38, 39, 40, 41, 42, 44, 51, 27], "free": [31, 37, 44, 51],
           "tail": ("2026-08-17", "2026-09-05"), "p3excl": {38, 40}}
RNG = np.random.default_rng(20261004)
UTC = dt.timezone.utc


def c1(st, Z, targets, decoy_pool, free):
    pool = sorted(set(decoy_pool) | set(targets))
    idx = {p: k for k, p in enumerate(pool)}
    Kb = {r: np.vstack([L.gvec(q, "kickoff", regime=r) for q in pool]) for r in ("I", "II", "III")}
    P = len(pool)
    S = np.full((P, P), np.nan)
    s = st.with_row_index("i").filter((pl.col("src_goal") == pl.col("goal_no")) & (pl.col("day") == 1) & ~pl.col("pre_kick"))
    spread = {}
    for p in pool:
        r = L.period_regime(p)
        g = s.filter(pl.col("goal_no") == p).group_by("agent").agg(pl.col("i"), pl.len().alias("n")).filter(pl.col("n") >= 3)
        if g.height < 3:
            continue
        V = np.vstack([E.unit(Z[np.asarray(ix)].mean(0)) for ix in g["i"].to_list()])
        S[idx[p]] = E.unit(V.mean(0)) @ Kb[r].T
        spread[p] = 1 - E.rarefied_q([Z[np.asarray(ix)] for ix in g["i"].to_list()], L.N_RARE, 50, RNG)
    Sh = E.colcenter(S)
    pi_all, t1_all = E.own_percentiles(Sh), E.top1(Sh)
    tk = [idx[p] for p in targets if np.isfinite(pi_all[idx[p]])]
    pi, t1 = pi_all[tk], t1_all[tk]
    v = E.p1_verdict(pi, t1)
    v["pass_rule"] = bool(v["median_pi"] >= 0.9 and v["top1"] >= 0.5 and v["p_wilcoxon"] < 0.01)
    v["per_target"] = {int(pool[k]): {"pi": float(pi_all[k]), "top1": float(t1_all[k])} for k in tk}
    shared = [idx[p] for p in targets if p not in free and np.isfinite(pi_all[idx[p]])]
    v["C1b_shared_rate_pi_ge_0.9"] = float(np.mean(pi_all[shared] >= 0.9)) if shared else None
    v["C1b_pass"] = bool(v["C1b_shared_rate_pi_ge_0.9"] is not None and v["C1b_shared_rate_pi_ge_0.9"] >= 0.75)
    # C5: S_emb vs spread on targets
    se = {p: float(1 - np.mean(np.delete(Kb[L.period_regime(p)] @ Kb[L.period_regime(p)][idx[p]], idx[p]))) for p in targets}
    xs = [se[p] for p in targets if p in spread]
    ys = [spread[p] for p in targets if p in spread]
    rho, pv, n = E.spearman(xs, ys, "less")
    c5 = {"rho": rho, "p_one": pv, "n": n, "pass": bool(np.isfinite(pv) and pv < 0.10 and rho < 0)}
    return v, c5


def c2(st, Z, window):
    G = L.goals().filter((pl.col("kind") == "agent_goal") & pl.col("valid_to").is_null())
    gt = pl.read_parquet(L.SHARED / "ground_truth_labels.parquet").filter(
        (pl.col("goal_no") == 51) & (pl.col("label_kind") == "role") & pl.col("preferred"))
    role_of = dict(zip(gt["agent"].to_list(), gt["value"].to_list()))
    s = st.with_row_index("i").filter((pl.col("goal_no") == 51) & (pl.col("src_goal") == 51)
                                      & (pl.col("pt_date") >= window[0]) & (pl.col("pt_date") < window[1]))
    g = s.group_by("agent").agg(pl.col("i"), pl.len().alias("n")).filter(pl.col("n") >= 5).sort("agent")
    gid = dict(zip(G["agent"].to_list(), G["gid"].to_list()))
    keep = [k for k, a in enumerate(g["agent"].to_list()) if a in gid]
    agents = [g["agent"][k] for k in keep]
    V = np.vstack([E.unit(Z[np.asarray(g["i"][k])].mean(0)) for k in keep])
    Gm = np.vstack([L.whiten_unit(L.goal_raw()[gid[a]][None], "III")[0] for a in agents])
    roles = [role_of.get(a, f"own{a}") for a in agents]
    ur = {x: i for i, x in enumerate(sorted(set(roles)))}
    rc = np.array([ur[x] for x in roles])
    acc, npairs = E.swap_pairs(V, Gm, rc)
    p = E.swap_perm_p(V, Gm, rc, n_perm=5000, rng=RNG)
    return {"window": list(window), "n_agents": len(agents), "n_pairs": npairs, "swap_accuracy": acc, "p_perm": p,
            "pass": bool(acc >= 0.8 and p < 0.01)}


def c3(projects, periods_primary, periods_all):
    out = {}
    for lab, ps in (("primary", periods_primary), ("all", periods_all)):
        d = projects.filter((pl.col("src") == "own") & pl.col("goal_no").is_in(ps) & pl.col("cls").is_in(["day1_dominant", "day1_scored"]))
        if d.height == 0:
            out[lab] = None
            continue
        t = E.naming_table(d["named_goal"].to_numpy(), (d["cls"] == "day1_dominant").to_numpy(), d["goal_no"].to_numpy(), 5000, RNG)
        t["periods"] = sorted(set(d["goal_no"].to_list()))
        t["pass"] = bool(t["n_frozen"] and t["enrichment"] >= 2 and t["p_fisher"] < 0.05)
        out[lab] = t
    return out


def c4(base, st, Z, periods):
    hm = pl.read_parquet(base / "human_msgs.parquet").filter(pl.col("goal_no").is_in(periods))
    pool = pl.read_parquet(base / "human_msgs.parquet")
    sti = st.with_row_index("i")
    rows = []
    for h in hm.iter_rows(named=True):
        p = h["goal_no"]
        r = L.period_regime(p)
        s = sti.filter((pl.col("goal_no") == p) & (pl.col("src_goal") == p) & (pl.col("day") >= 1))
        if r != "I":
            s = s.filter((pl.col("kind") == "chat") & (pl.col("room") == h["room"]))
        t = h["t"]

        def cen(a0, a1):
            w = s.filter((pl.col("t") >= t + dt.timedelta(minutes=a0)) & (pl.col("t") < t + dt.timedelta(minutes=a1))) if a0 < 0 else \
                s.filter((pl.col("t") > t + dt.timedelta(minutes=a0)) & (pl.col("t") <= t + dt.timedelta(minutes=a1)))
            g = w.group_by("agent").agg(pl.col("i"))
            if g.height < 3:
                return None
            return E.unit(np.vstack([E.unit(Z[np.asarray(ix)].mean(0)) for ix in g["i"].to_list()]).mean(0))
        cb, ca = cen(-60, 0), cen(0, 60)
        if cb is None or ca is None:
            continue
        dec = pool.filter((pl.col("goal_no") != p) & pl.col("goal_no").is_in([q for q in pool["goal_no"].unique().to_list() if L.period_regime(q) == r])
                          & (pl.col("length") >= h["length"] / 2) & (pl.col("length") <= h["length"] * 2))
        ids = dec["message_id"].to_list()
        if len(ids) < 3:
            continue
        ids = list(RNG.choice(ids, min(50, len(ids)), replace=False))
        EV = L.chat_vec([h["message_id"]] + ids, r)
        if not np.all(np.isfinite(EV[0])):
            continue
        D = EV[1:][np.all(np.isfinite(EV[1:]), axis=1)]
        rows.append(float((ca - cb) @ EV[0] - ((ca - cb) @ D.T).mean()))
    a = np.array(rows)
    if not len(a):
        return {"n": 0, "pass": False}
    ps = float(stats.binomtest(int((a > 0).sum()), len(a), 0.5, alternative="greater").pvalue)
    return {"n": len(a), "median_excess": float(np.median(a)), "pos_rate": float(np.mean(a > 0)), "p_sign": ps,
            "pass": bool(np.median(a) > 0 and ps < 0.05)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.dry_run:
        base = L.OUT
        targets, free, tail, p3excl = STANDIN["T1"], STANDIN["free"], STANDIN["tail"], STANDIN["p3excl"]
        decoys = [q for q in L.eligible() if q not in targets]
        out_name = "confirm_dryrun.json"
    elif a.confirm and a.ack:
        base = L.OUT / "confirm"
        subprocess.run([sys.executable, str(L.HYP / "scheme" / "build.py"), "--allow-holdout", "--out", str(base)], check=True)
        targets, free, tail, p3excl = T1, FREE_T1, TAIL, P3SET_EXCL
        decoys = L.eligible()
        out_name = "results.json"
    else:
        sys.exit("refusing: confirmatory run needs --confirm --i-understand-this-uses-the-locked-holdout (or use --dry-run)")
    st, Z, _ = L.load_stmt(base)
    res = {"mode": "dry-run (stand-ins)" if a.dry_run else "CONFIRMATORY", "targets": targets, "run_at": dt.datetime.now(UTC).isoformat()}
    res["C1"], res["C5"] = c1(st, Z, targets, decoys, free)
    res["C2"] = c2(st, Z, tail)
    projects = pl.read_parquet(base / "projects.parquet")
    res["C3"] = c3(projects, [p for p in targets if p not in p3excl], targets)
    res["C4"] = c4(base, st, Z, targets)
    (base if not a.dry_run else L.OUT).mkdir(parents=True, exist_ok=True)
    L.write_json((L.OUT / out_name) if a.dry_run else (base / out_name), res)
    print(json.dumps({k: (v if k != "C1" else {kk: vv for kk, vv in v.items() if kk != "per_target"}) for k, v in res.items()}, indent=1, default=str))


if __name__ == "__main__":
    main()
