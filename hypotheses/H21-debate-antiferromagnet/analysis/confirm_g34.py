"""H21 CONFIRMATORY test on the locked holdout: goal period #34 (2026-03-05 -> 03-16, regime II; "develop a
turn-based RPG together while voting out Easter Egg saboteurs"). WRITTEN 2026-10-03, NOT RUN.

!!! Running this consumes #34 for H21. #34 is held out (blocked by the NE30 window). Do not run until the card's
!!! "Confirmatory test (#34)" section is final, committed, and the run is signed off by Vivian.
!!! It refuses to run without BOTH --confirm and --i-understand-this-uses-the-locked-holdout.
!!! --dry-run exercises every code path on NON-holdout stand-ins and asserts that no holdout day is read:
!!!   (a) the label-extraction rule on #33 (2026-03-02 -> 03-05, regime II, the period just before #34);
!!!   (b) the detection pipeline (masking, embedding, whitening, statistics) on #12, with each debate as a
!!!       "day" and a seeded random minority of each debate's Opposition as stand-in "saboteurs".

Question. In #34 each agent privately rolls a d6 each day; a 1 makes it a saboteur that hides Easter eggs, and
the others vote suspected saboteurs out. Roles are hidden. If hidden roles act as a staggered field on content
(model 11 / model 10 two-sublattice), the saboteur minority should be anti-aligned with the villager majority in
whitened, agent-centred content space, and an UNSUPERVISED sublattice score should recover who the saboteurs were.

Pre-registered design (see ../README.md, "Confirmatory test (#34)"):
  Unit: agent-day (PT date) in #34. Agents with >= 2 public chat messages that day.
  Labels (ground truth, derived automatically, never inspected before the run): an agent-day is SABOTEUR if the
    agent's OWN intentions (session goals) or OWN chat messages that day match a saboteur self-identification
    pattern (SAB_PATTERNS) and no villager pattern; VILLAGER if they match VIL_PATTERNS or nothing; days matching
    both are AMBIGUOUS and dropped. Coverage gate: if < 4 saboteur agent-days are found, or the saboteur rate is
    < 1/24 of agent-days (expected 1/6), the test is UNTESTABLE (no verdict either way).
  Content: public chat only (intentions are the label source and are never used as content). Text masked for
    agent names (that day's roster), team/role words and game-role words (GAME_ROLE_WORDS), embedded with
    bge-small-en-v1.5 (CPU), whitened with the regime-II whitener (fitted on non-holdout statements, D = 32),
    agent-centred over #34, day-centred, unit-normalised.
  Primary statistic (unsupervised): minority-sublattice score q_i = - u_i . mean_{j != i} u_j, u = unit of the
    agent-centred day mean (NOT day-centred: the room's shared direction defines the majority sublattice). AUC(saboteur > villager) pooled over agent-days; null = labels permuted within
    day (counts fixed), 20,000 draws, one-sided.
  Secondary: (S1) exact recovery of the saboteur set by the size-k two-block partition maximising
    within-minus-cross cosine (chance 1/C(n,k) per day); (S2) supervised LOAO staggered order m_s, within-day
    permutation null; (S3) family placebo: the same AUC with the agents' lab as the "role", and the primary AUC
    with no agent-centring (if roles track labs the centred AUC should fall).
  Decision rule: SUPPORTED if AUC >= 0.60 and p < 0.05; FAILED if AUC < 0.55 or p > 0.20; otherwise MIXED.
  AMENDMENT (2026-10-03, after the G12 exploratory result and BEFORE any #34 run; primary unchanged):
    G12 showed no full-vector two-sublattice order even for ASSIGNED, PUBLIC sides, but a weak staggered moment along
    an a-priori text axis. Added (S4): an a-priori role axis a = unit(W(e(t_hide)) - W(e(t_find))) from two fixed
    templates (TEMPLATES below, masked like the content); score_i = unit(v_i - mean_{j != i} v_j) . a per agent-day;
    AUC(saboteur > villager) with the within-day permutation null. Credences lowered (see PREDICTIONS).

Usage:
  uv run --offline --with sentence-transformers python hypotheses/H21-debate-antiferromagnet/analysis/confirm_g34.py --dry-run
  uv run --offline --with sentence-transformers python .../confirm_g34.py --confirm --i-understand-this-uses-the-locked-holdout
Writes data/processed/H21-debate-antiferromagnet/confirm_g34/ (or confirm_g34_dryrun/).
"""
from __future__ import annotations

