"""H25 CONFIRMATORY test on the LOCKED HOLDOUT -- ROUND-1B RE-FREEZE of `confirm.py`. Written 2026-10-04 after round 1b,
before any holdout outcome was computed. NOT RUN. `confirm.py` stays byte-for-byte unchanged (holdout ledger item 8:
its Stage B lacks the trimmed variants).

Design as confirm.py (Stage A content on #1, #9, #14, #15, #22, #43; Stage B activity/talk day-level statistics on the
same periods, gated on H19's confirmatory score), with the inputs switched (H25_DATA_VERSION=fixed, set below):
  Stage B  spins from activity_bins_fixed; the DQ8 design: the `trim` variant (auto stall mask AND the all-present
           window, applied before the block-shift null is drawn; explore.run_binary_variants, imported unchanged).
           The round-1 `auto` variant is reported next to it.
  Stage A  content dial F2 in TWO embedding models:
             bge  primary, the frozen pipeline (scheme/build.build_statements: H12 near-copy rule, cos > 0.95 within
                  agent-day on raw bge) so that the frozen CA thresholds and the measurement come from the same
                  pipeline; a bge variant deduplicated with DQ5 `statement_flags.self_repeat` is reported;
             gte  gte-modernbert vectors (shared), whitened with the gte regime whitener, deduplicated with DQ5's
                  rate-matched `self_repeat_gte`.
  The gate now also accepts H19's round-1b confirmatory score (r1b/confirm_r1b/score.json).
  Context-ledger visibility, the work ledger, failures and nudge targets are not inputs of this design.

Re-frozen predictions (r1b/results/frozen_confirm_r1b.json, written by --dry-run from EXPLORATORY round-1b outputs
only if absent; sha256 fixed below; --confirm refuses on any mismatch):
  CA1-CA4  unchanged rules and values (content point estimates are identical in round 1b), scored on bge.
  CA5-r1b  (new) model agreement: |median g_gte - median g_bge| <= 0.15 (CA4's tolerance) in >= min(4, n) held-out
           periods. Content claims count as confirmed only if CA1-CA4 pass on bge AND CA5-r1b holds. Reason: DQ5 /
           Standards section 2 (report content with both models); no gte exploratory baseline exists, so gte enters as
           an agreement clause, not with its own thresholds.
  CB1-r1b  activity and talk dials (trim) with upper bound < 0.8 on >= 95% of held-out days. Reason: Stage B now on
           the DQ8 design (round 1b: 100% of exploratory days on both designs).
  CB2-r1b  share of held-out periods (>= 5 days) with Cochran's Q p < 0.05 for the activity dial (trim) within +-0.25 of
           the exploratory trim share. Reason: the frozen share came from the buggy table and the untrimmed variant.
  CB3-r1b  (new) day-edge field vs coupling: share of held-out days above the trimmed per-day null q95 is at least 0.10
           higher for talk than for activity, and the activity share lies within +-0.20 of its exploratory value
           (round 1b: activity 24%, talk 53%). Reason: round 1b showed most apparent activity feedback is day-edge
           synchrony while talk survives trimming.
Stage B stays GATED: it runs only after H19's confirmatory score exists, and scores only day-level statistics H19
does not compute (per-day subcriticality, within-period heterogeneity, the null-ceiling shares).

Holdout reuse (infra/shared/holdout_ledger.check() before any confirm computation): no executed run on #1, #9, #14,
#15, #22, #43. Planned same-family users: H19 and H38 (equal-time gains), H12 (#28/#29, not targeted here), content
users H20 (#1 aging), H24 (#14), H12 C7 (#22 participation ratio). Disclose in both cards and LOG.md.

Usage:
  uv run python hypotheses/H25-criticality-dial/analysis/confirm_r1b.py --dry-run
  uv run python hypotheses/H25-criticality-dial/analysis/confirm_r1b.py --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import os

os.environ["H25_DATA_VERSION"] = "fixed"
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2"
os.environ.setdefault("POLARS_MAX_THREADS", "2")

import hashlib  # noqa: E402
import json  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h25common as C  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import dial as D  # noqa: E402
import confirm as CF  # noqa: E402  (frozen calendar_for / content_stage / score helpers; main() is not called)
import explore as X  # noqa: E402  (run_binary_variants: the trim variant, unchanged)

sys.path.insert(0, str(C.ROOT / "infra/shared"))
import embed_models as EM  # noqa: E402

assert C.DATA_VERSION == "fixed"
FLAGS = ("--confirm", "--i-understand-this-uses-the-locked-holdout")
STAGE_A = [1, 9, 14, 15, 22, 43]
STAGE_B = [1, 9, 14, 15, 22, 43]
DRY_A, DRY_B = [24, 27, 41], [23, 42]
FROZEN = C.RESD / "results/frozen_confirm_r1b.json"
FROZEN_SHA = "63ec9a27fa8454ba597a7f42cf59244b04fafe380b88bd5f032b218b90065bdc"   # fixed 2026-10-04 after the dry-run freeze (exploratory data only)
H19_SCORES = [C.PROC / "H19-loop-gain-collapse/confirm/score.json",
              C.PROC / "H19-loop-gain-collapse/r1b/confirm_r1b/score.json"]
LEDGER_TARGETS = ["G01", "G09", "G14", "G15", "G22", "G43"]


def freeze():
    """Frozen values from the round-1b exploratory outputs (non-holdout only)."""
    if FROZEN.exists():
        return
    per = pl.read_parquet(C.RESD / "dial_period.parquet")
    daily = pl.read_parquet(C.RESD / "dial_daily.parquet")
    C.assert_no_holdout(daily["pt_date"], daily["goal_no"])
    c = per.filter((pl.col("channel") == "content") & (pl.col("variant") == "F2"))
    cd = daily.filter((pl.col("channel") == "content") & (pl.col("variant") == "F2") & (pl.col("flag") == "ok"))
    a = per.filter((pl.col("channel") == "activity") & (pl.col("variant") == "trim") & (pl.col("k") >= 5))
    bd = daily.filter(pl.col("channel").is_in(["activity", "talk"]) & (pl.col("variant") == "trim") & (pl.col("flag") == "ok"))
    above = {ch: float((d["g"] > d["null_q95"]).mean()) for ch in ("activity", "talk")
             for d in [bd.filter((pl.col("channel") == ch) & pl.col("null_q95").is_not_null())]}
    fz = {"written_from": "exploratory round 1b (non-holdout only; activity_bins_fixed; trim variant for Stage B)",
          "CA1_range": [float(c["median"].quantile(0.05)), float(c["median"].quantile(0.95))],
          "CA2_share_hi_lt_08": float((cd["hi"] < 0.8).mean()),
          "CA3_share_above_null": float((cd["g"] > cd["null_q95"]).mean()),
          "CA4_rho": float(cd.with_columns(((pl.col("VR") - 1) / (pl.col("N") - 1)).alias("r"))["r"].median()),
          "CA4_const": float(c["median"].median()), "CA4_tol": 0.15, "CA5_tol": 0.15,
          "CB1_threshold": 0.95, "CB1_exploratory_share_trim": float((bd["hi"] < 0.8).mean()),
          "CB2_share_Q_sig_trim": float((a["p_Q"] < 0.05).mean()) if a.height else None,
          "CB3_share_above_null_trim": above, "CB3_min_talk_minus_activity": 0.10, "CB3_tol_activity": 0.20,
          "stage_a_periods": STAGE_A, "stage_b_periods": STAGE_B}
    txt = json.dumps(fz, indent=1)
    FROZEN.parent.mkdir(parents=True, exist_ok=True)
    FROZEN.write_text(txt)
    FROZEN.with_suffix(".sha256").write_text(hashlib.sha256(txt.encode()).hexdigest() + "\n")


def load_frozen(confirm: bool) -> dict:
    txt = FROZEN.read_text()
    h = hashlib.sha256(txt.encode()).hexdigest()
    if confirm and (FROZEN_SHA is None or h != FROZEN_SHA):
        sys.exit("frozen predictions missing their fixed hash or changed; refusing to run")
    return json.loads(txt) | {"_sha256": h}


def statements_model(cal: pl.DataFrame, model: str, flagcol: str):
    """Chat statements of the days in `cal` with `model` vectors (regime-whitened, 32-d, unit), DQ5 flag dedupe."""
    days = cal["pt_date"].to_list()
    raw = np.load(C.SHARED / f"embeddings/chat_{EM.MODELS[model]['suffix']}.npy", mmap_mode="r")
    st = (pl.read_parquet(C.SHARED / "embeddings/statements.parquet").with_row_index("srow")
          .filter((pl.col("kind") == "chat") & pl.col("pt_date").is_in(days) & pl.col("agent").is_not_null())
          .join(cal.select("pt_date", "win_start", "goal_no", "regime"), on="pt_date", suffix="_cal")
          .with_columns(((pl.col("t") - pl.col("win_start")).dt.total_seconds() / 60).alias("minute"))
          .filter(pl.col("minute") >= 0).with_columns((pl.col("minute") // 30).cast(pl.Int16).alias("window"))
          .sort("pt_date", "agent", "t"))
    fl = pl.read_parquet(C.SHARED / "statement_flags.parquet", columns=["srow", flagcol])
    dup = fl[flagcol].to_numpy()[st["srow"].to_numpy()].astype(bool)
    rows = st["src_row"].to_numpy()
    V = np.zeros((len(rows), 32), np.float32)
    regs = np.array(st["regime"].to_list())
    for r in np.unique(regs):
        m = regs == r
        W = EM.load_whitener(r, 32, model)
        o = np.argsort(rows[m])
        z = np.empty((m.sum(), 32), np.float32)
        z[o] = W(np.asarray(raw[rows[m][o]], np.float32))
        V[m] = z / np.maximum(np.linalg.norm(z, axis=1, keepdims=True), 1e-12)
    meta = st.select("pt_date", pl.col("goal_no").cast(pl.Int8), "regime", "minute", "window", "agent", "room",
                     pl.Series("dup", dup), pl.col("t"))
    return meta, V


def exo_model(cal: pl.DataFrame, model: str):
    days = cal["pt_date"].to_list()
    raw = np.load(C.SHARED / f"embeddings/chat_{EM.MODELS[model]['suffix']}.npy", mmap_mode="r")
    idx = pl.read_parquet(C.SHARED / "embeddings/chat_index.parquet").with_row_index("src_row")
    ch = (pl.read_parquet(C.SHARED / "chat_core.parquet", columns=["message_id", "t", "pt_date", "room", "speaker_kind"])
          .filter(pl.col("speaker_kind").is_in(["human", "automated"]) & pl.col("pt_date").is_in(days))
          .join(idx, on="message_id").join(cal.select("pt_date", "win_start", "regime"), on="pt_date")
          .with_columns(((pl.col("t") - pl.col("win_start")).dt.total_seconds() / 60).alias("minute")).sort("pt_date", "t"))
    rows = ch["src_row"].to_numpy()
    V = np.zeros((len(rows), 32), np.float32)
    regs = np.array(ch["regime"].to_list())
    for r in np.unique(regs):
        m = regs == r
        W = EM.load_whitener(r, 32, model)
        z = W(np.asarray(raw[np.sort(rows[m])], np.float32))[np.argsort(np.argsort(rows[m]))]
        V[m] = z / np.maximum(np.linalg.norm(z, axis=1, keepdims=True), 1e-12)
    return ch.select("pt_date", "minute", "room", pl.col("speaker_kind").alias("kind")), V


def content_dials(cal: pl.DataFrame, meta, V, ex, EV) -> pl.DataFrame:
    """Same per-day call as confirm.content_stage, on given statements / exogenous vectors."""
    meta = meta.with_row_index("_i").filter(~pl.col("dup"))
    rows = []
    for day in cal["pt_date"].to_list():
        s = meta.filter(pl.col("pt_date") == day)
        e = ex.with_row_index("_i").filter(pl.col("pt_date") == day)
        r = D.compute_dial(None, statements=s.select(pl.col("pt_date").alias("day"), "minute", "agent", "window"),
                           statement_vectors=V[s["_i"].to_numpy()].astype(np.float32), channels=("content",),
                           exo_statements=e.select(pl.col("pt_date").alias("day"), "minute") if e.height else None,
                           exo_vectors=EV[e["_i"].to_numpy()].astype(np.float32) if e.height else None,
                           seed=int(hashlib.sha1(day.encode()).hexdigest()[:8], 16))
        for x in r.iter_rows(named=True):
            rows.append({**x, "goal_no": int(cal.filter(pl.col("pt_date") == day)["goal_no"][0])})
    return pl.DataFrame(rows, infer_schema_length=None)


def stage_a(goals, holdout):
    cal = CF.calendar_for(goals, holdout)
    out = {"bge": CF.content_stage(goals, holdout)}                 # frozen pipeline (H12 dup rule)
    for name, model, flag in (("bge_dq5", "bge_small", "self_repeat"), ("gte", "gte_modernbert", "self_repeat_gte")):
        meta, V = statements_model(cal, model, flag)
        ex, EV = exo_model(cal, model)
        out[name] = content_dials(cal, meta, V, ex, EV)
    return out


def stage_b(goals, holdout):
    import build as B
    cal = CF.calendar_for(goals, holdout)
    sp = B.build_spins(cal)
    rows = []
    for day in cal["pt_date"].to_list():
        g = int(cal.filter(pl.col("pt_date") == day)["goal_no"][0])
        rng = np.random.default_rng(X.seed_of("H25", day))
        rows += [r | {"goal_no": g} for r in X.run_binary_variants(day, sp.filter(pl.col("pt_date") == day),
                                                                  sp.filter(pl.col("goal_no") == g), None, rng)]
    d = pl.DataFrame(rows, infer_schema_length=None)
    return d.filter(pl.col("variant").is_in(["trim", "auto"]))


def score_r1b(fz, A: dict, B: pl.DataFrame | None) -> dict:
    fz_r1 = {"CA1_range": fz["CA1_range"], "CA2_share_hi_lt_08": fz["CA2_share_hi_lt_08"],
             "CA3_share_above_null": fz["CA3_share_above_null"], "CA4_rho": fz["CA4_rho"], "CA4_const": fz["CA4_const"],
             "CA4_tol": fz["CA4_tol"]}
    res = {"stage_A_bge": CF.score(fz_r1, A["bge"], None)}
    res["stage_A_bge_dq5_variant"] = CF.score(fz_r1, A["bge_dq5"], None)
    res["stage_A_gte_descriptive"] = CF.score(fz_r1, A["gte"], None)
    mb = A["bge"].filter(pl.col("flag") == "ok").group_by("goal_no").agg(pl.col("g").median().alias("g_bge"))
    mg = A["gte"].filter(pl.col("flag") == "ok").group_by("goal_no").agg(pl.col("g").median().alias("g_gte"))
    j = mb.join(mg, on="goal_no")
    k = int(((j["g_gte"] - j["g_bge"]).abs() <= fz["CA5_tol"]).sum())
    res["CA5-r1b"] = {"periods": j.to_dicts(), "agree": k, "n": j.height, "pass": bool(j.height and k >= min(4, j.height))}
    ca = res["stage_A_bge"]
    res["content_confirmed"] = bool(all(ca[c]["pass"] for c in ("CA1", "CA2", "CA3", "CA4")) and res["CA5-r1b"]["pass"])
    if B is None:
        res["stage_B"] = "skipped: H19's confirmatory score not found (gate)"
        return res
    for v in ("trim", "auto"):
        okb = B.filter((pl.col("flag") == "ok") & (pl.col("variant") == v))
        s1 = float((okb["hi"] < 0.8).mean()) if okb.height else float("nan")
        qs = []
        for _g, d in okb.filter(pl.col("channel") == "activity").group_by("goal_no"):
            a = D.aggregate_days(d["g"].to_numpy(), d["se"].to_numpy())
            if a.get("k", 0) >= 5:
                qs.append(a["p_Q"] < 0.05)
        s2 = float(np.mean(qs)) if qs else float("nan")
        ab = {ch: float((d["g"] > d["null_q95"]).mean()) if d.height else float("nan")
              for ch in ("activity", "talk") for d in [okb.filter((pl.col("channel") == ch) & pl.col("null_q95").is_not_null())]}
        r = {"CB1": {"share": s1, "pass": bool(s1 >= fz["CB1_threshold"])},
             "CB2": {"share": s2, "n_periods": len(qs), "frozen": fz["CB2_share_Q_sig_trim"],
                     "pass": bool(qs and fz["CB2_share_Q_sig_trim"] is not None and abs(s2 - fz["CB2_share_Q_sig_trim"]) <= 0.25)},
             "CB3": {"above_null": ab, "frozen": fz["CB3_share_above_null_trim"],
                     "pass": bool(ab["talk"] - ab["activity"] >= fz["CB3_min_talk_minus_activity"]
                                  and abs(ab["activity"] - fz["CB3_share_above_null_trim"]["activity"]) <= fz["CB3_tol_activity"])}}
        res[f"stage_B_{v}" + ("_primary-r1b" if v == "trim" else "_round1_design")] = r
    return res


def committed() -> bool:
    files = ["hypotheses/H25-criticality-dial/analysis/confirm_r1b.py", "hypotheses/H25-criticality-dial/analysis/confirm.py",
             "hypotheses/H25-criticality-dial/README.md", "hypotheses/H25-criticality-dial/analysis/dial.py",
             "hypotheses/H25-criticality-dial/analysis/explore.py"]
    r = subprocess.run(["git", "-C", str(C.ROOT), "status", "--porcelain", *files], capture_output=True, text=True)
    t = subprocess.run(["git", "-C", str(C.ROOT), "ls-files", "--error-unmatch", *files], capture_output=True, text=True)
    return r.stdout.strip() == "" and t.returncode == 0


def ledger_checks():
    import holdout_ledger as HL
    out = {}
    for t in LEDGER_TARGETS:
        c = HL.check("H25", t, "message content", ["content_alignment", "curie_weiss_gain"])
        out[t] = {"allowed": c["allowed"], "prior_runs": sorted({u["hypothesis"] for u in c["prior_runs"]}),
                  "competing_planned": sorted({u["hypothesis"] for u in c["competing_planned"]})}
    return out


def main():
    args = set(sys.argv[1:])
    dry = "--dry-run" in args
    confirm = all(f in args for f in FLAGS)
    if dry and confirm:
        sys.exit("choose either --dry-run or the two confirmation flags, not both")
    if not dry and not confirm:
        sys.exit("This script uses the LOCKED HOLDOUT. Refusing to run without both flags:\n  " + " ".join(FLAGS) +
                 "\n(or --dry-run for the non-holdout code-path check).")
    led = ledger_checks()
    if dry:
        freeze()
    fz = load_frozen(confirm)
    if confirm:
        if not committed():
            sys.exit("reuse policy: commit confirm_r1b.py, confirm.py, dial.py, explore.py and the card first")
        if any(not c["allowed"] for c in led.values()):
            sys.exit("holdout_ledger.check refuses a target (same-family prior run)")
    out = C.RESD / ("confirm_r1b_dryrun" if dry else "confirm_r1b")
    out.mkdir(parents=True, exist_ok=True)
    print("DRY RUN (non-holdout stand-ins)" if dry else "CONFIRMATORY RUN ON THE LOCKED HOLDOUT", "| frozen sha", fz["_sha256"])
    A = stage_a(DRY_A if dry else STAGE_A, holdout=not dry)
    for k, v in A.items():
        v.write_parquet(out / f"stage_a_content_{k}.parquet")
    gate = dry or any(p.exists() for p in H19_SCORES)
    Bt = stage_b(DRY_B if dry else STAGE_B, holdout=not dry) if gate else None
    if Bt is not None:
        Bt.write_parquet(out / "stage_b_binary.parquet")
    res = score_r1b(fz, A, Bt)
    res["mode"] = "dry-run (numbers meaningless as confirmation)" if dry else "confirmatory (round-1b re-freeze)"
    res["ledger"] = led
    (out / "score.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps({k: v for k, v in res.items() if k != "ledger"}, indent=1, default=str))


if __name__ == "__main__":
    main()
