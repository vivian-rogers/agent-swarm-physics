"""Shared analysis units: every goal period split at every step change inside it (the project rule: the goal period is
the unit of analysis, split at step changes). Replaces the per-hypothesis splits of H01/H12/H13 (GOAL_SPLITS), H22
(UNITS), H03 and H18 (step_changes + segment_days / segments_of), H16 (date_to windows) and H17 (NE_SPLITS).

One rule. A unit is a maximal run of a goal period's active PT days (calendar) containing no step change. A change
dated D (strictly after the period's first active day) starts a new unit on the first active day >= D. Changes:
  ne           every dated row of hypotheses/natural-experiments.md (scaffold NE01-NE26, roster NE27-NE33, operator
               NE35-NE38, appended NE41/NE42; ranges and lists give every listed date, e.g. NE14 2026-03-11 -> 03-24,
               NE21 06-07 / 06-15 / 06-29, NE33 09-03/04). Undated rows (NE34 goal changes, NE39, NE40) are skipped:
               goal changes are period boundaries already.
  roster_join / roster_leave   roster.parquet joined / left dates (CHANGELOG roster), Claude Code agent excluded.
  rooms        the structural room set changes: rooms that are the modal room (by agent events) of >= 2 agents on a
               day, compared with the previous active day (e.g. #best/#rest 03-16, merge 05-04 and split 05-11, #focus
               08-05 and its end 08-24; one-agent onboarding rooms and stray visits do not count).
  hours        the documented daily hours change (calendar.documented_hours; 2025-07-18, 2025-08-18, NE21's dates).
  holdout      the locked-holdout status changes between consecutive active days (e.g. #51 at the 09-07 tail), so no
               unit mixes held-out and exploratory days.
  outage       a village-off gap inside a day: >= OUTAGE_MIN minutes with no agent event or computer-use turn, with
               >= SIDE_MIN minutes and >= SIDE_N records on both sides (a restart, not a stray record). The unit then
               ends at the last record before the gap and the next starts at the restart, so that day is listed in
               both units. Stray fragments (1-10 records hours before or after the session, 6 days) do not split; they
               are counted in `n_offgaps` (calendar windows on those days are stretched by them; see infra/README).
               When the shared `outages` table (H38) lands, this rule can switch to it.

Output: data/processed/shared/period_units.parquet, one row per unit:
  unit_id (goal number, plus a, b, c ... when the period has > 1 unit), goal_no, seq, start, end (UTC: first day's
  window start or the restart time; last day's window end or the last record before an outage), first_day, last_day,
  n_days, days (list of PT dates), reason (what started the unit: "goal_start" or the boundary's changes, '; '-joined),
  reasons (list), n_agents (roster agents with >= 1 record in [start, end]), n_roster (roster size on the first day,
  Claude Code excluded), rooms (structural room codes, union over days), regime, holdout (every day held out), n_offgaps
Also: data/processed/shared/period_step_changes.parquet (date, kind, source, what): every change the rule used.

Usage: uv run python infra/shared/period_units.py              (build)
       uv run python infra/shared/period_units.py --compare    (disagreements with H01/H12/H13, H22, H03/H18, H16, H17)
Library: unit_of_day(pt_date) -> list of unit_ids; units() -> DataFrame.
"""
from __future__ import annotations

import os

for _v, _n in (("POLARS_MAX_THREADS", "2"), ("OMP_NUM_THREADS", "2"), ("OPENBLAS_NUM_THREADS", "2"),
               ("MKL_NUM_THREADS", "2"), ("VECLIB_MAXIMUM_THREADS", "2")):
    os.environ.setdefault(_v, _n)

import json  # noqa: E402
import re  # noqa: E402
import string  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT, ROOT, write_provenance  # noqa: E402

OUTAGE_MIN = 60
SIDE_MIN = 30
SIDE_N = 100
ROOM_MIN_AGENTS = 2
NE_FILE = ROOT / "hypotheses/natural-experiments.md"


