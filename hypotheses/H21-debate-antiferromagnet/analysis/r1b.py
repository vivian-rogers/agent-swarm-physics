"""H21 round 1b (improved data, 2026-10-04): replication on the corrected inputs + stance channel + native tests.

Layer 1 (replication; card P1-P7 unchanged, round-1b pre-registration S1-S4):
  - DQ6 ground truth check: H21's #12 labels (teams, judges, winners, phases) vs ground_truth_labels (preferred, ~holdout).
  - content channel re-run (g12_analysis.run) for model x source x dedupe (CONFIG in g12_analysis), plus the
    statement-level text-axis tilt and its post-verdict reversal (round-1 Q5/Q6, same code logic).
  - stance channel (DQ2 reply_pairs): Delta_stance (team permutation + calibrated agent-field null), team recovery from
    the stance graph, post-verdict switch-off, stance vs content AUC on the same replies.
Layer 2 (native; predictions in the G12 / G26 / G33 READMEs, written before running):
  - G12: re-drafting within-pair contrast (stance and content).
  - G26: approval-ballot camps vs stance and content, per election round.
  - G33: spontaneous camps in an unassigned debate (stance graph vs calibrated agent-field null).

Usage: uv run python hypotheses/H21-debate-antiferromagnet/analysis/r1b.py [--fast] [--skip-content]
Writes data/processed/H21-debate-antiferromagnet/r1b/*.json (numbers only; no text).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt  # noqa: E402
import itertools  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
import warnings  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "infra/shared"))
import afmlib as L  # noqa: E402
import g12_analysis as G  # noqa: E402
import h21core as C  # noqa: E402
from common import holdout_mask  # noqa: E402
from nulls import fit_ordinal, simulate_ordinal  # noqa: E402

warnings.simplefilter("ignore", RuntimeWarning)
SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H21-debate-antiferromagnet/r1b"
FAST = "--fast" in sys.argv
NPERM = 5000 if FAST else 20000
NSIM = 100 if FAST else 500
RNG = 20261004


def jdump(o):
    def d(x):
        if isinstance(x, dict):
            return {str(k): d(v) for k, v in x.items()}
        if isinstance(x, (list, tuple)):
            return [d(v) for v in x]
        if isinstance(x, np.ndarray):
            return d(x.tolist())
        if isinstance(x, (np.floating, float)):
            return None if not np.isfinite(x) else float(x)
        if isinstance(x, (np.integer,)):
            return int(x)
        if isinstance(x, np.bool_):
            return bool(x)
        return x
    return json.dumps(d(o), indent=1)


# ============================================================================================ ground truth check
def gt_check():
    deb = json.loads((G.DATA / "debates_resolved.json").read_text())
    r = pl.read_parquet(SH / "roster.parquet").select("agent", "name")
    n2a = dict(zip(r["name"], r["agent"]))
    g = pl.read_parquet(SH / "ground_truth_labels.parquet").filter(
        (pl.col("goal_no") == 12) & pl.col("preferred") & ~pl.col("holdout"))
    out = {"n_debates": len(deb), "team_mismatch": [], "judge_mismatch": [], "winner_mismatch": [], "phase_max_abs_s": {}}
    for d in deb:
        u = f"debate_{d['debate']:02d}"
        t = g.filter((pl.col("label_kind") == "team") & (pl.col("unit") == u))
        gov = {a for a, v in zip(t["agent"], t["value"]) if v == "gov"}
        opp = {a for a, v in zip(t["agent"], t["value"]) if v == "opp"}
        if gov != {n2a[x] for x in d["gov"]} or opp != {n2a[x] for x in d["opp"]}:
            out["team_mismatch"].append(d["debate"])
        j = g.filter((pl.col("label_kind") == "judge") & (pl.col("unit") == u))["agent"].to_list()
        if j != [n2a[d["judge"]]]:
            out["judge_mismatch"].append(d["debate"])
        res = g.filter((pl.col("label_kind") == "debate_result") & (pl.col("unit") == u))
        if res.height:
            v = (res["value"][0] or "").lower()
            if (d.get("winner") or "").lower() not in v:
                out["winner_mismatch"].append({"debate": d["debate"], "h21": d.get("winner"), "dq6": res["value"][0]})
        ph = g.filter((pl.col("label_kind") == "phase") & (pl.col("unit") == u))
        f = {v: (a, b) for v, a, b in zip(ph["value"], ph["t_valid_from"], ph["t_valid_to"])}
        diffs = []
        for key, val in (("deb", d["t_first_speech"]), ("post", d["t_verdict"])):
            if key in f:
                diffs.append(abs((f[key][0] - dt.datetime.fromisoformat(val)).total_seconds()))
        if "post" in f:
            diffs.append(abs((f["post"][1] - dt.datetime.fromisoformat(d["_t_post_end"])).total_seconds()))
        out["phase_max_abs_s"][d["debate"]] = max(diffs) if diffs else None
    out["agree"] = not (out["team_mismatch"] or out["judge_mismatch"])
    return out


# ============================================================================================ content channel
def text_axis_statement(st_pl, st, X, debates, W, phase):
    """Round-1 Q5/Q6: Gov-minus-Opp mean projection of phase statements on the pro-minus-con template axis."""
    Xc = L.agent_center(X, st["agent"])
    mot = G._motions()
    ax = {int(d): L.unit(W(e[1][None])[0] - W(e[2][None])[0]) for d, e in zip(mot["debates"], mot["emb"])}
    diffs, per = [], []
    for deb_ in debates:
        m = (st["debate"] == deb_["debate"]) & (st["phase"] == phase) & np.isin(st["agent"], deb_["gov"] + deb_["opp"])
        idx = np.flatnonzero(m)
        if deb_["debate"] not in ax or len(idx) < 4:
            continue
        proj = Xc[idx] @ ax[deb_["debate"]]
        ag = st["agent"][idx]
        members = sorted(set(ag))
        eps = {a: C.team_of(deb_, a) for a in members}
        if len({eps[a] for a in members}) < 2:
            continue

        def stat(e):
            g = np.array([e[a] for a in ag])
            return proj[g == 1].mean() - proj[g == -1].mean()
        allv = []
        kA = sum(1 for a in members if eps[a] == 1)
        for part in L.partitions(len(members), kA):
            e = dict(zip(members, part))
            allv.append(stat(e))
            if 2 * kA == len(members):
                allv.append(stat({a: -v for a, v in e.items()}))
        per.append({"debate": deb_["debate"], "obs": stat(eps), "all": np.array(allv)})
        diffs.append(stat(eps))
    if not per:
        return {"n_debates": 0}
    o = float(np.mean(diffs))
    n5 = L.perm_null(per, "all", NPERM, RNG)
    return {"gov_minus_opp": o, "p": L.p_upper(o, n5), "n_debates": len(per), "positive": int(sum(d > 0 for d in diffs)),
            "per_debate": {int(q["debate"]): float(q["obs"]) for q in per}}


def content_variant(model, source, dedupe, full=True):
    G.CONFIG.update(model=model, source=source, dedupe=dedupe)
    res = G.run(full=full)
    res.pop("_verdict_rows", None)
    res.pop("time_course", None)
    if "fluct" in res:
        res["fluct"].pop("series", None)
    st_pl, st, X, debates, lab_of, W = G.load(32, masked=(source == "masked"))
    tdeb = text_axis_statement(st_pl, st, X, debates, W, "deb")
    tpost = text_axis_statement(st_pl, st, X, debates, W, "post")
    common = [d for d in tpost.get("per_debate", {}) if d in tdeb.get("per_debate", {})]
    post_neg = int(sum(tpost["per_debate"][d] < 0 for d in common))
    res["text_axis_statement"] = {"deb": tdeb, "post": tpost, "n_common": len(common), "post_negative": post_neg,
                                  "post_over_deb": float(np.mean([tpost["per_debate"][d] for d in common])
                                                         / np.mean([tdeb["per_debate"][d] for d in common])) if common else None}
    res["n_statements"] = int(st_pl.height)
    G.CONFIG.update(model="bge_small", source="masked", dedupe="none")
    return res


def content_summary(r):
    s = r["static"]
    out = {"delta": s["delta"], "p_delta": s["p_delta"], "delta_ci": s.get("delta_ci"), "ms": s["ms"], "p_ms": s["p_ms"],
           "recovered": s["recovered"], "recovered_expected": s["recovered_expected_null"], "p_recovered": s["p_recovered"],
           "n_statements": r.get("n_statements")}
    if "rotation_null" in r:
        out["p_delta_rotation"] = r["rotation_null"]["p_delta"]
    if "text_axis" in r:
        out["text_axis_sigma"] = r["text_axis"]["raw"].get("ms_text")
        out["text_axis_p"] = r["text_axis"]["raw"].get("p_text")
        out["text_axis_pos"] = int(sum(x > 0 for x in r["text_axis"]["raw"].get("per_debate", [])))
        out["text_axis_spec_sigma"] = r["text_axis"]["motion_specific"].get("ms_text")
        out["text_axis_spec_p"] = r["text_axis"]["motion_specific"].get("p_text")
    if "fluct" in r:
        out["rho_3min"] = r["fluct"].get("rho")
        out["rho_3min_p_neg"] = r["fluct"].get("p_rho_neg")
    if "family" in r:
        fe = r["family"]["pair_fixed_effects"]
        out["b_team_pairFE"] = fe.get("b_team_pairFE")
        out["p_b_team_pairFE"] = fe.get("p_team_pairFE")
    t = r.get("text_axis_statement", {})
    out["stmt_text_deb"] = t.get("deb", {}).get("gov_minus_opp")
    out["stmt_text_deb_p"] = t.get("deb", {}).get("p")
    out["stmt_text_deb_pos"] = t.get("deb", {}).get("positive")
    out["stmt_text_post"] = t.get("post", {}).get("gov_minus_opp")
    out["stmt_text_post_negative"] = t.get("post_negative")
    out["stmt_text_n_common"] = t.get("n_common")
    mg = r.get("magnetization", [])
    for ph in ("pre", "deb", "post"):
        v = [m["Mu_topic"] for m in mg if m["phase"] == ph and m.get("Mu_topic") is not None and np.isfinite(m["Mu_topic"])]
        out[f"Mu_topic_{ph}"] = float(np.mean(v)) if v else None
    return out


# ============================================================================================ stance channel
def load_debates():
    st_pl, st, X, debates, lab_of, W = G.load(32)
    return st_pl, debates, lab_of


def stance_pairs(goal, phases=None):
    r = pl.read_parquet(SH / "reply_pairs.parquet",
                        columns=["B_message_id", "A_message_id", "b_agent", "a_agent", "a_kind", "pair_set", "labelled",
                                 "p_reply", "p_supports", "p_opposes", "stance", "pt_date", "goal_no", "holdout"])
    r = r.filter((pl.col("goal_no") == goal) & (pl.col("pair_set") == "cand") & pl.col("labelled") & (pl.col("a_kind") == 0)
                 & ~pl.col("holdout") & (pl.col("b_agent") != pl.col("a_agent")))
    r = r.with_columns((pl.col("p_supports") - pl.col("p_opposes")).alias("s"),
                       pl.when(pl.col("stance") == "supports").then(1).when(pl.col("stance") == "opposes").then(-1)
                       .otherwise(0).alias("h"))
    return r


def g12_replies(st_pl, debates):
    """DQ2 replies inside #12 debate phases between two debaters of that debate."""
    r = stance_pairs(12)
    ph = st_pl.select(pl.col("message_id").alias("B_message_id"), "debate", "phase", pl.col("t").alias("tB"))
    r = r.join(ph, on="B_message_id", how="inner").filter(pl.col("debate") >= 0)
    rows = []
    dd = {d["debate"]: d for d in debates}
    for x in r.iter_rows(named=True):
        d = dd.get(x["debate"])
        if d is None:
            continue
        eb, ea = C.team_of(d, x["b_agent"]), C.team_of(d, x["a_agent"])
        if eb == 0 or ea == 0:
            continue
        rows.append({**x, "eb": eb, "ea": ea, "same": eb == ea})
    return pl.DataFrame(rows)


