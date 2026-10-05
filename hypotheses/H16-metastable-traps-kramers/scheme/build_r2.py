"""H16 round 2 scheme: context composition at every regime-III call, gate rows with composition, TS1r spell kinds.

Outputs (data/processed/H16-metastable-traps-kramers/r2/; codes and numbers only, no text):
  ruler.json           lab token ruler (own prompt growth per idle / active call, prompt at ctx_pos 1; H45 room ruler)
  calls_comp.parquet   one row per regime-III non-reserved cu call: segment, n_rep, n_act, k_ctx, urn shares
  gates_r2.parquet     shared idle_gates rows (regime III; G51 before 09-03) + composition at the gate and at the idle
                       call before it, reset flags, trap kind (what the last active call before the trap was)
  ts1r_kinds.parquet   r1b TS1r spells of the 11 H16 periods + kind at spell start (consol: a consolidation call starts
                       within 60 s; else the declared idle in the first 180 s: pause / wait / silent; and what the last
                       active row was: real failure, talk, other)
Reserved data: ledger rows with holdout = True and common.holdout_mask rows are dropped and asserted absent.
Usage: uv run python hypotheses/H16-metastable-traps-kramers/scheme/build_r2.py
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt
import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent / "analysis"))
sys.path.insert(0, str(ROOT / "infra/shared"))
import r2lib as R  # noqa: E402
from common import holdout_mask  # noqa: E402

SH = R.SH
OUTD = R.R2
PERIODS = ["G27", "G30", "G31", "G37", "G38", "G39", "G40", "G41", "G42", "G44", "G51"]
DECL_S = 180.0
FAIL_WIN_S = 5.0
PLATFORM_FAIL = ["timeout", "vm", "resource", "network", "tool_use", "other"]


def log(t0, *a):
    print(f"[{time.time() - t0:6.1f}s]", *a, flush=True)


def load_calls() -> pl.DataFrame:
    t = pl.read_parquet(SH / "context_ledger_turns.parquet",
                        columns=["turn_id", "agent", "pt_date", "goal_no", "regime", "holdout", "t_call", "kind", "talk",
                                 "ctx_mode", "k_new", "chars_new", "n_ev", "k_ctx", "ctx_pos", "reset_consol",
                                 "reset_forced", "reset_session", "first_of_day"])
    t = t.filter((pl.col("regime").cast(pl.Utf8) == "III") & ~pl.col("holdout") & (pl.col("ctx_mode").cast(pl.Utf8) == "cu"))
    hm = np.array(holdout_mask(t["pt_date"].to_list(), t["goal_no"].to_list()))
    t = t.filter(pl.Series(~hm))
    ros = pl.read_parquet(SH / "roster.parquet").filter(~pl.col("claude_code")).select("agent", "lab", "model_string")
    t = t.join(ros, on="agent", how="inner")
    t = t.with_columns(n_oev=(pl.col("n_ev") - pl.col("k_new")).clip(0, None))
    p = pl.read_parquet(ROOT / "data/processed/H45-context-homeostasis/calls.parquet", columns=["turn_id", "P"])
    return t.join(p, on="turn_id", how="left")


def last_active_kind(comp: pl.DataFrame) -> pl.DataFrame:
    """For each call: turn_id of the latest earlier active (non-idle) call of the agent, its talk flag and failure."""
    fl = pl.read_parquet(SH / "calls.parquet", columns=["turn_id", "fail"])
    c = comp.select("turn_id", "agent", "t_call", "idle", "talk").sort("agent", "t_call", "turn_id").join(fl, on="turn_id", how="left")
    c = c.with_columns(
        la_tid=pl.when(~pl.col("idle")).then(pl.col("turn_id")).otherwise(None),
        la_talk=pl.when(~pl.col("idle")).then(pl.col("talk")).otherwise(None),
        la_fail=pl.when(~pl.col("idle")).then(pl.col("fail").fill_null(0) > 0).otherwise(None))
    c = c.with_columns([pl.col(x).shift(1).forward_fill().over("agent").alias(x) for x in ("la_tid", "la_talk", "la_fail")])
    return c.select("turn_id", "la_tid", "la_talk", "la_fail")


def build_gates(comp: pl.DataFrame) -> pl.DataFrame:
    g = pl.read_parquet(SH / "idle_gates/idle_gates.parquet").filter(pl.col("regime") == "III")
    g = g.filter((pl.col("goal_no") != 51) | (pl.col("pt_date") < R.G51_END))
    hm = np.array(holdout_mask(g["pt_date"].to_list(), g["goal_no"].to_list()))
    assert not hm.any(), "reserved rows in idle_gates"
    cols = ["turn_id", "seg", "ctx_pos", "reset_forced", "reset_consol", "reset_session", "n_rep", "n_act", "kc", "k_new",
            "chars_new", "f_tok", "f_tokP", "f_call", "f_entry", "f_rec", "f_tok_pre", "f_entry_pre", "P", "P_hat", "model_string"]
    cc = comp.sort("agent", "t_call", "turn_id")
    prev = cc.select("agent", "turn_id", *[pl.col(x).shift(1).over("agent").alias(f"{x}_prev") for x in
                                           ("turn_id", "seg", "n_rep", "n_act", "kc", "f_tok", "f_call", "f_entry", "f_rec", "idle")])
    g = g.join(comp.select(cols), on="turn_id", how="left").join(prev.drop("agent"), on="turn_id", how="left")
    g = g.join(last_active_kind(comp), on="turn_id", how="left")
    # composition at the end of the old segment (the idle call before the gate, plus that call itself)
    g = g.with_columns(
        reset_at_gate=(pl.col("seg") != pl.col("seg_prev")).fill_null(False),
        trap_kind=pl.when(pl.col("la_fail")).then(pl.lit("after_fail"))
        .when(pl.col("la_talk")).then(pl.lit("after_talk")).otherwise(pl.lit("after_work")),
    )
    # resets since the trap started: count segment changes between the last active call and the gate
    return g


def ts1r_kinds() -> pl.DataFrame:
    """Kind at spell start for the r1b TS1r spells: declared idle in [t0, t0 + 180 s] and the last active row."""
    frames = []
    for p in PERIODS:
        d = pl.read_parquet(R.OUT / "r1b" / p / "ts1r.parquet").with_columns(pl.lit(p).alias("period"))
        frames.append(d)
    ts = pl.concat(frames, how="diagonal")
    days = ts["pt_date"].unique().to_list()
    ev = (pl.read_parquet(SH / "events_core.parquet", columns=["t", "pt_date", "actor_kind", "agent", "action_type"])
          .filter((pl.col("actor_kind") == "agent") & pl.col("pt_date").is_in(days))
          .with_columns(k=pl.col("action_type").cast(pl.Utf8), ts=pl.col("t").dt.epoch("us") / 1e6))
    pz = ev.filter(pl.col("k").is_in(["PAUSE", "WAIT"])).select("agent", "ts", "k").sort("agent", "ts")
    talk = ev.filter(pl.col("k") == "AGENT_TALK").select("agent", "ts").sort("agent", "ts")
    cons = ev.filter(pl.col("k") == "CONSOLIDATE").select("agent", "ts").sort("agent", "ts")
    a = pl.read_parquet(SH / "actions.parquet", columns=["t", "agent", "action"]).with_row_index("row")
    b = pl.read_parquet(SH / "actions_bash_head_fixed.parquet", columns=["row", "error_class"])
    a = (a.join(b, on="row", how="left").filter(pl.col("agent").is_not_null())
         .with_columns(pt_date=pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8))
         .filter(pl.col("pt_date").is_in(days)))
    to = pl.read_parquet(ROOT / "data/processed/behavior_states/turn_outcomes.parquet", columns=["t", "agent", "failed"]).unique(["agent", "t"], keep="first")
    a = a.join(to, on=["agent", "t"], how="left").with_columns(
        fail=pl.when(pl.col("action").cast(pl.Utf8).is_in(["bash", "type"])).then(pl.col("failed").fill_null(False))
        .otherwise(pl.col("error_class").cast(pl.Utf8).is_in(PLATFORM_FAIL).fill_null(False)),
        ts=pl.col("t").dt.epoch("us") / 1e6)
    fails = a.filter(pl.col("fail")).select("agent", "ts").sort("agent", "ts")

    def by_agent(df):
        return {int(k[0]): g["ts"].to_numpy() for k, g in df.group_by("agent")}
    PZ = {int(k[0]): (g["ts"].to_numpy(), g["k"].to_numpy()) for k, g in pz.group_by("agent")}
    TK, FL, CN = by_agent(talk), by_agent(fails), by_agent(cons)
    sm = (pl.read_parquet(SH / "context_ledger_turns.parquet", columns=["agent", "t_call", "ctx_mode", "pt_date"])
          .filter((pl.col("ctx_mode").cast(pl.Utf8) == "summary") & pl.col("pt_date").is_in(days))
          .with_columns(ts=pl.col("t_call").dt.epoch("us") / 1e6))
    SM = by_agent(sm.sort("agent", "ts"))
    ag = ts["agent"].to_numpy(); t0 = ts["t0"].to_numpy(); t1 = ts["t1"].to_numpy()
    kind = np.full(len(ag), "silent", dtype=object)
    lastk = np.full(len(ag), "work", dtype=object)
    esc_cons = np.zeros(len(ag), bool)
    consol = np.zeros(len(ag), bool)
    for a_ in np.unique(ag):
        m = np.flatnonzero(ag == a_)
        if a_ in PZ:
            pt, pk = PZ[a_]
            i = np.searchsorted(pt, t0[m], "left")
            ok = (i < len(pt))
            ii = np.minimum(i, len(pt) - 1)
            hit = ok & (pt[ii] <= t0[m] + DECL_S) & (pt[ii] < t1[m])
            kind[m[hit & (pk[ii] == "PAUSE")]] = "pause"
            kind[m[hit & (pk[ii] == "WAIT")]] = "wait"
        for arr, lab in ((TK.get(a_), "talk"), (FL.get(a_), "fail")):
            if arr is None or len(arr) == 0:
                continue
            j = np.searchsorted(arr, t0[m] + 1.0, "right") - 1
            okj = (j >= 0) & (np.abs(arr[np.maximum(j, 0)] - t0[m]) <= FAIL_WIN_S)
            lastk[m[okj]] = lab              # fail written after talk: a failure wins a tie
        if a_ in SM and len(SM[a_]):
            arr = SM[a_]
            j = np.searchsorted(arr, t0[m] - 30.0, "left")
            jj = np.minimum(j, len(arr) - 1)
            consol[m[(j < len(arr)) & (arr[jj] <= t0[m] + 60.0) & (arr[jj] < t1[m])]] = True
        if a_ in CN and len(CN[a_]):
            arr = CN[a_]
            j = np.searchsorted(arr, t1[m] - 1.0, "left")
            okc = (j < len(arr)) & (np.abs(arr[np.minimum(j, len(arr) - 1)] - t1[m]) <= 60.0)
            esc_cons[m[okc]] = True
    kind[consol] = "consol"                  # a summary (consolidation) call starts within 60 s of the spell start
    return ts.with_columns(pl.Series("kind_start", kind.astype(str)), pl.Series("last_kind", lastk.astype(str)),
                           pl.Series("end_at_consolidate", esc_cons))


def main():
    t0 = time.time()
    OUTD.mkdir(parents=True, exist_ok=True)
    calls = load_calls()
    log(t0, "calls", calls.height)
    cal = json.loads((ROOT / "data/processed/H45-context-homeostasis/calibration.json").read_text())
    calls = calls.with_columns(idle=(pl.col("kind").cast(pl.Utf8).is_in(["pause", "wait"]) & ~pl.col("talk")))
    # ruler needs segments: build them once through composition with a provisional ruler, then recompute
    prov = {k: {"tau_I": 1.0, "tau_A": 1.0, "B": 1.0, "a": 1.0, "b": 0.0, "e": 0.0} for k in ("Anthropic", "Google", "other")}
    tmp = R.composition(calls.drop("idle"), prov)
    rul = R.ruler(tmp, cal)
    R.jdump(rul, OUTD / "ruler.json")
    log(t0, "ruler", json.dumps({k: {kk: round(v, 1) for kk, v in d.items()} for k, d in rul.items()}))
    comp = R.composition(calls.drop("idle"), rul)
    keep = ["turn_id", "agent", "lab", "model_string", "pt_date", "goal_no", "t_call", "kind", "talk", "idle", "seg", "ctx_pos",
            "reset_forced", "reset_consol", "reset_session", "n_rep", "n_act", "kc", "k_new", "chars_new", "P", "P_hat",
            "f_tok", "f_tokP", "f_call", "f_entry", "f_rec", "f_tok_pre", "f_entry_pre"]
    comp = comp.select(keep)
    comp.with_columns([pl.col(c).cast(pl.Float32) for c in ("P_hat", "f_tok", "f_tokP", "f_call", "f_entry", "f_rec", "f_tok_pre", "f_entry_pre")]
                      ).write_parquet(OUTD / "calls_comp.parquet", compression="zstd")
    log(t0, "calls_comp written")
    g = build_gates(comp)
    g.write_parquet(OUTD / "gates_r2.parquet", compression="zstd")
    log(t0, "gates", g.height)
    k = ts1r_kinds()
    k.write_parquet(OUTD / "ts1r_kinds.parquet", compression="zstd")
    log(t0, "ts1r kinds", k.height)
    prov_ = {"built_by": "hypotheses/H16-metastable-traps-kramers/scheme/build_r2.py", "git_commit": _git(),
             "inputs": [{"source": "ai-village", "tables": ["context_ledger_turns", "idle_gates", "calls", "roster", "events_core",
                                                             "actions", "actions_bash_head_fixed", "turn_outcomes",
                                                             "H45 calls.parquet (P)", "H45 calibration.json", "H16 r1b ts1r"]}],
             "params": {"M_REC": R.M_REC, "F_CAP": R.F_CAP, "G51_END": R.G51_END, "DECL_S": DECL_S, "FAIL_WIN_S": FAIL_WIN_S},
             "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUTD / "_provenance.json").write_text(json.dumps(prov_, indent=1))
    log(t0, "done")


def _git():
    import subprocess
    try:
        return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
    except Exception:  # noqa: BLE001
        return "unknown"


if __name__ == "__main__":
    main()
