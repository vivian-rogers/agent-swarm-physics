"""H13 round 2, R2-C: family coupling at the read-out call (card: Round 2, R2-C).

Content: H50's matched-age read-out jump, reimplemented from shared tables (call_windows, chat_core, producing_calls,
context_ledger_items, DQ5 statement vectors). Rows (source m, recipient j, j's statement B): hop h = pos(prod(B)) -
pos(receiving call of m) + 1 in j's non-summary call sequence; y = cos(z_B, z_m) - mean cos(z_B, z_m') (m' = 2 seeded
statements of the same sender >= 2 h away). J^c_1 = matched-age (10-s bins in [0, 60) s) hop-1 minus hop-0 jump.
Family partition: same-lab vs cross-lab rows; primary contrast named-stratified.
Talk: per non-summary call, talk ~ items read at the call (same/cross lab x named/unnamed), agent-day fixed effects.

Usage: uv run python hypotheses/H13-family-fields/analysis/r2_readout.py build | synthetic [--reps 40] | run
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import r2lib as R  # noqa: E402
import build as B  # noqa: E402
from common import holdout_mask  # noqa: E402

OUTD = R.R2 / "readout"
BINS = np.arange(0, 61, 10.0)
HMAX = 6
NBOOT = 400
REGIME_III = [u for u in R.COUNTED if u != "35"]
LABG = {"Anthropic": 0, "OpenAI": 1, "Google": 2}           # K x K groups; everything else = 3 ("other")


# ============================================================================ build rows
def tabs():
    st = pl.read_parquet(R.ED / "statements.parquet", columns=["kind", "src_row"]).with_row_index("srow")
    ci = pl.read_parquet(R.ED / "chat_index.parquet").with_row_index("src_row")
    st = st.filter(pl.col("kind") == "chat").join(ci, on="src_row").select("message_id", "srow")
    return dict(
        st=st,
        cw=pl.read_parquet(R.SH / "call_windows.parquet", columns=["turn_id", "agent", "pt_date", "holdout", "ctx_mode",
                                                                   "t_call", "talk"]),
        chat=pl.read_parquet(R.SH / "chat_core.parquet", columns=["message_id", "t", "pt_date", "room", "speaker_kind", "agent"]),
        prod=pl.read_parquet(R.SH / "producing_calls.parquet", columns=["message_id", "turn_id_prod"]),
        items=pl.read_parquet(R.SH / "context_ledger_items.parquet", columns=["turn_id", "message_id", "kind", "ment"]),
    )


def secs(s):
    return s.dt.epoch("us").to_numpy() / 1e6


def build_unit(u, T, lab_of, seed=1):
    spec = B.UNITS[u]
    days = B.unit_days(spec)
    assert not any(holdout_mask(days, [spec[1]] * len(days)))
    dix = {d: i for i, d in enumerate(days)}
    cw = (T["cw"].filter(pl.col("pt_date").is_in(days) & ~pl.col("holdout") & (pl.col("ctx_mode") != "summary"))
          .sort("agent", "t_call"))
    c_agent = cw["agent"].to_numpy().astype(np.int64)
    c_day = np.array([dix[d] for d in cw["pt_date"].to_list()])
    c_tc = secs(cw["t_call"])
    c_talk = cw["talk"].to_numpy().astype(float)
    pos = {int(t): i for i, t in enumerate(cw["turn_id"].to_list())}
    ch = (T["chat"].filter(pl.col("pt_date").is_in(days) & (pl.col("speaker_kind") == "agent")).sort("t", "message_id")
          .join(T["st"], on="message_id", how="left").join(T["prod"], on="message_id", how="left"))
    m_t = secs(ch["t"])
    snd = ch["agent"].to_numpy().astype(np.int64)
    mday = np.array([dix[d] for d in ch["pt_date"].to_list()])
    prod = np.array([pos.get(int(t), -1) if t is not None else -1 for t in ch["turn_id_prod"].to_list()], np.int64)
    ok = prod >= 0
    ok &= np.where(ok, c_agent[np.maximum(prod, 0)] == snd, False)
    ok &= np.where(ok, c_day[np.maximum(prod, 0)] == mday, False)
    prod = np.where(ok, prod, -1)
    srow = ch["srow"].fill_null(-1).to_numpy().astype(np.int64)
    mid = ch["message_id"].to_list()
    midx = {m: i for i, m in enumerate(mid)}
    it = T["items"].filter((pl.col("kind") == "agent") & pl.col("turn_id").is_in(cw["turn_id"]) & pl.col("message_id").is_in(mid))
    p_pos = np.array([pos[int(t)] for t in it["turn_id"].to_list()], np.int64)
    p_msg = np.array([midx[m] for m in it["message_id"].to_list()], np.int64)
    p_ment = it["ment"].to_numpy().astype(bool)
    p_rec = c_agent[p_pos]
    keep = snd[p_msg] != p_rec
    p_pos, p_msg, p_ment, p_rec = p_pos[keep], p_msg[keep], p_ment[keep], p_rec[keep]
    # placebo statements m' (same sender, >= 2 h away, has a vector)
    rng = np.random.default_rng(seed)
    has = srow >= 0
    plc = np.full((len(m_t), 2), -1, np.int64)
    for a in np.unique(snd):
        idx = np.where((snd == a) & has)[0]
        ta = m_t[idx]
        for i in idx:
            far = idx[np.abs(ta - m_t[i]) >= 7200]
            if len(far):
                plc[i] = rng.choice(far, 2)
    # content rows
    rows = {k: [] for k in ("src", "B", "h", "age", "ment", "rday")}
    use = has[p_msg]
    for j in np.unique(p_rec[use]):
        S = np.where((snd == j) & has & (prod >= 0))[0]
        if len(S) == 0:
            continue
        TS = m_t[S]
        P = np.where(use & (p_rec == j))[0]
        tm = m_t[p_msg[P]]
        i0 = np.searchsorted(TS, tm, side="right")
        for k in range(8):
            ii = i0 + k
            okk = ii < len(S)
            Pk, Bk = P[okk], S[ii[okk]]
            age = m_t[Bk] - m_t[p_msg[Pk]]
            hb = prod[Bk] - p_pos[Pk] + 1
            o2 = (age <= 1800) & (c_day[prod[Bk]] == c_day[p_pos[Pk]]) & (hb >= 0) & (hb <= HMAX)
            rows["src"].append(p_msg[Pk][o2]); rows["B"].append(Bk[o2]); rows["h"].append(hb[o2])
            rows["age"].append(age[o2]); rows["ment"].append(p_ment[Pk][o2]); rows["rday"].append(c_day[p_pos[Pk]][o2])
    rows = {k: np.concatenate(v) if v else np.zeros(0) for k, v in rows.items()}
    labs = np.array([lab_of.get(int(a)) for a in range(64)], dtype=object)
    lg = np.array([LABG.get(l, 3) for l in labs])
    src = rows["src"].astype(np.int64)
    Bm = rows["B"].astype(np.int64)
    out = dict(src=src, B=Bm, h=rows["h"].astype(np.int8), age=rows["age"].astype(np.float32),
               ment=rows["ment"].astype(bool), rday=rows["rday"].astype(np.int16),
               t_src=m_t[src], s_agent=snd[src].astype(np.int8), r_agent=snd[Bm].astype(np.int8),
               same=(labs[snd[src]] == labs[snd[Bm]]), s_lg=lg[snd[src]].astype(np.int8), r_lg=lg[snd[Bm]].astype(np.int8),
               m_srow=srow, plc=plc, day_t0=np.array([m_t[mday == d].min() if (mday == d).any() else 0 for d in range(len(days))]),
               # talk: reads per call by (same lab, named)
               c_agent=c_agent.astype(np.int8), c_day=c_day.astype(np.int16), c_talk=c_talk.astype(np.int8), c_tc=c_tc)
    same_read = labs[snd[p_msg]] == labs[p_rec]
    Rc = np.zeros((len(c_tc), 4), np.int16)                  # same_un, same_nm, cross_un, cross_nm
    np.add.at(Rc, (p_pos, (~same_read) * 2 + p_ment), 1)
    out["c_reads"] = Rc
    OUTD.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUTD / f"u{u}.npz", **out)
    return dict(unit=u, n_rows=len(src), n_h1=int(((out["h"] == 1) & (out["age"] < 60)).sum()),
                n_h0=int(((out["h"] == 0) & (out["age"] < 60)).sum()), n_calls=len(c_tc), n_reads=len(p_msg))


def outcome(D, model="bge", kind="white32"):
    f = {"white32": f"statements_white32_{R.MODELS[model]}.npy",
         "srp": f"statements_style_resid_period32_{R.MODELS[model]}.npy"}[kind]
    A = np.load(R.ED / f, mmap_mode="r")
    srow = D["m_srow"]
    Z = np.full((len(srow), 32), np.nan, np.float32)
    okv = srow >= 0
    Z[okv] = R.unitv(np.asarray(A[srow[okv]])).astype(np.float32)
    zb, zs = Z[D["B"]], Z[D["src"]]
    y_raw = np.einsum("ij,ij->i", zb, zs)
    pc = []
    for q in range(2):
        pi = D["plc"][D["src"], q]
        pc.append(np.where(pi >= 0, np.einsum("ij,ij->i", zb, Z[np.maximum(pi, 0)]), np.nan))
    return y_raw - np.nanmean(np.vstack(pc), 0)


# ============================================================================ estimators
BLOCK = "hour"     # Amendment C-A1 (after the synthetic, before real data): 1-h blocks in every unit ("day" = pre-reg)


def blocks(D):
    nd = len(D["day_t0"])
    if nd >= 3 and BLOCK == "day":
        return D["rday"].astype(np.int64), nd
    h = np.clip(((D["t_src"] - D["day_t0"][D["rday"]]) // 3600).astype(np.int64), 0, 47)
    return D["rday"].astype(np.int64) * 48 + h, nd * 48


HPULL = 1          # hops pooled into the "read" side (1 = pre-registered J^c_1; 2 = Amendment C-A3 variant)


def cells(y, h, age, blk, nblk, sel, hpull=None):
    hp = HPULL if hpull is None else hpull
    ok = sel & np.isfinite(y) & (age < BINS[-1]) & (h <= hp)
    b = np.digitize(age[ok], BINS) - 1
    hh = np.minimum(h[ok].astype(int), 1)
    S = np.zeros((nblk, 2, len(BINS) - 1)); N = np.zeros_like(S)
    np.add.at(S, (blk[ok], hh, b), y[ok]); np.add.at(N, (blk[ok], hh, b), 1.0)
    return S, N


def jump(S, N, w=None):
    Ss, Ns = (S.sum(0), N.sum(0)) if w is None else (np.tensordot(w, S, 1), np.tensordot(w, N, 1))
    n0, n1 = Ns[0], Ns[1]
    ok = (n0 > 0) & (n1 > 0)
    if not ok.any():
        return np.nan
    wt = np.where(ok, n0 * n1 / np.maximum(n0 + n1, 1e-9), 0)
    d = np.where(ok, Ss[1] / np.maximum(n1, 1e-9) - Ss[0] / np.maximum(n0, 1e-9), 0)
    return float((wt * d).sum() / wt.sum())


def family_jumps(D, y, nboot=NBOOT, seed=7, hpull=None):
    """J (all), J_same, J_cross per naming stratum and named-stratified Delta, with paired block-bootstrap draws."""
    blk, nblk = blocks(D)
    h, age, ment, same = D["h"], D["age"], D["ment"], D["same"]
    subsets = {"all": np.ones(len(h), bool), "same": same, "cross": ~same}
    for s, m in (("nm", ment), ("un", ~ment)):
        subsets[f"same_{s}"] = same & m
        subsets[f"cross_{s}"] = ~same & m
        subsets[f"all_{s}"] = m
    C = {k: cells(y, h, age, blk, nblk, v, hpull) for k, v in subsets.items()}
    in60 = (age < 60) & (h == 1)
    w_nm = float((in60 & ment).sum() / max(in60.sum(), 1))
    counts = {k: int((v & in60).sum()) for k, v in subsets.items()}
    counts.update({k + "_h0": int((v & (age < 60) & (h == 0)).sum()) for k, v in subsets.items()})

    def stats(w):
        J = {k: jump(*C[k], w) for k in C}
        J["delta_raw"] = J["same"] - J["cross"]
        J["delta_adj"] = w_nm * (J["same_nm"] - J["cross_nm"]) + (1 - w_nm) * (J["same_un"] - J["cross_un"])
        return J
    est = stats(None)
    used = np.unique(blk[np.isfinite(y) & (age < 60) & (h <= (HPULL if hpull is None else hpull))])
    rng = np.random.default_rng(seed)
    bs = [stats(np.bincount(rng.choice(used, len(used)), minlength=nblk).astype(float)) for _ in range(nboot)] if len(used) >= 2 else []
    out = {}
    for k, v in est.items():
        arr = np.array([b[k] for b in bs], float) if bs else np.array([np.nan])
        out[k] = dict(est=v, se=float(np.nanstd(arr)), lo=float(np.nanpercentile(arr, 2.5)) if bs else np.nan,
                      hi=float(np.nanpercentile(arr, 97.5)) if bs else np.nan, draws=arr)
    n1, n0 = counts["all"], counts["all_h0"]
    out["weight"] = n1 * n0 / max(n1 + n0, 1)
    out["w_named"] = w_nm
    out["counts"] = counts
    return out


def kxk_jumps(D, y):
    """J^c_1 by sender lab group x receiver lab group (point estimates and row counts)."""
    blk, nblk = blocks(D)
    M = np.full((4, 4), np.nan); Nn = np.zeros((4, 4), int)
    for a in range(4):
        for b in range(4):
            sel = (D["s_lg"] == a) & (D["r_lg"] == b)
            S, N = cells(y, D["h"], D["age"], blk, nblk, sel)
            M[a, b] = jump(S, N)
            Nn[a, b] = int(N[:, 1].sum())
    return M, Nn


def talk_fit(D, nboot=NBOOT, seed=11, y=None):
    """LPM talk ~ reads (same_un, same_nm, cross_un, cross_nm), agent-day FE; returns betas and named-stratified
    Delta beta and beta_bar (all reads) with block-bootstrap CIs (day blocks, or 1-h blocks for < 3 days)."""
    y = D["c_talk"].astype(float) if y is None else y
    X = D["c_reads"].astype(float)
    g = D["c_agent"].astype(np.int64) * 100 + D["c_day"]
    _, gi = np.unique(g, return_inverse=True)
    cnt = np.bincount(gi).astype(float)
    def dm(M):
        M = M if M.ndim == 2 else M[:, None]
        S = np.zeros((cnt.size, M.shape[1])); np.add.at(S, gi, M)
        return M - (S / cnt[:, None])[gi]
    Xd, yd = dm(X), dm(y)[:, 0]
    nd = len(D["day_t0"])
    if nd >= 3 and BLOCK == "day":
        blk, nblk = D["c_day"].astype(np.int64), nd
    else:
        hh = np.clip(((D["c_tc"] - D["day_t0"][D["c_day"]]) // 3600).astype(np.int64), 0, 47)
        blk, nblk = D["c_day"].astype(np.int64) * 48 + hh, nd * 48
    G = np.zeros((nblk, 4, 4)); V = np.zeros((nblk, 4))
    for j in range(4):
        np.add.at(G[:, j, :], blk, Xd[:, j:j + 1] * Xd)
        np.add.at(V[:, j], blk, Xd[:, j] * yd)
    tot = X.sum(0)
    w_nm = float((tot[1] + tot[3]) / max(tot.sum(), 1))
    def solve(w):
        A = np.tensordot(w, G, 1); v = np.tensordot(w, V, 1)
        try:
            b = np.linalg.solve(A + 1e-9 * np.eye(4), v)
        except np.linalg.LinAlgError:
            b = np.full(4, np.nan)
        d_adj = w_nm * (b[1] - b[3]) + (1 - w_nm) * (b[0] - b[2])
        # beta_bar: read-count-weighted mean effect per read item
        bbar = float((b * tot).sum() / max(tot.sum(), 1))
        return np.r_[b, d_adj, bbar]
    est = solve(np.ones(nblk))
    used = np.unique(blk)
    rng = np.random.default_rng(seed)
    bs = np.array([solve(np.bincount(rng.choice(used, len(used)), minlength=nblk).astype(float)) for _ in range(nboot)])
    names = ["same_un", "same_nm", "cross_un", "cross_nm", "delta_adj", "beta_bar"]
    return {n: dict(est=float(est[k]), se=float(np.nanstd(bs[:, k])), lo=float(np.nanpercentile(bs[:, k], 2.5)),
                    hi=float(np.nanpercentile(bs[:, k], 97.5)), draws=bs[:, k]) for k, n in enumerate(names)} | {
        "w_named": w_nm, "n_calls": int(len(y)), "weight": float(tot.sum())}


def ivw(vals):
    e = np.array([v["est"] for v in vals], float); s = np.array([v["se"] for v in vals], float)
    ok = np.isfinite(e) & np.isfinite(s) & (s > 0)
    if not ok.any():
        return dict(est=np.nan, se=np.nan, lo=np.nan, hi=np.nan, k=0)
    w = 1 / s[ok] ** 2
    m = float((w * e[ok]).sum() / w.sum()); se = float(1 / np.sqrt(w.sum()))
    return dict(est=m, se=se, lo=m - 1.96 * se, hi=m + 1.96 * se, k=int(ok.sum()))


def pool_draws(vals, weights):
    """Amendment C-A2: fixed-weight pooling (content: n1 n0 / (n1 + n0); talk: read items). Pooled bootstrap draw b =
    weighted mean of the units' draw b (units are bootstrapped independently); percentile CI."""
    w = np.asarray(weights, float)
    e = np.array([v["est"] for v in vals], float)
    ok = np.isfinite(e) & (w > 0)
    if not ok.any():
        return dict(est=np.nan, se=np.nan, lo=np.nan, hi=np.nan, k=0)
    nb = min(len(v["draws"]) for v, o in zip(vals, ok) if o)
    Dr = np.array([np.asarray(v["draws"])[:nb] for v, o in zip(vals, ok) if o])
    ww = w[ok] / w[ok].sum()
    Dr = np.where(np.isfinite(Dr), Dr, e[ok][:, None])
    pd = ww @ Dr
    est = float(ww @ e[ok])
    return dict(est=est, se=float(pd.std()), lo=float(np.percentile(pd, 2.5)), hi=float(np.percentile(pd, 97.5)),
                k=int(ok.sum()))


