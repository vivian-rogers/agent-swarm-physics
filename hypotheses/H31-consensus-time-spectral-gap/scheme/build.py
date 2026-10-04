"""H31 scheme: reading schedules, block windows, project states and content alignment, per goal period.

  uv run python hypotheses/H31-consensus-time-spectral-gap/scheme/build.py               # all non-holdout periods 10-44
  uv run python hypotheses/H31-consensus-time-spectral-gap/scheme/build.py --goals 26 31

Definitions are in the card (`../README.md`, "Data scheme" and "Observables"). Summary:
- turns of agent i: `actions` minus `pause` mirrors, plus `events_core` agent events (H18's `turn_times`, imported);
- reads: for each `exposure` row (agent message m -> roster recipient i != sender), t_seen = i's first turn strictly
  after t_m (call-start visibility, H18), t_upd = i's first turn after t_seen + 1 s (output of the call that saw m);
- active time: calendar.active_offset_s + clip(t - win_start, 0, window_s), rebased to the period's first day;
- block = room; block_windows gives roster agents per room per 30-min window (room at the window midpoint);
- project states: H11's labels_project_w{15,30,60} (imported unchanged; carry-forward is applied in analysis);
- content alignment: per block x 30-min window, mean pairwise cosine of whitened (regime whitener, d = 32),
  unit-normalized agent_win30 vectors, >= 3 agents.

Outputs (data/processed/H31-consensus-time-spectral-gap/G<NN>/, zstd parquet, no text): msgs, reads, turns,
block_windows, states_project_w{15,30,60}, alignment, kicks; _provenance.json at the folder root.
Holdout days are dropped before anything is computed unless --allow-holdout (only analysis/confirm_holdout.py).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("POLARS_MAX_THREADS", "2")
os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(ROOT / "hypotheses/H18-attention-dilution/analysis"))
from common import REVISION, git_commit, holdout_mask, load_holdout, load_whitener  # noqa: E402


def _load_h18():
    """H18's scheme module (for turn_times), loaded by path under a unique name; imported, never modified."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("h18_scheme_build", ROOT / "hypotheses/H18-attention-dilution/scheme/build.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


h18build = _load_h18()

SH = ROOT / "data/processed/shared"
H11 = ROOT / "data/processed/H11-potts-labor-vs-herding"
OUT = ROOT / "data/processed/H31-consensus-time-spectral-gap"
W_MIN = 30
GUARD_S = 1.0
KIND = {"agent": 0, "human": 1, "automated": 2}


def _us(s: pl.Series) -> np.ndarray:
    return s.dt.epoch("us").to_numpy().astype(np.int64)


class Shared:
    def __init__(self):
        self.cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("n_agent_events") > 0)
        chat = pl.read_parquet(SH / "chat_core.parquet",
                               columns=["message_id", "t", "pt_date", "goal_no", "room", "speaker_kind", "agent"]
                               ).with_row_index("msg")
        men = pl.read_parquet(SH / "chat_mentions_clean.parquet", columns=["mentions_roster"])
        self.chat = pl.concat([chat, men], how="horizontal_extend")
        self.exposure = pl.read_parquet(SH / "exposure.parquet", columns=["msg", "agent"])
        self.ev = pl.read_parquet(SH / "events_core.parquet", columns=["t", "pt_date", "actor_kind", "agent", "action_type"]
                                  ).filter((pl.col("actor_kind") == "agent") & pl.col("agent").is_not_null())
        self.roster = pl.read_parquet(SH / "roster.parquet")
        self.rooms_tl = pl.read_parquet(SH / "rooms_timeline.parquet").sort("agent", "t_start")
        self.kicks = pl.read_parquet(SH / "kicks.parquet")
        self.cc = set(self.roster.filter(pl.col("claude_code"))["agent"].to_list())


def period_days(sh: Shared, g: int, allow_holdout: bool) -> pl.DataFrame:
    cal = sh.cal.filter(pl.col("goal_no") == g).sort("pt_date")
    if not allow_holdout:
        m = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
        cal = cal.filter(~pl.Series(m) & ~pl.col("holdout"))
    if cal.height == 0:
        return cal
    off0 = cal["active_offset_s"][0]
    return cal.with_columns((pl.col("active_offset_s") - off0).alias("act0"),
                            pl.col("pt_date").rank("dense").cast(pl.Int16).sub(1).alias("day"))


