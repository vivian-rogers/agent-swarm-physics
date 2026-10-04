"""H37 CONFIRMATORY test on the locked holdout: goal period #34 (2026-03-05 -> 03-16, regime II; "develop a
turn-based RPG together while voting out Easter Egg saboteurs"). WRITTEN 2026-10-04, NOT RUN.

!!! Running this consumes #34 for H37. #34 is held out (blocked by the NE30 window) and is already the target of
!!! unrun confirmatory scripts of H01, H05, H07, H12, H19 and H21. Holdout reuse policy (hypotheses/holdout.md):
!!!   1. H37's predictions and this script must be committed before the run;
!!!   2. H37's observable is a different data modality: zero-shot Jev STANCE labels on reply pairs (agree / support /
!!!      neutral / oppose / undermine). Nobody has computed stance labels on #34. (H21 uses embedding content; the
!!!      others use activity timing, rooms, repos or embeddings.) H37 shares H21's saboteur GROUND-TRUTH rule
!!!      (self-identification patterns, imported from H21's script), which is a label, not an observable;
!!!   3. the reuse is disclosed in both cards (H37 here; H21 to be told) and in LOG.md.
!!! It refuses to run without BOTH --confirm and --i-understand-this-uses-the-locked-holdout.
!!! The confirmatory run sends #34 chat text to the Jev API (OpenRouter; approved by Vivian for H37 labelling) with
!!! its own spend cap (--max-usd, default 0.50; expected ~$0.35 for ~9k pairs).
!!! --dry-run exercises every code path on NON-holdout stand-ins and makes NO API call:
!!!   (a) the ground-truth label rule on #33 (2026-03-02 -> 03-05, regime II, the period just before #34);
!!!   (b) the detection pipeline on #26 (cached H37 Jev labels), with a seeded random 1/6 of agent-days as stand-in
!!!       "saboteurs": once as is (a null: AUC ~ 0.5 expected) and with planted effects (stand-ins' received soft
!!!       stance shifted by -0.1 and -0.3), to show the pipeline detects a planted signal and how large it must be.

Question. Saboteurs hide Easter eggs; villagers try to find and vote them out. If conflict lives in stance, the
saboteur agent-days should stand out in the signed reply graph: villagers' replies to suspected saboteurs turn
negative (accusation) and saboteurs' replies may deflect or undermine.

Pre-registered design (card "Confirmatory test (#34)"; written 2026-10-04 before any #34 data):
  Pairs: H37's two constructions (addressed reply 30 min; adjacent reply 5 min), all #34 rooms, agent messages only.
  Labels: Jev stance-v1, exactly label_stance.py's prompt and truncation; soft stance s_e; responds >= 0.5.
  Ground truth: H21's self-identification rule (agent's own intentions or chat that day; ambiguous days dropped).
    UNTESTABLE if < 4 saboteur agent-days or saboteur rate < 1/24.
  Unit: agent-day (PT) with >= 3 received labelled replies (received score) / >= 3 given (given score).
  Scores (two-way FE over the whole period with agent-day target and speaker effects):
    PRIMARY   suspicion_received(i, d) = -z of i's agent-day TARGET effect (how others treat i that day), z within day.
    SECONDARY suspicion_given(i, d)    = -z of i's agent-day SPEAKER effect; combined = mean of the two z's.
  Statistic: AUC(saboteur > villager), pooled over agent-days; null = labels permuted within day (counts fixed),
    20,000 draws, one-sided.
  Decision: SUPPORTED if primary AUC >= 0.60 and p < 0.05; FAILED if AUC < 0.55 or p > 0.20; else MIXED.
  Secondary (reported, not decisive): daily two-camp ground state of the residual stance graph; fraction of
    saboteur agent-days in the minority camp vs chance (blind by construction to a pure "everyone distrusts i"
    target effect, which the residual removes; it sees only pair structure such as saboteur cliques);
    f_neg on replies to saboteurs vs villagers.

Usage:
  uv run python hypotheses/H37-stance-spins/analysis/confirm_g34.py --dry-run
  uv run --with httpx python hypotheses/H37-stance-spins/analysis/confirm_g34.py --confirm --i-understand-this-uses-the-locked-holdout
Writes data/processed/H37-stance-spins/confirm_g34/ (or confirm_g34_dryrun/).
"""
from __future__ import annotations

