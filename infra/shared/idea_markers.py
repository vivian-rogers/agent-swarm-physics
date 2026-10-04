"""Idea markers (H34 marker rule, pre-registered 2026-10-04 01:30 UTC), moved to infra/shared for reuse (H61, H62 and
their confirm scripts). The rule functions are a verbatim copy of hypotheses/H34-idea-cascades/scheme/markers.py
(H34's file is untouched); `--verify` checks that this copy reproduces H34's marker table exactly on non-holdout rows.

Classes: U artifact (repo / site / file, from `artifact_mentions`); D number with >= 3 significant digits; N name or
coinage (capitalised runs, code identifiers, hex ids, hashtags, short quoted phrases); W rare word. Markers containing
a roster-name token are dropped. Only hashes leave this module: marker_id(cls, norm) -> signed 64-bit int.

  uses_for_rows(rows, allow_holdout=False)  marker uses (msg, marker, cls) for chat_core rows; text in memory only.
                                            Held-out rows raise unless allow_holdout (confirm scripts only).
  uv run python infra/shared/idea_markers.py --verify
"""
from __future__ import annotations

import hashlib
import re
from functools import lru_cache
from pathlib import Path

DICT_PATH = Path("/usr/share/dict/words")
DICT_SHA1 = "6d17bc9e8cbc3d7514e2e003aeeaf8a4c72fbe0d"
CLS = {"U": 0, "D": 1, "N": 2, "W": 3}
CLS_NAME = {v: k for k, v in CLS.items()}

# Agent, model-family and lab words: markers containing one of these are "who is present", a roster field.
FAMILY = {"claude", "sonnet", "opus", "haiku", "gpt", "gemini", "grok", "deepseek", "kimi", "glm", "fable", "muse",
          "o1", "o3", "o4", "o4-mini", "sol", "terra", "luna", "astra", "anthropic", "openai", "google", "deepmind",
          "xai", "moonshot", "zhipu", "chatgpt", "llama", "qwen", "mistral"}
LEAD_STOP = set("""the a an this that these those our my your their its his her i we you it he she they and or but if
in on at for to of with by from as is are was were be been so hi hello hey thanks thank great good yes no ok okay when
while after before now then also just here there what why how who where which let please dear re update note all any
each every both some new next final done today tomorrow yesterday per via day week session quick big key important
monday tuesday wednesday thursday friday saturday sunday january february march april may june july august september
october november december""".split())

URL_RE = re.compile(r"https?://[^\s<>()\"'`\]]+|www\.[^\s<>()\"'`\]]+")
DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}(?:[T ][\d:.]+Z?)?\b|\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b")
TIME_RE = re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?(?:\s?[AaPp][Mm])?\b")
VERSION_RE = re.compile(r"\b[vV]?\d+\.\d+\.\d+(?:\.\d+)*\b")
NUM_RE = re.compile(r"(?<![\w.#/@:_\-])([$€£]?)(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?(%?)(?![A-Za-z\d_]|[.,]\d)")
CAMEL_RE = re.compile(r"(?<![\w#-])[A-Za-z][a-z0-9]+[A-Z][A-Za-z0-9]*(?![\w-])")
SNAKE_RE = re.compile(r"(?<![\w-])[A-Za-z0-9]+(?:_[A-Za-z0-9]+)+(?:\.[a-z]{1,5})?(?![\w-])")
KEBAB_RE = re.compile(r"(?<![\w-])[a-z0-9]+(?:-[a-z0-9]+){1,}(?:\.[a-z]{1,5})?(?![\w-])")
HEX_RE = re.compile(r"(?<![\w-])[0-9a-f]{7,40}(?![\w-])")
HASHTAG_RE = re.compile(r"(?<![\w&])#([A-Za-z][A-Za-z0-9_]{2,})")
QUOTE_RE = re.compile(r"[\"“]([^\"“”\n]{3,60})[\"”]")
CLAUSE_SPLIT = re.compile(r"(?:[.!?](?=\s|$))|[:;,()\[\]{}\"“”*\n|—–>#`]")
WORD_RE = re.compile(r"[^\W\d_]+")
STRIP = "\"'“”‘’()[]{}*_~`<>"
SUFFIXES = ("ments", "ment", "ness", "ing", "ers", "est", "er", "es", "ed", "ly", "s", "d")


@lru_cache(maxsize=1)
def dictionary() -> frozenset:
    words = DICT_PATH.read_text(encoding="utf-8", errors="ignore").split()
    return frozenset(w.lower() for w in words)


