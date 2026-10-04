"""H34 confirmatory test on the locked holdout. WRITTEN 2026-10-04, NOT RUN on the holdout.

  uv run python hypotheses/H34-idea-cascades/analysis/confirm.py --dry-run
      runs the full pipeline on non-holdout stand-ins (#51 08-24 -> 09-05, #13, #25, #16); safe; exploration data only
  uv run python hypotheses/H34-idea-cascades/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
      reads held-out chat text (in memory only), builds cascades for the targets and scores the frozen predictions.
      Refuses to run without BOTH flags. Writes results/confirm_sealed.json (SHA-256 of the frozen predictions) BEFORE
      touching any held-out data, then results/confirm_results.json.

Targets (locked holdout; reuse policy in hypotheses/holdout.md):
  T1  #51 tail (2026-09-07 -> 09-21; the held-out days of goal 51)   primary: same mode/regime as G51
  T2  #15 (regime I, mode C)     T3  #28 (regime I, mode C)     T4  #22 (regime I, mode F)
Reuse disclosure: the #51 tail is also targeted by unrun confirm scripts of H14 (behavior entropy), H18 (mention
responses), H20 (content aging), H22 (content couplings); #22 and #28 by H11 (project choice) and H10 (#22 -> #23).
None has been run. H34's observable (first-use cascades of novel markers through visible exposure) is a different
statistic from all of them. Disclose in both cards and LOG.md if run. Avoided: #45 (H23 content copying), #14 (H24
numbers), #34 (six scripts).
Novelty for a target: a marker is an idea of the target if it is not used in the non-holdout corpus before the target's
first message (held-out text of *other* held-out periods is never read, so a marker introduced in another held-out
period counts as novel here: a small, disclosed contamination).

Frozen predictions (from round-1 exploration; C4 uses the post-hoc rule V3, amendment A6):
  C1 subcritical: R-hat upper 95% CI < 1 and R-hat in [0.08, 0.40] in every target.
  C2 contagion beyond the field: HR10 (recency k, idea-stratified conditional MLE) lower 95% CI > 1 in >= 3 of 4
     targets, and in T1.
  C3 per-pair dilution: log(R-hat/(N_room-1)) inside the 90% prediction interval of the non-holdout fit
     log(R/(N-1)) = -2.547 - 0.549 log(N-1) (s = 0.380, n = 32) in >= 3 of 4 targets.
  C4 forecast rule V3 (GW-NB with R-hat from the previous 2 days, k-hat, drift sigma_eta = 0.254): day-ahead 90% PI
     coverage >= 0.75 for P(s>=3) and >= 0.60 for P(s>=2), pooled over target days with >= 20 trees (and >= 30
     training trees); V3 beats the homogeneous-field binomial rival on summed log score in every target with >= 2
     scored days.
  C5 signature: pure s^-3/2 rejected (LR p < 0.05) and tau_app >= 2 in every target with >= 200 trees.
  C6 heterogeneity: in T1, observed P(s>=5) above the FN-GW 90% band; mean offspring of roots < non-roots in >= 3/4.
  Overall: SUPPORTED (as a subcritical, contagion-driven, heterogeneous branching description) if C1, C2 and C5 pass;
  the forecast rule is CONFIRMED if C4 passes. Each C is reported separately.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import os
import sys
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h34core as C  # noqa: E402
import h34stats as S  # noqa: E402
import markers as M  # noqa: E402
from explore import class_stats  # noqa: E402
from forecast_posthoc import tail_band  # noqa: E402
from build import room_size  # noqa: E402

sys.path.insert(0, str(C.ROOT / "infra/shared"))
from common import git_commit  # noqa: E402

RES = C.OUT / "results"
SIGMA_ETA = 0.254
FIT = dict(b0=-2.54716277, b1=-0.54904123, s=0.3799718257151742, n=32,
           XtXi=[[0.6595200449474959, -0.314938489391457], [-0.31493848939145697, 0.15787200567307297]])
TARGETS = {"T1": dict(goal=51, label="#51 tail"), "T2": dict(goal=15, label="#15"), "T3": dict(goal=28, label="#28"),
           "T4": dict(goal=22, label="#22")}
STANDINS = {"T1": dict(goal=51, label="#51 08-24 -> 09-05 (stand-in)", dates=("2026-08-24", "2026-09-05")),
            "T2": dict(goal=13, label="#13 (stand-in for #15)"), "T3": dict(goal=25, label="#25 (stand-in for #28)"),
            "T4": dict(goal=16, label="#16 (stand-in for #22)")}
PREDICTIONS_TEXT = __doc__


def marker_uses_for_rows(sh: C.Shared, rows: np.ndarray) -> pl.DataFrame:
    """Extract markers (same rule as build_markers) for the given chat_core rows; text in memory only."""
    ids = sh.chat.filter(pl.col("msg").is_in(rows)).select("msg")
    mid = pl.read_parquet(C.SH / "chat_core.parquet", columns=["message_id"]).with_row_index("msg").join(ids, on="msg")
    txt = (pl.scan_parquet(C.SH / "chat_text.parquet").select("message_id", "text")
           .join(mid.lazy(), on="message_id", how="inner").select("msg", "text").collect())
    ros = M.roster_full_names(sh.roster["name"].to_list())
    msg, mk, cl = [], [], []
    for r, t in zip(txt["msg"].to_list(), txt["text"].to_list()):
        for c, x in M.extract(t, ros):
            msg.append(r)
            mk.append(M.marker_id(c, x))
            cl.append(M.CLS[c])
    del txt
    art = pl.read_parquet(C.SH / "artifacts.parquet", columns=["artifact", "kind"])
    am = (pl.read_parquet(C.SH / "artifact_mentions.parquet", columns=["artifact", "source", "how", "message_id"])
          .filter((pl.col("source") == "chat") & pl.col("how").cast(pl.Utf8).is_in(["url", "bare"]))
          .join(art, on="artifact").filter(pl.col("kind").cast(pl.Utf8).is_in(["repo", "site", "file"]))
          .join(mid, on="message_id", how="inner"))
    u = pl.DataFrame({"msg": am["msg"].cast(pl.UInt32), "marker": [M.marker_id("U", str(a)) for a in am["artifact"].to_list()],
                      "cls": pl.Series([0] * am.height, dtype=pl.UInt8)})
    d = pl.DataFrame({"msg": pl.Series(msg, dtype=pl.UInt32), "marker": pl.Series(mk, dtype=pl.Int64),
                      "cls": pl.Series(cl, dtype=pl.UInt8)})
    return pl.concat([u, d]).unique(["msg", "marker"])


def run_unit(sh: C.Shared, goal: int, days: list[str]) -> dict:
    chat = sh.chat.filter((pl.col("goal_no") == goal) & pl.col("pt_date").is_in(days)).sort("msg")
    rows = chat["msg"].to_numpy()
    uses = marker_uses_for_rows(sh, rows)
    t0 = chat["t"].min()
    seen_before = sh.first_seen.filter(pl.col("first_t") < t0).select("marker")
    uses = uses.join(seen_before, on="marker", how="anti")
    # first use within the unit (any speaker) defines the idea set: all remaining markers are novel here
    inp = C.period_inputs(sh, goal, days=days, uses=uses)
    res = C.assemble(inp, atrisk_cap=4000, seed=goal)
    N = room_size(inp)
    st = class_stats(res["first_uses"], res["trees"], res["atrisk"], res["jitter"], res["roomx"], N, "ALL", seed=goal)
    st["N_room"] = N
    st["n_days"] = len(days)
    st["forecast"] = forecast_v3(res, N)
    return st


def forecast_v3(res, N) -> dict:
    tr, fu = res["trees"], res["first_uses"]
    Nf = max(N, int(tr["size"].max()))
    rng = np.random.default_rng(7)
    out = []
    for d in sorted(tr["day"].unique().to_list())[1:]:
        tst, trn = tr.filter(pl.col("day") == d), tr.filter((pl.col("day") < d) & (pl.col("day") >= d - 2))
        if tst.height < 20 or trn.height < 30:
            continue
        fu_t = fu.join(trn.select("idea", "tree"), on=["idea", "tree"], how="inner")
        R = float((((fu_t["status"] == 1) & (fu_t["parent"] >= 0)).sum()) / fu_t.height)
        k = S.fit_offspring(fu_t["offspring"].to_numpy())["k"]
        s_te = np.minimum(tst["size"].to_numpy(), Nf)
        n = len(s_te)
        b2, b3 = tail_band(R, k, Nf, n, SIGMA_ETA, rng)
        p = S.nb_gw_pmf_trunc(R, k, Nf)
        s_tr = np.minimum(trn["size"].to_numpy(), Nf)
        eps = (s_tr - 1).mean() / (Nf - 1)
        pb = stats.binom.pmf(np.arange(Nf), Nf - 1, min(max(eps, 1e-9), 1 - 1e-9))
        o2, o3 = float((s_te >= 2).mean()), float((s_te >= 3).mean())
        out.append(dict(day=int(d), n=n, cover2=bool(b2[0] <= o2 <= b2[1]), cover3=bool(b3[0] <= o3 <= b3[1]),
                        ls_v3=float(np.log(np.maximum(p[s_te - 1], 1e-9)).sum()),
                        ls_binom=float(np.log(np.maximum(pb[s_te - 1], 1e-9)).sum())))
    return dict(days=out)


def score(units: dict) -> dict:
    out = {}
    U = units
    out["C1"] = all(u["R_hi"] < 1 and 0.08 <= u["R"] <= 0.40 for u in U.values())
    hr = {k: bool(u.get("contagion_pass")) for k, u in U.items()}
    out["C2"] = sum(hr.values()) >= 3 and hr.get("T1", False)
    inside = {}
    for k, u in U.items():
        x = math.log(u["N_room"] - 1)
        y = math.log(u["R"] / (u["N_room"] - 1))
        xv = np.array([1.0, x])
        se = FIT["s"] * math.sqrt(1 + xv @ np.array(FIT["XtXi"]) @ xv)
        tq = stats.t.ppf(0.95, FIT["n"] - 2)
        pred = FIT["b0"] + FIT["b1"] * x
        inside[k] = bool(abs(y - pred) <= tq * se)
    out["C3"] = sum(inside.values()) >= 3
    days = [d for u in U.values() for d in u["forecast"]["days"]]
    c2 = np.mean([d["cover2"] for d in days]) if days else float("nan")
    c3 = np.mean([d["cover3"] for d in days]) if days else float("nan")
    beats = {k: (sum(d["ls_v3"] for d in u["forecast"]["days"]) > sum(d["ls_binom"] for d in u["forecast"]["days"]))
             for k, u in U.items() if len(u["forecast"]["days"]) >= 2}
    out["C4"] = bool(days) and c3 >= 0.75 and c2 >= 0.60 and all(beats.values())
    out["C5"] = all((u.get("p_15pure", 1) < 0.05 and u.get("tau_app", 0) >= 2) for u in U.values() if u["trees"] >= 200)
    t1 = U.get("T1", {})
    out["C6"] = bool(t1.get("p5", 0) > (t1.get("fn_hi5") or 1)) and sum(
        (u.get("off_root", 1) < u.get("off_nonroot", 0)) for u in U.values()) >= 3
    out["detail"] = dict(hr10_pass=hr, c3_inside=inside, forecast_cover2=c2, forecast_cover3=c3, forecast_days=len(days),
                         v3_beats_binom=beats)
    out["overall_supported"] = bool(out["C1"] and out["C2"] and out["C5"])
    out["forecast_confirmed"] = bool(out["C4"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    a = ap.parse_args()
    if a.confirm and not a.ack:
        sys.exit("Refusing: --confirm also needs --i-understand-this-uses-the-locked-holdout.")
    if not a.confirm and not a.dry_run:
        sys.exit("Choose --dry-run (non-holdout stand-ins) or --confirm --i-understand-this-uses-the-locked-holdout.")
    sh = C.Shared()
    units = {}
    if a.confirm:
        RES.mkdir(parents=True, exist_ok=True)
        sealed = RES / "confirm_sealed.json"
        h = hashlib.sha256(PREDICTIONS_TEXT.encode()).hexdigest()
        if not sealed.exists():
            sealed.write_text(json.dumps({"sha256": h, "sealed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                                          "git_commit": git_commit()}, indent=1))
        elif json.loads(sealed.read_text())["sha256"] != h:
            sys.exit("Frozen predictions changed since sealing: refusing.")
        for k, t in TARGETS.items():
            days = sh.period_days(t["goal"], only_holdout=True)
            units[k] = run_unit(sh, t["goal"], days)
        out_path = RES / "confirm_results.json"
    else:
        for k, t in STANDINS.items():
            days = sh.period_days(t["goal"])
            if t.get("dates"):
                days = [d for d in days if t["dates"][0] <= d < t["dates"][1]]
            units[k] = run_unit(sh, t["goal"], days)
        out_path = RES / "confirm_dryrun.json"
    sc = score(units)
    keep = ("R", "R_lo", "R_hi", "R_c", "hr10", "hr10_lo", "hr10_hi", "p2", "p3", "p5", "fn_hi5", "tau_app", "p_15pure",
            "off_root", "off_nonroot", "trees", "nodes", "N_room", "n_days", "forecast")
    rep = {"mode": "confirm" if a.confirm else "dry-run (non-holdout stand-ins)",
           "units": {k: {kk: u.get(kk) for kk in keep} | {"label": (TARGETS if a.confirm else STANDINS)[k]["label"]}
                     for k, u in units.items()},
           "score": sc, "run_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    out_path.write_text(json.dumps(rep, indent=1, default=float))
    print(json.dumps({k: v for k, v in sc.items()}, indent=1, default=float))


if __name__ == "__main__":
    main()
