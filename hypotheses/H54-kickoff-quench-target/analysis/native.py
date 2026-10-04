"""H54 period-native tests: G51 (private goals) + NE38 (Opus 5 reassignment), G44 and G38 (two room instructions),
G26 (election kickoff + the elected leader's goal announcement). Predictions N1-N4 in the card and period READMEs.

Writes data/processed/H54-kickoff-quench-target/G51/native.json, G44/native.json, G38/native.json, G26/native.json.
Usage: uv run python native.py [--only g51,g44,g38,g26]
"""
from __future__ import annotations

import argparse
import datetime as dt

import numpy as np
import polars as pl

import h54est as E
import h54lib as L

RNG = np.random.default_rng(5454)
UTC = dt.timezone.utc


def load():
    st, Z, ZS = L.load_stmt()
    return st.with_row_index("i"), Z, ZS


def agent_vecs(s, Z, n_min=3, by=("agent",)):
    g = s.group_by(list(by)).agg(pl.col("i"), pl.len().alias("n")).filter(pl.col("n") >= n_min).sort(list(by))
    V = np.vstack([E.unit(Z[np.asarray(ix)].mean(0)) for ix in g["i"].to_list()]) if g.height else np.zeros((0, L.D))
    return g, V


def decoy_kicks(p, regime):
    el = [q for q in L.eligible() if q != p]
    return np.vstack([L.gvec(q, "kickoff", regime=regime) for q in el])


