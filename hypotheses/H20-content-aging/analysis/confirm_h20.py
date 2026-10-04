"""H20 confirmatory test on the LOCKED HOLDOUT. Written in round 1; NOT RUN.

Refuses to touch holdout data unless BOTH flags are given:
    --confirm --i-understand-this-uses-the-locked-holdout
`--dry-run` runs the identical pipeline on non-holdout stand-ins (no holdout row is read):
    #1 (C1)         -> stand-in #4  (long, regime I, mode C)
    #51 tail (C2)   -> stand-in: #51 days 36-45 as the "tail", fitted on days <= 35
    short holdouts  -> stand-ins #10, #11, #12, #16, #17, #21, #23, #24, #25

The pre-registered rules are in PREREG below and in the card (README.md, "Confirmatory predictions").
Usage:
    uv run python hypotheses/H20-content-aging/analysis/confirm_h20.py --dry-run
    UV_OFFLINE=1 HF_HUB_OFFLINE=1 uv run --with sentence-transformers python \
        hypotheses/H20-content-aging/analysis/confirm_h20.py --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h20lib as L  # noqa: E402
from h20lib import hc  # noqa: E402
import run_periods as RP  # noqa: E402

RP.NULL_KIND = "aniso"   # the confirmatory tests use the calibrated null (Amendment 2)

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

# --------------------------------------------------------------------------------------------------
# Pre-registered rules (fixed 2026-10-03 after exploratory round 1, before any holdout run; see the card)
# --------------------------------------------------------------------------------------------------
PREREG = {
    "written": "2026-10-03 (after exploratory round 1, before any holdout run)",
    "null": "Amendment 2 (stationary swarm model with latent shapes estimated from the data); B = 500",
    "C1": {"period": 1, "stand_in": 4,
           "rule": "#1 (30 days, regime I, the same charity goal as #38): (a) no late slowing: A_late is not significantly > 0 "
                   "(one-sided p >= 0.05); (b) the kickoff relaxation recurs: A_early > 0 with one-sided p < 0.05. "
                   "C1 passes if (a) and (b) hold (interrupted aging, the #38 pattern).",
           "credence": {"a": 0.75, "b": 0.4}},
    "C2": {"period": 51, "train_max_d": 45, "tail_days": [46, 55], "stand_in_train_max_d": 35, "stand_in_tail": [36, 45],
           "rule": "fitted on days <= train_max_d, the M1 (Box-Cox aging) fit predicts the C entries that involve a tail day "
                   "(t_w >= 2) with lower weighted MSE than both the stationary M0 and the free-lag MT "
                   "(the weak late slowing of round 1, mu-hat 0.22, extrapolates)",
           "credence": 0.4},
    "C3": {"periods": hc.CONFIRM_SHORT, "stand_ins": [10, 11, 12, 16, 17, 21, 23, 24, 25],
           "rule": "calibration of the Amendment-2 null on new data: across the short holdout periods the robust SD "
                   "(1.4826 MAD) of z = (A - null mean)/null SD is <= 1.5; the RE mean of A_early is reported with I^2",
           "credence": 0.6},
}
CONF_DIR = hc.OUT / "confirm"


def build_period_shared(g: int, allow_holdout: bool, max_d: int | None = None) -> L.Period:
    """Build a Period from the SHARED tables (the H20 processed folder has no holdout rows)."""
    st = pl.read_parquet(hc.ED / "statements.parquet")
    st = st.filter((pl.col("goal_no") == g) & (pl.col("agent") != hc.CLAUDE_CODE_AGENT))
    if not allow_holdout:
        st = st.filter(~pl.col("holdout"))
        hc.assert_not_holdout(st["goal_no"].to_list(), st["pt_date"].to_list())
    days = pl.read_parquet(hc.OUT / "days.parquet")
    st = st.join(days.select("goal_no", "pt_date", "d", "d_cal"), on=["goal_no", "pt_date"], how="inner").sort("t")
    if max_d is not None:
        st = st.filter(pl.col("d") <= max_d)
    Ec = np.load(hc.ED / "chat_bge_small.npy", mmap_mode="r")
    Ei = np.load(hc.ED / "intentions_bge_small.npy", mmap_mode="r")
    kind, src, reg = st["kind"].to_numpy(), st["src_row"].to_numpy(), st["regime"].to_numpy()
    Z = np.zeros((st.height, 64), np.float32)
    for r in sorted(set(reg)):
        W = hc.common.load_whitener(r, 64)
        for k, E in (("chat", Ec), ("intent", Ei)):
            s = np.flatnonzero((reg == r) & (kind == k))
            if s.size:
                Z[s] = W(np.asarray(E[src[s]], np.float32))
    stt = st.select("kind", "agent", "t", "pt_date", "goal_no", "regime", "room", "d", "d_cal").with_row_index("row")
    P = L.load_period(g, statements=stt, Z64=Z, days=days, allow_holdout=allow_holdout)
    if P.goal_dirs.get(32, (None, {}))[0] is None and allow_holdout:
        P.goal_dirs = goal_dirs_by_embedding(g, P)
    return P


def goal_dirs_by_embedding(g: int, P: L.Period) -> dict:
    """ĝ for a holdout goal (not in H01's table): embed the goal text + kickoff (H01's rule) with bge-small, offline.
    Text is held in memory only."""
    from sentence_transformers import SentenceTransformer
    goals = {x["goal_no"]: x for x in hc.common.load_goals()}
    cal = pl.read_parquet(hc.SH / "calendar.parquet").filter(pl.col("goal_no") == g).sort("pt_date")
    d0, ws = cal["pt_date"][0], cal["win_start"][0]
    cc = pl.read_parquet(hc.SH / "chat_core.parquet").filter((pl.col("speaker_kind") == "human") & (pl.col("pt_date") == d0)
                                                               & (pl.col("length") >= 250))
    k = cc.filter((pl.col("t") >= ws - pl.duration(minutes=10)) & (pl.col("t") <= ws + pl.duration(minutes=45)))
    if k.height == 0:
        k = cc.sort("length", descending=True).head(1)
    txt = pl.read_parquet(hc.SH / "chat_text.parquet", columns=["message_id", "text"]).join(k.select("message_id"), on="message_id")
    m = SentenceTransformer("BAAI/bge-small-en-v1.5", device="cpu")
    eg = m.encode([goals[g]["goal"]], normalize_embeddings=True)
    ek = m.encode(txt["text"].to_list(), normalize_embeddings=True) if txt.height else None
    out = {}
    for n in (16, 32, 64):
        W = hc.common.load_whitener(P.regime, n)
        parts = [L._unit(W(eg)[0])]
        if ek is not None:
            parts.append(L._unit(np.mean([L._unit(x) for x in W(ek)], axis=0)))
        out[n] = (L._unit(np.sum(parts, axis=0)), {})
    return out


def test_C1(P: L.Period, rng):
    xbar, v, n, valid = L.states(P, "raw", 32)
    main, *_ = RP.null_test(xbar, v, n, valid, P.wk_gap, P.T, rng, 500, stable=L.stable_subset(valid))
    st = main["stats"]
    a = not (st["A_late"]["obs"] > 0 and st["A_late"]["p_upper"] < 0.05)
    b = st["A_early"]["obs"] > 0 and st["A_early"]["p_upper"] < 0.05
    return dict(A=st["A"], A_early=st["A_early"], A_late=st["A_late"], K=st["K"], A_c=st["A_c"],
                a_no_late_slowing=bool(a), b_kickoff_relaxation=bool(b), passed=bool(a and b))


def test_C2(P: L.Period, train_max_d: int, tail: list, rng):
    xbar, v, n, valid = L.states(P, "raw", 32)
    C, npair = L.two_time(xbar, v, valid)
    E = L.entries(C, npair, P.wk_gap, tw_min=2)
    tr = E["d2"] + 1 <= train_max_d
    te = (E["d2"] + 1 >= tail[0]) & (E["d2"] + 1 <= tail[1])
    Etr = {k: x[tr] for k, x in E.items()}
    Ete = {k: x[te] for k, x in E.items()}
    mse = {}
    for m in ("M0", "M0b", "M1"):
        p, _ = L.fit_model(m, Etr)
        mse[m] = float(np.average((L.predict(m, p, Ete) - Ete["c"]) ** 2, weights=Ete["w"]))
        if m == "M1":
            mse["mu_hat_train"] = float(p[3])
    tab = L.model_toeplitz_fit(Etr)
    glob = np.average(Etr["c"], weights=Etr["w"])
    pr = np.array([tab.get(Lg, glob) for Lg in Ete["lag"]])
    mse["MT"] = float(np.average((pr - Ete["c"]) ** 2, weights=Ete["w"]))
    main, *_ = RP.null_test(xbar, v, n, valid, P.wk_gap, P.T, rng, 500, with_derived=False)
    A = main["stats"]["A"]
    passed = (mse["M1"] < mse["M0"]) and (mse["M1"] < mse["MT"]) and A["obs"] > 0 and A["p_upper"] < 0.05
    return dict(mse=mse, n_test_entries=int(te.sum()), A_all_days=A, passed=bool(passed))


def test_C3(periods, builder, rng):
    rows = []
    for g in periods:
        P = builder(g)
        xbar, v, n, valid = L.states(P, "raw", 32)
        main, *_ = RP.null_test(xbar, v, n, valid, P.wk_gap, P.T, rng, 500, with_derived=False)
        s = main["stats"]
        z = (s["A"]["obs"] - s["A"]["null_mean"]) / s["A"]["null_sd"] if s["A"]["null_sd"] else np.nan
        rows.append(dict(goal_no=g, A=s["A"]["obs"], z=z, A_early=s["A_early"]["obs"], se=s["A_early"]["null_sd"]))
    z = np.array([r["z"] for r in rows if np.isfinite(r["z"])])
    rsd = float(1.4826 * np.median(np.abs(z - np.median(z)))) if z.size else np.nan
    re = L.dersimonian_laird([r["A_early"] for r in rows], [r["se"] for r in rows])
    return dict(per_period=rows, z_robust_sd=rsd, re_A_early=re, passed=bool(np.isfinite(rsd) and rsd <= 1.5))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.confirm and args.dry_run:
        sys.exit("choose --dry-run or --confirm, not both")
    if not args.dry_run and not (args.confirm and args.ack):
        sys.exit("Refusing to run: this script uses the LOCKED HOLDOUT. Pass --dry-run for the non-holdout stand-ins, or "
                 "--confirm --i-understand-this-uses-the-locked-holdout once the pre-registration is signed off.")
    holdout = not args.dry_run
    rng = np.random.default_rng(hc.SEED + 999)
    t0 = time.time()
    out = {"mode": "CONFIRM (holdout)" if holdout else "dry-run (non-holdout stand-ins)", "prereg": PREREG}
    if holdout:
        b = lambda g, max_d=None: build_period_shared(g, allow_holdout=True, max_d=max_d)  # noqa: E731
        out["C1"] = test_C1(b(PREREG["C1"]["period"]), rng)
        out["C2"] = test_C2(b(51), PREREG["C2"]["train_max_d"], PREREG["C2"]["tail_days"], rng)
        out["C3"] = test_C3(PREREG["C3"]["periods"], b, rng)
    else:
        b = lambda g, max_d=None: build_period_shared(g, allow_holdout=False, max_d=max_d)  # noqa: E731
        out["C1"] = test_C1(b(PREREG["C1"]["stand_in"]), rng)
        out["C2"] = test_C2(b(51), PREREG["C2"]["stand_in_train_max_d"], PREREG["C2"]["stand_in_tail"], rng)
        out["C3"] = test_C3(PREREG["C3"]["stand_ins"], b, rng)
    out["runtime_s"] = round(time.time() - t0, 1)
    CONF_DIR.mkdir(parents=True, exist_ok=True)
    fn = CONF_DIR / ("confirm_result.json" if holdout else "dry_run_result.json")
    fn.write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps({k: (v.get("passed") if isinstance(v, dict) else v) for k, v in out.items() if k != "prereg"}, indent=1))
    print(f"written {fn}")


if __name__ == "__main__":
    main()
