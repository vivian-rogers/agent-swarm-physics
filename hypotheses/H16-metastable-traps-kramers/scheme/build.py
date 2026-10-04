"""H16 scheme: build per-goal-period trap tables from the shared tables.

Outputs, per period, in data/processed/H16-metastable-traps-kramers/G<NN>/ (non-holdout days only unless called by
confirm.py with allow_holdout=True, which writes to a separate confirm/ folder):
  ts1.parquet     TS1 inactive spells, strict (any active row ends the spell); kick counts during the spell
  ts1r.parquet    TS1r inactive spells, robust (isolated active rows ignored)
  ts2.parquet     TS2 pause-chain gates (regime III; empty elsewhere)
  ts3.parquet     TS3 error-loop turn rows
  ts4.parquet     TS4 identical-command-loop turn rows (command text hashed in memory, never stored)
  minutes.parquet per agent-day-minute active indicator a (agents with >= 1 active row that day)
  kicks.parquet   kick times by class reaching each agent (agent, ts, kclass); no text
Each folder gets a _provenance.json.

Usage: uv run python hypotheses/H16-metastable-traps-kramers/scheme/build.py [--period G38 ...] [--all]
       ... build.py --r1b [G38 ...]   round 1b (improved data, 2026-10-04): TS3 from real failures (turn_outcomes),
       N_tgt = leading-@ nudge target, plus TS5/TS6 window traps from Jev v3.1; writes <OUT>/r1b/<period>/.
       Without --r1b the round-1 path is unchanged.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis"))
import h16lib as L  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

# Exploratory periods (non-holdout). Windows exclude step changes inside the period (named on the card).
PERIODS = {
    "G27": dict(goal=27, regime="I"),
    "G30": dict(goal=30, regime="I"),
    "G31": dict(goal=31, regime="I", date_to="2026-02-20"),        # NE11 (100-turn session cap) on 02-20 excluded
    "G37": dict(goal=37, regime="III"),
    "G38": dict(goal=38, regime="III"),                             # NE17 (04-14) split is a sensitivity in analysis
    "G39": dict(goal=39, regime="III"),
    "G40": dict(goal=40, regime="III"),
    "G41": dict(goal=41, regime="III"),
    "G42": dict(goal=42, regime="III"),
    "G44": dict(goal=44, regime="III"),
    "G51": dict(goal=51, regime="III", date_to="2026-09-03"),      # NE33 batch join (09-03) onward excluded; tail held out
}


def build_period(name: str, days: list[str], out: Path, allow_holdout=False, r1b=False) -> dict:
    t0 = time.time()
    out.mkdir(parents=True, exist_ok=True)
    W = L.windows(days)
    extra = {}
    if r1b:
        import r1blib as RB  # noqa: E402
        rows = RB.load_rows_r1b(days, allow_holdout=allow_holdout)
        K, extra = RB.load_kicks_r1b(days, allow_holdout=allow_holdout)
    else:
        rows = L.load_rows(days, allow_holdout=allow_holdout)
        K = L.load_kicks(days, allow_holdout=allow_holdout)
    ts1 = L.build_ts1(rows, W, K)
    ts1r = L.build_ts1(rows, W, K, robust=True)
    ts2 = L.build_ts2(rows, W, K)
    ts3 = L.build_turn_loops(rows, W, K, "err")
    ts4 = L.build_turn_loops(rows, W, K, "cmd")
    MA = L.minute_activity(rows, W)
    mins = []
    for d, (ag, A) in MA.items():
        n_ag, n_min = A.shape
        mins.append(pl.DataFrame({"pt_date": [d] * (n_ag * n_min), "agent": np.repeat(ag, n_min).astype(np.int16),
                                  "minute": np.tile(np.arange(n_min, dtype=np.int16), n_ag), "a": A.ravel().astype(np.int8)}))
    mins = pl.concat(mins) if mins else pl.DataFrame()
    kk = []
    for a, cl in K.items():
        for c, arr in cl.items():
            kk.append(pl.DataFrame({"agent": np.full(len(arr), a, np.int16), "ts": arr, "kclass": [c] * len(arr)}))
    kk = pl.concat(kk) if kk else pl.DataFrame({"agent": [], "ts": [], "kclass": []})
    tables = [("ts1", ts1), ("ts1r", ts1r), ("ts2", ts2), ("ts3", ts3), ("ts4", ts4), ("minutes", mins), ("kicks", kk)]
    if r1b:
        tables += [("ts5", RB.build_window_traps(days, K, "blocked", allow_holdout)),
                   ("ts6", RB.build_window_traps(days, K, "loop", allow_holdout))]
    for nm, df in tables:
        df.write_parquet(out / f"{nm}.parquet", compression="zstd")
    L.write_provenance(out, "hypotheses/H16-metastable-traps-kramers/scheme/build.py",
                       ["events_core", "actions", "artifact_commands_text (hashed)", "chat_core", "chat_mentions_clean",
                        "exposure", "calendar", "roster"],
                       {"period": name, "days": days, "allow_holdout": allow_holdout, "r1b": r1b, **extra, "MIN_GAP_S": L.MIN_GAP_S,
                        "ISO_S": L.ISO_S, "LOOP_MIN": L.LOOP_MIN, "TS4_MAX_GAP_S": L.TS4_MAX_GAP_S,
                        "kick_classes": list(L.KCLASSES), "mentions": "chat_mentions_clean.mentions_roster",
                        **({"ts3": "turn_outcomes.failed (bash/type) or platform error_class", "N_tgt": "leading-@ nudge target",
                            "ts5": "v3 p_blocked >= 0.5 window spells", "ts6": "v3 longest_run >= 5 window spells"} if r1b else {})})
    info = {"period": name, "n_days": len(days), "ts1": ts1.height, "ts1r": ts1r.height, "ts2": ts2.height,
            "ts3": ts3.height, "ts4": ts4.height, "agent_days": len(rows), "seconds": round(time.time() - t0, 1)}
    print(info, flush=True)
    return info


def main():
    args = sys.argv[1:]
    r1b = "--r1b" in args
    sel = [a for a in args if a.startswith("G")]
    names = sel if sel else list(PERIODS)
    for nm in names:
        p = PERIODS[nm]
        days = L.period_days(p["goal"], allow_holdout=False, date_from=p.get("date_from"), date_to=p.get("date_to"))
        L.assert_no_holdout(days)
        build_period(nm, days, (L.OUT / "r1b" / nm) if r1b else (L.OUT / nm), r1b=r1b)


if __name__ == "__main__":
    main()
