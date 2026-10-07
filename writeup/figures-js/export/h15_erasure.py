"""H15 context erasure (Fig. erasure): work commits per call around forced vs voluntary context erasures.

    uv run python writeup/figures-js/export/h15_erasure.py

Round-1b data (H15 card, NE41; the paper's numbers): context-ledger calls in regime III with DQ4 work commits mapped
to calls (data/processed/H15-semantic-information-scrambles/r1b/calls.parquet, column w) and the classified
consolidations (r1b/consolidations.parquet: CF = forced by the 41-call cap, CV = voluntary, segment >= 10 calls).

The profile is the round-1b build's own profile (scheme/build.py, r1b branch: calls -20..-1 of the erased segment,
+1..+20 of the new one, mean work commits per call, pooled over the nine units). It is recomputed here because the
stored r1b/consolidation_profile.parquet groups by the call kind instead of CF/CV (a column-name clash in that
build's join: the call table's own `kind` wins); calls.parquet has no call-kind column, so the clash cannot recur.

The printed dip (-39% [-42, -35], 7/9 periods) is read from r1b/r1b_extra.json (CTX_meta.CF_w: random-effects pool of
the per-period ratio dips, calls +1..+10 vs -20..-11), not recomputed. All rows are non-reserved (the build refuses
reserved days; asserted again here with holdout_mask).
"""
from __future__ import annotations

import json

import polars as pl

from common import ROOT, write


def _shared_common():
    import importlib.util
    spec = importlib.util.spec_from_file_location("shared_common", ROOT / "infra/shared/common.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


holdout_mask = _shared_common().holdout_mask

H = ROOT / "data/processed/H15-semantic-information-scrambles/r1b"


def profile():
    tt = pl.read_parquet(H / "calls.parquet").with_columns((pl.col("seg_len") - pl.col("pos")).alias("rpos"))
    ce = pl.read_parquet(H / "consolidations.parquet", columns=["agent", "t", "pt_date", "goal_no", "unit", "kind"])
    days = ce.select("pt_date", "goal_no").unique()
    assert not any(holdout_mask(days["pt_date"].to_list(), days["goal_no"].to_list())), "reserved consolidation day"
    cdays = tt["pt_date"].unique().to_list()
    gmap = dict(zip(days["pt_date"].to_list(), days["goal_no"].to_list()))
    assert not any(holdout_mask(cdays, [gmap.get(d, -1) for d in cdays])), "reserved call day"
    ck = ce.select("agent", "pt_date", pl.col("t").alias("tc"), pl.col("kind").alias("ekind"), "unit")
    segk = (tt.filter(pl.col("reset_consol") & (pl.col("pos") == 0)).select("agent", "pt_date", "seg", pl.col("t_call").alias("tc"))
            .join(ck, on=["agent", "pt_date", "tc"], how="inner"))
    key = segk.select("agent", "pt_date", pl.col("seg").alias("cseg"), "ekind", "unit")
    before = (tt.filter(pl.col("rpos") <= 20).with_columns((-pl.col("rpos")).alias("off"), (pl.col("seg") + 1).alias("cseg"))
              .join(key, on=["agent", "pt_date", "cseg"]))
    after = (tt.filter(pl.col("pos") < 20).with_columns((pl.col("pos") + 1).alias("off"), pl.col("seg").alias("cseg"))
             .join(key, on=["agent", "pt_date", "cseg"]))
    allc = pl.concat([before.select("unit", "ekind", "off", "w"), after.select("unit", "ekind", "off", "w")])
    prof = (allc.filter(pl.col("ekind").is_in(["CF", "CV"])).group_by("ekind", "off")
            .agg(pl.col("w").cast(pl.Float64).mean().alias("rate"), pl.len().alias("n")).sort("ekind", "off"))
    nev = segk.group_by("ekind").len()
    return prof, dict(zip(nev["ekind"].to_list(), nev["len"].to_list())), sorted(allc["unit"].unique().to_list())


def main():
    prof, nev, units = profile()
    x = json.loads((H / "r1b_extra.json").read_text())["CTX_meta"]
    cf = x["CF_w"]
    out = {"series": {}}
    for k in ("CF", "CV"):
        p = prof.filter(pl.col("ekind") == k)
        out["series"][k] = [dict(off=int(o), rate=float(r), n=int(n)) for o, r, n in zip(p["off"], p["rate"], p["n"])]
        ref = p.filter(pl.col("off").is_between(-20, -11))["rate"].mean()
        post = p.filter(pl.col("off").is_between(1, 10))["rate"].mean()
        print(f"{k}: events {nev.get(k)}, ref {ref:.4f}, post {post:.4f}, pooled-profile ratio {post / ref - 1:+.3f}")
    out["dip"] = dict(mu=cf["mu"], lo=cf["lo"], hi=cf["hi"], below0=x["CF_w_below0"], k=x["CF_w_k"])
    out["units"] = units
    out["n_events"] = nev
    print("meta CF_w", {k: round(v, 3) for k, v in out["dip"].items()}, "units", units)
    # the paper prints 39% [35, 42], 7/9
    assert (round(-100 * cf["mu"]), round(-100 * cf["hi"]), round(-100 * cf["lo"])) == (39, 35, 42), cf
    write("h15_erasure", out, "writeup/figures-js/export/h15_erasure.py",
          ["data/processed/H15-semantic-information-scrambles/r1b/calls.parquet",
           "data/processed/H15-semantic-information-scrambles/r1b/consolidations.parquet",
           "data/processed/H15-semantic-information-scrambles/r1b/r1b_extra.json"],
          dict(offsets="-20..-1, +1..+20", post="+1..+10", ref="-20..-11", round="r1b"))


if __name__ == "__main__":
    main()