def delta_by_debate(df, col="s", weight="p_reply", label=None):
    """Mean stance same-team minus opposite-team per debate (weighted), pooled with equal weight per debate."""
    per = {}
    for (d,), g in df.group_by("debate"):
        same = g["same"].to_numpy() if label is None else label(g)
        v, w = g[col].to_numpy(), (g[weight].to_numpy() if weight else np.ones(g.height))
        if same.sum() == 0 or (~same).sum() == 0:
            continue
        per[int(d)] = float(np.average(v[same], weights=w[same]) - np.average(v[~same], weights=w[~same]))
    return float(np.mean(list(per.values()))) if per else np.nan, per


def team_perm_null(df, debates, col, weight, rng, n):
    """Re-partition each debate's debaters into blocks of the true sizes; recompute the pooled Delta."""
    dd = {d["debate"]: d for d in debates}
    groups = {}
    for (d,), g in df.group_by("debate"):
        deb = dd[int(d)]
        members = sorted(set(deb["gov"]) | set(deb["opp"]))
        kA = len(deb["gov"])
        parts = [dict(zip(members, e)) for e in L.partitions(len(members), kA)]
        b, a = g["b_agent"].to_numpy(), g["a_agent"].to_numpy()
        v, w = g[col].to_numpy(), (g[weight].to_numpy() if weight else np.ones(g.height))
        vals = []
        for e in parts:
            same = np.array([e[x] == e[y] for x, y in zip(b, a)])
            if same.sum() == 0 or (~same).sum() == 0:
                continue
            vals.append(np.average(v[same], weights=w[same]) - np.average(v[~same], weights=w[~same]))
        groups[int(d)] = np.array(vals)
    tot = np.zeros(n)
    for vals in groups.values():
        tot += vals[rng.integers(0, len(vals), n)]
    return tot / len(groups)


