"""H91 synthetic validation (axis F) at village counts, before any real-data rotation statistic.

Content days: N in {4, 8, 16, 32}, W in {4, 8, 16} windows x 32 dims, fill 0.75, AR(1) window persistence
rho_w in {0, 0.5}; loadings = uniform market factor (a = 0.4) + one factor per room (two rooms, b = 0.4; b = 0.25 for
the weak variant). Scenarios per day pair (a -> b):
  S0  stationary (same loadings)                          -> size of p_rot < 0.05; trailing-alarm FAR
  S1  regrouping (half of each room swaps rooms on b)      -> power of z_rot >= 2; AUC vs S0; alarm hit rate
  S2  mid-day uniform topic step on b (field step inside the day, before agent-day centering) -> must stay near S0
  S3  market strength 0.4 -> 0.7 on b, eigenvectors fixed -> must stay near S0
Talk days: N as above, L in {120, 240, 480} kept minutes, talk rate 0.1, minute persistence 0.7 (H12's calibration), market 0.3, room 0.4;
S0, S1, S3.
Output: data/processed/H91-eigenvector-rotation-signal/synthetic/{pairs.parquet, summary.parquet, summary.json}
Usage: uv run python hypotheses/H91-eigenvector-rotation-signal/analysis/synthetic.py [--pairs 60] [--R 99]
"""
from __future__ import annotations

import argparse
import json
import time

import numpy as np
import polars as pl

import h91lib as L

DM = L.DM
RHO_T = 0.7   # minute persistence of the latent talk drive (H12 Amendment 1 calibration: 0.6-0.7)


