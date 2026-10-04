"""H46 replication layer: the common estimator on every eligible goal period (templated verdicts).

Per period: entry-boundary percentiles (from conservation_rows), cross-boundary fingerprint (fingerprint.parquet),
within-period split-half fingerprint and agent variance share (style vs content, day-demeaned), and the KW
information (kw_info.json, #30 onward).
Output: data/processed/H46-style-conserved-charge/replication.json
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h46lib as L  # noqa: E402
from write_period_cards import ENTRY  # noqa: E402


def r2_agent(M, ag):
    mu = M.mean(0)
    sst = ((M - mu) ** 2).sum()
    ssw = sum(((M[ag == a] - M[ag == a].mean(0)) ** 2).sum() for a in np.unique(ag))
    return float(1 - ssw / sst) if sst > 0 else np.nan


def main():
    el = json.loads((L.DATA / "period_list.json").read_text())["eligible"]
    rows = pl.read_parquet(L.DATA / "conservation_rows.parquet")
    fp = pl.read_parquet(L.DATA / "fingerprint.parquet")
    kw = json.loads((L.DATA / "kw_info.json").read_text())["periods"] if (L.DATA / "kw_info.json").exists() else {}
    m = L.load_messages()
    mats = {"style": L.style_matrix(m, "tc"), "content": L.content_matrix(m, "resid")}
    dt_ = L.day_table(m, mats)
    L.add_demeaned(dt_, ["style", "content"])
    k = dt_.keys
    out = {}
    for g in el:
        r = {"goal": g}
        kk = k.filter(pl.col("goal_no") == g)
        ix = kk["row"].to_numpy()
        ag = kk["agent"].to_numpy()
        days = sorted(kk["pt_date"].unique().to_list())
        r["n_agents"], r["n_days"], r["n_agent_days"] = int(len(np.unique(ag))), len(days), int(len(ix))
        for c in ("style", "content"):
            r[f"r2_agent_{c}"] = r2_agent(dt_.M[c + "_dm"][ix], ag)
        # split-half fingerprint within period
        if len(days) >= 2:
            h = len(days) // 2
            first, second = set(days[:h]), set(days[h:])
            dd = kk["pt_date"].to_numpy()
            tr, te = np.isin(dd, list(first)), np.isin(dd, list(second))
            common = np.intersect1d(ag[tr], ag[te])
            tr &= np.isin(ag, common)
            te &= np.isin(ag, common)
            if len(common) >= 3:
                for c in ("style", "content"):
                    M = dt_.M[c + "_dm"][ix]
                    yhat = L.nc_classify(M[tr], ag[tr], M[te])
                    r[f"split_{c}"] = L.balanced_acc(ag[te], yhat)
                r["split_chance"] = 1 / len(common)
        # entry boundary
        if g in ENTRY:
            p = ENTRY[g][0]
            lab = [x for x in rows["label"].unique().to_list() if x.split(" ")[0] == f"{p}->{g}"]
            if lab:
                sub = rows.filter(pl.col("label") == lab[0])
                r["entry"] = {"label": lab[0], "n_agents": sub.height, "flag": ENTRY[g][1]}
                for ch in ("style", "style_raw", "content", "content_white", "style_dm", "content_dm"):
                    if f"r_{ch}" in sub.columns:
                        t = L.class_test(sub, ch, n_rand=5000, n_boot=500)
                        r["entry"][ch] = {"T": t.get("T"), "p_rand": t.get("p_rand"), "lo": t.get("lo"), "hi": t.get("hi")}
                f = fp.filter((pl.col("label") == lab[0]) & (pl.col("family") == "all"))
                for row in f.iter_rows(named=True):
                    r["entry"][f"fp_{row['variant']}"] = {"cross": row["cross"], "chance": row["chance"],
                                                          "ceiling": row["ceiling"]}
        if f"G{g:02d}" in kw:
            v = kw[f"G{g:02d}"]
            r["kw"] = {c: {"bits": v[c].get("bits"), "p": v[c].get("p"), "r2_cv": v[c].get("r2_cv")}
                       for c in ("style", "content") if c in v}
        # templated verdict
        e = r.get("entry")
        if e and "style" in e and "fp_style" in e:
            Ts, Tc = e["style"]["T"], e["content"]["T"]
            acc_s, acc_c, ch_ = e["fp_style"]["cross"], e["fp_content"]["cross"], e["fp_style"]["chance"]
            if Ts > 0.60 and Ts >= Tc - 0.10 or acc_s <= 1.5 * ch_:
                v = "failed"
            elif Ts <= 0.60 and Tc >= Ts + 0.10 and acc_s > acc_c and acc_s >= 2 * ch_:
                v = "supported"
            else:
                v = "mixed"
        else:
            v = "descriptive"
        r["verdict"] = v
        out[f"G{g:02d}"] = r
        print(g, v, {kk_: (round(vv["T"], 2) if isinstance(vv, dict) and "T" in vv else None)
                     for kk_, vv in (e or {}).items() if kk_ in ("style", "content")},
              round(r.get("split_style", np.nan), 2), round(r.get("split_content", np.nan), 2), round(r.get("split_chance", np.nan), 2))
    (L.DATA / "replication.json").write_text(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
