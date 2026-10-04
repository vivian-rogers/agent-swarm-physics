"""H34 confirmatory test on the locked holdout, RE-FROZEN ON ROUND-1B INPUTS. WRITTEN 2026-10-04, NOT RUN on the holdout.

Re-freeze of `confirm.py` (left byte-for-byte untouched), written before any held-out data was read. Details in
`CONFIRM_R1B.md`. Inputs switched:
  * visibility: DQ1 context ledger (H34_DATA=r1b in scheme/h34core.py): a use m is a visible exposure of agent j's use u
    iff m reached one of j's receiving calls no later than the call that produced u. Sets k_src, parents, lags, at-risk
    sets (HR10), the jitter null and the room contrast (round 1 used H18's call-start rule);
  * new H57 in-flight placebo (C7-r1b): adoption hazard after read vs not-yet-read uses in the last 5 min;
  * C3's dilution fit and C4's drift sigma_eta re-estimated on the round-1b non-holdout period table (same estimators;
    the same code on round-1 tables reproduces the original constants exactly).
Not inputs of H34: activity bins, outages, embeddings (ideas are hashed text markers, so the two-model rule does not
apply), work ledger, failures, nudges.

  uv run python hypotheses/H34-idea-cascades/analysis/confirm_r1b.py --dry-run [--out FILE]
      full pipeline on non-holdout stand-ins (#51 08-24 -> 09-05, #13, #25, #16); exploration data only
  uv run python hypotheses/H34-idea-cascades/analysis/confirm_r1b.py --confirm --i-understand-this-uses-the-locked-holdout
      reads held-out chat text (in memory only), builds cascades for the targets and scores the frozen predictions.
      Refuses without BOTH flags, and unless infra/shared/holdout_ledger.check() allows every target. Writes
      results/confirm_r1b_sealed.json (SHA-256 of these predictions) BEFORE touching held-out data, then
      r1b/results/confirm_r1b_results.json.

Targets (unchanged; locked holdout): T1 #51 tail (primary), T2 #15, T3 #28, T4 #22 (regime I).
Reuse (ledger L212-L215): no prior run on any target. Planned same-family users: #51 tail H08, H18, H29, H37, H39;
#22 H11, H28; #28 H08, H11, H18, H28. Whoever runs first makes the others second users (disclose in cards + LOG.md).
Novelty contamination (unchanged, disclosed): markers first introduced in another held-out period count as novel.

Frozen predictions (round-1b re-freeze; C4 uses the post-hoc rule V3, amendment A6):
  C1 subcritical: R-hat upper 95% CI < 1 and R-hat in [0.08, 0.40] in every target. (unchanged; round 1b 0.09-0.40)
  C2 contagion beyond the field: HR10 lower 95% CI > 1 in >= 3 of 4 targets, and in T1. (unchanged; round 1b 32/32)
  C3-r1b per-pair dilution: log(R-hat/(N_room-1)) inside the 90% prediction interval of the round-1b non-holdout fit
     log(R/(N-1)) = -2.232 - 0.663 log(N-1) (s = 0.367, n = 32) in >= 3 of 4 targets.
     (was -2.547 - 0.549 log(N-1), s = 0.380 on round-1 visibility; reason: ledger visibility changes R-hat)
  C4-r1b forecast rule V3 (GW-NB with R-hat from the previous 2 days, k-hat, drift sigma_eta = 0.245): day-ahead 90% PI
     coverage >= 0.75 for P(s>=3) and >= 0.60 for P(s>=2), pooled over target days with >= 20 trees (and >= 30
     training trees); V3 beats the homogeneous-field binomial rival on summed log score in every target with >= 2
     scored days. (was sigma_eta = 0.254; reason: re-estimated on round-1b trees, leave-one-period-out median)
  C5 signature: pure s^-3/2 rejected (LR p < 0.05) and tau_app >= 2 in every target with >= 200 trees. (unchanged)
  C6 heterogeneity: in T1, observed P(s>=5) above the FN-GW 90% band; mean offspring of roots < non-roots in >= 3/4.
  C7-r1b copying beyond convergence (new; H57 placebo): HR_seen5 > HR_unread5 in >= 3 of 4 targets. (round 1b 30/32)
  Overall: SUPPORTED (subcritical, contagion-driven, heterogeneous branching) if C1, C2 and C5 pass; the forecast rule
  is CONFIRMED if C4-r1b passes; "copying through reading beyond convergence" CONFIRMED if C7-r1b passes. Each C is
  reported separately.
"""
from __future__ import annotations

import os

os.environ["H34_DATA"] = "r1b"
os.environ.setdefault("POLARS_MAX_THREADS", "2")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h34core as C  # noqa: E402
import h34stats as S  # noqa: E402
from explore import class_stats  # noqa: E402
from forecast_posthoc import tail_band  # noqa: E402
from build import room_size  # noqa: E402
import confirm as C0  # noqa: E402  (marker extraction, unchanged)

