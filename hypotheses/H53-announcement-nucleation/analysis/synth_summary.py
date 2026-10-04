"""Summarize the synthetic validation: per world x target, recovery rates of each test and the classification table."""
from __future__ import annotations

import json

import numpy as np

from h53core import OUT

SYN = OUT / "synthetic"


def rate(xs):
    xs = [x for x in xs if x is not None]
    return float(np.mean(xs)) if xs else None


def summarize(path=SYN / "synthetic_results.json", write=True):
    d = json.loads(path.read_text())
    res = d["results"]
    keys = sorted({(r["world"], r["target"]) for r in res}, key=lambda k: (k[1], k[0]))
    table = {}
    for w, t in keys:
        rs = [r for r in res if r["world"] == w and r["target"] == t]
        ag = [r["agent"].get("x_timely", {}) for r in rs]
        f1 = [r["field"]["F1"]["ratio"] for r in rs]
        f2 = [r["field"]["F2"]["ratio"] for r in rs]
        f4 = [r["field"]["F4"].get("ratio") for r in rs]
        sh0 = [r["shift"]["0"]["lo"] > 0 for r in rs]
        shx = [max(r["shift"][k]["lo"] > 0 for k in r["shift"] if k != "0") for r in rs]
        mf = [r["models"]["M_full+R"] for r in rs]
        stat = [(m["coef"][m["cols"].index("lstat")] - 1.96 * m["se"][m["cols"].index("lstat")]) > 0 for m in mf]
        labs = [r["label"] for r in rs]
        labs2 = [r.get("label_v2") for r in rs]
        agi = [r.get("agent_int", {}).get("x_recept", {}) for r in rs]
        table[f"{w}@{t}"] = dict(
            n=len(rs), mean_wave=float(np.mean([r["mean_wave"] for r in rs])),
            rr_median=float(np.median([a.get("rr", np.nan) for a in ag])),
            p1_pos=rate([a.get("lo", 0) > 1 for a in ag]),
            p1_pass=rate([(a.get("lo", 0) > 1) and (a.get("rr", 0) >= 1.5) for a in ag]),
            mR_beats_N=rate([r["cmp"]["M_R-M_N"]["lo90"] > 0 for r in rs]),
            mR_beats_U=rate([r["cmp"]["M_R-M_U"]["lo90"] > 0 for r in rs]),
            fullR_beats_full=rate([r["cmp"]["M_full+R-M_full"]["lo90"] > 0 for r in rs]),
            status_pos=rate(stat),
            f1_median=float(np.nanmedian([x if x is not None else np.nan for x in f1])),
            f1_ge3=rate([x is not None and x >= 3 for x in f1]),
            f2_median=float(np.nanmedian([x if x is not None else np.nan for x in f2])),
            f2_le03=rate([x is not None and x <= 0.3 for x in f2]),
            f4_median=float(np.nanmedian([x if x is not None else np.nan for x in f4])),
            shift0_pos=rate(sh0), shift_any_pos=rate(shx),
            labels={k: labs.count(k) for k in sorted(set(labs))},
            labels_v2={k: labs2.count(k) for k in sorted(set(x for x in labs2 if x))},
            rrint_median=float(np.median([a.get("rr", np.nan) for a in agi])) if agi and agi[0] else None,
            int_pos=rate([a.get("lo", 0) > 1 for a in agi]) if agi and agi[0] else None,
        )
    if write:
        (SYN / "synthetic_summary.json").write_text(json.dumps(table, indent=1))
    return table


if __name__ == "__main__":
    t = summarize()
    cols = ["mean_wave", "rr_median", "p1_pos", "p1_pass", "mR_beats_N", "mR_beats_U", "fullR_beats_full", "status_pos",
            "f1_median", "f1_ge3", "f2_median", "f2_le03", "f4_median", "shift0_pos", "shift_any_pos", "rrint_median", "int_pos"]
    print("world".ljust(12), " ".join(c[:9].rjust(9) for c in cols), "labels")
    for k, v in t.items():
        print(k.ljust(12), " ".join((f"{v[c]:9.2f}" if isinstance(v[c], float) else str(v[c]).rjust(9)) for c in cols), v["labels_v2"])
