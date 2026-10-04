"""H27 round 1b (improved data, 2026-10-04): replication on the shared deterministic labels, the work-space version,
and the native tests (#31 wave in work; #40 hub at the minute clock). Predictions were written in the card
("Round 1b") and the period READMEs before this was run.

  uv run python hypotheses/H27-herding-early-warning/analysis/round1b.py replicate   # explore + assemble, attention
  uv run python hypotheses/H27-herding-early-warning/analysis/round1b.py work        # explore + assemble, work ledger
  uv run python hypotheses/H27-herding-early-warning/analysis/round1b.py compare     # onset lags, #31 and #40 natives

Inputs: data/processed/H27-herding-early-warning/r1b/ (scheme/build.py --labels shared). Each mode runs in its own
process because explore.py reads H27_DATA / H27_STATE at import. Outputs go to the same folder (suffix _work for the
work space) plus compare_r1b.json. No text is read.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
R1B = ROOT / "data/processed/H27-herding-early-warning/r1b"
MODE = sys.argv[1] if len(sys.argv) > 1 else "compare"
os.environ["H27_DATA"] = str(R1B)
os.environ["H27_STATE"] = "work" if MODE == "work" else "project"

import json  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ews_core as E  # noqa: E402
import explore as X  # noqa: E402

SH = ROOT / "data/processed/shared"
H11R = ROOT / "data/processed/H11-potts-labor-vs-herding/r1b"


def jdump(obj, f):
    f.write_text(json.dumps(obj, indent=1, default=lambda o: None if (isinstance(o, float) and not np.isfinite(o))
                            else (o.item() if hasattr(o, "item") else str(o))))


def onset_table(state: str, W: int = 15) -> pl.DataFrame:
    """O1 onsets per period for one state at W, with project names and window start times (recomputed from series)."""
    ser = "series" if state == "project" else "series_work"
    cov = json.loads((R1B / ("coverage.json" if state == "project" else "coverage_work.json")).read_text())
    cal = pl.read_parquet(SH / "calendar.parquet").select("pt_date", "win_start")
    rows = []
    for g, c in cov.items():
        if f"w{W}" not in c or c[f"w{W}"]["q"] == 0:
            continue
        s = pl.read_parquet(R1B / f"G{int(g):02d}" / f"{ser}_w{W}.parquet").sort("gwin")
        q = c[f"w{W}"]["q"]
        k = s.select([f"k{a}" for a in range(1, q + 1)]).to_numpy().astype(int)
        n = s["n"].to_numpy().astype(int)
        on = E.find_onsets(k, n, s["win"].to_numpy(), s["day"].to_numpy(), E.P0 if W == 15 else E.P_W30)
        pj = pl.read_parquet(R1B / f"G{int(g):02d}" / (f"projects_w{W}.parquet" if state == "project" else f"projects_work_w{W}.parquet"))
        names = dict(zip(pj["label"].to_list(), pj["project"].to_list()))
        sj = s.join(cal, on="pt_date", how="left")
        for o in on:
            r = sj.row(o["w0"], named=True)
            rows.append(dict(goal=int(g), state=state, project=names.get(o["project"] + 1), w0=o["w0"], day=r["day"],
                             win=r["win"], pt_date=r["pt_date"], k=int(k[o["w0"], o["project"]]), n=int(n[o["w0"]])))
    return pl.DataFrame(rows) if rows else pl.DataFrame()


def compare():
    out = {}
    a = onset_table("project")
    w = onset_table("work")
    out["n_onsets"] = dict(attention=a.height, work=w.height,
                           attention_by_period=dict(a.group_by("goal").len().sort("goal").rows()) if a.height else {},
                           work_by_period=dict(w.group_by("goal").len().sort("goal").rows()) if w.height else {})
    # lags for projects with onsets in both spaces (same window grid: gwin = w0)
    lags = []
    if a.height and w.height:
        for r in w.iter_rows(named=True):
            m = a.filter((pl.col("goal") == r["goal"]) & (pl.col("project") == r["project"]))
            if m.height:
                d = r["w0"] - m["w0"].to_numpy()
                j = int(np.argmin(np.abs(d)))
                lags.append(dict(goal=r["goal"], project_rank=None, lag_windows=int(d[j]), w0_work=r["w0"], w0_att=int(m["w0"][j])))
    out["lags"] = lags
    out["lag_summary"] = dict(n=len(lags), median=float(np.median([x["lag_windows"] for x in lags])) if lags else None,
                              n_work_first=int(sum(x["lag_windows"] < 0 for x in lags)),
                              n_same=int(sum(x["lag_windows"] == 0 for x in lags)),
                              n_work_after=int(sum(x["lag_windows"] > 0 for x in lags)))
    # work onsets restricted to periods >= 30 (dense ledger) vs attention onsets on the same periods
    out["periods_ge30"] = dict(attention=int(a.filter(pl.col("goal") >= 30).height) if a.height else 0,
                               work=int(w.filter(pl.col("goal") >= 30).height) if w.height else 0)
    out["onsets_attention"] = a.to_dicts() if a.height else []
    out["onsets_work"] = w.to_dicts() if w.height else []
    out["g40"] = g40_minute_clock()
    jdump(out, R1B / "compare_r1b.json")
    print(json.dumps({k: v for k, v in out.items() if k not in ("onsets_attention", "onsets_work")}, indent=1, default=str)[:5000])


def g40_minute_clock():
    """#40 native (H27-R2): first strict mention of the hub per agent after its first chat link, at the minute clock;
    work: first work commit to the hub repo. Hub = label 1 of the shared attention labels."""
    sys.path.insert(0, str(ROOT / "infra/shared"))
    import project_states as PS
    pj = pl.read_parquet(H11R / "G40" / "projects_w30.parquet").sort("aw", descending=True)
    hub = pj.filter(pl.col("label") == 1)["project"][0]
    days = pl.read_parquet(H11R / "G40" / "windows_w30.parquet")["pt_date"].unique().sort().to_list()
    cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("pt_date").is_in(days)).sort("pt_date")
    kick = cal["win_start"][0]
    pm = PS.project_map()
    am = (pl.scan_parquet(SH / "artifact_mentions.parquet")
          .filter((pl.col("speaker_kind").cast(pl.String) == "agent") & pl.col("how").cast(pl.String).is_in(list(PS.STRICT_HOW))
                  & pl.col("agent").is_not_null()).select("artifact", "t", "agent", "source").collect()
          .join(pm, on="artifact", how="inner").filter((pl.col("project") == hub) & pl.col("t").is_between(kick - pl.duration(days=3), cal["win_end"][-1])))
    links = am.filter(pl.col("source").cast(pl.String) == "chat").sort("t")
    t_link = links["t"][0] if links.height else None
    rt = pl.read_parquet(SH / "rooms_timeline.parquet")
    room_agents = sorted(set(pl.read_parquet(H11R / "G40" / "labels_project_w30.parquet").filter(pl.col("room") == 4)["agent"].to_list()))
    first = am.filter(pl.col("t") >= kick).group_by("agent").agg(pl.col("t").min()).filter(pl.col("agent").is_in(room_agents))
    lag_k = np.sort(np.array([(t - kick).total_seconds() / 60 for t in first["t"].to_list()]))
    lag_l = np.sort(np.array([(t - t_link).total_seconds() / 60 for t in first["t"].to_list()])) if t_link else None
    half = int(np.ceil(len(room_agents) / 2))
    wc = (pl.scan_parquet(SH / "work_commits.parquet")
          .filter(pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind").cast(pl.String) == "agent") & ~pl.col("automated")
                  & (pl.col("repo").cast(pl.String) == hub) & (pl.col("t") >= kick)).select("t", "author_agent").collect())
    wfirst = wc.group_by("author_agent").agg(pl.col("t").min()).filter(pl.col("author_agent").is_in(room_agents))
    wl = np.sort(np.array([(t - kick).total_seconds() / 60 for t in wfirst["t"].to_list()]))
    # active minutes: the clock is wall time inside day 1 unless it crosses days; report day of t50
    return dict(hub_is_repo=bool(hub.startswith(("github.com", "gitlab.com"))), hub_label_share=float(pj.filter(pl.col("label") == 1)["share"][0]),
                kickoff=str(kick), first_chat_link=str(t_link), link_after_kickoff_min=((t_link - kick).total_seconds() / 60) if t_link else None,
                link_before_kickoff=bool(t_link is not None and t_link < kick),
                n_room_agents=len(room_agents), n_mentioned=int(len(lag_k)),
                t50_from_kickoff_min=float(lag_k[half - 1]) if len(lag_k) >= half else None,
                t50_from_link_min=float(lag_l[half - 1]) if (lag_l is not None and len(lag_l) >= half) else None,
                mention_lags_from_kickoff_min=lag_k.round(1).tolist(),
                n_work_committers=int(len(wl)), work_t50_from_kickoff_min=float(wl[half - 1]) if len(wl) >= half else None,
                work_lags_from_kickoff_min=wl.round(1).tolist(), work_commits_on_hub=int(wc.height))


def estimates():
    sys.path.insert(0, str(ROOT / "infra/shared"))
    import estimates as ES
    rows = []
    src = "data/processed/H27-herding-early-warning/r1b/"
    for state, f in (("project", "results_round1.json"), ("work", "results_round1_work.json")):
        R = json.loads((R1B / f).read_text())["W15"]
        for ps in R["period_summaries"]:
            g = int(ps["goal"])
            base = dict(period_unit=ES.map_unit(g), goal_no=g, role="replication", source=src + f, post_hoc=False,
                        status="exploratory round 1b (shared labels)")
            rows.append(dict(base, statistic="herding_onsets", channel=state, estimate=float(ps["n_onsets"]), ci_kind="none",
                             n=float(ps["T"]), n_kind="15-min windows", null="none (count)",
                             method="O1 project-share step onset (x >= 0.5, k >= 3, n >= 4, prior hour <= 0.25, next hour >= 0.4), W=15 (round 1b)"))
            fa = ps["operator"]["ews"]["false_alarms"]
            rows.append(dict(base, statistic="ews_false_alarms_per_day", channel=state, estimate=fa / max(ps["active_days_evaluated"], 1),
                             ci_kind="none", n=float(ps["active_days_evaluated"]), n_kind="active days", null="rate-matched circular shift",
                             method="frozen EWS alarm (tau_AR1 and tau_SD > 0.538 over 6 h, project below 30%), W=15 (round 1b)"))
            per = R["per_period"].get(str(g))
            if per and per["n_eval"] >= 2 and per["auc_composite"] is not None:
                rows.append(dict(base, statistic="ews_composite_auc", channel=state, estimate=per["auc_composite"], ci_kind="none",
                                 n=float(per["n_eval"]), n_kind="evaluable onsets", null="placebo segments (AUC 0.5)",
                                 method="Kendall-trend composite tau_AR1 + tau_SD at lead 1 h, onset vs matched placebo segments (round 1b)"))
    c = json.loads((R1B / "compare_r1b.json").read_text())["g40"]
    rows.append(dict(period_unit=ES.map_unit(40), goal_no=40, role="native", source=src + "compare_r1b.json", statistic="hub_t50_from_first_link_min",
                     channel="project", estimate=c["t50_from_link_min"], ci_kind="none", n=float(c["n_room_agents"]), n_kind="room agents",
                     null="none", method="minutes from the hub's first chat link until half the room's agents have a strict mention of it (round 1b native)",
                     post_hoc=False, status="exploratory round 1b native"))
    rows.append(dict(period_unit=ES.map_unit(40), goal_no=40, role="native", source=src + "compare_r1b.json", statistic="hub_t50_from_kickoff_min",
                     channel="work", estimate=c["work_t50_from_kickoff_min"], ci_kind="none", n=float(c["n_room_agents"]), n_kind="room agents",
                     null="none", method="minutes from the kickoff until half the room's agents have a work commit to the hub repo (round 1b native)",
                     post_hoc=False, status="exploratory round 1b native"))
    ES.write_estimates(rows, hypothesis="H27", replace_keys=("statistic", "channel", "method", "role"))
    print(f"estimates written: {len(rows)}")


if __name__ == "__main__":
    if MODE == "estimates":
        estimates()
    if MODE in ("replicate", "work"):
        import assemble as A
        X.main()
        A.main()
    elif MODE == "compare":
        compare()
