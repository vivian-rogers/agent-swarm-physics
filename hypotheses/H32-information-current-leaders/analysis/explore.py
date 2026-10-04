"""H32 exploratory round 1 on real data (non-holdout periods only; asserted in ic_core.load_period).

Per period (data/processed/H32-information-current-leaders/G<NN>/):
  result.json   currents (Out, In, Net, z), T and its null, centralization (Phi, Gini, Q), human source, exposure
                contrast (multi-room), split-half stability, rival rankings, robustness variants
  gain.npz      G, dG, null median (+ seen-beyond-unseen / unseen dG where computed)
Then explore.json (all periods), segment tests (#26 after the election decision, #44 #best on 05-28/29), NE42.

Usage: uv run python hypotheses/H32-information-current-leaders/analysis/explore.py [periods|robust|segments|ne42|all]
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
import warnings  # noqa: E402
from multiprocessing import Pool  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ic_core as C  # noqa: E402

warnings.filterwarnings("ignore", category=RuntimeWarning)
SH = C.SH
DATA = C.DATA
T_ELECT_26 = dt.datetime(2026, 1, 9, 18, 59, 29, 461823, tzinfo=dt.timezone.utc).timestamp()
ROBUST = {"K1": dict(K_field=1), "K10": dict(K_field=10), "d16": dict(dim=16), "d64": dict(dim=64),
          "tau5": dict(tau=300.0), "tau45": dict(tau=2700.0), "no_intent": dict(no_intent=True),
          "Kdata": dict(text_fields=False)}


def periods():
    return [p["goal_no"] for p in json.loads((DATA / "periods.json").read_text())]


def names():
    ro = pl.read_parquet(SH / "roster.parquet")
    d = dict(zip(ro["agent"].to_list(), ro["name"].to_list()))
    d[C.HUMAN] = "humans"; d[C.AUTO] = "automated"
    return d


def sp(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 4 or np.std(a[m]) == 0 or np.std(b[m]) == 0:
        return None
    return float(spearmanr(a[m], b[m]).statistic)


# ============================================================================================== rivals
def rivals(g: int, sk: C.Skeleton, nodes: list[int]) -> dict:
    t0, t1 = sk.day_start[0], sk.day_start[-1] + sk.day_len[-1] + 3600
    cnt = {a: int((sk.spk == a).sum()) for a in nodes}
    cc = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "goal_no", "speaker_kind", "agent"]).filter(
        (pl.col("goal_no") == g) & (pl.col("speaker_kind") == "agent"))
    cm = pl.read_parquet(SH / "chat_mentions_clean.parquet", columns=["message_id", "mentions_roster"])
    mm = cc.join(cm, on="message_id").explode("mentions_roster").drop_nulls("mentions_roster")
    mm = mm.filter(pl.col("mentions_roster") != pl.col("agent"))
    indeg = dict(mm.group_by("mentions_roster").len().iter_rows())
    art = pl.read_parquet(SH / "artifacts.parquet", columns=["artifact", "first_t", "first_agent"]).filter(
        pl.col("first_agent").is_not_null())
    art = art.with_columns(pl.col("first_t").dt.epoch("us") / 1e6).filter((pl.col("first_t") >= t0) & (pl.col("first_t") <= t1))
    men = pl.read_parquet(SH / "artifact_mentions.parquet", columns=["artifact", "t", "agent", "speaker_kind"]).filter(
        pl.col("speaker_kind") == "agent").with_columns(pl.col("t").dt.epoch("us") / 1e6).filter((pl.col("t") >= t0) & (pl.col("t") <= t1))
    j = men.join(art, on="artifact").filter((pl.col("agent") != pl.col("first_agent")) & (pl.col("t") > pl.col("first_t")))
    adopt = dict(j.select("artifact", "first_agent").unique().group_by("first_agent").len().iter_rows())
    h02 = {}
    f = ROOT_H02 = C.ROOT / "data/processed/H02-couplings-are-real/real_influence.parquet"
    if f.exists():
        x = pl.read_parquet(f).filter((pl.col("est") == "block") & pl.col("chunk").str.starts_with(f"g{g}c"))
        if x.height:
            h02 = dict(x.group_by("agent").agg(pl.col("zI").mean()).iter_rows())
    h29 = {}
    f29 = C.ROOT / f"data/processed/H29-driver-nodes/G{g}/agents.parquet"
    if f29.exists():  # descriptive comparison with H29 (run in parallel; not pre-registered)
        x = pl.read_parquet(f29)
        h29 = {"net": dict(zip(x["agent"].to_list(), x["net"].to_list())), "D": dict(zip(x["agent"].to_list(), x["D"].to_list()))}
    return {"h29_net": [float(h29["net"][a]) if h29 and a in h29["net"] else None for a in nodes],
            "h29_D": [float(h29["D"][a]) if h29 and a in h29["D"] else None for a in nodes],
            "count": [cnt.get(a, 0) for a in nodes], "mention_indeg": [int(indeg.get(a, 0)) for a in nodes],
            "artifact_adopt": [int(adopt.get(a, 0)) for a in nodes],
            "h02_zI": [float(h02[a]) if a in h02 else None for a in nodes], "h02_covered": bool(h02)}


# ============================================================================================== one period
def load_variant(g: int, v: dict) -> C.Skeleton:
    sk = C.load_period(g, dim=v.get("dim"), K_field=v.get("K_field"), text_fields=v.get("text_fields", True))
    if v.get("no_intent"):
        sk = C.Skeleton(sk.goal_no, sk.days, sk.day_start, sk.day_off, sk.day_len, sk.a_total, sk.t, sk.a, sk.day, sk.room,
                        sk.spk, sk.z, sk.it_t[:0], sk.it_spk[:0], sk.it_z[:0], sk.rooms_tl, sk.agents, sk.meta)
    return sk


def trimmed(x, frac=0.1):
    x = np.sort(np.asarray(x, float)[np.isfinite(x)])
    k = int(len(x) * frac)
    return float(x[k:len(x) - k].mean()) if len(x) > 2 * k else float("nan")


def run_period(g: int, tag: str = "") -> dict:
    t0 = time.time()
    if tag == "A2":
        C.P["min_train_targets"] = 20
    sk = C.load_period(g)
    multi = len(sk.meta["rooms_populated"]) >= 2
    modes = ("seen", "seen_beyond_unseen", "unseen") if multi else ("seen",)
    r = C.run_unit(sk, n_null=C.P["n_null"], seed=C.SEED + g, modes=modes, do_human=True, n_withinday=20)
    nodes = r["nodes"]
    N = names()
    out = {"goal_no": g, "meta": sk.meta, "days": sk.days, "nodes": nodes, "names": [N.get(a, str(a)) for a in nodes],
           "out": r["out"].tolist(), "in": r["in"].tolist(), "net": r["net"].tolist(), "z_out": r["z_out"].tolist(),
           "z_net": r["z_net"].tolist(), "var_jack": r["var_jack"].tolist(), "T": r["T"], "p_T": r["p_T"],
           "T_null_q": np.nanquantile(r["T_null"], [0.05, 0.5, 0.95]).tolist(), "cent": r["cent"],
           "cent_nullvar": r["cent_nullvar"], "var_null": r["var_null"].tolist(), "standout": r["standout"],
           "p_standout": r["p_standout"], "p_max": r["p_max"],
           "withinday": {"T": r["withinday"]["T"], "p_T": r["withinday"]["p_T"], "z_out": r["withinday"]["z_out"].tolist(),
                         "out": r["withinday"]["out"].tolist(), "p_standout": r["withinday"]["p_standout"],
                         "p_max": r["withinday"]["p_max"]},
           "n_targets": {str(k): v for k, v in r["n_targets"].items()}, "human": r.get("human")}
    for m in modes[1:]:
        out[f"T_{m}"] = r[f"T_{m}"]; out[f"p_T_{m}"] = r[f"p_T_{m}"]
        out[f"T_{m}_null_q"] = np.nanquantile(r[f"T_{m}_null"], [0.05, 0.5, 0.95]).tolist()
        with np.errstate(invalid="ignore"):
            out[f"out_{m}"] = np.nanmean(r[f"dG_{m}"], 1).tolist()
    # same-room vs cross-room pairs (modal room of each agent in the period)
    if multi:
        mod = {}
        for a in nodes:
            rr = sk.room[sk.spk == a]
            mod[a] = int(np.bincount(rr[rr >= 0]).argmax()) if np.any(rr >= 0) else -1
        same, cross_seen, cross_unseen = [], [], []
        ix = {a: k for k, a in enumerate(nodes)}
        for i in nodes:
            for j in nodes:
                if i == j:
                    continue
                if mod[i] == mod[j]:
                    same.append(r["dG"][ix[i], ix[j]])
                else:
                    cross_seen.append(r["dG"][ix[i], ix[j]]); cross_unseen.append(r["dG_unseen"][ix[i], ix[j]])
        def summ(x):
            x = np.array(x, float); x = x[np.isfinite(x)]
            if len(x) < 3:
                return {"n": int(len(x))}
            rng = np.random.default_rng(1)
            bs = [np.mean(rng.choice(x, len(x))) for _ in range(2000)]
            return {"n": int(len(x)), "mean": float(x.mean()), "ci90": np.quantile(bs, [0.05, 0.95]).tolist()}
        out["pairs_same_room"] = summ(same); out["pairs_cross_room_seen"] = summ(cross_seen)
        out["pairs_cross_room_unseen"] = summ(cross_unseen); out["modal_room"] = {str(k): v for k, v in mod.items()}
    # split halves
    D = sorted(set(int(x) for x in sk.day))
    if len(D) >= 4 and len(nodes) >= 6:
        odd, even = [d for d in D if d % 2 == 1], [d for d in D if d % 2 == 0]
        ro = C.run_unit(sk.subset_days(odd), n_null=20, seed=C.SEED + g + 1, do_human=False)
        re_ = C.run_unit(sk.subset_days(even), n_null=20, seed=C.SEED + g + 2, do_human=False)
        oo = dict(zip(ro["nodes"], ro["out"])); ee = dict(zip(re_["nodes"], re_["out"]))
        com = [a for a in nodes if a in oo and a in ee]
        out["split_half"] = {"rho_out": sp([oo[a] for a in com], [ee[a] for a in com]), "n": len(com),
                             "rho_net": sp([dict(zip(ro["nodes"], ro["net"]))[a] for a in com],
                                           [dict(zip(re_["nodes"], re_["net"]))[a] for a in com]),
                             "top_odd": int(ro["nodes"][int(np.nanargmax(ro["out"]))]),
                             "top_even": int(re_["nodes"][int(np.nanargmax(re_["out"]))]),
                             "T_odd": ro["T"], "T_even": re_["T"]}
    rv = rivals(g, sk, nodes)
    out["rivals"] = rv
    keys = ("count", "mention_indeg", "artifact_adopt", "h02_zI", "h29_net", "h29_D")
    out["rho"] = {k: sp(r["out"], [np.nan if x is None else x for x in rv[k]]) for k in keys}
    out["rho_net"] = {k: sp(r["net"], [np.nan if x is None else x for x in rv[k]]) for k in keys}
    # human pseudo-agent rank among agents, by Out and by message count
    if r.get("human") is not None and np.isfinite(r["human"]["out"]):
        o = np.array(r["out"], float)
        out["human"]["rank_out"] = int(1 + np.sum(o > r["human"]["out"]))
        out["human"]["n_msgs"] = int((sk.spk == C.HUMAN).sum())
        out["human"]["rank_count"] = int(1 + np.sum(np.array(rv["count"]) > out["human"]["n_msgs"]))
        out["human"]["above_median_agent"] = bool(r["human"]["out"] > np.nanmedian(o))
    top = int(np.nanargmax(r["out"]))
    out["leader_call"] = {"top_out": nodes[top], "top_out_name": N.get(nodes[top]), "z_top": float(r["z_out"][top]),
                          "identified": bool(r["p_standout"] < 0.05 and r["p_max"] < 0.05),
                          "top_net": nodes[int(np.nanargmax(r["net"]))], "top_net_name": N.get(nodes[int(np.nanargmax(r['net']))])}
    d = DATA / f"G{g:02d}"
    d.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(d / ("gain.npz" if not tag else f"gain_{tag}.npz"), nodes=np.array(nodes), G=r["G"], dG=r["dG"],
                        G_null_median=r["G_null_median"],
                        **({"dG_seen_beyond_unseen": r["dG_seen_beyond_unseen"], "dG_unseen": r["dG_unseen"]} if multi else {}))
    # robust aggregate (added post hoc, A2): 10% trimmed mean of dG and of each null replica's dG
    out["T_trim"] = r["T_trim"]; out["p_T_trim"] = r["p_T_trim"]
    out["runtime_s"] = time.time() - t0
    out["tag"] = tag or "primary"
    (d / ("result.json" if not tag else f"result_{tag}.json")).write_text(json.dumps(out, indent=1, default=float))
    print(g, f"T={out['T']*100:.3f}% p={out['p_T']:.3f}", "top", out["leader_call"]["top_out_name"],
          f"z={out['leader_call']['z_top']:.1f}", "phi", round(out["cent_nullvar"]["phi"], 3) if np.isfinite(out["cent_nullvar"]["phi"]) else None,
          "p_standout", round(out["p_standout"], 3), f"{out['runtime_s']:.0f}s", flush=True)
    return out


def run_robust(args) -> dict:
    g, name = args
    v = ROBUST[name]
    sk = load_variant(g, v)
    old = dict(C.P)
    if "tau" in v:
        C.P["tau"] = v["tau"]
    try:
        r = C.run_unit(sk, n_null=20, seed=C.SEED + g + 7, do_human=False)
    finally:
        C.P.update(old)
    prim = json.loads((DATA / f"G{g:02d}" / "result.json").read_text())
    po = dict(zip(prim["nodes"], prim["out"]))
    com = [a for a in r["nodes"] if a in po]
    return {"g": g, "variant": name, "T": r["T"], "p_T": r["p_T"], "top": int(r["nodes"][int(np.nanargmax(r["out"]))]),
            "rho_out_vs_primary": sp([dict(zip(r["nodes"], r["out"]))[a] for a in com], [po[a] for a in com]),
            "phi": r["cent"]["phi"], "pQ": r["cent"]["pQ"]}


# ============================================================================================== segments
def segments() -> dict:
    N = names()
    res = {}
    sk = C.load_period(26)
    post = sk.t >= T_ELECT_26
    pre = sk.day < 4
    src = [int(a) for a in sk.agents]
    res["G26_post"] = {str(k): v for k, v in C.pooled_sender_gain(sk, post, src, n_null=40).items()}
    res["G26_pre_days1to4"] = {str(k): v for k, v in C.pooled_sender_gain(sk, pre, src, n_null=40).items()}
    res["G26_post_n_msgs"] = {str(a): int(((sk.spk == a) & post).sum()) for a in src}
    sk = C.load_period(44)
    days = [k for k, d in enumerate(sk.days) if d in ("2026-05-28", "2026-05-29")]
    best = (sk.room == 2) & np.isin(sk.day, days)
    present = sorted(set(int(a) for a in sk.spk[best] if a < 100))
    res["G44_best_0528_29"] = {str(k): v for k, v in C.pooled_sender_gain(sk, best, present + [C.HUMAN], n_null=40).items()}
    res["G44_best_n_msgs"] = {str(a): int(((sk.spk == a) & best).sum()) for a in present + [C.HUMAN]}
    for k in list(res):
        if not k.endswith("n_msgs"):
            print(k, sorted(((N.get(int(a)), round(v["dG"] * 100, 3), round(v["z"], 1)) for a, v in res[k].items()),
                            key=lambda x: -x[1]), flush=True)
    (DATA / "segments.json").write_text(json.dumps(res, indent=1, default=float))
    return res


# ============================================================================================== NE42
def ne42(tag: str = "") -> dict:
    sfx = "" if not tag else f"_{tag}"
    R = {g: json.loads((DATA / f"G{g:02d}" / f"result{sfx}.json").read_text()) for g in (39, 40, 41)}
    Z = {g: np.load(DATA / f"G{g:02d}" / f"gain{sfx}.npz") for g in (39, 40, 41)}

    def val(g, i, j, kind):
        nodes = list(Z[g]["nodes"])
        if i not in nodes or j not in nodes:
            return np.nan
        key = "dG" if kind == "seen" else "dG_unseen"
        return float(Z[g][key][nodes.index(i), nodes.index(j)])
    mr = {g: {int(k): v for k, v in R[g].get("modal_room", {}).items()} for g in (39, 41)}
    common = sorted(set(mr[39]) & set(mr[41]) & set(int(a) for a in R[40]["nodes"]))
    split, stay = [], []
    for i in common:
        for j in common:
            if i == j:
                continue
            if mr[39][i] != mr[39][j] and mr[41][i] != mr[41][j]:
                b = np.nanmean([val(39, i, j, "unseen"), val(41, i, j, "unseen")])
                split.append((i, j, val(40, i, j, "seen"), b))
            elif mr[39][i] == mr[39][j] and mr[41][i] == mr[41][j]:
                b = np.nanmean([val(39, i, j, "seen"), val(41, i, j, "seen")])
                stay.append((i, j, val(40, i, j, "seen"), b))
    from scipy.stats import binomtest
    def stats(rows):
        d = np.array([a - b for _, _, a, b in rows], float); d = d[np.isfinite(d)]
        if len(d) == 0:
            return {"n": 0}
        k = int(np.sum(d > 0))
        return {"n": int(len(d)), "mean_diff": float(d.mean()), "median_diff": float(np.median(d)), "n_pos": k,
                "p_sign": float(binomtest(k, len(d), 0.5, alternative="greater").pvalue),
                "mean_40": float(np.nanmean([a for _, _, a, _ in rows])), "mean_39_41": float(np.nanmean([b for _, _, _, b in rows]))}
    res = {"split_pairs": stats(split), "same_room_pairs": stats(stay)}
    if res["split_pairs"].get("n") and res["same_room_pairs"].get("n"):
        res["did"] = res["split_pairs"]["mean_diff"] - res["same_room_pairs"]["mean_diff"]
        rng = np.random.default_rng(2)
        ds = np.array([a - b for _, _, a, b in split], float); ds = ds[np.isfinite(ds)]
        dt_ = np.array([a - b for _, _, a, b in stay], float); dt_ = dt_[np.isfinite(dt_)]
        bs = [np.mean(rng.choice(ds, len(ds))) - np.mean(rng.choice(dt_, len(dt_))) for _ in range(4000)]
        res["did_ci90"] = np.quantile(bs, [0.05, 0.95]).tolist()
    print("NE42" + sfx, json.dumps(res), flush=True)
    (DATA / f"ne42{sfx}.json").write_text(json.dumps(res, indent=1, default=float))
    return res


def collect():
    allr = {}
    for g in periods():
        f = DATA / f"G{g:02d}" / "result.json"
        if f.exists():
            allr[g] = json.loads(f.read_text())
    rob = json.loads((DATA / "robust.json").read_text()) if (DATA / "robust.json").exists() else []
    (DATA / "explore.json").write_text(json.dumps({"periods": allr, "robust": rob}, indent=1, default=float))
    prov_p = DATA / "_provenance.json"
    prov = json.loads(prov_p.read_text())
    prov["explore"] = {"built_by": "hypotheses/H32-information-current-leaders/analysis/explore.py",
                       "git_commit": __import__("common").git_commit(),
                       "inputs": [{"source": "ai-village", "revision": __import__("common").REVISION,
                                   "tables": ["H32/messages.parquet+vec_w64.npy+fields.npz", "shared/rooms_timeline",
                                              "shared/chat_core", "shared/chat_mentions_clean", "shared/artifacts",
                                              "shared/artifact_mentions", "H02/real_influence.parquet (read only)",
                                              "H11/G26/votes.parquet (election time, read only)"]}],
                       "params": {**C.P, "robust_variants": list(ROBUST), "t_elect_26": T_ELECT_26},
                       "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    prov_p.write_text(json.dumps(prov, indent=1, default=float))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd in ("periods", "all"):
        gs = periods() if len(sys.argv) < 3 else [int(x) for x in sys.argv[2].split(",")]
        with Pool(2) as pool:
            list(pool.imap_unordered(run_period, gs))
    if cmd == "posthoc_A2":
        from functools import partial
        with Pool(2) as pool:
            list(pool.imap_unordered(partial(run_period, tag="A2"), periods()))
        raise SystemExit
    if cmd in ("robust", "all"):
        jobs = [(g, v) for g in periods() for v in ROBUST]
        with Pool(2) as pool:
            rob = list(pool.imap_unordered(run_robust, jobs))
        (DATA / "robust.json").write_text(json.dumps(rob, indent=1, default=float))
    if cmd in ("segments", "all"):
        segments()
    if cmd in ("ne42", "all"):
        ne42()
    if cmd == "ne42_A2":
        ne42("A2")
        raise SystemExit
    collect()
