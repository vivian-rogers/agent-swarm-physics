"""H74 round 2: per-period Round-2 blocks and `**Verdict (r2):**` lines in the G folders, Round-2 blocks in the native NE
folders (NE14, NE40, NE43, NE45; new NE39), and per-period estimate rows. Idempotent (blocks between <!-- R2 --> marks).
Run after r2_monitor.py (both catalogs), r2_presence.py and r2_did.py:
    uv run python hypotheses/H74-change-detector/analysis/r2_periods.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r2lib as R  # noqa: E402
from r2_common import OUT, ROOT, load_frame  # noqa: E402

sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

HYP = ROOT / "hypotheses/H74-change-detector/goalperiod-subhypotheses"
TARGET = ["scaffold_tool", "scaffold_family", "operator", "operator_schedule", "undocumented", "goal"]
METHOD = ("H74 round 2 precision monitor: S schema diff ∪ D3 operator counters (log z, two-day persistence) ∪ frozen C3 "
          "topic rule (H36, bge); S and D3 thresholds leave-one-period-out conformal at alpha 0.02 on P2 placebo days; "
          "hit = alarm on day -1..+1")
NULL = "P2 placebo days (>= 2 active days from every catalogued event), thresholds calibrated on other periods"
SRC = "data/processed/H74-change-detector/r2/monitor_days.parquet"


def put_block(text: str, block: str) -> str:
    pat = re.compile(r"\n## Round 2 \(2026-10-05\)\n<!-- R2 -->.*?<!-- /R2 -->\n", re.S)
    new = "\n## Round 2 (2026-10-05)\n<!-- R2 -->\n" + block.strip() + "\n<!-- /R2 -->\n"
    if pat.search(text):
        return pat.sub(lambda _: new, text)
    if "\n## Scorecard" in text:
        i = text.index("\n## Scorecard")
        return text[:i] + new + text[i:]
    return text.rstrip() + "\n" + new


def put_verdict(text: str, v: str) -> str:
    if "**Verdict (r2):**" in text:
        return re.sub(r"\*\*Verdict \(r2\):\*\*[^\n]*", f"**Verdict (r2):** {v}", text)
    m = re.search(r"\*\*Verdict:\*\*[^\n]*\n", text)
    return text[:m.end()] + f"**Verdict (r2):** {v}\n" + text[m.end():]


def main():
    fr = load_frame("prereg")
    md = pl.read_parquet(OUT / "monitor_days.parquet")
    mon = md["alarm_monitor"].to_numpy()
    aS, aD, aC = md["alarm_S"].to_numpy(), md["alarm_D3"].to_numpy(), md["alarm_C3"].to_numpy()
    w = fr.window_any(mon)
    ev = fr.ev
    rows, table = [], []
    for g in sorted(set(fr.period.tolist())):
        idx = np.where(fr.period == g)[0]
        days = [fr.dl[i] for i in idx]
        e = ev.filter(pl.col("day0").is_in(days) & pl.col("cls").is_in(TARGET)).sort("day0")
        hits = [bool(w[fr.day_pos[d]]) for d in e["day0"].to_list()]
        p2 = idx[fr.P2[idx]]
        nfa = int(mon[p2].sum())
        nh = sum(hits)
        if e.height == 0:
            verdict = "descriptive"
        elif nh == e.height and nfa == 0:
            verdict = "supported"
        elif nh == 0:
            verdict = "failed"
        else:
            verdict = "mixed"
        n_alarm = int(mon[idx].sum())
        lines = []
        for (d, cls, lab), h in zip(e.select("day0", "cls", "label").iter_rows(), hits):
            i = fr.day_pos[d]
            ch = sorted({c for j in fr.nbr[i] for c, a in (("S", aS), ("D3", aD), ("C3", aC)) if a[j]})
            lines.append(f"| {d} | {cls.replace('_', ' ')} | {lab[:60].replace('|', '/')} | {'hit (' + ', '.join(ch) + ')' if h else 'miss'} |")
        fa_days = [fr.dl[j] for j in p2 if mon[j]]
        block = f"""Round-2 precision monitor on this period (card: Round 2; S ∪ D3 ∪ C3, LOPO thresholds at α = 0.02; role: replication, exploratory).
