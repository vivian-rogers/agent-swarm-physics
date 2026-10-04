"""H33 round 1b (2026-10-04): period-native tests and post hoc checks on the round-1b tables.

  G51  rival pairs (same DQ6 role, same day): pair difference in log(1 + work commits) on the PR10 difference and the
       difference of squares, pair FE, CR1 by pair; role classes (media / support / other): within-agent slopes
  G39  one world per agent: across agents, Spearman of mean PR10 with work commits and distinct files; within-agent slope
  G42  videos per agent (link-based): across agents, Spearman of mean PR10 with videos first linked and work commits
  post hoc: right-side slope (two-lines b2) by diversity variant without #51 and without #38 (decides no verdict)
Writes data/processed/H33-diversity-productivity/r1b/native.json.
Usage: H33_ROUND=r1b uv run python hypotheses/H33-diversity-productivity/analysis/r1b_native.py
"""
from __future__ import annotations

import json
import os

os.environ.setdefault("H33_ROUND", "r1b")
import h33lib as H  # noqa: E402,I001
import h33common as C  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

assert C.ROUND == "r1b"
Y = C.Y_PRIMARY
out = {}
ad = C.load_agent_day()
C.refuse_holdout(ad["pt_date"].unique().to_list(), "agent_day")
gt = pl.read_parquet(C.SH / "ground_truth_labels.parquet").filter((pl.col("goal_no") == 51) & pl.col("preferred") & ~pl.col("holdout"))


def within_slope(sub, x_col, cls=None):
    x = sub[x_col].to_numpy().astype(float)
    y = np.log1p(sub[Y].to_numpy().astype(float))
    Z = np.column_stack([np.log(sub["n_chat_raw"].to_numpy().astype(float)), np.log1p(sub["engaged_min"].to_numpy().astype(float))])
    ag = H.codes(sub["agent"].to_numpy())
    D = H.Design([ag, H.codes(sub["pt_date"].to_numpy())], ag, Z)
    X = np.column_stack([x, x ** 2]) if cls is None else np.column_stack([x, x * cls])
    b, V, e, G = D.fit(D.dm(y), D.dm(X))
    se = np.sqrt(np.diag(V))
    return {"b": b.tolist(), "se": se.tolist(), "p": [H.pval(b[i], se[i], G)[0] for i in range(len(b))], "n": int(len(y)), "G": int(G)}


# ------------------------------------------------------------------ G51: rival pairs
a51 = ad.filter((pl.col("goal_no") == 51) & pl.col("pr10").is_not_null())
rp = gt.filter(pl.col("label_kind") == "rival_pair").select("agent_a", "agent_b", "value", "t_valid_from", "t_valid_to")
rows = []
for i, (a, b, val, t0, t1) in enumerate(rp.iter_rows()):
    d0, d1 = str(t0.date()), str(t1.date())
    xa = a51.filter((pl.col("agent") == a) & pl.col("pt_date").is_between(pl.lit(d0), pl.lit(d1))).select("pt_date", pl.col("pr10").alias("xa"), pl.col(Y).alias("ya"))
    xb = a51.filter((pl.col("agent") == b) & pl.col("pt_date").is_between(pl.lit(d0), pl.lit(d1))).select("pt_date", pl.col("pr10").alias("xb"), pl.col(Y).alias("yb"))
    j = xa.join(xb, on="pt_date", how="inner")
    for d, xa_, ya_, xb_, yb_ in j.select("pt_date", "xa", "ya", "xb", "yb").iter_rows():
        rows.append({"pair": i, "role": val, "pt_date": d, "dx": xa_ - xb_, "dx2": xa_ ** 2 - xb_ ** 2,
                     "dy": float(np.log1p(ya_) - np.log1p(yb_))})
