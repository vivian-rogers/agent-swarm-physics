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
