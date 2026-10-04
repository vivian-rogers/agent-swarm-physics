"""H08 confirmatory test on the LOCKED HOLDOUT. Written 2026-10-04 after exploratory round 1. NOT RUN.

  uv run python hypotheses/H08-context-is-the-coupling/analysis/confirm_holdout.py --dry-run
  uv run python hypotheses/H08-context-is-the-coupling/analysis/confirm_holdout.py --confirm --i-understand-this-uses-the-locked-holdout

Run the real version only after the card and this script are committed and Vivian signs off. `--dry-run` runs the
identical code on non-holdout stand-ins (its numbers have no bearing on the hypothesis).

Predictions (also on the card, "Confirmatory predictions"):
- CF1 (C9, primary design; regime-III held-out units #43, #45, #46, #47, #48, #49, #50, #51 tail = 8 units):
  D_addr > 0 with CI excluding 0 in >= 7/8; D_talk > 0 with CI excluding 0 in >= 5/8; the reply/refractory
  signature pre_addr = G_addr(0) - G_addr(-1) < 0 (point) in >= 6/8.
- CF2 (C9, recipients that did not talk at o = -2, -1; all 10 held-out units incl. regime-I #28, #29): D_addr > 0 with
  CI excluding 0 in >= 8/10, and the floor |G_addr(0)| < 1/3 G_addr(1) in >= 8/10.
- CF3 (C8, #51 tail only): nudge -> target A30 > 0 (CI excludes 0); onset lags the zero-parameter read-out prediction,
  Phi(1,5)_measured - Phi(1,5)_predicted < -0.2 (point); in the day-split CV the context model beats the immediate and
  Hawkes families in >= 60% of splits but beats the constant-delay family in < 60%.
- CF4 (C3 / NE41; regime-III held-out units, random-effects pooled): beta_F < 0 with CI excluding 0; pooled relative
  drop in [-0.35, -0.08]; beta_V < 0.
- CF5 (C1; the Claude Code agent's held-out days #28, #29, #32 and #34): recall >= 0.9 and replay share < 5% in each;
  during #34 (incl. the #voted-out stints) other-room coverage <= 5%; median delay of the current feed < 60 s.
Holdout reuse (policy in hypotheses/holdout.md): #45 (H02 activity couplings; H04 kernels/Hawkes as segment A1) and
#46-#50 (H04 Hawkes n, nudge-kernel A30, MF) -> C8 is NOT tested there (kernels already computed); C9's turn-offset
discontinuity, C3's erasure-coupling and C1's fetch logs were never computed on any held-out period. NE12 (H05) and
NE30 days enter only through CF5 (fetch-log modality). Disclose in both cards and LOG.md when run.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h08lib import *  # noqa: E402,F403

FLAG = "--i-understand-this-uses-the-locked-holdout"
R3_UNITS = [43, 45, 46, 47, 48, 49, 50, "51tail"]
R1_UNITS = [28, 29]
CC_UNITS = [28, 29, 32, 34]


def heldout_days(u) -> list[str]:
    cal = calendar().filter(pl.col("window_s") > 0)
    if u == "51tail":
        return sorted(cal.filter((pl.col("goal_no") == 51) & pl.col("holdout"))["pt_date"].to_list())
    return sorted(cal.filter(pl.col("goal_no") == u)["pt_date"].to_list())


def standins():
    """Non-holdout stand-ins with the same code path (dry run)."""
    g51 = period_days(51)
    return {"r3": {42: period_days(42), 44: period_days(44), "51tail": g51[-10:]},
            "r1": {30: period_days(30), 31: period_days(31)},
            "c8": g51[-15:], "cc": [30, 31, 33]}


def unit_goal(u):
    return 51 if u == "51tail" else int(u)


def run(dry: bool):
    import build_turns as bt
    import visibility as vis
    import erasure as er
    import kernels as kn
    out_root = OUT / ("confirm_dryrun" if dry else "confirm")
    out_root.mkdir(parents=True, exist_ok=True)
    if dry:
        S = standins()
        r3 = S["r3"]; r1 = S["r1"]; c8_days = S["c8"]; cc_units = S["cc"]
    else:
        r3 = {u: heldout_days(u) for u in R3_UNITS}
        r1 = {u: heldout_days(u) for u in R1_UNITS}
        c8_days = heldout_days("51tail"); cc_units = CC_UNITS
        for u, ds in {**r3, **r1}.items():
            assert all(is_holdout(d, unit_goal(u)) for d in ds), f"{u}: not all held out"
    chat = chat_table()
    expo = pl.read_parquet(SH / "exposure.parquet", columns=["msg", "agent"])
    tl = bt.room_lookup()
    chat_day = dict(zip(*[chat.select("msg", "pt_date")[c].to_list() for c in ("msg", "pt_date")]))
    res = {"dry_run": dry, "units": {}}
    for u, ds in {**r3, **r1}.items():
        if not ds:
            res["units"][str(u)] = {"n_days": 0}
            continue
        folder = out_root / f"U{u}"
        bt.build_period(unit_goal(u), chat, expo, tl, days=ds, out_dir=folder)
        c9 = vis.run_period(unit_goal(u), chat_day, seed=7, folder=folder)
        ent = {"n_days": len(ds), "regime": "III" if u in r3 else "I"}
        if c9 and "talk" in c9.get("primary", {}):
            p, c = c9["primary"], c9.get("posthoc_clean", {})
            ent.update({"D_talk": p["talk"]["D"], "D_addr": p["addr"]["D"], "pre_addr": p["addr"]["pre"],
                        "clean_D_addr": c.get("addr", {}).get("D"),
                        "clean_floor": (c.get("addr", {}).get("G", {}).get(0) or c.get("addr", {}).get("G", {}).get("0")),
                        "clean_top": (c.get("addr", {}).get("G", {}).get(1) or c.get("addr", {}).get("G", {}).get("1"))})
        if u in r3:
            ros = pl.read_parquet(SH / "roster.parquet").select(pl.col("agent").alias("id"), "name").to_dicts()
            sys.path.insert(0, str(ROOT / "infra/shared"))
            from common import mention_regexes
            c3 = er.run(unit_goal(u), set(mention_regexes(ros).keys()), folder=folder, kinds="segment")
            if c3 and "beta" in c3:
                ent.update({"beta_F": c3["beta"]["erased_F"], "beta_V": c3["beta"]["erased_V"], "rel_F": c3.get("rel_F"),
                            "n_CF": c3["n_erased"].get("CF", 0)})
        res["units"][str(u)] = ent
    # CF3: #51 tail kernel
    k = kn.run_period(51, chat, days=c8_days, folder=out_root / "U51tail_c8")
    s = k["out"]["sets"].get("nudge_target_iso", {}) if k else {}
    res["c8"] = {"n_cells": s.get("n_cells"), "A30": s.get("shape", {}).get("A30"),
                 "phi_diff": s.get("shape", {}).get("phi_1_5_diff_hr"), "ctx_wins": s.get("cv", {}).get("ctx_wins_share")}
    # CF5: Claude Code agent
    import build_cc_exposure as bce
    import cc_exposure as cce
    if dry:
        cce.main(cc_dir=OUT / "cc", periods=cc_units, out_name="c1_confirm_dryrun.json")
        c1 = json.loads((OUT / "cc/c1_confirm_dryrun.json").read_text())
    else:
        bce.main(allow=True, out_dir=out_root / "cc")
        cce.main(cc_dir=out_root / "cc", periods=cc_units, out_name="c1_confirm.json")
        c1 = json.loads((out_root / "cc/c1_confirm.json").read_text())
    res["c1"] = {g: {k_: r.get(k_) for k_ in ("recall", "replay_share", "other_room_coverage", "delay_s")}
                 for g, r in c1["periods"].items()}
    res["verdicts"] = evaluate(res, r3, r1)
    jdump(res, out_root / ("dryrun.json" if dry else "confirm.json"))
    print(json.dumps(res["verdicts"], indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    write_provenance(("confirm_dryrun" if dry else "confirm") + "/*", "hypotheses/H08-context-is-the-coupling/analysis/confirm_holdout.py",
                     ["shared tables", "claude_code_messages", "events"], {"dry_run": dry, "units": [str(u) for u in {**r3, **r1}]})


def evaluate(res, r3, r1):
    U = res["units"]
    v = {}
    r3u = [U[str(u)] for u in r3 if "D_addr" in U.get(str(u), {})]
    n = len(r3u)
    a = sum(x["D_addr"][1] > 0 for x in r3u); t = sum(x["D_talk"][1] > 0 for x in r3u); pre = sum(x["pre_addr"][0] < 0 for x in r3u)
    need = (7, 5, 6) if n == 8 else (int(np.ceil(7 / 8 * n)), int(np.ceil(5 / 8 * n)), int(np.ceil(6 / 8 * n)))
    v["CF1"] = {"units": n, "addr": a, "talk": t, "pre_neg": pre, "pass": a >= need[0] and t >= need[1] and pre >= need[2]}
    allu = [U[str(u)] for u in list(r3) + list(r1) if U.get(str(u), {}).get("clean_D_addr")]
    m = len(allu)
    ca = sum(x["clean_D_addr"][1] > 0 for x in allu)
    fl = sum(abs(x["clean_floor"][0]) < x["clean_top"][0] / 3 for x in allu if x.get("clean_floor") and x.get("clean_top"))
    v["CF2"] = {"units": m, "addr": ca, "floor": fl, "pass": ca >= np.ceil(0.8 * m) and fl >= np.ceil(0.8 * m)}
    c8 = res["c8"]
    if c8.get("A30") and c8.get("ctx_wins"):
        w = c8["ctx_wins"]
        fam = {"imm": min(w.get("imm", 0), w.get("imm_hr", 0)), "hawkes": w.get("hawkes", 0),
               "delay": min(w.get("delay", 0), w.get("delay_hr", 0))}
        v["CF3"] = {"A30": c8["A30"], "phi_diff": c8["phi_diff"], "fam": fam,
                    "pass": c8["A30"][1] > 0 and c8["phi_diff"][0] < -0.2 and fam["imm"] >= 0.6 and fam["hawkes"] >= 0.6 and fam["delay"] < 0.6}
    else:
        v["CF3"] = {"pass": None, "note": "kernel not estimable"}
    import erasure as er
    bf = [U[str(u)]["beta_F"] for u in r3 if U.get(str(u), {}).get("beta_F") and U[str(u)].get("n_CF", 0) >= 50]
    rf = [U[str(u)]["rel_F"] for u in r3 if U.get(str(u), {}).get("rel_F") and U[str(u)].get("n_CF", 0) >= 50]
    bv = [U[str(u)]["beta_V"] for u in r3 if U.get(str(u), {}).get("beta_V")]
    pf = er.dl_meta([x[0] for x in bf], [(x[2] - x[1]) / 3.92 for x in bf])
    pr = er.dl_meta([x[0] for x in rf], [(x[2] - x[1]) / 3.92 for x in rf])
    pv = er.dl_meta([x[0] for x in bv], [(x[2] - x[1]) / 3.92 for x in bv])
    if pf and pr and pv:
        v["CF4"] = {"beta_F": pf, "rel_F": pr, "beta_V": pv,
                    "pass": (pf["mu"] + 1.96 * pf["se"] < 0) and (-0.35 <= pr["mu"] <= -0.08) and pv["mu"] < 0}
    else:
        v["CF4"] = {"pass": None, "note": "too few units"}
    c1 = res["c1"]
    ok = True
    for g, r in c1.items():
        if r.get("recall") is None:
            continue
        ok &= r["recall"] >= 0.9 and (r.get("replay_share") or 0) < 0.05
        if r.get("delay_s"):
            ok &= r["delay_s"]["50"] < 60
        if g == "G34" and r.get("other_room_coverage") is not None:
            ok &= r["other_room_coverage"] <= 0.05
    v["CF5"] = {"pass": bool(ok), "periods": list(c1.keys())}
    return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument(FLAG, dest="ack", action="store_true")
    a = ap.parse_args()
    if a.dry_run:
        run(dry=True)
        return
    if not (a.confirm and a.ack):
        sys.exit(f"Refusing: the confirmatory run uses the locked holdout. Pass --confirm {FLAG} (after sign-off), "
                 "or --dry-run for the non-holdout stand-ins.")
    run(dry=False)


if __name__ == "__main__":
    main()