# ----------------------------------------------------------------------------- step changes
def ne_changes() -> list[dict]:
    """Dated NE rows (same date parsing as H03/H18's step_changes)."""
    out, section = [], ""
    for line in NE_FILE.read_text().splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
        m = re.match(r"^\| (NE\d+) \| ([^|]+) \| ([^|]+) \|", line)
        if not m:
            continue
        ne, dfield, change = m.group(1), m.group(2), m.group(3).strip()
        full = re.findall(r"(\d{4})-(\d{2})-(\d{2})", dfield)
        if not full:
            continue
        y = full[0][0]
        dates = {f"{a}-{b}-{c}" for a, b, c in full}
        rest = re.sub(r"\d{4}-\d{2}-\d{2}", "", dfield)
        for mm, dd in re.findall(r"(\d{2})-(\d{2})", rest):      # "-> 03-24", "/ 06-15"
            dates.add(f"{y}-{mm}-{dd}")
        for dd in re.findall(r"/(\d{2})(?!-)", rest):              # "2025-11-20/25"
            dates.add(f"{y}-{full[0][1]}-{dd}")
        for d in sorted(dates):
            out.append({"date": d, "kind": "ne", "source": ne, "what": f"{section}: {re.sub(r'[*`]', '', change)[:70]}"})
    return out


def roster_changes() -> list[dict]:
    ros = pl.read_parquet(OUT / "roster.parquet").filter(~pl.col("claude_code"))
    out = []
    for r in ros.iter_rows(named=True):
        out.append({"date": r["joined"], "kind": "roster_join", "source": r["name"], "what": f"joins (agent {r['agent']})"})
        if r["left"]:
            out.append({"date": r["left"], "kind": "roster_leave", "source": r["name"], "what": f"leaves (agent {r['agent']})"})
    return out


def room_sets() -> pl.DataFrame:
    """Per active day: structural rooms = modal room (by agent events) of >= ROOM_MIN_AGENTS agents."""
    ev = (pl.read_parquet(OUT / "events_core.parquet", columns=["pt_date", "actor_kind", "agent", "room"])
          .filter((pl.col("actor_kind") == "agent") & pl.col("room").is_not_null() & pl.col("agent").is_not_null()))
    m = (ev.group_by("pt_date", "agent", "room").len().sort(["len", "room"], descending=[True, False])
         .group_by("pt_date", "agent", maintain_order=True).agg(pl.col("room").first()))
    return (m.group_by("pt_date", "room").len().filter(pl.col("len") >= ROOM_MIN_AGENTS)
            .group_by("pt_date").agg(pl.col("room").sort().alias("rooms")).sort("pt_date"))


def room_changes(cal: pl.DataFrame, rs: pl.DataFrame) -> list[dict]:
    names = dict(pl.read_parquet(OUT / "rooms.parquet").select("room", "name").iter_rows())
    x = cal.select("pt_date").join(rs, on="pt_date", how="left").sort("pt_date")
    out, prev = [], None
    for d, rooms in x.iter_rows():
        cur = tuple(rooms) if rooms is not None else None
        if cur is None:
            continue
        if prev is not None and cur != prev:
            fmt = lambda s: "{" + ", ".join("#" + names.get(r, str(r)) for r in s) + "}"  # noqa: E731
            out.append({"date": d, "kind": "rooms", "source": fmt(cur), "what": f"structural rooms {fmt(prev)} -> {fmt(cur)}"})
        prev = cur
    return out


def hours_changes(cal: pl.DataFrame) -> list[dict]:
    x = cal.select("pt_date", "documented_hours").sort("pt_date")
    out, prev = [], None
    for d, h in x.iter_rows():
        if h is None:
            continue
        if prev is not None and h != prev:
            out.append({"date": d, "kind": "hours", "source": f"{prev}h->{h}h", "what": "documented daily hours change"})
        prev = h
    return out


def records() -> pl.DataFrame:
    """Every agent record time (agent events + computer-use turns), with PT date."""
    ev = (pl.read_parquet(OUT / "events_core.parquet", columns=["t", "pt_date", "actor_kind", "agent"])
          .filter((pl.col("actor_kind") == "agent") & pl.col("agent").is_not_null()).select("t", "agent", "pt_date"))
    ac = (pl.read_parquet(OUT / "actions.parquet", columns=["t", "agent"]).filter(pl.col("agent").is_not_null())
          .with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("pt_date")))
    return pl.concat([ev, ac.select("t", "agent", "pt_date")]).sort("t")


