"""H43 round 2 per-period estimates -> shared per_period_estimates (infra/shared/estimates.py: write_estimates)."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import estimates as E  # noqa: E402

D = ROOT / "data/processed/H43-kick-refractory-window/r2"
SRC = "data/processed/H43-kick-refractory-window/r2"
NOTE = "round 2 (2026-10-05)"
WAKE = "after-PAUSE timer wakes (shared idle_gates); sustained escape (wake call + next two active)"


def ok(x):
    return x if (x is not None and isinstance(x, (int, float)) and math.isfinite(x)) else None


def unit(g, d0, d1):
    return E.map_unit(g, d0, d1) or f"local:{g}_{d0[5:]}_{d1[5:]}"


def row(base, stat, s, **kw):
    return base | dict(statistic=stat, estimate=ok(s["est"]), se=ok(s.get("se")), ci_lo=ok(s["ci"][0]), ci_hi=ok(s["ci"][1])) | kw


def days_of(goal, d0=None, d1=None):
    cal = pl.read_parquet(ROOT / "data/processed/shared/calendar.parquet").filter((pl.col("goal_no") == goal) & ~pl.col("holdout"))
    if d0:
        cal = cal.filter(pl.col("pt_date") >= d0)
    if d1:
        cal = cal.filter(pl.col("pt_date") < d1)
    ds = sorted(cal["pt_date"].to_list())
    return ds[0], ds[-1]


def main():
    rows = []
    # ------------------------------------------------------------- R2 (G51 before 08-21; native: the nudger exists only here)
    r2 = json.loads((D / "results_r2.json").read_text())
    d0, d1 = days_of(51, None, "2026-08-21")
    base = dict(period_unit=unit(51, d0, d1), goal_no=51, first_day=d0, last_day=d1, source=f"{SRC}/results_r2.json", ci_level=0.95,
                ci_kind="percentile", notes=NOTE, role="native", n_kind="nudged wakes")
    n_ref = r2["counts"]["refire_same"] + r2["counts"]["refire_new"]
    for m, ch, meth in (("proxy", WAKE, "agent-FE logit; prior-nudge state; nudge x (ln k, ln trap age, recent run); ln k, trap age, pause, hour, activity, reads"),
                        ("base", WAKE, "agent-FE logit; prior-nudge state; ln k, trap age, pause, hour, activity, reads (no proxy interactions)"),
                        ("proxy_agentday", WAKE, "agent-day-FE logit, proxy model"),
                        ("glance_proxy", "after-PAUSE timer wakes; glance (the wake call is active)", "agent-FE logit, proxy model")):
        s = r2["models"][m]["stats"]
        rows.append(row(base, "nudge_refire_minus_first_lnOR", s["dF"], channel=f"{ch}; model {m}", n=n_ref, method=meth + "; day-bootstrap CI",
                        null="0 (no facilitation)"))
        if m in ("proxy", "base"):
            rows.append(row(base, "nudge_first_wake_lnOR", s["g_first"], channel=f"{ch}; model {m}", n=r2["counts"]["first"], method=meth,
                            null="0"))
            rows.append(row(base, "nudge_refire_wake_lnOR", s["g_refire"], channel=f"{ch}; model {m}", n=n_ref, method=meth, null="0"))
    s = r2["models"]["proxy_split"]["stats"]
    rows.append(row(base, "nudge_refire_minus_first_lnOR", s["d_same"], channel=f"{WAKE}; re-fire inside the same trap", n=r2["counts"]["refire_same"],
                    method="agent-FE logit, proxy model, re-fire classes split", null="0"))
    rows.append(row(base, "nudge_refire_minus_first_lnOR", s["d_new"], channel=f"{WAKE}; re-fire after a sustained run (new trap)", n=r2["counts"]["refire_new"],
                    method="agent-FE logit, proxy model, re-fire classes split", null="0"))
    # ------------------------------------------------------------- R3 (replication: receiving calls, talk at the call)
    r3 = json.loads((D / "results_r3.json").read_text())
    for p, v in r3["periods"].items():
        if "stats" not in v:
            continue
        g = int(p[1:])
        a, b = days_of(g)
        bs = dict(period_unit=unit(g, a, b), goal_no=g, first_day=a, last_day=b, source=f"{SRC}/results_r3.json", ci_level=0.95,
                  ci_kind="percentile", notes=NOTE, role="replication", n_kind="receiving calls")
        ch = "active-at-read receiving calls; the call talks; dose = directed items newly read (ledger)"
        meth = "agent-FE logit with dose indicators, ln window, undirected counts, previous talk, day third, unit; day-bootstrap CI"
        st = v["stats"]
        rows.append(row(bs, "dose1_talk_lnOR", st["f1"], channel=ch, n=v["dose_counts"]["1"], method=meth, null="0"))
        rows.append(row(bs, "second_kick_same_read_marginal_lnOR", st["m2"], channel=ch, n=v["dose_counts"]["2"], method=meth, null="0 (batched kick adds nothing)"))
        if ok(st["rho2"]["est"]) is not None and ok(st["rho2"]["ci"][0]) is not None:
            rows.append(row(bs, "batching_ratio_rho2", st["rho2"], channel=ch, n=v["dose_counts"]["2"], method=meth + "; rho2 = (f2 - f1)/f1",
                            null="1 (additive kicks)"))
        if p == "G51":
            for k, lab in (("S2_gemini_logged", "Gemini calls with logged starts"), ("S2b_not_logged", "calls with calibrated starts"),
                           ("S3_no_uncertain", "no uncertain item in this or the previous call"), ("S4_lo", "doses recounted at t_call_lo"),
                           ("S4_hi", "doses recounted at t_call_hi")):
                sv = r3["g51_sens"].get(k)
                if sv and "stats" in sv and ok(sv["stats"]["rho2"]["est"]) is not None:
                    rows.append(row(bs, "batching_ratio_rho2", sv["stats"]["rho2"], channel=f"{ch}; {lab}", n=sv["dose_counts"]["2"], method=meth,
                                    null="1 (additive kicks)"))
    for p, v in r3.get("timer_wake", {}).items():
        g = int(p[1:])
        a, b = days_of(g)
        bs = dict(period_unit=unit(g, a, b), goal_no=g, first_day=a, last_day=b, source=f"{SRC}/results_r3.json", ci_level=0.95,
                  ci_kind="percentile", notes=NOTE, role="replication", n_kind="wakes")
        st = v["stats"]
        rows.append(row(bs, "second_kick_same_read_marginal_lnOR", st["m2"], channel=f"{WAKE}; dose of directed items read at the wake", n=v["dose_counts"]["2"],
                        method="agent-FE logit, dose indicators + wake nuisance", null="0"))
        if ok(st["rho2"]["est"]) is not None and ok(st["rho2"]["ci"][0]) is not None:
            rows.append(row(bs, "batching_ratio_rho2", st["rho2"], channel=f"{WAKE}; dose of directed items read at the wake", n=v["dose_counts"]["2"],
                            method="agent-FE logit, dose indicators + wake nuisance", null="1"))
    # ------------------------------------------------------------- R5 (replication: regime-III periods)
    r5 = json.loads((D / "results_r5.json").read_text())
    for p, v in r5["strict"]["periods"].items():
        if not v.get("fit"):
            continue
        g = int(p[1:])
        a, b = days_of(g)
        key = "stats" if p == "G51" else "stats_pen"
        st = v[key]
        bs = dict(period_unit=unit(g, a, b), goal_no=g, first_day=a, last_day=b, source=f"{SRC}/results_r5.json", ci_level=0.95,
                  ci_kind="percentile", notes=NOTE + ("" if key == "stats" else "; N(0, 2.5^2) prior on directed terms (post hoc, separation)"),
                  role="replication", post_hoc=(key != "stats"))
        meth = "agent-FE logit; class dummies; directed read x {fresh, re-kicked, other}; ln k, trap age, pause, hour, activity, reads; day-bootstrap CI"
        ch = f"{WAKE}; re-kicked = isolated effective directed primer within 120 min, run ended (A2-1)"
        rows.append(row(bs, "directed_wake_lnOR_fresh", st["b_fresh"], channel=ch, n=v["n_D_fresh"], n_kind="directed fresh wakes", method=meth, null="0"))
        rows.append(row(bs, "directed_wake_lnOR_rekicked", st["b_re"], channel=ch, n=v["n_D_rekick"], n_kind="directed re-kicked wakes", method=meth, null="0"))
        rows.append(row(bs, "rekick_minus_fresh_lnOR", st["d"], channel=ch, n=v["n_D_rekick"], n_kind="directed re-kicked wakes", method=meth,
                        null="0 (no refractoriness at the wake)"))
        if ok(st["R"]["est"]) is not None and ok(st["R"]["ci"][0]) is not None:
            rows.append(row(bs, "refractory_ratio_wake", st["R"], channel=ch, n=v["n_D_rekick"], n_kind="directed re-kicked wakes", method=meth + "; R = b_re/b_fresh",
                            null="1"))
    # ------------------------------------------------------------- R6 (native: NE43 inside #51)
    r6 = json.loads((D / "results_r6.json").read_text())
    a, b = "2026-08-06", "2026-09-04"
    bs = dict(period_unit=f"local:51_{a[5:]}_{b[5:]}", goal_no=51, first_day=a, last_day=b, source=f"{SRC}/results_r6.json", ci_level=0.95,
              ci_kind="percentile", notes=NOTE + "; before 08-06..08-20 vs after 08-21..09-04", role="native", n_kind="days")
    ch = "sustained escapes per idle agent-minute (round-1 statistic), NE43 before/after"
    mech = r6["mechanical"]
    for k, stat in (("dlnR", "ne43_dlnR_escape_per_idle_min"), ("dlnp", "ne43_dlnR_part_per_read_escape"), ("dlnGM", "ne43_dlnR_part_read_cadence")):
        rows.append(row(bs, stat, mech[k], channel=ch, n=22, method="E = G p identity; day bootstrap within window", null="0"))
    ss = r6["shift_share"]
    for k, stat in (("within", "ne43_dR_within_incumbents"), ("reweight", "ne43_dR_reweighting_incumbents"), ("newcomers_leavers", "ne43_dR_newcomers_leavers")):
        rows.append(row(bs, stat, ss[k], channel=ch + "; per idle minute", n=22, method="shift-share on agent rates, weights = idle minutes", null="0"))
    oa = r6["oaxaca_all"]
    for k in ("nudger", "room", "day_edge", "step"):
        rows.append(row(bs, f"ne43_wake_escape_part_{k}", oa[k], channel=f"{WAKE}; change in mean escape probability", n=oa["n_wakes"], n_kind="wakes",
                        method="agent-FE logit over both windows; linearized covariate contributions; post step", null="0"))
    for k, v in r6["segments_wake_logit"].items():
        rows.append(row(bs, "ne43_segment_step_logit", v, channel=f"{WAKE}; segment {k} vs before window", n=oa["n_wakes"], n_kind="wakes",
                        method="agent-FE logit with segment dummies", null="0 (placebo band of the single step reported in card)"))
    out = E.write_estimates(rows, hypothesis="H43")
    print(f"wrote {out.height} rows")


if __name__ == "__main__":
    main()