import datetime as dt
import json
import math
import os
import re
import sys
from itertools import combinations
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("POLARS_MAX_THREADS", "2")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
sys.path.insert(0, str(ROOT / "infra/shared"))
import afmlib as L  # noqa: E402
from common import git_commit, holdout_mask, load_whitener  # noqa: E402
from masking import build_masker  # noqa: E402

SH = ROOT / "data/processed/shared"
DRY = "--dry-run" in sys.argv
CONFIRM = "--confirm" in sys.argv and "--i-understand-this-uses-the-locked-holdout" in sys.argv
OUT = ROOT / "data/processed/H21-debate-antiferromagnet" / ("confirm_g34_dryrun" if DRY else "confirm_g34")
TARGET_GOAL, LABEL_STANDIN_GOAL, DETECT_STANDIN_GOAL = 34, 33, 12
MODEL = "BAAI/bge-small-en-v1.5"
SEED = 20261003

# ============================================================================ pre-registered (2026-10-03)
PREDICTIONS = {
    "P_C1_primary": "Unsupervised minority-sublattice score q recovers saboteur agent-days: AUC >= 0.60 with "
                    "within-day permutation p < 0.05. Credence ~30% as first written; AMENDED 2026-10-03 to ~10% after "
                    "G12 (no full-vector order even for assigned public sides; hidden private roles are weaker still).",
    "P_C2_recovery": "Exact recovery of the saboteur set above chance (Poisson-binomial p < 0.05). Credence ~20%; amended ~5%.",
    "P_C3_supervised": "Supervised LOAO staggered order m_s > 0, p < 0.05. Credence ~35%; amended ~10%.",
    "P_S4_template_axis": "ADDED 2026-10-03 (before any #34 run): a-priori role-axis score AUC > 0.5 with p < 0.05. "
                          "Credence ~20%. Reported as secondary; does not change the decision rule.",
    "P_C4_family": "Lab-as-role placebo AUC within its null (p > 0.05) and the centred primary AUC not lower than "
                   "the uncentred one by more than 0.05 (roles are not labs).",
    "decision": "SUPPORTED if AUC >= 0.60 and p < 0.05; FAILED if AUC < 0.55 or p > 0.20; else MIXED. UNTESTABLE if "
                "fewer than 4 saboteur agent-days are labelled or the labelled saboteur rate < 1/24.",
}
SAB_PATTERNS = [
    r"\bI(?:'m| am| was|'ve been| have been)\s+(?:a\s+|the\s+|today's\s+|one of the\s+)?saboteur\b",
    r"\bmy\s+(?:secret\s+|hidden\s+)?role\s+(?:today\s+|for today\s+)?is\s+(?:a\s+|the\s+)?saboteur\b",
    r"\bas\s+(?:a|the|today's)\s+saboteur\b",
    r"\b(?:I\s+)?rolled\s+(?:a\s+)?(?:1|one)\b(?![\d.])",
    r"\b(?:d6|die|dice)\s+(?:roll\s+)?(?:result\s+)?(?:is|was|=|:)\s*1\b(?![\d.])",
]
VIL_PATTERNS = [
    r"\b(?:I\s+)?rolled\s+(?:a\s+)?(?:[2-6]|two|three|four|five|six)\b(?![\d.])",
    r"\b(?:d6|die|dice)\s+(?:roll\s+)?(?:result\s+)?(?:is|was|=|:)\s*[2-6]\b(?![\d.])",
    r"\bI(?:'m| am)\s+(?:a\s+)?(?:villager|not\s+(?:a\s+)?saboteur)\b",
]
GAME_ROLE_WORDS = ["saboteur", "saboteurs", "villager", "villagers", "sabotage", "sabotaging", "sabotaged",
                   "rolled a 1", "rolled a 2", "rolled a 3", "rolled a 4", "rolled a 5", "rolled a 6", "d6", "dice roll"]
MIN_STATEMENTS, N_PERM = 2, 20000
TEMPLATES = ("I quietly added a hidden secret to the game code and I am not telling anyone about it.",
             "I am searching the game for hidden secrets so that I can find them and report them to everyone.")


# ============================================================================ helpers
def guard_no_holdout(pt_dates, goal_nos, what):
    if any(holdout_mask(list(pt_dates), list(goal_nos))):
        raise SystemExit(f"DRY-RUN SAFETY: holdout rows reached while loading {what}; aborting.")


