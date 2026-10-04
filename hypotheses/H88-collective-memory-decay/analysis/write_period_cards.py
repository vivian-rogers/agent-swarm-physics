"""Write H88's goal-period READMEs (--stage predict | results)."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h88lib as H  # noqa: E402

HYP = H.ROOT / "hypotheses/H88-collective-memory-decay"
PRED_STAMP = "2026-10-04 21:04 UTC"
NATIVE = {"G05", "G10", "NE28"}

REPL_PRED = """*Written {stamp}, before running on this period. Templated replication prediction (layer 1).*
- **Observable:** the veterans' attention share to this period's items over the 120 village days after its last day (artifacts: repos, sites, files first seen here; terms: H34 N-class coinages first seen here). Fits M1 (single exponential), M2 (biexponential), M1c (exponential + floor), MP (power law) by quasi-likelihood; QAIC.
- **Prediction:** M2 is the best model and beats M1 by ≥ 2 QAIC (a fast τ₁ of 0.5–5 village days and a slow τ₂ of 10–120); the present veterans' share at k 21–40 is below the share at k 1–3.
- **Verdict rule (templated, per channel; artifacts primary where eligible):** supported if M2 is best with ΔQAIC(M1−M2) ≥ 2; failed if M1 is best; mixed if M1c or MP is best. Per-period power for the call is 0.4–0.6 (artifacts) and 0.6–0.97 (terms) at the synthetic biexponential.
- *Counts against:* M1 best (kill 1), or no decay of the present veterans' share (kill 2)."""

NAT_PRED = {
    "G05": """*Written {stamp}, before running (native N1).*
- **Why native:** from 2025-05-23 (Claude Opus 4 joins) to 2025-08-15 the roster is fixed at four agents (Claude 3.7 Sonnet, o3, Gemini 2.5 Pro, Claude Opus 4). No departure and no newcomer can shape the decay of attention to #4–#7's items.
- **N1 prediction:** with the follow-up truncated at 2025-08-15, M2 beats M1 (best by QAIC and ΔQAIC ≥ 2) for at least 2 of #4, #5, #6, #7 on artifacts or terms.
- *Counts against:* M1 best in ≥ 3 of 4, or no decay (decay needs carrier turnover).""",
    "G10": """*Written {stamp}, before running (native N2).*
- **Why native:** NE27: GPT-5, Grok 4 and Claude Opus 4.1 join the four veterans on 2025-08-18 with empty memories. From that day both groups can use the items of #2–#8; only the veterans were there.
- **N2 prediction:** over 08-18 → 09-19 (non-holdout), the newcomers' standardized ratio R (observed uses / uses expected at the veterans' share on the same day, same source period) is < 1 for items whose source period ended ≤ 15 village days earlier (CI < 1), and R rises with item age: R(> 40 days) > R(≤ 15 days).
- *Counts against:* R(≤ 15) ≥ 1, or R falling with age (newcomers learn recent items as fast as veterans remember them).""",
    "NE28": """*Written {stamp}, before running (native N3; NE28 and NE29, plus Grok 4's exit).*
- **Why native:** retirements remove a carrier with a long memory: Grok 4 (2025-10-29), o3 and Claude Opus 4.1 (2025-12-01, NE28), Claude 3.7 Sonnet (2026-02-19, NE29; the longest-serving agent). This folder spans goal boundaries (exception (c)).
- **N3 design:** items (from any earlier non-holdout period) with ≥ 5 agent uses in the 10 village days before an exit. Retiree-carried: the retiree made ≥ 40% of those uses. Controls: items with < 10% retiree uses, in the same pre-exit volume tercile. Outcome: other agents' uses in the 10 village days after vs before; ratio of ratios (carried / control), item-block bootstrap.
- **N3 prediction:** other agents keep using retiree-carried items: the ratio of ratios lies in [0.5, 2] with a CI that includes 1.
- *Counts against:* CI below 1 (the item's memory left with its carrier).""",
}


