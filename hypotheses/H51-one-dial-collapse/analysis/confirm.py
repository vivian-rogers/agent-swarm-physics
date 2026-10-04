"""H51 confirmatory run on the LOCKED HOLDOUT. Written and frozen 2026-10-04 after round 1; NOT RUN.

Guard: touches held-out data only with BOTH `--confirm` and H51_CONFIRM=1, only if `holdout_ledger.check` allows every
target, only if this file's SHA-256 equals the one stored by `--freeze` in results/frozen_model.json, and only if the
upstream confirmatory axis rows exist (H67 `readout_loop_gain_g_lag` with confirmatory=True on the target units).
Otherwise it refuses. `--dry-run` runs the identical scoring on non-holdout stand-in periods (scratch output only).
`--freeze` fits the frozen models on non-holdout periods only (part of round 1; no held-out row is read).

Targets: held-out goal periods for which H67's confirm script produces g_lag: #22, #28 (regime I), #43 and the #51 tail
(regime III). Observables computed here on the targets: Y2 herding share (H11 definition, as in the scheme) and Y4 loop
rate (DQ5 flags). Y1 (H48) and Y3 (H34 ledger trees) enter only if their owners' confirmatory rows exist.

Frozen predictions (from round 1: the one-dial collapse failed; see the card):
  C1  D1 does not beat regime labels out of sample: on the targets, for every available observable, the frozen D1 model
      (Y ~ g_lag, non-holdout fit) has a mean squared prediction error >= 0.9 x that of the frozen regime-only model.
  C2  The one-dial residual is not smaller in regime III: mean |z_D1| over regime-III targets >= 0.8 x its round-1 value
      (no hidden collapse where the coupling is non-zero).
Reading: C1 + C2 confirm "g_lag is not a one-dial collapse variable"; a C1 failure (D1 beats regime by > 10% on every
available observable) would revive HH178.
Reuse policy (hypotheses/holdout.md): H51's statistics are new (collapse residuals), but its inputs are H67's g_lag
(H67 must run first) and loop / herding statistics that H12, H11 and H06 plan on the same periods. Disclose before running.

Usage:
  uv run python hypotheses/H51-one-dial-collapse/analysis/confirm.py --freeze
  uv run python hypotheses/H51-one-dial-collapse/analysis/confirm.py --dry-run
  H51_CONFIRM=1 uv run python hypotheses/H51-one-dial-collapse/analysis/confirm.py --confirm
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
import h51lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "hypotheses/H51-one-dial-collapse/scheme"))
import build as B  # noqa: E402

FROZEN = L.DATA / "results/frozen_model.json"
OUT = L.DATA / "confirm"
SCRATCH = Path(os.environ.get("TMPDIR", "/tmp")) / "h51_confirm_dryrun"
TARGET_GOALS = {22: "I", 28: "I", 43: "III", 51: "III"}
TARGET_LEDGER = {22: "G22", 28: "G28", 43: "G43", 51: "#51-tail"}
STANDINS = {27: "I", 24: "I", 42: "III", 44: "III"}
OBS_CONFIRM = ["Y2_herd", "Y4_loop"]
CRIT = dict(C1_ratio=0.9, C2_ratio=0.8)


def sha_self() -> str:
    txt = Path(__file__).read_text()
    return hashlib.sha256(txt.encode()).hexdigest()


def freeze():
    d = L.common_sample(L.load("primary"))
    model = {"sha256": sha_self(), "obs": {}, "crit": CRIT}
    for j in L.OBS:
        s = d.filter(pl.col(j).is_not_null())
        y = s[j].to_numpy().astype(float)
        K = s["K"].to_numpy().astype(float)
        A = np.column_stack([np.ones(len(y)), K])
        coef, *_ = np.linalg.lstsq(A, y, rcond=None)
        sd = float(np.std(y - A @ coef, ddof=2))
        reg_mean = {r: float(s.filter(pl.col("regime") == r)[j].mean()) for r in ("I", "II", "III")
                    if s.filter(pl.col("regime") == r).height}
        _, predK = L.lopo_r2(y, K[:, None])
        z3 = np.abs((y - predK) / sd)[s["regime"].to_numpy() == "III"]
        model["obs"][j] = {"a": float(coef[0]), "b": float(coef[1]), "sd": sd, "regime_mean": reg_mean,
                           "mean_abs_z_III": float(z3.mean()) if len(z3) else None, "n": len(y)}
    L.jdump(model, FROZEN)
    print("frozen", json.dumps(model, indent=1)[:1500])


def target_obs(goal: int, days: list[str] | None, allow_holdout: bool) -> dict:
    """Y2 and Y4 for one target (held-out reads only when allow_holdout)."""
    s = pl.read_parquet(B.SH / "embeddings/statements.parquet", columns=["kind", "t", "pt_date", "goal_no", "holdout"])
    f = pl.read_parquet(B.SH / "statement_flags.parquet", columns=["self_repeat"])
    d = pl.concat([s, f], how="horizontal_extend").filter((pl.col("kind") == "chat") & (pl.col("goal_no") == goal))
    if days is not None:
        d = d.filter(pl.col("pt_date").is_in(days))
    if not allow_holdout:
        assert not d["holdout"].any()
    p = pl.read_parquet(B.SH / "project_states.parquet").filter(
        (pl.col("goal_no") == goal) & (pl.col("w_min") == 30) & (pl.col("sources") == "all") & pl.col("project").is_not_null())
    if days is not None:
        p = p.filter(pl.col("pt_date").is_in(days))
    if not allow_holdout:
        assert not p["holdout"].any()
    p = p.select("pt_date", "win", "agent", "room", pl.col("project").cast(pl.String))
    ex, _, _ = B.herd_share(p)
    lr = float(d["self_repeat"].mean()) if d.height else np.nan
    return {"Y2_herd": ex, "Y4_loop": float(L.logit(lr)) if np.isfinite(lr) else np.nan}


def score(rows: list[dict], model: dict) -> dict:
    res = {"targets": rows, "C1": {}, "C2": {}}
    c1 = []
    for j in OBS_CONFIRM:
        m = model["obs"][j]
        ok = [r for r in rows if np.isfinite(r.get(j, np.nan)) and np.isfinite(r.get("K", np.nan))]
        if not ok:
            continue
        eK = np.mean([(r[j] - (m["a"] + m["b"] * r["K"])) ** 2 for r in ok])
        eR = np.mean([(r[j] - m["regime_mean"][r["regime"]]) ** 2 for r in ok])
        res["C1"][j] = {"mse_D1": float(eK), "mse_regime": float(eR), "ratio": float(eK / eR) if eR > 0 else None}
        c1.append(eR > 0 and eK / eR >= CRIT["C1_ratio"])
    res["C1"]["pass"] = bool(c1 and all(c1))
    z3 = []
    for j in OBS_CONFIRM:
        m = model["obs"][j]
        for r in rows:
            if r["regime"] == "III" and np.isfinite(r.get(j, np.nan)) and np.isfinite(r.get("K", np.nan)):
                z3.append(abs(r[j] - (m["a"] + m["b"] * r["K"])) / m["sd"] / (m["mean_abs_z_III"] or 1.0))
    res["C2"] = {"mean_rel_abs_z_III": float(np.mean(z3)) if z3 else None,
                 "pass": bool(z3 and np.mean(z3) >= CRIT["C2_ratio"])}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--freeze", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    a = ap.parse_args()
    if a.freeze:
        freeze()
        return
    model = json.loads(FROZEN.read_text())
    if a.dry_run:
        dd = L.load("primary")
        rows = []
        for g, reg in STANDINS.items():
            r = target_obs(g, None, allow_holdout=False)
            r.update(goal_no=g, regime=reg, K=float(dd.filter(pl.col("goal_no") == g)["K"][0]))
            rows.append(r)
        out = score(rows, model)
        SCRATCH.mkdir(parents=True, exist_ok=True)
        (SCRATCH / "dryrun.json").write_text(json.dumps({"sha256": sha_self(), **out}, indent=1, default=float))
        print(json.dumps(out, indent=1, default=float))
        return
    if not a.confirm or os.environ.get("H51_CONFIRM") != "1":
        sys.exit("refused: needs --confirm and H51_CONFIRM=1 (Vivian's sign-off)")
    if sha_self() != model["sha256"]:
        sys.exit("refused: confirm.py changed since --freeze (re-freeze needs a dated card amendment)")
    sys.path.insert(0, str(L.ROOT / "infra/shared"))
    import holdout_ledger as HL  # noqa: E402
    for g in TARGET_GOALS:
        chk = HL.check("H51", TARGET_LEDGER[g], "multi", ["one_dial_collapse"])
        if not chk["allowed"]:
            sys.exit(f"refused by holdout ledger: {chk}")
    est = pl.read_parquet(B.SH / "per_period_estimates.parquet").filter(
        (pl.col("hypothesis") == "H67") & (pl.col("statistic") == "readout_loop_gain_g_lag") & pl.col("confirmatory"))
    pu = pl.read_parquet(B.SH / "period_units.parquet").filter(pl.col("holdout") & pl.col("goal_no").is_in(list(TARGET_GOALS)))
    rows = []
    for g, reg in TARGET_GOALS.items():
        units = pu.filter(pl.col("goal_no") == g)
        if g == 51:
            units = units.filter(pl.col("unit_id") == "51m")
        k = est.filter(pl.col("period_unit").is_in(units["unit_id"].to_list() + [f"G{g:02d}"]))
        if not k.height:
            sys.exit(f"refused: no confirmatory H67 g_lag rows for #{g} (run H67 confirm first)")
        days = sum((list(x) for x in units["days"].to_list()), [])
        r = target_obs(g, days, allow_holdout=True)
        r.update(goal_no=g, regime=reg, K=float(k["estimate"].mean()))
        rows.append(r)
    out = score(rows, model)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "confirm_result.json").write_text(json.dumps({"sha256": sha_self(), **out}, indent=1, default=float))
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