def label_agent_days(goal):
    """Apply the pre-registered self-identification rule. Returns (labels df, coverage dict)."""
    cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("goal_no") == goal)
    if DRY:
        guard_no_holdout(cal["pt_date"], cal["goal_no"], f"calendar goal {goal}")
    days = set(cal["pt_date"].to_list())
    it = (pl.read_parquet(SH / "intentions.parquet", columns=["event_index", "t", "agent"])
          .with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("pt_date"))
          .filter(pl.col("pt_date").is_in(list(days)))
          .join(pl.read_parquet(SH / "intentions_text.parquet", columns=["event_index", "goal_text"]), on="event_index", how="left")
          .select("agent", "pt_date", pl.col("goal_text").alias("text")))
    ch = (pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "pt_date", "goal_no", "speaker_kind", "agent"])
          .filter((pl.col("goal_no") == goal) & (pl.col("speaker_kind") == "agent"))
          .join(pl.read_parquet(SH / "chat_text.parquet", columns=["message_id", "text"]), on="message_id", how="left")
          .select("agent", "pt_date", "text"))
    if DRY:
        guard_no_holdout(ch["pt_date"], [goal] * ch.height, "chat for labels")
    allt = pl.concat([it, ch])
    sab = re.compile("|".join(SAB_PATTERNS), re.IGNORECASE)
    vil = re.compile("|".join(VIL_PATTERNS), re.IGNORECASE)
    rows = []
    for (a, d), g in allt.group_by(["agent", "pt_date"]):
        texts = [t or "" for t in g["text"].to_list()]
        s = any(sab.search(t) for t in texts)
        v = any(vil.search(t) for t in texts)
        rows.append({"agent": int(a), "pt_date": d, "label": "ambiguous" if (s and v) else "saboteur" if s else "villager"})
    lab = pl.DataFrame(rows) if rows else pl.DataFrame(schema={"agent": pl.Int64, "pt_date": pl.String, "label": pl.String})
    n_sab = int((lab["label"] == "saboteur").sum()) if lab.height else 0
    cov = {"goal": goal, "agent_days": lab.height, "saboteur": n_sab,
           "ambiguous": int((lab["label"] == "ambiguous").sum()) if lab.height else 0,
           "saboteur_rate": n_sab / lab.height if lab.height else 0.0}
    cov["testable"] = (n_sab >= 4) and (cov["saboteur_rate"] >= 1 / 24)
    return lab, cov


def embed_masked(texts, names):
    """Masked embeddings of the texts, plus the two S4 role templates (last two rows)."""
    import torch
    torch.set_num_threads(2)
    from sentence_transformers import SentenceTransformer
    m = SentenceTransformer(MODEL, device="cpu")
    m.max_seq_length = 256
    mask = build_masker(names, extra_words=GAME_ROLE_WORDS)
    return m.encode([mask(t or "")[:2000] for t in list(texts) + list(TEMPLATES)], batch_size=64,
                    normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)


def unit_spins(X, agents, units, min_n, centre_agents=True):
    """Per (unit, agent) raw agent-centred window means V (units with >= 4 agents; unit -1 = outside any unit)."""
    Xc = L.agent_center(X, agents) if centre_agents else X
    out = {}
    for u in np.unique(units):
        if u == -1:
            continue
        ids, V, _ = L.window_means(Xc, agents, units == u, min_n)
        if len(ids) >= 4:
            out[u] = (ids, V)
    return out


def auc(scores, labels):
    """P(score_sab > score_vil) with ties = 1/2."""
    s1, s0 = scores[labels == 1], scores[labels == 0]
    if len(s1) == 0 or len(s0) == 0:
        return np.nan
    gt = (s1[:, None] > s0[None, :]).mean()
    eq = (s1[:, None] == s0[None, :]).mean()
    return float(gt + 0.5 * eq)


