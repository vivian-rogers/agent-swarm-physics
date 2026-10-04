"""Shared computer-use turn errors and sessions (one pass over raw computer_use_turns), plus the actions sidecar with
the fixed bash head and error classes. Moved here from H38 (hypotheses/H38-platform-stalls/scheme/scan_turn_errors.py;
used by H38, H25, H26, H36); the categorization is unchanged.

`actions.error` is a boolean "stderr was non-empty": ~41% of those turns are benign git / curl output, only ~16% are
infrastructure failures. Use `error_class` (below) instead of the boolean.

Categories (first matching rule on the first 400 characters of the turn's `error` / `system` string):
  timeout     bash/tool did not return ("timed out")
  vm          VM / display / session plumbing (coordinates unavailable, xdotool / DISPLAY, "Session has not started",
              screenshot failures, X server)
  resource    too many open files, no space left, cannot allocate memory, killed (OOM)
  network     DNS / connection refused / reset / unreachable, TLS, HTTP 429 / 5xx gateway text
  git_info    benign git stderr ("From https://...", "To https://...", "Switched to branch", "Already on")
  progress    curl / wget progress meters
  tool_use    tool-argument misuse ("text is required for key", "is not accepted for")
  other       anything else (tracebacks, syntax errors, command not found, non-zero exits)
  none        no error / system string
Infrastructure categories: timeout, vm, resource, network.

Outputs (data/processed/shared/; no text anywhere):
  turn_errors.parquet   t, agent, session (int32 code), err_cat, sys_cat   [= H38's columns; rows with an error or
                        system string only] + pt_date, holdout
  sessions.parquet      computer-use sessions: session, agent, created, first_t, last_t, n_turns, asked_to_stop
                        [= H38's columns] + holdout (by the PT date of `created`)
  actions_bash_head_fixed.parquet   row-aligned with actions.parquet (one row per actions row, same order):
                        row, t (for an alignment check), bash_head_fixed (bash turns: first command word after leading
                        blank / '#' comment lines; scan_tables.bash_head), error_class (err_cat), system_class (sys_cat)
                        This is the sidecar for the actions.bash_head bug (null for ~87% of regime-III bash turns)
                        until actions.parquet is rebuilt by scan_tables.py; error_class replaces the raw boolean.

Usage: uv run python infra/shared/turn_errors.py            (one raw pass, single process)
       uv run python infra/shared/turn_errors.py --verify   (compare with H38's tables; check the sidecar)
Library: main(out_dir) writes turn_errors / sessions to another folder (for a shim in H38's scheme folder).
"""
from __future__ import annotations

import os

for _v, _n in (("POLARS_MAX_THREADS", "2"), ("OMP_NUM_THREADS", "2"), ("OPENBLAS_NUM_THREADS", "2"),
               ("MKL_NUM_THREADS", "2"), ("VECLIB_MAXIMUM_THREADS", "2")):
    os.environ.setdefault(_v, _n)

import gzip  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import orjson  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT, RAW, ROOT, write_provenance  # noqa: E402
from scan_tables import BASH_HEAD, bash_head  # noqa: E402

RULES = [
    ("timeout", re.compile(r"timed out|has not returned|Timeout(Error)?\b", re.I)),
    ("vm", re.compile(r"Unable to get coordinates|xdotool|DISPLAY=|cannot open display|Session has not started|"
                      r"screenshot|X server|Xlib|no display", re.I)),
    ("resource", re.compile(r"Too many open files|No space left|Cannot allocate memory|MemoryError|out of memory|"
                            r"\bKilled\b", re.I)),
    ("network", re.compile(r"Could not resolve host|Temporary failure in name resolution|Name or service not known|"
                           r"Connection (refused|reset|timed out|aborted)|Network is unreachable|SSL|TLS|"
                           r"\b(429|502|503|504)\b|Bad Gateway|Service Unavailable|Too Many Requests|rate.?limit", re.I)),
    ("git_info", re.compile(r"^(From|To) (https?://|git@)|^Switched to (a new )?branch|^Already on|^remote:|"
                            r"^Everything up-to-date|^branch '", re.I)),
    ("progress", re.compile(r"% Total\s+% Received|^\s*\d+\s+\d+[kKmM]?\s+\d+\s", re.I)),
    ("tool_use", re.compile(r"is required for|is not accepted for|not a valid|Invalid (action|key|coordinate)", re.I)),
]
CATS = ["none", "timeout", "vm", "resource", "network", "git_info", "progress", "tool_use", "other"]
INFRA = ["timeout", "vm", "resource", "network"]
SID = re.compile(rb'"session_id":"([0-9a-f\-]{36})"')
CAT_RE = re.compile(rb'"created_at":"([^"]+)"')
TS_FMT = "%Y-%m-%d %H:%M:%S%.f"


def cat_of(s: str | None) -> str:
    if not s:
        return "none"
    head = s[:400]
    for name, rx in RULES:
        if rx.search(head):
            return name
    return "other"


def _old_head(cmd):
    m = BASH_HEAD.match(cmd or "")
    return m.group(1).split("/")[-1][:24] if m else None


