"""H72 round 2 library: context composition (copied from H16), the wake design, the competing-mechanism models,
day-blocked cross-validated log scores, frozen-slope transfer between periods, and sequential synthetic worlds.

Copied, not imported (STANDARDS section 8): `composition` and `recency_share` follow H16 analysis/r2lib.py
(round 2, 2026-10-05) line for line, minus the token ruler (U-tok needs H45's prompt calibration and was descriptive in
H16). `simulate_traps` and `trap_index` follow the same file.

Model terms (card, "Round 2"):
  base B   agent FE; nuisance z (round-1 prep: previous pause bins, hour-of-day bins, swarm_act10, ln last run);
           current reads at the wake (ln(1 + directed), ln(1 + undirected), own nudge, bookend);
           short-window flag (< 5 calls earlier today); reset at the wake (forced, voluntary; regime III);
           trap kind at start (after_fail, after_talk vs after_work).
  A        aging clocks: ln a_sus (min) and ln k_sus (wake index; H16 frailty lesson).
  S        input starvation: ln s_dir (min since the last directed read; s_dir_none indicator).
  C        chatter hold: ln(1 + U5), undirected novel items read at the 5 calls before the wake.
  W        ln(duration of the 5-call window) (rate variant: C + W = dose at fixed window = chatter rate).
  F        context self-share: ln(1 - f_call) (H16 U-call urn; regime III only).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import hazard_fe as HF  # noqa: E402

OUT = ROOT / "data/processed/H72-trap-aging-input-starvation"
R2 = OUT / "r2"
FLOOR = 10.0
F_CAP = 0.98
M_REC = 10
SEED = 20261005
MIN_EVENTS = 30


# ============================================================================ composition (copied from H16 r2lib)
def recency_share(kn: np.ndarray, idle: np.ndarray, seg: np.ndarray, M: int = M_REC) -> np.ndarray:
    """Idle-call share among the last M entries before each call's own entry (H16 r2lib, verbatim logic)."""
    n = len(kn)
    step = kn.astype(np.int64) + 1
    end_pos = np.cumsum(step)
    call_pos = end_pos - 1
    pos_c = call_pos
    new = np.r_[True, seg[1:] != seg[:-1]]
    first_idx = np.maximum.accumulate(np.where(new, np.arange(n), 0))
    seg_start = (end_pos - step)[first_idx]
    lo = np.maximum(pos_c - M, seg_start)
    idle_pos = call_pos[idle]
    cnt = np.searchsorted(idle_pos, pos_c, "left") - np.searchsorted(idle_pos, lo, "left")
    L = pos_c - lo
    return np.where(L > 0, cnt / np.maximum(L, 1), np.nan)


def composition(calls: pl.DataFrame) -> pl.DataFrame:
    """Per-call composition: segment (ctx_pos restarts), n_rep / n_act (own idle / active calls earlier in the segment),
    kc (room items in the context, including the call's new items), f_call, f_entry, f_rec (H16 r2lib, minus U-tok)."""
    c = calls.sort("agent", "t_call", "turn_id")
    c = c.with_columns(idle=(pl.col("kind").cast(pl.Utf8).is_in(["pause", "wait"]) & ~pl.col("talk")))
    c = c.with_columns(newseg=(pl.col("ctx_pos") == 1) | (pl.col("ctx_pos") <= pl.col("ctx_pos").shift(1).over("agent")).fill_null(True))
    c = c.with_columns(seg=pl.col("newseg").cast(pl.Int32).cum_sum().over("agent"))
    c = c.with_columns(
        n_rep=(pl.col("idle").cast(pl.Int32).cum_sum().over("agent", "seg") - pl.col("idle").cast(pl.Int32)),
        n_act=((~pl.col("idle")).cast(pl.Int32).cum_sum().over("agent", "seg") - (~pl.col("idle")).cast(pl.Int32)),
        kc=pl.col("k_new").cast(pl.Int64).cum_sum().over("agent", "seg"),
    )
    frec = np.full(c.height, np.nan)
    ag = c["agent"].to_numpy(); kn = c["k_new"].to_numpy(); idl = c["idle"].to_numpy(); sg = c["seg"].to_numpy()
    cuts = np.flatnonzero(np.diff(ag)) + 1
    for lo, hi in zip(np.r_[0, cuts], np.r_[cuts, len(ag)]):
        frec[lo:hi] = recency_share(kn[lo:hi], idl[lo:hi], sg[lo:hi])
    c = c.with_columns(pl.Series("f_rec", frec))
    c = c.with_columns(
        f_call=pl.when((pl.col("n_rep") + pl.col("n_act")) > 0).then(pl.col("n_rep") / (pl.col("n_rep") + pl.col("n_act"))).otherwise(None),
        f_entry=pl.when((pl.col("n_rep") + pl.col("n_act") + pl.col("kc")) > 0)
        .then(pl.col("n_rep") / (pl.col("n_rep") + pl.col("n_act") + pl.col("kc"))).otherwise(None),
    )
    return c.drop("newseg")


