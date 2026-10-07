"""Build data/processed/H140-degroot-readout-self-weight/G<NN>/ (per-row metadata and Gram terms; no text, no vectors).

Usage: uv run python hypotheses/H140-degroot-readout-self-weight/scheme/build.py [--period 38 ...]
  regime III (talk calls; #51 also timer wakes): 37, 38, 39, 40, 41, 42, 44, 51
  regime I/II (O2 only, chat mode, segment = PT day): 13, 16, 35, 36 (unit 36a only)
Files per period: rows.parquet (meta), gram_<tag>.parquet (Gram terms; primary tags bge, gte also carry the N1
cross-day surrogate batch products), items_<tag>.parquet (O4 matched-age items), wake_* for #51 wakes, counts.json.
Tags: bge, gte (style_resid32, goal/kickoff projection), bgeF (window-field projection variant), bgeW (white32).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h140scheme as S  # noqa: E402
from common import REVISION, git_commit  # noqa: E402

OUT = S.ROOT / "data/processed/H140-degroot-readout-self-weight"
VARIANTS = [("bge", "bge_small", "style_resid32", False, True, True), ("gte", "gte_modernbert", "style_resid32", False, True, True),
            ("bgeF", "bge_small", "style_resid32", True, False, True), ("bgeW", "bge_small", "white32", False, False, False)]


def write_set(d: Path, prefix: str, sk: S.Skeleton, variants) -> dict:
    cnt = {}
    sk.rows.write_parquet(d / f"{prefix}rows.parquet", compression="zstd")
    cnt[f"{prefix}rows"] = len(sk.rows)
    for tag, model, var, field, sur, items in variants:
        V = S.real_vectors(sk, model, var)
        g, it, _ = S.gram_rows(sk, V, model=model, field=field, with_items=items, with_sur=sur)
        g.write_parquet(d / f"{prefix}gram_{tag}.parquet", compression="zstd")
        if it is not None:
            it.write_parquet(d / f"{prefix}items_{tag}.parquet", compression="zstd")
    return cnt


def build(g: int) -> dict:
    t0 = time.time()
    d = OUT / f"G{g:02d}"
    d.mkdir(parents=True, exist_ok=True)
    if g in S.REG3:
        sk = S.build_skeleton(g)
        cnt = {"goal_no": g, "regime": sk.regime, "statements": len(sk.st)}
        cnt.update(write_set(d, "", sk, VARIANTS))
        r = sk.rows
        cnt["rows_in"] = int((r["pmode"] == "in").sum()); cnt["rows_in_z"] = int(((r["pmode"] == "in") & r["has_z"]).sum())
        cnt["rows_xreset"] = int((r["pmode"] == "xreset").sum())
        if g == 51:
            skw = S.build_skeleton(51, ps_kind="wakes")
            cnt.update(write_set(d, "wake_", skw, VARIANTS[:2]))
    else:
        sk = S.build_skeleton(g, only_units=S.REG12[g], chat_mode=True)
        cnt = {"goal_no": g, "regime": sk.regime, "statements": len(sk.st)}
        cnt.update(write_set(d, "", sk, VARIANTS[:2]))
    cnt["build_s"] = round(time.time() - t0, 1)
    (d / "counts.json").write_text(json.dumps(cnt, indent=1))
    return cnt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", type=int, action="append")
    a = ap.parse_args()
    periods = a.period or (list(S.REG3) + list(S.REG12))
    OUT.mkdir(parents=True, exist_ok=True)
    for g in periods:
        print(json.dumps(build(g)), flush=True)
    prov = {"built_by": "hypotheses/H140-degroot-readout-self-weight/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["pending_sets/G<NN> (talks, pending, wakes, wake_pending)", "chat_core", "producing_calls",
                                   "context_ledger_turns (ctx_pos, k_ctx, reset_consol, reset_forced, reset_session)",
                                   "embeddings/statements + chat_index", "statements_{style_resid32,white32}_<model>",
                                   "goal_vectors_<model> + goals", "whitening_<model>_<regime>", "statement_flags",
                                   "period_units"]}],
            "params": {"field_window_s": S.FIELD_WIN_S, "field_min": S.FIELD_MIN, "min_well": S.MIN_WELL, "n_sur": S.N_SUR,
                       "age_max_s": S.AGE_MAX_S, "periods": periods, "variants": [v[0] for v in VARIANTS]},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    pp = OUT / "_provenance.json"
    old = json.loads(pp.read_text()) if pp.exists() else {}
    old["scheme"] = prov
    pp.write_text(json.dumps(old, indent=1))


if __name__ == "__main__":
    main()