*Period rule written 2026-10-05 04:05 UTC, before any round-2 statistic: supported if every non-reserved target event (scaffold tool, scaffold family, drive, undocumented, goal) is hit and no P2 placebo day alarms; failed if none is hit; mixed otherwise; descriptive if none.*

Monitor alarm days: {n_alarm}/{len(days)}. P2 placebo days: {len(p2)}, false alarms {nfa}{' (' + ', '.join(fa_days) + ')' if fa_days else ''}.

| day 0 | class | event | monitor (channels in window) |
| --- | --- | --- | --- |
""" + ("\n".join(lines) if lines else "| – | – | no target event with a non-reserved day 0 | – |") + f"""

Result under the period rule: **{verdict}**. Data: `{SRC}` (goal_no = {g})."""
        f = HYP / f"G{g:02d}" / "README.md"
        if f.exists():
            t = f.read_text()
            f.write_text(put_verdict(put_block(t, block), verdict))
        unit = E.map_unit(int(g))
        base = {"period_unit": unit, "goal_no": int(g), "method": METHOD, "role": "replication", "first_day": days[0],
                "last_day": days[-1], "source": SRC, "null": NULL, "post_hoc": False}
        lo, hi = R.wilson(n_alarm, len(days))
        rows.append({**base, "statistic": "monitor_r2_alarm_day_rate", "channel": "S+D3+C3", "estimate": n_alarm / len(days),
                     "ci_lo": lo, "ci_hi": hi, "ci_kind": "parametric", "ci_level": 0.95, "n": len(days),
                     "n_kind": "scored days", "notes": "Wilson interval"})
        if e.height:
            lo, hi = R.wilson(nh, e.height)
            rows.append({**base, "statistic": "monitor_r2_target_hit_rate", "channel": "S+D3+C3", "estimate": nh / e.height,
                         "ci_lo": lo, "ci_hi": hi, "ci_kind": "parametric", "ci_level": 0.95, "n": e.height,
                         "n_kind": "target events (scaffold tool/family, drive, undocumented, goal)", "notes": "Wilson interval"})
        if len(p2):
            lo, hi = R.wilson(nfa, len(p2))
            rows.append({**base, "statistic": "monitor_r2_placebo_far_per_day", "channel": "S+D3+C3", "estimate": nfa / len(p2),
                         "ci_lo": lo, "ci_hi": hi, "ci_kind": "parametric", "ci_level": 0.95, "n": len(p2),
                         "n_kind": "P2 placebo days (out-of-sample)", "notes": "Wilson interval"})
        table.append({"goal_no": int(g), "verdict_r2": verdict, "n_days": len(days), "n_target": e.height, "n_hit": nh,
                      "n_P2": len(p2), "n_fa": nfa, "n_alarm": n_alarm})

    # ---------------- natives
    mj = json.loads((OUT / "monitor.json").read_text())
    mx = json.loads((OUT / "monitor_ext.json").read_text())
    pj = json.loads((OUT / "presence.json").read_text())
    nm, nx = mj["named"], mx["named"]
    r3 = mj["R3_variants"]

    def nrow(stat, goal, day, est, chan, note, n=3, n_kind="days in window", post_hoc=False):
        return {"period_unit": E.map_unit(goal, day, day) or f"local:{stat.split('_')[0]}", "goal_no": goal,
                "statistic": stat, "channel": chan, "estimate": float(est), "ci_lo": None, "ci_hi": None, "ci_kind": "none",
                "n": n, "n_kind": n_kind, "method": "H74 round 2 channel score, max over days -1..+1 (threshold in notes)",
                "null": NULL, "role": "native", "source": "data/processed/H74-change-detector/r2/monitor.json",
                "first_day": day, "last_day": day, "post_hoc": post_hoc, "notes": note}

    rows += [nrow("NE39_window_max_score_D3", 6, "2025-07-01", nm["NE39"]["D3"], "D3",
                  f"LOPO threshold {nm['NE39']['D3_threshold']:.2f}; alarm {nm['NE39']['D3_alarm']}"),
             nrow("NE43a_window_max_score_D3", 51, "2026-08-05", nm["NE43a"]["D3"], "D3",
                  f"LOPO threshold {nm['NE43a']['D3_threshold']:.2f}; alarm {nm['NE43a']['D3_alarm']}"),
             nrow("NE43b_window_max_score_D3", 51, "2026-08-21", nm["NE43b"]["D3"], "D3",
                  f"LOPO threshold {nm['NE43b']['D3_threshold']:.2f}; alarm {nm['NE43b']['D3_alarm']}")]
    acc = pj["prereg"]["acc"]["named"]["NE40"]
    rows.append({**nrow("NE40_presence_retirement_delay", 38, "2026-04-20", acc["first_within5"][0] if acc["first_within5"] else np.nan,
                        "presence", "accumulating retirement rule; delay in scored days to the first alarm (b_star3, b_star)",
                        n=1, n_kind="event"), "source": "data/processed/H74-change-detector/r2/presence.json"})
    E.write_estimates(rows, hypothesis="H74")
    pl.DataFrame(table).write_parquet(OUT / "period_table_r2.parquet")
    print(pl.DataFrame(table).group_by("verdict_r2").len())

    # ---------------- NE folder blocks
    def yn(b):
        return "alarm" if b else "no alarm"

    blocks = {
        "NE14": f"""Round-2 readout (card: Round 2). Monitor channels at 03-24 (window −1..+1):
