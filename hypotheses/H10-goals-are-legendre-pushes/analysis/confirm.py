"""H10 CONFIRMATORY test on the locked holdout: #22b -> #23 and #31a -> #32. WRITTEN, NOT RUN.

The confirmatory predictions and verdict rules are in the card (README.md, "Confirmatory test"). This script is the
only H10 code that may read held-out statements, and only with both flags:

    uv run --with sentence-transformers python confirm.py --confirm --i-understand-this-uses-the-locked-holdout

    uv run --with sentence-transformers python confirm.py --dry-run
        runs the identical pipeline (built from the shared tables, goal and kickoff texts embedded on the fly) on
        non-holdout stand-ins (#16 -> #17 for C1, #11 -> #12a for C2) and refuses to touch any held-out row.

Pairs (pre-registered):
  C1  F = #22b, 2025-12-10 .. 12-12 (after NE08, goal in prompt; same scaffold as #23)   A = #23 days 2+, 12-16 .. 12-19
  C2  F = #31a, 2026-02-16 .. 02-19 (before the 100-turn cap)                             A = #32 days 2+, 02-24 .. 02-27
      (A spans 02-25: rooms added but no pair separated (H05), and the operator's format reset NE35; variant A = 02-24)
Outputs: data/processed/H10-goals-are-legendre-pushes/confirm/ (or confirm_dryrun/).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys

import numpy as np
import polars as pl

from h10data import DATA, ROOT, SH, save_json
from h10lib import (aggregate, analyze_pair, perm_p_r, random_transverse, stouffer, verdict_P1, verdict_P2, verdict_P3,
                    verdict_P4, verdict_pair)

sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(ROOT / "hypotheses/H10-goals-are-legendre-pushes/scheme"))
from common import REVISION, git_commit, load_holdout, load_whitener  # noqa: E402

EMB = SH / "embeddings"
CONFIRM = {
    "C1": {"F": 22, "F_days": ("2025-12-10", "2025-12-12"), "A": 23, "A_days": ("2025-12-16", "2025-12-19"), "regime": "I"},
    "C2": {"F": 31, "F_days": ("2026-02-16", "2026-02-19"), "A": 32, "A_days": ("2026-02-24", "2026-02-27"), "regime": "I",
           "variant_A_days": ("2026-02-24", "2026-02-24")},
}
STANDIN = {
    "C1": {"F": 16, "F_days": ("2025-10-06", "2025-10-10"), "A": 17, "A_days": ("2025-10-14", "2025-10-17"), "regime": "I"},
    "C2": {"F": 11, "F_days": ("2025-08-25", "2025-08-29"), "A": 12, "A_days": ("2025-09-02", "2025-09-04"), "regime": "I",
           "variant_A_days": ("2025-09-02", "2025-09-02")},
}
ALLOWED_HOLDOUT = {22, 23, 31, 32}


def load_shared_statements(goal, days, allow_holdout: bool):
    st = pl.read_parquet(EMB / "statements.parquet").with_row_index("emb_row")
    cc = pl.read_parquet(SH / "roster.parquet").filter(pl.col("claude_code"))["agent"].to_list()
    s = st.filter((pl.col("goal_no") == goal) & (pl.col("pt_date") >= days[0]) & (pl.col("pt_date") <= days[1])
                  & pl.col("win30").is_not_null() & ~pl.col("agent").is_in(cc))
    if s["holdout"].any() and not allow_holdout:
        raise SystemExit(f"refusing: #{goal} {days} contains held-out rows (use --confirm with the acknowledgement flag)")
    return s


def vectors(s, regime, n=32):
    Ec = np.load(EMB / "chat_bge_small.npy", mmap_mode="r")
    Ei = np.load(EMB / "intentions_bge_small.npy", mmap_mode="r")
    W = load_whitener(regime, n)
    kind, src = s["kind"].to_numpy(), s["src_row"].to_numpy()
    X = np.zeros((s.height, n))
    for k, E in (("chat", Ec), ("intent", Ei)):
        sel = np.flatnonzero(kind == k)
        if len(sel):
            order = np.argsort(src[sel])
            raw = np.asarray(E[src[sel][order]], dtype=np.float32)
            X[sel[order]] = W(raw)
    return X / np.linalg.norm(X, axis=1, keepdims=True)


def goal_vector(goal, regime, allow_holdout: bool, n=32):
    """g = unit(unit(W goal) + unit(W kickoff)), same rule as scheme/build.py; texts in memory only."""
    import build  # scheme/build.py
    cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("goal_no") == goal).sort("pt_date")
    if cal["holdout"].any() and not allow_holdout:
        raise SystemExit(f"refusing: goal #{goal} kickoff lies in the holdout")
    meta, gtext, ktext = goal_texts_any(goal, build)
    G, K = build.embed(gtext, ktext)
    W = load_whitener(regime, n)
    gv = W(G[0][None])[0]; gv /= np.linalg.norm(gv)
    if not np.isfinite(K[0]).all():
        return gv, meta
    kv = W(K[0][None])[0]; kv /= np.linalg.norm(kv)
    v = gv + kv
    return v / np.linalg.norm(v), meta


def goal_texts_any(goal, build):
    """build.goal_texts restricted to non-holdout days; here the first active day of the goal regardless of holdout."""
    from common import load_goals
    goals = {g["goal_no"]: g for g in load_goals()}
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "win_start", "goal_no"]).filter(pl.col("goal_no") == goal).sort("pt_date")
    d0, ws = cal["pt_date"][0], cal["win_start"][0]
    cc = (pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "pt_date", "speaker_kind", "length"])
          .filter((pl.col("speaker_kind") == "human") & (pl.col("pt_date") == d0) & (pl.col("length") >= 250)))
    k = cc.filter((pl.col("t") >= ws - dt.timedelta(minutes=10)) & (pl.col("t") <= ws + dt.timedelta(minutes=45)))
    if k.height == 0:
        k = cc.sort("length", descending=True).head(1)
    ct = pl.read_parquet(SH / "chat_text.parquet", columns=["message_id", "text"])
    k = k.join(ct, on="message_id").sort("t")
    body = " ".join(build.strip_boilerplate(x) for x in k["text"].to_list())
    return {"goal_no": goal, "first_day": d0, "n_kick_msgs": k.height}, [goals[goal]["goal"]], [build.chunks(body)]


def segment_for(goal, days, regime, U, allow_holdout):
    s = load_shared_statements(goal, days, allow_holdout)
    X = vectors(s, regime, U.shape[0])
    dl = sorted(s["pt_date"].unique().to_list())
    dmap = {d: i for i, d in enumerate(dl)}
    day = np.array([dmap[d] for d in s["pt_date"].to_list()])
    return aggregate(X, s["agent"].to_numpy().astype(int), day, day * 1000 + s["win30"].to_numpy().astype(int), U,
                     {"goal": goal, "days": dl})


def eps_max():
    return float(json.loads((DATA / "synthetic_summary.json").read_text()).get("eps_max_P2", 1.0))


def run(spec, allow_holdout, rng, n_boot):
    out = {}
    for key, cfg in spec.items():
        g, meta = goal_vector(cfg["A"], cfg["regime"], allow_holdout)
        U = random_transverse(g, 50, np.random.default_rng(0))
        F = segment_for(cfg["F"], cfg["F_days"], cfg["regime"], U, allow_holdout)
        variants = {"primary": cfg["A_days"]}
        if "variant_A_days" in cfg:
            variants["A_variant"] = cfg["variant_A_days"]
        for vname, adays in variants.items():
            A = segment_for(cfg["A"], adays, cfg["regime"], U, allow_holdout)
            r = analyze_pair(F, A, rng, n_boot=n_boot, n_rot=2000)
            r["v1"] = verdict_P1(r["P1_r"], r["P1_p"], r["P1_mse_tilt"], r["P1_mse_trans"])
            r["v2"] = (verdict_P2(r["P2_rho"], r.get("P2_rho_ci90", [np.nan, np.nan])) if abs(r["eps"]) <= eps_max()
                       else f"n/a (non-perturbative, eps = {r['eps']:.2f})")
            r["v3"] = verdict_P3(r.get("dg", np.nan), r.get("dg_ci90", [np.nan, np.nan]))
            r["v4"] = verdict_P4(r.get("P4_D", np.nan), r.get("P4_D_ci90", [np.nan, np.nan]), r.get("P4_cos_Cg", np.nan),
                                 r.get("P4_rot_p95", np.nan))
            r["v"] = verdict_pair(r["v1"], r["v2"], r["v3"], r["v4"])
            r["goal_meta"] = meta
            out[f"{key}:{vname}"] = r
            print(key, vname, f"N={r['N']} Dbar={r['Dbar']:.4f} eps={r['eps']:.2f} P1 r={r['P1_r']:.2f} p={r['P1_p']:.3f} "
                  f"rho={r['P2_rho']:.2f} dg={r.get('dg', np.nan):.2f} D={r.get('P4_D', np.nan):.3f} -> "
                  f"{r['v1']} / {r['v2']} / {r['v3']} / {r['v4']}", flush=True)
    prim = [out[f"{k}:primary"] for k in spec]
    # Confirmatory rules (card, "Confirmatory test", written 2026-10-03 after exploration, before any holdout run):
    #  CH10  the hypothesis as stated: P1 r > 0 in both pairs AND Stouffer(one-sided p for r > 0) < 0.05
    #  CX1   the exploratory counter-finding (anti-FDT): Stouffer(one-sided p for r < 0) < 0.05
    #  CX2   field-specific dispersal: ln(var_A / var_F) along g > ln 1.5 in both pairs AND |rho_perp| < ln 1.5 in both
    #  CX3   the push exists: Dbar > 0 in both pairs (90% CI above 0)
    #  P2    tilt variance verdict only if eps <= eps_max (expected n/a)
    p_neg = [perm_p_r(np.array(r["P1_k2F"]), -np.array(r["P1_D"]), np.random.default_rng(1))[1] for r in prim]
    comb = {"CH10": bool(all(r["P1_r"] > 0 for r in prim) and stouffer([r["P1_p"] for r in prim]) < 0.05),
            "CH10_stouffer_p": stouffer([r["P1_p"] for r in prim]),
            "CX1": bool(stouffer(p_neg) < 0.05), "CX1_stouffer_p": stouffer(p_neg),
            "CX2": bool(all(r["P2_rho_gauss"] > np.log(1.5) for r in prim) and all(abs(r["P2_rho_perp"]) < np.log(1.5) for r in prim)),
            "CX2_values": [(r["P2_rho_gauss"], r["P2_rho_perp"]) for r in prim],
            "CX3": bool(all(r.get("Dbar_ci90", [np.nan])[0] > 0 for r in prim)),
            "P2": [r["v2"] for r in prim]}
    return out, comb


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    rng = np.random.default_rng(20261004)
    if a.dry_run and not a.confirm:
        held = set(load_holdout()["goal_periods_held_out"]) | {23}
        if any(c["F"] in held or c["A"] in held for c in STANDIN.values()):
            raise SystemExit("stand-in touches the holdout")
        out, comb = run(STANDIN, allow_holdout=False, rng=rng, n_boot=a.boot)
        dest = DATA / "confirm_dryrun"
    elif a.confirm and a.ack and not a.dry_run:
        touched = {c["F"] for c in CONFIRM.values()} | {c["A"] for c in CONFIRM.values()}
        held = set(load_holdout()["goal_periods_held_out"]) | {23}
        if (touched & held) - ALLOWED_HOLDOUT:
            raise SystemExit(f"refusing: {sorted((touched & held) - ALLOWED_HOLDOUT)} not pre-registered for H10")
        out, comb = run(CONFIRM, allow_holdout=True, rng=rng, n_boot=a.boot)
        dest = DATA / "confirm"
    else:
        raise SystemExit("refusing: pass --dry-run (non-holdout stand-ins) or --confirm "
                         "--i-understand-this-uses-the-locked-holdout")
    print("combined", comb)
    save_json({"pairs": out, "combined": comb, "git_commit": git_commit(), "revision": REVISION,
               "run_at": dt.datetime.now(dt.timezone.utc).isoformat(), "dry_run": bool(a.dry_run)}, dest / "results.json")


if __name__ == "__main__":
    main()