def lnq(f) -> np.ndarray:
    f = np.asarray(f, float)
    return np.log(np.clip(1.0 - np.nan_to_num(f, nan=0.0), 1.0 - F_CAP, 1.0))


def lmin(x):
    return np.log(np.maximum(np.asarray(x, dtype=float), FLOOR) / 60.0)


# ============================================================================ design
def load_wakes(goal: int, sample: str = "primary") -> pl.DataFrame:
    """At-risk wakes of one period. primary: sustained-escape rows with a_sus, H16's G51 window (r16), consolidation-
    start traps dropped. 'all': no consolidation drop (bridge to H16)."""
    w = pl.read_parquet(R2 / "wakes_r2.parquet").filter(pl.col("goal_no") == goal)
    w = w.filter(pl.col("y_sus").is_not_null() & pl.col("a_sus").is_not_null() & pl.col("r16"))
    if sample == "primary":
        w = w.filter(~pl.col("consol_start"))
    return w.sort("agent", "pt_date", "t_call", "turn_id")


def prep(w: pl.DataFrame, dose: str = "U5", s_var: str = "dir", f_var: str = "f_call") -> dict:
    """Arrays for one period. Every term family is a dict of named columns."""
    y = w["y_sus"].cast(pl.Float64).to_numpy()
    n = len(y)
    regime3 = w["regime"][0] == "III"
    nd = w["n_dir"].to_numpy().astype(float)
    nn = w["n_novel"].to_numpy().astype(float)
    z = {
        "cur_dir": np.log1p(nd),
        "cur_undir": np.log1p(np.maximum(nn - nd, 0)),
        "cur_nudge": (w["n_nudge_me"].to_numpy() > 0).astype(float),
        "cur_bookend": (w["n_bookend"].to_numpy() > 0).astype(float),
        "swarm_act10": w["swarm_act10"].fill_null(0).to_numpy().astype(float),
        "ln_last_run": np.log(np.maximum(w["last_run_len"].fill_null(1).to_numpy().astype(float), 1)),
        "after_fail": (w["trap_kind"].to_numpy() == "after_fail").astype(float),
        "after_talk": (w["trap_kind"].to_numpy() == "after_talk").astype(float),
        "short_win": (w["nwin5"].to_numpy() < 5).astype(float),
    }
    pk = w["prev_kind"].to_numpy()
    ps = w["prev_pause_s"].to_numpy().astype(float)
    z["prev_wait"] = (pk == "wait").astype(float)
    z["pause_nodur"] = ((pk == "pause") & ~np.isfinite(ps)).astype(float)
    for lo, hi, nm in ((60, 300, "p60_300"), (300, 1800, "p300_1800"), (1800, np.inf, "p1800")):
        z[nm] = ((pk == "pause") & (ps > lo) & (ps <= hi)).astype(float)
    hd = np.clip(np.floor(w["h_day"].fill_null(0).to_numpy()), 0, 6)
    for h in range(1, 7):
        z[f"hday{h}"] = (hd == h).astype(float)
    if regime3:
        z["forced"] = w["forced"].fill_null(False).to_numpy().astype(float)
        z["vol"] = w["vol"].fill_null(False).to_numpy().astype(float)
    s_none = w[f"s_{s_var}_none"].to_numpy()
    s_raw = np.where(s_none, w["s_lc"].fill_null(FLOOR).to_numpy(), w[f"s_{s_var}"].fill_null(FLOOR).to_numpy())
    S = {"ln_s": lmin(s_raw)}
    if s_none.any() and not s_none.all():
        S["s_none"] = s_none.astype(float)
    C = {"ln_dose": np.log1p(w[dose].fill_null(0).to_numpy().astype(float))}
    u = w[dose].fill_null(0).to_numpy().astype(float)
    wmin = np.maximum(w["win5_s"].fill_null(FLOOR).to_numpy().astype(float), FLOOR) / 60.0
    W = {"ln_win5": np.log(wmin)}                                   # window duration (rate variant only)
    rate = np.where(u > 0, np.log(np.maximum(u, 1) / wmin), np.nan)  # ln chatter rate (items / min), U > 0 rows
    A = {"ln_a": lmin(w["a_sus"].to_numpy()), "ln_k": np.log(w["k_sus"].to_numpy().astype(float))}
    F = {}
    if regime3 and f_var in w.columns:
        F = {"lnq": lnq(w[f_var].to_numpy().astype(float))}
    days = w["pt_date"].to_numpy()
    _, day = np.unique(days, return_inverse=True)
    trap = (w["agent"].cast(pl.Utf8) + "|" + w["pt_date"] + "|" + w["trap_id"].cast(pl.Utf8)).to_numpy()
    _, trap_code = np.unique(trap, return_inverse=True)
    return {"y": y, "n": n, "z": {k: v for k, v in z.items() if np.std(v) > 0}, "S": S, "C": C, "A": A, "F": F, "W": W,
            "ln_rate": rate, "D": {"ln_ddose": np.log1p(w["D5"].fill_null(0).to_numpy().astype(float))},
            "agent": w["agent"].to_numpy(), "day": day, "days": days, "trap": trap_code,
            "dir_wake": (nd > 0).astype(float), "k": w["k_sus"].to_numpy(),
            "inflight": np.log1p(w["n_inflight_call"].to_numpy().astype(float)), "regime3": regime3}


