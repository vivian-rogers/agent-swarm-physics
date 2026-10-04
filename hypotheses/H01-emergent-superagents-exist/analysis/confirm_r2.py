"""H01 round 2 CONFIRMATORY test on the LOCKED HOLDOUT. Written 2026-10-04 after exploratory round 2. NOT RUN.

Refuses to read any holdout day unless BOTH flags are given:
    --confirm --i-understand-this-uses-the-locked-holdout
`--dry-run` runs the identical statistics on non-holdout stand-ins (no holdout day is read).

Frozen criteria (also in goalperiod-subhypotheses/NE30/README.md and NE24/README.md; machine-readable in PREDICTIONS):
  C1  NE30 same-family succession (Gemini 3 Pro -> Gemini 3.1 Pro, 2026-03-09, inside #34). Crews (strict writers of a
      shared project, membership from #34's pre-swap days) that contained Gemini 3 Pro. R7 predicts:
      (a) the crew's writes per bin on R_G over the 2 active days after the swap, relative to the 2 days before, plus the
          predecessor's pre-swap write share, is >= 0 (no loss beyond the departed share; one-sided, the point estimate);
      (b) Gemini 3.1 Pro writes on a project of the predecessor's crews within its first 2 active days.
      Both -> supported; neither -> failed; otherwise mixed. n = 1 succession: descriptive strength only.
  C2  R6b allocation continuity across nights (leave-target-day-out membership) in every holdout unit with a work
      ledger (>= 2 days, >= 100 strict writes, >= 4 writers): Delta C >= 0.2 in >= 2/3 of them.
  C3  R6c continuity after memory loss (H15 ML/MG rule, applied by H15's own build on holdout days): event rate minus
      base rate > -0.2, over unique (agent, day) events of crew members (A2); inconclusive if < 15 unique agent-days.
  C4  NE24 artifact migration (GitHub -> GitLab, 2026-06-29; inside the NE21+NE23 window, same day as NE21's last
      hours switch). The unit-store scramble. Crews alive on github.com projects in the 2 active days before.
      R7 ("dissolves when its artifact is scrambled") predicts: (a) re-formation rate < 0.5, re-formation = >= 2 former
      members co-write one gitlab.com project within the 3 active days after; (b) former members' V_adv (any project)
      over days 1-2 after drops below their 2 days before by more than the median night-to-night change of crews in the
      same window. Rival (the unit is carried by its members and channel, the artifact is replaceable): re-formation >= 0.5.
  C5  R4d ranking on holdout units with >= 2 rooms or labs: Delta C of crews and co-allocation communities exceeds that
      of rooms and labs in >= 2/3 of eligible units.
  (R4 timing individuality, R5 KW kernel and R8a are not confirmed: A1 found them not identifiable at village
   sampling; running them on the holdout would spend it for nothing.)

Holdout reuse (hypotheses/holdout.md policy): #34 is targeted by unrun confirm scripts of H01 (round 1), H05, H07, H12,
H19, H21; #45 by H02 (run: activity timing), H23 (message content), H11 (project labels), H13; NE30 by H15
(`confirm_ne30.py`, per-agent write-turn deficits). This script's observables are crew-level continuity and
re-formation statistics of strict write events on shared projects: a different statistic from every earlier one,
not examined by anyone. Must be disclosed in the H01 card, the H15 card (NE30) and LOG.md before running, and the
script committed first.

Run:   uv run python hypotheses/H01-emergent-superagents-exist/analysis/confirm_r2.py --dry-run
Real:  ... --confirm --i-understand-this-uses-the-locked-holdout     (only after Vivian signs off)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import r2lib as L  # noqa: E402  (thread caps)
import r2_run as RR  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

R2 = RR.R2
SH = RR.SH
PRED = {
    "C1": "NE30: crew V_cnt rel. change + predecessor share >= 0 AND successor writes on a predecessor crew project within 2 active days",
    "C2": "R6b: Delta C >= 0.2 (leave-out) in >= 2/3 of holdout units with a work ledger",
    "C3": "R6c: memory-loss continuity event - base > -0.2 (>= 15 events, else inconclusive)",
    "C4": "NE24: crew re-formation on gitlab < 0.5 AND former members' V_adv drop beyond the median night change",
    "C5": "R4d: Delta C(crew, coalloc) > Delta C(room, lab) in >= 2/3 of eligible holdout units",
}
GEMINI3, GEMINI31 = "Gemini 3 Pro", "Gemini 3.1 Pro"
NE30_DAY, NE24_DAY = "2026-03-09", "2026-06-29"


def confirm_unit_fn(goal_no: int, pt_date: str) -> str:
    if goal_no == 34:
        return "34a" if pt_date < NE30_DAY else "34b"
    if goal_no == 51:
        return "51t"
    return str(int(goal_no))


# ============================================================================ criteria
def c2_c5(D, K_all):
    out = {"C2": {}, "C5": {}}
    for i, u in enumerate(D.units):
        P = D.period(u)
        if len(P.days) < 2:
            continue
        r = {k: RR.continuity_leaveout(D, u, P, K_all[u["unit"]], k, n_perm=400, seed=777 + i)
             for k in ("crew", "coalloc", "room", "lab", "sub")}
        out["C2"][u["unit"]] = r["crew"]
        art = [r[k]["dC"] for k in ("crew", "coalloc") if r.get(k)]
        base = [r[k]["dC"] for k in ("room", "lab") if r.get(k)]
        if art and base:
            out["C5"][u["unit"]] = {"artifact": art, "baseline": base, "win": bool(min(art) > max(base))}
    dc = [v["dC"] for v in out["C2"].values() if v]
    out["C2_verdict"] = ("supported" if dc and sum(x >= 0.2 for x in dc) >= 2 / 3 * len(dc) else "failed") if dc else "n/a"
    w = [v["win"] for v in out["C5"].values()]
    out["C5_verdict"] = ("supported" if w and sum(w) >= 2 / 3 * len(w) else "failed") if w else "n/a"
    return out


def c3(D, K_all):
    _, mem = RR.r6_night_and_memory(D, K_all, 778)
    n = mem["n_unique_agent_days"]          # A2: unique agent-days, not crew-member rows
    if n < 15:
        v = "inconclusive"
    else:
        v = "supported" if mem["unique_diff"] > -0.2 else "failed"
    return {"memory": {k: mem.get(k) for k in ("n_event", "n_unique_agent_days", "n_unique_agents", "unique_event_rate",
                                               "base_rate", "unique_diff", "diff")}, "verdict": v}


def succession(D, K_all, pre_unit, post_unit, pred_name, succ_name, swap_day):
    """C1 statistic, also used by the dry-run stand-in with another departure/arrival pair."""
    name2a = {v: k for k, v in D.name.items()}
    pred, succ = name2a.get(pred_name), name2a.get(succ_name)
    w = D.w.filter(pl.col("strict"))
    pre_days = sorted({d for u in D.units if u["unit"] == pre_unit for d in u["days"]})
    post_days = sorted({d for u in D.units if u["unit"] == post_unit for d in u["days"]})
    pre2 = [d for d in pre_days if d < swap_day][-2:]
    post2 = [d for d in post_days if d >= swap_day][:2]
    if not pre2 or not post2 or pred is None or succ is None:
        return {"ok": False, "why": "days or agents missing"}
    wp = w.filter(pl.col("pt_date").is_in(pre_days) & (pl.col("pt_date") < swap_day))
    projs = wp.group_by("project").agg(pl.col("agent").n_unique().alias("nw"), pl.len().alias("n"),
                                        pl.col("agent").unique().alias("agents"))
    crews = projs.filter((pl.col("nw") >= 2) & (pl.col("n") >= 10) & pl.col("agents").list.contains(pred))
    nb = {d: int(np.ceil(D.cal.filter(pl.col("pt_date") == d)["window_s"][0] / 1800)) for d in pre2 + post2}
    rows = []
    for k, agents in zip(crews["project"].to_list(), crews["agents"].to_list()):
        a_pre = w.filter(pl.col("project") == k, pl.col("pt_date").is_in(pre2))
        a_post = w.filter(pl.col("project") == k, pl.col("pt_date").is_in(post2))
        v_pre = a_pre.height / sum(nb[d] for d in pre2)
        v_post = a_post.height / sum(nb[d] for d in post2)
        share = a_pre.filter(pl.col("agent") == pred).height / max(a_pre.height, 1)
        rel = (v_post - v_pre) / v_pre if v_pre > 0 else np.nan
        rows.append({"project": int(k), "n_members": len(agents), "rel_V_cnt": rel, "pred_share": share,
                     "excess": rel + share if np.isfinite(rel) else np.nan,
                     "successor_writes_post": int(a_post.filter(pl.col("agent") == succ).height)})
    if not rows:
        return {"ok": False, "why": "no crew contained the predecessor"}
    ex = [r["excess"] for r in rows if np.isfinite(r["excess"])]
    a_ok = bool(ex and np.mean(ex) >= 0)
    b_ok = bool(any(r["successor_writes_post"] > 0 for r in rows))
    v = "supported" if (a_ok and b_ok) else ("failed" if not (a_ok or b_ok) else "mixed")
    return {"ok": True, "crews": rows, "mean_excess": float(np.mean(ex)) if ex else None, "a": a_ok, "b": b_ok, "verdict": v}


def migration(D, K_all, cut_day, old_host="github.com", new_host="gitlab.com", unit=None):
    """C4 statistic (and its dry-run stand-in at a non-holdout pseudo-cut)."""
    proj = pl.read_parquet(R2 / "projects.parquet") if (R2 / "projects.parquet").exists() else None
    names = dict(zip(proj["project"].to_list(), proj["name"].to_list())) if proj is not None else {}
    w = D.w.filter(pl.col("strict"))
    days = sorted(w["pt_date"].unique().to_list())
    pre2 = [d for d in days if d < cut_day][-2:]
    post3 = [d for d in days if d >= cut_day][:3]
    if len(pre2) < 2 or len(post3) < 2:
        return {"ok": False, "why": "days missing"}
    wp = w.filter(pl.col("pt_date").is_in(pre2))
    host = {k: (names.get(k) or "") for k in w["project"].unique().to_list()}
    pj = wp.group_by("project").agg(pl.col("agent").unique().alias("agents"), pl.len().alias("n"))
    pj = pj.filter((pl.col("agents").list.len() >= 2) & (pl.col("n") >= 5))
    pj = pj.filter(pl.col("project").map_elements(lambda k: host.get(k, "").startswith(old_host), return_dtype=pl.Boolean))
    wpost = w.filter(pl.col("pt_date").is_in(post3))
    new = wpost.filter(pl.col("project").map_elements(lambda k: host.get(k, "").startswith(new_host), return_dtype=pl.Boolean))
    co = new.group_by("project").agg(pl.col("agent").unique().alias("agents"))
    reform, drops = [], []
    nb = {d: int(np.ceil(D.cal.filter(pl.col("pt_date") == d)["window_s"][0] / 1800)) for d in pre2 + post3}
    for agents in pj["agents"].to_list():
        s = set(agents)
        reform.append(any(len(s & set(a)) >= 2 for a in co["agents"].to_list()))
        def vadv(dd):
            x = w.filter(pl.col("agent").is_in(list(s)) & pl.col("pt_date").is_in(dd)).select("pt_date", "bin").unique()
            return x.height / sum(nb[d] for d in dd)
        drops.append(vadv(post3[:2]) - vadv(pre2))
    if not reform:
        return {"ok": False, "why": "no crews on the old host"}
    return {"ok": True, "n_crews": len(reform), "reformation_rate": float(np.mean(reform)),
            "mean_dV_adv": float(np.mean(drops)), "pre": pre2, "post": post3}


# ============================================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if not a.dry_run and not (a.confirm and a.ack):
        raise SystemExit("REFUSED: this script uses the locked holdout (#34 with NE30, #43, #45-#50 with NE24, #51 tail).\n"
                         "Run with --dry-run on non-holdout stand-ins, or with BOTH --confirm and "
                         "--i-understand-this-uses-the-locked-holdout once Vivian has signed off and the reuse is disclosed.")
    out = {"predictions": PRED, "mode": "dry-run" if a.dry_run else "CONFIRM"}
    if a.dry_run:
        D = RR.Data()                       # non-holdout only (guard asserted)
        K_all = {u["unit"]: RR.coarse_grainings(D, u, D.period(u)) for u in D.units}
        out["stand_ins"] = {"C1": "NE29: the non-holdout same-lab succession Claude 3.7 Sonnet -> Claude Sonnet 4.6 "
                                  "(#31; 3.7 retired 2026-02-19, 4.6 joined 02-18), scored with the same code",
                            "C2/C3/C5": "non-holdout units (= exploratory R6b/R6c/R4d)", "C4": "pseudo-cut 2026-05-11 (NE42 split)"}
        out["C1_standin"] = {"note": "NE29 is the only non-holdout same-lab succession; it is also exploratory R7 evidence",
                             "result": succession(D, K_all, "31", "31", "Claude 3.7 Sonnet", "Claude Sonnet 4.6", "2026-02-19")}
        out.update(c2_c5(D, K_all))
        out["C3"] = c3(D, K_all)
        out["C4_standin"] = migration(D, K_all, "2026-05-11", old_host="github.com", new_host="github.com")
        path = R2 / "confirm_dryrun.json"
    else:
        # ---- holdout build (only behind both flags) ----
        from build_r2 import build  # noqa: E402
        sys.path.insert(0, str(L.ROOT / "hypotheses/H15-semantic-information-scrambles/scheme"))
        import h15common as C15  # noqa: E402
        from build import build as build15  # noqa: E402  (H15's scheme/build.py)
        hdays = sorted(C15.holdout_days())
        cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("pt_date").is_in(hdays) & (pl.col("goal_no") >= 30))
        days = cal["pt_date"].to_list()
        cdir = R2 / "confirm"
        cal15 = cal.filter((pl.col("n_agent_events") > 0)).with_columns(
            C15.unit_expr().alias("unit"), ((pl.col("win_end") - pl.col("win_start")).dt.total_seconds() / 3600).alias("win_h"))
        build15(cal15, set(), cdir / "h15", guard=False)
        build(cdir, days, allow_holdout=True, unit_fn=confirm_unit_fn, h15_dir=cdir / "h15")
        D = RR.Data(base=cdir, allow_holdout=True)
        K_all = {u["unit"]: RR.coarse_grainings(D, u, D.period(u)) for u in D.units}
        out["C1"] = succession(D, K_all, "34a", "34b", GEMINI3, GEMINI31, NE30_DAY)
        out.update(c2_c5(D, K_all))
        out["C3"] = c3(D, K_all)
        out["C4"] = migration(D, K_all, NE24_DAY)
        path = cdir / "confirm_results.json"
    path.write_text(json.dumps(RR.clean(out), indent=1))
    print(json.dumps(RR.clean({k: v for k, v in out.items() if k not in ("C2", "C5")}), indent=1)[:3000])


if __name__ == "__main__":
    main()
