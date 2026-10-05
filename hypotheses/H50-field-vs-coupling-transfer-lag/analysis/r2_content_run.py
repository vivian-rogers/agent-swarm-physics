"""R1 real data: content read-out jump by hop (matched age), every eligible non-reserved round-1 period unit.
Variants: bge (primary), gte, style_resid_period (bge), drop self-repeats (self_repeat_both), H29 bins [0, 30) s,
age x latency-tercile matching, raw cosine. Named vs unnamed (ledger ment). Hop profile (descriptive).
Writes r2/content_units.parquet and r2/content_summary.json.

Usage: uv run python hypotheses/H50-field-vs-coupling-transfer-lag/analysis/r2_content_run.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "2")
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import r2lib as R2  # noqa: E402
from build import load_unit  # noqa: E402
from common import holdout_mask  # noqa: E402

OUT = ROOT / "data/processed/H50-field-vs-coupling-transfer-lag"
ED = ROOT / "data/processed/shared/embeddings"
NBOOT = 400


def unitvec(x):
    x = x.astype(np.float32)
    n = np.linalg.norm(x, axis=1, keepdims=True)
    return x / np.maximum(n, 1e-9)


def main():
    Z = {"bge": unitvec(np.load(ED / "statements_white32_bge_small.npy")),
         "gte": unitvec(np.load(ED / "statements_white32_gte_modernbert.npy")),
         "bge_srp": unitvec(np.load(ED / "statements_style_resid_period32_bge_small.npy"))}
    flags = pl.read_parquet(ROOT / "data/processed/shared/statement_flags.parquet", columns=["srow", "self_repeat_both"])
    rep = np.zeros(len(Z["bge"]), bool)
    rep[flags["srow"].to_numpy()] = flags["self_repeat_both"].fill_null(False).to_numpy()
    units = pl.read_parquet(OUT / "units.parquet").filter(pl.col("eligible") & (pl.col("kind") == "period_unit"))
    rows_out, profiles = [], {}
    for u, reg, g in zip(units["unit"], units["regime"], units["goal_no"]):
        U = load_unit(OUT / "units" / f"{u}.npz")
        U["N"] = int(U["N"])
        days = [str(d) for d in U["days"]]
        assert not any(holdout_mask(days, [int(g)] * len(days)))
        R = R2.load_r2(OUT / "r2/units" / f"{u}.npz")
        plc = R2.placebo_index(R, np.random.default_rng(1))
        srow = R["m_srow"]
        for model in ("bge", "gte", "bge_srp"):
            Zm = np.where((srow >= 0)[:, None], Z[model][np.maximum(srow, 0)], np.nan).astype(np.float32)
            rows = R2.content_rows(U, R, Zm, plc)
            in60 = rows["age"] < 60
            n1, n0 = int(((rows["h"] == 1) & in60).sum()), int(((rows["h"] == 0) & in60).sum())
            base = dict(unit=u, regime=reg, goal_no=int(g), model=model, n_h1=n1, n_h0=n0, eligible=(n1 >= 200) & (n0 >= 200))
            if not base["eligible"]:
                rows_out.append(dict(base, variant="primary", subset="all"))
                continue
            norep = ~rep[srow[rows["B"]]]
            variants = [("primary", "y", {}, None)]
            if model == "bge":
                variants += [("bins30", "y", dict(bins=np.arange(0, 31, 10.0)), None),
                             ("latmatch", "y", dict(lat_match=True), None),
                             ("raw", "y_raw", {}, None),
                             ("dedupe", "y", {}, norep)]
            for vname, yname, kw, extra in variants:
                for sub, sel in (("all", None), ("named", rows["ment"]), ("unnamed", ~rows["ment"])):
                    if vname not in ("primary", "dedupe") and sub != "all" and model == "bge" and vname != "latmatch":
                        continue
                    s = np.ones(len(rows["h"]), bool) if sel is None else sel.copy()
                    if extra is not None:
                        s &= extra
                    mj = R2.matched_age_jump(rows, U, yname, sel=s, nboot=NBOOT, seed=7, **kw)
                    r = dict(base, variant=vname, subset=sub, n_blocks=mj["n_blocks"],
                             naive=R2.unmatched_contrast(rows, yname, s))
                    for hi, h in enumerate((1, 2, 3)):
                        r[f"J{h}"], r[f"J{h}_lo"], r[f"J{h}_hi"], r[f"J{h}_se"] = (float(mj["J"][hi]), float(mj["lo"][hi]),
                                                                                    float(mj["hi"][hi]), float(mj["se"][hi]))
                        r[f"n{h}"] = float(mj["n_h"][hi + 1])
                    r["n0"] = float(mj["n_h"][0])
                    rows_out.append(r)
            if model == "bge":
                profiles[u] = dict(regime=reg, all=R2.hop_profile(rows, "y"), named=R2.hop_profile(rows, "y", rows["ment"]),
                                   unnamed=R2.hop_profile(rows, "y", ~rows["ment"]))
        p = [x for x in rows_out if x["unit"] == u and x["model"] == "bge" and x["variant"] == "primary" and x["subset"] == "all"]
        if p and p[0].get("J1") is not None:
            print(f"{u} ({reg}) bge J1 {p[0]['J1']:.4f} [{p[0]['J1_lo']:.4f}, {p[0]['J1_hi']:.4f}] n1 {p[0]['n_h1']} n0 {p[0]['n_h0']}", flush=True)
        else:
            print(f"{u} ({reg}) not eligible", flush=True)
    df = pl.DataFrame(rows_out, infer_schema_length=None)
    df.write_parquet(OUT / "r2/content_units.parquet")
    # pooled by regime (IVW over eligible units)
    summ = {}
    for (model, variant, sub), g in df.filter(pl.col("eligible")).group_by(["model", "variant", "subset"]):
        for reg in ("I", "II", "III"):
            s = g.filter(pl.col("regime") == reg)
            if not len(s) or "J1" not in s.columns:
                continue
            key = f"{model}|{variant}|{sub}|{reg}"
            d = dict(n_units=len(s))
            for h in (1, 2, 3):
                m, se = R2.ivw(s[f"J{h}"].to_numpy(), s[f"J{h}_se"].to_numpy())
                d[f"J{h}"], d[f"J{h}_se"] = m, se
                d[f"J{h}_pos"] = int((s[f"J{h}_lo"] > 0).sum())
                d[f"J{h}_neg"] = int((s[f"J{h}_hi"] < 0).sum())
            d["naive_median"] = float(s["naive"].median())
            summ[key] = d
    (OUT / "r2/content_summary.json").write_text(json.dumps(dict(pooled=summ, profiles=profiles), indent=1))
    for k in sorted(summ):
        if "|primary|" in k or "|dedupe|" in k or "|latmatch|" in k:
            d = summ[k]
            print(k, f"units {d['n_units']} J1 {d['J1']:.4f}±{1.96 * d['J1_se']:.4f} (+{d['J1_pos']}/-{d['J1_neg']}) "
                     f"J2 {d['J2']:.4f}±{1.96 * d['J2_se']:.4f} J3 {d['J3']:.4f}±{1.96 * d['J3_se']:.4f} naive {d['naive_median']:.4f}")


if __name__ == "__main__":
    main()
