"""H01 exploratory round 1 on REAL data, non-holdout only: P1-P9 of the card (+ Amendments 1 and 2).

Unit of analysis = goal period split at step changes (scheme/h01common.py: GOAL_SPLITS). Every test is run per unit;
cross-unit summaries are random-effects meta-analyses (heterogeneity tau^2, I^2 reported), never pooled fits.

Sections (run all, or pass --only SECTION[,SECTION]):
  inv   h_i invariance check (Amendment 1(b)) - run first; decides the agent-field rule
  p1    P1 rooms vs random same-size groups (semantic entropy, rarefied, k = 40) + P2 labs and field removal + P3 JSD
  p4    P4 polarization along g-hat (#8, #21 and every unit, descriptive)
  p56   P5 field R^2 and P6 exposure slope (+ directions, lag, rooms, nulls), per unit; P7 merge DiD (#39 -> #40)
  p8    P8 NE32 GPT-5.6 triplet (07-09 isolated, 07-10 merged)
  p9    P9 mean-field O(32) fit per unit

Usage: uv run python hypotheses/H01-emergent-superagents-exist/analysis/explore.py [--only p1,p56] [--d 32] [--fast]
Writes data/processed/H01-emergent-superagents-exist/explore[_d16|_d64].json and per-goal-period G##/results.json.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h01data import P1_EXTRA, P1_UNITS, P56_UNITS, Scheme  # noqa: E402
from h01lib import (Unit, fluct_rho_rooms, fe_slope, fe_slope_fast, js_distance, mf_fit, pair_table, partition_test,  # noqa: E402
                    permute_unit_days, r2_field, random_effects, rarefied_counts, rarefied_vectors, rotate_agents,
                    shuffle_days, split_half_vectors, unit)
from h01common import OUT, SEED, kmeans  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ARGS = sys.argv[1:]
ONLY = set(ARGS[ARGS.index("--only") + 1].split(",")) if "--only" in ARGS else {"inv", "p1", "p4", "p56", "p8", "p9", "p9r"}
D = int(ARGS[ARGS.index("--d") + 1]) if "--d" in ARGS else 32
K = int(ARGS[ARGS.index("--k") + 1]) if "--k" in ARGS else 40
FAST = "--fast" in ARGS
WEIGHT = ARGS[ARGS.index("--weight") + 1] if "--weight" in ARGS else "agent"   # agent | message
H_MODE = ARGS[ARGS.index("--hmode") + 1] if "--hmode" in ARGS else "firstday"   # Amendment 3 primary; "crossfit" = variant
SEED_OFF = int(ARGS[ARGS.index("--seed") + 1]) if "--seed" in ARGS else 0
LEX = "--lex" in ARGS
TAG = ARGS[ARGS.index("--tag") + 1] if "--tag" in ARGS else (f"_d{D}" if D != 32 else "") + (f"_k{K}" if K != 40 else "") + ("_wmsg" if WEIGHT == "message" else "") + ("_hcross" if H_MODE == "crossfit" else "") + (f"_seed{SEED_OFF}" if SEED_OFF else "") + ("_lex" if LEX else "")
NPERM = 300 if FAST else 1000
NNULL = 50 if FAST else 200
M_ENT, R_ENT = 8, 20          # P1: statements per agent-day, rarefaction draws
M_VEC, R_VEC = 8, 10          # P6 (Amendment 2): rarefied agent-day vectors
GPT5 = 10
TRIPLET = (35, 36, 37)


def log(*a):
    print(*a, flush=True)


# ============================================================================ invariance
def invariance(S: Scheme):
    out = {}
    for R in ("I", "II", "III"):
        info = S.adinfo.filter(pl.col("regime") == R)
        cos_same, cos_other, per_agent = [], [], {}
        goals_first = dict(info.group_by("goal_no").agg(pl.col("pt_date").min()).iter_rows())
        hA, hB = {}, {}
        for a in info["agent"].unique().to_list():
            ia = info.filter(pl.col("agent") == a)
            gl = sorted(ia["goal_no"].unique().to_list(), key=lambda g: goals_first[g])
            for g in gl:
                oth = [x for x in gl if x != g]
                A, B = oth[0::2], oth[1::2]
                if not A or not B:
                    continue
                va = unit(np.mean([S.adV[(a, d)] for d in ia.filter(pl.col("goal_no").is_in(A))["pt_date"].to_list()], 0))
                vb = unit(np.mean([S.adV[(a, d)] for d in ia.filter(pl.col("goal_no").is_in(B))["pt_date"].to_list()], 0))
                hA[(a, g)] = va; hB[(a, g)] = vb
                c = float(va @ vb); cos_same.append(c); per_agent.setdefault(int(a), []).append(c)
        keys = list(hA)
        for (a, g) in keys:
            for (b, g2) in keys:
                if g2 == g and b != a:
                    cos_other.append(float(hA[(a, g)] @ hB[(b, g)]))
        if cos_same:
            out[R] = {"n_agent_targets": len(cos_same), "n_agents": len(per_agent), "median_cos_same": float(np.median(cos_same)),
                      "q25": float(np.quantile(cos_same, 0.25)), "q75": float(np.quantile(cos_same, 0.75)),
                      "median_cos_between_agents": float(np.median(cos_other)) if cos_other else None,
                      "per_agent_median": {S.name_of[a]: float(np.median(v)) for a, v in per_agent.items()},
                      "pass": bool(np.median(cos_same) >= 0.5)}
    return out


# ============================================================================ P1 / P2 / P3
def eligible(u: Unit, t, M=M_ENT):
    return np.where((u.day == t) & (u.nstmt >= M) & (u.room >= 0))[0]


def field_removed_labels(S: Scheme, regime_units: dict, rng):
    """Statement vectors with the agent field direction projected out (each statement uses its unit's cross-fitted
    h of its agent), re-clustered (k = K) per regime on all non-holdout statements of that regime."""
    labels = np.full(len(S.U), -1, np.int16)
    for R, names in regime_units.items():
        rows_all, vecs = [], []
        for name in names:
            u = S.unit(name, h_mode=H_MODE)
            for i, rr in enumerate(u.rows):
                a = u.agents[i]
                X = S.U[rr].astype(np.float64)
                if a in u.h:
                    X = unit(X - np.outer(X @ u.h[a], u.h[a]))
                rows_all.append(rr); vecs.append(X)
        rows_all = np.concatenate(rows_all); vecs = np.concatenate(vecs).astype(np.float32)
        C, lab, _ = kmeans(vecs, K, seed=SEED + 777)
        labels[rows_all] = lab
    return labels


def p1_section(S: Scheme, rng):
    reg_units = {"II": ["33", "35", "36a"], "III": [u for u in S.units if S.units[u]["regimes"] == ["III"]]}
    fr = field_removed_labels(S, reg_units, rng)
    days_out, p3_out = [], []
    for name in P1_UNITS + P1_EXTRA:
        u = S.unit(name)
        uh = S.unit(name, h_mode=H_MODE)
        T = int(u.day.max()) + 1
        for t in range(T):
            idx = eligible(u, t)
            labs_room = u.room[idx]
            rec = {"unit": name, "day": u.day_names[t], "day_idx": t, "primary": name in P1_UNITS, "n_agents": int(len(idx))}
            cnt_room = np.bincount(np.unique(labs_room, return_inverse=True)[1]) if len(idx) else np.array([])
            rec["room_sizes"] = sorted(cnt_room.tolist(), reverse=True)
            if len(idx) < 4 or (cnt_room >= 2).sum() < 2:
                rec["skip"] = "fewer than 2 rooms with >= 2 eligible agents"
                days_out.append(rec); continue
            if WEIGHT == "message":
                cnt = np.stack([np.bincount(u.lab[K][u.rows[i]], minlength=K) for i in idx]).astype(np.float32)[None]
            else:
                cnt = rarefied_counts(u, idx, K, M_ENT, R_ENT, rng)
            rec["room"] = partition_test(cnt, labs_room, NPERM, rng)
            labs_lab = np.array([u.labs[a] for a in u.agents[idx]])
            if (np.unique(labs_lab, return_counts=True)[1] >= 2).any():
                rec["lab"] = partition_test(cnt, labs_lab, NPERM, rng)
            if K in (40,) and D == 32 and WEIGHT == "agent":
                # P2 (Amendment 3): only agents whose h_i comes from an EARLIER day of the unit
                firstd = {a: u.day[u.agents == a].min() for a in np.unique(u.agents)}
                okm = np.array([(H_MODE == "crossfit" and a in uh.h) or (a in uh.h and firstd[a] < t) for a in u.agents[idx]])
                i2 = idx[okm]; lr2 = u.room[i2]; ll2 = np.array([u.labs[a] for a in u.agents[i2]])
                if len(i2) >= 4:
                    c_raw = rarefied_counts(u, i2, K, M_ENT, R_ENT, rng)
                    c_fr = rarefied_counts(u, i2, K, M_ENT, R_ENT, rng, labels=fr)
                    if (np.bincount(np.unique(lr2, return_inverse=True)[1]) >= 2).sum() >= 2:
                        rec["room_raw2"] = partition_test(c_raw, lr2, NPERM, rng)
                        rec["room_fr"] = partition_test(c_fr, lr2, NPERM, rng)
                    if (np.unique(ll2, return_counts=True)[1] >= 2).any():
                        rec["lab_raw2"] = partition_test(c_raw, ll2, NPERM, rng)
                        rec["lab_fr"] = partition_test(c_fr, ll2, NPERM, rng)
            days_out.append(rec)
        # P3: consecutive day pairs
        for t in range(T - 1):
            a0 = set(u.agents[eligible(u, t)]); a1 = set(u.agents[eligible(u, t + 1)])
            both = sorted(a0 & a1)
            if len(both) < 4:
                continue
            i0 = {u.agents[i]: i for i in eligible(u, t)}; i1 = {u.agents[i]: i for i in eligible(u, t + 1)}
            c0 = rarefied_counts(u, [i0[a] for a in both], K, M_ENT, R_ENT, rng)
            c1 = rarefied_counts(u, [i1[a] for a in both], K, M_ENT, R_ENT, rng)
            rooms0 = np.array([u.room[i0[a]] for a in both]); rooms1 = np.array([u.room[i1[a]] for a in both])
            for r in np.unique(rooms0):
                m0 = rooms0 == r; m1 = rooms1 == r
                if m0.sum() < 2 or m1.sum() < 2 or m0.sum() == len(both):
                    continue
                js = js_distance(c0[:, m0].sum(1), c1[:, m1].sum(1)).mean()
                null = []
                for _ in range(500):
                    s = rng.choice(len(both), m0.sum(), replace=False)
                    null.append(js_distance(c0[:, s].sum(1), c1[:, s].sum(1)).mean())
                q05 = float(np.quantile(null, 0.05))
                p3_out.append({"unit": name, "day0": u.day_names[t], "room": int(r), "size": int(m0.sum()), "js": float(js),
                               "null_q05": q05, "null_mean": float(np.mean(null)), "below_q05": bool(js < q05),
                               "pct": float((np.array(null) <= js).mean()), "primary": name in P1_UNITS})
    # summaries
    def summ(recs, key):
        v = [r[key]["dH"] for r in recs if key in r]
        if not v:
            return None
        return {"n_days": len(v), "frac_dH_neg": float(np.mean(np.array(v) < 0)), "median_dH": float(np.median(v)),
                "frac_p05": float(np.mean([r[key]["p"] < 0.05 for r in recs if key in r])),
                "mean_z": float(np.mean([r[key]["z"] for r in recs if key in r]))}
    prim = [r for r in days_out if r["primary"] and "room" in r]
    per_unit = {}
    for name in P1_UNITS + P1_EXTRA:
        rr = [r for r in days_out if r["unit"] == name and "room" in r]
        if not rr:
            per_unit[name] = {"eligible_days": 0}; continue
        d1 = [r for r in rr if r["day_idx"] == 0]
        later = [r for r in rr if r["day_idx"] > 0]
        di = np.array([r["day_idx"] for r in rr]); dh = np.array([r["room"]["dH"] for r in rr])
        per_unit[name] = {"room": summ(rr, "room"), "lab": summ(rr, "lab"), "room_fr": summ(rr, "room_fr"), "lab_fr": summ(rr, "lab_fr"),
                          "day1_dH": d1[0]["room"]["dH"] if d1 else None, "days2plus": summ(later, "room"),
                          "drift_slope": float(np.polyfit(di, dh, 1)[0]) if len(set(di)) > 1 else None}
    P1 = summ(prim, "room")
    P1["pass"] = bool(P1["frac_dH_neg"] >= 0.6 and P1["median_dH"] <= -0.1)
    P1["pass_direction_only"] = bool(P1["frac_dH_neg"] >= 0.6)
    P1["n_units_meeting_both"] = int(sum(1 for n in P1_UNITS if per_unit[n].get("room") and per_unit[n]["room"]["frac_dH_neg"] >= 0.6
                                         and per_unit[n]["room"]["median_dH"] <= -0.1))
    P1["n_units_with_days"] = int(sum(1 for n in P1_UNITS if per_unit[n].get("room")))
    P1["days2plus"] = summ([r for r in prim if r["day_idx"] > 0], "room")
    P1["day1"] = summ([r for r in prim if r["day_idx"] == 0], "room")
    P2 = None
    if any("room_fr" in r for r in prim):
        lab0 = summ(prim, "lab_raw2"); lab1 = summ(prim, "lab_fr"); room0 = summ(prim, "room_raw2"); room1 = summ(prim, "room_fr")
        sh = lambda a, b: float(1 - b["median_dH"] / a["median_dH"]) if a and b and a["median_dH"] < 0 else None  # noqa: E731
        P2 = {"lab_raw": lab0, "lab_field_removed": lab1, "room_raw": room0, "lab_raw_all_days": summ(prim, "lab"),
              "room_field_removed": room1, "lab_shrink": sh(lab0, lab1), "room_shrink": sh(room0, room1)}
        P2["pass"] = bool(lab0 and lab0["frac_dH_neg"] >= 0.6 and lab0["median_dH"] < 0 and P2["lab_shrink"] is not None
                          and P2["lab_shrink"] >= 0.5 and P2["room_shrink"] is not None and P2["room_shrink"] < 0.5)
    p3p = [r for r in p3_out if r["primary"]]
    P3 = {"n_room_day_pairs": len(p3p), "frac_below_q05": float(np.mean([r["below_q05"] for r in p3p])) if p3p else None,
          "median_pct": float(np.median([r["pct"] for r in p3p])) if p3p else None,
          "per_unit": {n: {"n": len([r for r in p3p if r["unit"] == n]),
                           "frac_below_q05": float(np.mean([r["below_q05"] for r in p3p if r["unit"] == n]))}
                       for n in P1_UNITS if any(r["unit"] == n for r in p3p)}}
    P3["pass"] = bool(p3p and P3["frac_below_q05"] >= 0.6)
    P3["goal_change_jumps"] = goal_change_jumps(S, rng)
    return {"P1": P1, "P2": P2, "P3": P3, "per_unit": per_unit, "days": days_out, "p3_pairs": p3_out}


def goal_change_jumps(S: Scheme, rng):
    """NE34 (descriptive): whole-swarm JSD between consecutive non-holdout days, within a unit vs across a goal change
    (same regime only, both days non-holdout and adjacent in the non-holdout calendar)."""
    allu = sorted(S.units.values(), key=lambda x: x["days"][0])
    seq = []
    for ui in allu:
        for d in ui["days"]:
            seq.append((d, ui["unit"], ui["goal_no"], ui["regimes"][0]))
    cache = {}

    def dist(d, name):
        if (d, name) not in cache:
            u = S.unit(name, days=[d])
            idx = np.where(u.nstmt >= M_ENT)[0]
            cache[(d, name)] = (rarefied_counts(u, idx, K, M_ENT, R_ENT, rng).sum(1), set(u.agents[idx])) if len(idx) >= 3 else None
        return cache[(d, name)]
    within, across = [], []
    for (d0, n0, g0, r0), (d1, n1, g1, r1) in zip(seq, seq[1:]):
        if r0 != r1:
            continue
        a, b = dist(d0, n0), dist(d1, n1)
        if a is None or b is None:
            continue
        js = float(js_distance(a[0], b[0]).mean())
        (within if g0 == g1 else across).append({"d0": d0, "d1": d1, "g0": g0, "g1": g1, "js": js, "regime": r0})
    return {"n_within": len(within), "n_across": len(across), "median_within": float(np.median([x["js"] for x in within])),
            "median_across": float(np.median([x["js"] for x in across])) if across else None,
            "frac_across_above_within_q90": float(np.mean([x["js"] > np.quantile([w["js"] for w in within], 0.9) for x in across])) if across else None,
            "across": across}


# ============================================================================ P4
def p4_section(S: Scheme, rng):
    out = {}
    for name, ui in S.units.items():
        if len(ui["days"]) < 2:
            continue
        u = S.unit(name)
        pg, pm, al = [], [], []
        for t in range(int(u.day.max()) + 1):
            idx = np.where((u.day == t) & (u.nstmt >= 3))[0]
            if len(idx) < 2:
                continue
            M = u.V[idx].mean(0)
            pg.append(float(M @ u.ghat)); pm.append(float(M @ M - 1 / len(idx))); al.extend((u.V[idx] @ u.ghat).tolist())
        if pg:
            N = np.mean([len(np.where((u.day == t) & (u.nstmt >= 3))[0]) for t in range(int(u.day.max()) + 1)])
            out[name] = {"regime": ui["regimes"][0], "goal_no": ui["goal_no"], "n_days": len(pg), "pol_g_mean": float(np.mean(pg)),
                         "pol_g_daily": pg, "pol_sq_corrected_mean": float(np.mean(pm)), "agent_cos_g_mean": float(np.mean(al)),
                         "null_sd_pol_g": float(1 / np.sqrt(D * N))}
    reg1 = {k: v for k, v in out.items() if v["regime"] == "I"}
    rank = sorted(reg1, key=lambda k: -reg1[k]["pol_g_mean"])
    res = {"units": out, "regime_I_rank_by_pol_g": rank}
    if "8" in out and "21" in out:
        res["P4"] = {"pol_g_8": out["8"]["pol_g_mean"], "pol_g_21": out["21"]["pol_g_mean"],
                     "rank_8": rank.index("8") + 1, "rank_21": rank.index("21") + 1, "n_regime_I_units": len(rank),
                     "as_predicted": bool(out["8"]["pol_g_mean"] > out["21"]["pol_g_mean"])}
    return res


# ============================================================================ P5 / P6 / P7
def unit_p56(u: Unit, rng, two_room: bool):
    res = {"unit": u.name, "n_agents": int(len(np.unique(u.agents))), "n_days": int(u.day.max() + 1),
           "h_first_day_agents": int(len(u.h_firstday)), "n_agent_goal_fields": int(len(u.ghat_agent))}
    pt = pair_table(u, n_min=3)
    if pt is None:
        return res
    res["n_pair_days_full"] = int(len(pt["a"]))
    res["r2"] = r2_field(pt)
    X = np.column_stack([np.ones(len(pt["a"])), pt["Tg"]])
    e = pt["a"] - X @ np.linalg.lstsq(X, pt["a"], rcond=None)[0]
    res["r2_goal_only"] = float(1 - e.var() / pt["a"].var())
    res["var_share_phi"] = float(np.var(pt["phi"]) / np.var(pt["a"]))
    r2rot = []
    for _ in range(min(NNULL, 100)):
        Vr, hr, _ = rotate_agents(u, rng)
        r2rot.append(r2_field(pair_table(u, n_min=3, Vover=Vr, hover=hr)))
    res["r2_rot_mean"] = float(np.mean(r2rot)); res["r2_rot_q95"] = float(np.quantile(r2rot, 0.95))
    A, B = split_half_vectors(u, rng)
    ok = ~np.isnan(A[pt["xi"]]).any(1) & ~np.isnan(A[pt["yi"]]).any(1)
    aAB = (A[pt["xi"]] * B[pt["yi"]]).sum(1); aBA = (B[pt["xi"]] * A[pt["yi"]]).sum(1)
    rh = float(np.corrcoef(aAB[ok], aBA[ok])[0, 1])
    res["a_reliability"] = float(2 * rh / (1 + rh))
    res["mean_a"] = float(pt["a"].mean()); res["mean_phi"] = float(pt["phi"].mean()); res["mean_r_full"] = float(pt["r"].mean())
    # P6 on rarefied vectors (Amendment 2)
    Vr = rarefied_vectors(u, M_VEC, R_VEC, rng)
    ptr = pair_table(u, n_min=M_VEC, Vover=Vr)
    if ptr is None or len(ptr["a"]) < 20:
        res["p6_note"] = "too few pair-days with >= 8 statements"
        return res
    ptr["x"] = np.log1p(ptr["Eij"] + ptr["Eji"]); ptr["x1"] = np.log1p(ptr["Eij"]); ptr["x2"] = np.log1p(ptr["Eji"])
    res["n_pair_days"] = int(len(ptr["a"])); res["mean_r"] = float(ptr["r"].mean())
    res["x_within_sd"] = float(np.std(ptr["x"] - np.array([ptr["x"][(ptr["i"] == i) & (ptr["j"] == j)].mean() for i, j in zip(ptr["i"], ptr["j"])])))
    f = fe_slope(ptr, ["x"])
    if f is not None:
        res["slope"] = float(f["b"][0]); res["slope_se"] = float(f["se"][0]); res["slope_p"] = float(f["p"][0])
        rot, shf = [], []
        for _ in range(NNULL):
            _, hr, Vrr = rotate_agents(u, rng, extra=Vr)
            p0 = pair_table(u, n_min=M_VEC, Vover=Vrr, hover=hr)
            rot.append(float(fe_slope_fast(f, p0["r"])[0]))
            _, Vss = shuffle_days(u, rng, extra=Vr, n_min=M_VEC)
            p1 = pair_table(u, n_min=M_VEC, Vover=Vss)
            shf.append(float(fe_slope_fast(f, p1["r"])[0]) if len(p1["r"]) == len(ptr["r"]) else np.nan)
        res["slope_rot_null"] = rot; res["slope_shuf_null"] = shf
        res["p_rot"] = float((1 + np.sum(np.array(rot) >= res["slope"])) / (1 + len(rot)))
        shf_ = np.array(shf)[np.isfinite(shf)]
        res["p_shuf"] = float((1 + np.sum(shf_ >= res["slope"])) / (1 + len(shf_)))
    # full-vector variant with log n controls
    pt["x"] = np.log1p(pt["Eij"] + pt["Eji"]); pt["lni"] = np.log(pt["ni"]); pt["lnj"] = np.log(pt["nj"])
    ff = fe_slope(pt, ["x"], covars=("lni", "lnj"))
    if ff is not None:
        res["slope_fullvec"] = float(ff["b"][0]); res["slope_fullvec_se"] = float(ff["se"][0])
    fd = fe_slope(ptr, ["x1", "x2"])
    if fd is not None:
        res["dir"] = {"b1": float(fd["b"][0]), "se1": float(fd["se"][0]), "b2": float(fd["b"][1]), "se2": float(fd["se"][1])}
    lagm = ptr["Eij_lag"] >= 0
    if lagm.sum() > 20:
        ptr["xl"] = np.log1p(np.clip(ptr["Eij_lag"], 0, None) + np.clip(ptr["Eji_lag"], 0, None))
        fl = fe_slope(ptr, ["xl"], mask=lagm)
        fs = fe_slope(ptr, ["x"], mask=lagm)
        fj = fe_slope(ptr, ["x", "xl"], mask=lagm)
        if fj is not None:
            res["joint_same"] = float(fj["b"][0]); res["joint_same_se"] = float(fj["se"][0])
            res["joint_lag"] = float(fj["b"][1]); res["joint_lag_se"] = float(fj["se"][1])
        if fl is not None:
            res["lag_slope"] = float(fl["b"][0]); res["lag_slope_se"] = float(fl["se"][0])
        if fs is not None:
            res["same_slope_on_lag_sample"] = float(fs["b"][0]); res["same_slope_on_lag_sample_se"] = float(fs["se"][0])
    d2 = ptr["day"] > 0
    if d2.sum() > 20:
        f2 = fe_slope(ptr, ["x"], mask=d2)
        if f2 is not None:
            res["slope_days2plus"] = float(f2["b"][0]); res["slope_days2plus_se"] = float(f2["se"][0])
    res["mean_r_by_day"] = [float(ptr["r"][ptr["day"] == t].mean()) if (ptr["day"] == t).any() else None for t in range(int(u.day.max()) + 1)]
    di = ptr["day"].astype(float)
    res["r_drift_per_day"] = float(np.polyfit(di, ptr["r"], 1)[0]) if len(np.unique(di)) > 1 else None
    if two_room and ptr["same"].any() and (~ptr["same"]).any():
        def wc(p):
            pk = p["i"] * 1000 + p["j"]
            pairs = np.unique(pk)
            pm = np.array([p["r"][pk == q].mean() for q in pairs]); ps = np.array([p["same"][pk == q].mean() > 0.5 for q in pairs])
            return float(pm[ps].mean() - pm[~ps].mean()), pm, ps
        diff, pm, ps = wc(ptr)
        res["within_minus_cross"] = diff; res["n_within_pairs"] = int(ps.sum()); res["n_cross_pairs"] = int((~ps).sum())
        perm = [float(pm[q].mean() - pm[~q].mean()) for q in (rng.permutation(ps) for _ in range(2000))]
        res["p_pairlabel_perm"] = float((1 + np.sum(np.array(perm) >= diff)) / 2001)
        # room-label permutation at the agent level (keeps room sizes)
        ags = np.unique(u.agents); rm = {a: np.bincount(u.room[(u.agents == a) & (u.room >= 0)]).argmax() if ((u.agents == a) & (u.room >= 0)).any() else -1 for a in ags}
        pk = ptr["i"] * 1000 + ptr["j"]; pairs = np.unique(pk); pi_ = pairs // 1000; pj_ = pairs % 1000
        lab = np.array([rm[a] for a in ags])
        nullv = []
        for _ in range(2000):
            pl_ = dict(zip(ags, rng.permutation(lab)))
            same = np.array([(pl_[a] == pl_[b]) and pl_[a] >= 0 for a, b in zip(pi_, pj_)])
            if same.any() and (~same).any():
                nullv.append(float(pm[same].mean() - pm[~same].mean()))
        res["p_agent_room_perm"] = float((1 + np.sum(np.array(nullv) >= diff)) / (1 + len(nullv)))
        rotd = []
        for _ in range(min(NNULL, 100)):
            _, hr, Vrr = rotate_agents(u, rng, extra=Vr)
            rotd.append(wc(pair_table(u, n_min=M_VEC, Vover=Vrr, hover=hr))[0])
        res["within_minus_cross_rot_mean"] = float(np.mean(rotd)); res["p_rot_wc"] = float((1 + np.sum(np.array(rotd) >= diff)) / (1 + len(rotd)))
        ptf = pair_table(u, n_min=M_VEC, Vover=Vr, use_room=True)
        res["within_minus_cross_roomfield_removed"] = wc(ptf)[0]
    return res


def p7_merge(S: Scheme, rng):
    """P7: 05-04 merge DiD (#39 pre, #40 post). h excludes both #39 and #40 (common agent field across the boundary)."""
    out = {}
    tabs = {}
    u39 = S.unit("39")
    first39 = {a: u39.day_names[u39.day[u39.agents == a].min()] for a in np.unique(u39.agents)}
    for name in ("39", "40"):
        u = S.unit(name)
        ui = S.units[name]
        h = {}
        if H_MODE == "crossfit":
            info = S.adinfo.filter((pl.col("regime") == "III") & ~pl.col("goal_no").is_in([39, 40]))
            for a in np.unique(u.agents):
                dd = info.filter(pl.col("agent") == a)["pt_date"].to_list()
                if dd:
                    h[a] = unit(np.mean([S.adV[(a, d)] for d in dd], 0))
            u.h_firstday = set()
        else:
            for a in np.unique(u.agents):
                if a in first39 and (u39.agents == a).sum() >= 2:
                    h[a] = S.adV[(a, first39[a])]
            u.h_firstday = set(h) if name == "39" else set()
        u.h = h
        Vr = rarefied_vectors(u, M_VEC, R_VEC, rng)
        pt = pair_table(u, n_min=M_VEC, Vover=Vr)
        rm = {}
        for a in np.unique(u.agents):
            m = (u.agents == a) & (u.room >= 0)
            if m.any():
                rm[a] = int(np.bincount(u.room[m]).argmax())
        tabs[name] = (pt, rm, ui["days"])
    pt39, rm39, d39 = tabs["39"]; pt40, rm40, d40 = tabs["40"]
    rows = {k: [] for k in ("i", "j", "day", "r", "post", "a")}
    for post, (pt, off) in enumerate(((pt39, 0), (pt40, 100))):
        for k in ("i", "j", "r", "a"):
            rows[k].append(pt[k])
        rows["day"].append(pt["day"] + off); rows["post"].append(np.full(len(pt["r"]), post))
    P = {k: np.concatenate(v) for k, v in rows.items()}

    def groups(r39, r40):
        g = []
        for i, j in zip(P["i"], P["j"]):
            if i not in r39 or j not in r39 or i not in r40 or j not in r40:
                g.append("na"); continue
            s39 = r39[i] == r39[j]; s40 = r40[i] == r40[j]
            if GPT5 in (i, j):
                g.append("g5_cut" if s39 and not s40 else ("g5_cross" if not s39 and not s40 else "g5_other"))
            else:
                g.append("stay" if s39 and s40 else ("new" if (not s39) and s40 else "other"))
        return np.array(g)
    G = groups(rm39, rm40)
    res = {}
    for arm in ("new", "g5_cut", "g5_cross"):
        m = np.isin(G, ["stay", arm])
        if (G[m] == arm).sum() == 0:
            continue
        P["treat"] = ((G == arm) & (P["post"] == 1)).astype(float)
        f = fe_slope(P, ["treat"], mask=m)
        if f is None:
            continue
        res[arm] = {"did": float(f["b"][0]), "se": float(f["se"][0]), "p": float(f["p"][0]),
                    "n_pairs_arm": int(len(np.unique((P["i"] * 1000 + P["j"])[m & (G == arm)]))),
                    "n_pairs_stay": int(len(np.unique((P["i"] * 1000 + P["j"])[m & (G == "stay")])))}
        if arm == "new":
            # assignment permutation: permute #39 room labels among non-GPT-5 agents (keeps sizes)
            ags = [a for a in rm39 if a != GPT5]; labs = [rm39[a] for a in ags]
            nulls = []
            for _ in range(500 if not FAST else 100):
                r39p = dict(rm39); r39p.update(dict(zip(ags, rng.permutation(labs))))
                Gp = groups(r39p, rm40)
                mp = np.isin(Gp, ["stay", "new"])
                if (Gp[mp] == "new").sum() == 0 or (Gp[mp] == "stay").sum() == 0:
                    continue
                P["treat"] = ((Gp == "new") & (P["post"] == 1)).astype(float)
                fp = fe_slope(P, ["treat"], mask=mp)
                if fp is not None:
                    nulls.append(float(fp["b"][0]))
            res[arm]["p_perm_one_sided"] = float((1 + np.sum(np.array(nulls) >= res[arm]["did"])) / (1 + len(nulls)))
    # raw means for the table
    for g in ("stay", "new", "g5_cut", "g5_cross"):
        for post in (0, 1):
            m = (G == g) & (P["post"] == post)
            if m.any():
                res.setdefault("means", {})[f"{g}_{'post' if post else 'pre'}"] = float(P["r"][m].mean())
    res["as_predicted"] = bool("new" in res and res["new"]["did"] > 0 and ("g5_cut" not in res or res["g5_cut"]["did"] <= 0))
    return res


def p56_section(S: Scheme, rng):
    per = {}
    for name in P56_UNITS:
        t0 = time.time()
        u = S.unit(name, h_mode=H_MODE)
        two_room = len([r for r in np.unique(u.room) if r >= 0 and (u.room == r).sum() >= 2]) >= 2
        per[name] = unit_p56(u, rng, two_room)
        per[name]["two_room"] = two_room
        log("p56", name, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in per[name].items() if not isinstance(v, (list, dict))}, f"{time.time()-t0:.0f}s")
    units = [n for n in P56_UNITS if "slope" in per[n]]
    b = np.array([per[n]["slope"] for n in units]); se = np.array([per[n]["slope_se"] for n in units])
    re = random_effects(b, se)
    rot = np.array([per[n]["slope_rot_null"] for n in units]); shf = np.array([per[n]["slope_shuf_null"] for n in units])
    mu_rot = [random_effects(rot[:, k], se)["mu"] for k in range(rot.shape[1])]
    mu_shf = [random_effects(np.nan_to_num(shf[:, k]), se)["mu"] for k in range(shf.shape[1])]
    re["p_rot_null"] = float((1 + np.sum(np.array(mu_rot) >= re["mu"])) / (1 + len(mu_rot)))
    re["p_shuf_null"] = float((1 + np.sum(np.array(mu_shf) >= re["mu"])) / (1 + len(mu_shf)))
    d_units = [n for n in units if "dir" in per[n]]
    re1 = random_effects([per[n]["dir"]["b1"] for n in d_units], [per[n]["dir"]["se1"] for n in d_units])
    re2 = random_effects([per[n]["dir"]["b2"] for n in d_units], [per[n]["dir"]["se2"] for n in d_units])
    l_units = [n for n in units if "lag_slope" in per[n]]
    rel = random_effects([per[n]["lag_slope"] for n in l_units], [per[n]["lag_slope_se"] for n in l_units])
    res_same_lag = random_effects([per[n]["same_slope_on_lag_sample"] for n in l_units if "same_slope_on_lag_sample" in per[n]],
                                  [per[n]["same_slope_on_lag_sample_se"] for n in l_units if "same_slope_on_lag_sample" in per[n]])
    j_units = [n for n in units if "joint_lag" in per[n]]
    re_jl = random_effects([per[n]["joint_lag"] for n in j_units], [per[n]["joint_lag_se"] for n in j_units])
    re_js = random_effects([per[n]["joint_same"] for n in j_units], [per[n]["joint_same_se"] for n in j_units])
    f_units = [n for n in P56_UNITS if "slope_fullvec" in per[n]]
    re_full = random_effects([per[n]["slope_fullvec"] for n in f_units], [per[n]["slope_fullvec_se"] for n in f_units])
    d2 = [n for n in units if "slope_days2plus" in per[n]]
    re_d2 = random_effects([per[n]["slope_days2plus"] for n in d2], [per[n]["slope_days2plus_se"] for n in d2])
    r2 = {n: per[n]["r2"] for n in P56_UNITS if "r2" in per[n]}
    P5 = {"r2": r2, "n_units": len(r2), "n_ge_0.6": int(sum(v >= 0.6 for v in r2.values())),
          "median_r2": float(np.median(list(r2.values()))),
          "median_r2_rot": float(np.median([per[n]["r2_rot_mean"] for n in r2])),
          "median_reliability": float(np.median([per[n]["a_reliability"] for n in r2])),
          "falsifier_lt_0.3": int(sum(v < 0.3 for v in r2.values()))}
    P5["pass"] = bool(P5["n_ge_0.6"] >= 2 / 3 * P5["n_units"])
    tw = [n for n in units if per[n].get("two_room") and "within_minus_cross" in per[n]]
    P6 = {"re_slope": re, "n_units": len(units), "n_pos": int((b > 0).sum()), "frac_pos": float((b > 0).mean()),
          "re_dir_lo_saw_hi": re1, "re_dir_hi_saw_lo": re2, "re_lag": rel, "re_same_on_lag_sample": res_same_lag,
          "re_joint_lag": re_jl, "re_joint_same": re_js,
          "re_fullvec_logn": re_full, "re_days2plus": re_d2,
          "two_room": {n: {"within_minus_cross": per[n]["within_minus_cross"], "p_agent_room_perm": per[n]["p_agent_room_perm"],
                           "p_rot": per[n]["p_rot_wc"], "roomfield_removed": per[n]["within_minus_cross_roomfield_removed"]} for n in tw}}
    P6["slope_criterion"] = bool(P6["frac_pos"] >= 2 / 3 and re["mu"] > 0 and re["p_two"] < 0.01)
    P6["direction_criterion"] = bool(re1["mu"] > 0 and re2["mu"] > 0 and re1["p_two"] < 0.01 and re2["p_two"] < 0.01)
    P6["room_criterion"] = bool(tw and np.mean([per[n]["within_minus_cross"] > 0 for n in tw]) >= 2 / 3)
    P6["falsifier_large_slope"] = bool(re["mu"] >= 0.1)
    P6["pass"] = bool(P6["slope_criterion"] and P6["direction_criterion"] and P6["room_criterion"])
    P7 = p7_merge(S, rng)
    for n in per:
        per[n].pop("slope_rot_null", None); per[n].pop("slope_shuf_null", None)
    return {"P5": P5, "P6": P6, "P7": P7, "per_unit": per}


