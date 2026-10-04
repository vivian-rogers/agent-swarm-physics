"""H23 confirmatory test on goal period #45 ("Follow your leader!"), LOCKED HOLDOUT -- ROUND-1B RE-FREEZE of
`confirm_g45.py`. Written 2026-10-04 after round 1b, before any #45 message content was read. NOT RUN.
`confirm_g45.py`, `h23lib.py`, `h23run.py` and `scheme/build_messages.py` stay byte-for-byte unchanged; this script
imports them and swaps inputs from outside (as analysis/r1b.py does).

Refuses to run on #45 unless (as confirm_g45.py, plus this script and the ledger):
  1. this script, confirm_g45.py, h23lib.py, h23run.py, build_messages.py and the H23 card are committed and unmodified;
  2. the flags --confirm --i-understand-this-uses-the-locked-holdout are given;
  3. the reuse is disclosed in the H02 card and in LOG.md (grep for 'H23' near '#45' with reuse/confirmation);
  4. infra/shared/holdout_ledger.check('H23', 'G45', ...) reports no same-family prior run.
Without the flags it runs a DRY RUN on the non-holdout G44 v7-aug-64 segment (agent 28), reading nothing from #45.

Input switches (round 1b):
  * copy information from infra/shared/copy_info (h23lib's decompose / mi_parts came from H07's folder; round 1b
    reproduced all 1,022 G44 numbers exactly);
  * C0-r1b, holdout ledger item 14 (PROPOSED AMENDMENT, needs Vivian's approval): agent-30 messages before
    2026-06-01 17:15:40 UTC (about 11 min under a wrong model string, DQ6) are NOT leader messages; they stay in the
    table as context for others. Set APPLY_ITEM14 = False to reproduce confirm_g45.py's leader set;
  * leader checkpoints for agent 28 from DQ6 `checkpoint` rows (round 1b: 0 of 27 relabelled); agent 30 keeps
    h23lib's label apart from C0-r1b;
  * contexts by receiving-call visibility: a message's 3 context messages are the latest period-set messages by other
    speakers posted BEFORE THE PRODUCING CALL'S t_call (DQ1 call_windows; message -> call through its AGENT_TALK event,
    as DQ2), not the 3 messages before the message's own timestamp, which include in-flight messages the author could
    not have read. Human speakers (no calls) keep the room-order rule. z_ctx and prev_act are rebuilt accordingly;
  * C5 embedding level in BOTH models: bge (the frozen run_period value) and gte-modernbert (shared chat vectors; the
    31 corpus targets embedded with gte once, offline, cached in G44/r1b/corpus_target_gte_modernbert.npy).
  activity_bins, the DQ8 trim, the work ledger, failures and nudge targets are not inputs of this design.

Re-frozen predictions (ids kept where unchanged):
  C1  unchanged: corpus-distinctive marker rate leader / CTRL >= 1.2 with p < 0.05, and leader > Kimi K2.6 (p < 0.10).
  C2  unchanged: bigram copy information vs CTRL <= 0.01 bits/bigram, and leader c2 < 0.5 x 0.182.
  C3  unchanged: directive share <= corpus - 0.25; JSD > corpus self-resampling p95; c_ex < 0.10; efficiency < 0.5.
  C4-r1b  same thresholds on ledger-visible contexts (JSD(leader, contexts) < JSD(leader, corpus); leader's lexical
          context copy not above CTRL's, p > 0.10). Reason: Standards section 2 (a message acts at the receiving call).
  C5-r1b  leader > Kimi K2.6 same-period on d = cos(z, C) - cos(z, K) with p < 0.10 in BOTH bge and gte. Reason: round
          1b's only pro-distillation hint (bge p 0.08) vanished in gte (p 0.43).
  Verdicts: vocabulary copied iff C1 and C2; plans not copied iff C3; R1 rejected iff C1's Kimi clause and C5-r1b;
  R2 favoured on plans iff C4-r1b.

Holdout reuse: H02 (activity couplings) and H04 (Hawkes / kernels, segment A1) ran on #45 in another modality; planned
same-family users of #45 content: H12, H13, H16, H33, H36 (content alignment) and H11, H15, H28 (lineage). Whoever runs
first makes the others second users. Disclose in both cards and LOG.md.

Usage:
  uv run --with sentence-transformers python hypotheses/H23-leader-distillation-copy/analysis/confirm_r1b.py   # dry run (G44)
  ... --confirm --i-understand-this-uses-the-locked-holdout                                                       # the real test
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2"
os.environ.setdefault("HF_HUB_OFFLINE", "1")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import json  # noqa: E402
import shutil  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h23lib as L  # noqa: E402

ROOT = L.ROOT
sys.path.insert(0, str(ROOT / "infra/shared"))
import copy_info as CI  # noqa: E402
import embed_models as EM  # noqa: E402

L.decompose, L.mi_parts = CI.decompose, CI.mi_parts      # shared module instead of H07's folder (round 1b, part B)
import h23run  # noqa: E402
import confirm_g45 as CG  # noqa: E402  (frozen evaluate() and preconditions(); main() is not called)

APPLY_ITEM14 = True
ITEM14_FIX_UTC = dt.datetime(2026, 6, 1, 17, 15, 40, tzinfo=dt.timezone.utc)
G44 = L.OUT / "G44"
GTE_CACHE = G44 / "r1b" / "corpus_target_gte_modernbert.npy"
CFG = {"checkpoints": ["kimi-v7-aug-64"]}


def relabel(M: pl.DataFrame) -> tuple[pl.DataFrame, dict]:
    """DQ6 checkpoints for agent 28 (non-holdout); C0-r1b exclusion window for agent 30."""
    gt = (pl.read_parquet(L.SH / "ground_truth_labels.parquet")
          .filter((pl.col("label_kind") == "checkpoint") & (pl.col("agent") == 28)).sort("t_valid_from"))
    spans = gt.select("value", "t_valid_from", "t_valid_to").rows()

    def lab(g, a, t, old):
        if g != "leader":
            return old
        if a == 28:
            for v, t0, t1 in spans:
                if t0 <= t < t1:
                    return v
            return old
        if a == 30 and APPLY_ITEM14 and t < ITEM14_FIX_UTC:
            return "excluded_item14"
        return old
    new = [lab(g, a, t, o) for g, a, t, o in M.select("group", "agent", "t", "checkpoint").rows()]
    info = {"n_leader_relabelled": int(sum(1 for o, n in zip(M["checkpoint"].to_list(), new) if o != n)),
            "item14_applied": APPLY_ITEM14}
    return M.with_columns(pl.Series("checkpoint", new, dtype=pl.String)), info


def ledger_contexts(pdir: Path, M: pl.DataFrame, allow_holdout: bool) -> tuple[pl.DataFrame, dict]:
    """Rebuild ctx_ids / prev_act / z_ctx with receiving-call visibility (see the module docstring)."""
    per = M.filter(pl.col("set") == "period").sort("t")
    days = per["pt_date"].unique().to_list()
    cw = (pl.scan_parquet(L.SH / "call_windows.parquet")
          .filter(pl.col("pt_date").is_in(days) & (pl.col("ctx_mode").cast(pl.Utf8) != "summary")
                  & (pl.lit(True) if allow_holdout else ~pl.col("holdout")))
          .select("agent", "t_call", "t_first", "t_log").collect().sort("t_first"))
    ev = (pl.read_parquet(L.SH / "events_core.parquet", columns=["t", "message_id", "action_type"])
          .filter(pl.col("action_type") == "AGENT_TALK").select("message_id", pl.col("t").alias("t_ev")))
    ag = (per.filter(pl.col("speaker_kind") == "agent").select("message_id", "agent", "t")
          .join(ev, on="message_id", how="left").with_columns(pl.col("t_ev").fill_null(pl.col("t"))).sort("t_ev")
          .join_asof(cw.with_columns(pl.col("agent").cast(per["agent"].dtype)), left_on="t_ev", right_on="t_first",
                     by="agent", strategy="backward")
          .with_columns(pl.when(pl.col("t_ev") <= pl.col("t_log")).then(pl.col("t_call")).otherwise(None).alias("t_call")))
    tcall = dict(zip(ag["message_id"].to_list(), ag["t_call"].to_list()))
    rows = per.select("message_id", "agent", "speaker_kind", "primary", "t").to_dicts()
    ts = [r["t"] for r in rows]
    ctx_ids, prev_act, n_call = {}, {}, 0
    import bisect
    for i, r in enumerate(rows):
        cut = tcall.get(r["message_id"]) if r["speaker_kind"] == "agent" else None
        if cut is not None:
            n_call += 1
            j = bisect.bisect_left(ts, cut) - 1          # latest message strictly before t_call
        else:
            j = i - 1                                    # room-order fallback (humans; unmatched calls)
        me = (r["speaker_kind"], r["agent"])
        prev = []
        while j >= 0 and len(prev) < 3:
            o = rows[j]
            if not (o["speaker_kind"] == "agent" and (o["speaker_kind"], o["agent"]) == me):
                prev.append(o)
            j -= 1
        ctx_ids[r["message_id"]] = [o["message_id"] for o in prev]
        prev_act[r["message_id"]] = prev[0]["primary"] if prev else None
    M2 = M.with_columns(
        pl.when(pl.col("set") == "period").then(pl.col("message_id").map_elements(lambda m: ctx_ids.get(m), return_dtype=pl.List(pl.String)))
        .otherwise(pl.col("ctx_ids")).alias("ctx_ids"),
        pl.when(pl.col("set") == "period").then(pl.col("message_id").map_elements(lambda m: prev_act.get(m), return_dtype=pl.String))
        .otherwise(pl.col("prev_act")).alias("prev_act"))
    V = dict(np.load(pdir / "vectors.npz", allow_pickle=False))
    E = np.load(L.SH / "embeddings/chat_bge_small.npy", mmap_mode="r")
    W = EM.load_whitener("III", 32, "bge_small")
    rowmap = dict(zip(M2["message_id"].to_list(), M2["emb_row"].to_list()))
    Zc = V["z_ctx"].copy()
    for i, (m, s) in enumerate(zip(V["message_id"], V["set"])):
        if s != "period":
            continue
        ids = ctx_ids.get(str(m)) or []
        Zc[i] = W(np.asarray(E[[rowmap[x] for x in ids]], dtype=np.float32).mean(0, keepdims=True))[0] if ids else np.nan
    V["z_ctx"] = Zc.astype(np.float32)
    np.savez_compressed(pdir / "vectors.npz", **V)
    return M2, {"n_agent_msgs_with_call": n_call, "n_period": per.height, "_tcall": tcall}


def ctx_copy_ledger(pdir: Path, tcall: dict) -> dict:
    """C4-r1b lexical clause: h23run's token-matched bigram context copy (rival R2), with the context window ending at
    the producing call's t_call instead of at the message itself (in-memory text only; nothing written)."""
    import bisect
    M = pl.read_parquet(pdir / "messages.parquet")
    per = M.filter(pl.col("set") == "period")
    lead = per.filter((pl.col("group") == "leader") & pl.col("live") & pl.col("checkpoint").is_in(CFG["checkpoints"]))
    ctrl = pl.concat([per.filter((pl.col("group") == "kimi") & pl.col("live")), per.filter((pl.col("group") == "village") & pl.col("live"))])
    C = pl.read_parquet(G44 / "corpus_text.parquet").filter(pl.col("member"))
    ntoks_c = sum(len(L.tokens(x)) for x in C["response"].to_list())
    perall = per.sort("t")
    T = h23run._texts(perall["message_id"].to_list())
    ptxt = [T.get(m) or "" for m in perall["message_id"].to_list()]
    pid, pagent, pkind, pt = (perall[c].to_list() for c in ("message_id", "agent", "speaker_kind", "t"))
    pos = {m: i for i, m in enumerate(pid)}

    def cc(df):
        out = []
        for m, a in zip(df["message_id"].to_list(), df["agent"].to_list()):
            cut = tcall.get(m)
            j = (bisect.bisect_left(pt, cut) - 1) if cut is not None else pos[m] - 1
            ref, nt = set(), 0
            while j >= 0 and nt < ntoks_c:
                if not (pkind[j] == "agent" and pagent[j] == a):
                    tok = L.tokens(ptxt[j])
                    ref |= L.ngram_set(tok, 2)
                    nt += len(tok)
                j -= 1
            out.append(L.copy_fraction(T.get(m) or "", ref, 2) if nt >= 0.5 * ntoks_c else np.nan)
        return np.array(out)
    t = L.perm_mean_diff(cc(lead), cc(ctrl), seed=h23run.RNG_SEED)
    return {"p": float(t["p"]), "diff": float(t["diff"])}


