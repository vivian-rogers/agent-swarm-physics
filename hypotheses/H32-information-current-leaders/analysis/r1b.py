"""H32 round 1b (2026-10-04): replication on ledger exposure, embedding/style/dedupe variants, the H57 unread placebo,
and the natives (#26 term 1, #35 lead designers, #44 leader window). Native predictions are in the period READMEs
(written 16:45 UTC, before this script was run). Variant is chosen by env (see ic_core): H32_DATA=r1b is set here.

  H32_EMB=bge   uv run python .../analysis/r1b.py periods [full]   # primary r1b (full: + within-day null, split-half)
  H32_EMB=gte   uv run python .../analysis/r1b.py periods          # second embedding model
  H32_EMB=style uv run python .../analysis/r1b.py periods          # style-residualized (within period) bge
  H32_S0=unread uv run python .../analysis/r1b.py periods          # H57 placebo: unread same-room messages as the 2nd term
  H32_DEDUPE=1  uv run python .../analysis/r1b.py periods          # targets without cross-echo / templated / self-repeat flags
  uv run python .../analysis/r1b.py natives
Writes data/processed/H32-information-current-leaders/r1b/<variant>/G<NN>/result.json and r1b/natives.json.
"""
from __future__ import annotations

import os

os.environ["H32_DATA"] = "r1b"
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
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
DEDUPE = os.environ.get("H32_DEDUPE", "") == "1"
TAU = os.environ.get("H32_TAU")      # short-lag variant: tau (s) for every decayed sum; window = 3 tau
if TAU:
    C.P["tau"] = float(TAU)
OUTV = C.OUT_R1B.parent / (C.OUT_R1B.name + ("_dedupe" if DEDUPE else "") + (f"_tau{TAU}" if TAU else ""))


def periods():
    return [p["goal_no"] for p in json.loads((C.DATA / "periods.json").read_text())]


