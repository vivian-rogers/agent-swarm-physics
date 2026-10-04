"""H45 confirmatory script (LOCKED HOLDOUT). Written 2026-10-04 after exploratory round 1. NOT RUN.

Frozen predictions (card "Confirmatory design"; thresholds fixed from round 1, before any holdout data is loaded):
  C1 regulation fails (replication): in each held-out regime-III target with >= 30 band segments, the regulation index
     RI < 0.5 with its day-bootstrap upper bound < 0.5, and eps lies within 0.25 of the passive value 1 - s_bar.
     Targets: #45, #46, #47, #49, #50 (#43 and #48 are one-day periods: reported, not scored); the #51 tail (51m).  [0.85]
  C2 no own-content lever: |eta_W| < 0.25 in >= 4 of the scored targets.                                            [0.8]
  C3 the reply-based dilution exponent replicates: beta (E1, cloglog with agent-day effects) in [0.6, 1.2] with the
     CI excluding 0 in >= 4 of the scored targets (round 1, regime III: 0.79-1.12, pooled 0.98).                     [0.7]
  C4 no homeostat signature in engagement: in the pooled held-out regime-III talk calls, NOT (g_R < 0 and g_W > 0
     with both CIs excluding 0).                                                                                     [0.75]
  C5 post-erasure talk undershoot: pooled over the held-out regime-III targets, the k-adjusted talk ratio in calls
     1-3 after a forced reset lies in [0.5, 0.95] with the CI's upper bound < 1 (round 1: 0.74 [0.69, 0.80]), i.e. no
     homeostatic import burst and a talk dip.                                                                          [0.65]
  C6 NE22 (2026-06-11, the 200-event cap; inside #46): cap-hit calls are < 0.5% of #46c calls, and the set point
     s* of agents present in 46b and 46c moves by less than the passive prediction (1 - s_bar) * dln(lambda) + 0.2
     (a scaffold ceiling on k per call cannot set the share).                                                        [0.7]

Reuse disclosure (hypotheses/holdout.md policy): #45 was used by H02 (activity couplings) and is planned by H23 (message
content); #46/#47 are targets of H26's and H47's unrun confirm scripts (content statistics); NE22 is planned by H08 and
H18 (backlog response). H45's observables (prompt-token context composition, reply-parent engagement against prompt
size) are a different statistic and modality from all of these. Disclose in this card, the other cards and LOG.md
before running.

Safeguards:
  * refuses to run on the holdout without --confirm --i-understand-this-uses-the-locked-holdout;
  * refuses unless this script, the card, h45lib.py, run_periods.py and scheme/build.py are tracked and unmodified in git;
  * --dry-run uses non-holdout stand-ins (#41, #42, #44, unit 51l for the targets; 51k -> 51l for NE22), builds the
    table in memory without the holdout, asserts no holdout day is loaded, and checks that the in-memory build
    reproduces run_periods' RI for #41 and #44 within 0.02.

Usage: uv run python hypotheses/H45-context-homeostasis/analysis/confirm.py --dry-run
       uv run python hypotheses/H45-context-homeostasis/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h45lib as L  # noqa: E402

ROOT = L.ROOT
TARGETS = [45, 46, 47, 49, 50]
REPORT_ONLY = [43, 48]
STANDINS = [41, 42, 44]
FILES = ["hypotheses/H45-context-homeostasis/analysis/confirm.py", "hypotheses/H45-context-homeostasis/README.md",
         "hypotheses/H45-context-homeostasis/analysis/h45lib.py", "hypotheses/H45-context-homeostasis/analysis/run_periods.py",
         "hypotheses/H45-context-homeostasis/scheme/build.py"]


def git_clean() -> bool:
    for f in FILES:
        tracked = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--error-unmatch", f], capture_output=True).returncode == 0
        dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", f], capture_output=True, text=True).stdout.strip()
        if not tracked or dirty:
            print(f"refusing: {f} is untracked or modified", file=sys.stderr)
            return False
    return True


def load_build():
    spec = importlib.util.spec_from_file_location("h45build", ROOT / "hypotheses/H45-context-homeostasis/scheme/build.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def prepared(include_holdout: bool) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Same preparation as run_periods.prepare, from an in-memory build."""
    import run_periods as RP
    c = load_build().build(include_holdout=include_holdout)
    if not include_holdout:
        assert not c["holdout"].any(), "dry run loaded holdout rows"
    cal = L.load_calibration()                   # frozen round-1 calibration (non-holdout fit)
    cu = L.add_share(c.filter((pl.col("ctx_mode") == "cu") & pl.col("seg").is_not_null()), cal)
    seg = (cu.group_by("seg").agg(pl.col("agent").first(), pl.col("pt_date").first(), pl.col("t_first").min().alias("t0"))
           .sort("agent", "t0").with_columns(pl.col("pt_date").shift(-1).over("agent").alias("next_date")))
    cu = cu.join(seg.select("seg", "next_date"), on="seg", how="left")
    vol = (pl.col("next_date") == pl.col("pt_date")) & (pl.col("end_consol").fill_null(False) & ~pl.col("end_forced").fill_null(False))
    cu = cu.with_columns(vol.fill_null(False).alias("end_consol"), pl.lit(False).alias("end_forced_lever"))
    talks = c.filter(pl.col("talk") & pl.col("eng_pending").is_not_null())
    return cu, talks, RP


