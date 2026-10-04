"""H30 scheme: per-goal-period kick table and content pairs (no text) from the shared tables.

Writes data/processed/H30-operator-susceptibility/G<NN>/{kicks.parquet, content.parquet, build.json, _provenance.json}.
Non-holdout days only (asserted in the loaders). Run:
  uv run python hypotheses/H30-operator-susceptibility/scheme/build.py --period G51   (or --all)
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis"))
from h30lib import *  # noqa: E402,F403

PERIODS = ["G04", "G05", "G06", "G13", "G30", "G31", "G33", "G35", "G37", "G38", "G39", "G40", "G41", "G42", "G44", "G51"]


def build_period(p: str, allow_holdout: bool = False, days: list[str] | None = None, out_dir: Path | None = None,
                 data: str = "r1") -> dict:
    """data = "r1" (round 1: activity_bins, all named agents as nudge targets, kick at the posting minute, exposure
    recipients) or "r1b" (round 1b, 2026-10-04: activity_bins_fixed, the nudge's leading @ as its only target, kicks
    timed at the receiving call and recipients from the DQ1 context ledger; content also with the second embedding
    model). Round-1b outputs go to OUT/r1b/<period>."""
    t0 = time.time()
    goal = int(p[1:])
    days = days or period_days(goal, allow_holdout=allow_holdout)
    if not allow_holdout:
        assert_no_holdout(days)
    panels, meta = load_panels(days, allow_holdout=allow_holdout, data=data)
    regimes = sorted({str(meta[pp.label]["regime"]) for pp in panels})
    if len(regimes) != 1:
        raise RuntimeError(f"{p}: mixed regimes {regimes}")
    regime = regimes[0]
    kick_counts = None
    if data == "r1b":
        msgs = load_operator_messages_r1b([pp.label for pp in panels])
        kicks, kick_counts = build_kicks_r1b(panels, msgs)
    else:
        msgs = load_operator_messages([pp.label for pp in panels])
        kicks = build_kicks(panels, msgs)
    kicks = context_fill(kicks, regime) if kicks.height else kicks
    ros = pl.read_parquet(SH / "roster.parquet").select(pl.col("agent").cast(pl.Int32), "lab")
    gday = {pp.day: pp.goal_day for pp in panels}
    kicks = (kicks.join(ros, on="agent", how="left")
             .with_columns(pl.col("day").replace_strict(gday, default=None).alias("goal_day"),
                           pl.lit(regime).alias("regime")))
    # content pairs: every kick with an embedding for the message
    dmap = {pp.label: pp.day for pp in panels}
    if data == "r1b":   # nudge pools by leading target only
        tg = pl.when(pl.col("kind") == "nudge").then(pl.concat_list(pl.col("target").cast(pl.Int64))).otherwise(
            pl.col("named").cast(pl.List(pl.Int64)))
    else:
        tg = pl.col("named").cast(pl.List(pl.Int64))
    mm = (msgs.filter(pl.col("kind") != "bookend")
          .with_columns(pl.col("pt_date").replace_strict(dmap, default=None).alias("day"), tg.alias("targets"))
          .select("msg", "day", "kind", "targets"))
    pairs = kicks.with_row_index("pair").with_columns(pl.col("pair").cast(pl.Int64))
    out = out_dir or (out_root(data) / p)
    out.mkdir(parents=True, exist_ok=True)
    n_stmt = 0
    for model in (("bge_small", "gte_modernbert") if data == "r1b" else ("bge_small",)):
        stmt_t, stmt_v, n_stmt = load_statements([pp.label for pp in panels], regime, allow_holdout=allow_holdout, model=model)
        U = message_vectors(msgs, regime, model=model)
        P, Q, npre, npost, S = pre_post_means(stmt_t, stmt_v, pairs)
        cs = content_scores(pairs.select("pair", "msg", "agent", "day", "cls", "kind"), P, Q, U, mm, S=S,
                            rng=np.random.default_rng(SEED + goal))
        cs = cs.with_columns(pl.Series("n_pre", npre), pl.Series("n_post", npost))
        cs.write_parquet(out / ("content.parquet" if model == "bge_small" else "content_gte.parquet"), compression="zstd")
    kicks.write_parquet(out / "kicks.parquet", compression="zstd")
    info = {"period": p, "regime": regime, "days": [pp.label for pp in panels], "n_days": len(panels),
            "n_agents_max": int(max(len(pp.agents) for pp in panels)),
            "n_messages": {k: int(v) for k, v in msgs.group_by("kind").len().iter_rows()},
            "n_kicks": {k: int(v) for k, v in kicks.group_by("cls").len().iter_rows()} if kicks.height else {},
            "n_statements": int(n_stmt), "n_pairs_both_sides": int(((npre > 0) & (npost > 0)).sum()),
            "data": data, "kick_counts_r1b": kick_counts,
            "fill_coverage": float(kicks["fill"].is_not_nan().mean()) if kicks.height else None,
            "ptok_coverage": float(kicks["ptok"].is_not_nan().mean()) if kicks.height else None,
            "secs": round(time.time() - t0, 1)}
    jdump(info, out / "build.json")
    tables = (["activity_bins", "calendar", "chat_core", "chat_mentions_clean", "exposure", "roster", "events_core",
               "actions", "embeddings/statements", "embeddings/chat_index", "embeddings/chat_bge_small",
               "embeddings/intentions_bge_small", f"embeddings/whitening_{regime}"] if data == "r1" else
              ["activity_bins_fixed", "calendar", "call_windows", "context_ledger_items", "kicks_classified",
               "chat_core", "chat_text (leading @ only, in memory)", "roster", "events_core", "actions",
               "embeddings/statements", "embeddings/chat_index", "embeddings/{chat,intentions}_{bge_small,gte_modernbert}",
               f"embeddings/whitening[_gte_modernbert]_{regime}"])
    write_provenance(out, "hypotheses/H30-operator-susceptibility/scheme/build.py", tables,
                     {"period": p, "data": data, "con_win_s": CON_WIN_S, "con_kmax": CON_KMAX,
                      "basis": "last 8 statements in 2 h", "n_match": N_MATCH, "classes": CLASSES})
    return info


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", default=None)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--data", default="r1", choices=["r1", "r1b"])
    a = ap.parse_args()
    todo = PERIODS if a.all else [a.period]
    for p in todo:
        info = build_period(p, data=a.data)
        print(json.dumps({k: v for k, v in info.items() if k != "days"}, default=str), flush=True)
