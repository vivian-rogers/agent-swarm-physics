"""H121 confirmatory run on the LOCKED HOLDOUT. Written and frozen 2026-10-04 after round 1; NOT RUN.

Guard: runs on held-out data only with BOTH `--confirm` and H121_CONFIRM=1, only if `holdout_ledger.check` allows
every target, and only after H67's confirmatory run has written g_lag for the same held-out units
(data/processed/H67-lagged-criticality-dial/confirm/confirm_result.json). Otherwise it refuses. `--dry-run` runs the
identical pipeline on non-holdout stand-in units (H67 exploratory g_lag) and writes to a scratch directory.

Targets (period units of): #22, #28 (regime I), #43 and the #51 tail (regime III).

Frozen predictions (estimators = round 1's: scheme/build.py, h121lib.unit_estimate with B = 200, posthoc.stats with a
unit-day cluster bootstrap B = 400; thresholds fixed from round 1):
  C1  Registered single-exponential test fails (predicted): the regime-III targets' random-effects pooled K_boot (HH form)
      lies above 2 (point estimate > 2). [The HH's kill, predicted to fire again.]
  C2  Fast part on the call clock (post hoc in round 1, forward here): pooled over regime-III targets, K_fast =
      tau_fast / tau_pred lies in [0.5, 2] (point), with tau_fast from the first-call ratio e(1)/e(0) over the
      k = 20-60 plateau. Round 1: 2.0 [0.8, 23]. Evaluated on #43 alone if the #51-tail spike is absent (see C5).
  C3  Regime I fast part is shorter than one update: pooled regime-I tau_fast < 1 call (upper CI < 1.5). Round 1:
      0.54 [0.41, 0.67].
  C4  Slow part: regime-III slow excess (mean talk at k = 20-240 over the steady state, minus 1) > 0 with the CI
      excluding 0. Round 1: +0.12 [0.04, 0.20].
  C5  Spike size by regime: regime-I e(0) >= 0.2 (round 1: 0.36); #51-tail e(0) CI includes 0 (round 1 late #51,
      51f/51g: e(0) -0.01 / -0.03, no first-call spike).
Reading: C1 + C2 + C4 confirm "the boot is a fast call-clock spike near tau0/(1 - g_lag) plus a slow day-scale talk
excess that the single-exponential Glauber relation misses". C2 is the only test of the HH's coupling relation that
survives round 1; it is weak, because tau_pred is about 1 call wherever rho_self <= 0.37.

Reuse policy (hypotheses/holdout.md): H67 (talk read-out, same targets) must run first and its g_lag is an input, not a
second use of the same statistic. H99 (curie_weiss_gain) and H25/H19 (equal-time dial) plan the same targets with
other statistics; disclose. The boot curve (talk share by call index since boot) has not been computed on any target.

Usage:
  uv run python hypotheses/H121-daily-boot-quench/analysis/confirm.py --dry-run
  H121_CONFIRM=1 uv run python hypotheses/H121-daily-boot-quench/analysis/confirm.py --confirm
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import build as B  # noqa: E402
import h121lib as L  # noqa: E402
import posthoc as PH  # noqa: E402

ROOT = HERE.parents[2]
SH = ROOT / "data/processed/shared"
sys.path.insert(0, str(ROOT / "infra/shared"))
OUT = ROOT / "data/processed/H121-daily-boot-quench/confirm"
EXPL = ROOT / "data/processed/H121-daily-boot-quench"
H67_CONFIRM = ROOT / "data/processed/H67-lagged-criticality-dial/confirm/confirm_result.json"
H67_EXPL = ROOT / "data/processed/H67-lagged-criticality-dial/results/units.parquet"
SCRATCH = Path(os.environ.get("TMPDIR", "/tmp")) / "h121_confirm_dryrun"
TARGET_GOALS = {22: "I", 28: "I", 43: "III", 51: "III"}
STANDINS = {"27": "I", "24": "I", "41": "III", "51g": "III"}     # 51g plays the #51 tail in the dry run
FROZEN = dict(C1=dict(K_min=2.0), C2=dict(band=(0.5, 2.0)), C3=dict(tau_max=1.0, hi_max=1.5), C4=dict(lo_min=0.0),
              C5=dict(e0_I_min=0.2))


def unit_rows(base: Path, uid: str, g: float, gse: float, K: int) -> dict:
    df = pl.read_parquet(base / "calls" / f"{uid}.parquet")
    e = L.unit_estimate(df, K, g, gse, B=200, seed=1)
    return {"unit": uid, **{k: v for k, v in e.items() if not isinstance(v, (list, dict))}}


def frame(base: Path, uids: list[str], tau_pred: dict) -> pl.DataFrame:
    parts = []
    for j, u in enumerate(uids):
        d = (pl.read_parquet(base / "calls" / f"{u}.parquet", columns=["agent", "day", "k", "Y", "ss", "kickoff_day"])
             .filter(pl.col("k") <= 240)
             .with_columns((pl.col("day").cast(pl.Int32) + 1000 * j).alias("uday"), pl.lit(tau_pred[u]).alias("tau_pred")))
        parts.append(d)
    return pl.concat(parts)


def ss_rate(base, uids):
    num = den = 0.0
    for u in uids:
        d = pl.read_parquet(base / "calls" / f"{u}.parquet", columns=["Y", "ss"]).filter(pl.col("ss"))
        num += float(d["Y"].sum()); den += d.height
    return num / den


def score(base: Path, units: dict, regime_of: dict, tail: set) -> dict:
    """units: uid -> dict(g, gse, K)."""
    rows = [unit_rows(base, u, v["g"], v["gse"], v["K"]) for u, v in units.items()]
    df = pl.DataFrame([r for r in rows if r.get("ok")], infer_schema_length=None)
    df = df.with_columns(pl.col("unit").replace_strict(regime_of, default=None).alias("regime"))
    out = {"units": df.to_dicts()}
    s3 = df.filter(pl.col("regime") == "III")
    mk, sek, _ = L.re_pool(np.log(np.clip(s3["K"].to_numpy(), 1e-6, None)), np.nan_to_num(s3["ln_K_se"].to_numpy(), nan=1.0))
    out["C1_detail"] = {"K_pool": float(np.exp(mk)), "lo": float(np.exp(mk - 1.96 * sek)), "hi": float(np.exp(mk + 1.96 * sek))}
    out["C1"] = bool(np.exp(mk) > FROZEN["C1"]["K_min"])
    tp = {r["unit"]: r["tau_pred"] for r in df.to_dicts()}
    reg_units = {g: [u for u in df["unit"].to_list() if regime_of[u] == g] for g in ("I", "III")}
    PH.B = 400
    st = {}
    for g, us in reg_units.items():
        if us:
            st[g] = PH.boot(frame(base, us, tp), ss_rate(base, us), 1)
    tail_us = [u for u in reg_units["III"] if u in tail]
    nontail = [u for u in reg_units["III"] if u not in tail]
    st["tail"] = PH.boot(frame(base, tail_us, tp), ss_rate(base, tail_us), 2) if tail_us else None
    out["C5_detail"] = {"e0_I": st.get("I", {}).get("e0"), "tail_e0": None if st["tail"] is None else
                        [st["tail"]["e0"], st["tail"]["e0_lo"], st["tail"]["e0_hi"]]}
    tail_spike_absent = st["tail"] is not None and st["tail"]["e0_lo"] <= 0 <= st["tail"]["e0_hi"]
    out["C5"] = bool((st.get("I", {}).get("e0", 0) >= FROZEN["C5"]["e0_I_min"]) and tail_spike_absent)
    c2_src = PH.boot(frame(base, nontail, tp), ss_rate(base, nontail), 3) if (tail_spike_absent and nontail) else st.get("III")
    lo, hi = FROZEN["C2"]["band"]
    out["C2_detail"] = {k: c2_src.get(k) for k in ("tau_fast", "tau_fast_lo", "tau_fast_hi", "K_fast", "K_fast_lo", "K_fast_hi")} | \
        {"units": nontail if tail_spike_absent else reg_units["III"]}
    out["C2"] = bool(c2_src.get("K_fast") is not None and np.isfinite(c2_src["K_fast"]) and lo <= c2_src["K_fast"] <= hi)
    sI = st.get("I", {})
    out["C3_detail"] = {k: sI.get(k) for k in ("tau_fast", "tau_fast_lo", "tau_fast_hi")}
    out["C3"] = bool(sI and sI["tau_fast"] < FROZEN["C3"]["tau_max"] and sI["tau_fast_hi"] < FROZEN["C3"]["hi_max"])
    s3p = st.get("III", {})
    out["C4_detail"] = {k: s3p.get(k) for k in ("slow_excess", "slow_excess_lo", "slow_excess_hi")}
    out["C4"] = bool(s3p and s3p["slow_excess_lo"] > FROZEN["C4"]["lo_min"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if a.dry_run:
        meta = pl.read_parquet(EXPL / "unit_meta.parquet")
        g67 = pl.read_parquet(H67_EXPL)
        units = {}
        for u in STANDINS:
            m = meta.filter(pl.col("unit_id") == u).to_dicts()[0]
            gr = g67.filter(pl.col("unit_id") == u).to_dicts()[0]
            units[u] = {"g": gr["g"], "gse": (gr["g_hi"] - gr["g_lo"]) / 3.92, "K": m["K_max"]}
        out = score(EXPL, units, STANDINS, {"51g"})
        SCRATCH.mkdir(parents=True, exist_ok=True)
        (SCRATCH / "dryrun.json").write_text(json.dumps({"sha256": sha, **out}, indent=1, default=float))
        print(json.dumps({k: v for k, v in out.items() if k != "units"}, indent=1, default=float))
        return
    if not (a.confirm and os.environ.get("H121_CONFIRM") == "1"):
        sys.exit("refusing: confirmatory run needs --confirm and H121_CONFIRM=1 (Vivian's sign-off)")
    if not H67_CONFIRM.exists():
        sys.exit("refusing: H67's confirmatory g_lag (confirm_result.json) is the unfitted input; run H67's confirm first")
    import holdout_ledger as HL
    for g in TARGET_GOALS:
        tgt = "#51-tail" if g == 51 else f"G{g}"
        chk = HL.check("H121", tgt, "talk", ["other"])
        if not chk["allowed"]:
            sys.exit(f"refusing: holdout ledger blocks {tgt}: {chk['prior_runs_same_family']}")
    g67 = {r["unit"]: r for r in json.loads(H67_CONFIRM.read_text())["units"]}
    pu = pl.read_parquet(SH / "period_units.parquet").filter(pl.col("holdout") & pl.col("goal_no").is_in(list(TARGET_GOALS)))
    pu = pu.filter((pl.col("goal_no") != 51) | (pl.col("first_day") >= "2026-09-07"))
    cal = pl.read_parquet(SH / "calendar.parquet")
    cw, og = B.load_shared(allow_holdout=True)
    regime_of, tail, units = {}, set(), {}
    for u in pu.to_dicts():
        r = B.build_unit(u, cw, og, cal, out_dir=OUT, allow_holdout=True)
        if r is None or r["n_agentdays"] < 8 or u["unit_id"] not in g67:
            continue
        gg = g67[u["unit_id"]]
        units[u["unit_id"]] = {"g": gg["g"], "gse": gg.get("g_se") or (gg["g_hi"] - gg["g_lo"]) / 3.92, "K": r["K_max"]}
        regime_of[u["unit_id"]] = TARGET_GOALS[u["goal_no"]]
        if u["goal_no"] == 51:
            tail.add(u["unit_id"])
    out = score(OUT, units, regime_of, tail)
    (OUT / "confirm_result.json").write_text(json.dumps({"sha256": sha, **out}, indent=1, default=float))
    print(json.dumps({k: v for k, v in out.items() if k != "units"}, indent=1, default=float))


if __name__ == "__main__":
    main()