def load(u):
    z = np.load(OUTD / f"u{u}.npz", allow_pickle=False)
    return {k: z[k] for k in z.files}


def eligible(D):
    in60 = D["age"] < 60
    return int(((D["h"] == 1) & in60).sum()) >= 200 and int(((D["h"] == 0) & in60).sum()) >= 200


# ============================================================================ synthetic (real rows, synthetic outcomes)
def syn_y(D, world, rng, Jbar=0.033, sig=0.25):
    n = len(D["h"])
    blk, nblk = blocks(D)
    y = 0.08 * np.exp(-D["age"] / 20.0) + rng.normal(0, 0.01, nblk)[blk] + rng.normal(0, sig, n)
    h1 = D["h"] >= 1
    ment, same = D["ment"], D["same"]
    w_nm = float(((D["age"] < 60) & (D["h"] == 1) & ment).sum() / max(((D["age"] < 60) & (D["h"] == 1)).sum(), 1))
    j_un = Jbar / (1 + 4 * w_nm)                          # named = 5 x unnamed; naming-weighted mean = Jbar
    pull = np.where(ment, 5 * j_un, j_un)
    if world == "N0":
        return y
    if world == "N4":                                      # only named couple
        return y + h1 * np.where(ment, Jbar / max(w_nm, 1e-6), 0.0)
    y = y + h1 * pull
    if world == "N2":
        y = y + h1 * same * 0.5 * Jbar
    if world == "N3":                                      # family-common drive at every hop, no family coupling
        y = y + same * 0.03 * np.exp(-D["age"] / 30.0)
    return y


