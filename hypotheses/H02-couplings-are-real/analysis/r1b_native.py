"""H02 round 1b period-native tests (2026-10-04; predictions in the period READMEs, written before these runs).

g12   #12 debate tournament: a relation-structured kinetic Ising on 1-min talk spins inside the 10 debate windows
      (DQ6 team / judge rows). For each debater i (bench agents excluded):
        logit P(s_i(t+1)=+1) = 2[h_i + delta(debate, 10-min block) + J_self s_i(t) + J_same m_same(t) + J_opp m_opp(t)
                                 + J_judge s_judge(t)]
      m_same / m_opp = mean talk spin of i's current teammates / opponents. Null for J_opp - J_same: team labels
      re-drafted at random within each debate (sizes kept), 500 permutations; null for J_judge: the judge's series
      circularly shifted within the debate, 500 surrogates. Secondary: active spins.
g44   #44b (05-28, 05-29): the temporary fine-tuned leader (agent 28, DQ6 `leader`) among #best agents
      (room_assignment), KI-1 + block fields, net outgoing influence I_k, rank and z vs 200 N1 block-shift
      surrogates; active and talk spins; whole-grid and DQ8-trimmed (all-present window + explained joint silences
      removed before the surrogates). Secondary: the whole village.
Inputs: activity_bins_fixed, outages_fixed, ground_truth_labels, calendar. Non-holdout only (asserted).
Output: data/processed/H02-couplings-are-real/r1b/native_<test>.json
Usage: OMP_NUM_THREADS=2 uv run python hypotheses/H02-couplings-are-real/analysis/r1b_native.py g12|g44
"""
from __future__ import annotations

import os

os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "2"); os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("POLARS_MAX_THREADS", "2")
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h02lib as L  # noqa: E402
import r1b_common as RB  # noqa: E402

ROOT = RB.ROOT
SH = RB.SH
OUT = RB.BASE / "r1b"
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402


def guard(days, goal):
    assert not any(holdout_mask(days, [goal] * len(days))), "holdout day in a native test"


