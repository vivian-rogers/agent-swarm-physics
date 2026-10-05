"""H36 round 2 (2026-10-05): write a <!-- R2 --> block into each goal-period README (kickoff periods) and into the NE
folders the round touches (NE34 kickoffs overall, NE42 room A-B-A, NE43 #focus, NE14 / NE17 / NE40 / NE45 scaffold
detector). Idempotent: an existing R2 block is replaced. Numbers come from data/processed/H36-reorganization-alarm/r2/.

Usage: uv run python hypotheses/H36-reorganization-alarm/analysis/r2_periods.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h36lib as L  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

R2 = L.OUT / "r2"
GP = L.HYP / "goalperiod-subhypotheses"


def f(x, nd=2):
    return "–" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:.{nd}f}"


def put(folder: str, body: str):
    p = GP / folder / "README.md"
    if not p.exists():
        return False
    s = p.read_text()
    block = f"<!-- R2 -->\n{body.strip()}\n<!-- /R2 -->"
    if "<!-- R2 -->" in s:
        s = re.sub(r"<!-- R2 -->.*?<!-- /R2 -->", lambda m: block, s, flags=re.S)
    else:
        s = s.rstrip() + "\n\n## Round 2 (2026-10-05)\n" + block + "\n"
    p.write_text(s)
    return True


def main():
    intr = {t: json.loads((R2 / f"intraday_{t}.json").read_text()) for t in ("bge", "gte")}
    kk = {t: {k["ref"]: k for k in intr[t]["kickoffs"]} for t in intr}
    et = {t: pl.read_parquet(R2 / f"rob_{t}_restate" / "event_table.parquet").filter(pl.col("cls") == "goal") for t in ("bge", "gte")}
    inv = pl.read_parquet(R2 / "activity_inv.parquet")
    zi = dict(zip(inv["aday"].to_list(), inv["Z_act_inv"].to_list()))
    n = 0
    for r in et["bge"].iter_rows(named=True):
        g = int(r["ref"][1:])
        rg = et["gte"].filter(pl.col("ref") == r["ref"]).row(0, named=True)
        lines = ["Round-2 readouts at this period's kickoff (card: Round 2; predictions P2.1–P2.3, RB1, P3.2). Role: replication (exploratory).", "",
                 "| Readout | bge | gte |", "| --- | --- | --- |"]
        for t in ("bge", "gte"):
            pass
        zw = {t: kk[t].get(r["ref"], {}).get("z_by_win", {}) for t in ("bge", "gte")}
        fa = {t: kk[t].get(r["ref"], {}).get("first_alarm_win") for t in ("bge", "gte")}
        lines.append(f"| intraday topic-shift z, windows 0 / 1 / 2 of day 0 | " + " | ".join(
            " / ".join(f(zw[t].get(str(w))) for w in (0, 1, 2)) for t in ("bge", "gte")) + " |")
        lines.append(f"| first intraday alarm window (z ≥ 3) | {fa['bge'] if fa['bge'] is not None else 'none'} | {fa['gte'] if fa['gte'] is not None else 'none'} |")
        lines.append(f"| frozen C3 score, max over days −1..+1 (alarm ≥ 2) | {f(r['C3_wmax'])} | {f(rg['C3_wmax'])} |")
        zv = [zi.get(r["aday0"] + o) for o in (-1, 0, 1)]
        lines.append(f"| Z_act_inv (sampling-invariant activity), days −1 / 0 / +1 | " + " / ".join(f(x) for x in zv) + " | (same) |")
        lines += ["", "Data: `data/processed/H36-reorganization-alarm/r2/` (intraday_<model>.json, rob_<model>_restate/, activity_inv.parquet)."]
        if r["n_scored"] and put(f"G{g:02d}", "\n".join(lines)):
            n += 1
    # NE34: kickoffs overall
    rb = json.loads((R2 / "robust.json").read_text()); act = json.loads((R2 / "activity_inv.json").read_text())
    b = ["Round-2 readouts over all scored kickoffs (card: Round 2).", "",
         "| Readout | bge | gte |", "| --- | --- | --- |",
         f"| intraday alarm in the first 2 windows of day 0: kickoffs vs placebo days | {f(intr['bge']['kickoff_first2_rate'][0])} vs {f(intr['bge']['placebo_first2_rate'][0])} | {f(intr['gte']['kickoff_first2_rate'][0])} vs {f(intr['gte']['placebo_first2_rate'][0])} |",
         f"| AUC (max z in windows 0–1), kickoff vs placebo days | {f(intr['bge']['auc_first2_kickoff_vs_placebo'])} | {f(intr['gte']['auc_first2_kickoff_vs_placebo'])} |",
         f"| lead: alarm in the last 4 windows of day −1 vs placebo days | {f(intr['bge']['kickoff_dm1_last4_rate'][0])} vs {f(intr['bge']['placebo_last4_rate'][0])} | {f(intr['gte']['kickoff_dm1_last4_rate'][0])} vs {f(intr['gte']['placebo_last4_rate'][0])} |",
         f"| C3 hit · window FAR (restate, round-2 seed) | {f(rb['variants']['bge_restate']['C3']['hit'])} · {f(rb['variants']['bge_restate']['C3']['far_win_placebo'])} | {f(rb['variants']['gte_restate']['C3']['hit'])} · {f(rb['variants']['gte_restate']['C3']['far_win_placebo'])} |",
         f"| C3 window FAR on Monday placebos M1 · M2 | {f(rb['variants']['bge_restate']['C3']['far_win_M1'])} · {f(rb['variants']['bge_restate']['C3']['far_win_M2'])} | {f(rb['variants']['gte_restate']['C3']['far_win_M1'])} · {f(rb['variants']['gte_restate']['C3']['far_win_M2'])} |",
         f"| Z_act_inv AUC day 0 [95% CI] | {f(act['Z_act_inv']['auc_d0'])} [{f(act['Z_act_inv']['auc_d0_ci'][0])}, {f(act['Z_act_inv']['auc_d0_ci'][1])}] | (activity) |",
         "", "Verdict for this NE (round 2): **supported** for the intraday timing (all first alarms in window 0); the physics alarm verdict (mixed/failed) is unchanged."]
    put("NE34", "\n".join(b))
    # rooms
    ro = {t: intr[t]["rooms"] for t in intr}

    def roomline(k, lab):
        return (f"| {lab} | window {ro['bge'][k]['win_of_event']} | " + " | ".join(
            ", ".join(f"w{w}: {f(z)}" for w, z in ro[t][k]["z_near"].items()) + (" (alarm)" if ro[t][k]["alarm_within_1"] else "") for t in ("bge", "gte")) + " |")
    put("NE42", "\n".join(["Intraday timing of the A-B-A (card: Round 2, P2.4). Design fact: the merge room was created 16:07 UTC, 4 min after the #40 kickoff message and before the day window (17:01 UTC); agents moved in at 17:01–17:19 UTC. Both steps are day-start events.", "",
                           "| Event | event window | intraday z near the event, bge | gte |", "| --- | --- | --- | --- |",
                           roomline("merge_0504", "merge 05-04"), roomline("split_0511", "split back 05-11"), "",
                           "Both fire in window 0, as predicted [0.6]: held. They cannot be separated from the kickoffs of #40 and #41."]))
    put("NE43", "\n".join(["Intraday timing of the #focus room, 08-05 (card: Round 2, P2.4; native, exploratory). Room created 16:36 UTC; first agent move 17:39 UTC (window 3; day window opened 16:00 UTC).", "",
                           "| Event | event window | intraday z near the event, bge | gte |", "| --- | --- | --- | --- |",
                           roomline("focus_0805", "#focus first move"), roomline("side_room_0724", "side-room 07-24 (#51)"), "",
                           "Prediction (alarm within ±1 window of the first move) [0.35]: **mixed**: gte alarms in window 2 (z 3.2, between the room's creation and the first move); bge peaks there at 2.3, below the threshold. Side-room silent, as predicted [0.7]."]))
    sc = json.loads((R2 / "scaffold.json").read_text())
    nm = sc["named"]
    for folder, key, pred in (("NE14", "NE14b_0324", "alarm [0.85]: **supported** (bash grammar)"),
                              ("NE45", "NE45_0729", "not separately predicted; the schema diff S dates it, R5 does not"),
                              ("NE40", "NE40_0420", "not separately predicted"), ("NE17", "NE17_0414", "not separately predicted")):
        x = nm[key]
        put(folder, "\n".join([f"Scaffold detector R5 (card: Round 2; prediction P5.3 for NE14b: {pred}).", "",
                               "| Channel | z on day 0 |", "| --- | --- |",
                               f"| z_R5 (alarm ≥ 4) | {f(x['R5'])} |", f"| tool mix | {f(x['tool'])} |", f"| bash grammar | {f(x['bash'])} |",
                               f"| context-boundary rate (abs) | {f(x['bnd_abs'])} |", f"| schema diff S (H74, shared) | {f(x['S'], 0)} |",
                               f"| H74 mix M | {f(x['M_h74'])} |", "", "Data: `data/processed/H36-reorganization-alarm/r2/scaffold_days.parquet`."]))
    print(f"wrote R2 blocks: {n} G folders + NE34, NE42, NE43, NE14, NE45, NE40, NE17")


if __name__ == "__main__":
    main()
