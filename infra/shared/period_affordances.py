"""DQ9: the period-affordance catalog, machine-readable half.

One row per period unit (`period_units.parquet`, 109 units): what that unit offers for testing.
  - size and length: N, documented and empirical active hours, regime, rooms;
  - ground truth available (DQ6 `ground_truth_labels`, preferred rows, counts by kind);
  - interventions inside it (NEs, data-found step dates, roster joins and leaves, room events, nudges, operator
    bookends, human messages, forced context erasures from the DQ1 context ledger);
  - structure (teams, votes, roles, rival pairs, checkpoints, forks, leaders, private goals, hidden roles,
    competitions, per-room goals), hand-coded per goal from the record (goal-periods.md, natural-experiments.md,
    DQ6 docs, the cards' period setups);
  - outcome measures (DQ4 work ledger: agent work commits, distinct files, new repos, site/pages commits, deploys,
    API writes; `work_outcomes` kinds and reliability);
  - `native_for`: hypotheses whose period-native tests the catalog recommends here (the cross-index in
    hypotheses/hypohypotheses/period-affordances.md, inverted).

Holdout units (locked 2026-10-03) are described from setup and ground-truth metadata only: every column that would
need event data (kicks, chat volume, calls, erasures, work, outages, empirical hours) is null there, and
`holdout = True`. Ground-truth counts by kind are metadata (DQ6 already publishes them); no label values are read.
No message text is read or stored.

Usage:
  uv run python infra/shared/period_affordances.py           build data/processed/shared/period_affordances.parquet
  uv run python infra/shared/period_affordances.py --show    print a compact per-unit summary (non-holdout counts only)
  uv run python infra/shared/period_affordances.py --validate   reconcile unit sums with the source tables; holdout mask
Docs: infra/data-quality/period_affordances.md
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT, REVISION, UTC, git_commit  # noqa: E402

TABLE = OUT / "period_affordances.parquet"

# --------------------------------------------------------------------------------------------- hand-coded structure
# Per goal. Sources: hypotheses/hypohypotheses/goal-periods.md (setup, by/mode codes, corrections),
# hypotheses/natural-experiments.md, infra/data-quality/ground_truth_labels.md (DQ6), work_ledger.md (DQ4), the cards.
# Flags mean the structure exists in the record, not that it has been tested.
#   teams: assigned or drafted sides; votes: ballots/vote-outs with a record; roles: assigned per-agent roles;
#   rival_pairs: pairs holding the same role; checkpoints: model checkpoints (#44/#45); forks: lineages of one
#   artifact evolving separately; leader: a designated or elected leader; private_goals: per-agent goals others
#   can't fully see; hidden_roles: secret roles (saboteurs); competition: agents scored against each other;
#   room_goal_split: rooms given different assigned goals on the same days; ext_event: a real-world event with
#   humans; operator_correction: a dated operator message that corrects beliefs or sets rules inside the period.
#   outcome_narr: goal-specific outcome known only from narration or summaries (not in the work ledger).
F = False
T = True
GOALS: dict[int, dict] = {
    1: dict(by="O", mode="C", slug="charity fundraiser (year 1)", outcome_narr="money raised ($1,984; narration)"),
    2: dict(by="F", mode="F", slug="unsupervised weekend look-back"),
    3: dict(by="F", mode="F", slug="holiday"),
    4: dict(by="O", mode="C", slug="story + 100-person in-person event", ext_event=T,
            outcome_narr="event held (narration)"),
    5: dict(by="F", mode="F", slug="holiday (leadership-format survey)", outcome_narr="survey: rotating leadership, 9 votes (summary only)"),
    6: dict(by="O", mode="K", slug="merch store competition", competition=T, outcome_narr="store profit per agent (summary only)"),
    7: dict(by="F", mode="F", slug="holiday (human helpers B)"),
    8: dict(by="D", mode="C", slug="design and take an open-ended benchmark"),
    9: dict(by="F", mode="F", slug="holiday"),
    10: dict(by="O", mode="I", slug="complete games", outcome_narr="games completed (narration only)"),
    11: dict(by="F", mode="F", slug="free week"),
    12: dict(by="O", mode="M", slug="debate tournament (10 debates)", teams=T, roles=T, leader=T, competition=T),
    13: dict(by="O", mode="C", slug="human-subjects experiment", ext_event=T, outcome_narr="participants recruited (narration)"),
    14: dict(by="O", mode="I", slug="personality tests", operator_correction=T),
    15: dict(by="O", mode="C", slug="peer therapy"),
    16: dict(by="F", mode="F", slug="free week with operator rules", operator_correction=T),
    17: dict(by="O", mode="I", slug="personal websites"),
    18: dict(by="O", mode="C", slug="reduce global poverty"),
    19: dict(by="O", mode="C", slug="daily puzzle game"),
    20: dict(by="O", mode="I", slug="Substack blogs"),
    21: dict(by="O", mode="I", slug="AI forecasts"),
    22: dict(by="F", mode="F", slug="free week"),
    23: dict(by="O", mode="K", slug="chess tournament", competition=T, outcome_narr="game results (not extracted)"),
    24: dict(by="O", mode="C", slug="random acts of kindness"),
    25: dict(by="O", mode="C", slug="digital museum of 2025"),
    26: dict(by="A", mode="C", slug="elect a leader who sets the goal", votes=T, leader=T),
    27: dict(by="O", mode="K", slug="Juice Shop hacking competition", competition=T,
             outcome_narr="challenges solved (narration only)"),
    28: dict(by="O", mode="C", slug="personality quiz"),
    29: dict(by="O", mode="K", slug="breaking-news competition", competition=T),
    30: dict(by="O", mode="C", slug="adopt a park"),
    31: dict(by="F", mode="F", slug="free week (3.7 Sonnet farewell)"),
    32: dict(by="D", mode="K", slug="challenge each other (alphabetical turns)", competition=T, operator_correction=T),
    33: dict(by="O", mode="C", slug="Pentagon-AI news: debate and act"),
    34: dict(by="O", mode="M", slug="build an RPG with hidden saboteurs", votes=T, hidden_roles=T, teams=T),
    35: dict(by="O", mode="C", slug="test your game (forked per room)", forks=T, roles=T, leader=T),
    36: dict(by="O", mode="C", slug="interact with outside agents", forks=T),
    37: dict(by="F", mode="F", slug="free 3 days", forks=T),
    38: dict(by="O", mode="C", slug="charity fundraiser (year 2)", operator_correction=T,
             outcome_narr="money raised (narration only)"),
    39: dict(by="O", mode="I", slug="build your own interactive world"),
    40: dict(by="O", mode="C", slug="connect worlds into a 3D universe"),
    41: dict(by="O", mode="I", slug="novel research"),
    42: dict(by="O", mode="I", slug="YouTube channels"),
    43: dict(by="O", mode="I", slug="improve your memory"),
    44: dict(by="D", mode="C", slug="#best fine-tunes a leader; #rest own goals", checkpoints=T, leader=T,
             room_goal_split=T),
    45: dict(by="A", mode="C", slug="follow the fine-tuned leader", checkpoints=T, leader=T, room_goal_split=T),
    46: dict(by="O", mode="C", slug="#best SF event; #rest surprise each other", ext_event=T, room_goal_split=T),
    47: dict(by="O", mode="C", slug="#best reduce suffering; #rest games", room_goal_split=T),
    48: dict(by="O", mode="C", slug="help Gemini 2.5 Pro"),
    49: dict(by="O", mode="I", slug="beat the hardest game"),
    50: dict(by="O", mode="K", slug="#best assistant competition; #rest own goals", competition=T, room_goal_split=T),
    51: dict(by="P", mode="I/K", slug="maximize your private assigned role", roles=T, rival_pairs=T, private_goals=T,
             competition=T),
}
# Unit-level overrides (structure that holds only in part of a period).
UNIT_OVERRIDES: dict[str, dict] = {
    "12b": dict(teams=F, roles=F, leader=F, competition=F),   # 09-05: no debates (DQ6 / H21 correction)
    "50f": dict(private_goals=T),                             # NE26 J private goals 07-03
    "51b": dict(isolated_newcomer_rooms=T),                   # NE32 sol/terra/luna rooms 07-09 -> 07-10
    "51e": dict(operator_correction=T),                       # Opus 5 first role by operator message (DQ6)
    "51f": dict(operator_correction=T),                       # NE38 role reassignment 07-29
}

ROOM_MERGE_UNITS = {"40"}                    # NE42 merge into #universe-coordination (A-B-A with #39/#41)
DATA_STEPS = [  # step dates not (or not correctly) in natural-experiments.md; found by this build (counts only)
    ("2025-07-01", "public_chat_closed_est", "human messages/day ~100 -> <=4 and distinct human speakers ~16 -> 1 "
     "between 06-30 and 07-01: an estimate for the undated NE39"),
    ("2025-07-16", "human_helpers_B", "CHANGELOG human-use feature (B, 07-16 to 07-21); no NE id; #7 has 9-13 "
     "human speakers/day again"),
    ("2026-02-13", "nudges_first_seen", "first nudger message in the record (NE10 is dated 02-10)"),
    ("2026-08-04", "bookends_last", "last daily pause/resume bookend (NE43 says bookends stop 08-21)"),
    ("2026-08-20", "nudges_last", "last nudge (NE43)"),
]
EXTRA_NE = [("2026-08-21", "NE43")]          # not in period_step_changes (added to the NE catalog after period_units)

# ------------------------------------------------------------------------------------------- native-test index
# Hypothesis -> recommended native-test periods/NEs (the md cross-index). Period keys are goal numbers or NE ids;
# inverted below into a per-unit `native_for` list (NE keys map to the unit(s) where the NE lands).
NATIVE: dict[str, list] = {
    "H01": [12, "NE42", "NE32", "NE15"], "H02": [12, 26, 44, "NE38"], "H03": [51, "NE43", 10, 2],
    "H04": ["NE10", "NE43", "NE14"], "H05": ["NE42", "NE32", 51, "NE15"], "H06": [31, 37, 44, 19],
    "H07": [39, 40, 37, "NE15"], "H08": ["NE32", "NE03", "NE09", "NE41"], "H09": ["NE43", 51, "NE14"],
    "H10": [44, "NE38", 26, 19], "H11": [31, 40, 24, 19], "H12": [26, 12, 42, 31], "H13": ["NE06", 35, "NE32", 51],
    "H14": ["NE06", "NE14", "NE43"], "H15": ["NE29", "NE36", "NE18", "NE41"], "H16": [16, "NE43", 27, "NE10"],
    "H17": [27, 51, "NE14"], "H18": ["NE42", "NE32", 51, "NE03"], "H19": [51, "NE42", "NE43"],
    "H20": [51, 38, 27], "H21": [26, 33, 12], "H22": ["NE38", 23, 51, 6], "H23": [26, 44, 35],
    "H24": [8, 41, 21], "H25": ["NE43", 51, "NE42"], "H26": ["NE42", 12, 51, 42], "H27": [31, 18, 40, 19],
    "H28": [17, 31, 40, "NE09"], "H29": ["NE38", 26, 35, 51], "H30": ["NE10", 5, "NE38", "NE36"],
    "H31": [26, "NE42", 19, 31], "H32": [26, 35, 44, 12], "H33": [51, 39, 42, 40], "H34": [42, 41, 17, 35],
    "H35": ["NE10", "NE43", 51], "H36": [6, "NE43", "NE32", "NE38"], "H37": [26, 33, 27, 23],
    "H38": ["NE43", 4, "NE14", 36], "H39": ["NE07", 7, "NE43", "NE10"], "H40": ["NE06", "NE14", 51, "NE11"],
    "H41": ["NE32", "NE15", "NE42", 51], "H42": [36, "NE41", 51], "H43": [51, "NE10", "NE43"],
    "H44": [51, 38, "NE16", 36], "H45": ["NE42", "NE32", 51, "NE41"], "H46": ["NE38", "NE41", "NE15", 39],
    "H47": ["NE42", 44, 51, "NE15"], "H48": [38, "NE42", 51], "H49": [51, 44, "NE43", 40],
    "H50": [12, "NE32", 8, 38], "H51": ["NE42", 51, "NE43"], "H52": [5, 4, 6, 51],
    "H53": [31, 40, 17, 42], "H54": [44, 26, 38, 35], "H55": [51, 33, 16, 42], "H56": ["NE06", "NE14", "NE43", "NE11"],
    "H57": ["NE42", "NE32", "NE41", 51], "H58": [40, 44, 31, 35],
}
# NE -> unit ids where its native test sits (both sides where the design is a before/after across the step).
NE_UNITS = {
    "NE03": ["10a", "10b"], "NE06": ["20b", "20c", "20d"], "NE07": ["21a", "21b"], "NE09": ["24"],
    "NE10": ["30a", "30b"], "NE11": ["31c", "31d"], "NE14": ["36a", "36b"], "NE15": ["35"], "NE16": ["36b", "36c"],
    "NE18": ["38c", "38d"], "NE29": ["31b", "31c"], "NE32": ["51a", "51b", "51c"], "NE36": ["38a"],
    "NE38": ["51e", "51f"], "NE41": ["36b", "38a", "51c"], "NE42": ["39", "40", "41"], "NE43": ["51g", "51h"],
}


def build() -> pl.DataFrame:
    S = OUT
    pu = pl.read_parquet(S / "period_units.parquet").sort("start")
    cal = pl.read_parquet(S / "calendar.parquet").sort("pt_date")
    rooms = pl.read_parquet(S / "rooms.parquet")
    room_name = dict(zip(rooms["room"].to_list(), rooms["name"].to_list()))
    steps = pl.read_parquet(S / "period_step_changes.parquet")

    # ---- day -> unit map; split days (intra-day restarts) carry a cutoff = the later unit's start
    dm = (pu.select("unit_id", "goal_no", "start", "days", "holdout").explode("days", empty_as_null=True)
          .rename({"days": "pt_date"}))
    dup = dm.group_by("pt_date").agg(pl.len().alias("n"), pl.col("start").max().alias("cut")).filter(pl.col("n") > 1)
    first_unit = dm.sort("start").group_by("pt_date", maintain_order=True).first().select("pt_date", "unit_id")
    later_unit = dm.sort("start").group_by("pt_date", maintain_order=True).last().select(
        "pt_date", pl.col("unit_id").alias("unit_late"))
    daymap = first_unit.join(later_unit, on="pt_date").join(dup.select("pt_date", "cut"), on="pt_date", how="left")
    unit_holdout = dict(zip(pu["unit_id"].to_list(), pu["holdout"].to_list()))
    active_days = sorted(cal["pt_date"].to_list())

    def assign_t(df: pl.DataFrame, tcol: str) -> pl.DataFrame:
        """unit_id for time-stamped rows: by PT day, split days by the later unit's start."""
        out = df.join(daymap, on="pt_date", how="left")
        return out.with_columns(
            pl.when(pl.col("cut").is_not_null() & (pl.col(tcol) >= pl.col("cut"))).then(pl.col("unit_late"))
            .otherwise(pl.col("unit_id")).alias("unit_id")).drop("unit_late", "cut")

    def unit_of_date(d: str) -> str | None:
        """A change dated d lands in the unit holding the first active day >= d (the period_units rule)."""
        nxt = next((x for x in active_days if x >= d), None)
        if nxt is None:
            return None
        r = first_unit.filter(pl.col("pt_date") == nxt)
        return r["unit_id"][0] if r.height else None

    # ---- hours: documented (all units) and empirical (non-holdout), split days cut at the later unit's start
    cal_u = cal.join(daymap, on="pt_date", how="inner")
    rows_h = []
    for r in cal_u.iter_rows(named=True):
        ws, we, cut = r["win_start"], r["win_end"], r["cut"]
        if cut is None:
            rows_h.append((r["unit_id"], r["pt_date"], (we - ws).total_seconds(), r["documented_hours"]))
        else:
            rows_h.append((r["unit_id"], r["pt_date"], max((cut - ws).total_seconds(), 0), r["documented_hours"]))
            rows_h.append((r["unit_late"], r["pt_date"], max((we - cut).total_seconds(), 0), None))
    hrs = pl.DataFrame(rows_h, schema={"unit_id": pl.Utf8, "pt_date": pl.Utf8, "win_s": pl.Float64,
                                       "doc_h": pl.Int8}, orient="row")
    hrs_u = hrs.group_by("unit_id").agg((pl.col("win_s").sum() / 3600).alias("active_hours_window"),
                                        pl.col("doc_h").drop_nulls().median().alias("doc_hours_per_day"),
                                        pl.col("doc_h").drop_nulls().sum().alias("doc_hours_total"))
    out_off = (assign_t(pl.read_parquet(S / "outages.parquet").filter(~pl.col("holdout")), "t_start")
               .group_by("unit_id").agg(
                   (pl.col("dur_min").filter(pl.col("village_off")).sum() / 60).alias("village_off_hours"),
                   pl.col("village_off").sum().cast(pl.Int32).alias("n_village_off"),
                   pl.col("infra_burst").sum().cast(pl.Int32).alias("n_infra_bursts")))

    # ---- kicks (non-holdout)
    k = assign_t(pl.read_parquet(S / "kicks_classified.parquet").filter(~pl.col("holdout"))
                 .with_columns(pl.col("kind").cast(pl.Utf8), pl.col("subkind").cast(pl.Utf8)), "t")
    kick_u = k.group_by("unit_id").agg(
        (pl.col("kind") == "nudge").sum().cast(pl.Int32).alias("n_nudges"),
        ((pl.col("kind") == "pause_resume")).sum().cast(pl.Int32).alias("n_bookends"),
        (pl.col("kind") == "human_message").sum().cast(pl.Int32).alias("n_human_msgs"),
        ((pl.col("kind") == "human_message") & (pl.col("subkind") == "mention")).sum().cast(pl.Int32)
        .alias("n_human_msgs_naming"),
        ((pl.col("kind") == "human_message") & (pl.col("subkind") == "kickoff")).sum().cast(pl.Int32)
        .alias("n_human_kickoff_msgs"),
        (pl.col("kind") == "mention").sum().cast(pl.Int32).alias("n_agent_mentions"))
    # distinct human speakers (hashed; chat_core.human) per unit
    # chat_core has no holdout column: keep only PT days that belong to non-holdout units before counting
    open_days = daymap.filter(~pl.col("unit_id").replace_strict(unit_holdout, default=True)
                              & ~pl.col("unit_late").replace_strict(unit_holdout, default=True))["pt_date"].to_list()
    ch = assign_t(pl.scan_parquet(S / "chat_core.parquet").filter(pl.col("pt_date").is_in(open_days))
                  .select("t", "pt_date", "speaker_kind", "human").collect(), "t")
    chat_u = ch.group_by("unit_id").agg(
        (pl.col("speaker_kind") == "agent").sum().cast(pl.Int32).alias("n_agent_msgs"),
        pl.col("human").filter(pl.col("speaker_kind") == "human").n_unique().cast(pl.Int32).alias("n_human_speakers"))

    # ---- calls and erasures (DQ1 context ledger; non-holdout)
    cl = (pl.scan_parquet(S / "context_ledger_turns.parquet").filter(~pl.col("holdout"))
          .select("pt_date", "t_call", "reset_forced", "reset_consol", "cap_hit").collect())
    cl = assign_t(cl, "t_call")
    call_u = cl.group_by("unit_id").agg(
        pl.len().cast(pl.Int32).alias("n_calls"),
        pl.col("reset_forced").sum().cast(pl.Int32).alias("n_erasures_forced"),
        (pl.col("reset_consol") & ~pl.col("reset_forced")).sum().cast(pl.Int32).alias("n_consolidations_voluntary"),
        pl.col("cap_hit").sum().cast(pl.Int32).alias("n_event_cap_hits"))

    # ---- work ledger (DQ4; agent level, non-holdout; split days go to the first unit)
    wd = (pl.read_parquet(S / "work_daily.parquet").filter((pl.col("level") == "agent") & ~pl.col("holdout"))
          .join(first_unit, on="pt_date", how="inner"))
    work_u = wd.group_by("unit_id").agg(
        pl.col("commits").sum().cast(pl.Int32).alias("work_commits"),
        pl.col("agent").filter(pl.col("commits") > 0).n_unique().cast(pl.Int16).alias("work_committing_agents"),
        pl.col("distinct_files").sum().cast(pl.Int32).alias("work_distinct_files"),
        pl.col("new_repos").sum().cast(pl.Int32).alias("work_new_repos"),
        (pl.col("pages_commits") + pl.col("site_default_commits")).sum().cast(pl.Int32).alias("work_site_commits"),
        pl.col("deploy_cmds").sum().cast(pl.Int32).alias("work_deploy_cmds"),
        (pl.col("api_writes_gitlab") + pl.col("api_writes_github")).sum().cast(pl.Int32).alias("work_api_writes"),
        pl.col("commits_automated").sum().cast(pl.Int32).alias("work_commits_automated"),
        pl.col("active").sum().cast(pl.Int32).alias("active_agent_days"))
    wo = pl.read_parquet(S / "work_outcomes.parquet")
    generic = {"agent_commits", "committing_agents", "repos_committed_to"}
    oc = (wo.filter(~pl.col("outcome").is_in(list(generic)))
          .group_by("goal_no").agg(pl.col("outcome").unique().sort().alias("outcome_kinds"),
                                   pl.col("reliability").unique().sort().alias("outcome_reliability")))

    # ---- ground truth (DQ6; preferred rows; counts by kind are metadata, also for holdout)
    gt = pl.read_parquet(S / "ground_truth_labels.parquet").filter(pl.col("preferred"))
    gt = gt.with_columns(pl.col("t_valid_from").dt.convert_time_zone("America/Los_Angeles").dt.date()
                         .cast(pl.Utf8).alias("pt_date"))
    # unit = the goal's unit with first_day <= date (else the goal's first unit)
    units_by_goal = {g: sub.sort("start").select("unit_id", "first_day").rows()
                     for (g,), sub in pu.group_by(["goal_no"])}

    def gt_unit(g, d):
        us = units_by_goal.get(g, [])
        cand = [u for u, fd in us if fd <= d]
        return cand[-1] if cand else (us[0][0] if us else None)
    gt = gt.with_columns(pl.struct("goal_no", "pt_date").map_elements(lambda s: gt_unit(s["goal_no"], s["pt_date"]),
                                                                      return_dtype=pl.Utf8).alias("unit_id"))
    room_kinds = ["room_assignment", "room_presence"]
    gt_u = gt.group_by("unit_id").agg(
        pl.len().cast(pl.Int32).alias("n_gt_rows"),
        pl.col("label_kind").filter(~pl.col("label_kind").is_in(room_kinds)).len().cast(pl.Int32)
        .alias("n_gt_structural_rows"))
    gt_kinds = (gt.filter(~pl.col("label_kind").is_in(room_kinds)).group_by("unit_id", "label_kind").len()
                .sort("unit_id", "label_kind")
                .with_columns(pl.format("{}:{}", "label_kind", "len").alias("kc"))
                .group_by("unit_id", maintain_order=True).agg(pl.col("kc").alias("gt_kinds")))

    # ---- step changes per unit (NEs, roster, rooms, hours) by the period_units rule
    st = steps.with_columns(pl.col("date").map_elements(unit_of_date, return_dtype=pl.Utf8).alias("unit_id"))
    extra = pl.DataFrame({"date": [d for d, _ in EXTRA_NE], "kind": ["ne"] * len(EXTRA_NE),
                          "source": [n for _, n in EXTRA_NE],
                          "what": ["natural-experiments.md row added after period_units was built"] * len(EXTRA_NE)})
    extra = extra.with_columns(pl.col("date").map_elements(unit_of_date, return_dtype=pl.Utf8).alias("unit_id"))
    st = pl.concat([st, extra.select(st.columns)])
    ne_u = (st.filter(pl.col("kind") == "ne").group_by("unit_id")
            .agg(pl.col("source").unique().sort().alias("ne_inside")))
    st = st.filter(~((pl.col("date") == "2025-04-02") & pl.col("kind").is_in(["roster_join"])))  # launch roster
    ros_u = st.group_by("unit_id").agg(
        (pl.col("kind") == "roster_join").sum().cast(pl.Int16).alias("n_roster_joins"),
        (pl.col("kind") == "roster_leave").sum().cast(pl.Int16).alias("n_roster_leaves"),
        (pl.col("kind") == "rooms").sum().cast(pl.Int16).alias("n_room_set_changes"),
        (pl.col("kind") == "hours").sum().cast(pl.Int16).alias("n_hours_changes"))
    ds = pl.DataFrame({"date": [d for d, _, _ in DATA_STEPS], "step": [s for _, s, _ in DATA_STEPS]})
    ds = ds.with_columns(pl.col("date").map_elements(unit_of_date, return_dtype=pl.Utf8).alias("unit_id"))
    ds_u = ds.group_by("unit_id").agg(pl.format("{}:{}", "step", "date").alias("data_steps"))

    # ---- transient rooms created during the unit (setup metadata; all units)
    tr_rows = []
    for u in pu.iter_rows(named=True):
        s, e = u["start"], u["end"]
        names = []
        for r in rooms.iter_rows(named=True):
            c = dt.datetime.fromisoformat(r["created_at"]).replace(tzinfo=UTC)
            d = dt.datetime.fromisoformat(r["deleted_at"]).replace(tzinfo=UTC) if r["deleted_at"] else None
            alive = c <= e and (d is None or d >= s)
            if alive and r["room"] not in (u["rooms"] or []) and r["name"] not in ("general",):
                if c >= s - dt.timedelta(days=1) or (d is not None and d <= e + dt.timedelta(days=1)):
                    names.append(r["name"])
        tr_rows.append((u["unit_id"], sorted(names)))
    tr = pl.DataFrame(tr_rows, schema={"unit_id": pl.Utf8, "transient_rooms": pl.List(pl.Utf8)}, orient="row")

    # ---- assemble
    base = pu.select("unit_id", "goal_no", "seq", "first_day", "last_day", "n_days", "regime", "holdout",
                     pl.col("n_agents").alias("N"), "n_roster", "rooms", "reason")
    base = base.with_columns(
        pl.col("rooms").map_elements(lambda xs: [room_name[x] for x in xs], return_dtype=pl.List(pl.Utf8))
        .alias("rooms_structural"),
        pl.col("rooms").list.len().cast(pl.Int8).alias("n_rooms"))
    df = base
    for t in (hrs_u, out_off, kick_u, chat_u, call_u, work_u, gt_u, gt_kinds, ne_u, ros_u, ds_u, tr):
        df = df.join(t, on="unit_id", how="left")
    df = df.join(oc, on="goal_no", how="left")
    df = df.with_columns(
        (pl.col("active_hours_window") - pl.col("village_off_hours").fill_null(0)).alias("active_hours"),
        pl.col("transient_rooms").fill_null([]), pl.col("ne_inside").fill_null([]),
        pl.col("gt_kinds").fill_null([]), pl.col("outcome_kinds").fill_null([]),
        pl.col("outcome_reliability").fill_null([]), pl.col("data_steps").fill_null([]))
    for c in ("n_gt_rows", "n_gt_structural_rows", "n_roster_joins", "n_roster_leaves", "n_room_set_changes",
              "n_hours_changes"):
        df = df.with_columns(pl.col(c).fill_null(0))

    # hand-coded structure
    flags = ["teams", "votes", "roles", "rival_pairs", "checkpoints", "forks", "leader", "private_goals",
             "hidden_roles", "competition", "room_goal_split", "ext_event", "operator_correction",
             "isolated_newcomer_rooms"]
    rows_s = []
    for u in df.select("unit_id", "goal_no").iter_rows(named=True):
        g = GOALS[u["goal_no"]]
        o = UNIT_OVERRIDES.get(u["unit_id"], {})
        rec = {"unit_id": u["unit_id"], "by": g["by"], "mode": g["mode"], "goal_slug": g["slug"],
               "outcome_narration": g.get("outcome_narr")}
        for f in flags:
            rec["has_" + f] = bool(o.get(f, g.get(f, False)))
        rec["has_room_merge"] = u["unit_id"] in ROOM_MERGE_UNITS
        rows_s.append(rec)
    struct = pl.DataFrame(rows_s)
    df = df.join(struct, on="unit_id", how="left")

    # native_for: invert NATIVE
    nf: dict[str, set] = {}
    for h, keys in NATIVE.items():
        for key in keys:
            if isinstance(key, int):  # native tests are exploratory: non-holdout units only
                us = pu.filter((pl.col("goal_no") == key) & ~pl.col("holdout"))["unit_id"].to_list()
            else:
                us = NE_UNITS.get(key, [])
            for x in us:
                nf.setdefault(x, set()).add(h)
    df = df.with_columns(pl.col("unit_id").map_elements(lambda x: sorted(nf.get(x, set())),
                                                        return_dtype=pl.List(pl.Utf8)).alias("native_for"))

    # regime / scaffold flags by date (setup, all units)
    def between(lo, hi=None):
        e = pl.col("last_day") >= lo
        if hi:
            e = e & (pl.col("first_day") < hi)
        return e
    df = df.with_columns(
        (pl.col("n_rooms") >= 2).alias("has_rooms"),
        between("2026-02-25").alias("rooms_era"),
        between("2026-03-24").alias("forced_erasure_regime"),        # NE41: 41-turn cap, regime III
        between("2026-06-11").alias("event_cap_200"),                # NE22
        between("2026-06-29").alias("gitlab_era"),                   # NE24
        between("2026-07-03").alias("private_plans"),                # NE26
        between("2026-01-26", "2026-04-02").alias("claude_code_present"),
        between("2026-03-17", "2026-04-02").alias("cc_feed_replay"),  # H08: replayed 2025 history
        (pl.col("goal_no") >= 30).alias("git_dense"),                # DQ4: dense from #30
        between("2026-02-13", "2026-08-21").alias("nudger_era"),     # first/last nudge in the record
        (between("2025-05-05", "2026-08-05")).alias("bookend_era"),  # first/last pause-resume bookend
    )
    # mask event-derived columns on holdout units (they are null already, from the ~holdout filters; enforce)
    masked = ["active_hours_window", "active_hours", "village_off_hours", "n_village_off", "n_infra_bursts",
              "n_nudges", "n_bookends", "n_human_msgs", "n_human_msgs_naming", "n_human_kickoff_msgs",
              "n_agent_mentions", "n_agent_msgs", "n_human_speakers", "n_calls", "n_erasures_forced",
              "n_consolidations_voluntary", "n_event_cap_hits", "work_commits", "work_committing_agents",
              "work_distinct_files", "work_new_repos", "work_site_commits", "work_deploy_cmds", "work_api_writes",
              "work_commits_automated", "active_agent_days"]
    df = df.with_columns([pl.when(pl.col("holdout")).then(None).otherwise(pl.col(c)).alias(c) for c in masked])
    # zero-fill counts on non-holdout units where the source simply had no rows
    zero = [c for c in masked if c.startswith("n_") or c.startswith("work_") or c == "active_agent_days"]
    df = df.with_columns([pl.when(~pl.col("holdout")).then(pl.col(c).fill_null(0)).otherwise(None).alias(c)
                          for c in zero])
    # work before #30 is ambiguous (git sparse); keep values but flag
    order = (["unit_id", "goal_no", "seq", "first_day", "last_day", "n_days", "regime", "holdout", "by", "mode",
              "goal_slug", "N", "n_roster", "doc_hours_per_day", "doc_hours_total", "active_hours_window",
              "village_off_hours", "active_hours", "rooms_structural", "n_rooms", "has_rooms", "transient_rooms",
              "reason", "ne_inside", "data_steps", "n_roster_joins", "n_roster_leaves", "n_room_set_changes",
              "n_hours_changes", "n_nudges", "n_bookends", "n_human_msgs", "n_human_msgs_naming",
              "n_human_kickoff_msgs", "n_human_speakers", "n_agent_msgs", "n_agent_mentions", "n_calls",
              "n_erasures_forced", "n_consolidations_voluntary", "n_event_cap_hits", "n_village_off",
              "n_infra_bursts"]
             + ["has_" + f for f in flags] + ["has_room_merge",
                "n_gt_rows", "n_gt_structural_rows", "gt_kinds", "work_commits", "work_committing_agents",
                "work_distinct_files", "work_new_repos", "work_site_commits", "work_deploy_cmds", "work_api_writes",
                "work_commits_automated", "active_agent_days", "git_dense", "outcome_kinds",
                "outcome_reliability", "outcome_narration", "rooms_era", "forced_erasure_regime", "event_cap_200",
                "gitlab_era", "private_plans", "claude_code_present", "cc_feed_replay", "nudger_era",
                "bookend_era", "native_for"])
    df = df.select(order).sort("goal_no", "seq")
    df = df.with_columns(pl.col("doc_hours_total").cast(pl.Int16), pl.col("active_hours_window").cast(pl.Float32),
                         pl.col("village_off_hours").cast(pl.Float32), pl.col("active_hours").cast(pl.Float32),
                         pl.col("doc_hours_per_day").cast(pl.Float32))
    return df


