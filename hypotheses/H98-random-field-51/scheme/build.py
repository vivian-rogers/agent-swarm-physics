"""H98 scheme: per unit (shared period_units; #51 non-holdout units and the regime-III contrast units 38a, 39, 40, 41),
agent-day states, time-split half states, 30-min window states (both embedding models, variants style_resid_period and
white32), role vectors (#51; whitened goal texts), and pair covariates (lab, DQ6 rival/opposed classes, ledger reads,
DQ2 reply intensity and soft stance). Codes and vectors only, no text.

    uv run python hypotheses/H98-random-field-51/scheme/build.py

Output: data/processed/H98-random-field-51/<unit>/{agent_day.parquet, S_<var>_<model>.npy, halves.parquet,
H1_<var>_<model>.npy, H2_<var>_<model>.npy, win.parquet, X_<var>_<model>.npy, pairs.parquet}, roles.parquet,
roles_<model>.npy, units.parquet, _provenance.json. Holdout asserted twice (calendar.holdout and common.holdout_mask).

allow_holdout is set only by analysis/confirm.py (guarded); it writes to a separate root.
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
from common import REVISION, git_commit, holdout_mask  # noqa: E402
from embed_models import load_whitener  # noqa: E402

SH = ROOT / "data/processed/shared"
ED = SH / "embeddings"
OUT = ROOT / "data/processed/H98-random-field-51"
MODELS = ("bge_small", "gte_modernbert")
VARIANTS = ("style_resid_period", "white32")
STMT_VAR = {"style_resid_period": "style_resid_period32", "white32": "white32"}
CONTRAST = ("38a", "39", "40", "41")
MIN_DAY_STMTS = 3
MIN_WIN_STMTS = 2
MIN_HALF = 2
UTC = dt.timezone.utc


def goal_vec_path(model: str) -> Path:
    return ED / ("goal_vectors.npy" if model == "bge_small" else f"goal_vectors_{model}.npy")


def units_table(allow_holdout: bool = False, extra: list[dict] | None = None) -> pl.DataFrame:
    pu = pl.read_parquet(SH / "period_units.parquet")
    sel = pu.filter(((pl.col("goal_no") == 51) | pl.col("unit_id").is_in(list(CONTRAST))) & (pl.col("regime") == "III"))
    if not allow_holdout:
        sel = sel.filter(~pl.col("holdout"))
    sel = sel.select("unit_id", "goal_no", "first_day", "last_day", "n_days", "days", "rooms", "n_agents")
    if extra:
        sel = pl.concat([sel, pl.DataFrame(extra, schema=sel.schema)])
    return sel.sort("goal_no", "first_day")


ALLOW_HOLDOUT_LABELS = False   # set only by main(allow_holdout=True) (confirm.py, guarded)


def role_spells() -> pl.DataFrame:
    """DQ6 #51 roles (preferred & ~holdout unless confirming) with the goal-vector row to use."""
    g = pl.read_parquet(SH / "ground_truth_labels.parquet").filter(
        (pl.col("goal_no") == 51) & pl.col("preferred") & (pl.col("label_kind") == "role")
        & (pl.lit(ALLOW_HOLDOUT_LABELS) | ~pl.col("holdout")))
    goals = pl.read_parquet(ED / "goals.parquet").filter(pl.col("kind").cast(pl.String) == "agent_goal") \
        .select("gid", "agent", "valid_from", "valid_to").sort("agent", "valid_from")
    # latest agent_goal row per agent (agent 42 has an early superseded row on 09-01)
    latest = goals.group_by("agent").agg(pl.col("gid").last())
    return g.select("agent", pl.col("value").alias("role"), "t_valid_from", "t_valid_to").join(latest, on="agent", how="left")


def role_vectors(model: str) -> dict:
    """Whitened (regime III, d = 32), unit-normalized role vectors keyed by (agent, role)."""
    G = np.load(goal_vec_path(model)).astype(np.float32)
    W = load_whitener("III", 32, model)
    sp = role_spells()
    out = {}
    for r in sp.iter_rows(named=True):
        if r["role"] == "game dev" and r["agent"] == 40:
            continue  # first role overwritten in agent_goals (DQ6): filled below
        if r["gid"] is None:
            continue
        v = W(G[r["gid"]][None, :])[0]
        out[(r["agent"], r["role"])] = v / np.linalg.norm(v)
    gd = [out[(a, "game dev")] for a in (24, 26) if (a, "game dev") in out]
    if gd:
        v = np.mean(gd, 0)
        out[(40, "game dev")] = v / np.linalg.norm(v)
    return out