def _holdout(df: pl.DataFrame, tcol: str) -> pl.DataFrame:
    cal = pl.read_parquet(OUT / "calendar.parquet", columns=["pt_date", "holdout"])
    return (df.with_columns(pl.col(tcol).dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("pt_date"))
            .join(cal, on="pt_date", how="left").with_columns(pl.col("holdout").fill_null(False)))


def scan():
    """One pass: H38's error rows and session stats, plus every bash turn's fixed head (in memory)."""
    t0 = time.time()
    roster = pl.read_parquet(OUT / "roster.parquet").select("agent", "agent_id")
    acode = dict(zip(roster["agent_id"].to_list(), roster["agent"].to_list()))
    sess = {}
    with gzip.open(RAW / "computer_use_sessions.jsonl.gz", "rb") as f:
        for line in f:
            r = orjson.loads(line)
            sess[r["id"]] = [len(sess), acode.get(r["agent_id"]), r["created_at"], bool(r.get("has_been_asked_to_stop")),
                             None, None, 0]
    errs, bash = [], []
    n = 0
    with gzip.open(RAW / "computer_use_turns.jsonl.gz", "rb") as f:
        for line in f:
            n += 1
            m = SID.search(line)
            sid = m.group(1).decode() if m else None
            ts = CAT_RE.findall(line)
            t = ts[-1].decode() if ts else None  # the record's own created_at is the last one on the line
            s = sess.get(sid)
            if s is not None and t is not None:
                if s[4] is None or t < s[4]:
                    s[4] = t
                if s[5] is None or t > s[5]:
                    s[5] = t
                s[6] += 1
            need_err = not (b'"error":null' in line and b'"system":null' in line)
            need_cmd = b'"command"' in line
            if not (need_err or need_cmd):
                continue
            r = orjson.loads(line)
            if need_cmd:
                a = r.get("agent_action") or {}
                if "command" in a and not a.get("action"):
                    cmd = a.get("command")
                    bash.append((r["created_at"], s[1] if s else None, bash_head(cmd), _old_head(cmd)))
            if need_err:
                ec, sc = cat_of(r.get("error")), cat_of(r.get("system"))
                if not (ec == "none" and sc == "none"):
                    errs.append((r["created_at"], s[1] if s else None, s[0] if s else None, ec, sc))
            if n % 500000 == 0:
                print(f"{n:,} lines {time.time() - t0:.0f}s", flush=True)
    print(f"scan: {n:,} turns, {len(errs):,} error/system rows, {len(bash):,} bash turns, {time.time() - t0:.0f}s", flush=True)
    return sess, errs, bash, n


def tables(sess, errs):
    E = (pl.DataFrame(errs, schema=["t", "agent", "session", "err_cat", "sys_cat"], orient="row")
         .with_columns(pl.col("t").str.to_datetime(TS_FMT, time_zone="UTC").dt.cast_time_unit("us"),
                       pl.col("agent").cast(pl.Int8), pl.col("session").cast(pl.Int32),
                       pl.col("err_cat").cast(pl.Enum(CATS)), pl.col("sys_cat").cast(pl.Enum(CATS)))
         .sort("t", maintain_order=True))
    S = (pl.DataFrame([(v[0], v[1], v[2], v[4], v[5], v[6], v[3]) for v in sess.values()],
                      schema=["session", "agent", "created", "first_t", "last_t", "n_turns", "asked_to_stop"], orient="row")
         .with_columns(*[pl.col(c).str.to_datetime(TS_FMT, time_zone="UTC", strict=False).dt.cast_time_unit("us")
                         for c in ("created", "first_t", "last_t")],
                       pl.col("session").cast(pl.Int32), pl.col("agent").cast(pl.Int8), pl.col("n_turns").cast(pl.Int32))
         .sort("created", maintain_order=True))
    return E, S


