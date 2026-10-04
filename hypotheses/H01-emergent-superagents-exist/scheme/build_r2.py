"""H01 round 2 scheme: work-ledger panels for candidate superagents (card: "Round 2 formal setup", F1-F6, F9).

Builds data/processed/H01-emergent-superagents-exist/round2/ from the shared tables (non-holdout days only; the
holdout guard of h01common is asserted on every table):
  units.json            eligible units of analysis (round-1 unit splits; >= 2 days, >= 100 strict writes, >= 4 writers)
  writes.parquet        write events: one row per (agent, command turn, project); verb class; confirmed flag
                        (git printed a push range / new commit hash); strict (url/output/bare) vs lenient (+cwd)
  attention.parquet     strict project mentions by agents (any verb, any source), deduplicated per turn/message
  bins.parquet          30-min active bins per day (window from calendar), with y^h (human/automated message or
                        goal kickoff in the bin) and platform-stall flags (shared outages table)
  presence.parquet      agent-day presence (any agent event or computer-use turn) and modal room of the day
  rooms_period.parquet  time-weighted modal room per agent and unit
  mentions.parquet      agent -> agent addressing counts per unit (chat_mentions_clean, roster-restricted)
  scrambles.parquet     natural-scramble catalog used by R6-R8: H15's ML/MG/MN memory events and NE41 forced (CF) /
                        voluntary (CV) consolidations (agent, time), restricted to eligible units
Writes are taken from executed commands only (source = action); narration in chat is never counted (card rule).
Run: uv run python hypotheses/H01-emergent-superagents-exist/scheme/build_r2.py
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ[_v] = "2"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h01common import OUT as OUT1, SH, guard_holdout, nonholdout_days, unit_of, write_provenance  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

OUT = OUT1 / "round2"
H15 = OUT1.parent / "H15-semantic-information-scrambles"
BIN_MIN = 30
WRITE_VERBS = ["git push", "git commit", "deploy", "gh pr create", "gh pr merge", "gh repo create",
               "glab mr create", "glab mr merge", "glab repo create", "glab project create"]
VERB_CLASS = {"git push": "push", "git commit": "commit", "deploy": "deploy"}
STRICT = ["url", "output", "bare"]
LENIENT = STRICT + ["cwd", "session_cwd"]
CLAUDE_CODE = 19
TZ = "America/Los_Angeles"


def pt_date(col="t"):
    return pl.col(col).dt.convert_time_zone(TZ).dt.date().cast(pl.Utf8)


def project_map():
    """H11's project map: repo; file/site -> parent repo when known, else itself; domains and Google placeholders out."""
    art = pl.read_parquet(SH / "artifacts.parquet").select("artifact", "kind", "name", "parent")
    art = art.with_columns(pl.when(pl.col("kind") == "repo").then(pl.col("artifact"))
                           .when(pl.col("kind").is_in(["file", "site"]) & pl.col("parent").is_not_null()).then(pl.col("parent"))
                           .when(pl.col("kind").is_in(["file", "site"])).then(pl.col("artifact"))
                           .otherwise(None).alias("project"))
    return art.filter(pl.col("project").is_not_null() & ~pl.col("name").str.contains("docs.google.com/e/"))


def load_mentions(day_unit: dict, art: pl.DataFrame) -> pl.DataFrame:
    m = pl.read_parquet(SH / "artifact_mentions.parquet")
    m = m.filter((pl.col("speaker_kind") == "agent") & (pl.col("agent") != CLAUDE_CODE))
    m = m.join(art.select("artifact", "project"), on="artifact", how="inner")
    m = m.with_columns(pt_date().alias("pt_date")).filter(pl.col("pt_date").is_in(list(day_unit)))
    return m.with_columns(pl.col("pt_date").replace_strict(day_unit, default=None).alias("unit"))


def load_writes(m: pl.DataFrame) -> pl.DataFrame:
    """Write events from executed commands only: one row per (agent, turn, project); strict flag; confirmed flag."""
    w = m.filter((pl.col("source") == "action") & pl.col("verb").cast(pl.Utf8).is_in(WRITE_VERBS)
                 & pl.col("how").cast(pl.Utf8).is_in(LENIENT))
    w = w.with_columns(pl.col("how").cast(pl.Utf8).is_in(STRICT).alias("strict"),
                       pl.col("verb").cast(pl.Utf8).replace_strict(VERB_CLASS, default="pr_repo").alias("vclass"))
    w = (w.group_by("agent", "ref_index", "project").agg(pl.col("t").min(), pl.col("pt_date").first(), pl.col("unit").first(),
                                                          pl.col("strict").any(), pl.col("vclass").first()))
    cmd = pl.read_parquet(SH / "artifact_commands_text.parquet", columns=["row", "out_hashes"])
    cmd = cmd.with_columns((pl.col("out_hashes").list.len() > 0).alias("confirmed")).select("row", "confirmed")
    return w.join(cmd, left_on="ref_index", right_on="row", how="left").with_columns(pl.col("confirmed").fill_null(False))


