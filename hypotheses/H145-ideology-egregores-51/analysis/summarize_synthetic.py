"""Summarize H145 synthetic validation (synthetic/disc_a.jsonl, tests_*.jsonl) into synthetic/summary.json and a
markdown table printed to stdout."""
from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h145lib as L  # noqa: E402

SYN = L.OUT / "synthetic"


def rate(x):
    x = [bool(v) for v in x]
    if not x:
        return None
    p = float(np.mean(x))
    return {"rate": round(p, 3), "n": len(x), "se": round(float(np.sqrt(p * (1 - p) / len(x))), 3)}


def main():
    out = {"disc": {}, "tests": {}}
    rows = [json.loads(l) for f in sorted(glob.glob(str(SYN / "disc_*.jsonl"))) for l in open(f)]
    print("## Discovery (2-h bins, gamma 1)\n")
    print("| world | reps | card: hub-free qual. (mean) | card: max size | card: planted Jaccard (mean) | A1: qual. (mean) | A1: planted recovered (J>=0.5, qualifies) | A1: P1 pass | null count mean (agent-scope) | null count mean (within-day) |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for w in dict.fromkeys(r["world"] for r in rows):
        rr = [r for r in rows if r["world"] == w]
        cj = [p["jaccard"] for r in rr for p in r["card"]["planted"]]
        rec = [p["jaccard"] >= 0.5 and bool(p.get("qualifies")) for r in rr for p in r["A1"]["planted"]]
        nd = [c for r in rr for c in r["A1"].get("null_counts_day", [])]
        d = {"reps": len(rr), "card_qual": float(np.mean([r["card"]["n_qualify_hub_free"] for r in rr])),
             "card_max_size": float(np.mean([r["card"]["max_size"] for r in rr])), "card_planted_J": float(np.mean(cj)),
             "A1_qual": float(np.mean([r["A1"]["n_qualify_hub_free"] for r in rr])), "A1_recovered": rate(rec),
             "A1_P1_pass": rate([r["A1"]["P1_pass"] for r in rr]),
             "null_agent_mean": float(np.mean([c for r in rr for c in r["A1"]["null_counts"]])),
             "null_day_mean": float(np.mean(nd)) if nd else None,
             "timeshuffle_identical": [r.get("timeshuffle_graph_identical") for r in rr if "timeshuffle_graph_identical" in r]}
        out["disc"][w] = d
        print(f"| {w} | {d['reps']} | {d['card_qual']:.1f} | {d['card_max_size']:.0f} | {d['card_planted_J']:.2f} | {d['A1_qual']:.1f} | "
              f"{d['A1_recovered']['rate'] if w != 'W0' else 'n/a'} | {d['A1_P1_pass']['rate']} | {d['null_agent_mean']:.2f} | "
              f"{d['null_day_mean'] if d['null_day_mean'] is None else round(d['null_day_mean'], 2)} |")
    rows = [json.loads(l) for f in sorted(glob.glob(str(SYN / "tests_*.jsonl"))) for l in open(f)]
    print("\n## P2 and P3 on the planted pattern (instrument) and on the discovered match (end-to-end)\n")
    print("| world | target | n | P2 as written pass | P2 D pass | P2 phi pass | P3 A pass (z>=2) | P3 Delta pass | P3 both | mean A z | mean Delta z |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for w in dict.fromkeys(r["world"] for r in rows):
        rr = [r for r in rows if r["world"] == w]
        for tgt in ("planted", "discovered"):
            pats = [p for r in rr for p in r["patterns"] if p["target"].startswith(tgt)]
            if tgt == "discovered":
                # end-to-end: a planted pattern counts only if recovered (J >= 0.5 and qualifies); J = 1 reuses planted
                pats = []
                for r in rr:
                    for j, rec in enumerate(r.get("recovered", [])):
                        ok = rec["jaccard"] >= 0.5 and bool(rec.get("qualifies"))
                        d = [p for p in r["patterns"] if p["target"] == f"discovered{j}"]
                        pl_ = [p for p in r["patterns"] if p["target"] == f"planted{j}"]
                        src = d[0] if d else (pl_[0] if pl_ else None)
                        pats.append(src if (ok and src) else None)
            if not pats:
                continue

            def g(p, f):
                return False if p is None else f(p)
            okP3 = [p for p in pats if p is not None and p["P3"].get("ok")]
            d = {"n": len(pats), "P2_written": rate([g(p, lambda p: p["P2"]["diff"]["pass"]) for p in pats]),
                 "P2_D": rate([g(p, lambda p: p["P2"]["D"]["pass"]) for p in pats]),
                 "P2_phi": rate([g(p, lambda p: p["P2"]["R"]["pass"]) for p in pats]),
                 "P3_A": rate([g(p, lambda p: p["P3"].get("pass_A", False)) for p in pats]),
                 "P3_D": rate([g(p, lambda p: p["P3"].get("pass_D", False)) for p in pats]),
                 "P3_both": rate([g(p, lambda p: p["P3"].get("pass_A", False) and p["P3"].get("pass_D", False)) for p in pats]),
                 "A_z": float(np.nanmean([p["P3"]["A_z"] for p in okP3])) if okP3 else None,
                 "D_z": float(np.nanmean([p["P3"]["D_z"] for p in okP3])) if okP3 else None}
            out["tests"][f"{w}|{tgt}"] = d
            print(f"| {w} | {tgt} | {d['n']} | {d['P2_written']['rate']} | {d['P2_D']['rate']} | {d['P2_phi']['rate']} | "
                  f"{d['P3_A']['rate']} | {d['P3_D']['rate']} | {d['P3_both']['rate']} | "
                  f"{'' if d['A_z'] is None else round(d['A_z'], 2)} | {'' if d['D_z'] is None else round(d['D_z'], 2)} |")
    (SYN / "summary.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
