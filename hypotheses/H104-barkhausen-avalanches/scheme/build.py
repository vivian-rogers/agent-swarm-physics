"""H104 scheme: per non-holdout goal period, agent at-risk spans, switch events in two channels (work arrivals from
DQ4, attention arrivals from shared project_states w15), field steps (human sessions), kickoffs, nudges, receipts and
step novelty. Codes and times only (no text).

    uv run python hypotheses/H104-barkhausen-avalanches/scheme/build.py [--goals 44,51]

Output: data/processed/H104-barkhausen-avalanches/G<NN>/{days,spans,switches_work,switches_attn,daystart_work,
daystart_attn,steps,step_receipts,kickoffs,nudges}.parquet, periods.parquet, _provenance.json.
Times are float seconds since EPOCH (2025-01-01 UTC). Holdout asserted twice (calendar.holdout, common.holdout_mask).
allow_holdout is set only by analysis/confirm.py (guarded), which writes to its own root.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H104-barkhausen-avalanches"
EPOCH = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)
UTC = dt.timezone.utc
RISK_START = 30 * 60      # at-risk span starts 30 min after the agent's first call of the day
RISK_END = 15 * 60        # and ends 15 min before its last call
ARRIVAL_GAP = 3600.0      # a work switch onto Y needs no commit to Y in the previous 60 min
ATTN_LOOKBACK = 4         # attention switch: Y not held in the previous 4 labelled windows
SESSION_GAP = 600.0       # human messages <= 10 min apart form one session
NOVELTY_WIN = 3600.0
MIN_CALLS_PRESENT = 20


def secs(col: str, alias: str | None = None) -> pl.Expr:
    return ((pl.col(col) - pl.lit(EPOCH)).dt.total_microseconds() / 1e6).alias(alias or col)


def work_filter() -> pl.Expr:
    return pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind") == "agent") & ~pl.col("automated")


def prepare(allow_holdout: bool = False):
    cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("goal_no").is_not_null() & (pl.col("n_agent_events") > 0))
    cal = cal.with_columns(pl.Series("ho", holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())))
    if not allow_holdout:
        cal = cal.filter(~pl.col("ho") & ~pl.col("holdout"))
    cw = (pl.scan_parquet(SH / "call_windows.parquet").filter(pl.lit(allow_holdout) | ~pl.col("holdout"))
          .select("agent", "pt_date", "goal_no", "t_call").collect())
    wc = (pl.scan_parquet(SH / "work_commits.parquet").filter(work_filter())
          .select(pl.col("repo").cast(pl.String), "t", pl.col("author_agent").alias("agent"), "goal_no", "pt_date", "holdout")
          .collect())
    ps = (pl.scan_parquet(SH / "project_states.parquet")
          .filter((pl.col("w_min") == 15) & (pl.col("sources").cast(pl.String) == "all"))
          .select("goal_no", "pt_date", "win", "agent", pl.col("project").cast(pl.String), "holdout").collect())
    if not allow_holdout:   # day-start switches must not look back into held-out days
        wc = wc.filter(~pl.col("holdout"))
        ps = ps.filter(~pl.col("holdout"))
    kc = pl.read_parquet(SH / "kicks_classified.parquet").with_columns(pl.col("kind").cast(pl.String),
                                                                       pl.col("subkind").cast(pl.String))
    kt = pl.read_parquet(SH / "kicks_targets.parquet", columns=["message_id", "primary_target"])
    kr = pl.read_parquet(SH / "kicks_receipts.parquet", columns=["msg", "agent", "t_call", "in_exposure", "is_named", "holdout"])
    return cal, cw, wc, ps, kc, kt, kr


def work_switches(wc: pl.DataFrame) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Within-day work arrivals, and day-start changes vs the agent's previous active day."""
    w = wc.sort("agent", "t").with_columns(secs("t"))
    w = w.with_columns(pl.col("repo").shift(1).over("agent", "pt_date").alias("prev_repo"),
                       pl.col("t").shift(1).over("agent", "repo", "pt_date").alias("t_prev_same"))
    sw = w.filter(pl.col("prev_repo").is_not_null() & (pl.col("prev_repo") != pl.col("repo"))
                  & (pl.col("t_prev_same").is_null() | ((pl.col("t") - pl.col("t_prev_same")) > ARRIVAL_GAP)))
    first = w.group_by("agent", "pt_date").agg(pl.col("t").first(), pl.col("repo").first(), pl.col("repo").last().alias("last_repo"),
                                               pl.col("goal_no").first(), pl.col("holdout").first()).sort("agent", "pt_date")
    first = first.with_columns(pl.col("last_repo").shift(1).over("agent").alias("prev_day_repo"))
    ds = first.with_columns((pl.col("prev_day_repo").is_not_null() & (pl.col("prev_day_repo") != pl.col("repo"))).alias("switch"))
    return sw.select("agent", "pt_date", "goal_no", "t", "repo", "holdout"), ds.select("agent", "pt_date", "goal_no", "t", "switch", "holdout")


