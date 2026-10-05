"""Add (or refresh) the "Round 2" section of every H67 goal-period README from round2/periods.parquet and
round2/units.parquet. Regime-I periods take the round-2 chat-clock verdict as their top verdict (card rule, written
before the run); other periods keep their round-1 verdict.

    uv run python hypotheses/H67-lagged-criticality-dial/analysis/r2_write_periods.py
"""
import re
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[3]
H = ROOT / "hypotheses/H67-lagged-criticality-dial/goalperiod-subhypotheses"
R2 = ROOT / "data/processed/H67-lagged-criticality-dial/round2"
P = pl.read_parquet(R2 / "periods.parquet")
U = pl.read_parquet(R2 / "units.parquet").filter(pl.col("ok"))
V1 = dict(pl.read_parquet(ROOT / "data/processed/H67-lagged-criticality-dial/results/periods.parquet")
          .select("goal_no", "verdict").iter_rows())        # round-1 verdicts
f = lambda x: "n/a" if x is None or x != x else f"{x:.3f}"  # noqa: E731
ci = lambda r, k: f"{f(r.get(k))} [{f(r.get(k + '_lo'))}, {f(r.get(k + '_hi'))}]"  # noqa: E731
MARK = "## Round 2 (2026-10-05)"

for r in P.iter_rows(named=True):
    g = r["goal_no"]
    p = H / f"G{g:02d}" / "README.md"
    if not p.exists():
        continue
    txt = p.read_text()
    if MARK in txt:
        txt = txt.split(MARK)[0].rstrip() + "\n"
    us = U.filter(pl.col("unit_id").is_in(r["units"])).sort("unit_id")
    lad = "\n".join(
        f"| {u['unit_id']} | {f(u['g_L1'])} | {f(u.get('g_L4W'))} | {f(u['g_L8'])} | {f(u['g_L9'])} | "
        f"{f(u.get('r4_G3'))} | {f(u.get('r4_G5'))} [{f(u.get('r4_G5_lo'))}, {f(u.get('r4_G5_hi'))}] |"
        for u in us.iter_rows(named=True))
    body = [MARK, ""]
    reg = r["regime"]
    if reg == "I" and r.get("verdict_r2"):
        v1 = V1.get(g, "n/a")
        txt = re.sub(r"^\*\*Verdict:\*\*.*$", f"**Verdict:** {r['verdict_r2']} (round 2, chat clock; round 1: {v1})",
                     txt, count=1, flags=re.M)
        chat = "\n".join(
            f"| {u['unit_id']} | {u.get('chat_n_rows') or 'n/a'} | {f(u.get('chat_J'))} [{f(u.get('chat_J_lo'))}, "
            f"{f(u.get('chat_J_hi'))}] | {f(u.get('g_chat'))} [{f(u.get('g_chat_lo'))}, {f(u.get('g_chat_hi'))}] | "
            f"{f(u.get('g_cu'))} | {f(u.get('g_chat_logged'))} |" for u in us.iter_rows(named=True))
        body += [
            "### R1: the chat clock (regime I)",
            "*Prediction (card, 2026-10-05 02:45 UTC, before the run):* the round-1 rule re-applied on the chat clock, "
            "with g_I = g_cu + g_chat in place of g_lag and J*_chat in place of J₁*. Card-level R1-P1: regime-I median "
            "g_chat ≥ 0.05 [0.4].",
            "",
            f"**Result:** g_chat = {ci(r, 'g_chat')}, J*_chat = {ci(r, 'J_chat')}, g_cu = {ci(r, 'g_cu')}, "
            f"**g_I = {ci(r, 'g_I')}**, g_eq (round 1, same data) = {f(r.get('g_eq'))}; {r.get('n_chat_rows')} trimmed "
            f"chat-mode calls. **Round-2 verdict: {r['verdict_r2']}.** Start-time error attenuates g_chat to about "
            "0.23 × truth (synthetic S-R1d), so g_chat is a lower bound.",
            "",
            "| Unit | chat calls | J*_chat [95%] | g_chat [95%] | g_cu | g_chat (logged starts) |",
            "| --- | --- | --- | --- | --- | --- |",
            chat, ""]
    body += [
        "### R3 ladder and R4 multi-hop gain",
        f"*Descriptive (card, Round 2). Period pools (random effects).* H50's pair RD re-implemented (L1) "
        f"{ci(r, 'g_L1')} → with call-class cells (L4W) {ci(r, 'g_L4W')} → call counts with cells (L8) "
        f"{ci(r, 'g_L8')} → H67 main (L9) {ci(r, 'g_L9')}. R4 (synthetic S-R4 failed, descriptive only): "
        f"G₁ {ci(r, 'G1')}, G₃ {ci(r, 'G3')}, G₅ {ci(r, 'G5')}.",
        "",
        "| Unit | L1 (H50) | L4W (cells) | L8 (counts) | L9 (H67) | G₃ | G₅ [95%] |",
        "| --- | --- | --- | --- | --- | --- | --- |",
        lad, "",
        "Data: `data/processed/H67-lagged-criticality-dial/round2/units.parquet`, `periods.parquet`.", ""]
    p.write_text(txt.rstrip() + "\n\n" + "\n".join(body))
print("done")
