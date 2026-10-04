"""H30 confirmatory test on the LOCKED HOLDOUT (written 2026-10-03 after exploratory round 1; NOT RUN).

Targets and reuse (hypotheses/holdout.md, reuse policy):
  T1  #51 tail (2026-09-07 -> 09-21): primary. No confirmatory run has used it (H13 and H15 scripts list it; not run).
      Statistics: activity response to nudges, content response to human messages, daily-gauge stability.
  T2  #45: secondary. H02 used it for activity-timing couplings (and a Curie-Weiss betaJ0); H23 plans message-content
      statistics of the leader. H30's statistics differ (kick-triggered activity response; alignment of recipients'
      statements with operator-message directions). Disclosed in the card and to be logged in LOG.md.
  T3  #46-#50 (inside NE21+NE23): CONTENT ONLY. H04 ran activity responses to nudges there (C1-C4), so H30 must not
      compute any activity statistic on these days; the code path below never builds activity panels for T3.

Refuses to run on the holdout without BOTH --confirm and --i-understand-this-uses-the-locked-holdout, and refuses
if the H30 folder has uncommitted changes (predictions must be committed first). --dry-run runs the identical code on
non-holdout stand-ins (T1: the last 10 non-holdout days of #51; T2: #44; T3: #41 and #42) and writes confirm_dryrun/.

NOTE (found in round 1, from non-holdout days only): every automated message (nudges and the daily pause/resume
bookends) stops after 2026-08-20, undocumented in the CHANGELOG. The #51 tail may therefore have no nudges; nothing
about the tail was looked at. Activity predictions on T1 are conditional on >= 30 N_tgt kicks there (else n/a).

Predictions (C-*). Rules use day-block bootstrap 95% CIs (1000 draws).
  C-act (primary)   random-effects pooled chi_act(N_tgt), pre-registered model (no day FE), over the activity-eligible
                    targets (T2 always; T1 if it has >= 30 N_tgt kicks): > 0 with CI excluding 0.  [G51: 0.59 [0.24, 0.93]]
  C51-1 (secondary, conditional) chi_act(N_tgt) on T1 > 0 with CI excluding 0 (n/a if < 30 N_tgt kicks).
  C51-2 (primary)   chi_con(H_und), orthogonalized: > 0, CI excluding 0.                    [round 1: 0.025 [0.014, 0.033]]
  C51-3 (secondary) first-nudge chi_act (day FE) > repeat-nudge chi_act (day FE): point difference > 0.  [1.36 vs 0.26]
  C51-4 (secondary) bystander chi_act(N_by), pre-registered model: |point| <= 0.3.            [0.13 [-0.11, 0.38]]
  C51-5 (secondary) daily chi_act(N_tgt) (day FE): message-permutation p >= 0.05 or permutation-calibrated R1 < 0.5,
                    and lag-1 autocorrelation p >= 0.05 (no usable day-to-day signal).
  C51-6 (secondary) chi_con(N_tgt): |point| < 0.02 (template nudges carry no message-specific content).
  C45-1 (secondary) chi_act(N_tgt) point > 0.
  C45-2 (secondary) chi_con(H_und) point > 0.
  C4650-1 (primary for T3) random-effects pooled chi_con over human recipients (H_und and H_men pairs) across
                    #46-#50: > 0 with CI excluding 0.                                        [round 1 pooled H_und 0.026]
  C4650-2 (secondary) pooled chi_con(N_tgt) across #46-#50: |point| < 0.02.
Overall: supported if every testable primary passes; failed if no testable primary passes; mixed otherwise.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h30lib import *  # noqa: E402,F403
import run_period as RP  # noqa: E402
from build import build_period  # noqa: E402

FLAGS = ("--confirm", "--i-understand-this-uses-the-locked-holdout")


def holdout_days_of(goal: int, start: str | None = None, end: str | None = None) -> list[str]:
    c = calendar().filter((pl.col("goal_no") == goal) & (pl.col("window_s") > 0))
    if start:
        c = c.filter(pl.col("pt_date") >= start)
    if end:
        c = c.filter(pl.col("pt_date") < end)
    return sorted(c["pt_date"].to_list())


def targets(mode: str) -> dict:
    if mode == "confirm":
        return {"T1": ("G51", holdout_days_of(51, "2026-09-07", "2026-09-21")),
                "T2": ("G45", holdout_days_of(45)),
                "T3": [(f"G{g}", holdout_days_of(g)) for g in (46, 47, 48, 49, 50)]}
    g51 = [d for d in period_days(51) if "2026-08-07" <= d < "2026-08-21"]   # last 10 non-holdout days with nudges
    return {"T1": ("G51", g51), "T2": ("G44", period_days(44)),
            "T3": [("G41", period_days(41)), ("G42", period_days(42))]}


def fval(c):
    return None if not c or c[0] is None else c[0]


def ok_pos(c):
    """CI excludes 0 from above; a degenerate bootstrap CI (all mass on one day) does not count."""
    return bool(c and c[0] is not None and c[1] is not None and c[2] is not None and c[2] - c[1] > 1e-9 and c[1] > 0)


def content_only(p: str, days: list[str], allow: bool, out: Path) -> dict:
    """T3: content statistics only (no activity panels or responses are built)."""
    info = build_period(p, allow_holdout=allow, days=days, out_dir=out)
    cs = pl.read_parquet(out / "content.parquet")
    nd = info["n_days"]; W = boot_weights(nd, 1000)
    res = {"n_days": nd, "n_messages": info["n_messages"]}
    hum = cs.filter(pl.col("cls").is_in(["H_und", "H_men"]) & pl.col("chi_orth").is_not_nan())
    res["con_human"] = boot_mean_by_day(hum, "chi_orth", np.arange(nd), W) if hum.height >= 10 else None
    res["n_human_pairs"] = hum.height
    nt = cs.filter((pl.col("cls") == "N_tgt") & pl.col("chi_orth").is_not_nan())
    res["con_Ntgt"] = boot_mean_by_day(nt, "chi_orth", np.arange(nd), W) if nt.height >= 10 else None
    res["n_Ntgt_pairs"] = nt.height
    return res


def dl(est, ses):
    est, ses = np.asarray(est, float), np.asarray(ses, float)
    ok = np.isfinite(est) & np.isfinite(ses) & (ses > 0)
    est, ses = est[ok], ses[ok]
    if len(est) == 0:
        return None
    w = 1 / ses ** 2; mu = (w * est).sum() / w.sum()
    Q = (w * (est - mu) ** 2).sum(); df = max(len(est) - 1, 1)
    tau2 = max(0.0, (Q - df) / (w.sum() - (w ** 2).sum() / w.sum())) if len(est) > 1 else 0.0
    ws = 1 / (ses ** 2 + tau2); m = (ws * est).sum() / ws.sum(); s = np.sqrt(1 / ws.sum())
    return [float(m), float(m - 1.96 * s), float(m + 1.96 * s)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="understand", action="store_true")
    a = ap.parse_args()
    if not a.dry_run:
        if not (a.confirm and a.understand):
            sys.exit(f"Refusing: the confirmatory run needs both {FLAGS[0]} and {FLAGS[1]} (or use --dry-run).")
        dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--", "hypotheses/H30-operator-susceptibility"],
                               capture_output=True, text=True).stdout.strip()
        if dirty:
            sys.exit("Refusing: commit the H30 card and this script before the holdout run (reuse policy, condition 1).")
    mode = "dryrun" if a.dry_run else "confirm"
    allow = not a.dry_run
    root = OUT / ("confirm_dryrun" if a.dry_run else "confirm")
    T = targets("dryrun" if a.dry_run else "confirm")
    out = {"mode": mode, "targets": {k: (v if k != "T3" else [x[0] for x in v]) for k, v in
                                     {"T1": T["T1"][0], "T2": T["T2"][0], "T3": T["T3"]}.items()}}
    rows = []

    def add(id_, primary, obs, passed):
        rows.append({"id": id_, "primary": primary, "observed": obs, "pass": passed})

    # ---- T1 (#51 tail or stand-in)
    p, days = T["T1"]
    d1 = root / "T1"
    build_period(p, allow_holdout=allow, days=days, out_dir=d1)
    R1 = RP.run_period(p, days=days, allow_holdout=allow, out_dir=d1, fig_dir=d1 / "figures", do_h04=False, n_swap=10)
    n_t1 = R1["act_n"].get("N_tgt") or 0
    c11 = R1["act_nofe"].get("N_tgt") if n_t1 >= 30 else None
    add("C51-1", False, {"chi": c11, "n_kicks": n_t1}, ok_pos(c11) if n_t1 >= 30 else None)
    c12 = (R1["con"].get("H_und") or {}).get("orth"); add("C51-2", True, c12, ok_pos(c12))
    fr, rp = (R1.get("act_first") or {}).get("N_tgt"), (R1.get("act_repeat") or {}).get("N_tgt")
    add("C51-3", False, {"first": fr, "repeat": rp}, bool(fval(fr) is not None and fval(rp) is not None and fval(fr) > fval(rp)))
    c14 = R1["act_nofe"].get("N_by"); add("C51-4", False, c14, bool(fval(c14) is not None and abs(fval(c14)) <= 0.3))
    s = R1["stability"].get("act_N_tgt", {})
    no_signal = (s.get("p_perm_msg", 1) >= 0.05 or (s.get("R1_perm_msg") or 0) < 0.5) and (s.get("p_lag1") is None or s["p_lag1"] >= 0.05)
    add("C51-5", False, {k: s.get(k) for k in ("n_days_eligible", "p_perm_msg", "R1_perm_msg", "lag1", "p_lag1")}, bool(no_signal))
    c16 = (R1["con"].get("N_tgt") or {}).get("orth"); add("C51-6", False, c16, bool(fval(c16) is not None and abs(fval(c16)) < 0.02))
    # ---- T2 (#45 or stand-in)
    p, days = T["T2"]
    d2 = root / "T2"
    build_period(p, allow_holdout=allow, days=days, out_dir=d2)
    R2 = RP.run_period(p, days=days, allow_holdout=allow, out_dir=d2, fig_dir=d2 / "figures", do_h04=False, n_swap=10)
    c21 = R2["act_nofe"].get("N_tgt"); add("C45-1", False, c21, bool(fval(c21) is not None and fval(c21) > 0))
    acts = [c for c in ([c11] if c11 else []) + ([c21] if c21 and (R2["act_n"].get("N_tgt") or 0) >= 10 else [])
            if c and c[1] is not None]
    pooled_act = dl([c[0] for c in acts], [(c[2] - c[1]) / 3.92 for c in acts]) if acts else None
    add("C-act", True, {"pooled": pooled_act, "k": len(acts)}, ok_pos(pooled_act) if acts else None)
    c22 = (R2["con"].get("H_und") or {}).get("orth"); add("C45-2", False, c22, bool(fval(c22) is not None and fval(c22) > 0))
    # ---- T3 (#46-#50 or stand-ins): content only
    t3 = {}
    for p, days in T["T3"]:
        t3[p] = content_only(p, days, allow, root / "T3" / p)
    hum = [(v["con_human"][0], (v["con_human"][2] - v["con_human"][1]) / 3.92) for v in t3.values()
           if v.get("con_human") and v["con_human"][1] is not None]
    pooled = dl([h[0] for h in hum], [h[1] for h in hum]) if hum else None
    add("C4650-1", True, {"pooled": pooled, "per_period": {k: v.get("con_human") for k, v in t3.items()}}, ok_pos(pooled))
    nt = [(v["con_Ntgt"][0], (v["con_Ntgt"][2] - v["con_Ntgt"][1]) / 3.92) for v in t3.values()
          if v.get("con_Ntgt") and v["con_Ntgt"][1] is not None]
    pn = dl([h[0] for h in nt], [h[1] for h in nt]) if nt else None
    add("C4650-2", False, pn, bool(pn is not None and abs(pn[0]) < 0.02))
    prim = [r["pass"] for r in rows if r["primary"] and r["pass"] is not None]
    overall = ("untestable" if not prim else "supported" if all(prim) else ("failed" if not any(prim) else "mixed"))
    out.update({"rows": rows, "overall": overall, "t3": t3})
    jdump(out, root / "confirm_results.json")
    print(f"[{mode}] overall: {overall}")
    for r in rows:
        print(f"  {r['id']:8s} {'P' if r['primary'] else 's'} pass={r['pass']}  {r['observed']}")


if __name__ == "__main__":
    main()