def attn_switches(ps: pl.DataFrame, cal: pl.DataFrame) -> tuple[pl.DataFrame, pl.DataFrame]:
    p = ps.join(cal.select("pt_date", "win_start"), on="pt_date", how="inner").with_columns(
        (secs("win_start") + pl.col("win").cast(pl.Float64) * 900.0).alias("t")).sort("agent", "pt_date", "win")
    lags = [pl.col("project").shift(k).over("agent", "pt_date").alias(f"p{k}") for k in range(1, ATTN_LOOKBACK + 1)]
    p = p.with_columns(lags)
    held = pl.any_horizontal([pl.col(f"p{k}") == pl.col("project") for k in range(1, ATTN_LOOKBACK + 1)]).fill_null(False)
    sw = p.filter(pl.col("p1").is_not_null() & (pl.col("p1") != pl.col("project")) & ~held)
    first = p.group_by("agent", "pt_date").agg(pl.col("t").first(), pl.col("project").first(), pl.col("project").last().alias("last_p"),
                                               pl.col("goal_no").first(), pl.col("holdout").first()).sort("agent", "pt_date")
    first = first.with_columns(pl.col("last_p").shift(1).over("agent").alias("prev_day_p"))
    ds = first.with_columns((pl.col("prev_day_p").is_not_null() & (pl.col("prev_day_p") != pl.col("project"))).alias("switch"))
    return (sw.select("agent", "pt_date", "goal_no", "t", pl.col("project").alias("repo"), "holdout"),
            ds.select("agent", "pt_date", "goal_no", "t", "switch", "holdout"))


def sessions(hm: pl.DataFrame) -> pl.DataFrame:
    h = hm.sort("t").with_columns(secs("t"))
    h = h.with_columns((((pl.col("t") - pl.col("t").shift(1)).fill_null(1e9) > SESSION_GAP)
                        | (pl.col("pt_date") != pl.col("pt_date").shift(1)).fill_null(True)).alias("new"))
    h = h.with_columns(pl.col("new").cum_sum().alias("session"))
    return h.group_by("session").agg(pl.col("t").min().alias("t"), pl.col("t").max().alias("t_last"), pl.len().alias("m"),
                                     (pl.col("subkind") == "plain").any().alias("broadcast"),
                                     pl.col("room").first(), pl.col("pt_date").first(), pl.col("message_id"),
                                     pl.col("msg")).sort("t")


def novelty(st: pl.DataFrame, chat: pl.DataFrame, E: np.ndarray) -> list:
    """1 - cos(session mean vector, mean of agent chat in the same room in the previous 60 min)."""
    out = []
    for r in st.iter_rows(named=True):
        rows = chat.filter(pl.col("message_id").is_in(r["message_id"]))["row"].to_numpy()
        prev = chat.filter((pl.col("speaker_kind") == "agent") & (pl.col("room") == r["room"])
                           & (pl.col("t") < r["t"]) & (pl.col("t") >= r["t"] - NOVELTY_WIN))["row"].to_numpy()
        if len(rows) == 0 or len(prev) < 3:
            out.append(None)
            continue
        a = np.asarray(E[rows], np.float32).mean(0)
        b = np.asarray(E[prev], np.float32).mean(0)
        out.append(float(1 - a @ b / (np.linalg.norm(a) * np.linalg.norm(b))))
    return out


