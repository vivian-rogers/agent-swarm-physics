"""H67 replication layer: the read-out loop gain on every eligible non-holdout unit, its variants, the equal-time dial
on the same data, the shift null and a heterogeneous (spectral-radius) variant. Writes
data/processed/H67-lagged-criticality-dial/results/units.parquet (one row per unit).

    uv run python hypotheses/H67-lagged-criticality-dial/analysis/run_units.py [--units 40,41] [--workers 4]
"""
from __future__ import annotations

import argparse
import json
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import polars as pl

import h67lib as L

SH = L.ROOT / "data/processed/shared"
N_SHIFT = 19


def het_gain(d: pl.DataFrame, msgs: pl.DataFrame, pooled_J: float) -> float:
    """Spectral radius of K_ij = m_i * J_i * F_ij (F_ij = share of j's in-window messages that i reads at a trimmed
    call; J_i = recipient i's matched-lag jump shrunk to the pooled value with weight n_i / (n_i + median n))."""
    rows = L._rows(d, True)
    ags = sorted(rows["agent"].unique().to_list())
    if len(ags) < 3:
        return np.nan
    J, n = {}, {}
    for a in ags:
        r = L.fit(rows.filter(pl.col("agent") == a).with_columns(pl.lit(True).alias("trim")), msgs, "main", True, B=0)
        if r.get("ok") and np.isfinite(r.get("J1", np.nan)):
            J[a], n[a] = r["J1"], r["n_rows"]
    if len(J) < 3:
        return np.nan
    n0 = float(np.median(list(n.values())))
    Js = {a: (n[a] / (n[a] + n0)) * J[a] + (n0 / (n[a] + n0)) * pooled_J for a in J}
    # read shares from the ledger items of the trimmed calls
    turns = rows.select("turn_id", "agent")
    it = (pl.scan_parquet(SH / "context_ledger_items.parquet").filter(pl.col("kind") == "agent")
          .select("turn_id", "sender").collect().join(turns, on="turn_id"))
    win = rows.group_by("day").agg(pl.col("ap_lo").first(), pl.col("ap_hi").first())
    mj = (msgs.join(win, on="day").filter((pl.col("t") >= pl.col("ap_lo")) & (pl.col("t") <= pl.col("ap_hi")))
          .group_by("agent").len())
    nj = dict(mj.iter_rows())
    talks = rows.group_by("agent").agg(pl.col("talk").sum()).to_dict(as_series=False)
    mi = {a: nj.get(a, 0) / max(t, 1) for a, t in zip(talks["agent"], talks["talk"])}
    rd = it.group_by("agent", "sender").len()
    idx = {a: k for k, a in enumerate(ags)}
    K = np.zeros((len(ags), len(ags)))
    for i, j, c in rd.iter_rows():
        if i in idx and j in idx and nj.get(j, 0) > 0 and i in Js:
            K[idx[i], idx[j]] = mi.get(i, 1.0) * Js[i] * min(c / nj[j], 1.0)
    return float(np.max(np.abs(np.linalg.eigvals(K))))


