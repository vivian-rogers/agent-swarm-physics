"""H35 scheme: per-goal-period nudge, minute-grid and gate tables from the shared tables (non-holdout only).

Outputs, per period, in data/processed/H35-nudger-maxwell-demon/<period>/ (parquet, zstd, no text):
  nudges.parquet  one row per automated `repeated-idling` message on the period's days: message_id, t, pt_date, room,
                  target (leading-@ agent code; null if unmatched), n_mentions (clean roster mentions),
                  h04_targets (H04 mapping: all valid roster mentions)
  grid.parquet    agent-minute decision epochs with states (D, G, K, N), nudge indicator M, kicks and outcomes
  gates.parquet   TS2r gates (regime III) with gate states, M_g, escape and y30_gate
  _provenance.json
Text is read in memory only to find the trigger tag and the leading target; it is never written.

Usage: uv run python hypotheses/H35-nudger-maxwell-demon/scheme/build.py [G51 G38 ...] [--all]
Confirmatory use: confirm.py calls build_period(..., allow_holdout=True, out=<confirm folder>).
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis"))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "infra/shared"))
import h35lib as L  # noqa: E402
from h35lib import h16lib  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
import common  # noqa: E402  (infra/shared/common.py: mention_regexes)

MIRRORS = ("pause", "send_message_back_to_chat", "search_history", "move_to_room")
TAG = "triggered by: [repeated-idling]"

# Exploratory periods (non-holdout). Windows exclude step changes named on the card.
PERIODS = {
    "G27": dict(goal=27, gate=False),                                   # NE10 before-period (no nudger)
    "G30": dict(goal=30, gate=False),                                   # NE10: first nudges on 02-13
    "G31": dict(goal=31, gate=False, date_to="2026-02-20"),            # NE11 (02-20) excluded, as in H16
    "G33": dict(goal=33, gate=False),
    "G35": dict(goal=35, gate=False),
    "G36": dict(goal=36, gate=False),
    "G37": dict(goal=37, gate=True),
    "G38": dict(goal=38, gate=True),
    "G39": dict(goal=39, gate=True),
    "G40": dict(goal=40, gate=True),
    "G41": dict(goal=41, gate=True),
    "G42": dict(goal=42, gate=True),
    "G44": dict(goal=44, gate=True),
    "G51": dict(goal=51, gate=True, date_to="2026-08-20"),             # nudger on (07-06 .. 08-19)
    "G51off": dict(goal=51, gate=True, date_from="2026-08-21", date_to="2026-09-03"),  # nudger silent; NE33 on 09-03
    # confirm.py dry-run stand-ins only (subsets of G51, the only short-pause non-holdout period)
    "G51a": dict(goal=51, gate=True, date_from="2026-07-06", date_to="2026-07-11", standin=True),
    "G51b": dict(goal=51, gate=True, date_from="2026-07-13", date_to="2026-07-18", standin=True),
}


def roster_today():
    ros = pl.read_parquet(L.SH / "roster.parquet").filter(~pl.col("claude_code"))
    return ros


def nudge_table(days: list[str], allow_holdout=False) -> pl.DataFrame:
    """Automated repeated-idling messages on `days` with the leading-@ target (no text kept)."""
    if not allow_holdout:
        h16lib.assert_no_holdout(days)
    chat = pl.read_parquet(L.SH / "chat_core.parquet", columns=["message_id", "t", "pt_date", "room", "speaker_kind"])
    men = pl.read_parquet(L.SH / "chat_mentions_clean.parquet", columns=["message_id", "mentions_roster"])
    assert chat.height == men.height and (chat["message_id"] == men["message_id"]).all()
    chat = chat.with_columns(men["mentions_roster"].alias("men"))
    au = chat.filter((pl.col("speaker_kind").cast(pl.Utf8) == "automated") & pl.col("pt_date").is_in(days))
    if au.height == 0:
        return pl.DataFrame(schema={"message_id": pl.Utf8, "t": pl.Datetime("us", "UTC"), "pt_date": pl.Utf8, "room": pl.Int8,
                                    "target": pl.Int16, "n_mentions": pl.Int16, "h04_targets": pl.List(pl.Int8), "ts": pl.Float64})
    txt = pl.read_parquet(L.SH / "chat_text.parquet", columns=["message_id", "text"]).filter(
        pl.col("message_id").is_in(au["message_id"].implode()))
    au = au.join(txt, on="message_id", how="left")
    au = au.filter(pl.col("text").str.contains(TAG, literal=True))
    ros = roster_today()
    agents = [{"id": int(a), "name": n} for a, n in ros.select("agent", "name").iter_rows()]
    pats = common.mention_regexes(agents)
    span = {int(a): (j, l) for a, j, l in ros.select("agent", "joined", "left").iter_rows()}
    tgt = []
    for d, text in au.select("pt_date", "text").iter_rows():
        best, blen = None, 0
        if text and text.startswith("@"):
            for a, pat in pats.items():
                j, l = span[a]
                if not (j <= d and (l is None or d < l)):
                    continue
                m = pat.match(text, 1)
                if m and (m.end() - m.start()) > blen:
                    best, blen = a, m.end() - m.start()
        tgt.append(best)
    out = au.with_columns(pl.Series("target", tgt, dtype=pl.Int16),
                          pl.col("men").list.len().cast(pl.Int16).alias("n_mentions"),
                          pl.col("men").alias("h04_targets"),
                          (pl.col("t").dt.epoch("us") / 1e6).alias("ts"))
    return out.select("message_id", "t", "pt_date", "room", "target", "n_mentions", "h04_targets", "ts").sort("t")


def kicks_with_targets(days: list[str], nud: pl.DataFrame, allow_holdout=False) -> dict:
    """H16 kick classes (clean mentions, exposure), with N_tgt replaced by the leading-@ target and every other
    exposure to a nudge (including being named second) counted as N_by."""
    K = h16lib.load_kicks(days, allow_holdout=allow_holdout)
    for a in K:
        K[a].pop("N_tgt", None)
        K[a].pop("N_by", None)
    chat = pl.read_parquet(L.SH / "chat_core.parquet", columns=["message_id"]).with_row_index("msg")
    ids = chat.filter(pl.col("message_id").is_in(nud["message_id"].implode()))
    ex = (pl.read_parquet(L.SH / "exposure.parquet", columns=["msg", "agent"]).join(ids, on="msg", how="inner")
          .join(nud.select("message_id", "target", "ts"), on="message_id", how="inner"))
    by = ex.filter(pl.col("agent").cast(pl.Int16) != pl.col("target").fill_null(-1))
    for (a,), g in by.group_by(["agent"]):
        K.setdefault(int(a), {})["N_by"] = np.sort(g["ts"].to_numpy())
    for (a,), g in nud.drop_nulls("target").group_by(["target"]):
        K.setdefault(int(a), {})["N_tgt"] = np.sort(g["ts"].to_numpy())
    return K


def tool_rows(days: list[str]) -> dict:
    acts = (pl.read_parquet(L.SH / "actions.parquet", columns=["t", "agent", "action"])
            .filter(pl.col("agent").is_not_null() & ~pl.col("action").cast(pl.Utf8).is_in(list(MIRRORS)))
            .with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8).alias("pt_date"))
            .filter(pl.col("pt_date").is_in(days))
            .with_columns((pl.col("t").dt.epoch("us") / 1e6).alias("ts")))
    return {(int(a), d): np.sort(g["ts"].to_numpy()) for (a, d), g in acts.group_by(["agent", "pt_date"])}


def build_period(name: str, days: list[str], out: Path, gate: bool, allow_holdout=False) -> dict:
    t0 = time.time()
    out.mkdir(parents=True, exist_ok=True)
    W = h16lib.windows(days)
    rows = h16lib.load_rows(days, allow_holdout=allow_holdout)
    nud = nudge_table(days, allow_holdout=allow_holdout)
    K = kicks_with_targets(days, nud, allow_holdout=allow_holdout)
    gates = L.gate_table(rows, W, K) if gate else pl.DataFrame()
    grid = L.build_grid(rows, W, gates, K, tool_rows(days), regime_gate=gate)
    nud.write_parquet(out / "nudges.parquet", compression="zstd")
    grid.write_parquet(out / "grid.parquet", compression="zstd")
    if gates.height:
        keep = [c for c in gates.columns if c not in ("chain",)]
        gates.select(keep).write_parquet(out / "gates.parquet", compression="zstd")
    L.write_provenance(out, "hypotheses/H35-nudger-maxwell-demon/scheme/build.py",
                       ["events_core", "actions", "artifact_commands_text (hashed, via h16lib)", "chat_core",
                        "chat_text (tag and leading target only, in memory)", "chat_mentions_clean", "exposure", "calendar", "roster"],
                       {"period": name, "days": days, "allow_holdout": allow_holdout, "gate": gate, "tag": TAG,
                        "state_time": "end of minute", "burn_min": L.BURN_MIN, "horizon": L.HORIZON, "mirrors": MIRRORS})
    info = {"period": name, "n_days": len(days), "nudges": nud.height, "targeted": int(nud["target"].is_not_null().sum()),
            "grid": grid.height, "grid_nudge_epochs": int(grid["M"].sum()) if grid.height else 0,
            "gates": gates.height, "nudged_gates": int(gates["M"].sum()) if gates.height else 0,
            "seconds": round(time.time() - t0, 1)}
    print(info, flush=True)
    return info


def period_days(p: dict, allow_holdout=False) -> list[str]:
    return h16lib.period_days(p["goal"], allow_holdout=allow_holdout, date_from=p.get("date_from"), date_to=p.get("date_to"))


def main():
    args = sys.argv[1:]
    names = [k for k, v in PERIODS.items() if not v.get("standin")] if ("--all" in args or not args) else [a for a in args if a in PERIODS]
    for nm in names:
        p = PERIODS[nm]
        days = period_days(p)
        h16lib.assert_no_holdout(days)
        if not days:
            print(nm, "no non-holdout days")
            continue
        build_period(nm, days, L.OUT / nm, p["gate"])


if __name__ == "__main__":
    main()
