"""H06 round 1b (2026-10-04): the round-1 estimator on the corrected inputs, a ledger copying-channel test, natives.

Runs only with H06_DATA=r1b; round 1 (explore.py etc.) is unchanged. Labels from scheme/build_r1b.py.

Subcommands:
  replicate [--scopes ...]  per scope: the card's estimator (profile synthetic-likelihood fits of NCD, Hubbell and the
                            conformist model; LLRs, PPCs, P1-P4 verdicts) on intention clusters gte_sr (primary, the
                            6-clustering ladder; 3 k-means for #51) and the km24 comparison variants (gte_w, bge_w,
                            bge_sr), shared attention labels (art) and work labels; model-free statistics and the
                            day-shift null for every label set, testable or not.            -> r1b/<scope>/round1b.json
  copying [--scopes ...]    R1b-4: copying channel from the context ledger (V read / U posted-unread / N)
                                                                                            -> r1b/copying_r1b.json
  natives                   G35 (known universe), G51 (DQ6 rival pairs), G44 (two arms)     -> r1b/natives_r1b.json
  assemble                  cross-period table, estimates rows                              -> r1b/results_r1b.parquet
Usage: H06_DATA=r1b uv run python hypotheses/H06-neutral-cooperative-dynamics/analysis/round1b.py replicate --scopes G31
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from multiprocessing import get_context
from pathlib import Path

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import explore as X  # noqa: E402
import ncd_core as M  # noqa: E402

ROOT = X.ROOT
SHARED = ROOT / "data/processed/shared"
R1B = ROOT / "data/processed/H06-neutral-cooperative-dynamics/r1b"
from infra.shared import common as C  # noqa: E402

LADDER = ["km8", "km24", "km64", "wd8", "wd24", "wd64"]
COMPARE = ["gte_w_km24", "bge_w_km24", "bge_sr_km24"]
PRIMARY = "km24"
# scope -> (r1b folder, date range or None, role, room filter applied in analysis or None)
SCOPES = {k: (v[0], v[1], v[2], None) for k, v in X.SCOPES.items() if k not in ("G08", "G10", "NE33pre", "NE33post")}
SCOPES.update({"G35": ("G35", None, "native", None), "G35best": ("G35", None, "native", 2),
               "G35rest": ("G35", None, "native", 3), "G44best": ("G44best", None, "native", None)})
FREE = X.FREE


def need_r1b():
    if os.environ.get("H06_DATA") != "r1b":
        raise SystemExit("round 1b: set H06_DATA=r1b (round 1 is explore.py)")


def load(scope):
    folder, rng_, role, room = SCOPES[scope]
    d = R1B / folder
    wins = pl.read_parquet(d / "windows.parquet").sort("gwin")
    if rng_:
        wins = wins.filter((pl.col("pt_date") >= rng_[0]) & (pl.col("pt_date") <= rng_[1]))
    dates = sorted(set(wins["pt_date"].to_list()))
    g = int(folder[1:3])
    assert not any(C.holdout_mask(dates, [g] * len(dates))), "holdout"
    keep = wins["gwin"].to_list()
    remap = {x: i for i, x in enumerate(keep)}
    _, day = np.unique(wins["day"].to_numpy(), return_inverse=True)
    labs = {}
    for nm in ("int", "art", "work"):
        df = pl.read_parquet(d / f"labels_{nm}.parquet").filter(pl.col("gwin").is_in(keep))
        if room is not None:
            df = df.filter(pl.col("room") == room)
        labs[nm] = df
    return wins, day, remap, labs, role


def freestats(lab, day, seed):
    """Model-free statistics and the day-shift independent-agents null for any label set."""
    t = M.label_stats(lab, day)
    c, f, n_tr, n_ch, n_nov = M.moments(lab, day)
    nobs = (lab >= 0).sum(1)
    out = {"N": int(lab.shape[1]), "mean_per_win": float(nobs.mean()), "n_changes": int(n_ch), "c": float(c), "f_nov": float(f),
           "lam": t["lam"], "single": t["single"], "xmax": t["xmax"], "rich": t["rich"], "beta": t["beta"],
           "beta_se": t["beta_se"], "n_events": t["n_events"], "copyfrac": t["copyfrac"], "n_species": t["n_species"]}
    if lab.shape[1] >= 2 and int(day.max()) >= 1 and (nobs >= 2).any():
        nul = X.day_shift_null(lab, day, seed=seed)
        out["null_lam"] = float(np.nanmean(nul[:, 0]))
        out["null_lam_p"] = float((np.sum(nul[:, 0] >= t["lam"]) + 1) / (len(nul) + 1))
        out["null_copy"] = float(np.nanmean(nul[:, 1]))
        out["null_copy_p"] = float((np.sum(nul[:, 1] >= t["copyfrac"]) + 1) / (len(nul) + 1))
    return out


def slim(r):
    """Compact per-label-set record (drop histograms and scatter)."""
    keep = {k: v for k, v in r.items() if k not in ("hist", "res_max")}
    if "fits" in keep:
        keep["fits"] = {m: {k: v for k, v in f.items() if k not in ("hist_mean",)} for m, f in keep["fits"].items()}
    return keep


def run_scope(scope):
    t0 = time.time()
    wins, day, remap, labs, role = load(scope)
    T = wins.height
    out = {"scope": scope, "role": role, "T": T, "days": int(day.max()) + 1,
           "pt_dates": sorted(set(wins["pt_date"].to_list())), "sets": {}, "free": {}}
    lint = labs["int"]
    agents = sorted(set(lint["agent"].to_list()))
    cols = [k for k in LADDER + COMPARE if k in lint.columns and (lint[k] >= 0).any()]
    if cols:
        li = {k: X.matrix(lint, k, remap, T, agents)[0] for k in cols}
        mask = li[PRIMARY] >= 0
        for k, lab in li.items():
            assert ((lab >= 0) == mask).all()
            out["free"][k] = freestats(lab, day, M._seed(scope, k, "r1b"))
        bank = M.Bank(mask, day, seed=M._seed(scope, "int"))
        for k, lab in li.items():
            out["sets"][k] = slim(X.analyse_labelset(f"{scope}/{k}", lab, day, bank,
                                                     extra=(k == PRIMARY or k in COMPARE), seed=0))
    for nm in ("art", "work"):
        df = labs[nm]
        if df.height == 0:
            continue
        lab, _ = X.matrix(df, "project_id", remap, T)
        out["free"][nm] = freestats(lab, day, M._seed(scope, nm, "r1b"))
        if (lab >= 0).sum(1).mean() < X.MIN_PER_WIN:
            out["sets"][nm] = {"labelset": f"{scope}/{nm}", "testable": False, "mean_per_win": float((lab >= 0).sum(1).mean()),
                               "N": lab.shape[1]}
            continue
        bank = M.Bank(lab >= 0, day, seed=M._seed(scope, nm, "r1b"))
        out["sets"][nm] = slim(X.analyse_labelset(f"{scope}/{nm}", lab, day, bank, extra=True))
    S = out["sets"]
    out["P1"] = X.verdict_p1({k: S[k] for k in LADDER if k in S}) if PRIMARY in S else {"verdict": "n/a"}
    for k in COMPARE + ["art", "work"]:
        out[f"P1_{k}"] = X.verdict_simple(S.get(k))
    out["P2"], out["P3"], out["P4"] = X.p2(S.get(PRIMARY)), X.p3(S.get(PRIMARY)), X.p4(S.get(PRIMARY))
    for k in ("art", "work"):
        out[f"P2_{k}"], out[f"P3_{k}"] = X.p2(S.get(k)), X.p3(S.get(k))
    out["secs"] = time.time() - t0
    (R1B / SCOPES[scope][0]).mkdir(parents=True, exist_ok=True)
    with open(R1B / SCOPES[scope][0] / f"round1b_{scope}.json", "w") as fh:
        json.dump(out, fh, indent=1, default=float)
    print(f"{scope}: {out['secs']:.0f}s P1 {out['P1'].get('verdict')} | art {out['P1_art']} | work {out['P1_work']}", flush=True)
    return scope


def replicate(scopes, workers):
    with get_context("spawn").Pool(min(2, workers)) as pool:
        for s in pool.imap_unordered(run_scope, scopes, chunksize=1):
            pass


# ------------------------------------------------------------------------------------------------ R1b-4 copying channel
def _messages(goals):
    """Agent chat messages with the projects they name (strict mentions; files/sites -> parent repo)."""
    sys.path.insert(0, str(ROOT / "infra/shared"))
    import project_states as PS
    pm = PS.project_map()
    am = pl.scan_parquet(SHARED / "artifact_mentions.parquet").filter(
        (pl.col("source").cast(pl.String) == "chat") & pl.col("how").cast(pl.String).is_in(["url", "output", "bare"])
        & pl.col("message_id").is_not_null()).select("artifact", "message_id").collect()
    am = am.join(pm, on="artifact", how="inner").select("message_id", "project").unique()
    cc = pl.read_parquet(SHARED / "chat_core.parquet", columns=["message_id", "t", "room", "speaker_kind", "agent", "goal_no"]).filter(
        pl.col("goal_no").is_in(goals) & (pl.col("speaker_kind").cast(pl.String) == "agent"))
    return cc.join(am, on="message_id", how="inner")


def _reads(goals, msg_ids):
    cw = pl.scan_parquet(SHARED / "call_windows.parquet").filter(pl.col("goal_no").is_in(goals)).select(
        "turn_id", "agent", "t_call").collect()
    it = pl.scan_parquet(SHARED / "context_ledger_items.parquet").filter(pl.col("message_id").is_in(msg_ids)).select(
        "turn_id", "message_id").collect()
    return it.join(cw, on="turn_id", how="inner").select("message_id", pl.col("agent").alias("recipient"), "t_call")


def mh_or(tab):
    """Mantel-Haenszel odds ratio over strata; tab: list of (a, b, c, d) = (exp&Y, exp&~Y, ref&Y, ref&~Y).
    Robins-Breslow-Greenland 95% CI."""
    num = den = 0.0
    P = Q = R = S = 0.0
    for a, b, c, d in tab:
        n = a + b + c + d
        if n == 0:
            continue
        r_, s_ = a * d / n, b * c / n
        num += r_
        den += s_
        p_, q_ = (a + d) / n, (b + c) / n
        P += p_ * r_
        Q += p_ * s_ + q_ * r_
        R += q_ * s_
    if num == 0 or den == 0:
        return {"or": float("nan"), "lo": float("nan"), "hi": float("nan")}
    orr = num / den
    var = P / (2 * num ** 2) + Q / (2 * num * den) + R / (2 * den ** 2)
    se = var ** 0.5
    return {"or": orr, "lo": float(np.exp(np.log(orr) - 1.96 * se)), "hi": float(np.exp(np.log(orr) + 1.96 * se)), "se_log": se}


def copying_scope(scope, nm, msgs, reads):
    wins, day, remap, labs, role = load(scope)
    df = labs[nm]
    if df.height == 0:
        return None
    folder = SCOPES[scope][0]
    proj = pl.read_parquet(R1B / folder / f"projects_{nm}.parquet")
    pid2name = dict(zip(proj["project_id"].to_list(), proj["project"].to_list()))
    lab, agents = X.matrix(df, "project_id", remap, wins.height)
    T, N = lab.shape
    tmid = wins["t_mid"].to_list()
    import datetime as dt
    half = dt.timedelta(minutes=15)
    ws = [t - half for t in tmid]
    we = [t + half for t in tmid]
    g = int(folder[1:3])
    m = msgs.filter(pl.col("goal_no") == g)
    rd = reads.join(m.select("message_id").unique(), on="message_id", how="semi")
    rd_by = {}
    for mid, rc, tc in rd.iter_rows():
        rd_by.setdefault(mid, {}).setdefault(rc, tc)
        if tc < rd_by[mid][rc]:
            rd_by[mid][rc] = tc
    import bisect
    wsl = list(ws)
    def widx(t_):
        i = bisect.bisect_right(wsl, t_) - 1
        return i if 0 <= i < T and t_ < we[i] else None
    ai = {ag: i for i, ag in enumerate(agents)}
    V = {}   # (t, a) -> projects read during window t (messages by others)
    posted = {}  # t -> list of (message_id, sender, project)
    for mid, tm_, snd, pr in m.select("message_id", "t", "agent", "project").iter_rows():
        tp = widx(tm_)
        if tp is not None:
            posted.setdefault(tp, []).append((mid, snd, pr))
        for rc, tr in rd_by.get(mid, {}).items():
            if rc == snd or rc not in ai:
                continue
            tw = widx(tr)
            if tw is not None:
                V.setdefault((tw, ai[rc]), set()).add(pr)
    rows = []
    counts = {"V": [0, 0], "U": [0, 0], "N": [0, 0]}
    for t in range(T - 1):
        if day[t] != day[t + 1]:
            continue
        held = {}
        for a in range(N):
            if lab[t, a] >= 0:
                held.setdefault(lab[t, a], set()).add(a)
        for a in range(N):
            if lab[t, a] < 0 or lab[t + 1, a] < 0:
                continue
            ag = agents[a]
            Va = V.get((t, a), set())
            Ua = set()
            for mid, snd, pr in posted.get(t, []):
                if snd == ag:
                    continue
                tr = rd_by.get(mid, {}).get(ag)
                if tr is None or tr >= we[t]:
                    Ua.add(pr)
            for q, hs in held.items():
                if q == lab[t, a]:
                    continue
                others = hs - {a}
                if not others:
                    continue
                name = pid2name.get(int(q))
                cls = "V" if name in Va else ("U" if name in Ua else "N")
                y = int(lab[t + 1, a] == q)
                rows.append((min(len(others), 3), cls, y))
                counts[cls][0] += y
                counts[cls][1] += 1
    return rows, counts


def copying(scopes):
    goals = sorted({int(SCOPES[s][0][1:3]) for s in scopes})
    msgs = _messages(goals)
    reads = _reads(goals, msgs["message_id"].unique().to_list())
    res = {}
    pooled = {nm: [] for nm in ("art", "work")}
    for s in scopes:
        for nm in ("art", "work"):
            r = copying_scope(s, nm, msgs, reads)
            if r is None:
                continue
            rows, counts = r
            res.setdefault(s, {})[nm] = {k: {"switches": v[0], "candidates": v[1], "rate": (v[0] / v[1]) if v[1] else None}
                                         for k, v in counts.items()}
            pooled[nm] += [(s, *x) for x in rows]
            print(s, nm, res[s][nm], flush=True)
    summary = {}
    for nm, rows in pooled.items():
        if not rows:
            continue
        summ = {}
        for e, ref in (("V", "N"), ("V", "U"), ("U", "N")):
            tab = []
            for s in sorted({r[0] for r in rows}):
                for k in (1, 2, 3):
                    sub = [r for r in rows if r[0] == s and r[1] == k]
                    a = sum(1 for r in sub if r[2] == e and r[3] == 1)
                    b = sum(1 for r in sub if r[2] == e and r[3] == 0)
                    c = sum(1 for r in sub if r[2] == ref and r[3] == 1)
                    d = sum(1 for r in sub if r[2] == ref and r[3] == 0)
                    tab.append((a, b, c, d))
            summ[f"OR_{e}_vs_{ref}"] = mh_or(tab)
        summ["n_candidates"] = {c: sum(1 for r in rows if r[2] == c) for c in "VUN"}
        summ["n_switches"] = {c: sum(1 for r in rows if r[2] == c and r[3] == 1) for c in "VUN"}
        summ["scopes"] = sorted({r[0] for r in rows})
        summary[nm] = summ
    out = {"per_scope": res, "pooled": summary,
           "design": "candidate (agent i labelled at t and t+1 same day, project q held by another agent at t, q != i's "
                     "label at t); Y = i holds q at t+1. V: a chat message by another agent with a strict mention of q "
                     "entered one of i's calls during window t (context ledger); U: such a message was posted during t but "
                     "had not entered i's context by the end of t; N: neither. MH over (scope, abundance of q at t: 1/2/3+)."}
    (R1B / "copying_r1b.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(summary, indent=1, default=float))


# ------------------------------------------------------------------------------------------------ natives
FORK = {2: "github.com/ai-village-agents/rpg-game-best", 3: "github.com/ai-village-agents/rpg-game-rest"}


def native_g35():
    out = {}
    wins, day, remap, labs, _ = load("G35")
    for nm in ("art", "work"):
        df = labs[nm]
        proj = pl.read_parquet(R1B / "G35" / f"projects_{nm}.parquet")
        df = df.join(proj.with_columns(pl.col("project_id").cast(pl.Int32)), on="project_id", how="left")
        per = {}
        for room in (2, 3):
            d = df.filter(pl.col("room") == room)
            per[room] = {"labelled_aw": d.height, "own_fork_share": float((d["project"] == FORK[room]).mean()) if d.height else None,
                         "other_fork_share": float((d["project"] == FORK[5 - room]).mean()) if d.height else None}
        out[nm] = per
    L_ = json.loads((R1B / "light_r1b.json").read_text())
    for sc in ("G35best", "G35rest", "G35"):
        if sc in L_:
            out[sc] = L_[sc]["sets"]
    for nm in ("work", "art", "km24"):
        f = R1B / "G35" / f"fit_G35_{nm}.json"
        if f.exists():
            r = json.loads(f.read_text())
            out[f"fit_{nm}"] = {"testable": r.get("testable"), "verdict": r.get("verdict"),
                                "ppc_joint": {m: r["fits"][m]["ppc_joint"] for m in M.MODELS} if r.get("fits") else None,
                                "adequate": {m: r["fits"][m]["adequate"] for m in M.MODELS} if r.get("fits") else None,
                                "LLR_NH": r.get("LLR_NH"), "LLR_NC": r.get("LLR_NC"), "obs": r.get("obs"),
                                "copyfrac": r.get("copyfrac"), "mean_per_win": r.get("mean_per_win"),
                                "n_changes": r.get("n_changes")}
    return out


def native_g51(n_perm=999):
    gt = pl.read_parquet(SHARED / "ground_truth_labels.parquet").filter(
        (pl.col("goal_no") == 51) & pl.col("preferred") & ~pl.col("holdout") & (pl.col("label_kind") == "rival_pair"))
    pairs = [(int(a), int(b), tf, tt) for a, b, tf, tt in gt.select("agent_a", "agent_b", "t_valid_from", "t_valid_to").iter_rows()]
    res = {}
    for scope in ("G51a", "G51b", "G51c"):
        wins, day, remap, labs, _ = load(scope)
        tmid = wins["t_mid"].to_list()
        rb = {}
        for nm, colname in (("int", PRIMARY), ("art", "project_id"), ("work", "project_id")):
            df = labs[nm]
            lab, agents = X.matrix(df, colname, remap, wins.height)
            T, N = lab.shape
            # rival indicator per window: pair valid at t_mid
            riv = np.zeros((T, N, N), dtype=bool)
            ai = {a: i for i, a in enumerate(agents)}
            for a, b, tf, tt in pairs:
                if a in ai and b in ai:
                    for t in range(T):
                        if tf <= tmid[t] < tt:
                            riv[t, ai[a], ai[b]] = riv[t, ai[b], ai[a]] = True
            same = np.zeros((T, N, N), dtype=bool)
            both = np.zeros((T, N, N), dtype=bool)
            for t in range(T):
                o = lab[t] >= 0
                both[t] = o[:, None] & o[None, :]
                same[t] = (lab[t][:, None] == lab[t][None, :]) & both[t]
            iu = np.triu_indices(N, 1)

            def ratio(rv):
                B, S, Rv = both[:, iu[0], iu[1]], same[:, iu[0], iu[1]], rv[:, iu[0], iu[1]]
                nr, no = (B & Rv).sum(), (B & ~Rv).sum()
                if nr == 0 or no == 0:
                    return float("nan"), int(nr), int(no)
                sr, so = (S & Rv).sum() / nr, (S & ~Rv).sum() / no
                return (sr / so if so > 0 else float("inf")), int(nr), int(no), float(sr), float(so)
            obs = ratio(riv)
            rng = np.random.default_rng(M._seed(scope, nm, "g51perm"))
            nul = []
            for _ in range(n_perm):
                p = rng.permutation(N)
                nul.append(ratio(riv[:, p][:, :, p])[0])
            nul = np.array(nul, dtype=float)
            ok = np.isfinite(nul)
            pval = float((np.sum(nul[ok] >= obs[0]) + 1) / (ok.sum() + 1)) if np.isfinite(obs[0]) else float("nan")
            rb[nm] = {"R": obs[0], "rival_pair_windows": obs[1], "other_pair_windows": obs[2],
                      "s_rival": obs[3] if len(obs) > 3 else None, "s_other": obs[4] if len(obs) > 4 else None,
                      "null_median": float(np.nanmedian(nul)), "p": pval}
        res[scope] = rb
        print(scope, json.dumps(rb, default=float), flush=True)
    return res


def native_g44():
    L_ = json.loads((R1B / "light_r1b.json").read_text())
    out = {}
    for sc in ("G44", "G44best"):
        out[sc] = {}
        for k in ("km24", "art", "work"):
            s_ = L_[sc]["sets"].get(k)
            if not s_:
                continue
            out[sc][k] = dict(s_, lam_excess=s_["lam"] - s_["null_lam"],
                              copy_excess=(s_["copyfrac"] - s_["null_copy"]) if s_["copyfrac"] == s_["copyfrac"] else None)
    return out


def natives():
    out = {"G35": native_g35(), "G51": native_g51(), "G44": native_g44()}
    (R1B / "natives_r1b.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out["G35"], indent=1, default=float)[:3000])
    print(json.dumps(out["G44"], indent=1, default=float))


# ------------------------------------------------------------------------------------------------ light replication
LIGHT_SETS = ["km24", "gte_w_km24", "bge_w_km24", "bge_sr_km24", "art", "work"]


def fast_stats(lab, day):
    T, N = lab.shape
    obs = lab >= 0
    lam, single, occ = [], 0, 0
    n_copy = n_nc = 0
    seen = set()
    cnts = []
    for t in range(T):
        v = lab[t][obs[t]]
        if len(v) == 0:
            cnts.append({})
            continue
        u, c = np.unique(v, return_counts=True)
        cnts.append(dict(zip(u.tolist(), c.tolist())))
        occ += len(c)
        single += int((c == 1).sum())
        if len(v) >= 2:
            x = c / len(v)
            lam.append(float((x * x).sum()))
    for t in range(T - 1):
        seen.update(cnts[t].keys())
        if day[t] != day[t + 1] or obs[t].sum() < 2:
            continue
        for a in np.flatnonzero(obs[t] & obs[t + 1]):
            o, nw = lab[t, a], lab[t + 1, a]
            if o == nw or nw not in seen:
                continue
            if cnts[t].get(nw, 0) - (1 if nw == o else 0) > 0:
                n_copy += 1
            else:
                n_nc += 1
    return (float(np.mean(lam)) if lam else float("nan"), single / occ if occ else float("nan"),
            n_copy / (n_copy + n_nc) if (n_copy + n_nc) else float("nan"), n_copy + n_nc)


def shift_null(lab, day, n, seed):
    rng = np.random.default_rng(seed)
    D = int(day.max()) + 1
    T, N = lab.shape
    starts = [np.flatnonzero(day == d) for d in range(D)]
    out = []
    for _ in range(n):
        sh = np.full_like(lab, -1)
        for a in range(N):
            k = int(rng.integers(0, D))
            for d in range(D):
                src, dst = starts[(d + k) % D], starts[d]
                mm = min(len(src), len(dst))
                sh[dst[:mm], a] = lab[src[:mm], a]
        out.append(fast_stats(sh, day)[:3])
    return np.array(out)


def light_scope(scope, n_null=100):
    wins, day, remap, labs, role = load(scope)
    T = wins.height
    res = {"scope": scope, "role": role, "T": T, "days": int(day.max()) + 1, "sets": {}}
    lint = labs["int"]
    agents = sorted(set(lint["agent"].to_list()))
    for k in LIGHT_SETS:
        if k in ("art", "work"):
            df = labs[k]
            if df.height == 0:
                continue
            lab, _ = X.matrix(df, "project_id", remap, T)
        else:
            if k not in lint.columns or not (lint[k] >= 0).any():
                continue
            lab, _ = X.matrix(lint, k, remap, T, agents)
        lam, single, cc, nsw = fast_stats(lab, day)
        r = {"N": int(lab.shape[1]), "per_win": float((lab >= 0).sum(1).mean()), "lam": lam, "single": single,
             "copyfrac": cc, "n_switch_nonnovel": nsw}
        if int(day.max()) >= 1 and lab.shape[1] >= 2:
            nul = shift_null(lab, day, n_null, M._seed(scope, k, "light"))
            r.update({"null_lam": float(np.nanmean(nul[:, 0])), "p_lam": float((np.sum(nul[:, 0] >= lam) + 1) / (n_null + 1)),
                      "null_single": float(np.nanmean(nul[:, 1])),
                      "null_copy": float(np.nanmean(nul[:, 2])),
                      "p_copy": float((np.sum(nul[:, 2] >= cc) + 1) / (n_null + 1)) if np.isfinite(cc) else None})
        res["sets"][k] = r
    # round-1 values for old -> new
    f1 = ROOT / "data/processed/H06-neutral-cooperative-dynamics" / SCOPES[scope][0] / f"round1_{scope}.json"
    if f1.exists():
        r1 = json.loads(f1.read_text())["sets"]
        res["round1"] = {k: {"lam": v["obs"]["lam"], "single": v["obs"]["single"], "copyfrac": v["copyfrac"]}
                         for k, v in r1.items() if v.get("testable") and k in ("km24", "art")}
    return res


def light(scopes):
    out = {}
    with get_context("spawn").Pool(1) as pool:
        for r in pool.imap_unordered(light_scope, scopes):
            out[r["scope"]] = r
            print(r["scope"], {k: (round(v["lam"], 3), round(v["single"], 3), round(v["copyfrac"], 3) if v["copyfrac"] == v["copyfrac"] else None)
                               for k, v in r["sets"].items()}, flush=True)
    f = R1B / "light_r1b.json"
    old = json.loads(f.read_text()) if f.exists() else {}
    old.update(out)
    f.write_text(json.dumps(old, indent=1, default=float))


def fit_one(scope, nm):
    """Model fits on one label set of one scope (the card's estimator), for natives and spot checks."""
    t0 = time.time()
    wins, day, remap, labs, role = load(scope)
    T = wins.height
    if nm in ("art", "work"):
        lab, _ = X.matrix(labs[nm], "project_id", remap, T)
    else:
        lint = labs["int"]
        lab, _ = X.matrix(lint, nm, remap, T, sorted(set(lint["agent"].to_list())))
    bank = M.Bank(lab >= 0, day, seed=M._seed(scope, nm, "r1b"))
    r = X.analyse_labelset(f"{scope}/{nm}", lab, day, bank, extra=False)
    r = slim(r)
    r["verdict"] = X.verdict_simple(r)
    r["secs"] = time.time() - t0
    (R1B / SCOPES[scope][0] / f"fit_{scope}_{nm}.json").write_text(json.dumps(r, indent=1, default=float))
    print(scope, nm, r.get("testable"), r.get("verdict"), {m: r["fits"][m]["ppc_joint"] for m in M.MODELS} if r.get("fits") else None,
          f"{r['secs']:.0f}s", flush=True)


def main():
    need_r1b()
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["replicate", "copying", "natives", "light", "fit", "estimates"])
    ap.add_argument("--set", default="work")
    ap.add_argument("--scopes", nargs="*", default=None)
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    if a.what == "replicate":
        replicate(a.scopes or list(SCOPES), a.workers)
    elif a.what == "copying":
        copying(a.scopes or ["G31", "G37", "G44", "G30", "G38", "G19", "G25"])
    elif a.what == "natives":
        natives()
    elif a.what == "light":
        light(a.scopes or list(SCOPES))
    elif a.what == "estimates":
        estimates()
    elif a.what == "fit":
        for sc in a.scopes:
            fit_one(sc, a.set)


