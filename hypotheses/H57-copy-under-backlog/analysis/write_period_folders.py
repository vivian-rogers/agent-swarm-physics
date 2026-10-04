"""H57 period folders: predictions first (before the real-data run), results filled in afterwards.

  uv run python hypotheses/H57-copy-under-backlog/analysis/write_period_folders.py predict
  uv run python hypotheses/H57-copy-under-backlog/analysis/write_period_folders.py results

predict: one goalperiod-subhypotheses/G<NN>/README.md per eligible period (role replication; G51 native) and the
         native folders NE42 and NE41, each with Verdict pending and a dated prediction.
results: keeps everything above '## Result', sets the Verdict line and writes the Result and Scorecard sections
         from data/processed/H57-copy-under-backlog/results/*.json. Codes and numbers only.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
HDIR = HERE.parent
ROOT = HDIR.parents[1]
GP = HDIR / "goalperiod-subhypotheses"
RES = ROOT / "data/processed/H57-copy-under-backlog/results"
SK = ROOT / "data/processed/H57-copy-under-backlog/skeleton"
AFF = ROOT / "hypotheses/hypohypotheses/period-affordances.md"
NATIVE_G = {51}


def catalog() -> dict:
    txt = AFF.read_text()
    out = {}
    for m in re.finditer(r"^### G(\d\d) · (.+?)\n`([^`]+)`(.*)$", txt, re.M):
        out[int(m.group(1))] = {"title": m.group(2).replace("🔒", "").strip(), "dates": m.group(3),
                                "line": (m.group(3) + m.group(4)).strip()}
    return out


def eligible_periods() -> list[tuple[int, int, int]]:
    import polars as pl
    s = pl.read_parquet(SK / "skeleton_summary.parquet")
    return [(r["goal_no"], r["n_k1"], r["n_agents"]) for r in s.iter_rows(named=True)
            if r["n_k1"] >= 200 and r["n_agents"] >= 3]


def mdd(s: str) -> str:
    return s.replace("#", "\\#") if False else s


def replication_readme(g: int, cat: dict, n: int, na: int, stamp: str) -> str:
    c = cat.get(g, {"title": f"goal period {g}", "dates": "", "line": ""})
    se = 0.010 * (1500 / max(n, 1)) ** 0.5
    return f"""# H57 × G{g:02d}: {c['title']} ({c['dates']})

**Verdict:** pending
**Role:** replication
**Period:** {c['line']}. Non-holdout statements with backlog k ≥ 1: {n} by {na} agents.

## Why this period
Layer 1 (replication): the common H57 estimator on every eligible goal period, so the per-period slopes are comparable points on a phase diagram (copying vs backlog against period size, regime and median k). This folder is one such point, not an independent native test.

