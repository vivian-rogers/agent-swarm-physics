"""H52 round 2, real-data statistics (card section "Round 2"; run only after r2_synthetic.py A and B).

  content    per period: human content premium and agent naming effect under the primary quote-free candidate (and gte,
             style-residualized, chi_dd2 check); DerSimonian-Laird pooling by regime -> r2/r4_content.json
  partition  read vs in-flight contrast at matched lag x before-age (period-stratified), humans and agents, both models,
             Delta and Delta_q -> r2/r4_partition.json
  estimates  per_period_estimates rows
Usage: uv run python hypotheses/H52-humans-loud-agents/analysis/r2_run.py content|partition|estimates [--B 1000]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h52lib as L  # noqa: E402
import estimate as E  # noqa: E402
import r2lib as R  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

OUT = R.R2OUT


def primary_candidate() -> str:
    s = json.loads((OUT / "synthetic" / "A_summary.json").read_text())
    return s.get("primary") or "chi_q1"


def meta(p):
    return json.loads((L.OUT / p / "meta.json").read_text())


def period_frame(p: str) -> tuple[pl.DataFrame, dict]:
    rows = pl.read_parquet(L.OUT / p / "rows.parquet")
    c = pl.read_parquet(OUT / p / "r2_content.parquet")
    al = json.loads((OUT / p / "r2_alpha_sums.json").read_text())
    df = rows.join(c, on="item", how="left")
    cols, alphas = {}, {}
    for tag, key in (("", "_bge"), ("_gte", "_gte"), ("_sr", "_sr")):
        pieces = {k: df[k + tag].cast(pl.Float64).fill_null(np.nan).to_numpy() for k in
                  ("q1_t", "q1_p", "qm_t", "qm_p", "a_t", "b_t", "a_p", "b_p", "q1_jd", "qm_jd") if k + tag in df.columns}
        pieces["alpha_sums"] = np.array(al[key])
        cd = R.candidates(pieces)
        alphas[key] = cd.pop("alpha")
        for k, v in cd.items():
            cols[k + tag] = v
    df = df.with_columns(*[pl.Series(k, v).fill_nan(None) for k, v in cols.items()])
    return df, alphas


def run_content(B: int):
    prim = primary_candidate()
    res = {"primary": prim, "periods": {}}
    for p in L.REPLICATION:
        df, alphas = period_frame(p)
        out = {"regime": meta(p)["regime"], "alpha": alphas}
        for var in ("", "_gte", "_sr"):
            for cand in ([prim, "chi_dd2"] if var == "" else [prim]):
                col = cand + var
                d = E.prepare(df, con_col=col)
                y = d["y_con"].cast(pl.Float64).fill_null(np.nan).to_numpy()
                cls = d["cls"].to_numpy(); named = d["named"].to_numpy().astype(bool)
                clu, rule = E.cluster_ids(d, 1)
                prem = L.att(y, cls == 1, cls == 0, d["s_con"].to_numpy(), clu, B=B, msg=d["msg"].to_numpy())
                rec = {"premium": prem, "cluster": rule}
                if var == "":
                    rec["premium_named"] = L.att(y, (cls == 1) & named, (cls == 0) & named, d["s_con"].to_numpy(), clu, B=B, naive=False)
                    rec["premium_unnamed"] = L.att(y, (cls == 1) & ~named, (cls == 0) & ~named, d["s_con"].to_numpy(), clu, B=B, naive=False)
                    rec["naming"] = L.att(y, (cls == 0) & named, (cls == 0) & ~named, d["s_nn"].to_numpy(),
                                          d["day_idx"].to_numpy().astype(np.int64), B=B, naive=True)
                out[col] = rec
        # agreement of the recomputed DiD (new placebo draws) with round 1's chi_dd
        a = df["chi_dd"].cast(pl.Float64).fill_null(np.nan).to_numpy(); b = df["chi_dd2"].cast(pl.Float64).fill_null(np.nan).to_numpy()
        ok = np.isfinite(a) & np.isfinite(b)
        out["check_chi_dd"] = dict(r=float(np.corrcoef(a[ok], b[ok])[0, 1]) if ok.sum() > 10 else None,
                                   mean_diff=float(np.mean(b[ok] - a[ok])) if ok.any() else None, n=int(ok.sum()))
        res["periods"][p] = out
        pr = out[prim]["premium"]; nm = out[prim]["naming"]
        print(p, out["regime"], f"prem {pr['att']:+.4f} {pr['ci']} naming {nm['att']:+.4f} {nm['ci']} | dd-check {out['check_chi_dd']}", flush=True)
    # pooling by regime
    pool = {}
    for rg in ("I", "III"):
        ps = [p for p in L.REPLICATION if res["periods"][p]["regime"] == rg]
        for key, sub in (("premium", prim), ("naming", prim), ("premium_gte", prim + "_gte"), ("premium_sr", prim + "_sr"),
                         ("premium_dd2", "chi_dd2")):
            fld = "naming" if key == "naming" else "premium"
            e = [res["periods"][p][sub][fld]["att"] for p in ps]
            s = [res["periods"][p][sub][fld]["se"] for p in ps]
            pool[f"{rg}_{key}"] = L.re_pool(e, s)
        pool[f"{rg}_naming_positive"] = int(sum(res["periods"][p][prim]["naming"]["att"] > 0 for p in ps if np.isfinite(res["periods"][p][prim]["naming"]["att"])))
        pool[f"{rg}_n_periods"] = len(ps)
    allp = L.REPLICATION
    pool["all_naming_positive"] = int(sum(res["periods"][p][prim]["naming"]["att"] > 0 for p in allp))
    res["pooled"] = pool
    g = res["periods"]["G51"][prim]
    res["G51_ratio_premium_naming"] = g["premium"]["att"] / g["naming"]["att"] if g["naming"]["att"] else None
    L.jdump(res, OUT / "r4_content.json")
    print(json.dumps(pool, indent=1, default=str))


def length_weights(P: pl.DataFrame, human: pl.DataFrame) -> np.ndarray:
    """Weights for agent pairs so their message-length quintiles (cut at human quintiles) match the human distribution."""
    cuts = np.quantile(human["len"].to_numpy(), [0.2, 0.4, 0.6, 0.8])
    qa = np.searchsorted(cuts, P["len"].to_numpy())
    qh = np.searchsorted(cuts, human["len"].to_numpy())
    ph = np.bincount(qh, minlength=5) / len(qh)
    pa = np.bincount(qa, minlength=5) / max(len(qa), 1)
    w = ph[qa] / np.maximum(pa[qa], 1e-9)
    return w


def run_partition(B: int):
    frames = []
    for p in L.REPLICATION:
        f = OUT / p / "r2_pairdelta.parquet"
        if f.exists():
            frames.append(pl.read_parquet(f))
    P = pl.concat(frames).with_columns(pl.col("named").fill_null(False))
    res = {"n_pairs": P.height}
    for scope, flt in (("all", pl.lit(True)), ("I", pl.col("regime") == "I"), ("III", pl.col("regime") == "III"),
                       ("G51", pl.col("period") == "G51"), ("G04", pl.col("period") == "G04")):
        S = P.filter(flt)
        out = {}
        for col in ("delta", "delta_gte", "delta_q", "delta_q_gte"):
            H = S.filter(pl.col("cls") == 1)
            An = S.filter((pl.col("cls") == 0) & ~pl.col("named"))
            Ad = S.filter((pl.col("cls") == 0) & pl.col("named"))
            rh = R.partition_contrast(H, col, n_boot=B, seed=1)
            ran = R.partition_contrast(An, col, n_boot=B, seed=2)
            rad = R.partition_contrast(Ad, col, n_boot=B, seed=3)
            hh = H.filter(pl.col(col).is_not_null())
            w = length_weights(An, hh) if hh.height else None
            ranw = R.partition_contrast(An, col, n_boot=B, seed=4, weights=w) if w is not None else {}
            out[col] = {"human": R.strip_boot(rh), "agent_unnamed": R.strip_boot(ran), "agent_named": R.strip_boot(rad),
                        "agent_unnamed_lenw": R.strip_boot(ranw) if ranw else {},
                        "human_minus_agent_unnamed": R.diff_independent(rh, ran),
                        "human_minus_agent_unnamed_lenw": R.diff_independent(rh, ranw) if ranw else {},
                        "agent_named_minus_unnamed": R.diff_independent(rad, ran)}
        res[scope] = out
        o = out["delta"]
        print(scope, "human C", round(o["human"].get("C", np.nan), 4), o["human"].get("C_ci"), "A", round(o["human"].get("A", np.nan), 4),
              "| agent-unnamed C", round(o["agent_unnamed"].get("C", np.nan), 4), "| named C", round(o["agent_named"].get("C", np.nan), 4),
              "| H-Au(lenw)", o["human_minus_agent_unnamed_lenw"], flush=True)
    # per-period human contrasts where in-flight pairs suffice
    per = {}
    for p in L.REPLICATION:
        S = P.filter((pl.col("period") == p) & (pl.col("cls") == 1))
        if S.filter(pl.col("arm") == "inflight").height >= 20:
            per[p] = {col: R.strip_boot(R.partition_contrast(S, col, n_boot=B, seed=5)) for col in ("delta", "delta_gte", "delta_q")}
    res["per_period_human"] = per
    L.jdump(res, OUT / "r4_partition.json")


def write_estimates():
    sys.path.insert(0, str(L.ROOT / "infra/shared"))
    import estimates as ES
    c = json.loads((OUT / "r4_content.json").read_text())
    prim = c["primary"]
    rows = []
    for p, o in c["periods"].items():
        g = int(p[1:3])
        for key, sub, fld, ch in (("human_content_premium_quotefree", prim, "premium", "content_bge"),
                                  ("human_content_premium_quotefree", prim + "_gte", "premium", "content_gte"),
                                  ("agent_naming_effect_quotefree", prim, "naming", "content_bge")):
            r = o[sub][fld]
            if r.get("att") is None or not np.isfinite(r.get("att", np.nan)):
                continue
            rows.append(dict(period_unit=f"G{g:02d}", goal_no=g, statistic=key, channel=ch, estimate=r["att"], ci_lo=r["ci"][0],
                             ci_hi=r["ci"][1], se=r.get("se"), ci_level=0.95, ci_kind="percentile", n=r.get("n_t"), n_kind="rows",
                             method=f"CEM ATT on {prim} (quote-free DiD, round 2), cluster bootstrap ({o[sub].get('cluster')})",
                             null="matched agent rows (premium) / matched unnamed agent rows (naming)", role="replication",
                             source="H52-humans-loud-agents/r2/r4_content.json", post_hoc=False))
    pp = json.loads((OUT / "r4_partition.json").read_text())
    for p, o in pp.get("per_period_human", {}).items():
        g = int(p[1:3])
        for col, ch in (("delta", "content_bge"), ("delta_gte", "content_gte")):
            r = o[col]
            if r.get("C") is None or not np.isfinite(r["C"]) or not np.isfinite(r["C_ci"][0]):
                continue
            rows.append(dict(period_unit=f"G{g:02d}", goal_no=g, statistic="human_read_minus_inflight_C", channel=ch, estimate=r["C"],
                             ci_lo=r["C_ci"][0], ci_hi=r["C_ci"][1], se=r.get("C_se"), ci_level=0.95, ci_kind="percentile",
                             n=r.get("n_inflight"), n_kind="in-flight pairs",
                             method="read minus in-flight at matched after-lag x before-age, decoy-corrected pull, message-cluster bootstrap",
                             null="in-flight arm (posted after m, produced without m in context)", role="native",
                             source="H52-humans-loud-agents/r2/r4_partition.json", post_hoc=False))
    df = ES.write_estimates(rows, hypothesis="H52")
    print("estimates rows", df.height)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--B", type=int, default=1000)
    a = ap.parse_args()
    if a.cmd == "content":
        run_content(a.B)
    elif a.cmd == "partition":
        run_partition(a.B)
    elif a.cmd == "estimates":
        write_estimates()


if __name__ == "__main__":
    main()
