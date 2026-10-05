"""H16 round 2 library: context composition (Polya urn), urn simulation, reset and kick designs, spell kinds, trap depth.

Used by scheme/build_r2.py (composition tables), analysis/synthetic_r2.py (validation on the real skeleton) and
analysis/run_r2.py (real data, non-reserved days only). Earlier rounds are untouched (h16lib, r1blib unchanged).

Definitions (card, "Round 2"):
  segment        an agent's cu-mode calls between context resets (ctx_pos restarts at 1; regime III; the ledger's
                 first_of_day is not a reset in regime III).
  own repeat     an own idle call (kind pause/wait, not talking) earlier in the segment.
  composition at call c (before c's own output; items read at c are in the context):
     n_rep, n_act  own idle / own active calls earlier in the segment
     k_ctx         room items in the context (ledger, includes c's new items)
     f_tok   (U-tok, primary)  own-repeat share of the prompt in tokens:
                 n_rep*tau_I / (B_L + n_rep*tau_I + n_act*tau_A + R),  R = a_L k + b_L chars + e_L other events
                 (H45 room ruler; tau_I, tau_A, B_L = lab medians of own prompt growth after an idle / active call and of
                 the prompt at ctx_pos 1; labs without action-row tokens use the Anthropic/Google mean)
     f_call  (U-call)  n_rep / (n_rep + n_act)            share of own calls in the segment that are idle
     f_entry (U-entry) n_rep / (n_rep + n_act + k_ctx)    share of context entries (own calls + room items)
     f_rec   (U-rec)   idle calls among the last M = 10 entries (own calls and room items, time order, same segment)
  urn            P(escape at a gate) = c_i (1 - f); per 30-s bin on the wall clock, cloglog h = alpha_i + ln(1 - f).
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
from scipy import special

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H16-metastable-traps-kramers"
R2 = OUT / "r2"
sys.path.insert(0, str(ROOT / "infra/shared"))
import hazard_fe as HF  # noqa: E402

URNS = ("f_tok", "f_call", "f_entry", "f_rec")
M_REC = 10
F_CAP = 0.98                      # 1 - f floor 0.02 so ln(1 - f) stays finite
SEED = 20261005
G51_END = "2026-09-03"            # H16 rule: NE33 batch join (09-03) onward excluded


# ============================================================================ composition
def recency_share(kn: np.ndarray, idle: np.ndarray, seg: np.ndarray, M: int = M_REC) -> np.ndarray:
    """Idle-call share among the last M entries before each call's own entry (entries: each call's new items, then
    the call itself; windows do not cross segment starts). One agent's calls in time order."""
    n = len(kn)
    step = kn.astype(np.int64) + 1
    end_pos = np.cumsum(step)                  # position after call c's entry
    call_pos = end_pos - 1                     # 0-based index of call c's own entry
    pos_c = call_pos                           # window is [pos_c - M, pos_c): includes c's items, excludes c
    seg_start = np.zeros(n, np.int64)
    new = np.r_[True, seg[1:] != seg[:-1]]
    first_idx = np.maximum.accumulate(np.where(new, np.arange(n), 0))
    seg_start = (end_pos - step)[first_idx]    # entry position where the segment starts
    lo = np.maximum(pos_c - M, seg_start)
    idle_pos = call_pos[idle]
    cnt = np.searchsorted(idle_pos, pos_c, "left") - np.searchsorted(idle_pos, lo, "left")
    L = pos_c - lo
    out = np.where(L > 0, cnt / np.maximum(L, 1), np.nan)
    return out


def ruler(calls: pl.DataFrame, cal: dict) -> dict:
    """Lab medians: own prompt growth after an idle / active call (dP minus calibrated room tokens) and P at ctx_pos 1.
    Fitted on Anthropic and Google cu calls (prompt tokens on every call); other labs get their mean."""
    c = calls.filter(pl.col("P").is_not_null()).sort("agent", "t_call", "turn_id")
    c = c.with_columns(dP=pl.col("P") - pl.col("P").shift(1).over("agent", "seg"),
                       prev_idle=pl.col("idle").shift(1).over("agent", "seg"))
    out = {}
    for lab in ("Anthropic", "Google"):
        a, b, e = cal[lab]["a_per_item"], cal[lab]["b_per_char"], cal[lab]["e_per_other_event"]
        d = c.filter((pl.col("lab") == lab) & pl.col("dP").is_not_null() & (pl.col("ctx_pos") > 1))
        d = d.with_columns(own=pl.col("dP") - (a * pl.col("k_new") + b * pl.col("chars_new") + e * pl.col("n_oev")))
        tI = float(d.filter(pl.col("prev_idle"))["own"].median())
        tA = float(d.filter(~pl.col("prev_idle"))["own"].median())
        B = float(c.filter((pl.col("lab") == lab) & (pl.col("ctx_pos") == 1))["P"].median())
        out[lab] = {"tau_I": tI, "tau_A": tA, "B": B, "a": a, "b": b, "e": e,
                    "n_idle": int(d.filter(pl.col("prev_idle")).height), "n_act": int(d.filter(~pl.col("prev_idle")).height)}
    out["other"] = {k: float(np.mean([out["Anthropic"][k], out["Google"][k]])) for k in ("tau_I", "tau_A", "B", "a", "b", "e")}
    return out