def agent_field_sims(df, n, rng):
    """Calibrated agent-field null (H37 Amendment 2 via infra/shared/nulls.py): ordered logit with speaker and target
    fields fitted on the hard labels, simulated on the real reply structure."""
    ags = sorted(set(df["b_agent"].to_list()) | set(df["a_agent"].to_list()))
    pos = {a: k for k, a in enumerate(ags)}
    spk = np.array([pos[x] for x in df["b_agent"]])
    tgt = np.array([pos[x] for x in df["a_agent"]])
    y = df["h"].to_numpy() + 1
    c, a, b, ok = fit_ordinal(spk, tgt, y, len(ags))
    return [simulate_ordinal(spk, tgt, c, a, b, rng) for _ in range(n)], ok


def stance_graph_recovery(df, debates):
    """Per debate: J_ij = weighted mean soft stance (both directions); best two-block split (true sizes) maximizing
    within - across mean J; exact recovery count vs the Poisson-binomial chance."""
    dd = {d["debate"]: d for d in debates}
    rec, ps, per = 0, [], {}
    for (d,), g in df.group_by("debate"):
        deb = dd[int(d)]
        members = sorted(set(deb["gov"]) | set(deb["opp"]))
        pos = {a: k for k, a in enumerate(members)}
        n = len(members)
        S = np.zeros((n, n)); Wt = np.zeros((n, n))
        for b, a, s, w in zip(g["b_agent"], g["a_agent"], g["s"], g["p_reply"]):
            i, j = pos[b], pos[a]
            S[i, j] += s * w; S[j, i] += s * w; Wt[i, j] += w; Wt[j, i] += w
        J = np.where(Wt > 0, S / np.where(Wt > 0, Wt, 1), np.nan)
        kA = len(deb["gov"])
        parts = L.partitions(n, kA)
        truth = L.canon(np.array([C.team_of(deb, a) for a in members]))
        iu = np.triu_indices(n, 1)
        sc = []
        for e in parts:
            same = e[iu[0]] == e[iu[1]]
            v = J[iu]
            ok = np.isfinite(v)
            sc.append(np.nanmean(v[same & ok]) - np.nanmean(v[~same & ok]) if (same & ok).any() and (~same & ok).any() else -np.inf)
        best = parts[int(np.argmax(sc))]
        hit = L.canon(best) == truth
        rec += int(hit)
        ps.append(1 / len(parts))
        per[int(d)] = {"recovered": bool(hit), "n_part": len(parts), "n_replies": int(g.height),
                       "n_pairs_observed": int(np.isfinite(J[iu]).sum())}
    return {"recovered": rec, "n_debates": len(per), "expected": float(sum(ps)), "p": L.poisson_binomial_sf(rec, ps), "per_debate": per}


