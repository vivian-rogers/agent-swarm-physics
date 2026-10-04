"""H28 round 1b assembly (2026-10-04): round 1 vs ledger visibility vs work switches, per period and pooled.

  uv run python hypotheses/H28-links-spread-herding/analysis/r1b_assemble.py [table|estimates|readmes]

Reads G<NN>/round1.json (round 1) and r1b/G<NN>/round1b.json, round1b_work.json; writes r1b/cross_period_r1b.json.
Pooling: DerSimonian-Laird over per-period estimates (named exception d, as in round 1).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
from assemble import dl  # noqa: E402
from h28lib import ALL_PERIODS, CONTRAST, OUT, PERIOD_DIR, gname  # noqa: E402
from period_folders import verdict  # noqa: E402

R1B = OUT / "r1b"


def load(kind):
    out = {}
    for g in ALL_PERIODS:
        p = (OUT / gname(g) / "round1.json") if kind == "r1" else (R1B / gname(g) / f"round1b{'_work' if kind == 'work' else ''}.json")
        if p.exists():
            out[g] = json.loads(p.read_text())
    return out


def row(r):
    return dict(kappa=r["kappa"], se=r["se"], p=r["p"], z=r["z_shift"], lead=r["lead"]["lead"]["b"], se_lead=r["lead"]["lead"]["se"],
                diff=r["lead"]["diff"]["d"], se_diff=r["lead"]["diff"].get("se", np.nan), p_diff=r["lead"]["diff"]["p"],
                lam=r["attr"]["lam"], R=r["attr"]["R_link"], arrivals=r["arrivals"], tested=r["tested"], verdict=verdict(r),
                naive=r["naive"]["b"], se_naive=r["naive"]["se"], f0=r.get("cf_summary", {}).get("f0", {}).get("peak_occ", np.nan),
                es_pre=r["event_study"]["pre"]["O"] / r["event_study"]["pre"]["E"] if r["event_study"]["pre"]["E"] > 0 else np.nan,
                n_shift=r["null"]["n"])


def table():
    r1, led, wk = load("r1"), load("led"), load("work")
    herd = [g for g in ALL_PERIODS if g not in CONTRAST]
    out = {"periods": {}}
    for g in ALL_PERIODS:
        out["periods"][g] = {"r1": row(r1[g]) if g in r1 else None, "ledger": row(led[g]) if g in led else None,
                             "work": row(wk[g]) if g in wk else None}
    for lab, src in (("r1", r1), ("ledger", led), ("work", wk)):
        T = [row(src[g]) for g in herd if g in src and src[g]["tested"]]
        C = [row(src[g]) for g in CONTRAST if g in src and src[g]["tested"]]
        if not T:
            continue
        out[lab] = dict(n_tested=len(T), counts={v: sum(t["verdict"] == v for t in T) for v in ("supported", "weak", "failed")},
                        pooled_kappa=dl([t["kappa"] for t in T], [t["se"] for t in T]),
                        pooled_diff=dl([t["diff"] for t in T], [t["se_diff"] for t in T]),
                        lead_ge_lag=sum(t["lead"] >= t["kappa"] for t in T),
                        p_lt05=sum(t["p"] < 0.05 and t["kappa"] > 0 for t in T), z_ge2=sum(t["z"] >= 2 for t in T),
                        lam_median=float(np.median([t["lam"] for t in T])), R_median=float(np.median([t["R"] for t in T])),
                        R_max=float(np.max([t["R"] for t in T])), f0_median=float(np.nanmedian([t["f0"] for t in T])),
                        naive_pooled=dl([t["naive"] for t in T], [t["se_naive"] for t in T]),
                        contrast=dict(pooled_diff=dl([t["diff"] for t in C], [t["se_diff"] for t in C]),
                                      counts={v: sum(t["verdict"] == v for t in C) for v in ("supported", "weak", "failed")}) if C else None,
                        periods=[g for g in herd if g in src and src[g]["tested"]])
    (R1B / "cross_period_r1b.json").write_text(json.dumps(out, indent=1, default=float))
    for g in ALL_PERIODS:
        p = out["periods"][g]
        f = lambda x: "—" if x is None else f"{x['kappa']:+.2f}±{x['se']:.2f} z{x['z']:+.1f} lead{x['lead']:+.2f} {x['verdict']} n{x['arrivals']}"
        print(g, "| r1", f(p["r1"]), "| led", f(p["ledger"]), "| work", f(p["work"]))
    for lab in ("r1", "ledger", "work"):
        if lab in out:
            o = out[lab]
            print(lab, o["counts"], "pooled k", round(o["pooled_kappa"]["b"], 3), round(o["pooled_kappa"]["se"], 3), "diff",
                  round(o["pooled_diff"]["b"], 3), round(o["pooled_diff"]["se"], 3), "lead>=lag", o["lead_ge_lag"], "/", o["n_tested"],
                  "lam", round(o["lam_median"], 3), "R", round(o["R_median"], 3), "f0", o["f0_median"])
    return out


def estimates():
    sys.path.insert(0, str(OUT.parents[2] / "infra/shared"))
    from estimates import map_unit, write_estimates
    rows = []
    for lab, src, meth in (("ledger", load("led"), "H28.r1b_ledger"), ("work", load("work"), "H28.r1b_work")):
        for g, r in src.items():
            days = [d["pt_date"] for d in json.loads((OUT / gname(g) / "meta.json").read_text())["days"]]
            base = dict(goal_no=g, period_unit=map_unit(g, days[0], days[-1]) or f"G{g:02d}", first_day=days[0], last_day=days[-1],
                        role="replication", method=meth, channel="attention" if lab == "ledger" else "work",
                        n=float(r["arrivals"]), n_kind="switches", source=f"data/processed/H28-links-spread-herding/r1b/{gname(g)}")
            k, se = r["kappa"], r["se"]
            rows.append({**base, "statistic": "kappa_link60", "estimate": k, "se": se, "ci_lo": k - 1.96 * se, "ci_hi": k + 1.96 * se,
                         "ci_kind": "se_z", "null": "link time-shift (z in notes)", "notes": f"z_shift {r['z_shift']:.2f}"})
            d, sd = r["lead"]["diff"]["d"], r["lead"]["diff"].get("se", np.nan)
            rows.append({**base, "statistic": "kappa_minus_lead", "estimate": d, "se": sd, "ci_lo": d - 1.96 * sd, "ci_hi": d + 1.96 * sd,
                         "ci_kind": "se_z"})
            if lab == "ledger":
                a = r["attr"]
                lo, hi = a.get("R_ci", [None, None])
                rows.append({**base, "statistic": "R_link", "estimate": a["R_link"], "ci_lo": lo, "ci_hi": hi,
                             "ci_kind": "percentile" if lo is not None else "none"})
    nb = json.loads((R1B / "ne09_blind.json").read_text())
    for g, v in nb["periods"].items():
        g = int(g)
        days = [d["pt_date"] for d in json.loads((OUT / gname(g) / "meta.json").read_text())["days"]]
        rows.append(dict(goal_no=g, period_unit=map_unit(g, days[0], days[-1]) or f"G{g:02d}", first_day=days[0], last_day=days[-1],
                         role="native", method="H28.r1b_blind_window", channel="attention", statistic="E_blind",
                         estimate=v["E_blind"], ci_kind="none", n=float(v["pairs"]), n_kind="link-recipient pairs",
                         null="link time-shift baseline", notes=f"E_read {v['E_read']:.2f}; median delay {v['median_delay_s']:.0f} s",
                         source="data/processed/H28-links-spread-herding/r1b/ne09_blind.json"))
    write_estimates(rows, "H28")
    print(len(rows), "rows")


def readmes():
    led, wk = load("led"), load("work")
    for g in ALL_PERIODS:
        f = PERIOD_DIR / gname(g) / "README.md"
        if not f.exists() or g not in led:
            continue
        r = row(led[g])
        line = (f"**Verdict (1b):** {'mixed' if r['verdict'] == 'weak' else r['verdict']} (ledger visibility: κ {r['kappa']:+.2f} ± {r['se']:.2f}, "
                f"z_shift {r['z']:+.1f}, κ_lead {r['lead']:+.2f}")
        if g in wk:
            w = row(wk[g])
            line += f"; work switches κ {w['kappa']:+.2f} ± {w['se']:.2f}, z {w['z']:+.1f}, lead {w['lead']:+.2f}"
        line += ")"
        s = f.read_text()
        if "**Role:** native" in s:      # native folders carry their own 1b verdict line
            continue
        s = re.sub(r"\*\*Verdict \(1b\):\*\*[^\n]*\n", "", s)
        s = re.sub(r"(\*\*Verdict:\*\*[^\n]*\n)", lambda m: m.group(1) + line + "\n", s, count=1)
        f.write_text(s)
    print("readmes ok")


if __name__ == "__main__":
    {"table": table, "estimates": estimates, "readmes": readmes}[sys.argv[1] if len(sys.argv) > 1 else "table"]()