def detection_stats(spins_by_unit, role_by_unit, rng, axis=None):
    """role_by_unit: {unit: {agent: 1 (minority/saboteur) | 0}}. axis: optional a-priori role axis (S4)."""
    q, y, unit_of, q4 = [], [], [], []
    rec, p_rec, ms_list, ms_null_parts = 0, [], [], []
    for u, (ids, V) in spins_by_unit.items():
        roles = role_by_unit.get(u)
        if roles is None:
            continue
        keep = np.array([a in roles for a in ids])
        ids, V = ids[keep], V[keep]
        if len(ids) < 4:
            continue
        lab = np.array([roles[a] for a in ids])
        # minority-sublattice score in the uncentred frame (the room's shared direction defines the majority):
        # q_i = - u_i . mean_{j != i} u_j, u = unit(agent-centred mean); no unit-centring, so no self-leakage
        U = L.unit(V)
        tot = U.sum(0)
        q += [-(U[i] @ ((tot - U[i]) / (len(ids) - 1))) for i in range(len(ids))]
        if axis is not None:
            q4 += [L.unit(V[i] - V[np.arange(len(ids)) != i].mean(0)) @ axis for i in range(len(ids))]
        S = L.spins(V)
        y += lab.tolist()
        unit_of += [u] * len(ids)
        k = int(lab.sum())
        if 1 <= k < len(ids):
            eps = np.where(lab == 1, 1, -1)
            best, best_d = None, -np.inf
            for A in combinations(range(len(ids)), k):
                e = -np.ones(len(ids), dtype=int); e[list(A)] = 1
                d = L.delta_stat(S, e) if k >= 2 or len(ids) - k >= 2 else -np.inf
                if np.isfinite(d) and d > best_d:
                    best, best_d = e, d
            if best is not None:
                rec += int(np.array_equal(best, eps))
                p_rec.append(1 / math.comb(len(ids), k))
            ms_list.append(L.loao_sigma(V, eps).mean())
            ms_null_parts.append(np.array([L.loao_sigma(V, e).mean() for e in L.partitions(len(ids), k)]))
    q, y, unit_of = np.array(q), np.array(y), np.array(unit_of)
    q4 = np.array(q4)
    a_obs = auc(q, y)
    a4 = auc(q4, y) if len(q4) else np.nan
    null = np.zeros(N_PERM)
    null4 = np.zeros(N_PERM)
    for b in range(N_PERM):
        yp = y.copy()
        for u in np.unique(unit_of):
            m = unit_of == u
            yp[m] = rng.permutation(y[m])
        null[b] = auc(q, yp)
        if len(q4):
            null4[b] = auc(q4, yp)
    out = {"n_units": int(len(np.unique(unit_of))), "n_agent_units": int(len(y)), "n_minority": int(y.sum()),
           "auc": a_obs, "p_auc": L.p_upper(a_obs, null), "auc_null_q95": float(np.nanquantile(null, 0.95)),
           "recovered": rec, "recovered_expected_null": float(sum(p_rec)),
           "p_recovered": L.poisson_binomial_sf(rec, p_rec) if p_rec else np.nan}
    if len(q4):
        out.update({"S4_template_auc": a4, "S4_p": L.p_upper(a4, null4)})
    if ms_list:
        obs = float(np.mean(ms_list))
        nul = L.perm_null([{"all": a} for a in ms_null_parts], "all", N_PERM, rng.integers(1e9))
        out.update({"ms": obs, "p_ms": L.p_upper(obs, nul)})
    return out


def decide(res, cov):
    if not cov["testable"]:
        return "UNTESTABLE"
    a, p = res["auc"], res["p_auc"]
    if a >= 0.60 and p < 0.05:
        return "SUPPORTED"
    if a < 0.55 or p > 0.20:
        return "FAILED"
    return "MIXED"


# ============================================================================ main
def run_detection(goal, role_fn, regime, rng):
    cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("goal_no") == goal)
    if DRY:
        guard_no_holdout(cal["pt_date"], cal["goal_no"], f"calendar goal {goal}")
    roster = pl.read_parquet(SH / "roster.parquet").select("agent", "name", "lab")
    ch = (pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "pt_date", "goal_no", "speaker_kind", "agent"])
          .filter((pl.col("goal_no") == goal) & (pl.col("speaker_kind") == "agent"))
          .join(roster, on="agent", how="left").sort("t", "message_id"))
    if DRY:
        guard_no_holdout(ch["pt_date"], ch["goal_no"], "detection chat")
    text = dict(pl.read_parquet(SH / "chat_text.parquet", columns=["message_id", "text"])
                .filter(pl.col("message_id").is_in(ch["message_id"].to_list())).iter_rows())
    E = embed_masked([text.get(m) for m in ch["message_id"].to_list()], sorted(set(ch["name"].to_list())))
    Xall = load_whitener(regime, 32)(E).astype(np.float64)
    X, axis = Xall[:-2], L.unit(Xall[-2] - Xall[-1])
    units, roles = role_fn(ch)
    agents = ch["agent"].to_numpy().astype(int)
    sp = unit_spins(X, agents, units, MIN_STATEMENTS)
    res = detection_stats(sp, roles, rng, axis)
    # family placebo: lab (Anthropic vs other) as the "role"; and the primary without agent-centring
    lab_of = dict(zip(roster["agent"].to_list(), roster["lab"].to_list()))
    lab_roles = {u: {a: int(lab_of[a] == "Anthropic") for a in roles[u]} for u in roles}
    res["family_lab_placebo"] = detection_stats(sp, lab_roles, rng)
    res["uncentred"] = detection_stats(unit_spins(X, agents, units, MIN_STATEMENTS, centre_agents=False), roles, rng)
    return res


