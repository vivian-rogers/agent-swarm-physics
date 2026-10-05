"""H44 round 2 scheme. Builds data/processed/H44-erasure-reacquisition-thrash/r2/ from shared tables and the round-1
calls table (round-1 outputs are read, never changed).

  objects.parquet     one row per regime-III non-reserved call with >= 1 object: turn_id, `paths` (63-bit hashes of
                      file-path tokens parsed in memory from bash command text and typed text: last two path components,
                      URLs excluded), `arts` (artifact_mentions ids, action source, how in {url, output, bare}),
                      `arts_cwd` (the same plus how in {cwd, session_cwd})
  calls_long.parquet  computer-use calls of the non-reserved regime I/II periods with dense git (G30, G31, G33, G35):
                      category (round-1 classifier), write evidence, work commits, session position k = ctx_pos,
                      session id and length, in-loop flag (round-1 rule)
  label_sample/       R1 blind sample: written to the SCRATCH directory given by --scratch (command text, never inside
                      the repo); only the key without text (turn ids, strata, classifier category) goes to r2/

Usage: uv run python hypotheses/H44-erasure-reacquisition-thrash/scheme/build_r2.py [--only objects,long,sample]
       [--scratch DIR]
Command text is parsed and hashed in memory; no text is written under data/ or the repo.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import h44common as C  # noqa: E402

R2 = C.OUT / "r2"
LONG_GOALS = [30, 31, 33, 35]
TOK_SPLIT = re.compile(r"[\s;|&()<>`\"'=,{}\[\]]+")
EXT_RX = re.compile(r"^[~\w./@+-]*[\w@+-]\.[A-Za-z][A-Za-z0-9]{0,5}$")
SLASH_RX = re.compile(r"^[~\w./@+-]*[A-Za-z][~\w./@+-]*$")
SKIP_TOK = {"/dev/null", "dev/null", "/tmp", "tmp", "/", ".", "..", "~", "/usr/bin/env", "usr/bin/env"}


def _h(s: str) -> int:
    return int.from_bytes(hashlib.blake2b(s.encode(), digest_size=8).digest(), "little") >> 1


def path_tokens(text: str | None) -> list[int]:
    """Hashes of file-path-like tokens: a token with a file extension, or containing a slash with a letter. URLs, flags
    and numbers are skipped; the last two path components are kept (a/b/c/d.py -> c/d.py)."""
    if not text:
        return []
    out = set()
    for tok in TOK_SPLIT.split(text):
        if not tok or tok.startswith("-") or "://" in tok or tok.startswith("www.") or "$" in tok or "*" in tok:
            continue
        tok = tok.rstrip(":.").lstrip("./") if tok not in (".", "..") else tok
        if tok.endswith("/"):
            tok = tok.rstrip("/")
        if not tok or tok in SKIP_TOK or len(tok) > 200:
            continue
        has_ext = bool(EXT_RX.match(tok))
        has_slash = "/" in tok and bool(SLASH_RX.match(tok))
        if not (has_ext or has_slash):
            continue
        if re.fullmatch(r"[\d.]+", tok):
            continue
        parts = [p for p in tok.split("/") if p and p != "."]
        if not parts:
            continue
        key = "/".join(parts[-2:])
        if key in SKIP_TOK:
            continue
        out.add(_h(key))
    return sorted(out)


def _map_rows_to_calls(rows: pl.DataFrame, calls: pl.DataFrame) -> pl.DataFrame:
    keys = calls.select("turn_id", "agent", "t_first", "t_log").sort("t_first")
    return (rows.sort("t").join_asof(keys, left_on="t", right_on="t_first", by="agent", strategy="backward")
            .filter(pl.col("turn_id").is_not_null() & (pl.col("t") <= pl.col("t_log") + pl.duration(seconds=1))))


def build_objects():
    t0 = time.time()
    calls = pl.read_parquet(C.OUT / "calls.parquet", columns=["turn_id", "agent", "pt_date", "t_first", "t_log"])
    C.refuse_holdout(calls["pt_date"].unique().to_list(), "calls")
    tmin = calls["t_first"].min()
    to = (pl.read_parquet(C.BS / "turn_outcomes.parquet", columns=["t", "agent", "act", "cmd"])
          .filter((pl.col("t") >= tmin) & pl.col("cmd").is_not_null()).unique(["agent", "t"], keep="first"))
    to = to.with_columns(pl.Series("paths", [path_tokens(c) for c in to["cmd"].to_list()], dtype=pl.List(pl.Int64)))
    to = to.drop("cmd")
    m = _map_rows_to_calls(to, calls)
    P = (m.explode("paths").drop_nulls("paths").group_by("turn_id")
         .agg(pl.col("paths").unique().sort()))
    C.log("calls with path tokens", P.height, f"{time.time() - t0:.0f}s")
    am = pl.read_parquet(C.SH / "artifact_mentions.parquet", columns=["artifact", "t", "agent", "source", "how"])
    am = am.filter((pl.col("source") == "action") & (pl.col("t") >= tmin) & pl.col("agent").is_not_null())
    am = am.with_columns(pl.col("how").cast(pl.Utf8))
    ma = _map_rows_to_calls(am.select("t", "agent", "artifact", "how"), calls)
    A = (ma.filter(pl.col("how").is_in(["url", "output", "bare"])).group_by("turn_id")
         .agg(pl.col("artifact").unique().sort().alias("arts")))
    Acwd = ma.group_by("turn_id").agg(pl.col("artifact").unique().sort().alias("arts_cwd"))
    obj = P.join(A, on="turn_id", how="full", coalesce=True).join(Acwd, on="turn_id", how="full", coalesce=True)
    obj = obj.with_columns(pl.col("arts").cast(pl.List(pl.Int64)), pl.col("arts_cwd").cast(pl.List(pl.Int64)))
    R2.mkdir(parents=True, exist_ok=True)
    obj.write_parquet(R2 / "objects.parquet", compression="zstd")
    C.log("objects", obj.height, "paths", obj["paths"].is_not_null().sum(), "arts", obj["arts"].is_not_null().sum(),
          f"{time.time() - t0:.0f}s")


def long_days() -> pl.DataFrame:
    cal = pl.read_parquet(C.SH / "calendar.parquet")
    hm = C.holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    cal = cal.with_columns(pl.Series("hm", hm))
    return cal.filter(~pl.col("holdout") & ~pl.col("hm") & pl.col("goal_no").is_in(LONG_GOALS)
                      & (pl.col("n_agent_events") > 0)).select("pt_date", "goal_no")


def action_rows_between(t0, t1) -> pl.DataFrame:
    """Round-1 action-row categorization (scheme/build.py: action_rows) for an arbitrary time span."""
    a = (pl.read_parquet(C.SH / "actions.parquet", columns=["t", "agent", "action"]).with_row_index("row")
         .filter((pl.col("t") >= t0) & (pl.col("t") < t1)))
    bh = pl.read_parquet(C.SH / "actions_bash_head_fixed.parquet", columns=["row", "bash_head_fixed"])
    a = a.join(bh, on="row", how="left")
    to = (pl.read_parquet(C.BS / "turn_outcomes.parquet",
                          columns=["t", "agent", "failed", "commit_ok", "push_ok", "file_write", "api_write", "deploy",
                                   "cmd"])
          .filter((pl.col("t") >= t0) & (pl.col("t") < t1)).unique(["agent", "t"], keep="first"))
    a = a.join(to, on=["agent", "t"], how="left")
    act, cmd, head = a["action"].cast(pl.Utf8).to_list(), a["cmd"].to_list(), a["bash_head_fixed"].cast(pl.Utf8).to_list()
    wr = (a["commit_ok"].fill_null(False) | a["push_ok"].fill_null(False) | a["file_write"].fill_null(False)
          | a["api_write"].fill_null(False) | a["deploy"].fill_null(False)).to_list()
    cats, hashes = [], []
    for ac, cm, hd, w in zip(act, cmd, head, wr):
        if ac == "bash":
            cats.append("write" if w else C.classify_bash(cm if cm else hd))
            hashes.append(_h(cm) if cm else None)
        elif ac == "type":
            cats.append("gui_type"); hashes.append(None)
        elif ac in C.GUI_LOOK:
            cats.append("look"); hashes.append(None)
        elif ac in C.GUI_NAV:
            cats.append("gui"); hashes.append(None)
        else:
            cats.append(C.EVENT_CAT.get(ac, "other")); hashes.append(None)
    a = a.with_columns(pl.Series("cat", [C.CAT[c] for c in cats], dtype=pl.Int8), pl.Series("h", hashes, dtype=pl.Int64),
                       pl.Series("any_write", wr))
    return a.select("t", "agent", "cat", "h", "any_write", pl.col("failed").fill_null(False))


def build_long():
    t0 = time.time()
    days = long_days()
    umap = days.with_columns(pl.format("G{}", pl.col("goal_no").cast(pl.Utf8).str.zfill(2)).alias("period")).select(
        "pt_date", "period")
    t = (pl.read_parquet(C.SH / "context_ledger_turns.parquet",
                         columns=["turn_id", "agent", "pt_date", "goal_no", "regime", "holdout", "t_call", "t_first",
                                  "t_log", "kind", "talk", "ctx_mode", "ctx_pos", "reset_session"])
         .filter(~pl.col("holdout") & (pl.col("ctx_mode") == "cu") & pl.col("pt_date").is_in(days["pt_date"].implode()))
         .join(umap, on="pt_date", how="inner"))
    C.refuse_holdout(t["pt_date"].unique().to_list(), "long calls")
    a = action_rows_between(t["t_first"].min() - __import__("datetime").timedelta(minutes=5),
                            t["t_log"].max() + __import__("datetime").timedelta(minutes=5))
    m = _map_rows_to_calls(a, t)
    agg = m.sort("t").group_by("turn_id").agg(pl.col("cat").min(), pl.col("any_write").any(),
                                              pl.col("failed").sum().cast(pl.Int16).alias("n_fail"),
                                              pl.col("h").drop_nulls().first())
    t = t.join(agg, on="turn_id", how="left")
    kind_cat = (pl.when(pl.col("kind") == "talk").then(C.CAT["talk"])
                .when(pl.col("kind").is_in(["pause", "wait"])).then(C.CAT["idle"])
                .when(pl.col("kind") == "search").then(C.CAT["room_read"]).otherwise(C.CAT["other"]))
    t = t.with_columns(pl.coalesce("cat", kind_cat).cast(pl.Int8).alias("cat"), pl.col("any_write").fill_null(False),
                       pl.col("n_fail").fill_null(0))
    wc = (pl.read_parquet(C.SH / "work_commits.parquet",
                          columns=["t", "author_agent", "author_kind", "canonical", "imported", "automated", "holdout"])
          .filter(pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind") == "agent") & ~pl.col("automated")
                  & ~pl.col("holdout")).select("t", pl.col("author_agent").alias("agent")).drop_nulls().sort("t"))
    wm = wc.join_asof(t.select("turn_id", "agent", "t_log").sort("t_log"), left_on="t", right_on="t_log", by="agent",
                      strategy="forward", tolerance="10m")
    wcnt = wm.drop_nulls("turn_id").group_by("turn_id").agg(pl.len().cast(pl.Int16).alias("n_work"))
    t = t.join(wcnt, on="turn_id", how="left").with_columns(pl.col("n_work").fill_null(0))
    t = t.sort("agent", "t_first").with_columns(
        pl.col("reset_session").cast(pl.Int32).cum_sum().over("agent").alias("sess"),
        pl.int_range(pl.len()).over("agent", "pt_date").cast(pl.Int32).alias("seq"))
    t = t.with_columns(pl.len().over("agent", "sess").cast(pl.Int16).alias("sess_len"),
                       pl.col("ctx_pos").cast(pl.Int16).alias("k"))
    same = sum((pl.col("h") == pl.col("h").shift(o).over("agent", "pt_date")).fill_null(False).cast(pl.Int8)
               for o in range(1, 11))
    nf = sum((pl.col("n_fail").shift(o).over("agent", "pt_date").fill_null(0) > 0).cast(pl.Int8) for o in range(1, 10))
    t = t.with_columns(((same >= 2) | ((pl.col("n_fail") > 0) & (nf >= 2))).alias("in_loop"))
    t = t.select("turn_id", "agent", "pt_date", "goal_no", "period", "regime", "t_first", "t_log", "kind", "cat",
                 "any_write", "n_work", "n_fail", "in_loop", "k", "sess", "sess_len", "seq")
    R2.mkdir(parents=True, exist_ok=True)
    t.write_parquet(R2 / "calls_long.parquet", compression="zstd")
    C.log("long calls", t.height, t.group_by("period").len().sort("period").rows(), f"{time.time() - t0:.0f}s")


# ------------------------------------------------------------------------------------------------- R1 blind sample
BASH_Q = ["write", "notes_read", "local_read", "remote_read", "run", "monitor", "setup", "other", "gui_type"]
TOOL_Q = ["look", "gui", "room_read", "talk", "idle"]


def build_sample(scratch: Path, n_per: int = 15, seed: int = 20261005):
    """Stratified blind sample: per window (post = +1..+5 after a forced reset; mid = pos 11..30 of segments with no
    reset in pos 1..40 window), 15 calls per bash-derived category and GUI type, 15 over tool-name categories.
    Blind file (scratch, text): id + action list. Key (r2/, no text): id, turn_id, window, classifier category."""
    rng = np.random.default_rng(seed)
    calls = pl.read_parquet(C.OUT / "calls.parquet", columns=["turn_id", "agent", "pt_date", "t_first", "t_log", "cat",
                                                               "pos", "seg_kind", "seg_len", "period"])
    C.refuse_holdout(calls["pt_date"].unique().to_list(), "calls")
    post = calls.filter((pl.col("seg_kind") == "forced") & (pl.col("pos") <= 5)).with_columns(pl.lit("post").alias("win"))
    mid = calls.filter((pl.col("pos") >= 11) & (pl.col("pos") <= 30) & (pl.col("seg_len") >= 31)).with_columns(
        pl.lit("mid").alias("win"))
    pick = []
    for w in (post, mid):
        for c in BASH_Q:
            g = w.filter(pl.col("cat") == C.CAT[c])
            idx = rng.choice(g.height, size=min(n_per, g.height), replace=False)
            pick.append(g[idx.tolist()])
        g = w.filter(pl.col("cat").is_in([C.CAT[c] for c in TOOL_Q]))
        idx = rng.choice(g.height, size=n_per, replace=False)
        pick.append(g[idx.tolist()])
    S = pl.concat(pick)
    perm = rng.permutation(S.height)
    S = S[perm.tolist()].with_row_index("id", offset=1)
    # action rows of each sampled call (text in memory and in the scratch file only)
    a = (pl.read_parquet(C.SH / "actions.parquet", columns=["t", "agent", "action"]).with_row_index("row")
         .filter(pl.col("t") >= S["t_first"].min() - __import__("datetime").timedelta(minutes=1)))
    to = (pl.read_parquet(C.BS / "turn_outcomes.parquet", columns=["t", "agent", "cmd"])
          .unique(["agent", "t"], keep="first"))
    a = a.join(to, on=["agent", "t"], how="left")
    m = _map_rows_to_calls(a, S.select("turn_id", "agent", "t_first", "t_log"))
    m = m.join(S.select("turn_id", "id"), on="turn_id")
    ev = pl.read_parquet(C.SH / "context_ledger_turns.parquet", columns=["turn_id", "kind"]).join(
        S.select("turn_id", "id"), on="turn_id")
    lines = []
    rows = {i: g.sort("t") for (i,), g in m.group_by("id")}
    kinds = dict(zip(ev["id"].to_list(), ev["kind"].cast(pl.Utf8).to_list()))
    for i in S["id"].to_list():
        lines.append(f"### {i}  (ledger kind: {kinds.get(i)})")
        g = rows.get(i)
        if g is None or g.height == 0:
            lines.append("  (no action rows)")
            continue
        for ac, cm in list(zip(g["action"].cast(pl.Utf8).to_list(), g["cmd"].to_list()))[:6]:
            txt = (cm or "").replace("\n", " \\n ")
            lines.append(f"  - {ac}: {txt[:260]}")
        if g.height > 6:
            lines.append(f"  - (+{g.height - 6} more rows)")
    scratch.mkdir(parents=True, exist_ok=True)
    (scratch / "blind_sample.md").write_text("\n".join(lines))
    key = S.select("id", "turn_id", "win", "cat", "period")
    R2.mkdir(parents=True, exist_ok=True)
    key.write_parquet(R2 / "label_key.parquet")
    # population shares per window x category (for reweighting)
    pop = pl.concat([post, mid]).group_by("win", "cat").len()
    pop.write_parquet(R2 / "label_pop.parquet")
    C.log("blind sample", S.height, "->", scratch / "blind_sample.md")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="objects,long")
    ap.add_argument("--scratch", default=None)
    a = ap.parse_args()
    only = set(a.only.split(","))
    if "objects" in only:
        build_objects()
    if "long" in only:
        build_long()
    if "sample" in only:
        if not a.scratch:
            raise SystemExit("--scratch DIR required for the blind sample (text never goes into the repo)")
        build_sample(Path(a.scratch))
    prov = {"built_by": "hypotheses/H44-erasure-reacquisition-thrash/scheme/build_r2.py", "git_commit": C.git_commit(),
            "inputs": [{"source": "ai-village", "revision": C.REVISION,
                        "tables": ["H44 calls.parquet (round 1)", "turn_outcomes (cmd parsed in memory, never stored)",
                                   "artifact_mentions", "context_ledger_turns", "actions", "actions_bash_head_fixed",
                                   "work_commits", "calendar"]}],
            "params": {"long_goals": LONG_GOALS, "path_tokens": "extension or slash tokens, last two components, "
                                                                "63-bit blake2b hash", "arts": "how in url/output/bare",
                       "sample": "15 per window x bash category + GUI type, 15 tool-name; seed 20261005"},
            "built_at": __import__("datetime").datetime.now(C.UTC).isoformat(timespec="seconds")}
    R2.mkdir(parents=True, exist_ok=True)
    (R2 / "_provenance.json").write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    main()
