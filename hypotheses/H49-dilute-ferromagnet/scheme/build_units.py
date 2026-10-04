"""H49 scheme: dense per-unit matrices for the conditioned inverse-Ising pipeline.

Inputs (read-only, data/processed/shared/): activity_bins_fixed (DQ8 join fix; the original activity_bins drops about
half of all events), outages_fixed/reasons and outages_fixed/stall_minutes (H38's rule rebuilt from the fixed bins),
period_units, calendar. `--buggy` rebuilds from the original activity_bins / reasons / stall_minutes (for the
old-vs-new comparison only).
Eligible replication units: non-holdout period_units with >= 2 days, regime III or I, >= 6 present agents
(H02 rule: an activity_bins row on every day of the unit and >= 30 active minutes).
Native windows (fixed populations): NE43 W1/W2/W3 (#51), G44 merged (4 days, leader excluded), NE14 II / III sides.

Output: data/processed/H49-dilute-ferromagnet/units.parquet and mats/<unit>.npz with
  S (T, N) int8 activity spin (state >= 3), Tk (T, N) int8 talk spin (state == 4), R (T, N) int8 reason code
  (0 none, 1 pre, 2 post, 3 infra_err, 4 consol, 5 pause; only on silent minutes), day (T,) int16, minute (T,) int32,
  sched (T,) bool (off-schedule minute), agents (N,) int16, days (D,) str.

Usage: uv run python hypotheses/H49-dilute-ferromagnet/scheme/build_units.py
"""
from __future__ import annotations

import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
import os  # noqa: E402

os.environ.setdefault("POLARS_MAX_THREADS", "2")
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from common import holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H49-dilute-ferromagnet"
MIN_DAYS, MIN_N, MIN_ACTIVE = 2, 6, 30

NATIVE = {
    # NE43 inside #51: bookends on / bookend messages off / nudges off too (dates from kicks_classified, see card)
    "NE43_W1": {"days": ("2026-07-27", "2026-08-04"), "group": "NE43"},
    "NE43_W2": {"days": ("2026-08-05", "2026-08-20"), "group": "NE43"},
    "NE43_W3": {"days": ("2026-08-21", "2026-09-04"), "group": "NE43"},
    "G44_all": {"goal": 44, "group": "G44", "exclude_agents": [28]},
    "NE14_II": {"units": ["35", "36a"], "group": "NE14"},
    "NE14_III": {"units": ["36b", "36c", "37"], "group": "NE14"},
}


def git_commit() -> str:
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    d = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"], capture_output=True, text=True).stdout
    return (r.stdout.strip() or "none") + ("+uncommitted" if d.strip() else "")


def assert_nonholdout(days, cal):
    gm = dict(zip(cal["pt_date"].to_list(), cal["goal_no"].to_list()))
    hm = dict(zip(cal["pt_date"].to_list(), cal["holdout"].to_list()))
    assert not any(hm[d] for d in days), "holdout day (calendar)"
    assert not any(holdout_mask(days, [gm[d] for d in days])), "holdout day (holdout_mask)"


def present(ab: pl.DataFrame, days: list[str]) -> list[int]:
    p = (ab.filter(pl.col("pt_date").is_in(days)).group_by("agent")
         .agg(pl.col("pt_date").n_unique().alias("nd"), (pl.col("state") >= 3).sum().alias("na"))
         .filter((pl.col("nd") == len(days)) & (pl.col("na") >= MIN_ACTIVE)).sort("agent"))
    return p["agent"].to_list()


def matrices(ab, rs, sm, days, agents):
    d = ab.filter(pl.col("pt_date").is_in(days) & pl.col("agent").is_in(agents))
    dmap = {x: i for i, x in enumerate(days)}
    d = d.join(rs, on=["pt_date", "minute", "agent"], how="left").with_columns(pl.col("reason").fill_null(0))
    d = d.with_columns(pl.col("pt_date").replace_strict(dmap, return_dtype=pl.Int16).alias("day"))
    cols = [str(a) for a in agents]
    st = d.pivot(on="agent", index=["day", "minute"], values="state").sort("day", "minute")
    rr = d.pivot(on="agent", index=["day", "minute"], values="reason").sort("day", "minute")
    state = np.nan_to_num(st.select(cols).to_numpy().astype(float), nan=1).astype(np.int8)
    reas = np.nan_to_num(rr.select(cols).to_numpy().astype(float), nan=0).astype(np.int8)
    day = st["day"].to_numpy().astype(np.int16)
    minute = st["minute"].to_numpy().astype(np.int32)
    S = np.where(state >= 3, 1, -1).astype(np.int8)
    Tk = np.where(state == 4, 1, -1).astype(np.int8)
    R = np.where(S > 0, 0, reas).astype(np.int8)
    key = pl.DataFrame({"day": day, "minute": minute})
    sch = (sm.filter(pl.col("pt_date").is_in(days))
           .with_columns(pl.col("pt_date").replace_strict(dmap, return_dtype=pl.Int16).alias("day"))
           .select("day", "minute", "scheduled"))
    sched = key.join(sch, on=["day", "minute"], how="left")["scheduled"].fill_null(False).to_numpy()
    return S, Tk, R, day, minute, sched