def composition(calls: pl.DataFrame, R: dict) -> pl.DataFrame:
    """Per-call composition (see module docstring). `calls`: regime-III cu calls with agent, lab, t_call, turn_id,
    ctx_pos, kind, talk, k_new, chars_new, n_oev, k_ctx (and optional P)."""
    c = calls.sort("agent", "t_call", "turn_id")
    c = c.with_columns(idle=(pl.col("kind").cast(pl.Utf8).is_in(["pause", "wait"]) & ~pl.col("talk")))
    c = c.with_columns(newseg=(pl.col("ctx_pos") == 1) | (pl.col("ctx_pos") <= pl.col("ctx_pos").shift(1).over("agent")).fill_null(True))
    c = c.with_columns(seg=pl.col("newseg").cast(pl.Int32).cum_sum().over("agent"))
    c = c.with_columns(
        n_rep=(pl.col("idle").cast(pl.Int32).cum_sum().over("agent", "seg") - pl.col("idle").cast(pl.Int32)),
        n_act=((~pl.col("idle")).cast(pl.Int32).cum_sum().over("agent", "seg") - (~pl.col("idle")).cast(pl.Int32)),
        chars_seg=pl.col("chars_new").cast(pl.Int64).cum_sum().over("agent", "seg"),
        oev_seg=pl.col("n_oev").cast(pl.Int64).cum_sum().over("agent", "seg"),
        kc=pl.col("k_new").cast(pl.Int64).cum_sum().over("agent", "seg"),
    )
    # recency urn, per agent
    frec = np.full(c.height, np.nan)
    ag = c["agent"].to_numpy(); kn = c["k_new"].to_numpy(); idl = c["idle"].to_numpy(); sg = c["seg"].to_numpy()
    cuts = np.flatnonzero(np.diff(ag)) + 1
    for lo, hi in zip(np.r_[0, cuts], np.r_[cuts, len(ag)]):
        frec[lo:hi] = recency_share(kn[lo:hi], idl[lo:hi], sg[lo:hi])
    c = c.with_columns(pl.Series("f_rec", frec))
    labkey = pl.when(pl.col("lab").is_in(["Anthropic", "Google"])).then(pl.col("lab")).otherwise(pl.lit("other"))
    c = c.with_columns(labkey=labkey)
    par = pl.DataFrame({"labkey": ["Anthropic", "Google", "other"],
                        **{k: [R[l][k] for l in ("Anthropic", "Google", "other")] for k in ("tau_I", "tau_A", "B", "a", "b", "e")}})
    c = c.join(par, on="labkey", how="left")
    c = c.with_columns(Rtok=pl.col("a") * pl.col("kc") + pl.col("b") * pl.col("chars_seg") + pl.col("e") * pl.col("oev_seg"))
    c = c.with_columns(rep_tok=pl.col("n_rep") * pl.col("tau_I"))
    c = c.with_columns(P_hat=pl.col("B") + pl.col("rep_tok") + pl.col("n_act") * pl.col("tau_A") + pl.col("Rtok"))
    c = c.with_columns(
        f_tok=pl.col("rep_tok") / pl.col("P_hat"),
        f_call=pl.when((pl.col("n_rep") + pl.col("n_act")) > 0).then(pl.col("n_rep") / (pl.col("n_rep") + pl.col("n_act"))).otherwise(None),
        f_entry=pl.when((pl.col("n_rep") + pl.col("n_act") + pl.col("kc")) > 0)
        .then(pl.col("n_rep") / (pl.col("n_rep") + pl.col("n_act") + pl.col("kc"))).otherwise(None),
    )
    if "P" in c.columns:
        c = c.with_columns(f_tokP=pl.when(pl.col("P") > 0).then((pl.col("rep_tok") / pl.col("P")).clip(0, 1)).otherwise(None))
    # composition without the call's own new items (for the urn-implied effect of current reads)
    c = c.with_columns(
        Rtok_pre=pl.col("a") * (pl.col("kc") - pl.col("k_new")) + pl.col("b") * (pl.col("chars_seg") - pl.col("chars_new"))
        + pl.col("e") * (pl.col("oev_seg") - pl.col("n_oev")))
    c = c.with_columns(f_tok_pre=pl.col("rep_tok") / (pl.col("B") + pl.col("rep_tok") + pl.col("n_act") * pl.col("tau_A") + pl.col("Rtok_pre")),
                       f_entry_pre=pl.when((pl.col("n_rep") + pl.col("n_act") + pl.col("kc") - pl.col("k_new")) > 0)
                       .then(pl.col("n_rep") / (pl.col("n_rep") + pl.col("n_act") + pl.col("kc") - pl.col("k_new"))).otherwise(None))
    return c.drop("a", "b", "e", "tau_I", "tau_A", "B", "labkey", "newseg")


