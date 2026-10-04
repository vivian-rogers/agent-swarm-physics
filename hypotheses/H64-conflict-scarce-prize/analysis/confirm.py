"""H64 confirmatory test on the LOCKED HOLDOUT. Written and frozen 2026-10-04 after exploratory round 1; NOT RUN.

Refuses to touch held-out data without:  --confirm --i-understand-this-uses-the-locked-holdout
and refuses if the H64 folder has uncommitted changes (the frozen script and card must be committed first).
Default is --dry-run on non-holdout stand-ins with the identical code path.

Targets (reuse policy hypotheses/holdout.md; holdout_ledger.check() is called and printed first):
  #29  breaking-news competition (held out, mode K): a competition prize period.
  #34  saboteur game with vote-outs into #voted-out (held out; NE30 window): a vote is a rival-exclusive outcome
       with dated settlements (DQ6 room_presence rows with room 'voted-out', preferred, holdout=True).
  #51 tail (2026-09-07 -> 09-21): rivalry without an exclusive prize.
Stand-ins for --dry-run: #29 -> #27; #34 -> #26 with two stand-in 'vote-outs' (agent 6 at the 01-05 result, agent 0 at
the 01-09 confirmatory vote); #51 tail -> units 51h-51l.

Frozen predictions (exploration values in brackets; prize-free median of r_p over 26 non-holdout prize-free units =
0.0094, 75th percentile 0.0135; DQ2 confident 'opposes' with opp_type = position, p_reply >= 0.5):
  C1 (primary): r_p(#29) > 0.0094 (the four exploratory competition periods: 0.011-0.034, 4/4 above). Credence 0.6.
  C2 (primary): r_p(#34) > 0.0094. Credence 0.5.
  C3 (#34 vote-outs, settlement switch): replies involving the agent voted out that day are more negative (soft stance)
     in the 2 h before its move to #voted-out than other replies in the same window, relative to the same contrast
     in the preceding 30 h (DiD with event effects): gamma_open < 0 with permutation p < 0.05 (the 'accused' label permuted
     among the agents with replies that day). [#12 debates: gamma_open -0.78, p 0.0002]. Credence 0.3.
  C4: r_p(#51 tail) < 0.0135 and at most half of the tail's units show excess antagonistic pairs (cluster-robust,
     agent-field null p <= 0.05). [#51 head 0.0106; 2/12 units]. Credence 0.6.
  Decision: 'competition raises position-opposition' confirmed if C1 and C2 pass; the settlement switch-off
  generalizes beyond assigned debates if C3 passes; 'rivalry without a prize stays at the floor' if C4 passes.
Output: data/processed/H64-conflict-scarce-prize/confirm/{results,dryrun}.json.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h64lib as L  # noqa: E402

ROOT = L.ROOT
OUT = ROOT / "data/processed/H64-conflict-scarce-prize/confirm"
UTC = dt.timezone.utc
FROZEN = {"pf_median": 0.0094, "pf_q75": 0.0135}
TAIL = ("2026-09-07", "2026-09-21")
FLAG = "--i-understand-this-uses-the-locked-holdout"


def guard(confirm: bool):
    if not confirm:
        return
    if FLAG not in sys.argv:
        raise SystemExit(f"refusing: add {FLAG}")
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "hypotheses/H64-conflict-scarce-prize"],
                           capture_output=True, text=True).stdout.strip()
    if dirty:
        raise SystemExit("refusing: commit the H64 folder (card + this script) before a confirmatory run")


def ledger():
    sys.path.insert(0, str(ROOT / "infra/shared"))
    import holdout_ledger as HL
    out = {}
    for tgt in ("G29", "G34", "#51-tail"):
        r = HL.check("H64", tgt, "stance labels", ["stance"])
        out[tgt] = {"allowed": r["allowed"], "needs_disclosure": r["needs_disclosure"],
                    "prior_runs": [u["hypothesis"] for u in r["prior_runs"]],
                    "competing_planned": sorted({u["hypothesis"] for u in r["competing_planned"]})}
    return out


def replies(confirm: bool) -> pl.DataFrame:
    import build as B
    B.ALLOW_HOLDOUT = confirm
    return B.load_replies()


def r_pos(rp: pl.DataFrame) -> dict:
    sys.path.insert(0, str(HERE))
    from run import day_boot
    b = day_boot(rp, ["pos_opp", "conf_opp", "s"])
    return {"r_pos": b["pos_opp"], "r_opp": b["conf_opp"], "sbar": b["s"], "n": rp.height}


def voteout_events(confirm: bool):
    if not confirm:
        return [(6, dt.datetime(2026, 1, 5, 19, 35, 22, tzinfo=UTC)), (0, dt.datetime(2026, 1, 9, 18, 45, tzinfo=UTC))]
    gt = pl.read_parquet(ROOT / "data/processed/shared/ground_truth_labels.parquet").filter(
        pl.col("preferred") & (pl.col("goal_no") == 34) & (pl.col("label_kind") == "room_presence")
        & (pl.col("value") == "voted-out"))
    return [(int(a), t) for a, t in gt.select("agent", "t_valid_from").iter_rows()]


def c3(rp: pl.DataFrame, events, P=5000, rng=None):
    rng = rng or np.random.default_rng(34)
    rows = []
    for a, tv in events:
        day = rp.filter((pl.col("t") < tv) & (pl.col("t") >= tv - dt.timedelta(hours=30)))
        if day.height == 0:
            continue
        rows.append(day.with_columns(acc=pl.lit(a), O=(pl.col("t") >= tv - dt.timedelta(hours=2)).cast(pl.Int8),
                                     ev=pl.lit(str(tv))))
    if not rows:
        return {"testable": False}
    d = pl.concat(rows).with_columns(R=(pl.col("b_agent") == pl.col("acc")) | (pl.col("a_agent") == pl.col("acc")))
    d = d.with_columns(pl.col("R").cast(pl.Int8))
    spk, tgt, N, _ = L.reindex(d["b_agent"].to_numpy(), d["a_agent"].to_numpy())
    y = d["s"].cast(pl.Float64).to_numpy()
    win = d["ev"].to_numpy()
    R, O = d["R"].to_numpy().astype(float), d["O"].to_numpy().astype(float)
    if (R * O).sum() < 5 or (R * (1 - O)).sum() < 5:
        return {"testable": False, "n_rival_open": int((R * O).sum())}
    est = L.did_fit(y, spk, tgt, win, R, O)
    ba, aa, ev = d["b_agent"].to_numpy(), d["a_agent"].to_numpy(), d["ev"].to_numpy()
    null = []
    for _ in range(P):
        Rp = np.zeros(len(d))
        for e in np.unique(ev):
            m = ev == e
            ags = np.unique(np.r_[ba[m], aa[m]])
            acc = rng.choice(ags)
            Rp[m] = (ba[m] == acc) | (aa[m] == acc)
        if (Rp * O).sum() == 0 or (Rp * (1 - O)).sum() == 0:
            continue
        null.append(L.did_fit(y, spk, tgt, win, Rp, O)["g_open"])
    p = L.perm_p(est["g_open"], np.array(null))
    return {"testable": True, **est, "p_open": p, "n": d.height, "n_rival_open": int((R * O).sum()),
            "pass": bool(est["g_open"] < 0 and p < 0.05)}


def c4_units(rp: pl.DataFrame):
    out = []
    for u in sorted(rp["unit_id"].unique().to_list()):
        x = rp.filter(pl.col("unit_id") == u)
        if x.height < 300:
            continue
        spk, tgt, N, _ = L.reindex(x["b_agent"].to_numpy(), x["a_agent"].to_numpy())
        e = L.excess(spk, tgt, x["y"].to_numpy(), x["block"].to_numpy(), N, R=200)
        out.append({"unit": u, "n": x.height, "p_af_robust": e["p_af_robust"], "n_neg_robust": e["n_neg_robust"]})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument(FLAG, action="store_true", dest="ack")
    a = ap.parse_args()
    guard(a.confirm)
    res = {"mode": "confirm" if a.confirm else "dryrun", "ledger": ledger(), "frozen": FROZEN,
           "run_at": dt.datetime.now(UTC).isoformat()}
    rp = replies(a.confirm)
    g29, g34 = (29, 34) if a.confirm else (27, 26)
    tail = (rp.filter((pl.col("goal_no") == 51) & (pl.col("pt_date") >= TAIL[0]) & (pl.col("pt_date") < TAIL[1]))
            if a.confirm else rp.filter(pl.col("unit_id").is_in(["51h", "51i", "51j", "51k", "51l"])))
    res["C1"] = r_pos(rp.filter(pl.col("goal_no") == g29))
    res["C1"]["pass"] = bool(res["C1"]["r_pos"][0] > FROZEN["pf_median"])
    res["C2"] = r_pos(rp.filter(pl.col("goal_no") == g34))
    res["C2"]["pass"] = bool(res["C2"]["r_pos"][0] > FROZEN["pf_median"])
    res["C3"] = c3(rp.filter(pl.col("goal_no") == g34), voteout_events(a.confirm))
    t = r_pos(tail)
    units = c4_units(tail)
    res["C4"] = {**t, "units": units, "pass": bool(t["r_pos"][0] < FROZEN["pf_q75"] and
                                                    sum(u["p_af_robust"] <= 0.05 for u in units) <= len(units) / 2)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / ("results.json" if a.confirm else "dryrun.json")).write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps({k: (v.get("pass") if isinstance(v, dict) else v) for k, v in res.items() if k.startswith("C")}))


if __name__ == "__main__":
    main()