def score(cu, talks, RP, targets, unit_target=None, B=200) -> dict:
    res = {"per_target": {}}
    for g in targets:
        r = RP.period_stats(cu, talks, g, B=B)
        res["per_target"][f"G{g:02d}"] = {k: r.get(k) for k in ("regulation", "beta", "share_dependence", "reset_forced_talk",
                                                                 "n_cu_calls", "days")}
    if unit_target:
        x = cu.filter(pl.col("unit_id").cast(pl.Utf8) == unit_target)
        bs = L.band_segments(x)
        res["per_target"][unit_target] = {"regulation": L.elasticities(bs, group_cols=("agent",), B=B),
                                          "beta": L.fit_beta_glm(L.talk_rows(talks.filter(pl.col("unit_id").cast(pl.Utf8) == unit_target)), B=100)}
    pooled = cu.filter(pl.col("goal_no").is_in(targets) | (pl.col("unit_id").cast(pl.Utf8) == (unit_target or "")))
    res["pooled_share_dependence"] = L.share_dependence(L.talk_rows(pooled), B=100)
    res["pooled_overshoot"] = L.reset_profile(pooled, "open_forced", "talk", B=100)
    # verdicts
    pt = res["per_target"]
    scored = [k for k, v in pt.items() if (v.get("regulation") or {}).get("n_seg", 0) >= 30]
    c1 = [pt[k]["regulation"]["RI"] < 0.5 and pt[k]["regulation"]["RI_ci"][1] < 0.5
          and abs(pt[k]["regulation"]["eps"] - pt[k]["regulation"]["eps_passive"]) < 0.25 for k in scored]
    c2 = [abs(pt[k]["regulation"]["eta_W"]) < 0.25 for k in scored]
    c3 = [(pt[k].get("beta") or {}).get("beta") is not None and 0.6 <= pt[k]["beta"]["beta"] <= 1.2
          and pt[k]["beta"]["beta_ci"][0] > 0 for k in scored]
    sd = res["pooled_share_dependence"]
    c4 = not ("g_R" in sd and sd["g_R_ci"][1] < 0 and sd["g_W_ci"][0] > 0)
    ov = res["pooled_overshoot"].get("overshoot")
    res["verdicts"] = {"scored_targets": scored, "C1": bool(all(c1)) if c1 else None, "C2": sum(c2) >= min(4, len(scored)),
                       "C3": sum(c3) >= min(4, len(scored)), "C4": bool(c4),
                       "C5": (ov is not None and 0.5 <= ov <= 0.95 and res["pooled_overshoot"]["overshoot_ci"][1] < 1)}
    return res


def ne22(cu, units=("46b", "46c"), B=200) -> dict:
    a, b = units
    x = cu.filter(pl.col("unit_id").cast(pl.Utf8).is_in(list(units)))
    sp = L.set_points(x, by=("agent", "unit_id"), min_calls=30)
    bs = L.band_segments(x)
    lam = bs.group_by("agent", "unit_id").agg(pl.col("lam").median().alias("lam_seg"))
    sp = sp.join(lam, on=["agent", "unit_id"]).with_columns(pl.col("unit_id").cast(pl.Utf8))
    piv = sp.pivot(on="unit_id", index="agent", values=["s_star", "lam_seg"]).drop_nulls()
    if piv.height < 3:
        return {"n_agents": piv.height}
    s_bar = float(sp["s_star"].mean())
    ds = np.log(piv[f"s_star_{b}"].to_numpy()) - np.log(piv[f"s_star_{a}"].to_numpy())
    dl = np.log(piv[f"lam_seg_{b}"].to_numpy()) - np.log(piv[f"lam_seg_{a}"].to_numpy())
    pred = (1 - s_bar) * dl
    cap = x.filter(pl.col("unit_id").cast(pl.Utf8) == b)
    return {"n_agents": piv.height, "median_dlns": float(np.median(ds)), "median_passive_pred": float(np.median(pred)),
            "C6_share_moves_less": bool(np.median(ds) < np.median(pred) + 0.2),
            "cap_hit_share": float(cap["cap_hit"].mean()) if cap.height else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--B", type=int, default=200)
    a = ap.parse_args()
    if a.dry_run:
        cu, talks, RP = prepared(include_holdout=False)
        res = score(cu, talks, RP, STANDINS, unit_target="51l", B=a.B)
        ref = {}
        for g in (41, 44):
            p = L.DATA / f"G{g:02d}" / "results.json"
            if p.exists():
                ref[g] = json.loads(p.read_text())["regulation"]["RI"]
        for g, v in ref.items():
            got = res["per_target"][f"G{g:02d}"]["regulation"]["RI"]
            assert abs(got - v) < 0.02, f"dry run does not reproduce G{g} RI: {got} vs {v}"
        res["ne22_standin"] = ne22(cu, units=("51k", "51l"), B=a.B)
        (L.DATA / "confirm_dryrun.json").write_text(json.dumps(res, indent=1, default=float))
        print(json.dumps(res["verdicts"], indent=1), json.dumps(res["ne22_standin"], indent=1))
        return
    if not (a.confirm and a.ack):
        sys.exit("refusing: pass --confirm --i-understand-this-uses-the-locked-holdout (or --dry-run)")
    if not git_clean():
        sys.exit(1)
    cu, talks, RP = prepared(include_holdout=True)
    cu = cu.filter(pl.col("holdout"))
    talks = talks.filter(pl.col("holdout"))
    res = score(cu, talks, RP, TARGETS, unit_target="51m", B=a.B)
    res["report_only"] = {f"G{g:02d}": RP.period_stats(cu, talks, g, B=a.B).get("regulation") for g in REPORT_ONLY}
    res["ne22"] = ne22(cu)
    out = L.DATA / "confirm"
    out.mkdir(exist_ok=True)
    (out / "confirm.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res["verdicts"], indent=1), json.dumps(res["ne22"], indent=1))


if __name__ == "__main__":
    main()