def residualize_two_way(y, spk, tgt):
    """OLS residuals of y on speaker and target dummies (two-way fixed effects)."""
    us, ut = np.unique(spk), np.unique(tgt)
    X = np.column_stack([np.ones(len(y))] + [(spk == a).astype(float) for a in us[1:]] + [(tgt == a).astype(float) for a in ut[1:]])
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    return y - X @ b


def auc(score, label):
    from scipy.stats import mannwhitneyu
    pos, neg = score[label], score[~label]
    if len(pos) == 0 or len(neg) == 0:
        return np.nan
    return float(mannwhitneyu(pos, neg).statistic / (len(pos) * len(neg)))


def stance_channel(st_pl, debates):
    rng = np.random.default_rng(RNG)
    df = g12_replies(st_pl, debates)
    out = {"n_replies_all_phases": df.height}
    deb = df.filter(pl.col("phase") == "deb")
    out["n_replies_deb"] = deb.height
    out["n_same"] = int(deb["same"].sum()); out["n_opp"] = int((~deb["same"]).sum())
    out["mean_s_same"] = float(np.average(deb.filter(pl.col("same"))["s"], weights=deb.filter(pl.col("same"))["p_reply"]))
    out["mean_s_opp"] = float(np.average(deb.filter(~pl.col("same"))["s"], weights=deb.filter(~pl.col("same"))["p_reply"]))
    out["opposes_share_same"] = float((deb.filter(pl.col("same"))["h"] == -1).mean())
    out["opposes_share_opp"] = float((deb.filter(~pl.col("same"))["h"] == -1).mean())
    # S1 soft Delta with team-permutation null
    D, per = delta_by_debate(deb, "s", "p_reply")
    nullD = team_perm_null(deb, debates, "s", "p_reply", rng, NPERM)
    out["S1_delta_soft"] = {"delta": D, "p_team_perm": L.p_upper(D, nullD), "null_q95": float(np.quantile(nullD, 0.95)),
                            "per_debate": per, "positive_debates": int(sum(v > 0 for v in per.values())), "n_debates": len(per)}
    # S1 hard Delta with the calibrated agent-field null (and team permutation)
    Dh, perh = delta_by_debate(deb, "h", None)
    sims, ok = agent_field_sims(deb, NSIM, rng)
    nullh = []
    for ysim in sims:
        tmp = deb.with_columns(pl.Series("hs", ysim))
        nullh.append(delta_by_debate(tmp, "hs", None)[0])
    nullh = np.array(nullh)
    nullDh = team_perm_null(deb, debates, "h", None, rng, NPERM)
    out["S1_delta_hard"] = {"delta": Dh, "p_team_perm": L.p_upper(Dh, nullDh), "agent_field_null_mean": float(np.nanmean(nullh)),
                            "agent_field_null_q95": float(np.nanquantile(nullh, 0.95)),
                            "p_agent_field": float((1 + np.sum(nullh >= Dh)) / (1 + np.sum(np.isfinite(nullh)))),
                            "ordinal_fit_ok": ok, "n_sims": len(nullh)}
    out["S1_pass"] = bool(out["S1_delta_soft"]["p_team_perm"] < 0.01 and Dh > out["S1_delta_hard"]["agent_field_null_q95"])
    # S2 recovery
    out["S2_recovery"] = stance_graph_recovery(deb, debates)
    # S3 post-verdict
    post = df.filter(pl.col("phase") == "post")
    Dp, perp = delta_by_debate(post, "s", "p_reply")
    common = [d for d in perp if d in per]
    out["S3_post"] = {"delta_post": Dp, "n_replies": post.height, "n_debates": len(perp), "per_debate": perp,
                      "delta_deb_same_debates": float(np.mean([per[d] for d in common])) if common else None,
                      "ratio_post_over_deb": float(np.mean([perp[d] for d in common]) / np.mean([per[d] for d in common])) if common else None}
    pre = df.filter(pl.col("phase") == "pre")
    out["pre"] = {"delta_pre": delta_by_debate(pre, "s", "p_reply")[0], "n_replies": pre.height}
    # S4 stance vs content AUC on the same replies (agent-adjusted)
    lab = deb["same"].to_numpy()
    spk, tgt = deb["b_agent"].to_numpy(), deb["a_agent"].to_numpy()
    s_res = residualize_two_way(deb["s"].to_numpy().astype(float), spk, tgt)
    out["S4"] = {"auc_stance_raw": auc(deb["s"].to_numpy(), lab), "auc_stance_adj": auc(s_res, lab)}
    for model in ("bge_small", "gte_modernbert"):
        G.CONFIG.update(model=model, source="masked", dedupe="none")
        stp, stn, X, _, _, _ = G.load(32)
        pos = dict(zip(stp["message_id"].to_list(), range(stp.height)))
        Xn = L.unit(X)
        ib = np.array([pos.get(m, -1) for m in deb["B_message_id"]]); ia = np.array([pos.get(m, -1) for m in deb["A_message_id"]])
        okk = (ib >= 0) & (ia >= 0)
        cs = np.full(deb.height, np.nan)
        cs[okk] = np.sum(Xn[ib[okk]] * Xn[ia[okk]], 1)
        m = np.isfinite(cs)
        c_res = residualize_two_way(cs[m], spk[m], tgt[m])
        out["S4"][f"auc_content_raw_{model}"] = auc(cs[m], lab[m])
        out["S4"][f"auc_content_adj_{model}"] = auc(c_res, lab[m])
        out["S4"][f"mean_cos_same_{model}"] = float(np.mean(cs[m][lab[m]])); out["S4"][f"mean_cos_opp_{model}"] = float(np.mean(cs[m][~lab[m]]))
    G.CONFIG.update(model="bge_small", source="masked", dedupe="none")
    return out, deb


