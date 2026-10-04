"""H99 replication pipeline (layer 1): per non-holdout unit and channel, the mean-field split estimators with 1-h
block bootstrap CIs, variants, the trimmed block-shift null for g_chi, the content channel, and the talk kick layer.

Channels: talk (primary), activity (control), content (bge primary; gte variant).
Outputs data/processed/H99-glauber-fluctuation-relaxation/results/units.parquet (one row per unit x channel x
variant) and kicks.parquet (talk kick layer).
Usage: uv run python hypotheses/H99-glauber-fluctuation-relaxation/analysis/run.py [--units 27,40]
"""
from __future__ import annotations

import argparse
import sys
import zlib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h99lib as L  # noqa: E402

ROOT = HERE.parents[2]
BASE = ROOT / "data/processed/H99-glauber-fluctuation-relaxation"
B = 400
R_NULL = 19
KICK_MIN = 30
KICK_L = 15
KEEP_COLS = (["g_chi", "g_tau", "dg", "rho_c1", "rho_p1", "tau_c", "tau_p", "tau_c_pred", "K", "dg_ml", "dg_nr",
              "g_chi_nr", "g_tau_nr", "g_tau2", "dg2", "g_tau3", "dg3", "g_tau5", "dg5", "rho_c3", "rho_p3", "drho1",
              "drho2", "rho_c2", "rho_p2"])


def load_grid(unit):
    z = np.load(BASE / "grids" / f"{unit}.npz")
    nd = len(z["days"])
    g = {"days": [str(d) for d in z["days"]]}
    for key in ("talk", "act", "keep", "stall", "agents", "rooms"):
        g[key] = [z[f"{key}_{k}"] for k in range(nd)]
    return g


def summarize(rows, rng, prefix=""):
    b = L.boot(rows, B=B, rng=rng)
    out = {"n_min": b["n_min"], "n_blocks": b["n_blocks"]}
    for k in KEEP_COLS:
        out[k] = b.get(k)
        out[f"{k}_lo"] = b.get(f"{k}_lo")
        out[f"{k}_hi"] = b.get(f"{k}_hi")
        out[f"{k}_se"] = b.get(f"{k}_se")
    return out


def binary_unit(unit, g, chan, rng):
    days = g["talk"] if chan == "talk" else g["act"]
    keeps = g["keep"]
    res = []
    rows = L.binary_sums(days, keeps)
    if len(rows) == 0:
        return res
    main = summarize(rows, rng)
    # block-shift null for g_chi (trimmed grid; DQ8)
    null = []
    for _ in range(R_NULL):
        sd = L.block_shift(days, keeps, rng)
        e = L.estimates(L.binary_sums(sd, keeps).sum(0))
        null.append((e["g_chi"], e["g_tau"], e["dg"], e["dg3"]))
    null = np.array(null, float)
    main["null_g_chi_q95"] = float(np.nanpercentile(null[:, 0], 95))
    main["null_g_chi_p"] = float((1 + (null[:, 0] >= main["g_chi"]).sum()) / (R_NULL + 1))
    main["null_dg3_med"] = float(np.nanmedian(null[:, 3]))
    main["N_med"] = float(np.median([len(a) for a in g["agents"]]))
    res.append({"unit": unit, "channel": chan, "variant": "main", **main})
    # variants: stall-masked, untrimmed
    rs = L.binary_sums(days, keeps, stall=g["stall"])
    if len(rs):
        res.append({"unit": unit, "channel": chan, "variant": "stall", **summarize(rs, rng)})
    full = [np.ones(len(k), bool) for k in keeps]
    ru = L.binary_sums(days, full)
    if len(ru):
        res.append({"unit": unit, "channel": chan, "variant": "untrimmed", **summarize(ru, rng)})
    return res


def content_unit(unit, rng):
    p = BASE / "content" / f"{unit}.npz"
    if not p.exists():
        return []
    z = np.load(p)
    a, d, w = z["agent"], z["day"], z["win"]
    res = []
    for model in ("bge", "gte"):
        V = z[f"vec_{model}"].astype(np.float64)
        for ag in np.unique(a):
            V[a == ag] -= V[a == ag].mean(0)
        # Amendment A1: agent centring only; a leave-in day mean fakes anti-correlation (synthetic_content.py)
        rows = L.content_sums(a, d, w, V)
        if len(rows) < 3:
            continue
        out = summarize(rows, rng)
        out["N_med"] = float(len(np.unique(a)))
        res.append({"unit": unit, "channel": "content", "variant": "main" if model == "bge" else "gte", **out})
    return res


