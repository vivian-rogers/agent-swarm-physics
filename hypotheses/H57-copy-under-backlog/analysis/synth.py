"""H57 synthetic validation (axis F): synthetic content written on REAL read-out schedules, analysed with the exact
real-data code path (h57core.outcomes -> h57lib.prepare / slope / decomposition / pointwise).

  uv run python hypotheses/H57-copy-under-backlog/analysis/synth.py --period 40 --seeds 20
  uv run python hypotheses/H57-copy-under-backlog/analysis/synth.py --period 51 --unit 51c --seeds 10

World (per message, in time order over the period's agent messages):
  - latent content v in d = 48 with anisotropic noise (simulate.aniso_shape); a period topic, a kickoff direction, a
    room-day topic that drifts in 10-min bins (local topic phase), agent style offsets, a fixed transformation map T;
  - a statement with read set R (the real ledger read set) copies an item of R with probability pi, else transforms
    one (v = 0.7 T v_A + topic + style + noise); the source is drawn with recency weights 0.8^(rank-1)
    (attention dilution); messages without a read set are topic + style + noise;
  - copy probability: load  logit pi = logit pi0 + 0.35 (log2(1+k) - mean)   (H57)
                      const pi = pi0                                         (null)
                      phase logit pi = logit pi0 + 1.0 (early - mean)        (rival a)
  - shared sources on in every scenario: templates (3% of messages, 4 templates used by everyone) and kickoff quoting
    (15% on the first day, decaying e^-day) (rival b);
  - markers: new ids, topic-bin pools, template and kickoff sets; copies keep 80% of the source's markers;
  - two "embedding models": different random projections of v (64-d, 96-d) plus model-specific noise, PCA-whitened to
    32-d for the codebooks.
No real content is read: only the skeleton (statements, read sets, placebo sets, times, agents, rooms).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h57core as C  # noqa: E402
import h57lib as L  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(C.ROOT / "infra/shared"))
from simulate import aniso_shape  # noqa: E402

D = 48
DM = {"bge": 64, "gte": 96}
THR_SYN = {"bge": 0.90, "gte": 0.90}
OUTD = C.OUT / "synthetic"


def _unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-12)


def load_skeleton(goal_no: int, unit: str | None):
    S = pl.read_parquet(C.OUT / "skeleton" / f"G{goal_no:02d}_S.parquet")
    P = pl.read_parquet(C.OUT / "skeleton" / f"G{goal_no:02d}_P.parquet")
    if unit:
        keep = S.filter(pl.col("unit_id") == unit)
        P = P.filter(pl.col("sid").is_in(keep["sid"].to_list()))
        remap = {o: i for i, o in enumerate(keep["sid"].to_list())}
        S = keep.with_columns(pl.col("sid").replace_strict(remap, return_dtype=pl.Int32))
        P = P.with_columns(pl.col("sid").replace_strict(remap, return_dtype=pl.Int32))
    return S, P


def generate(S: pl.DataFrame, P: pl.DataFrame, scenario: str, seed: int, pi0: float = 0.10,
             b_load: float = 0.35, c_phase: float = 1.0, p_tmpl: float = 0.03, p_kick: float = 0.15,
             p_conv: float = 0.0, conv_s: float = 30.0):
    """p_conv: contemporaneous convergence (Amendment 2): with this probability a message adopts the content of its
    room's current 'moment' (a 30-s bin), whether or not anyone read anything, so agents posting at the same moment
    write near-duplicates without reading each other (seen in the real data: unread in-flight pairs are near-copies
    as often as read pairs at matched short lags)."""
    rng = np.random.default_rng(seed)
    msgs = np.unique(np.r_[S["msg"].to_numpy(), P.filter(pl.col("set") != 3)["msg"].to_numpy()]).astype(np.int64)
    meta = C.chat()[msgs].select("msg", "t", "agent", "room", "pt_date").with_row_index("loc")
    meta = meta.sort("t")
    n = len(msgs)
    loc_of = {int(m): i for i, m in enumerate(msgs)}
    days = sorted(meta["pt_date"].unique().to_list())
    dix = {d: i for i, d in enumerate(days)}
    Lc = aniso_shape(rng, D, k0=6.0)
    mu = _unit(rng.standard_normal(D))
    kappa = _unit(mu + 0.6 * _unit(rng.standard_normal(D)))
    Tm, _ = np.linalg.qr(rng.standard_normal((D, D)))
    tmpl = _unit(rng.standard_normal((4, D)))
    agents = np.unique(meta["agent"].to_numpy())
    style = {int(a): _unit(rng.standard_normal(D)) for a in agents}
    nxt = [10**9]

    def new_ids(k):
        a = np.arange(nxt[0], nxt[0] + k, dtype=np.int64)
        nxt[0] += k
        return a
    tmpl_mk = [new_ids(4) for _ in range(4)]
    kick_mk = new_ids(6)
    # room-day topic bins (10 min)
    t0_day = meta.group_by("pt_date", "room").agg(pl.col("t").min().alias("t0"))
    t0d = {(r["pt_date"], r["room"]): r["t0"] for r in t0_day.iter_rows(named=True)}
    topics, pools = {}, {}
    moments = {}

    def topic(pt, room, b):
        key = (pt, room, b)
        if key in topics:
            return topics[key], pools[key]
        if b == 0:
            th = _unit(mu + 0.9 * _unit(rng.standard_normal(D)))
        else:
            prev, _ = topic(pt, room, b - 1)
            th = _unit(0.85 * prev + 0.5 * _unit(rng.standard_normal(D)))
        topics[key], pools[key] = th, new_ids(15)
        return th, pools[key]
    # statement info
    sid_of_loc = {loc_of[int(m)]: int(s) for s, m in zip(S["sid"].to_list(), S["msg"].to_list())}
    k_arr = S["k"].to_numpy().astype(float)
    early = S["early"].cast(pl.Float64).to_numpy()
    lk = np.log2(1 + k_arr)
    act = k_arr >= 1
    m_lk = lk[act].mean() if act.any() else 0.0
    m_e = early[act].mean() if act.any() else 0.0
    lg0 = np.log(pi0 / (1 - pi0))
    if scenario == "load":
        lg = lg0 + b_load * (lk - m_lk)
    elif scenario == "phase":
        lg = lg0 + c_phase * (early - m_e)
    else:
        lg = np.full(len(k_arr), lg0)
    pi = 1 / (1 + np.exp(-lg))
    R_items = {}
    PR = P.filter(pl.col("set") == 0)
    for s_, m_, r_ in zip(PR["sid"].to_list(), PR["msg"].to_list(), PR["rank"].to_list()):
        R_items.setdefault(s_, []).append((loc_of[int(m_)], r_))
    V = np.zeros((n, D))
    MK = [None] * n
    truth = np.zeros(len(k_arr), dtype=np.int8)   # 1 copy, 2 transform, 3 template, 0 none
    true_src = np.full(len(k_arr), -1, dtype=np.int64)  # local index of the true source
    for loc, t, ag, room, pt in zip(meta["loc"].to_list(), meta["t"].to_list(), meta["agent"].to_list(),
                                    meta["room"].to_list(), meta["pt_date"].to_list()):
        b = int((t - t0d[(pt, room)]).total_seconds() // 600)
        th, pool = topic(pt, room, b)
        sid = sid_of_loc.get(loc)
        items = R_items.get(sid, []) if sid is not None else []
        noise = Lc @ rng.standard_normal(D) / np.sqrt(np.trace(Lc @ Lc.T))
        kind = 0
        if rng.random() < p_tmpl:
            j = rng.integers(4)
            v = _unit(tmpl[j] + 0.12 * noise)
            mk = np.r_[tmpl_mk[j], new_ids(rng.poisson(0.5))]
            kind = 3
        elif items:
            w = np.array([0.8 ** (r - 1) for _, r in items])
            src = items[rng.choice(len(items), p=w / w.sum())][0]
            if rng.random() < pi[sid]:
                v = _unit(V[src] + rng.uniform(0.06, 0.30) * noise)
                keep = MK[src][rng.random(len(MK[src])) < 0.8]
                mk = np.r_[keep, new_ids(rng.poisson(0.4))]
                kind = 1
            else:
                v = _unit(0.7 * (Tm @ V[src]) + 0.6 * th + 0.35 * style[int(ag)] + 0.5 * noise)
                ref = MK[src][rng.random(len(MK[src])) < 0.15]
                mk = np.r_[new_ids(rng.poisson(2.5)), rng.choice(pool, rng.poisson(1.0)), ref]
                kind = 2
        else:
            v = _unit(0.8 * th + 0.35 * style[int(ag)] + 0.6 * noise)
            mk = np.r_[new_ids(rng.poisson(3.0)), rng.choice(pool, rng.poisson(1.0))]
        if p_conv > 0 and kind != 1 and rng.random() < p_conv:
            mkey = (pt, room, int((t - t0d[(pt, room)]).total_seconds() // conv_s))
            if mkey not in moments:
                moments[mkey] = (_unit(th + 0.8 * _unit(rng.standard_normal(D))), new_ids(4))
            mv, mm = moments[mkey]
            v = _unit(mv + 0.1 * noise)
            mk = np.r_[mm, new_ids(rng.poisson(0.5))]
            kind = 4 if kind == 0 else kind
        if rng.random() < p_kick * np.exp(-dix[pt]):
            v = _unit(v + 1.2 * kappa)
            mk = np.r_[mk, rng.choice(kick_mk, 2, replace=False)]
        V[loc] = v
        MK[loc] = np.unique(mk.astype(np.int64))
        if sid is not None:
            truth[sid] = kind
            if kind in (1, 2):
                true_src[sid] = src
    content = {"msgs": msgs, "raw": {}, "white": {}}
    kick = {}
    for m, dm in DM.items():
        A, _ = np.linalg.qr(rng.standard_normal((dm, D)))
        Lm = aniso_shape(rng, dm, k0=8.0)
        E = V @ A.T + 0.2 * (rng.standard_normal((n, dm)) @ Lm.T)  # trace(Lm Lm^T) = 1: unit-norm noise
        E = _unit(E)
        content["raw"][m] = E.astype(np.float32)
        Z = E - E.mean(0)
        U, sv, Vt = np.linalg.svd(Z, full_matrices=False)
        W = (Z @ Vt[:32].T) / (sv[:32] / np.sqrt(n))
        content["white"][m] = _unit(W).astype(np.float32)
        kick[m] = _unit((A @ kappa)[None, :]).astype(np.float32)
    mk_rows = [(int(msgs[i]), int(x)) for i in range(n) for x in MK[i]]
    content["markers"] = pl.DataFrame(mk_rows, schema={"msg": pl.Int64, "marker": pl.Int64}, orient="row")
    content["true_src"] = true_src
    return content, kick, truth, pi


def synth_parents(S: pl.DataFrame, P: pl.DataFrame, content: dict, seed: int, recall: float = 0.9,
                  fp: float = 0.08):
    """Emulate DQ2: candidate pool = up to 40 most recent messages by others in the room within 60 min before the
    call; score = bge cosine + 0.05 new - 0.03 ln(pos); top 3; the 'labeller' names the true source if it is in
    the top 3 (prob recall), else (prob fp) calls the top candidate a reply. Returns (S', P') with set 3 replaced."""
    rng = np.random.default_rng(seed + 7)
    msgs = content["msgs"]
    meta = C.chat()[msgs].select("msg", "t", "agent", "room", "pt_date").with_row_index("loc")
    E = content["raw"]["bge"]
    grp = {key: (g["t"].to_numpy(), g["loc"].to_numpy(), g["agent"].to_numpy())
           for key, g in meta.sort("t").group_by(["pt_date", "room"])}
    pos = {int(m): i for i, m in enumerate(msgs)}
    Rset = {}
    PR = P.filter(pl.col("set") == 0)
    for s_, m_ in zip(PR["sid"].to_list(), PR["msg"].to_list()):
        Rset.setdefault(s_, set()).add(pos[int(m_)])
    par, npool = [], []
    hour = np.timedelta64(3600 * 10**6, "us")
    for sid, msg, ag, pt, room, tc in zip(S["sid"].to_list(), S["msg"].to_list(), S["agent"].to_list(),
                                          S["pt_date"].to_list(), S["room"].to_list(), S["t_call"].to_numpy()):
        tt, ll, aa = grp[(pt, room)]
        hi = int(np.searchsorted(tt, tc, side="left"))
        lo = int(np.searchsorted(tt, tc - hour, side="left"))
        cand = [(ll[j]) for j in range(hi - 1, lo - 1, -1) if aa[j] != ag][:40]
        npool.append(len(cand))
        if not cand:
            par.append(-1)
            continue
        b = pos[int(msg)]
        cosv = E[np.array(cand)] @ E[b]
        R_ = Rset.get(sid, set())
        score = cosv + 0.05 * np.array([c in R_ for c in cand]) - 0.03 * np.log(np.arange(1, len(cand) + 1))
        top = [cand[j] for j in np.argsort(-score)[:3]]
        src = content["true_src"][sid]
        if src >= 0 and src in top and rng.random() < recall:
            par.append(int(msgs[src]))
        elif rng.random() < fp:
            par.append(int(msgs[top[0]]))
        else:
            par.append(-1)
    par = np.array(par)
    S2 = S.with_columns(pl.Series("par_msg", np.where(par >= 0, par, 0), dtype=pl.UInt32),
                        pl.Series("n_pool_all", npool, dtype=pl.Int16),
                        pl.Series("is_reply", par >= 0)).with_columns(
        pl.when(pl.col("is_reply")).then(pl.col("par_msg")).otherwise(None).alias("par_msg"))
    has = np.flatnonzero(par >= 0)
    P3 = pl.DataFrame({"sid": S["sid"].to_numpy()[has].astype(np.int32), "msg": par[has].astype(np.uint32),
                       "set": np.full(len(has), 3, np.int8), "rank": np.ones(len(has), np.int32)})
    P2 = pl.concat([P.filter(pl.col("set") != 3), P3]).sort("sid", "set", "rank")
    return S2, P2


def synth_addressed(S: pl.DataFrame, P: pl.DataFrame, content: dict, truth: np.ndarray, seed: int,
                    p_name: float = 0.6, p_rand: float = 0.1):
    """Emulate naming: a copy or transformation names its source's author with prob p_name (the same for both
    modes); other statements with a read set name a random read author with prob p_rand. Addressed source = the
    latest read item by the named author (set 4)."""
    rng = np.random.default_rng(seed + 11)
    msgs = content["msgs"]
    pos = {int(m): i for i, m in enumerate(msgs)}
    ag = C.chat()[msgs]["agent"].to_numpy()
    PR = P.filter(pl.col("set") == 0).sort("sid", "rank")
    items = {}
    for s_, m_ in zip(PR["sid"].to_list(), PR["msg"].to_list()):
        items.setdefault(s_, []).append(pos[int(m_)])          # newest first
    addr = np.full(S.height, -1, dtype=np.int64)
    addr_n = np.zeros(S.height, dtype=np.int16)
    for sid in range(S.height):
        it = items.get(sid)
        if not it:
            continue
        src = content["true_src"][sid]
        named = None
        if truth[sid] in (1, 2) and src >= 0:
            if rng.random() < p_name:
                named = ag[src]
        elif rng.random() < p_rand:
            named = ag[it[rng.integers(len(it))]]
        if named is not None:
            hits = [loc for loc in it if ag[loc] == named]
            if hits:
                addr[sid] = int(msgs[hits[0]])
                addr_n[sid] = len(hits)
    has = np.flatnonzero(addr >= 0)
    S2 = S.with_columns(pl.Series("addr_msg", np.where(addr >= 0, addr, 0), dtype=pl.UInt32),
                        pl.Series("addressed", addr >= 0), pl.Series("addr_n", addr_n)).with_columns(
        pl.when(pl.col("addressed")).then(pl.col("addr_msg")).otherwise(None).alias("addr_msg"))
    P4 = pl.DataFrame({"sid": S["sid"].to_numpy()[has].astype(np.int32), "msg": addr[has].astype(np.uint32),
                       "set": np.full(len(has), 4, np.int8), "rank": np.ones(len(has), np.int32)})
    return S2, pl.concat([P.filter(pl.col("set") != 4), P4]).sort("sid", "set", "rank")


def synth_common(S, content):
    """The real common-marker rule applied to synthetic markers (period = the skeleton's messages)."""
    mk = content["markers"]
    meta = C.chat()[content["msgs"]].select(pl.col("msg").cast(pl.Int64), "agent", "pt_date")
    j = mk.join(meta, on="msg", how="left")
    nmsg = len(content["msgs"])
    freq = j.group_by("marker").agg(pl.len().alias("n"))
    common = set(freq.filter(pl.col("n") >= C.COMMON_FRAC * nmsg)["marker"].to_list())
    d1 = meta["pt_date"].min()
    a1 = j.filter(pl.col("pt_date") == d1).group_by("marker").agg(pl.col("agent").n_unique().alias("na"))
    return common | set(a1.filter(pl.col("na") >= C.COMMON_DAY1_AGENTS)["marker"].to_list())


def synth_templated(S, content, thr):
    """DQ5-style templated flag on synthetic content: >= 2 other agents with a same-period message above thr (bge)."""
    E = content["raw"]["bge"]
    meta = C.chat()[content["msgs"]].select("agent")
    ag = meta["agent"].to_numpy()
    pos = {int(g): i for i, g in enumerate(content["msgs"])}
    b = np.array([pos[int(x)] for x in S["msg"].to_list()])
    out = np.zeros(len(b), bool)
    for a in range(0, len(b), 2000):
        sims = E[b[a:a + 2000]] @ E.T
        for r, bi in enumerate(b[a:a + 2000]):
            hit = np.flatnonzero(sims[r] >= thr)
            out[a + r] = len(set(ag[hit].tolist()) - {ag[bi]}) >= 2
    return out


def analyse(S, P, content, kick, seed, n_perm=200, common=None, templated=None):
    o = C.outcomes(S, P, content, K_list=(16, 32), common=common, kick=kick, seed=seed, thr=THR_SYN)
    df = S.join(o, on="sid", how="left")
    if templated is not None:
        df = df.with_columns(pl.Series("templated_bge", templated), pl.Series("templated_gte", templated))
    d = L.prepare(df)
    res = {"n": d.height}
    for y in ("e_bge", "e_gte", "e_both", "es_bge", "er_bge", "mkn_all", "mkn_rare", "mkns_all", "mkr_all", "em_bge",
              "mks_all", "near_bge_addr", "near_gte_addr", "near_bge_par", "el_bge", "el_gte", "el_both", "mkl_all",
              "mkl_rare", "elc_bge", "elc_gte", "elc_both", "mklc_all", "mklc_rare", "els_bge", "els_gte", "els_both",
              "mkls_all", "mkls_rare"):
        for spec in ("agent", "day"):
            r = L.slope(d, y, spec)
            res[f"{y}|{spec}|b"] = L.bget(r)
            res[f"{y}|{spec}|p"] = L.bget(r, key="p")
    if templated is not None:  # rival b filter: drop templated and kickoff-echo statements
        q = {m: d[f"kick_cos_{m}"].quantile(0.9) for m in L.MODELS}
        df2 = d.filter(~pl.col("templated_bge") & (pl.col("kick_cos_bge") < q["bge"]) & (pl.col("kick_cos_gte") < q["gte"]))
        for y in ("e_bge", "e_gte", "er_bge", "mkn_rare", "el_bge", "el_gte", "mkl_rare", "elc_bge", "elc_gte",
                  "mklc_rare"):
            r = L.slope(df2, y, "agent")
            res[f"{y}|filt|b"] = L.bget(r)
            res[f"{y}|filt|p"] = L.bget(r, key="p")
    for m in L.MODELS:
        dpar = L.decomposition(d, m, 32, n_perm=n_perm, n_null=0, seed=seed, src="par")
        res[f"Tpar_{m}_K32"] = dpar.get("T", np.nan)
        res[f"Tparp_{m}_K32"] = dpar.get("p_one", np.nan)
        for K in (16, 32):
            dec = L.decomposition(d, m, K, n_perm=n_perm, n_null=0, seed=seed, src="addr")
            res[f"T_{m}_K{K}"] = dec.get("T", np.nan)
            res[f"Tp_{m}_K{K}"] = dec.get("p_one", np.nan)
            res[f"s_bottom_{m}_K{K}"] = dec.get("s_bottom", np.nan)
            res[f"s_top_{m}_K{K}"] = dec.get("s_top", np.nan)
        dp = L.add_pointwise(d, m, 32)
        for y in (f"pc_{m}", f"pt_{m}"):
            r = L.slope(dp, y, "agent")
            res[f"{y}|b"] = L.bget(r)
            res[f"{y}|p"] = L.bget(r, key="p")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", type=int, required=True)
    ap.add_argument("--unit", default=None)
    ap.add_argument("--seeds", type=int, default=20)
    ap.add_argument("--scenarios", default="const,load,phase")
    ap.add_argument("--n_perm", type=int, default=200)
    ap.add_argument("--seed0", type=int, default=1000)
    ap.add_argument("--p_conv", type=float, default=0.0)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    S, P = load_skeleton(a.period, a.unit)
    OUTD.mkdir(parents=True, exist_ok=True)
    tag = f"G{a.period:02d}" + (f"_{a.unit}" if a.unit else "") + (f"_{a.tag}" if a.tag else "")
    rows = []
    for sc in a.scenarios.split(","):
        for s in range(a.seeds):
            t0 = time.time()
            seed = a.seed0 + s
            content, kick, truth, pi = generate(S, P, sc, seed, p_conv=a.p_conv)
            S2, P2 = synth_parents(S, P, content, seed)
            S2, P2 = synth_addressed(S2, P2, content, truth, seed)
            common = synth_common(S2, content)
            tpl = synth_templated(S2, content, THR_SYN["bge"])
            res = analyse(S2, P2, content, kick, seed, n_perm=a.n_perm, common=common, templated=tpl)
            act = S["k"].to_numpy() >= 1
            tc = (truth == 1).astype(float)
            r_true = L.slope(L.prepare(S2.join(C.outcomes(S2, P2, content, K_list=(16,), seed=seed, thr=THR_SYN),
                                               on="sid").with_columns(pl.Series("true_copy", tc))), "true_copy", "agent")
            res["true_copy|agent|b"] = L.bget(r_true)
            res.update({"skeleton": tag, "p_conv": a.p_conv, "scenario": sc, "seed": seed, "copy_rate": float((truth[act] == 1).mean()),
                        "tmpl_rate": float((truth == 3).mean()), "pi_mean": float(pi[act].mean()),
                        "sec": round(time.time() - t0, 1)})
            rows.append(res)
            print(json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in res.items()
                              if k in ("scenario", "seed", "copy_rate", "true_copy|agent|b", "e_bge|agent|b", "e_bge|agent|p",
                                       "mkn_all|agent|b", "mkn_all|agent|p", "T_bge_K32", "Tp_bge_K32", "near_bge_addr|agent|b",
                                       "near_bge_par|agent|b",
                                       "sec")}), flush=True)
            pl.DataFrame(rows).write_parquet(OUTD / f"synth_{tag}.parquet")


if __name__ == "__main__":
    main()
