"""H15 confirmatory test on the LOCKED HOLDOUT. Written 2026-10-03 after exploratory round 1; NOT RUN.

Refuses to touch holdout data unless BOTH flags are given:
    --confirm --i-understand-this-uses-the-locked-holdout
`--dry-run` runs the identical pipeline on non-holdout stand-ins (no holdout day is read beyond the calendar flags).

Pre-registered confirmatory criteria (fixed 2026-10-03, informed by exploration; see the card, "Confirmatory test"):
  C1  NE30 same-family succession (Gemini 3 Pro -> Gemini 3.1 Pro, 2026-03-09, regime II). The successor starts with an
      empty memory. Exploration found no newcomer deficit at the day scale (P4 failed). Prediction: the successor's
      deficit (tenure active days 1-3 vs 6-12, same-day differenced, vs. the incumbent pseudo-join null of its period)
      is not significantly negative: z > -2 on V_rel (V* for regime I/II) AND on V_eng. REFUTATION-ONLY criterion:
      with one event it can refute the round-1 reading (a significant deficit), not confirm it.
      Stand-in (dry run): GPT-5.4 joining in #35 (regime II).
  C2  NE33 batch join (Muse Spark 1.3, Gemini 3.8 Flash, GPT-6 Astra; 2026-09-03/04; reference window in the #51 tail).
      Prediction: period-mean deficit on V_eng (V* for regime III) not significantly negative, z > -2. Refutation-only.
      (Amended 2026-10-03 before any holdout use: C1/C2 first also required effect > -0.3 / >= -0.1 SD; the dry run
      showed that with 1-3 events such thresholds are noise-dominated: stand-ins gave -0.93 and -0.20 SD.)
      Stand-in: the GPT-5.6 triplet (2026-07-09, #51).
  C3  Context erasure (post-hoc exploratory finding, confirmed here): in every holdout regime III period with >= 200
      forced consolidations, writes in turns +1..+10 after a FORCED consolidation fall relative to turns -20..-11 of the
      same segment. Criterion: DerSimonian-Laird meta of the per-period relative dip <= -0.25 with 95% CI below 0, AND
      the per-period dip < 0 with CI below 0 in >= 2/3 of those periods.
      Stand-in: the non-holdout regime III periods.
  C4  Memory loss beyond normal consolidation (ML, same detection rule) in holdout periods: meta ΔV on V* (kal) is NOT
      <= -0.3 SD with z <= -2 (exploration found no day-scale cost). Reported as inconclusive if < 2 periods have events.
      Stand-in: non-holdout ML events.
  C5  Task-phase confound check: dip_CF - dip_CV (vs agent-day base) > 0 in the meta (CI above 0), as in exploration.
Overall: H15 round-1 reading ("day-scale memory is not load-bearing; the context window is") is CONFIRMED if C3 and C4
pass and neither C1 nor C2 refutes; REFUTED if C3 fails, or C4's opposite holds, or C1/C2 show a significant deficit
on V*; INCONCLUSIVE otherwise (e.g. C4 has < 2 periods). C5 is a check, not a criterion.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import h15common as C  # noqa: E402
from h15lib import (Panel, agent_mu, autocov_params, cluster_boot_diff, dl_meta, event_delta,  # noqa: E402
                    period_test, residual_panel, unit_placebo_pool)

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

V_STAR = {"I": "V_rel", "II": "V_rel", "III": "V_eng"}
HOLDOUT_UNITS_III = ["43", "45", "46", "47", "48", "49", "50", "51"]


def full_calendar() -> pl.DataFrame:
    cal = pl.read_parquet(C.SH / "calendar.parquet")
    cal = cal.filter((pl.col("goal_no") > 0) & (pl.col("n_agent_events") > 0))
    return cal.with_columns(C.unit_expr().alias("unit"),
                            ((pl.col("win_end") - pl.col("win_start")).dt.total_seconds() / 3600).alias("win_h"))


def load_tables(mode: str):
    """dry: the exploratory (non-holdout) tables. confirm: rebuild everything on the full calendar (holdout included)."""
    if mode == "dry":
        o = C.OUT
        return (pl.read_parquet(o / "agent_day.parquet"), pl.read_parquet(o / "scramble_catalog.parquet"),
                pl.read_parquet(o / "consolidations.parquet"), C.calendar_nonholdout())
    from build import build  # noqa: E402  (scheme/build.py)
    cal = full_calendar()
    out = C.OUT / "confirm"
    t = build(cal, set(), out, guard=False)
    return t["agent_day"], t["catalog"], t["consolidations"], cal


def unit_days_of(cal):
    return {u: sorted(g["pt_date"].to_list()) for (u,), g in cal.group_by(["unit"])}


def newcomer_deficits(ad, cat, cal, agents, V, rng):
    """Deficit (tenure days 1-3 minus 6-12 of u) for the given newcomer agent codes, vs incumbent pseudo-joins."""
    rp = residual_panel(ad, V)
    ud = unit_days_of(cal)
    useq = {int(a): dict(zip(g["pt_date"].to_list(), g["u"].to_list())) for (a,), g in rp.group_by(["agent"])}
    aseq = {int(a): g.sort("pt_date")["pt_date"].to_list() for (a,), g in ad.group_by(["agent"])}
    mn = cat.filter((pl.col("type") == "MN") & pl.col("agent").is_in(agents))
    newcomers = set(cat.filter(pl.col("type") == "MN")["agent"].to_list())
    vals, nulls, rows = [], [], []
    for e in mn.iter_rows(named=True):
        a = int(e["agent"])
        seq = [d for d in aseq.get(a, []) if d >= e["pt_date"]]
        xs = np.array([useq.get(a, {}).get(d, np.nan) for d in seq[:12]], float)
        if len(xs) < 12 or np.isfinite(xs[:3]).sum() < 1 or np.isfinite(xs[5:12]).sum() < 3:
            continue
        val = float(np.nanmean(xs[:3]) - np.nanmean(xs[5:12]))
        null = []
        for b, s in useq.items():
            if b in newcomers:
                continue
            bseq = aseq[b]
            pos = {d: i for i, d in enumerate(bseq)}
            for d0 in ud[e["unit"]]:
                j = pos.get(d0)
                if j is None:
                    continue
                ys = np.array([s.get(d, np.nan) for d in bseq[j:j + 12]], float)
                if len(ys) == 12 and np.isfinite(ys[:3]).sum() >= 1 and np.isfinite(ys[5:12]).sum() >= 3:
                    null.append(float(np.nanmean(ys[:3]) - np.nanmean(ys[5:12])))
        vals.append(val)
        nulls.append(null)
        rows.append({"agent": a, "pt_date": e["pt_date"], "unit": e["unit"], "deficit": val})
    return period_test(vals, nulls, rng=rng), rows


def ml_meta(ad, cat, cal, units, rng):
    """ML ΔV (kal, unit-pooled placebo null) on V* per unit, then DL meta."""
    ud = unit_days_of(cal)
    reg = {u: str(cal.filter(pl.col("unit") == u)["regime"][0]) for u in ud}
    ts = {}
    for V in sorted(set(V_STAR.values())):
        rp = residual_panel(ad, V)
        panel = Panel(rp, ud)
        ev = {}
        for e in cat.filter(pl.col("type").is_in(["ML", "MG", "MR", "CC", "MN"])).iter_rows(named=True):
            if e["pt_date"] in ud.get(e["unit"], []):
                ev.setdefault((int(e["agent"]), e["unit"]), []).append(ud[e["unit"]].index(e["pt_date"]))
        prm = {r: autocov_params(panel, [u for u in ud if reg[u] == r], exclude=ev) for r in ("I", "II", "III")}
        cache = {}
        for u in units:
            if u not in ud or V_STAR[reg[u]] != V:
                continue
            vals, nulls = [], []
            for e in cat.filter((pl.col("type") == "ML") & (pl.col("unit") == u)).iter_rows(named=True):
                x = panel.get(int(e["agent"]), u)
                if x is None:
                    continue
                i0 = ud[u].index(e["pt_date"])
                evs = ev.get((int(e["agent"]), u), [])
                r = event_delta(x, i0, [1, 2], agent_mu(x, evs), prm[reg[u]])
                if r is None:
                    continue
                pool = unit_placebo_pool(panel, u, ev, [1, 2], prm[reg[u]], cache)
                vals.append(r["kal"])
                nulls.append([p["kal"] for p in pool])
            t = period_test(vals, nulls, rng=rng)
            if t:
                ts[u] = t
    m = dl_meta([t["effect"] for t in ts.values()], [t["null_sd"] for t in ts.values()])
    return m, ts


def ctx_tests(ad, ce, units, rng):
    base = ad.select("agent", "pt_date", (pl.col("n_writes") / pl.col("n_turns")).alias("w_base"))
    c = (ce.join(base, on=["agent", "pt_date"], how="left").filter(pl.col("kind").is_in(["CF", "CV"]))
         .with_columns((pl.col("agent").cast(pl.Utf8) + "_" + pl.col("pt_date")).alias("cl")))
    rd, diff = {}, {}
    for u in units:
        g = c.filter(pl.col("unit") == u)
        cf = g.filter((pl.col("kind") == "CF") & (pl.col("n_far") >= 10) & (pl.col("n_post") >= 10))
        if cf.height >= 200:
            cl = cf["cl"].to_numpy()
            uu, inv = np.unique(cl, return_inverse=True)
            sp = np.bincount(inv, weights=cf["w_post"].to_numpy())
            sf = np.bincount(inv, weights=cf["w_far"].to_numpy())
            est = sp.sum() / max(sf.sum(), 1e-12) - 1
            bs = [sp[ii].sum() / max(sf[ii].sum(), 1e-12) - 1 for ii in
                  (rng.integers(0, len(uu), len(uu)) for _ in range(500))]
            rd[u] = {"rel_dip": float(est), "lo": float(np.percentile(bs, 2.5)), "hi": float(np.percentile(bs, 97.5)),
                     "se": float(np.std(bs, ddof=1)), "n": cf.height}
        gb = g.filter(pl.col("w_base").is_not_null())
        a, b = gb.filter(pl.col("kind") == "CF"), gb.filter(pl.col("kind") == "CV")
        if a.height >= 20 and b.height >= 20:
            diff[u] = cluster_boot_diff((a["w_post"] - a["w_base"]).to_numpy(), a["cl"].to_numpy(),
                                        (b["w_post"] - b["w_base"]).to_numpy(), b["cl"].to_numpy(), 500, rng)
    m_rd = dl_meta([v["rel_dip"] for v in rd.values()], [v["se"] for v in rd.values()])
    m_diff = dl_meta([v["est"] for v in diff.values() if v], [v["se"] for v in diff.values() if v])
    return m_rd, rd, m_diff, diff


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.dry_run and (a.confirm or a.ack):
        raise SystemExit("choose either --dry-run or the two confirmation flags, not both")
    if not a.dry_run and not (a.confirm and a.ack):
        raise SystemExit("REFUSED: this script uses the locked holdout (NE30, NE33 tail, #43, #45-#50, #51 tail).\n"
                         "Run with --dry-run on non-holdout stand-ins, or with BOTH --confirm and "
                         "--i-understand-this-uses-the-locked-holdout once Vivian has signed off.")
    mode = "dry" if a.dry_run else "confirm"
    rng = np.random.default_rng(C.SEED)
    ad, cat, ce, cal = load_tables(mode)
    roster = pl.read_parquet(C.SH / "roster.parquet")
    code = {n: int(c) for c, n in roster.select("agent", "name").rows()}
    if mode == "dry":
        c1_agents = [code["GPT-5.4"]]
        c2_agents = [code["GPT-5.6 Sol"], code["GPT-5.6 Terra"], code["GPT-5.6 Luna"]]
        u3 = ["36b", "37", "38", "39", "40", "41", "42", "44", "51"]
        u4 = sorted(set(cat.filter(pl.col("type") == "ML")["unit"].to_list()))
    else:
        c1_agents = [code["Gemini 3.1 Pro"]]
        c2_agents = [code["Muse Spark 1.3"], code["Gemini 3.8 Flash"], code["GPT-6 Astra"]]
        u3 = HOLDOUT_UNITS_III
        hdays = C.holdout_days()
        # #51 mixes explored days and the held-out tail: confirmatory events and consolidations on holdout days only
        ce = ce.filter(pl.col("pt_date").is_in(list(hdays)))
        cat = cat.filter((pl.col("type") != "ML") | pl.col("pt_date").is_in(list(hdays)))
        u4 = sorted(set(cat.filter(pl.col("type") == "ML")["unit"].to_list()))
    out = {"mode": mode, "criteria": {}}
    c1 = {V: newcomer_deficits(ad, cat, cal, c1_agents, V, rng) for V in ("V_rel", "V_eng")}
    out["C1"] = {V: {"test": t, "rows": r} for V, (t, r) in c1.items()}
    out["criteria"]["C1"] = (None if any(t is None for t, _ in c1.values()) else all(t["z"] > -2 for t, _ in c1.values()))
    t2, r2 = newcomer_deficits(ad, cat, cal, c2_agents, "V_eng", rng)
    out["C2"] = {"test": t2, "rows": r2}
    out["criteria"]["C2"] = None if t2 is None else bool(t2["z"] > -2)
    m_rd, rd, m_diff, diff = ctx_tests(ad, ce, u3, rng)
    out["C3"] = {"meta": m_rd, "units": rd}
    frac = np.mean([v["hi"] < 0 for v in rd.values()]) if rd else 0.0
    out["criteria"]["C3"] = bool(m_rd and m_rd["mu"] <= -0.25 and m_rd["hi"] < 0 and frac >= 2 / 3)
    m4, t4 = ml_meta(ad, cat, cal, u4, rng)
    out["C4"] = {"meta": m4, "units": t4}
    out["criteria"]["C4"] = (None if (m4 is None or m4["k"] < 2) else not (m4["mu"] <= -0.3 and m4["z"] <= -2))
    out["C5_check"] = {"meta": m_diff, "units": diff, "holds": bool(m_diff and m_diff["lo"] > 0)}
    cr = out["criteria"]
    if cr["C3"] is False or cr["C4"] is False or cr["C1"] is False or cr["C2"] is False:
        overall = "REFUTED"
    elif cr["C3"] is True and cr["C4"] is True:
        overall = "CONFIRMED"
    else:
        overall = "INCONCLUSIVE"
    out["overall"] = overall
    dest = C.OUT / ("confirm_dryrun.json" if mode == "dry" else "confirm/confirm_result.json")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=1, default=lambda o: None if o != o else float(o)))
    print(json.dumps({"mode": mode, "criteria": cr, "overall": overall,
                      "C1": {V: (round(t["effect"], 3), round(t["z"], 2)) if t else None for V, (t, _) in c1.items()},
                      "C2": (round(t2["effect"], 3), round(t2["z"], 2)) if t2 else None,
                      "C3": (round(m_rd["mu"], 3), round(m_rd["lo"], 3), round(m_rd["hi"], 3), m_rd["k"]) if m_rd else None,
                      "C4": (round(m4["mu"], 3), round(m4["z"], 2), m4["k"]) if m4 else None,
                      "C5": (round(m_diff["mu"], 4), round(m_diff["lo"], 4)) if m_diff else None}, indent=1))
    print("wrote", dest)


if __name__ == "__main__":
    main()