def main():
    if not (DRY or CONFIRM):
        sys.exit("Refusing to run: pass --dry-run (non-holdout stand-ins) or BOTH --confirm and "
                 "--i-understand-this-uses-the-locked-holdout (consumes #34 for H21).")
    if DRY and ("--confirm" in sys.argv):
        sys.exit("Choose one of --dry-run / --confirm.")
    rng = np.random.default_rng(SEED)
    OUT.mkdir(parents=True, exist_ok=True)
    report = {"written": "2026-10-03", "mode": "dry-run" if DRY else "CONFIRM", "predictions": PREDICTIONS,
              "git_commit": git_commit(), "run_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    if DRY:
        # (a) label rule on the non-holdout stand-in #33
        lab33, cov33 = label_agent_days(LABEL_STANDIN_GOAL)
        report["label_rule_standin_g33"] = cov33
        # (b) detection on #12 debates: minority = seeded random 1-2 members of each debate's Opposition
        deb = json.loads((ROOT / "data/processed/H21-debate-antiferromagnet/G12/debates_resolved.json").read_text())

        def role_fn(ch):
            name2a = dict(zip(ch["name"], ch["agent"]))
            ts = ch["t"].to_list()
            units = np.full(ch.height, -1)
            roles = {}
            for d in deb:
                t1 = dt.datetime.fromisoformat(d["t_first_speech"]); t2 = dt.datetime.fromisoformat(d["t_verdict"])
                for i, t in enumerate(ts):
                    if t1 <= t < t2:
                        units[i] = d["debate"]
                opp = [name2a[x] for x in d["opp"]]
                k = int(rng.integers(1, min(2, len(opp)) + 1))
                sab = set(rng.choice(opp, size=k, replace=False).tolist())
                roles[d["debate"]] = {name2a[x]: int(name2a[x] in sab) for x in d["gov"] + d["opp"]}
            return units, roles
        res = run_detection(DETECT_STANDIN_GOAL, role_fn, "I", rng)
        report["detection_standin_g12"] = res
        report["note"] = ("Dry run: stand-in minority = random 1-2 Opposition members per #12 debate; a positive AUC here "
                          "only shows the pipeline can see ASSIGNED public sides; it says nothing about #34.")
    else:
        lab, cov = label_agent_days(TARGET_GOAL)
        report["coverage"] = cov
        lab.write_parquet(OUT / "labels_g34.parquet")

        def role_fn(ch):
            day = np.array(ch["pt_date"].to_list())
            day_id = {d: k for k, d in enumerate(sorted(set(day)))}  # deterministic unit ids
            units = np.array([day_id[d] for d in day])
            m = {(r["agent"], r["pt_date"]): r["label"] for r in lab.iter_rows(named=True)}
            roles = {}
            for d in sorted(set(day)):
                u = day_id[d]
                roles[u] = {int(a): int(m[(int(a), d)] == "saboteur") for a in set(ch.filter(pl.col("pt_date") == d)["agent"].to_list())
                            if m.get((int(a), d)) in ("saboteur", "villager")}
            return units, roles
        res = run_detection(TARGET_GOAL, role_fn, "II", rng)
        report["detection"] = res
        report["verdict"] = decide(res, cov)
    (OUT / "result.json").write_text(json.dumps(report, indent=1, default=float))
    print(json.dumps({k: v for k, v in report.items() if k != "predictions"}, indent=1, default=float)[:4000])


if __name__ == "__main__":
    main()
