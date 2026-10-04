"""H69 confirmatory script (LOCKED HOLDOUT). Written 2026-10-04 after exploratory round 1. NOT RUN.

Frozen predictions (thresholds fixed from round 1, before any holdout data is loaded). Targets: the held-out regime-III
goal periods #43, #45, #46, #47, #49, #50 and the #51 tail (2026-09-07 -> 09-21). A target is scored when it has >= 30
restatement episodes (cross-call, either model, >= 2 in a row); pooled values are random-effects means over scored targets.
  C1 restatements copy what is in context: pooled in-context enrichment OR (MH, strata agent x 0.1-decade lag x
     calls-between bin) >= 1.5 with the 95% CI above 1 (round 1: 3.4 [2.6, 4.5], 4/4 periods).                      [0.85]
  C2 erasure ends loops: pooled exit OR for a forced erasure between two statements > 1 (CI above 1)
     (round 1: 2.4 [1.2, 4.9]).                                                                                        [0.6]
  C3 erasure prevents onset: pooled onset OR for a forced erasure since the previous statement < 1 (CI below 1)
     (round 1: 0.54 [0.34, 0.86]).                                                                                     [0.6]
  C4 the trigger is not the self-share: pooled b_K (room items in context, at fixed own count) has a 95% CI that
     includes 0 or lies above 0 (round 1: +0.04 [-0.17, 0.25]).                                                       [0.75]
  C5 own statements in context raise onset: pooled b_O > 0 (CI above 0) (round 1: 0.34 [0.09, 0.60]).               [0.55]
  C6 novel input does not end loops: pooled exit coefficient on log(1 + novel reads) has a 95% CI including 0
     (round 1: 0.21 [-0.16, 0.58]).                                                                                    [0.6]

Reuse disclosure (hypotheses/holdout.md policy): #43, #45-#47, #49, #50 and the #51 tail are targets of other
hypotheses' content and activity scripts (H12, H26, H47, H55, H57 among them; see infra/data-quality/holdout_ledger.json).
H69's statistics (restatement onset/exit hazards on ledger context segments; source-location enrichment) are a
different statistic from those; DQ5 flag rates per period are already published for the holdout in
statement_flags_by_period (non-holdout only). Disclose in this card, the other cards and LOG.md before running.

Safeguards:
  * refuses to run on the holdout without --confirm --i-understand-this-uses-the-locked-holdout and a passing
    holdout_ledger.check() for every target;
  * refuses unless this script, the card, h69lib.py, run_periods.py and scheme/build.py are tracked and unmodified;
  * --dry-run builds the non-holdout stand-ins (#38, #41 for the periods; #51 non-holdout for the tail) in memory into
    a scratch folder, asserts no held-out day is loaded, and checks that it reproduces run_periods' enrichment log OR
    for #38 within 0.05.

Usage: uv run python hypotheses/H69-loops-context-fixed-points/analysis/confirm.py --dry-run
       uv run python hypotheses/H69-loops-context-fixed-points/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "infra/shared"))
import h69lib as L  # noqa: E402

TARGETS = {43: None, 45: None, 46: None, 47: None, 49: None, 50: None, 51: ("2026-09-07", "2026-09-21")}
STANDINS = {38: None, 41: None, 51: ("2026-07-06", "2026-09-05")}
FILES = ["hypotheses/H69-loops-context-fixed-points/analysis/confirm.py",
         "hypotheses/H69-loops-context-fixed-points/README.md",
         "hypotheses/H69-loops-context-fixed-points/analysis/h69lib.py",
         "hypotheses/H69-loops-context-fixed-points/analysis/run_periods.py",
         "hypotheses/H69-loops-context-fixed-points/scheme/build.py"]
FROZEN = dict(C1_min_or=1.5, episodes_min=30)


def git_clean() -> bool:
    for f in FILES:
        tracked = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--error-unmatch", f], capture_output=True).returncode == 0
        dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", f], capture_output=True, text=True).stdout.strip()
        if not tracked or dirty:
            print(f"refusing: {f} is untracked or modified", file=sys.stderr)
            return False
    return True


def load_build(out_dir: Path, include_holdout: bool, windows: dict):
    """The round-1 scheme module with its day selection replaced (holdout days allowed only when confirming)."""
    spec = importlib.util.spec_from_file_location("h69build", ROOT / "hypotheses/H69-loops-context-fixed-points/scheme/build.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.OUT = out_dir
    from common import holdout_mask

    m.ALLOW_HOLDOUT = include_holdout

    def days_of(g):
        cal = pl.read_parquet(m.SH / "calendar.parquet").filter(
            (pl.col("goal_no") == g) & (pl.col("regime").cast(pl.Utf8) == "III") & (pl.col("window_s") > 0))
        d = cal["pt_date"].to_list()
        hc = cal["holdout"].to_list()
        w = windows.get(g)
        hm = holdout_mask(d, [g] * len(d))
        keep = []
        for x, h1, h2 in zip(d, hm, hc):
            if w and not (w[0] <= x < w[1]):
                continue
            held = h1 or h2
            if held == include_holdout:
                keep.append(x)
        return sorted(keep)
    m.days_of = days_of
    return m


def score(out_dir: Path, gs) -> dict:
    import run_periods as RP
    RP.D = out_dir
    per = {}
    for g in gs:
        p = f"G{g:02d}"
        if not (out_dir / p / "statements.parquet").exists():
            continue
        st = pl.read_parquet(out_dir / p / "statements.parquet")
        it = pl.read_parquet(out_dir / p / "items.parquet")
        pr = pl.read_parquet(out_dir / p / "pairs.parquet")
        tb, tg = RP.thresholds()
        pr = pr.with_columns(((pl.col("cos_bge") > tb) | (pl.col("cos_gte") > tg)).alias("y"))
        s, _ = L.prepare(st, it)
        ep = L.episodes(L.prepare(st, None)[0], "r_either")
        o = dict(episodes=ep, onset=L.onset(s), exit=L.exit_model(s), enrich=L.enrichment(pr, s, "y", B=300, seed=1))
        d0 = s.filter(pl.col("r_prev") == 0)
        if d0.height >= 50 and d0["r_either"].sum() >= 10:
            X = L._X(d0, ["forced_between", "log1p:n_prev_day", "log:lag_prev_s", "log:calls_prev", "log1p:n_read"])
            if X[:, 0].std() > 0:
                r = L.fit_logit(d0["r_either"].to_numpy().astype(float), X,
                                np.unique(d0["agent"].to_numpy(), return_inverse=True)[1], clusters=d0["aday"].to_list())
                o["onset_forced"] = dict(b=float(r["b"][0]), se=float(r["se_cl"][0]))
        o["scored"] = ep["n_episodes"] >= FROZEN["episodes_min"]
        per[p] = o

    def pool(k, b, se):
        e = [(o[k][b], o[k][se]) for o in per.values() if o["scored"] and o.get(k) and math.isfinite(o[k].get(b, np.nan))]
        return L.dl_pool([x[0] for x in e], [x[1] for x in e])
    P = dict(enrich=pool("enrich", "log_or", "se"), exit_forced=pool("exit", "b_forced_between", "se_forced_between"),
             onset_forced=pool("onset_forced", "b", "se"), b_K=pool("onset", "b_K", "se_K"),
             b_O=pool("onset", "b_O", "se_O"), nov=pool("exit", "b_nov_read", "se_nov_read"))
    C = dict(C1=P["enrich"].get("k", 0) > 0 and math.exp(P["enrich"]["mean"]) >= FROZEN["C1_min_or"] and P["enrich"]["lo"] > 0,
             C2=P["exit_forced"].get("k", 0) > 0 and P["exit_forced"]["lo"] > 0,
             C3=P["onset_forced"].get("k", 0) > 0 and P["onset_forced"]["hi"] < 0,
             C4=P["b_K"].get("k", 0) > 0 and P["b_K"]["hi"] >= 0,
             C5=P["b_O"].get("k", 0) > 0 and P["b_O"]["lo"] > 0,
             C6=P["nov"].get("k", 0) > 0 and P["nov"]["lo"] <= 0 <= P["nov"]["hi"])
    return dict(periods=per, pooled=P, verdicts=C)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    a = ap.parse_args()
    if a.dry_run:
        tmp = Path(tempfile.mkdtemp(prefix="h69_confirm_dry_"))
        m = load_build(tmp, include_holdout=False, windows=STANDINS)
        mm = m  # the round-1 builder (same code path the confirm run uses)
        emb = mm.Emb()
        meta = json.loads((mm.SH / "statement_flags_meta.json").read_text())
        thr = dict(bge=meta["thr_bge"], gte=meta["thr_gte_rate_matched"])
        stm, flags, ev, chat, kicks = _inputs(mm, include_holdout=False)
        for g in STANDINS:
            mm.build(g, emb, flags, stm, ev, chat, kicks, thr)
        from common import holdout_mask
        for g in STANDINS:
            st = pl.read_parquet(tmp / f"G{g:02d}" / "statements.parquet")
            assert not any(holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list())), "holdout day in dry run"
        res = score(tmp, STANDINS)
        ref = json.loads((ROOT / "data/processed/H69-loops-context-fixed-points/G38/results.json").read_text())
        d = abs(res["periods"]["G38"]["enrich"]["log_or"] - ref["enrich"]["log_or"])
        print(json.dumps(res["verdicts"]), "G38 enrichment reproduction |d| =", round(d, 4))
        assert d < 0.05, "dry run does not reproduce round 1"
        print("dry run OK (non-holdout stand-ins only)")
        return
    if not (a.confirm and a.ack):
        sys.exit("refusing: confirmatory run needs --confirm --i-understand-this-uses-the-locked-holdout")
    if not git_clean():
        sys.exit(1)
    import holdout_ledger as HL
    for g in TARGETS:
        t = "#51-tail" if g == 51 else f"G{g}"
        c = HL.check("H69", t, "content", ["restatement_hazard"])
        if not c["allowed"]:
            sys.exit(f"refusing: holdout ledger blocks {t}")
    out = ROOT / "data/processed/H69-loops-context-fixed-points/confirm"
    m = load_build(out, include_holdout=True, windows=TARGETS)
    emb = m.Emb()
    meta = json.loads((m.SH / "statement_flags_meta.json").read_text())
    thr = dict(bge=meta["thr_bge"], gte=meta["thr_gte_rate_matched"])
    stm, flags, ev, chat, kicks = _inputs(m, include_holdout=True)
    for g in TARGETS:
        m.build(g, emb, flags, stm, ev, chat, kicks, thr)
    res = score(out, TARGETS)
    (out / "confirm_results.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res["verdicts"], indent=1))


def _inputs(m, include_holdout: bool):
    """Same inputs as scheme/build.py main(); holdout statements kept only when confirming."""
    stm = pl.read_parquet(m.ED / "statements.parquet").with_row_index("srow").filter(
        (pl.col("kind") == "chat") & (pl.col("regime") == "III"))
    if not include_holdout:
        stm = stm.filter(~pl.col("holdout"))
    else:
        stm = stm.with_columns(pl.lit(False).alias("holdout"))
    flags = pl.read_parquet(m.SH / "statement_flags.parquet", columns=[
        "srow", "self_repeat_bge", "self_repeat_gte", "self_repeat_src_bge", "self_repeat_src_gte", "templated",
        "cross_echo", "self_repeat_cos_bge", "self_repeat_cos_gte"])
    ev = (pl.read_parquet(m.SH / "events_core.parquet", columns=["t", "message_id", "action_type"])
          .filter(pl.col("action_type") == "AGENT_TALK").select("message_id", pl.col("t").alias("t_ev")).unique("message_id"))
    ci = pl.read_parquet(m.ED / "chat_index.parquet").with_row_index("crow")
    chat = pl.read_parquet(m.SH / "chat_core.parquet", columns=["message_id", "t", "pt_date", "room", "speaker_kind", "agent",
                                                                 "length"]).join(ci, on="message_id", how="left")
    kicks = pl.read_parquet(m.SH / "kicks_classified.parquet", columns=["message_id", "kind"]).filter(
        pl.col("message_id").is_not_null()).unique("message_id")
    return stm, flags, ev, chat, kicks


if __name__ == "__main__":
    main()
