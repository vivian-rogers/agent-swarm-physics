"""H89 scheme: agent-day traits (content bge/gte, style, conventions) per split half, and in-cone adoption rows
(cultural parentage inputs) for every non-holdout goal period with H34 ideas.

  uv run python hypotheses/H89-price-equation-culture/scheme/build.py [--goals 31,38,51]

Outputs (data/processed/H89-price-equation-culture/):
  traits/G<NN>.npz     agent-day keys (agent, day index, pt_date) and per-half traits:
                       content_bge / content_gte (n x 3 x 32: whole, A, B), style (n x 3 x 20), conv (n x 3 x 50),
                       counts n / nA / nB, conv_ideas (the 50 trait ideas, hashed markers)
  agent_days.parquet   goal, pt_date, day, agent, n, nA, nB, active, F_all, F_notrait (first uses of period ideas)
  adoptions.parquet    goal, pt_date, day, adopter, marker, cls, in_trait, kind (read | plc), sources (list),
                       named_sources (list), human_source (bool)
  kickoff.npz          per goal and embedding model: unit kickoff direction in the regime's 32-d whitened basis
  residual_pool/G<NN>.npz   message-level residuals from the agent-day mean (content_bge, style) with agent, day,
                       half: used only by analysis/synthetic.py
No text is read or written. Held-out days are excluded by idea_ledger (holdout_mask + calendar.holdout, asserted).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2"

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import idea_ledger as IL  # noqa: E402
from common import holdout_mask, git_commit  # noqa: E402
from embed_models import load_whitener, goal_vectors  # noqa: E402

SH = ROOT / "data/processed/shared"
ED = SH / "embeddings"
OUT = ROOT / "data/processed/H89-price-equation-culture"
CC_AGENT = 19
MIN_MSG, MIN_HALF = 6, 2
K_CONV = 50
CLS_N = 2
SYN_GOALS = {12, 20, 31, 38, 51}
STYLE = ["log_chars", "lines", "bullet_share", "headers", "bold", "emoji", "excl", "ques", "urls", "backticks",
         "digit_share", "upper_share", "at", "emdash", "fps", "fpp", "sp", "colon", "word_len", "parens"]
FCOLS = [f"f_{k}" for k in STYLE]


def half_of(mid: str) -> int:
    return hashlib.sha1(mid.encode()).digest()[-1] & 1


def candidate_goals() -> list[int]:
    fs = pl.read_parquet(ROOT / "data/processed/H34-idea-cascades/markers/first_seen.parquet", columns=["first_goal"])
    goals = sorted(set(fs["first_goal"].to_list()))
    held = set(json.loads((ROOT / "hypotheses/holdout.json").read_text())["goal_periods_held_out"])
    return [g for g in goals if g not in held]


class Shared:
    """Tables read once: statement map, style standardization, embeddings (memory-mapped)."""

    def __init__(self):
        st = pl.read_parquet(ED / "statements.parquet", columns=["kind", "src_row", "holdout"]).with_row_index("srow")
        ci = pl.read_parquet(ED / "chat_index.parquet").with_row_index("src_row")
        sf = pl.read_parquet(SH / "statement_flags.parquet", columns=["srow", "self_repeat_both"])
        chat_st = (st.filter(pl.col("kind") == "chat").join(ci, on="src_row", how="left")
                   .join(sf, on="srow", how="left"))
        self.st_of = chat_st.select("message_id", "srow", "self_repeat_both")
        self.emb = {m: np.load(ED / f"statements_style_resid_period32_{m}.npy", mmap_mode="r")
                    for m in ("bge_small", "gte_modernbert")}
        tf = pl.read_parquet(SH / "text_features.parquet", columns=["message_id", "agent", "holdout", *FCOLS])
        ref = tf.filter(~pl.col("holdout").fill_null(True) & pl.col("agent").is_not_null())
        X = ref.select(FCOLS).to_numpy().astype(np.float64)
        X = np.nan_to_num(X)
        lo, hi = np.quantile(X, 0.001, axis=0), np.quantile(X, 0.999, axis=0)
        Xw = np.clip(X, lo, hi)
        self.style_lo, self.style_hi = lo, hi
        self.style_mu, self.style_sd = Xw.mean(0), Xw.std(0) + 1e-12
        self.tf = tf.select("message_id", *FCOLS)

    def style(self, mids: list[str]) -> np.ndarray:
        d = pl.DataFrame({"message_id": mids}).join(self.tf, on="message_id", how="left", maintain_order="left")
        X = np.nan_to_num(d.select(FCOLS).to_numpy().astype(np.float64))
        return ((np.clip(X, self.style_lo, self.style_hi) - self.style_mu) / self.style_sd).astype(np.float32)


def kickoff_dirs(goals: list[int]) -> dict:
    gq = pl.read_parquet(ED / "goals.parquet")
    out = {}
    for model in ("bge_small", "gte_modernbert"):
        G = goal_vectors(model).astype(np.float32)
        for g in goals:
            rows = gq.filter((pl.col("goal_no") == g) & (pl.col("kind") == "kickoff"))
            if rows.height == 0:
                rows = gq.filter((pl.col("goal_no") == g) & (pl.col("kind") == "goal"))
            if rows.height == 0:
                continue
            reg = str(rows["regime"][0])
            W = load_whitener(reg, 32, model)
            v = W(G[int(rows["gid"][0])][None, :])[0].astype(np.float64)
            out[f"G{g:02d}_{model}"] = (v / (np.linalg.norm(v) + 1e-12)).astype(np.float32)
    return out


def agent_day_means(X: np.ndarray, key: np.ndarray, half: np.ndarray, n_keys: int) -> np.ndarray:
    """(n_keys x 3 x d): whole, half A (0), half B (1) means."""
    d = X.shape[1]
    out = np.full((n_keys, 3, d), np.nan, dtype=np.float32)
    for j, sel in enumerate([np.ones(len(key), bool), half == 0, half == 1]):
        s = np.zeros((n_keys, d)); c = np.zeros(n_keys)
        np.add.at(s, key[sel], X[sel].astype(np.float64))
        np.add.at(c, key[sel], 1)
        ok = c > 0
        out[ok, j] = (s[ok] / c[ok, None]).astype(np.float32)
    return out


def build_period(base: IL.Base, sh: Shared, g: int, P: dict | None = None) -> tuple[pl.DataFrame, pl.DataFrame, dict] | None:
    """P: a preloaded idea_ledger period with use_pos / use_marker / use_cls (confirm.py passes held-out targets;
    round 1 leaves it None, so its outputs are unchanged)."""
    if P is None:
        P = IL.load_period(base, g)
    if P is None:
        return None
    days = P["days"]
    mids = P["message_id"]
    n = len(mids)
    kind, sender, day = P["kind"], P["sender"].astype(np.int64), P["day"].astype(np.int64)
    # ---------------- eligible messages
    m = pl.DataFrame({"message_id": mids, "pos": np.arange(n)}).join(sh.st_of, on="message_id", how="left",
                                                                     maintain_order="left")
    srow = m["srow"].to_numpy()
    copy = m["self_repeat_both"].fill_null(False).to_numpy()
    has_st = ~m["srow"].is_null().to_numpy()
    elig = (kind == 0) & (sender >= 0) & (sender != CC_AGENT) & ~copy & has_st
    ei = np.flatnonzero(elig)
    half = np.array([half_of(mids[i]) for i in ei], dtype=np.int8)
    ag, dy = sender[ei], day[ei]
    keys = pl.DataFrame({"agent": ag, "day": dy}).unique().sort("agent", "day").with_row_index("k")
    key = pl.DataFrame({"agent": ag, "day": dy}).join(keys, on=["agent", "day"], how="left",
                                                     maintain_order="left")["k"].to_numpy().astype(np.int64)
    nk = keys.height
    cnt = np.bincount(key, minlength=nk)
    cA = np.bincount(key[half == 0], minlength=nk)
    cB = np.bincount(key[half == 1], minlength=nk)
    # ---------------- traits
    sr = srow[ei].astype(np.int64)
    traits = {}
    resid = {}
    for model, tag in (("bge_small", "content_bge"), ("gte_modernbert", "content_gte")):
        X = np.asarray(sh.emb[model][sr], dtype=np.float32)
        traits[tag] = agent_day_means(X, key, half, nk)
        if model == "bge_small" and g in SYN_GOALS:
            resid["content_bge"] = (X - traits[tag][key, 0]).astype(np.float16)
    Xs = sh.style([mids[i] for i in ei])
    traits["style"] = agent_day_means(Xs, key, half, nk)
    if g in SYN_GOALS:
        resid["style"] = (Xs - traits["style"][key, 0]).astype(np.float16)
    # conventions: top-K N-class period ideas by distinct agent users (eligible messages)
    up, umk, ucl = P["use_pos"], P["use_marker"], P["use_cls"]
    pos_e = np.full(n, -1, dtype=np.int64)
    pos_e[ei] = np.arange(len(ei))
    selN = (ucl == CLS_N) & (pos_e[up] >= 0)
    uN = pl.DataFrame({"marker": umk[selN], "agent": sender[up[selN]], "e": pos_e[up[selN]]})
    top = (uN.group_by("marker").agg(pl.col("agent").n_unique().alias("users"), pl.len().alias("uses"))
           .sort(["users", "uses", "marker"], descending=[True, True, False]).head(K_CONV))
    conv_ideas = top["marker"].to_numpy()
    Xc = np.zeros((len(ei), K_CONV), dtype=np.float32)
    if len(conv_ideas):
        col = {int(k): c for c, k in enumerate(conv_ideas)}
        u2 = uN.filter(pl.col("marker").is_in(conv_ideas)).unique(["marker", "e"])
        Xc[u2["e"].to_numpy(), [col[int(k)] for k in u2["marker"].to_list()]] = 1.0
    traits["conv"] = agent_day_means(Xc, key, half, nk)
    # ---------------- adoptions (cultural parentage inputs)
    TS, cs, t = P["TS"], P["cs"], P["t"]
    named = P["named"]
    trait_set = set(int(x) for x in conv_ideas)
    rows = []
    fu_rows = []
    for mk, cl, pos in IL.ideas_grouped(P):
        fu = IL.first_uses(P, pos)
        first = int(pos[0])
        in_trait = mk in trait_set
        spk = np.where(kind[pos] == 0, sender[pos], -1)
        for a, u in fu.items():
            fu_rows.append((a, int(day[u]), in_trait))
            if u == first:
                continue
            vis = (TS[pos, a] <= cs[u]) & (spk != a)
            vis_agents = vis & (spk >= 0)
            human = bool((vis & (spk < 0)).any())
            if vis_agents.any():
                pv = pos[vis_agents]
                srcs = sorted(set(int(x) for x in sender[pv]))
                nmd = sorted(set(int(sender[p]) for p in pv if a in (named[p] or [])))
                rows.append((int(day[u]), int(a), mk, int(cl), in_trait, "read", srcs, nmd, human))
            elif not vis.any():
                prior = (t[pos] < t[u]) & (day[pos] == day[u]) & (spk >= 0) & (spk != a) & (TS[pos, a] > cs[u])
                if prior.any():
                    srcs = sorted(set(int(x) for x in sender[pos[prior]]))
                    rows.append((int(day[u]), int(a), mk, int(cl), in_trait, "plc", srcs, [], False))
    adop = pl.DataFrame(rows, schema={"day": pl.Int16, "adopter": pl.Int16, "marker": pl.Int64, "cls": pl.Int8,
                                      "in_trait": pl.Boolean, "kind": pl.String, "sources": pl.List(pl.Int16),
                                      "named_sources": pl.List(pl.Int16), "human_source": pl.Boolean},
                        orient="row").with_columns(pl.lit(g).cast(pl.Int8).alias("goal"),
                                                   pl.col("day").map_elements(lambda d: days[d], return_dtype=pl.String)
                                                   .alias("pt_date"))
    fuf = pl.DataFrame(fu_rows, schema={"agent": pl.Int64, "day": pl.Int64, "in_trait": pl.Boolean}, orient="row")
    F = fuf.group_by("agent", "day").agg(pl.len().alias("F_all"), (~pl.col("in_trait")).sum().alias("F_notrait"))
    ad = (keys.with_columns(pl.Series("n", cnt), pl.Series("nA", cA), pl.Series("nB", cB))
          .with_columns(((pl.col("n") >= MIN_MSG) & (pl.col("nA") >= MIN_HALF) & (pl.col("nB") >= MIN_HALF)).alias("active"))
          .join(F, on=["agent", "day"], how="left").with_columns(pl.col("F_all").fill_null(0), pl.col("F_notrait").fill_null(0))
          .with_columns(pl.lit(g).cast(pl.Int8).alias("goal"),
                        pl.col("day").map_elements(lambda d: days[d], return_dtype=pl.String).alias("pt_date")))
    npz = dict(agent=keys["agent"].to_numpy().astype(np.int16), day=keys["day"].to_numpy().astype(np.int16),
               n=cnt, nA=cA, nB=cB, conv_ideas=conv_ideas, days=np.array(days), **traits)
    if resid:
        npz["_resid"] = dict(agent=ag.astype(np.int16), day=dy.astype(np.int16), half=half, **resid)
    return ad, adop, npz


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--goals", default="")
    a = ap.parse_args()
    goals = [int(x) for x in a.goals.split(",") if x] or candidate_goals()
    t0 = time.time()
    (OUT / "traits").mkdir(parents=True, exist_ok=True)
    (OUT / "residual_pool").mkdir(parents=True, exist_ok=True)
    base = IL.Base()
    sh = Shared()
    ads, adops = [], []
    for g in goals:
        r = build_period(base, sh, g)
        if r is None:
            print(f"G{g:02d}: no data")
            continue
        ad, adop, npz = r
        res = npz.pop("_resid", None)
        np.savez_compressed(OUT / "traits" / f"G{g:02d}.npz", **npz)
        if res is not None:
            np.savez_compressed(OUT / "residual_pool" / f"G{g:02d}.npz", **res)
        ads.append(ad); adops.append(adop)
        act = ad.filter(pl.col("active"))
        print(f"G{g:02d}: {ad['day'].n_unique()} days, {act.height} active agent-days, "
              f"{adop.filter(pl.col('kind') == 'read').height} read adoptions, "
              f"{adop.filter(pl.col('kind') == 'plc').height} placebo  ({time.time() - t0:.0f}s)", flush=True)
    if not a.goals:
        pl.concat(ads, how="vertical_relaxed").write_parquet(OUT / "agent_days.parquet", compression="zstd")
        pl.concat(adops, how="vertical_relaxed").write_parquet(OUT / "adoptions.parquet", compression="zstd")
        np.savez_compressed(OUT / "kickoff.npz", **kickoff_dirs(goals))
        # assert: no held-out day anywhere
        allad = pl.read_parquet(OUT / "agent_days.parquet")
        assert not any(holdout_mask(allad["pt_date"].to_list(), allad["goal"].to_list())), "held-out day in output"
        prov = {"built_by": "hypotheses/H89-price-equation-culture/scheme/build.py", "git_commit": git_commit(),
                "inputs": [{"source": "ai-village", "revision": "see data/processed/shared/_provenance.json",
                            "tables": ["chat_core", "context_ledger_items", "call_windows", "chat_mentions_clean",
                                       "reply_pairs", "embeddings/statements", "statements_style_resid_period32_*",
                                       "statement_flags", "text_features", "roster", "calendar", "embeddings/goals",
                                       "H34-idea-cascades/markers"]}],
                "params": {"min_msg": MIN_MSG, "min_half": MIN_HALF, "k_conv": K_CONV, "cc_agent_excluded": CC_AGENT,
                           "copies_dropped": "self_repeat_both", "half_rule": "sha1(message_id)[-1] & 1",
                           "goals": goals},
                "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
        (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print(f"done in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
