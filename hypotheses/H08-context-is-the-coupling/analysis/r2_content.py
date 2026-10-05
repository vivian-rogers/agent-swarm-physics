"""H08 round 2, R2: non-mention content response, read vs in flight at matched lag (card "Round 2", R2).

  uv run python hypotheses/H08-context-is-the-coupling/analysis/r2_content.py synth            # synthetic guard first
  uv run python hypotheses/H08-context-is-the-coupling/analysis/r2_content.py real [--period 38 ...]
  uv run python hypotheses/H08-context-is-the-coupling/analysis/r2_content.py summarize

Units: (agent message m by sender j, recipient i) from `context_ledger_items` (own room) and every talk statement s of i
posted at lag 0 < t_s - t_m <= 300 s. The producing call of s is the ledger call with t_first <= t_s <= t_log (as in
scheme/build_turns_ledger.py). side = read (producing call is the receiving call of m or later), flight (producing call
assembled before m: t_call <= t_m), or ambiguous (dropped). Response x = cos(s, m) - b(m, i), with b the mean cosine of
the same message with i's statements on the same PT day at |t - t_m| in [20, 60] min (secondary: i's statements on
other days of the period). Partition contrast Delta = sum_b w_b (xbar_read,b - xbar_flight,b) / sum_b w_b over lag bins,
w_b = n_r n_f / (n_r + n_f); convergence share kappa_c = sum_b w_b xbar_flight,b / sum_b w_b xbar_read,b. Day-cluster
bootstrap B = 200. Both embedding models. Other-room placebo in two-room periods ("read" = producing call assembled
after m). Reserved days are dropped before anything is computed (period_days_any uses holdout_mask and calendar.holdout).
No text is read; outputs hold codes and floats only.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from h08lib import *  # noqa: E402,F403
from build_turns_ledger import chat_full, period_days_any  # noqa: E402
from build_turns import room_lookup, room_at  # noqa: E402

OUT2 = OUT / "r2"
LAG_EDGES = np.array([0, 15, 30, 60, 120, 300], float)
MAXLAG_US = 300 * US
NULL_LO, NULL_HI = 20 * 60 * US, 60 * 60 * US
B = 200
MODELS = {"bge": "chat_bge_small.npy", "gte": "chat_gte_modernbert.npy"}
SYN_PERIODS = [38, 41]
# Amendments (2026-10-05, after the synthetic guard, before any real-data run; card "Round 2", R2-A1..A3):
DENSITY = True                      # R2-A2: strata = lag bin x density bin (switch off to get the pre-registered lag-only match)
DENS_EDGES = np.array([0, 2, 4, 8])  # density bins: 0-1, 2-3, 4-7, 8+ messages in the 300 s before s
NSTRATA = (len(LAG_EDGES) - 1) * len(DENS_EDGES)
CLUSTER_HOURS = True                # R2-A1: resample 1-hour blocks within days instead of whole days


# ----------------------------------------------------------------------------- skeleton
def skeleton(g: int, chat: pl.DataFrame, tl) -> dict | None:
    """Index arrays for one period: messages/statements (A), own-room pairs and other-room pairs. No embeddings."""
    days = period_days_any(g)
    if not days:
        return None
    cw = (pl.scan_parquet(SH / "call_windows.parquet")
          .filter(pl.col("pt_date").is_in(days) & ~pl.col("holdout") & (pl.col("ctx_mode").cast(pl.Utf8) != "summary"))
          .select("turn_id", "agent", "pt_date", "t_call", "t_first", "t_log").collect()
          .sort("agent", "t_call", "turn_id"))
    cw = cw.with_columns(pl.int_range(pl.len()).over("agent").alias("cidx"))
    ev = (pl.read_parquet(SH / "events_core.parquet", columns=["t", "message_id", "action_type"])
          .filter(pl.col("action_type") == "AGENT_TALK").select("message_id", pl.col("t").alias("t_ev")))
    A = (chat.filter(pl.col("pt_date").is_in(days) & (pl.col("speaker_kind").cast(pl.Utf8) == "agent") & pl.col("erow").is_not_null())
         .select("msg", "message_id", "agent", "t", "pt_date", "room", "mentions_roster", "erow")
         .join(ev, on="message_id", how="left").with_columns(pl.col("t_ev").fill_null(pl.col("t"))).sort("t_ev"))
    A = A.join_asof(cw.select("turn_id", "agent", "t_first", "t_log", "t_call", "cidx").sort("t_first"),
                    left_on="t_ev", right_on="t_first", by="agent", strategy="backward")
    A = A.with_columns(pl.when(pl.col("t_ev") <= pl.col("t_log")).then(pl.col("turn_id")).otherwise(None).alias("turn_id"))
    A = A.with_columns(pl.when(pl.col("turn_id").is_not_null()).then(pl.col("cidx")).otherwise(None).alias("cidx"),
                       pl.when(pl.col("turn_id").is_not_null()).then(pl.col("t_call")).otherwise(None).alias("t_call"))
    rp = (pl.read_parquet(SH / "reply_pairs.parquet", columns=["b_msg", "pair_set", "parent", "a_agent", "holdout"])
          .filter(~pl.col("holdout") & (pl.col("pair_set") == "cand") & pl.col("parent"))
          .group_by("b_msg").agg(pl.col("a_agent").unique().alias("par_auth")).rename({"b_msg": "msg"}))
    A = A.join(rp, on="msg", how="left")
    st = (pl.read_parquet(SH / "embeddings/statements.parquet", columns=["kind", "src_row"]).with_row_index("srow")
          .filter(pl.col("kind") == "chat").select("srow", pl.col("src_row").alias("erow")))
    fl = pl.read_parquet(SH / "statement_flags.parquet", columns=["srow", "self_repeat_both"])
    st = st.join(fl, on="srow", how="left")
    A = A.join(st.select("erow", "self_repeat_both"), on="erow", how="left").sort("t_ev")
    A = A.with_row_index("aid")
    n = A.height
    t = us(A["t_ev"]); agent = A["agent"].to_numpy().astype(np.int16)
    room = A["room"].to_numpy().astype(np.int16)
    day = A["pt_date"].to_list()
    dix_of = {d: i for i, d in enumerate(days)}
    dix = np.array([dix_of[d] for d in day], np.int16)
    is_st = A["turn_id"].is_not_null().to_numpy()
    cidx = A["cidx"].fill_null(-1).to_numpy().astype(np.int64)
    tcall = np.where(is_st, A["t_call"].dt.epoch("us").fill_null(0).to_numpy(), 0).astype(np.int64)
    ment = np.array([mask_of(x) for x in A["mentions_roster"].to_list()], np.uint64)
    pauth = np.array([mask_of(x) for x in A["par_auth"].to_list()], np.uint64)
    copy = A["self_repeat_both"].fill_null(False).to_numpy()
    aid_of_msg = dict(zip(A["msg"].to_list(), range(n)))
    # statements per recipient, sorted by time
    S = {}
    for a in np.unique(agent):
        ix = np.nonzero(is_st & (agent == a))[0]
        ix = ix[np.argsort(t[ix], kind="stable")]
        S[int(a)] = ix
    # receiving-call index of each ledger item
    it = (pl.scan_parquet(SH / "context_ledger_items.parquet").filter(pl.col("turn_id").is_in(cw["turn_id"].implode())
                                                                      & (pl.col("kind").cast(pl.Utf8) == "agent"))
          .select("turn_id", "message_id", "sender").collect())
    it = it.join(cw.select("turn_id", pl.col("agent").alias("rcpt"), "cidx"), on="turn_id", how="left")
    it = it.join(A.select("message_id", "aid"), on="message_id", how="inner").filter(pl.col("sender") != pl.col("rcpt"))

    def expand(m_aid, rcpt, Rcidx, placebo):
        rows = []
        for a in np.unique(rcpt):
            if int(a) not in S:
                continue
            sel = np.nonzero(rcpt == a)[0]
            six = S[int(a)]
            if not len(six):
                continue
            ts = t[six]
            tm = t[m_aid[sel]]
            lo = np.searchsorted(ts, tm, side="right")
            hi = np.searchsorted(ts, tm + MAXLAG_US, side="right")
            cnt = hi - lo
            if cnt.sum() == 0:
                continue
            rep = np.repeat(np.arange(len(sel)), cnt)
            off = np.arange(cnt.sum()) - np.repeat(np.cumsum(cnt) - cnt, cnt)
            sid = six[lo[rep] + off]
            mid = m_aid[sel][rep]
            lag = (t[sid] - t[mid]) / US
            if placebo:
                side = np.where(tcall[sid] > t[mid], 1, 0).astype(np.int8)
            else:
                R = Rcidx[sel][rep]
                side = np.where(cidx[sid] >= R, 1, np.where(tcall[sid] <= t[mid], 0, 2)).astype(np.int8)
            rows.append((mid, sid, np.full(len(sid), a, np.int16), lag.astype(np.float32), side))
        if not rows:
            return None
        mid, sid, rc, lag, side = (np.concatenate(x) for x in zip(*rows))
        return dict(mid=mid, sid=sid, rcpt=rc, lag=lag, side=side)

    own = expand(it["aid"].to_numpy().astype(np.int64), it["rcpt"].to_numpy().astype(np.int16),
                 it["cidx"].to_numpy().astype(np.int64), False)
    oth = None
    if g in TWO_ROOM:
        on_day = {}
        for (a, d), _ in cw.group_by(["agent", "pt_date"]):
            on_day.setdefault(d, set()).add(int(a))
        mids, rcs = [], []
        for d in days:
            mi = np.nonzero(np.array([x == d for x in day]))[0]
            if not len(mi):
                continue
            for a in sorted(on_day.get(d, ())):
                if a == CC_AGENT:
                    continue
                ra = room_at(tl, a, t[mi])
                sel = mi[(ra >= 0) & (ra != room[mi]) & (agent[mi] != a)]
                mids.append(sel); rcs.append(np.full(len(sel), a, np.int16))
        if mids:
            mids = np.concatenate(mids); rcs = np.concatenate(rcs)
            oth = expand(mids, rcs, np.zeros(len(mids), np.int64), True)
    # amendment R2-A1: resampling clusters = 1-hour blocks of message time within a PT day (G41: ~20 blocks vs 5 days)
    hr = ((t - np.array([t[dix == d].min() for d in range(len(days))])[dix]) // (3600 * US)).astype(np.int64)
    key = dix.astype(np.int64) * 100 + hr
    uk, clu = np.unique(key, return_inverse=True)
    return dict(g=g, days=days, t=t, agent=agent, dix=dix, clu_h=clu.astype(np.int64), nclu_h=len(uk), is_st=is_st, ment=ment, pauth=pauth, copy=copy,
                erow=A["erow"].to_numpy().astype(np.int64), S=S, own=own, oth=oth, n=n, aid_of_msg=aid_of_msg)


# ----------------------------------------------------------------------------- response
def null_sums(sk: dict, V: np.ndarray):
    """Per recipient: cumulative sums of statement vectors in time order (same-day window null) and per-day totals."""
    t, dix = sk["t"], sk["dix"]
    C, T, D = {}, {}, {}
    for a, six in sk["S"].items():
        X = V[six]
        C[a] = np.vstack([np.zeros((1, V.shape[1]), np.float32), np.cumsum(X, 0, dtype=np.float64).astype(np.float32)])
        T[a] = t[six]
        nd = len(sk["days"])
        tot = np.zeros((nd, V.shape[1]), np.float32); cnt = np.zeros(nd)
        np.add.at(tot, dix[six], X); np.add.at(cnt, dix[six], 1)
        D[a] = (tot, cnt)
    return C, T, D


def response(sk: dict, P: dict, V: np.ndarray, sums) -> dict:
    """x = cos(s, m) - b(m, i) (same-day [20, 60] min null) and xo (other-day null) for every pair row."""
    C, T, D = sums
    mid, sid, rc = P["mid"], P["sid"], P["rcpt"]
    raw = np.einsum("ij,ij->i", V[mid], V[sid]).astype(np.float32)
    b = np.full(len(mid), np.nan, np.float32); bo = np.full(len(mid), np.nan, np.float32)
    t, dix = sk["t"], sk["dix"]
    for a in np.unique(rc):
        sel = np.nonzero(rc == a)[0]
        if int(a) not in C:
            continue
        Ca, Ta = C[int(a)], T[int(a)]
        tm = t[mid[sel]]
        s1 = np.searchsorted(Ta, tm - NULL_HI, "left"); e1 = np.searchsorted(Ta, tm - NULL_LO, "right")
        s2 = np.searchsorted(Ta, tm + NULL_LO, "left"); e2 = np.searchsorted(Ta, tm + NULL_HI, "right")
        cnt = (e1 - s1) + (e2 - s2)
        vs = (Ca[e1] - Ca[s1]) + (Ca[e2] - Ca[s2])
        ok = cnt > 0
        b[sel[ok]] = np.einsum("ij,ij->i", V[mid[sel[ok]]], vs[ok]) / cnt[ok]
        tot, cn = D[int(a)]
        dd = dix[mid[sel]]
        allv = tot.sum(0); alln = cn.sum()
        ov = allv[None, :] - tot[dd]; on = alln - cn[dd]
        ok2 = on > 0
        bo[sel[ok2]] = np.einsum("ij,ij->i", V[mid[sel[ok2]]], ov[ok2]) / on[ok2]
    return {"raw": raw, "x": raw - b, "xo": raw - bo}


def pair_flags(sk: dict, P: dict):
    snd = sk["agent"][P["mid"]].astype(np.uint64)
    bit = np.uint64(1) << np.minimum(snd, 63)
    named = ((sk["ment"][P["sid"]] & bit) != 0) | ((sk["pauth"][P["sid"]] & bit) != 0)
    lagbin = np.clip(np.searchsorted(LAG_EDGES, P["lag"], side="left") - 1, 0, len(LAG_EDGES) - 2).astype(np.int8)
    if DENSITY:   # amendment R2-A2: match on lag x message density (own-room messages received in the 300 s before s)
        dens = np.bincount(sk["own"]["sid"], minlength=sk["n"])[P["sid"]]
        dbin = np.clip(np.searchsorted(DENS_EDGES, dens, side="right") - 1, 0, len(DENS_EDGES) - 1)
        lagbin = (lagbin * len(DENS_EDGES) + dbin).astype(np.int16)
    return {"nonname": ~named, "copy": sk["copy"][P["sid"]], "lagbin": lagbin, "day": (sk["clu_h"] if CLUSTER_HOURS else sk["dix"].astype(np.int64))[P["mid"]],
            "pair": P["mid"].astype(np.int64) * 64 + P["rcpt"].astype(np.int64)}


# ----------------------------------------------------------------------------- estimator
def contrast(day, side, lagbin, x, nd: int, W: np.ndarray, paired_key=None) -> dict:
    """Delta and kappa_c over matched strata. Primary CI (amendment R2-A1): leave-one-day-out jackknife, t with nd - 1 df;
    the pre-registered day-cluster percentile bootstrap (W: B+1 x nd, row 0 = point estimate) is kept as `*_boot`."""
    from scipy.stats import t as tdist
    ok = np.isfinite(x) & (side <= 1)
    if paired_key is not None:
        pk = paired_key[ok]; sd = side[ok]
        both = set(pk[sd == 1].tolist()) & set(pk[sd == 0].tolist())
        keep = np.isin(pk, np.fromiter(both, np.int64)) if both else np.zeros(ok.sum(), bool)
        idx = np.nonzero(ok)[0][keep]
        ok = np.zeros_like(ok); ok[idx] = True
    nb = NSTRATA if DENSITY else len(LAG_EDGES) - 1
    S = np.zeros((2, nb, nd)); N = np.zeros((2, nb, nd))
    np.add.at(S, (side[ok], lagbin[ok], day[ok]), x[ok])
    np.add.at(N, (side[ok], lagbin[ok], day[ok]), 1.0)
    J = np.ones((nd, nd)) - np.eye(nd)
    WW = np.vstack([W, J])

    def stats(Wm):
        Sw = np.einsum("bd,sld->bsl", Wm, S); Nw = np.einsum("bd,sld->bsl", Wm, N)
        with np.errstate(invalid="ignore", divide="ignore"):
            xb = Sw / Nw
            w = Nw[:, 1] * Nw[:, 0] / (Nw[:, 1] + Nw[:, 0])
            w = np.where(np.isfinite(xb[:, 0]) & np.isfinite(xb[:, 1]), w, 0)
            xr = np.where(w > 0, xb[:, 1], 0); xf = np.where(w > 0, xb[:, 0], 0)
            mr = (w * xr).sum(1) / w.sum(1); mf = (w * xf).sum(1) / w.sum(1)
        return {"delta": mr - mf, "x_read": mr, "x_flight": mf, "kappa_c": mf / mr}, xb

    st, xb = stats(WW)
    nbt = W.shape[0]
    out = {}
    q = tdist.ppf(0.975, max(nd - 1, 1))
    for k, v in st.items():
        est = float(v[0]); jk = v[nbt:]
        jk = jk[np.isfinite(jk)]
        se = float(np.sqrt((len(jk) - 1) / len(jk) * ((jk - jk.mean()) ** 2).sum())) if len(jk) > 1 else float("nan")
        out[k] = (est, est - q * se, est + q * se)
        out[k + "_se"] = se
        out[k + "_boot"] = ci(v[:nbt])
    nl = len(LAG_EDGES) - 1
    nd_ = len(DENS_EDGES) if DENSITY else 1
    out.update({"n_read": int(N[1].sum()), "n_flight": int(N[0].sum()), "ci_kind": "jackknife over days, t (nd-1 df)",
                "by_lag": {f"{int(LAG_EDGES[b])}-{int(LAG_EDGES[b + 1])}s": {
                    "n_r": int(N[1, b * nd_:(b + 1) * nd_].sum()), "n_f": int(N[0, b * nd_:(b + 1) * nd_].sum()),
                    "x_r": float(S[1, b * nd_:(b + 1) * nd_].sum() / max(N[1, b * nd_:(b + 1) * nd_].sum(), 1)),
                    "x_f": float(S[0, b * nd_:(b + 1) * nd_].sum() / max(N[0, b * nd_:(b + 1) * nd_].sum(), 1))} for b in range(nl)}})
    return out


def boot_w(nd: int, seed: int) -> np.ndarray:
    return np.vstack([np.ones((1, nd)), np.random.default_rng(seed).multinomial(nd, np.full(nd, 1 / nd), size=B)]).astype(float)


def evaluate(sk: dict, V: np.ndarray, W: np.ndarray, full: bool = True) -> dict:
    sums = null_sums(sk, V)
    nd = sk["nclu_h"] if CLUSTER_HOURS else len(sk["days"])
    out = {}
    for lab in ("own", "oth"):
        P = sk[lab]
        if P is None:
            continue
        r = response(sk, P, V, sums)
        f = pair_flags(sk, P)
        res = {"nonname": contrast(f["day"], P["side"], f["lagbin"], np.where(f["nonname"], r["x"], np.nan), nd, W)}
        if full:
            res["all"] = contrast(f["day"], P["side"], f["lagbin"], r["x"], nd, W)
            res["nonname_nocopy"] = contrast(f["day"], P["side"], f["lagbin"], np.where(f["nonname"] & ~f["copy"], r["x"], np.nan), nd, W)
            res["nonname_otherday"] = contrast(f["day"], P["side"], f["lagbin"], np.where(f["nonname"], r["xo"], np.nan), nd, W)
            if lab == "own":
                res["nonname_paired"] = contrast(f["day"], P["side"], f["lagbin"], np.where(f["nonname"], r["x"], np.nan), nd, W,
                                                 paired_key=f["pair"])
                res["share_named"] = float(1 - f["nonname"][P["side"] <= 1].mean())
                res["n_ambiguous"] = int((P["side"] == 2).sum())
        out[lab] = res
    return out


def vectors(sk: dict, E: np.ndarray) -> np.ndarray:
    return np.asarray(E[sk["erow"]], np.float32)


# ----------------------------------------------------------------------------- synthetic
def synth_vectors(sk: dict, truth: str, rng, dim=64, alpha=0.3, alpha_u=0.15, tau_min=60.0) -> np.ndarray:
    """Synthetic embeddings on the real skeleton: OU day field shared by all agents, agent style, noise, planted response."""
    t, dix, agent = sk["t"], sk["dix"], sk["agent"]
    n = sk["n"]
    V = np.zeros((n, dim), np.float32)
    style = {int(a): rng.normal(0, 0.7 / np.sqrt(dim), dim) for a in np.unique(agent)}
    field = np.zeros((n, dim))
    for d in range(len(sk["days"])):
        ix = np.nonzero(dix == d)[0]
        if not len(ix):
            continue
        t0 = t[ix].min() - 3600 * US
        m = int((t[ix].max() - t0) / (60 * US)) + 2
        a = np.exp(-1 / tau_min)
        z = np.zeros((m, dim)); z[0] = rng.normal(0, 1 / np.sqrt(dim), dim)
        eps = rng.normal(0, np.sqrt(1 - a * a) / np.sqrt(dim), (m, dim))
        for k in range(1, m):
            z[k] = a * z[k - 1] + eps[k]
        field[ix] = z[((t[ix] - t0) / (60 * US)).astype(int)]
    P = sk["own"]
    gated_src = {}; all_src = {}
    if truth != "null":
        for mid_, sid_, side_ in zip(P["mid"], P["sid"], P["side"]):
            all_src.setdefault(int(sid_), []).append(int(mid_))
            if side_ == 1:
                gated_src.setdefault(int(sid_), []).append(int(mid_))
    order = np.argsort(t, kind="stable")
    noise = rng.normal(0, 1.0 / np.sqrt(dim), (n, dim))
    for k in order:
        v = field[k] + style[int(agent[k])] + noise[k]
        if truth in ("gated", "mixed") and k in gated_src:
            v = v + alpha * V[gated_src[k]].sum(0)
        if truth == "ungated" and k in all_src:
            v = v + alpha * V[all_src[k]].sum(0)
        if truth == "mixed" and k in all_src:
            v = v + alpha_u * V[all_src[k]].sum(0)
        V[k] = v / np.linalg.norm(v)
    return V


def run_synth(n_rep: int = 20):
    """Each replicate is scored under four estimator configurations: prereg (lag strata, percentile bootstrap over days),
    hb_lag (lag strata, bootstrap over 1-hour blocks), hb_lagdens (lag x density strata, hour-block bootstrap) and
    hjk_lagdens (lag x density, hour-block jackknife-t). Amendments R2-A1/A2 pick the configuration from this table."""
    global DENSITY, CLUSTER_HOURS
    chat = chat_full(); tl = room_lookup()
    res = {}
    cfgs = {"prereg": (False, False, "boot"), "hb_lag": (False, True, "boot"), "hb_lagdens": (True, True, "boot"),
            "hjk_lagdens": (True, True, "jk")}
    for g in SYN_PERIODS:
        sk = skeleton(g, chat, tl)
        res[gname(g)] = {}
        for truth in ("gated", "ungated", "mixed", "null"):
            reps = {c: [] for c in cfgs}
            for r in range(n_rep):
                rng = np.random.default_rng(1000 * g + 17 * r + {"gated": 1, "ungated": 2, "mixed": 3, "null": 4}[truth])
                V = synth_vectors(sk, truth, rng)
                for c, (dens, hours, kind) in cfgs.items():
                    DENSITY, CLUSTER_HOURS = dens, hours
                    nd = sk["nclu_h"] if hours else len(sk["days"])
                    o = evaluate(sk, V, boot_w(nd, r), full=False)["own"]["nonname"]
                    reps[c].append((o["delta_boot"] if kind == "boot" else o["delta"], o["kappa_c"][0]))
            res[gname(g)][truth] = {}
            for cfg, L in reps.items():
                d = np.array([x[0] for x in L]); k = np.array([x[1] for x in L])
                res[gname(g)][truth][cfg] = {"pos": float((d[:, 1] > 0).mean()), "neg": float((d[:, 2] < 0).mean()),
                                             "covers0": float(((d[:, 1] <= 0) & (d[:, 2] >= 0)).mean()),
                                             "delta_med": float(np.median(d[:, 0])), "kappa_med": float(np.median(k))}
            print(gname(g), truth, {c: (v["pos"], v["neg"], round(v["delta_med"], 4), round(v["kappa_med"], 2))
                                    for c, v in res[gname(g)][truth].items()}, flush=True)
    DENSITY, CLUSTER_HOURS = True, True
    OUT2.mkdir(parents=True, exist_ok=True)
    jdump({"n_rep": n_rep, "periods": res, "configs": {k: list(v) for k, v in cfgs.items()},
           "design": "real skeleton (ledger calls, statement times, receipts), 64-d synthetic vectors, OU day field tau 60 min, "
                     "alpha 0.3 (mixed: gated 0.3 + ungated 0.15); entries: share of replicates with CI > 0 (pos), CI < 0 (neg)"},
          OUT2 / "r2_synthetic.json")


# ----------------------------------------------------------------------------- real
def run_real(periods):
    global DENSITY, CLUSTER_HOURS
    chat = chat_full(); tl = room_lookup()
    Es = {k: np.load(SH / "embeddings" / v, mmap_mode="r") for k, v in MODELS.items()}
    for g in periods:
        t0 = time.time()
        sk = skeleton(g, chat, tl)
        if sk is None or sk["own"] is None:
            continue
        nd = sk["nclu_h"] if CLUSTER_HOURS else len(sk["days"])
        W = boot_w(nd, g)
        out = {"period": gname(g), "n_days": len(sk["days"]), "n_clusters": nd, "n_rows_own": int(len(sk["own"]["mid"])),
               "n_rows_other": int(len(sk["oth"]["mid"])) if sk["oth"] else 0}
        for k, E in Es.items():
            V = vectors(sk, E)
            DENSITY, CLUSTER_HOURS = True, True
            out[k] = evaluate(sk, V, W)
            # the pre-registered configuration (lag-only strata, percentile bootstrap over days), for comparison
            DENSITY, CLUSTER_HOURS = False, False
            pr = evaluate(sk, V, boot_w(len(sk["days"]), g), full=False)
            out[k]["prereg_nonname"] = {lab: {"delta_boot": v["nonname"]["delta_boot"], "kappa_c": v["nonname"]["kappa_c"][0]}
                                        for lab, v in pr.items()}
            DENSITY, CLUSTER_HOURS = True, True
        od = OUT2 / gname(g); od.mkdir(parents=True, exist_ok=True)
        jdump(out, od / "r2_content.json")
        b, gg = out["bge"]["own"]["nonname"], out["gte"]["own"]["nonname"]
        b, gg = dict(b, delta=b["delta_boot"]), dict(gg, delta=gg["delta_boot"])
        print(f"{gname(g)}: rows {out['n_rows_own']} (+{out['n_rows_other']} other); Delta_nonname bge {b['delta'][0]:+.4f} "
              f"[{b['delta'][1]:+.4f},{b['delta'][2]:+.4f}] gte {gg['delta'][0]:+.4f} [{gg['delta'][1]:+.4f},{gg['delta'][2]:+.4f}] "
              f"kappa bge {b['kappa_c'][0]:.2f}; n_r {b['n_read']} n_f {b['n_flight']}; {time.time() - t0:.0f}s", flush=True)
    write_provenance("r2 content (r2/G<NN>/r2_content.json)", "hypotheses/H08-context-is-the-coupling/analysis/r2_content.py",
                     ["call_windows", "context_ledger_items", "chat_core", "chat_mentions_clean", "events_core", "reply_pairs",
                      "embeddings/chat_bge_small", "embeddings/chat_gte_modernbert", "embeddings/statements", "statement_flags",
                      "rooms_timeline", "calendar"],
                     {"lag_edges_s": LAG_EDGES.tolist(), "null_window_min": [20, 60], "B": B,
                      "reserved_days": "dropped before computation"}, folder=OUT2)


def summarize():
    rows = []
    for g in sorted(PERIODS):
        f = OUT2 / gname(g) / "r2_content.json"
        if not f.exists():
            continue
        o = json.loads(f.read_text())
        r = {"period": gname(g), "regime": PERIODS[g]["regime"]}
        for k in MODELS:
            nn = o[k]["own"]["nonname"]
            r[f"{k}_delta"] = nn["delta_boot"]; r[f"{k}_kappa"] = nn["kappa_c_boot"]
            r[f"{k}_paired"] = o[k]["own"]["nonname_paired"]["delta_boot"]
            r[f"{k}_all"] = o[k]["own"]["all"]["delta_boot"]
            r[f"{k}_nocopy"] = o[k]["own"]["nonname_nocopy"]["delta_boot"]
            r[f"{k}_otherday"] = o[k]["own"]["nonname_otherday"]["delta_boot"]
            if "oth" in o[k]:
                r[f"{k}_other_room"] = o[k]["oth"]["nonname"]["delta_boot"]
        r["n_read"] = o["bge"]["own"]["nonname"]["n_read"]; r["n_flight"] = o["bge"]["own"]["nonname"]["n_flight"]
        r["share_named"] = o["bge"]["own"]["share_named"]
        rows.append(r)
    R3 = [r for r in rows if int(r["period"][1:]) in REGIME_III]     # G36 counts as regime III (as in C3), 9 periods
    R12 = [r for r in rows if int(r["period"][1:]) not in REGIME_III]
    pos = lambda r, k: r[f"{k}_delta"][1] > 0
    p1 = sum(pos(r, "bge") and pos(r, "gte") for r in R3)
    p1_cov = max(sum(r[f"{k}_delta"][1] <= 0 for r in R3) for k in MODELS)
    p2 = sum(r["bge_delta"][0] > 0 and r["gte_delta"][0] > 0 for r in R12)
    p2_neg = sum(r["bge_delta"][2] < 0 and r["gte_delta"][2] < 0 for r in R12)
    kap = [r["bge_kappa"][0] for r in R3]
    two = [r for r in rows if int(r["period"][1:]) in TWO_ROOM and "bge_other_room" in r]
    p4 = sum(abs(r["bge_other_room"][0]) < abs(r["bge_delta"][0]) / 3 and r["bge_other_room"][1] <= 0 <= r["bge_other_room"][2]
             for r in two)
    p5 = sum(np.sign(r["bge_paired"][0]) == np.sign(r["bge_delta"][0]) and np.sign(r["gte_paired"][0]) == np.sign(r["gte_delta"][0])
             for r in R3)
    summ = {"rows": rows,
            "R2-P1": {"both_models_CI_pos": p1, "of": len(R3), "max_CI_includes0_one_model": p1_cov,
                      "pass": p1 >= 6, "kill": p1_cov >= 5},
            "R2-P2": {"both_pos_sign": p2, "of": len(R12), "both_neg_CI": p2_neg, "pass": p2 >= 5 and p2_neg == 0},
            "R2-P3": {"median_kappa_bge": float(np.median(kap)) if kap else None, "kappas": kap,
                      "pass": bool(kap) and 0.2 <= float(np.median(kap)) <= 0.6},
            "R2-P4": {"pass_count": p4, "of": len(two), "pass": p4 >= 6},
            "R2-P5": {"sign_agree": int(p5), "of": len(R3), "pass": bool(p5 >= 7)},
            "descriptive_all_statements": {"both_models_CI_pos_regIII": sum(r["bge_all"][1] > 0 and r["gte_all"][1] > 0 for r in R3),
                                           "bge_CI_pos_regIII": sum(r["bge_all"][1] > 0 for r in R3),
                                           "bge_CI_pos_regI_II": sum(r["bge_all"][1] > 0 for r in R12),
                                           "nonname_bge_CI_neg_regIII": sum(r["bge_delta"][2] < 0 for r in R3)}}
    jdump(summ, OUT2 / "r2_summary.json")
    for k in ("R2-P1", "R2-P2", "R2-P3", "R2-P4", "R2-P5", "descriptive_all_statements"):
        print(k, {a: b for a, b in summ[k].items() if a != "kappas"})
    for r in rows:
        print(r["period"], r["regime"], "all bge", [round(v, 4) for v in r["bge_all"]], "gte", [round(v, 4) for v in r["gte_all"]],
              "| nonname bge", [round(v, 4) for v in r["bge_delta"]], "gte", [round(v, 4) for v in r["gte_delta"]],
              "kappa", round(r["bge_kappa"][0], 2), "other", [round(v, 4) for v in r.get("bge_other_room", [np.nan] * 3)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["synth", "real", "summarize"])
    ap.add_argument("--period", type=int, action="append")
    ap.add_argument("--reps", type=int, default=20)
    a = ap.parse_args()
    if a.mode == "synth":
        run_synth(a.reps)
    elif a.mode == "real":
        run_real(a.period or sorted(PERIODS))
    else:
        summarize()


if __name__ == "__main__":
    main()