def minute_of(t, win_start):
    return int((t - win_start).total_seconds() // 60)


def spin_grid(days, agents, thr):
    ab = (pl.scan_parquet(SH / "activity_bins_fixed.parquet").filter(pl.col("pt_date").is_in(days) & pl.col("agent").is_in(agents))
          .select("pt_date", "minute", "agent", "state").collect())
    piv = (ab.with_columns(pl.when(pl.col("state") >= thr).then(1).otherwise(-1).cast(pl.Int8).alias("s"))
           .pivot(on="agent", index=["pt_date", "minute"], values="s").sort("pt_date", "minute"))
    cols = [str(a) for a in agents if str(a) in piv.columns]
    return piv, cols


# ============================================================================================== #12
def g12(n_perm=500, spin="talk"):
    cal = pl.read_parquet(SH / "calendar.parquet").select("pt_date", "win_start", "goal_no")
    gt = pl.read_parquet(SH / "ground_truth_labels.parquet").filter(pl.col("goal_no") == 12)
    teams = gt.filter(pl.col("label_kind") == "team")
    judges = gt.filter(pl.col("label_kind") == "judge")
    debates = sorted(teams["unit"].unique().to_list())
    agents = sorted(set(teams["agent"].to_list()) | set(judges["agent"].to_list()))
    days = sorted(cal.filter(pl.col("goal_no") == 12)["pt_date"].to_list())
    guard(days, 12)
    piv, cols = spin_grid(days, agents, 4 if spin == "talk" else 3)
    ws = dict(cal.select("pt_date", "win_start").iter_rows())
    blocks = []  # per debate: S (T x 7), gov/opp/judge index arrays
    for k, db in enumerate(debates):
        tr = teams.filter(pl.col("unit") == db)
        t0, t1 = tr["t_valid_from"][0], tr["t_valid_to"][0]
        d = t0.astimezone(__import__("zoneinfo").ZoneInfo("America/Los_Angeles")).date().isoformat()
        m0, m1 = minute_of(t0, ws[d]), minute_of(t1, ws[d])
        sub = piv.filter((pl.col("pt_date") == d) & (pl.col("minute") >= m0) & (pl.col("minute") <= m1)).sort("minute")
        S = np.nan_to_num(sub.select(cols).to_numpy().astype(float), nan=-1.0)
        idx = {int(c): i for i, c in enumerate(cols)}
        gov = [idx[a] for a, v in zip(tr["agent"], tr["value"]) if v == "gov" and a in idx]
        opp = [idx[a] for a, v in zip(tr["agent"], tr["value"]) if v == "opp" and a in idx]
        jd = judges.filter(pl.col("unit") == db)["agent"].to_list()
        blocks.append({"debate": db, "S": S, "gov": gov, "opp": opp, "judge": idx.get(jd[0]) if jd else None,
                       "minute": sub["minute"].to_numpy(), "k": k})

    def design(teamsets):
        """Stack transitions (t -> t+1) of every debater in every debate. teamsets: per debate (gov, opp)."""
        X, Y, A, B = [], [], [], []
        for blk, (gov, opp) in zip(blocks, teamsets):
            S = blk["S"]
            T = S.shape[0]
            if T < 3:
                continue
            ok = np.flatnonzero(np.diff(blk["minute"]) == 1)
            sj = S[:, blk["judge"]] if blk["judge"] is not None else np.zeros(T)
            for team, other in ((gov, opp), (opp, gov)):
                for i in team:
                    mates = [j for j in team if j != i]
                    ms = S[:, mates].mean(1) if mates else np.zeros(T)
                    mo = S[:, other].mean(1)
                    for t in ok:
                        X.append([S[t, i], ms[t], mo[t], sj[t]])
                        Y.append(1.0 if S[t + 1, i] > 0 else 0.0)
                        A.append(i)
                        B.append(blk["k"] * 10 + (t + 1) // 10)
        X = np.asarray(X); Y = np.asarray(Y)[:, None]
        A = np.asarray(A); B = np.asarray(B)
        _, Bi = np.unique(B, return_inverse=True)
        Xf = np.hstack([L.one_hot(A, len(cols)), X, L.one_hot(Bi)])
        pen = np.r_[np.full(len(cols), 1e-6), np.full(4, L.LAM_J), np.full(Bi.max() + 1, L.LAM_D)]
        return Xf, Y, pen

    def fit(teamsets):
        Xf, Y, pen = design(teamsets)
        b = L.fit_logistic(Xf, Y, pen)[0]
        j = b[len(cols):len(cols) + 4] / 2.0
        return {"J_self": j[0], "J_same": j[1], "J_opp": j[2], "J_judge": j[3], "n_trans": int(len(Y))}

    real_sets = [(b["gov"], b["opp"]) for b in blocks]
    real = fit(real_sets)
    rng = np.random.default_rng([20261004, 12])
    perm = []
    for _ in range(n_perm):
        sets = []
        for b in blocks:
            deb = b["gov"] + b["opp"]
            p = rng.permutation(deb)
            sets.append((list(p[:len(b["gov"])]), list(p[len(b["gov"]):])))
        perm.append(fit(sets))
    d_real = real["J_opp"] - real["J_same"]
    d_perm = np.array([p["J_opp"] - p["J_same"] for p in perm])
    # judge null: circular shift of the judge's series within each debate
    jn = []
    saved = [b["S"].copy() for b in blocks]
    for _ in range(min(n_perm, 300)):
        for b, S0 in zip(blocks, saved):
            if b["judge"] is None or S0.shape[0] < 3:
                continue
            S = S0.copy()
            S[:, b["judge"]] = np.roll(S0[:, b["judge"]], rng.integers(1, S0.shape[0]))
            b["S"] = S
        jn.append(fit(real_sets)["J_judge"])
    for b, S0 in zip(blocks, saved):
        b["S"] = S0
    jn = np.array(jn)
    res = {"spin": spin, "debates": len(blocks), "debate_minutes": int(sum(b["S"].shape[0] for b in blocks)), **real,
           "d_opp_minus_same": d_real, "perm_mean": float(d_perm.mean()), "perm_sd": float(d_perm.std()),
           "z_d": float((d_real - d_perm.mean()) / d_perm.std()),
           "p_d_two_sided": float((1 + (np.abs(d_perm - d_perm.mean()) >= abs(d_real - d_perm.mean())).sum()) / (n_perm + 1)),
           "judge_null_mean": float(jn.mean()), "judge_null_sd": float(jn.std()),
           "z_judge": float((real["J_judge"] - jn.mean()) / jn.std()),
           "talk_occupancy": float(np.mean([(b["S"] > 0).mean() for b in blocks]))}
    return res


# ============================================================================================== #44b
def g44(n_surr=200):
    days = ["2026-05-28", "2026-05-29"]
    guard(days, 44)
    gt = pl.read_parquet(SH / "ground_truth_labels.parquet").filter(pl.col("goal_no") == 44)
    best = sorted(gt.filter((pl.col("label_kind") == "room_assignment") & (pl.col("value") == "best"))["agent"].to_list())
    leader = int(gt.filter(pl.col("label_kind") == "leader")["agent"][0])
    ab = (pl.scan_parquet(SH / "activity_bins_fixed.parquet").filter(pl.col("pt_date").is_in(days)).collect())
    pres = (ab.group_by("agent").agg(pl.col("pt_date").n_unique().alias("nd"), (pl.col("state") >= 3).sum().alias("nact"),
                                     (pl.col("state") == 4).sum().alias("ntalk"))
            .filter((pl.col("nd") == len(days)) & (pl.col("nact") >= 30)).sort("agent"))
    village = pres["agent"].to_list()
    rs = pl.read_parquet(SH / "outages_fixed/reasons.parquet").filter(pl.col("pt_date").is_in(days)).with_columns(pl.col("minute").cast(pl.Int64))
    sm = pl.read_parquet(SH / "outages_fixed/stall_minutes.parquet", columns=["pt_date", "minute", "scheduled"]).filter(
        pl.col("pt_date").is_in(days)).with_columns(pl.col("minute").cast(pl.Int64))
    d = ab.join(rs, on=["pt_date", "minute", "agent"], how="left").with_columns(pl.col("reason").fill_null(0))
    out = {"leader": leader, "best": best, "village_N": len(village), "days": days}
    rng = np.random.default_rng([20261004, 44])
    for scope, agents in (("best", [a for a in village if a in best + [leader]]), ("village", village)):
        for spin, thr in (("active", 3), ("talk", 4)):
            ag = agents if spin == "active" else [a for a in agents if
                                                  pres.filter(pl.col("agent") == a)["ntalk"][0] >= 30 or a == leader]
            if leader not in ag or len(ag) < 3:
                out[f"{scope}|{spin}"] = {"skipped": "leader absent or < 3 agents", "agents": ag}
                continue
            dd = d.filter(pl.col("agent").is_in(ag)).with_columns(
                pl.col("pt_date").replace_strict({x: i for i, x in enumerate(days)}, return_dtype=pl.Int16).alias("day"))
            cols = [str(a) for a in ag]
            st = dd.pivot(on="agent", index=["day", "minute"], values="state").sort("day", "minute")
            state = np.nan_to_num(st.select(cols).to_numpy().astype(float), nan=1)
            R = np.nan_to_num(dd.pivot(on="agent", index=["day", "minute"], values="reason").sort("day", "minute")
                              .select(cols).to_numpy().astype(float), nan=0).astype(np.int8)
            day, minute = st["day"].to_numpy(), st["minute"].to_numpy()
            Sa = np.where(state >= 3, 1, -1).astype(np.int8)
            S = np.where(state >= thr, 1, -1).astype(np.int8)
            R = np.where(Sa > 0, 0, R).astype(np.int8)
            key = pl.DataFrame({"pt_date": [days[i] for i in day], "minute": minute})
            sched = key.join(sm, on=["pt_date", "minute"], how="left")["scheduled"].fill_null(False).to_numpy()
            li = ag.index(leader)
            for mk in ("none", "trim_stall"):
                keep = RB.keep_runs(day, RB.row_mask(Sa, R, sched, mk))
                Sk, dk, mk_ = S[keep], day[keep], minute[keep]
                J, _, _ = L.fit_kinetic(Sk, dk, mk_, "block", "1")
                I = L.net_influence(J)
                segs = L.segments(dk, mk_, "block")
                In = np.array([L.net_influence(L.fit_kinetic(L.circular_shift(Sk, segs, rng), dk, mk_, "block", "1")[0])
                               for _ in range(n_surr)])
                z = (I - In.mean(0)) / In.std(0)
                out[f"{scope}|{spin}|{mk}"] = {"N": len(ag), "T": int(keep.sum()), "kept_share": float(keep.mean()),
                                               "leader_I": float(I[li]), "leader_rank": L.rank_of(I, li),
                                               "leader_z": float(z[li]), "top_z": float(np.nanmax(z)),
                                               "top_agent": int(ag[int(np.nanargmax(z))]),
                                               "leader_active_frac": float((Sk[:, li] > 0).mean()),
                                               "rule_pass": bool(L.rank_of(I, li) == 1 and z[li] >= 2)}
                print(scope, spin, mk, out[f"{scope}|{spin}|{mk}"], flush=True)
    return out


def main():
    cmd = sys.argv[1]
    OUT.mkdir(parents=True, exist_ok=True)
    if cmd == "g12":
        res = {"talk": g12(spin="talk"), "active": g12(spin="active")}
    elif cmd == "g44":
        res = g44()
    else:
        raise SystemExit(cmd)
    (OUT / f"native_{cmd}.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
