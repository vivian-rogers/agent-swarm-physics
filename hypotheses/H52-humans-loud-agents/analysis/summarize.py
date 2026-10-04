"""H52 cross-period synthesis: per-period headline table, random-effects pooling per regime, decision rules.

Reads data/processed/H52-humans-loud-agents/<period>/results.json (+ native/*.json); writes summary.json and
period_table.parquet in data/processed/H52-humans-loud-agents/.
Usage: uv run python hypotheses/H52-humans-loud-agents/analysis/summarize.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h52lib as L  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

OUTC = ("con", "rep", "act", "st")
REGIME = {p: ("III" if int(p[1:3]) >= 37 else "I") for p in L.REPLICATION + L.EXTRA}


def load(period):
    p = L.OUT / period / "results.json"
    return json.loads(p.read_text()) if p.exists() else None


def main():
    rows = []
    for p in L.REPLICATION + L.EXTRA:
        r = load(p)
        if not r:
            continue
        hd = r["headline"]
        de = r.get("descr", {})
        for oc in OUTC:
            for c in ("human", "bot"):
                h = hd.get(f"{oc}_{c}")
                if not h or h.get("att") is None:
                    continue
                rows.append(dict(period=p, regime=REGIME[p], replication=p in L.REPLICATION, outcome=oc, cls=c,
                                 att=h["att"], lo=(h.get("ci") or [None, None])[0], hi=(h.get("ci") or [None, None])[1],
                                 se=h.get("se"), n_t=h.get("n_t"), n_msgs=h.get("n_t_msgs"), matched=h.get("matched"),
                                 ctrl_mean=h.get("ctrl_mean"), naive=h.get("naive"), cluster=h.get("cluster"),
                                 days_cls=de.get(c, {}).get("days"),
                                 naming=hd.get(f"{oc}_agent_naming", {}).get("att"),
                                 naming_se=hd.get(f"{oc}_agent_naming", {}).get("se")))
    T = pl.DataFrame(rows, infer_schema_length=None)
    T = T.with_columns([pl.col(c).cast(pl.Float64) for c in ("att", "lo", "hi", "se", "matched", "ctrl_mean", "naive",
                                                              "naming", "naming_se")])
    # powered (pre-registered): >= 300 matched human content rows and >= 6 days with human messages
    con_h = T.filter((pl.col("outcome") == "con") & (pl.col("cls") == "human"))
    powered = [r["period"] for r in con_h.iter_rows(named=True)
               if (r["n_t"] or 0) * (r["matched"] or 0) >= 300 and (r["days_cls"] or 0) >= 6 and r["replication"]]
    T = T.with_columns(pl.col("period").is_in(powered).alias("powered"))
    # margins
    S = {"powered": powered}
    margins = {}
    for oc in ("con", "rep"):
        sub = T.filter((pl.col("outcome") == oc) & (pl.col("cls") == "human") & pl.col("replication")).unique("period")
        pn = L.re_pool(sub["naming"].to_list(), sub["naming_se"].to_list())
        margins[oc] = 0.5 * abs(pn["pooled"]) if np.isfinite(pn["pooled"]) else np.nan
        S[f"agent_naming_pooled_{oc}"] = pn
    margins["act"] = 0.5
    margins["st"] = 0.05
    S["margins"] = margins
    T = T.with_columns(pl.struct("outcome", "lo", "hi").map_elements(
        lambda s: L.verdict_from_ci([s["lo"] if s["lo"] is not None else np.nan, s["hi"] if s["hi"] is not None else np.nan],
                                    margins.get(s["outcome"])), return_dtype=pl.Utf8).alias("verdict"))
    # pooled per regime (replication periods only)
    pooled = {}
    for oc in OUTC:
        for c in ("human", "bot"):
            for reg in ("I", "III", "all"):
                sub = T.filter((pl.col("outcome") == oc) & (pl.col("cls") == c) & pl.col("replication"))
                if reg != "all":
                    sub = sub.filter(pl.col("regime") == reg)
                if sub.height == 0:
                    continue
                pr = L.re_pool(sub["att"].to_list(), sub["se"].to_list())
                pr["verdict"] = L.verdict_from_ci(pr["ci"], margins.get(oc))
                pr["naive_pooled"] = L.re_pool(sub["naive"].to_list(), sub["se"].to_list())["pooled"]
                pr["periods"] = sub["period"].to_list()
                pooled[f"{oc}_{c}_{reg}"] = pr
    S["pooled"] = pooled
    # counts
    cnt = {}
    for oc in OUTC:
        for c in ("human", "bot"):
            sub = T.filter((pl.col("outcome") == oc) & (pl.col("cls") == c) & pl.col("replication"))
            cnt[f"{oc}_{c}"] = dict(sub.group_by("verdict").len().iter_rows())
            subp = sub.filter(pl.col("powered"))
            cnt[f"{oc}_{c}_powered"] = dict(subp.group_by("verdict").len().iter_rows())
    S["verdict_counts"] = cnt
    # P6: naive vs matched beyond SE in powered periods
    p6 = T.filter(pl.col("powered") & (pl.col("cls") == "human")).with_columns(
        ((pl.col("naive") - pl.col("att")).abs() > pl.col("se")).alias("naive_differs"))
    S["P6_naive_differs"] = p6.select("period", "outcome", "naive", "att", "se", "naive_differs").to_dicts()
    # extra pools: bot over every period with nudges (named rows; activity BC), H30-orth naming, boundary diffs
    extra = {}
    for oc, sub_key in (("rep", "named"), ("act", "named_bc"), ("con", "all"), ("rep", "all"), ("st", "all")):
        e, se, per = [], [], []
        for p in L.REPLICATION + L.EXTRA:
            r = load(p)
            if not r or "bot" not in r["primary"].get(oc, {}):
                continue
            b = r["primary"][oc]["bot"].get(sub_key, {})
            if b.get("att") is not None and b.get("se") is not None and np.isfinite(b["se"]) and b["se"] > 0:
                e.append(b["att"]); se.append(b["se"]); per.append(p)
        extra[f"bot_{oc}_{sub_key}_allperiods"] = dict(**L.re_pool(e, se), periods=per)
    for tag in ("con_h30orth", "con_gte", "con_jd", "con_sr"):
        e, se, ne, nse = [], [], [], []
        for p in L.REPLICATION:
            r = load(p)
            if not r or tag not in r["robustness"]:
                continue
            h = r["robustness"][tag].get("human", {}).get("all", {}); n = r["robustness"][tag].get("agent_naming", {})
            if h.get("att") is not None and h.get("se"):
                e.append(h["att"]); se.append(h["se"])
            if n.get("att") is not None and n.get("se"):
                ne.append(n["att"]); nse.append(n["se"])
        extra[f"human_{tag}_pooled"] = L.re_pool(e, se)
        extra[f"agent_naming_{tag}_pooled"] = L.re_pool(ne, nse)
    bd = []
    for p in L.REPLICATION:
        r = load(p)
        if r and r.get("boundary", {}).get("human_minus_agent_unnamed", {}).get("diff") is not None:
            b = r["boundary"]["human_minus_agent_unnamed"]
            bd.append(dict(period=p, diff=b["diff"], ci=b["ci"]))
    extra["boundary_human_minus_agent_unnamed"] = bd
    S["extra"] = extra
    # native
    nat = {}
    for f in sorted((L.OUT / "native").glob("*.json")):
        nat[f.stem] = json.loads(f.read_text())
    S["native"] = nat
    T.write_parquet(L.OUT / "period_table.parquet")
    L.jdump(S, L.OUT / "summary.json")
    print("powered:", powered)
    for k, v in pooled.items():
        print(k, round(v["pooled"], 4) if np.isfinite(v["pooled"]) else None, [round(x, 4) for x in v["ci"]], v["verdict"], "k", v["k"])


if __name__ == "__main__":
    main()