def main():
    days = nonholdout_days()
    guard_holdout(days)
    build(OUT, days, allow_holdout=False)


def build(OUT: Path, days: list, allow_holdout: bool = False, unit_fn=None, h15_dir: Path = H15):
    """Build the round-2 panels for the given days into OUT. Exploration: non-holdout days, guard asserted.
    The confirmatory script (analysis/confirm_r2.py) calls this with holdout days and allow_holdout=True only after
    its refusal check; unit_fn maps (goal_no, pt_date) -> unit label (default: round-1 splits)."""
    t0 = time.time()
    unit_fn = unit_fn or unit_of
    OUT.mkdir(parents=True, exist_ok=True)
    guard_holdout(days, allow=allow_holdout)
    cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("pt_date").is_in(days) & (pl.col("goal_no") >= 30))
    cal = cal.with_columns(pl.struct("goal_no", "pt_date").map_elements(lambda r: unit_fn(r["goal_no"], r["pt_date"]),
                                                                        return_dtype=pl.Utf8).alias("unit"))
    day_unit = dict(zip(cal["pt_date"].to_list(), cal["unit"].to_list()))
    roster = pl.read_parquet(SH / "roster.parquet")

    # ------------------------------------------------------------------ projects, mentions, write events
    art = project_map()
    pname = dict(zip(art["artifact"].to_list(), art["name"].to_list()))
    m = load_mentions(day_unit, art)
    w = load_writes(m)
    guard_holdout(sorted(w["pt_date"].unique().to_list()), allow=allow_holdout)

    # ------------------------------------------------------------------ attention (strict mentions, any verb/source)
    at = m.filter(pl.col("how").cast(pl.Utf8).is_in(STRICT))
    at = at.with_columns(pl.coalesce(pl.col("message_id"), pl.col("ref_index").cast(pl.Utf8)).alias("ref"))
    at = at.group_by("agent", "source", "ref", "project").agg(pl.col("t").min(), pl.col("pt_date").first(), pl.col("unit").first())
    at = at.select("agent", "project", "t", "pt_date", "unit", "source")

    # ------------------------------------------------------------------ eligibility
    act = pl.concat([
        pl.read_parquet(SH / "events_core.parquet", columns=["t", "actor_kind", "agent"]).filter(pl.col("actor_kind") == "agent")
        .select("t", "agent"),
        pl.read_parquet(SH / "actions.parquet", columns=["t", "agent"])])
    act = act.with_columns(pt_date().alias("pt_date")).filter(pl.col("pt_date").is_in(list(day_unit)) & (pl.col("agent") != CLAUDE_CODE))
    pres = act.group_by("agent", "pt_date").agg(pl.len().alias("n_actions"))
    ws = w.filter(pl.col("strict"))
    elig = []
    for u, g in cal.group_by("unit"):
        u = u[0]
        wu = ws.filter(pl.col("unit") == u)
        n_days = g.height
        n_w = wu.height
        n_a = wu["agent"].n_unique()
        info = {"unit": u, "goal_no": int(g["goal_no"][0]), "regime": str(g["regime"][0]), "days": sorted(g["pt_date"].to_list()),
                "n_days": n_days, "n_writes_strict": n_w, "n_writers": n_a, "n_projects": wu["project"].n_unique(),
                "eligible": bool(n_days >= 2 and n_w >= 100 and n_a >= 4)}
        elig.append(info)
    elig = sorted(elig, key=lambda r: (r["goal_no"], r["unit"]))
    (OUT / "units.json").write_text(json.dumps(elig, indent=1))
    units_ok = {r["unit"] for r in elig if r["eligible"]}
    print("eligible units", sorted(units_ok, key=lambda s: (int("".join(c for c in s if c.isdigit())), s)), flush=True)

    # ------------------------------------------------------------------ bins, y^h, stalls
    cc = pl.read_parquet(SH / "chat_core.parquet", columns=["t", "pt_date", "speaker_kind", "room"])
    hum = cc.filter(pl.col("speaker_kind").is_in(["human", "automated"]) & pl.col("pt_date").is_in(list(day_unit)))
    kk = pl.read_parquet(SH / "kicks.parquet").filter(pl.col("kind") == "goal_kickoff").with_columns(pt_date().alias("pt_date"))
    out_ = pl.read_parquet(SH / "outages.parquet").filter((allow_holdout | ~pl.col("holdout")) & pl.col("pt_date").is_in(list(day_unit))
                                                         & (pl.col("village_off") | pl.col("infra_burst")) & ~pl.col("at_day_edge"))
    rows = []
    for r in cal.filter(pl.col("unit").is_in(list(units_ok))).sort("pt_date").iter_rows(named=True):
        nb = int(np.ceil(r["window_s"] / (BIN_MIN * 60))) or 1
        ht = hum.filter(pl.col("pt_date") == r["pt_date"])["t"]
        kt = kk.filter(pl.col("pt_date") == r["pt_date"])["t"]
        def binof(ts):
            return ((ts - r["win_start"]).dt.total_seconds() // (BIN_MIN * 60)).cast(pl.Int32).to_numpy()
        yh = np.zeros(nb, bool)
        for arr in (binof(ht), binof(kt)):
            arr = arr[(arr >= 0) & (arr < nb)]
            yh[arr] = True
        st = out_.filter(pl.col("pt_date") == r["pt_date"])
        stall = np.zeros(nb, bool)
        for s0, s1 in zip(st["t_start"].to_list(), st["t_end"].to_list()):
            b0 = int((s0 - r["win_start"]).total_seconds() // (BIN_MIN * 60))
            b1 = int((s1 - r["win_start"]).total_seconds() // (BIN_MIN * 60))
            stall[max(b0, 0):min(b1, nb - 1) + 1] = True
        for b in range(nb):
            rows.append({"unit": r["unit"], "pt_date": r["pt_date"], "bin": b, "yh": bool(yh[b]), "stall": bool(stall[b]),
                         "win_start": r["win_start"], "win_end": r["win_end"]})
    bins = pl.DataFrame(rows)
    bins.write_parquet(OUT / "bins.parquet", compression="zstd")

    # ------------------------------------------------------------------ attach bin / minute offsets to events
    ws_ = cal.select("pt_date", "win_start", "win_end")

    def attach(df, all_units=False):
        df = (df if all_units else df.filter(pl.col("unit").is_in(list(units_ok)))).join(ws_, on="pt_date", how="inner")
        return (df.with_columns(((pl.col("t") - pl.col("win_start")).dt.total_seconds() / 60).alias("minute"))
                .with_columns((pl.col("minute") // BIN_MIN).cast(pl.Int16).alias("bin")).drop("win_start", "win_end"))

    # writes on every non-holdout day of goal >= 30 (the cross-boundary designs need the next goal's first days)
    w = attach(w, all_units=True).with_columns(pl.col("agent").cast(pl.Int8), pl.col("project").cast(pl.Int32),
                                               pl.col("minute").cast(pl.Float32), pl.col("unit").is_in(list(units_ok)).alias("eligible"))
    w.drop("ref_index").write_parquet(OUT / "writes.parquet", compression="zstd")
    at = attach(at).with_columns(pl.col("agent").cast(pl.Int8), pl.col("project").cast(pl.Int32), pl.col("minute").cast(pl.Float32))
    at.write_parquet(OUT / "attention.parquet", compression="zstd")
    pl.DataFrame({"project": list(pname.keys()), "name": list(pname.values())}).filter(
        pl.col("project").is_in(w["project"].unique().to_list() + at["project"].unique().to_list())).write_parquet(
        OUT / "projects.parquet", compression="zstd")

    # ------------------------------------------------------------------ presence, rooms
    rt = pl.read_parquet(SH / "rooms_timeline.parquet")
    pres = pres.with_columns(pl.col("pt_date").replace_strict(day_unit, default=None).alias("unit")).filter(pl.col("unit").is_in(list(units_ok)))
    rooms_day = []
    for r in cal.filter(pl.col("unit").is_in(list(units_ok))).iter_rows(named=True):
        lo, hi = r["win_start"], r["win_end"]
        x = rt.filter((pl.col("t_start") < hi) & (pl.col("t_end").is_null() | (pl.col("t_end") > lo)))
        x = x.with_columns(((pl.min_horizontal(pl.col("t_end").fill_null(hi), pl.lit(hi)) -
                             pl.max_horizontal(pl.col("t_start"), pl.lit(lo))).dt.total_seconds()).alias("ov"))
        x = x.filter(pl.col("ov") > 0).sort("ov", descending=True).group_by("agent").agg(pl.col("room").first(), pl.col("ov").first())
        for a, room, ov in x.iter_rows():
            rooms_day.append({"agent": a, "pt_date": r["pt_date"], "room": room, "ov_s": ov})
    rd = pl.DataFrame(rooms_day)
    pres = pres.join(rd.select("agent", "pt_date", "room"), on=["agent", "pt_date"], how="left")
    pres.write_parquet(OUT / "presence.parquet", compression="zstd")
    rp = (rd.with_columns(pl.col("pt_date").replace_strict(day_unit, default=None).alias("unit"))
          .group_by("unit", "agent", "room").agg(pl.col("ov_s").sum()).sort("ov_s", descending=True)
          .group_by("unit", "agent").agg(pl.col("room").first(), pl.col("ov_s").sum()))
    rp.write_parquet(OUT / "rooms_period.parquet", compression="zstd")

    # ------------------------------------------------------------------ addressing graph
    cm = pl.read_parquet(SH / "chat_mentions_clean.parquet", columns=["message_id", "mentions_roster"])
    ca = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "pt_date", "speaker_kind", "agent"]).filter(
        (pl.col("speaker_kind") == "agent") & pl.col("pt_date").is_in(list(day_unit)))
    ca = ca.join(cm, on="message_id").explode("mentions_roster").drop_nulls("mentions_roster")
    ca = ca.with_columns(pl.col("pt_date").replace_strict(day_unit, default=None).alias("unit")).filter(
        pl.col("unit").is_in(list(units_ok)) & (pl.col("agent") != pl.col("mentions_roster")))
    ca.group_by("unit", "agent", "mentions_roster").agg(pl.len().alias("n")).rename({"mentions_roster": "target"}).write_parquet(
        OUT / "mentions.parquet", compression="zstd")

    # ------------------------------------------------------------------ scramble catalog (H15 outputs, read-only)
    sc = pl.read_parquet(h15_dir / "scramble_catalog.parquet").filter(pl.col("type").is_in(["ML", "MG", "MN"]))
    sc = sc.select(pl.col("type").alias("kind"), "agent", "t", "pt_date", "dose").with_columns(
        pl.col("pt_date").replace_strict(day_unit, default=None).alias("unit"))
    co = pl.read_parquet(h15_dir / "consolidations.parquet", columns=["agent", "t", "pt_date", "kind"]).filter(pl.col("kind").is_in(["CF", "CV"]))
    co = co.with_columns(pl.col("pt_date").replace_strict(day_unit, default=None).alias("unit"), pl.lit(None, pl.Float64).alias("dose"))
    scr = pl.concat([sc.select("kind", "agent", "t", "pt_date", "dose", "unit"), co.select("kind", "agent", "t", "pt_date", "dose", "unit")])
    scr = scr.filter(pl.col("unit").is_in(list(units_ok)))
    scr = pl.concat([attach(scr.filter(pl.col("t").is_not_null())),
                     scr.filter(pl.col("t").is_null()).with_columns(pl.lit(None, pl.Float64).alias("minute"),
                                                                     pl.lit(None, pl.Int16).alias("bin"))], how="diagonal_relaxed")
    scr.write_parquet(OUT / "scrambles.parquet", compression="zstd")

    for f in ("writes", "attention", "bins", "presence", "scrambles"):
        d = pl.read_parquet(OUT / f"{f}.parquet")
        if "pt_date" in d.columns:
            guard_holdout(sorted(d["pt_date"].drop_nulls().unique().to_list()), allow=allow_holdout)
    import datetime as dt
    from h01common import REVISION, git_commit
    prov = {"built_by": "hypotheses/H01-emergent-superagents-exist/scheme/build_r2.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION, "tables": None}], "params": None,
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    _write_prov = lambda name, by, tables, params: (OUT / "_provenance.json").write_text(json.dumps(
        {**prov, "inputs": [{"source": "ai-village", "revision": REVISION, "tables": tables}], "params": params}, indent=1))
    _write_prov("round2", "hypotheses/H01-emergent-superagents-exist/scheme/build_r2.py",
                     ["artifacts", "artifact_mentions", "artifact_commands_text", "calendar", "events_core", "actions",
                      "chat_core", "chat_mentions_clean", "kicks", "rooms_timeline", "roster", "outages (shared, built by H38)",
                      "H15 scramble_catalog + consolidations (data/processed/H15-semantic-information-scrambles)"],
                     {"bin_min": BIN_MIN, "write_verbs": WRITE_VERBS, "strict_how": STRICT, "lenient_how": LENIENT,
                      "source": "action only for writes", "eligibility": ">=2 days, >=100 strict writes, >=4 writers",
                      "units": "round-1 splits (h01common.GOAL_SPLITS)", "stalls": "village_off or infra_burst, not at day edge"})
    print("writes", w.height, "strict", w.filter(pl.col("strict")).height, "attention", at.height, "bins", bins.height,
          f"{time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