pr = pl.DataFrame(rows)
res = {"n_pair_days": pr.height, "n_pairs": int(pr["pair"].n_unique()) if pr.height else 0}
if pr.height >= 20:
    cl = H.codes(pr["pair"].to_numpy())
    D = H.Design([cl], cl, None)
    for name, X in (("linear", pr.select("dx").to_numpy()), ("quadratic", pr.select("dx", "dx2").to_numpy())):
        b, V, e, G = D.fit(D.dm(pr["dy"].to_numpy()), D.dm(X.astype(float)))
        se = np.sqrt(np.diag(V))
        res[name] = {"b": b.tolist(), "se": se.tolist(), "p": [H.pval(b[k], se[k], G)[0] for k in range(len(b))], "G": int(G)}
    bq = res["quadratic"]["b"]
    res["vertex"] = float(-bq[0] / (2 * bq[1])) if bq[1] != 0 else None
    res["N1"] = bool(res["linear"]["p"][0] > 0.05 and res["quadratic"]["p"][1] > 0.05)
    res["against"] = bool(bq[1] < 0 and res["quadratic"]["p"][1] < 0.05)
out["G51_rival_pairs"] = res
# role classes
rc = dict(gt.filter(pl.col("label_kind") == "role_class").select("agent", "value").iter_rows())
a51 = a51.with_columns(pl.col("agent").replace_strict(rc, default="other", return_dtype=pl.Utf8).alias("rclass"))
cls_res = {}
for c in ("media", "support", "other"):
    sub = a51.filter(pl.col("rclass") == c)
    if sub["agent"].n_unique() >= 3 and sub.height >= 30:
        r = within_slope(sub, "pr10")
        cls_res[c] = {"n": r["n"], "agents": int(sub["agent"].n_unique()), "lin_b": r["b"][0], "lin_p": r["p"][0],
                      "quad_b": r["b"][1], "quad_p": r["p"][1]}
media = (a51["rclass"] == "media").cast(pl.Float64).to_numpy()
inter = within_slope(a51, "pr10", cls=media)
cls_res["interaction_media"] = {"b": inter["b"][1], "p": inter["p"][1]}
# linear-only slope per class (the prediction is about the slope)
for c in ("media", "support", "other"):
    sub = a51.filter(pl.col("rclass") == c)
    if sub["agent"].n_unique() >= 3 and sub.height >= 30:
        x = sub["pr10"].to_numpy().astype(float)
        yy = np.log1p(sub[Y].to_numpy().astype(float))
        Z = np.column_stack([np.log(sub["n_chat_raw"].to_numpy().astype(float)), np.log1p(sub["engaged_min"].to_numpy().astype(float))])
        ag = H.codes(sub["agent"].to_numpy())
        D = H.Design([ag, H.codes(sub["pt_date"].to_numpy())], ag, Z)
        b, V, e, G = D.fit(D.dm(yy), D.dm(x))
        cls_res[c]["slope"] = float(b[0])
        cls_res[c]["slope_p"] = H.pval(b[0], np.sqrt(V[0, 0]), G)[0]
cls_res["N2"] = bool(all(cls_res[c].get("slope_p", 1) > 0.05 for c in ("media", "support", "other") if c in cls_res)
                     and cls_res["interaction_media"]["p"] > 0.05)
out["G51_role_classes"] = cls_res


