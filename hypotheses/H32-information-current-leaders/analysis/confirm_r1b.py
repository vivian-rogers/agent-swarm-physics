"""H32 confirmatory test on the locked holdout, RE-FROZEN ON ROUND-1B INPUTS (written 2026-10-04; NOT RUN).

Re-freeze of `confirm.py` (left byte-for-byte untouched), written before any look at #14/#22/#28. Details in
`CONFIRM_R1B.md`. Inputs switched (round-1b switches of analysis/ic_core.py, set per run below):
  * exposure: DQ1 ledger call starts (H32_DATA=r1b): i's message is seen by j's message m iff posted in j's room before
    t_call of the call that produced m; same-room messages posted during that call are unread (in flight);
  * content: bge-small (primary, as frozen) AND gte-modernbert (whitened in the period's regime basis, gte goal fields);
    the transfer and identity criteria must hold under both (C1-r1b, C7-r1b);
  * new H57 in-flight placebo C9-r1b: at tau = 60 s (window 3 min) the read term beats the same-age unread term;
  * dedupe (DQ5 statement_flags: cross-echo either model, templated either, self-repeat both) reported for #28.
Activity tables, outages, work and failures are not inputs of H32's estimator.

Targets (unchanged; held out, never examined by H32): #28 (mode C, regime I), #22 (mode F), #14 (mode I). #45 refused.
Ledger (L197-L199): no prior run on these targets; planned same-family users H06, H10, H12, H24, H33, H36 must be
told whoever runs first.

Modes:
  --dry-run (default)  identical pipeline, built from scratch for the non-holdout stand-ins (#30 for #28, #16 for #22,
                       #17 for #14) into --base (default data/processed/H32-information-current-leaders/confirm_r1b_dryrun)
  --confirm --i-understand-this-uses-the-locked-holdout
                       build the three held-out periods into .../confirm_r1b/ (gte vectors and fields included, ledger
                       calls of held-out days included) and evaluate the frozen predictions. Refuses unless this script,
                       CONFIRM_R1B.md, ic_core.py, r1b.py, scheme/build*.py and the card are committed and unmodified,
                       and unless infra/shared/holdout_ledger.check() allows every target.

Usage: uv run python hypotheses/H32-information-current-leaders/analysis/confirm_r1b.py [--dry-run] [--base DIR]
"""
from __future__ import annotations

import os

os.environ["H32_DATA"] = "r1b"
os.environ.pop("H32_EMB", None)
os.environ.pop("H32_S0", None)
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("POLARS_MAX_THREADS", "2")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import json  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import build as B  # noqa: E402
import ic_core as C  # noqa: E402
from common import holdout_mask, load_holdout  # noqa: E402

assert C.R1B
TARGETS = {28: 30, 22: 16, 14: 17}
CARD = HERE.parent / "README.md"
HYP = "H32"
ED = C.ROOT / "data/processed/shared/embeddings"
TAU0 = C.P["tau"]

# Frozen predictions (re-frozen 2026-10-04 on round-1b inputs, before any look at #14/#22/#28).
# Round-1b basis: ledger bge T significant 17/32, gte 23/32; top source agrees across models in 17/32; split-half
# rho > 0 in 20/26; at tau = 60 s read > unread in 17/17 transfer periods (unread ~ 1/3 of read); leaders 0/3 natives.
FROZEN = {
    "C1_r1b_transfer_28": "#28: T > 0 against the cross-day null at p_T < 0.05 under BOTH bge and gte [0.7] "
                          "(was bge only; DQ5 both-model rule)",
    "C2_transfer_IF": "#22 and #14: p_T >= 0.05 in at least one of the two (bge) [0.7]",
    "C3_no_leader": "a leader is called (standout p < 0.05 and max p < 0.05) in at most 1 of the 3 targets (bge) [0.8]",
    "C4_stability_28": "#28 split-half Spearman rho(Out_odd, Out_even) > 0 (bge) [0.7]",
    "C5_mode": "T(#28) > T(#22) and T(#28) > T(#14) (bge) [0.55]",
    "C6_both_nulls_28": "#28 T significant under both N1 and N1w (bge) [0.6]",
    "C7_r1b_identity_28": "#28's top source by Out is Claude Opus 4.5 or GPT-5.2 under BOTH bge and gte [0.3] "
                          "(was bge only; round 1b: top source agrees across models in 17/32)",
    "C8_humans_28": "if #28 has >= 15 human messages: the human pseudo-agent's Out is NOT above the median agent's [0.7]",
    "C9_r1b_read_beats_unread_28": "#28 at tau = 60 s (window 3 min), S0 = unread: T_read > T_unread (bge) [0.8] "
                                   "(new; H57 in-flight placebo, round 1b 17/17)",
    "S_dedupe_28": "reported, not scored: #28 T with deduped targets (bge)",
}


