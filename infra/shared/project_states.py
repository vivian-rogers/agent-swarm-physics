"""Shared artifact-based project states: the modal project each agent touches per window of a day's active window.
Moved here from H11 (hypotheses/H11-potts-labor-vs-herding/scheme/build.py: project_map, assign_windows, modal,
window_table, attach_rooms, build_project, label_projects), which H06, H27, H28 and H31 import.

Rule (H11, unchanged):
  mentions  artifact_mentions by agents (speaker_kind == agent), strict only (how in {url, output, bare}: directory-
            based resolution is 0.81-0.89 precise), artifacts of kind repo / site / file;
  project   files and sites map to their parent repo when known (coalesce(parent name, name)); Netlify
            "deploy-preview-N--" prefixes stripped; Google "/e" published-placeholder ids dropped;
  dedupe    one count per (agent, source, ref, project), ref = chat message_id or the action/intention ref_index;
  window    W-minute bins from the day's calendar win_start (mentions outside [win_start, win_end] dropped);
  state     the modal project per (goal, day, window, agent); ties -> the most recent mention; exact ties -> the
            project first seen earliest in the dataset, then the name (deterministic; H11's choice varied by run);
  room      the agent's room at the window midpoint (rooms_timeline), 0 (#general) when unknown;
  label     per goal period: projects ranked by labeled agent-windows; the top <= Q_MAX (8) with share >= 2% get
            labels 1..q, the rest 0 ("other"). The ranking uses the period's NON-HOLDOUT rows when it has any
            (so held-out windows never shape exploratory labels), else all rows (fully held-out periods).
Variants: w_min in {15, 30 (primary), 60}; sources "all" (chat + actions + intentions) or "action" (computer-use
actions only; H11's post-hoc robustness variant).
All goal periods (1..51), including the holdout: `holdout` flags held-out days (measurements; exploration must filter).

Output: data/processed/shared/project_states.parquet
  w_min, sources, goal_no, pt_date, day (0-based dense day index within the period), win, agent, room, project
  (canonical artifact name of the repo/site/file; no agent text), n (mentions of the modal project), n_all (all
  strict mentions in the window), n_tied (projects tied for the mode on count and last-mention time; > 1 in ~1% of
  windows, resolved by project name), label (0..q), holdout
Helpers: window_table(cal, W) gives every window of every active day (for circular shifts); projects_table(df)
gives H11's per-period label -> project table.

Usage: uv run python infra/shared/project_states.py            (build)
       uv run python infra/shared/project_states.py --verify   (compare with H11's per-period labels; read-only)
"""
from __future__ import annotations

import os

for _v, _n in (("POLARS_MAX_THREADS", "2"), ("OMP_NUM_THREADS", "2"), ("OPENBLAS_NUM_THREADS", "2"),
               ("MKL_NUM_THREADS", "2"), ("VECLIB_MAXIMUM_THREADS", "2")):
    os.environ.setdefault(_v, _n)

import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT, ROOT, holdout_mask, write_provenance  # noqa: E402

SHARED = OUT
WINDOWS_MIN = (15, 30, 60)
W_PRIMARY = 30
Q_MAX = 8
MIN_SHARE = 0.02
STRICT_HOW = ("url", "output", "bare")
DEPLOY_PREVIEW = r"^deploy-preview-\d+--"


def load_calendar(goals=None, allow_holdout=True):
    """Active days of the given goal periods (default: all goal periods >= 1) with a dense per-period day index."""
    cal = pl.read_parquet(SHARED / "calendar.parquet")
    cal = cal.filter(pl.col("goal_no") >= 1) if goals is None else cal.filter(pl.col("goal_no").is_in(goals))
    cal = cal.filter(pl.col("n_agent_events") > 0)
    mask = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    cal = cal.with_columns(pl.Series("ho", mask))
    if not allow_holdout:
        cal = cal.filter(~pl.col("ho"))
    cal = cal.sort("pt_date").with_columns(pl.col("pt_date").rank("dense").over("goal_no").cast(pl.Int16).sub(1).alias("day"))
    return cal.select("pt_date", "goal_no", "day", "regime", "win_start", "win_end", "window_s", "ho")


