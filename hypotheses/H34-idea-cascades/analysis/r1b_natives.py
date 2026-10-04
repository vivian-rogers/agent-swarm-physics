"""H34 round 1b natives and estimates (2026-10-04). Predictions: goalperiod-subhypotheses/G35/README.md and G26/README.md
(written 16:50 UTC, before this script was run). Reads the round-1b trees (H34_DATA=r1b build, ledger visibility).

  uv run python hypotheses/H34-idea-cascades/analysis/r1b_natives.py natives     # -> r1b/results/natives.json
  uv run python hypotheses/H34-idea-cascades/analysis/r1b_natives.py estimates   # -> shared per_period_estimates (role exploratory)
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402

DATA = ROOT / "data/processed/H34-idea-cascades/r1b"
SH = ROOT / "data/processed/shared"
US = 1_000_000


def gt(goal):
    g = pl.read_parquet(SH / "ground_truth_labels.parquet").filter(
        (pl.col("goal_no") == goal) & pl.col("preferred") & ~pl.col("holdout"))
    return g


def seed_table(goal):
    """One row per idea seeded in the period: seeder agent, seed time, seed room, size of the seed's tree."""
    fu = pl.read_parquet(DATA / f"G{goal:02d}" / "first_uses.parquet")
    tr = pl.read_parquet(DATA / f"G{goal:02d}" / "trees.parquet")
    seeds = fu.filter(pl.col("status") == 0).select("idea", "agent", "pos", "t_us", "tree")
    seeds = seeds.join(tr.select("idea", "tree", "size"), on=["idea", "tree"], how="left")
    chat = pl.read_parquet(SH / "chat_core.parquet", columns=["goal_no", "pt_date", "room"]).with_row_index("msg").filter(
        pl.col("goal_no") == goal)
    # pos is the index into the period's (non-holdout, time-sorted) message rows: rebuild that ordering
    meta = json.loads((DATA / f"G{goal:02d}" / "meta.json").read_text())
    days = meta["days"]
    assert not any(holdout_mask(days, [goal] * len(days)))
    rows = chat.filter(pl.col("pt_date").is_in(days)).sort("msg")
    room = rows["room"].fill_null(-1).to_numpy()
    pdate = rows["pt_date"].to_numpy()
    return seeds.with_columns(pl.Series("room", room[seeds["pos"].to_numpy()]), pl.Series("pt_date", pdate[seeds["pos"].to_numpy()]))


def ratio_ci(lead_sizes, other_sizes, strata_lead=None, strata_other=None, B=2000, seed=0):
    """P(s >= 2) ratio (leader-seeded / other-seeded), pooled over strata by MH weights; idea bootstrap."""
    rng = np.random.default_rng(seed)
    sl, so = np.asarray(lead_sizes), np.asarray(other_sizes)
    stl = np.zeros(len(sl), int) if strata_lead is None else np.asarray(strata_lead)
    sto = np.zeros(len(so), int) if strata_other is None else np.asarray(strata_other)

    def mh(il, io):
        num = den = 0.0
        for k in np.unique(np.r_[stl, sto]):
            a, b = sl[il][stl[il] == k], so[io][sto[io] == k]
            n1, n0 = len(a), len(b)
            if n1 == 0 or n0 == 0:
                continue
            x1, x0 = (a >= 2).sum(), (b >= 2).sum()
            T = n1 + n0
            num += x1 * n0 / T
            den += x0 * n1 / T
        return num / den if den > 0 else np.nan
    est = mh(np.arange(len(sl)), np.arange(len(so)))
    bs = np.array([mh(rng.integers(0, len(sl), len(sl)), rng.integers(0, len(so), len(so))) for _ in range(B)])
    bs = bs[np.isfinite(bs)]
    return dict(ratio=float(est), ci95=np.quantile(bs, [0.025, 0.975]).tolist(), n_lead=int(len(sl)), n_other=int(len(so)),
                p2_lead=float((sl >= 2).mean()) if len(sl) else None, p2_other=float((so >= 2).mean()) if len(so) else None,
                mean_lead=float(sl.mean()) if len(sl) else None, mean_other=float(so.mean()) if len(so) else None)


def native_35():
    st = seed_table(35)
    g = gt(35).filter(pl.col("label_kind") == "leader")
    rooms = pl.read_parquet(SH / "rooms.parquet")
    rmap = dict(zip(rooms["name"].to_list(), rooms["room"].to_list())) if "name" in rooms.columns else {}
    lead_s, oth_s, lst, ost, per = [], [], [], [], []
    for k, r in enumerate(g.sort("t_valid_from").iter_rows(named=True)):
        day = (r["t_valid_from"] - dt.timedelta(hours=7)).date().isoformat()
        rname = r["detail"].split(";")[0].replace("room=", "").strip()
        room = rmap.get(rname, rmap.get("#" + rname))
        sub = st.filter((pl.col("pt_date") == day) & (pl.col("room") == room))
        a = sub.filter(pl.col("agent") == r["agent"])["size"].to_numpy()
        b = sub.filter(pl.col("agent") != r["agent"])["size"].to_numpy()
        lead_s += list(a); oth_s += list(b); lst += [k] * len(a); ost += [k] * len(b)
        per.append(dict(day=day, room=rname, room_code=room, leader=int(r["agent"]), n_lead=int(len(a)), n_other=int(len(b)),
                        p2_lead=float((a >= 2).mean()) if len(a) else None, p2_other=float((b >= 2).mean()) if len(b) else None))
    res = dict(per_room_day=per, pooled=ratio_ci(lead_s, oth_s, lst, ost, seed=35))
    # N35b: cross-room first uses (agent's room != seed room) classified exposed
    fu = pl.read_parquet(DATA / "G35" / "first_uses.parquet").filter(pl.col("status") > 0)
    seeds = st.select("idea", pl.col("room").alias("seed_room"))
    chat_room = pl.read_parquet(SH / "chat_core.parquet", columns=["goal_no", "pt_date", "room"]).with_row_index("msg").filter(
        pl.col("goal_no") == 35)
    meta = json.loads((DATA / "G35" / "meta.json").read_text())
    rr = chat_room.filter(pl.col("pt_date").is_in(meta["days"])).sort("msg")["room"].fill_null(-1).to_numpy()
    fu = fu.with_columns(pl.Series("room", rr[fu["pos"].to_numpy()])).join(seeds, on="idea", how="left")
    cross = fu.filter(pl.col("room") != pl.col("seed_room"))
    res["N35b"] = dict(cross_room_first_uses=cross.height, exposed=int((cross["status"] == 1).sum()),
                       share_exposed=float((cross["status"] == 1).mean()) if cross.height else None,
                       within_room_share_exposed=float((fu.filter(pl.col("room") == pl.col("seed_room"))["status"] == 1).mean()))
    return res