def committed_and_clean(paths) -> bool:
    for p in paths:
        r = subprocess.run(["git", "-C", str(C.ROOT), "status", "--porcelain", "--", str(p)], capture_output=True, text=True)
        if r.stdout.strip():
            return False
        r = subprocess.run(["git", "-C", str(C.ROOT), "ls-files", "--error-unmatch", str(p)], capture_output=True, text=True)
        if r.returncode != 0:
            return False
    return True


def ledger_status(goals) -> list[str]:
    sys.path.insert(0, str(C.ROOT))
    from infra.shared import holdout_ledger as hl
    led = hl.load()
    bad = []
    for g in goals:
        t = f"G{g:02d}"
        fam = sorted({f for e in led["entries"] if e["hypothesis"] == HYP and e["target"] == t for f in e["estimator_family"]})
        r = hl.check(HYP, t, "message content", fam or ["content_alignment"])
        print(f"ledger {t}: allowed={r['allowed']} needs_disclosure={r['needs_disclosure']} "
              f"prior_runs={sorted({u['hypothesis'] for u in r['prior_runs']})} "
              f"competing_planned={sorted({u['hypothesis'] for u in r['competing_planned']})}")
        if not r["allowed"]:
            bad.append(t)
    return bad


def ledger_calls_with_holdout(agents, t0: float, t1: float) -> dict:
    """Confirm path only: ic_core.ledger_calls without its ~holdout filter (held-out days are the target)."""
    cw = (pl.scan_parquet(C.SH / "call_windows.parquet").select("agent", "t_call")
          .filter(pl.col("agent").is_in([int(a) for a in agents])
                  & (pl.col("t_call") >= dt.datetime.fromtimestamp(t0, dt.timezone.utc))
                  & (pl.col("t_call") <= dt.datetime.fromtimestamp(t1, dt.timezone.utc))).collect())
    return {int(a): np.sort(sub["t_call"].dt.epoch("us").to_numpy() / 1e6) for (a,), sub in cw.group_by(["agent"])}


def build(goals, out_dir: Path, allow_holdout: bool):
    cal = pl.read_parquet(C.SH / "calendar.parquet").with_columns(pl.col("regime").cast(pl.String))
    hm = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    cal = cal.with_columns(pl.Series("hm", hm)).filter(pl.col("goal_no").is_in(goals))
    held = cal.filter(pl.col("holdout") | pl.col("hm"))
    if not allow_holdout:
        assert held.height == 0, "dry run touched a held-out day"
    else:
        h = load_holdout()
        assert set(goals) <= set(h["goal_periods_held_out"]), "confirm mode only targets held-out goal periods"
        assert 45 not in goals, "#45 is refused (reuse policy)"
    cal = cal.drop("hm")
    cc = B.chat_table(cal)
    per = B.select_periods(cal, cc)
    missing = set(goals) - set(per["goal_no"].to_list())
    if missing:
        print("periods failing the data rule (reported as n/a):", sorted(missing))
    gs = per["goal_no"].to_list()
    B.assemble(gs, cal, cc, per, out_dir, with_text_fields=True, allow_holdout_fields=allow_holdout)
    build_gte(out_dir, allow_holdout)
    return gs


