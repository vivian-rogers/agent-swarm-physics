"""H42 confirmatory script (locked holdout). WRITTEN, NOT RUN in round 1.

Runs the frozen round-1 estimator (world B call-clock TALK model with class baselines; world A H03-world comparator;
nulls) on held-out units and scores the frozen predictions below. Without the guard flags it refuses to touch the
holdout; --dry-run runs the identical pipeline on non-holdout stand-in units (no holdout data read).

  uv run python hypotheses/H42-readout-hawkes-kernel/analysis/confirm.py --dry-run
  uv run python hypotheses/H42-readout-hawkes-kernel/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout

Reuse policy (hypotheses/holdout.md): every target is checked with infra/shared/holdout_ledger.check (estimator
family hawkes_branching, modality event timing). Targets where the check returns allowed=False are refused:
#45-#50 and NE21+NE23 (H04 already ran Hawkes branching there), which is why the brief's NE20 (#45) and NE44
(NE21+NE23 window) are NOT targets. All allowed targets still need disclosure in both cards and LOG.md; H03, H08 and
H19 have planned (not run) Hawkes-family statistics on some of them: H42's statistic (read-out kernel cross gain and
n_cross in the call-clock world) is a different statistic, disclosed here.

Frozen predictions: see PREDICTIONS (written 2026-10-04 after exploratory round 1; numbers in the card). C5 freezes
a post-hoc exploratory finding (named messages carry the read-out excitation) for confirmation.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import h42lib as L  # noqa: E402

GUARD = ("--confirm", "--i-understand-this-uses-the-locked-holdout")
# held-out targets (unit ids from period_units) and their non-holdout stand-ins for the dry run
TARGETS = {
    "51m": {"goal": 51, "regime": "III", "standin": "51l", "kind": "#51-tail", "ledger": "#51-tail"},
    "28": {"goal": 28, "regime": "I", "standin": "26", "kind": "regime I (C)", "ledger": "G28"},
    "22a": {"goal": 22, "regime": "I", "standin": "21a", "kind": "regime I (F)", "ledger": "G22"},
    "22b": {"goal": 22, "regime": "I", "standin": "21b", "kind": "regime I (F)", "ledger": "G22"},
    "29a": {"goal": 29, "regime": "I", "standin": "27", "kind": "regime I (K)", "ledger": "G29"},
    "43": {"goal": 43, "regime": "III", "standin": "42b", "kind": "regime III, 1 day", "ledger": "G43"},
}
def _f(r, k, default=np.nan):
    v = r.get(k)
    return default if v is None else v


def _c1(rows):
    """regime III: world-B n_cross(B) <= 0.05 (the shared-field floor) in every held-out regime-III unit, and <= 0.02
    in the #51 tail (late-#51 collapse continues)."""
    r3 = [r for r in rows if r["regime"] == "III"]
    ok = all(_f(r, "B:B:nx") <= 0.05 for r in r3)
    tail = [r for r in r3 if r["target"].startswith("51")]
    ok_tail = all(_f(r, "B:B:nx") <= 0.02 for r in tail)
    return {"units": len(r3), "values": {r["target"]: _f(r, "B:B:nx") for r in r3}, "pass": bool(ok and ok_tail)}


def _c2(rows):
    """regime I: world-B read-out excitation absent (n_cross(B) <= max(day-block max, 0.01) and held-out gain(B) <=
    0.5 mnats/event where >= 2 days) while world-A exponential n_cross(A) >= 0.04 (timing co-modulation reappears)."""
    r1 = [r for r in rows if r["regime"] == "I"]
    res = {}
    for r in r1:
        thr = max(_f(r, "B:B:dayblock_max", 0.0) or 0.0, 0.01)
        gain = (_f(r, "B:B:cv") - _f(r, "B:S0:cv")) * 1e3 if r.get("B:B:cv") is not None else np.nan
        res[r["target"]] = {"nxB": _f(r, "B:B:nx"), "thr": thr, "gainB_mnats": gain, "nxA": _f(r, "A:A:nx"),
                            "pass": bool(_f(r, "B:B:nx") <= thr and (not np.isfinite(gain) or gain <= 0.5)
                                         and _f(r, "A:A:nx") >= 0.04)}
    k = sum(v["pass"] for v in res.values())
    return {"units": res, "n_pass": k, "pass": bool(len(res) and k >= 0.75 * len(res))}