class ActiveClock:
    """Wall-clock (us since epoch) -> active seconds since the period's first day (clipped into each day's window)."""

    def __init__(self, cal: pl.DataFrame):
        self.ws = _us(cal["win_start"])
        self.we = _us(cal["win_end"])
        self.a0 = cal["act0"].to_numpy().astype(np.float64)
        self.wlen = cal["window_s"].to_numpy().astype(np.float64)
        self.dates = cal["pt_date"].to_list()

    def __call__(self, t_us: np.ndarray) -> np.ndarray:
        t_us = np.asarray(t_us, dtype=np.int64)
        k = np.searchsorted(self.ws, t_us, side="right") - 1
        kc = np.clip(k, 0, len(self.ws) - 1)
        off = np.clip((t_us - self.ws[kc]) / 1e6, 0, self.wlen[kc])
        out = self.a0[kc] + off
        return np.where(k < 0, 0.0, out)


def window_grid(cal: pl.DataFrame, W: int = W_MIN) -> pl.DataFrame:
    rows = []
    for r in cal.iter_rows(named=True):
        nk = int(-(-r["window_s"] // (W * 60))) if r["window_s"] else 1
        for k in range(max(nk, 1)):
            t_mid = r["win_start"] + dt.timedelta(seconds=k * W * 60 + W * 30)
            rows.append({"pt_date": r["pt_date"], "day": r["day"], "win": k, "t_mid": t_mid,
                         "act_mid": float(r["act0"] + min(k * W * 60 + W * 30, r["window_s"]))})
    return pl.DataFrame(rows, schema={"pt_date": pl.String, "day": pl.Int16, "win": pl.Int16,
                                      "t_mid": pl.Datetime("us", "UTC"), "act_mid": pl.Float64})


def rooms_at(sh: Shared, agents: list[int], t_us: np.ndarray) -> dict[int, np.ndarray]:
    out = {}
    for a in agents:
        sub = sh.rooms_tl.filter(pl.col("agent") == a)
        if sub.height == 0:
            out[a] = np.full(len(t_us), -1, np.int16)
            continue
        ts, te = _us(sub["t_start"]), sub["t_end"].dt.epoch("us").fill_null(np.iinfo(np.int64).max).to_numpy()
        rm = sub["room"].to_numpy()
        idx = np.searchsorted(ts, t_us, side="right") - 1
        ok = (idx >= 0) & (t_us < te[np.clip(idx, 0, None)])
        out[a] = np.where(ok, rm[np.clip(idx, 0, None)], -1).astype(np.int16)
    return out


def build_period(sh: Shared, g: int, allow_holdout: bool = False, verbose: bool = True) -> dict | None:
    cal = period_days(sh, g, allow_holdout)
    if cal.height == 0:
        return None
    days = cal["pt_date"].to_list()
    clock = ActiveClock(cal)
    t0 = cal["win_start"].min() - dt.timedelta(hours=2)
    t1 = cal["win_end"].max() + dt.timedelta(hours=26)
    ros = sh.roster.filter(~pl.col("claude_code"))
    roster_agents = set(ros["agent"].to_list())

    # ---- messages (all speaker kinds; agent ones are graph edges, others are kicks)
    chat = sh.chat.filter(pl.col("pt_date").is_in(days)).sort("t")
    m_t = _us(chat["t"])
    msgs = pl.DataFrame({
        "msg": chat["msg"], "t_us": m_t, "act": clock(m_t), "pt_date": chat["pt_date"],
        "room": chat["room"], "kind": chat["speaker_kind"].cast(pl.Utf8).replace_strict(KIND, default=3).cast(pl.Int8),
        "sender": chat["agent"].fill_null(-1).cast(pl.Int8),
        "mentions": chat["mentions_roster"],
    })

    # ---- turns (H18 rule)
    tt = h18build.turn_times(SimpleNamespace(ev=sh.ev), t0, t1)
    tt = {a: v for a, v in tt.items() if a in roster_agents}
    turn_rows = []
    for a, v in tt.items():
        inday = clock(v)
        k = np.searchsorted(clock.ws, v, side="right") - 1
        ok = (k >= 0) & (v <= clock.we[np.clip(k, 0, None)] + 60e6)  # within a period day's window (+1 min)
        turn_rows.append(pl.DataFrame({"agent": np.full(ok.sum(), a, np.int8), "t_us": v[ok], "act": inday[ok]}))
    turns = pl.concat(turn_rows).sort("agent", "t_us") if turn_rows else pl.DataFrame()

    # ---- reads: exposure rows of agent messages, recipient a roster agent != sender
    am = msgs.filter(pl.col("kind") == 0)
    ex = sh.exposure.filter(pl.col("msg").is_in(am["msg"].implode())).join(
        am.select("msg", "t_us", "sender", "room"), on="msg").filter(
        (pl.col("agent") != pl.col("sender")) & pl.col("agent").is_in(list(roster_agents)))
    reads = []
    for (a,), sub in ex.group_by(["agent"], maintain_order=True):
        a = int(a)
        if a not in tt:
            continue
        T = tt[a]
        tm = sub["t_us"].to_numpy()
        i1 = np.searchsorted(T, tm, side="right")
        ok1 = i1 < len(T)
        ts = np.where(ok1, T[np.clip(i1, 0, len(T) - 1)], -1)
        i2 = np.searchsorted(T, ts + int(GUARD_S * 1e6), side="right")
        ok2 = ok1 & (i2 < len(T))
        tu = np.where(ok2, T[np.clip(i2, 0, len(T) - 1)], -1)
        # a read only counts if seen within the period's days
        kd = np.searchsorted(clock.ws, ts, side="right") - 1
        ok = ok2 & (kd >= 0) & (ts <= clock.we[np.clip(kd, 0, None)] + 60e6)
        reads.append(pl.DataFrame({"msg": sub["msg"].to_numpy()[ok], "recipient": np.full(ok.sum(), a, np.int8),
                                   "sender": sub["sender"].to_numpy()[ok], "room": sub["room"].to_numpy()[ok],
                                   "t_seen_us": ts[ok], "t_upd_us": tu[ok]}))
    reads = pl.concat(reads) if reads else pl.DataFrame()
    if reads.height:
        reads = reads.with_columns(pl.Series("act_seen", clock(reads["t_seen_us"].to_numpy())),
                                   pl.Series("act_upd", clock(reads["t_upd_us"].to_numpy()))).sort("t_upd_us")

    # ---- block windows: roster agents per room at each 30-min window midpoint
    grid = window_grid(cal)
    tmid = _us(grid["t_mid"])
    on_ros = []
    for r in ros.iter_rows(named=True):
        on_ros.append((int(r["agent"]), r["joined"], r["left"]))
    ra = rooms_at(sh, [a for a, _, _ in on_ros], tmid)
    bw = []
    for a, jn, lf in on_ros:
        inr = np.array([(jn <= d) and (lf is None or d < lf) for d in grid["pt_date"].to_list()])
        rm = ra[a]
        keep = inr & (rm >= 0)
        if keep.any():
            bw.append(pl.DataFrame({"day": grid["day"].to_numpy()[keep], "win": grid["win"].to_numpy()[keep],
                                    "agent": np.full(keep.sum(), a, np.int8), "room": rm[keep].astype(np.int8)}))
    bw = pl.concat(bw) if bw else pl.DataFrame()
    block_windows = grid.join(bw, on=["day", "win"], how="left") if bw.height else grid

    # ---- project states (H11, imported)
    states = {}
    for W in (15, 30, 60):
        f = H11 / f"G{g:02d}" / f"labels_project_w{W}.parquet"
        if f.exists():
            lab = pl.read_parquet(f)
            # H11 'day' is the dense rank of non-holdout days within the goal; map by pt_date to ours
            lab = lab.drop("day").join(cal.select("pt_date", "day"), on="pt_date", how="inner")
            states[W] = lab.select("pt_date", "day", "win", "agent", "room", "label", "project")

    # ---- content alignment per block x window
    align = alignment_period(g, cal, grid, sh, ra, on_ros)

    # ---- kicks: human messages (with room) and the goal kickoff (period's first window)
    hk = msgs.filter(pl.col("kind") == 1).select("act", "room").with_columns(pl.lit("human_message").alias("kind"))
    kicks = pl.concat([hk, pl.DataFrame({"act": [0.0], "room": pl.Series([None], dtype=pl.Int8),
                                         "kind": ["goal_kickoff"]})], how="vertical_relaxed")
    res = dict(cal=cal.select("pt_date", "day", "win_start", "win_end", "window_s", "act0", "regime"),
               msgs=msgs, turns=turns, reads=reads, block_windows=block_windows, states=states,
               alignment=align, kicks=kicks)
    if verbose:
        print(f"G{g:02d}: {len(days)} days, {am.height} agent msgs, {turns.height} turns, {reads.height} reads, "
              f"states {list(states)}, alignment rows {align.height if align is not None else 0}", flush=True)
    return res


_WHITEN = {}


def alignment_period(g, cal, grid, sh, ra, on_ros) -> pl.DataFrame | None:
    aw = pl.read_parquet(SH / "embeddings/agent_win30.parquet").filter(
        (pl.col("goal_no") == g) & pl.col("pt_date").is_in(cal["pt_date"].to_list()) & (pl.col("n_chat") + pl.col("n_intent") > 0))
    if aw.height == 0:
        return None
    vec = np.load(SH / "embeddings/agent_win30_vec.npy", mmap_mode="r")
    aw = aw.join(cal.select("pt_date", "day"), on="pt_date")
    X = np.asarray(vec[aw["gid"].to_numpy()], dtype=np.float32)
    Z = np.zeros((X.shape[0], 32), np.float32)
    regs = aw["regime"].to_numpy()
    for rg in np.unique(regs):
        if rg not in _WHITEN:
            _WHITEN[rg] = load_whitener(rg, 32)
        m = regs == rg
        Z[m] = _WHITEN[rg](X[m])
    Z /= np.maximum(np.linalg.norm(Z, axis=1, keepdims=True), 1e-9)
    # room of each agent-window at the window midpoint
    key = {(d, w): i for i, (d, w) in enumerate(zip(grid["day"].to_list(), grid["win"].to_list()))}
    rows = []
    days, wins, ags = aw["day"].to_numpy(), aw["win30"].to_numpy(), aw["agent"].to_numpy()
    room = np.full(len(days), -1, np.int16)
    for i in range(len(days)):
        k = key.get((int(days[i]), int(wins[i])))
        if k is not None and int(ags[i]) in ra:
            room[i] = ra[int(ags[i])][k]
    df = pl.DataFrame({"day": days, "win": wins, "agent": ags, "room": room, "i": np.arange(len(days))})
    for (d, w, r), sub in df.filter(pl.col("room") >= 0).group_by(["day", "win", "room"]):
        idx = sub["i"].to_numpy()
        n = len(idx)
        if n < 2:
            continue
        V = Z[idx]
        C = V @ V.T
        npair = n * (n - 1) // 2
        A = (C.sum() - np.trace(C)) / (2 * npair)
        rows.append({"day": int(d), "win": int(w), "room": int(r), "n_agents": n, "A": float(A)})
    if not rows:
        return None
    out = pl.DataFrame(rows).join(grid.select("day", "win", "act_mid"), on=["day", "win"], how="left")
    return out.sort("room", "day", "win")


def write_period(g: int, res: dict, out: Path = OUT):
    f = out / f"G{g:02d}"
    f.mkdir(parents=True, exist_ok=True)
    res["cal"].write_parquet(f / "days.parquet", compression="zstd")
    res["msgs"].write_parquet(f / "msgs.parquet", compression="zstd")
    if res["turns"].height:
        res["turns"].write_parquet(f / "turns.parquet", compression="zstd")
    if res["reads"].height:
        res["reads"].write_parquet(f / "reads.parquet", compression="zstd")
    res["block_windows"].write_parquet(f / "block_windows.parquet", compression="zstd")
    for W, lab in res["states"].items():
        lab.write_parquet(f / f"states_project_w{W}.parquet", compression="zstd")
    if res["alignment"] is not None:
        res["alignment"].write_parquet(f / "alignment.parquet", compression="zstd")
    res["kicks"].write_parquet(f / "kicks.parquet", compression="zstd")


def write_provenance(goals: list[int], params: dict, out: Path = OUT):
    out.mkdir(parents=True, exist_ok=True)
    prov = {"built_by": "hypotheses/H31-consensus-time-spectral-gap/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["calendar", "chat_core", "chat_mentions_clean", "exposure", "events_core", "actions",
                                   "roster", "rooms_timeline", "kicks", "embeddings/agent_win30", "whitening_<regime>"],
                        "via": "data/processed/shared"},
                       {"source": "H11", "path": "data/processed/H11-potts-labor-vs-herding/G<NN>/labels_project_w{15,30,60}",
                        "built_by": "hypotheses/H11-potts-labor-vs-herding/scheme/build.py"}],
            "imports": ["hypotheses/H18-attention-dilution/scheme/build.py: turn_times"],
            "params": params, "goals": goals, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (out / "_provenance.json").write_text(json.dumps(prov, indent=1))


