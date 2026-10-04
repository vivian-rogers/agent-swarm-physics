"""H08 confirmatory test on the LOCKED HOLDOUT -- ROUND-1B RE-FREEZE of `confirm_holdout.py`. Written 2026-10-04 after
round 1b, before any holdout outcome was computed. NOT RUN. `confirm_holdout.py` stays byte-for-byte unchanged; its
evaluate() is imported.

  uv run python hypotheses/H08-context-is-the-coupling/analysis/confirm_r1b.py --dry-run
  uv run python hypotheses/H08-context-is-the-coupling/analysis/confirm_r1b.py --confirm --i-understand-this-uses-the-locked-holdout

Why (holdout ledger item 10): confirm_holdout.py still builds round-1 inputs (H08's own call-start rule, `exposure`
membership, H15's consolidation catalog, H04's round-1 nudge kernel on the buggy activity_bins with all-mention targets
and future-kick isolation).

Inputs switched to the round-1b ledger scheme (imported unchanged; held-out rows admitted only under --confirm):
  * turns / read-out: DQ1 `call_windows` (ctx_mode != summary), the read-out call = the call that received the message
    (`context_ledger_items`), scheme/build_turns_ledger.py; C9 by analysis/visibility_ledger.py;
  * erasures (C3 / NE41): ledger `reset_forced` / `reset_consol` between the read-out call and the talk call,
    analysis/erasure_ledger.py (H15's catalog no longer used);
  * responses: @-mention (pre-registered, primary) and the DQ2 reply-parent author (`reply_pairs`, pair_set = cand);
  * C1's Claude Code fetch logs are unaffected by round 1b (same code path as confirm_holdout.py).
  Embeddings enter only through the descriptive content jump (bge, as round 1b); activity_bins, the DQ8 trim, the work
  ledger, failures and nudge targets are not inputs once CF3 is retired.
build_turns_ledger.load_calls hard-codes `~holdout`; this script installs an equivalent loader with the holdout filter
switched by mode (identical on non-holdout days).

Re-frozen predictions (unit sets as confirm_holdout.py):
  CF1   unchanged thresholds, ledger inputs: regime-III #43, #45-#50, #51 tail: D_addr > 0 (CI) in >= 7/8; D_talk > 0
        (CI) in >= 5/8; G_addr(0) - G_addr(-1) < 0 in >= 6/8. (Round 1b, regime III: D_addr 7/8, D_talk 5/8.)
  CF1b-r1b NEW: reply-author discontinuity D_auth > 0 (CI) in >= 7/8 of the same units (round 1b: 17/17 periods).
  CF2   unchanged, ledger inputs: clean recipients, all 10 units incl. #28, #29: D_addr > 0 (CI) in >= 8/10 and
        |G_addr(0)| < 1/3 G_addr(1) in >= 8/10. (Round 1b: clean subset 15/17; regime-I in-flight peak gone.)
  CF3   RETIRED (CF3-r1b): round 1b reversed its basis -- aligned on the receiving call the nudge response starts at
        read-out (Phi(1,5) measured 1.76 vs predicted 0.52, the opposite of "< -0.2"), the receiving-call kernel lives
        with H04/H43, and the #51-tail kick-response cell is claimed by H12, H19, H30, H39 (same family).
  CF4   unchanged thresholds on ledger erasures (mention response, pre-registered): pooled beta_F < 0 (CI); relative
        drop in [-0.35, -0.08]; beta_V < 0. The reply-author version is reported (round 1b: -21% +- 7%, 8/9).
  CF5   unchanged (Claude Code fetch logs).

Holdout reuse (infra/shared/holdout_ledger.check() before any confirm build): #45 (H02 activity; H04 kernels), #46-#50
(H04 Hawkes / kernels / MF), #32 and #34 (H05; CF5's fetch logs only): all other modality. Planned same-family
(addressing) users: H18 (#28, #29, #45-#50), H11 and H28 (#28, #45), H29, H34, H39 (#51 tail). Disclose in both cards
and LOG.md.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2"
os.environ.setdefault("POLARS_MAX_THREADS", "2")

import argparse  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h08lib import *  # noqa: E402,F403
import confirm_holdout as CH  # noqa: E402  (frozen unit lists, heldout_days, standins, evaluate; main() not called)

FLAG = "--i-understand-this-uses-the-locked-holdout"
LEDGER_TARGETS = ["G28", "G29", "G32", "G34", "G43", "G45", "G46", "G47", "G48", "G49", "G50", "#51-tail"]
B = 200


def make_load_calls(allow_holdout: bool):
    """build_turns_ledger.load_calls with the holdout filter switched by mode (same columns and rules)."""
    import build_turns_ledger as BT
    hfilt = (lambda: pl.lit(True)) if allow_holdout else (lambda: ~pl.col("holdout"))

    def load_calls(days, chat):
        cw = (pl.scan_parquet(SH / "call_windows.parquet").filter(pl.col("pt_date").is_in(days) & hfilt()
                                                                 & (pl.col("ctx_mode").cast(pl.Utf8) != "summary"))
              .select("turn_id", "agent", "pt_date", "talk", "kind", "ctx_mode", "gap_kind", "t_call", "t_first", "t_log", "pause_s")
              .collect())
        lt = (pl.scan_parquet(SH / "context_ledger_turns.parquet").filter(pl.col("pt_date").is_in(days) & hfilt())
              .select("turn_id", "reset_forced", "reset_consol", "k_new").collect())
        cw = cw.join(lt, on="turn_id", how="left").sort("turn_id")
        ev = (pl.read_parquet(SH / "events_core.parquet", columns=["t", "message_id", "action_type"])
              .filter(pl.col("action_type") == "AGENT_TALK").select("message_id", pl.col("t").alias("t_ev")))
        b = (chat.filter(pl.col("pt_date").is_in(days) & (pl.col("speaker_kind").cast(pl.Utf8) == "agent"))
             .select("msg", "message_id", "agent", "t", "mentions_roster", "erow").join(ev, on="message_id", how="left")
             .with_columns(pl.col("t_ev").fill_null(pl.col("t"))).sort("t_ev"))
        b = b.join_asof(cw.select("turn_id", "agent", "t_first", "t_log").sort("t_first"), left_on="t_ev", right_on="t_first",
                        by="agent", strategy="backward")
        b = b.filter(pl.col("turn_id").is_not_null() & (pl.col("t_ev") <= pl.col("t_log")))
        rp = (pl.read_parquet(SH / "reply_pairs.parquet", columns=["b_msg", "a_msg", "pair_set", "parent", "a_agent", "holdout"])
              .filter(hfilt() & (pl.col("pair_set") == "cand") & pl.col("parent")).select(pl.col("b_msg").alias("msg"), "a_msg", "a_agent"))
        b = b.join(rp, on="msg", how="left")
        tm = (b.sort("t").group_by("turn_id").agg(pl.col("msg").first().alias("msg0"), pl.col("erow").first().alias("erow0"),
                                                  pl.col("mentions_roster").flatten().drop_nulls().unique().alias("ment"),
                                                  pl.col("a_msg").drop_nulls().unique().alias("par_msgs"),
                                                  pl.col("a_agent").drop_nulls().unique().alias("par_auth")))
        return cw.join(tm, on="turn_id", how="left")
    BT.load_calls = load_calls
    return BT


def unit_goal(u):
    return 51 if u == "51tail" else int(u)


def ledger_checks():
    sys.path.insert(0, str(ROOT / "infra/shared"))
    import holdout_ledger as HL
    out = {}
    for t in LEDGER_TARGETS:
        c = HL.check("H08", t, "other", ["dilution_addressing"])
        out[t] = {"allowed": c["allowed"], "needs_disclosure": c["needs_disclosure"],
                  "prior_runs": sorted({u["hypothesis"] for u in c["prior_runs"]}),
                  "prior_runs_same_family": sorted({u["hypothesis"] for u in c["prior_runs_same_family"]})}
    return out


def run(dry: bool):
    import visibility_ledger as VL
    import erasure_ledger as EL
    from build_turns import room_lookup
    BT = make_load_calls(allow_holdout=not dry)
    out_root = OUT / ("confirm_r1b_dryrun" if dry else "confirm_r1b")
    out_root.mkdir(parents=True, exist_ok=True)
    if dry:
        S = CH.standins()
        r3, r1, cc_units = S["r3"], S["r1"], S["cc"]
        for u, ds in {**r3, **r1}.items():
            assert not any(is_holdout(d, unit_goal(u)) for d in ds), f"stand-in {u} touches the holdout"
    else:
        r3 = {u: CH.heldout_days(u) for u in CH.R3_UNITS}
        r1 = {u: CH.heldout_days(u) for u in CH.R1_UNITS}
        cc_units = CH.CC_UNITS
        for u, ds in {**r3, **r1}.items():
            assert all(is_holdout(d, unit_goal(u)) for d in ds), f"{u}: not all held out"
    chat = BT.chat_full()
    tl = room_lookup()
    E = np.load(SH / "embeddings/chat_bge_small.npy", mmap_mode="r")
    cd = pl.read_parquet(SH / "chat_core.parquet", columns=["pt_date"]).with_row_index("msg")
    chat_day = dict(zip(cd["msg"].to_list(), cd["pt_date"].to_list()))
    res = {"dry_run": dry, "inputs": "round-1b ledger scheme", "units": {}}
    for u, ds in {**r3, **r1}.items():
        if not ds:
            res["units"][str(u)] = {"n_days": 0}
            continue
        g = unit_goal(u)
        folder = out_root / f"U{u}"
        BT.OUT1B = folder
        BT.period_days_any = (lambda _g, _ds=list(ds): sorted(_ds))
        BT.build_period(g, chat, tl, E)
        VL.OUT1B = folder
        c9 = VL.run_period(g, chat_day, seed=7)
        ent = {"n_days": len(ds), "regime": "III" if u in r3 else "I"}
        if c9 and "talk" in c9.get("primary", {}):
            p, c = c9["primary"], c9.get("posthoc_clean", {})
            ent.update({"D_talk": p["talk"]["D"], "D_addr": p["addr"]["D"], "pre_addr": p["addr"]["pre"],
                        "D_auth": p.get("auth", {}).get("D"), "D_cos": p.get("cos", {}).get("D"),
                        "clean_D_addr": c.get("addr", {}).get("D"),
                        "clean_floor": (c.get("addr", {}).get("G", {}).get(0) or c.get("addr", {}).get("G", {}).get("0")),
                        "clean_top": (c.get("addr", {}).get("G", {}).get(1) or c.get("addr", {}).get("G", {}).get("1"))})
        if u in r3:
            EL.OUT1B = folder
            U, days = EL.units(g)
            nd = len(days)
            W = np.vstack([np.ones((1, nd)), np.random.default_rng(g).multinomial(nd, np.full(nd, 1 / nd), size=B)]).astype(float)
            n_er = {k: int(v) for k, v in U.filter(pl.col("erased")).group_by("kind").len().iter_rows()}
            fm, fa = EL.fit(U, days, W, "men"), EL.fit(U, days, W, "auth")
            if "beta" in fm:
                ent.update({"beta_F": fm["beta"]["erased_F"], "beta_V": fm["beta"]["erased_V"], "rel_F": fm.get("rel_F"),
                            "n_CF": n_er.get("CF", 0)})
            if "beta" in fa:
                ent.update({"beta_F_auth": fa["beta"]["erased_F"], "rel_F_auth": fa.get("rel_F")})
        res["units"][str(u)] = ent
    res["c8"] = {}                                       # CF3 retired: no kernel computed
    import build_cc_exposure as bce
    import cc_exposure as cce
    if dry:
        cce.main(cc_dir=OUT / "cc", periods=cc_units, out_name="c1_confirm_r1b_dryrun.json")
        c1 = json.loads((OUT / "cc/c1_confirm_r1b_dryrun.json").read_text())
    else:
        bce.main(allow=True, out_dir=out_root / "cc")
        cce.main(cc_dir=out_root / "cc", periods=cc_units, out_name="c1_confirm.json")
        c1 = json.loads((out_root / "cc/c1_confirm.json").read_text())
    res["c1"] = {gg: {k_: r.get(k_) for k_ in ("recall", "replay_share", "other_room_coverage", "delay_s")} for gg, r in c1["periods"].items()}
    v = CH.evaluate(res, r3, r1)
    v["CF3"] = {"pass": None, "status": "retired (CF3-r1b): see the module docstring"}
    r3u = [res["units"][str(u)] for u in r3 if res["units"].get(str(u), {}).get("D_auth")]
    need = int(np.ceil(7 / 8 * len(r3u))) if r3u else 0
    na = sum(x["D_auth"][1] > 0 for x in r3u)
    v["CF1b-r1b"] = {"units": len(r3u), "auth": int(na), "pass": bool(r3u and na >= need)}
    import erasure as er
    bf = [res["units"][str(u)]["beta_F_auth"] for u in r3 if res["units"].get(str(u), {}).get("beta_F_auth") and res["units"][str(u)].get("n_CF", 0) >= 50]
    v["CF4_reply_author_descriptive"] = er.dl_meta([x[0] for x in bf], [(x[2] - x[1]) / 3.92 for x in bf]) if bf else None
    res["verdicts"] = v
    jdump(res, out_root / ("dryrun.json" if dry else "confirm.json"))
    print(json.dumps(v, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    write_provenance(("confirm_r1b_dryrun" if dry else "confirm_r1b") + "/*", "hypotheses/H08-context-is-the-coupling/analysis/confirm_r1b.py",
                     ["call_windows", "context_ledger_turns", "context_ledger_items", "reply_pairs", "chat_core", "chat_mentions_clean",
                      "events_core", "embeddings/chat_bge_small", "claude_code_messages"], {"dry_run": dry, "units": [str(u) for u in {**r3, **r1}]})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument(FLAG, dest="ack", action="store_true")
    a = ap.parse_args()
    if a.dry_run and (a.confirm or a.ack):
        sys.exit("choose either --dry-run or --confirm, not both")
    led = ledger_checks()
    print("ledger:", json.dumps(led))
    if a.dry_run:
        run(dry=True)
        return
    if not (a.confirm and a.ack):
        sys.exit(f"Refusing: the confirmatory run uses the locked holdout. Pass --confirm {FLAG} (after sign-off), "
                 "or --dry-run for the non-holdout stand-ins.")
    blocked = [t for t, c in led.items() if not c["allowed"]]
    if blocked:
        sys.exit(f"holdout_ledger.check refuses {blocked} (same-family prior run); resolve before running.")
    run(dry=False)


if __name__ == "__main__":
    main()