def _c3(rows):
    """every held-out unit with >= 2 days: the call-clock world beats the H03 world on held-out log-likelihood by
    >= 0.3 nats/event (best spec vs best spec)."""
    vals = {}
    for r in rows:
        if r.get("B:S0:cv") is None:
            continue
        bB = max(_f(r, f"B:{s}:cv", -np.inf) for s in ("S0", "B", "A_g", "C_g"))
        bA = max(_f(r, f"A:{s}:cv", -np.inf) for s in ("S0", "A"))
        vals[r["target"]] = bB - bA
    return {"diff": vals, "pass": bool(len(vals) and all(v >= 0.3 for v in vals.values()))}


def _c4(rows):
    """shape: where world-B n_cross(B) > 0.005, >= 80% of B's mass sits at the read-out call and the next one."""
    v = {r["target"]: _f(r, "B:B:B01") for r in rows if _f(r, "B:B:nx", 0) > 0.005}
    return {"values": v, "pass": bool(all(x >= 0.8 for x in v.values())) if v else None}


def _c5(rows):
    """POST HOC finding frozen for confirmation: in regime III, messages that NAME the recipient excite its talk at
    read-out (world B): extra talk per named message >= 0.05 and named n_cross > its shift-null max, while unnamed
    messages stay at or below their shift-null max (or <= 0.005 per message)."""
    r3 = [r for r in rows if r["regime"] == "III" and "m:per_named" in r]
    res = {r["target"]: {"per_named": r["m:per_named"], "named_gt_null": r["m:named_gt_null"],
                         "per_unnamed": r["m:per_unnamed"], "unnamed_le_null": r["m:unnamed_le_null"]} for r in r3}
    ok = all(v["per_named"] >= 0.05 and v["named_gt_null"] and (v["unnamed_le_null"] or v["per_unnamed"] <= 0.005)
             for v in res.values())
    return {"units": res, "pass": bool(res) and ok}


# Frozen 2026-10-04 (after exploratory round 1, before any holdout run). C1-C3 are the round-1 reading (call clock,
# not cross-excitation, sets talk timing; read-out excitation small and regime-dependent); C4 the hop-1 shape.
PREDICTIONS = {"C1_regimeIII_small": {"fn": _c1}, "C2_regimeI_absent": {"fn": _c2},
               "C3_call_clock_wins": {"fn": _c3}, "C4_hop1_shape": {"fn": _c4}, "C5_named_readout": {"fn": _c5}}
OUT = L.DATA / "confirm"


def ledger_ok(target: str) -> dict:
    sys.path.insert(0, str(L.ROOT / "infra/shared"))
    import holdout_ledger as hl
    return hl.check("H42", target, "event timing", "hawkes_branching")


