"""H107 round 1 (exploratory, non-holdout): onset ratio, onset direction, half-day profile, inherited repo and carried
content fields, work persistence, the G41 re-split memory test; both embedding models, style_resid and white32, and a
no-constants variant.

Writes data/processed/H107-room-split-onset/results/{raw_all.json}.
Usage: uv run python hypotheses/H107-room-split-onset/analysis/run.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h107lib as L  # noqa: E402
import rslib as R  # noqa: E402

RES = L.DATA / "results"
VARIANTS = [("bge_small", "style_resid", True), ("gte_modernbert", "style_resid", True),
            ("bge_small", "white32", True), ("gte_modernbert", "white32", True), ("bge_small", "style_resid", False)]


def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.ndarray):
        return clean(o.tolist())
    if isinstance(o, float) and not np.isfinite(o):
        return None
    return o


def one(st, rm, arp, model, variant, use_consts, boot):
    V = R.load_vectors(model, variant)
    ad, Xc = R.day_centered_agent_days(st, V, R.REG3 + [33, 35])
    out = {"model": model, "variant": variant, "constants": use_consts, "periods": {}}
    for P in R.PERIODS:
        t0 = time.time()
        consts = R.constants(ad, Xc, exclude={P, R.PRE[P]}) if (use_consts and P != 35) else None
        pday = R.build_panel(st, V, P, "day", consts, halves=True)
        phalf = R.build_panel(st, V, P, "half", consts)
        res = L.onset(pday, phalf, n_perm=2000, seed=P)
        res["days"] = pday.days
        res["agents"] = [int(a) for a in pday.agents]; res["labels"] = [int(x) for x in pday.lab]
        if boot:
            res["ci"] = L.onset_boot(pday, phalf, n_boot=200, n_perm=200, seed=P)
        if P != 35:
            u, info = L.inherited_repo_field(st, V, rm, arp, P, pday.agents, pday.lab)
            res["repo_field_info"] = info
            if u is not None:
                res["repo"] = L.field_alignment(pday, u, n_null=2000, seed=P + 1)
            cprev = R.constants(ad, Xc, exclude={P, R.PRE[P]}) if use_consts else {}
            up, pinfo = L.carried_content_field(ad, Xc, cprev, P, pday.agents, pday.lab)
            res["prev_field_info"] = pinfo
            if up is not None:
                res["prev"] = L.field_alignment(pday, up, n_null=2000, seed=P + 2)
        res["kappa_w"] = L.kappa_w(arp, P, pday.agents, pday.lab)
        res["seconds"] = round(time.time() - t0, 1)
        out["periods"][f"G{P}"] = res
        print(model, variant, use_consts, P, {k: (round(res[k], 3) if isinstance(res.get(k), float) else res.get(k))
                                               for k in ("r1", "pi1", "c1", "p_F", "r_h0")}, flush=True)
    if use_consts:
        c41 = R.constants(ad, Xc, exclude={41, 40}); c39 = R.constants(ad, Xc, exclude={39, 38})
        out["resplit_G41"] = L.resplit_memory(st, V, c41, c39)
    return clean(out)


def main():
    RES.mkdir(parents=True, exist_ok=True)
    st = L.load_inputs()
    rm = pl.read_parquet(L.DATA / "repo_mentions.parquet")
    arp = pl.read_parquet(L.DATA / "agent_repo_period.parquet")
    allr = {}
    for model, variant, use_consts in VARIANTS:
        boot = variant == "style_resid" and use_consts
        key = f"{model}/{variant}" + ("" if use_consts else "/noconst")
        allr[key] = one(st, rm, arp, model, variant, use_consts, boot)
        (RES / "raw_all.json").write_text(json.dumps(allr, indent=1))
        print("done", key, flush=True)


if __name__ == "__main__":
    main()