def run_unit(uid: str) -> dict:
    c = pl.read_parquet(L.OUT / "units" / f"{uid}.parquet")
    m = pl.read_parquet(L.OUT / "msgs" / f"{uid}.parquet")
    d = L.all_counts(c, m)
    out = {"unit_id": uid}
    rows = L._rows(d, True)
    out["n_rows_trim"] = rows.height
    out["N"] = int(rows["agent"].n_unique()) if rows.height else 0
    out["med_call_s"] = float((rows["t_call"] - rows["t_prev"]).median()) if rows.height else np.nan
    out["med_w_s"] = float(rows["w"].median()) if rows.height else np.nan
    out["base_talk"] = float(rows["talk"].mean()) if rows.height else np.nan
    r = L.fit(d, m, "main", True, B=200, seed=1)
    if not r.get("ok"):
        out["ok"] = False
        return out
    out["ok"] = True
    for k in ("g", "g_lo", "g_hi", "g_se", "J1", "J1_lo", "J1_hi", "J1_se", "g3", "g3_lo", "g3_hi", "rbar", "mbar",
              "b_R_m", "b_R_m_lo", "b_R_m_hi", "b_P", "b_P_lo", "b_P_hi", "b_R_o", "b_R_l1", "b_R_l2", "b_y_l1",
              "n_reads", "n_msgs", "n_blocks"):
        out[k] = r.get(k, np.nan)
    for var, tag in (("noexo", "noexo"), ("all", "all"), ("dm", "dm"), ("naive", "naive")):
        rv = L.fit(d, m, var, True, B=100, seed=2)
        out[f"g_{tag}"] = rv.get("g", np.nan)
        out[f"g_{tag}_lo"] = rv.get("g_lo", np.nan)
        out[f"g_{tag}_hi"] = rv.get("g_hi", np.nan)
    ru = L.fit(d, m, "main", False, B=100, seed=3)
    out["g_untrim"], out["g_untrim_lo"], out["g_untrim_hi"] = ru.get("g", np.nan), ru.get("g_lo", np.nan), ru.get(
        "g_hi", np.nan)
    rn = L.fit(d, m, "named", True, B=200, seed=4)
    for k in ("J1_named", "J1_named_lo", "J1_named_hi", "J1_named_se", "J1_unnamed", "J1_unnamed_lo",
              "J1_unnamed_hi", "J1_unnamed_se"):
        out[k] = rn.get(k, np.nan)
    out["n_named_reads"] = float(rows["R_m_n"].sum() + 0)
    out["share_named"] = float(rows["R_all_n"].sum() / max(rows["R_all"].sum(), 1))
    # named / unnamed decomposition of g (post hoc A2): g_x = m_bar r_bar s_x J_x
    sn, gm = out["share_named"], r["rbar"] * r["mbar"]
    for tag, sh in (("named", sn), ("unnamed", 1 - sn)):
        for suf in ("", "_lo", "_hi"):
            out[f"g_{tag}{suf}"] = gm * sh * rn.get(f"J1_{tag}{suf}", np.nan)
    # quiet-recipient variant (post hoc A2): no own talk output in the previous 300 s
    L.QUIET_S = 300
    rq = L.fit(d, m, "main", True, B=100, seed=6)
    L.QUIET_S = None
    out["g_quiet"], out["g_quiet_lo"], out["g_quiet_hi"] = rq.get("g", np.nan), rq.get("g_lo", np.nan), rq.get(
        "g_hi", np.nan)
    out["n_rows_quiet"] = rq.get("n_rows", 0)
    eq = L.equal_time(d, B=200, seed=5)
    out.update({k: eq.get(k, np.nan) for k in ("g_eq", "g_eq_lo", "g_eq_hi", "n_days_eq", "N_eq")})
    # shift null (day-preserving sender shifts), point estimates + CI exclusion share
    rng = np.random.default_rng(int.from_bytes(uid.encode(), "little") % 2**32)
    gs, ex = [], 0
    for k in range(N_SHIFT):
        ms = L.shift_msgs(m, c, rng)
        ds = L.all_counts(c, ms)
        rs = L.fit(ds, ms, "main", True, B=60, seed=100 + k)
        if rs.get("ok"):
            gs.append(rs["g"])
            ex += int((rs.get("g_lo", 0) > 0) or (rs.get("g_hi", 0) < 0))
    out["shift_g_mean"] = float(np.mean(gs)) if gs else np.nan
    out["shift_g_q95"] = float(np.quantile(gs, 0.95)) if gs else np.nan
    out["shift_excl0_share"] = ex / max(len(gs), 1)
    out["shift_n"] = len(gs)
    try:
        out["g_het"] = het_gain(d, m, r["J1"])
    except Exception as e:  # noqa: BLE001
        out["g_het"] = np.nan
        out["het_err"] = str(e)[:80]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", default="")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    meta = pl.read_parquet(L.OUT / "unit_meta.parquet")
    elig = meta.filter((pl.col("n_agents_calling") >= 3) & (pl.col("n_msgs") >= 100) & (pl.col("n_calls_trim") >= 200))
    if a.units:
        elig = elig.filter(pl.col("unit_id").is_in(a.units.split(",")))
    ids = elig["unit_id"].to_list()
    print(len(ids), "eligible units", flush=True)
    with ProcessPoolExecutor(a.workers) as ex:
        res = list(ex.map(run_unit, ids))
    df = pl.DataFrame(res, infer_schema_length=None).join(meta, on="unit_id", how="left")
    od = L.OUT / "results"
    od.mkdir(parents=True, exist_ok=True)
    path = od / "units.parquet"
    if a.units and path.exists():
        old = pl.read_parquet(path).filter(~pl.col("unit_id").is_in(ids))
        df = pl.concat([old, df], how="diagonal_relaxed")
    df.write_parquet(path)
    print(df.select("unit_id", "N", "g", "g_lo", "g_hi", "J1", "rbar", "g_eq", "shift_excl0_share").sort("unit_id"))


if __name__ == "__main__":
    main()
