"""H32 confirmatory test on the locked holdout (written 2026-10-03 after exploratory round 1; NOT RUN).

Targets (held out, never examined by H32): #28 (mode C, regime I, 11 agents), #22 (mode F, regime I), #14 (mode I,
regime I). #45 is refused: H02 used its timing and H23 has reserved its message content (same modality as H32), so a
#45 leader test needs Vivian's decision under the reuse policy in hypotheses/holdout.md and a card amendment.

Pipeline: identical to round 1's primary (ic_core, frozen parameters P, K = 5 field subspace with the goal text and
per-room kickoffs from the shared goal-field table, whose held-out rows are used only under --confirm; cross-day null
N1 with 40 replicas plus the within-day null N1w with 20). Post-hoc A2 settings are NOT used (reported as secondary).

Modes:
  default / --dry-run   run the identical pipeline on the non-holdout stand-ins (#30 for #28, #16 for #22, #17 for #14),
                        built into data/processed/H32-information-current-leaders/confirm_dryrun/
  --confirm --i-understand-this-uses-the-locked-holdout
                        build the three held-out periods into .../confirm/ and evaluate the FROZEN predictions.
                        Refuses unless this script and the card are committed and unmodified.

Usage: uv run python hypotheses/H32-information-current-leaders/analysis/confirm.py [--dry-run]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import build as B  # noqa: E402
import ic_core as C  # noqa: E402
from common import holdout_mask, load_holdout  # noqa: E402

TARGETS = {28: 30, 22: 16, 14: 17}   # held-out target -> non-holdout stand-in (same regime; mode C->C, F->F, I->I)
CARD = HERE.parent / "README.md"

# Frozen predictions (written 2026-10-03 after round 1 on 32 non-holdout periods, before any look at #14/#22/#28).
# Round-1 basis: regime-I transfer significant in 7/9 mode-C, 1/5 mode-F, 1/4 mode-I periods; leader called in 2/18
# transfer periods; split-half rho > 0 in 23/26; humans above the median agent in 4/16 (only the viewer-heavy #3-#6);
# top source in late regime I usually Claude Opus 4.5 or GPT-5.2.
FROZEN = {
    "C1_transfer_28": "#28 (mode C): T > 0 against the cross-day null at p_T < 0.05 [credence 0.75]",
    "C2_transfer_IF": "#22 (mode F) and #14 (mode I): p_T >= 0.05 in at least one of the two [0.7]",
    "C3_no_leader": "a leader is called (standout p < 0.05 and max p < 0.05) in at most 1 of the 3 targets [0.8]",
    "C4_stability_28": "#28 split-half Spearman rho(Out_odd, Out_even) > 0 [0.75]",
    "C5_mode": "T(#28) > T(#22) and T(#28) > T(#14) [0.55]",
    "C6_both_nulls_28": "#28 T significant under both N1 and N1w [0.6]",
    "C7_identity_28": "#28's top source by Out is Claude Opus 4.5 or GPT-5.2 [0.5]",
    "C8_humans_28": "if #28 has >= 15 human messages: the human pseudo-agent's Out is NOT above the median agent's [0.7]",
}


def committed_and_clean(paths) -> bool:
    for p in paths:
        r = subprocess.run(["git", "-C", str(C.ROOT), "status", "--porcelain", "--", str(p)], capture_output=True, text=True)
        if r.stdout.strip():
            return False
        r = subprocess.run(["git", "-C", str(C.ROOT), "ls-files", "--error-unmatch", str(p)], capture_output=True, text=True)
        if r.returncode != 0:
            return False
    return True


def build(goals, out_dir: Path, allow_holdout: bool):
    cal = pl.read_parquet(C.SH / "calendar.parquet").with_columns(pl.col("regime").cast(pl.String))
    hm = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    cal = cal.with_columns(pl.Series("hm", hm)).filter(pl.col("goal_no").is_in(goals))
    held = cal.filter(pl.col("holdout") | pl.col("hm"))
    if not allow_holdout:
        assert held.height == 0, "dry run touched a held-out day"
    else:
        h = load_holdout()
        assert set(goals) <= set(h["goal_periods_held_out"]), "confirm mode only targets held-out goal periods"
        assert 45 not in goals, "#45 is refused (reuse policy)"
    cal = cal.drop("hm")
    cc = B.chat_table(cal)
    per = B.select_periods(cal, cc)
    missing = set(goals) - set(per["goal_no"].to_list())
    if missing:
        print("periods failing the data rule (reported as n/a):", sorted(missing))
    gs = per["goal_no"].to_list()
    B.assemble(gs, cal, cc, per, out_dir, with_text_fields=True, allow_holdout_fields=allow_holdout)
    return gs


def evaluate(g, base: Path, allow_holdout: bool):
    sk = C.load_period(g, allow_holdout=allow_holdout, base=base, text_fields=True)
    r = C.run_unit(sk, n_null=C.P["n_null"], seed=C.SEED + g, do_human=True, n_withinday=20)
    ro = pl.read_parquet(C.SH / "roster.parquet")
    names = dict(zip(ro["agent"].to_list(), ro["name"].to_list()))
    top = r["nodes"][int(np.nanargmax(r["out"]))]
    out = {"goal_no": g, "T": r["T"], "p_T": r["p_T"], "p_T_withinday": r["withinday"]["p_T"], "T_trim": r["T_trim"],
           "p_T_trim": r["p_T_trim"], "standout": r["standout"], "p_standout": r["p_standout"], "p_max": r["p_max"],
           "phi": r["cent_nullvar"]["phi"], "nodes": r["nodes"], "out": r["out"].tolist(), "top": int(top),
           "top_name": names.get(top), "n_human": int((sk.spk == C.HUMAN).sum())}
    if "human" in r and np.isfinite(r["human"]["out"]):
        out["human_above_median"] = bool(r["human"]["out"] > np.nanmedian(r["out"]))
    D = sorted(set(int(x) for x in sk.day))
    if len(D) >= 4 and len(r["nodes"]) >= 6:
        ro = C.run_unit(sk.subset_days([d for d in D if d % 2]), n_null=20, seed=C.SEED + g + 1, do_human=False)
        re_ = C.run_unit(sk.subset_days([d for d in D if not d % 2]), n_null=20, seed=C.SEED + g + 2, do_human=False)
        oo, ee = dict(zip(ro["nodes"], ro["out"])), dict(zip(re_["nodes"], re_["out"]))
        com = [a for a in r["nodes"] if a in oo and a in ee]
        from scipy.stats import spearmanr
        out["split_half_rho"] = float(spearmanr([oo[a] for a in com], [ee[a] for a in com]).statistic)
    return out


def verdicts(res: dict, order: list[int]) -> dict:
    """order = [mode-C target, mode-F target, mode-I target] (or their stand-ins)."""
    c, f, i = order
    v = {}
    v["C1_transfer_28"] = bool(c in res and res[c]["p_T"] < 0.05)
    v["C2_transfer_IF"] = bool(any(g in res and res[g]["p_T"] >= 0.05 for g in (f, i)))
    v["C3_no_leader"] = sum(res[g]["p_standout"] < 0.05 and res[g]["p_max"] < 0.05 for g in order if g in res) <= 1
    v["C4_stability_28"] = (res[c].get("split_half_rho", np.nan) > 0) if c in res and "split_half_rho" in res[c] else "n/a"
    v["C5_mode"] = bool(all(g in res for g in order) and res[c]["T"] > res[f]["T"] and res[c]["T"] > res[i]["T"])
    v["C6_both_nulls_28"] = bool(c in res and res[c]["p_T"] < 0.05 and res[c]["p_T_withinday"] < 0.05)
    v["C7_identity_28"] = bool(c in res and res[c]["top_name"] in ("Claude Opus 4.5", "GPT-5.2"))
    if c in res and res[c]["n_human"] >= 15 and "human_above_median" in res[c]:
        v["C8_humans_28"] = not res[c]["human_above_median"]
    else:
        v["C8_humans_28"] = "n/a"
    return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    a = ap.parse_args()
    if a.confirm and not a.ack:
        raise SystemExit("refusing: --confirm needs --i-understand-this-uses-the-locked-holdout")
    if a.ack and not a.confirm:
        raise SystemExit("refusing: the acknowledgement flag alone does nothing; pass --confirm too")
    confirm = a.confirm and a.ack and not a.dry_run
    if confirm:
        if not committed_and_clean([Path(__file__).resolve(), CARD]):
            raise SystemExit("refusing: commit this script and the card (unmodified) before the confirmatory run")
        goals, base = list(TARGETS), C.DATA / "confirm"
    else:
        goals, base = list(TARGETS.values()), C.DATA / "confirm_dryrun"
        h = load_holdout()
        assert not set(goals) & set(h["goal_periods_held_out"]), "stand-ins must be non-holdout"
    built = build(goals, base, allow_holdout=confirm)
    res = {g: evaluate(g, base, allow_holdout=confirm) for g in built}
    out = {"mode": "confirm" if confirm else "dry_run", "run_at": dt.datetime.now(dt.timezone.utc).isoformat(),
           "frozen": FROZEN, "results": res, "verdicts": verdicts(res, goals)}
    name = "confirm_result.json" if confirm else "confirm_dryrun_result.json"
    (C.DATA / name).write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out["verdicts"], indent=1, default=str))
    for g in goals:
        if g in res:
            print(g, f"T={res[g]['T'] * 100:.3f}% p={res[g]['p_T']:.3f} standout p={res[g]['p_standout']:.3f}")


if __name__ == "__main__":
    main()