def families(model: str) -> list[str]:
    """'B', 'B+A', 'B+S+C+F+A' ... -> term families."""
    return [] if model == "B" else model.split("+")[1:]


def columns(P: dict, model: str, extra: dict | None = None):
    cols, names = [], []
    for fam in families(model):
        for k, v in P[fam].items():
            cols.append(v); names.append(k)
    for k, v in (extra or {}).items():
        cols.append(v); names.append(k)
    for k, v in P["z"].items():
        cols.append(v); names.append(k)
    return np.column_stack(cols), names


def fit(P: dict, model: str, idx=None, extra=None, y=None, fe="agent", offset=None):
    C, names = columns(P, model, extra)
    g = P[fe] if isinstance(fe, str) else fe
    if idx is not None:
        C, g = C[idx], g[idx]
    yy = (P["y"] if y is None else y)
    yy = yy if idx is None else yy[idx]
    X, nm = HF.design(C, names, g)
    keep = np.r_[True, X[:, 1:].std(axis=0) > 0]
    f = HF.fit_binary(X[:, keep], yy)
    beta = np.zeros(X.shape[1]); beta[keep] = f["beta"]
    se = np.full(X.shape[1], np.nan); se[keep] = np.sqrt(np.diag(f["cov"]))
    return {"beta": dict(zip(nm, beta)), "se": dict(zip(nm, se)), "names": nm, "bvec": beta, "ll": f["ll"],
            "converged": f["converged"], "cov": f["cov"], "keep": keep}


def b(fitres, term):
    return float(fitres["beta"][term]), float(fitres["se"][term])


# ============================================================================ cross-validated log scores
RECONCILE = ("B", "B+A", "B+S", "B+C", "B+F", "B+S+A", "B+C+A", "B+F+A", "B+S+C+F", "B+S+C+F+A")


