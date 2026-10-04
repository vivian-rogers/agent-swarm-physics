"""H55 POST HOC decomposition of the reversed P1 (written 2026-10-04 after the replication run; not pre-registered).

Question: is the received-negativity field nu_j mostly *being corrected*? If doers get corrected and verifiers do the
correcting, c_j and nu_j anticorrelate without any friction toward enforcers.
  (a) rho(c_j, nu_j^pos): nu refitted with received corrections/declines (B is a Jev correction, or opp_type in
      {correction, decline}) recoded as neutral, so only position-type opposition counts as negative.
  (b) rho(c_j, r_j): r_j = share of replies to j that are Jev corrections (being corrected).
  (c) rho(r_j, nu_j).
Random-effects Fisher-z means across the P1-eligible periods.
  uv run python hypotheses/H55-norm-enforcer-immunity/analysis/posthoc.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h55lib as L  # noqa: E402
from h55lib import H  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402


def main():
    msgs = pl.read_parquet(H.OUT / "messages.parquet")
    rates = L.sender_rates(msgs)
    pp = L.pair_table()
    per = pl.read_parquet(H.OUT / "replication/per_period.parquet").filter(pl.col("P1_scorable") == True)  # noqa: E712
    out = []
    for g in per["goal_no"].to_list():
        p = pp.filter(pl.col("goal_no") == g)
        rt = rates.filter(pl.col("goal_no") == g)
        base = L.friction_agent(p, rt, R=200)
        ppos = p.with_columns(pl.when((pl.col("y") == -1) & (pl.col("B_corr") | pl.col("opp_type").is_in(["correction", "decline"])))
                              .then(0).otherwise(pl.col("y")).cast(pl.Int8).alias("y"))
        fpos = L.friction_agent(ppos, rt, R=200)
        rj = dict(p.group_by("a_agent").agg(pl.col("B_corr").mean()).iter_rows())
        ag = base["agents"]
        c = np.array(base["c"]); nu = np.array(base["nu"]); r = np.array([rj.get(a, 0.0) for a in ag])
        cpos = dict(zip(fpos.get("agents", []), fpos.get("nu", [])))
        nupos = np.array([cpos.get(a, np.nan) for a in ag])
        ok = np.isfinite(nupos)
        out.append({"goal_no": g, "n": len(ag), "rho_c_nu": base["rho"],
                    "rho_c_nupos": float(stats.spearmanr(c[ok], nupos[ok]).statistic) if ok.sum() >= 5 else None,
                    "rho_c_r": float(stats.spearmanr(c, r).statistic) if np.std(r) > 0 else None,
                    "rho_r_nu": float(stats.spearmanr(r, nu).statistic) if np.std(r) > 0 else None})
    df = pl.DataFrame(out)
    res = {"per_period": out}
    for col in ("rho_c_nu", "rho_c_nupos", "rho_c_r", "rho_r_nu"):
        d = df.filter(pl.col(col).is_not_null() & pl.col(col).is_not_nan())
        res[col] = L.fisher_z_meta(d[col].to_numpy(), d["n"].to_numpy())
        res[col]["n_pos"] = int((d[col] > 0).sum())
    (H.OUT / "replication/posthoc_p1.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps({k: v for k, v in res.items() if k != "per_period"}, indent=1))


if __name__ == "__main__":
    main()