def unit_roles(days: list[str]) -> pl.DataFrame:
    """Role held on most of the unit's days by each agent (DQ6 spells, PT days)."""
    sp = role_spells()
    rows = []
    for r in sp.iter_rows(named=True):
        lo = r["t_valid_from"].astimezone(dt.timezone(dt.timedelta(hours=-7))).date().isoformat()
        hi = r["t_valid_to"].astimezone(dt.timezone(dt.timedelta(hours=-7))).date().isoformat()
        for d in days:
            if lo <= d <= hi:
                rows.append((r["agent"], r["role"], d))
    if not rows:
        return pl.DataFrame(schema={"agent": pl.Int8, "role": pl.String, "n": pl.UInt32})
    df = pl.DataFrame(rows, schema={"agent": pl.Int8, "role": pl.String, "day": pl.String}, orient="row")
    return df.group_by("agent", "role").agg(pl.len().alias("n")).sort("agent", "n", descending=[False, True]) \
        .group_by("agent", maintain_order=True).first()


def pair_classes(days: list[str]) -> pl.DataFrame:
    g = pl.read_parquet(SH / "ground_truth_labels.parquet").filter(
        (pl.col("goal_no") == 51) & pl.col("preferred") & pl.col("label_kind").is_in(["rival_pair", "opposed_pair"])
        & (pl.lit(ALLOW_HOLDOUT_LABELS) | ~pl.col("holdout")))
    rows = []
    pt = dt.timezone(dt.timedelta(hours=-7))
    for r in g.iter_rows(named=True):
        lo = r["t_valid_from"].astimezone(pt).date().isoformat()
        hi = r["t_valid_to"].astimezone(pt).date().isoformat()
        n_in = sum(lo <= d <= hi for d in days)
        if 2 * n_in >= len(days) and n_in > 0:
            a, b = sorted((r["agent_a"], r["agent_b"]))
            rows.append((a, b, "SR" if r["label_kind"] == "rival_pair" else "OP"))
    return pl.DataFrame(rows, schema={"i": pl.Int8, "j": pl.Int8, "cls": pl.String}, orient="row")


