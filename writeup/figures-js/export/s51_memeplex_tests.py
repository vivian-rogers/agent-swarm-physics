"""Paper 2, Sec. results: the 15 memeplexes of goal period 51 against the five conditions of the definition
(Fig. fig:tests). One row per memeplex (H145's frozen K01-K15), five columns:
  renew  : H145 P2 (A4), D_K(5) minus the 95th percentile of 200 frequency-matched pseudo-patterns;
  A_z    : H145 P3a, colonial A excess z over pseudo-patterns at 2 h with E = e1-e4;
  wipe   : H146 P4, hazard ratio of re-expression after a forced wipe vs a placebo call (calls 1-20), with 30 pseudo values;
  repair : H146 P5, rate ratio of named K messages from other hosts in the 2 h after a wipe vs placebo, with 30 pseudo values;
  cost   : H147 A2, hosting effect on the host's own-repo commits at matched activity, with the pseudo-pattern 2.5-97.5% band.

    uv run python writeup/figures-js/export/s51_memeplex_tests.py

Inputs are the cards' result files (exploration days only; the cards assert 51m absent). Every number printed in the
paper's results section is asserted here against the cards' Round 1 tables.
"""
from __future__ import annotations

import json
import math

from common import ROOT, write

H145 = ROOT / "data/processed/H145-ideology-egregores-51"
H146 = ROOT / "data/processed/H146-egregore-recruitment-behaviors-51/results/real_h145.json"
H147 = ROOT / "data/processed/H147-egregore-value-and-hosts-51/results"

LABEL = {"verify": "check and correct", "governance": "governance", "echoes": "serial novel", "frameworks": "frameworks",
         "welfare": "AI welfare", "unlabelled": "", "": ""}


def main():
    t = json.load(open(H145 / "results/tests.json"))
    h146 = json.load(open(H146))["patterns"]
    rows = []
    for m in t["memeplexes"]:
        k = m["id"]
        s = h146[k]["stats"]
        ps = h146[k]["pseudo"]["values"]
        h7 = json.load(open(H147 / f"pattern_{k}.json"))
        a2 = h7["host"]["A2"]
        br = h7["wipe"]["b_rate"]
        dV = math.exp(br["excess"]) - 1.0
        rows.append(dict(
            id=k, label=LABEL.get(m.get("candidate") or "", m.get("candidate") or ""), n_el=m["n_el"], h_K=m["h_K"],
            n_hosts=h146[k]["meta"]["n_hosts"], labs=len(h146[k]["meta"]["labs"]),
            renew=m["P2"]["D"]["obs"] - m["P2"]["D"]["thr"], renew_pass=bool(m["P2"]["pass"]),
            A_z=m["P3"]["A_z"], A_pass=bool(m["P2"]["pass"] and m["P3"]["A_z"] >= 2),
            A_excess=m["P3"]["A_excess"],
            wipe=s["P4"]["HR_F_vs_P"], wipe_ci=s["P4"]["ci"], wipe_pseudo=[v for v in ps["P4_HR"] if isinstance(v, float) and math.isfinite(v)],
            repair=s["P5"]["wipe"]["rr"], repair_ci=s["P5"]["wipe"]["ci"], repair_pseudo=[v for v in ps["P5_wipe"] if isinstance(v, float) and math.isfinite(v)],
            cost=a2["est"]["commits"], cost_ci=a2["ci"]["commits"], cost_band=a2["pseudo_q"]["commits"],
            cost_class=a2["class_exc"],
            dV=dV, dV_ci=[math.exp(min(v, 50.0)) - 1 for v in br["comb"]],
        ))
    rows.sort(key=lambda r: r["id"])
    # --- checks against the cards' Round 1 tables
    k03 = next(r for r in rows if r["id"] == "K03")
    assert round(k03["A_z"], 2) == 2.96 and round(k03["A_excess"], 2) == 0.20, k03   # H145: K03 z 2.96, excess 0.20
    assert [r["id"] for r in rows if r["renew_pass"]] == ["K03", "K07", "K14"]          # H145 P2 (A4): 3 of 15
    assert [r["id"] for r in rows if r["A_pass"]] == ["K03"]                           # H145 P3a: K03 only
    hr = sorted(r["wipe"] for r in rows if r["id"] != "K14")
    assert round((hr[6] + hr[7]) / 2, 2) == 0.90 and round(min(hr), 2) == 0.78 and round(max(hr), 2) == 1.11, hr  # H146 P4
    assert max(r["repair"] for r in rows if r["id"] != "K14") <= 1.07 + 1e-9                                   # H146 P5
    assert [r["id"] for r in rows if r["cost_class"] == "parasitic"] == ["K02", "K03", "K14"]                   # H147 P4 beyond pseudo
    assert [r["id"] for r in rows if r["cost_class"] == "mutualist"] == ["K09"]
    dist = sorted(r["dV"] for r in rows if r["id"] != "K14")
    med_dV = (dist[6] + dist[7]) / 2
    print("median dV over 14 distributed:", round(med_dV, 3), "(card: +0.05)")
    assert abs(med_dV - 0.05) < 0.02, med_dV
    p1 = json.load(open(H145 / "results/p1.json"))
    assert p1["obs_hub_free"] == 15 and p1["null_q95"] == 6
    null_mean = sum(p1["null_counts"]) / len(p1["null_counts"])
    print(f"{len(rows)} memeplexes; discovery null mean {null_mean:.1f}, 95th pct {p1['null_q95']:.0f}")
    pseudo_hr = [v for r in rows for v in r["wipe_pseudo"] if isinstance(v, float) and math.isfinite(v)]
    pseudo_hr.sort()
    print("pseudo HR median", round(pseudo_hr[len(pseudo_hr) // 2], 2), "(card: 0.89)")
    write("s51_memeplex_tests", dict(rows=rows, discovery=dict(n=15, null_mean=null_mean, null_q95=p1["null_q95"]),
                                     thresholds=dict(A_z=2.0, wipe_kill=0.5, wipe_ok=0.8, repair=1.2)),
          "writeup/figures-js/export/s51_memeplex_tests.py",
          ["data/processed/H145-ideology-egregores-51/results/tests.json",
           "data/processed/H145-ideology-egregores-51/results/p1.json",
           "data/processed/H146-egregore-recruitment-behaviors-51/results/real_h145.json",
           "data/processed/H147-egregore-value-and-hosts-51/results/pattern_K*.json"],
          dict(bins="2 h", span="2026-07-06..09-04"))


if __name__ == "__main__":
    main()
