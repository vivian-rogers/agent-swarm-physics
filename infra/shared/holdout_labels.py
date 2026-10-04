"""Held-out label preparation (DQ10, authorized by Vivian 2026-10-04): Jev labels on LOCKED-HOLDOUT rows, kept apart.

Input preparation for frozen confirm scripts only. Nothing here analyses held-out data:
  - outputs go to data/processed/holdout_labels/ (never into the non-holdout shared tables), every row flagged holdout=True;
  - the script prints only completeness (expected, labelled, errors) and spend: no class counts, distributions or statistics;
  - every selected row is re-checked against the locked holdout (calendar flag or holdout_mask); non-holdout rows are refused.

  uv run --with httpx python infra/shared/holdout_labels.py behavior --cap 0.40   # v3.1 states, #51 holdout windows left unlabelled by HTTP 402
  uv run --with httpx python infra/shared/holdout_labels.py opptype  --cap 0.30   # H55 prerequisite: DQ2 opp_type on held-out opposes pairs
  uv run --with httpx python infra/shared/holdout_labels.py stance2  --cap X      # stance v2.1 on held-out reply pairs (only if its gate passed)
  uv run python infra/shared/holdout_labels.py spent

The behavior and opptype passes use the exact questions and states of their non-holdout pipelines (label_v3.questions,
reply_threading.questions_opp, stance_v2.questions). The key comes from load_key() and is never printed or written.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import asyncio  # noqa: E402
import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "behavior_states"))
from common import OUT, REVISION, git_commit, holdout_mask  # noqa: E402

HD = OUT.parent / "holdout_labels"
TASK_CAP = 3.00


def spent() -> float:
    s = 0.0
    for f in HD.glob("*.jsonl"):
        for line in f.open():
            try:
                s += float(json.loads(line).get("cost") or 0)
            except json.JSONDecodeError:
                pass
    return s


def is_holdout(dates, goals, flags=None) -> list[bool]:
    hm = holdout_mask([str(d) for d in dates], list(goals))
    return [bool(h) or bool(f) for h, f in zip(hm, flags if flags is not None else [False] * len(hm))]


def prov(name: str, params: dict):
    p = HD / "_provenance.json"
    pv = json.loads(p.read_text()) if p.exists() else {}
    pv[name] = {"built_by": "infra/shared/holdout_labels.py", "git_commit": git_commit(),
                "inputs": {"source": "ai-village", "revision": REVISION}, "params": {**params, "holdout_only": True},
                "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    p.write_text(json.dumps(pv, indent=1, default=str))


# ------------------------------------------------------------------------------------------------ behavior states v3.1
def behavior(cap: float, workers: int):
    import assemble_v3 as A
    import label_v3 as LV
    src = LV.BS / f"jev_all_{LV.TAXONOMY}.jsonl"
    errk, okk = set(), set()
    for line in LV.lines(src):
        try:
            j = json.loads(line)
        except json.JSONDecodeError:
            continue
        (okk if j.get("answers") else errk).add((j["pt_date"], j["agent"], j["w"]))
    keys = sorted(errk - okk)
    kd = pl.DataFrame({"pt_date": [k[0] for k in keys], "agent": [k[1] for k in keys], "w": [k[2] for k in keys]})
    cal = pl.read_parquet(OUT / "calendar.parquet", columns=["pt_date", "goal_no", "holdout"])
    kd = kd.join(cal, on="pt_date", how="left")
    ok = is_holdout(kd["pt_date"].to_list(), kd["goal_no"].to_list(), kd["holdout"].fill_null(False).to_list())
    if not all(ok):
        sys.exit(f"refusing: {len(ok) - sum(ok)} unlabelled windows are not in the holdout; they belong to the non-holdout pipeline")
    out = HD / "jev_holdout_behavior_v3.jsonl"
    done = LV.done_keys(out)
    f = A.features(kd.select("pt_date", "agent", "w"))
    expected = f.height
    s0 = spent()
    todo = expected - len(done & set(zip(f["pt_date"], f["agent"], f["w"])))
    print(f"behavior v3.1 holdout: expected {expected} windows (unlabelled after DQ3), {todo} to label; holdout-label spend so far ${s0:.4f}; cap ${cap}", flush=True)
    if todo and s0 < cap:
        key = LV.load_key()
        st = asyncio.run(LV.run(LV.iter_items(f, done), out, key, cap, s0, workers, False, todo))
        print(f"calls {st['n']}, errors {st['err']}, retries {st['retries']}, this run ${st['spent']:.4f}", flush=True)
    latest = {}
    for line in LV.lines(out):
        j = json.loads(line)
        k = (j["pt_date"], j["agent"], j["w"])
        if j.get("answers") or k not in latest:
            latest[k] = j
    rows = [LV.flatten(j) for j in latest.values()]
    T = pl.DataFrame(rows, infer_schema_length=None).with_columns(pl.lit(True).alias("holdout"), pl.lit(LV.TAXONOMY).alias("taxonomy"))
    T.write_parquet(HD / "behavior_states_v3_holdout.parquet", compression="zstd")
    n_lab = int(T["behavior"].is_not_null().sum())
    print(f"behavior v3.1 holdout: labelled {n_lab} / expected {expected}; label errors {T.height - n_lab}", flush=True)
    prov("behavior_states_v3_holdout", {"taxonomy": LV.TAXONOMY, "expected": expected, "labelled": n_lab, "cap_usd": cap,
                                        "join": "pt_date, agent, w onto behavior_states_v3 rows with labeled = false"})


# ------------------------------------------------------------------------------------------- reply pairs (opp, stance)
def holdout_pairs(stance_filter: str | None) -> pl.DataFrame:
    r = pl.read_parquet(OUT / "reply_pairs.parquet")
    r = r.filter((pl.col("pair_set") == "cand") & pl.col("p_reply").is_not_null() & (pl.col("p_reply") >= 0.5))
    hz = is_holdout(r["pt_date"].to_list(), r["goal_no"].to_list(), r["holdout"].fill_null(False).to_list())
    r = r.filter(pl.Series(hz))
    if stance_filter == "opposes":
        r = r.filter((pl.col("stance") == "opposes") & pl.col("opp_type").is_null())
    idx = pl.read_parquet(OUT / "chat_core.parquet", columns=["message_id"]).with_row_index("msg")
    r = (r.join(idx.select(pl.col("msg").alias("b"), pl.col("message_id").alias("B_message_id")), on="B_message_id")
         .join(idx.select(pl.col("msg").alias("a"), pl.col("message_id").alias("A_message_id")), on="A_message_id"))
    return r.unique(["B_message_id", "A_message_id"], keep="first").sort("B_message_id", "A_message_id")


async def _pairs_run(items, key, qs, out: Path, cap: float, workers: int, parse):
    import httpx
    import reply_threading as rt
    s = spent()
    sem = asyncio.Semaphore(workers)
    n = nerr = 0
    async with httpx.AsyncClient(http2=False) as client:
        with out.open("a") as fout:
            for k in range(0, len(items), workers * 8):
                if s >= cap:
                    print(f"cap reached before batch (${s:.4f} >= ${cap}); stopping", flush=True)
                    break
                batch = items[k:k + workers * 8]
                res = await asyncio.gather(*[rt._call(client, sem, it, key, qs) for it in batch])
                for it, r in zip(batch, res):
                    c = float(((r.get("usage") or {}).get("cost")) or 0)
                    s += c; n += 1; nerr += r.get("error") is not None
                    fout.write(json.dumps({"B_message_id": it["B_message_id"], "A_message_id": it["A_message_id"], **parse(r),
                                           "error": r.get("error"), "cost": c, "holdout": True}) + "\n")
                fout.flush()
    print(f"calls {n}, errors {nerr}; holdout-label spend ${s:.4f}", flush=True)


def pairs_pass(kind: str, cap: float, workers: int):
    import reply_threading as rt
    from label_windows import load_key
    if kind == "opptype":
        P = holdout_pairs("opposes")
        qs, out, field = rt.questions_opp(), HD / "opptype_holdout.jsonl", "opp_type"
        parse = lambda r: rt.parse(r, "opptype")  # noqa: E731
        tax = "opp-type-v1"
    else:
        import stance_v2 as sv
        res_file = sv.VAL / "results_confirm2__stance-v2.1.json"
        if not (res_file.exists() and json.loads(res_file.read_text())["gate"]["pass"]):
            sys.exit("stance2 holdout pass refused: the stance v2.1 gate has not passed")
        P = holdout_pairs(None)
        qs, out, field = sv.questions("stance-v2.1"), HD / "stance_v2_holdout.jsonl", "stance2"
        parse = sv.parse
        tax = "stance-v2.1"
    done = set()
    if out.exists():
        for line in out.open():
            j = json.loads(line)
            if j.get(field) is not None:
                done.add((j["B_message_id"], j["A_message_id"]))
    expected = P.height
    todo = P.filter(~pl.struct("B_message_id", "A_message_id").map_elements(
        lambda s: (s["B_message_id"], s["A_message_id"]) in done, return_dtype=pl.Boolean))
    print(f"{kind} holdout: expected {expected} pairs, {todo.height} to label; holdout-label spend so far ${spent():.4f}; cap ${cap}", flush=True)
    if todo.height and spent() < cap:
        key = load_key()
        for lo in range(0, todo.height, 20000):
            part = todo.slice(lo, 20000)
            st = rt.make_states(part.select("b", "a", pl.lit("cand").alias("set"), pl.col("cand_rank").alias("rank")))
            ids = part.select("B_message_id", "A_message_id").rows()
            items = [{"state": s_["state"], "B_message_id": i[0], "A_message_id": i[1]} for s_, i in zip(st, ids)]
            asyncio.run(_pairs_run(items, key, qs, out, cap, workers, parse))
            if spent() >= cap:
                break
    recs = {}
    for line in out.open():
        j = json.loads(line)
        k = (j["B_message_id"], j["A_message_id"])
        if j.get(field) is not None or k not in recs:
            recs[k] = j
    T = pl.DataFrame(list(recs.values()), infer_schema_length=None).with_columns(pl.lit(True).alias("holdout"), pl.lit(tax).alias("taxonomy"))
    T = T.join(P.select("B_message_id", "A_message_id", "pt_date", "goal_no", "regime", "b_agent", "a_agent", "a_kind", "room"),
               on=["B_message_id", "A_message_id"], how="left")
    name = "opptype_holdout" if kind == "opptype" else "reply_stance_v2_holdout"
    T.write_parquet(HD / f"{name}.parquet", compression="zstd")
    n_lab = int(T[field].is_not_null().sum())
    print(f"{kind} holdout: labelled {n_lab} / expected {expected}; label errors {T.height - n_lab}", flush=True)
    prov(name, {"taxonomy": tax, "expected": expected, "labelled": n_lab, "cap_usd": cap,
                "scope": "reply_pairs pair_set=cand, p_reply>=0.5, locked holdout" + (", DQ2 stance=opposes, opp_type null" if kind == "opptype" else "")})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["behavior", "opptype", "stance2", "spent"])
    ap.add_argument("--cap", type=float, default=0.30)
    ap.add_argument("--workers", type=int, default=12)
    a = ap.parse_args()
    HD.mkdir(parents=True, exist_ok=True)
    if a.cmd == "spent":
        print(f"holdout-label spend ${spent():.4f}")
        return
    if a.cap > TASK_CAP:
        sys.exit(f"cap above the ${TASK_CAP} task cap")
    if a.cmd == "behavior":
        behavior(a.cap, min(a.workers, 16))
    else:
        pairs_pass(a.cmd, a.cap, a.workers)


if __name__ == "__main__":
    main()
