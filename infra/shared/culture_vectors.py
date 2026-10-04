"""Culture-vector inputs: eligible agent-day content vectors, exogenous field directions (goal fields plus human-message
centroids per goal period and per PT day) and personal (agent) vectors, for culture / field hypotheses.

Moved from H81 (reference; hypotheses/H81-culture-beyond-composition/scheme/build.py and analysis/h81lib.py) and H82
(hypotheses/H82-remanence-endogenous-field/scheme/build.py, a copy of H81's scheme with an include_holdout switch;
analysis/h82lib.py: Data.prior). STANDARDS §8, 2026-10-04. Rules unchanged; the hypothesis copies stay in place.
H83, H88 and H89 could use it.

  eligible_agentdays(include_holdout=False)  agent_day rows with n_chat + n_intent >= 5, agents 19/28/30 excluded,
                                             period unit, dominant chat room, ISO week, block = goal x regime x week
  build_blocks(ad)                           block table (first/last/mid day, members)
  directions(model, ad, include_holdout)     unit directions in each regime's 32-d whitened basis: per goal (goal,
                                             kickoff, kickoff_room, agent_goal; goal_whole skipped), human-message
                                             centroid per goal period and per PT day. Returns (V, index)
  projectors(V, idx, regime, goals, agents_by_goal, use_human)   field-removal projectors per (goal, agent)
  personal_vectors(agent, goal, Xp, weights, method)  leave-goal-out personal vectors: "fe" = two-way agent + goal fixed
                                             effects on agent-goal cell means without goal G (H81 Amendment A1,
                                             primary); "mean" = plain mean of the agent's other-goal vectors
  prior_mean(...)                            H82's prior: unit leave-goals-out mean (no goal fixed effects)
Note: H81 and H82 do not use the same personal vector. H81 uses the two-way FE; H82's remanence design uses the
plain mean prior. State which one a result uses (the leave-period-out mean folds other periods' village states in;
Known issue, H81).

Holdout: the default build drops held-out agent-days (common.holdout_mask and agent_day.holdout, asserted) and held-out
goals' directions and human messages. include_holdout=True is for guarded confirm scripts only (in memory; the CLI never
sets it, and the shared outputs never contain held-out rows).

Outputs (data/processed/shared/culture_vectors/, + _provenance.json; the same files as H81's scheme folder):
  agentdays.parquet, vecs_<model>_<variant>.npy (unit 32-d float32, rows of agentdays), dirs_<model>.npz (V) +
  dirs_index_<model>.json, blocks.parquet
Usage: uv run python infra/shared/culture_vectors.py            (build)
       uv run python infra/shared/culture_vectors.py --verify   (H81 and H82 tables; H81 personal_vectors and H82 prior
                                                                  through read-only imports)
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import REVISION, ROOT, git_commit, holdout_mask  # noqa: E402
from embed_models import load_whitener, goal_vectors, MODELS  # noqa: E402

SH = ROOT / "data/processed/shared"
ED = SH / "embeddings"
OUT = SH / "culture_vectors"
H81 = ROOT / "data/processed/H81-culture-beyond-composition"
H82 = ROOT / "data/processed/H82-remanence-endogenous-field"
MODEL_LIST = ["bge_small", "gte_modernbert"]
VARIANTS = ["style_resid", "white32", "style_resid_period"]
EXCLUDE = {19, 28, 30}
MIN_STAT = 5
MIN_OTHER_DAYS = 3        # H81 personal vectors; H82 MIN_PRIOR_DAYS (same value)

def unit(X: np.ndarray) -> np.ndarray:
    X = np.asarray(X, dtype=np.float64)
    n = np.linalg.norm(X, axis=-1, keepdims=True)
    n[n == 0] = 1.0
    return X / n


def eligible_agentdays(include_holdout: bool = False) -> pl.DataFrame:
    """include_holdout is used only by the guarded analysis/confirm.py."""
    ad = pl.read_parquet(ED / "agent_day.parquet").with_row_index("src")
    hm = np.array(holdout_mask(ad["pt_date"].to_list(), ad["goal_no"].to_list()))
    ad = ad.with_columns(pl.Series("hm", hm), (pl.col("n_chat") + pl.col("n_intent")).alias("n_stat"))
    ad = ad.filter((include_holdout | (~pl.col("hm") & ~pl.col("holdout"))) & (pl.col("n_stat") >= MIN_STAT)
                   & ~pl.col("agent").is_in(list(EXCLUDE)))
    if not include_holdout:
        assert not ad["hm"].any() and not ad["holdout"].any()
    # unit of analysis
    pu = pl.read_parquet(SH / "period_units.parquet").select("unit_id", "goal_no", "days").explode("days") \
        .rename({"days": "pt_date"})
    ad = ad.join(pu, on=["goal_no", "pt_date"], how="left").unique(subset=["src"], keep="first", maintain_order=True)
    # dominant room of the agent-day (chat statements)
    st = pl.read_parquet(ED / "statements.parquet", columns=["kind", "agent", "pt_date", "room"]) \
        .filter((pl.col("kind") == "chat") & pl.col("room").is_not_null())
    dom = (st.group_by("agent", "pt_date", "room").len().sort("len", descending=True)
           .group_by("agent", "pt_date", maintain_order=True).first().select("agent", "pt_date", "room"))
    ad = ad.join(dom, on=["agent", "pt_date"], how="left")
    d = ad["pt_date"].str.to_date()
    iso = d.dt.iso_year().cast(pl.Int32) * 100 + d.dt.week().cast(pl.Int32)
    ad = ad.with_columns(iso.alias("week"))
    ad = ad.with_columns((pl.col("goal_no").cast(pl.Utf8) + pl.col("regime") + "w" + pl.col("week").cast(pl.Utf8))
                         .alias("block"))
    return ad.sort("src")


def build_blocks(ad: pl.DataFrame) -> pl.DataFrame:
    b = (ad.group_by("block", "goal_no", "regime", "week")
         .agg(pl.col("pt_date").min().alias("first_day"), pl.col("pt_date").max().alias("last_day"),
              pl.col("pt_date").n_unique().alias("n_days"), pl.col("agent").unique().sort().alias("members"))
         .with_columns(pl.col("members").list.len().alias("n_agents")))
    mid = [(dt.date.fromisoformat(a) + (dt.date.fromisoformat(z) - dt.date.fromisoformat(a)) / 2)
           for a, z in zip(b["first_day"], b["last_day"])]
    t0 = dt.date(2025, 1, 1)
    b = b.with_columns(pl.Series("mid_day", [(m - t0).days for m in mid], dtype=pl.Float64))
    return b.sort("first_day")


def directions(model: str, ad: pl.DataFrame, include_holdout: bool = False) -> tuple[dict, dict]:
    """Unit exogenous directions in each regime's 32-d whitened space for this model (include_holdout: confirm.py only)."""
    g = pl.read_parquet(ED / "goals.parquet").with_row_index("row")
    GV = goal_vectors(model).astype(np.float32)
    W = {r: load_whitener(r, 32, model) for r in ("I", "II", "III")}
    goals_keep = set(ad["goal_no"].unique().to_list())
    regimes_of_goal = {gn: sorted(set(ad.filter(pl.col("goal_no") == gn)["regime"].to_list())) for gn in goals_keep}
    vecs, index = [], []

    def add(key: dict, raw: np.ndarray, regime: str):
        v = unit(W[regime](raw[None, :]))[0]
        index.append({**key, "regime": regime, "i": len(vecs)})
        vecs.append(v)

    for r in g.filter((include_holdout | ~pl.col("holdout")) & pl.col("goal_no").is_in(list(goals_keep))).iter_rows(named=True):
        kind = str(r["kind"])
        if kind == "goal_whole":
            continue
        for reg in regimes_of_goal[r["goal_no"]]:
            key = {"level": "goal", "goal_no": r["goal_no"], "kind": kind, "room": r["room"], "agent": r["agent"],
                   "valid_from": r["valid_from"], "valid_to": r["valid_to"], "pt_date": None}
            add(key, GV[r["row"]], reg)
    # human messages: per goal period and per PT day
    k = pl.read_parquet(SH / "kicks_classified.parquet").filter(pl.col("kind") == "human_message") \
        .select("message_id", "goal_no", "pt_date")
    hm = np.array(holdout_mask(k["pt_date"].to_list(), k["goal_no"].to_list()))
    if not include_holdout:
        k = k.filter(~pl.Series(hm))
    ci = pl.read_parquet(ED / "chat_index.parquet").with_row_index("row")
    k = k.join(ci, on="message_id", how="inner")
    C = np.load(ED / f"chat_{MODELS[model]['suffix']}.npy", mmap_mode="r")
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "regime"]).with_columns(pl.col("regime").cast(pl.Utf8))
    k = k.join(cal, on="pt_date", how="left").filter(pl.col("goal_no").is_in(list(goals_keep)))
    for (gn, reg), sub in k.group_by(["goal_no", "regime"]):
        rows = np.sort(sub["row"].to_numpy())
        Xw = unit(W[reg](np.asarray(C[rows], dtype=np.float32)))
        index.append({"level": "goal", "goal_no": gn, "kind": "human", "room": None, "agent": None,
                      "valid_from": None, "valid_to": None, "pt_date": None, "regime": reg, "i": len(vecs)})
        vecs.append(unit(Xw.mean(0)))
    for (day, gn, reg), sub in k.group_by(["pt_date", "goal_no", "regime"]):
        rows = np.sort(sub["row"].to_numpy())
        Xw = unit(W[reg](np.asarray(C[rows], dtype=np.float32)))
        index.append({"level": "day", "goal_no": gn, "kind": "human", "room": None, "agent": None,
                      "valid_from": None, "valid_to": None, "pt_date": day, "regime": reg, "i": len(vecs)})
        vecs.append(unit(Xw.mean(0)))
    return np.array(vecs, dtype=np.float32), index