# ============================================================================================ native G12: within-pair
def native_g12(deb, st_pl, debates):
    rng = np.random.default_rng(RNG + 1)
    out = {}
    # stance: per unordered pair and condition
    key = lambda b, a: (min(b, a), max(b, a))
    acc = {}
    for b, a, s, w, same in zip(deb["b_agent"], deb["a_agent"], deb["s"], deb["p_reply"], deb["same"]):
        acc.setdefault(key(b, a), {True: [0.0, 0.0, 0], False: [0.0, 0.0, 0]})
        acc[key(b, a)][bool(same)][0] += s * w; acc[key(b, a)][bool(same)][1] += w; acc[key(b, a)][bool(same)][2] += 1
    c, pairs = [], []
    for p, v in acc.items():
        if v[True][2] >= 1 and v[False][2] >= 1:
            c.append(v[False][0] / v[False][1] - v[True][0] / v[True][1]); pairs.append(p)
    c = np.array(c)
    n = len(c)
    flips = np.array([np.mean(c * rng.choice([-1, 1], n)) for _ in range(NPERM)])
    out["stance_soft"] = {"n_pairs": n, "mean_c": float(c.mean()) if n else None, "negative": int((c < 0).sum()),
                          "p_signflip_lower": float((1 + np.sum(flips <= c.mean())) / (1 + NPERM)) if n else None,
                          "per_pair": {f"{a}-{b}": float(x) for (a, b), x in zip(pairs, c)}}
    # hard labels and the calibrated agent-field null for the same within-pair contrast
    def hard_c(hcol):
        acc2 = {}
        for b, a, h, same in zip(deb["b_agent"], deb["a_agent"], hcol, deb["same"]):
            acc2.setdefault(key(b, a), {True: [], False: []})[bool(same)].append(h)
        cc = [np.mean(v[False]) - np.mean(v[True]) for p, v in acc2.items() if v[True] and v[False]]
        return float(np.mean(cc)) if cc else np.nan
    obs_h = hard_c(deb["h"].to_numpy())
    sims, ok = agent_field_sims(deb, NSIM, rng)
    nul = np.array([hard_c(y) for y in sims])
    out["stance_hard"] = {"mean_c": obs_h, "agent_field_null_mean": float(np.nanmean(nul)), "agent_field_q05": float(np.nanquantile(nul, 0.05)),
                          "p_agent_field_lower": float((1 + np.sum(nul <= obs_h)) / (1 + np.sum(np.isfinite(nul))))}
    # content: per-debate pair cosines of H21's spins (masked; bge and gte)
    for model in ("bge_small", "gte_modernbert"):
        G.CONFIG.update(model=model, source="masked", dedupe="none")
        stp, stn, X, debs, _, _ = G.load(32)
        Wd = C.build_windows(X, stn, debs, "deb", Xc=L.agent_center(X, stn["agent"]))
        accc = {}
        for w in Wd:
            Gm = w["S"] @ w["S"].T
            for i, j in zip(*np.triu_indices(len(w["agents"]), 1)):
                p = key(int(w["agents"][i]), int(w["agents"][j]))
                accc.setdefault(p, {True: [], False: []})[bool(w["eps"][i] == w["eps"][j])].append(Gm[i, j])
        cc = np.array([np.mean(v[False]) - np.mean(v[True]) for v in accc.values() if v[True] and v[False]])
        fl = np.array([np.mean(cc * rng.choice([-1, 1], len(cc))) for _ in range(NPERM)])
        out[f"content_{model}"] = {"n_pairs": int(len(cc)), "mean_c": float(cc.mean()),
                                   "p_signflip_two_sided": float((1 + np.sum(np.abs(fl) >= abs(cc.mean()))) / (1 + NPERM)),
                                   "negative": int((cc < 0).sum())}
    G.CONFIG.update(model="bge_small", source="masked", dedupe="none")
    return out