def content_pair(rng, N, W, scen, rho_w, b_room, R):
    rooms = np.arange(N) % 2
    la = DM.room_loads(N, 0.4, b_room, rooms)
    if scen == "S1":
        rb = rooms.copy()
        for r in (0, 1):
            idx = np.flatnonzero(rooms == r)
            sw = rng.choice(idx, max(1, len(idx) // 2), replace=False)
            rb[sw] = 1 - r
        lb = DM.room_loads(N, 0.4, b_room, rb)
    elif scen == "S3":
        lb = DM.room_loads(N, 0.7, b_room, rooms)
    else:
        lb = la
    Za = DM.synth_content_day(rng, N, W, la, rho_w)
    if scen == "S2":
        # mid-day uniform field step: the same vector added to every agent from the middle window on, then re-center
        Zr = DM.synth_content_day(rng, N, W, lb, rho_w)
        pres = np.abs(Zr).sum(2) > 0
        u = rng.standard_normal(DM.D); u *= 1.0 * np.sqrt(DM.D) / np.linalg.norm(u)
        step = (np.arange(W) >= W // 2)[None, :, None] * u[None, None, :]
        X = (Zr + step) * pres[:, :, None]
        mu = X.sum(1) / pres.sum(1)[:, None]
        Zb = (X - mu[:, None, :]) * pres[:, :, None]
    else:
        Zb = DM.synth_content_day(rng, N, W, lb, rho_w)
    return L.rot_content(Za, Zb, rng, R=R)


def spin_pair(rng, N, Lm, scen, R):
    rooms = np.arange(N) % 2
    la = DM.room_loads(N, 0.3, 0.4, rooms)
    if scen == "S1":
        rb = rooms.copy()
        for r in (0, 1):
            idx = np.flatnonzero(rooms == r)
            rb[rng.choice(idx, max(1, len(idx) // 2), replace=False)] = 1 - r
        lb = DM.room_loads(N, 0.3, 0.4, rb)
    elif scen == "S3":
        lb = DM.room_loads(N, 0.6, 0.4, rooms)
    else:
        lb = la
    Sa = DM.synth_spin_day(rng, N, Lm, la, rho_t=RHO_T); Sb = DM.synth_spin_day(rng, N, Lm, lb, rho_t=RHO_T)
    m = np.arange(Lm)
    return L.rot_spins(Sa, m, Sb, m, rng, R=R)


def alarm_rates(z0: np.ndarray, z1: np.ndarray, rng, reps: int = 400):
    """Trailing alarm on sequences of 10 stationary pairs followed by one test pair (S0 -> FAR, S1 -> hit)."""
    far, hit = [], []
    for _ in range(reps):
        base = rng.choice(z0, 10)
        far.append(L.trailing_z(np.append(base, rng.choice(z0)))[-1] >= L.THRESH)
        hit.append(L.trailing_z(np.append(base, rng.choice(z1)))[-1] >= L.THRESH)
    return float(np.mean(far)), float(np.mean(hit))


SCORES = {"split": "z{k}_split", "boot": "z{k}_boot", "raw": "d{k}"}
KEYS = ["channel", "N", "W", "L", "rho", "b_room"]


def summarize(df, rng):
    summ = []
    for cell, g in df.group_by(KEYS, maintain_order=True):
        rec = dict(zip(KEYS, cell))
        g0 = g.filter(pl.col("scen") == "S0")
        for k in (1, 2):
            for nm in ("split", "boot"):
                rec[f"size_{nm}_k{k}"] = float(np.mean(g0[f"p{k}_{nm}"].to_numpy() < 0.05))
            for sc, col in SCORES.items():
                c = col.format(k=k)
                z0 = g0[c].to_numpy()
                for s in ("S1", "S2", "S3"):
                    gs = g.filter(pl.col("scen") == s)
                    if not gs.height:
                        continue
                    zs = gs[c].to_numpy()
                    rec[f"auc_{s}_{sc}_k{k}"] = L.auc(zs, z0)
                    if sc != "raw":
                        rec[f"rej_{s}_{sc}_k{k}"] = float(np.mean(gs[f"p{k}_{sc}"].to_numpy() < 0.05))
                    if s == "S1":
                        far, hit = alarm_rates(z0, zs, rng)
                        rec[f"far_{sc}_k{k}"], rec[f"hit_{sc}_k{k}"] = far, hit
        summ.append(rec)
    return summ


def show(sm):
    pl.Config.set_tbl_rows(200); pl.Config.set_tbl_cols(40); pl.Config.set_tbl_width_chars(260)
    cols = KEYS + ["size_split_k2", "size_boot_k2", "rej_S1_boot_k2", "auc_S1_split_k2", "auc_S1_boot_k2", "auc_S1_raw_k2",
                   "auc_S2_boot_k2", "auc_S3_boot_k2", "auc_S2_raw_k2", "auc_S3_raw_k2", "far_raw_k2", "hit_raw_k2",
                   "far_boot_k2", "hit_boot_k2"]
    print(sm.select([c for c in cols if c in sm.columns]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", type=int, default=60)
    ap.add_argument("--R", type=int, default=99)
    a = ap.parse_args()
    rng = np.random.default_rng(L.SEED)
    out = L.OUT / "synthetic"; out.mkdir(parents=True, exist_ok=True)
    rows = []
    t0 = time.time()
    for N in (4, 8, 16, 32):
        for W in (4, 8, 16):
            for rho in (0.0, 0.5):
                for b_room in (0.4, 0.25):
                    for scen in ("S0", "S1", "S2", "S3"):
                        if b_room == 0.25 and scen in ("S2", "S3"):
                            continue
                        for i in range(a.pairs):
                            r = content_pair(rng, N, W, scen, rho, b_room, a.R)
                            rows.append({"channel": "content", "N": N, "W": W, "L": None, "rho": rho, "b_room": b_room,
                                         "scen": scen, **r})
        print(f"content N={N} done ({time.time() - t0:.0f}s)", flush=True)
        for Lm in (120, 240, 480):
            for scen in ("S0", "S1", "S3"):
                for i in range(a.pairs):
                    r = spin_pair(rng, N, Lm, scen, a.R)
                    rows.append({"channel": "talk", "N": N, "W": None, "L": Lm, "rho": RHO_T, "b_room": 0.4, "scen": scen, **r})
        print(f"talk N={N} done ({time.time() - t0:.0f}s)", flush=True)
    df = pl.DataFrame(rows, infer_schema_length=None)
    df.write_parquet(out / "pairs.parquet", compression="zstd")
    summ = summarize(df, rng)
    sm = pl.DataFrame(summ, infer_schema_length=None)
    sm.write_parquet(out / "summary.parquet", compression="zstd")
    (out / "summary.json").write_text(json.dumps({"pairs_per_cell": a.pairs, "R": a.R, "cells": summ}, indent=1, default=float))
    show(sm)
    print(f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