# ------------------------------------------------------------------------------------------------- personal vectors and projectors
def _proj(D: np.ndarray) -> np.ndarray:
    if len(D) == 0:
        return np.eye(32)
    Q, R = np.linalg.qr(D.T)
    keep = np.abs(np.diag(R)) > 1e-8
    Q = Q[:, keep]
    return np.eye(32) - Q @ Q.T


def projectors(V: np.ndarray, idx: list, regime: str, goals, agents_by_goal: dict, use_human: bool = True) -> dict:
    """(goal_no, agent) -> 32x32 projector removing the goal's exogenous directions in `regime` (kickoff, goal,
    kickoff_room, and the period human centroid when use_human), plus the agent's own #51 goal (key agent -1 = none).
    H81 h81lib.projectors with the direction table passed in."""
    V = np.asarray(V, dtype=np.float64)
    P = {}
    for g in goals:
        base = [e["i"] for e in idx if e["level"] == "goal" and e["goal_no"] == g and e["regime"] == regime
                and e["kind"] in ("kickoff", "goal", "kickoff_room") ]
        if use_human:
            base += [e["i"] for e in idx if e["level"] == "goal" and e["goal_no"] == g and e["regime"] == regime
                     and e["kind"] == "human"]
        P[(g, -1)] = _proj(V[base])
        for a in agents_by_goal[g]:
            ag = [e["i"] for e in idx if e["level"] == "goal" and e["goal_no"] == g and e["regime"] == regime
                  and e["kind"] == "agent_goal" and e["agent"] == a]
            P[(g, a)] = _proj(V[base + ag]) if ag else P[(g, -1)]
    return P