# ============================================================================================ helpers for G26 / G33
def content_agent_vectors(goal, t_from=None, t_to=None, model="bge_small"):
    """Agent means of unit-normalized regime-whitened chat statement vectors (white32), agent-centred over the whole
    goal period, then window-demeaned (mean over agents removed)."""
    st = pl.read_parquet(SH / "embeddings/statements.parquet").with_row_index("srow").filter(
        (pl.col("kind") == "chat") & (pl.col("goal_no") == goal) & ~pl.col("holdout"))
    V = np.load(SH / f"embeddings/statements_white32_{model}.npy", mmap_mode="r")
    X = np.asarray(V[st["srow"].to_numpy()], dtype=np.float64)
    ag = st["agent"].to_numpy()
    Xc = L.agent_center(X, ag)
    m = np.ones(st.height, bool)
    if t_from is not None:
        m &= (st["t"] >= t_from).to_numpy()
    if t_to is not None:
        m &= (st["t"] < t_to).to_numpy()
    out = {}
    for a in np.unique(ag[m]):
        k = m & (ag == a)
        if k.sum() >= 2:
            out[int(a)] = Xc[k].mean(0)
    if len(out) >= 2:
        mu = np.mean(list(out.values()), 0)
        out = {a: L.unit(v - mu) for a, v in out.items()}
    return out


def pair_J(df, agents, min_n):
    pos = {a: k for k, a in enumerate(agents)}
    n = len(agents)
    S = np.zeros((n, n)); Wt = np.zeros((n, n)); N = np.zeros((n, n))
    for b, a, s, w in zip(df["b_agent"], df["a_agent"], df["s"], df["p_reply"]):
        if b in pos and a in pos:
            i, j = pos[b], pos[a]
            S[i, j] += s * w; S[j, i] += s * w; Wt[i, j] += w; Wt[j, i] += w; N[i, j] += 1; N[j, i] += 1
    J = np.where((N >= min_n) & (Wt > 0), S / np.where(Wt > 0, Wt, 1), np.nan)
    np.fill_diagonal(J, np.nan)
    return J, N


def double_center_nan(J):
    """Double-centre over observed entries (agent effects removed), NaN kept."""
    M = J.copy()
    for _ in range(20):
        r = np.nanmean(M, 1, keepdims=True); r[~np.isfinite(r)] = 0
        M = M - r
        cmean = np.nanmean(M, 0, keepdims=True); cmean[~np.isfinite(cmean)] = 0
        M = M - cmean
    return (M + M.T) / 2


def camp_score(J):
    """Satisfied |J| weight of the best two-camp split (exact enumeration), over observed pairs."""
    n = len(J)
    iu = np.triu_indices(n, 1)
    v = J[iu]
    ok = np.isfinite(v)
    tot = np.abs(v[ok]).sum()
    if tot == 0:
        return np.nan, None
    best, arg = -np.inf, None
    for bits in range(2 ** (n - 1)):
        xi = np.array([1] + [1 if (bits >> k) & 1 else -1 for k in range(n - 1)])
        sat = (v[ok] * xi[iu[0]][ok] * xi[iu[1]][ok]).sum()
        if sat > best:
            best, arg = sat, xi
    return float((best + tot) / (2 * tot)), arg


def mantel(A, B, rng, n=20000):
    iu = np.triu_indices(len(A), 1)
    a, b = A[iu], B[iu]
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 5:
        return {"r": None, "p": None, "n_pairs": int(ok.sum())}
    r = float(np.corrcoef(a[ok], b[ok])[0, 1])
    nul = []
    for _ in range(n):
        p = rng.permutation(len(A))
        bp = B[np.ix_(p, p)][iu]
        okk = np.isfinite(a) & np.isfinite(bp)
        nul.append(np.corrcoef(a[okk], bp[okk])[0, 1] if okk.sum() >= 5 else np.nan)
    nul = np.array(nul)
    return {"r": r, "p_greater": float((1 + np.sum(nul >= r)) / (1 + np.sum(np.isfinite(nul)))), "n_pairs": int(ok.sum())}


