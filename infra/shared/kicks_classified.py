"""Shared classified kicks: every outside or peer impulse to an agent, with its kind, targets and recipients.
Merges H04's nudge-to-target mapping (hypotheses/H04-reversible-forcing/analysis/h04lib.py: load_messages) and H16's
kick classes (hypotheses/H16-metastable-traps-kramers/analysis/h16lib.py: load_kicks; also H35, H39), using the
corrected mentions (chat_mentions_clean.mentions_roster: o1-bug-free, restricted to that day's roster).

Kinds (one row per message, plus one row per goal start):
  nudge          automated message addressed to agents (automated + >= 1 roster mention, or starting with '@': 3
                 messages whose @-name the mention regex cannot parse have empty targets); targeted
  pause_resume   automated daily bookend ("pausing / resuming the village", "resuming for today"; subkind pause /
                 resume); untargeted. These never carry roster mentions.
  automated_other  any other automated message (0 at build time; kept so nothing is silently dropped)
  human_message  human speaker; subkind kickoff (the goal_fields kickoff rule: >= 250 chars within [-10, +45] min of
                 a goal's first-day window, or that day's fallback), mention (names >= 1 roster agent), plain
  mention        agent message naming >= 1 other roster agent (the agent @-mention / name-mention kick)
  goal_kickoff   village_goals start time (one row per goal; targets = everyone; no message)
Columns: t, kind, subkind, targeted, room, speaker (agent code for `mention`, else null), targets (list of agent codes:
  mentions_roster), n_targets, recipients (list: agents in the room who would see it, from exposure; excludes the
  speaker), msg (row index into chat_core sorted by t, the key exposure uses), message_id, goal_no, pt_date, holdout,
  ref (goal number for goal_kickoff). No text, no human identities (chat_core.human hashes are not copied).
H16's (message, recipient) classes follow from explode(recipients): A_men = mention & recipient in targets;
H_men / H_und = human & recipient in / not in targets; N_tgt / N_by = nudge & recipient in / not in targets (H16 only
counts recipients in the room; H04 also counts nudge targets outside the room: targets | recipients).
All days; `holdout` flags locked-holdout days.

Output: data/processed/shared/kicks_classified.parquet
Usage: uv run python infra/shared/kicks_classified.py            (build)
       uv run python infra/shared/kicks_classified.py --verify   (counts vs H04's load_messages and H16's load_kicks,
                                                                  non-holdout days; imports their code read-only)
"""
from __future__ import annotations

import os

for _v, _n in (("POLARS_MAX_THREADS", "2"), ("OMP_NUM_THREADS", "2"), ("OPENBLAS_NUM_THREADS", "2"),
               ("MKL_NUM_THREADS", "2"), ("VECLIB_MAXIMUM_THREADS", "2")):
    os.environ.setdefault(_v, _n)

import importlib.util  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT, ROOT, load_goals, write_provenance  # noqa: E402
from goal_fields import kickoff_messages  # noqa: E402

PAUSE_RX = r"(?i)paus\w* the village"
RESUME_RX = r"(?i)resum\w* (?:the village|for today)"
ADDRESSED_RX = r"^\s*@"


