"""H39 confirmatory test on the LOCKED HOLDOUT. Written 2026-10-04 after exploratory round 1; NOT RUN.

Refuses to touch held-out days unless called with BOTH flags:
    --confirm --i-understand-this-uses-the-locked-holdout
`--dry-run` runs the identical code on non-holdout stand-ins and writes confirm_dryrun/ (not evidence).

Holdout reuse (hypotheses/holdout.md): #45 (H02 activity timing, H23 content), NE21+NE23 / #46-#50 (H04 activity n),
#51 tail (planned by others) have been or will be used by other hypotheses. H39's observables are different
statistics (stationary decomposition of behavior-state transition matrices in matched kick windows; O6 content drift
toward the kick message; step decomposition of kickoffs) and nobody has computed them there. Before a real run the
card and this script must be committed, and the reuse disclosed in the card and LOG.md.

Pre-registered confirmatory predictions (C-*; the estimators, windows, matching and class rules are frozen as in
round 1, including Amendments A1 and A2):

| ID   | Target                     | Statement                                                                       | Primary |
| C1   | #45-#47, #49, #50 pooled   | nudges: pooled K > 0, 95% CI excluding 0 (escape at fixed occupancy rises)      | yes |
| C2   | #45-#47, #49, #50 pooled   | nudges: pooled idle escape ln ratio > 0 and Delta pi_idle < 0 (CIs excl. 0)     | no  |
| C3   | #51 tail                   | @-mentions: no behavior lever: |K| < 0.10 and phi_exc < 0.10                     | yes |
| C4   | #51 tail                   | @-mentions and human messages: content drift toward the message > 0 (p < 0.05)  | yes |
| C5   | #51 tail                   | human messages: no behavior lever: |K| < 0.10 and phi_exc < 0.10                | no  |
| C6   | #45-#47, #49, #50 pooled   | forced erasure (A2 chain): Delta pi_idle < 0 and Delta pi_work > 0 (pooled CIs)  | yes |
| C7   | kickoffs #44->#45 ... #49->#50 (regime III, held out) | content C6 phi above the frozen regime-III placebo p95 in >= 50%  | no  |
| C8   | NE23 (06-13 off vs 06-12 on, #best panel) | Delta pi_idle (off - on) > 0; not required significant           | no  |

Overall: supported if C1 and at least two of C3/C4/C6 pass; failed if C1 fails and at most one of C3/C4/C6 passes;
otherwise mixed. (Amended 2026-10-04 before any run: the automated speaker is silent from 2026-08-21 on non-holdout
days, so the #51 tail very likely has no nudges; nudge predictions moved to the 4-h regime-III held-out periods, where
power for the field part is low, so C2 is secondary. Nudges in the #51 tail, if any, are reported descriptively.)

Usage:
  uv run python hypotheses/H39-catalysts-vs-fields/analysis/confirm.py --dry-run
  uv run python hypotheses/H39-catalysts-vs-fields/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2" if _v == "POLARS_MAX_THREADS" else "1"

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h39lib as L  # noqa: E402
import run_period as RP  # noqa: E402
import run_steps as RS  # noqa: E402

ROOT = L.ROOT
SH = ROOT / "data/processed/shared"
sys.path.insert(0, str(ROOT / "hypotheses/H14-behavior-entropy-production/scheme"))
sys.path.insert(0, str(ROOT / "hypotheses/H39-catalysts-vs-fields/scheme"))
import build_states as H14  # noqa: E402
import build as SCHEME  # noqa: E402

HOLD = json.loads((ROOT / "hypotheses/holdout.json").read_text())

TARGETS = {
    "tail51": dict(goal=51, date_from="2026-09-07", date_to="2026-09-21"),
    "erasure": dict(goals=[45, 46, 47, 49, 50]),
    "kickoffs": [(44, 45), (45, 46), (46, 47), (47, 48), (48, 49), (49, 50)],
    "ne23": dict(off=["2026-06-13"], on=["2026-06-12"]),
}
STANDINS = {   # non-holdout stand-ins with the same structure (dry run only)
    "tail51": dict(goal=51, date_from="2026-08-24", date_to="2026-09-05"),
    "erasure": dict(goals=[38, 41, 42, 44]),
    "kickoffs": [(37, 38), (38, 39), (41, 42)],
    "ne23": dict(off=["2026-04-17"], on=["2026-04-16"]),
}


def days_for(cal, goal=None, goals=None, date_from=None, date_to=None, allow_holdout=False):
    c = cal.filter(pl.col("window_s") > 0)
    if goal is not None:
        c = c.filter(pl.col("goal_no") == goal)
    if goals is not None:
        c = c.filter(pl.col("goal_no").is_in(goals))
    if date_from:
        c = c.filter(pl.col("pt_date") >= date_from)
    if date_to:
        c = c.filter(pl.col("pt_date") < date_to)
    days = sorted(c["pt_date"].to_list())
    if not allow_holdout:
        assert not c["holdout"].any(), "dry run touched a holdout day"
    return days


def consolidation_kinds(days: list[str], allow_holdout: bool = False) -> pl.DataFrame:
    """CF/CV classification as H15: computer-use turns since the agent's previous CONSOLIDATE (41-42 = CF forced,
    10-38 = CV voluntary). Computed over all regime-III days so segments can start on earlier days."""
    cal = pl.read_parquet(SH / "calendar.parquet")
    c3 = cal.filter(pl.col("regime") == "III")
    if not allow_holdout:
        c3 = c3.filter(~pl.col("holdout"))
    r3 = c3["pt_date"].to_list()
    act = (pl.read_parquet(SH / "actions.parquet", columns=["t", "agent"]).filter(pl.col("agent").is_not_null())
           .with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8).alias("pt_date"))
           .filter(pl.col("pt_date").is_in(r3)).select("agent", "t", "pt_date", pl.lit(0, pl.Int8).alias("isc")))
    ev = (pl.read_parquet(SH / "events_core.parquet", columns=["t", "pt_date", "actor_kind", "agent", "action_type"])
          .filter((pl.col("action_type") == "CONSOLIDATE") & (pl.col("actor_kind") == "agent") & pl.col("pt_date").is_in(r3))
          .select("agent", "t", "pt_date", pl.lit(1, pl.Int8).alias("isc")))
    seq = pl.concat([act, ev]).sort("agent", "t", "isc").with_columns(pl.col("isc").cum_sum().over("agent").alias("seg"))
    seglen = seq.filter(pl.col("isc") == 0).group_by("agent", "seg").agg(pl.len().alias("seg_len_pre"))
    ce = (seq.filter(pl.col("isc") == 1).with_columns((pl.col("seg") - 1).alias("prev"))
          .join(seglen.rename({"seg": "prev"}), on=["agent", "prev"], how="left")
          .with_columns(pl.col("seg_len_pre").fill_null(0)))
    ce = ce.with_columns(pl.when(pl.col("seg_len_pre").is_between(41, 42)).then(pl.lit("CF"))
                         .when(pl.col("seg_len_pre").is_between(10, 38)).then(pl.lit("CV")).otherwise(pl.lit("other")).alias("kind"))
    return ce.filter(pl.col("pt_date").is_in(days)).select("agent", "t", "pt_date", "kind", "seg_len_pre")


def in_memory_tables(days: list[str], allow_holdout: bool):
    _, states = H14.build(days, {})
    kicks = SCHEME.load_kick_table(days, allow_holdout=allow_holdout)
    er = consolidation_kinds(days, allow_holdout)
    return states, kicks, er


def point_unit(days, cal, allow_holdout, classes, erasure=False, B=300, P=200):
    states, kicks, er = in_memory_tables(days, allow_holdout)
    seg = RP.load_period(days, cal, states=states, kicks=kicks, erasures=er if erasure else None)
    out = {"n_agent_days": len(seg["b6"]), "days": days}
    U4 = RP.make_units(seg)
    for c in classes:
        out[c] = L.run_point(U4, c, B=B, P=P, seed=L.SEED + 4040)
    if erasure:
        Ue = RP.make_units(seg, erasure=True)
        pool = L.control_pool(Ue, L.W_DEFAULT, quiet=10)
        g, s0, ab = RP.erasure_episodes(Ue, "CF", L.W_DEFAULT, 10, 3)
        out["CF_b4_nocons"] = L.run_point(Ue, "CF", B=B, P=P, seed=L.SEED + 4041, g_override=g, s0_override=s0,
                                          age_override=ab, pool_mask=pool, quiet=10, keep_states=[0, 1, 2])
    return out, seg, U4


def ci_excl0(c, sign):
    return (c[0] > 0) if sign > 0 else (c[1] < 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.dry_run and (a.confirm or a.ack):
        sys.exit("Choose exactly one: --dry-run, or --confirm --i-understand-this-uses-the-locked-holdout.")
    if not a.dry_run and not (a.confirm and a.ack):
        sys.exit("Refusing: a real (holdout) run needs BOTH --confirm and --i-understand-this-uses-the-locked-holdout. "
                 "Use --dry-run for the non-holdout stand-ins.")
    real = not a.dry_run
    T = TARGETS if real else STANDINS
    outdir = L.OUT / ("confirm" if real else "confirm_dryrun")
    t0 = time.time()
    cal = pl.read_parquet(SH / "calendar.parquet")
    res = {"mode": "CONFIRMATORY (holdout)" if real else "dry run on non-holdout stand-ins (not evidence)", "targets": {}}
    # ---- #51 tail: nudges, mentions, human messages, content drift
    d51 = days_for(cal, goal=T["tail51"]["goal"], date_from=T["tail51"]["date_from"], date_to=T["tail51"]["date_to"], allow_holdout=real)
    u51, seg51, U51 = point_unit(d51, cal, real, ("N_tgt", "A_men", "H_any"))   # N_tgt descriptive only
    u51["content"] = RP.content_drift(seg51, d51, cal, "III", ("A_men", "H_any"), U51, L.W_DEFAULT, np.random.default_rng(L.SEED), B=300, P=100)
    res["targets"]["tail51"] = u51
    C = {}
    m = u51["A_men"]
    C["C3"] = bool("K" in m and abs(m["K"]) < 0.10 and m["phi_exc"] < 0.10)
    cd = u51["content"]
    C["C4"] = bool(all(isinstance(cd.get(c), dict) and cd[c].get("field_c", -1) > 0 and cd[c].get("p_field_c", 1) < 0.05 for c in ("A_men", "H_any")))
    h = u51["H_any"]
    C["C5"] = bool("K" in h and abs(h["K"]) < 0.10 and h["phi_exc"] < 0.10)
    # ---- erasure pooled over 4-h regime-III periods
    units, nud = [], []
    for g in T["erasure"]["goals"]:
        dg = days_for(cal, goal=g, allow_holdout=real)
        if not dg:
            continue
        ue, _, _ = point_unit(dg, cal, real, ("N_tgt",), erasure=True, B=300, P=100)
        units.append(ue["CF_b4_nocons"])
        nud.append(ue["N_tgt"])
        res["targets"].setdefault("erasure", {})[f"G{g:02d}"] = ue["CF_b4_nocons"]
        res["targets"].setdefault("nudges", {})[f"G{g:02d}"] = ue["N_tgt"]
    nu = [u for u in nud if u.get("n_ep", 0) >= 10 and "K_boot_se" in u]
    if nu:
        mk = L.dl_meta([u["K"] for u in nu], [u["K_boot_se"] for u in nu])
        me = L.dl_meta([u["esc"][2] for u in nu], [u["esc_boot_se"][2] for u in nu])
        md = L.dl_meta([u["dpi"][2] for u in nu], [u["dpi_boot_se"][2] for u in nu])
        res["targets"]["nudges_pooled"] = dict(K=mk, esc_idle=me, dpi_idle=md, n_ep=int(sum(u["n_ep"] for u in nu)))
        C["C1"] = bool(mk["ci"][0] > 0)
        C["C2"] = bool(me["ci"][0] > 0 and md["ci"][1] < 0)
    else:
        C["C1"] = C["C2"] = False
    pw = [u for u in units if u.get("status") == "ok"]
    if pw:
        mi = L.dl_meta([u["dpi"][2] for u in pw], [u["dpi_boot_se"][2] for u in pw])
        mw = L.dl_meta([u["dpi"][0] for u in pw], [u["dpi_boot_se"][0] for u in pw])
        res["targets"]["erasure_pooled"] = dict(idle=mi, work=mw)
        C["C6"] = bool(mi["ci"][1] < 0 and mw["ci"][0] > 0)
    else:
        C["C6"] = False
    # ---- kickoffs: content field vs the frozen round-1 regime-III placebo pool
    frozen = json.loads((L.OUT / "steps" / "steps_results.json").read_text())["placebo"]["2x2"]
    pool = [p for p in frozen if p["era"] == "III-4h" and "c6" in p and "phi" in p["c6"]]
    kres = []
    for g0, g1 in T["kickoffs"]:
        pre = days_for(cal, goal=g0, allow_holdout=real)[-2:]
        post = days_for(cal, goal=g1, allow_holdout=real)[:2]
        if not pre or not post:
            continue
        D = HoldoutData(pre + post, real)
        r = RS.compare(D, pre, post, 300)
        if "c6" in r:
            r["judge_c6"] = L.judge_step(r["c6"], [p["c6"] for p in pool])
        kres.append(dict(id=f"K{g0:02d}-{g1:02d}", pre=pre, post=post, b4=r.get("b4"), c6=r.get("c6"), judge_c6=r.get("judge_c6")))
    res["targets"]["kickoffs"] = kres
    jk = [k["judge_c6"] for k in kres if k.get("judge_c6") and "phi_p95" in k["judge_c6"]]
    C["C7"] = bool(jk and np.mean([j["phi_pct"] >= 95 for j in jk]) >= 0.5)
    # ---- NE23 step (descriptive)
    off, on = T["ne23"]["off"], T["ne23"]["on"]
    D = HoldoutData(on + off, real)
    r = RS.compare(D, on, off, 300, content=False)
    res["targets"]["ne23"] = r
    C["C8"] = bool(r.get("b4") and r["b4"]["dpi"][2] > 0)
    sec = sum(C[k] for k in ("C3", "C4", "C6"))
    overall = "supported" if C["C1"] and sec >= 2 else ("failed" if (not C["C1"] and sec <= 1) else "mixed")
    if not real:   # check the CF/CV classifier against H15's table on the stand-in days
        mine = consolidation_kinds(sorted(set(d51)), False)
        h15 = pl.read_parquet(L.OUT / "erasures.parquet").filter(pl.col("pt_date").is_in(d51))
        j = mine.join(h15.select("agent", "t", pl.col("kind").alias("k15")), on=["agent", "t"], how="inner")
        res["cfcv_check"] = dict(n_mine=mine.height, n_h15=h15.height, n_joined=j.height,
                                 agreement=float((j["kind"] == j["k15"]).mean()) if j.height else None)
    res["predictions"] = C
    res["overall"] = overall
    res["runtime_s"] = time.time() - t0
    L.jdump(res, outdir / "confirm_results.json")
    print(json.dumps({"mode": res["mode"], "predictions": C, "overall": overall}, indent=1))


class HoldoutData(RS.Data):
    """RS.Data restricted to explicit days; holdout days allowed only in a real confirmatory run."""

    def __init__(self, days: list[str], allow_holdout: bool):
        cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("pt_date").is_in(days) & (pl.col("window_s") > 0))
        if not allow_holdout:
            assert not cal["holdout"].any(), "dry run touched a holdout day"
        self.cal = cal.sort("pt_date")
        self.meta = {r["pt_date"]: r for r in self.cal.iter_rows(named=True)}
        _, st = H14.build(days, {})
        self.seqs = {}
        for (d, ag), g in st.filter(pl.col("present")).sort("pt_date", "agent", "minute").group_by(["pt_date", "agent"], maintain_order=True):
            nrec = g["n_rec"].to_numpy()
            occ = np.flatnonzero(nrec > 0)
            if len(occ) >= 2:
                self.seqs.setdefault(d, {})[int(ag)] = g["coarse_min"].to_numpy()[occ[0]:occ[-1] + 1].astype(np.int8)
        idx = pl.read_parquet(SH / "embeddings/agent_win30.parquet").with_row_index("row").filter(pl.col("pt_date").is_in(days))
        self.win = {}
        for (d, ag), g in idx.group_by(["pt_date", "agent"]):
            self.win.setdefault(d, {})[int(ag)] = (g["win30"].to_numpy(), g["row"].to_numpy())
        self.V = np.load(SH / "embeddings/agent_win30_vec.npy", mmap_mode="r")
        self.wh = {r: RS.load_whitener(r, 32) for r in ("I", "II", "III")}


if __name__ == "__main__":
    main()
