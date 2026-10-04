"""H26 CONFIRMATORY test on the LOCKED HOLDOUT -- ROUND-1B RE-FREEZE of `confirm.py`. Written 2026-10-04 after round 1b,
before any holdout outcome was computed. NOT RUN. `confirm.py` stays byte-for-byte unchanged.

!!! --confirm consumes the holdout for H26. It refuses unless BOTH flags are given:
!!!     --confirm --i-understand-this-uses-the-locked-holdout
!!! and unless this script, confirm.py, h26lib.py, explore.py and the card are committed and unmodified (reuse item 1),
!!! and infra/shared/holdout_ledger.check() reports no same-family prior run for the statistics being computed.
!!! --dry-run runs every code path on NON-holdout stand-ins (#41, #42, #44), asserts no holdout day is touched, and
!!! compares with the round-1b explore outputs (r1b/bge_fixed_trim, r1b/gte_fixed).

Targets as confirm.py: #46, #47 (primary; two-room, inside NE21+NE23) and #45 (content-only).

Inputs switched (round 1b; mirrors scheme/build.py --r1b ... --data-version fixed --trim):
  * activity from activity_bins_fixed, trimmed to each day's all-present window (DQ8) before windows and split halves;
    the outage proxy is recomputed on it;
  * statement vectors in BOTH models (bge_small, gte_modernbert) from the shared embeddings, whitened with H01's
    round-1b regime-III basis of that model (r1b/bge_none, r1b/gte_none; fitted on non-holdout data), first 32 dims;
  * DQ5 own-model restatement flags (bge self_repeat, gte self_repeat_gte; chat only) instead of round 1's rule;
  * static field: shared goal fields (goal + per-room kickoffs, embeddings/goals.parquet; held-out rows only under
    --confirm) + top-3 first-hour PCs, as the round-1b scheme (confirm.py had to substitute kickoff-day exogenous
    directions because held-out goal embeddings were not available; the shared table now has them);
  * exogenous message directions in each model's basis.
  Context-ledger visibility, the work ledger, failures and nudge targets are not inputs (rooms use the broadcast rule).

Re-frozen predictions ("-r1b" = changed because round 1b changed the result it rested on):
  C1-r1b  content room excess (L3, day): g_ex > 0 with N2 p < 0.05 in >= 2 of 3 targets AND median over {#45, #46, #47}
          in [0.3, 0.75] -- in BOTH models. (Round 1b: bge 0.52, gte 0.47.)
  C2-r1b  REPLACES C2 (R2 "no gap" was set from round-1 activity numbers that round 1b withdrew): the content-activity
          gap is real at 30 min: w30 dg_ca = g_ex(content) - g_ex(activity, trimmed) > 0 in both #46 and #47 and
          > 0.15 in at least one, in both models. (Round 1b, trimmed: +0.22 [0.01, ...], 6/10 units > 0.15.)
  C2t-r1b NEW (R2 against talk still holds): w30 dg_ck = g_ex(content) - g_ex(talk, trimmed) <= 0.15 in at least one
          of #46, #47, in both models. (Round 1b: dg_ck -0.03 to -0.09.)
  C3-r1b  REPLACES C3 ("activity co-fluctuation is global" was the event-drop artifact: activity cross-room rho_c
          0.79 -> -0.05): w30 rho_c(activity, trimmed) - rho_c(content) < 0.2 in both #46 and #47, both models.
  C4      unchanged (exogenous share <= 10% in every target), both models.
  C5      unchanged (|g_room(L2) - g_room(L0)| < 0.1, content day, every target), both models.
  Ledger gate: C2-r1b, C2t-r1b and C3-r1b are activity/talk equal-time gains on #46/#47, the Curie-Weiss family of
  H04's executed NE21+NE23 run (holdout ledger item 3) -> computed under --confirm ONLY with the extra flag
  --vivian-approved-activity-reuse; otherwise reported as "blocked by ledger". Content criteria (C1, C4, C5) are a
  different modality from every executed run (H02 #45 activity couplings; H04 #45-#50 Hawkes / kernels / MF).

Usage:
  uv run python hypotheses/H26-content-near-critical/analysis/confirm_r1b.py --dry-run
  uv run python hypotheses/H26-content-near-critical/analysis/confirm_r1b.py --confirm --i-understand-this-uses-the-locked-holdout
Writes data/processed/H26-content-near-critical/confirm_r1b[_dryrun]/confirm.json
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_v] = "2"
os.environ.setdefault("POLARS_MAX_THREADS", "2")

HERE = Path(__file__).resolve().parent
DRY = "--dry-run" in sys.argv
CONFIRM = "--confirm" in sys.argv and "--i-understand-this-uses-the-locked-holdout" in sys.argv
ACT_OVERRIDE = "--vivian-approved-activity-reuse" in sys.argv
if not (DRY or CONFIRM):
    sys.exit("Refusing to run: pass --dry-run (non-holdout stand-ins) or "
             "--confirm --i-understand-this-uses-the-locked-holdout (consumes the H26 holdout; needs sign-off).")
if DRY and CONFIRM:
    sys.exit("Pass either --dry-run or --confirm, not both.")
sys.argv = [sys.argv[0]]

sys.path.insert(0, str(HERE))
import h26lib as L  # noqa: E402
import explore as EX  # noqa: E402

ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(ROOT / "hypotheses/H01-emergent-superagents-exist/scheme"))
from common import holdout_mask, load_holdout  # noqa: E402
from h01common import unit as unitf, whiten_apply  # noqa: E402
import holdout_ledger as HL  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

SH = ROOT / "data/processed/shared"
H01R1B = ROOT / "data/processed/H01-emergent-superagents-exist/r1b"
H26 = ROOT / "data/processed/H26-content-near-critical"
OUTD = H26 / ("confirm_r1b_dryrun" if DRY else "confirm_r1b")
TARGETS = {"46": ("2026-06-08", "2026-06-15"), "47": ("2026-06-15", "2026-06-22"), "45": ("2026-06-01", "2026-06-08")}
PRIMARY = ["46", "47"]
STANDINS = ["41", "42", "44"]
MODELS = {"bge": ("bge_small", "bge_none", "self_repeat", "bge_fixed_trim"),
          "gte": ("gte_modernbert", "gte_none", "self_repeat_gte", "gte_fixed")}
GOALVEC = {"bge_small": "goal_vectors.npy", "gte_modernbert": "goal_vectors_gte_modernbert.npy"}
SEED = 20261004


def git_clean_or_die():
    files = [str(Path(__file__).relative_to(ROOT)), "hypotheses/H26-content-near-critical/analysis/confirm.py",
             "hypotheses/H26-content-near-critical/README.md", "hypotheses/H26-content-near-critical/analysis/h26lib.py",
             "hypotheses/H26-content-near-critical/analysis/explore.py"]
    for f in files:
        tracked = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--error-unmatch", f], capture_output=True)
        dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", f], capture_output=True, text=True).stdout
        if tracked.returncode != 0 or dirty.strip():
            sys.exit(f"Refusing: {f} must be committed and unmodified before a confirmatory run (reuse policy item 1).")


def days_between(lo, hi):
    cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("window_s") > 0)
    return sorted(cal.filter((pl.col("pt_date") >= lo) & (pl.col("pt_date") < hi))["pt_date"].to_list())


def ledger():
    out = {}
    for t in ("G45", "G46", "G47", "NE21+NE23"):
        cc = HL.check("H26", t, "message content", ["content_alignment"])
        ca = HL.check("H26", t, "activity timing", ["curie_weiss_gain"])
        out[t] = {"content_allowed": cc["allowed"], "activity_allowed": ca["allowed"],
                  "prior_runs": sorted({u["hypothesis"] for u in cc["prior_runs"]}),
                  "activity_same_family_runs": sorted({u["hypothesis"] for u in ca["prior_runs_same_family"]}),
                  "competing_planned": sorted({u["hypothesis"] for u in cc["competing_planned"]})}
    return out


def build_data(units: dict[str, list[str]], allow_holdout: bool, model_key: str):
    """Round-1b mirror of scheme/build.py (fixed activity + trim, model vectors, DQ5 flags, shared goal fields)."""
    model, h01tag, flagcol, _ = MODELS[model_key]
    all_days = sorted({d for v in units.values() for d in v})
    cal = pl.read_parquet(SH / "calendar.parquet")
    hm = dict(zip(cal["pt_date"].to_list(), holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())))
    hc = dict(zip(cal["pt_date"].to_list(), cal["holdout"].to_list()))
    if not allow_holdout:
        assert not {d for d in all_days if hm.get(d) or hc.get(d)}, "dry run touched holdout days"
    cal = cal.filter(pl.col("pt_date").is_in(all_days)).select("pt_date", "win_start", "window_s").with_columns(
        (pl.col("window_s") / 1800).round().clip(1, None).cast(pl.Int16).alias("n_win"))
    dayidx = pl.DataFrame([{"unit": u, "pt_date": d, "day": i} for u, v in units.items() for i, d in enumerate(v)])
    bz = np.load(H01R1B / h01tag / "basis_III.npz")
    basis = {k: bz[k] for k in bz.files}
    # ---------------- statements (agent chat + intentions), model vectors, DQ5 flags
    st = (pl.read_parquet(SH / "embeddings/statements.parquet").with_row_index("srow")
          .filter(pl.col("pt_date").is_in(all_days) & pl.col("agent").is_not_null()))
    st = st.join(dayidx, on="pt_date").join(cal, on="pt_date").sort("t")
    st = st.with_columns((((pl.col("t") - pl.col("win_start")).dt.total_seconds() // 1800).clip(0, None)).cast(pl.Int16).alias("w"))
    st = st.with_columns(pl.min_horizontal("w", pl.col("n_win") - 1).alias("win30")).drop("w").with_row_index("i")
    suf = "bge_small" if model == "bge_small" else "gte_modernbert"
    Ec = np.load(SH / f"embeddings/chat_{suf}.npy", mmap_mode="r")
    Ei = np.load(SH / f"embeddings/intentions_{suf}.npy", mmap_mode="r")
    kind = st["kind"].to_numpy(); src = st["src_row"].to_numpy()
    raw = np.zeros((st.height, Ec.shape[1]), np.float32)
    for kk, E in (("chat", Ec), ("intent", Ei)):
        m = kind == kk if kk == "chat" else kind != "chat"
        o = np.argsort(src[m])
        tmp = np.asarray(E[src[m][o]], np.float32)
        out_ = np.empty_like(tmp); out_[o] = tmp
        raw[m] = out_
    V = unitf(whiten_apply(raw, basis, 32)).astype(np.float32)
    fl = pl.read_parquet(SH / "statement_flags.parquet", columns=["srow", flagcol])
    dup = fl[flagcol].to_numpy()[st["srow"].to_numpy()].astype(bool) & (kind == "chat")
    st = st.with_columns(pl.Series("dup", dup))
    # ---------------- activity (fixed table, trimmed to the all-present window)
    ab = (pl.scan_parquet(SH / "activity_bins_fixed.parquet").filter(pl.col("pt_date").is_in(all_days))
          .select("pt_date", "minute", "agent", "state", pl.col("talk").alias("r_talk"), pl.col("idle").alias("r_idle"),
                  pl.col("consolidate").alias("r_cons"), pl.col("other_event").alias("r_other"), pl.col("turns").alias("r_turns"))
          .collect().join(cal.select("pt_date", "n_win"), on="pt_date")
          .with_columns(pl.min_horizontal(pl.col("minute") // 30, pl.col("n_win").cast(pl.Int64) - 1).cast(pl.Int16).alias("win30"),
                        (pl.col("state") >= 3).alias("act"), (pl.col("state") == 4).alias("talk")))
    present = ab.group_by("pt_date", "agent").agg((pl.col("state") >= 2).any().alias("p")).filter("p")
    ab = ab.join(present.select("pt_date", "agent"), on=["pt_date", "agent"])
    rec = (ab.filter((pl.col("r_talk") + pl.col("r_idle") + pl.col("r_cons") + pl.col("r_other") + pl.col("r_turns")) > 0)
           .group_by("pt_date", "agent").agg(pl.col("minute").min().alias("m0"), pl.col("minute").max().alias("m1")))
    win = rec.group_by("pt_date").agg(pl.col("m0").max().alias("lo"), pl.col("m1").min().alias("hi"))
    n0 = ab.height
    ab = (ab.join(win, on="pt_date", how="left").filter((pl.col("minute") >= pl.col("lo")) & (pl.col("minute") <= pl.col("hi")))
          .drop("lo", "hi", "r_talk", "r_idle", "r_cons", "r_other", "r_turns").sort("pt_date", "agent", "minute"))
    trim_kept = ab.height / max(n0, 1)
    outage = (ab.group_by("pt_date", "minute").agg(pl.col("act").any().alias("any"), pl.col("win30").first())
              .group_by("pt_date", "win30").agg((1 - pl.col("any").cast(pl.Float32).mean()).alias("idle_share")))
    rng = np.random.default_rng(SEED)
    ab = ab.with_columns(*[pl.Series(f"h{s}", rng.random(ab.height) < 0.5) for s in range(3)])
    aggs = [pl.len().alias("n_min"), pl.col("act").sum().alias("n_act"), pl.col("talk").sum().alias("n_talk")]
    for s in range(3):
        h = pl.col(f"h{s}")
        aggs += [h.sum().alias(f"n_min_A{s}"), (h & pl.col("act")).sum().alias(f"n_act_A{s}"),
                 (h & pl.col("talk")).sum().alias(f"n_talk_A{s}")]
    act = ab.group_by("pt_date", "agent", "win30").agg(aggs).join(dayidx, on="pt_date")
    # ---------------- rooms (broadcast rule), exogenous messages
    rt = pl.read_parquet(SH / "rooms_timeline.parquet").sort("t_start")
    aw = pl.concat([act.select("unit", "pt_date", "agent", "win30"), st.select("unit", "pt_date", "agent", "win30")]).unique()
    aw = aw.join(cal.select("pt_date", "win_start"), on="pt_date").with_columns(
        (pl.col("win_start") + pl.duration(seconds=pl.col("win30").cast(pl.Int64) * 1800 + 900)).alias("mid")).sort("mid")
    aw = aw.join_asof(rt.select("agent", "room", "t_start", "t_end"), left_on="mid", right_on="t_start", by="agent")
    aw = aw.with_columns(pl.when(pl.col("t_end").is_null() | (pl.col("mid") < pl.col("t_end"))).then(pl.col("room")).alias("room"))
    chat = (pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "pt_date", "room", "speaker_kind"])
            .filter(pl.col("pt_date").is_in(all_days) & pl.col("speaker_kind").is_in(["human", "automated"])))
    ci = pl.read_parquet(SH / "embeddings/chat_index.parquet").with_row_index("emb_row")
    exo = chat.join(ci, on="message_id").join(cal, on="pt_date").with_columns(
        ((pl.col("t") - pl.col("win_start")).dt.total_seconds() // 1800).cast(pl.Int16).alias("win30")).join(dayidx, on="pt_date")
    er = exo["emb_row"].to_numpy()
    o = np.argsort(er)
    tmp = np.asarray(Ec[er[o]], np.float32)
    rawe = np.empty_like(tmp); rawe[o] = tmp
    Ve = unitf(whiten_apply(rawe, basis, 32)).astype(np.float32)
    exo = exo.with_row_index("i")
    # ---------------- static field: shared goal fields + first-hour PCs (round-1b scheme)
    sg = pl.read_parquet(SH / "embeddings/goals.parquet").with_columns(pl.col("kind").cast(pl.String))
    G = np.load(SH / "embeddings" / GOALVEC[model]).astype(np.float32)
    static, sinfo = {}, {}
    for u, ds in units.items():
        g = int(u)
        rows = sg.filter((pl.col("goal_no") == g) & pl.col("kind").is_in(["goal", "kickoff_room"])
                         & (pl.lit(True) if allow_holdout else ~pl.col("holdout")))
        dirs = [unitf(whiten_apply(G[int(r):int(r) + 1], basis, 32))[0] for r in rows["gid"].to_list()]
        names = rows["kind"].to_list()
        s0 = st.filter((pl.col("unit") == u) & (pl.col("day") == 0))
        fh = s0.filter((pl.col("t") - pl.col("win_start")).dt.total_seconds() < 3600)
        if fh.height >= 6:
            Xf = V[fh["i"].to_numpy()]
            dirs += list(np.linalg.svd(Xf - Xf.mean(0), full_matrices=False)[2][:3]); names += ["first_hour_pc"] * 3
        static[u] = L.orthobasis(np.array(dirs)) if dirs else np.zeros((0, 32))
        sinfo[u] = {"directions": names, "rank": int(static[u].shape[0])}
    Dt = EX.Data.__new__(EX.Data)
    Dt.st = st.select("i", "unit", "agent", "pt_date", "day", "t", "win30", "n_win", "kind", "dup")
    Dt.V = V; Dt.act = act; Dt.rooms = aw.select("unit", "pt_date", "agent", "win30", "room")
    Dt.outage = outage; Dt.exo = exo.select("i", "unit", "pt_date", "t", "win30", "room", "speaker_kind"); Dt.Ve = Ve
    Dt.static = static
    Dt.units = {u: {"days": ds, "goal_no": int(u)} for u, ds in units.items()}
    return Dt, {"trim_kept": trim_kept, "dup_chat": int(dup.sum()), "static": sinfo}


def evaluate(Dt, units):
    res = {}
    for u in units:
        rng = np.random.default_rng(EX.stable_seed(u, "confirm"))
        panels, info = EX.build_panels(Dt, u, dedup=True)
        r = {"info": info}
        for (ch, rr), P in panels.items():
            if rr == "wd":
                continue
            r[f"{ch}_{rr}"] = EX.analyze_panel(P, ch, rng, do_nulls=True)
        r["drive_share_day"] = EX.drive_share(panels[("c", "day")], Dt, u, rng)
        res[u] = r
    return res


def gval(res, u, k, lv="L2", st="g_ex"):
    rec = res[u].get(k, {}).get(lv) or {}
    if st in ("g_ex", "g_room"):
        rho = rec.get("rho_ex" if st == "g_ex" else "rho_w"); nr = rec.get("Nr")
        if rho is None or nr is None:
            return None
        R = 1 + (nr - 1) * rho
        return float(np.clip(1 - 1 / R, -1, 1)) if R > 0 else -1.0
    return rec.get(st)


def verdicts_one(res, targets, primary, activity: bool):
    out = {}
    c1 = {u: (gval(res, u, "c_day"), gval(res, u, "c_day", "L2", "p_N2_rho_ex")) for u in targets}
    vals = [v[0] for v in c1.values() if v[0] is not None]
    n_ok = sum(1 for v in c1.values() if v[0] is not None and v[0] > 0 and v[1] is not None and v[1] < 0.05)
    med = float(np.median(vals)) if vals else None
    out["C1"] = {"values": c1, "median": med, "n_ok": n_ok, "pass": bool(n_ok >= 2 and med is not None and 0.3 <= med <= 0.75)}
    sh = {u: res[u]["drive_share_day"].get("excess_share_of_all_room_variance") for u in targets}
    out["C4"] = {"excess_share": sh, "pass": all(v is not None and v <= 0.10 for v in sh.values())}
    c5 = {u: (gval(res, u, "c_day", "L0", "g_room"), gval(res, u, "c_day", "L2", "g_room")) for u in targets}
    out["C5"] = {"L0_vs_L2_room": c5, "pass": all(a is not None and b is not None and abs(a - b) < 0.1 for a, b in c5.values())}
    if not activity:
        out["C2-r1b"] = out["C2t-r1b"] = out["C3-r1b"] = {"pass": None, "note": "blocked by ledger (H04 same family on #46/#47)"}
        return out
    gca = {u: (None if gval(res, u, "c_w30") is None or gval(res, u, "a_w30") is None else gval(res, u, "c_w30") - gval(res, u, "a_w30"))
           for u in primary}
    out["C2-r1b"] = {"gaps": gca, "pass": bool(all(v is not None and v > 0 for v in gca.values())
                                                and any(v is not None and v > 0.15 for v in gca.values()))}
    gck = {u: (None if gval(res, u, "c_w30") is None or gval(res, u, "k_w30") is None else gval(res, u, "c_w30") - gval(res, u, "k_w30"))
           for u in primary}
    out["C2t-r1b"] = {"gaps": gck, "pass": any(v is not None and v <= 0.15 for v in gck.values())}
    rc = {u: (gval(res, u, "a_w30", "L2", "rho_c"), gval(res, u, "c_w30", "L2", "rho_c")) for u in primary}
    out["C3-r1b"] = {"rho_c_activity_content": rc, "pass": all(a is not None and c is not None and a - c < 0.2 for a, c in rc.values())}
    return out


def combine(V):
    keys = ["C1", "C2-r1b", "C2t-r1b", "C3-r1b", "C4", "C5"]
    return {k: (None if any(V[m][k]["pass"] is None for m in V) else all(V[m][k]["pass"] for m in V)) for k in keys}


def main():
    OUTD.mkdir(parents=True, exist_ok=True)
    led = ledger()
    if CONFIRM:
        git_clean_or_die()
        if not all(c["content_allowed"] for c in led.values()):
            sys.exit("holdout_ledger.check refuses a content target (same-family prior run)")
        h = load_holdout()
        assert all(int(u) in h["goal_periods_held_out"] for u in TARGETS), "targets must be held-out periods"
        units = {u: days_between(*TARGETS[u]) for u in TARGETS}
        targets, primary, allow = list(TARGETS), PRIMARY, True
        activity = ACT_OVERRIDE
    else:
        U = json.loads((ROOT / "data/processed/H01-emergent-superagents-exist/units.json").read_text())
        units = {u["unit"]: u["days"] for u in U if u["unit"] in STANDINS}
        targets, primary, allow, activity = list(units), ["41", "44"], False, True
    out = {"mode": "confirm (round-1b re-freeze)" if CONFIRM else "dry-run (round-1b re-freeze)", "ledger": led,
           "activity_side_computed": activity, "per_model": {}, "build": {}}
    for mk in MODELS:
        Dt, binfo = build_data(units, allow, mk)
        res = evaluate(Dt, units)
        out["build"][mk] = binfo
        out["per_model"][mk] = verdicts_one(res, targets, primary, activity)
        if DRY:   # reproduction against the round-1b explore outputs on the stand-ins
            rep = {}
            for u in units:
                f = H26 / "r1b" / MODELS[mk][3] / f"G{int(u):02d}/{u}.json"
                if f.exists():
                    ex = json.loads(f.read_text())
                    rep[u] = {k: {"confirm_r1b": (res[u].get(k1, {}).get("L2") or {}).get("g_ex"),
                                  "explore_r1b": (ex.get(k2, {}).get("L2") or {}).get("g_ex")}
                              for k, k1, k2 in (("content_day", "c_day", "c_day_dedup"), ("content_w30", "c_w30", "c_w30_dedup"),
                                                ("activity_w30", "a_w30", "a_w30"), ("talk_w30", "k_w30", "k_w30"))}
            out.setdefault("reproduction", {})[f"{mk} vs r1b/{MODELS[mk][3]}"] = rep
    out["verdicts_both_models"] = combine(out["per_model"])
    (OUTD / "confirm.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps({"verdicts_both_models": out["verdicts_both_models"],
                      "per_model": {m: {k: v.get("pass") for k, v in vv.items()} for m, vv in out["per_model"].items()}}, indent=1))
    if DRY:
        print(json.dumps(out["reproduction"], indent=1, default=float))
    print("ledger:", json.dumps({t: {k: v for k, v in c.items() if k != "competing_planned"} for t, c in led.items()}))


if __name__ == "__main__":
    main()
