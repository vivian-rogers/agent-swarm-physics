"""H80 scheme: commit windows (automated vs agent) and command motifs. Hashes and numbers only, no text.

uv run python hypotheses/H80-assembly-vs-compression/scheme/build.py [--windows] [--motifs]
Writes data/processed/H80-assembly-vs-compression/{windows,motifs,motif_presence,agent_day_tokens}.parquet
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
from zoneinfo import ZoneInfo  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(HERE.parent / "analysis"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402
import h80lib as L  # noqa: E402

SH = ROOT / "data/processed/shared"
PTZ = ZoneInfo("America/Los_Angeles")
OUTD = ROOT / "data/processed/H80-assembly-vs-compression"
WIN = 16              # commits per window
CAP = 20              # windows per stream-day
PERIODS = [31, 38, 41, 51]
NGRAMS = range(4, 9)
MIN_COPIES = 20


def h64(*parts) -> int:
    return int.from_bytes(hashlib.blake2b("|".join(map(str, parts)).encode(), digest_size=8).digest(), "little",
                          signed=True)


def calendar() -> pl.DataFrame:
    c = pl.read_parquet(SH / "calendar.parquet").select("pt_date", "goal_no", "regime", "win_start", "win_end")
    mask = holdout_mask(c["pt_date"].to_list(), c["goal_no"].to_list())
    return c.with_columns(pl.Series("ho", mask))


# ============================================================================ commit windows
def build_windows(periods=None, allow_holdout: bool = False) -> pl.DataFrame:
    """allow_holdout=True only from analysis/confirm.py behind its guard."""
    periods = periods or PERIODS
    cal = calendar()
    wc = pl.read_parquet(SH / "work_commits.parquet", columns=[
        "repo", "hash", "t", "pt_date", "goal_no", "holdout", "author_agent", "author_kind", "imported", "canonical",
        "n_files", "msg_len", "insertions", "deletions", "is_merge", "pages_branch", "deploy_msg", "bulk",
        "automated", "in_window"])
    wc = wc.filter((pl.col("author_kind") == "agent") & ~pl.col("imported") & pl.col("goal_no").is_in(periods)
                   & (pl.lit(allow_holdout) | ~pl.col("holdout")))
    wc = wc.join(cal.select("pt_date", "ho"), on="pt_date", how="left")
    # post-period days (no calendar row): keep for goal 51 as unit "G51post" if outside the holdout mask (A1)
    last51 = cal.filter(pl.col("goal_no") == 51)["pt_date"].max()
    post = (pl.col("goal_no") == 51) & (pl.col("pt_date") > last51) & pl.col("ho").is_null()
    pmask = holdout_mask(wc["pt_date"].to_list(), wc["goal_no"].to_list())
    wc = wc.with_columns(pl.Series("hm", pmask), post.alias("post"))
    if allow_holdout:
        wc = wc.filter(pl.col("ho").is_not_null() | pl.col("post"))
    else:
        wc = wc.filter(~pl.col("hm") & (~pl.col("ho").fill_null(True) | pl.col("post")))
    # one row per hash: canonical first (DQ4: non-canonical rows include fork copies of parent commits)
    wc = wc.sort("canonical", descending=True).unique("hash", keep="first", maintain_order=True)
    wc = wc.with_columns(pl.col("repo").cast(pl.Utf8))
    wc = wc.with_columns(pl.when(pl.col("post")).then(pl.lit("G51post")).otherwise(
        pl.lit("G") + pl.col("goal_no").cast(pl.Utf8)).alias("unit"))
    wc = wc.sort("goal_no", "repo", "author_agent", "t")
    rows = []
    byte_list = []
    rng = np.random.default_rng(20261004)
    for (g, unit, repo, a), d in wc.group_by(["goal_no", "unit", "repo", "author_agent"], maintain_order=True):
        n = d.height // WIN
        if n == 0:
            continue
        tok = [h64(*r) for r in d.select("n_files", "msg_len", "insertions", "deletions", "is_merge", "pages_branch",
                                         "deploy_msg", "bulk").iter_rows()]
        ts = d["t"].to_list()
        auto = d["automated"].to_numpy()
        inw = d["in_window"].fill_null(False).to_numpy()
        days = d["pt_date"].to_list()
        idx = list(range(n))
        # cap per stream-day (day of the window's first commit)
        byday: dict = {}
        for i in idx:
            byday.setdefault(days[i * WIN], []).append(i)
        keep = []
        for dd, ii in byday.items():
            keep += list(rng.choice(ii, CAP, replace=False)) if len(ii) > CAP else ii
        for i in sorted(keep):
            s = slice(i * WIN, (i + 1) * WIN)
            seq = tok[s]
            tt = ts[s]
            gaps = np.array([(b - a_).total_seconds() for a_, b in zip(tt[:-1], tt[1:])])
            lg = np.log10(np.maximum(gaps, 0) + 1)
            med = np.median(gaps)
            pt_hours = np.array([x.astimezone(PTZ).hour + x.minute / 60 for x in tt])
            ang = 2 * np.pi * pt_hours / 24
            f = L.features(seq)
            lab = auto[s].mean()
            rows.append({
                "goal_no": int(g), "unit": unit, "stream": h64(repo, a), "repo_h": h64(repo), "author_agent": int(a),
                "day": days[i * WIN], "t0": tt[0], "y": int(lab > 0.5), "purity": float(max(lab, 1 - lab)),
                "lg_med": float(np.median(lg)), "lg_iqr": float(np.subtract(*np.percentile(lg, [75, 25]))),
                "lg_min": float(lg.min()), "lg_max": float(lg.max()),
                "periodic": float(np.mean(np.abs(gaps - med) <= 2)),
                "sec0": float(np.mean([x.second < 5 for x in tt])),
                "hour_sin": float(np.sin(ang).mean()), "hour_cos": float(np.cos(ang).mean()),
                "in_window": float(inw[s].mean()),
                **{k: float(v) for k, v in f.items()}})
            byte_list.append(L.to_bytes(seq))
    df = pl.DataFrame(rows)
    os.environ.setdefault("H80_TMP", str(OUTD))
    df = df.with_columns(pl.Series("zstd", np.array(L.zstd_sizes(byte_list), float) / WIN))
    return df


# ============================================================================ command motifs
def command_tokens(allow_holdout: bool = False) -> pl.DataFrame:
    """Regime-III, non-holdout actions with session ids and hashed tokens (action type or bash head)."""
    cal = calendar()
    a = pl.scan_parquet(SH / "actions.parquet").select("t", "agent", "action").with_row_index("row").collect()
    b = pl.read_parquet(SH / "actions_bash_head_fixed.parquet", columns=["row", "bash_head_fixed"])
    a = a.join(b.with_columns(pl.col("row").cast(pl.UInt32)), on="row", how="left")
    a = a.with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.strftime("%Y-%m-%d").alias("pt_date"))
    a = a.join(cal.select("pt_date", "goal_no", "regime", "ho"), on="pt_date", how="left")
    a = a.filter((pl.col("regime") == "III") & (pl.lit(allow_holdout) | ~pl.col("ho").fill_null(True))
                 & pl.col("agent").is_not_null())
    tok = pl.when(pl.col("action") == "bash").then(
        pl.lit("b:") + pl.col("bash_head_fixed").cast(pl.Utf8).fill_null("?")).otherwise(pl.col("action").cast(pl.Utf8))
    a = a.with_columns(tok.alias("tok_s"))
    vocab = a.select("tok_s").unique().sort("tok_s").with_row_index("tok")
    a = a.join(vocab, on="tok_s").drop("tok_s", "bash_head_fixed", "action")
    ses = pl.read_parquet(SH / "sessions.parquet", columns=["session", "agent", "first_t", "last_t"]).sort("first_t")
    a = a.sort("t").join_asof(ses.with_columns(pl.col("agent").cast(a.schema["agent"])), left_on="t",
                              right_on="first_t", by="agent", strategy="backward")
    a = a.filter(pl.col("session").is_not_null() & (pl.col("t") <= pl.col("last_t") + pl.duration(minutes=5)))
    return a.select("t", "agent", "session", "pt_date", "goal_no", pl.col("tok").cast(pl.Int32)).sort("session", "t")


def build_motifs(tokens: pl.DataFrame, goal: int = 51):
    roster = pl.read_parquet(SH / "roster.parquet").select("agent", "lab", "joined")
    t = tokens.filter(pl.col("goal_no") == goal).sort("session", "t").with_row_index("i")
    tok_arr = t["tok"].to_numpy()
    parts = []
    P = 1_000_003
    for n in NGRAMS:
        h = pl.lit(0, pl.Int64)
        ok = pl.lit(True)
        for j in range(n):
            h = h * P + pl.col("tok").shift(-j).over("session").cast(pl.Int64)
            ok = ok & pl.col("tok").shift(-j).over("session").is_not_null()
        parts.append(t.with_columns(h.alias("m"), ok.alias("ok"), pl.lit(n, pl.Int8).alias("n"))
                     .filter(pl.col("ok")).select("n", "m", "i", "session", "agent", "pt_date"))
    occ = pl.concat(parts)
    stats = occ.group_by("n", "m").agg(pl.col("session").n_unique().alias("copies"),
                                       pl.col("agent").n_unique().alias("n_agents"), pl.len().alias("occ"),
                                       pl.col("i").first().alias("i0"))
    keep = stats.filter(pl.col("copies") >= MIN_COPIES)
    rows = []
    for n, m, i0 in keep.select("n", "m", "i0").iter_rows():
        seq = tuple(int(x) for x in tok_arr[i0:i0 + n])
        rows.append((int(n), int(m), L.exact_assembly(seq), len(set(seq)), L.lz78(seq)))
    a_df = pl.DataFrame(rows, schema={"n": pl.Int8, "m": pl.Int64, "a": pl.Int16, "n_distinct": pl.Int16,
                                      "lz78": pl.Int16}, orient="row")
    keep = keep.join(a_df, on=["n", "m"], how="left")
    # presence by agent-day and labs
    pres = occ.join(keep.select("n", "m"), on=["n", "m"]).select("n", "m", "agent", "pt_date").unique()
    labs = pres.join(roster.with_columns(pl.col("agent").cast(pres.schema["agent"])), on="agent").group_by(
        "n", "m").agg(pl.col("lab").n_unique().alias("n_labs"))
    keep = keep.join(labs, on=["n", "m"], how="left").with_columns(pl.lit(goal, pl.Int8).alias("goal_no"))
    return keep, pres.with_columns(pl.lit(goal, pl.Int8).alias("goal_no"))


def agent_day_tokens(tokens: pl.DataFrame, goal: int = 51) -> pl.DataFrame:
    return tokens.filter(pl.col("goal_no") == goal).sort("t").group_by("agent", "pt_date", maintain_order=True).agg(
        pl.col("tok"), pl.col("session").n_unique().alias("n_sessions"))


def provenance(params):
    (OUTD / "_provenance.json").write_text(json.dumps({
        "built_by": "hypotheses/H80-assembly-vs-compression/scheme/build.py", "git_commit": git_commit(),
        "inputs": [{"source": "ai-village", "revision": REVISION,
                    "tables": ["work_commits (DQ4)", "actions", "actions_bash_head_fixed", "sessions", "calendar",
                               "roster"]}],
        "params": params, "built_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "note": "hashes and numeric features only; no agent text, commit messages or command text"}, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--windows", action="store_true")
    ap.add_argument("--motifs", action="store_true")
    a = ap.parse_args()
    OUTD.mkdir(parents=True, exist_ok=True)
    both = not (a.windows or a.motifs)
    if a.windows or both:
        w = build_windows()
        w.write_parquet(OUTD / "windows.parquet", compression="zstd")
        print("windows", w.group_by("goal_no", "y").len().sort("goal_no", "y"))
    if a.motifs or both:
        tk = command_tokens()
        tk.select("agent", "session", "pt_date", "goal_no", "t", "tok").write_parquet(OUTD / "command_tokens.parquet",
                                                                                   compression="zstd")
        k, p = build_motifs(tk, 51)
        k.write_parquet(OUTD / "motifs.parquet", compression="zstd")
        p.write_parquet(OUTD / "motif_presence.parquet", compression="zstd")
        agent_day_tokens(tk, 51).write_parquet(OUTD / "agent_day_tokens.parquet", compression="zstd")
        print("motifs", k.height, "presence rows", p.height)
    provenance({"window": WIN, "cap_per_stream_day": CAP, "periods": PERIODS, "ngrams": list(NGRAMS),
                "min_copies": MIN_COPIES, "token_commit": "hash(n_files,msg_len,ins,del,merge,pages,deploy,bulk)",
                "token_command": "hash(action type or bash head)"})


if __name__ == "__main__":
    main()