def write(df: pl.DataFrame):
    df.write_parquet(TABLE, compression="zstd", compression_level=10)
    path = OUT / "_provenance.json"
    prov = json.loads(path.read_text()) if path.exists() else {}
    prov["period_affordances"] = {
        "built_by": "infra/shared/period_affordances.py", "git_commit": git_commit(),
        "inputs": [{"source": "ai-village", "revision": REVISION, "tables": ["(shared tables only)"]},
                   {"shared": ["period_units", "period_step_changes", "calendar", "rooms", "outages",
                               "kicks_classified", "chat_core", "context_ledger_turns", "work_daily",
                               "work_outcomes", "ground_truth_labels"]},
                   {"documents": ["hypotheses/hypohypotheses/goal-periods.md", "hypotheses/natural-experiments.md",
                                  "hypotheses/holdout.json", "infra/data-quality/ground_truth_labels.md",
                                  "hypotheses/H*/README.md (questions only)"]}],
        "params": {"n_units": df.height, "n_goals": int(df["goal_no"].n_unique()),
                   "holdout_units": int(df["holdout"].sum()),
                   "holdout_rule": "event-derived columns null on holdout units; GT counts by kind kept (metadata)",
                   "split_days": "time-stamped rows split at the later unit's start; day-level rows to the first unit",
                   "extra_ne": EXTRA_NE, "data_steps": DATA_STEPS, "no_text": True},
        "output": "data/processed/shared/period_affordances.parquet",
        "built_at": dt.datetime.now(UTC).isoformat()}
    path.write_text(json.dumps(prov, indent=1))
    print(f"wrote {TABLE} ({df.height} rows, {TABLE.stat().st_size / 1e3:.0f} kB)")