| Channel | Score | Threshold | Outcome |
| --- | --- | --- | --- |
| S (pre-registered catalog) | {nm['NE14']['S']:.0f} | 20 (LOPO; two provider format changes sit on P2 days) | {yn(nm['NE14']['S_alarm'])} |
| S (catalog + round-1 provider dates, post hoc) | {nx['NE14']['S']:.0f} | 0 | {yn(nx['NE14']['S_alarm'])} |
| D3 (counters) | {nm['NE14']['D3']:.2f} | {nm['NE14']['D3_threshold']:.2f} | {yn(nm['NE14']['D3_alarm'])} |
| C3 (frozen topic rule) | {nm['NE14']['C3']:.2f} | 2 | {yn(nm['NE14']['C3_alarm'])} |

The monitor fires ({yn(nm['NE14']['monitor'])}). The positive control holds only through C3 under the pre-registered catalog; S recovers it once the provider dates leave the placebo pool.""",
        "NE40": f"""Round-2 readout (card: Round 2, R2 presence rule; a recovery, not blind).
| Rule | P2 false alarms (scored search days) | NE40 (04-20) |
| --- | --- | --- |
| accumulating retirement (primary, Amendment R2-A1) | {pj['prereg']['acc']['far_P2_scored'][0]}/{pj['prereg']['acc']['far_P2_scored'][1]} | first alarm 04-22, {acc['first_within5'][0]} scored days late (bullet markers `*`, 3-space `*`); outside ±1 |
| one-day retirement (pre-registered) | {pj['prereg']['pre']['far_P2_scored'][0]}/{pj['prereg']['pre']['far_P2_scored'][1]} | alarm on 04-20 (same markers) |
| appearance (secondary) | {pj['prereg']['appear']['far_P2_scored'][0]}/{pj['prereg']['appear']['far_P2_scored'][1]} | alarm on 04-20 (h2, `-` bullets, an opening-phrase class appear) |

The 03-31 search outage is not seen by any presence rule. Round-2 verdict: mixed (the primary rule dates the swap 2 days late at 0 false alarms; the pre-registered and appearance rules date it to the day).""",
        "NE43": f"""Round-2 readout (card: Round 2, D3 counters with two-day persistence, LOPO threshold).
| Step | D3 window max | Threshold | Outcome |
| --- | --- | --- | --- |
| NE43a (08-05, bookends stop) | {nm['NE43a']['D3']:.1f} | {nm['NE43a']['D3_threshold']:.2f} | {yn(nm['NE43a']['D3_alarm'])} |
| NE43b (08-21, nudges stop) | {nm['NE43b']['D3']:.1f} | {nm['NE43b']['D3_threshold']:.2f} | {yn(nm['NE43b']['D3_alarm'])} |

