"""H90 scheme: per-period, per-day DQ8-trimmed grids for three channels, plus who-names-whom weights and rooms.

  uv run python hypotheses/H90-collective-entropy-production/scheme/build.py      (writes data/processed/H90-.../<G..>/)

Library use (analysis/run.py): load_period(goal, channel) -> (days, agents); weights(goal, agents); rooms(goal, ...).
Channels:
  behavior  H76's coarse 5-state soft vectors on 5-min v3 windows (absent = no labelled record); trim = windows where
            every day-present agent (any in_span window) is in_span (H76 trim_mask; DQ8 all-present rule).
            Copied from H76 `h76lib.load_v3` / `trim_mask` (2026-10-04) with attribution, not imported.
  talk      1-min spin 1[talk > 0] from activity_bins_fixed; activity: 1[state >= 3] (act or talk).
            Day-present = any record (state >= 2); span = [first, last] record minute; trim = nulls.all_present_window.
Holdout: every table passes holdout_mask and ~holdout; held-out days never enter.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "analysis"))
import h90lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402
from nulls import all_present_window  # noqa: E402

V3 = ["execute_task", "research_browse", "monitor_wait", "verify_report", "self_maintenance", "debug_recover",
      "communicate_external", "idle", "plan_coordinate", "social", "meta"]
COARSE_GROUPS = {"absent": [], "work": ["execute_task", "debug_recover", "verify_report"],
                 "explore": ["research_browse"],
                 "coord": ["plan_coordinate", "communicate_external", "social", "meta"],
                 "wait": ["monitor_wait", "idle", "self_maintenance"]}
GOALS = [37, 38, 39, 40, 41, 42, 44, 51]


def _nonholdout(df: pl.DataFrame, goal_col: str = "goal_no", allow_holdout: bool = False) -> pl.DataFrame:
    if allow_holdout:          # confirm.py only
        return df
    hm = holdout_mask(df["pt_date"].to_list(), df[goal_col].to_list())
    out = df.filter(~pl.Series(hm))
    return out.filter(~pl.col("holdout")) if "holdout" in out.columns else out


def calendar() -> pl.DataFrame:
    c = pl.read_parquet(L.SH / "calendar.parquet")
    return _nonholdout(c)


# ------------------------------------------------------------------------------------------------ behavior
def behavior_days(goal: int, allow_holdout: bool = False) -> tuple[list, list]:
    cols = ["pt_date", "agent", "w", "goal_no", "holdout", "active", "in_span", "labeled"] + [f"p_{s}" for s in V3]
    b = pl.read_parquet(L.SH / "behavior_states_v3.parquet", columns=cols).filter(pl.col("goal_no") == goal)
    b = _nonholdout(b, allow_holdout=allow_holdout)
    P = b.select([f"p_{s}" for s in V3]).fill_null(0.0).to_numpy().astype(np.float64)
    tot = P.sum(1, keepdims=True)
    lab = (b["active"] & b["labeled"]).to_numpy() & (tot[:, 0] > 0)
    P = np.where(tot > 0, P / np.where(tot > 0, tot, 1), 0.0)
    idx = {s: i for i, s in enumerate(V3)}
    X = np.zeros((P.shape[0], 5), np.float32)
    X[:, 0] = ~lab
    for k, g in enumerate(list(COARSE_GROUPS)[1:], start=1):
        X[lab, k] = P[lab][:, [idx[s] for s in COARSE_GROUPS[g]]].sum(1)
    agents = sorted(b["agent"].unique().to_list())
    gi = {a: k for k, a in enumerate(agents)}
    b = b.with_row_index("_r")
    days = []
    for (d,), sub in b.group_by(["pt_date"], maintain_order=True):
        ags = sorted(sub["agent"].unique().to_list())
        nw = int(sub["w"].max()) + 1
        arr = np.zeros((len(ags), nw, 5), np.float32)
        arr[:, :, 0] = 1.0
        span = np.zeros((len(ags), nw), bool)
        ai = {a: k for k, a in enumerate(ags)}
        r = sub["_r"].to_numpy()
        ia = np.array([ai[a] for a in sub["agent"].to_list()])
        w = sub["w"].to_numpy()
        arr[ia, w] = X[r]
        span[ia, w] = sub["in_span"].to_numpy()
        keep = span.any(1)
        if keep.sum() < 2:
            continue
        arr, span = arr[keep], span[keep]
        ags = [a for a, k in zip(ags, keep) if k]
        m = span.all(0)
        if m.sum() < 3:
            continue
        lo, hi = np.nonzero(m)[0][[0, -1]]
        seg = arr[:, lo:hi + 1]
        if not m[lo:hi + 1].all():               # keep the longest all-present run if the window has holes
            run = _longest_run(m)
            seg = arr[:, run[0]:run[1]]
        days.append({"date": d, "agents": np.array([gi[a] for a in ags]), "X": seg})
    return sorted(days, key=lambda x: x["date"]), agents


def _longest_run(m: np.ndarray) -> tuple[int, int]:
    best, cur, st = (0, 0), 0, 0
    for i, v in enumerate(np.r_[m, False]):
        if v:
            if cur == 0:
                st = i
            cur += 1
        else:
            if cur > best[1] - best[0]:
                best = (st, st + cur)
            cur = 0
    return best


# ------------------------------------------------------------------------------------------------ talk, activity
_AB = {}


def bins(allow_holdout: bool = False) -> pl.DataFrame:
    if allow_holdout not in _AB:
        ab = pl.read_parquet(L.SH / "activity_bins_fixed.parquet", columns=["pt_date", "minute", "agent", "talk", "state"])
        cal = pl.read_parquet(L.SH / "calendar.parquet", columns=["pt_date", "goal_no", "holdout"])
        ab = ab.join(cal, on="pt_date", how="inner")
        _AB[allow_holdout] = _nonholdout(ab, allow_holdout=allow_holdout)
    return _AB[allow_holdout]


def spin_days(goal: int, channel: str, allow_holdout: bool = False) -> tuple[list, list]:
    ab = bins(allow_holdout).filter(pl.col("goal_no") == goal)
    agents = sorted(ab.filter(pl.col("state") >= 2)["agent"].unique().to_list())
    gi = {a: k for k, a in enumerate(agents)}
    days = []
    for (d,), sub in ab.group_by(["pt_date"], maintain_order=True):
        rec = sub.filter(pl.col("state") >= 2)
        ags = sorted(rec["agent"].unique().to_list())
        if len(ags) < 2:
            continue
        T = int(sub["minute"].max()) + 1
        pres = np.zeros((T, len(ags)), bool)
        S = np.zeros((len(ags), T), np.uint8)
        ai = {a: k for k, a in enumerate(ags)}
        r = rec.select("agent", "minute").to_numpy()
        pres[r[:, 1], [ai[a] for a in r[:, 0]]] = True
        # span: [first, last] record per agent
        span = np.zeros_like(pres)
        for k in range(len(ags)):
            nz = np.nonzero(pres[:, k])[0]
            span[nz[0]:nz[-1] + 1, k] = True
        m = all_present_window(span)
        if m.sum() < 5:
            continue
        val = (sub["talk"] > 0) if channel == "talk" else (sub["state"] >= 3)
        s = sub.with_columns(val.alias("v")).filter(pl.col("agent").is_in(ags)).select("agent", "minute", "v").to_numpy()
        S[[ai[a] for a in s[:, 0]], s[:, 1].astype(int)] = s[:, 2].astype(np.uint8)
        lo, hi = _longest_run(m)
        days.append({"date": d, "agents": np.array([gi[a] for a in ags]), "X": S[:, lo:hi]})
    return sorted(days, key=lambda x: x["date"]), agents


# ------------------------------------------------------------------------------------------------ naming, rooms
def weights(goal: int, agents: list, allow_holdout: bool = False, days: list | None = None) -> np.ndarray:
    """w[j, i] = messages by agent j that name agent i (mentions_roster), non-holdout days of the goal."""
    cc = pl.read_parquet(L.SH / "chat_core.parquet", columns=["message_id", "pt_date", "goal_no", "speaker_kind", "agent"])
    cc = cc.with_columns(pl.lit(False).alias("holdout"))
    cc = _nonholdout(cc.filter((pl.col("goal_no") == goal) & (pl.col("speaker_kind") == "agent") & pl.col("agent").is_not_null()),
                     allow_holdout=allow_holdout)
    if days is not None:
        cc = cc.filter(pl.col("pt_date").is_in(days))
    mc = pl.read_parquet(L.SH / "chat_mentions_clean.parquet", columns=["message_id", "mentions_roster"])
    j = cc.join(mc, on="message_id", how="inner").explode("mentions_roster").drop_nulls("mentions_roster")
    j = j.filter(pl.col("agent") != pl.col("mentions_roster"))
    gi = {a: k for k, a in enumerate(agents)}
    w = np.zeros((len(agents), len(agents)))
    for r in j.group_by(["agent", "mentions_roster"]).len().iter_rows():
        if r[0] in gi and r[1] in gi:
            w[gi[r[0]], gi[r[1]]] = r[2]
    return w


def rooms_by_day(goal: int, agents: list, days: list) -> dict:
    """Room of each agent at the midpoint of each day's calendar window (rooms_timeline; open rooms' null t_end -> +inf)."""
    rt = pl.read_parquet(L.SH / "rooms_timeline.parquet").with_columns(
        pl.col("t_end").fill_null(dt.datetime(2100, 1, 1, tzinfo=dt.timezone.utc)))
    cal = pl.read_parquet(L.SH / "calendar.parquet", columns=["pt_date", "win_start", "win_end"])
    mid = {r[0]: r[1] + (r[2] - r[1]) / 2 for r in cal.iter_rows()}
    out = {}
    for d in days:
        t = mid[d["date"]]
        r = rt.filter((pl.col("t_start") <= t) & (pl.col("t_end") > t))
        rm = dict(zip(r["agent"].to_list(), r["room"].to_list()))
        out[d["date"]] = np.array([rm.get(a, -1) if rm.get(a) is not None else -1 for a in agents])
    return out


# ------------------------------------------------------------------------------------------------ io
def save_period(goal: int, channel: str, days: list, agents: list):
    d = L.OUTD / f"G{goal:02d}"
    d.mkdir(parents=True, exist_ok=True)
    arrs = {"agents": np.array(agents), "dates": np.array([x["date"] for x in days])}
    for k, x in enumerate(days):
        arrs[f"a{k}"] = x["agents"]
        arrs[f"x{k}"] = x["X"].astype(np.float16) if channel == "behavior" else x["X"].astype(np.uint8)
    np.savez_compressed(d / f"grid_{channel}.npz", **arrs)


def load_period(goal: int, channel: str) -> tuple[list, list]:
    f = L.OUTD / f"G{goal:02d}" / f"grid_{channel}.npz"
    z = np.load(f, allow_pickle=False)
    dates = z["dates"].tolist()
    days = [{"date": dd, "agents": z[f"a{k}"], "X": z[f"x{k}"].astype(np.float32)} for k, dd in enumerate(dates)]
    return days, z["agents"].tolist()


def provenance(params: dict):
    L.OUTD.mkdir(parents=True, exist_ok=True)
    (L.OUTD / "_provenance.json").write_text(json.dumps({
        "built_by": "hypotheses/H90-collective-entropy-production/scheme/build.py (+ analysis/run.py, analysis/synthetic.py)",
        "git_commit": git_commit(),
        "inputs": [{"source": "ai-village", "revision": REVISION,
                    "tables": ["behavior_states_v3 (DQ3)", "activity_bins_fixed", "chat_core", "chat_mentions_clean",
                               "rooms_timeline", "calendar", "period_units"]}],
        "params": params, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}, indent=1))


def main():
    for g in GOALS:
        for ch in ("behavior", "talk", "activity"):
            days, agents = behavior_days(g) if ch == "behavior" else spin_days(g, ch)
            save_period(g, ch, days, agents)
            w = weights(g, agents)
            pl.DataFrame({"j": np.repeat(agents, len(agents)), "i": np.tile(agents, len(agents)),
                          "w_ji": w.ravel()}).filter(pl.col("w_ji") > 0).write_parquet(
                L.OUTD / f"G{g:02d}" / f"weights_{ch}.parquet")
            print(g, ch, "days", len(days), "agents", len(agents), "steps", sum(x["X"].shape[1] for x in days), flush=True)
    provenance({"goals": GOALS, "behavior": "coarse5 soft, 5-min v3, H76 trim", "talk": "1-min talk>0, all-present trim",
                "activity": "1-min state>=3, all-present trim", "naming": "chat_mentions_clean.mentions_roster, agent speakers"})


if __name__ == "__main__":
    main()