def main():
    buggy = "--buggy" in sys.argv
    (OUT / "mats").mkdir(parents=True, exist_ok=True)
    cal = pl.read_parquet(SH / "calendar.parquet")
    pu = pl.read_parquet(SH / "period_units.parquet")
    bins = SH / ("activity_bins.parquet" if buggy else "activity_bins_fixed.parquet")
    odir = SH if buggy else SH / "outages_fixed"
    ab = pl.read_parquet(bins, columns=["pt_date", "minute", "agent", "state"]).with_columns(pl.col("minute").cast(pl.Int32))
    rs = pl.read_parquet(odir / "reasons.parquet")
    sm = pl.read_parquet(odir / "stall_minutes.parquet", columns=["pt_date", "minute", "scheduled"])
    nh_days = set(cal.filter(~pl.col("holdout"))["pt_date"].to_list())
    rows = []

    def save(uid, days, agents, meta):
        assert_nonholdout(days, cal)
        S, Tk, R, day, minute, sched = matrices(ab, rs, sm, days, agents)
        np.savez_compressed(OUT / "mats" / f"{uid}.npz", S=S, Tk=Tk, R=R, day=day, minute=minute, sched=sched,
                            agents=np.array(agents, np.int16), days=np.array(days))
        rows.append({"unit": uid, **meta, "n_days": len(days), "first_day": days[0], "last_day": days[-1],
                     "N": len(agents), "T": int(S.shape[0]), "sched_min": int(sched.sum()),
                     "agents": ",".join(map(str, agents))})

    for r in pu.filter(~pl.col("holdout") & pl.col("regime").is_in(["I", "III"])).sort("start").iter_rows(named=True):
        days = [d for d in r["days"] if d in nh_days]
        if len(days) < MIN_DAYS:
            continue
        agents = present(ab, days)
        if len(agents) < MIN_N:
            continue
        save(r["unit_id"], days, agents, {"kind": "replication", "goal_no": r["goal_no"], "regime": r["regime"],
                                          "group": f"G{r['goal_no']:02d}"})
    units = {r["unit_id"]: r for r in pu.iter_rows(named=True)}
    for uid, spec in NATIVE.items():
        if "days" in spec:
            a, b = spec["days"]
            days = sorted(d for d in nh_days if a <= d <= b)
        elif "goal" in spec:
            days = sorted(d for d in nh_days if cal.filter(pl.col("pt_date") == d)["goal_no"][0] == spec["goal"])
        else:
            days = sorted({d for u in spec["units"] for d in units[u]["days"]} & nh_days)
        rows_n = {"kind": "native", "goal_no": int(cal.filter(pl.col("pt_date") == days[0])["goal_no"][0]),
                  "regime": str(cal.filter(pl.col("pt_date") == days[-1])["regime"][0]), "group": spec["group"]}
        if spec["group"] in ("NE43", "NE14"):
            continue  # fixed populations set below
        agents = [a for a in present(ab, days) if a not in spec.get("exclude_agents", [])]
        save(uid, days, agents, rows_n)
    # fixed populations across the windows of one natural experiment
    for grp in ("NE43", "NE14"):
        specs = {u: s for u, s in NATIVE.items() if s["group"] == grp}
        wdays = {}
        for uid, spec in specs.items():
            if "days" in spec:
                a, b = spec["days"]
                wdays[uid] = sorted(d for d in nh_days if a <= d <= b)
            else:
                wdays[uid] = sorted({d for u in spec["units"] for d in units[u]["days"]} & nh_days)
        common = None
        for uid, days in wdays.items():
            p = set(present(ab, days))
            common = p if common is None else common & p
        common = sorted(common)
        for uid, days in wdays.items():
            save(uid, days, common, {"kind": "native", "goal_no": int(cal.filter(pl.col("pt_date") == days[0])["goal_no"][0]),
                                     "regime": str(cal.filter(pl.col("pt_date") == days[-1])["regime"][0]), "group": grp})
    df = pl.DataFrame(rows)
    df.write_parquet(OUT / "units.parquet")
    prov = {"built_by": "hypotheses/H49-dilute-ferromagnet/scheme/build_units.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village (shared derived tables)", "revision": "838b4150303ca8228e8edb432d8b8ccae353d258 (see data/processed/shared/_provenance.json)",
                        "tables": ([str(bins.relative_to(ROOT)), str((odir / "reasons.parquet").relative_to(ROOT)),
                                    str((odir / "stall_minutes.parquet").relative_to(ROOT)), "period_units", "calendar"])}],
            "params": {"MIN_DAYS": MIN_DAYS, "MIN_N": MIN_N, "MIN_ACTIVE": MIN_ACTIVE, "native": NATIVE, "buggy_bins": buggy},
            "built_at": dt.datetime.now(dt.UTC).isoformat()}
    p = OUT / "_provenance.json"
    old = json.loads(p.read_text()) if p.exists() else {}
    old["units"] = prov
    p.write_text(json.dumps(old, indent=1, default=str))
    with pl.Config(tbl_rows=100, tbl_width_chars=200):
        print(df.select("unit", "kind", "group", "regime", "n_days", "N", "T", "sched_min"))


if __name__ == "__main__":
    main()
