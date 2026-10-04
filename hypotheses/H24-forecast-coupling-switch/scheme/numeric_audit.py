"""H24 hand-verified numeric anchor units (amendment A2, 2026-10-03, after the first real-data run).

Each unit points to the rows of numeric.parquet (prereg extractor rows, any attribution) that hold the agent's
first and last *unconditional, self-stated* forecast for an anchor question. The source sentences were read
by hand. Pointers are UTC timestamps (ddHHMMSS, December 2025); no forecast values are stored in this
file (derived numbers stay in data/).

Why the extractors were not enough (reasons, paraphrased):
  - thresholds (a bound such as "doom under some level"), complements (the probability of avoiding a
    catastrophe), worked examples of a method, and scenario-conditional values (a probability given one
    scenario) were read as forecasts;
  - another agent's numbers were attributed to the speaker when the agent was named by a short name
    (a possessive short name followed by that agent's numbers);
  - agents state their *own* numbers in their own comparison matrices, next to a teammate's,
    which the rule labels 'other'.
Excluded units: Gemini 2.5 Pro and GPT-5 (no self-stated anchor values), Opus SI-2050 (only a different
question, "SI within 10 years of AGI").

Output: data/processed/H24-forecast-coupling-switch/G21/numeric_handverified.parquet
"""
from __future__ import annotations

import sys
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h24lib import H24  # noqa: E402

# (speaker, question, first ddHHMMSS[:attribution], last ddHHMMSS[:attribution], note)
UNITS = [
    (16, "AGI2035", "01180933", "05182534", "pre-switch draft doc -> final doc"),
    (12, "AGI2035", "01182428", "04195548", "pre-switch chat (own median, first person) -> tracker values"),
    (14, "AGI2035", "01200127", "02192523", "explicit own value set in own matrix -> own framework mixture"),
    (13, "AGI2035", "01192838", "05180913", "own value in own divergence matrix -> tracker submission"),
    (0, "AGI2035", "01195846", "05180607", "own forecast data sent to team -> tracker submission"),
    (15, "AGI2035", "04200312", "05183411", "first stated on 12-04 -> final"),
    (17, "AGI2035", "04183448", "04194541", "late joiner, first doc -> final doc"),
    (12, "SI2050", "01181018", "04195548", "pre-switch draft doc -> tracker values"),
    (14, "SI2050", "01213231", "02203506", "own anchor points -> own update"),
    (13, "SI2050", "01192838", "05180913", "own value in own divergence matrix -> tracker submission"),
    (0, "SI2050", "01195846", "05180607", "own forecast data sent to team -> tracker submission"),
    (15, "SI2050", "04200312", "05183411", "first stated on 12-04 -> final"),
    (17, "SI2050", "04183448", "04191108", "late joiner, first doc -> CSV values"),
    (16, "DOOM2100", "01180933", "05181624", "pre-switch draft doc -> final doc"),
    (14, "DOOM2100", "01213231", "02202528", "own anchor points -> own update"),
    (13, "DOOM2100", "02205913:self", "05180913", "own 'baseline' on 12-02 -> tracker submission"),
    (0, "DOOM2100", "01200114", "05180607", "own x-risk in reply to a teammate -> tracker submission"),
    (12, "DOOM2100", "04195548", "05182442", "first stated on 12-04 -> final"),
    (15, "DOOM2100", "04200312", "05183411", "first stated on 12-04 -> final"),
    (17, "DOOM2100", "04183448", "04184510", "late joiner, first doc -> later doc"),
]


def build():
    G = H24 / "G21"
    N = pl.read_parquet(G / "numeric.parquet").filter(pl.col("extractor") == "prereg") \
          .with_columns(pl.col("t").dt.strftime("%d%H%M%S").alias("ts"))
    rows = []
    for sp, q, f, l, note in UNITS:
        def pick(ptr):
            ts, _, attr = ptr.partition(":")
            s = N.filter(pl.col("speaker") == sp, pl.col("question") == q, pl.col("ts") == ts)
            if attr:
                s = s.filter(pl.col("attribution") == attr)
            assert s.height >= 1 and s["value"].n_unique() == 1, (sp, q, ptr)
            return s.row(0, named=True)
        a, b = pick(f), pick(l)
        rows.append({"speaker": sp, "question": q, "first": a["value"], "last": b["value"], "t_first": a["t"], "t_last": b["t"],
                     "seg_first": a["seg"], "note": note})
    df = pl.DataFrame(rows)
    df.write_parquet(G / "numeric_handverified.parquet")
    return df


if __name__ == "__main__":
    print(build().select("speaker", "question", "t_first", "t_last", "seg_first"))
