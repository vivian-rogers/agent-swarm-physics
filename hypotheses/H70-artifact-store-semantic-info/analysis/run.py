"""H70 round 1: replication per period (artifact row), natives NE41 (call-scale kappa table) and NE34 (goal boundaries).

Exploratory, non-holdout only. Writes data/processed/H70-artifact-store-semantic-info/results/{periods,natives}.json.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h70lib as L  # noqa: E402

K = L.K
RES = L.OUT / "results"
B = 300


def verdict(row: dict | None, n_ok: bool) -> str:
    if row is None or not n_ok:
        return "descriptive"
    I_sig = row["p_perm"] < 0.05 and row["I"] > 0
    lo, hi = row["dV_rel_ci"]
    if lo is None:
        return "descriptive"
    if not I_sig or hi < 0:
        return "failed"
    if lo > 0:
        return "supported"
    return "mixed"


def per_period(ev: pl.DataFrame) -> dict:
    out = {}
    for per in sorted(ev["period"].unique().to_list()):
        e = ev.filter(pl.col("period") == per)
        r = {"period": per, "regime": e["regime"].mode().first(), "return": L.return_prob(e)}
        for scale in ("call", "day"):
            r[scale] = {}
            for ch in ("A", "C"):
                row = L.row_or_none(e, scale, ch, B=B, seed=hash((per, scale, ch)) % 1000)
                if row is not None:
                    r[scale][ch] = row
        prim = "call" if "A" in r["call"] else "day"
        r["primary_scale"] = prim
        r["verdict"] = verdict(r[prim].get("A"), "A" in r[prim])
        a = r[prim].get("A")
        if a:
            print(per, prim, r["verdict"], f"I_A {a['I']:+.3f} [{a['I_ci'][0]:+.3f}, {a['I_ci'][1]:+.3f}] p {a['p_perm']:.3f} "
                  f"dV_rel {a['dV_rel']:+.3f} {a['dV_rel_ci']} dV {a['dV']:+.3f} Vpl {a['V_mean_placebo']:.2f} "
                  f"kappa {a['kappa']:+.3f} ret {r['return']}", flush=True)
        else:
            print(per, "no primary row", flush=True)
        out[per] = r
    return out


def pooled_table(ev: pl.DataFrame, scale: str, regime3: bool) -> dict:
    e = ev.filter(pl.col("regime") == "III") if regime3 else ev
    t = {}
    for ch in ("A", "M", "R", "C"):
        row = L.row_or_none(e, scale, ch, B=B, seed=7 + ord(ch))
        t[ch] = row
        if row:
            print(f"pooled {scale} {ch}: I {row['I']:+.3f} {row['I_ci']} dV_rel {row['dV_rel']:+.3f} {row['dV_rel_ci']} dV {row['dV']:+.3f} {row['dV_ci']} "
                  f"kappa {row['kappa']:+.3f} {row['kappa_ci']} open F/P {row.get('open_share_scramble')} "
                  f"{row.get('open_share_placebo')}", flush=True)
    return t


def dl_rows(per_res: dict, scale: str, key: str) -> dict:
    est, se = [], []
    for r in per_res.values():
        a = r.get(scale, {}).get("A")
        # rows with a degenerate bootstrap (e.g. a pointer constant within every agent: I = 0 exactly, SE 0) are skipped
        if a and a.get(key + "_se") and a[key + "_se"] > 1e-4 and np.isfinite(a[key]):
            est.append(a[key])
            se.append(a[key + "_se"])
    return K.dl_pool(est, se)


def ne34(ev: pl.DataFrame) -> dict:
    """Nights whose previous active day (of the same agent) is in another goal period vs within-period nights."""
    n = (ev.filter((pl.col("etype") == "N") & (pl.col("A_prev") >= 0)).sort("agent", "pt_date")
         .with_columns(pl.col("goal_no").shift(1).over("agent").alias("goal_prev"),
                       pl.col("pt_date").shift(1).over("agent").alias("date_prev")))
    n = n.filter(pl.col("goal_prev").is_not_null())
    n = n.with_columns((pl.col("pt_date").str.to_date() - pl.col("date_prev").str.to_date()).dt.total_days()
                       .alias("gap_d"))
    n = n.filter(pl.col("gap_d") <= 7)
    n = n.with_columns(
        pl.when(pl.col("goal_prev") == pl.col("goal_no")).then(pl.lit("within"))
        .when((pl.col("goal_prev") == 39) & (pl.col("goal_no") == 40)).then(pl.lit("continuation"))
        .otherwise(pl.lit("new_goal")).alias("kind"),
        (pl.format("{}->{}", pl.col("goal_prev"), pl.col("goal_no"))).alias("boundary"))
    rng = np.random.default_rng(34)
    out = {}
    for kind in ("within", "new_goal", "continuation"):
        g = n.filter(pl.col("kind") == kind)
        c = g.filter(pl.col("X_next") >= 0)
        pr = float((c["X_next"] == c["A_prev"]).mean()) if c.height else None
        # agent-cluster bootstrap for P(return)
        ags = c["agent"].unique().to_list()
        bs = []
        for _ in range(1000):
            pick = rng.choice(len(ags), len(ags))
            sub = pl.concat([c.filter(pl.col("agent") == ags[j]) for j in pick]) if ags else c
            bs.append(float((sub["X_next"] == sub["A_prev"]).mean()) if sub.height else np.nan)
        st = (g["agent"].cast(pl.Utf8)).to_numpy()
        info = K.mi_corrected(g["X_next"].to_numpy(), g["A_prev"].to_numpy(), st, n_perm=500, rng=rng) \
            if g.height >= 10 else None
        out[kind] = {"n_nights": g.height, "n_with_commit": c.height, "p_return": pr,
                     "p_return_ci": [float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5))]
                     if c.height else None, "info": info, "boundaries": sorted(g["boundary"].unique().to_list())
                     if kind != "within" else None,
                     "V_mean": float(g["V"].mean()) if g.height else None}
        print("NE34", kind, {k: v for k, v in out[kind].items() if k != "boundaries"}, flush=True)
    per_b = []
    for b, g in n.filter(pl.col("kind") != "within").group_by("boundary"):
        c = g.filter(pl.col("X_next") >= 0)
        per_b.append({"boundary": b[0], "n": g.height, "n_commit": c.height,
                      "p_return": float((c["X_next"] == c["A_prev"]).mean()) if c.height else None})
    out["per_boundary"] = sorted(per_b, key=lambda d: d["boundary"])
    return out


def main():
    ev = L.load_events()
    RES.mkdir(parents=True, exist_ok=True)
    per_res = per_period(ev)
    (RES / "periods.json").write_text(json.dumps(per_res, indent=1, default=float))
    nat = {"NE41": {"call_regime3": pooled_table(ev, "call", True),
                    "dl_I_A": dl_rows(per_res, "call", "I"), "dl_dV_A": dl_rows(per_res, "call", "dV"),
                    "dl_dV_rel_A": dl_rows(per_res, "call", "dV_rel"),
                    "return": L.return_prob(ev.filter(pl.col("regime") == "III"))},
           "day_pooled": {"table": pooled_table(ev, "day", False),
                          "dl_I_A": dl_rows(per_res, "day", "I"), "dl_dV_A": dl_rows(per_res, "day", "dV"),
                          "dl_dV_rel_A": dl_rows(per_res, "day", "dV_rel")},
           "NE34": ne34(ev)}
    (RES / "natives.json").write_text(json.dumps(nat, indent=1, default=float))
    print("DL call I", nat["NE41"]["dl_I_A"], "dV", nat["NE41"]["dl_dV_A"])
    print("DL day I", nat["day_pooled"]["dl_I_A"], "dV", nat["day_pooled"]["dl_dV_A"])


def recompute_dl():
    per_res = json.loads((RES / "periods.json").read_text())
    nat = json.loads((RES / "natives.json").read_text())
    for blk, scale in (("NE41", "call"), ("day_pooled", "day")):
        for key in ("I", "dV", "dV_rel"):
            nat[blk][f"dl_{key}_A"] = dl_rows(per_res, scale, key)
            print(blk, key, nat[blk][f"dl_{key}_A"])
    (RES / "natives.json").write_text(json.dumps(nat, indent=1, default=float))


if __name__ == "__main__":
    if "--dl" in sys.argv:
        recompute_dl()
    else:
        main()