def lnq(f) -> np.ndarray:
    """ln(1 - f) with the floor 1 - f >= 1 - F_CAP."""
    f = np.asarray(f, float)
    return np.log(np.clip(1.0 - f, 1.0 - F_CAP, 1.0))


# ============================================================================ fits
def fe_logit(y, X, g, link="logit"):
    """Agent-FE binary GLM (profiled FE; h16lib.glm_fe semantics: groups without variation dropped)."""
    sys.path.insert(0, str(HERE))
    import h16lib as L  # noqa: E402
    return L.glm_fe(y, X, g, link)


def day_boot(fn, days: np.ndarray, B: int, rng) -> np.ndarray:
    """Day-block bootstrap of a statistic fn(idx) -> array."""
    rows = HF.rows_per_day(days)
    out = []
    for _ in range(B):
        idx = HF.block_resample(days, rng, rows)
        try:
            out.append(np.atleast_1d(fn(idx)))
        except Exception:  # noqa: BLE001
            continue
    return np.array(out, float)


def pct_ci(a, q=(2.5, 97.5)):
    a = np.asarray(a, float)
    a = a[np.isfinite(a)]
    if len(a) < 10:
        return [float("nan"), float("nan")]
    return [float(np.percentile(a, q[0])), float(np.percentile(a, q[1]))]


# ============================================================================ urn simulation
def urn_prob(f, agent, level=0.5):
    """Gate escape probability c (1 - f) with one constant c chosen so that the mean is `level` (outcome-free)."""
    q = np.clip(1.0 - np.asarray(f, float), 1.0 - F_CAP, 1.0)
    c = min(level / q.mean(), 1.0 / q.max())
    return np.clip(c * q, 1e-4, 1 - 1e-4)


def simulate_gate(rng, p):
    return (rng.random(len(p)) < p).astype(np.int8)


def simulate_bins(rng, f, agent, alpha_sd=0.5, level=0.02):
    """Per-bin cloglog escape: alpha_i + ln(1 - f), alpha_i ~ N(ln(level), alpha_sd) per agent (absorbed by agent FE)."""
    ua = np.unique(agent)
    al = dict(zip(ua, np.log(level) + alpha_sd * rng.standard_normal(len(ua))))
    eta = np.array([al[a] for a in agent]) + lnq(f)
    h = -np.expm1(-np.exp(np.clip(eta, -30, 3)))
    return (rng.random(len(h)) < h).astype(np.int8)


# ============================================================================ helpers
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


def expit(x):
    return special.expit(x)