def kick_unit(unit, g, talk_main, rng):
    kp = BASE / "kicks" / f"{unit}.parquet"
    if not kp.exists():
        return None
    k = pl.read_parquet(kp)
    keeps = g["keep"]
    kd = {}
    n_in = 0
    for r in k.iter_rows(named=True):
        if keeps[r["day"]][r["minute"]]:
            kd.setdefault(r["day"], []).append((r["minute"], r["room"]))
            n_in += 1
    if n_in < KICK_MIN:
        return {"unit": unit, "n_kicks": n_in, "ok": False}
    # single-room days: all agents are members (room -1 on kicks or agents)
    rooms = []
    for day_rooms in g["rooms"]:
        rooms.append(day_rooms)
    kd2 = {}
    for day, lst in kd.items():
        ar = rooms[day]
        if len(set(ar[ar >= 0].tolist())) <= 1:
            kd2[day] = [(m, -1) for m, _ in lst]
        else:
            kd2[day] = lst
    pieces = L.kick_kernel(g["talk"], keeps, kd2, rooms, L=KICK_L)
    if len(pieces) < 5:
        return {"unit": unit, "n_kicks": n_in, "ok": False}
    beta = L.kernel_from(pieces)
    tm, peak = L.tail_mean_delay(beta)
    lam = L.geom_ratio(beta)
    draws, b0 = [], []
    for _ in range(400):
        sel = [pieces[i] for i in rng.integers(0, len(pieces), len(pieces))]
        try:
            bb = L.kernel_from(sel)
        except np.linalg.LinAlgError:
            continue
        draws.append(L.geom_ratio(bb))
        b0.append(bb[:2].sum())
    draws = np.array(draws, float)
    draws = draws[np.isfinite(draws)]
    gchi, rp, rc = talk_main["g_chi"], talk_main["rho_p1"], talk_main["rho_c1"]
    rpc = min(max(rp, 1e-3), 0.999) if np.isfinite(rp) else np.nan
    lam_pred = rpc ** (1 - gchi) if np.isfinite(rpc) else np.nan
    return {"unit": unit, "n_kicks": n_in, "ok": True, "peak_lag": peak, "tau_tailmean": tm,
            "lam_kick": lam, "lam_kick_lo": float(np.percentile(draws, 2.5)) if len(draws) > 100 else np.nan,
            "lam_kick_hi": float(np.percentile(draws, 97.5)) if len(draws) > 100 else np.nan,
            "lam_pred_c": lam_pred, "lam_meas_c": rc, "lam_perp": rp,
            "resp01": float(beta[:2].sum()), "resp01_lo": float(np.percentile(b0, 2.5)) if len(b0) > 100 else np.nan,
            "resp01_hi": float(np.percentile(b0, 97.5)) if len(b0) > 100 else np.nan,
            "beta0": float(beta[0]), "beta_peak": float(beta[peak]), "kernel": [float(x) for x in beta]}


def run_unit(unit):
    rng = np.random.default_rng(zlib.crc32(unit.encode()))
    g = load_grid(unit)
    res = []
    for chan in ("talk", "act"):
        res += binary_unit(unit, g, chan, rng)
    res += content_unit(unit, rng)
    tm = next((r for r in res if r["channel"] == "talk" and r["variant"] == "main"), None)
    kick = kick_unit(unit, g, tm, rng) if tm else None
    return res, kick


def kicks_only(units):
    """Recompute only the kick layer from the saved talk rows (Amendment A2 estimator)."""
    U = pl.read_parquet(BASE / "results" / "units.parquet").filter((pl.col("channel") == "talk") & (pl.col("variant") == "main"))
    tm = {r["unit"]: r for r in U.to_dicts()}
    out = []
    for u in units:
        if u in tm:
            out.append(kick_unit(u, load_grid(u), tm[u], np.random.default_rng(zlib.crc32(("k" + u).encode()))))
    return [k for k in out if k]


def save_kicks(kicks):
    import json
    kd = pl.DataFrame([{k: v for k, v in r.items() if k != "kernel"} for r in kicks], infer_schema_length=None)
    kd.write_parquet(BASE / "results" / "kicks.parquet")
    (BASE / "results" / "kick_kernels.json").write_text(json.dumps({r["unit"]: r.get("kernel") for r in kicks}))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", default="")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--kicks-only", action="store_true")
    a = ap.parse_args()
    meta = pl.read_parquet(BASE / "unit_meta.parquet")
    units = a.units.split(",") if a.units else meta["unit_id"].to_list()
    if a.kicks_only:
        save_kicks(kicks_only(units))
        return
    with ProcessPoolExecutor(a.workers) as ex:
        out = list(ex.map(run_unit, units))
    rows = [r for res, _ in out for r in res]
    kicks = [k for _, k in out if k]
    df = pl.DataFrame(rows, infer_schema_length=None).join(
        meta.select("unit_id", "goal_no", "regime", "n_days").rename({"unit_id": "unit"}), on="unit", how="left")
    (BASE / "results").mkdir(parents=True, exist_ok=True)
    df.write_parquet(BASE / "results" / "units.parquet")
    if kicks:
        save_kicks(kicks)
    print(df.filter(pl.col("variant") == "main").select("unit", "channel", "g_chi", "g_tau", "dg", "dg3", "n_min").head(30))


if __name__ == "__main__":
    main()