def estimates():
    """Per-period estimate rows (round 1b) into the shared table."""
    sys.path.insert(0, str(ROOT / "infra/shared"))
    import estimates as E
    L_ = json.loads((R1B / "light_r1b.json").read_text())
    nat = json.loads((R1B / "natives_r1b.json").read_text())
    src = "data/processed/H06-neutral-cooperative-dynamics/r1b/"
    rows = []

    def unit(scope):
        folder, rng_, _, room = SCOPES[scope]
        g = int(folder[1:3])
        if rng_:
            u = E.map_unit(g, rng_[0], rng_[1])
            return g, (u or f"local:{scope}"), rng_
        return g, (E.map_unit(g) if room is None and scope not in ("G44best",) else f"local:{scope}"), None
    for scope, r in L_.items():
        g, u, rng_ = unit(scope)
        role = "native" if SCOPES[scope][2] == "native" else "replication"
        for k, ch in (("km24", "stated goals (gte style_resid_period, km24)"), ("work", "work (DQ4 commits)"),
                      ("art", "attention (project_states)")):
            s_ = r["sets"].get(k)
            if not s_ or not np.isfinite(s_["single"]):
                continue
            base = dict(goal_no=g, period_unit=u, channel=ch, role=role, source=src + "light_r1b.json", post_hoc=False,
                        status="exploratory round 1b", first_day=rng_[0] if rng_ else None, last_day=rng_[1] if rng_ else None)
            rows.append(dict(base, statistic="singleton_fraction", estimate=s_["single"], n=s_["N"], n_kind="agent slots",
                             ci_kind="none", null=f"day-shift independent agents: {s_.get('null_single')}",
                             method="share of species occurrences per 30-min window held by one agent (H06 round 1b)"))
            if np.isfinite(s_["lam"]) and s_.get("null_lam") is not None:
                rows.append(dict(base, statistic="simpson_lambda_excess_over_dayshift", estimate=s_["lam"] - s_["null_lam"],
                                 n=s_["N"], n_kind="agent slots", ci_kind="none", null="day-shift independent agents (100 draws)",
                                 method="mean Simpson lambda over windows minus its day-shift null mean (H06 round 1b)"))
    for f in sorted(R1B.glob("*/fit_*.json")) + sorted(R1B.glob("*/round1b_*.json")):
        d = json.loads(f.read_text())
        items = [(f.stem.split("_")[1], f.stem.split("_", 2)[2], d)] if f.stem.startswith("fit_") else \
            [(d["scope"], k, d["sets"][k]) for k in ("km24", "work", "art") if k in d["sets"]]
        for scope, k, s_ in items:
            if not s_.get("testable"):
                continue
            g, u, rng_ = unit(scope)
            ch = {"km24": "stated goals (gte style_resid_period, km24)", "work": "work (DQ4 commits)", "art": "attention (project_states)"}[k]
            rows.append(dict(goal_no=g, period_unit=u, channel=ch, role="replication", source=src + f"{f.parent.name}/{f.name}",
                             post_hoc=False, status="exploratory round 1b", statistic="ncd_joint_ppc_p",
                             estimate=s_["fits"]["ncd"]["ppc_joint"], n=400, n_kind="simulated replicates", ci_kind="none",
                             null="NCD at its profile synthetic-likelihood fit", first_day=rng_[0] if rng_ else None,
                             last_day=rng_[1] if rng_ else None,
                             method="joint Mahalanobis posterior-predictive p of 9 statistics under fitted NCD (H06 round 1b)"))
            rows.append(dict(goal_no=g, period_unit=u, channel=ch, role="replication", source=src + f"{f.parent.name}/{f.name}",
                             post_hoc=False, status="exploratory round 1b", statistic="llr_ncd_minus_hubbell",
                             estimate=s_["LLR_NH"], n=400, n_kind="simulated replicates", ci_kind="none",
                             null="LLR = 0", first_day=rng_[0] if rng_ else None, last_day=rng_[1] if rng_ else None,
                             method="Gaussian synthetic log-likelihood, NCD minus Hubbell (H06 round 1b)"))
    for blk, v in nat["G51"].items():
        g, u, rng_ = unit(blk)
        for k, s_ in v.items():
            if s_["R"] is None or not np.isfinite(s_["R"]):
                continue
            rows.append(dict(goal_no=51, period_unit=u, channel={"int": "stated goals", "art": "attention", "work": "work"}[k],
                             role="native", source=src + "natives_r1b.json", post_hoc=False, status="exploratory round 1b native",
                             statistic="rival_pair_colabel_ratio", estimate=s_["R"], n=s_["rival_pair_windows"],
                             n_kind="rival pair-windows", ci_kind="none", null=f"agent permutation (999), p = {s_['p']:.3f}",
                             first_day=rng_[0], last_day=rng_[1],
                             method="same-label rate of DQ6 rival pairs / other pairs per 30-min window"))
    E.write_estimates(rows, hypothesis="H06", replace_keys=("statistic", "channel", "method", "role", "source"))
    print(f"estimates: {len(rows)} rows")


if __name__ == "__main__":
    main()
