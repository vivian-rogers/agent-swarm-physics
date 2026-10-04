"""H33 measurement reliability of the agent-day diversity measures (x side only; no outcome used).

For eligible-unit agent-days with >= 20 deduplicated chat statements, split the statements at random into two
disjoint halves, compute PR10 and TV10 on each (same estimator as the scheme), and report the within-FE
(agent x unit and day demeaned) split-half correlation and its Spearman-Brown full-day reliability.
Writes reliability.json (used by synthetic.py for errors-in-variables).

Usage: uv run python hypotheses/H33-diversity-productivity/analysis/reliability.py
"""
from __future__ import annotations

import json

import h33lib as H  # noqa: I001
import h33common as C
import numpy as np
import polars as pl

import h12lib as L12
import posthoc as P12


def main():
    el = pl.read_parquet(C.OUT / "eligibility.parquet").filter("eligible")["unit"].to_list()
    cal = C.calendar_nonholdout().filter(pl.col("unit").is_in(el))
    days = set(cal["pt_date"].to_list())
    C.refuse_holdout(days, "calendar")
    st = (pl.read_parquet(C.EMB / "statements.parquet").with_row_index("row")
          .filter((pl.col("kind") == "chat") & pl.col("pt_date").is_in(list(days)) & ~pl.col("holdout")
                  & (pl.col("agent") != C.CLAUDE_CODE_AGENT)))
    kept = P12.dedup_rows(st.select("kind", "agent", "t", "pt_date", "row"))
    st = st.filter(pl.col("row").is_in(kept["row"].to_list())).join(cal.select("pt_date", "unit"), on="pt_date")
    E = np.load(C.EMB / "chat_bge_small.npy", mmap_mode="r")
    rows = []
    for (d, a, u, reg), g in st.group_by(["pt_date", "agent", "unit", "regime"]):
        if g.height < 2 * C.N_PR:
            continue
        W = C.load_whitener(reg, C.D)
        src = np.sort(g["src_row"].to_numpy())
        Y = W(np.asarray(E[src], dtype=np.float32)).astype(np.float64)
        rng = np.random.default_rng([C.SEED, C.stable_seed([d, int(a), "split"])])
        p = rng.permutation(len(Y))
        h1, h2 = p[: len(Y) // 2], p[len(Y) // 2:]
        z1 = np.zeros(len(h1), dtype=np.int64)
        z2 = np.zeros(len(h2), dtype=np.int64)
        r1 = L12.pr_rarefied(Y[h1], z1, C.N_PR, None, C.DRAWS, rng, erank=False)
        r2 = L12.pr_rarefied(Y[h2], z2, C.N_PR, None, C.DRAWS, rng, erank=False)
        rows.append({"pt_date": d, "agent": int(a), "unit": u, "pr_h1": r1["pr"], "pr_h2": r2["pr"],
                     "tv_h1": r1["tv"], "tv_h2": r2["tv"]})
    df = pl.DataFrame(rows).drop_nans()
    au = H.codes(df["agent"].to_numpy(), df["unit"].to_numpy())
    dy = H.codes(df["pt_date"].to_numpy())
    out = {"n_agent_days": df.height}
    for m in ("pr", "tv"):
        a = H.demean(df[f"{m}_h1"].to_numpy(), [au, dy])
        b = H.demean(df[f"{m}_h2"].to_numpy(), [au, dy])
        r = float(np.corrcoef(a, b)[0, 1])
        ra = float(np.corrcoef(df[f"{m}_h1"].to_numpy(), df[f"{m}_h2"].to_numpy())[0, 1])
        out[m] = {"within_fe_split_r": r, "within_fe_reliability_SB": 2 * r / (1 + r), "raw_split_r": ra,
                  "raw_reliability_SB": 2 * ra / (1 + ra)}
    (C.OUT / "reliability.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