def build_gte(base: Path, allow_holdout: bool):
    """gte vectors and fields for the periods in base (scheme/build_r1b.py's gte part, base-aware)."""
    import embed_models as EM
    out = base / "r1b"
    out.mkdir(parents=True, exist_ok=True)
    m = pl.read_parquet(base / "messages.parquet").with_row_index("row")
    if not allow_holdout:
        assert not any(holdout_mask(m["pt_date"].to_list(), m["goal_no"].to_list()))
    ci = pl.read_parquet(ED / "chat_index.parquet").with_row_index("crow")
    ii = pl.read_parquet(ED / "intentions_index.parquet").with_row_index("irow")
    m = m.join(ci, on="message_id", how="left").join(ii, on="event_index", how="left").sort("row")
    kind = m["kind"].to_numpy()
    crow, irow = m["crow"].to_numpy(), m["irow"].to_numpy()
    periods = {p["goal_no"]: p for p in json.loads((base / "periods.json").read_text())}
    reg = np.array([periods[int(g)]["regime_basis"] for g in m["goal_no"].to_list()])
    Ec = np.load(EM.emb_path("chat", "gte_modernbert"), mmap_mode="r")
    Ei = np.load(EM.emb_path("intentions", "gte_modernbert"), mmap_mode="r")
    V = np.zeros((m.height, 64), np.float32)
    for R in sorted(set(reg)):
        W = EM.load_whitener(R, 64, model="gte_modernbert")
        for k, E, idx in ((0, Ec, crow), (1, Ei, irow)):
            sel = np.flatnonzero((reg == R) & (kind == k))
            if len(sel):
                V[sel] = W(np.asarray(E[idx[sel].astype(np.int64)], np.float32))
    np.save(out / "vec_w64_gte.npy", V.astype(np.float16))
    gm = pl.read_parquet(ED / "goals.parquet").with_columns(pl.col("kind").cast(pl.String))
    graw = EM.goal_vectors("gte_modernbert").astype(np.float32)
    fz = {}
    for g in periods:
        f = (pl.col("goal_no") == g) & pl.col("kind").is_in(["goal_whole", "kickoff_room"])
        rows_ = gm.filter(f if allow_holdout else (f & ~pl.col("holdout"))).sort("gid")
        fz[f"g{g}_raw"] = graw[rows_["gid"].to_numpy()] if rows_.height else np.zeros((0, graw.shape[1]), np.float32)
        fz[f"g{g}_kind"] = np.array([0 if k == "goal_whole" else 1 for k in rows_["kind"].to_list()], np.int8)
        fz[f"g{g}_room"] = rows_["room"].fill_null(-1).to_numpy().astype(np.int16) if rows_.height else np.zeros(0, np.int16)
    np.savez(out / "fields_gte.npz", **fz)


def dedupe_keep(g: int, base: Path, sk) -> np.ndarray:
    """r1b.dedupe_mask with a base directory."""
    m = pl.read_parquet(base / "messages.parquet").filter((pl.col("goal_no") == g) & (pl.col("kind") == 0)).select(
        "message_id").with_row_index("ord")
    ci = pl.read_parquet(C.SH / "embeddings/chat_index.parquet").with_row_index("src_row")
    st = pl.read_parquet(C.SH / "embeddings/statements.parquet", columns=["kind", "src_row"]).with_row_index("srow").filter(
        pl.col("kind") == "chat")
    fl = pl.read_parquet(C.SH / "statement_flags.parquet", columns=["srow", "cross_echo", "templated", "self_repeat_both"])
    j = m.join(ci, on="message_id", how="left").join(st, on="src_row", how="left").join(fl, on="srow", how="left").sort("ord")
    bad = (j["cross_echo"].fill_null(False) | j["templated"].fill_null(False) | j["self_repeat_both"].fill_null(False)).to_numpy()
    assert len(bad) == len(sk.t)
    return ~bad


def set_variant(emb: str = "bge", s0: str = "other", tau: float | None = None):
    C.EMB_VARIANT, C.S0_MODE = emb, s0
    C.P["tau"] = TAU0 if tau is None else float(tau)