Both steps alarm with one day of delay (persistence). Round-2 verdict: supported.""",
        "NE45": f"""Round-2 readout (card: Round 2).
| Channel | Score at 07-29 | Threshold | Outcome |
| --- | --- | --- | --- |
| S (pre-registered catalog) | {nm['NE45']['S']:.0f} | 20 | {yn(nm['NE45']['S_alarm'])} |
| S (catalog + round-1 provider dates, post hoc) | {nx['NE45']['S']:.0f} | 0 | {yn(nx['NE45']['S_alarm'])} |
| presence rule (P2.4: should stay silent) | – | – | accumulating rule silent; one-day rule fires on h1 (a false attribution) |

Round-2 verdict: mixed (S is blinded by its own uncatalogued provider finds in the pre-registered placebo pool).""",
    }
    for ne, b in blocks.items():
        f = HYP / ne / "README.md"
        t = f.read_text()
        t = put_block(t, b)
        v = re.search(r"Round-2 verdict: (\w+)", b)
        if v:
            t = put_verdict(t, v.group(1))
        elif ne == "NE14":
            t = put_verdict(t, "supported" if nm["NE14"]["monitor"] else "failed")
        f.write_text(t)
    # NE39 (new folder; prediction P3.1 was written in the card before the run)
    d = HYP / "NE39"
    (d / "figures").mkdir(parents=True, exist_ok=True)
    q = r3["Q_D6"]["named"]["NE39"]; gg = r3["G_D6"]["named"]["NE39"]; ll = r3["L_D3_p2"]["named"]["NE39"]
    hum = mj["NE39_n_human"]
    (d / "README.md").write_text(f"""# H74 × NE39: public chat closes (#6; ≈ 2025-07-01, undocumented)

**Verdict:** supported
**Role:** native
**Period:** regime I · #6 · unit {E.map_unit(6) or '6'}.

## Why this period
Human messages per day fall from ~100–170 to ≤ 4 when the chat closes to the public. Round 1's Gaussian z on raw counts missed it. This is the test case of redirect H74-R3 (heavy-tailed baselines).

## Prediction
*Written in the card's Round 2 pre-registration (2026-10-05 03:50 UTC) and Amendment R2-A1 (~04:30 UTC), before any round-2 statistic. This folder was created after the run.*
- **P3.1** Q (empirical quantiles, 30 days) alarms on n_human within day −1..+1 of 07-01 at the LOPO-calibrated D threshold [0.75]; G (round-1 Gaussian z, raw) does not [0.8].
- Amendment R2-A1: the primary D channel became D3-L-p2 (log1p counts, Gaussian z, two-day persistence); P3.1 is read on it and on Q.

## Result
Human messages per day: {', '.join(f'{k[5:]} {int(v)}' for k, v in hum.items())}.

| Score | NE39 window max | LOPO threshold | Outcome |
| --- | --- | --- | --- |
| G, six features, one day (round 1) | {gg['window_max']:.1f} | {gg['threshold']:.1f} | {yn(gg['alarm'])} |
| Q, six features, one day (pre-registered primary) | {q['window_max']:.1f} | {q['threshold']:.1f} | {yn(q['alarm'])} |
| **D3-L-p2 (amended primary)** | **{ll['window_max']:.1f}** | **{ll['threshold']:.2f}** | **{yn(ll['alarm'])}** |

The log-count channel with persistence dates NE39 (alarm on 07-02, the second low day) at an out-of-sample per-day FAR of 1/82. Q does not: its threshold is set by heavy-tailed hours and silence features on placebo days. Round-2 verdict: supported on the amended channel; failed on the pre-registered Q.

## Scorecard (period-specific axes)
- G: the undocumented drive step is dated within one day.
- B: a log transform plus persistence handles the count tails; Q alone does not.
""")


if __name__ == "__main__":
    main()
