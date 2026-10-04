"""H127 confirmatory test on the LOCKED HOLDOUT. Written 2026-10-04 after exploratory round 1; NOT RUN.

Guard: the holdout is touched only with BOTH flags, a clean git state for H127's code, and a holdout-ledger check:
  uv run python hypotheses/H127-content-trails-goal-call-clock/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
Without flags it prints the frozen predictions. --dry-run runs the identical in-memory pipeline on non-holdout stand-in
kickoffs (#11-#13, #38-#42) and writes data/processed/H127-content-trails-goal-call-clock/confirm_dryrun.json only.

Targets: held-out goal periods with a shared kickoff and >= 5 contiguous active days from day 1 in one regime (resolved at
run time from #1, #9, #14, #15, #28, #29, #34, #43, #45-#50; #22/#23/#32 excluded for H10). Estimator identical to
h127lib (bge-small white32, free day-1 amplitude, 0.36-s hour floor, read-out call from the context ledger).
Frozen predictions (exploration found a read-out spike, not a call-clock relaxation):
  C1  read-out spike: the share of rising agents whose day-1 plateau is reached at the read-out call (fit at the grid
      floor) is >= 0.5 over all targets (exploration 0.74; synthetic relaxation worlds <= 0.20, read-out jump 0.42-0.47).
      Credence 0.8.
  C2  spike then decay: the agent-weighted mean of (a - P)/A over statements from calls 1-3 since the read-out call is
      >= 1.5 (A = the agent's mean over calls >= 64 since read-out; exploration 2.3-2.4). Credence 0.7.
  C3  no call-clock law: pooled within-kickoff slope of log T_half^H on log call rate has its 90% CI containing 0 or above
      -0.5 (exploration +0.59 [-0.45, +1.75]). Credence 0.75.
Planned separately (not in this script): NE44 (2026-06-11, pause default 12 h -> 5 min, held-out window) as a
village-wide cadence step for the decay of the read-out spike (round 2, after a new card section).
Reuse policy: H125, H97 and H54 plan the same held-out kickoffs with different statistics; disclose in all cards and LOG.md.
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
import h127lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
from embed_models import goal_vectors, load_whitener  # noqa: E402

FROZEN = {"targets": [1, 9, 14, 15, 28, 29, 34, 43, 45, 46, 47, 48, 49, 50], "standins": [11, 12, 13, 38, 39, 40, 41, 42],
          "exclude_agents": [19, 28, 30], "min_days": 5, "C1_share": 0.5, "C2_ratio": 1.5, "C3_bound": -0.5}
FILES = ["hypotheses/H127-content-trails-goal-call-clock/analysis/confirm.py", "hypotheses/H127-content-trails-goal-call-clock/analysis/h127lib.py"]


def git_clean() -> bool:
    out = subprocess.run(["git", "-C", str(L.ROOT), "status", "--porcelain", "--", *FILES], capture_output=True, text=True).stdout
    return out.strip() == ""


def build_units(p: int, allow: bool):
    """In-memory equivalent of H125's and H127's schemes for one kickoff (no files written)."""
    from common import holdout_mask
    cal = pl.read_parquet(L.S / "calendar.parquet").with_columns(pl.col("regime").cast(pl.String)).sort("pt_date")
    cal = cal.with_columns(pl.Series("ho", holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())))
    alld = cal["pt_date"].to_list()
    gd = cal.filter(pl.col("goal_no") == p)
    if not allow:
        gd = gd.filter(~pl.col("ho"))
    days = gd["pt_date"].to_list()
    if len(days) < FROZEN["min_days"] or gd.head(FROZEN["min_days"])["regime"].n_unique() > 1:
        return None
    reg = gd["regime"][0]
    goals = pl.read_parquet(L.ED / "goals.parquet").with_columns(pl.col("kind").cast(pl.String))
    kr = goals.filter((pl.col("goal_no") == p) & (pl.col("kind") == "kickoff"))
    if kr.height == 0:
        return None
    kr = kr.row(0, named=True)
    t0 = kr["win_start"]
    try:
        k54 = pl.read_parquet(L.ROOT / "data/processed/H54-kickoff-quench-target/kickoffs.parquet").filter((pl.col("goal_no") == p) & pl.col("room").is_null())
        if k54.height:
            t0 = k54["t0"][0]
    except Exception:  # noqa: BLE001
        pass
    i0 = alld.index(days[0]); prev = alld[i0 - 1] if i0 > 0 else None
    prev_ok = prev is not None and (allow or not cal.filter(pl.col("pt_date") == prev)["ho"][0])
    st = pl.read_parquet(L.ED / "statements.parquet").with_row_index("row").filter(~pl.col("agent").is_in(FROZEN["exclude_agents"]))
    st = st.filter(((pl.col("goal_no") == p) & pl.col("pt_date").is_in(days[:5])) | (pl.col("pt_date") == (prev if prev_ok else "")))
    if not allow:
        st = st.filter(~pl.Series(holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list())))
    inc = sorted(set(st.filter((pl.col("pt_date") == days[0]) & (pl.col("t") >= t0) & (pl.col("goal_no") == p))["agent"].to_list()))
    m = "bge_small"
    own = load_whitener(reg, 32, m)(goal_vectors(m)[kr["gid"]][None, :].astype(np.float64))[0]; own /= np.linalg.norm(own)
    V = dict(np.load(L.H125 / "vectors.npz")); K = V[f"K|{m}|{reg}"]; kg = V["kick_goal_no"]
    D = K[[j for j, g in enumerate(kg) if g not in (p - 1, p, p + 1, 23)]]
    X = np.asarray(L.statement_matrix(m, "white")[st["row"].to_numpy()], dtype=np.float64)
    st = st.with_columns(pl.Series("a", X @ own - (X @ D.T).mean(1)))
    cw = pl.read_parquet(L.S / "call_windows.parquet", columns=["turn_id", "agent", "pt_date", "t_call"]).filter(pl.col("pt_date") == days[0]).sort("t_call")
    kc = pl.read_parquet(L.S / "kicks_classified.parquet")
    mids = kc.filter((((pl.col("kind") == "human_message") & (pl.col("subkind") == "kickoff")) | (pl.col("kind") == "goal_kickoff"))
                     & (pl.col("goal_no") == p) & pl.col("message_id").is_not_null())["message_id"].to_list()
    items = pl.read_parquet(L.S / "context_ledger_items.parquet", columns=["turn_id", "message_id", "omitted"])
    roturns = set(items.filter(pl.col("message_id").is_in(mids) & ~pl.col("omitted").fill_null(False))["turn_id"].to_list())
    win_end = cal.filter(pl.col("pt_date") == days[0])["win_end"][0]
    hours1 = max((win_end - t0).total_seconds() / 3600, 1e-6)
    units = []
    for i in inc:
        sa = st.filter(pl.col("agent") == i)
        pre = sa.filter((pl.col("pt_date") == prev) | ((pl.col("pt_date") == days[0]) & (pl.col("t") < t0)))["a"].to_numpy()
        sett = sa.filter(pl.col("pt_date").is_in(days[1:5]))["a"].to_numpy()
        d1 = sa.filter((pl.col("pt_date") == days[0]) & (pl.col("t") >= t0)).sort("t")
        c_i = cw.filter((pl.col("agent") == i) & (pl.col("t_call") > t0))
        tc = np.array([t.timestamp() for t in c_i["t_call"].to_list()])
        ro = c_i.filter(pl.col("turn_id").is_in(list(roturns)))
        t_ro = ro["t_call"][0] if ro.height else (c_i["t_call"][0] if c_i.height else None)
        ts = np.array([t.timestamp() for t in d1["t"].to_list()])
        c = np.searchsorted(tc, ts, side="right") if len(tc) else np.zeros(len(ts))
        if t_ro is not None:
            c_ro = c - np.searchsorted(tc, t_ro.timestamp(), side="left"); h_ro = (ts - t_ro.timestamp()) / 3600
        else:
            c_ro = np.full(len(ts), np.nan); h_ro = np.full(len(ts), np.nan)
        pre_fb = len(pre) < L.MIN_PRE
        P = 0.0 if pre_fb else float(pre.mean()); S_ = float(sett.mean()) if len(sett) else np.nan
        se = np.sqrt((pre.var(ddof=1) / len(pre) if not pre_fb else 0.0) + (sett.var(ddof=1) / len(sett) if len(sett) > 1 else np.nan))
        u = dict(design=f"T{p:02d}", agent=i, regime=reg, lab=None, r=len(tc) / hours1, r_lpo=None, n_pre=len(pre), n_set=len(sett),
                 P=P, S=S_, Delta=S_ - P, se_Delta=float(se), pre_fallback=pre_fb, ro_fallback=not ro.height, ro_delay_h=None,
                 a=d1["a"].to_numpy(), h=((ts - t0.timestamp()) / 3600), c=c.astype(float), h_ro=h_ro, c_ro=c_ro.astype(float))
        u["eligible"] = bool(len(sett) >= L.MIN_SET and len(ts) >= L.MIN_DAY1 and len(tc) >= 3)
        u["rising"] = bool(u["eligible"] and u["Delta"] > L.RISE_Z * u["se_Delta"])
        units.append(u)
    return units


def spike_ratio(units):
    v = []
    for u in units:
        if not u["rising"]:
            continue
        y = u["a"] - u["P"]; late = y[u["c_ro"] >= 64]
        A = late.mean() if len(late) >= 4 else u["Delta"]
        e = y[(u["c_ro"] >= 1) & (u["c_ro"] <= 3)]
        if A > 0.02 and len(e):
            v.append(e.mean() / A)
    return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ok", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    print(json.dumps(FROZEN, indent=1))
    if a.dry_run:
        goals, allow = FROZEN["standins"], False
    elif a.confirm and a.ok:
        if not git_clean():
            sys.exit("H127 code has uncommitted changes; commit the frozen version first.")
        import holdout_ledger as HL
        for g in FROZEN["targets"]:
            chk = HL.check("H127", f"G{g:02d}", "content_kickoff_rise_clock", "embedding_content")
            if not chk["allowed"]:
                sys.exit(f"ledger refuses G{g:02d}: {chk['prior_runs_same_family']}")
            if chk["needs_disclosure"]:
                print("disclose:", g, [u["hypothesis"] for u in chk["prior_runs"] + chk["competing_planned"]])
        goals, allow = FROZEN["targets"], True
    else:
        print("Frozen predictions printed; nothing run (pass --dry-run, or both confirm flags with Vivian's sign-off).")
        return
    imm, spikes, pa, per = [], [], [], {}
    for g in goals:
        us = build_units(g, allow)
        if not us:
            continue
        r = L.analyze_kickoff(us, n_boot=0)
        per[g] = dict(n_rise=r["n_rise"], imm_ro=r.get("imm_ro"), s=r.get("s"))
        imm += [x["THro_floor"] for x in r.get("_per_agent", [])]
        pa += r.get("_per_agent", [])
        spikes += spike_ratio(us)
    po = L.pooled_slope(pa, n_boot=1000) if pa else dict(s_pool=np.nan, s_pool_lo=np.nan, s_pool_hi=np.nan)
    out = dict(mode="dry-run" if a.dry_run else "CONFIRMATORY", per=per,
               C1=dict(share=float(np.mean(imm)) if imm else None, n=len(imm), pass_=bool(imm and np.mean(imm) >= FROZEN["C1_share"])),
               C2=dict(ratio=float(np.mean(spikes)) if spikes else None, n=len(spikes), pass_=bool(spikes and np.mean(spikes) >= FROZEN["C2_ratio"])),
               C3=dict(pooled=po, pass_=bool(po["s_pool_lo"] <= 0 <= po["s_pool_hi"] or po["s_pool_hi"] > FROZEN["C3_bound"])),
               run_at=dt.datetime.now(dt.timezone.utc).isoformat())
    name = "confirm_dryrun.json" if a.dry_run else "confirm_results.json"
    (L.DATA / name).write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps({k: v for k, v in out.items() if k != "per"}, indent=1, default=float))


if __name__ == "__main__":
    main()