def build_goal(g, cal, cw, wsw, wds, asw, ads, kc, kt, kr, chat, E, out_root=OUT, allow_holdout=False, days_filter=None):
    days = cal.filter(pl.col("goal_no") == g).sort("pt_date")
    if days_filter is not None:
        days = days.filter(pl.col("pt_date").is_in(days_filter))
    dl = days["pt_date"].to_list()
    if not dl:
        return None
    if not allow_holdout:
        assert not any(holdout_mask(dl, [g] * len(dl))), f"holdout day in G{g}"
    od = out_root / f"G{g:02d}"
    od.mkdir(parents=True, exist_ok=True)
    c = cw.filter((pl.col("goal_no") == g) & pl.col("pt_date").is_in(dl)).with_columns(secs("t_call"))
    span = c.group_by("pt_date", "agent").agg(pl.len().alias("n_calls"), pl.col("t_call").min().alias("first_call"),
                                              pl.col("t_call").max().alias("last_call"))
    span = span.with_columns((pl.col("first_call") + RISK_START).alias("risk_lo"), (pl.col("last_call") - RISK_END).alias("risk_hi"))
    ap = (span.filter(pl.col("n_calls") >= MIN_CALLS_PRESENT).group_by("pt_date")
          .agg(pl.col("first_call").max().alias("ap_lo"), pl.col("last_call").min().alias("ap_hi")))
    dy = days.select("pt_date", secs("win_start"), secs("win_end")).join(ap, on="pt_date", how="left")
    sel = lambda df: df.filter((pl.col("goal_no") == g) & pl.col("pt_date").is_in(dl))  # noqa: E731
    sw_w, ds_w, sw_a, ds_a = sel(wsw), sel(wds), sel(asw), sel(ads)
    if not allow_holdout:
        for df in (sw_w, ds_w, sw_a, ds_a):
            assert not df["holdout"].fill_null(False).any()
    k = kc.filter((pl.col("goal_no") == g) & pl.col("pt_date").is_in(dl))
    hm = k.filter((pl.col("kind") == "human_message") & pl.col("subkind").is_in(["plain", "mention"]))
    st = sessions(hm) if hm.height else None
    n_steps = 0
    if st is not None:
        st = st.with_columns(pl.Series("novelty", novelty(st, chat, E), dtype=pl.Float64))
        # receipts: earliest receiving call per agent for the session's messages
        rc = (kr.filter(pl.col("in_exposure")).join(st.select("session", pl.col("msg")).explode("msg"), on="msg")
              .with_columns(secs("t_call")).group_by("session", "agent").agg(pl.col("t_call").min().alias("t_read"),
                                                                             pl.col("is_named").any().alias("named")))
        rc.write_parquet(od / "step_receipts.parquet")
        st.drop("message_id", "msg").write_parquet(od / "steps.parquet")
        n_steps = st.height
    kick = k.filter((pl.col("kind") == "goal_kickoff") | (pl.col("subkind") == "kickoff")).sort("t").head(1).select(secs("t"), "pt_date", "room")
    kick.write_parquet(od / "kickoffs.parquet")
    nud = k.filter(pl.col("kind") == "nudge").join(kt, on="message_id", how="left").select(secs("t"), "pt_date", "room",
                                                                                          pl.col("primary_target").alias("target"))
    nud.write_parquet(od / "nudges.parquet")
    dy.write_parquet(od / "days.parquet")
    span.write_parquet(od / "spans.parquet")
    sw_w.drop("holdout").write_parquet(od / "switches_work.parquet")
    sw_a.drop("holdout").write_parquet(od / "switches_attn.parquet")
    ds_w.drop("holdout").write_parquet(od / "daystart_work.parquet")
    ds_a.drop("holdout").write_parquet(od / "daystart_attn.parquet")
    return {"goal_no": g, "n_days": len(dl), "n_agents": span["agent"].n_unique(), "n_sw_work": sw_w.height,
            "n_sw_attn": sw_a.height, "n_steps": n_steps, "n_kick": kick.height, "n_nudges": nud.height}


def load_chat():
    chat = (pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "room", "speaker_kind"])
            .join(pl.read_parquet(SH / "embeddings/chat_index.parquet").with_row_index("row"), on="message_id")
            .with_columns(secs("t"), pl.col("speaker_kind").cast(pl.String)))
    E = np.load(SH / "embeddings/chat_bge_small.npy", mmap_mode="r")
    return chat, E


def main(goals=None, allow_holdout=False, out_root=OUT, days_filter=None):
    cal, cw, wc, ps, kc, kt, kr = prepare(allow_holdout)
    if not allow_holdout:
        kr = kr.filter(~pl.col("holdout"))
    wsw, wds = work_switches(wc)
    asw, ads = attn_switches(ps, pl.read_parquet(SH / "calendar.parquet"))
    chat, E = load_chat()
    gl = goals or sorted(cal["goal_no"].unique().to_list())
    rows = []
    for g in gl:
        r = build_goal(g, cal, cw, wsw, wds, asw, ads, kc, kt, kr, chat, E, out_root, allow_holdout, days_filter)
        if r:
            rows.append(r)
            print(r, flush=True)
    out_root.mkdir(parents=True, exist_ok=True)
    pl.DataFrame(rows).write_parquet(out_root / "periods.parquet")
    prov = {"built_by": "hypotheses/H104-barkhausen-avalanches/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["work_commits (DQ4)", "project_states (w15, all)", "kicks_classified", "kicks_targets",
                                   "kicks_receipts", "call_windows (DQ1)", "chat_core", "embeddings/chat_bge_small",
                                   "calendar"]}],
            "params": {"risk_start_s": RISK_START, "risk_end_s": RISK_END, "arrival_gap_s": ARRIVAL_GAP,
                       "attn_lookback": ATTN_LOOKBACK, "session_gap_s": SESSION_GAP, "novelty_win_s": NOVELTY_WIN,
                       "allow_holdout": allow_holdout},
            "built_at": dt.datetime.now(UTC).isoformat()}
    (out_root / "_provenance.json").write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--goals", default="")
    a = ap.parse_args()
    main([int(x) for x in a.goals.split(",") if x] or None)