sys.path.insert(0, str(C.ROOT / "infra/shared"))
from common import git_commit  # noqa: E402

assert C.R1B
HYP = "H34"
RES = C.OUT / "results"
RES1B = C.OUT_RUN / "results"
SIGMA_ETA = 0.245          # round-1b LOPO median (r1b/G*/trees.parquet); the same code on round-1 trees gives 0.253
FIT = dict(b0=-2.23237733352803, b1=-0.6634100788956541, s=0.367320875888109, n=32,
           XtXi=[[0.6595200449474959, -0.314938489391457], [-0.31493848939145697, 0.15787200567307297]])
TARGETS = C0.TARGETS
STANDINS = C0.STANDINS
LEDGER_T = {"T1": "#51-tail", "T2": "G15", "T3": "G28", "T4": "G22"}
PREDICTIONS_TEXT = __doc__


def ledger_status() -> list[str]:
    sys.path.insert(0, str(C.ROOT))
    from infra.shared import holdout_ledger as hl
    led = hl.load()
    bad = []
    for k, t in LEDGER_T.items():
        fam = sorted({f for e in led["entries"] if e["hypothesis"] == HYP and e["target"] == t for f in e["estimator_family"]})
        r = hl.check(HYP, t, "message content", fam or ["cascade"])
        print(f"ledger {t}: allowed={r['allowed']} needs_disclosure={r['needs_disclosure']} "
              f"prior_runs={sorted({u['hypothesis'] for u in r['prior_runs']})} "
              f"competing_planned={sorted({u['hypothesis'] for u in r['competing_planned']})}", flush=True)
        if not r["allowed"]:
            bad.append(t)
    return bad


def allow_holdout_ledger():
    """Confirm path only: h34core.ledger_arrays asserts that no held-out call joins (exploration guard). Re-bind a copy
    without that assertion; identical otherwise."""
    def ledger_arrays_h(chat, t, kind, sender, n_agents, t0, t1):
        mids = chat["message_id"].to_list()
        pos = pl.DataFrame({"message_id": mids, "pos": np.arange(len(mids), dtype=np.int64)})
        it = pl.scan_parquet(C.SH / "context_ledger_items.parquet").select("turn_id", "message_id").join(
            pos.lazy(), on="message_id", how="inner").collect()
        cw = (pl.scan_parquet(C.SH / "call_windows.parquet").select("turn_id", "agent", "t_call")
              .filter((pl.col("t_call") >= t0) & (pl.col("t_call") <= t1)).collect())
        j = it.join(cw.select("turn_id", "agent", "t_call"), on="turn_id", how="inner")
        TS = np.full((len(mids), n_agents), C.INF_US, dtype=np.int64)
        if j.height:
            np.minimum.at(TS, (j["pos"].to_numpy(), j["agent"].to_numpy().astype(np.int64)), C._us(j["t_call"]))
        cs = t - C.GUARD_US
        cfb = np.ones(len(t), dtype=bool)
        for a in np.unique(sender[kind == 0]):
            if a < 0:
                continue
            ca = np.sort(C._us(cw.filter(pl.col("agent") == int(a))["t_call"]))
            idx = np.where((kind == 0) & (sender == a))[0]
            if len(ca) == 0:
                continue
            k = np.searchsorted(ca, t[idx], side="left") - 1
            ok = k >= 0
            ok &= (t[idx] - ca[np.clip(k, 0, None)]) <= C.STALE_US
            cs[idx[ok]] = ca[k[ok]]
            cfb[idx[ok]] = False
        return dict(TS=TS, cs=cs, cs_fb=cfb, n_ledger_items=int(j.height))
    C.ledger_arrays = ledger_arrays_h


def run_unit(sh: C.Shared, goal: int, days: list[str]) -> dict:
    chat = sh.chat.filter((pl.col("goal_no") == goal) & pl.col("pt_date").is_in(days)).sort("msg")
    rows = chat["msg"].to_numpy()
    uses = C0.marker_uses_for_rows(sh, rows)
    t0 = chat["t"].min()
    seen_before = sh.first_seen.filter(pl.col("first_t") < t0).select("marker")
    uses = uses.join(seen_before, on="marker", how="anti")
    inp = C.period_inputs(sh, goal, days=days, uses=uses)
    res = C.assemble(inp, atrisk_cap=4000, seed=goal)
    N = room_size(inp)
    st = class_stats(res["first_uses"], res["trees"], res["atrisk"], res["jitter"], res["roomx"], N, "ALL", seed=goal)
    st["N_room"] = N
    st["n_days"] = len(days)
    st["fallback_frac"] = float(np.mean(inp["cs_fb"][inp["kind"] == 0])) if "cs_fb" in inp else None
    st["forecast"] = forecast_v3(res, N)
    return st


def forecast_v3(res, N) -> dict:
    """confirm.forecast_v3 with this module's SIGMA_ETA."""
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


