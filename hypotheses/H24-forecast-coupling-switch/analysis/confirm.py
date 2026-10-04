"""H24 confirmatory test on the locked holdout: goal period #14 ("take a bunch of personality tests"; regime I,
mode I, held out). WRITTEN 2026-10-03, NOT RUN. Predictions are in PREDICTIONS below and in the card.

Why #14: the only held-out period whose catalogued setup has an individual-work-then-compare structure
(each agent takes tests on its own, results can then be compared). No held-out period is a forecasting week,
so this is a transfer test of the *mechanism* (reading teammates' outputs switches content coupling on), not
of forecasting. Nothing about #14 beyond its goal-periods.md entry was looked at while writing this.

Pipeline (identical rules to round 1; everything automated, no hand audit):
  1. extract the period's computer-use text (scheme/extract_cu_text.main) into data/processed/H24.../confirm_G14/
  2. switch-on per agent with scheme/build.compute_switch_on (the card's rule)
  3. statements from the shared embeddings, whitened (regime I, n = 32), g-hat from goal + kickoff (same rule)
  4. C0-C3 below, with N1 (within-period placebos), N2 (the round-1 kickoff-matched placebo weeks, offset = the
     period's median tau_i offset), N3 (per-agent rotations)

Usage:
  dry run on a non-holdout period (pipeline check; allowed):
     uv run --offline --with sentence-transformers python hypotheses/H24-forecast-coupling-switch/analysis/confirm.py --dry-run 21
  the real run (needs Vivian's sign-off; refuses otherwise):
     uv run --offline --with sentence-transformers python hypotheses/H24-forecast-coupling-switch/analysis/confirm.py \
         --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

import numpy as np
import polars as pl
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "scheme"))
from h24lib import H24, CARD, mention_regexes, unit  # noqa: E402
from h24stats import seg_alignment, segments, random_rotations  # noqa: E402
from common import OUT, load_goals, load_holdout, load_whitener, holdout_mask  # noqa: E402

TARGET = 14
K, B, POST = 4, 200, 60.0
SHIFTS = (60.0, 90.0, 120.0)
SEED = 20261003

PREDICTIONS = {
    "written": "2026-10-03, after exploratory round 1 on #21 (where P1 failed, the levels were high from the first hour, "
               "and the ramp rose); before any look at #14 data",
    "C0_switch_exists": {"rule": ">= 4 agents (and >= 2/3 of those present on day 1) have tau_i on the first active day",
                         "credence": 0.5, "if_false": "H24 is not applicable to #14; C1 not evaluated; C2/C3 still reported"},
    "C1_step": {"rule": "dA_res (all statements, k=4, 60-min post) > q90 of N1 AND > q90 of N2",
                "H24_predicts": "pass", "my_credence_pass": 0.2,
                "verdicts": {"pass": "H24 step transfers (revives it)", "fail": "H24 step refuted in transfer (if C0 holds)"}},
    "C2_level": {"rule": "A_res in the pre-switch segment > q95 of the per-agent rotation null (N3)",
                 "credence": 0.85, "meaning": "content is aligned before any document coupling (field or chat)"},
    "C3_ramp": {"rule": "Spearman rho of A_res over 2-h blocks after day-1 block 0 > 0 (H24' ramp)", "credence": 0.55},
    "power_note": "#14 has N = 6 (vs 7 switched agents in #21); the #21 synthetic gives power >= 0.5 only for true "
                  "post-switch betaJ0/n >= ~0.45, so a C1 failure at N = 6 is weak evidence",
}


def period_bounds(goal):
    cal = pl.read_parquet(OUT / "calendar.parquet").filter(pl.col("goal_no") == goal).sort("pt_date")
    return cal


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--dry-run", type=int, default=None, help="run the pipeline on a non-holdout goal period instead")
    a = ap.parse_args()
    held = set(load_holdout()["goal_periods_held_out"])
    if a.dry_run is not None:
        goal = a.dry_run
        if goal in held:
            sys.exit(f"--dry-run {goal}: that period is in the locked holdout; refusing.")
        tag = f"dryrun_G{goal}"
    else:
        goal = TARGET
        if not (a.confirm and a.ack):
            sys.exit("This uses the locked holdout (#14). Refusing without --confirm --i-understand-this-uses-the-locked-holdout "
                     "(and Vivian's sign-off, logged in LOG.md).")
        assert goal in held
        tag = f"confirm_G{goal}"
    dest = H24 / tag
    dest.mkdir(parents=True, exist_ok=True)
    cal = period_bounds(goal)
    days = cal["pt_date"].to_list()
    win0, win_end = cal["win_start"][0], cal["win_end"][-1]
    if a.dry_run is not None:
        assert not any(holdout_mask(days, [goal] * len(days)))
    rng = np.random.default_rng(SEED)

    # 1. computer-use text
    import extract_cu_text
    if not (dest / "cu_turns_text.parquet").exists():
        extract_cu_text.main(win0 - dt.timedelta(hours=1), win_end + dt.timedelta(minutes=5), dest)
    cu = pl.read_parquet(dest / "cu_turns_text.parquet")

    # 2. switch-on
    from build import compute_switch_on, embed
    roster = pl.read_parquet(OUT / "roster.parquet")
    names = dict(zip(roster["agent"].to_list(), roster["name"].to_list()))
    pats = mention_regexes([{"id": x, "name": n} for x, n in zip(roster["agent"].to_list(), roster["name"].to_list())])
    st = pl.read_parquet(OUT / "embeddings/statements.parquet").filter(pl.col("goal_no") == goal) \
           .join(roster.select("agent", "claude_code"), on="agent").filter(~pl.col("claude_code")).drop("claude_code").sort("t")
    present = sorted(st["agent"].unique().to_list())
    sw = compute_switch_on(goal, cu, win0, win_end, present, names, pats, st)
    sw.write_parquet(dest / "switch_on.parquet")
    day1_present = sorted(st.filter(pl.col("pt_date") == days[0])["agent"].unique().to_list())
    switched = sw.filter(pl.col("role") == "switched", pl.col("agent").is_in(day1_present))["agent"].to_list()
    tau = dict(zip(sw["agent"].to_list(), sw["tau_offset_min"].to_list()))
    out = {"goal_no": goal, "tag": tag, "predictions": PREDICTIONS, "present": present, "day1_present": day1_present,
           "switched": switched, "switch_on": sw.select("agent", "rule", "role", "tau_offset_min").to_dicts()}
    C0 = len(switched) >= 4 and len(switched) >= (2 / 3) * len(day1_present)
    out["C0"] = {"pass": bool(C0), "n_switched": len(switched), "n_day1": len(day1_present)}

    # 3. statements, whitening, g-hat
    kind = st["kind"].to_numpy(); src = st["src_row"].to_numpy()
    Ec = np.load(OUT / "embeddings/chat_bge_small.npy", mmap_mode="r"); Ei = np.load(OUT / "embeddings/intentions_bge_small.npy", mmap_mode="r")
    E = np.empty((st.height, 384), dtype=np.float32); m = kind == "chat"; E[m] = Ec[src[m]]; E[~m] = Ei[src[~m]]
    W = load_whitener("I", 32)
    Z = unit(W(E).astype(np.float64))
    g = [x for x in load_goals() if x["goal_no"] == goal][0]
    ctext = pl.read_parquet(OUT / "chat_text.parquet", columns=["message_id", "text"])
    hum = pl.read_parquet(OUT / "chat_core.parquet", columns=["message_id", "t", "speaker_kind"]) \
            .filter(pl.col("speaker_kind") == "human", pl.col("t") >= win0 - dt.timedelta(minutes=10),
                    pl.col("t") <= win0 + dt.timedelta(minutes=45)).join(ctext, on="message_id")
    kick = [s for k in hum["text"].to_list() if len(k) >= 250 for s in re.split(r"(?<=[.!?])\s+", k)
            if not re.search(r"(?i)(previous goal|last (two )?weeks?'? goal|to a close|archived|reflect on how it went)", s)]
    Eg = embed([g["goal"]] + ([" ".join(kick)] if kick else []))
    Wg = unit(W(Eg).astype(np.float64))
    ghat = unit(Wg.sum(0)) if len(Wg) > 1 else Wg[0]
    from h24stats import project_out
    Zr = unit(project_out(Z, ghat[None]))
    opens = dict(zip(cal["pt_date"].to_list(), cal["win_start"].to_list()))
    mins = np.array([(t - opens[d]).total_seconds() / 60 for t, d in zip(st["t"].to_list(), st["pt_date"].to_list())])
    agents = st["agent"].to_numpy(); pdays = np.array(st["pt_date"].to_list())

    def o1(ZZ, taus, day):
        pre, post = segments(np.where(pdays == day, mins, np.nan), agents, switched, taus, POST)
        return seg_alignment(ZZ, pre, post, K, B, rng)

    if switched:
        tau_sw = {x: tau[x] for x in switched}
        tau_star = float(np.median(list(tau_sw.values())))
        r = o1(Zr, tau_sw, days[0])
        out["tau_star_min"] = tau_star
        if r is not None:
            plac = [o1(Zr, {x: tau_sw[x] + s for x in switched}, days[0]) for s in SHIFTS] + [o1(Zr, tau_sw, d) for d in days[1:]]
            n1 = [p["dA"] for p in plac if p]
            sys.path.insert(0, str(HERE))
            from explore import placebo_N2
            n2 = [w["res"]["dA"] for w in placebo_N2(32, K, rng, tau_star)]
            lv = []
            for rep in range(25):
                rots = random_rotations(32, len(switched), rng)
                ZR = Zr.copy()
                for x, Q in zip(switched, rots):
                    ZR[agents == x] = Zr[agents == x] @ Q
                q = o1(ZR, tau_sw, days[0])
                if q:
                    lv.append(q["A_pre"])
            out["C1"] = {"dA_res": r["dA"], "A_pre": r["A_pre"], "A_post": r["A_post"], "N1": n1,
                         "N1_q90": float(np.quantile(n1, 0.9)) if n1 else None, "N2_q90": float(np.quantile(n2, 0.9)), "N2_n": len(n2),
                         "pass": bool(C0 and n1 and r["dA"] > np.quantile(n1, 0.9) and r["dA"] > np.quantile(n2, 0.9)),
                         "evaluated": bool(C0)}
            out["C2"] = {"A_pre_res": r["A_pre"], "rot_q95": float(np.quantile(lv, 0.95)),
                         "pass": bool(r["A_pre"] > np.quantile(lv, 0.95))}
    # C3 ramp
    blk = np.array([int(mm // 120) for mm in mins])
    rows = []
    for bi, d in enumerate(days):
        for b in (0, 1):
            sel = (pdays == d) & (blk == b)
            groups = [np.flatnonzero(sel & (agents == x)) for x in sorted(set(agents[sel].tolist()))]
            groups = [gg for gg in groups if len(gg) >= K]
            if len(groups) < 3 or (bi == 0 and b == 0):
                continue
            vals = []
            for _ in range(B):
                V = np.array([unit(Zr[rng.choice(gg, K, replace=False)].mean(0)) for gg in groups])
                C = V @ V.T; n = len(V); vals.append((C.sum() - n) / (n * (n - 1)))
            rows.append({"idx": 2 * bi + b, "A_res": float(np.mean(vals)), "N": len(groups)})
    if len(rows) >= 4:
        rho, p = stats.spearmanr([x["idx"] for x in rows], [x["A_res"] for x in rows])
        out["C3"] = {"rho": float(rho), "p": float(p), "blocks": rows, "pass": bool(rho > 0)}
    (dest / "confirm_results.json").write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps({k: out.get(k) for k in ("C0", "C1", "C2", "C3")}, indent=1, default=str)[:3000])


if __name__ == "__main__":
    main()
