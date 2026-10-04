"""H61 scheme: one row per agent-seeded idea with its first-use features and its 24-h reach (no text).

  uv run python hypotheses/H61-contagiousness-at-first-use/scheme/build.py [--goals 38,51]

Definitions: ../README.md, "Operational definitions" (written 2026-10-04 19:15 UTC).
Inputs: infra/shared/idea_ledger.py (chat timeline, DQ1 ledger reads, H34 markers, DQ2 parents, mentions), DQ5 chat
embeddings (bge-small, gte-modernbert) and embeddings/goals.parquet (kickoff field). Held-out days never enter.
Output: data/processed/H61-contagiousness-at-first-use/G<NN>/ideas.parquet (+ _provenance.json).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "4")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
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
from common import REVISION, git_commit  # noqa: E402
from embed_models import load_whitener, goal_vectors, emb_path  # noqa: E402

OUT = ROOT / "data/processed/H61-contagiousness-at-first-use"
SH = ROOT / "data/processed/shared"
US = IL.US
H24 = 24 * 3600 * US
LAG5 = 300 * US
# the 32 non-holdout periods H34 analysed
GOALS = [5, 6, 7, 8, 10, 11, 12, 13, 16, 17, 18, 19, 20, 21, 23, 24, 25, 26, 27, 30, 31, 33, 35, 36, 37, 38, 39, 40,
         41, 42, 44, 51]
MODELS = ("bge_small", "gte_modernbert")


class Emb:
    def __init__(self):
        self.idx = pl.read_parquet(SH / "embeddings/chat_index.parquet").with_row_index("erow")
        self.E = {m: np.load(emb_path("chat", m), mmap_mode="r") for m in MODELS}
        self.goals = pl.read_parquet(SH / "embeddings/goals.parquet").with_row_index("grow")
        self.G = {m: goal_vectors(m) for m in MODELS}
        self.W = {}

    def whit(self, regime: str, m: str):
        if (regime, m) not in self.W:
            self.W[(regime, m)] = load_whitener(regime, 32, m)
        return self.W[(regime, m)]

    def field(self, g: int, room: int, m: str, regime: str) -> np.ndarray:
        gg = self.goals.filter(pl.col("goal_no") == g)
        for cond in ((pl.col("kind") == "kickoff_room") & (pl.col("room") == room), pl.col("kind") == "kickoff",
                     pl.col("kind") == "goal"):
            r = gg.filter(cond)
            if r.height:
                v = self.whit(regime, m)(self.G[m][int(r["grow"][0])][None, :])[0]
                return v / np.linalg.norm(v)
        return None


def regime_of(base: IL.Base, days: list[str]) -> str:
    r = base.cal.filter(pl.col("pt_date").is_in(days))["regime"].drop_nulls()
    return r.mode()[0] if r.len() else "III"


def build_period(base: IL.Base, emb: Emb, g: int, P: dict | None = None) -> pl.DataFrame | None:
    """P may be supplied (confirm.py builds held-out timelines with allow_holdout); default: non-holdout days."""
    P = IL.load_period(base, g) if P is None else P
    if P is None:
        return None
    t, kind, sender, TS, cs, room, day = P["t"], P["kind"], P["sender"], P["TS"], P["cs"], P["room"], P["day"]
    regime = regime_of(base, P["days"])
    agent_msg = (kind == 0) & (sender >= 0)
    t_last = int(t[agent_msg].max())
    # presence: agents who posted in (room, day)
    pres = {}
    for r_, d_, a_ in zip(room[agent_msg], day[agent_msg], sender[agent_msg]):
        if int(a_) in P["cc"]:
            continue
        pres.setdefault((int(r_), int(d_)), set()).add(int(a_))
    # poster history: message times, replies received (time of the replying message)
    msg_t = {}
    for a in np.unique(sender[agent_msg]):
        msg_t[int(a)] = t[agent_msg & (sender == a)]
    par = P["parent"]
    rec = {}
    for b in np.where(par >= 0)[0]:
        a_par = int(sender[par[b]]) if kind[par[b]] == 0 else -1
        if a_par >= 0 and kind[b] == 0 and int(sender[b]) != a_par:
            rec.setdefault(a_par, []).append(t[b])
    rec = {a: np.sort(np.array(v)) for a, v in rec.items()}
    # embeddings of every agent message (whitened, unit) for both models; fields per room
    mids = pl.DataFrame({"message_id": P["message_id"], "pos": np.arange(len(t))})
    ej = mids.join(emb.idx, on="message_id", how="left")
    erow = ej.sort("pos")["erow"].to_numpy()
    groups = list(IL.ideas_grouped(P))
    first_pos = np.array([int(pos[0]) for _, _, pos in groups])
    n_novel_at = {}
    for fp in first_pos:
        n_novel_at[int(fp)] = n_novel_at.get(int(fp), 0) + 1
    seed_positions = sorted({int(fp) for fp in first_pos if kind[fp] == 0 and sender[fp] >= 0
                             and int(sender[fp]) not in P["cc"]})
    spec = {m: {} for m in MODELS}
    for m in MODELS:
        W = emb.whit(regime, m)
        fields = {}
        sp = [p for p in seed_positions if erow[p] is not None and not np.isnan(erow[p])] if erow.dtype.kind == "f" \
            else [p for p in seed_positions if erow[p] is not None]
        if not sp:
            continue
        V = W(np.asarray(emb.E[m][np.array([int(erow[p]) for p in sp])], dtype=np.float32))
        V /= np.linalg.norm(V, axis=1, keepdims=True)
        for p, v in zip(sp, V):
            r_ = int(room[p])
            if r_ not in fields:
                fields[r_] = emb.field(g, r_, m, regime)
            f = fields[r_]
            spec[m][p] = float(1.0 - v @ f) if f is not None else np.nan
    rows = []
    for mk, cl, pos in groups:
        first = int(pos[0])
        if kind[first] != 0 or sender[first] < 0 or int(sender[first]) in P["cc"]:
            continue
        t0 = int(t[first])
        if t0 + H24 > t_last:
            continue                                        # right-censored
        p = int(sender[first])
        fu = IL.first_uses(P, pos)
        spk = np.where(kind[pos] == 0, sender[pos].astype(np.int64), -100 - kind[pos].astype(np.int64))
        reach = 1
        n_exp = n_unexp = n_read5 = n_unr5 = n_old = 0
        for a, u in fu.items():
            if u == first or t[u] > t0 + H24:
                continue
            reach += 1
            prior = (pos < u) & (spk != a)
            pp = pos[prior]
            vis = TS[pp, a] <= cs[u]
            if vis.any():
                n_exp += 1
            else:
                n_unexp += 1
            rec5 = t[pp] > t[u] - LAG5
            if rec5.any():
                tsr = TS[pp[rec5], a]
                if (tsr <= cs[u]).any():
                    n_read5 += 1
                elif ((tsr > cs[u]) & (tsr < IL.INF_US)).any():
                    n_unr5 += 1
            elif vis.any():
                n_old += 1
        r_, d_ = int(room[first]), int(day[first])
        others = sorted(pres.get((r_, d_), set()) - {p})
        n_pres = len(others) + 1
        if others:
            dl = TS[first, np.array(others)] - t0
            n_rec = int(((dl >= 0) & (dl <= LAG5)).sum())
        else:
            n_rec = 0
        mt = msg_t.get(p, np.zeros(0, np.int64))
        M_p = int(np.searchsorted(mt, t0, side="left"))
        rr = rec.get(p, np.zeros(0, np.int64))
        R_p = int(np.searchsorted(rr, t0, side="left"))
        named = [x for x in P["named"][first] if x != p]
        rows.append(dict(
            goal=g, idea=mk, cls=cl, seed_pos=first, seed_msg=int(P["rows"][first]), poster=p, room=r_, day=d_,
            t0_us=t0, n_novel=n_novel_at[first], seed_len=int(P["length"][first]),
            spec_bge=spec["bge_small"].get(first, np.nan), spec_gte=spec["gte_modernbert"].get(first, np.nan),
            indeg=(R_p + 1) / (M_p + 2), R_p=R_p, M_p=M_p, n_present=n_pres, n_receptive=n_rec,
            f_receptive=(n_rec / (n_pres - 1)) if n_pres > 1 else 0.0, addressed=bool(named),
            threaded=bool(par[first] >= 0), reach24=reach, n_exposed=n_exp, n_unexposed=n_unexp, n_read5=n_read5,
            n_unread5=n_unr5, n_read_old=n_old, regime=regime))
    if not rows:
        return None
    return pl.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--goals", default="")
    a = ap.parse_args()
    goals = [int(x) for x in a.goals.split(",")] if a.goals else GOALS
    base = IL.Base()
    emb = Emb()
    for g in goals:
        t_s = time.time()
        df = build_period(base, emb, g)
        if df is None:
            print(f"G{g:02d}: no ideas")
            continue
        (OUT / f"G{g:02d}").mkdir(parents=True, exist_ok=True)
        df.write_parquet(OUT / f"G{g:02d}/ideas.parquet", compression="zstd")
        print(f"G{g:02d}: {df.height} seeded ideas (uncensored), {time.time() - t_s:.1f}s")
    prov = {"built_by": "hypotheses/H61-contagiousness-at-first-use/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["shared/chat_core", "shared/calendar", "shared/roster", "shared/call_windows",
                                   "shared/context_ledger_items", "shared/reply_pairs", "shared/chat_mentions_clean",
                                   "shared/embeddings/chat_{bge_small,gte_modernbert}.npy",
                                   "shared/embeddings/goals.parquet", "H34-idea-cascades/markers (data, hashes)"]}],
            "params": {"horizon_h": 24, "lag5_s": 300, "receptive_s": 300, "holdout": "excluded (holdout_mask)",
                       "loader": "infra/shared/idea_ledger.py"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    main()
