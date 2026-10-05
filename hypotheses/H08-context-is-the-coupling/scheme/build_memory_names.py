"""H08 round 2, R4 scheme: which agents each memory snapshot names (no text is written).

  uv run python hypotheses/H08-context-is-the-coupling/scheme/build_memory_names.py

One streaming pass over data/raw/ai-village/agent_memories.jsonl.gz. Rows are kept only if their PT date is a
non-reserved day of H08's NE41 periods (G36 from 2026-03-24, G37-G42, G44, G51; `period_days`, which applies
`holdout_mask` and `calendar.holdout`); reserved-day rows are skipped before parsing (prefilter on the raw
`created_at` field), so no reserved memory text is read. Names use the shared `common.mention_regexes` alias rule
(one alternation, same lookarounds). Per snapshot: names_mask (bit a = agent a named anywhere), added_mask (bit a =
agent a named in a line that is new relative to the same agent's previous kept snapshot; null if there is none within
24 h), n_lines. Output: data/processed/H08-context-is-the-coupling/r2/memory_names.parquet (codes and bitmasks only).
"""
from __future__ import annotations

import gzip
import re
import sys
import time
from pathlib import Path

import orjson

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h08lib import *  # noqa: E402,F403
from h08lib import ROOT  # noqa: E402

sys.path.insert(0, str(ROOT / "infra/shared"))
from common import rows as raw_rows  # noqa: E402
from scan_tables import agent_codes  # noqa: E402

RAW = ROOT / "data/raw/ai-village"
OUT2 = OUT / "r2"
NE41 = [36, 37, 38, 39, 40, 41, 42, 44, 51]


def name_regex():
    """One alternation over all aliases; returns (regex, alias.lower() -> agent code). Same alias rule and lookarounds
    as common.mention_regexes (o1/o3 are pre-regime-III agents and are skipped here)."""
    A = agent_codes()
    alias = {}
    for a in raw_rows("agents"):
        name = a["name"]
        if name.startswith("[Temporary]") or "Claude Code" in name or name in ("o1", "o3") or a["id"] not in A:
            continue
        al = {name}
        if name.startswith("Claude "):
            al.add(name[len("Claude "):])
        if name.endswith(" Pro"):
            al.add(name[: -len(" Pro")])
        for x in al:
            if len(x) >= 4:
                alias[x.lower()] = A[a["id"]]
    alt = "|".join(re.escape(x) for x in sorted(alias, key=len, reverse=True))
    return re.compile(rf"(?<![\w.])({alt})(?![\w]|\.\d)", re.IGNORECASE), alias


def main():
    t0 = time.time()
    days = set()
    for g in NE41:
        dd = period_days(g)
        if g == 36:
            dd = [d for d in dd if d >= "2026-03-24"]
        days |= set(dd)
    assert not any(is_holdout(d, None) for d in days)
    rx, alias = name_regex()
    A = agent_codes()
    import datetime as _dt
    from zoneinfo import ZoneInfo
    PT = ZoneInfo("America/Los_Angeles")
    lo = min(days); hi_ = max(days)
    hi1 = (_dt.date.fromisoformat(hi_) + _dt.timedelta(days=1)).isoformat()
    cache: dict[int, int] = {}
    snaps = []
    n_seen = 0
    with gzip.open(RAW / "agent_memories.jsonl.gz", "rb") as f:
        for line in f:
            i = line.rfind(b'"created_at":"')
            if i < 0:
                continue
            j = line.find(b'"', i + 14)
            ca = line[i + 14:j].decode(errors="ignore")
            # PT date from the raw field, before parsing the row: reserved-day rows are never parsed
            if ca[:10] < lo or ca[:10] > hi1:
                continue
            t = dt.datetime.fromisoformat(ca).replace(tzinfo=dt.timezone.utc)
            d = t.astimezone(PT).date().isoformat()
            if d not in days:
                continue
            r = orjson.loads(line)
            n_seen += 1
            ag = A.get(r["agent_id"])
            hs = []
            nm = 0
            for ln in (r["content"] or "").splitlines():
                ln = ln.strip()
                if not ln:
                    continue
                h = hash(ln)
                m = cache.get(h)
                if m is None:
                    m = 0
                    for x in rx.findall(ln):
                        m |= 1 << int(alias[x.lower()])
                    cache[h] = m
                hs.append(h)
                nm |= m
            snaps.append((t, ag, d, nm, frozenset(hs)))
    snaps.sort(key=lambda x: (x[1] if x[1] is not None else -1, x[0]))
    recs = []
    prev = {}
    for t, ag, d, nm, hs in snaps:
        p = prev.get(ag)
        if p is not None and (t - p[0]).total_seconds() <= 24 * 3600:
            am = 0
            for h in hs - p[1]:
                am |= cache[h]
        else:
            am = None
        recs.append((t, ag, d, nm, am, len(hs)))
        prev[ag] = (t, hs)
    df = pl.DataFrame(recs, schema={"t": pl.Datetime("us", "UTC"), "agent": pl.Int8, "pt_date": pl.Utf8, "names_mask": pl.UInt64,
                                    "added_mask": pl.UInt64, "n_lines": pl.Int32}, orient="row").sort("agent", "t")
    OUT2.mkdir(parents=True, exist_ok=True)
    df.write_parquet(OUT2 / "memory_names.parquet", compression="zstd")
    print(f"{df.height} snapshots kept ({n_seen} parsed), {len(cache)} distinct lines, {time.time() - t0:.0f}s", flush=True)
    write_provenance("r2/memory_names.parquet", "hypotheses/H08-context-is-the-coupling/scheme/build_memory_names.py",
                     ["agent_memories (raw, text read in memory only)", "agents", "calendar"],
                     {"days": "non-reserved days of G36 (from 03-24), G37-G42, G44, G51", "alias_rule": "common.mention_regexes",
                      "added": "names in lines absent from the same agent's previous kept snapshot (<= 24 h)",
                      "reserved_days": "skipped before parsing"}, folder=OUT2)


if __name__ == "__main__":
    main()