def personal_vectors(agent: np.ndarray, goal: np.ndarray, Xp: np.ndarray, weights: np.ndarray | None = None,
                     method: str = "fe", min_other_days: int = MIN_OTHER_DAYS):
    """mu[(agent, goal)]: the agent's personal vector estimated from its days in OTHER goals of the regime
    (>= MIN_OTHER_DAYS). method 'fe' (Amendment A1, primary): two-way fixed effects (agent + goal) fitted on agent-goal
    means without goal G, so other goals' village states are not folded into the personal vector; 'mean' (the HH's
    literal null, pre-amendment): plain mean of the agent's projected vectors in other goals."""
    w = np.ones(len(Xp)) if weights is None else weights
    agents = np.unique(agent); goals = np.unique(goal)
    ai = {a: k for k, a in enumerate(agents)}; gi = {g: k for k, g in enumerate(goals)}
    Y = np.zeros((len(agents), len(goals), Xp.shape[1])); Wt = np.zeros((len(agents), len(goals)))
    np.add.at(Y, (np.vectorize(ai.get)(agent), np.vectorize(gi.get)(goal)), Xp * w[:, None])
    np.add.at(Wt, (np.vectorize(ai.get)(agent), np.vectorize(gi.get)(goal)), w)
    cnt = np.zeros_like(Wt); np.add.at(cnt, (np.vectorize(ai.get)(agent), np.vectorize(gi.get)(goal)), 1)
    mu = {}
    for g in goals:
        keep = np.ones(len(goals), bool); keep[gi[g]] = False
        if method == "fe":
            A_hat = _twoway(Y[:, keep], Wt[:, keep])
        for a in agents:
            if cnt[ai[a], gi[g]] == 0 or cnt[ai[a], keep].sum() < min_other_days:
                continue
            if method == "fe":
                mu[(a, g)] = A_hat[ai[a]]
            else:
                mu[(a, g)] = Y[ai[a], keep].sum(0) / Wt[ai[a], keep].sum()
    return mu