def build() -> pl.DataFrame:
    chat = pl.read_parquet(OUT / "chat_core.parquet", columns=["message_id", "t", "pt_date", "goal_no", "room", "speaker_kind", "agent"])
    men = pl.read_parquet(OUT / "chat_mentions_clean.parquet", columns=["message_id", "mentions_roster"])
    assert chat.height == men.height and (chat["message_id"] == men["message_id"]).all(), "chat_mentions_clean misaligned"
    chat = chat.with_row_index("msg").with_columns(men["mentions_roster"].alias("targets"),
                                                   pl.col("speaker_kind").cast(pl.String).alias("sk"))
    chat = chat.filter((pl.col("sk") != "agent") | (pl.col("targets").list.len() > 0))
    # automated: text flags only (never stored)
    auto_ids = chat.filter(pl.col("sk") == "automated").select("message_id")
    txt = (pl.read_parquet(OUT / "chat_text.parquet", columns=["message_id", "text"]).join(auto_ids, on="message_id", how="semi")
           .select("message_id", pl.col("text").str.contains(PAUSE_RX).alias("is_pause"),
                   pl.col("text").str.contains(RESUME_RX).alias("is_resume"),
                   pl.col("text").str.contains(ADDRESSED_RX).alias("addressed")))
    chat = chat.join(txt, on="message_id", how="left")
    # human kickoff messages (goal_fields rule, on every goal's first active day)
    cal = pl.read_parquet(OUT / "calendar.parquet", columns=["pt_date", "win_start", "goal_no", "holdout"])
    hum = (pl.read_parquet(OUT / "chat_core.parquet", columns=["message_id", "t", "pt_date", "room", "speaker_kind", "length"])
           .filter(pl.col("speaker_kind").cast(pl.String) == "human"))
    firsts = cal.filter(pl.col("goal_no") > 0).sort("pt_date").group_by("goal_no", maintain_order=True).first()
    kick_ids = set()
    for d0 in firsts["pt_date"].to_list():
        k, _, _ = kickoff_messages(cal, hum, d0)
        kick_ids |= set(k["message_id"].to_list())
    n_t = pl.col("targets").list.len()
    chat = chat.with_columns(
        pl.when(pl.col("sk") == "agent").then(pl.lit("mention"))
        .when(pl.col("sk") == "human").then(pl.lit("human_message"))
        .when(pl.col("is_pause") | pl.col("is_resume")).then(pl.lit("pause_resume"))
        .when((n_t > 0) | pl.col("addressed")).then(pl.lit("nudge"))
        .otherwise(pl.lit("automated_other")).alias("kind"))
    chat = chat.with_columns(
        pl.when(pl.col("kind") == "pause_resume").then(pl.when(pl.col("is_pause")).then(pl.lit("pause")).otherwise(pl.lit("resume")))
        .when(pl.col("kind") == "human_message").then(
            pl.when(pl.col("message_id").is_in(list(kick_ids))).then(pl.lit("kickoff"))
            .when(n_t > 0).then(pl.lit("mention")).otherwise(pl.lit("plain")))
        .when((pl.col("kind") == "nudge") & (n_t == 0)).then(pl.lit("unparsed_target"))
        .otherwise(None).alias("subkind"),
        pl.when(pl.col("kind").is_in(["nudge", "mention"]) | ((pl.col("kind") == "human_message") & (n_t > 0)))
        .then(True).otherwise(False).alias("targeted"))
    # recipients (exposure: agents in the room, excluding the speaker)
    rec = (pl.read_parquet(OUT / "exposure.parquet", columns=["msg", "agent"]).join(chat.select("msg"), on="msg", how="semi")
           .group_by("msg").agg(pl.col("agent").sort().alias("recipients")))
    chat = chat.join(rec, on="msg", how="left").with_columns(
        pl.col("recipients").fill_null(pl.lit([], dtype=pl.List(pl.Int8))))
    msgs = chat.select(
        "t", "kind", "subkind", "targeted", "room", pl.when(pl.col("kind") == "mention").then(pl.col("agent")).alias("speaker"),
        "targets", n_t.cast(pl.Int8).alias("n_targets"), "recipients", pl.col("msg").cast(pl.UInt32), "message_id",
        "goal_no", "pt_date", pl.lit(None, dtype=pl.Int8).alias("ref"))
    goals = pl.DataFrame([{"t": g["start"], "goal_no": g["goal_no"]} for g in load_goals()]).with_columns(
        pl.col("t").dt.cast_time_unit("us"))
    goals = goals.with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("pt_date"))
    gk = goals.select("t", pl.lit("goal_kickoff").alias("kind"), pl.lit(None, dtype=pl.String).alias("subkind"),
                      pl.lit(False).alias("targeted"), pl.lit(None, dtype=pl.Int8).alias("room"),
                      pl.lit(None, dtype=pl.Int8).alias("speaker"), pl.lit(None, dtype=pl.List(pl.Int8)).alias("targets"),
                      pl.lit(None, dtype=pl.Int8).alias("n_targets"), pl.lit(None, dtype=pl.List(pl.Int8)).alias("recipients"),
                      pl.lit(None, dtype=pl.UInt32).alias("msg"), pl.lit(None, dtype=pl.String).alias("message_id"),
                      pl.col("goal_no").cast(pl.Int8), "pt_date", pl.col("goal_no").cast(pl.Int8).alias("ref"))
    df = pl.concat([msgs, gk], how="vertical_relaxed")
    df = (df.join(cal.select("pt_date", "holdout"), on="pt_date", how="left")
          .with_columns(pl.col("holdout").fill_null(False), pl.col("kind").cast(pl.Categorical), pl.col("subkind").cast(pl.Categorical),
                        pl.col("speaker").cast(pl.Int8), pl.col("room").cast(pl.Int8))
          .sort("t", "kind"))
    return df