# ============================================================================ gate design and estimators (R1, R2)
def prep_gates(g: pl.DataFrame) -> pl.DataFrame:
    """At-risk gate rows with derived covariates: trap id, reset flags, urn-implied jump and kick terms."""
    g = g.filter(pl.col("y_sus").is_not_null() & pl.col("a_sus").is_not_null()).sort("agent", "t_call", "turn_id")
    g = g.with_columns(trap=(pl.col("k_sus") == 1).cast(pl.Int32).cum_sum().over("agent", "pt_date"))
    # composition at the end of the old segment (the idle call before the gate included)
    fprev_call = ((pl.col("n_rep_prev") + 1) / (pl.col("n_rep_prev") + pl.col("n_act_prev") + 1))
    g = g.with_columns(
        forced=(pl.col("reset_at_gate") & pl.col("reset_forced")).fill_null(False),
        vol=(pl.col("reset_at_gate") & ~pl.col("reset_forced").fill_null(False)).fill_null(False),
        f_call_end=fprev_call, f_tok_end=pl.col("f_tok_prev"))
    g = g.with_columns(
        du_call=pl.when(pl.col("forced")).then(-(1 - pl.col("f_call_end").clip(0, F_CAP)).log()).otherwise(0.0),
        du_tok=pl.when(pl.col("forced")).then(-(1 - pl.col("f_tok_end").clip(0, F_CAP)).log()).otherwise(0.0),
        dir1=(pl.col("n_dir") > 0), undir1=((pl.col("n_novel") > 0) & (pl.col("n_dir") == 0)),
        dir_n=pl.col("n_dir").clip(0, 2))
    # urn-implied effect of the items read at the gate: ln(1 - f_with) - ln(1 - f_without)
    g = g.with_columns(
        dk_tok=((1 - pl.col("f_tok").clip(0, F_CAP)).log() - (1 - pl.col("f_tok_pre").clip(0, F_CAP)).log()).fill_null(0.0),
        dk_entry=((1 - pl.col("f_entry").clip(0, F_CAP)).log() - (1 - pl.col("f_entry_pre").clip(0, F_CAP)).log()).fill_null(0.0))
    return g


def nuisance(g: pl.DataFrame) -> np.ndarray:
    la = np.log(np.maximum(g["a_sus"].to_numpy(), 10.0) / 60.0)
    pp = np.log(np.clip(g["prev_pause_s"].fill_null(300.0).to_numpy(), 10.0, 86400.0))
    hd = np.clip(g["h_day"].to_numpy(), 0, 12)
    sw = g["swarm_act10"].fill_null(0.0).to_numpy()
    lr = np.log1p(g["last_run_len"].fill_null(0).to_numpy())
    return np.column_stack([la, pp, hd, sw, lr])


NUIS = ["ln_a", "ln_prev_pause", "h_day", "swarm_act10", "ln_last_run"]


def gate_fit(y, X, agent, names, link="logit"):
    f = fe_logit(y, X, agent, link)
    return {n: (float(b), float(s)) for n, b, s in zip(names, f["beta"], f["se"])}, f


def gate_models(g: pl.DataFrame, y: np.ndarray, urn_cols=("f_tok", "f_call", "f_entry", "f_rec"), parts=("abs", "reset", "kick")) -> dict:
    """All round-2 gate statistics on one outcome vector (real or simulated). Values are [estimate, Wald SE]."""
    X0 = nuisance(g)
    ag = g["agent"].to_numpy()
    out = {}
    c0, _ = gate_fit(y, X0, ag, NUIS)
    out["beta_a0"] = list(c0["ln_a"])
    if "abs" in parts:
        for u in urn_cols:
            f = g[u].to_numpy().astype(float)
            ok = np.isfinite(f)
            c0u, _ = gate_fit(y[ok], X0[ok], ag[ok], NUIS)
            X = np.column_stack([X0[ok], lnq(f[ok])])
            c1, _ = gate_fit(y[ok], X, ag[ok], NUIS + ["lnq"])
            b0, b1 = c0u["ln_a"][0], c1["ln_a"][0]
            out[f"abs_{u}"] = {"beta_a0": list(c0u["ln_a"]), "beta_a": list(c1["ln_a"]), "beta_f": list(c1["lnq"]),
                               "rho": [(1 - b1 / b0) if b0 < 0 else float("nan"), float("nan")]}
    # Amendment R2-A1 (after the synthetic validation, before real data): reset and kick models add ln(gate index k_sus),
    # because a per-trap frailty world fakes a reset step (+0.47, power 0.87) through survivor selection at k = 1.
    X0 = np.column_stack([X0, np.log(g["k_sus"].to_numpy().astype(float))])
    NU = NUIS + ["ln_k"]
    if "reset" in parts:
        fo = g["forced"].to_numpy().astype(float); vo = g["vol"].to_numpy().astype(float)
        X = np.column_stack([X0, fo, vo])
        c2, _ = gate_fit(y, X, ag, NU + ["forced", "vol"])
        out["reset"] = {"forced": list(c2["forced"]), "vol": list(c2["vol"])}
        for d in ("du_call", "du_tok"):
            du = g[d].to_numpy().astype(float)
            mu = du[fo > 0].mean() if fo.sum() else 0.0
            X = np.column_stack([X0, fo, vo, np.where(fo > 0, du - mu, 0.0)])
            c3, _ = gate_fit(y, X, ag, NU + ["forced", "vol", "dose"])
            out["reset"][f"dose_{d}"] = list(c3["dose"])
    if "kick" in parts:
        d1 = g["dir1"].to_numpy().astype(float); u1 = g["undir1"].to_numpy().astype(float)
        X = np.column_stack([X0, d1, u1])
        f4 = fe_logit(y, X, ag)
        i, j = len(NU), len(NU) + 1
        dse = float(np.sqrt(max(f4["cov"][i, i] + f4["cov"][j, j] - 2 * f4["cov"][i, j], 0)))
        out["kick"] = {"dir": [float(f4["beta"][i]), float(f4["se"][i])], "undir": [float(f4["beta"][j]), float(f4["se"][j])],
                       "diff": [float(f4["beta"][i] - f4["beta"][j]), dse]}
        for dk in ("dk_tok", "dk_entry"):
            z = g[dk].to_numpy().astype(float)
            X = np.column_stack([X0, d1, u1, z])
            c5, _ = gate_fit(y, X, ag, NU + ["dir", "undir", "dk"])
            out["kick"][f"coef_{dk}"] = list(c5["dk"])
            out["kick"][f"mean_{dk}_dir"] = [float(z[d1 > 0].mean()) if d1.sum() else float("nan"), float("nan")]
        dn = g["dir_n"].to_numpy()
        X = np.column_stack([X0, (dn == 1).astype(float), (dn >= 2).astype(float), u1])
        c6, _ = gate_fit(y, X, ag, NU + ["dir1", "dir2p", "undir"])
        out["kick"]["dose1"] = list(c6["dir1"]); out["kick"]["dose2p"] = list(c6["dir2p"])
    return out


