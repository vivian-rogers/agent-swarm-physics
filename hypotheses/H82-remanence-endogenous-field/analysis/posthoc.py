"""H82 post hoc mechanism checks (written after the pooled replication result was seen; labelled post hoc in the card).

PH1 wrap-up vs remanence: day-1 vectors rebuilt from statements posted >= 1 h after the kickoff window start of P
    (style_resid32 statement vectors, unit mean; >= 5 statements), then the same placebo-corrected regression.
PH2 own past vs village: veterans' own P-1 mean added as a regressor (individual carry-over), so gamma measures the
    village centroid beyond the agent's own previous content.
Both on day 1, both models; pooled unweighted mean of Delta gamma_1 against the primary S0 q95 (approximate: the
synthetic was not re-run for these variants).
Output: data/processed/H82-remanence-endogenous-field/posthoc/posthoc.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h82lib as L  # noqa: E402

ED = L.ROOT / "data/processed/shared/embeddings"
M2 = ("bge_small", "gte_modernbert")


def after_kickoff_vectors(D, model):
    st = pl.read_parquet(ED / "statements.parquet").with_row_index("srow")
    S = np.load(ED / f"statements_style_resid32_{model}.npy", mmap_mode="r")
    g = pl.read_parquet(ED / "goals.parquet").filter(pl.col("kind") == "kickoff").select("goal_no", "win_start")
    out = {}
    for b in D.bd.iter_rows(named=True):
        P, day1 = b["P"], b["days_P"][0]
        ws = g.filter(pl.col("goal_no") == P)["win_start"]
        if ws.len() == 0:
            continue
        t0 = ws[0]
        s = st.filter((pl.col("goal_no") == P) & (pl.col("pt_date") == day1))
        s = s.with_columns((pl.col("t") >= pl.lit(t0) + pl.duration(hours=1)).alias("after"))
        for a, sub in s.group_by("agent"):
            a = int(a[0]); aft = sub.filter(pl.col("after"))
            out[(P, day1, a)] = (L.unit(np.asarray(S[aft["srow"].to_numpy()], dtype=np.float64).mean(0)) if aft.height >= 5 else None,
                                 aft.height / max(sub.height, 1))
    return out


def run(D, designs, ysub=None, extra_own=False):
    res = []
    for b, des in designs:
        res += [r for r in L.boundary_stats(b, des[:1], n_boot=0, Ysub=ysub) if r["term"] == "e"]
    return res


def main():
    out = L.OUT / "posthoc"; out.mkdir(parents=True, exist_ok=True)
    res = {}
    for m in M2:
        D = L.Data(m)
        bds = list(D.bd.iter_rows(named=True))
        syn = json.loads((L.OUT / f"synthetic/synthetic_{m}.json").read_text())
        q95 = syn["S0_q95"]["all/e/mean_dg1"]
        # PH1: replace day-1 vectors by after-kickoff vectors; agents without them are dropped from every design
        ak = after_kickoff_vectors(D, m)
        designs = []
        for b in bds:
            des = L.boundary_designs(D, b, days=1)
            item = des[0]
            if item is None:
                continue
            day, dd, plc = item
            new = {}
            for key, d in dd.items():
                if d is None:
                    new[key] = None
                    continue
                Y, Z, names, ag, isnew = d
                keep = [j for j, a in enumerate(ag) if ak.get((b["P"], day, int(a)), (None,))[0] is not None]
                if len(keep) < 2:
                    new[key] = None
                    continue
                Y2 = np.array([ak[(b["P"], day, int(ag[j]))][0] for j in keep])
                new[key] = (Y2, Z[keep], names, ag[keep], isnew[keep])
            if new.get("prev") is not None:
                designs.append((b, [(day, new, plc)]))
        r1 = run(D, designs)
        share_after = float(np.mean([v[1] for v in ak.values()]))
        # PH2: own P-1 mean as an extra regressor (veterans; zeros for newcomers)
        designs2 = []
        for b in bds:
            des = L.boundary_designs(D, b, days=1)
            if des[0] is None:
                continue
            day, dd, plc = des[0]
            new = {}
            for key, d in dd.items():
                if d is None:
                    new[key] = None
                    continue
                Y, Z, names, ag, isnew = d
                own = []
                for a in ag:
                    mm = (D.agent == a) & (D.goal == b["prev"]) & (D.regime == b["regime"])
                    own.append(L.unit(D.X[mm].mean(0)) if mm.sum() else np.zeros(32))
                Z2 = np.concatenate([Z[:, :, :-1], np.array(own)[:, :, None], Z[:, :, -1:]], axis=2)
                new[key] = (Y, Z2, names[:-1] + ["own_prev"] + names[-1:], ag, isnew)
            designs2.append((b, [(day, new, plc)]))
        r2 = run(D, designs2)
        base = run(D, [(b, L.boundary_designs(D, b, days=1)) for b in bds])
        f = lambda rr: float(np.nanmean([x["dgamma"] for x in rr]))  # noqa: E731
        g = lambda rr: float(np.nanmean([x["dgamma"] > 0 for x in rr]))  # noqa: E731
        res[m] = {"S0_q95_primary": q95, "primary_mean_dg1": f(base), "primary_frac_pos": g(base),
                  "PH1_after_kickoff_mean_dg1": f(r1), "PH1_frac_pos": g(r1), "PH1_k": len(r1),
                  "PH1_share_statements_after_kickoff_plus1h": share_after,
                  "PH2_own_prev_mean_dg1": f(r2), "PH2_frac_pos": g(r2), "PH2_k": len(r2)}
        print(m, res[m], flush=True)
    (out / "posthoc.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
