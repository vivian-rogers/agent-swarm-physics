"""H83 period-native tests (non-holdout only): N1 NE32 (G51), N2 two rooms (G38), N3 kickoff-matched start (G10).

  uv run python hypotheses/H83-enculturation-of-newcomers/analysis/natives.py
Output: data/processed/H83-enculturation-of-newcomers/natives/natives.json
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h83lib as L  # noqa: E402

OUTD = L.DATA / "natives"
B = 5000


def ne32(ad, vill, days, newc, doses, rep):
    others = [(int(a), jd) for a, jd, jh in newc.select("agent", "join_day", "join_holdout").iter_rows()
              if jd and not jh and a not in (35, 36, 37) and str(a) in rep["joins"]]
    s = L.ne32_stats(ad, vill, days, others=others)
    iso = doses.filter(pl.col("agent").is_in([35, 36, 37]) & (pl.col("pt_date") == "2026-07-09"))
    s["isolated_day_veteran_items"] = int(iso["items_vet"].sum()) if iso.height else 0
    s["isolated_day_agent_items"] = int(iso["items_agent"].sum()) if iso.height else 0
    rng = np.random.default_rng(32)
    o1 = np.array(s.pop("o1")); oc = np.array(s.pop("oc"))
    d1b = s["G1_triplet"] - o1[rng.integers(0, len(o1), (B, len(o1)))].mean(1)
    d2b = (s["Gpost_triplet"] - s["G1_triplet"]) - oc[rng.integers(0, len(oc), (B, len(oc)))].mean(1)
    s["d1_ci"] = [float(np.quantile(d1b, .025)), float(np.quantile(d1b, .975))]
    s["d2_ci"] = [float(np.quantile(d2b, .025)), float(np.quantile(d2b, .975))]
    # per-agent day-1 gaps of the triplet (descriptive)
    s["G1_each"] = {int(a): (L.day_gap(ad, vill, [a], "2026-07-09") or (None, 0)) for a in (35, 36, 37)}
    p1 = s["d1"] < 0 and s["d1_ci"][1] < 0
    p2 = s["d2"] > 0 and s["d2_ci"][0] > 0
    s["verdict"] = "supported" if (p1 and p2) else ("failed" if (s["d1"] >= 0 and s["d2"] <= 0) else
                                                    ("mixed" if (p1 or p2) else "inconclusive"))
    return s


def g38_rooms(ad, days):
    rv = L.room_villages(ad)
    use = [d for d in ["2026-04-20", "2026-04-21", "2026-04-22", "2026-04-23", "2026-04-24"]
           if sum(1 for r in rv if d in rv[r] and rv[r][d][1] >= 2) >= 2]
    newrows, vetrows = [], []
    for d in use:
        for k in ad.by_day[d]:
            R = L.room_R(ad, rv, k)
            if R is None:
                continue
            a = int(ad.agent[k])
            if a in (24, 25):
                newrows.append((a, d, R, int(ad.n[k])))
            elif ad.vet[k]:
                vetrows.append((a, d, R, int(ad.n[k])))
    if not newrows:
        return {"verdict": "n/a", "days": use}
    rng = np.random.default_rng(38)
    Rn = np.array([x[2] for x in newrows]); Rv = np.array([x[2] for x in vetrows])
    bs = Rn[rng.integers(0, len(Rn), (B, len(Rn)))].mean(1)
    out = {"days": use, "R_new": float(Rn.mean()), "R_new_ci": [float(np.quantile(bs, .025)), float(np.quantile(bs, .975))],
           "n_new_agent_days": len(Rn), "R_new_each": {f"{a}:{d}": float(r) for a, d, r, n in newrows},
           "n_stmts_new": {str(a): int(sum(n for b, _, _, n in newrows if b == a)) for a in (24, 25)},
           "R_vet": float(Rv.mean()) if len(Rv) else None, "n_vet_agent_days": len(Rv)}
    out["ratio_new_vet"] = out["R_new"] / out["R_vet"] if out["R_vet"] else None
    out["verdict"] = "supported" if out["R_new_ci"][0] > 0 else ("failed" if out["R_new"] <= 0 else "inconclusive")
    return out


def ne27(ad, vill, days, rep):
    jd = "2025-08-18"
    Ed = L.window_days(jd, days, *L.E_WIN)
    rows = []
    for a in (9, 10, 11):
        for d in Ed:
            g = L.day_gap(ad, vill, [a], d)
            if g is not None:
                rows.append((a, d, g[0]))
    gaps = np.array([x[2] for x in rows])
    rng = np.random.default_rng(27)
    bs = gaps[rng.integers(0, len(gaps), (B, len(gaps)))].mean(1)
    dG = [rep["joins"][str(a)]["G"]["delta"] for a in (9, 10, 11) if str(a) in rep["joins"]]
    out = {"E_days": Ed, "gap_E": float(gaps.mean()), "gap_E_ci": [float(np.quantile(bs, .025)), float(np.quantile(bs, .975))],
           "n_agent_days": len(rows), "gap_E_each": {f"{a}:{d}": float(g) for a, d, g in rows},
           "dG_batch": float(np.mean(dG)) if dG else None, "dG_each": dG}
    p1 = out["gap_E_ci"][1] < 0
    p2 = out["dG_batch"] is not None and out["dG_batch"] > 0
    out["verdict"] = "supported" if (p1 and p2) else ("failed" if out["gap_E"] >= 0 else ("mixed" if (p1 or p2) else
                                                                                         "inconclusive"))
    return out


def ne32_ph2(st, X, ad, vill):
    """Post hoc PH2 (after the ledger showed the triplet left its isolated rooms on 07-09 itself, ~1.5-2 h after
    joining): statement-level cosine with the veterans' 07-09 centroid, isolated-room statements (rooms 10-12)
    vs #general statements of the same agents on the same day."""
    d = "2026-07-09"
    m = (st["pt_date"] == d) & st["agent"].is_in([35, 36, 37])
    sub = st.with_row_index("i").filter(m)
    if d not in vill:
        return None
    V = L.unit(vill[d][0] / vill[d][1])
    c = X[sub["i"].to_numpy()] @ V
    iso = sub["room"].is_in([10, 11, 12]).to_numpy()
    if iso.sum() == 0 or (~iso).sum() == 0:
        return {"n_isolated": int(iso.sum()), "n_merged": int((~iso).sum())}
    rng = np.random.default_rng(322)
    a, b = c[iso], c[~iso]
    bs = [rng.choice(b, len(b)).mean() - rng.choice(a, len(a)).mean() for _ in range(B)]
    return {"n_isolated": int(iso.sum()), "n_merged": int((~iso).sum()),
            "n_isolated_by_agent": {str(k): int(v) for k, v in zip(*np.unique(sub["agent"].to_numpy()[iso], return_counts=True))},
            "cos_isolated": float(a.mean()), "cos_merged": float(b.mean()), "diff": float(b.mean() - a.mean()),
            "diff_ci": [float(np.quantile(bs, .025)), float(np.quantile(bs, .975))]}


def main():
    OUTD.mkdir(parents=True, exist_ok=True)
    days = L.calendar_days(); newc = L.newcomers()
    doses = pl.read_parquet(L.DATA / "doses.parquet")
    rep = json.loads((L.DATA / "replication" / "replication.json").read_text())
    out = {"run_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}
    for model in ("bge", "gte"):
        st, X, _ = L.load(model, "vec")
        ad = L.AD(st, X, None); vill = L.village(ad, "M")
        o = {"NE32": ne32(ad, vill, days, newc, doses, rep), "G38": g38_rooms(ad, days),
             "NE27": ne27(ad, vill, days, rep), "NE32_PH2": ne32_ph2(st, X, ad, vill)}
        # the premise of N1 (no veteran reads on tau 1) is false: 733 veteran items read on 07-09
        if o["NE32"]["isolated_day_veteran_items"] > 0:
            o["NE32"]["verdict_rule"] = o["NE32"]["verdict"]
            o["NE32"]["verdict"] = "n/a"
        out[model] = o
        print(model, json.dumps(o, default=float, indent=1)[:2500], flush=True)
    (OUTD / "natives.json").write_text(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