def cv_per_day(P: dict, models=RECONCILE, k: int = 5, y=None) -> dict:
    """Day-blocked CV (5 interleaved day folds): per-day held-out log-likelihood for each model (agent FE; an agent
    unseen in training gets the reference level)."""
    yy = P["y"] if y is None else y
    folds = HF.interleaved_folds(P["day"], k)
    nd = P["day"].max() + 1
    out = {}
    for m in models:
        if "F" in families(m) and not P["F"]:
            continue
        C, names = columns(P, m)
        X, nm = HF.design(C, names, P["agent"])
        per = np.zeros(nd)
        for f in range(k):
            tr = np.flatnonzero(folds != f); te = np.flatnonzero(folds == f)
            Xtr = X[tr]
            keep = np.r_[True, Xtr[:, 1:].std(axis=0) > 0]
            fr = HF.fit_binary(Xtr[:, keep], yy[tr])
            beta = np.zeros(X.shape[1]); beta[keep] = fr["beta"]
            ll = HF.loglik_binary(X[te], yy[te], beta)
            np.add.at(per, P["day"][te], ll)
        out[m] = per
    return out


def cv_stats(per: dict, n: int, B: int = 1000, seed: int = 0) -> dict:
    """Gains (nats per 1,000 wakes) and aging shares with a day bootstrap of per-day contributions."""
    rng = np.random.default_rng(seed)
    nd = len(per["B"])
    picks = [rng.integers(0, nd, nd) for _ in range(B)]
    sc = 1000.0 / n
    defs = {}
    for M in ("A", "S", "C", "F"):
        if f"B+{M}" in per:
            defs[f"gain_{M}"] = (lambda p, M=M: p[f"B+{M}"] - p["B"])
    if "B+S+C+F" in per:
        defs["gain_SCF"] = lambda p: p["B+S+C+F"] - p["B"]
    out = {}
    for nm, fn in defs.items():
        v = fn(per)
        bs = [v[i].sum() * sc for i in picks]
        out[nm] = [float(v.sum() * sc), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
    # aging information left after mechanism M, and the explained share eps(M) = 1 - left / G(A)
    GA = per["B+A"] - per["B"]
    eps = {}
    for M, mm in (("S", "B+S"), ("C", "B+C"), ("F", "B+F"), ("SCF", "B+S+C+F")):
        if mm in per and f"{mm}+A" in per:
            left = per[f"{mm}+A"] - per[mm]
            eps[M] = left
    for M, left in eps.items():
        e = 1 - left.sum() / GA.sum()
        bs = []
        for i in picks:
            ga = GA[i].sum()
            bs.append(1 - left[i].sum() / ga if ga > 0 else np.nan)
        out[f"eps_{M}"] = [float(e), float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5))]
    for M1, M2 in (("F", "C"), ("F", "S"), ("C", "S")):
        if M1 in eps and M2 in eps:
            d = (eps[M2] - eps[M1]).sum() / GA.sum()      # eps(M1) - eps(M2)
            bs = []
            for i in picks:
                ga = GA[i].sum()
                bs.append((eps[M2][i].sum() - eps[M1][i].sum()) / ga if ga > 0 else np.nan)
            out[f"deps_{M1}_{M2}"] = [float(d), float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5))]
    return out


