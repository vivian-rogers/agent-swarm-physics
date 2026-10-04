"""H68 scheme: per-agent dilution units from H18's round-1b ledger pending tables.

  uv run python hypotheses/H68-dilution-mixture/scheme/build.py            # all periods
  uv run python hypotheses/H68-dilution-mixture/scheme/build.py --period G38

Input: data/processed/H18-attention-dilution/r1b/G<NN>/{talks,pending,wakes,wake_pending}.parquet (built by H18's
scheme/build_ledger.py from the DQ1 context ledger, chat_mentions_clean and DQ2 reply_pairs; holdout already dropped).
This script re-applies the holdout mask and asserts nothing held out remains.

Output: data/processed/H68-dilution-mixture/G<NN>/units.parquet, one row per scored (talk, pending sender):
  talk_id, agent, day (int code within period), pt_date, t_us, k (ledger k_since_talk), logk, n (pending messages of
  the sender), rank_min, ment (any pending message of the sender @-mentions the agent), n_ment (how many do), resp (mention response),
  resp_reply (DQ2 reply parent among the sender's pending messages), engaged (agent addressed this sender in its
  previous talk turn that day, among pending senders), after_pause, lab.
  G51 also: wake_units.parquet (timer-wake batches, D2: k = batch size, resp = mention within 300 s).
No text anywhere.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "4")

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402

SRC = ROOT / "data/processed/H18-attention-dilution/r1b"
OUT = ROOT / "data/processed/H68-dilution-mixture"
SH = ROOT / "data/processed/shared"
PERIODS = ["G10", "G24", "G25", "G26", "G27", "G30", "G31", "G35", "G36", "G37", "G38", "G39", "G40", "G41", "G42",
           "G44", "G51"]


def lab_map() -> dict[int, str]:
    r = pl.read_parquet(SH / "roster.parquet")
    return dict(zip(r["agent"].to_list(), r["lab"].to_list()))


def drop_holdout(df: pl.DataFrame, g: int) -> pl.DataFrame:
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "holdout"])
    df = df.join(cal, on="pt_date", how="left")
    hm = np.array(holdout_mask(df["pt_date"].to_list(), [g] * df.height), dtype=bool)
    keep = ~hm & ~df["holdout"].fill_null(True).to_numpy()
    return df.filter(pl.Series(keep)).drop("holdout")


def build_period(p: str) -> dict:
    g = int(p[1:])
    d = SRC / p
    talks = pl.read_parquet(d / "talks.parquet")
    n0 = talks.height
    talks = drop_holdout(talks, g)
    assert talks.height == n0, f"{p}: held-out talks present in the H18 input"
    pend = pl.read_parquet(d / "pending.parquet")
    pend = pend.filter(pl.col("talk_id").is_in(talks["talk_id"].implode()))
    sc = pend.filter(pl.col("scored"))
    units = (sc.group_by("talk_id", "sender")
             .agg(pl.len().alias("n"), pl.col("rank").min().alias("rank_min"), pl.col("ment_i").any().alias("ment"),
                  pl.col("ment_i").sum().cast(pl.Int16).alias("n_ment"),
                  pl.col("resp").any().alias("resp"), pl.col("resp_reply").any().alias("resp_reply")))
    tk = talks.select("talk_id", "agent", "pt_date", "t_us", "k", "after_pause")
    units = units.join(tk, on="talk_id", how="inner")
    # engagement: the sender was addressed (as a pending sender) in the agent's previous talk turn that day
    order = tk.sort("agent", "pt_date", "t_us").with_columns(
        pl.col("talk_id").shift(1).over("agent", "pt_date").alias("prev_talk"))
    units = units.join(order.select("talk_id", "prev_talk"), on="talk_id", how="left")
    addressed = units.filter(pl.col("resp")).select(pl.col("talk_id").alias("prev_talk"), "sender",
                                                    pl.lit(True).alias("engaged"))
    units = units.join(addressed, on=["prev_talk", "sender"], how="left").with_columns(
        pl.col("engaged").fill_null(False)).drop("prev_talk")
    days = sorted(units["pt_date"].unique().to_list())
    labs = lab_map()
    units = units.with_columns(
        pl.col("pt_date").replace_strict({x: i for i, x in enumerate(days)}, return_dtype=pl.Int16).alias("day"),
        pl.col("k").cast(pl.Float64).log().alias("logk"),
        pl.col("agent").replace_strict(labs, return_dtype=pl.String).alias("lab"),
    ).sort("talk_id", "sender")
    o = OUT / p
    o.mkdir(parents=True, exist_ok=True)
    units.write_parquet(o / "units.parquet", compression="zstd")
    info = {"period": p, "units": units.height, "talks": units["talk_id"].n_unique(), "agents": units["agent"].n_unique(),
            "days": len(days)}
    if p == "G51" and (d / "wakes.parquet").exists():
        wk = drop_holdout(pl.read_parquet(d / "wakes.parquet"), g)
        wp = pl.read_parquet(d / "wake_pending.parquet").filter(pl.col("wake_id").is_in(wk["wake_id"].implode()))
        wsc = wp.filter(pl.col("scored")) if "scored" in wp.columns else wp
        wu = (wsc.group_by("wake_id", "sender")
              .agg(pl.len().alias("n"), pl.col("ment_i").any().alias("ment"), pl.col("resp").any().alias("resp"),
                   pl.col("resp_reply").any().alias("resp_reply")))
        kcol = "k" if "k" in wk.columns else "k_w"
        wu = wu.join(wk.select("wake_id", "agent", "pt_date", pl.col(kcol).alias("k")), on="wake_id", how="inner")
        wu = wu.filter(pl.col("k") >= 1).with_columns(
            pl.col("pt_date").replace_strict({x: i for i, x in enumerate(sorted(wu["pt_date"].unique().to_list()))},
                                             return_dtype=pl.Int16).alias("day"),
            pl.col("k").cast(pl.Float64).log().alias("logk"),
            pl.col("agent").replace_strict(labs, return_dtype=pl.String).alias("lab"))
        wu.write_parquet(o / "wake_units.parquet", compression="zstd")
        info["wake_units"] = wu.height
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", default=None)
    a = ap.parse_args()
    ps = [a.period] if a.period else PERIODS
    infos = [build_period(p) for p in ps]
    for i in infos:
        print(i, flush=True)
    prov = {"built_by": "hypotheses/H68-dilution-mixture/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["H18-attention-dilution/r1b/G<NN>/{talks,pending,wakes,wake_pending}",
                                   "shared/roster", "shared/calendar"]}],
            "params": {"periods": ps, "unit": "(talk call, scored pending agent sender)", "response": "mention (resp); "
                       "reply parent (resp_reply)", "holdout": "re-masked (holdout_mask, calendar.holdout); asserted 0"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    main()