def sp(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 4 or np.std(a[m]) == 0 or np.std(b[m]) == 0:
        return None
    return float(spearmanr(a[m], b[m]).statistic)


def dedupe_mask(g: int, sk: C.Skeleton) -> np.ndarray:
    """Targets kept: agent chat not flagged cross_echo (either model), templated (either) or self_repeat_both (DQ5)."""
    m = pl.read_parquet(C.DATA / "messages.parquet").filter((pl.col("goal_no") == g) & (pl.col("kind") == 0)).select("message_id").with_row_index("ord")
    ci = pl.read_parquet(C.SH / "embeddings/chat_index.parquet").with_row_index("src_row")
    st = pl.read_parquet(C.SH / "embeddings/statements.parquet", columns=["kind", "src_row"]).with_row_index("srow").filter(
        pl.col("kind") == "chat")
    fl = pl.read_parquet(C.SH / "statement_flags.parquet", columns=["srow", "cross_echo", "templated", "self_repeat_both"])
    j = m.join(ci, on="message_id", how="left").join(st, on="src_row", how="left").join(fl, on="srow", how="left").sort("ord")
    bad = (j["cross_echo"].fill_null(False) | j["templated"].fill_null(False) | j["self_repeat_both"].fill_null(False)).to_numpy()
    assert len(bad) == len(sk.t)
    return ~bad


def run_period(args) -> dict:
    g, full = args
    t0 = time.time()
    sk = C.load_period(g)
    multi = len(sk.meta["rooms_populated"]) >= 2
    if C.S0_MODE == "unread":
        modes = ("seen", "unseen")
    else:
        modes = ("seen", "unseen") if (multi and full) else ("seen",)
    n_null = C.P["n_null"] if full else 20
    if DEDUPE:
        keep = dedupe_mask(g, sk)
        orig = C.build_design
        C.build_design = lambda s, **kw: orig(s, **{**kw, "targets_mask": keep if len(s.t) == len(keep) else None})
    r = C.run_unit(sk, n_null=n_null, seed=C.SEED + g, modes=modes, do_human=full, n_withinday=20 if full else 0)
    nodes = r["nodes"]
    out = {"goal_no": g, "variant": OUTV.name, "nodes": nodes, "out": r["out"].tolist(), "net": r["net"].tolist(),
           "z_out": r["z_out"].tolist(), "T": r["T"], "p_T": r["p_T"], "T_trim": r["T_trim"], "p_T_trim": r["p_T_trim"],
           "standout": r["standout"], "p_standout": r["p_standout"], "p_max": r["p_max"], "n_null": n_null,
           "cent_nullvar": r["cent_nullvar"], "top": int(nodes[int(np.nanargmax(r["out"]))])}
    if DEDUPE:
        out["targets_kept_frac"] = float(keep[sk.spk < 100].mean())
    if "withinday" in r:
        out["withinday"] = {"T": r["withinday"]["T"], "p_T": r["withinday"]["p_T"]}
    if r.get("human") is not None and np.isfinite(r["human"]["out"]):
        o = np.array(r["out"], float)
        out["human"] = {"out": r["human"]["out"], "z": r["human"]["z"], "rank_out": int(1 + np.sum(o > r["human"]["out"])),
                        "above_median_agent": bool(r["human"]["out"] > np.nanmedian(o))}
    for m in modes[1:]:
        out[f"T_{m}"] = r[f"T_{m}"]; out[f"p_T_{m}"] = r[f"p_T_{m}"]
    if full:
        D = sorted(set(int(x) for x in sk.day))
        if len(D) >= 4 and len(nodes) >= 6:
            odd, even = [d for d in D if d % 2 == 1], [d for d in D if d % 2 == 0]
            ro = C.run_unit(sk.subset_days(odd), n_null=20, seed=C.SEED + g + 1, do_human=False)
            re_ = C.run_unit(sk.subset_days(even), n_null=20, seed=C.SEED + g + 2, do_human=False)
            oo = dict(zip(ro["nodes"], ro["out"])); ee = dict(zip(re_["nodes"], re_["out"]))
            com = [a for a in nodes if a in oo and a in ee]
            out["split_half"] = {"rho_out": sp([oo[a] for a in com], [ee[a] for a in com]), "n": len(com)}
    sh = out.get("split_half", {}).get("rho_out")
    if out["p_T"] >= 0.05:
        v = "failed"
    elif (sh is not None and sh > 0) or (sh is None and out["p_standout"] < 0.05):
        v = "supported"
    else:
        v = "mixed"
    out["verdict_general"] = v if full else None
    out["runtime_s"] = time.time() - t0
    d = OUTV / f"G{g:02d}"
    d.mkdir(parents=True, exist_ok=True)
    (d / "result.json").write_text(json.dumps(out, indent=1, default=float))
    print(g, OUTV.name, f"T={out['T']*100:.3f}% p={out['p_T']:.3f}", v, f"{out['runtime_s']:.0f}s", flush=True)
    return out


def natives():
    assert C.EMB_VARIANT == "bge" and C.S0_MODE == "other"
    ro = pl.read_parquet(C.SH / "roster.parquet")
    N = dict(zip(ro["agent"].to_list(), ro["name"].to_list())); N[C.HUMAN] = "humans"
    gt = pl.read_parquet(C.SH / "ground_truth_labels.parquet").filter(pl.col("preferred") & ~pl.col("holdout"))
    res = {}

    def rank_of(r, a):
        vals = {int(k): v["dG"] for k, v in r.items() if np.isfinite(v["dG"])}
        order = sorted(vals, key=lambda k: -vals[k])
        return (order.index(a) + 1 if a in vals else None), len(order)

    # #26 term 1
    sk = C.load_period(26)
    lead = gt.filter((pl.col("goal_no") == 26) & (pl.col("label_kind") == "leader")).sort("t_valid_from")
    t1a, t1b = lead["t_valid_from"][0].timestamp(), lead["t_valid_to"][0].timestamp()
    seg = (sk.t >= t1a) & (sk.t < t1b)
    cnt = {int(a): int(((sk.spk == a)).sum()) for a in sk.agents}
    src = [int(a) for a in sk.agents if cnt[int(a)] >= 10]
    r = C.pooled_sender_gain(sk, seg, src, n_null=40)
    rk, n = rank_of(r, 17)
    res["G26_term1"] = {"window": [lead["t_valid_from"][0].isoformat(), lead["t_valid_to"][0].isoformat()], "rank_17": rk, "n": n,
                        "z_17": r[17]["z"], "dG_17": r[17]["dG"], "n_targets": int(seg.sum()),
                        "per_agent": {N.get(k, str(k)): (round(v["dG"] * 100, 4), round(v["z"], 2)) for k, v in r.items()}}
    res["G26_term1"]["verdict"] = ("supported" if (rk == 1 and r[17]["z"] >= 2) else
                                   "failed" if (rk is not None and rk >= 3 and r[17]["z"] < 2) else "mixed")
    # #35 lead designers per room-day
    sk = C.load_period(35)
    rooms = dict(zip(*pl.read_parquet(C.SH / "rooms.parquet").select("name", "room").to_dict(as_series=False).values()))
    L = gt.filter((pl.col("goal_no") == 35) & (pl.col("label_kind") == "leader")).sort("t_valid_from")
    rows, pct = [], []
    for x in L.iter_rows(named=True):
        room = rooms[x["detail"].split(";")[0].replace("room=", "").strip()]
        a0, a1 = x["t_valid_from"].timestamp(), x["t_valid_to"].timestamp()
        seg = (sk.t >= a0) & (sk.t < a1) & (sk.room == room)
        present = sorted(set(int(a) for a in sk.spk[seg] if a < 100 and int(((sk.spk == a) & seg).sum()) >= 3))
        if x["agent"] not in present or len(present) < 2:
            rows.append({"day": x["t_valid_from"].isoformat(), "room": room, "leader": int(x["agent"]), "present": present,
                         "note": "leader has < 3 messages in its room-day"})
            continue
        r = C.pooled_sender_gain(sk, seg, present, n_null=40, seed=C.SEED + int(x["agent"]))
        rk, n = rank_of(r, int(x["agent"]))
        p = None if rk is None or n < 2 else 1 - (rk - 1) / (n - 1)
        if p is not None:
            pct.append((p, n))
        rows.append({"day": x["t_valid_from"].isoformat(), "room": room, "leader": int(x["agent"]), "rank": rk, "n": n,
                     "percentile": p, "z": r[int(x["agent"])]["z"], "n_targets": int(seg.sum())})
    # exact permutation null for the mean percentile (each segment: uniform over ranks)
    rng = np.random.default_rng(35)
    obs = float(np.mean([p for p, _ in pct])) if pct else float("nan")
    null = np.array([np.mean([1 - (rng.integers(0, n)) / (n - 1) for _, n in pct]) for _ in range(20000)]) if pct else np.array([])
    top_half = int(sum(p > 0.5 for p, _ in pct))
    pv = float((1 + np.sum(null >= obs)) / (1 + len(null))) if len(null) else float("nan")
    res["G35_leads"] = {"segments": rows, "mean_percentile": obs, "p_one_sided": pv, "top_half": top_half, "n_tested": len(pct),
                        "verdict": "supported" if (pv < 0.05 and top_half >= 4) else "failed" if (pv >= 0.05 and top_half <= 3) else "mixed"}
    # #44 leader window (#best, non-holdout days of #44)
    sk = C.load_period(44)
    x = gt.filter((pl.col("goal_no") == 44) & (pl.col("label_kind") == "leader"))
    a0 = x["t_valid_from"][0].timestamp()
    best = rooms["best"]
    seg = (sk.t >= a0) & (sk.room == best)
    present = sorted(set(int(a) for a in sk.spk[seg] if a < 100 and int(((sk.spk == a) & seg).sum()) >= 3))
    r = C.pooled_sender_gain(sk, seg, present + [C.HUMAN], n_null=40)
    ag = {k: v for k, v in r.items() if k != C.HUMAN}
    rk28, n = rank_of(ag, 28)
    rkh, nh = rank_of(r, C.HUMAN)
    res["G44_window"] = {"window_start": x["t_valid_from"][0].isoformat(), "rank_28_among_agents": rk28, "n_agents": n,
                         "z_28": r.get(28, {}).get("z"), "rank_operator_among_sources": rkh, "n_sources": nh,
                         "z_operator": r[C.HUMAN]["z"], "n_targets": int(seg.sum()),
                         "per_source": {N.get(k, str(k)): (round(v["dG"] * 100, 4), round(v["z"], 2)) for k, v in r.items()}}
    sup = (rk28 == 1 and (r.get(28, {}).get("z") or 0) >= 2) or (rkh == 1 and r[C.HUMAN]["z"] >= 2)
    res["G44_window"]["verdict"] = "supported" if sup else ("failed" if (rk28 is not None and rk28 > n / 2 and rkh != 1) else "mixed")
    (C.DATA / "r1b").mkdir(exist_ok=True)
    (C.DATA / "r1b" / "natives.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "periods"
    if cmd == "periods":
        full = len(sys.argv) > 2 and sys.argv[2] == "full"
        gs = periods() if len(sys.argv) < 4 else [int(x) for x in sys.argv[3].split(",")]
        with Pool(2) as pool:
            list(pool.imap_unordered(run_period, [(g, full) for g in gs]))
        pv = OUTV / "_provenance.json"
        pv.write_text(json.dumps({"built_by": "hypotheses/H32-information-current-leaders/analysis/r1b.py",
                                  "git_commit": __import__("common").git_commit(),
                                  "inputs": [{"source": "ai-village", "revision": __import__("common").REVISION,
                                              "tables": ["H32 messages/vectors (r1b variant)", "shared/call_windows",
                                                         "shared/rooms_timeline", "shared/statement_flags (dedupe)"]}],
                                  "params": {**{k: v for k, v in C.P.items()}, "variant": OUTV.name, "full": full},
                                  "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}, indent=1, default=str))
    elif cmd == "natives":
        natives()