# ============================================================================================ native G26
def native_g26():
    rng = np.random.default_rng(RNG + 2)
    cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("goal_no") == 26)
    assert not any(holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list()))
    g = pl.read_parquet(SH / "ground_truth_labels.parquet").filter((pl.col("goal_no") == 26) & pl.col("preferred") & ~pl.col("holdout"))
    cc = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "agent"]).rename({"agent": "voter"})
    b = g.filter(pl.col("label_kind") == "ballot").with_columns(pl.col("source_ref").str.replace("chat_core:message_id=", "").alias("mid")) \
        .join(cc, left_on="mid", right_on="message_id", how="left")
    appr = {}
    for v, c in zip(b.filter(pl.col("unit") == "approval")["voter"], b.filter(pl.col("unit") == "approval")["agent_b"]):
        appr.setdefault(int(v), set()).add(int(c))
    runoff = {int(v): int(c) for v, c in zip(b.filter(pl.col("unit") == "runoff")["voter"], b.filter(pl.col("unit") == "runoff")["agent_b"])}
    voters = sorted(appr)
    cands = sorted(set().union(*appr.values()))
    n = len(voters)
    Dm = np.zeros((n, n))
    for i, j in itertools.combinations(range(n), 2):
        A, B = appr[voters[i]], appr[voters[j]]
        Dm[i, j] = Dm[j, i] = 1 - len(A & B) / len(A | B)
    ph = g.filter(pl.col("label_kind") == "phase")
    t_res1 = ph.filter((pl.col("unit") == "round1") & (pl.col("value") == "result"))["t_valid_from"][0]
    t_day1 = dt.datetime(2026, 1, 5, 8, 0, tzinfo=dt.timezone.utc)  # 00:00 PT
    t_day5 = dt.datetime(2026, 1, 9, 8, 0, tzinfo=dt.timezone.utc)
    t_end = dt.datetime(2026, 1, 10, 8, 0, tzinfo=dt.timezone.utc)
    wins = {"contest": (t_day1, t_res1), "after": (t_res1, t_day5), "reelection_day": (t_day5, t_end)}
    r = stance_pairs(26).join(pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t"]).rename({"message_id": "B_message_id"}),
                              on="B_message_id", how="left")
    out = {"voters": voters, "n_voters": n, "candidates": cands, "runoff_choice": runoff,
           "ballot_dissimilarity_mean": float(Dm[np.triu_indices(n, 1)].mean()),
           "ballot_dissimilarity_distinct_values": sorted(set(np.round(Dm[np.triu_indices(n, 1)], 3).tolist()))}
    for wname, (a, bnd) in wins.items():
        rw = r.filter((pl.col("t") >= a) & (pl.col("t") < bnd))
        J, N = pair_J(rw, voters, 2)
        Jr = double_center_nan(J)
        res = {"n_replies": rw.height, "n_pairs_J": int(np.isfinite(J[np.triu_indices(n, 1)]).sum()),
               "mean_s": float(np.average(rw["s"], weights=rw["p_reply"])) if rw.height else None,
               "stance_mantel": mantel(Jr, -Dm, rng)}
        for model in ("bge_small", "gte_modernbert"):
            cv = content_agent_vectors(26, a, bnd, model)
            M = np.full((n, n), np.nan)
            for i, j in itertools.combinations(range(n), 2):
                if voters[i] in cv and voters[j] in cv:
                    M[i, j] = M[j, i] = float(cv[voters[i]] @ cv[voters[j]])
            res[f"content_mantel_{model}"] = mantel(M, -Dm, rng)
        out[wname] = res
    return out