# ============================================================================ frozen-slope transfer between periods
def transfer(P_src: dict, P_tgt: dict, fam: str, k: int = 5) -> list:
    """Slopes of family `fam` fitted on the whole source period (model B+fam) enter the target as a fixed offset; the
    target's base (agent FE + nuisance) is re-fitted on its training day folds. Returns the held-out gain over the
    target's base (nats per 1,000 wakes) with a day bootstrap."""
    fs = fit(P_src, f"B+{fam}")
    off = np.zeros(P_tgt["n"])
    for kname, v in P_tgt[fam].items():
        off += fs["beta"].get(kname, 0.0) * v
    folds = HF.interleaved_folds(P_tgt["day"], k)
    C, names = columns(P_tgt, "B")
    X, _ = HF.design(C, names, P_tgt["agent"])
    nd = P_tgt["day"].max() + 1
    per0, per1 = np.zeros(nd), np.zeros(nd)
    for f in range(k):
        tr = np.flatnonzero(folds != f); te = np.flatnonzero(folds == f)
        keep = np.r_[True, X[tr][:, 1:].std(axis=0) > 0]
        b0 = np.zeros(X.shape[1]); b0[keep] = HF.fit_binary(X[tr][:, keep], P_tgt["y"][tr])["beta"]
        b1 = np.zeros(X.shape[1]); b1[keep] = fit_offset(X[tr][:, keep], P_tgt["y"][tr], off[tr])
        np.add.at(per0, P_tgt["day"][te], HF.loglik_binary(X[te], P_tgt["y"][te], b0))
        mu = 1 / (1 + np.exp(-(X[te] @ b1 + off[te])))
        mu = np.clip(mu, 1e-10, 1 - 1e-10)
        yt = P_tgt["y"][te]
        np.add.at(per1, P_tgt["day"][te], yt * np.log(mu) + (1 - yt) * np.log(1 - mu))
    v = per1 - per0
    rng = np.random.default_rng(SEED)
    sc = 1000.0 / P_tgt["n"]
    bs = [v[rng.integers(0, nd, nd)].sum() * sc for _ in range(1000)]
    return [float(v.sum() * sc), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]


def fit_offset(X, y, off, maxit=60):
    beta = np.zeros(X.shape[1])
    for _ in range(maxit):
        mu = np.clip(1 / (1 + np.exp(-(X @ beta + off))), 1e-10, 1 - 1e-10)
        W = mu * (1 - mu)
        H = (X * W[:, None]).T @ X + np.diag(np.r_[0.0, np.full(X.shape[1] - 1, 1e-6)])
        step = np.linalg.solve(H, X.T @ (y - mu))
        beta = beta + step
        if np.max(np.abs(step)) < 1e-7:
            break
    return beta


# ============================================================================ day-block bootstrap
def boot(P: dict, fn, B: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    rpd = HF.rows_per_day(P["day"])
    out = []
    for _ in range(B):
        idx = HF.block_resample(P["day"], rng, rpd)
        try:
            out.append(np.atleast_1d(fn(idx)))
        except Exception:  # noqa: BLE001
            continue
    return np.array(out, float)


def pct(a):
    a = np.asarray(a, float)
    a = a[np.isfinite(a)]
    if len(a) < 10:
        return [float("nan"), float("nan")]
    return [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))]


# ============================================================================ sequential simulation (copied from H16)
def trap_index(P: dict):
    """Row ranges of each trap (rows sorted by agent, day, t_call)."""
    tr = P["trap"]
    cuts = np.flatnonzero(tr[1:] != tr[:-1]) + 1
    return np.r_[0, cuts], np.r_[cuts, len(tr)]


def simulate_traps(rng, p: np.ndarray, starts, ends):
    """Walk each trap: outcome per wake with prob p; stop at the first escape; censor at the real trap end."""
    hit = rng.random(len(p)) < p
    keep = np.zeros(len(p), bool)
    y = np.zeros(len(p), np.int8)
    for s, e in zip(starts, ends):
        h = np.flatnonzero(hit[s:e])
        if len(h):
            j = s + h[0]
            keep[s:j + 1] = True
            y[j] = 1
        else:
            keep[s:e] = True
    return keep, y


def subset(P: dict, mask: np.ndarray) -> dict:
    Q = {}
    for k, v in P.items():
        if isinstance(v, np.ndarray) and len(v) == P["n"]:
            Q[k] = v[mask]
        elif isinstance(v, dict):
            Q[k] = {kk: vv[mask] for kk, vv in v.items()}
        else:
            Q[k] = v
    Q["z"] = {k: v for k, v in Q["z"].items() if np.std(v) > 0}
    Q["n"] = int(mask.sum())
    _, Q["day"] = np.unique(Q["day"], return_inverse=True)
    return Q


def jdump(obj, path: Path):
    def conv(o):
        if isinstance(o, (np.floating,)):
            return None if not np.isfinite(o) else float(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, np.ndarray):
            return [conv(x) for x in o.tolist()]
        if isinstance(o, float) and not np.isfinite(o):
            return None
        if isinstance(o, dict):
            return {str(k): conv(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [conv(x) for x in o]
        return o
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(conv(obj), indent=1))
