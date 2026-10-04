"""H31 round 1b: E-V (vote consensus) per #26 election round from DQ6 ballots (native test; predictions in
goalperiod-subhypotheses/G26/README.md, written 2026-10-04 before this was run).

Per round r (approval 01-05, runoff 01-05, confirmatory 01-09):
  onset t0   runoff: the administrator's opening message (19:32:19 UTC); confirmatory: the scheduled opening (18:45:00);
             approval: the first ballot (19:25:09; the recorded opening at 19:26:03 postdates 6/9 ballots, H53).
  consensus  the first ballot after which one candidate holds >= 50% of the ballots cast so far, with >= 3 ballots
             (approval: a candidate's approvals / ballots cast; a tie of leaders at the close is right-censored).
  tau_V      t_c - t0 in active hours (ActiveClock from scheme/build.py).
  read-out   tau_read(k): time from t0 until the k-th roster agent's first receiving call that has the round's opening
             message in context (context_ledger_items); approval: the first ballot message.
Ballot rows are read from H11's round-1b copy (data/processed/H11-potts-labor-vs-herding/r1b/G26/ballots.parquet,
phases.parquet: codes and times only).
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SH = ROOT / "data/processed/shared"
H11R = ROOT / "data/processed/H11-potts-labor-vs-herding/r1b/G26"


def _clock(days: pl.DataFrame):
    spec = importlib.util.spec_from_file_location("h31b_ev", HERE.parent / "scheme/build.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.ActiveClock(days)


def _us(t) -> int:
    return int(pl.Series([t]).dt.epoch("us")[0])


def readout(msg_id: str, t0, roster: set[int]) -> dict:
    it = pl.scan_parquet(SH / "context_ledger_items.parquet").filter(pl.col("message_id") == msg_id).select("turn_id").collect()
    tu = pl.scan_parquet(SH / "context_ledger_turns.parquet").filter(pl.col("goal_no") == 26).select(
        "turn_id", "agent", "t_call").collect()
    r = it.join(tu, on="turn_id").filter(pl.col("agent").is_in(list(roster))).group_by("agent").agg(pl.col("t_call").min())
    lag = np.sort(np.array([(t - t0).total_seconds() for t in r["t_call"].to_list()]))
    return dict(n_readers=int(len(lag)), lags_s=lag.tolist(),
                **{f"tau_read{k}_s": (float(lag[k - 1]) if len(lag) >= k else None) for k in (1, 2, 3, 5)},
                tau_read_half_s=(float(lag[int(np.ceil(len(roster) / 2)) - 1]) if len(lag) >= np.ceil(len(roster) / 2) else None))


def ev26_rounds(P: dict) -> dict:
    b = pl.read_parquet(H11R / "ballots.parquet").sort("t")
    ph = pl.read_parquet(H11R / "phases.parquet")
    clock = _clock(P["days"])
    roster = set(pl.read_parquet(SH / "roster.parquet").filter(
        (pl.col("joined") <= "2026-01-05") & (pl.col("left").is_null() | (pl.col("left") > "2026-01-09")) & ~pl.col("claude_code"))["agent"].to_list())

    def act_h(t):
        return float(clock(np.array([_us(t)]))[0] / 3600)

    def phase(value):
        r = ph.filter((pl.col("label_kind") == "phase") & (pl.col("value") == value) & pl.col("preferred"))
        return r["t_valid_from"][0], r["t_valid_to"][0], r["message_id"][0]

    rounds = {}
    for rnd in ("approval", "runoff", "confirmatory"):
        d = b.filter(pl.col("round") == rnd)
        if rnd == "approval":
            t0, msg0 = d["t"].min(), d.sort("t")["message_id"][0]
            t_close = phase("approval_vote")[1]
        else:
            t0, t_close, msg0 = phase("runoff" if rnd == "runoff" else "confirmatory_vote")
            if rnd == "confirmatory":
                t0 = t0.replace(second=0, microsecond=0)      # the scheduled opening (18:45:00)
        voters = d.select("voter", "t").unique("voter", keep="first").sort("t")
        tally, t_c, traj = {}, None, []
        nv = 0
        for v, tv in zip(voters["voter"].to_list(), voters["t"].to_list()):
            nv += 1
            for c in d.filter(pl.col("voter") == v)["candidate"].to_list():
                tally[c] = tally.get(c, 0) + 1
            top = max(tally.values())
            leaders = [c for c, k in tally.items() if k == top]
            share = top / nv
            traj.append(dict(n=nv, t_s=(tv - t0).total_seconds(), top_share=share, n_leaders=len(leaders)))
            if t_c is None and nv >= 3 and share >= 0.5 and len(leaders) == 1:
                t_c = tv
        top = max(tally.values())
        leaders = sorted(c for c, k in tally.items() if k == top)
        ro = readout(msg0, t0, roster)
        tau = (act_h(t_c) - act_h(t0)) if t_c is not None else None
        rounds[rnd] = dict(t0=str(t0), t_close=str(t_close), opening_message=msg0, n_ballots=nv,
                           tally={int(k): int(v) for k, v in tally.items()}, leaders=[int(x) for x in leaders],
                           censored=t_c is None, t_c=str(t_c) if t_c else None, tau_V_h=tau,
                           tau_V_s=(t_c - t0).total_seconds() if t_c else None, onset_h=act_h(t0),
                           readout=ro, ratio_tauV_read3=((t_c - t0).total_seconds() / ro["tau_read3_s"])
                           if (t_c and ro.get("tau_read3_s")) else None, trajectory=traj)
    ru = rounds["runoff"]
    winner = max(ru["tally"], key=ru["tally"].get)
    ap = rounds["approval"]
    return {"source": "DQ6 ballots per round (round 1b)", "rounds": rounds,
            "onset_h": ru["onset_h"], "t_cons_h": (ru["onset_h"] + ru["tau_V_h"]) if ru["tau_V_h"] is not None else None,
            "tau_V_h": ru["tau_V_h"], "winner": int(winner), "n_declared_post": ru["n_ballots"],
            "final_share": ru["tally"][winner] / ru["n_ballots"], "pre_runoff_max_share": max(ap["tally"].values()) / ap["n_ballots"],
            "pre_runoff_n": ap["n_ballots"], "rise_posthoc_h": None, "share_before_posthoc": None,
            "trajectory": [(x["t_s"] / 3600, x["top_share"], x["n"]) for x in ru["trajectory"]]}