def offgaps(rec: pl.DataFrame) -> pl.DataFrame:
    """Interior all-agent-silent gaps >= OUTAGE_MIN per day, with activity on each side; split = a real restart."""
    r = rec.select("t", "pt_date").sort("t").with_columns(
        (pl.col("t") - pl.col("t").shift(1).over("pt_date")).dt.total_seconds().alias("gap_s"),
        pl.col("t").shift(1).over("pt_date").alias("t_before"))
    gaps = r.filter(pl.col("gap_s") >= OUTAGE_MIN * 60).select("pt_date", "t_before", pl.col("t").alias("t_restart"), "gap_s")
    out = []
    for d, tb, tr, gs in gaps.iter_rows():
        day = r.filter(pl.col("pt_date") == d)
        pre, post = day.filter(pl.col("t") <= tb), day.filter(pl.col("t") >= tr)
        pre_min = (pre["t"].max() - pre["t"].min()).total_seconds() / 60
        post_min = (post["t"].max() - post["t"].min()).total_seconds() / 60
        split = pre_min >= SIDE_MIN and post_min >= SIDE_MIN and pre.height >= SIDE_N and post.height >= SIDE_N
        out.append({"pt_date": d, "t_before": tb, "t_restart": tr, "gap_min": gs / 60, "pre_min": pre_min, "pre_n": pre.height,
                    "post_min": post_min, "post_n": post.height, "split": split})
    return pl.DataFrame(out, schema={"pt_date": pl.String, "t_before": pl.Datetime("us", "UTC"), "t_restart": pl.Datetime("us", "UTC"),
                                     "gap_min": pl.Float64, "pre_min": pl.Float64, "pre_n": pl.Int64, "post_min": pl.Float64,
                                     "post_n": pl.Int64, "split": pl.Boolean})


def step_changes(cal: pl.DataFrame, rs: pl.DataFrame) -> pl.DataFrame:
    rows = ne_changes() + roster_changes() + room_changes(cal, rs) + hours_changes(cal)
    return pl.DataFrame(rows).unique().sort("date", "kind", "source")


