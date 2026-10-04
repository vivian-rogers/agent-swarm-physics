"""Shared per-message style features and marker-word counts for agent chat messages (numbers only, no text).
Moved here from H13 (hypotheses/H13-family-fields/scheme/build.py: text_features, STYLE, MARKERS), where they were
computed per unit and kept only as agent-day aggregates.

Rows: every chat message with speaker_kind == agent (human and automated messages are not featurized: no style
fingerprints of people). All days; `holdout` flags locked-holdout days.
Features (Float64, as H13; nch = characters, words = \\b\\w+\\b tokens, letters = [A-Za-z]):
  f_log_chars log(nch + 1)        f_lines log(newlines + 1)        f_bullet_share bullet / numbered lines per line
  f_headers markdown headers     f_bold '**' pairs                f_emoji emoji count
  f_excl, f_ques '!' / '?' per 100 chars                          f_urls 'http(s)://' count
  f_backticks '`' count          f_digit_share digits / (nch + 1)  f_upper_share uppercase / (letters + 1)
  f_at '@' count                 f_emdash '—' count
  f_fps, f_fpp, f_sp first-person singular / plural / second-person pronouns per word
  f_colon ':' per 100 chars      f_word_len letters per word       f_parens '()' per 100 chars
  words (Int32) word count
Markers m_<name> (Int16): case-insensitive regex counts of H13's pre-registered list (MARKERS below).
Key columns: message_id, msg (row index into chat_core sorted by t, the exposure key), agent, t, pt_date, goal_no, room,
holdout.

Output: data/processed/shared/text_features.parquet
Usage: uv run python infra/shared/text_features.py            (build)
       uv run python infra/shared/text_features.py --verify   (rebuild H13's agent-day aggregates and compare; read-only)
"""
from __future__ import annotations

import os

for _v, _n in (("POLARS_MAX_THREADS", "2"), ("OMP_NUM_THREADS", "2"), ("OPENBLAS_NUM_THREADS", "2"),
               ("MKL_NUM_THREADS", "2"), ("VECLIB_MAXIMUM_THREADS", "2")):
    os.environ.setdefault(_v, _n)

import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT, ROOT, write_provenance  # noqa: E402

APOS = "['’]"
MARKERS = {
    "genuinely": r"\bgenuinely\b", "honestly": r"\bhonestly\b", "appreciate": r"\bappreciat\w*",
    "youre_right": rf"\byou{APOS}?re (?:absolutely )?right\b", "wonderful": r"\bwonderful\b", "beautiful": r"\bbeautiful\w*",
    "fascinating": r"\bfascinat\w*", "i_think": r"\bi think\b",
    "per": r"\bper\b", "eta": r"\beta\b", "ack": r"\back\b", "fyi": r"\bfyi\b", "noted": r"\bnoted\b",
    "confirmed": r"\bconfirmed\b", "verified": r"\bverified\b", "blocked": r"\bblocked\b", "next_step": r"\bnext steps?\b",
    "will_do": r"\bwill do\b", "on_it": r"\bon it\b", "standing_by": r"\bstanding by\b",
    "delve": r"\bdelv\w*", "crucial": r"\bcrucial\w*", "robust": r"\brobust\w*", "comprehensive": r"\bcomprehensive\w*",
    "seamless": r"\bseamless\w*", "leverage": r"\bleverag\w*", "indeed": r"\bindeed\b", "i_will": r"\bi will\b",
    "i_am": r"\bi am\b",
    "absolutely": r"\babsolutely\b", "perfect": r"\bperfect\w*", "excellent": r"\bexcellent\b", "great": r"\bgreat\b",
    "amazing": r"\bamazing\b", "awesome": r"\bawesome\b", "thanks": r"\bthanks?\b|\bthank you\b",
    "sorry": r"\bsorry\b|\bapologi\w*",
}
STYLE = ["log_chars", "lines", "bullet_share", "headers", "bold", "emoji", "excl", "ques", "urls", "backticks",
         "digit_share", "upper_share", "at", "emdash", "fps", "fpp", "sp", "colon", "word_len", "parens"]


def text_features(txt: pl.DataFrame) -> pl.DataFrame:
    """H13's features for a frame with message_id, text (unchanged; words as Float64 here, cast by the builder)."""
    t = pl.col("text").fill_null("")
    nch = t.str.len_chars().cast(pl.Float64)
    nl = (t.str.count_matches("\n") + 1).cast(pl.Float64)
    letters = t.str.count_matches(r"[A-Za-z]").cast(pl.Float64)
    words = t.str.count_matches(r"\b\w+\b").cast(pl.Float64)
    per100 = lambda e: e.cast(pl.Float64) * 100.0 / (nch + 1.0)  # noqa: E731
    perw = lambda e: e.cast(pl.Float64) / (words + 1.0)  # noqa: E731
    feats = [
        (nch + 1).log().alias("f_log_chars"),
        nl.log().alias("f_lines"),
        (t.str.count_matches(r"(?m)^\s*(?:[-*•]|\d+[.)])\s").cast(pl.Float64) / nl).alias("f_bullet_share"),
        t.str.count_matches(r"(?m)^\s*#{1,6}\s").cast(pl.Float64).alias("f_headers"),
        (t.str.count_matches(r"\*\*").cast(pl.Float64) / 2).alias("f_bold"),
        t.str.count_matches(r"[\x{1F300}-\x{1FAFF}\x{2600}-\x{27BF}]").cast(pl.Float64).alias("f_emoji"),
        per100(t.str.count_matches("!")).alias("f_excl"),
        per100(t.str.count_matches(r"\?")).alias("f_ques"),
        t.str.count_matches(r"https?://").cast(pl.Float64).alias("f_urls"),
        t.str.count_matches("`").cast(pl.Float64).alias("f_backticks"),
        (t.str.count_matches(r"\d").cast(pl.Float64) / (nch + 1)).alias("f_digit_share"),
        (t.str.count_matches(r"[A-Z]").cast(pl.Float64) / (letters + 1)).alias("f_upper_share"),
        t.str.count_matches("@").cast(pl.Float64).alias("f_at"),
        t.str.count_matches("—").cast(pl.Float64).alias("f_emdash"),
        perw(t.str.count_matches(r"(?i)\b(?:i|me|my|mine|myself)\b")).alias("f_fps"),
        perw(t.str.count_matches(r"(?i)\b(?:we|us|our|ours|ourselves)\b")).alias("f_fpp"),
        perw(t.str.count_matches(r"(?i)\b(?:you|your|yours|yourself)\b")).alias("f_sp"),
        per100(t.str.count_matches(":")).alias("f_colon"),
        (letters / (words + 1)).alias("f_word_len"),
        per100(t.str.count_matches(r"[()]")).alias("f_parens"),
        words.alias("words"),
    ]
    marks = [t.str.count_matches("(?i)" + p).cast(pl.Int32).alias("m_" + k) for k, p in MARKERS.items()]
    return txt.select("message_id", *feats, *marks)