def marker_id(cls: str, norm: str) -> int:
    return int.from_bytes(hashlib.sha1(f"{cls}:{norm}".encode()).digest()[:8], "little", signed=True)


def _has_family(norm: str, roster_full: frozenset) -> bool:
    toks = set(re.split(r"[\s\-_.]+", norm))
    if toks & FAMILY:
        return True
    return any(r in norm for r in roster_full)


def _sig_digits(intpart: str, dec: str) -> int:
    i = intpart.replace(",", "").lstrip("0")
    d = dec[1:].rstrip("0") if dec else ""
    if not i:  # 0.00x: leading zeros of the decimal part are not significant
        return len(d.lstrip("0"))
    return len(i) + len(d)


def numbers(text: str) -> set[str]:
    out = set()
    for m in NUM_RE.finditer(text):
        unit, ip, dec, pct = m.group(1), m.group(2), m.group(3) or "", m.group(4)
        if _sig_digits(ip, dec) < 3:
            continue
        iv = ip.replace(",", "")
        if not unit and not pct and not dec and "," not in ip and len(iv) == 4 and 1900 <= int(iv) <= 2099:
            continue  # bare year
        d = dec.rstrip("0").rstrip(".") if dec else ""
        out.add(f"{unit}{iv.lstrip('0') or '0'}{d}{pct}")
    return out


def _clean_token(tok: str) -> str:
    tok = tok.strip(STRIP)
    for poss in ("'s", "’s"):
        if tok.endswith(poss):
            tok = tok[: -len(poss)]
    return tok.strip(STRIP + ".,;:!?")


def _is_cap(tok: str) -> bool:
    return bool(tok) and tok[0].isalpha() and tok[0].isupper()


def cap_runs(text: str) -> set[str]:
    out = set()
    for clause in CLAUSE_SPLIT.split(text):
        toks = [_clean_token(t) for t in clause.split()]
        run: list[str] = []
        for t in toks + [""]:
            if _is_cap(t):
                run.append(t)
                continue
            while run and run[0].lower() in LEAD_STOP:
                run.pop(0)
            if len(run) >= 2:
                out.add(" ".join(run[:5]).lower())
            run = []
    return out


def identifiers(text: str) -> set[str]:
    out = set()
    for m in CAMEL_RE.finditer(text):
        if len(m.group(0)) >= 6:
            out.add(m.group(0).lower())
    for m in SNAKE_RE.finditer(text):
        s = m.group(0)
        if len(s) >= 6 and re.search(r"[A-Za-z]", s):
            out.add(s.lower())
    for m in KEBAB_RE.finditer(text):
        s = m.group(0)
        if len(s) >= 6 and re.search(r"[a-z]", s) and (s.count("-") >= 2 or re.search(r"\d", s)):
            out.add(s)
    for m in HEX_RE.finditer(text):
        s = m.group(0)
        if re.search(r"\d", s) and re.search(r"[a-f]", s):
            out.add(s)
    for m in HASHTAG_RE.finditer(text):
        out.add("#" + m.group(1).lower())
    return out


def quoted(text: str) -> set[str]:
    out = set()
    for m in QUOTE_RE.finditer(text):
        words = WORD_RE.findall(m.group(1).lower())
        if 2 <= len(words) <= 6:
            out.add(" ".join(words))
    return out


def _known_inflection(w: str, D) -> bool:
    """True if w is a regular inflection of a dictionary word (Webster's 2nd lists few inflected forms)."""
    cands = set()
    for suf in SUFFIXES:
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            stem = w[: -len(suf)]
            cands |= {stem, stem + "e"}
            if len(stem) >= 4 and stem[-1] == stem[-2]:
                cands.add(stem[:-1])  # stopped -> stop
    for suf in ("ies", "ied", "ier", "iest", "ily"):
        if w.endswith(suf):
            cands.add(w[: -len(suf)] + "y")
    return any(c in D for c in cands)


def rare_words(text: str) -> set[str]:
    D = dictionary()
    out = set()
    for w in WORD_RE.findall(text):
        if len(w) < 6 or not w.islower() or not w.isascii():
            continue
        if w in D:
            continue
        if _known_inflection(w, D):
            continue
        out.add(w)
    return out