def _twoway(Ysum: np.ndarray, W: np.ndarray, iters: int = 200) -> np.ndarray:
    """Weighted two-way FE on cell sums: minimize sum W_ig |ybar_ig - a_i - c_g|^2 with sum_g (W_.g) c_g = 0.
    Returns a (agents x d); agents with no cells get zeros."""
    Wa = W.sum(1); Wg = W.sum(0)
    Ybar = np.divide(Ysum, W[..., None], out=np.zeros_like(Ysum), where=W[..., None] > 0)
    a = np.divide(Ysum.sum(1), Wa[:, None], out=np.zeros((len(Wa), Ysum.shape[2])), where=Wa[:, None] > 0)
    c = np.zeros((len(Wg), Ysum.shape[2]))
    for _ in range(iters):
        c_new = np.divide((W[..., None] * (Ybar - a[:, None, :])).sum(0), Wg[:, None], out=np.zeros_like(c),
                          where=Wg[:, None] > 0)
        c_new -= (Wg[:, None] * c_new).sum(0) / Wg.sum()
        a_new = np.divide((W[..., None] * (Ybar - c_new[None, :, :])).sum(1), Wa[:, None], out=np.zeros_like(a),
                          where=Wa[:, None] > 0)
        if np.abs(a_new - a).max() < 1e-9 and np.abs(c_new - c).max() < 1e-9:
            a, c = a_new, c_new
            break
        a, c = a_new, c_new
    return a


def prior_mean(X: np.ndarray, agent: np.ndarray, goal: np.ndarray, regime: np.ndarray, a: int, reg: str, leave_goals: set,
               min_days: int = MIN_OTHER_DAYS):
    """H82's personal prior (h82lib.Data.prior): unit mean of agent a's vectors in regime `reg` outside leave_goals;
    None with fewer than min_days rows. A plain leave-goals-out mean, NOT the two-way fixed effect (H81 Amendment A1)."""
    m = (agent == a) & (regime == reg) & ~np.isin(goal, list(leave_goals))
    return unit(X[m].mean(0)) if m.sum() >= min_days else None


