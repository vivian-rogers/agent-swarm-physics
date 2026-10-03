"""Shared loading and model registry for the H03 analysis scripts."""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
from pathlib import Path

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
import hawkes_core as hc  # noqa: E402

DATA = ROOT / "data/processed/H03-self-excited-criticality"
FIG = HERE.parent / "figures"
FITS = DATA / "fits"
N_WORKERS = 3
BETA_STARTS = [1 / 5, 1 / 30, 1 / 300, 1 / 3000]
MODE_ORDER = ["F", "I", "K", "M", "C", "P"]
# reference categorical palette (dataviz skill), fixed order; >3 categories in scatters -> marker shape is the
# secondary encoding and points carry goal-number labels
MODE_COLORS = {"C": "#2a78d6", "F": "#eb6834", "I": "#1baf7a", "K": "#eda100", "M": "#e87ba4", "P": "#4a3aa7"}
MODE_MARKERS = {"C": "o", "F": "s", "I": "^", "K": "D", "M": "v", "P": "*"}
MODE_NAMES = {"C": "C shared objective", "F": "F free / holiday", "I": "I individual objectives",
              "K": "K competition", "M": "M teams", "P": "P private roles (#51)"}
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"


def load():
    days = pl.read_parquet(DATA / "days.parquet")
    ev = pl.read_parquet(DATA / "events.parquet")
    exo = pl.read_parquet(DATA / "exo.parquet")
    holdout = json.loads((ROOT / "hypotheses/holdout.json").read_text())
    held = set(holdout["goal_periods_held_out"])
    assert not (set(days["goal_no"].unique().to_list()) & held), "holdout goal leaked"
    for w in holdout["ne_windows"]:
        bad = days.filter((pl.col("pt_date") >= w["start"]) & (pl.col("pt_date") < w["end"]))
        assert bad.height == 0, f"holdout window {w['id']} leaked"
    return days, ev, exo


def specs():
    """Model registry: name -> (Spec, fixed-cross flag)."""
    S = hc.Spec
    return {
        "M1_B2": S("B2"),                                  # primary
        "M1_B0": S("B0", exo=False, kick=False),           # naive constant baseline (Filimonov-Sornette trap)
        "M1_B1": S("B1"),
        "M1_B3": S("B3"),
        "M1_B2_noexo": S("B2", exo=False),
        "P_B2": S("B2", kernel="none"),                    # inhomogeneous Poisson null (same baseline + exo)
        "P_B0": S("B0", exo=False, kick=False, kernel="none"),
        "P_B1": S("B1", kernel="none"),
        "P_B3": S("B3", kernel="none"),
        "M2_grid": S("B2", kernel="grid"),
        "M2_pl": S("B2", kernel="powerlaw"),
        "M3_sc": S("B2a", kernel="selfcross"),
        "M3_self": S("B2a", kernel="selfcross"),           # cross weights fixed at 0 (scheduler-only rival)
        "P_B2a": S("B2a", kernel="none"),
    }


def self_only_start(ds: "hc.Dataset", p=None):
    """Start vector + fixed mask with all cross-kernel weights pinned at ~0."""
    sl, P = ds.layout()
    p = ds.init_params() if p is None else p.copy()
    fixed = np.zeros(P, bool)
    for j, nm in enumerate(ds.names):
        if nm.startswith("cross"):
            p[sl["w"].start + j] = -30.0
            fixed[sl["w"].start + j] = True
    return p, fixed


def fit_model(name, ds, p0=None, beta_starts=BETA_STARTS):
    if name == "M3_self":
        p, fixed = self_only_start(ds, p0)
        return ds.fit(p0=p, fixed=fixed)
    if ds.free_beta:
        return ds.fit(p0=p0, beta_starts=beta_starts)
    return ds.fit(p0=p0)


def period_meta(days, keys):
    sub = days.filter(pl.col("day_id").is_in(keys))
    return {"n_days": sub.height, "N_active": float(sub["n_active"].mean()),
            "hours": float(sub["T_s"].median() / 3600), "regime": "/".join(sorted(set(sub["regime"].to_list()))),
            "mode": sub["mode"][0], "first_date": sub["pt_date"].min(), "last_date": sub["pt_date"].max()}


def write_provenance(extra: dict):
    path = DATA / "_provenance.json"
    prov = json.loads(path.read_text()) if path.exists() else {}
    prov.setdefault("analysis_outputs", {}).update(
        {k: {**v, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()} for k, v in extra.items()})
    path.write_text(json.dumps(prov, indent=1, default=str))