def run_one(u: L.Unit) -> dict:
    rng = np.random.default_rng(20261004)
    res = {"unit_id": u.unit_id, "n_days": u.n_days, "n_talk": len(u.talk)}
    for world, SP, specs in (("B", L.WORLD_B_SPECS, ["S0", "B", "A_g", "C_g"]), ("A", L.WORLD_A_SPECS, ["S0", "A"])):
        ds = L.build_talk(u, world=world)
        fits = {}
        for s in specs:
            f = L.fit_spec(ds, SP, s, warm=fits.get("S0"))
            fits[s] = f
            br = L.branching(ds, f)
            res[f"{world}:{s}:nx"] = br["n_cross"]
            if world == "B" and s == "B" and br["n_cross"] > 0:
                c = br["contrib"]
                res["B:B:B01"] = (c.get("B_0", 0) + c.get("B_1", 0)) / br["n_cross"]
        if ds.D >= 2:
            cvr = L.cv(ds, SP, specs)
            for s, (ll, n) in cvr.items():
                res[f"{world}:{s}:cv"] = ll / max(n, 1)
        own = "B" if world == "B" else "A"
        nulls = []
        for _ in range(5):
            items, _k = L.shift_items(u, rng)
            dn = L.build_talk(u, world=world, items_override=items, only_cross=True, base=ds)
            f0 = L.fit_spec(dn, SP, "S0")
            nulls.append(L.branching(dn, L.fit_spec(dn, SP, own, warm=f0))["n_cross"])
        res[f"{world}:{own}:shift_q95"] = float(np.quantile(nulls, 0.95))
        db = []
        for k in range(1, min(3, u.n_days - 1) + 1):
            dn = L.build_talk(u, world=world, items_override=L.dayblock_items(u, k), only_cross=True, base=ds)
            f0 = L.fit_spec(dn, SP, "S0")
            db.append(L.branching(dn, L.fit_spec(dn, SP, own, warm=f0))["n_cross"])
        res[f"{world}:{own}:dayblock_max"] = float(max(db)) if db else None
    if u.regime == "III":
        import posthoc_mention as PM
        m = PM.run_unit(u)
        nI = u.items.filter(pl.col("kind") == "agent").height
        nN = max(m["n_named_items"], 1)
        res["m:per_named"] = m["n_named"] * m["n_events"] / nN
        res["m:per_unnamed"] = m["n_unnamed"] * m["n_events"] / max(nI - nN, 1)
        res["m:named_gt_null"] = bool(m["n_named"] > m["null_named_max"])
        res["m:unnamed_le_null"] = bool(m["n_unnamed"] <= m["null_unnamed_max"] + 1e-12)
    return res


def score(rows: list[dict]) -> dict:
    out = {}
    for name, p in PREDICTIONS.items():
        out[name] = p["fn"](rows)
    return out


def main():
    argv = sys.argv
    dry = "--dry-run" in argv
    real = all(g in argv for g in GUARD)
    if not dry and not real:
        print("Refusing: pass --dry-run (stand-ins) or both guard flags", GUARD)
        sys.exit(2)
    if real and dry:
        print("Choose one of --dry-run / --confirm"); sys.exit(2)
    rows = []
    if dry:
        out = L.DATA / "confirm_dryrun"
        for tgt, meta in TARGETS.items():
            uid = meta["standin"]
            u = L.load_unit(uid)
            assert not pl.read_parquet(L.ROOT / "data/processed/shared/period_units.parquet").filter(
                pl.col("unit_id") == uid)["holdout"][0], "stand-in must be non-holdout"
            r = run_one(u)
            r.update(target=tgt, standin=uid, regime=meta["regime"])
            rows.append(r)
            print(tgt, "<-", uid, {k: round(v, 4) for k, v in r.items() if isinstance(v, float)}, flush=True)
    else:
        import build as scheme_build
        out = OUT
        for tgt, meta in TARGETS.items():
            chk = ledger_ok(meta["ledger"])
            if not chk["allowed"]:
                print(f"{tgt}: refused by the reuse policy ({chk['prior_runs_same_family']})"); continue
        allowed = [t for t, m in TARGETS.items() if ledger_ok(m["ledger"])["allowed"]]
        scheme_build.build(holdout_units=allowed, out_root=OUT / "extract")
        for tgt in allowed:
            u = L.load_unit(tgt, TARGETS[tgt]["goal"], root=OUT / "extract")
            r = run_one(u)
            r.update(target=tgt, regime=TARGETS[tgt]["regime"])
            rows.append(r)
    out.mkdir(parents=True, exist_ok=True)
    pl.DataFrame(rows).write_parquet(out / "confirm_rows.parquet")
    sc = score(rows)
    (out / "confirm_scores.json").write_text(json.dumps(sc, indent=1, default=float))
    print(json.dumps(sc, indent=1, default=float))


if __name__ == "__main__":
    main()