# ----------------------------------------------------------------------------- units
def _suffix(k: int) -> str:
    a = string.ascii_lowercase
    return a[k] if k < 26 else a[k // 26 - 1] + a[k % 26]


def build():
    cal = (pl.read_parquet(OUT / "calendar.parquet").filter(pl.col("goal_no") >= 1)
           .with_columns(pl.col("regime").cast(pl.String)).sort("pt_date"))
    rs = room_sets()
    sc = step_changes(cal, rs)
    rec = records()
    og = offgaps(rec)
    roster = pl.read_parquet(OUT / "roster.parquet").filter(~pl.col("claude_code"))
    ros_agents = set(roster["agent"].to_list())
    rooms_by_day = {d: r for d, r in rs.iter_rows()}
    by_date: dict = {}
    for r in sc.iter_rows(named=True):
        by_date.setdefault(r["date"], []).append(r)
    cdates = sorted(by_date)
    splits = {r["pt_date"]: r for r in og.filter(pl.col("split")).iter_rows(named=True)}
    n_off = og.filter(~pl.col("split")).group_by("pt_date").len()
    n_off = dict(n_off.iter_rows())

    units = []
    for (g,), sub in cal.group_by(["goal_no"], maintain_order=True):
        sub = sub.sort("pt_date")
        days = sub.to_dicts()
        segs = []  # each: dict(days=[...], start, end, reasons)
        cur = None
        for i, d in enumerate(days):
            reasons = []
            if i > 0:
                prev = days[i - 1]
                for c in cdates:
                    if prev["pt_date"] < c <= d["pt_date"]:
                        reasons += [f"{x['kind']}:{x['source']}" for x in by_date[c]]
                if bool(prev["holdout"]) != bool(d["holdout"]):
                    reasons.append(f"holdout:{'enter' if d['holdout'] else 'exit'}")
            if cur is None or reasons:
                if cur is not None:
                    segs.append(cur)
                cur = {"days": [], "start": d["win_start"], "end": d["win_end"], "reasons": reasons or ["goal_start"]}
            cur["days"].append(d["pt_date"])
            cur["end"] = d["win_end"]
            if d["pt_date"] in splits:  # restart inside the day: close the unit at the gap, open a new one
                s = splits[d["pt_date"]]
                cur["end"] = s["t_before"]
                segs.append(cur)
                cur = {"days": [d["pt_date"]], "start": s["t_restart"], "end": d["win_end"],
                       "reasons": [f"outage:{s['gap_min']:.0f}min"]}
        segs.append(cur)
        for k, s in enumerate(segs):
            uid = str(int(g)) if len(segs) == 1 else f"{int(g)}{_suffix(k)}"
            dset = set(s["days"])
            ho = [bool(x["holdout"]) for x in days if x["pt_date"] in dset]
            regs = sorted({x["regime"] for x in days if x["pt_date"] in dset})
            rooms = sorted({r for dd in s["days"] for r in (rooms_by_day.get(dd) or [])})
            n_roster = roster.filter((pl.col("joined") <= s["days"][0]) & (pl.col("left").is_null() | (pl.col("left") > s["days"][0]))).height
            units.append({"unit_id": uid, "goal_no": int(g), "seq": k, "start": s["start"], "end": s["end"],
                          "first_day": s["days"][0], "last_day": s["days"][-1], "n_days": len(s["days"]), "days": s["days"],
                          "reason": "; ".join(s["reasons"]), "reasons": s["reasons"], "n_roster": n_roster, "rooms": rooms,
                          "regime": "/".join(regs), "holdout": all(ho), "holdout_any": any(ho),
                          "n_offgaps": int(sum(n_off.get(dd, 0) for dd in s["days"]))})
    U = pl.DataFrame(units, schema_overrides={"rooms": pl.List(pl.Int8), "goal_no": pl.Int8, "seq": pl.Int16,
                                              "n_days": pl.Int16, "n_roster": pl.Int16, "n_offgaps": pl.Int16})
    assert (U["holdout"] == U["holdout_any"]).all(), "a unit mixes holdout and non-holdout days"
    U = U.drop("holdout_any")
    # active agents per unit (roster agents with >= 1 record in [start, end])
    rr = rec.filter(pl.col("agent").is_in(list(ros_agents)))
    n_act = []
    for s, e in U.select("start", "end").iter_rows():
        n_act.append(rr.filter((pl.col("t") >= s) & (pl.col("t") <= e))["agent"].n_unique())
    U = U.with_columns(pl.Series("n_agents", n_act, dtype=pl.Int16))
    cols = ["unit_id", "goal_no", "seq", "start", "end", "first_day", "last_day", "n_days", "days", "reason", "reasons",
            "n_agents", "n_roster", "rooms", "regime", "holdout", "n_offgaps"]
    return U.select(cols), sc, og


def main():
    t0 = time.time()
    U, sc, og = build()
    U.write_parquet(OUT / "period_units.parquet", compression="zstd")
    sc.write_parquet(OUT / "period_step_changes.parquet", compression="zstd")
    per_goal = U.group_by("goal_no").len()
    print(f"{U.height} units over {per_goal.height} goal periods; {per_goal.filter(pl.col('len') > 1).height} periods split; "
          f"{U.filter(pl.col('n_days') == 1).height} one-day units; holdout units {U['holdout'].sum()}")
    print("intra-day village-off gaps:", og.select("pt_date", "gap_min", "pre_min", "pre_n", "post_min", "post_n", "split").rows())
    write_provenance("period_units", ["calendar", "roster", "rooms", "events_core", "actions", "hypotheses/natural-experiments.md"],
                     {"changes": ["ne (all dated rows)", "roster_join/leave (non-Claude-Code)", f"rooms (modal room of >= {ROOM_MIN_AGENTS} agents)",
                                  "hours (documented)", "holdout boundary", f"outage (>= {OUTAGE_MIN} min, both sides >= {SIDE_MIN} min and >= {SIDE_N} records)"],
                      "rule": "a change dated D starts a unit on the first active day >= D (strictly after the period's first day)",
                      "n_units": U.height})
    print(f"done {time.time() - t0:.0f}s")


# ----------------------------------------------------------------------------- library
def units() -> pl.DataFrame:
    return pl.read_parquet(OUT / "period_units.parquet")


def unit_of_day(pt_date: str) -> list[str]:
    u = units().explode("days").filter(pl.col("days") == pt_date)
    return u["unit_id"].to_list()


# ----------------------------------------------------------------------------- comparison with existing splits
def _boundaries_from_units(U: pl.DataFrame) -> dict:
    """goal -> set of day-level boundary dates (first day of each unit after the first; outage splits excluded)."""
    out = {}
    for g, sub in U.sort("goal_no", "seq").group_by("goal_no", maintain_order=True):
        b = set()
        for r in sub.iter_rows(named=True):
            if r["seq"] > 0 and not r["reason"].startswith("outage"):
                b.add(r["first_day"])
        out[int(g[0])] = b
    return out


def compare():
    U = units()
    cal = pl.read_parquet(OUT / "calendar.parquet", columns=["pt_date", "goal_no", "holdout"])
    nh_days = {g: sorted(d) for g, d in cal.filter(~pl.col("holdout")).group_by("goal_no").agg(pl.col("pt_date")).iter_rows()}
    shared = _boundaries_from_units(U)
    reason_of = {(r["goal_no"], r["first_day"]): r["reason"] for r in U.iter_rows(named=True)}

    def first_active_on_or_after(g, d):
        ds = [x for x in nh_days.get(g, []) if x >= d]
        return ds[0] if ds else None

    theirs = {}
    # H01 / H12 / H13 (same GOAL_SPLITS; H13's and H22's unit dicts list the same days)
    h01 = {36: ["2026-03-24"], 38: ["2026-04-14", "2026-04-20"], 51: ["2026-07-09", "2026-08-05", "2026-08-25", "2026-09-03"]}
    theirs["H01/H12/H13 GOAL_SPLITS"] = {g: {first_active_on_or_after(g, d) for d in v} for g, v in h01.items()}
    # H22 UNITS (first days of the non-first units)
    h22 = {51: ["2026-07-09", "2026-08-05", "2026-08-25", "2026-09-03"], 38: ["2026-04-14", "2026-04-20"]}
    theirs["H22 UNITS"] = {g: set(v) for g, v in h22.items()}
    # H17 NE_SPLITS (run_period.py)
    theirs["H17 NE_SPLITS"] = {21: {first_active_on_or_after(21, "2025-12-04")}, 30: {first_active_on_or_after(30, "2026-02-10")},
                               38: {first_active_on_or_after(38, "2026-04-14")}}
    # H03 (segment_days.parquet; H18 uses the same rule: segments_of(step_changes()))
    p = ROOT / "data/processed/H03-self-excited-criticality/segment_days.parquet"
    if p.exists():
        sd = pl.read_parquet(p).sort("goal_no", "pt_date")
        b = {}
        for (g,), sub in sd.group_by(["goal_no"], maintain_order=True):
            segs = sub["seg"].to_list(); ds = sub["pt_date"].to_list()
            b[int(g)] = {ds[i] for i in range(1, len(ds)) if segs[i] != segs[i - 1]}
        theirs["H03/H18 step_changes"] = b
    # H16 windows (period cut at date_to: the excluded part starts a new unit)
    theirs["H16 date_to"] = {31: {first_active_on_or_after(31, "2026-02-20")}, 51: {first_active_on_or_after(51, "2026-09-03")}}

    report = {}
    for name, B in theirs.items():
        rows = []
        goals = sorted(B) if not name.startswith("H03") else sorted(set(B) | {g for g in shared if g in nh_days})
        for g in goals:
            if g not in nh_days:
                continue
            nh = set(nh_days[g])
            sh = {d for d in shared.get(g, set()) if d in nh}
            th = {d for d in B.get(g, set()) if d}
            if sh != th:
                rows.append({"goal": g, "only_shared": sorted((d, reason_of.get((g, d), "")) for d in sh - th),
                             "only_theirs": sorted(th - sh)})
        report[name] = rows
    for name, rows in report.items():
        print(f"\n== {name}: {len(rows)} goal periods disagree")
        for r in rows:
            print(f"  #{r['goal']}: only shared {r['only_shared']}; only theirs {r['only_theirs']}")
    return report


if __name__ == "__main__":
    if "--compare" in sys.argv:
        compare()
    else:
        main()
