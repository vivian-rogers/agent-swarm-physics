"""H102 scheme: statements with their room, domains and hoppers per unit, read-outs per agent-day, field vectors.

Output: data/processed/H102-room-domain-walls/
  statements.parquet       row, srow (row in shared statements), kind, agent, t, pt_date, goal_no, unit, regime,
                           room_at (chat: message room; intentions: as-of rooms_timeline, null t_end -> +inf),
                           self_repeat_both
  x_<variant>_<model>.npy  float16 32-d unit statement vectors (DQ5), variant in {style_resid, white32}
  domains.parquet          unit, agent, home (home domain room), role (core | hopper | stayer), n_other_segments,
                           hours_other (time in the other room during the unit)
  reads_day.parquet        unit, agent, pt_date, calls, n_items (agent items), R_hop (items received while in a room
                           other than the agent's home room), R_dom (items whose sender's home domain differs),
                           posted_other (agent messages posted that day in the other domain's room by others), U
                           (posted_other not received by the agent)
  fields.parquet + fields_<model>.npy   whitened unit room-kickoff vectors (#35-#44) and #51 agent_goal vectors
Units: the goal periods #35-#44 (regime III days only for #36; #35 regime II) and #51 unit 51g (#general/#focus).
Non-holdout only (holdout_mask); the Claude Code agent is excluded. No text is read.

Usage: uv run python hypotheses/H102-room-domain-walls/scheme/build.py
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
from common import REVISION, git_commit, holdout_mask  # noqa: E402
from embed_models import load_whitener  # noqa: E402

SH = ROOT / "data/processed/shared"
ED = SH / "embeddings"
OUT = ROOT / "data/processed/H102-room-domain-walls"
MODELS = ["bge_small", "gte_modernbert"]
SUFFIX = {"bge_small": "", "gte_modernbert": "_gte_modernbert"}
FAR = dt.datetime(2100, 1, 1, tzinfo=dt.timezone.utc)
GOALS = [35, 36, 37, 38, 39, 40, 41, 42, 44, 51]
FOCUS, GENERAL = 15, 0


def rooms_timeline() -> pl.DataFrame:
    return (pl.read_parquet(SH / "rooms_timeline.parquet")
            .with_columns(pl.col("t_end").fill_null(pl.lit(FAR).cast(pl.Datetime("us", "UTC"))))
            .sort("agent", "t_start"))


def statement_rooms(st: pl.DataFrame) -> pl.DataFrame:
    """Room of every statement (duplicated from H100's scheme on purpose: STANDARDS §8 forbids importing it;
    suggested for infra/shared)."""
    rt = rooms_timeline().select("agent", pl.col("t_start").alias("t"), pl.col("room").alias("room_rt"), "t_end")
    s = st.sort("agent", "t")
    j = s.join_asof(rt, on="t", by="agent", strategy="backward")
    j = j.with_columns(pl.when(pl.col("t") < pl.col("t_end")).then(pl.col("room_rt")).otherwise(None).alias("room_rt"))
    return j.with_columns(pl.when(pl.col("kind") == "chat").then(pl.col("room")).otherwise(pl.col("room_rt"))
                          .alias("room_at")).drop("room_rt", "t_end").sort("srow")


def unit_of(goal_no: int, regime: str, unit_id: str, pt_date: str = "") -> str | None:
    if goal_no == 51:
        if unit_id == "51g":
            return "51g"
        return "51tail" if pt_date >= "2026-09-07" else None   # reachable only with the confirm switch
    if goal_no == 36 and regime != "III":
        return None
    if goal_no == 35 and regime != "II":
        return None
    return f"G{goal_no}"


def main(goals=None, allow_holdout=False, write=True):
    """write=False returns the in-memory tables (statements, {(variant, model): X}, domains, reads_day). allow_holdout
    is set only by analysis/confirm.py (guarded); held-out rows are never written."""
    GOALS_ = goals or GOALS
    if write:
        assert not allow_holdout, "held-out rows are never written to disk"
        OUT.mkdir(parents=True, exist_ok=True)
    roster = pl.read_parquet(SH / "roster.parquet")
    cc = roster.filter(pl.col("claude_code"))["agent"].to_list()
    pu = pl.read_parquet(SH / "period_units.parquet").select("unit_id", "goal_no", "days").explode("days") \
        .rename({"days": "pt_date"})

    st = pl.read_parquet(ED / "statements.parquet").with_row_index("srow")
    st = st.filter(pl.col("goal_no").is_in(GOALS_) & ~pl.col("agent").is_in(cc))
    if not allow_holdout:
        st = st.filter(~pl.col("holdout"))
        st = st.filter(pl.Series(~np.array(holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list()))))
    st = st.join(pu, on=["goal_no", "pt_date"], how="left")
    st = st.with_columns(pl.struct("goal_no", "regime", "unit_id", "pt_date").map_elements(
        lambda r: unit_of(r["goal_no"], r["regime"], r["unit_id"], r["pt_date"]), return_dtype=pl.String).alias("unit"))
    st = st.filter(pl.col("unit").is_not_null())
    st = statement_rooms(st)
    fl = pl.read_parquet(SH / "statement_flags.parquet", columns=["srow", "self_repeat_both"])
    st = st.join(fl, on="srow", how="left").sort("srow").with_row_index("row")
    if not allow_holdout:
        assert not any(holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list()))
    st_out = st.select("row", "srow", "kind", "agent", "t", "pt_date", "goal_no", "unit", "regime", "room_at",
                       "self_repeat_both")
    if write:
        st_out.write_parquet(OUT / "statements.parquet", compression="zstd")
    srow = st["srow"].to_numpy()
    Xs = {}
    for m in MODELS:
        for v in ("style_resid", "white32"):
            a = np.load(ED / f"statements_{v}32_{m}.npy" if v == "style_resid" else ED / f"statements_white32_{m}.npy",
                        mmap_mode="r")
            Xs[(v, m)] = np.asarray(a[srow], dtype=np.float16)
            if write:
                np.save(OUT / f"x_{v}_{m}.npy", Xs[(v, m)])

    # ---- domains: home room per (unit, agent); hoppers from rooms_timeline
    rt = rooms_timeline()
    units = st.group_by("unit").agg(pl.col("t").min().alias("t0"), pl.col("t").max().alias("t1"),
                                    pl.col("pt_date").min().alias("d0"), pl.col("pt_date").max().alias("d1"))
    dom_rows = []
    for u in units.sort("unit").to_dicts():
        su = st.filter((pl.col("unit") == u["unit"]) & pl.col("room_at").is_not_null())
        if u["unit"] in ("51g", "51tail"):
            # core = agents with #focus as their modal room on >= 2 days (H47's rule)
            md = (su.group_by("agent", "pt_date", "room_at").len()
                  .sort(["agent", "pt_date", "len"], descending=[False, False, True])
                  .group_by("agent", "pt_date", maintain_order=True).first())
            core = md.filter(pl.col("room_at") == FOCUS).group_by("agent").len().filter(pl.col("len") >= 2)["agent"].to_list()
            home = {a: (FOCUS if a in core else GENERAL) for a in su["agent"].unique().to_list()}
        else:
            hm = (su.group_by("agent", "room_at").len().sort(["agent", "len"], descending=[False, True])
                  .group_by("agent", maintain_order=True).first())
            home = dict(zip(hm["agent"].to_list(), hm["room_at"].to_list()))
            core = []
        rooms_u = sorted(set(home.values()))
        seg = rt.filter((pl.col("t_end") > u["t0"]) & (pl.col("t_start") < u["t1"]))
        for a, h in home.items():
            s_a = seg.filter((pl.col("agent") == a) & (pl.col("room") != h) & pl.col("room").is_in(
                rooms_u if u["unit"] not in ("51g", "51tail") else [FOCUS, GENERAL]))
            hours = float(((s_a["t_end"].clip(upper_bound=u["t1"]) - s_a["t_start"].clip(lower_bound=u["t0"]))
                           .dt.total_seconds() / 3600).sum()) if s_a.height else 0.0
            n_other = s_a.height
            n_other_stat = su.filter((pl.col("agent") == a) & (pl.col("room_at") != h)).height
            role = "core" if a in core else ("hopper" if (n_other > 0 and n_other_stat > 0) or
                                                  (n_other > 0 and hours > 0.25) else "stayer")
            dom_rows.append({"unit": u["unit"], "agent": a, "home": h, "role": role, "n_other_segments": n_other,
                             "hours_other": hours, "n_stat_other_room": n_other_stat})
    dom = pl.DataFrame(dom_rows)
    if write:
        dom.write_parquet(OUT / "domains.parquet")

    # ---- read-outs per (unit, agent, day)
    days = st.select("unit", "pt_date").unique()
    turns = (pl.scan_parquet(SH / "context_ledger_turns.parquet")
             .select("turn_id", "agent", "pt_date", "goal_no", "holdout", "room")
             .filter((~pl.col("holdout") | pl.lit(allow_holdout)) & pl.col("goal_no").is_in(GOALS_)).collect())
    turns = turns.join(pu, on=["goal_no", "pt_date"], how="left").join(days.rename({"unit": "unit_st"}),
                                                                       on="pt_date", how="inner")
    if not allow_holdout:
        turns = turns.filter(~pl.Series(holdout_mask(turns["pt_date"].to_list(), turns["goal_no"].to_list())))
    items = (pl.scan_parquet(SH / "context_ledger_items.parquet").select("turn_id", "message_id", "sender", "kind")
             .filter(pl.col("kind") == "agent").collect())
    items = items.join(turns.select("turn_id", "agent", "pt_date", pl.col("unit_st").alias("unit"),
                                    pl.col("room").alias("room_call")), on="turn_id", how="inner")
    cc_msgs = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "room", "agent", "pt_date",
                                                                 "speaker_kind", "goal_no"])
    items = items.join(cc_msgs.select("message_id", pl.col("room").alias("msg_room")), on="message_id", how="left")
    items = items.join(dom.select("unit", "agent", pl.col("home").alias("home_r")), on=["unit", "agent"], how="left")
    items = items.join(dom.select("unit", pl.col("agent").alias("sender"), pl.col("home").alias("home_s")),
                       on=["unit", "sender"], how="left")
    rd = items.group_by("unit", "agent", "pt_date").agg(
        pl.len().alias("n_items"),
        (pl.col("msg_room") != pl.col("home_r")).sum().alias("R_hop"),
        (pl.col("home_s") != pl.col("home_r")).sum().alias("R_dom"))
    calls = turns.group_by(pl.col("unit_st").alias("unit"), "agent", "pt_date").len().rename({"len": "calls"})
    # posted in the other domain's room that day, by others; U = posted - received
    posted = (cc_msgs.filter(pl.col("speaker_kind") == "agent").join(days, on="pt_date", how="inner")
              .group_by("unit", "pt_date", "room").agg(pl.col("message_id").alias("mids"), pl.len().alias("n")))
    recv = items.group_by("unit", "agent", "pt_date").agg(pl.col("message_id").alias("recv"))
    rows = []
    rd_d = {(r["unit"], r["agent"], r["pt_date"]): r for r in rd.to_dicts()}
    recv_d = {(r["unit"], r["agent"], r["pt_date"]): set(r["recv"]) for r in recv.to_dicts()}
    post_d = {(r["unit"], r["pt_date"], r["room"]): r["mids"] for r in posted.to_dicts()}
    msg_agent = dict(zip(cc_msgs["message_id"].to_list(), cc_msgs["agent"].to_list()))
    homes = {(r["unit"], r["agent"]): r["home"] for r in dom.to_dicts()}
    unit_rooms = {u: sorted(set(dom.filter(pl.col("unit") == u)["home"].to_list())) for u in dom["unit"].unique()}
    for r in calls.to_dicts():
        key = (r["unit"], r["agent"], r["pt_date"])
        h = homes.get((r["unit"], r["agent"]))
        if h is None:
            continue
        others = [x for x in unit_rooms[r["unit"]] if x != h]
        mids = [m for o in others for m in post_d.get((r["unit"], r["pt_date"], o), []) if msg_agent.get(m) != r["agent"]]
        got = recv_d.get(key, set())
        x = rd_d.get(key, {"n_items": 0, "R_hop": 0, "R_dom": 0})
        rows.append({**r, "n_items": x["n_items"], "R_hop": x["R_hop"], "R_dom": x["R_dom"],
                     "posted_other": len(mids), "U": len([m for m in mids if m not in got])})
    rdf = pl.DataFrame(rows).sort("unit", "agent", "pt_date")
    if not write:
        return st_out, Xs, dom, rdf
    rdf.write_parquet(OUT / "reads_day.parquet")

    # ---- fields
    g = pl.read_parquet(ED / "goals.parquet").with_columns(pl.col("kind").cast(pl.String))
    fr, fv = [], {m: [] for m in MODELS}
    sel = g.filter(((pl.col("kind") == "kickoff_room") & pl.col("goal_no").is_in([35, 36, 37, 38, 39, 41, 42, 44]))
                   | ((pl.col("kind") == "agent_goal") & (pl.col("goal_no") == 51)))
    sel = sel.filter(~pl.col("holdout"))
    for m in MODELS:
        gv = np.load(ED / f"goal_vectors{SUFFIX[m]}.npy").astype(np.float32)
        for r in sel.sort("gid").to_dicts():
            W = load_whitener("II" if r["goal_no"] == 35 else "III", 32, m)
            v = W(gv[r["gid"]][None])[0]
            fv[m].append(v / np.linalg.norm(v))
            if m == MODELS[0]:
                fr.append({"gid": r["gid"], "goal_no": r["goal_no"], "kind": r["kind"], "room": r["room"],
                           "agent": r["agent"], "valid_from": r["valid_from"], "valid_to": r["valid_to"]})
    pl.DataFrame(fr).with_row_index("frow").write_parquet(OUT / "fields.parquet")
    for m in MODELS:
        np.save(OUT / f"fields_{m}.npy", np.array(fv[m], dtype=np.float32))

    prov = {"built_by": "hypotheses/H102-room-domain-walls/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["shared/embeddings/statements (+statements_style_resid32_*, statements_white32_*)",
                                   "shared/statement_flags", "shared/rooms_timeline", "shared/period_units",
                                   "shared/roster", "shared/context_ledger_turns", "shared/context_ledger_items",
                                   "shared/chat_core", "shared/embeddings/goals + goal_vectors*",
                                   "shared/embeddings/whitening_*"]}],
            "params": {"units": "G35 (regime II), G36 (36b+c), G37-G44, 51g", "holdout": "excluded (holdout_mask)",
                       "rooms_timeline_null_t_end": "+inf", "focus_core_rule": "#focus modal room on >= 2 days (H47)",
                       "hopper_rule": ">= 1 other-room segment and (>= 1 statement there or > 0.25 h)",
                       "claude_code_excluded": cc},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print(f"statements {st.height}; domains {dom.height}; reads rows {len(rows)}")


if __name__ == "__main__":
    main()