# ============================================================================ P8
def p8_section(S: Scheme, rng):
    u = S.unit("51b", h_mode="crossfit")   # Amendment 3: P8 keeps Amendment 2's h rule
    st = S.st
    days = ["2026-07-09", "2026-07-10", "2026-07-13", "2026-07-14", "2026-07-15", "2026-07-16", "2026-07-17"]
    days = [d for d in days if d in u.day_names]
    res = {"days": days, "h_source_triplet": {}}
    for a in TRIPLET:
        res["h_source_triplet"][S.name_of[a]] = ("first_day" if a in u.h_firstday else ("in_h" if a in u.h else "none"))
    # 07-09: triplet statements while in their isolated rooms
    iso = {}
    for a in TRIPLET:
        rr = st.filter((pl.col("agent") == a) & (pl.col("pt_date") == "2026-07-09") & pl.col("room").is_in([10, 11, 12]))["row"].to_numpy()
        if len(rr) >= 3:
            iso[a] = (unit(S.U[rr].mean(0)), len(rr))
    n_iso_all = {S.name_of[a]: int(st.filter((pl.col("agent") == a) & (pl.col("pt_date") == "2026-07-09")
                                             & pl.col("room").is_in([10, 11, 12])).height) for a in TRIPLET}
    res["n_isolated_statements"] = n_iso_all
    t0 = u.day_names.index("2026-07-09")
    if not iso:
        # No statements were made while isolated (only operators posted in the isolated rooms): fall back to the
        # triplet's full 07-09 vectors, all of which were written in #general after the merge (flagged).
        res["isolated_vectors_available"] = False
        for a in TRIPLET:
            m = (u.agents == a) & (u.day == t0)
            if m.any():
                iso[a] = (u.V[np.where(m)[0][0]], int(u.nstmt[m][0]))
    else:
        res["isolated_vectors_available"] = True
    inc = [i for i in np.where((u.day == t0) & (u.nstmt >= 3))[0] if u.agents[i] not in TRIPLET]
    incv = {u.agents[i]: u.V[i] for i in inc}

    def resid(v, a, b, va):
        F = np.stack([u.ghat, u.h[a], u.h[b]] + [u.ghat_agent[x] for x in (a, b) if x in u.ghat_agent], 1)
        Q, _ = np.linalg.qr(F)
        r1 = v - Q @ (Q.T @ v); r2 = va - Q @ (Q.T @ va)
        return float(r1 @ r2 / (np.linalg.norm(r1) * np.linalg.norm(r2)))
    g_inc = [float(v @ u.ghat) for v in incv.values()]
    g_tri = {S.name_of[a]: float(v[0] @ u.ghat) for a, v in iso.items()}
    res["align_g_0709"] = {"incumbents_mean": float(np.mean(g_inc)), "incumbents_sd": float(np.std(g_inc)), "triplet": g_tri}
    tt = [float(iso[a][0] @ iso[b][0]) for ai, a in enumerate(iso) for b in list(iso)[ai + 1:]]
    ii = [float(incv[a] @ incv[b]) for ai, a in enumerate(incv) for b in list(incv)[ai + 1:]]
    ti = [float(iso[a][0] @ incv[b]) for a in iso for b in incv]
    res["raw_align_0709"] = {"triplet_triplet": tt, "incumbent_incumbent_mean": float(np.mean(ii)), "incumbent_incumbent_q90": float(np.quantile(ii, 0.9)),
                             "triplet_incumbent_mean": float(np.mean(ti))}
    # residual alignment by day: triplet-incumbent vs incumbent-incumbent
    byday = {}
    for d in days:
        t = u.day_names.index(d)
        idx = np.where((u.day == t) & (u.nstmt >= 3))[0]
        vec = {u.agents[i]: u.V[i] for i in idx}
        if d == "2026-07-09":
            for a in iso:
                vec[a] = iso[a][0]
        tri = [a for a in vec if a in TRIPLET and a in u.h]
        incs = [a for a in vec if a not in TRIPLET and a in u.h]
        r_ti = [resid(vec[a], a, b, vec[b]) for a in tri for b in incs]
        r_ii = [resid(vec[a], a, b, vec[b]) for ai, a in enumerate(incs) for b in incs[ai + 1:]]
        r_tt = [resid(vec[a], a, b, vec[b]) for ai, a in enumerate(tri) for b in tri[ai + 1:]]
        byday[d] = {"r_triplet_incumbent": float(np.mean(r_ti)) if r_ti else None, "r_incumbent_incumbent": float(np.mean(r_ii)) if r_ii else None,
                    "r_triplet_triplet": float(np.mean(r_tt)) if r_tt else None, "n_tri": len(tri), "n_inc": len(incs),
                    "se_ti": float(np.std(r_ti) / np.sqrt(max(len(r_ti), 1))) if r_ti else None}
    res["resid_by_day"] = byday
    d0 = byday.get("2026-07-09", {}); d1 = byday.get("2026-07-10", {})
    after = [byday[d]["r_triplet_incumbent"] for d in days[2:] if byday[d]["r_triplet_incumbent"] is not None]
    res["checks"] = {
        "triplet_g_alignment_within_1sd_of_incumbents": bool(g_tri and all(abs(v - np.mean(g_inc)) <= np.std(g_inc) for v in g_tri.values())),
        "triplet_mutual_above_incumbent_q90": bool(tt and np.mean(tt) > np.quantile(ii, 0.9)),
        "ti_below_ii_on_0709": bool(d0.get("r_triplet_incumbent") is not None and d0["r_triplet_incumbent"] < d0["r_incumbent_incumbent"]),
        "ti_rises_0710_and_after": bool(d0.get("r_triplet_incumbent") is not None and d1.get("r_triplet_incumbent") is not None and after
                                        and d1["r_triplet_incumbent"] > d0["r_triplet_incumbent"] and np.mean(after) > d0["r_triplet_incumbent"])}
    return res


