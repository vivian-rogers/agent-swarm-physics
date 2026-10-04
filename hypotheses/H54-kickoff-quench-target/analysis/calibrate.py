"""Calibration statistics for the synthetic validation, from generic content structure only.

No kickoff, goal or plan direction is used. Statistics (per regime, eligible non-holdout periods):
  R_stmt      resultant length of an agent-day's unit statement vectors (days >= 2, n >= 5)
  q_later     mean pairwise cosine of agent-day vectors within a day (days >= 2)
  persist     cos(v_i,d, v_i,d+1) for consecutive active days (d >= 2)
  q_cross     cos between day-1 centroids of different periods in the same regime (period-specific content share)
  cen_persist cos(m_d, m_d+1) for d >= 2
  spectrum    eigenvalues of the covariance of agent-day vectors (days >= 2), normalized to sum 1
  n_day1      per-agent day-1 post-kickoff statement counts (structure)
Writes data/processed/H54-kickoff-quench-target/synthetic/calibration.json + spectrum_<regime>.npy
"""
from __future__ import annotations

import numpy as np
import polars as pl

import h54lib as L


def main():
    st, Z, _ = L.load_stmt()
    st = st.with_row_index("i")
    out = {}
    for reg in ["I", "II", "III"]:
        pers = [p for p in L.eligible() if L.period_regime(p) == reg]
        s = st.filter(pl.col("goal_no").is_in(pers) & (pl.col("src_goal") == pl.col("goal_no")))
        later = s.filter(pl.col("day") >= 2)
        g = later.group_by("goal_no", "day", "agent").agg(pl.col("i"), pl.len().alias("n")).filter(pl.col("n") >= 5)
        R, V, keys = [], [], []
        for ix, (p, d, a) in zip(g["i"].to_list(), g.select("goal_no", "day", "agent").iter_rows()):
            m = Z[np.asarray(ix)].mean(0)
            R.append(np.linalg.norm(m))
            V.append(L.unit(m))
            keys.append((p, d, a))
        V = np.vstack(V)
        kd = pl.DataFrame(keys, schema=["p", "d", "a"], orient="row").with_row_index("j")
        q_later, pers_v, cen = [], [], {}
        for (p, d), grp in kd.group_by("p", "d"):
            j = grp["j"].to_numpy()
            if len(j) >= 3:
                q_later.append(L.pairwise_q(V[j]))
            cen[(p, d)] = V[j].mean(0)
        idx = {k: i for i, k in enumerate(keys)}
        for (p, d, a), i in idx.items():
            n = idx.get((p, d + 1, a))
            if n is not None:
                pers_v.append(float(V[i] @ V[n]))
        cp = [float(L.unit(cen[(p, d)]) @ L.unit(cen[(p, d + 1)])) for (p, d) in cen if (p, d + 1) in cen]
        # day-1 centroids (post kickoff), cross-period similarity
        d1 = s.filter((pl.col("day") == 1) & ~pl.col("pre_kick"))
        d1g = d1.group_by("goal_no", "agent").agg(pl.col("i"), pl.len().alias("n")).filter(pl.col("n") >= 3)
        c1 = {}
        for p, grp in d1g.group_by("goal_no"):
            vs = np.vstack([L.unit(Z[np.asarray(ix)].mean(0)) for ix in grp["i"].to_list()])
            c1[int(p[0])] = L.unit(vs.mean(0))
        ks = sorted(c1)
        qc = [float(c1[a] @ c1[b]) for ii, a in enumerate(ks) for b in ks[ii + 1:]]
        C = np.cov(V.T)
        ev = np.sort(np.linalg.eigvalsh(C))[::-1]
        np.save(L.OUT / "synthetic" / f"spectrum_{reg}.npy", C)
        n1 = d1g["n"].to_list()
        out[reg] = {"periods": pers, "n_agent_days": len(R), "R_stmt_median": float(np.median(R)), "R_stmt_iqr": [float(np.percentile(R, 25)), float(np.percentile(R, 75))],
                    "q_later_median": float(np.median(q_later)), "persist_median": float(np.median(pers_v)),
                    "cen_persist_median": float(np.median(cp)) if cp else None,
                    "q_cross_day1_median": float(np.median(qc)) if qc else None,
                    "spectrum_top10": (ev[:10] / ev.sum()).tolist(), "eff_dim": float(ev.sum() ** 2 / (ev ** 2).sum()),
                    "n_day1_median": float(np.median(n1)), "n_day1_q10": float(np.percentile(n1, 10)),
                    "agents_day1_median": float(np.median(d1g.group_by("goal_no").len()["len"].to_numpy()))}
        print(reg, {k: v for k, v in out[reg].items() if k not in ("spectrum_top10", "periods")})
    L.write_json(L.OUT / "synthetic" / "calibration.json", out)


if __name__ == "__main__":
    (L.OUT / "synthetic").mkdir(parents=True, exist_ok=True)
    main()