import asyncio
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("POLARS_MAX_THREADS", "2")
import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
sys.path.insert(0, str(ROOT / "infra/shared"))
import h37lib as L  # noqa: E402
import h37data as D  # noqa: E402
from common import git_commit, holdout_mask  # noqa: E402

DRY = "--dry-run" in sys.argv
CONFIRM = "--confirm" in sys.argv and "--i-understand-this-uses-the-locked-holdout" in sys.argv
OUT = D.DATA / ("confirm_g34_dryrun" if DRY else "confirm_g34")
TARGET, LABEL_STANDIN, DETECT_STANDIN = 34, 33, 26
SEED = 20261004
N_PERM = 20000
MIN_REPLIES = 3


def h21_patterns():
    """H21's pre-registered self-identification patterns (imported constants; H21 code is not modified)."""
    src = (ROOT / "hypotheses/H21-debate-antiferromagnet/analysis/confirm_g34.py").read_text()
    ns: dict = {}
    for name in ("SAB_PATTERNS", "VIL_PATTERNS"):
        m = re.search(rf"^{name} = \[.*?^\]", src, re.S | re.M)
        exec(m.group(0), {}, ns)
    return ns["SAB_PATTERNS"], ns["VIL_PATTERNS"]


PREDICTIONS = {
    "C1_primary": "suspicion_received AUC >= 0.60 with within-day permutation p < 0.05. Credence 0.25 "
                  "(synthetic S5: AUC ~0.8 if accused saboteurs receive -1 logit stance; but villagers may not "
                  "identify saboteurs, and LLM politeness compresses negative stance).",
    "C2_given": "suspicion_given AUC > 0.5, p < 0.05 (saboteurs deflect or undermine). Credence 0.15.",
    "C3_combined": "combined AUC >= 0.60, p < 0.05. Credence 0.25.",
    "C4_minority_camp": "saboteur agent-days fall in the daily ground-state minority camp more often than chance "
                        "(descriptive). Credence 0.2.",
    "decision": "SUPPORTED if primary AUC >= 0.60 and p < 0.05; FAILED if AUC < 0.55 or p > 0.20; else MIXED. "
                "UNTESTABLE if fewer than 4 saboteur agent-days or rate < 1/24.",
}


def guard(pt_dates, goals, what):
    if DRY and any(holdout_mask(list(pt_dates), list(goals))):
        raise SystemExit(f"DRY-RUN SAFETY: holdout rows reached while loading {what}; aborting.")