def build_unit(u: dict, ad: pl.DataFrame, aw: pl.DataFrame, st: pl.DataFrame, arrs: dict, out_root: Path,
               allow_holdout: bool, rv: dict, lab: dict, reads: pl.DataFrame, rp: pl.DataFrame) -> dict:
    days = list(u["days"])
    g = u["goal_no"]
    if not allow_holdout:
        assert not any(holdout_mask(days, [g] * len(days))), f"holdout day in {u['unit_id']}"
    od = out_root / u["unit_id"]
    od.mkdir(parents=True, exist_ok=True)
    dmap = {d: k for k, d in enumerate(sorted(days))}
    # agent-day states
    a = ad.filter((pl.col("goal_no") == g) & pl.col("pt_date").is_in(days)
                  & ((pl.col("n_chat") + pl.col("n_intent")) >= MIN_DAY_STMTS))
    if not allow_holdout:
        assert not a["holdout"].any()
    # modal chat room per agent-day (intentions have no room)
    rm = (st.filter((pl.col("goal_no") == g) & pl.col("pt_date").is_in(days) & pl.col("room").is_not_null())
          .group_by("agent", "pt_date").agg(pl.col("room").mode().first().alias("room")))
    a = a.join(rm, on=["agent", "pt_date"], how="left").with_columns(pl.col("room").fill_null(-1),
                                                                      pl.col("pt_date").replace_strict(dmap, return_dtype=pl.Int16).alias("day"))
    a = a.sort("agent", "day")
    a.select("gid", "agent", "pt_date", "day", "room", "n_chat", "n_intent").write_parquet(od / "agent_day.parquet")
    for (lv, var, mod), A in arrs.items():
        if lv == "day":
            np.save(od / f"S_{var}_{mod}.npy", np.asarray(A[a["gid"].to_numpy()], np.float32))
    # time-split halves from statements
    s = (st.filter((pl.col("goal_no") == g) & pl.col("pt_date").is_in(days))
         .join(a.select("agent", "pt_date"), on=["agent", "pt_date"], how="semi").sort("agent", "pt_date", "t"))
    s = s.with_columns(pl.col("t").rank("ordinal").over("agent", "pt_date").alias("rk"),
                       pl.len().over("agent", "pt_date").alias("nn"))
    s = s.with_columns((pl.col("rk") > pl.col("nn") // 2).cast(pl.Int8).alias("half"))
    hk = (s.group_by("agent", "pt_date", "half").agg(pl.col("srow"), pl.len().alias("n"))
          .filter(pl.col("n") >= MIN_HALF))
    full = hk.group_by("agent", "pt_date").agg(pl.len().alias("nh")).filter(pl.col("nh") == 2)
    hk = hk.join(full.select("agent", "pt_date"), on=["agent", "pt_date"], how="semi").sort("agent", "pt_date", "half")
    hmeta = hk.filter(pl.col("half") == 0).select("agent", "pt_date").with_columns(
        pl.col("pt_date").replace_strict(dmap, return_dtype=pl.Int16).alias("day"))
    hmeta.write_parquet(od / "halves.parquet")
    for var in VARIANTS:
        for mod in MODELS:
            SV = arrs[("stmt", var, mod)]
            H = {0: [], 1: []}
            for r in hk.iter_rows(named=True):
                H[r["half"]].append(np.asarray(SV[np.asarray(r["srow"])], np.float32).mean(0))
            for h in (0, 1):
                np.save(od / f"H{h + 1}_{var}_{mod}.npy", np.asarray(H[h], np.float32).reshape(-1, 32))
    # window states
    w = aw.filter((pl.col("goal_no") == g) & pl.col("pt_date").is_in(days)
                  & ((pl.col("n_chat") + pl.col("n_intent")) >= MIN_WIN_STMTS))
    wr = (st.filter((pl.col("goal_no") == g) & pl.col("pt_date").is_in(days) & pl.col("room").is_not_null())
          .group_by("agent", "pt_date", "win30").agg(pl.col("room").mode().first().alias("room")))
    w = w.join(wr, on=["agent", "pt_date", "win30"], how="left").join(
        a.select("agent", "pt_date", pl.col("room").alias("day_room")), on=["agent", "pt_date"], how="left")
    w = w.with_columns(pl.coalesce("room", "day_room").fill_null(-1).alias("room"),
                       pl.col("pt_date").replace_strict(dmap, return_dtype=pl.Int16).alias("day")).sort("agent", "day", "win30")
    w.select("gid", "agent", "pt_date", "day", "win30", "room", "n_chat", "n_intent").write_parquet(od / "win.parquet")
    for (lv, var, mod), A in arrs.items():
        if lv == "win":
            np.save(od / f"X_{var}_{mod}.npy", np.asarray(A[w["gid"].to_numpy()], np.float32))
    # pairs: lab, classes, reads, replies, stance (agents with any state in the unit)
    ags = sorted(set(a["agent"].to_list()) | set(w["agent"].to_list()))
    pr = [(i, j) for k, i in enumerate(ags) for j in ags[k + 1:]]
    P = pl.DataFrame(pr, schema={"i": pl.Int8, "j": pl.Int8}, orient="row")
    P = P.with_columns(pl.struct("i", "j").map_elements(lambda r: lab.get(r["i"]) == lab.get(r["j"]) and lab.get(r["i"]) is not None,
                                                        return_dtype=pl.Boolean).alias("same_lab"))
    if g == 51:
        pc = pair_classes(days)
        P = P.join(pc, on=["i", "j"], how="left")
    else:
        P = P.with_columns(pl.lit(None, dtype=pl.String).alias("cls"))
    rd = (reads.filter((pl.col("goal_no") == g) & pl.col("pt_date").is_in(days))
          .with_columns(pl.min_horizontal("i", "j").alias("a"), pl.max_horizontal("i", "j").alias("b"),
                        (pl.col("reads_i_from_j") + pl.col("reads_j_from_i")).alias("r"))
          .group_by("a", "b").agg(pl.col("r").log1p().sum().alias("lr_sum")))
    P = P.join(rd.rename({"a": "i", "b": "j"}), on=["i", "j"], how="left").with_columns(
        (pl.col("lr_sum").fill_null(0) / len(days)).alias("log_reads")).drop("lr_sum")
    r_ = (rp.filter((pl.col("goal_no") == g) & pl.col("pt_date").is_in(days))
          .with_columns(pl.min_horizontal("a_agent", "b_agent").alias("i"), pl.max_horizontal("a_agent", "b_agent").alias("j")))
    rep = r_.group_by("i", "j", "pt_date").agg(pl.col("p_reply").sum().alias("pr")).group_by("i", "j").agg(
        pl.col("pr").log1p().sum().alias("lp_sum"))
    stn = (r_.filter(pl.col("p_reply").is_not_null() & pl.col("p_supports").is_not_null())
           .group_by("i", "j").agg(((pl.col("p_supports") - pl.col("p_opposes")) * pl.col("p_reply")).sum().alias("sw"),
                                   pl.col("p_reply").sum().alias("w"), (pl.col("p_reply") >= 0.5).sum().alias("n_rep")))
    P = P.join(rep, on=["i", "j"], how="left").with_columns((pl.col("lp_sum").fill_null(0) / len(days)).alias("log_replies")).drop("lp_sum")
    P = P.join(stn, on=["i", "j"], how="left").with_columns(
        pl.when(pl.col("n_rep") >= 3).then(pl.col("sw") / pl.col("w")).alias("stance"),
        pl.col("n_rep").fill_null(0)).drop("sw", "w")
    P.write_parquet(od / "pairs.parquet")
    # roles in the unit
    if g == 51:
        ur = unit_roles(days)
        ur.write_parquet(od / "roles.parquet")
    return {"unit": u["unit_id"], "goal_no": g, "n_days": len(days), "n_agent_days": a.height,
            "n_agents": a["agent"].n_unique(), "n_halves": hmeta.height, "n_windows": w.height, "n_pairs": P.height,
            "n_SR": int((P["cls"] == "SR").sum()) if g == 51 else 0}


def prepare(allow_holdout: bool = False):
    ad = pl.read_parquet(ED / "agent_day.parquet")
    aw = pl.read_parquet(ED / "agent_win30.parquet")
    st = pl.read_parquet(ED / "statements.parquet")
    if not allow_holdout:
        ad = ad.filter(~pl.col("holdout"))
        aw = aw.filter(~pl.col("holdout"))
        st = st.with_row_index("_r").filter(~pl.col("holdout"))
    else:
        st = st.with_row_index("_r")
    arrs = {}
    for var in VARIANTS:
        for mod in MODELS:
            arrs[("day", var, mod)] = np.load(ED / f"agent_day_{var}_{mod}.npy", mmap_mode="r")
            arrs[("win", var, mod)] = np.load(ED / f"agent_win30_{var}_{mod}.npy", mmap_mode="r")
            arrs[("stmt", var, mod)] = np.load(ED / f"statements_{STMT_VAR[var]}_{mod}.npy", mmap_mode="r")
    # statements: keep the global row index (arrays are indexed by it)
    st = st.rename({"_r": "srow_global"})
    roster = pl.read_parquet(SH / "roster.parquet")
    lab = dict(zip(roster["agent"].to_list(), roster["lab"].to_list()))
    reads = pl.read_parquet(SH / "pair_day_reads.parquet")
    rp = (pl.scan_parquet(SH / "reply_pairs.parquet")
          .filter((pl.col("pair_set").cast(pl.String) == "cand") & pl.col("labelled") & (pl.col("a_kind") == 0)
                  & (pl.col("goal_no").is_in([38, 39, 40, 41, 51])))
          .select("goal_no", "pt_date", "holdout", "a_agent", "b_agent", "p_reply", "p_supports", "p_opposes").collect())
    if not allow_holdout:
        reads = reads.filter(~pl.col("holdout"))
        rp = rp.filter(~pl.col("holdout"))
    return ad, aw, st, arrs, lab, reads, rp


def main(allow_holdout: bool = False, out_root: Path = OUT, extra_units: list[dict] | None = None,
         only_units: list[str] | None = None):
    global ALLOW_HOLDOUT_LABELS
    ALLOW_HOLDOUT_LABELS = allow_holdout
    ad, aw, st, arrs, lab, reads, rp = prepare(allow_holdout)
    # statements: the half builder indexes arrays by the global row
    st_h = st.rename({"srow_global": "srow"})
    units = units_table(allow_holdout, extra_units)
    if only_units:
        units = units.filter(pl.col("unit_id").is_in(only_units))
    out_root.mkdir(parents=True, exist_ok=True)
    rows = []
    for u in units.iter_rows(named=True):
        r = build_unit(u, ad, aw, st_h, arrs, out_root, allow_holdout, None, lab, reads, rp)
        rows.append(r)
        print(r, flush=True)
    for mod in MODELS:
        rv = role_vectors(mod)
        keys = sorted(rv)
        np.save(out_root / f"roles_{mod}.npy", np.asarray([rv[k] for k in keys], np.float32))
        pl.DataFrame({"agent": [k[0] for k in keys], "role": [k[1] for k in keys]},
                     schema={"agent": pl.Int8, "role": pl.String}).write_parquet(out_root / "roles.parquet")
    units.write_parquet(out_root / "units.parquet")
    pl.DataFrame(rows).write_parquet(out_root / "unit_counts.parquet")
    prov = {"built_by": "hypotheses/H98-random-field-51/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["embeddings/agent_day", "embeddings/agent_win30", "embeddings/statements",
                                   "embeddings/goals + goal_vectors (bge, gte)", "ground_truth_labels (DQ6)",
                                   "pair_day_reads", "reply_pairs (DQ2)", "roster", "period_units"]}],
            "params": {"models": MODELS, "variants": VARIANTS, "min_day_statements": MIN_DAY_STMTS,
                       "min_window_statements": MIN_WIN_STMTS, "min_half_statements": MIN_HALF,
                       "contrast_units": CONTRAST, "allow_holdout": allow_holdout},
            "built_at": dt.datetime.now(UTC).isoformat()}
    (out_root / "_provenance.json").write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    main()