def syn_talk(D, world, rng, b_un=0.003, b_nm=0.015):
    X = D["c_reads"].astype(float)
    g = D["c_agent"].astype(np.int64) * 100 + D["c_day"]
    _, gi = np.unique(g, return_inverse=True)
    base = np.clip(np.bincount(gi, weights=D["c_talk"]) / np.bincount(gi), 0.02, 0.9)[gi]
    b = np.array([b_un, b_nm, b_un, b_nm]) * (3.0 if world == "T1s" else 1.0)
    if world == "T2":
        tot = X.sum(0)
        bbar = float((b * tot).sum() / max(tot.sum(), 1))
        b = b + np.array([0.5 * bbar, 0.5 * bbar, 0, 0])
    if world == "T0":
        b = b * 0
    p = np.clip(base + X @ b - (X @ b).mean(), 0.001, 0.999)
    return (rng.random(len(p)) < p).astype(float)


def synthetic(reps=40, seed=3, all_units=False, hpull=1, talk=True):
    rng = np.random.default_rng(seed)
    units = [u for u in REGIME_III if (OUTD / f"u{u}.npz").exists()]
    Ds = {u: load(u) for u in units}
    if not all_units:
        Ds = {u: D for u, D in Ds.items() if eligible(D)}
    out = {"units": list(Ds), "hpull": hpull, "all_units": all_units}
    for world in ("N0", "N1", "N2", "N3", "N4"):
        rec = {"adj": [], "adj_lo": [], "adj_hi": [], "raw": [], "raw_lo": [], "raw_hi": [], "all": []}
        for r in range(reps):
            fj = {u: family_jumps(D, syn_y(D, world, rng), nboot=100, seed=r, hpull=hpull) for u, D in Ds.items()}
            wts = [fj[u]["weight"] for u in Ds]
            a = pool_draws([fj[u]["delta_adj"] for u in Ds], wts); b = pool_draws([fj[u]["delta_raw"] for u in Ds], wts)
            c = pool_draws([fj[u]["all"] for u in Ds], wts)
            rec["adj"].append(a["est"]); rec["adj_lo"].append(a["lo"]); rec["adj_hi"].append(a["hi"])
            rec["raw"].append(b["est"]); rec["raw_lo"].append(b["lo"]); rec["raw_hi"].append(b["hi"]); rec["all"].append(c["est"])
        A = {k: np.array(v) for k, v in rec.items()}
        out[world] = dict(adj_mean=float(A["adj"].mean()), adj_sd=float(A["adj"].std()),
                          rate_adj_ci_pos=float((A["adj_lo"] > 0).mean()), rate_adj_ci_neg=float((A["adj_hi"] < 0).mean()),
                          raw_mean=float(A["raw"].mean()), rate_raw_ci_excl0=float(((A["raw_lo"] > 0) | (A["raw_hi"] < 0)).mean()),
                          J_all_mean=float(A["all"].mean()),
                          rate_upper_below_half=float((A["adj_hi"] < 0.5 * A["all"]).mean()))
        print(world, out[world], flush=True)
    for world in (("T0", "T1", "T2", "T1s") if talk else ()):
        rec = {"d": [], "lo": [], "hi": [], "bbar": []}
        for r in range(max(reps // 2, 10)):
            tf = {u: talk_fit(D, nboot=100, seed=r, y=syn_talk(D, world, rng)) for u, D in Ds.items()}
            wts = [tf[u]["weight"] for u in Ds]
            a = pool_draws([tf[u]["delta_adj"] for u in Ds], wts); bb = pool_draws([tf[u]["beta_bar"] for u in Ds], wts)
            rec["d"].append(a["est"]); rec["lo"].append(a["lo"]); rec["hi"].append(a["hi"]); rec["bbar"].append(bb["est"])
        A = {k: np.array(v) for k, v in rec.items()}
        out[world] = dict(d_mean=float(A["d"].mean()), rate_ci_pos=float((A["lo"] > 0).mean()),
                          rate_ci_neg=float((A["hi"] < 0).mean()), bbar_mean=float(A["bbar"].mean()),
                          rate_upper_below_half=float((A["hi"] < 0.5 * A["bbar"]).mean()))
        print(world, out[world], flush=True)
    return out


def run():
    res = {"units": {}}
    for u in R.COUNTED + R.DESCRIPTIVE:
        p = OUTD / f"u{u}.npz"
        if not p.exists():
            continue
        D = load(u)
        r = {"eligible": eligible(D), "n_h1": int(((D["h"] == 1) & (D["age"] < 60)).sum()),
             "n_h0": int(((D["h"] == 0) & (D["age"] < 60)).sum())}
        if r["eligible"]:
            for model, kind in (("bge", "white32"), ("gte", "white32"), ("bge", "srp")):
                y = outcome(D, model, kind)
                r[f"{model}_{kind}"] = family_jumps(D, y)
                if model == "bge" and kind == "white32":
                    M, Nn = kxk_jumps(D, y)
                    r["kxk"] = M.tolist(); r["kxk_n"] = Nn.tolist()
        r["talk"] = talk_fit(D)
        res["units"][u] = r
        _d = lambda x: {k: v for k, v in x.items() if k != "draws"} if isinstance(x, dict) else x
        print(u, r["eligible"], _d(r.get("bge_white32", {}).get("delta_adj")), _d(r["talk"]["delta_adj"]), flush=True)
    pooled = {}
    for scope, units in (("III", REGIME_III), ("II", ["35"])):
        el = [u for u in units if u in res["units"] and res["units"][u]["eligible"]]
        for ch in ("bge_white32", "gte_white32", "bge_srp"):
            wts = [res["units"][u][ch]["weight"] for u in el]
            for k in ("all", "same", "cross", "delta_raw", "delta_adj", "same_nm", "cross_nm", "same_un", "cross_un",
                      "all_nm", "all_un"):
                pooled[f"{scope}|{ch}|{k}"] = pool_draws([res["units"][u][ch][k] for u in el], wts)
                pooled[f"{scope}|{ch}|{k}|ivw_prereg"] = ivw([res["units"][u][ch][k] for u in el])
        tl = [u for u in units if u in res["units"]]
        wts = [res["units"][u]["talk"]["weight"] for u in tl]
        for k in ("same_un", "same_nm", "cross_un", "cross_nm", "delta_adj", "beta_bar"):
            pooled[f"{scope}|talk|{k}"] = pool_draws([res["units"][u]["talk"][k] for u in tl], wts)
        pooled[f"{scope}|n_eligible"] = len(el)
    # pooled K x K (inverse-row-count weighting is not available per cell; row-count weighted mean of unit cells)
    el = [u for u in REGIME_III if u in res["units"] and res["units"][u]["eligible"]]
    M = np.zeros((4, 4)); W = np.zeros((4, 4))
    for u in el:
        m = np.array(res["units"][u]["kxk"], float); n = np.array(res["units"][u]["kxk_n"], float)
        ok = np.isfinite(m) & (n >= 50)
        M[ok] += m[ok] * n[ok]; W[ok] += n[ok]
    pooled["kxk_III"] = np.where(W > 0, M / np.maximum(W, 1), np.nan).tolist()
    pooled["kxk_III_n"] = W.tolist()
    res["pooled"] = pooled
    for u, r in res["units"].items():
        for ch, v in r.items():
            if isinstance(v, dict):
                for k, x in v.items():
                    if isinstance(x, dict):
                        x.pop("draws", None)
    R.dump(res, R.R2 / "readout.json")
    return res


def main():
    t0 = time.time()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "build":
        T = tabs()
        lab_of, _ = R.roster_labs()
        info = [build_unit(u, T, lab_of) for u in R.COUNTED + R.DESCRIPTIVE]
        for i in info:
            print(i, flush=True)
        R.dump({"units": info, "seconds": round(time.time() - t0)}, OUTD / "build_info.json")
    elif cmd == "synthetic":
        reps = int(sys.argv[sys.argv.index("--reps") + 1]) if "--reps" in sys.argv else 40
        out = {"primary": synthetic(reps)}
        out["all_units_hop12"] = synthetic(reps, seed=4, all_units=True, hpull=2, talk=False)
        out["eligible_hop12"] = synthetic(reps, seed=5, all_units=False, hpull=2, talk=False)
        out["all_units_hop1"] = synthetic(reps, seed=6, all_units=True, hpull=1, talk=False)
        out["seconds"] = round(time.time() - t0)
        R.dump(out, R.R2 / "synthetic_C.json")
    else:
        run()


if __name__ == "__main__":
    main()