def sidecar(E: pl.DataFrame, bash: list) -> tuple[pl.DataFrame, dict]:
    """Row-aligned with actions.parquet: fixed bash head and error classes, matched on (t, agent)."""
    acts = pl.read_parquet(OUT / "actions.parquet", columns=["t", "agent", "action", "bash_head", "error"]).with_row_index("row")
    B = (pl.DataFrame(bash, schema=["t", "agent", "bash_head_fixed", "old_head"], orient="row")
         .with_columns(pl.col("t").str.to_datetime(TS_FMT, time_zone="UTC").dt.cast_time_unit("us"), pl.col("agent").cast(pl.Int8)))
    chk = {"bash_turns_raw": B.height, "bash_rows_actions": int((acts["action"] == "bash").sum())}
    dupB = B.group_by("t", "agent").len().filter(pl.col("len") > 1).height
    B = B.unique(["t", "agent"], keep="first").with_columns(pl.lit(True).alias("_m"))
    ab = acts.filter(pl.col("action") == "bash").select("row", "t", "agent", "bash_head").join(B, on=["t", "agent"], how="left")
    chk.update({"bash_dup_keys": dupB, "bash_unmatched": int(ab["_m"].is_null().sum()),
                "old_head_agrees_with_actions": int(((ab["old_head"] == ab["bash_head"].cast(pl.String))
                                                     | (ab["old_head"].is_null() & ab["bash_head"].is_null())).fill_null(False).sum()),
                "bash_matched": int(ab["_m"].is_not_null().sum())})
    Eu = E.select("t", "agent", "err_cat", "sys_cat")
    dupE = Eu.group_by("t", "agent").len().filter(pl.col("len") > 1).height
    Eu = Eu.unique(["t", "agent"], keep="first")
    out = (acts.select("row", "t", "agent", "error")
           .join(ab.select("row", "bash_head_fixed"), on="row", how="left")
           .join(Eu, on=["t", "agent"], how="left")
           .with_columns(pl.col("err_cat").fill_null("none").alias("error_class"), pl.col("sys_cat").fill_null("none").alias("system_class"))
           .sort("row"))
    chk.update({"error_dup_keys": dupE,
                "error_bool_vs_class_disagree": int((out["error"] != (out["error_class"] != "none")).sum()),
                "bash_head_null_before": int(acts.filter(pl.col("action") == "bash")["bash_head"].is_null().sum()),
                "bash_head_null_after": int(out.filter(pl.col("row").is_in(ab["row"].implode()))["bash_head_fixed"].is_null().sum())})
    out = out.select(pl.col("row").cast(pl.UInt32), "t", pl.col("bash_head_fixed").cast(pl.Categorical),
                     pl.col("error_class").cast(pl.Enum(CATS)), pl.col("system_class").cast(pl.Enum(CATS)))
    return out, chk


def main(out_dir: Path = OUT, with_sidecar: bool | None = None):
    t0 = time.time()
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    with_sidecar = (out_dir == OUT) if with_sidecar is None else with_sidecar
    sess, errs, bash, n = scan()
    E, S = tables(sess, errs)
    _holdout(E, "t").write_parquet(out_dir / "turn_errors.parquet", compression="zstd")
    _holdout(S, "created").drop("pt_date").write_parquet(out_dir / "sessions.parquet", compression="zstd")
    chk = {}
    if with_sidecar:
        sc, chk = sidecar(E, bash)
        sc.write_parquet(out_dir / "actions_bash_head_fixed.parquet", compression="zstd")
        print("sidecar checks:", chk, flush=True)
    print(E.group_by("err_cat").len().sort("len", descending=True))
    if out_dir == OUT:
        write_provenance("turn_errors", ["computer_use_turns", "computer_use_sessions", "roster", "actions (sidecar alignment)",
                                         "calendar"],
                         {"categories": CATS, "infra_categories": INFRA, "rules": {k: v.pattern for k, v in RULES},
                          "text": "none kept", "sidecar": "actions_bash_head_fixed: bash_head after blank/# lines; error/system class",
                          "sidecar_checks": chk, "source": "hypotheses/H38-platform-stalls/scheme/scan_turn_errors.py (rules unchanged)"})
    print(f"{n:,} turns, {E.height:,} error/system rows, {S.height:,} sessions; {time.time() - t0:.0f}s")


def verify():
    h38 = ROOT / "data/processed/H38-platform-stalls"
    res = {}
    for name, key in (("turn_errors", ["t", "agent", "session", "err_cat", "sys_cat"]),
                      ("sessions", ["session", "agent", "created", "first_t", "last_t", "n_turns", "asked_to_stop"])):
        a = pl.read_parquet(h38 / f"{name}.parquet")
        b = pl.read_parquet(OUT / f"{name}.parquet").select(a.columns)
        res[name] = {"h38_rows": a.height, "shared_rows": b.height, "equal_sorted": a.sort(key).equals(b.sort(key))}
    sc = pl.read_parquet(OUT / "actions_bash_head_fixed.parquet")
    acts = pl.read_parquet(OUT / "actions.parquet", columns=["t", "action", "bash_head", "error"])
    a3 = acts.with_columns(sc["bash_head_fixed"], sc["error_class"], (pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date()
                                                                     >= pl.date(2026, 3, 24)).alias("r3"))
    b = a3.filter(pl.col("action") == "bash")
    res["sidecar"] = {"rows": sc.height, "aligned_t": bool((sc["t"] == acts["t"]).all()),
                      "regime_III_bash_head_coverage": {"before": float(b.filter("r3")["bash_head"].is_not_null().mean()),
                                                        "after": float(b.filter("r3")["bash_head_fixed"].is_not_null().mean())},
                      "regime_I_II_bash_head_coverage": {"before": float(b.filter(~pl.col("r3"))["bash_head"].is_not_null().mean()),
                                                         "after": float(b.filter(~pl.col("r3"))["bash_head_fixed"].is_not_null().mean())},
                      "old_nonnull_heads_unchanged": bool(b.filter(pl.col("bash_head").is_not_null()).select(
                          (pl.col("bash_head").cast(pl.String) == pl.col("bash_head_fixed").cast(pl.String)).all()).item()),
                      "error_true_by_class": dict(a3.filter(pl.col("error")).group_by(pl.col("error_class").cast(pl.String)).len().iter_rows())}
    for k, v in res.items():
        print(k, v)
    return res


if __name__ == "__main__":
    if "--verify" in sys.argv:
        verify()
    else:
        main()