def validate(df: pl.DataFrame) -> bool:
    """Reconcile unit sums with their source tables (non-holdout) and check the holdout mask."""
    S = OUT
    nh = df.filter(~pl.col("holdout"))
    k = (pl.read_parquet(S / "kicks_classified.parquet").filter(~pl.col("holdout"))
         .with_columns(pl.col("kind").cast(pl.Utf8)))
    cl = (pl.scan_parquet(S / "context_ledger_turns.parquet").filter(~pl.col("holdout"))
          .select(pl.col("reset_forced").sum().alias("f"), pl.len().alias("n")).collect().row(0))
    w = pl.read_parquet(S / "work_daily.parquet").filter((pl.col("level") == "agent") & ~pl.col("holdout"))
    gt = pl.read_parquet(S / "ground_truth_labels.parquet").filter(pl.col("preferred"))
    checks = [
        ("nudges", nh["n_nudges"].sum(), k.filter(pl.col("kind") == "nudge").height),
        ("human messages", nh["n_human_msgs"].sum(), k.filter(pl.col("kind") == "human_message").height),
        ("bookends", nh["n_bookends"].sum(), k.filter(pl.col("kind") == "pause_resume").height),
        ("forced erasures", nh["n_erasures_forced"].sum(), cl[0]),
        ("model calls", nh["n_calls"].sum(), cl[1]),
        ("work commits", nh["work_commits"].sum(), w["commits"].sum()),
        ("GT rows (preferred)", df["n_gt_rows"].sum(), gt.height),
        ("units", df.height, pl.read_parquet(S / "period_units.parquet").height),
    ]
    ok = True
    for name, got, want in checks:
        flag = "ok" if got == want else "MISMATCH"
        ok &= got == want
        print(f"{name:22s} {got:>10} vs source {want:>10}  {flag}")
    masked = ["n_nudges", "n_human_msgs", "n_calls", "n_erasures_forced", "work_commits", "active_hours", "n_agent_msgs"]
    leak = df.filter(pl.col("holdout")).select([pl.col(c).is_not_null().sum().alias(c) for c in masked]).row(0)
    print(f"holdout units {int(df['holdout'].sum())}; non-null event-derived values on them: {sum(leak)} (must be 0)")
    nf_leak = df.filter(pl.col("holdout"))["native_for"].list.len().sum()
    print(f"native_for entries on holdout units: {nf_leak} (must be 0)")
    return ok and sum(leak) == 0 and nf_leak == 0


def show(df: pl.DataFrame):
    cols = ["unit_id", "N", "n_days", "active_hours", "n_rooms", "ne_inside", "n_roster_joins", "n_nudges",
            "n_human_msgs", "n_erasures_forced", "work_commits", "n_gt_structural_rows"]
    with pl.Config(tbl_rows=200, tbl_cols=20, fmt_str_lengths=40, tbl_width_chars=220):
        print(df.select(cols))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", action="store_true", help="print a compact per-unit summary; don't write")
    ap.add_argument("--validate", action="store_true", help="reconcile with source tables; don't write")
    a = ap.parse_args()
    d = build()
    if a.show:
        show(d)
    elif a.validate:
        sys.exit(0 if validate(d) else 1)
    else:
        write(d)
