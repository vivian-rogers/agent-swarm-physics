"""H99 round 2 drivers shared by the synthetic validation and the real run: unit loading, minute-grid removal
variants (V0-V5), minute statistics with the room partition, and the call-clock kernel (R1).
"""
from __future__ import annotations

import datetime as dt
import math
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r2lib as R  # noqa: E402

ROOT = HERE.parents[2]
BASE = ROOT / "data/processed/H99-glauber-fluctuation-relaxation"
R2 = BASE / "r2"
SH = ROOT / "data/processed/shared"
EPOCH = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)
EDGE = 30
EXO_MIN = 15
NUDGE_MIN = 5          # Amendment B1: nudges mask 5 min swarm-wide (strict variant V3s/V5s keeps 15 min for all)
KICKOFF_MIN = 60


def load_unit(uid):
    meta = pl.read_parquet(R2 / "unit_meta.parquet").filter(pl.col("unit_id") == uid).to_dicts()[0]
    calls = pl.read_parquet(R2 / "calls" / f"{uid}.parquet")
    msgs = pl.read_parquet(R2 / "msgs" / f"{uid}.parquet")
    exo = pl.read_parquet(R2 / "exo" / f"{uid}.parquet")
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "win_start", "holdout"])
    assert not cal.filter(pl.col("pt_date").is_in(meta["days"]) & pl.col("holdout").fill_null(False)).height
    wsd = dict(zip(cal["pt_date"].to_list(), ((cal["win_start"] - EPOCH).dt.total_microseconds() / 1e6).to_list()))
    ws_by_day = {k: wsd[d] for k, d in enumerate(meta["days"])}
    return meta, calls, msgs, exo, ws_by_day


def exo_masks(exo, ws_by_day, day_idx, L, nudge_min=NUDGE_MIN):
    """V3 mask (True = drop): [m, m + 15] after any human/nudge/operator message; window start to kickoff + 60 min."""
    m = np.zeros(L, bool)
    e = exo.filter(pl.col("day") == day_idx)
    if not e.height:
        return m
    ws = ws_by_day[day_idx]
    for t, k in zip(e["t"].to_list(), e["kind"].to_list()):
        mm = int((t - ws) // 60)
        if k == "goal_kickoff":
            m[:max(0, min(L, mm + KICKOFF_MIN + 1))] = True
        elif 0 <= mm < L:
            m[mm:min(L, mm + (nudge_min if k == "nudge" else EXO_MIN) + 1)] = True
    return m


def edge_mask(keep):
    idx = np.flatnonzero(keep)
    m = np.zeros(len(keep), bool)
    if len(idx) > 2 * EDGE + 30:
        m[idx[:EDGE]] = True
        m[idx[-EDGE:]] = True
    else:
        m[:] = True
    return m


def variants(talk, keep, actonly, expect, rooms, exo, ws_by_day, day_ids):
    """Minute-grid removal stack (Amendment B1). Centring always uses the full kept 30-min blocks; masks (V2, V3) only
    remove minutes from the sums. Returns {variant: (Xs, oks, rooms)}.
      V0 round-1 centring; V1 talk minus its call-skeleton expectation E (r2lib.expect_grid), then centred;
      V2 edge buffer; V3 exogenous mask; V4 leave-one-out act-only field regression; V5 = V1 + V2 + V3 + V4."""
    X0, ok0, X1 = [], [], []
    for S, kp, E in zip(talk, keep, expect):
        a, b = R.center(S, kp)
        X0.append(a); ok0.append(b)
        X1.append(R.center(np.asarray(S, float) - E, kp)[0])
    m2 = [~edge_mask(kp) for kp in keep]
    m3 = [~exo_masks(exo, ws_by_day, d, len(kp)) for kp, d in zip(keep, day_ids)]
    ok2 = [o & m for o, m in zip(ok0, m2)]
    ok3 = [o & m for o, m in zip(ok0, m3)]
    ok5 = [o & a & b for o, a, b in zip(ok0, m2, m3)]
    m3s = [~exo_masks(exo, ws_by_day, d, len(kp), nudge_min=EXO_MIN) for kp, d in zip(keep, day_ids)]
    ok3s = [o & m for o, m in zip(ok0, m3s)]
    ok5s = [o & a & b for o, a, b in zip(ok0, m2, m3s)]
    V = {"V0": (X0, ok0), "V1": (X1, ok0), "V2": (X0, ok2), "V3": (X0, ok3),
         "V4": (R.resid_actfield(X0, ok0, actonly), ok0), "V5": (R.resid_actfield(X1, ok5, actonly), ok5),
         "V3s": (X0, ok3s), "V5s": (R.resid_actfield(X1, ok5s, actonly), ok5s)}
    return {k: (v[0], v[1], rooms) for k, v in V.items()}


def minute_stats(V, rng, B=400, pairs=("V0", "V5")):
    out = {}
    for k, (Xs, oks, rooms) in V.items():
        rows = R.sums_X(Xs, oks)
        b = R.boot_X(rows, B=B, rng=rng)
        out.update({f"{k}_{s}": v for s, v in b.items()})
        if k in pairs:
            ps = R.pair_sums(Xs, oks, rooms)
            if len(ps) and ps[:, 3].sum() > 0 and ps[:, 1].sum() > 0:
                pb = R.pair_boot(ps, B=B, rng=rng)
                out.update({f"{k}_pair_{s}": v for s, v in pb.items()})
    return out


def r1_stats(calls, msgs, meta, rng, B=200):
    D = R.call_design(calls, msgs)
    tr = D.filter(pl.col("trim"))
    tmin, tmax = tr["t"].min(), tr["t"].max()
    m_tr = msgs.filter(pl.col("t").is_between(tmin, tmax)).height if tr.height else 0
    out = R.kernel_summary(D, m_tr, int(tr["talk"].sum()), meta["r_bar"], B=B, seed=int(rng.integers(1 << 30)))
    rs = R.rho_self(D)
    e, lo, hi, se = R.ratio_boot(rs, rng=rng) if len(rs) else (np.nan,) * 4
    out.update({"rho_s": e, "rho_s_lo": lo, "rho_s_hi": hi, "rho_s_se": se})
    return out, D


def call_grid_variants(calls, exo, ws_by_day):
    G = R.call_grid(calls, ws_by_day)
    return variants(G["talk"], G["keep"], G["actonly"], G["expect"], G["rooms"], exo, ws_by_day, G["days"])


def round1_grid_variants(uid, meta, calls, exo, ws_by_day):
    """The round-1 activity_bins grid (grids/<unit>.npz) with occupancy and act-only from the call skeleton."""
    z = np.load(BASE / "grids" / f"{uid}.npz")
    dmap = {d: k for k, d in enumerate(meta["days"])}
    talk, keep, act, occ, rooms, dids = [], [], [], [], [], []
    for k, d in enumerate([str(x) for x in z["days"]]):
        T, A, kp = z[f"talk_{k}"], z[f"act_{k}"], z[f"keep_{k}"]
        ags = list(z[f"agents_{k}"])
        di = dmap[d]
        L = T.shape[1]
        E = R.expect_grid(calls.filter(pl.col("day") == di), ags, L)
        talk.append(T); keep.append(kp); act.append((A > 0) & (T == 0)); occ.append(E)
        rooms.append(np.asarray(z[f"rooms_{k}"])); dids.append(di)
    return variants(talk, keep, [a.astype(np.int8) for a in act], occ, rooms, exo, ws_by_day, dids)