def c5_two_models(pdir: Path) -> dict:
    """d = cos(z, corpus centroid) - cos(z, Kimi-field centroid), regime-III whitened 32-d, per model (r1b part C)."""
    M = pl.read_parquet(pdir / "messages.parquet")
    C = pl.read_parquet(G44 / "corpus_text.parquet")
    mem = np.array(C["member"].to_list())
    if not GTE_CACHE.exists():
        from sentence_transformers import SentenceTransformer
        import torch
        torch.set_num_threads(2)
        spec = EM.MODELS["gte_modernbert"]
        m = SentenceTransformer(spec["hf"], revision=spec["revision"], device="cpu")
        m.max_seq_length = 256
        tg = m.encode([s[:2000] for s in C["response"].to_list()], batch_size=16, normalize_embeddings=True,
                      convert_to_numpy=True).astype(np.float32)
        GTE_CACHE.parent.mkdir(parents=True, exist_ok=True)
        np.save(GTE_CACHE, tg)
    tgt = {"bge_small": np.load(G44 / "corpus_emb.npz")["target"], "gte_modernbert": np.load(GTE_CACHE)}
    per = M.filter(pl.col("set") == "period")
    groups = {"leader": per.filter((pl.col("group") == "leader") & pl.col("live") & pl.col("checkpoint").is_in(CFG["checkpoints"])),
              "K_same": per.filter((pl.col("group") == "kimi") & pl.col("live"))}
    kfield = M.filter(pl.col("set") == "field")
    out = {}
    for model in ("bge_small", "gte_modernbert"):
        Eraw = np.load(L.SH / f"embeddings/chat_{EM.MODELS[model]['suffix']}.npy", mmap_mode="r")
        W = EM.load_whitener("III", 32, model)
        zbarC = W(tgt[model][mem]).mean(0)
        zbarK = W(np.asarray(Eraw[kfield["emb_row"].to_numpy()], dtype=np.float32)).mean(0)
        D = {g: L.cos_rows(W(np.asarray(Eraw[df["emb_row"].to_numpy()], dtype=np.float32)), zbarC)
             - L.cos_rows(W(np.asarray(Eraw[df["emb_row"].to_numpy()], dtype=np.float32)), zbarK) for g, df in groups.items()}
        t = L.perm_mean_diff(D["leader"], D["K_same"], seed=20261003)
        out[model] = {"d_mean": {g: float(v.mean()) for g, v in D.items()}, "p": float(t["p"]), "pass": bool(t["p"] < 0.10)}
    out["pass_both"] = bool(out["bge_small"]["pass"] and out["gte_modernbert"]["pass"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    args = ap.parse_args()
    from build_messages import build
    import holdout_ledger as HL
    led = HL.check("H23", "G45", "message content", ["content_alignment", "artifact_lineage"])
    led = {"allowed": led["allowed"], "needs_disclosure": led["needs_disclosure"],
           "prior_runs": sorted({u["hypothesis"] for u in led["prior_runs"]}),
           "competing_planned": sorted({u["hypothesis"] for u in led["competing_planned"]})}
    if args.confirm or args.ack:
        if not (args.confirm and args.ack):
            raise SystemExit("refusing: both --confirm and --i-understand-this-uses-the-locked-holdout are required")
        fails = CG.preconditions()
        rel = str(Path(__file__).resolve().relative_to(ROOT))
        if CG._git("ls-files", "--error-unmatch", rel).returncode != 0 or CG._git("diff", "--quiet", "HEAD", "--", rel).returncode != 0:
            fails.append(f"not committed or modified: {rel}")
        if not led["allowed"]:
            fails.append("holdout_ledger.check: a same-family prior run exists on G45")
        if fails:
            raise SystemExit("refusing (holdout reuse policy):\n  - " + "\n  - ".join(fails))
        pdir = L.OUT / "G45_r1b"
        build(45, pdir, allow_holdout=True)
        mode, allow = "CONFIRMATORY #45 (locked holdout), round-1b re-freeze", True
    else:
        pdir = G44 / "dryrun_confirm_r1b"
        pdir.mkdir(parents=True, exist_ok=True)
        for f in ("messages.parquet", "vectors.npz"):
            shutil.copy(G44 / f, pdir / f)
        M0 = pl.read_parquet(pdir / "messages.parquet")
        from common import holdout_mask
        assert not any(holdout_mask(M0["pt_date"].to_list(), M0["goal_no"].to_list())), "dry run touched the holdout"
        mode, allow = "DRY RUN on G44 (non-holdout stand-in), round-1b re-freeze", False
    M = pl.read_parquet(pdir / "messages.parquet")
    M, info_cp = relabel(M)
    M, info_ctx = ledger_contexts(pdir, M, allow)
    M.write_parquet(pdir / "messages.parquet", compression="zstd")
    R = h23run.run_period(pdir, CFG)
    V = CG.evaluate(R)
    V["C4-r1b"] = V.pop("C4")
    lx = ctx_copy_ledger(pdir, info_ctx.pop("_tcall"))
    V["C4-r1b"]["p_ctx_copy_room_order"] = V["C4-r1b"].pop("p_ctx_copy")
    V["C4-r1b"]["p_ctx_copy_ledger"] = lx["p"]
    V["C4-r1b"]["pass"] = bool(V["C4-r1b"]["jsd_leader_ctx"] < V["C4-r1b"]["jsd_leader_corpus"] and lx["p"] > 0.10)
    V["C5_bge_frozen_path"] = V.pop("C5")
    V["C5-r1b"] = c5_two_models(pdir)
    V["R1_rejected"] = bool(V["C1"]["p_kimi"] < 0.10 and V["C5-r1b"]["pass_both"])
    V["R2_favored_on_plans"] = V["C4-r1b"]["pass"]
    V.update({"mode": mode, "n": R["n"], "checkpoints": info_cp, "contexts": info_ctx, "ledger": led,
              "run_at": dt.datetime.now(dt.timezone.utc).isoformat()})
    (pdir / "confirm_r1b_verdicts.json").write_text(json.dumps(V, indent=1, default=h23run._np))
    print(json.dumps(V, indent=1, default=h23run._np))


if __name__ == "__main__":
    main()