def main():
    t0 = time.time()
    core = (pl.read_parquet(OUT / "chat_core.parquet", columns=["message_id", "t", "pt_date", "goal_no", "room", "speaker_kind", "agent"])
            .with_row_index("msg").filter(pl.col("speaker_kind").cast(pl.String) == "agent").drop("speaker_kind"))
    cal = pl.read_parquet(OUT / "calendar.parquet", columns=["pt_date", "holdout"])
    parts = []
    for i in range(0, core.height, 40_000):  # chunks keep peak memory low (text never leaves this process)
        ids = core.slice(i, 40_000).select("message_id")
        txt = pl.read_parquet(OUT / "chat_text.parquet", columns=["message_id", "text"]).join(ids, on="message_id", how="semi")
        parts.append(text_features(txt))
        del txt
    F = pl.concat(parts).with_columns(pl.col("words").cast(pl.Int32), *[pl.col("m_" + k).cast(pl.Int16) for k in MARKERS])
    df = (core.join(F, on="message_id", how="left").join(cal, on="pt_date", how="left")
          .with_columns(pl.col("holdout").fill_null(False), pl.col("msg").cast(pl.UInt32))
          .select("message_id", "msg", "agent", "t", "pt_date", "goal_no", "room", "holdout",
                  *[f"f_{k}" for k in STYLE], "words", *[f"m_{k}" for k in MARKERS])
          .sort("msg"))
    df.write_parquet(OUT / "text_features.parquet", compression="zstd")
    print(f"text_features: {df.height} agent messages, {len(STYLE)} style features, {len(MARKERS)} markers; {time.time() - t0:.0f}s")
    write_provenance("text_features", ["chat_core", "chat_text (counts only)", "calendar"],
                     {"rows": "agent chat messages", "style": STYLE, "markers": MARKERS,
                      "source": "hypotheses/H13-family-fields/scheme/build.py text_features (unchanged)"})


def verify():
    """H13 keeps agent-day aggregates per unit (u<unit>_agent_day.parquet): n, words (sum), m_* (sums), f_* (means)
    over the unit's agent chat statements. Rebuild them from the shared table and compare."""
    h13 = ROOT / "data/processed/H13-family-fields"
    units = json.loads((h13 / "units.json").read_text())
    tf = pl.read_parquet(OUT / "text_features.parquet")
    st = (pl.read_parquet(OUT / "embeddings/statements.parquet").filter(pl.col("kind") == "chat")
          .join(pl.read_parquet(OUT / "embeddings/chat_index.parquet").with_row_index("src_row"), on="src_row")
          .select("message_id"))
    tf = tf.join(st, on="message_id", how="semi")
    worst, n_rows, n_units = 0.0, 0, 0
    exact_cols_ok = True
    for u, meta in units.items():
        f = h13 / meta["gdir"] / f"u{u}_agent_day.parquet"
        if not f.exists():
            continue
        a = pl.read_parquet(f)
        b = (tf.filter(pl.col("pt_date").is_in(meta["days"])).group_by("agent", "pt_date")
             .agg(pl.len().alias("n"), pl.col("words").sum(), *[pl.col("m_" + k).sum() for k in MARKERS],
                  *[pl.col(f"f_{k}").mean() for k in STYLE]))
        j = a.join(b, on=["agent", "pt_date"], how="full", suffix="_s", coalesce=True)
        assert j.height == a.height == b.height, (u, a.height, b.height, j.height)
        for c in ["n", "words"] + ["m_" + k for k in MARKERS]:
            exact_cols_ok &= bool((j[c].cast(pl.Int64) == j[c + "_s"].cast(pl.Int64)).all())
        for k in STYLE:
            x, y = j[f"f_{k}"].to_numpy(), j[f"f_{k}_s"].to_numpy()
            worst = max(worst, float(np.nanmax(np.abs(x - y) / np.maximum(np.abs(x), 1e-12))))
        n_rows += a.height
        n_units += 1
    res = {"units": n_units, "agent_days": n_rows, "counts_and_markers_exact": exact_cols_ok, "style_means_max_rel_diff": worst}
    print(res)
    return res


if __name__ == "__main__":
    if "--verify" in sys.argv:
        verify()
    else:
        main()