def label_agent_days(goal):
    SAB, VIL = h21_patterns()
    sh = D.SHARED
    cal = pl.read_parquet(sh / "calendar.parquet").filter(pl.col("goal_no") == goal)
    guard(cal["pt_date"], cal["goal_no"], f"calendar {goal}")
    days = set(cal["pt_date"].to_list())
    it = (pl.read_parquet(sh / "intentions.parquet", columns=["event_index", "t", "agent"])
          .with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("pt_date"))
          .filter(pl.col("pt_date").is_in(list(days)))
          .join(pl.read_parquet(sh / "intentions_text.parquet", columns=["event_index", "goal_text"]), on="event_index", how="left")
          .select("agent", "pt_date", pl.col("goal_text").alias("text")))
    ch = (pl.read_parquet(sh / "chat_core.parquet", columns=["message_id", "pt_date", "goal_no", "speaker_kind", "agent"])
          .filter((pl.col("goal_no") == goal) & (pl.col("speaker_kind") == "agent"))
          .join(pl.read_parquet(sh / "chat_text.parquet", columns=["message_id", "text"]), on="message_id", how="left")
          .select("agent", "pt_date", "text"))
    guard(ch["pt_date"], [goal] * ch.height, "chat for labels")
    allt = pl.concat([it, ch])
    sab = re.compile("|".join(SAB), re.IGNORECASE); vil = re.compile("|".join(VIL), re.IGNORECASE)
    rows = []
    for (a, d), g in allt.group_by(["agent", "pt_date"]):
        texts = [t or "" for t in g["text"].to_list()]
        s = any(sab.search(t) for t in texts); v = any(vil.search(t) for t in texts)
        rows.append({"agent": int(a), "pt_date": d, "label": "ambiguous" if (s and v) else "saboteur" if s else "villager"})
    lab = pl.DataFrame(rows, schema={"agent": pl.Int64, "pt_date": pl.String, "label": pl.String})
    n_sab = int((lab["label"] == "saboteur").sum())
    cov = {"goal": goal, "agent_days": lab.height, "saboteur": n_sab, "ambiguous": int((lab["label"] == "ambiguous").sum()),
           "saboteur_rate": n_sab / lab.height if lab.height else 0.0}
    cov["testable"] = bool(n_sab >= 4 and cov["saboteur_rate"] >= 1 / 24)
    return lab, cov


def build_and_label_target(max_usd):
    """CONFIRM ONLY: #34 reply pairs (H37 constructions) and Jev stance labels with their own spend cap."""
    import build_pairs as BP
    import label_stance as LS
    assert CONFIRM and not DRY
    c = BP.load_chat([TARGET]).with_columns(pl.lit(False).alias("hold"))  # deliberate: confirmatory use of #34
    df, meta = BP.build_goal(c, TARGET)
    OUT.mkdir(parents=True, exist_ok=True)
    df.write_parquet(OUT / "pairs_G34.parquet", compression="zstd")
    items = LS.make_states(df)
    key = LS.load_key()
    jsonl = OUT / "labels_G34.jsonl"
    done = set()
    if jsonl.exists():
        for line in jsonl.open():
            done.add(json.loads(line)["pair_id"])
    items = [it for it in items if it["pair_id"] not in done]

    async def run():
        import httpx
        sem = asyncio.Semaphore(6); spent = sum(json.loads(l).get("cost") or 0 for l in jsonl.open()) if jsonl.exists() else 0.0
        async with httpx.AsyncClient() as client:
            with jsonl.open("a") as f:
                for k in range(0, len(items), 24):
                    res = await asyncio.gather(*[LS.call(client, sem, it, key) for it in items[k:k + 24]])
                    for it, r in zip(items[k:k + 24], res):
                        cost = float(((r.get("usage") or {}).get("cost")) or 0); spent += cost
                        f.write(json.dumps({"pair_id": it["pair_id"], **LS.parse(r), "error": r.get("error"), "cost": cost}) + "\n")
                    if spent >= max_usd:
                        print(f"spend cap ${max_usd} reached; stopping"); break
        return spent
    spent = asyncio.run(run())
    lab = pl.DataFrame([json.loads(l) for l in jsonl.open()], infer_schema_length=None).filter(pl.col("stance").is_not_null())
    lab = lab.with_columns((pl.col("p_agree") + pl.col("p_support") - pl.col("p_oppose") - pl.col("p_undermine")).alias("s_soft"),
                           pl.col("stance").replace_strict(D.SIGN, return_dtype=pl.Int8).alias("s_hard"))
    return df.join(lab, on="pair_id", how="inner"), {"pairs": meta, "spent_usd": spent}


