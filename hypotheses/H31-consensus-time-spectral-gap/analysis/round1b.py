"""H31 round 1b (improved data, 2026-10-04): attention vs work consensus events, #26 per election round, and the NE42
room merge A-B-A. Run after the round-1b pipeline:

  H31_DATA=data/processed/H31-consensus-time-spectral-gap/r1b uv run python .../analysis/predictors.py
  H31_DATA=... H31_EV26=dq6 uv run python .../analysis/explore.py --W 30      (and --W 15, --W 60)
  H31_DATA=... H31_STATE=work uv run python .../analysis/explore.py --W 30
  H31_DATA=... uv run python .../analysis/robustness.py
  uv run python hypotheses/H31-consensus-time-spectral-gap/analysis/round1b.py

Writes data/processed/H31-consensus-time-spectral-gap/r1b/round1b_summary.json. Predictions: card "Round 1b",
goalperiod-subhypotheses/G26 and NE42 READMEs (written before running).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
OLD = ROOT / "data/processed/H31-consensus-time-spectral-gap"
R1B = OLD / "r1b"


def classify(ep: pl.DataFrame) -> pl.DataFrame:
    c = ep.filter(pl.col("consensus"))
    return c.with_columns(pl.when(~pl.col("frozen")).then(pl.lit("gradual"))
                          .when(pl.col("t0_h") > 0.75 + 1e-6).then(pl.lit("instant")).otherwise(pl.lit("frozen")).alias("kind"))


def counts(ep: pl.DataFrame, goals=None) -> dict:
    if goals is not None:
        ep = ep.filter(pl.col("goal_no").is_in(goals))
    c = classify(ep)
    g = c.filter(pl.col("kind") == "gradual")
    return dict(projects=ep.height, consensus=c.height, frozen=int((c["kind"] == "frozen").sum()),
                instant=int((c["kind"] == "instant").sum()), gradual=g.height,
                median_tau_h=float(g["tau_h"].median()) if g.height else None,
                q10_tau_h=float(g["tau_h"].quantile(0.1)) if g.height else None,
                q90_tau_h=float(g["tau_h"].quantile(0.9)) if g.height else None,
                blocks=int(ep.select("goal_no", "room").unique().height), periods=int(ep["goal_no"].n_unique()) if ep.height else 0)


def main():
    out = {}
    epo = pl.read_parquet(OLD / "events_ep_w30.parquet")
    epn = pl.read_parquet(R1B / "events_ep_w30.parquet")
    epw = pl.read_parquet(R1B / "events_ep_w30_work.parquet") if (R1B / "events_ep_w30_work.parquet").exists() else pl.DataFrame()
    out["counts_round1"] = counts(epo)
    out["counts_r1b"] = counts(epn)
    ge30 = sorted(set(epw["goal_no"].to_list())) if epw.height else []
    both = sorted(set(ge30) & set(epn["goal_no"].to_list()))
    both = [g for g in both if g >= 30]
    out["work_periods"] = ge30
    out["attention_on_work_periods"] = counts(epn, both)
    out["work_on_work_periods"] = counts(epw, both) if epw.height else None
    per = []
    for g in sorted(set(epn.filter(pl.col("goal_no") >= 30)["goal_no"].to_list()) | set(ge30)):
        row = dict(goal=g)
        for nm, ep in (("att", epn), ("work", epw)):
            if ep.height == 0 or ep.filter(pl.col("goal_no") == g).height == 0:
                row[nm] = None
                continue
            row[nm] = counts(ep, [g])
        per.append(row)
    out["per_period_ge30"] = per
    # cross-period summaries
    for nm, f in (("w30", "cross_period_w30.json"), ("w15", "cross_period_w15.json"), ("w60", "cross_period_w60.json"),
                  ("w30_work", "cross_period_w30_work.json")):
        for tag, base in (("old", OLD), ("new", R1B)):
            p = base / f
            if p.exists():
                c = json.loads(p.read_text())
                out.setdefault("cross", {}).setdefault(nm, {})[tag] = {k: c.get(k) for k in (
                    "ep_counts", "ep_tau", "P1", "T3_lopo_rmse", "T4_kick", "T5_abrupt", "ec_counts", "E_V") if k in c}
                t1 = c.get("T1_slopes_period", {})
                out["cross"][nm][tag]["T1"] = {k: {kk: t1[k].get(kk) for kk in ("b", "lo", "hi", "p_perm", "p_holm", "n", "n_periods")}
                                               for k in t1 if isinstance(t1[k], dict)}
                t6 = c.get("T6_two_room", [])
                out["cross"][nm][tag]["T6"] = dict(n=len(t6), agrees_D=int(sum(x["agrees_D"] for x in t6)),
                                                    goals=[x["goal_no"] for x in t6], agree_list=[x["agrees_D"] for x in t6])
    # #26 per round
    ev = json.loads((R1B / "ev26.json").read_text())
    out["g26"] = {k: v for k, v in ev.items() if k != "trajectory"}
    # NE42: predictors per block in #39, #40, #41 (ledger visibility), and events by kind
    pp = pl.read_parquet(R1B / "predictors_period.parquet").filter(pl.col("variant") == "all")
    ppo = pl.read_parquet(OLD / "predictors_period.parquet").filter(pl.col("variant") == "all")
    ne = {}
    for g in (39, 40, 41):
        blocks = []
        for r in pp.filter(pl.col("goal_no") == g).iter_rows(named=True):
            o = ppo.filter((pl.col("goal_no") == g) & (pl.col("room") == r["room"]))
            blocks.append(dict(room=r["room"], N_b=r["N_b"], msg_rate=r["msg_rate"], u=r["u"], l2_sym=r["l2_sym"],
                               l2_sym_round1=o["l2_sym"][0] if o.height else None, tau_wave_min=r["tau_wave"] * 60,
                               ul2_rw=r["ul2_rw"], g_tr=r["g_tr"]))
        evs = {}
        for nm, ep in (("attention", epn), ("work", epw)):
            if ep.height == 0:
                continue
            c = classify(ep.filter(pl.col("goal_no") == g))
            evs[nm] = dict(projects=int(ep.filter(pl.col("goal_no") == g).height),
                           by_kind=dict(c.group_by("kind").len().rows()) if c.height else {},
                           gradual_tau_h=c.filter(pl.col("kind") == "gradual")["tau_h"].to_list(),
                           events=c.select("room", "label", "kind", "tau_h", "t0_h", "tc_h").to_dicts())
        ne[g] = dict(blocks=blocks, events=evs)
    l2 = {g: max([b["l2_sym"] for b in ne[g]["blocks"]] or [np.nan]) for g in ne}
    ne["l2_ratio_40_vs_39max"] = l2[40] / l2[39] if l2[39] else None
    ne["l2_ratio_40_vs_41max"] = l2[40] / l2[41] if l2[41] else None
    out["NE42"] = ne
    (R1B / "round1b_summary.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps({k: v for k, v in out.items() if k not in ("per_period_ge30",)}, indent=1, default=float)[:9000])
    for r in per:
        print(r["goal"], "att", r["att"] and {k: r["att"][k] for k in ("consensus", "frozen", "instant", "gradual", "median_tau_h")},
              "work", r["work"] and {k: r["work"][k] for k in ("consensus", "frozen", "instant", "gradual", "median_tau_h")})


def estimates():
    import sys
    sys.path.insert(0, str(ROOT / "infra/shared"))
    import estimates as E
    rows = []
    src = "data/processed/H31-consensus-time-spectral-gap/r1b/"
    for space, f in (("project", "events_ep_w30.parquet"), ("work", "events_ep_w30_work.parquet")):
        ep = pl.read_parquet(R1B / f)
        c = classify(ep)
        for g in sorted(set(ep["goal_no"].to_list())):
            cg = c.filter(pl.col("goal_no") == g)
            gr = cg.filter(pl.col("kind") == "gradual")
            base = dict(period_unit=E.map_unit(g), goal_no=g, role="replication", source=src + f, post_hoc=False,
                        status="exploratory round 1b (ledger visibility, shared labels)")
            rows.append(dict(base, statistic="consensus_events", channel=space, estimate=float(cg.height), ci_kind="none",
                             n=float(ep.filter(pl.col("goal_no") == g).height), n_kind="projects held by >= 2 agents",
                             null="none (count)", method="E-P rule: >= max(3, N/3) agents and >= 50% of labelled agents for 2 windows, W=30, carry-forward 4 (round 1b)",
                             notes=f"frozen {int((cg['kind'] == 'frozen').sum())}, instant {int((cg['kind'] == 'instant').sum())}, gradual {gr.height}"))
            if gr.height:
                rows.append(dict(base, statistic="consensus_time_gradual_median_h", channel=space, estimate=float(gr["tau_h"].median()),
                                 ci_lo=float(gr["tau_h"].min()), ci_hi=float(gr["tau_h"].max()), ci_kind="none", n=float(gr.height),
                                 n_kind="gradual events", null="M0 constant forecast",
                                 method="active hours from a project's first appearance to the E-P consensus window, gradual events (round 1b)",
                                 notes="ci_lo/ci_hi = min/max over events, not a CI"))
    pp = pl.read_parquet(R1B / "predictors_period.parquet").filter(pl.col("variant") == "all")
    for r in pp.iter_rows(named=True):
        rows.append(dict(period_unit=E.map_unit(r["goal_no"]), goal_no=r["goal_no"], role="replication", source=src + "predictors_period.parquet",
                         statistic=f"exposure_lambda2_wsym_room{r['room']}", channel="ledger", estimate=r["l2_sym"], ci_kind="none",
                         n=r["N_b"], n_kind="median roster agents in the room", null="none",
                         method="second eigenvalue of the symmetrized seen-weighted exposure Laplacian per active hour; seen = context ledger (round 1b)",
                         post_hoc=False, status="exploratory round 1b"))
    ev = json.loads((R1B / "ev26.json").read_text())
    for rnd, x in ev["rounds"].items():
        if x["tau_V_s"] is None:
            continue
        rows.append(dict(period_unit=E.map_unit(26), goal_no=26, role="native", source=src + "ev26.json", statistic=f"vote_consensus_time_s_{rnd}",
                         channel="ballots", estimate=x["tau_V_s"], ci_kind="none", n=float(x["n_ballots"]), n_kind="ballots",
                         null="M_lambda forecast (h) and read-out time tau_read(3)",
                         method="DQ6 ballots: seconds from the round's opening until one candidate holds >= 50% of >= 3 ballots (round 1b)",
                         notes=f"tau_read(3) = {x['readout']['tau_read3_s']:.1f} s", post_hoc=False, status="exploratory round 1b native"))
    E.write_estimates(rows, hypothesis="H31", replace_keys=("statistic", "channel", "method", "role"))
    print(f"estimates written: {len(rows)}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "estimates":
        estimates()
    else:
        main()
