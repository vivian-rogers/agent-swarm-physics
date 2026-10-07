"""Size, power and bias table from analysis/synthetic.py outputs (data/processed/H137-.../synthetic/<tag>/W*.jsonl).

Tests (pooled over the skeleton units):
  P1 card   theta (pop + in-degree controls): bootstrap CI > 0 and N2 p < 0.05
  P1 A1     theta_act (+ hopper propensity): CI > 0 and N2 p < 0.05
  theta two-sided: CI excludes 0 (either sign), card and A1
  O1 flip   mean A (one-way) above the N1 direction-flip null (p < 0.05)
  O1 adj    mean A above the N1b propensity-adjusted null (p < 0.05)
  P3 card   sigma_one - sigma_none, pair-bootstrap CI > 0
  P3 adj    contrast above its N1b null (p < 0.05)
  sym flip  sigma_mutual or sigma_none above the flip null (p < 0.05) in a testable unit (per-unit P2 rejection rate)
  sym adj   the same against N1b
  P4        read minus in-flight follow rate, CI > 0
Writes results/synthetic_table.json and prints a markdown table.
Usage: uv run python hypotheses/H137-nonreciprocal-potts-named-pairs/analysis/synthetic_summary.py --tag calls
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h137lib as L  # noqa: E402


def rate(rs, f):
    v = [f(r) for r in rs]
    v = [x for x in v if x is not None]
    return (float(np.mean(v)) if v else float("nan")), len(v)


def nz(x):
    return x is not None and np.isfinite(x)


def summarize_light(rs):
    out = {"runs": len(rs)}
    out["P1_A1"] = rate(rs, lambda r: (nz(r["theta_act_lo"]) and r["theta_act_lo"] > 0 and r["theta_act_p"] < 0.05) if nz(r["theta_act"]) else None)
    out["theta_2s_A1"] = rate(rs, lambda r: (r["theta_act_lo"] > 0 or r["theta_act_hi"] < 0) if nz(r["theta_act_lo"]) else None)
    out["P4"] = rate(rs, lambda r: (r["o4_lo"] > 0) if nz(r["o4_lo"]) else None)
    for k in ("theta_act", "o4"):
        v = np.array([r[k] for r in rs if nz(r[k])], float)
        out[f"mean_{k}"] = (float(v.mean()), float(v.std()))
    out["hops_mean"] = float(np.mean([sum(p["hops"] for p in r["pre"]) for r in rs]))
    out["follow_hops_mean"] = float(np.mean([sum(p["follow"] for p in r["pre"]) for r in rs]))
    out["units"] = len(rs[0]["pre"])
    return out


def summarize(rs):
    if "theta" not in rs[0]:
        return summarize_light(rs)
    out = {"runs": len(rs)}
    out["P1_card"] = rate(rs, lambda r: (nz(r["theta_lo"]) and r["theta_lo"] > 0 and r["theta_p"] < 0.05) if nz(r["theta"]) else None)
    out["P1_A1"] = rate(rs, lambda r: (nz(r["theta_act_lo"]) and r["theta_act_lo"] > 0 and r["theta_act_p"] < 0.05) if nz(r["theta_act"]) else None)
    out["theta_2s_card"] = rate(rs, lambda r: (r["theta_lo"] > 0 or r["theta_hi"] < 0) if nz(r["theta_lo"]) else None)
    out["theta_2s_A1"] = rate(rs, lambda r: (r["theta_act_lo"] > 0 or r["theta_act_hi"] < 0) if nz(r["theta_act_lo"]) else None)
    out["theta_raw_pos"] = rate(rs, lambda r: (r["theta_raw_lo"] > 0) if nz(r["theta_raw_lo"]) else None)
    out["O1_flip"] = rate(rs, lambda r: (r["A_one_p"] < 0.05) if nz(r["A_one_p"]) else None)
    out["O1_adj"] = rate(rs, lambda r: (r["A_one_padj"] < 0.05) if nz(r.get("A_one_padj")) else None)
    out["P3_card"] = rate(rs, lambda r: (r["contrast_lo"] > 0) if nz(r["contrast_lo"]) else None)
    out["P3_adj"] = rate(rs, lambda r: (r["contrast_padj"] < 0.05) if nz(r.get("contrast_padj")) else None)
    for k in ("sig_one", "sig_mutual", "sig_none"):
        out[f"{k}_flip"] = rate(rs, lambda r, k=k: (r[f"{k}_p"] < 0.05) if nz(r[f"{k}_p"]) else None)
        out[f"{k}_adj"] = rate(rs, lambda r, k=k: (r[f"{k}_padj"] < 0.05) if nz(r.get(f"{k}_padj")) else None)
    sf, sa = [], []
    for r in rs:
        for u in r["p2_units"]:
            for c in ("mutual", "none"):
                if c in u:
                    sf.append(u[c] < 0.05)
                    sa.append(u[c + "_adj"] < 0.05)
    out["sym_unit_flip"] = (float(np.mean(sf)) if sf else float("nan"), len(sf))
    out["sym_unit_adj"] = (float(np.mean(sa)) if sa else float("nan"), len(sa))
    out["P4"] = rate(rs, lambda r: (r["o4_lo"] > 0) if nz(r["o4_lo"]) else None)
    for k in ("theta", "theta_act", "theta_raw", "A_one", "contrast", "o4"):
        v = np.array([r[k] for r in rs if nz(r[k])], float)
        out[f"mean_{k}"] = (float(v.mean()) if v.size else float("nan"), float(v.std()) if v.size else float("nan"))
    pre = [p for r in rs for p in r["pre"]]
    out["testable_frac"] = float(np.mean([p["testable"] for p in pre]))
    out["follow_hops_mean"] = float(np.mean([sum(p["follow"] for p in r["pre"]) for r in rs]))
    out["hops_mean"] = float(np.mean([sum(p["hops"] for p in r["pre"]) for r in rs]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="calls")
    a = ap.parse_args()
    d = L.D / "synthetic" / a.tag
    tab = {}
    for f in sorted(d.glob("W*.jsonl")):
        rs = [json.loads(x) for x in open(f)]
        tab[f.stem] = summarize(rs)
    keys = ["runs", "P1_card", "P1_A1", "theta_2s_card", "theta_2s_A1", "theta_raw_pos", "O1_flip", "O1_adj", "P3_card",
            "P3_adj", "sig_mutual_flip", "sig_mutual_adj", "sig_none_flip", "sig_none_adj", "sym_unit_flip", "sym_unit_adj", "P4",
            "mean_theta", "mean_theta_act", "mean_theta_raw", "mean_A_one", "mean_contrast", "mean_o4", "hops_mean",
            "follow_hops_mean"]
    print("| stat | " + " | ".join(tab) + " |")
    print("|---" * (len(tab) + 1) + "|")
    for k in keys:
        cells = []
        for w in tab:
            v = tab[w].get(k)
            if v is None:
                cells.append("")
            elif isinstance(v, tuple):
                cells.append(f"{v[0]:.3f}" if k.startswith("mean") is False else f"{v[0]:.3f} ± {v[1]:.3f}")
            else:
                cells.append(f"{v:.0f}" if isinstance(v, (int, float)) else str(v))
        print(f"| {k} | " + " | ".join(cells) + " |")
    out = L.D / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"synthetic_table_{a.tag}.json").write_text(json.dumps(tab, indent=1))


if __name__ == "__main__":
    main()
