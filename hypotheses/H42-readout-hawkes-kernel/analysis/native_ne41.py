"""H42 native test NE41: does a forced context erasure cut the read-out kernel's tail?

World B (call-clock) TALK design per regime-III unit. B's tail (calls m >= 1 after the read-out call) is split by what
happened to the recipient's context between the read-out call k1 and the current call k = k1 + m:
  intact    no consolidation in calls k1+1..k
  forced    a forced reset (41-turn cap; ledger reset_forced) in k1+1..k   [quasi-random timing: the intervention]
  voluntary only voluntary consolidations in k1+1..k (agent-chosen; not quasi-random, reported for contrast)
Columns (per item-call counts x the call pulse, compensator = pulse mass x counts): B_0 (read-out call), and
{intact, forced, voluntary} x m-bins {1}, {2-3}, {4-15}; plus a gated "post-reset" call term (first call after any
consolidation) so a talk burst after re-orientation is not credited to (or against) the tail.

Statistic: surviving fraction R = sum_b w_forced,b Z_forced,b / sum_b w_intact,b Z_forced,b (forced item-calls' fitted
excitation over what intact weights would give them, matched on m-bin). Pooled over units as a ratio of sums; grouped
jackknife over unit-days for the SE. Same for voluntary.

Writes data/processed/H42-readout-hawkes-kernel/NE41/ne41.parquet and ne41_summary.json.
"""
from __future__ import annotations

import json
import sys
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import h42lib as L  # noqa: E402

MBINS = ((1, 1), (2, 3), (4, 15))
STAT = ("int", "frc", "vol")
OUT = L.DATA / "NE41"


def split_design(u: L.Unit):
    ds = L.build_talk(u, world="B", specs=(), internals=True)
    m = ds.meta
    G, RF, kstar, pulse, ev_u = m["_G"], m["_RF"], m["_kstar"], m["_pulse"], m["_ev_u"]
    sd, sr, ss, k1, uk = m["_items"]
    n, D = len(kstar), ds.D
    u_day = m["_u_day"]
    names = ["B_0"] + [f"T{s}_{a}" for s in STAT for a, b in MBINS] + ["post"]
    cols = np.zeros((n, len(names)))
    Z = np.zeros((D, len(names)))
    for k in np.unique(uk):
        if G[k] is None:
            continue
        gg, e, Fm, mu, sg = G[k]
        K = len(gg)
        rfF, rfV = RF[k]
        cF = np.concatenate([[0], np.cumsum(rfF)])     # forced resets at calls 0..K-1 (on the call: reset since prev)
        cV = np.concatenate([[0], np.cumsum(rfV)])
        cnt = np.zeros((K, len(names)))
        kk1 = k1[uk == k]
        np.add.at(cnt[:, 0], kk1, 1.0)
        for m_ in range(1, 16):
            kc = kk1 + m_
            ok = kc < K
            a, c = kk1[ok], kc[ok]
            frc = (cF[c + 1] - cF[a + 1]) > 0
            vol = ~frc & ((cV[c + 1] - cV[a + 1]) > 0)
            st = np.where(frc, 1, np.where(vol, 2, 0))
            bi = 0 if m_ == 1 else (1 if m_ <= 3 else 2)
            for s_ in range(3):
                sel = st == s_
                np.add.at(cnt[:, 1 + 3 * s_ + bi], c[sel], 1.0)
        post = (rfF | rfV).astype(float)
        cnt[:, -1] = post
        Z[u_day[k]] += (Fm[:, None] * cnt).sum(0)
        evs = np.where((ev_u == k) & (kstar >= 0))[0]
        cols[evs] = pulse[evs, None] * cnt[kstar[evs]]
    # units with no erasure calls still get the post column from their own resets
    for k in range(len(u_day)):
        if G.get(k) is None or k in set(np.unique(uk)):
            continue
        gg, e, Fm, mu, sg = G[k]
        rfF, rfV = RF[k]
        post = (rfF | rfV).astype(float)
        Z[u_day[k], -1] += (Fm * post).sum()
        evs = np.where((ev_u == k) & (kstar >= 0))[0]
        cols[evs, -1] = pulse[evs] * post[kstar[evs]]
    ds.F = np.column_stack([ds.F, cols])
    ds.Zd = np.column_stack([ds.Zd, Z])
    ds.names = ds.names + names
    for key in list(ds.meta):
        if key.startswith("_"):
            del ds.meta[key]
    return ds


