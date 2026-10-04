"""H26 CONFIRMATORY test on the LOCKED HOLDOUT: drive-removed content vs activity loop gains in held-out two-room
regime-III periods. WRITTEN 2026-10-04 after exploratory round 1. NOT RUN.

!!! --confirm consumes the holdout for H26. It refuses unless BOTH flags are given:
!!!     --confirm --i-understand-this-uses-the-locked-holdout
!!! and (reuse policy, hypotheses/holdout.md) unless this script and the H26 card are committed and unmodified in git.
!!! --dry-run runs every code path on NON-holdout stand-in periods (#41, #42, #44) and asserts that no holdout day is
!!! touched; it also checks that this pipeline (built from shared tables) reproduces explore.py on the stand-ins.

Targets (two-room regime-III held-out periods, per H01's NE15 card):
  primary   #46 (2026-06-08 -> 06-15), #47 (06-15 -> 06-22): inside the NE21+NE23 window. Prior use: H04 computed
            Hawkes branching n and nudge responses of ACTIVITY there (a different statistic); nobody has examined their
            content.
  secondary #45 (06-01 -> 06-08). Prior use: H02's confirmatory run computed Curie-Weiss couplings of 1-min ACTIVITY
            spins (same family as H26's activity gain, different resolution and drive removal) -> the activity side of
            #45 is DISCLOSED AS PREVIOUSLY EXAMINED and #45 enters only C1 (content); H23 plans content-style tests on
            #45 (different statistic).
Reuse disclosure must also go into LOG.md and the H02/H04/H23 cards when this is run (policy item 3).

Pipeline: statements from the shared embeddings (agent chat + intentions), whitened with H01's regime-III basis (fitted
on non-holdout data), first 32 components, unit-normalized; H12 dedupe; activity_bins; rooms_timeline; outage proxy;
exogenous human/automated messages. Static field = top-3 PCs of the first-hour statements + the kickoff-day exogenous
directions (goal-text embeddings are not available offline for held-out goals; the dry run reports the effect of this
substitution on the stand-ins). Estimators: h26lib via explore.build_panels / analyze_panel (unchanged).

Usage:
  uv run python hypotheses/H26-content-near-critical/analysis/confirm.py --dry-run
  uv run python hypotheses/H26-content-near-critical/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
Writes data/processed/H26-content-near-critical/confirm[_dryrun]/confirm.json
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DRY = "--dry-run" in sys.argv
CONFIRM = "--confirm" in sys.argv and "--i-understand-this-uses-the-locked-holdout" in sys.argv
if not (DRY or CONFIRM):
    sys.exit("Refusing to run: pass --dry-run (non-holdout stand-ins) or "
             "--confirm --i-understand-this-uses-the-locked-holdout (consumes the H26 holdout; needs sign-off).")
if DRY and CONFIRM:
    sys.exit("Pass either --dry-run or --confirm, not both.")
sys.argv = [sys.argv[0]]

sys.path.insert(0, str(HERE))
import h26lib as L  # noqa: E402  (thread caps 2)
import explore as EX  # noqa: E402

ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(ROOT / "hypotheses/H01-emergent-superagents-exist/scheme"))
from common import holdout_mask, load_holdout  # noqa: E402
from h01common import load_basis, unit as unitf, whiten_apply  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

SH = ROOT / "data/processed/shared"
OUTD = ROOT / "data/processed/H26-content-near-critical" / ("confirm_dryrun" if DRY else "confirm")
TARGETS = {"46": ("2026-06-08", "2026-06-15"), "47": ("2026-06-15", "2026-06-22"), "45": ("2026-06-01", "2026-06-08")}
PRIMARY = ["46", "47"]
STANDINS = {"41": None, "42": None, "44": None}

# Frozen predictions (written 2026-10-04 ~03:00 UTC from exploratory round 1; see the card, "Confirmatory design").
# Activity-based predictions use only the primary targets (#46, #47): #45's activity was examined by H02.
PREDICTIONS = {
    "C1": "content room excess is real: L3 day-level content gain g_ex > 0 with N2 room-permutation p < 0.05 in >= 2 of "
          "3 targets, and the median over {#45, #46, #47} lies in [0.3, 0.75]",
    "C2": "no robust channel gap (R2): w30 Delta g = g_ex(content) - g_ex(activity) <= 0.15 in at least one of #46, #47 "
          "(pre-registered estimator); H26's 'content near-critical but activity subcritical' fails again",
    "C3": "activity co-fluctuation is global, content is room-local: w30 cross-room correlation rho_c(activity) exceeds "
          "rho_c(content) by >= 0.2 in both #46 and #47",
    "C4": "measured exogenous share: human/automated message directions explain <= 10% of room-day mean deviation "
          "variance above their null in every target",
    "C5": "multi-direction field removal barely matters for content: |g_room(L2) - g_room(L0)| < 0.1 at day level in "
          "every target (static goal/kickoff/first-hour directions and exogenous message directions do not carry the "
          "day-to-day co-fluctuation; exploration: 10/10 units)",
}


def git_clean_or_die():
    files = [str(Path(__file__).relative_to(ROOT)), "hypotheses/H26-content-near-critical/README.md",
             "hypotheses/H26-content-near-critical/analysis/h26lib.py",
             "hypotheses/H26-content-near-critical/analysis/explore.py"]
    for f in files:
        tracked = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--error-unmatch", f], capture_output=True)
        dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", f], capture_output=True, text=True).stdout
        if tracked.returncode != 0 or dirty.strip():
            sys.exit(f"Refusing: {f} must be committed and unmodified before a confirmatory run (reuse policy item 1).")


def days_between(lo, hi):
    cal = pl.read_parquet(SH / "calendar.parquet")
    return sorted(cal.filter((pl.col("pt_date") >= lo) & (pl.col("pt_date") < hi))["pt_date"].to_list())


def build_data(units: dict[str, list[str]], allow_holdout: bool):
    """Mirror of scheme/build.py from shared tables for arbitrary units (name -> days)."""
    all_days = sorted({d for v in units.values() for d in v})
    cal = pl.read_parquet(SH / "calendar.parquet")
    hm = dict(zip(cal["pt_date"].to_list(), holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())))
    held = {d for d in all_days if hm.get(d)}
    if not allow_holdout:
        assert not held, f"dry run touched holdout days {sorted(held)}"
    cal = cal.filter(pl.col("pt_date").is_in(all_days)).select("pt_date", "win_start", "window_s").with_columns(
        (pl.col("window_s") / 1800).round().clip(1, None).cast(pl.Int16).alias("n_win"))
    dayidx = pl.DataFrame([{"unit": u, "pt_date": d, "day": i} for u, v in units.items() for i, d in enumerate(v)])
    basis = load_basis("III")
    st = pl.read_parquet(SH / "embeddings/statements.parquet").filter(pl.col("pt_date").is_in(all_days))
    st = st.join(dayidx, on="pt_date").join(cal, on="pt_date").sort("t")
    st = st.with_columns((((pl.col("t") - pl.col("win_start")).dt.total_seconds() // 1800).clip(0, None)).cast(pl.Int16).alias("w"))
    st = st.with_columns(pl.min_horizontal("w", pl.col("n_win") - 1).alias("win30")).drop("w").with_row_index("i")
    Ec = np.load(SH / "embeddings/chat_bge_small.npy", mmap_mode="r")
    Ei = np.load(SH / "embeddings/intentions_bge_small.npy", mmap_mode="r")
    kind = st["kind"].to_numpy(); src = st["src_row"].to_numpy()
    raw = np.zeros((st.height, Ec.shape[1]), np.float32)
    m = kind == "chat"
    raw[m] = Ec[src[m]]; raw[~m] = Ei[src[~m]]
    V = unitf(whiten_apply(raw, basis, 32)).astype(np.float32)
    dup = np.zeros(st.height, bool)
    for _, g in st.filter(pl.col("kind") == "chat").group_by(["agent", "pt_date"]):
        if g.height < 2:
            continue
        g = g.sort("t"); X = raw[g["i"].to_numpy()]
        S = np.tril(X @ X.T, -1)
        dup[g["i"].to_numpy()[S.max(1) > 0.95]] = True
    st = st.with_columns(pl.Series("dup", dup))
    ab = (pl.scan_parquet(SH / "activity_bins.parquet").filter(pl.col("pt_date").is_in(all_days))
          .select("pt_date", "minute", "agent", "state").collect().join(cal.select("pt_date", "n_win"), on="pt_date")
          .with_columns(pl.min_horizontal(pl.col("minute") // 30, pl.col("n_win").cast(pl.Int64) - 1).cast(pl.Int16).alias("win30"),
                        (pl.col("state") >= 3).alias("act"), (pl.col("state") == 4).alias("talk")))
    present = ab.group_by("pt_date", "agent").agg((pl.col("state") >= 2).any().alias("p")).filter("p")
    ab = ab.join(present.select("pt_date", "agent"), on=["pt_date", "agent"]).sort("pt_date", "agent", "minute")
    outage = (ab.group_by("pt_date", "minute").agg(pl.col("act").any().alias("any"), pl.col("win30").first())
              .group_by("pt_date", "win30").agg((1 - pl.col("any").cast(pl.Float32).mean()).alias("idle_share")))
    rng = np.random.default_rng(20261004)
    ab = ab.with_columns(*[pl.Series(f"h{s}", rng.random(ab.height) < 0.5) for s in range(3)])
    aggs = [pl.len().alias("n_min"), pl.col("act").sum().alias("n_act"), pl.col("talk").sum().alias("n_talk")]
    for s in range(3):
        h = pl.col(f"h{s}")
        aggs += [h.sum().alias(f"n_min_A{s}"), (h & pl.col("act")).sum().alias(f"n_act_A{s}"),
                 (h & pl.col("talk")).sum().alias(f"n_talk_A{s}")]
    act = ab.group_by("pt_date", "agent", "win30").agg(aggs).join(dayidx, on="pt_date")
    rt = pl.read_parquet(SH / "rooms_timeline.parquet").sort("t_start")
    aw = pl.concat([act.select("unit", "pt_date", "agent", "win30"), st.select("unit", "pt_date", "agent", "win30")]).unique()
    aw = aw.join(cal.select("pt_date", "win_start"), on="pt_date").with_columns(
        (pl.col("win_start") + pl.duration(seconds=pl.col("win30").cast(pl.Int64) * 1800 + 900)).alias("mid")).sort("mid")
    aw = aw.join_asof(rt.select("agent", "room", "t_start", "t_end"), left_on="mid", right_on="t_start", by="agent")
    aw = aw.with_columns(pl.when(pl.col("t_end").is_null() | (pl.col("mid") < pl.col("t_end"))).then(pl.col("room")).alias("room"))
    chat = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "pt_date", "room", "speaker_kind"]) \
             .filter(pl.col("pt_date").is_in(all_days) & pl.col("speaker_kind").is_in(["human", "automated"]))
    ci = pl.read_parquet(SH / "embeddings/chat_index.parquet").with_row_index("emb_row")
    exo = chat.join(ci, on="message_id").join(cal, on="pt_date").with_columns(
        ((pl.col("t") - pl.col("win_start")).dt.total_seconds() // 1800).cast(pl.Int16).alias("win30")).join(dayidx, on="pt_date")
    Ve = unitf(whiten_apply(np.asarray(Ec[exo["emb_row"].to_numpy()], np.float32), basis, 32)).astype(np.float32)
    exo = exo.with_row_index("i")
    static = {}
    for u, ds in units.items():
        s0 = st.filter((pl.col("unit") == u) & (pl.col("day") == 0))
        fh = s0.filter((pl.col("t") - pl.col("win_start")).dt.total_seconds() < 3600)
        dirs = []
        if fh.height >= 6:
            Xf = V[fh["i"].to_numpy()]
            dirs += list(np.linalg.svd(Xf - Xf.mean(0), full_matrices=False)[2][:3])
        e0 = exo.filter((pl.col("unit") == u) & (pl.col("pt_date") == ds[0]))
        if e0.height:
            dirs += list(Ve[e0["i"].to_numpy()][:3])
        static[u] = L.orthobasis(np.array(dirs)) if dirs else np.zeros((0, 32))
    Dt = EX.Data.__new__(EX.Data)
    Dt.st = st.select("i", "unit", "agent", "pt_date", "day", "t", "win30", "n_win", "kind", "dup")
    Dt.V = V; Dt.act = act; Dt.rooms = aw.select("unit", "pt_date", "agent", "win30", "room")
    Dt.outage = outage; Dt.exo = exo.select("i", "unit", "pt_date", "t", "win30", "room", "speaker_kind"); Dt.Ve = Ve
    Dt.static = static
    Dt.units = {u: {"days": ds, "goal_no": int(u)} for u, ds in units.items()}
    return Dt


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


def verdicts(res, targets, primary):
    def g(u, k, lv="L2", st="g_ex"):
        rec = res[u].get(k, {}).get(lv) or {}
        if st in ("g_ex", "g_room"):   # recompute from rho so that -inf (stored as None) becomes -1 (clipped)
            rho = rec.get("rho_ex" if st == "g_ex" else "rho_w"); nr = rec.get("Nr")
            if rho is None or nr is None:
                return None
            R = 1 + (nr - 1) * rho
            return float(np.clip(1 - 1 / R, -1, 1)) if R > 0 else -1.0
        return rec.get(st)
    out = {}
    c1 = {u: (g(u, "c_day"), g(u, "c_day", "L2", "p_N2_rho_ex")) for u in targets}
    vals = [v[0] for v in c1.values() if v[0] is not None]
    n_ok = sum(1 for v in c1.values() if v[0] is not None and v[0] > 0 and v[1] is not None and v[1] < 0.05)
    med = float(np.median(vals)) if vals else None
    out["C1"] = {"values": c1, "median": med, "n_ok": n_ok,
                 "pass": n_ok >= 2 and med is not None and 0.3 <= med <= 0.75}
    gaps = {}
    for u in primary:
        gc, ga = g(u, "c_w30"), g(u, "a_w30")
        gaps[u] = None if gc is None or ga is None else gc - ga
    out["C2"] = {"gaps": gaps, "pass": any(v is not None and v <= 0.15 for v in gaps.values())}
    rc = {u: (g(u, "a_w30", "L2", "rho_c"), g(u, "c_w30", "L2", "rho_c")) for u in primary}
    out["C3"] = {"rho_c_activity_content": rc,
                 "pass": all(a is not None and c is not None and a - c >= 0.2 for a, c in rc.values())}
    sh = {u: res[u]["drive_share_day"].get("excess_share_of_all_room_variance") for u in targets}
    out["C4"] = {"excess_share": sh, "pass": all(v is not None and v <= 0.10 for v in sh.values())}
    c5 = {u: (g(u, "c_day", "L0", "g_room"), g(u, "c_day", "L2", "g_room")) for u in targets}
    out["C5"] = {"L0_vs_L2_room": c5, "pass": all(a is not None and b is not None and abs(a - b) < 0.1 for a, b in c5.values())}
    return out


def main():
    OUTD.mkdir(parents=True, exist_ok=True)
    if CONFIRM:
        git_clean_or_die()
        h = load_holdout()
        assert all(int(u) in h["goal_periods_held_out"] for u in TARGETS), "targets must be held-out periods"
        units = {u: days_between(*TARGETS[u]) for u in TARGETS}
        Dt = build_data(units, allow_holdout=True)
        res = evaluate(Dt, units)
        out = {"mode": "confirm", "predictions": PREDICTIONS, "verdicts": verdicts(res, list(TARGETS), PRIMARY),
               "results": res}
    else:
        U = json.loads((ROOT / "data/processed/H01-emergent-superagents-exist/units.json").read_text())
        units = {u["unit"]: u["days"] for u in U if u["unit"] in STANDINS}
        Dt = build_data(units, allow_holdout=False)
        res = evaluate(Dt, units)
        # reproduction check against explore.py on the stand-ins
        repro = {}
        for u in units:
            f = ROOT / f"data/processed/H26-content-near-critical/G{int(u):02d}/{u}.json"
            if f.exists():
                ex = json.loads(f.read_text())
                repro[u] = {k: {"confirm_pipeline": (res[u].get(k1, {}).get("L2") or {}).get("g_ex"),
                                "explore": (ex.get(k2, {}).get("L2") or {}).get("g_ex")}
                            for k, k1, k2 in (("content_day", "c_day", "c_day_dedup"), ("content_w30", "c_w30", "c_w30_dedup"),
                                              ("activity_w30", "a_w30", "a_w30"), ("talk_w30", "k_w30", "k_w30"))}
        out = {"mode": "dry-run", "standins": list(units), "predictions": PREDICTIONS,
               "verdicts_on_standins": verdicts(res, list(units), ["41", "44"]), "reproduction": repro}
    (OUTD / "confirm.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out.get("verdicts") or out.get("verdicts_on_standins"), indent=1, default=float))
    if "reproduction" in out:
        print(json.dumps(out["reproduction"], indent=1, default=float))


if __name__ == "__main__":
    main()