def main():
    t0 = time.time()
    df = build()
    df.write_parquet(OUT / "kicks_classified.parquet", compression="zstd")
    print(df.group_by("kind", "subkind").agg(pl.len(), pl.col("holdout").sum().alias("holdout"),
                                             pl.col("n_targets").mean().alias("mean_targets")).sort("kind", "subkind"))
    write_provenance("kicks_classified", ["chat_core", "chat_mentions_clean", "chat_text (automated rows: regex flags only)",
                                          "exposure", "calendar", "village_goals"],
                     {"pause_rx": PAUSE_RX, "resume_rx": RESUME_RX, "nudge": "automated & (mentions_roster or starts with '@')",
                      "mentions": "chat_mentions_clean.mentions_roster", "kickoff": "goal_fields.kickoff_messages",
                      "sources": "H04 h04lib.load_messages; H16 h16lib.load_kicks"})
    print(f"done {time.time() - t0:.0f}s")


# ----------------------------------------------------------------------------- verification (read-only imports)
def _load(name, path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod  # dataclasses need the module registered
    spec.loader.exec_module(mod)
    return mod


def verify():
    df = pl.read_parquet(OUT / "kicks_classified.parquet").with_columns(pl.col("kind").cast(pl.String))
    cal = pl.read_parquet(OUT / "calendar.parquet", columns=["pt_date", "holdout"])
    days = cal.filter(~pl.col("holdout"))["pt_date"].to_list()
    d = df.filter(pl.col("pt_date").is_in(days) & (pl.col("kind") != "goal_kickoff"))
    res = {}
    # H04: kinds human / nudge / bookend per message
    h04 = _load("h04lib_ro", ROOT / "hypotheses/H04-reversible-forcing/analysis/h04lib.py")
    m = h04.load_messages(days)
    h = dict(m.group_by("kind").len().iter_rows())
    mine = {"human": d.filter(pl.col("kind") == "human_message").height, "nudge": d.filter(pl.col("kind") == "nudge").height,
            "bookend": d.filter(pl.col("kind").is_in(["pause_resume", "automated_other"])).height}
    j = m.select("msg", pl.col("kind").alias("h04"), "valid_mentions").join(
        d.select(pl.col("msg").cast(pl.UInt32), "kind", "targets"), on="msg", how="full", coalesce=True)
    xt = j.group_by("h04", "kind").len().sort("h04", "kind")
    tgt_same = j.filter((pl.col("h04") == "nudge") & (pl.col("kind") == "nudge")).with_columns(
        (pl.col("valid_mentions").list.sort() == pl.col("targets").list.sort()).alias("same"))
    res["H04"] = {"h04_counts": h, "shared_counts": mine, "crosstab": xt.rows(),
                  "nudges_with_identical_targets": f"{int(tgt_same['same'].sum())}/{tgt_same.height}"}
    # H16: (message, recipient) classes
    h16 = _load("h16lib_ro", ROOT / "hypotheses/H16-metastable-traps-kramers/analysis/h16lib.py")
    K = h16.load_kicks(days)
    hc = {}
    for a, cls in K.items():
        for c, arr in cls.items():
            hc[c] = hc.get(c, 0) + len(arr)
    e = d.filter(pl.col("kind").is_in(["mention", "human_message", "nudge"])).explode("recipients").drop_nulls("recipients")
    e = e.with_columns(pl.col("targets").list.contains(pl.col("recipients")).alias("dir"))
    mc = {"A_men": e.filter((pl.col("kind") == "mention") & pl.col("dir")).height,
          "H_men": e.filter((pl.col("kind") == "human_message") & pl.col("dir")).height,
          "H_und": e.filter((pl.col("kind") == "human_message") & ~pl.col("dir")).height,
          "N_tgt": e.filter((pl.col("kind") == "nudge") & pl.col("dir")).height,
          "N_by": e.filter((pl.col("kind") == "nudge") & ~pl.col("dir") & (pl.col("n_targets") > 0)).height}
    res["H16"] = {"h16_counts": {k: hc.get(k, 0) for k in sorted(hc)}, "shared_counts": mc,
                  "note": "A_und is not reproduced: agent messages without a mention are not kicks here"}
    for k, v in res.items():
        print(k, v)
    return res


if __name__ == "__main__":
    if "--verify" in sys.argv:
        verify()
    else:
        main()