def evaluate(g, base: Path, allow_holdout: bool, primary: bool):
    """bge primary block (as frozen) plus the r1b additions. Only #28 / its stand-in (primary=True) gets gte identity,
    the unread placebo and the dedupe variant; all targets get the gte T for C1-r1b bookkeeping."""
    ro_ = pl.read_parquet(C.SH / "roster.parquet")
    names = dict(zip(ro_["agent"].to_list(), ro_["name"].to_list()))
    set_variant("bge")
    sk = C.load_period(g, allow_holdout=allow_holdout, base=base, text_fields=True)
    r = C.run_unit(sk, n_null=C.P["n_null"], seed=C.SEED + g, do_human=True, n_withinday=20)
    top = r["nodes"][int(np.nanargmax(r["out"]))]
    out = {"goal_no": g, "T": r["T"], "p_T": r["p_T"], "p_T_withinday": r["withinday"]["p_T"], "T_trim": r["T_trim"],
           "p_T_trim": r["p_T_trim"], "standout": r["standout"], "p_standout": r["p_standout"], "p_max": r["p_max"],
           "phi": r["cent_nullvar"]["phi"], "nodes": r["nodes"], "out": r["out"].tolist(), "top": int(top),
           "top_name": names.get(top), "n_human": int((sk.spk == C.HUMAN).sum())}
    if "human" in r and np.isfinite(r["human"]["out"]):
        out["human_above_median"] = bool(r["human"]["out"] > np.nanmedian(r["out"]))
    D = sorted(set(int(x) for x in sk.day))
    if len(D) >= 4 and len(r["nodes"]) >= 6:
        ro = C.run_unit(sk.subset_days([d for d in D if d % 2]), n_null=20, seed=C.SEED + g + 1, do_human=False)
        re_ = C.run_unit(sk.subset_days([d for d in D if not d % 2]), n_null=20, seed=C.SEED + g + 2, do_human=False)
        oo, ee = dict(zip(ro["nodes"], ro["out"])), dict(zip(re_["nodes"], re_["out"]))
        com = [a for a in r["nodes"] if a in oo and a in ee]
        from scipy.stats import spearmanr
        out["split_half_rho"] = float(spearmanr([oo[a] for a in com], [ee[a] for a in com]).statistic)
    # gte (second model)
    set_variant("gte")
    skg = C.load_period(g, allow_holdout=allow_holdout, base=base, text_fields=True)
    rg = C.run_unit(skg, n_null=C.P["n_null"], seed=C.SEED + g, do_human=False)
    out["gte"] = {"T": rg["T"], "p_T": rg["p_T"], "top": int(rg["nodes"][int(np.nanargmax(rg["out"]))])}
    out["gte"]["top_name"] = names.get(out["gte"]["top"])
    if primary:
        # H57 in-flight placebo at tau = 60 s
        set_variant("bge", s0="unread", tau=60.0)
        sku = C.load_period(g, allow_holdout=allow_holdout, base=base, text_fields=True)
        ru = C.run_unit(sku, n_null=20, seed=C.SEED + g, modes=("seen", "unseen"), do_human=False)
        out["tau60_unread"] = {"T_read": ru["T"], "p_T_read": ru["p_T"], "T_unread": ru["T_unseen"], "p_T_unread": ru["p_T_unseen"]}
        # dedupe (reported)
        set_variant("bge")
        keep = dedupe_keep(g, base, sk)
        orig = C.build_design
        C.build_design = lambda s, **kw: orig(s, **{**kw, "targets_mask": keep if len(s.t) == len(keep) else None})
        try:
            rd = C.run_unit(sk, n_null=20, seed=C.SEED + g, do_human=False)
        finally:
            C.build_design = orig
        out["dedupe"] = {"T": rd["T"], "p_T": rd["p_T"], "kept_frac": float(keep[sk.spk < 100].mean())}
    set_variant("bge")
    return out