def flat(d: dict, pre="") -> dict:
    o = {}
    for k, v in d.items():
        if isinstance(v, dict):
            o.update(flat(v, f"{pre}{k}."))
        else:
            o[f"{pre}{k}"] = v
    return o


# ============================================================================ sequential gate simulation
def trap_index(g: pl.DataFrame):
    """Row ranges of each trap (rows sorted by agent, t_call; trap = run starting at k_sus == 1)."""
    a = g["agent"].to_numpy(); d = np.array(g["pt_date"].to_list()); tr = g["trap"].to_numpy()
    brk = (a[1:] != a[:-1]) | (d[1:] != d[:-1]) | (tr[1:] != tr[:-1])
    cuts = np.flatnonzero(brk) + 1
    return np.r_[0, cuts], np.r_[cuts, len(a)]


def simulate_traps(rng, p: np.ndarray, starts, ends):
    """Walk each trap: outcome per gate with prob p; stop at the first escape; censor at the real trap end.
    Returns (keep mask, y)."""
    u = rng.random(len(p))
    hit = u < p
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


# ============================================================================ TS1r rows with kinds (mixture rival)
def ts1r_deep(period: str, deep_s=600.0):
    sys.path.insert(0, str(HERE))
    import h16lib as L  # noqa: E402
    k = pl.read_parquet(R2 / "ts1r_kinds.parquet").filter(pl.col("period") == period).filter(pl.col("first_act_s") >= 0)
    k = k.sort("pt_date", "agent", "t0")
    H = L.ts1_hazard_rows(k, None)
    m = H["elapsed"] >= deep_s
    H = {kk: v[m] for kk, v in H.items()}
    H["day"] = np.array(k["pt_date"].to_list())[H["spell"]]
    H["kind_start"] = np.array(k["kind_start"].to_list())[H["spell"]]
    H["last_kind"] = np.array(k["last_kind"].to_list())[H["spell"]]
    H["lnel"] = np.log(H["elapsed"] / 60.0)
    return H


def cell_codes(H, cols=("kind_start", "last_kind")):
    key = np.char.add(H["agent"].astype(str), "|")
    for c in cols:
        key = np.char.add(np.char.add(key, H[c].astype(str)), "|")
    _, code = np.unique(key, return_inverse=True)
    return code


def slope_cloglog(y, x, g):
    f = fe_logit(y, x[:, None], g, "cloglog")
    return float(f["beta"][0]), float(f["se"][0])


def mixture_null(rng, H, y_obs, cells, sims=200):
    """Constant hazard per cell (MLE = events / rows), per-row draws on the real deep skeleton; agent-FE slope each draw."""
    ev = np.bincount(cells, y_obs.astype(float))
    n = np.bincount(cells)
    h = np.clip(ev / np.maximum(n, 1), 1e-6, 1 - 1e-6)[cells]
    out = []
    for _ in range(sims):
        ys = (rng.random(len(h)) < h).astype(np.int8)
        out.append(slope_cloglog(ys, H["lnel"], H["agent"])[0])
    return np.array(out)