def project_map():
    art = pl.read_parquet(SHARED / "artifacts.parquet").select("artifact", "kind", "name", "parent")
    par = art.select(pl.col("artifact").alias("parent"), pl.col("name").alias("parent_name"))
    art = art.join(par, on="parent", how="left")
    art = art.filter(pl.col("kind").cast(pl.String).is_in(["repo", "site", "file"]))
    art = art.with_columns(pl.coalesce("parent_name", "name").alias("project"))
    art = art.with_columns(pl.col("project").str.replace(DEPLOY_PREVIEW, ""))
    art = art.filter(~pl.col("project").str.contains(r"/e$"))  # Google 'published' placeholder ids
    return art.select("artifact", "project")


def project_first_seen() -> pl.DataFrame:
    """project -> first_seen: the earliest first_t over the artifacts mapped to the project (exact-tie breaker)."""
    pm = project_map()
    ft = pl.read_parquet(SHARED / "artifacts.parquet").select("artifact", "first_t")
    return pm.join(ft, on="artifact").group_by("project").agg(pl.col("first_t").min().alias("first_seen"))


def assign_windows(df, cal, W):
    df = df.with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("pt_date"))
    df = df.join(cal.select("pt_date", "goal_no", "day", "win_start", "win_end"), on="pt_date", how="inner")
    df = df.filter((pl.col("t") >= pl.col("win_start")) & (pl.col("t") <= pl.col("win_end")))
    return df.with_columns(((pl.col("t") - pl.col("win_start")).dt.total_seconds() // (W * 60)).cast(pl.Int16).alias("win"))


def modal(df, key, first_seen: pl.DataFrame | None = None):
    """Modal value of `key` per (goal, day, win, agent); ties -> the most recent mention (H11). Exact ties (same count
    and same last-mention time, e.g. one message naming two projects; ~1-3% of windows) -> the project seen earliest in
    the dataset (`first_seen`: key -> first_seen), then the smallest `key`. H11's version stopped at the time tie-break
    and grouped without maintain_order, so its choice in exact ties varied from run to run."""
    g = df.group_by("goal_no", "pt_date", "day", "win", "agent", key).agg(pl.len().alias("n"), pl.col("t").max().alias("tl"))
    if first_seen is not None:
        g = g.join(first_seen, on=key, how="left")
    else:
        g = g.with_columns(pl.lit(None, dtype=pl.Datetime("us", "UTC")).alias("first_seen"))
    g = g.sort(["n", "tl", "first_seen", key], descending=[True, True, False, False], nulls_last=True).group_by(
        "goal_no", "pt_date", "day", "win", "agent", maintain_order=True).agg(
        pl.col(key).first(), pl.col("n").first(), pl.col("n").sum().alias("n_all"),
        ((pl.col("n") == pl.col("n").first()) & (pl.col("tl") == pl.col("tl").first())).sum().cast(pl.Int8).alias("n_tied"))
    return g


def window_table(cal, W):
    rows = []
    for r in cal.iter_rows(named=True):
        nk = int(-(-r["window_s"] // (W * 60))) if r["window_s"] else 0
        for k in range(max(nk, 1)):
            rows.append({"goal_no": r["goal_no"], "pt_date": r["pt_date"], "day": r["day"], "win": k})
    w = pl.DataFrame(rows, schema={"goal_no": pl.Int8, "pt_date": pl.String, "day": pl.Int16, "win": pl.Int16})
    w = w.join(cal.select("pt_date", "win_start"), on="pt_date").with_columns(
        (pl.col("win_start") + pl.duration(seconds=(pl.col("win").cast(pl.Int64) * W * 60 + W * 30))).alias("t_mid")).drop("win_start")
    return w.with_columns(pl.col("win").cast(pl.Int16))


def attach_rooms(lab, wins):
    rt = pl.read_parquet(SHARED / "rooms_timeline.parquet")
    keys = lab.select("goal_no", "pt_date", "day", "win", "agent").unique().join(wins, on=["goal_no", "pt_date", "day", "win"])
    j = keys.join(rt, on="agent", how="left").filter(
        (pl.col("t_start") <= pl.col("t_mid")) & (pl.col("t_end").is_null() | (pl.col("t_mid") < pl.col("t_end"))))
    j = j.sort("t_start", descending=True).group_by("goal_no", "pt_date", "day", "win", "agent").agg(pl.col("room").first())
    lab = lab.join(j, on=["goal_no", "pt_date", "day", "win", "agent"], how="left")
    return lab.with_columns(pl.col("room").fill_null(0).cast(pl.Int8))


def build_project(cal, W, wins, sources=None):
    pm = project_map()
    am = pl.scan_parquet(SHARED / "artifact_mentions.parquet").filter(
        (pl.col("speaker_kind").cast(pl.String) == "agent") & pl.col("how").cast(pl.String).is_in(list(STRICT_HOW))
        & pl.col("agent").is_not_null()).select("artifact", "t", "agent", "source", "message_id", "ref_index").collect()
    am = am.join(pm, on="artifact", how="inner")
    if sources is not None:
        am = am.filter(pl.col("source").cast(pl.String).is_in(list(sources)))
    am = am.with_columns(pl.coalesce(pl.col("message_id"), pl.col("ref_index").cast(pl.String)).alias("ref"))
    am = am.unique(subset=["agent", "source", "ref", "project"])
    am = assign_windows(am, cal, W)
    lab = modal(am, "project", project_first_seen())
    return attach_rooms(lab, wins)


def label_projects(lab, ref_mask: pl.Expr | None = None):
    """Per goal: rank projects by labeled agent-windows; keep <= Q_MAX with share >= MIN_SHARE (H11).
    ref_mask (optional, boolean expression on lab): rows that define the ranking; when a goal has no such rows, all
    of its rows are used. Returns (labeled rows, per-goal project table)."""
    out, proj = [], []
    for (g,), d in lab.group_by(["goal_no"], maintain_order=True):
        ref = d
        if ref_mask is not None:
            r = d.filter(ref_mask)
            ref = r if r.height else d
        tot = ref.height
        c = ref.group_by("project").agg(pl.len().alias("aw"), pl.col("agent").n_unique().alias("n_agents")).sort(
            ["aw", "project"], descending=[True, False])
        c = c.with_columns((pl.col("aw") / tot).alias("share"))
        keep = c.filter(pl.col("share") >= MIN_SHARE).head(Q_MAX)
        mp = {p: i + 1 for i, p in enumerate(keep["project"].to_list())}
        out.append(d.with_columns(pl.col("project").replace_strict(mp, default=0).cast(pl.Int8).alias("label")))
        proj.append(c.with_columns(pl.lit(g).cast(pl.Int8).alias("goal_no"),
                                   pl.col("project").replace_strict(mp, default=0).cast(pl.Int8).alias("label")))
    return pl.concat(out), pl.concat(proj)


def projects_table(df: pl.DataFrame) -> pl.DataFrame:
    """H11's projects_w{W} table (label -> project, agent-windows, distinct agents, share) from project_states rows
    of one (w_min, sources) variant, computed on the rows given (filter holdout first for exploration)."""
    out = []
    for (g,), d in df.group_by(["goal_no"], maintain_order=True):
        c = d.group_by("project").agg(pl.len().alias("aw"), pl.col("agent").n_unique().alias("n_agents"),
                                      pl.col("label").first()).sort(["aw", "project"], descending=[True, False])
        out.append(c.with_columns((pl.col("aw") / d.height).alias("share"), pl.lit(g).cast(pl.Int8).alias("goal_no")))
    return pl.concat(out)


def main():
    t0 = time.time()
    cal = load_calendar()
    parts = []
    for W in WINDOWS_MIN:
        wins = window_table(cal, W)
        for src_name, src in (("all", None), ("action", ("action",))):
            lab = build_project(cal, W, wins, sources=src)
            lab = lab.join(cal.select("pt_date", pl.col("ho").alias("holdout")), on="pt_date", how="left")
            lp, _ = label_projects(lab, ref_mask=~pl.col("holdout"))
            parts.append(lp.with_columns(pl.lit(W, dtype=pl.Int16).alias("w_min"), pl.lit(src_name).alias("sources")))
            print(f"W={W} sources={src_name}: {lp.height} agent-windows, {time.time() - t0:.0f}s", flush=True)
    df = (pl.concat(parts, how="vertical_relaxed")
          .select("w_min", pl.col("sources").cast(pl.Categorical), "goal_no", "pt_date", "day", "win", "agent", "room",
                  pl.col("project").cast(pl.Categorical), pl.col("n").cast(pl.Int32), pl.col("n_all").cast(pl.Int32), "n_tied", "label",
                  "holdout")
          .sort("w_min", "sources", "goal_no", "day", "win", "agent"))
    df.write_parquet(SHARED / "project_states.parquet", compression="zstd")
    print(df.group_by("w_min", "sources").agg(pl.len(), pl.col("holdout").sum()).sort("w_min", "sources"))
    write_provenance("project_states", ["artifacts", "artifact_mentions", "calendar", "rooms_timeline"],
                     {"windows_min": list(WINDOWS_MIN), "primary": W_PRIMARY, "q_max": Q_MAX, "min_share": MIN_SHARE,
                      "strict_how": list(STRICT_HOW), "sources_variants": {"all": "chat+action+intention", "action": "action only"},
                      "label_ranking": "per goal on non-holdout rows when any, else all rows",
                      "holdout": "all goal periods included; holdout flagged",
                      "source": "hypotheses/H11-potts-labor-vs-herding/scheme/build.py (logic unchanged)"})
    print(f"done {time.time() - t0:.0f}s")


def verify():
    """Compare with H11's per-period label files. H11's exact-tie choice was nondeterministic (see modal), so the
    project is compared in untied windows (must be identical) and tied windows are counted separately; labels can
    then permute between projects whose agent-window counts differ by a few windows."""
    h11 = ROOT / "data/processed/H11-potts-labor-vs-herding"
    df = pl.read_parquet(SHARED / "project_states.parquet").with_columns(pl.col("project").cast(pl.String),
                                                                         pl.col("sources").cast(pl.String))
    keys = ["goal_no", "pt_date", "day", "win", "agent"]
    res = {}
    for W in WINDOWS_MIN:
        for fname, src in (("labels_project", "all"), ("labels_projectact", "action")):
            files = sorted(h11.glob(f"G*/{fname}_w{W}.parquet"))
            if not files:
                continue
            a = pl.concat([pl.read_parquet(f) for f in files]).with_columns(pl.col("n").cast(pl.Int32), pl.col("n_all").cast(pl.Int32))
            b = df.filter((pl.col("w_min") == W) & (pl.col("sources") == src) & pl.col("goal_no").is_in(a["goal_no"].unique().implode()))
            j = a.join(b, on=keys, how="full", suffix="_s", coalesce=True)
            tied = j["n_tied"].fill_null(0) > 1
            pdiff = j["project"] != j["project_s"]
            same_rows = int(j.filter(pl.col("project").is_not_null() & pl.col("project_s").is_not_null()).height)
            res[f"w{W}_{src}"] = {
                "periods": len(files), "h11_rows": a.height, "shared_rows": b.height, "rows_matched_on_keys": same_rows,
                "room_n_nall_differ": int(((j["room"] != j["room_s"]) | (j["n"] != j["n_s"]) | (j["n_all"] != j["n_all_s"])).sum()),
                "project_differs_untied": int((pdiff & ~tied).sum()),
                "tied_windows": int(tied.sum()), "project_differs_tied": int((pdiff & tied).sum()),
                "label_differs": int((j["label"] != j["label_s"]).sum()),
                "label_differs_periods": int(j.filter(pl.col("label") != pl.col("label_s"))["goal_no"].n_unique())}
    for k, v in res.items():
        print(k, v)
    return res


if __name__ == "__main__":
    if "--verify" in sys.argv:
        verify()
    else:
        main()