def agent_day_scores(P):
    """Two-way FE over the period with agent-day speaker and target effects; z within day. Returns dict per (agent, day)."""
    P = P.filter(pl.col("responds") >= 0.5)
    days = sorted(set(P["pt_date"].to_list()))
    keys_t = list(zip(P["agent_a"].to_list(), P["pt_date"].to_list()))
    keys_s = list(zip(P["agent_b"].to_list(), P["pt_date"].to_list()))
    ut = sorted(set(keys_t)); us = sorted(set(keys_s))
    it = {k: n for n, k in enumerate(ut)}; is_ = {k: n for n, k in enumerate(us)}
    ti = np.array([it[k] for k in keys_t]); si = np.array([is_[k] for k in keys_s])
    s = P["s_soft"].to_numpy().astype(float)
    n = len(s)
    X = np.zeros((n, 1 + len(us) + len(ut))); X[:, 0] = 1
    X[np.arange(n), 1 + si] = 1; X[np.arange(n), 1 + len(us) + ti] = 1
    beta, *_ = np.linalg.lstsq(X, s, rcond=None)
    a = beta[1:1 + len(us)]; b = beta[1 + len(us):]
    nt = np.bincount(ti, minlength=len(ut)); ns = np.bincount(si, minlength=len(us))
    out = {}
    for d in days:
        kt = [k for k in ut if k[1] == d and nt[it[k]] >= MIN_REPLIES]
        ks = [k for k in us if k[1] == d and ns[is_[k]] >= MIN_REPLIES]
        if len(kt) >= 3:
            v = np.array([b[it[k]] for k in kt]); z = (v - v.mean()) / (v.std() + 1e-12)
            for k, zz in zip(kt, z):
                out.setdefault(k, {})["susp_received"] = float(-zz)
        if len(ks) >= 3:
            v = np.array([a[is_[k]] for k in ks]); z = (v - v.mean()) / (v.std() + 1e-12)
            for k, zz in zip(ks, z):
                out.setdefault(k, {})["susp_given"] = float(-zz)
    for k, v in out.items():
        vals = [v.get("susp_received"), v.get("susp_given")]
        vals = [x for x in vals if x is not None]
        v["susp_combined"] = float(np.mean(vals)) if vals else None
    return out


def auc_test(scores, labels, days, rng):
    s = np.array(scores, float); y = np.array(labels, int); d = np.array(days)
    ok = np.isfinite(s)
    s, y, d = s[ok], y[ok], d[ok]
    if y.sum() == 0 or (1 - y).sum() == 0:
        return {"auc": None, "n_sab": int(y.sum()), "n": int(len(y))}
    a = L.auc(s[y == 1], s[y == 0])
    null = []
    groups = [np.flatnonzero(d == dd) for dd in np.unique(d)]
    for _ in range(N_PERM):
        yp = y.copy()
        for g in groups:
            yp[g] = rng.permutation(y[g])
        null.append(L.auc(s[yp == 1], s[yp == 0]))
    null = np.array(null)
    return {"auc": float(a), "p": float((1 + np.sum(null >= a)) / (1 + N_PERM)), "n_sab": int(y.sum()), "n": int(len(y))}


def minority_camp(P, labels):
    """Daily ground state of the residual stance graph; P(saboteur in minority camp) vs the villagers' rate."""
    rows = []
    for d in sorted(set(P["pt_date"].to_list())):
        X = P.filter((pl.col("pt_date") == d) & (pl.col("responds") >= 0.5))
        if X.height < 20:
            continue
        agents = sorted(set(X["agent_a"].to_list()) | set(X["agent_b"].to_list()))
        ix = {a: k for k, a in enumerate(agents)}
        spk = np.array([ix[a] for a in X["agent_b"]]); tgt = np.array([ix[a] for a in X["agent_a"]])
        J, _ = L.residual_matrix(spk, tgt, X["s_soft"].to_numpy().astype(float), len(agents), nmin=2)
        x, _ = L.ground_state(J)
        minority = 1 if (x == 1).sum() < (x == -1).sum() else -1
        for a in agents:
            lab = labels.get((a, d))
            if lab in ("saboteur", "villager"):
                rows.append({"agent": a, "pt_date": d, "sab": lab == "saboteur", "in_minority": bool(x[ix[a]] == minority)})
    if not rows:
        return {}
    R = pl.DataFrame(rows)
    return {"P_minority_sab": float(R.filter(pl.col("sab"))["in_minority"].mean()) if R["sab"].any() else None,
            "P_minority_vil": float(R.filter(~pl.col("sab"))["in_minority"].mean()), "n_sab": int(R["sab"].sum()), "n": R.height}