# ============================================================================ P9
def p9_rooms(S: Scheme, rng):
    """Descriptive: day-to-day co-fluctuation within vs across rooms in two-room units (+ #40 merged, #51 single room)."""
    out = {}
    for name in P1_UNITS + P1_EXTRA:
        u = S.unit(name)
        out[name] = fluct_rho_rooms(u, rng)
        log("p9r", name, out[name])
    return out


def p9_section(S: Scheme, rng):
    out = {}
    for name, ui in S.units.items():
        if len(ui["days"]) < 2:
            continue
        u = S.unit(name)
        f = mf_fit(u, rng)
        if f is None:
            continue
        nullR = []
        for _ in range(50 if FAST else 100):
            g = mf_fit(permute_unit_days(u, rng), rng, n_split=2)
            if g is not None:
                nullR.append(g["R"])
        jk = []
        for a in np.unique(u.agents):
            m = u.agents != a
            uj = Unit(**{**u.__dict__, "agents": u.agents[m], "day": u.day[m], "room": u.room[m], "V": u.V[m], "nstmt": u.nstmt[m],
                         "rows": [r for r, k in zip(u.rows, m) if k]})
            g = mf_fit(uj, rng, n_split=2)
            if g is not None:
                jk.append(g["bJ_over_n"])
        jk = np.array(jk)
        f.update({"regime": ui["regimes"][0], "goal_no": ui["goal_no"], "n_days": len(ui["days"]),
                  "null_R_mean": float(np.mean(nullR)), "null_R_q95": float(np.quantile(nullR, 0.95)),
                  "p_R_above_null": float((1 + np.sum(np.array(nullR) >= f["R"])) / (1 + len(nullR))),
                  "bJn_jk_se": float(np.sqrt((len(jk) - 1) / len(jk) * np.sum((jk - jk.mean()) ** 2))) if len(jk) > 2 else None})
        out[name] = f
        log("p9", name, {k: round(v, 3) if isinstance(v, float) else v for k, v in f.items()})
    vals = [v["bJ_over_n"] for v in out.values()]
    return {"units": out, "P9": {"n_units": len(out), "max_bJn": float(np.max(vals)), "median_bJn": float(np.median(vals)),
                                 "n_bJn_ge_0.5": int(sum(x >= 0.5 for x in vals)),
                                 "n_upper95_ge_0.5": int(sum((v["bJ_over_n"] + 1.96 * (v["bJn_jk_se"] or 0)) >= 0.5 for v in out.values())),
                                 "pass": bool(all(x < 0.5 for x in vals))}}