def verdicts(res: dict, order: list[int]) -> dict:
    c, f, i = order
    v = {}
    ok_c = c in res
    v["C1_r1b_transfer_28"] = bool(ok_c and res[c]["p_T"] < 0.05 and res[c]["gte"]["p_T"] < 0.05)
    v["C1_bge_only"] = bool(ok_c and res[c]["p_T"] < 0.05)
    v["C2_transfer_IF"] = bool(any(g in res and res[g]["p_T"] >= 0.05 for g in (f, i)))
    v["C3_no_leader"] = sum(res[g]["p_standout"] < 0.05 and res[g]["p_max"] < 0.05 for g in order if g in res) <= 1
    v["C4_stability_28"] = (res[c].get("split_half_rho", np.nan) > 0) if ok_c and "split_half_rho" in res[c] else "n/a"
    v["C5_mode"] = bool(all(g in res for g in order) and res[c]["T"] > res[f]["T"] and res[c]["T"] > res[i]["T"])
    v["C6_both_nulls_28"] = bool(ok_c and res[c]["p_T"] < 0.05 and res[c]["p_T_withinday"] < 0.05)
    ids = ("Claude Opus 4.5", "GPT-5.2")
    v["C7_r1b_identity_28"] = bool(ok_c and res[c]["top_name"] in ids and res[c]["gte"]["top_name"] in ids)
    if ok_c and res[c]["n_human"] >= 15 and "human_above_median" in res[c]:
        v["C8_humans_28"] = not res[c]["human_above_median"]
    else:
        v["C8_humans_28"] = "n/a"
    u = res[c].get("tau60_unread") if ok_c else None
    v["C9_r1b_read_beats_unread_28"] = bool(u and u["T_read"] > u["T_unread"]) if u else "n/a"
    return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--base", type=Path, default=C.DATA / "confirm_r1b_dryrun", help="dry-run build directory")
    a = ap.parse_args()
    if a.confirm and not a.ack:
        raise SystemExit("refusing: --confirm needs --i-understand-this-uses-the-locked-holdout")
    if a.ack and not a.confirm:
        raise SystemExit("refusing: the acknowledgement flag alone does nothing; pass --confirm too")
    confirm = a.confirm and a.ack and not a.dry_run
    if confirm:
        must = [Path(__file__).resolve(), HERE / "CONFIRM_R1B.md", CARD, HERE / "ic_core.py", HERE / "r1b.py",
                HERE.parent / "scheme/build.py", HERE.parent / "scheme/build_r1b.py"]
        if not committed_and_clean(must):
            raise SystemExit("refusing: commit confirm_r1b.py, CONFIRM_R1B.md, ic_core.py, r1b.py, scheme/build*.py and "
                             "the card (unmodified) before the confirmatory run")
        bad = ledger_status(list(TARGETS))
        if bad:
            raise SystemExit(f"refusing: holdout_ledger.check() blocks {bad}")
        C.ledger_calls = ledger_calls_with_holdout
        goals, base = list(TARGETS), C.DATA / "confirm_r1b"
    else:
        ledger_status(list(TARGETS))
        goals, base = list(TARGETS.values()), a.base
        h = load_holdout()
        assert not set(goals) & set(h["goal_periods_held_out"]), "stand-ins must be non-holdout"
    built = build(goals, base, allow_holdout=confirm)
    res = {}
    for k, g in enumerate(goals):
        if g in built:
            res[g] = evaluate(g, base, allow_holdout=confirm, primary=(k == 0))
            print(g, f"bge T={res[g]['T'] * 100:.3f}% p={res[g]['p_T']:.3f}; gte T={res[g]['gte']['T'] * 100:.3f}% "
                     f"p={res[g]['gte']['p_T']:.3f}", flush=True)
    out = {"mode": "confirm_r1b" if confirm else "dry_run_r1b", "run_at": dt.datetime.now(dt.timezone.utc).isoformat(),
           "frozen": FROZEN, "results": res, "verdicts": verdicts(res, goals)}
    dest = (C.DATA / "confirm_r1b_result.json") if confirm else (base / "confirm_r1b_dryrun_result.json")
    dest.write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out["verdicts"], indent=1, default=str))
    if goals[0] in res:
        print("tau60:", res[goals[0]].get("tau60_unread"), "dedupe:", res[goals[0]].get("dedupe"))


if __name__ == "__main__":
    main()