# ============================================================================================ native G33
def native_g33():
    rng = np.random.default_rng(RNG + 3)
    cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("goal_no") == 33)
    assert not any(holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list()))
    r = stance_pairs(33)
    agents = sorted(set(r["b_agent"].to_list()) | set(r["a_agent"].to_list()))
    n = len(agents)
    J, N = pair_J(r, agents, 3)
    Jr = double_center_nan(J)
    cs, xi = camp_score(Jr)
    # negative pairs: per-pair z on double-centred reply residuals (soft stance minus speaker and target means)
    pos = {a: k for k, a in enumerate(agents)}
    spk = np.array([pos[x] for x in r["b_agent"]]); tgt = np.array([pos[x] for x in r["a_agent"]])

    def neg_pairs(svals):
        res = residualize_two_way(np.asarray(svals, float), spk, tgt)
        cnt = 0
        for i, j in itertools.combinations(range(n), 2):
            k = ((spk == i) & (tgt == j)) | ((spk == j) & (tgt == i))
            if k.sum() >= 3:
                z = res[k].mean() / (res[k].std(ddof=1) / np.sqrt(k.sum()) + 1e-9)
                cnt += int(z < -2)
        return cnt
    obs_neg = neg_pairs(r["s"].to_numpy())
    c, a, b, ok = fit_ordinal(spk, tgt, r["h"].to_numpy() + 1, n)
    null_cs, null_neg, null_mean = [], [], []
    hard_obs = r["h"].to_numpy().astype(float)
    J_h, _ = pair_J(r.with_columns(pl.Series("s", hard_obs), pl.lit(1.0).alias("p_reply")), agents, 3)
    cs_h, _ = camp_score(double_center_nan(J_h))
    for _ in range(min(NSIM, 300)):
        y = simulate_ordinal(spk, tgt, c, a, b, rng)
        Js, _ = pair_J(r.with_columns(pl.Series("s", y), pl.lit(1.0).alias("p_reply")), agents, 3)
        null_cs.append(camp_score(double_center_nan(Js))[0])
        null_neg.append(neg_pairs(y))
        null_mean.append(y.mean())
    null_cs, null_neg = np.array(null_cs), np.array(null_neg)
    out = {"n_agents": n, "n_replies": r.height, "n_pairs_J": int(np.isfinite(J[np.triu_indices(n, 1)]).sum()),
           "mean_s": float(np.average(r["s"], weights=r["p_reply"])), "opposes_share": float((r["h"] == -1).mean()),
           "supports_share": float((r["h"] == 1).mean()),
           "camp_score_soft": cs, "camp_score_hard": cs_h,
           "camp_null_mean": float(np.nanmean(null_cs)), "camp_null_q95": float(np.nanquantile(null_cs, 0.95)),
           "p_camp_agent_field": float((1 + np.sum(null_cs >= cs_h)) / (1 + np.sum(np.isfinite(null_cs)))),
           "neg_pairs": obs_neg, "neg_pairs_null_mean": float(null_neg.mean()), "neg_pairs_null_q95": float(np.quantile(null_neg, 0.95)),
           "p_neg_pairs": float((1 + np.sum(null_neg >= obs_neg)) / (1 + len(null_neg))), "ordinal_fit_ok": ok}
    # content: does the stance split (if any) separate in content? and lab confound of the stance split
    lab = dict(zip(*[pl.read_parquet(SH / "roster.parquet")[c].to_list() for c in ("agent", "lab")]))
    if xi is not None:
        camps = dict(zip(agents, xi.tolist()))
        out["stance_split_sizes"] = [int((xi == 1).sum()), int((xi == -1).sum())]
        out["stance_split_by_lab"] = {lab[a]: [camps[x] for x in agents if lab[x] == lab[a]] for a in agents}
        for model in ("bge_small", "gte_modernbert"):
            cv = content_agent_vectors(33, model=model)
            ids = [x for x in agents if x in cv]
            if len(ids) >= 4 and len({camps[x] for x in ids}) == 2:
                S = np.array([cv[x] for x in ids]); e = np.array([camps[x] for x in ids])
                out[f"content_delta_for_stance_split_{model}"] = float(L.delta_stat(S, e))
    return out


# ============================================================================================ main
def main():
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    res = {"gt_check": gt_check()}
    print("GT", res["gt_check"], flush=True)
    if "--skip-content" not in sys.argv:
        variants = [("bge_small", "masked", "none"), ("gte_modernbert", "masked", "none"),
                    ("bge_small", "unmasked", "none"), ("gte_modernbert", "unmasked", "none"),
                    ("bge_small", "styp", "none"), ("gte_modernbert", "styp", "none"),
                    ("bge_small", "masked", "restatements"), ("gte_modernbert", "masked", "restatements"),
                    ("bge_small", "masked", "copies")]
        content = {}
        for v in variants:
            name = "_".join(v)
            r = content_variant(*v, full=True)
            (OUT / f"content_{name}.json").write_text(jdump(r))
            content[name] = content_summary(r)
            print("CONTENT", name, jdump(content[name]).replace("\n", " ")[:900], flush=True)
        res["content"] = content
    else:  # resume: content variants already on disk (written by an earlier full run)
        res["content"] = {f.stem.replace("content_", ""): content_summary(json.loads(f.read_text()))
                          for f in sorted(OUT.glob("content_*.json"))}
    st_pl, debates, lab_of = load_debates()
    sc, deb = stance_channel(st_pl, debates)
    res["stance"] = sc
    print("STANCE", jdump({k: v for k, v in sc.items() if k not in ("S1_delta_soft",)}).replace("\n", " ")[:2500], flush=True)
    print("S1 soft", jdump({k: v for k, v in sc["S1_delta_soft"].items() if k != "per_debate"}).replace("\n", " "), flush=True)
    res["native_G12"] = native_g12(deb, st_pl, debates)
    print("G12 native", jdump({k: v if k != "stance_soft" else {kk: vv for kk, vv in v.items() if kk != "per_pair"}
                               for k, v in res["native_G12"].items()}).replace("\n", " "), flush=True)
    res["native_G26"] = native_g26()
    print("G26 native", jdump(res["native_G26"]).replace("\n", " ")[:2500], flush=True)
    res["native_G33"] = native_g33()
    print("G33 native", jdump(res["native_G33"]).replace("\n", " ")[:2500], flush=True)
    res["settings"] = {"NPERM": NPERM, "NSIM": NSIM, "fast": FAST}
    res["seconds"] = round(time.time() - t0, 1)
    (OUT / ("r1b_fast.json" if FAST else "r1b.json")).write_text(jdump(res))
    print("done", res["seconds"])


if __name__ == "__main__":
    main()
