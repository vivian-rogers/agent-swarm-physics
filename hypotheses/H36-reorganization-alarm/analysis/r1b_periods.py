"""H36 round 1b: write `**Verdict (1b):**` lines and a short "Round 1b" block into every period README (G and NE
folders scored by the replication), and the native results into the NE39/NE40/NE43/NE45 folders.

Reads r1b/{fixed_bge_restate,fixed_gte_restate}/{results.json,event_table.parquet,native.json}. Idempotent: the block
between <!-- R1B --> and <!-- /R1B --> is replaced; the Verdict (1b) line is replaced or inserted after `**Verdict:**`.

Usage: uv run python hypotheses/H36-reorganization-alarm/analysis/r1b_periods.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h36lib as L  # noqa: E402

import polars as pl  # noqa: E402

GP = L.HYP / "goalperiod-subhypotheses"
TAGS = {"bge": "fixed_bge_restate", "gte": "fixed_gte_restate"}


def fmt(x):
    return "–" if x is None or x != x else f"{x:.2f}"


def set_verdict(text: str, line: str) -> str:
    if "**Verdict (1b):**" in text:
        return re.sub(r"\*\*Verdict \(1b\):\*\*.*", line, text, count=1)
    return re.sub(r"(\*\*Verdict:\*\*[^\n]*\n)", r"\1" + line + "\n", text, count=1)


def set_block(text: str, body: str, header: str = "## Round 1b (improved data, 2026-10-04)") -> str:
    blk = f"<!-- R1B -->\n{body}\n<!-- /R1B -->"
    if "<!-- R1B -->" in text:
        return re.sub(r"<!-- R1B -->.*?<!-- /R1B -->", blk, text, flags=re.S)
    return text.rstrip() + f"\n\n{header}\n{blk}\n"


def main():
    R = {m: json.loads((L.OUT / "r1b" / t / "results.json").read_text()) for m, t in TAGS.items()}
    ET = {m: pl.read_parquet(L.OUT / "r1b" / t / "event_table.parquet") for m, t in TAGS.items()}
    NAT = {m: json.loads((L.OUT / "r1b" / t / "native.json").read_text()) for m, t in TAGS.items()}
    r1 = json.loads((L.OUT / "results.json").read_text())
    n = 0
    for d in sorted(GP.glob("G*")):
        f = d / "README.md"
        if not f.exists():
            continue
        g = d.name
        v = {m: R[m]["periods"].get(g, {}).get("verdict") for m in TAGS}
        if v["bge"] is None:
            continue
        v0 = r1["periods"].get(g, {}).get("verdict")
        same = v["bge"] == v["gte"]
        line = f"**Verdict (1b):** {v['bge']}" + ("" if same else f" (bge) / {v['gte']} (gte)") + \
               (" (unchanged)" if same and v["bge"] == v0 else "")
        rows = ["Re-run on the fixed activity table and outage mask (DQ8), restatements removed, both embedding models "
                "(card: Round 1b). Same verdict rule as round 1.", "",
                "| Score (day −1 / 0 / +1) | round 1 | 1b bge | 1b gte |", "| --- | --- | --- | --- |"]
        e0 = pl.read_parquet(L.OUT / "event_table.parquet").filter((pl.col("cls") == "goal") & (pl.col("ref") == f"#{int(g[1:])}"))
        e = {m: ET[m].filter((pl.col("cls") == "goal") & (pl.col("ref") == f"#{int(g[1:])}")) for m in TAGS}
        if e0.height and e["bge"].height:
            for k, lab in (("Z_phys", "Z_phys (alarm)"), ("Z_act", "Z_act"), ("Z_cont", "Z_cont"), ("R1", "R1")):
                cell = lambda df: " / ".join(fmt(df[f"{k}_o{o}"][0]) for o in (-1, 0, 1))  # noqa: E731
                rows.append(f"| {lab} | {cell(e0)} | {cell(e['bge'])} | {cell(e['gte'])} |")
        else:
            rows.append("| (kickoff not scored) | | | |")
        pb = {m: (R[m]["periods"][g]["placebo_n"], R[m]["periods"][g]["placebo_fa"]) for m in TAGS}
        rows += ["", f"Placebo days: {pb['bge'][0]} (alarms {pb['bge'][1]} bge, {pb['gte'][1]} gte). Data: "
                 f"`data/processed/H36-reorganization-alarm/r1b/{TAGS['bge']}/` and `.../{TAGS['gte']}/`."]
        txt = f.read_text()
        txt = set_block(set_verdict(txt, line), "\n".join(rows))
        f.write_text(txt); n += 1
    # NE folders scored in round 1 (NE34 summary, NE14/17/18/15/42/41)
    ne_v = {m: {k: x["verdict"] for k, x in R[m]["ne"].items()} for m in TAGS}
    for ne in ("NE34", "NE14", "NE17", "NE18", "NE15", "NE42", "NE41"):
        f = GP / ne / "README.md"
        if not f.exists():
            continue
        vb, vg = ne_v["bge"].get(ne), ne_v["gte"].get(ne)
        line = f"**Verdict (1b):** {vb}" + ("" if vb == vg else f" (bge) / {vg} (gte)")
        body = f"Round 1b tables (bge-small, restatements removed, fixed activity table):\n\n{R['bge']['ne'][ne]['body']}\n\n" \
               f"gte-modernbert:\n\n{R['gte']['ne'][ne]['body']}"
        f.write_text(set_block(set_verdict(f.read_text(), line), body)); n += 1
    # native folders
    tests = {"NE39": ["NE39"], "NE40": ["NE40"], "NE43": ["NE43a", "NE43b"], "NE45": ["NE45"]}
    for folder, tgts in tests.items():
        f = GP / folder / "README.md"
        lines = []
        for t in tgts:
            for m in TAGS:
                rec = NAT[m][t]
                lines += [f"**{t}** (day 0 {rec['day0']}, #{rec['goal_no']}; same day: {rec['same_day_refs']}; "
                          f"{rec['n_candidates']} candidate days for blind dating), {m}:", "",
                          "| Score | day −1 | day 0 | day +1 | hit (≥ 2) | top day in window | percentile vs candidates |",
                          "| --- | --- | --- | --- | --- | --- | --- |"]
                for k in ("Z_phys", "Z_act", "Z_act_trim", "Z_cont", "R1", "C3"):
                    x = rec[k]
                    lines.append(f"| {k} | {fmt(x['d-1'])} | {fmt(x['d0'])} | {fmt(x['d+1'])} | {'yes' if x['hit'] else 'no'} | "
                                 f"{'yes' if x['top_in_window'] else 'no'} | {fmt(x['pct_vs_candidates'])} |")
                lines.append("")
        txt = f.read_text()
        f.write_text(set_block(txt, "\n".join(lines).rstrip(), header="## Result")); n += 1
    print("updated", n, "READMEs")


if __name__ == "__main__":
    main()