# ------------------------------------------------------------------ G39 and G42: across agents
def across(goal, extra_outcome=None):
    sub = ad.filter((pl.col("goal_no") == goal))
    per = (sub.group_by("agent").agg(pl.col("pr10").mean().alias("pr_mean"), pl.col("pr10").is_not_null().sum().alias("n_pr"),
                                     pl.col("commits_w").sum().alias("commits"), pl.col("files_w").sum().alias("files"))
           .filter(pl.col("n_pr") >= 2))
    if extra_outcome:
        wo = (pl.read_parquet(C.SH / "work_outcomes.parquet").filter((pl.col("goal_no") == goal) & (pl.col("outcome") == extra_outcome)
                                                                    & ~pl.col("holdout") & pl.col("agent").is_not_null())
              .select("agent", pl.col("value").alias("extra")))
        per = per.join(wo, on="agent", how="left").with_columns(pl.col("extra").fill_null(0))
    r = {"n_agents": per.height}
    for col in ["commits", "files"] + (["extra"] if extra_outcome else []):
        rho, p = stats.spearmanr(per["pr_mean"].to_numpy(), per[col].to_numpy())
        r[f"rho_{col}"], r[f"p_{col}"] = float(rho), float(p)
    x = per["pr_mean"].to_numpy()
    yv = np.log1p(per["commits"].to_numpy())
    X = np.column_stack([np.ones_like(x), x - x.mean(), (x - x.mean()) ** 2])
    beta, *_ = np.linalg.lstsq(X, yv, rcond=None)
    e = yv - X @ beta
    s2 = e @ e / max(1, len(yv) - 3)
    se = np.sqrt(np.diag(s2 * np.linalg.inv(X.T @ X)))
    r["quad_b2"], r["quad_p2"] = float(beta[2]), float(2 * stats.t.sf(abs(beta[2] / se[2]), len(yv) - 3))
    w = within_slope(sub.filter(pl.col("pr10").is_not_null()), "pr10")
    r["within_lin_b"], r["within_lin_p"] = w["b"][0], w["p"][0]
    if extra_outcome:
        top = per.sort("extra", descending=True).row(0, named=True)
        r["top_extra_agent_pr_rank_pct"] = float((per["pr_mean"] < top["pr_mean"]).mean())
    return r


g39 = across(39)
g39["N1"] = bool(abs(g39["rho_commits"]) < 0.55 and abs(g39["rho_files"]) < 0.55 and not (g39["quad_b2"] < 0 and g39["quad_p2"] < 0.05))
g39["N2"] = bool(g39["within_lin_p"] > 0.05)
out["G39"] = g39
g42 = across(42, "youtube_videos_first_linked")
g42["N1"] = bool(g42["p_extra"] > 0.05 and g42["p_commits"] > 0.05)
out["G42"] = g42


# ------------------------------------------------------------------ post hoc: right-side slope by variant
def tl(x, y, Z, au, day):
    D = H.Design([au, day], au, Z)
    r, sp = H.two_lines(D, D.dm(y), x)
    return {k: r[k] for k in ("xc", "b1", "p1", "b2", "p2", "n_lo", "n_hi")} | {"x_max": sp["x_max"], "interior": sp["interior"]}


ph = {}
for xcol in ("pr10", "pr15", "pr10_bge_w", "pr10_bge_restate", "pr10_gte", "pr10_gte_restate", "pr10_bge_copies", "pr10_gte_copies"):
    a2, x, y, Z, au, day = H.load_pooled(xcol, Y)
    u = a2["unit"].to_numpy()
    ph[xcol] = {"all": tl(x, y, Z, au, day)}
    for drop in ("51", "38"):
        m = u != drop
        ph[xcol][f"without_{drop}"] = tl(x[m], y[m], Z[m], H.codes(au[m]), H.codes(day[m]))
out["posthoc_right_side"] = ph


def clean(o):
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


(C.OUT / "native.json").write_text(json.dumps(clean(out), indent=1))
C.write_provenance("hypotheses/H33-diversity-productivity/analysis/r1b_native.py",
                   ["H33 r1b agent_day", "ground_truth_labels (#51 rival_pair, role_class)", "work_outcomes (#42 videos)"],
                   {"round": "r1b", "y": Y})
print(json.dumps(clean({k: v for k, v in out.items() if k != "posthoc_right_side"}), indent=1))
for k, v in ph.items():
    print(k, {kk: (round(vv["b2"], 3), round(vv["p2"], 3), round(vv["b1"], 3), round(vv["p1"], 3)) for kk, vv in v.items()})