def extract(text: str | None, roster_full: frozenset) -> list[tuple[str, str]]:
    """All D / N / W markers in one message (U comes from artifact_mentions)."""
    if not text:
        return []
    t = URL_RE.sub(" ", text)
    tn = VERSION_RE.sub(" ", TIME_RE.sub(" ", DATE_RE.sub(" ", t)))
    out: list[tuple[str, str]] = [("D", x) for x in numbers(tn)]
    for x in cap_runs(t) | identifiers(t) | quoted(t):
        if not _has_family(x, roster_full):
            out.append(("N", x))
    for x in rare_words(t):
        if x not in FAMILY and not _has_family(x, roster_full):
            out.append(("W", x))
    return out


def roster_full_names(names) -> frozenset:
    return frozenset(n.lower() for n in names if len(n) >= 4)



# ------------------------------------------------------------------------------------------- shared extraction
def uses_for_rows(rows, allow_holdout: bool = False):
    """Marker uses for chat_core rows (same rule as H34's build_markers: D/N/W from text, U from artifact_mentions)."""
    import sys
    import numpy as np
    import polars as pl
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from common import OUT as SH, holdout_mask
    rows = np.asarray(rows, dtype=np.int64)
    chat = (pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "pt_date", "goal_no"]).with_row_index("msg")
            .filter(pl.col("msg").is_in(rows)))
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "holdout"])
    c2 = chat.join(cal, on="pt_date", how="left")
    held = np.array(holdout_mask(c2["pt_date"].to_list(), c2["goal_no"].to_list())) | c2["holdout"].fill_null(False).to_numpy()
    if held.any() and not allow_holdout:
        raise PermissionError("held-out rows requested without allow_holdout")
    ids = chat.select("message_id", "msg")
    txt = (pl.scan_parquet(SH / "chat_text.parquet").select("message_id", "text")
           .join(ids.lazy(), on="message_id", how="inner").select("msg", "text").collect().sort("msg"))
    ros = roster_full_names(pl.read_parquet(SH / "roster.parquet")["name"].to_list())
    dictionary()
    msg, mk, cl = [], [], []
    for r, t in zip(txt["msg"].to_list(), txt["text"].to_list()):
        for c, x in extract(t, ros):
            msg.append(r); mk.append(marker_id(c, x)); cl.append(CLS[c])
    del txt
    dnw = pl.DataFrame({"msg": np.array(msg, np.uint32), "marker": np.array(mk, np.int64), "cls": np.array(cl, np.uint8)})
    art = pl.read_parquet(SH / "artifacts.parquet", columns=["artifact", "kind"])
    am = (pl.read_parquet(SH / "artifact_mentions.parquet", columns=["artifact", "source", "how", "message_id"])
          .filter((pl.col("source") == "chat") & pl.col("how").cast(pl.Utf8).is_in(["url", "bare"]))
          .join(art, on="artifact").filter(pl.col("kind").cast(pl.Utf8).is_in(["repo", "site", "file"]))
          .join(ids, on="message_id", how="inner"))
    u = am.select(pl.col("msg").cast(pl.UInt32), pl.col("artifact").map_elements(lambda a: marker_id("U", str(a)), return_dtype=pl.Int64)
                  .alias("marker"), pl.lit(0, pl.UInt8).alias("cls"))
    return pl.concat([u, dnw]).unique(["msg", "marker"]).sort("msg", "marker")


def verify(goals=(20, 38)) -> bool:
    import polars as pl
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from common import ROOT, OUT as SH
    h34 = pl.read_parquet(ROOT / "data/processed/H34-idea-cascades/markers/uses.parquet")
    chat = pl.read_parquet(SH / "chat_core.parquet", columns=["goal_no"]).with_row_index("msg")
    ok = True
    for g in goals:
        rows = h34.join(chat.filter(pl.col("goal_no") == g), on="msg", how="semi")["msg"].unique().sort()
        rows = rows.head(3000)
        mine = uses_for_rows(rows.to_numpy())
        ref = h34.filter(pl.col("msg").is_in(rows.implode()))
        same = mine.sort("msg", "marker").equals(ref.sort("msg", "marker"))
        print(f"G{g:02d}: {rows.len()} messages, {ref.height} H34 uses, {mine.height} recomputed, identical: {same}")
        ok &= same
    print("verify:", "OK" if ok else "MISMATCH")
    return ok


if __name__ == "__main__":
    import sys
    if "--verify" in sys.argv:
        sys.exit(0 if verify() else 1)
    print(__doc__)
