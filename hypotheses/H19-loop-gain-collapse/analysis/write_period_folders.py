"""Write the H19 goal-period folders (hypotheses/H19-loop-gain-collapse/G<NN>/README.md).

  --predict   write each period's README with its dated prediction (verdict pending), BEFORE the real-data fit
  --results   fill Verdict, Result and Scorecard from data/processed/H19-loop-gain-collapse/results/explore.json,
              keeping the prediction text (and its timestamp) exactly as written

Usage: uv run python hypotheses/H19-loop-gain-collapse/analysis/write_period_folders.py --predict|--results
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h19common as C  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

PRIMARY_X = "x_att_village"
LABEL = {"H19.geq_active": "g_eq active (E1, primary)", "H19.geq_talk": "g_eq talk (E2)", "H04.K_week": "H04 K, weekly (E3)",
         "H05.g2b_talk": "H05 two-block g, talk (E4)", "H05.g2b_active": "H05 two-block g, active (E5)",
         "H03.n_talk": "H03 n̂ TALK (T1, primary)", "H03.n_all": "H03 n̂ ALL (T2)", "H03.nx_fast": "H03 fast n_x (T3)",
         "H04.n_week": "H04 n, weekly (T4)", "H02.gcw_active": "H02 βJ₀q (validation of E1)"}
NOTES = {
    2: "Two weekend days, 'unsupervised'; the profile CI is used for n̂.",
    35: "First period with rooms (#best/#rest split on 03-16); regime II.",
    36: "Straddles the 03-24 perma-computer-use switch (1 day II, 4 days III); coded III by majority.",
    37: "Three days, free mode, first regime-III week.",
    38: "Longest exploratory regime-III period (17 days, 4 step changes inside per H03).",
    40: "#best and #rest merged into one room for the week (05-04).",
    44: "Room-specific goals (#best fine-tunes a leader; #rest picks its own).",
    51: "Only 8 h/day exploratory period; 45 non-holdout days (the 09-07 → 09-21 tail is held out); N grows 21 → 32.",
}


def titles() -> dict:
    txt = (C.ROOT / "hypotheses/hypohypotheses/goal-periods.md").read_text()
    return {int(m.group(1)): m.group(2).strip() for m in re.finditer(r"^### (\d+) · (.+)$", txt, re.M)}


def head(g, ctr, t):
    c = ctr
    return (f"# H19 × {C.pname(g)}: {t.get(g, '')} ({c['first_day']} → {c['last_day']})\n\n")


def period_line(c):
    return (f"**Period:** regime {c['regime']}{' (mixed)' if c['regime_mixed'] else ''} · mode {c['mode']} · "
            f"{c['N_roster']:.1f} agents (N_room {c['N_room']:.1f}) · {c['n_rooms']} room(s) carrying ≥ 5% of agent messages · "
            f"{c['n_days']} non-holdout days · {c['hours_emp']:.1f} h/day (empirical).")


def predict():
    ctr = pl.read_parquet(C.OUT / "controls.parquet")
    est = pl.read_parquet(C.OUT / "estimates.parquet")
    t = titles()
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    xs = ctr[PRIMARY_X].to_numpy()
    med = float(np.median(xs))
    for c in ctr.iter_rows(named=True):
        g = c["goal_no"]
        rank = int((xs < c[PRIMARY_X]).sum()) + 1
        meths = est.filter((pl.col("goal_no") == g) & ~pl.col("validation_only"))["method"].to_list()
        side = "above" if c[PRIMARY_X] > med else "below"
        d = C.HYP / C.pname(g)
        (d / "figures").mkdir(parents=True, exist_ok=True)
        txt = head(g, c, t) + "**Verdict:** pending\n**Role:** exploratory (round 1, non-holdout)\n" + period_line(c) + "\n\n"
        txt += "## Why this period\n"
        txt += (f"One point on every method's curve. Loop-gain estimates available here: {', '.join(LABEL.get(m, m) for m in meths)}. "
                f"Controls: x_att = {c[PRIMARY_X]:.2f} (rank {rank}/35), messages per village turn {c['m_turn_village']:.2f}, "
                f"attention load k̄ = {c['k_village']:.1f} agent messages waiting per turn, {c['m_hour']:.1f} agent messages per agent-hour, "
                f"human share of chat {100 * c['human_share']:.1f}%.")
        if g in NOTES:
            txt += " " + NOTES[g]
        txt += "\n\n## Prediction\n"
        txt += f"*Written {now}, before H19 related any control parameter to any loop gain (the card's P1 applied here).*\n"
        txt += (f"- Under the attention-dilution collapse (P1), every loop gain is affine-increasing in x_att. This period's "
                f"x_att = {c[PRIMARY_X]:.2f} is **{side}** the cross-period median ({med:.2f}), so its estimates should sit "
                f"**{side}** each method's cross-period median, and on the common curve.\n")
        txt += ("- **Per-period verdict rule** (fixed now): fit the primary collapse model (per-method affine in x_att) "
                "without this period (LOPO). **supported** if (i) both primary estimates (T1 n̂ TALK, E1 g_eq active) fall "
                "inside their 90% LOPO predictive intervals and (ii) the period's summed LOPO log density under the collapse "
                "model is ≥ that under the regime-only rival N1; **mixed** if exactly one of (i), (ii) holds; **failed** if neither.\n")
        txt += "- Against it: estimates outside the intervals in the direction opposite to the x_att prediction, or N1 predicting the period better.\n\n"
        txt += "## Result\n*Pending.*\n\n## Scorecard (period-specific axes)\n*Pending.*\n\n## Notes\n"
        txt += f"- Inputs: `data/processed/H19-loop-gain-collapse/{C.pname(g)}/inputs.json`.\n"
        (d / "README.md").write_text(txt)
    print(f"wrote {ctr.height} period folders (predictions dated {now})")


def results():
    R = json.loads((C.OUT / "results/explore.json").read_text())
    per = R["per_period"]
    ctr = pl.read_parquet(C.OUT / "controls.parquet")
    for c in ctr.iter_rows(named=True):
        g = c["goal_no"]; P = C.pname(g)
        f = C.HYP / P / "README.md"
        txt = f.read_text()
        pp = per[P]
        txt = re.sub(r"^\*\*Verdict:\*\* .*$", f"**Verdict:** {pp['verdict']}", txt, count=1, flags=re.M)
        res = ["## Result",
               f"Primary collapse model (per-method affine in x_att), fitted without {P} (LOPO); shrunken = partial-pooling "
               "(BLUP) estimate under the collapse model fitted to all periods, shown beside the period's own estimate.", "",
               "| Method | Own estimate ± SE | LOPO prediction [90% PI] | z | inside | Shrunken | Regime-only N1 prediction |",
               "| --- | --- | --- | --- | --- | --- | --- |"]
        for m, r in pp["methods"].items():
            pi = f"{r['mu']:.3f} [{r['lo90']:.3f}, {r['hi90']:.3f}]" if r.get("mu") is not None else "n/a"
            z = f"{r['z']:+.2f}" if r.get("z") is not None else "n/a"
            ins = ("yes" if r["inside"] else "**no**") if r.get("inside") is not None else "n/a"
            sh = f"{r['shrunk']:.3f}" if r.get("shrunk") is not None else "n/a"
            n1 = f"{r['mu_regime']:.3f}" if r.get("mu_regime") is not None else "n/a"
            res.append(f"| {LABEL.get(m, m)} | {r['y']:.3f} ± {r['s']:.3f} | {pi} | {z} | {ins} | {sh} | {n1} |")
        res += ["", f"- (i) both primaries inside their 90% intervals: **{pp['cond_i']}**; (ii) summed LOPO log density, "
                f"collapse {pp['lpd_x']:.2f} vs regime-only {pp['lpd_regime']:.2f}: **{pp['cond_ii']}**.",
                f"- Direction check (prediction: {pp['predicted_side']} median): primaries observed "
                f"{', '.join(f'{k} {v}' for k, v in pp['observed_side'].items())}.",
                f"- Per-period figure: `figures/{P}_residuals.png`. Data: `data/processed/H19-loop-gain-collapse/{P}/residuals.parquet`.", ""]
        sc = ["## Scorecard (period-specific axes)",
              f"- **C** (adequacy vs. rivals, this period): collapse vs. regime-only log density {pp['lpd_x'] - pp['lpd_regime']:+.2f} nats.",
              f"- **D** (unfitted): the period's estimates are predicted out of sample (LOPO), not fitted.",
              "- E, G: not informed by a single period.", ""]
        txt = re.sub(r"## Result\n.*?(?=## Notes)", "\n".join(res) + "\n" + "\n".join(sc) + "\n", txt, count=1, flags=re.S)
        f.write_text(txt)
    print("filled results in", ctr.height, "period folders")


if __name__ == "__main__":
    if "--predict" in sys.argv:
        predict()
    elif "--results" in sys.argv:
        results()
    else:
        print(__doc__)
