"""H92: next-day forecasts of the agent correlation matrix with seven estimators, every non-holdout unit and channel.

For each unit (period_units, non-holdout), each target day j >= 1 of the unit and each training window (expanding:
all earlier days of the unit; prev: the previous day only), agents = eligible on the target day and on >= 50% of the
training days (N >= 4). Estimators E0-E6 (h92lib), the calibrated edge from 49 surrogates of the training data
(content: within-day circular window shifts; spins: DQ8 trimmed 30-min block shift). Score: off-diagonal MSE against
the realized target-day matrix; room contrast (within minus between modal rooms) per estimator and realized.
Channels: content_bge, content_gte (primary), *_style_resid_period (variant), talk, act.
Output: data/processed/H92-rmt-cleaned-forecast/forecasts.parquet
Usage: uv run python hypotheses/H92-rmt-cleaned-forecast/analysis/run_forecast.py
"""
from __future__ import annotations

import time
import zlib

import numpy as np
import polars as pl

import h92lib as L

DM = L.DM
CHANNELS = ["content_bge", "content_gte", "content_bge_style_resid_period", "content_gte_style_resid_period", "talk", "act"]


def load_channel(ch: str) -> dict:
    return DM.load_days(L.OUT / ("spins.npz" if ch in ("talk", "act") else f"{ch}.npz"))


def run(channels=CHANNELS, loader=load_channel, keep_unit=lambda u: True, seed_tag: str = "") -> pl.DataFrame:
    t0 = time.time()
    cal = DM.calendar()
    unit_of = dict(zip(cal["pt_date"].to_list(), cal["unit_id"].to_list()))
    rooms = pl.read_parquet(L.OUT / "rooms.parquet")
    rows = []
    for ch in channels:
        spin = ch in ("talk", "act")
        days = loader(ch)
        units: dict = {}
        for d in days:
            if unit_of.get(d) is not None and keep_unit(unit_of[d]):
                units.setdefault(unit_of[d], []).append(d)
        for u, dl in units.items():
            dl = sorted(dl)
            for j in range(1, len(dl)):
                tgt = days[dl[j]]
                ok_t = tgt["agents"][tgt[f"{ch}_ok"]] if spin else tgt["agents"]
                for var, tr_days in (("expand", dl[:j]), ("prev", dl[j - 1:j])):
                    cnt = {}
                    for d in tr_days:
                        rec = days[d]
                        ag = rec["agents"][rec[f"{ch}_ok"]] if spin else rec["agents"]
                        for a in ag:
                            cnt[a] = cnt.get(a, 0) + 1
                    agents = np.array(sorted(a for a in ok_t if cnt.get(a, 0) >= 0.5 * len(tr_days)))
                    if len(agents) < DM.MIN_AGENTS:
                        continue
                    rng = np.random.default_rng(zlib.crc32(f"{seed_tag}{ch}|{u}|{dl[j]}|{var}".encode()) + L.SEED)
                    tr, mins = [], []
                    for d in tr_days:
                        rec = days[d]
                        if spin:
                            S = DM.standardize(rec[ch])
                            ok = rec[f"{ch}_ok"]
                            A = np.zeros((len(agents), S.shape[1]))
                            for i, a in enumerate(agents):
                                k = np.searchsorted(rec["agents"], a)
                                if k < len(rec["agents"]) and rec["agents"][k] == a and ok[k]:
                                    A[i] = S[k]
                            tr.append(A); mins.append(rec["minutes"])
                        else:
                            Z = rec["Z"]
                            A = np.zeros((len(agents),) + Z.shape[1:])
                            for i, a in enumerate(agents):
                                k = np.searchsorted(rec["agents"], a)
                                if k < len(rec["agents"]) and rec["agents"][k] == a:
                                    A[i] = Z[k]
                            tr.append(A)
                    if spin:
                        X = L.spins_X(tr); edge = L.edge_spins(tr, mins, rng)
                        it = np.searchsorted(tgt["agents"], agents)
                        Q = DM.corr(DM.standardize(tgt[ch][it]))
                        size_t = int(tgt[ch].shape[1])
                    else:
                        X = L.content_X(tr, None); edge = L.edge_content(tr, rng)
                        it = np.searchsorted(tgt["agents"], agents)
                        Q = DM.overlap(tgt["Z"][it])
                        size_t = int(tgt["Z"].shape[1])
                    est = L.all_estimates(X, edge)
                    rm = rooms.filter(pl.col("pt_date") == dl[j])
                    rmap = dict(zip(rm["agent"].to_list(), rm["room"].to_list()))
                    rv = np.array([rmap.get(int(a), -1) for a in agents])
                    rec_out = {"channel": ch, "unit_id": u, "pt_date": dl[j], "variant": var, "n_train_days": len(tr_days),
                               "size_target": size_t, "n_rooms": int(len(set(rv[rv >= 0]))), **est["_meta"],
                               "cont_real": L.room_contrast(Q, rv)}
                    for k in L.EST:
                        rec_out[f"mse_{k}"] = L.mse_off(est[k], Q)
                        rec_out[f"cont_{k}"] = L.room_contrast(est[k], rv)
                    rows.append(rec_out)
        print(f"{ch}: {sum(1 for r in rows if r['channel'] == ch)} forecasts ({time.time() - t0:.0f}s)", flush=True)
    df = pl.DataFrame(rows, infer_schema_length=None)
    return df.join(cal.select("pt_date", "goal_no", "regime"), on="pt_date", how="left")


def main():
    t0 = time.time()
    df = run()
    df.write_parquet(L.OUT / "forecasts.parquet", compression="zstd")
    print(f"done: {df.height} rows in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
