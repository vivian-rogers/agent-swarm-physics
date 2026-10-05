"""Write H58 round-2 per-period rows to the shared estimates table (infra/shared/estimates.py: write_estimates).
R1/R2 rows per unit of analysis (period_unit 'local:H01-<unit>', as round 1); R3 rows per goal period
(period_unit 'local:H58-G<NN>' with the non-reserved first/last day of the H58 units in that period). Non-reserved only.
All rows in one call (the writer replaces rows with the same statistic/channel/method/role/source).
Run: uv run python hypotheses/H58-coordinated-superagents/analysis/r2_rows.py"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r2lib58 as R  # noqa: E402

sys.path.insert(0, str(R.ROOT / "infra/shared"))
import estimates as E  # noqa: E402

SRC1 = "data/processed/H58-coordinated-superagents/r2/r1_results.json"
SRC2 = "data/processed/H58-coordinated-superagents/r2/r2_results.json"
SRC3 = "data/processed/H58-coordinated-superagents/r2/r3_results.json"


def f(x):
    try:
        v = float(x)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def main():
    meta = {x["unit"]: x for x in R.units_meta()}
    r1 = json.loads((R.R2 / "r1_results.json").read_text())
    r2 = json.loads((R.R2 / "r2_results.json").read_text())
    r3 = json.loads((R.R2 / "r3_results.json").read_text())
    rows = []

    def base(u, src):
        m = meta[u]
        return {"period_unit": f"local:H01-{u}", "unit_local": u, "goal_no": m["goal_no"], "first_day": m["days"][0],
                "last_day": m["days"][-1], "role": "replication" if u in R.REPL else "native", "post_hoc": False,
                "source": src}
    for u, x in r1.items():
        v = x["village"]
        lr, zl = f(v["lam_V_ratio"]), f(v["z_lam"])
        se_l = abs((lr - 1) / zl) if (lr is not None and zl not in (None, 0)) else None
        rows.append({**base(u, SRC1), "statistic": "r2_village_attraction_ratio", "channel": "work allocation (which repo)",
                     "estimate": lr, "se": se_l, "ci_lo": None if se_l is None else lr - 1.96 * se_l,
                     "ci_hi": None if se_l is None else lr + 1.96 * se_l, "ci_kind": "se_z", "ci_level": 0.95,
                     "n": f(v["n_ctx"]), "n_kind": "join-context agent-pair moves",
                     "method": "occupied-set attraction Lambda_V / rotation mean (pairwise, LODO popularity)",
                     "null": "100 within-day rotations of every agent", "notes": f"z_rot={zl}"})
        tv, zt = f(v["T_V"]), f(v["z_T"])
        se_t = abs(tv / zt) if (tv is not None and zt not in (None, 0)) else None
        rows.append({**base(u, SRC1), "statistic": "r2_village_exclusion_T", "channel": "work allocation (which repo)",
                     "estimate": tv, "se": se_t, "ci_lo": None if se_t is None else tv - 1.96 * se_t,
                     "ci_hi": None if se_t is None else tv + 1.96 * se_t, "ci_kind": "se_z", "ci_level": 0.95,
                     "n": f(v["pairbins"]), "n_kind": "eligible agent pair-bins",
                     "method": "exclusion on shared artifacts T = 1 - C_obs / C_rot",
                     "null": "100 within-day rotations of every agent", "notes": f"z (positive = exclusion)={zt}"})
        c = x["candidates"]
        rows.append({**base(u, SRC1), "statistic": "r2_attraction_candidates", "channel": "work allocation (which repo)",
                     "estimate": float(sum(k["A"]["qualifies"] for k in c)), "ci_kind": "none", "n": float(len(c)),
                     "n_kind": "round-1 candidate sets tested", "method": "A-rule (attraction, shift null, outside reference)",
                     "null": "rotations + activity-matched outsiders"})
        rows.append({**base(u, SRC1), "statistic": "r2_territorial_candidates", "channel": "work allocation (which repo)",
                     "estimate": float(sum(k["T"]["qualifies"] for k in c)), "ci_kind": "none", "n": float(len(c)),
                     "n_kind": "round-1 candidate sets tested", "method": "T-rule (exclusion, rotation, random partition)",
                     "null": "rotations + random-partition blocks at matched activity and pair-bins"})
        sp = x["static"]
        if sp.get("ok"):
            rows.append({**base(u, SRC1), "statistic": "r2_static_own_share", "channel": "work allocation (which repo)",
                         "estimate": f(sp["own_share"]), "ci_kind": "none", "n": float(sp["n_agents"]), "n_kind": "agents",
                         "method": "commit share on repos the agent holds >= 50% of",
                         "null": f"random partition at matched activity (mean {sp['own_null']:.3f})",
                         "notes": f"z={sp['z_own']}"})
    # R2: pooled per unit
    by_unit = {}
    for k, x in r2.items():
        by_unit.setdefault(x["unit"], []).append(x)
    for u, xs in by_unit.items():
        zs = [(f(x["village"]["z_lam"]), f(x["village"]["n_ctx"])) for x in xs]
        zs = [(z, n) for z, n in zs if z is not None and n]
        if zs:
            w = np.sqrt([n for _, n in zs])
            st = float((w * np.array([z for z, _ in zs])).sum() / math.sqrt((w ** 2).sum()))
            rows.append({**base(u, SRC2), "statistic": "r2_file_attraction_stouffer_z", "channel": "file inside shared repo",
                         "estimate": st, "ci_kind": "none", "n": float(len(zs)), "n_kind": "eligible shared repos",
                         "method": "Lambda_file vs rotation, Stouffer weighted by sqrt(join-context moves)",
                         "null": "100 within-day rotations of the repo's writers"})
        ex = [f(x["static"].get("excl")) for x in xs if x["static"].get("ok")]
        exn = [f(x["static"].get("excl_null")) for x in xs if x["static"].get("ok")]
        if ex:
            rows.append({**base(u, SRC2), "statistic": "r2_file_exclusivity_median", "channel": "file inside shared repo",
                         "estimate": float(np.median(ex)), "ci_kind": "none", "n": float(len(ex)),
                         "n_kind": "eligible shared repos", "method": "share of file-touches on single-writer files",
                         "null": f"random partition at matched activity (median {np.median(exn):.3f})"})
    # R3 per goal period
    days = {}
    for u, m in meta.items():
        if m["regime"] == "III":
            days.setdefault(m["goal_no"], []).extend(m["days"])
    for g, x in r3.get("per_period", {}).items():
        g = int(g)
        b = {"period_unit": f"local:H58-G{g:02d}", "goal_no": g, "first_day": min(days[g]), "last_day": max(days[g]),
             "role": "native", "post_hoc": False, "source": SRC3}
        st = x["store"]
        rows.append({**b, "statistic": "r2_pair_store_bits_forced", "channel": "own artifact (file codes)",
                     "estimate": f(st["I_store_F"]), "ci_lo": f(st["I_store_F_ci"][0]), "ci_hi": f(st["I_store_F_ci"][1]),
                     "ci_kind": "percentile", "ci_level": 0.95, "n": float(st["n_F"]), "n_kind": "forced erasures",
                     "method": "KL(p(X) || p(X vs time-shifted artifact state)), 8 file codes",
                     "null": f"placebo calls: {st['I_store_P']:.3f} bits"})
        ru = x["read_unread"]
        ci = ru.get("inter_ci", [None, None])
        rows.append({**b, "statistic": "r2_read_x_erasure_logor", "channel": "own artifact (file codes)",
                     "estimate": f(ru["inter"]), "ci_lo": f(ci[0]), "ci_hi": f(ci[1]), "ci_kind": "percentile",
                     "ci_level": 0.95, "n": float(ru["n_F"]), "n_kind": "forced erasures with a commit",
                     "method": "MH log-OR(return to r1 | r1 read vs unread), forced minus placebo",
                     "null": "placebo calls (posted-but-unread contrast)"})
        k = x["kappa"]["own"]
        rows.append({**b, "statistic": "r2_kappa_I_own_files", "channel": "re-read own files",
                     "estimate": f(k["I"]), "ci_lo": f(k["I_ci"][0]), "ci_hi": f(k["I_ci"][1]), "ci_kind": "percentile",
                     "ci_level": 0.95, "n": float(k["n_scramble"]), "n_kind": "forced erasures",
                     "method": "semantic_kappa.kappa_row I (X file code; S re-read own-file code)",
                     "null": "within agent x unit permutation floor",
                     "notes": f"identified={k.get('identified')}; dV_rel={f(k.get('dV_rel'))}; kappa={f(k.get('kappa'))}"})
    # pooled NE41 rows
    pooled_days = sorted(d for g in days for d in days[g])
    bp = {"period_unit": "local:H58-NE41-r3", "goal_no": 51, "first_day": pooled_days[0], "last_day": pooled_days[-1],
          "role": "native", "post_hoc": False, "source": SRC3,
          "notes": "pooled over regime-III H58 units (agent x unit strata); goal_no set to the largest contributor"}
    for cls in ("own", "oth", "goal", "any"):
        k = r3["kappa_pooled"][cls]
        rows.append({**bp, "statistic": f"r2_kappa_I_{cls}", "channel": f"re-read class {cls}",
                     "estimate": f(k["I"]), "ci_lo": f(k["I_ci"][0]), "ci_hi": f(k["I_ci"][1]), "ci_kind": "percentile",
                     "ci_level": 0.95, "n": float(k["n_scramble"]), "n_kind": "forced erasures",
                     "method": "semantic_kappa.kappa_row I", "null": "within agent x unit permutation floor",
                     "notes": f"identified={k.get('identified')}; I_sparse={k.get('I_sparse')}; dV_rel={f(k.get('dV_rel'))} "
                              f"{k.get('dV_rel_ci')}; kappa={f(k.get('kappa'))}"})
    out = E.write_estimates(rows, hypothesis="H58")
    print(out.height, "rows written")


if __name__ == "__main__":
    main()