# ----------------------------------------------------------------------------------------------- G51
def g51(st, Z):
    p, r = 51, "III"
    G = L.goals().filter(pl.col("kind") == "agent_goal")
    G = G.filter(pl.col("valid_to").is_null())               # current goal per agent (drops #42's same-day superseded row)
    gt = pl.read_parquet(L.SHARED / "ground_truth_labels.parquet").filter(
        (pl.col("goal_no") == 51) & (pl.col("label_kind") == "role") & pl.col("preferred")
        & (pl.col("t_valid_from") < dt.datetime(2026, 9, 7, tzinfo=UTC)))
    role_of = dict(zip(gt["agent"].to_list(), gt["value"].to_list()))
    s51 = st.filter((pl.col("goal_no") == 51) & (pl.col("src_goal") == 51) & (pl.col("day") >= 1) & ~pl.col("pre_kick"))
    gv, roles, V, agents, first_day = [], [], [], [], {}
    for row in G.sort("agent").iter_rows(named=True):
        a = row["agent"]
        sa = s51.filter((pl.col("agent") == a) & (pl.col("pt_date") >= row["valid_from"]))
        if a == 40:   # NE38: role reassigned on 07-29; use its days from 07-29 for the "first day" of the current goal
            sa = sa.filter(pl.col("t") >= dt.datetime(2026, 7, 29, 16, 51, tzinfo=UTC))
        days = sa.group_by("pt_date").len().filter(pl.col("len") >= 3).sort("pt_date")
        if days.height == 0:
            continue
        d = days["pt_date"][0]
        z = Z[sa.filter(pl.col("pt_date") == d)["i"].to_numpy()]
        V.append(E.unit(z.mean(0)))
        gv.append(L.whiten_unit(L.goal_raw()[row["gid"]][None], r)[0])
        roles.append(role_of.get(a, f"own{a}"))
        agents.append(a)
        first_day[a] = d
    V, Gm = np.vstack(V), np.vstack(gv)
    ur = {x: i for i, x in enumerate(sorted(set(roles)))}
    rc = np.array([ur[x] for x in roles])
    acc, npairs = E.swap_pairs(V, Gm, rc)
    pperm = E.swap_perm_p(V, Gm, rc, n_perm=5000, rng=RNG)
    S = V @ Gm.T
    pis = []
    for i in range(len(V)):
        dec = [j for j in range(len(V)) if rc[j] != rc[i]]
        pis.append(float(np.mean(S[i, dec] < S[i, i])))
    ca = E.centered_alignment(V, Gm)
    # permutation null for the centered alignment (permute goals by role)
    obs_ca = float(ca.mean())
    cnt = 0
    for _ in range(5000):
        perm = dict(zip(ur.values(), RNG.permutation(list(ur.values()))))
        rep = {c: np.flatnonzero(rc == c)[0] for c in ur.values()}
        G2 = np.vstack([Gm[rep[perm[c]]] for c in rc])
        cnt += E.centered_alignment(V, G2).mean() >= obs_ca
    k51 = L.gvec(51, "kickoff", regime=r)
    Dk = decoy_kicks(51, r)
    ex_goal = np.array([S[i, i] - np.mean(S[i, rc != rc[i]]) for i in range(len(V))])
    ex_kick = V @ k51 - (V @ Dk.T).mean(1)
    orig = np.array([first_day[a] == "2026-07-06" for a in agents])
    res = {"n_agents": len(V), "n_roles": len(ur), "n_pairs": npairs, "swap_accuracy": acc, "p_perm": pperm,
           "own_goal_pct_median": float(np.median(pis)), "own_goal_pct_mean": float(np.mean(pis)), "own_goal_top1": float(np.mean(np.array(pis) == 1.0)),
           "centered_alignment_mean": obs_ca, "centered_alignment_p": (cnt + 1) / 5001, "centered_alignment_pos_rate": float(np.mean(ca > 0)),
           "excess_own_goal_median": float(np.median(ex_goal)), "excess_shared_kickoff_median": float(np.median(ex_kick)),
           "own_goal_beats_kickoff_rate": float(np.mean(ex_goal > ex_kick)),
           "originals": {"n": int(orig.sum()), "swap_accuracy": E.swap_pairs(V[orig], Gm[orig], rc[orig])[0]},
           "late_joiners": {"n": int((~orig).sum()), "own_goal_pct_median": float(np.median(np.array(pis)[~orig])) if (~orig).any() else None}}
    # persistence over the head: weekly swap accuracy
    weeks = []
    days_all = sorted(s51["pt_date"].unique().to_list())
    d0 = dt.date(2026, 7, 6)
    s51w = s51.with_columns(((pl.col("pt_date").str.to_date() - d0).dt.total_days() // 7).alias("wk"))
    aidx = {a: i for i, a in enumerate(agents)}
    for wk in sorted(s51w["wk"].unique().to_list()):
        sw = s51w.filter((pl.col("wk") == wk) & pl.col("agent").is_in(agents))
        if 40 in agents:
            sw = sw.filter(~((pl.col("agent") == 40) & (pl.col("t") < dt.datetime(2026, 7, 29, 16, 51, tzinfo=UTC))))
        g, Vw = agent_vecs(sw, Z, 5)
        if g.height < 6:
            continue
        ii = np.array([aidx[a] for a in g["agent"].to_list()])
        a_w, n_w = E.swap_pairs(Vw, Gm[ii], rc[ii])
        weeks.append({"week": int(wk), "n_agents": g.height, "swap_accuracy": a_w, "n_pairs": n_w})
    res["weekly"] = weeks
    res["days_used"] = [days_all[0], days_all[-1]]
    # NE38: Opus 5 (agent 40), game-dev goal shared with 24/26 before 07-29 16:51 UTC, math goal after
    res["NE38"] = ne38(st, Z, G)
    return res


def ne38(st, Z, G):
    r = "III"
    t_re = dt.datetime(2026, 7, 29, 16, 51, tzinfo=UTC)
    g_new = L.whiten_unit(L.goal_raw()[G.filter(pl.col("agent") == 40)["gid"][0]][None], r)[0]
    g_old = L.whiten_unit(L.goal_raw()[G.filter(pl.col("agent") == 24)["gid"][0]][None], r)[0]   # game-dev goal (shared role)
    s = st.filter((pl.col("goal_no") == 51) & (pl.col("src_goal") == 51) & (pl.col("day") >= 1))
    s = s.with_columns((pl.col("t") >= t_re).alias("post"))
    rows = []
    for (a, d, post), grp in s.group_by("agent", "pt_date", "post"):
        if grp.height < 3:
            continue
        v = E.unit(Z[grp["i"].to_numpy()].mean(0))
        rows.append({"agent": a, "pt_date": d, "post": post, "new": float(v @ g_new), "old": float(v @ g_old)})
    D = pl.DataFrame(rows)
    D = D.filter((pl.col("pt_date") >= "2026-07-24") & (pl.col("pt_date") <= "2026-08-07"))
    me = D.filter(pl.col("agent") == 40)
    ctrl = D.filter(~pl.col("agent").is_in([40, 24, 26])).group_by("pt_date", "post").agg(pl.col("new").mean(), pl.col("old").mean())

    def did(col, me_, ct_):
        a = me_.filter(pl.col("post"))[col].mean() - me_.filter(~pl.col("post"))[col].mean()
        b = ct_.filter(pl.col("post"))[col].mean() - ct_.filter(~pl.col("post"))[col].mean()
        return a - b, a, b
    out = {}
    for col in ("new", "old"):
        est, a, b = did(col, me, ctrl)
        boots = []
        mp, mq = me.filter(pl.col("post")), me.filter(~pl.col("post"))
        cp, cq = ctrl.filter(pl.col("post")), ctrl.filter(~pl.col("post"))
        for _ in range(2000):
            def bs(df):
                return df[RNG.integers(0, df.height, df.height)] if df.height else df
            e2, _, _ = did(col, pl.concat([bs(mp), bs(mq)]), pl.concat([bs(cp), bs(cq)]))
            boots.append(e2)
        out[col] = {"did": float(est), "opus5_change": float(a), "control_change": float(b),
                    "ci95": [float(np.nanpercentile(boots, 2.5)), float(np.nanpercentile(boots, 97.5))],
                    "n_pre_days": mq.height, "n_post_days": mp.height}
    out["window"] = ["2026-07-24", "2026-08-07"]
    out["series_opus5"] = me.sort("pt_date", "post").to_dicts()
    out["series_control"] = ctrl.sort("pt_date", "post").to_dicts()
    return out


# ----------------------------------------------------------------------------------------------- two-room periods
def rooms_day1(st, p):
    """Agent -> room on day 1: DQ6 room_assignment where available (#44), else the modal room of day-1 chat."""
    s = st.filter((pl.col("goal_no") == p) & (pl.col("src_goal") == p) & (pl.col("day") == 1) & ~pl.col("pre_kick"))
    modal = (s.filter(pl.col("kind") == "chat").group_by("agent", "room").len().sort("len", descending=True)
             .group_by("agent").first())
    rm = dict(zip(modal["agent"].to_list(), modal["room"].to_list()))
    gt = pl.read_parquet(L.SHARED / "ground_truth_labels.parquet").filter(
        (pl.col("goal_no") == p) & (pl.col("label_kind") == "room_assignment") & pl.col("preferred"))
    if gt.height:
        code = {"best": 2, "rest": 3}
        for a, v in zip(gt["agent"].to_list(), gt["value"].to_list()):
            if v in code:
                rm[a] = code[v]
    return s, rm


def two_rooms(st, Z, p):
    r = L.period_regime(p)
    s, rm = rooms_day1(st, p)
    g, V = agent_vecs(s, Z, 3)
    keep = [i for i, a in enumerate(g["agent"].to_list()) if rm.get(a) in (2, 3)]
    agents = [g["agent"][i] for i in keep]
    V = V[keep]
    rooms = np.array([rm[a] for a in agents])
    kr = {room: L.gvec(p, "kickoff_room", room=room, regime=r) for room in (2, 3)}
    rs = E.room_swap(V, rooms, kr)
    u = kr[2] - kr[3]
    d_obs = E.axis_separation(V, rooms, u)        # room 2 minus room 3 along (k2 - k3): predicted > 0
    el = L.eligible()
    K = np.vstack([L.gvec(q, "kickoff", regime=r) for q in el if q != p])
    null = np.array([E.axis_separation(V, rooms, K[i] - K[j]) for i in range(len(K)) for j in range(i + 1, len(K))])
    null = null[np.isfinite(null)]
    # spread and depth per room
    per_room = {}
    Dk = decoy_kicks(p, r)
    for room in (2, 3):
        m = rooms == room
        groups = [Z[np.asarray(ix)] for a, ix in zip(g["agent"].to_list(), g["i"].to_list()) if rm.get(a) == room]
        per_room[str(room)] = {"n": int(m.sum()), "q_rare": E.rarefied_q(groups, L.N_RARE, 100, RNG),
                               "q": E.pairwise_q(V[m]) if m.sum() >= 2 else None,
                               "depth_own_room_kick": float(np.mean(V[m] @ kr[room]) - np.mean(V[m] @ Dk.T)) if m.sum() else None,
                               "align_own": float(np.mean(V[m] @ kr[room])) if m.sum() else None,
                               "align_other": float(np.mean(V[m] @ kr[5 - room])) if m.sum() else None}
    # permutation of room labels (agent-level) for the room-swap accuracy
    cnt = 0
    for _ in range(5000):
        cnt += E.room_swap(V, RNG.permutation(rooms), kr)["accuracy"] >= rs["accuracy"]
    res = {"regime": r, "n_agents": len(V), "rooms": {str(k): int((rooms == k).sum()) for k in (2, 3)},
           "kick_room_cos": float(kr[2] @ kr[3]), "room_swap": rs, "room_swap_p_perm": (cnt + 1) / 5001,
           "axis_d": d_obs, "axis_pct_abs": float(np.mean(np.abs(null) < abs(d_obs))), "axis_pct_signed": float(np.mean(null < d_obs)),
           "n_null_axes": int(len(null)), "per_room": per_room,
           "projections": {str(room): (V[rooms == room] @ E.unit(u)).round(4).tolist() for room in (2, 3)}}
    # HH181 inside each room: first plan centrality (room-level plans)
    fp = pl.read_parquet(L.OUT / "first_plans.parquet").filter(pl.col("goal_no") == p)
    res["first_plans"] = fp.select("scope", "agent", "words", "has_art", "rank_in_day", "min_after_kick").to_dicts()
    return res


# ----------------------------------------------------------------------------------------------- G26
def g26(st, Z):
    p, r = 26, "I"
    info = __import__("json").loads((L.OUT / "g26_leader.json").read_text())
    mid = info["message_id"]
    t_star = dt.datetime.fromisoformat(info["t"])
    e_star = L.chat_vec([mid], r)[0]
    s = st.filter((pl.col("goal_no") == p) & (pl.col("src_goal") == p) & (pl.col("day") >= 1) & (pl.col("agent") != 17))
    tf = pl.read_parquet(L.SHARED / "text_features.parquet", columns=["message_id", "agent", "t", "pt_date", "goal_no", "words"])
    day1 = s.filter(pl.col("day") == 1)["pt_date"][0]
    dec_ids = tf.filter((pl.col("goal_no") == p) & (pl.col("pt_date") == day1) & (pl.col("words") >= 60)
                        & (pl.col("agent") != 17) & (pl.col("agent") != L.CLAUDE_CODE))["message_id"].to_list()
    ED = L.chat_vec(dec_ids, r)
    ED = ED[np.all(np.isfinite(ED), axis=1)]

    def cen(a0, a1):
        w = s.filter((pl.col("t") >= t_star + dt.timedelta(minutes=a0)) & (pl.col("t") < t_star + dt.timedelta(minutes=a1)))
        g = w.group_by("agent").agg(pl.col("i"))
        if g.height < 3:
            return None, g.height
        return E.unit(np.vstack([E.unit(Z[np.asarray(ix)].mean(0)) for ix in g["i"].to_list()]).mean(0)), g.height
    out = {"t_star": info["t"], "n_decoys": int(len(ED))}
    cb, nb = cen(-60, 0)
    for lab, (a0, a1) in {"0-60min": (0, 60), "60-180min": (60, 180), "rest_of_day1": (0, 600)}.items():
        ca, na = cen(a0, a1)
        if cb is None or ca is None:
            continue
        a = float((ca - cb) @ e_star)
        ad = (ca - cb) @ ED.T
        out[lab] = {"a_star": a, "decoy_mean": float(ad.mean()), "excess": a - float(ad.mean()), "pct": float(np.mean(ad < a)),
                    "n_before": nb, "n_after": na}
    # daily: kickoff vs leader announcement as targets (excess over decoys)
    k = L.gvec(p, "kickoff", regime=r)
    Dk = decoy_kicks(p, r)
    daily = []
    for d in sorted(s["day"].unique().to_list()):
        sd = s.filter(pl.col("day") == d)
        if d == 1:
            sd = sd.filter(pl.col("t") >= t_star)
        g, V = agent_vecs(sd, Z, 3)
        if g.height < 3:
            continue
        daily.append({"day": d, "n": g.height, "ex_kick": float(np.mean(V @ k) - np.mean(V @ Dk.T)),
                      "ex_leader": float(np.mean(V @ e_star) - np.mean(V @ ED.T))})
    # before t* on day 1
    g, V = agent_vecs(s.filter((pl.col("day") == 1) & (pl.col("t") < t_star) & ~pl.col("pre_kick")), Z, 3)
    if g.height >= 3:
        daily.insert(0, {"day": "1-pre", "n": g.height, "ex_kick": float(np.mean(V @ k) - np.mean(V @ Dk.T)),
                         "ex_leader": float(np.mean(V @ e_star) - np.mean(V @ ED.T))})
    out["daily"] = daily
    # projects named by the announcement vs H31 #26 events
    am = pl.read_parquet(L.SHARED / "artifact_mentions.parquet").filter(pl.col("message_id") == mid)
    import sys
    sys.path.insert(0, str(L.ROOT / "infra/shared"))
    from project_states import project_map
    pm = project_map()
    named = set(am.join(pm, on="artifact")["project"].to_list())
    pr = pl.read_parquet(L.OUT / "projects.parquet").filter((pl.col("src") == "H31") & (pl.col("goal_no") == 26))
    pa = pm.group_by("project").agg(pl.col("artifact").min())
    art2proj = dict(zip(pa["artifact"].to_list(), pa["project"].to_list()))
    out["announcement_projects"] = len(named)
    out["h31_26"] = [{"cls": rr["cls"], "named_by_announcement": art2proj.get(rr["artifact"]) in named, "t0_h": rr["t0_h"],
                      "named_by_kickoff": rr["named"]} for rr in pr.iter_rows(named=True)]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="g51,g44,g38,g26")
    a = ap.parse_args()
    st, Z, _ = load()
    only = a.only.split(",")
    if "g51" in only:
        res = g51(st, Z)
        L.write_json(L.OUT / "G51" / "native.json", res)
        print("G51", {k: v for k, v in res.items() if k not in ("weekly", "NE38")})
        print("weekly", res["weekly"])
        print("NE38", {k: v for k, v in res["NE38"].items() if k != "series_opus5"})
    for p in (44, 38):
        if f"g{p}" in only:
            res = two_rooms(st, Z, p)
            L.write_json(L.OUT / f"G{p}" / "native.json", res)
            print(f"G{p}", {k: v for k, v in res.items() if k not in ("projections",)})
    if "g26" in only:
        res = g26(st, Z)
        L.write_json(L.OUT / "G26" / "native.json", res)
        print("G26", res)
    L.provenance("analysis/native.py", ["H54 stmt tables", "goal_fields (agent_goal, kickoff_room)", "ground_truth_labels (DQ6)",
                                        "text_features", "artifact_mentions", "chat bge-small"], {"rng": 5454})


if __name__ == "__main__":
    main()