## Prediction
*Written {stamp}, before running H57 on this period. Templated replication prediction (layer 1), as the two-layer rule allows.*
- **P1:** the within-agent slope of the chance-corrected read-set echo on log₂(1 + k) is positive in both embedding models (β_echo,bge > 0 and β_echo,gte > 0).
- **P2:** the chance-corrected marker near-copy slope β_mk is positive.
- **P3:** the copy share of the near-coded addressed channel rises from the bottom to the top k tercile (T > 0).
- **Power:** at this size the slope SE is roughly {se:.3f} per doubling of k (scaled from the synthetic #40 worlds), so only slopes above ~{2.8 * se:.3f} are reliably detectable here. The synthetic load world plants ≈ 0.03.
- **Verdict rule (card):** supported if β_echo (both models) and β_mk are > 0 with at least one one-sided p < 0.05 and none significantly negative; failed if any of them is significantly negative or all are ≤ 0; mixed otherwise.
- **Against:** slopes ≤ 0, or significantly negative.

## Result
Pending.
"""


NATIVE = {
    "NE42": """# H57 × NE42: #best/#rest merge and split, A-B-A (2026-05-04 / 05-11)

**Verdict:** pending
**Role:** native
**Period:** #39 (2026-04-27 → 05-01, two rooms) → #40 (05-04 → 05-08, one merged room, #universe-coordination) → #41 (05-11 → 05-15, two rooms, same partition). Regime III, 15 agents, not held out. Goal-confounded: each phase is a new goal, and #40 is a shared objective.

## Why this period
The merge puts 14 agents in one room at a fixed roster, so every agent's backlog should jump; the split lowers it again. The backlog moves for a reason unrelated to any one agent's content, and the A-B-A shape guards against a monotone drift. If load drives copying, each agent's chance-corrected echo should rise in #40 and fall in #41, and agents whose backlog rose most should change most.

## Prediction
*Written {stamp}, before running H57 on these periods.*
- **N42a (DiD):** across agents present in all three phases (≥ 10 statements each), the DiD = y(40) − [y(39) + y(41)]/2 of the chance-corrected echo (bge and gte) and marker near-copy is > 0, with a one-sided sign-flip p < 0.05 for at least one of them and the right sign for all three.
- **N42b (dose):** the per-agent DiD in log k is > 0 on average, and the Spearman correlation across agents between the DiD in echo and the DiD in log k is > 0.
- **N42c (statement level, the transition as the object):** with agent fixed effects over the three periods, the merged-week coefficient is > 0 and shrinks once log k is controlled (the backlog carries the merge effect).
- **Against:** DiD ≤ 0, or a merged-week effect that does not depend on log k (a goal effect of #40's shared objective).
- **Power:** ~15 agents. Only a large effect is detectable.

## Result
Pending.
""",
    "NE41": """# H57 × NE41: forced context erasures reset the context load (regime III, non-holdout)

**Verdict:** pending
**Role:** native
**Period:** regime III non-holdout goal periods #36–#42, #44, #51 (units 51a–51l). At the 41-turn cap the scaffold erases the context window (memory kept) at a time set by the scaffold, not the agent: ~21k forced vs ~16k voluntary consolidations (DQ1 ledger, non-holdout).

## Why this period
The backlog k counts what arrived since the agent last spoke; the context load k_ctx counts everything in the window since the last reset. A forced erasure sets k_ctx to ≈ 0 at a quasi-random time while leaving the conversation (and k) untouched. If copying is a response to load on a bounded context, statements just after an erasure, at the same backlog, should copy less. If agents echo recent messages to re-orient after losing their context, they should copy more.

## Prediction
*Written {stamp}, before running H57 on these periods.*
- **N41a:** within agent × unit, comparing statements in the first three receiving calls after a forced erasure with those in the last three calls before one (same day), at fixed log k and the card's controls, the after-erasure coefficient on the chance-corrected echo (bge and gte) and marker near-copy is < 0 (random-effects pooled over periods).
- **N41b:** in all computer-use statements, the slope on log₂(1 + k_ctx) at fixed log k is > 0 (pooled).
- **Comparison:** voluntary consolidations (agent-timed) give the same contrast with a timing confound. A forced–voluntary difference would point to the agent choosing when to consolidate.
- **Against:** after-erasure coefficient ≥ 0 (> 0 = the reorientation reading).

## Result
Pending.
""",
}


G51_NATIVE = """# H57 × G51: Maximize your private assigned role (non-holdout units 51a–51l)

**Verdict:** pending
**Role:** native
**Period:** {line}. Non-holdout statements with backlog k ≥ 1: {n} by {na} agents. The tail (09-07 →) is held out.

## Why this period
The roster grows from 21 to 32 agents in 11 dated steps at a fixed goal, hours and (mostly) one room, so the backlog grows for reasons unrelated to content. It is also the period with the heaviest backlog tail (k ≥ 30 is common) and by far the most statements (≈ 34k), so it carries most of H57's power. Native observables: the unit-level N sweep, the high-k tail and family heterogeneity, plus the replication estimator.

## Prediction
*Written {stamp}, before running H57 on this period.*
- **N51a (replication estimator, most powered):** β_echo > 0 in both models and β_mk > 0, each with p < 0.05.
- **N51b (N sweep):** across the 12 non-holdout units, the unit-mean chance-corrected echo rises with the unit's median log k (Spearman > 0; one-sided permutation p < 0.1 given 12 units), and the median log k rises with N.
- **N51c (high-k tail):** within agent × unit, statements with k ≥ 30 have a higher chance-corrected echo than those with k ≤ 3.
- **N51d (P3 here):** T > 0 on the near-coded addressed channel (both models).
- **Against:** a flat or falling echo across the k bins and units.

## Result
Pending.
"""


def predict():
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    cat = catalog()
    for g, n, na in eligible_periods():
        d = GP / f"G{g:02d}"
        (d / "figures").mkdir(parents=True, exist_ok=True)
        f = d / "README.md"
        if f.exists() and "Verdict:** pending" not in f.read_text():
            continue
        if g in NATIVE_G:
            f.write_text(G51_NATIVE.format(line=cat[g]["line"], n=n, na=na, stamp=stamp))
        else:
            f.write_text(replication_readme(g, cat, n, na, stamp))
    for k, txt in NATIVE.items():
        d = GP / k
        (d / "figures").mkdir(parents=True, exist_ok=True)
        if not (d / "README.md").exists():
            (d / "README.md").write_text(txt.replace("{stamp}", stamp))
    print("predictions written", stamp)


if __name__ == "__main__":
    if sys.argv[1] == "predict":
        predict()


# ------------------------------------------------------------------------------------------------ results
def _s(r, key, c="logk"):
    v = (r["slopes"].get(key, {}) or {}).get(c) or {}
    return v.get("b"), v.get("se"), v.get("p")


def _fmt(b, se=None, p=None, pc=None):
    if b is None:
        return "n/a"
    out = f"{b:+.4f}"
    if se is not None:
        out += f" ± {1.96 * se:.4f}"
    if pc is not None:
        out += f" (p_cal {pc:.3g})"
    elif p is not None:
        out += f" (p {p:.3g})"
    return out


def replication_result(r: dict, pooled: dict) -> tuple[str, str]:
    cp = r.get("calibrated_p", {})
    rows = []
    for key, lab, pred in (("e_bge|agent", "P1 β_echo, bge (chance-corrected)", "> 0"),
                           ("e_gte|agent", "P1 β_echo, gte", "> 0"),
                           ("mkn_all|agent", "P2 β_mk (marker near-copy)", "> 0")):
        b, se, p = _s(r, key)
        pc = (cp.get(key) or {}).get("p_cal")
        ok = "met" if (b or 0) > 0 and pc is not None and pc / 2 < 0.05 else ("against (sig. < 0)" if (b or 0) < 0 and pc is not None and pc < 0.05 else "not met")
        rows.append(f"| {lab} | {pred} | {_fmt(b, se, None, pc)} | {ok} |")
    for m in ("bge", "gte"):
        d = r["decomp"].get(f"addr|{m}|K32", {})
        T, pT = d.get("T"), d.get("p_one")
        rows.append(f"| P3 T, near-coded addressed channel, {m} (n {d.get('n', 0)}) | > 0 | "
                    f"{'n/a' if T is None else f'{T:+.4f}'} (s {(d.get('s_bottom') if d.get('s_bottom') is not None else float('nan')):.3f} → {(d.get('s_top') if d.get('s_top') is not None else float('nan')):.3f}; perm. p {pT if pT is None else round(pT, 3)}) | "
                    f"{'met' if T is not None and pT is not None and pT < 0.05 and T > 0 else 'not met'} |")
    post = []
    for key, lab in (("er_bge|agent", "raw read-set echo, bge (upper bound; no chance correction)"),
                     ("er_gte|agent", "raw read-set echo, gte"),
                     ("elc_bge|agent", "lag-matched count excess, bge (Amendment 2)"),
                     ("elc_gte|agent", "lag-matched count excess, gte"),
                     ("elc_bge|filt", "lag-matched count excess, bge, without templated / kickoff-echo statements"),
                     ("cross_echo_bge_f|agent", "DQ5 cross_echo (crude flag, P7)"),
                     ("e_bge|day", "rival a: β_echo bge with day FE"),
                     ("e_bge|filt", "rival b: β_echo bge without templated / kickoff-echo statements"),
                     ("elc_bge|kctx", "context load log₂(1+k_ctx) at fixed k, lag-matched (bge)")):
        c = "logkctx" if key.endswith("kctx") else "logk"
        b, se, p = _s(r, key, c)
        post.append(f"| {lab} | {_fmt(b, se, p)} |")
    rt = {k: (v if v is not None else float("nan")) for k, v in r["rates"].items()}
    tab = ("| Prediction (dated) | Predicted | Observed (95% CI) | Verdict |\n| --- | --- | --- | --- |\n" + "\n".join(rows) +
           "\n\n**Post hoc and robustness (not part of the verdict):**\n\n| Statistic | Slope per doubling of k (95% CI) |\n| --- | --- |\n" +
           "\n".join(post))
    ctx = (f"n = {r['n']} statements with k ≥ 1 ({r['n_agents']} agents, {r['n_days']} days, {r['n_units']} units); "
           f"median k {r['k_med']:.0f}, q90 {r['k_q90']:.0f}. Read-set echo rate {rt.get('echo_bge_R', float('nan')):.4f} (bge), "
           f"{rt.get('echo_gte_R', float('nan')):.4f} (gte); in-flight chance rate per pair {rt.get('q_bge', float('nan')):.4f} (bge). "
           f"corr(log k, first day) {r['corr_logk_early'] if r['corr_logk_early'] is None else round(r['corr_logk_early'], 3)}.")
    v = r["verdict"]
    vtxt = (f"{v} (pre-registered rule; the chance-corrected slopes are biased negative by contemporaneous convergence, card "
            f"Amendment 2; raw-echo upper bound {_fmt(_s(r, 'er_bge|agent')[0])} per doubling)")
    return vtxt, ctx + "\n\n" + tab


def cnote(r: dict) -> str:
    er = _s(r, "er_bge|agent")[0] or 0.0
    elc, elcse, _ = _s(r, "elc_bge|agent")
    ef = _s(r, "elc_bge|filt")[0]
    if er > 0.01 or (elc is not None and elcse and elc - 1.96 * elcse > 0):
        if elc is not None and elc <= 0:
            return ("The load-dependent copy model does not beat the constant-copy null. The raw echo slope is sizeable "
                    f"here (bge {er:+.4f}), but the lag-matched slope is negative ({elc:+.4f}): the raw rise is chance "
                    "growth from contemporaneous near-copies, not copying.")
        tail = (f"The raw echo slope is sizeable here (bge {er:+.4f}); the lag-matched slope is {elc:+.4f} but "
                f"{'turns ' + format(ef, '+.4f') + ' without templated / kickoff-echo statements (rival b: shared sources)' if ef is not None and ef <= 0 else 'survives the shared-source filter (' + format(ef or 0, '+.4f') + '); a post hoc lead only'}.")
        return "The load-dependent copy model does not beat the constant-copy null on the pre-registered estimator. " + tail
    return ("The load-dependent copy model does not beat the constant-copy null here: the pre-registered slope is ≤ 0 "
            f"and the raw upper bound is small ({er:+.4f} per doubling, bge).")


def results():
    pooled = json.loads((RES / "pooled.json").read_text())
    for f in sorted(RES.glob("G*.json")):
        r = json.loads(f.read_text())
        g = r["goal_no"]
        if g in NATIVE_G:
            continue
        p = GP / f"G{g:02d}" / "README.md"
        if not p.exists():
            continue
        txt = p.read_text()
        head = txt.split("## Result")[0]
        vtxt, body = replication_result(r, pooled)
        head = re.sub(r"^\*\*Verdict:\*\* .*$", f"**Verdict:** {vtxt}", head, count=1, flags=re.M)
        res = (f"## Result\n*Run 2026-10-04 (non-holdout). Numbers: `data/processed/H57-copy-under-backlog/results/G{g:02d}.json`.*\n\n"
               f"{body}\n\n## Scorecard (period-specific axes)\n"
               f"- **C (adequacy):** 0. {cnote(r)}\n"
               f"- **D (unfitted predictions):** 0. P1–P3 not met.\n\n"
               f"## Notes\n- Replication folder (layer 1): one phase-diagram point, not an independent test. "
               f"Per-period p-values are calibrated with κ from the constant-π synthetic worlds (card Amendment 1c).\n"
               f"- The near-coded copy share s is ≈ 0 in both k terciles wherever T = 0: agents almost never near-copy the "
               f"message they address (the copy information left after the Miller–Madow correction is ≤ 0).\n")
        p.write_text(head + res)
    print("replication results written")


if __name__ == "__main__" and sys.argv[1] == "results":
    results()
