"""H88 replication layer: decay fits per eligible period and channel, departure check, newcomer ratio, store contrast,
re-coinage check and the exogenous re-activation refit (non-holdout only).

  uv run python hypotheses/H88-collective-memory-decay/analysis/replication.py
Output: data/processed/H88-collective-memory-decay/replication/replication.json
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h88lib as H  # noqa: E402

OUTD = H.DATA / "replication"


def no_human_series(daily, uses, P, kind):
    """Veteran series without items that a human mentions after P's last day (O6 / K5); O unchanged."""
    per = pl.read_parquet(H.DATA / "periods.parquet").filter(pl.col("P") == P)
    last = per["last_day"][0]
    hum = uses.filter((pl.col("P") == P) & (pl.col("kind") == kind) & (pl.col("speaker") == "human")
                      & (pl.col("pt_date") > last))["item"].unique()
    car = pl.read_parquet(H.DATA / "carriers.parquet").filter((pl.col("P") == P) & (pl.col("group") == "vet"))
    u = uses.filter((pl.col("P") == P) & (pl.col("kind") == kind) & (pl.col("speaker") == "agent")
                    & ~pl.col("item").is_in(hum.implode()) & pl.col("agent").is_in(car["agent"].implode()))
    yc = dict(u.group_by("pt_date").len().iter_rows())
    s = daily.filter((pl.col("P") == P) & (pl.col("kind") == kind) & (pl.col("group") == "vet") & pl.col("observed")
                     & (pl.col("O") > 0)).sort("k")
    y = np.array([yc.get(d, 0) for d in s["pt_date"].to_list()], float)
    return s["k"].to_numpy().astype(float), y, s["O"].to_numpy().astype(float), int(hum.len())