def score(U: dict) -> dict:
    out = {}
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
        inside[k] = bool(abs(y - (FIT["b0"] + FIT["b1"] * x)) <= tq * se)
    out["C3_r1b"] = sum(inside.values()) >= 3
    days = [d for u in U.values() for d in u["forecast"]["days"]]
    c2 = np.mean([d["cover2"] for d in days]) if days else float("nan")
    c3 = np.mean([d["cover3"] for d in days]) if days else float("nan")
    beats = {k: (sum(d["ls_v3"] for d in u["forecast"]["days"]) > sum(d["ls_binom"] for d in u["forecast"]["days"]))
             for k, u in U.items() if len(u["forecast"]["days"]) >= 2}
    out["C4_r1b"] = bool(days) and c3 >= 0.75 and c2 >= 0.60 and all(beats.values())
    out["C5"] = all((u.get("p_15pure", 1) < 0.05 and u.get("tau_app", 0) >= 2) for u in U.values() if u["trees"] >= 200)
    t1 = U.get("T1", {})
    out["C6"] = bool(t1.get("p5", 0) > (t1.get("fn_hi5") or 1)) and sum(
        (u.get("off_root", 1) < u.get("off_nonroot", 0)) for u in U.values()) >= 3
    sv = {k: bool(u.get("hr_seen5") is not None and u.get("hr_unread5") is not None
                  and np.isfinite(u["hr_seen5"]) and u["hr_seen5"] > u["hr_unread5"]) for k, u in U.items()}
    out["C7_r1b"] = sum(sv.values()) >= 3
    out["detail"] = dict(hr10_pass=hr, c3_inside=inside, forecast_cover2=c2, forecast_cover3=c3, forecast_days=len(days),
                         v3_beats_binom=beats, seen5_gt_unread5=sv)
    out["overall_supported"] = bool(out["C1"] and out["C2"] and out["C5"])
    out["forecast_confirmed"] = bool(out["C4_r1b"])
    out["copying_beyond_convergence_confirmed"] = bool(out["C7_r1b"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--out", type=Path, default=RES1B / "confirm_r1b_dryrun.json", help="dry-run result file")
    a = ap.parse_args()
    if a.confirm and not a.ack:
        sys.exit("Refusing: --confirm also needs --i-understand-this-uses-the-locked-holdout.")
    if not a.confirm and not a.dry_run:
        sys.exit("Choose --dry-run (non-holdout stand-ins) or --confirm --i-understand-this-uses-the-locked-holdout.")
    bad = ledger_status()
    sh = C.Shared()
    units = {}
    if a.confirm:
        if bad:
            sys.exit(f"Refusing: holdout_ledger.check() blocks {bad}.")
        RES.mkdir(parents=True, exist_ok=True)
        sealed = RES / "confirm_r1b_sealed.json"
        h = hashlib.sha256(PREDICTIONS_TEXT.encode()).hexdigest()
        if not sealed.exists():
            sealed.write_text(json.dumps({"sha256": h, "sealed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                                          "git_commit": git_commit()}, indent=1))
        elif json.loads(sealed.read_text())["sha256"] != h:
            sys.exit("Frozen predictions changed since sealing: refusing.")
        allow_holdout_ledger()
        for k, t in TARGETS.items():
            days = sh.period_days(t["goal"], only_holdout=True)
            units[k] = run_unit(sh, t["goal"], days)
        RES1B.mkdir(parents=True, exist_ok=True)
        out_path = RES1B / "confirm_r1b_results.json"
    else:
        for k, t in STANDINS.items():
            days = sh.period_days(t["goal"])
            if t.get("dates"):
                days = [d for d in days if t["dates"][0] <= d < t["dates"][1]]
            units[k] = run_unit(sh, t["goal"], days)
            print(k, "done", flush=True)
        out_path = a.out
    sc = score(units)
    keep = ("R", "R_lo", "R_hi", "R_c", "hr10", "hr10_lo", "hr10_hi", "hr_seen5", "hr_seen5_lo", "hr_seen5_hi",
            "hr_unread5", "hr_unread5_lo", "hr_unread5_hi", "p2", "p3", "p5", "fn_hi5", "tau_app", "p_15pure",
            "off_root", "off_nonroot", "trees", "nodes", "N_room", "n_days", "fallback_frac", "forecast")
    rep = {"mode": "confirm r1b" if a.confirm else "dry-run r1b (non-holdout stand-ins)",
           "units": {k: {kk: u.get(kk) for kk in keep} | {"label": (TARGETS if a.confirm else STANDINS)[k]["label"]}
                     for k, u in units.items()},
           "score": sc, "constants": {"sigma_eta": SIGMA_ETA, "fit": FIT},
           "run_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(rep, indent=1, default=float))
    print(json.dumps({k: v for k, v in sc.items()}, indent=1, default=float))


if __name__ == "__main__":
    main()
