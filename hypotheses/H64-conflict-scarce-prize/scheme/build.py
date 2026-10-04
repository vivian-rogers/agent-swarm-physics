"""H64 scheme: reply-stance rows (DQ2) per non-holdout period, plus the native relation tables (#12, #26, #23).

    uv run python hypotheses/H64-conflict-scarce-prize/scheme/build.py

Writes data/processed/H64-conflict-scarce-prize/{replies,g12_rel,g26_rel,g23_rel,g23_games}.parquet and
_provenance.json. Codes and numbers only; #23 game ids are read from agent chat text in memory and stored as hashes.
Rules are the card's (written 2026-10-04 19:20 UTC, before any H64 outcome statistic).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import datetime as dt  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H64-conflict-scarce-prize"
UTC = dt.timezone.utc
BLOCK_S = 1800

G26_RIVALS = (0, 6, 17)
G26_RESULT = dt.datetime(2026, 1, 5, 19, 35, 22, 589746, tzinfo=UTC)
G26_CONF = dt.datetime(2026, 1, 9, 18, 45, 0, tzinfo=UTC)
ALLOW_HOLDOUT = False   # set only by analysis/confirm.py under --confirm
LICHESS = re.compile(r"lichess\.org/([A-Za-z0-9]{8})")


def load_replies() -> pl.DataFrame:
    rp = pl.read_parquet(SH / "reply_pairs.parquet", columns=[
        "B_message_id", "A_message_id", "b_agent", "a_agent", "a_kind", "pair_set", "labelled", "p_reply",
        "p_supports", "p_opposes", "stance", "stance_conf", "opp_type", "goal_no", "pt_date", "holdout", "room",
        "regime"])
    rp = rp.filter((pl.col("pair_set") == "cand") & pl.col("labelled") & (ALLOW_HOLDOUT | ~pl.col("holdout"))
                   & (pl.col("a_kind") == 0)
                   & (pl.col("a_agent") >= 0) & (pl.col("b_agent") >= 0) & (pl.col("a_agent") != pl.col("b_agent"))
                   & (pl.col("p_reply") >= 0.5))
    cc = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t"]).rename({"message_id": "B_message_id"})
    rp = rp.join(cc, on="B_message_id", how="left")
    if not ALLOW_HOLDOUT:
        hm = holdout_mask(rp["pt_date"].to_list(), rp["goal_no"].to_list())
        rp = rp.filter(~pl.Series(hm))
    st = pl.col("stance").cast(pl.String)
    rp = rp.with_columns(
        y=pl.when(st == "supports").then(1).when(st == "opposes").then(-1).otherwise(0).cast(pl.Int8),
        s=(pl.col("p_supports") - pl.col("p_opposes")).cast(pl.Float32),
        conf_opp=((st == "opposes") & (pl.col("stance_conf") >= 0.8)),
        has_sub=pl.col("opp_type").is_not_null(),
        tsec=pl.col("t").dt.epoch("s"),
    ).with_columns(
        pos_opp=pl.col("conf_opp") & (pl.col("opp_type").cast(pl.String) == "position").fill_null(False),
        block=(pl.col("room").cast(pl.Int64) * 10_000_000 + pl.col("tsec") // BLOCK_S),
    )
    pu = pl.read_parquet(SH / "period_units.parquet").select("unit_id", "goal_no", "start", "end")
    rp = rp.sort("t").join_asof(pu.sort("start").rename({"start": "t"}), on="t", by="goal_no", strategy="backward")
    return rp.select("B_message_id", "A_message_id", "goal_no", "unit_id", "pt_date", "regime", "t", "room",
                     "b_agent", "a_agent", "y", "s", "p_reply", "stance_conf", "conf_opp", "pos_opp", "has_sub",
                     "block")


def g12(rp: pl.DataFrame) -> pl.DataFrame:
    gt = pl.read_parquet(SH / "ground_truth_labels.parquet").filter(
        pl.col("preferred") & ~pl.col("holdout") & (pl.col("goal_no") == 12))
    ph = gt.filter(pl.col("label_kind") == "phase").select("unit", "value", "t_valid_from", "t_valid_to")
    tm = gt.filter(pl.col("label_kind") == "team").select("unit", "agent", "value")
    res = gt.filter(pl.col("label_kind") == "debate_result").select("unit", "value")
    x = rp.filter(pl.col("goal_no") == 12)
    out = []
    for u, v, a, b in ph.iter_rows():
        T = dict(tm.filter(pl.col("unit") == u).select("agent", "value").iter_rows())
        win = res.filter(pl.col("unit") == u)["value"][0]
        w = x.filter((pl.col("t") >= a) & (pl.col("t") < b) & pl.col("b_agent").is_in(list(T))
                     & pl.col("a_agent").is_in(list(T)))
        w = w.with_columns(debate=pl.lit(u), phase=pl.lit(v),
                           team_b=pl.col("b_agent").replace_strict(T, return_dtype=pl.String),
                           team_a=pl.col("a_agent").replace_strict(T, return_dtype=pl.String),
                           winner=pl.lit(win))
        out.append(w)
    d = pl.concat(out).with_columns(
        R=(pl.col("team_b") != pl.col("team_a")).cast(pl.Int8),
        O=(pl.col("phase") != "post").cast(pl.Int8),
        wblock=pl.col("debate") + "_" + pl.col("phase"),
        b_won=(pl.col("team_b") == pl.col("winner")),
    )
    return d


def g26(rp: pl.DataFrame) -> pl.DataFrame:
    x = rp.filter(pl.col("goal_no") == 26)
    R = list(G26_RIVALS)
    return x.with_columns(
        R=(pl.col("b_agent").is_in(R) & pl.col("a_agent").is_in(R)).cast(pl.Int8),
        window=pl.when(pl.col("t") < G26_RESULT).then(pl.lit("open"))
        .when(pl.col("t") < G26_CONF).then(pl.lit("settled")).otherwise(pl.lit("confirmatory")),
    ).with_columns(O=(pl.col("window") == "open").cast(pl.Int8))


def g23_games() -> pl.DataFrame:
    cc = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "goal_no", "pt_date", "speaker_kind",
                                                             "agent"])
    cc = cc.filter((pl.col("goal_no") == 23) & (pl.col("speaker_kind").cast(pl.String) == "agent"))
    hm = holdout_mask(cc["pt_date"].to_list(), cc["goal_no"].to_list())
    assert not any(hm)
    tx = pl.read_parquet(SH / "chat_text.parquet", columns=["message_id", "text"]).join(
        cc.select("message_id"), on="message_id", how="semi")
    tx = tx.join(cc, on="message_id")
    rows = []
    for _mid, text, t, ag in tx.select("message_id", "text", "t", "agent").iter_rows():
        for gid in set(LICHESS.findall(text or "")):
            rows.append((hashlib.sha1(gid.encode()).hexdigest()[:12], int(ag), t))
    del tx
    links = pl.DataFrame(rows, schema=["game", "agent", "t"], orient="row")
    g = links.group_by("game").agg(pl.col("agent").unique().sort().alias("agents"), pl.col("t").min().alias("t0"),
                                   pl.col("t").max().alias("t1"), pl.len().alias("n_links"))
    g = g.filter(pl.col("agents").list.len() == 2).with_columns(
        a1=pl.col("agents").list.get(0).cast(pl.Int8), a2=pl.col("agents").list.get(1).cast(pl.Int8),
        t1=pl.col("t1") + dt.timedelta(minutes=10)).drop("agents")
    return g.sort("t0")


def g23(rp: pl.DataFrame, games: pl.DataFrame) -> pl.DataFrame:
    x = rp.filter(pl.col("goal_no") == 23)
    opp = {(min(a, b), max(a, b)) for a, b in games.select("a1", "a2").iter_rows()}
    wins: dict = {}
    for a, b, t0, t1 in games.select("a1", "a2", "t0", "t1").iter_rows():
        wins.setdefault((min(a, b), max(a, b)), []).append((t0, t1))
    R, O = [], []
    for ba, aa, t in x.select("b_agent", "a_agent", "t").iter_rows():
        k = (min(ba, aa), max(ba, aa))
        R.append(int(k in opp))
        O.append(int(any(t0 <= t < t1 for t0, t1 in wins.get(k, []))))
    # the "open" state of a non-opponent reply: any game open at t (for the heat term)
    allw = list(games.select("t0", "t1").iter_rows())
    anyo = [int(any(t0 <= t < t1 for t0, t1 in allw)) for t in x["t"].to_list()]
    return x.with_columns(R=pl.Series(R, dtype=pl.Int8), O=pl.Series(O, dtype=pl.Int8),
                          any_open=pl.Series(anyo, dtype=pl.Int8))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rp = load_replies()
    rp.write_parquet(OUT / "replies.parquet", compression="zstd")
    d12 = g12(rp)
    d12.write_parquet(OUT / "g12_rel.parquet", compression="zstd")
    d26 = g26(rp)
    d26.write_parquet(OUT / "g26_rel.parquet", compression="zstd")
    games = g23_games()
    games.write_parquet(OUT / "g23_games.parquet", compression="zstd")
    d23 = g23(rp, games)
    d23.write_parquet(OUT / "g23_rel.parquet", compression="zstd")
    counts = {
        "replies": rp.height, "periods": rp["goal_no"].n_unique(),
        "g12": d12.group_by("phase", "R").len().sort("phase", "R").rows(),
        "g26": d26.group_by("window", "R").len().sort("window", "R").rows(),
        "g23_games": games.height, "g23_opp_pairs": len({(a, b) for a, b in games.select("a1", "a2").iter_rows()}),
        "g23": d23.group_by("R", "O").len().sort("R", "O").rows(),
    }
    prov = {"built_by": "hypotheses/H64-conflict-scarce-prize/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["shared/reply_pairs", "shared/chat_core", "shared/chat_text (in memory, #23)",
                                   "shared/ground_truth_labels", "shared/period_units"]}],
            "params": {"p_reply_min": 0.5, "block_s": BLOCK_S, "g26_rivals": G26_RIVALS,
                       "g26_result": G26_RESULT.isoformat(), "g26_conf": G26_CONF.isoformat(),
                       "g23_game_close_pad_min": 10},
            "counts": counts, "built_at": dt.datetime.now(UTC).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1, default=str))
    print(json.dumps(counts, default=str))


if __name__ == "__main__":
    main()