def detect(P, labels, rng):
    sc = agent_day_scores(P)
    res = {}
    for key in ("susp_received", "susp_given", "susp_combined"):
        ks = [k for k in sc if sc[k].get(key) is not None and labels.get(k) in ("saboteur", "villager")]
        res[key] = auc_test([sc[k][key] for k in ks], [labels[k] == "saboteur" for k in ks], [k[1] for k in ks], rng)
    res["minority_camp"] = minority_camp(P, labels)
    sab_t = P.filter(pl.col("responds") >= 0.5).with_columns(
        pl.Series("sab_target", [labels.get((a, d)) == "saboteur" for a, d in zip(P.filter(pl.col("responds") >= 0.5)["agent_a"],
                                                                                   P.filter(pl.col("responds") >= 0.5)["pt_date"])]))
    res["f_neg_to"] = sab_t.group_by("sab_target").agg(pl.col("s_hard").eq(-1).mean().alias("f_neg"), pl.len().alias("n")).to_dicts()
    a = res["susp_received"].get("auc"); p = res["susp_received"].get("p")
    res["decision"] = ("UNTESTABLE" if a is None else "SUPPORTED" if (a >= 0.60 and p < 0.05) else
                       "FAILED" if (a < 0.55 or p > 0.20) else "MIXED")
    return res


def dry_run():
    rng = np.random.default_rng(SEED)
    out = {"mode": "dry-run (no holdout data, no API calls)", "predictions": PREDICTIONS}
    lab33, cov33 = label_agent_days(LABEL_STANDIN)
    out["label_rule_standin_G33"] = cov33
    P = D.load_pairs(DETECT_STANDIN)
    guard(P["pt_date"], P["goal_no"], "stand-in pairs")
    agents = sorted(set(P["agent_a"].to_list()) | set(P["agent_b"].to_list()))
    days = sorted(set(P["pt_date"].to_list()))
    labels = {(a, d): ("saboteur" if rng.random() < 1 / 6 else "villager") for a in agents for d in days}
    out["standin_G26_null"] = detect(P, labels, rng)
    for shift in (0.1, 0.3):
        planted = P.with_columns(pl.Series("s_soft", [s - shift if labels[(a, d)] == "saboteur" else s
                                                      for s, a, d in zip(P["s_soft"], P["agent_a"], P["pt_date"])]))
        out[f"standin_G26_planted_received_-{shift}"] = detect(planted, labels, rng)
    return out


def main():
    if not (DRY or CONFIRM):
        sys.exit("refusing to run: pass --dry-run, or BOTH --confirm and --i-understand-this-uses-the-locked-holdout "
                 "(after the predictions are committed and Vivian signs off)")
    OUT.mkdir(parents=True, exist_ok=True)
    if DRY:
        out = dry_run()
    else:
        max_usd = float(sys.argv[sys.argv.index("--max-usd") + 1]) if "--max-usd" in sys.argv else 0.50
        rng = np.random.default_rng(SEED)
        lab, cov = label_agent_days(TARGET)
        out = {"mode": "CONFIRMATORY (#34, locked holdout)", "predictions": PREDICTIONS, "label_coverage": cov}
        if not cov["testable"]:
            out["decision"] = "UNTESTABLE (label coverage)"
        else:
            P, meta = build_and_label_target(max_usd)
            out["build"] = meta
            labels = {(r["agent"], r["pt_date"]): r["label"] for r in lab.iter_rows(named=True)}
            out["result"] = detect(P, labels, rng)
            out["decision"] = out["result"]["decision"]
    out["git_commit"] = git_commit(); out["run_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    (OUT / "results.json").write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps(out, indent=1, default=str)[:4000])


if __name__ == "__main__":
    main()