def nonholdout_goals(lo=10, hi=44) -> list[int]:
    held = set(load_holdout()["goal_periods_held_out"])
    return [g for g in range(lo, hi + 1) if g not in held]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--goals", type=int, nargs="*", default=None)
    ap.add_argument("--allow-holdout", action="store_true", help="only for analysis/confirm_holdout.py")
    a = ap.parse_args()
    goals = a.goals or nonholdout_goals()
    held = set(load_holdout()["goal_periods_held_out"])
    if (set(goals) & held) and not a.allow_holdout:
        raise SystemExit(f"refusing: {sorted(set(goals) & held)} are in the locked holdout")
    t = time.time()
    sh = Shared()
    print(f"loaded shared tables in {time.time() - t:.0f}s", flush=True)
    built = []
    for g in goals:
        res = build_period(sh, g, a.allow_holdout)
        if res is None:
            print(f"G{g:02d}: no days", flush=True)
            continue
        write_period(g, res)
        built.append(g)
    write_provenance(built, {"window_min": W_MIN, "guard_s": GUARD_S, "whiten_dim": 32,
                             "visibility": "H18 call-start rule; t_upd = first turn after t_seen + 1 s",
                             "allow_holdout": a.allow_holdout})
    print(f"done in {time.time() - t:.0f}s", flush=True)


if __name__ == "__main__":
    main()
