"""H83 scheme: newcomer and veteran chat statements with kickoff-projected style-free vectors, style vectors, tenure,
rooms and veteran read doses.

Inputs (shared tables only; no text is read or written):
  embeddings/statements.parquet (chat rows), statements_style_resid_period32_<model>.npy, statements_white32_<model>.npy,
  statement_flags.parquet (self_repeat_both), chat_index.parquet + text_features.parquet (20 f_* features),
  embeddings/goals.parquet + goal_vectors{,_gte_modernbert}.npy, regime whiteners, roster, calendar,
  context_ledger_items + call_windows (newcomer receiving calls).
Holdout: rows with calendar.holdout or common.holdout_mask are dropped before anything else and asserted absent.

Output: data/processed/H83-enculturation-of-newcomers/
  statements.parquet   one row per eligible chat statement: srow, agent, pt_date, goal_no, regime, room, lab, tau
                       (tenure day, null for founding agents), newcomer, veteran (on that day)
  vec_<m>.npy          kickoff-projected style_resid_period vectors (fp16, 32-d, unit), m in {bge, gte}
  vecraw_<m>.npy       the same without the kickoff projection (variant)
  white_<m>.npy        kickoff-projected white32 vectors (not style-residualized; variant)
  style.npy            20-d standardized style features (fp32)
  doses.parquet        newcomer x day: veteran agent items read, all agent items read (receiving calls that day)
  newcomers.parquet    agent, name, lab, joined, join_day (first calendar day >= joined), join_unit, join_holdout

  uv run python hypotheses/H83-enculturation-of-newcomers/scheme/build.py
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import git_commit, holdout_mask  # noqa: E402
from embed_models import load_whitener  # noqa: E402

SH = ROOT / "data/processed/shared"
ED = SH / "embeddings"
OUT = ROOT / "data/processed/H83-enculturation-of-newcomers"
DROP_AGENTS = {19, 28, 30}          # Claude Code; fine-tuned leaders
FOUNDING_DAY = "2025-04-02"
VET_TAU = 20                         # veteran on day d: tenure tau > 20 (or founding agent)
MODELS = {"bge": "bge_small", "gte": "gte_modernbert"}
FCOLS = ["f_log_chars", "f_lines", "f_bullet_share", "f_headers", "f_bold", "f_emoji", "f_excl", "f_ques", "f_urls",
         "f_backticks", "f_digit_share", "f_upper_share", "f_at", "f_emdash", "f_fps", "f_fpp", "f_sp", "f_colon",
         "f_word_len", "f_parens"]


def tenure_table(cal: pl.DataFrame, roster: pl.DataFrame) -> pl.DataFrame:
    """agent x calendar day -> tau (1 on the first calendar day >= joined). Founding agents get tau = null."""
    days = cal["pt_date"].sort().to_list()
    rows = []
    for a, j, left in roster.select("agent", "joined", "left").iter_rows():
        if a in DROP_AGENTS:
            continue
        for k, d in enumerate([d for d in days if d >= j and (left is None or d <= left)]):
            rows.append((a, d, None if j <= FOUNDING_DAY else k + 1))
    return pl.DataFrame(rows, schema={"agent": pl.Int8, "pt_date": pl.String, "tau": pl.Int32}, orient="row")


def kickoff_basis(goals: pl.DataFrame, G: np.ndarray, model: str, goal_no: int, regime: str, room, agent, day):
    """Orthonormal basis (32 x k) of the whitened goal_whole, kickoff, room kickoff and (#51) own role vectors."""
    W = load_whitener(regime, 32, model)
    g = goals.filter(pl.col("goal_no") == goal_no)
    sel = g.filter(pl.col("kind").is_in(["goal_whole", "kickoff"]))
    if room is not None:
        sel = pl.concat([sel, g.filter((pl.col("kind") == "kickoff_room") & (pl.col("room") == room))])
    if agent is not None:
        ag = g.filter((pl.col("kind") == "agent_goal") & (pl.col("agent") == agent)
                      & (pl.col("valid_from").is_null() | (pl.col("valid_from") <= day))
                      & (pl.col("valid_to").is_null() | (pl.col("valid_to") >= day)))
        sel = pl.concat([sel, ag])
    if sel.height == 0:
        return np.zeros((32, 0))
    X = W(G[sel["gid"].to_numpy()].astype(np.float32)).T          # 32 x k
    X = X / np.linalg.norm(X, axis=0, keepdims=True)
    Q, R = np.linalg.qr(X)
    keep = np.abs(np.diag(R)) > 1e-6
    return Q[:, keep]


def project(U: np.ndarray, keys: list, basis_of) -> np.ndarray:
    """Project out the basis of each statement's (goal, regime, room, agent, day) key; renormalize."""
    out = np.empty_like(U, dtype=np.float32)
    keys_arr = np.array([hash(k) for k in keys])
    uniq = {}
    for i, k in enumerate(keys):
        uniq.setdefault(k, []).append(i)
    for k, idx in uniq.items():
        B = basis_of(k)
        X = U[idx].astype(np.float32)
        if B.shape[1]:
            X = X - (X @ B) @ B.T
        n = np.linalg.norm(X, axis=1, keepdims=True)
        out[idx] = X / np.where(n > 0, n, 1.0)
    del keys_arr
    return out


def build(include_holdout: bool = False, write: bool = True):
    """include_holdout=True is for analysis/confirm.py only (in memory; write must be False)."""
    assert not (include_holdout and write), "held-out rows are never written to disk"
    if write:
        OUT.mkdir(parents=True, exist_ok=True)
    cal = pl.read_parquet(SH / "calendar.parquet").select("pt_date", "goal_no", "regime", "holdout")
    roster = pl.read_parquet(SH / "roster.parquet")
    st = pl.read_parquet(ED / "statements.parquet").with_row_index("srow")
    fl = pl.read_parquet(SH / "statement_flags.parquet", columns=["srow", "self_repeat_both"])
    st = st.join(fl, on="srow", how="left")
    st = st.filter((pl.col("kind") == "chat") & (pl.lit(include_holdout) | ~pl.col("holdout"))
                   & ~pl.col("agent").is_in(list(DROP_AGENTS)) & ~pl.col("self_repeat_both").fill_null(False))
    hm = np.array(holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list()))
    st = st.with_columns(pl.Series("held", hm))
    nonheld = ~hm
    if not include_holdout:
        st = st.filter(pl.Series(nonheld)).drop("held")
        held_days = set(cal.filter(pl.col("holdout").fill_null(False))["pt_date"].to_list())
        assert not set(st["pt_date"].unique().to_list()) & held_days, "held-out day in statements"
        assert not any(holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list()))

    # tenure, lab, veteran flag
    ten = tenure_table(cal, roster)
    st = st.join(ten, on=["agent", "pt_date"], how="left")
    st = st.join(roster.select("agent", "lab", "joined"), on="agent", how="left")
    st = st.with_columns((pl.col("joined") > FOUNDING_DAY).alias("newcomer_agent"),
                         (pl.col("tau").is_null() | (pl.col("tau") > VET_TAU)).alias("veteran"))
    # modal chat room of the agent that day
    mroom = (st.group_by("agent", "pt_date", "room").len().sort("len", descending=True)
             .group_by("agent", "pt_date").agg(pl.col("room").first().alias("day_room")))
    st = st.join(mroom, on=["agent", "pt_date"], how="left").sort("srow")

    # style features (chat_index row = src_row)
    ci = pl.read_parquet(ED / "chat_index.parquet").with_row_index("src_row")
    tf = pl.read_parquet(SH / "text_features.parquet", columns=["message_id", *FCOLS])
    sty = st.select("srow", "src_row").join(ci, on="src_row", how="left").join(tf, on="message_id", how="left")
    assert sty.height == st.height and sty["srow"].equals(st["srow"])
    F = np.nan_to_num(sty.select(FCOLS).to_numpy().astype(np.float64))
    fitm = ~st["held"].to_numpy() if include_holdout else np.ones(len(F), bool)   # standardization: non-holdout only
    lo, hi = np.quantile(F[fitm], 0.001, axis=0), np.quantile(F[fitm], 0.999, axis=0)
    F = np.clip(F, lo, hi)
    mu, sd = F[fitm].mean(0), F[fitm].std(0)
    F = (F - mu) / np.where(sd > 0, sd, 1.0)
    vecs = {"style": F.astype(np.float32)}
    if write:
        np.save(OUT / "style.npy", F.astype(np.float32))
    st = st.with_columns(pl.Series("message_id", sty["message_id"]))

    # vectors and kickoff projection
    goals = pl.read_parquet(ED / "goals.parquet")
    srows = st["srow"].to_numpy()
    reg = st["regime"].to_list(); gno = st["goal_no"].to_list(); rm = st["room"].to_list()
    ag = st["agent"].to_list(); dd = st["pt_date"].to_list()
    keys = [(g, r, ro, (a if g == 51 else None), (d if g == 51 else None)) for g, r, ro, a, d in zip(gno, reg, rm, ag, dd)]
    nbasis = {}
    for short, model in MODELS.items():
        G = np.load(ED / ("goal_vectors.npy" if model == "bge_small" else f"goal_vectors_{model}.npy"))
        cache = {}

        def basis_of(k, G=G, model=model, cache=cache):
            if k not in cache:
                g, r, ro, a, d = k
                cache[k] = kickoff_basis(goals, G, model, g, r, ro, a, d)
            return cache[k]
        R = np.load(ED / f"statements_style_resid_period32_{model}.npy", mmap_mode="r")[srows].astype(np.float32)
        Wt = np.load(ED / f"statements_white32_{model}.npy", mmap_mode="r")[srows].astype(np.float32)
        Rn = R / np.linalg.norm(R, axis=1, keepdims=True)
        V = project(Rn, keys, basis_of).astype(np.float16)
        vecs[f"vec_{short}"] = V
        if write:
            np.save(OUT / f"vecraw_{short}.npy", Rn.astype(np.float16))
            np.save(OUT / f"vec_{short}.npy", V)
            np.save(OUT / f"white_{short}.npy", project(Wt / np.linalg.norm(Wt, axis=1, keepdims=True), keys,
                                                         basis_of).astype(np.float16))
        nbasis[short] = {str(k[:3]): int(v.shape[1]) for k, v in list(cache.items())[:400]}
        print(short, "projected", len(cache), "keys", flush=True)

    # newcomers
    days = cal["pt_date"].sort().to_list()
    pu = pl.read_parquet(SH / "period_units.parquet").select("unit_id", "days")
    new = roster.filter((pl.col("joined") > FOUNDING_DAY) & ~pl.col("agent").is_in(list(DROP_AGENTS)))
    nrows = []
    for a, name, lab, j in new.select("agent", "name", "lab", "joined").iter_rows():
        jd = next((d for d in days if d >= j), None)
        g = cal.filter(pl.col("pt_date") == jd)["goal_no"][0] if jd else None
        jh = bool(holdout_mask([jd], [g])[0]) or bool(cal.filter(pl.col("pt_date") == jd)["holdout"].fill_null(False)[0])
        unit = None
        for u, ds in pu.iter_rows():
            if jd in ds:
                unit = u
                break
        nrows.append((a, name, lab, j, jd, g, unit, jh))
    newdf = pl.DataFrame(nrows, schema={"agent": pl.Int8, "name": pl.String, "lab": pl.String, "joined": pl.String,
                                        "join_day": pl.String, "join_goal": pl.Int8, "join_unit": pl.String,
                                        "join_holdout": pl.Boolean}, orient="row")
    if write:
        newdf.write_parquet(OUT / "newcomers.parquet")

    # doses: newcomer receiving calls (non-holdout) x items read
    vet_days = st.select("agent", "pt_date", "veteran").unique()
    nag = newdf["agent"].to_list()
    cw = (pl.scan_parquet(SH / "call_windows.parquet").select("turn_id", "agent", "pt_date", "holdout")
          .filter(pl.col("agent").is_in(nag) & (pl.lit(include_holdout) | ~pl.col("holdout"))).collect())
    if not include_holdout:
        hmc = np.array(holdout_mask(cw["pt_date"].to_list(), [None] * cw.height))
        cw = cw.filter(pl.Series(~hmc))
    it = (pl.scan_parquet(SH / "context_ledger_items.parquet").select("turn_id", "sender", "kind")
          .filter(pl.col("kind") == "agent").collect())
    j = it.join(cw, on="turn_id", how="inner")
    ten2 = ten.rename({"agent": "sender", "tau": "s_tau"})
    j = j.join(ten2, left_on=["sender", "pt_date"], right_on=["sender", "pt_date"], how="left")
    j = j.with_columns((pl.col("s_tau").is_null() | (pl.col("s_tau") > VET_TAU)).alias("from_vet"))
    doses = (j.group_by("agent", "pt_date").agg(pl.len().alias("items_agent"), pl.col("from_vet").sum().alias("items_vet"))
             .sort("agent", "pt_date"))
    if not include_holdout:
        assert not any(holdout_mask(doses["pt_date"].to_list(), [None] * doses.height))
    del vet_days
    keep = ["srow", "message_id", "agent", "t", "pt_date", "goal_no", "regime", "room", "day_room", "lab", "tau",
            "newcomer_agent", "veteran"] + (["held"] if include_holdout else [])
    if not write:
        return st.select(keep), vecs, newdf, doses
    doses.write_parquet(OUT / "doses.parquet")

    st.select(keep).write_parquet(OUT / "statements.parquet")
    prov = {"built_by": "hypotheses/H83-enculturation-of-newcomers/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": "838b4150303ca8228e8edb432d8b8ccae353d258",
                        "tables": ["shared/embeddings/statements", "shared/embeddings/statements_style_resid_period32_*",
                                   "shared/embeddings/statements_white32_*", "shared/statement_flags",
                                   "shared/text_features", "shared/embeddings/goals + goal_vectors*",
                                   "shared/embeddings/whitening*", "shared/roster", "shared/calendar",
                                   "shared/period_units", "shared/call_windows", "shared/context_ledger_items"]}],
            "params": {"drop_agents": sorted(DROP_AGENTS), "veteran_tau": VET_TAU,
                       "projection": "goal_whole + kickoff + kickoff_room(room) + own #51 agent_goal, regime-whitened",
                       "style": "20 H13 features, winsorized 0.1/99.9%, z-scored on non-holdout eligible chat",
                       "dedupe": "self_repeat_both dropped", "holdout": "excluded before any statistic"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat(), "n_statements": st.height}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print("statements", st.height, "newcomers", newdf.height, "dose rows", doses.height)


def main():
    build(include_holdout=False, write=True)


if __name__ == "__main__":
    main()