def write_predict():
    syn = json.loads((H.DATA / "synthetic" / "synthetic.json").read_text())
    elig = sorted(set(syn["eligible_art"]) | set(syn["eligible_term"]))
    periods = pl.read_parquet(H.DATA / "periods.parquet")
    folders = [f"G{p:02d}" for p in elig] + ["G10", "NE28"]
    for f in sorted(set(folders) | {"G05"}):
        d = HYP / "goalperiod-subhypotheses" / f
        (d / "figures").mkdir(parents=True, exist_ok=True)
        (d / "figures" / ".gitkeep").touch()
        role = "native" if f in NATIVE else "replication"
        if f.startswith("G"):
            P = int(f[1:])
            pr = periods.filter(pl.col("P") == P)
            first, last, reg = pr["first_day"][0], pr["last_day"][0], pr["regime"][0]
            na, nt = pr["art"][0], pr["term"][0]
            title = f"# H88 × {f}: the afterlife of goal period #{P} ({first} → {last})"
            per = (f"**Period:** regime {reg} · items: {na or 0} artifacts, {nt or 0} terms · follow-up 120 village days "
                   f"after {last} (held-out days censored). Channels eligible: "
                   f"{'artifacts' if P in syn['eligible_art'] else ''}{', ' if P in syn['eligible_art'] and P in syn['eligible_term'] else ''}"
                   f"{'terms' if P in syn['eligible_term'] else ''}.")
        else:
            title = "# H88 × NE28: carrier loss (retirements: Grok 4, o3, Claude Opus 4.1, Claude 3.7 Sonnet)"
            per = "**Period:** spans goal periods #18–#31 (exits 2025-10-29, 2025-12-01, 2026-02-19); regime I."
        why = (NAT_PRED[f].split("\n")[1].replace("- **Why native:** ", "") if role == "native"
               else "A replication point for the common estimator (layer 1): every eligible finished period gets the same fits.")
        pred = NAT_PRED[f] if role == "native" else REPL_PRED
        if role == "native" and f.startswith("G") and int(f[1:]) in elig:
            pred += "\n\nThe templated replication prediction also applies to this period:\n" + REPL_PRED
        (d / "README.md").write_text(f"""{title}

**Verdict:** pending
**Role:** {role} (exploratory)
{per}

## Why this period
{why}

## Prediction
{pred.format(stamp=PRED_STAMP)}

## Result
Pending.
""")
    import shutil
    if (HYP / "goalperiod-subhypotheses" / "GNN").exists():
        shutil.rmtree(HYP / "goalperiod-subhypotheses" / "GNN")
    print("wrote", len(set(folders) | {"G05"}))


def fmt_fit(r):
    if not r:
        return "not eligible (design) or fewer than 50 post-period veteran uses"
    m2 = r["fit"]["M2_params"]
    return (f"best {r['fit']['best']}; ΔQAIC(M1−M2) {r['fit']['dq_M1_M2']:+.1f}; M2 τ₁ {m2['tau1']:.1f}, τ₂ {m2['tau2']:.0f}, "
            f"slow share {m2['slow_share']:.2f}; M1 τ {r['fit']['M1_params']['tau']:.1f}; φ {r['fit']['phi']:.1f}; "
            f"share ratio (k 21–40 / 1–3) {r['ratio']['ratio']:.2f}" if r.get("ratio") and r["ratio"].get("ratio") is not None
            else f"best {r['fit']['best']}; ΔQAIC {r['fit']['dq_M1_M2']:+.1f}")


def templ(r):
    if not r:
        return None
    b = r["fit"]["best"]
    if b == "M2" and r["fit"]["dq_M1_M2"] >= 2:
        return "supported"
    return "failed" if b == "M1" else "mixed"


def write_results():
    rep = json.loads((H.DATA / "replication" / "replication.json").read_text())
    nat = json.loads((H.DATA / "natives" / "natives.json").read_text())
    for d in sorted((HYP / "goalperiod-subhypotheses").iterdir()):
        if not d.is_dir():
            continue
        f = d.name
        p = d / "README.md"
        pre = p.read_text().split("## Result")[0]
        lines = ["## Result", f"*Run {rep['run_at']} (`analysis/replication.py`, `analysis/natives.py`) → "
                 "`data/processed/H88-collective-memory-decay/replication/replication.json`, `natives/natives.json`.*", ""]
        verdict = "n/a"
        if f.startswith("G"):
            P = str(int(f[1:]))
            ra = rep["periods"].get(P, {}).get("art"); rt = rep["periods"].get(P, {}).get("term")
            lines += [f"- **Artifacts (veterans):** {fmt_fit(ra)}.", f"- **Terms (veterans):** {fmt_fit(rt)}."]
            v = templ(ra) or templ(rt)
            verdict = v or "n/a"
            lines.append(f"- **Templated verdict:** {verdict} ({'artifacts' if templ(ra) else 'terms'} channel).")
        if f in nat.get("texts", {}):
            lines += ["", nat["texts"][f]["text"]]
            verdict = nat["texts"][f]["verdict"]
        body = re.sub(r"\*\*Verdict:\*\* [^\n]*", f"**Verdict:** {verdict}", pre, count=1)
        sc = ("\n## Scorecard (period-specific axes)\n" +
              (nat["texts"][f]["scorecard"] if f in nat.get("texts", {}) else
               "- Replication point only (layer 1): informs C and I in the main card.") + "\n")
        p.write_text(body + "\n".join(lines) + "\n" + sc)
    print("results written")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["predict", "results"], required=True)
    a = ap.parse_args()
    write_predict() if a.stage == "predict" else write_results()
