"""H43 period-native tests (role `native`; predictions P6-P9 in the card, written before these runs).

  NE43  #51 before (days < 2026-08-21) vs after (08-21 .. 09-04): nudge spacing curve before (P6a); swarm-level
        prediction of the nudger-off change in sustained escape per idle minute, refractory vs additive accounting
        (P6b); mention (A, O2) curve invariance across the switch (P7). Exception (c): the transition is the object.
  G38   pause gates: directed kicks (D = nudge, named human message, @-mention) read at a gate after an effective
        directed primer whose launched episode has ended (status post, delta <= 120 min) vs fresh gates (P8, A3);
        batched directed dose at the gate.
  G04   human-message trains in a human-driven regime-I period (units 4a, 4c), 5-min quiet rule (A2), busy-recipient
        outcomes O2 and O2c (P9 as amended).

Usage:  uv run python hypotheses/H43-kick-refractory-window/analysis/run_native.py --test NE43|G38|G04 [--B 300]
Output: data/processed/H43-kick-refractory-window/native/<test>.json
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h43lib as L  # noqa: E402

NE43 = "2026-08-21"
NAT = L.OUT / "native"


def prep(goal_no, **kw):
    calls, states, writes, cal = L.load_real(goal_no, **kw)
    return L.Prep(calls, states, writes, cal), calls, states


def delta_mask(D, lo, hi):
    return (D["d_t"] > lo) & (D["d_t"] <= hi)


# ----------------------------------------------------------------------------- NE43

def escape_rate(P: L.Prep, states: pl.DataFrame, days: list[str], o: str = "O1") -> dict:
    """Escapes from idle (O1: sustained run starts; O1a: any active call) at idle-at-read calls, per idle agent-minute
    (behavior-state idle minutes), per day."""
    rs3 = (np.isin(P.gt, P.rs3_key) if o == "O1" else P.active) & P.idle_at_read
    esc_day = np.bincount(P.day[rs3], minlength=len(P.days)).astype(float)
    idle = (states.filter(pl.col("present") & pl.col("in_span") & (pl.col("lump4_min") == 2))
            .group_by("pt_date").len())
    im = {r[0]: r[1] for r in idle.iter_rows()}
    idle_day = np.array([im.get(d, 0) for d in P.days], float)
    sel = np.array([d in days for d in P.days])
    return {"esc_day": esc_day[sel], "idle_day": idle_day[sel], "days": [d for d in P.days if d in days]}


def nudge_receipts(P: L.Prep):
    """All nudge receipts at idle-at-read calls with spacing to the previous nudge receipt (same agent-day)."""
    idx = np.flatnonzero((P.k["N"] > 0) & P.has_prev & ~P.first_of_day)
    prev = np.full(len(idx), np.inf)
    kk, kt = P.kick_key["N"], P.kick_t["N"]
    j = np.searchsorted(kk, P.gt[idx], "left") - 1
    ok = j >= 0
    same = np.zeros(len(idx), bool)
    same[ok] = np.floor(kk[j[ok]] / 1e7) == np.floor(P.gt[idx][ok] / 1e7)
    prev[ok & same] = (P.t[idx][ok & same] - kt[j[ok & same]]) / 60.0
    return idx, prev


def swarm_block(Ppre, Ppost, spre, spost, Cpre, rng, B, o):
    """P6b: predicted vs observed nudger-off change in escapes per idle minute (outcome o: O1 sustained, O1a any)."""
    D = L.build_design(Ppre, "N")
    e1 = L.e1_table(Ppre, D, o, Cpre)
    e1_rd = e1["summary"]["F_kick"] - e1["summary"]["F_ctrl"]
    idx, prev = nudge_receipts(Ppre)
    idle_rx = Ppre.idle_at_read[idx]
    rd_by_range = {}
    for lab, lo, hi in (("0-15", 0, 15), ("15-60", 15, 60), ("60-240", 60, 240)):
        r, _ = L.ratio_for(Ppre, D, o, delta_mask(D, lo, hi), e1, Cpre) if "sec" in D else ({"n": 0}, None)
        rd_by_range[lab] = (r.get("F_kick", np.nan) - r.get("F_ctrl", np.nan)) if r.get("n", 0) >= 10 else np.nan
    contrib_add = np.where(idle_rx, e1_rd, 0.0)
    contrib_ref = np.zeros(len(idx))
    for i, (ir, d) in enumerate(zip(idle_rx, prev)):
        if not ir:
            continue
        if not np.isfinite(d) or d > 240:          # no nudge in the previous 4 h: a fresh kick
            contrib_ref[i] = e1_rd
        else:                                        # a re-fire: the observed second-kick excess for its spacing
            lab = "0-15" if d <= 15 else ("15-60" if d <= 60 else "60-240")
            v = rd_by_range.get(lab, np.nan)
            contrib_ref[i] = v if np.isfinite(v) else e1_rd
    k = len(Ppost.days)
    pre_win = Ppre.days[-k:]
    pw = escape_rate(Ppre, spre, pre_win, o)
    post_rate = escape_rate(Ppost, spost, Ppost.days, o)
    esc_pre_win = pw["esc_day"].sum()
    rate_pre = pw["esc_day"].sum() / pw["idle_day"].sum()
    rate_post = post_rate["esc_day"].sum() / post_rate["idle_day"].sum()
    obs = rate_post / rate_pre - 1
    bo = []
    for _ in range(B):
        a_ = rng.integers(len(pw["esc_day"]), size=len(pw["esc_day"]))
        b_ = rng.integers(len(post_rate["esc_day"]), size=len(post_rate["esc_day"]))
        bo.append((post_rate["esc_day"][b_].sum() / post_rate["idle_day"][b_].sum())
                  / (pw["esc_day"][a_].sum() / pw["idle_day"][a_].sum()) - 1)
    in_win = np.isin(np.array(Ppre.pt_date)[idx], pre_win)
    pred_add = -contrib_add[in_win].sum() / esc_pre_win
    pred_ref = -contrib_ref[in_win].sum() / esc_pre_win
    allp = escape_rate(Ppre, spre, Ppre.days, o)
    plac = []
    for s_ in range(k, len(Ppre.days) - k + 1):
        e0, i0 = allp["esc_day"][s_ - k:s_].sum(), allp["idle_day"][s_ - k:s_].sum()
        e1_, i1 = allp["esc_day"][s_:s_ + k].sum(), allp["idle_day"][s_:s_ + k].sum()
        if i0 > 0 and i1 > 0:
            plac.append((e1_ / i1) / (e0 / i0) - 1)
    plac = np.array(plac)
    return {
        "outcome": o, "window_days": k, "pre_window": pre_win, "rate_pre_per_idle_min": rate_pre,
        "rate_post_per_idle_min": rate_post, "observed_rel_change": obs,
        "observed_ci": [float(np.percentile(bo, 2.5)), float(np.percentile(bo, 97.5))],
        "n_nudge_receipts_pre_window": int(in_win.sum()), "n_idle_receipts_pre_window": int((in_win & idle_rx).sum()),
        "escapes_pre_window": float(esc_pre_win), "E1_rd": e1_rd, "rd_by_range": rd_by_range,
        "pred_additive_rel": pred_add, "pred_refractory_rel": pred_ref,
        "placebo_rel_changes": {"n": len(plac), "p2.5": float(np.percentile(plac, 2.5)) if len(plac) else None,
                                "p97.5": float(np.percentile(plac, 97.5)) if len(plac) else None,
                                "sd": float(np.std(plac)) if len(plac) else None},
        "closer": "refractory" if abs(obs - pred_ref) < abs(obs - pred_add) else "additive",
        "share_of_observed_explained_refractory": pred_ref / obs if obs != 0 else None,
        "share_of_observed_explained_additive": pred_add / obs if obs != 0 else None}


def run_ne43(B: int) -> dict:
    out = {"test": "NE43", "switch": NE43}
    rng = np.random.default_rng(L.SEED + 4300)
    Ppre, cpre, spre = prep(51, date_to=NE43)
    Ppost, cpost, spost = prep(51, date_from=NE43)
    Cpre = L.day_draws(len(Ppre.days), B, rng)
    Cpost = L.day_draws(len(Ppost.days), B, rng)
    out["pre_days"], out["post_days"] = Ppre.days, Ppost.days
    # (a) nudge curve before the switch (also mentions/human, both sides)
    res = {}
    for side, P, C in (("pre", Ppre, Cpre), ("post", Ppost, Cpost)):
        res[side] = {cl: L.analyze_class(P, cl, rng, B=B, outcomes=("O1", "O2", "O2c", "O1a"), draws=C)
                     for cl in (("N", "H", "A") if side == "pre" else ("H", "A"))}
    out["classes"] = res
    out["P6a_nudge_pool"] = {o: res["pre"]["N"]["outcomes"][o].get("R_pool") for o in ("O1", "O1a")}
    out["P6a_nudge_E1"] = {o: res["pre"]["N"]["outcomes"][o].get("E1") for o in ("O1", "O1a")}
    out["P6b_swarm"] = {o: swarm_block(Ppre, Ppost, spre, spost, Cpre, rng, B, o) for o in ("O1", "O1a")}
    # (c) invariance of the mention curve on O2 (busy recipients)
    inv = {}
    for lab in ("0-15", "15-60", "60-240"):
        a_ = res["pre"]["A"]["outcomes"]["O2"].get("R_pool", {}).get(lab)
        b_ = res["post"]["A"]["outcomes"]["O2"].get("R_pool", {}).get(lab)
        if a_ and b_:
            inv[lab] = {"R_pre": a_["R"], "R_post": b_["R"], "dR": b_["R"]["est"] - a_["R"]["est"],
                        "n_pre": a_["n"], "n_post": b_["n"],
                        "dR_se": float(np.hypot(a_["R"]["se"] or np.nan, b_["R"]["se"] or np.nan))}
    out["P7_invariance"] = inv
    return out


# ----------------------------------------------------------------------------- G38 gates

def run_g38(B: int) -> dict:
    out = {"test": "G38"}
    rng = np.random.default_rng(L.SEED + 3800)
    P, calls, states = prep(38)
    C = L.day_draws(len(P.days), B, rng)
    gap = calls.sort("agent", "pt_date", "t_call")["gap_c"].to_numpy()
    out["idle_at_read_after_pause_share"] = float(np.isin(gap[P.idle_at_read], [1, 2]).mean())
    res = L.analyze_class(P, "D", rng, B=B, outcomes=("O1", "O1a"), draws=C)
    out["D"] = res
    D = L.build_design(P, "D")
    for o in ("O1", "O1a"):
        e1 = L.e1_table(P, D, o, C)
        blk = {"E1_fresh_gates": e1["summary"]}
        if "sec" in D:
            post = (D["st_t"] == L.STATUS["post"]) & (D["d_t"] <= 120)
            blk["P8_post_episode_gates"], _ = L.ratio_for(P, D, o, post, e1, C)
            noeff = (D["st_t"] == L.STATUS["noeff"]) & (D["d_t"] <= 120)
            blk["noeff_gates"], _ = L.ratio_for(P, D, o, noeff, e1, C)
        blk["P8_batched"] = res["outcomes"][o].get("batched")
        out[o] = blk
    # nudges only and mentions only at gates, for reference
    out["N_at_gates"] = L.analyze_class(P, "N", rng, B=B, outcomes=("O1", "O1a"), draws=C)["outcomes"]
    out["A_at_gates"] = L.analyze_class(P, "A", rng, B=B, outcomes=("O1", "O1a"), draws=C)["outcomes"]
    return out


# ----------------------------------------------------------------------------- G04 human trains

def run_g04(B: int) -> dict:
    out = {"test": "G04", "quiet_min": 5, "units": ["4a", "4c"]}
    rng = np.random.default_rng(L.SEED + 400)
    P, calls, states = prep(4, units=["4a", "4c"])
    C = L.day_draws(len(P.days), B, rng)
    out["chat_mode_share"] = float((calls["ctx_mode"] == "chat").mean())
    res = L.analyze_class(P, "H", rng, B=B, outcomes=("O2", "O2c"), draws=C, quiet_s=300)
    out["H"] = res
    D = L.build_design(P, "H", quiet_s=300)
    p9 = {}
    for o in ("O2", "O2c"):
        e1 = L.e1_table(P, D, o, C)
        r_short, _ = L.ratio_for(P, D, o, delta_mask(D, 0, 2), e1, C)
        r_mid, _ = L.ratio_for(P, D, o, delta_mask(D, 5, 30), e1, C)
        r_25, _ = L.ratio_for(P, D, o, delta_mask(D, 2, 5), e1, C)
        p9[o] = {"E1": e1["summary"], "R_0_2": r_short, "R_2_5": r_25, "R_5_30": r_mid}
    out["P9"] = p9
    out["A_reference"] = L.analyze_class(P, "A", rng, B=B, outcomes=("O2", "O2c"), draws=C, quiet_s=300)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", required=True, choices=["NE43", "G38", "G04"])
    ap.add_argument("--B", type=int, default=L.B_BOOT)
    a = ap.parse_args()
    t0 = time.time()
    res = {"NE43": run_ne43, "G38": run_g38, "G04": run_g04}[a.test](a.B)
    res["secs"] = round(time.time() - t0, 1)
    res["git_commit"] = L.git_commit()
    res["built_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    L.jdump(res, NAT / f"{a.test}.json")
    print(a.test, "done", res["secs"], "s")


if __name__ == "__main__":
    main()
