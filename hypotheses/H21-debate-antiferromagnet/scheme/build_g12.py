"""H21 scheme for G12 (debate week, 2025-09-01 -> 09-05): statement table + masked embeddings.

Inputs
- data/processed/shared/chat_core.parquet, chat_text.parquet (text read in memory only), roster.parquet,
  calendar.parquet, embeddings/chat_index.parquet (to link the stored unmasked embeddings).
- scheme/labels/g12_debates.json: derived structural labels (judge, teams, phase boundaries, winner, motion and
  verdict message ids). Derived by reading the chat BEFORE any alignment outcome was computed; see G12/README.md.

Outputs, data/processed/H21-debate-antiferromagnet/G12/
- statements.parquet   one row per agent chat message in #12: message_id, t, ts (s since period start), agent,
                       name, lab, length, debate, phase (pre | deb | post | other), team (+1 Gov, -1 Opp, 0 judge,
                       2 bench), is_verdict, chat_row (row in shared chat_bge_small.npy), emb_row
- emb_masked.npy       float16 (n x 384) bge-small-en-v1.5 embeddings of the MASKED text (names, role words)
- motions.npz          per held debate: embeddings of the motion (topic) and of pro/con templates of it
- _provenance.json
No text is written. Masked text exists only in memory.

Usage: uv run --offline --with sentence-transformers python hypotheses/H21-debate-antiferromagnet/scheme/build_g12.py
(env: HF_HUB_OFFLINE=1; <= 2 threads)
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("POLARS_MAX_THREADS", "2")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(HERE))
from common import REVISION, git_commit, holdout_mask  # noqa: E402
from masking import build_masker  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H21-debate-antiferromagnet/G12"
LABELS = HERE / "labels/g12_debates.json"
GOAL = 12
POST_MAX_MIN = 10  # post-verdict window: at most 10 min, never past the next debate's pre start or the day end
PRE_MAX_MIN = 15   # pre (sides and motion known, before the first speech): at most 15 min
MODEL = "BAAI/bge-small-en-v1.5"


def ts(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None


def extract_motion(text: str) -> str | None:
    """First quoted clause of a motion announcement (straight or curly quotes)."""
    for pat in (r"[“\"]((?:This House|TH|THW|THBT|THS|THP)[^”\"]{5,300})[”\"]",
                r"[“\"]([^”\"]{15,300})[”\"]"):
        m = re.search(pat, text or "")
        if m:
            return m.group(1).strip()
    return None


def main():
    lab = json.loads(LABELS.read_text())
    debates = lab["debates"]
    roster = pl.read_parquet(SH / "roster.parquet").select("agent", "name", "lab")
    cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("goal_no") == GOAL)
    assert not any(holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())), "G12 must be non-holdout"
    day_end = {r["pt_date"]: r["win_end"] for r in cal.iter_rows(named=True)}

    chat = (pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "pt_date", "goal_no", "speaker_kind", "agent", "length"])
            .filter((pl.col("goal_no") == GOAL) & (pl.col("speaker_kind") == "agent"))
            .join(roster, on="agent", how="left")
            .join(pl.read_parquet(SH / "embeddings/chat_index.parquet").with_row_index("chat_row"), on="message_id", how="left")
            .sort("t", "message_id"))
    name2agent = dict(zip(roster["name"], roster["agent"]))
    t0 = cal["win_start"].min()

    # ---- phase/debate/team assignment from the labels
    n = chat.height
    deb = np.full(n, -1, dtype=np.int16)
    phase = np.array(["other"] * n, dtype=object)
    team = np.full(n, 2, dtype=np.int8)
    tt = chat["t"].to_list()
    agents = chat["agent"].to_numpy()
    held = sorted([d for d in debates if d["held"]], key=lambda d: ts(d["t_first_speech"]))
    # phase rule (labels file, fixed before outcomes): pre = [max(t_lineup, t_motion, t_first_speech - 15 min), fs);
    # deb = [fs, verdict); post = [verdict, min(verdict + 10 min, next debate's pre start, day end))
    for d in held:
        d["_t_pre"] = max(ts(d["t_lineup"]), ts(d["t_motion"]), ts(d["t_first_speech"]) - dt.timedelta(minutes=PRE_MAX_MIN))
    for k, d in enumerate(held):
        t_v = ts(d["t_verdict"])
        day = (t_v - dt.timedelta(hours=7)).date().isoformat()
        cands = [t_v + dt.timedelta(minutes=POST_MAX_MIN), day_end[day]]
        if k + 1 < len(held):
            cands.append(held[k + 1]["_t_pre"])
        d["_t_post_end"] = min(cands)
    for d in held:
        t_pre, t_fs, t_v, t_pe = d["_t_pre"], ts(d["t_first_speech"]), ts(d["t_verdict"]), d["_t_post_end"]
        gov = {name2agent[x] for x in d["gov"]}
        opp = {name2agent[x] for x in d["opp"]}
        judge = name2agent[d["judge"]]
        for i in range(n):
            t = tt[i]
            ph = "pre" if t_pre <= t < t_fs else "deb" if t_fs <= t < t_v else "post" if t_v <= t < t_pe else None
            if ph is None:
                continue
            assert deb[i] == -1, "phase windows overlap"
            deb[i] = d["debate"]
            phase[i] = ph
            a = agents[i]
            team[i] = 1 if a in gov else -1 if a in opp else 0 if a == judge else 2
        d["t_teams"] = t_pre.isoformat()
        d["_t_post_end"] = t_pe.isoformat()
    verdict_ids = {d["verdict_message_id"] for d in held if d.get("verdict_message_id")}
    motion_ids = {d["debate"]: d["motion_message_id"] for d in held if d.get("motion_message_id")}

    # ---- masked embeddings (text in memory only)
    text = dict(pl.read_parquet(SH / "chat_text.parquet", columns=["message_id", "text"])
                .filter(pl.col("message_id").is_in(chat["message_id"].to_list() + list(motion_ids.values())))
                .iter_rows())
    mask = build_masker(sorted(set(chat["name"].to_list())))  # only the agents on #12's roster
    masked = [mask(text.get(m) or "")[:2000] for m in chat["message_id"].to_list()]

    import torch
    torch.set_num_threads(2)
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(MODEL, device="cpu")
    model.max_seq_length = 256
    E = model.encode(masked, batch_size=64, normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)

    # consistency check: our CPU pipeline vs the stored (MPS, unmasked) embeddings on unmasked text
    Es = np.load(SH / "embeddings/chat_bge_small.npy", mmap_mode="r")
    probe = list(range(0, n, max(1, n // 50)))
    Eu = model.encode([(text.get(chat["message_id"][i]) or "")[:2000] for i in probe], normalize_embeddings=True,
                      convert_to_numpy=True, show_progress_bar=False)
    rows = chat["chat_row"].to_numpy()
    cos_check = float(np.mean(np.sum(Eu * np.asarray(Es[rows[probe]], dtype=np.float32), axis=1)))
    print(f"CPU vs stored embedding cosine on unmasked probe: {cos_check:.4f}")
    n_changed = sum(1 for m, s in zip(chat["message_id"].to_list(), masked) if (text.get(m) or "")[:2000] != s)

    # ---- motion embeddings (topic + pro/con templates); motion text never stored
    mot = {}
    for d in held:
        mtxt = extract_motion(text.get(motion_ids.get(d["debate"])) or "")
        if not mtxt:
            print(f"debate {d['debate']}: motion not extracted")
            continue
        m = mask(mtxt)
        e = model.encode([m, f"I strongly support the motion: {m}. This should happen.",
                          f"I strongly oppose the motion: {m}. This should not happen."],
                         normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)
        mot[d["debate"]] = e

    OUT.mkdir(parents=True, exist_ok=True)
    st = chat.select("message_id", "t", "agent", "name", "lab", "length", "chat_row").with_columns(
        ((pl.col("t") - t0).dt.total_seconds()).alias("ts"),
        pl.Series("debate", deb), pl.Series("phase", phase.tolist()), pl.Series("team", team),
        pl.col("message_id").is_in(list(verdict_ids)).alias("is_verdict"),
        pl.Series("emb_row", np.arange(n, dtype=np.int32)))
    st.write_parquet(OUT / "statements.parquet", compression="zstd")
    np.save(OUT / "emb_masked.npy", E.astype(np.float16))
    np.savez(OUT / "motions.npz", debates=np.array(sorted(mot)), emb=np.stack([mot[k] for k in sorted(mot)]).astype(np.float32))
    (OUT / "debates_resolved.json").write_text(json.dumps(
        [{k: v for k, v in d.items() if k in ("debate", "held", "judge", "gov", "opp", "winner", "t_teams",
                                              "t_first_speech", "t_verdict", "_t_post_end")} for d in held], indent=1))
    prov = {"built_by": "hypotheses/H21-debate-antiferromagnet/scheme/build_g12.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["chat_core", "chat_text", "roster", "calendar", "embeddings/chat_index"]},
                       {"labels": "hypotheses/H21-debate-antiferromagnet/scheme/labels/g12_debates.json"}],
            "params": {"goal": GOAL, "post_max_min": POST_MAX_MIN, "pre_max_min": PRE_MAX_MIN, "model": MODEL, "device": "cpu",
                       "mask_tokens": ["someone (names)", "speaker (roles)"], "max_chars": 2000, "max_seq_length": 256,
                       "cpu_vs_stored_cos": cos_check, "n_messages": n, "n_masked_changed": n_changed},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    (OUT.parent / "_provenance.json").write_text(json.dumps({"G12": prov}, indent=1))
    print(st.group_by("phase").len(), f"masked {n_changed}/{n} messages changed")


if __name__ == "__main__":
    main()