SPECS = {"S0p": L.W_BASE + ("post",), "split": L.W_BASE + ("post", "B", "Tint", "Tfrc", "Tvol")}


def stat_from(ds, f):
    w = dict(zip(f.names, np.exp(f.p[len(f.U_sel) + f.Kb - 1:])))
    Z = dict(zip(ds.names, ds.Zd[f.days].sum(0)))
    out = {}
    for s in ("frc", "vol"):
        num = sum(w.get(f"T{s}_{a}", 0) * Z[f"T{s}_{a}"] for a, b in MBINS)
        den = sum(w.get(f"Tint_{a}", 0) * Z[f"T{s}_{a}"] for a, b in MBINS)
        out[f"num_{s}"], out[f"den_{s}"] = num, den
    out.update({f"w_{k}": v for k, v in w.items() if k.startswith(("T", "B_0", "post"))})
    out.update({f"Z_{k}": v for k, v in Z.items() if k.startswith(("T", "B_0"))})
    return out


def run(uid):
    goal = int("".join(ch for ch in uid if ch.isdigit()))
    u = L.load_unit(uid, goal)
    ds = split_design(u)
    rows = []
    f0 = L.fit_spec(ds, SPECS, "S0p")
    f = L.fit_spec(ds, SPECS, "split", warm=f0)
    r = {"unit_id": uid, "drop_day": -1, "ll": f.ll, "ll0": f0.ll, "n": f.n, **stat_from(ds, f)}
    rows.append(r)
    if ds.D >= 2:
        for d in range(ds.D):
            days = [x for x in range(ds.D) if x != d]
            f0 = L.fit_spec(ds, SPECS, "S0p", days=days)
            f = L.fit_spec(ds, SPECS, "split", days=days, warm=f0)
            rows.append({"unit_id": uid, "drop_day": d, "ll": f.ll, "ll0": f0.ll, "n": f.n, **stat_from(ds, f)})
    return rows


def main():
    units = L.list_units().filter(pl.col("eligible") & (pl.col("regime") == "III")).sort("n_calls", descending=True)
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    with Pool(2, maxtasksperchild=4) as pool:
        for rr in pool.imap_unordered(run, units["unit_id"].to_list()):
            rows += rr
            print(rr[0]["unit_id"], f"Zfrc={sum(rr[0][f'Z_Tfrc_{a}'] for a, b in MBINS):.1f}",
                  f"num={rr[0]['num_frc']:.3f} den={rr[0]['den_frc']:.3f}", flush=True)
    df = pl.DataFrame(rows)
    df.write_parquet(OUT / "ne41.parquet")
    full = df.filter(pl.col("drop_day") == -1)
    summ = {}
    for s in ("frc", "vol"):
        R = full[f"num_{s}"].sum() / max(full[f"den_{s}"].sum(), 1e-12)
        # grouped jackknife over unit-days: replace one unit's full-fit contribution by its drop-one-day fit
        jk = []
        for r in df.filter(pl.col("drop_day") >= 0).iter_rows(named=True):
            fu = full.filter(pl.col("unit_id") == r["unit_id"])
            num = full[f"num_{s}"].sum() - fu[f"num_{s}"][0] + r[f"num_{s}"]
            den = full[f"den_{s}"].sum() - fu[f"den_{s}"][0] + r[f"den_{s}"]
            jk.append(num / max(den, 1e-12))
        jk = np.array(jk)
        G = len(jk)
        se = float(np.sqrt((G - 1) / G * ((jk - jk.mean()) ** 2).sum())) if G > 1 else np.nan
        summ[s] = {"R": float(R), "se": se, "units": int(len(full)), "den": float(full[f"den_{s}"].sum()),
                   "per_unit_R": {r["unit_id"]: (r[f"num_{s}"] / r[f"den_{s}"] if r[f"den_{s}"] > 0 else None)
                                  for r in full.iter_rows(named=True)}}
    summ["tail_intact_share"] = float(full.select(sum(pl.col(f"w_Tint_{a}") * pl.col(f"Z_Tint_{a}") for a, b in MBINS)).sum().item()
                                      / max(full.select(pl.col("w_B_0") * pl.col("Z_B_0")).sum().item() + 1e-12, 1e-12))
    (OUT / "ne41_summary.json").write_text(json.dumps(summ, indent=1, default=float))
    print(json.dumps({k: (v if not isinstance(v, dict) else {kk: vv for kk, vv in v.items() if kk != 'per_unit_R'})
                      for k, v in summ.items()}, indent=1, default=float))


if __name__ == "__main__":
    main()
