"""Write H147 round-1 rows to the shared per-period estimates table (role native: #51 is the only period this card
runs on; one row per memeplex and statistic, plus the K1 positive control). No synthetic rows.
Usage: uv run python hypotheses/H147-egregore-value-and-hosts-51/analysis/write_estimates.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h147common as C  # noqa: E402
import estimates as E  # noqa: E402  (infra/shared)

import polars as pl  # noqa: E402

RES = C.OUT / "results"


def base(stat, channel, est, lo, hi, n, method, null, notes, n_kind="events", ci_kind="percentile", post_hoc=False):
    return {"period_unit": "G51", "goal_no": 51, "statistic": stat, "channel": channel, "estimate": est,
            "ci_lo": lo, "ci_hi": hi, "n": float(n), "method": method, "null": null, "role": "native",
            "ci_level": 0.95, "ci_kind": ci_kind, "n_kind": n_kind, "first_day": C.FIRST, "last_day": C.LAST,
            "confirmatory": False, "post_hoc": post_hoc, "source": str(RES.relative_to(C.ROOT)), "notes": notes}


def main():
    rows = []
    k1 = json.loads((RES / "k1_selfdip.json").read_text())
    n_ev = pl.read_parquet(C.OUT / "events_fp.parquet").height
    for k, v in k1.items():
        rows.append(base("h147_k1_selfdip", k, v["dV_rel"], v["ci"][0], v["ci"][1], n_ev,
                         "Poisson stratum FE, own output in calls 1..20 after F vs P; agent-day cluster bootstrap",
                         "placebo call 21 of a segment >= 40", "K1 positive control (pattern-free)"))
    df = pl.read_parquet(RES / "patterns.parquet").filter(pl.col("source") == "H145")
    for r in df.iter_rows(named=True):
        ch = f"memeplex {r['id']}"
        note = f"{r['label']}; h_K {r['h_K']:.2f}" if r["h_K"] is not None else str(r["label"])
        rows.append(base("h147_dV_wipe_rate", ch, r["dV_rate"], r["dV_lo"], r["dV_hi"], r["n_host_events"],
                         "A1 rate form: exp(b_rate)-1 minus pseudo median; agent-day bootstrap B=200",
                         "100 frequency-matched pseudo-patterns; placebo calls", note))
        rows.append(base("h147_others_response", ch, r["oth"], r["oth_lo"], r["oth_hi"], r["n_host_events"],
                         "others' K share per unit dose; combined CI (bootstrap + pseudo spread)",
                         "100 frequency-matched pseudo-patterns; placebo calls", note, ci_kind="se_z"))
        rows.append(base("h147_host_commits", ch, r["host_c"], r["host_c_lo"], r["host_c_hi"], r["n_bins_host_fit"],
                         "A2 within agent, activity held; Poisson agent x day-part FE + trends; bootstrap B=200",
                         "matched non-hosting bins of the same agent", note + f"; class {r['class']}",
                         n_kind="agent-bins"))
        rows.append(base("h147_host_alignment", ch, r["host_a"], r["host_a_lo"], r["host_a_hi"], r["n_bins_host_fit"],
                         "A2 within agent, activity held; OLS agent x day-part FE + trends; relative to non-hosting",
                         "matched non-hosting bins of the same agent", note, n_kind="agent-bins"))
    out = E.write_estimates(rows, hypothesis="H147")
    print(out.height, "rows written")


if __name__ == "__main__":
    main()
