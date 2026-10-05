"""H67 round-2 real-data run (non-reserved units only): the R3 ladder, the R4 lagged in-flight multi-hop gain and the
R1 regime-I chat clock, per unit. Writes data/processed/H67-lagged-criticality-dial/round2/units.parquet.

    uv run python hypotheses/H67-lagged-criticality-dial/analysis/r2_run.py [--units 41,51e] [--workers 2]

Reserved data: every unit's days are checked with common.holdout_mask and calendar.holdout (assertion).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import polars as pl

import h67lib as L
import r2lib as R

sys.path.insert(0, str(L.ROOT / "infra/shared"))
from common import git_commit, holdout_mask  # noqa: E402

SH = L.ROOT / "data/processed/shared"
W50 = dict(pl.read_parquet(L.ROOT / "data/processed/H50-field-vs-coupling-transfer-lag/unit_table.parquet")
           .select("unit", "W").iter_rows())
B = 200


def check_reserved(uid: str):
    pu = pl.read_parquet(SH / "period_units.parquet").filter(pl.col("unit_id") == uid)
    assert pu.height == 1 and not pu["holdout"][0], uid
    days = list(pu["days"][0])
    assert not any(holdout_mask(days, [pu["goal_no"][0]] * len(days))), f"reserved day in {uid}"
    cal = pl.read_parquet(SH / "calendar.parquet")
    assert not cal.filter(pl.col("pt_date").is_in(days) & pl.col("holdout")).height, f"calendar reserved {uid}"


def put(out, tag, r, keys=("J", "J_lo", "J_hi", "J_se")):
    for k in keys:
        out[f"{tag}_{k}"] = r.get(k, np.nan) if r.get("ok") else np.nan
    out[f"{tag}_n_pairs"] = r.get("n_pairs", np.nan)


def ols_J(rows, cells, seed):
    b, bs = R.block_ols(rows, ["R_m", "P"], cells, B=B, seed=seed)
    J = b["R_m"] - b["P"]
    lo, hi, se = R.pct([x["R_m"] - x["P"] for x in bs])
    return {"ok": True, "J": J, "J_lo": lo, "J_hi": hi, "J_se": se}


def run_unit(uid: str) -> dict:
    check_reserved(uid)
    c = pl.read_parquet(L.OUT / "units" / f"{uid}.parquet")
    m = pl.read_parquet(L.OUT / "msgs" / f"{uid}.parquet")
    d = L.all_counts(c, m)
    out = {"unit_id": uid}
    r9 = L.fit(d, m, "main", True, B=B, seed=1)          # identical call to round 1 (reproduces g_lag)
    if not r9.get("ok"):
        out["ok"] = False
        return out
    out["ok"] = True
    gm = r9["rbar"] * r9["mbar"]
    out.update({"gmul": gm, "rbar": r9["rbar"], "mbar": r9["mbar"], "g_L9": r9["g"], "g_L9_lo": r9.get("g_lo"),
                "g_L9_hi": r9.get("g_hi"), "J_L9": r9["J1"], "J_L9_lo": r9.get("J1_lo"), "J_L9_hi": r9.get("J1_hi"),
                "J_L9_se": r9.get("J1_se")})
    rows = L._rows(d, True)
    w_bar = float(rows["w"].median())
    W = W50.get(uid, np.nan)
    out["W50"], out["w_bar"] = W, w_bar
    # ---------------------------------------------------------------- R3 ladder
    if np.isfinite(W):
        put(out, "L1", R.pair_rd(d, m, W, trim=False, demean=False, placebo=True, B=B, seed=11))
        put(out, "L1fs", R.pair_rd(d, m, W, trim=False, demean=False, placebo=True, outcome="R_all", B=100, seed=12))
        put(out, "L2", R.pair_rd(d, m, W, trim=True, demean=False, placebo=True, B=100, seed=13))
        put(out, "L4W", R.pair_rd(d, m, W, trim=True, demean=True, placebo=True, B=100, seed=14))
    put(out, "L3", R.pair_rd(d, m, w_bar, trim=True, demean=False, placebo=True, B=100, seed=15))
    put(out, "L4", R.pair_rd(d, m, w_bar, trim=True, demean=True, placebo=True, B=B, seed=16))
    put(out, "L5", R.pair_rd(d, m, w_bar, trim=True, demean=True, placebo=False, B=100, seed=17))
    put(out, "L6fs", R.pair_rd(d, m, w_bar, trim=True, demean=True, placebo=True, outcome="R_all", B=100, seed=18))
    put(out, "L7", ols_J(rows, False, 19), ("J", "J_lo", "J_hi", "J_se"))
    put(out, "L8", ols_J(rows, True, 20), ("J", "J_lo", "J_hi", "J_se"))
    if np.isfinite(W):
        cap0 = L.W_CAP
        try:
            L.W_CAP = W
            d9b = L.all_counts(c, m)
        finally:
            L.W_CAP = cap0
        r9b = L.fit(d9b, m, "main", True, B=100, seed=21)
        out["J_L9b"] = r9b.get("J1", np.nan)
        out["J_L9b_lo"], out["J_L9b_hi"] = r9b.get("J1_lo", np.nan), r9b.get("J1_hi", np.nan)
    for tag in ("L1", "L2", "L3", "L4", "L4W", "L5", "L7", "L8", "L9", "L9b"):
        j = out.get(f"J_{tag}", out.get(f"{tag}_J", np.nan))
        out[f"g_{tag}"] = j * gm if j is not None and np.isfinite(j) else np.nan
    if np.isfinite(out.get("L6fs_J", np.nan)) and out["L6fs_J"] > 0.2:
        out["g_L6"] = out["L4_J"] / out["L6fs_J"] * gm
    # ---------------------------------------------------------------- R4 multi-hop
    dl = R.add_lags(R.hw_counts(d, m))
    r4 = R.multihop(d, m, B=B, seed=31, dl=dl)
    if r4.get("ok"):
        out.update({f"r4_{k}": v for k, v in r4.items() if k not in ("ok",)})
    r4n = R.multihop(d, m, B=0, seed=32, dl=dl, slopes=False)
    out.update({f"r4ns_G{h}": r4n.get(f"G{h}", np.nan) for h in (1, 3, 5)})
    # ---------------------------------------------------------------- R1 chat clock (regimes I, II)
    nchat = int(c["is_chat"].sum())
    out["n_chat_calls"] = nchat
    if nchat >= 300:
        dc = R.chat_counts(c, m)
        rc = L.fit(dc, m, "main", True, B=B, seed=41)
        if rc.get("ok"):
            out.update({"chat_J": rc["J1"], "chat_J_lo": rc.get("J1_lo"), "chat_J_hi": rc.get("J1_hi"),
                        "chat_J_se": rc.get("J1_se"), "chat_rbar": rc["rbar"], "chat_n_rows": rc["n_rows"],
                        "chat_b_R_m": rc.get("b_R_m"), "chat_b_P": rc.get("b_P"), "chat_b_R_o": rc.get("b_R_o")})
            s = rc["rbar"] * r9["mbar"]
            out["g_chat"], out["g_chat_lo"], out["g_chat_hi"] = rc["J1"] * s, rc.get("J1_lo", np.nan) * s, rc.get(
                "J1_hi", np.nan) * s
            out["g_chat_se"] = rc.get("J1_se", np.nan) * s
            out["chat_base_talk"] = float(L._rows(dc, True)["talk"].mean())
            rn = L.fit(dc, m, "named", True, B=B, seed=42)
            for k in ("J1_named", "J1_named_lo", "J1_named_hi", "J1_named_se", "J1_unnamed", "J1_unnamed_lo",
                      "J1_unnamed_hi", "J1_unnamed_se"):
                out[f"chat_{k}"] = rn.get(k, np.nan)
            dh = dc.filter(pl.col("start_conf").cast(pl.String) == "high")
            out["chat_n_logged"] = int(L._rows(dh, True).height) if dh.height else 0
            if out["chat_n_logged"] >= 200:
                rh = L.fit(dh, m, "main", True, B=B, seed=43)
                if rh.get("ok"):
                    out["g_chat_logged"] = rh["J1"] * s
                    out["g_chat_logged_lo"], out["g_chat_logged_hi"] = rh.get("J1_lo", np.nan) * s, rh.get(
                        "J1_hi", np.nan) * s
                    out["g_chat_logged_se"] = rh.get("J1_se", np.nan) * s
        cu = d.filter(pl.col("is_chat") == 0)
        rcu = L.fit(cu, m, "main", True, B=B, seed=44)
        if rcu.get("ok"):
            # computer-use rows of the all-call clock; scaled by the unit's m_bar r_bar (reads at cu calls only)
            sh = float(L._rows(cu, True)["R_all"].sum()) / max(float(rows["R_all"].sum()), 1.0)
            out["share_reads_cu"] = sh
            out["g_cu"] = rcu["J1"] * gm * sh
            out["g_cu_lo"], out["g_cu_hi"] = rcu.get("J1_lo", np.nan) * gm * sh, rcu.get("J1_hi", np.nan) * gm * sh
            out["g_cu_se"] = rcu.get("J1_se", np.nan) * gm * sh
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", default="")
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    u1 = pl.read_parquet(L.OUT / "results" / "units.parquet").filter(pl.col("ok").fill_null(False))
    ids = u1["unit_id"].to_list()
    if a.units:
        ids = [i for i in ids if i in a.units.split(",")]
    # largest units first so the pool stays busy
    size = dict(u1.select("unit_id", "n_rows_trim").iter_rows())
    ids.sort(key=lambda i: -size.get(i, 0))
    print(len(ids), "units", flush=True)
    res = []
    with ProcessPoolExecutor(min(a.workers, 2)) as ex:
        for r in ex.map(run_unit, ids):
            res.append(r)
            print(r["unit_id"], {k: round(r[k], 3) for k in ("g_L9", "g_L1", "g_L4", "r4_G5", "g_chat")
                                 if isinstance(r.get(k), float) and np.isfinite(r[k])}, flush=True)
    df = pl.DataFrame(res, infer_schema_length=None)
    R.R2.mkdir(parents=True, exist_ok=True)
    path = R.R2 / "units.parquet"
    if a.units and path.exists():
        old = pl.read_parquet(path).filter(~pl.col("unit_id").is_in(ids))
        df = pl.concat([old, df], how="diagonal_relaxed")
    df.write_parquet(path)
    prov = {"built_by": "hypotheses/H67-lagged-criticality-dial/analysis/r2_run.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": "shared tables via H67 round-1 scheme (units/, msgs/)",
                        "tables": ["call_windows", "context_ledger_turns", "context_ledger_items", "chat_core",
                                   "chat_mentions_clean", "calendar", "period_units"]},
                       {"source": "H50 unit_table (W per unit, read as data)"}],
            "params": {"bootstrap": B, "K_hops": R.K_HOPS, "donut_s": R.DONUT, "reserved": "excluded, asserted"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (R.R2 / "_provenance.json").write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    main()
