"""H50 scheme: per-unit arrays for the transfer-function / gate analysis, from shared tables only.

For each eligible non-holdout period unit (and the NE43 pseudo-units), writes
data/processed/H50-field-vs-coupling-transfer-lag/units/<unit>.npz with:
  calls  (non-summary model calls from call_windows): agent idx, day idx, tc (t_call), tl (t_log), talk, act,
         first (first_of_day), low (start_conf == low), turn_id
  msgs   (agent chat messages from chat_core): t, day, sender idx (-1 if not a calling agent), room
  mpairs (context_ledger_items, kind agent): msg idx, recipient idx, receiving turn_id, ment, uncertain
  inputs (kicks_classified bookends / human messages / nudges, + 'edge' = window start on days without a resume):
         t, day, kind code (h50lib.KINDS), subkind code, n_targets
  ipairs (ledger items for human / nudge / pause_resume; edge -> every day-present agent): inp idx, recipient, tgt
  plat   (turn_errors infrastructure categories; onsets = first error of a run with gaps > 5 min): t, day, agent
  day_t0, day_t1 (calendar window -15 / +5 min), days (pt_date), agent_codes
No text is read or stored. Times are seconds since 2025-01-01 UTC.

Usage: uv run python hypotheses/H50-field-vs-coupling-transfer-lag/scheme/build.py [--only 38a,51c]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(ROOT / "hypotheses/H50-field-vs-coupling-transfer-lag/analysis"))
from common import REVISION, holdout_mask  # noqa: E402
import h50lib as L  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H50-field-vs-coupling-transfer-lag"
BASE = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc).timestamp()
INFRA = ["timeout", "vm", "resource", "network"]
SUBK = {"plain": 0, "mention": 1, "kickoff": 2}

# NE43 pseudo-units (exception (c): the transition is the object). #51 non-holdout days only.
# Found while building (2026-10-04): the daily bookends stop after 2026-08-04 (last resume/pause 08-04), the nudges
# after 2026-08-20. So: A = bookends + nudges (07-29..08-04, = unit 51f), B = nudges only (08-05..08-20),
# C = neither (08-21..09-04). B vs C isolates the nudge switch-off; A vs B the bookend switch-off (confounded with
# the #focus room split on 08-05).
NE43_A = ("2026-07-29", "2026-08-04")
NE43_B = ("2026-08-05", "2026-08-20")
NE43_C = ("2026-08-21", "2026-09-04")


def secs(s: pl.Series) -> np.ndarray:
    return s.dt.epoch("us").to_numpy() / 1e6 - BASE


def git_commit() -> str:
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    d = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "hypotheses/H50-field-vs-coupling-transfer-lag"],
                       capture_output=True, text=True).stdout
    return (r.stdout.strip() or "none") + ("+uncommitted" if d.strip() else "")


def unit_list():
    pu = pl.read_parquet(SH / "period_units.parquet").filter(~pl.col("holdout"))
    rows = [dict(unit=r["unit_id"], goal_no=r["goal_no"], regime=r["regime"], days=list(r["days"]), n_agents=r["n_agents"],
                 rooms=list(r["rooms"]), kind="period_unit") for r in pu.iter_rows(named=True)]
    cal = pl.read_parquet(SH / "calendar.parquet")
    for name, (a, b) in (("NE43A", NE43_A), ("NE43B", NE43_B), ("NE43C", NE43_C)):
        days = cal.filter((pl.col("pt_date") >= a) & (pl.col("pt_date") <= b) & (pl.col("goal_no") == 51) & ~pl.col("holdout"))["pt_date"].to_list()
        rows.append(dict(unit=name, goal_no=51, regime="III", days=days, n_agents=None, rooms=None, kind="ne43"))
    return rows


def build_unit(u, tabs, allow_holdout=False):
    """allow_holdout is used ONLY by analysis/confirm.py --confirm (locked-holdout confirmation)."""
    days = sorted(u["days"])
    cal = tabs["cal"].filter(pl.col("pt_date").is_in(days)).sort("pt_date")
    days = cal["pt_date"].to_list()
    hm = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    if not allow_holdout:
        assert not any(hm) and not cal["holdout"].any(), f"holdout day in unit {u['unit']}"
    dix = {d: i for i, d in enumerate(days)}
    t0 = secs(cal["win_start"]) - 900
    t1 = secs(cal["win_end"]) + 300
    cw = tabs["cw"].filter(pl.col("pt_date").is_in(days) & (allow_holdout | ~pl.col("holdout")) & (pl.col("ctx_mode") != "summary"))
    agents = np.sort(cw["agent"].unique().to_numpy())
    aix = {int(a): i for i, a in enumerate(agents)}
    cw = cw.with_columns(pl.col("agent").replace_strict(aix, return_dtype=pl.Int64).alias("ai"),
                         pl.col("pt_date").replace_strict(dix, return_dtype=pl.Int64).alias("di")).sort("ai", "t_call")
    kind = cw["kind"].cast(pl.String)
    calls = dict(agent=cw["ai"].to_numpy(), day=cw["di"].to_numpy(), tc=secs(cw["t_call"]), tl=secs(cw["t_log"]),
                 talk=cw["talk"].to_numpy(), act=~kind.is_in(["pause", "wait"]).to_numpy(),
                 first=cw["first_of_day"].to_numpy(), low=(cw["start_conf"].cast(pl.String) == "low").to_numpy(),
                 turn_id=cw["turn_id"].to_numpy(),
                 chat=(cw["ctx_mode"].cast(pl.String) == "chat").to_numpy(),
                 wait=(kind == "wait").to_numpy(), pause=(kind == "pause").to_numpy())
    # sanity: sorted by agent then tc
    key = calls["agent"] * L.KEYMUL + calls["tc"]
    assert np.all(np.diff(key) >= 0)
    turn_pos = dict(zip(calls["turn_id"].tolist(), range(len(calls["turn_id"]))))
    # peer messages
    ch = tabs["chat"].filter(pl.col("pt_date").is_in(days) & (pl.col("speaker_kind") == "agent")).sort("t")
    mid = ch["message_id"].to_list()
    midx = {m: i for i, m in enumerate(mid)}
    snd = np.array([aix.get(int(a), -1) if a is not None else -1 for a in ch["agent"].to_list()], np.int64)
    msgs = dict(t=secs(ch["t"]), day=np.array([dix[d] for d in ch["pt_date"].to_list()], np.int64), sender=snd,
                room=ch["room"].fill_null(-1).to_numpy().astype(np.int64))
    it = tabs["items"].filter(pl.col("turn_id").is_in(calls["turn_id"]))
    ag_it = it.filter(pl.col("kind") == "agent").filter(pl.col("message_id").is_in(mid))
    tpos = np.array([turn_pos[t] for t in ag_it["turn_id"].to_list()], np.int64)
    mpairs = dict(msg=np.array([midx[m] for m in ag_it["message_id"].to_list()], np.int64),
                  rec=calls["agent"][tpos], turn_pos=tpos, ment=ag_it["ment"].to_numpy(),
                  uncertain=ag_it["uncertain"].to_numpy())
    # exogenous inputs
    kk = tabs["kicks"].filter(pl.col("pt_date").is_in(days) & (allow_holdout | ~pl.col("holdout"))
                              & pl.col("kind").is_in(["human_message", "nudge", "pause_resume"])).sort("t")
    kinds, subk, ntg, tin, dinp, kmid = [], [], [], [], [], []
    for r in kk.iter_rows(named=True):
        kname = {"human_message": "human", "nudge": "nudge"}.get(r["kind"], r["subkind"])
        kinds.append(L.K[kname])
        subk.append(SUBK.get(r["subkind"], -1) if r["kind"] == "human_message" else -1)
        ntg.append(r["n_targets"] or 0)
        tin.append(r["t"])
        dinp.append(dix[r["pt_date"]])
        kmid.append(r["message_id"])
    tin = secs(pl.Series(tin, dtype=pl.Datetime("us", "UTC"))) if tin else np.zeros(0)
    tgt_sets = [set(aix[a] for a in (r["targets"] or []) if a in aix) for r in kk.iter_rows(named=True)]
    kix = {m: i for i, m in enumerate(kmid)}
    ex_it = it.filter(pl.col("kind").is_in(["human", "nudge", "pause_resume"]) & pl.col("message_id").is_in(kmid))
    ipi, ipr, ipt = [], [], []
    for m, t in zip(ex_it["message_id"].to_list(), ex_it["turn_id"].to_list()):
        i = kix[m]
        r = int(calls["agent"][turn_pos[t]])
        ipi.append(i)
        ipr.append(r)
        ipt.append(r in tgt_sets[i])
    kinds, subk, ntg, dinp = list(kinds), list(subk), list(ntg), list(dinp)
    tin = list(tin)
    # edges: days without a resume bookend
    for d, day in enumerate(days):
        has = any(k == L.K["resume"] and dd == d for k, dd in zip(kinds, dinp))
        if not has:
            e = len(kinds)
            kinds.append(L.K["edge"])
            subk.append(-1)
            ntg.append(0)
            tin.append(t0[d] + 900)
            dinp.append(d)
            pres = np.unique(calls["agent"][calls["day"] == d])
            for r in pres:
                ipi.append(e)
                ipr.append(int(r))
                ipt.append(False)
    inputs = dict(t=np.asarray(tin, float), day=np.asarray(dinp, np.int64), kind=np.asarray(kinds, np.int64),
                  subkind=np.asarray(subk, np.int64), n_targets=np.asarray(ntg, np.int64))
    ipairs = dict(inp=np.asarray(ipi, np.int64), rec=np.asarray(ipr, np.int64), tgt=np.asarray(ipt, bool))
    # platform onsets
    te = tabs["terr"].filter(pl.col("pt_date").is_in(days) & (allow_holdout | ~pl.col("holdout")) & pl.col("err_cat").cast(pl.String).is_in(INFRA)
                             & pl.col("agent").is_in(list(aix))).sort("agent", "t")
    pa, pt, pd_ = [], [], []
    last = {}
    for a, t, d in zip(te["agent"].to_list(), secs(te["t"]), te["pt_date"].to_list()):
        if a not in last or t - last[a] > 300:
            pa.append(aix[a])
            pt.append(t)
            pd_.append(dix[d])
        last[a] = t
    plat = dict(t=np.asarray(pt, float), day=np.asarray(pd_, np.int64), agent=np.asarray(pa, np.int64))
    U = dict(name=u["unit"], regime=u["regime"], goal_no=u["goal_no"], N=len(agents), day_t0=t0, day_t1=t1,
             days=np.array(days), agent_codes=agents, calls=calls, msgs=msgs, mpairs=mpairs, inputs=inputs,
             ipairs=ipairs, plat=plat)
    return U


def save_unit(U, path):
    flat = {}
    for k, v in U.items():
        if isinstance(v, dict):
            for kk, vv in v.items():
                flat[f"{k}__{kk}"] = np.asarray(vv)
        else:
            flat[k] = np.asarray(v)
    np.savez_compressed(path, **flat)


def load_unit(path):
    z = np.load(path, allow_pickle=False)
    U = {}
    for k in z.files:
        if "__" in k:
            a, b = k.split("__", 1)
            U.setdefault(a, {})[b] = z[k]
        else:
            v = z[k]
            U[k] = v.item() if v.ndim == 0 else v
    return U


def load_tabs():
    return dict(
        cal=pl.read_parquet(SH / "calendar.parquet"),
        cw=pl.read_parquet(SH / "call_windows.parquet", columns=["turn_id", "agent", "pt_date", "holdout", "kind", "talk",
                                                                  "ctx_mode", "t_call", "t_log", "start_conf", "first_of_day"]),
        chat=pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "pt_date", "room", "speaker_kind", "agent"]),
        items=pl.read_parquet(SH / "context_ledger_items.parquet", columns=["turn_id", "message_id", "kind", "ment", "uncertain"]),
        kicks=pl.read_parquet(SH / "kicks_classified.parquet"),
        terr=pl.read_parquet(SH / "turn_errors.parquet", columns=["t", "agent", "err_cat", "pt_date", "holdout"]),
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    (OUT / "units").mkdir(parents=True, exist_ok=True)
    tabs = load_tabs()
    units = unit_list()
    if args.only:
        units = [u for u in units if u["unit"] in args.only.split(",")]
    rows = []
    for u in units:
        U = build_unit(u, tabs)
        n_msgs = len(U["msgs"]["t"])
        elig = (U["N"] >= 3) and (n_msgs >= 100)
        row = dict(unit=u["unit"], goal_no=u["goal_no"], regime=u["regime"], kind=u["kind"], n_days=len(U["days"]),
                   first_day=str(U["days"][0]), last_day=str(U["days"][-1]), N=U["N"], n_calls=len(U["calls"]["tc"]),
                   n_msgs=n_msgs, n_pairs=len(U["mpairs"]["msg"]), n_inputs=len(U["inputs"]["t"]),
                   n_human=int((U["inputs"]["kind"] == L.K["human"]).sum()), n_nudge=int((U["inputs"]["kind"] == L.K["nudge"]).sum()),
                   n_resume=int((U["inputs"]["kind"] == L.K["resume"]).sum()), n_plat=len(U["plat"]["t"]), eligible=elig)
        rows.append(row)
        if elig:
            save_unit(U, OUT / "units" / f"{u['unit']}.npz")
        print(row, flush=True)
    df = pl.DataFrame(rows)
    if args.only and (OUT / "units.parquet").exists():
        old = pl.read_parquet(OUT / "units.parquet").filter(~pl.col("unit").is_in(df["unit"]))
        df = pl.concat([old, df], how="diagonal_relaxed")
    df.write_parquet(OUT / "units.parquet")
    prov = dict(built_by="hypotheses/H50-field-vs-coupling-transfer-lag/scheme/build.py", git_commit=git_commit(),
                inputs=[dict(source="ai-village", revision=REVISION,
                             tables=["call_windows", "context_ledger_items", "chat_core", "kicks_classified",
                                     "turn_errors", "calendar", "period_units"])],
                params=dict(eligible="N>=3 calling agents and >=100 agent chat messages; non-holdout",
                            grid="calendar window -15/+5 min", summary_calls="dropped (ctx_mode summary)",
                            act="kind not in pause/wait", platform="err_cat in timeout/vm/resource/network, onset gap>5min",
                            ne43=dict(A=NE43_A, B=NE43_B, C=NE43_C)),
                built_at=dt.datetime.now(dt.timezone.utc).isoformat())
    p = OUT / "_provenance.json"
    old = json.loads(p.read_text()) if p.exists() else {}
    old["scheme"] = prov
    p.write_text(json.dumps(old, indent=1))


if __name__ == "__main__":
    main()