def main():
    t0 = time.time()
    rng = np.random.default_rng(SEED + SEED_OFF)
    S = Scheme(d=D, base=OUT / "lexical") if LEX else Scheme(d=D)
    if K != 40:
        S.labels[40] = S.labels[K] if K in S.labels else S.labels[40]
        S.labels = {K: S.labels[K]}
    path = OUT / f"explore{TAG}.json"
    res = json.loads(path.read_text()) if path.exists() else {}
    res["config"] = {"d": D, "k": K, "weight": WEIGHT, "h_mode": H_MODE, "seed_offset": SEED_OFF, "lexical": LEX, "nperm": NPERM, "nnull": NNULL, "M_ent": M_ENT, "R_ent": R_ENT,
                     "M_vec": M_VEC, "R_vec": R_VEC, "fast": FAST}
    if "inv" in ONLY:
        res["invariance"] = invariance(S); log("invariance", json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "per_agent_median"} for k, v in res["invariance"].items()}))
    if "p1" in ONLY:
        res["p1"] = p1_section(S, rng); log("P1", res["p1"]["P1"]); log("P2", res["p1"]["P2"]); log("P3", {k: v for k, v in res["p1"]["P3"].items() if k != "goal_change_jumps"}, f"{time.time()-t0:.0f}s")
    if "p4" in ONLY:
        res["p4"] = p4_section(S, rng); log("P4", res["p4"].get("P4"))
    if "p56" in ONLY:
        res["p56"] = p56_section(S, rng); log("P5", res["p56"]["P5"]); log("P6", {k: v for k, v in res["p56"]["P6"].items() if k != "two_room"}); log("P7", res["p56"]["P7"])
    if "p8" in ONLY:
        res["p8"] = p8_section(S, rng); log("P8", res["p8"])
    if "p9" in ONLY:
        res["p9"] = p9_section(S, rng); log("P9", res["p9"]["P9"])
    if "p9r" in ONLY:
        res["p9_rooms"] = p9_rooms(S, rng)
    path.write_text(json.dumps(res, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    log("done", f"{time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
