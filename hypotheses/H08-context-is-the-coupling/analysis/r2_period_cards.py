"""H08 round 2: add a dated "Round 2" section to each goal-period README and to NE41 (idempotent: replaces the section).

  uv run python hypotheses/H08-context-is-the-coupling/analysis/r2_period_cards.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h08lib import *  # noqa: E402,F403

R2 = OUT / "r2"
HEAD = "## Round 2 (2026-10-05)"


def f(v, k=100):
    return f"{k * v[0]:+.2f} [{k * v[1]:+.2f}, {k * v[2]:+.2f}]"


def insert(path: Path, block: str):
    s = path.read_text()
    s = re.sub(rf"\n{re.escape(HEAD)}.*?(?=\n## |\Z)", "", s, flags=re.S)
    if "\n## Notes" in s:
        s = s.replace("\n## Notes", "\n" + block.rstrip() + "\n\n## Notes", 1)
    else:
        s = s.rstrip() + "\n\n" + block
    path.write_text(s if s.endswith("\n") else s + "\n")


def main():
    S = {r["period"]: r for r in json.loads((R2 / "r2_summary.json").read_text())["rows"]}
    P = json.loads((R2 / "r4_pooled.json").read_text())
    A = json.loads((R2 / "r5_audit.json").read_text())
    for g in sorted(PERIODS):
        gn = gname(g)
        r = S.get(gn)
        if r is None:
            continue
        lines = [HEAD,
                 "*Predictions: the card's \"Round 2\" section (written 2026-10-05 02:45 UTC, before any round-2 statistic on real "
                 "data; amendments R2-A1..A3, R4-A1, R5-A1 written after the synthetic guards, still before real data). Role: "
                 "replication (R2, R5-b, R5-c)" + (", native (R4)" if gn in P["periods"] else "") + ". Reserved days never read. "
                 "Data: `data/processed/H08-context-is-the-coupling/r2/`. Content values are cosine ×100; brackets are 95% "
                 "1-hour-block bootstrap intervals (R4: day bootstrap).*", "",
                 "| Statistic | This period | Prediction | Note |", "| --- | --- | --- | --- |",
                 f"| R2 read − in-flight content at matched lag, no name and no reply (bge / gte) | {f(r['bge_delta'])} / {f(r['gte_delta'])} | > 0 (CI) in both models | read {r['n_read']}, in flight {r['n_flight']} statement rows |",
                 f"| R2 same, all statements (bge / gte) | {f(r['bge_all'])} / {f(r['gte_all'])} | — (robustness) | {100 * r['share_named']:.0f}% of rows name or reply to the sender |",
                 f"| R2 convergence share κ_c (bge, non-name) | {r['bge_kappa'][0]:.2f} | [0.2, 0.6]; synthetic gated-only ≈ 0.73 | κ_c > 1: in-flight statements are closer |"]
        if "bge_other_room" in r:
            lines.append(f"| R2 other-room placebo (bge, non-name) | {f(r['bge_other_room'])} | \\|Δ_other\\| < ⅓ Δ_own, CI at 0 | |")
        mon = A["monitor"].get(gn, {})
        sb, sg = (mon.get("bge") or {}).get("standard"), (mon.get("gte") or {}).get("standard")
        if sb and sg:
            lines.append(f"| R5-b log-free monitor: flagged agent-days minus floor (bge / gte, pp) | {sb['excess_pp']:+.1f} / {sg['excess_pp']:+.1f} "
                         f"({sb['n_agent_days']} agent-days; longest flagged run {sb['max_consecutive_flagged_days']} / {sg['max_consecutive_flagged_days']}) | ≤ 2 pp (regime III) | not a validated detector (R5-P4 failed) |")
        om = A["omitted"].get(gn)
        if om:
            lines.append(f"| R5-c ledger items beyond the 200-event cap | {100 * om['omitted_share']:.2f}% of {om['n_items']} | < 1% before 06-11; ≤ 5% in G51 | |")
        if gn in P["periods"]:
            v = P["periods"][gn]; b = v["auth"]["beta"]; d = v["describe"]["CF"]
            lines.append(f"| R4 forced-erasure units with the sender newly written to memory | {100 * d['dose_rate']:.0f}% of {d['n_with_dose']} | descriptive | |")
            lines.append(f"| R4 CF × dose on replies (pp) | {f(b['CFz'])} | > 0 pooled | pooled power 0.04 at half protection |")
            lines.append(f"| R4 dose salience β_z on replies (pp) | {f(b['z'])} | > 0 pooled | |")
        if g in (35, 36):
            fa = A["fetch_audit"]
            lines.append(f"| R5-a Claude Code feed | replay episode {fa['episodes'][0]['start_day']} → {fa['episodes'][0]['end_day']} "
                         f"({fa['episodes'][0]['n_fetches']} fetches, {fa['episodes'][0]['active_h']:.1f} active h) | one episode from 03-17 | supported |")
        rd = ("the round-1b content jump (regime III) is carried by statements that name or reply to the sender; without them, "
              "read statements are no closer to the message than in-flight statements at the same lag." if g in REGIME_III else
              "in regime I/II the round-1b content jump ran negative (in-flight talk sits closer in time). Lag matching removes "
              "that recency term; statements without the sender's name or a reply to it still show no read-gated content.")
        lines += ["", "**Reading:** " + rd + " The period verdict is unchanged (round 2 adds no period verdict rule).", ""]
        insert(GP / gn / "README.md", "\n".join(lines))
    # NE41
    pa = P["pooled"]["auth"]
    lines = [HEAD,
             "*R4, the memory dose (card \"Round 2\"; predictions 2026-10-05 02:45 UTC, amendment R4-A1 after the synthetic guard, "
             "before real data). Role: native. Data: `r2/r4_pooled.json`, `r2/G<NN>/r4_dose.json`.*", "",
             "| Prediction | Observed (reply author, pooled over 9 periods, DerSimonian–Laird) | Verdict |", "| --- | --- | --- |",
             f"| R4-P1 memory protects: CF × dose > 0, π ≥ 0.5 | CF × dose {100 * pa['CFz']['mu']:+.2f} ± {100 * pa['CFz']['se']:.2f} pp (π ≈ {pa['pi_pooled']:.2f}); G51 alone {f(P['periods']['G51']['auth']['beta']['CFz'])} | not supported; **inconclusive** (synthetic power 0.04 at π = 0.5, 0.22 at π = 1) |",
             f"| R4-P2 salience: placebo dose predicts replies | β_z {100 * pa['z']['mu']:+.1f} ± {100 * pa['z']['se']:.1f} pp; CI > 0 in 7/9 | supported |",
             f"| forced-erasure cut in this sample (CF, z = 0) | {100 * pa['CF']['mu']:+.2f} ± {100 * pa['CF']['se']:.2f} pp | consistent with round 1b |",
             "| R4-P3 dose rate | 48–90% of forced-erased units have the sender newly written to memory | descriptive |", "",
             "**Reading:** agents usually write the senders they are engaged with into memory (dose rate 48–90%), and those senders "
             "get more replies whether or not an erasure intervened. Writing the name does not measurably restore the coupling the "
             "erasure cut; in G51, the only well-powered period, the cut is if anything larger for named senders. The test cannot "
             "reject protection (power ≤ 0.22 even for full protection).", ""]
    insert(GP / "NE41" / "README.md", "\n".join(lines))
    print("period cards updated")


if __name__ == "__main__":
    main()
