"""H24 confirmatory test on the locked holdout #14 (personality tests; regime I, mode I), RE-FROZEN ON ROUND-1B
INPUTS (2026-10-04). WRITTEN, NOT RUN. `confirm.py` is left byte-for-byte untouched; changes are in CONFIRM_R1B.md:
  * goal field from the SHARED goal fields (embeddings/goals.parquet + goal_vectors; goal_fields.py) instead of H24's
    own goal + kickoff embedding (cos 0.88 on the kickoff part in #21), removed along MULTIPLE directions: g-hat plus
    every goal-text and kickoff chunk (goal_fields chunking, embedded here with each model; vector-spins pitfall);
  * BOTH embedding models (bge-small, gte-modernbert): shared regime-whitened statement vectors (statements_white32);
    a prediction passes only if it passes in both models ('model-dependent' otherwise);
  * style: within-period style-residualized statement vectors (style_resid.fit_style / apply_style refit on the
    period's own statements per kind, as the style_resid docstring prescribes for a held-out period), as a sensitivity;
  * N2 placebo weeks with the shared fields and multi-direction removal (explore.placebo_N2 under the round-1b CFG);
  * new C4-r1b: the pair-level reading DiD (round 1b G21 native) transferred to #14;
  * holdout_ledger.check() and a commit check on the confirm path.
Activity bins, outages and the DQ8 trim are not H24 inputs. Reading events come from agent narration (a claim).

Usage:
  dry run on a non-holdout period (default #21; pipeline check, reproduces the round-1b G21 configuration):
     uv run --offline --with sentence-transformers python hypotheses/H24-forecast-coupling-switch/analysis/confirm_r1b.py --dry-run 21
  the real run (needs Vivian's sign-off; refuses otherwise):
     uv run --offline --with sentence-transformers python hypotheses/H24-forecast-coupling-switch/analysis/confirm_r1b.py \
         --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2" if _v == "POLARS_MAX_THREADS" else "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ.setdefault("HF_HUB_OFFLINE", "1")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "scheme"))
from h24lib import H24, mention_regexes, project_out, record_reads, unit  # noqa: E402
from h24stats import random_rotations, seg_alignment, segments  # noqa: E402
from common import OUT, REVISION, git_commit, holdout_mask, load_holdout  # noqa: E402
import embed_models as EM  # noqa: E402
import explore as X  # noqa: E402

ROOT = HERE.parents[2]
HYP = "H24"
TARGET = 14
K, B, POST, DIM = 4, 200, 60.0, 32
SHIFTS = (60.0, 90.0, 120.0)
SEED = 20261003
MODELS = ("bge_small", "gte_modernbert")
MIN_DID_EVENTS = 10

PREDICTIONS = {
    "written": "2026-10-04, re-frozen on round-1b inputs before any look at #14 data (original 2026-10-03)",
    "inputs": "shared goal fields, multi-direction field removal (g-hat + goal/kickoff chunks), both embedding models, "
              "regime-whitened 32-d statement vectors; style-residualized vectors (period refit) as a sensitivity",
    "C0_switch_exists": {"rule": "(unchanged) >= 4 agents (and >= 2/3 of those present on day 1) have tau_i on day 1",
                         "credence": 0.5},
    "C1-r1b_step": {"rule": "dA_res > q90 of N1 AND > q90 of N2, in BOTH models (pass); fails in both -> fail; else "
                            "'model-dependent'", "my_credence_pass": 0.15,
                    "reason": "round 1b: no step in 13/13 configurations, but the gte step (+0.16) is matched by "
                              "kickoff-day placebos only; one model is not enough"},
    "C2-r1b_level": {"rule": "A_res(pre-switch) > q95 of the per-agent rotation null, in both models", "credence": 0.85,
                     "reason": "round 1b: 0.34-0.42 vs q95 0.02-0.10 in every configuration"},
    "C3-r1b_ramp": {"rule": "Spearman rho > 0 over 2-h blocks after day-1 block 0, in both models", "credence": 0.5,
                    "reason": "round 1b: sign holds in both models, significance model-dependent"},
    "C4-r1b_reading_did": {"rule": "statements move toward the owner of a document just read, relative to agents not "
                                   "read (G21 native design): mean DiD > 0 and owner-permutation p < 0.05 in both models; "
                                   f"< {MIN_DID_EVENTS} usable events -> inconclusive",
                           "credence": 0.35, "reason": "new: round 1b G21 native, +0.036 / +0.030, p 0.035 / 0.038; "
                                                      "weakens after style removal (reported as a sensitivity)"},
    "power_note": "#14 has N = 6; a C1 failure is weak evidence; reading events at N = 6 may be too few for C4-r1b",
}


# ------------------------------------------------------------------ guards
def committed_clean(paths) -> bool:
    for p in paths:
        r = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--error-unmatch", str(p)], capture_output=True)
        if r.returncode != 0:
            return False
        r = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--", str(p)], capture_output=True, text=True)
        if r.returncode != 0 or r.stdout.strip():
            return False
    return True


def ledger_status(strict: bool) -> bool:
    sys.path.insert(0, str(ROOT))
    from infra.shared import holdout_ledger as hl
    r = hl.check(HYP, f"G{TARGET:02d}", "message content", ["content_alignment"])
    print(f"ledger G{TARGET:02d}: allowed={r['allowed']} needs_disclosure={r['needs_disclosure']} "
          f"prior_runs={sorted({u['hypothesis'] for u in r['prior_runs']})} "
          f"same_family_runs={sorted({u['hypothesis'] for u in r['prior_runs_same_family']})} "
          f"competing_planned={sorted({u['hypothesis'] for u in r['competing_planned']})}", flush=True)
    return r["allowed"] or not strict


# ------------------------------------------------------------------ inputs
def field_vectors(goal: int, allow_holdout: bool) -> dict:
    """Per model: ghat (shared goal + kickoff vectors, regime-I whitened) and the chunk directions (goal text and
    kickoff chunks embedded with the model). Mirrors scheme/build_r1b.py. Text in memory only."""
    import goal_fields as GF
    import torch
    from sentence_transformers import SentenceTransformer
    torch.set_num_threads(2)
    meta, texts = GF.goal_texts()
    rec = {}
    for m, tx in zip(meta, texts):
        if m["goal_no"] == goal and m["kind"] in ("goal", "kickoff"):
            assert allow_holdout or not m["holdout"]
            rec[m["kind"]] = tx
    del texts
    gm = pl.read_parquet(EM.ED / "goals.parquet").with_columns(pl.col("kind").cast(pl.String))
    out = {}
    for model in MODELS:
        spec = EM.MODELS[model]
        dev = "mps" if torch.backends.mps.is_available() else "cpu"
        mdl = SentenceTransformer(spec["hf"], revision=spec.get("revision"), device=dev)
        mdl.max_seq_length = 256
        W = EM.load_whitener("I", 64, model)
        V = EM.goal_vectors(model).astype(np.float32)
        ch = []
        for kind in ("goal", "kickoff"):
            if rec.get(kind):
                e = mdl.encode([s[:2000] for s in rec[kind]], batch_size=16, normalize_embeddings=True, convert_to_numpy=True)
                ch.append(unit(W(e)))
        q = gm.filter((pl.col("goal_no") == goal) & (pl.col("kind") == "goal"))
        gv = unit(W(V[q["gid"][0]][None])[0])
        q = gm.filter((pl.col("goal_no") == goal) & (pl.col("kind") == "kickoff"))
        kv = unit(W(V[q["gid"][0]][None])[0]) if q.height else None
        out[model] = dict(ghat=(unit(gv + kv) if kv is not None else gv).astype(np.float64),
                          chunks=np.vstack(ch).astype(np.float64) if ch else np.zeros((0, 64)))
        del mdl
    return out


def style_vectors(st: pl.DataFrame, model: str) -> tuple[np.ndarray, dict]:
    """style_resid_period vectors for the period's statements, refit within (goal, regime, kind) on the period's own
    rows (>= MIN_FIT_PERIOD), else the shared (regime-fallback) vectors."""
    import style_resid as SR
    srow = st["srow"].to_numpy()
    shared = np.asarray(np.load(EM.ED / f"statements_style_resid_period32_{EM.MODELS[model]['suffix']}.npy",
                                mmap_mode="r")[np.sort(srow)], np.float64)[np.argsort(np.argsort(srow))]
    out = shared.copy()
    info = {}
    allst = pl.read_parquet(EM.ED / "statements.parquet").with_row_index("srow").filter(
        (pl.col("goal_no") == st["goal_no"][0]))
    for kind in ("chat", "intent"):
        g = allst.filter(pl.col("kind") == kind).sort("srow")
        if g.height < SR.MIN_FIT_PERIOD:
            info[kind] = {"fit": "regime_fallback (shared)", "n": g.height}
            continue
        rows = g["srow"].to_numpy()
        U = np.asarray(np.load(EM.ED / f"statements_white32_{EM.MODELS[model]['suffix']}.npy", mmap_mode="r")[rows], np.float64)
        U /= np.maximum(np.linalg.norm(U, axis=1, keepdims=True), 1e-12)
        F = SR.style_matrix(g.select("kind", "src_row"))
        allm = np.ones(len(rows), bool)
        c, r2 = SR.fit_style(U, F, allm)
        Rk = SR.apply_style(U, F, allm, c)
        pos = {r: i for i, r in enumerate(rows.tolist())}
        sel = np.flatnonzero(st["kind"].to_numpy() == kind)
        out[sel] = Rk[[pos[r] for r in srow[sel]]]
        sh = shared[sel] / np.maximum(np.linalg.norm(shared[sel], axis=1, keepdims=True), 1e-12)
        info[kind] = {"fit": "period refit", "n": int(len(rows)), "style_r2": r2,
                      "cos_to_shared_min": float((out[sel] * sh).sum(1).min()) if len(sel) else None}
    return out, info


def residual(X0, fld):
    Z = unit(np.asarray(X0, np.float64)[:, :DIM])
    F = [fld["ghat"][:DIM]] + list(fld["chunks"][:, :DIM])
    return Z, unit(project_out(Z, np.array(F)))


# ------------------------------------------------------------------ statistics
def reading_did(cu, st, Zr, present, pats, rng, n_perm=2000):
    """Round 1b G21 native (natives_r1b.g21, statements only) on any period: first reading event per (reader, owner,
    day) from the reader's own reasoning (a claim); DiD = change in the reader's alignment with the owner minus the mean
    change with agents not read within +-60 min; owner-permutation null."""
    cu = cu.filter(pl.col("agent").is_in(present) & pl.col("reasoning").is_not_null())
    ev = []
    for x in cu.sort("t").iter_rows(named=True):
        for sent in re.split(r"(?<=[.!?\n])\s+", x["reasoning"]):
            if not record_reads(sent):
                continue
            hits = [b for b in present if b != x["agent"] and pats[b].search(sent)]
            if hits:
                ev.append({"agent": x["agent"], "t": x["t"], "whose": hits[0]})
                break
    if not ev:
        return {"n": 0, "n_events_all": 0}
    E = pl.DataFrame(ev, schema={"agent": pl.Int8, "t": pl.Datetime("us", "UTC"), "whose": pl.Int8}).with_columns(
        pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("pt_date"))
    first = E.sort("t").group_by("agent", "whose", "pt_date", maintain_order=True).first()
    tS = st["t"].to_numpy().astype("datetime64[us]").astype(np.int64) / 6e7
    aS = st["agent"].to_numpy()
    allE = E.with_columns((pl.col("t").cast(pl.Int64) / 6e7).alias("m"))

    def vec(sel):
        return unit(Zr[sel].mean(0)) if sel.sum() >= 2 else None
    rows = []
    for r in first.iter_rows(named=True):
        i, j = int(r["agent"]), int(r["whose"])
        tm = r["t"].timestamp() / 60
        pre, post = vec((aS == i) & (tS >= tm - 60) & (tS < tm)), vec((aS == i) & (tS >= tm) & (tS < tm + 60))
        if pre is None or post is None:
            continue
        d = {}
        for k in present:
            if k != i:
                ref = vec((aS == k) & (tS >= tm - 180) & (tS < tm))
                if ref is not None:
                    d[k] = float(post @ ref - pre @ ref)
        if j not in d:
            continue
        near = set(allE.filter((pl.col("agent") == i) & ((pl.col("m") - tm).abs() <= 60))["whose"].to_list())
        ctrl = [k for k in d if k != j and k not in near]
        if ctrl:
            rows.append({"d": d, "j": j, "near": near, "did": d[j] - float(np.mean([d[k] for k in ctrl]))})
    if not rows:
        return {"n": 0, "n_events_all": E.height}
    obs = float(np.mean([x["did"] for x in rows]))
    null = []
    for _ in range(n_perm):
        vals = []
        for x in rows:
            cand = [k for k in x["d"] if k != x["j"] and k not in x["near"]]
            jj = cand[rng.integers(len(cand))]
            cc = [k for k in x["d"] if k not in (jj, x["j"]) and k not in x["near"]]
            if cc:
                vals.append(x["d"][jj] - float(np.mean([x["d"][k] for k in cc])))
        null.append(np.mean(vals) if vals else np.nan)
    null = np.array(null, float)
    return {"n": len(rows), "n_events_all": E.height, "mean_did": obs,
            "perm_p": float((1 + np.nansum(null >= obs)) / (1 + np.isfinite(null).sum())),
            "frac_pos": float(np.mean([x["did"] > 0 for x in rows]))}


def run_model(model, st, Z, Zr, mins, agents, pdays, days, switched, tau, C0, rng, cu, present, pats):
    out = {}

    def o1(ZZ, taus, day):
        pre, post = segments(np.where(pdays == day, mins, np.nan), agents, switched, taus, POST)
        return seg_alignment(ZZ, pre, post, K, B, rng)
    if switched:
        tau_sw = {x: tau[x] for x in switched}
        tau_star = float(np.median(list(tau_sw.values())))
        r = o1(Zr, tau_sw, days[0])
        if r is not None:
            plac = [o1(Zr, {x: tau_sw[x] + s for x in switched}, days[0]) for s in SHIFTS] + [o1(Zr, tau_sw, d) for d in days[1:]]
            n1 = [p["dA"] for p in plac if p]
            X.CFG.update({"emb": model, "goals": "shared", "field": "multi", "dedupe": "none", "style": False})
            n2 = [w["res"]["dA"] for w in X.placebo_N2(DIM, K, rng, tau_star)]
            lv = []
            for _ in range(25):
                ZR = Zr.copy()
                for x, Q in zip(switched, random_rotations(DIM, len(switched), rng)):
                    ZR[agents == x] = Zr[agents == x] @ Q
                q = o1(ZR, tau_sw, days[0])
                if q:
                    lv.append(q["A_pre"])
            out["C1"] = {"dA_res": r["dA"], "A_pre": r["A_pre"], "A_post": r["A_post"], "N1": n1,
                         "N1_q90": float(np.quantile(n1, 0.9)) if n1 else None, "N2_q90": float(np.quantile(n2, 0.9)),
                         "N2_n": len(n2), "evaluated": bool(C0),
                         "pass": bool(C0 and n1 and r["dA"] > np.quantile(n1, 0.9) and r["dA"] > np.quantile(n2, 0.9))}
            out["C2"] = {"A_pre_res": r["A_pre"], "rot_q95": float(np.quantile(lv, 0.95)), "pass": bool(r["A_pre"] > np.quantile(lv, 0.95))}
    blk = np.array([int(mm // 120) if np.isfinite(mm) else -1 for mm in mins])
    rows = []
    for bi, d in enumerate(days):
        for b in (0, 1):
            sel = (pdays == d) & (blk == b)
            groups = [np.flatnonzero(sel & (agents == x)) for x in sorted(set(agents[sel].tolist()))]
            groups = [gg for gg in groups if len(gg) >= K]
            if len(groups) < 3 or (bi == 0 and b == 0):
                continue
            vals = []
            for _ in range(B):
                V = np.array([unit(Zr[rng.choice(gg, K, replace=False)].mean(0)) for gg in groups])
                Cm = V @ V.T
                n = len(V)
                vals.append((Cm.sum() - n) / (n * (n - 1)))
            rows.append({"idx": 2 * bi + b, "A_res": float(np.mean(vals)), "N": len(groups)})
    if len(rows) >= 4:
        rho, p = stats.spearmanr([x["idx"] for x in rows], [x["A_res"] for x in rows])
        out["C3"] = {"rho": float(rho), "p": float(p), "pass": bool(rho > 0), "n_blocks": len(rows)}
    out["C4"] = reading_did(cu, st, Zr, present, pats, rng)
    return out


def both(per, key, field="pass"):
    v = [per[m].get(key, {}).get(field) for m in MODELS]
    if any(x is None for x in v):
        return "n/a"
    return "pass" if all(v) else ("fail" if not any(v) else "model-dependent")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--dry-run", type=int, default=None, help="run the pipeline on a non-holdout goal period instead")
    a = ap.parse_args()
    held = set(load_holdout()["goal_periods_held_out"])
    if a.dry_run is not None:
        goal = a.dry_run
        if goal in held:
            sys.exit(f"--dry-run {goal}: that period is in the locked holdout; refusing.")
        tag, allow = f"confirm_r1b_dryrun_G{goal}", False
        ledger_status(strict=False)
    else:
        goal = TARGET
        if not (a.confirm and a.ack):
            sys.exit("This uses the locked holdout (#14). Refusing without --confirm --i-understand-this-uses-the-locked-holdout "
                     "(and Vivian's sign-off, logged in LOG.md).")
        assert goal in held
        must = [Path(__file__).resolve(), HERE / "CONFIRM_R1B.md", HERE.parent / "README.md", HERE / "h24stats.py",
                HERE / "explore.py", HERE.parent / "scheme/h24lib.py", HERE.parent / "scheme/build.py",
                HERE.parent / "scheme/extract_cu_text.py", ROOT / "infra/shared/style_resid.py", ROOT / "infra/shared/goal_fields.py"]
        if not committed_clean(must):
            sys.exit("refusing: commit confirm_r1b.py, CONFIRM_R1B.md, the card and the code it imports first")
        if not ledger_status(strict=True):
            sys.exit("refusing: holdout_ledger.check() reports a same-family prior run on #14; Vivian decides")
        tag, allow = f"confirm_r1b_G{goal}", True
    dest = H24 / tag
    dest.mkdir(parents=True, exist_ok=True)
    cal = pl.read_parquet(OUT / "calendar.parquet").filter(pl.col("goal_no") == goal).sort("pt_date")
    days = cal["pt_date"].to_list()
    win0, win_end = cal["win_start"][0], cal["win_end"][-1]
    if not allow:
        assert not any(holdout_mask(days, [goal] * len(days)))
    rng = np.random.default_rng(SEED)

    import extract_cu_text
    if not (dest / "cu_turns_text.parquet").exists():
        extract_cu_text.main(win0 - dt.timedelta(hours=1), win_end + dt.timedelta(minutes=5), dest)
    cu = pl.read_parquet(dest / "cu_turns_text.parquet")

    from build import compute_switch_on
    roster = pl.read_parquet(OUT / "roster.parquet")
    names = dict(zip(roster["agent"].to_list(), roster["name"].to_list()))
    pats = mention_regexes([{"id": x, "name": n} for x, n in zip(roster["agent"].to_list(), roster["name"].to_list())])
    st = (pl.read_parquet(OUT / "embeddings/statements.parquet").with_row_index("srow").filter(pl.col("goal_no") == goal)
          .join(roster.select("agent", "claude_code"), on="agent").filter(~pl.col("claude_code")).drop("claude_code").sort("t"))
    if not allow:
        assert not st["holdout"].any()
    present = sorted(st["agent"].unique().to_list())
    sw = compute_switch_on(goal, cu, win0, win_end, present, names, pats, st)
    sw.write_parquet(dest / "switch_on.parquet")
    day1 = sorted(st.filter(pl.col("pt_date") == days[0])["agent"].unique().to_list())
    switched = sw.filter(pl.col("role") == "switched", pl.col("agent").is_in(day1))["agent"].to_list()
    tau = dict(zip(sw["agent"].to_list(), sw["tau_offset_min"].to_list()))
    C0 = len(switched) >= 4 and len(switched) >= (2 / 3) * len(day1)
    out = {"goal_no": goal, "tag": tag, "predictions": PREDICTIONS, "n_present": len(present), "n_day1": len(day1),
           "C0": {"pass": bool(C0), "n_switched": len(switched), "n_day1": len(day1)}}

    flds = field_vectors(goal, allow)
    opens = dict(zip(cal["pt_date"].to_list(), cal["win_start"].to_list()))
    mins = np.array([(t - opens[d]).total_seconds() / 60 if d in opens else np.nan
                     for t, d in zip(st["t"].to_list(), st["pt_date"].to_list())])
    agents, pdays = st["agent"].to_numpy(), np.array(st["pt_date"].to_list())
    srow = st["srow"].to_numpy()
    per, sens, checks = {}, {}, {}
    for model in MODELS:
        W32 = np.load(EM.ED / f"statements_white32_{EM.MODELS[model]['suffix']}.npy", mmap_mode="r")
        X0 = np.asarray(W32[np.sort(srow)], np.float64)[np.argsort(np.argsort(srow))]
        Z, Zr = residual(X0, flds[model])
        per[model] = run_model(model, st, Z, Zr, mins, agents, pdays, days, switched, tau, C0, rng, cu, present, pats)
        S, sinfo = style_vectors(st, model)
        _, Zs = residual(S, flds[model])
        sens[model] = {"style_refit": sinfo, "C4_style": reading_did(cu, st, Zs, present, pats, rng)}
        if a.dry_run == 21:     # reproduce the round-1b G21 field (shared g-hat + chunks)
            f = dict(np.load(H24 / "G21/r1b" / f"field_{model}.npz"))
            checks[model] = {"cos_ghat_vs_r1b": float(unit(f["ghat"][:DIM].astype(np.float64)) @ unit(flds[model]["ghat"][:DIM])),
                             "n_chunks": [int(len(f["chunks"])), int(len(flds[model]["chunks"]))]}
    out["per_model"] = per
    out["sensitivity_style"] = sens
    out["checks"] = checks
    did = {m: per[m].get("C4", {}) for m in MODELS}
    if min(d.get("n", 0) for d in did.values()) < MIN_DID_EVENTS:
        c4 = "inconclusive (underpowered)"
    else:
        ok = [d["mean_did"] > 0 and d["perm_p"] < 0.05 for d in did.values()]
        c4 = "pass" if all(ok) else ("fail" if not any(ok) else "model-dependent")
    out["verdicts"] = {"C0": out["C0"]["pass"], "C1-r1b": both(per, "C1") if C0 else "not evaluated (C0 fails)",
                       "C2-r1b": both(per, "C2"), "C3-r1b": both(per, "C3"), "C4-r1b": c4}
    (dest / "confirm_r1b_results.json").write_text(json.dumps(out, indent=1, default=str))
    (dest / "_provenance.json").write_text(json.dumps({
        "built_by": "hypotheses/H24-forecast-coupling-switch/analysis/confirm_r1b.py", "git_commit": git_commit(),
        "inputs": [{"source": "ai-village", "revision": REVISION,
                    "tables": ["raw computer_use_turns/sessions (text sidecar)", "embeddings/statements",
                               "embeddings/statements_white32_{bge_small,gte_modernbert}", "embeddings/goals + goal_vectors",
                               "chat_text (goal/kickoff chunks, memory only)", "text_features + intentions_text (style)",
                               "placebo/r1b/field_<model>.npz"]}],
        "params": {"K": K, "B": B, "POST": POST, "DIM": DIM, "models": list(MODELS)},
        "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}, indent=1))
    print(json.dumps({"C0": out["C0"], "verdicts": out["verdicts"], "checks": checks,
                      "per_model": {m: {k: {kk: vv for kk, vv in v.items() if kk not in ("N1",)} for k, v in per[m].items()}
                                    for m in MODELS},
                      "style_C4": {m: sens[m]["C4_style"] for m in MODELS},
                      "style_refit": {m: sens[m]["style_refit"] for m in MODELS}}, indent=1, default=str)[:6000])


if __name__ == "__main__":
    main()
