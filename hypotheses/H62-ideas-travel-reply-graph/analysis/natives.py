"""H62 native tests (predictions in the period READMEs, in analysis/write_period_cards.py since 2026-10-04 19:33 UTC, before running).

  G51   dilution in the largest rooms: Lambda and T_room vs the other regime-III periods
  NE42  #39 -> #40 -> #41: T_room vs T_rep across the merge; cross-group pairs (by the #39 partition) in #40
  G12   DQ6 debate teams: reply exposure across teams vs room-only exposure from team-mates
  uv run python hypotheses/H62-ideas-travel-reply-graph/analysis/natives.py
Output: data/processed/H62-ideas-travel-reply-graph/results/natives.json (+ G12/, NE42/ split cells)
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2"

import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
sys.path.insert(0, str(ROOT / "infra/shared"))
import h62core as C  # noqa: E402
import h62lib as L  # noqa: E402
import idea_ledger as IL  # noqa: E402

OUT = ROOT / "data/processed/H62-ideas-travel-reply-graph"
SH = ROOT / "data/processed/shared"


def gt(goal: int, kind: str) -> pl.DataFrame:
    g = pl.read_parquet(SH / "ground_truth_labels.parquet")
    return g.filter((pl.col("goal_no") == goal) & (pl.col("label_kind") == kind) & pl.col("preferred") & ~pl.col("holdout"))


def f(x, d=2):
    return "–" if x is None or x != x else f"{x:.{d}f}"


def native_g51(rows: dict) -> dict:
    r = rows[51]
    others = [v for g, v in rows.items() if g != 51 and v["regime"] == "III" and v.get("eligible")]
    med_lam = float(np.median([v["Lam"] for v in others]))
    t_room_min = min(v["T_room"] for v in others)
    t_rep = [v["T_rep"] for v in others]
    a = r["Lam"] >= 2 and r.get("Lam_lo", 0) > 1 and r["Lam"] > med_lam
    b = r["T_room"] < t_room_min and min(t_rep) <= r["T_rep"] <= max(t_rep)
    v = "supported" if a and b else ("failed" if not a and not b else "mixed")
    text = ("*Run 2026-10-04 after the prediction above.* Other eligible regime-III periods: "
            + ", ".join(f"G{g:02d}" for g, x in rows.items() if x in others) + ".\n\n"
            "| Prediction | Observed | Verdict |\n| --- | --- | --- |\n"
            f"| N51-a Λ ≥ 2, CI > 1, above the regime-III median | Λ = {f(r['Lam'])} [{f(r.get('Lam_lo'))}, {f(r.get('Lam_hi'))}]; "
            f"other regime-III median {f(med_lam)} | {'pass' if a else 'fail'} |\n"
            f"| N51-b T_room lowest of regime III; T_rep inside their range | T_room {f(r['T_room'], 3)} (others' min {f(t_room_min, 3)}); "
            f"T_rep {f(r['T_rep'], 3)} (others {f(min(t_rep), 3)}–{f(max(t_rep), 3)}) | {'pass' if b else 'fail'} |\n\n"
            f"**Native verdict: {v}.**\n")
    return dict(verdict=v, text=text, Lam=r["Lam"], med_lam_III=med_lam, T_room=r["T_room"], T_rep=r["T_rep"])


def native_ne42(rows: dict, base: IL.Base) -> dict:
    T = {g: (rows[g]["T_room"], rows[g]["T_rep"], rows[g].get("T_ratio")) for g in (39, 40, 41)}
    a = T[40][0] < T[39][0] and T[40][0] < T[41][0]
    ref = (T[39][1] + T[41][1]) / 2
    b = abs(T[40][1] - ref) <= 0.3 * ref
    ra = gt(39, "room_assignment")
    room39 = {int(x["agent"]): x["value"] for x in ra.to_dicts()}
    P = IL.load_period(base, 40)
    grp = lambda k, j, t: int(room39.get(k) is not None and room39.get(j) is not None and room39[k] != room39[j])  # noqa: E731
    r = C.assemble(P, group=grp, ng=2)
    (OUT / "NE42").mkdir(parents=True, exist_ok=True)
    r["events"].write_parquet(OUT / "NE42/events_g40_cross.parquet")
    r["cells"].write_parquet(OUT / "NE42/cells_g40_cross.parquet")
    ev = r["events"].filter(pl.col("grp") == 1)
    tc = L.transmissibility(ev, "chan", B=1000, seed=42)
    c = (tc.get("T_ratio") or 0) >= 2
    v = "supported" if a and b else ("failed" if not a and not b else "mixed")
    text = ("*Run 2026-10-04 after the prediction above.*\n\n"
            "| Prediction | Observed | Verdict |\n| --- | --- | --- |\n"
            f"| N42-a T_room(#40) below #39 and #41 | T_room #39 {f(T[39][0], 3)}, #40 {f(T[40][0], 3)}, #41 {f(T[41][0], 3)} | {'pass' if a else 'fail'} |\n"
            f"| N42-b T_rep(#40) within ±30% of the #39/#41 mean | T_rep #39 {f(T[39][1], 3)}, #40 {f(T[40][1], 3)}, #41 {f(T[41][1], 3)} "
            f"(mean of #39/#41 {f(ref, 3)}) | {'pass' if b else 'fail'} |\n"
            f"| N42-c #40 cross-group pairs: T_rep / T_room ≥ 2 | {f(tc.get('T_ratio'))} [{f(tc.get('T_ratio_lo'))}, {f(tc.get('T_ratio_hi'))}]; "
            f"T_rep {f(tc.get('T_rep'), 3)} ({tc.get('n_rep')} events), T_room {f(tc.get('T_room'), 3)} ({tc.get('n_room')}) | {'pass' if c else 'fail'} |\n\n"
            f"T_rep / T_room by week: #39 {f(T[39][2])}, #40 {f(T[40][2])}, #41 {f(T[41][2])}. **Native verdict: {v}.**\n")
    return dict(verdict=v, text=text, T=T, cross=tc)


def native_g12(base: IL.Base) -> dict:
    tm = gt(12, "team")
    spans = []
    for x in tm.to_dicts():
        spans.append((int(x["agent"]), x["value"], int(x["t_valid_from"].timestamp() * 1e6), int(x["t_valid_to"].timestamp() * 1e6)))

    def team(a, t):
        for ag, v, lo, hi in spans:
            if ag == a and lo <= t < hi and v in ("gov", "opp"):
                return v
        return None

    def grp(k, j, t):
        tk, tj = team(k, t), team(j, t)
        if tk is None or tj is None:
            return 0
        return 2 if tk == tj else 1

    P = IL.load_period(base, 12)
    r = C.assemble(P, group=grp, ng=3)
    (OUT / "G12").mkdir(parents=True, exist_ok=True)
    r["cells"].write_parquet(OUT / "G12/cells_teams.parquet")
    r["events"].write_parquet(OUT / "G12/events_teams.parquet")
    terms = ["rec_rep_g0", "rec_room_g0", "rec_rep_g1", "rec_room_g1", "rec_rep_g2", "rec_room_g2", "rec_hum"]
    h = L.hr_fit(r["cells"], terms, B=200, seed=12, contrasts={"repX_vs_roomS": ("rec_rep_g1", "rec_room_g2")})
    ev = r["events"].filter(pl.col("grp") == 1)
    tc = L.transmissibility(ev, "chan", B=1000, seed=12)
    small = min(h.get("adopt_rec_rep_g1", 0), h.get("adopt_rec_room_g2", 0)) < 10
    a = h.get("repX_vs_roomS", 0) >= 1
    b = (tc.get("T_ratio") or 0) > 1
    v = "descriptive" if small else ("supported" if a and b else ("failed" if not a and not b else "mixed"))
    text = ("*Run 2026-10-04 after the prediction above.* Teams from DQ6 (`team`, gov / opp; bench and out-of-debate "
            "times form group 0).\n\n"
            "| Prediction | Observed | Verdict |\n| --- | --- | --- |\n"
            f"| N12-a HR(reply, cross-team) ≥ HR(room-only, same team) | HR reply cross {f(h.get('hr_rec_rep_g1'))} "
            f"({h.get('adopt_rec_rep_g1')} adoptions); HR room-only same {f(h.get('hr_rec_room_g2'))} ({h.get('adopt_rec_room_g2')}); "
            f"ratio {f(h.get('repX_vs_roomS'))} [{f(h.get('repX_vs_roomS_lo'))}, {f(h.get('repX_vs_roomS_hi'))}] | {'pass' if a else 'fail'} |\n"
            f"| N12-b T_rep,cross > T_room,cross | {f(tc.get('T_rep'), 3)} ({tc.get('n_rep')} events) vs {f(tc.get('T_room'), 3)} "
            f"({tc.get('n_room')}); ratio {f(tc.get('T_ratio'))} [{f(tc.get('T_ratio_lo'))}, {f(tc.get('T_ratio_hi'))}] | {'pass' if b else 'fail'} |\n\n"
            f"Other cells: HR reply same-team {f(h.get('hr_rec_rep_g2'))} ({h.get('adopt_rec_rep_g2')}), room-only cross-team "
            f"{f(h.get('hr_rec_room_g1'))} ({h.get('adopt_rec_room_g1')}), outside debates reply {f(h.get('hr_rec_rep_g0'))} "
            f"({h.get('adopt_rec_rep_g0')}) / room-only {f(h.get('hr_rec_room_g0'))} ({h.get('adopt_rec_room_g0')}). **Native verdict: {v}.**\n")
    return dict(verdict=v, text=text, hr=h, cross=tc)


def main():
    rows = {r["goal"]: r for r in json.loads((OUT / "results/periods.json").read_text())}
    base = IL.Base()
    res = {"G51": native_g51(rows), "NE42": native_ne42(rows, base), "G12": native_g12(base)}
    (OUT / "results/natives.json").write_text(json.dumps(res, indent=1, default=float))
    for k, v in res.items():
        print(k, v["verdict"])
        print(v["text"])


if __name__ == "__main__":
    main()
