"""DQ10: reply stance v2 (design + pre-registration: infra/data-quality/stance_v2.md).

One zero-shot Jev choice question per DQ2 reply pair (A, B) that separates disagreement on the merits from task correction,
decline, coordination, questions, acknowledgments and information. Non-holdout only: held-out pairs are never sampled,
sent or labelled.

  uv run python infra/shared/stance_v2.py sample  [--which draft|fresh]   # blind sheet (gated text) + key; no Jev output
  uv run --with httpx python infra/shared/stance_v2.py label --phase draft|fresh|full [--limit N]
  uv run python infra/shared/stance_v2.py validate [--which draft|fresh]  # needs claude_labels_<which>.json
  uv run python infra/shared/stance_v2.py compile                         # reply_stance_v2.parquet + provenance (no API)

HARD SPEND CAP: the sum of usage.cost over every stance_v2/labels/*.jsonl stays below CAP_USD ($5.90; DQ10 task cap $6.00).
The total is printed before every batch. The key comes from label_windows.load_key() and is never printed or written.
Message text goes only to the Jev API and, for the blind sheets, to data/processed (gitignored).
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
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "behavior_states"))
from common import OUT, REVISION, git_commit, holdout_mask  # noqa: E402
import reply_threading as rt  # noqa: E402

SV = OUT / "stance_v2"
LABELS = SV / "labels"
VAL = SV / "validation"
SEED = 20261004
CAP_USD = 5.90          # script cap; DQ10 task cap is $6.00 over both jobs (job 2 makes no calls)
TASK_CAP = 6.00
WORKERS = 12
TAXONOMY = "stance-v2.1"   # default; stance-v2.0 (the failed draft prompt) stays selectable with --taxonomy
P_REPLY_MIN = 0.5

INSTR = ("Message B was posted after message A in the same group chat. Which class best describes what B does with respect "
         "to A? Judge B's substance toward A and ignore courtesy openers and sign-offs (e.g. 'great point, but ...' is judged "
         "by what follows). Use 'disagree' only for a dispute on the merits of something A claims, proposes, decides or argues. "
         "Fixing a detail, declining a request, or reporting something different without contesting A is not 'disagree'.")
CLASSES = {
    "agree": "B endorses A on the merits: agrees with A's claim, argument or opinion, supports or votes for A's proposal or decision, or says A is right. Thanks or praise alone is not agree.",
    "disagree": "B disputes A on the merits: contests A's claim, argument, opinion, plan, proposal, decision or vote, argues for an alternative instead of A's, or says A or A's work is wrong or bad. A dispute about what A said or wants, not a small factual fix.",
    "correct": "B fixes a detail in A without contesting A's overall point or plan: a fact, number, name, date, status, link, file or technical detail, or reports a bug or error in A's work.",
    "decline": "B declines, refuses, postpones or redirects a request, task, invitation or offer made in A, or says it cannot do it.",
    "coordinate": "B handles task logistics with A: accepts or confirms a request or assignment, claims or hands off work, reports doing what A asked, divides tasks, schedules, or sets next steps.",
    "ask": "B asks A's author a question about A, or asks for clarification, details or confirmation.",
    "acknowledge": "B only acknowledges, thanks, praises, congratulates or welcomes A, without taking a position on A's content.",
    "inform": "B gives information or a status update that takes no side on A, or B does not respond to A at all.",
}
# stance-v2.1 (Amendment 1, written after the v2.0 draft failed the gate, before the fresh sheet was drawn)
INSTR_21 = INSTR + (" Judge B's stance toward A itself, not toward third parties that A or B mention: if A criticizes something "
                    "and B joins in, B agrees with A.")
CLASSES_21 = dict(CLASSES)
CLASSES_21["disagree"] = ("B explicitly rejects or contests something A said or wants: says that A's claim, argument, plan, proposal, "
                          "decision or vote is wrong, should not be done, or should give way to B's alternative. A different report, "
                          "B's own new plan, or a next step that does not reject A is not disagree. A dispute about the merits, not a small factual fix.")
CLASSES_21["inform"] = ("B gives information or a status update that takes no side on A, including an observation or result that differs "
                        "from A's without saying A is wrong, or B does not respond to A at all.")
CLASSES_21["coordinate"] = CLASSES["coordinate"][:-1] + ", or takes over or redirects the work."
CLASSES_21["correct"] = ("B fixes a detail in A without contesting A's overall point or plan: B says a specific detail in A (a fact, number, "
                         "name, date, status, link, file or technical detail) is wrong or out of date while A's overall point stands, or reports a bug or error in A's work.")
TAXONOMIES = {"stance-v2.0": (INSTR, CLASSES), "stance-v2.1": (INSTR_21, CLASSES_21)}
CK = list(CLASSES)
SIGN = {"agree": 1, "disagree": -1}
GROUP4 = {"agree": "agree", "disagree": "disagree", "correct": "pushback", "decline": "pushback"}   # else "zero"
TO_DQ2 = {"agree": "supports", "disagree": "opposes", "correct": "opposes", "decline": "opposes", "ask": "asks"}  # else neutral
# validation strata (pre-registered): first match wins
STRATA_N = {"G12": 30, "OPP": 50, "ASK": 20, "NEU": 20, "SUP-I": 26, "SUP-II": 20, "SUP-III": 34}
STRATA_N_FRESH = {"G12": 30, "OPP": 60, "ASK": 8, "NEU": 10, "SUP-I": 14, "SUP-II": 8, "SUP-III": 20}   # Amendment 1: 150, enriched
FLAG_RULES = {"stance-v2.0": {"b_flag_conf_0.8": 0.8}, "stance-v2.1": {"b_flag_conf_0.8": 0.8, "c_flag_conf_0.6": 0.6}}
FLAG_CONF = 0.8


def questions(tax: str = TAXONOMY) -> dict:
    instr, classes = TAXONOMIES[tax]
    return {"stance2": {"type": "choice", "instructions": instr, "criteria": classes}}


# ---------------------------------------------------------------------------------------------------------- population
def population() -> pl.DataFrame:
    """Non-holdout DQ2 reply pairs: visible candidates with a DQ2 label and p_reply >= 0.5 (holdout re-masked here)."""
    r = pl.read_parquet(OUT / "reply_pairs.parquet")
    r = r.filter((pl.col("pair_set") == "cand") & pl.col("p_reply").is_not_null() & (pl.col("p_reply") >= P_REPLY_MIN)
                 & ~pl.col("holdout").fill_null(True))
    hm = holdout_mask(r["pt_date"].cast(pl.Utf8).to_list(), r["goal_no"].to_list())
    r = r.filter(~pl.Series(hm))
    # current chat_core row index (make_states keys on it); reply_pairs carries stable message ids
    idx = pl.read_parquet(OUT / "chat_core.parquet", columns=["message_id"]).with_row_index("msg")
    r = (r.join(idx.select(pl.col("msg").alias("b"), pl.col("message_id").alias("B_message_id")), on="B_message_id")
         .join(idx.select(pl.col("msg").alias("a"), pl.col("message_id").alias("A_message_id")), on="A_message_id"))
    r = r.unique(["B_message_id", "A_message_id"], keep="first").sort("B_message_id", "A_message_id")
    reg = r["regime"].cast(pl.Utf8)
    stratum = (pl.when(pl.col("goal_no") == 12).then(pl.lit("G12"))
               .when(pl.col("stance") == "opposes").then(pl.lit("OPP"))
               .when(pl.col("stance") == "asks").then(pl.lit("ASK"))
               .when(pl.col("stance") == "neutral").then(pl.lit("NEU"))
               .otherwise(pl.concat_str(pl.lit("SUP-"), pl.col("regime").cast(pl.Utf8))))
    return r.with_columns(stratum.alias("stratum"), reg.alias("regime_s"))


# -------------------------------------------------------------------------------------------------------------- sample
def sample(which: str = "draft"):
    P = population()
    excl = set()
    for f in rt.VAL.glob("key_*.parquet"):                       # DQ2's blind sheets (old taxonomy)
        k = pl.read_parquet(f)
        excl |= set(zip(k["b"].to_list(), k["a"].to_list()))
    used = set()
    for f in VAL.glob("key_*.parquet"):                          # earlier v2 sheets
        used |= set(pl.read_parquet(f)["B_message_id"].to_list())
    idx = pl.read_parquet(rt.RT / "msg_index.parquet")           # DQ2 keys use the pinned index
    ids = dict(idx.iter_rows())
    excl_ids = {ids.get(b) for b, a in excl}
    P = P.filter(~pl.col("B_message_id").is_in(list(excl_ids | used)))
    n_by = STRATA_N if which == "draft" else STRATA_N_FRESH
    parts = []
    for s, n in n_by.items():
        sub = P.filter(pl.col("stratum") == s)
        parts.append(sub.sample(min(n, sub.height), seed=SEED + (0 if which == "draft" else 7)))
    x = pl.concat(parts).unique("B_message_id", keep="first")    # one pair per B message
    x = x.sample(fraction=1.0, shuffle=True, seed=SEED + 11).with_row_index("vid")
    st = rt.make_states(x.select("b", "a", pl.lit("cand").alias("set"), pl.col("cand_rank").alias("rank")))
    VAL.mkdir(parents=True, exist_ok=True)
    with (VAL / f"sheet_{which}.jsonl").open("w") as f:          # gated text: data/processed only, never committed
        for vid, s in enumerate(st):
            f.write(json.dumps({"vid": vid, "A": s["state"]["message_A"], "B": s["state"]["message_B"]}) + "\n")
    Nst = dict(P.group_by("stratum").len().iter_rows())
    x = x.with_columns(pl.col("stratum").replace_strict(Nst, return_dtype=pl.Float64).alias("N_stratum"))
    x.select("vid", "b", "a", "B_message_id", "A_message_id", "stratum", "N_stratum", "regime_s", "goal_no", "stance",
             "stance_conf", "opp_type", "p_reply", "cand_rank").write_parquet(VAL / f"key_{which}.parquet")
    print(f"wrote sheet_{which}.jsonl ({x.height} items; strata {dict(x.group_by('stratum').len().iter_rows())}); key kept separately")


# -------------------------------------------------------------------- Amendment 2: two-phase second confirmation attempt
POOL_REST = 4000
F_MAX, H_MAX, O_PER = 45, 25, 20
CONFIRM2 = "confirm2"


def used_b() -> set:
    used = set()
    for f in VAL.glob("key_*.parquet"):
        used |= set(pl.read_parquet(f)["B_message_id"].to_list())
    return used


def pool2() -> pl.DataFrame:
    """Phase-1 pool (fixed by seed; written once): every OPP and G12 pair + a uniform 4,000 of the rest, unused B only."""
    path = VAL / "pool2.parquet"
    if path.exists():
        return pl.read_parquet(path)
    P = population()
    P = P.with_columns(pl.when(pl.col("stratum").is_in(["OPP", "G12"])).then(pl.col("stratum")).otherwise(pl.lit("REST")).alias("s1"))
    N1 = dict(P.group_by("s1").len().iter_rows())
    Q = P.filter(~pl.col("B_message_id").is_in(list(used_b())))
    rest = Q.filter(pl.col("s1") == "REST").sort("B_message_id", "A_message_id")
    rest = rest.sample(min(POOL_REST, rest.height), seed=SEED)
    X = pl.concat([Q.filter(pl.col("s1") != "REST"), rest])
    n1 = dict(X.group_by("s1").len().iter_rows())
    X = X.with_columns(pl.col("s1").replace_strict(N1, return_dtype=pl.Float64).alias("N_s1"),
                       pl.col("s1").replace_strict(n1, return_dtype=pl.Float64).alias("n1_s1"))
    X.write_parquet(path)
    print(f"pool2: {X.height} pairs (complete strata OPP/G12 minus used B; REST uniform {rest.height})")
    return X


def sample_confirm2(tax: str = "stance-v2.1"):
    """Phase-2 sheet from the labelled pool: cells s1 x {F, H, O}; weights N_cell / n2_cell. Prints no Jev output."""
    X = pool2()
    lab = labels_df(tax).select("B_message_id", "A_message_id", pl.col("stance2").alias("j"), "stance2_conf")
    X = X.join(lab, on=["B_message_id", "A_message_id"], how="inner")
    X = X.with_columns(pl.when((pl.col("j") == "disagree") & (pl.col("stance2_conf") >= 0.6)).then(pl.lit("F"))
                       .when(pl.col("j") == "disagree").then(pl.lit("H")).otherwise(pl.lit("O")).alias("c"))
    X = X.with_columns(pl.concat_str("s1", pl.lit("|"), "c").alias("cell"))
    n1c = dict(X.group_by("cell").len().iter_rows())
    X = X.with_columns((pl.col("N_s1") * pl.col("cell").replace_strict(n1c, return_dtype=pl.Float64) / pl.col("n1_s1")).alias("N_cell"))
    import numpy as np
    rng = np.random.default_rng(SEED + 23)

    def alloc(cls: str, total: int) -> dict:
        Ncell = {s1: float(X.filter(pl.col("cell") == f"{s1}|{cls}")["N_cell"].max() or 0) for s1 in ("OPP", "G12", "REST")}
        avail = {s1: n1c.get(f"{s1}|{cls}", 0) for s1 in Ncell}
        if sum(avail.values()) <= total:
            return avail
        out = {s1: min(avail[s1], 5) for s1 in Ncell}
        left = total - sum(out.values())
        tot = sum(Ncell.values())
        for s1 in sorted(Ncell, key=lambda k: -Ncell[k]):
            add = min(avail[s1] - out[s1], round(left * Ncell[s1] / tot) if tot else 0)
            out[s1] += max(add, 0)
        return out

    parts = []
    for cls, total in (("F", F_MAX), ("H", H_MAX)):
        for s1, n in alloc(cls, total).items():
            sub = X.filter(pl.col("cell") == f"{s1}|{cls}").sort("B_message_id", "A_message_id")
            if n and sub.height:
                parts.append(sub[np.sort(rng.choice(sub.height, size=min(n, sub.height), replace=False))])
    for s1 in ("OPP", "G12", "REST"):
        sub = X.filter(pl.col("cell") == f"{s1}|O").sort("B_message_id", "A_message_id")
        parts.append(sub[np.sort(rng.choice(sub.height, size=min(O_PER, sub.height), replace=False))])
    x = pl.concat(parts).unique("B_message_id", keep="first")
    x = x.sample(fraction=1.0, shuffle=True, seed=SEED + 29).with_row_index("vid")
    st = rt.make_states(x.select("b", "a", pl.lit("cand").alias("set"), pl.col("cand_rank").alias("rank")))
    with (VAL / f"sheet_{CONFIRM2}.jsonl").open("w") as f:
        for vid, s_ in enumerate(st):
            f.write(json.dumps({"vid": vid, "A": s_["state"]["message_A"], "B": s_["state"]["message_B"]}) + "\n")
    x.select("vid", "b", "a", "B_message_id", "A_message_id", pl.col("cell").alias("stratum"), pl.col("N_cell").alias("N_stratum"),
             "regime_s", "goal_no", "stance", "stance_conf", "opp_type", "p_reply", "cand_rank").write_parquet(VAL / f"key_{CONFIRM2}.parquet")
    print(f"wrote sheet_{CONFIRM2}.jsonl ({x.height} items); key kept separately (cell composition not printed)")


# --------------------------------------------------------------------------------------------------------------- Jev
def total_spent() -> float:
    s = 0.0
    for f in LABELS.glob("*.jsonl"):
        for line in f.open():
            try:
                s += float(json.loads(line).get("cost") or 0)
            except Exception:
                pass
    return s


def done_pairs(tax: str) -> set:
    out = set()
    for f in LABELS.glob("*.jsonl"):
        for line in f.open():
            try:
                j = json.loads(line)
            except json.JSONDecodeError:
                continue
            if j.get("stance2") is not None and j.get("taxonomy") == tax:
                out.add((j["B_message_id"], j["A_message_id"]))
    return out


def parse(res: dict) -> dict:
    a = (res.get("answers") or {}).get("stance2") or {}
    pr = a.get("probabilities") or {}
    return {"stance2": a.get("choice"), "stance2_conf": a.get("confidence"),
            **{f"p_{k}": (float(pr[k]) if isinstance(pr, dict) and k in pr else None) for k in CK}}


async def _run(items, key, cap, workers, jsonl, phase, tax):
    import httpx
    spent = total_spent()
    sem = asyncio.Semaphore(workers)
    qs = questions(tax)
    t0, nerr, step = time.time(), 0, workers * 8
    async with httpx.AsyncClient(http2=False) as client:
        with jsonl.open("a") as fout:
            for k in range(0, len(items), step):
                if spent >= cap:
                    print(f"HARD CAP reached before batch: ${spent:.4f} >= ${cap}; stopping", flush=True)
                    break
                batch = items[k:k + step]
                res = await asyncio.gather(*[rt._call(client, sem, it, key, qs) for it in batch])
                for it, r in zip(batch, res):
                    cost = float(((r.get("usage") or {}).get("cost")) or 0)
                    spent += cost
                    nerr += r.get("error") is not None
                    fout.write(json.dumps({"B_message_id": it["B_message_id"], "A_message_id": it["A_message_id"], "phase": phase,
                                           **parse(r), "error": r.get("error"), "cost": cost, "taxonomy": tax}) + "\n")
                fout.flush()
                if (k // step) % 25 == 0:
                    rate = (k + len(batch)) / max(1e-9, time.time() - t0)
                    print(f"  {k + len(batch)}/{len(items)}  total spent ${spent:.4f}  errors {nerr}  {rate:.1f}/s", flush=True)
                if nerr > 50 and nerr > 0.2 * (k + len(batch)):
                    print(f"too many errors ({nerr}); stopping (last error {res[-1].get('error')})", flush=True)
                    break
    return spent


def select(phase: str, pri_keep: list[int] | None = None) -> pl.DataFrame:
    if phase == "pool2":
        return pool2().select("b", "a", "B_message_id", "A_message_id", "cand_rank")
    if phase in ("draft", "fresh"):
        k = pl.read_parquet(VAL / f"key_{phase}.parquet")
        return k.select("b", "a", "B_message_id", "A_message_id", "cand_rank")
    P = population()                                             # full: III, #12, II, I; random within
    rng = np.random.default_rng(SEED)
    pri = (pl.when(pl.col("regime_s") == "III").then(0).when(pl.col("goal_no") == 12).then(1)
           .when(pl.col("regime_s") == "II").then(2).otherwise(3))
    P = P.with_columns(pri.alias("_pri"), pl.Series("_u", rng.random(P.height)))
    if pri_keep is not None:
        P = P.filter(pl.col("_pri").is_in(pri_keep))
    return P.sort("_pri", "_u").select("b", "a", "B_message_id", "A_message_id", "cand_rank")


def label(phase: str, limit: int | None, cap: float, workers: int, tax: str = TAXONOMY, pri_keep: list[int] | None = None):
    from label_windows import load_key
    if cap > TASK_CAP:
        sys.exit(f"cap above the ${TASK_CAP} DQ10 task cap")
    LABELS.mkdir(parents=True, exist_ok=True)
    x = select(phase, pri_keep)
    done = done_pairs(tax)
    if done:
        x = x.filter(~pl.struct("B_message_id", "A_message_id").map_elements(
            lambda s: (s["B_message_id"], s["A_message_id"]) in done, return_dtype=pl.Boolean))
    if limit:
        x = x.head(limit)
    print(f"phase {phase} [{tax}]: {x.height} pairs to label ({len(done)} labelled already); total spent so far ${total_spent():.4f}; cap ${cap}", flush=True)
    if x.is_empty():
        return
    key = load_key()
    CH = 20000
    spent = total_spent()
    for lo in range(0, x.height, CH):
        if spent >= cap:
            break
        part = x.slice(lo, CH)
        st = rt.make_states(part.select("b", "a", pl.lit("cand").alias("set"), pl.col("cand_rank").alias("rank")))
        ids = part.select("B_message_id", "A_message_id").rows()
        items = [{"state": s["state"], "B_message_id": i[0], "A_message_id": i[1]} for s, i in zip(st, ids)]
        fname = f"{phase}.jsonl" if tax == "stance-v2.0" else f"{phase}__{tax}.jsonl"
        spent = asyncio.run(_run(items, key, cap, workers, LABELS / fname, phase, tax))
    print(f"phase {phase} done; total spent across all runs ${total_spent():.4f}", flush=True)


def labels_df(tax: str = TAXONOMY) -> pl.DataFrame:
    recs = []
    for f in sorted(LABELS.glob("*.jsonl")):
        for line in f.open():
            try:
                j = json.loads(line)
            except json.JSONDecodeError:
                continue
            if j.get("stance2") is not None and j.get("taxonomy") == tax:
                recs.append(j)
    if not recs:
        return pl.DataFrame()
    df = pl.DataFrame(recs, infer_schema_length=None)
    return df.unique(["B_message_id", "A_message_id"], keep="first", maintain_order=True)


# ---------------------------------------------------------------------------------------------------------- validate
def kappa(y1, y2, w=None) -> float:
    return rt_kappa(y1, y2, w)


def rt_kappa(y1, y2, w=None):
    from reply_threading_validate import kappa as k
    return k(list(y1), list(y2), None if w is None else list(w))


def wilson(k: float, n: float) -> list:
    if n <= 0:
        return [float("nan")] * 2
    z, p = 1.96, k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [float(c - h), float(c + h)]


def precision_block(V: pl.DataFrame, pred: str, ref: str, cls: str, mask=None) -> dict:
    d = V if mask is None else V.filter(mask)
    sel = d.filter(pl.col(pred) == cls)
    n = sel.height
    k = int((sel[ref] == cls).sum())
    wn = float(sel["w"].sum()) if n else 0.0
    wk = float(sel.filter(pl.col(ref) == cls)["w"].sum()) if n else 0.0
    rel = d.filter(pl.col(ref) == cls)
    rec_k = int((rel[pred] == cls).sum())
    out = {"n_pred": n, "n_correct": k, "precision_raw": (k / n if n else None), "precision_raw_ci": wilson(k, n),
           "precision_reweighted": (wk / wn if wn else None), "n_ref": rel.height,
           "recall_raw": (rec_k / rel.height if rel.height else None),
           "recall_reweighted": (float(rel.filter(pl.col(pred) == cls)["w"].sum()) / float(rel["w"].sum()) if rel.height else None)}
    return out


def boot_prec(V: pl.DataFrame, pred: str, ref: str, cls: str, mask_col: str | None = None, B: int = 2000) -> list:
    """Stratified bootstrap CI of the reweighted precision (resample items within strata)."""
    rng = np.random.default_rng(SEED)
    groups = [g for _, g in V.group_by("stratum")]
    vals = []
    for _ in range(B):
        parts = [g[rng.integers(0, g.height, g.height)] for g in groups]
        d = pl.concat(parts)
        if mask_col:
            d = d.filter(pl.col(mask_col))
        sel = d.filter(pl.col(pred) == cls)
        if sel.height:
            vals.append(float(sel.filter(pl.col(ref) == cls)["w"].sum()) / float(sel["w"].sum()))
    return [float(np.quantile(vals, 0.025)), float(np.quantile(vals, 0.975))] if vals else [None, None]


def validate(which: str = "draft", tax: str = TAXONOMY):
    key = pl.read_parquet(VAL / f"key_{which}.parquet")
    raw = json.loads((VAL / f"ref_labels_{which}.json").read_text())["labels"]
    cl = pl.DataFrame([{"vid": int(r["vid"]), "c": r["stance2"], "c_amb": bool(r.get("ambiguous", False))} for r in raw],
                      schema={"vid": pl.UInt32, "c": pl.Utf8, "c_amb": pl.Boolean})
    assert set(cl["c"].unique().to_list()) <= set(CK), set(cl["c"].unique().to_list()) - set(CK)
    lab = labels_df(tax)
    V = (key.join(cl, on="vid").join(lab.select("B_message_id", "A_message_id", pl.col("stance2").alias("j"), "stance2_conf",
                                                *[f"p_{k}" for k in CK]), on=["B_message_id", "A_message_id"], how="inner"))
    # weights: population share of the stratum / sample share
    nst = dict(V.group_by("stratum").len().iter_rows())
    V = V.with_columns((pl.col("N_stratum") / pl.col("stratum").replace_strict(nst, return_dtype=pl.Float64)).alias("w"))
    V = V.with_columns(
        pl.col("j").replace_strict(SIGN, default=0, return_dtype=pl.Int8).alias("j_sign"),
        pl.col("c").replace_strict(SIGN, default=0, return_dtype=pl.Int8).alias("c_sign"),
        pl.col("j").replace_strict(GROUP4, default="zero", return_dtype=pl.Utf8).alias("j_g4"),
        pl.col("c").replace_strict(GROUP4, default="zero", return_dtype=pl.Utf8).alias("c_g4"),
        pl.col("c").replace_strict(TO_DQ2, default="neutral", return_dtype=pl.Utf8).alias("c_dq2"),
        ((pl.col("j") == "disagree") & (pl.col("stance2_conf") >= FLAG_CONF)).alias("j_flag"))
    V = V.with_columns(pl.when(pl.col("j_flag")).then(pl.lit("disagree")).otherwise(pl.lit("other")).alias("j_flagcls"))
    for name, thr in FLAG_RULES[tax].items():
        V = V.with_columns(pl.when((pl.col("j") == "disagree") & (pl.col("stance2_conf") >= thr)).then(pl.lit("disagree"))
                           .otherwise(pl.lit("other")).alias(name))
    res = {"which": which, "taxonomy": tax, "computed_at": dt.datetime.now(dt.timezone.utc).isoformat(), "n": V.height,
           "n_ambiguous_ref": int(V["c_amb"].sum()), "strata": {k: int(v) for k, v in nst.items()}}
    w = V["w"].to_list()
    res["kappa"] = {
        "8class_raw": kappa(V["j"], V["c"]), "8class_reweighted": kappa(V["j"], V["c"], w),
        "agree_raw": float((V["j"] == V["c"]).mean()),
        "agree_reweighted": float((V.filter(pl.col("j") == pl.col("c"))["w"].sum()) / V["w"].sum()),
        "sign_raw": kappa(V["j_sign"], V["c_sign"]), "sign_reweighted": kappa(V["j_sign"], V["c_sign"], w),
        "group4_raw": kappa(V["j_g4"], V["c_g4"]), "group4_reweighted": kappa(V["j_g4"], V["c_g4"], w),
        "dq2_4class_vs_ref_mapped_raw": kappa(V["stance"].cast(pl.Utf8), V["c_dq2"]),
        "dq2_4class_vs_ref_mapped_reweighted": kappa(V["stance"].cast(pl.Utf8), V["c_dq2"], w),
        "v2_mapped_to_dq2_vs_ref_mapped_raw": kappa(V["j"].replace_strict(TO_DQ2, default="neutral"), V["c_dq2"]),
        "8class_raw_unambiguous": kappa(V.filter(~pl.col("c_amb"))["j"], V.filter(~pl.col("c_amb"))["c"]),
    }
    res["per_class"] = {c: precision_block(V, "j", "c", c) for c in CK}
    res["disagree"] = {
        "hard": {**precision_block(V, "j", "c", "disagree"), "precision_reweighted_ci": boot_prec(V, "j", "c", "disagree")},
        "flag_conf_ge_0.8": {**precision_block(V, "j_flagcls", "c", "disagree"),
                             "precision_reweighted_ci": boot_prec(V, "j_flagcls", "c", "disagree")},
        "hard_unambiguous_ref": precision_block(V, "j", "c", "disagree", ~pl.col("c_amb")),
        "pushback_group": precision_block(V, "j_g4", "c_g4", "pushback"),
        "by_stratum": {s: precision_block(V, "j", "c", "disagree", pl.col("stratum") == s) for s in nst},
        "jev_disagree_ref_calls": {k: int(v) for k, v in V.filter(pl.col("j") == "disagree").group_by("c").len().iter_rows()},
        "ref_disagree_jev_calls": {k: int(v) for k, v in V.filter(pl.col("c") == "disagree").group_by("j").len().iter_rows()},
    }
    for name in FLAG_RULES[tax]:
        res["disagree"][name] = {**precision_block(V, name, "c", "disagree"), "precision_reweighted_ci": boot_prec(V, name, "c", "disagree")}
    hp = res["disagree"]["hard"]
    gates = {"a_hard_class": (hp["precision_reweighted"] or 0) >= 0.6}
    for name, thr in FLAG_RULES[tax].items():
        fp = res["disagree"][name]
        gates[name] = (fp["precision_reweighted"] or 0) >= 0.6 and fp["n_pred"] >= 15
    obs = {"a_hard_class": "stance2 == disagree", **{n: f"stance2 == disagree & stance2_conf >= {t}" for n, t in FLAG_RULES[tax].items()}}
    passed = [n for n, ok in gates.items() if ok]
    # if several pass, ship the least restrictive one (highest recall): hard class, then the lower threshold
    order = ["a_hard_class", "c_flag_conf_0.6", "b_flag_conf_0.8"]
    best = next((n for n in order if n in passed), None)
    res["gate"] = {**gates, "pass": bool(passed), "validated_rule": best, "validated_observable": obs.get(best),
                   "validated_conf_min": (0.0 if best == "a_hard_class" else FLAG_RULES[tax].get(best)) if best else None}
    # what the reference calls DQ2's opposes pairs, and what v2 calls them
    opp = V.filter(pl.col("stance") == "opposes")
    res["dq2_opposes"] = {"n": opp.height, "ref": {k: int(v) for k, v in opp.group_by("c").len().iter_rows()},
                          "jev_v2": {k: int(v) for k, v in opp.group_by("j").len().iter_rows()},
                          "dq2_opp_type_position_ref": {k: int(v) for k, v in opp.filter(pl.col("opp_type") == "position").group_by("c").len().iter_rows()}}
    # agreement by Jev confidence
    bins = [(0.8, 1.01), (0.5, 0.8), (0.0, 0.5)]
    res["by_conf"] = {f"{lo}-{hi}": {"n": int(d.height), "agree": float((d["j"] == d["c"]).mean()) if d.height else None,
                                     "kappa": kappa(d["j"], d["c"]) if d.height > 5 else None}
                      for lo, hi in bins for d in [V.filter(pl.col("stance2_conf").is_between(lo, hi, closed="left"))]}
    res["confusion_jev_rows_ref_cols"] = {a: {b: int(V.filter((pl.col("j") == a) & (pl.col("c") == b)).height) for b in CK} for a in CK}
    res["distribution"] = {"jev": {k: int(v) for k, v in V.group_by("j").len().iter_rows()},
                           "ref": {k: int(v) for k, v in V.group_by("c").len().iter_rows()}}
    res["cost_this_sheet"] = None
    out = VAL / (f"results_{which}.json" if tax == "stance-v2.0" else f"results_{which}__{tax}.json")
    out.write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps({k: res[k] for k in ("n", "kappa", "gate", "distribution")}, indent=1, default=str))
    print(json.dumps(res["disagree"]["hard"], indent=1, default=str))
    for name in FLAG_RULES[tax]:
        print(name, json.dumps(res["disagree"][name], indent=1, default=str))
    print(f"wrote {out}")


# ----------------------------------------------------------------------------------------------------------- compile
def compile_table(tax: str = TAXONOMY):
    lab = labels_df(tax)
    if lab.is_empty():
        sys.exit("no stance v2 labels")
    rf = VAL / f"results_{CONFIRM2}__{tax}.json"
    gate = json.loads(rf.read_text())["gate"] if rf.exists() else {"pass": False, "validated_conf_min": None}
    if not gate.get("pass"):
        print(f"compile skipped: the pre-registered gate has not passed for {tax} (see {rf.name}); no shared table is written")
        return
    conf_min = gate.get("validated_conf_min")
    P = population()
    keep = ["B_message_id", "A_message_id", "b_agent", "a_kind", "a_agent", "room", "pt_date", "goal_no", "regime",
            "cand_rank", "parent", "p_reply", "stance", "stance_conf", "opp_type"]
    T = P.select(keep).rename({"stance": "dq2_stance", "stance_conf": "dq2_stance_conf", "opp_type": "dq2_opp_type"})
    L = lab.select("B_message_id", "A_message_id", "phase", "stance2", "stance2_conf", *[f"p_{k}" for k in CK], "cost")
    T = T.join(L, on=["B_message_id", "A_message_id"], how="left")
    pr = [f"p_{k}" for k in CK]
    T = T.with_columns(pl.col("stance2").is_not_null().alias("labelled"),
                       *[pl.col(c).cast(pl.Float32) for c in pr + ["stance2_conf", "cost"]])
    T = T.with_columns(pl.col("stance2").replace_strict(SIGN, default=0, return_dtype=pl.Int8).alias("s2_sign"),
                       (pl.col("p_agree") - pl.col("p_disagree")).alias("s2_soft"),
                       (pl.col("p_disagree") + pl.col("p_correct") + pl.col("p_decline")).alias("p_pushback"),
                       ((pl.col("stance2") == "disagree") & (pl.col("stance2_conf") >= FLAG_CONF)).alias("disagree_conf"),
                       ((pl.col("stance2") == "disagree") & (pl.col("stance2_conf") >= (conf_min if conf_min is not None else 2.0))).alias("disagree_validated"),
                       pl.col("stance2").cast(pl.Enum(CK)), pl.lit(False).alias("holdout"))
    T = T.with_columns(pl.when(pl.col("labelled")).then(pl.col("s2_sign")).alias("s2_sign"),
                       pl.when(pl.col("labelled")).then(pl.col("disagree_conf")).alias("disagree_conf"),
                       pl.when(pl.col("labelled")).then(pl.col("disagree_validated")).alias("disagree_validated"))
    # post hoc (Amendment 2 sensitivity): replies to automated messages (mostly the idling nudge) are where the reference's
    # "disagree" calls are least secure; conflict analyses should use the validated flag on agent or human parents only
    T = T.with_columns((pl.col("disagree_validated") & (pl.col("a_kind") != 2)).alias("disagree_validated_agent"))
    path = OUT / "reply_stance_v2.parquet"
    T.sort("B_message_id", "A_message_id").write_parquet(path, compression="zstd")
    gates = {f.stem: json.loads(f.read_text()).get("gate") for f in sorted(VAL.glob("results_*.json"))}
    params = {"model": "typesafe/jev-1.13", "taxonomy": tax, "validated_rule": gate.get("validated_observable"), "classes": CK, "population": "reply_pairs: pair_set=cand, DQ2-labelled, p_reply>=0.5, non-holdout (flag + holdout_mask)",
              "rows": T.height, "labelled": int(T["labelled"].sum()), "spent_usd_total": round(total_spent(), 4), "cap_usd": CAP_USD,
              "a_chars": rt.A_CHARS, "b_chars": rt.B_CHARS, "flag_conf": FLAG_CONF, "gates": gates, "zero_shot": True}
    prov_path = OUT / "_provenance.json"
    prov = json.loads(prov_path.read_text()) if prov_path.exists() else {}
    prov["reply_stance_v2"] = {"built_by": "infra/shared/stance_v2.py", "git_commit": git_commit(),
                               "inputs": {"source": "ai-village", "revision": REVISION,
                                          "tables": ["shared/reply_pairs", "shared/chat_core", "shared/chat_text (Jev only)", "shared/roster"]},
                               "params": params, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    prov_path.write_text(json.dumps(prov, indent=1, default=str))
    SV.mkdir(parents=True, exist_ok=True)
    (SV / "_provenance.json").write_text(json.dumps(prov["reply_stance_v2"], indent=1, default=str))
    print(json.dumps(params, indent=1, default=str))
    print(f"wrote {path} ({path.stat().st_size / 1e6:.1f} MB)")


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    s1 = sp.add_parser("sample"); s1.add_argument("--which", default="draft", choices=["draft", "fresh", CONFIRM2])
    s2 = sp.add_parser("label"); s2.add_argument("--phase", required=True, choices=["draft", "fresh", "pool2", "full"])
    s2.add_argument("--pri", help="full only: priority groups to label (0 regime III, 1 #12, 2 regime II, 3 regime I), e.g. 0,1,2")
    s2.add_argument("--limit", type=int); s2.add_argument("--cap", type=float, default=CAP_USD); s2.add_argument("--workers", type=int, default=WORKERS)
    s3 = sp.add_parser("validate"); s3.add_argument("--which", default="draft", choices=["draft", "fresh", CONFIRM2])
    s4 = sp.add_parser("compile"); sp.add_parser("spent")
    for x in (s2, s3, s4):
        x.add_argument("--taxonomy", default=TAXONOMY, choices=list(TAXONOMIES))
    a = ap.parse_args()
    if a.cmd == "sample":
        sample_confirm2() if a.which == CONFIRM2 else sample(a.which)
    elif a.cmd == "label":
        if a.phase == "full":
            rf = VAL / f"results_{CONFIRM2}__{a.taxonomy}.json"
            if not (rf.exists() and json.loads(rf.read_text())["gate"]["pass"]):
                sys.exit("full run refused: the pre-registered gate has not passed on the fresh sheet")
        label(a.phase, a.limit, a.cap, a.workers, a.taxonomy, [int(v) for v in a.pri.split(",")] if a.pri else None)
    elif a.cmd == "validate":
        validate(a.which, a.taxonomy)
    elif a.cmd == "compile":
        compile_table(a.taxonomy)
    elif a.cmd == "spent":
        print(f"stance v2 total spent ${total_spent():.4f} (cap ${CAP_USD})")


if __name__ == "__main__":
    main()