# ------------------------------------------------------------------------------------------------- build + verify
def build(out: Path = OUT):
    """H81 scheme/build.py main(), into `out`."""
    out.mkdir(parents=True, exist_ok=True)
    ad = eligible_agentdays()
    src = ad["src"].to_numpy()
    for m in MODEL_LIST:
        for v in VARIANTS:
            X = np.load(ED / f"agent_day_{v}_{MODELS[m]['suffix']}.npy").astype(np.float32)[src]
            np.save(out / f"vecs_{m}_{v}.npy", unit(X).astype(np.float32))
        V, idx = directions(m, ad)
        np.savez_compressed(out / f"dirs_{m}.npz", V=V)
        (out / f"dirs_index_{m}.json").write_text(json.dumps(idx))
        print(m, "directions", len(idx), flush=True)
    ad.drop("hm").write_parquet(out / "agentdays.parquet")
    blocks = build_blocks(ad)
    blocks.write_parquet(out / "blocks.parquet")
    print("agent-days", ad.height, "blocks", blocks.height, flush=True)
    prov = {"built_by": "infra/shared/culture_vectors.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["embeddings/agent_day", "agent_day_{style_resid,white32,style_resid_period}_<model>",
                                   "embeddings/statements", "embeddings/goals", "goal_vectors", "kicks_classified",
                                   "chat_index", "chat_<model>", "whitening_<model>_<regime>", "period_units",
                                   "calendar"]}],
            "params": {"min_statements": MIN_STAT, "exclude_agents": sorted(EXCLUDE), "models": MODEL_LIST,
                       "variants": VARIANTS, "block": "goal_no x regime x ISO week", "holdout": "dropped (holdout_mask)",
                       "source": "H81 scheme/build.py (reference) = H82 scheme/build.py agent-day and direction code"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (out / "_provenance.json").write_text(json.dumps(prov, indent=1))


def _dir_map(folder: Path, m: str) -> dict:
    V = np.load(folder / f"dirs_{m}.npz")["V"]
    idx = json.loads((folder / f"dirs_index_{m}.json").read_text())
    return {json.dumps({k: v for k, v in e.items() if k != "i"}, sort_keys=True, default=str): V[e["i"]] for e in idx}


def _cmp_dirs(a: dict, b: dict) -> str:
    if a.keys() != b.keys():
        return f"keys differ ({len(a)} vs {len(b)}; {len(a.keys() ^ b.keys())} unmatched)"
    d = max(float(np.max(np.abs(a[k].astype(np.float64) - b[k].astype(np.float64)))) for k in a)
    return "identical" if d == 0 else f"max_abs_diff {d:.2e}"


def _ro_import(path: Path, name: str):
    import importlib.util
    sys.dont_write_bytecode = True          # read-only import: never write into hypotheses/
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def verify() -> bool:
    res, ok = {}, True
    ad = pl.read_parquet(OUT / "agentdays.parquet")
    for name, folder in (("H81", H81), ("H82", H82)):
        r = {}
        old = pl.read_parquet(folder / "agentdays.parquet")
        if old.equals(ad):
            r["agentdays"] = "identical"
        elif old.drop("room").equals(ad.drop("room")):
            # the dominant room breaks exact count ties with an unstable sort (rule kept verbatim): accept differences
            # only on agent-days whose top room count is tied
            st = pl.read_parquet(ED / "statements.parquet", columns=["kind", "agent", "pt_date", "room"]).filter(
                (pl.col("kind") == "chat") & pl.col("room").is_not_null())
            c = st.group_by("agent", "pt_date", "room").len()
            tied = c.group_by("agent", "pt_date").agg((pl.col("len") == pl.col("len").max()).sum().alias("nt")) \
                .filter(pl.col("nt") > 1).select("agent", "pt_date", pl.lit(True).alias("tied"))
            j = ad.select("agent", "pt_date").with_columns(old["room"].alias("r_old"), ad["room"].alias("r_new")) \
                .join(tied, on=["agent", "pt_date"], how="left")
            diff = j.filter(~(pl.col("r_old").eq_missing(pl.col("r_new"))))
            r["agentdays"] = ("identical except tied rooms" if diff["tied"].fill_null(False).all() else "differ")
            r["agentdays_room_ties_differing"] = diff.height
        else:
            r["agentdays"] = "differ"
        for m in MODEL_LIST:
            for v in VARIANTS:
                f = f"vecs_{m}_{v}.npy"
                r[f] = "identical" if np.array_equal(np.load(folder / f), np.load(OUT / f)) else "differ"
            r[f"dirs_{m}"] = _cmp_dirs(_dir_map(folder, m), _dir_map(OUT, m))
        if (folder / "blocks.parquet").exists():
            r["blocks"] = "identical" if pl.read_parquet(folder / "blocks.parquet").equals(pl.read_parquet(OUT / "blocks.parquet")) else "differ"
        ok &= all(x in ("identical", "identical except tied rooms") for k, x in r.items() if not k.endswith("_differing"))
        res[name] = r
    # personal vectors: H81's own function (read-only import) on H81's panel vs this module, both methods
    L = _ro_import(ROOT / "hypotheses/H81-culture-beyond-composition/analysis/h81lib.py", "_h81lib_ro")
    for regime in ("I", "III"):
        a81, X, blocks = L.load("bge_small", "style_resid", regime)
        P = L.projectors("bge_small", regime, a81)
        pan = L.Panel(a81, blocks, P)
        Xp = L.project(pan, X)
        V = np.load(OUT / "dirs_bge_small.npz")["V"]
        idx = json.loads((OUT / "dirs_index_bge_small.json").read_text())
        goals = sorted(set(a81["goal_no"].to_list()))
        abg = {g: sorted(set(a81.filter(pl.col("goal_no") == g)["agent"].to_list())) for g in goals}
        P2 = projectors(V, idx, regime, goals, abg)
        pdiff = max(float(np.abs(P[k] - P2[k]).max()) for k in P)
        for meth in ("fe", "mean"):
            mu_ref = L.personal_vectors(pan, Xp, method=meth)
            mu = personal_vectors(pan.agent, pan.goal, Xp, method=meth)
            same = mu_ref.keys() == mu.keys() and all(np.array_equal(mu_ref[k], mu[k]) for k in mu)
            res[f"personal_vectors {meth} regime {regime}"] = "identical" if same else "differ"
            ok &= same
        res[f"projectors regime {regime}"] = "identical" if pdiff == 0 else f"max_abs_diff {pdiff:.2e}"
        ok &= pdiff == 0
    # H82 prior (read-only import of h82lib.Data on H82's own folder)
    L82 = _ro_import(ROOT / "hypotheses/H82-remanence-endogenous-field/analysis/h82lib.py", "_h82lib_ro")
    D = L82.Data("bge_small")
    bad = n = 0
    for a in np.unique(D.agent)[:12]:
        for reg in ("I", "III"):
            for g in D.goals_in_regime(reg)[:6]:
                p1 = D.prior(int(a), reg, {g})
                p2 = prior_mean(D.X, D.agent, D.goal, D.regime, int(a), reg, {g})
                n += 1
                bad += not ((p1 is None and p2 is None) or (p1 is not None and p2 is not None and np.array_equal(p1, p2)))
    res["H82 prior_mean"] = {"checked": n, "mismatches": bad}
    ok &= bad == 0
    res["ok"] = bool(ok)
    print(json.dumps(res, indent=1), flush=True)
    return ok


if __name__ == "__main__":
    if "--verify" in sys.argv:
        sys.exit(0 if verify() else 1)
    build()