def main():
    OUTD.mkdir(parents=True, exist_ok=True)
    daily = H.load_daily(); uses = pl.read_parquet(H.DATA / "uses.parquet")
    syn = json.loads((H.DATA / "synthetic" / "synthetic.json").read_text())
    elig = {"art": syn["eligible_art"], "term": syn["eligible_term"]}
    out = {"run_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), "eligible": elig, "periods": {}}
    for kind in ("art", "term"):
        for P in elig[kind]:
            k, y, O = H.series(daily, P, kind, "vet")
            if y.sum() < 50:
                out["periods"].setdefault(str(P), {})[kind] = None
                continue
            r = {"n_uses_post": int(y.sum()), "n_days": len(k)}
            r["fit"] = H.fit_all(k, y, O)
            r["M2_ci"] = H.block_boot_M2(k, y, O, B=100, seed=P)
            r["ratio"] = H.share_ratio(k, y, O, seed=P)
            kn, yn, On = H.series(daily, P, kind, "new")
            if yn.sum() >= 20 and len(kn) >= 15:
                f1 = H.fit("M1", kn, yn, On)
                r["new_M1_tau"] = float(np.exp(f1.x[1])); r["new_uses"] = int(yn.sum())
            k2, y2, O2, nh = no_human_series(daily, uses, P, kind)
            if y2.sum() >= 50:
                f2 = H.fit_all(k2, y2, O2)
                r["no_human"] = {"best": f2["best"], "dq_M1_M2": f2["dq_M1_M2"], "biexp": f2["biexp"],
                                 "M2_params": f2["M2_params"], "n_items_dropped": nh}
            out["periods"].setdefault(str(P), {})[kind] = r
            print(kind, P, r["fit"]["best"], round(r["fit"]["dq_M1_M2"], 1), flush=True)
    # card level
    card = {}
    for kind in ("art", "term"):
        rs = [v[kind] for v in out["periods"].values() if v.get(kind)]
        best = Counter(r["fit"]["best"] for r in rs)
        bi = sum(r["fit"]["biexp"] for r in rs)
        t1 = [r["fit"]["M2_params"]["tau1"] for r in rs if r["fit"]["biexp"]]
        t2 = [r["fit"]["M2_params"]["tau2"] for r in rs if r["fit"]["biexp"]]
        rat = [r["ratio"] for r in rs if r["ratio"].get("ratio") is not None and np.isfinite(r["ratio"]["ratio"])]
        dec = sum(1 for x in rat if x.get("ci") and x["ci"][1] < 1)
        nh = [r["no_human"] for r in rs if r.get("no_human")]
        card[kind] = {"n_periods": len(rs), "best_counts": dict(best), "n_biexp": bi,
                      "modal_best": best.most_common(1)[0][0] if best else None,
                      "tau1_median": float(np.median(t1)) if t1 else None, "tau2_median": float(np.median(t2)) if t2 else None,
                      "tau1_iqr": [float(np.quantile(t1, .25)), float(np.quantile(t1, .75))] if t1 else None,
                      "tau2_iqr": [float(np.quantile(t2, .25)), float(np.quantile(t2, .75))] if t2 else None,
                      "slow_share_median": float(np.median([r["fit"]["M2_params"]["slow_share"] for r in rs])) if rs else None,
                      "ratio_median": float(np.median([x["ratio"] for x in rat])) if rat else None,
                      "M1c_tau_median": float(np.median([r["fit"]["M1c_params"]["tau"] for r in rs])),
                      "M1c_floor_ratio_median": float(np.median([r["fit"]["M1c_params"]["c"] / r["fit"]["M1c_params"]["A"]
                                                                  for r in rs])),
                      "M1_tau_median": float(np.median([r["fit"]["M1_params"]["tau"] for r in rs])),
                      "n_ratio_decay": dec, "n_ratio": len(rat),
                      "no_human_best_counts": dict(Counter(x["best"] for x in nh)),
                      "no_human_n_biexp": sum(x["biexp"] for x in nh), "no_human_n": len(nh)}
        thr = 0.4 if kind == "art" else 0.5
        card[kind]["P1_pass"] = bool(card[kind]["modal_best"] == "M2" and bi >= thr * len(rs))
        card[kind]["kill1"] = bool(best.get("M1", 0) >= 0.5 * len(rs))
        card[kind]["P2_pass"] = bool(len(rat) and dec >= (2 / 3) * len(rat))
        # newcomers (A1.1)
        rows = daily.filter(pl.col("kind") == kind).filter(pl.col("P").is_in(elig[kind]) & pl.col("observed")
                                                             & (pl.col("O") > 0) & pl.col("group").is_in(["vet", "new"]))
        rows = rows.select("P", "group", "k", "y", "O")
        card[kind]["newcomer"] = H.ratio_bands_boot(rows, B=2000, seed=88)
        nb = card[kind]["newcomer"]
        card[kind]["P3_pass"] = bool(nb["b"] is not None and nb["b"] > 0 and nb["b_ci"] and nb["b_ci"][0] > 0)
        nt = [(r["new_M1_tau"], r["fit"]["M2_params"]["tau1"]) for r in rs if "new_M1_tau" in r]
        card[kind]["newcomer_tau_vs_tau1"] = {"n": len(nt), "n_new_tau_gt_tau1": sum(a > b for a, b in nt),
                                             "median_new_tau": float(np.median([a for a, _ in nt])) if nt else None}
        print(kind, json.dumps(card[kind], default=float)[:900], flush=True)
    # P4 store contrast
    both = [(v["art"]["fit"]["M2_params"]["slow_share"], v["term"]["fit"]["M2_params"]["slow_share"], P)
            for P, v in out["periods"].items() if v.get("art") and v.get("term")]
    card["P4"] = {"n": len(both), "n_art_gt_term": sum(a > b for a, b, _ in both),
                  "pairs": {P: [a, b] for a, b, P in both}}
    card["P4"]["pass"] = bool(both and card["P4"]["n_art_gt_term"] >= (2 / 3) * len(both))
    # P5 re-coinage
    tf = pl.read_parquet(H.DATA / "term_firstuse_newc.parquet")
    card["P5"] = {"n_first_uses": tf.height, "in_cone_share": float(tf["in_cone"].mean()) if tf.height else None}
    out["card"] = card
    (OUTD / "replication.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps({k: v for k, v in card.items() if k in ("P4", "P5")}, default=float)[:600])


if __name__ == "__main__":
    main()
