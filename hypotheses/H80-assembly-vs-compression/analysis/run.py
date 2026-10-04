"""H80 analysis: classifier comparisons per unit (P1-P4), motif prior test (P5), NCD drift (P6), natives (NE32, G38).

uv run python hypotheses/H80-assembly-vs-compression/analysis/run.py [--part cls|motifs|ncd|natives|all]
Writes data/processed/H80-assembly-vs-compression/results/*.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h80lib as L  # noqa: E402

ROOT = HERE.parents[2]
D = ROOT / "data/processed/H80-assembly-vs-compression"
RES = D / "results"
SH = ROOT / "data/processed/shared"

T_FEATS = ["lg_med", "lg_iqr", "lg_min", "lg_max", "periodic", "sec0", "hour_sin", "hour_cos", "in_window"]
C_FEATS = ["lz76", "lz78", "h1", "h_rate", "gzip", "zstd", "n_distinct"]
A_FEATS = ["a_rp"]
SETS = {"T": T_FEATS, "T_noW": T_FEATS[:-1], "C": C_FEATS, "A": A_FEATS, "C+A": C_FEATS + A_FEATS,
        "T+C": T_FEATS + C_FEATS, "T+C+A": T_FEATS + C_FEATS + A_FEATS}
NBOOT = 1000


def unit_frame(w: pl.DataFrame, unit: str) -> pl.DataFrame:
    if unit == "G51+post":
        return w.filter(pl.col("unit").is_in(["G51", "G51post"]))
    return w.filter(pl.col("unit") == unit)


def cluster_boot(y, scores: dict, groups, nboot=NBOOT, seed=0):
    """Bootstrap over groups: AUC per set and dAUC pairs."""
    rng = np.random.default_rng(seed)
    ug = np.unique(groups)
    idx = {g: np.flatnonzero(groups == g) for g in ug}
    out = {k: [] for k in scores}
    for _ in range(nboot):
        pick = np.concatenate([idx[g] for g in rng.choice(ug, len(ug), replace=True)])
        if len(set(y[pick])) < 2:
            continue
        for k, s in scores.items():
            out[k].append(L.auc(y[pick], s[pick]))
    return {k: np.array(v) for k, v in out.items()}


def classify(w: pl.DataFrame, unit: str, block: str) -> dict:
    d = unit_frame(w, unit)
    y = d["y"].to_numpy()
    if block == "repo":
        groups = d["repo_h"].to_numpy()
    elif block == "day":
        groups = np.array([int(x.replace("-", "")) for x in d["day"].to_list()])
    else:                                   # window-level folds (one positive stream on one day: G41)
        groups = np.arange(d.height)
    scores = {}
    for name, feats in SETS.items():
        X = d.select(feats).to_numpy().astype(float)
        scores[name] = L.oof_scores(X, y, groups, k=5, seed=0)
    ok = ~np.isnan(np.column_stack(list(scores.values()))).any(1)
    y2, g2 = y[ok], groups[ok]
    sc = {k: v[ok] for k, v in scores.items()}
    aucs = {k: L.auc(y2, v) for k, v in sc.items()}
    bs = cluster_boot(y2, sc, g2)
    ci = {k: [float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))] for k, v in bs.items()}

    def dci(a, b):
        n = min(len(bs[a]), len(bs[b]))
        dd = bs[a][:n] - bs[b][:n]
        return {"est": aucs[a] - aucs[b], "ci": [float(np.nanpercentile(dd, 2.5)), float(np.nanpercentile(dd, 97.5))]}

    # stream-weighted AUC (each stream counts once)
    sw = d.filter(pl.Series(ok)).group_by("stream").len()
    wmap = dict(zip(sw["stream"].to_list(), (1 / sw["len"].cast(pl.Float64)).to_list()))
    ww = np.array([wmap[s] for s in d["stream"].to_numpy()[ok]])
    # label-permutation null for C (window labels permuted within unit), 200 draws
    rng = np.random.default_rng(1)
    null = [L.auc(rng.permutation(y2), sc["C"]) for _ in range(200)]
    rho = spearmanr(d["a_rp"].to_numpy(), d["lz78"].to_numpy())[0]
    rho76 = spearmanr(d["a_rp"].to_numpy(), d["lz76"].to_numpy())[0]
    return {"unit": unit, "block": block, "n_windows": int(len(y2)), "n_pos": int(y2.sum()),
            "n_neg": int((1 - y2).sum()), "pos_streams": int(d.filter(pl.col("y") == 1)["stream"].n_unique()),
            "neg_streams": int(d.filter(pl.col("y") == 0)["stream"].n_unique()), "n_groups": int(len(np.unique(g2))),
            "auc": aucs, "auc_ci": ci, "auc_stream_weighted": {k: L.auc(y2, v, ww) for k, v in sc.items()},
            "dAUC_A_over_C": dci("C+A", "C"), "dAUC_C_over_T": dci("T+C", "T"),
            "dAUC_A_over_TC": dci("T+C+A", "T+C"), "dAUC_C_over_TnoW": None,
            "perm_null_C_p": float((np.array(null) >= aucs["C"]).mean()),
            "rho_arp_lz78": float(rho), "rho_arp_lz76": float(rho76),
            "means_by_class": {c: {f: float(d.filter(pl.col("y") == c)[f].mean()) for f in C_FEATS + A_FEATS + ["periodic"]}
                               for c in (0, 1)}}


def part_cls():
    w = pl.read_parquet(D / "windows.parquet")
    out = []
    for unit, block in (("G51", "day"), ("G31", "day"), ("G41", "window"), ("G51+post", "repo"), ("G51+post", "day")):
        r = classify(w, unit, block)
        out.append(r)
        print(unit, block, {k: round(v, 3) for k, v in r["auc"].items()}, "dA", round(r["dAUC_A_over_C"]["est"], 4),
              "rho", round(r["rho_arp_lz78"], 3))
    (RES / "classifier.json").write_text(json.dumps(out, indent=1, default=float))
    return out


# ============================================================================ motifs (P5) and natives NE32
def joiners():
    r = pl.read_parquet(SH / "roster.parquet").select("agent", "name", "lab", "joined")
    return r.filter((pl.col("joined") >= "2026-07-06") & (pl.col("joined") <= "2026-09-04"))


def part_motifs():
    m = pl.read_parquet(D / "motifs.parquet")
    pres = pl.read_parquet(D / "motif_presence.parquet")
    adt = pl.read_parquet(D / "agent_day_tokens.parquet")
    J = joiners()
    jag = J["agent"].to_list()
    days = adt.select("agent", "pt_date").unique().sort("agent", "pt_date")
    first = days.group_by("agent").agg(pl.col("pt_date").min().alias("d1"), pl.col("pt_date").sort().alias("ds"))
    first = first.filter(pl.col("agent").is_in(jag))
    d1 = dict(zip(first["agent"].to_list(), first["d1"].to_list()))
    later = {a: ds[1:] for a, ds in zip(first["agent"].to_list(), first["ds"].to_list())}
    roster = pl.read_parquet(SH / "roster.parquet").select("agent", "lab")
    hh = m.filter((pl.col("a") >= 6) & (pl.col("copies") >= 20))
    lo = m.filter((pl.col("a") <= 3) & (pl.col("copies") >= 20))
    pj = pres.filter(pl.col("agent").is_in(jag))
    by_motif = {(n, mm): set(zip(a, d)) for n, mm, a, d in pj.group_by("n", "m").agg(
        pl.col("agent"), pl.col("pt_date")).iter_rows()}

    def stats(tab):
        rows = []
        for n, mm, copies, nl in tab.select("n", "m", "copies", "n_labs").iter_rows():
            s = by_motif.get((n, mm), set())
            f1 = np.mean([(a, d1[a]) in s for a in d1])
            fl = [np.mean([(a, d) in s for d in later[a]]) for a in d1 if len(later[a]) >= 2]
            fL = float(np.mean(fl)) if fl else float("nan")
            rows.append({"n": n, "m": mm, "copies": copies, "n_labs": nl, "any_first": bool(f1 > 0), "f1": float(f1),
                         "fL": fL, "ratio": float(f1 / fL) if fL and fL > 0 else float("nan")})
        return pl.DataFrame(rows)

    sh, sl = stats(hh), stats(lo)
    # copy-matched low-index contrast: reweight low-index motifs to the high-index copy-decile distribution
    qs = np.quantile(m["copies"].to_numpy(), np.linspace(0, 1, 11))
    def dec(c): return np.clip(np.searchsorted(qs, c, side="right") - 1, 0, 9)
    hd = np.bincount(dec(sh["copies"].to_numpy()), minlength=10) / max(sh.height, 1)
    ld = dec(sl["copies"].to_numpy())
    lw = np.array([hd[x] / max((ld == x).mean(), 1e-9) for x in ld])
    prior_share = float((sh["any_first"] & (sh["n_labs"] >= 2)).mean())
    res = {"n_joiners": len(d1), "n_hh_motifs": sh.height, "n_low_motifs": sl.height,
           "P5_share_first_day_and_2labs": prior_share,
           "share_any_first": float(sh["any_first"].mean()), "share_2labs": float((sh["n_labs"] >= 2).mean()),
           "median_ratio_first_vs_later": float(np.nanmedian(sh["ratio"].to_numpy())),
           "mean_f1": float(sh["f1"].mean()), "mean_fL": float(np.nanmean(sh["fL"].to_numpy())),
           "low_copy_matched_share_any_first": float(np.average(sl["any_first"].to_numpy(), weights=lw)),
           "low_median_ratio": float(np.nanmedian(sl["ratio"].to_numpy())),
           "ensemble_A": {}}
    # ensemble assembly A per n-gram length (copies counted per session; N_T = total occurrences of kept motifs)
    for n in sorted(m["n"].unique().to_list()):
        mm = m.filter(pl.col("n") == n)
        NT = mm["occ"].sum()
        res["ensemble_A"][int(n)] = float((np.exp(mm["a"].to_numpy()) * (mm["copies"].to_numpy() - 1)).sum() / NT)
    # bootstrap over joiners for the ratio
    rng = np.random.default_rng(2)
    ag = list(d1)
    br = []
    for _ in range(300):
        pick = rng.choice(ag, len(ag), replace=True)
        rr = []
        for n, mm in sh.select("n", "m").iter_rows():
            s = by_motif.get((n, mm), set())
            f1 = np.mean([(a, d1[a]) in s for a in pick])
            fl = [np.mean([(a, d) in s for d in later[a]]) for a in pick if len(later[a]) >= 2]
            if fl and np.mean(fl) > 0:
                rr.append(f1 / np.mean(fl))
        br.append(np.median(rr))
    res["median_ratio_ci"] = [float(np.percentile(br, 2.5)), float(np.percentile(br, 97.5))]
    sh.write_parquet(RES / "motifs_hh_stats.parquet")
    (RES / "motifs.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))
    return res


def part_natives():
    """NE32 (isolated newcomers vs incumbents, vs NE33) and G38 (no-automation false positives)."""
    out = {}
    m = pl.read_parquet(D / "motifs.parquet")
    hh = m.filter((pl.col("a") >= 6) & (pl.col("copies") >= 20)).select("n", "m")
    tk = pl.read_parquet(D / "command_tokens.parquet").filter(pl.col("goal_no") == 51).sort("session", "t")
    # recompute session-level presence of any HH-HC motif
    P = 1_000_003
    parts = []
    for n in sorted(hh["n"].unique().to_list()):
        h = pl.lit(0, pl.Int64)
        for j in range(n):
            h = h * P + pl.col("tok").shift(-j).over("session").cast(pl.Int64)
        parts.append(tk.with_columns(h.alias("m"), pl.lit(n, pl.Int8).alias("n")).select("n", "m", "session"))
    hit = pl.concat(parts).join(hh, on=["n", "m"]).select("session").unique().with_columns(pl.lit(True).alias("hit"))
    ses = tk.select("agent", "pt_date", "session").unique().join(hit, on="session", how="left").with_columns(
        pl.col("hit").fill_null(False))
    ad = ses.group_by("agent", "pt_date").agg(pl.col("hit").mean().alias("share"), pl.len().alias("n_ses"))
    J = joiners()
    ne32 = J.filter(pl.col("joined") == "2026-07-09")["agent"].to_list()
    ne33 = J.filter(pl.col("joined").is_in(["2026-09-03", "2026-09-04"]))["agent"].to_list()
    first = ad.group_by("agent").agg(pl.col("pt_date").min().alias("d1"))
    ad = ad.join(first, on="agent")
    d1_rows = ad.filter(pl.col("pt_date") == pl.col("d1"))
    s32 = d1_rows.filter(pl.col("agent").is_in(ne32))
    s33 = d1_rows.filter(pl.col("agent").is_in(ne33))
    inc0709 = ad.filter((pl.col("pt_date") == "2026-07-09") & ~pl.col("agent").is_in(J["agent"].to_list()))
    w = lambda f: float((f["share"] * f["n_ses"]).sum() / max(f["n_ses"].sum(), 1))  # noqa: E731
    # motif-level: share of HH-HC motifs used on day 1 by >= 1 NE32 / NE33 newcomer
    pres = pl.read_parquet(D / "motif_presence.parquet").join(hh, on=["n", "m"])
    d1map = dict(zip(first["agent"].to_list(), first["d1"].to_list()))
    def motif_cov(ags):
        sel = pres.filter(pl.col("agent").is_in(ags)).with_columns(
            pl.col("agent").replace_strict(d1map, default=None).alias("d1")).filter(pl.col("pt_date") == pl.col("d1"))
        return sel.select("n", "m").unique().height / max(hh.height, 1)
    rng = np.random.default_rng(3)
    inc = inc0709["share"].to_numpy()
    out["NE32"] = {"ne32_agents": ne32, "ne33_agents": ne33,
                   "ne32_day1_share": w(s32), "ne33_day1_share": w(s33), "incumbents_0709_share": w(inc0709),
                   "ne32_per_agent": s32.select("agent", "share", "n_ses").to_dicts(),
                   "ne33_per_agent": s33.select("agent", "share", "n_ses").to_dicts(),
                   "N1a_ratio_ne32_vs_incumbents": w(s32) / max(w(inc0709), 1e-9),
                   "N1b_ratio_ne33_vs_ne32": w(s33) / max(w(s32), 1e-9),
                   "N1c_motif_cov_ne32": motif_cov(ne32), "N1c_motif_cov_ne33": motif_cov(ne33),
                   "incumbent_share_boot_ci": [float(np.percentile([rng.choice(inc, len(inc)).mean() for _ in range(500)], q))
                                               for q in (2.5, 97.5)] if len(inc) else None,
                   "n_incumbents_0709": int(inc0709.height)}
    # G38 false positives
    win = pl.read_parquet(D / "windows.parquet")
    tr = win.filter(pl.col("unit").is_in(["G51", "G51post"]))
    te = win.filter(pl.col("unit") == "G38")
    res = {"n_test": te.height, "n_test_pos": int(te["y"].sum())}
    for name in ("T", "T_noW", "C", "C+A", "A"):
        f = SETS[name]
        Xtr, Xte = L.standardize(tr.select(f).to_numpy().astype(float), te.select(f).to_numpy().astype(float))
        b = L.fit_logit(Xtr, tr["y"].to_numpy())
        ptr = L.predict_logit(b, Xtr)
        thr = np.quantile(ptr[tr["y"].to_numpy() == 1], 0.10)   # 90% sensitivity in training
        pte = L.predict_logit(b, Xte)
        fp = pte >= thr
        res[name] = {"fpr": float(fp[te["y"].to_numpy() == 0].mean()), "thr": float(thr),
                     "fpr_ci_wilson": wilson(int(fp.sum()), te.height)}
    out["G38"] = res
    (RES / "natives.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, indent=1, default=float))
    return out


def wilson(k, n, z=1.96):
    if n == 0:
        return [None, None]
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [float(c - h), float(c + h)]


# ============================================================================ NCD drift (P6)
def part_ncd():
    adt = pl.read_parquet(D / "agent_day_tokens.parquet").sort("agent", "pt_date")
    J = joiners()
    jag = set(J["agent"].to_list())
    enc = lambda toks: b"".join(int(t).to_bytes(2, "little") for t in toks)  # noqa: E731
    firsts = {}
    for a, g in adt.group_by("agent", maintain_order=True):
        firsts[a[0]] = g["tok"][0].to_list()[:1000]
    rows = []
    for a, g in adt.group_by("agent", maintain_order=True):
        a = a[0]
        ref_agents = [x for x in firsts if x in jag and x != a]
        ref = enc([t for x in ref_agents for t in firsts[x]])
        for k, toks in enumerate(g["tok"].to_list()):
            if len(toks) < 200:
                continue
            mid = max(0, len(toks) // 2 - 200)
            x = enc(toks[mid:mid + 400])
            rows.append({"agent": a, "tenure_day": k + 1, "joiner": a in jag, "ncd": L.ncd(x, ref)})
    df = pl.DataFrame(rows)
    df.write_parquet(RES / "ncd.parquet")
    per = []
    for a, g in df.filter(pl.col("joiner")).group_by("agent"):
        e = g.filter(pl.col("tenure_day") <= 2)["ncd"].mean()
        l_ = g.filter(pl.col("tenure_day") >= 5)["ncd"].median()
        if e is not None and l_ is not None:
            per.append(l_ - e)
    allag = df.filter(~pl.col("joiner"))
    slope = np.polyfit(allag["tenure_day"].to_numpy(), allag["ncd"].to_numpy(), 1)[0] if allag.height > 5 else None
    res = {"n_joiners": len(per), "median_change_late_minus_early": float(np.median(per)) if per else None,
           "per_joiner": [float(x) for x in per],
           "incumbent_slope_per_day": float(slope) if slope is not None else None,
           "joiner_mean_ncd": float(df.filter(pl.col("joiner"))["ncd"].mean()),
           "incumbent_mean_ncd": float(allag["ncd"].mean())}
    (RES / "ncd.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", default="all")
    a = ap.parse_args()
    RES.mkdir(parents=True, exist_ok=True)
    if a.part in ("cls", "all"):
        part_cls()
    if a.part in ("motifs", "all"):
        part_motifs()
    if a.part in ("ncd", "all"):
        part_ncd()
    if a.part in ("natives", "all"):
        part_natives()


if __name__ == "__main__":
    main()
