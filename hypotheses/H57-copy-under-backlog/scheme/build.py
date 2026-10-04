"""H57 scheme: read-set skeletons and real-content outcomes, per goal period (non-holdout days only).

  uv run python hypotheses/H57-copy-under-backlog/scheme/build.py skeleton [--periods 40,51]
  uv run python hypotheses/H57-copy-under-backlog/scheme/build.py outcomes [--periods 40,51]

Outputs in data/processed/H57-copy-under-backlog/:
  skeleton/G<NN>_S.parquet   statements (structure, controls; no content)
  skeleton/G<NN>_P.parquet   read-set and placebo pairs (sid, msg, set, rank)
  statements.parquet         skeleton + real-content outcomes for every period (codes and numbers only)
  _provenance.json
No text is read or written (embeddings, hashed H34 markers and ids only).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h57core as C  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from common import REVISION, git_commit  # noqa: E402

SK = C.OUT / "skeleton"


def periods_all() -> list[int]:
    cc = C.chat().filter(~pl.col("holdout") & (pl.col("speaker_kind") == "agent"))
    return sorted(cc["goal_no"].unique().drop_nulls().to_list())


def do_skeleton(periods):
    SK.mkdir(parents=True, exist_ok=True)
    rows = []
    for g in periods:
        t0 = time.time()
        S, P = C.build_skeleton(g)
        if S.height == 0:
            continue
        S.write_parquet(SK / f"G{g:02d}_S.parquet", compression="zstd")
        P.write_parquet(SK / f"G{g:02d}_P.parquet", compression="zstd")
        a = S.filter(pl.col("k") > 0)
        rows.append({"goal_no": g, "n_stmt": S.height, "n_k1": a.height, "n_k1_ffull": a.filter(pl.col("f_full")).height,
                     "n_agents": a["agent"].n_unique(), "k_med": float(a["k"].median() or 0),
                     "k_q90": float(a["k"].quantile(0.9) or 0), "pairs": P.height, "sec": round(time.time() - t0, 1)})
        print(rows[-1], flush=True)
    pl.DataFrame(rows).write_parquet(SK / "skeleton_summary.parquet")


def do_outcomes(periods):
    parts = []
    for g in periods:
        fS, fP = SK / f"G{g:02d}_S.parquet", SK / f"G{g:02d}_P.parquet"
        if not fS.exists():
            continue
        t0 = time.time()
        S, P = pl.read_parquet(fS), pl.read_parquet(fP)
        msgs = np.unique(np.r_[S["msg"].to_numpy(), P["msg"].to_numpy()]).astype(np.int64)
        content = C.load_real_content(msgs)
        common = C.common_markers(g, S, content)
        kick = C.kickoff_vectors(g)
        o = C.outcomes(S, P, content, common=common, kick=kick, seed=g)
        flags = dq5_flags(S)
        parts.append(S.join(o, on="sid", how="left").join(flags, on="msg", how="left"))
        print(f"G{g:02d}: {S.height} statements, {P.height} pairs, {len(common)} common markers, "
              f"{time.time() - t0:.1f}s", flush=True)
    out = pl.concat(parts, how="diagonal_relaxed")
    f = C.OUT / "statements.parquet"
    if f.exists() and len(periods) < len(periods_all()):
        old = pl.read_parquet(f).filter(~pl.col("goal_no").is_in(periods))
        out = pl.concat([old, out], how="diagonal_relaxed")
    out.sort("goal_no", "sid").write_parquet(f, compression="zstd")
    provenance({"outcomes_periods": sorted(out["goal_no"].unique().to_list())})


def dq5_flags(S: pl.DataFrame) -> pl.DataFrame:
    cc = C.chat().select("msg", "crow")
    st = pl.read_parquet(C.ED / "statements.parquet", columns=["kind", "src_row"]).with_row_index("srow")
    st = st.filter(pl.col("kind") == "chat").select("srow", pl.col("src_row").cast(pl.UInt32).alias("crow"))
    fl = pl.read_parquet(C.SH / "statement_flags.parquet",
                         columns=["srow", "cross_echo_bge", "cross_echo_gte", "cross_echo_both", "templated_bge",
                                  "templated_gte", "templated_both", "self_repeat_both"])
    m = (S.select("msg").join(cc, on="msg", how="left").join(st, on="crow", how="left")
         .join(fl, on="srow", how="left").drop("crow", "srow"))
    return m


def provenance(params: dict):
    f = C.OUT / "_provenance.json"
    prov = json.loads(f.read_text()) if f.exists() else {}
    prov.update({
        "built_by": "hypotheses/H57-copy-under-backlog/scheme/build.py",
        "git_commit": git_commit(),
        "inputs": [{"source": "ai-village", "revision": REVISION,
                    "tables": ["shared/chat_core", "shared/context_ledger_turns", "shared/context_ledger_items",
                               "shared/calendar", "shared/period_units", "shared/roster", "shared/reply_pairs (parent)",
                               "shared/embeddings/chat_index + chat_{bge_small,gte_modernbert}.npy",
                               "shared/embeddings/whitening*_{I,II,III}.npz", "shared/embeddings/goals + goal_vectors*",
                               "shared/embeddings/statements + statement_flags",
                               "H34-idea-cascades/markers/uses.parquet (read-only)"]}],
        "params": {"talk_tol_s": C.TALK_TOL_S, "thr": C.THR, "common_frac": C.COMMON_FRAC,
                   "common_day1_agents": C.COMMON_DAY1_AGENTS, "K": [16, 32, 64], "holdout": "excluded (calendar + holdout_mask)",
                   **params},
        "built_at": dt.datetime.now(dt.timezone.utc).isoformat()})
    f.write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["skeleton", "outcomes"])
    ap.add_argument("--periods", default="")
    a = ap.parse_args()
    ps = [int(x) for x in a.periods.split(",") if x] or periods_all()
    C.OUT.mkdir(parents=True, exist_ok=True)
    if a.step == "skeleton":
        do_skeleton(ps)
        provenance({"skeleton_periods": ps})
    else:
        do_outcomes(ps)