def native_26():
    st = seed_table(26)
    g = gt(26).filter(pl.col("label_kind") == "leader").sort("t_valid_from")
    t0 = int(g["t_valid_from"].min().timestamp() * US)
    w = st.filter(pl.col("t_us") >= t0)
    a = w.filter(pl.col("agent") == 17)["size"].to_numpy()
    b = w.filter(pl.col("agent") != 17)["size"].to_numpy()
    res = dict(window_start=str(g["t_valid_from"].min()), pooled=ratio_ci(a, b, seed=26))
    pre = st.filter(pl.col("t_us") < t0)
    res["pre_election"] = dict(n_lead=int((pre["agent"] == 17).sum()), n_other=int((pre["agent"] != 17).sum()))
    # N26b: ideas seeded per agent message in the window
    cc = pl.read_parquet(SH / "chat_core.parquet", columns=["goal_no", "pt_date", "t", "speaker_kind", "agent"]).filter(
        (pl.col("goal_no") == 26) & (pl.col("speaker_kind") == "agent") & (pl.col("t").dt.epoch("us") >= t0))
    days = json.loads((DATA / "G26" / "meta.json").read_text())["days"]
    cc = cc.filter(pl.col("pt_date").is_in(days))
    m17, mo = int((cc["agent"] == 17).sum()), int((cc["agent"] != 17).sum())
    res["N26b"] = dict(msgs_lead=m17, msgs_other=mo, seeds_per_msg_lead=len(a) / max(m17, 1), seeds_per_msg_other=len(b) / max(mo, 1))
    res["N26b"]["ratio"] = res["N26b"]["seeds_per_msg_lead"] / res["N26b"]["seeds_per_msg_other"]
    return res


def natives():
    out = {"G35": native_35(), "G26": native_26()}
    (DATA / "results" / "natives.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, indent=1, default=float))


def estimates():
    from estimates import write_estimates, map_unit
    pt = pl.read_parquet(DATA / "results" / "period_table.parquet").filter(pl.col("cls") == "ALL")
    rows = []
    for r in pt.iter_rows(named=True):
        g = int(r["goal"])
        days = json.loads((DATA / f"G{g:02d}" / "meta.json").read_text())["days"]
        base = dict(goal_no=g, period_unit=map_unit(g, days[0], days[-1]), first_day=days[0], last_day=days[-1],
                    role="replication", method="H34.r1b_ledger", channel="content", n=float(r["nodes"]), n_kind="agent first uses",
                    source="data/processed/H34-idea-cascades/r1b/results/period_table.parquet")
        def add(stat, v, lo, hi, kind, null=None, notes=None):
            rows.append({**base, "statistic": stat, "estimate": v, "ci_lo": lo, "ci_hi": hi, "ci_kind": kind, "null": null,
                         "notes": notes})
        add("R_hat", r["R"], r["R_lo"], r["R_hi"], "percentile", notes="idea-cluster bootstrap; ledger visibility")
        add("HR10", r["hr10"], r["hr10_lo"], r["hr10_hi"], "profile", null="no-exposure turns, idea-stratified")
        add("R_c", r["R_c"], r["R_c_lo"], r["R_c_hi"], "profile")
        if r.get("hr_seen5") is not None:
            add("HR_seen5", r["hr_seen5"], r["hr_seen5_lo"], r["hr_seen5_hi"], "profile", null="H57: no use in last 5 min")
            add("HR_unread5", r["hr_unread5"], r["hr_unread5_lo"], r["hr_unread5_hi"], "profile",
                null="H57: no use in last 5 min", notes="placebo: same-room uses not yet read by the producing call")
    nat = json.loads((DATA / "results" / "natives.json").read_text())
    for g, key in ((35, "G35"), (26, "G26")):
        days = json.loads((DATA / f"G{g:02d}" / "meta.json").read_text())["days"]
        q = nat[key]["pooled"]
        rows.append(dict(goal_no=g, period_unit=map_unit(g, days[0], days[-1]), first_day=days[0], last_day=days[-1],
                         role="native", method="H34.r1b_leader_seed", channel="content", statistic="P2_ratio_leader_seeded",
                         estimate=q["ratio"], ci_lo=q["ci95"][0], ci_hi=q["ci95"][1], ci_kind="percentile",
                         n=float(q["n_lead"] + q["n_other"]), n_kind="seeded ideas", null="other agents' seeds, same window",
                         source="data/processed/H34-idea-cascades/r1b/results/natives.json"))
    write_estimates(rows, "H34")
    print(len(rows), "rows")


if __name__ == "__main__":
    {"natives": natives, "estimates": estimates}[sys.argv[1] if len(sys.argv) > 1 else "natives"]()
