"""H34 round 2, R4: semantic ideas by online leader clustering of DQ5 chat embeddings (first-story detection).

Rule (card, "Round 2 / R4"): every non-holdout chat message with >= 40 characters, in time order. Message m is a use of
every existing seed with cos(m, seed) >= theta; with none, m founds a new seed (a new idea, first used at t_m). Seeds
never move. Novelty: an idea of period g is a seed founded in g. Embeddings are read as numbers; no text is used.

  uv run python hypotheses/H34-idea-cascades/scheme/build_semantic.py ratematch            # theta_gte for theta_bge
  uv run python hypotheses/H34-idea-cascades/scheme/build_semantic.py cluster MODEL THETA   # uses + seeds tables
  H34_DATA=r1b uv run python hypotheses/H34-idea-cascades/scheme/build_semantic.py build MODEL THETA   # trees per period
  uv run python hypotheses/H34-idea-cascades/scheme/build_semantic.py synth                # S-R4 planted paraphrases
Outputs: data/processed/H34-idea-cascades/r2/semantic/ and r2/sem_<model>[_<theta>]/G<NN>/
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
import time
import zlib
from multiprocessing import Pool
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(HERE))
from common import REVISION, git_commit, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
ED = SH / "embeddings"
OUT = ROOT / "data/processed/H34-idea-cascades"
R2 = OUT / "r2"
SEM = R2 / "semantic"
MIN_CHARS = 40
THETA_BGE = 0.90
BLOCK = 1024
N_WORKERS = 2
MODELS = {"bge_small": "chat_bge_small.npy", "gte_modernbert": "chat_gte_modernbert.npy"}
CLS_SEM = 4


def corpus() -> pl.DataFrame:
    """Non-holdout chat messages (any speaker kind) with >= MIN_CHARS characters, in chat_core row order (sorted by t),
    with their embedding row."""
    chat = (pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "pt_date", "goal_no", "speaker_kind",
                                                                "agent", "length"]).with_row_index("msg"))
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "holdout"])
    chat = chat.join(cal, on="pt_date", how="left")
    hm = np.array(holdout_mask(chat["pt_date"].to_list(), chat["goal_no"].to_list()))
    keep = ~hm & ~chat["holdout"].fill_null(False).to_numpy() & (chat["length"].fill_null(0).to_numpy() >= MIN_CHARS)
    chat = chat.filter(pl.Series(keep)).drop("holdout")
    idx = pl.read_parquet(ED / "chat_index.parquet").with_row_index("erow")
    chat = chat.join(idx, on="message_id", how="inner").sort("msg")
    return chat


def load_emb(model: str, rows: np.ndarray) -> np.ndarray:
    E = np.load(ED / MODELS[model], mmap_mode="r")
    out = np.empty((len(rows), E.shape[1]), dtype=np.float32)
    for i in range(0, len(rows), 50_000):
        out[i:i + 50_000] = E[rows[i:i + 50_000]]
    out /= np.maximum(np.linalg.norm(out, axis=1, keepdims=True), 1e-6)
    return out


def leader_cluster(X: np.ndarray, theta: float, n_prior: int = 0, verbose: bool = True):
    """Online leader clustering over the rows of X (time order). Returns
    seed_of_row  (n,) seed index founded by the row, or -1
    uses         (U, 2) [row, seed] for every seed within theta of the row (multi-membership; a seed uses itself)
    nearest      (n,) the nearest seed within theta (the founded seed for seeds)."""
    n, d = X.shape
    seeds = np.empty((n, d), dtype=np.float32)
    seed_row = np.empty(n, dtype=np.int64)
    ns = 0
    seed_of_row = np.full(n, -1, dtype=np.int64)
    nearest = np.full(n, -1, dtype=np.int64)
    U_r, U_s = [], []
    t0 = time.time()
    for b0 in range(0, n, BLOCK):
        Xb = X[b0:b0 + BLOCK]
        nb = len(Xb)
        if ns:
            Sp = Xb @ seeds[:ns].T
            hit = Sp >= theta
            rr, ss = np.nonzero(hit)
            best_prev = np.where(hit.any(1), Sp.argmax(1), -1)
            best_prev_v = np.where(hit.any(1), Sp.max(1), -1.0)
        else:
            rr = ss = np.zeros(0, dtype=np.int64)
            best_prev = np.full(nb, -1); best_prev_v = np.full(nb, -1.0)
        U_r.append(rr + b0); U_s.append(ss)
        XX = Xb @ Xb.T
        new_local = []          # local indices of rows that founded seeds in this block
        for i in range(nb):
            bi, bv = int(best_prev[i]), float(best_prev_v[i])
            if new_local:
                nl = np.array(new_local)
                sims = XX[i, nl]
                h = np.nonzero(sims >= theta)[0]
                if len(h):
                    sid = seed_of_row[b0 + nl[h]]
                    U_r.append(np.full(len(h), b0 + i)); U_s.append(sid)
                    j = int(np.argmax(sims[h]))
                    if sims[h][j] > bv:
                        bi, bv = int(sid[j]), float(sims[h][j])
            if bi < 0:
                seeds[ns] = Xb[i]
                seed_row[ns] = b0 + i
                seed_of_row[b0 + i] = ns
                U_r.append(np.array([b0 + i])); U_s.append(np.array([ns]))
                nearest[b0 + i] = ns
                new_local.append(i)
                ns += 1
            else:
                nearest[b0 + i] = bi
        if verbose and (b0 // BLOCK) % 25 == 0:
            print(f"  {b0 + nb}/{n} rows, {ns} seeds, {time.time() - t0:.0f}s", flush=True)
    uses = np.stack([np.concatenate(U_r), np.concatenate(U_s)], 1).astype(np.int64)
    return seed_of_row, uses, nearest, seed_row[:ns]


def tag(model: str, theta: float) -> str:
    return f"sem_{model}" + ("" if abs(theta - default_theta(model)) < 1e-9 else f"_{theta:.3f}")


def default_theta(model: str) -> float:
    if model == "bge_small":
        return THETA_BGE
    p = SEM / "ratematch.json"
    return json.loads(p.read_text())["theta"][model][f"{THETA_BGE:.2f}"] if p.exists() else np.nan


# ============================================================================================ rate matching
def ratematch(n_sample: int = 20_000, seed: int = 0):
    ch = corpus()
    rng = np.random.default_rng(seed)
    ag = ch.filter(pl.col("speaker_kind") == "agent")
    samp = np.sort(rng.choice(ag.height, min(n_sample, ag.height), replace=False))
    srows = ag[samp]
    maxcos = {}
    for model in MODELS:
        X = load_emb(model, ch["erow"].to_numpy())
        pos = {int(m): i for i, m in enumerate(ch["msg"].to_numpy())}
        goal = ch["goal_no"].to_numpy()
        mc = np.full(srows.height, np.nan, dtype=np.float32)
        for g in np.unique(srows["goal_no"].to_numpy()):
            sel = np.where(srows["goal_no"].to_numpy() == g)[0]
            gi = np.where(goal == g)[0]                      # rows of period g, time order
            si = np.array([pos[int(m)] for m in srows["msg"].to_numpy()[sel]])
            Sg = X[si] @ X[gi].T                             # (sample in g, period rows)
            earlier = gi[None, :] < si[:, None]
            Sg = np.where(earlier, Sg, -2.0)
            mc[sel] = Sg.max(1)
        maxcos[model] = mc
        del X
    ok = np.isfinite(maxcos["bge_small"]) & (maxcos["bge_small"] > -1.5) & (maxcos["gte_modernbert"] > -1.5)
    out = {"n_sample": int(ok.sum()), "theta": {"bge_small": {}, "gte_modernbert": {}}, "share": {}}
    for tb in (0.85, 0.90, 0.95):
        share = float((maxcos["bge_small"][ok] >= tb).mean())
        tg = float(np.quantile(maxcos["gte_modernbert"][ok], 1 - share))
        out["theta"]["bge_small"][f"{tb:.2f}"] = tb
        out["theta"]["gte_modernbert"][f"{tb:.2f}"] = tg
        out["share"][f"{tb:.2f}"] = share
    SEM.mkdir(parents=True, exist_ok=True)
    (SEM / "ratematch.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


# ============================================================================================ clustering
def cluster(model: str, theta: float):
    ch = corpus()
    X = load_emb(model, ch["erow"].to_numpy())
    t0 = time.time()
    seed_of_row, uses, nearest, seed_rows = leader_cluster(X, theta)
    msg = ch["msg"].to_numpy().astype(np.uint32)
    goal = ch["goal_no"].to_numpy()
    tg = tag(model, theta)
    od = SEM / tg
    od.mkdir(parents=True, exist_ok=True)
    pl.DataFrame({"msg": msg[uses[:, 0]], "marker": uses[:, 1].astype(np.int64),
                  "cls": np.full(len(uses), CLS_SEM, dtype=np.uint8)}).write_parquet(od / "uses.parquet", compression="zstd")
    pl.DataFrame({"msg": msg, "marker": nearest.astype(np.int64), "cls": np.full(len(msg), CLS_SEM, dtype=np.uint8)}) \
        .write_parquet(od / "uses_nearest.parquet", compression="zstd")
    fs = pl.DataFrame({"marker": np.arange(len(seed_rows), dtype=np.int64), "first_msg": msg[seed_rows],
                       "first_goal": goal[seed_rows]})
    cnt = pl.DataFrame({"marker": uses[:, 1].astype(np.int64)}).group_by("marker").len().rename({"len": "n_msgs"})
    fs = fs.join(cnt, on="marker", how="left")
    fs.write_parquet(od / "first_seen.parquet", compression="zstd")
    meta = dict(model=model, theta=theta, n_rows=int(len(msg)), n_seeds=int(len(seed_rows)), n_uses=int(len(uses)),
                seed_share=float(len(seed_rows) / len(msg)), uses_per_msg=float(len(uses) / len(msg)),
                secs=round(time.time() - t0, 1), git_commit=git_commit(), built_at=dt.datetime.now(dt.timezone.utc).isoformat())
    (od / "meta.json").write_text(json.dumps(meta, indent=1))
    print(json.dumps(meta, indent=1))


# ============================================================================================ trees (round-1b assembler)
_SH = None
_USES = None
_FS = None


def _binit(model, theta, nearest):
    global _SH, _USES, _FS
    sys.path.insert(0, str(HERE))
    import h34core as C
    assert C.R1B, "set H34_DATA=r1b (ledger visibility)"
    _SH = C.Shared()
    od = SEM / tag(model, theta)
    _USES = pl.read_parquet(od / ("uses_nearest.parquet" if nearest else "uses.parquet"))
    _FS = pl.read_parquet(od / "first_seen.parquet")


def room_size(inp: dict) -> int:
    """Median room size (recipients + sender) of agent messages; same rule as scheme/build.py room_size."""
    am = inp["kind"] == 0
    E = inp["E"][am]
    snd = inp["sender"][am].astype(np.int64)
    inc = E[np.arange(len(snd)), snd]
    return int(np.median(E.sum(1) + (~inc).astype(int)))


def build_period(task):
    g, out_tag = task
    import h34core as C
    t0 = time.time()
    days = _SH.period_days(g)
    chat = _SH.chat.filter((pl.col("goal_no") == g) & pl.col("pt_date").is_in(days))
    rows = chat["msg"].to_numpy()
    ideas = _FS.filter(pl.col("first_goal") == g)["marker"].to_numpy()
    uses = _USES.filter(pl.col("msg").is_in(rows) & pl.col("marker").is_in(ideas))
    inp = C.period_inputs(_SH, g, days=days, uses=uses)
    res = C.assemble(inp, atrisk_cap=4000, seed=g)
    od = R2 / out_tag / f"G{g:02d}"
    od.mkdir(parents=True, exist_ok=True)
    for k in ("first_uses", "trees", "atrisk", "jitter", "roomx"):
        res[k].write_parquet(od / f"{k}.parquet", compression="zstd")
    meta = dict(res["meta"])
    meta.update(goal=g, days=inp["days"], N_room=room_size(inp), N_roster_active=meta["n_agents"], n_uses=int(len(inp["use_pos"])),
                secs=round(time.time() - t0, 1), tag=out_tag)
    (od / "meta.json").write_text(json.dumps(meta, indent=1))
    print(f"G{g:02d} [{out_tag}]: {meta['n_ideas']} ideas, {res['first_uses'].height} first uses, {res['trees'].height} trees, "
          f"{meta['secs']}s", flush=True)
    return {k: v for k, v in meta.items() if k != "days"}


def build(model: str, theta: float, nearest: bool = False):
    periods = sorted(int(p.name[1:]) for p in (OUT / "r1b").glob("G*") if (p / "meta.json").exists())
    out_tag = tag(model, theta) + ("_nearest" if nearest else "")
    order = sorted(periods, key=lambda g: -1 if g == 51 else g)
    with Pool(N_WORKERS, initializer=_binit, initargs=(model, theta, nearest)) as pool:
        metas = pool.map(build_period, [(g, out_tag) for g in order], chunksize=1)
    od = R2 / out_tag
    pl.DataFrame(metas, infer_schema_length=None).write_parquet(od / "periods_meta.parquet")
    prov = {"built_by": "hypotheses/H34-idea-cascades/scheme/build_semantic.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["shared/chat_core", "shared/embeddings/chat_index", f"shared/embeddings/{MODELS[model]}",
                                   "shared/context_ledger_items", "shared/call_windows", "shared/events_core", "shared/roster",
                                   "shared/calendar"]}],
            "params": {"model": model, "theta": theta, "min_chars": MIN_CHARS, "assignment": "nearest" if nearest else "multi",
                       "visibility": "DQ1 context ledger (round-1b assembler)"},
            "periods": periods, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (od / "_provenance.json").write_text(json.dumps(prov, indent=1))


# ============================================================================================ S-R4 synthetic
SYN_PERIODS = {42: None, 51: ("2026-07-27", "2026-08-08")}
N_PRIOR = 20_000


def synth_task(task):
    g, model, q, eps, rep = task
    sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "analysis"))
    import h34core as C
    from r2_mixture import simulate_ideas_het
    assert not C.R1B
    rng = np.random.default_rng(zlib.crc32(repr(task).encode()))
    sh = C.Shared()
    days = sh.period_days(g)
    if SYN_PERIODS[g]:
        days = [d for d in days if SYN_PERIODS[g][0] <= d < SYN_PERIODS[g][1]]
    empty = pl.DataFrame(schema={"msg": pl.UInt32, "marker": pl.Int64, "cls": pl.UInt8})
    inp = C.period_inputs(sh, g, days=days, uses=empty)
    n_ideas = 600
    upos, umk = simulate_ideas_het(inp, n_ideas, np.full(n_ideas, q), eps, rng)
    # one planted idea per message: keep the first planted use of each message
    order = np.lexsort((umk, upos))
    upos, umk = upos[order], umk[order]
    first = np.r_[True, upos[1:] != upos[:-1]]
    upos, umk = upos[first], umk[first]
    ch = corpus()
    period_msgs = inp["rows"]
    pr = ch.filter(pl.col("msg") < int(period_msgs.min())).tail(N_PRIOR)
    pc = ch.filter(pl.col("msg").is_in(period_msgs))
    allc = pl.concat([pr, pc])
    X = load_emb(model, allc["erow"].to_numpy())
    row_of_msg = {int(m): i for i, m in enumerate(allc["msg"].to_numpy())}
    pos_msg = period_msgs[upos]                       # chat msg ids of planted uses
    has = np.array([int(m) in row_of_msg for m in pos_msg])
    upos, umk, pos_msg = upos[has], umk[has], pos_msg[has]
    # seeds = first planted use of each idea (time order); paraphrase the others
    cs = np.ones(len(upos))
    seed_vec = {}
    for i in np.argsort(upos, kind="stable"):
        r = row_of_msg[int(pos_msg[i])]
        k = int(umk[i])
        if k not in seed_vec:
            seed_vec[k] = X[r].copy()
            continue
        e0 = seed_vec[k]
        c = rng.uniform(0.80, 1.00)
        v = X[r] - (X[r] @ e0) * e0
        v /= max(np.linalg.norm(v), 1e-6)
        X[r] = c * e0 + np.sqrt(1 - c * c) * v
        cs[i] = c
    theta = THETA_BGE if model == "bge_small" else default_theta(model)
    seed_of_row, uses, nearest, seed_rows = leader_cluster(X, theta, verbose=False)
    msgs = allc["msg"].to_numpy()
    in_period = np.isin(msgs, period_msgs)
    period_seeds = set(seed_of_row[in_period & (seed_of_row >= 0)].tolist())
    U = pl.DataFrame({"msg": msgs[uses[:, 0]].astype(np.uint32), "marker": uses[:, 1]})
    U = U.filter(pl.col("marker").is_in(list(period_seeds)) & pl.col("msg").is_in(period_msgs))
    # planted ideas whose seed founded a period seed
    seed_first = {}
    for i in np.argsort(upos, kind="stable"):
        seed_first.setdefault(int(umk[i]), int(pos_msg[i]))
    planted_seed_id = {k: int(seed_of_row[row_of_msg[m]]) for k, m in seed_first.items()}
    recovered = {k: s for k, s in planted_seed_id.items() if s >= 0 and s in period_seeds}
    pos_of_msg = {int(m): i for i, m in enumerate(period_msgs)}

    def run(use_pos, use_mk):
        inp2 = dict(inp)
        inp2.update(use_pos=np.asarray(use_pos, np.int64), use_marker=np.asarray(use_mk, np.int64),
                    use_cls=np.full(len(use_pos), 2, dtype=np.int8))
        r = C.assemble(inp2, atrisk_cap=len(set(use_mk)) + 1, seed=rep)
        fu = r["first_uses"]
        R = float(((fu["status"] == 1) & (fu["parent"] >= 0)).mean()) if fu.height else np.nan
        dr = None
        from h34stats import dose_response
        if r["atrisk"].height:
            dr = dose_response(r["atrisk"], B=100, kcol="krbin")
        hr = dr["hr10"] if dr else np.nan
        return fu, R, hr
    # truth restricted to recovered planted ideas and uses with c >= theta (plus seeds)
    keep_t = np.array([int(umk[i]) in recovered and cs[i] >= theta for i in range(len(upos))])
    fu_t, R_t, hr_t = run(upos[keep_t], umk[keep_t])
    keep_all = np.array([int(umk[i]) in recovered for i in range(len(upos))])
    fu_ta, R_ta, _ = run(upos[keep_all], umk[keep_all])
    # recovered semantic ideas of planted seeds
    Ur = U.filter(pl.col("marker").is_in(list(recovered.values())))
    sem_pos = np.array([pos_of_msg[int(m)] for m in Ur["msg"].to_numpy()], np.int64)
    fu_s, R_s, hr_s = run(sem_pos, Ur["marker"].to_numpy())
    # false adopters: agent first uses in the recovered ideas that are not planted users of that idea
    inv = {s: k for k, s in recovered.items()}
    planted_users = set()
    for i in range(len(upos)):
        if int(umk[i]) in recovered:
            planted_users.add((recovered[int(umk[i])], int(inp["sender"][upos[i]])))
    fa = sum((int(r_["idea"]), int(r_["agent"])) not in planted_users for r_ in fu_s.iter_rows(named=True)) if fu_s.height else 0
    # all period semantic ideas (real + planted), q = 0 check uses R_c on everything planted only
    out = dict(goal=g, model=model, q=q, eps=eps, rep=rep, theta=theta, n_planted=len(seed_first), n_recovered=len(recovered),
               novelty_loss=1 - len(recovered) / max(len(seed_first), 1), R_true_theta=R_t, R_true_all=R_ta, R_sem=R_s,
               hr10_true=hr_t, hr10_sem=hr_s, Rc_sem=R_s * max(0.0, 1 - 1 / hr_s) if np.isfinite(hr_s) and hr_s > 0 else np.nan,
               first_uses_true=int(fu_t.height), first_uses_sem=int(fu_s.height), false_adopters=int(fa),
               false_adopter_share=fa / max(int(fu_ta.height), 1), n_inv=len(inv))
    print(out, flush=True)
    return out


def synth():
    os.environ.pop("H34_DATA", None)
    tasks = []
    for g in SYN_PERIODS:
        for model in MODELS:
            for q, eps, reps in ((0.015, 0.0005, 2), (0.0, 0.002, 2)):
                for rep in range(reps):
                    tasks.append((g, model, q, eps, rep))
    with Pool(N_WORKERS) as pool:
        res = pool.map(synth_task, tasks, chunksize=1)
    SEM.mkdir(parents=True, exist_ok=True)
    df = pl.DataFrame(res, infer_schema_length=None)
    df.write_parquet(SEM / "synth_r4.parquet")
    with pl.Config(tbl_rows=50, tbl_cols=25, tbl_width_chars=250, float_precision=3):
        print(df)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "ratematch":
        ratematch()
    elif cmd == "cluster":
        cluster(sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else default_theta(sys.argv[2]))
    elif cmd == "build":
        m = sys.argv[2]
        th = float(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3] != "-" else default_theta(m)
        build(m, th, nearest="--nearest" in sys.argv)
    elif cmd == "synth":
        synth()
